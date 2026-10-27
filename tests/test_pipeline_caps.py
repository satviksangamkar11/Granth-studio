import importlib.util
import json
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("caps", ROOT / "scripts" / "pipeline" / "caps.py")
cp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)

CAPS = {"total": 5.0, "stages": {"stage1": 1.0, "stage2": 3.0, "contingency": 1.0}}


def write(tmp_path, obj):
    f = tmp_path / "caps.json"
    f.write_text(json.dumps(obj), encoding="utf-8")
    return f


def test_load_valid_and_invalid(tmp_path):
    assert cp.load_caps(write(tmp_path, CAPS)) == CAPS
    for bad in ({"total": 0, "stages": {"a": 1}}, {"total": 5, "stages": {}}, {"total": 5, "stages": {"a": -1}}, {"total": 1, "stages": {"a": 1, "b": 1}},
                {"total": "5", "stages": {"a": 1}}, {"stages": {"a": 1}}, {"total": True, "stages": {"a": 1}}):
        with pytest.raises(ValueError):
            cp.load_caps(write(tmp_path, bad))
    with pytest.raises(FileNotFoundError):
        cp.load_caps(tmp_path / "nope.json")


def test_check_is_pure_and_refuses_over_stage_total_unknown_stage():
    assert cp.check(CAPS, {"stage1": 0.5}, "stage1", 0.4) == pytest.approx(0.1)
    assert cp.check(CAPS, {}, "stage2", 3.0) == pytest.approx(0.0)
    with pytest.raises(cp.CapRefused):
        cp.check(CAPS, {"stage1": 0.7}, "stage1", 0.4)
    with pytest.raises(cp.CapRefused):
        cp.check({"total": 2.0, "stages": {"stage1": 1.5, "stage2": 1.5}}, {"stage1": 1.5, "stage2": 0.3}, "stage2", 0.5)
    with pytest.raises(cp.CapRefused):
        cp.check(CAPS, {}, "stage3", 0.1)
    for bad in (-1, float("nan"), True):
        with pytest.raises(ValueError):
            cp.check(CAPS, {}, "stage1", bad)


def test_reserve_counts_the_worst_case_before_the_call_and_settle_replaces_it(tmp_path):
    s = tmp_path / "spend.jsonl"
    assert cp.reserve(s, CAPS, "stage1", 0.6, "r1") == pytest.approx(0.4)
    assert cp.spent(s) == {"stage1": 0.6}                                   # reserved money counts at once
    with pytest.raises(cp.CapRefused):
        cp.reserve(s, CAPS, "stage1", 0.5, "r2")                           # 0.6 + 0.5 > 1.0
    cp.settle(s, "r1", 0.08)
    assert cp.spent(s) == {"stage1": 0.08}
    assert cp.reserve(s, CAPS, "stage1", 0.9, "r3") == pytest.approx(0.02)
    assert cp.state(s)["r1"] == {"stage": "stage1", "status": "settled", "reserved": 0.6, "actual": 0.08}


def test_duplicate_request_ids_and_bad_settles_are_refused(tmp_path):
    s = tmp_path / "spend.jsonl"
    cp.reserve(s, CAPS, "stage1", 0.1, "r1")
    with pytest.raises(ValueError):
        cp.reserve(s, CAPS, "stage1", 0.1, "r1")
    for rid, actual in (("nope", 0.1), ("r1", -1), ("r1", float("nan")), ("r1", True)):
        with pytest.raises(ValueError):
            cp.settle(s, rid, actual)
    cp.settle(s, "r1", 0.05)
    with pytest.raises(ValueError):
        cp.settle(s, "r1", 0.05)                                            # only an open reservation can be settled


def test_unknown_keeps_the_reservation_until_the_owner_reconciles(tmp_path):
    s = tmp_path / "spend.jsonl"
    cp.reserve(s, CAPS, "stage2", 0.3, "r1")
    cp.unknown(s, "r1", "timeout")
    assert cp.unreconciled(s) == ["r1"] and cp.spent(s) == {"stage2": 0.3}
    with pytest.raises(ValueError):
        cp.reconcile(s, "r1", 0.1, "x")                                     # a note of at least 5 characters is required
    cp.reconcile(s, "r1", 0.1, "dashboard 2026-10-27")
    assert cp.unreconciled(s) == [] and cp.spent(s) == {"stage2": 0.1}


def test_a_new_reservation_is_refused_while_another_is_unreconciled_when_asked(tmp_path):
    s = tmp_path / "spend.jsonl"
    cp.reserve(s, CAPS, "stage1", 0.1, "r1")
    with pytest.raises(cp.CapRefused):
        cp.reserve(s, CAPS, "stage1", 0.1, "r2", require_reconciled=True)
    cp.settle(s, "r1", 0.05)
    cp.reserve(s, CAPS, "stage1", 0.1, "r2", require_reconciled=True)


def test_two_threads_cannot_both_pass_the_same_balance(tmp_path):
    s = tmp_path / "spend.jsonl"
    caps = {"total": 1.0, "stages": {"stage1": 1.0}}
    results = []

    def go(i):
        try:
            cp.reserve(s, caps, "stage1", 0.6, f"r{i}")
            results.append("ok")
        except cp.CapRefused:
            results.append("refused")
    ts = [threading.Thread(target=go, args=(i,)) for i in range(6)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    assert sorted(results) == ["ok"] + ["refused"] * 5


def test_a_fresh_nested_folder_works_and_replay_rejects_corruption(tmp_path):
    s = tmp_path / "a" / "b" / "spend.jsonl"
    cp.reserve(s, CAPS, "stage1", 0.1, "r1")
    assert cp.unreconciled(s) == ["r1"]
    with s.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"id": "r1", "stage": "stage1", "status": "open", "reserved": 0.2}) + chr(10))     # a second open for the same id
    for fn in (cp.state, cp.spent, cp.unreconciled):
        with pytest.raises(ValueError):
            fn(s)
    t = tmp_path / "t.jsonl"
    cp.reserve(t, CAPS, "stage1", 0.1, "r1")
    with t.open("a", encoding="utf-8") as f:
        f.write('{"id": "r1", "sta')                                        # truncated record
    with pytest.raises(ValueError):
        cp.state(t)
    with pytest.raises(ValueError):
        cp.reserve(t, CAPS, "stage1", 0.1, "r9")


def test_a_leftover_lock_is_never_deleted_automatically(tmp_path, monkeypatch):
    s = tmp_path / "spend.jsonl"
    (tmp_path / "spend.jsonl.lock").write_text("", encoding="utf-8")
    monkeypatch.setattr(cp.time, "monotonic", iter([0.0, 11.0, 12.0]).__next__)
    with pytest.raises(cp.CapRefused):
        cp.reserve(s, CAPS, "stage1", 0.1, "r1")
    assert (tmp_path / "spend.jsonl.lock").exists()
