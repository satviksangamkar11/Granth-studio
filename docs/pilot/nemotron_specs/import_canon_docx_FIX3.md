# FIX CALL: return BOTH files in full: `scripts/pipeline/import_canon_docx.py` and `tests/test_import_canon_docx.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
FF...FFFFFFFFF..F.FF                                                     [100%]
================================== FAILURES ===================================
_____________________ TestParseDocx.test_valid_synthetic ______________________
tests\test_import_canon_docx.py:149: in test_valid_synthetic
    parsed = parse_docx(docx_path)
             ^^^^^^^^^^^^^^^^^^^^^
scripts\pipeline\import_canon_docx.py:309: in parse_docx
    raise LayoutError("no PART 2 paragraph found")
E   scripts.pipeline.import_canon_docx.LayoutError: no PART 2 paragraph found
____________________ TestParseDocx.test_mismatch_reporting ____________________
tests\test_import_canon_docx.py:243: in test_mismatch_reporting
    parsed = parse_docx(docx_path)
             ^^^^^^^^^^^^^^^^^^^^^
scripts\pipeline\import_canon_docx.py:309: in parse_docx
    raise LayoutError("no PART 2 paragraph found")
E   scripts.pipeline.import_canon_docx.LayoutError: no PART 2 paragraph found
________________ TestParseDocx.test_refuse_bad_section_header _________________
tests\test_import_canon_docx.py:322: in test_refuse_bad_section_header
    with pytest.raises(LayoutError, match="section header does not match pattern"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AssertionError: Regex pattern did not match.
E     Expected regex: 'section header does not match pattern'
E     Actual message: 'no PART 2 paragraph found'
__________ TestParseDocx.test_refuse_non_consecutive_section_numbers __________
tests\test_import_canon_docx.py:354: in test_refuse_non_consecutive_section_numbers
    with pytest.raises(LayoutError, match="section numbers not consecutive"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AssertionError: Regex pattern did not match.
E     Expected regex: 'section numbers not consecutive'
E     Actual message: 'no PART 2 paragraph found'
_____ TestParseDocx.test_refuse_header_not_followed_by_context_and_table ______
tests\test_import_canon_docx.py:383: in test_refuse_header_not_followed_by_context_and_table
    with pytest.raises(LayoutError, match="section header not followed by context paragraph"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AssertionError: Regex pattern did not match.
E     Expected regex: 'section header not followed by context paragraph'
E     Actual message: 'no PART 2 paragraph found'
_____________ TestParseDocx.test_refuse_table_header_not_5_cells ______________
tests\test_import_canon_docx.py:417: in test_refuse_table_header_not_5_cells
    with pytest.raises(LayoutError, match="table header row does not have 5 cells"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AssertionError: Regex pattern did not match.
E     Expected regex: 'table header row does not have 5 cells'
E     Actual message: 'no PART 2 paragraph found'
_______________ TestParseDocx.test_refuse_data_row_not_5_cells ________________
tests\test_import_canon_docx.py:450: in test_refuse_data_row_not_5_cells
    with pytest.raises(LayoutError, match="data row 0 does not have 5 cells"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AssertionError: Regex pattern did not match.
E     Expected regex: 'data row 0 does not have 5 cells'
E     Actual message: 'no PART 2 paragraph found'
______________ TestParseDocx.test_refuse_non_integer_row_number _______________
tests\test_import_canon_docx.py:483: in test_refuse_non_integer_row_number
    with pytest.raises(LayoutError, match="row number not an integer"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AssertionError: Regex pattern did not match.
E     Expected regex: 'row number not an integer'
E     Actual message: 'no PART 2 paragraph found'
_______ TestParseDocx.test_refuse_row_numbers_out_of_order_or_mismatch ________
tests\test_import_canon_docx.py:516: in test_refuse_row_numbers_out_of_order_or_mismatch
    with pytest.raises(LayoutError, match="row numbers out of order or mismatch"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AssertionError: Regex pattern did not match.
E     Expected regex: 'row numbers out of order or mismatch'
E     Actual message: 'no PART 2 paragraph found'
______________ TestParseDocx.test_refuse_non_contiguous_sections ______________
tests\test_import_canon_docx.py:548: in test_refuse_non_contiguous_sections
    with pytest.raises(LayoutError, match="sections not contiguous"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AssertionError: Regex pattern did not match.
E     Expected regex: 'sections not contiguous'
E     Actual message: 'no PART 2 paragraph found'
________________ TestParseDocx.test_refuse_empty_required_cell ________________
tests\test_import_canon_docx.py:580: in test_refuse_empty_required_cell
    with pytest.raises(LayoutError, match="empty required cell"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AssertionError: Regex pattern did not match.
E     Expected regex: 'empty required cell'
E     Actual message: 'no PART 2 paragraph found'
_________________________ TestMain.test_main_success __________________________
tests\test_import_canon_docx.py:658: in test_main_success
    assert ret == 0
E   assert 2 == 0
---------------------------- Captured stdout call -----------------------------
refused: no PART 2 paragraph found
___________________ TestMain.test_main_refused_file_exists ____________________
tests\test_import_canon_docx.py:680: in test_main_refused_file_exists
    assert ret == 0
E   assert 2 == 0
---------------------------- Captured stdout call -----------------------------
refused: no PART 2 paragraph found
________________ TestRealFile.test_real_file_parses_correctly _________________
tests\test_import_canon_docx.py:696: in test_real_file_parses_correctly
    parsed = parse_docx(docx_path)
             ^^^^^^^^^^^^^^^^^^^^^
scripts\pipeline\import_canon_docx.py:309: in parse_docx
    raise LayoutError("no PART 2 paragraph found")
E   scripts.pipeline.import_canon_docx.LayoutError: no PART 2 paragraph found
=========================== short test summary info ===========================
FAILED tests/test_import_canon_docx.py::TestParseDocx::test_valid_synthetic
FAILED tests/test_import_canon_docx.py::TestParseDocx::test_mismatch_reporting
FAILED tests/test_import_canon_docx.py::TestParseDocx::test_refuse_bad_section_header
FAILED tests/test_import_canon_docx.py::TestParseDocx::test_refuse_non_consecutive_section_numbers
FAILED tests/test_import_canon_docx.py::TestParseDocx::test_refuse_header_not_followed_by_context_and_table
FAILED tests/test_import_canon_docx.py::TestParseDocx::test_refuse_table_header_not_5_cells
FAILED tests/test_import_canon_docx.py::TestParseDocx::test_refuse_data_row_not_5_cells
FAILED tests/test_import_canon_docx.py::TestParseDocx::test_refuse_non_integer_row_number
FAILED tests/test_import_canon_docx.py::TestParseDocx::test_refuse_row_numbers_out_of_order_or_mismatch
FAILED tests/test_import_canon_docx.py::TestParseDocx::test_refuse_non_contiguous_sections
FAILED tests/test_import_canon_docx.py::TestParseDocx::test_refuse_empty_required_cell
FAILED tests/test_import_canon_docx.py::TestMain::test_main_success - assert ...
FAILED tests/test_import_canon_docx.py::TestMain::test_main_refused_file_exists
FAILED tests/test_import_canon_docx.py::TestRealFile::test_real_file_parses_correctly
14 failed, 6 passed in 0.44s

```

## SPEC
# SPEC: NEW `scripts/pipeline/import_canon_docx.py` + NEW `tests/test_import_canon_docx.py`. Return exactly these TWO files in full. Do not output or change any other file.
Purpose: read an "Audited Canon Edition" .docx (one Adhyay) into plain data so later stages need no docx knowledge. Standard library only (`zipfile`, `xml.etree.ElementTree`, `json`, `re`, `argparse`, `pathlib`, `hashlib`); no new dependency. Style: `from __future__ import annotations`; nothing at import time; no print except in `main()`. `ROOT = Path(__file__).resolve().parents[1]` in the module's own tests means `parents[1]` of the test file = repo root; the module uses `Path(__file__).resolve().parents[2]`.
## Layout of the real file (`canon/test_inputs/Shri_Gajanan_Vijay_Chapter_2_Audited_Canon_Edition.docx`), read `word/document.xml` body children in order (WordprocessingML namespace `http://schemas.openxmlformats.org/wordprocessingml/2006/main`)
- Paragraph text = concatenation of all `w:t` in the paragraph. A cell's text = its paragraphs' texts joined by "\n". Keep text exactly (do not normalise Unicode; keep U+200D); only strip leading/trailing whitespace of each cell/paragraph.
- A paragraph starting `PART 1` begins the story bible. Inside it, headings start `1. Characters`, `2. Locations`, `3. Key Objects` (the number then a dot); the following paragraphs with style `ListBullet` (`w:pStyle w:val="ListBullet"`) are that list's items. An item reads `Name (Marathi name): description`.
- A paragraph starting `PART 2` begins the translation. Then, repeated, in this order: a section header paragraph `Section N: LLL–HHH | <marathi title> (<english title>)` (the dash is U+2013 or an ASCII hyphen; LLL, HHH are zero padded ovi numbers), a context paragraph starting `संदर्भ:`, and a table. Table row 1 is the header with 5 cells (ovi, original Marathi, simple Marathi, Hindi, Easy English). Every other row has exactly 5 cells: [row number e.g. `001`, original Marathi, simple Marathi, Hindi, Easy English].
- The original Marathi cell ends with the printed verse number between double danda marks, e.g. `॥११९॥` (Devanagari digits U+0966-U+096F). It is an AUDIT value, not the identity: the identity is the row number in cell 1.
- After the last table come closing paragraphs (ignore them).
## API (all pure except main)
- `parse_docx(path) -> dict`: returns `{"sections": [{"section": int, "first": int, "last": int, "title_mr": str, "title_en": str, "context": str}], "ovis": [{"ovi": int, "section": int, "original_marathi": str, "simple_marathi": str, "hindi": str, "easy_english": str, "printed_number": int | None}], "packet": {"characters": [item], "locations": [item], "objects": [item]}, "mismatches": [{"ovi": int, "printed": int | None}], "source_sha256": str}` where item = `{"raw": str, "name": str, "name_mr": str, "description": str}` (name = text before the first " (", name_mr = text inside the first parentheses, description = text after the first ": " following them; any missing part is "" and `raw` always holds the full paragraph). `printed_number` = the LAST `॥digits॥` in the original Marathi cell converted to int (None when absent). `mismatches` lists every ovi whose printed_number is None or differs from its row number, in ovi order. `source_sha256` = sha256 hex of the docx file bytes.
- It must REFUSE a deviating layout by raising `LayoutError(ValueError)` with a clear message in each case: file is not a zip or has no `word/document.xml`; no `PART 2` paragraph; a section header that does not match the pattern; section numbers not 1,2,3... consecutive; a header paragraph not followed by a context paragraph and then a table; a table whose header row does not have 5 cells or whose data row does not have exactly 5 cells; a row number that is not an integer; a table's row numbers not exactly the integers FIRST..LAST of its section header, in order; sections not contiguous (a section's FIRST must be the previous LAST + 1, the first section starts at 1); an empty required cell (cells 1-5). It must never raise anything else on bad input (wrap lower-level errors from zipfile or XML into LayoutError).
- `write_outputs(parsed: dict, adhyay: int, out_root: Path) -> list[Path]`: refuses (raises `FileExistsError`) if any target exists; creates `out_root / f"adhyay_{adhyay:02d}" / "source" / "ovis.jsonl"` (one JSON object per line, UTF-8, `ensure_ascii=False`, each ovi record plus `"adhyay": adhyay`), `.../source/sections.json`, `.../source/import_report.json` (`{"adhyay", "ovi_count", "section_count", "mismatches", "source_sha256"}`) and `out_root / f"adhyay_{adhyay:02d}" / "research" / "packet.json"` (`{"adhyay", "characters", "locations", "objects"}`); returns the four paths.
- `main(argv=None) -> int`: `--docx PATH` (required), `--adhyay N` (int, required), `--out-root PATH` (default `ROOT / "canon"`). Calls parse_docx then write_outputs; prints one line `adhyay N: <ovi_count> ovis, <section_count> sections, <len(mismatches)> printed-number mismatches: <comma separated ovi numbers>`; returns 0; on `LayoutError` or `FileExistsError` prints `refused: <message>` and returns 2. `if __name__ == "__main__": raise SystemExit(main())`.
## Tests (table-driven; write a helper in the test file that builds a minimal valid synthetic .docx with `zipfile` (parts: `[Content_Types].xml`, `_rels/.rels`, `word/document.xml`) from a small Python description: two sections, e.g. ovis 1-2 and 3-5, with `PART 1` lists and `PART 2` tables; synthetic text only, ASCII or short invented Devanagari words, never real scripture)
1. Valid synthetic file: counts, section ranges, titles, contexts, printed_number parsing, packet items (name / name_mr / description / raw), empty mismatches list; `source_sha256` equals sha256 of the file.
2. Mismatch reporting: a row whose printed number differs, and a row with no printed number: both listed in `mismatches` with the right values.
3. Each refusal rule above has its own isolated test (a mutation of the valid file that violates ONLY that rule) asserting `LayoutError`: not a zip, no document.xml, no PART 2, bad section header, non-consecutive section numbers, header not followed by context + table, table header not 5 cells, data row not 5 cells, non-integer row number, row numbers out of order or not matching FIRST..LAST, non-contiguous sections, empty required cell.
4. `write_outputs`: creates the four files with the right content in `tmp_path`; a second call raises `FileExistsError` and leaves existing files unchanged.
5. `main`: success line and return 0 (capsys); `refused:` line and return 2 for a bad file; for an existing output folder.
6. REAL FILE test (skip with `pytest.mark.skipif` if the file is missing): `canon/test_inputs/Shri_Gajanan_Vijay_Chapter_2_Audited_Canon_Edition.docx` parses to exactly 148 ovis, 12 sections, ovi numbers 1..148 in order, section ranges starting 1 and ending 148 contiguous, and `mismatches` is exactly `[{"ovi": 118, "printed": 119}, {"ovi": 129, "printed": 119}]`; packet has 11 characters, 6 locations, 12 objects; ovi 1 original Marathi text starts with `जयजय अज अजिता`.
Reply with only the two FILE blocks:
FILE: scripts/pipeline/import_canon_docx.py
FILE: tests/test_import_canon_docx.py


## CURRENT MODULE scripts/pipeline/import_canon_docx.py
```python
from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from typing import Any, Dict, List, Optional, Tuple


class LayoutError(ValueError):
    """Raised when the DOCX layout deviates from the expected structure."""


NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def _sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _get_text(node: ET.Element) -> str:
    """Concatenate all w:t text under this node."""
    texts = []
    for t in node.findall(".//w:t", NS):
        if t.text:
            texts.append(t.text)
    return "".join(texts)


def _get_paragraph_text(para: ET.Element) -> str:
    return _get_text(para).strip()


def _get_cell_text(cell: ET.Element) -> str:
    """Cell text = its paragraphs joined by newline, each stripped."""
    paras = cell.findall("w:p", NS)
    lines = [_get_paragraph_text(p) for p in paras]
    return "\n".join(lines).strip()


def _get_style_val(para: ET.Element) -> Optional[str]:
    pPr = para.find("w:pPr", NS)
    if pPr is None:
        return None
    pStyle = pPr.find("w:pStyle", NS)
    if pStyle is None:
        return None
    return pStyle.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val")


def _parse_printed_number(text: str) -> Optional[int]:
    """Find the LAST occurrence of ॥digits॥ (Devanagari digits) and return as int."""
    # Devanagari digits U+0966-U+096F
    pattern = re.compile(r"॥([\u0966-\u096F]+)॥")
    matches = list(pattern.finditer(text))
    if not matches:
        return None
    last = matches[-1].group(1)
    # Convert Devanagari digits to int
    dev_to_int = {chr(0x0966 + i): str(i) for i in range(10)}
    ascii_digits = "".join(dev_to_int[ch] for ch in last)
    return int(ascii_digits)


def _parse_item_line(line: str) -> Dict[str, str]:
    """Parse 'Name (Marathi name): description' into parts."""
    raw = line
    name = ""
    name_mr = ""
    description = ""
    # Find first ' ('
    idx_paren = line.find(" (")
    if idx_paren != -1:
        name = line[:idx_paren].strip()
        rest = line[idx_paren + 2:]  # after ' ('
        idx_close = rest.find(")")
        if idx_close != -1:
            name_mr = rest[:idx_close].strip()
            after = rest[idx_close + 1:].lstrip()
            if after.startswith(":"):
                description = after[1:].strip()
            else:
                description = after
        else:
            # No closing paren, treat rest as name_mr
            name_mr = rest.strip()
    else:
        # No ' (', maybe has ': '
        idx_colon = line.find(": ")
        if idx_colon != -1:
            name = line[:idx_colon].strip()
            description = line[idx_colon + 2:].strip()
        else:
            name = line.strip()
    return {"raw": raw, "name": name, "name_mr": name_mr, "description": description}


def parse_docx(path: Path) -> Dict[str, Any]:
    source_sha256 = _sha256_of_file(path)

    # Open zip and read word/document.xml
    try:
        with zipfile.ZipFile(path, "r") as zf:
            if "word/document.xml" not in zf.namelist():
                raise LayoutError("missing word/document.xml in docx")
            xml_bytes = zf.read("word/document.xml")
    except zipfile.BadZipFile as e:
        raise LayoutError("file is not a valid zip") from e

    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as e:
        raise LayoutError("word/document.xml is not valid XML") from e

    body = root.find("w:body", NS)
    if body is None:
        raise LayoutError("word/document.xml has no w:body")

    # Iterate body children in order
    children = list(body)

    # State machine
    state = "BEFORE_PART1"  # BEFORE_PART1, IN_PART1, BEFORE_PART2, IN_PART2_SECTIONS, AFTER_TABLES
    part1_lists: Dict[str, List[Dict[str, str]]] = {
        "characters": [],
        "locations": [],
        "objects": [],
    }
    current_part1_list: Optional[str] = None

    sections: List[Dict[str, Any]] = []
    ovis: List[Dict[str, Any]] = []
    mismatches: List[Dict[str, Any]] = []

    i = 0
    while i < len(children):
        child = children[i]
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag

        if tag == "p":
            para_text = _get_paragraph_text(child)
            style = _get_style_val(child)

            if state == "BEFORE_PART1":
                if para_text.startswith("PART 1"):
                    state = "IN_PART1"
                    current_part1_list = None
                # else ignore
            elif state == "IN_PART1":
                if para_text.startswith("PART 2"):
                    state = "BEFORE_PART2"
                elif para_text.startswith("1. Characters"):
                    current_part1_list = "characters"
                elif para_text.startswith("2. Locations"):
                    current_part1_list = "locations"
                elif para_text.startswith("3. Key Objects"):
                    current_part1_list = "objects"
                elif style == "ListBullet" and current_part1_list is not None:
                    item = _parse_item_line(para_text)
                    part1_lists[current_part1_list].append(item)
                # else ignore other paragraphs in PART 1
            elif state == "BEFORE_PART2":
                if para_text.startswith("PART 2"):
                    state = "IN_PART2_SECTIONS"
                # else ignore
            elif state == "IN_PART2_SECTIONS":
                # Expect section header
                # Pattern: Section N: LLL–HHH | <marathi title> (<english title>)
                # dash can be U+2013 or ASCII hyphen
                m = re.match(
                    r"^Section\s+(\d+):\s*(\d+)\s*[\u2013-]\s*(\d+)\s*\|\s*(.+?)\s*\((.+?)\)\s*$",
                    para_text,
                )
                if not m:
                    raise LayoutError(f"section header does not match pattern: {para_text!r}")
                sec_num = int(m.group(1))
                first = int(m.group(2))
                last = int(m.group(3))
                title_mr = m.group(4).strip()
                title_en = m.group(5).strip()

                # Validate section numbers consecutive
                expected_sec = len(sections) + 1
                if sec_num != expected_sec:
                    raise LayoutError(f"section numbers not consecutive: expected {expected_sec}, got {sec_num}")

                # Validate contiguous ovi ranges
                if sections:
                    prev_last = sections[-1]["last"]
                    if first != prev_last + 1:
                        raise LayoutError(f"sections not contiguous: previous last={prev_last}, this first={first}")
                else:
                    if first != 1:
                        raise LayoutError(f"first section must start at 1, got {first}")

                if first > last:
                    raise LayoutError(f"section first > last: {first} > {last}")

                # Next paragraph must be context (starts with संदर्भ:)
                i += 1
                if i >= len(children):
                    raise LayoutError("section header not followed by context paragraph")
                context_child = children[i]
                if context_child.tag.split("}")[-1] != "p":
                    raise LayoutError("section header not followed by context paragraph")
                context_text = _get_paragraph_text(context_child)
                if not context_text.startswith("संदर्भ:"):
                    raise LayoutError(f"context paragraph does not start with 'संदर्भ:': {context_text!r}")
                context = context_text[len("संदर्भ:"):].strip()

                # Next must be a table
                i += 1
                if i >= len(children):
                    raise LayoutError("context paragraph not followed by table")
                table_child = children[i]
                if table_child.tag.split("}")[-1] != "tbl":
                    raise LayoutError("context paragraph not followed by table")

                # Parse table
                rows = table_child.findall("w:tr", NS)
                if not rows:
                    raise LayoutError("table has no rows")

                # Header row
                header_cells = rows[0].findall("w:tc", NS)
                if len(header_cells) != 5:
                    raise LayoutError(f"table header row does not have 5 cells: got {len(header_cells)}")

                # Data rows
                data_rows = rows[1:]
                if len(data_rows) != (last - first + 1):
                    raise LayoutError(f"table data row count {len(data_rows)} does not match section range {first}-{last}")

                section_ovis = []
                for row_idx, row in enumerate(data_rows):
                    cells = row.findall("w:tc", NS)
                    if len(cells) != 5:
                        raise LayoutError(f"data row {row_idx} does not have 5 cells: got {len(cells)}")

                    cell_texts = [_get_cell_text(c) for c in cells]

                    # Cell 1: row number (ovi identity)
                    row_num_str = cell_texts[0].strip()
                    try:
                        row_num = int(row_num_str)
                    except ValueError:
                        raise LayoutError(f"row number not an integer: {row_num_str!r}")

                    expected_row_num = first + row_idx
                    if row_num != expected_row_num:
                        raise LayoutError(f"row numbers out of order or mismatch: expected {expected_row_num}, got {row_num}")

                    # Cells 2-5: original_marathi, simple_marathi, hindi, easy_english
                    original_marathi = cell_texts[1]
                    simple_marathi = cell_texts[2]
                    hindi = cell_texts[3]
                    easy_english = cell_texts[4]

                    # Check empty required cells (1-5)
                    for ci, ct in enumerate(cell_texts):
                        if not ct.strip():
                            raise LayoutError(f"empty required cell at row {row_num}, column {ci+1}")

                    printed_number = _parse_printed_number(original_marathi)

                    ovi_record = {
                        "ovi": row_num,
                        "section": sec_num,
                        "original_marathi": original_marathi,
                        "simple_marathi": simple_marathi,
                        "hindi": hindi,
                        "easy_english": easy_english,
                        "printed_number": printed_number,
                    }
                    section_ovis.append(ovi_record)
                    ovis.append(ovi_record)

                    if printed_number is None or printed_number != row_num:
                        mismatches.append({"ovi": row_num, "printed": printed_number})

                sections.append({
                    "section": sec_num,
                    "first": first,
                    "last": last,
                    "title_mr": title_mr,
                    "title_en": title_en,
                    "context": context,
                })

                state = "IN_PART2_SECTIONS"  # continue for next section
            elif state == "AFTER_TABLES":
                # Ignore closing paragraphs
                pass

        elif tag == "tbl" and state == "IN_PART2_SECTIONS":
            # A table not preceded by header+context is invalid
            raise LayoutError("unexpected table without section header and context")

        i += 1

    if state != "IN_PART2_SECTIONS" and state != "AFTER_TABLES":
        # If we never reached PART 2
        if state == "BEFORE_PART2" or state == "IN_PART1" or state == "BEFORE_PART1":
            raise LayoutError("no PART 2 paragraph found")

    # Final validation: ovi numbers should be 1..N contiguous
    if ovis:
        expected = 1
        for o in ovis:
            if o["ovi"] != expected:
                raise LayoutError(f"ovis not contiguous: expected {expected}, got {o['ovi']}")
            expected += 1

    packet = {
        "characters": part1_lists["characters"],
        "locations": part1_lists["locations"],
        "objects": part1_lists["objects"],
    }

    return {
        "sections": sections,
        "ovis": ovis,
        "packet": packet,
        "mismatches": mismatches,
        "source_sha256": source_sha256,
    }


def write_outputs(parsed: Dict[str, Any], adhyay: int, out_root: Path) -> List[Path]:
    adhyay_dir = out_root / f"adhyay_{adhyay:02d}"
    source_dir = adhyay_dir / "source"
    research_dir = adhyay_dir / "research"

    # Check if any target exists
    targets = [
        source_dir / "ovis.jsonl",
        source_dir / "sections.json",
        source_dir / "import_report.json",
        research_dir / "packet.json",
    ]
    for t in targets:
        if t.exists():
            raise FileExistsError(f"output already exists: {t}")

    # Create directories
    source_dir.mkdir(parents=True, exist_ok=False)
    research_dir.mkdir(parents=True, exist_ok=False)

    # ovis.jsonl
    with (source_dir / "ovis.jsonl").open("w", encoding="utf-8") as f:
        for ovi in parsed["ovis"]:
            rec = dict(ovi)
            rec["adhyay"] = adhyay
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # sections.json
    with (source_dir / "sections.json").open("w", encoding="utf-8") as f:
        json.dump(parsed["sections"], f, ensure_ascii=False, indent=2)

    # import_report.json
    import_report = {
        "adhyay": adhyay,
        "ovi_count": len(parsed["ovis"]),
        "section_count": len(parsed["sections"]),
        "mismatches": parsed["mismatches"],
        "source_sha256": parsed["source_sha256"],
    }
    with (source_dir / "import_report.json").open("w", encoding="utf-8") as f:
        json.dump(import_report, f, ensure_ascii=False, indent=2)

    # packet.json
    packet = {
        "adhyay": adhyay,
        "characters": parsed["packet"]["characters"],
        "locations": parsed["packet"]["locations"],
        "objects": parsed["packet"]["objects"],
    }
    with (research_dir / "packet.json").open("w", encoding="utf-8") as f:
        json.dump(packet, f, ensure_ascii=False, indent=2)

    return targets


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Import Audited Canon Edition DOCX")
    parser.add_argument("--docx", type=Path, required=True, help="Path to the .docx file")
    parser.add_argument("--adhyay", type=int, required=True, help="Adhyay number")
    parser.add_argument("--out-root", type=Path, default=Path(__file__).resolve().parents[2] / "canon", help="Output root directory")
    args = parser.parse_args(argv)

    try:
        parsed = parse_docx(args.docx)
        write_outputs(parsed, args.adhyay, args.out_root)
        mismatch_ovis = [str(m["ovi"]) for m in parsed["mismatches"]]
        print(f"adhyay {args.adhyay}: {len(parsed['ovis'])} ovis, {len(parsed['sections'])} sections, {len(parsed['mismatches'])} printed-number mismatches: {', '.join(mismatch_ovis)}")
        return 0
    except LayoutError as e:
        print(f"refused: {e}")
        return 2
    except FileExistsError as e:
        print(f"refused: {e}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

```

## CURRENT TESTS tests/test_import_canon_docx.py
```python
from __future__ import annotations

import hashlib
import io
import json
import zipfile
from pathlib import Path
from typing import Dict, List, Optional
from xml.etree import ElementTree as ET

import pytest

from scripts.pipeline.import_canon_docx import parse_docx, write_outputs, main, LayoutError


NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def _make_docx_xml(parts: Dict[str, str]) -> bytes:
    """Build a minimal docx from parts dict: content_types, rels, document.xml"""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in parts.items():
            zf.writestr(name, content)
    return buf.getvalue()


def _build_document_xml(body_children: List[ET.Element]) -> str:
    root = ET.Element("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}document")
    body = ET.SubElement(root, "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}body")
    for child in body_children:
        body.append(child)
    return ET.tostring(root, encoding="unicode")


def _p(text: str, style: Optional[str] = None) -> ET.Element:
    """Create a paragraph element with given text and optional style."""
    p = ET.Element("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p")
    if style:
        pPr = ET.SubElement(p, "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pPr")
        pStyle = ET.SubElement(pPr, "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pStyle")
        pStyle.set("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val", style)
    r = ET.SubElement(p, "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r")
    t = ET.SubElement(r, "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t")
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text
    return p


def _tbl(rows: List[List[str]]) -> ET.Element:
    """Create a table element from list of rows (each row is list of cell texts)."""
    tbl = ET.Element("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tbl")
    for row_cells in rows:
        tr = ET.SubElement(tbl, "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tr")
        for cell_text in row_cells:
            tc = ET.SubElement(tr, "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tc")
            p = ET.SubElement(tc, "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p")
            r = ET.SubElement(p, "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r")
            t = ET.SubElement(r, "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t")
            t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            t.text = cell_text
    return tbl


def _valid_docx_bytes() -> bytes:
    """Build a valid synthetic docx with PART 1 and PART 2, two sections."""
    # PART 1
    part1_para = _p("PART 1")
    char_heading = _p("1. Characters")
    char_item1 = _p("Gajanan (गजानन): The protagonist", style="ListBullet")
    char_item2 = _p("Vijay (विजय): The companion", style="ListBullet")
    loc_heading = _p("2. Locations")
    loc_item1 = _p("Kashi (काशी): Holy city", style="ListBullet")
    obj_heading = _p("3. Key Objects")
    obj_item1 = _p("Mala (माला): Prayer beads", style="ListBullet")

    # PART 2
    part2_para = _p("PART 2")

    # Section 1: ovis 1-2
    sec1_header = _p("Section 1: 001–002 | प्रथम अध्याय (First Chapter)")
    sec1_context = _p("संदर्भ: This is the first section context.")
    sec1_table = _tbl([
        ["ovi", "original Marathi", "simple Marathi", "Hindi", "Easy English"],
        ["001", "जयजय अज अजिता ॥१॥", "सरल मराठी 1", "हिंदी 1", "Easy English 1"],
        ["002", "श्री गजानन विजय ॥२॥", "सरल मराठी 2", "हिंदी 2", "Easy English 2"],
    ])

    # Section 2: ovis 3-5
    sec2_header = _p("Section 2: 003–005 | द्वितीय अध्याय (Second Chapter)")
    sec2_context = _p("संदर्भ: This is the second section context.")
    sec2_table = _tbl([
        ["ovi", "original Marathi", "simple Marathi", "Hindi", "Easy English"],
        ["003", "ओवि तीन ॥३॥", "सरल मराठी 3", "हिंदी 3", "Easy English 3"],
        ["004", "ओवि चार ॥४॥", "सरल मराठी 4", "हिंदी 4", "Easy English 4"],
        ["005", "ओवि पांच ॥५॥", "सरल मराठी 5", "हिंदी 5", "Easy English 5"],
    ])

    body_children = [
        part1_para,
        char_heading,
        char_item1,
        char_item2,
        loc_heading,
        loc_item1,
        obj_heading,
        obj_item1,
        part2_para,
        sec1_header,
        sec1_context,
        sec1_table,
        sec2_header,
        sec2_context,
        sec2_table,
    ]

    document_xml = _build_document_xml(body_children)

    content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""

    rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

    parts = {
        "[Content_Types].xml": content_types,
        "_rels/.rels": rels,
        "word/document.xml": document_xml,
    }
    return _make_docx_xml(parts)


def _write_docx(tmp_path: Path, content: bytes) -> Path:
    p = tmp_path / "test.docx"
    p.write_bytes(content)
    return p


class TestParseDocx:
    def test_valid_synthetic(self, tmp_path: Path):
        docx_bytes = _valid_docx_bytes()
        docx_path = _write_docx(tmp_path, docx_bytes)

        parsed = parse_docx(docx_path)

        # Check source_sha256
        assert parsed["source_sha256"] == hashlib.sha256(docx_bytes).hexdigest()

        # Sections
        assert len(parsed["sections"]) == 2
        sec1 = parsed["sections"][0]
        assert sec1["section"] == 1
        assert sec1["first"] == 1
        assert sec1["last"] == 2
        assert sec1["title_mr"] == "प्रथम अध्याय"
        assert sec1["title_en"] == "First Chapter"
        assert sec1["context"] == "This is the first section context."

        sec2 = parsed["sections"][1]
        assert sec2["section"] == 2
        assert sec2["first"] == 3
        assert sec2["last"] == 5
        assert sec2["title_mr"] == "द्वितीय अध्याय"
        assert sec2["title_en"] == "Second Chapter"
        assert sec2["context"] == "This is the second section context."

        # Ovis
        assert len(parsed["ovis"]) == 5
        for idx, ovi in enumerate(parsed["ovis"], 1):
            assert ovi["ovi"] == idx
            assert ovi["section"] == (1 if idx <= 2 else 2)
            assert ovi["printed_number"] == idx

        # Mismatches empty
        assert parsed["mismatches"] == []

        # Packet
        packet = parsed["packet"]
        assert len(packet["characters"]) == 2
        c1 = packet["characters"][0]
        assert c1["raw"] == "Gajanan (गजानन): The protagonist"
        assert c1["name"] == "Gajanan"
        assert c1["name_mr"] == "गजानन"
        assert c1["description"] == "The protagonist"

        c2 = packet["characters"][1]
        assert c2["name"] == "Vijay"
        assert c2["name_mr"] == "विजय"
        assert c2["description"] == "The companion"

        assert len(packet["locations"]) == 1
        l1 = packet["locations"][0]
        assert l1["name"] == "Kashi"
        assert l1["name_mr"] == "काशी"
        assert l1["description"] == "Holy city"

        assert len(packet["objects"]) == 1
        o1 = packet["objects"][0]
        assert o1["name"] == "Mala"
        assert o1["name_mr"] == "माला"
        assert o1["description"] == "Prayer beads"

    def test_mismatch_reporting(self, tmp_path: Path):
        # Build docx with mismatches: ovi 2 printed 5, ovi 4 no printed number
        part1_para = _p("PART 1")
        part2_para = _p("PART 2")
        sec1_header = _p("Section 1: 001–004 | Test (Test)")
        sec1_context = _p("संदर्भ: context")
        sec1_table = _tbl([
            ["ovi", "original Marathi", "simple Marathi", "Hindi", "Easy English"],
            ["001", "ओवि १ ॥१॥", "s1", "h1", "e1"],
            ["002", "ओवि २ ॥५॥", "s2", "h2", "e2"],  # printed 5 != 2
            ["003", "ओवि ३ ॥३॥", "s3", "h3", "e3"],
            ["004", "ओवि ४ कोई नंबर नहीं", "s4", "h4", "e4"],  # no printed number
        ])

        body_children = [part1_para, part2_para, sec1_header, sec1_context, sec1_table]
        document_xml = _build_document_xml(body_children)

        content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""
        rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

        parts = {
            "[Content_Types].xml": content_types,
            "_rels/.rels": rels,
            "word/document.xml": document_xml,
        }
        docx_bytes = _make_docx_xml(parts)
        docx_path = _write_docx(tmp_path, docx_bytes)

        parsed = parse_docx(docx_path)

        assert len(parsed["ovis"]) == 4
        mismatches = parsed["mismatches"]
        assert len(mismatches) == 2
        assert mismatches[0] == {"ovi": 2, "printed": 5}
        assert mismatches[1] == {"ovi": 4, "printed": None}

    # Refusal tests
    def test_refuse_not_a_zip(self, tmp_path: Path):
        bad = tmp_path / "bad.docx"
        bad.write_bytes(b"not a zip")
        with pytest.raises(LayoutError, match="not a valid zip"):
            parse_docx(bad)

    def test_refuse_no_document_xml(self, tmp_path: Path):
        # Zip without word/document.xml
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("[Content_Types].xml", "<Types/>")
            zf.writestr("_rels/.rels", "<Relationships/>")
        docx_path = _write_docx(tmp_path, buf.getvalue())
        with pytest.raises(LayoutError, match="missing word/document.xml"):
            parse_docx(docx_path)

    def test_refuse_no_part2(self, tmp_path: Path):
        # Valid but missing PART 2
        part1_para = _p("PART 1")
        char_heading = _p("1. Characters")
        char_item = _p("A (अ): desc", style="ListBullet")
        body_children = [part1_para, char_heading, char_item]
        document_xml = _build_document_xml(body_children)

        content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""
        rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""
        parts = {
            "[Content_Types].xml": content_types,
            "_rels/.rels": rels,
            "word/document.xml": document_xml,
        }
        docx_bytes = _make_docx_xml(parts)
        docx_path = _write_docx(tmp_path, docx_bytes)

        with pytest.raises(LayoutError, match="no PART 2 paragraph found"):
            parse_docx(docx_path)

    def test_refuse_bad_section_header(self, tmp_path: Path):
        part1_para = _p("PART 1")
        part2_para = _p("PART 2")
        bad_header = _p("Section 1 001–002 | Title (En)")
        context = _p("संदर्भ: ctx")
        table = _tbl([["ovi", "o", "s", "h", "e"], ["001", "t", "s", "h", "e"]])
        body_children = [part1_para, part2_para, bad_header, context, table]
        document_xml = _build_document_xml(body_children)

        content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""
        rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""
        parts = {
            "[Content_Types].xml": content_types,
            "_rels/.rels": rels,
            "word/document.xml": document_xml,
        }
        docx_bytes = _make_docx_xml(parts)
        docx_path = _write_docx(tmp_path, docx_bytes)

        with pytest.raises(LayoutError, match="section header does not match pattern"):
            parse_docx(docx_path)

    def test_refuse_non_consecutive_section_numbers(self, tmp_path: Path):
        part1_para = _p("PART 1")
        part2_para = _p("PART 2")
        sec1_header = _p("Section 1: 001–002 | T (E)")
        sec1_context = _p("संदर्भ: c")
        sec1_table = _tbl([["ovi", "o", "s", "h", "e"], ["001", "t", "s", "h", "e"], ["002", "t", "s", "h", "e"]])
        sec2_header = _p("Section 3: 003–004 | T (E)")  # skip 2
        sec2_context = _p("संदर्भ: c")
        sec2_table = _tbl([["ovi", "o", "s", "h", "e"], ["003", "t", "s", "h", "e"], ["004", "t", "s", "h", "e"]])
        body_children = [part1_para, part2_para, sec1_header, sec1_context, sec1_table, sec2_header, sec2_context, sec2_table]
        document_xml = _build_document_xml(body_children)

        content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""
        rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""
        parts = {
            "[Content_Types].xml": content_types,
            "_rels/.rels": rels,
            "word/document.xml": document_xml,
        }
        docx_bytes = _make_docx_xml(parts)
        docx_path = _write_docx(tmp_path, docx_bytes)

        with pytest.raises(LayoutError, match="section numbers not consecutive"):
            parse_docx(docx_path)

    def test_refuse_header_not_followed_by_context_and_table(self, tmp_path: Path):
        part1_para = _p("PART 1")
        part2_para = _p("PART 2")
        sec1_header = _p("Section 1: 001–002 | T (E)")
        # Missing context, directly table
        sec1_table = _tbl([["ovi", "o", "s", "h", "e"], ["001", "t", "s", "h", "e"], ["002", "t", "s", "h", "e"]])
        body_children = [part1_para, part2_para, sec1_header, sec1_table]
        document_xml = _build_document_xml(body_children)

        content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""
        rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""
        parts = {
            "[Content_Types].xml": content_types,
            "_rels/.rels": rels,
            "word/document.xml": document_xml,
        }
        docx_bytes = _make_docx_xml(parts)
        docx_path = _write_docx(tmp_path, docx_bytes)

        with pytest.raises(LayoutError, match="section header not followed by context paragraph"):
            parse_docx(docx_path)

    def test_refuse_table_header_not_5_cells(self, tmp_path: Path):
        part1_para = _p("PART 1")
        part2_para = _p("PART 2")
        sec1_header = _p("Section 1: 001–002 | T (E)")
        sec1_context = _p("संदर्भ: c")
        # Header with 4 cells
        sec1_table = _tbl([
            ["ovi", "o", "s", "h"],  # 4 cells
            ["001", "t", "s", "h", "e"],
            ["002", "t", "s", "h", "e"],
        ])
        body_children = [part1_para, part2_para, sec1_header, sec1_context, sec1_table]
        document_xml = _build_document_xml(body_children)

        content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""
        rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""
        parts = {
            "[Content_Types].xml": content_types,
            "_rels/.rels": rels,
            "word/document.xml": document_xml,
        }
        docx_bytes = _make_docx_xml(parts)
        docx_path = _write_docx(tmp_path, docx_bytes)

        with pytest.raises(LayoutError, match="table header row does not have 5 cells"):
            parse_docx(docx_path)

    def test_refuse_data_row_not_5_cells(self, tmp_path: Path):
        part1_para = _p("PART 1")
        part2_para = _p("PART 2")
        sec1_header = _p("Section 1: 001–002 | T (E)")
        sec1_context = _p("संदर्भ: c")
        sec1_table = _tbl([
            ["ovi", "o", "s", "h", "e"],
            ["001", "t", "s", "h"],  # 4 cells
            ["002", "t", "s", "h", "e"],
        ])
        body_children = [part1_para, part2_para, sec1_header, sec1_context, sec1_table]
        document_xml = _build_document_xml(body_children)

        content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""
        rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""
        parts = {
            "[Content_Types].xml": content_types,
            "_rels/.rels": rels,
            "word/document.xml": document_xml,
        }
        docx_bytes = _make_docx_xml(parts)
        docx_path = _write_docx(tmp_path, docx_bytes)

        with pytest.raises(LayoutError, match="data row 0 does not have 5 cells"):
            parse_docx(docx_path)

    def test_refuse_non_integer_row_number(self, tmp_path: Path):
        part1_para = _p("PART 1")
        part2_para = _p("PART 2")
        sec1_header = _p("Section 1: 001–002 | T (E)")
        sec1_context = _p("संदर्भ: c")
        sec1_table = _tbl([
            ["ovi", "o", "s", "h", "e"],
            ["abc", "t", "s", "h", "e"],
            ["002", "t", "s", "h", "e"],
        ])
        body_children = [part1_para, part2_para, sec1_header, sec1_context, sec1_table]
        document_xml = _build_document_xml(body_children)

        content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""
        rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""
        parts = {
            "[Content_Types].xml": content_types,
            "_rels/.rels": rels,
            "word/document.xml": document_xml,
        }
        docx_bytes = _make_docx_xml(parts)
        docx_path = _write_docx(tmp_path, docx_bytes)

        with pytest.raises(LayoutError, match="row number not an integer"):
            parse_docx(docx_path)

    def test_refuse_row_numbers_out_of_order_or_mismatch(self, tmp_path: Path):
        part1_para = _p("PART 1")
        part2_para = _p("PART 2")
        sec1_header = _p("Section 1: 001–002 | T (E)")
        sec1_context = _p("संदर्भ: c")
        sec1_table = _tbl([
            ["ovi", "o", "s", "h", "e"],
            ["002", "t", "s", "h", "e"],  # first row is 002, expected 001
            ["001", "t", "s", "h", "e"],
        ])
        body_children = [part1_para, part2_para, sec1_header, sec1_context, sec1_table]
        document_xml = _build_document_xml(body_children)

        content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""
        rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""
        parts = {
            "[Content_Types].xml": content_types,
            "_rels/.rels": rels,
            "word/document.xml": document_xml,
        }
        docx_bytes = _make_docx_xml(parts)
        docx_path = _write_docx(tmp_path, docx_bytes)

        with pytest.raises(LayoutError, match="row numbers out of order or mismatch"):
            parse_docx(docx_path)

    def test_refuse_non_contiguous_sections(self, tmp_path: Path):
        part1_para = _p("PART 1")
        part2_para = _p("PART 2")
        sec1_header = _p("Section 1: 001–002 | T (E)")
        sec1_context = _p("संदर्भ: c")
        sec1_table = _tbl([["ovi", "o", "s", "h", "e"], ["001", "t", "s", "h", "e"], ["002", "t", "s", "h", "e"]])
        sec2_header = _p("Section 2: 004–005 | T (E)")  # gap: missing 3
        sec2_context = _p("संदर्भ: c")
        sec2_table = _tbl([["ovi", "o", "s", "h", "e"], ["004", "t", "s", "h", "e"], ["005", "t", "s", "h", "e"]])
        body_children = [part1_para, part2_para, sec1_header, sec1_context, sec1_table, sec2_header, sec2_context, sec2_table]
        document_xml = _build_document_xml(body_children)

        content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""
        rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""
        parts = {
            "[Content_Types].xml": content_types,
            "_rels/.rels": rels,
            "word/document.xml": document_xml,
        }
        docx_bytes = _make_docx_xml(parts)
        docx_path = _write_docx(tmp_path, docx_bytes)

        with pytest.raises(LayoutError, match="sections not contiguous"):
            parse_docx(docx_path)

    def test_refuse_empty_required_cell(self, tmp_path: Path):
        part1_para = _p("PART 1")
        part2_para = _p("PART 2")
        sec1_header = _p("Section 1: 001–001 | T (E)")
        sec1_context = _p("संदर्भ: c")
        sec1_table = _tbl([
            ["ovi", "o", "s", "h", "e"],
            ["001", "", "s", "h", "e"],  # empty original Marathi
        ])
        body_children = [part1_para, part2_para, sec1_header, sec1_context, sec1_table]
        document_xml = _build_document_xml(body_children)

        content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""
        rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""
        parts = {
            "[Content_Types].xml": content_types,
            "_rels/.rels": rels,
            "word/document.xml": document_xml,
        }
        docx_bytes = _make_docx_xml(parts)
        docx_path = _write_docx(tmp_path, docx_bytes)

        with pytest.raises(LayoutError, match="empty required cell"):
            parse_docx(docx_path)


class TestWriteOutputs:
    def test_write_outputs_creates_files(self, tmp_path: Path):
        parsed = {
            "sections": [
                {"section": 1, "first": 1, "last": 2, "title_mr": "T1", "title_en": "E1", "context": "C1"},
                {"section": 2, "first": 3, "last": 3, "title_mr": "T2", "title_en": "E2", "context": "C2"},
            ],
            "ovis": [
                {"ovi": 1, "section": 1, "original_marathi": "o1", "simple_marathi": "s1", "hindi": "h1", "easy_english": "e1", "printed_number": 1},
                {"ovi": 2, "section": 1, "original_marathi": "o2", "simple_marathi": "s2", "hindi": "h2", "easy_english": "e2", "printed_number": 2},
                {"ovi": 3, "section": 2, "original_marathi": "o3", "simple_marathi": "s3", "hindi": "h3", "easy_english": "e3", "printed_number": 3},
            ],
            "packet": {
                "characters": [{"raw": "r1", "name": "n1", "name_mr": "nm1", "description": "d1"}],
                "locations": [],
                "objects": [],
            },
            "mismatches": [],
            "source_sha256": "abc123",
        }
        out_root = tmp_path / "out"
        paths = write_outputs(parsed, 5, out_root)

        assert len(paths) == 4
        for p in paths:
            assert p.exists()

        # Check ovis.jsonl
        ovis_lines = (out_root / "adhyay_05" / "source" / "ovis.jsonl").read_text(encoding="utf-8").strip().splitlines()
        assert len(ovis_lines) == 3
        for line in ovis_lines:
            rec = json.loads(line)
            assert "adhyay" in rec and rec["adhyay"] == 5

        # sections.json
        sections = json.loads((out_root / "adhyay_05" / "source" / "sections.json").read_text(encoding="utf-8"))
        assert len(sections) == 2

        # import_report.json
        report = json.loads((out_root / "adhyay_05" / "source" / "import_report.json").read_text(encoding="utf-8"))
        assert report["adhyay"] == 5
        assert report["ovi_count"] == 3
        assert report["section_count"] == 2
        assert report["mismatches"] == []
        assert report["source_sha256"] == "abc123"

        # packet.json
        packet = json.loads((out_root / "adhyay_05" / "research" / "packet.json").read_text(encoding="utf-8"))
        assert packet["adhyay"] == 5
        assert len(packet["characters"]) == 1

    def test_write_outputs_refuses_existing(self, tmp_path: Path):
        parsed = {
            "sections": [],
            "ovis": [],
            "packet": {"characters": [], "locations": [], "objects": []},
            "mismatches": [],
            "source_sha256": "x",
        }
        out_root = tmp_path / "out"
        write_outputs(parsed, 1, out_root)
        with pytest.raises(FileExistsError):
            write_outputs(parsed, 1, out_root)
        # Ensure files unchanged (just check they still exist)
        assert (out_root / "adhyay_01" / "source" / "ovis.jsonl").exists()


class TestMain:
    def test_main_success(self, tmp_path: Path, capsys):
        docx_bytes = _valid_docx_bytes()
        docx_path = _write_docx(tmp_path, docx_bytes)
        out_root = tmp_path / "out"

        ret = main(["--docx", str(docx_path), "--adhyay", "2", "--out-root", str(out_root)])
        assert ret == 0
        captured = capsys.readouterr()
        assert "adhyay 2: 5 ovis, 2 sections, 0 printed-number mismatches:" in captured.out

    def test_main_refused_layout_error(self, tmp_path: Path, capsys):
        # Not a zip
        bad = tmp_path / "bad.docx"
        bad.write_bytes(b"not a zip")
        out_root = tmp_path / "out"

        ret = main(["--docx", str(bad), "--adhyay", "1", "--out-root", str(out_root)])
        assert ret == 2
        captured = capsys.readouterr()
        assert "refused:" in captured.out

    def test_main_refused_file_exists(self, tmp_path: Path, capsys):
        docx_bytes = _valid_docx_bytes()
        docx_path = _write_docx(tmp_path, docx_bytes)
        out_root = tmp_path / "out"

        # First run succeeds
        ret = main(["--docx", str(docx_path), "--adhyay", "1", "--out-root", str(out_root)])
        assert ret == 0
        # Second run refuses
        ret = main(["--docx", str(docx_path), "--adhyay", "1", "--out-root", str(out_root)])
        assert ret == 2
        captured = capsys.readouterr()
        assert "refused:" in captured.out


@pytest.mark.skipif(
    not (Path(__file__).resolve().parents[1] / "canon" / "test_inputs" / "Shri_Gajanan_Vijay_Chapter_2_Audited_Canon_Edition.docx").exists(),
    reason="Real canon docx not present"
)
class TestRealFile:
    def test_real_file_parses_correctly(self):
        repo_root = Path(__file__).resolve().parents[1]
        docx_path = repo_root / "canon" / "test_inputs" / "Shri_Gajanan_Vijay_Chapter_2_Audited_Canon_Edition.docx"
        parsed = parse_docx(docx_path)

        assert len(parsed["ovis"]) == 148
        assert len(parsed["sections"]) == 12
        # Ovi numbers 1..148 in order
        for idx, ovi in enumerate(parsed["ovis"], 1):
            assert ovi["ovi"] == idx
        # Sections contiguous, first starts at 1, last ends at 148
        assert parsed["sections"][0]["first"] == 1
        assert parsed["sections"][-1]["last"] == 148
        for i in range(1, len(parsed["sections"])):
            assert parsed["sections"][i]["first"] == parsed["sections"][i-1]["last"] + 1

        # Mismatches exactly as specified
        assert parsed["mismatches"] == [{"ovi": 118, "printed": 119}, {"ovi": 129, "printed": 119}]

        # Packet counts
        assert len(parsed["packet"]["characters"]) == 11
        assert len(parsed["packet"]["locations"]) == 6
        assert len(parsed["packet"]["objects"]) == 12

        # Ovi 1 original Marathi starts with जयजय अज अजिता
        assert parsed["ovis"][0]["original_marathi"].startswith("जयजय अज अजिता")

```

## NOTE (two earlier attempts, 14 of 20 tests fail the same way)
Most failures are `LayoutError: no PART 2 paragraph found`, on BOTH the real file and the synthetic documents, so the cause is common: the way paragraphs are found or their text is read (or the way the synthetic test document is built so that the module cannot find them). Think carefully: trace one tiny synthetic document through `parse_docx` by hand, step by step, find where `PART 2` is lost, and fix the root cause in the right file (module or test helper). In the real file the PART 2 paragraph text is `PART 2: COMPLETE TRILINGUAL TRANSLATION (OVIS 1 TO 148 — AUDITED EDITION)` and it is a direct child `w:p` of `w:body`; the body also contains `w:tbl` children and a final `w:sectPr`. Also check that a refusal test mutates ONLY the rule it names and that tests asserting a regex match the real message text. Return BOTH complete FILE blocks.
