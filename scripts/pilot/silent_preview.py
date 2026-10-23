"""Silent preview of the provisional 45-second pilot: the three scenes' shots in plan order and timing, WITHOUT narration audio.

  python scripts/pilot/silent_preview.py --ltx 1=PATH 2=PATH 3=PATH --out DIR

Per scene: shot 1 and shot 3 are Tier 0 stills (the existing ffmpeg.still_motion_clip slow zoom) of the approved style-anchor keyframe, shot 2 is the LTX
clip rendered from the same keyframe. Every shot is conformed to one 3:2 size (1152x768, 24 fps) before the existing ffmpeg.assemble joins them: the
pipeline's LTX clips are 768x512 while its Tier 0 default is 1280x720, so the production assembly still has to solve this (recorded in the preview report).
Marathi and Hindi subtitle files (.srt) use the PLANNED shot timings, because no narration audio exists yet (IndicF5 waits for the narrator's recording and
consent). The Hindi lines are the assistant's drafts (review PENDING). Nothing here is a release; human review NOT_DONE.
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
sys.path.insert(0, str(ROOT / "src"))

from granthstudio.ffmpeg import assemble, probe, still_motion_clip  # noqa: E402

SIZE = (1152, 768)
FPS = 24
KEYFRAMES = ROOT / "docs" / "evidence" / "sdxl_scenes" / "style_anchor_16d48472"
CROPS = {1: "scale=1267:-2:flags=lanczos,crop=1216:810:0:0",                  # the same reframing as the scene 1 LTX start image (pseudo-signature outside)
         2: "crop=1216:810:0:11", 3: "crop=1216:810:0:11"}                      # centre 3:2 crop of the 1216x832 keyframe


def _load_builder():
    spec = importlib.util.spec_from_file_location("build_pilot_project", ROOT / "scripts" / "pilot" / "build_pilot_project.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["build_pilot_project"] = module
    spec.loader.exec_module(module)
    return module


def ffmpeg(*args: str) -> None:
    subprocess.run(["ffmpeg", "-y", "-v", "error", *args], check=True)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def srt_time(seconds: float) -> str:
    ms = round(seconds * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ltx", nargs=3, required=True, metavar="N=PATH", help="the LTX clip of each scene, e.g. 1=clip_gpu0.mp4")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    ltx = {int(k): Path(v) for k, v in (item.split("=", 1) for item in args.ltx)}
    if sorted(ltx) != [1, 2, 3] or not all(p.is_file() for p in ltx.values()):
        parser.error("--ltx needs 1=, 2= and 3= with existing files")
    bp = _load_builder()
    manifest, timelines = bp.manifest(), bp.timelines()
    out = args.out
    work = out / "work"
    work.mkdir(parents=True, exist_ok=True)
    clips, report, cues = [], {"size": list(SIZE), "fps": FPS, "audio": None, "shots": []}, {"mr": [], "hi": []}
    texts = {lang: {e["dialogue_id"]: e["text"] for e in timelines[lang]["entries"]} for lang in ("mr", "hi")}
    cursor = 0.0
    for n, scene in enumerate(manifest["scenes"], start=1):
        keyframe = KEYFRAMES / f"scene{n}_keyframe.png"
        still = work / f"scene{n}_still_3x2.png"
        ffmpeg("-i", str(keyframe), "-vf", CROPS[n], "-frames:v", "1", str(still))
        for shot in scene["shots"]:
            clip = work / f"{shot['shot_id']}.mp4"
            if shot["tier"] == 0:
                still_motion_clip(still, clip, shot["duration_s"], fps=FPS, size=SIZE)
                source = {"kind": "tier0_still_motion", "image": str(keyframe.relative_to(ROOT)), "image_sha256": sha256(keyframe)}
            else:
                ffmpeg("-i", str(ltx[n]), "-vf", f"scale={SIZE[0]}:{SIZE[1]}:flags=lanczos,fps={FPS},format=yuv420p", "-an",
                       "-c:v", "libx264", "-threads", "1", str(clip))
                source = {"kind": "ltx_i2v", "clip": str(ltx[n]), "clip_sha256": sha256(ltx[n])}
            info = probe(clip)
            duration = info.video_duration_s if info.video_duration_s is not None else info.duration_s
            for lang in ("mr", "hi"):
                for line in shot["dialogue_ids"]:
                    cues[lang].append((cursor, cursor + duration, texts[lang][line]))
            report["shots"].append({"shot_id": shot["shot_id"], "start_s": round(cursor, 3), "duration_s": round(duration, 3),
                                    "planned_duration_s": shot["duration_s"], **source})
            clips.append(clip)
            cursor += duration
    video = out / "pilot_silent_preview.mp4"
    assemble(clips, video)
    for lang, items in cues.items():
        (out / f"pilot_silent_preview.{lang}.srt").write_text(
            "".join(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{text}\n\n" for i, (a, b, text) in enumerate(items, start=1)), encoding="utf-8")
    info = probe(video)
    report.update(video=video.name, video_sha256=sha256(video), duration_s=info.duration_s, width=info.width, height=info.height,
                  note="SILENT PREVIEW of a provisional technical test: no narration audio (IndicF5 waits for the narrator's recording and consent); "
                       "subtitles use planned shot timings; Hindi lines are drafts (review PENDING); human review NOT_DONE.")
    (out / "preview_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("video", "duration_s", "width", "height")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
