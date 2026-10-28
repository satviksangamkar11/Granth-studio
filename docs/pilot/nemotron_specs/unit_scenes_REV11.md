# FIX CALL: return BOTH files in full: `scripts/pipeline/stage1/scenes.py` and `tests/test_stage1_scenes.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
........................................................                 [100%]
56 passed in 0.08s

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


def _validate_semantic(adhyay: int, doc: dict[str, Any], docs: dict[str, Any], ctx: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    notes: list[str] = []

    # adhyay check
    doc_adhyay = doc.get("adhyay")
    if doc_adhyay != adhyay:
        errors.append(f"scenes adhyay {doc_adhyay} does not match {adhyay}")

    scenes = doc.get("scenes", [])
    if not isinstance(scenes, list):
        return errors + notes

    # Convert ctx lists/sets to sets for membership, keep script_line_ids as list for order
    script_line_ids_list = list(ctx.get("script_line_ids", []))
    script_line_ids_set = set(script_line_ids_list)
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
    try:
        return _validate_semantic(adhyay, doc, docs, ctx)
    except (TypeError, AttributeError, KeyError, ValueError, IndexError):
        return ["scenes: malformed structure"]

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

# ---------- Semantic tests ----------
# Each row changes ONE thing; contexts stay complete unless row is about that context
@pytest.mark.parametrize("mutate_fn,keyword,ctx_overrides", [
    # duplicate scene_id (append real duplicate)
    (lambda d: append_at(d, ["scenes"], copy.deepcopy(d["scenes"][0])), "S1", {}),
    # ovi_range lo > hi
    (lambda d: set_at(d, ["scenes",0,"ovi_range"], [5,1]), "S1", {}),
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
    assert isinstance(M.validate(1, None, {}, {}), list)
    assert isinstance(M.validate(1, "not a dict", {}, {}), list)
    assert isinstance(M.validate(1, [], {}, {}), list)
    # scenes not a list
    assert isinstance(M.validate(1, {"adhyay": 1, "scenes": "not a list"}, {}, {}), list)
    # scene not a dict
    assert isinstance(M.validate(1, {"adhyay": 1, "scenes": ["not a dict"]}, {}, {}), list)
    # unhashable scene_id
    assert isinstance(M.validate(1, {"adhyay": 1, "scenes": [{"scene_id": ["S1"], "section_kind": "story", "ovi_range": [1,5], "goal": "g", "turn": {"ovi": 1, "text": "t"}, "line_ids": []}]}, {}, {}), list)
    # unhashable line_id
    assert isinstance(M.validate(1, {"adhyay": 1, "scenes": [{"scene_id": "S1", "section_kind": "story", "ovi_range": [1,5], "goal": "g", "turn": {"ovi": 1, "text": "t"}, "line_ids": [["S1-L1"]]}]}, {}, {}), list)
    # non-int ovi_range bounds
    assert isinstance(M.validate(1, {"adhyay": 1, "scenes": [{"scene_id": "S1", "section_kind": "story", "ovi_range": ["a", 5], "goal": "g", "turn": {"ovi": 1, "text": "t"}, "line_ids": []}]}, {}, {}), list)
    # turn ovi with non-int bounds
    assert isinstance(M.validate(1, {"adhyay": 1, "scenes": [{"scene_id": "S1", "section_kind": "story", "ovi_range": ["1", 5], "goal": "g", "turn": {"ovi": 3, "text": "t"}, "line_ids": []}]}, {}, {}), list)
    # unknown line id doesn't break order check
    ctx = base_ctx()
    docs = base_docs()
    docs["scenes"] = set_at(docs["scenes"], ["scenes",0,"line_ids"], ["S1-L2", "S9-L9", "S1-L1"])
    errs = M.validate(1, docs["scenes"], docs, ctx)
    # Should report both unknown line and order error
    assert any("S9-L9" in e for e in errs)
    assert any("S1" in e for e in errs)

def test_schema_errors_odd_data_no_raise():
    """schema_errors() must never raise on any JSON-shaped input."""
    assert isinstance(M.schema_errors(None), list)
    assert isinstance(M.schema_errors("not a dict"), list)
    assert isinstance(M.schema_errors([]), list)
    assert isinstance(M.schema_errors({"adhyay": 1, "scenes": "not a list"}), list)

# ---------- Positive ----------
def test_valid():
    docs = base_docs()
    ctx = base_ctx()
    assert M.schema_errors(docs["scenes"]) == []
    assert M.validate(1, docs["scenes"], docs, ctx) == []

```

## ROUND 3 REVIEW FINDINGS (apply what the SPEC supports; Codex items are verified, Haiku items unverified). Keep the catch-all guard in validate. For test findings: make the row ISOLATED (only the rule under test is violated, so the test fails if that rule's check is removed) and assert the offending id/field, never wording the spec does not quote. For coverage: do not convert numeric strings with isdigit/int; accept only real integers and report anything else as an error, never raise. All existing tests must still pass. Return BOTH FILE blocks complete.
### Codex round 3
## Verdict: FIX FIRST

### story_map

none.

### coverage

1. **High —** [coverage.py:129](</D:/aai work/granthstudio/scripts/pipeline/stage1/coverage.py:129>): `covered_by: "²"` makes `validate` raise `ValueError`: `isdigit()` accepts it, but `int()` does not. Remove the numeric-string conversion; the schema permits chapter ovis as integers. I reproduced this with a `jsonschema` stub.

### scenes

1. **Low —** [test_stage1_scenes.py:177](</D:/aai work/granthstudio/tests/test_stage1_scenes.py:177>): The duplicate-scene test also creates overlapping ranges and duplicate lines. Its `"S1"` assertion can pass without duplicate-scene detection. Append an S1 scene with a non-overlapping range and no lines.
2. **Low —** [test_stage1_scenes.py:239](</D:/aai work/granthstudio/tests/test_stage1_scenes.py:239>): `"S1"` also matches the unknown-line error for `S9-L9`, so the assertion does not verify ordering. Check for a separate error associated with S1, distinct from the unknown-line error.

### shots

1. **Low —** [test_stage1_shots.py:170](</D:/aai work/granthstudio/tests/test_stage1_shots.py:170>): The invalid `need_new.class` row fails because the existing preset requires `need_new` to be null. Set the preset to `NEED_NEW` for this row and assert the class error.
2. **Low —** [test_stage1_shots.py:268](</D:/aai work/granthstudio/tests/test_stage1_shots.py:268>): `"S2"` matches the uncovered `S2-L1` error even if the missing-shots check is removed. Isolate the missing-shots rule, for example by giving S2 no lines.
3. **Low —** [test_stage1_shots.py:371](</D:/aai work/granthstudio/tests/test_stage1_shots.py:371>): The test asserts `"not in scene"`, which the spec does not quote. Assert the shot ID in a separate error from the quoted uncovered-line message.

### briefs

1. **Low —** [test_stage1_briefs.py:412](</D:/aai work/granthstudio/tests/test_stage1_briefs.py:412>): The test asserts `"scene exists"`, which the spec does not quote. Assert the image ID in the isolated missing-scene case.

### looks

none.

### voices

none.

### sounds

1. **Low —** [test_stage1_sounds.py:229](</D:/aai work/granthstudio/tests/test_stage1_sounds.py:229>): The test asserts `"document must be an object"`, which the spec does not quote. Assert the document identifier instead.

### questions

none.

The workspace is read-only, so I could not write the requested report file. I could not independently run the suite because the available Python lacks `jsonschema`, and I did not reproduce every Round 2 case; the verdict reflects the verified findings above, not a complete revalidation of all earlier findings.### Haiku round 3
# Stage 1 unit modules: Round 3 review (read-only)

Scope: `scripts/pipeline/stage1/{story_map,coverage,scenes,shots,briefs,looks,voices,sounds,questions}.py`, `tests/test_stage1_<unit>.py`, against `docs/pilot/nemotron_specs/unit_<unit>.md`, `stage1_base.json`, `STAGE1_RULES.md`.

Evidence: `uv run pytest -q --tb=short tests/test_stage1_*.py` gives **418 passed**. Every defect below was checked by calling the module in memory with a small input (no project file written, no network). Fuzzing: every leaf of every document and every ctx key was replaced with 13 odd values (None, int, str, list, dict, bool, nested lists), and each validate/schema_errors call was made with empty and None docs/ctx. The only raises were from `coverage.validate` when a ctx list (`script_line_ids`, `chapter_ovis`, `unfilmed_ovis`) was None or an int. That is ctx, not document data, so it is not counted. No print, env, key or secret handling was found in any module or test.

## Verdict: FIX FIRST

---

## Round 2 findings: status

| Unit | Round 2 finding | Status |
|---|---|---|
| story_map | 1 `ovi_types` not type-checked | FIXED (story_map.py:84-85) |
| story_map | 2 `events` not type-checked | FIXED (story_map.py:108-110) |
| story_map | 3 `key_ovis` not type-checked | FIXED (story_map.py:117-118) |
| story_map | 4 test asserts "not an object" | FIXED (test row now asserts "doc") |
| scenes | 1 test asserts "duplicate scene id" | FIXED (test asserts "S1") |
| scenes | 2 test asserts "order" | FIXED (test asserts "S1") |
| shots | 1 `ovi_ids: 5` raises | FIXED (shots.py:169-170) |
| shots | 2 `beat_line_ids: None` raises | FIXED (shots.py:181-182) |
| shots | 3 scene `line_ids: 5` raises | FIXED (shots.py:177) |
| shots | 4 class-enum row uses preset `01_establishing_shot` | STILL OPEN (defect S-2) |
| shots | 5 test asserts "scene has no shots" | FIXED (test asserts "S2") |
| briefs | 1 `scene_id: ["S1"]` raises | FIXED (briefs.py:121-126, verified) |
| briefs | 2 `references.characters: [""]` accepted | FIXED (briefs.py:78-81, schema error verified) |
| voices | 1 `validate(1, 1, ...)` / `None` raises | FIXED (voices.py:153-154, verified) |
| voices | 2 duplicate entries of one character reported twice | FIXED (voices.py:136-138 uses sets, verified) |
| sounds | 1 test asserts non-quoted wording | PARTLY FIXED (cue[0] now used; line 229 still open, defect O-1) |
| coverage, looks, questions | none | n/a |

---

## story_map

none.

## coverage

none.

## scenes

1. `tests/test_stage1_scenes.py:217-231` (class 3): nine `assert isinstance(M.validate(...), list)` checks. `scenes.validate` wraps `_validate_semantic` in a catch-all that returns `["scenes: malformed structure"]`, so `validate` can never raise and these asserts can never fail. Fix: for each call, assert `not any("malformed structure" in e for e in errs)`, as `test_stage1_sounds.py:290` already does.

## shots

1. `tests/test_stage1_shots.py:305-360` (class 3): twelve `assert isinstance(errs, list)` checks inside `test_validate_odd_data_no_raise`. `shots.validate` has a catch-all, so these can never fail. Fix: replace each with `assert not any("malformed structure" in e for e in errs)`.
2. `tests/test_stage1_shots.py:170` (class 3, Round 2 item 4 still open, verified): the row `(["shots", 0, "need_new"], {"reason": "x", "class": "bad_class"})` sits in a table where `preset` is `01_establishing_shot`. `schema_errors` returns only `shots shots/0/need_new: ... is not of type 'null'` (the else branch), so the class enum is never exercised. With preset `NEED_NEW` the same value gives `shots shots/0/need_new/class: 'bad_class' is not one of [...]`. Fix: move this row to a separate test with `preset` set to `"NEED_NEW"` and assert `"class"` in the message.

## briefs

1. `tests/test_stage1_briefs.py:339, 348, 357, 363, 369, 380` (class 3): six `assert isinstance(errs, list)` checks. `briefs.validate` has a catch-all, so these can never fail. Fix: assert `not any("malformed structure" in e for e in errs)`.
2. `tests/test_stage1_briefs.py:412` (class 4): asserts `"scene exists"`. The spec gives "scene exists" only as rule prose, not as a quoted message. Fix: `assert any("s99_test" in e for e in errs)`.

## looks

none.

## voices

1. `scripts/pipeline/stage1/voices.py:111-115` (class 1): the spec says "a character already RECURRING must not be listed twice". The code counts only RECURRING entries, so a character with one RECURRING entry and one NEW_PROPOSED entry is not flagged when not speaking. Verified: `validate` with `gajanan_maharaj` listed as RECURRING and again as NEW_PROPOSED, and `speaking_characters` set to `["narrator"]`, returns `[]`. Fix: `for char, entries in char_entries.items(): if len(entries) > 1 and any(e.get("status") == "RECURRING" for e in entries): messages.append(f"{char}: recurring character listed twice")`. Add a test row for this case. (The rule is worded in plain prose, so if the owner reads it as "two RECURRING entries only", close this as none.)

## sounds

1. `tests/test_stage1_sounds.py:229` (class 4, Round 2 item 1 partly open, verified): asserts `"document must be an object"`, which the spec does not quote. Fix: `assert isinstance(errs, list) and any("sounds" in e for e in errs)`, or assert the item id only.
2. `tests/test_stage1_sounds.py:235, 264, 269, 274, 281, 288, 297` (class 3): seven `assert isinstance(errs, list)` checks after calls to `validate`, which has a catch-all. These can never fail. Fix: assert `not any("malformed structure" in e for e in errs)`.

## questions

none.

---

## Defects per unit (Round 3)

| Unit | Defects |
|---|---|
| story_map | 0 |
| coverage | 0 |
| scenes | 1 |
| shots | 2 |
| briefs | 2 |
| looks | 0 |
| voices | 1 |
| sounds | 2 |
| questions | 0 |
| **Total** | **8** |

Notes:
- Class 2 (raise) is clean for document data. Every raise found in Round 2 is fixed. The catch-all in six modules hides any future raise, which is why the isinstance-only tests in scenes, shots, briefs and sounds cannot fail. Fixing those tests (items above) is the way to make the no-raise checks real.
- The pytest count is now 418 (Round 2 printed 400).
