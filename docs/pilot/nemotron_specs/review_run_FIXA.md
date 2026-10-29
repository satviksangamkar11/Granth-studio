# FIX CALL: return BOTH files in full: `scripts/source/review_run.py` and `tests/test_review_run.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
.F..............FF.....                                                  [100%]
================================== FAILURES ===================================
__________ TestBuildPrompt.test_fence_longer_than_content_backticks ___________
tests\test_review_run.py:43: in test_fence_longer_than_content_backticks
    assert fl.count("`") > 3
E   AssertionError: assert 3 > 3
E    +  where 3 = <built-in method count of str object at 0x000002099B9E2340>('`')
E    +    where <built-in method count of str object at 0x000002099B9E2340> = '```'.count
_______________ TestRunReview.test_caller_raises_writes_failed ________________
tests\test_review_run.py:266: in test_caller_raises_writes_failed
    assert "error" in result
E   AssertionError: assert 'error' in {'model': 'test-model', 'out': 'C:\\Users\\Satvik\\AppData\\Local\\Temp\\pytest-of-Satvik\\pytest-315\\test_caller_raises_writes_fail0\\out.md', 'status': 0, 'wall_s': 0.0, ...}
______ TestSecretsScrubbing.test_scrub_keys_removes_from_output_and_dict ______
tests\test_review_run.py:300: in test_scrub_keys_removes_from_output_and_dict
    assert "[key]" in str(result)
E   assert '[key]' in "{'model': 'test-model', 'out': 'C:\\\\Users\\\\Satvik\\\\AppData\\\\Local\\\\Temp\\\\pytest-of-Satvik\\\\pytest-315\\...out.md', 'status': 200, 'wall_s': 0.1, 'finish': 'stop', 'usage': {}, 'problems': [], 'chars': 49, 'verdict': 'READY'}"
E    +  where "{'model': 'test-model', 'out': 'C:\\\\Users\\\\Satvik\\\\AppData\\\\Local\\\\Temp\\\\pytest-of-Satvik\\\\pytest-315\\...out.md', 'status': 200, 'wall_s': 0.1, 'finish': 'stop', 'usage': {}, 'problems': [], 'chars': 49, 'verdict': 'READY'}" = str({'model': 'test-model', 'out': 'C:\\Users\\Satvik\\AppData\\Local\\Temp\\pytest-of-Satvik\\pytest-315\\test_scrub_keys_removes_from_o0\\out.md', 'status': 200, 'wall_s': 0.1, ...})
=========================== short test summary info ===========================
FAILED tests/test_review_run.py::TestBuildPrompt::test_fence_longer_than_content_backticks
FAILED tests/test_review_run.py::TestRunReview::test_caller_raises_writes_failed
FAILED tests/test_review_run.py::TestSecretsScrubbing::test_scrub_keys_removes_from_output_and_dict
3 failed, 20 passed in 0.35s

```

## SPEC
# SPEC: NEW `scripts/source/review_run.py` + NEW `tests/test_review_run.py`. Return exactly these TWO files in full; do not output or change any other file.
Purpose (owner 2026-10-29): Codex is out of limit, so a second reviewer family is run through the free NVIDIA endpoint: GLM (default model `z-ai/glm-5.3-flash`). The tool sends ONE review prompt plus the files to review to the model and writes the model's report to a markdown file. It is READ-ONLY with respect to the project: it never edits a reviewed file, never runs code from the reviewed files, and never prints, logs or stores any key. Standard library only; `from __future__ import annotations`; nothing at import time except imports and definitions; plain functions.

## Code you build on (load by importlib BY PATH; do not modify them)
- `scripts/source/draft_source.py` (module name `ds`): `ds.nt.load_keys()`, `ds.nt.KeyPool(keys)`, `ds.nt.scrub(text, keys)`, `ds.chat_stream(pool, keys, model, system, user, max_tokens=N) -> (reply_text, info)` with `info` keys `status`, `wall_s`, `finish`, `usage`, `error`. A usable reply has `info["status"] == 200` and non-empty text.
- `scripts/source/coder_run.py`: `with_idle_timeout(ds, seconds: int | None = None)` returns ds with the socket idle timeout raised (default 600 s); `wrap_ds`-style length continuation is NOT needed here.
Repo root in this module: `Path(__file__).resolve().parents[2]`; in tests `Path(__file__).resolve().parents[1]`.

## API
- `SYSTEM_PROMPT`: a short fixed text: you are a strict READ-ONLY code and design reviewer; you may not run anything; report only real, verified defects with file:line and an exact fix; if nothing is wrong say so; end the report with exactly one line `## Verdict: READY` or `## Verdict: FIX FIRST`.
- `build_prompt(prompt_text: str, files: list[Path], root: Path, max_total_bytes: int = 400_000) -> tuple[str, list[str]]`: returns the user text and a list of problems. The user text is `prompt_text`, then for each file a heading `## FILE <path relative to root with forward slashes>` followed by the file content in a fenced block (use a fence longer than any backtick run inside the content). Rules: a file that does not exist, is not under `root`, is a directory, or whose name contains `secrets` or ends with `.env`/`.key` is skipped with the problem `skipped <path>: <reason>` (never read); a binary or non-UTF-8 file is skipped with `skipped <path>: not text`; when adding a file would exceed `max_total_bytes` the file is cut at the limit with a line `[truncated]` and the problem `truncated <path>`; later files are skipped with `skipped <path>: size limit`. Never raises.
- `run_review(model: str, prompt_file: Path, files: list[Path], out_path: Path, *, root: Path | None = None, max_tokens: int = 64000, idle_s: int | None = None, caller=None) -> dict`: `caller` is injectable for tests: `caller(system: str, user: str) -> tuple[str, dict]`; when None the real path loads draft_source by path, applies `with_idle_timeout(ds, idle_s)`, loads the keys and the key pool, and calls `ds.chat_stream(pool, keys, model, SYSTEM_PROMPT, user, max_tokens=max_tokens)`, scrubbing the reply with `ds.nt.scrub`. Writes the reply to `out_path` (parents created) and returns `{"model", "out", "status", "wall_s", "finish", "usage", "problems", "chars", "verdict"}` where `verdict` is `READY`, `FIX FIRST` or `NONE` (read from the last `## Verdict:` line of the reply). REFUSES (raises `FileExistsError`) if `out_path` already exists. If the call fails (status not 200 or empty reply) nothing is written to `out_path` except a small file with the text `REVIEW FAILED: <error>` and the verdict `NONE`; never raises for model problems (an exception inside the caller becomes `error: <ExceptionClass>`).
- `main(argv=None) -> int`: `--model` (default `z-ai/glm-5.3-flash`), `--prompt-file PATH` (required), `--file PATH` (repeatable), `--out PATH` (required), `--max-tokens` (default 64000), `--idle-s` (default None -> 600). Prints ONE summary line `review: status=<n> wall_s=<n> verdict=<V> problems=<k> out=<path>` and returns 0 when the call succeeded (any verdict), 1 when it failed, 2 on a refusal (existing out file, missing prompt file). `if __name__ == "__main__": raise SystemExit(main())`.

