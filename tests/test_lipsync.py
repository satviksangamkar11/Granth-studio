"""Optional lip-sync (frozen sections 10 and 13): refuses until a human validates a runner for the approved style.

The fake runner below is a test double that only re-tints the video; it proves wiring, not lip-sync quality.
"""
from __future__ import annotations

import json
import sys

import pytest
import yaml

from granthstudio.config import load_models, load_yaml
from granthstudio.errors import GateFailure, GranthError
from granthstudio.ffmpeg import validate_video
from granthstudio.integrity import atomic_write_json, read_json
from granthstudio.pipeline import episode_store, load_bundle, plan_tasks
from granthstudio.scheduler import Scheduler
from tests.conftest import have_tool
from granthstudio.lipsync import style_identity
from tests.test_review_regressions import make_cpu_project

pytestmark = pytest.mark.skipif(not (have_tool("ffmpeg") and have_tool("ffprobe")), reason="media tools missing")

LIP = {"languages": ["mr"], "reviewed_by": "synthetic-test-only"}
SHOT1, SHOT2 = "a01_s01_sh01", "a01_s01_sh02"

RUNNER = '''
import json, subprocess, sys
payload = json.load(sys.stdin)
with open(r"{log}", "a") as handle:
    handle.write(json.dumps(payload) + "\\n")
if {fail}:
    sys.stderr.write("synthetic runner failure"); sys.exit(1)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", payload["video_path"], "-vf", "hue=h=90",
                "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", payload["out_path"]], check=True)
print("{{}}")
'''


@pytest.fixture(autouse=True)
def ready_host(approved_project, tmp_path, monkeypatch):
    """Lip-sync runners are GPU-capable tasks: run them on a synthetic ready host (not a real one)."""
    from tests.test_pilot_flow import make_gpu_ready
    make_gpu_ready(approved_project, tmp_path, monkeypatch)


def set_lip_sync(project, shot_id=SHOT1, lip=LIP):
    path = project.episodes_dir / "adhyay_01" / "manifest.yaml"
    manifest = load_yaml(path)
    for shot in manifest["scenes"][0]["shots"]:
        if shot["shot_id"] == shot_id:
            shot["lip_sync"] = lip
    atomic_write_json(path, manifest)


def style_dict(registry_style="approved", version=1, prefix="synthetic style"):
    return None if registry_style is None else {"style_id": "style_synth", "version": version, "status": registry_style,
        **({"approved_by": "synthetic-test-only"} if registry_style == "approved" else {}),
        "prompt_prefix": prefix, "negative_prompt": ""}


def configure(project, tmp_path, fail=False, style_id="style_synth", status="validated", registry_style="approved",
              version=1, prefix="synthetic style", bind=True):
    """Write a lipsync runner section and the visual-assets style; returns the runner log path."""
    log = tmp_path / "runner.log"
    script = tmp_path / "runner.py"
    script.write_text(RUNNER.format(log=str(log).replace("\\", "/"), fail=fail), encoding="utf-8")
    models = load_models(project)
    models["lipsync"] = {"status": status, "command": [sys.executable, str(script)], "model": "synthetic-double",
                         "revision": "test", "validated_style_id": style_id, "timeout_s": 120}
    if bind:  # the runner was validated against exactly this approved style version and content
        identity = style_identity(style_dict("approved", version, prefix))
        models["lipsync"].update(validated_style_version=identity["version"], validated_style_sha256=identity["sha256"])
    atomic_write_json(project.root / "config" / "models.yaml", models)
    style = style_dict(registry_style, version, prefix)
    (project.canon_dir / "visual_assets.yaml").write_text(
        yaml.safe_dump({"schema_version": 1, "style": style, "designs": [], "assets": []}), encoding="utf-8")
    return log


def run_all(project):
    current = load_bundle(project, load_models(project), 1)
    scheduler = Scheduler(episode_store(project, 1))
    tasks = plan_tasks(current, scheduler)
    results = {r.name: r for r in scheduler.run(tasks)}
    return scheduler, tasks, results


def test_default_config_refuses_and_blocks_assembly(approved_project):
    set_lip_sync(approved_project)
    make_cpu_project(approved_project)
    scheduler, tasks, results = run_all(approved_project)
    lip = results[f"lipsync_mr_{SHOT1}"]
    assert lip.status == "not_validated" and "NOT VALIDATED" in lip.detail
    assert not scheduler.task_dir(next(t for t in tasks if t.stage == "lipsync")).exists()
    assert results["assemble_mr"].status == "blocked"
    assert results["assemble_hi"].status == "complete"  # Hindi did not ask for lip-sync
    assert [t.name for t in tasks if t.stage == "lipsync"] == [f"lipsync_mr_{SHOT1}"]


