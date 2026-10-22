"""Phase A: Kaggle runtime infrastructure. Synthetic hosts only; no GPU or download is real."""
from __future__ import annotations

import importlib.metadata
import io
import json

import pytest
import yaml

from granthstudio.cli import main
from granthstudio.config import load_models
from granthstudio.errors import ConfigError, IntegrationUnavailable, TaskFailed
from granthstudio.integrity import read_json, sha256_bytes
from granthstudio.runtime import (LocalDirStorage, bootstrap_plan, fetch, get_storage, gpu_status, load_runtime,
                                  preflight, require_gpu_ready, require_single_worker, session_remaining_s,
                                  stop_before_deadline)
from granthstudio.scheduler import Scheduler, Task

T4 = [{"index": 0, "name": "Tesla T4", "memory_total_mb": 15360.0, "memory_used_mb": 0.0, "memory_free_mb": 15000.0}]


def ready_runtime(project, tmp_path, **resources):
    runtime = load_runtime(project)
    runtime["resources"] = {"min_free_vram_mb": 12000, "min_ram_mb": 8000, "min_disk_gb": 0.001,
                            "min_session_remaining_s": 600, **resources}
    runtime["storage"] = {"provider": "local_dir", "path": str(tmp_path / "durable")}
    runtime["python_packages"] = {"pytest": importlib.metadata.version("pytest")}
    runtime["sources"] = {**runtime["sources"], "comfyui_commit": "a" * 40, "node_pack_commit": "b" * 40}
    return runtime


def pinned_models(project):
    models = load_models(project)
    models["ltx"]["runtime"] = {**(models["ltx"].get("runtime") or {}), "comfyui_commit": "a" * 40, "node_pack_commit": "b" * 40}
    return models


def test_gpu_status_parses_nvidia_smi_and_absence_is_not_measured():
    gpus = gpu_status(lambda _: "0, Tesla T4, 15360, 256, 15104\n")
    assert gpus == [{"index": 0, "name": "Tesla T4", "memory_total_mb": 15360.0,
                     "memory_used_mb": 256.0, "memory_free_mb": 15104.0}]
    def missing(_): raise FileNotFoundError("nvidia-smi")
    assert gpu_status(missing) is None


def test_shipped_runtime_config_is_not_gpu_ready(project):
    report = preflight(project, load_models(project), load_runtime(project), T4, 16000)
    assert report["gpu_ready"] is False
    assert report["checks"]["free_vram"]["status"] == "not_configured"
    assert report["checks"]["storage"]["status"] == "not_configured"
    with pytest.raises(IntegrationUnavailable, match="GPU preflight not passed"):
        require_gpu_ready(report)


def test_preflight_passes_only_with_measured_minimums(project, tmp_path, monkeypatch):
    monkeypatch.setenv("GRANTHSTUDIO_SESSION_DEADLINE", "2999-01-01T00:00:00+00:00")
    runtime = ready_runtime(project, tmp_path)
    models = pinned_models(project)
    assert preflight(project, models, runtime, T4, 16000)["gpu_ready"] is True
    low = preflight(project, models, runtime, [{**T4[0], "memory_free_mb": 1000.0}], 16000)
    assert low["gpu_ready"] is False and low["checks"]["free_vram"]["status"] == "fail"
    other = preflight(project, models, runtime, [{**T4[0], "name": "RTX 3050"}], 16000)
    assert other["checks"]["gpu"]["status"] == "fail"
    assert preflight(project, models, runtime, None, None)["checks"]["gpu"]["status"] == "not_measured"
    runtime["python_packages"] = {"pytest": "0.0.0"}
    assert preflight(project, models, runtime, T4, 16000)["checks"]["python_packages"]["status"] == "fail"


def test_session_deadline_stops_launching_and_resume_finishes(tmp_path, monkeypatch, project):
    runtime = load_runtime(project); runtime["resources"]["min_session_remaining_s"] = 600
    monkeypatch.setenv("GRANTHSTUDIO_SESSION_DEADLINE", "2000-01-01T00:00:00+00:00")
    assert session_remaining_s() < 0
    def write(name):
        def run(work): (work / "o.bin").write_bytes(name.encode()); return {"o": "o.bin"}
        return run
    tasks = [Task("tier0", "a", {}, "v", write("a")), Task("tier0", "b", {}, "v", write("b"))]
    first = Scheduler(tmp_path / "s").run(tasks, should_stop=stop_before_deadline(runtime))
    assert [r.status for r in first] == ["deferred", "deferred"]
    monkeypatch.setenv("GRANTHSTUDIO_SESSION_DEADLINE", "2999-01-01T00:00:00+00:00")
    assert [r.status for r in Scheduler(tmp_path / "s").run(tasks, stop_before_deadline(runtime))] == ["complete", "complete"]
    monkeypatch.setenv("GRANTHSTUDIO_SESSION_DEADLINE", "2026-10-22T10:00:00")
    with pytest.raises(ConfigError, match="UTC offset"):
        session_remaining_s()


def test_fetch_verifies_pin_and_never_keeps_a_bad_file(tmp_path):
    data = b"synthetic weights"
    opener = lambda _url: io.BytesIO(data)
    dest = tmp_path / "models" / "w.safetensors"
    assert fetch("https://example.invalid/w", dest, sha256_bytes(data), opener=opener) == sha256_bytes(data)
    assert dest.read_bytes() == data
    bad = tmp_path / "models" / "bad.safetensors"
    with pytest.raises(TaskFailed, match="file discarded"):
        fetch("https://example.invalid/w", bad, "0" * 64, opener=opener)
    assert not bad.exists() and not list(bad.parent.glob(".*.part"))
    with pytest.raises(ConfigError, match="no sha256 pin"):
        fetch("https://example.invalid/w", tmp_path / "unpinned", None, opener=opener)
    assert fetch("https://example.invalid/w", tmp_path / "rec", None, record=True, opener=opener) == sha256_bytes(data)


