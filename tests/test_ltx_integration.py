"""Phase B: LTX/ComfyUI adapter against a fake local ComfyUI server. Not evidence the real server works."""
from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from granthstudio.comfy import (ComfyBackend, check_checkpoint_binding, execution_seconds, load_template,
                                reconcile, cancel, WorkflowTemplate)
from granthstudio.config import load_models
from granthstudio.errors import ConfigError, IntegrationUnavailable, JobPending, TaskFailed
from granthstudio.integrity import atomic_write_json, read_json, sha256_obj
from granthstudio.pipeline import load_bundle, validate_ltx_inputs
from tests.conftest import have_tool, make_still

CHECKPOINT = "ltxv-2b-0.9.8-distilled.safetensors"
GRAPH = {"1": {"class_type": "SyntheticLoader", "inputs": {"ckpt_name": CHECKPOINT}},
         "2": {"class_type": "SyntheticSave", "inputs": {"images": ["1", 0]}}}


class FakeComfy:
    """Minimal ComfyUI: /prompt, /queue, /history, /object_info, /system_stats, /interrupt."""

    def __init__(self):
        self.posts, self.interrupts, self.queue_deletes = [], [], []
        self.running, self.pending, self.history, self.nodes = [], [], {}, {"SyntheticLoader", "SyntheticSave"}
        self.forget_history = False
        self.cache, self.executions, self.cache_hits = set(), 0, 0   # ComfyUI caches node outputs by node inputs
        self.auto_outputs = None   # when set, every POST /prompt finishes at once with these outputs
        self.auto_status = "success"   # ComfyUI status_str of those auto-finished jobs ("error" simulates a failed render)
        self.view_bytes = b""      # body served by /view
        self.object_info_override = None   # optional richer /object_info dict (tests/test_weight_checks.py)
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_): pass
            def _send(self, payload, code=200):
                data = json.dumps(payload).encode(); self.send_response(code)
                self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])) or b"{}")
                if self.path == "/prompt":
                    pid = f"p{len(outer.posts) + 1}"; outer.posts.append(body)
                    key = json.dumps(body["prompt"], sort_keys=True)   # extra_data / prompt_id are NOT part of the cache key
                    if key in outer.cache: outer.cache_hits += 1
                    else: outer.cache.add(key); outer.executions += 1
                    outer.running.append([0, pid, body["prompt"], body.get("extra_data", {}), []])
                    if outer.auto_outputs is not None:
                        outer.finish(pid, status=outer.auto_status)
                        outer.history[pid]["outputs"] = outer.auto_outputs
                    self._send({"prompt_id": pid})
                elif self.path == "/interrupt":
                    outer.interrupts.append(body); self._send({})
                elif self.path == "/queue":
                    outer.queue_deletes.append(body); self._send({})
                else:
                    self._send({}, 404)
            def do_GET(self):
                if self.path.startswith("/view"):
                    self.send_response(200); self.send_header("Content-Length", str(len(outer.view_bytes)))
                    self.end_headers(); self.wfile.write(outer.view_bytes)
                elif self.path == "/object_info": self._send(outer.object_info_override if outer.object_info_override is not None else {n: {} for n in outer.nodes})
                elif self.path == "/system_stats": self._send({"system": {"comfyui_version": "synthetic"}})
                elif self.path == "/queue": self._send({"queue_running": outer.running, "queue_pending": outer.pending})
                elif self.path == "/history":
                    self._send({} if outer.forget_history else outer.history)
                elif self.path.startswith("/history/"):
                    pid = self.path.rsplit("/", 1)[1]
                    self._send({pid: outer.history[pid]} if pid in outer.history and not outer.forget_history else {})
                else:
                    self._send({}, 404)

        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_port}"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def finish(self, pid, status="success", ts=(1000, 4500)):
        item = next(i for i in self.running if i[1] == pid); self.running.remove(item)
        self.history[pid] = {"prompt": item, "outputs": {"2": {"videos": [{"filename": "a.mp4"}]}},
                             "status": {"status_str": status, "messages": [
                                 ["execution_start", {"timestamp": ts[0]}], ["execution_success", {"timestamp": ts[1]}]]}}

    def close(self): self.server.shutdown(); self.server.server_close()


@pytest.fixture
def comfy():
    server = FakeComfy(); yield server; server.close()


def backend(server):
    return ComfyBackend(server.url, timeout_s=2, poll_s=0.01, max_wait_s=0.3)


def test_inspect_reports_missing_nodes_and_stats(comfy):
    b = backend(comfy)
    b.require_nodes(GRAPH)
    comfy.nodes.discard("SyntheticSave")
    with pytest.raises(IntegrationUnavailable, match="SyntheticSave"):
        b.require_nodes(GRAPH)
    assert b.system_stats()["system"]["comfyui_version"] == "synthetic"


