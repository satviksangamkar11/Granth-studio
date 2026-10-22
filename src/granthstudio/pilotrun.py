"""A-F pilot execution, receipts, human review and the GO/NO-GO report (frozen sections 15 and 9).

Nothing here decides anything. Receipts record what was measured; acceptance comes only from a named
reviewer's rubric (O-005); the report separates measured, estimated, not_computed and unvalidated
values and always leaves the production decision to the user. Benchmark mode lets the pilot run an
unvalidated LTX capability so that its evidence can validate it (pins and files are still enforced).
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import Project, load_models, load_yaml
from .diagnostics import measure_shot
from .errors import ConfigError, GateFailure
from .ffmpeg import probe
from .integrity import atomic_write_json, read_json, sha256_file, sha256_obj
from .pilot import PILOT_DEFINITIONS, plan_pilot, score_receipts
from .pipeline import (ASSEMBLY_VERSION, LANGUAGE_NAME, Bundle, check_recovery_evidence, episode_store, load_bundle,
                       plan_tasks, production_problems, snapshot)
from .runtime import (gpu_status, load_runtime, preflight, ram_available_mb, require_gpu_ready, require_single_worker,
                      stop_before_deadline, write_run_receipt)
from .scheduler import RUN_LOG, Scheduler
from .schemas import validate_document

SHOT_LABELS = "ABCDEF"
KINDS = {
    "measured": "taken directly from a tool or file in this run",
    "estimated": "derived from measurements with a stated approximation",
    "not_computed": "no measurement exists; the reason is given",
    "unvalidated": "depends on a model, workflow or setting that no human has validated",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def typed(value: Any, kind: str, note: str | None = None) -> dict[str, Any]:
    if kind not in KINDS:
        raise ValueError(f"unknown value kind {kind!r}")
    return {"value": value, "kind": kind, **({"note": note} if note else {})}


def pilot_dir(project: Project) -> Path:
    return project.benchmarks_dir / "pilot_af"


def pilot_config(project: Project) -> dict[str, Any]:
    data = load_yaml(project.root / "config" / "pilot.yaml")
    validate_document("pilot_config", data)
    return data


def store_for(project: Project, adhyay: int, name: str | None) -> Path:
    if name is None:
        return episode_store(project, adhyay)
    if not re.fullmatch(r"[a-z0-9_]+", name):
        raise ConfigError("store names are lower-case letters, digits and underscores")
    return project.artifacts_dir / "tasks" / name


def _bundle(project: Project, models: dict[str, Any], adhyay: int) -> Bundle:
    if adhyay != 1:
        raise ConfigError("the pilot chapter is Adhyay 1 (P-003)")
    return load_bundle(project, models, adhyay, benchmark=True)


def selection(bundle: Bundle, scheduler: Scheduler):
    """Tasks the pilot needs: shots A-F with their keyframes, both audio tracks, and the assembly
    only when every shot of the chapter is a pilot shot (assembly depends on all shots)."""
    mapping = plan_pilot(bundle.compiled)
    tasks = plan_tasks(bundle, scheduler)
    by_name = {t.name: t for t in tasks}
    by_id = {t.task_id(): t for t in tasks}
    wanted = {by_name[mapping[label]].task_id() for label in SHOT_LABELS}
    wanted |= {t.task_id() for t in tasks if t.stage == "audio"}
    full_chapter = {s["shot_id"] for s in bundle.compiled["shots"]} <= set(mapping.values())
    if full_chapter:
        wanted |= {t.task_id() for t in tasks if t.stage == "assembly"}
    stack = list(wanted)  # close over dependencies AFTER assembly joins: lip-sync and audio deps come with it
    while stack:
        for dep in by_id[stack.pop()].depends_on:
            if dep not in wanted:
                wanted.add(dep)
                stack.append(dep)
    return mapping, [t for t in tasks if t.task_id() in wanted], full_chapter


# ------------------------------------------------------------------ running

def run_pilot(project: Project, adhyay: int, store_name: str | None, execute: bool, require_gpu: bool):
    models = load_models(project)
    bundle = _bundle(project, models, adhyay)
    scheduler = Scheduler(store_for(project, adhyay, store_name))
    mapping, selected, full_chapter = selection(bundle, scheduler)
    if not execute:
        return mapping, selected, full_chapter, None, None
    started = _now()
    runtime = load_runtime(project)
    require_single_worker(runtime)
    report = preflight(project, models, runtime, gpu_status(), ram_available_mb())
    if require_gpu:
        require_gpu_ready(report)
    results = scheduler.run(selected, should_stop=stop_before_deadline(runtime))
    path = write_run_receipt(project, "pilot_run", adhyay, started, results, [], snapshot(bundle), report, scheduler.store)
    return mapping, selected, full_chapter, results, path


# ------------------------------------------------------------------ measurement and receipts

def run_history(store: Path, task_id: str) -> tuple[float, int]:
    """Wall-clock seconds and attempts over every logged run of the task, failures included (D-004)."""
    log = store / RUN_LOG
    entries = [json.loads(l) for l in log.read_text(encoding="utf-8").splitlines() if l.strip()] if log.is_file() else []
    mine = [e for e in entries if e["task_id"] == task_id]
    attempts = sum(e["attempts"] for e in mine if e["status"] in ("complete", "failed", "pending", "not_validated"))
    return sum(e.get("elapsed_s", 0.0) for e in mine), max(attempts, 1)


def _gpu_label(name: str | None) -> str:
    if not name:
        return "unknown"
    return "T4" if "T4" in name else name


def complete_ids(scheduler: Scheduler, tasks) -> set[str]:
    """Task ids whose receipts, inputs and dependencies verify now (status() plans the tasks first)."""
    return {r.task_id for r in scheduler.status(tasks) if r.status == "complete"}


def measured_receipt(bundle: Bundle, scheduler: Scheduler, mapping, tasks, label: str, plan_sha: str,
                     complete: set[str]) -> dict[str, Any] | None:
    """Measured fields of one shot's receipt, or None when its task has no valid output."""
    by_name = {t.name: t for t in tasks}
    notes: dict[str, str] = {}
    if label == "F":
        pair = [by_name.get("assemble_mr"), by_name.get("assemble_hi")]
        if any(t is None or t.task_id() not in complete for t in pair):
            return None
        videos = {t.name: scheduler.task_dir(t) / f"adhyay_{bundle.adhyay:02d}_{LANGUAGE_NAME[t.name[-2:]]}.mp4" for t in pair}
        elapsed = sum(run_history(scheduler.store, t.task_id())[0] for t in pair)
        attempts = sum(run_history(scheduler.store, t.task_id())[1] for t in pair)
        notes["video_seconds"] = ("0 by accounting choice: the edits re-use shot footage already counted once; "
                                  "the user may change this (O-004)")
        return {"schema_version": 1, "capability": "assembly", "shot": "F", "checkpoint_sha256": None,
                "workflow_version": ASSEMBLY_VERSION, "gpu": "CPU", "gpu_count": 1, "gpu_seconds_total": 0.0,
                "attempts": attempts, "video_seconds": 0.0, "peak_vram_mb": None,
                "output_sha256": sha256_obj({n: sha256_file(p) for n, p in sorted(videos.items())}),
                "pilot_plan_sha256": plan_sha,
                "measurement_notes": {**notes, "cpu_wall_seconds": f"{elapsed:.1f} (not counted as GPU time)"}}
    task = by_name[mapping[label]]
    directory = scheduler.task_dir(task)
    if task.task_id() not in complete:
        return None
    elapsed, attempts = run_history(scheduler.store, task.task_id())
    if (directory / "fallback.json").is_file():
        # The LTX renders failed and a Tier 0 stand-in was used: that is evidence against the capability, not for it.
        return {"schema_version": 1, "shot": label, "gpu_count": 1, "attempts": attempts, "video_seconds": 0.0,
                "output_sha256": None, "pilot_plan_sha256": plan_sha, "capability": "i2v" if task.stage == "tier1" else "flf",
                "checkpoint_sha256": None, "workflow_version": task.workflow_version, "gpu": "unknown",
                "gpu_seconds_total": elapsed, "peak_vram_mb": None,
                "measurement_notes": {"fallback": "all LTX attempts failed; a Tier 0 stand-in was used and is not counted",
                                      "gpu_seconds_total": "estimated: wall-clock of every attempt"}}
    info = probe(directory / "clip.mp4")
    seconds = info.video_duration_s if info.video_duration_s is not None else info.duration_s
    base = {"schema_version": 1, "shot": label, "gpu_count": 1, "attempts": attempts, "video_seconds": seconds,
            "output_sha256": sha256_file(directory / "clip.mp4"), "pilot_plan_sha256": plan_sha}
    if task.stage == "tier0":
        return {**base, "capability": "tier0", "checkpoint_sha256": None, "workflow_version": task.workflow_version,
                "gpu": "CPU", "gpu_seconds_total": 0.0, "peak_vram_mb": None,
                "measurement_notes": {"gpu_seconds_total": "0: FFmpeg stills use no GPU",
                                      "cpu_wall_seconds": f"{elapsed:.1f}"}}
    metrics = read_json(directory / "metrics.json")
    peak = metrics["peak_vram_mb"]["value"]
    return {**base, "capability": metrics["capability"], "checkpoint_sha256": metrics["checkpoint_sha256"],
            "workflow_version": metrics["workflow_version"], "runtime_sha256": metrics["runtime_sha256"],
            "gpu": _gpu_label(metrics["gpu"]), "gpu_seconds_total": elapsed, "peak_vram_mb": peak,
            "measurement_notes": {
                "gpu_seconds_total": "estimated: wall-clock seconds of every attempt in every session on one GPU "
                                     "(failed attempts included, D-004); not GPU utilisation",
                "peak_vram_mb": "sampled lower bound: nvidia-smi at each poll, not a true peak" if peak is not None
                                else "not measured: nvidia-smi gave no sample",
                "comfyui_execution_s": str(metrics["execution_s"]["value"]),
                "wall_s_last_attempt": f"{metrics['wall_s']['value']:.1f}"}}


