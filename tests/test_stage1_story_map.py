from __future__ import annotations
import copy
import sys
import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "pipeline" / "stage1"))
import story_map as sm

# ---------- robust helpers ----------
def get_parent(doc: dict, path: list):
    """Return (parent_container, key) where parent_container[key] is the target"""
    cur = doc
    for p in path[:-1]:
        cur = cur[p]
    return cur, path[-1]

def get_target(doc: dict, path: list):
    """Return the target object at path"""
    cur = doc
    for p in path:
        cur = cur[p]
    return cur

def set_at(base: dict, path: list, value) -> dict:
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    parent[key] = value
    assert doc != base, "mutation had no effect"
    return doc

def delete_at(base: dict, path: list) -> dict:
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    del parent[key]
    assert doc != base, "mutation had no effect"
    return doc

def append_at(base: dict, path: list, value) -> dict:
    doc = copy.deepcopy(base)
    target = get_target(doc, path)
    assert isinstance(target, list), "append target must be list"
    target.append(value)
    assert doc != base, "mutation had no effect"
    return doc

# ---------- BASE data ----------
BASE_DOCS = {
    "story_map": {
        "adhyay": 1,
        "ovi_types": [
            {"ovi": 1, "type": "STORY"},
            {"ovi": 2, "type": "STORY"},
            {"ovi": 3, "type": "STORY"},
            {"ovi": 4, "type": "STORY"},
            {"ovi": 5, "type": "STORY"},
            {"ovi": 6, "type": "TEACHING"},
            {"ovi": 7, "type": "TEACHING"},
            {"ovi": 8, "type": "TEACHING"},
            {"ovi": 9, "type": "TEACHING"},
        ],
        "events": [
            {
                "event_id": "E1",
                "title": "Arrival",
                "ovi_range": [1, 5],
                "key_ovis": [3],
                "kind": "story",
                "closure": "RESOLVED_IN_ADHYAY",
            },
            {
                "event_id": "E2",
                "title": "Teaching",
                "ovi_range": [6, 9],
                "key_ovis": [7],
                "kind": "discourse",
                "closure": "NA",
            },
        ],
    }
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

# ---------- schema_errors tests ----------
@pytest.mark.parametrize("path,value,keyword", [
    # valid
    (None, None, None),
    # missing required top-level
    (["adhyay"], ..., "adhyay"),
    (["ovi_types"], ..., "ovi_types"),
    (["events"], ..., "events"),
    # extra top-level key
    (["extra"], 1, "extra"),
    # adhyay range
    (["adhyay"], 0, "adhyay"),
    (["adhyay"], 22, "adhyay"),
    # ovi_types items
    (["ovi_types", 0, "ovi"], ..., "ovi"),
    (["ovi_types", 0, "type"], ..., "type"),
    (["ovi_types", 0, "type"], "INVALID", "type"),
    (["ovi_types", 0, "extra"], 1, "extra"),
    (["ovi_types", 0, "ovi"], "x", "ovi"),
    # events items
    (["events", 0, "event_id"], ..., "event_id"),
    (["events", 0, "title"], ..., "title"),
    (["events", 0, "ovi_range"], ..., "ovi_range"),
    (["events", 0, "key_ovis"], ..., "key_ovis"),
    (["events", 0, "kind"], ..., "kind"),
    (["events", 0, "closure"], ..., "closure"),
    (["events", 0, "event_id"], "X1", "event_id"),
    (["events", 0, "kind"], "invalid", "kind"),
    (["events", 0, "closure"], "INVALID", "closure"),
    (["events", 0, "ovi_range"], [1], "ovi_range"),
    (["events", 0, "extra"], 1, "extra"),
    # --- Round 9 additions: enum coverage for ovi_types.type ---
    (["ovi_types", 0, "type"], "INVOCATION", None),
    (["ovi_types", 0, "type"], "OTHER", None),
    (["ovi_types", 0, "type"], "PHILOSOPHY", None),
    (["ovi_types", 0, "type"], "RECAP", None),
    (["ovi_types", 0, "type"], "PHALASHRUTI", None),
    # --- Round 9 additions: enum coverage for events.closure ---
    (["events", 0, "closure"], "CONTINUES_NEXT_ADHYAY", None),
    (["events", 0, "closure"], "STARTED_EARLIER", None),
    (["events", 0, "closure"], "SOURCE_INCOMPLETE_OR_AMBIGUOUS", None),
    # --- Round 9 additions: minimum bounds for ovi (>=1) ---
    (["ovi_types", 0, "ovi"], 0, "ovi"),
    (["events", 0, "ovi_range", 0], 0, "ovi_range"),
    (["events", 0, "ovi_range", 1], 0, "ovi_range"),
    (["events", 0, "key_ovis", 0], 0, "key_ovis"),
    # --- Round 9 additions: minLength for events.title ---
    (["events", 0, "title"], "", "title"),
])
def test_schema_errors(path, value, keyword):
    doc = BASE_DOCS["story_map"]
    if path is not None:
        if value is ...:
            doc = delete_at(doc, path)
        else:
            doc = set_at(doc, path, value)
    errs = sm.schema_errors(doc)
    if keyword is None:
        assert errs == []
    else:
        assert any(keyword in e for e in errs), f"{keyword} not in {errs}"

# ---------- validate tests ----------
@pytest.mark.parametrize("adhyay,mutations,keywords", [
    # valid
    (1, [], []),
    # adhyay mismatch
    (2, [], ["adhyay", "does not match"]),
    # ovi untyped (delete first ovi_type)
    (1, [(["ovi_types", 0], ...)], ["ovi 1", "untyped"]),
    # ovi typed twice (append duplicate ovi 1)
    (1, [(["ovi_types"], {"ovi": 1, "type": "STORY"})], ["ovi 1", "typed twice"]),
    # ovi outside chapter (append ovi 99)
    (1, [(["ovi_types"], {"ovi": 99, "type": "STORY"})], ["ovi 99"]),
    # event ovi_range lo > hi (semantic, not schema) - isolate by clearing key_ovis
    (1, [(["events", 0, "ovi_range"], [5, 1]), (["events", 0, "key_ovis"], [])], ["E1"]),
    # key_ovis outside range (above)
    (1, [(["events", 0, "key_ovis"], [9])], ["E1"]),
    # key_ovis outside range (below)
    (1, [(["events", 0, "key_ovis"], [0])], ["E1"]),
    # empty events valid
    (1, [(["events"], [])], []),
    # empty ovi_types -> all untyped
    (1, [(["ovi_types"], [])], ["ovi 1", "untyped"]),
    # odd data: doc not a dict
    (1, [("__replace__", "not a dict")], ["doc"]),
    # odd data: ovi_types with non-dict item -> ovi 1 untyped
    (1, [(["ovi_types", 0], "not a dict")], ["ovi 1", "untyped"]),
    # odd data: ovi_range with non-int
    (1, [(["events", 0, "ovi_range"], ["a", 5])], []),
    # regression: ovi_types is null
    (1, [(["ovi_types"], None)], ["ovi 1", "untyped"]),
    # regression: events is null
    (1, [(["events"], None)], []),
    # regression: event key_ovis is null
    (1, [(["events", 0, "key_ovis"], None)], []),
    # regression: events is non-list
    (1, [(["events"], 5)], []),
    # regression: ovi_types is non-list
    (1, [(["ovi_types"], "not a list")], ["ovi 1", "untyped"]),
])
def test_validate(adhyay, mutations, keywords):
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    doc = docs["story_map"]
    for path, val in mutations:
        if path == "__replace__":
            doc = val
        elif val is ...:
            doc = delete_at(doc, path)
        elif isinstance(val, dict) and path and path[-1] == "ovi_types":
            doc = append_at(doc, path, val)
        else:
            doc = set_at(doc, path, val)
    errs = sm.validate(adhyay, doc, docs, ctx)
    if not keywords:
        assert errs == [], errs
    else:
        for kw in keywords:
            assert any(kw in e for e in errs), f"{kw} not in {errs}"
