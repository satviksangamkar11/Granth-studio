import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("nc", ROOT / "scripts" / "source" / "nemotron_code.py")
nc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nc)


def block(path, body="x = 1"):
    return f"FILE: {path}\n```python\n{body}\n```\n"


@pytest.mark.parametrize("path", ["../x.py", "/etc/x.py", "C:/x.py", "secrets/k.py", "a/.git/x.py", "x.exe", "x.sh"])
def test_bad_paths_are_refused(path):
    ok, refused = nc.parse_files(block(path))
    assert not ok and refused[0][0] == path


def test_good_files_pass_and_blender_code_is_refused():
    ok, refused = nc.parse_files(block("pipeline/a.py") + block("pipeline/b.py", "import bpy\nbpy.ops.x()") + block("pipeline/a.py", "y = 2"))
    assert list(ok) == ["pipeline/a.py"] and ok["pipeline/a.py"] == "x = 1\n"
    assert {r[1] for r in refused} == {"Blender/animation code (D-017)", "duplicate"}


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
    assert nc.check_spec(good) is None
    assert nc.check_spec(tmp_path / "missing.md")
    (tmp_path / "k.json").write_text("{}", encoding="utf-8")
    assert nc.check_spec(tmp_path / "k.json")
    sec = tmp_path / "secrets"
    sec.mkdir()
    (sec / "a.md").write_text("k", encoding="utf-8")
    assert "forbidden" in nc.check_spec(sec / "a.md")
    big = tmp_path / "big.md"
    big.write_text("x" * 300_000, encoding="utf-8")
    assert nc.check_spec(big)
    assert nc.check_out(tmp_path / "new", [tmp_path]) is None
    assert nc.check_out(tmp_path, [tmp_path])
    assert nc.check_out(tmp_path / "new", [tmp_path / "other"])
    assert nc.check_out(sec / "new", [tmp_path])


def test_a_partial_or_surprising_reply_is_never_written():
    ok, refused = nc.parse_files(block("a.py") + block("b.py"))
    assert nc.exact_set(ok, refused, ["a.py", "b.py"]) is None
    assert nc.exact_set(ok, refused, ["a.py"])
    assert nc.exact_set(ok, refused, ["a.py", "b.py", "c.py"])
    ok, refused = nc.parse_files(block("a.py") + block("../b.py"))
    assert nc.exact_set(ok, refused, ["a.py"])
