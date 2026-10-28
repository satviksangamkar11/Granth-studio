# FIX CALL: return BOTH files in full: `scripts/pipeline/stage1/questions.py` and `tests/test_stage1_questions.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
.........................                                                [100%]
25 passed in 0.04s

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
        if not isinstance(qid, str):
            continue
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
        if not isinstance(scene_id, str):
            continue
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
    # unhashable id (list)
    doc = {"adhyay": 1, "questions": [{"id": ["Q1"], "text": "t"}]}
    errs = validate(1, doc, base()["docs"], base()["ctx"])
    assert isinstance(errs, list)
    # unhashable scene_id (list)
    doc = {"adhyay": 1, "questions": [{"id": "Q1", "text": "t", "scene_id": ["S1"]}]}
    errs = validate(1, doc, base()["docs"], base()["ctx"])
    assert isinstance(errs, list)

```

## ROUND 9 FINDINGS: TESTS ONLY. The module must be returned UNCHANGED, character for character (unless one of your new rows proves a real module defect against the SPEC; then fix the module and say so in no prose). Add data rows to the existing tables (schema-valid rows for each enum value; schema-invalid rows for each bound/minLength) so that removing that schema rule fails a test. Keep every existing test and every assertion 'not any("malformed structure" in e ...)' unchanged. Only the items listed for YOUR unit 'questions' in the report below apply; if there are none for 'questions', return both files unchanged. Return BOTH complete FILE blocks.
### Haiku round 9 (use only the section for questions)
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
