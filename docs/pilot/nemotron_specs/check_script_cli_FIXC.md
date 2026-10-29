# FIX CALL: return BOTH files in full: `scripts/pipeline/check_script_cli.py` and `tests/test_check_script_cli.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
F.......F..                                                              [100%]
================================== FAILURES ===================================
_______________________________ test_happy_path _______________________________
tests\test_check_script_cli.py:68: in test_happy_path
    assert result["errors"] == []
E   AssertionError: assert ['ovi 3 has n...no core line'] == []
E     
E     Left contains 2 more items, first extra item: 'ovi 3 has no core line'
E     Use -v to get more diff
______________________ test_main_output_and_return_codes ______________________
tests\test_check_script_cli.py:177: in test_main_output_and_return_codes
    assert rc == 0
E   assert 1 == 0
=========================== short test summary info ===========================
FAILED tests/test_check_script_cli.py::test_happy_path - AssertionError: asse...
FAILED tests/test_check_script_cli.py::test_main_output_and_return_codes - as...
2 failed, 9 passed in 0.28s

```

## SPEC
# SPEC: NEW `scripts/pipeline/check_script_cli.py` + NEW `tests/test_check_script_cli.py`. Return exactly these TWO files in full; do not output or change any other file.
Checklist row 17: run the existing source/EASY script checker on a REAL script and write a receipt. The checker only reports; it never edits the script. Standard library only; `from __future__ import annotations`; nothing at import time except imports and definitions; no print except in `main()`; plain functions.

## Existing code (load by importlib BY PATH; do not modify)
- `scripts/pipeline/check_script.py`: `parse_script(text) -> list[dict]` (records with `id, scene, voice, ovi, priority, marathi, hindi, ...`), `check_script(lines, chapter_ovis: set[int], unfilmed_ovis: set[int], voices: set[str], glossary: dict[str, str]) -> list[str]` (error messages), `script_sha256(text) -> str`.
- `scripts/pipeline/chapter.py`: `chapter_paths(adhyay, root)` with the keys `script`, `source_ovis`, `stage1_dir` (ValueError for an invalid adhyay).
- `scripts/pipeline/stage1/context.py`: `build_ctx(adhyay, root, extra=None) -> (ctx, problems)`; ctx keys used here: `chapter_ovis` (list of int), `unfilmed_ovis` (list of int, the owner-APPROVED omissions), `saved_voices` (dict voice_key -> voice_id), `series_voices` (dict character_id -> voice_key).
Repo root in this module: `Path(__file__).resolve().parents[2]`; in tests `Path(__file__).resolve().parents[1]`.

## API
- `run_check(adhyay: int, root: Path | str, glossary: dict[str, str] | None = None, extra_voices: list[str] | None = None) -> dict`: NEVER raises. Reads the script text from `chapter_paths(...)["script"]` (missing -> a problem `script: missing` and an empty result), parses it, builds the ctx, and the allowed voice set = `{"narrator"}` plus `saved_voices` keys plus `series_voices` keys plus `extra_voices`; calls `check_script(lines, set(chapter_ovis), set(unfilmed_ovis), voices, glossary or {})`. Returns `{"adhyay", "script": <path relative to root with forward slashes>, "script_sha256", "lines": len(lines), "scenes": number of distinct scene ids, "core": count of priority core, "optional": count of the others, "errors": [...], "problems": ctx problems + own problems, "ok": errors == [] and no own problem}`.
- `write_receipt(result: dict, root: Path | str, today: str | None = None) -> Path`: writes `<stage1_dir>/script_check_receipt.json` (json, indent 1, sort_keys, `ensure_ascii=False`) with the result plus `"date"` (today or ISO today) and the field `"note": "report only; the script was never edited"`; raises `FileExistsError` if the file exists; creates the folder.
- `main(argv=None) -> int`: `--adhyay N` (required), `--root PATH` (default repo root), `--write-receipt` (flag), `--extra-voice ID` (repeatable). Prints one line `adhyay N: <lines> lines, <scenes> scenes, <core> core, <errors> errors, <problems> problems` then each error as `error: <text>` (at most 40, then `... and <k> more`); with `--write-receipt` writes the receipt (an existing receipt -> prints `refused: receipt exists` and returns 2) and prints `receipt <path>`. Returns 0 when ok, 1 otherwise.

## Tests (`tests/test_check_script_cli.py`; synthetic data in tmp_path plus real-file tests)
Synthetic root for adhyay 2: `canon/adhyay_02/source/ovis.jsonl` (`{"ovi": n}` for n in 1..4), `canon/adhyay_02/script/easy.md` in the REAL EASY format (`## S1`, then `**S1-L1** | narrator | ovi 1 | core`, `- Marathi: ...`, `- Hindi: ...`, blank line, and so on; lines for ovis 1, 2, 3 and 4 with 2 scenes), `canon/series/voices.json` with `{"voices": [ {"voice_key": "narrator", "voice_id": "id1"} ]}`.
1. Happy path: counts right, `errors == []`, `ok` True, `script_sha256` equals `script_sha256(text)`.
2. Each defect in its own isolated test (verified by the checker itself): a duplicate line id, a missing Hindi line, an unknown voice (`stranger`), an ovi not in the chapter; assert the result is not ok and the error mentions the line id.
3. Missing script -> problem `script: missing`, no exception; invalid adhyay -> no exception and a problem.
4. `write_receipt`: file content, the note, refusal on a second write; `main` output and return codes (capsys), `--write-receipt`, the refusal returning 2.
5. REAL files (skipif a file is missing): `run_check(1, ROOT)` returns 62 lines and 9 scenes (Adhyay 1 script `docs/pilot/A1_full_script_simple.md` through chapter_paths); `run_check(2, ROOT)` returns 148 lines and 12 scenes; neither raises. Do NOT assert that the real errors list is empty (the checker may report real findings); assert only the counts and that every error is a string.
Use plain assignment and `copy.deepcopy`; never a helper that rejects no-effect mutations.

