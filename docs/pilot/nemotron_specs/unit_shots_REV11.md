# FIX CALL: return BOTH files in full: `scripts/pipeline/stage1/shots.py` and `tests/test_stage1_shots.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
.....................................................                    [100%]
53 passed in 0.08s

```

## SPEC
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



## CURRENT MODULE scripts/pipeline/stage1/shots.py
```python
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema import Draft202012Validator

SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "stage1_shots",
    "type": "object",
    "additionalProperties": False,
    "required": ["adhyay", "shots"],
    "properties": {
        "adhyay": {"type": "integer", "minimum": 1, "maximum": 21},
        "shots": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "shot_id",
                    "scene_id",
                    "ovi_ids",
                    "beat_line_ids",
                    "preset",
                    "need_new",
                    "needs_cutout",
                    "pose",
                    "framing",
                ],
                "properties": {
                    "shot_id": {"type": "string", "pattern": "^S[0-9]{1,2}-[0-9]{1,2}$"},
                    "scene_id": {"type": "string", "pattern": "^S[0-9]{1,2}$"},
                    "ovi_ids": {
                        "type": "array",
                        "items": {"type": "integer", "minimum": 1},
                        "minItems": 1,
                    },
                    "beat_line_ids": {
                        "type": "array",
                        "items": {"type": "string", "pattern": "^S[0-9]{1,2}-L[0-9]{1,3}$"},
                        "minItems": 1,
                    },
                    "preset": {"type": "string", "pattern": "^([0-9]{2}_[a-z0-9_]+|NEED_NEW)$"},
                    "need_new": {"type": ["object", "null"]},
                    "needs_cutout": {"type": "boolean"},
                    "pose": {"type": "string", "minLength": 1, "maxLength": 400},
                    "framing": {"type": "string", "minLength": 1, "maxLength": 400},
                },
                "if": {"properties": {"preset": {"const": "NEED_NEW"}}},
                "then": {
                    "properties": {
                        "need_new": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["reason", "class"],
                            "properties": {
                                "reason": {"type": "string", "minLength": 1, "maxLength": 400},
                                "class": {"enum": ["missing_image", "json_arrangement", "renderer_gap"]},
                            },
                        }
                    }
                },
                "else": {"properties": {"need_new": {"type": "null"}}},
            },
        },
    },
}

_validator = Draft202012Validator(SCHEMA)


def schema_errors(doc: dict[str, Any]) -> list[str]:
    errors = []
    if not isinstance(doc, dict):
        errors.append("shots doc: document must be an object")
        return errors
    for err in _validator.iter_errors(doc):
        path = "/".join(str(p) for p in err.path) if err.path else "doc"
        errors.append(f"shots {path}: {err.message}")
    return errors


