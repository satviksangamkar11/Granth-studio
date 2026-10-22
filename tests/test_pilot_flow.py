"""Phase F: A-F pilot orchestration against a fake ComfyUI. Fixtures, reviewers, rubric and the 'T4' are
synthetic; nothing here shows that the real LTX workflow, GPU timing or video quality work."""
from __future__ import annotations

import subprocess

import pytest
import yaml

from granthstudio import pilotrun
from granthstudio.cli import main
from granthstudio.config import load_models, load_yaml, require_capability
from granthstudio.errors import CapabilityDisabled, ConfigError, GateFailure
from granthstudio.integrity import atomic_write_json, normalize_text, read_json, sha256_file, sha256_obj
from granthstudio.pipeline import load_bundle, plan_tasks
from granthstudio.scheduler import Scheduler
from tests.conftest import have_tool, make_clip
from tests.test_claude_findings import prepare_current_pilot
from tests.test_ltx_integration import FakeComfy

pytestmark = pytest.mark.skipif(not (have_tool("ffmpeg") and have_tool("ffprobe")), reason="media tools missing")
CKPT = "ltxv-2b-0.9.8-distilled.safetensors"
T4 = [{"index": 0, "name": "Tesla T4", "memory_total_mb": 15360.0, "memory_used_mb": 9000.0, "memory_free_mb": 6000.0}]


def graph(extra=""):
    return {"_status": "unvalidated", "_output_node": "9",
            "1": {"class_type": "SyntheticLoader", "inputs": {"ckpt_name": CKPT, "image": "{{START_IMAGE}}", "prompt": "{{MOTION_PROMPT}}",
                  "frames": "{{FRAMES}}", "seed": "{{SEED}}", "fps": "{{FPS}}", "w": "{{WIDTH}}", "h": "{{HEIGHT}}", **({"end": "{{END_IMAGE}}"} if extra else {})}},
            "9": {"class_type": "SyntheticSave", "inputs": {"video": ["1", 0]}}}


@pytest.fixture
def comfy(tmp_path):
    server = FakeComfy()
    server.nodes = {"SyntheticLoader", "SyntheticSave"}
    clip = tmp_path / "server_clip.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "testsrc=size=160x120:rate=24", "-frames:v", "49",
                    "-c:v", "libx264", "-threads", "1", "-pix_fmt", "yuv420p", str(clip)], check=True, timeout=30)
    server.view_bytes = clip.read_bytes()
    server.auto_outputs = {"9": {"videos": [{"filename": "o.mp4", "type": "output"}]}}
    yield server
    server.close()


def add_audio(project):
    for lang in ("mr", "hi"):
        path = project.episodes_dir / "adhyay_01" / f"{lang}.yaml"
        timeline = load_yaml(path)
        for index, entry in enumerate(timeline["entries"]):
            audio = project.artifacts_dir / "audio" / f"{lang}_{index}.wav"
            audio.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=24000:duration=0.2",
                            "-c:a", "pcm_s16le", str(audio)], check=True, timeout=20)
            entry["audio"] = {"path": audio.name, "sha256": sha256_file(audio), "language": lang, "speaker": entry["speaker"],
                              "text_sha256": sha256_obj(normalize_text(entry["text"])), "speech_reviewed_by": "synthetic-test-only"}
        atomic_write_json(path, timeline)


@pytest.fixture
def pilot(approved_project, tmp_path, comfy, monkeypatch):
    project = approved_project
    prepare_current_pilot(project)
    add_audio(project)
    files = {}
    for kind in ("checkpoint", "vae", "text_encoder"):
        path = tmp_path / f"{kind}.bin"; path.write_bytes(f"synthetic {kind}".encode())
        files[kind] = {"path": str(path), "sha256": sha256_file(path)}
    models = load_models(project)
    models["comfyui"]["base_url"] = comfy.url
    models["ltx"].update(checkpoint_sha256=files["checkpoint"]["sha256"],
        capabilities={"i2v": "unvalidated", "flf": "unvalidated"},
        runtime={"files": files, "comfyui_commit": "a" * 40, "node_pack_commit": "b" * 40, "gpu": "T4",
                 "precision": "fp16", "width": 160, "height": 120})
    atomic_write_json(project.root / "config" / "models.yaml", models)
    atomic_write_json(project.root / "workflows" / "comfyui" / "ltx_i2v_098.json", graph())
    atomic_write_json(project.root / "workflows" / "comfyui" / "ltx_flf_098.json", graph("end"))
    monkeypatch.setattr("granthstudio.pipeline.gpu_status", lambda: T4)
    return project


