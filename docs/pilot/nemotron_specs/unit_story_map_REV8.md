# FIX CALL: return BOTH files in full: `scripts/pipeline/stage1/story_map.py` and `tests/test_stage1_story_map.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
....................................                                     [100%]
36 passed in 0.05s

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


def validate(adhyay: int, doc: dict[str, Any], docs: dict[str, Any], ctx: dict[str, Any]) -> list[str]:
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

    # Check ovi_types
    ovi_types = doc.get("ovi_types", [])
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

    # Check events
    events = doc.get("events", [])
    for event in events:
        if not isinstance(event, dict):
            continue
        event_id = event.get("event_id", "unknown")
        ovi_range = event.get("ovi_range", [])
        key_ovis = event.get("key_ovis", [])

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
    (1, [("__replace__", "not a dict")], ["not an object"]),
    # odd data: ovi_types with non-dict item -> ovi 1 untyped
    (1, [(["ovi_types", 0], "not a dict")], ["ovi 1", "untyped"]),
    # odd data: ovi_range with non-int
    (1, [(["events", 0, "ovi_range"], ["a", 5])], []),
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

## ROUND 2 REVIEW FINDINGS (apply what the SPEC supports; Codex reproduced its items, Haiku's are unverified).
MANDATORY ROOT-CAUSE FIX: rename the current semantic body to a private helper and make `validate(adhyay, doc, docs, ctx)` call it inside `try/except (TypeError, AttributeError, KeyError, ValueError, IndexError)`; on such an exception return `["story_map: malformed structure"]` (the spec says validate must never raise on odd data). ALSO fix each specific defect below at its source (type-check lists/ids before iterating or building sets), add one isolated regression test per defect, make weak tests isolated and assert ids instead of unquoted wording. All existing tests must still pass.
### Codex round 2
## Verdict: FIX FIRST

### story_map

1. **High —** [story_map.py:85](</D:/aai work/granthstudio/scripts/pipeline/stage1/story_map.py:85>): `ovi_types: null`, `events: null`, or an event with `key_ovis: null` raises `TypeError`. Check each value is a list before iterating and return errors for malformed values.

### coverage

None.

### scenes

1. **Low —** [test_stage1_scenes.py:177](</D:/aai work/granthstudio/tests/test_stage1_scenes.py:177>): The duplicate-scene test asserts `duplicate scene id`, which the spec does not quote. Use an isolated duplicate case and assert its scene ID.

### shots

1. **High —** [shots.py:168](</D:/aai work/granthstudio/scripts/pipeline/stage1/shots.py:168>): `ovi_ids: null` or `beat_line_ids: null` raises `TypeError`. Guard both arrays before iteration.
2. **High —** [shots.py:183](</D:/aai work/granthstudio/scripts/pipeline/stage1/shots.py:183>): A beat line assigned to the wrong scene is still counted as covered. With `S2-L1` on an S1 shot and no S2 shot covering it, validation reports the wrong assignment but misses `S2-L1: line is in no shot beat`. Count coverage only for lines belonging to that shot’s scene.
3. **Low —** [test_stage1_shots.py:170](</D:/aai work/granthstudio/tests/test_stage1_shots.py:170>): The invalid-class row fails because the existing preset forbids an object, even without the class enum. Set the preset to `NEED_NEW` for this row.
4. **Low —** [test_stage1_shots.py:268](</D:/aai work/granthstudio/tests/test_stage1_shots.py:268>): The test asserts the unquoted wording `scene has no shots`. Isolate the missing-scene-shots rule and assert the scene ID.

### briefs

1. **High —** [briefs.py:118](</D:/aai work/granthstudio/scripts/pipeline/stage1/briefs.py:118>): A referenced scene with `scene_id: []` raises `TypeError` while building the set. Include only string scene IDs and guard malformed referenced arrays.
2. **Low —** [test_stage1_briefs.py:295](</D:/aai work/granthstudio/tests/test_stage1_briefs.py:295>): The missing-scene case also leaves a shot belonging to another scene, so it passes if the scene-existence check is removed. Give the brief no shot references for this test.

