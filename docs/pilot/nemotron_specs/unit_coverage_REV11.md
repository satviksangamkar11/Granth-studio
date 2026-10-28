# FIX CALL: return BOTH files in full: `scripts/pipeline/stage1/coverage.py` and `tests/test_stage1_coverage.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
...............................................                          [100%]
47 passed in 0.06s

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

    # Guard: doc must be a dict
    if not isinstance(doc, dict):
        errors.append("coverage doc: must be an object")
        return errors + notes

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

    # Guard: ovis must be a list
    if not isinstance(ovis, list):
        ovis = []

    for ovi_entry in ovis:
        # Guard: each entry must be a dict
        if not isinstance(ovi_entry, dict):
            continue

        ovi = ovi_entry.get("ovi")
        disposition = ovi_entry.get("disposition")

        # Guard: ovi must be an int
        if not isinstance(ovi, int):
            continue

        if disposition is None:
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


# ---------- regression: validate never raises on odd data ----------
@pytest.mark.parametrize(
    "doc,ctx",
    [
        # doc not a dict
        (None, {}),
        ("not a dict", {}),
        (123, {}),
        ([], {}),
        # ovis not a list
        ({"adhyay": 1, "ovis": "not a list"}, {}),
        ({"adhyay": 1, "ovis": 123}, {}),
        ({"adhyay": 1, "ovis": None}, {}),
        # ovis entries not dicts
        ({"adhyay": 1, "ovis": ["not a dict", 123, None]}, {}),
        # ovi not an int (unhashable)
        ({"adhyay": 1, "ovis": [{"ovi": [1, 2], "disposition": "VISUALISED"}]}, {}),
        # ovi not an int (string)
        ({"adhyay": 1, "ovis": [{"ovi": "1", "disposition": "VISUALISED"}]}, {}),
        # ovi not an int (float)
        ({"adhyay": 1, "ovis": [{"ovi": 1.5, "disposition": "VISUALISED"}]}, {}),
        # disposition not a string
        ({"adhyay": 1, "ovis": [{"ovi": 1, "disposition": 123}]}, {}),
    ],
)
def test_validate_odd_data_no_raise(doc, ctx):
    """validate must never raise; it should return a list of errors (possibly empty)."""
    docs = {"coverage": {}, "story_map": {}, "scenes": {}, "shots": {}, "briefs": {}, "looks": {}, "voices": {}, "sounds": {}, "questions": {}}
    errs = validate(1, doc, docs, ctx)
    assert isinstance(errs, list)

