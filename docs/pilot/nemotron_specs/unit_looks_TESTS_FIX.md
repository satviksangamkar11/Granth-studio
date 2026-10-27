# FIX CALL for the test file `tests/test_stage1_looks.py` (write ONLY that file, one FILE block). Two independent reviewers (Codex, Haiku) found real defects in your previous version (shown below). Repair ALL of them. The unit spec, BASE data and clarifications follow. HARD RULES that the previous attempts broke:
1. Write ONE robust helper set at the top and use it everywhere: `get_parent(doc, path)` that walks a path list where an int part indexes a list and a str part indexes a dict; `set_at(base, path, value)`, `delete_at(base, path)`, `append_at(base, path, value)` (all work on a deep copy and handle list indexes and dict keys, never index a list with a string). EVERY mutation must be proven to change the document: the helper asserts `mutated != base` (a no-op mutation fails loudly). Never address a list element that does not exist in BASE (append instead).
2. Each row changes exactly ONE thing and leaves everything else valid; contexts (script lines, saved voices, presets) stay complete unless the row is about that context. Each row asserts the item id AND only the keyword the spec QUOTES; for rules with no quoted phrase assert only the item id (never invented words like unique, outside, prefix, shared, empty, mismatch, not exist).
3. Positive rows assert `[]` exactly. A "twice/duplicate" rule needs a real duplicate (append a second entry). A rule that is schema-level in the spec is tested through `schema_errors`; a rule the spec makes semantic is tested ONLY through `validate` (never expect jsonschema to reject reversed ranges or empty names unless the spec's schema says so). jsonschema reports required/additionalProperties errors at the PARENT path: assert the offending field name appears in the message, never a child path.
4. Required-field rows DELETE each required field from a deep copy (root fields and nested objects); extra-key rows ADD one unknown key to an otherwise valid object at the root and at every nested object; every enum has one invalid-value row.
5. `validate(adhyay, doc, docs, ctx)`: `docs` is the dict of ALL nine documents (use only the ones the unit spec lists; pass {} for absent ones) and `ctx` is separate (never `docs["ctx"]`).
6. ids are strings and ovis are integers (covered_by uses an integer ovi or a line id string).
7. Keep it compact (<= 170 lines), synthetic only, loading the module by path with importlib as the unit spec says.
Reply with exactly one FILE block: FILE: tests/test_stage1_looks.py

## CODEX FINDINGS FOR THIS UNIT
- **looks — Medium:** `test_validate_errors` row **110** changes only Bankatlal’s state ID; the entity/state pairs remain distinct. It wrongly expects a duplicate error and supplies no actual duplicate-pair test. Assertions **108,110,125** mandate unquoted `source_ovis`/`duplicate` wording without requiring the affected entity ID.

## HAIKU FINDINGS FOR THIS UNIT
(2) Line 110 changes entries[1].state_id but leaves entity_id "bankatlal", so no entity+state duplicate exists. Fix: set entries[1].entity_id = "gajanan_maharaj" with state adult_youth_v2. (4) Line 108 asserts "source_ovis"; "duplicate" on line 110 is not quoted.

## UNIT SPEC (binding)
# UNIT SPEC: Stage 1 document `looks` (schema `stage1_canon_looks`)
This is ONE unit of the Stage 1 contract (the master spec `stage1_v2.md` was split because one big spec gave unreliable tests). Keep the unit small and exact.
Module: `scripts/pipeline/stage1/looks.py`. Tests: `tests/test_stage1_looks.py`. Style: `from __future__ import annotations`, standard library plus `jsonschema`; no print, no network, nothing at import time; tests use only the BASE data below and `tmp_path`; the test file loads the module by path with importlib (`ROOT = Path(__file__).resolve().parents[1]`, `ROOT / "scripts" / "pipeline" / "stage1" / "looks.py"`).

## Module API (exactly this)
- `SCHEMA`: dict, JSON Schema draft 2020-12 for the document, `additionalProperties: false` on EVERY object (nested too), `$schema` = "https://json-schema.org/draft/2020-12/schema", `title` = "stage1_canon_looks".
- `schema_errors(doc) -> list[str]`: one message per jsonschema error, formatted "looks <path>: <message>" (path joined by "/", "doc" when empty).
- `validate(adhyay, doc, docs, ctx) -> list[str]`: SEMANTIC checks only (the schema has already passed; it must still never raise on odd data). `docs` is a dict of ALL nine documents (key names: story_map, coverage, scenes, shots, briefs, looks, voices, sounds, questions; a missing one counts as empty), `ctx` the context dict (keys: script_line_ids list, core_line_ids set, chapter_ovis set, unfilmed_ovis set, preset_ids set, sound_ids set, saved_voices dict voice_key->voice_id, speaking_characters set, known_states dict entity_id->set of state ids). Lists in ctx may arrive as lists or sets: convert with set(). Notes (messages that start with "note: ") come AFTER error messages. Include the adhyay check first: "looks adhyay <n> does not match <adhyay>".

## Ids and common types
scene_id `^S[0-9]{1,2}$`; shot_id `^S[0-9]{1,2}-[0-9]{1,2}$`; line_id `^S[0-9]{1,2}-L[0-9]{1,3}$`; image id (Stage 1 brief) `^s[0-9]{1,2}_[a-z][a-z0-9_]{0,40}$`; ovi = integer >= 1; adhyay = integer 1..21; text = string 1..400 chars; preset id = string matching `^[0-9]{2}_[a-z0-9_]+$`; sound id `^(bed|fx)_[a-z0-9_]+$`.

## The document shape (from the master spec)
6. `stage1_canon_looks`: `entries`: array of {entity_id, kind: character|place|prop, state_id, look text, source_ovis [ovi...] (min 1), basis: stated|inferred}. No other fields (no events, no dialogue).

## Semantic rules of this unit (master spec step 8)
8. looks: source_ovis inside `chapter_ovis`; an entry whose entity_id is a key of `known_states` and whose state_id is already in `known_states[entity_id]` is an error ("<entity>: known state <state_id> redecided"); a state_id that is NOT yet known for a known entity is allowed (a new state); entity_id+state_id unique inside the document.

Messages: tests assert only the quoted keywords/phrases of the rules plus the item id; for rules without a quoted phrase the message is `<item id>: <condition in plain words>`.

## BASE data (valid, note-free; the baseline for EVERY test; `validate(1, BASE_DOCS["looks"], BASE_DOCS, CTX)` must return [] and `schema_errors` must return [])
File `docs/pilot/nemotron_specs/stage1_base.json` has the keys "docs" (the nine documents) and "ctx". The test file must embed its own copy of what it needs as Python literals (copy the values below exactly):
```json
{
 "docs": {
  "looks": {
   "adhyay": 1,
   "entries": [
    {
     "entity_id": "gajanan_maharaj",
     "kind": "character",
     "state_id": "adult_youth_v2",
     "look": "slim adult, cropped hair, open frayed grey-white vest",
     "source_ovis": [
      1
     ],
     "basis": "stated"
    },
    {
     "entity_id": "bankatlal",
     "kind": "character",
     "state_id": "merchant_v1",
     "look": "cream turban, sage coat",
     "source_ovis": [
      2
     ],
     "basis": "inferred"
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



## YOUR PREVIOUS tests/test_stage1_looks.py (repair it)
```python
import copy
import pytest
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "pipeline" / "stage1" / "looks.py"
spec = importlib.util.spec_from_file_location("looks", MODULE_PATH)
looks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(looks)

BASE_DOCS = {
    "looks": {
        "adhyay": 1,
        "entries": [
            {
                "entity_id": "gajanan_maharaj",
                "kind": "character",
                "state_id": "adult_youth_v2",
                "look": "slim adult, cropped hair, open frayed grey-white vest",
                "source_ovis": [1],
                "basis": "stated",
            },
            {
                "entity_id": "bankatlal",
                "kind": "character",
                "state_id": "merchant_v1",
                "look": "cream turban, sage coat",
                "source_ovis": [2],
                "basis": "inferred",
            },
        ],
    }
}
CTX = {
    "script_line_ids": ["S1-L1", "S1-L2", "S2-L1"],
    "core_line_ids": ["S1-L1", "S2-L1"],
    "chapter_ovis": [1, 2, 3, 4, 5, 6, 7, 8, 9],
    "unfilmed_ovis": [],
    "preset_ids": ["01_establishing_shot", "03_slow_cinematic_push"],
    "sound_ids": ["bed_roadside_quiet", "fx_door_wood_creak"],
    "saved_voices": {"narrator": "CXkeo30p0Sk4Lr0TAzeo", "gajanan": "8fqGzH80bdkm2UseeV9f"},
    "speaking_characters": ["narrator", "gajanan_maharaj"],
    "known_states": {"gajanan_maharaj": ["adult_youth_v1"]},
}


def base():
    return {"docs": copy.deepcopy(BASE_DOCS), "ctx": copy.deepcopy(CTX)}


def mutate(obj, path, value):
    parts = path.split(".")
    target = obj
    for part in parts[:-1]:
        target = target[int(part)] if part.isdigit() else target[part]
    last = parts[-1]
    if value is None:
        del target[last]
    else:
        target[last] = value
    return obj


SCHEMA_CASES = [
    ("valid", None, None, []),
    ("missing_adhyay", "docs.looks.adhyay", None, "adhyay"),
    ("adhyay_zero", "docs.looks.adhyay", 0, "adhyay"),
    ("adhyay_22", "docs.looks.adhyay", 22, "adhyay"),
    ("adhyay_string", "docs.looks.adhyay", "1", "adhyay"),
    ("missing_entries", "docs.looks.entries", None, "entries"),
    ("entries_not_array", "docs.looks.entries", "x", "entries"),
    ("entries_empty", "docs.looks.entries", [], []),  # valid per spec
    ("missing_entity_id", "docs.looks.entries.0.entity_id", None, "entity_id"),
    ("missing_kind", "docs.looks.entries.0.kind", None, "kind"),
    ("missing_state_id", "docs.looks.entries.0.state_id", None, "state_id"),
    ("missing_look", "docs.looks.entries.0.look", None, "look"),
    ("missing_source_ovis", "docs.looks.entries.0.source_ovis", None, "source_ovis"),
    ("missing_basis", "docs.looks.entries.0.basis", None, "basis"),
    ("kind_invalid", "docs.looks.entries.0.kind", "invalid", "kind"),
    ("basis_invalid", "docs.looks.entries.0.basis", "invalid", "basis"),
    ("source_ovis_not_array", "docs.looks.entries.0.source_ovis", "x", "source_ovis"),
    ("source_ovis_empty", "docs.looks.entries.0.source_ovis", [], "source_ovis"),
    ("source_ovis_zero", "docs.looks.entries.0.source_ovis", [0], "source_ovis"),
    ("source_ovis_string", "docs.looks.entries.0.source_ovis", ["1"], "source_ovis"),
    ("look_empty", "docs.looks.entries.0.look", "", "look"),
    ("look_too_long", "docs.looks.entries.0.look", "x" * 401, "look"),
    ("extra_root_field", "docs.looks.extra", "x", "extra"),
    ("extra_entry_field", "docs.looks.entries.0.extra", "x", "extra"),
]


@pytest.mark.parametrize("name,path,value,expected_field", SCHEMA_CASES)
def test_schema_errors(name, path, value, expected_field):
    b = base()
    if path:
        mutate(b, path, value)
    errors = looks.schema_errors(b["docs"]["looks"])
    if expected_field == []:
        assert errors == []
    else:
        assert any(expected_field in e for e in errors), f"{name}: {errors}"


SEMANTIC_CASES = [
    ("valid", None, None, []),
    ("adhyay_mismatch", "docs.looks.adhyay", 2, "adhyay"),
    ("source_ovi_unknown", "docs.looks.entries.0.source_ovis", [99], "source_ovis"),
    ("known_state_redecided", "docs.looks.entries.0.state_id", "adult_youth_v1", "redecided"),
    ("duplicate_entity_state", "docs.looks.entries.1.state_id", "adult_youth_v2", "duplicate"),
    ("new_state_known_entity", "docs.looks.entries.0.state_id", "adult_youth_v3", []),
    ("unknown_entity", "docs.looks.entries.0.entity_id", "new_entity", []),
]


@pytest.mark.parametrize("name,path,value,expected_keyword", SEMANTIC_CASES)
def test_validate_errors(name, path, value, expected_keyword):
    b = base()
    if path:
        mutate(b, path, value)
    errors = looks.validate(1, b["docs"]["looks"], b["docs"], b["ctx"])
    if expected_keyword == []:
        assert errors == [], f"{name}: {errors}"
    else:
        assert any(expected_keyword in e for e in errors), f"{name}: {errors}"

```
