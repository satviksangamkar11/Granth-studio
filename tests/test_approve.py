import importlib.util
import json
import sys
from pathlib import Path

import pytest

# Load modules by path
REPO_ROOT = Path(__file__).resolve().parents[1]
PIPELINE_DIR = REPO_ROOT / "scripts" / "pipeline"

def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

approvals = load_module("approvals", PIPELINE_DIR / "approvals.py")
chapter = load_module("chapter", PIPELINE_DIR / "chapter.py")
approve = load_module("approve", PIPELINE_DIR / "approve.py")


@pytest.fixture
def tmp_root(tmp_path: Path) -> Path:
    """Create a temporary repo root with canon/adhyay_02 structure."""
    root = tmp_path
    # Create adhyay 2 directories
    (root / "canon" / "adhyay_02" / "stage1").mkdir(parents=True)
    (root / "canon" / "adhyay_02" / "source").mkdir(parents=True)
    # Create a dummy ovis.jsonl for build_ctx
    (root / "canon" / "adhyay_02" / "source" / "ovis.jsonl").write_text(
        '{"ovi": 1}\n', encoding="utf-8"
    )
    return root


def test_approve_file_happy_path(tmp_root: Path):
    # Create a file to approve
    file_path = tmp_root / "canon" / "adhyay_02" / "stage1" / "test.txt"
    file_path.write_text("hello", encoding="utf-8")
    expected_sha = approvals.sha256_file(file_path)

    result = approve.approve_file(
        adhyay=2,
        item="test_item",
        file=file_path,
        owner="Owner Name",
        root=tmp_root,
        today="2024-01-01",
        confirm=approve.CONFIRM_PHRASE,
    )
    assert result == {
        "item": "test_item",
        "sha256": expected_sha,
        "owner": "Owner Name",
        "date": "2024-01-01",
        "status": "APPROVED",
    }

    # Check approvals.json
    approvals_path = tmp_root / "canon" / "adhyay_02" / "approvals.json"
    assert approvals_path.exists()
    data = approvals.load(approvals_path)
    assert data["test_item"]["sha256"] == expected_sha
    assert data["test_item"]["owner"] == "Owner Name"
    assert data["test_item"]["date"] == "2024-01-01"

    # Check log
    log_path = approvals_path.with_name("approvals_log.jsonl")
    assert log_path.exists()
    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    log_entry = json.loads(lines[0])
    assert log_entry["item"] == "test_item"
    assert log_entry["sha256"] == expected_sha
    assert log_entry["owner"] == "Owner Name"
    assert log_entry["date"] == "2024-01-01"
    assert log_entry["file"] == "canon/adhyay_02/stage1/test.txt"
    assert log_entry["adhyay"] == 2

    # Second approval appends
    file2 = tmp_root / "canon" / "adhyay_02" / "stage1" / "test2.txt"
    file2.write_text("world", encoding="utf-8")
    expected_sha2 = approvals.sha256_file(file2)
    approve.approve_file(
        adhyay=2,
        item="test_item2",
        file=file2,
        owner="Owner Name",
        root=tmp_root,
        today="2024-01-02",
        confirm=approve.CONFIRM_PHRASE,
    )
    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["item"] == "test_item"
    assert json.loads(lines[1])["item"] == "test_item2"


@pytest.mark.parametrize("confirm", ["wrong", "", "I AM THE OWNER AND I APPROVE THIS FILE "])
def test_approve_file_wrong_confirm(tmp_root: Path, confirm: str):
    file_path = tmp_root / "canon" / "adhyay_02" / "stage1" / "test.txt"
    file_path.write_text("hello", encoding="utf-8")
    with pytest.raises(ValueError, match=r"^refused: confirm phrase does not match"):
        approve.approve_file(
            adhyay=2,
            item="test_item",
            file=file_path,
            owner="Owner",
            root=tmp_root,
            confirm=confirm,
        )
    # Nothing written
    assert not (tmp_root / "canon" / "adhyay_02" / "approvals.json").exists()
    assert not (tmp_root / "canon" / "adhyay_02" / "approvals_log.jsonl").exists()


