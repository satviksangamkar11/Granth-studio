# FIX CALL: return BOTH files in full: `scripts/pipeline/stage1/scenes.py` and `tests/test_stage1_scenes.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
........................................................................ [ 93%]
.....                                                                    [100%]
77 passed in 0.10s

```

## SPEC
# UNIT SPEC: Stage 1 document `scenes` (schema `stage1_scenes`)
This is ONE unit of the Stage 1 contract (the master spec `stage1_v2.md` was split because one big spec gave unreliable tests). Keep the unit small and exact.
Module: `scripts/pipeline/stage1/scenes.py`. Tests: `tests/test_stage1_scenes.py`. Style: `from __future__ import annotations`, standard library plus `jsonschema`; no print, no network, nothing at import time; tests use only the BASE data below and `tmp_path`; the test file loads the module by path with importlib (`ROOT = Path(__file__).resolve().parents[1]`, `ROOT / "scripts" / "pipeline" / "stage1" / "scenes.py"`).

## Module API (exactly this)
- `SCHEMA`: dict, JSON Schema draft 2020-12 for the document, `additionalProperties: false` on EVERY object (nested too), `$schema` = "https://json-schema.org/draft/2020-12/schema", `title` = "stage1_scenes".
- `schema_errors(doc) -> list[str]`: one message per jsonschema error, formatted "scenes <path>: <message>" (path joined by "/", "doc" when empty).
- `validate(adhyay, doc, docs, ctx) -> list[str]`: SEMANTIC checks only (the schema has already passed; it must still never raise on odd data). `docs` is a dict of ALL nine documents (key names: story_map, coverage, scenes, shots, briefs, looks, voices, sounds, questions; a missing one counts as empty), `ctx` the context dict (keys: script_line_ids list, core_line_ids set, chapter_ovis set, unfilmed_ovis set, preset_ids set, sound_ids set, saved_voices dict voice_key->voice_id, speaking_characters set, known_states dict entity_id->set of state ids). Lists in ctx may arrive as lists or sets: convert with set(). Notes (messages that start with "note: ") come AFTER error messages. Include the adhyay check first: "scenes adhyay <n> does not match <adhyay>".

## Ids and common types
scene_id `^S[0-9]{1,2}$`; shot_id `^S[0-9]{1,2}-[0-9]{1,2}$`; line_id `^S[0-9]{1,2}-L[0-9]{1,3}$`; image id (Stage 1 brief) `^s[0-9]{1,2}_[a-z][a-z0-9_]{0,40}$`; ovi = integer >= 1; adhyay = integer 1..21; text = string 1..400 chars; preset id = string matching `^[0-9]{2}_[a-z0-9_]+$`; sound id `^(bed|fx)_[a-z0-9_]+$`.

## The document shape (from the master spec)
3. `stage1_scenes`: `scenes`: array of {scene_id, section_kind: story|discourse, ovi_range [lo,hi], goal, turn {ovi, text}, line_ids [line_id...], teaching_treatment: none|narration_over_typography|contemplative_hold|symbol_from_text (REQUIRED when section_kind is discourse; must be absent or "none" for story)}.

## Semantic rules of this unit (master spec step 5)
5. scenes: scene ids unique; ranges ordered lo <= hi and non-overlapping; every chapter ovi not unfilmed is inside a scene range; an unfilmed ovi inside a range is an error ("<scene>: ovi <n> is unfilmed but inside the range"); ovis outside the chapter are errors; turn ovi inside its range; line ids exist in `script_line_ids`, none used twice, in script order within a scene, and every core line is in a scene; a discourse scene has a teaching_treatment other than none.

Messages: tests assert only the quoted keywords/phrases of the rules plus the item id; for rules without a quoted phrase the message is `<item id>: <condition in plain words>`.

## BASE data (valid, note-free; the baseline for EVERY test; `validate(1, BASE_DOCS["scenes"], BASE_DOCS, CTX)` must return [] and `schema_errors` must return [])
File `docs/pilot/nemotron_specs/stage1_base.json` has the keys "docs" (the nine documents) and "ctx". The test file must embed its own copy of what it needs as Python literals (copy the values below exactly):
```json
{
 "docs": {
  "scenes": {
   "adhyay": 1,
   "scenes": [
    {
     "scene_id": "S1",
     "section_kind": "story",
     "ovi_range": [
      1,
      5
     ],
     "goal": "arrival",
     "turn": {
      "ovi": 3,
      "text": "he sits"
     },
     "line_ids": [
      "S1-L1",
      "S1-L2"
     ]
    },
    {
     "scene_id": "S2",
     "section_kind": "discourse",
     "ovi_range": [
      6,
      9
     ],
     "goal": "teaching",
     "turn": {
      "ovi": 7,
      "text": "the saying"
     },
     "line_ids": [
      "S2-L1"
     ],
     "teaching_treatment": "narration_over_typography"
    }
   ]
  }
 },
 "ctx": {
  "script_line_ids": [
   "S1-L1",
   "S1-L2",
   "S2-L1"
  ],
  "core_line_ids": [
   "S1-L1",
   "S2-L1"
  ],
  "chapter_ovis": [
   1,
   2,
   3,
   4,
   5,
   6,
   7,
   8,
   9
  ],
  "unfilmed_ovis": [],
  "preset_ids": [
   "01_establishing_shot",
   "03_slow_cinematic_push"
  ],
  "sound_ids": [
   "bed_roadside_quiet",
   "fx_door_wood_creak"
  ],
  "saved_voices": {
   "narrator": "CXkeo30p0Sk4Lr0TAzeo",
   "gajanan": "8fqGzH80bdkm2UseeV9f"
  },
  "speaking_characters": [
   "narrator",
   "gajanan_maharaj"
  ],
  "known_states": {
   "gajanan_maharaj": [
    "adult_youth_v1"
   ]
  }
 }
}
```
(Documents not shown for this unit are not needed; pass them as `{}` where absent.)

## Clarifications added after the Codex review of the first tests (binding for tests and code)
- API: `make_schemas.py` exposes `write_all(out_dir, overwrite=False) -> list[Path]` (writes the 13 schemas: nine Stage 1 + the four legacy ones unchanged; raises FileExistsError if a target exists and overwrite is False) and `main()` (CLI `--out`, `--overwrite`) calling it. Legacy schemas keep their current definitions exactly (beats: top-level keys adhyay + scenes; image_catalog: adhyay + images; animation_scene: adhyay + scene_id + shots; shot_plan: adhyay, scene_id, fingerprints, shots, approved_by, approved_date). Schemas use dialect `https://json-schema.org/draft/2020-12/schema`.
- Validator tests generate the schemas into tmp_path and pass that folder to the validator through a keyword argument `schema_dir=None` (default: the repository `schemas/` folder next to `scripts`).
- The baseline valid fixture must be NOTE-FREE (no PROPOSE_OMISSION) and `validate_stage1` must return `[]` for it. A PROPOSE_OMISSION adds exactly one message that STARTS with `note: ` (notes come after all error messages; an omission is not an error).
- Messages: tests assert only the quoted keywords/phrases of this spec plus the item id; for rules without a quoted phrase the message is `<item id>: <condition in plain words>` and tests only check that the item id appears.
- story_map `events` may be an empty array (zero-story chapter): valid. A zero-story chapter = every ovi typed TEACHING/PHILOSOPHY/INVOCATION/..., one `discourse` scene, empty events.
- Context defaults in test helpers: use `None` as the default and replace only when the argument is None, so intentionally empty sets/dicts survive; tests must include empty-context cases that produce specific missing-reference messages (e.g. "<line>: line is not in the script").
- Tests live at their final location `tests/` (so `ROOT = Path(__file__).resolve().parents[1]` is correct there); the review staging copy is relocated before running.
- Keyword rule for sound: a non-NEED_NEW cue carrying `sound_prompt` is a SCHEMA error (the schema forbids it).