### looks

None.

### voices

1. **High —** [voices.py:51](</D:/aai work/granthstudio/scripts/pipeline/stage1/voices.py:51>): `validate(1, None, docs, ctx)` raises `AttributeError`. Check that `doc` is a dictionary before calling `.get`.
2. **High —** [voices.py:111](</D:/aai work/granthstudio/scripts/pipeline/stage1/voices.py:111>): The validator rejects duplicate `NEW_PROPOSED` entries for a character outside `speaking_characters`, although the spec only requires exactly one entry for speaking characters and prohibits duplicate recurring characters. Restrict duplicate checks to those rules.
3. **High —** [voices.py:147](</D:/aai work/granthstudio/scripts/pipeline/stage1/voices.py:147>): Two entries for the *same* non-narrator are treated as two characters sharing a voice. Deduplicate character IDs before checking sharing.
4. **Low —** [test_stage1_voices.py:208](</D:/aai work/granthstudio/tests/test_stage1_voices.py:208>): The recurring non-speaker duplicate case also triggers the same-character voice-sharing error, so it does not isolate the recurring-duplicate rule. Use distinct voice keys for the duplicate entries and keep both keys valid in context.
5. **Low —** [test_stage1_voices.py:215](</D:/aai work/granthstudio/tests/test_stage1_voices.py:215>): The narrator-plus-two-characters case uses an unsaved `shared` key, so the asserted character ID also appears in a saved-cast error. Use a saved key and matching voice ID.

### sounds

1. **High —** [sounds.py:109](</D:/aai work/granthstudio/scripts/pipeline/stage1/sounds.py:109>): A referenced scene with `line_ids: [[]]` raises `TypeError` during set construction. Filter for string line IDs before constructing the set.

### questions

None.

The report could not be written as a file because the workspace is read-only. I reproduced the listed semantic failures in memory with a `jsonschema` stub; the virtual-environment interpreter was denied execution, so I could not independently rerun the suite or reproduce every Round 1 schema finding.### Haiku round 2
# Stage 1 unit modules: Round 2 review (read-only)

Scope: `scripts/pipeline/stage1/{story_map,coverage,scenes,shots,briefs,looks,voices,sounds,questions}.py`, `tests/test_stage1_<unit>.py`, against `docs/pilot/nemotron_specs/unit_<unit>.md`, `stage1_base.json`, `STAGE1_RULES.md`.

Evidence: `uv run pytest -q --tb=short tests/test_stage1_*.py` gives **400 passed** (the brief states 415; the count here is what the run printed). Every defect below was reproduced by calling the module in memory with a small input (no project file written, no network). No print, env, key or secret handling was found in any module or test.

## Verdict: FIX FIRST

---

## Round 1 findings: status

