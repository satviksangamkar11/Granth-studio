# TASK: return ONLY ONE FILE: tests/test_review_run.py (complete). Reply with exactly one block `FILE: tests/test_review_run.py` then the python fenced. The MODULE scripts/source/review_run.py was deliberately changed (shown for reference, do NOT return it): (1) the secrets skip applies to the WHOLE path (any component containing `secrets`, case-insensitive, or a name ending `.env`/`.key`; problem text `skipped <path>: secrets`); (2) file content goes into the fenced block VERBATIM (no added leading space); (3) the verdict is exactly READY, FIX FIRST or NONE (anything else NONE); (4) the total size of the prompt never exceeds max_total_bytes (overhead counted in bytes). UPDATE the old tests that assumed the previous behaviour (the failing ones are listed below) and ADD isolated regression tests: a file under a folder named `secrets` is skipped and its content absent; verbatim content (a file with leading spaces appears character for character: assert the exact text is a substring); an unknown verdict line gives NONE; the byte limit holds exactly (total <= limit, also with non-ASCII text). Keep every other test.
## Failing tests with the new module
FAILED tests/test_review_run.py::TestBuildPrompt::test_fence_longer_than_content_backticks
FAILED tests/test_review_run.py::TestBuildPrompt::test_secrets_file_skipped
FAILED tests/test_review_run.py::TestBuildPrompt::test_env_file_skipped - ass...
FAILED tests/test_review_run.py::TestBuildPrompt::test_key_file_skipped - ass...
4 failed, 32 passed in 0.38s

## CURRENT tests/test_review_run.py
```python
from __future__ import annotations

import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

TEST_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = TEST_ROOT / "scripts" / "source"

sys.path.insert(0, str(SRC_ROOT))

import review_run as rr


class TestBuildPrompt:
    def test_basic_prompt_and_file(self, tmp_path: Path):
        root = tmp_path / "proj"
        root.mkdir()
        f = root / "a.py"
        f.write_text("print('hello')", encoding="utf-8")
        prompt = "Review this:"
        user, problems = rr.build_prompt(prompt, [f], root)
        assert "Review this:" in user
        assert "## FILE a.py" in user
        assert "print('hello')" in user
        assert problems == []

    def test_fence_longer_than_content_backticks(self, tmp_path: Path):
        root = tmp_path / "proj"
        root.mkdir()
        f = root / "b.py"
        content = "```\ncode\n```"
        f.write_text(content, encoding="utf-8")
        user, problems = rr.build_prompt("p", [f], root)
        assert "```" in user
        fence_lines = [line for line in user.splitlines() if line.startswith("```")]
        assert len(fence_lines) >= 2
        for fl in fence_lines:
            assert fl.count("`") > 3
        assert problems == []

    def test_missing_file_skipped(self, tmp_path: Path):
        root = tmp_path / "proj"
        root.mkdir()
        missing = root / "missing.py"
        user, problems = rr.build_prompt("p", [missing], root)
        assert "missing.py" not in user
        assert any("skipped" in p and "not found" in p for p in problems)

    def test_file_outside_root_skipped(self, tmp_path: Path):
        root = tmp_path / "proj"
        root.mkdir()
        outside = tmp_path / "outside.py"
        outside.write_text("x=1", encoding="utf-8")
        user, problems = rr.build_prompt("p", [outside], root)
        assert "outside.py" not in user
        assert any("skipped" in p and "not under root" in p for p in problems)

    def test_directory_skipped(self, tmp_path: Path):
        root = tmp_path / "proj"
        root.mkdir()
        sub = root / "subdir"
        sub.mkdir()
        user, problems = rr.build_prompt("p", [sub], root)
        assert "subdir" not in user
        assert any("skipped" in p and "is a directory" in p for p in problems)

    def test_secrets_file_skipped(self, tmp_path: Path):
        root = tmp_path / "proj"
        root.mkdir()
        secret = root / "secrets.py"
        secret.write_text("API_KEY = 'real-key-123'", encoding="utf-8")
        user, problems = rr.build_prompt("p", [secret], root)
        assert "real-key-123" not in user
        assert any("skipped" in p and "secret-like name" in p for p in problems)

    def test_env_file_skipped(self, tmp_path: Path):
        root = tmp_path / "proj"
        root.mkdir()
        env = root / ".env"
        env.write_text("SECRET=abc", encoding="utf-8")
        user, problems = rr.build_prompt("p", [env], root)
        assert "SECRET=abc" not in user
        assert any("skipped" in p and "secret-like name" in p for p in problems)

    def test_key_file_skipped(self, tmp_path: Path):
        root = tmp_path / "proj"
        root.mkdir()
        keyf = root / "api.key"
        keyf.write_text("keydata", encoding="utf-8")
        user, problems = rr.build_prompt("p", [keyf], root)
        assert "keydata" not in user
        assert any("skipped" in p and "secret-like name" in p for p in problems)

    def test_binary_file_skipped(self, tmp_path: Path):
        root = tmp_path / "proj"
        root.mkdir()
        binf = root / "data.bin"
        binf.write_bytes(b"\x00\x01\x02\xff")
        user, problems = rr.build_prompt("p", [binf], root)
        assert "data.bin" not in user
        assert any("skipped" in p and "not text" in p for p in problems)

    def test_size_limit_truncates_and_skips_rest(self, tmp_path: Path):
        root = tmp_path / "proj"
        root.mkdir()
        f1 = root / "f1.txt"
        f2 = root / "f2.txt"
        big = "x" * 500_000
        f1.write_text(big, encoding="utf-8")
        f2.write_text("small", encoding="utf-8")
        user, problems = rr.build_prompt("p", [f1, f2], root, max_total_bytes=1000)
        assert "[truncated]" in user
        assert any("truncated" in p and "f1.txt" in p for p in problems)
        assert any("skipped" in p and "f2.txt" in p and "size limit" in p for p in problems)

    # Defect 2: PermissionError on read should be caught, not propagate
    def test_permission_error_on_read_is_caught(self, tmp_path: Path, monkeypatch):
        root = tmp_path / "proj"
        root.mkdir()
        f = root / "secret.txt"
        f.write_text("content", encoding="utf-8")

        original_read_text = Path.read_text

        def mock_read_text(self, encoding="utf-8"):
            if self == f:
                raise PermissionError("Permission denied")
            return original_read_text(self, encoding=encoding)

        monkeypatch.setattr(Path, "read_text", mock_read_text)

        user, problems = rr.build_prompt("p", [f], root)
        assert "secret.txt" not in user
        assert any("skipped" in p and "not readable" in p for p in problems)


