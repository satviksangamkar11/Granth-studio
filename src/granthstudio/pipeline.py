"""File-driven stage batches with source-bound inputs and independent language edits.

Imported, reviewed speech is supported for CPU integration. Model generation remains
explicitly NOT VALIDATED. No production authorization is created by this module.
"""
from __future__ import annotations

import json
import math
import os
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .canon import Canon, load_canon
from .comfy import (ComfyBackend, check_checkpoint_binding, ensure_validated, execution_seconds, load_template,
                    render_graph, select_video)
from .config import Project, load_models, require_capability, verify_benchmark_runtime
from .episodes import compile_episode, trimmed_required_actions, unplaced_required_actions
from .errors import GateFailure, GranthError, IntegrationUnavailable, TaskFailed
from .ffmpeg import assemble, assemble_audio, audio_video_tolerance, hold_clip, probe, still_motion_clip, trim_hold, validate_audio, validate_video
from .lipsync import plan_lipsync
from .keyframes import (approved_keyframe, keyframe_request, load_registry, require_references, sdxl_generate,
                        sdxl_preflight)
from .integrity import (atomic_write_bytes, atomic_write_json, contained_path, normalize_text, read_json, sha256_bytes,
                        sha256_file, sha256_obj)
from .pilot import plan_pilot, score_receipts
from .qa import GateResult, gate
from .research import load_research, require_approved
from .runtime import gpu_status
from .scheduler import RECEIPT, RUN_LOG, STAGE_ORDER, RunFn, Scheduler, Task, TaskResult
from .schemas import validate_document
from .timelines import check_timelines, load_timeline, srt_text

VOICE_VERSION = "reviewed-audio-v2"
KEYFRAME_VERSION = "keyframe-adapter-not-validated-v0"
TIER0_VERSION = "ffmpeg-zoompan-v2"
ASSEMBLY_VERSION = "ffmpeg-language-edits-v3"
MAX_ATTEMPTS = 3
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
    benchmark: bool = False  # pilot only: may run LTX capabilities that are not validated yet

def load_bundle(project: Project, models: dict[str, Any], adhyay: int, benchmark: bool = False) -> Bundle:
    canon = load_canon(project)
    receipt = require_approved(project, adhyay)
    research = load_research(project, adhyay)
    if sha256_file(project.research_dir / f"adhyay_{adhyay:02d}" / "research.yaml") != receipt["research_sha256"]:
        raise GateFailure("research changed while loading")
    compiled = compile_episode(project, models, canon, adhyay, research, receipt)
    timelines = {lang: load_timeline(project, adhyay, lang) for lang in ("mr", "hi")}
    problems = check_timelines(canon, compiled, research, timelines["mr"], timelines["hi"])
    if problems:
        raise GateFailure("timeline gate failed: " + "; ".join(problems))
    return Bundle(project, models, adhyay, canon, research, compiled, timelines, benchmark)

def episode_store(project: Project, adhyay: int) -> Path:
    return project.artifacts_dir / "tasks" / f"adhyay_{adhyay:02d}"

def snapshot(bundle: Bundle) -> dict:
    return {"compiled": sha256_obj(bundle.compiled), "models": sha256_obj(bundle.models),
            "research_sha256": bundle.compiled["research_sha256"], "research_version": bundle.compiled["research_version"],
            "canon_sha256": bundle.canon.digest(),
            "timelines": {lang: sha256_obj(timeline) for lang, timeline in bundle.timelines.items()}}

def require_current(bundle: Bundle) -> None:
    current = load_bundle(bundle.project, load_models(bundle.project), bundle.adhyay, bundle.benchmark)
    if snapshot(current) != snapshot(bundle):
        raise GateFailure("production input snapshot changed; reload and reconcile affected tasks")

def _not_validated(component: str) -> RunFn:
    def run(_workdir):
        raise IntegrationUnavailable(f"{component} is NOT VALIDATED: no output produced")
    return run

def _keyframe_request(bundle, visual_id):
    registry = load_registry(bundle.project, bundle.canon)
    return keyframe_request(bundle.compiled, bundle.canon, registry, bundle.models, visual_id), registry

def _keyframe_preflight(bundle, visual_id):
    request, _ = _keyframe_request(bundle, visual_id)
    sdxl_preflight(bundle.project, bundle.models, request)
    require_references(request, bundle.models)

def _keyframe_run(bundle, visual_id, journal):
    def run(work):
        request, _ = _keyframe_request(bundle, visual_id)
        return sdxl_generate(bundle.project, bundle.models, request, journal, work)
    return run