| Unit | Round 1 finding | Status |
|---|---|---|
| story_map | `ovi_types: [null]` raises | FIXED (returns "ovi N is untyped") |
| story_map | tests assert `lo > hi`, `key_ovi`, `outside` wording | FIXED (rows assert "E1") |
| story_map | `key_ovis` below range branch untested | FIXED (row `key_ovis: [0]` present) |
| coverage | `ovis: [null]` raises | FIXED. Note: Round 1 said "Tests: none"; `tests/test_stage1_coverage.py` exists (243 lines) |
| scenes | out-of-order check lost after unknown line id | FIXED |
| scenes | `ovi_range: ["a", 2]` turn check raises TypeError | FIXED |
| scenes | unhashable `scene_id` / `line_id` raises | FIXED |
| scenes | story `teaching_treatment: "none"` rejected by schema | FIXED (schema `const: none`; positive test present) |
| scenes | no isolated test for forbidden story treatment | FIXED (`test_schema_story_scene_forbidden_treatment`) |
| scenes | duplicate-scene test passes through collateral match | FIXED (now asserts "duplicate scene id"; wording see defect S1) |
| shots | `shots: [null]` raises | FIXED |
| shots | `preset` accepts any string | FIXED (pattern `^([0-9]{2}_[a-z0-9_]+\|NEED_NEW)$`) |
| shots | class-enum row uses non-NEED_NEW preset | STILL OPEN (defect H4) |
| shots | scene-has-shots test collateral "S2" | FIXED (asserts "scene has no shots") |
| shots | "consecutive" wording asserted | FIXED (asserts "S1"; the test fails if the rule is removed) |
| shots | preset check skipped when scene missing | FIXED (verified: "S1-1: unknown preset bogus" is reported) |
| briefs | non-string `image_id` / `shot_id` / `scene_id` raises | PARTLY: `image_id`/`shot_id` FIXED; `scene_id` in scenes still raises (defect B1) |
| briefs | `prop`/`prop_state` empty accepted; text bounds missing | FIXED for listed fields; `references.characters` items still unbounded (defect B2) |
| briefs | asserted wording not quoted by spec | FIXED (asserts item id) |
| voices | `cast: [1]` / `cast: None` / non-dict entries raise | FIXED |
| voices | two NEW_PROPOSED entries not flagged; recurring duplicate outside speaking set | FIXED (verified) |
| voices | narrator suppresses error for two other sharers | FIXED (verified: both `x` and `y` flagged) |
| voices | required fields never tested by deletion | FIXED (DELETE rows present) |
| voices | asserted wording not quoted | FIXED (asserts item id) |
| sounds | cue without `sound_id` raises AttributeError | FIXED (verified) |
| sounds | asserted wording not quoted | PARTLY: `cue[0]` used in the main table; guard-message asserts remain (defect SO1) |
| questions | unhashable `id` / `scene_id` raises | FIXED (verified) |
| questions | odd-data test lacks unhashable cases | FIXED (cases present) |
| looks | none | n/a |

---

## story_map

1. `scripts/pipeline/stage1/story_map.py:83-85`: `ovi_types` is not type-checked. `{"ovi_types": None}` raises `TypeError: 'NoneType' object is not iterable` (verified). Fix: `ovi_types = doc.get("ovi_types"); if not isinstance(ovi_types, list): ovi_types = []`.
2. `scripts/pipeline/stage1/story_map.py:106-107`: `events` is not type-checked. `{"events": 5}` raises `TypeError` (verified). Fix: `events = doc.get("events"); if not isinstance(events, list): events = []`.
3. `scripts/pipeline/stage1/story_map.py:112, 122`: `key_ovis` is not type-checked. `key_ovis: 5` raises `TypeError` (verified). Fix: `key_ovis = event.get("key_ovis"); if not isinstance(key_ovis, list): key_ovis = []`.
4. `tests/test_stage1_story_map.py:163` (class 4): the odd-data row asserts `"not an object"`, which the spec does not quote. Fix: assert the item id, for example `["doc"]`, instead of the wording.

## coverage

none.

## scenes

1. `tests/test_stage1_scenes.py:177` (class 4): the duplicate-id test asserts `"duplicate scene id"`, which the spec does not quote. Fix: keep the test but assert the item id only, e.g. `any(e.startswith("S1:") for e in errs)`, and assert that the message set differs from the valid baseline. The collateral-match problem is fixed, so the wording is the only remaining issue.
2. `tests/test_stage1_scenes.py:239` (class 4): asserts `"order"`, which the spec does not quote ("in script order" is rule prose, not a message). Fix: `assert any("S1" in e for e in errs)`.

## shots