def test_checkpoint_binding_rejects_other_ltx_family(tmp_path):
    def template(text): return WorkflowTemplate("t", tmp_path / "t.json", "v", "validated", text, "2")
    check_checkpoint_binding(template(json.dumps(GRAPH)), CHECKPOINT)
    with pytest.raises(ConfigError, match="does not load the pinned checkpoint"):
        check_checkpoint_binding(template(json.dumps({"1": {"inputs": {"ckpt_name": "other.safetensors"}}})), CHECKPOINT)
    ltx2 = {"1": {"inputs": {"ckpt_name": CHECKPOINT}}, "2": {"inputs": {"model": "ltx-2-19b-dev.safetensors"}}}
    with pytest.raises(ConfigError, match="other LTX weights"):
        check_checkpoint_binding(template(json.dumps(ltx2)), CHECKPOINT)


def test_shipped_stub_workflows_remain_refused(project):
    models = load_models(project)
    for relative in models["ltx"]["workflow_templates"].values():
        with pytest.raises(ConfigError, match="does not load the pinned checkpoint"):
            check_checkpoint_binding(load_template(project.root / relative), models["ltx"]["checkpoint_file"])


def test_full_job_over_http_posts_once_and_reports_timing(comfy, tmp_path):
    b = backend(comfy); journal = tmp_path / "job.json"
    with pytest.raises(JobPending):
        b.execute(GRAPH, journal)  # job still running on the server
    state = read_json(journal)
    assert state["state"] == "submitted" and state["prompt_id"] == "p1" and len(comfy.posts) == 1
    assert comfy.posts[0]["extra_data"]["granthstudio_job"] == state["job_token"]
    comfy.finish("p1")
    samples = []
    entry = b.execute(GRAPH, journal, sampler=lambda: samples.append(1))
    assert len(comfy.posts) == 1 and samples and execution_seconds(entry) == 3.5
    assert execution_seconds({"status": {}}) is None


def test_lost_response_is_found_by_token_not_resubmitted(comfy, tmp_path):
    b = backend(comfy); journal = tmp_path / "job.json"
    token = sha256_obj({"base_url": b.base_url, "graph_sha256": sha256_obj(GRAPH), "journal": "job.json", "attempt": 1})
    atomic_write_json(journal, {"base_url": b.base_url, "graph_sha256": sha256_obj(GRAPH), "state": "submitting",
                                "job_token": token, "attempt": 1})
    comfy.running.append([0, "p9", GRAPH, {"granthstudio_job": token}, []])  # server accepted the lost POST
    with pytest.raises(JobPending, match="reconcile"):
        b.execute(GRAPH, journal)
    assert reconcile(b, journal)["prompt_id"] == "p9" and comfy.posts == []
    comfy.finish("p9")
    assert b.execute(GRAPH, journal)["status"]["status_str"] == "success" and comfy.posts == []


def test_unfound_submission_needs_an_explicit_declaration_before_resubmit(comfy, tmp_path):
    b = backend(comfy); journal = tmp_path / "job.json"
    atomic_write_json(journal, {"base_url": b.base_url, "graph_sha256": sha256_obj(GRAPH), "state": "submitting",
                                "job_token": "t" * 64, "attempt": 1})
    with pytest.raises(JobPending, match="declare-lost"):
        reconcile(b, journal)
    assert reconcile(b, journal, declare_lost=True)["state"] == "failed"
    with pytest.raises(JobPending):
        b.execute(GRAPH, journal)
    assert len(comfy.posts) == 1 and read_json(journal)["attempt"] == 2  # a new, distinct attempt token


def test_cancel_interrupts_running_job_and_blocks_resubmit_until_stopped(comfy, tmp_path):
    b = backend(comfy); journal = tmp_path / "job.json"
    with pytest.raises(JobPending): b.execute(GRAPH, journal)
    assert cancel(b, journal)["state"] == "cancelled" and comfy.interrupts == [{"prompt_id": "p1"}]
    with pytest.raises(JobPending, match="cancelled"):
        b.execute(GRAPH, journal)
    with pytest.raises(JobPending, match="still running"):
        reconcile(b, journal)
    comfy.finish("p1", status="error")
    assert reconcile(b, journal)["state"] == "failed"
    with pytest.raises(JobPending): b.execute(GRAPH, journal)
    assert len(comfy.posts) == 2
    with pytest.raises(ConfigError, match="only a submitted job"):
        cancel(b, tmp_path / "missing.json") if False else cancel(b, _failed(tmp_path))


def _failed(tmp_path):
    path = tmp_path / "failed.json"; atomic_write_json(path, {"state": "failed"}); return path


