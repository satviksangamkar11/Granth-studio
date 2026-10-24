import importlib.util
import json
import re
import subprocess
import sys

import pytest

from tests.conftest import REPO, have_tool

pytestmark = pytest.mark.skipif(not have_tool("ffmpeg"), reason="ffmpeg required")


def load():
    spec = importlib.util.spec_from_file_location("motion", REPO / "scripts" / "animation" / "motion.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["motion"] = module
    spec.loader.exec_module(module)
    return module


def make_image(path, width=1216, height=810):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"testsrc2=size={width}x{height}:rate=1,boxblur=6", "-frames:v", "1", str(path)], check=True)   # soft: PSNR must measure geometry, not resampling of fine detail
    return path


def frame_md5s(video):
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-f", "framemd5", "-"], capture_output=True, text=True, check=True).stdout
    return [line.split(",")[-1].strip() for line in out.splitlines() if line and not line.startswith("#")]


def psnr(a, b):
    done = subprocess.run(["ffmpeg", "-v", "info", "-i", str(a), "-i", str(b), "-lavfi", "psnr", "-f", "null", "-"], capture_output=True, text=True)
    match = re.search(r"average:([\d.]+|inf)", done.stderr)
    return float("inf") if match.group(1) == "inf" else float(match.group(1))


def spec_for(image, **camera):
    return {"image": str(image), "duration_s": 2.0, "fps": 24, "size": [576, 384],
            "camera": {"start": {"zoom": 1.0, "cx": 0.5, "cy": 0.5}, "end": {"zoom": 1.0, "cx": 0.5, "cy": 0.5}, "ease": "smooth", **camera}}


def test_the_spec_is_validated_before_anything_is_rendered(tmp_path):
    m = load()
    image = make_image(tmp_path / "a.png")
    with pytest.raises(m.SpecError, match="below 1"):
        m.validate(spec_for(image, start={"zoom": 0.9}))
    with pytest.raises(m.SpecError, match="leaves the image"):
        m.validate(spec_for(image, end={"zoom": 2.0, "cx": 0.9, "cy": 0.5}))
    with pytest.raises(m.SpecError, match="hold"):
        m.validate(spec_for(image, ease="hold", end={"zoom": 1.1, "cx": 0.5, "cy": 0.5}))
    with pytest.raises(m.SpecError, match="size"):
        m.validate({**spec_for(image), "size": [575, 384]})
    assert m.validate(spec_for(image))["duration_s"] == 2.0


def test_hold_gives_identical_frames_and_a_move_ends_exactly_on_its_end_window(tmp_path):
    m = load()
    image = make_image(tmp_path / "a.png")
    held = tmp_path / "hold.mp4"
    m.render(spec_for(image, ease="hold"), held)
    assert len(frame_md5s(held)) == 48
    frames = []
    for index in (0, 23, 47):
        target = tmp_path / f"hold{index}.png"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(held), "-vf", f"select=eq(n\\,{index})", "-frames:v", "1", str(target)], check=True)
        frames.append(target)
    assert psnr(frames[0], frames[1]) > 45 and psnr(frames[0], frames[2]) > 45                    # a locked-off camera: the frames match to within lossy-encoder noise
    moved = tmp_path / "move.mp4"
    spec = spec_for(image, end={"zoom": 1.5, "cx": 0.4, "cy": 0.45})
    m.render(spec, moved)
    assert len(frame_md5s(moved)) == 48
    first_ref, last_ref = tmp_path / "first.png", tmp_path / "last.png"
    for frame, target in ((0, first_ref), (47, last_ref)):
        zoom, cx, cy = m.window(spec, frame)
        w, h = 1216 / zoom, 810 / zoom                                                            # the image is already 3:2, no crop needed
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(image), "-vf", f"crop={w}:{h}:{cx * 1216 - w / 2}:{cy * 810 - h / 2},scale=576:384:flags=lanczos", "-frames:v", "1", str(target)], check=True)
    for frame, target in ((0, first_ref), (47, last_ref)):
        got = tmp_path / f"got{frame}.png"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(moved), "-vf", f"select=eq(n\\,{frame})", "-frames:v", "1", str(got)], check=True)
        assert psnr(got, target) > 27, (frame, psnr(got, target))                                 # the first and last frame are the planned windows


def test_the_camera_path_is_smooth_monotonic_and_stays_inside_the_image(tmp_path):
    m = load()
    image = make_image(tmp_path / "a.png")
    spec = spec_for(image, end={"zoom": 1.8, "cx": 0.7, "cy": 0.3})
    path = [m.window(spec, f) for f in range(48)]
    zooms = [z for z, _, _ in path]
    assert zooms[0] == 1.0 and abs(zooms[-1] - 1.8) < 1e-9 and all(a <= b + 1e-12 for a, b in zip(zooms, zooms[1:]))
    steps = [b - a for a, b in zip(zooms, zooms[1:])]
    assert steps[0] < steps[len(steps) // 2] and steps[-1] < steps[len(steps) // 2]                 # smoothstep: slow in, fast in the middle, slow out
    assert all(0.5 / z - 1e-9 <= cx <= 1 - 0.5 / z + 1e-9 and 0.5 / z - 1e-9 <= cy <= 1 - 0.5 / z + 1e-9 for z, cx, cy in path)


def test_a_wrong_aspect_image_is_cropped_not_stretched_and_the_cli_writes_the_clip(tmp_path):
    m = load()
    tall = make_image(tmp_path / "wide.png", 1600, 900)                                            # 16:9 source, 3:2 output
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(json.dumps({**spec_for(tall, ease="hold"), "image": "wide.png"}), encoding="utf-8")
    out = tmp_path / "clip.mp4"
    assert m.main(["render", str(spec_path), str(out)]) == 0                                       # a relative image path resolves next to the spec
    info = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height,nb_frames,r_frame_rate", "-of", "json", str(out)], capture_output=True, text=True, check=True).stdout
    stream = json.loads(info)["streams"][0]
    assert (stream["width"], stream["height"], int(stream["nb_frames"]), stream["r_frame_rate"]) == (576, 384, 48, "24/1")
