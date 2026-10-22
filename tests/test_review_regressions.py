"""Regression checks for F01-F12. All media/approvals/model pins below are SYNTHETIC.

Synthetic tones verify timing, not translation, speech or historical authenticity.
No real research, approval, model or GPU runtime is used by this suite.
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import time
from pathlib import Path

import pytest

from granthstudio.canon import load_canon
from granthstudio.cli import main
from granthstudio.comfy import ComfyBackend, select_video
from granthstudio.config import load_models, load_yaml, require_capability
from granthstudio.episodes import compile_episode
from granthstudio.errors import CanonReferenceError, CapabilityDisabled, ConfigError, GateFailure, IntegrationUnavailable, JobPending, TaskFailed
from granthstudio.ffmpeg import MEDIA_TIMEOUT_S, _run, assemble, probe, validate_video
from granthstudio.integrity import atomic_write_json, contained_path, normalize_text, read_json, sha256_file, sha256_obj
from granthstudio.pipeline import episode_store, hard_gates, load_bundle, plan_tasks, production_problems
from granthstudio.research import approve, load_research, require_approved
from granthstudio.scheduler import RECEIPT, Scheduler, Task
from granthstudio.timelines import check_timelines
from tests.conftest import FIXED_TIME, have_tool, make_clip

def bundle(project):
    return load_bundle(project, load_models(project), 1)

def compile_project(project):
    return compile_episode(project, load_models(project), load_canon(project), 1,
                           load_research(project, 1), require_approved(project, 1))

def write_task(content):
    def run(work):
        (work / "out.bin").write_bytes(content)
        return {"out": "out.bin"}
    return run

def test_f01_dependency_identity_invalidates_downstream(tmp_path):
    first = Task("tier0", "clip", {"visual": "v1"}, "v", write_task(b"one"))
    changed = Task("tier0", "clip", {"visual": "v2"}, "v", write_task(b"two"))
    a = Task("assembly", "final", {}, "v", write_task(b"old"), depends_on=(first.task_id(),))
    b = Task("assembly", "final", {}, "v", write_task(b"new"), depends_on=(changed.task_id(),))
    assert a.task_id() != b.task_id()
    scheduler = Scheduler(tmp_path)
    scheduler.run([first, a])
    assert [r.status for r in scheduler.run([changed, b])] == ["complete", "complete"]

def test_f01_dependency_output_hash_invalidates_same_task_id(tmp_path):
    upstream = Task("tier0", "clip", {}, "v", write_task(b"one"))
    downstream = Task("assembly", "final", {}, "v", write_task(b"final"), depends_on=(upstream.task_id(),))
    scheduler = Scheduler(tmp_path)
    scheduler.run([upstream, downstream])
    (scheduler.task_dir(upstream) / "out.bin").write_bytes(b"corrupt")
    upstream.run = write_task(b"new output under same input identity")
    results = scheduler.run([upstream, downstream])
    assert [r.status for r in results] == ["complete", "complete"]

def test_f01_receipt_must_match_expected_task(tmp_path):
    task = Task("tier0", "clip", {"source": "one"}, "v", write_task(b"one"))
    scheduler = Scheduler(tmp_path)
    scheduler.run([task])
    path = scheduler.task_dir(task) / RECEIPT
    receipt = read_json(path)
    receipt["inputs"] = {"source": "different"}
    atomic_write_json(path, receipt)
    assert scheduler.status([task])[0].status == "missing"

def test_f01_hindi_edit_preserves_shared_visual_tasks(approved_project):
    before = bundle(approved_project)
    scheduler = Scheduler(episode_store(approved_project, 1))
    first = {t.name: t.task_id() for t in plan_tasks(before, scheduler)}
    path = approved_project.episodes_dir / "adhyay_01" / "hi.yaml"
    hi = load_yaml(path)
    hi["entries"][0]["text"] += " SYNTHETIC"
    hi["entries"][0]["alignment"]["verification"]["hi_sha256"] = sha256_obj(normalize_text(hi["entries"][0]["text"]))
    atomic_write_json(path, hi)
    second = {t.name: t.task_id() for t in plan_tasks(bundle(approved_project), scheduler)}
    assert first["a01_s01_sh01"] == second["a01_s01_sh01"]
    assert first["a01_s01_sh02"] == second["a01_s01_sh02"]
    assert first["hi_voice"] != second["hi_voice"]
    assert first["assemble_hi"] != second["assemble_hi"]
    assert first["assemble_mr"] == second["assemble_mr"]

def test_f01_canon_edit_changes_dependent_clip_ids(approved_project):
    scheduler = Scheduler(episode_store(approved_project, 1))
    before = {t.name: t.task_id() for t in plan_tasks(bundle(approved_project), scheduler)}
    path = approved_project.canon_dir / "characters.yaml"
    canon = load_yaml(path)
    canon["entries"][0]["canonical_name"] = "SYNTH-A revised"
    atomic_write_json(path, canon)
    after = {t.name: t.task_id() for t in plan_tasks(bundle(approved_project), scheduler)}
    assert before["a01_s01_sh01"] != after["a01_s01_sh01"]

def test_f02_missing_silent_research_scene_is_blocked(approved_project):
    path = approved_project.research_dir / "adhyay_01" / "research.yaml"
    research = load_yaml(path)
    scene = copy.deepcopy(research["scenes"][0])
    scene.update(scene_id="a01_s02", dialogue=[])
    research["scenes"].append(scene)
    atomic_write_json(path, research)
    approve(approved_project, 1, "synthetic-test-only", FIXED_TIME)
    path = approved_project.episodes_dir / "adhyay_01" / "manifest.yaml"
    manifest = load_yaml(path); manifest["research_version"] = 2; atomic_write_json(path, manifest)
    with pytest.raises(GateFailure, match="every approved scene"):
        compile_project(approved_project)

@pytest.mark.parametrize("change", ["omit", "duplicate", "reorder"])
def test_f02_dialogue_coverage_and_order_are_required(approved_project, change):
    path = approved_project.episodes_dir / "adhyay_01" / "manifest.yaml"
    manifest = load_yaml(path)
    shots = manifest["scenes"][0]["shots"]
    if change == "omit": shots[1]["dialogue_ids"] = []
    elif change == "duplicate": shots[0]["dialogue_ids"].append("d_0001")
    else: shots.reverse()
    atomic_write_json(path, manifest)
    with pytest.raises(GateFailure, match="all approved dialogue"):
        compile_project(approved_project)

def test_f03_actions_and_provenance_survive_compilation(approved_project):
    path = approved_project.research_dir / "adhyay_01" / "research.yaml"
    research = load_yaml(path)
    fact = {"id": "synthetic-action", "text": "synthetic gesture", "source_refs": ["fixture:3"], "artistic": False}
    research["scenes"][0]["actions"].append(fact)
    atomic_write_json(path, research)
    approve(approved_project, 1, "synthetic-test-only", FIXED_TIME)
    path = approved_project.episodes_dir / "adhyay_01" / "manifest.yaml"
    manifest = load_yaml(path); manifest["research_version"] = 2
    manifest["scenes"][0]["shots"][0]["action_ids"] = ["synthetic-action"]
    atomic_write_json(path, manifest)
    shot = compile_project(approved_project)["shots"][0]
    assert fact in shot["research_scene"]["actions"]
    assert shot["characters"] == research["scenes"][0]["characters"]
    assert shot["location"] == research["scenes"][0]["location"]

def test_f03_unsupported_approved_location_is_blocked(approved_project):
    path = approved_project.canon_dir / "locations.yaml"
    canon = load_yaml(path)
    canon["entries"].append({"id": "loc_other", "canonical_name": "OTHER", "status": "approved"})
    atomic_write_json(path, canon)
    path = approved_project.episodes_dir / "adhyay_01" / "manifest.yaml"
    manifest = load_yaml(path); manifest["scenes"][0]["location"] = "loc_other"; atomic_write_json(path, manifest)
    with pytest.raises(CanonReferenceError, match="differs from approved research"):
        compile_project(approved_project)

def test_f04_unreviewed_or_changed_hindi_is_blocked(approved_project):
    current = bundle(approved_project)
    hi = copy.deepcopy(current.timelines["hi"])
    hi["entries"][0]["alignment"]["reviewed"] = False
    assert any("not approved" in p for p in check_timelines(current.canon, current.compiled, current.research, current.timelines["mr"], hi))
    hi["entries"][0]["alignment"]["reviewed"] = True
    hi["entries"][0]["text"] = "SYNTH-A does NOT say 2 things"
    assert any("current text" in p for p in check_timelines(current.canon, current.compiled, current.research, current.timelines["mr"], hi))

def test_f06_validator_really_decodes(monkeypatch, tmp_path):
    import granthstudio.ffmpeg as media
    path = tmp_path / "bad.mp4"; path.write_bytes(b"synthetic")
    monkeypatch.setattr(media, "_tool", lambda name: name)
    calls = []
    def run(command):
        calls.append(command[0])
        if command[0] == "ffprobe":
            return subprocess.CompletedProcess(command, 0, json.dumps({"format": {"duration": "1"},
                "streams": [{"codec_type": "video", "codec_name": "h264"}]}), "")
        raise TaskFailed("synthetic damaged packet")
    monkeypatch.setattr(media, "_run", run)
    with pytest.raises(TaskFailed, match="damaged packet"):
        validate_video(path, 1)
    assert calls == ["ffprobe", "ffmpeg"]

def test_ffmpeg_timeout_is_bounded_and_partial_work_is_removed(monkeypatch, tmp_path):
    import granthstudio.ffmpeg as media
    def timeout(command, **kwargs):
        assert kwargs["timeout"] == 300 == MEDIA_TIMEOUT_S
        raise subprocess.TimeoutExpired(command, kwargs["timeout"])
    monkeypatch.setattr(media.subprocess, "run", timeout)
    def partial(work):
        (work / "partial.mp4").write_bytes(b"partial")
        _run(["ffmpeg"])
    scheduler = Scheduler(tmp_path)
    task = Task("tier0", "timeout", {}, "v", partial)
    assert scheduler.run([task])[0].status == "failed"
    assert not scheduler.task_dir(task).exists()
    assert not list((tmp_path / "tier0").glob(".work-*"))

def runtime_models(project, tmp_path):
    models = load_models(project)
    files = {}
    for kind in ("checkpoint", "vae", "text_encoder"):
        path = tmp_path / kind; path.write_bytes(b"SYNTHETIC PIN ONLY:" + kind.encode())
        files[kind] = {"path": str(path), "sha256": sha256_file(path)}
    models["ltx"].update(checkpoint_sha256=files["checkpoint"]["sha256"],
        runtime={"files": files, "comfyui_commit": "a"*40, "node_pack_commit": "b"*40,
                 "gpu": "T4", "precision": "fp16", "width": 512, "height": 320})
    models["ltx"]["capabilities"]["i2v"] = "validated"
    runtime_hash = sha256_obj({"runtime": models["ltx"]["runtime"], "frame_counts": models["ltx"]["frame_counts"],
                              "family": "LTX-Video", "version": "0.9.8", "variant": "2b-distilled"})
    receipt = {"schema_version": 1, "capability": "i2v", "shot": "B", "checkpoint_sha256": files["checkpoint"]["sha256"],
        "workflow_version": "workflow-one", "runtime_sha256": runtime_hash, "gpu": "T4", "gpu_count": 1,
        "gpu_seconds_total": 60, "attempts": 1, "video_seconds": 2, "accepted": True, "outcome": "pass",
        "peak_vram_mb": 10000, "output_sha256": "c"*64, "recorded_at": FIXED_TIME}
    atomic_write_json(project.benchmarks_dir / "synthetic.json", receipt)
    return models

def test_f07_exact_workflow_and_runtime_files_are_required(project, tmp_path):
    models = runtime_models(project, tmp_path)
    assert require_capability(models, "i2v", project.benchmarks_dir, "workflow-one")
    with pytest.raises(CapabilityDisabled):
        require_capability(models, "i2v", project.benchmarks_dir, "workflow-two")
    Path(models["ltx"]["runtime"]["files"]["vae"]["path"]).write_bytes(b"changed")
    with pytest.raises(CapabilityDisabled, match="hash mismatch"):
        require_capability(models, "i2v", project.benchmarks_dir, "workflow-one")

def test_f08_timeout_and_restart_reuse_prompt_id(tmp_path):
    class Backend(ComfyBackend):
        submissions = 0
        polls = 0
        def submit(self, graph): self.submissions += 1; return "prompt-one"
        def wait(self, prompt_id):
            assert prompt_id == "prompt-one"
            self.polls += 1
            if self.polls == 1: raise JobPending("still running")
            return {"outputs": {}}
    backend = Backend("http://synthetic.invalid")
    journal = tmp_path / "job.json"
    with pytest.raises(JobPending): backend.execute({"1": {}}, journal)
    assert backend.execute({"1": {}}, journal) == {"outputs": {}}
    assert backend.submissions == 1

def test_f08_ambiguous_submission_never_posts_twice(tmp_path):
    class Backend(ComfyBackend):
        submissions = 0
        def submit(self, graph):
            self.submissions += 1
            raise IntegrationUnavailable("response lost after server accepted POST")
    backend = Backend("http://synthetic.invalid")
    for _ in range(2):
        with pytest.raises(JobPending): backend.execute({}, tmp_path / "job.json")
    assert backend.submissions == 1

def test_f09_only_designated_video_is_selected():
    history = {"outputs": {"3": {"images": [{"filename": "preview.png"}]},
                           "9": {"videos": [{"filename": "final.mp4"}]}}}
    assert select_video(history, "9")["filename"] == "final.mp4"
    history["outputs"]["9"]["videos"].append({"filename": "other.mp4"})
    with pytest.raises(TaskFailed, match="exactly one"):
        select_video(history, "9")

def test_f10_no_implicit_production_approval(approved_project):
    assert production_problems(bundle(approved_project))

@pytest.mark.parametrize("path", ["../outside.png", "sub/../../outside.png", r"C:\outside.png", "/outside.png"])
def test_f11_data_paths_are_confined(tmp_path, path):
    with pytest.raises(ConfigError): contained_path(tmp_path, path)

def test_f11_symlink_escape_is_rejected(tmp_path):
    root = tmp_path / "root"; root.mkdir()
    other = tmp_path / "outside"; other.mkdir()
    try: (root / "link").symlink_to(other, target_is_directory=True)
    except OSError: pytest.skip("symlinks unavailable on this host")
    with pytest.raises(ConfigError): contained_path(root, "link/frame.png")

def test_f12_reapproval_during_run_blocks_old_snapshot(approved_project):
    old = bundle(approved_project)
    path = approved_project.research_dir / "adhyay_01" / "research.yaml"
    research = load_yaml(path); research["scenes"][0]["description"] += " revised"; atomic_write_json(path, research)
    approve(approved_project, 1, "synthetic-test-only", FIXED_TIME)
    path = approved_project.episodes_dir / "adhyay_01" / "manifest.yaml"
    manifest = load_yaml(path); manifest["research_version"] = 2; atomic_write_json(path, manifest)
    gates = {g.name: g for g in hard_gates(old, [])}
    assert gates["source_integrity"].passed is False

def make_cpu_project(project):
    """Reviewed test tones provide a complete CPU path; they are not real speech."""
    path = project.episodes_dir / "adhyay_01" / "manifest.yaml"
    manifest = load_yaml(path)
    for shot in manifest["scenes"][0]["shots"]:
        shot["tier"] = 0; shot["duration_s"] = 0.5
        shot.pop("frames", None); shot.pop("motion_prompt", None)
        shot["coverage"] = {"mode": "hold_final_frame", "reviewed_by": "synthetic-test-only"}
    atomic_write_json(path, manifest)
    for lang in ("mr", "hi"):
        path = project.episodes_dir / "adhyay_01" / f"{lang}.yaml"
        timeline = load_yaml(path)
        for index, entry in enumerate(timeline["entries"]):
            duration = 1.1 if lang == "hi" and index == 1 else 0.2
            audio = project.artifacts_dir / "audio" / f"{lang}_{index}.wav"
            audio.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
                f"sine=frequency=440:sample_rate=24000:duration={duration}", "-c:a", "pcm_s16le", str(audio)], check=True, timeout=20)
            entry["audio"] = {"path": audio.name, "sha256": sha256_file(audio), "language": lang,
                "speaker": entry["speaker"], "text_sha256": sha256_obj(normalize_text(entry["text"])),
                "speech_reviewed_by": "synthetic-test-only"}
        atomic_write_json(path, timeline)
    return bundle(project)

@pytest.mark.skipif(not (have_tool("ffmpeg") and have_tool("ffprobe")), reason="media tools missing")
def test_complete_cpu_bilingual_path_measures_audio_and_reuses_visuals(approved_project):
    current = make_cpu_project(approved_project)
    scheduler = Scheduler(episode_store(approved_project, 1))
    tasks = plan_tasks(current, scheduler)
    results = scheduler.run(tasks)
    assert all(r.status == "complete" for r in results), results
    plans = {}
    for lang in ("mr", "hi"):
        task = next(t for t in tasks if t.name == f"assemble_{lang}")
        directory = scheduler.task_dir(task)
        plan = read_json(directory / "edit_plan.json"); plans[lang] = plan
        name = "marathi" if lang == "mr" else "hindi"
        media = directory / f"adhyay_01_{name}.mp4"
        assert validate_video(media, plan["duration_s"], require_audio=True) == []
        assert plan["cues"][1]["start_s"] == 0.5
        assert (directory / f"adhyay_01_{name}.srt").is_file()
    assert plans["hi"]["duration_s"] > plans["mr"]["duration_s"]
    assert [s["source_sha256"] for s in plans["mr"]["shots"]] == [s["source_sha256"] for s in plans["hi"]["shots"]]
    resumed = scheduler.run(tasks)
    assert all(r.status == "resumed" for r in resumed)
    gates = {g.name: g.passed for g in hard_gates(current, resumed)}
    assert all(passed for name, passed in gates.items() if name != "production_go")
    assert gates["production_go"] is False

@pytest.mark.skipif(not (have_tool("ffmpeg") and have_tool("ffprobe")), reason="media tools missing")
def test_f01_changed_live_visual_blocks_resume(approved_project):
    current = make_cpu_project(approved_project)
    scheduler = Scheduler(episode_store(approved_project, 1))
    tasks = plan_tasks(current, scheduler)
    assert all(r.status == "complete" for r in scheduler.run(tasks))
    path = approved_project.artifacts_dir / "visuals" / "vis" / "room.png"
    path.write_bytes(b"changed outside manifest")
    results = scheduler.run(tasks)
    assert all(r.status == "failed" for r in results if r.stage == "tier0")
    assert all(r.status == "blocked" for r in results if r.stage == "assembly")

@pytest.mark.skipif(not (have_tool("ffmpeg") and have_tool("ffprobe")), reason="media tools missing")
def test_f05_assemble_refuses_longer_speech(approved_project, tmp_path):
    current = make_cpu_project(approved_project)
    video = make_clip(tmp_path / "one.mp4", 0.5)
    speech = approved_project.artifacts_dir / "audio" / "hi_1.wav"
    with pytest.raises(TaskFailed, match="refusing speech truncation"):
        assemble([video], tmp_path / "out.mp4", speech)

def test_process_kill_resume_matches_clean_output_hashes(tmp_path):
    store = tmp_path / "interrupted"
    marker = tmp_path / "ready"
    code = """
