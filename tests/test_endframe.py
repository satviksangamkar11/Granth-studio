"""Frozen section 7 Tier 2: the end keyframe derives from the start image (workflow NOT VALIDATED until selected)."""
from __future__ import annotations

import copy

import pytest

from granthstudio import keyframes as kf
from granthstudio.config import load_models, load_yaml
from granthstudio.errors import GateFailure, IntegrationUnavailable
from granthstudio.integrity import atomic_write_json, sha256_file
from granthstudio.pipeline import episode_store, load_bundle, plan_tasks
from granthstudio.scheduler import Scheduler
from tests.conftest import have_tool
from tests.test_keyframes import add_keyframe_visual, approve_references, comfy, configure_sdxl, write_registry  # noqa: F401

pytestmark = pytest.mark.skipif(not (have_tool("ffmpeg") and have_tool("ffprobe")), reason="media tools missing")


def _bundle(project):
    return load_bundle(project, load_models(project), 1)


def _request(project, vid):
    bundle = _bundle(project)
    return kf.keyframe_request(bundle.compiled, bundle.canon, kf.load_registry(project, bundle.canon), bundle.models, vid)


def make_end(project, keyframe_start=False):
    """sh02 becomes a Tier 2 shot ending on keyframe visual vis_end."""
    if keyframe_start:
        add_keyframe_visual(project)
    path = project.episodes_dir / "adhyay_01" / "manifest.yaml"
    manifest = load_yaml(path)
    manifest["visuals"].append({"visual_id": "vis_end", "source": "keyframe", "path": "kf/vis_end.png", "sha256": None})
    shot = manifest["scenes"][0]["shots"][1]
    shot.update(tier=2, end_visual_id="vis_end")
    if keyframe_start:
        shot["visual_id"] = "vis_kf"
    atomic_write_json(path, manifest)


@pytest.fixture
def end_project(approved_project, tmp_path, comfy):  # noqa: F811
    write_registry(approved_project)
    approve_references(approved_project, tmp_path)
    configure_sdxl(approved_project, tmp_path, comfy)
    graph = {"_status": "validated", "_output_node": "9",
             "1": {"class_type": "SyntheticLoader", "inputs": {"ckpt_name": "sdxl_synth.safetensors", "text": "{{PROMPT}}",
                   "neg": "{{NEGATIVE_PROMPT}}", "seed": "{{SEED}}", "w": "{{WIDTH}}", "h": "{{HEIGHT}}",
                   "start": "{{START_IMAGE}}", "r1": "{{REFERENCE_IMAGE_1}}", "r2": "{{REFERENCE_IMAGE_2}}",
                   "r3": "{{REFERENCE_IMAGE_3}}"}},
             "9": {"class_type": "SyntheticSave", "inputs": {"images": ["1", 0]}}}
    atomic_write_json(approved_project.root / "workflows" / "comfyui" / "sdxl_endframe.json", graph)
    return approved_project


def test_end_request_derives_from_file_start_and_start_hash_is_unchanged(end_project):
    make_end(end_project)
    end = _request(end_project, "vis_end")
    bundle = _bundle(end_project)
    room = next(v for v in bundle.compiled["visuals"] if v["visual_id"] == "vis_room_still")
    assert end["derived_from"] == {"visual_id": "vis_room_still", "kind": "file", "path": room["path"], "sha256": room["sha256"]}
    assert end["role"] == "end" and not end["missing_references"] and end == _request(end_project, "vis_end")
    add_keyframe_visual(end_project)
    assert "derived_from" not in _request(end_project, "vis_kf")  # start requests are unchanged


