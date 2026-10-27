import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / "pipeline" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gt = load("gates")
H = {k: (k[0] * 64) for k in "sctjr"}            # script, clips, timing, jobs, render -> 64 identical hex chars
DEPS = {"clips": ["script"], "timing": ["clips"], "jobs": ["timing"], "render": ["jobs"], "script": []}
SHA = {"script": "a" * 64, "clips": "b" * 64, "timing": "c" * 64, "jobs": "d" * 64, "render": "e" * 64}


def appr(**over):
    out = {k: {"sha256": v, "owner": "o", "date": "2026-10-28"} for k, v in SHA.items()}
    out.update(over)
    return out


def test_all_approved_chain_is_approved():
    assert set(gt.pipeline_state(DEPS, appr(), SHA).values()) == {"APPROVED"}


def test_draft_stale_and_missing_current_hash():
    a = appr()
    del a["clips"]
    st = gt.pipeline_state(DEPS, a, SHA)
    assert st["clips"] == "DRAFT"
    changed = dict(SHA, script="f" * 64)
    st = gt.pipeline_state(DEPS, appr(), changed)
    assert st["script"] == "STALE"
    nocur = {k: v for k, v in SHA.items() if k != "script"}
    assert gt.pipeline_state(DEPS, appr(), nocur)["script"] == "STALE"


def test_blocked_propagates_down_the_chain_but_never_hides_an_items_own_status():
    changed = dict(SHA, script="f" * 64)
    st = gt.pipeline_state(DEPS, appr(), changed)
    assert [st[k] for k in ("script", "clips", "timing", "jobs", "render")] == ["STALE", "BLOCKED", "BLOCKED", "BLOCKED", "BLOCKED"]
    a = appr()
    del a["jobs"]
    st = gt.pipeline_state(DEPS, a, SHA)
    assert st["jobs"] == "DRAFT" and st["render"] == "BLOCKED" and st["timing"] == "APPROVED"
    changed = dict(SHA, jobs="f" * 64)                                       # a stale item that is also downstream of an approved one stays STALE
    assert gt.pipeline_state(DEPS, appr(), changed)["jobs"] == "STALE"


def test_cycles_terminate_and_self_dependency_is_ignored():
    deps = {"a": ["b"], "b": ["a"]}
    sha = {"a": "a" * 64, "b": "b" * 64}
    ap = {k: {"sha256": v, "owner": "o", "date": "d"} for k, v in sha.items()}
    assert set(gt.pipeline_state(deps, ap, sha).values()) == {"APPROVED"}   # an all-approved cycle stays approved
    assert gt.pipeline_state(deps, ap, dict(sha, a="f" * 64)) == {"a": "STALE", "b": "BLOCKED"}
    assert gt.pipeline_state({"a": ["a"]}, {"a": ap["a"]}, {"a": sha["a"]}) == {"a": "APPROVED"}


def test_require_approved_uses_the_dependency_graph():
    gt.require_approved(["jobs"], DEPS, appr(), SHA)
    changed = dict(SHA, script="f" * 64)
    with pytest.raises(gt.GateBlocked) as e:
        gt.require_approved(["jobs", "script"], DEPS, appr(), changed)       # jobs itself is unchanged but its ancestor is stale
    assert set(e.value.blockers) == {"jobs", "script"}
    assert "STALE" in e.value.blockers["script"] and "BLOCKED" in e.value.blockers["jobs"] and "script" in e.value.blockers["jobs"]
    a = appr()
    del a["clips"]
    with pytest.raises(gt.GateBlocked) as e:
        gt.require_approved(["clips"], DEPS, a, SHA)
    assert e.value.blockers == {"clips": "DRAFT"}


def test_ready_stages_and_next_approvals():
    stages = {"voice": ["script"], "timing_stage": ["clips"], "render_stage": ["jobs", "timing"]}
    assert gt.ready_stages(stages, DEPS, appr(), SHA) == ["render_stage", "timing_stage", "voice"]
    changed = dict(SHA, script="f" * 64)
    assert gt.ready_stages(stages, DEPS, appr(), changed) == []
    a = appr()
    for k in ("clips", "timing", "jobs", "render"):
        del a[k]
    assert gt.next_approvals_needed(DEPS, a, SHA) == ["clips"]               # only the item whose inputs are all approved
    assert gt.next_approvals_needed(DEPS, appr(), SHA) == []
    assert gt.next_approvals_needed(DEPS, appr(), changed) == ["script"]


def test_an_invalid_recorded_hash_never_approves_and_unknown_items_are_leaves():
    junk = {"script": {"sha256": "junk", "owner": "o", "date": "d"}}
    assert gt.pipeline_state({"script": []}, junk, {"script": "junk"}) == {"script": "STALE"}
    with pytest.raises(gt.GateBlocked) as e:
        gt.require_approved(["ghost"], DEPS, appr(), SHA)                     # an item nobody has approved: DRAFT, never a KeyError
    assert e.value.blockers == {"ghost": "DRAFT"}
    assert gt.ready_stages({"s": ["ghost"]}, DEPS, appr(), SHA) == []
