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


# ======================================================================
# Expected frozen legacy schemas (copied from current repository state)
# ======================================================================
EXPECTED_BEATS_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["adhyay", "scenes"],
    "properties": {
        "adhyay": {"type": "integer", "minimum": 1, "maximum": 21},
        "scenes": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["scene_id", "beats"],
                "properties": {
                    "scene_id": {"type": "string", "pattern": "^S[0-9]{1,2}$"},
                    "beats": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["beat_id", "line_id", "description"],
                            "properties": {
                                "beat_id": {"type": "string", "pattern": "^B[0-9]{1,3}$"},
                                "line_id": {"type": "string", "pattern": "^S[0-9]{1,2}-L[0-9]{1,3}$"},
                                "description": {"type": "string", "minLength": 1, "maxLength": 400},
                            },
                        },
                    },
                },
            },
        },
    },
}

EXPECTED_IMAGE_CATALOG_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["adhyay", "images"],
    "properties": {
        "adhyay": {"type": "integer", "minimum": 1, "maximum": 21},
        "images": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["image_id", "scene_id", "shot_id", "prompt", "negative_prompt", "width", "height", "seed", "model", "approved"],
                "properties": {
                    "image_id": {"type": "string", "pattern": "^s[0-9]{1,2}_[a-z][a-z0-9_]{0,40}$"},
                    "scene_id": {"type": "string", "pattern": "^S[0-9]{1,2}$"},
                    "shot_id": {"type": "string", "pattern": "^S[0-9]{1,2}-[0-9]{1,2}$"},
                    "prompt": {"type": "string", "minLength": 1, "maxLength": 2000},
                    "negative_prompt": {"type": "string", "maxLength": 2000},
                    "width": {"type": "integer", "minimum": 64, "maximum": 2048},
                    "height": {"type": "integer", "minimum": 64, "maximum": 2048},
                    "seed": {"type": "integer", "minimum": 0, "maximum": 2147483647},
                    "model": {"type": "string", "minLength": 1},
                    "approved": {"type": "boolean"},
                },
            },
        },
    },
}

EXPECTED_ANIMATION_SCENE_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["adhyay", "scene_id", "shots"],
    "properties": {
        "adhyay": {"type": "integer", "minimum": 1, "maximum": 21},
        "scene_id": {"type": "string", "pattern": "^S[0-9]{1,2}$"},
        "shots": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["shot_id", "duration_frames", "camera", "lighting", "assets"],
                "properties": {
                    "shot_id": {"type": "string", "pattern": "^S[0-9]{1,2}-[0-9]{1,2}$"},
                    "duration_frames": {"type": "integer", "minimum": 1},
                    "camera": {"type": "string", "minLength": 1},
                    "lighting": {"type": "string", "minLength": 1},
                    "assets": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["asset_id", "transform"],
                            "properties": {
                                "asset_id": {"type": "string", "minLength": 1},
                                "transform": {"type": "object"},
                            },
                        },
                    },
                },
            },
        },
    },
}

