import importlib.util
import json
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("nc", ROOT / "scripts" / "source" / "nemotron_code.py")
nc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nc)

# Load real policy for test data
with open(ROOT / "config" / "codegen_policy.json", encoding="utf-8") as f:
    _real_policy = json.load(f)
_REAL_REASON = _real_policy["forbidden_text"]["refusal_reason"]
_REAL_EXAMPLE = _real_policy["forbidden_text"]["refused_examples"][0]


def block(path, body="x = 1"):
    return f"FILE: {path}\n```python\n{body}\n```\n"


@pytest.mark.parametrize("path", ["../x.py", "/etc/x.py", "C:/x.py", "secrets/k.py", "a/.git/x.py", "x.exe", "x.sh"])
def test_bad_paths_are_refused(path):
    ok, refused = nc.parse_files(block(path))
    assert not ok and refused[0][0] == path


def test_good_files_pass_and_policy_code_is_refused():
    ok, refused = nc.parse_files(block("pipeline/a.py") + block("pipeline/b.py", _REAL_EXAMPLE) + block("pipeline/a.py", "y = 2"))
    assert list(ok) == ["pipeline/a.py"] and ok["pipeline/a.py"] == "x = 1\n"
    assert {r[1] for r in refused} == {_REAL_REASON, "duplicate"}


def test_prose_without_file_blocks_gives_nothing():
    assert nc.parse_files("Here is some code: x = 1") == ({}, [])


def test_write_scratch_stays_inside_and_never_overwrites(tmp_path):
    out = tmp_path / "s"
    nc.write_scratch({"a/b.py": "x\n"}, out)
    assert (out / "a" / "b.py").read_text() == "x\n"
    with pytest.raises(FileExistsError):
        nc.write_scratch({"a/b.py": "y\n"}, out)
    with pytest.raises(ValueError):
        nc.write_scratch({"../evil.py": "z\n"}, out)


def test_spec_and_out_paths_are_checked(tmp_path):
    good = tmp_path / "spec.md"
    good.write_text("x", encoding="utf-8")
    assert nc.check_spec(good, roots=[tmp_path]) is None
    assert nc.check_spec(tmp_path / "missing.md", roots=[tmp_path])
    (tmp_path / "k.json").write_text("{}", encoding="utf-8")
    assert nc.check_spec(tmp_path / "k.json", roots=[tmp_path])
    sec = tmp_path / "secrets"
    sec.mkdir()
    (sec / "a.md").write_text("k", encoding="utf-8")
    assert "forbidden" in nc.check_spec(sec / "a.md", roots=[tmp_path])
    big = tmp_path / "big.md"
    big.write_text("x" * 300_000, encoding="utf-8")
    assert nc.check_spec(big, roots=[tmp_path])
    assert nc.check_out(tmp_path / "new", [tmp_path], repo_root=tmp_path) is None
    assert nc.check_out(tmp_path, [tmp_path], repo_root=tmp_path)
    assert nc.check_out(tmp_path / "new", [tmp_path / "other"], repo_root=tmp_path)
    assert nc.check_out(sec / "new", [tmp_path], repo_root=tmp_path)
    # SPEC_ROOTS default
    assert nc.SPEC_ROOTS == [ROOT / "docs" / "pilot" / "nemotron_specs"]


def test_a_partial_or_surprising_reply_is_never_written():
    ok, refused = nc.parse_files(block("a.py") + block("b.py"))
    assert nc.exact_set(ok, refused, ["a.py", "b.py"]) is None
    assert nc.exact_set(ok, refused, ["a.py"])
    assert nc.exact_set(ok, refused, ["a.py", "b.py", "c.py"])
    ok, refused = nc.parse_files(block("a.py") + block("../b.py"))
    assert nc.exact_set(ok, refused, ["a.py"])


# --- New tests for policy loading and fail-closed behavior ---

def test_load_policy_missing_file(tmp_path):
    missing = tmp_path / "missing.json"
    with pytest.raises(ValueError, match="policy file not found"):
        nc.load_policy(missing)