def test_keyframe_start_needs_approval_and_changes_end_hash(end_project, tmp_path):
    make_end(end_project, keyframe_start=True)
    before = _request(end_project, "vis_end")
    assert "start_image:vis_kf" in before["missing_references"] and before["derived_from"]["sha256"] is None
    with pytest.raises(GateFailure, match="no approved start image"):
        kf.require_references(before, load_models(end_project))
    # generate + register + approve the start keyframe for its exact request
    start = _request(end_project, "vis_kf")
    image = tmp_path / "start.png"; image.write_bytes(b"start image one")
    bundle = _bundle(end_project)
    asset = kf.import_asset(end_project, bundle.canon, start["asset_id"], "keyframe", None, "vis_kf", "start", image)
    registry = kf.load_registry(end_project, bundle.canon)
    next(a for a in registry["assets"] if a["asset_id"] == asset["asset_id"])["request_sha256"] = start["request_sha256"]
    kf.save_registry(end_project, registry)
    kf.approve_asset(end_project, bundle.canon, asset["asset_id"], 1, "synthetic-test-only")
    after = _request(end_project, "vis_end")
    assert after["missing_references"] == [] and after["derived_from"]["kind"] == "keyframe"
    assert after["derived_from"]["sha256"] == sha256_file(image) and after["request_sha256"] != before["request_sha256"]
    # a re-approved, different start image changes the end request
    image.write_bytes(b"start image two")
    again = kf.import_asset(end_project, bundle.canon, start["asset_id"], "keyframe", None, "vis_kf", "start", image)
    registry = kf.load_registry(end_project, bundle.canon)
    next(a for a in registry["assets"] if a["asset_id"] == start["asset_id"] and a["version"] == again["version"])["request_sha256"] = start["request_sha256"]
    kf.save_registry(end_project, registry)
    kf.approve_asset(end_project, bundle.canon, start["asset_id"], again["version"], "synthetic-test-only")
    assert _request(end_project, "vis_end")["request_sha256"] not in (before["request_sha256"], after["request_sha256"])
    # pipeline: the end keyframe task depends on the start keyframe task
    tasks = {t.name: t for t in plan_tasks(_bundle(end_project), Scheduler(episode_store(end_project, 1)))}
    assert tasks["keyframe_vis_kf"].task_id() in tasks["keyframe_vis_end"].depends_on


def test_unselected_edit_workflow_is_not_validated(end_project):
    make_end(end_project)
    models = load_models(end_project); models["sdxl"]["edit_workflow_template"] = None
    atomic_write_json(end_project.root / "config" / "models.yaml", models)
    request = _request(end_project, "vis_end")
    with pytest.raises(IntegrationUnavailable, match="end-frame derivation workflow not selected"):
        kf.sdxl_generate(end_project, load_models(end_project), request, end_project.root / "j.json", end_project.root)
    # the plain keyframe workflow is never used as a fallback
    kf.sdxl_preflight(end_project, load_models(end_project))


def test_end_keyframe_generation_posts_start_image(end_project, comfy, tmp_path):  # noqa: F811
    make_end(end_project)
    work = tmp_path / "work"; work.mkdir()
    request = _request(end_project, "vis_end")
    out = kf.sdxl_generate(end_project, load_models(end_project), request, tmp_path / "journal.json", work)
    assert (work / out["image"]).is_file() and len(comfy.posts) == 1
    posted = comfy.posts[0]["prompt"]["1"]["inputs"]["start"]
    assert posted == str(kf.derived_file(end_project, request["derived_from"])) and posted.endswith("room.png")


def test_two_start_visuals_for_one_end_visual_fail(end_project):
    make_end(end_project)
    bundle = _bundle(end_project)
    compiled = copy.deepcopy(bundle.compiled)
    other = copy.deepcopy(next(s for s in compiled["shots"] if s["shot_id"] == "a01_s01_sh01"))
    other.update(visual_id="vis_other", end_visual_id="vis_end")
    compiled["shots"].append(other)
    with pytest.raises(GateFailure, match="exactly one start visual"):
        kf.keyframe_request(compiled, bundle.canon, kf.load_registry(end_project, bundle.canon), bundle.models, "vis_end")