def test_approve_file_empty_owner(tmp_root: Path):
    file_path = tmp_root / "canon" / "adhyay_02" / "stage1" / "test.txt"
    file_path.write_text("hello", encoding="utf-8")
    with pytest.raises(ValueError, match=r"^refused: owner is empty"):
        approve.approve_file(
            adhyay=2,
            item="test_item",
            file=file_path,
            owner="",
            root=tmp_root,
            confirm=approve.CONFIRM_PHRASE,
        )
    assert not (tmp_root / "canon" / "adhyay_02" / "approvals.json").exists()


def test_approve_file_whitespace_owner(tmp_root: Path):
    file_path = tmp_root / "canon" / "adhyay_02" / "stage1" / "test.txt"
    file_path.write_text("hello", encoding="utf-8")
    with pytest.raises(ValueError, match=r"^refused: owner is empty"):
        approve.approve_file(
            adhyay=2,
            item="test_item",
            file=file_path,
            owner="   ",
            root=tmp_root,
            confirm=approve.CONFIRM_PHRASE,
        )


def test_approve_file_item_with_space(tmp_root: Path):
    file_path = tmp_root / "canon" / "adhyay_02" / "stage1" / "test.txt"
    file_path.write_text("hello", encoding="utf-8")
    with pytest.raises(ValueError, match=r"^refused: item is empty or contains whitespace"):
        approve.approve_file(
            adhyay=2,
            item="test item",
            file=file_path,
            owner="Owner",
            root=tmp_root,
            confirm=approve.CONFIRM_PHRASE,
        )


def test_approve_file_empty_item(tmp_root: Path):
    file_path = tmp_root / "canon" / "adhyay_02" / "stage1" / "test.txt"
    file_path.write_text("hello", encoding="utf-8")
    with pytest.raises(ValueError, match=r"^refused: item is empty or contains whitespace"):
        approve.approve_file(
            adhyay=2,
            item="",
            file=file_path,
            owner="Owner",
            root=tmp_root,
            confirm=approve.CONFIRM_PHRASE,
        )


def test_approve_file_missing_file(tmp_root: Path):
    file_path = tmp_root / "canon" / "adhyay_02" / "stage1" / "missing.txt"
    with pytest.raises(ValueError, match=r"^refused: file does not exist or is not a regular file"):
        approve.approve_file(
            adhyay=2,
            item="test_item",
            file=file_path,
            owner="Owner",
            root=tmp_root,
            confirm=approve.CONFIRM_PHRASE,
        )


def test_approve_file_directory(tmp_root: Path):
    dir_path = tmp_root / "canon" / "adhyay_02" / "stage1"
    with pytest.raises(ValueError, match=r"^refused: file does not exist or is not a regular file"):
        approve.approve_file(
            adhyay=2,
            item="test_item",
            file=dir_path,
            owner="Owner",
            root=tmp_root,
            confirm=approve.CONFIRM_PHRASE,
        )


@pytest.mark.parametrize("adhyay", [0, 22, True, "x"])
def test_approve_file_invalid_adhyay(tmp_root: Path, adhyay):
    file_path = tmp_root / "canon" / "adhyay_02" / "stage1" / "test.txt"
    file_path.write_text("hello", encoding="utf-8")
    with pytest.raises(ValueError, match=r"^refused:"):
        approve.approve_file(
            adhyay=adhyay,
            item="test_item",
            file=file_path,
            owner="Owner",
            root=tmp_root,
            confirm=approve.CONFIRM_PHRASE,
        )


def test_item_status_draft_before_approval(tmp_root: Path):
    file_path = tmp_root / "canon" / "adhyay_02" / "stage1" / "test.txt"
    file_path.write_text("hello", encoding="utf-8")
    status = approve.item_status(2, "test_item", file_path, tmp_root)
    assert status == "DRAFT"


