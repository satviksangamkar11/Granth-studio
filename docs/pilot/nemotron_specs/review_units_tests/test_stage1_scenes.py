from __future__ import annotations
import copy
import json
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "pipeline" / "stage1"))
import scenes as M  # type: ignore

def base() -> tuple[dict, dict]:
    docs = {
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
        }
    }
    ctx = {
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
    return copy.deepcopy(docs), copy.deepcopy(ctx)

def mutate(obj: dict, path: str, value):
    """Set or delete a single key in a nested dict/list. path like 'scenes/0/section_kind'."""
    parts = path.split("/")
    cur = obj
    for p in parts[:-1]:
        cur = cur[int(p)] if p.isdigit() else cur[p]
    key = parts[-1]
    if value is None:
        cur.pop(key, None)
    else:
        cur[key] = value

# ---------- Schema tests ----------
@pytest.mark.parametrize("path,value,keyword", [
    # adhyay
    ("adhyay", 0, "adhyay"),
    ("adhyay", 22, "adhyay"),
    ("adhyay", "1", "adhyay"),
    # scenes array
    ("scenes", "not-array", "scenes"),
    ("scenes/0", "not-obj", "scenes"),
    # scene_id pattern
    ("scenes/0/scene_id", "X1", "scene_id"),
    ("scenes/0/scene_id", "S100", "scene_id"),
    # section_kind enum
    ("scenes/0/section_kind", "invalid", "section_kind"),
    # ovi_range
    ("scenes/0/ovi_range", [5, 1], "ovi_range"),
    ("scenes/0/ovi_range", [1], "ovi_range"),
    ("scenes/0/ovi_range", [1, 5, 9], "ovi_range"),
    ("scenes/0/ovi_range", ["1", 5], "ovi_range"),
    # goal required string
    ("scenes/0/goal", "", "goal"),
    ("scenes/0/goal", 123, "goal"),
    # turn
    ("scenes/0/turn", "x", "turn"),
    ("scenes/0/turn/ovi", 0, "ovi"),
    ("scenes/0/turn/ovi", "3", "ovi"),
    ("scenes/0/turn/text", "", "text"),
    ("scenes/0/turn/text", 123, "text"),
    ("scenes/0/turn/text", "x" * 401, "text"),
    # line_ids
    ("scenes/0/line_ids", "x", "line_ids"),
    ("scenes/0/line_ids/0", 123, "line_ids"),
    ("scenes/0/line_ids/0", "bad-id", "line_ids"),
    # teaching_treatment enum
    ("scenes/1/teaching_treatment", "bad", "teaching_treatment"),
    # extra keys on nested objects
    ("scenes/0", {"extra": 1}, "extra"),
    ("scenes/0/turn", {"extra": 1}, "extra"),
    # teaching_treatment presence rules (schema level: discourse requires it)
    ("scenes/1/teaching_treatment", None, "teaching_treatment"),
    # story must not have teaching_treatment (or must be none) - schema allows none, semantic checks rest
])
def test_schema_errors(path, value, keyword):
    docs, ctx = base()
    mutate(docs["scenes"], path, value)
    errs = M.schema_errors(docs["scenes"])
    assert any(keyword in e for e in errs), f"missing {keyword} in {errs}"

# ---------- Semantic tests ----------
@pytest.mark.parametrize("path,value,keyword", [
    # duplicate scene_id
    ("scenes/1/scene_id", "S1", "S1"),
    # ovi_range lo > hi
    ("scenes/0/ovi_range", [5, 1], "S1"),
    # overlapping ranges
    ("scenes/1/ovi_range", [4, 9], "S2"),
    # chapter ovi not covered (ovi 9 missing)
    ("scenes/1/ovi_range", [6, 8], "9"),
    # unfilmed ovi inside range
    ("scenes/0/ovi_range", [1, 5], "S1"),  # will add unfilmed 3 in ctx
    # ovi outside chapter (ovi 10)
    ("scenes/1/ovi_range", [6, 10], "10"),
    # turn ovi outside range
    ("scenes/0/turn/ovi", 6, "S1"),
    # line_id not in script
    ("scenes/0/line_ids/0", "S9-L1", "S9-L1"),
    # duplicate line_id across scenes
    ("scenes/1/line_ids/0", "S1-L1", "S1-L1"),
    # line_ids not in script order within scene
    ("scenes/0/line_ids", ["S1-L2", "S1-L1"], "S1"),
    # core line not in any scene
    ("scenes/0/line_ids", ["S1-L2"], "S1-L1"),
    # discourse scene missing teaching_treatment (semantic: must not be none)
    ("scenes/1/teaching_treatment", "none", "S2"),
    # adhyay mismatch
    ("adhyay", 2, "adhyay"),
])
def test_semantic_errors(path, value, keyword):
    docs, ctx = base()
    # special handling for unfilmed ovi test
    if path == "scenes/0/ovi_range" and value == [1, 5] and keyword == "S1":
        ctx = copy.deepcopy(ctx)
        ctx["unfilmed_ovis"] = [3]
    else:
        ctx = copy.deepcopy(ctx)
    mutate(docs["scenes"], path, value)
    errs = M.validate(1, docs["scenes"], docs, ctx)
    assert any(keyword in e for e in errs), f"missing {keyword} in {errs}"

# ---------- Positive ----------
def test_valid():
    docs, ctx = base()
    assert M.schema_errors(docs["scenes"]) == []
    assert M.validate(1, docs["scenes"], docs, ctx) == []
