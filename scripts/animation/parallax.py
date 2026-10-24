"""2.5D parallax for a painted still: the same exact camera path as motion.py plus a depth-based sideways shift while the picture itself is never regenerated.
The shift is a rotation about a fixation plane at depth 0.5: content nearer than that plane slides one way, content farther slides the other way, in proportion
to its distance from the plane (a camera that orbits slightly around the subject). Depth 1 (nearest) and depth 0 (farthest) therefore move equally and
oppositely; only the SIGN says near from far. Host script (needs torch, numpy, Pillow and the Depth-Anything-V2-Small model through
transformers): it is NOT part of the granthstudio package and adds no package dependency (D-006).

  python scripts/animation/parallax.py render SPEC.json OUT.mp4 [--depth-cache DIR]

The spec is the motion.py spec plus  "parallax": {"start": -0.008, "end": 0.004}  (fractions of the image width, both within +-0.02: more shows stretched
edges). The shift ramps from start to end over the shot with the camera's easing. Neighbouring shots of one scene must use the previous shot's end as their start
or the picture jumps at the cut. `{"amplitude": a}` is shorthand for start -a/2, end +a/2. Depth is estimated once per image and cached as .npy next to a sha256 of
the image so a re-render is deterministic and offline.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load_motion():
    spec = importlib.util.spec_from_file_location("motion", ROOT / "scripts" / "animation" / "motion.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["motion"] = module
    spec.loader.exec_module(module)
    return module


motion = _load_motion()
MAX_AMPLITUDE = 0.02
DEPTH_MODEL = "depth-anything/Depth-Anything-V2-Small-hf"


def ends(spec: dict) -> tuple[float, float]:
    block = spec.get("parallax", {})
    if "amplitude" in block:
        return -block["amplitude"] / 2, block["amplitude"] / 2
    return block.get("start", 0.0), block.get("end", 0.0)


def validate(spec: dict) -> dict:
    motion.validate(spec)
    block = spec.get("parallax", {})
    unknown = set(block) - {"amplitude", "start", "end"}
    if unknown or ("amplitude" in block and ("start" in block or "end" in block)):
        raise motion.SpecError("parallax takes either amplitude or start/end, nothing else")
    for key in block:
        value = block[key]
        low = 0 if key == "amplitude" else -MAX_AMPLITUDE
        if not (isinstance(value, (int, float)) and not isinstance(value, bool) and low <= value <= MAX_AMPLITUDE):
            raise motion.SpecError(f"parallax.{key} must be a number in {low}..{MAX_AMPLITUDE} (the amplitude limit)")
    if spec["camera"].get("ease", "smooth") == "hold" and ends(spec)[0] != ends(spec)[1]:
        raise motion.SpecError("parallax start and end must be equal when the camera ease is 'hold' (a held shot has no ramp: the end would never be reached)")
    return spec


def shift_at(spec: dict, frame: int) -> float:
    """Sideways parallax shift (fraction of the width) at `frame`: start -> end with the camera easing."""
    n = motion.frame_count(spec)
    p = frame / (n - 1) if n > 1 else 0.0
    ease = spec["camera"].get("ease", "smooth")
    e = 0.0 if ease == "hold" else p if ease == "linear" else p * p * (3 - 2 * p)
    start, end = ends(spec)
    return start + (end - start) * e


def estimate_depth(image_path: Path, cache: Path | None):
    """Normalised depth map in [0, 1] (1 = nearest), cached by image hash."""
    import numpy as np
    from PIL import Image
    digest = hashlib.sha256(image_path.read_bytes()).hexdigest()[:16]
    cached = (cache / f"{image_path.stem}_{digest}_depth.npy") if cache else None
    if cached and cached.is_file():
        return np.load(cached)
    from transformers import pipeline
    result = pipeline("depth-estimation", model=DEPTH_MODEL, device=-1)(Image.open(image_path).convert("RGB"))
    depth = np.asarray(result["predicted_depth"].squeeze().cpu().numpy() if hasattr(result["predicted_depth"], "cpu") else result["predicted_depth"], dtype="float32")
    low, high = np.percentile(depth, [2, 98])
    depth = np.clip((depth - low) / max(high - low, 1e-6), 0, 1).astype("float32")
    if cached:
        cache.mkdir(parents=True, exist_ok=True)
        np.save(cached, depth)
    return depth


def render(spec: dict, out: Path, base: Path | None = None, cache: Path | None = None) -> Path:
    validate(spec)
    image_path = Path(spec["image"])
    if not image_path.is_absolute() and base is not None:
        image_path = (base / image_path).resolve()
        if not image_path.is_relative_to(base.resolve()):
            raise motion.SpecError("a relative image path must stay inside the spec's folder (absolute paths are for the owner's own scripts)")
    if not image_path.is_file():
        raise motion.SpecError(f"image {image_path} does not exist")
    import numpy as np
    import torch
    import torch.nn.functional as F
    from PIL import Image
    width, height = spec["size"]
    fps, n = spec.get("fps", 24), motion.frame_count(spec)
    image = Image.open(image_path).convert("RGB")
    iw, ih = image.size
    target = width / height                                                                        # crop to the output aspect, centred (as motion.py does)
    cw, ch = (iw, round(iw / target)) if iw / ih <= target else (round(ih * target), ih)
    left, top = (iw - cw) // 2, (ih - ch) // 2
    image = image.crop((left, top, left + cw, top + ch))
    depth = F.interpolate(torch.from_numpy(estimate_depth(image_path, cache))[None, None], size=(ih, iw), mode="bilinear", align_corners=False)[0, 0].numpy()
    depth = torch.from_numpy(depth[top:top + ch, left:left + cw].copy())[None, None]
    depth = F.avg_pool2d(depth, 9, stride=1, padding=4)                                            # smooth the map: no speckle in the displacement
    source = torch.from_numpy(np.asarray(image, dtype="float32") / 255.0).permute(2, 0, 1)[None]
    ys, xs = torch.meshgrid(torch.linspace(-1, 1, height), torch.linspace(-1, 1, width), indexing="ij")
    command = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{width}x{height}", "-r", str(fps), "-i", "-", "-an",
               "-c:v", "libx264", "-threads", "1", "-pix_fmt", "yuv420p", str(out)]
    proc = subprocess.Popen(command, stdin=subprocess.PIPE)
    try:
        for frame in range(n):
            zoom, cx, cy = motion.window(spec, frame)
            gx, gy = 2 * cx - 1 + xs / zoom, 2 * cy - 1 + ys / zoom
            near = F.grid_sample(depth, torch.stack([gx, gy], -1)[None], mode="bilinear", padding_mode="border", align_corners=True)[0, 0]
            gx = gx + shift_at(spec, frame) * 2 * (near - 0.5) * 2                                  # x2: grid units are [-1, 1]; x2: near/far spread -1..+1
            frame_rgb = F.grid_sample(source, torch.stack([gx, gy], -1)[None], mode="bilinear", padding_mode="border", align_corners=True)[0]
            proc.stdin.write((frame_rgb.clamp(0, 1) * 255).round().byte().permute(1, 2, 0).numpy().tobytes())
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed while encoding the parallax frames")
    finally:
        if proc.poll() is None:
            proc.kill()
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("render")
    one.add_argument("spec", type=Path)
    one.add_argument("out", type=Path)
    one.add_argument("--depth-cache", type=Path)
    args = parser.parse_args(argv)
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    render(spec, args.out, base=args.spec.parent, cache=args.depth_cache)
    print(args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
