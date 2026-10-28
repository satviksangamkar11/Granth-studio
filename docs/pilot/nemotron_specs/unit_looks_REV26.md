# FIX CALL: return BOTH files in full: `scripts/pipeline/stage1/looks.py` and `tests/test_stage1_looks.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
.....................................                                    [100%]
37 passed in 0.05s

```

## SPEC
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



## CURRENT MODULE scripts/pipeline/stage1/looks.py
```python
from __future__ import annotations

import jsonschema
from jsonschema import Draft202012Validator
from typing import Any

SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "stage1_canon_looks",
    "type": "object",
    "additionalProperties": False,
    "required": ["adhyay", "entries"],
    "properties": {
        "adhyay": {
            "type": "integer",
            "minimum": 1,
            "maximum": 21,
        },
        "entries": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["entity_id", "kind", "state_id", "look", "source_ovis", "basis"],
                "properties": {
                    "entity_id": {"type": "string"},
                    "kind": {"type": "string", "enum": ["character", "place", "prop"]},
                    "state_id": {"type": "string"},
                    "look": {"type": "string", "minLength": 1, "maxLength": 400},
                    "source_ovis": {
                        "type": "array",
                        "minItems": 1,
                        "items": {"type": "integer", "minimum": 1},
                    },
                    "basis": {"type": "string", "enum": ["stated", "inferred"]},
                },
            },
        },
    },
}

_validator = Draft202012Validator(SCHEMA)


def _as_set(value: Any) -> set[Any]:
    """ctx lists/sets -> real set; anything else becomes an empty set (never raises)."""
    if isinstance(value, (list, tuple, set, frozenset)):
        try:
            return set(value)
        except TypeError:
            return set()
    return set()


def schema_errors(doc: Any) -> list[str]:
    errors: list[str] = []
    for error in _validator.iter_errors(doc):
        path = "/".join(str(p) for p in error.path) if error.path else "doc"
        errors.append(f"looks {path}: {error.message}")
    return errors


def validate(adhyay: int, doc: Any, docs: dict[str, Any], ctx: dict[str, Any]) -> list[str]:
    messages: list[str] = []
    notes: list[str] = []

    if not isinstance(doc, dict):
        return ["looks doc: not an object"]

    doc_adhyay = doc.get("adhyay")
    if doc_adhyay != adhyay:
        messages.append(f"looks adhyay {doc_adhyay} does not match {adhyay}")

    entries = doc.get("entries")
    if not isinstance(entries, list):
        return messages

    if not isinstance(ctx, dict):
        ctx = {}
    chapter_ovis = _as_set(ctx.get("chapter_ovis"))
    known_states = ctx.get("known_states")
    if not isinstance(known_states, dict):
        known_states = {}

    seen_pairs: set[tuple[str, str]] = set()

    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue

        entity_id = entry.get("entity_id")
        state_id = entry.get("state_id")
        source_ovis = entry.get("source_ovis")

        pair_ok = (
            isinstance(entity_id, str)
            and isinstance(state_id, str)
            and bool(entity_id)
            and bool(state_id)
        )
        item_id = f"{entity_id}:{state_id}" if pair_ok else f"entry[{idx}]"

        if pair_ok:
            pair = (entity_id, state_id)
            if pair in seen_pairs:
                messages.append(f"{item_id}: duplicate entity_id+state_id")
            else:
                seen_pairs.add(pair)

        if isinstance(source_ovis, list):
            for ovi in source_ovis:
                try:
                    inside = ovi in chapter_ovis
                except TypeError:
                    inside = False
                if not inside:
                    messages.append(f"{item_id}: source_ovi {ovi} not in chapter_ovis")

        if isinstance(entity_id, str) and isinstance(state_id, str):
            known = _as_set(known_states.get(entity_id))
            if state_id in known:
                messages.append(f"{entity_id}: known state {state_id} redecided")

    messages.extend(notes)
    return messages

```

## CURRENT TESTS tests/test_stage1_looks.py
```python
import copy
import importlib.util
from pathlib import Path

import pytest

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


def get_parent(doc, path):
    cur = doc
    for p in path[:-1]:
        cur = cur[int(p)] if isinstance(p, int) else cur[p]
    return cur, path[-1]


def set_at(base, path, value):
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    if isinstance(parent, list):
        assert isinstance(key, int) and 0 <= key < len(parent), "index out of range"
    parent[key] = value
    assert doc != base, "no-op mutation"
    return doc


def delete_at(base, path):
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    if isinstance(parent, list):
        assert isinstance(key, int) and 0 <= key < len(parent), "index out of range"
    del parent[key]
    assert doc != base, "no-op mutation"
    return doc


def append_at(base, path, value):
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    assert isinstance(parent, list) and isinstance(key, str), "append requires list parent"
    parent.append(value)
    assert doc != base, "no-op mutation"
    return doc


def base():
    return {"docs": copy.deepcopy(BASE_DOCS), "ctx": copy.deepcopy(CTX)}


