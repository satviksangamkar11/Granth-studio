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


def test_the_parallax_amount_is_validated_and_ramps_with_the_camera_easing(tmp_path):
    p = load()
    with pytest.raises(p.motion.SpecError, match="amplitude"):
        p.validate(base(tmp_path, parallax={"amplitude": 0.5}))
    with pytest.raises(p.motion.SpecError, match="amplitude"):
        p.validate(base(tmp_path, parallax={"amplitude": True}))
    spec = p.validate(base(tmp_path, parallax={"amplitude": 0.016}))
    shifts = [p.shift_at(spec, f) for f in range(p.motion.frame_count(spec))]
    assert abs(shifts[0] + 0.008) < 1e-12 and abs(shifts[-1] - 0.008) < 1e-12 and all(a <= b for a, b in zip(shifts, shifts[1:]))
    assert p.shift_at({**spec, "parallax": {}}, 5) == 0.0                                            # no parallax block: no shift


def test_near_pixels_move_more_than_far_pixels(tmp_path):
    torch = pytest.importorskip("torch")
    np = pytest.importorskip("numpy")
    pytest.importorskip("PIL")
    p = load()
    depth = np.zeros((400, 600), dtype="float32")
    depth[:, 300:] = 1.0                                                                             # left half far, right half near (a stub: no model download)
    p.estimate_depth = lambda image_path, cache: depth
    spec = base(tmp_path, parallax={"amplitude": 0.02})
    clip = tmp_path / "p.mp4"
    p.render(spec, clip)
    frames = {}
    for index in (0, 23):
        out = tmp_path / f"f{index}.png"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(clip), "-vf", f"select=eq(n\\,{index})", "-frames:v", "1", str(out)], check=True)
        frames[index] = out
    still = tmp_path / "still.mp4"
    flat = dict(spec, parallax={"amplitude": 0.0})
    p.render(flat, still)
    assert clip.stat().st_size > 0 and still.stat().st_size > 0
    from PIL import Image
    a, b = (np.asarray(Image.open(frames[i]).convert("L"), dtype="float32") for i in (0, 23))
    far_change = float(np.abs(a[:, :100] - b[:, :100]).mean())                                       # inside the far half
    near_change = float(np.abs(a[:, 190:] - b[:, 190:]).mean())                                      # inside the near half
    assert near_change > far_change
