from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# Load validate_stage1 module by path
spec = importlib.util.spec_from_file_location(
    "validate_stage1", ROOT / "scripts" / "pipeline" / "validate_stage1.py"
)
validate_stage1_mod = importlib.util.module_from_spec(spec)
sys.modules["validate_stage1"] = validate_stage1_mod
spec.loader.exec_module(validate_stage1_mod)

validate_stage1 = validate_stage1_mod.validate_stage1


def make_ctx(
    *,
    script_line_ids=None,
    core_line_ids=None,
    chapter_ovis=None,
    unfilmed_ovis=None,
    preset_ids=None,
    sound_ids=None,
    saved_voices=None,
    speaking_characters=None,
    known_entities=None,
):
    return {
        "script_line_ids": script_line_ids or ["S1-L1", "S1-L2", "S2-L1"],
        "core_line_ids": core_line_ids or {"S1-L1", "S2-L1"},
        "chapter_ovis": chapter_ovis or {1, 2, 3, 4, 5},
        "unfilmed_ovis": unfilmed_ovis or set(),
        "preset_ids": preset_ids or {"01_wide", "02_medium", "03_close"},
        "sound_ids": sound_ids or {"bed_battlefield", "fx_conch"},
        "saved_voices": saved_voices or {"arjuna_voice": "v_arjuna_001", "krishna_voice": "v_krishna_001"},
        "speaking_characters": speaking_characters or {"arjuna", "krishna"},
        "known_entities": known_entities or {"arjuna", "krishna", "battlefield"},
    }