def test_item_status_approved_after_approval(tmp_root: Path):
    file_path = tmp_root / "canon" / "adhyay_02" / "stage1" / "test.txt"
    file_path.write_text("hello", encoding="utf-8")
    approve.approve_file(
        adhyay=2,
        item="test_item",
        file=file_path,
        owner="Owner",
        root=tmp_root,
        today="2024-01-01",
        confirm=approve.CONFIRM_PHRASE,
    )
    status = approve.item_status(2, "test_item", file_path, tmp_root)
    assert status == "APPROVED"


def test_item_status_stale_after_content_change(tmp_root: Path):
    file_path = tmp_root / "canon" / "adhyay_02" / "stage1" / "test.txt"
    file_path.write_text("hello", encoding="utf-8")
    approve.approve_file(
        adhyay=2,
        item="test_item",
        file=file_path,
        owner="Owner",
        root=tmp_root,
        today="2024-01-01",
        confirm=approve.CONFIRM_PHRASE,
    )
    # Change content
    file_path.write_text("hello world", encoding="utf-8")
    status = approve.item_status(2, "test_item", file_path, tmp_root)
    assert status == "STALE"


def test_item_status_stale_after_deletion(tmp_root: Path):
    file_path = tmp_root / "canon" / "adhyay_02" / "stage1" / "test.txt"
    file_path.write_text("hello", encoding="utf-8")
    approve.approve_file(
        adhyay=2,
        item="test_item",
        file=file_path,
        owner="Owner",
        root=tmp_root,
        today="2024-01-01",
        confirm=approve.CONFIRM_PHRASE,
    )
    file_path.unlink()
    status = approve.item_status(2, "test_item", file_path, tmp_root)
    assert status == "STALE"


def test_item_status_invalid_adhyay_returns_draft(tmp_root: Path):
    file_path = tmp_root / "canon" / "adhyay_02" / "stage1" / "test.txt"
    file_path.write_text("hello", encoding="utf-8")
    status = approve.item_status(0, "test_item", file_path, tmp_root)
    assert status == "DRAFT"
    status = approve.item_status(22, "test_item", file_path, tmp_root)
    assert status == "DRAFT"


def test_write_omissions_sorted_unique(tmp_root: Path):
    out_path = approve.write_omissions(2, [48, 142, 143, 48, 142], tmp_root)
    assert out_path.exists()
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data == {"adhyay": 2, "ovis": [48, 142, 143]}


@pytest.mark.parametrize("ovis", [[], [0], [-1], [True], ["3"], [2.5]])
def test_write_omissions_invalid_ovis(tmp_root: Path, ovis):
    with pytest.raises(ValueError, match=r"^refused:"):
        approve.write_omissions(2, ovis, tmp_root)


def test_write_omissions_file_exists_raises(tmp_root: Path):
    out_path = tmp_root / "canon" / "adhyay_02" / "stage1" / "omissions_approved.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("{}", encoding="utf-8")
    with pytest.raises(FileExistsError, match=r"^refused:"):
        approve.write_omissions(2, [1], tmp_root)
    # File unchanged
    assert out_path.read_text(encoding="utf-8") == "{}"


def test_write_omissions_invalid_adhyay(tmp_root: Path):
    with pytest.raises(ValueError, match=r"^refused:"):
        approve.write_omissions(0, [1], tmp_root)
    with pytest.raises(ValueError, match=r"^refused:"):
        approve.write_omissions(22, [1], tmp_root)


def test_write_omissions_integration_with_build_ctx(tmp_root: Path):
    # Load stage1.context module
    context = load_module("context", PIPELINE_DIR / "stage1" / "context.py")
    # Write omissions
    out_path = approve.write_omissions(2, [48, 142, 143], tmp_root)
    # Approve the omissions file
    approve.approve_file(
        adhyay=2,
        item="stage1_omissions",
        file=out_path,
        owner="Owner",
        root=tmp_root,
        today="2024-01-01",
        confirm=approve.CONFIRM_PHRASE,
    )
    # Build context
    ctx, problems = context.build_ctx(2, tmp_root)
    assert ctx["unfilmed_ovis"] == [48, 142, 143]
    # No omissions problem
    omissions_problems = [p for p in problems if "omissions" in p.lower()]
    assert not omissions_problems

    # Edit the file (make it stale)
    out_path.write_text('{"adhyay": 2, "ovis": [1]}', encoding="utf-8")
    ctx2, problems2 = context.build_ctx(2, tmp_root)
    assert ctx2["unfilmed_ovis"] == []
    stale_problems = [p for p in problems2 if "STALE" in p]
    assert stale_problems


