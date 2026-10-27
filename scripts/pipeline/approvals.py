from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Set


def sha256_file(path: str | Path) -> str:
    """Return the SHA-256 hex digest of the file at *path*."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path: str | Path) -> Dict[str, Any]:
    """Load approvals JSON from *path*; return empty dict if missing."""
    p = Path(path)
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def approve(
    path: str | Path,
    item: str,
    sha256: str,
    owner: str,
    date: str,
) -> None:
    """
    Record an approval for *item* with the given *sha256*, *owner*, and *date*.

    Validates that *item*, *owner*, and *date* are non-empty strings and that
    *sha256* is exactly 64 lowercase hexadecimal characters. Raises ValueError
    on validation failure and writes nothing. On success, writes atomically
    (temp file + os.replace) as UTF-8 JSON with indent=1 and sorted keys.
    """
    if not (isinstance(item, str) and item):
        raise ValueError("item must be a non-empty string")
    if not (isinstance(owner, str) and owner):
        raise ValueError("owner must be a non-empty string")
    if not (isinstance(date, str) and date):
        raise ValueError("date must be a non-empty string")
    if not (isinstance(sha256, str) and len(sha256) == 64 and all(c in "0123456789abcdef" for c in sha256)):
        raise ValueError("sha256 must be a 64-character lowercase hex string")

    p = Path(path)
    approvals = load(p)
    approvals[item] = {"sha256": sha256, "owner": owner, "date": date}

    # Atomic write
    p.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=p.parent,
        delete=False,
        suffix=".tmp",
    ) as tmp:
        json.dump(approvals, tmp, indent=1, sort_keys=True)
        tmp_path = tmp.name
    os.replace(tmp_path, p)


def _is_sha(v) -> bool:
    return isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v)


def status(approvals: Dict[str, Any], item: str, current_sha256: Any) -> str:
    """DRAFT: no record. APPROVED: the recorded and the current hash are both valid and equal. STALE: anything else (a missing or invalid hash never approves)."""
    rec = approvals.get(item)
    if rec is None:
        return "DRAFT"
    recorded = rec.get("sha256") if isinstance(rec, dict) else None
    return "APPROVED" if _is_sha(recorded) and _is_sha(current_sha256) and recorded == current_sha256 else "STALE"


def stale_dependents(deps: Dict[str, list[str]], changed: Set[str]) -> Set[str]:
    """
    Return all items that depend (directly or transitively) on any item in *changed*.

    *deps* maps an item to the list of items it depends on. The result does not
    include the items in *changed* themselves. Cycles are handled gracefully.
    """
    # Build reverse dependency graph: dep -> set of items that depend on it
    rev: Dict[str, Set[str]] = {}
    for item, dependencies in deps.items():
        for dep in dependencies:
            rev.setdefault(dep, set()).add(item)

    result: Set[str] = set()
    visited: Set[str] = set()

    for start in changed:
        stack = [start]
        while stack:
            cur = stack.pop()
            for nxt in rev.get(cur, ()):
                if nxt not in visited:
                    visited.add(nxt)
                    result.add(nxt)
                    stack.append(nxt)
    return result - set(changed)
