# FIX CALL: return BOTH files in full: `scripts/pipeline/stage1/briefs.py` and `tests/test_stage1_briefs.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
........................................................................ [ 83%]
..............                                                           [100%]
86 passed in 0.10s

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
                            "characters": {"type": "array", "items": {"type": "string"}},
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


def validate(adhyay: int, doc: Any, docs: dict[str, Any], ctx: dict[str, Any]) -> list[str]:
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
    scene_ids = {s.get("scene_id") for s in scenes_list if isinstance(s, dict)}

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
            messages.append(f"{img_id}: scene exists")

        shot_ids = img.get("shot_ids", [])
        if isinstance(shot_ids, list):
            for sid in shot_ids:
                if not isinstance(sid, str) or sid not in shot_map:
                    messages.append(f"{img_id}: shot_ids exist and belong to the same scene")
                elif shot_map[sid] != scene_id:
                    messages.append(f"{img_id}: shot_ids exist and belong to the same scene")

        people = img.get("people", [])
        if isinstance(people, list):
            for i, p in enumerate(people):
                if isinstance(p, dict):
                    name = p.get("name")
                    if not isinstance(name, str) or name.strip() == "":
                        messages.append(f"{img_id}: no empty name")

        on_screen_facts = img.get("on_screen_facts", [])
        if not isinstance(on_screen_facts, list) or len(on_screen_facts) == 0:
            messages.append(f"{img_id}: non-empty")

    return messages + notes

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
    # scene does not exist (use consistent image_id prefix for non-existent scene S99)
    ("scene does not exist", lambda docs, ctx: (set_at(set_at(docs, ["briefs", "images", 0, "scene_id"], "S99"), ["briefs", "images", 0, "image_id"], "s99_test"), ctx), "s99_test"),
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


def test_validate_non_string_scene_id_no_raise():
    """Non-string scene_id should not raise TypeError during regex/set operations."""
    b = base()
    docs = _deepcopy(b["docs"])
    docs["briefs"]["images"][0]["scene_id"] = ["S1"]
    errs = briefs.validate(1, docs["briefs"], docs, b["ctx"])
    assert isinstance(errs, list)


def test_validate_non_string_shot_id_no_raise():
    """Non-string shot_id should not raise during dict lookup."""
    b = base()
    docs = _deepcopy(b["docs"])
    docs["briefs"]["images"][0]["shot_ids"] = [123]
    errs = briefs.validate(1, docs["briefs"], docs, b["ctx"])
    assert isinstance(errs, list)


def test_validate_none_doc_no_raise():
    """None doc should not raise."""
    errs = briefs.validate(1, None, {}, {})
    assert isinstance(errs, list)


def test_schema_errors_none_doc_no_raise():
    """None doc should not raise in schema_errors."""
    errs = briefs.schema_errors(None)
    assert isinstance(errs, list)