Reply with only the two FILE blocks:
FILE: scripts/pipeline/check_script_cli.py
FILE: tests/test_check_script_cli.py


## CURRENT MODULE scripts/pipeline/check_script_cli.py
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

## CURRENT TESTS tests/test_check_script_cli.py
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
        "**S2-L1** | narrator | ovi 3 | optional\n"
        "- Marathi: आज हवा चांगली आहे\n"
        "- Hindi: आज मौसम अच्छा है\n"
        "\n"
        "**S2-L2** | narrator | ovi 4 | optional\n"
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

    return root


def test_happy_path(tmp_path: Path):
    root = _make_synthetic_root(tmp_path)
    result = check_script_cli.run_check(2, root)
    assert result["adhyay"] == 2
    assert result["lines"] == 4
    assert result["scenes"] == 2
    assert result["core"] == 2
    assert result["optional"] == 2
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
    assert "adhyay 2: 4 lines, 2 scenes, 2 core, 0 errors, 0 problems" in out

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

## DIAGNOSIS (verified)
Two tests still fail (test_happy_path, test_main_output_and_return_codes) with the real checker errors `ovi 3 has no core line` (and one more of the same kind): the checker requires EVERY chapter ovi (ctx chapter_ovis) to be either covered by at least one `core` script line or listed as an unfilmed ovi. The synthetic script in the tests does not give ovi 3 (and another ovi) a core line. FIX THE TEST FIXTURE (module is correct): the synthetic ovis file has ovis 1..4; the synthetic script must contain one line per ovi 1, 2, 3 and 4, each with priority `core` (`**S1-L1** | narrator | ovi 1 | core`, `**S1-L2** | narrator | ovi 2 | core`, `**S2-L1** | narrator | ovi 3 | core`, `**S2-L2** | narrator | ovi 4 | core`), Devanagari text without digits or Latin letters. Then run the happy path by hand against the checker rules (ids unique and ordered, both languages present, voices allowed: narrator) so that `errors == []`. Keep the other tests; the defect tests must still violate exactly one rule each. Return BOTH complete FILE blocks.
