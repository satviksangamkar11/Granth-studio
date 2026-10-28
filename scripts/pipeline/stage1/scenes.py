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
                "allOf": [
                    {
                        "if": {"properties": {"section_kind": {"const": "discourse"}}},
                        "then": {
                            "required": ["teaching_treatment"],
                            "properties": {
                                "teaching_treatment": {"not": {"const": "none"}}
                            }
                        }
                    },
                    {
                        "if": {"properties": {"section_kind": {"const": "story"}}},
                        "then": {
                            "properties": {
                                "teaching_treatment": {"const": "none"}
                            }
                        }
                    },
                ],
            },
        },
    },
}

_validator = Draft202012Validator(SCHEMA)


def _is_int_not_bool(x: Any) -> bool:
    """Check if x is an int but not a bool (since bool is subclass of int in Python)."""
    return isinstance(x, int) and not isinstance(x, bool)


def schema_errors(doc: Any) -> list[str]:
    errors = []
    if not isinstance(doc, dict):
        errors.append("scenes doc: document must be an object")
        return errors
    for err in _validator.iter_errors(doc):
        path = "/".join(str(p) for p in err.path) if err.path else "doc"
        errors.append(f"scenes {path}: {err.message}")
    return errors


def _as_usable_list(value: Any) -> list:
    """Convert a ctx value to a list if it's a usable collection type, else empty list."""
    if isinstance(value, (list, tuple, set, frozenset, range)):
        return list(value)
    return []


def _as_usable_set(value: Any) -> set:
    """Convert a ctx value to a set of hashable items if it's a usable collection type, else empty set."""
    if isinstance(value, (list, tuple, set, frozenset, range)):
        result = set()
        for item in value:
            try:
                hash(item)
                result.add(item)
            except TypeError:
                pass
        return result
    return set()