def test_main_omissions(capsys, tmp_root: Path):
    # Write omissions via main
    sys.argv = [
        "approve",
        "omissions",
        "--adhyay", "2",
        "--ovis", "48,142,143",
        "--root", str(tmp_root),
    ]
    ret = approve.main()
    assert ret == 0
    captured = capsys.readouterr()
    assert "wrote" in captured.out
    out_path = tmp_root / "canon" / "adhyay_02" / "stage1" / "omissions_approved.json"
    assert out_path.exists()


def test_main_omissions_refusal(capsys, tmp_root: Path):
    # Empty ovis
    sys.argv = [
        "approve",
        "omissions",
        "--adhyay", "2",
        "--ovis", "",
        "--root", str(tmp_root),
    ]
    ret = approve.main()
    assert ret == 2
    captured = capsys.readouterr()
    assert "refused:" in captured.out


def test_main_approve(capsys, tmp_root: Path):
    file_path = tmp_root / "canon" / "adhyay_02" / "stage1" / "test.txt"
    file_path.write_text("hello", encoding="utf-8")
    sys.argv = [
        "approve",
        "approve",
        "--adhyay", "2",
        "--item", "test_item",
        "--file", str(file_path),
        "--owner", "Owner",
        "--confirm", approve.CONFIRM_PHRASE,
        "--root", str(tmp_root),
    ]
    ret = approve.main()
    assert ret == 0
    captured = capsys.readouterr()
    assert "approved test_item sha256=" in captured.out
    assert "by Owner" in captured.out


def test_main_approve_refusal(capsys, tmp_root: Path):
    file_path = tmp_root / "canon" / "adhyay_02" / "stage1" / "test.txt"
    file_path.write_text("hello", encoding="utf-8")
    sys.argv = [
        "approve",
        "approve",
        "--adhyay", "2",
        "--item", "test_item",
        "--file", str(file_path),
        "--owner", "Owner",
        "--confirm", "wrong",
        "--root", str(tmp_root),
    ]
    ret = approve.main()
    assert ret == 2
    captured = capsys.readouterr()
    assert "refused:" in captured.out


def test_main_status_approved(capsys, tmp_root: Path):
    file_path = tmp_root / "canon" / "adhyay_02" / "stage1" / "test.txt"
    file_path.write_text("hello", encoding="utf-8")
    approve.approve_file(
        adhyay=2,
        item="test_item",
        file=file_path,
        owner="Owner",
        root=tmp_root,
        today="2024-01-01",
        confirm=approve.CONFIRM_PHRASE,
    )
    sys.argv = [
        "approve",
        "status",
        "--adhyay", "2",
        "--item", "test_item",
        "--file", str(file_path),
        "--root", str(tmp_root),
    ]
    ret = approve.main()
    assert ret == 0
    captured = capsys.readouterr()
    assert "test_item: APPROVED" in captured.out


def test_main_status_not_approved(capsys, tmp_root: Path):
    file_path = tmp_root / "canon" / "adhyay_02" / "stage1" / "test.txt"
    file_path.write_text("hello", encoding="utf-8")
    sys.argv = [
        "approve",
        "status",
        "--adhyay", "2",
        "--item", "test_item",
        "--file", str(file_path),
        "--root", str(tmp_root),
    ]
    ret = approve.main()
    assert ret == 1
    captured = capsys.readouterr()
    assert "test_item: DRAFT" in captured.out


def test_source_no_input_or_subprocess():
    source = (PIPELINE_DIR / "approve.py").read_text(encoding="utf-8")
    assert "input(" not in source
    assert "subprocess" not in source
