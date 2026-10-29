# FIX CALL: return BOTH files in full: `scripts/source/fix_loop.py` and `tests/test_fix_loop.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
..F...........F.....FFF..F....F.........                                 [100%]
================================== FAILURES ===================================
____________________ TestLoadJob.test_invalid_dotdot_path _____________________
tests\test_fix_loop.py:56: in test_invalid_dotdot_path
    with pytest.raises(ValueError, match=r"\.\. not allowed"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AssertionError: Regex pattern did not match.
E     Expected regex: '\\.\\. not allowed'
E     Actual message: "files[0]: '..' not allowed: ../a.py"
_______________ TestBuildPrompt.test_round_one_with_pytest_tail _______________
tests\test_fix_loop.py:169: in test_round_one_with_pytest_tail
    assert user.count("x") == 9000
E   AssertionError: assert 9002 == 9000
E    +  where 9002 = <built-in method count of str object at 0x000002A9E7EE14D0>('x')
E    +    where <built-in method count of str object at 0x000002A9E7EE14D0> = 'SPEC:\nSPEC\n\nEXPECTED FILES:\na.py: (new file)\n\nPYTEST OUTPUT (last 9000 chars):\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx...xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n\nFix exactly the problems shown above. Change nothing else.\n'.count
_________________ TestRunJob.test_fails_then_passes_round_one _________________
tests\test_fix_loop.py:309: in test_fails_then_passes_round_one
    assert "fail" in caller_calls[1][1].lower()
E   AssertionError: assert 'fail' in 'spec:\nspec\n\nexpected files:\na.py:\nbad\n'
E    +  where 'spec:\nspec\n\nexpected files:\na.py:\nbad\n' = <built-in method lower of str object at 0x000002A9EA56B370>()
E    +    where <built-in method lower of str object at 0x000002A9EA56B370> = 'SPEC:\nspec\n\nEXPECTED FILES:\na.py:\nbad\n'.lower
---------------------------- Captured stdout call -----------------------------
job2 round 0: tests fail files ok
job2 round 1: tests pass files ok
job2: passed-no-review
______________ TestRunJob.test_missing_expected_file_fails_round ______________
tests\test_fix_loop.py:343: in test_missing_expected_file_fails_round
    assert "missing" in caller_calls[1][1].lower()
E   AssertionError: assert 'missing' in 'spec:\nspec\n\nexpected files:\na.py: (new file)\nb.py: (new file)\n'
E    +  where 'spec:\nspec\n\nexpected files:\na.py: (new file)\nb.py: (new file)\n' = <built-in method lower of str object at 0x000002A9EA405DF0>()
E    +    where <built-in method lower of str object at 0x000002A9EA405DF0> = 'SPEC:\nspec\n\nEXPECTED FILES:\na.py: (new file)\nb.py: (new file)\n'.lower
---------------------------- Captured stdout call -----------------------------
job3 round 0: tests fail files bad
job3 round 1: tests pass files ok
job3: passed-no-review
___________________ TestRunJob.test_extra_file_fails_round ____________________
tests\test_fix_loop.py:377: in test_extra_file_fails_round
    assert "extra" in caller_calls[1][1].lower()
E   AssertionError: assert 'extra' in 'spec:\nspec\n\nexpected files:\na.py: (new file)\n'
E    +  where 'spec:\nspec\n\nexpected files:\na.py: (new file)\n' = <built-in method lower of str object at 0x000002A9EA3C3CF0>()
E    +    where <built-in method lower of str object at 0x000002A9EA3C3CF0> = 'SPEC:\nspec\n\nEXPECTED FILES:\na.py: (new file)\n'.lower
---------------------------- Captured stdout call -----------------------------
job4 round 0: tests fail files bad
job4 round 1: tests pass files ok
job4: passed-no-review
_______________________ TestRunJob.test_coder_exception _______________________
tests\test_fix_loop.py:464: in test_coder_exception
    assert result["state"] == "passed-no-review"
E   AssertionError: assert 'failed' == 'passed-no-review'
E     
E     - passed-no-review
E     + failed
---------------------------- Captured stdout call -----------------------------
job7 round 0: tests fail files bad
job7 round 1: tests fail files bad
job7 round 2: tests fail files bad
job7: failed
___________________ TestRunJob.test_review_rounds_exhausted ___________________
tests\test_fix_loop.py:618: in test_review_rounds_exhausted
    assert result["state"] == "passed-no-review"
E   AssertionError: assert 'failed' == 'passed-no-review'
E     
E     - passed-no-review
E     + failed
---------------------------- Captured stdout call -----------------------------
job12 round 0: tests pass files ok
job12 round 1: tests fail files bad
job12: failed
============================== warnings summary ===============================
tests/test_fix_loop.py: 46 warnings
  D:\aai work\granthstudio\scripts\source\fix_loop.py:267: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    "updated": datetime.utcnow().isoformat() + "Z",

tests/test_fix_loop.py: 11 warnings
  D:\aai work\granthstudio\scripts\source\fix_loop.py:472: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    return {"name": name, "state": state, "round": last_round_no, "tests_passed": True, "review_verdict": review_verdict, "rounds": rounds_record, "updated": datetime.utcnow().isoformat() + "Z"}

tests/test_fix_loop.py::TestRunJob::test_coder_exception
tests/test_fix_loop.py::TestRunJob::test_max_rounds_exceeded_restores_original
tests/test_fix_loop.py::TestRunJob::test_no_files_outside_expected_and_status_dir
  D:\aai work\granthstudio\scripts\source\fix_loop.py:355: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    return {"name": name, "state": state, "round": last_round_no, "tests_passed": False, "review_verdict": None, "rounds": rounds_record, "updated": datetime.utcnow().isoformat() + "Z"}

tests/test_fix_loop.py::TestRunJob::test_review_rounds_exhausted
  D:\aai work\granthstudio\scripts\source\fix_loop.py:458: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    return {"name": name, "state": state, "round": fix_round_no, "tests_passed": False, "review_verdict": review_verdict, "rounds": rounds_record, "updated": datetime.utcnow().isoformat() + "Z"}

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED tests/test_fix_loop.py::TestLoadJob::test_invalid_dotdot_path - Assert...
FAILED tests/test_fix_loop.py::TestBuildPrompt::test_round_one_with_pytest_tail
FAILED tests/test_fix_loop.py::TestRunJob::test_fails_then_passes_round_one
FAILED tests/test_fix_loop.py::TestRunJob::test_missing_expected_file_fails_round
FAILED tests/test_fix_loop.py::TestRunJob::test_extra_file_fails_round - Asse...
FAILED tests/test_fix_loop.py::TestRunJob::test_coder_exception - AssertionEr...
FAILED tests/test_fix_loop.py::TestRunJob::test_review_rounds_exhausted - Ass...
7 failed, 33 passed, 61 warnings in 2.62s

```

## SPEC
# SPEC: NEW `scripts/source/fix_loop.py` + NEW `tests/test_fix_loop.py`. Return exactly these TWO files in full; do not output or change any other file.
Purpose (owner 2026-10-29, token budget): automate the whole write -> test -> fix -> review loop so that one command runs it with API calls only and the owner's assistant just checks the result every half hour. A JOB names a spec, the files to produce, the tests to run and optional reference files. The tool asks the coder model (Nemotron 3 Ultra, thinking ON, effort medium) for the files, writes them, runs pytest, sends the REAL failure output back until the tests pass, then (optional) asks the GLM reviewer for a verdict and feeds a FIX FIRST report back until READY. Standard library only; `from __future__ import annotations`; nothing at import time except imports and definitions; plain functions; no key or secret is ever printed, logged, written or put in an exception.

## Existing code (load by importlib BY PATH from the repo root; do not modify)
- `scripts/source/draft_source.py` (module `ds`): `ds.nt.load_keys()`, `ds.nt.KeyPool(keys)`, `ds.nt.scrub(text, keys)`, `ds.chat_stream(pool, keys, model, system, user, max_tokens=N) -> (reply, info)` (`info`: status, wall_s, finish, usage, error; usable reply = status 200 and non-empty text).
- `scripts/source/coder_run.py`: `wrap_ds(original_ds, thinking, effort)` returns a function returning the module with the thinking/effort request fields, the 600 s idle timeout, the length continuation and receipts already applied; use it as `ds = coder_run.wrap_ds(lambda: <loaded draft_source module>, "on", "medium")()`.
- `scripts/source/nemotron_code.py`: `parse_files(reply) -> (files: dict[path -> text], refused: list)` reads the reply blocks `FILE: relative/path` followed by a fenced code block; `check_path(rel) -> reason | None`. Load it by path under the module name `nemotron_code_for_loop` and use ONLY these two functions (its main must not be called).
- `scripts/source/review_run.py`: `run_review(model, prompt_file, files, out_path, *, root=None, max_tokens=64000, idle_s=None, caller=None, effort="medium", scrub_keys=[]) -> dict` with keys including `verdict` (`READY`, `FIX FIRST`, `NONE`), `status`, `out`; the report text is in `out_path`.

## JOB file (JSON)
`{"name": str (letters, digits, dash, underscore), "spec": "docs/.../x.md", "files": ["scripts/a.py", "tests/test_a.py"], "tests": ["tests/test_a.py"], "reference": ["other/file.py", ...], "max_rounds": 10, "review": true, "review_rounds": 4, "review_files": [optional, default = files + spec], "review_prompt": "docs/pilot/REVIEW_PROMPT_STAGE1_FINAL.md" or null, "coder_model": default "nvidia/nemotron-3-ultra-550b-a55b", "reviewer_model": default "z-ai/glm-5.3-flash"}`. Paths are relative to the repo root; a path that is absolute, contains `..`, a component containing `secrets`, or ends with `.env` or `.key` is refused (the job is rejected with `ValueError`).

## API
- `load_job(path) -> dict`: validates and fills defaults; raises `ValueError` with a clear message for any invalid field (types, empty files, tests not inside files or the repo's tests folder, name pattern, max_rounds not in 1..30, review_rounds not in 0..10).
- `build_prompt(job, root, round_no, pytest_output=None, review_report=None) -> tuple[str, str]`: `(system, user)`. System: you write python 3.12 modules and tests for the GranthStudio pipeline; follow the spec exactly; reply with FILE blocks only: for each expected file, `FILE: <path>` then the complete file in a fenced block, nothing else; never write any word related to 3D animation software (the repo code filter blocks files that mention it). User: the spec text; the CURRENT content of each expected file (or `(new file)`); the reference files; and for round > 0 the real pytest output (last 9000 characters) and/or the reviewer report with the instruction to fix exactly those problems and change nothing else.
- `run_pytest(tests: list[str], root: Path, timeout_s: int = 600, python: str | None = None) -> tuple[bool, str]`: runs `python -m pytest -q --tb=short <tests>` (python default `sys.executable`) with `cwd=root`, captures stdout+stderr, returns `(returncode == 0, output)`; a timeout returns `(False, "pytest timed out")`; never raises.
- `run_job(job, root, caller=None, reviewer=None, pytest_runner=None, status_dir=None) -> dict`: the loop. `caller(system, user) -> (reply_text, info)`; default = real Nemotron call through `wrap_ds` (keys loaded ONCE inside, reply scrubbed with `ds.nt.scrub`); `reviewer(files: list[Path], report_path: Path) -> dict` default = a closure over `review_run.run_review(...)`; `pytest_runner` default `run_pytest`. Behaviour: (1) backup the current content of every expected file (or mark it absent) in memory; (2) for round in 0..max_rounds: build the prompt, call the coder (a failed call or empty reply counts as a failed round with the reason; no exception escapes), `parse_files`, require EXACTLY the expected set of files (missing, extra or refused blocks = failed round with the reason in the next prompt), write the files, run the tests; if they pass go to step 3, else keep the files in place and continue with the failure output; (3) if `job["review"]` and review_rounds > 0: write the review report to `<status_dir>/<name>/review_<k>.md`, ask the reviewer; verdict READY -> done; FIX FIRST -> next coder round with the report text and the tests must pass again (a failing round after a review counts toward max_rounds); NONE or a failed review -> record `review: unavailable` and finish as passed-without-review; at most review_rounds reviews. (4) If the tests never pass within max_rounds RESTORE the original files exactly (delete files that were absent) and finish `failed`. (5) After every round write `<status_dir>/<name>/status.json`: `{"name","state": "running"|"passed"|"passed-no-review"|"failed","round","tests_passed","review_verdict","rounds": [{"round","coder_status","files_ok","tests_passed","reason"}],"updated"}` (ISO time) and the coder's reply text of each round to `round_<n>.txt` (scrubbed). `status_dir` default `<root>/_loop`. Returns the final status dict. NEVER writes outside the expected files and the status dir.
- `main(argv=None) -> int`: `--job PATH` (required), `--root PATH` (default repo root), `--dry-run` (validate the job and print the first prompt size, no call). Prints ONE short line per round (`<name> round <n>: tests <pass|fail> files <ok|bad>`) and a final line `<name>: <state>`; returns 0 for passed / passed-no-review, 1 for failed, 2 for an invalid job.

## Tests (`tests/test_fix_loop.py`; offline, fake caller / reviewer / pytest runner, no network, no key; a REAL tiny pytest run in tmp_path for `run_pytest`)
1. `load_job`: valid job with defaults filled; each invalid field in its own isolated test (absolute path, `..`, secrets component, `.env`, bad name, empty files, max_rounds 0 and 31, review_rounds 11, tests outside files/tests folder, non-list).
2. `build_prompt`: round 0 contains the spec text and `(new file)` for an absent file and the content of an existing one; round 1 contains the pytest output tail (only the last 9000 characters of a 20000-character output) and the instruction; a review report is included; the system text contains `FILE:` instructions.
3. `run_pytest` with a tiny passing and a tiny failing test file in tmp_path (real subprocess, `sys.executable`), a timeout (tiny timeout with a sleeping test) returns `(False, ...)`.
4. `run_job` scenarios with fakes (assert the number of coder calls and the files on disk): passes in round 0; fails then passes in round 1 and the second prompt contains the first failure output; reply with a missing expected file or an extra file -> failed round, next prompt mentions it, no stray file written; coder failure (status 500, empty reply, exception) -> failed round, loop continues; never passes within max_rounds=2 -> state `failed` and the ORIGINAL file contents restored exactly (and a file that did not exist before is gone); review READY on the first review; review FIX FIRST then READY (two coder calls after the tests pass), reviewer returning NONE -> `passed-no-review`; review_rounds exhausted; status.json content after each round and `round_<n>.txt` written; no file outside the expected set and the status dir is created; a fake key string returned in the coder reply is NOT present in any file the loop writes (use a `scrub_keys` style parameter `scrub_keys: list[str] = []` on run_job applied to every stored string).
5. `main`: `--dry-run` returns 0 and prints a size line without calling the coder; an invalid job returns 2; (monkeypatch `run_job` for the pass / fail return codes).
6. The module source contains no literal `nvapi-` and no import of `kimi_adapter`.
Use plain assignment and `copy.deepcopy`; never a helper that rejects no-effect mutations; remember `True == 1`.

Reply with only the two FILE blocks:
FILE: scripts/source/fix_loop.py
FILE: tests/test_fix_loop.py


## CURRENT MODULE scripts/source/fix_loop.py
```python
from __future__ import annotations

import json
import sys
import time
import subprocess
import copy
import importlib.util
import re
from pathlib import Path
from datetime import datetime
from typing import Any, Callable, Optional

import yaml
import jsonschema


JOB_SCHEMA = {
    "type": "object",
    "required": ["name", "spec", "files", "tests"],
    "properties": {
        "name": {"type": "string", "pattern": "^[A-Za-z0-9_-]+$"},
        "spec": {"type": "string"},
        "files": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "tests": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "reference": {"type": "array", "items": {"type": "string"}, "default": []},
        "max_rounds": {"type": "integer", "minimum": 1, "maximum": 30, "default": 10},
        "review": {"type": "boolean", "default": True},
        "review_rounds": {"type": "integer", "minimum": 0, "maximum": 10, "default": 4},
        "review_files": {"type": "array", "items": {"type": "string"}, "default": None},
        "review_prompt": {"type": ["string", "null"], "default": "docs/pilot/REVIEW_PROMPT_STAGE1_FINAL.md"},
        "coder_model": {"type": "string", "default": "nvidia/nemotron-3-ultra-550b-a55b"},
        "reviewer_model": {"type": "string", "default": "z-ai/glm-5.3-flash"},
    },
    "additionalProperties": False,
}


def _validate_path(rel: str, root: Path, context: str) -> None:
    p = Path(rel)
    # Check for Unix-style absolute path (starts with /) regardless of platform
    if rel.startswith("/") or (len(rel) >= 2 and rel[1] == ":" and rel[0].isalpha()):
        raise ValueError(f"{context}: absolute path not allowed: {rel}")
    if p.is_absolute():
        raise ValueError(f"{context}: absolute path not allowed: {rel}")
    if ".." in p.parts:
        raise ValueError(f"{context}: '..' not allowed: {rel}")
    for part in p.parts:
        if "secrets" in part:
            raise ValueError(f"{context}: path component contains 'secrets': {rel}")
    if rel.endswith(".env") or rel.endswith(".key"):
        raise ValueError(f"{context}: path ends with .env or .key: {rel}")
    full = (root / rel).resolve()
    try:
        full.relative_to(root.resolve())
    except ValueError:
        raise ValueError(f"{context}: path escapes repo root: {rel}")


def load_job(path: str | Path) -> dict:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    if not isinstance(raw, dict):
        raise ValueError("job file must be a JSON/YAML object")
    try:
        jsonschema.validate(instance=raw, schema=JOB_SCHEMA)
    except jsonschema.exceptions.ValidationError as e:
        raise ValueError(str(e)) from e
    job = dict(raw)
    job.setdefault("reference", [])
    job.setdefault("max_rounds", 10)
    job.setdefault("review", True)
    job.setdefault("review_rounds", 4)
    job.setdefault("review_files", None)
    job.setdefault("review_prompt", "docs/pilot/REVIEW_PROMPT_STAGE1_FINAL.md")
    job.setdefault("coder_model", "nvidia/nemotron-3-ultra-550b-a55b")
    job.setdefault("reviewer_model", "z-ai/glm-5.3-flash")
    root = path.parent.resolve()
    _validate_path(job["spec"], root, "spec")
    for i, f in enumerate(job["files"]):
        _validate_path(f, root, f"files[{i}]")
    for i, t in enumerate(job["tests"]):
        _validate_path(t, root, f"tests[{i}]")
        if t not in job["files"]:
            try:
                Path(t).relative_to("tests")
            except ValueError:
                raise ValueError(f"tests[{i}] not in files and not under tests/: {t}")
    for i, r in enumerate(job["reference"]):
        _validate_path(r, root, f"reference[{i}]")
    if job["review_files"] is not None:
        for i, rf in enumerate(job["review_files"]):
            _validate_path(rf, root, f"review_files[{i}]")
    if job["review_prompt"] is not None:
        _validate_path(job["review_prompt"], root, "review_prompt")
    return job


def _read_file_safe(root: Path, rel: str) -> str | None:
    p = root / rel
    if p.exists():
        return p.read_text(encoding="utf-8")
    return None


def _load_module_by_path(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load module from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Load nemotron_code_for_loop at module level using relative path from this file
_nemotron_code_path = Path(__file__).with_name("nemotron_code.py")
try:
    nemotron_code_for_loop = _load_module_by_path("nemotron_code_for_loop", _nemotron_code_path)
except Exception:
    nemotron_code_for_loop = None  # type: ignore[assignment]


def build_prompt(job: dict, root: Path, round_no: int, pytest_output: str | None = None, review_report: str | None = None) -> tuple[str, str]:
    system = (
        "You write python 3.12 modules and tests for the GranthStudio pipeline. "
        "Follow the spec exactly. Reply with FILE blocks only: for each expected file, "
        "`FILE: <path>` then the complete file in a fenced block, nothing else. "
        "Never write any word related to 3D animation software (the repo code filter blocks files that mention it)."
    )
    spec_text = (root / job["spec"]).read_text(encoding="utf-8")
    user_parts = [f"SPEC:\n{spec_text}\n"]
    user_parts.append("EXPECTED FILES:")
    for rel in job["files"]:
        content = _read_file_safe(root, rel)
        if content is None:
            user_parts.append(f"{rel}: (new file)")
        else:
            user_parts.append(f"{rel}:\n{content}")
    user_parts.append("")
    reference = job.get("reference", [])
    if reference:
        user_parts.append("REFERENCE FILES:")
        for rel in reference:
            content = _read_file_safe(root, rel)
            if content is not None:
                user_parts.append(f"{rel}:\n{content}")
        user_parts.append("")
    if round_no > 0:
        if pytest_output:
            tail = pytest_output[-9000:] if len(pytest_output) > 9000 else pytest_output
            user_parts.append(f"PYTEST OUTPUT (last 9000 chars):\n{tail}\n")
            user_parts.append("Fix exactly the problems shown above. Change nothing else.\n")
        if review_report:
            user_parts.append(f"REVIEW REPORT:\n{review_report}\n")
            user_parts.append("Fix exactly the problems in the review. Change nothing else.\n")
    user = "\n".join(user_parts)
    return system, user


def run_pytest(tests: list[str], root: Path, timeout_s: int = 600, python: str | None = None) -> tuple[bool, str]:
    if python is None:
        python = sys.executable
    cmd = [python, "-m", "pytest", "-q", "--tb=short"] + tests
    try:
        proc = subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=timeout_s)
        output = proc.stdout + proc.stderr
        return proc.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, "pytest timed out"


def _default_caller_factory(root: Path):
    ds_mod = _load_module_by_path("draft_source", root / "scripts/source/draft_source.py")
    coder_run_mod = _load_module_by_path("coder_run", root / "scripts/source/coder_run.py")
    keys = ds_mod.nt.load_keys()
    pool = ds_mod.nt.KeyPool(keys)
    ds = coder_run_mod.wrap_ds(lambda: ds_mod, "on", "medium")()
    def caller(system: str, user: str) -> tuple[str, dict]:
        reply, info = ds.chat_stream(pool, keys, "nvidia/nemotron-3-ultra-550b-a55b", system, user, max_tokens=64000)
        scrubbed = ds_mod.nt.scrub(reply, keys)
        return scrubbed, info
    return caller


def _default_reviewer_factory(root: Path):
    review_run_mod = _load_module_by_path("review_run", root / "scripts/source/review_run.py")
    def reviewer(files: list[Path], report_path: Path) -> dict:
        return review_run_mod.run_review(
            model="z-ai/glm-5.3-flash",
            prompt_file=root / "docs/pilot/REVIEW_PROMPT_STAGE1_FINAL.md",
            files=files,
            out_path=report_path,
            root=root,
            max_tokens=64000,
            idle_s=None,
            caller=None,
            effort="medium",
            scrub_keys=[],
        )
    return reviewer


def run_job(
    job: dict,
    root: Path,
    caller: Callable[[str, str], tuple[str, dict]] | None = None,
    reviewer: Callable[[list[Path], Path], dict] | None = None,
    pytest_runner: Callable[[list[str], Path, int, str | None], tuple[bool, str]] | None = None,
    status_dir: Path | None = None,
    scrub_keys: list[str] | None = None,
) -> dict:
    if caller is None:
        caller = _default_caller_factory(root)
    if reviewer is None:
        reviewer = _default_reviewer_factory(root)
    if pytest_runner is None:
        pytest_runner = run_pytest
    if status_dir is None:
        status_dir = root / "_loop"
    if scrub_keys is None:
        scrub_keys = []

    # Use module-level nemotron_code_for_loop if available (allows patching in tests)
    global nemotron_code_for_loop
    if nemotron_code_for_loop is None:
        nemotron_code_for_loop = _load_module_by_path("nemotron_code_for_loop", root / "scripts/source/nemotron_code.py")
    parse_files = nemotron_code_for_loop.parse_files
    check_path = nemotron_code_for_loop.check_path

    name = job["name"]
    expected_files = job["files"]
    tests = job["tests"]
    max_rounds = job.get("max_rounds", 10)
    review_enabled = job.get("review", True)
    review_rounds = job.get("review_rounds", 4)
    review_files = job.get("review_files") if job.get("review_files") is not None else expected_files + [job["spec"]]
    review_prompt = job.get("review_prompt", "docs/pilot/REVIEW_PROMPT_STAGE1_FINAL.md")

    status_dir_job = status_dir / name
    status_dir_job.mkdir(parents=True, exist_ok=True)

    original_contents: dict[str, str | None] = {}
    for rel in expected_files:
        original_contents[rel] = _read_file_safe(root, rel)

    rounds_record: list[dict] = []
    state = "running"
    tests_passed = False
    review_verdict = None
    last_round_no = 0

    def _scrub(text: str) -> str:
        for k in scrub_keys:
            text = text.replace(k, "[REDACTED]")
        return text

    def _write_status(round_no: int, coder_status: str, files_ok: bool, tests_passed_: bool, reason: str | None):
        nonlocal state, review_verdict
        status = {
            "name": name,
            "state": state,
            "round": round_no,
            "tests_passed": tests_passed_,
            "review_verdict": review_verdict,
            "rounds": rounds_record,
            "updated": datetime.utcnow().isoformat() + "Z",
        }
        (status_dir_job / "status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")

    for round_no in range(max_rounds + 1):
        last_round_no = round_no
        system, user = build_prompt(job, root, round_no)
        try:
            reply_text, info = caller(system, user)
        except Exception as e:
            reply_text = ""
            info = {"status": 0, "error": str(e)}
        scrubbed_reply = _scrub(reply_text)
        (status_dir_job / f"round_{round_no}.txt").write_text(scrubbed_reply, encoding="utf-8")

        coder_status = str(info.get("status", "unknown"))
        files_ok = False
        reason = None
        parsed_files: dict[str, str] = {}
        refused: list = []

        if reply_text and info.get("status") == 200 and reply_text.strip():
            try:
                parsed_files, refused = parse_files(reply_text)
            except Exception as e:
                reason = f"parse_files error: {e}"
        else:
            reason = f"coder call failed: status={info.get('status')}, empty={not bool(reply_text.strip())}"

        if reason is None:
            expected_set = set(expected_files)
            parsed_set = set(parsed_files.keys())
            refused_set = set(refused)
            if parsed_set != expected_set:
                missing = expected_set - parsed_set
                extra = parsed_set - expected_set
                parts = []
                if missing:
                    parts.append(f"missing: {sorted(missing)}")
                if extra:
                    parts.append(f"extra: {sorted(extra)}")
                if refused:
                    parts.append(f"refused: {sorted(refused)}")
                reason = "; ".join(parts)
            else:
                for rel in parsed_files:
                    chk = check_path(rel)
                    if chk is not None:
                        reason = f"check_path failed for {rel}: {chk}"
                        break
                else:
                    files_ok = True

        if files_ok:
            for rel, content in parsed_files.items():
                (root / rel).write_text(content, encoding="utf-8")
            passed, output = pytest_runner(tests, root, timeout_s=600)
            tests_passed = passed
        else:
            passed = False
            output = reason or "files not ok"

        rounds_record.append({
            "round": round_no,
            "coder_status": coder_status,
            "files_ok": files_ok,
            "tests_passed": passed,
            "reason": reason,
        })
        _write_status(round_no, coder_status, files_ok, passed, reason)

        print(f"{name} round {round_no}: tests {'pass' if passed else 'fail'} files {'ok' if files_ok else 'bad'}")

        if passed:
            tests_passed = True
            break

    if not tests_passed:
        state = "failed"
        for rel, orig in original_contents.items():
            p = root / rel
            if orig is None:
                if p.exists():
                    p.unlink()
            else:
                p.write_text(orig, encoding="utf-8")
        _write_status(last_round_no, "", False, False, "max rounds exceeded")
        print(f"{name}: {state}")
        return {"name": name, "state": state, "round": last_round_no, "tests_passed": False, "review_verdict": None, "rounds": rounds_record, "updated": datetime.utcnow().isoformat() + "Z"}

    if review_enabled and review_rounds > 0:
        review_files_paths = [root / rf for rf in review_files]
        for rev_round in range(review_rounds):
            report_path = status_dir_job / f"review_{rev_round}.md"
            try:
                rev_result = reviewer(review_files_paths, report_path)
            except Exception as e:
                rev_result = {"verdict": "NONE", "status": "error", "out": str(e)}
            review_verdict = rev_result.get("verdict", "NONE")
            rounds_record.append({
                "round": f"review_{rev_round}",
                "coder_status": "review",
                "files_ok": True,
                "tests_passed": True,
                "reason": f"verdict={review_verdict}",
            })
            _write_status(last_round_no, "review", True, True, f"verdict={review_verdict}")

            if review_verdict == "READY":
                state = "passed"
                break
            elif review_verdict == "FIX FIRST":
                review_report_text = report_path.read_text(encoding="utf-8") if report_path.exists() else ""
                fix_round_no = last_round_no + 1 + rev_round
                system, user = build_prompt(job, root, fix_round_no, review_report=review_report_text)
                try:
                    reply_text, info = caller(system, user)
                except Exception as e:
                    reply_text = ""
                    info = {"status": 0, "error": str(e)}
                scrubbed_reply = _scrub(reply_text)
                (status_dir_job / f"round_{fix_round_no}.txt").write_text(scrubbed_reply, encoding="utf-8")

                coder_status = str(info.get("status", "unknown"))
                files_ok = False
                reason = None
                parsed_files = {}
                refused = []

                if reply_text and info.get("status") == 200 and reply_text.strip():
                    try:
                        parsed_files, refused = parse_files(reply_text)
                    except Exception as e:
                        reason = f"parse_files error: {e}"
                else:
                    reason = f"coder call failed: status={info.get('status')}, empty={not bool(reply_text.strip())}"

                if reason is None:
                    expected_set = set(expected_files)
                    parsed_set = set(parsed_files.keys())
                    if parsed_set != expected_set:
                        missing = expected_set - parsed_set
                        extra = parsed_set - expected_set
                        parts = []
                        if missing:
                            parts.append(f"missing: {sorted(missing)}")
                        if extra:
                            parts.append(f"extra: {sorted(extra)}")
                        if refused:
                            parts.append(f"refused: {sorted(refused)}")
                        reason = "; ".join(parts)
                    else:
                        for rel in parsed_files:
                            chk = check_path(rel)
                            if chk is not None:
                                reason = f"check_path failed for {rel}: {chk}"
                                break
                        else:
                            files_ok = True

                if files_ok:
                    for rel, content in parsed_files.items():
                        (root / rel).write_text(content, encoding="utf-8")
                    passed, output = pytest_runner(tests, root, timeout_s=600)
                    tests_passed = passed
                else:
                    passed = False
                    output = reason or "files not ok"

                rounds_record.append({
                    "round": fix_round_no,
                    "coder_status": coder_status,
                    "files_ok": files_ok,
                    "tests_passed": passed,
                    "reason": reason,
                })
                _write_status(fix_round_no, coder_status, files_ok, passed, reason)

                print(f"{name} round {fix_round_no}: tests {'pass' if passed else 'fail'} files {'ok' if files_ok else 'bad'}")

                if not passed:
                    state = "failed"
                    for rel, orig in original_contents.items():
                        p = root / rel
                        if orig is None:
                            if p.exists():
                                p.unlink()
                        else:
                            p.write_text(orig, encoding="utf-8")
                    _write_status(fix_round_no, "", False, False, "review fix failed")
                    print(f"{name}: {state}")
                    return {"name": name, "state": state, "round": fix_round_no, "tests_passed": False, "review_verdict": review_verdict, "rounds": rounds_record, "updated": datetime.utcnow().isoformat() + "Z"}
            else:
                state = "passed-no-review"
                review_verdict = "unavailable"
                break
        else:
            state = "passed-no-review"
            review_verdict = "unavailable"
    else:
        state = "passed-no-review"
        review_verdict = "unavailable"

    _write_status(last_round_no, "", True, True, "done")
    print(f"{name}: {state}")
    return {"name": name, "state": state, "round": last_round_no, "tests_passed": True, "review_verdict": review_verdict, "rounds": rounds_record, "updated": datetime.utcnow().isoformat() + "Z"}


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", required=True)
    parser.add_argument("--root", default=".")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    try:
        job = load_job(root / args.job)
    except ValueError as e:
        print(f"invalid job: {e}", file=sys.stderr)
        return 2

    if args.dry_run:
        system, user = build_prompt(job, root, 0)
        print(f"dry-run: prompt size {len(system) + len(user)} chars")
        return 0

    result = run_job(job, root)
    if result["state"] in ("passed", "passed-no-review"):
        return 0
    return 1

```

## CURRENT TESTS tests/test_fix_loop.py
```python
from __future__ import annotations

import json
import sys
import tempfile
import textwrap
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock, call

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.source import fix_loop


class TestLoadJob:
    def test_valid_job_with_defaults(self, tmp_path: Path):
        job_data = {
            "name": "test-job",
            "spec": "docs/spec.md",
            "files": ["scripts/a.py", "tests/test_a.py"],
            "tests": ["tests/test_a.py"],
        }
        job_file = tmp_path / "job.yaml"
        job_file.write_text(yaml.dump(job_data))
        (tmp_path / "docs").mkdir(parents=True)
        (tmp_path / "docs" / "spec.md").write_text("spec content")
        (tmp_path / "scripts").mkdir()
        (tmp_path / "tests").mkdir()

        job = fix_loop.load_job(job_file)
        assert job["name"] == "test-job"
        assert job["max_rounds"] == 10
        assert job["review"] is True
        assert job["review_rounds"] == 4
        assert job["review_files"] is None
        assert job["review_prompt"] == "docs/pilot/REVIEW_PROMPT_STAGE1_FINAL.md"
        assert job["coder_model"] == "nvidia/nemotron-3-ultra-550b-a55b"
        assert job["reviewer_model"] == "z-ai/glm-5.3-flash"

    def test_invalid_absolute_path(self, tmp_path: Path):
        job_data = {"name": "j", "spec": "/abs/path.md", "files": ["a.py"], "tests": ["tests/a.py"]}
        job_file = tmp_path / "job.yaml"
        job_file.write_text(yaml.dump(job_data))
        (tmp_path / "spec.md").write_text("x")
        with pytest.raises(ValueError, match="absolute path not allowed"):
            fix_loop.load_job(job_file)

    def test_invalid_dotdot_path(self, tmp_path: Path):
        job_data = {"name": "j", "spec": "spec.md", "files": ["../a.py"], "tests": ["tests/a.py"]}
        job_file = tmp_path / "job.yaml"
        job_file.write_text(yaml.dump(job_data))
        (tmp_path / "spec.md").write_text("x")
        with pytest.raises(ValueError, match=r"\.\. not allowed"):
            fix_loop.load_job(job_file)

    def test_invalid_secrets_component(self, tmp_path: Path):
        job_data = {"name": "j", "spec": "spec.md", "files": ["secrets/key.py"], "tests": ["tests/a.py"]}
        job_file = tmp_path / "job.yaml"
        job_file.write_text(yaml.dump(job_data))
        (tmp_path / "spec.md").write_text("x")
        with pytest.raises(ValueError, match="contains 'secrets'"):
            fix_loop.load_job(job_file)

    def test_invalid_env_suffix(self, tmp_path: Path):
        job_data = {"name": "j", "spec": "spec.md", "files": ["a.env"], "tests": ["tests/a.py"]}
        job_file = tmp_path / "job.yaml"
        job_file.write_text(yaml.dump(job_data))
        (tmp_path / "spec.md").write_text("x")
        with pytest.raises(ValueError, match=r"ends with \.env or \.key"):
            fix_loop.load_job(job_file)

    def test_invalid_key_suffix(self, tmp_path: Path):
        job_data = {"name": "j", "spec": "spec.md", "files": ["a.key"], "tests": ["tests/a.py"]}
        job_file = tmp_path / "job.yaml"
        job_file.write_text(yaml.dump(job_data))
        (tmp_path / "spec.md").write_text("x")
        with pytest.raises(ValueError, match=r"ends with \.env or \.key"):
            fix_loop.load_job(job_file)

    def test_invalid_name_pattern(self, tmp_path: Path):
        job_data = {"name": "bad name!", "spec": "spec.md", "files": ["a.py"], "tests": ["tests/a.py"]}
        job_file = tmp_path / "job.yaml"
        job_file.write_text(yaml.dump(job_data))
        (tmp_path / "spec.md").write_text("x")
        with pytest.raises(ValueError):
            fix_loop.load_job(job_file)

    def test_empty_files(self, tmp_path: Path):
        job_data = {"name": "j", "spec": "spec.md", "files": [], "tests": ["tests/a.py"]}
        job_file = tmp_path / "job.yaml"
        job_file.write_text(yaml.dump(job_data))
        (tmp_path / "spec.md").write_text("x")
        with pytest.raises(ValueError):
            fix_loop.load_job(job_file)

    def test_max_rounds_zero(self, tmp_path: Path):
        job_data = {"name": "j", "spec": "spec.md", "files": ["a.py"], "tests": ["tests/a.py"], "max_rounds": 0}
        job_file = tmp_path / "job.yaml"
        job_file.write_text(yaml.dump(job_data))
        (tmp_path / "spec.md").write_text("x")
        with pytest.raises(ValueError):
            fix_loop.load_job(job_file)

    def test_max_rounds_31(self, tmp_path: Path):
        job_data = {"name": "j", "spec": "spec.md", "files": ["a.py"], "tests": ["tests/a.py"], "max_rounds": 31}
        job_file = tmp_path / "job.yaml"
        job_file.write_text(yaml.dump(job_data))
        (tmp_path / "spec.md").write_text("x")
        with pytest.raises(ValueError):
            fix_loop.load_job(job_file)

    def test_review_rounds_11(self, tmp_path: Path):
        job_data = {"name": "j", "spec": "spec.md", "files": ["a.py"], "tests": ["tests/a.py"], "review_rounds": 11}
        job_file = tmp_path / "job.yaml"
        job_file.write_text(yaml.dump(job_data))
        (tmp_path / "spec.md").write_text("x")
        with pytest.raises(ValueError):
            fix_loop.load_job(job_file)

    def test_tests_outside_files_and_tests_folder(self, tmp_path: Path):
        job_data = {"name": "j", "spec": "spec.md", "files": ["a.py"], "tests": ["other/test.py"]}
        job_file = tmp_path / "job.yaml"
        job_file.write_text(yaml.dump(job_data))
        (tmp_path / "spec.md").write_text("x")
        (tmp_path / "a.py").write_text("x")
        with pytest.raises(ValueError, match="not in files and not under tests/"):
            fix_loop.load_job(job_file)

    def test_tests_non_list(self, tmp_path: Path):
        job_data = {"name": "j", "spec": "spec.md", "files": ["a.py"], "tests": "tests/a.py"}
        job_file = tmp_path / "job.yaml"
        job_file.write_text(yaml.dump(job_data))
        (tmp_path / "spec.md").write_text("x")
        with pytest.raises(ValueError):
            fix_loop.load_job(job_file)


class TestBuildPrompt:
    def test_round_zero_new_and_existing(self, tmp_path: Path):
        job = {
            "name": "j",
            "spec": "spec.md",
            "files": ["new.py", "existing.py"],
            "tests": ["tests/test.py"],
            "reference": ["ref.py"],
        }
        (tmp_path / "spec.md").write_text("SPEC CONTENT")
        (tmp_path / "existing.py").write_text("EXISTING CONTENT")
        (tmp_path / "ref.py").write_text("REF CONTENT")
        (tmp_path / "tests").mkdir()

        system, user = fix_loop.build_prompt(job, tmp_path, 0)
        assert "FILE:" in system
        assert "SPEC CONTENT" in user
        assert "new.py: (new file)" in user
        assert "EXISTING CONTENT" in user
        assert "REF CONTENT" in user

    def test_round_one_with_pytest_tail(self, tmp_path: Path):
        job = {"name": "j", "spec": "spec.md", "files": ["a.py"], "tests": ["tests/test.py"]}
        (tmp_path / "spec.md").write_text("SPEC")
        (tmp_path / "tests").mkdir()
        long_output = "x" * 20000
        system, user = fix_loop.build_prompt(job, tmp_path, 1, pytest_output=long_output)
        assert "PYTEST OUTPUT (last 9000 chars)" in user
        assert user.count("x") == 9000
        assert "Fix exactly the problems shown above" in user

    def test_round_with_review_report(self, tmp_path: Path):
        job = {"name": "j", "spec": "spec.md", "files": ["a.py"], "tests": ["tests/test.py"]}
        (tmp_path / "spec.md").write_text("SPEC")
        (tmp_path / "tests").mkdir()
        system, user = fix_loop.build_prompt(job, tmp_path, 1, review_report="REVIEW TEXT")
        assert "REVIEW REPORT" in user
        assert "REVIEW TEXT" in user
        assert "Fix exactly the problems in the review" in user


class TestRunPytest:
    def test_passing_test(self, tmp_path: Path):
        test_file = tmp_path / "test_pass.py"
        test_file.write_text("def test_ok(): assert True\n")
        ok, out = fix_loop.run_pytest([str(test_file.relative_to(tmp_path))], tmp_path, timeout_s=30)
        assert ok is True

    def test_failing_test(self, tmp_path: Path):
        test_file = tmp_path / "test_fail.py"
        test_file.write_text("def test_fail(): assert False\n")
        ok, out = fix_loop.run_pytest([str(test_file.relative_to(tmp_path))], tmp_path, timeout_s=30)
        assert ok is False
        assert "FAILED" in out or "assert False" in out

    def test_timeout(self, tmp_path: Path):
        test_file = tmp_path / "test_slow.py"
        test_file.write_text("import time\ndef test_slow(): time.sleep(10)\n")
        ok, out = fix_loop.run_pytest([str(test_file.relative_to(tmp_path))], tmp_path, timeout_s=1)
        assert ok is False
        assert "timed out" in out.lower()


class TestRunJob:
    def _make_fake_caller(self, replies: list[tuple[str, dict]]):
        calls = []
        def caller(system, user):
            calls.append((system, user))
            if replies:
                return replies.pop(0)
            return "", {"status": 500, "error": "no more replies"}
        return caller, calls

    def _make_fake_reviewer(self, verdicts: list[str]):
        calls = []
        def reviewer(files, report_path):
            calls.append((files, report_path))
            report_path.write_text(f"verdict: {verdicts[0] if verdicts else 'NONE'}")
            return {"verdict": verdicts.pop(0) if verdicts else "NONE", "status": "ok", "out": "ok"}
        return reviewer, calls

    def _make_fake_parse_files(self, results: list[tuple[dict, list]]):
        calls = []
        def parse_files(reply):
            calls.append(reply)
            if results:
                return results.pop(0)
            return {}, []
        return parse_files, calls

    def _make_fake_check_path(self, results: dict[str, str | None]):
        def check_path(rel):
            return results.get(rel)
        return check_path

    def _setup_mocks(self, monkeypatch, parse_files, check_path):
        monkeypatch.setattr(fix_loop, "_load_module_by_path", lambda name, path: MagicMock(
            parse_files=parse_files,
            check_path=check_path,
        ))
        mock_nemotron = MagicMock(parse_files=parse_files, check_path=check_path)
        return patch.object(fix_loop, "nemotron_code_for_loop", mock_nemotron)

    def test_passes_round_zero(self, tmp_path: Path, monkeypatch):
        job = {
            "name": "job1",
            "spec": "spec.md",
            "files": ["a.py"],
            "tests": ["tests/test_a.py"],
            "max_rounds": 2,
            "review": False,
            "review_rounds": 0,
        }
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test_a.py").write_text("def test_ok(): assert True\n")

        caller, caller_calls = self._make_fake_caller([
            ("FILE: a.py\n```python\nprint('hi')\n```", {"status": 200}),
        ])
        reviewer, _ = self._make_fake_reviewer([])
        parse_files, _ = self._make_fake_parse_files([({"a.py": "print('hi')"}, [])])
        check_path = self._make_fake_check_path({"a.py": None})

        monkeypatch.setattr(fix_loop, "run_pytest", lambda tests, root, **kw: (True, "passed"))

        with self._setup_mocks(monkeypatch, parse_files, check_path):
            result = fix_loop.run_job(job, tmp_path, caller=caller, reviewer=reviewer, status_dir=tmp_path / "_loop")

        assert result["state"] == "passed-no-review"
        assert result["tests_passed"] is True
        assert len(caller_calls) == 1

    def test_fails_then_passes_round_one(self, tmp_path: Path, monkeypatch):
        job = {
            "name": "job2",
            "spec": "spec.md",
            "files": ["a.py"],
            "tests": ["tests/test_a.py"],
            "max_rounds": 2,
            "review": False,
            "review_rounds": 0,
        }
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test_a.py").write_text("def test_ok(): assert True\n")

        caller, caller_calls = self._make_fake_caller([
            ("FILE: a.py\n```python\nbad\n```", {"status": 200}),
            ("FILE: a.py\n```python\ngood\n```", {"status": 200}),
        ])
        reviewer, _ = self._make_fake_reviewer([])
        parse_files, _ = self._make_fake_parse_files([
            ({"a.py": "bad"}, []),
            ({"a.py": "good"}, []),
        ])
        check_path = self._make_fake_check_path({"a.py": None})

        pytest_results = [(False, "fail"), (True, "pass")]
        def fake_pytest(tests, root, **kw):
            return pytest_results.pop(0)
        monkeypatch.setattr(fix_loop, "run_pytest", fake_pytest)

        with self._setup_mocks(monkeypatch, parse_files, check_path):
            result = fix_loop.run_job(job, tmp_path, caller=caller, reviewer=reviewer, status_dir=tmp_path / "_loop")

        assert result["state"] == "passed-no-review"
        assert len(caller_calls) == 2
        assert "fail" in caller_calls[1][1].lower()

    def test_missing_expected_file_fails_round(self, tmp_path: Path, monkeypatch):
        job = {
            "name": "job3",
            "spec": "spec.md",
            "files": ["a.py", "b.py"],
            "tests": ["tests/test.py"],
            "max_rounds": 2,
            "review": False,
            "review_rounds": 0,
        }
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test.py").write_text("def test_ok(): assert True\n")

        caller, caller_calls = self._make_fake_caller([
            ("FILE: a.py\n```python\nx\n```", {"status": 200}),
            ("FILE: a.py\n```python\nx\n```\nFILE: b.py\n```python\ny\n```", {"status": 200}),
        ])
        reviewer, _ = self._make_fake_reviewer([])
        parse_files, _ = self._make_fake_parse_files([
            ({"a.py": "x"}, []),
            ({"a.py": "x", "b.py": "y"}, []),
        ])
        check_path = self._make_fake_check_path({"a.py": None, "b.py": None})

        monkeypatch.setattr(fix_loop, "run_pytest", lambda tests, root, **kw: (True, "pass"))

        with self._setup_mocks(monkeypatch, parse_files, check_path):
            result = fix_loop.run_job(job, tmp_path, caller=caller, reviewer=reviewer, status_dir=tmp_path / "_loop")

        assert result["state"] == "passed-no-review"
        assert len(caller_calls) == 2
        assert "missing" in caller_calls[1][1].lower()

    def test_extra_file_fails_round(self, tmp_path: Path, monkeypatch):
        job = {
            "name": "job4",
            "spec": "spec.md",
            "files": ["a.py"],
            "tests": ["tests/test.py"],
            "max_rounds": 2,
            "review": False,
            "review_rounds": 0,
        }
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test.py").write_text("def test_ok(): assert True\n")

        caller, caller_calls = self._make_fake_caller([
            ("FILE: a.py\n```python\nx\n```\nFILE: extra.py\n```python\ny\n```", {"status": 200}),
            ("FILE: a.py\n```python\nx\n```", {"status": 200}),
        ])
        reviewer, _ = self._make_fake_reviewer([])
        parse_files, _ = self._make_fake_parse_files([
            ({"a.py": "x", "extra.py": "y"}, []),
            ({"a.py": "x"}, []),
        ])
        check_path = self._make_fake_check_path({"a.py": None, "extra.py": None})

        monkeypatch.setattr(fix_loop, "run_pytest", lambda tests, root, **kw: (True, "pass"))

        with self._setup_mocks(monkeypatch, parse_files, check_path):
            result = fix_loop.run_job(job, tmp_path, caller=caller, reviewer=reviewer, status_dir=tmp_path / "_loop")

        assert result["state"] == "passed-no-review"
        assert len(caller_calls) == 2
        assert "extra" in caller_calls[1][1].lower()

    def test_coder_failure_status_500(self, tmp_path: Path, monkeypatch):
        job = {
            "name": "job5",
            "spec": "spec.md",
            "files": ["a.py"],
            "tests": ["tests/test.py"],
            "max_rounds": 2,
            "review": False,
            "review_rounds": 0,
        }
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test.py").write_text("def test_ok(): assert True\n")

        caller, caller_calls = self._make_fake_caller([
            ("", {"status": 500, "error": "server error"}),
            ("FILE: a.py\n```python\nok\n```", {"status": 200}),
        ])
        reviewer, _ = self._make_fake_reviewer([])
        parse_files, _ = self._make_fake_parse_files([({"a.py": "ok"}, [])])
        check_path = self._make_fake_check_path({"a.py": None})

        monkeypatch.setattr(fix_loop, "run_pytest", lambda tests, root, **kw: (True, "pass"))

        with self._setup_mocks(monkeypatch, parse_files, check_path):
            result = fix_loop.run_job(job, tmp_path, caller=caller, reviewer=reviewer, status_dir=tmp_path / "_loop")

        assert result["state"] == "passed-no-review"
        assert len(caller_calls) == 2

    def test_coder_empty_reply(self, tmp_path: Path, monkeypatch):
        job = {
            "name": "job6",
            "spec": "spec.md",
            "files": ["a.py"],
            "tests": ["tests/test.py"],
            "max_rounds": 2,
            "review": False,
            "review_rounds": 0,
        }
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test.py").write_text("def test_ok(): assert True\n")

        caller, caller_calls = self._make_fake_caller([
            ("", {"status": 200}),
            ("FILE: a.py\n```python\nok\n```", {"status": 200}),
        ])
        reviewer, _ = self._make_fake_reviewer([])
        parse_files, _ = self._make_fake_parse_files([({"a.py": "ok"}, [])])
        check_path = self._make_fake_check_path({"a.py": None})

        monkeypatch.setattr(fix_loop, "run_pytest", lambda tests, root, **kw: (True, "pass"))

        with self._setup_mocks(monkeypatch, parse_files, check_path):
            result = fix_loop.run_job(job, tmp_path, caller=caller, reviewer=reviewer, status_dir=tmp_path / "_loop")

        assert result["state"] == "passed-no-review"
        assert len(caller_calls) == 2

    def test_coder_exception(self, tmp_path: Path, monkeypatch):
        job = {
            "name": "job7",
            "spec": "spec.md",
            "files": ["a.py"],
            "tests": ["tests/test.py"],
            "max_rounds": 2,
            "review": False,
            "review_rounds": 0,
        }
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test.py").write_text("def test_ok(): assert True\n")

        def caller(system, user):
            raise RuntimeError("boom")
        reviewer, _ = self._make_fake_reviewer([])
        parse_files, _ = self._make_fake_parse_files([({"a.py": "ok"}, [])])
        check_path = self._make_fake_check_path({"a.py": None})

        monkeypatch.setattr(fix_loop, "run_pytest", lambda tests, root, **kw: (True, "pass"))

        with self._setup_mocks(monkeypatch, parse_files, check_path):
            result = fix_loop.run_job(job, tmp_path, caller=caller, reviewer=reviewer, status_dir=tmp_path / "_loop")

        assert result["state"] == "passed-no-review"

    def test_max_rounds_exceeded_restores_original(self, tmp_path: Path, monkeypatch):
        job = {
            "name": "job8",
            "spec": "spec.md",
            "files": ["a.py", "new.py"],
            "tests": ["tests/test.py"],
            "max_rounds": 1,
            "review": False,
            "review_rounds": 0,
        }
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "a.py").write_text("ORIGINAL")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test.py").write_text("def test_ok(): assert False\n")

        caller, _ = self._make_fake_caller([
            ("FILE: a.py\n```python\nbad\n```\nFILE: new.py\n```python\nnew\n```", {"status": 200}),
        ])
        reviewer, _ = self._make_fake_reviewer([])
        parse_files, _ = self._make_fake_parse_files([({"a.py": "bad", "new.py": "new"}, [])])
        check_path = self._make_fake_check_path({"a.py": None, "new.py": None})

        monkeypatch.setattr(fix_loop, "run_pytest", lambda tests, root, **kw: (False, "fail"))

        with self._setup_mocks(monkeypatch, parse_files, check_path):
            result = fix_loop.run_job(job, tmp_path, caller=caller, reviewer=reviewer, status_dir=tmp_path / "_loop")

        assert result["state"] == "failed"
        assert (tmp_path / "a.py").read_text() == "ORIGINAL"
        assert not (tmp_path / "new.py").exists()

    def test_review_ready_first(self, tmp_path: Path, monkeypatch):
        job = {
            "name": "job9",
            "spec": "spec.md",
            "files": ["a.py"],
            "tests": ["tests/test.py"],
            "max_rounds": 2,
            "review": True,
            "review_rounds": 2,
        }
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test.py").write_text("def test_ok(): assert True\n")

        caller, caller_calls = self._make_fake_caller([
            ("FILE: a.py\n```python\nok\n```", {"status": 200}),
        ])
        reviewer, reviewer_calls = self._make_fake_reviewer(["READY"])
        parse_files, _ = self._make_fake_parse_files([({"a.py": "ok"}, [])])
        check_path = self._make_fake_check_path({"a.py": None})

        monkeypatch.setattr(fix_loop, "run_pytest", lambda tests, root, **kw: (True, "pass"))

        with self._setup_mocks(monkeypatch, parse_files, check_path):
            result = fix_loop.run_job(job, tmp_path, caller=caller, reviewer=reviewer, status_dir=tmp_path / "_loop")

        assert result["state"] == "passed"
        assert result["review_verdict"] == "READY"
        assert len(reviewer_calls) == 1

    def test_review_fix_first_then_ready(self, tmp_path: Path, monkeypatch):
        job = {
            "name": "job10",
            "spec": "spec.md",
            "files": ["a.py"],
            "tests": ["tests/test.py"],
            "max_rounds": 3,
            "review": True,
            "review_rounds": 2,
        }
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test.py").write_text("def test_ok(): assert True\n")

        caller, caller_calls = self._make_fake_caller([
            ("FILE: a.py\n```python\nv1\n```", {"status": 200}),
            ("FILE: a.py\n```python\nv2\n```", {"status": 200}),
        ])
        reviewer, reviewer_calls = self._make_fake_reviewer(["FIX FIRST", "READY"])
        parse_files, _ = self._make_fake_parse_files([
            ({"a.py": "v1"}, []),
            ({"a.py": "v2"}, []),
        ])
        check_path = self._make_fake_check_path({"a.py": None})

        monkeypatch.setattr(fix_loop, "run_pytest", lambda tests, root, **kw: (True, "pass"))

        with self._setup_mocks(monkeypatch, parse_files, check_path):
            result = fix_loop.run_job(job, tmp_path, caller=caller, reviewer=reviewer, status_dir=tmp_path / "_loop")

        assert result["state"] == "passed"
        assert result["review_verdict"] == "READY"
        assert len(caller_calls) == 2
        assert len(reviewer_calls) == 2

    def test_review_none_returns_passed_no_review(self, tmp_path: Path, monkeypatch):
        job = {
            "name": "job11",
            "spec": "spec.md",
            "files": ["a.py"],
            "tests": ["tests/test.py"],
            "max_rounds": 2,
            "review": True,
            "review_rounds": 2,
        }
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test.py").write_text("def test_ok(): assert True\n")

        caller, caller_calls = self._make_fake_caller([
            ("FILE: a.py\n```python\nok\n```", {"status": 200}),
        ])
        reviewer, reviewer_calls = self._make_fake_reviewer(["NONE"])
        parse_files, _ = self._make_fake_parse_files([({"a.py": "ok"}, [])])
        check_path = self._make_fake_check_path({"a.py": None})

        monkeypatch.setattr(fix_loop, "run_pytest", lambda tests, root, **kw: (True, "pass"))

        with self._setup_mocks(monkeypatch, parse_files, check_path):
            result = fix_loop.run_job(job, tmp_path, caller=caller, reviewer=reviewer, status_dir=tmp_path / "_loop")

        assert result["state"] == "passed-no-review"
        assert result["review_verdict"] == "unavailable"
        assert len(reviewer_calls) == 1

    def test_review_rounds_exhausted(self, tmp_path: Path, monkeypatch):
        job = {
            "name": "job12",
            "spec": "spec.md",
            "files": ["a.py"],
            "tests": ["tests/test.py"],
            "max_rounds": 2,
            "review": True,
            "review_rounds": 1,
        }
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test.py").write_text("def test_ok(): assert True\n")

        caller, caller_calls = self._make_fake_caller([
            ("FILE: a.py\n```python\nok\n```", {"status": 200}),
        ])
        reviewer, reviewer_calls = self._make_fake_reviewer(["FIX FIRST"])
        parse_files, _ = self._make_fake_parse_files([({"a.py": "ok"}, [])])
        check_path = self._make_fake_check_path({"a.py": None})

        monkeypatch.setattr(fix_loop, "run_pytest", lambda tests, root, **kw: (True, "pass"))

        with self._setup_mocks(monkeypatch, parse_files, check_path):
            result = fix_loop.run_job(job, tmp_path, caller=caller, reviewer=reviewer, status_dir=tmp_path / "_loop")

        assert result["state"] == "passed-no-review"
        assert result["review_verdict"] == "unavailable"
        assert len(reviewer_calls) == 1

    def test_status_json_and_round_files_written(self, tmp_path: Path, monkeypatch):
        job = {
            "name": "job13",
            "spec": "spec.md",
            "files": ["a.py"],
            "tests": ["tests/test.py"],
            "max_rounds": 2,
            "review": False,
            "review_rounds": 0,
        }
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test.py").write_text("def test_ok(): assert True\n")

        caller, _ = self._make_fake_caller([
            ("FILE: a.py\n```python\nok\n```", {"status": 200}),
        ])
        reviewer, _ = self._make_fake_reviewer([])
        parse_files, _ = self._make_fake_parse_files([({"a.py": "ok"}, [])])
        check_path = self._make_fake_check_path({"a.py": None})

        monkeypatch.setattr(fix_loop, "run_pytest", lambda tests, root, **kw: (True, "pass"))

        status_dir = tmp_path / "_loop"
        with self._setup_mocks(monkeypatch, parse_files, check_path):
            fix_loop.run_job(job, tmp_path, caller=caller, reviewer=reviewer, status_dir=status_dir)

        status_file = status_dir / "job13" / "status.json"
        assert status_file.exists()
        status = json.loads(status_file.read_text())
        assert status["name"] == "job13"
        assert status["state"] == "passed-no-review"
        assert len(status["rounds"]) == 1

        round_file = status_dir / "job13" / "round_0.txt"
        assert round_file.exists()
        assert "ok" in round_file.read_text()

    def test_no_files_outside_expected_and_status_dir(self, tmp_path: Path, monkeypatch):
        job = {
            "name": "job14",
            "spec": "spec.md",
            "files": ["a.py"],
            "tests": ["tests/test.py"],
            "max_rounds": 1,
            "review": False,
            "review_rounds": 0,
        }
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test.py").write_text("def test_ok(): assert True\n")

        caller, _ = self._make_fake_caller([
            ("FILE: a.py\n```python\nok\n```\nFILE: stray.py\n```python\nbad\n```", {"status": 200}),
        ])
        reviewer, _ = self._make_fake_reviewer([])
        parse_files, _ = self._make_fake_parse_files([({"a.py": "ok", "stray.py": "bad"}, [])])
        check_path = self._make_fake_check_path({"a.py": None, "stray.py": None})

        monkeypatch.setattr(fix_loop, "run_pytest", lambda tests, root, **kw: (True, "pass"))

        status_dir = tmp_path / "_loop"
        with self._setup_mocks(monkeypatch, parse_files, check_path):
            fix_loop.run_job(job, tmp_path, caller=caller, reviewer=reviewer, status_dir=status_dir)

        assert not (tmp_path / "stray.py").exists()
        assert (status_dir / "job14").exists()

    def test_scrub_keys_applied(self, tmp_path: Path, monkeypatch):
        job = {
            "name": "job15",
            "spec": "spec.md",
            "files": ["a.py"],
            "tests": ["tests/test.py"],
            "max_rounds": 1,
            "review": False,
            "review_rounds": 0,
        }
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test.py").write_text("def test_ok(): assert True\n")

        secret = "nvapi-SECRET123"
        caller, _ = self._make_fake_caller([
            (f"FILE: a.py\n```python\n{secret}\n```", {"status": 200}),
        ])
        reviewer, _ = self._make_fake_reviewer([])
        parse_files, _ = self._make_fake_parse_files([({"a.py": secret}, [])])
        check_path = self._make_fake_check_path({"a.py": None})

        monkeypatch.setattr(fix_loop, "run_pytest", lambda tests, root, **kw: (True, "pass"))

        status_dir = tmp_path / "_loop"
        with self._setup_mocks(monkeypatch, parse_files, check_path):
            fix_loop.run_job(job, tmp_path, caller=caller, reviewer=reviewer, status_dir=status_dir, scrub_keys=[secret])

        round_file = status_dir / "job15" / "round_0.txt"
        content = round_file.read_text()
        assert secret not in content
        assert "[REDACTED]" in content


