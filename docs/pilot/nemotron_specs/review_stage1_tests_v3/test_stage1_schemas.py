from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location(
    "make_schemas", ROOT / "scripts" / "pipeline" / "make_schemas.py"
)
make_schemas = importlib.util.module_from_spec(spec)
sys.modules["make_schemas"] = make_schemas
spec.loader.exec_module(make_schemas)


@pytest.fixture(scope="session")
def schemas_dir(tmp_path_factory):
    out_dir = tmp_path_factory.mktemp("schemas")
    written = make_schemas.write_all(out_dir, overwrite=False)
    assert len(written) == 13
    return out_dir


def load_schema(schemas_dir: Path, name: str) -> dict:
    path = schemas_dir / f"{name}.schema.json"
    assert path.exists(), f"schema {name} not found at {path}"
    return json.loads(path.read_text())


def validate(instance: dict, schema: dict) -> list[str]:
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)
    return [f"{'.'.join(str(p) for p in e.path) or 'root'}: {e.message}" for e in errors]


# ======================================================================
# ACTUAL frozen legacy schemas (byte-for-byte from repository)
# ======================================================================
EXPECTED_BEATS_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "beats",
    "type": "object",
    "additionalProperties": False,
    "required": ["adhyay", "scenes"],
    "properties": {
        "adhyay": {"type": "integer", "minimum": 1, "maximum": 21},
        "scenes": {
            "type": "array",
            "minItems": 0,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["scene_id", "beats"],
                "properties": {
                    "scene_id": {"type": "string", "pattern": "^S[0-9]{1,2}$"},
                    "beats": {
                        "type": "array",
                        "minItems": 0,
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["line_id", "voice", "mr_s", "hi_s", "start_s", "end_s", "shot"],
                            "properties": {
                                "line_id": {"type": "string", "pattern": "^S[0-9]{1,2}-L[0-9]{1,3}$"},
                                "voice": {"type": "string", "minLength": 1, "maxLength": 400},
                                "mr_s": {"type": "number", "exclusiveMinimum": 0},
                                "hi_s": {"type": "number", "exclusiveMinimum": 0},
                                "start_s": {"type": "number", "minimum": 0},
                                "end_s": {"type": "number", "exclusiveMinimum": 0},
                                "shot": {"type": "integer", "minimum": 1},
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
    "title": "image_catalog",
    "type": "object",
    "additionalProperties": False,
    "required": ["adhyay", "images"],
    "properties": {
        "adhyay": {"type": "integer", "minimum": 1, "maximum": 21},
        "images": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "additionalProperties": False,
                "required": ["file", "sha256", "chosen_version", "prompt_sha256", "model", "edit_id", "approved"],
                "properties": {
                    "file": {"type": "string", "minLength": 1, "maxLength": 400},
                    "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                    "chosen_version": {"type": "integer", "minimum": 1},
                    "prompt_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                    "model": {"type": "string", "minLength": 1, "maxLength": 400},
                    "edit_id": {"type": ["string", "null"]},
                    "approved": {"type": "boolean"},
                },
            },
        },
    },
}

EXPECTED_ANIMATION_SCENE_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "animation_scene",
    "type": "object",
    "additionalProperties": False,
    "required": ["adhyay", "scene_id", "shots"],
    "properties": {
        "adhyay": {"type": "integer", "minimum": 1, "maximum": 21},
        "scene_id": {"type": "string", "pattern": "^S[0-9]{1,2}$"},
        "shots": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["shot_id", "preset", "assets", "held_pose", "transition_out", "need_new"],
                "properties": {
                    "shot_id": {"type": "string", "pattern": "^S[0-9]{1,2}-[0-9]{1,2}$"},
                    "preset": {"type": "string", "minLength": 1},
                    "assets": {
                        "type": "object",
                        "additionalProperties": {"type": "string", "pattern": "^SH_S[0-9]{1,2}_[0-9]{2}$"},
                    },
                    "held_pose": {"type": "string", "minLength": 1, "maxLength": 400},
                    "transition_out": {"enum": ["cut", "slide", "pan_bridge"]},
                    "need_new": {
                        "anyOf": [
                            {"type": "null"},
                            {
                                "type": "object",
                                "additionalProperties": False,
                                "required": ["reason", "class"],
                                "properties": {
                                    "reason": {"type": "string", "minLength": 1, "maxLength": 400},
                                    "class": {"enum": ["missing_image", "json_arrangement", "renderer_gap"]},
                                },
                            },
                        ],
                    },
                },
            },
        },
    },
}

