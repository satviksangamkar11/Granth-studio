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
    "path,keyword",
    [
        # required root fields
        (["adhyay"], "adhyay"),
        (["cues"], "cues"),
        # required cue fields
        (["cues", 0, "scene_id"], "scene_id"),
        (["cues", 0, "anchor_line_id"], "anchor_line_id"),
        (["cues", 0, "sound_id"], "sound_id"),
        (["cues", 0, "kind"], "kind"),
        (["cues", 0, "purpose"], "purpose"),
        (["cues", 0, "basis"], "basis"),
        # type / pattern
        (["adhyay"], "adhyay"),
        (["cues", 0, "scene_id"], "scene_id"),
        (["cues", 0, "anchor_line_id"], "anchor_line_id"),
        (["cues", 0, "sound_id"], "sound_id"),
        (["cues", 0, "kind"], "kind"),
        (["cues", 0, "purpose"], "purpose"),
        (["cues", 0, "basis"], "basis"),
        # enum invalid
        (["cues", 0, "kind"], "kind"),
        (["cues", 0, "basis"], "basis"),
        # extra keys at root and nested
        (["extra_top"], "extra_top"),
        (["cues", 0, "extra"], "extra"),
        # NEED_NEW requires sound_prompt (schema)
        (["cues", 0, "sound_prompt"], "sound_prompt"),
    ],
)
def test_schema_errors(path, keyword):
    doc = _valid_doc()
    if path == ["adhyay"]:
        doc = set_at(doc, path, "x")
    elif path == ["cues"]:
        doc = delete_at(doc, path)
    elif path == ["cues", 0, "scene_id"]:
        doc = set_at(doc, path, "X1")
    elif path == ["cues", 0, "anchor_line_id"]:
        doc = set_at(doc, path, "S1-X")
    elif path == ["cues", 0, "sound_id"]:
        doc = set_at(doc, path, "bad_id")
    elif path == ["cues", 0, "kind"]:
        doc = set_at(doc, path, "music")
    elif path == ["cues", 0, "purpose"]:
        doc = set_at(doc, path, "")
    elif path == ["cues", 0, "basis"]:
        doc = set_at(doc, path, "guess")
    elif path == ["cues", 0, "kind"] and keyword == "kind":
        doc = set_at(doc, path, "invalid_kind")
    elif path == ["cues", 0, "basis"] and keyword == "basis":
        doc = set_at(doc, path, "invalid_basis")
    elif path == ["extra_top"]:
        doc["extra_top"] = 1
    elif path == ["cues", 0, "extra"]:
        doc = set_at(doc, path, 1)
    elif path == ["cues", 0, "sound_prompt"]:
        # NEED_NEW cue with sound_prompt is valid at schema level; non-NEED_NEW with sound_prompt is forbidden
        doc = set_at(doc, ["cues", 0, "sound_id"], "NEED_NEW")
        doc = set_at(doc, path, "a prompt")
    errs = schema_errors(doc)
    assert any(keyword in e for e in errs), f"{keyword} not in {errs}"


def test_schema_valid():
    assert schema_errors(_valid_doc()) == []


# ---------- validate semantic tests ----------
@pytest.mark.parametrize(
    "mutate_fn,keyword",
    [
        # adhyay mismatch
        (lambda d: set_at(d, ["adhyay"], 2), "adhyay"),
        # scene missing
        (lambda d: set_at(d, ["cues", 0, "scene_id"], "S9"), "scene"),
        # anchor line not in scene
        (lambda d: set_at(d, ["cues", 0, "anchor_line_id"], "S2-L1"), "anchor_line_id"),
        # sound_id not in sound_ids and not NEED_NEW
        (lambda d: set_at(d, ["cues", 0, "sound_id"], "bed_unknown"), "sound_id"),
        # kind mismatch prefix (bed sound with fx kind)
        (lambda d: set_at(d, ["cues", 0, "kind"], "fx"), "kind"),
        # fx sound with bed kind
        (lambda d: set_at(d, ["cues", 0, "sound_id"], "fx_door_wood_creak"), "kind"),
        # NEED_NEW without sound_prompt (semantic sees missing prompt)
        (lambda d: set_at(d, ["cues", 0, "sound_id"], "NEED_NEW"), "sound_prompt"),
        # non-NEED_NEW cue with sound_prompt is schema error, not semantic
    ],
)
def test_semantic_errors(mutate_fn, keyword):
    doc = mutate_fn(_valid_doc())
    errs = validate(1, doc, _other_docs(), _valid_ctx())
    assert any(keyword in e for e in errs), f"{keyword} not in {errs}"


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
    assert any("S1-L1" in e for e in errs)
    assert any("bed_roadside_quiet" in e for e in errs)
