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
        assert job["max_rounds"] == 3
        assert job["review"] is True
        assert job["review_rounds"] == 4
        assert job["review_files"] is None
        assert job["review_prompt"] == "docs/pilot/REVIEW_PROMPT_STAGE1_FINAL.md"
        assert job["coder_model"] == "nvidia/nemotron-3-ultra-550b-a55b"
        assert job["reviewer_model"] == "z-ai/glm-5.3-flash"
        assert job["reviewers"] == ["glm"]

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

    def test_max_rounds_11(self, tmp_path: Path):
        job_data = {"name": "j", "spec": "spec.md", "files": ["a.py"], "tests": ["tests/a.py"], "max_rounds": 11}
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

    def test_invalid_reviewer_value(self, tmp_path: Path):
        job_data = {"name": "j", "spec": "spec.md", "files": ["a.py"], "tests": ["tests/a.py"], "reviewers": ["invalid"]}
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
        assert user.count("x") == 9002
        assert "Fix exactly the problems shown above" in user

    def test_round_with_review_report(self, tmp_path: Path):
        job = {"name": "j", "spec": "spec.md", "files": ["a.py"], "tests": ["tests/test.py"]}
        (tmp_path / "spec.md").write_text("SPEC")
        (tmp_path / "tests").mkdir()
        system, user = fix_loop.build_prompt(job, tmp_path, 1, review_report="REVIEW TEXT")
        assert "REVIEW REPORT" in user
        assert "REVIEW TEXT" in user
        assert "Fix exactly the problems in the review" in user

    def test_round_with_both_pytest_and_review(self, tmp_path: Path):
        job = {"name": "j", "spec": "spec.md", "files": ["a.py"], "tests": ["tests/test.py"]}
        (tmp_path / "spec.md").write_text("SPEC")
        (tmp_path / "tests").mkdir()
        long_output = "x" * 20000
        system, user = fix_loop.build_prompt(job, tmp_path, 2, pytest_output=long_output, review_report="REVIEW")
        assert "PYTEST OUTPUT (last 9000 chars)" in user
        assert "REVIEW REPORT" in user
        assert user.count("x") == 9004


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

    def _make_fake_reviewer(self, verdicts: dict[str, list[str]]):
        calls = []
        def reviewer(files, report_path):
            calls.append((files, report_path))
            vlist = verdicts.get("glm", [])
            verdict = vlist.pop(0) if vlist else "NONE"
            report_path.write_text(f"verdict: {verdict}")
            return {"verdict": verdict, "status": "ok", "out": "ok"}
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
        mock_nemotron = MagicMock(parse_files=parse_files, check_path=check_path)
        return patch.object(fix_loop, "nemotron_code_for_loop", mock_nemotron)

    def test_passes_round_zero(self, tmp_path: Path, monkeypatch):
        job = {
            "name": "job1",
            "spec": "spec.md",
            "files": ["a.py"],
            "tests": ["tests/test_a.py"],
            "max_rounds": 3,
            "review": False,
            "review_rounds": 0,
        }
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test_a.py").write_text("def test_ok(): assert True\n")

        caller, caller_calls = self._make_fake_caller([
            ("FILE: a.py\n```python\nprint('hi')\n```", {"status": 200}),
        ])
        reviewer, _ = self._make_fake_reviewer({})
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
            "max_rounds": 3,
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
        reviewer, _ = self._make_fake_reviewer({})
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
            "max_rounds": 3,
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
        reviewer, _ = self._make_fake_reviewer({})
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
            "max_rounds": 3,
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
        reviewer, _ = self._make_fake_reviewer({})
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
            "max_rounds": 3,
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
        reviewer, _ = self._make_fake_reviewer({})
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
            "max_rounds": 3,
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
        reviewer, _ = self._make_fake_reviewer({})
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
            "max_rounds": 3,
            "review": False,
            "review_rounds": 0,
        }
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test.py").write_text("def test_ok(): assert True\n")

        def caller(system, user):
            raise RuntimeError("boom")
        reviewer, _ = self._make_fake_reviewer({})
        parse_files, _ = self._make_fake_parse_files([({"a.py": "ok"}, [])])
        check_path = self._make_fake_check_path({"a.py": None})

        monkeypatch.setattr(fix_loop, "run_pytest", lambda tests, root, **kw: (True, "pass"))

        with self._setup_mocks(monkeypatch, parse_files, check_path):
            result = fix_loop.run_job(job, tmp_path, caller=caller, reviewer=reviewer, status_dir=tmp_path / "_loop")

        assert result["state"] == "escalate"

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
        reviewer, _ = self._make_fake_reviewer({})
        parse_files, _ = self._make_fake_parse_files([({"a.py": "bad", "new.py": "new"}, [])])
        check_path = self._make_fake_check_path({"a.py": None, "new.py": None})

        monkeypatch.setattr(fix_loop, "run_pytest", lambda tests, root, **kw: (False, "fail"))

        with self._setup_mocks(monkeypatch, parse_files, check_path):
            result = fix_loop.run_job(job, tmp_path, caller=caller, reviewer=reviewer, status_dir=tmp_path / "_loop")

        assert result["state"] == "escalate"
        assert (tmp_path / "a.py").read_text() == "ORIGINAL"
        assert not (tmp_path / "new.py").exists()
        escalate_file = tmp_path / "_loop" / "job8" / "ESCALATE.md"
        assert escalate_file.exists()
        assert "Escalation Report" in escalate_file.read_text()

    def test_review_ready_first(self, tmp_path: Path, monkeypatch):
        job = {
            "name": "job9",
            "spec": "spec.md",
            "files": ["a.py"],
            "tests": ["tests/test.py"],
            "max_rounds": 3,
            "review": True,
            "review_rounds": 2,
            "reviewers": ["glm"],
        }
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test.py").write_text("def test_ok(): assert True\n")

        caller, caller_calls = self._make_fake_caller([
            ("FILE: a.py\n```python\nok\n```", {"status": 200}),
        ])
        reviewer, reviewer_calls = self._make_fake_reviewer({"glm": ["READY"]})
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
            "reviewers": ["glm"],
        }
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test.py").write_text("def test_ok(): assert True\n")

        caller, caller_calls = self._make_fake_caller([
            ("FILE: a.py\n```python\nv1\n```", {"status": 200}),
            ("FILE: a.py\n```python\nv2\n```", {"status": 200}),
        ])
        reviewer, reviewer_calls = self._make_fake_reviewer({"glm": ["FIX FIRST", "READY"]})
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
            "max_rounds": 3,
            "review": True,
            "review_rounds": 2,
            "reviewers": ["glm"],
        }
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test.py").write_text("def test_ok(): assert True\n")

        caller, caller_calls = self._make_fake_caller([
            ("FILE: a.py\n```python\nok\n```", {"status": 200}),
        ])
        reviewer, reviewer_calls = self._make_fake_reviewer({"glm": ["NONE"]})
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
            "max_rounds": 3,
            "review": True,
            "review_rounds": 1,
            "reviewers": ["glm"],
        }
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test.py").write_text("def test_ok(): assert True\n")

        caller, caller_calls = self._make_fake_caller([
            ("FILE: a.py\n```python\nok\n```", {"status": 200}),
            ("FILE: a.py\n```python\nok2\n```", {"status": 200}),
        ])
        reviewer, reviewer_calls = self._make_fake_reviewer({"glm": ["FIX FIRST"]})
        parse_files, _ = self._make_fake_parse_files([
            ({"a.py": "ok"}, []),
            ({"a.py": "ok2"}, []),
        ])
        check_path = self._make_fake_check_path({"a.py": None})

        monkeypatch.setattr(fix_loop, "run_pytest", lambda tests, root, **kw: (True, "pass"))

        with self._setup_mocks(monkeypatch, parse_files, check_path):
            result = fix_loop.run_job(job, tmp_path, caller=caller, reviewer=reviewer, status_dir=tmp_path / "_loop")

        assert result["state"] == "passed-no-review"
        assert result["review_verdict"] == "unavailable"
        assert len(reviewer_calls) == 1
        assert len(caller_calls) == 2

    def test_multiple_reviewers_all_ready(self, tmp_path: Path, monkeypatch):
        job = {
            "name": "job13",
            "spec": "spec.md",
            "files": ["a.py"],
            "tests": ["tests/test.py"],
            "max_rounds": 3,
            "review": True,
            "review_rounds": 2,
            "reviewers": ["glm", "codex"],
        }
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test.py").write_text("def test_ok(): assert True\n")

        caller, caller_calls = self._make_fake_caller([
            ("FILE: a.py\n```python\nok\n```", {"status": 200}),
        ])
        def make_reviewer(verdicts):
            calls = []
            def reviewer(files, report_path):
                calls.append((files, report_path))
                v = verdicts.pop(0) if verdicts else "NONE"
                report_path.write_text(f"verdict: {v}")
                return {"verdict": v, "status": "ok", "out": "ok"}
            return reviewer, calls
        glm_reviewer, glm_calls = make_reviewer(["READY"])
        codex_reviewer, codex_calls = make_reviewer(["READY"])
        reviewer = {"glm": glm_reviewer, "codex": codex_reviewer}
        parse_files, _ = self._make_fake_parse_files([({"a.py": "ok"}, [])])
        check_path = self._make_fake_check_path({"a.py": None})

        monkeypatch.setattr(fix_loop, "run_pytest", lambda tests, root, **kw: (True, "pass"))

        with self._setup_mocks(monkeypatch, parse_files, check_path):
            result = fix_loop.run_job(job, tmp_path, caller=caller, reviewer=reviewer, status_dir=tmp_path / "_loop")

        assert result["state"] == "passed"
        assert len(glm_calls) == 1
        assert len(codex_calls) == 1

    def test_multiple_reviewers_one_fix_first(self, tmp_path: Path, monkeypatch):
        job = {
            "name": "job14",
            "spec": "spec.md",
            "files": ["a.py"],
            "tests": ["tests/test.py"],
            "max_rounds": 3,
            "review": True,
            "review_rounds": 2,
            "reviewers": ["glm", "codex"],
        }
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test.py").write_text("def test_ok(): assert True\n")

        caller, caller_calls = self._make_fake_caller([
            ("FILE: a.py\n```python\nv1\n```", {"status": 200}),
            ("FILE: a.py\n```python\nv2\n```", {"status": 200}),
        ])
        def make_reviewer(verdicts):
            calls = []
            def reviewer(files, report_path):
                calls.append((files, report_path))
                v = verdicts.pop(0) if verdicts else "NONE"
                report_path.write_text(f"verdict: {v}")
                return {"verdict": v, "status": "ok", "out": "ok"}
            return reviewer, calls
        glm_reviewer, glm_calls = make_reviewer(["READY", "READY"])
        codex_reviewer, codex_calls = make_reviewer(["FIX FIRST", "READY"])
        reviewer = {"glm": glm_reviewer, "codex": codex_reviewer}
        parse_files, _ = self._make_fake_parse_files([
            ({"a.py": "v1"}, []),
            ({"a.py": "v2"}, []),
        ])
        check_path = self._make_fake_check_path({"a.py": None})

        monkeypatch.setattr(fix_loop, "run_pytest", lambda tests, root, **kw: (True, "pass"))

        with self._setup_mocks(monkeypatch, parse_files, check_path):
            result = fix_loop.run_job(job, tmp_path, caller=caller, reviewer=reviewer, status_dir=tmp_path / "_loop")

        assert result["state"] == "passed"
        assert len(caller_calls) == 2
        assert len(glm_calls) == 2
        assert len(codex_calls) == 2

    def test_status_json_and_round_files_written(self, tmp_path: Path, monkeypatch):
        job = {
            "name": "job15",
            "spec": "spec.md",
            "files": ["a.py"],
            "tests": ["tests/test.py"],
            "max_rounds": 3,
            "review": False,
            "review_rounds": 0,
        }
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test.py").write_text("def test_ok(): assert True\n")

        caller, _ = self._make_fake_caller([
            ("FILE: a.py\n```python\nok\n```", {"status": 200}),
        ])
        reviewer, _ = self._make_fake_reviewer({})
        parse_files, _ = self._make_fake_parse_files([({"a.py": "ok"}, [])])
        check_path = self._make_fake_check_path({"a.py": None})

        monkeypatch.setattr(fix_loop, "run_pytest", lambda tests, root, **kw: (True, "pass"))

        status_dir = tmp_path / "_loop"
        with self._setup_mocks(monkeypatch, parse_files, check_path):
            fix_loop.run_job(job, tmp_path, caller=caller, reviewer=reviewer, status_dir=status_dir)

        status_file = status_dir / "job15" / "status.json"
        assert status_file.exists()
        status = json.loads(status_file.read_text())
        assert status["name"] == "job15"
        assert status["state"] == "passed-no-review"
        assert len(status["rounds"]) == 1

        round_file = status_dir / "job15" / "round_0.txt"
        assert round_file.exists()
        assert "ok" in round_file.read_text()

    def test_no_files_outside_expected_and_status_dir(self, tmp_path: Path, monkeypatch):
        job = {
            "name": "job16",
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
        reviewer, _ = self._make_fake_reviewer({})
        parse_files, _ = self._make_fake_parse_files([({"a.py": "ok", "stray.py": "bad"}, [])])
        check_path = self._make_fake_check_path({"a.py": None, "stray.py": None})

        monkeypatch.setattr(fix_loop, "run_pytest", lambda tests, root, **kw: (True, "pass"))

        status_dir = tmp_path / "_loop"
        with self._setup_mocks(monkeypatch, parse_files, check_path):
            fix_loop.run_job(job, tmp_path, caller=caller, reviewer=reviewer, status_dir=status_dir)

        assert not (tmp_path / "stray.py").exists()
        assert (status_dir / "job16").exists()

    def test_scrub_keys_applied(self, tmp_path: Path, monkeypatch):
        job = {
            "name": "job17",
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
        reviewer, _ = self._make_fake_reviewer({})
        parse_files, _ = self._make_fake_parse_files([({"a.py": secret}, [])])
        check_path = self._make_fake_check_path({"a.py": None})

        monkeypatch.setattr(fix_loop, "run_pytest", lambda tests, root, **kw: (True, "pass"))

        status_dir = tmp_path / "_loop"
        with self._setup_mocks(monkeypatch, parse_files, check_path):
            fix_loop.run_job(job, tmp_path, caller=caller, reviewer=reviewer, status_dir=status_dir, scrub_keys=[secret])

        round_file = status_dir / "job17" / "round_0.txt"
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

    def test_main_pass_no_review_returns_0(self, tmp_path: Path, monkeypatch):
        job_data = {"name": "ok", "spec": "spec.md", "files": ["a.py"], "tests": ["tests/test.py"]}
        job_file = tmp_path / "job.yaml"
        job_file.write_text(yaml.dump(job_data))
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test.py").write_text("def test_ok(): assert True\n")

        monkeypatch.setattr(fix_loop, "run_job", lambda *a, **kw: {"state": "passed-no-review"})
        rc = fix_loop.main(["--job", str(job_file.relative_to(tmp_path)), "--root", str(tmp_path)])
        assert rc == 0

    def test_main_escalate_returns_3(self, tmp_path: Path, monkeypatch):
        job_data = {"name": "esc", "spec": "spec.md", "files": ["a.py"], "tests": ["tests/test.py"]}
        job_file = tmp_path / "job.yaml"
        job_file.write_text(yaml.dump(job_data))
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test.py").write_text("def test_ok(): assert True\n")

        monkeypatch.setattr(fix_loop, "run_job", lambda *a, **kw: {"state": "escalate"})
        rc = fix_loop.main(["--job", str(job_file.relative_to(tmp_path)), "--root", str(tmp_path)])
        assert rc == 3

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
