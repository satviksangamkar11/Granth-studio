# FIX CALL: return BOTH files in full: `scripts/pipeline/stage1/script_from_docx.py` and `tests/test_stage1_script_from_docx.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
F.F.........                                                             [100%]
================================== FAILURES ===================================
____________________________ test_basic_synthetic _____________________________
tests\test_stage1_script_from_docx.py:74: in test_basic_synthetic
    assert script == expected
E   AssertionError: assert '# Adhyay 2: ...\u0941\u0930\u094d\u0925 \u0905\u0927\u094d\u092f\u093e\u092f\\n' == '# Adhyay 2: ...\u094d\u0925 \u0905\u0927\u094d\u092f\u093e\u092f\\n\\n'
E     
E     Skipping 681 identical leading characters in diff, use -v to show
E       \u0930\u094d\u0925 \u0905\u0927\u094d\u092f\u093e\u092f
E     -
_________________________ test_ordering_and_numbering _________________________
tests\test_stage1_script_from_docx.py:121: in test_ordering_and_numbering
    assert [r["scene"] for r in records] == [1, 1, 3, 3]
E   AssertionError: assert ['S1', 'S1', 'S3', 'S3'] == [1, 1, 3, 3]
E     
E     At index 0 diff: 'S1' != 1
E     Use -v to get more diff
=========================== short test summary info ===========================
FAILED tests/test_stage1_script_from_docx.py::test_basic_synthetic - Assertio...
FAILED tests/test_stage1_script_from_docx.py::test_ordering_and_numbering - A...
2 failed, 10 passed in 6.91s

```

## SPEC
# SPEC: NEW `scripts/pipeline/stage1/script_from_docx.py` + NEW `tests/test_stage1_script_from_docx.py`. Return exactly these TWO files in full; do not output or change any other file.
Purpose: Adhyay 2 (and every later Adhyay) arrives as the owner's Audited Canon docx, which has NO script in the pipeline's line format. For dry runs and trials, build a DRAFT script MECHANICALLY from the docx columns that the owner already supplied (Simple Marathi and Hindi), without changing a single word. This is NOT the owner's final script; the file says so in its heading. Standard library only; `from __future__ import annotations`; nothing at import time except imports and definitions; no print except in `main()`. Plain functions, no classes.

## Input
The ovis written by `scripts/pipeline/import_canon_docx.py` into `canon/adhyay_NN/source/ovis.jsonl`: one JSON object per line with the fields `adhyay` (int), `ovi` (int), `section` (int, the docx section number), `original_marathi`, `simple_marathi`, `hindi`, `easy_english`, `printed_number` (int or null).

## API
- `ovis_to_script(adhyay: int, ovis: list[dict]) -> str`: returns the script text. Sort the ovis by `ovi`. Output exactly this format (it is parsed by `scripts/pipeline/check_script.parse_script`, whose header regex is `^\*\*(S(\d+)-L(\d+))\*\* \| (\S+) \| ovi (\d+) \| (\S+)$`):
  ```
  # Adhyay <N>: DRAFT script built mechanically from the owner's docx columns (Simple Marathi, Hindi). NOT the owner's final script; speakers are all narrator; every line is core.
  
  ## S<section>
  **S<section>-L<k>** | narrator | ovi <ovi> | core
  - Marathi: <simple_marathi on ONE line>
  - Hindi: <hindi on ONE line>
  
  ```
  where `<section>` is the record's `section`, `<k>` counts the lines inside that section from 1 in ovi order, a `## S<section>` heading is written once when the section changes, and a blank line follows each line block. The text of a cell is used UNCHANGED except that every run of whitespace (including newlines) is collapsed to one space and the ends are stripped. Never translate, shorten, correct or add words.
  Errors: raise `ValueError` (clear message) when `ovis` is empty, when a record lacks an int `ovi` or an int `section`, when `simple_marathi` or `hindi` is missing or empty after collapsing, or when two records share an ovi. A bool is not an int.
- `main(argv=None) -> int`: `--adhyay N` (int, required), `--root PATH` (default the repo root `Path(__file__).resolve().parents[3]`). Reads `<root>/canon/adhyay_<NN>/source/ovis.jsonl`, writes `<root>/canon/adhyay_<NN>/script/easy.md` (creating the folder); refuses with `refused: <reason>` and returns 2 if the output exists, the input is missing or a record is invalid; prints one line `adhyay N: <lines> lines, <sections> sections` and returns 0. `if __name__ == "__main__": raise SystemExit(main())`.

