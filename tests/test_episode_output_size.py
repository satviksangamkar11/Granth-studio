"""R4 (docs/ARCHITECTURE_V3_2_PROPOSAL.md, D-012): one episode output size for every clip, never stretched. Synthetic media only."""
from __future__ import annotations

import subprocess

import pytest

from granthstudio.config import load_models, load_yaml, dump_yaml
from granthstudio.errors import GateFailure
from granthstudio.ffmpeg import conform_clip, conform_filter, probe, still_motion_clip
from granthstudio.pipeline import episode_store, load_bundle, plan_tasks, snapshot, require_current
from granthstudio.scheduler import Scheduler
from tests.conftest import have_tool
from tests.test_review_regressions import make_cpu_project

MEDIA = pytest.mark.skipif(not (have_tool("ffmpeg") and have_tool("ffprobe")), reason="media tools missing")


def set_output(project, output):
    path = project.root / "config" / "runtime.yaml"
    runtime = load_yaml(path)
    if output is None:
        runtime.pop("output", None)
    else:
        runtime["output"] = output
    dump_yaml(path, runtime)


def solid(path, size, color="red", seconds=1):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c={color}:s={size[0]}x{size[1]}:r=24:d={seconds}", "-pix_fmt", "yuv420p", str(path)], check=True)
    return path


def test_conform_filter_never_stretches_and_refuses_an_unknown_fit():
    assert "force_original_aspect_ratio=increase" in conform_filter((320, 214), "cover") and "crop=320:214" in conform_filter((320, 214), "cover")
    assert "force_original_aspect_ratio=decrease" in conform_filter((320, 214), "pad") and "pad=320:214" in conform_filter((320, 214), "pad")
    with pytest.raises(ValueError):
        conform_filter((320, 214), "stretch")


@MEDIA
def test_conform_clip_brings_any_aspect_to_the_exact_size_and_fps(tmp_path):
    for source, fit in (((768, 512), "cover"), ((1280, 720), "cover"), ((1280, 720), "pad"), ((400, 600), "pad")):
        clip = solid(tmp_path / f"s{source[0]}{fit}.mp4", source)
        out = tmp_path / f"o{source[0]}{fit}.mp4"
        conform_clip(clip, out, (320, 214), fit, 24)
        info = probe(out)
        assert (info.width, info.height) == (320, 214) and not info.has_audio and abs(info.duration_s - 1.0) < 0.1


@MEDIA
def test_a_still_with_a_fit_is_cropped_not_stretched(tmp_path):
    image = tmp_path / "wide.png"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=1600x900:rate=1", "-frames:v", "1", str(image)], check=True)
    out = tmp_path / "still.mp4"
    still_motion_clip(image, out, 1.0, fps=24, size=(288, 192), fit="cover")
    assert (probe(out).width, probe(out).height) == (288, 192)
    legacy = tmp_path / "legacy.mp4"
    still_motion_clip(image, legacy, 1.0, fps=24, size=(288, 192))                                 # without a fit the old behaviour is unchanged
    assert (probe(legacy).width, probe(legacy).height) == (288, 192)


@MEDIA
def test_with_an_output_size_every_tier0_clip_and_both_final_videos_have_exactly_that_size(approved_project):
    make_cpu_project(approved_project)
    set_output(approved_project, {"width": 320, "height": 214, "fit": "cover"})
    bundle = load_bundle(approved_project, load_models(approved_project), 1)
    scheduler = Scheduler(episode_store(approved_project, 1))
    tasks = plan_tasks(bundle, scheduler)
    results = scheduler.run(tasks)
    assert all(r.status == "complete" for r in results), results
    for task in tasks:
        if task.stage == "tier0":
            clip = probe(scheduler.task_dir(task) / "clip.mp4")
            assert (clip.width, clip.height) == (320, 214)
        if task.stage == "assembly":
            stem = "adhyay_01_marathi" if task.name.endswith("mr") else "adhyay_01_hindi"
            final = probe(scheduler.task_dir(task) / f"{stem}.mp4")
            assert (final.width, final.height) == (320, 214)


@MEDIA
def test_the_output_size_is_part_of_tier0_and_assembly_identities_only_and_removing_it_restores_the_legacy_ones(approved_project):
    make_cpu_project(approved_project)
    scheduler = Scheduler(episode_store(approved_project, 1))
    legacy = {t.name: t.task_id() for t in plan_tasks(load_bundle(approved_project, load_models(approved_project), 1), scheduler)}
    set_output(approved_project, {"width": 320, "height": 214, "fit": "cover"})
    sized_tasks = plan_tasks(load_bundle(approved_project, load_models(approved_project), 1), scheduler)
    changed = {t.name for t in sized_tasks if t.task_id() != legacy[t.name]}
    assert changed and {t.stage for t in sized_tasks if t.name in changed} <= {"tier0", "assembly"}      # audio and LTX identities do not depend on the picture size
    assert {t.name for t in sized_tasks if t.stage == "assembly"} <= changed and {t.name for t in sized_tasks if t.stage == "tier0"} <= changed
    set_output(approved_project, None)
    tasks = plan_tasks(load_bundle(approved_project, load_models(approved_project), 1), scheduler)
    assert {t.name: t.task_id() for t in tasks} == legacy                                           # the exact legacy identities come back
    results = scheduler.run(tasks)
    assert all(r.status == "complete" for r in results)
    clip = probe(scheduler.task_dir(next(t for t in tasks if t.stage == "tier0")) / "clip.mp4")
    assert (clip.width, clip.height) == (1280, 720)