class TestApplyReviewProfile:
    def test_medium_adds_fields(self):
        body = {"model": "test", "messages": [], "temperature": 0.7}
        out = rr.apply_review_profile(body, "medium")
        assert out["chat_template_kwargs"]["enable_thinking"] is True
        assert out["reasoning_effort"] == "medium"
        # Protected keys unchanged
        assert out["model"] == "test"
        assert out["messages"] == []
        assert out["temperature"] == 0.7
        # Input not mutated
        assert "chat_template_kwargs" not in body
        assert "reasoning_effort" not in body

    def test_none_omits_reasoning_effort(self):
        body = {"model": "test", "messages": []}
        out = rr.apply_review_profile(body, "none")
        assert out["chat_template_kwargs"]["enable_thinking"] is True
        assert "reasoning_effort" not in out
        assert out["model"] == "test"

    def test_unknown_effort_treated_as_medium(self):
        body = {"model": "test"}
        out = rr.apply_review_profile(body, "unknown")
        assert out["reasoning_effort"] == "medium"
        out2 = rr.apply_review_profile(body, "high")
        assert out2["reasoning_effort"] == "high"
        out3 = rr.apply_review_profile(body, "low")
        assert out3["reasoning_effort"] == "low"

    def test_protected_keys_not_overwritten(self):
        body = {
            "model": "original-model",
            "messages": [{"role": "user", "content": "hi"}],
            "stream": False,
            "max_tokens": 100,
            "temperature": 0.5,
        }
        out = rr.apply_review_profile(body, "medium")
        assert out["model"] == "original-model"
        assert out["messages"] == [{"role": "user", "content": "hi"}]
        assert out["stream"] is False
        assert out["max_tokens"] == 100
        assert out["temperature"] == 0.5

    def test_input_not_mutated(self):
        body = {"model": "test"}
        body_copy = dict(body)
        rr.apply_review_profile(body, "medium")
        assert body == body_copy


