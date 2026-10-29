# FIX CALL: return BOTH files in full: `scripts/pipeline/approve.py` and `tests/test_approve.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
............................F.......                                     [100%]
================================== FAILURES ===================================
_______________ test_write_omissions_integration_with_build_ctx _______________
tests\test_approve.py:331: in test_write_omissions_integration_with_build_ctx
    assert ctx["unfilmed_ovis"] == [48, 142, 143]
E   assert [] == [48, 142, 143]
E     
E     Right contains 3 more items, first extra item: 48
E     Use -v to get more diff
=========================== short test summary info ===========================
FAILED tests/test_approve.py::test_write_omissions_integration_with_build_ctx
1 failed, 35 passed in 0.35s

```

## SPEC
# SPEC: NEW `scripts/pipeline/approve.py` + NEW `tests/test_approve.py`. Return exactly these TWO files in full; do not output or change any other file.
Checklist row 12 (approval authority): the ONLY way an approval gets into `approvals.json` is this command, run by the owner. It records the sha256 of the approved file, the owner name and the date, and appends the same fact to an append-only log. A changed file makes the approval STALE (already implemented in `approvals.py`). Standard library only; `from __future__ import annotations`; nothing at import time except imports and definitions; no print except in `main()`; plain functions; no key or secret is read or printed.

## Existing code (load by importlib BY PATH; do not modify)
- `scripts/pipeline/approvals.py`: `sha256_file(path) -> str`, `load(path) -> dict` (empty dict if the file is missing), `approve(path, item, sha256, owner, date) -> None` (validates non-empty item, owner, date and a 64-hex sha256, raises ValueError otherwise, writes atomically), `status(approvals: dict, item: str, current_sha256) -> "DRAFT" | "APPROVED" | "STALE"`.
- `scripts/pipeline/chapter.py`: `chapter_paths(adhyay, root) -> dict` with the keys `approvals` (the approvals.json path) and `stage1_dir`; it raises ValueError for an adhyay outside 1..21.
Repo root in this module: `Path(__file__).resolve().parents[2]`; in tests `Path(__file__).resolve().parents[1]`.

## API
- `CONFIRM_PHRASE = "I AM THE OWNER AND I APPROVE THIS FILE"`.
- `approve_file(adhyay: int, item: str, file: Path | str, owner: str, root: Path | str, today: str | None = None, confirm: str = "") -> dict`: the single approval write path. Refuses with `ValueError` (message starts with `refused:`) when `confirm != CONFIRM_PHRASE`, when `owner` is empty or only whitespace, when `item` is empty or contains whitespace, when the file does not exist or is not a regular file, or for an invalid adhyay. Otherwise computes the sha256 of the file, calls `approvals.approve(approvals_path, item, sha, owner.strip(), date)` where `date` is `today` or today's date in ISO form (`YYYY-MM-DD`), appends ONE JSON line `{"item","sha256","owner","date","file","adhyay"}` (file = path relative to root with forward slashes when it lies under root, else the name only) to `approvals_log.jsonl` in the same folder as approvals.json (create it if missing; never rewrite or truncate it), and returns `{"item","sha256","owner","date","status": "APPROVED"}`.
- `item_status(adhyay: int, item: str, file: Path | str, root: Path | str) -> str`: `DRAFT` when there is no record, `APPROVED` or `STALE` through `approvals.status` against the current sha256 of the file; `STALE` is also returned when a record exists and the file is missing. Never raises (returns `DRAFT` for an invalid adhyay).
- `write_omissions(adhyay: int, ovis: list[int], root: Path | str) -> Path`: writes `<stage1_dir>/omissions_approved.json` as `{"adhyay": N, "ovis": sorted unique ints}` (json, indent 1, utf-8, `ensure_ascii=False`), creating the folder; raises `ValueError` for an invalid adhyay, an empty list, or a non-int / bool / non-positive item; raises `FileExistsError` if the file exists (the owner deletes it deliberately to redo). It does NOT approve anything.
- `main(argv=None) -> int` with sub-commands: `omissions --adhyay N --ovis 48,142,143 [--root PATH]` (writes the file, prints `wrote <path>`, returns 0; refusal -> prints `refused: <reason>` and returns 2); `approve --adhyay N --item ITEM --file PATH --owner NAME --confirm "<phrase>" [--root PATH]` (prints `approved <item> sha256=<first 12 chars> by <owner>`, returns 0; refusal -> `refused: <reason>`, returns 2); `status --adhyay N --item ITEM --file PATH [--root PATH]` (prints `<item>: <STATUS>`, returns 0 for APPROVED and 1 otherwise). The default root is the repo root. `if __name__ == "__main__": raise SystemExit(main())`.

## Tests (`tests/test_approve.py`; synthetic data in tmp_path; load modules by importlib BY PATH)
Use a tmp root: the approvals path for adhyay 2 is `<root>/canon/adhyay_02/approvals.json` (created by the command), files to approve are written under `<root>/canon/adhyay_02/stage1/`.
1. `approve_file` happy path: returns APPROVED with the right sha256 (compare with `hashlib.sha256(bytes).hexdigest()`), owner, date; approvals.json contains the record; the log has exactly one line with the same fields; a second approval of another item appends a second line and keeps the first; the log is never truncated.
2. Each refusal in its own isolated test (wrong confirm phrase, empty owner, whitespace owner, item with a space, empty item, missing file, a directory, adhyay 0, 22, True, "x"): `ValueError` starting with `refused:` and NOTHING written (no approvals file, no log).
3. `item_status`: DRAFT before approval; APPROVED after; STALE after the file content changes; STALE when the file is deleted after approval; invalid adhyay -> DRAFT, no exception.
4. `write_omissions`: sorted unique ovis written; duplicates collapsed; each invalid input (empty, 0, -1, True, "3", 2.5) raises ValueError in its own test; an existing file raises FileExistsError and stays unchanged; the written file approved through `approve_file` makes `scripts/pipeline/stage1/context.py` (`build_ctx(adhyay, root)` returns `(ctx, problems)`) return those ovis in `ctx["unfilmed_ovis"]` with no omissions problem, and after editing the file the ctx has `[]` and a problem containing `STALE` (this connects the write path to the real consumer; build a tiny synthetic ovis file `canon/adhyay_02/source/ovis.jsonl` with `{"ovi": 1}` lines so build_ctx runs; missing voice library etc. only add other problems, assert only on the omissions behaviour).
5. `main`: each sub-command's output text and return codes (capsys), the refusal path returning 2, `status` returning 0 / 1.
6. A source-level test: the module source contains no `input(` call and does not import `subprocess`.
Use plain assignment and `copy.deepcopy`; never a helper that rejects no-effect mutations; remember `True == 1`.

Reply with only the two FILE blocks:
FILE: scripts/pipeline/approve.py
FILE: tests/test_approve.py


## CURRENT MODULE scripts/pipeline/approve.py
```python
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

# Import existing modules (same directory, loaded into sys.modules by tests)
import approvals
import chapter

CONFIRM_PHRASE = "I AM THE OWNER AND I APPROVE THIS FILE"


def _sha256_file(path: Path) -> str:
    """Return sha256 hex digest of file."""
    return approvals.sha256_file(path)


def _approvals_log_path(approvals_path: Path) -> Path:
    return approvals_path.with_name("approvals_log.jsonl")


def _relative_to_root(file_path: Path, root: Path) -> str:
    try:
        rel = file_path.resolve().relative_to(root.resolve())
        return rel.as_posix()
    except ValueError:
        return file_path.name


def approve_file(
    adhyay: int,
    item: str,
    file: Path | str,
    owner: str,
    root: Path | str,
    today: str | None = None,
    confirm: str = "",
) -> dict[str, Any]:
    """Approve a file for the given adhyay and item."""
    # Validate confirm phrase
    if confirm != CONFIRM_PHRASE:
        raise ValueError("refused: confirm phrase does not match")
    # Validate owner
    owner_stripped = owner.strip()
    if not owner_stripped:
        raise ValueError("refused: owner is empty")
    # Validate item
    if not item or any(ch.isspace() for ch in item):
        raise ValueError("refused: item is empty or contains whitespace")
    # Validate file
    file_path = Path(file)
    if not file_path.exists() or not file_path.is_file():
        raise ValueError("refused: file does not exist or is not a regular file")
    # Validate adhyay and get paths
    try:
        paths = chapter.chapter_paths(adhyay, root)
    except ValueError as e:
        raise ValueError(f"refused: {e}") from e
    approvals_path = paths["approvals"]
    # Compute sha256
    sha = _sha256_file(file_path)
    # Date
    approval_date = today or date.today().isoformat()
    # Approve via approvals module
    approvals.approve(approvals_path, item, sha, owner_stripped, approval_date)
    # Append to log
    log_path = _approvals_log_path(approvals_path)
    log_entry = {
        "item": item,
        "sha256": sha,
        "owner": owner_stripped,
        "date": approval_date,
        "file": _relative_to_root(file_path, Path(root)),
        "adhyay": adhyay,
    }
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    return {
        "item": item,
        "sha256": sha,
        "owner": owner_stripped,
        "date": approval_date,
        "status": "APPROVED",
    }


def item_status(
    adhyay: int,
    item: str,
    file: Path | str,
    root: Path | str,
) -> str:
    """Return status of item: DRAFT, APPROVED, or STALE."""
    try:
        paths = chapter.chapter_paths(adhyay, root)
    except ValueError:
        return "DRAFT"
    approvals_path = paths["approvals"]
    approvals_dict = approvals.load(approvals_path)
    file_path = Path(file)
    current_sha = None
    if file_path.exists() and file_path.is_file():
        current_sha = _sha256_file(file_path)
    return approvals.status(approvals_dict, item, current_sha)


def write_omissions(
    adhyay: int,
    ovis: list[int],
    root: Path | str,
) -> Path:
    """Write omissions_approved.json in stage1_dir."""
    # Validate adhyay
    try:
        paths = chapter.chapter_paths(adhyay, root)
    except ValueError as e:
        raise ValueError(f"refused: {e}") from e
    stage1_dir = paths["stage1_dir"]
    # Validate ovis
    if not ovis:
        raise ValueError("refused: ovis list is empty")
    seen = set()
    unique_ovis = []
    for ovi in ovis:
        if isinstance(ovi, bool) or not isinstance(ovi, int):
            raise ValueError("refused: ovis must be integers")
        if ovi <= 0:
            raise ValueError("refused: ovis must be positive")
        if ovi not in seen:
            seen.add(ovi)
            unique_ovis.append(ovi)
    unique_ovis.sort()
    # Write file
    out_path = Path(stage1_dir) / "omissions_approved.json"
    if out_path.exists():
        raise FileExistsError(f"refused: {out_path} already exists")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    data = {"adhyay": adhyay, "ovis": unique_ovis}
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    return out_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="approve")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # omissions subcommand
    om_parser = subparsers.add_parser("omissions")
    om_parser.add_argument("--adhyay", type=int, required=True)
    om_parser.add_argument("--ovis", type=str, required=True)
    om_parser.add_argument("--root", type=str, default=None)

    # approve subcommand
    ap_parser = subparsers.add_parser("approve")
    ap_parser.add_argument("--adhyay", type=int, required=True)
    ap_parser.add_argument("--item", type=str, required=True)
    ap_parser.add_argument("--file", type=str, required=True)
    ap_parser.add_argument("--owner", type=str, required=True)
    ap_parser.add_argument("--confirm", type=str, required=True)
    ap_parser.add_argument("--root", type=str, default=None)

    # status subcommand
    st_parser = subparsers.add_parser("status")
    st_parser.add_argument("--adhyay", type=int, required=True)
    st_parser.add_argument("--item", type=str, required=True)
    st_parser.add_argument("--file", type=str, required=True)
    st_parser.add_argument("--root", type=str, default=None)

    args = parser.parse_args(argv)

    # Determine root
    if args.root is None:
        root = Path(__file__).resolve().parents[2]
    else:
        root = Path(args.root)

    try:
        if args.command == "omissions":
            ovis_list = [int(x) for x in args.ovis.split(",") if x.strip()]
            out_path = write_omissions(args.adhyay, ovis_list, root)
            print(f"wrote {out_path}")
            return 0
        elif args.command == "approve":
            result = approve_file(
                args.adhyay,
                args.item,
                args.file,
                args.owner,
                root,
                confirm=args.confirm,
            )
            print(
                f"approved {result['item']} sha256={result['sha256'][:12]} by {result['owner']}"
            )
            return 0
        elif args.command == "status":
            status = item_status(args.adhyay, args.item, args.file, root)
            print(f"{args.item}: {status}")
            return 0 if status == "APPROVED" else 1
    except ValueError as e:
        msg = str(e)
        if msg.startswith("refused:"):
            print(msg)
            return 2
        raise
    except FileExistsError as e:
        print(f"refused: {e}")
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

```

## CURRENT TESTS tests/test_approve.py
```python
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
        item="omissions_approved.json",
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

```

## DIAGNOSIS (verified by running the tests)
ONE failing test: test_write_omissions_integration_with_build_ctx expects ctx['unfilmed_ovis'] == [48, 142, 143] after write_omissions + approve_file, but build_ctx returned []. Trace why (hand-check): (a) the approvals record must be {item: {'sha256','owner','date'}} written by approvals.approve under chapter_paths(adhyay, root)['approvals'] with the item name EXACTLY 'stage1_omissions'; (b) build_ctx reads <stage1_dir>/omissions_approved.json, hashes it and compares with that record through approvals.status; (c) the file approved must be the SAME file write_omissions wrote (same path); (d) the test's synthetic root must be the one passed to both functions. Find which of these differs in the module or the test and fix that side (the SPEC decides). Run the logic mentally with a tiny example before answering.