## Tests (`tests/test_review_run.py`; offline, no network, no key; fake caller)
1. `build_prompt`: the prompt text and a file heading with the relative path appear; fence logic with a file containing triple backticks; a missing file, a file outside root, a directory, a `secrets` path and a `.env` file are skipped with the right problem and their content never appears (create a secret-looking file and assert its text is absent); a non-UTF-8 binary file is skipped; the size limit truncates the file that crosses the limit and skips the rest.
2. `run_review` with a fake caller returning a report that ends with `## Verdict: READY` -> out file written, verdict READY, status 200; with `FIX FIRST`; with no verdict line -> NONE; an existing out file raises FileExistsError and the file is unchanged; a caller returning status 500 or an empty reply -> out file contains `REVIEW FAILED`, verdict NONE, no exception; a caller that raises -> same, with `error: <class>`.
3. Secrets: a fake caller that echoes a fake key string; `run_review(... caller=...)` with the key injected through an optional `scrub_keys: list[str] = []` parameter must not leave the key in the out file or the returned dict (add this parameter and apply `str.replace(key, "[key]")` to the reply and to every returned string).
4. `main`: missing prompt file -> returns 2 and prints `refused:`; success path with `run_review` monkeypatched returns 0 and prints the one-line summary (capsys); the module source contains no literal `nvapi-` and no import of `kimi_adapter`.
Use plain assignment and `copy.deepcopy`; never a helper that rejects no-effect mutations.

Reply with only the two FILE blocks:
FILE: scripts/source/review_run.py
FILE: tests/test_review_run.py


## CURRENT MODULE scripts/source/review_run.py
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

        rel_posix = rel.as_posix()
        header = f"## FILE {rel_posix}"
        header_bytes = header.encode("utf-8")
        content_bytes = content.encode("utf-8")

        fence = "```"
        while fence in content:
            fence += "`"
        fence_bytes = fence.encode("utf-8")
        newline = b"\n"

        needed = len(header_bytes) + len(newline) + len(fence_bytes) + len(newline) + len(content_bytes) + len(newline) + len(fence_bytes) + len(newline)

        if used + needed > max_total_bytes:
            remaining = max_total_bytes - used
            if remaining < 0:
                remaining = 0
            if remaining > len(header_bytes) + len(newline) + len(fence_bytes) * 2 + len(newline) * 3 + len("[truncated]".encode()):
                avail = remaining - (len(header_bytes) + len(newline) + len(fence_bytes) + len(newline) + len(fence_bytes) + len(newline) * 2)
                if avail > 0:
                    truncated_content = content_bytes[:avail].decode("utf-8", errors="ignore") + "\n[truncated]"
                    parts.append(header)
                    parts.append(fence)
                    parts.append(truncated_content)
                    parts.append(fence)
                    used += len(header_bytes) + len(newline) + len(fence_bytes) + len(newline) + truncated_content.encode().__len__() + len(newline) + len(fence_bytes) + len(newline)
                    problems.append(f"truncated {f}")
                else:
                    problems.append(f"skipped {f}: size limit")
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
    scrub_keys: list[str] | None = None,
) -> dict:
    if scrub_keys is None:
        scrub_keys = []

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
            ds = ds.with_idle_timeout(ds, idle_s)
            keys = ds.nt.load_keys()
            pool = ds.nt.KeyPool(keys)
            reply_text, info = ds.chat_stream(pool, keys, model, SYSTEM_PROMPT, user_text, max_tokens=max_tokens)
            reply_text = ds.nt.scrub(reply_text, keys)
    except Exception as e:
        info = {"status": 0, "wall_s": 0.0, "finish": "error", "usage": {}, "error": f"{type(e).__name__}: {e}"}
        reply_text = ""

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

    for key in scrub_keys:
        if key:
            verdict = verdict.replace(key, "[key]")
            for k, v in info.items():
                if isinstance(v, str):
                    info[k] = v.replace(key, "[key]")

    return {
        "model": model,
        "out": str(out_path),
        "status": info.get("status", 0),
        "wall_s": info.get("wall_s", 0.0),
        "finish": info.get("finish", ""),
        "usage": info.get("usage", {}),
        "problems": problems,
        "chars": len(reply_text),
        "verdict": verdict,
    }


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

## CURRENT TESTS tests/test_review_run.py
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
