"""Flat preset variants 12-17 (owner 2026-11-01: flat-first for Adhyay 1): camera paths for ONE flat final, rendered by motion.py."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from granthstudio import motion
from granthstudio.ffmpeg import probe

ROOT = Path(__file__).resolve().parents[1]
PRESETS = ROOT / "assets" / "v5_presets"
FLAT = ["12_flat_push_in", "13_flat_pull_out", "14_flat_pan_left", "15_flat_pan_right", "16_flat_tilt_up", "17_flat_hold"]
FINAL = Path("D:/aai work/flow_outputs/adhyay_01/final_clean/SH_S4_01.png")


def _load(name: str) -> dict:
    return json.loads((PRESETS / f"{name}.json").read_text(encoding="utf-8"))


def _move(cam: dict) -> tuple[float, float]:
    s, e = cam["start"], cam["end"]
    return abs(e["zoom"] - s["zoom"]), abs(e["cx"] - s["cx"]) + abs(e["cy"] - s["cy"])


@pytest.mark.parametrize("name", FLAT)
def test_variant_is_a_valid_bounded_camera(name):
    d = _load(name)
    assert d["preset"] == name and d["renderer"] == "motion.py" and d["roles"] == ["img"]
    cam = motion.validate_camera(d["camera"])
    b = d["bounds"]
    dz, dp = _move(cam)
    for end in ("start", "end"):
        assert b["zoom"][0] <= cam[end]["zoom"] <= b["zoom"][1]
    assert dz <= b["zoom_change_max"] and dp <= b["pan_change_max"]
    if cam.get("ease") == "hold":
        assert name == b["hold_allowed_only_in"] and dz == dp == 0
    else:
        assert dz + dp >= b["move_min"], "a moving variant must really move"


@pytest.mark.parametrize("name", FLAT)
def test_window_never_leaves_the_image(name):
    spec = {"image": "x", "duration_s": 6.0, "fps": 24, "size": [1280, 720], "camera": _load(name)["camera"]}
    for f in range(motion.frame_count(spec)):
        z, cx, cy = motion.window(spec, f)
        half = 0.5 / z
        assert half - 1e-9 <= cx <= 1 - half + 1e-9 and half - 1e-9 <= cy <= 1 - half + 1e-9


def test_index_lists_every_variant_with_the_flat_role_and_both_copies_agree():
    idx = json.loads((PRESETS / "index.json").read_text(encoding="utf-8"))
    by = {x["preset"]: x for x in idx}
    for name in FLAT:
        assert by[name]["assets"] == ["img"] and by[name]["simplest_renderer"] == "motion.py"
    assert [x["preset"] for x in idx][:11] == sorted(p.stem for p in PRESETS.glob("[01][0-9]_*.json") if p.stem[:2] <= "11")
    copy = ROOT / "canon" / "packets" / "adhyay_01" / "presets_index.json"
    assert json.loads(copy.read_text(encoding="utf-8")) == idx


def test_directions_are_what_the_names_say():
    c = {n: _load(n)["camera"] for n in FLAT}
    assert c["12_flat_push_in"]["end"]["zoom"] > c["12_flat_push_in"]["start"]["zoom"]
    assert c["13_flat_pull_out"]["end"]["zoom"] < c["13_flat_pull_out"]["start"]["zoom"]
    assert c["14_flat_pan_left"]["end"]["cx"] < c["14_flat_pan_left"]["start"]["cx"]
    assert c["15_flat_pan_right"]["end"]["cx"] > c["15_flat_pan_right"]["start"]["cx"]
    assert c["16_flat_tilt_up"]["end"]["cy"] < c["16_flat_tilt_up"]["start"]["cy"]


@pytest.mark.skipif(not FINAL.is_file() or not shutil.which("ffmpeg"), reason="real final image or ffmpeg not on this machine")
@pytest.mark.parametrize("name", FLAT)
def test_full_frame_render_from_a_real_final(name, tmp_path):
    spec = {"image": str(FINAL), "duration_s": 1.0, "fps": 24, "size": [320, 180], "camera": _load(name)["camera"]}
    out = motion.render(spec, tmp_path / f"{name}.mp4")
    p = probe(out)
    assert (p.width, p.height) == (320, 180) and p.video_codec == "h264"
    assert abs(p.duration_s - 1.0) < 0.1
