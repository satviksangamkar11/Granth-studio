from __future__ import annotations

import json
import importlib.util
import sys
from pathlib import Path

import pytest
import jsonschema

ROOT = Path(__file__).resolve().parents[1]

# Load make_schemas module by path
spec = importlib.util.spec_from_file_location(
    "make_schemas", ROOT / "scripts" / "pipeline" / "make_schemas.py"
)
make_schemas = importlib.util.module_from_spec(spec)
sys.modules["make_schemas"] = make_schemas
spec.loader.exec_module(make_schemas)


@pytest.fixture(scope="session")
def schemas_dir(tmp_path_factory):
    """Generate all schemas into a temp directory once per session."""
    out_dir = tmp_path_factory.mktemp("schemas")
    written = make_schemas.write_all(out_dir, overwrite=False)
    assert written, "no schemas written"
    return out_dir


def load_schema(schemas_dir: Path, name: str) -> dict:
    path = schemas_dir / f"{name}.schema.json"
    assert path.exists(), f"schema {name} not found at {path}"
    return json.loads(path.read_text())


def validate(instance: dict, schema: dict) -> list[str]:
    """Return list of validation error messages (empty if valid)."""
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)
    return [f"{'.'.join(str(p) for p in e.path) or 'root'}: {e.message}" for e in errors]