def test_load_policy_invalid_json(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{ not json }", encoding="utf-8")
    with pytest.raises(ValueError, match="not valid JSON"):
        nc.load_policy(bad)


def test_load_policy_wrong_version(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text('{"version": 2, "forbidden_text": {"pattern": "zz_forbidden_zz", "ignore_case": true, "refusal_reason": "r", "system_rule": "s", "refused_examples": ["x"]}}', encoding="utf-8")
    with pytest.raises(ValueError, match="version must be the integer 1"):
        nc.load_policy(bad)


def test_load_policy_missing_key(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text('{"version": 1, "forbidden_text": {"pattern": "zz_forbidden_zz", "ignore_case": true, "refusal_reason": "r", "system_rule": "s"}}', encoding="utf-8")
    with pytest.raises(ValueError, match="missing key"):
        nc.load_policy(bad)


def test_load_policy_ignore_case_not_bool(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text('{"version": 1, "forbidden_text": {"pattern": "zz_forbidden_zz", "ignore_case": "yes", "refusal_reason": "r", "system_rule": "s", "refused_examples": ["x"]}}', encoding="utf-8")
    with pytest.raises(ValueError, match="must be bool"):
        nc.load_policy(bad)


def test_load_policy_empty_refused_examples(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text('{"version": 1, "forbidden_text": {"pattern": "zz_forbidden_zz", "ignore_case": true, "refusal_reason": "r", "system_rule": "s", "refused_examples": []}}', encoding="utf-8")
    with pytest.raises(ValueError, match="non-empty list"):
        nc.load_policy(bad)


def test_load_policy_bad_pattern(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text('{"version": 1, "forbidden_text": {"pattern": "[", "ignore_case": true, "refusal_reason": "r", "system_rule": "s", "refused_examples": ["x"]}}', encoding="utf-8")
    with pytest.raises(ValueError, match="does not compile"):
        nc.load_policy(bad)


def test_parse_files_with_custom_policy(tmp_path):
    pol_file = tmp_path / "pol.json"
    pol_file.write_text('{"version": 1, "forbidden_text": {"pattern": "zz_forbidden_zz", "ignore_case": true, "refusal_reason": "custom reason", "system_rule": "rule", "refused_examples": ["zz_forbidden_zz"]}}', encoding="utf-8")
    pol = nc.load_policy(pol_file)
    ok, refused = nc.parse_files(block("a.py", "clean code"), policy=pol)
    assert ok == {"a.py": "clean code\n"}
    assert refused == []
    ok, refused = nc.parse_files(block("b.py", "zz_forbidden_zz here"), policy=pol)
    assert ok == {}
    assert refused == [("b.py", "custom reason")]


def test_parse_files_fail_closed_when_policy_unavailable(monkeypatch):
    monkeypatch.setattr(nc, "POLICY", None)
    monkeypatch.setattr(nc, "POLICY_ERROR", "x")
    ok, refused = nc.parse_files(block("a.py", "x = 1"))
    assert ok == {}
    assert refused == [("a.py", "policy unavailable: x")]


@pytest.mark.parametrize("path,expected", [
    ("./config/codegen_policy.json", "protected policy file"),
    ("config//codegen_policy.json", "protected policy file"),
    ("config/./codegen_policy.json", "protected policy file"),
    ("CONFIG/./Codegen_Policy.json", "protected policy file"),
    ("config/other.json", None),
    ("configx/codegen_policy.json", None),
])
def test_check_path_protected_policy_file_variants(path, expected):
    assert nc.check_path(path) == expected


def test_load_policy_directory_raises(tmp_path):
    with pytest.raises(ValueError, match="policy file unreadable"):
        nc.load_policy(tmp_path)


def test_load_policy_non_object_json_raises(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("[1, 2]", encoding="utf-8")
    with pytest.raises(ValueError, match="policy file must be a JSON object"):
        nc.load_policy(bad)


def test_load_policy_invalid_utf8_raises(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_bytes(b"\xff\xfe")
    with pytest.raises(ValueError, match="policy file unreadable"):
        nc.load_policy(bad)


def test_unfinished_blocks_refused(tmp_path):
    # One valid block + unfinished header
    reply = block("a.py") + "FILE: b.py\n```python\nunclosed"
    ok, refused = nc.parse_files(reply)
    assert ok == {"a.py": "x = 1\n"}
    assert ("b.py", "unfinished block") in refused
    assert nc.exact_set(ok, refused, ["a.py"]) is not None

    # Only unfinished block
    reply2 = "FILE: c.py\n```python\nno close"
    ok2, refused2 = nc.parse_files(reply2)
    assert ok2 == {}
    assert ("c.py", "unfinished block") in refused2

    # Complete two-block reply
    reply3 = block("a.py") + block("b.py")
    ok3, refused3 = nc.parse_files(reply3)
    assert nc.exact_set(ok3, refused3, ["a.py", "b.py"]) is None


def test_unfinished_block_count_matches_excess_headers(tmp_path):
    # Two complete blocks for a.py, three headers -> one unfinished
    reply = block("a.py", "x=1") + block("a.py", "y=2") + "FILE: a.py\n```python\nunclosed"
    ok, refused = nc.parse_files(reply)
    assert ok == {"a.py": "x=1\n"}
    assert refused.count(("a.py", "duplicate")) == 1
    assert refused.count(("a.py", "unfinished block")) == 1

    # Three headers, one complete -> two unfinished
    reply2 = block("b.py") + "FILE: b.py\n```python\nx\n" + "FILE: b.py\n```python\\uny"
    ok2, refused2 = nc.parse_files(reply2)
    assert ok2 == {"b.py": "x = 1\n"}
    # The block pattern treats a fence line that starts with three backticks as a closing fence (known limitation, out of scope).
    assert nc.exact_set(ok2, refused2, ["b.py"]) == "2 block(s) refused"


# --- New tests for strict version type checking (FIX ROUND 3) ---

def test_load_policy_version_true_rejected(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text('{"version": true, "forbidden_text": {"pattern": "zz_forbidden_zz", "ignore_case": true, "refusal_reason": "r", "system_rule": "s", "refused_examples": ["x"]}}', encoding="utf-8")
    with pytest.raises(ValueError, match="policy version must be the integer 1, got True"):
        nc.load_policy(bad)


def test_load_policy_version_float_rejected(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text('{"version": 1.0, "forbidden_text": {"pattern": "zz_forbidden_zz", "ignore_case": true, "refusal_reason": "r", "system_rule": "s", "refused_examples": ["x"]}}', encoding="utf-8")
    with pytest.raises(ValueError, match="policy version must be the integer 1, got 1.0"):
        nc.load_policy(bad)


def test_load_policy_version_string_rejected(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text('{"version": "1", "forbidden_text": {"pattern": "zz_forbidden_zz", "ignore_case": true, "refusal_reason": "r", "system_rule": "s", "refused_examples": ["x"]}}', encoding="utf-8")
    with pytest.raises(ValueError, match="policy version must be the integer 1, got '1'"):
        nc.load_policy(bad)


def test_load_policy_version_int_1_accepted(tmp_path):
    good = tmp_path / "good.json"
    good.write_text('{"version": 1, "forbidden_text": {"pattern": "zz_forbidden_zz", "ignore_case": true, "refusal_reason": "r", "system_rule": "s", "refused_examples": ["x"]}}', encoding="utf-8")
    pol = nc.load_policy(good)
    assert pol is not None
    assert "pattern" in pol


# --- New tests for FIX ROUND 4: all exceptions become ValueError ---

def test_load_policy_deeply_nested_json_raises_valueerror(tmp_path):
    """A valid but deeply nested JSON (100000 '[' then 100000 ']') must raise ValueError, not RecursionError."""
    bad = tmp_path / "deep.json"
    # Create a deeply nested array that will cause RecursionError in json.loads
    deep_json = "[" * 100000 + "]" * 100000
    bad.write_text(deep_json, encoding="utf-8")
    with pytest.raises(ValueError, match="policy unusable: RecursionError"):
        nc.load_policy(bad)


def test_load_policy_monkeypatched_json_loads_typeerror_raises_valueerror(tmp_path, monkeypatch):
    """Monkeypatching json.loads to raise TypeError must yield ValueError from load_policy."""
    good = tmp_path / "good.json"
    good.write_text('{"version": 1, "forbidden_text": {"pattern": "zz_forbidden_zz", "ignore_case": true, "refusal_reason": "r", "system_rule": "s", "refused_examples": ["x"]}}', encoding="utf-8")
    
    def bad_loads(*args, **kwargs):
        raise TypeError("boom")
    
    monkeypatch.setattr(json, "loads", bad_loads)
    with pytest.raises(ValueError, match="policy unusable: TypeError: boom"):
        nc.load_policy(good)
