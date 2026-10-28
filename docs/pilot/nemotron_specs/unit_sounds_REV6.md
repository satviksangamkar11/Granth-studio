# FIX CALL: return BOTH files in full: `scripts/pipeline/stage1/sounds.py` and `tests/test_stage1_sounds.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
............................                                             [100%]
28 passed in 0.05s

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
            messages.append(f"{cue_id}: scene exists check failed for '{scene_id}'")
            continue

        scene = scene_by_id[scene_id]

        # Anchor line belongs to the scene
        scene_line_ids = set(scene.get("line_ids", []))
        if anchor_line_id not in scene_line_ids:
            messages.append(f"{cue_id}: anchor line belongs to the scene check failed for '{anchor_line_id}'")

        # sound_id in sound_ids or NEED_NEW
        if sound_id != "NEED_NEW" and sound_id not in sound_ids:
            messages.append(f"{cue_id}: sound_id in sound_ids or NEED_NEW check failed for '{sound_id}'")

        # kind matches the id prefix (only for non-NEED_NEW)
        if sound_id != "NEED_NEW":
            expected_kind = "bed" if sound_id.startswith("bed_") else "fx" if sound_id.startswith("fx_") else None
            if expected_kind and kind != expected_kind:
                messages.append(f"{cue_id}: kind matches the id prefix check failed (expected '{expected_kind}', got '{kind}')")

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
    "mutate_fn,keyword,expected_id",
    [
        # adhyay mismatch
        (lambda d: set_at(d, ["adhyay"], 2), "adhyay", "sounds adhyay"),
        # scene missing
        (lambda d: set_at(d, ["cues", 0, "scene_id"], "S9"), "scene exists", "cue[0]"),
        # anchor line not in scene
        (lambda d: set_at(d, ["cues", 0, "anchor_line_id"], "S2-L1"), "anchor line belongs to the scene", "cue[0]"),
        # sound_id not in sound_ids and not NEED_NEW
        (lambda d: set_at(d, ["cues", 0, "sound_id"], "bed_unknown"), "sound_id in sound_ids or NEED_NEW", "cue[0]"),
        # kind mismatch prefix (bed sound with fx kind)
        (lambda d: set_at(d, ["cues", 0, "kind"], "fx"), "kind matches the id prefix", "cue[0]"),
        # fx sound with bed kind
        (lambda d: set_at(d, ["cues", 0, "sound_id"], "fx_door_wood_creak"), "kind matches the id prefix", "cue[0]"),
    ],
)
def test_semantic_errors(mutate_fn, keyword, expected_id):
    doc = mutate_fn(_valid_doc())
    errs = validate(1, doc, _other_docs(), _valid_ctx())
    assert any(keyword in e and expected_id in e for e in errs), f"{keyword} or {expected_id} not in {errs}"


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
    assert any("sound_id in sound_ids or NEED_NEW" in e and "cue[0]" in e for e in errs)
    # anchor line check uses scenes doc, not ctx, so no error for S1-L1
    # adhyay matches, scene exists, kind matches
    assert len(errs) == 1

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
