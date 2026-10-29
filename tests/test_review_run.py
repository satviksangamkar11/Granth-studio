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
        lines = user.splitlines()
        # Find the heading line for this file
        heading_idx = None
        for i, line in enumerate(lines):
            if line.strip() == "## FILE b.py":
                heading_idx = i
                break
        assert heading_idx is not None, "Heading not found"
        # Opening fence is the line right after the heading
        open_fence_line = lines[heading_idx + 1]
        assert open_fence_line.startswith("```"), f"Expected opening fence, got: {open_fence_line}"
        open_backticks = len(open_fence_line) - len(open_fence_line.lstrip('`'))
        # Find the closing fence: last backtick-only line before next heading or end
        close_fence_idx = None
        for i in range(heading_idx + 2, len(lines)):
            stripped = lines[i].strip()
            if stripped and all(ch == '`' for ch in stripped):
                close_fence_idx = i
            elif stripped.startswith("## FILE "):
                break
        assert close_fence_idx is not None, "Closing fence not found"
        close_fence_line = lines[close_fence_idx]
        close_backticks = len(close_fence_line) - len(close_fence_line.lstrip('`'))
        # Longest backtick run in original content is 3
        max_content_backticks = 3
        assert open_backticks > max_content_backticks, f"Opening fence has {open_backticks} backticks, need > {max_content_backticks}"
        assert close_backticks > max_content_backticks, f"Closing fence has {close_backticks} backticks, need > {max_content_backticks}"
        # Content lines between fences should match original content exactly
        content_lines = lines[heading_idx + 2:close_fence_idx]
        assert content_lines == content.splitlines(), f"Content mismatch: {content_lines} vs {content.splitlines()}"
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
        assert any("skipped" in p and "secrets" in p for p in problems)

    def test_env_file_skipped(self, tmp_path: Path):
        root = tmp_path / "proj"
        root.mkdir()
        env = root / ".env"
        env.write_text("SECRET=abc", encoding="utf-8")
        user, problems = rr.build_prompt("p", [env], root)
        assert "SECRET=abc" not in user
        assert any("skipped" in p and "secrets" in p for p in problems)

    def test_key_file_skipped(self, tmp_path: Path):
        root = tmp_path / "proj"
        root.mkdir()
        keyf = root / "api.key"
        keyf.write_text("keydata", encoding="utf-8")
        user, problems = rr.build_prompt("p", [keyf], root)
        assert "keydata" not in user
        assert any("skipped" in p and "secrets" in p for p in problems)

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

    # Regression: file under a folder named secrets is skipped
    def test_file_under_secrets_folder_skipped(self, tmp_path: Path):
        root = tmp_path / "proj"
        root.mkdir()
        secret_dir = root / "secrets"
        secret_dir.mkdir()
        secret_file = secret_dir / "config.py"
        secret_file.write_text("SECRET=123", encoding="utf-8")
        user, problems = rr.build_prompt("p", [secret_file], root)
        assert "SECRET=123" not in user
        assert any("skipped" in p and "secrets" in p for p in problems)

    # Regression: verbatim content (leading spaces preserved)
    def test_verbatim_content_preserved(self, tmp_path: Path):
        root = tmp_path / "proj"
        root.mkdir()
        f = root / "indented.py"
        content = "  def foo():\n    return 42"
        f.write_text(content, encoding="utf-8")
        user, problems = rr.build_prompt("p", [f], root)
        # The exact content should appear as a substring (verbatim)
        assert content in user
        assert problems == []

    # Regression: byte limit holds exactly with non-ASCII text
    def test_byte_limit_exact_with_nonascii(self, tmp_path: Path):
        root = tmp_path / "proj"
        root.mkdir()
        f = root / "utf8.txt"
        # 3-byte UTF-8 characters: '€' is 3 bytes
        content = "€" * 200  # 600 bytes
        f.write_text(content, encoding="utf-8")
        user, problems = rr.build_prompt("P", [f], root, max_total_bytes=500)
        user_bytes = user.encode("utf-8")
        assert len(user_bytes) <= 500
        assert "[truncated]" in user
        assert any("truncated" in p and "utf8.txt" in p for p in problems)


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

    # Regression: unknown verdict line gives NONE
    def test_unknown_verdict_line_gives_none(self, tmp_path: Path):
        root = tmp_path / "proj"
        root.mkdir()
        prompt = root / "prompt.txt"
        prompt.write_text("Review:", encoding="utf-8")
        out = tmp_path / "out.md"

        def fake_caller_unknown_verdict(system: str, user: str) -> tuple[str, dict]:
            return "Something.\n## Verdict: MAYBE", {"status": 200, "wall_s": 0.1, "finish": "stop", "usage": {}, "error": ""}

        result = rr.run_review(
            model="test-model",
            prompt_file=prompt,
            files=[],
            out_path=out,
            root=root,
            caller=fake_caller_unknown_verdict,
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