def _visual_file(bundle, visual):
    if visual["source"] == "keyframe":
        request, registry = _keyframe_request(bundle, visual["visual_id"])
        return approved_keyframe(bundle.project, registry, request)
    path = contained_path(bundle.project.artifacts_dir / "visuals", visual["path"])
    if not path.is_file() or sha256_file(path) != visual["sha256"]:
        raise TaskFailed(f"visual missing or changed: {visual['visual_id']}")
    return path

def _audio_file(bundle, entry):
    item = entry.get("audio")
    if item is None:
        raise IntegrationUnavailable("IndicF5 speech generation is NOT VALIDATED; reviewed imported audio is required")
    path = contained_path(bundle.project.artifacts_dir / "audio", item["path"])
    if not path.is_file() or sha256_file(path) != item["sha256"]:
        raise TaskFailed(f"audio missing or changed: {entry['dialogue_id']}")
    return path

def _audio_run(bundle, lang):
    def run(work):
        files = {}
        timings = {}
        for entry in bundle.timelines[lang]["entries"]:
            source = _audio_file(bundle, entry)
            duration = validate_audio(source)
            name = entry["dialogue_id"] + ".wav"
            shutil.copyfile(source, work / name)
            timings[entry["dialogue_id"]] = {"duration_s": duration, "path": name,
                "sha256": sha256_file(work / name), "language": lang, "speaker": entry["speaker"],
                "text_sha256": entry["audio"]["text_sha256"], "speech_reviewed_by": entry["audio"]["speech_reviewed_by"],
                "provenance": entry["audio"].get("provenance", {"origin": "imported"})}
            files[entry["dialogue_id"]] = name
        atomic_write_json(work / "timings.json", timings)
        files["timings"] = "timings.json"
        return files
    return run

def _verify_audio(bundle, lang, directory):
    timings = read_json(directory / "timings.json")
    expected = {e["dialogue_id"] for e in bundle.timelines[lang]["entries"]}
    if set(timings) != expected:
        raise TaskFailed("audio receipt has missing/extra utterances")
    for entry in bundle.timelines[lang]["entries"]:
        item = timings[entry["dialogue_id"]]
        audio = entry["audio"]
        if (item["language"] != lang or item["speaker"] != entry["speaker"]
                or item["text_sha256"] != audio["text_sha256"] or item["speech_reviewed_by"] != audio["speech_reviewed_by"]):
            raise TaskFailed("audio metadata differs from approved script/review")
        path = contained_path(directory, item["path"])
        if sha256_file(path) != audio["sha256"] or item["sha256"] != audio["sha256"]:
            raise TaskFailed("audio artifact does not match reviewed audio")
        if abs(validate_audio(path) - item["duration_s"]) > 0.001:
            raise TaskFailed("audio duration receipt mismatch")

def _seed(shot_id):
    return int(sha256_bytes(shot_id.encode())[:8], 16) % 2**31

def _tier0_run(bundle, shot, visual):
    def run(work):
        still_motion_clip(_visual_file(bundle, visual), work / "clip.mp4", shot["duration_s"], fps=FPS)
        return {"clip": "clip.mp4"}
    return run

def _reject_flat(project, path, what):
    """Frozen 8 numerical-stability proxy: every frame one flat colour means a failed generation."""
    from .diagnostics import is_degenerate
    from .runtime import load_runtime
    if load_runtime(project)["checks"]["reject_flat_output"] and is_degenerate(path):
        raise TaskFailed(f"{what}: every frame is one flat colour: likely a failed FP16 decode")

def _verify_clip(directory, duration, project=None):
    """``project`` is passed for LTX tasks only; a Tier 0 fallback stand-in is never flat-checked."""
    problems = validate_video(directory / "clip.mp4", duration, tolerance_s=1 / FPS)
    if problems:
        raise TaskFailed("; ".join(problems))
    if project is not None and not (directory / "fallback.json").is_file():
        _reject_flat(project, directory / "clip.mp4", "LTX clip")

def _verify_keyframe(bundle, visual_id, directory):
    request, _ = _keyframe_request(bundle, visual_id)
    stored = read_json(directory / "request.json")
    if stored["request_sha256"] != request["request_sha256"] or stored != request:
        raise TaskFailed(f"keyframe {visual_id}: stored request differs from the current request")
    info = probe(directory / "keyframe.png")
    if (info.width, info.height) != (request["width"], request["height"]):
        raise TaskFailed(f"keyframe {visual_id}: decoded size differs from the request")
    _reject_flat(bundle.project, directory / "keyframe.png", f"keyframe {visual_id}")