def _digest(measured: dict[str, Any]) -> str:
    return sha256_obj(measured)


def build_receipts(project: Project, adhyay: int, store_name: str | None) -> dict[str, Any]:
    """Write one benchmark receipt per rendered shot. Acceptance is taken only from matching reviews."""
    models = load_models(project)
    bundle = _bundle(project, models, adhyay)
    scheduler = Scheduler(store_for(project, adhyay, store_name))
    mapping, selected, _ = selection(bundle, scheduler)
    plan_path = pilot_dir(project) / "pilot_plan.json"
    if not plan_path.is_file() or read_json(plan_path) != bundle.compiled:
        atomic_write_json(plan_path, bundle.compiled)
    plan_sha = sha256_file(plan_path)
    written, missing, pending = [], {}, []
    complete = complete_ids(scheduler, selected)
    for label in SHOT_LABELS:
        measured = measured_receipt(bundle, scheduler, mapping, selected, label, plan_sha, complete)
        if measured is None:
            missing[label] = "task has no valid output in this store"
            continue
        review_path = pilot_dir(project) / "reviews" / f"{label}.json"
        review = read_json(review_path) if review_path.is_file() else None
        if "fallback" in measured.get("measurement_notes", {}):
            accepted, outcome = False, "fail"  # a stand-in clip can never accept the capability it replaced
        elif review and review["measurement_sha256"] == _digest(measured):
            accepted, outcome = review["decision"] == "accept", "pass" if review["decision"] == "accept" else "fail"
        else:
            accepted, outcome = None, "pending"
            pending.append(label)
        receipt = {**measured, "accepted": accepted, "outcome": outcome, "recorded_at": _now()}
        validate_document("benchmark_receipt", receipt)
        atomic_write_json(pilot_dir(project) / "receipts" / f"{label}.json", receipt)
        written.append(label)
    return {"written": written, "missing": missing, "awaiting_review": pending, "pilot_plan_sha256": plan_sha}