@pytest.mark.parametrize("kwargs,message", [
    ({"style_id": None}, "validated_style_id is not set"),
    ({"style_id": "style_other"}, "validated for style style_other, but the approved style is style_synth"),
    ({"registry_style": "pending"}, "needs an approved style"),
    ({"registry_style": None}, "needs an approved style"),
    ({"status": "unvalidated"}, "status is 'unvalidated'"),
])
def test_runner_not_validated_for_the_approved_style_is_refused(approved_project, tmp_path, kwargs, message):
    set_lip_sync(approved_project)
    make_cpu_project(approved_project)
    log = configure(approved_project, tmp_path, **kwargs)
    scheduler, tasks, results = run_all(approved_project)
    lip = results[f"lipsync_mr_{SHOT1}"]
    assert lip.status == "not_validated" and message in lip.detail and "NOT VALIDATED" in lip.detail
    assert not log.exists()  # the runner was never called
    assert results["assemble_mr"].status == "blocked"
    assert not scheduler.task_dir(next(t for t in tasks if t.name == "assemble_mr")).exists()


def test_configured_lip_sync_changes_only_the_declared_language(approved_project, tmp_path):
    set_lip_sync(approved_project)
    make_cpu_project(approved_project)
    log = configure(approved_project, tmp_path)
    scheduler, tasks, results = run_all(approved_project)
    assert all(r.status == "complete" for r in results.values()), results
    assert len(log.read_text().splitlines()) == 1
    payload = json.loads(log.read_text().splitlines()[0])
    assert payload["language"] == "mr" and set(payload) == {"video_path", "audio_path", "language", "out_path"}
    plans, provenance = {}, {}
    for lang, name in (("mr", "marathi"), ("hi", "hindi")):
        directory = scheduler.task_dir(next(t for t in tasks if t.name == f"assemble_{lang}"))
        plans[lang] = read_json(directory / "edit_plan.json")
        provenance[lang] = read_json(directory / "provenance.json")
        assert validate_video(directory / f"adhyay_01_{name}.mp4", plans[lang]["duration_s"], require_audio=True) == []
    mr, hi = plans["mr"]["shots"], plans["hi"]["shots"]
    assert [s["clip_source"] for s in mr] == ["lipsync", "rendered"]
    assert [s["clip_source"] for s in hi] == ["rendered", "rendered"]
    assert mr[0]["source_sha256"] != hi[0]["source_sha256"] and mr[1]["source_sha256"] == hi[1]["source_sha256"]
    assert mr[0]["duration_s"] == hi[0]["duration_s"] == mr[0]["primary_action_duration_s"] == 0.5  # lip-sync keeps the shot timing
    assert provenance["mr"]["lipsync_shots"] == [SHOT1] and provenance["hi"]["lipsync_shots"] == []
    assert all(r.status == "resumed" for r in scheduler.run(tasks))
    # A changed lipsync section (here: revision) invalidates the task and everything downstream of it.
    models = load_models(approved_project)
    models["lipsync"]["revision"] = "test-2"
    atomic_write_json(approved_project.root / "config" / "models.yaml", models)
    again = plan_tasks(load_bundle(approved_project, load_models(approved_project), 1), scheduler)
    by_name = {t.name: t.task_id() for t in tasks}
    changed = {t.name for t in again if t.task_id() != by_name[t.name]}
    assert changed == {f"lipsync_mr_{SHOT1}", "assemble_mr"}


def test_failing_runner_blocks_assembly_without_retry_or_release(approved_project, tmp_path):
    set_lip_sync(approved_project)
    make_cpu_project(approved_project)
    log = configure(approved_project, tmp_path, fail=True)
    scheduler, tasks, results = run_all(approved_project)
    lip = results[f"lipsync_mr_{SHOT1}"]
    assert lip.status == "failed" and "synthetic runner failure" in lip.detail and lip.attempts == 1
    assert len(log.read_text().splitlines()) == 1
    assert results["assemble_mr"].status == "blocked"
    assert not scheduler.task_dir(next(t for t in tasks if t.name == "assemble_mr")).exists()
    assert results["assemble_hi"].status == "complete"


