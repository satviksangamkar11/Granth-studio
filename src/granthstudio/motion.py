"""Code-driven animation of a painted still: exact camera paths from a JSON motion spec, rendered with FFmpeg only (no extra Python dependency).

  python scripts/animation/motion.py render SPEC.json OUT.mp4     (or: python -m granthstudio.motion render SPEC.json OUT.mp4)

Spec (all numbers are fractions of the image, so the same spec works at any resolution):
  {"image": "keyframe.png", "duration_s": 6.0, "fps": 24, "size": [1152, 768],
   "camera": {"start": {"zoom": 1.0, "cx": 0.5, "cy": 0.5}, "end": {"zoom": 1.06, "cx": 0.5, "cy": 0.47}, "ease": "smooth"}}
`zoom` 1.0 shows the whole image, 2.0 shows half its width. `cx`/`cy` are the centre of the visible window. `ease` is smooth (smoothstep), linear or hold
(no movement: every frame identical). The moving window is clamped inside the image, the image is first cropped to the output aspect ratio, and the source is
upscaled before the move so slow motion does not shimmer. Deterministic: the same spec and image give the same frames. This replaces the fixed zoom of
`granthstudio.ffmpeg.still_motion_clip` for Tier 0 shots that carry a `camera` (R3, owner-approved D-012).
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

EASES = ("smooth", "linear", "hold")
UPSCALE = 4          # source width = 4 x output width before zoompan: zoompan rounds its window to whole pixels, this keeps the steps sub-pixel


class SpecError(ValueError):
    pass


def validate(spec: dict) -> dict:
    for key in ("image", "duration_s", "size", "camera"):
        if key not in spec:
            raise SpecError(f"motion spec lacks '{key}'")
    width, height = spec["size"]
    if not (isinstance(width, int) and isinstance(height, int) and width >= 64 and height >= 64 and width % 2 == 0 and height % 2 == 0):
        raise SpecError("size must be two even integers >= 64")
    duration, fps = spec["duration_s"], spec.get("fps", 24)
    if not (isinstance(duration, (int, float)) and not isinstance(duration, bool) and 0 < duration <= 120):
        raise SpecError("duration_s must be a number in (0, 120]")
    if not (isinstance(fps, int) and not isinstance(fps, bool) and 1 <= fps <= 60):
        raise SpecError("fps must be an integer 1-60")
    if math.ceil(duration * fps - 1e-6) < 1:
        raise SpecError("duration_s is shorter than one frame")
    camera = spec["camera"]
    if camera.get("ease", "smooth") not in EASES:
        raise SpecError(f"ease must be one of {EASES}")
    for end in ("start", "end"):
        point = camera.get(end)
        if not point:
            raise SpecError(f"camera.{end} is missing")
        zoom, cx, cy = point.get("zoom", 1.0), point.get("cx", 0.5), point.get("cy", 0.5)
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in (zoom, cx, cy)):
            raise SpecError(f"camera.{end} zoom, cx and cy must be numbers")
        if not (1.0 <= zoom <= 3.0):
            raise SpecError(f"camera.{end}.zoom must be 1.0-3.0 (below 1 would show outside the image)")
        if not (0.5 / zoom - 1e-9 <= cx <= 1 - 0.5 / zoom + 1e-9 and 0.5 / zoom - 1e-9 <= cy <= 1 - 0.5 / zoom + 1e-9):
            raise SpecError(f"camera.{end} window leaves the image: at zoom {zoom} cx and cy must lie in [{0.5 / zoom:.4f}, {1 - 0.5 / zoom:.4f}]")
    if camera.get("ease", "smooth") == "hold" and camera["start"] != camera["end"]:
        raise SpecError("ease 'hold' needs identical start and end")
    return spec


def validate_camera(camera: object) -> dict:
    """Check just a manifest shot's `camera` block (the picture, size and duration come from the pipeline)."""
    if not isinstance(camera, dict):
        raise SpecError("camera must be an object with start, end and optional ease")
    unknown = set(camera) - {"start", "end", "ease"}
    if unknown:
        raise SpecError(f"unknown camera keys {sorted(unknown)}")
    validate({"image": "x", "duration_s": 1, "size": [64, 64], "camera": camera})
    return camera