1. `scripts/pipeline/stage1/shots.py:168` (class 2): `shot.get("ovi_ids", [])` is iterated without a type check. A shot with `ovi_ids: 5` inside a valid scene raises `TypeError` (verified). Fix: `ovi_ids = shot.get("ovi_ids"); if isinstance(ovi_ids, list): for ovi in ovi_ids: ...`.
2. `scripts/pipeline/stage1/shots.py:179` (class 2): `beat_line_ids` iterated without a type check. `beat_line_ids: None` raises `TypeError` (verified). Fix: `beat_line_ids = shot.get("beat_line_ids"); if not isinstance(beat_line_ids, list): beat_line_ids = []`.
3. `scripts/pipeline/stage1/shots.py:205` (class 2): scene `line_ids` iterated in the "line is in no shot beat" loop with no type check. A scene with `line_ids: 5` raises `TypeError` (verified). Fix: `line_ids = scene.get("line_ids"); if not isinstance(line_ids, list): line_ids = []` before the loop.
4. `tests/test_stage1_shots.py:170` (class 3, Round 1 still open): the row `{"reason": "x", "class": "bad_class"}` sits in a table where `preset` is the base value `01_establishing_shot`. The failure comes from the `else` branch ("is not of type 'null'", verified), so the class enum is never exercised by this row. Fix: set `preset` to `"NEED_NEW"` for this row, as `test_need_new_class_enum` already does, and check the message names `class`.
5. `tests/test_stage1_shots.py:268` (class 4): asserts `"scene has no shots"`, which the spec does not quote. Fix: assert `"S2"` in the error and that the `has no shots` item is the only one for S2, or use the item id only.

## briefs

1. `scripts/pipeline/stage1/briefs.py:118` (class 2, Round 1 still open): `scene_ids = {s.get("scene_id") ...}` builds a set from unvalidated values. A scenes entry with `scene_id: ["S1"]` raises `TypeError: unhashable type: 'list'` (verified). Fix: `scene_ids = {sid for s in scenes_list if isinstance(s, dict) for sid in [s.get("scene_id")] if isinstance(sid, str)}`. Add a regression case.
2. `scripts/pipeline/stage1/briefs.py:78` (class 1): the spec's `references.characters` is `[text...]` (text = 1..400 chars). The schema gives items `{"type": "string"}` with no bounds, so `references.characters: [""]` produces no schema error (verified). Fix: `"characters": {"type": "array", "items": {"type": "string", "minLength": 1, "maxLength": 400}}`. Add a schema test.

## looks

none.

## voices

1. `scripts/pipeline/stage1/voices.py:51` and `:60` (class 2, new): `validate` calls `doc.get` without checking `doc`. `validate(1, [1], ...)` and `validate(1, None, ...)` raise `AttributeError` (verified). Fix: first line of `validate`: `if not isinstance(doc, dict): return ["voices doc: document must be an object"]`.
2. `scripts/pipeline/stage1/voices.py:147` (class 1, false positive, new): when one character is listed twice with the same non-narrator `voice_key`, the code reports `"<char>: voice key shared with another character"` once per entry. Repro: entries `extra_char`, `extra_char` both with key `gajanan` produce two "shared" messages for `extra_char` (verified). The spec's rule is about two different characters. Fix: `non_narrator_chars = sorted({c for c in chars if c != "narrator"})` so repeated entries of one character count once.

## sounds

1. `tests/test_stage1_sounds.py:229, 241, 247, 253, 259` (class 4, partly Round 1 open): the guard and rule asserts include wording the spec does not quote ("document must be an object", "cue must be an object", "scene does not exist", "anchor_line_id must be a string", "sound_id must be a string"). Fix: assert `"cue[0]"` (or `"sounds"` for the document row) only, as the spec requires.

## questions

none.

---

## Defects per unit (Round 2)

| Unit | Defects |
|---|---|
| story_map | 4 |
| coverage | 0 |
| scenes | 2 |
| shots | 5 |
| briefs | 2 |
| looks | 0 |
| voices | 2 |
| sounds | 1 |
| questions | 0 |
| **Total** | **16** |

Notes:
- Three of the new raises (story_map 1-3, shots 1-3, briefs 1, voices 1) would have been caught by the odd-data tests the spec asks for. Those tests should gain the cases listed above when the fixes land.
- The pytest count printed is 400 (the brief says 415). Confirm which run the coder counted.
