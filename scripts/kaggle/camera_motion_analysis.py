"""Separate OFFLINE analysis of a generated clip: is a low frame-to-frame similarity camera movement or real content drift?

  python scripts/kaggle/camera_motion_analysis.py CLIP --out-dir DIR [--frames 12 24 36 48] [--input-image PNG] [--json FILE]

For frames 12, 24, 36, 48 (default) against frame 0 it estimates a similarity transform (scale, rotation, translation) from ORB feature matches with RANSAC, warps the frame
back onto frame 0, and reports the raw SSIM and the motion-compensated SSIM (over the area both frames cover). An alignment that is not backed by enough consistent matches is
marked INCONCLUSIVE and its compensated score is not used. Verdict per frame: CAMERA_MOTION (a real scale/shift and the compensated score recovers), CONTENT_DRIFT (aligned but
still dissimilar), STATIC (no motion, similar), INCONCLUSIVE. It never edits receipts or verdicts: it writes its own report and example images, and it is evidence for a human.

Developer tool for CPU analysis of saved evidence: needs numpy, opencv-python and scikit-image, which are NOT GranthStudio runtime dependencies.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

MIN_INLIERS, MIN_INLIER_RATIO = 25, 0.35
MOTION_SCALE, MOTION_SHIFT = 0.04, 0.03             # 4 % scale change or a 3 % of the width shift counts as camera movement
RECOVERED_SSIM, DRIFT_SSIM = 0.55, 0.40


def _libs():
    try:
        import cv2
        import numpy
        from skimage.metrics import structural_similarity
    except ImportError as exc:                       # pragma: no cover - environment dependent
        raise SystemExit(f"camera_motion_analysis needs numpy, opencv-python and scikit-image ({exc})")
    return cv2, numpy, structural_similarity


def read_frames(cv2, clip: Path, wanted: list[int]) -> dict[int, "numpy.ndarray"]:
    capture = cv2.VideoCapture(str(clip))
    frames, index = {}, 0
    while True:
        ok, frame = capture.read()
        if not ok or index > max(wanted):
            break
        if index in wanted:
            frames[index] = frame
        index += 1
    capture.release()
    missing = [n for n in wanted if n not in frames]
    if missing:
        raise SystemExit(f"{clip} has no frames {missing}")
    return frames


def estimate(cv2, np, reference, frame) -> dict:
    """Similarity transform mapping FRAME onto REFERENCE coordinates, or an unreliable result."""
    gray = lambda image: cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    orb = cv2.ORB_create(nfeatures=3000)
    ka, da = orb.detectAndCompute(gray(reference), None)
    kb, db = orb.detectAndCompute(gray(frame), None)
    if da is None or db is None or len(ka) < MIN_INLIERS or len(kb) < MIN_INLIERS:
        return {"reliable": False, "reason": "too few features"}
    matches = sorted(cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(db, da), key=lambda m: m.distance)[:600]
    if len(matches) < MIN_INLIERS:
        return {"reliable": False, "reason": f"only {len(matches)} matches"}
    src = np.float32([kb[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst = np.float32([ka[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
    matrix, mask = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=3.0)
    if matrix is None:
        return {"reliable": False, "reason": "no consistent transform"}
    inliers = int(mask.sum())
    scale = float(np.hypot(matrix[0, 0], matrix[1, 0]))
    rotation = float(np.degrees(np.arctan2(matrix[1, 0], matrix[0, 0])))
    height, width = reference.shape[:2]
    shift = (float(matrix[0, 2]), float(matrix[1, 2]))
    return {"reliable": inliers >= MIN_INLIERS and inliers / len(matches) >= MIN_INLIER_RATIO, "inliers": inliers, "matches": len(matches),
            "inlier_ratio": round(inliers / len(matches), 3), "scale_frame_to_reference": round(scale, 4), "rotation_deg": round(rotation, 3),
            "shift_px": [round(shift[0], 1), round(shift[1], 1)], "shift_fraction_of_width": [round(shift[0] / width, 4), round(shift[1] / height, 4)],
            "matrix": matrix.tolist()}


def compensated(cv2, np, ssim, reference, frame, estimate_: dict) -> dict:
    """SSIM between the reference and the frame warped onto it, averaged ONLY over pixels whose whole SSIM window lies inside the area the warped frame really covers."""
    matrix = np.float32(estimate_["matrix"])
    height, width = reference.shape[:2]
    warped = cv2.warpAffine(frame, matrix, (width, height), flags=cv2.INTER_LINEAR, borderValue=0)
    coverage = cv2.warpAffine(np.full(frame.shape[:2], 255, np.uint8), matrix, (width, height), flags=cv2.INTER_NEAREST, borderValue=0) > 0
    rows, cols = np.where(coverage)
    if len(rows) < 0.2 * height * width:
        return {"warped": warped, "ssim": None, "covered_fraction": round(float(coverage.mean()), 3)}
    r0, r1, c0, c1 = rows.min(), rows.max() + 1, cols.min(), cols.max() + 1
    gray = lambda image: cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    a, b = gray(reference)[r0:r1, c0:c1], gray(warped)[r0:r1, c0:c1]
    window = 7
    if min(a.shape) < window:                          # a crop narrower than the SSIM window cannot be scored
        return {"warped": warped, "ssim": None, "covered_fraction": round(float(coverage.mean()), 3)}
    _, ssim_map = ssim(a, b, data_range=255, full=True)
    window = 7                                         # skimage's default window: a pixel counts only if its whole window is covered (no black corners leak in)
    inside = cv2.erode(coverage[r0:r1, c0:c1].astype(np.uint8), np.ones((window, window), np.uint8), borderValue=0) > 0
    if not inside.any():
        return {"warped": warped, "ssim": None, "covered_fraction": round(float(coverage.mean()), 3)}
    return {"warped": warped, "ssim": round(float(ssim_map[inside].mean()), 4), "covered_fraction": round(float(coverage.mean()), 3)}


def verdict(raw: float, est: dict, comp: float | None) -> str:
    if not est.get("reliable") or comp is None:
        return "INCONCLUSIVE"
    moved = abs(est["scale_frame_to_reference"] - 1) > MOTION_SCALE or max(abs(v) for v in est["shift_fraction_of_width"]) > MOTION_SHIFT
    if comp < DRIFT_SSIM:
        return "CONTENT_DRIFT"
    if moved and comp >= RECOVERED_SSIM and comp - raw >= 0.1:
        return "CAMERA_MOTION"
    return "STATIC" if not moved and comp >= RECOVERED_SSIM else "INCONCLUSIVE"


def analyse(clip: Path, out_dir: Path, frames: list[int], input_image: Path | None = None) -> dict:
    cv2, np, ssim = _libs()
    out_dir.mkdir(parents=True, exist_ok=True)
    wanted = sorted({0, *frames})
    video = read_frames(cv2, clip, wanted)
    reference = video[0]
    gray = lambda image: cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    report: dict = {"kind": "offline_camera_motion_analysis", "clip": str(clip), "clip_sha256": hashlib.sha256(clip.read_bytes()).hexdigest(),
                    "thresholds": {"min_inliers": MIN_INLIERS, "min_inlier_ratio": MIN_INLIER_RATIO, "motion_scale": MOTION_SCALE, "motion_shift_fraction": MOTION_SHIFT,
                                   "recovered_ssim": RECOVERED_SSIM, "drift_ssim": DRIFT_SSIM},
                    "original_harness_verdict_untouched": True, "frames": {}}
    if input_image is not None:
        source = cv2.imread(str(input_image))
        resized = cv2.resize(source, (reference.shape[1], reference.shape[0]), interpolation=cv2.INTER_AREA)
        report["frame_0_vs_input_ssim"] = round(float(ssim(gray(reference), gray(resized), data_range=255)), 4)
    for n in frames:
        frame = video[n]
        raw = round(float(ssim(gray(reference), gray(frame), data_range=255)), 4)
        est = estimate(cv2, np, reference, frame)
        entry = {"raw_ssim_vs_frame_0": raw, "alignment": {k: v for k, v in est.items() if k != "matrix"}, "motion_compensated_ssim": None, "covered_fraction": None}
        if "matrix" in est:
            comp = compensated(cv2, np, ssim, reference, frame, est)
            if est.get("reliable"):
                entry["motion_compensated_ssim"], entry["covered_fraction"] = comp["ssim"], comp["covered_fraction"]
            else:                                    # shown for a human, never used in the verdict
                entry["unreliable_alignment_compensated_ssim_NOT_USED"] = comp["ssim"]
            diff = cv2.absdiff(reference, comp["warped"])
            sheet = np.hstack([reference, frame, comp["warped"], diff])
            suffix = "" if est.get("reliable") else "_UNRELIABLE_ALIGNMENT"
            cv2.imwrite(str(out_dir / f"aligned_frame_{n:02d}{suffix}.png"), cv2.resize(sheet, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA))
        entry["verdict"] = verdict(raw, est, entry["motion_compensated_ssim"])
        report["frames"][str(n)] = entry
    verdicts = [e["verdict"] for e in report["frames"].values()]
    report["summary"] = ("INCONCLUSIVE" if "INCONCLUSIVE" in verdicts and verdicts.count("INCONCLUSIVE") == len(verdicts) else
                         "CONTENT_DRIFT" if "CONTENT_DRIFT" in verdicts else "CAMERA_MOTION" if "CAMERA_MOTION" in verdicts else "STATIC"
                         if set(verdicts) == {"STATIC"} else "MIXED_OR_INCONCLUSIVE")
    report["note"] = ("Camera movement is estimated from background feature matches with one global similarity transform; a moving subject or parallax from a real push-in makes the "
                      "compensated score a lower bound. Visual examples: aligned_frame_NN.png = reference | frame | warped frame | absolute difference. Human review is still required.")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("clip", type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--frames", type=int, nargs="+", default=[12, 24, 36, 48])
    parser.add_argument("--input-image", type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args(argv)
    if args.json is not None and args.json.resolve() == args.clip.resolve():
        parser.error("--json would overwrite the clip")
    if args.json is not None and args.json.exists():       # only this tool's own earlier report may be replaced: never a receipt, journal or any other evidence file
        try:
            previous = json.loads(args.json.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            previous = None
        if not (isinstance(previous, dict) and previous.get("kind") == "offline_camera_motion_analysis"):
            parser.error(f"--json {args.json} exists and is not an earlier camera_motion_analysis report: the original evidence is never overwritten")
    report = analyse(args.clip, args.out_dir, args.frames, args.input_image)
    text = json.dumps(report, indent=2)
    if args.json:
        args.json.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
