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
        self.node_cache, self.executions, self.cache_hits, self.sampler_runs = set(), 0, 0, 0   # node-level, dependency-aware cache
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
                    outer.run_prompt(body["prompt"])   # extra_data / prompt_id are NOT part of any cache key
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

    def run_prompt(self, prompt):
        """ComfyUI semantics: only nodes the output depends on run, and a node's cache key is its class plus its
        inputs with upstream links replaced by the upstream node's own key. Disconnected nodes never run."""
        nodes = {i: n for i, n in prompt.items() if isinstance(n, dict)}
        outputs = [i for i, n in nodes.items() if str(n.get("class_type", "")).endswith("Save")] or list(nodes)
        keys = {}
        def key(i):
            if i not in keys:
                ins = {k: (["@", key(v[0]), v[1]] if isinstance(v, list) and len(v) == 2 and v[0] in nodes else v)
                       for k, v in nodes[i].get("inputs", {}).items()}
                keys[i] = json.dumps([nodes[i]["class_type"], ins], sort_keys=True)
            return keys[i]
        needed, stack = set(), list(outputs)
        while stack:
            i = stack.pop()
            if i in needed: continue
            needed.add(i)
            stack += [v[0] for v in nodes[i].get("inputs", {}).values() if isinstance(v, list) and len(v) == 2 and v[0] in nodes]
        fresh = [i for i in needed if key(i) not in self.node_cache]
        self.node_cache.update(key(i) for i in fresh)
        if fresh:
            self.executions += 1
            self.sampler_runs += sum(1 for i in fresh if "seed" in nodes[i].get("inputs", {}))
        else:
            self.cache_hits += 1

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
    """Loader -> Sampler(seed) -> Save: the seed sits on the path to the designated output."""
    return {"1": GRAPH["1"], "3": {"class_type": "SyntheticSampler", "inputs": {"model": ["1", 0], "seed": seed}},
            "2": {"class_type": "SyntheticSave", "inputs": {"images": ["3", 0]}}}


def disconnected(seed):
    """The seed varies but on a node the output does not depend on (a stray SEED placeholder)."""
    return {**GRAPH, "3": {"class_type": "SyntheticSampler", "inputs": {"seed": seed}}}


def test_rejected_output_forces_fresh_generation_valid_output_does_not(comfy, tmp_path):
    from granthstudio.comfy import generation_seed, reject_output
    from granthstudio.errors import GateFailure
    b = backend(comfy); journal = tmp_path / "job.json"
    with pytest.raises(JobPending):
        b.execute(seeded(generation_seed(journal, 7)), journal, output_node="2")   # polling uncertain: prompt id preserved
    assert reject_output(journal, "nope") is False and read_json(journal)["state"] == "submitted"
    with pytest.raises(JobPending):
        b.execute(seeded(generation_seed(journal, 7)), journal, output_node="2")
    assert len(comfy.posts) == 1 and comfy.executions == 1      # no duplicate generation while possibly active
    comfy.finish("p1")
    b.execute(seeded(7), journal, output_node="2")
    assert read_json(journal)["state"] == "completed"
    b.execute(seeded(7), journal, output_node="2")
    assert len(comfy.posts) == 1                                # valid completed output: never resubmitted
    assert reject_output(journal, "flat video") is True
    assert read_json(journal)["state"] == "rejected"            # durable across an interruption
    with pytest.raises(GateFailure, match="same generation inputs"):
        backend(comfy).execute(seeded(7), journal, output_node="2")              # same inputs would be served from ComfyUI's cache
    assert len(comfy.posts) == 1
    seed = generation_seed(journal, 7)
    assert seed == 8
    with pytest.raises(JobPending):
        backend(comfy).execute(seeded(seed), journal, output_node="2", generation={"seed": seed, "seed_offset": 1})
    state = read_json(journal)
    assert len(comfy.posts) == 2 and comfy.executions == 2 and comfy.cache_hits == 0   # genuinely new generation
    assert comfy.sampler_runs == 2                              # the sampler itself re-ran; it was not served from cache
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
        b.execute(seeded(generation_seed(journal, 1)), journal, output_node="2"); (work / "out.txt").write_text("x"); return {"out": "out.txt"}
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
            backend(comfy).execute(seeded(n), journal, output_node="2", max_attempts=3)   # a "restarted" backend each time
    assert len(comfy.posts) == 3 and read_json(journal)["attempt"] == 3
    with pytest.raises(GateFailure, match="budget exhausted"):
        backend(comfy).execute(seeded(99), journal, output_node="2", max_attempts=3)
    assert len(comfy.posts) == 3
    with pytest.raises(ConfigError):
        reset_budget(journal, " ")
    reset_budget(journal, "synthetic-test-only")
    with pytest.raises(TaskFailed):
        backend(comfy).execute(seeded(100), journal, output_node="2", max_attempts=3)
    assert len(comfy.posts) == 4 and read_json(journal)["budget_resets"][0]["by"] == "synthetic-test-only"
    # an outstanding job is polled/recovered any number of times without spending budget
    comfy.auto_outputs = None; other = tmp_path / "other.json"
    for _ in range(5):
        with pytest.raises(JobPending):
            backend(comfy).execute(seeded(1), other, output_node="2", max_attempts=1)
    assert len(comfy.posts) == 5 and read_json(other)["attempt"] == 1


