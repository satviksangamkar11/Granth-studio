from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location(
    "validate_stage1", ROOT / "scripts" / "pipeline" / "validate_stage1.py"
)
validate_stage1_mod = importlib.util.module_from_spec(spec)
sys.modules["validate_stage1"] = validate_stage1_mod
spec.loader.exec_module(validate_stage1_mod)

validate_stage1 = validate_stage1_mod.validate_stage1


# ======================================================================
# Context builder (defaults only when None)
# ======================================================================
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


# ======================================================================
# Baseline valid documents (note-free, NEW states not in known_states)
# ======================================================================
def make_valid_docs(adhyay=1):
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
                {"event_id": "E1", "title": "Opening", "ovi_range": [1, 2], "key_ovis": [1], "kind": "story", "closure": "RESOLVED_IN_ADHYAY"},
                {"event_id": "E2", "title": "Teaching", "ovi_range": [3, 5], "key_ovis": [3, 4], "kind": "discourse", "closure": "RESOLVED_IN_ADHYAY"},
            ],
        },
        "coverage": {
            "adhyay": adhyay,
            "ovis": [
                {"ovi": 1, "disposition": "VISUALISED"},
                {"ovi": 2, "disposition": "NARRATED"},
                {"ovi": 3, "disposition": "QUOTED"},
                {"ovi": 4, "disposition": "MERGED_EQUIVALENT", "reason": "same as 3", "covered_by": 3},
                {"ovi": 5, "disposition": "QUOTED"},
            ],
        },
        "scenes": {
            "adhyay": adhyay,
            "scenes": [
                {"scene_id": "S1", "section_kind": "story", "ovi_range": [1, 2], "goal": "Setup", "turn": {"ovi": 1, "text": "Arjuna sees armies"}, "line_ids": ["S1-L1", "S1-L2"], "teaching_treatment": "none"},
                {"scene_id": "S2", "section_kind": "discourse", "ovi_range": [3, 5], "goal": "Teaching", "turn": {"ovi": 3, "text": "Krishna speaks"}, "line_ids": ["S2-L1"], "teaching_treatment": "contemplative_hold"},
            ],
        },
        "shots": {
            "adhyay": adhyay,
            "shots": [
                {"shot_id": "S1-1", "scene_id": "S1", "ovi_ids": [1], "beat_line_ids": ["S1-L1"], "preset": "01_wide", "need_new": None, "needs_cutout": False, "pose": "standing", "framing": "wide"},
                {"shot_id": "S1-2", "scene_id": "S1", "ovi_ids": [2], "beat_line_ids": ["S1-L2"], "preset": "02_medium", "need_new": None, "needs_cutout": False, "pose": "kneeling", "framing": "medium"},
                {"shot_id": "S2-1", "scene_id": "S2", "ovi_ids": [3, 4, 5], "beat_line_ids": ["S2-L1"], "preset": "03_close", "need_new": None, "needs_cutout": True, "pose": "seated", "framing": "close"},
            ],
        },
        "briefs": {
            "adhyay": adhyay,
            "images": [
                {"image_id": "s1_arjuna_standing", "scene_id": "S1", "shot_ids": ["S1-1"], "people": [{"name": "Arjuna", "position": "center", "pose": "standing", "gaze": "forward"}], "place_id": "battlefield", "prop": "bow", "prop_state": "strung", "camera": "eye level", "light": "harsh noon", "reason_new": "first shot", "on_screen_facts": ["Arjuna stands", "bow visible"], "references": {"characters": ["Arjuna"], "place": "battlefield", "style_anchor": "epic realism", "prop": "bow"}},
                {"image_id": "s2_krishna_seated", "scene_id": "S2", "shot_ids": ["S2-1"], "people": [{"name": "Krishna", "position": "center", "pose": "seated", "gaze": "at Arjuna"}], "place_id": "chariot", "prop": None, "prop_state": None, "camera": "low angle", "light": "divine glow", "reason_new": "teaching moment", "on_screen_facts": ["Krishna seated", "chariot interior"], "references": {"characters": ["Krishna"], "place": "chariot", "style_anchor": "epic realism", "prop": None}},
            ],
        },
        "looks": {
            "adhyay": adhyay,
            "entries": [
                {"entity_id": "arjuna", "kind": "character", "state_id": "battle_ready_new", "look": "armored, bow in hand", "source_ovis": [1, 2], "basis": "stated"},
                {"entity_id": "krishna", "kind": "character", "state_id": "charioteer_new", "look": "peacock feather, yellow garment", "source_ovis": [3, 4, 5], "basis": "stated"},
                {"entity_id": "battlefield", "kind": "place", "state_id": "dawn_armies_new", "look": "two armies arrayed", "source_ovis": [1], "basis": "stated"},
            ],
        },
        "voices": {
            "adhyay": adhyay,
            "cast": [
                {"character_id": "arjuna", "voice_key": "arjuna_voice", "voice_id": "v_arjuna_001_valid_id", "gender": "male", "status": "RECURRING"},
                {"character_id": "krishna", "voice_key": "krishna_voice", "voice_id": "v_krishna_001_valid_id", "gender": "male", "status": "RECURRING"},
            ],
        },
        "sounds": {
            "adhyay": adhyay,
            "cues": [
                {"scene_id": "S1", "anchor_line_id": "S1-L1", "sound_id": "bed_battlefield", "kind": "bed", "purpose": "ambience", "basis": "staging"},
                {"scene_id": "S2", "anchor_line_id": "S2-L1", "sound_id": "fx_conch", "kind": "fx", "purpose": "signal start", "basis": "stated"},
            ],
        },
        "questions": {
            "adhyay": adhyay,
            "questions": [{"id": "Q1", "text": "Why does Arjuna hesitate?", "scene_id": "S1"}, {"id": "Q2", "text": "What is the nature of the self?"}],
        },
    }


