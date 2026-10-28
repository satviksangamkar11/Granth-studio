# FIX CALL: return BOTH files in full: `scripts/pipeline/stage1/voices.py` and `tests/test_stage1_voices.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
...........................................                              [100%]
43 passed in 0.06s

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
            {"character_id": "other_char", "voice_key": "other", "voice_id": "ZZZZZZZZZZ", "gender": "male", "status": "NEW_PROPOSED"},
        ],
    }
    errs = validate(1, doc, b["docs"], ctx)
    # Should only have the recurring duplicate error for other_char
    assert any("other_char" in e for e in errs)

```

## ROUND 9 FINDINGS: TESTS ONLY. The module must be returned UNCHANGED, character for character (unless one of your new rows proves a real module defect against the SPEC; then fix the module and say so in no prose). Add data rows to the existing tables (schema-valid rows for each enum value; schema-invalid rows for each bound/minLength) so that removing that schema rule fails a test. Keep every existing test and every assertion 'not any("malformed structure" in e ...)' unchanged. Only the items listed for YOUR unit 'voices' in the report below apply; if there are none for 'voices', return both files unchanged. Return BOTH complete FILE blocks.
### Haiku round 9 (use only the section for voices)
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