## Tests (`tests/test_stage1_script_from_docx.py`; synthetic data only, plus ONE real-file test)
Load the module and `scripts/pipeline/check_script.py` by importlib BY PATH (`ROOT = Path(__file__).resolve().parents[1]`).
1. A small synthetic ovis list (3 sections, 6 ovis, short invented Devanagari words) gives the exact expected text (compare the full string) and `parse_script` returns one record per ovi with the right id, scene, voice `narrator`, ovi, priority `core`, and the Marathi/Hindi texts equal to the collapsed cell texts.
2. Whitespace collapsing: a cell with newlines and double spaces becomes one line with single spaces; nothing else changes (assert the other characters are identical).
3. Ordering and numbering: ovis given unsorted are sorted by ovi; `k` restarts at 1 in every section; a section number that jumps (1, 3) is kept as given.
4. Each error case raises ValueError (empty list, missing ovi, missing section, bool ovi, empty hindi, duplicate ovi), each in its own isolated test.
5. `main`: writes the file in tmp_path, refuses to overwrite (return 2), refuses a missing input (return 2) (use capsys).
6. REAL file (skip with `pytest.mark.skipif` if the file is missing): `canon/test_inputs/Shri_Gajanan_Vijay_Chapter_2_Audited_Canon_Edition.docx` through `scripts/pipeline/import_canon_docx.py` (`parse_docx(Path)` returns a dict with `ovis`), then `ovis_to_script(2, parsed["ovis"])`: `parse_script` gives exactly 148 records, 12 distinct scenes, every record has non-empty Marathi and Hindi, `check_script.check_script` is NOT required.
Use `copy.deepcopy` and plain assignment for any mutation; never a helper that rejects "no effect" mutations.

Reply with only the two FILE blocks:
FILE: scripts/pipeline/stage1/script_from_docx.py
FILE: tests/test_stage1_script_from_docx.py


## CURRENT MODULE scripts/pipeline/stage1/script_from_docx.py
```python
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def collapse_whitespace(text: str) -> str:
    """Collapse any run of whitespace (including newlines) to a single space and strip ends."""
    return re.sub(r"\s+", " ", text).strip()


def ovis_to_script(adhyay: int, ovis: list[dict[str, Any]]) -> str:
    """
    Convert a list of ovi records into the draft script text.

    Raises ValueError with a clear message for any invalid input.
    """
    if not ovis:
        raise ValueError("ovis list is empty")

    # Validate and collect ovi numbers for duplicate detection
    seen_ovis = set()
    for idx, rec in enumerate(ovis):
        # ovi must be present and be an int (not bool)
        if "ovi" not in rec:
            raise ValueError(f"record at index {idx} missing 'ovi'")
        ovi = rec["ovi"]
        if not isinstance(ovi, int) or isinstance(ovi, bool):
            raise ValueError(f"record at index {idx} has non-int ovi: {ovi!r}")
        if ovi in seen_ovis:
            raise ValueError(f"duplicate ovi: {ovi}")
        seen_ovis.add(ovi)

        # section must be present and be an int (not bool)
        if "section" not in rec:
            raise ValueError(f"record at index {idx} missing 'section'")
        section = rec["section"]
        if not isinstance(section, int) or isinstance(section, bool):
            raise ValueError(f"record at index {idx} has non-int section: {section!r}")

        # simple_marathi and hindi must be present and non-empty after collapsing
        for field in ("simple_marathi", "hindi"):
            if field not in rec:
                raise ValueError(f"record at index {idx} missing '{field}'")
            collapsed = collapse_whitespace(str(rec[field]))
            if not collapsed:
                raise ValueError(f"record at index {idx} has empty '{field}' after collapsing whitespace")

    # Sort by ovi
    sorted_ovis = sorted(ovis, key=lambda r: r["ovi"])

    lines: list[str] = []
    # Header
    lines.append(
        f"# Adhyay {adhyay}: DRAFT script built mechanically from the owner's docx columns (Simple Marathi, Hindi). NOT the owner's final script; speakers are all narrator; every line is core."
    )
    lines.append("")  # blank line after header

    current_section = None
    line_in_section = 0

    for rec in sorted_ovis:
        section = rec["section"]
        ovi = rec["ovi"]
        marathi = collapse_whitespace(str(rec["simple_marathi"]))
        hindi = collapse_whitespace(str(rec["hindi"]))

        if section != current_section:
            current_section = section
            line_in_section = 1
            lines.append(f"## S{current_section}")
        else:
            line_in_section += 1

        lines.append(f"**S{section}-L{line_in_section}** | narrator | ovi {ovi} | core")
        lines.append(f"- Marathi: {marathi}")
        lines.append(f"- Hindi: {hindi}")
        lines.append("")  # blank line after each line block

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build draft script from ovis.jsonl")
    parser.add_argument("--adhyay", type=int, required=True, help="Adhyay number (e.g., 2)")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[3],
        help="Repository root (default: repo root inferred from this file)",
    )
    args = parser.parse_args(argv)

    adhyay = args.adhyay
    root = args.root

    input_path = root / "canon" / f"adhyay_{adhyay:02d}" / "source" / "ovis.jsonl"
    output_path = root / "canon" / f"adhyay_{adhyay:02d}" / "script" / "easy.md"

    if not input_path.exists():
        print(f"refused: input file not found: {input_path}", file=sys.stderr)
        return 2

    if output_path.exists():
        print(f"refused: output file already exists: {output_path}", file=sys.stderr)
        return 2

    # Read ovis.jsonl
    ovis: list[dict[str, Any]] = []
    try:
        with input_path.open("r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    ovis.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"refused: invalid JSON on line {line_num}: {e}", file=sys.stderr)
                    return 2
    except OSError as e:
        print(f"refused: cannot read input file: {e}", file=sys.stderr)
        return 2

    # Generate script
    try:
        script_text = ovis_to_script(adhyay, ovis)
    except ValueError as e:
        print(f"refused: {e}", file=sys.stderr)
        return 2

    # Write output
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            f.write(script_text)
    except OSError as e:
        print(f"refused: cannot write output file: {e}", file=sys.stderr)
        return 2

    # Count lines and sections
    num_lines = len(ovis)
    num_sections = len({rec["section"] for rec in ovis})
    print(f"adhyay {adhyay}: {num_lines} lines, {num_sections} sections")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

## CURRENT TESTS tests/test_stage1_script_from_docx.py
```python
from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# Load script_from_docx module
spec_sfd = importlib.util.spec_from_file_location(
    "script_from_docx", ROOT / "scripts/pipeline/stage1/script_from_docx.py"
)
assert spec_sfd is not None and spec_sfd.loader is not None
sfd = importlib.util.module_from_spec(spec_sfd)
spec_sfd.loader.exec_module(sfd)