EXPECTED_SHOT_PLAN_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "shot_plan",
    "type": "object",
    "additionalProperties": False,
    "required": ["adhyay", "scene_id", "fingerprints", "shots", "approved_by", "approved_date"],
    "properties": {
        "adhyay": {"type": "integer", "minimum": 1, "maximum": 21},
        "scene_id": {"type": "string", "pattern": "^S[0-9]{1,2}$"},
        "fingerprints": {
            "type": "object",
            "additionalProperties": False,
            "required": ["script", "timing", "presets", "images"],
            "properties": {
                "script": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "timing": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "presets": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "images": {"type": "object", "additionalProperties": {"type": "string", "pattern": "^[0-9a-f]{64}$"}},
            },
        },
        "shots": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["shot_id", "preset", "assets", "held_pose", "transition_out", "need_new"],
                "properties": {
                    "shot_id": {"type": "string", "pattern": "^S[0-9]{1,2}-[0-9]{1,2}$"},
                    "preset": {"type": "string", "minLength": 1},
                    "assets": {"type": "object", "additionalProperties": {"type": "string", "pattern": "^SH_S[0-9]{1,2}_[0-9]{2}$"}},
                    "held_pose": {"type": "string", "minLength": 1, "maxLength": 400},
                    "transition_out": {"enum": ["cut", "slide", "pan_bridge"]},
                    "need_new": {
                        "anyOf": [
                            {"type": "null"},
                            {
                                "type": "object",
                                "additionalProperties": False,
                                "required": ["reason", "class"],
                                "properties": {
                                    "reason": {"type": "string", "minLength": 1, "maxLength": 400},
                                    "class": {"enum": ["missing_image", "json_arrangement", "renderer_gap"]},
                                },
                            },
                        ],
                    },
                },
            },
        },
        "approved_by": {"type": "string", "minLength": 1, "maxLength": 400},
        "approved_date": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"},
    },
}


# ======================================================================
# Baseline valid document builders (note-free, new states)
# ======================================================================
def base_story_map(adhyay=1):
    return {
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
    }


def base_coverage(adhyay=1):
    return {
        "adhyay": adhyay,
        "ovis": [
            {"ovi": 1, "disposition": "VISUALISED"},
            {"ovi": 2, "disposition": "NARRATED"},
            {"ovi": 3, "disposition": "QUOTED"},
            {"ovi": 4, "disposition": "MERGED_EQUIVALENT", "reason": "same as 3", "covered_by": 3},
            {"ovi": 5, "disposition": "QUOTED"},
        ],
    }


def base_scenes(adhyay=1):
    return {
        "adhyay": adhyay,
        "scenes": [
            {"scene_id": "S1", "section_kind": "story", "ovi_range": [1, 2], "goal": "Setup", "turn": {"ovi": 1, "text": "Arjuna sees armies"}, "line_ids": ["S1-L1", "S1-L2"], "teaching_treatment": "none"},
            {"scene_id": "S2", "section_kind": "discourse", "ovi_range": [3, 5], "goal": "Teaching", "turn": {"ovi": 3, "text": "Krishna speaks"}, "line_ids": ["S2-L1"], "teaching_treatment": "contemplative_hold"},
        ],
    }


def base_shots(adhyay=1):
    return {
        "adhyay": adhyay,
        "shots": [
            {"shot_id": "S1-1", "scene_id": "S1", "ovi_ids": [1], "beat_line_ids": ["S1-L1"], "preset": "01_wide", "need_new": None, "needs_cutout": False, "pose": "standing", "framing": "wide"},
            {"shot_id": "S1-2", "scene_id": "S1", "ovi_ids": [2], "beat_line_ids": ["S1-L2"], "preset": "02_medium", "need_new": None, "needs_cutout": False, "pose": "kneeling", "framing": "medium"},
            {"shot_id": "S2-1", "scene_id": "S2", "ovi_ids": [3, 4, 5], "beat_line_ids": ["S2-L1"], "preset": "03_close", "need_new": None, "needs_cutout": True, "pose": "seated", "framing": "close"},
        ],
    }


def base_briefs(adhyay=1):
    return {
        "adhyay": adhyay,
        "images": [
            {"image_id": "s1_arjuna_standing", "scene_id": "S1", "shot_ids": ["S1-1"], "people": [{"name": "Arjuna", "position": "center", "pose": "standing", "gaze": "forward"}], "place_id": "battlefield", "prop": "bow", "prop_state": "strung", "camera": "eye level", "light": "harsh noon", "reason_new": "first shot", "on_screen_facts": ["Arjuna stands", "bow visible"], "references": {"characters": ["Arjuna"], "place": "battlefield", "style_anchor": "epic realism", "prop": "bow"}},
            {"image_id": "s2_krishna_seated", "scene_id": "S2", "shot_ids": ["S2-1"], "people": [{"name": "Krishna", "position": "center", "pose": "seated", "gaze": "at Arjuna"}], "place_id": "chariot", "prop": None, "prop_state": None, "camera": "low angle", "light": "divine glow", "reason_new": "teaching moment", "on_screen_facts": ["Krishna seated", "chariot interior"], "references": {"characters": ["Krishna"], "place": "chariot", "style_anchor": "epic realism", "prop": None}},
        ],
    }