def test_compiler_requires_dialogue_for_lip_sync(approved_project):
    path = approved_project.episodes_dir / "adhyay_01" / "manifest.yaml"
    manifest = load_yaml(path)
    manifest["scenes"][0]["shots"].append({"shot_id": "a01_s01_sh03", "tier": 0, "visual_id": "vis_room_still",
                                           "duration_s": 1.0, "dialogue_ids": [], "lip_sync": LIP})
    atomic_write_json(path, manifest)
    with pytest.raises(GateFailure, match="a01_s01_sh03: lip_sync needs a shot with dialogue"):
        load_bundle(approved_project, load_models(approved_project), 1)


@pytest.mark.parametrize("lip", [
    {"languages": ["en"], "reviewed_by": "x"}, {"languages": [], "reviewed_by": "x"},
    {"languages": ["mr", "mr"], "reviewed_by": "x"}, {"languages": ["mr"], "reviewed_by": "   "},
    {"languages": ["mr"]}, {"languages": ["mr"], "reviewed_by": "x", "extra": 1}])
def test_manifest_rejects_malformed_lip_sync(approved_project, lip):
    set_lip_sync(approved_project, lip=lip)
    with pytest.raises(GranthError, match="lip_sync"):
        load_bundle(approved_project, load_models(approved_project), 1)


def test_changed_approved_style_content_invalidates_lipsync_even_with_same_style_id(approved_project, tmp_path):
    set_lip_sync(approved_project)
    make_cpu_project(approved_project)
    log = configure(approved_project, tmp_path)                       # runner validated for style_synth v1
    scheduler, tasks, results = run_all(approved_project)
    assert all(r.status == "complete" for r in results.values()), results
    v1_ids = {t.name: t.task_id() for t in tasks}
    # approved style_synth moves to version 2 with new content; style_id unchanged, runner binding untouched
    (approved_project.canon_dir / "visual_assets.yaml").write_text(
        yaml.safe_dump({"schema_version": 1, "style": style_dict("approved", 2, "different style"), "designs": [], "assets": []}),
        encoding="utf-8")
    again = plan_tasks(load_bundle(approved_project, load_models(approved_project), 1), scheduler)
    assert {t.name for t in again if t.task_id() != v1_ids[t.name]} == {f"lipsync_mr_{SHOT1}", "assemble_mr"}
    calls = len(log.read_text().splitlines())
    results = {r.name: r for r in scheduler.run(again)}
    assert results[f"lipsync_mr_{SHOT1}"].status == "not_validated" and "v1" in results[f"lipsync_mr_{SHOT1}"].detail
    assert len(log.read_text().splitlines()) == calls                 # stale runner validation never executed
    assert results["assemble_mr"].status == "blocked"
    # content change at the same version is caught by the digest alone
    configure(approved_project, tmp_path, version=2, prefix="different style")
    (approved_project.canon_dir / "visual_assets.yaml").write_text(
        yaml.safe_dump({"schema_version": 1, "style": style_dict("approved", 2, "silently edited"), "designs": [], "assets": []}),
        encoding="utf-8")
    results = {r.name: r for r in Scheduler(episode_store(approved_project, 1)).run(
        plan_tasks(load_bundle(approved_project, load_models(approved_project), 1), scheduler))}
    assert results[f"lipsync_mr_{SHOT1}"].status == "not_validated"


def test_unbound_style_digest_fails_closed(approved_project, tmp_path):
    set_lip_sync(approved_project)
    make_cpu_project(approved_project)
    log = configure(approved_project, tmp_path, bind=False)
    _, _, results = run_all(approved_project)
    assert results[f"lipsync_mr_{SHOT1}"].status == "not_validated" and not log.exists()


def test_lipsync_task_on_unready_host_never_calls_the_runner(approved_project, tmp_path):
    from granthstudio.config import dump_yaml
    set_lip_sync(approved_project)
    make_cpu_project(approved_project)
    log = configure(approved_project, tmp_path)
    runtime = load_yaml(approved_project.root / "config" / "runtime.yaml"); runtime["resources"]["min_free_vram_mb"] = 20000
    dump_yaml(approved_project.root / "config" / "runtime.yaml", runtime)       # pins match; VRAM check fails
    _, _, results = run_all(approved_project)
    lip = results[f"lipsync_mr_{SHOT1}"]
    assert lip.status == "not_validated" and "GPU preflight not passed" in lip.detail and not log.exists()
    assert results["assemble_mr"].status == "blocked"
