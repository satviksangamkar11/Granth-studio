"""Hashing, canonical JSON and crash-safe writes shared by every module."""

from __future__ import annotations

import hashlib
import json
import os
import unicodedata
import uuid
from pathlib import Path, PureWindowsPath

from .errors import ConfigError
from typing import Any


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_obj(obj: Any) -> str:
    return sha256_bytes(canonical_json(obj))


def normalize_text(text: str) -> str:
    """Unicode NFC with collapsed whitespace: the comparison form for Marathi and Hindi locks."""
    return " ".join(unicodedata.normalize("NFC", text).split())


def atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    with tmp.open("wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def atomic_write_json(path: Path, obj: Any) -> None:
    text = json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    atomic_write_bytes(path, text.encode("utf-8"))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def contained_path(base: Path, relative: str) -> Path:
    """Data paths are relative to their declared root, on Windows and POSIX."""
    win = PureWindowsPath(relative)
    parts = relative.replace("\\", "/").split("/")
    if not relative or win.drive or win.root or Path(relative).is_absolute() or ".." in parts:
        raise ConfigError(f"path must stay under {base}: {relative!r}")
    root = base.resolve()
    result = root.joinpath(*parts).resolve()
    if not result.is_relative_to(root) or result == root:
        raise ConfigError(f"path escapes {base}: {relative!r}")
    return result
