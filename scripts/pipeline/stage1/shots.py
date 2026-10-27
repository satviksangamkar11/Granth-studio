from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema import Draft202012Validator

SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "stage1_shots",
    "type": "object",
    "additionalProperties": False,
    "required": ["adhyay", "shots"],
    "properties": {
        "adhyay": {"type": "integer", "minimum": 1, "maximum": 21},
        "shots": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "shot_id",
                    "scene_id",
                    "ovi_ids",
                    "beat_line_ids",
                    "preset",
                    "need_new",
                    "needs_cutout",
                    "pose",
                    "framing",
                ],
                "properties": {
                    "shot_id": {"type": "string", "pattern": "^S[0-9]{1,2}-[0-9]{1,2}$"},
                    "scene_id": {"type": "string", "pattern": "^S[0-9]{1,2}$"},
                    "ovi_ids": {
                        "type": "array",
                        "items": {"type": "integer", "minimum": 1},
                        "minItems": 1,
                    },
                    "beat_line_ids": {
                        "type": "array",
                        "items": {"type": "string", "pattern": "^S[0-9]{1,2}-L[0-9]{1,3}$"},
                        "minItems": 1,
                    },
                    "preset": {"type": "string"},
                    "need_new": {
                        "anyOf": [
                            {"type": "null"},
                            {
                                "type": "object",
                                "additionalProperties": False,
                                "required": ["reason", "class"],
                                "properties": {
                                    "reason": {"type": "string", "minLength": 1, "maxLength": 400},
                                    "class": {"enum": ["missing_image", "json_arrangement", "renderer_gap"]},
                                },
                            },
                        ]
                    },
                    "needs_cutout": {"type": "boolean"},
                    "pose": {"type": "string", "minLength": 1, "maxLength": 400},
                    "framing": {"type": "string", "minLength": 1, "maxLength": 400},
                },
                "if": {"properties": {"preset": {"const": "NEED_NEW"}}},
                "then": {"properties": {"need_new": {"type": "object"}}},
                "else": {"properties": {"need_new": {"type": "null"}}},
            },
        },
    },
}

_validator = Draft202012Validator(SCHEMA)


def schema_errors(doc: dict[str, Any]) -> list[str]:
    errors = []
    for err in _validator.iter_errors(doc):
        path = "/".join(str(p) for p in err.path) if err.path else "doc"
        errors.append(f"shots {path}: {err.message}")
    return errors


def validate(adhyay: int, doc: dict[str, Any], docs: dict[str, Any], ctx: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    notes: list[str] = []

    # Adhyay check
    doc_adhyay = doc.get("adhyay")
    if doc_adhyay != adhyay:
        errors.append(f"shots adhyay {doc_adhyay} does not match {adhyay}")

    shots = doc.get("shots", [])
    scenes_doc = docs.get("scenes", {})
    scenes = scenes_doc.get("scenes", [])

    # Build scene lookup
    scene_by_id = {s["scene_id"]: s for s in scenes if isinstance(s, dict) and "scene_id" in s}

    # Collect preset_ids from ctx
    preset_ids = set(ctx.get("preset_ids", []) or [])

    # Track shot numbers per scene for consecutiveness
    shot_nums_by_scene: dict[str, list[int]] = {}
    shot_ids_seen: set[str] = set()

    # Track which lines are covered by shots
    covered_lines: set[str] = set()

    for shot in shots:
        if not isinstance(shot, dict):
            continue
        shot_id = shot.get("shot_id", "")
        scene_id = shot.get("scene_id", "")

        # Unique shot ids
        if shot_id in shot_ids_seen:
            errors.append(f"{shot_id}: duplicate shot id")
        shot_ids_seen.add(shot_id)

        # Parse shot number for consecutiveness
        m = re.match(r"^S([0-9]{1,2})-([0-9]{1,2})$", shot_id)
        if m:
            scene_num = m.group(1)
            shot_num = int(m.group(2))
            key = f"S{scene_num}"
            shot_nums_by_scene.setdefault(key, []).append(shot_num)

        # Scene exists
        if scene_id not in scene_by_id:
            errors.append(f"{shot_id}: scene {scene_id} does not exist")
            continue

        scene = scene_by_id[scene_id]

        # ovi_ids inside scene range
        ovi_range = scene.get("ovi_range", [])
        if len(ovi_range) == 2:
            lo, hi = ovi_range[0], ovi_range[1]
            for ovi in shot.get("ovi_ids", []):
                if not (lo <= ovi <= hi):
                    errors.append(f"{shot_id}: ovi {ovi} outside scene range [{lo}, {hi}]")

        # beat_line_ids belong to the scene
        scene_line_ids = set(scene.get("line_ids", []))
        for line_id in shot.get("beat_line_ids", []):
            if line_id not in scene_line_ids:
                errors.append(f"{shot_id}: beat line {line_id} not in scene {scene_id}")
            covered_lines.add(line_id)

        # preset validation
        preset = shot.get("preset")
        if preset != "NEED_NEW" and preset not in preset_ids:
            errors.append(f"{shot_id}: unknown preset {preset}")

    # Consecutive shot numbers per scene from 1
    for scene_key, nums in shot_nums_by_scene.items():
        nums_sorted = sorted(nums)
        if nums_sorted != list(range(1, len(nums_sorted) + 1)):
            errors.append(f"{scene_key}: shot numbers not consecutive from 1")

    # Every scene has shots
    for scene in scenes:
        scene_id = scene.get("scene_id", "")
        if scene_id and not any(s.get("scene_id") == scene_id for s in shots):
            errors.append(f"{scene_id}: scene has no shots")

    # Every line of every scene is in some shot's beat_line_ids
    for scene in scenes:
        for line_id in scene.get("line_ids", []):
            if line_id not in covered_lines:
                errors.append(f"{line_id}: line is in no shot beat")

    return errors + notes
