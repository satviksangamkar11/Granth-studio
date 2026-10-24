import importlib.util
import subprocess
import sys

import pytest

from tests.conftest import REPO, have_tool

pytestmark = pytest.mark.skipif(not have_tool("ffmpeg"), reason="ffmpeg required")


def load():
    spec = importlib.util.spec_from_file_location("parallax", REPO / "scripts" / "animation" / "parallax.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["parallax"] = module
    spec.loader.exec_module(module)
    return module


def base(tmp_path, **extra):
    image = tmp_path / "a.png"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=600x400:rate=1,boxblur=3", "-frames:v", "1", str(image)], check=True)
    return {"image": str(image), "duration_s": 1.0, "fps": 24, "size": [288, 192],
            "camera": {"start": {"zoom": 1.2, "cx": 0.5, "cy": 0.5}, "end": {"zoom": 1.2, "cx": 0.5, "cy": 0.5}, "ease": "smooth"}, **extra}


def test_the_parallax_values_are_validated_ramp_with_the_camera_easing_and_neighbouring_shots_can_be_continuous(tmp_path):
    p = load()
    for bad in ({"amplitude": 0.5}, {"amplitude": True}, {"start": 0.5, "end": 0.0}, {"amplitude": 0.01, "start": 0.0}, {"strength": 1}):
        with pytest.raises(p.motion.SpecError, match="parallax"):
            p.validate(base(tmp_path, parallax=bad))
    spec = p.validate(base(tmp_path, parallax={"start": -0.008, "end": 0.004}))
    shifts = [p.shift_at(spec, f) for f in range(p.motion.frame_count(spec))]
    assert abs(shifts[0] + 0.008) < 1e-12 and abs(shifts[-1] - 0.004) < 1e-12 and all(a <= b for a, b in zip(shifts, shifts[1:]))
    held = base(tmp_path, parallax={"start": -0.008, "end": 0.008})
    held["camera"] = {**held["camera"], "ease": "hold"}
    with pytest.raises(p.motion.SpecError, match="hold"):
        p.validate(held)                                                                             # a held shot never reaches the declared end: refuse the ramp
    held["parallax"] = {"start": 0.004, "end": 0.004}
    assert p.validate(held)
    short = p.validate(base(tmp_path, parallax={"amplitude": 0.016}))
    assert p.ends(short) == (-0.008, 0.008) and p.shift_at({**spec, "parallax": {}}, 5) == 0.0     # shorthand, and no block means no shift
    rp_spec = importlib.util.spec_from_file_location("render_motion_preview", REPO / "scripts" / "pilot" / "render_motion_preview.py")
    rp = importlib.util.module_from_spec(rp_spec); sys.modules["render_motion_preview"] = rp; rp_spec.loader.exec_module(rp)
    for scene, shots in rp.PARALLAX.items():
        assert all(shots[i][1] == shots[i + 1][0] for i in range(2)) and shots[2][1] == shots[0][0]    # no jump at either cut, and the scene returns to its start
    (tmp_path / "sub").mkdir()
    with pytest.raises(p.motion.SpecError, match="spec's folder"):
        p.render({**base(tmp_path), "image": "../a.png"}, tmp_path / "x.mp4", base=tmp_path / "sub")


def test_near_and_far_content_slide_in_opposite_directions_by_the_expected_amount(tmp_path):
    torch = pytest.importorskip("torch")
    np = pytest.importorskip("numpy")
    pytest.importorskip("PIL")
    from PIL import Image
    p = load()
    depth = np.zeros((400, 600), dtype="float32")
    depth[:, 300:] = 1.0                                                                             # left half far (0), right half near (1): a stub, no model download
    p.estimate_depth = lambda image_path, cache: depth
    image = np.zeros((400, 600, 3), dtype="uint8")
    image[195:205, 145:155] = 255                                                                    # a white dot in the far half
    image[195:205, 445:455] = 255                                                                    # and one in the near half
    Image.fromarray(image).save(tmp_path / "dots.png")
    spec = {"image": str(tmp_path / "dots.png"), "duration_s": 1.0, "fps": 24, "size": [288, 192],
            "camera": {"start": {"zoom": 1.0, "cx": 0.5, "cy": 0.5}, "end": {"zoom": 1.0, "cx": 0.5, "cy": 0.5}, "ease": "hold"}, "parallax": {"start": -0.01, "end": -0.01}}
    centroids = {}
    for label, shift in (("first", -0.01), ("last", 0.01)):
        clip = tmp_path / f"{label}.mp4"
        p.render({**spec, "parallax": {"start": shift, "end": shift}}, clip)
        frame = tmp_path / f"{label}.png"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(clip), "-frames:v", "1", str(frame)], check=True)
        gray = np.asarray(Image.open(frame).convert("L"), dtype="float32")
        columns = (gray > 100).sum(axis=0).astype("float32")
        left, right = columns[:144], columns[144:]
        centroids[label] = (float((np.arange(144) * left).sum() / left.sum()), float(144 + (np.arange(144) * right).sum() / right.sum()))
    far_move = centroids["last"][0] - centroids["first"][0]
    near_move = centroids["last"][1] - centroids["first"][1]
    expected = 0.02 * 288                                                                            # the shift moves by 0.02 of the width; depth 1 and 0 slide equally and oppositely
    assert far_move > 0 and near_move < 0, (far_move, near_move)
    assert abs(far_move - expected) < 2.0 and abs(near_move + expected) < 2.0, (far_move, near_move, expected)
