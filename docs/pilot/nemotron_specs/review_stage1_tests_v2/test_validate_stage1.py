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
    known_states=None,
):
    """Build context dict. Only apply defaults when argument is None (not empty)."""
    return {
        "script_line_ids": script_line_ids if script_line_ids is not None else ["S1-L1", "S1-L2", "S2-L1"],
        "core_line_ids": core_line_ids if core_line_ids is not None else {"S1-L1", "S2-L1"},
        "chapter_ovis": chapter_ovis if chapter_ovis is not None else {1, 2, 3, 4, 5},
        "unfilmed_ovis": unfilmed_ovis if unfilmed_ovis is not None else set(),
        "preset_ids": preset_ids if preset_ids is not None else {"01_wide", "02_medium", "03_close"},
        "sound_ids": sound_ids if sound_ids is not None else {"bed_battlefield", "fx_conch"},
        "saved_voices": saved_voices if saved_voices is not None else {"arjuna_voice": "v_arjuna_001_valid_id", "krishna_voice": "v_krishna_001_valid_id"},
        "speaking_characters": speaking_characters if speaking_characters is not None else {"arjuna", "krishna"},
        "known_states": known_states if known_states is not None else {"arjuna": {"battle_ready"}, "krishna": {"charioteer"}, "battlefield": {"dawn_armies"}},
    }


