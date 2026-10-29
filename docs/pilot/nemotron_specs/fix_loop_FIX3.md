# TASK: return ONLY ONE FILE: scripts/source/fix_loop.py (complete). Reply with exactly one block `FILE: scripts/source/fix_loop.py` then the python fenced. Keep everything; fix ONE root cause that fails 17 tests: `build_prompt` (line ~141) and `run_job` read `job["reference"]` with square brackets, but per the spec the JOB fields `reference`, `max_rounds`, `review`, `review_rounds`, `review_files`, `review_prompt`, `coder_model`, `reviewer_model` are OPTIONAL with defaults (reference [], max_rounds 10, review true, review_rounds 4, review_files None, review_prompt None, coder_model nvidia/nemotron-3-ultra-550b-a55b, reviewer_model z-ai/glm-5.3-flash) and tests pass job dicts that did not go through load_job. Read EVERY optional job field with `.get(name, default)` everywhere in the module (build_prompt, run_job, main); `name`, `spec`, `files` and `tests` stay required. Change nothing else. Never write any word related to 3D animation software.
## CURRENT scripts/source/fix_loop.py
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
    if job["reference"]:
        user_parts.append("REFERENCE FILES:")
        for rel in job["reference"]:
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