# Load check_script module
spec_cs = importlib.util.spec_from_file_location(
    "check_script", ROOT / "scripts/pipeline/check_script.py"
)
assert spec_cs is not None and spec_cs.loader is not None
cs = importlib.util.module_from_spec(spec_cs)
spec_cs.loader.exec_module(cs)

ovis_to_script = sfd.ovis_to_script
parse_script = cs.parse_script


def test_basic_synthetic():
    ovis = [
        {"adhyay": 2, "ovi": 1, "section": 1, "simple_marathi": "श्री गजानन", "hindi": "श्री गजानन", "easy_english": "", "printed_number": 1, "original_marathi": ""},
        {"adhyay": 2, "ovi": 2, "section": 1, "simple_marathi": "विजय ग्रन्थ", "hindi": "विजय ग्रन्थ", "easy_english": "", "printed_number": 2, "original_marathi": ""},
        {"adhyay": 2, "ovi": 3, "section": 2, "simple_marathi": "प्रथम अध्याय", "hindi": "प्रथम अध्याय", "easy_english": "", "printed_number": 3, "original_marathi": ""},
        {"adhyay": 2, "ovi": 4, "section": 2, "simple_marathi": "द्वितीय अध्याय", "hindi": "द्वितीय अध्याय", "easy_english": "", "printed_number": 4, "original_marathi": ""},
        {"adhyay": 2, "ovi": 5, "section": 3, "simple_marathi": "तृतीय अध्याय", "hindi": "तृतीय अध्याय", "easy_english": "", "printed_number": 5, "original_marathi": ""},
        {"adhyay": 2, "ovi": 6, "section": 3, "simple_marathi": "चतुर्थ अध्याय", "hindi": "चतुर्थ अध्याय", "easy_english": "", "printed_number": 6, "original_marathi": ""},
    ]
    script = ovis_to_script(2, ovis)
    expected = (
        "# Adhyay 2: DRAFT script built mechanically from the owner's docx columns (Simple Marathi, Hindi). NOT the owner's final script; speakers are all narrator; every line is core.\n"
        "\n"
        "## S1\n"
        "**S1-L1** | narrator | ovi 1 | core\n"
        "- Marathi: श्री गजानन\n"
        "- Hindi: श्री गजानन\n"
        "\n"
        "**S1-L2** | narrator | ovi 2 | core\n"
        "- Marathi: विजय ग्रन्थ\n"
        "- Hindi: विजय ग्रन्थ\n"
        "\n"
        "## S2\n"
        "**S2-L1** | narrator | ovi 3 | core\n"
        "- Marathi: प्रथम अध्याय\n"
        "- Hindi: प्रथम अध्याय\n"
        "\n"
        "**S2-L2** | narrator | ovi 4 | core\n"
        "- Marathi: द्वितीय अध्याय\n"
        "- Hindi: द्वितीय अध्याय\n"
        "\n"
        "## S3\n"
        "**S3-L1** | narrator | ovi 5 | core\n"
        "- Marathi: तृतीय अध्याय\n"
        "- Hindi: तृतीय अध्याय\n"
        "\n"
        "**S3-L2** | narrator | ovi 6 | core\n"
        "- Marathi: चतुर्थ अध्याय\n"
        "- Hindi: चतुर्थ अध्याय\n"
        "\n"
    )
    assert script == expected

    # Parse with check_script.parse_script
    records = parse_script(script)
    assert len(records) == 6
    for i, rec in enumerate(records):
        assert rec["id"] == f"S{ovis[i]['section']}-L{i+1 if ovis[i]['section']==ovis[i-1]['section'] else 1}"  # but careful: we need to compute expected id
    # Better: check each record's fields
    expected_ids = ["S1-L1", "S1-L2", "S2-L1", "S2-L2", "S3-L1", "S3-L2"]
    for i, rec in enumerate(records):
        assert rec["id"] == expected_ids[i]
        assert rec["scene"] == int(expected_ids[i][1])  # section number
        assert rec["voice"] == "narrator"
        assert rec["ovi"] == ovis[i]["ovi"]
        assert rec["priority"] == "core"
        assert rec["marathi"] == ovis[i]["simple_marathi"]
        assert rec["hindi"] == ovis[i]["hindi"]


