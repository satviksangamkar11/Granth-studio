# FIX CALL 3 for Stage 1 unit `sounds`: return BOTH files in full: `scripts/pipeline/stage1/sounds.py` and `tests/test_stage1_sounds.py`.
You previously wrote the module and (in a separate call) the tests. The tests were RUN against the module: the pytest output below is the mechanical truth, plus a Codex review of the tests. For EVERY failure decide, using the UNIT SPEC as the only authority, whether the TEST or the MODULE is wrong, and fix that side. Rules: the spec decides what is schema-level and what is semantic; JSON Schema cannot compare lo <= hi or check cross references (semantic); jsonschema reports required/additionalProperties errors at the PARENT path (tests assert the offending field name, not a child path); mutation helpers must work on lists AND dicts (int part = list index), must prove the edit changed the document, and nothing may be written into a `None` (initialise nested objects first in the test); every row changes exactly one thing and the baseline stays valid; assert only the item id and keywords the spec QUOTES; positive rows assert `[]`; `import pytest` must be present; tests load the module by path with importlib exactly as the unit spec says; compact, synthetic only. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module.

## PYTEST OUTPUT (mechanical truth)
```
...................F...F...F..F                                          [100%]
================================== FAILURES ===================================
___________________ test_schema_errors[path19-sound_prompt] ___________________
tests\test_stage1_sounds.py:193: in test_schema_errors
    assert any(keyword in e for e in errs), f"{keyword} not in {errs}"
E   AssertionError: sound_prompt not in []
E   assert False
E    +  where False = any(<generator object test_schema_errors.<locals>.<genexpr> at 0x000001C0D6178EE0>)
________________ test_semantic_errors[<lambda>-anchor_line_id] ________________
tests\test_stage1_sounds.py:224: in test_semantic_errors
    assert any(keyword in e for e in errs), f"{keyword} not in {errs}"
E   AssertionError: anchor_line_id not in ["cue[0]: anchor line 'S2-L1' not in scene 'S1'"]
E   assert False
E    +  where False = any(<generator object test_semantic_errors.<locals>.<genexpr> at 0x000001C0D63182B0>)
_________________ test_semantic_errors[<lambda>-sound_prompt] _________________
tests\test_stage1_sounds.py:224: in test_semantic_errors
    assert any(keyword in e for e in errs), f"{keyword} not in {errs}"
E   AssertionError: sound_prompt not in []
E   assert False
E    +  where False = any(<generator object test_semantic_errors.<locals>.<genexpr> at 0x000001C0D63186C0>)
_______________________ test_empty_context_missing_refs _______________________
tests\test_stage1_sounds.py:250: in test_empty_context_missing_refs
    assert any("S1-L1" in e for e in errs)
E   assert False
E    +  where False = any(<generator object test_empty_context_missing_refs.<locals>.<genexpr> at 0x000001C0D6319CB0>)
=========================== short test summary info ===========================
FAILED tests/test_stage1_sounds.py::test_schema_errors[path19-sound_prompt]
FAILED tests/test_stage1_sounds.py::test_semantic_errors[<lambda>-anchor_line_id]
FAILED tests/test_stage1_sounds.py::test_semantic_errors[<lambda>-sound_prompt]
FAILED tests/test_stage1_sounds.py::test_empty_context_missing_refs - assert ...

```

## CODEX REVIEW OF THE TESTS (static)
- **sounds:** Earlier independent kind mutations **FIXED**. **Medium:** `test_schema_errors`, **164–179**, replaces fields rather than performing the labeled required deletions; only `cues` is deleted. **188–193** constructs valid NEED_NEW-with-prompt but expects rejection. Neither missing-prompt nor ordinary-cue-with-prompt schema rejection is tested; **217** incorrectly demands missing-prompt rejection semantically. `test_semantic_errors`, **207–215**, still asserts unquoted field wording instead of item IDs. `test_empty_context_missing_refs`, **250**, still requires unsupported script-membership rejection.

## UNIT SPEC (the authority)
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
    for err in _validator.iter_errors(doc):
        path = "/".join(str(p) for p in err.path) if err.path else "doc"
        errors.append(f"sounds {path}: {err.message}")
    return errors