def _ltx_preflight(bundle, capability):
    template = load_template(contained_path(bundle.project.root, bundle.models["ltx"]["workflow_templates"][capability]))
    if bundle.benchmark:
        # Frozen section 15: benchmark the pinned runtime to earn validation. Pins, runtime files and the
        # checkpoint binding still apply; only the 'validated' status and receipt requirements are waived.
        verify_benchmark_runtime(bundle.models, capability, template.version)
        graph = json.loads(template.text)
        if not template.output_node or template.output_node not in graph:
            raise IntegrationUnavailable(f"workflow {template.name} has no real graph/_output_node: NOT VALIDATED")
    else:
        require_capability(bundle.models, capability, bundle.project.benchmarks_dir, template.version)
        ensure_validated(template)
    check_checkpoint_binding(template, bundle.models["ltx"]["checkpoint_file"])
    return template

def validate_ltx_inputs(models, shot, image):
    """Interface checks only. The exact LTX 0.9.8 frame/resolution rule is still O-003:
    frames must be in the pinned list, and size/FPS come from the pinned runtime."""
    ltx = models["ltx"]
    if shot["frames"] not in ltx["frame_counts"]:
        raise TaskFailed(f"{shot['shot_id']}: frames {shot['frames']} not in pinned frame_counts")
    runtime = ltx.get("runtime") or {}
    if not runtime.get("width") or not runtime.get("height"):
        raise IntegrationUnavailable("LTX runtime width/height are not pinned: NOT VALIDATED")
    info = probe(image)
    if not info.width or not info.height:
        raise TaskFailed(f"{image.name}: start image is not decodable")
    return {"frames": shot["frames"], "fps": FPS, "width": runtime["width"], "height": runtime["height"],
            "start_image": {"width": info.width, "height": info.height, "sha256": sha256_file(image)},
            "frame_rule": "pinned list only; exact rule open (O-003)"}


def _ltx_run(bundle, shot, visual, capability, journal):
    visuals = {v["visual_id"]: v for v in bundle.compiled["visuals"]}
    def run(work):
        template = _ltx_preflight(bundle, capability)
        start = _visual_file(bundle, visual)
        inputs = validate_ltx_inputs(bundle.models, shot, start)
        values = {"START_IMAGE": str(start), "MOTION_PROMPT": shot["motion_prompt"],
                  "FRAMES": shot["frames"], "SEED": _seed(shot["shot_id"]), "FPS": FPS,
                  "WIDTH": inputs["width"], "HEIGHT": inputs["height"]}
        if capability == "flf":
            values["END_IMAGE"] = str(_visual_file(bundle, visuals[shot["end_visual_id"]]))
        backend = ComfyBackend(bundle.models["comfyui"]["base_url"])
        graph = render_graph(template, values)
        backend.require_nodes(graph)
        backend.require_model_files(graph)
        stats = backend.system_stats()
        peak, gpu_names = [], []
        def sample():
            gpus = gpu_status()
            if gpus:
                peak.append(gpus[0]["memory_used_mb"])
                gpu_names[:] = [gpus[0]["name"]]
        started = time.monotonic()
        history = backend.execute(graph, journal, sample)
        wall = time.monotonic() - started
        backend.fetch(select_video(history, template.output_node), work / "clip.mp4")
        atomic_write_json(work / "metrics.json", {
            "schema_version": 1, "capability": capability, "shot_id": shot["shot_id"],
            "prompt_id": read_json(journal)["prompt_id"], "workflow_version": template.version,
            "checkpoint_sha256": bundle.models["ltx"]["checkpoint_sha256"], "inputs": inputs,
            "runtime_sha256": verify_benchmark_runtime(bundle.models, capability, template.version),
            "gpu": gpu_names[0] if gpu_names else None,
            "execution_s": {"value": execution_seconds(history), "kind": "measured by ComfyUI status messages"},
            "wall_s": {"value": wall, "kind": "measured in this session only (excludes earlier sessions)"},
            "peak_vram_mb": {"value": max(peak) if peak else None,
                             "kind": "sampled with nvidia-smi at each poll; lower bound of the true peak"},
            "gpu_count": 1, "system_stats": stats})
        return {"clip": "clip.mp4", "metrics": "metrics.json"}
    return run

