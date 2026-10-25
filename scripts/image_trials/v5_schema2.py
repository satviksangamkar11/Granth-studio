"""Shot JSON contract v2 for Builder v2 (D-017). Data only: IDs, times and bounded numbers. The look is the original flat colours (no riso block, D-016).
validate(shot, asset_names) returns a list of problems (empty = valid). Includes a minimum-motion rule so no shot can be as static as Phase 1 shot 1."""
from __future__ import annotations

import jsonschema

FRAMES = 144
COLOR = {"type": "string", "pattern": "^#[0-9a-fA-F]{6}$"}
NUM = lambda lo, hi: {"type": "number", "minimum": lo, "maximum": hi}
EASE = {"enum": ["linear", "ease_in_out", "ease_out", "ease_in"]}
CAM = {"type": "object", "additionalProperties": False, "required": ["x", "y", "zoom"],
       "properties": {"x": NUM(-1, 1), "y": NUM(-1, 1), "zoom": NUM(0.5, 3)}}
IDLE = {"type": "object", "additionalProperties": False, "required": ["amplitude", "period_sec"],
        "properties": {"amplitude": NUM(0, 0.03), "period_sec": NUM(1.5, 8)}}              # breathing: scale about the bottom edge
SWAY = {"type": "object", "additionalProperties": False, "required": ["angle_deg", "period_sec"],
        "properties": {"angle_deg": NUM(0, 6), "period_sec": NUM(1.5, 8), "phase": NUM(0, 1)}}   # rotation about the top edge (hanging leaves)
WARP = {"type": "object", "additionalProperties": False, "required": ["u", "v", "radius", "start", "end"],
        "properties": {"u": NUM(0, 1), "v": NUM(0, 1), "radius": NUM(0.05, 0.5), "start": {"type": "integer", "minimum": 1, "maximum": FRAMES},
                       "end": {"type": "integer", "minimum": 1, "maximum": FRAMES}, "rotate_deg": NUM(-25, 25), "dx": NUM(-0.1, 0.1), "dy": NUM(-0.1, 0.1)}}
LAYER = {"type": "object", "additionalProperties": False, "required": ["asset", "depth", "x", "y", "scale"],
         "properties": {"asset": {"type": "string", "pattern": "^[a-z][a-z0-9_]{0,31}$"},
                        "depth": NUM(0, 10), "x": NUM(-2, 2), "y": NUM(-2, 2), "scale": NUM(0.05, 5),
                        "opacity": NUM(0, 1), "blend": {"enum": ["normal", "add"]},
                        "move": {"type": "object", "additionalProperties": False,
                                 "properties": {"dx": NUM(-1, 1), "dy": NUM(-1, 1), "dscale": NUM(-0.5, 0.5)}},
                        "idle": IDLE, "sway": SWAY, "soft_warp": WARP}}
HALO = {"type": "object", "additionalProperties": False, "required": ["x", "y", "radius"],
        "properties": {"x": NUM(-2, 2), "y": NUM(-1, 1), "radius": NUM(0.05, 1.5), "color": COLOR, "intensity": NUM(0, 1), "pulse_period_sec": NUM(2, 10)}}
BACKDROP = {"type": "object", "additionalProperties": False, "required": ["top", "bottom"],
            "properties": {"top": COLOR, "bottom": COLOR, "floor_y": NUM(-0.5625, 0.5625), "floor_color": COLOR, "halo": HALO}}
ATMOS = {"type": "object", "additionalProperties": False,
         "properties": {"gloss": NUM(0, 1), "warm_tint": COLOR, "dust": NUM(0, 1), "vignette": NUM(0, 1)}}
TRANS = {"type": "object", "additionalProperties": False, "required": ["after_segment", "kind", "frames"],
         "properties": {"after_segment": {"type": "integer", "minimum": 0, "maximum": 6},
                        "kind": {"enum": ["cut", "slide", "pan_bridge"]},
                        "frames": {"type": "integer", "minimum": 3, "maximum": 8},
                        "direction": {"enum": ["left", "right", "up", "down"]}}}
SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["shot_id", "frames", "backdrop", "segments"],
    "properties": {
        "shot_id": {"type": "string", "pattern": "^S[A-Z]$"},
        "frames": {"type": "integer", "const": FRAMES},
        "on_twos": {"type": "boolean"},
        "backdrop": BACKDROP,
        "atmosphere": ATMOS,
        "transitions": {"type": "array", "maxItems": 6, "items": TRANS},
        "segments": {"type": "array", "minItems": 1, "maxItems": 8, "items": {
            "type": "object", "additionalProperties": False, "required": ["start", "end", "layers", "camera"],
            "properties": {"start": {"type": "integer", "minimum": 1, "maximum": FRAMES},
                           "end": {"type": "integer", "minimum": 1, "maximum": FRAMES},
                           "layers": {"type": "array", "minItems": 1, "maxItems": 8, "items": LAYER},
                           "camera": {"type": "object", "additionalProperties": False, "required": ["start", "end"],
                                      "properties": {"start": CAM, "end": CAM, "ease": EASE}}}}},
    },
}
MIN_SEGMENT_MOTION = 0.04       # |zoom change| + |pan change| per segment
MIN_SHOT_ZOOM = 0.12            # at least one segment changes zoom by this much


def validate(shot, asset_names: set) -> list[str]:
    problems = [f"{'/'.join(map(str, e.path)) or 'shot'}: {e.message}" for e in jsonschema.Draft202012Validator(SCHEMA).iter_errors(shot)]
    if problems:
        return problems
    expect, best_zoom = 1, 0.0
    for i, seg in enumerate(shot["segments"]):
        if seg["start"] != expect or seg["end"] < seg["start"]:
            problems.append(f"segments/{i}: must start at frame {expect} and end at or after its start (segments are contiguous)")
        expect = seg["end"] + 1
        for lay in seg["layers"]:
            if lay["asset"] not in asset_names:
                problems.append(f"segments/{i}: unknown asset {lay['asset']}")
            w = lay.get("soft_warp")
            if w and not (seg["start"] <= w["start"] <= w["end"] <= seg["end"]):
                problems.append(f"segments/{i}: soft_warp frames must lie inside the segment")
        c0, c1 = seg["camera"]["start"], seg["camera"]["end"]
        dz = abs(c1["zoom"] - c0["zoom"])
        motion = dz + abs(c1["x"] - c0["x"]) + abs(c1["y"] - c0["y"])
        best_zoom = max(best_zoom, dz)
        if motion < MIN_SEGMENT_MOTION and seg["end"] - seg["start"] >= 23:
            problems.append(f"segments/{i}: camera barely moves (zoom+pan change {motion:.3f} < {MIN_SEGMENT_MOTION}); give it a real move")
    if expect != FRAMES + 1:
        problems.append(f"segments must cover frames 1-{FRAMES} exactly")
    if best_zoom < MIN_SHOT_ZOOM:
        problems.append(f"no segment zooms by at least {MIN_SHOT_ZOOM} (best {best_zoom:.3f})")
    for j, t in enumerate(shot.get("transitions", [])):
        if t["after_segment"] >= len(shot["segments"]) - 1:
            problems.append(f"transitions/{j}: after_segment must be a segment that has a next segment")
    return problems
