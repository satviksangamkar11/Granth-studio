# FIX CALL: return BOTH files in full: `scripts/pipeline/stage1/briefs.py` and `tests/test_stage1_briefs.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
........................................................................ [ 77%]
.....................                                                    [100%]
93 passed in 0.12s

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
    # scene does not exist (use consistent image_id prefix for non-existent scene S99)
    ("scene does not exist", lambda docs, ctx: (
        set_at(
            set_at(docs, ["briefs", "images", 0, "scene_id"], "S99"),
            ["briefs", "images", 0, "image_id"],
            "s99_test"
        ),
        ctx
    ), "s99_test"),
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
    assert any("malformed structure" in e for e in errs)

```

## ROUND 5 REVIEW FINDINGS (apply what the SPEC supports; keep every existing passing test passing; tests isolated, assert the offending id, no wording the spec does not quote). Return BOTH FILE blocks complete.
Specific: tests/test_stage1_briefs.py around line 423 asserts the wording 'malformed structure', which the spec does not quote; assert only that the result is a list with at least one error and that no exception is raised.
### Codex round 5
## Verdict: FIX FIRST

### story_map

none

### coverage

none

### scenes

none

### shots

1. **Medium — [shots.py:133](</D:/aai work/granthstudio/scripts/pipeline/stage1/shots.py:133>):** Consecutiveness is grouped by the scene prefix in `shot_id`, rather than by the shot’s `scene_id`. Swapping the scene assignments of baseline shots `S1-1` and `S2-1`, with their ovis and lines adjusted to match the assigned scenes, returns `[]` even though the shot numbers assigned to each scene are not consecutive from 1. Group numbers by `scene_id` and reject a shot ID whose prefix does not match its assigned scene; add an isolated test.

### briefs

none

### looks

none

### voices

1. **Low — [test_stage1_voices.py:234](</D:/aai work/granthstudio/tests/test_stage1_voices.py:234>):** The new mixed `RECURRING`/`NEW_PROPOSED` duplicate test also shares `gajanan` with `gajanan_maharaj`. It therefore passes on the collateral `other_char: voice key shared with another character` error if recurring-duplicate detection is removed. Use the same narrator voice for both `other_char` entries, or otherwise isolate the duplicate rule.

### sounds

none

### questions

none

The Round 4 mixed-status voice behavior is fixed, but its new test is not isolated. The other reported Round 4 changes are present; I reproduced the scene duplicate case and inspected the revised shots, briefs, and looks checks.

The workspace is read-only, so I could not write a report file. I reproduced the findings in memory with a stub for `jsonschema`; I could not run the suite or independently verify schema behavior because the available Python lacks `jsonschema` and the project virtual environment could not start. The remaining units were not exhaustively verified.### Haiku round 5
# Stage 1 unit modules: Round 5 review (read-only)

Scope: `scripts/pipeline/stage1/{story_map,coverage,scenes,shots,briefs,looks,voices,sounds,questions}.py`, `tests/test_stage1_<unit>.py`, against `docs/pilot/nemotron_specs/unit_<unit>.md`, `stage1_base.json`, `STAGE1_RULES.md`.

Evidence:
- `uv run pytest -q tests/test_stage1_*.py` (nine files): **424 passed**.
- Mutation check: 54 single-rule mutations were applied to copies of the modules in the scratchpad (project files untouched) and each unit's test file was run against them. 53 were killed. One survived: the voices rule "a character already RECURRING must not be listed twice" (see voices 2 and 3).
- Round 4 findings were reproduced in memory where applicable (coverage `covered_by "²"`, briefs missing-scene message, voices mixed-status cast).
- No print, env, key or secret handling was found in any module or test.
- Not counted (out of the five classes): `coverage.validate` and `scenes.validate` raise TypeError when a ctx list is None (e.g. `chapter_ovis: None`); ctx is not document data. Verified for coverage.
- Not counted, observation: `scenes.py:148-149` expands `range(lo, hi+1)` for every scene, and `scenes.py:216-218` emits one message per covered ovi outside the chapter. `ovi_range [1, 5000000]` took 1.0 s and produced 4,999,997 messages. No raise was reproduced; scenes.validate has no catch-all.
- Not counted, observation: in briefs, a non-object entry in `people` raises inside the try block, so the whole document returns only `briefs: malformed structure` and all other semantic errors are hidden.

## Verdict: FIX FIRST

---

## Round 4 status

| Unit | Round 4 finding | Status (Round 5) |
|---|---|---|
| coverage | `covered_by "²"` raised ValueError | FIXED (reproduced: returns the covered_by error, no raise) |
| scenes | duplicate-scene test passes without duplicate detection | FIXED (mutation of duplicate-id check now fails the test) |
| shots | class enum row only exercises null branch | FIXED (`test_need_new_class_enum` uses NEED_NEW with schema_errors) |
| shots | test asserts "not in scene" (not quoted in spec) | FIXED (no such assertion remains in the test file) |
| shots | catch-all assertions only check for a list | FIXED (odd-data tests assert no "malformed structure") |
| briefs | missing-scene message says "scene exists" | FIXED (reproduced: `s99_x: scene S99 does not exist`) |
| looks | no odd-data test | FIXED (`test_validate_odd_doc_no_raise`, ODD_DOCS list) |
| voices | RECURRING + NEW_PROPOSED not flagged when not speaking | Code FIXED (reproduced: `gajanan_maharaj: recurring character listed twice`). The test for it is not isolated: see voices 2 and 3 |

---

## story_map

none.

## coverage

none.

## scenes

none.

## shots

none.

## briefs

1. `tests/test_stage1_briefs.py:423` (class 4): `assert any("malformed structure" in e for e in errs)` asserts wording the spec does not quote (grep of `unit_briefs.md` finds no "malformed"). Fix: `assert isinstance(errs, list) and len(errs) >= 1`.

## looks

none.

## voices

1. `tests/test_stage1_voices.py:209-214` (class 3): the row labelled "distinct voice_keys to isolate rule" reuses the keys `narrator` and `gajanan`, so `other_char` also triggers "voice key shared with another character" (`voices.py:145`). Verified: with `voices.py:113-114` removed, this row still passes on the shared-key message (the row asserts keyword `other_char`). Fix: give `other_char` its own key. Verified fix: add `"other": "ZZZZZZZZZZ"` to a copy of `ctx["saved_voices"]`, and use `voice_key "other"`, `voice_id "ZZZZZZZZZZ"` for both `other_char` entries. The original code then returns exactly `["other_char: recurring character listed twice"]`, and with the rule removed it returns `[]`, so the test becomes isolated. Because the row's keyword is in the tuple, this needs a standalone test function, not a new tuple row.
2. `tests/test_stage1_voices.py:235-240` (class 3): the Round 4 test for "non-speaking RECURRING + NEW_PROPOSED" has the same collateral. With the rule removed it still returns `other_char: voice key shared with another character`. Fix as in item 1 (distinct key `other` for both `other_char` entries, ctx `saved_voices` extended), and assert that the only message is `other_char: recurring character listed twice`.

## sounds

none.

## questions

none.

---

## Defects per unit (Round 5)

| Unit | Defects |
|---|---|
| story_map | 0 |
| coverage | 0 |
| scenes | 0 |
| shots | 0 |
| briefs | 1 |
| looks | 0 |
| voices | 2 |
| sounds | 0 |
| questions | 0 |
| **Total** | **3** |