def test_changing_the_output_size_after_loading_is_caught_by_require_current(approved_project):
    bundle = load_bundle(approved_project, load_models(approved_project), 1)
    require_current(bundle)
    set_output(approved_project, {"width": 320, "height": 214, "fit": "cover"})
    with pytest.raises(GateFailure, match="snapshot changed"):
        require_current(bundle)
    assert snapshot(load_bundle(approved_project, load_models(approved_project), 1))["output"]["width"] == 320


# ---------------------------------------------------------------- R3: a Tier 0 shot may carry an exact camera path

def put_camera(project, camera, shot_index=0, tier=None):
    from granthstudio.integrity import atomic_write_json
    path = project.episodes_dir / "adhyay_01" / "manifest.yaml"
    manifest = load_yaml(path)
    shot = manifest["scenes"][0]["shots"][shot_index]
    shot["camera"] = camera
    if tier is not None:
        shot["tier"] = tier
    atomic_write_json(path, manifest)


MOVE = {"start": {"zoom": 1.0, "cx": 0.5, "cy": 0.5}, "end": {"zoom": 1.4, "cx": 0.40, "cy": 0.45}, "ease": "smooth"}


@MEDIA
def test_a_tier0_shot_with_a_camera_is_rendered_by_the_motion_module_at_the_episode_size(approved_project, tmp_path):
    make_cpu_project(approved_project)
    set_output(approved_project, {"width": 320, "height": 214, "fit": "cover"})
    put_camera(approved_project, MOVE)
    bundle = load_bundle(approved_project, load_models(approved_project), 1)
    scheduler = Scheduler(episode_store(approved_project, 1))
    tasks = plan_tasks(bundle, scheduler)
    results = scheduler.run(tasks)
    assert all(r.status == "complete" for r in results), results
    first_shot = bundle.compiled["shots"][0]["shot_id"]
    clip = scheduler.task_dir(next(t for t in tasks if t.stage == "tier0" and t.name == first_shot)) / "clip.mp4"
    info = probe(clip)
    assert (info.width, info.height) == (320, 214)
    first, last = tmp_path / "f.png", tmp_path / "l.png"
    for index, target in ((0, first), (11, last)):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(clip), "-vf", f"select=eq(n\,{index})", "-frames:v", "1", str(target)], check=True)
    done = subprocess.run(["ffmpeg", "-v", "info", "-i", str(first), "-i", str(last), "-lavfi", "psnr", "-f", "null", "-"], capture_output=True, text=True)
    assert "average:inf" not in done.stderr and "average:" in done.stderr                         # the camera really moved: first and last frame differ


@MEDIA
def test_adding_a_camera_changes_only_that_shot_and_what_depends_on_it(approved_project):
    make_cpu_project(approved_project)
    scheduler = Scheduler(episode_store(approved_project, 1))
    before = {(t.stage, t.name): t.task_id() for t in plan_tasks(load_bundle(approved_project, load_models(approved_project), 1), scheduler)}
    bundle = load_bundle(approved_project, load_models(approved_project), 1)
    first_shot = bundle.compiled["shots"][0]["shot_id"]
    put_camera(approved_project, MOVE, shot_index=0)
    after = {(t.stage, t.name): t.task_id() for t in plan_tasks(load_bundle(approved_project, load_models(approved_project), 1), scheduler)}
    changed = {key for key in before if before[key] != after[key]}
    assert ("tier0", first_shot) in changed
    assert {stage for stage, _ in changed} <= {"tier0", "assembly"}                               # audio identities do not move
    assert {name for stage, name in changed if stage == "tier0"} == {first_shot}                  # the other shots keep their identities


def test_a_camera_is_refused_on_a_motion_shot_and_when_its_window_leaves_the_image(approved_project):
    from granthstudio.errors import ConfigError
    from tests.test_review_regressions import compile_project
    put_camera(approved_project, MOVE, shot_index=1, tier=1)
    with pytest.raises(ConfigError, match="Tier 0"):
        compile_project(approved_project)
    put_camera(approved_project, {"start": {"zoom": 1.0}, "end": {"zoom": 2.0, "cx": 0.95, "cy": 0.5}}, shot_index=0)       # the first shot is Tier 0 and is checked first
    with pytest.raises(ConfigError, match="leaves the image"):
        compile_project(approved_project)