SCHEMA_CASES = [
    ("valid", None, None, []),
    ("missing_adhyay", ["docs", "looks", "adhyay"], None, "adhyay"),
    ("adhyay_zero", ["docs", "looks", "adhyay"], 0, "adhyay"),
    ("adhyay_22", ["docs", "looks", "adhyay"], 22, "adhyay"),
    ("adhyay_string", ["docs", "looks", "adhyay"], "1", "adhyay"),
    ("missing_entries", ["docs", "looks", "entries"], None, "entries"),
    ("entries_not_array", ["docs", "looks", "entries"], "x", "entries"),
    ("entries_empty", ["docs", "looks", "entries"], [], []),
    ("missing_entity_id", ["docs", "looks", "entries", 0, "entity_id"], None, "entity_id"),
    ("missing_kind", ["docs", "looks", "entries", 0, "kind"], None, "kind"),
    ("missing_state_id", ["docs", "looks", "entries", 0, "state_id"], None, "state_id"),
    ("missing_look", ["docs", "looks", "entries", 0, "look"], None, "look"),
    ("missing_source_ovis", ["docs", "looks", "entries", 0, "source_ovis"], None, "source_ovis"),
    ("missing_basis", ["docs", "looks", "entries", 0, "basis"], None, "basis"),
    ("kind_invalid", ["docs", "looks", "entries", 0, "kind"], "invalid", "kind"),
    ("basis_invalid", ["docs", "looks", "entries", 0, "basis"], "invalid", "basis"),
    ("source_ovis_not_array", ["docs", "looks", "entries", 0, "source_ovis"], "x", "source_ovis"),
    ("source_ovis_empty", ["docs", "looks", "entries", 0, "source_ovis"], [], "source_ovis"),
    ("source_ovis_zero", ["docs", "looks", "entries", 0, "source_ovis"], [0], "source_ovis"),
    ("source_ovis_string", ["docs", "looks", "entries", 0, "source_ovis"], ["1"], "source_ovis"),
    ("look_empty", ["docs", "looks", "entries", 0, "look"], "", "look"),
    ("look_too_long", ["docs", "looks", "entries", 0, "look"], "x" * 401, "look"),
    ("extra_root_field", ["docs", "looks", "extra"], "x", "extra"),
    ("extra_entry_field", ["docs", "looks", "entries", 0, "extra"], "x", "extra"),
]


@pytest.mark.parametrize("name,path,value,expected_field", SCHEMA_CASES)
def test_schema_errors(name, path, value, expected_field):
    b = base()
    if path:
        if value is None:
            b = delete_at(b, path)
        else:
            b = set_at(b, path, value)
    errors = looks.schema_errors(b["docs"]["looks"])
    if expected_field == []:
        assert errors == []
    else:
        assert any(expected_field in e for e in errors), f"{name}: {errors}"


SEMANTIC_CASES = [
    ("valid", None, None, []),
    ("adhyay_mismatch", ["docs", "looks", "adhyay"], 2, "adhyay"),
    ("source_ovi_unknown", ["docs", "looks", "entries", 0, "source_ovis"], [99], "gajanan_maharaj"),
    ("known_state_redecided", ["docs", "looks", "entries", 0, "state_id"], "adult_youth_v1", "redecided"),
    # real duplicate pair: entry 1 becomes an exact copy of entry 0
    # -> (gajanan_maharaj, adult_youth_v2) appears twice
    (
        "duplicate_entity_state",
        ["docs", "looks", "entries", 1],
        copy.deepcopy(BASE_DOCS["looks"]["entries"][0]),
        "gajanan_maharaj",
    ),
    # same state_id on a DIFFERENT entity is NOT a duplicate pair
    ("same_state_different_entity", ["docs", "looks", "entries", 1, "state_id"], "adult_youth_v2", []),
    ("new_state_known_entity", ["docs", "looks", "entries", 0, "state_id"], "adult_youth_v3", []),
    ("unknown_entity", ["docs", "looks", "entries", 0, "entity_id"], "new_entity", []),
]


@pytest.mark.parametrize("name,path,value,expected_keyword", SEMANTIC_CASES)
def test_validate_errors(name, path, value, expected_keyword):
    b = base()
    if path:
        b = set_at(b, path, value)
    errors = looks.validate(1, b["docs"]["looks"], b["docs"], b["ctx"])
    if expected_keyword == []:
        assert errors == [], f"{name}: {errors}"
    else:
        assert any(expected_keyword in e for e in errors), f"{name}: {errors}"


ODD_DOCS = [
    None,
    [],
    "x",
    {"entries": None},
    {"entries": [None, 1, {"entity_id": ["x"]}]},
]


@pytest.mark.parametrize("doc", ODD_DOCS)
def test_validate_odd_doc_no_raise(doc):
    """validate must never raise on odd data; result must be a list."""
    result = looks.validate(1, doc, BASE_DOCS, CTX)
    assert isinstance(result, list)
    # ensure the catch-all message is not present (module has no catch-all, but guard against future regressions)
    assert not any("malformed structure" in e for e in result)

```

## ROUND 9 FINDINGS: TESTS ONLY. The module must be returned UNCHANGED, character for character (unless one of your new rows proves a real module defect against the SPEC; then fix the module and say so in no prose). Add data rows to the existing tables (schema-valid rows for each enum value; schema-invalid rows for each bound/minLength) so that removing that schema rule fails a test. Keep every existing test and every assertion 'not any("malformed structure" in e ...)' unchanged. Only the items listed for YOUR unit 'looks' in the report below apply; if there are none for 'looks', return both files unchanged. Return BOTH complete FILE blocks.
### Haiku round 9 (use only the section for looks)
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
