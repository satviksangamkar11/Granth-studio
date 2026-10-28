# FIX CALL: return BOTH files in full: `scripts/pipeline/stage1/voices.py` and `tests/test_stage1_voices.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
..........................................                               [100%]
42 passed in 0.06s

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
                    "status": {"type": "string", "enum": ["RECURRING", "NEW_PROPOSED"]}
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

    # Rule: a character already RECURRING must not be listed twice
    for char, entries in char_entries.items():
        recurring_count = sum(1 for e in entries if e.get("status") == "RECURRING")
        if recurring_count > 1:
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
        {"character_id": "extra_char", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "female", "status": "NEW_PROPOSED"},
    ], "extra_char"),
    # Another case: two non-narrators sharing a voice_key
    ("cast", [
        {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
        {"character_id": "char1", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "male", "status": "NEW_PROPOSED"},
        {"character_id": "char2", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "female", "status": "NEW_PROPOSED"},
    ], "char1"),
    # Two NEW_PROPOSED entries for same speaking character
    ("cast", [
        {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
        {"character_id": "gajanan_maharaj", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "male", "status": "NEW_PROPOSED"},
        {"character_id": "gajanan_maharaj", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "male", "status": "NEW_PROPOSED"},
    ], "gajanan_maharaj"),
    # Recurring character outside speaking_characters listed twice (distinct voice_keys to isolate rule)
    ("cast", [
        {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
        {"character_id": "gajanan_maharaj", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "male", "status": "RECURRING"},
        {"character_id": "other_char", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
        {"character_id": "other_char", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "male", "status": "RECURRING"},
    ], "other_char"),
    # Narrator and two others sharing a saved key - should error for the two non-narrators
    ("cast", [
        {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
        {"character_id": "charA", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "NEW_PROPOSED"},
        {"character_id": "charB", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "female", "status": "NEW_PROPOSED"},
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

```

## ROUND 4 REVIEW FINDINGS (both reviewers reproduced the voices and briefs items). Apply what the SPEC supports. Keep the catch-all guard in validate where present. Tests: isolate the rule (only that rule violated), assert the offending id/field, never wording the spec does not quote, and where a test only checks isinstance(list), also assert no error contains 'malformed structure'. All existing tests must still pass. Return BOTH FILE blocks complete.
Specific: voices: reject two or more cast entries for one character when ANY of them has status RECURRING (message contains the character id and 'recurring character listed twice'), add an isolated test. shots: replace the assertion on 'not in scene' by one on the shot id; add the 'no malformed structure' assertion to the isinstance-only odd-data tests; the invalid need_new.class row must be tested via schema_errors with preset NEED_NEW. briefs: the missing-scene message must say the scene does NOT exist, e.g. '<image_id>: scene <scene_id> does not exist'; keep the test asserting the image id. looks: add a parametrized odd-data test: validate(1, doc, docs, ctx) with doc None, [], 'x', a dict whose entries is None, and entries containing None, 1, {'entity_id': ['x']}; the result must be a list; fix the module if any input raises.
### Codex round 4
## Verdict: FIX FIRST

### story_map

No verified defect identified.

### coverage

No verified defect identified. The earlier numeric-string conversion has been removed.

### scenes

1. **Low — [test_stage1_scenes.py:177](</D:/aai work/granthstudio/tests/test_stage1_scenes.py:177>):** The duplicate-scene test uses ovis 10–12, outside the baseline chapter. The resulting error also contains `S1`, so the test can pass without duplicate-ID detection. Add those ovis to the test context or otherwise isolate the duplicate-ID violation.

### shots

1. **Low — [test_stage1_shots.py:170](</D:/aai work/granthstudio/tests/test_stage1_shots.py:170>):** The invalid `need_new.class` row still fails the null requirement for the existing preset. The new test at line 342 calls semantic `validate`, not `schema_errors`, and only checks that it returns a list. Test `schema_errors` with preset `NEED_NEW` and assert an error for `class`.
2. **Low — [test_stage1_shots.py:381](</D:/aai work/granthstudio/tests/test_stage1_shots.py:381>):** The test asserts `not in scene`, wording the spec does not quote. Assert the shot ID in an error separate from the quoted uncovered-line error.
3. **Low — [test_stage1_shots.py:356](</D:/aai work/granthstudio/tests/test_stage1_shots.py:356>):** This assertion and the analogous assertions at lines 363 and 370 only check for a list; the catch-all makes them pass when validation fails internally. Also assert that no error contains `malformed structure`.

### briefs

No verified defect identified.

### looks

No verified defect identified.

### voices

1. **Medium — [voices.py:113](</D:/aai work/granthstudio/scripts/pipeline/stage1/voices.py:113>):** A non-speaking character listed once as `RECURRING` and once as `NEW_PROPOSED` returns no error. The spec prohibits listing a character already `RECURRING` twice. Reject multiple entries when any entry is `RECURRING`, and add an isolated test.

### sounds

No verified defect identified.

### questions

No verified defect identified.

The workspace is read-only, so I could not write the report file. I reproduced the mixed-status voices case, but could not run the suite because the available Python lacks `jsonschema` and the project virtual environment could not start. I did not independently reproduce every Round 3 finding or complete an exhaustive review of all nine units; “no verified defect” is therefore not a clean bill of health.### Haiku round 4
# Stage 1 unit modules: Round 4 review (read-only)

Scope: `scripts/pipeline/stage1/{story_map,coverage,scenes,shots,briefs,looks,voices,sounds,questions}.py`, `tests/test_stage1_<unit>.py`, against `docs/pilot/nemotron_specs/unit_<unit>.md`, `stage1_base.json`, `STAGE1_RULES.md`.

Evidence: `uv run pytest -q --tb=short tests/test_stage1_*.py` gives **418 passed**. Defects below were reproduced by calling the module in memory (no project file written, no network). Fuzzing: about 6,600 validate and schema_errors calls, with every leaf of each document replaced by 14 odd values (None, 0, 7, -1, str, list, dict, bool, float, nested list), plus top-level None/list/str/{} documents. No raise was found from document data in any module. Out of scope and not counted: `coverage.validate` and `scenes.validate` raise TypeError when a ctx list (e.g. `chapter_ovis`) is None. No print, env, key or secret handling was found in any module or test.

## Verdict: FIX FIRST

---

## Round 3 findings: status

| Unit | Round 3 finding | Status |
|---|---|---|
| coverage | High: `covered_by: "²"` raises ValueError | FIXED (verified: returns the covered_by error, no raise) |
| scenes | 1 nine `isinstance`-only checks (catch-all) | FIXED (tests now assert no "malformed structure"; scenes.validate has no catch-all) |
| scenes | 2 duplicate-scene test asserts "S1" with overlaps | FIXED (verified: only "S1: duplicate scene id" contains S1) |
| scenes | 3 order test asserts "S1" also matched by unknown-line error | FIXED (verified: `S1: line_ids not in script order` is the only S1 message) |
| shots | 1 twelve `isinstance`-only checks | FIXED |
| shots | 2 class enum row uses preset `01_establishing_shot` | FIXED by `test_need_new_class_enum` (preset NEED_NEW; message contains "class"). The table row at line 170 still exercises only the null-type branch (residual, not a defect) |
| shots | 3 "S2" matched uncovered-line error | FIXED (verified: S2 line_ids emptied; only "S2: scene has no shots" contains S2) |
| shots | 4 test asserts "not in scene" | STILL OPEN (defect S-1) |
| briefs | 1 six `isinstance`-only checks | FIXED |
| briefs | 2 test asserts "scene exists" | FIXED (test asserts "s99_test"). The message itself is wrong, see B-1 |
| voices | 1 RECURRING + NEW_PROPOSED not flagged when not speaking | STILL OPEN (defect V-1, verified) |
| sounds | 1 test asserts "document must be an object" | FIXED (asserts "sounds" prefix) |
| sounds | 2 seven `isinstance`-only checks | FIXED |
| questions | none | n/a |
| looks | none | n/a |

---

## story_map

none.

## coverage

none.

## scenes

none.

## shots

1. `tests/test_stage1_shots.py:381` (class 4): `assert any("S1-1" in e and "not in scene" in e for e in errs)`. The spec quotes no "not in scene" phrase; the rule is only "beat_line_ids belong to the scene". Verified: the message is `S1-1: beat line S2-L1 not in scene S1`. Fix: `assert any("S1-1" in e for e in errs)` and keep the separate `"S2-L1" in e and "line is in no shot beat" in e` check.

## briefs

1. `scripts/pipeline/stage1/briefs.py:160` (class 1, message wrong): the missing-scene message is `f"{img_id}: scene exists"`. It is emitted when the scene does NOT exist. Verified: a brief with scene_id S99 returns `['s99_x: scene exists', ...]`. Fix: `messages.append(f"{img_id}: scene {scene_id} does not exist")`. The test at `tests/test_stage1_briefs.py:415` asserts only "s99_test" and still passes after the fix.

## looks

1. `tests/test_stage1_looks.py` (class 3, spec no-raise requirement has no test): the spec requires validate to "never raise on odd data", but the file has no odd-data test (grep for odd/raise/no_raise finds nothing). `looks.validate` has no catch-all, so a future regression would go unnoticed. Fix: add a parametrized test that passes `validate(1, doc, docs, ctx)` with doc set to None, [], "x", a dict whose `entries` is None, and entries containing `None`, `1`, `{"entity_id": ["x"]}`, and asserts the result is a list.

## voices

1. `scripts/pipeline/stage1/voices.py:111-114` (class 1): the rule "a character already RECURRING must not be listed twice" counts only RECURRING entries (`recurring_count > 1`). Verified: cast entries `gajanan_maharaj` RECURRING plus `gajanan_maharaj` NEW_PROPOSED, with speaking_characters = `["narrator"]`, returns `[]`. Fix:
   ```python
   for char, entries in char_entries.items():
       if len(entries) > 1 and any(e.get("status") == "RECURRING" for e in entries):
           messages.append(f"{char}: recurring character listed twice")
   ```
   Add a test row for this case (non-speaking character, one RECURRING and one NEW_PROPOSED entry, expecting "recurring character listed twice").

## sounds

none.

## questions

none.

---

## Defects per unit (Round 4)

| Unit | Defects |
|---|---|
| story_map | 0 |
| coverage | 0 |
| scenes | 0 |
| shots | 1 |
| briefs | 1 |
| looks | 1 |
| voices | 1 |
| sounds | 0 |
| questions | 0 |
| **Total** | **4** |
