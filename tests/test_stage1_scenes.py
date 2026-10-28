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

# Story scene with non-"none" teaching_treatment rejected by schema
def test_schema_story_scene_forbidden_treatment():
    doc = set_at(base_docs()["scenes"], ["scenes",0,"teaching_treatment"], "narration_over_typography")
    errs = M.schema_errors(doc)
    assert any("teaching_treatment" in e for e in errs)

# Story scene with "none" teaching_treatment accepted by schema
def test_schema_story_scene_none_treatment_allowed():
    doc = set_at(base_docs()["scenes"], ["scenes",0,"teaching_treatment"], "none")
    errs = M.schema_errors(doc)
    assert errs == []

# Discourse scene with teaching_treatment = "none" rejected by schema (not just semantic)
def test_schema_discourse_scene_none_treatment_rejected():
    doc = set_at(base_docs()["scenes"], ["scenes",1,"teaching_treatment"], "none")
    errs = M.schema_errors(doc)
    assert any("teaching_treatment" in e for e in errs)

# Discourse scene with each valid teaching_treatment accepted by schema
@pytest.mark.parametrize("treatment", [
    "narration_over_typography",
    "contemplative_hold",
    "symbol_from_text",
])
def test_schema_discourse_scene_valid_treatments(treatment):
    base = base_docs()["scenes"]
    # Ensure we actually mutate: if base already has this treatment, start from a different valid one
    current = base["scenes"][1].get("teaching_treatment")
    if current == treatment:
        other = next(t for t in ["narration_over_typography", "contemplative_hold", "symbol_from_text"] if t != treatment)
        base = set_at(base, ["scenes",1,"teaching_treatment"], other)
    doc = set_at(base, ["scenes",1,"teaching_treatment"], treatment)
    errs = M.schema_errors(doc)
    assert errs == [], f"unexpected error for {treatment}: {errs}"

# ovi_range item minimum 1 (schema constraint)
def test_schema_ovi_range_minimum():
    doc = set_at(base_docs()["scenes"], ["scenes",0,"ovi_range"], [0, 5])
    errs = M.schema_errors(doc)
    assert any("ovi_range" in e for e in errs)

# ---------- Additional schema bound tests (Note 3) ----------
# adhyay maximum 21
def test_schema_adhyay_maximum():
    doc = set_at(base_docs()["scenes"], ["adhyay"], 22)
    errs = M.schema_errors(doc)
    assert any("adhyay" in e for e in errs)

# ovi_range maxItems 2 (3 items)
def test_schema_ovi_range_maxitems():
    doc = set_at(base_docs()["scenes"], ["scenes",0,"ovi_range"], [1, 5, 9])
    errs = M.schema_errors(doc)
    assert any("ovi_range" in e for e in errs)

# ovi_range minItems 2 (1 item)
def test_schema_ovi_range_minitems():
    doc = set_at(base_docs()["scenes"], ["scenes",0,"ovi_range"], [1])
    errs = M.schema_errors(doc)
    assert any("ovi_range" in e for e in errs)

