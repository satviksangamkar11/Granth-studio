from __future__ import annotations

import hashlib
import io
import json
import zipfile
from pathlib import Path
from typing import Dict, List, Optional
from xml.etree import ElementTree as ET

import pytest

from scripts.pipeline.import_canon_docx import parse_docx, write_outputs, main, LayoutError, _parse_item_line


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


class TestParseItemLine:
    def test_colon_before_paren(self):
        # GAP 1: colon-space before first ' ('
        line = "A / B: The text (94-95) more"
        result = _parse_item_line(line)
        assert result["name"] == "A / B"
        assert result["name_mr"] == ""
        assert result["description"] == "The text (94-95) more"

    def test_paren_before_colon_unchanged(self):
        # Existing behavior: paren comes first
        line = "Name (Marathi): desc"
        result = _parse_item_line(line)
        assert result["name"] == "Name"
        assert result["name_mr"] == "Marathi"
        assert result["description"] == "desc"

    def test_colon_only_unchanged(self):
        line = "Name: desc"
        result = _parse_item_line(line)
        assert result["name"] == "Name"
        assert result["name_mr"] == ""
        assert result["description"] == "desc"


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

        # source_note should be None
        assert parsed["source_note"] is None

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

    def test_source_note_collection(self, tmp_path: Path):
        # Synthetic docx with one normal bullet and one source register bullet
        part1_para = _p("PART 1")
        char_heading = _p("1. Characters")
        char_item = _p("Normal (नाम): description", style="ListBullet")
        source_bullet = _p("Source register & boundary: note text", style="ListBullet")
        part2_para = _p("PART 2")
        sec1_header = _p("Section 1: 001–001 | T (E)")
        sec1_context = _p("संदर्भ: c")
        sec1_table = _tbl([["ovi", "o", "s", "h", "e"], ["001", "t", "s", "h", "e"]])
        body_children = [part1_para, char_heading, char_item, source_bullet, part2_para, sec1_header, sec1_context, sec1_table]
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

        # Only one object in characters
        assert len(parsed["packet"]["characters"]) == 1
        assert parsed["packet"]["characters"][0]["name"] == "Normal"
        # source_note captured
        assert parsed["source_note"] == "Source register & boundary: note text"

        # Write outputs and check import_report.json includes source_note
        out_root = tmp_path / "out"
        write_outputs(parsed, 1, out_root)
        report = json.loads((out_root / "adhyay_01" / "source" / "import_report.json").read_text(encoding="utf-8"))
        assert report["source_note"] == "Source register & boundary: note text"

    def test_no_source_note(self, tmp_path: Path):
        # Same as valid synthetic but ensure source_note is None and report has null
        docx_bytes = _valid_docx_bytes()
        docx_path = _write_docx(tmp_path, docx_bytes)
        parsed = parse_docx(docx_path)
        assert parsed["source_note"] is None
        out_root = tmp_path / "out"
        write_outputs(parsed, 1, out_root)
        report = json.loads((out_root / "adhyay_01" / "source" / "import_report.json").read_text(encoding="utf-8"))
        assert report["source_note"] is None

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


def _docx_from_body(tmp_path: Path, body_children: List[ET.Element]) -> Path:
    """A minimal docx around the given body elements (same parts as the tests above)."""
    content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""
    rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""
    parts = {"[Content_Types].xml": content_types, "_rels/.rels": rels, "word/document.xml": _build_document_xml(body_children)}
    return _write_docx(tmp_path, _make_docx_xml(parts))


def _section(n: int, first: int, last: int) -> List[ET.Element]:
    rows = [["ovi", "o", "s", "h", "e"]] + [[f"{k:03d}", "t", "s", "h", "e"] for k in range(first, last + 1)]
    return [_p(f"Section {n}: {first:03d}–{last:03d} | T (E)"), _p("संदर्भ: c"), _tbl(rows)]


