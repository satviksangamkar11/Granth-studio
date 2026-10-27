from __future__ import annotations
import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SHOTS_PATH = ROOT / "scripts" / "pipeline" / "stage1" / "shots.py"
sys.path.insert(0, str(SHOTS_PATH.parent))
import shots  # type: ignore


def base() -> tuple[dict, dict]:
    docs = {
        "shots": {
            "adhyay": 1,
            "shots": [
                {
                    "shot_id": "S1-1",
                    "scene_id": "S1",
                    "ovi_ids": [1, 2],
                    "beat_line_ids": ["S1-L1"],
                    "preset": "01_establishing_shot",
                    "need_new": None,
                    "needs_cutout": False,
                    "pose": "standing",
                    "framing": "wide",
                },
                {
                    "shot_id": "S1-2",
                    "scene_id": "S1",
                    "ovi_ids": [3],
                    "beat_line_ids": ["S1-L2"],
                    "preset": "03_slow_cinematic_push",
                    "need_new": None,
                    "needs_cutout": False,
                    "pose": "seated",
                    "framing": "medium",
                },
                {
                    "shot_id": "S2-1",
                    "scene_id": "S2",
                    "ovi_ids": [6, 7],
                    "beat_line_ids": ["S2-L1"],
                    "preset": "03_slow_cinematic_push",
                    "need_new": None,
                    "needs_cutout": False,
                    "pose": "seated",
                    "framing": "close",
                },
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
    if value is ...:
        if isinstance(cur, list):
            del cur[int(last)]
        else:
            del cur[last]
    else:
        if last.isdigit():
            cur[int(last)] = value
        else:
            cur[last] = value
    return obj


class TestSchema:
    @pytest.mark.parametrize("path", [
        "adhyay",
        "shots",
    ])
    def test_required_top_level(self, path):
        docs, ctx = base()
        doc = mutate(docs["shots"], path, ...)
        errs = shots.schema_errors(doc)
        assert any(f"shots {path}" in e for e in errs)

    @pytest.mark.parametrize("idx,field", [
        (0, "shot_id"), (0, "scene_id"), (0, "ovi_ids"), (0, "beat_line_ids"),
        (0, "preset"), (0, "need_new"), (0, "needs_cutout"), (0, "pose"), (0, "framing"),
    ])
    def test_required_shot_fields(self, idx, field):
        docs, ctx = base()
        doc = mutate(docs["shots"], f"shots.{idx}.{field}", ...)
        errs = shots.schema_errors(doc)
        assert any(f"shots shots/{idx}/{field}" in e for e in errs)

    @pytest.mark.parametrize("idx,field,val", [
        (0, "shot_id", "X1-1"),
        (0, "scene_id", "X1"),
        (0, "ovi_ids", "not-array"),
        (0, "ovi_ids", [0]),
        (0, "ovi_ids", [1.5]),
        (0, "beat_line_ids", "not-array"),
        (0, "beat_line_ids", ["X1-L1"]),
        (0, "preset", 123),
        (0, "preset", "bad_preset"),
        (0, "need_new", "not-object"),
        (0, "need_new", {"reason": "x", "class": "bad_class"}),
        (0, "needs_cutout", "not-bool"),
        (0, "pose", ""),
        (0, "pose", "x" * 401),
        (0, "framing", ""),
        (0, "framing", "x" * 401),
    ])
    def test_shot_field_types_and_formats(self, idx, field, val):
        docs, ctx = base()
        doc = mutate(docs["shots"], f"shots.{idx}.{field}", val)
        errs = shots.schema_errors(doc)
        assert any(f"shots shots/{idx}/{field}" in e for e in errs)

    @pytest.mark.parametrize("idx,extra", [
        (0, "hint"),
        (0, "extra_field"),
    ])
    def test_shot_no_extra_keys(self, idx, extra):
        docs, ctx = base()
        doc = mutate(docs["shots"], f"shots.{idx}.{extra}", "x")
        errs = shots.schema_errors(doc)
        assert any(f"shots shots/{idx}/{extra}" in e for e in errs)

    def test_need_new_if_then_need_new_without_preset_need_new(self):
        docs, ctx = base()
        doc = mutate(docs["shots"], "shots.0.preset", "01_establishing_shot")
        doc = mutate(doc, "shots.0.need_new", {"reason": "r", "class": "missing_image"})
        errs = shots.schema_errors(doc)
        assert any("shots shots/0/need_new" in e for e in errs)

    def test_need_new_if_then_preset_need_new_requires_object(self):
        docs, ctx = base()
        doc = mutate(docs["shots"], "shots.0.preset", "NEED_NEW")
        doc = mutate(doc, "shots.0.need_new", None)
        errs = shots.schema_errors(doc)
        assert any("shots shots/0/need_new" in e for e in errs)

    def test_need_new_class_enum(self):
        docs, ctx = base()
        doc = mutate(docs["shots"], "shots.0.preset", "NEED_NEW")
        doc = mutate(doc, "shots.0.need_new", {"reason": "r", "class": "bad"})
        errs = shots.schema_errors(doc)
        assert any("shots shots/0/need_new/class" in e for e in errs)


class TestValidate:
    def test_positive(self):
        docs, ctx = base()
        errs = shots.validate(1, docs["shots"], docs, ctx)
        assert errs == []

    def test_adhyay_mismatch(self):
        docs, ctx = base()
        doc = mutate(docs["shots"], "adhyay", 2)
        errs = shots.validate(1, doc, docs, ctx)
        assert any("shots adhyay 1 does not match 2" in e for e in errs)

    @pytest.mark.parametrize("idx,val", [
        (0, "S1-1"),  # duplicate
        (1, "S1-3"),  # non-consecutive
    ])
    def test_shot_id_unique_consecutive(self, idx, val):
        docs, ctx = base()
        doc = mutate(docs["shots"], f"shots.{idx}.shot_id", val)
        errs = shots.validate(1, doc, docs, ctx)
        assert any("S1" in e and ("unique" in e or "consecutive" in e) for e in errs)

    def test_scene_exists(self):
        docs, ctx = base()
        doc = mutate(docs["shots"], "shots.0.scene_id", "S9")
        errs = shots.validate(1, doc, docs, ctx)
        assert any("S1-1" in e and "scene" in e for e in errs)

    def test_ovi_ids_in_scene_range(self):
        docs, ctx = base()
        doc = mutate(docs["shots"], "shots.0.ovi_ids", [10])
        errs = shots.validate(1, doc, docs, ctx)
        assert any("S1-1" in e and "ovi" in e for e in errs)

    def test_beat_line_ids_belong_to_scene(self):
        docs, ctx = base()
        doc = mutate(docs["shots"], "shots.0.beat_line_ids", ["S2-L1"])
        errs = shots.validate(1, doc, docs, ctx)
        assert any("S1-1" in e and "beat_line" in e for e in errs)

    def test_every_scene_has_shots(self):
        docs, ctx = base()
        doc = mutate(docs["shots"], "shots", [
            {"shot_id": "S1-1", "scene_id": "S1", "ovi_ids": [1], "beat_line_ids": ["S1-L1"],
             "preset": "01_establishing_shot", "need_new": None, "needs_cutout": False,
             "pose": "x", "framing": "x"},
        ])
        errs = shots.validate(1, doc, docs, ctx)
        assert any("S2" in e and "shot" in e for e in errs)

    def test_every_line_in_some_shot_beat(self):
        docs, ctx = base()
        doc = mutate(docs["shots"], "shots.0.beat_line_ids", [])
        errs = shots.validate(1, doc, docs, ctx)
        assert any("S1-L1" in e and "no shot beat" in e for e in errs)

    def test_unknown_preset(self):
        docs, ctx = base()
        doc = mutate(docs["shots"], "shots.0.preset", "99_unknown")
        errs = shots.validate(1, doc, docs, ctx)
        assert any("S1-1" in e and "unknown preset" in e for e in errs)

    def test_preset_need_new_allows_need_new_object(self):
        docs, ctx = base()
        doc = mutate(docs["shots"], "shots.0.preset", "NEED_NEW")
        doc = mutate(doc, "shots.0.need_new", {"reason": "need new", "class": "missing_image"})
        errs = shots.validate(1, doc, docs, ctx)
        assert errs == []

    def test_empty_context_missing_refs(self):
        docs, ctx = base()
        empty_ctx = {
            "script_line_ids": [], "core_line_ids": [], "chapter_ovis": [],
            "unfilmed_ovis": [], "preset_ids": [], "sound_ids": [],
            "saved_voices": {}, "speaking_characters": [], "known_states": {},
        }
        errs = shots.validate(1, docs["shots"], docs, empty_ctx)
        assert any("S1-L1" in e and "not in the script" in e for e in errs)
        assert any("01_establishing_shot" in e and "unknown preset" in e for e in errs)
