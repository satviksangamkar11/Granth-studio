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