import sys,time
from pathlib import Path
from granthstudio.scheduler import Scheduler,Task
store,marker=map(Path,sys.argv[1:])
def first(work):
    (work/'out.bin').write_bytes(b'first');return {'out':'out.bin'}
def second(work):
    (work/'partial.bin').write_bytes(b'partial');marker.write_text('ready');time.sleep(20)
Scheduler(store).run([Task('tier0','first',{},'v',first),Task('tier0','second',{},'v',second)])
"""
    child = subprocess.Popen([sys.executable, "-c", code, str(store), str(marker)])
    try:
        deadline = time.monotonic() + 10
        while not marker.exists() and child.poll() is None and time.monotonic() < deadline:
            time.sleep(0.02)
        assert marker.exists(), "child did not reach interrupted task"
        child.kill(); child.wait(timeout=5)
    finally:
        if child.poll() is None: child.kill(); child.wait(timeout=5)
    tasks = [Task("tier0", "first", {}, "v", write_task(b"first")), Task("tier0", "second", {}, "v", write_task(b"second"))]
    resumed = Scheduler(store)
    assert [r.status for r in resumed.run(tasks)] == ["resumed", "complete"]
    clean = Scheduler(tmp_path / "clean"); clean.run(tasks)
    assert [sha256_file(resumed.task_dir(t) / "out.bin") for t in tasks] == [sha256_file(clean.task_dir(t) / "out.bin") for t in tasks]
    assert not list((store / "tier0").glob(".work-*"))


def synthetic_pilot(compiled):
    """Structure checks only; never a receipt for real pilot execution."""
    shots = []
    for label, tier in zip("ABCDEF", (0, 1, 2, 1, 1, 0)):
        shot = copy.deepcopy(compiled["shots"][0])
        shot.update(shot_id=f"synthetic_{label}", pilot_shot=label, tier=tier,
                    lighting="night" if label == "E" else "day_indoor")
        shots.append(shot)
    return {**compiled, "shots": shots}

def test_f10_pilot_requires_comparable_characters_and_lighting(approved_project):
    from granthstudio.pilot import plan_pilot
    pilot = synthetic_pilot(bundle(approved_project).compiled)
    assert set(plan_pilot(pilot)) == set("ABCDEF")
    pilot["shots"][2]["visual_id"] = "vis_other"
    with pytest.raises(ConfigError, match="same scene"):
        plan_pilot(pilot)
    pilot = synthetic_pilot(bundle(approved_project).compiled)
    pilot["shots"][4]["lighting"] = "day_indoor"
    with pytest.raises(ConfigError, match="different specified lighting"):
        plan_pilot(pilot)

def test_f07_changed_node_revision_and_disabled_flf_are_rejected(project, tmp_path):
    models = runtime_models(project, tmp_path)
    models["ltx"]["runtime"]["node_pack_commit"] = "d" * 40
    with pytest.raises(CapabilityDisabled, match="benchmark receipt"):
        require_capability(models, "i2v", project.benchmarks_dir, "workflow-one")
    with pytest.raises(CapabilityDisabled):
        require_capability(models, "flf", project.benchmarks_dir, "workflow-one")

@pytest.mark.skipif(not (have_tool("ffmpeg") and have_tool("ffprobe")), reason="media tools missing")
def test_real_cpu_process_recovery_matches_clean_bilingual_media(approved_project, tmp_path, record_testsuite_property):
    current = make_cpu_project(approved_project)
    store = tmp_path / "interrupted-media"
    marker = tmp_path / "media-ready"
    code = """