def test_durable_storage_round_trip_detects_tamper_and_partial_export(tmp_path):
    source = tmp_path / "artifacts"; (source / "tasks").mkdir(parents=True)
    (source / "tasks" / "a.bin").write_bytes(b"one"); (source / "tasks" / ".work-x").mkdir()
    (source / "tasks" / ".work-x" / "junk").write_bytes(b"partial")
    storage = LocalDirStorage(tmp_path / "durable")
    manifest = storage.export(source, "artifacts")
    assert list(manifest["files"]) == ["tasks/a.bin"]
    restored = tmp_path / "restored"; storage.restore("artifacts", restored)
    assert (restored / "tasks" / "a.bin").read_bytes() == b"one"
    (tmp_path / "durable" / "artifacts" / "tasks" / "a.bin").write_bytes(b"tampered")
    with pytest.raises(TaskFailed, match="does not match"):
        storage.restore("artifacts", tmp_path / "again")
    (tmp_path / "durable" / "partial").mkdir()
    with pytest.raises(IntegrationUnavailable, match="no complete export"):
        storage.restore("partial", tmp_path / "x")


def test_storage_provider_must_be_explicit(project):
    with pytest.raises(IntegrationUnavailable, match="O-008"):
        get_storage(load_runtime(project))
    with pytest.raises(ConfigError, match="absolute"):
        get_storage({"storage": {"provider": "local_dir", "path": "relative/dir"}})


def test_dual_t4_gate_is_disabled_and_requests_are_refused(project):
    runtime = load_runtime(project)
    require_single_worker(runtime)
    runtime["workers"]["dual_t4"] = "requested"
    with pytest.raises(IntegrationUnavailable, match="not implemented"):
        require_single_worker(runtime)


def test_bootstrap_requires_every_pin(project, tmp_path):
    runtime = load_runtime(project)
    with pytest.raises(ConfigError, match="unpinned"):
        bootstrap_plan(runtime, tmp_path)
    runtime["sources"] = {"comfyui_repo": "https://example.invalid/ComfyUI.git", "comfyui_commit": "a" * 40,
                          "node_pack_repo": "https://example.invalid/nodes.git", "node_pack_commit": "b" * 40}
    runtime["python_packages"] = {"torch": "synthetic-pin"}
    runtime["downloads"] = [{"name": "ckpt", "url": "https://example.invalid/c", "dest": "checkpoints/c", "sha256": None}]
    with pytest.raises(ConfigError, match="download ckpt sha256"):
        bootstrap_plan(runtime, tmp_path)
    runtime["downloads"][0]["sha256"] = "c" * 64
    commands = bootstrap_plan(runtime, tmp_path)
    assert ["git", "-C", str(tmp_path / "ComfyUI"), "checkout", "--detach", "a" * 40] in commands
    assert commands[-1][-3:] == ["runtime", "fetch", "ckpt"]


def test_cli_run_writes_a_schema_valid_run_receipt(approved_project):
    assert main(["--root", str(approved_project.root), "run", "1", "--execute"]) in (2, 3)
    receipts = list((approved_project.artifacts_dir / "runs").glob("*.json"))
    assert len(receipts) == 1
    receipt = read_json(receipts[0])
    assert receipt["kind"] == "episode_run" and receipt["preflight"]["gpu_ready"] is False
    assert receipt["results"] and {"stage", "status", "task_id"} <= set(receipt["results"][0])


def test_session_refuses_without_storage_and_exports_after_run(approved_project, tmp_path):
    root = str(approved_project.root)
    assert main(["--root", root, "session", "1", "--cpu-only"]) == 3  # no storage provider: O-008
    path = approved_project.root / "config" / "runtime.yaml"
    runtime = yaml.safe_load(path.read_text(encoding="utf-8"))
    runtime["storage"] = {"provider": "local_dir", "path": str(tmp_path / "durable")}
    path.write_text(yaml.safe_dump(runtime), encoding="utf-8")
    assert main(["--root", root, "session", "1"]) == 3  # GPU preflight refuses on this host
    manifest = json.loads((tmp_path / "durable" / "artifacts" / "export_manifest.json").read_text())
    assert any(name.startswith("runs/") for name in manifest["files"]) is False
    assert main(["--root", root, "session", "1", "--cpu-only"]) in (2, 3)
    manifest = json.loads((tmp_path / "durable" / "artifacts" / "export_manifest.json").read_text())
    assert any(name.startswith("runs/") for name in manifest["files"])


def test_source_pin_mismatch_blocks_gpu_readiness(project, tmp_path, monkeypatch):
    monkeypatch.setenv("GRANTHSTUDIO_SESSION_DEADLINE", "2999-01-01T00:00:00+00:00")
    runtime, models = ready_runtime(project, tmp_path), pinned_models(project)
    assert preflight(project, models, runtime, T4, 16000)["gpu_ready"] is True
    runtime["sources"]["node_pack_commit"] = "c" * 40
    report = preflight(project, models, runtime, T4, 16000)
    assert report["checks"]["sources"]["status"] == "fail" and report["gpu_ready"] is False
    with pytest.raises(IntegrationUnavailable, match="sources.*node_pack_commit"):
        require_gpu_ready(report)
    models["ltx"]["runtime"] = None  # unrecorded pins are not "ready" either
    assert preflight(project, models, ready_runtime(project, tmp_path), T4, 16000)["gpu_ready"] is False
