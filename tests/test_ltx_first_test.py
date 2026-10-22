"""scripts/ltx_first_test.py end to end against a FAKE ComfyUI: plumbing only. No real model, GPU or ComfyUI is involved,
the weights are a few synthetic bytes, and a run with --skip-static-verify can never produce PASS."""
from __future__ import annotations

import importlib.util
import json
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
    yield server, models, tmp_path / "work"
    server.close()


def base_args(host, *extra):
    server, models, work = host
    return ["--workdir", str(work), "--comfy-url", server.url, "--models-dir", str(models), "--min-disk-gb", "0.001", *extra]


def run(host, *extra):
    """CPU plumbing only: drives the private runner with the gates off. main() always enforces them for --execute."""
    work = host[2]
    code = ft._run(ft.parse_args(base_args(host, "--skip-static-verify", *extra)), enforce_gates=False)
    return code, json.loads((work / "test_receipt.json").read_text(encoding="utf-8"))


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
    assert text.index("LTX_DOWNLOAD_APPROVED:?") < text.index("== 0. refusals") < text.index("== 1. GPU") < text.index("git clone") < text.index("curl -L")
    assert text.index("local modifications: refusing") < text.index("pip install") < text.index("main.py")      # clean-tree check precedes any install or launch
    assert text.index("something already serves port") < text.index("main.py") and "kill -0 $COMFY_PID" in text
    assert "custom_nodes/ComfyUI-LTXVideo" not in text.replace("$W/ComfyUI-LTXVideo-src", "")                 # LTXVideo is never installed as a node pack


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


def gate_run(host, monkeypatch, *extra, approved="tester"):
    if approved:
        monkeypatch.setenv("LTX_DOWNLOAD_APPROVED", approved)
    else:
        monkeypatch.delenv("LTX_DOWNLOAD_APPROVED", raising=False)
    code = ft.main(base_args(host, "--execute", *extra))
    return code, json.loads((host[2] / "test_receipt.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", ["no approval", "two gpus", "not a t4", "skip static verify", "no deadline", "bad deadline", "short deadline"])
def test_main_refuses_every_ungated_execution_with_zero_requests(host, monkeypatch, name):
    server = host[0]
    extra, approved = [], "tester"
    if name == "no approval":
        approved = ""
    elif name == "two gpus":
        monkeypatch.setattr("granthstudio.runtime.gpu_status", lambda: [T4[0], T4[0]])
    elif name == "not a t4":
        monkeypatch.setattr("granthstudio.runtime.gpu_status", lambda: [{**T4[0], "name": "NVIDIA A100"}])
    elif name == "skip static verify":
        extra = ["--skip-static-verify"]
    elif name == "no deadline":
        monkeypatch.delenv("GRANTHSTUDIO_SESSION_DEADLINE")
    elif name == "bad deadline":
        monkeypatch.setenv("GRANTHSTUDIO_SESSION_DEADLINE", "tomorrow-ish")
    elif name == "short deadline":
        monkeypatch.setenv("GRANTHSTUDIO_SESSION_DEADLINE", "2000-01-01T00:00:00+00:00")
    code, receipt = gate_run(host, monkeypatch, *extra, approved=approved)
    assert code == 1 and receipt["verdict"] == "NOT_RUN" and receipt["reason"].startswith("execution gate:"), receipt["reason"]
    assert server.posts == [] and server.uploads == {} and "results" not in receipt


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
