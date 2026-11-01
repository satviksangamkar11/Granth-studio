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

    # assets/v5_presets/index.json (preset index for happy path)
    presets_dir = root / "assets" / "v5_presets"
    presets_dir.mkdir(parents=True)
    presets_index = json.dumps([{"preset": "p1", "use": "x", "assets": [], "simplest_renderer": "motion"}])
    (presets_dir / "index.json").write_text(presets_index, encoding="utf-8")

    return root


def _make_synthetic_root_no_presets(tmp_path: Path) -> Path:
    """Create a synthetic adhyay 2 structure WITHOUT preset index."""
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

    # NOTE: NO assets/v5_presets/index.json
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
    assert result["problems"] == []
    assert result["ok"] is True
    # script_sha256 matches
    script_path = root / "canon" / "adhyay_02" / "script" / "easy.md"
    text = script_path.read_text(encoding="utf-8")
    assert result["script_sha256"] == check_script_cli.script_sha256(text)


def test_happy_path_without_presets_reports_problem(tmp_path: Path):
    """Without preset index, run_check returns errors=[] and problems=['presets: missing']."""
    root = _make_synthetic_root_no_presets(tmp_path)
    result = check_script_cli.run_check(2, root)
    assert result["adhyay"] == 2
    assert result["lines"] == 4
    assert result["scenes"] == 2
    assert result["core"] == 4
    assert result["optional"] == 0
    assert result["errors"] == []
    assert result["problems"] == ["presets: missing"]
    # ok = (len(errors) == 0) and (len(own_problems) == 0)
    # "presets: missing" comes from ctx_problems, not own_problems, so ok is True
    assert result["ok"] is True


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
    # Happy path
    root = _make_synthetic_root(tmp_path)
    rc = check_script_cli.main(["--adhyay", "2", "--root", str(root)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "adhyay 2: 4 lines, 2 scenes, 4 core, 0 errors, 0 problems" in out

    # With errors (duplicate line id) - test failing script alone
    root_err = _make_synthetic_root(tmp_path / "err")
    script_path = root_err / "canon" / "adhyay_02" / "script" / "easy.md"
    text = script_path.read_text(encoding="utf-8")
    # Duplicate S1-L1 exactly
    text += (
        "**S1-L1** | narrator | ovi 1 | core\n"
        "- Marathi: नमस्कार मित्रांनो\n"
        "- Hindi: नमस्ते दोस्तों\n"
        "\n"
    )
    script_path.write_text(text, encoding="utf-8")
    rc = check_script_cli.main(["--adhyay", "2", "--root", str(root_err)])
    out = capsys.readouterr().out
    assert rc == 1
    assert "error:" in out

    # Write receipt - use a FRESH valid root (happy fixture)
    root_receipt = _make_synthetic_root(tmp_path / "receipt")
    rc = check_script_cli.main(["--adhyay", "2", "--root", str(root_receipt), "--write-receipt"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "receipt" in out
    # Verify receipt file exists with correct note
    receipt_path = root_receipt / "canon" / "adhyay_02" / "stage1" / "script_check_receipt.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["note"] == "report only; the script was never edited"

    # Refuse second write
    rc = check_script_cli.main(["--adhyay", "2", "--root", str(root_receipt), "--write-receipt"])
    out = capsys.readouterr().out
    assert rc == 2
    assert "refused: receipt exists" in out


@pytest.mark.skipif(
    not (_REPO_ROOT / "canon" / "adhyay_01" / "script" / "easy.md").exists(),
    reason="Real Adhyay 1 script not present",
)
def test_real_adhyay_1():
    result = check_script_cli.run_check(1, _REPO_ROOT)
    assert result["lines"] == 61                      # owner directive 2026-11-01: S7-L2 cut
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