def _assembly_run(bundle, lang, shot_tasks, audio_task, scheduler, lipsync_tasks=None):
    timeline = bundle.timelines[lang]
    stem = f"adhyay_{bundle.adhyay:02d}_{LANGUAGE_NAME[lang]}"
    def run(work):
        audio_dir = scheduler.task_dir(audio_task)
        _verify_audio(bundle, lang, audio_dir)
        timings = read_json(audio_dir / "timings.json")
        entries = {entry["dialogue_id"]: entry for entry in timeline["entries"]}
        clips, segments, cues, edits = [], [], [], []
        cursor = 0.0
        for index, shot in enumerate(bundle.compiled["shots"]):
            if shot["cutaway"]:
                continue  # coverage footage: only placed through another shot's coverage
            lip = (lipsync_tasks or {}).get(shot["shot_id"])  # declared lip-sync for this language: never the shared clip
            clip = scheduler.task_dir(lip) / "lipsync.mp4" if lip else scheduler.task_dir(shot_tasks[shot["shot_id"]]) / "clip.mp4"
            info = probe(clip)
            duration = info.video_duration_s if info.video_duration_s is not None else info.duration_s
            speech = sum(timings[line]["duration_s"] for line in shot["dialogue_ids"])
            span = math.ceil(max(duration, shot["duration_s"], speech) * FPS - 1e-6) / FPS
            cover = shot.get("coverage")
            if span - duration > 1e-6 and not cover:
                if speech > duration:
                    raise GateFailure(f"{shot['shot_id']}: extra speech needs reviewed final-frame coverage")
                raise GateFailure(f"{shot['shot_id']}: rendered clip {duration:.3f}s is shorter than the planned "
                                  f"{shot['duration_s']:.3f}s; reviewed final-frame coverage is required")
            edit = work / f"edit_{index:04d}.mp4"
            extra = span - duration
            if cover and cover["mode"] == "cutaway" and extra > 1e-6:
                cut = scheduler.task_dir(shot_tasks[cover["shot_id"]]) / "clip.mp4"
                trimmed = work / f"cutaway_{index:04d}.mp4"
                trim_hold(cut, trimmed, extra)
                edit_main = work / f"main_{index:04d}.mp4"
                hold_clip(clip, edit_main, duration)
                assemble([edit_main, trimmed], edit)
                coverage = {"mode": "cutaway", "shot_id": cover["shot_id"], "duration_s": extra,
                            "source_sha256": sha256_file(cut),
                            "source_duration_s": (lambda i: i.video_duration_s if i.video_duration_s is not None else i.duration_s)(probe(cut))}
            else:
                hold_clip(clip, edit, span)
                coverage = None
            clips.append(edit)
            offset = 0.0
            for line in shot["dialogue_ids"]:
                item = timings[line]
                segments.append((contained_path(audio_dir, item["path"]), item["duration_s"]))
                cues.append({**entries[line], "start_s": cursor + offset, "measured_duration_s": item["duration_s"]})
                offset += item["duration_s"]
            if span - offset > 0.000001:
                segments.append((None, span - offset))
            marker = clip.parent / "fallback.json"  # absent in a lip-sync task directory
            edits.append({"shot_id": shot["shot_id"], "start_s": cursor, "duration_s": span,
                          "source_sha256": sha256_file(clip), "primary_action_duration_s": duration,
                          **({"coverage": coverage} if coverage else {}),
                          "clip_source": "lipsync" if lip else "fallback_tier0" if marker.is_file() else "rendered",
                          **({"fallback": read_json(marker)} if marker.is_file() else {})})
            cursor += span
        missing = unplaced_required_actions(bundle.compiled, {e["coverage"]["shot_id"] for e in edits if "coverage" in e})
        if missing:
            raise GateFailure(f"required approved actions absent from the rendered plan: {missing}")
        trimmed = trimmed_required_actions(bundle.compiled, [e["coverage"] for e in edits if "coverage" in e])
        if trimmed:
            raise GateFailure("cutaway trimming could remove required approved actions: " + "; ".join(trimmed))
        assemble_audio(segments, work / "voice.wav")
        atomic_write_bytes(work / f"{stem}.srt", srt_text(cues).encode("utf-8"))
        assemble(clips, work / f"{stem}.mp4", work / "voice.wav")
        atomic_write_json(work / "edit_plan.json", {"language": lang, "duration_s": cursor, "shots": edits, "cues": cues})
        atomic_write_json(work / "provenance.json", {
            "schema_version": 1, "language": lang, "adhyay": bundle.adhyay,
            "research_sha256": bundle.compiled["research_sha256"],
            "video_sha256": sha256_file(work / f"{stem}.mp4"), "subtitles_sha256": sha256_file(work / f"{stem}.srt"),
            "voice_sha256": sha256_file(work / "voice.wav"), "edit_plan_sha256": sha256_file(work / "edit_plan.json"),
            "fallback_shots": [e["shot_id"] for e in edits if e["clip_source"] == "fallback_tier0"],
            "lipsync_shots": [e["shot_id"] for e in edits if e["clip_source"] == "lipsync"],
            "lines": [{"dialogue_id": line, "text_sha256": sha256_obj(normalize_text(entries[line]["text"])),
                       "audio_sha256": timings[line]["sha256"], "audio": timings[line]["provenance"],
                       "translation": entries[line].get("alignment", {}).get("source")}
                      for shot in bundle.compiled["shots"] for line in shot["dialogue_ids"]]})
        return {"video": f"{stem}.mp4", "subtitles": f"{stem}.srt", "edit_plan": "edit_plan.json", "voice": "voice.wav",
                "provenance": "provenance.json"}
    return run

