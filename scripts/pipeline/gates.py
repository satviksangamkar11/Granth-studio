from __future__ import annotations

import importlib.util
from collections.abc import Mapping
from pathlib import Path
from typing import Any

_spec = importlib.util.spec_from_file_location("_gate_approvals", Path(__file__).with_name("approvals.py"))
_approvals = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_approvals)


class GateBlocked(Exception):
    """Raised when one or more items are not APPROVED in the pipeline state."""
    def __init__(self, blockers: dict[str, str]) -> None:
        self.blockers = blockers
        super().__init__(str(blockers))


def _local_status(approvals: Mapping[str, Any], item: str, current_hash: str | None) -> str:
    """DRAFT / APPROVED / STALE from approvals.status (a missing or invalid hash never approves)."""
    return _approvals.status(dict(approvals), item, current_hash)


def _collect_items(deps: Mapping[str, list[str]], extra: Any = ()) -> set[str]:
    """All items that appear as keys, in dependency lists, or in `extra` (items a caller asks about that have no dependencies)."""
    items = set(deps.keys()) | set(extra)
    for dep_list in deps.values():
        items.update(dep_list)
    return items


def _transitive_deps(deps: Mapping[str, list[str]], items: set[str]) -> dict[str, set[str]]:
    """Transitive dependencies for each item (excluding the item itself). Self-dependencies are ignored."""
    trans: dict[str, set[str]] = {}
    for item in items:
        visited: set[str] = set()
        stack = [item]
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            for neighbor in deps.get(node, []):
                if neighbor == item:  # ignore self-dependency
                    continue
                if neighbor not in visited:
                    stack.append(neighbor)
        visited.discard(item)
        trans[item] = visited
    return trans


def pipeline_state(
    deps: Mapping[str, list[str]],
    approvals: Mapping[str, Any],
    current_sha: Mapping[str, str],
    extra: Any = (),
) -> dict[str, str]:
    """Compute the final pipeline state for all items (plus any `extra` leaf items)."""
    items = _collect_items(deps, extra)
    local = {item: _local_status(approvals, item, current_sha.get(item)) for item in items}
    trans = _transitive_deps(deps, items)

    final: dict[str, str] = {}
    for item in items:
        if local[item] in ("DRAFT", "STALE"):
            final[item] = local[item]
        else:  # APPROVED
            # blocked if any transitive dependency has local status DRAFT or STALE
            blocked = any(local[dep] in ("DRAFT", "STALE") for dep in trans[item])
            final[item] = "BLOCKED" if blocked else "APPROVED"
    return final


def require_approved(
    items: list[str],
    deps: Mapping[str, list[str]],
    approvals: Mapping[str, Any],
    current_sha: Mapping[str, str],
) -> None:
    """Raise GateBlocked unless every listed item is APPROVED in the final state."""
    state = pipeline_state(deps, approvals, current_sha, items)
    every = _collect_items(deps, items)
    local = {item: _local_status(approvals, item, current_sha.get(item)) for item in every}
    trans = _transitive_deps(deps, every)

    blockers: dict[str, str] = {}
    for item in items:
        if state[item] != "APPROVED":
            if state[item] in ("DRAFT", "STALE"):
                blockers[item] = state[item]
            else:  # BLOCKED
                # non-approved transitive dependencies (local DRAFT or STALE)
                causes = sorted(dep for dep in trans[item] if local[dep] in ("DRAFT", "STALE"))
                blockers[item] = "BLOCKED by " + ", ".join(causes)
    if blockers:
        raise GateBlocked(blockers)


def ready_stages(
    stages: Mapping[str, list[str]],
    deps: Mapping[str, list[str]],
    approvals: Mapping[str, Any],
    current_sha: Mapping[str, str],
) -> list[str]:
    """Return sorted stage names whose every item is APPROVED in the final state."""
    state = pipeline_state(deps, approvals, current_sha, {i for items in stages.values() for i in items})
    ready = [name for name, items in stages.items() if all(state.get(item) == "APPROVED" for item in items)]
    return sorted(ready)


def next_approvals_needed(
    deps: Mapping[str, list[str]],
    approvals: Mapping[str, Any],
    current_sha: Mapping[str, str],
) -> list[str]:
    """Sorted items whose local status is DRAFT/STALE and whose direct dependencies are all APPROVED."""
    items = _collect_items(deps)
    local = {item: _local_status(approvals, item, current_sha.get(item)) for item in items}
    state = pipeline_state(deps, approvals, current_sha)

    needed = []
    for item in items:
        if local[item] in ("DRAFT", "STALE"):
            direct = deps.get(item, [])
            if all(state.get(dep) == "APPROVED" for dep in direct):
                needed.append(item)
    return sorted(needed)
