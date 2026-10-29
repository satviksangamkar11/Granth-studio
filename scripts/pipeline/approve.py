from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

# Load existing modules (same directory) via importlib
_pipeline_dir = Path(__file__).resolve().parent
for _mod_name in ("approvals", "chapter"):
    _mod_path = _pipeline_dir / f"{_mod_name}.py"
    _spec = importlib.util.spec_from_file_location(_mod_name, _mod_path)
    if _spec is None or _spec.loader is None:
        raise ImportError(f"Cannot load {_mod_name} from {_mod_path}")
    _module = importlib.util.module_from_spec(_spec)
    sys.modules[_mod_name] = _module
    _spec.loader.exec_module(_module)

# Now available as regular imports
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
    try:
        approvals_dict = approvals.load(approvals_path)
        file_path = Path(file)
        current_sha = None
        if file_path.exists() and file_path.is_file():
            current_sha = _sha256_file(file_path)
    except (OSError, ValueError):
        return "STALE"
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
            try:
                ovis_list = [int(x) for x in args.ovis.split(",") if x.strip()]
            except ValueError:
                print("refused: ovis must be integers")
                return 2
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