# ---------- Semantic tests ----------
# Each row changes ONE thing; contexts stay complete unless row is about that context
@pytest.mark.parametrize("mutate_fn,keyword,ctx_overrides", [
    # duplicate scene_id (append real duplicate with non-overlapping range and no lines)
    (lambda d: append_at(d, ["scenes"], {
        "scene_id": "S1",
        "section_kind": "story",
        "ovi_range": [10, 12],
        "goal": "dup",
        "turn": {"ovi": 11, "text": "dup"},
        "line_ids": [],
    }), "S1", {}),
    # ovi_range lo > hi (isolated: remove turn so only range check fires)
    (lambda d: set_at(delete_at(d, ["scenes",0,"turn"]), ["scenes",0,"ovi_range"], [5,1]), "S1", {}),
    # overlapping ranges
    (lambda d: set_at(d, ["scenes",1,"ovi_range"], [4,9]), "S2", {}),
    # chapter ovi not covered (ovi 9 missing)
    (lambda d: set_at(d, ["scenes",1,"ovi_range"], [6,8]), "9", {}),
    # unfilmed ovi inside range
    (lambda d: d, "S1", {"unfilmed_ovis": {3}}),
    # ovi outside chapter (ovi 10) - now checks range bounds
    (lambda d: set_at(d, ["scenes",1,"ovi_range"], [6,10]), "S2", {}),
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

# ---------- Regression tests for crash cases ----------
def test_validate_odd_data_no_raise():
    """validate() must never raise on any JSON-shaped input."""
    # non-dict doc
    errs = M.validate(1, None, {}, {})
    assert isinstance(errs, list) and not any("malformed structure" in e for e in errs)
    errs = M.validate(1, "not a dict", {}, {})
    assert isinstance(errs, list) and not any("malformed structure" in e for e in errs)
    errs = M.validate(1, [], {}, {})
    assert isinstance(errs, list) and not any("malformed structure" in e for e in errs)
    # scenes not a list
    errs = M.validate(1, {"adhyay": 1, "scenes": "not a list"}, {}, {})
    assert isinstance(errs, list) and not any("malformed structure" in e for e in errs)
    # scene not a dict
    errs = M.validate(1, {"adhyay": 1, "scenes": ["not a dict"]}, {}, {})
    assert isinstance(errs, list) and not any("malformed structure" in e for e in errs)
    # unhashable scene_id
    errs = M.validate(1, {"adhyay": 1, "scenes": [{"scene_id": ["S1"], "section_kind": "story", "ovi_range": [1,5], "goal": "g", "turn": {"ovi": 1, "text": "t"}, "line_ids": []}]}, {}, {})
    assert isinstance(errs, list) and not any("malformed structure" in e for e in errs)
    # unhashable line_id
    errs = M.validate(1, {"adhyay": 1, "scenes": [{"scene_id": "S1", "section_kind": "story", "ovi_range": [1,5], "goal": "g", "turn": {"ovi": 1, "text": "t"}, "line_ids": [["S1-L1"]]}]}, {}, {})
    assert isinstance(errs, list) and not any("malformed structure" in e for e in errs)
    # non-int ovi_range bounds
    errs = M.validate(1, {"adhyay": 1, "scenes": [{"scene_id": "S1", "section_kind": "story", "ovi_range": ["a", 5], "goal": "g", "turn": {"ovi": 1, "text": "t"}, "line_ids": []}]}, {}, {})
    assert isinstance(errs, list) and not any("malformed structure" in e for e in errs)
    # turn ovi with non-int bounds
    errs = M.validate(1, {"adhyay": 1, "scenes": [{"scene_id": "S1", "section_kind": "story", "ovi_range": ["1", 5], "goal": "g", "turn": {"ovi": 3, "text": "t"}, "line_ids": []}]}, {}, {})
    assert isinstance(errs, list) and not any("malformed structure" in e for e in errs)
    # unknown line id doesn't break order check
    ctx = base_ctx()
    docs = base_docs()
    docs["scenes"] = set_at(docs["scenes"], ["scenes",0,"line_ids"], ["S1-L2", "S9-L9", "S1-L1"])
    errs = M.validate(1, docs["scenes"], docs, ctx)
    # Should report both unknown line and order error
    assert any("S9-L9" in e for e in errs)
    # order error should be separate from unknown line error
    assert any("S1" in e and "S9-L9" not in e for e in errs)

def test_schema_errors_odd_data_no_raise():
    """schema_errors() must never raise on any JSON-shaped input."""
    assert isinstance(M.schema_errors(None), list)
    assert isinstance(M.schema_errors("not a dict"), list)
    assert isinstance(M.schema_errors([]), list)
    assert isinstance(M.schema_errors({"adhyay": 1, "scenes": "not a list"}), list)

# ---------- Context robustness tests ----------
# For each ctx key used by this unit, test that None, str, int, and [[]] don't raise
# and don't produce 'malformed structure' messages.
CTX_KEYS_USED = ["script_line_ids", "core_line_ids", "chapter_ovis", "unfilmed_ovis"]
BAD_VALUES = [None, "not a list", 42, [[]]]

@pytest.mark.parametrize("key", CTX_KEYS_USED)
@pytest.mark.parametrize("bad_val", BAD_VALUES)
def test_validate_ctx_robustness(key, bad_val):
    """validate() handles non-collection ctx values gracefully."""
    docs = base_docs()
    ctx = base_ctx()
    ctx[key] = bad_val
    errs = M.validate(1, docs["scenes"], docs, ctx)
    assert isinstance(errs, list)
    assert not any("malformed structure" in e for e in errs)

# ---------- Catch-all wrapper tests ----------
def test_validate_ctx_none_returns_list():
    """validate() with ctx=None returns a list, no exception."""
    docs = base_docs()
    errs = M.validate(1, docs["scenes"], docs, None)
    assert isinstance(errs, list)

def test_validate_ctx_str_returns_list():
    """validate() with ctx='x' returns a list, no exception."""
    docs = base_docs()
    errs = M.validate(1, docs["scenes"], docs, "x")
    assert isinstance(errs, list)

def test_validate_docs_none_returns_list():
    """validate() with docs=None returns a list, no exception."""
    docs = base_docs()
    errs = M.validate(1, docs["scenes"], None, base_ctx())
    assert isinstance(errs, list)

# ---------- Huge range regression tests ----------
def test_validate_huge_ovi_range_returns_quickly():
    """validate() with huge ovi_range returns quickly without enumerating."""
    docs = base_docs()
    # Range far beyond chapter ovis
    docs["scenes"] = set_at(docs["scenes"], ["scenes", 0, "ovi_range"], [1, 10**12])
    docs["scenes"] = set_at(docs["scenes"], ["scenes", 1, "ovi_range"], [6, 10**12])
    ctx = base_ctx()
    errs = M.validate(1, docs["scenes"], docs, ctx)
    assert isinstance(errs, list)
    # Should report range extends above chapter ovis
    assert any("extends above chapter ovis" in e for e in errs)

def test_validate_negative_huge_ovi_range_returns_quickly():
    """validate() with negative huge ovi_range returns quickly."""
    docs = base_docs()
    docs["scenes"] = set_at(docs["scenes"], ["scenes", 0, "ovi_range"], [-10**12, 10**12])
    ctx = base_ctx()
    errs = M.validate(1, docs["scenes"], docs, ctx)
    assert isinstance(errs, list)
    # Should report range extends below and above chapter ovis
    assert any("extends below chapter ovis" in e for e in errs)
    assert any("extends above chapter ovis" in e for e in errs)

# ---------- Gap in chapter ovis regression test ----------
def test_validate_gap_in_chapter_ovis_reported():
    """validate() reports ovis inside scene range that are not in chapter_ovis (gap)."""
    docs = base_docs()
    ctx = base_ctx()
    # Remove ovi 7 from chapter_ovis, creating a gap
    ctx["chapter_ovis"] = {1,2,3,4,5,6,8,9}
    # S2 range [6,9] contains ovi 7 which is not a chapter ovi
    errs = M.validate(1, docs["scenes"], docs, ctx)
    assert any("ovi 7: outside chapter ovis" in e for e in errs), f"missing gap error in {errs}"

# ---------- Unfilmed ovi inside range but not in chapter regression test ----------
def test_validate_unfilmed_ovi_inside_range_not_in_chapter():
    """validate() reports unfilmed ovi inside scene range even when not a chapter ovi."""
    docs = base_docs()
    ctx = base_ctx()
    # Add unfilmed ovi 10, extend S2 range to [6,10]
    ctx["unfilmed_ovis"] = {10}
    docs["scenes"] = set_at(docs["scenes"], ["scenes", 1, "ovi_range"], [6, 10])
    errs = M.validate(1, docs["scenes"], docs, ctx)
    # Should report unfilmed ovi 10 inside S2 range
    assert any("S2: ovi 10 is unfilmed but inside the range" in e for e in errs), f"missing unfilmed error in {errs}"

# ---------- Sparse chapter ovis regression test (Class 1 bug fix) ----------
def test_validate_sparse_chapter_ovis_no_false_gaps():
    """validate() does not report false gaps when chapter_ovis is sparse and scene covers only filmed ovi."""
    docs = copy.deepcopy(base_docs())
    ctx = copy.deepcopy(base_ctx())
    # Sparse chapter ovis: 1,2,3,4,6,7,8,9 (ovi 5 missing)
    ctx["chapter_ovis"] = {1,2,3,4,6,7,8,9}
    ctx["unfilmed_ovis"] = set()
    # Adjust scene ranges: S1 covers [1,4], S2 covers [6,9] - no gap inside any range
    docs["scenes"]["scenes"][0]["ovi_range"] = [1, 4]
    # S2 stays [6, 9] (baseline value)
    errs = M.validate(1, docs["scenes"], docs, ctx)
    # Should NOT report ovi 5 as "outside chapter ovis" because it's not in any scene range
    outside_errors = [e for e in errs if "outside chapter ovis" in e]
    assert not outside_errors, f"unexpected outside chapter ovis errors: {outside_errors}"
    # Should have no errors at all for this valid setup
    assert errs == [], f"unexpected errors: {errs}"

def test_validate_gap_inside_range_reported():
    """validate() reports gap when chapter_ovis has a hole inside a scene range."""
    docs = copy.deepcopy(base_docs())
    ctx = copy.deepcopy(base_ctx())
    # Chapter ovis: 1,2,3,4,5,6,8,9 (ovi 7 missing) - BASE ranges [1,5] and [6,9]
    ctx["chapter_ovis"] = {1,2,3,4,5,6,8,9}
    ctx["unfilmed_ovis"] = set()
    # S2 range [6,9] contains ovi 7 which is not a chapter ovi
    errs = M.validate(1, docs["scenes"], docs, ctx)
    assert any("ovi 7: outside chapter ovis" in e for e in errs), f"missing gap error in {errs}"

# ---------- Additional gap regression tests ----------
def test_validate_dense_chapter_ovis_no_gaps():
    """validate() reports no gaps when chapter_ovis is dense and scene range matches."""
    docs = base_docs()
    ctx = base_ctx()
    # Dense chapter ovis 1-10, scene range [3,8] - all covered, no gaps
    ctx["chapter_ovis"] = set(range(1, 11))
    docs["scenes"] = {
        "adhyay": 1,
        "scenes": [
            {
                "scene_id": "S1",
                "section_kind": "story",
                "ovi_range": [3, 8],
                "goal": "middle",
                "turn": {"ovi": 5, "text": "middle"},
                "line_ids": [],
            }
        ],
    }
    errs = M.validate(1, docs["scenes"], docs, ctx)
    outside_errors = [e for e in errs if "outside chapter ovis" in e]
    assert not outside_errors, f"unexpected outside chapter ovis errors: {outside_errors}"

def test_validate_gap_at_start_of_range():
    """validate() reports gap at start of effective range."""
    docs = base_docs()
    ctx = base_ctx()
    # Chapter ovis: 1,2,3, 6,7,8 (gap 4,5)
    ctx["chapter_ovis"] = {1,2,3,6,7,8}
    # Scene range [2,7] - effective range [2,7], inside ovis [2,3,6,7]
    # Gaps: between 3 and 6 -> 4,5
    docs["scenes"] = {
        "adhyay": 1,
        "scenes": [
            {
                "scene_id": "S1",
                "section_kind": "story",
                "ovi_range": [2, 7],
                "goal": "test",
                "turn": {"ovi": 3, "text": "test"},
                "line_ids": [],
            }
        ],
    }
    errs = M.validate(1, docs["scenes"], docs, ctx)
    assert any("ovi 4: outside chapter ovis" in e for e in errs)
    assert any("ovi 5: outside chapter ovis" in e for e in errs)

def test_validate_gap_at_end_of_range():
    """validate() reports gap at end of effective range."""
    docs = base_docs()
    ctx = base_ctx()
    # Chapter ovis: 1,2,3, 6,7,8 (gap 4,5)
    ctx["chapter_ovis"] = {1,2,3,6,7,8}
    # Scene range [3,8] - effective range [3,8], inside ovis [3,6,7,8]
    # Gaps: between 3 and 6 -> 4,5
    docs["scenes"] = {
        "adhyay": 1,
        "scenes": [
            {
                "scene_id": "S1",
                "section_kind": "story",
                "ovi_range": [3, 8],
                "goal": "test",
                "turn": {"ovi": 6, "text": "test"},
                "line_ids": [],
            }
        ],
    }
    errs = M.validate(1, docs["scenes"], docs, ctx)
    assert any("ovi 4: outside chapter ovis" in e for e in errs)
    assert any("ovi 5: outside chapter ovis" in e for e in errs)

def test_validate_gap_before_first_inside():
    """validate() reports gap before first inside ovi when range starts before it."""
    docs = base_docs()
    ctx = base_ctx()
    # Chapter ovis: 5,6,7,8
    ctx["chapter_ovis"] = {5,6,7,8}
    # Scene range [2,8] - effective range [5,8] (clipped to chapter_min=5)
    # Inside ovis: [5,6,7,8]
    # Gap before first inside: eff_lo=5, first inside=5 -> no gap
    # But range extends below chapter ovis (2 < 5)
    docs["scenes"] = {
        "adhyay": 1,
        "scenes": [
            {
                "scene_id": "S1",
                "section_kind": "story",
                "ovi_range": [2, 8],
                "goal": "test",
                "turn": {"ovi": 6, "text": "test"},
                "line_ids": [],
            }
        ],
    }
    errs = M.validate(1, docs["scenes"], docs, ctx)
    # Should report extends below
    assert any("extends below chapter ovis" in e for e in errs)
    # No outside chapter ovis errors since no gaps inside effective range
    outside_errors = [e for e in errs if "outside chapter ovis" in e]
    assert not outside_errors, f"unexpected outside chapter ovis errors: {outside_errors}"

def test_validate_gap_after_last_inside():
    """validate() reports gap after last inside ovi when range ends after it."""
    docs = base_docs()
    ctx = base_ctx()
    # Chapter ovis: 1,2,3,4
    ctx["chapter_ovis"] = {1,2,3,4}
    # Scene range [1,7] - effective range [1,4] (clipped to chapter_max=4)
    # Inside ovis: [1,2,3,4]
    # Gap after last inside: last inside=4, eff_hi=4 -> no gap
    # But range extends above chapter ovis (7 > 4)
    docs["scenes"] = {
        "adhyay": 1,
        "scenes": [
            {
                "scene_id": "S1",
                "section_kind": "story",
                "ovi_range": [1, 7],
                "goal": "test",
                "turn": {"ovi": 2, "text": "test"},
                "line_ids": [],
            }
        ],
    }
    errs = M.validate(1, docs["scenes"], docs, ctx)
    # Should report extends above
    assert any("extends above chapter ovis" in e for e in errs)
    # No outside chapter ovis errors since no gaps inside effective range
    outside_errors = [e for e in errs if "outside chapter ovis" in e]
    assert not outside_errors, f"unexpected outside chapter ovis errors: {outside_errors}"

# ---------- Total gap message cap regression test (Note 1) ----------
def test_validate_total_gap_message_cap():
    """validate() caps total 'outside chapter ovis' messages at 1000 and adds summary."""
    docs = base_docs()
    ctx = base_ctx()
    # Chapter ovis: 3000 ovis spaced 3 apart (1, 4, 7, 10, ...)
    # This creates many gaps of size 2 between each consecutive ovi
    chapter_ovis = set(range(1, 9001, 3))  # 3000 ovis: 1, 4, 7, ..., 8998
    ctx["chapter_ovis"] = chapter_ovis
    # One scene covering the entire range [1, 8998]
    docs["scenes"] = {
        "adhyay": 1,
        "scenes": [
            {
                "scene_id": "S1",
                "section_kind": "story",
                "ovi_range": [1, 8998],
                "goal": "test",
                "turn": {"ovi": 1, "text": "test"},
                "line_ids": [],
            }
        ],
    }
    errs = M.validate(1, docs["scenes"], docs, ctx)
    # Count "outside chapter ovis" messages
    outside_msgs = [e for e in errs if "outside chapter ovis" in e and "message limit reached" not in e]
    summary_msgs = [e for e in errs if "message limit reached" in e]
    # Should have at most 1000 per-ovi messages
    assert len(outside_msgs) <= 1000, f"too many outside messages: {len(outside_msgs)}"
    # Should have exactly one summary message total
    assert len(summary_msgs) == 1, f"expected 1 summary message, got {len(summary_msgs)}: {summary_msgs}"
    assert "S1: more ovis outside chapter ovis (message limit reached)" in summary_msgs[0]
    # Total messages should be reasonable (not millions)
    assert len(errs) <= 1005, f"too many total messages: {len(errs)}"

# ---------- Bool ovi regression tests (Note 2) ----------
def test_validate_bool_chapter_ovi_ignored():
    """validate() treats bool in chapter_ovis as non-int (ignored), not as ovi 1."""
    docs = copy.deepcopy(base_docs())
    ctx = copy.deepcopy(base_ctx())
    # chapter_ovis contains True (which is 1 in Python) and 2-9
    # True should be ignored, so ovi 1 is NOT in chapter_ovis
    ctx["chapter_ovis"] = {True, 2, 3, 4, 5, 6, 7, 8, 9}
    errs = M.validate(1, docs["scenes"], docs, ctx)
    # ovi 1 should be reported as not covered (since True is ignored, 1 is not in chapter_ovis)
    # But wait: the scene range [1,5] covers 1, but 1 is not in chapter_ovis (True was ignored)
    # So ovi 1 is in scene range but not in chapter_ovis -> gap error
    # Actually, the logic: chapter_ovis_int filters out bool, so chapter_ovis_int = {2,3,4,5,6,7,8,9}
    # Scene S1 range [1,5] -> effective range [2,5] (clipped to chapter_min=2)
    # Inside ovis: [2,3,4,5]
    # Gap before first inside: eff_lo=2, first inside=2 -> no gap
    # But range extends below chapter ovis (1 < 2)
    assert any("extends below chapter ovis" in e for e in errs)
    # ovi 1 should NOT be reported as "outside chapter ovis" because it's below chapter_min
    # and the "extends below" message covers it
    outside_msgs = [e for e in errs if "outside chapter ovis" in e]
    # Should not have "ovi 1: outside chapter ovis" because it's handled by "extends below"
    assert not any("ovi 1: outside chapter ovis" in e for e in outside_msgs)

def test_validate_bool_unfilmed_ovi_ignored():
    """validate() treats bool in unfilmed_ovis as non-int (ignored)."""
    docs = copy.deepcopy(base_docs())
    ctx = copy.deepcopy(base_ctx())
    # unfilmed_ovis contains True (which is 1)
    ctx["unfilmed_ovis"] = {True}
    errs = M.validate(1, docs["scenes"], docs, ctx)
    # True should be ignored, so no unfilmed error for ovi 1
    unfilmed_errors = [e for e in errs if "unfilmed but inside the range" in e]
    assert not unfilmed_errors, f"unexpected unfilmed error for bool: {unfilmed_errors}"

def test_validate_bool_ovi_range_rejected():
    """validate() treats bool in ovi_range as non-int (reports error)."""
    docs = copy.deepcopy(base_docs())
    ctx = copy.deepcopy(base_ctx())
    # ovi_range with True as lo bound - build directly, not via set_at (True == 1)
    docs["scenes"]["scenes"][0]["ovi_range"] = [True, 5]
    errs = M.validate(1, docs["scenes"], docs, ctx)
    # Should report ovi_range must be integers
    assert any("S1: ovi_range must be integers" in e for e in errs)

def test_validate_bool_turn_ovi_rejected():
    """validate() treats bool in turn.ovi as non-int (ignored for range check)."""
    docs = copy.deepcopy(base_docs())
    ctx = copy.deepcopy(base_ctx())
    # turn.ovi = True (which is 1)
    docs["scenes"]["scenes"][0]["turn"]["ovi"] = True
    errs = M.validate(1, docs["scenes"], docs, ctx)
    # Should not report "turn ovi outside range" because True is not treated as int
    # (the check requires _is_int_not_bool for turn_ovi)
    turn_errors = [e for e in errs if "turn ovi outside range" in e]
    assert not turn_errors, f"unexpected turn ovi error for bool: {turn_errors}"

# ---------- Positive ----------
def test_valid():
    docs = base_docs()
    ctx = base_ctx()
    assert M.schema_errors(docs["scenes"]) == []
    assert M.validate(1, docs["scenes"], docs, ctx) == []
