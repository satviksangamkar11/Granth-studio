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
    expected_ids = ["S1-L1", "S1-L2", "S2-L1", "S2-L2", "S3-L1", "S3-L2"]
    for i, rec in enumerate(records):
        assert rec["id"] == expected_ids[i]
        assert rec["scene"] == expected_ids[i].split("-")[0]  # scene is like 'S1'
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
    # Sections: 1,1,3,3 (as strings 'S1', 'S1', 'S3', 'S3')
    assert [r["scene"] for r in records] == ["S1", "S1", "S3", "S3"]
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