def _validate_impl(adhyay: int, doc: dict[str, Any], docs: dict[str, Any], ctx: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    notes: list[str] = []

    # Guard: doc must be a dict
    if not isinstance(doc, dict):
        errors.append("shots doc: document must be an object")
        return errors + notes

    # Adhyay check
    doc_adhyay = doc.get("adhyay")
    if doc_adhyay != adhyay:
        errors.append(f"shots adhyay {doc_adhyay} does not match {adhyay}")

    shots_list = doc.get("shots", [])
    if not isinstance(shots_list, list):
        shots_list = []

    scenes_doc = docs.get("scenes", {})
    if not isinstance(scenes_doc, dict):
        scenes_doc = {}
    scenes = scenes_doc.get("scenes", [])
    if not isinstance(scenes, list):
        scenes = []

    # Build scene lookup
    scene_by_id = {}
    for s in scenes:
        if isinstance(s, dict) and "scene_id" in s and isinstance(s["scene_id"], str):
            scene_by_id[s["scene_id"]] = s

    # Collect preset_ids from ctx
    preset_ids = set(ctx.get("preset_ids", []) or [])

    # Track shot numbers per scene for consecutiveness
    shot_nums_by_scene: dict[str, list[int]] = {}
    shot_ids_seen: set[str] = set()

    # Track which lines are covered by shots (only lines belonging to the shot's scene)
    covered_lines: set[str] = set()

    for shot in shots_list:
        if not isinstance(shot, dict):
            continue
        shot_id = shot.get("shot_id", "")
        scene_id = shot.get("scene_id", "")

        # Unique shot ids
        if isinstance(shot_id, str) and shot_id in shot_ids_seen:
            errors.append(f"{shot_id}: duplicate shot id")
        if isinstance(shot_id, str):
            shot_ids_seen.add(shot_id)

        # Parse shot number for consecutiveness
        if isinstance(shot_id, str):
            m = re.match(r"^S([0-9]{1,2})-([0-9]{1,2})$", shot_id)
            if m:
                scene_num = m.group(1)
                shot_num = int(m.group(2))
                key = f"S{scene_num}"
                shot_nums_by_scene.setdefault(key, []).append(shot_num)

        # Preset validation (run for every shot, even if scene missing)
        preset = shot.get("preset")
        if isinstance(preset, str) and preset != "NEED_NEW" and preset not in preset_ids:
            errors.append(f"{shot_id}: unknown preset {preset}")

        # Scene exists
        if not isinstance(scene_id, str) or scene_id not in scene_by_id:
            if isinstance(shot_id, str):
                errors.append(f"{shot_id}: scene {scene_id} does not exist")
            continue

        scene = scene_by_id[scene_id]

        # ovi_ids inside scene range
        ovi_range = scene.get("ovi_range", [])
        if isinstance(ovi_range, list) and len(ovi_range) == 2:
            lo, hi = ovi_range[0], ovi_range[1]
            if isinstance(lo, int) and isinstance(hi, int):
                ovi_ids = shot.get("ovi_ids")
                if isinstance(ovi_ids, list):
                    for ovi in ovi_ids:
                        if isinstance(ovi, int) and not (lo <= ovi <= hi):
                            errors.append(f"{shot_id}: ovi {ovi} outside scene range [{lo}, {hi}]")

        # beat_line_ids belong to the scene
        scene_line_ids = set()
        line_ids = scene.get("line_ids", [])
        if isinstance(line_ids, list):
            for lid in line_ids:
                if isinstance(lid, str):
                    scene_line_ids.add(lid)
        beat_line_ids = shot.get("beat_line_ids")
        if isinstance(beat_line_ids, list):
            for line_id in beat_line_ids:
                if isinstance(line_id, str):
                    if line_id not in scene_line_ids:
                        errors.append(f"{shot_id}: beat line {line_id} not in scene {scene_id}")
                    else:
                        covered_lines.add(line_id)

    # Consecutive shot numbers per scene from 1
    for scene_key, nums in shot_nums_by_scene.items():
        nums_sorted = sorted(nums)
        if nums_sorted != list(range(1, len(nums_sorted) + 1)):
            errors.append(f"{scene_key}: shot numbers not consecutive from 1")

    # Every scene has shots
    for scene in scenes:
        if not isinstance(scene, dict):
            continue
        scene_id = scene.get("scene_id", "")
        if isinstance(scene_id, str) and scene_id and not any(
            isinstance(s, dict) and s.get("scene_id") == scene_id for s in shots_list
        ):
            errors.append(f"{scene_id}: scene has no shots")

    # Every line of every scene is in some shot's beat_line_ids
    for scene in scenes:
        if not isinstance(scene, dict):
            continue
        line_ids = scene.get("line_ids", [])
        if isinstance(line_ids, list):
            for line_id in line_ids:
                if isinstance(line_id, str) and line_id not in covered_lines:
                    errors.append(f"{line_id}: line is in no shot beat")

    return errors + notes


def validate(adhyay: int, doc: dict[str, Any], docs: dict[str, Any], ctx: dict[str, Any]) -> list[str]:
    try:
        return _validate_impl(adhyay, doc, docs, ctx)
    except (TypeError, AttributeError, KeyError, ValueError, IndexError):
        return ["shots: malformed structure"]

```

## CURRENT TESTS tests/test_stage1_shots.py
```python
from __future__ import annotations
import copy
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SHOTS_PATH = ROOT / "scripts" / "pipeline" / "stage1" / "shots.py"
sys.path.insert(0, str(SHOTS_PATH.parent))
import shots  # type: ignore


BASE_DOCS = {
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
BASE_CTX = {
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
        cur = cur[p]
    return cur, path[-1]


def set_at(base, path, value):
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    parent[key] = value
    assert doc != base
    return doc


def delete_at(base, path):
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    del parent[key]
    assert doc != base
    return doc


def append_at(base, path, value):
    doc = copy.deepcopy(base)
    cur = doc
    for p in path:
        cur = cur[p]
    cur.append(value)
    assert doc != base
    return doc


def docs_ctx(docs=None, ctx=None):
    d = copy.deepcopy(BASE_DOCS)
    c = copy.deepcopy(BASE_CTX)
    if docs:
        d.update(docs)
    if ctx:
        c.update(ctx)
    return d, c


class TestSchema:
    @pytest.mark.parametrize("field", ["adhyay", "shots"])
    def test_required_root(self, field):
        doc = delete_at(BASE_DOCS["shots"], [field])
        errs = shots.schema_errors(doc)
        # jsonschema reports missing required at parent path "doc"
        assert any("shots doc" in e and field in e for e in errs)

    @pytest.mark.parametrize("idx,field", [
        (0, "shot_id"), (0, "scene_id"), (0, "ovi_ids"), (0, "beat_line_ids"),
        (0, "preset"), (0, "need_new"), (0, "needs_cutout"), (0, "pose"), (0, "framing"),
    ])
    def test_required_shot_fields(self, idx, field):
        doc = delete_at(BASE_DOCS["shots"], ["shots", idx, field])
        errs = shots.schema_errors(doc)
        assert any(f"shots shots/{idx}" in e and field in e for e in errs)

    @pytest.mark.parametrize("field", ["reason", "class"])
    def test_required_need_new_fields(self, field):
        # Must initialise need_new as object before deleting a field
        doc = set_at(BASE_DOCS["shots"], ["shots", 0, "preset"], "NEED_NEW")
        doc = set_at(doc, ["shots", 0, "need_new"], {"reason": "r", "class": "missing_image"})
        doc = delete_at(doc, ["shots", 0, "need_new", field])
        errs = shots.schema_errors(doc)
        # Error reported at need_new object path
        assert any(f"shots shots/0/need_new" in e and field in e for e in errs)

    @pytest.mark.parametrize("path,value", [
        (["shots", 0, "shot_id"], "X1-1"),
        (["shots", 0, "scene_id"], "X1"),
        (["shots", 0, "ovi_ids"], "not-array"),
        (["shots", 0, "ovi_ids"], [0]),
        (["shots", 0, "ovi_ids"], [1.5]),
        (["shots", 0, "beat_line_ids"], "not-array"),
        (["shots", 0, "beat_line_ids"], ["X1-L1"]),
        (["shots", 0, "preset"], 123),
        (["shots", 0, "preset"], "bogus"),
        (["shots", 0, "need_new"], "not-object"),
        (["shots", 0, "need_new"], {"reason": "x", "class": "bad_class"}),
        (["shots", 0, "needs_cutout"], "not-bool"),
        (["shots", 0, "pose"], ""),
        (["shots", 0, "pose"], "x" * 401),
        (["shots", 0, "framing"], ""),
        (["shots", 0, "framing"], "x" * 401),
    ])
    def test_shot_field_types_and_formats(self, path, value):
        doc = set_at(BASE_DOCS["shots"], path, value)
        errs = shots.schema_errors(doc)
        assert any(f"shots shots/{path[1]}/{path[2]}" in e for e in errs)

    @pytest.mark.parametrize("path,extra", [
        ([], "extra_root"),
        (["shots", 0], "extra_shot"),
        (["shots", 0, "need_new"], "extra_need_new"),
    ])
    def test_no_extra_keys(self, path, extra):
        # For need_new extra key, must initialise need_new as object first
        if path == ["shots", 0, "need_new"]:
            base = set_at(BASE_DOCS["shots"], ["shots", 0, "preset"], "NEED_NEW")
            base = set_at(base, ["shots", 0, "need_new"], {"reason": "r", "class": "missing_image"})
        else:
            base = BASE_DOCS["shots"]
        doc = set_at(base, path + [extra], "x")
        errs = shots.schema_errors(doc)
        # jsonschema path for extra key on shots[0] is "shots/0"
        loc = "doc" if not path else "/".join(str(p) for p in path)
        assert any(f"shots {loc}" in e and extra in e for e in errs)

    def test_need_new_if_then_preset_not_need_new_forbids_object(self):
        doc = set_at(BASE_DOCS["shots"], ["shots", 0, "need_new"], {"reason": "r", "class": "missing_image"})
        errs = shots.schema_errors(doc)
        assert any("shots shots/0/need_new" in e for e in errs)

    def test_need_new_if_then_preset_need_new_requires_object(self):
        # Base already has need_new=null; just flip preset to NEED_NEW
        doc = set_at(BASE_DOCS["shots"], ["shots", 0, "preset"], "NEED_NEW")
        errs = shots.schema_errors(doc)
        assert any("shots shots/0/need_new" in e for e in errs)

    def test_need_new_class_enum(self):
        doc = set_at(BASE_DOCS["shots"], ["shots", 0, "preset"], "NEED_NEW")
        doc = set_at(doc, ["shots", 0, "need_new"], {"reason": "r", "class": "bad"})
        errs = shots.schema_errors(doc)
        # Enum error may be reported at need_new or need_new/class; accept either
        assert any("shots shots/0/need_new" in e and "class" in e for e in errs)


class TestValidate:
    def test_positive(self):
        docs, ctx = docs_ctx()
        errs = shots.validate(1, docs["shots"], docs, ctx)
        assert errs == []

    def test_adhyay_mismatch(self):
        docs, ctx = docs_ctx()
        doc = set_at(docs["shots"], ["adhyay"], 2)
        errs = shots.validate(1, doc, docs, ctx)
        assert any("shots adhyay 2 does not match 1" in e for e in errs)

    def test_shot_id_duplicate(self):
        docs, ctx = docs_ctx()
        dup = copy.deepcopy(docs["shots"]["shots"][0])
        dup["shot_id"] = "S1-1"
        doc = append_at(docs["shots"], ["shots"], dup)
        errs = shots.validate(1, doc, docs, ctx)
        assert any("S1-1" in e for e in errs)

    def test_shot_id_non_consecutive(self):
        docs, ctx = docs_ctx()
        doc = set_at(docs["shots"], ["shots", 1, "shot_id"], "S1-4")
        errs = shots.validate(1, doc, docs, ctx)
        # Error mentions scene S1
        assert any("S1" in e for e in errs)

    def test_scene_exists(self):
        docs, ctx = docs_ctx()
        doc = set_at(docs["shots"], ["shots", 0, "scene_id"], "S9")
        errs = shots.validate(1, doc, docs, ctx)
        assert any("S1-1" in e for e in errs)

    def test_ovi_ids_in_scene_range(self):
        docs, ctx = docs_ctx()
        doc = set_at(docs["shots"], ["shots", 0, "ovi_ids"], [10])
        errs = shots.validate(1, doc, docs, ctx)
        assert any("S1-1" in e for e in errs)

    def test_beat_line_ids_belong_to_scene(self):
        docs, ctx = docs_ctx()
        doc = set_at(docs["shots"], ["shots", 0, "beat_line_ids"], ["S2-L1"])
        errs = shots.validate(1, doc, docs, ctx)
        assert any("S1-1" in e for e in errs)

    def test_every_scene_has_shots(self):
        docs, ctx = docs_ctx()
        doc = set_at(docs["shots"], ["shots"], [docs["shots"]["shots"][0]])
        errs = shots.validate(1, doc, docs, ctx)
        assert any("S2" in e for e in errs)

    def test_every_line_in_some_shot_beat(self):
        docs, ctx = docs_ctx()
        # Baseline: S1-1 covers S1-L1, S1-2 covers S1-L2
        # Change S1-2 to cover S1-L1, leaving S1-L2 uncovered
        doc = set_at(docs["shots"], ["shots", 1, "beat_line_ids"], ["S1-L1"])
        errs = shots.validate(1, doc, docs, ctx)
        assert any("S1-L2" in e for e in errs)

    def test_unknown_preset(self):
        docs, ctx = docs_ctx()
        doc = set_at(docs["shots"], ["shots", 0, "preset"], "99_unknown")
        errs = shots.validate(1, doc, docs, ctx)
        assert any("S1-1" in e and "unknown preset" in e for e in errs)

    def test_preset_need_new_allows_need_new_object(self):
        docs, ctx = docs_ctx()
        doc = set_at(docs["shots"], ["shots", 0, "preset"], "NEED_NEW")
        doc = set_at(doc, ["shots", 0, "need_new"], {"reason": "need new", "class": "missing_image"})
        errs = shots.validate(1, doc, docs, ctx)
        assert errs == []

    def test_empty_context_missing_refs(self):
        # Keep scenes valid; only empty preset_ids to trigger unknown preset
        docs, ctx = docs_ctx(
            ctx={"preset_ids": [], "script_line_ids": [], "core_line_ids": [], "chapter_ovis": [],
                 "unfilmed_ovis": [], "sound_ids": [], "saved_voices": {},
                 "speaking_characters": [], "known_states": {}},
        )
        errs = shots.validate(1, docs["shots"], docs, ctx)
        assert any("unknown preset" in e for e in errs)
        assert any("S1-1" in e for e in errs)

    def test_validate_odd_data_no_raise(self):
        # shots: null
        errs = shots.validate(1, {"adhyay": 1, "shots": None}, BASE_DOCS, BASE_CTX)
        assert isinstance(errs, list)
        # shots: [null]
        errs = shots.validate(1, {"adhyay": 1, "shots": [None]}, BASE_DOCS, BASE_CTX)
        assert isinstance(errs, list)
        # scenes not a dict
        errs = shots.validate(1, BASE_DOCS["shots"], {"scenes": "not-dict"}, BASE_CTX)
        assert isinstance(errs, list)
        # scenes.scenes not a list
        errs = shots.validate(1, BASE_DOCS["shots"], {"scenes": {"scenes": "not-list"}}, BASE_CTX)
        assert isinstance(errs, list)
        # scene with non-string scene_id
        bad_scenes = {"scenes": [{"scene_id": ["S1"], "ovi_range": [1,5], "line_ids": []}]}
        errs = shots.validate(1, BASE_DOCS["shots"], bad_scenes, BASE_CTX)
        assert isinstance(errs, list)
        # scene with non-int ovi_range
        bad_scenes = {"scenes": [{"scene_id": "S1", "ovi_range": ["a", 5], "line_ids": []}]}
        errs = shots.validate(1, BASE_DOCS["shots"], bad_scenes, BASE_CTX)
        assert isinstance(errs, list)
        # shot with non-string shot_id
        doc = set_at(BASE_DOCS["shots"], ["shots", 0, "shot_id"], ["S1-1"])
        errs = shots.validate(1, doc, BASE_DOCS, BASE_CTX)
        assert isinstance(errs, list)
        # shot with non-string scene_id
        doc = set_at(BASE_DOCS["shots"], ["shots", 0, "scene_id"], ["S1"])
        errs = shots.validate(1, doc, BASE_DOCS, BASE_CTX)
        assert isinstance(errs, list)

    def test_shot_field_types_and_formats_need_new_class_enum(self):
        # This test ensures the need_new class enum is exercised with NEED_NEW preset
        docs, ctx = docs_ctx()
        doc = set_at(docs["shots"], ["shots", 0, "preset"], "NEED_NEW")
        doc = set_at(doc, ["shots", 0, "need_new"], {"reason": "r", "class": "bad_class"})
        errs = shots.validate(1, doc, docs, ctx)
        # Should not crash; schema would catch this but validate should handle gracefully
        assert isinstance(errs, list)

    def test_ovi_ids_not_a_list(self):
        # ovi_ids as non-list should not raise, just skip validation
        docs, ctx = docs_ctx()
        doc = set_at(docs["shots"], ["shots", 0, "ovi_ids"], 5)
        errs = shots.validate(1, doc, docs, ctx)
        assert isinstance(errs, list)

    def test_beat_line_ids_not_a_list(self):
        # beat_line_ids as non-list should not raise, just skip validation
        docs, ctx = docs_ctx()
        doc = set_at(docs["shots"], ["shots", 0, "beat_line_ids"], None)
        errs = shots.validate(1, doc, docs, ctx)
        assert isinstance(errs, list)

    def test_scene_line_ids_not_a_list(self):
        # scene line_ids as non-list should not raise
        docs, ctx = docs_ctx()
        bad_scenes = {"scenes": [{"scene_id": "S1", "ovi_range": [1,5], "line_ids": 5}]}
        errs = shots.validate(1, BASE_DOCS["shots"], bad_scenes, BASE_CTX)
        assert isinstance(errs, list)

    def test_beat_line_wrong_scene_not_counted_as_covered(self):
        # S2-L1 assigned to S1 shot; S2 has no shots covering S2-L1
        # Should report both: wrong assignment AND S2-L1 uncovered
        docs, ctx = docs_ctx()
        doc = set_at(docs["shots"], ["shots", 0, "beat_line_ids"], ["S2-L1"])
        # Remove S2 shot so S2-L1 has no valid coverage
        doc = set_at(doc, ["shots"], [doc["shots"][0]])
        errs = shots.validate(1, doc, docs, ctx)
        # Should have both errors
        assert any("S1-1" in e and "not in scene" in e for e in errs)
        assert any("S2-L1" in e and "line is in no shot beat" in e for e in errs)

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