def set_rubric(project, criteria=("identity_continuity", "sacred_fidelity"), budget=None):
    (project.root / "config" / "pilot.yaml").write_text(yaml.safe_dump(
        {"schema_version": 1, "rubric": {"criteria": list(criteria)},
         "acceptance": {"min_accepted_sec_per_gpu_hour": budget}}), encoding="utf-8")


def passes(*names):
    return {name: ("pass", "") for name in names}


def full_run(project, store=None):
    mapping, selected, full, results, receipt = pilotrun.run_pilot(project, 1, store, execute=True, require_gpu=False)
    return mapping, selected, full, results, receipt


def test_benchmark_mode_runs_unvalidated_capabilities_but_strict_mode_still_refuses(pilot, comfy):
    mapping, selected, full, results, receipt = full_run(pilot)
    assert sorted(mapping) == list("ABCDEF") and full is True
    assert all(r.status == "complete" for r in results), [(r.name, r.status, r.detail) for r in results]
    assert len(comfy.posts) == 4  # B, C, D, E
    assert all(r.elapsed_s >= 0 for r in results) and receipt.is_file()
    assert read_json(receipt)["kind"] == "pilot_run"
    strict = load_bundle(pilot, load_models(pilot), 1)
    outcome = {r.name: r.status for r in Scheduler(pilot.artifacts_dir / "tasks" / "strict").run(plan_tasks(strict, Scheduler(pilot.artifacts_dir / "tasks" / "strict")))}
    assert outcome[mapping["B"]] == "not_validated" and len(comfy.posts) == 4  # strict mode never submits


def test_benchmark_mode_still_enforces_pins_and_disabled_capabilities(pilot, comfy):
    models = load_models(pilot)
    models["ltx"]["checkpoint_sha256"] = "0" * 64
    atomic_write_json(pilot.root / "config" / "models.yaml", models)
    _, _, _, results, _ = full_run(pilot)
    assert {r.name: r.status for r in results if r.stage == "tier1"} and all(
        r.status == "not_validated" for r in results if r.stage in ("tier1", "tier2"))
    assert comfy.posts == []
    models = load_models(pilot); models["ltx"]["capabilities"]["flf"] = "disabled"
    atomic_write_json(pilot.root / "config" / "models.yaml", models)
    with pytest.raises(CapabilityDisabled, match="disabled"):
        from granthstudio.config import verify_benchmark_runtime
        verify_benchmark_runtime(models, "flf", "v")