def child(comfy, mode, journal, signal):
    import subprocess, sys
    from pathlib import Path
    script = Path(__file__).with_name("_comfy_child.py")
    return subprocess.Popen([sys.executable, str(script), mode, comfy.url, str(journal), str(signal)],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def test_live_owner_is_never_displaced_by_a_second_real_process(comfy, tmp_path):
    import time
    journal, signal = tmp_path / "job.json", tmp_path / "sig"; signal.mkdir()
    a = child(comfy, "hold", journal, signal)                     # owns the journal, pauses before writing intent
    for _ in range(300):
        if (signal / "held").exists(): break
        time.sleep(0.05)
    assert (signal / "held").exists()
    b = child(comfy, "fast", journal, signal)                     # same task, second OS process
    out, err = b.communicate(timeout=60)
    assert b.returncode == 5 and "owned by another process" in out, (out, err)
    assert comfy.posts == []                                       # B was refused; nothing submitted yet
    # no age rule exists: the lock file persists, so a long pause cannot let anyone else in
    (signal / "release").write_text("1")
    a_out, a_err = a.communicate(timeout=60)
    assert a.returncode == 5, (a_out, a_err)                       # A finished (job still running -> JobPending)
    assert len(comfy.posts) == 1 and read_json(journal)["state"] == "submitted"


def test_owner_crash_before_and_after_post_is_recoverable_without_duplicates(comfy, tmp_path):
    before, after = tmp_path / "before.json", tmp_path / "after.json"
    signal = tmp_path / "sig"; signal.mkdir()
    assert child(comfy, "crash_before_post", before, signal).wait(timeout=60) == 9      # died holding the lock
    assert read_json(before)["state"] == "submitting" and comfy.posts == []
    with pytest.raises(JobPending, match="reconcile"):                                   # OS freed the lock on death
        backend(comfy).execute(GRAPH, before)
    assert comfy.posts == []
    assert child(comfy, "crash_after_post", after, signal).wait(timeout=60) == 9
    assert read_json(after)["state"] == "submitting" and len(comfy.posts) == 1           # reply never journaled
    with pytest.raises(JobPending, match="reconcile"):
        backend(comfy).execute(GRAPH, after)
    assert reconcile(backend(comfy), after)["prompt_id"] == "p1"                         # found by token
    with pytest.raises(JobPending):
        backend(comfy).execute(GRAPH, after)
    assert len(comfy.posts) == 1


def test_journal_write_failure_before_post_submits_nothing(comfy, tmp_path, monkeypatch):
    from granthstudio import comfy as module
    journal = tmp_path / "job.json"
    monkeypatch.setattr(module, "atomic_write_json", lambda *a, **k: (_ for _ in ()).throw(OSError("disk full")))
    with pytest.raises(OSError):
        backend(comfy).execute(GRAPH, journal)
    assert comfy.posts == []
    monkeypatch.undo()
    with pytest.raises(JobPending):                                  # lock was released by the failed owner
        backend(comfy).execute(GRAPH, journal)
    assert len(comfy.posts) == 1


def test_threads_in_one_process_also_submit_exactly_once(comfy, tmp_path):
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


def test_disconnected_seed_does_not_satisfy_the_freshness_gate(comfy, tmp_path):
    from granthstudio.comfy import generation_evidence, reject_output
    from granthstudio.errors import GateFailure
    assert generation_evidence(disconnected(1), "2")["fingerprint"] == generation_evidence(disconnected(2), "2")["fingerprint"]
    assert generation_evidence(seeded(1), "2")["fingerprint"] != generation_evidence(seeded(2), "2")["fingerprint"]
    assert generation_evidence(seeded(1), "2")["seed_inputs"] == [{"node": "3", "input": "seed", "value": 1}]
    journal = tmp_path / "job.json"
    with pytest.raises(JobPending):
        backend(comfy).execute(disconnected(1), journal, output_node="2")
    comfy.finish("p1")
    backend(comfy).execute(disconnected(1), journal, output_node="2")
    assert reject_output(journal, "flat") is True
    with pytest.raises(GateFailure, match="no seed input on the path"):       # whole graph differs, closure does not
        backend(comfy).execute(disconnected(2), journal, output_node="2")
    assert len(comfy.posts) == 1
    # and the fake really would have served it from cache, proving the gate is what protects the GPU
    comfy.run_prompt(disconnected(2)); assert comfy.cache_hits == 1 and comfy.sampler_runs == 0


def test_generation_evidence_is_durable_and_recovery_keeps_the_attempt(comfy, tmp_path):
    from granthstudio.comfy import generation_seed, reject_output
    journal = tmp_path / "job.json"
    seed = generation_seed(journal, 5)
    with pytest.raises(JobPending):
        backend(comfy).execute(seeded(seed), journal, output_node="2", generation={"seed": seed, "seed_offset": 0})
    first = read_json(journal)
    with pytest.raises(JobPending):                                  # restart while uncertain: same attempt, no new POST
        backend(comfy).execute(seeded(generation_seed(journal, 5)), journal, output_node="2")
    assert read_json(journal)["job_token"] == first["job_token"] and len(comfy.posts) == 1
    entry = first["history"][0]
    assert entry["scope"] == "output_closure" and entry["seed_inputs"] == [{"node": "3", "input": "seed", "value": 5}]
    assert entry["fingerprint"] and entry["generation"] == {"seed": 5, "seed_offset": 0}
    comfy.finish("p1"); backend(comfy).execute(seeded(5), journal, output_node="2")
    reject_output(journal, "bad")
    assert read_json(journal)["rejected_fingerprints"] == [entry["fingerprint"]]
