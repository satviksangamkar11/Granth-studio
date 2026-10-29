# TASK: return ONLY ONE FILE: tests/test_codex_review.py (complete). Reply with exactly one block `FILE: tests/test_codex_review.py` then the python fenced. OPINION OF THE SUPERVISOR after three failed rounds: the MODULE is correct. The failing test test_run_codex_review_secrets_skipped calls `run_codex_review(prompt_file, [normal_file, secret_file], out_path, runner=fake_runner)` WITHOUT `root=tmp_path`, so the default root (the repo) makes both tmp files count as outside the root and they are skipped (hence the normal file text `print(ok)` is absent from the runner input). FIX: pass `root=tmp_path` in that call, and in the same test assert that the normal file text IS in the captured input and the secret text `SUPER_SECRET` is NOT. Check every other test that passes files for the same missing `root=`. Keep all other tests. Never write any word related to 3D animation software.
## CURRENT tests/test_codex_review.py
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


def test_run_codex_review_secrets_skipped(tmp_path):
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
        root=tmp_path,
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
## scripts/source/codex_review.py (reference only)
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


def _filter_secret_files(files: List[Path], root: Path) -> List[Path]:
    """Remove files that live under a secret directory (e.g., .secrets, secrets)."""
    secret_dirs = {".secrets", "secrets"}
    filtered = []
    for f in files:
        try:
            rel = f.relative_to(root)
        except ValueError:
            # File not under root; keep it (build_prompt will handle or ignore)
            filtered.append(f)
            continue
        # Check parent directories (excluding the file name itself)
        if any(part in secret_dirs for part in rel.parts[:-1]):
            continue
        filtered.append(f)
    return filtered


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

    # Filter out secret files before building the prompt
    files = _filter_secret_files(files, root)

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