def test_receipts_review_report_and_pilot_evidence_validates_capability(pilot, comfy):
    full_run(pilot)
    summary = pilotrun.build_receipts(pilot, 1, None)
    assert summary["written"] == list("ABCDEF") and summary["awaiting_review"] == list("ABCDEF")
    b = read_json(pilot.benchmarks_dir / "pilot_af" / "receipts" / "B.json")
    assert (b["capability"], b["gpu"], b["peak_vram_mb"], b["attempts"], b["accepted"], b["outcome"]) == ("i2v", "T4", 9000.0, 1, None, "pending")
    assert b["gpu_seconds_total"] > 0 and "estimated" in b["measurement_notes"]["gpu_seconds_total"]
    assert read_json(pilot.benchmarks_dir / "pilot_af" / "receipts" / "A.json")["gpu"] == "CPU"
    assert read_json(pilot.benchmarks_dir / "pilot_af" / "receipts" / "F.json")["video_seconds"] == 0.0
    report, path = pilotrun.pilot_report(pilot, 1, None)
    assert report["throughput"]["kind"] == "not_computed" and "NOT DECIDED" in report["decision"]["production_go"]
    assert report["shots"]["B"]["diagnostics"]["color_distribution"]["status"] == "computed"
    assert report["shots"]["B"]["diagnostics"]["face_embedding_similarity"]["status"] == "not_computed"
    assert report["shots"]["B"]["receipt"]["capability_status"]["kind"] == "unvalidated"
    assert all(line["asr_alignment"]["kind"] == "not_computed" for line in report["languages"]["mr"])
    assert report["languages"]["hi"][0]["translation"]["semantic_comparison"]["kind"] == "not_computed"

    with pytest.raises(ConfigError, match="O-005"):
        pilotrun.record_review(pilot, 1, None, "B", "synthetic-test-only", "accept", passes("identity_continuity"), "")
    set_rubric(pilot)
    with pytest.raises(ConfigError, match="rate exactly"):
        pilotrun.record_review(pilot, 1, None, "B", "synthetic-test-only", "accept", passes("identity_continuity"), "")
    with pytest.raises(GateFailure, match="failed criterion"):
        pilotrun.record_review(pilot, 1, None, "B", "synthetic-test-only", "accept",
                               {"identity_continuity": ("fail", "drifted"), "sacred_fidelity": ("pass", "")}, "")
    for label in "ABDEF":
        pilotrun.record_review(pilot, 1, None, label, "synthetic-test-only", "accept", passes("identity_continuity", "sacred_fidelity"), "")
    pilotrun.record_review(pilot, 1, None, "C", "synthetic-test-only", "reject",
                           {"identity_continuity": ("fail", "pose differs"), "sacred_fidelity": ("pass", "")}, "FLF not useful")
    summary = pilotrun.build_receipts(pilot, 1, None)
    assert summary["awaiting_review"] == []
    c = read_json(pilot.benchmarks_dir / "pilot_af" / "receipts" / "C.json")
    assert (c["accepted"], c["outcome"]) == (False, "fail")

    # a review bound to different measurements is ignored rather than trusted
    stale = pilot.benchmarks_dir / "pilot_af" / "reviews" / "D.json"
    review = read_json(stale); review["measurement_sha256"] = "0" * 64; atomic_write_json(stale, review)
    assert pilotrun.build_receipts(pilot, 1, None)["awaiting_review"] == ["D"]
    pilotrun.record_review(pilot, 1, None, "D", "synthetic-test-only", "accept", passes("identity_continuity", "sacred_fidelity"), "")
    assert pilotrun.build_receipts(pilot, 1, None)["awaiting_review"] == []

    report, _ = pilotrun.pilot_report(pilot, 1, None)
    assert report["throughput"]["kind"] == "estimated" and report["throughput"]["value"]["accepted_sec_per_gpu_hour"] > 0
    assert report["meets_budget"]["kind"] == "not_computed" and report["acceptance_budget"]["kind"] == "not_computed"
    assert report["flf_comparison"]["shots"]["C"]["outcome"] == "fail"

    # the loop is closed: pilot evidence, plus a human flipping the status, validates I2V but not the rejected FLF
    models = load_models(pilot)
    template = pilot.root / "workflows" / "comfyui" / "ltx_i2v_098.json"
    models["ltx"]["capabilities"]["i2v"] = "validated"
    from granthstudio.comfy import load_template
    version = load_template(template).version
    assert require_capability(models, "i2v", pilot.benchmarks_dir, version)["shot"] in ("B", "D", "E")
    models["ltx"]["capabilities"]["flf"] = "validated"
    with pytest.raises(CapabilityDisabled, match="no passing benchmark receipt"):
        require_capability(models, "flf", pilot.benchmarks_dir, load_template(pilot.root / "workflows" / "comfyui" / "ltx_flf_098.json").version)


def test_budget_comparison_uses_only_the_users_number(pilot):
    full_run(pilot)
    pilotrun.build_receipts(pilot, 1, None)
    set_rubric(pilot, budget=1.0)
    for label in "ABCDEF":
        pilotrun.record_review(pilot, 1, None, label, "synthetic-test-only", "accept", passes("identity_continuity", "sacred_fidelity"), "")
    pilotrun.build_receipts(pilot, 1, None)
    report, _ = pilotrun.pilot_report(pilot, 1, None)
    assert report["acceptance_budget"]["value"] == 1.0 and report["meets_budget"]["value"] is True
    assert "evidence only" in report["decision"]["production_go"]