## CURRENT MODULE scripts/pipeline/stage1/scenes.py
```python
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

        # scene ids unique - guard against unhashable
        if not isinstance(scene_id, str):
            errors.append(f"<scene_{i}>: scene_id must be a string")
        elif scene_id in seen_scene_ids:
            errors.append(f"{scene_id}: duplicate scene id")
        else:
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

        # turn ovi inside its range - validate bounds are ints first
        turn_ovi = turn.get("ovi") if isinstance(turn, dict) else None
        if isinstance(turn_ovi, int) and isinstance(ovi_range, list) and len(ovi_range) == 2:
            lo, hi = ovi_range[0], ovi_range[1]
            if isinstance(lo, int) and isinstance(hi, int):
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


def validate(adhyay: int, doc: dict[str, Any], docs: dict[str, Any], ctx: dict[str, Any]) -> list[str]:
    return _validate_semantic(adhyay, doc, docs, ctx)

```

## CURRENT TESTS tests/test_stage1_scenes.py
```python
from __future__ import annotations
import copy
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "pipeline" / "stage1"))
import scenes as M  # type: ignore

# ---------- Robust helpers ----------
def get_parent(doc: dict, path: list):
    cur = doc
    for p in path[:-1]:
        cur = cur[p] if isinstance(cur, dict) else cur[int(p)]
    return cur, path[-1]

def set_at(base: dict, path: list, value) -> dict:
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    if isinstance(parent, list):
        parent[int(key)] = value
    else:
        parent[key] = value
    assert doc != base, "mutation had no effect"
    return doc

def delete_at(base: dict, path: list) -> dict:
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    if isinstance(parent, list):
        del parent[int(key)]
    else:
        del parent[key]
    assert doc != base, "mutation had no effect"
    return doc

def append_at(base: dict, path: list, value) -> dict:
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    assert isinstance(parent, dict), "append target must be dict"
    lst = parent.setdefault(key, [])
    lst.append(value)
    assert doc != base, "mutation had no effect"
    return doc

# ---------- Base data ----------
def base_docs() -> dict:
    return {
        "scenes": {
            "adhyay": 1,
            "scenes": [
                {
                    "scene_id": "S1",
                    "section_kind": "story",
                    "ovi_range": [1, 5],
                    "goal": "arrival",
                    "turn": {"ovi": 3, "text": "he sits"},
                    "line_ids": ["S1-L1", "S1-L2"],
                },
                {
                    "scene_id": "S2",
                    "section_kind": "discourse",
                    "ovi_range": [6, 9],
                    "goal": "teaching",
                    "turn": {"ovi": 7, "text": "the saying"},
                    "line_ids": ["S2-L1"],
                    "teaching_treatment": "narration_over_typography",
                },
            ],
        },
        "story_map": {}, "coverage": {}, "shots": {}, "briefs": {},
        "looks": {}, "voices": {}, "sounds": {}, "questions": {},
    }

def base_ctx() -> dict:
    return {
        "script_line_ids": ["S1-L1", "S1-L2", "S2-L1"],
        "core_line_ids": {"S1-L1", "S2-L1"},
        "chapter_ovis": {1,2,3,4,5,6,7,8,9},
        "unfilmed_ovis": set(),
        "preset_ids": {"01_establishing_shot", "03_slow_cinematic_push"},
        "sound_ids": {"bed_roadside_quiet", "fx_door_wood_creak"},
        "saved_voices": {"narrator": "CXkeo30p0Sk4Lr0TAzeo", "gajanan": "8fqGzH80bdkm2UseeV9f"},
        "speaking_characters": {"narrator", "gajanan_maharaj"},
        "known_states": {"gajanan_maharaj": {"adult_youth_v1"}},
    }

# ---------- Schema tests ----------
# Required field deletions (root)
@pytest.mark.parametrize("path", [
    ["adhyay"], ["scenes"],
])
def test_schema_required_root(path):
    doc = delete_at(base_docs()["scenes"], path)
    errs = M.schema_errors(doc)
    assert any(path[-1] in e for e in errs)

# Required field deletions (scene object)
@pytest.mark.parametrize("path", [
    ["scenes",0,"scene_id"], ["scenes",0,"section_kind"], ["scenes",0,"ovi_range"],
    ["scenes",0,"goal"], ["scenes",0,"turn"], ["scenes",0,"line_ids"],
])
def test_schema_required_scene(path):
    doc = delete_at(base_docs()["scenes"], path)
    errs = M.schema_errors(doc)
    assert any(path[-1] in e for e in errs)

# Required field deletions (turn object)
@pytest.mark.parametrize("path", [
    ["scenes",0,"turn","ovi"], ["scenes",0,"turn","text"],
])
def test_schema_required_turn(path):
    doc = delete_at(base_docs()["scenes"], path)
    errs = M.schema_errors(doc)
    assert any(path[-1] in e for e in errs)

# Extra keys (root and nested)
@pytest.mark.parametrize("path", [
    [], ["scenes",0], ["scenes",0,"turn"],
])
def test_schema_extra_keys(path):
    doc = copy.deepcopy(base_docs()["scenes"])
    target, _ = get_parent(doc, path + ["__extra__"])
    target["__extra__"] = 1
    errs = M.schema_errors(doc)
    assert any("__extra__" in e for e in errs)

# Enum invalid values
@pytest.mark.parametrize("path,value", [
    (["scenes",0,"section_kind"], "bad"),
    (["scenes",1,"teaching_treatment"], "bad"),
])
def test_schema_enum(path, value):
    doc = set_at(base_docs()["scenes"], path, value)
    errs = M.schema_errors(doc)
    assert any(path[-1] in e for e in errs)

# Type/format/constraint errors
@pytest.mark.parametrize("path,value,keyword", [
    (["adhyay"], 0, "adhyay"), (["adhyay"], 22, "adhyay"), (["adhyay"], "1", "adhyay"),
    (["scenes"], "x", "scenes"), (["scenes",0], "x", "scenes"),
    (["scenes",0,"scene_id"], "X1", "scene_id"), (["scenes",0,"scene_id"], "S100", "scene_id"),
    (["scenes",0,"ovi_range"], [1], "ovi_range"), (["scenes",0,"ovi_range"], [1,5,9], "ovi_range"),
    (["scenes",0,"ovi_range"], ["1",5], "ovi_range"),
    (["scenes",0,"goal"], "", "goal"), (["scenes",0,"goal"], 123, "goal"),
    (["scenes",0,"turn"], "x", "turn"),
    (["scenes",0,"turn","ovi"], 0, "ovi"), (["scenes",0,"turn","ovi"], "3", "ovi"),
    (["scenes",0,"turn","text"], "", "text"), (["scenes",0,"turn","text"], 123, "text"),
    (["scenes",0,"turn","text"], "x"*401, "text"),
    (["scenes",0,"line_ids"], "x", "line_ids"),
    (["scenes",0,"line_ids",0], 123, "line_ids"), (["scenes",0,"line_ids",0], "bad-id", "line_ids"),
    # discourse requires teaching_treatment (schema required)
    (["scenes",1,"teaching_treatment"], None, "teaching_treatment"),
])
def test_schema_errors(path, value, keyword):
    doc = set_at(base_docs()["scenes"], path, value) if value is not None else delete_at(base_docs()["scenes"], path)
    errs = M.schema_errors(doc)
    assert any(keyword in e for e in errs), f"missing {keyword} in {errs}"

# Story scene with non-"none" teaching_treatment rejected by schema
def test_schema_story_scene_forbidden_treatment():
    doc = set_at(base_docs()["scenes"], ["scenes",0,"teaching_treatment"], "narration_over_typography")
    errs = M.schema_errors(doc)
    assert any("teaching_treatment" in e for e in errs)

# Story scene with "none" teaching_treatment accepted by schema
def test_schema_story_scene_none_treatment_allowed():
    doc = set_at(base_docs()["scenes"], ["scenes",0,"teaching_treatment"], "none")
    errs = M.schema_errors(doc)
    assert errs == []

# Discourse scene with teaching_treatment = "none" rejected by schema (not just semantic)
def test_schema_discourse_scene_none_treatment_rejected():
    doc = set_at(base_docs()["scenes"], ["scenes",1,"teaching_treatment"], "none")
    errs = M.schema_errors(doc)
    assert any("teaching_treatment" in e for e in errs)

# Discourse scene with each valid teaching_treatment accepted by schema
@pytest.mark.parametrize("treatment", [
    "narration_over_typography",
    "contemplative_hold",
    "symbol_from_text",
])
def test_schema_discourse_scene_valid_treatments(treatment):
    base = base_docs()["scenes"]
    # Ensure we actually mutate: if base already has this treatment, start from a different valid one
    current = base["scenes"][1].get("teaching_treatment")
    if current == treatment:
        other = next(t for t in ["narration_over_typography", "contemplative_hold", "symbol_from_text"] if t != treatment)
        base = set_at(base, ["scenes",1,"teaching_treatment"], other)
    doc = set_at(base, ["scenes",1,"teaching_treatment"], treatment)
    errs = M.schema_errors(doc)
    assert errs == [], f"unexpected error for {treatment}: {errs}"

# ovi_range item minimum 1 (schema constraint)
def test_schema_ovi_range_minimum():
    doc = set_at(base_docs()["scenes"], ["scenes",0,"ovi_range"], [0, 5])
    errs = M.schema_errors(doc)
    assert any("ovi_range" in e for e in errs)

# ---------- Semantic tests ----------
# Each row changes ONE thing; contexts stay complete unless row is about that context
@pytest.mark.parametrize("mutate_fn,keyword,ctx_overrides", [
    # duplicate scene_id (append real duplicate with non-overlapping range and no lines)
    (lambda d: append_at(d, ["scenes"], {
        "scene_id": "S1",
        "section_kind": "story",
        "ovi_range": [10, 12],
        "goal": "dup",
        "turn": {"ovi": 11, "text": "dup"},
        "line_ids": [],
    }), "S1", {}),
    # ovi_range lo > hi (isolated: remove turn so only range check fires)
    (lambda d: set_at(delete_at(d, ["scenes",0,"turn"]), ["scenes",0,"ovi_range"], [5,1]), "S1", {}),
    # overlapping ranges
    (lambda d: set_at(d, ["scenes",1,"ovi_range"], [4,9]), "S2", {}),
    # chapter ovi not covered (ovi 9 missing)
    (lambda d: set_at(d, ["scenes",1,"ovi_range"], [6,8]), "9", {}),
    # unfilmed ovi inside range
    (lambda d: d, "S1", {"unfilmed_ovis": {3}}),
    # ovi outside chapter (ovi 10)
    (lambda d: set_at(d, ["scenes",1,"ovi_range"], [6,10]), "10", {}),
    # turn ovi outside range
    (lambda d: set_at(d, ["scenes",0,"turn","ovi"], 6), "S1", {}),
    # line_id not in script
    (lambda d: set_at(d, ["scenes",0,"line_ids",0], "S9-L1"), "S9-L1", {}),
    # duplicate line_id across scenes (append second entry)
    (lambda d: append_at(d, ["scenes",1,"line_ids"], "S1-L1"), "S1-L1", {}),
    # line_ids not in script order within scene
    (lambda d: set_at(d, ["scenes",0,"line_ids"], ["S1-L2","S1-L1"]), "S1", {}),
    # core line not in any scene (remove S1-L1 from S1)
    (lambda d: set_at(d, ["scenes",0,"line_ids"], ["S1-L2"]), "S1-L1", {}),
    # discourse scene teaching_treatment none (semantic: must not be none)
    (lambda d: set_at(d, ["scenes",1,"teaching_treatment"], "none"), "S2", {}),
    # story scene with teaching_treatment (must be absent or none)
    (lambda d: set_at(d, ["scenes",0,"teaching_treatment"], "narration_over_typography"), "S1", {}),
    # adhyay mismatch
    (lambda d: set_at(d, ["adhyay"], 2), "adhyay", {}),
])
def test_semantic_errors(mutate_fn, keyword, ctx_overrides):
    docs = base_docs()
    docs["scenes"] = mutate_fn(docs["scenes"])
    ctx = base_ctx()
    ctx.update(ctx_overrides)
    errs = M.validate(1, docs["scenes"], docs, ctx)
    assert any(keyword in e for e in errs), f"missing {keyword} in {errs}"

# ---------- Regression tests for crash cases ----------
def test_validate_odd_data_no_raise():
    """validate() must never raise on any JSON-shaped input."""
    # non-dict doc
    errs = M.validate(1, None, {}, {})
    assert isinstance(errs, list) and not any("malformed structure" in e for e in errs)
    errs = M.validate(1, "not a dict", {}, {})
    assert isinstance(errs, list) and not any("malformed structure" in e for e in errs)
    errs = M.validate(1, [], {}, {})
    assert isinstance(errs, list) and not any("malformed structure" in e for e in errs)
    # scenes not a list
    errs = M.validate(1, {"adhyay": 1, "scenes": "not a list"}, {}, {})
    assert isinstance(errs, list) and not any("malformed structure" in e for e in errs)
    # scene not a dict
    errs = M.validate(1, {"adhyay": 1, "scenes": ["not a dict"]}, {}, {})
    assert isinstance(errs, list) and not any("malformed structure" in e for e in errs)
    # unhashable scene_id
    errs = M.validate(1, {"adhyay": 1, "scenes": [{"scene_id": ["S1"], "section_kind": "story", "ovi_range": [1,5], "goal": "g", "turn": {"ovi": 1, "text": "t"}, "line_ids": []}]}, {}, {})
    assert isinstance(errs, list) and not any("malformed structure" in e for e in errs)
    # unhashable line_id
    errs = M.validate(1, {"adhyay": 1, "scenes": [{"scene_id": "S1", "section_kind": "story", "ovi_range": [1,5], "goal": "g", "turn": {"ovi": 1, "text": "t"}, "line_ids": [["S1-L1"]]}]}, {}, {})
    assert isinstance(errs, list) and not any("malformed structure" in e for e in errs)
    # non-int ovi_range bounds
    errs = M.validate(1, {"adhyay": 1, "scenes": [{"scene_id": "S1", "section_kind": "story", "ovi_range": ["a", 5], "goal": "g", "turn": {"ovi": 1, "text": "t"}, "line_ids": []}]}, {}, {})
    assert isinstance(errs, list) and not any("malformed structure" in e for e in errs)
    # turn ovi with non-int bounds
    errs = M.validate(1, {"adhyay": 1, "scenes": [{"scene_id": "S1", "section_kind": "story", "ovi_range": ["1", 5], "goal": "g", "turn": {"ovi": 3, "text": "t"}, "line_ids": []}]}, {}, {})
    assert isinstance(errs, list) and not any("malformed structure" in e for e in errs)
    # unknown line id doesn't break order check
    ctx = base_ctx()
    docs = base_docs()
    docs["scenes"] = set_at(docs["scenes"], ["scenes",0,"line_ids"], ["S1-L2", "S9-L9", "S1-L1"])
    errs = M.validate(1, docs["scenes"], docs, ctx)
    # Should report both unknown line and order error
    assert any("S9-L9" in e for e in errs)
    # order error should be separate from unknown line error
    assert any("S1" in e and "S9-L9" not in e for e in errs)

def test_schema_errors_odd_data_no_raise():
    """schema_errors() must never raise on any JSON-shaped input."""
    assert isinstance(M.schema_errors(None), list)
    assert isinstance(M.schema_errors("not a dict"), list)
    assert isinstance(M.schema_errors([]), list)
    assert isinstance(M.schema_errors({"adhyay": 1, "scenes": "not a list"}), list)

# ---------- Context robustness tests ----------
# For each ctx key used by this unit, test that None, str, int, and [[]] don't raise
# and don't produce 'malformed structure' messages.
CTX_KEYS_USED = ["script_line_ids", "core_line_ids", "chapter_ovis", "unfilmed_ovis"]
BAD_VALUES = [None, "not a list", 42, [[]]]

@pytest.mark.parametrize("key", CTX_KEYS_USED)
@pytest.mark.parametrize("bad_val", BAD_VALUES)
def test_validate_ctx_robustness(key, bad_val):
    """validate() handles non-collection ctx values gracefully."""
    docs = base_docs()
    ctx = base_ctx()
    ctx[key] = bad_val
    errs = M.validate(1, docs["scenes"], docs, ctx)
    assert isinstance(errs, list)
    assert not any("malformed structure" in e for e in errs)

# ---------- Positive ----------
def test_valid():
    docs = base_docs()
    ctx = base_ctx()
    assert M.schema_errors(docs["scenes"]) == []
    assert M.validate(1, docs["scenes"], docs, ctx) == []

```