```

## ROUND 2 REVIEW FINDINGS (apply what the SPEC supports; Codex reproduced its items, Haiku's are unverified).
MANDATORY ROOT-CAUSE FIX: rename the current semantic body to a private helper and make `validate(adhyay, doc, docs, ctx)` call it inside `try/except (TypeError, AttributeError, KeyError, ValueError, IndexError)`; on such an exception return `["briefs: malformed structure"]` (the spec says validate must never raise on odd data). ALSO fix each specific defect below at its source (type-check lists/ids before iterating or building sets), add one isolated regression test per defect, make weak tests isolated and assert ids instead of unquoted wording. All existing tests must still pass.
### Codex round 2
## Verdict: FIX FIRST

### story_map

1. **High —** [story_map.py:85](</D:/aai work/granthstudio/scripts/pipeline/stage1/story_map.py:85>): `ovi_types: null`, `events: null`, or an event with `key_ovis: null` raises `TypeError`. Check each value is a list before iterating and return errors for malformed values.

### coverage

None.

### scenes

1. **Low —** [test_stage1_scenes.py:177](</D:/aai work/granthstudio/tests/test_stage1_scenes.py:177>): The duplicate-scene test asserts `duplicate scene id`, which the spec does not quote. Use an isolated duplicate case and assert its scene ID.

### shots

1. **High —** [shots.py:168](</D:/aai work/granthstudio/scripts/pipeline/stage1/shots.py:168>): `ovi_ids: null` or `beat_line_ids: null` raises `TypeError`. Guard both arrays before iteration.
2. **High —** [shots.py:183](</D:/aai work/granthstudio/scripts/pipeline/stage1/shots.py:183>): A beat line assigned to the wrong scene is still counted as covered. With `S2-L1` on an S1 shot and no S2 shot covering it, validation reports the wrong assignment but misses `S2-L1: line is in no shot beat`. Count coverage only for lines belonging to that shot’s scene.
3. **Low —** [test_stage1_shots.py:170](</D:/aai work/granthstudio/tests/test_stage1_shots.py:170>): The invalid-class row fails because the existing preset forbids an object, even without the class enum. Set the preset to `NEED_NEW` for this row.
4. **Low —** [test_stage1_shots.py:268](</D:/aai work/granthstudio/tests/test_stage1_shots.py:268>): The test asserts the unquoted wording `scene has no shots`. Isolate the missing-scene-shots rule and assert the scene ID.

### briefs

1. **High —** [briefs.py:118](</D:/aai work/granthstudio/scripts/pipeline/stage1/briefs.py:118>): A referenced scene with `scene_id: []` raises `TypeError` while building the set. Include only string scene IDs and guard malformed referenced arrays.
2. **Low —** [test_stage1_briefs.py:295](</D:/aai work/granthstudio/tests/test_stage1_briefs.py:295>): The missing-scene case also leaves a shot belonging to another scene, so it passes if the scene-existence check is removed. Give the brief no shot references for this test.

### looks

None.

### voices

1. **High —** [voices.py:51](</D:/aai work/granthstudio/scripts/pipeline/stage1/voices.py:51>): `validate(1, None, docs, ctx)` raises `AttributeError`. Check that `doc` is a dictionary before calling `.get`.
2. **High —** [voices.py:111](</D:/aai work/granthstudio/scripts/pipeline/stage1/voices.py:111>): The validator rejects duplicate `NEW_PROPOSED` entries for a character outside `speaking_characters`, although the spec only requires exactly one entry for speaking characters and prohibits duplicate recurring characters. Restrict duplicate checks to those rules.
3. **High —** [voices.py:147](</D:/aai work/granthstudio/scripts/pipeline/stage1/voices.py:147>): Two entries for the *same* non-narrator are treated as two characters sharing a voice. Deduplicate character IDs before checking sharing.
4. **Low —** [test_stage1_voices.py:208](</D:/aai work/granthstudio/tests/test_stage1_voices.py:208>): The recurring non-speaker duplicate case also triggers the same-character voice-sharing error, so it does not isolate the recurring-duplicate rule. Use distinct voice keys for the duplicate entries and keep both keys valid in context.
5. **Low —** [test_stage1_voices.py:215](</D:/aai work/granthstudio/tests/test_stage1_voices.py:215>): The narrator-plus-two-characters case uses an unsaved `shared` key, so the asserted character ID also appears in a saved-cast error. Use a saved key and matching voice ID.

### sounds

1. **High —** [sounds.py:109](</D:/aai work/granthstudio/scripts/pipeline/stage1/sounds.py:109>): A referenced scene with `line_ids: [[]]` raises `TypeError` during set construction. Filter for string line IDs before constructing the set.

### questions

None.

The report could not be written as a file because the workspace is read-only. I reproduced the listed semantic failures in memory with a `jsonschema` stub; the virtual-environment interpreter was denied execution, so I could not independently rerun the suite or reproduce every Round 1 schema finding.### Haiku round 2
# Stage 1 unit modules: Round 2 review (read-only)

Scope: `scripts/pipeline/stage1/{story_map,coverage,scenes,shots,briefs,looks,voices,sounds,questions}.py`, `tests/test_stage1_<unit>.py`, against `docs/pilot/nemotron_specs/unit_<unit>.md`, `stage1_base.json`, `STAGE1_RULES.md`.

Evidence: `uv run pytest -q --tb=short tests/test_stage1_*.py` gives **400 passed** (the brief states 415; the count here is what the run printed). Every defect below was reproduced by calling the module in memory with a small input (no project file written, no network). No print, env, key or secret handling was found in any module or test.

## Verdict: FIX FIRST

---

## Round 1 findings: status

| Unit | Round 1 finding | Status |
|---|---|---|
| story_map | `ovi_types: [null]` raises | FIXED (returns "ovi N is untyped") |
| story_map | tests assert `lo > hi`, `key_ovi`, `outside` wording | FIXED (rows assert "E1") |
| story_map | `key_ovis` below range branch untested | FIXED (row `key_ovis: [0]` present) |
| coverage | `ovis: [null]` raises | FIXED. Note: Round 1 said "Tests: none"; `tests/test_stage1_coverage.py` exists (243 lines) |
| scenes | out-of-order check lost after unknown line id | FIXED |
| scenes | `ovi_range: ["a", 2]` turn check raises TypeError | FIXED |
| scenes | unhashable `scene_id` / `line_id` raises | FIXED |
| scenes | story `teaching_treatment: "none"` rejected by schema | FIXED (schema `const: none`; positive test present) |
| scenes | no isolated test for forbidden story treatment | FIXED (`test_schema_story_scene_forbidden_treatment`) |
| scenes | duplicate-scene test passes through collateral match | FIXED (now asserts "duplicate scene id"; wording see defect S1) |
| shots | `shots: [null]` raises | FIXED |
| shots | `preset` accepts any string | FIXED (pattern `^([0-9]{2}_[a-z0-9_]+\|NEED_NEW)$`) |
| shots | class-enum row uses non-NEED_NEW preset | STILL OPEN (defect H4) |
| shots | scene-has-shots test collateral "S2" | FIXED (asserts "scene has no shots") |
| shots | "consecutive" wording asserted | FIXED (asserts "S1"; the test fails if the rule is removed) |
| shots | preset check skipped when scene missing | FIXED (verified: "S1-1: unknown preset bogus" is reported) |
| briefs | non-string `image_id` / `shot_id` / `scene_id` raises | PARTLY: `image_id`/`shot_id` FIXED; `scene_id` in scenes still raises (defect B1) |
| briefs | `prop`/`prop_state` empty accepted; text bounds missing | FIXED for listed fields; `references.characters` items still unbounded (defect B2) |
| briefs | asserted wording not quoted by spec | FIXED (asserts item id) |
| voices | `cast: [1]` / `cast: None` / non-dict entries raise | FIXED |
| voices | two NEW_PROPOSED entries not flagged; recurring duplicate outside speaking set | FIXED (verified) |
| voices | narrator suppresses error for two other sharers | FIXED (verified: both `x` and `y` flagged) |
| voices | required fields never tested by deletion | FIXED (DELETE rows present) |
| voices | asserted wording not quoted | FIXED (asserts item id) |
| sounds | cue without `sound_id` raises AttributeError | FIXED (verified) |
| sounds | asserted wording not quoted | PARTLY: `cue[0]` used in the main table; guard-message asserts remain (defect SO1) |
| questions | unhashable `id` / `scene_id` raises | FIXED (verified) |
| questions | odd-data test lacks unhashable cases | FIXED (cases present) |
| looks | none | n/a |

---

## story_map

1. `scripts/pipeline/stage1/story_map.py:83-85`: `ovi_types` is not type-checked. `{"ovi_types": None}` raises `TypeError: 'NoneType' object is not iterable` (verified). Fix: `ovi_types = doc.get("ovi_types"); if not isinstance(ovi_types, list): ovi_types = []`.
2. `scripts/pipeline/stage1/story_map.py:106-107`: `events` is not type-checked. `{"events": 5}` raises `TypeError` (verified). Fix: `events = doc.get("events"); if not isinstance(events, list): events = []`.
3. `scripts/pipeline/stage1/story_map.py:112, 122`: `key_ovis` is not type-checked. `key_ovis: 5` raises `TypeError` (verified). Fix: `key_ovis = event.get("key_ovis"); if not isinstance(key_ovis, list): key_ovis = []`.
4. `tests/test_stage1_story_map.py:163` (class 4): the odd-data row asserts `"not an object"`, which the spec does not quote. Fix: assert the item id, for example `["doc"]`, instead of the wording.

## coverage

none.

## scenes

1. `tests/test_stage1_scenes.py:177` (class 4): the duplicate-id test asserts `"duplicate scene id"`, which the spec does not quote. Fix: keep the test but assert the item id only, e.g. `any(e.startswith("S1:") for e in errs)`, and assert that the message set differs from the valid baseline. The collateral-match problem is fixed, so the wording is the only remaining issue.
2. `tests/test_stage1_scenes.py:239` (class 4): asserts `"order"`, which the spec does not quote ("in script order" is rule prose, not a message). Fix: `assert any("S1" in e for e in errs)`.

## shots

1. `scripts/pipeline/stage1/shots.py:168` (class 2): `shot.get("ovi_ids", [])` is iterated without a type check. A shot with `ovi_ids: 5` inside a valid scene raises `TypeError` (verified). Fix: `ovi_ids = shot.get("ovi_ids"); if isinstance(ovi_ids, list): for ovi in ovi_ids: ...`.
2. `scripts/pipeline/stage1/shots.py:179` (class 2): `beat_line_ids` iterated without a type check. `beat_line_ids: None` raises `TypeError` (verified). Fix: `beat_line_ids = shot.get("beat_line_ids"); if not isinstance(beat_line_ids, list): beat_line_ids = []`.
3. `scripts/pipeline/stage1/shots.py:205` (class 2): scene `line_ids` iterated in the "line is in no shot beat" loop with no type check. A scene with `line_ids: 5` raises `TypeError` (verified). Fix: `line_ids = scene.get("line_ids"); if not isinstance(line_ids, list): line_ids = []` before the loop.
4. `tests/test_stage1_shots.py:170` (class 3, Round 1 still open): the row `{"reason": "x", "class": "bad_class"}` sits in a table where `preset` is the base value `01_establishing_shot`. The failure comes from the `else` branch ("is not of type 'null'", verified), so the class enum is never exercised by this row. Fix: set `preset` to `"NEED_NEW"` for this row, as `test_need_new_class_enum` already does, and check the message names `class`.
5. `tests/test_stage1_shots.py:268` (class 4): asserts `"scene has no shots"`, which the spec does not quote. Fix: assert `"S2"` in the error and that the `has no shots` item is the only one for S2, or use the item id only.

## briefs

1. `scripts/pipeline/stage1/briefs.py:118` (class 2, Round 1 still open): `scene_ids = {s.get("scene_id") ...}` builds a set from unvalidated values. A scenes entry with `scene_id: ["S1"]` raises `TypeError: unhashable type: 'list'` (verified). Fix: `scene_ids = {sid for s in scenes_list if isinstance(s, dict) for sid in [s.get("scene_id")] if isinstance(sid, str)}`. Add a regression case.
2. `scripts/pipeline/stage1/briefs.py:78` (class 1): the spec's `references.characters` is `[text...]` (text = 1..400 chars). The schema gives items `{"type": "string"}` with no bounds, so `references.characters: [""]` produces no schema error (verified). Fix: `"characters": {"type": "array", "items": {"type": "string", "minLength": 1, "maxLength": 400}}`. Add a schema test.

## looks

none.

## voices

1. `scripts/pipeline/stage1/voices.py:51` and `:60` (class 2, new): `validate` calls `doc.get` without checking `doc`. `validate(1, [1], ...)` and `validate(1, None, ...)` raise `AttributeError` (verified). Fix: first line of `validate`: `if not isinstance(doc, dict): return ["voices doc: document must be an object"]`.
2. `scripts/pipeline/stage1/voices.py:147` (class 1, false positive, new): when one character is listed twice with the same non-narrator `voice_key`, the code reports `"<char>: voice key shared with another character"` once per entry. Repro: entries `extra_char`, `extra_char` both with key `gajanan` produce two "shared" messages for `extra_char` (verified). The spec's rule is about two different characters. Fix: `non_narrator_chars = sorted({c for c in chars if c != "narrator"})` so repeated entries of one character count once.

## sounds

1. `tests/test_stage1_sounds.py:229, 241, 247, 253, 259` (class 4, partly Round 1 open): the guard and rule asserts include wording the spec does not quote ("document must be an object", "cue must be an object", "scene does not exist", "anchor_line_id must be a string", "sound_id must be a string"). Fix: assert `"cue[0]"` (or `"sounds"` for the document row) only, as the spec requires.

## questions

none.

---

## Defects per unit (Round 2)

| Unit | Defects |
|---|---|
| story_map | 4 |
| coverage | 0 |
| scenes | 2 |
| shots | 5 |
| briefs | 2 |
| looks | 0 |
| voices | 2 |
| sounds | 1 |
| questions | 0 |
| **Total** | **16** |

Notes:
- Three of the new raises (story_map 1-3, shots 1-3, briefs 1, voices 1) would have been caught by the odd-data tests the spec asks for. Those tests should gain the cases listed above when the fixes land.
- The pytest count printed is 400 (the brief says 415). Confirm which run the coder counted.
