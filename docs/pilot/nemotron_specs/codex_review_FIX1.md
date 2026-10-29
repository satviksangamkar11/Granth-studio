# FIX CALL: return BOTH files in full: `scripts/source/codex_review.py` and `tests/test_codex_review.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
...............F.....                                                    [100%]
================================== FAILURES ===================================
____________________ test_run_codex_review_secrets_skipped ____________________
tests\test_codex_review.py:222: in test_run_codex_review_secrets_skipped
    assert "print('ok')" in captured_input["text"]
E   assert "print('ok')" in 'Review.'
=========================== short test summary info ===========================
FAILED tests/test_codex_review.py::test_run_codex_review_secrets_skipped - as...
1 failed, 20 passed in 0.50s

```

## SPEC
# SPEC: NEW `scripts/source/codex_review.py` + NEW `tests/test_codex_review.py`. Return exactly these TWO files in full; do not output or change any other file.
Purpose: run the Codex command line (model `gpt-6-luna`, reasoning effort high, READ-ONLY sandbox) as a reviewer with the same interface idea as `scripts/source/review_run.py`. Standard library only; `from __future__ import annotations`; nothing at import time except imports and definitions; no key or secret is ever handled (Codex uses its own login). Never write any word related to 3D animation software.
## Existing code (load by importlib BY PATH, do not modify)
`scripts/source/review_run.py`: `build_prompt(prompt_text: str, files: list[Path], root: Path, max_total_bytes: int = 400000) -> tuple[str, list[str]]` (the user text with the files embedded, and problems) and `run_review(...)` for the verdict rule: the verdict is read from the LAST line starting `## Verdict:`; exactly `READY`, `FIX FIRST` or `NONE`.
Repo root in this module: `Path(__file__).resolve().parents[2]`; in tests `parents[1]`.
## API
- `DEFAULT_MODEL = "gpt-6-luna"`, `DEFAULT_EFFORT = "high"`.
- `codex_command(model: str, effort: str, out_path: Path) -> list[str]`: `["codex", "exec", "--sandbox", "read-only", "--skip-git-repo-check", "-m", model, "-c", f"model_reasoning_effort={effort}", "-o", str(out_path), "-"]` (the prompt is sent on stdin through the final `-`).
- `parse_verdict(text: str) -> str`: last `## Verdict:` line (strip, case-insensitive) -> `READY`, `FIX FIRST` or `NONE`.
- `run_codex_review(prompt_file: Path, files: list[Path], out_path: Path, *, root: Path | None = None, model: str = DEFAULT_MODEL, effort: str = DEFAULT_EFFORT, timeout_s: int = 1800, runner=None) -> dict`: builds the text with `build_prompt` (reading the prompt file text; a missing prompt file -> returns the dict with `status: "refused"`, verdict `NONE`), REFUSES (`FileExistsError`) if `out_path` exists, runs `runner(cmd: list[str], input_text: str, timeout_s: int) -> tuple[int, str]` (default: `subprocess.run(cmd, input=input_text, capture_output=True, text=True, encoding="utf-8", timeout=timeout_s)` returning `(returncode, stdout + stderr)`; a timeout or an OSError (codex not installed) returns `(1, "<reason>")`), then reads the report from `out_path` (written by codex); if the file is missing or empty the result is `status: "failed"`, verdict `NONE`, and a small file `REVIEW FAILED: <reason>` is written. Returns `{"model","effort","out","status": "ok"|"failed"|"refused","verdict","problems","chars"}`. Never raises for tool problems.
- `main(argv=None) -> int`: `--prompt-file`, `--file` (repeatable), `--out` required; `--model`, `--effort`, `--timeout-s`; prints ONE line `codex-review: status=<s> verdict=<V> out=<path>`; returns 0 for ok, 1 for failed, 2 for refused or an existing out file.
## Tests (`tests/test_codex_review.py`; offline, fake runner, no codex needed)
codex_command exact list; parse_verdict cases (READY, FIX FIRST, none, unknown, lower case, last line wins); run_codex_review with a fake runner that writes a report ending in each verdict into out_path, a runner that returns a failure with no file (FAILED file + verdict NONE), a timeout reason, an existing out file (FileExistsError, file unchanged), a missing prompt file, secrets-path files skipped through build_prompt (assert the secret text never reaches the runner input); main return codes and the one-line output (capsys); the module source has no import of `kimi_adapter`.
Reply with only the two FILE blocks:
FILE: scripts/source/codex_review.py
FILE: tests/test_codex_review.py