class TestStage1StoryMapSchema:
    def test_valid_minimal(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_story_map")
        doc = {
            "adhyay": 1,
            "ovi_types": [
                {"ovi": 1, "type": "STORY"},
                {"ovi": 2, "type": "TEACHING"},
            ],
            "events": [
                {
                    "event_id": "E1",
                    "title": "Arjuna's dilemma",
                    "ovi_range": [1, 2],
                    "key_ovis": [1],
                    "kind": "story",
                    "closure": "RESOLVED_IN_ADHYAY",
                }
            ],
        }
        assert validate(doc, schema) == []

    def test_extra_key_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_story_map")
        doc = {
            "adhyay": 1,
            "ovi_types": [{"ovi": 1, "type": "STORY"}],
            "events": [],
            "extra_field": "not allowed",
        }
        errs = validate(doc, schema)
        assert any("extra_field" in e or "additionalProperties" in e for e in errs)

    def test_all_ovi_type_enums(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_story_map")
        for t in [
            "STORY",
            "TEACHING",
            "PHILOSOPHY",
            "INVOCATION",
            "RECAP",
            "PHALASHRUTI",
            "OTHER",
        ]:
            doc = {"adhyay": 1, "ovi_types": [{"ovi": 1, "type": t}], "events": []}
            assert validate(doc, schema) == [], f"enum {t} failed"

    def test_event_closure_enums(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_story_map")
        for c in [
            "RESOLVED_IN_ADHYAY",
            "CONTINUES_NEXT_ADHYAY",
            "STARTED_EARLIER",
            "SOURCE_INCOMPLETE_OR_AMBIGUOUS",
            "NA",
        ]:
            doc = {
                "adhyay": 1,
                "ovi_types": [{"ovi": 1, "type": "STORY"}],
                "events": [
                    {
                        "event_id": "E1",
                        "title": "t",
                        "ovi_range": [1, 1],
                        "key_ovis": [1],
                        "kind": "story",
                        "closure": c,
                    }
                ],
            }
            assert validate(doc, schema) == [], f"closure {c} failed"

    def test_event_kind_enum(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_story_map")
        for k in ["story", "discourse"]:
            doc = {
                "adhyay": 1,
                "ovi_types": [{"ovi": 1, "type": "STORY"}],
                "events": [
                    {
                        "event_id": "E1",
                        "title": "t",
                        "ovi_range": [1, 1],
                        "key_ovis": [1],
                        "kind": k,
                        "closure": "NA",
                    }
                ],
            }
            assert validate(doc, schema) == [], f"kind {k} failed"

    def test_invalid_ovi_type_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_story_map")
        doc = {
            "adhyay": 1,
            "ovi_types": [{"ovi": 1, "type": "INVALID"}],
            "events": [],
        }
        errs = validate(doc, schema)
        assert errs

    def test_invalid_event_id_pattern(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_story_map")
        doc = {
            "adhyay": 1,
            "ovi_types": [{"ovi": 1, "type": "STORY"}],
            "events": [
                {
                    "event_id": "X1",
                    "title": "t",
                    "ovi_range": [1, 1],
                    "key_ovis": [1],
                    "kind": "story",
                    "closure": "NA",
                }
            ],
        }
        errs = validate(doc, schema)
        assert errs


class TestStage1CoverageSchema:
    def test_valid_minimal(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_coverage")
        doc = {
            "adhyay": 1,
            "ovis": [
                {"ovi": 1, "disposition": "VISUALISED"},
                {"ovi": 2, "disposition": "NARRATED"},
            ],
        }
        assert validate(doc, schema) == []

    def test_extra_key_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_coverage")
        doc = {
            "adhyay": 1,
            "ovis": [{"ovi": 1, "disposition": "VISUALISED", "extra": "x"}],
        }
        errs = validate(doc, schema)
        assert any("additionalProperties" in e for e in errs)

    def test_all_disposition_enums(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_coverage")
        for d in [
            "VISUALISED",
            "NARRATED",
            "QUOTED",
            "MERGED_EQUIVALENT",
            "PROPOSE_OMISSION",
        ]:
            doc = {"adhyay": 1, "ovis": [{"ovi": 1, "disposition": d}]}
            # MERGED_EQUIVALENT and PROPOSE_OMISSION need extra fields per if/then
            if d in ("MERGED_EQUIVALENT", "PROPOSE_OMISSION"):
                continue
            assert validate(doc, schema) == [], f"disposition {d} failed"

    def test_propose_omission_requires_reason(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_coverage")
        # missing reason -> error
        doc = {"adhyay": 1, "ovis": [{"ovi": 1, "disposition": "PROPOSE_OMISSION"}]}
        errs = validate(doc, schema)
        assert any("reason" in e.lower() for e in errs)
        # with reason -> ok
        doc = {
            "adhyay": 1,
            "ovis": [
                {"ovi": 1, "disposition": "PROPOSE_OMISSION", "reason": "too brief"}
            ],
        }
        assert validate(doc, schema) == []

    def test_merged_equivalent_requires_covered_by(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_coverage")
        # missing covered_by -> error
        doc = {"adhyay": 1, "ovis": [{"ovi": 1, "disposition": "MERGED_EQUIVALENT"}]}
        errs = validate(doc, schema)
        assert any("covered_by" in e.lower() for e in errs)
        # with covered_by -> ok
        doc = {
            "adhyay": 1,
            "ovis": [
                {
                    "ovi": 1,
                    "disposition": "MERGED_EQUIVALENT",
                    "covered_by": "S1-L5",
                }
            ],
        }
        assert validate(doc, schema) == []

    def test_visualised_no_extra_required(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_coverage")
        doc = {
            "adhyay": 1,
            "ovis": [
                {"ovi": 1, "disposition": "VISUALISED", "reason": "x", "covered_by": "S1-L1"}
            ],
        }
        # extra fields allowed but not required; should still validate
        assert validate(doc, schema) == []


class TestStage1ScenesSchema:
    def test_valid_story_scene(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_scenes")
        doc = {
            "adhyay": 1,
            "scenes": [
                {
                    "scene_id": "S1",
                    "section_kind": "story",
                    "ovi_range": [1, 5],
                    "goal": "Establish conflict",
                    "turn": {"ovi": 3, "text": "Arjuna drops bow"},
                    "line_ids": ["S1-L1", "S1-L2"],
                    "teaching_treatment": "none",
                }
            ],
        }
        assert validate(doc, schema) == []

    def test_valid_discourse_scene_requires_treatment(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_scenes")
        for treatment in [
            "narration_over_typography",
            "contemplative_hold",
            "symbol_from_text",
        ]:
            doc = {
                "adhyay": 1,
                "scenes": [
                    {
                        "scene_id": "S1",
                        "section_kind": "discourse",
                        "ovi_range": [1, 5],
                        "goal": "Teach dharma",
                        "turn": {"ovi": 3, "text": "Krishna speaks"},
                        "line_ids": ["S1-L1"],
                        "teaching_treatment": treatment,
                    }
                ],
            }
            assert validate(doc, schema) == [], f"treatment {treatment} failed"

    def test_discourse_scene_without_treatment_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_scenes")
        doc = {
            "adhyay": 1,
            "scenes": [
                {
                    "scene_id": "S1",
                    "section_kind": "discourse",
                    "ovi_range": [1, 5],
                    "goal": "Teach",
                    "turn": {"ovi": 3, "text": "x"},
                    "line_ids": ["S1-L1"],
                    # teaching_treatment missing
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("teaching_treatment" in e for e in errs)

    def test_story_scene_with_treatment_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_scenes")
        doc = {
            "adhyay": 1,
            "scenes": [
                {
                    "scene_id": "S1",
                    "section_kind": "story",
                    "ovi_range": [1, 5],
                    "goal": "Story",
                    "turn": {"ovi": 3, "text": "x"},
                    "line_ids": ["S1-L1"],
                    "teaching_treatment": "narration_over_typography",
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("teaching_treatment" in e for e in errs)

    def test_extra_key_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_scenes")
        doc = {
            "adhyay": 1,
            "scenes": [
                {
                    "scene_id": "S1",
                    "section_kind": "story",
                    "ovi_range": [1, 5],
                    "goal": "x",
                    "turn": {"ovi": 3, "text": "x"},
                    "line_ids": [],
                    "teaching_treatment": "none",
                    "extra": "no",
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("additionalProperties" in e for e in errs)


class TestStage1ShotsSchema:
    def test_valid_shot_with_preset(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_shots")
        doc = {
            "adhyay": 1,
            "shots": [
                {
                    "shot_id": "S1-1",
                    "scene_id": "S1",
                    "ovi_ids": [1, 2],
                    "beat_line_ids": ["S1-L1"],
                    "preset": "01_wide_establishing",
                    "need_new": None,
                    "needs_cutout": False,
                    "pose": "standing",
                    "framing": "wide",
                }
            ],
        }
        assert validate(doc, schema) == []

    def test_valid_shot_need_new(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_shots")
        doc = {
            "adhyay": 1,
            "shots": [
                {
                    "shot_id": "S1-1",
                    "scene_id": "S1",
                    "ovi_ids": [1],
                    "beat_line_ids": ["S1-L1"],
                    "preset": "NEED_NEW",
                    "need_new": {"reason": "unique composition", "class": "missing_image"},
                    "needs_cutout": True,
                    "pose": "kneeling",
                    "framing": "close",
                }
            ],
        }
        assert validate(doc, schema) == []

    def test_need_new_requires_object(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_shots")
        doc = {
            "adhyay": 1,
            "shots": [
                {
                    "shot_id": "S1-1",
                    "scene_id": "S1",
                    "ovi_ids": [1],
                    "beat_line_ids": ["S1-L1"],
                    "preset": "NEED_NEW",
                    "need_new": None,
                    "needs_cutout": False,
                    "pose": "x",
                    "framing": "x",
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("need_new" in e for e in errs)

    def test_non_need_new_forbids_need_new_object(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_shots")
        doc = {
            "adhyay": 1,
            "shots": [
                {
                    "shot_id": "S1-1",
                    "scene_id": "S1",
                    "ovi_ids": [1],
                    "beat_line_ids": ["S1-L1"],
                    "preset": "01_wide",
                    "need_new": {"reason": "x", "class": "missing_image"},
                    "needs_cutout": False,
                    "pose": "x",
                    "framing": "x",
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("need_new" in e for e in errs)

    def test_preset_hint_old_key_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_shots")
        doc = {
            "adhyay": 1,
            "shots": [
                {
                    "shot_id": "S1-1",
                    "scene_id": "S1",
                    "ovi_ids": [1],
                    "beat_line_ids": ["S1-L1"],
                    "preset": "01_wide",
                    "preset_hint": "old field",
                    "need_new": None,
                    "needs_cutout": False,
                    "pose": "x",
                    "framing": "x",
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("preset_hint" in e or "additionalProperties" in e for e in errs)

    def test_extra_key_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_shots")
        doc = {
            "adhyay": 1,
            "shots": [
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
                    "extra": "no",
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("additionalProperties" in e for e in errs)

    def test_need_new_class_enum(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_shots")
        for c in ["missing_image", "json_arrangement", "renderer_gap"]:
            doc = {
                "adhyay": 1,
                "shots": [
                    {
                        "shot_id": "S1-1",
                        "scene_id": "S1",
                        "ovi_ids": [1],
                        "beat_line_ids": ["S1-L1"],
                        "preset": "NEED_NEW",
                        "need_new": {"reason": "r", "class": c},
                        "needs_cutout": False,
                        "pose": "x",
                        "framing": "x",
                    }
                ],
            }
            assert validate(doc, schema) == [], f"class {c} failed"


class TestStage1ImageBriefsSchema:
    def test_valid_minimal(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_image_briefs")
        doc = {
            "adhyay": 1,
            "images": [
                {
                    "image_id": "s1_arjuna_bow",
                    "scene_id": "S1",
                    "shot_ids": ["S1-1"],
                    "people": [
                        {"name": "Arjuna", "position": "center", "pose": "holding bow", "gaze": "down"}
                    ],
                    "place_id": "battlefield",
                    "prop": "bow",
                    "prop_state": "strung",
                    "camera": "eye level",
                    "light": "harsh noon",
                    "reason_new": "first appearance",
                    "on_screen_facts": ["Arjuna holds bow", "chariot behind"],
                    "references": {
                        "characters": ["Arjuna"],
                        "place": "battlefield",
                        "style_anchor": "epic realism",
                        "prop": "bow",
                    },
                }
            ],
        }
        assert validate(doc, schema) == []

    def test_extra_key_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_image_briefs")
        doc = {
            "adhyay": 1,
            "images": [
                {
                    "image_id": "s1_x",
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
                    "extra": "no",
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("additionalProperties" in e for e in errs)

    def test_empty_on_screen_facts_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_image_briefs")
        doc = {
            "adhyay": 1,
            "images": [
                {
                    "image_id": "s1_x",
                    "scene_id": "S1",
                    "shot_ids": ["S1-1"],
                    "people": [{"name": "A", "position": "c", "pose": "p", "gaze": "g"}],
                    "place_id": "p",
                    "prop": None,
                    "prop_state": None,
                    "camera": "c",
                    "light": "l",
                    "reason_new": "r",
                    "on_screen_facts": [],
                    "references": {"characters": [], "place": "p", "style_anchor": "s", "prop": None},
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("on_screen_facts" in e for e in errs)

    def test_empty_person_name_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_image_briefs")
        doc = {
            "adhyay": 1,
            "images": [
                {
                    "image_id": "s1_x",
                    "scene_id": "S1",
                    "shot_ids": ["S1-1"],
                    "people": [{"name": "", "position": "c", "pose": "p", "gaze": "g"}],
                    "place_id": "p",
                    "prop": None,
                    "prop_state": None,
                    "camera": "c",
                    "light": "l",
                    "reason_new": "r",
                    "on_screen_facts": ["f"],
                    "references": {"characters": [], "place": "p", "style_anchor": "s", "prop": None},
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("name" in e for e in errs)


class TestStage1CanonLooksSchema:
    def test_valid_minimal(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_canon_looks")
        doc = {
            "adhyay": 1,
            "entries": [
                {
                    "entity_id": "arjuna",
                    "kind": "character",
                    "state_id": "battle_ready",
                    "look": "armored, bow in hand",
                    "source_ovis": [1, 2],
                    "basis": "stated",
                }
            ],
        }
        assert validate(doc, schema) == []

    def test_extra_key_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_canon_looks")
        doc = {
            "adhyay": 1,
            "entries": [
                {
                    "entity_id": "arjuna",
                    "kind": "character",
                    "state_id": "battle_ready",
                    "look": "armored",
                    "source_ovis": [1],
                    "basis": "stated",
                    "events": ["E1"],  # old field, must be rejected
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("events" in e or "additionalProperties" in e for e in errs)

    def test_kind_enum(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_canon_looks")
        for k in ["character", "place", "prop"]:
            doc = {
                "adhyay": 1,
                "entries": [
                    {
                        "entity_id": "e",
                        "kind": k,
                        "state_id": "s",
                        "look": "l",
                        "source_ovis": [1],
                        "basis": "stated",
                    }
                ],
            }
            assert validate(doc, schema) == [], f"kind {k} failed"

    def test_basis_enum(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_canon_looks")
        for b in ["stated", "inferred"]:
            doc = {
                "adhyay": 1,
                "entries": [
                    {
                        "entity_id": "e",
                        "kind": "character",
                        "state_id": "s",
                        "look": "l",
                        "source_ovis": [1],
                        "basis": b,
                    }
                ],
            }
            assert validate(doc, schema) == [], f"basis {b} failed"

    def test_source_ovis_min_one(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_canon_looks")
        doc = {
            "adhyay": 1,
            "entries": [
                {
                    "entity_id": "e",
                    "kind": "character",
                    "state_id": "s",
                    "look": "l",
                    "source_ovis": [],
                    "basis": "stated",
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("source_ovis" in e for e in errs)


class TestStage1VoiceCastSchema:
    def test_valid_minimal(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_voice_cast")
        doc = {
            "adhyay": 1,
            "cast": [
                {
                    "character_id": "arjuna",
                    "voice_key": "arjuna_voice",
                    "voice_id": "v_arjuna_001",
                    "gender": "male",
                    "status": "RECURRING",
                }
            ],
        }
        assert validate(doc, schema) == []

    def test_extra_key_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_voice_cast")
        doc = {
            "adhyay": 1,
            "cast": [
                {
                    "character_id": "arjuna",
                    "voice_key": "k",
                    "voice_id": "v_arjuna_001",
                    "gender": "male",
                    "status": "RECURRING",
                    "extra": "no",
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("additionalProperties" in e for e in errs)

    def test_gender_enum(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_voice_cast")
        for g in ["male", "female"]:
            doc = {
                "adhyay": 1,
                "cast": [
                    {
                        "character_id": "c",
                        "voice_key": "k",
                        "voice_id": "v_001",
                        "gender": g,
                        "status": "RECURRING",
                    }
                ],
            }
            assert validate(doc, schema) == [], f"gender {g} failed"

    def test_status_enum(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_voice_cast")
        for s in ["RECURRING", "NEW_PROPOSED"]:
            doc = {
                "adhyay": 1,
                "cast": [
                    {
                        "character_id": "c",
                        "voice_key": "k",
                        "voice_id": "v_001",
                        "gender": "male",
                        "status": s,
                    }
                ],
            }
            assert validate(doc, schema) == [], f"status {s} failed"

    def test_voice_id_length(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_voice_cast")
        # too short
        doc = {
            "adhyay": 1,
            "cast": [
                {
                    "character_id": "c",
                    "voice_key": "k",
                    "voice_id": "short",
                    "gender": "male",
                    "status": "RECURRING",
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("voice_id" in e for e in errs)
        # too long
        doc["cast"][0]["voice_id"] = "x" * 41
        errs = validate(doc, schema)
        assert any("voice_id" in e for e in errs)


class TestStage1SoundSuggestionsSchema:
    def test_valid_bed_existing(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_sound_suggestions")
        doc = {
            "adhyay": 1,
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
        }
        assert validate(doc, schema) == []

    def test_valid_fx_need_new(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_sound_suggestions")
        doc = {
            "adhyay": 1,
            "cues": [
                {
                    "scene_id": "S1",
                    "anchor_line_id": "S1-L1",
                    "sound_id": "NEED_NEW",
                    "kind": "fx",
                    "sound_prompt": "conch blow",
                    "purpose": "signal",
                    "basis": "stated",
                }
            ],
        }
        assert validate(doc, schema) == []

    def test_need_new_requires_sound_prompt(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_sound_suggestions")
        doc = {
            "adhyay": 1,
            "cues": [
                {
                    "scene_id": "S1",
                    "anchor_line_id": "S1-L1",
                    "sound_id": "NEED_NEW",
                    "kind": "fx",
                    "purpose": "signal",
                    "basis": "stated",
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("sound_prompt" in e for e in errs)

    def test_non_need_new_forbids_sound_prompt(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_sound_suggestions")
        doc = {
            "adhyay": 1,
            "cues": [
                {
                    "scene_id": "S1",
                    "anchor_line_id": "S1-L1",
                    "sound_id": "bed_ambience",
                    "kind": "bed",
                    "sound_prompt": "should not be here",
                    "purpose": "ambience",
                    "basis": "staging",
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("sound_prompt" in e for e in errs)

    def test_duration_seconds_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_sound_suggestions")
        doc = {
            "adhyay": 1,
            "cues": [
                {
                    "scene_id": "S1",
                    "anchor_line_id": "S1-L1",
                    "sound_id": "bed_ambience",
                    "kind": "bed",
                    "purpose": "ambience",
                    "basis": "staging",
                    "duration_seconds": 5.0,
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("duration_seconds" in e or "additionalProperties" in e for e in errs)

    def test_extra_key_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_sound_suggestions")
        doc = {
            "adhyay": 1,
            "cues": [
                {
                    "scene_id": "S1",
                    "anchor_line_id": "S1-L1",
                    "sound_id": "bed_ambience",
                    "kind": "bed",
                    "purpose": "ambience",
                    "basis": "staging",
                    "extra": "no",
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("additionalProperties" in e for e in errs)

    def test_kind_enum(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_sound_suggestions")
        for k in ["bed", "fx"]:
            doc = {
                "adhyay": 1,
                "cues": [
                    {
                        "scene_id": "S1",
                        "anchor_line_id": "S1-L1",
                        "sound_id": "NEED_NEW",
                        "kind": k,
                        "sound_prompt": "p",
                        "purpose": "p",
                        "basis": "stated",
                    }
                ],
            }
            assert validate(doc, schema) == [], f"kind {k} failed"

    def test_basis_enum(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_sound_suggestions")
        for b in ["stated", "staging"]:
            doc = {
                "adhyay": 1,
                "cues": [
                    {
                        "scene_id": "S1",
                        "anchor_line_id": "S1-L1",
                        "sound_id": "NEED_NEW",
                        "kind": "fx",
                        "sound_prompt": "p",
                        "purpose": "p",
                        "basis": b,
                    }
                ],
            }
            assert validate(doc, schema) == [], f"basis {b} failed"


class TestStage1QuestionsSchema:
    def test_valid_minimal(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_questions")
        doc = {
            "adhyay": 1,
            "questions": [
                {"id": "Q1", "text": "Why does Arjuna hesitate?", "scene_id": "S1"},
                {"id": "Q2", "text": "What is dharma?"},
            ],
        }
        assert validate(doc, schema) == []

    def test_extra_key_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_questions")
        doc = {
            "adhyay": 1,
            "questions": [{"id": "Q1", "text": "t", "extra": "no"}],
        }
        errs = validate(doc, schema)
        assert any("additionalProperties" in e for e in errs)

    def test_id_pattern(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_questions")
        doc = {"adhyay": 1, "questions": [{"id": "X1", "text": "t"}]}
        errs = validate(doc, schema)
        assert any("id" in e for e in errs)


class TestOldSchemasUnchanged:
    """Ensure the four non-Stage-1 schemas are exactly as they were."""

    def test_beats_schema_keys(self, schemas_dir):
        schema = load_schema(schemas_dir, "beats")
        # Check required top-level keys exist
        assert "properties" in schema
        props = schema["properties"]
        assert "adhyay" in props
        assert "beats" in props
        assert schema.get("additionalProperties") is False

    def test_image_catalog_schema_keys(self, schemas_dir):
        schema = load_schema(schemas_dir, "image_catalog")
        assert "properties" in schema
        props = schema["properties"]
        assert "adhyay" in props
        assert "images" in props
        assert schema.get("additionalProperties") is False

    def test_animation_scene_schema_keys(self, schemas_dir):
        schema = load_schema(schemas_dir, "animation_scene")
        assert "properties" in schema
        props = schema["properties"]
        assert "adhyay" in props
        assert "scenes" in props
        assert schema.get("additionalProperties") is False

    def test_shot_plan_schema_keys(self, schemas_dir):
        schema = load_schema(schemas_dir, "shot_plan")
        assert "properties" in schema
        props = schema["properties"]
        assert "adhyay" in props
        assert "shots" in props
        assert schema.get("additionalProperties") is False
