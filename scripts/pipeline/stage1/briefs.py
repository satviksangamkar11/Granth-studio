from __future__ import annotations

import json
import re
from typing import Any

import jsonschema
from jsonschema import Draft202012Validator

SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "stage1_image_briefs",
    "type": "object",
    "additionalProperties": False,
    "required": ["adhyay", "images"],
    "properties": {
        "adhyay": {"type": "integer", "minimum": 1, "maximum": 21},
        "images": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "image_id",
                    "scene_id",
                    "shot_ids",
                    "people",
                    "place_id",
                    "prop",
                    "prop_state",
                    "camera",
                    "light",
                    "reason_new",
                    "on_screen_facts",
                    "references",
                ],
                "properties": {
                    "image_id": {
                        "type": "string",
                        "pattern": "^s[0-9]{1,2}_[a-z][a-z0-9_]{0,40}$",
                    },
                    "scene_id": {"type": "string", "pattern": "^S[0-9]{1,2}$"},
                    "shot_ids": {
                        "type": "array",
                        "items": {"type": "string", "pattern": "^S[0-9]{1,2}-[0-9]{1,2}$"},
                        "minItems": 1,
                    },
                    "people": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["name", "position", "pose", "gaze"],
                            "properties": {
                                "name": {"type": "string", "minLength": 1, "maxLength": 400},
                                "position": {"type": "string", "minLength": 1, "maxLength": 400},
                                "pose": {"type": "string", "minLength": 1, "maxLength": 400},
                                "gaze": {"type": "string", "minLength": 1, "maxLength": 400},
                            },
                        },
                    },
                    "place_id": {"type": "string", "minLength": 1, "maxLength": 400},
                    "prop": {"type": ["string", "null"], "minLength": 1, "maxLength": 400},
                    "prop_state": {"type": ["string", "null"], "minLength": 1, "maxLength": 400},
                    "camera": {"type": "string", "minLength": 1, "maxLength": 400},
                    "light": {"type": "string", "minLength": 1, "maxLength": 400},
                    "reason_new": {"type": "string", "minLength": 1, "maxLength": 400},
                    "on_screen_facts": {
                        "type": "array",
                        "items": {"type": "string", "minLength": 1, "maxLength": 400},
                        "minItems": 1,
                    },
                    "references": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["characters", "place", "style_anchor", "prop"],
                        "properties": {
                            "characters": {
                                "type": "array",
                                "items": {"type": "string", "minLength": 1, "maxLength": 400},
                            },
                            "place": {"type": "string", "minLength": 1, "maxLength": 400},
                            "style_anchor": {"type": "string", "minLength": 1, "maxLength": 400},
                            "prop": {"type": ["string", "null"], "minLength": 1, "maxLength": 400},
                        },
                    },
                },
            },
        },
    },
}

_validator = Draft202012Validator(SCHEMA)


def schema_errors(doc: Any) -> list[str]:
    errors = []
    for err in _validator.iter_errors(doc):
        path = "/".join(str(p) for p in err.path) if err.path else "doc"
        errors.append(f"briefs {path}: {err.message}")
    return errors


def _validate_semantic(adhyay: int, doc: Any, docs: dict[str, Any], ctx: dict[str, Any]) -> list[str]:
    messages: list[str] = []
    notes: list[str] = []

    if not isinstance(doc, dict):
        return ["briefs doc: not an object"]

    doc_adhyay = doc.get("adhyay")
    if doc_adhyay != adhyay:
        messages.append(f"briefs adhyay {doc_adhyay} does not match {adhyay}")

    images = doc.get("images", [])
    if not isinstance(images, list):
        return messages

    scenes_doc = docs.get("scenes", {})
    scenes_list = scenes_doc.get("scenes", []) if isinstance(scenes_doc, dict) else []
    scene_ids = {
        sid for s in scenes_list
        if isinstance(s, dict)
        for sid in [s.get("scene_id")]
        if isinstance(sid, str)
    }

    shots_doc = docs.get("shots", {})
    shots_list = shots_doc.get("shots", []) if isinstance(shots_doc, dict) else []
    shot_map: dict[str, str] = {}
    for sh in shots_list:
        if isinstance(sh, dict):
            sid = sh.get("shot_id")
            scid = sh.get("scene_id")
            if isinstance(sid, str) and isinstance(scid, str):
                shot_map[sid] = scid

    seen_image_ids: set[str] = set()

    for img in images:
        if not isinstance(img, dict):
            continue
        img_id = img.get("image_id")
        if not isinstance(img_id, str):
            continue

        if img_id in seen_image_ids:
            messages.append(f"{img_id}: unique with scene prefix")
        seen_image_ids.add(img_id)

        scene_id = img.get("scene_id")
        if isinstance(scene_id, str):
            m = re.match(r"^S([0-9]{1,2})$", scene_id)
            if m:
                expected_prefix = f"s{int(m.group(1))}_"
                if not img_id.startswith(expected_prefix):
                    messages.append(f"{img_id}: unique with scene prefix")

        if isinstance(scene_id, str) and scene_id not in scene_ids:
            messages.append(f"{img_id}: scene {scene_id} does not exist")

        shot_ids = img.get("shot_ids", [])
        if isinstance(shot_ids, list):
            for sid in shot_ids:
                if not isinstance(sid, str) or sid not in shot_map:
                    messages.append(f"{img_id}: shot_ids exist and belong to the same scene")
                elif shot_map[sid] != scene_id:
                    messages.append(f"{img_id}: shot_ids exist and belong to the same scene")

        people = img.get("people", [])
        for i, p in enumerate(people):
            name = p.get("name")
            if not isinstance(name, str) or name.strip() == "":
                messages.append(f"{img_id}: no empty name")

        on_screen_facts = img.get("on_screen_facts", [])
        if not isinstance(on_screen_facts, list) or len(on_screen_facts) == 0:
            messages.append(f"{img_id}: non-empty")

    return messages + notes


def validate(adhyay: int, doc: Any, docs: dict[str, Any], ctx: dict[str, Any]) -> list[str]:
    try:
        return _validate_semantic(adhyay, doc, docs, ctx)
    except (TypeError, AttributeError, KeyError, ValueError, IndexError):
        return ["briefs: malformed structure"]
