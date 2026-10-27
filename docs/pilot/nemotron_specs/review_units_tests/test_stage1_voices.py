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


def mutate(base: dict, path: str, value) -> dict:
    doc = copy.deepcopy(base)
    parts = path.split(".")
    target = doc
    for part in parts[:-1]:
        target = target[int(part)] if part.isdigit() else target[part]
    last = parts[-1]
    if value is None:
        if isinstance(target, list) and last.isdigit():
            del target[int(last)]
        else:
            del target[last]
    else:
        if isinstance(target, list) and last.isdigit():
            target[int(last)] = value
        else:
            target[last] = value
    return doc


@pytest.mark.parametrize("path,value,keyword", [
    (None, None, None),
    ("docs.voices.adhyay", None, "adhyay"),
    ("docs.voices.cast", None, "cast"),
    ("docs.voices.adhyay", "1", "adhyay"),
    ("docs.voices.adhyay", 0, "adhyay"),
    ("docs.voices.adhyay", 22, "adhyay"),
    ("docs.voices.cast", "x", "cast"),
    ("docs.voices.cast.0.character_id", None, "character_id"),
    ("docs.voices.cast.0.voice_key", None, "voice_key"),
    ("docs.voices.cast.0.voice_id", None, "voice_id"),
    ("docs.voices.cast.0.gender", None, "gender"),
    ("docs.voices.cast.0.status", None, "status"),
    ("docs.voices.cast.0.gender", "other", "gender"),
    ("docs.voices.cast.0.status", "INVALID", "status"),
    ("docs.voices.cast.0.voice_id", "short", "voice_id"),
    ("docs.voices.cast.0.voice_id", "x" * 41, "voice_id"),
    ("docs.voices.cast.0.extra", "field", "extra"),
    ("docs.voices.extra", "field", "extra"),
])
def test_schema(path, value, keyword):
    b = base()
    if path is None:
        assert schema_errors(b["docs"]["voices"]) == []
    else:
        doc = mutate(b, path, value)
        errs = schema_errors(doc["docs"]["voices"])
        assert errs
        assert any(keyword in e for e in errs)


@pytest.mark.parametrize("path,value,keyword", [
    (None, None, None),
    ("docs.voices.adhyay", 2, "adhyay"),
    ("docs.voices.cast.0", None, "narrator: no voice assigned"),
    ("docs.voices.cast.1", None, "gajanan_maharaj: no voice assigned"),
    ("docs.voices.cast.0.voice_key", "unknown", "narrator: voice not in the saved cast"),
    ("docs.voices.cast.0.voice_id", "wrong", "narrator: voice not in the saved cast"),
    ("docs.voices.cast", [
        {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
        {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
        {"character_id": "gajanan_maharaj", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "male", "status": "RECURRING"},
    ], "narrator: duplicate RECURRING character"),
    ("docs.voices.cast", [
        {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
        {"character_id": "gajanan_maharaj", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
    ], "gajanan_maharaj: voice_key shared with another character"),
    ("docs.voices.cast", [
        {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
        {"character_id": "gajanan_maharaj", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
    ], None),
    ("docs.ctx.speaking_characters", [], None),
    ("docs.voices.cast", [
        {"character_id": "narrator", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "male", "status": "RECURRING"},
        {"character_id": "gajanan_maharaj", "voice_key": "gajanan", "voice_id": "8fqGzH80bdkm2UseeV9f", "gender": "male", "status": "RECURRING"},
        {"character_id": "extra_char", "voice_key": "narrator", "voice_id": "CXkeo30p0Sk4Lr0TAzeo", "gender": "female", "status": "NEW_PROPOSED"},
    ], None),
])
def test_validate(path, value, keyword):
    b = base()
    if path is None:
        assert validate(1, b["docs"]["voices"], b["docs"], b["ctx"]) == []
    else:
        doc = mutate(b, path, value)
        errs = validate(1, doc["docs"]["voices"], doc["docs"], doc["ctx"])
        if keyword is None:
            assert errs == []
        else:
            assert errs
            assert any(keyword in e for e in errs)
