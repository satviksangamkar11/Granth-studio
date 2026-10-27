# Spec: write ONE file `scripts/pipeline/gates.py`. The frozen tests are in `tests/test_gates.py` (shown below; they load your module by path with importlib).
Style: `from __future__ import annotations`, standard library (plus `jsonschema` where stated), short docstrings, no print, no network, no file writes by the module (tests may write under pytest `tmp_path`), nothing at import time. The module never raises for bad DATA: it returns error strings (stable order, each message starts with the item id such as a line id, shot id, image id or document name). Type/argument misuse (wrong argument types) may raise TypeError/ValueError only where the API says so. The tests below are FROZEN: make them pass, do not change them. Messages are plain English and MUST contain the keywords the tests look for (case-sensitive).

## API (loads the sibling `approvals.py` by importlib from the same folder; uses its `status`)
- `class GateBlocked(Exception)`: attribute `blockers: dict[str, str]` (item -> reason).
- `pipeline_state(deps, approvals, current_sha) -> dict[str, str]`: `deps` maps item -> list of items it reads. Items = all keys and all listed dependencies. Local status of each item = `approvals.status(approvals, item, current_sha.get(item))` (DRAFT / APPROVED / STALE; an item with no current hash is STALE if it has a record). Final state: DRAFT and STALE are kept as they are; an item whose local status is APPROVED becomes "BLOCKED" if ANY transitive dependency (not itself) has local status DRAFT or STALE; otherwise APPROVED. A self-dependency is ignored; cycles terminate; an all-approved cycle stays APPROVED; in a cycle a<->b with a STALE and b APPROVED the result is a STALE, b BLOCKED.
- `require_approved(items, deps, approvals, current_sha) -> None`: compute `pipeline_state`; raise `GateBlocked` unless every listed item is APPROVED. blockers[item] = "DRAFT", "STALE" or "BLOCKED by <comma-separated sorted names of the non-approved transitive dependencies>".
- `ready_stages(stages, deps, approvals, current_sha) -> list[str]`: `stages` maps a stage name to the items it reads; sorted names of stages whose every item is APPROVED in the final state.
- `next_approvals_needed(deps, approvals, current_sha) -> list[str]`: sorted items whose local status is DRAFT or STALE and whose DIRECT dependencies are all APPROVED in the final state.

## The frozen tests (do not change)
FILE tests/test_gates.py:
```python
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

```

Reply with only: FILE: scripts/pipeline/gates.py followed by its code block.
