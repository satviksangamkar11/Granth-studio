# FIX CALL for the test file `tests/test_stage1_scenes.py` (write ONLY that file, one FILE block). Two independent reviewers (Codex, Haiku) found real defects in your previous version (shown below). Repair ALL of them. The unit spec, BASE data and clarifications follow. HARD RULES that the previous attempts broke:
1. Write ONE robust helper set at the top and use it everywhere: `get_parent(doc, path)` that walks a path list where an int part indexes a list and a str part indexes a dict; `set_at(base, path, value)`, `delete_at(base, path)`, `append_at(base, path, value)` (all work on a deep copy and handle list indexes and dict keys, never index a list with a string). EVERY mutation must be proven to change the document: the helper asserts `mutated != base` (a no-op mutation fails loudly). Never address a list element that does not exist in BASE (append instead).
2. Each row changes exactly ONE thing and leaves everything else valid; contexts (script lines, saved voices, presets) stay complete unless the row is about that context. Each row asserts the item id AND only the keyword the spec QUOTES; for rules with no quoted phrase assert only the item id (never invented words like unique, outside, prefix, shared, empty, mismatch, not exist).
3. Positive rows assert `[]` exactly. A "twice/duplicate" rule needs a real duplicate (append a second entry). A rule that is schema-level in the spec is tested through `schema_errors`; a rule the spec makes semantic is tested ONLY through `validate` (never expect jsonschema to reject reversed ranges or empty names unless the spec's schema says so). jsonschema reports required/additionalProperties errors at the PARENT path: assert the offending field name appears in the message, never a child path.
4. Required-field rows DELETE each required field from a deep copy (root fields and nested objects); extra-key rows ADD one unknown key to an otherwise valid object at the root and at every nested object; every enum has one invalid-value row.
5. `validate(adhyay, doc, docs, ctx)`: `docs` is the dict of ALL nine documents (use only the ones the unit spec lists; pass {} for absent ones) and `ctx` is separate (never `docs["ctx"]`).
6. ids are strings and ovis are integers (covered_by uses an integer ovi or a line id string).
7. Keep it compact (<= 170 lines), synthetic only, loading the module by path with importlib as the unit spec says.
Reply with exactly one FILE block: FILE: tests/test_stage1_scenes.py

## CODEX FINDINGS FOR THIS UNIT
- **scenes — High:** `test_schema_errors` **70,93–94,98–99** and `test_semantic_errors` **127,129** reach list leaves, but `mutate` **60** indexes lists with strings, raising `TypeError`. **Medium:** schema row **77** incorrectly tests semantic range ordering. Required-field deletion rows are missing for root fields, scene fields, and `turn.ovi/text`; only conditional teaching-treatment deletion is covered (**63–103**). Semantic rows **127,129** replace core lines, also causing missing-core-line failures; **129** can pass on that collateral diagnostic instead of detecting duplicate use.

## HAIKU FINDINGS FOR THIS UNIT
(1) Lines 70 and 98 target "scenes/0" (a list index). mutate() does cur["0"] on a list, which raises TypeError. (3) No test shows that a story scene carrying teaching_treatment is rejected; the comment at line 102 leaves it untested. (5) No required-field deletion rows for adhyay, scenes, scene_id, section_kind, ovi_range, goal, turn, line_ids, turn.ovi or turn.text; no root extra-key row.

## UNIT SPEC (binding)
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



## YOUR PREVIOUS tests/test_stage1_scenes.py (repair it)
```python
from __future__ import annotations
import copy
import json
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "pipeline" / "stage1"))
import scenes as M  # type: ignore

def base() -> tuple[dict, dict]:
    docs = {
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
    """Set or delete a single key in a nested dict/list. path like 'scenes/0/section_kind'."""
    parts = path.split("/")
    cur = obj
    for p in parts[:-1]:
        cur = cur[int(p)] if p.isdigit() else cur[p]
    key = parts[-1]
    if value is None:
        cur.pop(key, None)
    else:
        cur[key] = value

# ---------- Schema tests ----------
@pytest.mark.parametrize("path,value,keyword", [
    # adhyay
    ("adhyay", 0, "adhyay"),
    ("adhyay", 22, "adhyay"),
    ("adhyay", "1", "adhyay"),
    # scenes array
    ("scenes", "not-array", "scenes"),
    ("scenes/0", "not-obj", "scenes"),
    # scene_id pattern
    ("scenes/0/scene_id", "X1", "scene_id"),
    ("scenes/0/scene_id", "S100", "scene_id"),
    # section_kind enum
    ("scenes/0/section_kind", "invalid", "section_kind"),
    # ovi_range
    ("scenes/0/ovi_range", [5, 1], "ovi_range"),
    ("scenes/0/ovi_range", [1], "ovi_range"),
    ("scenes/0/ovi_range", [1, 5, 9], "ovi_range"),
    ("scenes/0/ovi_range", ["1", 5], "ovi_range"),
    # goal required string
    ("scenes/0/goal", "", "goal"),
    ("scenes/0/goal", 123, "goal"),
    # turn
    ("scenes/0/turn", "x", "turn"),
    ("scenes/0/turn/ovi", 0, "ovi"),
    ("scenes/0/turn/ovi", "3", "ovi"),
    ("scenes/0/turn/text", "", "text"),
    ("scenes/0/turn/text", 123, "text"),
    ("scenes/0/turn/text", "x" * 401, "text"),
    # line_ids
    ("scenes/0/line_ids", "x", "line_ids"),
    ("scenes/0/line_ids/0", 123, "line_ids"),
    ("scenes/0/line_ids/0", "bad-id", "line_ids"),
    # teaching_treatment enum
    ("scenes/1/teaching_treatment", "bad", "teaching_treatment"),
    # extra keys on nested objects
    ("scenes/0", {"extra": 1}, "extra"),
    ("scenes/0/turn", {"extra": 1}, "extra"),
    # teaching_treatment presence rules (schema level: discourse requires it)
    ("scenes/1/teaching_treatment", None, "teaching_treatment"),
    # story must not have teaching_treatment (or must be none) - schema allows none, semantic checks rest
])
def test_schema_errors(path, value, keyword):
    docs, ctx = base()
    mutate(docs["scenes"], path, value)
    errs = M.schema_errors(docs["scenes"])
    assert any(keyword in e for e in errs), f"missing {keyword} in {errs}"

# ---------- Semantic tests ----------
@pytest.mark.parametrize("path,value,keyword", [
    # duplicate scene_id
    ("scenes/1/scene_id", "S1", "S1"),
    # ovi_range lo > hi
    ("scenes/0/ovi_range", [5, 1], "S1"),
    # overlapping ranges
    ("scenes/1/ovi_range", [4, 9], "S2"),
    # chapter ovi not covered (ovi 9 missing)
    ("scenes/1/ovi_range", [6, 8], "9"),
    # unfilmed ovi inside range
    ("scenes/0/ovi_range", [1, 5], "S1"),  # will add unfilmed 3 in ctx
    # ovi outside chapter (ovi 10)
    ("scenes/1/ovi_range", [6, 10], "10"),
    # turn ovi outside range
    ("scenes/0/turn/ovi", 6, "S1"),
    # line_id not in script
    ("scenes/0/line_ids/0", "S9-L1", "S9-L1"),
    # duplicate line_id across scenes
    ("scenes/1/line_ids/0", "S1-L1", "S1-L1"),
    # line_ids not in script order within scene
    ("scenes/0/line_ids", ["S1-L2", "S1-L1"], "S1"),
    # core line not in any scene
    ("scenes/0/line_ids", ["S1-L2"], "S1-L1"),
    # discourse scene missing teaching_treatment (semantic: must not be none)
    ("scenes/1/teaching_treatment", "none", "S2"),
    # adhyay mismatch
    ("adhyay", 2, "adhyay"),
])
def test_semantic_errors(path, value, keyword):
    docs, ctx = base()
    # special handling for unfilmed ovi test
    if path == "scenes/0/ovi_range" and value == [1, 5] and keyword == "S1":
        ctx = copy.deepcopy(ctx)
        ctx["unfilmed_ovis"] = [3]
    else:
        ctx = copy.deepcopy(ctx)
    mutate(docs["scenes"], path, value)
    errs = M.validate(1, docs["scenes"], docs, ctx)
    assert any(keyword in e for e in errs), f"missing {keyword} in {errs}"

# ---------- Positive ----------
def test_valid():
    docs, ctx = base()
    assert M.schema_errors(docs["scenes"]) == []
    assert M.validate(1, docs["scenes"], docs, ctx) == []

```
