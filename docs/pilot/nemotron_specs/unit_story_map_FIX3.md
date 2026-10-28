# FIX CALL 3 for Stage 1 unit `story_map`: return BOTH files in full: `scripts/pipeline/stage1/story_map.py` and `tests/test_stage1_story_map.py`.
You previously wrote the module and (in a separate call) the tests. The tests were RUN against the module: the pytest output below is the mechanical truth, plus a Codex review of the tests. For EVERY failure decide, using the UNIT SPEC as the only authority, whether the TEST or the MODULE is wrong, and fix that side. Rules: the spec decides what is schema-level and what is semantic; JSON Schema cannot compare lo <= hi or check cross references (semantic); jsonschema reports required/additionalProperties errors at the PARENT path (tests assert the offending field name, not a child path); mutation helpers must work on lists AND dicts (int part = list index), must prove the edit changed the document, and nothing may be written into a `None` (initialise nested objects first in the test); every row changes exactly one thing and the baseline stays valid; assert only the item id and keywords the spec QUOTES; positive rows assert `[]`; `import pytest` must be present; tests load the module by path with importlib exactly as the unit spec says; compact, synthetic only. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module.

## PYTEST OUTPUT (mechanical truth)
```
................................                                         [100%]

```

## CODEX REVIEW OF THE TESTS (static)
- **story_map:** Earlier wording and schema-level range findings **FIXED**. **High:** `test_schema_errors`/`test_validate` decorators, **93,138**, reference `pytest` without importing it. `append_at`, **37–41**, checks the parent dictionary rather than its `ovi_types` list; duplicate/outside rows **146,148** raise `AssertionError`. **Medium:** reversed-range row **150** still also puts key ovi 3 outside the range; checking only `E1` cannot distinguish the two violations.

## UNIT SPEC (the authority)
# UNIT SPEC: Stage 1 document `story_map` (schema `stage1_story_map`)
This is ONE unit of the Stage 1 contract (the master spec `stage1_v2.md` was split because one big spec gave unreliable tests). Keep the unit small and exact.
Module: `scripts/pipeline/stage1/story_map.py`. Tests: `tests/test_stage1_story_map.py`. Style: `from __future__ import annotations`, standard library plus `jsonschema`; no print, no network, nothing at import time; tests use only the BASE data below and `tmp_path`; the test file loads the module by path with importlib (`ROOT = Path(__file__).resolve().parents[1]`, `ROOT / "scripts" / "pipeline" / "stage1" / "story_map.py"`).

## Module API (exactly this)
- `SCHEMA`: dict, JSON Schema draft 2020-12 for the document, `additionalProperties: false` on EVERY object (nested too), `$schema` = "https://json-schema.org/draft/2020-12/schema", `title` = "stage1_story_map".
- `schema_errors(doc) -> list[str]`: one message per jsonschema error, formatted "story_map <path>: <message>" (path joined by "/", "doc" when empty).
- `validate(adhyay, doc, docs, ctx) -> list[str]`: SEMANTIC checks only (the schema has already passed; it must still never raise on odd data). `docs` is a dict of ALL nine documents (key names: story_map, coverage, scenes, shots, briefs, looks, voices, sounds, questions; a missing one counts as empty), `ctx` the context dict (keys: script_line_ids list, core_line_ids set, chapter_ovis set, unfilmed_ovis set, preset_ids set, sound_ids set, saved_voices dict voice_key->voice_id, speaking_characters set, known_states dict entity_id->set of state ids). Lists in ctx may arrive as lists or sets: convert with set(). Notes (messages that start with "note: ") come AFTER error messages. Include the adhyay check first: "story_map adhyay <n> does not match <adhyay>".

## Ids and common types
scene_id `^S[0-9]{1,2}$`; shot_id `^S[0-9]{1,2}-[0-9]{1,2}$`; line_id `^S[0-9]{1,2}-L[0-9]{1,3}$`; image id (Stage 1 brief) `^s[0-9]{1,2}_[a-z][a-z0-9_]{0,40}$`; ovi = integer >= 1; adhyay = integer 1..21; text = string 1..400 chars; preset id = string matching `^[0-9]{2}_[a-z0-9_]+$`; sound id `^(bed|fx)_[a-z0-9_]+$`.

## The document shape (from the master spec)
1. `stage1_story_map`: `ovi_types`: array of {ovi, type: STORY|TEACHING|PHILOSOPHY|INVOCATION|RECAP|PHALASHRUTI|OTHER}; `events`: array of {event_id `^E[0-9]{1,2}$`, title, ovi_range [lo,hi], key_ovis [ovi...], kind: story|discourse, closure: RESOLVED_IN_ADHYAY|CONTINUES_NEXT_ADHYAY|STARTED_EARLIER|SOURCE_INCOMPLETE_OR_AMBIGUOUS|NA}.

