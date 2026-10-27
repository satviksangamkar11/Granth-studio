# FIX CALL for the test file `tests/test_stage1_coverage.py` (write ONLY that file, one FILE block). Two independent reviewers (Codex, Haiku) found real defects in your previous version (shown below). Repair ALL of them. The unit spec, BASE data and clarifications follow. HARD RULES that the previous attempts broke:
1. Write ONE robust helper set at the top and use it everywhere: `get_parent(doc, path)` that walks a path list where an int part indexes a list and a str part indexes a dict; `set_at(base, path, value)`, `delete_at(base, path)`, `append_at(base, path, value)` (all work on a deep copy and handle list indexes and dict keys, never index a list with a string). EVERY mutation must be proven to change the document: the helper asserts `mutated != base` (a no-op mutation fails loudly). Never address a list element that does not exist in BASE (append instead).
2. Each row changes exactly ONE thing and leaves everything else valid; contexts (script lines, saved voices, presets) stay complete unless the row is about that context. Each row asserts the item id AND only the keyword the spec QUOTES; for rules with no quoted phrase assert only the item id (never invented words like unique, outside, prefix, shared, empty, mismatch, not exist).
3. Positive rows assert `[]` exactly. A "twice/duplicate" rule needs a real duplicate (append a second entry). A rule that is schema-level in the spec is tested through `schema_errors`; a rule the spec makes semantic is tested ONLY through `validate` (never expect jsonschema to reject reversed ranges or empty names unless the spec's schema says so). jsonschema reports required/additionalProperties errors at the PARENT path: assert the offending field name appears in the message, never a child path.
4. Required-field rows DELETE each required field from a deep copy (root fields and nested objects); extra-key rows ADD one unknown key to an otherwise valid object at the root and at every nested object; every enum has one invalid-value row.
5. `validate(adhyay, doc, docs, ctx)`: `docs` is the dict of ALL nine documents (use only the ones the unit spec lists; pass {} for absent ones) and `ctx` is separate (never `docs["ctx"]`).
6. ids are strings and ovis are integers (covered_by uses an integer ovi or a line id string).
7. Keep it compact (<= 170 lines), synthetic only, loading the module by path with importlib as the unit spec says.
Reply with exactly one FILE block: FILE: tests/test_stage1_coverage.py

## CODEX FINDINGS FOR THIS UNIT
- **coverage — High:** `test_validate` **146,148** supplies two values for three parameter names, preventing collection. `test_schema_errors` **112** deletes absent `reason`, raising `KeyError`; **114** reapplies the unchanged valid MERGED_EQUIVALENT disposition while expecting an error. **Medium:** the purported duplicate mutation **148** merely reapplies VISUALISED; it creates no duplicate. `test_validate` **178,185** uses strings `"99"`/`"3"` instead of integer ovis. **153–156,209–211** checks note text membership but neither exactly one note nor error-before-note ordering. **172,180** prescribes unquoted diagnostic wording.

## HAIKU FINDINGS FOR THIS UNIT
(2) Line 148 ("ovis/0/disposition", "VISUALISED", "ovi 1 twice") is a no-op on the valid base, so the "twice" rule has no working test. Fix: append a second entry for ovi 1. (4) Line 172 asserts "line is not in the script" and line 181 asserts "ovi not in chapter"; neither is quoted in the spec. (2) Lines 178 and 185 pass covered_by as strings ("99", "3"), but the spec types an ovi as an integer. Use integers, or clarify the spec.

## UNIT SPEC (binding)
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



## YOUR PREVIOUS tests/test_stage1_coverage.py (repair it)
```python
from __future__ import annotations
import copy
import importlib.util
import json
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


def base() -> tuple[dict, dict]:
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


def mutate(obj: dict, path: str, value):
    """Set or delete a single key in a nested dict/list. path like 'a/b/0/c'."""
    parts = path.split("/")
    cur = obj
    for p in parts[:-1]:
        if p.isdigit():
            cur = cur[int(p)]
        else:
            cur = cur[p]
    last = parts[-1]
    if value is None:
        if last.isdigit():
            del cur[int(last)]
        else:
            del cur[last]
    else:
        if last.isdigit():
            cur[int(last)] = value
        else:
            cur[last] = value


# ---------- schema_errors tests ----------
@pytest.mark.parametrize(
    "path,value,expect_field",
    [
        # valid
        (None, None, None),
        # missing required root fields
        ("adhyay", None, "adhyay"),
        ("ovis", None, "ovis"),
        # adhyay type/range
        ("adhyay", 0, "adhyay"),
        ("adhyay", 22, "adhyay"),
        ("adhyay", "1", "adhyay"),
        # ovis not array
        ("ovis", {}, "ovis"),
        # ovi entry missing ovi
        ("ovis/0/ovi", None, "ovi"),
        # ovi entry missing disposition
        ("ovis/0/disposition", None, "disposition"),
        # invalid disposition enum
        ("ovis/0/disposition", "INVALID", "disposition"),
        # ovi type/range
        ("ovis/0/ovi", 0, "ovi"),
        ("ovis/0/ovi", -1, "ovi"),
        ("ovis/0/ovi", "1", "ovi"),
        # reason required for PROPOSE_OMISSION
        ("ovis/0/disposition", "PROPOSE_OMISSION", "reason"),
        ("ovis/0/reason", None, "reason"),
        # reason required for MERGED_EQUIVALENT
        ("ovis/4/disposition", "MERGED_EQUIVALENT", "reason"),
        ("ovis/4/reason", None, "reason"),
        # covered_by required for MERGED_EQUIVALENT
        ("ovis/4/covered_by", None, "covered_by"),
        # covered_by invalid format (not line_id or ovi)
        ("ovis/4/covered_by", "bad-id", "covered_by"),
        # extra keys
        ("ovis/0/extra", "x", "extra"),
        ("extra_root", "x", "extra_root"),
    ],
)
def test_schema_errors(path, value, expect_field):
    docs, _ = base()
    doc = docs["coverage"]
    if path is not None:
        mutate(doc, path, value)
    errs = schema_errors(doc)
    if expect_field is None:
        assert errs == []
    else:
        assert any(expect_field in e for e in errs), f"expected field {expect_field} in {errs}"


# ---------- validate tests ----------
@pytest.mark.parametrize(
    "adhyay,mutations,expect_keywords",
    [
        # valid baseline
        (1, [], []),
        # adhyay mismatch
        (2, [], ["coverage adhyay 1 does not match 2"]),
        # missing ovi disposition
        (1, [("ovis/0", None, "ovi 1 has no disposition")]),
        # duplicate ovi disposition
        (1, [("ovis/0/disposition", "VISUALISED", "ovi 1 twice")]),
        # PROPOSE_OMISSION -> note
        (
            1,
            [
                ("ovis/0/disposition", "PROPOSE_OMISSION", None),
                ("ovis/0/reason", "omit reason", None),
            ],
            ["note: ovi 1 omission proposed, owner approval needed"],
        ),
        # unfilmed but VISUALISED
        (
            1,
            [
                ("ctx/unfilmed_ovis", [1], None),
            ],
            ["ovi 1 is unfilmed but VISUALISED"],
        ),
        # covered_by invalid line_id
        (
            1,
            [
                ("ovis/4/covered_by", "S9-L99", None),
            ],
            ["S9-L99: line is not in the script"],
        ),
        # covered_by invalid ovi
        (
            1,
            [
                ("ovis/4/covered_by", "99", None),
            ],
            ["99: ovi not in chapter"],
        ),
        # covered_by valid line_id (no error)
        (1, [("ovis/4/covered_by", "S1-L1", None)], []),
        # covered_by valid ovi (no error)
        (1, [("ovis/4/covered_by", "3", None)], []),
        # empty chapter_ovis (zero-story chapter)
        (1, [("ctx/chapter_ovis", [], None)], []),
        # empty unfilmed_ovis
        (1, [("ctx/unfilmed_ovis", [], None)], []),
        # ctx values as sets (should work)
        (
            1,
            [
                ("ctx/script_line_ids", {"S1-L1", "S1-L2"}, None),
                ("ctx/chapter_ovis", {1, 2, 3}, None),
            ],
            [],
        ),
    ],
)
def test_validate(adhyay, mutations, expect_keywords):
    docs, ctx = base()
    for path, value, _ in mutations:
        if path.startswith("ctx/"):
            mutate(ctx, path[4:], value)
        else:
            mutate(docs["coverage"], path, value)
    errs = validate(adhyay, docs["coverage"], docs, ctx)
    # notes come after errors; check all expected keywords appear in order
    for kw in expect_keywords:
        assert any(kw in e for e in errs), f"expected '{kw}' in {errs}"
    if not expect_keywords:
        assert errs == []


# ---------- extra: ensure base is valid ----------
def test_base_valid():
    docs, ctx = base()
    assert schema_errors(docs["coverage"]) == []
    assert validate(1, docs["coverage"], docs, ctx) == []

```