def _validate_semantic(adhyay: int, doc: dict[str, Any], docs: dict[str, Any], ctx: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    notes: list[str] = []

    # Guard: doc must be a dict
    if not isinstance(doc, dict):
        errors.append("scenes doc: document must be an object")
        return errors + notes

    # adhyay check
    doc_adhyay = doc.get("adhyay")
    if doc_adhyay != adhyay:
        errors.append(f"scenes adhyay {doc_adhyay} does not match {adhyay}")

    scenes = doc.get("scenes", [])
    if not isinstance(scenes, list):
        return errors + notes

    # Convert ctx lists/sets to sets for membership, keep script_line_ids as list for order
    script_line_ids_list = _as_usable_list(ctx.get("script_line_ids"))
    script_line_ids_set = _as_usable_set(ctx.get("script_line_ids"))
    core_line_ids = _as_usable_set(ctx.get("core_line_ids"))
    chapter_ovis = _as_usable_set(ctx.get("chapter_ovis"))
    unfilmed_ovis = _as_usable_set(ctx.get("unfilmed_ovis"))

    # Filter chapter_ovis to only ints (not bool)
    chapter_ovis_int = {ovi for ovi in chapter_ovis if _is_int_not_bool(ovi)}
    chapter_ovis_sorted = sorted(chapter_ovis_int)

    # Filter unfilmed_ovis to only ints (not bool)
    unfilmed_ovis_int = {ovi for ovi in unfilmed_ovis if _is_int_not_bool(ovi)}

    # Track seen items
    seen_scene_ids = set()
    seen_line_ids = set()
    scene_ranges = []  # list of (lo, hi, scene_id)

    for i, scene in enumerate(scenes):
        if not isinstance(scene, dict):
            continue
        scene_id = scene.get("scene_id", f"<scene_{i}>")
        section_kind = scene.get("section_kind")
        ovi_range = scene.get("ovi_range", [])
        turn = scene.get("turn", {})
        line_ids = scene.get("line_ids", [])
        teaching_treatment = scene.get("teaching_treatment")

        # scene ids unique - guard against unhashable
        if not isinstance(scene_id, str):
            errors.append(f"<scene_{i}>: scene_id must be a string")
        elif scene_id in seen_scene_ids:
            errors.append(f"{scene_id}: duplicate scene id")
        else:
            seen_scene_ids.add(scene_id)

        # ovi_range lo <= hi (validate bounds are ints not bool)
        if isinstance(ovi_range, list) and len(ovi_range) == 2:
            lo, hi = ovi_range[0], ovi_range[1]
            if not (_is_int_not_bool(lo) and _is_int_not_bool(hi)):
                errors.append(f"{scene_id}: ovi_range must be integers")
            elif lo > hi:
                errors.append(f"{scene_id}: ovi_range lo > hi")
            else:
                scene_ranges.append((lo, hi, scene_id))
        else:
            errors.append(f"{scene_id}: invalid ovi_range")

        # turn ovi inside its range - validate bounds are ints first
        turn_ovi = turn.get("ovi") if isinstance(turn, dict) else None
        if _is_int_not_bool(turn_ovi) and isinstance(ovi_range, list) and len(ovi_range) == 2:
            lo, hi = ovi_range[0], ovi_range[1]
            if _is_int_not_bool(lo) and _is_int_not_bool(hi):
                if not (lo <= turn_ovi <= hi):
                    errors.append(f"{scene_id}: turn ovi outside range")

        # line ids exist in script_line_ids, none used twice, in script order within scene
        if isinstance(line_ids, list):
            prev_idx = -1
            for line_id in line_ids:
                if not isinstance(line_id, str):
                    errors.append(f"{scene_id}: line_id must be a string")
                    continue
                if line_id not in script_line_ids_set:
                    errors.append(f"{line_id}: line is not in the script")
                if line_id in seen_line_ids:
                    errors.append(f"{line_id}: line used in multiple scenes")
                seen_line_ids.add(line_id)
                # check script order within scene - only update prev_idx for known lines
                try:
                    idx = script_line_ids_list.index(line_id)
                except ValueError:
                    idx = -1
                if idx != -1:
                    if idx <= prev_idx:
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

    # Build set of covered chapter ovis
    all_covered_ovis = set()
    for ovi in chapter_ovis_int:
        for lo, hi, sid in scene_ranges:
            if lo <= ovi <= hi:
                all_covered_ovis.add(ovi)
                break

    # every chapter ovi not unfilmed is inside a scene range
    for ovi in chapter_ovis_int:
        if ovi in unfilmed_ovis_int:
            continue
        if ovi not in all_covered_ovis:
            errors.append(f"ovi {ovi}: not covered by any scene")

    # unfilmed ovi inside a range is an error - check directly against scene ranges
    for ovi in unfilmed_ovis_int:
        for lo, hi, sid in scene_ranges:
            if lo <= ovi <= hi:
                errors.append(f"{sid}: ovi {ovi} is unfilmed but inside the range")
                break

    # Check for ovis inside scene ranges that are not chapter ovis (gaps and outside)
    # Use sorted chapter ovis to find gaps without enumerating large ranges
    GAP_REPORT_LIMIT = 1000
    total_gap_messages = 0
    gap_limit_reached = False
    summary_emitted = False

    if chapter_ovis_sorted:
        chapter_min = chapter_ovis_sorted[0]
        chapter_max = chapter_ovis_sorted[-1]
        
        for lo, hi, sid in scene_ranges:
            # Check below chapter minimum
            if lo < chapter_min:
                errors.append(f"{sid}: ovi_range extends below chapter ovis")
            
            # Check above chapter maximum
            if hi > chapter_max:
                errors.append(f"{sid}: ovi_range extends above chapter ovis")
            
            # Effective range clipped to chapter bounds
            eff_lo = max(lo, chapter_min)
            eff_hi = min(hi, chapter_max)
            
            if eff_lo <= eff_hi:
                # Chapter ovis that fall inside the effective range
                inside = [o for o in chapter_ovis_sorted if eff_lo <= o <= eff_hi]
                
                # Boundaries: eff_lo - 1, then inside ovis, then eff_hi + 1
                # Gaps are between consecutive boundaries where difference > 1
                boundaries = [eff_lo - 1] + inside + [eff_hi + 1]
                
                for a, b in zip(boundaries, boundaries[1:]):
                    if b - a > 1:
                        gap_start = a + 1
                        gap_end = b - 1
                        gap_size = gap_end - gap_start + 1
                        if not gap_limit_reached:
                            if total_gap_messages + gap_size <= GAP_REPORT_LIMIT:
                                for g in range(gap_start, gap_end + 1):
                                    errors.append(f"ovi {g}: outside chapter ovis")
                                total_gap_messages += gap_size
                            else:
                                # Emit remaining allowed per-ovi messages
                                remaining = GAP_REPORT_LIMIT - total_gap_messages
                                for g in range(gap_start, gap_start + remaining):
                                    errors.append(f"ovi {g}: outside chapter ovis")
                                total_gap_messages = GAP_REPORT_LIMIT
                                # Add summary message (only once total)
                                if not summary_emitted:
                                    errors.append(f"{sid}: more ovis outside chapter ovis (message limit reached)")
                                    summary_emitted = True
                                gap_limit_reached = True
                        else:
                            # Already at limit, add summary only once total
                            if not summary_emitted:
                                errors.append(f"{sid}: more ovis outside chapter ovis (message limit reached)")
                                summary_emitted = True
    else:
        # No chapter ovis - any range is outside
        for lo, hi, sid in scene_ranges:
            errors.append(f"{sid}: ovi_range outside chapter ovis")

    # every core line is in a scene
    for line_id in core_line_ids:
        if line_id not in seen_line_ids:
            errors.append(f"{line_id}: core line not in any scene")

    return errors + notes


def validate(adhyay: int, doc: dict[str, Any], docs: dict[str, Any], ctx: dict[str, Any]) -> list[str]:
    try:
        # Normalize inputs
        if not isinstance(ctx, dict):
            ctx = {}
        if not isinstance(docs, dict):
            docs = {}
        return _validate_semantic(adhyay, doc, docs, ctx)
    except (TypeError, AttributeError, KeyError, ValueError, IndexError):
        return ["scenes: malformed structure"]
