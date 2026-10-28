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
    # adhyay minimum bound
    (["adhyay"], lambda d: set_at(d, ["adhyay"], 0), "adhyay"),
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