def test_whitespace_collapsing():
    ovis = [
        {"adhyay": 1, "ovi": 1, "section": 1, "simple_marathi": "  श्री   गजानन  \nविजय  ", "hindi": "श्री\tगजानन\nविजय", "easy_english": "", "printed_number": 1, "original_marathi": ""},
    ]
    script = ovis_to_script(1, ovis)
    # The collapsed texts should have single spaces
    assert "श्री गजानन विजय" in script
    # Ensure no other characters changed
    # We can parse and check
    records = parse_script(script)
    assert records[0]["marathi"] == "श्री गजानन विजय"
    assert records[0]["hindi"] == "श्री गजानन विजय"


def test_ordering_and_numbering():
    # Unsorted ovis, section jump
    ovis = [
        {"adhyay": 1, "ovi": 5, "section": 3, "simple_marathi": "पांच", "hindi": "पांच", "easy_english": "", "printed_number": 5, "original_marathi": ""},
        {"adhyay": 1, "ovi": 1, "section": 1, "simple_marathi": "एक", "hindi": "एक", "easy_english": "", "printed_number": 1, "original_marathi": ""},
        {"adhyay": 1, "ovi": 3, "section": 3, "simple_marathi": "तीन", "hindi": "तीन", "easy_english": "", "printed_number": 3, "original_marathi": ""},
        {"adhyay": 1, "ovi": 2, "section": 1, "simple_marathi": "दो", "hindi": "दो", "easy_english": "", "printed_number": 2, "original_marathi": ""},
    ]
    script = ovis_to_script(1, ovis)
    records = parse_script(script)
    assert len(records) == 4
    # Order should be by ovi: 1,2,3,5
    assert [r["ovi"] for r in records] == [1, 2, 3, 5]
    # Sections: 1,1,3,3
    assert [r["scene"] for r in records] == [1, 1, 3, 3]
    # Line numbers within section restart
    assert [r["id"] for r in records] == ["S1-L1", "S1-L2", "S3-L1", "S3-L2"]


def test_error_empty_list():
    with pytest.raises(ValueError, match="ovis list is empty"):
        ovis_to_script(1, [])


def test_error_missing_ovi():
    ovis = [{"adhyay": 1, "section": 1, "simple_marathi": "एक", "hindi": "एक", "easy_english": "", "printed_number": 1, "original_marathi": ""}]
    with pytest.raises(ValueError, match="missing 'ovi'"):
        ovis_to_script(1, ovis)


def test_error_missing_section():
    ovis = [{"adhyay": 1, "ovi": 1, "simple_marathi": "एक", "hindi": "एक", "easy_english": "", "printed_number": 1, "original_marathi": ""}]
    with pytest.raises(ValueError, match="missing 'section'"):
        ovis_to_script(1, ovis)