def base_looks(adhyay=1):
    return {
        "adhyay": adhyay,
        "entries": [
            {"entity_id": "arjuna", "kind": "character", "state_id": "battle_ready_new", "look": "armored, bow in hand", "source_ovis": [1, 2], "basis": "stated"},
            {"entity_id": "krishna", "kind": "character", "state_id": "charioteer_new", "look": "peacock feather, yellow garment", "source_ovis": [3, 4, 5], "basis": "stated"},
            {"entity_id": "battlefield", "kind": "place", "state_id": "dawn_armies_new", "look": "two armies arrayed", "source_ovis": [1], "basis": "stated"},
        ],
    }


def base_voices(adhyay=1):
    return {
        "adhyay": adhyay,
        "cast": [
            {"character_id": "arjuna", "voice_key": "arjuna_voice", "voice_id": "v_arjuna_001_valid_id", "gender": "male", "status": "RECURRING"},
            {"character_id": "krishna", "voice_key": "krishna_voice", "voice_id": "v_krishna_001_valid_id", "gender": "male", "status": "RECURRING"},
        ],
    }


def base_sounds(adhyay=1):
    return {
        "adhyay": adhyay,
        "cues": [
            {"scene_id": "S1", "anchor_line_id": "S1-L1", "sound_id": "bed_battlefield", "kind": "bed", "purpose": "ambience", "basis": "staging"},
            {"scene_id": "S2", "anchor_line_id": "S2-L1", "sound_id": "fx_conch", "kind": "fx", "purpose": "signal start", "basis": "stated"},
        ],
    }


def base_questions(adhyay=1):
    return {
        "adhyay": adhyay,
        "questions": [{"id": "Q1", "text": "Why does Arjuna hesitate?", "scene_id": "S1"}, {"id": "Q2", "text": "What is the nature of the self?"}],
    }


BASE_BUILDERS = {
    "stage1_story_map": base_story_map,
    "stage1_coverage": base_coverage,
    "stage1_scenes": base_scenes,
    "stage1_shots": base_shots,
    "stage1_image_briefs": base_briefs,
    "stage1_canon_looks": base_looks,
    "stage1_voice_cast": base_voices,
    "stage1_sound_suggestions": base_sounds,
    "stage1_questions": base_questions,
}


# ======================================================================
# Mutation helpers (deep copy + single change)
# ======================================================================
def mutate(doc: dict, path: list, value):
    """Deep copy doc and set value at path (list of keys/indices)."""
    d = copy.deepcopy(doc)
    cur = d
    for p in path[:-1]:
        cur = cur[p]
    cur[path[-1]] = value
    return d


def delete_field(doc: dict, path: list):
    """Deep copy doc and delete field at path."""
    d = copy.deepcopy(doc)
    cur = d
    for p in path[:-1]:
        cur = cur[p]
    del cur[path[-1]]
    return d


# ======================================================================
# Schema tests: positive + negative (table-driven)
# ======================================================================
class TestStage1SchemasPositive:
    @pytest.mark.parametrize("name", list(BASE_BUILDERS.keys()))
    def test_valid_baseline(self, schemas_dir, name):
        schema = load_schema(schemas_dir, name)
        doc = BASE_BUILDERS[name](1)
        assert validate(doc, schema) == [], f"{name} baseline failed: {validate(doc, schema)}"