# ------------------------------------------------------------------ human review

def record_review(project: Project, adhyay: int, store_name: str | None, label: str, reviewer: str, decision: str,
                  ratings: dict[str, tuple[str, str]], note: str) -> dict[str, Any]:
    """Capture the human rubric for one shot, bound to the exact measurements reviewed."""
    if label not in SHOT_LABELS:
        raise ConfigError("shot must be one of A-F")
    if not reviewer.strip():
        raise ConfigError("a reviewer name is required")
    criteria = pilot_config(project)["rubric"]["criteria"]
    if not criteria:
        raise ConfigError("no review criteria are defined in config/pilot.yaml (O-005): decide the rubric first")
    if set(ratings) != set(criteria):
        raise ConfigError(f"rate exactly the configured criteria {criteria}; got {sorted(ratings)}")
    if decision == "accept" and any(r == "fail" for r, _ in ratings.values()):
        raise GateFailure("a shot with a failed criterion cannot be accepted")
    models = load_models(project)
    bundle = _bundle(project, models, adhyay)
    scheduler = Scheduler(store_for(project, adhyay, store_name))
    mapping, selected, _ = selection(bundle, scheduler)
    plan_path = pilot_dir(project) / "pilot_plan.json"
    plan_sha = sha256_file(plan_path) if plan_path.is_file() else None
    if plan_sha is None:
        raise GateFailure("run 'pilot receipts' first: the pilot plan snapshot does not exist yet")
    measured = measured_receipt(bundle, scheduler, mapping, selected, label, plan_sha, complete_ids(scheduler, selected))
    if measured is None:
        raise GateFailure(f"shot {label} has not been rendered in this store")
    review = {"schema_version": 1, "adhyay": adhyay, "shot": label, "reviewer": reviewer.strip(), "decision": decision,
              "ratings": {k: {"rating": r, **({"note": n} if n else {})} for k, (r, n) in ratings.items()},
              **({"note": note} if note else {}), "measurement_sha256": _digest(measured), "recorded_at": _now()}
    validate_document("pilot_review", review)
    atomic_write_json(pilot_dir(project) / "reviews" / f"{label}.json", review)
    return review


