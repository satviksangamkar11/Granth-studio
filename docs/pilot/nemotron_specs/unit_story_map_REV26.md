# FIX CALL: return BOTH files in full: `scripts/pipeline/stage1/story_map.py` and `tests/test_stage1_story_map.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
.........................................                                [100%]
41 passed in 0.06s

```

## SPEC
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


def _validate_semantic(adhyay: int, doc: dict[str, Any], docs: dict[str, Any], ctx: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    notes: list[str] = []

    # Guard: doc must be a dict
    if not isinstance(doc, dict):
        errors.append("story_map doc: not an object")
        return errors + notes

    # Adhyay check
    doc_adhyay = doc.get("adhyay")
    if doc_adhyay != adhyay:
        errors.append(f"story_map adhyay {doc_adhyay} does not match {adhyay}")

    # Get chapter_ovis from ctx (convert to set)
    chapter_ovis = set(ctx.get("chapter_ovis", []))

    # Check ovi_types - guard against non-list
    ovi_types = doc.get("ovi_types")
    if not isinstance(ovi_types, list):
        ovi_types = []
    typed_ovis: dict[int, int] = {}  # ovi -> count
    for item in ovi_types:
        if not isinstance(item, dict):
            continue
        ovi = item.get("ovi")
        if isinstance(ovi, int):
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

    # Check events - guard against non-list
    events = doc.get("events")
    if not isinstance(events, list):
        events = []
    for event in events:
        if not isinstance(event, dict):
            continue
        event_id = event.get("event_id", "unknown")
        ovi_range = event.get("ovi_range", [])
        key_ovis = event.get("key_ovis")
        if not isinstance(key_ovis, list):
            key_ovis = []

        # ovi_range lo <= hi
        if isinstance(ovi_range, list) and len(ovi_range) == 2:
            lo, hi = ovi_range[0], ovi_range[1]
            if isinstance(lo, int) and isinstance(hi, int):
                if lo > hi:
                    errors.append(f"{event_id}: ovi_range lo > hi")

                # key_ovis inside their range
                for kovi in key_ovis:
                    if isinstance(kovi, int):
                        if kovi < lo or kovi > hi:
                            errors.append(f"{event_id}: key_ovi {kovi} outside ovi_range")

    return errors + notes


def validate(adhyay: int, doc: dict[str, Any], docs: dict[str, Any], ctx: dict[str, Any]) -> list[str]:
    try:
        return _validate_semantic(adhyay, doc, docs, ctx)
    except (TypeError, AttributeError, KeyError, ValueError, IndexError):
        return ["story_map: malformed structure"]

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
    (1, [(["events", 0, "ovi_range"], [5, 1]), (["events", 0, "key_ovis"], [])], ["E1"]),
    # key_ovis outside range (above)
    (1, [(["events", 0, "key_ovis"], [9])], ["E1"]),
    # key_ovis outside range (below)
    (1, [(["events", 0, "key_ovis"], [0])], ["E1"]),
    # empty events valid
    (1, [(["events"], [])], []),
    # empty ovi_types -> all untyped
    (1, [(["ovi_types"], [])], ["ovi 1", "untyped"]),
    # odd data: doc not a dict
    (1, [("__replace__", "not a dict")], ["doc"]),
    # odd data: ovi_types with non-dict item -> ovi 1 untyped
    (1, [(["ovi_types", 0], "not a dict")], ["ovi 1", "untyped"]),
    # odd data: ovi_range with non-int
    (1, [(["events", 0, "ovi_range"], ["a", 5])], []),
    # regression: ovi_types is null
    (1, [(["ovi_types"], None)], ["ovi 1", "untyped"]),
    # regression: events is null
    (1, [(["events"], None)], []),
    # regression: event key_ovis is null
    (1, [(["events", 0, "key_ovis"], None)], []),
    # regression: events is non-list
    (1, [(["events"], 5)], []),
    # regression: ovi_types is non-list
    (1, [(["ovi_types"], "not a list")], ["ovi 1", "untyped"]),
])
def test_validate(adhyay, mutations, keywords):
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    doc = docs["story_map"]
    for path, val in mutations:
        if path == "__replace__":
            doc = val
        elif val is ...:
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

## ROUND 9 FINDINGS: TESTS ONLY. The module must be returned UNCHANGED, character for character (unless one of your new rows proves a real module defect against the SPEC; then fix the module and say so in no prose). Add data rows to the existing tables (schema-valid rows for each enum value; schema-invalid rows for each bound/minLength) so that removing that schema rule fails a test. Keep every existing test and every assertion 'not any("malformed structure" in e ...)' unchanged. Only the items listed for YOUR unit 'story_map' in the report below apply; if there are none for 'story_map', return both files unchanged. Return BOTH complete FILE blocks.
### Haiku round 9 (use only the section for story_map)
# Stage 1 unit modules: Round 9 review (read-only)

Scope: `scripts/pipeline/stage1/{story_map,coverage,scenes,shots,briefs,looks,voices,sounds,questions}.py`, `tests/test_stage1_<unit>.py`, against `docs/pilot/nemotron_specs/unit_<unit>.md`, `stage1_base.json`, `STAGE1_RULES.md`.

## Method and evidence

- `uv run pytest -q --tb=short tests/test_stage1_*.py`: 425 passed (the review prompt says 460; the suite reports 425).
- Mutation checks run in memory only (a patched loader substitutes one source string per run; no file was written). Each run is one pytest invocation on the unit's test file. A "killed" mutant means at least one test fails.
  - 81 semantic-rule mutants (every `validate` rule, adhyay check included): all killed. Single-test kills for most rules, so the rule-specific test is isolated.
  - 38 schema-rule mutants (conditionals, required lists, patterns, object shapes): 6 survived as recorded below.
  - Every schema `enum` value removed one at a time: the survivors are recorded below.
  - Every `minItems`, `minimum`, `minLength` bound relaxed one at a time: the survivors are recorded below.
- Fuzz (in-process, no writes): 14,782 calls of `validate` and `schema_errors` with odd values (None, bool, numbers, strings, lists, dicts, nested wrong types, missing keys) on every document path (depth up to 4) and on every `docs` entry. No exception escaped from any document input. Not counted: `coverage.validate` and `scenes.validate` raise TypeError when a `ctx` list is None or a bool (`ctx` is the context dict, not a document). Not counted: `coverage.validate` raises AttributeError when `ctx` itself is None (Round 8 treatment).
- Grep: no print, environment read, key, token or secret handling in any module or test.

## Round 8 status

| Round 8 finding | Status (Round 9) |
|---|---|
| scenes 1: `malformed structure` assertions | Sentinel class, excluded per KNOWN DESIGN RULE |
| shots 1: `malformed structure` assertions | Sentinel class, excluded |
| briefs 1: collateral "scene does not exist" row | FIXED. Row is absent from `SEMANTIC_CASES`. Removing the scene-existence rule now fails only `test_semantic_scene_not_exist_no_shot_refs` (verified) |
| briefs 2: `malformed structure` assertions | Sentinel class, excluded |
| looks 1: `malformed structure` assertion | Sentinel class, excluded |
| sounds 1: `malformed structure` assertions | Sentinel class, excluded |
| Round 7 shots: `test_consecutive_grouped_by_scene_id` cannot fail | FIXED. Grouping by `f"S{scene_num}"` now fails that test (verified) |
| Round 9 scenes: reversed-range test isolated | Verified. Removing the `lo > hi` rule fails exactly one test |

## story_map

1. `story_map.py:23` (class 3): schema `type` enum values INVOCATION, OTHER, PHILOSOPHY, RECAP and PHALASHRUTI have no failing test when removed. Fix: add a schema-valid case per value to the schema-valid test, e.g. `ovi_types[0].type = "PHALASHRUTI"` must give `schema_errors == []`.
2. `story_map.py:47` (class 3): schema `closure` enum values CONTINUES_NEXT_ADHYAY, STARTED_EARLIER and SOURCE_INCOMPLETE_OR_AMBIGUOUS have no failing test when removed. Fix: same as item 1 for `events[0].closure`.
3. `story_map.py:22`, `:40`, `:44` (class 3): the `ovi >= 1` bound (ovi_types item `ovi`, events `ovi_range` items, events `key_ovis` items) is untested. Fix: add schema rows with `0` for each path.
4. `story_map.py:35` (class 3): `events[].title` minLength 1 is untested. Fix: add a schema row with `title = ""`.

## coverage

1. `coverage.py:25` (class 3): the enum value PROPOSE_OMISSION is never asserted as schema-valid; removing it from the enum fails no test. The omission tests call `validate` only. Fix: add a `schema_errors(doc) == []` case for a document with one PROPOSE_OMISSION entry that has a reason.
2. `coverage.py:27` (class 3): `reason` minLength 1 is untested. Fix: add a schema row with `reason = ""` for a VISUALISED entry, expecting a `reason` error.
3. `coverage.py:31` (class 3): `covered_by` integer minimum 1 is untested. Fix: add a schema row with `covered_by = 0` on a MERGED_EQUIVALENT entry.

## scenes

1. `scenes.py:49` (class 3): enum values `contemplative_hold` and `symbol_from_text` have no failing test when removed. Fix: add a schema-valid case per value to the discourse-scene schema test.
2. `scenes.py:58` (class 3): the schema clause `"teaching_treatment": {"not": {"const": "none"}}` for discourse scenes is untested (removing it fails no test). The semantic rule for the same case is tested, so only the schema clause is uncovered. Fix: add `schema_errors` non-empty for a discourse scene with `teaching_treatment = "none"`.
3. `scenes.py:31` (class 3): `ovi_range` item minimum 1 is untested. Fix: add a schema row with `ovi_range = [0, 5]`.

## shots

1. `shots.py:63` (class 3): enum values `missing_image`, `json_arrangement` and `renderer_gap` of `need_new.class` have no failing test when removed (only the required-field check is tested). Fix: add a schema-valid NEED_NEW case per class value.
2. `shots.py:18` (class 3): `adhyay` minimum 1 is untested (`adhyay = 0` passes the schema). Fix: add a schema row with `adhyay = 0` expecting an `adhyay` error.
3. `shots.py:62` (class 3): `need_new.reason` minLength 1 is untested. Fix: add a schema row with `need_new.reason = ""`.

## briefs

1. `briefs.py:17` (class 3): `adhyay` minimum 1 is untested. Fix: add a schema row with `adhyay = 0`.

## looks

1. `looks.py:27` (class 3): enum values `place` and `prop` of `kind` have no failing test when removed. Fix: add a schema-valid case per value (`kind = "place"`, `kind = "prop"`).

## voices

1. `voices.py:28` (class 3): enum value `female` of `gender` has no failing test when removed. Fix: add a schema-valid case with `gender = "female"`.
2. `voices.py:29` (class 3): enum value `NEW_PROPOSED` of `status` has no failing test when removed. Fix: add a schema-valid case with `status = "NEW_PROPOSED"`.

## sounds

1. `sounds.py:28` (class 3): enum value `fx` of `kind` has no failing test when removed. Fix: add a schema-valid cue with `kind = "fx"` and an `fx_` sound id.
2. `sounds.py:31` (class 3): enum value `stated` of `basis` has no failing test when removed. Fix: add a schema-valid cue with `basis = "stated"`.
3. `sounds.py:17` (class 3): `adhyay` minimum 1 is untested. Fix: add a schema row with `adhyay = 0`.
4. `sounds.py:29` (class 3): `sound_prompt` minLength 1 is untested. Fix: add a schema row with `sound_prompt = ""` on a NEED_NEW cue.
5. `sounds.py:30` (class 3): `purpose` minLength 1 is untested. Fix: add a schema row with `purpose = ""`.

## questions

1. `questions.py:22` (class 3): the id pattern `^Q[0-9]+$` is untested. Changing it to `^Q` fails no test. Fix: add a schema row with `id = "Qx"` (and one with `id = "Q"`) expecting an `id` error.

## Items checked and found implemented

Every semantic rule of every unit in its unit spec (`validate`) is implemented and has a failing test. The schema conditionals (scenes discourse/story, shots NEED_NEW/else, coverage PROPOSE_OMISSION and MERGED_EQUIVALENT, sounds NEED_NEW/else) and the spec-quoted messages match. No class 1 or class 2 defect was verified.

## Defects per unit (Round 9)

| Unit | Defects |
|---|---|
| story_map | 4 |
| coverage | 3 |
| scenes | 3 |
| shots | 3 |
| briefs | 1 |
| looks | 1 |
| voices | 2 |
| sounds | 5 |
| questions | 1 |
| **Total** | **23** |

All 23 are class 3 (test gaps). None is a missing rule or a raise on document data.

## Verdict: FIX FIRST