## CURRENT MODULE scripts/source/codex_review.py
```python
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from typing import Callable, Optional, Tuple, List, Dict, Any

DEFAULT_MODEL = "gpt-6-luna"
DEFAULT_EFFORT = "high"

# Load build_prompt from review_run.py by path
_REVIEW_RUN_PATH = Path(__file__).resolve().parents[2] / "scripts" / "source" / "review_run.py"
_spec = importlib.util.spec_from_file_location("review_run", _REVIEW_RUN_PATH)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Cannot load review_run from {_REVIEW_RUN_PATH}")
_review_run = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_review_run)
build_prompt = _review_run.build_prompt  # type: ignore[attr-defined]


def codex_command(model: str, effort: str, out_path: Path) -> List[str]:
    return [
        "codex",
        "exec",
        "--sandbox",
        "read-only",
        "--skip-git-repo-check",
        "-m",
        model,
        "-c",
        f"model_reasoning_effort={effort}",
        "-o",
        str(out_path),
        "-",
    ]


def parse_verdict(text: str) -> str:
    verdict = "NONE"
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("## verdict:"):
            value = stripped.split(":", 1)[1].strip().upper()
            if value in {"READY", "FIX FIRST", "NONE"}:
                verdict = value
    return verdict


def _default_runner(cmd: List[str], input_text: str, timeout_s: int) -> Tuple[int, str]:
    import subprocess
    try:
        result = subprocess.run(
            cmd,
            input=input_text,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout_s,
        )
        return result.returncode, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return 1, "timeout"
    except OSError as e:
        return 1, f"OSError: {e}"


def run_codex_review(
    prompt_file: Path,
    files: List[Path],
    out_path: Path,
    *,
    root: Optional[Path] = None,
    model: str = DEFAULT_MODEL,
    effort: str = DEFAULT_EFFORT,
    timeout_s: int = 1800,
    runner: Optional[Callable[[List[str], str, int], Tuple[int, str]]] = None,
) -> Dict[str, Any]:
    if out_path.exists():
        raise FileExistsError(f"Output file already exists: {out_path}")

    if not prompt_file.is_file():
        return {
            "model": model,
            "effort": effort,
            "out": str(out_path),
            "status": "refused",
            "verdict": "NONE",
            "problems": [],
            "chars": 0,
        }

    prompt_text = prompt_file.read_text(encoding="utf-8")
    if root is None:
        root = Path(__file__).resolve().parents[2]

    built_text, problems = build_prompt(prompt_text, files, root, max_total_bytes=400000)
    chars = len(built_text)

    cmd = codex_command(model, effort, out_path)
    run_fn = runner or _default_runner
    returncode, output = run_fn(cmd, built_text, timeout_s)

    # Read the report written by codex
    if out_path.is_file() and out_path.stat().st_size > 0:
        report_text = out_path.read_text(encoding="utf-8")
        verdict = parse_verdict(report_text)
        return {
            "model": model,
            "effort": effort,
            "out": str(out_path),
            "status": "ok",
            "verdict": verdict,
            "problems": problems,
            "chars": chars,
        }
    else:
        reason = output.strip() if output.strip() else "empty or missing report"
        out_path.write_text(f"REVIEW FAILED: {reason}", encoding="utf-8")
        return {
            "model": model,
            "effort": effort,
            "out": str(out_path),
            "status": "failed",
            "verdict": "NONE",
            "problems": problems,
            "chars": chars,
        }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="codex-review")
    parser.add_argument("--prompt-file", type=Path, required=True)
    parser.add_argument("--file", type=Path, action="append", default=[])
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL)
    parser.add_argument("--effort", type=str, default=DEFAULT_EFFORT)
    parser.add_argument("--timeout-s", type=int, default=1800)
    args = parser.parse_args(argv)

    try:
        result = run_codex_review(
            prompt_file=args.prompt_file,
            files=args.file,
            out_path=args.out,
            model=args.model,
            effort=args.effort,
            timeout_s=args.timeout_s,
        )
    except FileExistsError:
        print(f"codex-review: status=refused verdict=NONE out={args.out}")
        return 2

    status = result["status"]
    verdict = result["verdict"]
    out = result["out"]
    print(f"codex-review: status={status} verdict={verdict} out={out}")

    if status == "ok":
        return 0
    elif status == "failed":
        return 1
    else:  # refused
        return 2


if __name__ == "__main__":
    sys.exit(main())

```

