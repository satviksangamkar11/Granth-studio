"""Global canon: characters, locations and terminology with stable IDs and explicit identity decisions.

Identity rules (frozen section 4.2): uncertain matches are never merged automatically.
A possible match, or a name shared by two IDs, needs an explicit ``identity_decisions``
entry. ``same`` is refused because merging is a curated edit, not an automatic step.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Any

from .config import Project, load_yaml
from .errors import CanonReferenceError, ConfigError, IdentityConflict
from .integrity import normalize_text, sha256_obj
from .schemas import validate_document

PREFIX = {"characters": "chr", "locations": "loc", "terminology": "term", "props": "prp"}


@dataclass(frozen=True)
class Canon:
    entries: dict[str, dict[str, Any]]
    kinds: dict[str, str]
    documents: dict[str, dict[str, Any]]

    def require(self, entry_id: str, kind: str) -> dict[str, Any]:
        entry = self.entries.get(entry_id)
        if entry is None or self.kinds[entry_id] != kind:
            raise CanonReferenceError(f"unknown {kind} id {entry_id!r}")
        if entry["status"] != "approved":
            raise CanonReferenceError(f"{entry_id} is pending canon approval")
        return entry

    def digest(self) -> str:
        return sha256_obj(self.documents)


def _check_identities(kind: str, document: dict[str, Any]) -> None:
    decisions: dict[frozenset[str], str] = {}
    for item in document.get("identity_decisions", []):
        key = frozenset(item["ids"])
        if key in decisions:
            raise IdentityConflict(f"{kind}: duplicate identity decision for {sorted(key)}")
        decisions[key] = item["decision"]
    ids = {entry["id"] for entry in document["entries"]}
    for key, decision in decisions.items():
        if not key <= ids:
            raise IdentityConflict(f"{kind}: identity decision refers to unknown id in {sorted(key)}")
        if decision == "same":
            raise IdentityConflict(f"{sorted(key)}: 'same' requires a curated merge into one entry")
    for entry in document["entries"]:
        for other in entry.get("possible_matches", []):
            if frozenset({entry["id"], other}) not in decisions:
                raise IdentityConflict(f"{entry['id']} may be {other}: record an identity decision")
    owners: dict[str, set[str]] = {}
    for entry in document["entries"]:
        names = {normalize_text(entry["canonical_name"]), *(normalize_text(a) for a in entry.get("aliases", []))}
        for name in names:
            owners.setdefault(name, set()).add(entry["id"])
    for name, owner_ids in owners.items():
        if len(owner_ids) > 1:
            for pair in combinations(sorted(owner_ids), 2):
                if decisions.get(frozenset(pair)) != "different":
                    raise IdentityConflict(f"name {name!r} is shared by {sorted(owner_ids)}: record 'different' decisions")


def load_canon(project: Project) -> Canon:
    entries: dict[str, dict[str, Any]] = {}
    kinds: dict[str, str] = {}
    documents: dict[str, dict[str, Any]] = {}
    for kind, prefix in PREFIX.items():
        document = load_yaml(project.canon_dir / f"{kind}.yaml")
        validate_document("canon", document)
        if document["kind"] != kind:
            raise ConfigError(f"{kind}.yaml declares kind {document['kind']!r}")
        for entry in document["entries"]:
            entry_id = entry["id"]
            if not entry_id.startswith(prefix + "_"):
                raise ConfigError(f"{entry_id}: {kind} ids must start with {prefix}_")
            if entry_id in entries:
                raise IdentityConflict(f"duplicate canon id {entry_id}")
            entries[entry_id] = entry
            kinds[entry_id] = kind
        _check_identities(kind, document)
        documents[kind] = document
    return Canon(entries=entries, kinds=kinds, documents=documents)
