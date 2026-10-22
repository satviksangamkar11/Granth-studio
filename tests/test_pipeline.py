"""End-to-end wiring on the synthetic project: stage plan, refusals, resume, QA report and CLI exit codes."""

from __future__ import annotations

import json
import shutil

import pytest

from granthstudio.cli import EXIT_NOT_VALIDATED, main
from granthstudio.config import load_models
from granthstudio.pipeline import episode_store, hard_gates, load_bundle, plan_tasks
from granthstudio.qa import report_path
from granthstudio.scheduler import Scheduler
from tests.conftest import have_tool


def _bundle(project):
    return load_bundle(project, load_models(project), 1)


def test_plan_follows_frozen_stage_order(approved_project):
    bundle = _bundle(approved_project)
    tasks = plan_tasks(bundle, Scheduler(episode_store(approved_project, 1)))
    assert [t.stage for t in tasks] == ["audio", "audio", "tier0", "tier1", "assembly", "assembly"]


def test_real_run_refuses_unvalidated_stages(approved_project):
    bundle = _bundle(approved_project)
    store = Scheduler(episode_store(approved_project, 1))
    results = store.run(plan_tasks(bundle, store))
    by_stage = {}
    for result in results:
        by_stage.setdefault(result.stage, []).append(result.status)
    assert by_stage["audio"] == ["not_validated", "not_validated"]
    assert by_stage["tier1"] == ["not_validated"]
    assert set(by_stage["assembly"]) == {"blocked"}
    gates = {g.name: g.passed for g in hard_gates(bundle, results)}
    assert gates["task_outputs"] is False and gates["source_integrity"] is True


@pytest.mark.skipif(not have_tool("ffmpeg"), reason="ffmpeg not on PATH")
def test_tier0_shot_is_produced_and_resumed(approved_project):
    bundle = _bundle(approved_project)
    store = Scheduler(episode_store(approved_project, 1))
    first = store.run(plan_tasks(bundle, store))
    tier0 = [r for r in first if r.stage == "tier0"]
    assert tier0[0].status == "complete"
    second = store.run(plan_tasks(bundle, store))
    assert [r.status for r in second if r.stage == "tier0"] == ["resumed"]


def test_cli_run_exit_code_for_not_validated(approved_project):
    code = main(["--root", str(approved_project.root), "run", "1", "--execute"])
    assert code == EXIT_NOT_VALIDATED
    assert report_path(approved_project, 1).is_file()
    report = json.loads(report_path(approved_project, 1).read_text(encoding="utf-8"))
    assert report["released"] is False


def test_cli_dry_run_executes_nothing(approved_project, capsys):
    assert main(["--root", str(approved_project.root), "run", "1"]) == 0
    out = capsys.readouterr().out
    assert "dry run" in out and "planned  audio" in out
    assert not episode_store(approved_project, 1).exists()


def test_report_uses_receipts_not_claims(approved_project):
    bundle = _bundle(approved_project)
    shutil.rmtree(approved_project.artifacts_dir, ignore_errors=True)
    store = Scheduler(episode_store(approved_project, 1))
    results = store.status(plan_tasks(bundle, store))
    assert all(r.status == "missing" for r in results)
    assert main(["--root", str(approved_project.root), "report", "1"]) == 2
