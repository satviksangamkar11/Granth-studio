"""Shot JSON contract for the V5 builder (D-015 JSON route). A shot file holds only IDs, times and bounded numbers; the builder reads it as data.
validate(shot, asset_names) returns a list of problems (empty = valid)."""
from __future__ import annotations

import jsonschema

FRAMES = 144
COLOR = {"type": "string", "pattern": "^#[0-9a-fA-F]{6}$"}
NUM = lambda lo, hi: {"type": "number", "minimum": lo, "maximum": hi}
CAM = {"type": "object", "additionalProperties": False, "required": ["x", "y", "zoom"],
       "properties": {"x": NUM(-1, 1), "y": NUM(-1, 1), "zoom": NUM(0.5, 3)}}
LAYER = {"type": "object", "additionalProperties": False, "required": ["asset", "depth", "x", "y", "scale"],
         "properties": {"asset": {"type": "string", "pattern": "^[a-z][a-z0-9_]{0,31}$"},
                        "depth": NUM(0, 10), "x": NUM(-2, 2), "y": NUM(-2, 2), "scale": NUM(0.05, 5),
                        "opacity": NUM(0, 1), "blend": {"enum": ["normal", "add"]},
                        "move": {"type": "object", "additionalProperties": False,
                                 "properties": {"dx": NUM(-1, 1), "dy": NUM(-1, 1), "dscale": NUM(-0.5, 0.5)}}}}
SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["shot_id", "frames", "paper", "riso", "segments"],
    "properties": {
        "shot_id": {"type": "string", "pattern": "^S[A-Z]$"},
        "frames": {"type": "integer", "const": FRAMES},
        "paper": COLOR,
        "riso": {"type": "object", "additionalProperties": False, "required": ["inks", "dot_px", "misregister_px", "grain"],
                 "properties": {"inks": {"type": "array", "minItems": 2, "maxItems": 4, "items": COLOR},
                                "dot_px": NUM(2, 16), "misregister_px": NUM(0, 8), "grain": NUM(0, 1), "strength": NUM(0, 1)}},
        "on_twos": {"type": "boolean"},
        "segments": {"type": "array", "minItems": 1, "maxItems": 8, "items": {
            "type": "object", "additionalProperties": False, "required": ["start", "end", "layers", "camera"],
            "properties": {"start": {"type": "integer", "minimum": 1, "maximum": FRAMES},
                           "end": {"type": "integer", "minimum": 1, "maximum": FRAMES},
                           "layers": {"type": "array", "minItems": 1, "maxItems": 8, "items": LAYER},
                           "camera": {"type": "object", "additionalProperties": False, "required": ["start", "end"],
                                      "properties": {"start": CAM, "end": CAM, "ease": {"enum": ["linear", "ease_in_out"]}}}}}},
    },
}


def validate(shot, asset_names: set) -> list[str]:
    problems = [f"{'/'.join(map(str, e.path)) or 'shot'}: {e.message}" for e in jsonschema.Draft202012Validator(SCHEMA).iter_errors(shot)]
    if problems:
        return problems
    expect = 1
    for i, seg in enumerate(shot["segments"]):
        if seg["start"] != expect or seg["end"] < seg["start"]:
            problems.append(f"segments/{i}: must start at frame {expect} and end at or after its start (segments are contiguous cuts)")
        expect = seg["end"] + 1
        for lay in seg["layers"]:
            if lay["asset"] not in asset_names:
                problems.append(f"segments/{i}: unknown asset {lay['asset']}")
    if expect != FRAMES + 1:
        problems.append(f"segments must cover frames 1-{FRAMES} exactly")
    return problems