import sys,time
from pathlib import Path
from granthstudio.config import load_project,load_models
from granthstudio.pipeline import load_bundle,plan_tasks
from granthstudio.scheduler import Scheduler
root,store,marker=map(Path,sys.argv[1:])
project=load_project(root)
scheduler=Scheduler(store)
bundle=load_bundle(project,load_models(project),1)
tasks=plan_tasks(bundle,scheduler)
target=[task for task in tasks if task.stage=='tier0'][1]
def stop(work):
    (work/'partial.mp4').write_bytes(b'partial');marker.write_text('ready');time.sleep(20)
target.run=stop
scheduler.run(tasks)
"""
    child = subprocess.Popen([sys.executable, "-c", code, str(approved_project.root), str(store), str(marker)])
    try:
        deadline = time.monotonic() + 10
        while not marker.exists() and child.poll() is None and time.monotonic() < deadline:
            time.sleep(0.02)
        assert marker.exists(), "child did not reach second motion task"
        child.kill(); child.wait(timeout=5)
    finally:
        if child.poll() is None: child.kill(); child.wait(timeout=5)
    interrupted = Scheduler(store)
    tasks = plan_tasks(current, interrupted)
    results = interrupted.run(tasks)
    assert [r.status for r in results if r.stage == "tier0"] == ["resumed", "complete"]
    assert all(r.status in ("resumed", "complete") for r in results), results
    clean = Scheduler(tmp_path / "clean-media")
    clean_tasks = plan_tasks(current, clean)
    assert all(r.status == "complete" for r in clean.run(clean_tasks))
    for lang, name in (("mr", "marathi"), ("hi", "hindi")):
        task = next(t for t in tasks if t.name == f"assemble_{lang}")
        clean_task = next(t for t in clean_tasks if t.name == f"assemble_{lang}")
        filename = f"adhyay_01_{name}.mp4"
        recovered_hash = sha256_file(interrupted.task_dir(task) / filename)
        clean_hash = sha256_file(clean.task_dir(clean_task) / filename)
        assert recovered_hash == clean_hash
        record_testsuite_property(f"{lang}_recovered_sha256", recovered_hash)
        record_testsuite_property(f"{lang}_clean_sha256", clean_hash)
    record_testsuite_property("real_process_media_recovery", "passed")
    assert not list((store / "tier0").glob(".work-*"))


@pytest.mark.parametrize("change", ["invented_motion", "omit_required_action"])
def test_f03_motion_cannot_invent_or_omit_source_actions(approved_project, change):
    path = approved_project.episodes_dir / "adhyay_01" / "manifest.yaml"
    manifest = load_yaml(path)
    shot = manifest["scenes"][0]["shots"][1]
    if change == "invented_motion": shot["motion_prompt"] = "invent a different event"
    else: shot["action_ids"] = []
    atomic_write_json(path, manifest)
    with pytest.raises(GateFailure, match="approved action"):
        compile_project(approved_project)

def test_f10_malformed_approval_cannot_authorize_production(approved_project):
    path = approved_project.root / "approvals" / "adhyay_01.json"
    atomic_write_json(path, {"approved": True, "reviewed_by": None})
    assert production_problems(bundle(approved_project))


def test_f01_model_pin_invalidates_motion_and_assembly_only(approved_project):
    scheduler = Scheduler(episode_store(approved_project, 1))
    before = {t.name: t.task_id() for t in plan_tasks(bundle(approved_project), scheduler)}
    path = approved_project.root / "config" / "models.yaml"
    models = load_yaml(path); models["ltx"]["checkpoint_sha256"] = "d" * 64
    atomic_write_json(path, models)
    after = {t.name: t.task_id() for t in plan_tasks(bundle(approved_project), scheduler)}
    assert before["a01_s01_sh01"] == after["a01_s01_sh01"]
    assert before["a01_s01_sh02"] != after["a01_s01_sh02"]
    assert before["assemble_mr"] != after["assemble_mr"]
    assert before["assemble_hi"] != after["assemble_hi"]

def test_f11_receipt_cannot_claim_an_external_output(tmp_path):
    scheduler = Scheduler(tmp_path / "store")
    task = Task("tier0", "clip", {}, "v", write_task(b"one"))
    scheduler.run([task])
    receipt_path = scheduler.task_dir(task) / RECEIPT
    receipt = read_json(receipt_path)
    external = tmp_path / "outside.bin"; external.write_bytes(b"outside")
    receipt["outputs"]["out"] = {"path": str(external), "sha256": sha256_file(external)}
    atomic_write_json(receipt_path, receipt)
    assert scheduler.status([task])[0].status == "missing"

def test_f10_authorization_contract_allows_explicit_flf_no_go(approved_project, monkeypatch):
    """Isolated policy test; fake runtime evidence here is never real GPU validation."""
    from types import SimpleNamespace
    import granthstudio.pipeline as pipeline
    from tests.test_claude_findings import prepare_current_pilot, synthetic_recovery
    current = prepare_current_pilot(approved_project)
    current.models["ltx"]["capabilities"]["flf"] = "disabled"
    # The actual source configuration remains unvalidated. This unit test isolates policy.
    monkeypatch.setattr(pipeline, "_ltx_preflight", lambda *_: SimpleNamespace(version="synthetic-graph"))
    monkeypatch.setattr(pipeline, "require_capability", lambda *_: {"runtime_sha256": "a" * 64})
    pilot_path = approved_project.benchmarks_dir / "synthetic-pilot.json"
    atomic_write_json(pilot_path, load_bundle(approved_project, current.models, 1).compiled)
    refs = []
    for label, capability in zip("ABCDEF", ("tier0", "i2v", "flf", "i2v", "i2v", "assembly")):
        receipt = {"schema_version": 1, "capability": capability, "shot": label, "checkpoint_sha256": None,
            "workflow_version": "synthetic-graph", "runtime_sha256": "a" * 64, "gpu": "T4", "gpu_count": 1,
            "gpu_seconds_total": 60, "attempts": 1, "video_seconds": 2, "accepted": label != "C",
            "outcome": "fail" if label == "C" else "pass", "recorded_at": FIXED_TIME,
            "pilot_plan_sha256": sha256_file(pilot_path)}
        path = approved_project.benchmarks_dir / f"synthetic-{label}.json"
        atomic_write_json(path, receipt)
        refs.append({"path": path.name, "sha256": sha256_file(path)})
    recovery_path = approved_project.benchmarks_dir / "synthetic-recovery.json"
    atomic_write_json(recovery_path, synthetic_recovery(approved_project, sha256_file(pilot_path)))
    approval = {"schema_version": 1, "adhyay": current.adhyay, "approved": True, "reviewed_by": "synthetic-test-only",
        "input_sha256": sha256_obj(pipeline.snapshot(current)), "pilot_receipts": refs,
        "pilot_plan": {"path": pilot_path.name, "sha256": sha256_file(pilot_path)},
        "recovery_evidence": {"path": recovery_path.name, "sha256": sha256_file(recovery_path)},
        "minimum_accepted_sec_per_gpu_hour": 1, "flf_decision": "no_go"}
    path = approved_project.root / "approvals" / f"adhyay_{current.adhyay:02d}.json"
    atomic_write_json(path, approval)
    assert production_problems(current) == []
    # Stale GO and relabelled evidence must still fail.
    approval["input_sha256"] = "b" * 64; atomic_write_json(path, approval)
    assert any("stale" in p for p in production_problems(current))
    approval["input_sha256"] = sha256_obj(pipeline.snapshot(current))
    receipt_path = approved_project.benchmarks_dir / "synthetic-B.json"
    receipt = read_json(receipt_path); receipt["capability"] = "assembly"; atomic_write_json(receipt_path, receipt)
    approval["pilot_receipts"][1]["sha256"] = sha256_file(receipt_path); atomic_write_json(path, approval)
    assert any("capability mismatch" in p for p in production_problems(current))