class TestRunReview:
    def fake_caller_ready(self, system: str, user: str) -> tuple[str, dict]:
        return "All good.\n## Verdict: READY", {"status": 200, "wall_s": 1.2, "finish": "stop", "usage": {}, "error": ""}

    def fake_caller_fix(self, system: str, user: str) -> tuple[str, dict]:
        return "Fix line 10.\n## Verdict: FIX FIRST", {"status": 200, "wall_s": 0.5, "finish": "stop", "usage": {}, "error": ""}

    def fake_caller_no_verdict(self, system: str, user: str) -> tuple[str, dict]:
        return "Some text without verdict.", {"status": 200, "wall_s": 0.3, "finish": "stop", "usage": {}, "error": ""}

    def fake_caller_fail_status(self, system: str, user: str) -> tuple[str, dict]:
        return "", {"status": 500, "wall_s": 0.1, "finish": "error", "usage": {}, "error": "model error"}

    def fake_caller_empty_reply(self, system: str, user: str) -> tuple[str, dict]:
        return "", {"status": 200, "wall_s": 0.1, "finish": "stop", "usage": {}, "error": ""}

    def fake_caller_raises(self, system: str, user: str) -> tuple[str, dict]:
        raise RuntimeError("boom")

    def test_ready_verdict(self, tmp_path: Path):
        root = tmp_path / "proj"
        root.mkdir()
        prompt = root / "prompt.txt"
        prompt.write_text("Review:", encoding="utf-8")
        out = tmp_path / "out.md"
        result = rr.run_review(
            model="test-model",
            prompt_file=prompt,
            files=[],
            out_path=out,
            root=root,
            caller=self.fake_caller_ready,
        )
        assert out.exists()
        assert result["verdict"] == "READY"
        assert result["status"] == 200
        assert "All good" in out.read_text()

    def test_fix_first_verdict(self, tmp_path: Path):
        root = tmp_path / "proj"
        root.mkdir()
        prompt = root / "prompt.txt"
        prompt.write_text("Review:", encoding="utf-8")
        out = tmp_path / "out.md"
        result = rr.run_review(
            model="test-model",
            prompt_file=prompt,
            files=[],
            out_path=out,
            root=root,
            caller=self.fake_caller_fix,
        )
        assert result["verdict"] == "FIX FIRST"
        assert result["status"] == 200

    def test_no_verdict_line(self, tmp_path: Path):
        root = tmp_path / "proj"
        root.mkdir()
        prompt = root / "prompt.txt"
        prompt.write_text("Review:", encoding="utf-8")
        out = tmp_path / "out.md"
        result = rr.run_review(
            model="test-model",
            prompt_file=prompt,
            files=[],
            out_path=out,
            root=root,
            caller=self.fake_caller_no_verdict,
        )
        assert result["verdict"] == "NONE"

    def test_existing_out_file_raises(self, tmp_path: Path):
        root = tmp_path / "proj"
        root.mkdir()
        prompt = root / "prompt.txt"
        prompt.write_text("Review:", encoding="utf-8")
        out = tmp_path / "out.md"
        out.write_text("existing", encoding="utf-8")
        with pytest.raises(FileExistsError):
            rr.run_review(
                model="test-model",
                prompt_file=prompt,
                files=[],
                out_path=out,
                root=root,
                caller=self.fake_caller_ready,
            )
        assert out.read_text() == "existing"

    def test_fail_status_writes_failed(self, tmp_path: Path):
        root = tmp_path / "proj"
        root.mkdir()
        prompt = root / "prompt.txt"
        prompt.write_text("Review:", encoding="utf-8")
        out = tmp_path / "out.md"
        result = rr.run_review(
            model="test-model",
            prompt_file=prompt,
            files=[],
            out_path=out,
            root=root,
            caller=self.fake_caller_fail_status,
        )
        assert out.exists()
        assert "REVIEW FAILED" in out.read_text()
        assert result["verdict"] == "NONE"
        assert result["status"] == 500

    def test_empty_reply_writes_failed(self, tmp_path: Path):
        root = tmp_path / "proj"
        root.mkdir()
        prompt = root / "prompt.txt"
        prompt.write_text("Review:", encoding="utf-8")
        out = tmp_path / "out.md"
        result = rr.run_review(
            model="test-model",
            prompt_file=prompt,
            files=[],
            out_path=out,
            root=root,
            caller=self.fake_caller_empty_reply,
        )
        assert out.exists()
        assert "REVIEW FAILED" in out.read_text()
        assert result["verdict"] == "NONE"

    def test_caller_raises_writes_failed(self, tmp_path: Path):
        root = tmp_path / "proj"
        root.mkdir()
        prompt = root / "prompt.txt"
        prompt.write_text("Review:", encoding="utf-8")
        out = tmp_path / "out.md"
        result = rr.run_review(
            model="test-model",
            prompt_file=prompt,
            files=[],
            out_path=out,
            root=root,
            caller=self.fake_caller_raises,
        )
        assert out.exists()
        assert "REVIEW FAILED" in out.read_text()
        assert "RuntimeError" in out.read_text()
        assert result["verdict"] == "NONE"
        assert "error" in result
        assert "RuntimeError" in result["error"]

    def test_run_review_records_effort_and_thinking(self, tmp_path: Path):
        root = tmp_path / "proj"
        root.mkdir()
        prompt = root / "prompt.txt"
        prompt.write_text("Review:", encoding="utf-8")
        out = tmp_path / "out.md"
        result = rr.run_review(
            model="test-model",
            prompt_file=prompt,
            files=[],
            out_path=out,
            root=root,
            caller=self.fake_caller_ready,
            effort="high",
        )
        assert result["effort"] == "high"
        assert result["thinking"] is True

    # Defect 1: Error message with key should be scrubbed before writing to output file
    def test_error_message_scrubbed_before_write(self, tmp_path: Path):
        root = tmp_path / "proj"
        root.mkdir()
        prompt = root / "prompt.txt"
        prompt.write_text("Review:", encoding="utf-8")
        out = tmp_path / "out.md"
        secret_key = "SECRET_API_KEY_12345"

        def fake_caller_raises_with_key(system: str, user: str) -> tuple[str, dict]:
            raise RuntimeError(f"auth failed for {secret_key}")

        result = rr.run_review(
            model="test-model",
            prompt_file=prompt,
            files=[],
            out_path=out,
            root=root,
            caller=fake_caller_raises_with_key,
            scrub_keys=[secret_key],
        )
        content = out.read_text()
        assert secret_key not in content, f"Key leaked in output file: {content}"
        assert "[key]" in content
        assert "REVIEW FAILED" in content

    # Defect 3: Truncation should respect exact byte limit (account for "\n [truncated]" overhead)
    def test_truncation_respects_exact_byte_limit(self, tmp_path: Path):
        root = tmp_path / "proj"
        root.mkdir()
        f = root / "big.txt"
        # 5000 chars, well over 1000 byte limit
        f.write_text("x" * 5000, encoding="utf-8")
        user, problems = rr.build_prompt("P", [f], root, max_total_bytes=1000)
        # The total encoded bytes should not exceed max_total_bytes
        user_bytes = user.encode("utf-8")
        assert len(user_bytes) <= 1000, f"Expected <= 1000 bytes, got {len(user_bytes)}"
        assert "[truncated]" in user
        assert any("truncated" in p and "big.txt" in p for p in problems)


