from __future__ import annotations
import copy
from pathlib import Path
import importlib.util
import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "pipeline" / "stage1" / "voices.py"

spec = importlib.util.spec_from_file_location("voices", MODULE_PATH)
voices = importlib.util.module_from_spec(spec)
spec.loader.exec_module(voices)

schema_errors = voices.schema_errors
validate = voices.validate


def base() -> dict:
    return {
        "docs": {
            "voices": {
                "adhyay": 1,
                "cast": [
                    {
                        "character_id": "narrator",
                        "voice_key": "narrator",
                        "voice_id": "CXkeo30p0Sk4Lr0TAzeo",
                        "gender": "male",
                        "status": "RECURRING",
                    },
                    {
                        "character_id": "gajanan_maharaj",
                        "voice_key": "gajanan",
                        "voice_id": "8fqGzH80bdkm2UseeV9f",
                        "gender": "male",
                        "status": "RECURRING",
                    },
                ],
            }
        },
        "ctx": {
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
        },
    }


def get_parent(doc: dict, path: list) -> tuple[object, object]:
    """Walk path (list of str/int) to parent of last element. Returns (parent, last_key)."""
    cur = doc
    for p in path[:-1]:
        cur = cur[p]
    return cur, path[-1]


def set_at(base: dict, path: list, value) -> dict:
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    if isinstance(parent, list):
        parent[key] = value
    else:
        parent[key] = value
    assert doc != base, "mutation had no effect"
    return doc


def delete_at(base: dict, path: list) -> dict:
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    if isinstance(parent, list):
        del parent[key]
    else:
        del parent[key]
    assert doc != base, "mutation had no effect"
    return doc


def append_at(base: dict, path: list, value) -> dict:
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    assert isinstance(parent, list), "append_at target must be list"
    parent.append(value)
    assert doc != base, "mutation had no effect"
    return doc


def mutate_doc(base: dict, path_str: str, value):
    """Mutate base['docs']['voices'] using dot path with int indexes."""
    parts = []
    for p in path_str.split("."):
        parts.append(int(p) if p.isdigit() else p)
    return set_at(base, ["docs", "voices"] + parts, value)


def mutate_ctx(base: dict, path_str: str, value):
    """Mutate base['ctx'] using dot path with int indexes."""
    parts = []
    for p in path_str.split("."):
        parts.append(int(p) if p.isdigit() else p)
    return set_at(base, ["ctx"] + parts, value)


def delete_doc(base: dict, path_str: str):
    parts = []
    for p in path_str.split("."):
        parts.append(int(p) if p.isdigit() else p)
    return delete_at(base, ["docs", "voices"] + parts)


def delete_ctx(base: dict, path_str: str):
    parts = []
    for p in path_str.split("."):
        parts.append(int(p) if p.isdigit() else p)
    return delete_at(base, ["ctx"] + parts)


def append_doc(base: dict, path_str: str, value):
    parts = []
    for p in path_str.split("."):
        parts.append(int(p) if p.isdigit() else p)
    return append_at(base, ["docs", "voices"] + parts, value)


@pytest.mark.parametrize("path,value,keyword", [
    (None, None, None),
    ("adhyay", None, "adhyay"),
    ("cast", None, "cast"),
    ("adhyay", "1", "adhyay"),
    ("adhyay", 0, "adhyay"),
    ("adhyay", 22, "adhyay"),
    ("cast", "x", "cast"),
    ("cast.0.character_id", None, "character_id"),
    ("cast.0.voice_key", None, "voice_key"),
    ("cast.0.voice_id", None, "voice_id"),
    ("cast.0.gender", None, "gender"),
    ("cast.0.status", None, "status"),
    ("cast.0.gender", "other", "gender"),
    ("cast.0.status", "INVALID", "status"),
    ("cast.0.voice_id", "short", "voice_id"),
    ("cast.0.voice_id", "x" * 41, "voice_id"),
    ("cast.0.extra", "field", "extra"),
    ("extra", "field", "extra"),
    # Required field deletion tests
    ("cast.0.character_id", "DELETE", "character_id"),
    ("cast.0.voice_key", "DELETE", "voice_key"),
    ("cast.0.voice_id", "DELETE", "voice_id"),
    ("cast.0.gender", "DELETE", "gender"),
    ("cast.0.status", "DELETE", "status"),
    # Schema-valid enum value tests (removing the enum value should fail these)
    ("cast.0.gender", "female", None),
    ("cast.0.status", "NEW_PROPOSED", None),
])
def test_schema(path, value, keyword):
    b = base()
    if path is None:
        assert schema_errors(b["docs"]["voices"]) == []
    else:
        if value == "DELETE":
            doc = delete_doc(b, path)
        else:
            doc = mutate_doc(b, path, value)
        errs = schema_errors(doc["docs"]["voices"])
        if keyword is None:
            assert errs == []
        else:
            assert errs
            assert any(keyword in e for e in errs)


