from __future__ import annotations

import jsonschema
from jsonschema import Draft202012Validator
from typing import Any

SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "stage1_story_map",
    "type": "object",
    "additionalProperties": False,
    "required": ["adhyay", "ovi_types", "events"],
    "properties": {
        "adhyay": {"type": "integer", "minimum": 1, "maximum": 21},
        "ovi_types": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["ovi", "type"],
                "properties": {
                    "ovi": {"type": "integer", "minimum": 1},
                    "type": {"enum": ["STORY", "TEACHING", "PHILOSOPHY", "INVOCATION", "RECAP", "PHALASHRUTI", "OTHER"]}
                }
            }
        },
        "events": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["event_id", "title", "ovi_range", "key_ovis", "kind", "closure"],
                "properties": {
                    "event_id": {"type": "string", "pattern": "^E[0-9]{1,2}$"},
                    "title": {"type": "string", "minLength": 1, "maxLength": 400},
                    "ovi_range": {
                        "type": "array",
                        "minItems": 2,
                        "maxItems": 2,
                        "items": {"type": "integer", "minimum": 1}
                    },
                    "key_ovis": {
                        "type": "array",
                        "items": {"type": "integer", "minimum": 1}
                    },
                    "kind": {"enum": ["story", "discourse"]},
                    "closure": {"enum": ["RESOLVED_IN_ADHYAY", "CONTINUES_NEXT_ADHYAY", "STARTED_EARLIER", "SOURCE_INCOMPLETE_OR_AMBIGUOUS", "NA"]}
                }
            }
        }
    }
}

_validator = Draft202012Validator(SCHEMA)


def schema_errors(doc: Any) -> list[str]:
    errors = []
    for err in _validator.iter_errors(doc):
        path = "/".join(str(p) for p in err.path) if err.path else "doc"
        errors.append(f"story_map {path}: {err.message}")
    return errors


def validate(adhyay: int, doc: dict[str, Any], docs: dict[str, Any], ctx: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    notes: list[str] = []

    # Adhyay check
    doc_adhyay = doc.get("adhyay")
    if doc_adhyay != adhyay:
        errors.append(f"story_map adhyay {doc_adhyay} does not match {adhyay}")

    # Get chapter_ovis from ctx (convert to set)
    chapter_ovis = set(ctx.get("chapter_ovis", []))

    # Check ovi_types
    ovi_types = doc.get("ovi_types", [])
    typed_ovis: dict[int, int] = {}  # ovi -> count
    for item in ovi_types:
        ovi = item.get("ovi")
        if ovi is not None:
            typed_ovis[ovi] = typed_ovis.get(ovi, 0) + 1

    # Each ovi in chapter_ovis typed exactly once
    for ovi in chapter_ovis:
        count = typed_ovis.get(ovi, 0)
        if count == 0:
            errors.append(f"ovi {ovi} is untyped")
        elif count > 1:
            errors.append(f"ovi {ovi} is typed twice")

    # Typed ovis outside the chapter reported
    for ovi in typed_ovis:
        if ovi not in chapter_ovis:
            errors.append(f"ovi {ovi} is outside chapter")

    # Check events
    events = doc.get("events", [])
    for event in events:
        event_id = event.get("event_id", "unknown")
        ovi_range = event.get("ovi_range", [])
        key_ovis = event.get("key_ovis", [])

        # ovi_range lo <= hi
        if len(ovi_range) == 2:
            lo, hi = ovi_range[0], ovi_range[1]
            if lo > hi:
                errors.append(f"{event_id}: ovi_range lo > hi")

        # key_ovis inside their range
        if len(ovi_range) == 2:
            lo, hi = ovi_range[0], ovi_range[1]
            for kovi in key_ovis:
                if kovi < lo or kovi > hi:
                    errors.append(f"{event_id}: key_ovi {kovi} outside ovi_range")

    return errors + notes
