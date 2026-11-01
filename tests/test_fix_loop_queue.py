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