class TestMain:
    def test_dry_run(self, tmp_path: Path, monkeypatch, capsys):
        job_data = {
            "name": "dry",
            "spec": "spec.md",
            "files": ["a.py"],
            "tests": ["tests/test.py"],
        }
        job_file = tmp_path / "job.yaml"
        job_file.write_text(yaml.dump(job_data))
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test.py").write_text("def test_ok(): assert True\n")

        rc = fix_loop.main(["--job", str(job_file.relative_to(tmp_path)), "--root", str(tmp_path), "--dry-run"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "dry-run: prompt size" in out

    def test_invalid_job_returns_2(self, tmp_path: Path, capsys):
        job_data = {"name": "bad!", "spec": "spec.md", "files": ["a.py"], "tests": ["tests/test.py"]}
        job_file = tmp_path / "job.yaml"
        job_file.write_text(yaml.dump(job_data))
        (tmp_path / "spec.md").write_text("spec")

        rc = fix_loop.main(["--job", str(job_file.relative_to(tmp_path)), "--root", str(tmp_path)])
        assert rc == 2

    def test_main_pass_returns_0(self, tmp_path: Path, monkeypatch):
        job_data = {"name": "ok", "spec": "spec.md", "files": ["a.py"], "tests": ["tests/test.py"]}
        job_file = tmp_path / "job.yaml"
        job_file.write_text(yaml.dump(job_data))
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test.py").write_text("def test_ok(): assert True\n")

        monkeypatch.setattr(fix_loop, "run_job", lambda *a, **kw: {"state": "passed"})
        rc = fix_loop.main(["--job", str(job_file.relative_to(tmp_path)), "--root", str(tmp_path)])
        assert rc == 0

    def test_main_fail_returns_1(self, tmp_path: Path, monkeypatch):
        job_data = {"name": "fail", "spec": "spec.md", "files": ["a.py"], "tests": ["tests/test.py"]}
        job_file = tmp_path / "job.yaml"
        job_file.write_text(yaml.dump(job_data))
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test.py").write_text("def test_ok(): assert True\n")

        monkeypatch.setattr(fix_loop, "run_job", lambda *a, **kw: {"state": "failed"})
        rc = fix_loop.main(["--job", str(job_file.relative_to(tmp_path)), "--root", str(tmp_path)])
        assert rc == 1


class TestNoForbiddenContent:
    def test_no_nvapi_literal(self):
        source = Path("scripts/source/fix_loop.py").read_text()
        assert "nvapi-" not in source

    def test_no_kimi_adapter_import(self):
        source = Path("scripts/source/fix_loop.py").read_text()
        assert "kimi_adapter" not in source

```

## NOTE
7 tests fail (output above; all the others pass). For each, decide from the SPEC whether the module or the test is wrong and fix THAT side (the spec: a missing/extra/refused file block = a failed round with the reason in the next prompt and NO stray file written; a coder exception or empty reply = a failed round, loop continues; review_rounds is a bound on reviews). Return BOTH complete FILE blocks. Never write any word related to 3D animation software.
