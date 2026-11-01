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
                    "preset": {"type": "string", "pattern": "^([0-9]{2}_[a-z0-9_]+|NEED_NEW)$"},
                    "need_new": {"type": ["object", "null"]},
                    "needs_cutout": {"type": "boolean"},
                    "pose": {"type": "string", "minLength": 1, "maxLength": 400},
                    "framing": {"type": "string", "minLength": 1, "maxLength": 400},
                },
                "if": {"properties": {"preset": {"const": "NEED_NEW"}}},
                "then": {
                    "properties": {
                        "need_new": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["reason", "class"],
                            "properties": {
                                "reason": {"type": "string", "minLength": 1, "maxLength": 400},
                                "class": {"enum": ["missing_image", "json_arrangement", "renderer_gap"]},
                            },
                        }
                    }
                },
                "else": {"properties": {"need_new": {"type": "null"}}},
            },
        },
    },
}

_validator = Draft202012Validator(SCHEMA)


def schema_errors(doc: dict[str, Any]) -> list[str]:
    errors = []
    if not isinstance(doc, dict):
        errors.append("shots doc: document must be an object")
        return errors
    for err in _validator.iter_errors(doc):
        path = "/".join(str(p) for p in err.path) if err.path else "doc"
        errors.append(f"shots {path}: {err.message}")
    return errors


def _validate_impl(adhyay: int, doc: dict[str, Any], docs: dict[str, Any], ctx: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    notes: list[str] = []

    # Guard: doc must be a dict
    if not isinstance(doc, dict):
        errors.append("shots doc: document must be an object")
        return errors + notes

    # Adhyay check
    doc_adhyay = doc.get("adhyay")
    if doc_adhyay != adhyay:
        errors.append(f"shots adhyay {doc_adhyay} does not match {adhyay}")

    shots_list = doc.get("shots", [])
    if not isinstance(shots_list, list):
        shots_list = []

    scenes_doc = docs.get("scenes", {})
    if not isinstance(scenes_doc, dict):
        scenes_doc = {}
    scenes = scenes_doc.get("scenes", [])
    if not isinstance(scenes, list):
        scenes = []

    # Build scene lookup
    scene_by_id = {}
    for s in scenes:
        if isinstance(s, dict) and "scene_id" in s and isinstance(s["scene_id"], str):
            scene_by_id[s["scene_id"]] = s

    # Collect preset_ids from ctx
    preset_ids = set(ctx.get("preset_ids", []) or [])

    # Track shot numbers per scene for consecutiveness (grouped by scene_id)
    shot_nums_by_scene: dict[str, list[int]] = {}
    shot_ids_seen: set[str] = set()

    # Track which lines are covered by shots (only lines belonging to the shot's scene)
    covered_lines: set[str] = set()

    for shot in shots_list:
        if not isinstance(shot, dict):
            continue
        shot_id = shot.get("shot_id", "")
        scene_id = shot.get("scene_id", "")

        # Unique shot ids
        if isinstance(shot_id, str) and shot_id in shot_ids_seen:
            errors.append(f"{shot_id}: duplicate shot id")
        if isinstance(shot_id, str):
            shot_ids_seen.add(shot_id)

        # Parse shot number for consecutiveness
        if isinstance(shot_id, str):
            m = re.match(r"^S([0-9]{1,2})-([0-9]{1,2})$", shot_id)
            if m:
                scene_num = m.group(1)
                shot_num = int(m.group(2))
                # Group by scene_id only if scene_id is a string
                if isinstance(scene_id, str):
                    key = scene_id
                    shot_nums_by_scene.setdefault(key, []).append(shot_num)
                    # Reject shot_id prefix mismatch with scene_id
                    if f"S{scene_num}" != scene_id:
                        errors.append(f"{shot_id}: shot id prefix does not match scene_id")

        # Preset validation (run for every shot, even if scene missing)
        preset = shot.get("preset")
        if isinstance(preset, str) and preset != "NEED_NEW" and preset not in preset_ids:
            errors.append(f"{shot_id}: unknown preset {preset}")
        # A layer/cut-out preset cannot be fed by a flat final alone (owner 2026-11-01, flat-first)
        if preset in (ctx.get("cutout_presets") or []) and shot.get("needs_cutout") is False:
            errors.append(f"{shot_id}: preset {preset} needs layers or cut-outs but needs_cutout is false")

        # Scene exists
        if not isinstance(scene_id, str) or scene_id not in scene_by_id:
            if isinstance(shot_id, str):
                errors.append(f"{shot_id}: scene {scene_id} does not exist")
            continue

        scene = scene_by_id[scene_id]

        # ovi_ids inside scene range
        ovi_range = scene.get("ovi_range", [])
        if isinstance(ovi_range, list) and len(ovi_range) == 2:
            lo, hi = ovi_range[0], ovi_range[1]
            if isinstance(lo, int) and isinstance(hi, int):
                ovi_ids = shot.get("ovi_ids")
                if isinstance(ovi_ids, list):
                    for ovi in ovi_ids:
                        if isinstance(ovi, int) and not (lo <= ovi <= hi):
                            errors.append(f"{shot_id}: ovi {ovi} outside scene range [{lo}, {hi}]")

        # beat_line_ids belong to the scene
        scene_line_ids = set()
        line_ids = scene.get("line_ids", [])
        if isinstance(line_ids, list):
            for lid in line_ids:
                if isinstance(lid, str):
                    scene_line_ids.add(lid)
        beat_line_ids = shot.get("beat_line_ids")
        if isinstance(beat_line_ids, list):
            for line_id in beat_line_ids:
                if isinstance(line_id, str):
                    if line_id not in scene_line_ids:
                        errors.append(f"{shot_id}: beat line {line_id} not in scene {scene_id}")
                    else:
                        covered_lines.add(line_id)

    # Consecutive shot numbers per scene from 1
    for scene_key, nums in shot_nums_by_scene.items():
        nums_sorted = sorted(nums)
        if nums_sorted != list(range(1, len(nums_sorted) + 1)):
            errors.append(f"{scene_key}: shot numbers not consecutive from 1")

    # Every scene has shots
    for scene in scenes:
        if not isinstance(scene, dict):
            continue
        scene_id = scene.get("scene_id", "")
        if isinstance(scene_id, str) and scene_id and not any(
            isinstance(s, dict) and s.get("scene_id") == scene_id for s in shots_list
        ):
            errors.append(f"{scene_id}: scene has no shots")

    # Every line of every scene is in some shot's beat_line_ids
    for scene in scenes:
        if not isinstance(scene, dict):
            continue
        line_ids = scene.get("line_ids", [])
        if isinstance(line_ids, list):
            for line_id in line_ids:
                if isinstance(line_id, str) and line_id not in covered_lines:
                    errors.append(f"{line_id}: line is in no shot beat")

    return errors + notes


def validate(adhyay: int, doc: dict[str, Any], docs: dict[str, Any], ctx: dict[str, Any]) -> list[str]:
    try:
        return _validate_impl(adhyay, doc, docs, ctx)
    except (TypeError, AttributeError, KeyError, ValueError, IndexError):
        return ["shots: malformed structure"]
