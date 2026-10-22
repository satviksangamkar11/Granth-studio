"""Frozen section 9: bounded retries, a declared Tier 0 fallback only after real failed renders, never silent."""
from __future__ import annotations

import pytest

from granthstudio import pilotrun
from granthstudio.config import load_yaml
from granthstudio.episodes import compile_episode
from granthstudio.errors import ConfigError, GateFailure, IntegrationUnavailable, JobPending, TaskFailed
from granthstudio.integrity import atomic_write_json, read_json
from granthstudio.pipeline import load_bundle
from granthstudio.scheduler import RECEIPT, Scheduler, Task
from granthstudio.config import load_models
from tests.conftest import have_tool
from tests.test_pilot_flow import comfy, pilot, T4, full_run  # noqa: F401  (fixtures)


def fallback_task(run, calls, **kwargs):
    def fallback(work):
        calls.append("fallback"); (work / "clip.bin").write_bytes(b"standin"); return {"clip": "clip.bin"}
    return Task("tier1", "shot", {}, "v", run, max_attempts=3, fallback=fallback,
                fallback_info={"mode": "tier0", "kind": "faithful", "reviewed_by": "synthetic-test-only"}, **kwargs)


def test_fallback_after_all_attempts_is_complete_recorded_and_reused(tmp_path):
    calls = []
    def run(work): calls.append("run"); raise TaskFailed("render failed")
    task = fallback_task(run, calls)
    scheduler = Scheduler(tmp_path)
    result = scheduler.run([task])[0]
    assert result.status == "complete" and result.detail.startswith("FALLBACK after 3 failed attempt(s)")
    assert calls == ["run", "run", "run", "fallback"]  # initial attempt plus two more (frozen section 9)
    directory = scheduler.task_dir(task)
    receipt = read_json(directory / RECEIPT)
    assert [h["outcome"] for h in receipt["attempt_history"]] == ["failed", "failed", "failed", "complete"]
    marker = read_json(directory / "fallback.json")
    assert marker["kind"] == "faithful" and len(marker["failed_attempts"]) == 3 and "fallback" in receipt["outputs"]
    assert Scheduler(tmp_path).run([task])[0].status == "resumed" and calls.count("fallback") == 1


@pytest.mark.parametrize("error,status", [(IntegrationUnavailable("not validated"), "not_validated"),
                                          (JobPending("still running"), "pending"), (GateFailure("blocked"), "failed")])
def test_fallback_is_never_used_to_cover_unvalidated_pending_or_blocked_work(tmp_path, error, status):
    calls = []
    def run(work): raise error
    result = Scheduler(tmp_path).run([fallback_task(run, calls)])[0]
    assert result.status == status and calls == [] and "FALLBACK" not in result.detail


def test_first_success_leaves_no_fallback_and_a_failing_fallback_is_reported(tmp_path):
    calls = []
    def ok(work): (work / "clip.bin").write_bytes(b"real"); return {"clip": "clip.bin"}
    scheduler = Scheduler(tmp_path / "a")
    task = fallback_task(ok, calls)
    assert scheduler.run([task])[0].status == "complete" and calls == []
    assert not (scheduler.task_dir(task) / "fallback.json").exists()
    assert [h["outcome"] for h in read_json(scheduler.task_dir(task) / RECEIPT)["attempt_history"]] == ["complete"]
    def bad(work): raise TaskFailed("nope")
    def bad_fallback(work): raise TaskFailed("stand-in failed too")
    both = Task("tier1", "shot", {}, "v", bad, max_attempts=2, fallback=bad_fallback)
    result = Scheduler(tmp_path / "b").run([both])[0]
    assert result.status == "failed" and "fallback also failed" in result.detail


def test_compiler_refuses_ambient_fallback_over_a_required_action(approved_project):
    path = approved_project.episodes_dir / "adhyay_01" / "manifest.yaml"
    manifest = load_yaml(path)
    shot = manifest["scenes"][0]["shots"][1]  # tier 1, carries action_turn
    for fallback, error in (({"mode": "tier0", "kind": "ambient", "reviewed_by": "synthetic-test-only"}, "ambient fallback cannot replace"),
                            ):
        shot["fallback"] = fallback
        atomic_write_json(path, manifest)
        with pytest.raises(GateFailure, match=error):
            load_bundle(approved_project, load_models(approved_project), 1)
    shot["fallback"] = {"mode": "tier0", "kind": "faithful", "reviewed_by": "synthetic-test-only"}
    atomic_write_json(path, manifest)
    assert load_bundle(approved_project, load_models(approved_project), 1).compiled["shots"][1]["fallback"]["kind"] == "faithful"
    manifest["scenes"][0]["shots"][0]["fallback"] = shot["fallback"]  # a Tier 0 shot cannot fall back from itself
    atomic_write_json(path, manifest)
    with pytest.raises(ConfigError, match="nothing to fall back from"):
        load_bundle(approved_project, load_models(approved_project), 1)
    manifest["scenes"][0]["shots"][0]["fallback"] = {"mode": "tier0", "kind": "faithful", "reviewed_by": "  "}
    atomic_write_json(path, manifest)
    with pytest.raises(Exception, match="reviewed_by"):
        load_bundle(approved_project, load_models(approved_project), 1)


@pytest.mark.skipif(not (have_tool("ffmpeg") and have_tool("ffprobe")), reason="media tools missing")
def test_failed_pilot_renders_fall_back_visibly_and_never_validate_the_capability(pilot, comfy):
    path = pilot.episodes_dir / "adhyay_01" / "manifest.yaml"
    manifest = load_yaml(path)
    for scene in manifest["scenes"]:
        for shot in scene["shots"]:
            if shot["tier"] >= 1:
                shot["fallback"] = {"mode": "tier0", "kind": "faithful", "reviewed_by": "synthetic-test-only"}
    atomic_write_json(path, manifest)
    comfy.auto_status = "error"  # every render attempt fails on the server
    mapping, selected, full, results, receipt = full_run(pilot)
    assert all(r.status == "complete" for r in results), [(r.name, r.status, r.detail) for r in results]
    assert sum(r.detail.startswith("FALLBACK") for r in results) == 4 and len(comfy.posts) == 12
    store = pilot.artifacts_dir / "tasks" / "adhyay_01"
    scheduler = Scheduler(store)
    bundle = pilotrun._bundle(pilot, load_models(pilot), 1)
    tasks = {t.name: t for t in pilotrun.selection(bundle, scheduler)[1]}
    plan = read_json(scheduler.task_dir(tasks["assemble_mr"]) / "edit_plan.json")
    assert sorted(e["shot_id"] for e in plan["shots"] if e["clip_source"] == "fallback_tier0") == sorted(
        mapping[label] for label in "BCDE")
    provenance = read_json(scheduler.task_dir(tasks["assemble_hi"]) / "provenance.json")
    assert len(provenance["fallback_shots"]) == 4
    pilotrun.build_receipts(pilot, 1, None)
    for label in "BCDE":
        r = read_json(pilot.benchmarks_dir / "pilot_af" / "receipts" / f"{label}.json")
        assert (r["accepted"], r["outcome"]) == (False, "fail") and "fallback" in r["measurement_notes"] and r["attempts"] >= 3
