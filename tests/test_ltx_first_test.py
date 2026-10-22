"""scripts/ltx_first_test.py end to end against a FAKE ComfyUI: plumbing only. No real model, GPU or ComfyUI is involved,
the weights are a few synthetic bytes, and a run with --skip-static-verify can never produce PASS."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from tests.conftest import REPO, have_tool
from tests.test_ltx_integration import FakeComfy

pytestmark = pytest.mark.skipif(not (have_tool("ffmpeg") and have_tool("ffprobe")), reason="media tools missing")
SPEC = importlib.util.spec_from_file_location("ltx_first_test", REPO / "scripts" / "ltx_first_test.py")
ft = importlib.util.module_from_spec(SPEC)
sys.modules["ltx_first_test"] = ft
SPEC.loader.exec_module(ft)
PINS = yaml.safe_load((REPO / "config" / "ltx_098_pins.yaml").read_text(encoding="utf-8"))
T4 = [{"index": 0, "name": "Tesla T4", "memory_total_mb": 15360.0, "memory_used_mb": 9000.0, "memory_free_mb": 15000.0}]
PHYS = [{"index": i, "uuid": f"GPU-synthetic-{i}", "name": "Tesla T4", "memory_total_mb": 15360.0, "memory_used_mb": 300.0} for i in (0, 1)]


@pytest.fixture
def host(tmp_path, monkeypatch):
    server = FakeComfy()
    server.nodes = {n["class"] for n in PINS["required_nodes"]}
    clip = tmp_path / "server_clip.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "testsrc=size=768x512:rate=24", "-frames:v", "49", "-c:v", "libx264",
                    "-threads", "1", "-pix_fmt", "yuv420p", str(clip)], check=True, timeout=60)
    server.view_bytes = clip.read_bytes()
    server.auto_outputs = {"103": {"gifs": [{"filename": "o.mp4", "type": "output"}]}}
    models = tmp_path / "comfy"
    for sub, name in (("checkpoints", "ltxv-2b-0.9.8-distilled.safetensors"), ("text_encoders", "t5xxl_fp16.safetensors")):
        (models / "models" / sub).mkdir(parents=True); (models / "models" / sub / name).write_bytes(f"synthetic {name}".encode())
    for module in ("runtime", "pipeline"):
        monkeypatch.setattr(f"granthstudio.{module}.gpu_status", lambda: T4)
    monkeypatch.setattr("granthstudio.runtime.ram_available_mb", lambda: 20000)
    monkeypatch.setenv("GRANTHSTUDIO_SESSION_DEADLINE", "2999-01-01T00:00:00+00:00")
    monkeypatch.setattr(ft, "physical_gpus", lambda: [dict(PHYS[0]), dict(PHYS[1])])      # the dual-T4 host the plan assumes
    yield server, models, tmp_path / "work"
    server.close()


def base_args(host, *extra):
    server, models, work = host
    return ["--workdir", str(work), "--comfy-url", server.url, "--models-dir", str(models), "--min-disk-gb", "0.001", *extra]


def run(host, *extra):
    """CPU plumbing only: drives the private runner with the gates off. main() always enforces them for --execute."""
    work = host[2]
    code = ft._run(ft.parse_args(base_args(host, "--skip-static-verify", *extra)), enforce_gates=False)
    return code, json.loads((work / ("retry_receipt.json" if "--retry-test" in extra else "test_receipt.json")).read_text(encoding="utf-8"))


def test_dry_run_prepares_everything_but_submits_nothing(host):
    code, receipt = run(host)
    assert code == 1 and receipt["verdict"] == "NOT_RUN" and "dry run" in receipt["reason"]
    assert host[0].posts == [] and host[0].uploads == {}
    assert receipt["preflight"]["gpu_ready"] is True and receipt["preflight"]["checks"]["sources"]["status"] == "pass"
    models = yaml.safe_load((host[2] / "project" / "config" / "models.yaml").read_text(encoding="utf-8"))["ltx"]
    assert models["runtime"]["files"]["vae"] is None and models["capabilities"] == {"i2v": "unvalidated", "flf": "disabled"}
    assert models["runtime"]["files"]["checkpoint"]["sha256"] == receipt["inputs"]["checkpoint_sha256"]   # hashed from the bytes


def test_execute_goes_through_the_existing_pipeline_and_stages_the_image(host):
    server, _, work = host
    code, receipt = run(host, "--execute")
    assert receipt["verdict"] == "NOT_RUN" and "skipped" in receipt["reason"]        # clip decoded, but never a PASS without static verification
    assert [r["status"] for r in receipt["results"]] == ["complete"] and receipt["clip"]["width"] == 768 and receipt["clip"]["height"] == 512
    assert len(server.posts) == 1 and len(server.uploads) == 1
    graph = server.posts[0]["prompt"]
    staged = next(iter(server.uploads))
    assert graph["78"]["inputs"]["image"] == staged and staged.startswith("granth_")      # LoadImage got a staged name, not a path
    assert graph["95"]["inputs"]["length"] == 49 and graph["95"]["inputs"]["width"] == 768 and graph["95"]["inputs"]["height"] == 512
    assert graph["44"]["inputs"]["ckpt_name"] == "ltxv-2b-0.9.8-distilled.safetensors" and graph["6"]["inputs"]["text"] == "slight head turn"
    assert isinstance(graph["102"]["inputs"]["noise_seed"], int) and graph["103"]["inputs"]["frame_rate"] == 24
    journal = receipt["journal"]
    assert journal["state"] == "completed" and journal["history"][0]["scope"] == "output_closure"
    assert journal["history"][0]["seed_inputs"][0]["node"] == "102"                    # freshness is judged on the sampler path
    assert receipt["metrics"]["generation"]["attempt"] == 1


def test_missing_weights_fail_closed_before_any_request(host, tmp_path):
    server, models, work = host
    (models / "models" / "checkpoints" / "ltxv-2b-0.9.8-distilled.safetensors").unlink()
    code, receipt = run(host, "--execute")
    assert code == 1 and receipt["verdict"] == "NOT_RUN" and "missing file" in receipt["reason"]
    assert server.posts == [] and server.uploads == {}


def test_unready_host_is_refused_with_zero_submissions(host, monkeypatch):
    server, _, work = host
    monkeypatch.setattr("granthstudio.runtime.gpu_status", lambda: [{**T4[0], "memory_free_mb": 1000.0}])
    code, receipt = run(host, "--execute")
    assert receipt["results"][0]["status"] == "not_validated" and "GPU preflight not passed" in receipt["results"][0]["detail"]
    assert receipt["verdict"] == "NOT_VALIDATED" and server.posts == [] and server.uploads == {}


def test_real_static_verification_blocks_a_run_with_synthetic_weights(host):
    server, models, work = host
    code = ft._run(ft.parse_args(base_args(host, "--execute")), enforce_gates=False)
    receipt = json.loads((work / "test_receipt.json").read_text(encoding="utf-8"))
    assert code == 1 and receipt["verdict"] == "NOT_RUN" and "static pin verification not acceptable" in receipt["reason"]
    assert server.posts == [] and server.uploads == {}                                   # hashes differ from the pins, so nothing is sent


def test_static_ok_tolerates_only_the_substitution_item(tmp_path):
    report = tmp_path / "r.json"
    def write(*items):
        report.write_text(json.dumps({"results": [{"check": c, "status": s} for c, s in items]}), encoding="utf-8")
    write(("a", "PASS"), ("workflow:model_names", "UNVERIFIED"))
    assert ft.static_ok(report, 2)[0] is True
    write(("a", "PASS"), ("workflow:model_names", "UNVERIFIED"), ("node:FloatToSigmas", "UNVERIFIED"))
    assert ft.static_ok(report, 2)[0] is False
    assert ft.static_ok(report, 1)[0] is False and ft.static_ok(report, 0)[0] is True


@pytest.mark.skipif(not have_tool("bash"), reason="bash missing")
def test_gpu_script_is_syntactically_valid_and_refuses_before_any_network_step(tmp_path):
    import os
    script = REPO / "scripts" / "kaggle" / "ltx_first_test.sh"
    assert subprocess.run(["bash", "-n", str(script)]).returncode == 0
    base = {k: v for k, v in os.environ.items() if k not in ("LTX_DOWNLOAD_APPROVED", "LTX_EXPECTED_COMMIT", "SESSION_MINUTES")}
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    def go(**env):
        return subprocess.run(["bash", str(script)], capture_output=True, text=True, env={**base, "W": str(tmp_path / "w"), **env}, timeout=60)
    assert go().returncode != 0 and "LTX_DOWNLOAD_APPROVED" in go().stderr                                 # no approval
    assert "LTX_EXPECTED_COMMIT" in go(LTX_DOWNLOAD_APPROVED="x").stderr                                    # no pinned code revision
    wrong = go(LTX_DOWNLOAD_APPROVED="x", LTX_EXPECTED_COMMIT="0" * 40)
    assert wrong.returncode == 2 and "expected" in wrong.stdout                                             # not the reviewed commit
    for minutes in ("", "abc", "5", "9999"):                                                                 # invalid session length (only reached on a clean tree at HEAD)
        done = go(LTX_DOWNLOAD_APPROVED="x", LTX_EXPECTED_COMMIT=head, SESSION_MINUTES=minutes or "x")
        assert done.returncode == 2 and ("SESSION_MINUTES" in done.stdout or "local modifications" in done.stdout), done.stdout
    assert not (tmp_path / "w" / "ComfyUI").exists() and not (REPO / "ComfyUI").exists()                      # nothing cloned or downloaded
    text = script.read_text(encoding="utf-8")
    assert text.index("LTX_DOWNLOAD_APPROVED:?") < text.index("== 0. refusals") < text.index("== 1. host") < text.index("git clone") < text.index("curl -L")
    assert text.index("host_check.py") < text.index("git clone") and "exactly two" in text
    assert text.index("local modifications: refusing") < text.index("pip install") < text.index("main.py")      # clean-tree check precedes any install or launch
    assert text.index("something already listens on port") < text.index("main.py") and "kill -0" in text
    assert "port_owner.py" in text and "ss -ltnp" not in text and text.index("port_owner.py") < text.index("object_info.json")   # mandatory /proc proof, no optional tool
    assert "8188" not in text and '"${launch[@]}"' in text and 'CUDA_VISIBLE_DEVICES="$n"' in text          # fresh ports, argument array, one card per worker
    assert text.index("need_pass") < text.index("git clone") and "gpu_attribution.py" in text and "concurrent_check.py" in text
    assert 'clone ltxvideo_nodes "$W/ComfyUI-LTXVideo-src"' in text and 'clone ltxvideo_nodes "$COMFY' not in text   # source only, never a node pack


def test_pin_paths_used_by_the_gpu_script_resolve():
    import re
    text = (REPO / "scripts" / "kaggle" / "ltx_first_test.sh").read_text(encoding="utf-8")
    literal = set(re.findall(r'pin\s+"?((?:sources|workflow)\.[a-z_.]+)', text))
    for path in literal:
        node = PINS
        for part in path.split("."):
            node = node[part]
        assert node
    assert PINS["files"][0]["role"].startswith("ltx_checkpoint") and PINS["files"][1]["role"] == "text_encoder"   # fetch 0; fetch 1


def gate_run(host, monkeypatch, *extra, approved="tester", gpu_index="0"):
    if approved:
        monkeypatch.setenv("LTX_DOWNLOAD_APPROVED", approved)
    else:
        monkeypatch.delenv("LTX_DOWNLOAD_APPROVED", raising=False)
    index = ["--gpu-index", gpu_index] if gpu_index is not None else []
    code = ft.main(base_args(host, "--execute", *index, *extra))
    return code, json.loads((host[2] / "test_receipt.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", ["no approval", "one gpu only", "three gpus", "not a t4", "wrong indices", "no gpu index", "other gpu busy",
                                  "skip static verify", "no deadline", "bad deadline", "short deadline", "no nvidia-smi"])
def test_main_refuses_every_ungated_execution_with_zero_requests(host, monkeypatch, name):
    server = host[0]
    extra, approved, index = [], "tester", "0"
    if name == "no approval":
        approved = ""
    elif name == "one gpu only":
        monkeypatch.setattr(ft, "physical_gpus", lambda: [dict(PHYS[0])])
    elif name == "three gpus":
        monkeypatch.setattr(ft, "physical_gpus", lambda: [dict(PHYS[0]), dict(PHYS[1]), {**PHYS[1], "index": 2, "uuid": "GPU-synthetic-2"}])
    elif name == "not a t4":
        monkeypatch.setattr(ft, "physical_gpus", lambda: [dict(PHYS[0]), {**PHYS[1], "name": "NVIDIA A100"}])
    elif name == "wrong indices":
        monkeypatch.setattr(ft, "physical_gpus", lambda: [dict(PHYS[0]), {**PHYS[1], "index": 3}])
    elif name == "no gpu index":
        index = None
    elif name == "other gpu busy":
        monkeypatch.setattr(ft, "physical_gpus", lambda: [dict(PHYS[0]), {**PHYS[1], "memory_used_mb": 7000.0}])
    elif name == "skip static verify":
        extra = ["--skip-static-verify"]
    elif name == "no deadline":
        monkeypatch.delenv("GRANTHSTUDIO_SESSION_DEADLINE")
    elif name == "bad deadline":
        monkeypatch.setenv("GRANTHSTUDIO_SESSION_DEADLINE", "tomorrow-ish")
    elif name == "short deadline":
        monkeypatch.setenv("GRANTHSTUDIO_SESSION_DEADLINE", "2000-01-01T00:00:00+00:00")
    elif name == "no nvidia-smi":
        monkeypatch.setattr(ft, "physical_gpus", lambda: None)
    code, receipt = gate_run(host, monkeypatch, *extra, approved=approved, gpu_index=index)
    assert code == 1 and receipt["verdict"] == "NOT_RUN" and receipt["reason"].startswith("execution gate:"), receipt["reason"]
    assert server.posts == [] and server.uploads == {} and "results" not in receipt


def test_a_busy_other_card_is_fine_only_when_the_concurrent_stage_says_so(host, monkeypatch):
    monkeypatch.setattr(ft, "physical_gpus", lambda: [dict(PHYS[0]), {**PHYS[1], "memory_used_mb": 7000.0}])
    args = ft.parse_args(base_args(host, "--execute", "--gpu-index", "0", "--allow-other-gpu-busy"))
    monkeypatch.setenv("LTX_DOWNLOAD_APPROVED", "tester")
    assert ft.execution_gate_problems(args) == []
    assert ft.execution_gate_problems(ft.parse_args(base_args(host, "--execute", "--gpu-index", "0")))     # isolated stage: not allowed


def test_a_resumed_identical_run_reuses_the_clip_without_another_job(host):
    server = host[0]
    first = run(host, "--execute")[1]
    second_code, second = run(host, "--execute")
    assert [r["status"] for r in first["results"]] == ["complete"] and [r["status"] for r in second["results"]] == ["resumed"]
    assert second["reused_earlier_output"] is True and second["clip"]["sha256"] == first["clip"]["sha256"]
    assert len(server.posts) == 1 and len(server.uploads) == 1                       # nothing was submitted the second time


def test_expected_precision_is_recorded_not_assumed_to_be_fp16(host):
    code, receipt = run(host)
    models = yaml.safe_load((host[2] / "project" / "config" / "models.yaml").read_text(encoding="utf-8"))["ltx"]
    assert models["precision"] == models["runtime"]["precision"] == receipt["inputs"]["precision_expected"] == "fp32"
    code, receipt = run(host, "--precision", "bf16")
    assert receipt["inputs"]["precision_expected"] == "bf16"


@pytest.mark.skipif(not have_tool("bash") or not have_tool("git") or not have_tool("ffmpeg"), reason="bash/git/ffmpeg missing")
def test_gpu_script_refuses_a_legacy_installed_ltxvideo_pack_before_any_clone_or_install(tmp_path):
    """Behavioural: a clean clone at an expected commit, a fake single T4, and a leftover custom_nodes/ComfyUI-LTXVideo."""
    import os, shutil
    clone = tmp_path / "repo"
    subprocess.run(["git", "clone", "-q", str(REPO), str(clone)], check=True, capture_output=True)
    for rel in ("scripts/kaggle/ltx_first_test.sh", "config/ltx_098_pins.yaml"):          # test the working-tree script, committed inside the clone
        shutil.copyfile(REPO / rel, clone / rel)
    for cmd in (["config", "user.email", "t@t"], ["config", "user.name", "t"], ["add", "-A"], ["commit", "-qm", "test copy", "--allow-empty"]):
        subprocess.run(["git", "-C", str(clone), *cmd], check=True, capture_output=True)
    head = subprocess.run(["git", "-C", str(clone), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    # functions in BASH_ENV shadow the real tools for the non-interactive script (a PATH shim would lose to MSYS's own /usr/bin on Windows)
    shims = tmp_path / "shims.sh"
    py = Path(sys.executable).as_posix()
    shims.write_text(chr(10).join(["nvidia-smi() { echo 'GPU 0: Tesla T4 (UUID: GPU-synthetic)'; }",
                                   "df() { echo Avail; echo 500G; }", f'python() {{ case "$1" in *host_check.py) return 0;; esac; "{py}" "$@"; }}', ""]), encoding="utf-8")
    work = tmp_path / "w"
    (work / "ComfyUI" / "custom_nodes" / "ComfyUI-LTXVideo").mkdir(parents=True)
    env = {**os.environ, "BASH_ENV": str(shims), "W": str(work),
           "LTX_DOWNLOAD_APPROVED": "tester", "LTX_EXPECTED_COMMIT": head, "SESSION_MINUTES": "60"}
    done = subprocess.run(["bash", str(clone / "scripts" / "kaggle" / "ltx_first_test.sh")], capture_output=True, text=True, env=env, timeout=120)
    assert done.returncode == 4 and "legacy" in done.stdout and "installs no LTXVideo node pack" in done.stdout, (done.stdout, done.stderr)
    assert "session deadline:" in done.stdout and "fresh ports:" in done.stdout    # every earlier refusal was passed
    assert not (work / "ComfyUI" / ".git").exists() and not (work / "ComfyUI-LTXVideo-src").exists()    # nothing was cloned
    assert not (work / "ltx_first_test_evidence" / "pip_freeze.txt").exists()                           # nothing was installed


@pytest.mark.skipif(not have_tool("bash"), reason="bash missing")
def test_the_scripts_port_probe_line_refuses_an_occupied_port_and_allows_a_free_one():
    import socket
    line = next(l for l in (REPO / "scripts" / "kaggle" / "ltx_first_test.sh").read_text(encoding="utf-8").splitlines()
                if l.strip().startswith("python -c") and "connect_ex" in l).strip()
    srv = socket.socket(); srv.bind(("127.0.0.1", 0)); srv.listen(1)
    taken = srv.getsockname()[1]
    py = Path(sys.executable).as_posix()
    def probe(port):
        script = f'python() {{ "{py}" "$@"; }}; P={port}; {line}; echo "reached-$?"'
        return subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=30)
    occupied = probe(taken)
    assert "something already listens" in occupied.stdout and occupied.returncode == 2          # the script exits 2 here
    srv.close()
    free = probe(taken)                                                                           # the same port, now closed
    assert "something already listens" not in free.stdout and "reached-1" in free.stdout


def test_port_owner_matches_a_listening_socket_to_the_process_that_holds_it(tmp_path):
    import importlib.util as iu
    nl = chr(10)
    spec = iu.spec_from_file_location("port_owner", REPO / "scripts" / "kaggle" / "port_owner.py")
    po = iu.module_from_spec(spec); spec.loader.exec_module(po)
    proc = tmp_path / "proc"; (proc / "net").mkdir(parents=True)
    header = "  sl  local_address rem_address   st tx_queue rx_queue tr tm->when retrnsmt   uid  timeout inode"
    row = lambda port, state, inode: f"   0: 0100007F:{port:04X} 00000000:0000 {state} 00000000:00000000 00:00000000 00000000  1000        0 {inode} 1 0000000000000000 100 0 0 10 0"
    (proc / "net" / "tcp").write_text(nl.join([header, row(8190, "0A", 111), row(8190, "01", 222), row(9999, "0A", 333)]), encoding="utf-8")
    (proc / "net" / "tcp6").write_text(header + nl, encoding="utf-8")
    assert po.listening_inodes(proc, 8190) == {"111"}                          # LISTEN rows only, right port only
    for pid in (10, 20):
        (proc / str(pid) / "fd").mkdir(parents=True)
    try:
        os.symlink("socket:[111]", proc / "10" / "fd" / "3")                      # pid 10 holds the listener
        os.symlink("socket:[222]", proc / "20" / "fd" / "3")                      # pid 20 only holds a connected socket
    except OSError:
        pytest.skip("symlinks unavailable (the logic is exercised by the Linux run)")
    assert po.main(["10", "8190", "--proc-root", str(proc)]) == 0
    assert po.main(["20", "8190", "--proc-root", str(proc)]) == 1              # another process answering on the port is refused
    assert po.main(["10", "7777", "--proc-root", str(proc)]) == 1              # nothing listens there
    assert po.main(["30", "8190", "--proc-root", str(proc)]) == 2              # cannot inspect: refusal, never a pass


def test_first_test_allows_exactly_one_attempt_and_reports_out_of_memory_without_retrying(host, tmp_path):
    server = host[0]
    server.auto_status = "error"                       # every job the fake accepts fails, like an exhausted GPU would
    log = tmp_path / "comfyui.log"
    log.write_text("got prompt" + chr(10) + "torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 2.00 GiB" + chr(10), encoding="utf-8")
    code, receipt = run(host, "--execute", "--comfy-log", str(log))
    assert code == 1 and receipt["verdict"] == "FAIL" and receipt["out_of_memory"] is True
    assert "CUDA out of memory" in receipt["reason"] and "not retried" in receipt["reason"]
    assert receipt["attempts_allowed_per_task"] == 1 and len(server.posts) == 1          # one submission, never a second attempt
    assert receipt["results"][0]["attempts"] == 1


def test_a_plain_failure_is_a_fail_without_the_oom_claim(host, tmp_path):
    host[0].auto_status = "error"
    log = tmp_path / "comfyui.log"; log.write_text("some other error" + chr(10), encoding="utf-8")
    code, receipt = run(host, "--execute", "--comfy-log", str(log))
    assert receipt["verdict"] == "FAIL" and receipt["out_of_memory"] is False and "out of memory" not in receipt["reason"].lower()
    assert len(host[0].posts) == 1


def test_oom_markers_reads_only_the_log_tail_and_the_detail(tmp_path):
    log = tmp_path / "l.log"; log.write_text(chr(10).join(["fine"] * 500 + ["CUDA error: out of memory"]), encoding="utf-8")
    assert ft.oom_markers(log) == ["CUDA error: out of memory"]
    assert ft.oom_markers(None, "ComfyUI execution error") == [] and ft.oom_markers(None, "OutOfMemoryError: x")


def test_gpu_notebook_is_generated_valid_and_cannot_run_until_a_human_fills_it():
    import ast
    nb = json.loads((REPO / "notebooks" / "kaggle_ltx_first_test.ipynb").read_text(encoding="utf-8"))
    code = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]
    for source in code:
        ast.parse(source)
    params = code[0]
    assert 'APPROVER = ""' in params and 'EXPECTED_COMMIT = ""' in params                  # nothing is signed on anyone's behalf
    assert "assert APPROVER.strip()" in params and "[0-9a-f]{40}" in params
    namespace = {}
    with pytest.raises(AssertionError, match="APPROVER"):
        exec(params, namespace)                                                             # the unfilled notebook stops at its first cell
    joined = "\n".join(code)
    assert "assert head == EXPECTED_COMMIT" in joined and "scripts/kaggle/ltx_first_test.sh" in joined and "LTX_DOWNLOAD_APPROVED" in joined
    assert joined.index("assert head == EXPECTED_COMMIT") < joined.index("ltx_first_test.sh")   # commit check precedes the download script
    spec = importlib.util.spec_from_file_location("build_ltx_notebook", REPO / "scripts" / "kaggle" / "build_ltx_notebook.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    assert json.dumps(nb, indent=1) == json.dumps({"cells": [mod.cell(k, s) for k, s in mod.CELLS], "nbformat": 4, "nbformat_minor": 5,
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python"}}}, indent=1)


def test_variant_b_is_a_genuinely_different_synthetic_shot_with_its_own_project(host, tmp_path):
    server = host[0]
    code_a, a = run(host, "--execute", "--gpu-index", "0")
    other = (tmp_path / "work_b", )
    host_b = (server, host[1], tmp_path / "work_b")
    code_b, b = run(host_b, "--execute", "--gpu-index", "1", "--variant", "b")
    assert a["variant"] == "a" and b["variant"] == "b" and a["gpu_index"] == 0 and b["gpu_index"] == 1
    graph_a, graph_b = server.posts[0]["prompt"], server.posts[1]["prompt"]
    assert graph_a["6"]["inputs"]["text"] == "slight head turn" and graph_b["6"]["inputs"]["text"] == "slow camera push-in"
    assert graph_a["78"]["inputs"]["image"] != graph_b["78"]["inputs"]["image"]              # different staged still
    assert graph_a["102"]["inputs"]["noise_seed"] != graph_b["102"]["inputs"]["noise_seed"] or graph_a["6"] != graph_b["6"]
    ja, jb = a["journal"], b["journal"]
    assert ja["namespace"] != jb["namespace"] and ja["job_token"] != jb["job_token"]         # separate stores: separate namespaces and tokens
    assert (host[2] / "project").resolve() != (host_b[2] / "project").resolve()
    assert len(server.posts) == 2 and len(server.uploads) == 2


def test_gpu_index_is_exported_so_the_worker_measures_its_own_card(host, monkeypatch):
    monkeypatch.delenv("GRANTHSTUDIO_GPU_INDEX", raising=False)
    run(host, "--gpu-index", "1")
    import os
    assert os.environ["GRANTHSTUDIO_GPU_INDEX"] == "1"
    monkeypatch.delenv("GRANTHSTUDIO_GPU_INDEX")


def test_retry_test_replaces_the_first_output_with_a_fresh_generation_on_a_changed_seed(host, tmp_path):
    server, models, work = host
    first = run(host, "--execute")[1]
    first_clip = first["clip"]["sha256"]
    other = tmp_path / "other.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "mandelbrot=size=768x512:rate=24", "-frames:v", "49", "-c:v", "libx264",
                    "-threads", "1", "-pix_fmt", "yuv420p", str(other)], check=True, timeout=60)
    server.view_bytes = other.read_bytes()                                     # the second generation produces different pixels
    code, retry = run(host, "--execute", "--retry-test")
    assert (work / "test_receipt.json").is_file() and (work / "retry_receipt.json").is_file()      # the first receipt is kept
    assert retry["verdict"] == "PASS", retry["reason"]
    assert all(retry["retry_checks"].values()), retry["retry_checks"]
    assert retry["first_output"]["clip_sha256"] == first_clip != retry["second_output"]["clip_sha256"]
    assert retry["first_output"]["seed"] != retry["second_output"]["seed"]
    assert len(server.posts) == 2 and server.sampler_runs == 2                  # the sampler really ran twice
    assert "101" not in retry["cached_nodes_reported"] and "102" not in retry["cached_nodes_reported"]
    assert retry["journal"]["rejections"][0]["reason"].startswith("controlled output-rejection")


def test_retry_test_refuses_without_a_finished_first_run_and_does_not_submit(host):
    code, retry = run(host, "--execute", "--retry-test")
    assert retry["verdict"] == "NOT_RUN" and "nothing to reject" in retry["reason"] and host[0].posts == []


def test_retry_test_fails_when_the_server_reports_no_cache_information(host, tmp_path):
    server, models, work = host
    run(host, "--execute")
    server.cached_by_pid.clear()                                                # a server that never reports execution_cached
    orig = server.finish
    server.finish = lambda pid, status="success", ts=(1000, 4500): (server.cached_by_pid.pop(pid, None), orig(pid, status, ts))[1]
    code, retry = run(host, "--execute", "--retry-test")
    assert retry["verdict"] == "FAIL" and "history_reports_cache" in retry["reason"]      # cannot prove the sampler executed: not a PASS