class TestLayoutRefusals2026_11_01:
    """The three refusals added in the I2 review (bare PART 2, table after the last section, malformed later header)."""

    def test_bare_part2_is_refused_not_an_empty_import(self, tmp_path: Path):
        path = _docx_from_body(tmp_path, [_p("PART 1"), _p("PART 2")])
        with pytest.raises(LayoutError, match="no section headers"):
            parse_docx(path)

    def test_table_after_the_closing_paragraphs_is_refused(self, tmp_path: Path):
        body = [_p("PART 1"), _p("PART 2"), *_section(1, 1, 2), _p("closing line"), _p("second closing line"), _tbl([["x", "x", "x", "x", "x"]])]
        with pytest.raises(LayoutError, match="after last section"):
            parse_docx(_docx_from_body(tmp_path, body))

    def test_malformed_later_section_header_is_refused(self, tmp_path: Path):
        body = [_p("PART 1"), _p("PART 2"), *_section(1, 1, 2), _p("Section 2 broken header"), _p("संदर्भ: c"),
                _tbl([["ovi", "o", "s", "h", "e"], ["003", "t", "s", "h", "e"]])]
        with pytest.raises(LayoutError, match="does not match pattern"):
            parse_docx(_docx_from_body(tmp_path, body))

    def test_valid_two_sections_with_closing_lines_still_parse(self, tmp_path: Path):
        body = [_p("PART 1"), _p("PART 2"), *_section(1, 1, 2), *_section(2, 3, 3), _p("॥ closing ॥")]
        parsed = parse_docx(_docx_from_body(tmp_path, body))
        assert [o["ovi"] for o in parsed["ovis"]] == [1, 2, 3] and len(parsed["sections"]) == 2


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
            "source_note": None,
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
        assert report["source_note"] is None

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
            "source_note": None,
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
    not (Path(__file__).resolve().parents[1] / "canon" / "test_inputs" / "Shri_Gajanan_Vijay_Chapter_1_Final.docx").exists(),
    reason="Real canon docx not present"
)
class TestRealFileChapter1:
    def test_real_file_parses_correctly(self):
        repo_root = Path(__file__).resolve().parents[1]
        docx_path = repo_root / "canon" / "test_inputs" / "Shri_Gajanan_Vijay_Chapter_1_Final.docx"
        parsed = parse_docx(docx_path)

        assert len(parsed["ovis"]) == 146
        assert len(parsed["sections"]) == 12
        # Ovi numbers 1..146 in order
        for idx, ovi in enumerate(parsed["ovis"], 1):
            assert ovi["ovi"] == idx
        # Sections contiguous, first starts at 1, last ends at 146
        assert parsed["sections"][0]["first"] == 1
        assert parsed["sections"][-1]["last"] == 146
        for i in range(1, len(parsed["sections"])):
            assert parsed["sections"][i]["first"] == parsed["sections"][i-1]["last"] + 1

        # Mismatches: 0
        assert parsed["mismatches"] == []

        # Packet counts
        assert len(parsed["packet"]["characters"]) == 8
        assert len(parsed["packet"]["locations"]) == 5
        assert len(parsed["packet"]["objects"]) == 10

        # source_note starts with "Source register"
        assert parsed["source_note"] is not None
        assert parsed["source_note"].startswith("Source register")

        # No object name contains ": "
        for obj in parsed["packet"]["objects"]:
            assert ": " not in obj["name"]


@pytest.mark.skipif(
    not (Path(__file__).resolve().parents[1] / "canon" / "test_inputs" / "Shri_Gajanan_Vijay_Chapter_2_Audited_Canon_Edition.docx").exists(),
    reason="Real canon docx not present"
)
class TestRealFileChapter2:
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

        # source_note should be None for Chapter 2
        assert parsed["source_note"] is None

        # Compare with committed packet.json
        packet_path = repo_root / "canon" / "adhyay_02" / "research" / "packet.json"
        if packet_path.exists():
            with packet_path.open("r", encoding="utf-8") as f:
                committed = json.load(f)
            # Compare characters, locations, objects (order matters)
            assert parsed["packet"]["characters"] == committed["characters"]
            assert parsed["packet"]["locations"] == committed["locations"]
            assert parsed["packet"]["objects"] == committed["objects"]
