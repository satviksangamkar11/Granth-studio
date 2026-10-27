from __future__ import annotations
import copy
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "pipeline" / "stage1"))
import scenes as M  # type: ignore

# ---------- Robust helpers ----------
def get_parent(doc: dict, path: list):
    cur = doc
    for p in path[:-1]:
        cur = cur[p] if isinstance(cur, dict) else cur[int(p)]
    return cur, path[-1]

def set_at(base: dict, path: list, value) -> dict:
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    if isinstance(parent, list):
        parent[int(key)] = value
    else:
        parent[key] = value
    assert doc != base, "mutation had no effect"
    return doc

def delete_at(base: dict, path: list) -> dict:
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    if isinstance(parent, list):
        del parent[int(key)]
    else:
        del parent[key]
    assert doc != base, "mutation had no effect"
    return doc

def append_at(base: dict, path: list, value) -> dict:
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    assert isinstance(parent, dict), "append target must be dict"
    lst = parent.setdefault(key, [])
    lst.append(value)
    assert doc != base, "mutation had no effect"
    return doc

# ---------- Base data ----------
def base_docs() -> dict:
    return {
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
        "story_map": {}, "coverage": {}, "shots": {}, "briefs": {},
        "looks": {}, "voices": {}, "sounds": {}, "questions": {},
    }

def base_ctx() -> dict:
    return {
        "script_line_ids": ["S1-L1", "S1-L2", "S2-L1"],
        "core_line_ids": {"S1-L1", "S2-L1"},
        "chapter_ovis": {1,2,3,4,5,6,7,8,9},
        "unfilmed_ovis": set(),
        "preset_ids": {"01_establishing_shot", "03_slow_cinematic_push"},
        "sound_ids": {"bed_roadside_quiet", "fx_door_wood_creak"},
        "saved_voices": {"narrator": "CXkeo30p0Sk4Lr0TAzeo", "gajanan": "8fqGzH80bdkm2UseeV9f"},
        "speaking_characters": {"narrator", "gajanan_maharaj"},
        "known_states": {"gajanan_maharaj": {"adult_youth_v1"}},
    }

# ---------- Schema tests ----------
# Required field deletions (root)
@pytest.mark.parametrize("path", [
    ["adhyay"], ["scenes"],
])
def test_schema_required_root(path):
    doc = delete_at(base_docs()["scenes"], path)
    errs = M.schema_errors(doc)
    assert any(path[-1] in e for e in errs)

# Required field deletions (scene object)
@pytest.mark.parametrize("path", [
    ["scenes",0,"scene_id"], ["scenes",0,"section_kind"], ["scenes",0,"ovi_range"],
    ["scenes",0,"goal"], ["scenes",0,"turn"], ["scenes",0,"line_ids"],
])
def test_schema_required_scene(path):
    doc = delete_at(base_docs()["scenes"], path)
    errs = M.schema_errors(doc)
    assert any(path[-1] in e for e in errs)

# Required field deletions (turn object)
@pytest.mark.parametrize("path", [
    ["scenes",0,"turn","ovi"], ["scenes",0,"turn","text"],
])
def test_schema_required_turn(path):
    doc = delete_at(base_docs()["scenes"], path)
    errs = M.schema_errors(doc)
    assert any(path[-1] in e for e in errs)

# Extra keys (root and nested)
@pytest.mark.parametrize("path", [
    [], ["scenes",0], ["scenes",0,"turn"],
])
def test_schema_extra_keys(path):
    doc = copy.deepcopy(base_docs()["scenes"])
    target, _ = get_parent(doc, path + ["__extra__"])
    target["__extra__"] = 1
    errs = M.schema_errors(doc)
    assert any("__extra__" in e for e in errs)

# Enum invalid values
@pytest.mark.parametrize("path,value", [
    (["scenes",0,"section_kind"], "bad"),
    (["scenes",1,"teaching_treatment"], "bad"),
])
def test_schema_enum(path, value):
    doc = set_at(base_docs()["scenes"], path, value)
    errs = M.schema_errors(doc)
    assert any(path[-1] in e for e in errs)

