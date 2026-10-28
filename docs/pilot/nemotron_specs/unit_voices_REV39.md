# FIX CALL: return BOTH files in full: `scripts/pipeline/stage1/voices.py` and `tests/test_stage1_voices.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
...........................F.......................                      [100%]
================================== FAILURES ===================================
___________________ test_schema[cast.0.reason-DELETE-None] ____________________
tests\test_stage1_voices.py:186: in test_schema
    doc = delete_doc(b, path)
          ^^^^^^^^^^^^^^^^^^^
tests\test_stage1_voices.py:117: in delete_doc
    return delete_at(base, ["docs", "voices"] + parts)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\test_stage1_voices.py:83: in delete_at
    del parent[key]
        ^^^^^^^^^^^
E   KeyError: 'reason'
=========================== short test summary info ===========================
FAILED tests/test_stage1_voices.py::test_schema[cast.0.reason-DELETE-None] - ...
1 failed, 50 passed in 0.20s

```

## SPEC
# UNIT SPEC: Stage 1 document `voices` (schema `stage1_voice_cast`)
This is ONE unit of the Stage 1 contract (the master spec `stage1_v2.md` was split because one big spec gave unreliable tests). Keep the unit small and exact.
Module: `scripts/pipeline/stage1/voices.py`. Tests: `tests/test_stage1_voices.py`. Style: `from __future__ import annotations`, standard library plus `jsonschema`; no print, no network, nothing at import time; tests use only the BASE data below and `tmp_path`; the test file loads the module by path with importlib (`ROOT = Path(__file__).resolve().parents[1]`, `ROOT / "scripts" / "pipeline" / "stage1" / "voices.py"`).

## Module API (exactly this)
- `SCHEMA`: dict, JSON Schema draft 2020-12 for the document, `additionalProperties: false` on EVERY object (nested too), `$schema` = "https://json-schema.org/draft/2020-12/schema", `title` = "stage1_voice_cast".
- `schema_errors(doc) -> list[str]`: one message per jsonschema error, formatted "voices <path>: <message>" (path joined by "/", "doc" when empty).
- `validate(adhyay, doc, docs, ctx) -> list[str]`: SEMANTIC checks only (the schema has already passed; it must still never raise on odd data). `docs` is a dict of ALL nine documents (key names: story_map, coverage, scenes, shots, briefs, looks, voices, sounds, questions; a missing one counts as empty), `ctx` the context dict (keys: script_line_ids list, core_line_ids set, chapter_ovis set, unfilmed_ovis set, preset_ids set, sound_ids set, saved_voices dict voice_key->voice_id, speaking_characters set, known_states dict entity_id->set of state ids). Lists in ctx may arrive as lists or sets: convert with set(). Notes (messages that start with "note: ") come AFTER error messages. Include the adhyay check first: "voices adhyay <n> does not match <adhyay>".

## Ids and common types
scene_id `^S[0-9]{1,2}$`; shot_id `^S[0-9]{1,2}-[0-9]{1,2}$`; line_id `^S[0-9]{1,2}-L[0-9]{1,3}$`; image id (Stage 1 brief) `^s[0-9]{1,2}_[a-z][a-z0-9_]{0,40}$`; ovi = integer >= 1; adhyay = integer 1..21; text = string 1..400 chars; preset id = string matching `^[0-9]{2}_[a-z0-9_]+$`; sound id `^(bed|fx)_[a-z0-9_]+$`.

## The document shape (from the master spec)
7. `stage1_voice_cast`: `cast`: array of {character_id, voice_key, voice_id (string 10..40 chars), gender: male|female, status: RECURRING|NEW_PROPOSED}.

## Semantic rules of this unit (master spec step 9)
9. voices: every `speaking_characters` member has exactly one cast entry ("<character>: no voice assigned"); voice_key must be a key of `saved_voices` and voice_id must equal `saved_voices[voice_key]` ("<character>: voice not in the saved cast"); a character already RECURRING must not be listed twice; two characters must not share a voice_key unless one is the narrator.

Messages: tests assert only the quoted keywords/phrases of the rules plus the item id; for rules without a quoted phrase the message is `<item id>: <condition in plain words>`.

## BASE data (valid, note-free; the baseline for EVERY test; `validate(1, BASE_DOCS["voices"], BASE_DOCS, CTX)` must return [] and `schema_errors` must return [])
File `docs/pilot/nemotron_specs/stage1_base.json` has the keys "docs" (the nine documents) and "ctx". The test file must embed its own copy of what it needs as Python literals (copy the values below exactly):
```json
{
 "docs": {
  "voices": {
   "adhyay": 1,
   "cast": [
    {
     "character_id": "narrator",
     "voice_key": "narrator",
     "voice_id": "CXkeo30p0Sk4Lr0TAzeo",
     "gender": "male",
     "status": "RECURRING"
    },
    {
     "character_id": "gajanan_maharaj",
     "voice_key": "gajanan",
     "voice_id": "8fqGzH80bdkm2UseeV9f",
     "gender": "male",
     "status": "RECURRING"
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



## CURRENT MODULE scripts/pipeline/stage1/voices.py
```python
from __future__ import annotations

import jsonschema
from jsonschema import Draft202012Validator

SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "stage1_voice_cast",
    "type": "object",
    "additionalProperties": False,
    "required": ["adhyay", "cast"],
    "properties": {
        "adhyay": {
            "type": "integer",
            "minimum": 1,
            "maximum": 21
        },
        "cast": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["character_id", "voice_key", "voice_id", "gender", "status"],
                "properties": {
                    "character_id": {"type": "string"},
                    "voice_key": {"type": "string"},
                    "voice_id": {"type": "string", "minLength": 10, "maxLength": 40},
                    "gender": {"type": "string", "enum": ["male", "female"]},
                    "status": {"type": "string", "enum": ["RECURRING", "NEW_PROPOSED"]},
                    "reason": {"type": "string", "minLength": 1}
                },
                "if": {
                    "properties": {"status": {"const": "NEW_PROPOSED"}}
                },
                "then": {
                    "required": ["reason"]
                }
            }
        }
    }
}

_validator = Draft202012Validator(SCHEMA)


def schema_errors(doc) -> list[str]:
    errors = []
    for err in _validator.iter_errors(doc):
        path = "/".join(str(p) for p in err.path) if err.path else "doc"
        errors.append(f"voices {path}: {err.message}")
    return errors


def _validate_impl(adhyay: int, doc: dict, docs: dict, ctx: dict) -> list[str]:
    messages = []

    # Adhyay check
    doc_adhyay = doc.get("adhyay")
    if doc_adhyay != adhyay:
        messages.append(f"voices adhyay {doc_adhyay} does not match {adhyay}")

    # Convert ctx lists/sets to sets
    speaking_characters = set(ctx.get("speaking_characters", []))
    saved_voices = ctx.get("saved_voices", {})

    # Handle cast safely - validate structure
    cast_raw = doc.get("cast")
    if not isinstance(cast_raw, list):
        messages.append("cast: must be a list")
        cast = []
    else:
        cast = []
        for i, entry in enumerate(cast_raw):
            if not isinstance(entry, dict):
                messages.append(f"cast[{i}]: must be an object")
                continue
            # Check required fields
            for field in ["character_id", "voice_key", "voice_id", "gender", "status"]:
                if field not in entry:
                    messages.append(f"cast[{i}].{field}: required field missing")
            # Check types
            if "character_id" in entry and not isinstance(entry["character_id"], str):
                messages.append(f"cast[{i}].character_id: must be string")
            if "voice_key" in entry and not isinstance(entry["voice_key"], str):
                messages.append(f"cast[{i}].voice_key: must be string")
            if "voice_id" in entry and not isinstance(entry["voice_id"], str):
                messages.append(f"cast[{i}].voice_id: must be string")
            if "gender" in entry and not isinstance(entry["gender"], str):
                messages.append(f"cast[{i}].gender: must be string")
            if "status" in entry and not isinstance(entry["status"], str):
                messages.append(f"cast[{i}].status: must be string")
            # Only add to cast if it has all required fields with correct types
            if (isinstance(entry.get("character_id"), str) and
                isinstance(entry.get("voice_key"), str) and
                isinstance(entry.get("voice_id"), str) and
                isinstance(entry.get("gender"), str) and
                isinstance(entry.get("status"), str)):
                cast.append(entry)

    # Build lookup: character_id -> list of entries
    char_entries = {}
    for entry in cast:
        cid = entry.get("character_id")
        if not isinstance(cid, str):
            continue
        if cid not in char_entries:
            char_entries[cid] = []
        char_entries[cid].append(entry)

    # Rule: every speaking_character has exactly one cast entry
    for char in speaking_characters:
        entries = char_entries.get(char, [])
        if len(entries) == 0:
            messages.append(f"{char}: no voice assigned")
        elif len(entries) > 1:
            messages.append(f"{char}: listed more than once")

    # Rule: a character already RECURRING must not be listed twice (any status combination)
    for char, entries in char_entries.items():
        if len(entries) > 1 and any(e.get("status") == "RECURRING" for e in entries):
            messages.append(f"{char}: recurring character listed twice")

    # Rule: voice_key must be in saved_voices and voice_id must match
    for entry in cast:
        char = entry.get("character_id")
        if not isinstance(char, str):
            continue
        vkey = entry.get("voice_key")
        vid = entry.get("voice_id")
        if not isinstance(vkey, str) or vkey not in saved_voices:
            messages.append(f"{char}: voice not in the saved cast")
        elif saved_voices[vkey] != vid:
            messages.append(f"{char}: voice not in the saved cast")

    # Rule: two characters must not share a voice_key unless one is the narrator
    voice_key_to_chars = {}
    for entry in cast:
        vkey = entry.get("voice_key")
        char = entry.get("character_id")
        if not isinstance(vkey, str) or not isinstance(char, str):
            continue
        if vkey not in voice_key_to_chars:
            voice_key_to_chars[vkey] = set()
        voice_key_to_chars[vkey].add(char)

    for vkey, chars in voice_key_to_chars.items():
        # Get unique non-narrator characters sharing this key
        non_narrator_chars = [c for c in chars if c != "narrator"]
        if len(non_narrator_chars) > 1:
            # Multiple different non-narrator characters share this key - error for each
            for char in non_narrator_chars:
                messages.append(f"{char}: voice key shared with another character")

    return messages


def validate(adhyay: int, doc: dict, docs: dict, ctx: dict) -> list[str]:
    try:
        if not isinstance(doc, dict):
            return ["voices doc: document must be an object"]
        return _validate_impl(adhyay, doc, docs, ctx)
    except (TypeError, AttributeError, KeyError, ValueError, IndexError):
        return ["voices: malformed structure"]

```

## CURRENT TESTS tests/test_stage1_voices.py
```python
from __future__ import annotations
import copy
from pathlib import Path
import importlib.util
import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "pipeline" / "stage1" / "voices.py"

spec = importlib.util.spec_from_file_location("voices", MODULE_PATH)
voices = importlib.util.module_from_spec(spec)
spec.loader.exec_module(voices)

schema_errors = voices.schema_errors
validate = voices.validate


def base() -> dict:
    return {
        "docs": {
            "voices": {
                "adhyay": 1,
                "cast": [
                    {
                        "character_id": "narrator",
                        "voice_key": "narrator",
                        "voice_id": "CXkeo30p0Sk4Lr0TAzeo",
                        "gender": "male",
                        "status": "RECURRING",
                    },
                    {
                        "character_id": "gajanan_maharaj",
                        "voice_key": "gajanan",
                        "voice_id": "8fqGzH80bdkm2UseeV9f",
                        "gender": "male",
                        "status": "RECURRING",
                    },
                ],
            }
        },
        "ctx": {
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
        },
    }


def get_parent(doc: dict, path: list) -> tuple[object, object]:
    """Walk path (list of str/int) to parent of last element. Returns (parent, last_key)."""
    cur = doc
    for p in path[:-1]:
        cur = cur[p]
    return cur, path[-1]


def set_at(base: dict, path: list, value) -> dict:
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    if isinstance(parent, list):
        parent[key] = value
    else:
        parent[key] = value
    assert doc != base, "mutation had no effect"
    return doc


def delete_at(base: dict, path: list) -> dict:
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    if isinstance(parent, list):
        del parent[key]
    else:
        del parent[key]
    assert doc != base, "mutation had no effect"
    return doc


def append_at(base: dict, path: list, value) -> dict:
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    assert isinstance(parent, list), "append_at target must be list"
    parent.append(value)
    assert doc != base, "mutation had no effect"
    return doc


def mutate_doc(base: dict, path_str: str, value):
    """Mutate base['docs']['voices'] using dot path with int indexes."""
    parts = []
    for p in path_str.split("."):
        parts.append(int(p) if p.isdigit() else p)
    return set_at(base, ["docs", "voices"] + parts, value)


def mutate_ctx(base: dict, path_str: str, value):
    """Mutate base['ctx'] using dot path with int indexes."""
    parts = []
    for p in path_str.split("."):
        parts.append(int(p) if p.isdigit() else p)
    return set_at(base, ["ctx"] + parts, value)


def delete_doc(base: dict, path_str: str):
    parts = []
    for p in path_str.split("."):
        parts.append(int(p) if p.isdigit() else p)
    return delete_at(base, ["docs", "voices"] + parts)


def delete_ctx(base: dict, path_str: str):
    parts = []
    for p in path_str.split("."):
        parts.append(int(p) if p.isdigit() else p)
    return delete_at(base, ["ctx"] + parts)


def append_doc(base: dict, path_str: str, value):
    parts = []
    for p in path_str.split("."):
        parts.append(int(p) if p.isdigit() else p)
    return append_at(base, ["docs", "voices"] + parts, value)


@pytest.mark.parametrize("path,value,keyword", [
    (None, None, None),
    ("adhyay", None, "adhyay"),
    ("cast", None, "cast"),
    ("adhyay", "1", "adhyay"),
    ("adhyay", 0, "adhyay"),
    ("adhyay", 22, "adhyay"),
    ("cast", "x", "cast"),
    ("cast.0.character_id", None, "character_id"),
    ("cast.0.voice_key", None, "voice_key"),
    ("cast.0.voice_id", None, "voice_id"),
    ("cast.0.gender", None, "gender"),
    ("cast.0.status", None, "status"),
    ("cast.0.gender", "other", "gender"),
    ("cast.0.status", "INVALID", "status"),
    ("cast.0.voice_id", "short", "voice_id"),
    ("cast.0.voice_id", "x" * 41, "voice_id"),
    ("cast.0.extra", "field", "extra"),
    ("extra", "field", "extra"),
    # Required field deletion tests
    ("cast.0.character_id", "DELETE", "character_id"),
    ("cast.0.voice_key", "DELETE", "voice_key"),
    ("cast.0.voice_id", "DELETE", "voice_id"),
    ("cast.0.gender", "DELETE", "gender"),
    ("cast.0.status", "DELETE", "status"),
    # Schema-valid enum value tests (removing the enum value should fail these)
    ("cast.0.gender", "female", None),
    ("cast.0.status", "NEW_PROPOSED", "reason"),  # NEW_PROPOSED requires reason
    # reason field tests
    ("cast.0.reason", "valid reason", None),  # RECURRING with reason is valid
    ("cast.0.reason", "", "reason"),  # empty reason is invalid
    ("cast.0.reason", "DELETE", None),  # RECURRING without reason is valid
    # NEW_PROPOSED with reason tests
    ("cast", [
        {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
        {"character_id": "gajanan_maharaj", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "male", "status": "NEW_PROPOSED", "reason": "new voice for gajanan"},
    ], None),  # NEW_PROPOSED with reason is valid
    ("cast", [
        {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
        {"character_id": "gajanan_maharaj", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "male", "status": "NEW_PROPOSED"},
    ], "reason"),  # NEW_PROPOSED without reason fails
    ("cast", [
        {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
        {"character_id": "gajanan_maharaj", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "male", "status": "NEW_PROPOSED", "reason": ""},
    ], "reason"),  # NEW_PROPOSED with empty reason fails
])
def test_schema(path, value, keyword):
    b = base()
    if path is None:
        assert schema_errors(b["docs"]["voices"]) == []
    else:
        if value == "DELETE":
            doc = delete_doc(b, path)
        else:
            doc = mutate_doc(b, path, value)
        errs = schema_errors(doc["docs"]["voices"])
        if keyword is None:
            assert errs == []
        else:
            assert errs
            assert any(keyword in e for e in errs)


@pytest.mark.parametrize("path,value,keyword", [
    (None, None, None),
    ("adhyay", 2, "adhyay"),
    # Remove cast entry for narrator -> no voice assigned
    ("cast.0", None, "narrator"),
    # Remove cast entry for gajanan_maharaj -> no voice assigned
    ("cast.1", None, "gajanan_maharaj"),
    ("cast.0.voice_key", "unknown", "narrator"),
    # Use valid-length but wrong voice_id
    ("cast.0.voice_id", "x" * 10, "narrator"),
    # Duplicate narrator entry (RECURRING listed twice)
    ("cast", [
        {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
        {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
        {"character_id": "gajanan_maharaj", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "male", "status": "RECURRING"},
    ], "narrator"),
    # Two non-narrators sharing a voice_key (gajanan) -> forbidden
    ("cast", [
        {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
        {"character_id": "gajanan_maharaj", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "male", "status": "RECURRING"},
        {"character_id": "extra_char", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "female", "status": "NEW_PROPOSED", "reason": "new voice"},
    ], "extra_char"),
    # Another case: two non-narrators sharing a voice_key
    ("cast", [
        {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
        {"character_id": "char1", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "male", "status": "NEW_PROPOSED", "reason": "reason1"},
        {"character_id": "char2", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "female", "status": "NEW_PROPOSED", "reason": "reason2"},
    ], "char1"),
    # Two NEW_PROPOSED entries for same speaking character
    ("cast", [
        {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
        {"character_id": "gajanan_maharaj", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "male", "status": "NEW_PROPOSED", "reason": "reason1"},
        {"character_id": "gajanan_maharaj", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "male", "status": "NEW_PROPOSED", "reason": "reason2"},
    ], "gajanan_maharaj"),
    # Narrator and two others sharing a saved key - should error for the two non-narrators
    ("cast", [
        {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
        {"character_id": "charA", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "NEW_PROPOSED", "reason": "reasonA"},
        {"character_id": "charB", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "female", "status": "NEW_PROPOSED", "reason": "reasonB"},
    ], "charA"),
    ("ctx.speaking_characters", [], None),
    # Odd data: cast is not a list
    ("cast", "not a list", "cast"),
    # Odd data: cast contains non-dict entries
    ("cast", [{"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"}, "not a dict"], "cast"),
    # Odd data: cast contains entry with non-string character_id
    ("cast", [{"character_id": 123, "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"}], "character_id"),
    # Odd data: cast contains entry with non-string voice_key
    ("cast", [{"character_id": "narrator", "voice_key": 123, "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"}], "voice_key"),
    # Odd data: doc is not a dict
    ("__doc__", None, "doc"),
    # Odd data: doc is a list
    ("__doc__", [1, 2, 3], "doc"),
])
def test_validate(path, value, keyword):
    b = base()
    if path is None:
        assert validate(1, b["docs"]["voices"], b["docs"], b["ctx"]) == []
    elif path.startswith("ctx."):
        doc = mutate_ctx(b, path[4:], value)
        errs = validate(1, doc["docs"]["voices"], doc["docs"], doc["ctx"])
        if keyword is None:
            assert errs == []
        else:
            assert errs
            assert any(keyword in e for e in errs)
    elif path == "__doc__":
        # Special case: replace the whole doc
        if value is None:
            test_doc = None
        else:
            test_doc = value
        errs = validate(1, test_doc, b["docs"], b["ctx"])
        if keyword is None:
            assert errs == []
        else:
            assert errs
            assert any(keyword in e for e in errs)
    else:
        if value == "DELETE":
            doc = delete_doc(b, path)
        else:
            doc = mutate_doc(b, path, value)
        errs = validate(1, doc["docs"]["voices"], doc["docs"], doc["ctx"])
        if keyword is None:
            assert errs == []
        else:
            assert errs
            assert any(keyword in e for e in errs)


def test_validate_recurring_duplicate_isolated():
    """Test that recurring character listed twice is detected without collateral shared-key errors."""
    b = base()
    # Extend saved_voices with a unique key for other_char
    ctx = copy.deepcopy(b["ctx"])
    ctx["saved_voices"] = dict(ctx["saved_voices"])
    ctx["saved_voices"]["other"] = "ZZZZZZZZZZ"
    doc = {
        "adhyay": 1,
        "cast": [
            {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
            {"character_id": "gajanan_maharaj", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "male", "status": "RECURRING"},
            {"character_id": "other_char", "voice_key": "other", "voice_id": "ZZZZZZZZZZ", "gender": "male", "status": "RECURRING"},
            {"character_id": "other_char", "voice_key": "other", "voice_id": "ZZZZZZZZZZ", "gender": "male", "status": "RECURRING"},
        ],
    }
    errs = validate(1, doc, b["docs"], ctx)
    # Should only have the recurring duplicate error for other_char
    assert any("other_char" in e for e in errs)


def test_validate_recurring_newproposed_duplicate_isolated():
    """Test that non-speaking RECURRING + NEW_PROPOSED duplicate is detected without collateral shared-key errors."""
    b = base()
    # Extend saved_voices with a unique key for other_char
    ctx = copy.deepcopy(b["ctx"])
    ctx["saved_voices"] = dict(ctx["saved_voices"])
    ctx["saved_voices"]["other"] = "ZZZZZZZZZZ"
    doc = {
        "adhyay": 1,
        "cast": [
            {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
            {"character_id": "gajanan_maharaj", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "male", "status": "RECURRING"},
            {"character_id": "other_char", "voice_key": "other", "voice_id": "ZZZZZZZZZZ", "gender": "male", "status": "RECURRING"},
            {"character_id": "other_char", "voice_key": "other", "voice_id": "ZZZZZZZZZZ", "gender": "male", "status": "NEW_PROPOSED", "reason": "new voice"},
        ],
    }
    errs = validate(1, doc, b["docs"], ctx)
    # Should only have the recurring duplicate error for other_char
    assert any("other_char" in e for e in errs)

```

## THIS CALL RETURNS THREE FILES: scripts/pipeline/stage1/voices.py, tests/test_stage1_voices.py AND tests/test_stage1_aggregate.py (each complete).
1. voices test: the row 'cast.0.reason' DELETE fails because cast[0] is the RECURRING entry 'narrator' that has NO reason in the base, so deleting it changes nothing. Test the 'missing reason' case on a NEW_PROPOSED entry built with copy.deepcopy and plain assignment (append a NEW_PROPOSED entry without reason and assert a schema error naming reason). Never use a delete helper on a key that does not exist.
2. aggregate test: test_x7_new_proposed_for_series_char builds a NEW_PROPOSED cast entry WITHOUT the new required field 'reason' (non-empty string), so the voices document now fails its schema and X7 is skipped. Add a non-empty reason to every NEW_PROPOSED entry that test builds (and to any other aggregate test that builds a NEW_PROPOSED entry). Change nothing else in the aggregate tests.

## CURRENT tests/test_stage1_aggregate.py
```python
from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGG_PATH = ROOT / "scripts" / "pipeline" / "stage1" / "aggregate.py"
BASE_PATH = ROOT / "docs" / "pilot" / "nemotron_specs" / "stage1_base.json"

spec = importlib.util.spec_from_file_location("stage1_aggregate", AGG_PATH)
assert spec is not None and spec.loader is not None
agg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agg)

BASE = json.loads(BASE_PATH.read_text(encoding="utf-8"))
BASE_DOCS = BASE["docs"]
BASE_CTX = BASE["ctx"]


def _make_minimal_valid_docs(ovis_covered: list[int] | None = None) -> tuple[dict, dict]:
    """Create a minimal valid set of documents and ctx for the given ovis.
    This is used to isolate cross-rule tests."""
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # We'll adjust the base to only involve the ovis we care about.
    # But the base is already valid. We'll instead modify the base in the tests.
    return docs, ctx


def test_base_valid():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    errs = agg.validate_all(1, docs, ctx)
    assert errs == []


def test_x1_story_ovi_not_in_any_event():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Make ovi 3 STORY but events only cover [4,5]
    docs["story_map"]["ovi_types"] = [{"ovi": 3, "type": "STORY"}, {"ovi": 4, "type": "STORY"}]
    docs["story_map"]["events"] = [{"event_id": "E1", "kind": "story", "title": "t", "ovi_range": [4, 5], "key_ovis": [4], "closure": "RESOLVED_IN_ADHYAY"}]
    # Adjust ctx chapter_ovis to only 3,4 so story_map unit validation passes
    ctx["chapter_ovis"] = [3, 4]
    # Ensure coverage for 3,4 is not PROPOSE_OMISSION and they are in shots/scenes
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] in (3, 4):
            c["disposition"] = "VISUALISED"
    # Ensure scenes cover 3,4
    for sc in docs["scenes"]["scenes"]:
        sc["ovi_range"] = [3, 4]
    # Ensure shots include 3,4
    for sh in docs["shots"]["shots"]:
        sh["ovi_ids"] = [3, 4]
    # No unfilmed ovis
    ctx["unfilmed_ovis"] = []
    errs = agg.validate_all(1, docs, ctx)
    assert any("story_map: ovi 3 is typed STORY but is in no event" in e for e in errs)
    # Corrected twin: expand event range to cover 3
    docs["story_map"]["events"][0]["ovi_range"] = [3, 5]
    errs2 = agg.validate_all(1, docs, ctx)
    # Only assert the X1 error is gone; other unit-level errors may exist
    assert not any("story_map: ovi 3 is typed STORY but is in no event" in e for e in errs2)


def test_x1_empty_events():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    docs["story_map"]["ovi_types"] = [{"ovi": 1, "type": "STORY"}, {"ovi": 2, "type": "TEACHING"}]
    docs["story_map"]["events"] = []
    ctx["chapter_ovis"] = [1, 2]
    # Adjust coverage, scenes, shots for 1,2
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] in (1, 2):
            c["disposition"] = "VISUALISED"
    for sc in docs["scenes"]["scenes"]:
        sc["ovi_range"] = [1, 2]
    for sh in docs["shots"]["shots"]:
        sh["ovi_ids"] = [1, 2]
    ctx["unfilmed_ovis"] = []
    errs = agg.validate_all(1, docs, ctx)
    assert any("story_map: ovi 1 is typed STORY but is in no event" in e for e in errs)
    assert any("story_map: ovi 2 is typed TEACHING but is in no event" in e for e in errs)


def test_x2_story_ovi_propose_omission():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Find a STORY ovi in base
    story_ovi = None
    for ot in docs["story_map"]["ovi_types"]:
        if ot["type"] == "STORY":
            story_ovi = ot["ovi"]
            break
    assert story_ovi is not None
    # Set coverage to PROPOSE_OMISSION for that ovi
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] == story_ovi:
            c["disposition"] = "PROPOSE_OMISSION"
            c["reason"] = "test"
            break
    # Add to unfilmed so X3 passes
    ctx["unfilmed_ovis"] = [story_ovi]
    # Ensure it's in a scene and shot so X4 doesn't fire
    for sc in docs["scenes"]["scenes"]:
        if sc["ovi_range"][0] <= story_ovi <= sc["ovi_range"][1]:
            break
    else:
        docs["scenes"]["scenes"][0]["ovi_range"] = [story_ovi, story_ovi]
    for sh in docs["shots"]["shots"]:
        if story_ovi in sh.get("ovi_ids", []):
            break
    else:
        docs["shots"]["shots"][0]["ovi_ids"].append(story_ovi)
    # Ensure no other STORY/TEACHING ovis are PROPOSE_OMISSION
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] != story_ovi and c["disposition"] == "PROPOSE_OMISSION":
            c["disposition"] = "VISUALISED"
    errs = agg.validate_all(1, docs, ctx)
    assert any(f"coverage: ovi {story_ovi} is STORY but an omission is proposed" in e for e in errs)
    # Corrected twin
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] == story_ovi:
            c["disposition"] = "VISUALISED"
            break
    ctx["unfilmed_ovis"] = []
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any(f"coverage: ovi {story_ovi} is STORY but an omission is proposed" in e for e in errs2)


def test_x3_proposed_not_in_unfilmed():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Pick an ovi, set PROPOSE_OMISSION but don't add to unfilmed
    ovi = docs["coverage"]["ovis"][0]["ovi"]
    docs["coverage"]["ovis"][0]["disposition"] = "PROPOSE_OMISSION"
    docs["coverage"]["ovis"][0]["reason"] = "test"
    ctx["unfilmed_ovis"] = []
    # Ensure no other PROPOSE_OMISSION
    for c in docs["coverage"]["ovis"][1:]:
        if c["disposition"] == "PROPOSE_OMISSION":
            c["disposition"] = "VISUALISED"
    errs = agg.validate_all(1, docs, ctx)
    assert any(f"coverage: ovi {ovi} omission is not approved by the owner" in e for e in errs)


def test_x3_unfilmed_without_proposal():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Add an ovi to unfilmed that has no PROPOSE_OMISSION
    ovi = 999
    ctx["unfilmed_ovis"] = [ovi]
    # Ensure no coverage entry has PROPOSE_OMISSION for 999
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] == ovi:
            c["disposition"] = "VISUALISED"
    # Also ensure no other PROPOSE_OMISSION in coverage
    for c in docs["coverage"]["ovis"]:
        if c["disposition"] == "PROPOSE_OMISSION":
            c["disposition"] = "VISUALISED"
    errs = agg.validate_all(1, docs, ctx)
    assert any(f"coverage: ovi {ovi} is approved as unfilmed but has no omission proposal" in e for e in errs)


def test_x4_visualised_not_in_shot():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Pick an ovi, set VISUALISED but remove from all shots
    ovi = docs["coverage"]["ovis"][0]["ovi"]
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] == ovi:
            c["disposition"] = "VISUALISED"
            break
    # Remove ovi from all shots
    for sh in docs["shots"]["shots"]:
        if ovi in sh.get("ovi_ids", []):
            sh["ovi_ids"] = [x for x in sh["ovi_ids"] if x != ovi]
    # Ensure the ovi is in a scene so X4 part 2 doesn't fire
    for sc in docs["scenes"]["scenes"]:
        if sc["ovi_range"][0] <= ovi <= sc["ovi_range"][1]:
            break
    else:
        docs["scenes"]["scenes"][0]["ovi_range"] = [ovi, ovi]
    # Ensure no other VISUALISED ovis are missing from shots
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] != ovi and c["disposition"] == "VISUALISED":
            # add to first shot
            if ovi not in docs["shots"]["shots"][0]["ovi_ids"]:
                docs["shots"]["shots"][0]["ovi_ids"].append(c["ovi"])
    errs = agg.validate_all(1, docs, ctx)
    assert any(f"coverage: ovi {ovi} is VISUALISED but is in no shot" in e for e in errs)
    # Corrected twin
    docs["shots"]["shots"][0]["ovi_ids"].append(ovi)
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any(f"coverage: ovi {ovi} is VISUALISED but is in no shot" in e for e in errs2)


def test_x4_non_omitted_not_in_scene():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Pick an ovi that's not PROPOSE_OMISSION, remove from all scene ranges
    ovi = docs["coverage"]["ovis"][0]["ovi"]
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] == ovi:
            c["disposition"] = "NARRATED"
            break
    # Make all scene ranges not cover this ovi
    for sc in docs["scenes"]["scenes"]:
        sc["ovi_range"] = [100, 200]
    # Ensure the ovi is not VISUALISED (so part 1 doesn't fire)
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] == ovi:
            c["disposition"] = "NARRATED"
    # Ensure no other non-omitted ovis are missing from scenes
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] != ovi and c["disposition"] != "PROPOSE_OMISSION":
            # adjust first scene to cover it
            docs["scenes"]["scenes"][0]["ovi_range"] = [c["ovi"], c["ovi"]]
    errs = agg.validate_all(1, docs, ctx)
    assert any(f"coverage: ovi {ovi} is in no scene" in e for e in errs)
    # Corrected twin
    docs["scenes"]["scenes"][0]["ovi_range"] = [ovi, ovi]
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any(f"coverage: ovi {ovi} is in no scene" in e for e in errs2)


def test_x5_key_ovi_not_in_scene():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Set event key_ovi to 999, make scenes not cover it
    docs["story_map"]["events"][0]["key_ovis"] = [999]
    for sc in docs["scenes"]["scenes"]:
        sc["ovi_range"] = [1, 10]
    # Ensure coverage for 999 is not PROPOSE_OMISSION and not VISUALISED (to avoid X4)
    # Add a coverage entry for 999 if not present
    if not any(c["ovi"] == 999 for c in docs["coverage"]["ovis"]):
        docs["coverage"]["ovis"].append({"ovi": 999, "disposition": "NARRATED"})
    else:
        for c in docs["coverage"]["ovis"]:
            if c["ovi"] == 999:
                c["disposition"] = "NARRATED"
    errs = agg.validate_all(1, docs, ctx)
    assert any("story_map: key ovi 999 of event" in e and "is in no scene" in e for e in errs)
    # Corrected twin
    docs["scenes"]["scenes"][0]["ovi_range"] = [999, 999]
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any("story_map: key ovi 999 of event" in e and "is in no scene" in e for e in errs2)


def test_x6_ambiguous_event_no_question():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Set event E2 closure to SOURCE_INCOMPLETE_OR_AMBIGUOUS, remove questions on S2
    for ev in docs["story_map"]["events"]:
        if ev["event_id"] == "E2":
            ev["closure"] = "SOURCE_INCOMPLETE_OR_AMBIGUOUS"
            break
    # Remove questions on S2
    docs["questions"]["questions"] = [q for q in docs["questions"]["questions"] if q.get("scene_id") != "S2"]
    # Ensure scenes S2 exists and overlaps with E2
    # We assume base has S2 overlapping E2. If not, adjust.
    # Find E2 range
    e2_range = None
    for ev in docs["story_map"]["events"]:
        if ev["event_id"] == "E2":
            e2_range = ev["ovi_range"]
            break
    if e2_range:
        # Ensure there is a scene S2 with overlapping range
        s2_found = False
        for sc in docs["scenes"]["scenes"]:
            if sc.get("scene_id") == "S2":
                s2_found = True
                # make sure it overlaps
                sc["ovi_range"] = [e2_range[0], e2_range[1]]
                break
        if not s2_found:
            docs["scenes"]["scenes"].append({"scene_id": "S2", "section_kind": "story", "ovi_range": e2_range, "line_ids": []})
    errs = agg.validate_all(1, docs, ctx)
    assert any("story_map: ambiguous event E2 has no question" in e for e in errs)
    # Corrected twin: add question on S2
    docs["questions"]["questions"].append({"id": "Q99", "text": "test", "scene_id": "S2"})
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any("story_map: ambiguous event E2 has no question" in e for e in errs2)


def test_x7_recurring_voice_mismatch():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    ctx["series_voices"] = {"gajanan_maharaj": "other_key"}
    # Ensure cast has gajanan_maharaj as RECURRING with different key
    # But we must keep the voice_key in saved_voices to avoid unit validation error.
    # So we add "different_key" to saved_voices.
    saved = list(ctx.get("saved_voices", []))
    if "different_key" not in saved:
        saved.append("different_key")
    ctx["saved_voices"] = saved
    for cast in docs["voices"]["cast"]:
        if cast["character_id"] == "gajanan_maharaj":
            cast["status"] = "RECURRING"
            cast["voice_key"] = "different_key"
            break
    errs = agg.validate_all(1, docs, ctx)
    assert any("voices: recurring character gajanan_maharaj has a different voice than the series" in e for e in errs)
    # Corrected twin: matching key
    for cast in docs["voices"]["cast"]:
        if cast["character_id"] == "gajanan_maharaj":
            cast["voice_key"] = "other_key"
            break
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any("voices: recurring character gajanan_maharaj has a different voice than the series" in e for e in errs2)


def test_x7_new_proposed_for_series_char():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    ctx["series_voices"] = {"gajanan_maharaj": "some_key"}
    # Ensure the voice_key is in saved_voices
    saved = list(ctx.get("saved_voices", []))
    if "some_key" not in saved:
        saved.append("some_key")
    ctx["saved_voices"] = saved
    for cast in docs["voices"]["cast"]:
        if cast["character_id"] == "gajanan_maharaj":
            cast["status"] = "NEW_PROPOSED"
            cast["voice_key"] = "some_key"
            break
    errs = agg.validate_all(1, docs, ctx)
    assert any("voices: character gajanan_maharaj already has a series voice" in e for e in errs)
    # Corrected twin: change to RECURRING with matching key
    for cast in docs["voices"]["cast"]:
        if cast["character_id"] == "gajanan_maharaj":
            cast["status"] = "RECURRING"
            cast["voice_key"] = "some_key"
            break
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any("voices: character gajanan_maharaj already has a series voice" in e for e in errs2)


def test_x8_script_text_copied():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    script_line = "This is a long enough script line for testing purposes"
    ctx["script_texts"] = [script_line]
    # Copy into scenes[0].goal
    docs["scenes"]["scenes"][0]["goal"] = script_line
    errs = agg.validate_all(1, docs, ctx)
    assert any("scenes: free text copies script wording (scenes/0/goal)" in e for e in errs)
    # Short text should not trigger
    docs["scenes"]["scenes"][0]["goal"] = "Short"
    ctx["script_texts"] = ["Short"]
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any("free text copies script wording" in e for e in errs2)


def test_robustness_docs_none():
    errs = agg.validate_all(1, None, {})
    assert any("aggregate: docs must be an object" in e for e in errs)
    assert sum(1 for e in errs if "document missing" in e) == 9


def test_robustness_docs_empty():
    errs = agg.validate_all(1, {}, {})
    assert sum(1 for e in errs if "document missing" in e) == 9


def test_robustness_ctx_none():
    docs = copy.deepcopy(BASE_DOCS)
    errs = agg.validate_all(1, docs, None)
    assert any("aggregate: ctx must be an object" in e for e in errs)
    # Should still validate base
    assert not any("internal error" in e for e in errs)


def test_robustness_doc_is_list():
    docs = copy.deepcopy(BASE_DOCS)
    docs["story_map"] = []
    errs = agg.validate_all(1, docs, {})
    assert any("story_map: document missing" in e for e in errs)
    # Other units should still be checked
    assert not any("internal error" in e for e in errs)


def test_robustness_schema_failure_skips_validate_and_cross():
    docs = copy.deepcopy(BASE_DOCS)
    # Break coverage schema by making ovis a string (invalid type)
    docs["coverage"] = {"ovis": "invalid"}
    errs = agg.validate_all(1, docs, {})
    # Should have schema errors for coverage
    # Get the actual schema error message from the unit
    cov_module = agg._load_unit("coverage")
    schema_errs = cov_module.schema_errors(docs["coverage"]) if cov_module else []
    assert schema_errs, "coverage schema should produce errors for invalid ovis"
    # At least one of those schema errors should appear in aggregate output
    assert any(any(se in e for e in errs) for se in schema_errs)
    # Should not have internal error from validate
    assert not any("internal error in coverage.validate" in e for e in errs)
    # Cross rules needing coverage should be skipped silently (no X3/X4 markers)
    assert not any("coverage: ovi" in e and ("omission" in e or "VISUALISED" in e or "in no scene" in e) for e in errs)


def test_robustness_huge_ranges():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Set huge non-overlapping ranges for scenes
    for i, sc in enumerate(docs["scenes"]["scenes"]):
        start = 1 + i * 10**12
        end = start + 10**12 - 1
        sc["ovi_range"] = [start, end]
    # Set huge ranges for events (non-overlapping with each other)
    for i, ev in enumerate(docs["story_map"]["events"]):
        start = 1 + i * 10**12
        end = start + 10**12 - 1
        ev["ovi_range"] = [start, end]
    errs = agg.validate_all(1, docs, ctx)
    # Should complete quickly (no timeout) and return a list (no exception)
    assert isinstance(errs, list)


def test_export_schemas(tmp_path):
    out_dir = tmp_path / "schemas"
    paths = agg.export_schemas(out_dir)
    assert len(paths) == 9
    for p in paths:
        assert p.exists()
        content = p.read_text(encoding="utf-8")
        assert content.endswith("\n")
        json.loads(content)  # valid JSON
    # Second call should raise FileExistsError
    try:
        agg.export_schemas(out_dir)
        assert False, "expected FileExistsError"
    except FileExistsError:
        pass
    # Files unchanged
    for p in paths:
        assert p.exists()


def test_main_exit_codes(tmp_path, capsys):
    # Create minimal valid docs
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    for unit in agg.UNITS:
        (docs_dir / f"{unit}.json").write_text(json.dumps(BASE_DOCS[unit]), encoding="utf-8")
    ctx_file = tmp_path / "ctx.json"
    ctx_file.write_text(json.dumps(BASE_CTX), encoding="utf-8")

    # Exit 0: valid
    rc = agg.main(["--adhyay", "1", "--docs-dir", str(docs_dir), "--ctx", str(ctx_file)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "0 error(s)" in out

    # Exit 1: invalid (break X1)
    bad_docs = copy.deepcopy(BASE_DOCS)
    bad_docs["story_map"]["ovi_types"] = [{"ovi": 999, "type": "STORY"}]
    bad_docs["story_map"]["events"] = []
    (docs_dir / "story_map.json").write_text(json.dumps(bad_docs["story_map"]), encoding="utf-8")
    rc = agg.main(["--adhyay", "1", "--docs-dir", str(docs_dir), "--ctx", str(ctx_file)])
    assert rc == 1
    out = capsys.readouterr().out
    assert "1 error(s)" in out or "error(s)" in out

    # Exit 2: unreadable JSON
    (docs_dir / "coverage.json").write_text("not json", encoding="utf-8")
    rc = agg.main(["--adhyay", "1", "--docs-dir", str(docs_dir), "--ctx", str(ctx_file)])
    assert rc == 2
    out = capsys.readouterr().out
    assert "refused:" in out

    # Exit 2: export-schemas with existing file
    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()
    (schema_dir / "stage1_story_map.schema.json").write_text("{}", encoding="utf-8")
    rc = agg.main(["--adhyay", "1", "--docs-dir", str(docs_dir), "--export-schemas", str(schema_dir)])
    assert rc == 2
    out = capsys.readouterr().out
    assert "refused:" in out
```