def test_recovery_evidence_comes_from_two_real_runs_and_rejects_same_store(pilot):
    mapping, selected, _, _, _ = full_run(pilot, "clean")
    scheduler = Scheduler(pilotrun.store_for(pilot, 1, "resumed"))
    bundle = pilotrun._bundle(pilot, load_models(pilot), 1)
    _, subset, _ = pilotrun.selection(bundle, scheduler)
    interrupted = scheduler.run(subset[:3])  # simulate a crash after the first tasks
    assert [r.status for r in interrupted] == ["complete"] * 3
    _, _, _, results, _ = full_run(pilot, "resumed")
    assert [r.status for r in results].count("resumed") == 3
    pilotrun.build_receipts(pilot, 1, "clean")  # writes the pilot plan snapshot the evidence binds to
    path = pilotrun.build_recovery_evidence(pilot, 1, "clean", "resumed", "synthetic-test-only")
    evidence = read_json(path)
    assert evidence["clean_outputs"]["mr_video"]["sha256"] == evidence["resumed_outputs"]["mr_video"]["sha256"]
    assert evidence["clean_outputs"]["mr_video"]["path"] != evidence["resumed_outputs"]["mr_video"]["path"]
    with pytest.raises(GateFailure, match="different scheduler stores|alias one file"):
        pilotrun.build_recovery_evidence(pilot, 1, "clean", "clean", "synthetic-test-only")
    with pytest.raises(GateFailure, match="not a clean run|no resumed task"):
        pilotrun.build_recovery_evidence(pilot, 1, "resumed", "clean", "synthetic-test-only")


def test_pilot_cli_surface(pilot, capsys):
    root = ["--root", str(pilot.root)]
    assert main([*root, "pilot", "run", "1"]) == 0
    out = capsys.readouterr().out
    assert "assembly included" in out and "dry run" in out and out.count("planned") >= 8
    assert main([*root, "pilot", "run", "2"]) == 1  # the pilot chapter is Adhyay 1
    assert main([*root, "pilot", "review", "1", "--shot", "B", "--reviewer", "x", "--decision", "accept"]) == 1  # no --confirm
    assert main([*root, "pilot", "run", "1", "--execute", "--cpu-only"]) == 0
    assert main([*root, "pilot", "receipts", "1"]) == 0
    assert "awaiting human review: A, B, C, D, E, F" in capsys.readouterr().out
    assert main([*root, "pilot", "report", "1"]) == 0
    assert "evidence only" in capsys.readouterr().out
    assert main([*root, "pilot", "recovery-evidence", "1", "--clean", "a", "--resumed", "b", "--reviewer", "x"]) == 1


def test_pilot_selection_includes_lipsync_dependencies_of_assembly(pilot, tmp_path):
    from tests.test_lipsync import LIP, configure
    path = pilot.episodes_dir / "adhyay_01" / "manifest.yaml"
    manifest = load_yaml(path)
    speaking = next(sh for sc in manifest["scenes"] for sh in sc["shots"] if sh["dialogue_ids"])
    speaking["lip_sync"] = LIP
    SHOT1 = speaking["shot_id"]
    atomic_write_json(path, manifest)
    configure(pilot, tmp_path)
    scheduler = Scheduler(pilotrun.store_for(pilot, 1, "lip"))
    bundle = pilotrun._bundle(pilot, load_models(pilot), 1)
    mapping, selected, full = pilotrun.selection(bundle, scheduler)
    names = [t.name for t in selected]
    assert full and f"lipsync_mr_{SHOT1}" in names and "assemble_mr" in names
    assert names.index(f"lipsync_mr_{SHOT1}") < names.index("assemble_mr")
    ids = {t.task_id() for t in selected}
    assert all(dep in ids for t in selected for dep in t.depends_on)          # closed under dependencies
    assert [r.status for r in scheduler.status(selected)].count("missing") == len(selected)  # plan validates (_plan ran)
    assert [t.name for t in selected] == [t.name for t in pilotrun.selection(bundle, scheduler)[1]]  # deterministic