# ------------------------------------------------------------------ recovery evidence

def build_recovery_evidence(project: Project, adhyay: int, clean_store: str, resumed_store: str, reviewer: str) -> Path:
    """Describe two real scheduler runs as recovery evidence, verified with the production check.
    The 'passed' assertion is the named reviewer's; the files and logs are checked, not trusted."""
    if not reviewer.strip():
        raise ConfigError("a reviewer name is required")
    models = load_models(project)
    bundle = _bundle(project, models, adhyay)
    plan_path = pilot_dir(project) / "pilot_plan.json"
    if not plan_path.is_file():
        raise GateFailure("run 'pilot receipts' first: the pilot plan snapshot does not exist yet")

    def outputs(store_name: str) -> dict[str, dict[str, str]]:
        scheduler = Scheduler(store_for(project, adhyay, store_name))
        result = {}
        for task in plan_tasks(bundle, scheduler):
            if task.stage == "assembly":
                language = task.name[-2:]
                video = scheduler.task_dir(task) / f"adhyay_{adhyay:02d}_{LANGUAGE_NAME[language]}.mp4"
                if not video.is_file():
                    raise GateFailure(f"{store_name}: {task.name} has no output; the chapter must be fully assembled")
                result[f"{language}_video"] = {"path": video.relative_to(project.artifacts_dir.resolve()).as_posix(),
                                               "sha256": sha256_file(video)}
        return result

    evidence = {"schema_version": 1, "passed": True, "reviewed_by": reviewer.strip(),
                "pilot_plan_sha256": sha256_file(plan_path), "clean_outputs": outputs(clean_store),
                "resumed_outputs": outputs(resumed_store)}
    check_recovery_evidence(project.artifacts_dir, evidence, evidence["pilot_plan_sha256"])
    target = pilot_dir(project) / "recovery_evidence.json"
    atomic_write_json(target, evidence)
    return target


# ------------------------------------------------------------------ report

