# FIX CALL for the test file `tests/test_stage1_shots.py` (write ONLY that file, one FILE block). Two independent reviewers (Codex, Haiku) found real defects in your previous version (shown below). Repair ALL of them. The unit spec, BASE data and clarifications follow. HARD RULES that the previous attempts broke:
1. Write ONE robust helper set at the top and use it everywhere: `get_parent(doc, path)` that walks a path list where an int part indexes a list and a str part indexes a dict; `set_at(base, path, value)`, `delete_at(base, path)`, `append_at(base, path, value)` (all work on a deep copy and handle list indexes and dict keys, never index a list with a string). EVERY mutation must be proven to change the document: the helper asserts `mutated != base` (a no-op mutation fails loudly). Never address a list element that does not exist in BASE (append instead).
2. Each row changes exactly ONE thing and leaves everything else valid; contexts (script lines, saved voices, presets) stay complete unless the row is about that context. Each row asserts the item id AND only the keyword the spec QUOTES; for rules with no quoted phrase assert only the item id (never invented words like unique, outside, prefix, shared, empty, mismatch, not exist).
3. Positive rows assert `[]` exactly. A "twice/duplicate" rule needs a real duplicate (append a second entry). A rule that is schema-level in the spec is tested through `schema_errors`; a rule the spec makes semantic is tested ONLY through `validate` (never expect jsonschema to reject reversed ranges or empty names unless the spec's schema says so). jsonschema reports required/additionalProperties errors at the PARENT path: assert the offending field name appears in the message, never a child path.
4. Required-field rows DELETE each required field from a deep copy (root fields and nested objects); extra-key rows ADD one unknown key to an otherwise valid object at the root and at every nested object; every enum has one invalid-value row.
5. `validate(adhyay, doc, docs, ctx)`: `docs` is the dict of ALL nine documents (use only the ones the unit spec lists; pass {} for absent ones) and `ctx` is separate (never `docs["ctx"]`).
6. ids are strings and ovis are integers (covered_by uses an integer ovi or a line id string).
7. Keep it compact (<= 170 lines), synthetic only, loading the module by path with importlib as the unit spec says.
Reply with exactly one FILE block: FILE: tests/test_stage1_shots.py

## CODEX FINDINGS FOR THIS UNIT
- **shots — Medium:** `test_adhyay_mismatch` **203** reverses the expected values: the required message is `shots adhyay 2 does not match 1`. `test_shot_id_unique_consecutive` **206** leaves S1-1 unchanged; no duplicate exists. Its assertion **213** also mandates unquoted wording. Required-field and extra-key assertions **125,135,169** demand child paths, whereas jsonschema reports those errors at the containing object. `test_empty_context_missing_refs` **270** requires script-membership validation absent from this unit’s rules. Missing nested `need_new` deletion rows for `reason/class` and an extra-key row leave that object incompletely tested. Field row **148** uses an object under a normal preset, so the required-null violation masks invalid-class coverage there.

## HAIKU FINDINGS FOR THIS UNIT
(2) Line 206 ("S1-1" on shot 0) changes nothing, so the duplicate-shot_id rule never fails. (1) Lines 125, 135 and 169 expect "shots shots/0/<field>" or "shots adhyay" in messages. jsonschema reports required and additionalProperties errors at the parent path ("shots doc" or "shots shots/0"), so these assertions fail on a correct implementation. (4) Line 213 asserts "unique"/"consecutive", line 219 "scene", line 231 "beat_line", line 270 "not in the script"; none are quoted, and line 270 is not a shots rule. (5) No root extra-key row and no need_new nested extra-key row.

## UNIT SPEC (binding)
# UNIT SPEC: Stage 1 document `shots` (schema `stage1_shots`)
This is ONE unit of the Stage 1 contract (the master spec `stage1_v2.md` was split because one big spec gave unreliable tests). Keep the unit small and exact.
Module: `scripts/pipeline/stage1/shots.py`. Tests: `tests/test_stage1_shots.py`. Style: `from __future__ import annotations`, standard library plus `jsonschema`; no print, no network, nothing at import time; tests use only the BASE data below and `tmp_path`; the test file loads the module by path with importlib (`ROOT = Path(__file__).resolve().parents[1]`, `ROOT / "scripts" / "pipeline" / "stage1" / "shots.py"`).

## Module API (exactly this)
- `SCHEMA`: dict, JSON Schema draft 2020-12 for the document, `additionalProperties: false` on EVERY object (nested too), `$schema` = "https://json-schema.org/draft/2020-12/schema", `title` = "stage1_shots".
- `schema_errors(doc) -> list[str]`: one message per jsonschema error, formatted "shots <path>: <message>" (path joined by "/", "doc" when empty).
- `validate(adhyay, doc, docs, ctx) -> list[str]`: SEMANTIC checks only (the schema has already passed; it must still never raise on odd data). `docs` is a dict of ALL nine documents (key names: story_map, coverage, scenes, shots, briefs, looks, voices, sounds, questions; a missing one counts as empty), `ctx` the context dict (keys: script_line_ids list, core_line_ids set, chapter_ovis set, unfilmed_ovis set, preset_ids set, sound_ids set, saved_voices dict voice_key->voice_id, speaking_characters set, known_states dict entity_id->set of state ids). Lists in ctx may arrive as lists or sets: convert with set(). Notes (messages that start with "note: ") come AFTER error messages. Include the adhyay check first: "shots adhyay <n> does not match <adhyay>".

## Ids and common types
scene_id `^S[0-9]{1,2}$`; shot_id `^S[0-9]{1,2}-[0-9]{1,2}$`; line_id `^S[0-9]{1,2}-L[0-9]{1,3}$`; image id (Stage 1 brief) `^s[0-9]{1,2}_[a-z][a-z0-9_]{0,40}$`; ovi = integer >= 1; adhyay = integer 1..21; text = string 1..400 chars; preset id = string matching `^[0-9]{2}_[a-z0-9_]+$`; sound id `^(bed|fx)_[a-z0-9_]+$`.

## The document shape (from the master spec)
4. `stage1_shots`: `shots`: array of {shot_id, scene_id, ovi_ids [ovi...], beat_line_ids [line_id...], preset: a preset id OR the exact string NEED_NEW, need_new: null OR {reason text, class: missing_image|json_arrangement|renderer_gap}, needs_cutout boolean, pose text, framing text}. If preset is NEED_NEW then need_new must be an object; otherwise it must be null (schema `if/then`). NO free-text preset hint field.

## Semantic rules of this unit (master spec step 6)
6. shots: shot ids unique and consecutive per scene from 1; scene exists; ovi_ids inside the scene range; beat_line_ids belong to the scene; every scene has shots; every line of every scene is in some shot's beat_line_ids (message "<line>: line is in no shot beat"); `preset` is in `preset_ids` or NEED_NEW ("<shot>: unknown preset <p>").

Messages: tests assert only the quoted keywords/phrases of the rules plus the item id; for rules without a quoted phrase the message is `<item id>: <condition in plain words>`.

## BASE data (valid, note-free; the baseline for EVERY test; `validate(1, BASE_DOCS["shots"], BASE_DOCS, CTX)` must return [] and `schema_errors` must return [])
File `docs/pilot/nemotron_specs/stage1_base.json` has the keys "docs" (the nine documents) and "ctx". The test file must embed its own copy of what it needs as Python literals (copy the values below exactly):
```json
{
 "docs": {
  "shots": {
   "adhyay": 1,
   "shots": [
    {
     "shot_id": "S1-1",
     "scene_id": "S1",
     "ovi_ids": [
      1,
      2
     ],
     "beat_line_ids": [
      "S1-L1"
     ],
     "preset": "01_establishing_shot",
     "need_new": null,
     "needs_cutout": false,
     "pose": "standing",
     "framing": "wide"
    },
    {
     "shot_id": "S1-2",
     "scene_id": "S1",
     "ovi_ids": [
      3
     ],
     "beat_line_ids": [
      "S1-L2"
     ],
     "preset": "03_slow_cinematic_push",
     "need_new": null,
     "needs_cutout": false,
     "pose": "seated",
     "framing": "medium"
    },
    {
     "shot_id": "S2-1",
     "scene_id": "S2",
     "ovi_ids": [
      6,
      7
     ],
     "beat_line_ids": [
      "S2-L1"
     ],
     "preset": "03_slow_cinematic_push",
     "need_new": null,
     "needs_cutout": false,
     "pose": "seated",
     "framing": "close"
    }
   ]
  },
  "scenes": {
   "adhyay": 1,
   "scenes": [
    {
     "scene_id": "S1",
     "section_kind": "story",
     "ovi_range": [
      1,
      5
     ],
     "goal": "arrival",
     "turn": {
      "ovi": 3,
      "text": "he sits"
     },
     "line_ids": [
      "S1-L1",
      "S1-L2"
     ]
    },
    {
     "scene_id": "S2",
     "section_kind": "discourse",
     "ovi_range": [
      6,
      9
     ],
     "goal": "teaching",
     "turn": {
      "ovi": 7,
      "text": "the saying"
     },
     "line_ids": [
      "S2-L1"
     ],
     "teaching_treatment": "narration_over_typography"
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



## YOUR PREVIOUS tests/test_stage1_shots.py (repair it)
```python
from __future__ import annotations
import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SHOTS_PATH = ROOT / "scripts" / "pipeline" / "stage1" / "shots.py"
sys.path.insert(0, str(SHOTS_PATH.parent))
import shots  # type: ignore


def base() -> tuple[dict, dict]:
    docs = {
        "shots": {
            "adhyay": 1,
            "shots": [
                {
                    "shot_id": "S1-1",
                    "scene_id": "S1",
                    "ovi_ids": [1, 2],
                    "beat_line_ids": ["S1-L1"],
                    "preset": "01_establishing_shot",
                    "need_new": None,
                    "needs_cutout": False,
                    "pose": "standing",
                    "framing": "wide",
                },
                {
                    "shot_id": "S1-2",
                    "scene_id": "S1",
                    "ovi_ids": [3],
                    "beat_line_ids": ["S1-L2"],
                    "preset": "03_slow_cinematic_push",
                    "need_new": None,
                    "needs_cutout": False,
                    "pose": "seated",
                    "framing": "medium",
                },
                {
                    "shot_id": "S2-1",
                    "scene_id": "S2",
                    "ovi_ids": [6, 7],
                    "beat_line_ids": ["S2-L1"],
                    "preset": "03_slow_cinematic_push",
                    "need_new": None,
                    "needs_cutout": False,
                    "pose": "seated",
                    "framing": "close",
                },
            ],
        },
        "scenes": {
            "adhyay": 1,
            "scenes": [
                {
                    "scene_id": "S1",
                    "section_kind": "story",
                    "ovi_range": [1, 5],
                    "goal": "arrival",
                    "turn": {"ovi": 3, "text": "he sits"},
                    "line_ids": ["S1-L1", "S1-L2"],
                },
                {
                    "scene_id": "S2",
                    "section_kind": "discourse",
                    "ovi_range": [6, 9],
                    "goal": "teaching",
                    "turn": {"ovi": 7, "text": "the saying"},
                    "line_ids": ["S2-L1"],
                    "teaching_treatment": "narration_over_typography",
                },
            ],
        },
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
    """Set or delete a single item at dot/path. Returns mutated copy."""
    obj = copy.deepcopy(obj)
    parts = path.split(".")
    cur = obj
    for p in parts[:-1]:
        if p.isdigit():
            cur = cur[int(p)]
        else:
            cur = cur[p]
    last = parts[-1]
    if value is ...:
        if isinstance(cur, list):
            del cur[int(last)]
        else:
            del cur[last]
    else:
        if last.isdigit():
            cur[int(last)] = value
        else:
            cur[last] = value
    return obj


class TestSchema:
    @pytest.mark.parametrize("path", [
        "adhyay",
        "shots",
    ])
    def test_required_top_level(self, path):
        docs, ctx = base()
        doc = mutate(docs["shots"], path, ...)
        errs = shots.schema_errors(doc)
        assert any(f"shots {path}" in e for e in errs)

    @pytest.mark.parametrize("idx,field", [
        (0, "shot_id"), (0, "scene_id"), (0, "ovi_ids"), (0, "beat_line_ids"),
        (0, "preset"), (0, "need_new"), (0, "needs_cutout"), (0, "pose"), (0, "framing"),
    ])
    def test_required_shot_fields(self, idx, field):
        docs, ctx = base()
        doc = mutate(docs["shots"], f"shots.{idx}.{field}", ...)
        errs = shots.schema_errors(doc)
        assert any(f"shots shots/{idx}/{field}" in e for e in errs)

    @pytest.mark.parametrize("idx,field,val", [
        (0, "shot_id", "X1-1"),
        (0, "scene_id", "X1"),
        (0, "ovi_ids", "not-array"),
        (0, "ovi_ids", [0]),
        (0, "ovi_ids", [1.5]),
        (0, "beat_line_ids", "not-array"),
        (0, "beat_line_ids", ["X1-L1"]),
        (0, "preset", 123),
        (0, "preset", "bad_preset"),
        (0, "need_new", "not-object"),
        (0, "need_new", {"reason": "x", "class": "bad_class"}),
        (0, "needs_cutout", "not-bool"),
        (0, "pose", ""),
        (0, "pose", "x" * 401),
        (0, "framing", ""),
        (0, "framing", "x" * 401),
    ])
    def test_shot_field_types_and_formats(self, idx, field, val):
        docs, ctx = base()
        doc = mutate(docs["shots"], f"shots.{idx}.{field}", val)
        errs = shots.schema_errors(doc)
        assert any(f"shots shots/{idx}/{field}" in e for e in errs)

    @pytest.mark.parametrize("idx,extra", [
        (0, "hint"),
        (0, "extra_field"),
    ])
    def test_shot_no_extra_keys(self, idx, extra):
        docs, ctx = base()
        doc = mutate(docs["shots"], f"shots.{idx}.{extra}", "x")
        errs = shots.schema_errors(doc)
        assert any(f"shots shots/{idx}/{extra}" in e for e in errs)

    def test_need_new_if_then_need_new_without_preset_need_new(self):
        docs, ctx = base()
        doc = mutate(docs["shots"], "shots.0.preset", "01_establishing_shot")
        doc = mutate(doc, "shots.0.need_new", {"reason": "r", "class": "missing_image"})
        errs = shots.schema_errors(doc)
        assert any("shots shots/0/need_new" in e for e in errs)

    def test_need_new_if_then_preset_need_new_requires_object(self):
        docs, ctx = base()
        doc = mutate(docs["shots"], "shots.0.preset", "NEED_NEW")
        doc = mutate(doc, "shots.0.need_new", None)
        errs = shots.schema_errors(doc)
        assert any("shots shots/0/need_new" in e for e in errs)

    def test_need_new_class_enum(self):
        docs, ctx = base()
        doc = mutate(docs["shots"], "shots.0.preset", "NEED_NEW")
        doc = mutate(doc, "shots.0.need_new", {"reason": "r", "class": "bad"})
        errs = shots.schema_errors(doc)
        assert any("shots shots/0/need_new/class" in e for e in errs)


class TestValidate:
    def test_positive(self):
        docs, ctx = base()
        errs = shots.validate(1, docs["shots"], docs, ctx)
        assert errs == []

    def test_adhyay_mismatch(self):
        docs, ctx = base()
        doc = mutate(docs["shots"], "adhyay", 2)
        errs = shots.validate(1, doc, docs, ctx)
        assert any("shots adhyay 1 does not match 2" in e for e in errs)

    @pytest.mark.parametrize("idx,val", [
        (0, "S1-1"),  # duplicate
        (1, "S1-3"),  # non-consecutive
    ])
    def test_shot_id_unique_consecutive(self, idx, val):
        docs, ctx = base()
        doc = mutate(docs["shots"], f"shots.{idx}.shot_id", val)
        errs = shots.validate(1, doc, docs, ctx)
        assert any("S1" in e and ("unique" in e or "consecutive" in e) for e in errs)

    def test_scene_exists(self):
        docs, ctx = base()
        doc = mutate(docs["shots"], "shots.0.scene_id", "S9")
        errs = shots.validate(1, doc, docs, ctx)
        assert any("S1-1" in e and "scene" in e for e in errs)

    def test_ovi_ids_in_scene_range(self):
        docs, ctx = base()
        doc = mutate(docs["shots"], "shots.0.ovi_ids", [10])
        errs = shots.validate(1, doc, docs, ctx)
        assert any("S1-1" in e and "ovi" in e for e in errs)

    def test_beat_line_ids_belong_to_scene(self):
        docs, ctx = base()
        doc = mutate(docs["shots"], "shots.0.beat_line_ids", ["S2-L1"])
        errs = shots.validate(1, doc, docs, ctx)
        assert any("S1-1" in e and "beat_line" in e for e in errs)

    def test_every_scene_has_shots(self):
        docs, ctx = base()
        doc = mutate(docs["shots"], "shots", [
            {"shot_id": "S1-1", "scene_id": "S1", "ovi_ids": [1], "beat_line_ids": ["S1-L1"],
             "preset": "01_establishing_shot", "need_new": None, "needs_cutout": False,
             "pose": "x", "framing": "x"},
        ])
        errs = shots.validate(1, doc, docs, ctx)
        assert any("S2" in e and "shot" in e for e in errs)

    def test_every_line_in_some_shot_beat(self):
        docs, ctx = base()
        doc = mutate(docs["shots"], "shots.0.beat_line_ids", [])
        errs = shots.validate(1, doc, docs, ctx)
        assert any("S1-L1" in e and "no shot beat" in e for e in errs)

    def test_unknown_preset(self):
        docs, ctx = base()
        doc = mutate(docs["shots"], "shots.0.preset", "99_unknown")
        errs = shots.validate(1, doc, docs, ctx)
        assert any("S1-1" in e and "unknown preset" in e for e in errs)

    def test_preset_need_new_allows_need_new_object(self):
        docs, ctx = base()
        doc = mutate(docs["shots"], "shots.0.preset", "NEED_NEW")
        doc = mutate(doc, "shots.0.need_new", {"reason": "need new", "class": "missing_image"})
        errs = shots.validate(1, doc, docs, ctx)
        assert errs == []

    def test_empty_context_missing_refs(self):
        docs, ctx = base()
        empty_ctx = {
            "script_line_ids": [], "core_line_ids": [], "chapter_ovis": [],
            "unfilmed_ovis": [], "preset_ids": [], "sound_ids": [],
            "saved_voices": {}, "speaking_characters": [], "known_states": {},
        }
        errs = shots.validate(1, docs["shots"], docs, empty_ctx)
        assert any("S1-L1" in e and "not in the script" in e for e in errs)
        assert any("01_establishing_shot" in e and "unknown preset" in e for e in errs)

```