@pytest.mark.parametrize("path,value,keyword", [
    (None, None, None),
    ("adhyay", 2, "adhyay"),
    # Remove cast entry for narrator -> no voice assigned
    ("cast.0", None, "narrator"),
    # Remove cast entry for gajanan_maharaj -> no voice assigned
    ("cast.1", None, "gajanan_maharaj"),
    ("cast.0.voice_key", "unknown", "narrator"),
    # Use valid-length but wrong voice_id
    ("cast.0.voice_id", "x" * 10, "narrator"),
    # Duplicate narrator entry (RECURRING listed twice)
    ("cast", [
        {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
        {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
        {"character_id": "gajanan_maharaj", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "male", "status": "RECURRING"},
    ], "narrator"),
    # Two non-narrators sharing a voice_key (gajanan) -> forbidden
    ("cast", [
        {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
        {"character_id": "gajanan_maharaj", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "male", "status": "RECURRING"},
        {"character_id": "extra_char", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "female", "status": "NEW_PROPOSED"},
    ], "extra_char"),
    # Another case: two non-narrators sharing a voice_key
    ("cast", [
        {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
        {"character_id": "char1", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "male", "status": "NEW_PROPOSED"},
        {"character_id": "char2", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "female", "status": "NEW_PROPOSED"},
    ], "char1"),
    # Two NEW_PROPOSED entries for same speaking character
    ("cast", [
        {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
        {"character_id": "gajanan_maharaj", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "male", "status": "NEW_PROPOSED"},
        {"character_id": "gajanan_maharaj", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "male", "status": "NEW_PROPOSED"},
    ], "gajanan_maharaj"),
    # Narrator and two others sharing a saved key - should error for the two non-narrators
    ("cast", [
        {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
        {"character_id": "charA", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "NEW_PROPOSED"},
        {"character_id": "charB", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "female", "status": "NEW_PROPOSED"},
    ], "charA"),
    ("ctx.speaking_characters", [], None),
    # Odd data: cast is not a list
    ("cast", "not a list", "cast"),
    # Odd data: cast contains non-dict entries
    ("cast", [{"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"}, "not a dict"], "cast"),
    # Odd data: cast contains entry with non-string character_id
    ("cast", [{"character_id": 123, "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"}], "character_id"),
    # Odd data: cast contains entry with non-string voice_key
    ("cast", [{"character_id": "narrator", "voice_key": 123, "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"}], "voice_key"),
    # Odd data: doc is not a dict
    ("__doc__", None, "doc"),
    # Odd data: doc is a list
    ("__doc__", [1, 2, 3], "doc"),
])
def test_validate(path, value, keyword):
    b = base()
    if path is None:
        assert validate(1, b["docs"]["voices"], b["docs"], b["ctx"]) == []
    elif path.startswith("ctx."):
        doc = mutate_ctx(b, path[4:], value)
        errs = validate(1, doc["docs"]["voices"], doc["docs"], doc["ctx"])
        if keyword is None:
            assert errs == []
        else:
            assert errs
            assert any(keyword in e for e in errs)
    elif path == "__doc__":
        # Special case: replace the whole doc
        if value is None:
            test_doc = None
        else:
            test_doc = value
        errs = validate(1, test_doc, b["docs"], b["ctx"])
        if keyword is None:
            assert errs == []
        else:
            assert errs
            assert any(keyword in e for e in errs)
    else:
        if value == "DELETE":
            doc = delete_doc(b, path)
        else:
            doc = mutate_doc(b, path, value)
        errs = validate(1, doc["docs"]["voices"], doc["docs"], doc["ctx"])
        if keyword is None:
            assert errs == []
        else:
            assert errs
            assert any(keyword in e for e in errs)


def test_validate_recurring_duplicate_isolated():
    """Test that recurring character listed twice is detected without collateral shared-key errors."""
    b = base()
    # Extend saved_voices with a unique key for other_char
    ctx = copy.deepcopy(b["ctx"])
    ctx["saved_voices"] = dict(ctx["saved_voices"])
    ctx["saved_voices"]["other"] = "ZZZZZZZZZZ"
    doc = {
        "adhyay": 1,
        "cast": [
            {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
            {"character_id": "gajanan_maharaj", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "male", "status": "RECURRING"},
            {"character_id": "other_char", "voice_key": "other", "voice_id": "ZZZZZZZZZZ", "gender": "male", "status": "RECURRING"},
            {"character_id": "other_char", "voice_key": "other", "voice_id": "ZZZZZZZZZZ", "gender": "male", "status": "RECURRING"},
        ],
    }
    errs = validate(1, doc, b["docs"], ctx)
    # Should only have the recurring duplicate error for other_char
    assert any("other_char" in e for e in errs)


def test_validate_recurring_newproposed_duplicate_isolated():
    """Test that non-speaking RECURRING + NEW_PROPOSED duplicate is detected without collateral shared-key errors."""
    b = base()
    # Extend saved_voices with a unique key for other_char
    ctx = copy.deepcopy(b["ctx"])
    ctx["saved_voices"] = dict(ctx["saved_voices"])
    ctx["saved_voices"]["other"] = "ZZZZZZZZZZ"
    doc = {
        "adhyay": 1,
        "cast": [
            {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
            {"character_id": "gajanan_maharaj", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "male", "status": "RECURRING"},
            {"character_id": "other_char", "voice_key": "other", "voice_id": "ZZZZZZZZZZ", "gender": "male", "status": "RECURRING"},
            {"character_id": "other_char", "voice_key": "other", "voice_id": "ZZZZZZZZZZ", "gender": "male", "status": "NEW_PROPOSED"},
        ],
    }
    errs = validate(1, doc, b["docs"], ctx)
    # Should only have the recurring duplicate error for other_char
    assert any("other_char" in e for e in errs)