def _verify_assembly(bundle, lang, directory):
    stem = f"adhyay_{bundle.adhyay:02d}_{LANGUAGE_NAME[lang]}"
    plan = read_json(directory / "edit_plan.json")
    if plan["language"] != lang or [s["shot_id"] for s in plan["shots"]] != [s["shot_id"] for s in bundle.compiled["shots"] if not s["cutaway"]]:
        raise TaskFailed("editorial plan omits/reorders required shots")
    missing = unplaced_required_actions(bundle.compiled, {s["coverage"]["shot_id"] for s in plan["shots"] if "coverage" in s})
    if missing:
        raise TaskFailed(f"required approved actions absent from the editorial plan: {missing}")
    trimmed = trimmed_required_actions(bundle.compiled, [s["coverage"] for s in plan["shots"] if "coverage" in s])
    if trimmed:
        raise TaskFailed("cutaway trimming could remove required approved actions: " + "; ".join(trimmed))
    duration = plan["duration_s"]
    if not math.isfinite(duration) or duration <= 0:
        raise TaskFailed("invalid editorial duration")
    if abs(validate_audio(directory / "voice.wav") - duration) > audio_video_tolerance(probe(directory / "voice.wav")):
        raise TaskFailed("voice duration differs from editorial timeline")
    if (directory / f"{stem}.srt").read_text(encoding="utf-8") != srt_text(plan["cues"]):
        raise TaskFailed("subtitles differ from measured cue placements")
    expected_entries = bundle.timelines[lang]["entries"]
    if len(plan["cues"]) != len(expected_entries):
        raise TaskFailed("editorial cues omit approved dialogue")
    for cue, entry in zip(plan["cues"], expected_entries):
        if any(cue[key] != entry[key] for key in ("dialogue_id", "shot_id", "speaker", "text")):
            raise TaskFailed("editorial cue differs from approved script")
    if plan["cues"] and max(c["start_s"] + c["measured_duration_s"] for c in plan["cues"]) > duration + 0.001:
        raise TaskFailed("speech/subtitles extend past release")
    problems = validate_video(directory / f"{stem}.mp4", duration, tolerance_s=1 / FPS, require_audio=True)
    if problems:
        raise TaskFailed("; ".join(problems))

