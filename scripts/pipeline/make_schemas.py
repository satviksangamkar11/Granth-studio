"""Writes schemas/*.schema.json (the file contracts between pipeline stages). Run once; the JSON files are the contract, this script documents how they were generated.
Rules baked in: Kimi outputs carry NO timings, dialogue, claims or images_needed (additionalProperties false); Stage 1 image briefs use scene-prefixed ids; Stage 2 may use catalog ids only."""
import json
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "schemas"
SHA = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
TXT = {"type": "string", "minLength": 1, "maxLength": 400}
SCENE_ID = {"type": "string", "pattern": "^S[0-9]{1,2}$"}
SHOT_ID = {"type": "string", "pattern": "^S[0-9]{1,2}-[0-9]{1,2}$"}
LINE_ID = {"type": "string", "pattern": "^S[0-9]{1,2}-L[0-9]{1,3}$"}
IMG_ID = {"type": "string", "pattern": "^s[0-9]{1,2}_[a-z][a-z0-9_]{0,40}$"}
CAT_ID = {"type": "string", "pattern": "^SH_S[0-9]{1,2}_[0-9]{2}$"}
OVI = {"type": "integer", "minimum": 1}
ADH = {"type": "integer", "minimum": 1, "maximum": 21}


def obj(props, req=None):
    return {"type": "object", "additionalProperties": False, "required": req or list(props), "properties": props}


def arr(item, min_items=0):
    return {"type": "array", "minItems": min_items, "items": item}


SHOT_ANIM = obj({"shot_id": SHOT_ID, "preset": {"type": "string", "minLength": 1}, "assets": {"type": "object", "additionalProperties": CAT_ID}, "held_pose": TXT,
                 "transition_out": {"enum": ["cut", "slide", "pan_bridge"]},
                 "need_new": {"anyOf": [{"type": "null"}, obj({"reason": TXT, "class": {"enum": ["missing_image", "json_arrangement", "renderer_gap"]}})]}})
DEFS = {
    "stage1_scenes": obj({"adhyay": ADH, "scenes": arr(obj({"scene_id": SCENE_ID, "ovi_range": {"type": "array", "minItems": 2, "maxItems": 2, "items": OVI}, "goal": TXT,
                                                           "turn": obj({"ovi": OVI, "text": TXT}), "line_ids": arr(LINE_ID, 1)}), 1)}),
    "stage1_shots": obj({"adhyay": ADH, "shots": arr(obj({"shot_id": SHOT_ID, "scene_id": SCENE_ID, "ovi_ids": arr(OVI, 1), "beat_line_ids": arr(LINE_ID), "preset_hint": {"type": "string"},
                                                          "needs_cutout": {"type": "boolean"}, "pose": TXT, "framing": TXT}), 1)}),
    "stage1_image_briefs": obj({"adhyay": ADH, "images": arr(obj({"image_id": IMG_ID, "scene_id": SCENE_ID, "shot_ids": arr(SHOT_ID, 1),
                                                                 "people": arr(obj({"name": TXT, "position": TXT, "pose": TXT, "gaze": TXT})), "place_id": TXT,
                                                                 "prop": {"type": ["string", "null"]}, "camera": TXT, "reason_new": TXT}))}),
    "stage1_sound_suggestions": obj({"adhyay": ADH, "cues": arr(obj({"scene_id": SCENE_ID, "anchor_line_id": LINE_ID,
                                                                     "palette_id": {"type": "string", "pattern": "^(bed|fx)_[a-z0-9_]+$|^NEED_NEW$"}, "kind": {"enum": ["bed", "fx"]}, "reason": TXT},
                                                                    ["scene_id", "anchor_line_id", "palette_id", "kind"]))}),
    "stage1_questions": obj({"adhyay": ADH, "questions": arr(obj({"id": {"type": "string", "pattern": "^Q[0-9]+$"}, "text": TXT, "scene_id": SCENE_ID}, ["id", "text"]))}),
    "beats": obj({"adhyay": ADH, "scenes": arr(obj({"scene_id": SCENE_ID, "beats": arr(obj({"line_id": LINE_ID, "voice": TXT, "mr_s": {"type": "number", "exclusiveMinimum": 0},
                                                                                           "hi_s": {"type": "number", "exclusiveMinimum": 0}, "start_s": {"type": "number", "minimum": 0},
                                                                                           "end_s": {"type": "number", "exclusiveMinimum": 0}, "shot": {"type": "integer", "minimum": 1}}))}))}),
    "image_catalog": obj({"adhyay": ADH, "images": {"type": "object", "additionalProperties": obj({"file": TXT, "sha256": SHA, "chosen_version": {"type": "integer", "minimum": 1},
                                                                                                 "prompt_sha256": SHA, "model": TXT, "edit_id": {"type": ["string", "null"]},
                                                                                                 "approved": {"type": "boolean"}})}}),
    "animation_scene": obj({"adhyay": ADH, "scene_id": SCENE_ID, "shots": arr(SHOT_ANIM, 1)}),
    "shot_plan": obj({"adhyay": ADH, "scene_id": SCENE_ID,
                      "fingerprints": obj({"script": SHA, "timing": SHA, "presets": SHA, "images": {"type": "object", "additionalProperties": SHA}}),
                      "shots": arr(SHOT_ANIM, 1), "approved_by": TXT, "approved_date": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"}}),
}


def main():
    OUT.mkdir(exist_ok=True)
    for name, body in DEFS.items():
        target = OUT / f"{name}.schema.json"
        if target.exists() and "--overwrite" not in sys.argv:
            sys.exit(f"{target} exists; pass --overwrite to replace it")
        target.write_text(json.dumps({"$schema": "https://json-schema.org/draft/2020-12/schema", "title": name, **body}, indent=1), encoding="utf-8")
    print(len(DEFS), "schemas in", OUT)


if __name__ == "__main__":
    main()
