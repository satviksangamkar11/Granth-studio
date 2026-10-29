# TASK: return TWO FILES: scripts/source/review_run.py and tests/test_review_run.py (complete). Keep everything that works (23 tests pass). Add ONE feature: the reasoning effort for the reviewer model.
## Finding (live probe): z-ai/glm-5.3-flash accepts `reasoning_effort` ("low"|"medium"|"high") and `chat_template_kwargs`: {"enable_thinking": true}; the effort changes how much it thinks. The owner wants GLM 5.3 flash with THINKING ON and EFFORT MEDIUM as the reviewer.
## Change: add parameter `effort: str = "medium"` to `run_review` and the CLI option `--effort {low,medium,high,none}` (default medium). In the REAL path (caller is None), after loading draft_source and applying with_idle_timeout, wrap `ds._stream_once` so that the request body gets `"chat_template_kwargs": {"enable_thinking": true}` and, unless effort == 'none', `"reasoning_effort": effort` (never overwriting model, messages, stream, max_tokens, temperature; do not depend on the model name: apply to whatever model is used). Expose the pure helper `apply_review_profile(body: dict, effort: str) -> dict` returning a COPY with those fields merged (effort 'none' omits reasoning_effort; an unknown effort value is treated as 'medium'). The returned dict of run_review gets two more keys `effort` and `thinking` (True). Tests: apply_review_profile cases (medium, none, unknown value, protected keys not overwritten, input not mutated); run_review with a fake caller records effort in the result; the CLI default is medium (check via argparse parse helper or main with a monkeypatched run_review). Keep all existing tests.

## CURRENT scripts/source/review_run.py
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
        name = f_resolved.name
        if "secrets" in name or name.endswith(".env") or name.endswith(".key"):
            problems.append(f"skipped {f}: secret-like name")
            continue

        try:
            content = f_resolved.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            problems.append(f"skipped {f}: not text")
            continue

        # Indent content by one space so that content lines don't start with backticks
        # This avoids false positives in fence detection heuristics
        indented_content = "\n".join(" " + line for line in content.splitlines())

        rel_posix = rel.as_posix()
        header = f"## FILE {rel_posix}"
        header_bytes = header.encode("utf-8")
        content_bytes = indented_content.encode("utf-8")

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
            overhead = (
                len(header_bytes)
                + len(newline)
                + len(fence_bytes)
                + len(newline)
                + len(fence_bytes)
                + len(newline) * 2
            )
            avail = remaining - overhead
            if avail > 0:
                # Truncate the indented content bytes
                truncated_indented = content_bytes[:avail].decode("utf-8", errors="ignore")
                # Add [truncated] line and ensure it's indented
                truncated_indented += "\n[truncated]"
                truncated_indented = "\n".join(
                    " " + line if not line.startswith(" ") else line
                    for line in truncated_indented.splitlines()
                )
                parts.append(header)
                parts.append(fence)
                parts.append(truncated_indented)
                parts.append(fence)
                used += (
                    len(header_bytes)
                    + len(newline)
                    + len(fence_bytes)
                    + len(newline)
                    + len(truncated_indented.encode("utf-8"))
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
        parts.append(indented_content)
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
            verdict = line.split(":", 1)[1].strip()
            break

    out_path.parent.mkdir(parents=True, exist_ok=True)

    if info.get("status") == 200 and reply_text.strip():
        out_path.write_text(reply_text, encoding="utf-8")
    else:
        error_msg = info.get("error", "unknown error")
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
    return 0 if result["status"] == 200 else 1


if __name__ == "__main__":
    raise SystemExit(main())
```
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


class TestModuleHygiene:
    def test_no_nvapi_literal(self):
        source = (SRC_ROOT / "review_run.py").read_text(encoding="utf-8")
        assert "nvapi-" not in source

    def test_no_kimi_adapter_import(self):
        source = (SRC_ROOT / "review_run.py").read_text(encoding="utf-8")
        assert "kimi_adapter" not in source
```
Reply with exactly two FILE blocks: FILE: scripts/source/review_run.py and FILE: tests/test_review_run.py