def plan_tasks(bundle: Bundle, scheduler: Scheduler) -> list[Task]:
    compiled = bundle.compiled
    visuals = {v["visual_id"]: v for v in compiled["visuals"]}
    tasks, audio, keyframes, shot_tasks = [], {}, {}, {}
    for lang in ("mr", "hi"):
        def audio_preflight(lang=lang):
            require_current(bundle)
            for entry in bundle.timelines[lang]["entries"]:
                _audio_file(bundle, entry)
        audio[lang] = Task("audio", f"{lang}_voice", {"language": lang,
            "timeline": sha256_obj(bundle.timelines[lang]), "source": compiled["research_sha256"]},
            VOICE_VERSION, _audio_run(bundle, lang), preflight=audio_preflight,
            verify=lambda directory, lang=lang: _verify_audio(bundle, lang, directory))
        tasks.append(audio[lang])
    requests = {vid: _keyframe_request(bundle, vid)[0] for vid, v in visuals.items() if v["source"] == "keyframe"}
    derived = lambda vid: (requests[vid].get("derived_from") or {}).get("kind") == "keyframe"
    for vid, visual in sorted(visuals.items(), key=lambda kv: (kv[0] in requests and derived(kv[0]), kv[0])):
        if visual["source"] == "keyframe":
            request = requests[vid]
            keyframes[vid] = Task("keyframe", f"keyframe_{vid}", {"visual": sha256_obj(visual),
                "source": compiled["research_sha256"], "canon": compiled["canon_sha256"],
                "request": request["request_sha256"], "sdxl": sha256_obj(bundle.models.get("sdxl"))},
                KEYFRAME_VERSION, lambda work: {}, max_attempts=1,
                depends_on=(keyframes[request["derived_from"]["visual_id"]].task_id(),) if derived(vid) else (),
                preflight=lambda vid=vid: (require_current(bundle), _keyframe_preflight(bundle, vid)),
                verify=lambda directory, vid=vid: _verify_keyframe(bundle, vid, directory))
            keyframes[vid].journal = scheduler.store / "pending" / f"{keyframes[vid].task_id()}.json"
            keyframes[vid].run = _keyframe_run(bundle, vid, keyframes[vid].journal)
            tasks.append(keyframes[vid])
    for shot in compiled["shots"]:
        visual = visuals[shot["visual_id"]]
        deps = [keyframes[visual["visual_id"]].task_id()] if visual["source"] == "keyframe" else []
        relevant_ids = [*shot["characters"], shot["location"], *shot["props"]]
        inputs = {"shot": sha256_obj(shot), "visual": sha256_obj(visual),
                  "source": sha256_obj(shot["research_scene"]),
                  "canon": sha256_obj({key: bundle.canon.entries[key] for key in relevant_ids})}
        capability = None
        if shot["tier"] == 0:
            stage, version, run = "tier0", TIER0_VERSION, _tier0_run(bundle, shot, visual)
            duration = shot["duration_s"]
        else:
            capability = "i2v" if shot["tier"] == 1 else "flf"
            template = load_template(contained_path(bundle.project.root, bundle.models["ltx"]["workflow_templates"][capability]))
            stage, version, run = ("tier1" if capability == "i2v" else "tier2"), template.version, _not_validated("pending LTX task")
            duration = shot["frames"] / FPS
            inputs["model"] = sha256_obj(bundle.models["ltx"])
            inputs["server"] = bundle.models["comfyui"]["base_url"]
            if shot["tier"] == 2:
                end = visuals[shot["end_visual_id"]]
                inputs["end"] = sha256_obj(end)
                if end["source"] == "keyframe":
                    deps.append(keyframes[end["visual_id"]].task_id())
        def preflight(shot=shot, visual=visual, capability=capability):
            require_current(bundle)
            if capability:
                _ltx_preflight(bundle, capability)
            _visual_file(bundle, visual)
            if shot["tier"] == 2:
                _visual_file(bundle, visuals[shot["end_visual_id"]])
        if shot.get("fallback"):
            inputs["fallback"] = sha256_obj(shot["fallback"])
        task = Task(stage, shot["shot_id"], inputs, version, run, depends_on=tuple(deps), max_attempts=MAX_ATTEMPTS,
                    preflight=preflight, verify=lambda directory, duration=duration, ltx=bool(capability): _verify_clip(
                        directory, duration, bundle.project if ltx else None))
        if shot.get("fallback"):  # frozen 9: Tier 0 stand-in, only after real failed renders, recorded in the receipt
            task.fallback = _tier0_run(bundle, {**shot, "duration_s": duration}, visual)
            task.fallback_info = {"mode": "tier0", "shot_id": shot["shot_id"], **shot["fallback"]}
        if capability:
            task.journal = scheduler.store / "pending" / f"{task.task_id()}.json"
            task.run = _ltx_run(bundle, shot, visual, capability, task.journal)
        shot_tasks[shot["shot_id"]] = task
        tasks.append(task)
    lipsync_tasks = plan_lipsync(bundle, scheduler, audio, shot_tasks, require_current)
    tasks += [t for per_lang in lipsync_tasks.values() for t in per_lang.values()]
    for lang in ("mr", "hi"):
        deps = (audio[lang].task_id(), *(t.task_id() for t in shot_tasks.values()), *(t.task_id() for t in lipsync_tasks[lang].values()))
        task = Task("assembly", f"assemble_{lang}", {"language": lang, "timeline": sha256_obj(bundle.timelines[lang]),
                    "edit_rules": sha256_obj([{k: s[k] for k in ("shot_id", "duration_s", "dialogue_ids", "coverage")} for s in compiled["shots"]])},
                    ASSEMBLY_VERSION, _assembly_run(bundle, lang, shot_tasks, audio[lang], scheduler, lipsync_tasks[lang]),
                    depends_on=deps, preflight=lambda: require_current(bundle),
                    verify=lambda directory, lang=lang: _verify_assembly(bundle, lang, directory))
        tasks.append(task)
    tasks.sort(key=lambda t: STAGE_ORDER.index(t.stage))
    return tasks

