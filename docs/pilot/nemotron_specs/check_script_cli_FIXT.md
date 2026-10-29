# TASK: return ONLY ONE FILE: tests/test_check_script_cli.py (complete). Reply with exactly one block `FILE: tests/test_check_script_cli.py` then the python fenced. The module is CORRECT (verified by hand: on the tiny fixture it returns errors [] and problems ['presets: missing']). ONE test fails: test_main_output_and_return_codes expects '... 0 errors, 0 problems' but gets '... 1 problems' because the synthetic repo has NO preset index, so the context builder adds the problem `presets: missing`. FIX THE TEST FIXTURE: in the happy-path tmp root also write `assets/v5_presets/index.json` containing `[{"preset": "p1", "use": "x", "assets": [], "simplest_renderer": "motion"}]` (a JSON list) so that no context problem remains; keep the voice library with a narrator voice. Then assert the happy path (`run_check` ok True, problems == [], `main` output line with `0 errors, 0 problems`, return 0). Also add one isolated test that WITHOUT the preset index `run_check` still reports errors [] and the problem `presets: missing` and `ok` follows the module's behaviour (assert what the module does: check its code). Never write the word blender. Keep all other tests.

## CURRENT tests/test_check_script_cli.py
```python
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Ensure the pipeline scripts are importable
_REPO_ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS_DIR = _REPO_ROOT / "scripts" / "pipeline"
sys.path.insert(0, str(_SCRIPTS_DIR))

import check_script_cli  # type: ignore


def _make_synthetic_root(tmp_path: Path) -> Path:
    """Create a synthetic adhyay 2 structure under tmp_path."""
    root = tmp_path
    # canon/adhyay_02/source/ovis.jsonl
    ovis_dir = root / "canon" / "adhyay_02" / "source"
    ovis_dir.mkdir(parents=True)
    ovis_lines = "\n".join(json.dumps({"ovi": n}) for n in range(1, 5))
    (ovis_dir / "ovis.jsonl").write_text(ovis_lines + "\n", encoding="utf-8")

    # canon/adhyay_02/script/easy.md (REAL EASY format)
    script_dir = root / "canon" / "adhyay_02" / "script"
    script_dir.mkdir(parents=True)
    easy_md = (
        "## S1\n"
        "**S1-L1** | narrator | ovi 1 | core\n"
        "- Marathi: नमस्कार मित्रांनो\n"
        "- Hindi: नमस्ते दोस्तों\n"
        "\n"
        "**S1-L2** | narrator | ovi 2 | core\n"
        "- Marathi: आपण कसे आहात\n"
        "- Hindi: आप कैसे हैं\n"
        "\n"
        "## S2\n"
        "**S2-L1** | narrator | ovi 3 | core\n"
        "- Marathi: आज हवा चांगली आहे\n"
        "- Hindi: आज मौसम अच्छा है\n"
        "\n"
        "**S2-L2** | narrator | ovi 4 | core\n"
        "- Marathi: धन्यवाद\n"
        "- Hindi: धन्यवाद\n"
        "\n"
    )
    (script_dir / "easy.md").write_text(easy_md, encoding="utf-8")

    # canon/series/voices.json
    series_dir = root / "canon" / "series"
    series_dir.mkdir(parents=True)
    voices_json = json.dumps({"voices": [{"voice_key": "narrator", "voice_id": "id1"}]})
    (series_dir / "voices.json").write_text(voices_json, encoding="utf-8")

    # stage1 directory with saved_voices.json and unfilmed_ovis.json
    stage1_dir = root / "canon" / "adhyay_02" / "stage1"
    stage1_dir.mkdir(parents=True)
    (stage1_dir / "saved_voices.json").write_text("{}", encoding="utf-8")
    (stage1_dir / "unfilmed_ovis.json").write_text("[]", encoding="utf-8")

    return root


def test_happy_path(tmp_path: Path):
    root = _make_synthetic_root(tmp_path)
    result = check_script_cli.run_check(2, root)
    assert result["adhyay"] == 2
    assert result["lines"] == 4
    assert result["scenes"] == 2
    assert result["core"] == 4
    assert result["optional"] == 0
    assert result["errors"] == []
    assert result["ok"] is True
    # script_sha256 matches
    script_path = root / "canon" / "adhyay_02" / "script" / "easy.md"
    text = script_path.read_text(encoding="utf-8")
    assert result["script_sha256"] == check_script_cli.script_sha256(text)


def test_duplicate_line_id(tmp_path: Path):
    root = _make_synthetic_root(tmp_path)
    script_path = root / "canon" / "adhyay_02" / "script" / "easy.md"
    text = script_path.read_text(encoding="utf-8")
    # Duplicate S1-L1 exactly
    text += (
        "**S1-L1** | narrator | ovi 1 | core\n"
        "- Marathi: नमस्कार मित्रांनो\n"
        "- Hindi: नमस्ते दोस्तों\n"
        "\n"
    )
    script_path.write_text(text, encoding="utf-8")
    result = check_script_cli.run_check(2, root)
    assert result["ok"] is False
    assert any("S1-L1" in e for e in result["errors"])


def test_missing_hindi(tmp_path: Path):
    root = _make_synthetic_root(tmp_path)
    script_path = root / "canon" / "adhyay_02" / "script" / "easy.md"
    text = script_path.read_text(encoding="utf-8")
    # Remove Hindi line for S1-L1
    lines = text.splitlines()
    # Find the line after S1-L1 that starts with "- Hindi:"
    new_lines = []
    skip = False
    for line in lines:
        if skip and line.strip().startswith("- Hindi:"):
            skip = False
            continue
        if line.strip() == "**S1-L1** | narrator | ovi 1 | core":
            skip = True
        new_lines.append(line)
    script_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    result = check_script_cli.run_check(2, root)
    assert result["ok"] is False
    assert any("S1-L1" in e for e in result["errors"])


def test_unknown_voice(tmp_path: Path):
    root = _make_synthetic_root(tmp_path)
    script_path = root / "canon" / "adhyay_02" / "script" / "easy.md"
    text = script_path.read_text(encoding="utf-8")
    # Change voice to stranger
    text = text.replace("narrator", "stranger", 1)
    script_path.write_text(text, encoding="utf-8")
    result = check_script_cli.run_check(2, root)
    assert result["ok"] is False
    assert any("stranger" in e for e in result["errors"])


def test_ovi_not_in_chapter(tmp_path: Path):
    root = _make_synthetic_root(tmp_path)
    script_path = root / "canon" / "adhyay_02" / "script" / "easy.md"
    text = script_path.read_text(encoding="utf-8")
    # Change ovi to 99
    text = text.replace("ovi 1", "ovi 99", 1)
    script_path.write_text(text, encoding="utf-8")
    result = check_script_cli.run_check(2, root)
    assert result["ok"] is False
    assert any("99" in e for e in result["errors"])


def test_missing_script(tmp_path: Path):
    root = tmp_path
    # Create chapter structure but no script
    adhyay_dir = root / "canon" / "adhyay_02" / "source"
    adhyay_dir.mkdir(parents=True)
    (adhyay_dir / "ovis.jsonl").write_text('{"ovi": 1}\n', encoding="utf-8")
    # No script file
    result = check_script_cli.run_check(2, root)
    assert "script: missing" in result["problems"]
    assert result["lines"] == 0
    assert result["ok"] is False


def test_invalid_adhyay(tmp_path: Path):
    root = tmp_path
    result = check_script_cli.run_check(999, root)
    assert any("invalid adhyay" in p for p in result["problems"])
    assert result["ok"] is False


def test_write_receipt(tmp_path: Path):
    root = _make_synthetic_root(tmp_path)
    result = check_script_cli.run_check(2, root)
    receipt_path = check_script_cli.write_receipt(result, root, today="2025-01-01")
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["date"] == "2025-01-01"
    assert data["note"] == "report only; the script was never edited"
    # Second write should raise
    with pytest.raises(FileExistsError):
        check_script_cli.write_receipt(result, root)


def test_main_output_and_return_codes(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    root = _make_synthetic_root(tmp_path)
    # Happy path
    rc = check_script_cli.main(["--adhyay", "2", "--root", str(root)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "adhyay 2: 4 lines, 2 scenes, 4 core, 0 errors, 0 problems" in out

    # With errors (duplicate line id)
    script_path = root / "canon" / "adhyay_02" / "script" / "easy.md"
    text = script_path.read_text(encoding="utf-8")
    # Duplicate S1-L1 exactly
    text += (
        "**S1-L1** | narrator | ovi 1 | core\n"
        "- Marathi: नमस्कार मित्रांनो\n"
        "- Hindi: नमस्ते दोस्तों\n"
        "\n"
    )
    script_path.write_text(text, encoding="utf-8")
    rc = check_script_cli.main(["--adhyay", "2", "--root", str(root)])
    out = capsys.readouterr().out
    assert rc == 1
    assert "error:" in out

    # Write receipt
    rc = check_script_cli.main(["--adhyay", "2", "--root", str(root), "--write-receipt"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "receipt" in out

    # Refuse second write
    rc = check_script_cli.main(["--adhyay", "2", "--root", str(root), "--write-receipt"])
    out = capsys.readouterr().out
    assert rc == 2
    assert "refused: receipt exists" in out


@pytest.mark.skipif(
    not (_REPO_ROOT / "docs" / "pilot" / "A1_full_script_simple.md").exists(),
    reason="Real Adhyay 1 script not present",
)
def test_real_adhyay_1():
    result = check_script_cli.run_check(1, _REPO_ROOT)
    assert result["lines"] == 62
    assert result["scenes"] == 9
    assert isinstance(result["errors"], list)
    for e in result["errors"]:
        assert isinstance(e, str)


@pytest.mark.skipif(
    not (_REPO_ROOT / "canon" / "adhyay_02" / "script" / "easy.md").exists(),
    reason="Real Adhyay 2 script not present",
)
def test_real_adhyay_2():
    result = check_script_cli.run_check(2, _REPO_ROOT)
    assert result["lines"] == 148
    assert result["scenes"] == 12
    assert isinstance(result["errors"], list)
    for e in result["errors"]:
        assert isinstance(e, str)
```
## scripts/pipeline/check_script_cli.py (reference only)
```python
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

# Load existing modules by path
_REPO_ROOT = Path(__file__).resolve().parents[2]

def _load_module(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {module_name} from {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

_check_script_mod = _load_module("check_script", _REPO_ROOT / "scripts" / "pipeline" / "check_script.py")
_chapter_mod = _load_module("chapter", _REPO_ROOT / "scripts" / "pipeline" / "chapter.py")
_context_mod = _load_module("context", _REPO_ROOT / "scripts" / "pipeline" / "stage1" / "context.py")

parse_script = _check_script_mod.parse_script
check_script = _check_script_mod.check_script
script_sha256 = _check_script_mod.script_sha256
chapter_paths = _chapter_mod.chapter_paths
build_ctx = _context_mod.build_ctx


def run_check(
    adhyay: int,
    root: Path | str,
    glossary: dict[str, str] | None = None,
    extra_voices: list[str] | None = None,
) -> dict[str, Any]:
    root_path = Path(root)
    own_problems: list[str] = []
    script_rel = ""
    script_text = ""
    lines: list[dict] = []
    script_hash = ""

    try:
        paths = chapter_paths(adhyay, root_path)
    except ValueError as e:
        own_problems.append(f"invalid adhyay: {e}")
        return {
            "adhyay": adhyay,
            "script": "",
            "script_sha256": "",
            "lines": 0,
            "scenes": 0,
            "core": 0,
            "optional": 0,
            "errors": [],
            "problems": own_problems,
            "ok": False,
        }

    script_path = paths["script"]
    script_rel = script_path.relative_to(root_path).as_posix()

    if not script_path.exists():
        own_problems.append("script: missing")
        return {
            "adhyay": adhyay,
            "script": script_rel,
            "script_sha256": "",
            "lines": 0,
            "scenes": 0,
            "core": 0,
            "optional": 0,
            "errors": [],
            "problems": own_problems,
            "ok": False,
        }

    script_text = script_path.read_text(encoding="utf-8")
    script_hash = script_sha256(script_text)
    lines = parse_script(script_text)

    ctx, ctx_problems = build_ctx(adhyay, root_path, extra=None)
    chapter_ovis = ctx.get("chapter_ovis", [])
    unfilmed_ovis = ctx.get("unfilmed_ovis", [])
    saved_voices = ctx.get("saved_voices", {})
    series_voices = ctx.get("series_voices", {})

    allowed_voices: set[str] = {"narrator"}
    allowed_voices.update(saved_voices.keys())
    allowed_voices.update(series_voices.keys())
    if extra_voices:
        allowed_voices.update(extra_voices)

    errors = check_script(
        lines,
        set(chapter_ovis),
        set(unfilmed_ovis),
        allowed_voices,
        glossary or {},
    )

    scenes = len({line.get("scene") for line in lines if line.get("scene") is not None})
    core = sum(1 for line in lines if line.get("priority") == "core")
    optional = len(lines) - core

    all_problems = ctx_problems + own_problems
    ok = (len(errors) == 0) and (len(own_problems) == 0)

    return {
        "adhyay": adhyay,
        "script": script_rel,
        "script_sha256": script_hash,
        "lines": len(lines),
        "scenes": scenes,
        "core": core,
        "optional": optional,
        "errors": errors,
        "problems": all_problems,
        "ok": ok,
    }


def write_receipt(result: dict[str, Any], root: Path | str, today: str | None = None) -> Path:
    root_path = Path(root)
    adhyay = result["adhyay"]
    paths = chapter_paths(adhyay, root_path)
    stage1_dir = paths["stage1_dir"]
    stage1_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = stage1_dir / "script_check_receipt.json"
    if receipt_path.exists():
        raise FileExistsError(receipt_path)

    receipt_data = dict(result)
    receipt_data["date"] = today or date.today().isoformat()
    receipt_data["note"] = "report only; the script was never edited"

    receipt_path.write_text(
        json.dumps(receipt_data, indent=1, sort_keys=True, ensure_ascii=False),
        encoding="utf-8",
    )
    return receipt_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check EASY script for an adhyay")
    parser.add_argument("--adhyay", type=int, required=True, help="Adhyay number")
    parser.add_argument("--root", type=Path, default=_REPO_ROOT, help="Repository root")
    parser.add_argument("--write-receipt", action="store_true", help="Write receipt JSON")
    parser.add_argument("--extra-voice", action="append", default=[], help="Extra allowed voice IDs")
    args = parser.parse_args(argv)

    result = run_check(args.adhyay, args.root, extra_voices=args.extra_voice)

    print(
        f"adhyay {result['adhyay']}: {result['lines']} lines, "
        f"{result['scenes']} scenes, {result['core']} core, "
        f"{len(result['errors'])} errors, {len(result['problems'])} problems"
    )

    errors = result["errors"]
    for i, err in enumerate(errors):
        if i >= 40:
            remaining = len(errors) - 40
            print(f"... and {remaining} more")
            break
        print(f"error: {err}")

    if args.write_receipt:
        try:
            receipt_path = write_receipt(result, args.root)
            print(f"receipt {receipt_path}")
        except FileExistsError:
            print("refused: receipt exists")
            return 2

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
```
