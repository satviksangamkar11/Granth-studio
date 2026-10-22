"""External model runners (IndicTrans2, IndicF5, ASR) behind one JSON-over-stdio contract.

A runner is an argv list from config/models.yaml. It reads one JSON object on stdin and prints
one JSON object on stdout. No shell is used and no runner has been executed on this project:
a section is usable only after its ``status`` is set to ``validated`` by a human who has seen a
real run, with its model and revision named.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from .errors import GateFailure, IntegrationUnavailable, TaskFailed
from .integrity import atomic_write_json, read_json, sha256_obj


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


def identity_block(section: dict[str, Any], answer: dict[str, Any]) -> dict[str, Any]:
    """Model identity evidence for a runner answer. ``verified`` only when the runner returned the identity it
    actually loaded and it equals the configured one; a configured revision string alone is never proof."""
    found = answer.get("verified")
    if found is None:
        return {"status": "unverified"}
    if not (isinstance(found, dict) and set(found) == {"model", "revision"}
            and all(isinstance(v, str) and v for v in found.values())):
        raise TaskFailed("runner 'verified' must be {'model': str, 'revision': str}")
    if (found["model"], found["revision"]) != (section["model"], section["revision"]):
        raise GateFailure(f"runner verified {found['model']}@{found['revision']} but {section['model']}@{section['revision']} "
                          "is configured: refusing the output")
    return {"status": "verified", "model": found["model"], "revision": found["revision"]}


def record_run_evidence(root: Path, section: dict[str, Any], request_sha256: str, answer: dict[str, Any],
                        outputs: dict[str, Any], inputs: dict[str, Any] | None = None) -> tuple[dict[str, Any], str]:
    """Bind one runner execution: the request, the exact response, the identity the runner reported, the
    configured identity and the outputs it produced. The record is stored content-addressed under ``root``
    (file name = hash of its content), so later stages can re-verify it. This makes tampering detectable; it does
    not authenticate the runner (no signing key exists), and real-library behaviour stays NOT VALIDATED."""
    identity = identity_block(section, answer)
    evidence = {"schema_version": 1, "kind": "model_run", "request_sha256": request_sha256,
                "response_sha256": sha256_obj(answer), "configured": {"model": section["model"], "revision": section["revision"]},
                "identity": identity, "outputs": outputs, "inputs": inputs or {}}
    digest = sha256_obj(evidence)
    root.mkdir(parents=True, exist_ok=True)
    atomic_write_json(root / f"{digest}.json", {**evidence, "evidence_sha256": digest})
    return identity, digest


def _covers(have: Any, want: Any) -> bool:
    return (isinstance(have, dict) and all(_covers(have.get(k), v) for k, v in want.items())) if isinstance(want, dict) else have == want


def verify_run_evidence(root: Path, digest: Any, identity: Any, model: str, revision: str, outputs: dict[str, Any],
                        where: str, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
    """Re-verify stored evidence at approval/release. Returns the identity block that may be carried forward:
    ``verified`` only when intact evidence confirms it for exactly these outputs; a claim without it is refused."""
    claimed = identity or {"status": "unverified"}
    if claimed.get("status") not in ("verified", "unverified"):
        raise GateFailure(f"{where}: unknown identity status {claimed.get('status')!r}")
    if digest is None:
        if claimed["status"] == "verified":
            raise GateFailure(f"{where}: claims a verified model identity but carries no run evidence")
        return {"status": "unverified"}
    path = root / f"{digest}.json"
    if not path.is_file():
        raise GateFailure(f"{where}: run evidence {str(digest)[:12]} is missing")
    record = read_json(path)
    body = {k: v for k, v in record.items() if k != "evidence_sha256"}
    if sha256_obj(body) != digest or record.get("evidence_sha256") != digest:
        raise GateFailure(f"{where}: run evidence {str(digest)[:12]} fails its integrity check")
    if record["configured"] != {"model": model, "revision": revision}:
        raise GateFailure(f"{where}: run evidence was recorded for a different configured model")
    if record["identity"] != claimed:
        raise GateFailure(f"{where}: stored identity differs from the run evidence")
    if not _covers(record["outputs"], outputs):
        raise GateFailure(f"{where}: run evidence does not cover this output")
    if inputs and not _covers(record.get("inputs", {}), inputs):
        raise GateFailure(f"{where}: run evidence was recorded for a different request")
    if claimed["status"] == "verified" and (claimed.get("model"), claimed.get("revision")) != (model, revision):
        raise GateFailure(f"{where}: verified identity differs from the recorded model {model}@{revision}")
    return claimed
