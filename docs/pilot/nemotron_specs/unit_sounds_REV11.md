# FIX CALL: return BOTH files in full: `scripts/pipeline/stage1/sounds.py` and `tests/test_stage1_sounds.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
.............................                                            [100%]
29 passed in 0.06s

```

## SPEC
# UNIT SPEC: Stage 1 document `sounds` (schema `stage1_sound_suggestions`)
This is ONE unit of the Stage 1 contract (the master spec `stage1_v2.md` was split because one big spec gave unreliable tests). Keep the unit small and exact.
Module: `scripts/pipeline/stage1/sounds.py`. Tests: `tests/test_stage1_sounds.py`. Style: `from __future__ import annotations`, standard library plus `jsonschema`; no print, no network, nothing at import time; tests use only the BASE data below and `tmp_path`; the test file loads the module by path with importlib (`ROOT = Path(__file__).resolve().parents[1]`, `ROOT / "scripts" / "pipeline" / "stage1" / "sounds.py"`).

## Module API (exactly this)
- `SCHEMA`: dict, JSON Schema draft 2020-12 for the document, `additionalProperties: false` on EVERY object (nested too), `$schema` = "https://json-schema.org/draft/2020-12/schema", `title` = "stage1_sound_suggestions".
- `schema_errors(doc) -> list[str]`: one message per jsonschema error, formatted "sounds <path>: <message>" (path joined by "/", "doc" when empty).
- `validate(adhyay, doc, docs, ctx) -> list[str]`: SEMANTIC checks only (the schema has already passed; it must still never raise on odd data). `docs` is a dict of ALL nine documents (key names: story_map, coverage, scenes, shots, briefs, looks, voices, sounds, questions; a missing one counts as empty), `ctx` the context dict (keys: script_line_ids list, core_line_ids set, chapter_ovis set, unfilmed_ovis set, preset_ids set, sound_ids set, saved_voices dict voice_key->voice_id, speaking_characters set, known_states dict entity_id->set of state ids). Lists in ctx may arrive as lists or sets: convert with set(). Notes (messages that start with "note: ") come AFTER error messages. Include the adhyay check first: "sounds adhyay <n> does not match <adhyay>".

## Ids and common types
scene_id `^S[0-9]{1,2}$`; shot_id `^S[0-9]{1,2}-[0-9]{1,2}$`; line_id `^S[0-9]{1,2}-L[0-9]{1,3}$`; image id (Stage 1 brief) `^s[0-9]{1,2}_[a-z][a-z0-9_]{0,40}$`; ovi = integer >= 1; adhyay = integer 1..21; text = string 1..400 chars; preset id = string matching `^[0-9]{2}_[a-z0-9_]+$`; sound id `^(bed|fx)_[a-z0-9_]+$`.

## The document shape (from the master spec)
8. `stage1_sound_suggestions`: `cues`: array of {scene_id, anchor_line_id (line_id), sound_id (sound id OR the exact string NEED_NEW), kind: bed|fx, sound_prompt (text, REQUIRED when sound_id is NEED_NEW, else absent), purpose text, basis: stated|staging}. NO duration/loop/timing fields.

## Semantic rules of this unit (master spec step 10)
10. sounds: scene exists; anchor line belongs to the scene; sound_id in `sound_ids` or NEED_NEW; NEED_NEW needs sound_prompt (schema) — and a non-NEED_NEW cue must not carry sound_prompt; kind matches the id prefix.

Messages: tests assert only the quoted keywords/phrases of the rules plus the item id; for rules without a quoted phrase the message is `<item id>: <condition in plain words>`.

## BASE data (valid, note-free; the baseline for EVERY test; `validate(1, BASE_DOCS["sounds"], BASE_DOCS, CTX)` must return [] and `schema_errors` must return [])
File `docs/pilot/nemotron_specs/stage1_base.json` has the keys "docs" (the nine documents) and "ctx". The test file must embed its own copy of what it needs as Python literals (copy the values below exactly):
```json
{
 "docs": {
  "sounds": {
   "adhyay": 1,
   "cues": [
    {
     "scene_id": "S1",
     "anchor_line_id": "S1-L1",
     "sound_id": "bed_roadside_quiet",
     "kind": "bed",
     "purpose": "location bed",
     "basis": "staging"
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



## CURRENT MODULE scripts/pipeline/stage1/sounds.py
```python
from __future__ import annotations

import json
import re
from typing import Any

import jsonschema
from jsonschema import Draft202012Validator

SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "stage1_sound_suggestions",
    "type": "object",
    "additionalProperties": False,
    "required": ["adhyay", "cues"],
    "properties": {
        "adhyay": {"type": "integer", "minimum": 1, "maximum": 21},
        "cues": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["scene_id", "anchor_line_id", "sound_id", "kind", "purpose", "basis"],
                "properties": {
                    "scene_id": {"type": "string", "pattern": "^S[0-9]{1,2}$"},
                    "anchor_line_id": {"type": "string", "pattern": "^S[0-9]{1,2}-L[0-9]{1,3}$"},
                    "sound_id": {"type": "string", "pattern": "^(bed|fx)_[a-z0-9_]+$|^NEED_NEW$"},
                    "kind": {"type": "string", "enum": ["bed", "fx"]},
                    "sound_prompt": {"type": "string", "minLength": 1, "maxLength": 400},
                    "purpose": {"type": "string", "minLength": 1, "maxLength": 400},
                    "basis": {"type": "string", "enum": ["stated", "staging"]},
                },
                "if": {"properties": {"sound_id": {"const": "NEED_NEW"}}},
                "then": {"required": ["sound_prompt"]},
                "else": {"not": {"required": ["sound_prompt"]}},
            },
        },
    },
}

_validator = Draft202012Validator(SCHEMA)


def schema_errors(doc: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(doc, dict):
        errors.append("sounds doc: document must be an object")
        return errors
    for err in _validator.iter_errors(doc):
        path = "/".join(str(p) for p in err.path) if err.path else "doc"
        errors.append(f"sounds {path}: {err.message}")
    return errors


def _validate_semantic(adhyay: int, doc: dict[str, Any], docs: dict[str, Any], ctx: dict[str, Any]) -> list[str]:
    messages: list[str] = []

    # Adhyay check
    doc_adhyay = doc.get("adhyay")
    if doc_adhyay != adhyay:
        messages.append(f"sounds adhyay {doc_adhyay} does not match {adhyay}")

    # Prepare context sets
    sound_ids = set(ctx.get("sound_ids", [])) if isinstance(ctx.get("sound_ids"), (list, set)) else set()
    scenes_doc = docs.get("scenes", {})
    scenes_list = scenes_doc.get("scenes", []) if isinstance(scenes_doc, dict) else []

    # Build scene lookup
    scene_by_id: dict[str, dict[str, Any]] = {}
    if isinstance(scenes_list, list):
        for sc in scenes_list:
            if not isinstance(sc, dict):
                continue
            sid = sc.get("scene_id")
            if isinstance(sid, str):
                scene_by_id[sid] = sc

    cues = doc.get("cues", [])
    if not isinstance(cues, list):
        cues = []

    for i, cue in enumerate(cues):
        cue_id = f"cue[{i}]"
        if not isinstance(cue, dict):
            messages.append(f"{cue_id}: cue must be an object")
            continue

        scene_id = cue.get("scene_id")
        anchor_line_id = cue.get("anchor_line_id")
        sound_id = cue.get("sound_id")
        kind = cue.get("kind")

        # Scene exists
        if not isinstance(scene_id, str) or scene_id not in scene_by_id:
            messages.append(f"{cue_id}: scene does not exist")
            continue

        scene = scene_by_id[scene_id]

        # Anchor line belongs to the scene - filter for string line_ids
        if not isinstance(anchor_line_id, str):
            messages.append(f"{cue_id}: anchor_line_id must be a string")
        else:
            scene_line_ids_raw = scene.get("line_ids", [])
            scene_line_ids = set()
            if isinstance(scene_line_ids_raw, (list, set)):
                for lid in scene_line_ids_raw:
                    if isinstance(lid, str):
                        scene_line_ids.add(lid)
            if anchor_line_id not in scene_line_ids:
                messages.append(f"{cue_id}: anchor line not in scene")

        # sound_id in sound_ids or NEED_NEW
        if not isinstance(sound_id, str):
            messages.append(f"{cue_id}: sound_id must be a string")
        elif sound_id != "NEED_NEW" and sound_id not in sound_ids:
            messages.append(f"{cue_id}: sound_id not in sound_ids and not NEED_NEW")

        # kind matches the id prefix (only for non-NEED_NEW)
        if isinstance(sound_id, str) and sound_id != "NEED_NEW" and isinstance(kind, str):
            expected_kind = "bed" if sound_id.startswith("bed_") else "fx" if sound_id.startswith("fx_") else None
            if expected_kind and kind != expected_kind:
                messages.append(f"{cue_id}: kind does not match sound_id prefix")

    return messages


def validate(adhyay: int, doc: dict[str, Any], docs: dict[str, Any], ctx: dict[str, Any]) -> list[str]:
    # Guard: doc must be a dict
    if not isinstance(doc, dict):
        return ["sounds doc: document must be an object"]

    try:
        return _validate_semantic(adhyay, doc, docs, ctx)
    except (TypeError, AttributeError, KeyError, ValueError, IndexError):
        return ["sounds: malformed structure"]

```

## CURRENT TESTS tests/test_stage1_sounds.py
```python
from __future__ import annotations
import copy
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MOD_PATH = ROOT / "scripts" / "pipeline" / "stage1" / "sounds.py"
spec = importlib.util.spec_from_file_location("sounds", MOD_PATH)
sounds = importlib.util.module_from_spec(spec)
sys.modules["sounds"] = sounds
spec.loader.exec_module(sounds)

SCHEMA = sounds.SCHEMA
schema_errors = sounds.schema_errors
validate = sounds.validate


def _base_docs() -> dict:
    return {
        "sounds": {
            "adhyay": 1,
            "cues": [
                {
                    "scene_id": "S1",
                    "anchor_line_id": "S1-L1",
                    "sound_id": "bed_roadside_quiet",
                    "kind": "bed",
                    "purpose": "location bed",
                    "basis": "staging",
                }
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
    }


def _base_ctx() -> dict:
    return {
        "script_line_ids": ["S1-L1", "S1-L2", "S2-L1"],
        "core_line_ids": ["S1-L1", "S2-L1"],
        "chapter_ovis": [1, 2, 3, 4, 5, 6, 7, 8, 9],
        "unfilmed_ovis": [],
        "preset_ids": ["01_establishing_shot", "03_slow_cinematic_push"],
        "sound_ids": ["bed_roadside_quiet", "fx_door_wood_creak"],
        "saved_voices": {
            "narrator": "CXkeo30p0Sk4Lr0TAzeo",
            "gajanan": "8fqGzH80bdkm2UseeV9f",
        },
        "speaking_characters": ["narrator", "gajanan_maharaj"],
        "known_states": {"gajanan_maharaj": ["adult_youth_v1"]},
    }


def get_parent(doc: dict, path: list):
    cur = doc
    for part in path[:-1]:
        cur = cur[int(part)] if isinstance(part, int) else cur[part]
    return cur, path[-1]


def set_at(base: dict, path: list, value) -> dict:
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    if isinstance(parent, list):
        assert isinstance(key, int) and 0 <= key < len(parent), f"bad list index {key}"
        parent[key] = value
    else:
        parent[key] = value
    assert doc != base, "mutation did not change document"
    return doc


def delete_at(base: dict, path: list) -> dict:
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    if isinstance(parent, list):
        assert isinstance(key, int) and 0 <= key < len(parent), f"bad list index {key}"
        parent.pop(key)
    else:
        parent.pop(key, None)
    assert doc != base, "mutation did not change document"
    return doc


def append_at(base: dict, path: list, value) -> dict:
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    assert isinstance(parent, list) and key == "append", "append_at expects list parent and 'append' key"
    parent.append(value)
    assert doc != base, "mutation did not change document"
    return doc


def _valid_doc() -> dict:
    return copy.deepcopy(_base_docs()["sounds"])


def _valid_ctx() -> dict:
    return copy.deepcopy(_base_ctx())


def _other_docs() -> dict:
    return {k: v for k, v in _base_docs().items() if k != "sounds"}


# ---------- schema_errors tests ----------
@pytest.mark.parametrize(
    "mutate_fn,keyword",
    [
        # required root fields (deletion)
        (lambda d: delete_at(d, ["adhyay"]), "adhyay"),
        (lambda d: delete_at(d, ["cues"]), "cues"),
        # required cue fields (deletion)
        (lambda d: delete_at(d, ["cues", 0, "scene_id"]), "scene_id"),
        (lambda d: delete_at(d, ["cues", 0, "anchor_line_id"]), "anchor_line_id"),
        (lambda d: delete_at(d, ["cues", 0, "sound_id"]), "sound_id"),
        (lambda d: delete_at(d, ["cues", 0, "kind"]), "kind"),
        (lambda d: delete_at(d, ["cues", 0, "purpose"]), "purpose"),
        (lambda d: delete_at(d, ["cues", 0, "basis"]), "basis"),
        # type / pattern violations (set invalid value)
        (lambda d: set_at(d, ["adhyay"], "x"), "adhyay"),
        (lambda d: set_at(d, ["cues", 0, "scene_id"], "X1"), "scene_id"),
        (lambda d: set_at(d, ["cues", 0, "anchor_line_id"], "S1-X"), "anchor_line_id"),
        (lambda d: set_at(d, ["cues", 0, "sound_id"], "bad_id"), "sound_id"),
        # enum invalid
        (lambda d: set_at(d, ["cues", 0, "kind"], "music"), "kind"),
        (lambda d: set_at(d, ["cues", 0, "basis"], "guess"), "basis"),
        # extra keys at root and nested
        (lambda d: set_at(d, ["extra_top"], 1), "extra_top"),
        (lambda d: set_at(d, ["cues", 0, "extra"], 1), "extra"),
        # NEED_NEW requires sound_prompt (schema) - change sound_id to NEED_NEW without sound_prompt
        (lambda d: set_at(d, ["cues", 0, "sound_id"], "NEED_NEW"), "sound_prompt"),
        # non-NEED_NEW forbids sound_prompt (schema) - add sound_prompt to regular cue
        (lambda d: set_at(d, ["cues", 0, "sound_prompt"], "a prompt"), "sound_prompt"),
    ],
)
def test_schema_errors(mutate_fn, keyword):
    doc = mutate_fn(_valid_doc())
    errs = schema_errors(doc)
    assert any(keyword in e for e in errs), f"{keyword} not in {errs}"


def test_schema_valid():
    assert schema_errors(_valid_doc()) == []


# ---------- validate semantic tests ----------
@pytest.mark.parametrize(
    "mutate_fn,expected_id",
    [
        # adhyay mismatch
        (lambda d: set_at(d, ["adhyay"], 2), "sounds adhyay"),
        # scene missing
        (lambda d: set_at(d, ["cues", 0, "scene_id"], "S9"), "cue[0]"),
        # anchor line not in scene
        (lambda d: set_at(d, ["cues", 0, "anchor_line_id"], "S2-L1"), "cue[0]"),
        # sound_id not in sound_ids and not NEED_NEW
        (lambda d: set_at(d, ["cues", 0, "sound_id"], "bed_unknown"), "cue[0]"),
        # kind mismatch prefix (bed sound with fx kind)
        (lambda d: set_at(d, ["cues", 0, "kind"], "fx"), "cue[0]"),
        # fx sound with bed kind
        (lambda d: set_at(d, ["cues", 0, "sound_id"], "fx_door_wood_creak"), "cue[0]"),
    ],
)
def test_semantic_errors(mutate_fn, expected_id):
    doc = mutate_fn(_valid_doc())
    errs = validate(1, doc, _other_docs(), _valid_ctx())
    assert any(expected_id in e for e in errs), f"{expected_id} not in {errs}"


def test_semantic_valid():
    assert validate(1, _valid_doc(), _other_docs(), _valid_ctx()) == []


def test_valid_returns_empty():
    assert schema_errors(_valid_doc()) == []
    assert validate(1, _valid_doc(), _other_docs(), _valid_ctx()) == []


def test_empty_context_missing_refs():
    doc = _valid_doc()
    ctx = {
        "script_line_ids": [],
        "core_line_ids": [],
        "chapter_ovis": [],
        "unfilmed_ovis": [],
        "preset_ids": [],
        "sound_ids": [],
        "saved_voices": {},
        "speaking_characters": [],
        "known_states": {},
    }
    errs = validate(1, doc, _other_docs(), ctx)
    # sound_id not in sound_ids (empty ctx)
    assert any("cue[0]" in e for e in errs)
    # anchor line check uses scenes doc, not ctx, so no error for S1-L1
    # adhyay matches, scene exists, kind matches
    assert len(errs) == 1


# ---------- regression tests for odd data (no raise) ----------
def test_validate_odd_data_no_raise():
    # doc not a dict
    errs = validate(1, None, {}, {})
    assert isinstance(errs, list) and any("document must be an object" in e for e in errs)

    # cues not a list
    doc = _valid_doc()
    doc["cues"] = "not a list"
    errs = validate(1, doc, _other_docs(), _valid_ctx())
    assert isinstance(errs, list)

    # cue not a dict
    doc = _valid_doc()
    doc["cues"] = ["not a dict"]
    errs = validate(1, doc, _other_docs(), _valid_ctx())
    assert isinstance(errs, list) and any("cue[0]" in e for e in errs)

    # scene_id not a string
    doc = _valid_doc()
    doc["cues"][0]["scene_id"] = 123
    errs = validate(1, doc, _other_docs(), _valid_ctx())
    assert isinstance(errs, list) and any("cue[0]" in e for e in errs)

    # anchor_line_id not a string
    doc = _valid_doc()
    doc["cues"][0]["anchor_line_id"] = 123
    errs = validate(1, doc, _other_docs(), _valid_ctx())
    assert isinstance(errs, list) and any("cue[0]" in e for e in errs)

    # sound_id not a string
    doc = _valid_doc()
    doc["cues"][0]["sound_id"] = 123
    errs = validate(1, doc, _other_docs(), _valid_ctx())
    assert isinstance(errs, list) and any("cue[0]" in e for e in errs)

    # scenes doc not a dict
    doc = _valid_doc()
    errs = validate(1, doc, {"scenes": "not a dict"}, _valid_ctx())
    assert isinstance(errs, list)

    # scenes list not a list
    doc = _valid_doc()
    errs = validate(1, doc, {"scenes": {"scenes": "not a list"}}, _valid_ctx())
    assert isinstance(errs, list)

    # scene entry not a dict
    doc = _valid_doc()
    errs = validate(1, doc, {"scenes": {"scenes": ["not a dict"]}}, _valid_ctx())
    assert isinstance(errs, list)

    # sound_ids not a list
    doc = _valid_doc()
    ctx = _valid_ctx()
    ctx["sound_ids"] = "not a list"
    errs = validate(1, doc, _other_docs(), ctx)
    assert isinstance(errs, list)

    # scene line_ids contains non-string (list of list) - regression for TypeError
    doc = _valid_doc()
    docs = _other_docs()
    docs["scenes"]["scenes"][0]["line_ids"] = [["S1-L1"], "S1-L2"]
    errs = validate(1, doc, docs, _valid_ctx())
    assert isinstance(errs, list)
    # Should not raise, and anchor line check should still work for string line_ids
    assert not any("malformed structure" in e for e in errs)

    # scene line_ids is not a list
    doc = _valid_doc()
    docs = _other_docs()
    docs["scenes"]["scenes"][0]["line_ids"] = "not a list"
    errs = validate(1, doc, docs, _valid_ctx())
    assert isinstance(errs, list)
    assert not any("malformed structure" in e for e in errs)

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