class TestStage1SchemasNegative:
    # Each row: (schema_name, mutation_fn, expected_field_in_error)
    # mutation_fn takes a valid doc and returns a mutated doc with ONE error
    @pytest.mark.parametrize("schema_name,mutate_fn,expected_field", [
        # story_map
        ("stage1_story_map", lambda d: mutate(d, ["ovi_types", 0, "type"], "INVALID"), "type"),
        ("stage1_story_map", lambda d: mutate(d, ["events", 0, "event_id"], "X1"), "event_id"),
        ("stage1_story_map", lambda d: mutate(d, ["events", 0, "ovi_range"], [5, 1]), "ovi_range"),
        ("stage1_story_map", lambda d: mutate(d, ["events", 0, "key_ovis"], [99]), "key_ovis"),
        ("stage1_story_map", lambda d: mutate(d, ["events", 0, "closure"], "INVALID"), "closure"),
        ("stage1_story_map", lambda d: mutate(d, ["events", 0, "kind"], "invalid"), "kind"),
        ("stage1_story_map", lambda d: mutate(d, ["events", 0, "extra_nested"], "x"), "extra_nested"),
        ("stage1_story_map", lambda d: mutate(d, ["extra_top"], "x"), "extra_top"),
        # coverage
        ("stage1_coverage", lambda d: mutate(d, ["ovis", 0, "disposition"], "INVALID"), "disposition"),
        ("stage1_coverage", lambda d: mutate(d, ["ovis", 0, "disposition"], "PROPOSE_OMISSION"), "reason"),  # missing reason
        ("stage1_coverage", lambda d: mutate(d, ["ovis", 0, "disposition"], "MERGED_EQUIVALENT"), "covered_by"),  # missing covered_by
        ("stage1_coverage", lambda d: mutate(d, ["ovis", 0, "extra"], "x"), "extra"),
        # scenes
        ("stage1_scenes", lambda d: mutate(d, ["scenes", 0, "section_kind"], "invalid"), "section_kind"),
        ("stage1_scenes", lambda d: mutate(d, ["scenes", 1, "teaching_treatment"], "none"), "teaching_treatment"),  # discourse with none
        ("stage1_scenes", lambda d: mutate(d, ["scenes", 0, "teaching_treatment"], "narration_over_typography"), "teaching_treatment"),  # story with treatment
        ("stage1_scenes", lambda d: mutate(d, ["scenes", 0, "ovi_range"], [3, 1]), "ovi_range"),
        ("stage1_scenes", lambda d: mutate(d, ["scenes", 0, "extra"], "x"), "extra"),
        # shots
        ("stage1_shots", lambda d: mutate(d, ["shots", 0, "preset"], "NEED_NEW"), "need_new"),  # NEED_NEW with null need_new
        ("stage1_shots", lambda d: mutate(d, ["shots", 0, "preset"], "01_wide", ["shots", 0, "need_new"], {"reason": "x", "class": "missing_image"}), "need_new"),  # non-NEED_NEW with need_new object
        ("stage1_shots", lambda d: mutate(d, ["shots", 0, "preset_hint"], "old"), "preset_hint"),
        ("stage1_shots", lambda d: mutate(d, ["shots", 0, "extra"], "x"), "extra"),
        ("stage1_shots", lambda d: mutate(d, ["shots", 0, "need_new", "class"], "invalid"), "class"),
        # briefs
        ("stage1_image_briefs", lambda d: mutate(d, ["images", 0, "on_screen_facts"], []), "on_screen_facts"),
        ("stage1_image_briefs", lambda d: mutate(d, ["images", 0, "people", 0, "name"], ""), "name"),
        ("stage1_image_briefs", lambda d: mutate(d, ["images", 0, "extra"], "x"), "extra"),
        # looks
        ("stage1_canon_looks", lambda d: mutate(d, ["entries", 0, "kind"], "invalid"), "kind"),
        ("stage1_canon_looks", lambda d: mutate(d, ["entries", 0, "basis"], "invalid"), "basis"),
        ("stage1_canon_looks", lambda d: mutate(d, ["entries", 0, "source_ovis"], []), "source_ovis"),
        ("stage1_canon_looks", lambda d: mutate(d, ["entries", 0, "events"], ["E1"]), "events"),
        ("stage1_canon_looks", lambda d: mutate(d, ["entries", 0, "extra"], "x"), "extra"),
        # voices
        ("stage1_voice_cast", lambda d: mutate(d, ["cast", 0, "gender"], "invalid"), "gender"),
        ("stage1_voice_cast", lambda d: mutate(d, ["cast", 0, "status"], "INVALID"), "status"),
        ("stage1_voice_cast", lambda d: mutate(d, ["cast", 0, "voice_id"], "short"), "voice_id"),
        ("stage1_voice_cast", lambda d: mutate(d, ["cast", 0, "voice_id"], "x" * 41), "voice_id"),
        ("stage1_voice_cast", lambda d: mutate(d, ["cast", 0, "extra"], "x"), "extra"),
        # sounds
        ("stage1_sound_suggestions", lambda d: mutate(d, ["cues", 0, "kind"], "invalid"), "kind"),
        ("stage1_sound_suggestions", lambda d: mutate(d, ["cues", 0, "basis"], "invalid"), "basis"),
        ("stage1_sound_suggestions", lambda d: mutate(d, ["cues", 0, "sound_id"], "NEED_NEW", ["cues", 0, "sound_prompt"], None), "sound_prompt"),  # NEED_NEW missing sound_prompt
        ("stage1_sound_suggestions", lambda d: mutate(d, ["cues", 0, "sound_id"], "bed_ambience", ["cues", 0, "sound_prompt"], "x"), "sound_prompt"),  # non-NEED_NEW with sound_prompt
        ("stage1_sound_suggestions", lambda d: mutate(d, ["cues", 0, "duration_seconds"], 5.0), "duration_seconds"),
        ("stage1_sound_suggestions", lambda d: mutate(d, ["cues", 0, "extra"], "x"), "extra"),
        ("stage1_sound_suggestions", lambda d: mutate(d, ["cues", 0, "sound_id"], "invalid"), "sound_id"),
        # questions
        ("stage1_questions", lambda d: mutate(d, ["questions", 0, "id"], "X1"), "id"),
        ("stage1_questions", lambda d: mutate(d, ["questions", 0, "extra"], "x"), "extra"),
    ])
    def test_single_mutation_rejected(self, schemas_dir, schema_name, mutate_fn, expected_field):
        schema = load_schema(schemas_dir, schema_name)
        base = BASE_BUILDERS[schema_name](1)
        doc = mutate_fn(base)
        errs = validate(doc, schema)
        assert errs, f"{schema_name}: expected rejection for {expected_field}"
        # Check that the offending field appears in some error message
        assert any(expected_field in e for e in errs), f"{schema_name}: field {expected_field} not in errors: {errs}"


