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
        root=tmp_path,
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


def test_run_codex_review_secrets_skipped(tmp_path_factory):
    # The temp directory name must NOT contain "secrets" because build_prompt
    # (in review_run.py) treats ANY path component containing "secrets"
    # (case-insensitive) as a secret path and skips the file. The test function
    # name contains "secrets", so pytest's tmp_path would include it. We use
    # tmp_path_factory with a neutral prefix to avoid this.
    base = tmp_path_factory.mktemp("rcr")  # dir name like "rcr0", no "secrets"

    prompt_file = base / "prompt.txt"
    prompt_file.write_text("Review.")
    out_path = base / "report.md"
    secret_dir = base / ".secrets"
    secret_dir.mkdir()
    secret_file = secret_dir / "secret.txt"
    secret_content = "SUPER_SECRET"
    secret_file.write_text(secret_content, encoding="utf-8")
    normal_file = base / "normal.py"
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
        root=base,
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
