from __future__ import annotations

import jsonschema
from jsonschema import Draft202012Validator
from typing import Any

SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "stage1_canon_looks",
    "type": "object",
    "additionalProperties": False,
    "required": ["adhyay", "entries"],
    "properties": {
        "adhyay": {
            "type": "integer",
            "minimum": 1,
            "maximum": 21
        },
        "entries": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["entity_id", "kind", "state_id", "look", "source_ovis", "basis"],
                "properties": {
                    "entity_id": {"type": "string"},
                    "kind": {"type": "string", "enum": ["character", "place", "prop"]},
                    "state_id": {"type": "string"},
                    "look": {"type": "string", "minLength": 1, "maxLength": 400},
                    "source_ovis": {
                        "type": "array",
                        "minItems": 1,
                        "items": {"type": "integer", "minimum": 1}
                    },
                    "basis": {"type": "string", "enum": ["stated", "inferred"]}
                }
            }
        }
    }
}

_validator = Draft202012Validator(SCHEMA)


def schema_errors(doc: Any) -> list[str]:
    errors = []
    for error in _validator.iter_errors(doc):
        path = "/".join(str(p) for p in error.path) if error.path else "doc"
        errors.append(f"looks {path}: {error.message}")
    return errors


def validate(adhyay: int, doc: Any, docs: dict[str, Any], ctx: dict[str, Any]) -> list[str]:
    messages: list[str] = []
    notes: list[str] = []

    if not isinstance(doc, dict):
        return ["looks doc: not an object"]

    doc_adhyay = doc.get("adhyay")
    if doc_adhyay != adhyay:
        messages.append(f"looks adhyay {doc_adhyay} does not match {adhyay}")

    entries = doc.get("entries")
    if not isinstance(entries, list):
        return messages

    chapter_ovis = set(ctx.get("chapter_ovis", []))
    known_states = ctx.get("known_states", {})
    if not isinstance(known_states, dict):
        known_states = {}

    seen_pairs = set()

    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue

        entity_id = entry.get("entity_id")
        state_id = entry.get("state_id")
        source_ovis = entry.get("source_ovis")

        item_id = f"{entity_id}:{state_id}" if entity_id and state_id else f"entry[{idx}]"

        if entity_id and state_id:
            pair = (entity_id, state_id)
            if pair in seen_pairs:
                messages.append(f"{item_id}: duplicate entity_id+state_id")
            else:
                seen_pairs.add(pair)

        if isinstance(source_ovis, list):
            for ovi in source_ovis:
                if ovi not in chapter_ovis:
                    messages.append(f"{item_id}: source_ovi {ovi} not in chapter_ovis")

        if entity_id in known_states and isinstance(known_states[entity_id], (list, set)):
            known = set(known_states[entity_id])
            if state_id in known:
                messages.append(f"{entity_id}: known state {state_id} redecided")

    messages.extend(notes)
    return messages
