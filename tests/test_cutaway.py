"""Frozen section 10: language-neutral cutaway coverage. Synthetic media only."""
from __future__ import annotations

import copy
import pytest

from granthstudio.config import load_yaml, load_models
from granthstudio.errors import ConfigError, GateFailure, SchemaError
from granthstudio.ffmpeg import hold_clip, probe, trim_hold, validate_video
from granthstudio.integrity import atomic_write_json, read_json, sha256_file
from granthstudio.pipeline import episode_store, load_bundle, plan_tasks
from granthstudio.scheduler import Scheduler
from tests.conftest import have_tool, make_clip
from tests.test_review_regressions import compile_project, make_cpu_project

MEDIA = pytest.mark.skipif(not (have_tool("ffmpeg") and have_tool("ffprobe")), reason="media tools missing")
SH1, SH2, CUT = "a01_s01_sh01", "a01_s01_sh02", "a01_s01_sh03"


def edit_manifest(project, change, cutaway_shot=True):
    path = project.episodes_dir / "adhyay_01" / "manifest.yaml"
    manifest = load_yaml(path)
    shots = manifest["scenes"][0]["shots"]
    if cutaway_shot:
        shots.append({"shot_id": CUT, "tier": 0, "visual_id": "vis_room_still", "duration_s": 0.5,
                      "dialogue_ids": [], "cutaway": True})
    change(manifest, shots)
    atomic_write_json(path, manifest)


def cover(shot_id=CUT, reviewer="synthetic-test-only"):
    return {"mode": "cutaway", "shot_id": shot_id, "reviewed_by": reviewer}


def set_cover(coverage, target=1):
    def change(manifest, shots):
        shots[target]["coverage"] = coverage
    return change


def test_valid_cutaway_compiles(approved_project):
    edit_manifest(approved_project, set_cover(cover()))
    shots = {s["shot_id"]: s for s in compile_project(approved_project)["shots"]}
    assert shots[CUT]["cutaway"] is True and shots[SH2]["cutaway"] is False
    assert shots[SH2]["coverage"]["shot_id"] == CUT


def other_scene(manifest, shots):
    shots[1]["coverage"] = cover("a01_s02_sh01")


def unflagged(manifest, shots):
    shots[2].pop("cutaway"); shots[1]["coverage"] = cover()


def talking(manifest, shots):
    shots[2]["dialogue_ids"] = ["d_0002"]; shots[1]["dialogue_ids"] = []; shots[1]["coverage"] = cover()


def chained(manifest, shots):
    shots[2]["coverage"] = {"mode": "hold_final_frame", "reviewed_by": "x"}; shots[1]["coverage"] = cover()


def flagged_dialogue(manifest, shots):
    shots[0]["cutaway"] = True


@pytest.mark.parametrize("change,match", [
    (set_cover(cover(SH2)), "cannot be its own cutaway"),
    (other_scene, "not in scene a01_s01"),
    (unflagged, "not flagged cutaway"),
    (talking, "must carry no dialogue"),
    (chained, "no coverage of its own|must not have coverage"),
    (flagged_dialogue, "carries no dialogue"),
])
def test_invalid_cutaway_is_refused(approved_project, change, match):
    edit_manifest(approved_project, change)
    with pytest.raises(ConfigError, match=match):
        compile_project(approved_project)


@pytest.mark.parametrize("reviewer", ["", "  \t"])
def test_cutaway_needs_real_reviewer(approved_project, reviewer):
    edit_manifest(approved_project, set_cover(cover(reviewer=reviewer)))
    with pytest.raises(SchemaError, match="reviewed_by"):
        compile_project(approved_project)


@MEDIA
def test_trim_hold_exact(tmp_path):
    clip = make_clip(tmp_path / "c.mp4", 1.0)
    short, long = tmp_path / "s.mp4", tmp_path / "l.mp4"
    trim_hold(clip, short, 0.5)
    trim_hold(clip, long, 1.5)
    for path, want in ((short, 0.5), (long, 1.5)):
        assert abs(probe(path).video_duration_s - want) < 1 / 48, path
        assert not probe(path).has_audio


def run(project, lang_check=True):
    current = load_bundle(project, load_models(project), 1)
    scheduler = Scheduler(episode_store(project, 1))
    tasks = plan_tasks(current, scheduler)
    results = scheduler.run(tasks)
    return scheduler, tasks, results


def plan_of(scheduler, tasks, lang):
    directory = scheduler.task_dir(next(t for t in tasks if t.name == f"assemble_{lang}"))
    return directory, read_json(directory / "edit_plan.json")


@MEDIA
def test_cutaway_covers_extra_speech_per_language(approved_project):
    make_cpu_project(approved_project)
    edit_manifest(approved_project, set_cover(cover()))
    scheduler, tasks, results = run(approved_project)
    assert all(r.status == "complete" for r in results), results
    plans = {}
    for lang, name in (("mr", "marathi"), ("hi", "hindi")):
        directory, plan = plan_of(scheduler, tasks, lang)
        plans[lang] = plan
        assert CUT not in [s["shot_id"] for s in plan["shots"]]
        assert validate_video(directory / f"adhyay_01_{name}.mp4", plan["duration_s"], require_audio=True) == []
        assert read_json(directory / "provenance.json")["lines"]
    main = {l: next(s for s in p["shots"] if s["shot_id"] == SH2) for l, p in plans.items()}
    assert main["mr"]["primary_action_duration_s"] == main["hi"]["primary_action_duration_s"] == 0.5
    assert "coverage" not in main["mr"]
    cov = main["hi"]["coverage"]
    cut_clip = scheduler.task_dir(next(t for t in tasks if t.name == CUT)) / "clip.mp4"
    assert cov["mode"] == "cutaway" and cov["shot_id"] == CUT and cov["source_sha256"] == sha256_file(cut_clip)
    assert abs(cov["duration_s"] - (main["hi"]["duration_s"] - 0.5)) < 1e-6 and cov["duration_s"] > 0.5
    assert plans["hi"]["duration_s"] > plans["mr"]["duration_s"]
    assert all(r.status == "resumed" for r in scheduler.run(tasks))


@MEDIA
def test_extra_speech_without_coverage_still_fails(approved_project):
    make_cpu_project(approved_project)
    edit_manifest(approved_project, lambda m, shots: shots[1].pop("coverage"))
    _, _, results = run(approved_project)
    failed = [r for r in results if r.stage == "assembly" and r.status == "failed"]
    assert any("extra speech needs reviewed" in r.detail for r in failed), results


@MEDIA
def test_hold_final_frame_still_works(approved_project):
    make_cpu_project(approved_project)
    scheduler, tasks, results = run(approved_project)
    assert all(r.status == "complete" for r in results)
    _, plan = plan_of(scheduler, tasks, "hi")
    assert "coverage" not in plan["shots"][1] and plan["shots"][1]["duration_s"] > 0.5
