"""Retrospective, hash-bound OFFLINE validation of a Kaggle GPU stage's evidence directory (no GPU, no regeneration).

  python scripts/kaggle/offline_validate_gpu_evidence.py EVIDENCE_DIR --clip FILE --receipt FILE --journal FILE --attribution FILE [--out FILE]

It never edits or overrides the original verdict: the report restates it and records what this separate check could and could not confirm.
Checks: the clip decodes completely; size / frame count / fps match the receipt's requested configuration; the picture is not flat or frozen (luma statistics);
the journal shows exactly one completed submission with a sampler seed on the generation path; the per-card attribution file is ok; hashes of every input are recorded.
Human visual review, crash recovery, retry and dual-worker behaviour are NOT covered and are reported as not validated.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


MAX_STEP_DIFFERENCE = 40.0      # mean absolute luma change between consecutive frames (0-255 scale); a smooth I2V clip stays far below it


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def luma_stats(clip: Path) -> list[tuple[float, float]]:
    """Per-frame (YAVG, YDIF) from ffmpeg signalstats."""
    text = subprocess.run(["ffmpeg", "-v", "error", "-i", str(clip), "-vf", "signalstats,metadata=print:file=-", "-an", "-f", "null", "-"],
                          capture_output=True, text=True, timeout=300, check=True).stdout
    yavg = [float(v) for v in re.findall(r"lavfi\.signalstats\.YAVG=([0-9.]+)", text)]
    ydif = [float(v) for v in re.findall(r"lavfi\.signalstats\.YDIF=([0-9.]+)", text)]
    return list(zip(yavg, ydif or [0.0] * len(yavg)))


def probe(clip: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                          "stream=codec_name,width,height,r_frame_rate,nb_read_frames,pix_fmt,duration", "-of", "json", str(clip)],
                         capture_output=True, text=True, timeout=120, check=True).stdout
    return json.loads(out)["streams"][0]


def validate(clip: Path, receipt: dict, journal: dict, attribution: dict) -> tuple[list[str], dict]:
    problems: list[str] = []
    decode = subprocess.run(["ffmpeg", "-v", "error", "-xerror", "-i", str(clip), "-map", "0:v?", "-map", "0:a?", "-f", "null", "-"], capture_output=True, text=True)
    if decode.returncode != 0:
        problems.append(f"clip does not decode cleanly: {decode.stderr[:200]}")
    stream = probe(clip)
    wanted = receipt["inputs"]
    num, den = (int(x) for x in stream["r_frame_rate"].split("/"))
    if (int(stream["width"]), int(stream["height"])) != (wanted["width"], wanted["height"]):
        problems.append(f"size {stream['width']}x{stream['height']} != requested {wanted['width']}x{wanted['height']}")
    if int(stream["nb_read_frames"]) != wanted["frames"]:
        problems.append(f"{stream['nb_read_frames']} frames != requested {wanted['frames']}")
    if num / den != wanted["fps"]:
        problems.append(f"fps {num}/{den} != requested {wanted['fps']}")
    if (wanted["frames"] - 1) % 8 != 0 or wanted["width"] % 32 or wanted["height"] % 32:
        problems.append("requested configuration violates the 8n+1 / multiple-of-32 rule")
    stats = luma_stats(clip)
    if len(stats) != int(stream["nb_read_frames"]):
        problems.append("luma statistics do not cover every frame")
    spread = (max(y for y, _ in stats) - min(y for y, _ in stats)) if stats else 0.0
    motion = max((d for _, d in stats), default=0.0)
    if stats and (max(y for y, _ in stats) < 2 or motion < 0.05):
        problems.append(f"clip looks flat or frozen (luma spread {spread:.2f}, max frame difference {motion:.3f})")
    if stats and motion > MAX_STEP_DIFFERENCE:
        worst = max(range(len(stats)), key=lambda i: stats[i][1])
        problems.append(f"picture discontinuity: frame {worst} differs from frame {worst - 1} by a mean luma step of {motion:.1f} (> {MAX_STEP_DIFFERENCE}); "
                        "an image-to-video clip should continue its start image, so this needs human visual review before anything is concluded")
    history = journal.get("history", [])
    if journal.get("state") != "completed" or journal.get("attempt") != 1 or len(history) != 1:
        problems.append(f"journal is not one completed submission (state {journal.get('state')}, attempt {journal.get('attempt')}, {len(history)} record(s))")
    elif not history[0].get("seed_inputs"):
        problems.append("journal records no sampler seed on the generation path")
    if not attribution.get("ok"):
        problems.append(f"per-card attribution file is not ok: {attribution.get('problems')}")
    facts = {"codec": stream["codec_name"], "pix_fmt": stream["pix_fmt"], "width": stream["width"], "height": stream["height"], "frames": int(stream["nb_read_frames"]),
             "fps": f"{num}/{den}", "duration_s": float(stream["duration"]), "luma_spread": round(spread, 3), "max_frame_difference": round(motion, 3),
             "journal_state": journal.get("state"), "attempt": journal.get("attempt"), "prompt_id": journal.get("prompt_id")}
    return problems, facts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("evidence", type=Path)
    for name in ("clip", "receipt", "journal", "attribution"):
        parser.add_argument(f"--{name}", required=True, type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    inputs = {"clip": args.clip, "receipt": args.receipt, "journal": args.journal, "attribution": args.attribution}
    if args.out is not None and (args.out.resolve() in {path.resolve() for path in inputs.values()}
                                 or (args.out.exists() and any(args.out.samefile(path) for path in inputs.values()))):
        parser.error(f"--out {args.out} is one of the evidence inputs: the original evidence is never overwritten")
    receipt, journal, attribution = (json.loads(p.read_text(encoding="utf-8")) for p in (args.receipt, args.journal, args.attribution))
    problems, facts = validate(args.clip, receipt, journal, attribution)
    report = {"kind": "offline_retrospective_validation", "validated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "original_harness_verdict": receipt.get("verdict"), "original_harness_reason": receipt.get("reason"),
              "original_verdict_unchanged": True, "offline_checks_ok": not problems, "problems": problems, "facts": facts,
              "bound_inputs": {role: {"path": str(path), "sha256": sha256(path)} for role, path in inputs.items()},
              "not_covered": ["human visual / semantic review (none done)", "crash recovery and interrupted-submission behaviour", "fresh retry execution",
                              "dual-worker concurrent operation", "visual quality: the start image may not be carried into the later frames (see problems)", "that the harness itself would accept this output (needs a fresh run with the post-run fix)"]}
    if args.out:
        args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