class TestSecretsScrubbing:
    def fake_caller_echoes_key(self, system: str, user: str) -> tuple[str, dict]:
        return "The key is FAKE_KEY_12345 and that's it.\n## Verdict: READY", {
            "status": 200,
            "wall_s": 0.1,
            "finish": "stop",
            "usage": {},
            "error": "",
        }

    def test_scrub_keys_removes_from_output_and_dict(self, tmp_path: Path):
        root = tmp_path / "proj"
        root.mkdir()
        prompt = root / "prompt.txt"
        prompt.write_text("Review:", encoding="utf-8")
        out = tmp_path / "out.md"
        result = rr.run_review(
            model="test-model",
            prompt_file=prompt,
            files=[],
            out_path=out,
            root=root,
            caller=self.fake_caller_echoes_key,
            scrub_keys=["FAKE_KEY_12345"],
        )
        content = out.read_text()
        assert "FAKE_KEY_12345" not in content
        assert "[key]" in content
        assert result["verdict"] == "READY"
        assert "FAKE_KEY_12345" not in str(result)
        assert "[key]" in str(result)


class TestMain:
    def test_missing_prompt_file_returns_2(self, tmp_path: Path, capsys):
        prompt = tmp_path / "missing.txt"
        out = tmp_path / "out.md"
        rc = rr.main(["--prompt-file", str(prompt), "--out", str(out)])
        assert rc == 2
        captured = capsys.readouterr()
        assert "refused:" in captured.out.lower()

    def test_existing_out_file_returns_2(self, tmp_path: Path, capsys):
        root = tmp_path / "proj"
        root.mkdir()
        prompt = root / "prompt.txt"
        prompt.write_text("Review:", encoding="utf-8")
        out = tmp_path / "out.md"
        out.write_text("existing", encoding="utf-8")
        rc = rr.main(["--prompt-file", str(prompt), "--out", str(out)])
        assert rc == 2
        captured = capsys.readouterr()
        assert "refused:" in captured.out.lower()

    def test_success_path_prints_summary(self, tmp_path: Path, capsys, monkeypatch):
        root = tmp_path / "proj"
        root.mkdir()
        prompt = root / "prompt.txt"
        prompt.write_text("Review:", encoding="utf-8")
        out = tmp_path / "out.md"

        def mock_run_review(*args, **kwargs):
            return {
                "model": "z-ai/glm-5.3-flash",
                "out": str(out),
                "status": 200,
                "wall_s": 1.234,
                "finish": "stop",
                "usage": {},
                "problems": [],
                "chars": 10,
                "verdict": "READY",
            }

        monkeypatch.setattr(rr, "run_review", mock_run_review)
        rc = rr.main(["--prompt-file", str(prompt), "--out", str(out)])
        assert rc == 0
        captured = capsys.readouterr()
        assert "review: status=200" in captured.out
        assert "wall_s=1.234" in captured.out
        assert "verdict=READY" in captured.out
        assert "problems=0" in captured.out
        assert f"out={out}" in captured.out

    def test_cli_default_effort_medium(self, tmp_path: Path, monkeypatch):
        root = tmp_path / "proj"
        root.mkdir()
        prompt = root / "prompt.txt"
        prompt.write_text("Review:", encoding="utf-8")
        out = tmp_path / "out.md"

        captured_kwargs = {}

        def mock_run_review(*args, **kwargs):
            captured_kwargs.update(kwargs)
            return {
                "model": "z-ai/glm-5.3-flash",
                "out": str(out),
                "status": 200,
                "wall_s": 1.0,
                "finish": "stop",
                "usage": {},
                "problems": [],
                "chars": 10,
                "verdict": "READY",
                "effort": kwargs.get("effort", "medium"),
                "thinking": True,
            }

        monkeypatch.setattr(rr, "run_review", mock_run_review)
        rc = rr.main(["--prompt-file", str(prompt), "--out", str(out)])
        assert rc == 0
        assert captured_kwargs.get("effort") == "medium"

    def test_cli_effort_option(self, tmp_path: Path, monkeypatch):
        root = tmp_path / "proj"
        root.mkdir()
        prompt = root / "prompt.txt"
        prompt.write_text("Review:", encoding="utf-8")
        out = tmp_path / "out.md"

        captured_kwargs = {}

        def mock_run_review(*args, **kwargs):
            captured_kwargs.update(kwargs)
            return {
                "model": "z-ai/glm-5.3-flash",
                "out": str(out),
                "status": 200,
                "wall_s": 1.0,
                "finish": "stop",
                "usage": {},
                "problems": [],
                "chars": 10,
                "verdict": "READY",
                "effort": kwargs.get("effort", "medium"),
                "thinking": True,
            }

        monkeypatch.setattr(rr, "run_review", mock_run_review)
        rc = rr.main(["--prompt-file", str(prompt), "--out", str(out), "--effort", "high"])
        assert rc == 0
        assert captured_kwargs.get("effort") == "high"

    # Defect 4: main should return 1 when status=200 but chars=0 (empty reply)
    def test_main_returns_1_on_empty_reply_with_200_status(self, tmp_path: Path, monkeypatch, capsys):
        root = tmp_path / "proj"
        root.mkdir()
        prompt = root / "prompt.txt"
        prompt.write_text("Review:", encoding="utf-8")
        out = tmp_path / "out.md"

        def mock_run_review_empty_reply(*args, **kwargs):
            return {
                "model": "z-ai/glm-5.3-flash",
                "out": str(out),
                "status": 200,
                "wall_s": 1.0,
                "finish": "stop",
                "usage": {},
                "problems": [],
                "chars": 0,  # Empty reply
                "verdict": "NONE",
                "effort": "medium",
                "thinking": True,
            }

        monkeypatch.setattr(rr, "run_review", mock_run_review_empty_reply)
        rc = rr.main(["--prompt-file", str(prompt), "--out", str(out)])
        assert rc == 1, f"Expected exit code 1 for empty reply, got {rc}"