EXPECTED_SHOT_PLAN_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["adhyay", "scene_id", "fingerprints", "shots", "approved_by", "approved_date"],
    "properties": {
        "adhyay": {"type": "integer", "minimum": 1, "maximum": 21},
        "scene_id": {"type": "string", "pattern": "^S[0-9]{1,2}$"},
        "fingerprints": {
            "type": "object",
            "additionalProperties": False,
            "required": ["story_map", "coverage", "scenes", "shots", "briefs", "looks", "voices", "sounds", "questions"],
            "properties": {
                "story_map": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
                "coverage": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
                "scenes": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
                "shots": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
                "briefs": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
                "looks": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
                "voices": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
                "sounds": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
                "questions": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
            },
        },
        "shots": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["shot_id", "image_id", "animation_shot_id"],
                "properties": {
                    "shot_id": {"type": "string", "pattern": "^S[0-9]{1,2}-[0-9]{1,2}$"},
                    "image_id": {"type": "string", "pattern": "^s[0-9]{1,2}_[a-z][a-z0-9_]{0,40}$"},
                    "animation_shot_id": {"type": "string", "pattern": "^S[0-9]{1,2}-[0-9]{1,2}$"},
                },
            },
        },
        "approved_by": {"type": "string", "minLength": 1},
        "approved_date": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"},
    },
}


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

    def test_valid_empty_events(self, schemas_dir):
        """Zero-story chapter: events array may be empty."""
        schema = load_schema(schemas_dir, "stage1_story_map")
        doc = {
            "adhyay": 1,
            "ovi_types": [{"ovi": 1, "type": "TEACHING"}],
            "events": [],
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

    def test_event_ovi_range_exactly_two_items(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_story_map")
        # too few
        doc = {
            "adhyay": 1,
            "ovi_types": [{"ovi": 1, "type": "STORY"}],
            "events": [{"event_id": "E1", "title": "t", "ovi_range": [1], "key_ovis": [1], "kind": "story", "closure": "NA"}],
        }
        errs = validate(doc, schema)
        assert errs
        # too many
        doc["events"][0]["ovi_range"] = [1, 2, 3]
        errs = validate(doc, schema)
        assert errs

    def test_nested_extra_keys_rejected_in_event(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_story_map")
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
                    "closure": "NA",
                    "extra_nested": "no",
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("additionalProperties" in e for e in errs)


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
        # missing covered_by -> error (with reason present)
        doc = {"adhyay": 1, "ovis": [{"ovi": 1, "disposition": "MERGED_EQUIVALENT", "reason": "same"}]}
        errs = validate(doc, schema)
        assert any("covered_by" in e.lower() for e in errs)
        # with covered_by -> ok
        doc = {
            "adhyay": 1,
            "ovis": [
                {
                    "ovi": 1,
                    "disposition": "MERGED_EQUIVALENT",
                    "reason": "same",
                    "covered_by": "S1-L5",
                }
            ],
        }
        assert validate(doc, schema) == []

    def test_merged_equivalent_requires_reason(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_coverage")
        # missing reason -> error (with covered_by present)
        doc = {"adhyay": 1, "ovis": [{"ovi": 1, "disposition": "MERGED_EQUIVALENT", "covered_by": "S1-L5"}]}
        errs = validate(doc, schema)
        assert any("reason" in e.lower() for e in errs)
        # with reason -> ok
        doc = {
            "adhyay": 1,
            "ovis": [
                {
                    "ovi": 1,
                    "disposition": "MERGED_EQUIVALENT",
                    "reason": "same",
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
        assert validate(doc, schema) == []

    def test_covered_by_accepts_ovi_or_line_id(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_coverage")
        for covered in ["S1-L5", 3]:
            doc = {
                "adhyay": 1,
                "ovis": [
                    {
                        "ovi": 1,
                        "disposition": "MERGED_EQUIVALENT",
                        "reason": "same",
                        "covered_by": covered,
                    }
                ],
            }
            assert validate(doc, schema) == [], f"covered_by {covered} failed"


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

    def test_story_scene_treatment_absent_accepted(self, schemas_dir):
        """Story scene may omit teaching_treatment entirely (defaults to none via schema)."""
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
                }
            ],
        }
        assert validate(doc, schema) == []

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

    def test_ovi_range_exactly_two_items(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_scenes")
        doc = {
            "adhyay": 1,
            "scenes": [
                {
                    "scene_id": "S1",
                    "section_kind": "story",
                    "ovi_range": [1],
                    "goal": "x",
                    "turn": {"ovi": 1, "text": "x"},
                    "line_ids": [],
                    "teaching_treatment": "none",
                }
            ],
        }
        errs = validate(doc, schema)
        assert errs


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

    def test_preset_pattern(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_shots")
        # valid preset pattern
        doc = {
            "adhyay": 1,
            "shots": [
                {
                    "shot_id": "S1-1",
                    "scene_id": "S1",
                    "ovi_ids": [1],
                    "beat_line_ids": ["S1-L1"],
                    "preset": "01_wide_shot",
                    "need_new": None,
                    "needs_cutout": False,
                    "pose": "x",
                    "framing": "x",
                }
            ],
        }
        assert validate(doc, schema) == []
        # invalid preset pattern (not NEED_NEW and not matching pattern)
        doc["shots"][0]["preset"] = "invalid_preset"
        errs = validate(doc, schema)
        assert errs


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

    def test_image_id_pattern(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_image_briefs")
        # valid
        doc = {
            "adhyay": 1,
            "images": [
                {
                    "image_id": "s1_valid_name",
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
                }
            ],
        }
        assert validate(doc, schema) == []
        # invalid - wrong prefix
        doc["images"][0]["image_id"] = "s9_wrong"
        errs = validate(doc, schema)
        assert errs
        # invalid - uppercase
        doc["images"][0]["image_id"] = "S1_wrong"
        errs = validate(doc, schema)
        assert errs


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
                    "events": ["E1"],
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

    def test_entity_state_unique_within_document(self, schemas_dir):
        """Schema enforces unique entity_id+state_id via uniqueItems on entries? Actually not at schema level - semantic check."""
        # Schema alone cannot enforce cross-entry uniqueness; this is a semantic rule.
        # But we test that extra keys are rejected.
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
                    "extra": "no",
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("additionalProperties" in e for e in errs)


class TestStage1VoiceCastSchema:
    def test_valid_minimal(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_voice_cast")
        doc = {
            "adhyay": 1,
            "cast": [
                {
                    "character_id": "arjuna",
                    "voice_key": "arjuna_voice",
                    "voice_id": "v_arjuna_001_valid_id",
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
                    "voice_id": "v_arjuna_001_valid_id",
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
                        "voice_id": "v_valid_voice_id_001",
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
                        "voice_id": "v_valid_voice_id_001",
                        "gender": "male",
                        "status": s,
                    }
                ],
            }
            assert validate(doc, schema) == [], f"status {s} failed"

    def test_voice_id_length(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_voice_cast")
        # too short (min 10)
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
        # too long (max 40)
        doc["cast"][0]["voice_id"] = "x" * 41
        errs = validate(doc, schema)
        assert any("voice_id" in e for e in errs)
        # valid boundaries
        doc["cast"][0]["voice_id"] = "x" * 10
        assert validate(doc, schema) == []
        doc["cast"][0]["voice_id"] = "x" * 40
        assert validate(doc, schema) == []


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

    def test_sound_id_pattern(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_sound_suggestions")
        # valid bed
        doc = {
            "adhyay": 1,
            "cues": [
                {
                    "scene_id": "S1",
                    "anchor_line_id": "S1-L1",
                    "sound_id": "bed_ambience",
                    "kind": "bed",
                    "purpose": "p",
                    "basis": "stated",
                }
            ],
        }
        assert validate(doc, schema) == []
        # valid fx
        doc["cues"][0]["sound_id"] = "fx_conch"
        doc["cues"][0]["kind"] = "fx"
        assert validate(doc, schema) == []
        # invalid prefix
        doc["cues"][0]["sound_id"] = "invalid_sound"
        errs = validate(doc, schema)
        assert errs


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


class TestCommonTypeBoundaries:
    """Parameterized tests for all common type boundaries across schemas."""

    @pytest.mark.parametrize("name,schema_name,instance,should_pass", [
        # scene_id
        ("scene_id_valid", "stage1_scenes", {"adhyay": 1, "scenes": [{"scene_id": "S1", "section_kind": "story", "ovi_range": [1,1], "goal": "g", "turn": {"ovi": 1, "text": "t"}, "line_ids": [], "teaching_treatment": "none"}]}, True),
        ("scene_id_invalid_S0", "stage1_scenes", {"adhyay": 1, "scenes": [{"scene_id": "S0", "section_kind": "story", "ovi_range": [1,1], "goal": "g", "turn": {"ovi": 1, "text": "t"}, "line_ids": [], "teaching_treatment": "none"}]}, False),
        ("scene_id_invalid_S100", "stage1_scenes", {"adhyay": 1, "scenes": [{"scene_id": "S100", "section_kind": "story", "ovi_range": [1,1], "goal": "g", "turn": {"ovi": 1, "text": "t"}, "line_ids": [], "teaching_treatment": "none"}]}, False),
        # shot_id
        ("shot_id_valid", "stage1_shots", {"adhyay": 1, "shots": [{"shot_id": "S1-1", "scene_id": "S1", "ovi_ids": [1], "beat_line_ids": ["S1-L1"], "preset": "01_wide", "need_new": None, "needs_cutout": False, "pose": "x", "framing": "x"}]}, True),
        ("shot_id_invalid", "stage1_shots", {"adhyay": 1, "shots": [{"shot_id": "S1_1", "scene_id": "S1", "ovi_ids": [1], "beat_line_ids": ["S1-L1"], "preset": "01_wide", "need_new": None, "needs_cutout": False, "pose": "x", "framing": "x"}]}, False),
        # line_id
        ("line_id_valid", "stage1_scenes", {"adhyay": 1, "scenes": [{"scene_id": "S1", "section_kind": "story", "ovi_range": [1,1], "goal": "g", "turn": {"ovi": 1, "text": "t"}, "line_ids": ["S1-L1"], "teaching_treatment": "none"}]}, True),
        ("line_id_invalid", "stage1_scenes", {"adhyay": 1, "scenes": [{"scene_id": "S1", "section_kind": "story", "ovi_range": [1,1], "goal": "g", "turn": {"ovi": 1, "text": "t"}, "line_ids": ["S1-L"], "teaching_treatment": "none"}]}, False),
        # image_id
        ("image_id_valid", "stage1_image_briefs", {"adhyay": 1, "images": [{"image_id": "s1_valid_name", "scene_id": "S1", "shot_ids": ["S1-1"], "people": [{"name": "A", "position": "c", "pose": "p", "gaze": "g"}], "place_id": "p", "prop": None, "prop_state": None, "camera": "c", "light": "l", "reason_new": "r", "on_screen_facts": ["f"], "references": {"characters": [], "place": "p", "style_anchor": "s", "prop": None}}]}, True),
        ("image_id_invalid_prefix", "stage1_image_briefs", {"adhyay": 1, "images": [{"image_id": "s9_wrong", "scene_id": "S1", "shot_ids": ["S1-1"], "people": [{"name": "A", "position": "c", "pose": "p", "gaze": "g"}], "place_id": "p", "prop": None, "prop_state": None, "camera": "c", "light": "l", "reason_new": "r", "on_screen_facts": ["f"], "references": {"characters": [], "place": "p", "style_anchor": "s", "prop": None}}]}, False),
        # ovi minimum
        ("ovi_min_1", "stage1_story_map", {"adhyay": 1, "ovi_types": [{"ovi": 1, "type": "STORY"}], "events": []}, True),
        ("ovi_min_0_invalid", "stage1_story_map", {"adhyay": 1, "ovi_types": [{"ovi": 0, "type": "STORY"}], "events": []}, False),
        # adhyay bounds
        ("adhyay_1", "stage1_story_map", {"adhyay": 1, "ovi_types": [{"ovi": 1, "type": "STORY"}], "events": []}, True),
        ("adhyay_21", "stage1_story_map", {"adhyay": 21, "ovi_types": [{"ovi": 1, "type": "STORY"}], "events": []}, True),
        ("adhyay_0_invalid", "stage1_story_map", {"adhyay": 0, "ovi_types": [{"ovi": 1, "type": "STORY"}], "events": []}, False),
        ("adhyay_22_invalid", "stage1_story_map", {"adhyay": 22, "ovi_types": [{"ovi": 1, "type": "STORY"}], "events": []}, False),
        # text length 1..400
        ("text_min_1", "stage1_story_map", {"adhyay": 1, "ovi_types": [{"ovi": 1, "type": "STORY"}], "events": [{"event_id": "E1", "title": "x", "ovi_range": [1,1], "key_ovis": [1], "kind": "story", "closure": "NA"}]}, True),
        ("text_max_400", "stage1_story_map", {"adhyay": 1, "ovi_types": [{"ovi": 1, "type": "STORY"}], "events": [{"event_id": "E1", "title": "x"*400, "ovi_range": [1,1], "key_ovis": [1], "kind": "story", "closure": "NA"}]}, True),
        ("text_0_invalid", "stage1_story_map", {"adhyay": 1, "ovi_types": [{"ovi": 1, "type": "STORY"}], "events": [{"event_id": "E1", "title": "", "ovi_range": [1,1], "key_ovis": [1], "kind": "story", "closure": "NA"}]}, False),
        ("text_401_invalid", "stage1_story_map", {"adhyay": 1, "ovi_types": [{"ovi": 1, "type": "STORY"}], "events": [{"event_id": "E1", "title": "x"*401, "ovi_range": [1,1], "key_ovis": [1], "kind": "story", "closure": "NA"}]}, False),
        # preset_id pattern
        ("preset_id_valid", "stage1_shots", {"adhyay": 1, "shots": [{"shot_id": "S1-1", "scene_id": "S1", "ovi_ids": [1], "beat_line_ids": ["S1-L1"], "preset": "01_wide_shot", "need_new": None, "needs_cutout": False, "pose": "x", "framing": "x"}]}, True),
        ("preset_id_invalid", "stage1_shots", {"adhyay": 1, "shots": [{"shot_id": "S1-1", "scene_id": "S1", "ovi_ids": [1], "beat_line_ids": ["S1-L1"], "preset": "wide_shot", "need_new": None, "needs_cutout": False, "pose": "x", "framing": "x"}]}, False),
        # sound_id pattern
        ("sound_id_bed_valid", "stage1_sound_suggestions", {"adhyay": 1, "cues": [{"scene_id": "S1", "anchor_line_id": "S1-L1", "sound_id": "bed_ambience", "kind": "bed", "purpose": "p", "basis": "stated"}]}, True),
        ("sound_id_fx_valid", "stage1_sound_suggestions", {"adhyay": 1, "cues": [{"scene_id": "S1", "anchor_line_id": "S1-L1", "sound_id": "fx_conch", "kind": "fx", "purpose": "p", "basis": "stated"}]}, True),
        ("sound_id_need_new_valid", "stage1_sound_suggestions", {"adhyay": 1, "cues": [{"scene_id": "S1", "anchor_line_id": "S1-L1", "sound_id": "NEED_NEW", "kind": "fx", "sound_prompt": "p", "purpose": "p", "basis": "stated"}]}, True),
        ("sound_id_invalid", "stage1_sound_suggestions", {"adhyay": 1, "cues": [{"scene_id": "S1", "anchor_line_id": "S1-L1", "sound_id": "invalid", "kind": "bed", "purpose": "p", "basis": "stated"}]}, False),
        # voice_id length 10..40
        ("voice_id_min_10", "stage1_voice_cast", {"adhyay": 1, "cast": [{"character_id": "c", "voice_key": "k", "voice_id": "x"*10, "gender": "male", "status": "RECURRING"}]}, True),
        ("voice_id_max_40", "stage1_voice_cast", {"adhyay": 1, "cast": [{"character_id": "c", "voice_key": "k", "voice_id": "x"*40, "gender": "male", "status": "RECURRING"}]}, True),
        ("voice_id_9_invalid", "stage1_voice_cast", {"adhyay": 1, "cast": [{"character_id": "c", "voice_key": "k", "voice_id": "x"*9, "gender": "male", "status": "RECURRING"}]}, False),
        ("voice_id_41_invalid", "stage1_voice_cast", {"adhyay": 1, "cast": [{"character_id": "c", "voice_key": "k", "voice_id": "x"*41, "gender": "male", "status": "RECURRING"}]}, False),
        # question_id pattern
        ("question_id_valid", "stage1_questions", {"adhyay": 1, "questions": [{"id": "Q1", "text": "t"}]}, True),
        ("question_id_invalid", "stage1_questions", {"adhyay": 1, "questions": [{"id": "X1", "text": "t"}]}, False),
    ])
    def test_common_type_boundaries(self, schemas_dir, name, schema_name, instance, should_pass):
        schema = load_schema(schemas_dir, schema_name)
        errs = validate(instance, schema)
        if should_pass:
            assert errs == [], f"{name}: expected pass, got errors: {errs}"
        else:
            assert errs, f"{name}: expected failure, got none"


class TestRequiredFields:
    """Each required field missing should cause a schema error."""

    @pytest.mark.parametrize("schema_name,doc_base,missing_field", [
        ("stage1_story_map", {"adhyay": 1, "ovi_types": [], "events": []}, "ovi_types"),
        ("stage1_story_map", {"adhyay": 1, "ovi_types": [{"ovi": 1, "type": "STORY"}], "events": []}, "events"),
        ("stage1_coverage", {"adhyay": 1, "ovis": []}, "ovis"),
        ("stage1_scenes", {"adhyay": 1, "scenes": []}, "scenes"),
        ("stage1_shots", {"adhyay": 1, "shots": []}, "shots"),
        ("stage1_image_briefs", {"adhyay": 1, "images": []}, "images"),
        ("stage1_canon_looks", {"adhyay": 1, "entries": []}, "entries"),
        ("stage1_voice_cast", {"adhyay": 1, "cast": []}, "cast"),
        ("stage1_sound_suggestions", {"adhyay": 1, "cues": []}, "cues"),
        ("stage1_questions", {"adhyay": 1, "questions": []}, "questions"),
    ])
    def test_required_fields(self, schemas_dir, schema_name, doc_base, missing_field):
        schema = load_schema(schemas_dir, schema_name)
        errs = validate(doc_base, schema)
        assert any(missing_field in e and ("required" in e or "missing" in e) for e in errs), f"{schema_name}.{missing_field}"


class TestOldSchemasUnchanged:
    """Ensure the four non-Stage-1 schemas are exactly as they were (frozen copies)."""

    def test_beats_schema_exact(self, schemas_dir):
        schema = load_schema(schemas_dir, "beats")
        assert schema == EXPECTED_BEATS_SCHEMA

    def test_image_catalog_schema_exact(self, schemas_dir):
        schema = load_schema(schemas_dir, "image_catalog")
        assert schema == EXPECTED_IMAGE_CATALOG_SCHEMA

    def test_animation_scene_schema_exact(self, schemas_dir):
        schema = load_schema(schemas_dir, "animation_scene")
        assert schema == EXPECTED_ANIMATION_SCENE_SCHEMA

    def test_shot_plan_schema_exact(self, schemas_dir):
        schema = load_schema(schemas_dir, "shot_plan")
        assert schema == EXPECTED_SHOT_PLAN_SCHEMA


class TestMakeSchemasCLI:
    def test_write_all_returns_paths(self, tmp_path):
        written = make_schemas.write_all(tmp_path, overwrite=False)
        assert len(written) == 13  # 9 stage1 + 4 legacy
        for p in written:
            assert p.exists()
            assert p.suffix == ".json"

    def test_refuses_overwrite(self, tmp_path):
        make_schemas.write_all(tmp_path, overwrite=False)
        with pytest.raises(FileExistsError):
            make_schemas.write_all(tmp_path, overwrite=False)

    def test_overwrite_replaces(self, tmp_path):
        make_schemas.write_all(tmp_path, overwrite=False)
        # Should not raise with overwrite=True
        written = make_schemas.write_all(tmp_path, overwrite=True)
        assert len(written) == 13

    def test_generated_schema_dialect(self, tmp_path):
        make_schemas.write_all(tmp_path, overwrite=False)
        for p in tmp_path.glob("*.schema.json"):
            data = json.loads(p.read_text())
            assert data.get("$schema") == "https://json-schema.org/draft/2020-12/schema"

    def test_main_cli(self, tmp_path, monkeypatch, capsys):
        # Test CLI --out and --overwrite
        monkeypatch.setattr(sys, "argv", ["make_schemas.py", "--out", str(tmp_path), "--overwrite"])
        make_schemas.main()
        assert len(list(tmp_path.glob("*.schema.json"))) == 13
