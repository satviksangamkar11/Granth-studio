# FIX CALL for the test file `tests/test_stage1_story_map.py` (write ONLY that file, one FILE block). Two independent reviewers (Codex, Haiku) found real defects in your previous version (shown below). Repair ALL of them. The unit spec, BASE data and clarifications follow. HARD RULES that the previous attempts broke:
1. Write ONE robust helper set at the top and use it everywhere: `get_parent(doc, path)` that walks a path list where an int part indexes a list and a str part indexes a dict; `set_at(base, path, value)`, `delete_at(base, path)`, `append_at(base, path, value)` (all work on a deep copy and handle list indexes and dict keys, never index a list with a string). EVERY mutation must be proven to change the document: the helper asserts `mutated != base` (a no-op mutation fails loudly). Never address a list element that does not exist in BASE (append instead).
2. Each row changes exactly ONE thing and leaves everything else valid; contexts (script lines, saved voices, presets) stay complete unless the row is about that context. Each row asserts the item id AND only the keyword the spec QUOTES; for rules with no quoted phrase assert only the item id (never invented words like unique, outside, prefix, shared, empty, mismatch, not exist).
3. Positive rows assert `[]` exactly. A "twice/duplicate" rule needs a real duplicate (append a second entry). A rule that is schema-level in the spec is tested through `schema_errors`; a rule the spec makes semantic is tested ONLY through `validate` (never expect jsonschema to reject reversed ranges or empty names unless the spec's schema says so). jsonschema reports required/additionalProperties errors at the PARENT path: assert the offending field name appears in the message, never a child path.
4. Required-field rows DELETE each required field from a deep copy (root fields and nested objects); extra-key rows ADD one unknown key to an otherwise valid object at the root and at every nested object; every enum has one invalid-value row.
5. `validate(adhyay, doc, docs, ctx)`: `docs` is the dict of ALL nine documents (use only the ones the unit spec lists; pass {} for absent ones) and `ctx` is separate (never `docs["ctx"]`).
6. ids are strings and ovis are integers (covered_by uses an integer ovi or a line id string).
7. Keep it compact (<= 170 lines), synthetic only, loading the module by path with importlib as the unit spec says.
Reply with exactly one FILE block: FILE: tests/test_stage1_story_map.py

## CODEX FINDINGS FOR THIS UNIT
- **story_map — High:** `test_validate`, rows **137,139**, assigns index 9 of a nine-element list; `mutate` **78** raises `IndexError`. Append entries instead. **Medium:** `test_schema_errors` **112** wrongly requires schema rejection of reversed bounds, explicitly a semantic rule. `test_validate` **141** also leaves key ovi 3 outside the reversed range, combining violations. Assertions **141–143,159** require unmandated wording (`ovi_range`, `key_ovis`, `outside`); these rules permit checking the item ID.

## HAIKU FINDINGS FOR THIS UNIT
(1) Lines 137 and 139 use "ovi_types.9", but the base list has indices 0-8. mutate() then raises IndexError. (4) Line 139 asserts "outside" and line 141 asserts "ovi_range"; the spec quotes neither. Line 143 asserts "outside" for key_ovis, also not quoted. Fix: use "ovi_types.8" for both rows (or append); drop the unquoted wording.

## UNIT SPEC (binding)
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



## YOUR PREVIOUS tests/test_stage1_story_map.py (repair it)
```python
from __future__ import annotations
import copy
import json
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "pipeline" / "stage1"))
import story_map as sm

def base() -> tuple[dict, dict]:
    docs = {
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
    ctx = {
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
    return copy.deepcopy(docs), copy.deepcopy(ctx)

def mutate(obj: dict, path: str, value):
    """Set or delete a single item at dot/path. Returns mutated copy."""
    obj = copy.deepcopy(obj)
    parts = path.split(".")
    cur = obj
    for p in parts[:-1]:
        if p.isdigit():
            cur = cur[int(p)]
        else:
            cur = cur[p]
    last = parts[-1]
    if value is __import__("builtins").Ellipsis:
        if last.isdigit():
            del cur[int(last)]
        else:
            del cur[last]
    else:
        if last.isdigit():
            cur[int(last)] = value
        else:
            cur[last] = value
    return obj

# ---------- schema_errors tests ----------
@pytest.mark.parametrize("path,value,keyword", [
    # valid
    (None, None, None),
    # missing required top-level
    ("adhyay", ..., "adhyay"),
    ("ovi_types", ..., "ovi_types"),
    ("events", ..., "events"),
    # extra top-level key
    ("extra", 1, "extra"),
    # adhyay range
    ("adhyay", 0, "adhyay"),
    ("adhyay", 22, "adhyay"),
    # ovi_types items
    ("ovi_types.0.ovi", ..., "ovi"),
    ("ovi_types.0.type", ..., "type"),
    ("ovi_types.0.type", "INVALID", "type"),
    ("ovi_types.0.extra", 1, "extra"),
    ("ovi_types.0.ovi", "x", "ovi"),
    # events items
    ("events.0.event_id", ..., "event_id"),
    ("events.0.title", ..., "title"),
    ("events.0.ovi_range", ..., "ovi_range"),
    ("events.0.key_ovis", ..., "key_ovis"),
    ("events.0.kind", ..., "kind"),
    ("events.0.closure", ..., "closure"),
    ("events.0.event_id", "X1", "event_id"),
    ("events.0.kind", "invalid", "kind"),
    ("events.0.closure", "INVALID", "closure"),
    ("events.0.ovi_range", [5, 1], "ovi_range"),
    ("events.0.ovi_range", [1], "ovi_range"),
    ("events.0.extra", 1, "extra"),
])
def test_schema_errors(path, value, keyword):
    docs, ctx = base()
    if path is None:
        doc = docs["story_map"]
    else:
        doc = mutate(docs["story_map"], path, value)
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
    # ovi untyped
    (1, [("ovi_types.0", ...)], ["ovi 1", "untyped"]),
    # ovi typed twice
    (1, [("ovi_types.9", {"ovi": 1, "type": "STORY"})], ["ovi 1", "typed twice"]),
    # ovi outside chapter
    (1, [("ovi_types.9", {"ovi": 99, "type": "STORY"})], ["ovi 99", "outside"]),
    # event ovi_range lo > hi
    (1, [("events.0.ovi_range", [5, 1])], ["E1", "ovi_range"]),
    # key_ovis outside range
    (1, [("events.0.key_ovis", [9])], ["E1", "key_ovis", "outside"]),
    # empty events valid
    (1, [("events", [])], []),
    # empty ovi_types -> all untyped
    (1, [("ovi_types", [])], ["ovi 1", "untyped"]),
])
def test_validate(adhyay, mutations, keywords):
    docs, ctx = base()
    doc = docs["story_map"]
    for path, val in mutations:
        doc = mutate(doc, path, val)
    errs = sm.validate(adhyay, doc, docs, ctx)
    if not keywords:
        assert errs == [], errs
    else:
        for kw in keywords:
            assert any(kw in e for e in errs), f"{kw} not in {errs}"

```