def make_valid_docs(adhyay=1):
    """Return a fully valid set of nine documents for the given adhyay."""
    return {
        "story_map": {
            "adhyay": adhyay,
            "ovi_types": [
                {"ovi": 1, "type": "STORY"},
                {"ovi": 2, "type": "TEACHING"},
                {"ovi": 3, "type": "PHILOSOPHY"},
                {"ovi": 4, "type": "INVOCATION"},
                {"ovi": 5, "type": "RECAP"},
            ],
            "events": [
                {
                    "event_id": "E1",
                    "title": "Opening",
                    "ovi_range": [1, 2],
                    "key_ovis": [1],
                    "kind": "story",
                    "closure": "RESOLVED_IN_ADHYAY",
                },
                {
                    "event_id": "E2",
                    "title": "Teaching",
                    "ovi_range": [3, 5],
                    "key_ovis": [3, 4],
                    "kind": "discourse",
                    "closure": "RESOLVED_IN_ADHYAY",
                },
            ],
        },
        "coverage": {
            "adhyay": adhyay,
            "ovis": [
                {"ovi": 1, "disposition": "VISUALISED"},
                {"ovi": 2, "disposition": "NARRATED"},
                {"ovi": 3, "disposition": "QUOTED"},
                {"ovi": 4, "disposition": "MERGED_EQUIVALENT", "reason": "same as 3", "covered_by": 3},
                {"ovi": 5, "disposition": "PROPOSE_OMISSION", "reason": "redundant"},
            ],
        },
        "scenes": {
            "adhyay": adhyay,
            "scenes": [
                {
                    "scene_id": "S1",
                    "section_kind": "story",
                    "ovi_range": [1, 2],
                    "goal": "Setup",
                    "turn": {"ovi": 1, "text": "Arjuna sees armies"},
                    "line_ids": ["S1-L1", "S1-L2"],
                    "teaching_treatment": "none",
                },
                {
                    "scene_id": "S2",
                    "section_kind": "discourse",
                    "ovi_range": [3, 5],
                    "goal": "Teaching",
                    "turn": {"ovi": 3, "text": "Krishna speaks"},
                    "line_ids": ["S2-L1"],
                    "teaching_treatment": "contemplative_hold",
                },
            ],
        },
        "shots": {
            "adhyay": adhyay,
            "shots": [
                {
                    "shot_id": "S1-1",
                    "scene_id": "S1",
                    "ovi_ids": [1],
                    "beat_line_ids": ["S1-L1"],
                    "preset": "01_wide",
                    "need_new": None,
                    "needs_cutout": False,
                    "pose": "standing",
                    "framing": "wide",
                },
                {
                    "shot_id": "S1-2",
                    "scene_id": "S1",
                    "ovi_ids": [2],
                    "beat_line_ids": ["S1-L2"],
                    "preset": "02_medium",
                    "need_new": None,
                    "needs_cutout": False,
                    "pose": "kneeling",
                    "framing": "medium",
                },
                {
                    "shot_id": "S2-1",
                    "scene_id": "S2",
                    "ovi_ids": [3, 4, 5],
                    "beat_line_ids": ["S2-L1"],
                    "preset": "03_close",
                    "need_new": None,
                    "needs_cutout": True,
                    "pose": "seated",
                    "framing": "close",
                },
            ],
        },
        "briefs": {
            "adhyay": adhyay,
            "images": [
                {
                    "image_id": "s1_arjuna_standing",
                    "scene_id": "S1",
                    "shot_ids": ["S1-1"],
                    "people": [
                        {"name": "Arjuna", "position": "center", "pose": "standing", "gaze": "forward"}
                    ],
                    "place_id": "battlefield",
                    "prop": "bow",
                    "prop_state": "strung",
                    "camera": "eye level",
                    "light": "harsh noon",
                    "reason_new": "first shot",
                    "on_screen_facts": ["Arjuna stands", "bow visible"],
                    "references": {
                        "characters": ["Arjuna"],
                        "place": "battlefield",
                        "style_anchor": "epic realism",
                        "prop": "bow",
                    },
                },
                {
                    "image_id": "s2_krishna_seated",
                    "scene_id": "S2",
                    "shot_ids": ["S2-1"],
                    "people": [
                        {"name": "Krishna", "position": "center", "pose": "seated", "gaze": "at Arjuna"}
                    ],
                    "place_id": "chariot",
                    "prop": None,
                    "prop_state": None,
                    "camera": "low angle",
                    "light": "divine glow",
                    "reason_new": "teaching moment",
                    "on_screen_facts": ["Krishna seated", "chariot interior"],
                    "references": {
                        "characters": ["Krishna"],
                        "place": "chariot",
                        "style_anchor": "epic realism",
                        "prop": None,
                    },
                },
            ],
        },
        "looks": {
            "adhyay": adhyay,
            "entries": [
                {
                    "entity_id": "arjuna",
                    "kind": "character",
                    "state_id": "battle_ready",
                    "look": "armored, bow in hand",
                    "source_ovis": [1, 2],
                    "basis": "stated",
                },
                {
                    "entity_id": "krishna",
                    "kind": "character",
                    "state_id": "charioteer",
                    "look": "peacock feather, yellow garment",
                    "source_ovis": [3, 4, 5],
                    "basis": "stated",
                },
                {
                    "entity_id": "battlefield",
                    "kind": "place",
                    "state_id": "dawn_armies",
                    "look": "two armies arrayed",
                    "source_ovis": [1],
                    "basis": "stated",
                },
            ],
        },
        "voices": {
            "adhyay": adhyay,
            "cast": [
                {
                    "character_id": "arjuna",
                    "voice_key": "arjuna_voice",
                    "voice_id": "v_arjuna_001",
                    "gender": "male",
                    "status": "RECURRING",
                },
                {
                    "character_id": "krishna",
                    "voice_key": "krishna_voice",
                    "voice_id": "v_krishna_001",
                    "gender": "male",
                    "status": "RECURRING",
                },
            ],
        },
        "sounds": {
            "adhyay": adhyay,
            "cues": [
                {
                    "scene_id": "S1",
                    "anchor_line_id": "S1-L1",
                    "sound_id": "bed_battlefield",
                    "kind": "bed",
                    "purpose": "ambience",
                    "basis": "staging",
                },
                {
                    "scene_id": "S2",
                    "anchor_line_id": "S2-L1",
                    "sound_id": "fx_conch",
                    "kind": "fx",
                    "purpose": "signal start",
                    "basis": "stated",
                },
            ],
        },
        "questions": {
            "adhyay": adhyay,
            "questions": [
                {"id": "Q1", "text": "Why does Arjuna hesitate?", "scene_id": "S1"},
                {"id": "Q2", "text": "What is the nature of the self?"},
            ],
        },
    }


