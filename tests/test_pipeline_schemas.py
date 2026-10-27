import copy
import json
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[1]
SC = ROOT / "schemas"
SHA = "a" * 64
GOOD = {
    "stage1_scenes": {"adhyay": 1, "scenes": [{"scene_id": "S4", "ovi_range": [108, 112], "goal": "g", "turn": {"ovi": 112, "text": "t"}, "line_ids": ["S4-L1", "S4-L2"]}]},
    "stage1_shots": {"adhyay": 1, "shots": [{"shot_id": "S4-1", "scene_id": "S4", "ovi_ids": [108, 109], "beat_line_ids": ["S4-L1"], "preset_hint": "03_slow_cinematic_push", "needs_cutout": False, "pose": "p", "framing": "f"}]},
    "stage1_image_briefs": {"adhyay": 1, "images": [{"image_id": "s4_maharaj_seated", "scene_id": "S4", "shot_ids": ["S4-3"], "people": [{"name": "Maharaj", "position": "centre", "pose": "seated", "gaze": "forward"}], "place_id": "road", "prop": None, "camera": "medium", "reason_new": "new pose"}]},
    "stage1_sound_suggestions": {"adhyay": 1, "cues": [{"scene_id": "S4", "anchor_line_id": "S4-L1", "palette_id": "bed_village", "kind": "bed"}, {"scene_id": "S4", "anchor_line_id": "S4-L3", "palette_id": "NEED_NEW", "kind": "fx", "reason": "silence cue"}]},
    "stage1_questions": {"adhyay": 1, "questions": [{"id": "Q1", "text": "q"}]},
    "beats": {"adhyay": 1, "scenes": [{"scene_id": "S4", "beats": [{"line_id": "S4-L1", "voice": "narrator", "mr_s": 2.8, "hi_s": 2.88, "start_s": 0.5, "end_s": 3.38, "shot": 1}]}]},
    "image_catalog": {"adhyay": 1, "images": {"SH_S4_01": {"file": "SH_S4_01.png", "sha256": SHA, "chosen_version": 2, "prompt_sha256": SHA, "model": "Nano Banana Pro", "edit_id": None, "approved": False}}},
    "animation_scene": {"adhyay": 1, "scene_id": "S4", "shots": [{"shot_id": "S4-1", "preset": "03_slow_cinematic_push", "assets": {"img": "SH_S4_01"}, "held_pose": "p", "transition_out": "cut", "need_new": None},
                                                                 {"shot_id": "S4-2", "preset": "NEED_NEW", "assets": {}, "held_pose": "bow", "transition_out": "cut", "need_new": {"reason": "bow", "class": "missing_image"}}]},
}
GOOD["shot_plan"] = {"adhyay": 1, "scene_id": "S4", "fingerprints": {"script": SHA, "timing": SHA, "presets": SHA, "images": {"SH_S4_01": SHA}}, "shots": GOOD["animation_scene"]["shots"],
                     "approved_by": "owner", "approved_date": "2026-10-27"}


def load(name):
    return json.loads((SC / f"{name}.schema.json").read_text(encoding="utf-8"))


def errors(name, doc):
    return list(jsonschema.Draft202012Validator(load(name)).iter_errors(doc))


@pytest.mark.parametrize("name", sorted(GOOD))
def test_valid_example_passes(name):
    assert errors(name, GOOD[name]) == []


@pytest.mark.parametrize("name", sorted(GOOD))
def test_schema_itself_is_valid_and_an_extra_key_fails(name):
    jsonschema.Draft202012Validator.check_schema(load(name))
    bad = copy.deepcopy(GOOD[name])
    bad["surprise"] = 1
    assert errors(name, bad)


def test_every_schema_file_has_an_example():
    assert {p.name.removesuffix(".schema.json") for p in SC.glob("*.schema.json")} == set(GOOD)


@pytest.mark.parametrize("name", ["stage1_shots", "animation_scene"])
@pytest.mark.parametrize("key", ["start_s", "dialogue", "claims", "images_needed"])
def test_timings_dialogue_and_claims_are_rejected_in_kimi_outputs(name, key):
    bad = copy.deepcopy(GOOD[name])
    bad["shots"][0][key] = 1
    assert errors(name, bad)


def test_ids_must_follow_the_contract():
    bad = copy.deepcopy(GOOD["animation_scene"])
    bad["shots"][0]["assets"]["img"] = "s4_new_image"                        # Stage 2 may only use catalog ids
    assert errors("animation_scene", bad)
    bad = copy.deepcopy(GOOD["stage1_image_briefs"])
    bad["images"][0]["image_id"] = "maharaj_seated"                          # Stage 1 briefs carry the scene prefix
    assert errors("stage1_image_briefs", bad)
    bad = copy.deepcopy(GOOD["image_catalog"])
    bad["images"]["SH_S4_01"]["sha256"] = "xyz"
    assert errors("image_catalog", bad)
