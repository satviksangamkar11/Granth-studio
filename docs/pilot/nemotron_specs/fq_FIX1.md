# FIX CALL: return BOTH files in full: `scripts/source/fix_loop_queue.py` and `tests/test_fix_loop_queue.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```

=================================== ERRORS ====================================
________________ ERROR collecting tests/test_fix_loop_queue.py ________________
ImportError while importing test module 'D:\aai work\granthstudio\tests\test_fix_loop_queue.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Users\Satvik\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\test_fix_loop_queue.py:14: in <module>
    import fix_loop_queue as flq
scripts\source\fix_loop_queue.py:13: in <module>
    from . import fix_loop
E   ImportError: attempted relative import with no known parent package
=========================== short test summary info ===========================
ERROR tests/test_fix_loop_queue.py
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.25s

```

## SPEC
# SPEC: NEW `scripts/source/fix_loop_queue.py` + NEW `tests/test_fix_loop_queue.py`. Return exactly these TWO files in full; do not output or change any other file.
Purpose: run every pending loop job in a folder, one after another, and keep a human-readable summary, so a 30-minute scheduler (or the owner) can just start it and read `_loop/SUMMARY.md`. Standard library only; `from __future__ import annotations`; nothing at import time except imports and definitions; no key or secret is handled; never write any word related to 3D animation software.
## Existing code (load by importlib BY PATH, do not modify): `scripts/source/fix_loop.py` with `load_job(path) -> dict` (ValueError on invalid), `run_job(job, root, caller=None, reviewer=None, pytest_runner=None, status_dir=None, scrub_keys=[]) -> dict` (final status dict with `state` in passed, passed-no-review, escalate, failed). Status files: `<status_dir>/<job name>/status.json` with `state` (`running` while in progress), `round`, `tests_passed`, `review_verdict`, `updated`.
## API
- `FINAL_STATES = ("passed", "passed-no-review", "escalate", "failed")`.
- `pending_jobs(jobs_dir: Path, status_dir: Path) -> list[Path]`: the `*.json` files of `jobs_dir` sorted by name whose job `name` (read from the file; an unreadable file counts as pending-invalid and is reported by run_queue) has NO `status.json` with a final state.
- `read_status(status_dir: Path) -> list[dict]`: every `<status_dir>/*/status.json` that parses as an object, sorted by job name; unreadable ones are skipped.
- `write_summary(status_dir: Path, entries: list[dict], extra_lines: list[str] | None = None, now: str | None = None) -> Path`: writes `<status_dir>/SUMMARY.md`: a title with the time, a table `| job | state | round | tests | reviewers | updated |`, a line `ESCALATE: <names>` listing jobs in state escalate with the path `_loop/<name>/ESCALATE.md`, a line `RUNNING: <names>` for state running, then `extra_lines`. Returns the path.
- `run_queue(jobs_dir, root, status_dir=None, runner=None, max_jobs: int | None = None, now: str | None = None) -> dict`: `runner(job: dict, root: Path) -> dict` default = `fix_loop.run_job` with the default callers. A lock file `<status_dir>/queue.lock` (created atomically; content = start time) prevents overlapping runs: if it exists and is younger than 3 hours return `{"state": "locked", ...}` without running anything; an older lock is replaced; the lock is ALWAYS removed at the end (also after an exception). For each pending job: `load_job`; an invalid job is recorded in `invalid` with the reason and skipped; a runner exception is recorded as the job failed with the exception class name and the loop continues with the next job (an `escalate` or `failed` job never stops the queue). Stops after `max_jobs` jobs if given. Always rewrites SUMMARY.md at the end (and once at the start). Returns `{"state": "done"|"locked", "ran": [names], "invalid": [{"file","reason"}], "summary": path}`.
- `main(argv=None) -> int`: `--jobs-dir` (default `_loop/jobs`), `--root` (default repo root `Path(__file__).resolve().parents[2]`), `--max-jobs`; prints one line per job `<name>: <state>` and `summary: <path>`; returns 0 when nothing escalated or failed, 3 when any job escalated, 1 when any failed, 4 when locked. 
## Tests (`tests/test_fix_loop_queue.py`; offline, fake runner, tmp_path)
pending_jobs (no status, final status, running status, invalid json); read_status skips corrupt files; write_summary content (table row, ESCALATE and RUNNING lines); run_queue: runs pending jobs in name order and skips finished ones, an invalid job is reported and skipped, a runner that raises is recorded failed and the next job still runs, an escalate job does not stop the queue, max_jobs, the lock (a fresh lock -> locked and nothing run; a stale lock (set the mtime 4 hours back with os.utime) is replaced; the lock is removed after success and after a runner exception); main return codes 0/3/1/4 and output lines (capsys, monkeypatched run_queue where needed).
Reply with only the two FILE blocks:
FILE: scripts/source/fix_loop_queue.py
FILE: tests/test_fix_loop_queue.py


## CURRENT MODULE scripts/source/fix_loop_queue.py
```python
from __future__ import annotations

import json
import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Optional

# Import the existing fix_loop module (assumed to be in the same package)
from . import fix_loop

FINAL_STATES = ("passed", "passed-no-review", "escalate", "failed")


def _now_iso(now: Optional[str] = None) -> str:
    """Return current time in ISO format, or the provided now string."""
    if now is not None:
        return now
    return datetime.now(timezone.utc).isoformat()


def _now_timestamp(now: Optional[str] = None) -> float:
    """Return current time as timestamp, or parse the provided now string."""
    if now is not None:
        return datetime.fromisoformat(now).timestamp()
    return time.time()


def pending_jobs(jobs_dir: Path, status_dir: Path) -> list[Path]:
    """Return *.json files in jobs_dir sorted by name that have no final status."""
    job_files = sorted(jobs_dir.glob("*.json"))
    pending = []
    for job_file in job_files:
        job_name = None
        try:
            with job_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
            job_name = data.get("name")
        except Exception:
            # Unreadable or invalid JSON -> treat as pending (will be reported invalid later)
            pending.append(job_file)
            continue

        if job_name is None:
            # No name field -> treat as pending (invalid)
            pending.append(job_file)
            continue

        status_file = status_dir / job_name / "status.json"
        if status_file.exists():
            try:
                with status_file.open("r", encoding="utf-8") as f:
                    status = json.load(f)
                state = status.get("state")
                if state in FINAL_STATES:
                    continue  # has final state, not pending
            except Exception:
                # Corrupt status file -> treat as pending
                pass
        pending.append(job_file)
    return pending


def read_status(status_dir: Path) -> list[dict]:
    """Read all status.json files under status_dir, return list of dicts sorted by job name."""
    entries = []
    for job_dir in sorted(status_dir.iterdir()):
        if not job_dir.is_dir():
            continue
        status_file = job_dir / "status.json"
        if not status_file.exists():
            continue
        try:
            with status_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                entries.append(data)
        except Exception:
            # Skip unreadable or non-object files
            continue
    # Sort by job name (assuming each entry has a 'name' field)
    entries.sort(key=lambda e: e.get("name", ""))
    return entries


def write_summary(
    status_dir: Path,
    entries: list[dict],
    extra_lines: Optional[list[str]] = None,
    now: Optional[str] = None,
) -> Path:
    """Write SUMMARY.md in status_dir and return its path."""
    summary_path = status_dir / "SUMMARY.md"
    timestamp = _now_iso(now)
    lines = [f"# Loop Queue Summary ({timestamp})", ""]
    # Table header
    lines.append("| job | state | round | tests | reviewers | updated |")
    lines.append("|-----|-------|-------|-------|-----------|---------|")
    for entry in entries:
        job = entry.get("name", "")
        state = entry.get("state", "")
        round_val = entry.get("round", "")
        tests = entry.get("tests_passed", "")
        reviewers = entry.get("review_verdict", "")
        updated = entry.get("updated", "")
        lines.append(f"| {job} | {state} | {round_val} | {tests} | {reviewers} | {updated} |")
    lines.append("")

    # ESCALATE line
    escalate_jobs = [e.get("name", "") for e in entries if e.get("state") == "escalate"]
    if escalate_jobs:
        lines.append(f"ESCALATE: {', '.join(escalate_jobs)}")
    else:
        lines.append("ESCALATE:")

    # RUNNING line
    running_jobs = [e.get("name", "") for e in entries if e.get("state") == "running"]
    if running_jobs:
        lines.append(f"RUNNING: {', '.join(running_jobs)}")
    else:
        lines.append("RUNNING:")

    if extra_lines:
        lines.extend(extra_lines)

    summary_path.write_text("\n".join(lines), encoding="utf-8")
    return summary_path


def run_queue(
    jobs_dir: Path,
    root: Path,
    status_dir: Optional[Path] = None,
    runner: Optional[callable] = None,
    max_jobs: Optional[int] = None,
    now: Optional[str] = None,
) -> dict:
    """Run pending loop jobs sequentially, maintaining a lock and summary."""
    if status_dir is None:
        status_dir = jobs_dir.parent / "status"
    status_dir.mkdir(parents=True, exist_ok=True)

    lock_path = status_dir / "queue.lock"
    start_time = _now_iso(now)
    start_ts = _now_timestamp(now)

    # Lock handling
    if lock_path.exists():
        lock_mtime = lock_path.stat().st_mtime
        if start_ts - lock_mtime < 3 * 3600:  # younger than 3 hours
            return {
                "state": "locked",
                "ran": [],
                "invalid": [],
                "summary": None,
            }
        # Stale lock -> remove
        lock_path.unlink(missing_ok=True)

    # Create lock atomically
    try:
        with lock_path.open("x", encoding="utf-8") as f:
            f.write(start_time)
    except FileExistsError:
        # Race condition: another process created it after our check
        return {
            "state": "locked",
            "ran": [],
            "invalid": [],
            "summary": None,
        }

    # Default runner
    if runner is None:
        runner = fix_loop.run_job

    # Initial summary
    initial_entries = read_status(status_dir)
    write_summary(status_dir, initial_entries, now=now)

    ran = []
    invalid = []

    try:
        pending = pending_jobs(jobs_dir, status_dir)
        for job_file in pending:
            if max_jobs is not None and len(ran) >= max_jobs:
                break

            # Load job
            try:
                job = fix_loop.load_job(job_file)
            except Exception as e:
                invalid.append({"file": job_file.name, "reason": f"{type(e).__name__}: {e}"})
                continue

            job_name = job.get("name", job_file.stem)
            try:
                # Run the job (runner writes status file)
                runner(job, root)
                ran.append(job_name)
            except Exception as e:
                # Record as failed with exception class name
                # The runner is expected to have written a status file with state 'failed'?
                # But spec says: "a runner exception is recorded as the job failed with the exception class name"
                # We'll just record the name and continue; the status file may not be written.
                # However, the summary will be rewritten later from read_status, which may not have this job.
                # To ensure the failed job appears in summary, we could write a minimal status file.
                # But the spec says the runner (fix_loop.run_job) writes the status file.
                # If the runner raises, it might not have written. We'll assume the runner writes status before raising?
                # The spec: "a runner exception is recorded as the job failed with the exception class name and the loop continues"
                # We'll just note the failure in 'ran'? Actually 'ran' is for successfully run jobs.
                # The spec says 'ran' is list of names. It doesn't say failed jobs are in 'ran'.
                # But the test expects that a runner exception is recorded as failed and the next job runs.
                # We'll add the job name to ran? The test says: "a runner that raises is recorded failed and the next job still runs"
                # And the run_queue returns 'ran' list of names. The test likely checks that the job name appears in ran.
                # We'll add to ran even if it fails, because we attempted to run it.
                ran.append(job_name)
                # The exception is not stored in the return dict, but the status file should reflect failure.
                # If the runner didn't write a status file, we could write one here, but the spec doesn't require it.
                # We'll rely on the runner to have written a status file (fix_loop.run_job does that).
                continue

        # Final summary
        final_entries = read_status(status_dir)
        summary_path = write_summary(status_dir, final_entries, now=now)
    finally:
        # Always remove lock
        lock_path.unlink(missing_ok=True)

    return {
        "state": "done",
        "ran": ran,
        "invalid": invalid,
        "summary": summary_path,
    }


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run pending loop jobs.")
    parser.add_argument("--jobs-dir", type=Path, default=Path("_loop/jobs"))
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--max-jobs", type=int, default=None)
    args = parser.parse_args(argv)

    result = run_queue(args.jobs_dir, args.root, max_jobs=args.max_jobs)

    if result["state"] == "locked":
        print("locked")
        return 4

    # Print one line per job in ran with its state
    # We need to read the status for each ran job
    status_dir = args.jobs_dir.parent / "status"
    entries = read_status(status_dir)
    state_by_name = {e.get("name"): e.get("state", "") for e in entries}

    for name in result["ran"]:
        state = state_by_name.get(name, "unknown")
        print(f"{name}: {state}")

    print(f"summary: {result['summary']}")

    # Determine exit code based on any job in status_dir (not just ran)
    any_escalate = any(e.get("state") == "escalate" for e in entries)
    any_failed = any(e.get("state") == "failed" for e in entries)

    if any_escalate:
        return 3
    if any_failed:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

```

## CURRENT TESTS tests/test_fix_loop_queue.py
```python
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Import the module under test
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "source"))
import fix_loop_queue as flq


@pytest.fixture
def tmp_jobs_dir(tmp_path: Path) -> Path:
    jobs = tmp_path / "jobs"
    jobs.mkdir()
    return jobs


@pytest.fixture
def tmp_status_dir(tmp_path: Path) -> Path:
    status = tmp_path / "status"
    status.mkdir()
    return status


@pytest.fixture
def tmp_root(tmp_path: Path) -> Path:
    return tmp_path / "root"


def write_job(jobs_dir: Path, name: str, content: dict | None = None) -> Path:
    if content is None:
        content = {"name": name, "steps": []}
    else:
        content.setdefault("name", name)
    path = jobs_dir / f"{name}.json"
    path.write_text(json.dumps(content), encoding="utf-8")
    return path


def write_status(status_dir: Path, name: str, state: str, **extra) -> Path:
    job_dir = status_dir / name
    job_dir.mkdir(parents=True, exist_ok=True)
    status_file = job_dir / "status.json"
    data = {"name": name, "state": state, "round": 1, "tests_passed": True, "review_verdict": "approved", "updated": "2024-01-01T00:00:00Z"}
    data.update(extra)
    status_file.write_text(json.dumps(data), encoding="utf-8")
    return status_file


class TestPendingJobs:
    def test_no_status(self, tmp_jobs_dir, tmp_status_dir):
        write_job(tmp_jobs_dir, "job_a")
        write_job(tmp_jobs_dir, "job_b")
        pending = flq.pending_jobs(tmp_jobs_dir, tmp_status_dir)
        assert [p.name for p in pending] == ["job_a.json", "job_b.json"]

    def test_final_status(self, tmp_jobs_dir, tmp_status_dir):
        write_job(tmp_jobs_dir, "job_a")
        write_job(tmp_jobs_dir, "job_b")
        write_status(tmp_status_dir, "job_a", "passed")
        pending = flq.pending_jobs(tmp_jobs_dir, tmp_status_dir)
        assert [p.name for p in pending] == ["job_b.json"]

    def test_running_status(self, tmp_jobs_dir, tmp_status_dir):
        write_job(tmp_jobs_dir, "job_a")
        write_status(tmp_status_dir, "job_a", "running")
        pending = flq.pending_jobs(tmp_jobs_dir, tmp_status_dir)
        assert [p.name for p in pending] == ["job_a.json"]

    def test_invalid_json(self, tmp_jobs_dir, tmp_status_dir):
        write_job(tmp_jobs_dir, "job_a")
        bad = tmp_jobs_dir / "job_b.json"
        bad.write_text("{not json}", encoding="utf-8")
        pending = flq.pending_jobs(tmp_jobs_dir, tmp_status_dir)
        names = [p.name for p in pending]
        assert "job_a.json" in names
        assert "job_b.json" in names


class TestReadStatus:
    def test_reads_valid(self, tmp_status_dir):
        write_status(tmp_status_dir, "job_a", "passed")
        write_status(tmp_status_dir, "job_b", "failed")
        entries = flq.read_status(tmp_status_dir)
        assert len(entries) == 2
        assert entries[0]["name"] == "job_a"
        assert entries[1]["name"] == "job_b"

    def test_skips_corrupt(self, tmp_status_dir):
        write_status(tmp_status_dir, "job_a", "passed")
        bad_dir = tmp_status_dir / "job_b"
        bad_dir.mkdir()
        (bad_dir / "status.json").write_text("not json", encoding="utf-8")
        entries = flq.read_status(tmp_status_dir)
        assert len(entries) == 1
        assert entries[0]["name"] == "job_a"

    def test_sorts_by_name(self, tmp_status_dir):
        write_status(tmp_status_dir, "job_c", "passed")
        write_status(tmp_status_dir, "job_a", "passed")
        write_status(tmp_status_dir, "job_b", "passed")
        entries = flq.read_status(tmp_status_dir)
        assert [e["name"] for e in entries] == ["job_a", "job_b", "job_c"]


class TestWriteSummary:
    def test_content(self, tmp_status_dir):
        entries = [
            {"name": "job_a", "state": "passed", "round": 1, "tests_passed": True, "review_verdict": "approved", "updated": "2024-01-01T00:00:00Z"},
            {"name": "job_b", "state": "escalate", "round": 2, "tests_passed": False, "review_verdict": "rejected", "updated": "2024-01-02T00:00:00Z"},
            {"name": "job_c", "state": "running", "round": 1, "tests_passed": True, "review_verdict": "", "updated": "2024-01-03T00:00:00Z"},
        ]
        extra = ["Extra line 1", "Extra line 2"]
        summary_path = flq.write_summary(tmp_status_dir, entries, extra_lines=extra, now="2024-01-01T12:00:00+00:00")
        content = summary_path.read_text(encoding="utf-8")
        assert "# Loop Queue Summary (2024-01-01T12:00:00+00:00)" in content
        assert "| job_a | passed | 1 | True | approved | 2024-01-01T00:00:00Z |" in content
        assert "| job_b | escalate | 2 | False | rejected | 2024-01-02T00:00:00Z |" in content
        assert "| job_c | running | 1 | True |  | 2024-01-03T00:00:00Z |" in content
        assert "ESCALATE: job_b" in content
        assert "RUNNING: job_c" in content
        assert "Extra line 1" in content
        assert "Extra line 2" in content


class TestRunQueue:
    def test_runs_pending_in_order(self, tmp_jobs_dir, tmp_status_dir, tmp_root):
        write_job(tmp_jobs_dir, "job_a")
        write_job(tmp_jobs_dir, "job_b")
        write_job(tmp_jobs_dir, "job_c")

        mock_runner = MagicMock(side_effect=[
            {"name": "job_a", "state": "passed"},
            {"name": "job_b", "state": "passed"},
            {"name": "job_c", "state": "passed"},
        ])

        result = flq.run_queue(tmp_jobs_dir, tmp_root, status_dir=tmp_status_dir, runner=mock_runner, now="2024-01-01T00:00:00Z")
        assert result["state"] == "done"
        assert result["ran"] == ["job_a", "job_b", "job_c"]
        assert mock_runner.call_count == 3

    def test_skips_finished(self, tmp_jobs_dir, tmp_status_dir, tmp_root):
        write_job(tmp_jobs_dir, "job_a")
        write_job(tmp_jobs_dir, "job_b")
        write_status(tmp_status_dir, "job_a", "passed")

        mock_runner = MagicMock(return_value={"name": "job_b", "state": "passed"})
        result = flq.run_queue(tmp_jobs_dir, tmp_root, status_dir=tmp_status_dir, runner=mock_runner)
        assert result["ran"] == ["job_b"]
        assert mock_runner.call_count == 1

    def test_invalid_job_reported_and_skipped(self, tmp_jobs_dir, tmp_status_dir, tmp_root):
        write_job(tmp_jobs_dir, "job_a")
        bad = tmp_jobs_dir / "job_b.json"
        bad.write_text("{invalid", encoding="utf-8")

        mock_runner = MagicMock(return_value={"name": "job_a", "state": "passed"})
        result = flq.run_queue(tmp_jobs_dir, tmp_root, status_dir=tmp_status_dir, runner=mock_runner)
        assert result["ran"] == ["job_a"]
        assert len(result["invalid"]) == 1
        assert result["invalid"][0]["file"] == "job_b.json"
        assert "JSONDecodeError" in result["invalid"][0]["reason"]

    def test_runner_exception_recorded_failed_continues(self, tmp_jobs_dir, tmp_status_dir, tmp_root):
        write_job(tmp_jobs_dir, "job_a")
        write_job(tmp_jobs_dir, "job_b")

        def runner(job, root):
            if job["name"] == "job_a":
                raise RuntimeError("boom")
            return {"name": "job_b", "state": "passed"}

        result = flq.run_queue(tmp_jobs_dir, tmp_root, status_dir=tmp_status_dir, runner=runner)
        assert result["ran"] == ["job_a", "job_b"]
        # The status for job_a should be failed (written by fix_loop.run_job? but we mocked runner)
        # Since we mocked runner, no status file written. But the test only checks that the queue continues.
        # The spec says "recorded as the job failed with the exception class name".
        # Our implementation adds to ran and continues. The test will check that ran includes both.

    def test_escalate_does_not_stop_queue(self, tmp_jobs_dir, tmp_status_dir, tmp_root):
        write_job(tmp_jobs_dir, "job_a")
        write_job(tmp_jobs_dir, "job_b")

        def runner(job, root):
            if job["name"] == "job_a":
                return {"name": "job_a", "state": "escalate"}
            return {"name": "job_b", "state": "passed"}

        result = flq.run_queue(tmp_jobs_dir, tmp_root, status_dir=tmp_status_dir, runner=runner)
        assert result["ran"] == ["job_a", "job_b"]

    def test_max_jobs(self, tmp_jobs_dir, tmp_status_dir, tmp_root):
        write_job(tmp_jobs_dir, "job_a")
        write_job(tmp_jobs_dir, "job_b")
        write_job(tmp_jobs_dir, "job_c")

        mock_runner = MagicMock(return_value={"state": "passed"})
        result = flq.run_queue(tmp_jobs_dir, tmp_root, status_dir=tmp_status_dir, runner=mock_runner, max_jobs=2)
        assert result["ran"] == ["job_a", "job_b"]
        assert mock_runner.call_count == 2

    def test_lock_fresh(self, tmp_jobs_dir, tmp_status_dir, tmp_root):
        write_job(tmp_jobs_dir, "job_a")
        lock = tmp_status_dir / "queue.lock"
        lock.write_text("2024-01-01T00:00:00Z", encoding="utf-8")
        # Make it fresh (mtime now)
        time.sleep(0.01)
        result = flq.run_queue(tmp_jobs_dir, tmp_root, status_dir=tmp_status_dir, now="2024-01-01T00:00:05Z")
        assert result["state"] == "locked"
        assert result["ran"] == []

    def test_lock_stale_replaced(self, tmp_jobs_dir, tmp_status_dir, tmp_root):
        write_job(tmp_jobs_dir, "job_a")
        lock = tmp_status_dir / "queue.lock"
        lock.write_text("2024-01-01T00:00:00Z", encoding="utf-8")
        # Set mtime to 4 hours ago
        old_time = time.time() - 4 * 3600
        os.utime(lock, (old_time, old_time))

        mock_runner = MagicMock(return_value={"name": "job_a", "state": "passed"})
        result = flq.run_queue(tmp_jobs_dir, tmp_root, status_dir=tmp_status_dir, runner=mock_runner, now="2024-01-01T04:00:00Z")
        assert result["state"] == "done"
        assert result["ran"] == ["job_a"]
        assert mock_runner.call_count == 1

    def test_lock_removed_after_success(self, tmp_jobs_dir, tmp_status_dir, tmp_root):
        write_job(tmp_jobs_dir, "job_a")
        mock_runner = MagicMock(return_value={"name": "job_a", "state": "passed"})
        flq.run_queue(tmp_jobs_dir, tmp_root, status_dir=tmp_status_dir, runner=mock_runner)
        assert not (tmp_status_dir / "queue.lock").exists()

    def test_lock_removed_after_runner_exception(self, tmp_jobs_dir, tmp_status_dir, tmp_root):
        write_job(tmp_jobs_dir, "job_a")
        def runner(job, root):
            raise RuntimeError("boom")
        flq.run_queue(tmp_jobs_dir, tmp_root, status_dir=tmp_status_dir, runner=runner)
        assert not (tmp_status_dir / "queue.lock").exists()


class TestMain:
    def test_return_code_0(self, tmp_jobs_dir, tmp_status_dir, tmp_root, capsys):
        write_job(tmp_jobs_dir, "job_a")
        write_status(tmp_status_dir, "job_a", "passed")
        with patch.object(flq, "run_queue", return_value={"state": "done", "ran": [], "invalid": [], "summary": tmp_status_dir / "SUMMARY.md"}):
            rc = flq.main(["--jobs-dir", str(tmp_jobs_dir), "--root", str(tmp_root)])
        assert rc == 0

    def test_return_code_3_escalate(self, tmp_jobs_dir, tmp_status_dir, tmp_root, capsys):
        write_job(tmp_jobs_dir, "job_a")
        write_status(tmp_status_dir, "job_a", "escalate")
        with patch.object(flq, "run_queue", return_value={"state": "done", "ran": [], "invalid": [], "summary": tmp_status_dir / "SUMMARY.md"}):
            rc = flq.main(["--jobs-dir", str(tmp_jobs_dir), "--root", str(tmp_root)])
        assert rc == 3

    def test_return_code_1_failed(self, tmp_jobs_dir, tmp_status_dir, tmp_root, capsys):
        write_job(tmp_jobs_dir, "job_a")
        write_status(tmp_status_dir, "job_a", "failed")
        with patch.object(flq, "run_queue", return_value={"state": "done", "ran": [], "invalid": [], "summary": tmp_status_dir / "SUMMARY.md"}):
            rc = flq.main(["--jobs-dir", str(tmp_jobs_dir), "--root", str(tmp_root)])
        assert rc == 1

    def test_return_code_4_locked(self, tmp_jobs_dir, tmp_status_dir, tmp_root, capsys):
        with patch.object(flq, "run_queue", return_value={"state": "locked", "ran": [], "invalid": [], "summary": None}):
            rc = flq.main(["--jobs-dir", str(tmp_jobs_dir), "--root", str(tmp_root)])
        assert rc == 4

    def test_output_lines(self, tmp_jobs_dir, tmp_status_dir, tmp_root, capsys):
        write_job(tmp_jobs_dir, "job_a")
        write_job(tmp_jobs_dir, "job_b")
        write_status(tmp_status_dir, "job_a", "passed")
        write_status(tmp_status_dir, "job_b", "escalate")

        def fake_run_queue(jobs_dir, root, status_dir=None, runner=None, max_jobs=None, now=None):
            return {"state": "done", "ran": ["job_a", "job_b"], "invalid": [], "summary": status_dir / "SUMMARY.md"}

        with patch.object(flq, "run_queue", side_effect=fake_run_queue):
            rc = flq.main(["--jobs-dir", str(tmp_jobs_dir), "--root", str(tmp_root)])
        out = capsys.readouterr().out
        assert "job_a: passed" in out
        assert "job_b: escalate" in out
        assert "summary:" in out

```

## NOTE
The test file fails at collection (see output). Fix it (module or test per the SPEC). Return BOTH complete FILE blocks. Never write any word related to 3D animation software.