## FINAL REVIEW BLOCKING FINDINGS (Haiku verified them). Keep every existing test passing and every assertion 'not any("malformed structure" in e ...)'. Return BOTH complete FILE blocks.
1. Add the same catch-all wrapper the sibling units have: rename the current semantic body to a private helper and make validate(adhyay, doc, docs, ctx) call it inside try/except (TypeError, AttributeError, KeyError, ValueError, IndexError) returning ["scenes: malformed structure"]; ALSO make the real code robust so odd input is handled before the guard: ctx itself may be None or a non-dict (treat as an empty dict), docs may be a non-dict (empty dict). Add regression tests: ctx=None, ctx='x', docs=None each give a list and no exception.
2. NO ENUMERATION OF HUGE RANGES: scenes.py loops 'for ovi in range(lo, hi + 1)' for each scene's ovi_range, so ovi_range [1, 10**12] never finishes. Do not enumerate the declared range. Instead compute coverage by iterating the CHAPTER ovis (ctx chapter ovis, a bounded list) and testing lo <= ovi <= hi, and report a range that extends outside the chapter as ONE message per scene (keep the scene id in it; keep the existing 'ovi N: outside chapter ovis' style for the ovis inside the range that the existing tests expect, but bound that enumeration by the chapter size, e.g. only ovis between the chapter minimum and maximum, plus one message when lo or hi lies beyond them). Existing tests must keep passing. Add a regression test with ovi_range [1, 10**12] (and [-10**12, 10**12]) that returns a list quickly (the test itself must not hang: use the module directly, no timeout needed if you do not enumerate).
### Haiku final
# Haiku final review: Stage 1 unit modules (read-only)