class TestModuleHygiene:
    def test_no_nvapi_literal(self):
        source = (SRC_ROOT / "review_run.py").read_text(encoding="utf-8")
        assert "nvapi-" not in source

    def test_no_kimi_adapter_import(self):
        source = (SRC_ROOT / "review_run.py").read_text(encoding="utf-8")
        assert "kimi_adapter" not in source


class TestStreamOnceWrapper:
    # Defect 5: The wrapper for ds._stream_once must have signature (key, body, *args, **kwargs)
    # and pass key through unchanged as first argument, with modified body having
    # chat_template_kwargs.enable_thinking=True and reasoning_effort='medium'
    def test_stream_once_wrapper_signature_and_body(self, tmp_path: Path, monkeypatch):
        # Create a fake draft_source module with _stream_once(key, body) that records calls
        recorded = {"key": None, "body": None, "args": None, "kwargs": None}

        class FakeDraftSource:
            def __init__(self):
                self.nt = MagicMock()
                self.nt.load_keys.return_value = ["FAKEKEY"]
                self.nt.KeyPool = MagicMock(return_value=MagicMock())
                self.nt.scrub = lambda text, keys: text
                self._stream_once = self._stream_once_impl

            def _stream_once_impl(self, key, body, *args, **kwargs):
                recorded["key"] = key
                recorded["body"] = body
                recorded["args"] = args
                recorded["kwargs"] = kwargs
                # Return a synchronous generator that yields one chunk
                def gen():
                    yield "done"
                return gen()

            def chat_stream(self, pool, keys, model, system, user, max_tokens=64000):
                # Call _stream_once with the expected signature (synchronous)
                for chunk in self._stream_once("FAKEKEY", {"model": model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}], "stream": True, "max_tokens": max_tokens}):
                    pass
                return "done\n## Verdict: READY", {"status": 200, "wall_s": 0.1, "finish": "stop", "usage": {}, "error": ""}

        fake_ds = FakeDraftSource()

        # Patch _load_draft_source to return our fake
        import review_run as rr_module
        monkeypatch.setattr(rr_module, "_load_draft_source", lambda: fake_ds)
        # Patch _load_coder_run to return a mock with with_idle_timeout
        mock_cr = MagicMock()
        mock_cr.with_idle_timeout = lambda ds, idle_s: ds
        monkeypatch.setattr(rr_module, "_load_coder_run", lambda: mock_cr)

        root = tmp_path / "proj"
        root.mkdir()
        prompt = root / "prompt.txt"
        prompt.write_text("Review:", encoding="utf-8")
        out = tmp_path / "out.md"

        # Run with real path (no caller) - this exercises the wrapper
        result = rr.run_review(
            model="test-model",
            prompt_file=prompt,
            files=[],
            out_path=out,
            root=root,
            effort="medium",
        )

        # Verify the wrapper was called with correct signature and modified body
        assert recorded["key"] == "FAKEKEY", f"Key not passed through: {recorded['key']}"
        assert recorded["body"] is not None, "Body not passed"
        body = recorded["body"]
        assert body.get("chat_template_kwargs", {}).get("enable_thinking") is True, "enable_thinking not set"
        assert body.get("reasoning_effort") == "medium", f"reasoning_effort not set: {body.get('reasoning_effort')}"
        # Protected keys should be preserved
        assert body.get("model") == "test-model"
        assert body.get("stream") is True
        assert body.get("max_tokens") == 64000