```

## ROUND 3 REVIEW FINDINGS (apply what the SPEC supports; Codex items are verified, Haiku items unverified). Keep the catch-all guard in validate. For test findings: make the row ISOLATED (only the rule under test is violated, so the test fails if that rule's check is removed) and assert the offending id/field, never wording the spec does not quote. For coverage: do not convert numeric strings with isdigit/int; accept only real integers and report anything else as an error, never raise. All existing tests must still pass. Return BOTH FILE blocks complete.
### Codex round 3
## Verdict: FIX FIRST

### story_map

none.

### coverage

1. **High —** [coverage.py:129](</D:/aai work/granthstudio/scripts/pipeline/stage1/coverage.py:129>): `covered_by: "²"` makes `validate` raise `ValueError`: `isdigit()` accepts it, but `int()` does not. Remove the numeric-string conversion; the schema permits chapter ovis as integers. I reproduced this with a `jsonschema` stub.

### scenes

1. **Low —** [test_stage1_scenes.py:177](</D:/aai work/granthstudio/tests/test_stage1_scenes.py:177>): The duplicate-scene test also creates overlapping ranges and duplicate lines. Its `"S1"` assertion can pass without duplicate-scene detection. Append an S1 scene with a non-overlapping range and no lines.
2. **Low —** [test_stage1_scenes.py:239](</D:/aai work/granthstudio/tests/test_stage1_scenes.py:239>): `"S1"` also matches the unknown-line error for `S9-L9`, so the assertion does not verify ordering. Check for a separate error associated with S1, distinct from the unknown-line error.

### shots

1. **Low —** [test_stage1_shots.py:170](</D:/aai work/granthstudio/tests/test_stage1_shots.py:170>): The invalid `need_new.class` row fails because the existing preset requires `need_new` to be null. Set the preset to `NEED_NEW` for this row and assert the class error.
2. **Low —** [test_stage1_shots.py:268](</D:/aai work/granthstudio/tests/test_stage1_shots.py:268>): `"S2"` matches the uncovered `S2-L1` error even if the missing-shots check is removed. Isolate the missing-shots rule, for example by giving S2 no lines.
3. **Low —** [test_stage1_shots.py:371](</D:/aai work/granthstudio/tests/test_stage1_shots.py:371>): The test asserts `"not in scene"`, which the spec does not quote. Assert the shot ID in a separate error from the quoted uncovered-line message.

### briefs

1. **Low —** [test_stage1_briefs.py:412](</D:/aai work/granthstudio/tests/test_stage1_briefs.py:412>): The test asserts `"scene exists"`, which the spec does not quote. Assert the image ID in the isolated missing-scene case.

### looks

none.

### voices

none.

### sounds

1. **Low —** [test_stage1_sounds.py:229](</D:/aai work/granthstudio/tests/test_stage1_sounds.py:229>): The test asserts `"document must be an object"`, which the spec does not quote. Assert the document identifier instead.

### questions

none.

The workspace is read-only, so I could not write the requested report file. I could not independently run the suite because the available Python lacks `jsonschema`, and I did not reproduce every Round 2 case; the verdict reflects the verified findings above, not a complete revalidation of all earlier findings.### Haiku round 3
# Stage 1 unit modules: Round 3 review (read-only)

Scope: `scripts/pipeline/stage1/{story_map,coverage,scenes,shots,briefs,looks,voices,sounds,questions}.py`, `tests/test_stage1_<unit>.py`, against `docs/pilot/nemotron_specs/unit_<unit>.md`, `stage1_base.json`, `STAGE1_RULES.md`.

Evidence: `uv run pytest -q --tb=short tests/test_stage1_*.py` gives **418 passed**. Every defect below was checked by calling the module in memory with a small input (no project file written, no network). Fuzzing: every leaf of every document and every ctx key was replaced with 13 odd values (None, int, str, list, dict, bool, nested lists), and each validate/schema_errors call was made with empty and None docs/ctx. The only raises were from `coverage.validate` when a ctx list (`script_line_ids`, `chapter_ovis`, `unfilmed_ovis`) was None or an int. That is ctx, not document data, so it is not counted. No print, env, key or secret handling was found in any module or test.

## Verdict: FIX FIRST

---

## Round 2 findings: status

| Unit | Round 2 finding | Status |
|---|---|---|
| story_map | 1 `ovi_types` not type-checked | FIXED (story_map.py:84-85) |
| story_map | 2 `events` not type-checked | FIXED (story_map.py:108-110) |
| story_map | 3 `key_ovis` not type-checked | FIXED (story_map.py:117-118) |
| story_map | 4 test asserts "not an object" | FIXED (test row now asserts "doc") |
| scenes | 1 test asserts "duplicate scene id" | FIXED (test asserts "S1") |
| scenes | 2 test asserts "order" | FIXED (test asserts "S1") |
| shots | 1 `ovi_ids: 5` raises | FIXED (shots.py:169-170) |
| shots | 2 `beat_line_ids: None` raises | FIXED (shots.py:181-182) |
| shots | 3 scene `line_ids: 5` raises | FIXED (shots.py:177) |
| shots | 4 class-enum row uses preset `01_establishing_shot` | STILL OPEN (defect S-2) |
| shots | 5 test asserts "scene has no shots" | FIXED (test asserts "S2") |
| briefs | 1 `scene_id: ["S1"]` raises | FIXED (briefs.py:121-126, verified) |
| briefs | 2 `references.characters: [""]` accepted | FIXED (briefs.py:78-81, schema error verified) |
| voices | 1 `validate(1, 1, ...)` / `None` raises | FIXED (voices.py:153-154, verified) |
| voices | 2 duplicate entries of one character reported twice | FIXED (voices.py:136-138 uses sets, verified) |
| sounds | 1 test asserts non-quoted wording | PARTLY FIXED (cue[0] now used; line 229 still open, defect O-1) |
| coverage, looks, questions | none | n/a |

---

## story_map

none.

## coverage

none.

## scenes

1. `tests/test_stage1_scenes.py:217-231` (class 3): nine `assert isinstance(M.validate(...), list)` checks. `scenes.validate` wraps `_validate_semantic` in a catch-all that returns `["scenes: malformed structure"]`, so `validate` can never raise and these asserts can never fail. Fix: for each call, assert `not any("malformed structure" in e for e in errs)`, as `test_stage1_sounds.py:290` already does.

## shots

1. `tests/test_stage1_shots.py:305-360` (class 3): twelve `assert isinstance(errs, list)` checks inside `test_validate_odd_data_no_raise`. `shots.validate` has a catch-all, so these can never fail. Fix: replace each with `assert not any("malformed structure" in e for e in errs)`.
2. `tests/test_stage1_shots.py:170` (class 3, Round 2 item 4 still open, verified): the row `(["shots", 0, "need_new"], {"reason": "x", "class": "bad_class"})` sits in a table where `preset` is `01_establishing_shot`. `schema_errors` returns only `shots shots/0/need_new: ... is not of type 'null'` (the else branch), so the class enum is never exercised. With preset `NEED_NEW` the same value gives `shots shots/0/need_new/class: 'bad_class' is not one of [...]`. Fix: move this row to a separate test with `preset` set to `"NEED_NEW"` and assert `"class"` in the message.

## briefs

1. `tests/test_stage1_briefs.py:339, 348, 357, 363, 369, 380` (class 3): six `assert isinstance(errs, list)` checks. `briefs.validate` has a catch-all, so these can never fail. Fix: assert `not any("malformed structure" in e for e in errs)`.
2. `tests/test_stage1_briefs.py:412` (class 4): asserts `"scene exists"`. The spec gives "scene exists" only as rule prose, not as a quoted message. Fix: `assert any("s99_test" in e for e in errs)`.

## looks

none.

## voices

1. `scripts/pipeline/stage1/voices.py:111-115` (class 1): the spec says "a character already RECURRING must not be listed twice". The code counts only RECURRING entries, so a character with one RECURRING entry and one NEW_PROPOSED entry is not flagged when not speaking. Verified: `validate` with `gajanan_maharaj` listed as RECURRING and again as NEW_PROPOSED, and `speaking_characters` set to `["narrator"]`, returns `[]`. Fix: `for char, entries in char_entries.items(): if len(entries) > 1 and any(e.get("status") == "RECURRING" for e in entries): messages.append(f"{char}: recurring character listed twice")`. Add a test row for this case. (The rule is worded in plain prose, so if the owner reads it as "two RECURRING entries only", close this as none.)

## sounds

1. `tests/test_stage1_sounds.py:229` (class 4, Round 2 item 1 partly open, verified): asserts `"document must be an object"`, which the spec does not quote. Fix: `assert isinstance(errs, list) and any("sounds" in e for e in errs)`, or assert the item id only.
2. `tests/test_stage1_sounds.py:235, 264, 269, 274, 281, 288, 297` (class 3): seven `assert isinstance(errs, list)` checks after calls to `validate`, which has a catch-all. These can never fail. Fix: assert `not any("malformed structure" in e for e in errs)`.

## questions

none.

---

## Defects per unit (Round 3)

| Unit | Defects |
|---|---|
| story_map | 0 |
| coverage | 0 |
| scenes | 1 |
| shots | 2 |
| briefs | 2 |
| looks | 0 |
| voices | 1 |
| sounds | 2 |
| questions | 0 |
| **Total** | **8** |

Notes:
- Class 2 (raise) is clean for document data. Every raise found in Round 2 is fixed. The catch-all in six modules hides any future raise, which is why the isinstance-only tests in scenes, shots, briefs and sounds cannot fail. Fixing those tests (items above) is the way to make the no-raise checks real.
- The pytest count is now 418 (Round 2 printed 400).
