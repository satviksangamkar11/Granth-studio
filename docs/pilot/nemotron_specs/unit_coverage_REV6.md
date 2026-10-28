# FIX CALL: return BOTH files in full: `scripts/pipeline/stage1/coverage.py` and `tests/test_stage1_coverage.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
...................................                                      [100%]
35 passed in 0.06s

```

## SPEC
# UNIT SPEC: Stage 1 document `coverage` (schema `stage1_coverage`)
This is ONE unit of the Stage 1 contract (the master spec `stage1_v2.md` was split because one big spec gave unreliable tests). Keep the unit small and exact.
Module: `scripts/pipeline/stage1/coverage.py`. Tests: `tests/test_stage1_coverage.py`. Style: `from __future__ import annotations`, standard library plus `jsonschema`; no print, no network, nothing at import time; tests use only the BASE data below and `tmp_path`; the test file loads the module by path with importlib (`ROOT = Path(__file__).resolve().parents[1]`, `ROOT / "scripts" / "pipeline" / "stage1" / "coverage.py"`).

## Module API (exactly this)
- `SCHEMA`: dict, JSON Schema draft 2020-12 for the document, `additionalProperties: false` on EVERY object (nested too), `$schema` = "https://json-schema.org/draft/2020-12/schema", `title` = "stage1_coverage".
- `schema_errors(doc) -> list[str]`: one message per jsonschema error, formatted "coverage <path>: <message>" (path joined by "/", "doc" when empty).
- `validate(adhyay, doc, docs, ctx) -> list[str]`: SEMANTIC checks only (the schema has already passed; it must still never raise on odd data). `docs` is a dict of ALL nine documents (key names: story_map, coverage, scenes, shots, briefs, looks, voices, sounds, questions; a missing one counts as empty), `ctx` the context dict (keys: script_line_ids list, core_line_ids set, chapter_ovis set, unfilmed_ovis set, preset_ids set, sound_ids set, saved_voices dict voice_key->voice_id, speaking_characters set, known_states dict entity_id->set of state ids). Lists in ctx may arrive as lists or sets: convert with set(). Notes (messages that start with "note: ") come AFTER error messages. Include the adhyay check first: "coverage adhyay <n> does not match <adhyay>".

## Ids and common types
scene_id `^S[0-9]{1,2}$`; shot_id `^S[0-9]{1,2}-[0-9]{1,2}$`; line_id `^S[0-9]{1,2}-L[0-9]{1,3}$`; image id (Stage 1 brief) `^s[0-9]{1,2}_[a-z][a-z0-9_]{0,40}$`; ovi = integer >= 1; adhyay = integer 1..21; text = string 1..400 chars; preset id = string matching `^[0-9]{2}_[a-z0-9_]+$`; sound id `^(bed|fx)_[a-z0-9_]+$`.

## The document shape (from the master spec)
2. `stage1_coverage`: `ovis`: array of {ovi, disposition: VISUALISED|NARRATED|QUOTED|MERGED_EQUIVALENT|PROPOSE_OMISSION, reason (text, REQUIRED when PROPOSE_OMISSION or MERGED_EQUIVALENT, else optional), covered_by (line_id or ovi, REQUIRED when MERGED_EQUIVALENT, else optional)}. The schema enforces the REQUIRED rules with `if/then`.

## Semantic rules of this unit (master spec step 4)
4. coverage: every ovi of `chapter_ovis` has exactly one disposition ("ovi <n> has no disposition" / "twice"); PROPOSE_OMISSION is allowed but reported as a NOTE message starting "note: ovi <n> omission proposed, owner approval needed" (notes are returned in the list after the errors); an ovi in `unfilmed_ovis` must not be VISUALISED ("ovi <n> is unfilmed but VISUALISED"); covered_by must refer to a script line id or a chapter ovi.

Messages: tests assert only the quoted keywords/phrases of the rules plus the item id; for rules without a quoted phrase the message is `<item id>: <condition in plain words>`.

## BASE data (valid, note-free; the baseline for EVERY test; `validate(1, BASE_DOCS["coverage"], BASE_DOCS, CTX)` must return [] and `schema_errors` must return [])
File `docs/pilot/nemotron_specs/stage1_base.json` has the keys "docs" (the nine documents) and "ctx". The test file must embed its own copy of what it needs as Python literals (copy the values below exactly):
```json
{
 "docs": {
  "coverage": {
   "adhyay": 1,
   "ovis": [
    {
     "ovi": 1,
     "disposition": "VISUALISED"
    },
    {
     "ovi": 2,
     "disposition": "VISUALISED"
    },
    {
     "ovi": 3,
     "disposition": "NARRATED"
    },
    {
     "ovi": 4,
     "disposition": "QUOTED"
    },
    {
     "ovi": 5,
     "disposition": "MERGED_EQUIVALENT",
     "reason": "same meaning as the line",
     "covered_by": "S1-L2"
    },
    {
     "ovi": 6,
     "disposition": "NARRATED"
    },
    {
     "ovi": 7,
     "disposition": "NARRATED"
    },
    {
     "ovi": 8,
     "disposition": "NARRATED"
    },
    {
     "ovi": 9,
     "disposition": "NARRATED"
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



## CURRENT MODULE scripts/pipeline/stage1/coverage.py
```python
from __future__ import annotations

import jsonschema
from jsonschema import Draft202012Validator
from typing import Any

SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "stage1_coverage",
    "type": "object",
    "additionalProperties": False,
    "required": ["adhyay", "ovis"],
    "properties": {
        "adhyay": {"type": "integer", "minimum": 1, "maximum": 21},
        "ovis": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["ovi", "disposition"],
                "properties": {
                    "ovi": {"type": "integer", "minimum": 1},
                    "disposition": {
                        "type": "string",
                        "enum": ["VISUALISED", "NARRATED", "QUOTED", "MERGED_EQUIVALENT", "PROPOSE_OMISSION"]
                    },
                    "reason": {"type": "string", "minLength": 1, "maxLength": 400},
                    "covered_by": {
                        "oneOf": [
                            {"type": "string", "pattern": "^S[0-9]{1,2}-L[0-9]{1,3}$"},
                            {"type": "integer", "minimum": 1}
                        ]
                    }
                },
                "allOf": [
                    {
                        "if": {
                            "type": "object",
                            "required": ["disposition"],
                            "properties": {"disposition": {"const": "PROPOSE_OMISSION"}}
                        },
                        "then": {"type": "object", "required": ["reason"]}
                    },
                    {
                        "if": {
                            "type": "object",
                            "required": ["disposition"],
                            "properties": {"disposition": {"const": "MERGED_EQUIVALENT"}}
                        },
                        "then": {"type": "object", "required": ["reason", "covered_by"]}
                    }
                ]
            }
        }
    }
}

_validator = Draft202012Validator(SCHEMA)


def schema_errors(doc: Any) -> list[str]:
    errors = []
    for err in _validator.iter_errors(doc):
        path = "/".join(str(p) for p in err.path) if err.path else "doc"
        errors.append(f"coverage {path}: {err.message}")
    return errors


def validate(adhyay: int, doc: dict[str, Any], docs: dict[str, Any], ctx: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    notes: list[str] = []

    # Adhyay check
    doc_adhyay = doc.get("adhyay")
    if doc_adhyay != adhyay:
        errors.append(f"coverage adhyay {doc_adhyay} does not match {adhyay}")

    # Convert ctx lists/sets to sets
    script_line_ids = set(ctx.get("script_line_ids", []))
    chapter_ovis = set(ctx.get("chapter_ovis", []))
    unfilmed_ovis = set(ctx.get("unfilmed_ovis", []))

    # Track ovi dispositions
    ovi_dispositions: dict[int, list[str]] = {}
    ovis = doc.get("ovis", [])

    for ovi_entry in ovis:
        ovi = ovi_entry.get("ovi")
        disposition = ovi_entry.get("disposition")

        if ovi is None or disposition is None:
            continue

        if ovi not in ovi_dispositions:
            ovi_dispositions[ovi] = []
        ovi_dispositions[ovi].append(disposition)

        # PROPOSE_OMISSION note
        if disposition == "PROPOSE_OMISSION":
            notes.append(f"note: ovi {ovi} omission proposed, owner approval needed")

        # Unfilmed but VISUALISED
        if ovi in unfilmed_ovis and disposition == "VISUALISED":
            errors.append(f"ovi {ovi} is unfilmed but VISUALISED")

        # covered_by validation
        covered_by = ovi_entry.get("covered_by")
        if covered_by is not None:
            # Check if it's a script line id (S\d+-L\d+) or a chapter ovi (integer)
            is_line_id = isinstance(covered_by, str) and covered_by in script_line_ids
            is_chapter_ovi = isinstance(covered_by, int) and covered_by in chapter_ovis
            is_chapter_ovi_str = isinstance(covered_by, str) and covered_by.isdigit() and int(covered_by) in chapter_ovis

            if not (is_line_id or is_chapter_ovi or is_chapter_ovi_str):
                errors.append(f"ovi {ovi}: covered_by '{covered_by}' is not a script line id or chapter ovi")

    # Check every chapter ovi has exactly one disposition
    for ovi in chapter_ovis:
        dispositions = ovi_dispositions.get(ovi, [])
        if len(dispositions) == 0:
            errors.append(f"ovi {ovi} has no disposition")
        elif len(dispositions) > 1:
            errors.append(f"ovi {ovi} twice")

    return errors + notes

```

## CURRENT TESTS tests/test_stage1_coverage.py
```python
from __future__ import annotations
import copy
import importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "pipeline" / "stage1" / "coverage.py"
spec = importlib.util.spec_from_file_location("coverage", MODULE_PATH)
cov = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cov)

SCHEMA = cov.SCHEMA
schema_errors = cov.schema_errors
validate = cov.validate


def get_parent(doc, path):
    cur = doc
    for part in path[:-1]:
        cur = cur[part] if isinstance(part, str) else cur[part]
    return cur, path[-1]


def set_at(base, path, value):
    mutated = copy.deepcopy(base)
    parent, key = get_parent(mutated, path)
    parent[key] = value
    assert mutated != base, "mutation had no effect"
    return mutated


def delete_at(base, path):
    mutated = copy.deepcopy(base)
    parent, key = get_parent(mutated, path)
    del parent[key]
    assert mutated != base, "mutation had no effect"
    return mutated


def append_at(base, path, value):
    mutated = copy.deepcopy(base)
    parent, key = get_parent(mutated, path)
    parent[key].append(value)
    assert mutated != base, "mutation had no effect"
    return mutated


def base_docs_ctx():
    docs = {
        "coverage": {
            "adhyay": 1,
            "ovis": [
                {"ovi": 1, "disposition": "VISUALISED"},
                {"ovi": 2, "disposition": "VISUALISED"},
                {"ovi": 3, "disposition": "NARRATED"},
                {"ovi": 4, "disposition": "QUOTED"},
                {
                    "ovi": 5,
                    "disposition": "MERGED_EQUIVALENT",
                    "reason": "same meaning as the line",
                    "covered_by": "S1-L2",
                },
                {"ovi": 6, "disposition": "NARRATED"},
                {"ovi": 7, "disposition": "NARRATED"},
                {"ovi": 8, "disposition": "NARRATED"},
                {"ovi": 9, "disposition": "NARRATED"},
            ],
        },
        "story_map": {},
        "scenes": {},
        "shots": {},
        "briefs": {},
        "looks": {},
        "voices": {},
        "sounds": {},
        "questions": {},
    }
    ctx = {
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
    return copy.deepcopy(docs), copy.deepcopy(ctx)


# ---------- schema_errors tests ----------
@pytest.mark.parametrize(
    "mutator,expect_field",
    [
        (lambda d: d, None),  # valid
        (lambda d: delete_at(d, ["adhyay"]), "adhyay"),
        (lambda d: delete_at(d, ["ovis"]), "ovis"),
        (lambda d: set_at(d, ["adhyay"], 0), "adhyay"),
        (lambda d: set_at(d, ["adhyay"], 22), "adhyay"),
        (lambda d: set_at(d, ["adhyay"], "1"), "adhyay"),
        (lambda d: set_at(d, ["ovis"], {}), "ovis"),
        (lambda d: delete_at(d, ["ovis", 0, "ovi"]), "ovi"),
        (lambda d: delete_at(d, ["ovis", 0, "disposition"]), "disposition"),
        (lambda d: set_at(d, ["ovis", 0, "disposition"], "INVALID"), "disposition"),
        (lambda d: set_at(d, ["ovis", 0, "ovi"], 0), "ovi"),
        (lambda d: set_at(d, ["ovis", 0, "ovi"], -1), "ovi"),
        (lambda d: set_at(d, ["ovis", 0, "ovi"], "1"), "ovi"),
        # reason required for PROPOSE_OMISSION (ovi 1 has no reason in base)
        (lambda d: set_at(d, ["ovis", 0, "disposition"], "PROPOSE_OMISSION"), "reason"),
        # reason required for MERGED_EQUIVALENT (ovi 5)
        (lambda d: delete_at(d, ["ovis", 4, "reason"]), "reason"),
        # covered_by required for MERGED_EQUIVALENT (ovi 5)
        (lambda d: delete_at(d, ["ovis", 4, "covered_by"]), "covered_by"),
        # covered_by invalid format (not line_id pattern, not integer)
        (lambda d: set_at(d, ["ovis", 4, "covered_by"], "bad-id"), "covered_by"),
        # extra keys
        (lambda d: set_at(d, ["ovis", 0, "extra"], "x"), "extra"),
        (lambda d: set_at(d, ["extra_root"], "x"), "extra_root"),
    ],
)
def test_schema_errors(mutator, expect_field):
    docs, _ = base_docs_ctx()
    doc = mutator(docs["coverage"])
    errs = schema_errors(doc)
    if expect_field is None:
        assert errs == []
    else:
        assert any(expect_field in e for e in errs), f"expected field {expect_field} in {errs}"


# ---------- validate tests ----------
@pytest.mark.parametrize(
    "adhyay,mutator,expect_keywords",
    [
        # valid baseline
        (1, lambda d, c: (d, c), []),
        # adhyay mismatch
        (2, lambda d, c: (d, c), ["coverage adhyay 1 does not match 2"]),
        # missing ovi disposition (remove entire ovi entry for ovi 1)
        (1, lambda d, c: (delete_at(d, ["ovis", 0]), c), ["ovi 1 has no disposition"]),
        # duplicate ovi disposition (append second ovi=1)
        (1, lambda d, c: (append_at(d, ["ovis"], {"ovi": 1, "disposition": "VISUALISED"}), c), ["ovi 1 twice"]),
        # PROPOSE_OMISSION -> note (exactly one note, after errors)
        (1, lambda d, c: (set_at(set_at(d, ["ovis", 0, "disposition"], "PROPOSE_OMISSION"), ["ovis", 0, "reason"], "omit"), c), ["note: ovi 1 omission proposed, owner approval needed"]),
        # unfilmed but VISUALISED
        (1, lambda d, c: (d, set_at(c, ["unfilmed_ovis"], [1])), ["ovi 1 is unfilmed but VISUALISED"]),
        # covered_by invalid line_id
        (1, lambda d, c: (set_at(d, ["ovis", 4, "covered_by"], "S9-L99"), c), ["S9-L99"]),
        # covered_by invalid ovi (integer)
        (1, lambda d, c: (set_at(d, ["ovis", 4, "covered_by"], 99), c), ["99"]),
        # covered_by valid line_id (no error)
        (1, lambda d, c: (set_at(d, ["ovis", 4, "covered_by"], "S1-L1"), c), []),
        # covered_by valid ovi (integer, no error)
        (1, lambda d, c: (set_at(d, ["ovis", 4, "covered_by"], 3), c), []),
        # empty chapter_ovis (zero-story chapter)
        (1, lambda d, c: (d, set_at(c, ["chapter_ovis"], [])), []),
        # unfilmed_ovis with non-VISUALISED ovi (no error)
        (1, lambda d, c: (d, set_at(c, ["unfilmed_ovis"], [3])), []),
        # ctx values as sets (should work)
        (1, lambda d, c: (d, set_at(set_at(c, ["script_line_ids"], {"S1-L1", "S1-L2"}), ["chapter_ovis"], {1, 2, 3})), []),
    ],
)
def test_validate(adhyay, mutator, expect_keywords):
    docs, ctx = base_docs_ctx()
    doc, ctx = mutator(docs["coverage"], ctx)
    errs = validate(adhyay, doc, docs, ctx)
    # notes come after errors; check all expected keywords appear
    for kw in expect_keywords:
        assert any(kw in e for e in errs), f"expected '{kw}' in {errs}"
    if not expect_keywords:
        assert errs == []


# ---------- extra: ensure base is valid ----------
def test_base_valid():
    docs, ctx = base_docs_ctx()
    assert schema_errors(docs["coverage"]) == []
    assert validate(1, docs["coverage"], docs, ctx) == []


# ---------- note ordering and count ----------
def test_propose_omission_note_comes_after_errors():
    docs, ctx = base_docs_ctx()
    # Create a doc with both an error and a PROPOSE_OMISSION
    doc = copy.deepcopy(docs["coverage"])
    # Add an error: unfilmed but VISUALISED
    ctx = set_at(ctx, ["unfilmed_ovis"], [1])
    # Add a PROPOSE_OMISSION on ovi 2
    doc = set_at(doc, ["ovis", 1, "disposition"], "PROPOSE_OMISSION")
    doc = set_at(doc, ["ovis", 1, "reason"], "omit")
    errs = validate(1, doc, docs, ctx)
    # Should have error first, then note
    assert len(errs) == 2
    assert "ovi 1 is unfilmed but VISUALISED" in errs[0]
    assert errs[1].startswith("note: ")
    assert "ovi 2 omission proposed" in errs[1]


def test_propose_omission_exactly_one_note_per_entry():
    docs, ctx = base_docs_ctx()
    doc = copy.deepcopy(docs["coverage"])
    # Add two PROPOSE_OMISSION entries for same ovi (should produce two notes)
    doc = set_at(doc, ["ovis", 0, "disposition"], "PROPOSE_OMISSION")
    doc = set_at(doc, ["ovis", 0, "reason"], "omit1")
    doc = append_at(doc, ["ovis"], {"ovi": 1, "disposition": "PROPOSE_OMISSION", "reason": "omit2"})
    errs = validate(1, doc, docs, ctx)
    notes = [e for e in errs if e.startswith("note: ")]
    assert len(notes) == 2
    assert all("omission proposed" in n for n in notes)

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