class TestStage1SchemasRequiredFields:
    """Each required field missing should cause a schema error (field deleted from deep copy)."""
    @pytest.mark.parametrize("schema_name,doc_base,missing_path", [
        ("stage1_story_map", base_story_map(1), ["ovi_types"]),
        ("stage1_story_map", base_story_map(1), ["events"]),
        ("stage1_coverage", base_coverage(1), ["ovis"]),
        ("stage1_scenes", base_scenes(1), ["scenes"]),
        ("stage1_shots", base_shots(1), ["shots"]),
        ("stage1_image_briefs", base_briefs(1), ["images"]),
        ("stage1_canon_looks", base_looks(1), ["entries"]),
        ("stage1_voice_cast", base_voices(1), ["cast"]),
        ("stage1_sound_suggestions", base_sounds(1), ["cues"]),
        ("stage1_questions", base_questions(1), ["questions"]),
        # nested required fields
        ("stage1_story_map", base_story_map(1), ["ovi_types", 0, "ovi"]),
        ("stage1_story_map", base_story_map(1), ["ovi_types", 0, "type"]),
        ("stage1_story_map", base_story_map(1), ["events", 0, "event_id"]),
        ("stage1_story_map", base_story_map(1), ["events", 0, "title"]),
        ("stage1_story_map", base_story_map(1), ["events", 0, "ovi_range"]),
        ("stage1_story_map", base_story_map(1), ["events", 0, "key_ovis"]),
        ("stage1_story_map", base_story_map(1), ["events", 0, "kind"]),
        ("stage1_story_map", base_story_map(1), ["events", 0, "closure"]),
        ("stage1_coverage", base_coverage(1), ["ovis", 0, "ovi"]),
        ("stage1_coverage", base_coverage(1), ["ovis", 0, "disposition"]),
        ("stage1_scenes", base_scenes(1), ["scenes", 0, "scene_id"]),
        ("stage1_scenes", base_scenes(1), ["scenes", 0, "section_kind"]),
        ("stage1_scenes", base_scenes(1), ["scenes", 0, "ovi_range"]),
        ("stage1_scenes", base_scenes(1), ["scenes", 0, "goal"]),
        ("stage1_scenes", base_scenes(1), ["scenes", 0, "turn"]),
        ("stage1_scenes", base_scenes(1), ["scenes", 0, "turn", "ovi"]),
        ("stage1_scenes", base_scenes(1), ["scenes", 0, "turn", "text"]),
        ("stage1_scenes", base_scenes(1), ["scenes", 0, "line_ids"]),
        ("stage1_shots", base_shots(1), ["shots", 0, "shot_id"]),
        ("stage1_shots", base_shots(1), ["shots", 0, "scene_id"]),
        ("stage1_shots", base_shots(1), ["shots", 0, "ovi_ids"]),
        ("stage1_shots", base_shots(1), ["shots", 0, "beat_line_ids"]),
        ("stage1_shots", base_shots(1), ["shots", 0, "preset"]),
        ("stage1_shots", base_shots(1), ["shots", 0, "need_new"]),
        ("stage1_shots", base_shots(1), ["shots", 0, "needs_cutout"]),
        ("stage1_shots", base_shots(1), ["shots", 0, "pose"]),
        ("stage1_shots", base_shots(1), ["shots", 0, "framing"]),
        ("stage1_image_briefs", base_briefs(1), ["images", 0, "image_id"]),
        ("stage1_image_briefs", base_briefs(1), ["images", 0, "scene_id"]),
        ("stage1_image_briefs", base_briefs(1), ["images", 0, "shot_ids"]),
        ("stage1_image_briefs", base_briefs(1), ["images", 0, "people"]),
        ("stage1_image_briefs", base_briefs(1), ["images", 0, "people", 0, "name"]),
        ("stage1_image_briefs", base_briefs(1), ["images", 0, "people", 0, "position"]),
        ("stage1_image_briefs", base_briefs(1), ["images", 0, "people", 0, "pose"]),
        ("stage1_image_briefs", base_briefs(1), ["images", 0, "people", 0, "gaze"]),
        ("stage1_image_briefs", base_briefs(1), ["images", 0, "place_id"]),
        ("stage1_image_briefs", base_briefs(1), ["images", 0, "prop"]),
        ("stage1_image_briefs", base_briefs(1), ["images", 0, "prop_state"]),
        ("stage1_image_briefs", base_briefs(1), ["images", 0, "camera"]),
        ("stage1_image_briefs", base_briefs(1), ["images", 0, "light"]),
        ("stage1_image_briefs", base_briefs(1), ["images", 0, "reason_new"]),
        ("stage1_image_briefs", base_briefs(1), ["images", 0, "on_screen_facts"]),
        ("stage1_image_briefs", base_briefs(1), ["images", 0, "references"]),
        ("stage1_image_briefs", base_briefs(1), ["images", 0, "references", "characters"]),
        ("stage1_image_briefs", base_briefs(1), ["images", 0, "references", "place"]),
        ("stage1_image_briefs", base_briefs(1), ["images", 0, "references", "style_anchor"]),
        ("stage1_image_briefs", base_briefs(1), ["images", 0, "references", "prop"]),
        ("stage1_canon_looks", base_looks(1), ["entries", 0, "entity_id"]),
        ("stage1_canon_looks", base_looks(1), ["entries", 0, "kind"]),
        ("stage1_canon_looks", base_looks(1), ["entries", 0, "state_id"]),
        ("stage1_canon_looks", base_looks(1), ["entries", 0, "look"]),
        ("stage1_canon_looks", base_looks(1), ["entries", 0, "source_ovis"]),
        ("stage1_canon_looks", base_looks(1), ["entries", 0, "basis"]),
        ("stage1_voice_cast", base_voices(1), ["cast", 0, "character_id"]),
        ("stage1_voice_cast", base_voices(1), ["cast", 0, "voice_key"]),
        ("stage1_voice_cast", base_voices(1), ["cast", 0, "voice_id"]),
        ("stage1_voice_cast", base_voices(1), ["cast", 0, "gender"]),
        ("stage1_voice_cast", base_voices(1), ["cast", 0, "status"]),
        ("stage1_sound_suggestions", base_sounds(1), ["cues", 0, "scene_id"]),
        ("stage1_sound_suggestions", base_sounds(1), ["cues", 0, "anchor_line_id"]),
        ("stage1_sound_suggestions", base_sounds(1), ["cues", 0, "sound_id"]),
        ("stage1_sound_suggestions", base_sounds(1), ["cues", 0, "kind"]),
        ("stage1_sound_suggestions", base_sounds(1), ["cues", 0, "purpose"]),
        ("stage1_sound_suggestions", base_sounds(1), ["cues", 0, "basis"]),
        ("stage1_questions", base_questions(1), ["questions", 0, "id"]),
        ("stage1_questions", base_questions(1), ["questions", 0, "text"]),
    ])
    def test_required_field_missing(self, schemas_dir, schema_name, doc_base, missing_path):
        schema = load_schema(schemas_dir, schema_name)
        doc = delete_field(doc_base, missing_path)
        errs = validate(doc, schema)
        assert errs, f"{schema_name}: missing {missing_path} should error"
        field_name = missing_path[-1]
        assert any(field_name in e for e in errs), f"{schema_name}: field {field_name} not in errors: {errs}"