def validate(adhyay: int, doc: dict[str, Any], docs: dict[str, Any], ctx: dict[str, Any]) -> list[str]:
    messages: list[str] = []

    # Adhyay check
    doc_adhyay = doc.get("adhyay")
    if doc_adhyay != adhyay:
        messages.append(f"sounds adhyay {doc_adhyay} does not match {adhyay}")

    # Prepare context sets
    script_line_ids = set(ctx.get("script_line_ids", []))
    sound_ids = set(ctx.get("sound_ids", []))
    scenes_doc = docs.get("scenes", {})
    scenes_list = scenes_doc.get("scenes", [])

    # Build scene lookup
    scene_by_id: dict[str, dict[str, Any]] = {}
    for sc in scenes_list:
        sid = sc.get("scene_id")
        if sid:
            scene_by_id[sid] = sc

    cues = doc.get("cues", [])
    for i, cue in enumerate(cues):
        cue_id = f"cue[{i}]"
        scene_id = cue.get("scene_id")
        anchor_line_id = cue.get("anchor_line_id")
        sound_id = cue.get("sound_id")
        kind = cue.get("kind")

        # Scene exists
        if scene_id not in scene_by_id:
            messages.append(f"{cue_id}: scene '{scene_id}' does not exist")
            continue

        scene = scene_by_id[scene_id]

        # Anchor line belongs to the scene
        scene_line_ids = set(scene.get("line_ids", []))
        if anchor_line_id not in scene_line_ids:
            messages.append(f"{cue_id}: anchor line '{anchor_line_id}' not in scene '{scene_id}'")

        # sound_id in sound_ids or NEED_NEW
        if sound_id != "NEED_NEW" and sound_id not in sound_ids:
            messages.append(f"{cue_id}: sound_id '{sound_id}' not in sound_ids")

        # kind matches id prefix
        if sound_id != "NEED_NEW":
            expected_kind = "bed" if sound_id.startswith("bed_") else "fx" if sound_id.startswith("fx_") else None
            if expected_kind and kind != expected_kind:
                messages.append(f"{cue_id}: kind '{kind}' does not match sound_id prefix '{expected_kind}'")

    return messages

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
    "path,keyword",
    [
        # required root fields
        (["adhyay"], "adhyay"),
        (["cues"], "cues"),
        # required cue fields
        (["cues", 0, "scene_id"], "scene_id"),
        (["cues", 0, "anchor_line_id"], "anchor_line_id"),
        (["cues", 0, "sound_id"], "sound_id"),
        (["cues", 0, "kind"], "kind"),
        (["cues", 0, "purpose"], "purpose"),
        (["cues", 0, "basis"], "basis"),
        # type / pattern
        (["adhyay"], "adhyay"),
        (["cues", 0, "scene_id"], "scene_id"),
        (["cues", 0, "anchor_line_id"], "anchor_line_id"),
        (["cues", 0, "sound_id"], "sound_id"),
        (["cues", 0, "kind"], "kind"),
        (["cues", 0, "purpose"], "purpose"),
        (["cues", 0, "basis"], "basis"),
        # enum invalid
        (["cues", 0, "kind"], "kind"),
        (["cues", 0, "basis"], "basis"),
        # extra keys at root and nested
        (["extra_top"], "extra_top"),
        (["cues", 0, "extra"], "extra"),
        # NEED_NEW requires sound_prompt (schema)
        (["cues", 0, "sound_prompt"], "sound_prompt"),
    ],
)
def test_schema_errors(path, keyword):
    doc = _valid_doc()
    if path == ["adhyay"]:
        doc = set_at(doc, path, "x")
    elif path == ["cues"]:
        doc = delete_at(doc, path)
    elif path == ["cues", 0, "scene_id"]:
        doc = set_at(doc, path, "X1")
    elif path == ["cues", 0, "anchor_line_id"]:
        doc = set_at(doc, path, "S1-X")
    elif path == ["cues", 0, "sound_id"]:
        doc = set_at(doc, path, "bad_id")
    elif path == ["cues", 0, "kind"]:
        doc = set_at(doc, path, "music")
    elif path == ["cues", 0, "purpose"]:
        doc = set_at(doc, path, "")
    elif path == ["cues", 0, "basis"]:
        doc = set_at(doc, path, "guess")
    elif path == ["cues", 0, "kind"] and keyword == "kind":
        doc = set_at(doc, path, "invalid_kind")
    elif path == ["cues", 0, "basis"] and keyword == "basis":
        doc = set_at(doc, path, "invalid_basis")
    elif path == ["extra_top"]:
        doc["extra_top"] = 1
    elif path == ["cues", 0, "extra"]:
        doc = set_at(doc, path, 1)
    elif path == ["cues", 0, "sound_prompt"]:
        # NEED_NEW cue with sound_prompt is valid at schema level; non-NEED_NEW with sound_prompt is forbidden
        doc = set_at(doc, ["cues", 0, "sound_id"], "NEED_NEW")
        doc = set_at(doc, path, "a prompt")
    errs = schema_errors(doc)
    assert any(keyword in e for e in errs), f"{keyword} not in {errs}"


def test_schema_valid():
    assert schema_errors(_valid_doc()) == []


# ---------- validate semantic tests ----------
@pytest.mark.parametrize(
    "mutate_fn,keyword",
    [
        # adhyay mismatch
        (lambda d: set_at(d, ["adhyay"], 2), "adhyay"),
        # scene missing
        (lambda d: set_at(d, ["cues", 0, "scene_id"], "S9"), "scene"),
        # anchor line not in scene
        (lambda d: set_at(d, ["cues", 0, "anchor_line_id"], "S2-L1"), "anchor_line_id"),
        # sound_id not in sound_ids and not NEED_NEW
        (lambda d: set_at(d, ["cues", 0, "sound_id"], "bed_unknown"), "sound_id"),
        # kind mismatch prefix (bed sound with fx kind)
        (lambda d: set_at(d, ["cues", 0, "kind"], "fx"), "kind"),
        # fx sound with bed kind
        (lambda d: set_at(d, ["cues", 0, "sound_id"], "fx_door_wood_creak"), "kind"),
        # NEED_NEW without sound_prompt (semantic sees missing prompt)
        (lambda d: set_at(d, ["cues", 0, "sound_id"], "NEED_NEW"), "sound_prompt"),
        # non-NEED_NEW cue with sound_prompt is schema error, not semantic
    ],
)
def test_semantic_errors(mutate_fn, keyword):
    doc = mutate_fn(_valid_doc())
    errs = validate(1, doc, _other_docs(), _valid_ctx())
    assert any(keyword in e for e in errs), f"{keyword} not in {errs}"


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
    assert any("S1-L1" in e for e in errs)
    assert any("bed_roadside_quiet" in e for e in errs)

```
