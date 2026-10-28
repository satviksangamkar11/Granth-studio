# GLM 5.3 REVIEW CALL for Stage 1 unit `briefs`. Write ONE markdown file: `reviews/glm_review_briefs.md` (the ONLY file; no code files).
You are the senior reviewer of this unit. Inputs below: the UNIT SPEC (the only authority), the current MODULE, the current TESTS, and the real pytest output. Review both files against the spec and produce CORRECTION INSTRUCTIONS for the coder, in this exact structure:
# GLM review: briefs
## Verdict: READY | FIX FIRST   (READY only if every pytest test passes AND every rule below is covered AND no defect is listed)
## Spec rules: for each schema rule, enum, conditional (if/then), required field, extra-key rule and each semantic rule of the unit spec, one line: `rule | module implements it (yes/no, line) | isolated failing test exists (yes/no, test name) | notes`.
## Defects in the MODULE: numbered, each with the exact change to make (function, what to add/remove) or `none`.
## Defects in the TESTS: numbered, each with the test name and exact change (no-op mutation, collateral failure, wording not quoted in the spec, wrong schema/semantic level, missing row, assertion that can never fail) or `none`.
## Failing tests: for each failing pytest test say whether the TEST or the MODULE is wrong according to the spec and give the fix.
Be precise and short; only real, verified defects; do not rewrite files.

## PYTEST OUTPUT
```
.......................................................                  [100%]
55 passed in 0.07s

```

## UNIT SPEC (authority)
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



## MODULE scripts/pipeline/stage1/briefs.py
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
                                "name": {"type": "string", "minLength": 1},
                                "position": {"type": "string"},
                                "pose": {"type": "string"},
                                "gaze": {"type": "string"},
                            },
                        },
                    },
                    "place_id": {"type": "string"},
                    "prop": {"type": ["string", "null"], "maxLength": 400},
                    "prop_state": {"type": ["string", "null"], "maxLength": 400},
                    "camera": {"type": "string", "minLength": 1},
                    "light": {"type": "string", "minLength": 1},
                    "reason_new": {"type": "string", "minLength": 1},
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
                            "place": {"type": "string"},
                            "style_anchor": {"type": "string"},
                            "prop": {"type": ["string", "null"]},
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
            if sid and scid:
                shot_map[sid] = scid

    seen_image_ids: set[str] = set()

    for img in images:
        if not isinstance(img, dict):
            continue
        img_id = img.get("image_id")
        if not img_id:
            continue

        if img_id in seen_image_ids:
            messages.append(f"{img_id}: unique with scene prefix")
        seen_image_ids.add(img_id)

        scene_id = img.get("scene_id")
        if scene_id:
            m = re.match(r"^S([0-9]{1,2})$", scene_id)
            if m:
                expected_prefix = f"s{int(m.group(1))}_"
                if not img_id.startswith(expected_prefix):
                    messages.append(f"{img_id}: unique with scene prefix")

        if scene_id and scene_id not in scene_ids:
            messages.append(f"{img_id}: scene exists")

        shot_ids = img.get("shot_ids", [])
        if isinstance(shot_ids, list):
            for sid in shot_ids:
                if sid not in shot_map:
                    messages.append(f"{img_id}: shot_ids exist and belong to the same scene")
                elif shot_map[sid] != scene_id:
                    messages.append(f"{img_id}: shot_ids exist and belong to the same scene")

        people = img.get("people", [])
        if isinstance(people, list):
            for i, p in enumerate(people):
                if isinstance(p, dict):
                    name = p.get("name")
                    if not name or not isinstance(name, str) or name.strip() == "":
                        messages.append(f"{img_id}: no empty name")

        on_screen_facts = img.get("on_screen_facts", [])
        if not isinstance(on_screen_facts, list) or len(on_screen_facts) == 0:
            messages.append(f"{img_id}: non-empty")

    return messages + notes

```

## TESTS tests/test_stage1_briefs.py
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
]


@pytest.mark.parametrize("path,mutate,field", SCHEMA_CASES)
def test_schema_errors(path, mutate, field):
    b = base()
    doc = mutate(b["docs"]["briefs"])
    errs = briefs.schema_errors(doc)
    assert any(field in e for e in errs), f"field {field} not in {errs}"


# ---- Semantic error cases ----
# Each case: (description, mutate_fn, expected_keyword_in_message, expected_item_id)
# mutate_fn takes (docs, ctx) and returns mutated (docs, ctx)
SEMANTIC_CASES = [
    # adhyay mismatch
    ("adhyay mismatch", lambda docs, ctx: (set_at(docs, ["briefs", "adhyay"], 2), ctx), "adhyay", "briefs"),
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
        }), ctx), "unique with scene prefix", "s1_maharaj_seated"),
    # image_id prefix mismatch (scene S1 -> s1_)
    ("image_id prefix mismatch", lambda docs, ctx: (set_at(docs, ["briefs", "images", 0, "image_id"], "s2_wrong"), ctx), "unique with scene prefix", "s2_wrong"),
    # scene does not exist (use consistent image_id prefix for non-existent scene S99)
    ("scene does not exist", lambda docs, ctx: (set_at(set_at(docs, ["briefs", "images", 0, "scene_id"], "S99"), ["briefs", "images", 0, "image_id"], "s99_test"), ctx), "scene exists", "s99_test"),
    # shot_ids not in same scene
    ("shot_ids not in same scene", lambda docs, ctx: (set_at(docs, ["briefs", "images", 0, "shot_ids"], ["S2-1"]), ctx), "shot_ids exist and belong to the same scene", "s1_maharaj_seated"),
    # shot_id does not exist
    ("shot_id does not exist", lambda docs, ctx: (set_at(docs, ["briefs", "images", 0, "shot_ids"], ["S9-9"]), ctx), "shot_ids exist and belong to the same scene", "s1_maharaj_seated"),
    # people empty name
    ("people empty name", lambda docs, ctx: (set_at(docs, ["briefs", "images", 0, "people", 0, "name"], ""), ctx), "no empty name", "s1_maharaj_seated"),
    # on_screen_facts empty
    ("on_screen_facts empty", lambda docs, ctx: (set_at(docs, ["briefs", "images", 0, "on_screen_facts"], []), ctx), "non-empty", "s1_maharaj_seated"),
]


@pytest.mark.parametrize("desc,mutate,keyword,item_id", SEMANTIC_CASES)
def test_semantic_errors(desc, mutate, keyword, item_id):
    b = base()
    docs, ctx = mutate(b["docs"], b["ctx"])
    errs = briefs.validate(1, docs["briefs"], docs, ctx)
    # Assert item id and quoted keyword from spec
    assert any(item_id in e for e in errs), f"{desc}: item_id '{item_id}' not in {errs}"
    assert any(keyword in e for e in errs), f"{desc}: keyword '{keyword}' not in {errs}"


def test_valid_base():
    b = base()
    assert briefs.schema_errors(b["docs"]["briefs"]) == []
    assert briefs.validate(1, b["docs"]["briefs"], b["docs"], b["ctx"]) == []

```
