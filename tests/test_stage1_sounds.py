from __future__ import annotations
import copy
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MOD_PATH = ROOT / "scripts" / "pipeline" / "stage1" / "sounds.py"
spec = importlib.util.spec_from_file_location("sounds", MOD_PATH)
sounds = importlib.util.module_from_spec(spec)
sys.modules["sounds"] = sounds
spec.loader.exec_module(sounds)

SCHEMA = sounds.SCHEMA
schema_errors = sounds.schema_errors
validate = sounds.validate


def _base_docs() -> dict:
    return {
        "sounds": {
            "adhyay": 1,
            "cues": [
                {
                    "scene_id": "S1",
                    "anchor_line_id": "S1-L1",
                    "sound_id": "bed_roadside_quiet",
                    "kind": "bed",
                    "purpose": "location bed",
                    "basis": "staging",
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
    }


def _base_ctx() -> dict:
    return {
        "script_line_ids": ["S1-L1", "S1-L2", "S2-L1"],
        "core_line_ids": ["S1-L1", "S2-L1"],
        "chapter_ovis": [1, 2, 3, 4, 5, 6, 7, 8, 9],
        "unfilmed_ovis": [],
        "preset_ids": ["01_establishing_shot", "03_slow_cinematic_push"],
        "sound_ids": ["bed_roadside_quiet", "fx_door_wood_creak"],
        "saved_voices": {
            "narrator": "CXkeo30p0Sk4Lr0TAzeo",
            "gajanan": "8fqGzH80bdkm2UseeV9f",
        },
        "speaking_characters": ["narrator", "gajanan_maharaj"],
        "known_states": {"gajanan_maharaj": ["adult_youth_v1"]},
    }


def get_parent(doc: dict, path: list):
    cur = doc
    for part in path[:-1]:
        cur = cur[int(part)] if isinstance(part, int) else cur[part]
    return cur, path[-1]


def set_at(base: dict, path: list, value) -> dict:
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    if isinstance(parent, list):
        assert isinstance(key, int) and 0 <= key < len(parent), f"bad list index {key}"
        parent[key] = value
    else:
        parent[key] = value
    assert doc != base, "mutation did not change document"
    return doc


def delete_at(base: dict, path: list) -> dict:
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    if isinstance(parent, list):
        assert isinstance(key, int) and 0 <= key < len(parent), f"bad list index {key}"
        parent.pop(key)
    else:
        parent.pop(key, None)
    assert doc != base, "mutation did not change document"
    return doc


def append_at(base: dict, path: list, value) -> dict:
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    assert isinstance(parent, list) and key == "append", "append_at expects list parent and 'append' key"
    parent.append(value)
    assert doc != base, "mutation did not change document"
    return doc


def _valid_doc() -> dict:
    return copy.deepcopy(_base_docs()["sounds"])


def _valid_ctx() -> dict:
    return copy.deepcopy(_base_ctx())


def _other_docs() -> dict:
    return {k: v for k, v in _base_docs().items() if k != "sounds"}


# ---------- schema_errors tests ----------
@pytest.mark.parametrize(
    "mutate_fn,keyword",
    [
        # required root fields (deletion)
        (lambda d: delete_at(d, ["adhyay"]), "adhyay"),
        (lambda d: delete_at(d, ["cues"]), "cues"),
        # required cue fields (deletion)
        (lambda d: delete_at(d, ["cues", 0, "scene_id"]), "scene_id"),
        (lambda d: delete_at(d, ["cues", 0, "anchor_line_id"]), "anchor_line_id"),
        (lambda d: delete_at(d, ["cues", 0, "sound_id"]), "sound_id"),
        (lambda d: delete_at(d, ["cues", 0, "kind"]), "kind"),
        (lambda d: delete_at(d, ["cues", 0, "purpose"]), "purpose"),
        (lambda d: delete_at(d, ["cues", 0, "basis"]), "basis"),
        # type / pattern violations (set invalid value)
        (lambda d: set_at(d, ["adhyay"], "x"), "adhyay"),
        (lambda d: set_at(d, ["cues", 0, "scene_id"], "X1"), "scene_id"),
        (lambda d: set_at(d, ["cues", 0, "anchor_line_id"], "S1-X"), "anchor_line_id"),
        (lambda d: set_at(d, ["cues", 0, "sound_id"], "bad_id"), "sound_id"),
        # enum invalid
        (lambda d: set_at(d, ["cues", 0, "kind"], "music"), "kind"),
        (lambda d: set_at(d, ["cues", 0, "basis"], "guess"), "basis"),
        # extra keys at root and nested
        (lambda d: set_at(d, ["extra_top"], 1), "extra_top"),
        (lambda d: set_at(d, ["cues", 0, "extra"], 1), "extra"),
        # NEED_NEW requires sound_prompt (schema) - change sound_id to NEED_NEW without sound_prompt
        (lambda d: set_at(d, ["cues", 0, "sound_id"], "NEED_NEW"), "sound_prompt"),
        # non-NEED_NEW forbids sound_prompt (schema) - add sound_prompt to regular cue
        (lambda d: set_at(d, ["cues", 0, "sound_prompt"], "a prompt"), "sound_prompt"),
        # adhyay minimum 1 (schema)
        (lambda d: set_at(d, ["adhyay"], 0), "adhyay"),
        # sound_prompt minLength 1 on NEED_NEW cue (schema)
        (lambda d: set_at(set_at(d, ["cues", 0, "sound_id"], "NEED_NEW"), ["cues", 0, "sound_prompt"], ""), "sound_prompt"),
        # purpose minLength 1 (schema)
        (lambda d: set_at(d, ["cues", 0, "purpose"], ""), "purpose"),
    ],
)
def test_schema_errors(mutate_fn, keyword):
    doc = mutate_fn(_valid_doc())
    errs = schema_errors(doc)
    assert any(keyword in e for e in errs), f"{keyword} not in {errs}"


def test_schema_valid():
    assert schema_errors(_valid_doc()) == []


# Schema-valid enum value tests
@pytest.mark.parametrize(
    "mutate_fn",
    [
        # kind = fx with fx_ sound_id
        (lambda d: set_at(set_at(d, ["cues", 0, "sound_id"], "fx_door_wood_creak"), ["cues", 0, "kind"], "fx")),
        # basis = stated
        (lambda d: set_at(d, ["cues", 0, "basis"], "stated")),
    ],
)
def test_schema_valid_enum_values(mutate_fn):
    doc = mutate_fn(_valid_doc())
    assert schema_errors(doc) == []


# ---------- validate semantic tests ----------
@pytest.mark.parametrize(
    "mutate_fn,expected_id",
    [
        # adhyay mismatch
        (lambda d: set_at(d, ["adhyay"], 2), "sounds adhyay"),
        # scene missing
        (lambda d: set_at(d, ["cues", 0, "scene_id"], "S9"), "cue[0]"),
        # anchor line not in scene
        (lambda d: set_at(d, ["cues", 0, "anchor_line_id"], "S2-L1"), "cue[0]"),
        # sound_id not in sound_ids and not NEED_NEW
        (lambda d: set_at(d, ["cues", 0, "sound_id"], "bed_unknown"), "cue[0]"),
        # kind mismatch prefix (bed sound with fx kind)
        (lambda d: set_at(d, ["cues", 0, "kind"], "fx"), "cue[0]"),
        # fx sound with bed kind
        (lambda d: set_at(d, ["cues", 0, "sound_id"], "fx_door_wood_creak"), "cue[0]"),
    ],
)
def test_semantic_errors(mutate_fn, expected_id):
    doc = mutate_fn(_valid_doc())
    errs = validate(1, doc, _other_docs(), _valid_ctx())
    assert any(expected_id in e for e in errs), f"{expected_id} not in {errs}"


def test_semantic_valid():
    assert validate(1, _valid_doc(), _other_docs(), _valid_ctx()) == []


def test_valid_returns_empty():
    assert schema_errors(_valid_doc()) == []
    assert validate(1, _valid_doc(), _other_docs(), _valid_ctx()) == []


def test_empty_context_missing_refs():
    doc = _valid_doc()
    ctx = {
        "script_line_ids": [],
        "core_line_ids": [],
        "chapter_ovis": [],
        "unfilmed_ovis": [],
        "preset_ids": [],
        "sound_ids": [],
        "saved_voices": {},
        "speaking_characters": [],
        "known_states": {},
    }
    errs = validate(1, doc, _other_docs(), ctx)
    # sound_id not in sound_ids (empty ctx)
    assert any("cue[0]" in e for e in errs)
    # anchor line check uses scenes doc, not ctx, so no error for S1-L1
    # adhyay matches, scene exists, kind matches
    assert len(errs) == 1


# ---------- regression tests for odd data (no raise) ----------
def test_validate_odd_data_no_raise():
    # doc not a dict
    errs = validate(1, None, {}, {})
    assert isinstance(errs, list) and any("sounds" in e for e in errs)

    # cues not a list
    doc = _valid_doc()
    doc["cues"] = "not a list"
    errs = validate(1, doc, _other_docs(), _valid_ctx())
    assert isinstance(errs, list) and not any("malformed structure" in e for e in errs)

    # cue not a dict
    doc = _valid_doc()
    doc["cues"] = ["not a dict"]
    errs = validate(1, doc, _other_docs(), _valid_ctx())
    assert isinstance(errs, list) and any("cue[0]" in e for e in errs) and not any("malformed structure" in e for e in errs)

    # scene_id not a string
    doc = _valid_doc()
    doc["cues"][0]["scene_id"] = 123
    errs = validate(1, doc, _other_docs(), _valid_ctx())
    assert isinstance(errs, list) and any("cue[0]" in e for e in errs) and not any("malformed structure" in e for e in errs)

    # anchor_line_id not a string
    doc = _valid_doc()
    doc["cues"][0]["anchor_line_id"] = 123
    errs = validate(1, doc, _other_docs(), _valid_ctx())
    assert isinstance(errs, list) and any("cue[0]" in e for e in errs) and not any("malformed structure" in e for e in errs)

    # sound_id not a string
    doc = _valid_doc()
    doc["cues"][0]["sound_id"] = 123
    errs = validate(1, doc, _other_docs(), _valid_ctx())
    assert isinstance(errs, list) and any("cue[0]" in e for e in errs) and not any("malformed structure" in e for e in errs)

    # scenes doc not a dict
    doc = _valid_doc()
    errs = validate(1, doc, {"scenes": "not a dict"}, _valid_ctx())
    assert isinstance(errs, list) and not any("malformed structure" in e for e in errs)

    # scenes list not a list
    doc = _valid_doc()
    errs = validate(1, doc, {"scenes": {"scenes": "not a list"}}, _valid_ctx())
    assert isinstance(errs, list) and not any("malformed structure" in e for e in errs)

    # scene entry not a dict
    doc = _valid_doc()
    errs = validate(1, doc, {"scenes": {"scenes": ["not a dict"]}}, _valid_ctx())
    assert isinstance(errs, list) and not any("malformed structure" in e for e in errs)

    # sound_ids not a list
    doc = _valid_doc()
    ctx = _valid_ctx()
    ctx["sound_ids"] = "not a list"
    errs = validate(1, doc, _other_docs(), ctx)
    assert isinstance(errs, list) and not any("malformed structure" in e for e in errs)

    # scene line_ids contains non-string (list of list) - regression for TypeError
    doc = _valid_doc()
    docs = _other_docs()
    docs["scenes"]["scenes"][0]["line_ids"] = [["S1-L1"], "S1-L2"]
    errs = validate(1, doc, docs, _valid_ctx())
    assert isinstance(errs, list) and not any("malformed structure" in e for e in errs)
    # Should not raise, and anchor line check should still work for string line_ids

    # scene line_ids is not a list
    doc = _valid_doc()
    docs = _other_docs()
    docs["scenes"]["scenes"][0]["line_ids"] = "not a list"
    errs = validate(1, doc, docs, _valid_ctx())
    assert isinstance(errs, list) and not any("malformed structure" in e for e in errs)