def _language_report(project: Project, bundle: Bundle, scheduler: Scheduler, tasks) -> dict[str, Any]:
    from .speech import candidate_root
    audio_task = {t.name[:2]: t for t in tasks if t.stage == "audio"}
    report = {}
    for language in ("mr", "hi"):
        timings_path = scheduler.task_dir(audio_task[language]) / "timings.json"
        timings = read_json(timings_path) if timings_path.is_file() else {}
        lines = []
        for entry in bundle.timelines[language]["entries"]:
            line_id = entry["dialogue_id"]
            asr_path = candidate_root(project, language) / f"{line_id}.asr.json"
            asr = read_json(asr_path) if asr_path.is_file() else None
            audio = entry.get("audio") or {}
            matches = asr is not None and asr["audio_sha256"] == audio.get("sha256")
            align_path = candidate_root(project, language) / f"{line_id}.align.json"
            align = read_json(align_path) if align_path.is_file() else None
            align_ok = align is not None and align["audio_sha256"] == audio.get("sha256")
            row = {"dialogue_id": line_id,
                   "duration_s": typed(timings[line_id]["duration_s"], "measured") if line_id in timings
                   else typed(None, "not_computed", "audio task has no timings in this store"),
                   "asr_alignment": typed({"similarity": asr["similarity"], "missing_words": asr["missing_words"],
                                           "extra_words": asr["extra_words"]}, "measured",
                                          "word-level comparison with the script; not a pronunciation judgment")
                   if matches else typed(None, "not_computed", "no ASR report for the current audio"),
                   "word_alignment": typed({"words": align["words"], "model": align["model"], "revision": align["revision"]},
                                           "measured", "word timings only; subtitles stay phrase level (frozen 5.4)")
                   if align_ok else typed(None, "not_computed", "no word alignment for the current audio"),
                   "audio_provenance": audio.get("provenance", {"origin": "imported"}) if audio else "no audio attached"}
            if language == "hi":
                alignment = entry["alignment"]
                row["translation"] = {"origin": alignment.get("source", {"origin": "not recorded (hand-written)"}),
                                      "reviewed_by": alignment["verification"]["reviewer"],
                                      "deterministic_checks": typed("passed at load", "measured"),
                                      "semantic_comparison": typed(None, "not_computed",
                                          "no automatic semantic model; only the named human review exists")}
            lines.append(row)
        report[language] = lines
    return report


