# FIX CALL: return BOTH files in full: `scripts/pipeline/stage1/looks.py` and `tests/test_stage1_looks.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
................................                                         [100%]
32 passed in 0.05s

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
