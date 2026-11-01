from __future__ import annotations

import json
import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Optional

# Import the existing fix_loop module (assumed to be in the same directory)
import fix_loop

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
                ran.append(job_name)
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