def frame_count(spec: dict) -> int:
    return math.ceil(spec["duration_s"] * spec.get("fps", 24) - 1e-6)


def window(spec: dict, frame: int) -> tuple[float, float, float]:
    """(zoom, cx, cy) of the camera at `frame`, in plain Python (the same maths as the FFmpeg expression; used by tests and by the review report)."""
    camera, n = spec["camera"], frame_count(spec)
    p = frame / (n - 1) if n > 1 else 0.0
    ease = camera.get("ease", "smooth")
    e = 0.0 if ease == "hold" else p if ease == "linear" else p * p * (3 - 2 * p)
    s, t = camera["start"], camera["end"]
    zoom = s.get("zoom", 1.0) + (t.get("zoom", 1.0) - s.get("zoom", 1.0)) * e
    cx = s.get("cx", 0.5) + (t.get("cx", 0.5) - s.get("cx", 0.5)) * e
    cy = s.get("cy", 0.5) + (t.get("cy", 0.5) - s.get("cy", 0.5)) * e
    return zoom, min(max(cx, 0.5 / zoom), 1 - 0.5 / zoom), min(max(cy, 0.5 / zoom), 1 - 0.5 / zoom)


def video_filter(spec: dict) -> str:
    width, height = spec["size"]
    fps, n = spec.get("fps", 24), frame_count(spec)
    camera = spec["camera"]
    s, t = camera["start"], camera["end"]
    ease = camera.get("ease", "smooth")
    p = f"(on/{max(n - 1, 1)})"
    e = "0" if ease == "hold" else p if ease == "linear" else f"({p}*{p}*(3-2*{p}))"
    z0, z1 = s.get("zoom", 1.0), t.get("zoom", 1.0)
    x0, x1, y0, y1 = s.get("cx", 0.5), t.get("cx", 0.5), s.get("cy", 0.5), t.get("cy", 0.5)
    zoom = f"{z0:.6f}+({z1 - z0:.6f})*{e}"
    x = f"max(0,min(iw-iw/zoom,({x0:.6f}+({x1 - x0:.6f})*{e})*iw-iw/zoom/2))"
    y = f"max(0,min(ih-ih/zoom,({y0:.6f}+({y1 - y0:.6f})*{e})*ih-ih/zoom/2))"
    aspect = f"{width}/{height}"
    return (f"crop='min(iw,ih*{aspect})':'min(ih,iw/({aspect}))',scale={width * UPSCALE}:{height * UPSCALE}:flags=lanczos,"
            f"zoompan=z='{zoom}':x='{x}':y='{y}':d={n}:s={width}x{height}:fps={fps},format=yuv420p")


def render(spec: dict, out: Path, base: Path | None = None) -> Path:
    validate(spec)
    image = Path(spec["image"])
    if not image.is_absolute() and base is not None:
        image = (base / image).resolve()
        if not image.is_relative_to(base.resolve()):
            raise SpecError("a relative image path must stay inside the spec's folder (absolute paths are for the owner's own scripts)")
    if not image.is_file():
        raise SpecError(f"image {image} does not exist")
    n, fps = frame_count(spec), spec.get("fps", 24)
    command = ["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(image), "-vf", video_filter(spec), "-frames:v", str(n), "-an",
               "-c:v", "libx264", "-threads", "1", "-pix_fmt", "yuv420p", "-r", str(fps), str(out)]
    done = subprocess.run(command, capture_output=True, text=True)
    if done.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {done.stderr[-400:]}")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("render", help="render one motion spec to an MP4")
    one.add_argument("spec", type=Path)
    one.add_argument("out", type=Path)
    args = parser.parse_args(argv)
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    render(spec, args.out, base=args.spec.parent)
    print(args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