def test_cancel_pending_job_deletes_it_from_the_queue(comfy, tmp_path):
    b = backend(comfy); journal = tmp_path / "job.json"
    with pytest.raises(JobPending): b.execute(GRAPH, journal)
    comfy.pending.append(comfy.running.pop())
    cancel(b, journal)
    assert comfy.queue_deletes == [{"delete": ["p1"]}] and comfy.interrupts == []


def test_http_error_on_poll_keeps_prompt_over_real_sockets(comfy, tmp_path):
    b = backend(comfy); journal = tmp_path / "job.json"
    with pytest.raises(JobPending): b.execute(GRAPH, journal)
    comfy.close()
    with pytest.raises(JobPending): b.execute(GRAPH, journal)
    assert read_json(journal)["state"] == "submitted"


@pytest.mark.skipif(not (have_tool("ffmpeg") and have_tool("ffprobe")), reason="media tools missing")
def test_input_validation_interface(approved_project, tmp_path):
    models = load_models(approved_project)
    shot = {"shot_id": "a01_s01_sh02", "frames": 49}
    image = make_still(tmp_path / "start.png")
    with pytest.raises(IntegrationUnavailable, match="width/height"):
        validate_ltx_inputs(models, shot, image)
    models["ltx"]["runtime"] = {"width": 768, "height": 512}
    result = validate_ltx_inputs(models, shot, image)
    assert result["start_image"]["width"] == 640 and result["frame_rule"].endswith("(O-003)")
    with pytest.raises(TaskFailed, match="not in pinned frame_counts"):
        validate_ltx_inputs(models, {**shot, "frames": 50}, image)
    bad = tmp_path / "bad.png"; bad.write_bytes(b"not an image")
    with pytest.raises(Exception):
        validate_ltx_inputs(models, shot, bad)


def seeded(seed):
    return {**GRAPH, "3": {"class_type": "SyntheticSampler", "inputs": {"seed": seed}}}


def test_rejected_output_forces_fresh_generation_valid_output_does_not(comfy, tmp_path):
    from granthstudio.comfy import generation_seed, reject_output
    from granthstudio.errors import GateFailure
    b = backend(comfy); journal = tmp_path / "job.json"
    with pytest.raises(JobPending):
        b.execute(seeded(generation_seed(journal, 7)), journal)   # polling uncertain: prompt id preserved
    assert reject_output(journal, "nope") is False and read_json(journal)["state"] == "submitted"
    with pytest.raises(JobPending):
        b.execute(seeded(generation_seed(journal, 7)), journal)
    assert len(comfy.posts) == 1 and comfy.executions == 1      # no duplicate generation while possibly active
    comfy.finish("p1")
    b.execute(seeded(7), journal)
    assert read_json(journal)["state"] == "completed"
    b.execute(seeded(7), journal)
    assert len(comfy.posts) == 1                                # valid completed output: never resubmitted
    assert reject_output(journal, "flat video") is True
    assert read_json(journal)["state"] == "rejected"            # durable across an interruption
    with pytest.raises(GateFailure, match="identical graph inputs"):
        backend(comfy).execute(seeded(7), journal)              # same inputs would be served from ComfyUI's cache
    assert len(comfy.posts) == 1
    seed = generation_seed(journal, 7)
    assert seed == 8
    with pytest.raises(JobPending):
        backend(comfy).execute(seeded(seed), journal, generation={"seed": seed, "seed_offset": 1})
    state = read_json(journal)
    assert len(comfy.posts) == 2 and comfy.executions == 2 and comfy.cache_hits == 0   # genuinely new generation
    assert state["attempt"] == 2 and state["prompt_id"] == "p2" and state["rejections"][0]["reason"] == "flat video"
    assert [h["generation"] for h in state["history"]] == [{}, {"seed": 8, "seed_offset": 1}]
    assert state["history"][0]["graph_sha256"] != state["history"][1]["graph_sha256"]


def test_scheduler_resubmits_after_media_rejection_only(comfy, tmp_path):
    from granthstudio.comfy import generation_seed
    from granthstudio.errors import TaskFailed
    from granthstudio.scheduler import Scheduler, Task
    comfy.auto_outputs = {"2": {"videos": [{"filename": "a.mp4"}]}}
    b = backend(comfy); journal = tmp_path / "pending" / "t.json"; seen = []
    def run(work):
        b.execute(seeded(generation_seed(journal, 1)), journal); (work / "out.txt").write_text("x"); return {"out": "out.txt"}
    def verify(directory):
        seen.append(len(comfy.posts))
        if len(seen) == 1:
            raise TaskFailed("decoded video is flat")
    task = Task("tier1", "t", {}, "v1", run, max_attempts=2, verify=verify, journal=journal)
    result = Scheduler(tmp_path / "store").run([task])[0]
    assert result.status == "complete" and seen == [1, 2] and comfy.executions == 2
    assert read_json(journal)["rejections"][0]["reason"] == "decoded video is flat"