class TestValidateStage1:
    def test_fully_valid_returns_empty(self):
        docs = make_valid_docs(1)
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert errs == [], f"expected no errors, got: {errs}"

    def test_schema_error_stops_early(self):
        # Invalid story_map (missing required field)
        docs = make_valid_docs(1)
        docs["story_map"] = {"adhyay": 1, "ovi_types": [], "events": []}
        # Remove required ovi_types entries to trigger schema error
        docs["story_map"]["ovi_types"] = [{"ovi": 1}]  # missing type
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        # Should have schema errors and stop
        assert any("story_map" in e and "type" in e for e in errs)
        # Should not proceed to semantic checks
        assert not any("adhyay" in e and "does not match" in e for e in errs)

    def test_adhyay_mismatch_in_document(self):
        docs = make_valid_docs(1)
        docs["coverage"]["adhyay"] = 2
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("coverage adhyay 2 does not match 1" in e for e in errs)

    # --- Story map semantic tests ---
    def test_ovi_untyped(self):
        docs = make_valid_docs(1)
        docs["story_map"]["ovi_types"] = [{"ovi": 1, "type": "STORY"}]  # missing 2-5
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi 2 is untyped" in e for e in errs)
        assert any("ovi 3 is untyped" in e for e in errs)

    def test_ovi_typed_twice(self):
        docs = make_valid_docs(1)
        docs["story_map"]["ovi_types"] = [
            {"ovi": 1, "type": "STORY"},
            {"ovi": 1, "type": "TEACHING"},
            {"ovi": 2, "type": "TEACHING"},
            {"ovi": 3, "type": "PHILOSOPHY"},
            {"ovi": 4, "type": "INVOCATION"},
            {"ovi": 5, "type": "RECAP"},
        ]
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi 1 is typed twice" in e for e in errs)

    def test_typed_ovi_outside_chapter_reported(self):
        docs = make_valid_docs(1)
        docs["story_map"]["ovi_types"].append({"ovi": 99, "type": "STORY"})
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi 99" in e and "outside" in e for e in errs)

    def test_event_ovi_range_invalid(self):
        docs = make_valid_docs(1)
        docs["story_map"]["events"][0]["ovi_range"] = [5, 1]  # lo > hi
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi_range" in e and ("lo" in e or "high" in e or "order" in e) for e in errs)

    def test_event_key_ovis_outside_range(self):
        docs = make_valid_docs(1)
        docs["story_map"]["events"][0]["key_ovis"] = [99]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("key_ovis" in e and "range" in e for e in errs)

    # --- Coverage semantic tests ---
    def test_coverage_missing_disposition(self):
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"] = [{"ovi": 1, "disposition": "VISUALISED"}]  # missing 2-5
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi 2 has no disposition" in e for e in errs)

    def test_coverage_duplicate_disposition(self):
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"] = [
            {"ovi": 1, "disposition": "VISUALISED"},
            {"ovi": 1, "disposition": "NARRATED"},
            {"ovi": 2, "disposition": "NARRATED"},
            {"ovi": 3, "disposition": "QUOTED"},
            {"ovi": 4, "disposition": "MERGED_EQUIVALENT", "reason": "r", "covered_by": 3},
            {"ovi": 5, "disposition": "PROPOSE_OMISSION", "reason": "r"},
        ]
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi 1" in e and "twice" in e for e in errs)

    def test_propose_omission_note(self):
        docs = make_valid_docs(1)
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        # PROPOSE_OMISSION for ovi 5 should produce a note
        assert any("note: ovi 5 omission proposed, owner approval needed" in e for e in errs)

    def test_unfilmed_ovi_visualised_error(self):
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"][0]["disposition"] = "VISUALISED"  # ovi 1
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5}, unfilmed_ovis={1})
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi 1 is unfilmed but VISUALISED" in e for e in errs)

    def test_covered_by_invalid_reference(self):
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"][3]["covered_by"] = "INVALID-LINE"
        ctx = make_ctx(script_line_ids=["S1-L1"], chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        assert any("covered_by" in e and ("INVALID-LINE" in e or "invalid" in e.lower()) for e in errs)

    # --- Scenes semantic tests ---
    def test_scene_ids_unique(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"].append(
            {
                "scene_id": "S1",
                "section_kind": "story",
                "ovi_range": [3, 3],
                "goal": "dup",
                "turn": {"ovi": 3, "text": "x"},
                "line_ids": [],
                "teaching_treatment": "none",
            }
        )
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("scene" in e.lower() and "duplicate" in e.lower() for e in errs)

    def test_scene_range_order(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][0]["ovi_range"] = [3, 1]  # lo > hi
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi_range" in e and ("order" in e or "lo" in e or "high" in e) for e in errs)

    def test_scene_ranges_overlap(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][1]["ovi_range"] = [2, 4]  # overlaps with S1 [1,2]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("overlap" in e.lower() for e in errs)

    def test_chapter_ovi_not_in_any_scene(self):
        docs = make_valid_docs(1)
        # S1 covers 1-2, S2 covers 3-5, but chapter has 6
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5, 6})
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi 6" in e and ("not in any scene" in e or "uncovered" in e.lower()) for e in errs)

    def test_unfilmed_ovi_inside_scene_range_error(self):
        docs = make_valid_docs(1)
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5}, unfilmed_ovis={2})
        # S1 covers 1-2, ovi 2 is unfilmed but inside range
        errs = validate_stage1(1, docs, ctx)
        assert any("S1" in e and "ovi 2 is unfilmed but inside the range" in e for e in errs)

    def test_ovi_outside_chapter_in_scene(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][0]["ovi_range"] = [1, 99]
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi 99" in e and "outside" in e for e in errs)

    def test_turn_ovi_outside_scene_range(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][0]["turn"]["ovi"] = 99
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("turn" in e and "ovi" in e and "range" in e for e in errs)

    def test_line_id_not_in_script(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][0]["line_ids"] = ["S1-L99"]
        ctx = make_ctx(script_line_ids=["S1-L1"])
        errs = validate_stage1(1, docs, ctx)
        assert any("S1-L99" in e and ("not in script" in e or "unknown" in e.lower()) for e in errs)

    def test_line_id_used_twice_across_scenes(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][1]["line_ids"] = ["S1-L1"]  # already in S1
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S1-L1" in e and ("twice" in e or "duplicate" in e.lower()) for e in errs)

    def test_line_ids_not_in_script_order_within_scene(self):
        docs = make_valid_docs(1)
        # Script order: S1-L1, S1-L2, S2-L1
        # Scene S1 uses L2 then L1 (wrong order)
        docs["scenes"]["scenes"][0]["line_ids"] = ["S1-L2", "S1-L1"]
        ctx = make_ctx(script_line_ids=["S1-L1", "S1-L2", "S2-L1"])
        errs = validate_stage1(1, docs, ctx)
        assert any("order" in e.lower() and "S1" in e for e in errs)

    def test_core_line_missing_from_scenes(self):
        docs = make_valid_docs(1)
        # S2-L1 is core but not in any scene
        docs["scenes"]["scenes"][1]["line_ids"] = []
        ctx = make_ctx(core_line_ids={"S1-L1", "S2-L1"})
        errs = validate_stage1(1, docs, ctx)
        assert any("S2-L1" in e and ("core" in e.lower() and "missing" in e.lower() or "not in any scene" in e) for e in errs)

    def test_discourse_scene_requires_treatment(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][1]["teaching_treatment"] = "none"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("discourse" in e.lower() and "teaching_treatment" in e for e in errs)

    # --- Shots semantic tests ---
    def test_shot_ids_unique_and_consecutive(self):
        docs = make_valid_docs(1)
        # Duplicate shot id
        docs["shots"]["shots"].append(
            {
                "shot_id": "S1-1",
                "scene_id": "S1",
                "ovi_ids": [1],
                "beat_line_ids": ["S1-L1"],
                "preset": "01_wide",
                "need_new": None,
                "needs_cutout": False,
                "pose": "x",
                "framing": "x",
            }
        )
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("shot" in e.lower() and "duplicate" in e.lower() for e in errs)

    def test_shot_not_consecutive(self):
        docs = make_valid_docs(1)
        docs["shots"]["shots"][1]["shot_id"] = "S1-3"  # skip S1-2
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("consecutive" in e.lower() or "sequence" in e.lower() for e in errs)

    def test_shot_scene_not_exist(self):
        docs = make_valid_docs(1)
        docs["shots"]["shots"][0]["scene_id"] = "S99"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S99" in e and ("scene" in e and "not exist" in e or "unknown" in e.lower()) for e in errs)

    def test_shot_ovi_ids_outside_scene_range(self):
        docs = make_valid_docs(1)
        docs["shots"]["shots"][0]["ovi_ids"] = [99]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi" in e and "99" in e and ("range" in e or "scene" in e) for e in errs)

    def test_shot_beat_line_ids_not_in_scene(self):
        docs = make_valid_docs(1)
        docs["shots"]["shots"][0]["beat_line_ids"] = ["S2-L1"]  # belongs to S2
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("beat_line_ids" in e and ("scene" in e or "not belong" in e) for e in errs)

    def test_scene_with_no_shots(self):
        docs = make_valid_docs(1)
        docs["shots"]["shots"] = [s for s in docs["shots"]["shots"] if s["scene_id"] != "S2"]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S2" in e and ("no shots" in e or "has no shots" in e) for e in errs)

    def test_line_not_in_any_shot_beat(self):
        docs = make_valid_docs(1)
        # S1-L2 is in scene S1 but not in any shot's beat_line_ids
        docs["shots"]["shots"] = [s for s in docs["shots"]["shots"] if s["shot_id"] != "S1-2"]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S1-L2" in e and "line is in no shot beat" in e for e in errs)

    def test_shot_unknown_preset(self):
        docs = make_valid_docs(1)
        docs["shots"]["shots"][0]["preset"] = "99_unknown"
        ctx = make_ctx(preset_ids={"01_wide"})
        errs = validate_stage1(1, docs, ctx)
        assert any("unknown preset" in e and "99_unknown" in e for e in errs)

    # --- Briefs semantic tests ---
    def test_brief_image_id_scene_prefix(self):
        docs = make_valid_docs(1)
        docs["briefs"]["images"][0]["image_id"] = "s9_wrong_prefix"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("image_id" in e and "prefix" in e and "s1" in e.lower() for e in errs)

    def test_brief_scene_not_exist(self):
        docs = make_valid_docs(1)
        docs["briefs"]["images"][0]["scene_id"] = "S99"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S99" in e and ("scene" in e and "not exist" in e or "unknown" in e.lower()) for e in errs)

    def test_brief_shot_not_in_scene(self):
        docs = make_valid_docs(1)
        docs["briefs"]["images"][0]["shot_ids"] = ["S2-1"]  # belongs to S2
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("shot" in e and "S2-1" in e and ("scene" in e or "not belong" in e) for e in errs)

    def test_brief_empty_person_name(self):
        docs = make_valid_docs(1)
        docs["briefs"]["images"][0]["people"][0]["name"] = ""
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("name" in e and ("empty" in e or "missing" in e) for e in errs)

    def test_brief_empty_on_screen_facts(self):
        docs = make_valid_docs(1)
        docs["briefs"]["images"][0]["on_screen_facts"] = []
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("on_screen_facts" in e and ("empty" in e or "non-empty" in e) for e in errs)

    # --- Looks semantic tests ---
    def test_look_source_ovi_outside_chapter(self):
        docs = make_valid_docs(1)
        docs["looks"]["entries"][0]["source_ovis"] = [99]
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        assert any("source_ovis" in e and "99" in e and "outside" in e for e in errs)

    def test_known_entity_redecided_same_state_id(self):
        docs = make_valid_docs(1)
        # arjuna is in known_entities with state_id battle_ready
        # Entry has same entity_id and same state_id -> error
        docs["looks"]["entries"][0] = {
            "entity_id": "arjuna",
            "kind": "character",
            "state_id": "battle_ready",
            "look": "different look",
            "source_ovis": [1],
            "basis": "inferred",
        }
        ctx = make_ctx(known_entities={"arjuna"})
        errs = validate_stage1(1, docs, ctx)
        assert any("arjuna" in e and "known entity redecided with the same state id" in e for e in errs)

    def test_known_entity_new_state_id_allowed(self):
        docs = make_valid_docs(1)
        # New state_id for known entity should be OK
        docs["looks"]["entries"][0] = {
            "entity_id": "arjuna",
            "kind": "character",
            "state_id": "new_state",
            "look": "different",
            "source_ovis": [1],
            "basis": "inferred",
        }
        ctx = make_ctx(known_entities={"arjuna"})
        errs = validate_stage1(1, docs, ctx)
        assert not any("redecided" in e for e in errs)

    def test_entity_state_unique(self):
        docs = make_valid_docs(1)
        docs["looks"]["entries"].append(
            {
                "entity_id": "arjuna",
                "kind": "character",
                "state_id": "battle_ready",
                "look": "dup",
                "source_ovis": [2],
                "basis": "stated",
            }
        )
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("arjuna" in e and "battle_ready" in e and ("duplicate" in e.lower() or "unique" in e.lower()) for e in errs)

    # --- Voices semantic tests ---
    def test_speaking_character_no_voice(self):
        docs = make_valid_docs(1)
        docs["voices"]["cast"] = []  # no cast entries
        ctx = make_ctx(speaking_characters={"arjuna", "krishna"})
        errs = validate_stage1(1, docs, ctx)
        assert any("arjuna" in e and "no voice assigned" in e for e in errs)
        assert any("krishna" in e and "no voice assigned" in e for e in errs)

    def test_voice_key_not_in_saved(self):
        docs = make_valid_docs(1)
        docs["voices"]["cast"][0]["voice_key"] = "unknown_key"
        ctx = make_ctx(saved_voices={"arjuna_voice": "v_arjuna_001"})
        errs = validate_stage1(1, docs, ctx)
        assert any("arjuna" in e and "voice not in the saved cast" in e for e in errs)

    def test_voice_id_mismatch_saved(self):
        docs = make_valid_docs(1)
        docs["voices"]["cast"][0]["voice_id"] = "wrong_id"
        ctx = make_ctx(saved_voices={"arjuna_voice": "v_arjuna_001"})
        errs = validate_stage1(1, docs, ctx)
        assert any("arjuna" in e and "voice not in the saved cast" in e for e in errs)

    def test_recurring_character_listed_twice(self):
        docs = make_valid_docs(1)
        docs["voices"]["cast"].append(
            {
                "character_id": "arjuna",
                "voice_key": "arjuna_voice",
                "voice_id": "v_arjuna_001",
                "gender": "male",
                "status": "RECURRING",
            }
        )
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("arjuna" in e and ("twice" in e or "duplicate" in e.lower()) for e in errs)

    def test_two_characters_share_voice_key(self):
        docs = make_valid_docs(1)
        docs["voices"]["cast"][1]["voice_key"] = "arjuna_voice"  # same as arjuna
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("voice_key" in e and "shared" in e.lower() for e in errs)

    def test_narrator_can_share_voice_key(self):
        # Narrator is allowed to share voice_key
        docs = make_valid_docs(1)
        docs["voices"]["cast"] = [
            {
                "character_id": "arjuna",
                "voice_key": "shared_voice",
                "voice_id": "v_shared_001",
                "gender": "male",
                "status": "RECURRING",
            },
            {
                "character_id": "narrator",
                "voice_key": "shared_voice",
                "voice_id": "v_shared_001",
                "gender": "male",
                "status": "RECURRING",
            },
        ]
        ctx = make_ctx(
            speaking_characters={"arjuna", "narrator"},
            saved_voices={"shared_voice": "v_shared_001"},
        )
        errs = validate_stage1(1, docs, ctx)
        assert not any("shared" in e.lower() for e in errs)

    # --- Sounds semantic tests ---
    def test_sound_scene_not_exist(self):
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0]["scene_id"] = "S99"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S99" in e and ("scene" in e and "not exist" in e or "unknown" in e.lower()) for e in errs)

    def test_sound_anchor_line_not_in_scene(self):
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0]["anchor_line_id"] = "S2-L1"  # belongs to S2
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("anchor_line_id" in e and ("scene" in e or "not belong" in e) for e in errs)

    def test_sound_id_unknown(self):
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0]["sound_id"] = "bed_unknown"
        ctx = make_ctx(sound_ids={"bed_battlefield"})
        errs = validate_stage1(1, docs, ctx)
        assert any("unknown" in e.lower() and "bed_unknown" in e for e in errs)

    def test_sound_need_new_without_prompt_schema_catches(self):
        # This is caught by schema validation, not semantic
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0] = {
            "scene_id": "S1",
            "anchor_line_id": "S1-L1",
            "sound_id": "NEED_NEW",
            "kind": "fx",
            "purpose": "test",
            "basis": "stated",
        }
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("sound_prompt" in e for e in errs)

    def test_sound_non_need_new_with_prompt(self):
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0]["sound_prompt"] = "should not be here"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("sound_prompt" in e and ("not allowed" in e or "forbidden" in e or "unexpected" in e) for e in errs)

    def test_sound_kind_mismatch_prefix(self):
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0]["sound_id"] = "fx_conch"
        docs["sounds"]["cues"][0]["kind"] = "bed"  # prefix fx but kind bed
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("kind" in e and ("mismatch" in e or "prefix" in e) for e in errs)

    # --- Questions semantic tests ---
    def test_question_duplicate_id(self):
        docs = make_valid_docs(1)
        docs["questions"]["questions"].append({"id": "Q1", "text": "dup"})
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("Q1" in e and ("duplicate" in e.lower() or "unique" in e.lower()) for e in errs)

    def test_question_scene_not_exist(self):
        docs = make_valid_docs(1)
        docs["questions"]["questions"][0]["scene_id"] = "S99"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S99" in e and ("scene" in e and "not exist" in e or "unknown" in e.lower()) for e in errs)

    # --- Zero-story chapter test ---
    def test_zero_story_chapter_validates(self):
        """All ovis TEACHING/PHILOSOPHY, one discourse scene, no story events."""
        docs = {
            "story_map": {
                "adhyay": 2,
                "ovi_types": [
                    {"ovi": 1, "type": "TEACHING"},
                    {"ovi": 2, "type": "PHILOSOPHY"},
                ],
                "events": [
                    {
                        "event_id": "E1",
                        "title": "Teaching",
                        "ovi_range": [1, 2],
                        "key_ovis": [1, 2],
                        "kind": "discourse",
                        "closure": "RESOLVED_IN_ADHYAY",
                    }
                ],
            },
            "coverage": {
                "adhyay": 2,
                "ovis": [
                    {"ovi": 1, "disposition": "NARRATED"},
                    {"ovi": 2, "disposition": "QUOTED"},
                ],
            },
            "scenes": {
                "adhyay": 2,
                "scenes": [
                    {
                        "scene_id": "S1",
                        "section_kind": "discourse",
                        "ovi_range": [1, 2],
                        "goal": "Teaching",
                        "turn": {"ovi": 1, "text": "Krishna teaches"},
                        "line_ids": ["S1-L1"],
                        "teaching_treatment": "contemplative_hold",
                    }
                ],
            },
            "shots": {
                "adhyay": 2,
                "shots": [
                    {
                        "shot_id": "S1-1",
                        "scene_id": "S1",
                        "ovi_ids": [1, 2],
                        "beat_line_ids": ["S1-L1"],
                        "preset": "01_wide",
                        "need_new": None,
                        "needs_cutout": False,
                        "pose": "seated",
                        "framing": "medium",
                    }
                ],
            },
            "briefs": {
                "adhyay": 2,
                "images": [
                    {
                        "image_id": "s1_krishna_teaching",
                        "scene_id": "S1",
                        "shot_ids": ["S1-1"],
                        "people": [
                            {"name": "Krishna", "position": "center", "pose": "seated", "gaze": "forward"}
                        ],
                        "place_id": "chariot",
                        "prop": None,
                        "prop_state": None,
                        "camera": "eye level",
                        "light": "soft",
                        "reason_new": "teaching",
                        "on_screen_facts": ["Krishna teaches"],
                        "references": {
                            "characters": ["Krishna"],
                            "place": "chariot",
                            "style_anchor": "epic realism",
                            "prop": None,
                        },
                    }
                ],
            },
            "looks": {
                "adhyay": 2,
                "entries": [
                    {
                        "entity_id": "krishna",
                        "kind": "character",
                        "state_id": "teacher",
                        "look": "peacock feather",
                        "source_ovis": [1, 2],
                        "basis": "stated",
                    }
                ],
            },
            "voices": {
                "adhyay": 2,
                "cast": [
                    {
                        "character_id": "krishna",
                        "voice_key": "krishna_voice",
                        "voice_id": "v_krishna_001",
                        "gender": "male",
                        "status": "RECURRING",
                    }
                ],
            },
            "sounds": {
                "adhyay": 2,
                "cues": [
                    {
                        "scene_id": "S1",
                        "anchor_line_id": "S1-L1",
                        "sound_id": "bed_battlefield",
                        "kind": "bed",
                        "purpose": "ambience",
                        "basis": "staging",
                    }
                ],
            },
            "questions": {"adhyay": 2, "questions": [{"id": "Q1", "text": "What is yoga?"}]},
        }
        ctx = make_ctx(
            script_line_ids=["S1-L1"],
            core_line_ids={"S1-L1"},
            chapter_ovis={1, 2},
            unfilmed_ovis=set(),
            preset_ids={"01_wide"},
            sound_ids={"bed_battlefield"},
            saved_voices={"krishna_voice": "v_krishna_001"},
            speaking_characters={"krishna"},
            known_entities={"krishna", "chariot"},
        )
        errs = validate_stage1(2, docs, ctx)
        assert errs == [], f"zero-story chapter failed: {errs}"

    # --- Stability test ---
    def test_messages_stable_order(self):
        """Same input produces same error list order."""
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"] = []  # missing all dispositions
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs1 = validate_stage1(1, docs, ctx)
        errs2 = validate_stage1(1, docs, ctx)
        assert errs1 == errs2, "error order not stable"

    # --- Missing references never raise ---
    def test_missing_references_no_exception(self):
        """Validator never raises, only returns error strings."""
        docs = make_valid_docs(1)
        # Remove all context references
        ctx = make_ctx(
            script_line_ids=[],
            core_line_ids=set(),
            chapter_ovis=set(),
            unfilmed_ovis=set(),
            preset_ids=set(),
            sound_ids=set(),
            saved_voices={},
            speaking_characters=set(),
            known_entities=set(),
        )
        # Should not raise
        errs = validate_stage1(1, docs, ctx)
        assert isinstance(errs, list)
        assert all(isinstance(e, str) for e in errs)

    # --- Deliberately broken implementation style cases ---
    def test_broken_implementation_extra_fields_ignored(self):
        """If implementation ignores extra fields, schema should catch it."""
        docs = make_valid_docs(1)
        docs["story_map"]["extra_top_level"] = "ignored"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("additionalProperties" in e or "extra_top_level" in e for e in errs)

    def test_broken_implementation_wrong_type_not_caught_by_schema(self):
        """If implementation passes wrong type, semantic check should catch."""
        docs = make_valid_docs(1)
        docs["story_map"]["ovi_types"] = [{"ovi": "one", "type": "STORY"}]  # ovi as string
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        # Schema should catch type mismatch
        assert any("ovi" in e and ("type" in e or "integer" in e) for e in errs)

    def test_broken_implementation_missing_required_field(self):
        """If implementation omits required field, schema catches it."""
        docs = make_valid_docs(1)
        del docs["scenes"]["scenes"][0]["goal"]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("goal" in e and ("required" in e or "missing" in e) for e in errs)