# ======================================================================
# Mutation helpers for semantic tests
# ======================================================================
def mutate_docs(docs: dict, path: list, value):
    d = copy.deepcopy(docs)
    cur = d
    for p in path[:-1]:
        cur = cur[p]
    cur[path[-1]] = value
    return d


def delete_from_docs(docs: dict, path: list):
    d = copy.deepcopy(docs)
    cur = d
    for p in path[:-1]:
        cur = cur[p]
    del cur[path[-1]]
    return d


# ======================================================================
# Schema directory fixture for validator tests
# ======================================================================
@pytest.fixture(scope="session")
def schema_dir(tmp_path_factory):
    out_dir = tmp_path_factory.mktemp("schemas")
    import importlib.util
    spec = importlib.util.spec_from_file_location("make_schemas", ROOT / "scripts" / "pipeline" / "make_schemas.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.write_all(out_dir, overwrite=False)
    return out_dir


def run_validation(adhyay, docs, ctx, schema_dir):
    return validate_stage1(adhyay, docs, ctx, schema_dir=schema_dir)


# ======================================================================
# Tests
# ======================================================================
class TestValidateStage1:
    # --- Baseline ---
    def test_fully_valid_returns_empty(self, schema_dir):
        docs = make_valid_docs(1)
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert errs == [], f"expected no errors, got: {errs}"

    # --- Phase control ---
    def test_schema_error_stops_early(self, schema_dir):
        """Schema errors in multiple docs; adhyay mismatch also present.
        Should return ALL schema errors and NO semantic errors."""
        docs = make_valid_docs(1)
        # Introduce schema errors in two documents
        docs["story_map"]["ovi_types"] = [{"ovi": 1}]  # missing type
        docs["coverage"]["ovis"] = [{"ovi": 1}]  # missing disposition
        # Also introduce adhyay mismatch in a third document (semantic, not schema)
        docs["scenes"]["adhyay"] = 2
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        # All schema errors present
        assert any("story_map" in e and "type" in e for e in errs)
        assert any("coverage" in e and "disposition" in e for e in errs)
        # No semantic errors (adhyay mismatch is step 2, should not run)
        assert not any("scenes adhyay 2 does not match 1" in e for e in errs)

    def test_collects_all_semantic_steps(self, schema_dir):
        """Independent violations across steps 2-11; all should be reported."""
        docs = make_valid_docs(1)
        # Step 2: adhyay mismatch in coverage
        docs["coverage"]["adhyay"] = 2
        # Step 3: ovi untyped (remove ovi 2-5 from ovi_types)
        docs["story_map"]["ovi_types"] = [{"ovi": 1, "type": "STORY"}]
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
        errs = run_validation(1, docs, ctx, schema_dir)
        # Check each step's keywords appear
        keywords = [
            "coverage adhyay 2 does not match 1",
            "ovi 2 is untyped", "ovi 3 is untyped", "ovi 4 is untyped", "ovi 5 is untyped",
            "ovi 2 has no disposition", "ovi 1 is unfilmed but VISUALISED",
            "overlap", "S2-L1", "core", "discourse", "teaching_treatment",
            "consecutive", "unknown preset", "S1-L2", "line is in no shot beat",
            "prefix", "S2-1", "not belong",
            "source_ovis", "99", "outside", "arjuna", "known state", "battle_ready", "redecided",
            "arjuna", "no voice assigned", "voice not in the saved cast", "twice",
            "S99", "anchor_line_id", "bed_unknown", "kind", "mismatch",
            "Q1", "duplicate", "S99",
        ]
        for kw in keywords:
            assert any(kw in e for e in errs), f"missing keyword: {kw} in {errs}"

    # --- Step 2: adhyay mismatch ---
    @pytest.mark.parametrize("doc_key", [
        "story_map", "coverage", "scenes", "shots", "briefs", "looks", "voices", "sounds", "questions"
    ])
    def test_adhyay_mismatch_in_document(self, schema_dir, doc_key):
        docs = make_valid_docs(1)
        docs[doc_key]["adhyay"] = 2
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any(f"{doc_key} adhyay 2 does not match 1" in e for e in errs)

    # --- Step 3: story_map semantic ---
    def test_ovi_untyped(self, schema_dir):
        docs = make_valid_docs(1)
        docs["story_map"]["ovi_types"] = [{"ovi": 1, "type": "STORY"}]
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("ovi 2 is untyped" in e for e in errs)
        assert any("ovi 3 is untyped" in e for e in errs)
        assert any("ovi 4 is untyped" in e for e in errs)
        assert any("ovi 5 is untyped" in e for e in errs)

    def test_ovi_typed_twice(self, schema_dir):
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
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("ovi 1 is typed twice" in e for e in errs)

    def test_typed_ovi_outside_chapter_reported(self, schema_dir):
        docs = make_valid_docs(1)
        docs["story_map"]["ovi_types"].append({"ovi": 99, "type": "STORY"})
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("ovi 99" in e and "outside" in e for e in errs)

    def test_event_ovi_range_lo_gt_hi(self, schema_dir):
        docs = make_valid_docs(1)
        docs["story_map"]["events"][0]["ovi_range"] = [5, 1]
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("E1" in e and ("ovi_range" in e or "range" in e) for e in errs)

    def test_event_key_ovis_outside_range(self, schema_dir):
        docs = make_valid_docs(1)
        docs["story_map"]["events"][0]["key_ovis"] = [99]
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("E1" in e and "key_ovis" in e and "range" in e for e in errs)

    # --- Step 4: coverage semantic ---
    def test_coverage_missing_disposition(self, schema_dir):
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"] = [{"ovi": 1, "disposition": "VISUALISED"}]
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("ovi 2 has no disposition" in e for e in errs)
        assert any("ovi 3 has no disposition" in e for e in errs)
        assert any("ovi 4 has no disposition" in e for e in errs)
        assert any("ovi 5 has no disposition" in e for e in errs)

    def test_coverage_duplicate_disposition(self, schema_dir):
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
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("ovi 1" in e and "twice" in e for e in errs)

    def test_propose_omission_note(self, schema_dir):
        """PROPOSE_OMISSION adds exactly one NOTE message starting with 'note: '."""
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"][4] = {"ovi": 5, "disposition": "PROPOSE_OMISSION", "reason": "redundant"}
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = run_validation(1, docs, ctx, schema_dir)
        notes = [e for e in errs if e.startswith("note: ")]
        errors = [e for e in errs if not e.startswith("note: ")]
        assert len(notes) == 1
        assert "note: ovi 5 omission proposed, owner approval needed" in notes[0]
        assert errors == []  # no errors, only the note

    def test_notes_follow_errors(self, schema_dir):
        """Notes (PROPOSE_OMISSION) come after all error messages."""
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"][4] = {"ovi": 5, "disposition": "PROPOSE_OMISSION", "reason": "redundant"}
        # Also add a real error: missing disposition for ovi 2
        docs["coverage"]["ovis"] = [
            {"ovi": 1, "disposition": "VISUALISED"},
            {"ovi": 5, "disposition": "PROPOSE_OMISSION", "reason": "redundant"},
        ]
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = run_validation(1, docs, ctx, schema_dir)
        note_indices = [i for i, e in enumerate(errs) if e.startswith("note: ")]
        error_indices = [i for i, e in enumerate(errs) if not e.startswith("note: ")]
        assert note_indices, "expected a note"
        assert error_indices, "expected an error"
        assert max(error_indices) < min(note_indices), "notes must follow errors"

    def test_unfilmed_ovi_visualised_error(self, schema_dir):
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"][0]["disposition"] = "VISUALISED"
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5}, unfilmed_ovis={1})
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("ovi 1 is unfilmed but VISUALISED" in e for e in errs)

    def test_covered_by_invalid_reference(self, schema_dir):
        """Well-formed but nonexistent line_id and ovi outside chapter."""
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"][3]["covered_by"] = "S1-L99"
        ctx = make_ctx(script_line_ids=["S1-L1"], chapter_ovis={1, 2, 3, 4, 5})
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("covered_by" in e and "S1-L99" in e for e in errs)
        docs["coverage"]["ovis"][3]["covered_by"] = 99
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("covered_by" in e and "99" in e for e in errs)

    # --- Step 5: scenes semantic ---
    def test_scene_ids_unique(self, schema_dir):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"].append({
            "scene_id": "S1", "section_kind": "story", "ovi_range": [3, 3], "goal": "dup",
            "turn": {"ovi": 3, "text": "x"}, "line_ids": [], "teaching_treatment": "none",
        })
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("S1" in e and "duplicate" in e.lower() for e in errs)

    def test_scene_range_lo_gt_hi(self, schema_dir):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][0]["ovi_range"] = [3, 1]
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("S1" in e and "ovi_range" in e for e in errs)

    def test_scene_ranges_overlap(self, schema_dir):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][1]["ovi_range"] = [2, 4]
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("overlap" in e.lower() for e in errs)

    def test_chapter_ovi_not_in_any_scene(self, schema_dir):
        docs = make_valid_docs(1)
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5, 6})
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("ovi 6" in e and ("not in any scene" in e or "uncovered" in e.lower()) for e in errs)

    def test_unfilmed_ovi_inside_scene_range_error(self, schema_dir):
        docs = make_valid_docs(1)
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5}, unfilmed_ovis={2})
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("S1" in e and "ovi 2 is unfilmed but inside the range" in e for e in errs)

    def test_ovi_outside_chapter_in_scene(self, schema_dir):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][0]["ovi_range"] = [1, 99]
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("S1" in e and "ovi 99" in e and "outside" in e for e in errs)

    def test_turn_ovi_outside_scene_range(self, schema_dir):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][0]["turn"]["ovi"] = 99
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("S1" in e and "turn" in e and "ovi" in e and "range" in e for e in errs)

    def test_line_id_not_in_script(self, schema_dir):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][0]["line_ids"] = ["S1-L99"]
        ctx = make_ctx(script_line_ids=["S1-L1"])
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("S1-L99" in e and ("not in the script" in e or "not in script" in e) for e in errs)

    def test_line_id_used_twice_across_scenes(self, schema_dir):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][1]["line_ids"] = ["S1-L1"]
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("S1-L1" in e and ("twice" in e or "duplicate" in e.lower()) for e in errs)

    def test_line_id_used_twice_within_scene(self, schema_dir):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][0]["line_ids"] = ["S1-L1", "S1-L1"]
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("S1-L1" in e and ("twice" in e or "duplicate" in e.lower()) for e in errs)

    def test_line_ids_not_in_script_order_within_scene(self, schema_dir):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][0]["line_ids"] = ["S1-L2", "S1-L1"]
        ctx = make_ctx(script_line_ids=["S1-L1", "S1-L2", "S2-L1"])
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("S1" in e and "order" in e.lower() for e in errs)

    def test_core_line_missing_from_scenes(self, schema_dir):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][1]["line_ids"] = []
        ctx = make_ctx(core_line_ids={"S1-L1", "S2-L1"})
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("S2-L1" in e and "core" in e.lower() and ("missing" in e.lower() or "not in any scene" in e) for e in errs)

    def test_discourse_scene_requires_treatment(self, schema_dir):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][1]["teaching_treatment"] = "none"
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("S2" in e and "discourse" in e.lower() and "teaching_treatment" in e for e in errs)

    # --- Step 6: shots semantic ---
    def test_shot_ids_unique(self, schema_dir):
        docs = make_valid_docs(1)
        docs["shots"]["shots"].append({
            "shot_id": "S1-1", "scene_id": "S1", "ovi_ids": [1], "beat_line_ids": ["S1-L1"],
            "preset": "01_wide", "need_new": None, "needs_cutout": False, "pose": "x", "framing": "x",
        })
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("S1-1" in e and "duplicate" in e.lower() for e in errs)

    def test_shot_sequence_starts_at_one(self, schema_dir):
        """Shots per scene must be consecutive starting from 1."""
        docs = make_valid_docs(1)
        docs["shots"]["shots"][0]["shot_id"] = "S1-2"  # S1-1 missing
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("S1" in e and ("consecutive" in e.lower() or "starts at 1" in e.lower() or "sequence" in e.lower()) for e in errs)

    def test_shot_not_consecutive(self, schema_dir):
        docs = make_valid_docs(1)
        docs["shots"]["shots"][1]["shot_id"] = "S1-3"
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("S1" in e and ("consecutive" in e.lower() or "sequence" in e.lower()) for e in errs)

    def test_shot_scene_not_exist(self, schema_dir):
        docs = make_valid_docs(1)
        docs["shots"]["shots"][0]["scene_id"] = "S99"
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("S99" in e and ("scene" in e and "not exist" in e or "unknown" in e.lower()) for e in errs)

    def test_shot_ovi_ids_outside_scene_range(self, schema_dir):
        docs = make_valid_docs(1)
        docs["shots"]["shots"][0]["ovi_ids"] = [99]
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("S1-1" in e and "ovi" in e and "99" in e and ("range" in e or "scene" in e) for e in errs)

    def test_shot_beat_line_ids_not_in_scene(self, schema_dir):
        docs = make_valid_docs(1)
        docs["shots"]["shots"][0]["beat_line_ids"] = ["S2-L1"]
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("S1-1" in e and "beat_line_ids" in e and ("scene" in e or "not belong" in e) for e in errs)

    def test_scene_with_no_shots(self, schema_dir):
        docs = make_valid_docs(1)
        docs["shots"]["shots"] = [s for s in docs["shots"]["shots"] if s["scene_id"] != "S2"]
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("S2" in e and ("no shots" in e or "has no shots" in e) for e in errs)

    def test_core_line_not_in_any_shot_beat(self, schema_dir):
        """Every line of every scene must be in some shot's beat_line_ids."""
        docs = make_valid_docs(1)
        # Remove S1-2 which covers S1-L2 (core line)
        docs["shots"]["shots"] = [s for s in docs["shots"]["shots"] if s["shot_id"] != "S1-2"]
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("S1-L2" in e and "line is in no shot beat" in e for e in errs)

    def test_shot_unknown_preset(self, schema_dir):
        docs = make_valid_docs(1)
        docs["shots"]["shots"][0]["preset"] = "99_unknown"
        ctx = make_ctx(preset_ids={"01_wide", "02_medium", "03_close"})
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("S1-1" in e and "unknown preset" in e and "99_unknown" in e for e in errs)

    def test_shot_need_new_accepted(self, schema_dir):
        """NEED_NEW shot with valid need_new object is accepted."""
        docs = make_valid_docs(1)
        docs["shots"]["shots"][0] = {
            "shot_id": "S1-1", "scene_id": "S1", "ovi_ids": [1], "beat_line_ids": ["S1-L1"],
            "preset": "NEED_NEW", "need_new": {"reason": "unique", "class": "missing_image"},
            "needs_cutout": False, "pose": "x", "framing": "x",
        }
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert errs == [], f"NEED_NEW shot rejected: {errs}"

    # --- Step 7: briefs semantic ---
    def test_image_ids_unique(self, schema_dir):
        docs = make_valid_docs(1)
        docs["briefs"]["images"].append({
            "image_id": "s1_arjuna_standing", "scene_id": "S1", "shot_ids": ["S1-1"],
            "people": [{"name": "A", "position": "c", "pose": "p", "gaze": "g"}],
            "place_id": "p", "prop": None, "prop_state": None, "camera": "c", "light": "l",
            "reason_new": "r", "on_screen_facts": ["f"],
            "references": {"characters": [], "place": "p", "style_anchor": "s", "prop": None},
        })
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("s1_arjuna_standing" in e and "duplicate" in e.lower() for e in errs)

    def test_brief_image_id_scene_prefix(self, schema_dir):
        docs = make_valid_docs(1)
        docs["briefs"]["images"][0]["image_id"] = "s9_wrong_prefix"
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        # Check for the mutated ID and prefix-related message
        assert any("s9_wrong_prefix" in e for e in errs)
        assert any("prefix" in e.lower() or "s1" in e.lower() for e in errs)

    def test_brief_scene_not_exist(self, schema_dir):
        docs = make_valid_docs(1)
        docs["briefs"]["images"][0]["scene_id"] = "S99"
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("S99" in e and ("scene" in e and "not exist" in e or "unknown" in e.lower()) for e in errs)

    def test_brief_shot_missing(self, schema_dir):
        docs = make_valid_docs(1)
        docs["briefs"]["images"][0]["shot_ids"] = ["S1-99"]
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("S1-99" in e and ("shot" in e and "not exist" in e or "unknown" in e.lower()) for e in errs)

    def test_brief_shot_not_in_scene(self, schema_dir):
        docs = make_valid_docs(1)
        docs["briefs"]["images"][0]["shot_ids"] = ["S2-1"]
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("S2-1" in e and ("scene" in e or "not belong" in e) for e in errs)

    def test_brief_empty_person_name(self, schema_dir):
        docs = make_valid_docs(1)
        docs["briefs"]["images"][0]["people"][0]["name"] = ""
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("name" in e and ("empty" in e or "missing" in e) for e in errs)

    def test_brief_empty_on_screen_facts(self, schema_dir):
        docs = make_valid_docs(1)
        docs["briefs"]["images"][0]["on_screen_facts"] = []
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("on_screen_facts" in e and ("empty" in e or "non-empty" in e) for e in errs)

    # --- Step 8: looks semantic ---
    def test_look_source_ovi_outside_chapter(self, schema_dir):
        docs = make_valid_docs(1)
        docs["looks"]["entries"][0]["source_ovis"] = [99]
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("arjuna" in e and "source_ovis" in e and "99" in e and "outside" in e for e in errs)

    def test_known_entity_redecided_same_state_id(self, schema_dir):
        docs = make_valid_docs(1)
        docs["looks"]["entries"][0] = {
            "entity_id": "arjuna", "kind": "character", "state_id": "battle_ready",
            "look": "different look", "source_ovis": [1], "basis": "inferred",
        }
        ctx = make_ctx(known_states={"arjuna": {"battle_ready"}, "krishna": {"charioteer"}, "battlefield": {"dawn_armies"}})
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("arjuna" in e and "known state" in e and "battle_ready" in e and "redecided" in e for e in errs)

    def test_known_entity_new_state_id_allowed(self, schema_dir):
        docs = make_valid_docs(1)
        docs["looks"]["entries"][0] = {
            "entity_id": "arjuna", "kind": "character", "state_id": "new_state",
            "look": "different", "source_ovis": [1], "basis": "inferred",
        }
        ctx = make_ctx(known_states={"arjuna": {"battle_ready"}, "krishna": {"charioteer"}, "battlefield": {"dawn_armies"}})
        errs = run_validation(1, docs, ctx, schema_dir)
        assert not any("redecided" in e for e in errs)
        assert errs == []

    def test_entity_state_unique(self, schema_dir):
        docs = make_valid_docs(1)
        docs["looks"]["entries"].append({
            "entity_id": "arjuna", "kind": "character", "state_id": "battle_ready_new",
            "look": "dup", "source_ovis": [2], "basis": "stated",
        })
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("arjuna" in e and "battle_ready_new" in e and ("duplicate" in e.lower() or "unique" in e.lower()) for e in errs)

    # --- Step 9: voices semantic ---
    def test_speaking_character_no_voice(self, schema_dir):
        docs = make_valid_docs(1)
        docs["voices"]["cast"] = []
        ctx = make_ctx(speaking_characters={"arjuna", "krishna"})
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("arjuna" in e and "no voice assigned" in e for e in errs)
        assert any("krishna" in e and "no voice assigned" in e for e in errs)

    def test_voice_key_not_in_saved(self, schema_dir):
        docs = make_valid_docs(1)
        docs["voices"]["cast"][0]["voice_key"] = "unknown_key"
        ctx = make_ctx(saved_voices={"arjuna_voice": "v_arjuna_001_valid_id"})
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("arjuna" in e and "voice not in the saved cast" in e for e in errs)

    def test_voice_id_mismatch_saved(self, schema_dir):
        docs = make_valid_docs(1)
        docs["voices"]["cast"][0]["voice_id"] = "v_different_valid_id_001"
        ctx = make_ctx(saved_voices={"arjuna_voice": "v_arjuna_001_valid_id"})
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("arjuna" in e and "voice not in the saved cast" in e for e in errs)

    def test_recurring_character_listed_twice(self, schema_dir):
        docs = make_valid_docs(1)
        docs["voices"]["cast"].append({
            "character_id": "arjuna", "voice_key": "arjuna_voice", "voice_id": "v_arjuna_001_valid_id",
            "gender": "male", "status": "RECURRING",
        })
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("arjuna" in e and ("twice" in e or "duplicate" in e.lower()) for e in errs)

    def test_speaking_character_duplicate_new_proposed(self, schema_dir):
        docs = make_valid_docs(1)
        docs["voices"]["cast"] = [
            {"character_id": "arjuna", "voice_key": "k1", "voice_id": "v_valid_id_001", "gender": "male", "status": "NEW_PROPOSED"},
            {"character_id": "arjuna", "voice_key": "k2", "voice_id": "v_valid_id_002", "gender": "male", "status": "NEW_PROPOSED"},
        ]
        ctx = make_ctx(speaking_characters={"arjuna"}, saved_voices={"k1": "v_valid_id_001", "k2": "v_valid_id_002"})
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("arjuna" in e and ("twice" in e or "duplicate" in e.lower()) for e in errs)

    def test_two_characters_share_voice_key(self, schema_dir):
        docs = make_valid_docs(1)
        docs["voices"]["cast"][1]["voice_key"] = "arjuna_voice"
        docs["voices"]["cast"][1]["voice_id"] = "v_arjuna_001_valid_id"
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("voice_key" in e and "shared" in e.lower() for e in errs)

    def test_narrator_can_share_voice_key(self, schema_dir):
        docs = make_valid_docs(1)
        docs["voices"]["cast"] = [
            {"character_id": "arjuna", "voice_key": "shared_voice", "voice_id": "v_shared_valid_id_001", "gender": "male", "status": "RECURRING"},
            {"character_id": "narrator", "voice_key": "shared_voice", "voice_id": "v_shared_valid_id_001", "gender": "male", "status": "RECURRING"},
        ]
        ctx = make_ctx(
            speaking_characters={"arjuna", "narrator"},
            saved_voices={"shared_voice": "v_shared_valid_id_001"},
        )
        errs = run_validation(1, docs, ctx, schema_dir)
        assert not any("shared" in e.lower() for e in errs)
        assert errs == []

    # --- Step 10: sounds semantic ---
    def test_sound_scene_not_exist(self, schema_dir):
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0]["scene_id"] = "S99"
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("S99" in e and ("scene" in e and "not exist" in e or "unknown" in e.lower()) for e in errs)

    def test_sound_anchor_line_not_in_scene(self, schema_dir):
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0]["anchor_line_id"] = "S2-L1"
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("S1" in e and "anchor_line_id" in e and ("scene" in e or "not belong" in e) for e in errs)

    def test_sound_id_unknown(self, schema_dir):
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0]["sound_id"] = "bed_unknown"
        ctx = make_ctx(sound_ids={"bed_battlefield"})
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("bed_unknown" in e and ("unknown" in e.lower() or "not in" in e) for e in errs)

    def test_sound_need_new_without_prompt_schema_catches(self, schema_dir):
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0] = {
            "scene_id": "S1", "anchor_line_id": "S1-L1", "sound_id": "NEED_NEW",
            "kind": "fx", "purpose": "test", "basis": "stated",
        }
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("sound_prompt" in e for e in errs)

    def test_sound_non_need_new_with_prompt(self, schema_dir):
        """Non-NEED_NEW cue carrying sound_prompt is a SCHEMA error."""
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0]["sound_prompt"] = "should not be here"
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("sound_prompt" in e for e in errs)

    def test_sound_kind_mismatch_prefix(self, schema_dir):
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0]["sound_id"] = "fx_conch"
        docs["sounds"]["cues"][0]["kind"] = "bed"
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("fx_conch" in e and "kind" in e and ("mismatch" in e or "prefix" in e) for e in errs)

    def test_sound_need_new_accepted(self, schema_dir):
        """NEED_NEW sound with sound_prompt is accepted."""
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0] = {
            "scene_id": "S1", "anchor_line_id": "S1-L1", "sound_id": "NEED_NEW",
            "kind": "fx", "sound_prompt": "conch blow", "purpose": "signal", "basis": "stated",
        }
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert errs == [], f"NEED_NEW sound rejected: {errs}"

    # --- Step 11: questions semantic ---
    def test_question_duplicate_id(self, schema_dir):
        docs = make_valid_docs(1)
        docs["questions"]["questions"].append({"id": "Q1", "text": "dup"})
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("Q1" in e and ("duplicate" in e.lower() or "unique" in e.lower()) for e in errs)

    def test_question_scene_not_exist(self, schema_dir):
        docs = make_valid_docs(1)
        docs["questions"]["questions"][0]["scene_id"] = "S99"
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("S99" in e and ("scene" in e and "not exist" in e or "unknown" in e.lower()) for e in errs)

    # --- Zero-story chapter ---
    def test_zero_story_chapter_validates(self, schema_dir):
        """All ovis TEACHING/PHILOSOPHY, one discourse scene, no story events."""
        docs = {
            "story_map": {
                "adhyay": 2,
                "ovi_types": [
                    {"ovi": 1, "type": "TEACHING"},
                    {"ovi": 2, "type": "PHILOSOPHY"},
                ],
                "events": [
                    {"event_id": "E1", "title": "Teaching", "ovi_range": [1, 2], "key_ovis": [1, 2], "kind": "discourse", "closure": "RESOLVED_IN_ADHYAY"},
                ],
            },
            "coverage": {"adhyay": 2, "ovis": [{"ovi": 1, "disposition": "NARRATED"}, {"ovi": 2, "disposition": "QUOTED"}]},
            "scenes": {"adhyay": 2, "scenes": [{"scene_id": "S1", "section_kind": "discourse", "ovi_range": [1, 2], "goal": "Teaching", "turn": {"ovi": 1, "text": "Krishna teaches"}, "line_ids": ["S1-L1"], "teaching_treatment": "contemplative_hold"}]},
            "shots": {"adhyay": 2, "shots": [{"shot_id": "S1-1", "scene_id": "S1", "ovi_ids": [1, 2], "beat_line_ids": ["S1-L1"], "preset": "01_wide", "need_new": None, "needs_cutout": False, "pose": "seated", "framing": "medium"}]},
            "briefs": {"adhyay": 2, "images": [{"image_id": "s1_krishna_teaching", "scene_id": "S1", "shot_ids": ["S1-1"], "people": [{"name": "Krishna", "position": "center", "pose": "seated", "gaze": "forward"}], "place_id": "chariot", "prop": None, "prop_state": None, "camera": "eye level", "light": "soft", "reason_new": "teaching", "on_screen_facts": ["Krishna teaches"], "references": {"characters": ["Krishna"], "place": "chariot", "style_anchor": "epic realism", "prop": None}}]},
            "looks": {"adhyay": 2, "entries": [{"entity_id": "krishna", "kind": "character", "state_id": "teacher", "look": "peacock feather", "source_ovis": [1, 2], "basis": "stated"}]},
            "voices": {"adhyay": 2, "cast": [{"character_id": "krishna", "voice_key": "krishna_voice", "voice_id": "v_krishna_001_valid_id", "gender": "male", "status": "RECURRING"}]},
            "sounds": {"adhyay": 2, "cues": [{"scene_id": "S1", "anchor_line_id": "S1-L1", "sound_id": "bed_battlefield", "kind": "bed", "purpose": "ambience", "basis": "staging"}]},
            "questions": {"adhyay": 2, "questions": [{"id": "Q1", "text": "What is yoga?"}]},
        }
        ctx = make_ctx(
            script_line_ids=["S1-L1"], core_line_ids={"S1-L1"}, chapter_ovis={1, 2},
            unfilmed_ovis=set(), preset_ids={"01_wide"}, sound_ids={"bed_battlefield"},
            saved_voices={"krishna_voice": "v_krishna_001_valid_id"}, speaking_characters={"krishna"},
            known_states={"krishna": {"charioteer"}, "chariot": {"interior"}},
        )
        errs = run_validation(2, docs, ctx, schema_dir)
        assert errs == [], f"zero-story chapter failed: {errs}"

    def test_zero_story_empty_events_validates(self, schema_dir):
        """Zero-story chapter with empty events array is valid."""
        docs = {
            "story_map": {"adhyay": 3, "ovi_types": [{"ovi": 1, "type": "TEACHING"}, {"ovi": 2, "type": "PHILOSOPHY"}], "events": []},
            "coverage": {"adhyay": 3, "ovis": [{"ovi": 1, "disposition": "NARRATED"}, {"ovi": 2, "disposition": "QUOTED"}]},
            "scenes": {"adhyay": 3, "scenes": [{"scene_id": "S1", "section_kind": "discourse", "ovi_range": [1, 2], "goal": "Teaching", "turn": {"ovi": 1, "text": "Krishna teaches"}, "line_ids": ["S1-L1"], "teaching_treatment": "contemplative_hold"}]},
            "shots": {"adhyay": 3, "shots": [{"shot_id": "S1-1", "scene_id": "S1", "ovi_ids": [1, 2], "beat_line_ids": ["S1-L1"], "preset": "01_wide", "need_new": None, "needs_cutout": False, "pose": "seated", "framing": "medium"}]},
            "briefs": {"adhyay": 3, "images": [{"image_id": "s1_krishna_teaching", "scene_id": "S1", "shot_ids": ["S1-1"], "people": [{"name": "Krishna", "position": "center", "pose": "seated", "gaze": "forward"}], "place_id": "chariot", "prop": None, "prop_state": None, "camera": "eye level", "light": "soft", "reason_new": "teaching", "on_screen_facts": ["Krishna teaches"], "references": {"characters": ["Krishna"], "place": "chariot", "style_anchor": "epic realism", "prop": None}}]},
            "looks": {"adhyay": 3, "entries": [{"entity_id": "krishna", "kind": "character", "state_id": "teacher", "look": "peacock feather", "source_ovis": [1, 2], "basis": "stated"}]},
            "voices": {"adhyay": 3, "cast": [{"character_id": "krishna", "voice_key": "krishna_voice", "voice_id": "v_krishna_001_valid_id", "gender": "male", "status": "RECURRING"}]},
            "sounds": {"adhyay": 3, "cues": [{"scene_id": "S1", "anchor_line_id": "S1-L1", "sound_id": "bed_battlefield", "kind": "bed", "purpose": "ambience", "basis": "staging"}]},
            "questions": {"adhyay": 3, "questions": [{"id": "Q1", "text": "What is yoga?"}]},
        }
        ctx = make_ctx(
            script_line_ids=["S1-L1"], core_line_ids={"S1-L1"}, chapter_ovis={1, 2},
            unfilmed_ovis=set(), preset_ids={"01_wide"}, sound_ids={"bed_battlefield"},
            saved_voices={"krishna_voice": "v_krishna_001_valid_id"}, speaking_characters={"krishna"},
            known_states={"krishna": {"charioteer"}, "chariot": {"interior"}},
        )
        errs = run_validation(3, docs, ctx, schema_dir)
        assert errs == [], f"zero-story empty events failed: {errs}"

    # --- Stability ---
    def test_messages_stable_order(self, schema_dir):
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"] = []
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs1 = run_validation(1, docs, ctx, schema_dir)
        errs2 = run_validation(1, docs, ctx, schema_dir)
        assert errs1 == errs2, "error order not stable"
        assert any("ovi 1 has no disposition" in e for e in errs1)
        assert any("ovi 2 has no disposition" in e for e in errs1)

    def test_message_prefixes(self, schema_dir):
        """Each message starts with item id or document name."""
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"] = []
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = run_validation(1, docs, ctx, schema_dir)
        for e in errs:
            assert e.startswith("note: ") or any(e.startswith(prefix) for prefix in [
                "story_map", "coverage", "scenes", "shots", "briefs", "looks", "voices", "sounds", "questions",
                "S1", "S2", "E1", "E2", "Q1", "Q2", "ovi 1", "ovi 2", "ovi 3", "ovi 4", "ovi 5",
                "s1_", "s2_", "arjuna", "krishna", "battlefield"
            ]), f"message lacks required prefix: {e}"

    # --- Missing references never raise ---
    def test_missing_references_no_exception(self, schema_dir):
        """Validator never raises, only returns error strings.
        Empty context should produce specific missing-reference diagnostics."""
        docs = make_valid_docs(1)
        ctx = make_ctx(
            script_line_ids=[], core_line_ids=set(), chapter_ovis=set(),
            unfilmed_ovis=set(), preset_ids=set(), sound_ids=set(),
            saved_voices={}, speaking_characters=set(), known_states={},
        )
        errs = run_validation(1, docs, ctx, schema_dir)
        assert isinstance(errs, list)
        assert all(isinstance(e, str) for e in errs)
        # Should have specific missing-reference errors
        assert any("S1-L1" in e and "not in the script" in e for e in errs)
        assert any("01_wide" in e and "unknown preset" in e for e in errs)

    def test_empty_context_survives(self):
        """Intentionally empty sets/dicts in context are not replaced by defaults."""
        ctx = make_ctx(
            script_line_ids=[], core_line_ids=set(), chapter_ovis=set(),
            unfilmed_ovis=set(), preset_ids=set(), sound_ids=set(),
            saved_voices={}, speaking_characters=set(), known_states={},
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
    def test_broken_implementation_extra_fields_ignored(self, schema_dir):
        docs = make_valid_docs(1)
        docs["story_map"]["extra_top_level"] = "ignored"
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("additionalProperties" in e or "extra_top_level" in e for e in errs)

    def test_broken_implementation_wrong_type_not_caught_by_schema(self, schema_dir):
        docs = make_valid_docs(1)
        docs["story_map"]["ovi_types"] = [{"ovi": "one", "type": "STORY"}]
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("ovi" in e and ("type" in e or "integer" in e) for e in errs)

    def test_broken_implementation_missing_required_field(self, schema_dir):
        docs = make_valid_docs(1)
        del docs["scenes"]["scenes"][0]["goal"]
        ctx = make_ctx()
        errs = run_validation(1, docs, ctx, schema_dir)
        assert any("goal" in e and ("required" in e or "missing" in e) for e in errs)