```
## scripts/source/review_run.py (reference only)
```python
from __future__ import annotations

import sys
import importlib.util
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parents[2]

SYSTEM_PROMPT = (
    "You are a strict READ-ONLY code and design reviewer. "
    "You may not run anything. "
    "Report only real, verified defects with file:line and an exact fix. "
    "If nothing is wrong say so. "
    "End the report with exactly one line `## Verdict: READY` or `## Verdict: FIX FIRST`."
)


def apply_review_profile(body: dict, effort: str) -> dict:
    """Return a copy of body with review profile fields merged.

    - Adds chat_template_kwargs.enable_thinking = true
    - Adds reasoning_effort = effort (unless effort == 'none')
    - Never overwrites model, messages, stream, max_tokens, temperature
    - Unknown effort values are treated as 'medium'
    """
    protected = {"model", "messages", "stream", "max_tokens", "temperature"}
    new_body = dict(body)
    # Ensure chat_template_kwargs exists and is a dict
    ctk = new_body.get("chat_template_kwargs")
    if not isinstance(ctk, dict):
        ctk = {}
    ctk = dict(ctk)
    ctk["enable_thinking"] = True
    new_body["chat_template_kwargs"] = ctk

    eff = effort.lower() if isinstance(effort, str) else "medium"
    if eff not in ("low", "medium", "high", "none"):
        eff = "medium"
    if eff != "none":
        new_body["reasoning_effort"] = eff

    # Do not overwrite protected keys
    for k in protected:
        if k in body:
            new_body[k] = body[k]
    return new_body