class TestCommonTypeBoundaries:
    """Parameterized boundary tests for common types across schemas."""
    @pytest.mark.parametrize("schema_name,instance,should_pass", [
        # scene_id: S0 and S100 are SCHEMA-valid (prefix matching is semantic)
        ("stage1_scenes", {"adhyay": 1, "scenes": [{"scene_id": "S0", "section_kind": "story", "ovi_range": [1,1], "goal": "g", "turn": {"ovi": 1, "text": "t"}, "line_ids": [], "teaching_treatment": "none"}]}, True),
        ("stage1_scenes", {"adhyay": 1, "scenes": [{"scene_id": "S100", "section_kind": "story", "ovi_range": [1,1], "goal": "g", "turn": {"ovi": 1, "text": "t"}, "line_ids": [], "teaching_treatment": "none"}]}, True),
        ("stage1_scenes", {"adhyay": 1, "scenes": [{"scene_id": "S1", "section_kind": "story", "ovi_range": [1,1], "goal": "g", "turn": {"ovi": 1, "text": "t"}, "line_ids": [], "teaching_treatment": "none"}]}, True),
        ("stage1_scenes", {"adhyay": 1, "scenes": [{"scene_id": "X1", "section_kind": "story", "ovi_range": [1,1], "goal": "g", "turn": {"ovi": 1, "text": "t"}, "line_ids": [], "teaching_treatment": "none"}]}, False),
        # shot_id
        ("stage1_shots", {"adhyay": 1, "shots": [{"shot_id": "S1-1", "scene_id": "S1", "ovi_ids": [1], "beat_line_ids": ["S1-L1"], "preset": "01_wide", "need_new": None, "needs_cutout": False, "pose": "x", "framing": "x"}]}, True),
        ("stage1_shots", {"adhyay": 1, "shots": [{"shot_id": "S1_1", "scene_id": "S1", "ovi_ids": [1], "beat_line_ids": ["S1-L1"], "preset": "01_wide", "need_new": None, "needs_cutout": False, "pose": "x", "framing": "x"}]}, False),
        # line_id
        ("stage1_scenes", {"adhyay": 1, "scenes": [{"scene_id": "S1", "section_kind": "story", "ovi_range": [1,1], "goal": "g", "turn": {"ovi": 1, "text": "t"}, "line_ids": ["S1-L1"], "teaching_treatment": "none"}]}, True),
        ("stage1_scenes", {"adhyay": 1, "scenes": [{"scene_id": "S1", "section_kind": "story", "ovi_range": [1,1], "goal": "g", "turn": {"ovi": 1, "text": "t"}, "line_ids": ["S1-L"], "teaching_treatment": "none"}]}, False),
        # image_id: s9_wrong is SCHEMA-valid (scene prefix is semantic)
        ("stage1_image_briefs", {"adhyay": 1, "images": [{"image_id": "s1_valid_name", "scene_id": "S1", "shot_ids": ["S1-1"], "people": [{"name": "A", "position": "c", "pose": "p", "gaze": "g"}], "place_id": "p", "prop": None, "prop_state": None, "camera": "c", "light": "l", "reason_new": "r", "on_screen_facts": ["f"], "references": {"characters": [], "place": "p", "style_anchor": "s", "prop": None}}]}, True),
        ("stage1_image_briefs", {"adhyay": 1, "images": [{"image_id": "s9_wrong", "scene_id": "S1", "shot_ids": ["S1-1"], "people": [{"name": "A", "position": "c", "pose": "p", "gaze": "g"}], "place_id": "p", "prop": None, "prop_state": None, "camera": "c", "light": "l", "reason_new": "r", "on_screen_facts": ["f"], "references": {"characters": [], "place": "p", "style_anchor": "s", "prop": None}}]}, True),
        ("stage1_image_briefs", {"adhyay": 1, "images": [{"image_id": "S1_wrong", "scene_id": "S1", "shot_ids": ["S1-1"], "people": [{"name": "A", "position": "c", "pose": "p", "gaze": "g"}], "place_id": "p", "prop": None, "prop_state": None, "camera": "c", "light": "l", "reason_new": "r", "on_screen_facts": ["f"], "references": {"characters": [], "place": "p", "style_anchor": "s", "prop": None}}]}, False),
        # ovi minimum
        ("stage1_story_map", {"adhyay": 1, "ovi_types": [{"ovi": 1, "type": "STORY"}], "events": []}, True),
        ("stage1_story_map", {"adhyay": 1, "ovi_types": [{"ovi": 0, "type": "STORY"}], "events": []}, False),
        # adhyay bounds
        ("stage1_story_map", {"adhyay": 1, "ovi_types": [{"ovi": 1, "type": "STORY"}], "events": []}, True),
        ("stage1_story_map", {"adhyay": 21, "ovi_types": [{"ovi": 1, "type": "STORY"}], "events": []}, True),
        ("stage1_story_map", {"adhyay": 0, "ovi_types": [{"ovi": 1, "type": "STORY"}], "events": []}, False),
        ("stage1_story_map", {"adhyay": 22, "ovi_types": [{"ovi": 1, "type": "STORY"}], "events": []}, False),
        # text length 1..400
        ("stage1_story_map", {"adhyay": 1, "ovi_types": [{"ovi": 1, "type": "STORY"}], "events": [{"event_id": "E1", "title": "x", "ovi_range": [1,1], "key_ovis": [1], "kind": "story", "closure": "NA"}]}, True),
        ("stage1_story_map", {"adhyay": 1, "ovi_types": [{"ovi": 1, "type": "STORY"}], "events": [{"event_id": "E1", "title": "x"*400, "ovi_range": [1,1], "key_ovis": [1], "kind": "story", "closure": "NA"}]}, True),
        ("stage1_story_map", {"adhyay": 1, "ovi_types": [{"ovi": 1, "type": "STORY"}], "events": [{"event_id": "E1", "title": "", "ovi_range": [1,1], "key_ovis": [1], "kind": "story", "closure": "NA"}]}, False),
        ("stage1_story_map", {"adhyay": 1, "ovi_types": [{"ovi": 1, "type": "STORY"}], "events": [{"event_id": "E1", "title": "x"*401, "ovi_range": [1,1], "key_ovis": [1], "kind": "story", "closure": "NA"}]}, False),
        # preset_id pattern
        ("stage1_shots", {"adhyay": 1, "shots": [{"shot_id": "S1-1", "scene_id": "S1", "ovi_ids": [1], "beat_line_ids": ["S1-L1"], "preset": "01_wide_shot", "need_new": None, "needs_cutout": False, "pose": "x", "framing": "x"}]}, True),
        ("stage1_shots", {"adhyay": 1, "shots": [{"shot_id": "S1-1", "scene_id": "S1", "ovi_ids": [1], "beat_line_ids": ["S1-L1"], "preset": "wide_shot", "need_new": None, "needs_cutout": False, "pose": "x", "framing": "x"}]}, False),
        # sound_id pattern
        ("stage1_sound_suggestions", {"adhyay": 1, "cues": [{"scene_id": "S1", "anchor_line_id": "S1-L1", "sound_id": "bed_ambience", "kind": "bed", "purpose": "p", "basis": "stated"}]}, True),
        ("stage1_sound_suggestions", {"adhyay": 1, "cues": [{"scene_id": "S1", "anchor_line_id": "S1-L1", "sound_id": "fx_conch", "kind": "fx", "purpose": "p", "basis": "stated"}]}, True),
        ("stage1_sound_suggestions", {"adhyay": 1, "cues": [{"scene_id": "S1", "anchor_line_id": "S1-L1", "sound_id": "NEED_NEW", "kind": "fx", "sound_prompt": "p", "purpose": "p", "basis": "stated"}]}, True),
        ("stage1_sound_suggestions", {"adhyay": 1, "cues": [{"scene_id": "S1", "anchor_line_id": "S1-L1", "sound_id": "invalid", "kind": "bed", "purpose": "p", "basis": "stated"}]}, False),
        # voice_id length 10..40
        ("stage1_voice_cast", {"adhyay": 1, "cast": [{"character_id": "c", "voice_key": "k", "voice_id": "x"*10, "gender": "male", "status": "RECURRING"}]}, True),
        ("stage1_voice_cast", {"adhyay": 1, "cast": [{"character_id": "c", "voice_key": "k", "voice_id": "x"*40, "gender": "male", "status": "RECURRING"}]}, True),
        ("stage1_voice_cast", {"adhyay": 1, "cast": [{"character_id": "c", "voice_key": "k", "voice_id": "x"*9, "gender": "male", "status": "RECURRING"}]}, False),
        ("stage1_voice_cast", {"adhyay": 1, "cast": [{"character_id": "c", "voice_key": "k", "voice_id": "x"*41, "gender": "male", "status": "RECURRING"}]}, False),
        # question_id pattern
        ("stage1_questions", {"adhyay": 1, "questions": [{"id": "Q1", "text": "t"}]}, True),
        ("stage1_questions", {"adhyay": 1, "questions": [{"id": "X1", "text": "t"}]}, False),
    ])
    def test_boundaries(self, schemas_dir, schema_name, instance, should_pass):
        schema = load_schema(schemas_dir, schema_name)
        errs = validate(instance, schema)
        if should_pass:
            assert errs == [], f"expected pass, got: {errs}"
        else:
            assert errs, f"expected failure, got none"


