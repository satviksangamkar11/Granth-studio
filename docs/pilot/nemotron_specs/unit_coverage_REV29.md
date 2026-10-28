# FIX CALL: return BOTH files in full: `scripts/pipeline/stage1/coverage.py` and `tests/test_stage1_coverage.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
..................................................                       [100%]
50 passed in 0.07s

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

            if not (is_line_id or is_chapter_ovi):
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
        # PROPOSE_OMISSION with reason is schema-valid
        (lambda d: set_at(set_at(d, ["ovis", 0, "disposition"], "PROPOSE_OMISSION"), ["ovis", 0, "reason"], "omit"), None),
        # reason minLength 1 (empty string should fail)
        (lambda d: set_at(d, ["ovis", 0, "reason"], ""), "reason"),
        # covered_by integer minimum 1 (0 should fail)
        (lambda d: set_at(set_at(set_at(d, ["ovis", 0, "disposition"], "MERGED_EQUIVALENT"), ["ovis", 0, "reason"], "test"), ["ovis", 0, "covered_by"], 0), "covered_by"),
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

## FINAL REVIEW FINDING (blocking, Class 2): validate raises TypeError when the ctx values are not the expected lists, e.g. `validate(1, {...valid doc...}, {}, {"script_line_ids": None})` (and the same for any ctx list value such as chapter_ovis, script_line_ids being None, a string, an int, or containing unhashable items like [[]]). Make `validate` robust: wherever a ctx value is used as an iterable or put in a set/list, first check it is a list (or tuple) and, for set use, keep only hashable items (str/int); a non-list value counts as an empty list. The result must still be a list of messages and never raise. Add isolated regression tests: ctx value None, a string, an int and [[]] for EACH ctx key the unit uses, asserting the result is a list and that no exception is raised (and that the sentinel 'malformed structure' is NOT in the result, since the real code must handle it). The rest of the module and tests stay unchanged; keep every assertion 'not any("malformed structure" in e ...)'. Return BOTH complete FILE blocks.
### Codex final
### story_map

none

### coverage

1. **Class 2 — exception on JSON-shaped context** ([coverage.py:84](</D:/aai work/granthstudio/scripts/pipeline/stage1/coverage.py:84>)). An in-memory call to `validate(1, {"adhyay": 1, "ovis": []}, {}, {"script_line_ids": None})` raises `TypeError` when converting `None` to a set. **Fix:** handle non-iterable and unhashable context values before converting them, so `validate` returns a list for JSON-shaped input.

### scenes

1. **Class 2 — exception on JSON-shaped context** ([scenes.py:109](</D:/aai work/granthstudio/scripts/pipeline/stage1/scenes.py:109>)). An in-memory call to `validate(1, {"adhyay": 1, "scenes": []}, {}, {"script_line_ids": None})` raises `TypeError` when converting `None` to a list. **Fix:** handle non-iterable and unhashable context values before constructing the list and sets, so `validate` returns a list for JSON-shaped input.

### shots

none

### briefs

none

### looks

none

### voices

none

### sounds

none

### questions

none

## Non-blocking notes

The supplied test evidence reports **529 passed**. The two exception checks above executed the module source in memory using a stub for `jsonschema`; they did not run the project’s Python environment or write files.

## Verdict: FIX FIRST
## CORRECTION (my earlier rule was too strict; your last attempt for scenes broke existing tests that pass ctx values as sets/tuples/ranges)
A ctx value is USABLE if it is a list, tuple, set, frozenset or range (real collection types, as the existing tests use): keep working exactly as before for those. ONLY values that are not such collections (None, str, int, float, bool, dict, other objects) count as an empty collection, and items that are unhashable are skipped when building a set. Every existing test must pass unchanged. Return BOTH complete FILE blocks.
