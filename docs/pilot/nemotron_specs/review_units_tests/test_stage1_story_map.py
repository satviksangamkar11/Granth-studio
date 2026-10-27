from __future__ import annotations
import copy
import json
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "pipeline" / "stage1"))
import story_map as sm

def base() -> tuple[dict, dict]:
    docs = {
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
    """Set or delete a single item at dot/path. Returns mutated copy."""
    obj = copy.deepcopy(obj)
    parts = path.split(".")
    cur = obj
    for p in parts[:-1]:
        if p.isdigit():
            cur = cur[int(p)]
        else:
            cur = cur[p]
    last = parts[-1]
    if value is __import__("builtins").Ellipsis:
        if last.isdigit():
            del cur[int(last)]
        else:
            del cur[last]
    else:
        if last.isdigit():
            cur[int(last)] = value
        else:
            cur[last] = value
    return obj

# ---------- schema_errors tests ----------
@pytest.mark.parametrize("path,value,keyword", [
    # valid
    (None, None, None),
    # missing required top-level
    ("adhyay", ..., "adhyay"),
    ("ovi_types", ..., "ovi_types"),
    ("events", ..., "events"),
    # extra top-level key
    ("extra", 1, "extra"),
    # adhyay range
    ("adhyay", 0, "adhyay"),
    ("adhyay", 22, "adhyay"),
    # ovi_types items
    ("ovi_types.0.ovi", ..., "ovi"),
    ("ovi_types.0.type", ..., "type"),
    ("ovi_types.0.type", "INVALID", "type"),
    ("ovi_types.0.extra", 1, "extra"),
    ("ovi_types.0.ovi", "x", "ovi"),
    # events items
    ("events.0.event_id", ..., "event_id"),
    ("events.0.title", ..., "title"),
    ("events.0.ovi_range", ..., "ovi_range"),
    ("events.0.key_ovis", ..., "key_ovis"),
    ("events.0.kind", ..., "kind"),
    ("events.0.closure", ..., "closure"),
    ("events.0.event_id", "X1", "event_id"),
    ("events.0.kind", "invalid", "kind"),
    ("events.0.closure", "INVALID", "closure"),
    ("events.0.ovi_range", [5, 1], "ovi_range"),
    ("events.0.ovi_range", [1], "ovi_range"),
    ("events.0.extra", 1, "extra"),
])
def test_schema_errors(path, value, keyword):
    docs, ctx = base()
    if path is None:
        doc = docs["story_map"]
    else:
        doc = mutate(docs["story_map"], path, value)
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
    # ovi untyped
    (1, [("ovi_types.0", ...)], ["ovi 1", "untyped"]),
    # ovi typed twice
    (1, [("ovi_types.9", {"ovi": 1, "type": "STORY"})], ["ovi 1", "typed twice"]),
    # ovi outside chapter
    (1, [("ovi_types.9", {"ovi": 99, "type": "STORY"})], ["ovi 99", "outside"]),
    # event ovi_range lo > hi
    (1, [("events.0.ovi_range", [5, 1])], ["E1", "ovi_range"]),
    # key_ovis outside range
    (1, [("events.0.key_ovis", [9])], ["E1", "key_ovis", "outside"]),
    # empty events valid
    (1, [("events", [])], []),
    # empty ovi_types -> all untyped
    (1, [("ovi_types", [])], ["ovi 1", "untyped"]),
])
def test_validate(adhyay, mutations, keywords):
    docs, ctx = base()
    doc = docs["story_map"]
    for path, val in mutations:
        doc = mutate(doc, path, val)
    errs = sm.validate(adhyay, doc, docs, ctx)
    if not keywords:
        assert errs == [], errs
    else:
        for kw in keywords:
            assert any(kw in e for e in errs), f"{kw} not in {errs}"
