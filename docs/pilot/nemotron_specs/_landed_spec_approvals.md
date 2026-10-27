# Spec: write ONE file `scripts/pipeline/approvals.py`.
Style: `from __future__ import annotations`, standard library only, short docstring, no print, no network, no side effects at import.

## API
Functions: sha256_file(path)->str hex; load(path)->dict (missing file -> {}); approve(path, item, sha256, owner, date) validates (item, owner, date non-empty strings; sha256 exactly 64 lowercase hex) else ValueError and writes nothing; stores {item: {"sha256","owner","date"}} replacing an earlier approval of the same item; write atomically (temp file in the same folder, then os.replace), UTF-8 JSON, indent 1, sorted keys; status(approvals_dict, item, current_sha256)->"DRAFT" if the item is absent, "APPROVED" if the hash matches, else "STALE"; stale_dependents(deps, changed)->set: deps maps an item to the list of items it depends on; return every item that depends, directly or transitively, on any item in changed; must terminate on cycles.

## The tests it must pass (do not change them; the tests load the file by path)
FILE tests/test_pipeline_approvals.py:
```python
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("approvals", ROOT / "scripts" / "pipeline" / "approvals.py")
ap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ap)

H1, H2 = "a" * 64, "b" * 64


def test_sha256_file(tmp_path):
    f = tmp_path / "x.txt"
    f.write_bytes(b"abc")
    assert ap.sha256_file(f) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_missing_file_is_empty_and_approve_then_status(tmp_path):
    f = tmp_path / "approvals.json"
    assert ap.load(f) == {}
    ap.approve(f, "script", H1, "owner", "2026-10-27")
    a = ap.load(f)
    assert a["script"] == {"sha256": H1, "owner": "owner", "date": "2026-10-27"}
    assert ap.status(a, "script", H1) == "APPROVED"
    assert ap.status(a, "script", H2) == "STALE"
    assert ap.status(a, "images", H1) == "DRAFT"


def test_approve_validates_and_replaces(tmp_path):
    f = tmp_path / "approvals.json"
    for bad in ("", "abc", "g" * 64, "A" * 64, None):
        with pytest.raises(ValueError):
            ap.approve(f, "script", bad, "owner", "2026-10-27")
    with pytest.raises(ValueError):
        ap.approve(f, "", H1, "owner", "2026-10-27")
    with pytest.raises(ValueError):
        ap.approve(f, "script", H1, "", "2026-10-27")
    assert not f.exists()
    ap.approve(f, "script", H1, "owner", "2026-10-27")
    ap.approve(f, "script", H2, "owner", "2026-10-28")
    assert ap.load(f)["script"]["sha256"] == H2
    assert json.loads(f.read_text(encoding="utf-8"))["script"]["date"] == "2026-10-28"


def test_stale_dependents_are_transitive_and_cycle_safe():
    deps = {"timing": ["script", "clips"], "jobs": ["timing", "stage1"], "render": ["jobs"], "stage1": [], "clips": ["script"]}
    assert ap.stale_dependents(deps, {"script"}) == {"timing", "clips", "jobs", "render"}
    assert ap.stale_dependents(deps, {"stage1"}) == {"jobs", "render"}
    assert ap.stale_dependents(deps, set()) == set()
    assert "b" in ap.stale_dependents({"a": ["b"], "b": ["a"]}, {"a"})            # a cycle terminates

```

Reply with only: FILE: scripts/pipeline/approvals.py followed by the code block.


CORRECTED 2026-10-28: stale_dependents always excludes the changed items (a<->b, changed={a} returns exactly {b}). status() approves only when the recorded AND the current hash are valid 64-hex and equal; a missing or invalid hash is STALE. The owner field is metadata, not proof of authority (checklist item 12 defines who may write approvals).
