"""Optional lip-sync renders (frozen sections 10 and 13), NOT VALIDATED until a human validates a runner.

Essential visible-speech close-ups may get SEPARATE Marathi and Hindi renders. A task runs only when the
``lipsync`` runner is validated AND was validated for the style that is approved right now. Otherwise the task
is refused (not_validated), produces nothing, and the language assembly stays blocked: the shared clip is never
substituted silently.
"""
from __future__ import annotations

from typing import Any

from .errors import IntegrationUnavailable, TaskFailed
from .ffmpeg import assemble_audio, probe, validate_video
from .integrity import contained_path, read_json, sha256_obj
from .keyframes import _style, load_registry
from .runners import require_runner, run_json
from .scheduler import Task

LIPSYNC_VERSION = "lipsync-runner-not-validated-v0"
CLIP = "lipsync.mp4"
TOLERANCE_S = 1 / 24


def style_identity(style: dict[str, Any] | None) -> dict[str, Any]:
    """Version and content digest of the approved style: what a lip-sync validation is bound to."""
    if style is None:
        return {"style_id": None, "version": None, "sha256": None}
    content = {k: style.get(k) for k in ("style_id", "version", "prompt_prefix", "negative_prompt")}
    return {"style_id": style["style_id"], "version": style["version"], "sha256": sha256_obj(content)}


def usable_runner(bundle) -> dict[str, Any]:
    """The lipsync runner section, or IntegrationUnavailable (NOT VALIDATED) naming what is missing."""
    section = require_runner(bundle.models, "lipsync", "Lip-sync runner")
    style = _style(load_registry(bundle.project, bundle.canon))
    if style is None:
        raise IntegrationUnavailable("lip-sync needs an approved style in canon/visual_assets.yaml: NOT VALIDATED")
    validated = section.get("validated_style_id")
    if validated is None:
        raise IntegrationUnavailable("lip-sync validated_style_id is not set: NOT VALIDATED")
    if validated != style["style_id"]:
        raise IntegrationUnavailable(f"lip-sync runner was validated for style {validated}, "
                                     f"but the approved style is {style['style_id']}: NOT VALIDATED")
    now = style_identity(style)
    bound = (section.get("validated_style_version"), section.get("validated_style_sha256"))
    if bound[1] is None or bound[0] is None:
        raise IntegrationUnavailable("lip-sync validated_style_version/validated_style_sha256 are not set: NOT VALIDATED")
    if bound != (now["version"], now["sha256"]):
        raise IntegrationUnavailable(
            f"lip-sync runner was validated for style {validated} v{bound[0]} ({str(bound[1])[:12]}), but the approved style "
            f"is v{now['version']} ({now['sha256'][:12]}): NOT VALIDATED")
    return section


def _run(bundle, scheduler, shot, lang, shot_task, audio_task):
    def run(work):
        section = usable_runner(bundle)
        audio_dir = scheduler.task_dir(audio_task)
        timings = read_json(audio_dir / "timings.json")
        segments = [(contained_path(audio_dir, timings[line]["path"]), timings[line]["duration_s"])
                    for line in shot["dialogue_ids"]]
        assemble_audio(segments, work / "audio.wav")
        run_json(section, {"video_path": str(scheduler.task_dir(shot_task) / "clip.mp4"),
                           "audio_path": str(work / "audio.wav"), "language": lang, "out_path": str(work / CLIP)})
        if not (work / CLIP).is_file():
            raise TaskFailed(f"{shot['shot_id']}: lip-sync runner wrote no video")
        return {"clip": CLIP, "audio": "audio.wav"}
    return run


def _verify(scheduler, shot_task, directory):
    info = probe(scheduler.task_dir(shot_task) / "clip.mp4")
    shared = info.video_duration_s if info.video_duration_s is not None else info.duration_s
    problems = validate_video(directory / CLIP, shared, tolerance_s=TOLERANCE_S)
    if problems:
        raise TaskFailed("; ".join(problems))


def plan_lipsync(bundle, scheduler, audio, shot_tasks, require_current) -> dict[str, dict[str, Any]]:
    """{language: {shot_id: Task}} for every shot that declares lip_sync for that language."""
    plan: dict[str, dict[str, Any]] = {"mr": {}, "hi": {}}
    section_hash = sha256_obj(bundle.models.get("lipsync"))
    style = style_identity(_style(load_registry(bundle.project, bundle.canon)))
    for shot in bundle.compiled["shots"]:
        declared = shot.get("lip_sync")
        for lang in (declared["languages"] if declared else ()):
            shot_task = shot_tasks[shot["shot_id"]]
            task = Task("lipsync", f"lipsync_{lang}_{shot['shot_id']}",
                        {"language": lang, "shot": sha256_obj(shot), "lipsync_model": section_hash,
                         "style": sha256_obj(style)},
                        LIPSYNC_VERSION, _run(bundle, scheduler, shot, lang, shot_task, audio[lang]),
                        depends_on=(shot_task.task_id(), audio[lang].task_id()), max_attempts=1,
                        preflight=lambda: (require_current(bundle), usable_runner(bundle)),
                        verify=lambda directory, shot_task=shot_task: _verify(scheduler, shot_task, directory))
            plan[lang][shot["shot_id"]] = task
    return plan