Scope: `scripts/pipeline/stage1/{story_map,coverage,scenes,shots,briefs,looks,voices,sounds,questions}.py`, tests `tests/test_stage1_*.py`, specs `docs/pilot/nemotron_specs/unit_<unit>.md`, `stage1_base.json`, `docs/pilot/STAGE1_RULES.md`.

## Evidence
- `uv run pytest -q --tb=short tests/test_stage1_*.py`: 463 passed (per-unit counts match `docs/pilot/TEST_RUN_STAGE1.txt`).
- In-memory fuzz (no files written): about 430,000 calls mutating the nine base documents and the ctx dict, with random JSON-shaped values and special numbers (NaN, Infinity, huge ints, bools, zero, negative). Raises were found only in coverage and scenes, and only in the two cases below.
- Class 1 (spec rules): every semantic rule in the nine specs was checked against its module. No rule is missing or wrong.
- Class 3 (rules without a failing test): every semantic rule has at least one test with a matching assertion. Some assertions are weak (see notes), but none is absent.
- The `malformed structure` sentinel is treated as the project design rule and is not reported.

## Per-unit BLOCKING defects

### story_map
none

### coverage
1. `scripts/pipeline/stage1/coverage.py:69-141` (`validate`): no catch-all, unlike story_map, shots, briefs, sounds and voices. It raises on JSON-shaped ctx values (CLASS 2).
   - Verified: `validate(1, base coverage, base docs, None)` raises `AttributeError: 'NoneType' object has no attribute 'get'` (line 84).
   - Verified: ctx `chapter_ovis=[[1]]` raises `TypeError: unhashable type: 'list'` (line 85).
   - Exact fix: rename the body to `_validate_impl` and add `validate(adhyay, doc, docs, ctx)` that does `try: return _validate_impl(...)` and on `(TypeError, AttributeError, KeyError, ValueError, IndexError)` returns `["coverage: malformed structure"]`, as the sibling units do. Add tests for `ctx=None` and `chapter_ovis=[[1]]` asserting no exception.

