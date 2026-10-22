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


REQ = ["t::a", "t::b"]
SUPP = ["s::x", "s::y"]
OK_CODES = {"full": 0, "supplementary": 0}


def evaluate(full, supp, **overrides):
    args = dict(required=REQ, posix=True, kaggle=True, exit_codes=OK_CODES, supp_required=SUPP, expected_total=3)
    args.update(overrides)
    return lv.evaluate(full, supp, **args)


GOOD_FULL = rows(**{"t::a": "passed", "t::b": "passed", "t::c": "skipped"})
GOOD_SUPP = rows(**{"s::x": "passed", "s::y": "passed"})


def test_pass_needs_posix_exit_codes_complete_collection_and_every_required_test():
    good = evaluate(GOOD_FULL, GOOD_SUPP)
    assert good["verdict"] == "LINUX_CPU_PASS_ON_KAGGLE" and good["skipped"][0]["id"] == "t::c" and good["collected"] == 3
    assert evaluate(GOOD_FULL, GOOD_SUPP, kaggle=False)["verdict"] == "LINUX_CPU_PASS_NON_KAGGLE_HOST"
    assert evaluate(GOOD_FULL, GOOD_SUPP, posix=False)["verdict"] == "INCOMPLETE_NOT_LINUX"      # never a Linux PASS


@pytest.mark.parametrize("name,kwargs", [
    ("required skipped", dict(full=rows(**{"t::a": "passed", "t::b": "skipped", "t::c": "passed"}))),
    ("required missing", dict(full=rows(**{"t::a": "passed", "t::c": "passed", "t::d": "passed"}))),
    ("a failure", dict(full=rows(**{"t::a": "passed", "t::b": "passed", "t::c": "failed"}))),
    ("supplementary failed", dict(supp=rows(**{"s::x": "passed", "s::y": "failed"}))),
    ("supplementary test missing", dict(supp=rows(**{"s::x": "passed"}))),                         # reduced collection
    ("no supplementary at all", dict(supp=[])),
    ("unexpected extra supplementary", dict(supp=rows(**{"s::x": "passed", "s::y": "passed", "s::z": "passed"}))),
    ("full suite exit code 1 despite passing JUnit", dict(exit_codes={"full": 1, "supplementary": 0})),
    ("supplementary exit code 1 despite passing JUnit", dict(exit_codes={"full": 0, "supplementary": 1})),
    ("filtered collection", dict(full=rows(**{"t::a": "passed", "t::b": "passed"}))),               # 2 collected, 3 expected
    ("duplicate ids", dict(full=rows(**{"t::a": "passed", "t::b": "passed"}) + rows(**{"t::a": "passed"}))),
])
def test_any_gap_is_a_failure(name, kwargs):
    full = kwargs.pop("full", GOOD_FULL); supp = kwargs.pop("supp", GOOD_SUPP)
    out = evaluate(full, supp, **kwargs)
    assert out["verdict"] == "LINUX_CPU_FAIL" and out["problems"], name


def test_the_ten_required_baseline_results_alone_do_not_pass():
    """Codex finding: replaying only the required results plus one supplementary pass must not reach PASS."""
    full = rows(**{rid: "passed" for rid in lv.REQUIRED})
    supp = rows(**{lv.SUPPLEMENTARY[0]: "passed"})
    out = lv.evaluate(full, supp, lv.REQUIRED, True, True, OK_CODES, lv.SUPPLEMENTARY, lv.EXPECTED_BASELINE_TESTS)
    assert out["verdict"] == "LINUX_CPU_FAIL"
    assert any("collected 10 tests" in p for p in out["problems"]) and any("supplementary test" in p for p in out["problems"])


def test_supplementary_ids_match_the_harness_file_and_total_matches_the_recorded_baseline_run():
    import re
    text = (REPO / "scripts" / "kaggle" / "posix_primitives_tests.py").read_text(encoding="utf-8")
    assert sorted(re.findall(r"^def (test_\w+)\(", text, re.M)) == sorted(i.split("::")[1] for i in lv.SUPPLEMENTARY)
    recorded = lv.parse_junit(REPO / "benchmarks" / "linux" / "junit_full.xml")      # the real Kaggle run of f8d5d02
    assert len(recorded) == lv.EXPECTED_BASELINE_TESTS == 321
    assert all(r["id"] in {x["id"] for x in recorded} for r in rows(**{i: "x" for i in lv.REQUIRED}))


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