def _recovery_provenance(root, output, name, record):
    """A recovery output must be a sealed scheduler output: <store>/<stage>/<task_id>/<file>."""
    task_dir = output.parent
    store = task_dir.parent.parent
    if not store.is_relative_to(root.resolve()) or store == root.resolve():
        raise GateFailure(f"recovery output {name} must sit in a scheduler store under artifacts")
    try:
        receipt = read_json(task_dir / RECEIPT)
        validate_document("task_receipt", receipt)
    except (GranthError, OSError, ValueError) as exc:
        raise GateFailure(f"recovery output {name} has no valid scheduler task receipt") from exc
    listed = any(item["path"] == output.name and item["sha256"] == record["sha256"] for item in receipt["outputs"].values())
    if (not listed or receipt["status"] != "complete" or receipt["task_id"] != task_dir.name
            or receipt["stage"] != task_dir.parent.name):
        raise GateFailure(f"recovery output {name} is not recorded by its task receipt")
    language = name.removesuffix("_video")
    if name.endswith("_video") and (receipt["stage"], receipt["name"]) != ("assembly", f"assemble_{language}"):
        raise GateFailure(f"recovery output {name} is not the assemble_{language} release")
    return store, receipt["task_id"]

def check_recovery_evidence(artifacts_dir, evidence, pilot_sha256):
    """Recovery proof must be two distinct real scheduler runs with identical outputs (D4/M1).
    Raises GateFailure; shared by production approval and the recovery-evidence builder."""
    validate_document("recovery_evidence", evidence)
    if evidence["pilot_plan_sha256"] != pilot_sha256:
        raise GateFailure("recovery evidence belongs to another pilot plan")
    clean, resumed = evidence["clean_outputs"], evidence["resumed_outputs"]
    if set(clean) != set(resumed):
        raise GateFailure("clean/resumed recovery output sets differ")
    records = [(run, name, outputs[name]) for run, outputs in (("clean", clean), ("resumed", resumed))
               for name in sorted(outputs)]
    seen, paths = {}, {}
    for run, name, record in records:
        output = contained_path(artifacts_dir, record["path"])
        if sha256_file(output) != record["sha256"]:
            raise GateFailure(f"recovery output hash mismatch: {name}")
        # One file cannot prove two runs or two languages: reject same path
        # (case-insensitive on Windows) and same file identity (hard links).
        info = output.stat()
        keys = [os.path.normcase(str(output))] + ([(info.st_dev, info.st_ino)] if info.st_ino else [])
        for key in keys:
            if key in seen:
                raise GateFailure(f"recovery outputs alias one file: {seen[key]} and {run}.{name}")
            seen[key] = f"{run}.{name}"
        paths[run, name] = output
    stores, task_ids = {}, {}
    for run, name, record in records:
        store, task_ids[run, name] = _recovery_provenance(artifacts_dir, paths[run, name], name, record)
        stores.setdefault(run, set()).add(os.path.normcase(str(store)))
    if len(stores["clean"]) != 1 or len(stores["resumed"]) != 1:
        raise GateFailure("each recovery run must come from a single scheduler store")
    if stores["clean"] == stores["resumed"]:
        raise GateFailure("clean and resumed recovery outputs must come from different scheduler stores")
    for run, must_resume in (("clean", False), ("resumed", True)):
        log = Path(next(iter(stores[run]))) / RUN_LOG
        statuses = [json.loads(line)["status"] for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]
        if ("resumed" in statuses) != must_resume:
            raise GateFailure("resumed recovery store has no resumed task in its run log" if must_resume
                              else "clean recovery store reused earlier work; it is not a clean run")
    for name in sorted(clean):
        if task_ids["clean", name] != task_ids["resumed", name]:
            raise GateFailure(f"clean/resumed recovery outputs come from different tasks: {name}")
        if clean[name]["sha256"] != resumed[name]["sha256"]:
            raise GateFailure(f"clean/resumed recovery hashes differ: {name}")