### scenes
1. `scripts/pipeline/stage1/scenes.py:228-229` (`validate`): no catch-all. It raises on JSON-shaped ctx values (CLASS 2).
   - Verified: ctx `None` raises `AttributeError` (line 109). ctx `script_line_ids=5` raises `TypeError: 'int' object is not iterable` (line 109).
   - Exact fix: same wrapper as coverage item 1, returning `["scenes: malformed structure"]`, plus no-raise tests for these two ctx values.
2. `scripts/pipeline/stage1/scenes.py:148-149` (`for ovi in range(lo, hi + 1): all_covered_ovis.add(ovi)`): the schema sets no maximum on `ovi_range` values, so a document can force enumeration of any span (CLASS 2: the call does not finish or fails with MemoryError).
   - Verified: `[1, 2000000]` takes 0.36 s. `[1, 10**7]` takes 1.7 s and returns 9,999,992 messages. A span of `10**30` did not finish; the probe was stopped after it hung (not a completed run, so it is stated as unverified to completion).
   - Exact fix: do not enumerate the range. Either reject any span wider than the chapter (for example `if hi - lo > 1000: errors.append(f"{sid}: ovi_range too wide"); continue`), or compute coverage by checking only each chapter ovi against the ranges, and emit one message per out-of-chapter range instead of one per ovi. The second option changes the "ovi 10" message, so update `tests/test_stage1_scenes.py` (the `ovi outside chapter` row, around line 232) with it.

