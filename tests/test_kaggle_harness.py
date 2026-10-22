"""The Kaggle Linux harness verdict logic, with synthetic JUnit data (no Kaggle, no Linux claim is made here)."""
from __future__ import annotations

import importlib.util
import sys

import pytest

from tests.conftest import REPO

SPEC = importlib.util.spec_from_file_location("linux_cpu_verify", REPO / "scripts" / "kaggle" / "linux_cpu_verify.py")
lv = importlib.util.module_from_spec(SPEC)
sys.modules["linux_cpu_verify"] = lv
SPEC.loader.exec_module(lv)

JUNIT = """<testsuites><testsuite>
<testcase classname="tests.test_a" name="test_ok"/>
<testcase classname="tests.test_a" name="test_bad"><failure message="boom"/></testcase>
<testcase classname="tests.test_a" name="test_skip"><skipped type="pytest.skip" message="symlinks unavailable"/></testcase>
<testcase classname="tests.test_a" name="test_err"><error message="e"/></testcase>
</testsuite></testsuites>"""


def rows(**outcomes):
    return [{"id": k, "outcome": v, "detail": "reason"} for k, v in outcomes.items()]


def test_parse_junit_outcomes(tmp_path):
    path = tmp_path / "j.xml"; path.write_text(JUNIT, encoding="utf-8")
    got = {r["id"]: r["outcome"] for r in lv.parse_junit(path)}
    assert got == {"tests/test_a.py::test_ok": "passed", "tests/test_a.py::test_bad": "failed",
                   "tests/test_a.py::test_skip": "skipped", "tests/test_a.py::test_err": "error"}


def test_pass_needs_posix_all_required_passed_and_supplementary():
    required = ["t::a", "t::b"]
    full = rows(**{"t::a": "passed", "t::b": "passed", "t::c": "skipped"})
    supp = rows(**{"s::x": "passed"})
    good = lv.evaluate(full, supp, required, posix=True, kaggle=True)
    assert good["verdict"] == "LINUX_CPU_PASS_ON_KAGGLE" and good["skipped"][0]["id"] == "t::c"
    assert lv.evaluate(full, supp, required, posix=True, kaggle=False)["verdict"] == "LINUX_CPU_PASS_NON_KAGGLE_HOST"
    assert lv.evaluate(full, supp, required, posix=False, kaggle=False)["verdict"] == "INCOMPLETE_NOT_LINUX"   # never a Linux PASS


@pytest.mark.parametrize("full,supp", [
    ({"t::a": "passed", "t::b": "skipped"}, {"s::x": "passed"}),         # a required POSIX test was skipped
    ({"t::a": "passed"}, {"s::x": "passed"}),                            # a required test was not collected
    ({"t::a": "passed", "t::b": "passed", "t::c": "failed"}, {"s::x": "passed"}),
    ({"t::a": "passed", "t::b": "passed"}, {"s::x": "failed"}),
    ({"t::a": "passed", "t::b": "passed"}, {}),                          # supplementary produced nothing
])
def test_any_gap_is_a_failure(full, supp):
    out = lv.evaluate(rows(**full), rows(**supp), ["t::a", "t::b"], posix=True, kaggle=True)
    assert out["verdict"] == "LINUX_CPU_FAIL" and out["problems"]


def test_required_ids_exist_in_the_baseline_test_files():
    import re, subprocess
    for rid in lv.REQUIRED:
        path, name = rid.split("::")
        text = subprocess.run(["git", "-C", str(REPO), "show", f"{lv.BASELINE}:{path}"], capture_output=True, text=True, check=True).stdout
        assert re.search(rf"def {name}\(", text), rid


def test_wrong_commit_is_not_run(tmp_path):
    import subprocess
    repo = tmp_path / "r"; repo.mkdir()
    for cmd in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(repo), *cmd], check=True)
    (repo / "a").write_text("a"); subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "c"], check=True)
    code = lv.main(["--repo", str(repo), "--harness-dir", str(tmp_path), "--out", str(tmp_path / "out")])
    import json
    receipt = json.loads((tmp_path / "out" / "receipt.json").read_text())
    assert code == 1 and receipt["verdict"] == "NOT_RUN_WRONG_COMMIT"
    assert (tmp_path / "out.zip").is_file() and "environment.json" in receipt["artifacts"]
