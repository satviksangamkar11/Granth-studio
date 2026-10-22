"""External model runners (IndicTrans2, IndicF5, ASR) behind one JSON-over-stdio contract.

A runner is an argv list from config/models.yaml. It reads one JSON object on stdin and prints
one JSON object on stdout. No shell is used and no runner has been executed on this project:
a section is usable only after its ``status`` is set to ``validated`` by a human who has seen a
real run, with its model and revision named.
"""
from __future__ import annotations

import json
import subprocess
from typing import Any

from .errors import IntegrationUnavailable, TaskFailed


def require_runner(models: dict[str, Any], key: str, label: str) -> dict[str, Any]:
    section = models.get(key)
    if not section or section["status"] != "validated":
        status = section["status"] if section else "not configured"
        raise IntegrationUnavailable(f"{label} status is '{status}' (model and version undecided, O-007): NOT VALIDATED")
    for field in ("command", "model", "revision"):
        if not section[field]:
            raise IntegrationUnavailable(f"{label} {field} is not set (O-007): NOT VALIDATED")
    return section


def run_json(section: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    try:
        done = subprocess.run(section["command"], input=json.dumps(payload), capture_output=True, text=True,
                              encoding="utf-8", timeout=section["timeout_s"])
    except FileNotFoundError as exc:
        raise IntegrationUnavailable(f"runner command not found: {section['command'][0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise TaskFailed(f"runner exceeded {section['timeout_s']} s") from exc
    if done.returncode != 0:
        raise TaskFailed(f"runner exited {done.returncode}: {done.stderr.strip()[-500:]}")
    try:
        result = json.loads(done.stdout)
    except json.JSONDecodeError as exc:
        raise TaskFailed(f"runner printed invalid JSON: {exc}") from exc
    if not isinstance(result, dict):
        raise TaskFailed("runner output must be a JSON object")
    return result
