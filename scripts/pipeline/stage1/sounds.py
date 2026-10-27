from __future__ import annotations

import json
import re
from typing import Any

import jsonschema
from jsonschema import Draft202012Validator

SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "stage1_sound_suggestions",
    "type": "object",
    "additionalProperties": False,
    "required": ["adhyay", "cues"],
    "properties": {
        "adhyay": {"type": "integer", "minimum": 1, "maximum": 21},
        "cues": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["scene_id", "anchor_line_id", "sound_id", "kind", "purpose", "basis"],
                "properties": {
                    "scene_id": {"type": "string", "pattern": "^S[0-9]{1,2}$"},
                    "anchor_line_id": {"type": "string", "pattern": "^S[0-9]{1,2}-L[0-9]{1,3}$"},
                    "sound_id": {"type": "string", "pattern": "^(bed|fx)_[a-z0-9_]+$|^NEED_NEW$"},
                    "kind": {"type": "string", "enum": ["bed", "fx"]},
                    "sound_prompt": {"type": "string", "minLength": 1, "maxLength": 400},
                    "purpose": {"type": "string", "minLength": 1, "maxLength": 400},
                    "basis": {"type": "string", "enum": ["stated", "staging"]},
                },
                "if": {"properties": {"sound_id": {"const": "NEED_NEW"}}},
                "then": {"required": ["sound_prompt"]},
                "else": {"not": {"required": ["sound_prompt"]}},
            },
        },
    },
}

_validator = Draft202012Validator(SCHEMA)


def schema_errors(doc: Any) -> list[str]:
    errors: list[str] = []
    for err in _validator.iter_errors(doc):
        path = "/".join(str(p) for p in err.path) if err.path else "doc"
        errors.append(f"sounds {path}: {err.message}")
    return errors


def validate(adhyay: int, doc: dict[str, Any], docs: dict[str, Any], ctx: dict[str, Any]) -> list[str]:
    messages: list[str] = []

    # Adhyay check
    doc_adhyay = doc.get("adhyay")
    if doc_adhyay != adhyay:
        messages.append(f"sounds adhyay {doc_adhyay} does not match {adhyay}")

    # Prepare context sets
    script_line_ids = set(ctx.get("script_line_ids", []))
    sound_ids = set(ctx.get("sound_ids", []))
    scenes_doc = docs.get("scenes", {})
    scenes_list = scenes_doc.get("scenes", [])

    # Build scene lookup
    scene_by_id: dict[str, dict[str, Any]] = {}
    for sc in scenes_list:
        sid = sc.get("scene_id")
        if sid:
            scene_by_id[sid] = sc

    cues = doc.get("cues", [])
    for i, cue in enumerate(cues):
        cue_id = f"cue[{i}]"
        scene_id = cue.get("scene_id")
        anchor_line_id = cue.get("anchor_line_id")
        sound_id = cue.get("sound_id")
        kind = cue.get("kind")

        # Scene exists
        if scene_id not in scene_by_id:
            messages.append(f"{cue_id}: scene '{scene_id}' does not exist")
            continue

        scene = scene_by_id[scene_id]

        # Anchor line belongs to the scene
        scene_line_ids = set(scene.get("line_ids", []))
        if anchor_line_id not in scene_line_ids:
            messages.append(f"{cue_id}: anchor line '{anchor_line_id}' not in scene '{scene_id}'")

        # sound_id in sound_ids or NEED_NEW
        if sound_id != "NEED_NEW" and sound_id not in sound_ids:
            messages.append(f"{cue_id}: sound_id '{sound_id}' not in sound_ids")

        # kind matches id prefix
        if sound_id != "NEED_NEW":
            expected_kind = "bed" if sound_id.startswith("bed_") else "fx" if sound_id.startswith("fx_") else None
            if expected_kind and kind != expected_kind:
                messages.append(f"{cue_id}: kind '{kind}' does not match sound_id prefix '{expected_kind}'")

    return messages