# Type/format/constraint errors
@pytest.mark.parametrize("path,value,keyword", [
    (["adhyay"], 0, "adhyay"), (["adhyay"], 22, "adhyay"), (["adhyay"], "1", "adhyay"),
    (["scenes"], "x", "scenes"), (["scenes",0], "x", "scenes"),
    (["scenes",0,"scene_id"], "X1", "scene_id"), (["scenes",0,"scene_id"], "S100", "scene_id"),
    (["scenes",0,"ovi_range"], [5,1], "ovi_range"),  # schema: minItems/maxItems/type ok, but lo>hi is semantic
    (["scenes",0,"ovi_range"], [1], "ovi_range"), (["scenes",0,"ovi_range"], [1,5,9], "ovi_range"),
    (["scenes",0,"ovi_range"], ["1",5], "ovi_range"),
    (["scenes",0,"goal"], "", "goal"), (["scenes",0,"goal"], 123, "goal"),
    (["scenes",0,"turn"], "x", "turn"),
    (["scenes",0,"turn","ovi"], 0, "ovi"), (["scenes",0,"turn","ovi"], "3", "ovi"),
    (["scenes",0,"turn","text"], "", "text"), (["scenes",0,"turn","text"], 123, "text"),
    (["scenes",0,"turn","text"], "x"*401, "text"),
    (["scenes",0,"line_ids"], "x", "line_ids"),
    (["scenes",0,"line_ids",0], 123, "line_ids"), (["scenes",0,"line_ids",0], "bad-id", "line_ids"),
    # discourse requires teaching_treatment (schema required)
    (["scenes",1,"teaching_treatment"], None, "teaching_treatment"),
])
def test_schema_errors(path, value, keyword):
    doc = set_at(base_docs()["scenes"], path, value) if value is not None else delete_at(base_docs()["scenes"], path)
    errs = M.schema_errors(doc)
    assert any(keyword in e for e in errs), f"missing {keyword} in {errs}"

# ---------- Semantic tests ----------
# Each row changes ONE thing; contexts stay complete unless row is about that context
@pytest.mark.parametrize("mutate_fn,keyword,ctx_overrides", [
    # duplicate scene_id (append real duplicate)
    (lambda d: append_at(d, ["scenes"], copy.deepcopy(d["scenes"][0])), "S1", {}),
    # ovi_range lo > hi
    (lambda d: set_at(d, ["scenes",0,"ovi_range"], [5,1]), "S1", {}),
    # overlapping ranges
    (lambda d: set_at(d, ["scenes",1,"ovi_range"], [4,9]), "S2", {}),
    # chapter ovi not covered (ovi 9 missing)
    (lambda d: set_at(d, ["scenes",1,"ovi_range"], [6,8]), "9", {}),
    # unfilmed ovi inside range
    (lambda d: d, "S1", {"unfilmed_ovis": {3}}),
    # ovi outside chapter (ovi 10)
    (lambda d: set_at(d, ["scenes",1,"ovi_range"], [6,10]), "10", {}),
    # turn ovi outside range
    (lambda d: set_at(d, ["scenes",0,"turn","ovi"], 6), "S1", {}),
    # line_id not in script
    (lambda d: set_at(d, ["scenes",0,"line_ids",0], "S9-L1"), "S9-L1", {}),
    # duplicate line_id across scenes (append second entry)
    (lambda d: append_at(d, ["scenes",1,"line_ids"], "S1-L1"), "S1-L1", {}),
    # line_ids not in script order within scene
    (lambda d: set_at(d, ["scenes",0,"line_ids"], ["S1-L2","S1-L1"]), "S1", {}),
    # core line not in any scene (remove S1-L1 from S1)
    (lambda d: set_at(d, ["scenes",0,"line_ids"], ["S1-L2"]), "S1-L1", {}),
    # discourse scene teaching_treatment none (semantic: must not be none)
    (lambda d: set_at(d, ["scenes",1,"teaching_treatment"], "none"), "S2", {}),
    # story scene with teaching_treatment (must be absent or none)
    (lambda d: set_at(d, ["scenes",0,"teaching_treatment"], "narration_over_typography"), "S1", {}),
    # adhyay mismatch
    (lambda d: set_at(d, ["adhyay"], 2), "adhyay", {}),
])
def test_semantic_errors(mutate_fn, keyword, ctx_overrides):
    docs = base_docs()
    docs["scenes"] = mutate_fn(docs["scenes"])
    ctx = base_ctx()
    ctx.update(ctx_overrides)
    errs = M.validate(1, docs["scenes"], docs, ctx)
    assert any(keyword in e for e in errs), f"missing {keyword} in {errs}"

# ---------- Positive ----------
def test_valid():
    docs = base_docs()
    ctx = base_ctx()
    assert M.schema_errors(docs["scenes"]) == []
    assert M.validate(1, docs["scenes"], docs, ctx) == []