## Semantic rules of this unit (master spec step 3)
3. story_map: each ovi in `chapter_ovis` typed exactly once ("ovi <n> is untyped" / "ovi <n> is typed twice"); typed ovis outside the chapter reported; events ovi_range lo <= high; key_ovis inside their range.

Messages: tests assert only the quoted keywords/phrases of the rules plus the item id; for rules without a quoted phrase the message is `<item id>: <condition in plain words>`.

## BASE data (valid, note-free; the baseline for EVERY test; `validate(1, BASE_DOCS["story_map"], BASE_DOCS, CTX)` must return [] and `schema_errors` must return [])
File `docs/pilot/nemotron_specs/stage1_base.json` has the keys "docs" (the nine documents) and "ctx". The test file must embed its own copy of what it needs as Python literals (copy the values below exactly):
```json
{
 "docs": {
  "story_map": {
   "adhyay": 1,
   "ovi_types": [
    {
     "ovi": 1,
     "type": "STORY"
    },
    {
     "ovi": 2,
     "type": "STORY"
    },
    {
     "ovi": 3,
     "type": "STORY"
    },
    {
     "ovi": 4,
     "type": "STORY"
    },
    {
     "ovi": 5,
     "type": "STORY"
    },
    {
     "ovi": 6,
     "type": "TEACHING"
    },
    {
     "ovi": 7,
     "type": "TEACHING"
    },
    {
     "ovi": 8,
     "type": "TEACHING"
    },
    {
     "ovi": 9,
     "type": "TEACHING"
    }
   ],
   "events": [
    {
     "event_id": "E1",
     "title": "Arrival",
     "ovi_range": [
      1,
      5
     ],
     "key_ovis": [
      3
     ],
     "kind": "story",
     "closure": "RESOLVED_IN_ADHYAY"
    },
    {
     "event_id": "E2",
     "title": "Teaching",
     "ovi_range": [
      6,
      9
     ],
     "key_ovis": [
      7
     ],
     "kind": "discourse",
     "closure": "NA"
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



## CURRENT MODULE scripts/pipeline/stage1/story_map.py
```python
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

```

## CURRENT TESTS tests/test_stage1_story_map.py
```python
from __future__ import annotations
import copy
import sys
import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "pipeline" / "stage1"))
import story_map as sm

# ---------- robust helpers ----------
def get_parent(doc: dict, path: list):
    """Return (parent_container, key) where parent_container[key] is the target"""
    cur = doc
    for p in path[:-1]:
        cur = cur[p]
    return cur, path[-1]

def get_target(doc: dict, path: list):
    """Return the target object at path"""
    cur = doc
    for p in path:
        cur = cur[p]
    return cur

def set_at(base: dict, path: list, value) -> dict:
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    parent[key] = value
    assert doc != base, "mutation had no effect"
    return doc

def delete_at(base: dict, path: list) -> dict:
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    del parent[key]
    assert doc != base, "mutation had no effect"
    return doc

def append_at(base: dict, path: list, value) -> dict:
    doc = copy.deepcopy(base)
    target = get_target(doc, path)
    assert isinstance(target, list), "append target must be list"
    target.append(value)
    assert doc != base, "mutation had no effect"
    return doc

# ---------- BASE data ----------
BASE_DOCS = {
    "story_map": {
        "adhyay": 1,
        "ovi_types": [
            {"ovi": 1, "type": "STORY"},
            {"ovi": 2, "type": "STORY"},
            {"ovi": 3, "type": "STORY"},
            {"ovi": 4, "type": "STORY"},
            {"ovi": 5, "type": "STORY"},
            {"ovi": 6, "type": "TEACHING"},
            {"ovi": 7, "type": "TEACHING"},
            {"ovi": 8, "type": "TEACHING"},
            {"ovi": 9, "type": "TEACHING"},
        ],
        "events": [
            {
                "event_id": "E1",
                "title": "Arrival",
                "ovi_range": [1, 5],
                "key_ovis": [3],
                "kind": "story",
                "closure": "RESOLVED_IN_ADHYAY",
            },
            {
                "event_id": "E2",
                "title": "Teaching",
                "ovi_range": [6, 9],
                "key_ovis": [7],
                "kind": "discourse",
                "closure": "NA",
            },
        ],
    }
}
BASE_CTX = {
    "script_line_ids": ["S1-L1", "S1-L2", "S2-L1"],
    "core_line_ids": ["S1-L1", "S2-L1"],
    "chapter_ovis": [1, 2, 3, 4, 5, 6, 7, 8, 9],
    "unfilmed_ovis": [],
    "preset_ids": ["01_establishing_shot", "03_slow_cinematic_push"],
    "sound_ids": ["bed_roadside_quiet", "fx_door_wood_creak"],
    "saved_voices": {"narrator": "CXkeo30p0Sk4Lr0TAzeo", "gajanan": "8fqGzH80bdkm2UseeV9f"},
    "speaking_characters": ["narrator", "gajanan_maharaj"],
    "known_states": {"gajanan_maharaj": ["adult_youth_v1"]},
}

