from __future__ import annotations
import copy
import importlib.util
import json
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


def base() -> tuple[dict, dict]:
    docs = {
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
    ctx = {
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
    return copy.deepcopy(docs), copy.deepcopy(ctx)


def mutate(obj: dict, path: str, value):
    """Set or delete a single item by dot-path (e.g. 'cues.0.sound_id')."""
    parts = path.split(".")
    cur = obj
    for p in parts[:-1]:
        cur = cur[int(p)] if p.isdigit() else cur[p]
    last = parts[-1]
    if value is None:
        cur.pop(last, None)
    else:
        cur[last] = value


@pytest.mark.parametrize(
    "path,value,keyword",
    [
        # required fields
        ("adhyay", None, "adhyay"),
        ("cues", None, "cues"),
        ("cues.0.scene_id", None, "scene_id"),
        ("cues.0.anchor_line_id", None, "anchor_line_id"),
        ("cues.0.sound_id", None, "sound_id"),
        ("cues.0.kind", None, "kind"),
        ("cues.0.purpose", None, "purpose"),
        ("cues.0.basis", None, "basis"),
        # type / pattern
        ("adhyay", "x", "adhyay"),
        ("cues.0.scene_id", "X1", "scene_id"),
        ("cues.0.anchor_line_id", "S1-X", "anchor_line_id"),
        ("cues.0.sound_id", "bad_id", "sound_id"),
        ("cues.0.kind", "music", "kind"),
        ("cues.0.purpose", "", "purpose"),
        ("cues.0.basis", "guess", "basis"),
        # enum invalid
        ("cues.0.kind", "bed", None),  # valid
        ("cues.0.kind", "fx", None),  # valid
        ("cues.0.basis", "stated", None),  # valid
        ("cues.0.basis", "staging", None),  # valid
        # extra keys
        ("cues.0.extra", 1, "extra"),
        ("extra_top", 1, "extra_top"),
        # NEED_NEW + sound_prompt rules (schema level)
        ("cues.0.sound_id", "NEED_NEW", None),
        ("cues.0.sound_prompt", "a prompt", "sound_prompt"),  # extra on non-NEED_NEW
    ],
)
def test_schema_errors(path, value, keyword):
    docs, _ = base()
    doc = copy.deepcopy(docs["sounds"])
    if path == "extra_top":
        doc["extra_top"] = 1
    else:
        mutate(doc, path, value)
    errs = schema_errors(doc)
    if keyword is None:
        assert errs == []
    else:
        assert any(keyword in e for e in errs), f"{keyword} not in {errs}"


@pytest.mark.parametrize(
    "path,value,keyword",
    [
        # adhyay mismatch
        ("adhyay", 2, "adhyay"),
        # scene missing
        ("cues.0.scene_id", "S9", "scene"),
        # anchor line not in scene
        ("cues.0.anchor_line_id", "S2-L1", "anchor_line_id"),
        # sound_id not in sound_ids and not NEED_NEW
        ("cues.0.sound_id", "bed_unknown", "sound_id"),
        # kind mismatch prefix
        ("cues.0.kind", "fx", "kind"),
        ("cues.0.sound_id", "fx_door_wood_creak", None),  # valid fx
        ("cues.0.kind", "bed", "kind"),  # mismatch after change
        # NEED_NEW without sound_prompt is schema error, but semantic sees NEED_NEW ok
        ("cues.0.sound_id", "NEED_NEW", None),
        ("cues.0.sound_prompt", "new bed", None),  # valid with prompt
    ],
)
def test_semantic_errors(path, value, keyword):
    docs, ctx = base()
    doc = copy.deepcopy(docs["sounds"])
    mutate(doc, path, value)
    errs = validate(1, doc, docs, ctx)
    if keyword is None:
        assert errs == []
    else:
        assert any(keyword in e for e in errs), f"{keyword} not in {errs}"


def test_valid_returns_empty():
    docs, ctx = base()
    assert schema_errors(docs["sounds"]) == []
    assert validate(1, docs["sounds"], docs, ctx) == []


def test_empty_context_missing_refs():
    docs, _ = base()
    doc = copy.deepcopy(docs["sounds"])
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
    errs = validate(1, doc, docs, ctx)
    assert any("S1-L1" in e and "line is not in the script" in e for e in errs)
    assert any("bed_roadside_quiet" in e and "sound_id" in e for e in errs)
