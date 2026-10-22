"""Bilingual timeline gates, SRT timing, the filesystem scheduler and resume behaviour."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest

from granthstudio.canon import load_canon
from granthstudio.config import load_yaml
from granthstudio.episodes import compile_episode
from granthstudio.errors import GateFailure, IntegrationUnavailable
from granthstudio.integrity import atomic_write_json, sha256_file
from granthstudio.research import load_research, require_approved
from granthstudio.scheduler import RECEIPT, Scheduler, Task
from granthstudio.timelines import check_timelines, numbers_in, srt_text
from granthstudio.timelines import load_timeline


def _inputs(project):
    canon = load_canon(project)
    research = load_research(project, 1)
    receipt = require_approved(project, 1)
    models = load_yaml(project.root / "config" / "models.yaml")
    compiled = compile_episode(project, models, canon, 1, research, receipt)
    mr = load_timeline(project, 1, "mr")
    hi = load_timeline(project, 1, "hi")
    return canon, research, compiled, mr, hi


def _problems(project, mr=None, hi=None):
    canon, research, compiled, base_mr, base_hi = _inputs(project)
    return check_timelines(canon, compiled, research, mr or base_mr, hi or base_hi)


def test_consistent_bilingual_timelines_pass(approved_project):
    assert _problems(approved_project) == []


def test_marathi_text_change_is_blocked(approved_project):
    _, _, _, mr, _ = _inputs(approved_project)
    mr = copy.deepcopy(mr)
    mr["entries"][0]["text"] = "SYNTH-A says 3 things"
    assert any("Marathi lock" in p or "differs" in p for p in _problems(approved_project, mr=mr))


def test_missing_hindi_line_is_blocked(approved_project):
    _, _, _, _, hi = _inputs(approved_project)
    hi = copy.deepcopy(hi)
    hi["entries"].pop()
    assert any("sets differ" in p for p in _problems(approved_project, hi=hi))


def test_numeric_fact_change_is_blocked(approved_project):
    _, _, _, _, hi = _inputs(approved_project)
    hi = copy.deepcopy(hi)
    hi["entries"][0]["text"] = "SYNTH-A 3 बातें कहता है"
    assert any("numeric facts differ" in p for p in _problems(approved_project, hi=hi))


def test_protected_term_without_allowed_form_is_blocked(approved_project):
    _, _, _, _, hi = _inputs(approved_project)
    hi = copy.deepcopy(hi)
    hi["entries"][1]["text"] = "SYNTH-B नामित है"
    assert any("term_synth_x" in p for p in _problems(approved_project, hi=hi))


def test_numbers_normalise_devanagari_digits():
    assert numbers_in("३ आणि 4") == ["3", "4"]


def test_srt_requires_measured_durations():
    entries = [{"dialogue_id": "d_0001", "text": "x", "measured_duration_s": None}]
    with pytest.raises(GateFailure):
        srt_text(entries)


def test_srt_cues_are_sequential():
    entries = [
        {"dialogue_id": "d_0001", "text": "one", "measured_duration_s": 1.5},
        {"dialogue_id": "d_0002", "text": "two", "measured_duration_s": 2.0},
    ]
    text = srt_text(entries)
    assert "00:00:00,000 --> 00:00:01,500" in text
    assert "00:00:01,500 --> 00:00:03,500" in text


# ---- scheduler -------------------------------------------------------------------------------

def _writer(name: str, content: bytes = b"data"):
    calls = {"n": 0}

    def run(workdir: Path):
        calls["n"] += 1
        (workdir / name).write_bytes(content)
        return {"out": name}

    run.calls = calls
    return run


def test_run_then_resume_reuses_verified_receipts(tmp_path):
    run = _writer("a.bin")
    task = Task("tier0", "t", {"x": "1"}, "v1", run)
    store = tmp_path / "store"
    first = Scheduler(store).run([task])
    second = Scheduler(store).run([task])
    assert first[0].status == "complete"
    assert second[0].status == "resumed"
    assert run.calls["n"] == 1


def test_corrupted_output_is_rebuilt(tmp_path):
    run = _writer("a.bin")
    task = Task("tier0", "t", {"x": "1"}, "v1", run)
    store = tmp_path / "store"
    Scheduler(store).run([task])
    (Scheduler(store).task_dir(task) / "a.bin").write_bytes(b"tampered")
    result = Scheduler(store).run([task])[0]
    assert result.status == "complete"
    assert run.calls["n"] == 2


def test_retry_until_success(tmp_path):
    state = {"n": 0}

    def flaky(workdir: Path):
        state["n"] += 1
        if state["n"] < 3:
            raise RuntimeError("transient")
        (workdir / "ok.bin").write_bytes(b"ok")
        return {"out": "ok.bin"}

    task = Task("tier1", "t", {"x": "1"}, "v1", flaky, max_attempts=3)
    result = Scheduler(tmp_path / "s").run([task])[0]
    assert result.status == "complete"
    assert result.attempts == 3


def test_exhausted_retries_fail_and_block_dependents(tmp_path):
    def broken(_workdir: Path):
        raise RuntimeError("always")

    first = Task("tier1", "broken", {"x": "1"}, "v1", broken, max_attempts=2)
    second = Task("assembly", "after", {"x": "2"}, "v1", _writer("c.bin"), depends_on=(first.task_id(),))
    results = Scheduler(tmp_path / "s").run([first, second])
    assert results[0].status == "failed" and results[0].attempts == 2
    assert results[1].status == "blocked"


def test_not_validated_is_not_retried(tmp_path):
    calls = {"n": 0}

    def unavailable(_workdir: Path):
        calls["n"] += 1
        raise IntegrationUnavailable("NOT VALIDATED")

    task = Task("audio", "voice", {"x": "1"}, "v1", unavailable, max_attempts=3)
    result = Scheduler(tmp_path / "s").run([task])[0]
    assert result.status == "not_validated"
    assert calls["n"] == 1


def test_interrupted_run_leaves_no_partial_result_and_resumes(tmp_path):
    store = tmp_path / "s"

    def crash(_workdir: Path):
        raise KeyboardInterrupt  # simulates the process being killed mid-task

    first_task = Task("tier0", "first", {"x": "1"}, "v1", _writer("f.bin"))
    crashing = Task("tier0", "second", {"x": "2"}, "v1", crash)
    with pytest.raises(KeyboardInterrupt):
        Scheduler(store).run([first_task, crashing])
    assert Scheduler(store).status([first_task])[0].status == "complete"
    assert not (Scheduler(store).task_dir(crashing) / RECEIPT).exists()

    recovered = Scheduler(store).run([first_task, Task("tier0", "second", {"x": "2"}, "v1", _writer("g.bin"))])
    assert [r.status for r in recovered] == ["resumed", "complete"]
    assert not list((store / "tier0").glob(".work-*"))


def test_run_log_records_every_result(tmp_path):
    store = tmp_path / "s"
    Scheduler(store).run([Task("tier0", "t", {"x": "1"}, "v1", _writer("a.bin"))])
    lines = (store / "run_log.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1 and '"status": "complete"' in lines[0]


def test_task_id_is_deterministic_and_input_sensitive():
    a = Task("tier0", "t", {"x": "1"}, "v1", _writer("a.bin"))
    b = Task("tier0", "t", {"x": "1"}, "v1", _writer("a.bin"))
    c = Task("tier0", "t", {"x": "2"}, "v1", _writer("a.bin"))
    assert a.task_id() == b.task_id() != c.task_id()