def build_prompt(
    prompt_text: str,
    files: list[Path],
    root: Path,
    max_total_bytes: int = 400_000,
) -> tuple[str, list[str]]:
    root = root.resolve()
    parts: list[str] = [prompt_text]
    problems: list[str] = []
    used = len(prompt_text.encode("utf-8"))
    limit_reached = False

    for f in files:
        if limit_reached:
            problems.append(f"skipped {f}: size limit")
            continue

        try:
            f_resolved = f.resolve()
        except Exception:
            problems.append(f"skipped {f}: not found")
            continue

        if not f_resolved.exists():
            problems.append(f"skipped {f}: not found")
            continue
        if f_resolved.is_dir():
            problems.append(f"skipped {f}: is a directory")
            continue
        try:
            rel = f_resolved.relative_to(root)
        except ValueError:
            problems.append(f"skipped {f}: not under root")
            continue

        # Check for secrets in ANY path component (case-insensitive) or secret-like extensions
        rel_parts = rel.parts
        abs_parts = f_resolved.parts
        all_parts = rel_parts + abs_parts
        secret_found = any("secrets" in part.lower() for part in all_parts)
        name = f_resolved.name
        if secret_found or name.endswith(".env") or name.endswith(".key"):
            problems.append(f"skipped {f}: secrets")
            continue

        try:
            content = f_resolved.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            problems.append(f"skipped {f}: not text")
            continue
        except OSError:
            problems.append(f"skipped {f}: not readable")
            continue

        # Use content verbatim (no indentation)
        content_bytes = content.encode("utf-8")

        rel_posix = rel.as_posix()
        header = f"## FILE {rel_posix}"
        header_bytes = header.encode("utf-8")

        # Find a fence that doesn't appear in content
        fence = "```"
        while fence in content:
            fence += "`"
        fence_bytes = fence.encode("utf-8")
        newline = b"\n"

        needed = (
            len(header_bytes)
            + len(newline)
            + len(fence_bytes)
            + len(newline)
            + len(content_bytes)
            + len(newline)
            + len(fence_bytes)
            + len(newline)
        )

        if used + needed > max_total_bytes:
            remaining = max_total_bytes - used
            if remaining < 0:
                remaining = 0
            # Overhead: header\n + fence\n + \n + [truncated]\n + fence\n
            overhead = (
                len(header_bytes)
                + len(newline)
                + len(fence_bytes)
                + len(newline)
                + len(newline)          # newline after content (before marker)
                + len(b"[truncated]")
                + len(newline)          # newline after marker (before closing fence)
                + len(fence_bytes)
                + len(newline)
            )
            avail = remaining - overhead
            if avail > 0:
                # Truncate content bytes at UTF-8 boundary
                truncated_content_bytes = content_bytes[:avail]
                truncated_content = truncated_content_bytes.decode("utf-8", errors="ignore")
                truncated_content += "\n[truncated]"
                truncated_bytes = truncated_content.encode("utf-8")
                parts.append(header)
                parts.append(fence)
                parts.append(truncated_content)
                parts.append(fence)
                used += (
                    len(header_bytes)
                    + len(newline)
                    + len(fence_bytes)
                    + len(newline)
                    + len(truncated_bytes)
                    + len(newline)
                    + len(fence_bytes)
                    + len(newline)
                )
                problems.append(f"truncated {f}")
            else:
                problems.append(f"skipped {f}: size limit")
            limit_reached = True
            continue

        parts.append(header)
        parts.append(fence)
        parts.append(content)
        parts.append(fence)
        used += needed

    return "\n".join(parts), problems


