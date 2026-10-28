# FIX CALL: return BOTH files in full: `scripts/pipeline/stage1/questions.py` and `tests/test_stage1_questions.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
.........................                                                [100%]
25 passed in 0.05s

```

## SPEC
# UNIT SPEC: Stage 1 document `questions` (schema `stage1_questions`)
This is ONE unit of the Stage 1 contract (the master spec `stage1_v2.md` was split because one big spec gave unreliable tests). Keep the unit small and exact.
Module: `scripts/pipeline/stage1/questions.py`. Tests: `tests/test_stage1_questions.py`. Style: `from __future__ import annotations`, standard library plus `jsonschema`; no print, no network, nothing at import time; tests use only the BASE data below and `tmp_path`; the test file loads the module by path with importlib (`ROOT = Path(__file__).resolve().parents[1]`, `ROOT / "scripts" / "pipeline" / "stage1" / "questions.py"`).

## Module API (exactly this)
- `SCHEMA`: dict, JSON Schema draft 2020-12 for the document, `additionalProperties: false` on EVERY object (nested too), `$schema` = "https://json-schema.org/draft/2020-12/schema", `title` = "stage1_questions".
- `schema_errors(doc) -> list[str]`: one message per jsonschema error, formatted "questions <path>: <message>" (path joined by "/", "doc" when empty).
- `validate(adhyay, doc, docs, ctx) -> list[str]`: SEMANTIC checks only (the schema has already passed; it must still never raise on odd data). `docs` is a dict of ALL nine documents (key names: story_map, coverage, scenes, shots, briefs, looks, voices, sounds, questions; a missing one counts as empty), `ctx` the context dict (keys: script_line_ids list, core_line_ids set, chapter_ovis set, unfilmed_ovis set, preset_ids set, sound_ids set, saved_voices dict voice_key->voice_id, speaking_characters set, known_states dict entity_id->set of state ids). Lists in ctx may arrive as lists or sets: convert with set(). Notes (messages that start with "note: ") come AFTER error messages. Include the adhyay check first: "questions adhyay <n> does not match <adhyay>".

## Ids and common types
scene_id `^S[0-9]{1,2}$`; shot_id `^S[0-9]{1,2}-[0-9]{1,2}$`; line_id `^S[0-9]{1,2}-L[0-9]{1,3}$`; image id (Stage 1 brief) `^s[0-9]{1,2}_[a-z][a-z0-9_]{0,40}$`; ovi = integer >= 1; adhyay = integer 1..21; text = string 1..400 chars; preset id = string matching `^[0-9]{2}_[a-z0-9_]+$`; sound id `^(bed|fx)_[a-z0-9_]+$`.

## The document shape (from the master spec)
9. `stage1_questions`: `questions`: array of {id `^Q[0-9]+$`, text, scene_id (optional)}.

## Semantic rules of this unit (master spec step 11)
11. questions: ids unique; scene exists if given.

Messages: tests assert only the quoted keywords/phrases of the rules plus the item id; for rules without a quoted phrase the message is `<item id>: <condition in plain words>`.

## BASE data (valid, note-free; the baseline for EVERY test; `validate(1, BASE_DOCS["questions"], BASE_DOCS, CTX)` must return [] and `schema_errors` must return [])
File `docs/pilot/nemotron_specs/stage1_base.json` has the keys "docs" (the nine documents) and "ctx". The test file must embed its own copy of what it needs as Python literals (copy the values below exactly):
```json
{
 "docs": {
  "questions": {
   "adhyay": 1,
   "questions": [
    {
     "id": "Q1",
     "text": "Which hand holds the gourd?",
     "scene_id": "S1"
    }
   ]
  },
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



## CURRENT MODULE scripts/pipeline/stage1/questions.py
```python
from __future__ import annotations

from typing import Any

from jsonschema import Draft202012Validator

SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "stage1_questions",
    "type": "object",
    "additionalProperties": False,
    "required": ["adhyay", "questions"],
    "properties": {
        "adhyay": {"type": "integer", "minimum": 1, "maximum": 21},
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["id", "text"],
                "properties": {
                    "id": {"type": "string", "pattern": "^Q[0-9]+$"},
                    "text": {"type": "string", "minLength": 1, "maxLength": 400},
                    "scene_id": {"type": "string", "pattern": "^S[0-9]{1,2}$"},
                },
            },
        },
    },
}

_validator = Draft202012Validator(SCHEMA)


def schema_errors(doc: Any) -> list[str]:
    errors: list[str] = []
    for err in _validator.iter_errors(doc):
        path = "/".join(str(p) for p in err.path) if err.path else "doc"
        errors.append(f"questions {path}: {err.message}")
    return errors


def validate(adhyay: int, doc: dict[str, Any], docs: dict[str, Any], ctx: dict[str, Any]) -> list[str]:
    messages: list[str] = []

    # adhyay check first
    doc_adhyay = doc.get("adhyay") if isinstance(doc, dict) else None
    if doc_adhyay != adhyay:
        messages.append(f"questions adhyay {doc_adhyay} does not match {adhyay}")

    questions = doc.get("questions", []) if isinstance(doc, dict) else []
    if not isinstance(questions, list):
        return messages

    # unique ids
    seen_ids: set[str] = set()
    for q in questions:
        if not isinstance(q, dict):
            continue
        qid = q.get("id")
        if qid in seen_ids:
            messages.append(f"{qid}: duplicate question id")
        seen_ids.add(qid)

    # scene exists if given
    scenes_doc = docs.get("scenes", {}) if isinstance(docs, dict) else {}
    if not isinstance(scenes_doc, dict):
        scenes_doc = {}
    raw_scenes = scenes_doc.get("scenes", [])
    if not isinstance(raw_scenes, list):
        raw_scenes = []

    scene_ids: set[str] = set()
    for sc in raw_scenes:
        if isinstance(sc, dict):
            sid = sc.get("scene_id")
            if isinstance(sid, str):
                scene_ids.add(sid)

    for q in questions:
        if not isinstance(q, dict):
            continue
        qid = q.get("id")
        scene_id = q.get("scene_id")
        if scene_id and scene_id not in scene_ids:
            messages.append(f"{qid}: scene_id '{scene_id}' does not exist")

    return messages

```

## CURRENT TESTS tests/test_stage1_questions.py
```python
import copy
import importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "pipeline" / "stage1" / "questions.py"
spec = importlib.util.spec_from_file_location("questions", MODULE_PATH)
questions = importlib.util.module_from_spec(spec)
spec.loader.exec_module(questions)

SCHEMA = questions.SCHEMA
schema_errors = questions.schema_errors
validate = questions.validate


def base():
    return {
        "docs": {
            "questions": {
                "adhyay": 1,
                "questions": [
                    {"id": "Q1", "text": "Which hand holds the gourd?", "scene_id": "S1"}
                ],
            },
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
        },
        "ctx": {
            "script_line_ids": ["S1-L1", "S1-L2", "S2-L1"],
            "core_line_ids": ["S1-L1", "S2-L1"],
            "chapter_ovis": [1, 2, 3, 4, 5, 6, 7, 8, 9],
            "unfilmed_ovis": [],
            "preset_ids": ["01_establishing_shot", "03_slow_cinematic_push"],
            "sound_ids": ["bed_roadside_quiet", "fx_door_wood_creak"],
            "saved_voices": {"narrator": "CXkeo30p0Sk4Lr0TAzeo", "gajanan": "8fqGzH80bdkm2UseeV9f"},
            "speaking_characters": ["narrator", "gajanan_maharaj"],
            "known_states": {"gajanan_maharaj": ["adult_youth_v1"]},
        },
    }


def get_parent(doc, path):
    cur = doc
    for p in path[:-1]:
        cur = cur[int(p)] if isinstance(cur, list) else cur[p]
    return cur, path[-1]


def set_at(base, path, value):
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    if isinstance(parent, list):
        parent[int(key)] = value
    else:
        parent[key] = value
    assert doc != base
    return doc


def delete_at(base, path):
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    if isinstance(parent, list):
        del parent[int(key)]
    else:
        del parent[key]
    assert doc != base
    return doc


def append_at(base, path, value):
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    target = parent[key] if isinstance(parent, dict) else parent[int(key)]
    assert isinstance(target, list)
    target.append(value)
    assert doc != base
    return doc


@pytest.mark.parametrize("path,field", [
    (["docs", "questions", "adhyay"], "adhyay"),
    (["docs", "questions", "questions"], "questions"),
    (["docs", "questions", "questions", 0, "id"], "id"),
    (["docs", "questions", "questions", 0, "text"], "text"),
])
def test_schema_errors_required(path, field):
    doc = delete_at(base(), path)
    errs = schema_errors(doc["docs"]["questions"])
    assert any(field in e for e in errs)


@pytest.mark.parametrize("path,value,field", [
    (["docs", "questions", "questions", 0, "id"], "X1", "id"),
    (["docs", "questions", "questions", 0, "text"], "", "text"),
    (["docs", "questions", "questions", 0, "text"], "x" * 401, "text"),
    (["docs", "questions", "questions", 0, "scene_id"], "X1", "scene_id"),
    (["docs", "questions", "questions", 0, "extra"], "bad", "extra"),
    (["docs", "questions", "extra"], "bad", "extra"),
    (["docs", "questions", "adhyay"], 0, "adhyay"),
    (["docs", "questions", "adhyay"], 22, "adhyay"),
    (["docs", "questions", "adhyay"], "not-int", "adhyay"),
])
def test_schema_errors_format(path, value, field):
    doc = set_at(base(), path, value)
    errs = schema_errors(doc["docs"]["questions"])
    assert any(field in e for e in errs)


def test_schema_baseline_valid():
    errs = schema_errors(base()["docs"]["questions"])
    assert errs == []


def test_schema_scene_id_optional():
    doc = delete_at(base(), ["docs", "questions", "questions", 0, "scene_id"])
    errs = schema_errors(doc["docs"]["questions"])
    assert errs == []
    val_errs = validate(1, doc["docs"]["questions"], doc["docs"], doc["ctx"])
    assert val_errs == []


def test_schema_errors_message_format():
    # empty path -> "questions doc: "
    errs = schema_errors([])
    assert len(errs) == 1
    assert errs[0].startswith("questions doc: ")
    # mutated doc -> path fragment appears
    doc = set_at(base(), ["docs", "questions", "questions", 0, "id"], "X1")
    errs = schema_errors(doc["docs"]["questions"])
    assert any("questions/0/id" in e for e in errs)


def test_schema_non_array_questions():
    doc = set_at(base(), ["docs", "questions", "questions"], {})
    errs = schema_errors(doc["docs"]["questions"])
    assert any("questions" in e for e in errs)


def test_schema_non_dict_item():
    doc = append_at(base(), ["docs", "questions", "questions"], "not-a-dict")
    errs = schema_errors(doc["docs"]["questions"])
    assert any("questions" in e for e in errs)


def test_validate_ok():
    doc = base()
    errs = validate(1, doc["docs"]["questions"], doc["docs"], doc["ctx"])
    assert errs == []


def test_validate_adhyay_mismatch():
    doc = set_at(base(), ["docs", "questions", "adhyay"], 2)
    errs = validate(1, doc["docs"]["questions"], doc["docs"], doc["ctx"])
    assert any("does not match" in e for e in errs)


def test_validate_adhyay_check_first():
    # both adhyay mismatch and duplicate id -> adhyay message first
    dup = {"id": "Q1", "text": "duplicate?", "scene_id": "S1"}
    doc = append_at(base(), ["docs", "questions", "questions"], dup)
    doc = set_at(doc, ["docs", "questions", "adhyay"], 2)
    errs = validate(1, doc["docs"]["questions"], doc["docs"], doc["ctx"])
    assert errs[0].startswith("questions adhyay")


def test_validate_duplicate_id():
    dup = {"id": "Q1", "text": "duplicate?", "scene_id": "S1"}
    doc = append_at(base(), ["docs", "questions", "questions"], dup)
    errs = validate(1, doc["docs"]["questions"], doc["docs"], doc["ctx"])
    assert any("Q1" in e for e in errs)


def test_validate_scene_missing():
    doc = set_at(base(), ["docs", "questions", "questions", 0, "scene_id"], "S99")
    errs = validate(1, doc["docs"]["questions"], doc["docs"], doc["ctx"])
    assert any("Q1" in e for e in errs)


def test_validate_missing_scenes_doc():
    # missing scenes key counts as empty -> scene_id S1 no longer resolves
    doc = delete_at(base(), ["docs", "scenes"])
    errs = validate(1, doc["docs"]["questions"], doc["docs"], doc["ctx"])
    assert any("Q1" in e for e in errs)


def test_validate_odd_data_no_raise():
    # docs not a dict
    errs = validate(1, base()["docs"]["questions"], None, base()["ctx"])
    assert isinstance(errs, list)
    # scenes not a dict
    errs = validate(1, base()["docs"]["questions"], {"scenes": "not-a-dict"}, base()["ctx"])
    assert isinstance(errs, list)
    # scenes list not a list
    errs = validate(1, base()["docs"]["questions"], {"scenes": {"scenes": "not-a-list"}}, base()["ctx"])
    assert isinstance(errs, list)
    # doc not a dict
    errs = validate(1, "not-a-dict", base()["docs"], base()["ctx"])
    assert isinstance(errs, list)

```

## REVIEW FINDINGS to fix (Codex medium reproduced its items; Haiku low findings are unverified, apply only those the SPEC supports).
Fix rule for crashes: validate() and schema_errors() must NEVER raise on any JSON-shaped input (None, wrong type, non-hashable id, null list entries): return errors instead. Add one isolated regression test per crash. Replace unquoted-wording assertions by asserting the offending item id/field. Keep every existing passing test passing.
### Codex
## Verdict: FIX FIRST

### story_map

1. **High —** [story_map.py:81](</D:/aai work/granthstudio/scripts/pipeline/stage1/story_map.py:81>): `ovi_types: [null]` raises `AttributeError`. Check item types before reading them and return errors for malformed entries.
2. **Low —** [test_stage1_story_map.py:153](</D:/aai work/granthstudio/tests/test_stage1_story_map.py:153>): The tests require `lo > hi`, `key_ovi`, and `outside`, which the spec does not quote. Assert the event ID instead.

### coverage

1. **High —** [coverage.py:88](</D:/aai work/granthstudio/scripts/pipeline/stage1/coverage.py:88>): `ovis: [null]` raises `AttributeError`. Check entry types and return errors.

### scenes

1. **High —** [scenes.py:54](</D:/aai work/granthstudio/scripts/pipeline/stage1/scenes.py:54>): The schema rejects `teaching_treatment: "none"` for a story scene, although the spec permits it. Allow the field when its value is `"none"` and add a positive test.
2. **High —** [scenes.py:138](</D:/aai work/granthstudio/scripts/pipeline/stage1/scenes.py:138>): A range such as `["a", 2]` with turn ovi `1` raises `TypeError`. Validate both endpoints before comparing them with the turn.
3. **Low —** [test_stage1_scenes.py:188](</D:/aai work/granthstudio/tests/test_stage1_scenes.py:188>): The forbidden story treatment has no isolated schema test. Test that non-`"none"` treatment is rejected by `schema_errors`.

### shots

1. **High —** [shots.py:166](</D:/aai work/granthstudio/scripts/pipeline/stage1/shots.py:166>): `shots: [null]` raises `AttributeError` during the scene coverage check. Filter or type-check entries consistently throughout validation.
2. **High —** [shots.py:48](</D:/aai work/granthstudio/scripts/pipeline/stage1/shots.py:48>): The schema accepts any string as a preset, including `"bogus"`. Restrict it to the specified preset ID pattern or `"NEED_NEW"`.
3. **Low —** [test_stage1_shots.py:169](</D:/aai work/granthstudio/tests/test_stage1_shots.py:169>): The invalid `class` case fails because an object is forbidden for the existing preset, even if the class enum is removed. Set `preset` to `"NEED_NEW"` before testing the enum.

### briefs

1. **High —** [briefs.py:139](</D:/aai work/granthstudio/scripts/pipeline/stage1/briefs.py:139>): A nonempty list as `image_id` raises `TypeError` during set membership. Check the ID type before using it as a set key.
2. **High —** [briefs.py:63](</D:/aai work/granthstudio/scripts/pipeline/stage1/briefs.py:63>): `prop` and `prop_state` accept empty strings, but the spec defines text as 1–400 characters. Add `minLength: 1` and isolated tests.
3. **Low —** [test_stage1_briefs.py:263](</D:/aai work/granthstudio/tests/test_stage1_briefs.py:263>): Semantic tests assert phrases such as `unique with scene prefix` that the spec does not quote. Assert the item ID for these rules.

### looks

None.

### voices

1. **High —** [voices.py:66](</D:/aai work/granthstudio/scripts/pipeline/stage1/voices.py:66>): `cast: [1]` raises `AttributeError`. Check entry types and return errors.
2. **High —** [voices.py:76](</D:/aai work/granthstudio/scripts/pipeline/stage1/voices.py:76>): Two `NEW_PROPOSED` entries for a speaking character do not trigger the exactly-one-entry rule. A recurring character outside `speaking_characters` is also not checked for duplicates. Check counts independently of status and check recurring duplicates across the entire cast.
3. **High —** [voices.py:109](</D:/aai work/granthstudio/scripts/pipeline/stage1/voices.py:109>): If narrator and two other characters share a key, the narrator suppresses the error for the other pair. Check sharing between distinct non-narrator characters.
4. **Low —** [test_stage1_voices.py:180](</D:/aai work/granthstudio/tests/test_stage1_voices.py:180>): Tests assert unquoted wording such as `recurring character listed twice`. Assert the character ID and add isolated cases for the duplicate and sharing rules above.

### sounds

1. **High —** [sounds.py:98](</D:/aai work/granthstudio/scripts/pipeline/stage1/sounds.py:98>): A cue with a valid scene but missing `sound_id` raises `AttributeError`. Check that the ID is a string before calling `startswith`.
2. **Low —** [test_stage1_sounds.py:178](</D:/aai work/granthstudio/tests/test_stage1_sounds.py:178>): Tests assert unquoted wording such as `scene exists`. Assert the cue ID for rules without quoted messages.

### questions

1. **High —** [questions.py:60](</D:/aai work/granthstudio/scripts/pipeline/stage1/questions.py:60>): The odd-document fix is incomplete: `questions: [{"id": []}]` raises `TypeError` during set membership. Type-check IDs and scene IDs before set operations; add regression cases.

The semantic crash cases were reproduced with the available Python interpreter and a stub for `jsonschema`. I could not rerun the project tests: the sandbox denied launching the virtual-environment interpreter. I did not independently verify the reported green test run.### Haiku
# Stage 1 unit modules: review (read-only)

Scope: `scripts/pipeline/stage1/{story_map,coverage,scenes,shots,briefs,looks,voices,sounds,questions}.py` and `tests/test_stage1_<unit>.py`, against `docs/pilot/nemotron_specs/unit_<unit>.md`, `stage1_base.json` and `STAGE1_RULES.md`.

Evidence: `uv run pytest -q --tb=short tests/test_stage1_*.py` gives 333 passed. Raises and misses below were reproduced by calling the modules in memory (no files written, no network). No print, env, key or secret handling was found in any module or test.

## Verdict: FIX FIRST

---

## story_map

Module `scripts/pipeline/stage1/story_map.py`

1. L70, L81-83, L106-116: `validate` raises on odd data. `doc` not a dict, an `ovi_types` item not a dict, or `ovi_range` holding non-ints gives AttributeError/TypeError (reproduced: `ovi_types: [1]` and `ovi_range: ["a", 5]`). Fix: return early if `doc` is not a dict; skip non-dict items; before `lo > hi` (L108) and `kovi < lo` (L115) require `isinstance(lo, int) and isinstance(hi, int)`; require `isinstance(ovi, int)` before L82.

Tests `tests/test_stage1_story_map.py`

2. L153 and L155: assert `"lo > hi"`, `"key_ovi"`, `"outside"`. The spec quotes none of these (class 4). Fix: assert `"E1"` only.
3. L155 (`key_ovis` below range): the `kovi < lo` branch has no failing test; removing it passes the suite (class 3). Fix: add row `(1, [(["events", 0, "key_ovis"], [0])], ["E1"])`.

## coverage

Module `scripts/pipeline/stage1/coverage.py`

1. L74, L85-88, L94, L103: `validate` raises. `doc` not a dict or `ovis` items not dicts gives AttributeError (reproduced: `ovis: ["x"]`); an unhashable `ovi` (list) gives TypeError at `ovi not in ovi_dispositions` (reproduced). Fix: return early if `doc` is not a dict; if `ovis` is not a list use `[]`; skip non-dict entries; skip entries whose `ovi` is not an int before using it as a key.

Tests: none.

## scenes

Module `scripts/pipeline/stage1/scenes.py`

1. L155-157: out-of-order check is lost after an unknown line id. `prev_idx` is set to -1 for a line not in the script, so `['S1-L2','S9-L9','S1-L1']` reports only `S9-L9` and misses the order error (reproduced; class 1). Fix: update `prev_idx` only when `idx != -1`, and compare only in that case.
2. L136-138: `turn` check raises when `ovi_range` bounds are not ints (reproduced: `ovi_range: ["1", 5]`, turn ovi 3 gives TypeError). Fix: check `isinstance(lo, int) and isinstance(hi, int)` before `lo <= turn_ovi <= hi`.
3. L116, L145, L147: unhashable `scene_id` or `line_id` raises TypeError (reproduced with `scene_id: ["S1"]`). Fix: skip or report non-string ids before set membership.
4. L59-61 (schema, story `then`): `teaching_treatment: "none"` is rejected for story scenes. The spec says "must be absent or none for story"; `validate` L164 accepts it, so schema and semantics disagree (reproduced). Fix: replace the story `then` with `{"properties": {"teaching_treatment": {"const": "none"}}}`.

Tests `tests/test_stage1_scenes.py`

5. L165-167 (duplicate scene id): the case passes with the duplicate-id rule removed, because `"S1"` also matches `"S1-L1: line used in multiple scenes"` and `"S1: ovi_range overlaps with S1"` (both reproduced). Fix: assert `"duplicate scene id"` in errs.

## shots

Module `scripts/pipeline/stage1/shots.py`

1. L131-133: `continue` for a shot whose scene is missing skips the preset check (L154-155). Reproduced: shot `S9-1` with preset `bogus` and no scene S9 reports only `scene S9 does not exist`; the spec requires `preset` to be in `preset_ids` or NEED_NEW for every shot. Fix: run the preset check (and beat coverage, L147-150) before the `continue`.
2. L96, L99, L118, L131, L139-142: raises on odd data. `docs["scenes"]` not a dict gives AttributeError (reproduced); unhashable `scene_id` or `shot_id` gives TypeError (reproduced); scene `ovi_range` that is not a 2-int list gives TypeError. Fix: type-guard `docs["scenes"]`, scenes, shots, ids and bounds before use.
3. L48 (schema): `preset` is any string. The spec's preset id pattern `^[0-9]{2}_[a-z0-9_]+$` (or the exact string NEED_NEW) is not enforced. Fix: `"preset": {"type": "string", "pattern": "^([0-9]{2}_[a-z0-9_]+|NEED_NEW)$"}`.

Tests `tests/test_stage1_shots.py`

4. L263-267 (`test_every_scene_has_shots`): the assertion `"S2" in e` also matches `"S2-L1: line is in no shot beat"`, so the test passes without the "scene has no shots" rule (reproduced messages: `['S2: scene has no shots', 'S2-L1: line is in no shot beat']`). Fix: assert `"scene has no shots"` in errs.
5. L243: asserts `"consecutive"`, which the spec does not quote (class 4). Fix: assert `"S1"` and the item id only.
6. L169 (`test_shot_field_types_and_formats`): the `need_new` row with class `bad_class` uses a non-NEED_NEW preset, so the error comes from the `else` branch and the class enum is never exercised (class 3). Fix: set `preset` to `"NEED_NEW"` first, as `test_need_new_class_enum` does.

## briefs

Module `scripts/pipeline/stage1/briefs.py`

1. L118, L127-128, L139, L145, L148, L157: non-string `scene_id`, `image_id` or `shot_id` raises. Reproduced: `scene_id: ["S1"]` gives TypeError; `image_id: 5` gives AttributeError at `.startswith`. Fix: type-guard these values with `isinstance(x, str)` before set, dict and regex use.

Schema `briefs.py`

2. L55-58, L62, L65-67, L79-80: the spec's common type `text = string 1..400 chars` is not enforced. `people.position/pose/gaze`, `camera`, `light`, `reason_new`, `place_id`, `references.place` and `references.style_anchor` have no 1..400 bounds. Reproduced: `pose: ""` gives no schema error. Fix: add `"minLength": 1, "maxLength": 400` to each, and `"maxLength": 400` to `people.name`.

Tests `tests/test_stage1_briefs.py`

3. L263, L265, L267, L269, L271, L273, L275: asserts `"unique with scene prefix"`, `"scene exists"`, `"shot_ids exist and belong to the same scene"`, `"no empty name"` and `"non-empty"`. The spec quotes none of these (class 4). Fix: assert the item id only.

## looks

Module `scripts/pipeline/stage1/looks.py`: none.

Tests `tests/test_stage1_looks.py`: none.

## voices

Module `scripts/pipeline/stage1/voices.py`

1. L76-81: the spec's "every speaking_character has exactly one cast entry" is enforced only for RECURRING duplicates. Two non-RECURRING entries for one character pass silently (reproduced: two NEW_PROPOSED entries for `a` with keys `narrator` and `gajanan` return `[]`). Fix: for any `len(entries) > 1` add `f"{char}: listed more than once"`, and keep the RECURRING branch.
2. L59, L63-69, L84-104: raises on odd data. `cast` None gives TypeError (reproduced); non-dict entries give AttributeError; unhashable `character_id` or `voice_key` gives TypeError (reproduced). Fix: `cast = doc.get("cast")`; if not a list use `[]`; skip non-dict entries; type-guard `character_id` and `voice_key` as strings.

Tests `tests/test_stage1_voices.py`

3. L134-146 (schema): required fields are never tested by deletion. Every row sets the value to None, which only exercises the type rule, so removing `required` from SCHEMA passes the suite (class 3). Fix: add rows that delete `cast.0.character_id`, `cast.0.voice_key`, `cast.0.voice_id`, `cast.0.gender` and `cast.0.status`.
4. L180, L186, L192: asserts `"recurring character listed twice"` and `"voice key shared with another character"`, which the spec does not quote (class 4). Fix: assert the item id only (`"narrator"`, `"extra_char"`, `"char1"`).

## sounds

Module `scripts/pipeline/stage1/sounds.py`

1. L98: `sound_id.startswith` raises AttributeError when a cue lacks `sound_id` or it is not a string (reproduced). Also L62-63, L67-68, L75 and L81 raise on non-dict scenes or cues, or unhashable `scene_id`. Fix: guard `sound_id` with `isinstance(sound_id, str)` before L98, and skip non-dict cues and scenes.

Tests `tests/test_stage1_sounds.py`

2. L178, L180, L182, L184, L186 and L219: assert `"scene exists"`, `"anchor line belongs to the scene"`, `"sound_id in sound_ids or NEED_NEW"` and `"kind matches the id prefix"`, which the spec does not quote (class 4). Fix: assert `"cue[0]"` only.

## questions

Module `scripts/pipeline/stage1/questions.py`

1. L60, L62 and L84: the earlier fix guards non-dict `doc`, `docs` and `scenes` only. An unhashable `id` (L60) or `scene_id` (L84) still raises TypeError (reproduced with `id: ["Q1"]` and `scene_id: ["S1"]`). Fix: `if not isinstance(qid, str)` before L60, and `if not isinstance(scene_id, str)` before L84.

Tests `tests/test_stage1_questions.py`

2. L208-220 (`test_validate_odd_data_no_raise`): no case uses an unhashable `id` or `scene_id`, which is why defect 1 is not caught (class 3). Fix: add `{"id": ["Q1"], "text": "t"}` and `{"id": "Q1", "text": "t", "scene_id": ["S1"]}` cases asserting `isinstance(errs, list)`.

---

## Defects per unit

| Unit | Defects |
|---|---|
| story_map | 3 |
| coverage | 1 |
| scenes | 5 |
| shots | 6 |
| briefs | 3 |
| looks | 0 |
| voices | 4 |
| sounds | 2 |
| questions | 2 |
| Total | 26 |
