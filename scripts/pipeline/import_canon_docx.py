from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from typing import Any, Dict, List, Optional


class LayoutError(ValueError):
    """Raised when the DOCX layout deviates from the expected structure."""


NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

# Section header pattern: Section N: LLL–HHH | <marathi title> (<english title>)
# Dash can be U+2013 (en-dash) or ASCII hyphen
SECTION_HEADER_PATTERN = re.compile(
    r"^Section\s+(\d+):\s*(\d+)\s*[\u2013-]\s*(\d+)\s*\|\s*(.+?)\s*\((.+?)\)\s*$"
)


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
    state = "BEFORE_PART1"  # BEFORE_PART1, IN_PART1, IN_PART2_SECTIONS, AFTER_TABLES
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
                    state = "IN_PART2_SECTIONS"
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
            elif state == "IN_PART2_SECTIONS":
                # Expect section header
                m = SECTION_HEADER_PATTERN.match(para_text)
                if m:
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

                    # Stay in IN_PART2_SECTIONS for next section
                else:
                    # Not a section header
                    if not sections:
                        # First section header must match
                        raise LayoutError(f"section header does not match pattern: {para_text!r}")
                    else:
                        # Closing paragraphs after last table - ignore this and all subsequent
                        state = "AFTER_TABLES"
            elif state == "AFTER_TABLES":
                # Ignore closing paragraphs
                pass

        elif tag == "tbl" and state == "IN_PART2_SECTIONS":
            # A table not preceded by header+context is invalid
            raise LayoutError("unexpected table without section header and context")

        i += 1

    if state not in ("IN_PART2_SECTIONS", "AFTER_TABLES"):
        # If we never reached PART 2
        if state in ("BEFORE_PART1", "IN_PART1"):
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
