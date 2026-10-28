# FIX CALL: return BOTH files in full: `scripts/pipeline/stage1/voices.py` and `tests/test_stage1_voices.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
............................                                             [100%]
28 passed in 0.05s

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


def validate(adhyay: int, doc: dict, docs: dict, ctx: dict) -> list[str]:
    messages = []

    # Adhyay check
    doc_adhyay = doc.get("adhyay")
    if doc_adhyay != adhyay:
        messages.append(f"voices adhyay {doc_adhyay} does not match {adhyay}")

    # Convert ctx lists/sets to sets
    speaking_characters = set(ctx.get("speaking_characters", []))
    saved_voices = ctx.get("saved_voices", {})

    cast = doc.get("cast", [])

    # Build lookup: character_id -> list of entries (skip None entries)
    char_entries = {}
    for entry in cast:
        if entry is None:
            continue
        cid = entry.get("character_id")
        if cid not in char_entries:
            char_entries[cid] = []
        char_entries[cid].append(entry)

    # Rule: every speaking_character has exactly one cast entry
    for char in speaking_characters:
        entries = char_entries.get(char, [])
        if len(entries) == 0:
            messages.append(f"{char}: no voice assigned")
        elif len(entries) > 1:
            # A character already RECURRING must not be listed twice
            for e in entries:
                if e.get("status") == "RECURRING":
                    messages.append(f"{char}: recurring character listed twice")
                    break

    # Rule: voice_key must be in saved_voices and voice_id must match
    for entry in cast:
        if entry is None:
            continue
        char = entry.get("character_id")
        vkey = entry.get("voice_key")
        vid = entry.get("voice_id")
        if vkey not in saved_voices:
            messages.append(f"{char}: voice not in the saved cast")
        elif saved_voices[vkey] != vid:
            messages.append(f"{char}: voice not in the saved cast")

    # Rule: two characters must not share a voice_key unless one is the narrator
    voice_key_to_chars = {}
    for entry in cast:
        if entry is None:
            continue
        vkey = entry.get("voice_key")
        char = entry.get("character_id")
        if vkey not in voice_key_to_chars:
            voice_key_to_chars[vkey] = []
        voice_key_to_chars[vkey].append(char)

    for vkey, chars in voice_key_to_chars.items():
        if len(chars) > 1:
            # Check if one is narrator - sharing with narrator is allowed
            if "narrator" not in chars:
                # Report for each character sharing the key
                for char in chars:
                    messages.append(f"{char}: voice key shared with another character")

    return messages

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
])
def test_schema(path, value, keyword):
    b = base()
    if path is None:
        assert schema_errors(b["docs"]["voices"]) == []
    else:
        doc = mutate_doc(b, path, value)
        errs = schema_errors(doc["docs"]["voices"])
        assert errs
        assert any(keyword in e for e in errs)


@pytest.mark.parametrize("path,value,keyword", [
    (None, None, None),
    ("adhyay", 2, "adhyay"),
    # Remove cast entry for narrator -> no voice assigned
    ("cast.0", None, "narrator: no voice assigned"),
    # Remove cast entry for gajanan_maharaj -> no voice assigned
    ("cast.1", None, "gajanan_maharaj: no voice assigned"),
    ("cast.0.voice_key", "unknown", "narrator: voice not in the saved cast"),
    # Use valid-length but wrong voice_id
    ("cast.0.voice_id", "x" * 10, "narrator: voice not in the saved cast"),
    # Duplicate narrator entry (RECURRING listed twice)
    ("cast", [
        {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
        {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
        {"character_id": "gajanan_maharaj", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "male", "status": "RECURRING"},
    ], "narrator: recurring character listed twice"),
    # Two non-narrators sharing a voice_key (gajanan) -> forbidden
    ("cast", [
        {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
        {"character_id": "gajanan_maharaj", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "male", "status": "RECURRING"},
        {"character_id": "extra_char", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "female", "status": "NEW_PROPOSED"},
    ], "extra_char: voice key shared with another character"),
    # Another case: two non-narrators sharing a voice_key
    ("cast", [
        {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
        {"character_id": "char1", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "male", "status": "NEW_PROPOSED"},
        {"character_id": "char2", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "female", "status": "NEW_PROPOSED"},
    ], "char1: voice key shared with another character"),
    ("ctx.speaking_characters", [], None),
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
    else:
        doc = mutate_doc(b, path, value)
        errs = validate(1, doc["docs"]["voices"], doc["docs"], doc["ctx"])
        if keyword is None:
            assert errs == []
        else:
            assert errs
            assert any(keyword in e for e in errs)

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
