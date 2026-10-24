"""Silent preview of the pilot made ONLY with the code-driven motion toolkit (no AI video): each shot is a camera move over the approved keyframe, and the
three shots of a scene continue one camera path (the end of one shot is the start of the next), so there is no jump cut.

  python scripts/pilot/render_motion_preview.py --out DIR

Camera plans are in PLANS below (fractions of the image, see scripts/animation/motion.py). Marathi and Hindi subtitle files use the planned shot timings;
no narration exists yet; the Hindi lines are drafts (review PENDING). Provisional technical test; human review NOT_DONE.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from granthstudio.ffmpeg import assemble, probe  # noqa: E402

SIZE, FPS = [1152, 768], 24
KEYFRAMES = ROOT / "docs" / "evidence" / "sdxl_scenes" / "style_anchor_16d48472"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


motion = _load("motion", ROOT / "scripts" / "animation" / "motion.py")
bp = _load("build_pilot_project", ROOT / "scripts" / "pilot" / "build_pilot_project.py")


def pt(zoom: float, cx: float, cy: float) -> dict:
    return {"zoom": zoom, "cx": cx, "cy": cy}


# One continuous camera path per scene, split over its three shots. Scene 1 stays zoomed top-left so the pseudo-signature SDXL drew in the bottom-right
# corner is never in frame (the frozen style forbids text and signatures).
PLANS = {
    1: [(pt(1.12, 0.447, 0.447), pt(1.20, 0.46, 0.46)), (pt(1.20, 0.46, 0.46), pt(1.55, 0.42, 0.40)), (pt(1.55, 0.42, 0.40), pt(1.12, 0.447, 0.447))],
    2: [(pt(1.0, 0.5, 0.5), pt(1.30, 0.40, 0.58)), (pt(1.30, 0.40, 0.58), pt(1.60, 0.38, 0.60)), (pt(1.60, 0.38, 0.60), pt(1.0, 0.5, 0.5))],
    3: [(pt(1.0, 0.5, 0.5), pt(1.15, 0.5, 0.55)), (pt(1.15, 0.5, 0.55), pt(1.50, 0.5, 0.58)), (pt(1.50, 0.5, 0.58), pt(1.0, 0.5, 0.5))],
}


def srt_time(seconds: float) -> str:
    ms = round(seconds * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    out = args.out
    (out / "specs").mkdir(parents=True, exist_ok=True)
    manifest, timelines = bp.manifest(), bp.timelines()
    texts = {lang: {e["dialogue_id"]: e["text"] for e in timelines[lang]["entries"]} for lang in ("mr", "hi")}
    clips, report, cues, cursor = [], {"size": SIZE, "fps": FPS, "audio": None, "shots": []}, {"mr": [], "hi": []}, 0.0
    for n, scene in enumerate(manifest["scenes"], start=1):
        keyframe = KEYFRAMES / f"scene{n}_keyframe.png"
        for shot, (start, end) in zip(scene["shots"], PLANS[n]):
            spec = {"image": str(keyframe), "duration_s": shot["duration_s"], "fps": FPS, "size": SIZE, "camera": {"start": start, "end": end, "ease": "smooth"}}
            (out / "specs" / f"{shot['shot_id']}.json").write_text(json.dumps(spec, indent=2), encoding="utf-8")
            clip = out / f"{shot['shot_id']}.mp4"
            motion.render(spec, clip)
            info = probe(clip)
            duration = info.video_duration_s if info.video_duration_s is not None else info.duration_s
            for lang in cues:
                cues[lang] += [(cursor, cursor + duration, texts[lang][line]) for line in shot["dialogue_ids"]]
            report["shots"].append({"shot_id": shot["shot_id"], "start_s": round(cursor, 3), "duration_s": round(duration, 3), "camera": spec["camera"],
                                    "image": str(keyframe.relative_to(ROOT)), "image_sha256": hashlib.sha256(keyframe.read_bytes()).hexdigest()})
            clips.append(clip)
            cursor += duration
    video = out / "pilot_code_motion_preview.mp4"
    assemble(clips, video)
    for lang, items in cues.items():
        (out / f"pilot_code_motion_preview.{lang}.srt").write_text(
            "".join(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{text}\n\n" for i, (a, b, text) in enumerate(items, start=1)), encoding="utf-8")
    info = probe(video)
    report.update(video=video.name, video_sha256=hashlib.sha256(video.read_bytes()).hexdigest(), duration_s=info.duration_s, width=info.width, height=info.height,
                  note="SILENT PREVIEW, code-driven camera motion only (no AI video, no figure animation yet): provisional technical test; no narration; Hindi lines are "
                       "drafts (review PENDING); human review NOT_DONE.")
    (out / "preview_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("video", "duration_s", "width", "height")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
