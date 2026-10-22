"""Research approval: source receipts, the open-question gate and source-change detection.

Approval writes a receipt that pins the SHA-256 of research.yaml. Any later edit makes the
receipt stale, so production stops until a new approval version is recorded. Any item that
is not ``answered`` (open or provisional) blocks approval.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import Project, load_yaml
from .errors import ConfigError, ResearchNotApproved, SourceChanged
from .integrity import atomic_write_json, read_json, sha256_file
from .schemas import validate_document

RESEARCH_FILE = "research.yaml"
RECEIPT_FILE = "source_receipt.json"


@dataclass(frozen=True)
class SourceStatus:
    adhyay: int
    approved: bool
    version: int | None
    changed: bool


def adhyay_research_dir(project: Project, adhyay: int) -> Path:
    return project.research_dir / f"adhyay_{adhyay:02d}"


def load_research(project: Project, adhyay: int) -> dict[str, Any]:
    data = load_yaml(adhyay_research_dir(project, adhyay) / RESEARCH_FILE)
    validate_document("research", data)
    if data["adhyay"] != adhyay:
        raise ConfigError(f"research folder adhyay {adhyay} declares adhyay {data['adhyay']}")
    prefix = f"a{adhyay:02d}_s"
    for scene in data["scenes"]:
        if not scene["scene_id"].startswith(prefix):
            raise ConfigError(f"scene {scene['scene_id']} does not belong to adhyay {adhyay}")
    return data


def blocking_items(research: dict[str, Any]) -> list[str]:
    return [q["id"] for q in research["open_questions"] if q["status"] != "answered"]


def dialogue_index(research: dict[str, Any]) -> dict[str, dict[str, str]]:
    index: dict[str, dict[str, str]] = {}
    for scene in research["scenes"]:
        for line in scene["dialogue"]:
            if line["id"] in index:
                raise ConfigError(f"duplicate dialogue id {line['id']}")
            index[line["id"]] = {"scene_id": scene["scene_id"], "speaker": line["speaker"], "text": line["text"]}
    return index


def _read_receipt(project: Project, adhyay: int) -> dict[str, Any] | None:
    path = adhyay_research_dir(project, adhyay) / RECEIPT_FILE
    if not path.is_file():
        return None
    data = read_json(path)
    validate_document("source_receipt", data)
    return data


def approve(project: Project, adhyay: int, reviewer: str, approved_at: str) -> dict[str, Any]:
    if not reviewer.strip():
        raise ConfigError("a reviewer name is required")
    research = load_research(project, adhyay)
    blocked = blocking_items(research)
    if blocked:
        raise ResearchNotApproved(f"{len(blocked)} unresolved item(s) block approval: {', '.join(blocked[:12])}")
    folder = adhyay_research_dir(project, adhyay)
    previous = _read_receipt(project, adhyay)
    receipt = {
        "schema_version": 1,
        "adhyay": adhyay,
        "version": previous["version"] + 1 if previous else 1,
        "research_sha256": sha256_file(folder / RESEARCH_FILE),
        "approved_by": reviewer.strip(),
        "approved_at": approved_at,
    }
    validate_document("source_receipt", receipt)
    atomic_write_json(folder / RECEIPT_FILE, receipt)
    return receipt


def verify_source(project: Project, adhyay: int) -> SourceStatus:
    receipt = _read_receipt(project, adhyay)
    if receipt is None:
        return SourceStatus(adhyay, False, None, False)
    current = sha256_file(adhyay_research_dir(project, adhyay) / RESEARCH_FILE)
    return SourceStatus(adhyay, True, receipt["version"], current != receipt["research_sha256"])


def require_approved(project: Project, adhyay: int) -> dict[str, Any]:
    receipt = _read_receipt(project, adhyay)
    if receipt is None:
        raise ResearchNotApproved(f"adhyay {adhyay}: no source receipt (not approved)")
    status = verify_source(project, adhyay)
    if status.changed:
        raise SourceChanged(
            f"adhyay {adhyay}: research.yaml changed after approval version {receipt['version']}; "
            "re-approve to record a new version"
        )
    return receipt
