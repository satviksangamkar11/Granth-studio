"""Episode pipeline: bundle loading, the frozen stage plan (section 8), hard gates.

Stage order: audio, keyframe, tier0, tier1, tier2, assembly. Audio (IndicF5 / IndicTrans2) and
keyframes (SDXL) are NOT VALIDATED adapters: they refuse to run and never report success.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .canon import Canon, load_canon
from .comfy import ComfyBackend, collect_outputs, ensure_validated, load_template, render_graph
from .config import Project, require_capability
from .episodes import compile_episode
from .errors import GateFailure, IntegrationUnavailable, TaskFailed
from .ffmpeg import assemble, still_motion_clip, validate_video
from .integrity import atomic_write_bytes, sha256_bytes, sha256_file, sha256_obj
from .qa import GateResult, gate
from .research import load_research, require_approved, verify_source
from .scheduler import STAGE_ORDER, RunFn, Scheduler, Task, TaskResult
from .timelines import check_timelines, load_timeline, srt_text

VOICE_VERSION = "voice-adapter-not-validated-v0"
KEYFRAME_VERSION = "keyframe-adapter-not-validated-v0"
TIER0_VERSION = "ffmpeg-zoompan-v1"
ASSEMBLY_VERSION = "ffmpeg-concat-libx264-v1"
MAX_ATTEMPTS = 3  # frozen section 9: one attempt plus two retries for video
FPS = 24
LANGUAGE_NAME = {"mr": "marathi", "hi": "hindi"}


@dataclass(frozen=True)
class Bundle:
    project: Project
    models: dict[str, Any]
    adhyay: int
    canon: Canon
    research: dict[str, Any]
    compiled: dict[str, Any]
    timelines: dict[str, dict[str, Any]]


def load_bundle(project: Project, models: dict[str, Any], adhyay: int) -> Bundle:
    canon = load_canon(project)
    research = load_research(project, adhyay)
    receipt = require_approved(project, adhyay)
    compiled = compile_episode(project, models, canon, adhyay, research, receipt)
    timelines = {lang: load_timeline(project, adhyay, lang) for lang in ("mr", "hi")}
    problems = check_timelines(canon, compiled, research, timelines["mr"], timelines["hi"])
    if problems:
        raise GateFailure("timeline gate failed: " + "; ".join(problems))
    return Bundle(project, models, adhyay, canon, research, compiled, timelines)


def episode_store(project: Project, adhyay: int) -> Path:
    return project.artifacts_dir / "tasks" / f"adhyay_{adhyay:02d}"


def _not_validated(component: str) -> RunFn:
    def run(_workdir: Path) -> dict[str, str]:
        raise IntegrationUnavailable(f"{component} is NOT VALIDATED on this machine: no output produced")

    return run


def _visual_file(bundle: Bundle, visual: dict[str, Any]) -> Path:
    if visual["source"] != "file":
        raise TaskFailed(f"{visual['visual_id']} comes from the keyframe stage, which is NOT VALIDATED")
    path = bundle.project.artifacts_dir / "visuals" / visual["path"]
    if not path.is_file():
        raise TaskFailed(f"visual missing: {path}")
    if sha256_file(path) != visual["sha256"]:
        raise TaskFailed(f"visual changed since the manifest was compiled: {visual['visual_id']}")
    return path


def _seed(shot_id: str) -> int:
    return int(sha256_bytes(shot_id.encode("utf-8"))[:8], 16) % (2**31)


def _tier0_run(bundle: Bundle, shot: dict[str, Any], visual: dict[str, Any]) -> RunFn:
    def run(workdir: Path) -> dict[str, str]:
        image = _visual_file(bundle, visual)
        clip = workdir / "clip.mp4"
        still_motion_clip(image, clip, shot["duration_s"], fps=FPS)
        problems = validate_video(clip, shot["duration_s"], tolerance_s=0.1)
        if problems:
            raise TaskFailed("; ".join(problems))
        return {"clip": "clip.mp4"}

    return run


def _ltx_run(bundle: Bundle, shot: dict[str, Any], visual: dict[str, Any], capability: str) -> RunFn:
    template_rel = bundle.models["ltx"]["workflow_templates"][capability]
    visuals = {v["visual_id"]: v for v in bundle.compiled["visuals"]}

    def run(workdir: Path) -> dict[str, str]:
        require_capability(bundle.models, capability, bundle.project.benchmarks_dir)
        template = load_template(bundle.project.root / template_rel)
        ensure_validated(template)
        values = {
            "START_IMAGE": str(_visual_file(bundle, visual)),
            "MOTION_PROMPT": shot["motion_prompt"],
            "FRAMES": str(shot["frames"]),
            "SEED": str(_seed(shot["shot_id"])),
            "FPS": str(FPS),
        }
        if capability == "flf":
            values["END_IMAGE"] = str(_visual_file(bundle, visuals[shot["end_visual_id"]]))
        backend = ComfyBackend(bundle.models["comfyui"]["base_url"])
        outputs = collect_outputs(backend.wait(backend.submit(render_graph(template, values))))
        if not outputs:
            raise TaskFailed("ComfyUI returned no output files")
        clip = workdir / "clip.mp4"
        backend.fetch(outputs[0], clip)
        problems = validate_video(clip, shot["frames"] / FPS, tolerance_s=0.1)
        if problems:
            raise TaskFailed("; ".join(problems))
        return {"clip": "clip.mp4"}

    return run


def _assembly_run(bundle: Bundle, lang: str, shot_tasks: dict[str, Task], audio_task: Task, scheduler: Scheduler) -> RunFn:
    timeline = bundle.timelines[lang]
    stem = f"adhyay_{bundle.adhyay:02d}_{LANGUAGE_NAME[lang]}"
    total = sum(shot["duration_s"] for shot in bundle.compiled["shots"])

    def run(workdir: Path) -> dict[str, str]:
        clips = []
        for shot in bundle.compiled["shots"]:
            clip = scheduler.task_dir(shot_tasks[shot["shot_id"]]) / "clip.mp4"
            if not clip.is_file():
                raise TaskFailed(f"clip missing for {shot['shot_id']}")
            clips.append(clip)
        audio = scheduler.task_dir(audio_task) / "voice.wav"
        if not audio.is_file():
            raise TaskFailed(f"voice track missing for {lang}")
        subtitles = workdir / f"{stem}.srt"
        atomic_write_bytes(subtitles, srt_text(timeline["entries"]).encode("utf-8"))
        video = workdir / f"{stem}.mp4"
        assemble(clips, video, audio)
        problems = validate_video(video, total, tolerance_s=0.25)
        if problems:
            raise TaskFailed("; ".join(problems))
        return {"video": video.name, "subtitles": subtitles.name}

    return run


def plan_tasks(bundle: Bundle, scheduler: Scheduler) -> list[Task]:
    compiled = bundle.compiled
    visuals = {v["visual_id"]: v for v in compiled["visuals"]}
    tasks: list[Task] = []

    audio: dict[str, Task] = {}
    for lang in ("mr", "hi"):
        audio[lang] = Task(
            "audio",
            f"{lang}_voice",
            {"language": lang, "timeline": sha256_obj(bundle.timelines[lang]["entries"])},
            VOICE_VERSION,
            _not_validated("IndicF5 voice / IndicTrans2 adapter"),
        )
        tasks.append(audio[lang])

    keyframes: dict[str, Task] = {}
    for vid, visual in sorted(visuals.items()):
        if visual["source"] == "keyframe":
            keyframes[vid] = Task(
                "keyframe",
                f"keyframe_{vid}",
                {"visual_id": vid, "episode": compiled["episode_id"]},
                KEYFRAME_VERSION,
                _not_validated("SDXL keyframe adapter"),
            )
            tasks.append(keyframes[vid])

    shot_tasks: dict[str, Task] = {}
    for shot in compiled["shots"]:
        visual = visuals[shot["visual_id"]]
        deps = [keyframes[visual["visual_id"]].task_id()] if visual["source"] == "keyframe" else []
        inputs = {
            "shot_id": shot["shot_id"],
            "visual": visual["sha256"] or f"keyframe:{visual['visual_id']}",
            "duration_s": repr(shot["duration_s"]),
            "frames": str(shot["frames"] or 0),
            "motion_prompt": shot["motion_prompt"],
        }
        if shot["tier"] == 0:
            stage, run, version = "tier0", _tier0_run(bundle, shot, visual), TIER0_VERSION
        else:
            capability = "i2v" if shot["tier"] == 1 else "flf"
            template = load_template(bundle.project.root / bundle.models["ltx"]["workflow_templates"][capability])
            stage, run, version = ("tier1" if shot["tier"] == 1 else "tier2"), _ltx_run(bundle, shot, visual, capability), template.version
            if shot["tier"] == 2:
                end = visuals[shot["end_visual_id"]]
                inputs["end"] = end["sha256"] or f"keyframe:{end['visual_id']}"
                if end["source"] == "keyframe":
                    deps.append(keyframes[end["visual_id"]].task_id())
        task = Task(stage, shot["shot_id"], inputs, version, run, depends_on=tuple(deps), max_attempts=MAX_ATTEMPTS)
        shot_tasks[shot["shot_id"]] = task
        tasks.append(task)

    for lang in ("mr", "hi"):
        deps = (audio[lang].task_id(), *(t.task_id() for t in shot_tasks.values()))
        tasks.append(
            Task(
                "assembly",
                f"assemble_{lang}",
                {
                    "language": lang,
                    "shots": sha256_obj([s["shot_id"] for s in compiled["shots"]]),
                    "timeline": sha256_obj(bundle.timelines[lang]["entries"]),
                },
                ASSEMBLY_VERSION,
                _assembly_run(bundle, lang, shot_tasks, audio[lang], scheduler),
                depends_on=deps,
                max_attempts=1,
            )
        )
    tasks.sort(key=lambda t: STAGE_ORDER.index(t.stage))
    return tasks


def hard_gates(bundle: Bundle, results: list[TaskResult]) -> list[GateResult]:
    status = verify_source(bundle.project, bundle.adhyay)
    source_problems = [] if status.approved and not status.changed else ["research not approved or changed since approval"]
    failing = [f"{r.name}: {r.status}" for r in results if r.status not in ("complete", "resumed")]
    decode = [
        f"{r.name}: {r.status}"
        for r in results
        if r.stage in ("tier0", "tier1", "tier2", "assembly") and r.status not in ("complete", "resumed")
    ]
    return [
        gate("source_integrity", source_problems),
        gate("canon_identity", []),  # every reference is approved: enforced by compile_episode in load_bundle
        gate("marathi_lock", []),  # Marathi equals approved research: enforced by check_timelines in load_bundle
        gate("hindi_terms", []),  # speakers, numbers, protected terms: enforced by check_timelines in load_bundle
        gate("task_outputs", failing),
        gate("video_decode", decode),
    ]
