from __future__ import annotations

import json
import os
import time
from typing import Any


class CapRefused(Exception):
    """Raised when a cap check fails or lock cannot be acquired. A crashed run can leave `<spend>.lock` behind: the owner deletes it after checking no run is active."""


def _is_finite_number(x: Any, allow_zero: bool = True) -> bool:
    """A finite int/float (bool rejected) that is >= 0, or > 0 when allow_zero is False."""
    if isinstance(x, bool) or not isinstance(x, (int, float)) or x != x or x in (float("inf"), float("-inf")):
        return False
    return x >= 0 if allow_zero else x > 0


def load_caps(path: str) -> dict[str, Any]:
    """Load caps from JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("caps root must be an object")

    total = data.get("total")
    stages = data.get("stages")

    if not _is_finite_number(total, allow_zero=False):
        raise ValueError("total must be a finite number > 0")
    if not isinstance(stages, dict) or not stages:
        raise ValueError("stages must be a non-empty object")

    stage_sum = 0.0
    for name, cap in stages.items():
        if not _is_finite_number(cap, allow_zero=True):
            raise ValueError(f"stage {name!r} cap must be a finite number >= 0")
        stage_sum += float(cap)

    if stage_sum > float(total) + 1e-9:
        raise ValueError("stage caps sum exceeds total")

    return {"total": float(total), "stages": {k: float(v) for k, v in stages.items()}}


def check(caps: dict[str, Any], spent_by_stage: dict[str, float], stage: str, worst_usd: float) -> float:
    """Pure cap check. Returns remaining budget for the stage after this request."""
    if not _is_finite_number(worst_usd, allow_zero=True):
        raise ValueError("worst_usd must be a finite number >= 0")

    total = caps["total"]
    stages = caps["stages"]

    if stage not in stages:
        raise CapRefused(f"unknown stage: {stage}")

    spent_total = sum(spent_by_stage.values())
    if spent_total + worst_usd > total + 1e-9:
        raise CapRefused("total cap exceeded")

    stage_spent = spent_by_stage.get(stage, 0.0)
    stage_cap = stages[stage]
    if stage_spent + worst_usd > stage_cap + 1e-9:
        raise CapRefused(f"stage {stage!r} cap exceeded")

    return stage_cap - (stage_spent + worst_usd)


def _replay(spend_path) -> dict[str, dict[str, Any]]:
    """Read and replay the spend file. Returns dict of rid -> latest event info."""
    spend_path = os.fspath(spend_path)
    if not os.path.exists(spend_path):
        return {}

    requests: dict[str, dict[str, Any]] = {}
    with open(spend_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"invalid JSON on line {line_num}") from e

            if not isinstance(event, dict):
                raise ValueError(f"event on line {line_num} must be an object")

            rid = event.get("id")
            if not isinstance(rid, str) or not rid:
                raise ValueError(f"event on line {line_num} missing or invalid id")

            status = event.get("status")
            if status not in ("open", "settled", "UNKNOWN"):
                raise ValueError(f"event on line {line_num} has invalid status")

            if status == "open":
                stage = event.get("stage")
                reserved = event.get("reserved")
                if not isinstance(stage, str) or not stage:
                    raise ValueError(f"open event on line {line_num} missing stage")
                if not _is_finite_number(reserved, allow_zero=True):
                    raise ValueError(f"open event on line {line_num} invalid reserved")
                if rid in requests:
                    raise ValueError(f"duplicate open event for {rid!r} on line {line_num}")
                requests[rid] = {
                    "stage": stage,
                    "status": "open",
                    "reserved": float(reserved),
                    "actual": None,
                }
            elif status == "settled":
                actual = event.get("actual")
                if not _is_finite_number(actual, allow_zero=True):
                    raise ValueError(f"settled event on line {line_num} invalid actual")
                if rid not in requests:
                    raise ValueError(f"settled event on line {line_num} for unknown rid")
                if requests[rid]["status"] != "open" and requests[rid]["status"] != "UNKNOWN":
                    raise ValueError(f"settled event on line {line_num} for non-open request")
                requests[rid]["status"] = "settled"
                requests[rid]["actual"] = float(actual)
            elif status == "UNKNOWN":
                why = event.get("why", "")
                if not isinstance(why, str):
                    raise ValueError(f"UNKNOWN event on line {line_num} invalid why")
                if rid not in requests:
                    raise ValueError(f"UNKNOWN event on line {line_num} for unknown rid")
                if requests[rid]["status"] != "open":
                    raise ValueError(f"UNKNOWN event on line {line_num} for non-open request")
                requests[rid]["status"] = "UNKNOWN"
                requests[rid]["why"] = why[:80]

    return requests


def _acquire_lock(lock_path: str) -> int:
    """Acquire exclusive lock. Returns file descriptor."""
    deadline = time.monotonic() + 10.0
    while True:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            return fd
        except FileExistsError:
            if time.monotonic() > deadline:
                raise CapRefused("locked")
            time.sleep(0.02)


def _release_lock(fd: int, lock_path: str) -> None:
    """Release lock."""
    try:
        os.close(fd)
    finally:
        try:
            os.unlink(lock_path)
        except OSError:
            pass


def _append_event(spend_path, event: dict[str, Any]) -> None:
    """Append a JSON line to the spend file."""
    spend_path = os.fspath(spend_path)
    os.makedirs(os.path.dirname(spend_path) or ".", exist_ok=True)
    with open(spend_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, separators=(",", ":")) + "\n")


def reserve(spend_path, caps: dict[str, Any], stage: str, worst_usd: float, rid: str, require_reconciled: bool = False) -> float:
    """Reserve budget for a request."""
    if not rid:
        raise ValueError("rid must be non-empty")

    spend_path = os.fspath(spend_path)
    os.makedirs(os.path.dirname(spend_path) or ".", exist_ok=True)       # the lock needs the folder
    lock_path = spend_path + ".lock"
    fd = _acquire_lock(lock_path)
    try:
        requests = _replay(spend_path)

        if rid in requests:
            raise ValueError("rid already used")

        if require_reconciled:
            for r in requests.values():
                if r["status"] in ("open", "UNKNOWN"):
                    raise CapRefused("unreconciled request exists")

        spent_by_stage: dict[str, float] = {}
        for r in requests.values():
            amt = r["actual"] if r["actual"] is not None else r["reserved"]
            spent_by_stage[r["stage"]] = spent_by_stage.get(r["stage"], 0.0) + amt

        remaining = check(caps, spent_by_stage, stage, worst_usd)

        _append_event(spend_path, {
            "id": rid,
            "stage": stage,
            "status": "open",
            "reserved": worst_usd,
        })
        return remaining
    finally:
        _release_lock(fd, lock_path)


def settle(spend_path, rid: str, actual_usd: float) -> None:
    """Settle a request with actual cost."""
    if not _is_finite_number(actual_usd, allow_zero=True):
        raise ValueError("actual_usd must be a finite number >= 0")

    spend_path = os.fspath(spend_path)
    os.makedirs(os.path.dirname(spend_path) or ".", exist_ok=True)       # the lock needs the folder
    lock_path = spend_path + ".lock"
    fd = _acquire_lock(lock_path)
    try:
        requests = _replay(spend_path)

        if rid not in requests:
            raise ValueError("unknown rid")
        if requests[rid]["status"] != "open":
            raise ValueError("request not open")

        _append_event(spend_path, {
            "id": rid,
            "status": "settled",
            "actual": actual_usd,
        })
    finally:
        _release_lock(fd, lock_path)


def unknown(spend_path, rid: str, why: str) -> None:
    """Mark a request as UNKNOWN."""
    spend_path = os.fspath(spend_path)
    os.makedirs(os.path.dirname(spend_path) or ".", exist_ok=True)       # the lock needs the folder
    lock_path = spend_path + ".lock"
    fd = _acquire_lock(lock_path)
    try:
        requests = _replay(spend_path)

        if rid not in requests:
            raise ValueError("unknown rid")
        if requests[rid]["status"] != "open":
            raise ValueError("request not open")

        _append_event(spend_path, {
            "id": rid,
            "status": "UNKNOWN",
            "why": why[:80],
        })
    finally:
        _release_lock(fd, lock_path)


def reconcile(spend_path, rid: str, actual_usd: float, note: str) -> None:
    """Reconcile an open or UNKNOWN request."""
    if not _is_finite_number(actual_usd, allow_zero=True):
        raise ValueError("actual_usd must be a finite number >= 0")
    if not isinstance(note, str) or len(note.strip()) < 5:
        raise ValueError("note must be at least 5 non-whitespace characters")

    spend_path = os.fspath(spend_path)
    os.makedirs(os.path.dirname(spend_path) or ".", exist_ok=True)       # the lock needs the folder
    lock_path = spend_path + ".lock"
    fd = _acquire_lock(lock_path)
    try:
        requests = _replay(spend_path)

        if rid not in requests:
            raise ValueError("unknown rid")
        if requests[rid]["status"] not in ("open", "UNKNOWN"):
            raise ValueError("request not open or UNKNOWN")

        _append_event(spend_path, {
            "id": rid,
            "status": "settled",
            "actual": actual_usd,
            "reconciled": note.strip()[:80],
        })
    finally:
        _release_lock(fd, lock_path)


def state(spend_path) -> dict[str, dict[str, Any]]:
    """Return current state of all requests."""
    requests = _replay(spend_path)
    result = {}
    for rid, info in requests.items():
        result[rid] = {
            "stage": info["stage"],
            "status": info["status"],
            "reserved": info["reserved"],
            "actual": info["actual"],
        }
    return result


def spent(spend_path) -> dict[str, float]:
    """Return total spent per stage (actual if settled, else reserved)."""
    requests = _replay(spend_path)
    totals: dict[str, float] = {}
    for info in requests.values():
        amt = info["actual"] if info["actual"] is not None else info["reserved"]
        totals[info["stage"]] = totals.get(info["stage"], 0.0) + amt
    return totals


def unreconciled(spend_path) -> list[str]:
    """Rids whose latest status is open or UNKNOWN, in file order (same validated replay as every other reader)."""
    return [rid for rid, r in _replay(spend_path).items() if r["status"] in ("open", "UNKNOWN")]