def test_error_bool_ovi():
    ovis = [{"adhyay": 1, "ovi": True, "section": 1, "simple_marathi": "एक", "hindi": "एक", "easy_english": "", "printed_number": 1, "original_marathi": ""}]
    with pytest.raises(ValueError, match="non-int ovi"):
        ovis_to_script(1, ovis)


def test_error_empty_hindi():
    ovis = [{"adhyay": 1, "ovi": 1, "section": 1, "simple_marathi": "एक", "hindi": "   ", "easy_english": "", "printed_number": 1, "original_marathi": ""}]
    with pytest.raises(ValueError, match="empty 'hindi'"):
        ovis_to_script(1, ovis)


def test_error_duplicate_ovi():
    ovis = [
        {"adhyay": 1, "ovi": 1, "section": 1, "simple_marathi": "एक", "hindi": "एक", "easy_english": "", "printed_number": 1, "original_marathi": ""},
        {"adhyay": 1, "ovi": 1, "section": 2, "simple_marathi": "दो", "hindi": "दो", "easy_english": "", "printed_number": 2, "original_marathi": ""},
    ]
    with pytest.raises(ValueError, match="duplicate ovi"):
        ovis_to_script(1, ovis)


def test_main_writes_file(tmp_path, capsys):
    # Create a temporary repo structure
    root = tmp_path
    adhyay = 5
    input_dir = root / "canon" / f"adhyay_{adhyay:02d}" / "source"
    input_dir.mkdir(parents=True)
    output_dir = root / "canon" / f"adhyay_{adhyay:02d}" / "script"
    ovis = [
        {"adhyay": adhyay, "ovi": 1, "section": 1, "simple_marathi": "एक", "hindi": "एक", "easy_english": "", "printed_number": 1, "original_marathi": ""},
        {"adhyay": adhyay, "ovi": 2, "section": 1, "simple_marathi": "दो", "hindi": "दो", "easy_english": "", "printed_number": 2, "original_marathi": ""},
    ]
    input_file = input_dir / "ovis.jsonl"
    with input_file.open("w", encoding="utf-8") as f:
        for rec in ovis:
            f.write(json.dumps(rec) + "\n")

    # Run main
    ret = sfd.main(["--adhyay", str(adhyay), "--root", str(root)])
    assert ret == 0
    captured = capsys.readouterr()
    assert f"adhyay {adhyay}: 2 lines, 1 sections" in captured.out

    # Check output file exists and content
    output_file = output_dir / "easy.md"
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "DRAFT script" in content
    assert "**S1-L1**" in content
    assert "**S1-L2**" in content

    # Run again -> should refuse because output exists
    ret2 = sfd.main(["--adhyay", str(adhyay), "--root", str(root)])
    assert ret2 == 2
    captured2 = capsys.readouterr()
    assert "refused: output file already exists" in captured2.err


def test_main_refuses_missing_input(tmp_path, capsys):
    root = tmp_path
    adhyay = 7
    # No input file
    ret = sfd.main(["--adhyay", str(adhyay), "--root", str(root)])
    assert ret == 2
    captured = capsys.readouterr()
    assert "refused: input file not found" in captured.err


@pytest.mark.skipif(
    not (ROOT / "canon/test_inputs/Shri_Gajanan_Vijay_Chapter_2_Audited_Canon_Edition.docx").exists(),
    reason="Real docx test file not present",
)
def test_real_docx():
    # Import import_canon_docx
    spec_icd = importlib.util.spec_from_file_location(
        "import_canon_docx", ROOT / "scripts/pipeline/import_canon_docx.py"
    )
    assert spec_icd is not None and spec_icd.loader is not None
    icd = importlib.util.module_from_spec(spec_icd)
    spec_icd.loader.exec_module(icd)

    docx_path = ROOT / "canon/test_inputs/Shri_Gajanan_Vijay_Chapter_2_Audited_Canon_Edition.docx"
    parsed = icd.parse_docx(docx_path)
    ovis = parsed["ovis"]
    script = ovis_to_script(2, ovis)
    records = parse_script(script)
    assert len(records) == 148
    scenes = {r["scene"] for r in records}
    assert len(scenes) == 12
    for r in records:
        assert r["marathi"] != ""
        assert r["hindi"] != ""

```

## NOTE: 2 tests fail (test_basic_synthetic, test_ordering_and_numbering) because the TESTS compare the parsed `scene` to an int (`[1, 1, 3, 3]`) while `check_script.parse_script` returns the string form (`'S1'`, `'S3'`). Fix the TESTS (compare with `'S<section>'`); the module is correct. Return BOTH complete FILE blocks.