def _load_draft_source() -> object:
    ds_path = REPO_ROOT / "scripts" / "source" / "draft_source.py"
    spec = importlib.util.spec_from_file_location("ds", ds_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load draft_source from {ds_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_coder_run() -> object:
    cr_path = REPO_ROOT / "scripts" / "source" / "coder_run.py"
    spec = importlib.util.spec_from_file_location("cr", cr_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load coder_run from {cr_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_review(
    model: str,
    prompt_file: Path,
    files: list[Path],
    out_path: Path,
    *,
    root: Path | None = None,
    max_tokens: int = 64000,
    idle_s: int | None = None,
    caller: Callable[[str, str], tuple[str, dict]] | None = None,
    scrub_keys: list[str] = [],
    effort: str = "medium",
) -> dict:
    if out_path.exists():
        raise FileExistsError(f"Output file already exists: {out_path}")

    if root is None:
        root = REPO_ROOT

    prompt_text = prompt_file.read_text(encoding="utf-8")
    user_text, problems = build_prompt(prompt_text, files, root)

    reply_text = ""
    info: dict = {"status": 0, "wall_s": 0.0, "finish": "", "usage": {}, "error": ""}

    try:
        if caller is not None:
            reply_text, info = caller(SYSTEM_PROMPT, user_text)
        else:
            ds = _load_draft_source()
            cr = _load_coder_run()
            ds = cr.with_idle_timeout(ds, idle_s)
            # Wrap _stream_once to inject review profile
            original_stream_once = ds._stream_once
            def wrapped_stream_once(key, body, *args, **kwargs):
                modified_body = apply_review_profile(body, effort)
                return original_stream_once(key, modified_body, *args, **kwargs)
            ds._stream_once = wrapped_stream_once
            keys = ds.nt.load_keys()
            pool = ds.nt.KeyPool(keys)
            reply_text, info = ds.chat_stream(pool, keys, model, SYSTEM_PROMPT, user_text, max_tokens=max_tokens)
            reply_text = ds.nt.scrub(reply_text, keys)
    except Exception as e:
        info = {"status": 0, "wall_s": 0.0, "finish": "error", "usage": {}, "error": f"{type(e).__name__}: {e}"}
        reply_text = ""

    # Scrub reply text
    for key in scrub_keys:
        if key:
            reply_text = reply_text.replace(key, "[key]")

    verdict = "NONE"
    for line in reversed(reply_text.splitlines()):
        line = line.strip()
        if line.startswith("## Verdict:"):
            verdict_raw = line.split(":", 1)[1].strip()
            verdict_lower = verdict_raw.lower()
            if verdict_lower == "ready":
                verdict = "READY"
            elif verdict_lower == "fix first":
                verdict = "FIX FIRST"
            else:
                verdict = "NONE"
            break

    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Scrub error message before writing to output file
    error_msg = info.get("error", "unknown error")
    for key in scrub_keys:
        if key:
            error_msg = error_msg.replace(key, "[key]")

    if info.get("status") == 200 and reply_text.strip():
        out_path.write_text(reply_text, encoding="utf-8")
    else:
        out_path.write_text(f"REVIEW FAILED: {error_msg}", encoding="utf-8")
        verdict = "NONE"

    # Scrub verdict and info strings
    for key in scrub_keys:
        if key:
            verdict = verdict.replace(key, "[key]")
            for k, v in info.items():
                if isinstance(v, str):
                    info[k] = v.replace(key, "[key]")

    result = {
        "model": model,
        "out": str(out_path),
        "status": info.get("status", 0),
        "wall_s": info.get("wall_s", 0.0),
        "finish": info.get("finish", ""),
        "usage": info.get("usage", {}),
        "problems": problems,
        "chars": len(reply_text),
        "verdict": verdict,
        "reply": reply_text,
        "error": info.get("error", ""),
        "effort": effort,
        "thinking": True,
    }

    # Scrub all string values in the result dict
    for key in scrub_keys:
        if not key:
            continue
        for k, v in list(result.items()):
            if isinstance(v, str):
                result[k] = v.replace(key, "[key]")
            elif isinstance(v, list):
                result[k] = [item.replace(key, "[key]") if isinstance(item, str) else item for item in v]
            elif isinstance(v, dict):
                for k2, v2 in v.items():
                    if isinstance(v2, str):
                        v[k2] = v2.replace(key, "[key]")

    return result


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run a review via NVIDIA GLM endpoint")
    parser.add_argument("--model", default="z-ai/glm-5.3-flash")
    parser.add_argument("--prompt-file", type=Path, required=True)
    parser.add_argument("--file", type=Path, action="append", default=[])
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--max-tokens", type=int, default=64000)
    parser.add_argument("--idle-s", type=int, default=None)
    parser.add_argument("--effort", choices=["low", "medium", "high", "none"], default="medium")
    args = parser.parse_args(argv)

    if not args.prompt_file.exists():
        print(f"refused: prompt file not found: {args.prompt_file}")
        return 2

    if args.out.exists():
        print(f"refused: output file already exists: {args.out}")
        return 2

    try:
        result = run_review(
            model=args.model,
            prompt_file=args.prompt_file,
            files=args.file,
            out_path=args.out,
            max_tokens=args.max_tokens,
            idle_s=args.idle_s,
            effort=args.effort,
        )
    except FileExistsError:
        print(f"refused: output file already exists: {args.out}")
        return 2
    except Exception as e:
        print(f"review: status=0 wall_s=0 verdict=NONE problems=0 out={args.out}")
        return 1

    print(
        f"review: status={result['status']} wall_s={result['wall_s']:.3f} "
        f"verdict={result['verdict']} problems={len(result['problems'])} out={result['out']}"
    )
    ok = result["status"] == 200 and result["chars"] > 0
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
```
