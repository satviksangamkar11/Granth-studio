from __future__ import annotations

import json
import re
from typing import Any

import jsonschema
from jsonschema import Draft202012Validator

SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "stage1_scenes",
    "type": "object",
    "additionalProperties": False,
    "required": ["adhyay", "scenes"],
    "properties": {
        "adhyay": {"type": "integer", "minimum": 1, "maximum": 21},
        "scenes": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["scene_id", "section_kind", "ovi_range", "goal", "turn", "line_ids"],
                "properties": {
                    "scene_id": {"type": "string", "pattern": "^S[0-9]{1,2}$"},
                    "section_kind": {"type": "string", "enum": ["story", "discourse"]},
                    "ovi_range": {
                        "type": "array",
                        "minItems": 2,
                        "maxItems": 2,
                        "items": {"type": "integer", "minimum": 1},
                    },
                    "goal": {"type": "string", "minLength": 1, "maxLength": 400},
                    "turn": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["ovi", "text"],
                        "properties": {
                            "ovi": {"type": "integer", "minimum": 1},
                            "text": {"type": "string", "minLength": 1, "maxLength": 400},
                        },
                    },
                    "line_ids": {
                        "type": "array",
                        "items": {"type": "string", "pattern": "^S[0-9]{1,2}-L[0-9]{1,3}$"},
                    },
                    "teaching_treatment": {
                        "type": "string",
                        "enum": ["none", "narration_over_typography", "contemplative_hold", "symbol_from_text"],
                    },
                },
                "if": {"properties": {"section_kind": {"const": "discourse"}}},
                "then": {"required": ["teaching_treatment"]},
                "else": {"not": {"required": ["teaching_treatment"]}},
            },
        },
    },
}

_validator = Draft202012Validator(SCHEMA)


def schema_errors(doc: Any) -> list[str]:
    errors = []
    for err in _validator.iter_errors(doc):
        path = "/".join(str(p) for p in err.path) if err.path else "doc"
        errors.append(f"scenes {path}: {err.message}")
    return errors


def validate(adhyay: int, doc: dict[str, Any], docs: dict[str, Any], ctx: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    notes: list[str] = []

    # adhyay check
    doc_adhyay = doc.get("adhyay")
    if doc_adhyay != adhyay:
        errors.append(f"scenes adhyay {doc_adhyay} does not match {adhyay}")

    scenes = doc.get("scenes", [])
    if not isinstance(scenes, list):
        return errors + notes

    # Convert ctx lists/sets to sets
    script_line_ids = set(ctx.get("script_line_ids", []))
    core_line_ids = set(ctx.get("core_line_ids", []))
    chapter_ovis = set(ctx.get("chapter_ovis", []))
    unfilmed_ovis = set(ctx.get("unfilmed_ovis", []))

    # Track seen items
    seen_scene_ids = set()
    seen_line_ids = set()
    all_covered_ovis = set()
    scene_ranges = []

    for i, scene in enumerate(scenes):
        if not isinstance(scene, dict):
            continue
        scene_id = scene.get("scene_id", f"<scene_{i}>")
        section_kind = scene.get("section_kind")
        ovi_range = scene.get("ovi_range", [])
        turn = scene.get("turn", {})
        line_ids = scene.get("line_ids", [])
        teaching_treatment = scene.get("teaching_treatment")

        # scene ids unique
        if scene_id in seen_scene_ids:
            errors.append(f"{scene_id}: duplicate scene id")
        seen_scene_ids.add(scene_id)

        # ovi_range lo <= hi
        if isinstance(ovi_range, list) and len(ovi_range) == 2:
            lo, hi = ovi_range[0], ovi_range[1]
            if not (isinstance(lo, int) and isinstance(hi, int)):
                errors.append(f"{scene_id}: ovi_range must be integers")
            elif lo > hi:
                errors.append(f"{scene_id}: ovi_range lo > hi")
            else:
                scene_ranges.append((lo, hi, scene_id))
                for ovi in range(lo, hi + 1):
                    all_covered_ovis.add(ovi)
        else:
            errors.append(f"{scene_id}: invalid ovi_range")

        # turn ovi inside its range
        turn_ovi = turn.get("ovi") if isinstance(turn, dict) else None
        if isinstance(turn_ovi, int) and isinstance(ovi_range, list) and len(ovi_range) == 2:
            lo, hi = ovi_range[0], ovi_range[1]
            if not (lo <= turn_ovi <= hi):
                errors.append(f"{scene_id}: turn ovi outside range")

        # line ids exist in script_line_ids, none used twice, in script order within scene
        if isinstance(line_ids, list):
            prev_idx = -1
            for line_id in line_ids:
                if line_id not in script_line_ids:
                    errors.append(f"{line_id}: line is not in the script")
                if line_id in seen_line_ids:
                    errors.append(f"{line_id}: line used in multiple scenes")
                seen_line_ids.add(line_id)
                # check script order within scene
                try:
                    idx = list(script_line_ids).index(line_id) if line_id in script_line_ids else -1
                except ValueError:
                    idx = -1
                if idx != -1 and idx <= prev_idx:
                    errors.append(f"{scene_id}: line_ids not in script order")
                prev_idx = idx

        # discourse scene has teaching_treatment other than none
        if section_kind == "discourse":
            if teaching_treatment in (None, "none"):
                errors.append(f"{scene_id}: discourse scene missing teaching_treatment")
        elif section_kind == "story":
            if teaching_treatment is not None and teaching_treatment != "none":
                errors.append(f"{scene_id}: story scene must not have teaching_treatment")

    # ranges non-overlapping and ordered
    scene_ranges.sort(key=lambda x: x[0])
    for i in range(len(scene_ranges) - 1):
        lo1, hi1, id1 = scene_ranges[i]
        lo2, hi2, id2 = scene_ranges[i + 1]
        if hi1 >= lo2:
            errors.append(f"{id1}: ovi_range overlaps with {id2}")

    # every chapter ovi not unfilmed is inside a scene range
    for ovi in chapter_ovis:
        if ovi in unfilmed_ovis:
            continue
        if ovi not in all_covered_ovis:
            errors.append(f"ovi {ovi}: not covered by any scene")

    # unfilmed ovi inside a range is an error
    for ovi in unfilmed_ovis:
        if ovi in all_covered_ovis:
            # find which scene
            for lo, hi, sid in scene_ranges:
                if lo <= ovi <= hi:
                    errors.append(f"{sid}: ovi {ovi} is unfilmed but inside the range")
                    break

    # ovis outside the chapter are errors
    for ovi in all_covered_ovis:
        if ovi not in chapter_ovis:
            errors.append(f"ovi {ovi}: outside chapter ovis")

    # every core line is in a scene
    for line_id in core_line_ids:
        if line_id not in seen_line_ids:
            errors.append(f"{line_id}: core line not in any scene")

    return errors + notes