def production_problems(bundle):
    """Read authorization evidence. Never create or infer human approval."""
    path = bundle.project.root / "approvals" / f"adhyay_{bundle.adhyay:02d}.json"
    if not path.is_file():
        return ["no human production GO for this input snapshot"]
    try:
        approval = read_json(path)
        validate_document("production_approval", approval)
        required = {"schema_version", "adhyay", "approved", "reviewed_by", "input_sha256", "pilot_receipts", "recovery_evidence", "minimum_accepted_sec_per_gpu_hour", "pilot_plan", "flf_decision"}
        if set(approval) != required or approval["schema_version"] != 1 or approval["adhyay"] != bundle.adhyay:
            raise GateFailure("invalid production approval contract")
        if approval["approved"] is not True or not str(approval["reviewed_by"]).strip():
            raise GateFailure("production GO not approved")
        if approval["input_sha256"] != sha256_obj(snapshot(bundle)):
            raise GateFailure("production GO is stale for current inputs")
        pilot = approval["pilot_plan"]
        pilot_path = contained_path(bundle.project.benchmarks_dir, pilot["path"])
        if sha256_file(pilot_path) != pilot["sha256"]:
            raise GateFailure("pilot plan changed after human approval")
        pilot_plan = read_json(pilot_path)
        if pilot_plan.get("adhyay") != 1:
            raise GateFailure("approved pilot chapter must be Adhyay 1")
        plan_pilot(pilot_plan)
        if bundle.adhyay == 1:
            current_pilot = bundle.compiled
        else:
            current_pilot = load_bundle(bundle.project, bundle.models, 1).compiled
        if sha256_obj(pilot_plan) != sha256_obj(current_pilot):
            raise GateFailure("approved pilot plan differs from the current compiled pilot manifest")
        if approval["flf_decision"] not in ("go", "no_go"):
            raise GateFailure("a separate human FLF GO/NO-GO is required")
        if approval["flf_decision"] == "no_go":
            if bundle.models["ltx"]["capabilities"]["flf"] != "disabled" or any(s["tier"] == 2 for s in bundle.compiled["shots"]):
                raise GateFailure("FLF NO-GO requires disabled FLF and no production Tier 2 shots")
        receipts = []
        expected_capabilities = dict(zip("ABCDEF", ("tier0", "i2v", "flf", "i2v", "i2v", "assembly")))
        for item in approval["pilot_receipts"]:
            path = contained_path(bundle.project.benchmarks_dir, item["path"])
            if sha256_file(path) != item["sha256"]:
                raise GateFailure("pilot evidence changed")
            receipt = read_json(path)
            if receipt["capability"] != expected_capabilities.get(receipt["shot"]):
                raise GateFailure("pilot label/capability mismatch")
            if receipt.get("pilot_plan_sha256") != pilot["sha256"]:
                raise GateFailure("pilot receipt does not match approved pilot plan")
            rejected_flf = receipt["shot"] == "C" and approval["flf_decision"] == "no_go"
            if rejected_flf:
                if receipt["accepted"] is not False or receipt["outcome"] != "fail":
                    raise GateFailure("FLF NO-GO needs recorded failed/rejected C evidence")
            elif receipt["accepted"] is not True or receipt["outcome"] != "pass":
                raise GateFailure("pilot not accepted")
            if receipt["capability"] in ("i2v", "flf") and not rejected_flf:
                template = _ltx_preflight(bundle, receipt["capability"])
                passing = require_capability(bundle.models, receipt["capability"], bundle.project.benchmarks_dir, template.version)
                if receipt["runtime_sha256"] != passing["runtime_sha256"] or receipt["workflow_version"] != template.version:
                    raise GateFailure("pilot receipt belongs to different runtime/workflow")
            receipts.append(receipt)
        if {r["shot"] for r in receipts} != set("ABCDEF") or len(receipts) != 6:
            raise GateFailure("pilot GO requires one accepted receipt for each shot A-F")
        budget = approval["minimum_accepted_sec_per_gpu_hour"]
        if not isinstance(budget, (int, float)) or not math.isfinite(budget) or budget <= 0:
            raise GateFailure("pilot acceptance budget must be positive")
        if score_receipts(receipts)["accepted_sec_per_gpu_hour"] < budget:
            raise GateFailure("pilot throughput is below the human acceptance budget")
        recovery = approval["recovery_evidence"]
        path = contained_path(bundle.project.benchmarks_dir, recovery["path"])
        if sha256_file(path) != recovery["sha256"]:
            raise GateFailure("recovery evidence changed")
        evidence = read_json(path)
        check_recovery_evidence(bundle.project.artifacts_dir, evidence, pilot["sha256"])
        return []
    except (GranthError, OSError, ValueError, KeyError, TypeError) as exc:
        return [str(exc)]

def hard_gates(bundle: Bundle, results: list[TaskResult]) -> list[GateResult]:
    source_problems = []
    try:
        require_current(bundle)
    except (GranthError, OSError, ValueError) as exc:
        source_problems.append(str(exc))
    scheduler = Scheduler(episode_store(bundle.project, bundle.adhyay))
    expected = plan_tasks(bundle, scheduler)
    current = scheduler.status(expected)
    expected_ids = [t.task_id() for t in expected]
    failing = [f"{r.name}: {r.status}" for r in results if r.status not in ("complete", "resumed")]
    if [r.task_id for r in results] != expected_ids:
        failing.append("results do not cover the current task plan")
    failing += [f"{r.name}: no verified current output" for r in current if r.status != "complete"]
    decode = [f"{r.name}: media verification failed" for r in current
              if r.stage in ("audio", "tier0", "tier1", "tier2", "assembly") and r.status != "complete"]
    return [gate("source_integrity", source_problems), gate("canon_identity", source_problems),
            gate("marathi_lock", source_problems), gate("hindi_terms", source_problems),
            gate("task_outputs", failing), gate("video_decode", decode),
            gate("production_go", production_problems(bundle))]
