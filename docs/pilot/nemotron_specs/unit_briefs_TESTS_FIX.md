# FIX CALL for the test file `tests/test_stage1_briefs.py` (write ONLY that file, one FILE block). Two independent reviewers (Codex, Haiku) found real defects in your previous version (shown below). Repair ALL of them. The unit spec, BASE data and clarifications follow. HARD RULES that the previous attempts broke:
1. Write ONE robust helper set at the top and use it everywhere: `get_parent(doc, path)` that walks a path list where an int part indexes a list and a str part indexes a dict; `set_at(base, path, value)`, `delete_at(base, path)`, `append_at(base, path, value)` (all work on a deep copy and handle list indexes and dict keys, never index a list with a string). EVERY mutation must be proven to change the document: the helper asserts `mutated != base` (a no-op mutation fails loudly). Never address a list element that does not exist in BASE (append instead).
2. Each row changes exactly ONE thing and leaves everything else valid; contexts (script lines, saved voices, presets) stay complete unless the row is about that context. Each row asserts the item id AND only the keyword the spec QUOTES; for rules with no quoted phrase assert only the item id (never invented words like unique, outside, prefix, shared, empty, mismatch, not exist).
3. Positive rows assert `[]` exactly. A "twice/duplicate" rule needs a real duplicate (append a second entry). A rule that is schema-level in the spec is tested through `schema_errors`; a rule the spec makes semantic is tested ONLY through `validate` (never expect jsonschema to reject reversed ranges or empty names unless the spec's schema says so). jsonschema reports required/additionalProperties errors at the PARENT path: assert the offending field name appears in the message, never a child path.
4. Required-field rows DELETE each required field from a deep copy (root fields and nested objects); extra-key rows ADD one unknown key to an otherwise valid object at the root and at every nested object; every enum has one invalid-value row.
5. `validate(adhyay, doc, docs, ctx)`: `docs` is the dict of ALL nine documents (use only the ones the unit spec lists; pass {} for absent ones) and `ctx` is separate (never `docs["ctx"]`).
6. ids are strings and ovis are integers (covered_by uses an integer ovi or a line id string).
7. Keep it compact (<= 170 lines), synthetic only, loading the module by path with importlib as the unit spec says.
Reply with exactly one FILE block: FILE: tests/test_stage1_briefs.py

## CODEX FINDINGS FOR THIS UNIT
- **briefs — Medium:** `test_schema_errors` **175** requires schema rejection of empty person names, which the spec assigns to semantic validation. Extra-key rows **190–192** replace entire objects, simultaneously deleting required fields; add the extra key to otherwise valid objects. Root required-field deletions and a root extra-key row are absent. `test_semantic_errors` **214–239** requires unmandated wording instead of item IDs. Scene mutation **219** also breaks the image’s scene prefix, preventing isolated scene-existence coverage.

## HAIKU FINDINGS FOR THIS UNIT
(4) Line 214 asserts "unique" and line 217 "prefix"; neither is quoted in the spec. (5) Lines 190-192 replace whole objects with {"extra": 1} instead of adding a key, so they do not isolate the extra-key rule. No deletion rows for root "images" or "adhyay". (3) The "image ids unique" rule has no isolated failing row (the duplicate case in the table is valid input).

## UNIT SPEC (binding)
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



## YOUR PREVIOUS tests/test_stage1_briefs.py (repair it)
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


def base():
    return {"docs": copy.deepcopy(BASE_DOCS), "ctx": copy.deepcopy(BASE_CTX)}


def mutate(obj, path, value):
    """Set or delete a single item at dot/path. Returns mutated obj."""
    parts = path.split(".")
    target = obj
    for p in parts[:-1]:
        if p.isdigit():
            target = target[int(p)]
        else:
            target = target[p]
    last = parts[-1]
    if value is ...:
        if isinstance(target, list):
            del target[int(last)]
        else:
            del target[last]
    else:
        if last.isdigit():
            target[int(last)] = value
        else:
            target[last] = value
    return obj


SCHEMA_CASES = [
    # required fields
    ("images.0.image_id", ..., "image_id"),
    ("images.0.scene_id", ..., "scene_id"),
    ("images.0.shot_ids", ..., "shot_ids"),
    ("images.0.people", ..., "people"),
    ("images.0.place_id", ..., "place_id"),
    ("images.0.prop", ..., "prop"),
    ("images.0.prop_state", ..., "prop_state"),
    ("images.0.camera", ..., "camera"),
    ("images.0.light", ..., "light"),
    ("images.0.reason_new", ..., "reason_new"),
    ("images.0.on_screen_facts", ..., "on_screen_facts"),
    ("images.0.references", ..., "references"),
    # people required fields
    ("images.0.people.0.name", ..., "name"),
    ("images.0.people.0.position", ..., "position"),
    ("images.0.people.0.pose", ..., "pose"),
    ("images.0.people.0.gaze", ..., "gaze"),
    # references required fields
    ("images.0.references.characters", ..., "characters"),
    ("images.0.references.place", ..., "place"),
    ("images.0.references.style_anchor", ..., "style_anchor"),
    ("images.0.references.prop", ..., "prop"),
    # type/format violations
    ("images.0.image_id", "S1_bad", "image_id"),
    ("images.0.scene_id", "X1", "scene_id"),
    ("images.0.shot_ids", "not-array", "shot_ids"),
    ("images.0.shot_ids.0", "bad-shot", "shot_ids"),
    ("images.0.people", "not-array", "people"),
    ("images.0.people.0", "not-object", "people"),
    ("images.0.people.0.name", "", "name"),
    ("images.0.place_id", 123, "place_id"),
    ("images.0.prop", 123, "prop"),
    ("images.0.prop_state", 123, "prop_state"),
    ("images.0.camera", "", "camera"),
    ("images.0.light", "", "light"),
    ("images.0.reason_new", "", "reason_new"),
    ("images.0.on_screen_facts", "not-array", "on_screen_facts"),
    ("images.0.on_screen_facts.0", "", "on_screen_facts"),
    ("images.0.references", "not-object", "references"),
    ("images.0.references.characters", "not-array", "characters"),
    ("images.0.references.place", 123, "place"),
    ("images.0.references.style_anchor", 123, "style_anchor"),
    ("images.0.references.prop", 123, "prop"),
    # extra keys on nested objects
    ("images.0", {"extra": 1}, "extra"),
    ("images.0.people.0", {"extra": 1}, "extra"),
    ("images.0.references", {"extra": 1}, "extra"),
]


@pytest.mark.parametrize("path,value,field", SCHEMA_CASES)
def test_schema_errors(path, value, field):
    b = base()
    mutate(b["docs"]["briefs"], path, value)
    errs = briefs.schema_errors(b["docs"]["briefs"])
    assert any(field in e for e in errs), f"field {field} not in {errs}"


SEMANTIC_CASES = [
    # adhyay mismatch
    ("briefs.adhyay", 2, "adhyay"),
    # duplicate image_id
    (
        "briefs.images",
        [
            {"image_id": "s1_maharaj_seated", "scene_id": "S1", "shot_ids": ["S1-2"], "people": [{"name": "Maharaj", "position": "centre", "pose": "seated", "gaze": "forward"}], "place_id": "roadside", "prop": None, "prop_state": None, "camera": "medium", "light": "morning", "reason_new": "new", "on_screen_facts": ["x"], "references": {"characters": [], "place": "roadside", "style_anchor": "ref", "prop": None}},
            {"image_id": "s1_maharaj_seated", "scene_id": "S1", "shot_ids": ["S1-2"], "people": [{"name": "Maharaj", "position": "centre", "pose": "seated", "gaze": "forward"}], "place_id": "roadside", "prop": None, "prop_state": None, "camera": "medium", "light": "morning", "reason_new": "new", "on_screen_facts": ["x"], "references": {"characters": [], "place": "roadside", "style_anchor": "ref", "prop": None}},
        ],
        "unique",
    ),
    # image_id prefix mismatch
    ("briefs.images.0.image_id", "s2_wrong", "prefix"),
    # scene does not exist
    ("briefs.images.0.scene_id", "S99", "scene"),
    # shot_ids not in same scene
    ("briefs.images.0.shot_ids", ["S2-1"], "shot"),
    # shot_id does not exist
    ("briefs.images.0.shot_ids", ["S9-9"], "shot"),
    # people empty name
    ("briefs.images.0.people.0.name", "", "name"),
    # on_screen_facts empty
    ("briefs.images.0.on_screen_facts", [], "on_screen_facts"),
]


@pytest.mark.parametrize("path,value,keyword", SEMANTIC_CASES)
def test_semantic_errors(path, value, keyword):
    b = base()
    if path.startswith("briefs."):
        mutate(b["docs"]["briefs"], path[len("briefs.") :], value)
    else:
        mutate(b["docs"], path, value)
    errs = briefs.validate(1, b["docs"]["briefs"], b["docs"], b["ctx"])
    assert any(keyword in e for e in errs), f"keyword {keyword} not in {errs}"


def test_valid_base():
    b = base()
    assert briefs.schema_errors(b["docs"]["briefs"]) == []
    assert briefs.validate(1, b["docs"]["briefs"], b["docs"], b["ctx"]) == []

```