class TestOldSchemasUnchanged:
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
        assert len(written) == 13
        for p in written:
            assert p.exists()
            assert p.suffix == ".json"

    def test_refuses_overwrite(self, tmp_path):
        make_schemas.write_all(tmp_path, overwrite=False)
        with pytest.raises(FileExistsError):
            make_schemas.write_all(tmp_path, overwrite=False)

    def test_overwrite_replaces(self, tmp_path):
        make_schemas.write_all(tmp_path, overwrite=False)
        # Corrupt one file
        target = tmp_path / "stage1_story_map.schema.json"
        target.write_text("corrupted")
        # Overwrite should restore
        written = make_schemas.write_all(tmp_path, overwrite=True)
        assert len(written) == 13
        data = json.loads(target.read_text())
        assert data.get("$schema") == "https://json-schema.org/draft/2020-12/schema"

    def test_generated_schema_dialect(self, tmp_path):
        make_schemas.write_all(tmp_path, overwrite=False)
        for p in tmp_path.glob("*.schema.json"):
            data = json.loads(p.read_text())
            assert data.get("$schema") == "https://json-schema.org/draft/2020-12/schema"

    def test_main_cli(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["make_schemas.py", "--out", str(tmp_path), "--overwrite"])
        make_schemas.main()
        assert len(list(tmp_path.glob("*.schema.json"))) == 13
