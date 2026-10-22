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


def reject_link_components(root: Path, relative: str) -> None:
    """No existing component of root/relative (root itself included) may be a symlink or Windows junction."""
    current = root
    for part in ("", *relative.replace("\\", "/").split("/")):
        current = current / part if part else current
        if current.is_symlink() or (hasattr(os.path, "isjunction") and os.path.isjunction(current)):
            raise ConfigError(f"{current} is a link or junction; refusing to write through it")


def _race_hook(stage: str, path: Path) -> None:
    """Test seam: called just before each filesystem step of create_new_file (a no-op in production)."""


def _is_link(path: Path) -> bool:
    return path.is_symlink() or (hasattr(os.path, "isjunction") and os.path.isjunction(path))


def _windows_pin(path: Path, root_final: str | None):
    """Open a directory without FILE_SHARE_DELETE so it cannot be renamed, deleted or replaced while pinned;
    refuse reparse points (junctions/symlinks) and anything whose final path leaves the root."""
    import ctypes
    from ctypes import wintypes
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.CreateFileW.restype = wintypes.HANDLE
    k32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD,
                                wintypes.DWORD, wintypes.HANDLE]
    handle = k32.CreateFileW(str(path), 0x80000000, 0x3, None, 3, 0x02000000 | 0x00200000, None)   # BACKUP_SEMANTICS|OPEN_REPARSE_POINT
    if handle in (None, wintypes.HANDLE(-1).value):
        raise ConfigError(f"cannot pin directory {path}: error {ctypes.get_last_error()}")
    class Info(ctypes.Structure):
        _fields_ = [("attrs", wintypes.DWORD), ("rest", ctypes.c_byte * 48)]
    info = Info()
    k32.GetFileInformationByHandle.argtypes = [wintypes.HANDLE, ctypes.POINTER(Info)]
    buffer = ctypes.create_unicode_buffer(32768)
    k32.GetFinalPathNameByHandleW.argtypes = [wintypes.HANDLE, wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD]
    ok = k32.GetFileInformationByHandle(handle, ctypes.byref(info))
    k32.GetFinalPathNameByHandleW(handle, buffer, len(buffer), 0)
    final = buffer.value.removeprefix("\\\\?\\").lower().rstrip("\\")
    if not ok or info.attrs & 0x400 or (root_final is not None and not (final == root_final or final.startswith(root_final + "\\"))):
        k32.CloseHandle(handle)
        raise ConfigError(f"{path} is a link or junction or lies outside the trusted root; refusing to write through it")
    return handle, final, k32


def _create_windows(root: Path, parts: list[str], source: Path) -> Path:
    handles, current, root_final = [], root, None
    try:
        handle, root_final, k32 = _windows_pin(root, None)
        handles.append(handle)
        for index, part in enumerate(parts):
            current = current / part
            last = index == len(parts) - 1
            if last:
                _race_hook("before_open", current)
                return _copy_exclusive(current, source, root)
            _race_hook("before_mkdir", current)
            try:
                os.mkdir(current)
            except FileExistsError:
                pass
            handle, _, _ = _windows_pin(current, root_final)   # pinned from here on; parent stays pinned too
            handles.append(handle)
    finally:
        for handle in reversed(handles):
            k32.CloseHandle(handle)
    raise AssertionError("unreachable")


def _create_posix(root: Path, parts: list[str], source: Path) -> Path:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    fds = [os.open(root, flags)]
    current = root
    try:
        for index, part in enumerate(parts):
            current = current / part
            if index == len(parts) - 1:
                _race_hook("before_open", current)
                fd = os.open(part, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600, dir_fd=fds[-1])
                parent_fd = fds[-1]
                return _copy_fd(fd, current, source, lambda: os.unlink(part, dir_fd=parent_fd))
            _race_hook("before_mkdir", current)
            try:
                os.mkdir(part, dir_fd=fds[-1])
            except FileExistsError:
                pass
            try:
                fds.append(os.open(part, flags, dir_fd=fds[-1]))   # O_NOFOLLOW: a symlink here is an error
            except OSError as exc:
                raise ConfigError(f"{current} is a link or not a directory; refusing to write through it") from exc
    finally:
        for fd in reversed(fds):
            os.close(fd)
    raise AssertionError("unreachable")


def _copy_fd(fd: int, target: Path, source: Path, discard) -> Path:
    """Write through the already-open descriptor; link count and cleanup use that descriptor / the pinned parent
    (``discard``), never the pathname, which an attacker may have redirected meanwhile."""
    try:
        with source.open("rb") as reader, os.fdopen(fd, "wb") as writer:
            for block in iter(lambda: reader.read(1 << 20), b""):
                writer.write(block)
            writer.flush()
            if os.fstat(writer.fileno()).st_nlink != 1:
                raise ConfigError(f"destination aliases another file: {target}")
    except BaseException:
        try:
            discard()                         # a partial copy is ours (O_EXCL): never leave it to block a retry
        except OSError:
            pass
        raise
    return target


def _copy_exclusive(target: Path, source: Path, root: Path) -> Path:
    try:
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0), 0o600)
    except FileExistsError as exc:
        raise ConfigError(f"destination already exists and is not registered: {target}") from exc
    return _copy_fd(fd, target, source, lambda: target.unlink(missing_ok=True))   # Windows: ancestors are pinned


def create_new_file(root: Path, relative: str, source: Path) -> Path:
    """Copy ``source`` to root/relative without ever replacing anything and without following a redirected
    ancestor. Directory pinning: POSIX walks with dir_fd and O_NOFOLLOW; Windows holds every ancestor open
    without FILE_SHARE_DELETE (it cannot be swapped) and rejects reparse points. The destination is created
    O_EXCL. Where neither primitive exists the call fails closed instead of using path-based creation."""
    contained_path(root, relative)                                  # shape check: relative, no '..', no drive
    parts = relative.replace("\\", "/").split("/")
    root = root.resolve()
    try:
        if os.name == "nt":
            target = _create_windows(root, parts, source)
        elif os.open in os.supports_dir_fd and os.mkdir in os.supports_dir_fd:
            target = _create_posix(root, parts, source)
        else:
            raise ConfigError("no race-free directory-relative file creation on this platform; refusing")
    except FileExistsError as exc:
        raise ConfigError(f"destination already exists and is not registered: {exc.filename}") from exc
    if os.name == "nt" and not target.resolve().is_relative_to(root):   # POSIX: the pinned descriptors already guarantee it
        target.unlink(missing_ok=True)
        raise ConfigError(f"destination left the trusted root: {target}")
    return target