## CURRENT TESTS tests/test_codex_review.py
```python
import sys
from pathlib import Path
import pytest

# Ensure the source module can be imported
SRC_DIR = Path(__file__).resolve().parents[1] / "scripts" / "source"
sys.path.insert(0, str(SRC_DIR))

import codex_review


def test_codex_command_exact_list():
    out_path = Path("/tmp/report.md")
    cmd = codex_review.codex_command("gpt-6-luna", "high", out_path)
    expected = [
        "codex",
        "exec",
        "--sandbox",
        "read-only",
        "--skip-git-repo-check",
        "-m",
        "gpt-6-luna",
        "-c",
        "model_reasoning_effort=high",
        "-o",
        str(out_path),
        "-",
    ]
    assert cmd == expected


@pytest.mark.parametrize("text,expected", [
    ("## Verdict: READY\n", "READY"),
    ("## Verdict: FIX FIRST\n", "FIX FIRST"),
    ("## Verdict: NONE\n", "NONE"),
    ("no verdict here", "NONE"),
    ("## Verdict: UNKNOWN\n", "NONE"),
    ("## verdict: ready\n", "READY"),
    ("## Verdict: READY\n## Verdict: FIX FIRST\n", "FIX FIRST"),
])
def test_parse_verdict(text, expected):
    assert codex_review.parse_verdict(text) == expected


def test_run_codex_review_ok_with_fake_runner(tmp_path):
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("Review this code.")
    out_path = tmp_path / "report.md"
    files = [tmp_path / "a.py"]
    files[0].write_text("print('hello')")

    def fake_runner(cmd, input_text, timeout_s):
        # Write a report with a verdict
        out_path.write_text("Some analysis\n## Verdict: READY\n", encoding="utf-8")
        return 0, "ok"

    result = codex_review.run_codex_review(
        prompt_file=prompt_file,
        files=files,
        out_path=out_path,
        runner=fake_runner,
    )
    assert result["status"] == "ok"
    assert result["verdict"] == "READY"
    assert result["out"] == str(out_path)
    assert result["model"] == codex_review.DEFAULT_MODEL
    assert result["effort"] == codex_review.DEFAULT_EFFORT
    assert isinstance(result["problems"], list)
    assert result["chars"] > 0


def test_run_codex_review_fix_first_verdict(tmp_path):
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("Review.")
    out_path = tmp_path / "report.md"
    files = []

    def fake_runner(cmd, input_text, timeout_s):
        out_path.write_text("## Verdict: FIX FIRST\n", encoding="utf-8")
        return 0, "ok"

    result = codex_review.run_codex_review(
        prompt_file=prompt_file,
        files=files,
        out_path=out_path,
        runner=fake_runner,
    )
    assert result["status"] == "ok"
    assert result["verdict"] == "FIX FIRST"


def test_run_codex_review_none_verdict(tmp_path):
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("Review.")
    out_path = tmp_path / "report.md"

    def fake_runner(cmd, input_text, timeout_s):
        out_path.write_text("No verdict line.\n", encoding="utf-8")
        return 0, "ok"

    result = codex_review.run_codex_review(
        prompt_file=prompt_file,
        files=[],
        out_path=out_path,
        runner=fake_runner,
    )
    assert result["status"] == "ok"
    assert result["verdict"] == "NONE"


def test_run_codex_review_failed_missing_report(tmp_path):
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("Review.")
    out_path = tmp_path / "report.md"

    def fake_runner(cmd, input_text, timeout_s):
        # Do not write the report file
        return 1, "codex crashed"

    result = codex_review.run_codex_review(
        prompt_file=prompt_file,
        files=[],
        out_path=out_path,
        runner=fake_runner,
    )
    assert result["status"] == "failed"
    assert result["verdict"] == "NONE"
    # Check that a failure file was written
    assert out_path.is_file()
    content = out_path.read_text(encoding="utf-8")
    assert content.startswith("REVIEW FAILED:")


def test_run_codex_review_timeout_reason(tmp_path):
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("Review.")
    out_path = tmp_path / "report.md"

    def fake_runner(cmd, input_text, timeout_s):
        raise TimeoutError("timeout")

    # The default runner catches TimeoutExpired and returns (1, "timeout")
    # But we can also test with a runner that returns timeout reason
    def fake_runner2(cmd, input_text, timeout_s):
        return 1, "timeout"

    result = codex_review.run_codex_review(
        prompt_file=prompt_file,
        files=[],
        out_path=out_path,
        runner=fake_runner2,
    )
    assert result["status"] == "failed"
    assert result["verdict"] == "NONE"
    content = out_path.read_text(encoding="utf-8")
    assert "REVIEW FAILED: timeout" in content


def test_run_codex_review_existing_out_file_raises(tmp_path):
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("Review.")
    out_path = tmp_path / "report.md"
    out_path.write_text("existing", encoding="utf-8")

    with pytest.raises(FileExistsError):
        codex_review.run_codex_review(
            prompt_file=prompt_file,
            files=[],
            out_path=out_path,
        )
    # Ensure file unchanged
    assert out_path.read_text(encoding="utf-8") == "existing"


def test_run_codex_review_missing_prompt_file(tmp_path):
    prompt_file = tmp_path / "missing.txt"
    out_path = tmp_path / "report.md"

    result = codex_review.run_codex_review(
        prompt_file=prompt_file,
        files=[],
        out_path=out_path,
    )
    assert result["status"] == "refused"
    assert result["verdict"] == "NONE"
    assert not out_path.exists()


def test_run_codex_review_secrets_skipped(tmp_path, monkeypatch):
    # We need to ensure that build_prompt skips secret files.
    # Since we cannot modify review_run.py, we rely on its behavior.
    # We'll create a file under a path that build_prompt considers secret (e.g., .secrets/secret.txt)
    # and assert that its content never reaches the runner input.
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("Review.")
    out_path = tmp_path / "report.md"
    secret_dir = tmp_path / ".secrets"
    secret_dir.mkdir()
    secret_file = secret_dir / "secret.txt"
    secret_content = "SUPER_SECRET"
    secret_file.write_text(secret_content, encoding="utf-8")
    normal_file = tmp_path / "normal.py"
    normal_file.write_text("print('ok')", encoding="utf-8")

    captured_input = {}

    def fake_runner(cmd, input_text, timeout_s):
        captured_input["text"] = input_text
        out_path.write_text("## Verdict: READY\n", encoding="utf-8")
        return 0, "ok"

    result = codex_review.run_codex_review(
        prompt_file=prompt_file,
        files=[secret_file, normal_file],
        out_path=out_path,
        runner=fake_runner,
    )
    assert result["status"] == "ok"
    # The secret content should not appear in the input to the runner
    assert secret_content not in captured_input["text"]
    # The normal file content should appear
    assert "print('ok')" in captured_input["text"]


def test_main_ok(capsys, tmp_path):
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("Review.")
    out_path = tmp_path / "report.md"

    def fake_runner(cmd, input_text, timeout_s):
        out_path.write_text("## Verdict: READY\n", encoding="utf-8")
        return 0, "ok"

    # We need to monkey-patch the runner used by main. Since main calls run_codex_review without a runner,
    # we can't directly inject. But we can monkey-patch codex_review._default_runner.
    import codex_review as cr
    original_runner = cr._default_runner
    cr._default_runner = fake_runner
    try:
        ret = cr.main([
            "--prompt-file", str(prompt_file),
            "--out", str(out_path),
        ])
    finally:
        cr._default_runner = original_runner

    assert ret == 0
    captured = capsys.readouterr()
    assert "codex-review: status=ok verdict=READY out=" in captured.out


def test_main_failed(capsys, tmp_path):
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("Review.")
    out_path = tmp_path / "report.md"

    def fake_runner(cmd, input_text, timeout_s):
        # No report written
        return 1, "error"

    import codex_review as cr
    original_runner = cr._default_runner
    cr._default_runner = fake_runner
    try:
        ret = cr.main([
            "--prompt-file", str(prompt_file),
            "--out", str(out_path),
        ])
    finally:
        cr._default_runner = original_runner

    assert ret == 1
    captured = capsys.readouterr()
    assert "codex-review: status=failed verdict=NONE out=" in captured.out


def test_main_refused_missing_prompt(capsys, tmp_path):
    prompt_file = tmp_path / "missing.txt"
    out_path = tmp_path / "report.md"

    import codex_review as cr
    ret = cr.main([
        "--prompt-file", str(prompt_file),
        "--out", str(out_path),
    ])
    assert ret == 2
    captured = capsys.readouterr()
    assert "codex-review: status=refused verdict=NONE out=" in captured.out


def test_main_existing_out_file(capsys, tmp_path):
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("Review.")
    out_path = tmp_path / "report.md"
    out_path.write_text("existing", encoding="utf-8")

    import codex_review as cr
    ret = cr.main([
        "--prompt-file", str(prompt_file),
        "--out", str(out_path),
    ])
    assert ret == 2
    captured = capsys.readouterr()
    assert "codex-review: status=refused verdict=NONE out=" in captured.out
    # File unchanged
    assert out_path.read_text(encoding="utf-8") == "existing"


def test_no_kimi_adapter_import():
    # Ensure the module does not import kimi_adapter
    import codex_review
    assert not hasattr(codex_review, "kimi_adapter")
    # Also check that the module's globals don't contain it
    assert "kimi_adapter" not in codex_review.__dict__

```

## NOTE
One test fails (test_run_codex_review_secrets_skipped, output above). Decide from the SPEC (a file under a secrets path is skipped by review_run.build_prompt so its text never reaches the runner input): fix the test or module. Return BOTH complete FILE blocks. Never write any word related to 3D animation software.
