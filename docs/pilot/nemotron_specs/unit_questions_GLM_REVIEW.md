# GLM 5.3 REVIEW CALL for Stage 1 unit `questions`. Write ONE markdown file: `reviews/glm_review_questions.md` (the ONLY file; no code files).
You are the senior reviewer of this unit. Inputs below: the UNIT SPEC (the only authority), the current MODULE, the current TESTS, and the real pytest output. Review both files against the spec and produce CORRECTION INSTRUCTIONS for the coder, in this exact structure:
# GLM review: questions
## Verdict: READY | FIX FIRST   (READY only if every pytest test passes AND every rule below is covered AND no defect is listed)
## Spec rules: for each schema rule, enum, conditional (if/then), required field, extra-key rule and each semantic rule of the unit spec, one line: `rule | module implements it (yes/no, line) | isolated failing test exists (yes/no, test name) | notes`.
## Defects in the MODULE: numbered, each with the exact change to make (function, what to add/remove) or `none`.
## Defects in the TESTS: numbered, each with the test name and exact change (no-op mutation, collateral failure, wording not quoted in the spec, wrong schema/semantic level, missing row, assertion that can never fail) or `none`.
## Failing tests: for each failing pytest test say whether the TEST or the MODULE is wrong according to the spec and give the fix.
Be precise and short; only real, verified defects; do not rewrite files.

## PYTEST OUTPUT
```
..............                                                           [100%]
14 passed in 0.03s

```

## UNIT SPEC (authority)
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



## MODULE scripts/pipeline/stage1/questions.py
```python
from __future__ import annotations

import json
import re
from typing import Any

import jsonschema
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

    # adhyay check
    doc_adhyay = doc.get("adhyay")
    if doc_adhyay != adhyay:
        messages.append(f"questions adhyay {doc_adhyay} does not match {adhyay}")

    questions = doc.get("questions", [])
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
    scenes_doc = docs.get("scenes", {})
    scene_ids: set[str] = set()
    for sc in scenes_doc.get("scenes", []):
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

## TESTS tests/test_stage1_questions.py
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
])
def test_schema_errors_format(path, value, field):
    doc = set_at(base(), path, value)
    errs = schema_errors(doc["docs"]["questions"])
    assert any(field in e for e in errs)


def test_validate_ok():
    doc = base()
    errs = validate(1, doc["docs"]["questions"], doc["docs"], doc["ctx"])
    assert errs == []


def test_validate_adhyay_mismatch():
    doc = set_at(base(), ["docs", "questions", "adhyay"], 2)
    errs = validate(1, doc["docs"]["questions"], doc["docs"], doc["ctx"])
    assert any("does not match" in e for e in errs)


def test_validate_duplicate_id():
    dup = {"id": "Q1", "text": "duplicate?", "scene_id": "S1"}
    doc = append_at(base(), ["docs", "questions", "questions"], dup)
    errs = validate(1, doc["docs"]["questions"], doc["docs"], doc["ctx"])
    assert any("Q1" in e for e in errs)


def test_validate_scene_missing():
    doc = set_at(base(), ["docs", "questions", "questions", 0, "scene_id"], "S99")
    errs = validate(1, doc["docs"]["questions"], doc["docs"], doc["ctx"])
    assert any("Q1" in e and "scene" in e for e in errs)

```
