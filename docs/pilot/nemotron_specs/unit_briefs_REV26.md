# FIX CALL: return BOTH files in full: `scripts/pipeline/stage1/briefs.py` and `tests/test_stage1_briefs.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
........................................................................ [ 78%]
....................                                                     [100%]
92 passed in 0.11s

```

## SPEC
# UNIT SPEC: Stage 1 document `briefs` (schema `stage1_image_briefs`)
This is ONE unit of the Stage 1 contract (the master spec `stage1_v2.md` was split because one big spec gave unreliable tests). Keep the unit small and exact.
Module: `scripts/pipeline/stage1/briefs.py`. Tests: `tests/test_stage1_briefs.py`. Style: `from __future__ import annotations`, standard library plus `jsonschema`; no print, no network, nothing at import time; tests use only the BASE data below and `tmp_path`; the test file loads the module by path with importlib (`ROOT = Path(__file__).resolve().parents[1]`, `ROOT / "scripts" / "pipeline" / "stage1" / "briefs.py"`).

## Module API (exactly this)
- `SCHEMA`: dict, JSON Schema draft 2020-12 for the document, `additionalProperties: false` on EVERY object (nested too), `$schema` = "https://json-schema.org/draft/2020-12/schema", `title` = "stage1_image_briefs".
- `schema_errors(doc) -> list[str]`: one message per jsonschema error, formatted "briefs <path>: <message>" (path joined by "/", "doc" when empty).
- `validate(adhyay, doc, docs, ctx) -> list[str]`: SEMANTIC checks only (the schema has already passed; it must still never raise on odd data). `docs` is a dict of ALL nine documents (key names: story_map, coverage, scenes, shots, briefs, looks, voices, sounds, questions; a missing one counts as empty), `ctx` the context dict (keys: script_line_ids list, core_line_ids set, chapter_ovis set, unfilmed_ovis set, preset_ids set, sound_ids set, saved_voices dict voice_key->voice_id, speaking_characters set, known_states dict entity_id->set of state ids). Lists in ctx may arrive as lists or sets: convert with set(). Notes (messages that start with "note: ") come AFTER error messages. Include the adhyay check first: "briefs adhyay <n> does not match <adhyay>".

## Ids and common types
scene_id `^S[0-9]{1,2}$`; shot_id `^S[0-9]{1,2}-[0-9]{1,2}$`; line_id `^S[0-9]{1,2}-L[0-9]{1,3}$`; image id (Stage 1 brief) `^s[0-9]{1,2}_[a-z][a-z0-9_]{0,40}$`; ovi = integer >= 1; adhyay = integer 1..21; text = string 1..400 chars; preset id = string matching `^[0-9]{2}_[a-z0-9_]+$`; sound id `^(bed|fx)_[a-z0-9_]+$`.

## The document shape (from the master spec)
5. `stage1_image_briefs`: `images`: array of {image_id, scene_id, shot_ids [shot_id...], people [{name, position, pose, gaze}], place_id, prop (text or null), prop_state (text or null), camera, light, reason_new, on_screen_facts [text...] (only things visible), references {characters [text...], place text, style_anchor text, prop text or null}}.

## Semantic rules of this unit (master spec step 7)
7. briefs: image ids unique with scene prefix (scene S4 -> `s4_`); scene exists; shot_ids exist and belong to the same scene; every brief's people has no empty name; on_screen_facts non-empty.

Messages: tests assert only the quoted keywords/phrases of the rules plus the item id; for rules without a quoted phrase the message is `<item id>: <condition in plain words>`.

## BASE data (valid, note-free; the baseline for EVERY test; `validate(1, BASE_DOCS["briefs"], BASE_DOCS, CTX)` must return [] and `schema_errors` must return [])
File `docs/pilot/nemotron_specs/stage1_base.json` has the keys "docs" (the nine documents) and "ctx". The test file must embed its own copy of what it needs as Python literals (copy the values below exactly):
```json
{
 "docs": {
  "briefs": {
   "adhyay": 1,
   "images": [
    {
     "image_id": "s1_maharaj_seated",
     "scene_id": "S1",
     "shot_ids": [
      "S1-2"
     ],
     "people": [
      {
       "name": "Maharaj",
       "position": "centre",
       "pose": "seated",
       "gaze": "forward"
      }
     ],
     "place_id": "roadside",
     "prop": null,
     "prop_state": null,
     "camera": "medium, eye level",
     "light": "morning",
     "reason_new": "new pose",
     "on_screen_facts": [
      "Maharaj sits by the road"
     ],
     "references": {
      "characters": [
       "gajanan_maharaj"
      ],
      "place": "roadside",
      "style_anchor": "ref_temple",
      "prop": null
     }
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
  },
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



## CURRENT MODULE scripts/pipeline/stage1/briefs.py
```python
from __future__ import annotations

import json
import re
from typing import Any

import jsonschema
from jsonschema import Draft202012Validator

SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "stage1_image_briefs",
    "type": "object",
    "additionalProperties": False,
    "required": ["adhyay", "images"],
    "properties": {
        "adhyay": {"type": "integer", "minimum": 1, "maximum": 21},
        "images": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "image_id",
                    "scene_id",
                    "shot_ids",
                    "people",
                    "place_id",
                    "prop",
                    "prop_state",
                    "camera",
                    "light",
                    "reason_new",
                    "on_screen_facts",
                    "references",
                ],
                "properties": {
                    "image_id": {
                        "type": "string",
                        "pattern": "^s[0-9]{1,2}_[a-z][a-z0-9_]{0,40}$",
                    },
                    "scene_id": {"type": "string", "pattern": "^S[0-9]{1,2}$"},
                    "shot_ids": {
                        "type": "array",
                        "items": {"type": "string", "pattern": "^S[0-9]{1,2}-[0-9]{1,2}$"},
                        "minItems": 1,
                    },
                    "people": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["name", "position", "pose", "gaze"],
                            "properties": {
                                "name": {"type": "string", "minLength": 1, "maxLength": 400},
                                "position": {"type": "string", "minLength": 1, "maxLength": 400},
                                "pose": {"type": "string", "minLength": 1, "maxLength": 400},
                                "gaze": {"type": "string", "minLength": 1, "maxLength": 400},
                            },
                        },
                    },
                    "place_id": {"type": "string", "minLength": 1, "maxLength": 400},
                    "prop": {"type": ["string", "null"], "minLength": 1, "maxLength": 400},
                    "prop_state": {"type": ["string", "null"], "minLength": 1, "maxLength": 400},
                    "camera": {"type": "string", "minLength": 1, "maxLength": 400},
                    "light": {"type": "string", "minLength": 1, "maxLength": 400},
                    "reason_new": {"type": "string", "minLength": 1, "maxLength": 400},
                    "on_screen_facts": {
                        "type": "array",
                        "items": {"type": "string", "minLength": 1, "maxLength": 400},
                        "minItems": 1,
                    },
                    "references": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["characters", "place", "style_anchor", "prop"],
                        "properties": {
                            "characters": {
                                "type": "array",
                                "items": {"type": "string", "minLength": 1, "maxLength": 400},
                            },
                            "place": {"type": "string", "minLength": 1, "maxLength": 400},
                            "style_anchor": {"type": "string", "minLength": 1, "maxLength": 400},
                            "prop": {"type": ["string", "null"], "minLength": 1, "maxLength": 400},
                        },
                    },
                },
            },
        },
    },
}

_validator = Draft202012Validator(SCHEMA)


def schema_errors(doc: Any) -> list[str]:
    errors = []
    for err in _validator.iter_errors(doc):
        path = "/".join(str(p) for p in err.path) if err.path else "doc"
        errors.append(f"briefs {path}: {err.message}")
    return errors


def _validate_semantic(adhyay: int, doc: Any, docs: dict[str, Any], ctx: dict[str, Any]) -> list[str]:
    messages: list[str] = []
    notes: list[str] = []

    if not isinstance(doc, dict):
        return ["briefs doc: not an object"]

    doc_adhyay = doc.get("adhyay")
    if doc_adhyay != adhyay:
        messages.append(f"briefs adhyay {doc_adhyay} does not match {adhyay}")

    images = doc.get("images", [])
    if not isinstance(images, list):
        return messages

    scenes_doc = docs.get("scenes", {})
    scenes_list = scenes_doc.get("scenes", []) if isinstance(scenes_doc, dict) else []
    scene_ids = {
        sid for s in scenes_list
        if isinstance(s, dict)
        for sid in [s.get("scene_id")]
        if isinstance(sid, str)
    }

    shots_doc = docs.get("shots", {})
    shots_list = shots_doc.get("shots", []) if isinstance(shots_doc, dict) else []
    shot_map: dict[str, str] = {}
    for sh in shots_list:
        if isinstance(sh, dict):
            sid = sh.get("shot_id")
            scid = sh.get("scene_id")
            if isinstance(sid, str) and isinstance(scid, str):
                shot_map[sid] = scid

    seen_image_ids: set[str] = set()

    for img in images:
        if not isinstance(img, dict):
            continue
        img_id = img.get("image_id")
        if not isinstance(img_id, str):
            continue

        if img_id in seen_image_ids:
            messages.append(f"{img_id}: unique with scene prefix")
        seen_image_ids.add(img_id)

        scene_id = img.get("scene_id")
        if isinstance(scene_id, str):
            m = re.match(r"^S([0-9]{1,2})$", scene_id)
            if m:
                expected_prefix = f"s{int(m.group(1))}_"
                if not img_id.startswith(expected_prefix):
                    messages.append(f"{img_id}: unique with scene prefix")

        if isinstance(scene_id, str) and scene_id not in scene_ids:
            messages.append(f"{img_id}: scene {scene_id} does not exist")

        shot_ids = img.get("shot_ids", [])
        if isinstance(shot_ids, list):
            for sid in shot_ids:
                if not isinstance(sid, str) or sid not in shot_map:
                    messages.append(f"{img_id}: shot_ids exist and belong to the same scene")
                elif shot_map[sid] != scene_id:
                    messages.append(f"{img_id}: shot_ids exist and belong to the same scene")

        people = img.get("people", [])
        for i, p in enumerate(people):
            name = p.get("name")
            if not isinstance(name, str) or name.strip() == "":
                messages.append(f"{img_id}: no empty name")

        on_screen_facts = img.get("on_screen_facts", [])
        if not isinstance(on_screen_facts, list) or len(on_screen_facts) == 0:
            messages.append(f"{img_id}: non-empty")

    return messages + notes


def validate(adhyay: int, doc: Any, docs: dict[str, Any], ctx: dict[str, Any]) -> list[str]:
    try:
        return _validate_semantic(adhyay, doc, docs, ctx)
    except (TypeError, AttributeError, KeyError, ValueError, IndexError):
        return ["briefs: malformed structure"]

```

## CURRENT TESTS tests/test_stage1_briefs.py
```python
from __future__ import annotations
import copy
import importlib.util
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "pipeline" / "stage1" / "briefs.py"
spec = importlib.util.spec_from_file_location("briefs", MODULE_PATH)
briefs = importlib.util.module_from_spec(spec)
sys.modules["briefs"] = briefs
spec.loader.exec_module(briefs)

BASE_DOCS = {
    "briefs": {
        "adhyay": 1,
        "images": [
            {
                "image_id": "s1_maharaj_seated",
                "scene_id": "S1",
                "shot_ids": ["S1-2"],
                "people": [
                    {"name": "Maharaj", "position": "centre", "pose": "seated", "gaze": "forward"}
                ],
                "place_id": "roadside",
                "prop": None,
                "prop_state": None,
                "camera": "medium, eye level",
                "light": "morning",
                "reason_new": "new pose",
                "on_screen_facts": ["Maharaj sits by the road"],
                "references": {
                    "characters": ["gajanan_maharaj"],
                    "place": "roadside",
                    "style_anchor": "ref_temple",
                    "prop": None,
                },
            }
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


def _deepcopy(obj):
    return copy.deepcopy(obj)


def get_parent(doc, path):
    """Walk path (list of str/int) to parent of final key/index."""
    cur = doc
    for part in path[:-1]:
        if isinstance(part, int):
            cur = cur[part]
        else:
            cur = cur[part]
    return cur


def set_at(base, path, value):
    """Return deep copy with path set to value; assert mutation occurred."""
    doc = _deepcopy(base)
    parent = get_parent(doc, path)
    key = path[-1]
    if isinstance(key, int):
        parent[key] = value
    else:
        parent[key] = value
    assert doc != base, "set_at: no mutation"
    return doc


def delete_at(base, path):
    """Return deep copy with path deleted; assert mutation occurred."""
    doc = _deepcopy(base)
    parent = get_parent(doc, path)
    key = path[-1]
    if isinstance(key, int):
        del parent[key]
    else:
        del parent[key]
    assert doc != base, "delete_at: no mutation"
    return doc


def append_at(base, path, value):
    """Return deep copy with value appended to list at path; assert mutation occurred."""
    doc = _deepcopy(base)
    parent = get_parent(doc, path)
    key = path[-1]
    lst = parent[key]
    assert isinstance(lst, list), "append_at: target not a list"
    lst.append(value)
    assert doc != base, "append_at: no mutation"
    return doc


def base():
    return {"docs": _deepcopy(BASE_DOCS), "ctx": _deepcopy(BASE_CTX)}


# ---- Schema error cases ----
# Each case: (path_list, mutation_fn, expected_field_in_message)
# mutation_fn takes base doc and returns mutated doc
SCHEMA_CASES = [
    # Root required fields
    (["adhyay"], lambda d: delete_at(d, ["adhyay"]), "adhyay"),
    (["images"], lambda d: delete_at(d, ["images"]), "images"),
    # Root extra key
    (["extra_root"], lambda d: set_at(d, ["extra_root"], 1), "extra_root"),
    # Image required fields
    (["images", 0, "image_id"], lambda d: delete_at(d, ["images", 0, "image_id"]), "image_id"),
    (["images", 0, "scene_id"], lambda d: delete_at(d, ["images", 0, "scene_id"]), "scene_id"),
    (["images", 0, "shot_ids"], lambda d: delete_at(d, ["images", 0, "shot_ids"]), "shot_ids"),
    (["images", 0, "people"], lambda d: delete_at(d, ["images", 0, "people"]), "people"),
    (["images", 0, "place_id"], lambda d: delete_at(d, ["images", 0, "place_id"]), "place_id"),
    (["images", 0, "prop"], lambda d: delete_at(d, ["images", 0, "prop"]), "prop"),
    (["images", 0, "prop_state"], lambda d: delete_at(d, ["images", 0, "prop_state"]), "prop_state"),
    (["images", 0, "camera"], lambda d: delete_at(d, ["images", 0, "camera"]), "camera"),
    (["images", 0, "light"], lambda d: delete_at(d, ["images", 0, "light"]), "light"),
    (["images", 0, "reason_new"], lambda d: delete_at(d, ["images", 0, "reason_new"]), "reason_new"),
    (["images", 0, "on_screen_facts"], lambda d: delete_at(d, ["images", 0, "on_screen_facts"]), "on_screen_facts"),
    (["images", 0, "references"], lambda d: delete_at(d, ["images", 0, "references"]), "references"),
    # People required fields
    (["images", 0, "people", 0, "name"], lambda d: delete_at(d, ["images", 0, "people", 0, "name"]), "name"),
    (["images", 0, "people", 0, "position"], lambda d: delete_at(d, ["images", 0, "people", 0, "position"]), "position"),
    (["images", 0, "people", 0, "pose"], lambda d: delete_at(d, ["images", 0, "people", 0, "pose"]), "pose"),
    (["images", 0, "people", 0, "gaze"], lambda d: delete_at(d, ["images", 0, "people", 0, "gaze"]), "gaze"),
    # References required fields
    (["images", 0, "references", "characters"], lambda d: delete_at(d, ["images", 0, "references", "characters"]), "characters"),
    (["images", 0, "references", "place"], lambda d: delete_at(d, ["images", 0, "references", "place"]), "place"),
    (["images", 0, "references", "style_anchor"], lambda d: delete_at(d, ["images", 0, "references", "style_anchor"]), "style_anchor"),
    (["images", 0, "references", "prop"], lambda d: delete_at(d, ["images", 0, "references", "prop"]), "prop"),
    # Type/format violations
    (["images", 0, "image_id"], lambda d: set_at(d, ["images", 0, "image_id"], "S1_bad"), "image_id"),
    (["images", 0, "scene_id"], lambda d: set_at(d, ["images", 0, "scene_id"], "X1"), "scene_id"),
    (["images", 0, "shot_ids"], lambda d: set_at(d, ["images", 0, "shot_ids"], "not-array"), "shot_ids"),
    (["images", 0, "shot_ids", 0], lambda d: set_at(d, ["images", 0, "shot_ids", 0], "bad-shot"), "shot_ids"),
    (["images", 0, "people"], lambda d: set_at(d, ["images", 0, "people"], "not-array"), "people"),
    (["images", 0, "people", 0], lambda d: set_at(d, ["images", 0, "people", 0], "not-object"), "people"),
    (["images", 0, "people", 0, "name"], lambda d: set_at(d, ["images", 0, "people", 0, "name"], ""), "name"),
    (["images", 0, "place_id"], lambda d: set_at(d, ["images", 0, "place_id"], 123), "place_id"),
    (["images", 0, "prop"], lambda d: set_at(d, ["images", 0, "prop"], 123), "prop"),
    (["images", 0, "prop_state"], lambda d: set_at(d, ["images", 0, "prop_state"], 123), "prop_state"),
    (["images", 0, "camera"], lambda d: set_at(d, ["images", 0, "camera"], ""), "camera"),
    (["images", 0, "light"], lambda d: set_at(d, ["images", 0, "light"], ""), "light"),
    (["images", 0, "reason_new"], lambda d: set_at(d, ["images", 0, "reason_new"], ""), "reason_new"),
    (["images", 0, "on_screen_facts"], lambda d: set_at(d, ["images", 0, "on_screen_facts"], "not-array"), "on_screen_facts"),
    (["images", 0, "on_screen_facts", 0], lambda d: set_at(d, ["images", 0, "on_screen_facts", 0], ""), "on_screen_facts"),
    (["images", 0, "references"], lambda d: set_at(d, ["images", 0, "references"], "not-object"), "references"),
    (["images", 0, "references", "characters"], lambda d: set_at(d, ["images", 0, "references", "characters"], "not-array"), "characters"),
    (["images", 0, "references", "place"], lambda d: set_at(d, ["images", 0, "references", "place"], 123), "place"),
    (["images", 0, "references", "style_anchor"], lambda d: set_at(d, ["images", 0, "references", "style_anchor"], 123), "style_anchor"),
    (["images", 0, "references", "prop"], lambda d: set_at(d, ["images", 0, "references", "prop"], 123), "prop"),
    # Extra keys on nested objects (add to otherwise valid object)
    (["images", 0], lambda d: set_at(d, ["images", 0, "extra"], 1), "extra"),
    (["images", 0, "people", 0], lambda d: set_at(d, ["images", 0, "people", 0, "extra"], 1), "extra"),
    (["images", 0, "references"], lambda d: set_at(d, ["images", 0, "references", "extra"], 1), "extra"),
    # minLength violations for text fields (1..400)
    (["images", 0, "people", 0, "position"], lambda d: set_at(d, ["images", 0, "people", 0, "position"], ""), "position"),
    (["images", 0, "people", 0, "pose"], lambda d: set_at(d, ["images", 0, "people", 0, "pose"], ""), "pose"),
    (["images", 0, "people", 0, "gaze"], lambda d: set_at(d, ["images", 0, "people", 0, "gaze"], ""), "gaze"),
    (["images", 0, "place_id"], lambda d: set_at(d, ["images", 0, "place_id"], ""), "place_id"),
    (["images", 0, "camera"], lambda d: set_at(d, ["images", 0, "camera"], ""), "camera"),
    (["images", 0, "light"], lambda d: set_at(d, ["images", 0, "light"], ""), "light"),
    (["images", 0, "reason_new"], lambda d: set_at(d, ["images", 0, "reason_new"], ""), "reason_new"),
    (["images", 0, "references", "place"], lambda d: set_at(d, ["images", 0, "references", "place"], ""), "place"),
    (["images", 0, "references", "style_anchor"], lambda d: set_at(d, ["images", 0, "references", "style_anchor"], ""), "style_anchor"),
    (["images", 0, "references", "prop"], lambda d: set_at(d, ["images", 0, "references", "prop"], ""), "prop"),
    (["images", 0, "prop"], lambda d: set_at(d, ["images", 0, "prop"], ""), "prop"),
    (["images", 0, "prop_state"], lambda d: set_at(d, ["images", 0, "prop_state"], ""), "prop_state"),
    # maxLength violations for text fields (>400)
    (["images", 0, "people", 0, "name"], lambda d: set_at(d, ["images", 0, "people", 0, "name"], "x" * 401), "name"),
    (["images", 0, "people", 0, "position"], lambda d: set_at(d, ["images", 0, "people", 0, "position"], "x" * 401), "position"),
    (["images", 0, "people", 0, "pose"], lambda d: set_at(d, ["images", 0, "people", 0, "pose"], "x" * 401), "pose"),
    (["images", 0, "people", 0, "gaze"], lambda d: set_at(d, ["images", 0, "people", 0, "gaze"], "x" * 401), "gaze"),
    (["images", 0, "place_id"], lambda d: set_at(d, ["images", 0, "place_id"], "x" * 401), "place_id"),
    (["images", 0, "camera"], lambda d: set_at(d, ["images", 0, "camera"], "x" * 401), "camera"),
    (["images", 0, "light"], lambda d: set_at(d, ["images", 0, "light"], "x" * 401), "light"),
    (["images", 0, "reason_new"], lambda d: set_at(d, ["images", 0, "reason_new"], "x" * 401), "reason_new"),
    (["images", 0, "on_screen_facts", 0], lambda d: set_at(d, ["images", 0, "on_screen_facts", 0], "x" * 401), "on_screen_facts"),
    (["images", 0, "references", "place"], lambda d: set_at(d, ["images", 0, "references", "place"], "x" * 401), "place"),
    (["images", 0, "references", "style_anchor"], lambda d: set_at(d, ["images", 0, "references", "style_anchor"], "x" * 401), "style_anchor"),
    (["images", 0, "references", "prop"], lambda d: set_at(d, ["images", 0, "references", "prop"], "x" * 401), "prop"),
    (["images", 0, "prop"], lambda d: set_at(d, ["images", 0, "prop"], "x" * 401), "prop"),
    (["images", 0, "prop_state"], lambda d: set_at(d, ["images", 0, "prop_state"], "x" * 401), "prop_state"),
    # references.characters items bounds
    (["images", 0, "references", "characters", 0], lambda d: set_at(d, ["images", 0, "references", "characters", 0], ""), "characters"),
    (["images", 0, "references", "characters", 0], lambda d: set_at(d, ["images", 0, "references", "characters", 0], "x" * 401), "characters"),
]


@pytest.mark.parametrize("path,mutate,field", SCHEMA_CASES)
def test_schema_errors(path, mutate, field):
    b = base()
    doc = mutate(b["docs"]["briefs"])
    errs = briefs.schema_errors(doc)
    assert any(field in e for e in errs), f"field {field} not in {errs}"


# ---- Semantic error cases ----
# Each case: (description, mutate_fn, expected_item_id)
# mutate_fn takes (docs, ctx) and returns mutated (docs, ctx)
SEMANTIC_CASES = [
    # adhyay mismatch
    ("adhyay mismatch", lambda docs, ctx: (set_at(docs, ["briefs", "adhyay"], 2), ctx), "briefs"),
    # duplicate image_id (same scene prefix)
    ("duplicate image_id", lambda docs, ctx: (
        append_at(docs, ["briefs", "images"], {
            "image_id": "s1_maharaj_seated",
            "scene_id": "S1",
            "shot_ids": ["S1-2"],
            "people": [{"name": "Maharaj", "position": "centre", "pose": "seated", "gaze": "forward"}],
            "place_id": "roadside",
            "prop": None,
            "prop_state": None,
            "camera": "medium",
            "light": "morning",
            "reason_new": "new",
            "on_screen_facts": ["x"],
            "references": {"characters": [], "place": "roadside", "style_anchor": "ref", "prop": None},
        }), ctx), "s1_maharaj_seated"),
    # image_id prefix mismatch (scene S1 -> s1_)
    ("image_id prefix mismatch", lambda docs, ctx: (set_at(docs, ["briefs", "images", 0, "image_id"], "s2_wrong"), ctx), "s2_wrong"),
    # shot_ids not in same scene
    ("shot_ids not in same scene", lambda docs, ctx: (set_at(docs, ["briefs", "images", 0, "shot_ids"], ["S2-1"]), ctx), "s1_maharaj_seated"),
    # shot_id does not exist
    ("shot_id does not exist", lambda docs, ctx: (set_at(docs, ["briefs", "images", 0, "shot_ids"], ["S9-9"]), ctx), "s1_maharaj_seated"),
    # people empty name
    ("people empty name", lambda docs, ctx: (set_at(docs, ["briefs", "images", 0, "people", 0, "name"], ""), ctx), "s1_maharaj_seated"),
    # on_screen_facts empty
    ("on_screen_facts empty", lambda docs, ctx: (set_at(docs, ["briefs", "images", 0, "on_screen_facts"], []), ctx), "s1_maharaj_seated"),
]


@pytest.mark.parametrize("desc,mutate,item_id", SEMANTIC_CASES)
def test_semantic_errors(desc, mutate, item_id):
    b = base()
    docs, ctx = mutate(b["docs"], b["ctx"])
    errs = briefs.validate(1, docs["briefs"], docs, ctx)
    # Assert item id only (spec does not quote specific phrases for these rules)
    assert any(item_id in e for e in errs), f"{desc}: item_id '{item_id}' not in {errs}"


def test_valid_base():
    b = base()
    assert briefs.schema_errors(b["docs"]["briefs"]) == []
    assert briefs.validate(1, b["docs"]["briefs"], b["docs"], b["ctx"]) == []


# ---- Regression tests for crashes on odd data ----
def test_validate_non_string_image_id_no_raise():
    """Non-string image_id should not raise TypeError during set membership."""
    b = base()
    docs = _deepcopy(b["docs"])
    docs["briefs"]["images"][0]["image_id"] = ["not", "a", "string"]
    errs = briefs.validate(1, docs["briefs"], docs, b["ctx"])
    assert isinstance(errs, list)
    assert not any("malformed structure" in e for e in errs)


def test_validate_non_string_scene_id_no_raise():
    """Non-string scene_id should not raise TypeError during regex/set operations."""
    b = base()
    docs = _deepcopy(b["docs"])
    docs["briefs"]["images"][0]["scene_id"] = ["S1"]
    errs = briefs.validate(1, docs["briefs"], docs, b["ctx"])
    assert isinstance(errs, list)
    assert not any("malformed structure" in e for e in errs)


def test_validate_non_string_shot_id_no_raise():
    """Non-string shot_id should not raise during dict lookup."""
    b = base()
    docs = _deepcopy(b["docs"])
    docs["briefs"]["images"][0]["shot_ids"] = [123]
    errs = briefs.validate(1, docs["briefs"], docs, b["ctx"])
    assert isinstance(errs, list)
    assert not any("malformed structure" in e for e in errs)


def test_validate_none_doc_no_raise():
    """None doc should not raise."""
    errs = briefs.validate(1, None, {}, {})
    assert isinstance(errs, list)
    assert not any("malformed structure" in e for e in errs)


def test_schema_errors_none_doc_no_raise():
    """None doc should not raise in schema_errors."""
    errs = briefs.schema_errors(None)
    assert isinstance(errs, list)


# ---- Regression tests for specific defects ----
def test_validate_scenes_with_list_scene_id_no_raise():
    """Scene entry with scene_id as list should not raise TypeError when building scene_ids set."""
    b = base()
    docs = _deepcopy(b["docs"])
    # Add a malformed scene with scene_id as list
    docs["scenes"]["scenes"].append({"scene_id": ["S1"], "section_kind": "story", "ovi_range": [1, 1], "goal": "x", "turn": {"ovi": 1, "text": "x"}, "line_ids": []})
    errs = briefs.validate(1, docs["briefs"], docs, b["ctx"])
    assert isinstance(errs, list)
    assert not any("malformed structure" in e for e in errs)


def test_validate_references_characters_empty_string_schema_error():
    """references.characters items must have minLength 1."""
    b = base()
    doc = _deepcopy(b["docs"]["briefs"])
    doc["images"][0]["references"]["characters"] = [""]
    errs = briefs.schema_errors(doc)
    assert any("characters" in e for e in errs)


def test_validate_references_characters_too_long_schema_error():
    """references.characters items must have maxLength 400."""
    b = base()
    doc = _deepcopy(b["docs"]["briefs"])
    doc["images"][0]["references"]["characters"] = ["x" * 401]
    errs = briefs.schema_errors(doc)
    assert any("characters" in e for e in errs)


def test_semantic_scene_not_exist_no_shot_refs():
    """Scene existence check should work even when brief has no shot_ids."""
    b = base()
    docs = _deepcopy(b["docs"])
    # Change to non-existent scene S99 with matching image_id prefix, and remove shot_ids
    docs["briefs"]["images"][0]["scene_id"] = "S99"
    docs["briefs"]["images"][0]["image_id"] = "s99_test"
    docs["briefs"]["images"][0]["shot_ids"] = []
    errs = briefs.validate(1, docs["briefs"], docs, b["ctx"])
    assert any("s99_test" in e for e in errs)


def test_validate_malformed_structure_returns_error():
    """validate should return error message on malformed structure instead of raising."""
    # Pass a doc that will cause TypeError in semantic validation
    doc = {"adhyay": 1, "images": [{"image_id": "s1_test", "scene_id": "S1", "shot_ids": ["S1-1"], "people": "not-a-list", "place_id": "x", "prop": None, "prop_state": None, "camera": "x", "light": "x", "reason_new": "x", "on_screen_facts": ["x"], "references": {"characters": [], "place": "x", "style_anchor": "x", "prop": None}}]}
    errs = briefs.validate(1, doc, {}, {})
    assert isinstance(errs, list)
    assert len(errs) >= 1

```

## ROUND 9 FINDINGS: TESTS ONLY. The module must be returned UNCHANGED, character for character (unless one of your new rows proves a real module defect against the SPEC; then fix the module and say so in no prose). Add data rows to the existing tables (schema-valid rows for each enum value; schema-invalid rows for each bound/minLength) so that removing that schema rule fails a test. Keep every existing test and every assertion 'not any("malformed structure" in e ...)' unchanged. Only the items listed for YOUR unit 'briefs' in the report below apply; if there are none for 'briefs', return both files unchanged. Return BOTH complete FILE blocks.
### Haiku round 9 (use only the section for briefs)
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