# ---------- schema_errors tests ----------
@pytest.mark.parametrize("path,value,keyword", [
    # valid
    (None, None, None),
    # missing required top-level
    (["adhyay"], ..., "adhyay"),
    (["ovi_types"], ..., "ovi_types"),
    (["events"], ..., "events"),
    # extra top-level key
    (["extra"], 1, "extra"),
    # adhyay range
    (["adhyay"], 0, "adhyay"),
    (["adhyay"], 22, "adhyay"),
    # ovi_types items
    (["ovi_types", 0, "ovi"], ..., "ovi"),
    (["ovi_types", 0, "type"], ..., "type"),
    (["ovi_types", 0, "type"], "INVALID", "type"),
    (["ovi_types", 0, "extra"], 1, "extra"),
    (["ovi_types", 0, "ovi"], "x", "ovi"),
    # events items
    (["events", 0, "event_id"], ..., "event_id"),
    (["events", 0, "title"], ..., "title"),
    (["events", 0, "ovi_range"], ..., "ovi_range"),
    (["events", 0, "key_ovis"], ..., "key_ovis"),
    (["events", 0, "kind"], ..., "kind"),
    (["events", 0, "closure"], ..., "closure"),
    (["events", 0, "event_id"], "X1", "event_id"),
    (["events", 0, "kind"], "invalid", "kind"),
    (["events", 0, "closure"], "INVALID", "closure"),
    (["events", 0, "ovi_range"], [1], "ovi_range"),
    (["events", 0, "extra"], 1, "extra"),
])
def test_schema_errors(path, value, keyword):
    doc = BASE_DOCS["story_map"]
    if path is not None:
        if value is ...:
            doc = delete_at(doc, path)
        else:
            doc = set_at(doc, path, value)
    errs = sm.schema_errors(doc)
    if keyword is None:
        assert errs == []
    else:
        assert any(keyword in e for e in errs), f"{keyword} not in {errs}"

# ---------- validate tests ----------
@pytest.mark.parametrize("adhyay,mutations,keywords", [
    # valid
    (1, [], []),
    # adhyay mismatch
    (2, [], ["adhyay", "does not match"]),
    # ovi untyped (delete first ovi_type)
    (1, [(["ovi_types", 0], ...)], ["ovi 1", "untyped"]),
    # ovi typed twice (append duplicate ovi 1)
    (1, [(["ovi_types"], {"ovi": 1, "type": "STORY"})], ["ovi 1", "typed twice"]),
    # ovi outside chapter (append ovi 99)
    (1, [(["ovi_types"], {"ovi": 99, "type": "STORY"})], ["ovi 99"]),
    # event ovi_range lo > hi (semantic, not schema) - isolate by clearing key_ovis
    (1, [(["events", 0, "ovi_range"], [5, 1]), (["events", 0, "key_ovis"], [])], ["E1", "lo > hi"]),
    # key_ovis outside range
    (1, [(["events", 0, "key_ovis"], [9])], ["E1", "key_ovi", "outside"]),
    # empty events valid
    (1, [(["events"], [])], []),
    # empty ovi_types -> all untyped
    (1, [(["ovi_types"], [])], ["ovi 1", "untyped"]),
])
def test_validate(adhyay, mutations, keywords):
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    doc = docs["story_map"]
    for path, val in mutations:
        if val is ...:
            doc = delete_at(doc, path)
        elif isinstance(val, dict) and path and path[-1] == "ovi_types":
            doc = append_at(doc, path, val)
        else:
            doc = set_at(doc, path, val)
    errs = sm.validate(adhyay, doc, docs, ctx)
    if not keywords:
        assert errs == [], errs
    else:
        for kw in keywords:
            assert any(kw in e for e in errs), f"{kw} not in {errs}"

```