def test_attempt_budget_survives_restart_and_polling_does_not_consume_it(comfy, tmp_path):
    from granthstudio.comfy import reset_budget
    from granthstudio.errors import GateFailure
    journal = tmp_path / "job.json"
    comfy.auto_outputs = {"2": {}}; comfy.auto_status = "error"
    for n in range(3):
        with pytest.raises(TaskFailed):
            backend(comfy).execute(seeded(n), journal, max_attempts=3)   # a "restarted" backend each time
    assert len(comfy.posts) == 3 and read_json(journal)["attempt"] == 3
    with pytest.raises(GateFailure, match="budget exhausted"):
        backend(comfy).execute(seeded(99), journal, max_attempts=3)
    assert len(comfy.posts) == 3
    with pytest.raises(ConfigError):
        reset_budget(journal, " ")
    reset_budget(journal, "synthetic-test-only")
    with pytest.raises(TaskFailed):
        backend(comfy).execute(seeded(100), journal, max_attempts=3)
    assert len(comfy.posts) == 4 and read_json(journal)["budget_resets"][0]["by"] == "synthetic-test-only"
    # an outstanding job is polled/recovered any number of times without spending budget
    comfy.auto_outputs = None; other = tmp_path / "other.json"
    for _ in range(5):
        with pytest.raises(JobPending):
            backend(comfy).execute(seeded(1), other, max_attempts=1)
    assert len(comfy.posts) == 5 and read_json(other)["attempt"] == 1


def test_two_concurrent_callers_submit_exactly_once(comfy, tmp_path):
    import threading
    journal = tmp_path / "job.json"; barrier = threading.Barrier(2); outcomes = []
    def caller():
        barrier.wait()
        try:
            backend(comfy).execute(GRAPH, journal)
        except JobPending as exc:
            outcomes.append(str(exc))
    threads = [threading.Thread(target=caller) for _ in range(2)]
    [t.start() for t in threads]; [t.join() for t in threads]
    assert len(comfy.posts) == 1 and len(outcomes) == 2
    assert not list(tmp_path.glob("*.lock"))                    # ownership released


def test_abandoned_owner_after_submission_intent_reconciles_instead_of_resubmitting(comfy, tmp_path):
    import os, time
    from granthstudio.comfy import owned
    journal = tmp_path / "job.json"
    with pytest.raises(JobPending):
        backend(comfy).execute(GRAPH, journal)
    state = read_json(journal); state.pop("prompt_id"); state["state"] = "submitting"   # owner died before recording the reply
    atomic_write_json(journal, state)
    lock = tmp_path / "job.json.lock"; lock.write_text("{}")
    old = time.time() - 10_000; os.utime(lock, (old, old))                              # abandoned ownership
    with pytest.raises(JobPending, match="reconcile"):
        backend(comfy).execute(GRAPH, journal)
    assert len(comfy.posts) == 1 and not lock.exists()
    assert reconcile(backend(comfy), journal)["prompt_id"] == "p1"
    with pytest.raises(JobPending):
        backend(comfy).execute(GRAPH, journal)
    assert len(comfy.posts) == 1
    lock.write_text("{}")                                                                # a fresh lock is never broken
    with pytest.raises(JobPending, match="owned by another"):
        with owned(journal, wait_s=0.1):
            pass
    assert lock.exists()


def test_store_namespaces_keep_tokens_and_reconciliation_apart(comfy, tmp_path):
    from granthstudio.comfy import store_namespace
    a, b_ = tmp_path / "A" / "job.json", tmp_path / "B" / "job.json"
    for j in (a, b_):
        j.parent.mkdir()
    with pytest.raises(JobPending):
        backend(comfy).execute(GRAPH, a)
    with pytest.raises(JobPending):
        backend(comfy).execute(GRAPH, b_)
    token_a, token_b = read_json(a)["job_token"], read_json(b_)["job_token"]
    assert token_a != token_b and store_namespace(a) != store_namespace(b_)    # identical task and filename, distinct tokens
    # store B's response is lost; the server only holds store A's job under A's token
    lost = tmp_path / "B" / "lost.json"
    atomic_write_json(lost, {"base_url": backend(comfy).base_url, "graph_sha256": sha256_obj(GRAPH), "namespace": store_namespace(b_),
                             "state": "submitting", "job_token": token_a, "attempt": 1})
    with pytest.raises(JobPending, match="not found"):
        reconcile(backend(comfy), lost)                          # must not adopt A's prompt
    assert store_namespace(b_) == read_json(b_)["namespace"]     # restart reuses the persisted namespace
