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
    assert ap.stale_dependents({"a": ["b"], "b": ["a"]}, {"a"}) == {"b"}            # a cycle terminates; changed items are never in the result


def test_a_missing_or_invalid_hash_never_approves():
    a = {"x": {}, "y": {"sha256": H1}, "z": "junk"}
    assert ap.status(a, "x", None) == "STALE" and ap.status(a, "x", H1) == "STALE"
    assert ap.status(a, "y", None) == "STALE" and ap.status(a, "y", "short") == "STALE" and ap.status(a, "y", H1) == "APPROVED"
    assert ap.status(a, "z", H1) == "STALE"