### shots
none

### briefs
none

### looks
none

### voices
none

### sounds
none

### questions
none

## Non-blocking notes
- `sounds.py:64`: ctx `sound_ids` is accepted only as a list or set. A tuple or frozenset becomes an empty set and produces false "not in sound_ids" errors. `looks.py` `_as_set` handles these types. Low risk, since ctx comes from JSON.
- `briefs.py:171-174`: a non-object entry in `people` makes the loop raise, and the catch-all returns only the sentinel. The schema already rejects such entries, so this is not a defect in the validate path, but the item is not reported by name.
- Schema bounds without a test: `scenes` `ovi_range` has no maximum (root of scenes item 2); `shots` `ovi_ids` has no maximum. Enum values are present and tested.
- Weak test assertions (rule tests exist): `test_scenes` "unfilmed inside range" and "ovi not covered" match keywords `S1` and `9`, which appear in many messages. `test_briefs` `test_validate_malformed_structure_returns_error` only asserts `len(errs) >= 1`.
- `looks.py` and `questions.py` have no catch-all, but the fuzz found no raises in either.
- `sounds.py`: the rule "a non-NEED_NEW cue must not carry sound_prompt" is enforced by the schema only, as the spec says.

Two units have CLASS 2 blocking defects (coverage 1, scenes 2). Fix those and add the no-raise tests, then re-run the stage1 suites.

## Verdict: FIX FIRST