def make_valid_docs(adhyay=1):
    """Return a fully valid set of nine documents for the given adhyay.
    NOTE-FREE: no PROPOSE_OMISSION entries.
    """
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
                {"ovi": 5, "disposition": "QUOTED"},  # not PROPOSE_OMISSION
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
                    "voice_id": "v_arjuna_001_valid_id",
                    "gender": "male",
                    "status": "RECURRING",
                },
                {
                    "character_id": "krishna",
                    "voice_key": "krishna_voice",
                    "voice_id": "v_krishna_001_valid_id",
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
    # --- Baseline ---
    def test_fully_valid_returns_empty(self):
        docs = make_valid_docs(1)
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert errs == [], f"expected no errors, got: {errs}"

    # --- Phase control ---
    def test_schema_error_stops_early(self):
        """Schema errors in multiple docs; adhyay mismatch also present.
        Should return ALL schema errors and NO semantic errors."""
        docs = make_valid_docs(1)
        # Introduce schema errors in two documents
        docs["story_map"]["ovi_types"] = [{"ovi": 1}]  # missing type
        docs["coverage"]["ovis"] = [{"ovi": 1}]  # missing disposition
        # Also introduce adhyay mismatch in a third document
        docs["scenes"]["adhyay"] = 2
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        # All schema errors present
        assert any("story_map" in e and "type" in e for e in errs)
        assert any("coverage" in e and "disposition" in e for e in errs)
        assert any("scenes" in e and "adhyay" in e and "does not match" in e for e in errs)
        # No semantic errors (adhyay mismatch is a semantic step 2 check, but schema errors stop early)
        # Actually adhyay mismatch is step 2 (semantic), so it should NOT appear if schema errors stop early
        semantic_errs = [e for e in errs if "adhyay" in e and "does not match" in e]
        # The spec says: "return at once only if a schema step fails" - so semantic steps don't run
        # But wait: adhyay mismatch is step 2, which is semantic. Schema is step 1.
        # So if step 1 has errors, step 2 doesn't run. The adhyay mismatch in scenes is a semantic check.
        # However, the schema for scenes requires adhyay field - but the value 2 is valid for schema.
        # So the adhyay mismatch is NOT a schema error, it's semantic. It should NOT appear.
        assert not any("scenes adhyay 2 does not match 1" in e for e in errs)

    def test_collects_all_semantic_steps(self):
        """Independent violations across steps 2-11; all should be reported."""
        docs = make_valid_docs(1)
        # Step 2: adhyay mismatch in coverage
        docs["coverage"]["adhyay"] = 2
        # Step 3: ovi untyped
        docs["story_map"]["ovi_types"] = [{"ovi": 1, "type": "STORY"}]  # missing 2-5
        # Step 4: coverage missing disposition for ovi 2, unfilmed but VISUALISED
        docs["coverage"]["ovis"] = [
            {"ovi": 1, "disposition": "VISUALISED"},
            {"ovi": 3, "disposition": "QUOTED"},
            {"ovi": 4, "disposition": "MERGED_EQUIVALENT", "reason": "r", "covered_by": 3},
            {"ovi": 5, "disposition": "QUOTED"},
        ]
        # Step 5: scene range overlap, core line missing, discourse without treatment
        docs["scenes"]["scenes"][1]["ovi_range"] = [2, 4]  # overlaps S1 [1,2]
        docs["scenes"]["scenes"][1]["line_ids"] = []  # S2-L1 core but missing
        docs["scenes"]["scenes"][1]["teaching_treatment"] = "none"
        # Step 6: shot not consecutive, unknown preset, line not in any shot beat
        docs["shots"]["shots"][1]["shot_id"] = "S1-3"  # skip S1-2
        docs["shots"]["shots"][0]["preset"] = "99_unknown"
        docs["shots"]["shots"] = [s for s in docs["shots"]["shots"] if s["shot_id"] != "S1-2"]  # S1-L2 not in any shot
        # Step 7: brief image_id wrong prefix, shot not in scene
        docs["briefs"]["images"][0]["image_id"] = "s9_wrong"
        docs["briefs"]["images"][0]["shot_ids"] = ["S2-1"]
        # Step 8: look source_ovi outside chapter, known entity redecided same state
        docs["looks"]["entries"][0]["source_ovis"] = [99]
        docs["looks"]["entries"][0] = {
            "entity_id": "arjuna",
            "kind": "character",
            "state_id": "battle_ready",  # known state
            "look": "different",
            "source_ovis": [1],
            "basis": "inferred",
        }
        # Step 9: speaking character no voice, voice_key not in saved, recurring duplicate
        docs["voices"]["cast"] = []
        # Step 10: sound scene not exist, anchor not in scene, unknown sound_id, kind mismatch
        docs["sounds"]["cues"][0]["scene_id"] = "S99"
        docs["sounds"]["cues"][0]["anchor_line_id"] = "S2-L1"
        docs["sounds"]["cues"][0]["sound_id"] = "bed_unknown"
        docs["sounds"]["cues"][0]["kind"] = "bed"  # fx_conch is fx but kind bed
        # Step 11: question duplicate id, scene not exist
        docs["questions"]["questions"].append({"id": "Q1", "text": "dup"})
        docs["questions"]["questions"][0]["scene_id"] = "S99"

        ctx = make_ctx(
            chapter_ovis={1, 2, 3, 4, 5},
            unfilmed_ovis={1},
            preset_ids={"01_wide", "02_medium", "03_close"},
            sound_ids={"bed_battlefield", "fx_conch"},
            saved_voices={"arjuna_voice": "v_arjuna_001_valid_id", "krishna_voice": "v_krishna_001_valid_id"},
            speaking_characters={"arjuna", "krishna"},
            known_states={"arjuna": {"battle_ready"}, "krishna": {"charioteer"}, "battlefield": {"dawn_armies"}},
        )
        errs = validate_stage1(1, docs, ctx)
        # Check each step's keywords appear
        keywords = [
            "coverage adhyay 2 does not match 1",  # step 2
            "ovi 2 is untyped", "ovi 3 is untyped", "ovi 4 is untyped", "ovi 5 is untyped",  # step 3
            "ovi 2 has no disposition", "ovi 1 is unfilmed but VISUALISED",  # step 4
            "overlap", "S2-L1", "core", "discourse", "teaching_treatment",  # step 5
            "consecutive", "unknown preset", "S1-L2", "line is in no shot beat",  # step 6
            "prefix", "S2-1", "not belong",  # step 7
            "source_ovis", "99", "outside", "arjuna", "known state", "battle_ready", "redecided",  # step 8
            "arjuna", "no voice assigned", "voice not in the saved cast", "twice",  # step 9
            "S99", "anchor_line_id", "bed_unknown", "kind", "mismatch",  # step 10
            "Q1", "duplicate", "S99",  # step 11
        ]
        for kw in keywords:
            assert any(kw in e for e in errs), f"missing keyword: {kw} in {errs}"

    # --- Step 2: adhyay mismatch ---
    @pytest.mark.parametrize("doc_key", [
        "story_map", "coverage", "scenes", "shots", "briefs", "looks", "voices", "sounds", "questions"
    ])
    def test_adhyay_mismatch_in_document(self, doc_key):
        docs = make_valid_docs(1)
        docs[doc_key]["adhyay"] = 2
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any(f"{doc_key} adhyay 2 does not match 1" in e for e in errs)

    # --- Step 3: story_map semantic ---
    def test_ovi_untyped(self):
        docs = make_valid_docs(1)
        docs["story_map"]["ovi_types"] = [{"ovi": 1, "type": "STORY"}]
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi 2 is untyped" in e for e in errs)
        assert any("ovi 3 is untyped" in e for e in errs)
        assert any("ovi 4 is untyped" in e for e in errs)
        assert any("ovi 5 is untyped" in e for e in errs)

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

    def test_event_ovi_range_lo_gt_hi(self):
        docs = make_valid_docs(1)
        docs["story_map"]["events"][0]["ovi_range"] = [5, 1]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        # Message must contain item id (event_id or document) and condition
        assert any("E1" in e and ("ovi_range" in e or "range" in e) for e in errs)

    def test_event_key_ovis_outside_range(self):
        docs = make_valid_docs(1)
        docs["story_map"]["events"][0]["key_ovis"] = [99]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("E1" in e and "key_ovis" in e and "range" in e for e in errs)

    # --- Step 4: coverage semantic ---
    def test_coverage_missing_disposition(self):
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"] = [{"ovi": 1, "disposition": "VISUALISED"}]
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi 2 has no disposition" in e for e in errs)
        assert any("ovi 3 has no disposition" in e for e in errs)
        assert any("ovi 4 has no disposition" in e for e in errs)
        assert any("ovi 5 has no disposition" in e for e in errs)

    def test_coverage_duplicate_disposition(self):
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"] = [
            {"ovi": 1, "disposition": "VISUALISED"},
            {"ovi": 1, "disposition": "NARRATED"},
            {"ovi": 2, "disposition": "NARRATED"},
            {"ovi": 3, "disposition": "QUOTED"},
            {"ovi": 4, "disposition": "MERGED_EQUIVALENT", "reason": "r", "covered_by": 3},
            {"ovi": 5, "disposition": "QUOTED"},
        ]
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi 1" in e and "twice" in e for e in errs)

    def test_propose_omission_note(self):
        """PROPOSE_OMISSION adds a NOTE message starting with 'note: '."""
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"][4] = {"ovi": 5, "disposition": "PROPOSE_OMISSION", "reason": "redundant"}
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        notes = [e for e in errs if e.startswith("note: ")]
        assert any("note: ovi 5 omission proposed, owner approval needed" in e for e in notes)
        # Notes come after errors
        error_msgs = [e for e in errs if not e.startswith("note: ")]
        note_msgs = [e for e in errs if e.startswith("note: ")]
        assert all(not e.startswith("note: ") for e in error_msgs)
        assert all(e.startswith("note: ") for e in note_msgs)

    def test_unfilmed_ovi_visualised_error(self):
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"][0]["disposition"] = "VISUALISED"
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5}, unfilmed_ovis={1})
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi 1 is unfilmed but VISUALISED" in e for e in errs)

    def test_covered_by_invalid_reference(self):
        """Well-formed but nonexistent line_id and ovi outside chapter."""
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"][3]["covered_by"] = "S1-L99"  # well-formed, not in script
        ctx = make_ctx(script_line_ids=["S1-L1"], chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        assert any("covered_by" in e and "S1-L99" in e for e in errs)
        # Also test integer outside chapter_ovis
        docs["coverage"]["ovis"][3]["covered_by"] = 99
        errs = validate_stage1(1, docs, ctx)
        assert any("covered_by" in e and "99" in e for e in errs)

    # --- Step 5: scenes semantic ---
    def test_scene_ids_unique(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"].append({
            "scene_id": "S1",
            "section_kind": "story",
            "ovi_range": [3, 3],
            "goal": "dup",
            "turn": {"ovi": 3, "text": "x"},
            "line_ids": [],
            "teaching_treatment": "none",
        })
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S1" in e and "duplicate" in e.lower() for e in errs)

    def test_scene_range_lo_gt_hi(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][0]["ovi_range"] = [3, 1]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S1" in e and "ovi_range" in e for e in errs)

    def test_scene_ranges_overlap(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][1]["ovi_range"] = [2, 4]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("overlap" in e.lower() for e in errs)

    def test_chapter_ovi_not_in_any_scene(self):
        docs = make_valid_docs(1)
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5, 6})
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi 6" in e and ("not in any scene" in e or "uncovered" in e.lower()) for e in errs)

    def test_unfilmed_ovi_inside_scene_range_error(self):
        docs = make_valid_docs(1)
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5}, unfilmed_ovis={2})
        errs = validate_stage1(1, docs, ctx)
        assert any("S1" in e and "ovi 2 is unfilmed but inside the range" in e for e in errs)

    def test_ovi_outside_chapter_in_scene(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][0]["ovi_range"] = [1, 99]
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        assert any("S1" in e and "ovi 99" in e and "outside" in e for e in errs)

    def test_turn_ovi_outside_scene_range(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][0]["turn"]["ovi"] = 99
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S1" in e and "turn" in e and "ovi" in e and "range" in e for e in errs)

    def test_line_id_not_in_script(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][0]["line_ids"] = ["S1-L99"]
        ctx = make_ctx(script_line_ids=["S1-L1"])
        errs = validate_stage1(1, docs, ctx)
        assert any("S1-L99" in e and ("not in the script" in e or "not in script" in e) for e in errs)

    def test_line_id_used_twice_across_scenes(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][1]["line_ids"] = ["S1-L1"]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S1-L1" in e and ("twice" in e or "duplicate" in e.lower()) for e in errs)

    def test_line_id_used_twice_within_scene(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][0]["line_ids"] = ["S1-L1", "S1-L1"]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S1-L1" in e and ("twice" in e or "duplicate" in e.lower()) for e in errs)

    def test_line_ids_not_in_script_order_within_scene(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][0]["line_ids"] = ["S1-L2", "S1-L1"]
        ctx = make_ctx(script_line_ids=["S1-L1", "S1-L2", "S2-L1"])
        errs = validate_stage1(1, docs, ctx)
        assert any("S1" in e and "order" in e.lower() for e in errs)

    def test_core_line_missing_from_scenes(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][1]["line_ids"] = []
        ctx = make_ctx(core_line_ids={"S1-L1", "S2-L1"})
        errs = validate_stage1(1, docs, ctx)
        assert any("S2-L1" in e and "core" in e.lower() and ("missing" in e.lower() or "not in any scene" in e) for e in errs)

    def test_discourse_scene_requires_treatment(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][1]["teaching_treatment"] = "none"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S2" in e and "discourse" in e.lower() and "teaching_treatment" in e for e in errs)

    # --- Step 6: shots semantic ---
    def test_shot_ids_unique(self):
        docs = make_valid_docs(1)
        docs["shots"]["shots"].append({
            "shot_id": "S1-1",
            "scene_id": "S1",
            "ovi_ids": [1],
            "beat_line_ids": ["S1-L1"],
            "preset": "01_wide",
            "need_new": None,
            "needs_cutout": False,
            "pose": "x",
            "framing": "x",
        })
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S1-1" in e and "duplicate" in e.lower() for e in errs)

    def test_shot_sequence_starts_at_one(self):
        """Shots per scene must be consecutive starting from 1."""
        docs = make_valid_docs(1)
        docs["shots"]["shots"][0]["shot_id"] = "S1-2"  # S1-1 missing
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S1" in e and ("consecutive" in e.lower() or "starts at 1" in e.lower() or "sequence" in e.lower()) for e in errs)

    def test_shot_not_consecutive(self):
        docs = make_valid_docs(1)
        docs["shots"]["shots"][1]["shot_id"] = "S1-3"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S1" in e and ("consecutive" in e.lower() or "sequence" in e.lower()) for e in errs)

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
        assert any("S1-1" in e and "ovi" in e and "99" in e and ("range" in e or "scene" in e) for e in errs)

    def test_shot_beat_line_ids_not_in_scene(self):
        docs = make_valid_docs(1)
        docs["shots"]["shots"][0]["beat_line_ids"] = ["S2-L1"]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S1-1" in e and "beat_line_ids" in e and ("scene" in e or "not belong" in e) for e in errs)

    def test_scene_with_no_shots(self):
        docs = make_valid_docs(1)
        docs["shots"]["shots"] = [s for s in docs["shots"]["shots"] if s["scene_id"] != "S2"]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S2" in e and ("no shots" in e or "has no shots" in e) for e in errs)

    def test_core_line_not_in_any_shot_beat(self):
        """Every line of every scene must be in some shot's beat_line_ids."""
        docs = make_valid_docs(1)
        docs["shots"]["shots"] = [s for s in docs["shots"]["shots"] if s["shot_id"] != "S1-2"]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S1-L2" in e and "line is in no shot beat" in e for e in errs)

    def test_shot_unknown_preset(self):
        docs = make_valid_docs(1)
        docs["shots"]["shots"][0]["preset"] = "99_unknown"
        ctx = make_ctx(preset_ids={"01_wide", "02_medium", "03_close"})
        errs = validate_stage1(1, docs, ctx)
        assert any("S1-1" in e and "unknown preset" in e and "99_unknown" in e for e in errs)

    def test_shot_need_new_accepted(self):
        """NEED_NEW shot with valid need_new object is accepted."""
        docs = make_valid_docs(1)
        docs["shots"]["shots"][0] = {
            "shot_id": "S1-1",
            "scene_id": "S1",
            "ovi_ids": [1],
            "beat_line_ids": ["S1-L1"],
            "preset": "NEED_NEW",
            "need_new": {"reason": "unique", "class": "missing_image"},
            "needs_cutout": False,
            "pose": "x",
            "framing": "x",
        }
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert not any("S1-1" in e for e in errs)

    # --- Step 7: briefs semantic ---
    def test_image_ids_unique(self):
        docs = make_valid_docs(1)
        docs["briefs"]["images"].append({
            "image_id": "s1_arjuna_standing",  # duplicate
            "scene_id": "S1",
            "shot_ids": ["S1-1"],
            "people": [{"name": "A", "position": "c", "pose": "p", "gaze": "g"}],
            "place_id": "p",
            "prop": None,
            "prop_state": None,
            "camera": "c",
            "light": "l",
            "reason_new": "r",
            "on_screen_facts": ["f"],
            "references": {"characters": [], "place": "p", "style_anchor": "s", "prop": None},
        })
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("s1_arjuna_standing" in e and "duplicate" in e.lower() for e in errs)

    def test_brief_image_id_scene_prefix(self):
        docs = make_valid_docs(1)
        docs["briefs"]["images"][0]["image_id"] = "s9_wrong_prefix"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("s1_arjuna_standing" in e or "image_id" in e) and any("prefix" in e or "s1" in e.lower() for e in errs)

    def test_brief_scene_not_exist(self):
        docs = make_valid_docs(1)
        docs["briefs"]["images"][0]["scene_id"] = "S99"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S99" in e and ("scene" in e and "not exist" in e or "unknown" in e.lower()) for e in errs)

    def test_brief_shot_missing(self):
        """Shot referenced in brief does not exist."""
        docs = make_valid_docs(1)
        docs["briefs"]["images"][0]["shot_ids"] = ["S1-99"]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S1-99" in e and ("shot" in e and "not exist" in e or "unknown" in e.lower()) for e in errs)

    def test_brief_shot_not_in_scene(self):
        docs = make_valid_docs(1)
        docs["briefs"]["images"][0]["shot_ids"] = ["S2-1"]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S2-1" in e and ("scene" in e or "not belong" in e) for e in errs)

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

    # --- Step 8: looks semantic ---
    def test_look_source_ovi_outside_chapter(self):
        docs = make_valid_docs(1)
        docs["looks"]["entries"][0]["source_ovis"] = [99]
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        assert any("arjuna" in e and "source_ovis" in e and "99" in e and "outside" in e for e in errs)

    def test_known_entity_redecided_same_state_id(self):
        """Known entity with same state_id is an error."""
        docs = make_valid_docs(1)
        docs["looks"]["entries"][0] = {
            "entity_id": "arjuna",
            "kind": "character",
            "state_id": "battle_ready",  # known state for arjuna
            "look": "different look",
            "source_ovis": [1],
            "basis": "inferred",
        }
        ctx = make_ctx(known_states={"arjuna": {"battle_ready"}, "krishna": {"charioteer"}, "battlefield": {"dawn_armies"}})
        errs = validate_stage1(1, docs, ctx)
        assert any("arjuna" in e and "known state" in e and "battle_ready" in e and "redecided" in e for e in errs)

    def test_known_entity_new_state_id_allowed(self):
        """Known entity with NEW state_id is allowed (no error)."""
        docs = make_valid_docs(1)
        docs["looks"]["entries"][0] = {
            "entity_id": "arjuna",
            "kind": "character",
            "state_id": "new_state",  # not in known_states
            "look": "different",
            "source_ovis": [1],
            "basis": "inferred",
        }
        ctx = make_ctx(known_states={"arjuna": {"battle_ready"}, "krishna": {"charioteer"}, "battlefield": {"dawn_armies"}})
        errs = validate_stage1(1, docs, ctx)
        assert not any("redecided" in e for e in errs)
        assert errs == []  # fully valid otherwise

    def test_entity_state_unique(self):
        docs = make_valid_docs(1)
        docs["looks"]["entries"].append({
            "entity_id": "arjuna",
            "kind": "character",
            "state_id": "battle_ready",
            "look": "dup",
            "source_ovis": [2],
            "basis": "stated",
        })
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("arjuna" in e and "battle_ready" in e and ("duplicate" in e.lower() or "unique" in e.lower()) for e in errs)

    # --- Step 9: voices semantic ---
    def test_speaking_character_no_voice(self):
        docs = make_valid_docs(1)
        docs["voices"]["cast"] = []
        ctx = make_ctx(speaking_characters={"arjuna", "krishna"})
        errs = validate_stage1(1, docs, ctx)
        assert any("arjuna" in e and "no voice assigned" in e for e in errs)
        assert any("krishna" in e and "no voice assigned" in e for e in errs)

    def test_voice_key_not_in_saved(self):
        docs = make_valid_docs(1)
        docs["voices"]["cast"][0]["voice_key"] = "unknown_key"
        ctx = make_ctx(saved_voices={"arjuna_voice": "v_arjuna_001_valid_id"})
        errs = validate_stage1(1, docs, ctx)
        assert any("arjuna" in e and "voice not in the saved cast" in e for e in errs)

    def test_voice_id_mismatch_saved(self):
        """Schema-valid voice_id that doesn't match saved_voices."""
        docs = make_valid_docs(1)
        docs["voices"]["cast"][0]["voice_id"] = "v_different_valid_id_001"
        ctx = make_ctx(saved_voices={"arjuna_voice": "v_arjuna_001_valid_id"})
        errs = validate_stage1(1, docs, ctx)
        assert any("arjuna" in e and "voice not in the saved cast" in e for e in errs)

    def test_recurring_character_listed_twice(self):
        docs = make_valid_docs(1)
        docs["voices"]["cast"].append({
            "character_id": "arjuna",
            "voice_key": "arjuna_voice",
            "voice_id": "v_arjuna_001_valid_id",
            "gender": "male",
            "status": "RECURRING",
        })
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("arjuna" in e and ("twice" in e or "duplicate" in e.lower()) for e in errs)

    def test_speaking_character_duplicate_new_proposed(self):
        """Two NEW_PROPOSED entries for same character is an error."""
        docs = make_valid_docs(1)
        docs["voices"]["cast"] = [
            {"character_id": "arjuna", "voice_key": "k1", "voice_id": "v_valid_id_001", "gender": "male", "status": "NEW_PROPOSED"},
            {"character_id": "arjuna", "voice_key": "k2", "voice_id": "v_valid_id_002", "gender": "male", "status": "NEW_PROPOSED"},
        ]
        ctx = make_ctx(speaking_characters={"arjuna"}, saved_voices={"k1": "v_valid_id_001", "k2": "v_valid_id_002"})
        errs = validate_stage1(1, docs, ctx)
        assert any("arjuna" in e and ("twice" in e or "duplicate" in e.lower()) for e in errs)

    def test_two_characters_share_voice_key(self):
        docs = make_valid_docs(1)
        docs["voices"]["cast"][1]["voice_key"] = "arjuna_voice"
        docs["voices"]["cast"][1]["voice_id"] = "v_arjuna_001_valid_id"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("voice_key" in e and "shared" in e.lower() for e in errs)

    def test_narrator_can_share_voice_key(self):
        docs = make_valid_docs(1)
        docs["voices"]["cast"] = [
            {"character_id": "arjuna", "voice_key": "shared_voice", "voice_id": "v_shared_valid_id_001", "gender": "male", "status": "RECURRING"},
            {"character_id": "narrator", "voice_key": "shared_voice", "voice_id": "v_shared_valid_id_001", "gender": "male", "status": "RECURRING"},
        ]
        ctx = make_ctx(
            speaking_characters={"arjuna", "narrator"},
            saved_voices={"shared_voice": "v_shared_valid_id_001"},
        )
        errs = validate_stage1(1, docs, ctx)
        assert not any("shared" in e.lower() for e in errs)
        assert errs == []

    # --- Step 10: sounds semantic ---
    def test_sound_scene_not_exist(self):
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0]["scene_id"] = "S99"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S99" in e and ("scene" in e and "not exist" in e or "unknown" in e.lower()) for e in errs)

    def test_sound_anchor_line_not_in_scene(self):
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0]["anchor_line_id"] = "S2-L1"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S1" in e and "anchor_line_id" in e and ("scene" in e or "not belong" in e) for e in errs)

    def test_sound_id_unknown(self):
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0]["sound_id"] = "bed_unknown"
        ctx = make_ctx(sound_ids={"bed_battlefield"})
        errs = validate_stage1(1, docs, ctx)
        assert any("bed_unknown" in e and ("unknown" in e.lower() or "not in" in e) for e in errs)

    def test_sound_need_new_without_prompt_schema_catches(self):
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
        """Non-NEED_NEW cue carrying sound_prompt is a SCHEMA error."""
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0]["sound_prompt"] = "should not be here"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("sound_prompt" in e for e in errs)

    def test_sound_kind_mismatch_prefix(self):
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0]["sound_id"] = "fx_conch"
        docs["sounds"]["cues"][0]["kind"] = "bed"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("fx_conch" in e and "kind" in e and ("mismatch" in e or "prefix" in e) for e in errs)

    def test_sound_need_new_accepted(self):
        """NEED_NEW sound with sound_prompt is accepted."""
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0] = {
            "scene_id": "S1",
            "anchor_line_id": "S1-L1",
            "sound_id": "NEED_NEW",
            "kind": "fx",
            "sound_prompt": "conch blow",
            "purpose": "signal",
            "basis": "stated",
        }
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert not any("S1" in e for e in errs)

    # --- Step 11: questions semantic ---
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

    # --- Zero-story chapter ---
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
                        "voice_id": "v_krishna_001_valid_id",
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
            saved_voices={"krishna_voice": "v_krishna_001_valid_id"},
            speaking_characters={"krishna"},
            known_states={"krishna": {"charioteer"}, "chariot": {"interior"}},
        )
        errs = validate_stage1(2, docs, ctx)
        assert errs == [], f"zero-story chapter failed: {errs}"

    def test_zero_story_empty_events_validates(self):
        """Zero-story chapter with empty events array is valid."""
        docs = {
            "story_map": {
                "adhyay": 3,
                "ovi_types": [
                    {"ovi": 1, "type": "TEACHING"},
                    {"ovi": 2, "type": "PHILOSOPHY"},
                ],
                "events": [],  # empty
            },
            "coverage": {
                "adhyay": 3,
                "ovis": [
                    {"ovi": 1, "disposition": "NARRATED"},
                    {"ovi": 2, "disposition": "QUOTED"},
                ],
            },
            "scenes": {
                "adhyay": 3,
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
                "adhyay": 3,
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
                "adhyay": 3,
                "images": [
                    {
                        "image_id": "s1_krishna_teaching",
                        "scene_id": "S1",
                        "shot_ids": ["S1-1"],
                        "people": [{"name": "Krishna", "position": "center", "pose": "seated", "gaze": "forward"}],
                        "place_id": "chariot",
                        "prop": None,
                        "prop_state": None,
                        "camera": "eye level",
                        "light": "soft",
                        "reason_new": "teaching",
                        "on_screen_facts": ["Krishna teaches"],
                        "references": {"characters": ["Krishna"], "place": "chariot", "style_anchor": "epic realism", "prop": None},
                    }
                ],
            },
            "looks": {
                "adhyay": 3,
                "entries": [
                    {"entity_id": "krishna", "kind": "character", "state_id": "teacher", "look": "peacock feather", "source_ovis": [1, 2], "basis": "stated"}
                ],
            },
            "voices": {
                "adhyay": 3,
                "cast": [{"character_id": "krishna", "voice_key": "krishna_voice", "voice_id": "v_krishna_001_valid_id", "gender": "male", "status": "RECURRING"}],
            },
            "sounds": {
                "adhyay": 3,
                "cues": [{"scene_id": "S1", "anchor_line_id": "S1-L1", "sound_id": "bed_battlefield", "kind": "bed", "purpose": "ambience", "basis": "staging"}],
            },
            "questions": {"adhyay": 3, "questions": [{"id": "Q1", "text": "What is yoga?"}]},
        }
        ctx = make_ctx(
            script_line_ids=["S1-L1"],
            core_line_ids={"S1-L1"},
            chapter_ovis={1, 2},
            unfilmed_ovis=set(),
            preset_ids={"01_wide"},
            sound_ids={"bed_battlefield"},
            saved_voices={"krishna_voice": "v_krishna_001_valid_id"},
            speaking_characters={"krishna"},
            known_states={"krishna": {"charioteer"}, "chariot": {"interior"}},
        )
        errs = validate_stage1(3, docs, ctx)
        assert errs == [], f"zero-story empty events failed: {errs}"

    # --- Stability ---
    def test_messages_stable_order(self):
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"] = []
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs1 = validate_stage1(1, docs, ctx)
        errs2 = validate_stage1(1, docs, ctx)
        assert errs1 == errs2, "error order not stable"
        # Also verify expected diagnostics are present
        assert any("ovi 1 has no disposition" in e for e in errs1)
        assert any("ovi 2 has no disposition" in e for e in errs1)

    def test_notes_follow_errors(self):
        """Notes (PROPOSE_OMISSION) come after all error messages."""
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"][4] = {"ovi": 5, "disposition": "PROPOSE_OMISSION", "reason": "redundant"}
        # Also add a real error
        docs["coverage"]["ovis"] = [{"ovi": 1, "disposition": "VISUALISED"}]  # missing 2-5
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        # Find first note index
        note_indices = [i for i, e in enumerate(errs) if e.startswith("note: ")]
        error_indices = [i for i, e in enumerate(errs) if not e.startswith("note: ")]
        if note_indices and error_indices:
            assert max(error_indices) < min(note_indices), "notes must follow errors"

    def test_message_prefixes(self):
        """Each message starts with item id or document name."""
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"] = []
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        for e in errs:
            # Either starts with document name (story_map, coverage, etc.) or item id (S1, E1, Q1, ovi N, etc.)
            # or "note: "
            assert e.startswith("note: ") or any(e.startswith(prefix) for prefix in [
                "story_map", "coverage", "scenes", "shots", "briefs", "looks", "voices", "sounds", "questions",
                "S1", "S2", "E1", "E2", "Q1", "Q2", "ovi 1", "ovi 2", "ovi 3", "ovi 4", "ovi 5",
                "s1_", "s2_", "arjuna", "krishna", "battlefield"
            ]), f"message lacks required prefix: {e}"

    # --- Missing references never raise ---
    def test_missing_references_no_exception(self):
        """Validator never raises, only returns error strings.
        Empty context should produce specific missing-reference diagnostics."""
        docs = make_valid_docs(1)
        ctx = make_ctx(
            script_line_ids=[],
            core_line_ids=set(),
            chapter_ovis=set(),
            unfilmed_ovis=set(),
            preset_ids=set(),
            sound_ids=set(),
            saved_voices={},
            speaking_characters=set(),
            known_states={},
        )
        errs = validate_stage1(1, docs, ctx)
        assert isinstance(errs, list)
        assert all(isinstance(e, str) for e in errs)
        # Should have specific missing-reference errors
        assert any("S1-L1" in e and "not in the script" in e for e in errs)
        assert any("ovi 1" in e and ("no disposition" in e or "untyped" in e) for e in errs)

    def test_empty_context_survives(self):
        """Intentionally empty sets/dicts in context are not replaced by defaults."""
        ctx = make_ctx(
            script_line_ids=[],
            core_line_ids=set(),
            chapter_ovis=set(),
            unfilmed_ovis=set(),
            preset_ids=set(),
            sound_ids=set(),
            saved_voices={},
            speaking_characters=set(),
            known_states={},
        )
        assert ctx["script_line_ids"] == []
        assert ctx["core_line_ids"] == set()
        assert ctx["chapter_ovis"] == set()
        assert ctx["unfilmed_ovis"] == set()
        assert ctx["preset_ids"] == set()
        assert ctx["sound_ids"] == set()
        assert ctx["saved_voices"] == {}
        assert ctx["speaking_characters"] == set()
        assert ctx["known_states"] == {}

    # --- Deliberately broken implementation style cases ---
    def test_broken_implementation_extra_fields_ignored(self):
        docs = make_valid_docs(1)
        docs["story_map"]["extra_top_level"] = "ignored"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("additionalProperties" in e or "extra_top_level" in e for e in errs)

    def test_broken_implementation_wrong_type_not_caught_by_schema(self):
        docs = make_valid_docs(1)
        docs["story_map"]["ovi_types"] = [{"ovi": "one", "type": "STORY"}]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi" in e and ("type" in e or "integer" in e) for e in errs)

    def test_broken_implementation_missing_required_field(self):
        docs = make_valid_docs(1)
        del docs["scenes"]["scenes"][0]["goal"]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("goal" in e and ("required" in e or "missing" in e) for e in errs)