def pilot_report(project: Project, adhyay: int, store_name: str | None) -> tuple[dict[str, Any], Path]:
    models = load_models(project)
    bundle = _bundle(project, models, adhyay)
    scheduler = Scheduler(store_for(project, adhyay, store_name))
    mapping, selected, full_chapter = selection(bundle, scheduler)
    config = pilot_config(project)
    receipts, shots = {}, {}
    for label in SHOT_LABELS:
        path = pilot_dir(project) / "receipts" / f"{label}.json"
        receipts[label] = read_json(path) if path.is_file() else None
        review_path = pilot_dir(project) / "reviews" / f"{label}.json"
        by_name = {t.name: t for t in selected}
        clip = None
        if label != "F" and mapping[label] in by_name:
            candidate = scheduler.task_dir(by_name[mapping[label]]) / "clip.mp4"
            clip = candidate if candidate.is_file() else None
        shot: dict[str, Any] = {"focus": PILOT_DEFINITIONS[label]["focus"], "receipt": None, "review": None,
                                "diagnostics": None}
        receipt = receipts[label]
        if receipt:
            notes = receipt.get("measurement_notes", {})
            shot["receipt"] = {
                "accepted": typed(receipt["accepted"], "measured" if receipt["accepted"] is not None else "not_computed",
                                  None if receipt["accepted"] is not None else "no matching human review"),
                "video_seconds": typed(receipt["video_seconds"], "measured", notes.get("video_seconds")),
                "gpu_seconds_total": typed(receipt["gpu_seconds_total"],
                                           "estimated" if receipt["capability"] in ("i2v", "flf") else "measured",
                                           notes.get("gpu_seconds_total")),
                "attempts": typed(receipt["attempts"], "measured"),
                "peak_vram_mb": typed(receipt["peak_vram_mb"], "measured" if receipt["peak_vram_mb"] is not None else "not_computed",
                                      notes.get("peak_vram_mb")),
                "gpu": typed(receipt["gpu"], "measured"),
                "workflow_version": typed(receipt["workflow_version"], "measured"),
                "capability_status": typed(models["ltx"]["capabilities"].get(receipt["capability"], "n/a"), "unvalidated"
                                           if receipt["capability"] in ("i2v", "flf") else "measured")}
        else:
            shot["receipt"] = typed(None, "not_computed", "shot not rendered or receipts not built")
        if review_path.is_file():
            review = read_json(review_path)
            shot["review"] = {k: review[k] for k in ("reviewer", "decision", "ratings", "recorded_at")}
        if clip is not None:
            shot["diagnostics"] = measure_shot(models, clip, [])
        shots[label] = shot
    # throughput (D-004)
    complete = [r for r in receipts.values() if r]
    try:
        if len(complete) != 6:
            raise GateFailure("receipts for all six shots are required")
        scored = score_receipts(complete)
        throughput = typed(scored, "estimated", "GPU seconds are wall-clock estimates (D-004 accounting)")
    except GateFailure as exc:
        throughput = typed(None, "not_computed", str(exc))
    budget = config["acceptance"]["min_accepted_sec_per_gpu_hour"]
    meets = (None if budget is None or throughput["value"] is None
             else throughput["value"]["accepted_sec_per_gpu_hour"] >= budget)
    flf = {label: receipts[label] and {k: receipts[label][k] for k in
           ("capability", "video_seconds", "gpu_seconds_total", "peak_vram_mb", "attempts", "accepted", "outcome")}
           for label in ("B", "C")}
    strict = load_bundle(project, models, adhyay)
    approval_problems = production_problems(strict) if (project.root / "approvals" / f"adhyay_{adhyay:02d}.json").is_file() else None
    recovery_path = pilot_dir(project) / "recovery_evidence.json"
    report = {
        "schema_version": 1, "adhyay": adhyay, "generated_at": _now(), "legend": KINDS,
        "store": str(scheduler.store), "assembly_included": full_chapter,
        "pilot_plan_sha256": sha256_file(pilot_dir(project) / "pilot_plan.json") if (pilot_dir(project) / "pilot_plan.json").is_file() else None,
        "shots": shots,
        "throughput": throughput,
        "acceptance_budget": typed(budget, "measured" if budget is not None else "not_computed",
                                   None if budget is not None else "undecided (O-004): no verdict is given"),
        "meets_budget": typed(meets, "estimated" if meets is not None else "not_computed"),
        "flf_comparison": {"note": "B (I2V) vs C (FLF); values only, no verdict", "shots": flf},
        "languages": _language_report(project, bundle, scheduler, selected),
        "settings": {
            "ltx_i2v": typed(models["ltx"]["capabilities"]["i2v"], "unvalidated"),
            "ltx_flf": typed(models["ltx"]["capabilities"]["flf"], "unvalidated"),
            "sdxl": typed(models["sdxl"]["status"], "unvalidated"),
            "translation": typed(models["translation"]["status"], "unvalidated"),
            "speech": typed(models["speech"]["status"], "unvalidated"),
            "asr": typed(models["asr"]["status"], "unvalidated"),
            "frame_rule": typed("pinned list only", "unvalidated", "O-003 is open"),
            "dual_t4": typed(load_runtime(project)["workers"]["dual_t4"], "measured")},
        "recovery_evidence": {"present": recovery_path.is_file(),
                              "sha256": sha256_file(recovery_path) if recovery_path.is_file() else None},
        "production_approval": {"problems": approval_problems if approval_problems is not None
                                else "no approval file exists (it is created only by a human)"},
        "decision": {"production_go": "NOT DECIDED: the GO/NO-GO is the user's; this report is evidence only",
                     "tier2_flf": "NOT DECIDED: leave FLF disabled unless the human decision says go"},
        "open_decisions": ["O-003", "O-004", "O-005", "O-006", "O-007", "O-008"]}
    path = project.artifacts_dir / "reports" / f"pilot_adhyay_{adhyay:02d}.json"
    atomic_write_json(path, report)
    return report, path
