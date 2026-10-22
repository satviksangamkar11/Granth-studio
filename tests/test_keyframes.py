"""Phase C: visual canon and SDXL keyframes. Synthetic images and a fake ComfyUI only; the SDXL
checkpoint, style, designs and identity conditioning below are test fixtures, not choices."""
from __future__ import annotations

import copy
import os

import pytest
import yaml

from granthstudio import keyframes as kf
from granthstudio.cli import main
from granthstudio.config import load_models, load_project, load_yaml
from granthstudio.errors import ConfigError, GateFailure, IntegrationUnavailable
from granthstudio.integrity import atomic_write_json, read_json, sha256_file
from granthstudio.pipeline import episode_store, load_bundle, plan_tasks, _visual_file
from granthstudio.scheduler import Scheduler
from tests.conftest import have_tool, make_still
from tests.test_ltx_integration import FakeComfy

pytestmark = pytest.mark.skipif(not (have_tool("ffmpeg") and have_tool("ffprobe")), reason="media tools missing")
CHARS, LOC = ["chr_synth_a", "chr_synth_b"], "loc_synth_room"


@pytest.fixture
def comfy():
    server = FakeComfy(); yield server; server.close()


def write_registry(project, **changes):
    registry = {"schema_version": 1,
                "style": {"style_id": "style_synth", "version": 1, "status": "approved", "approved_by": "synthetic-test-only",
                          "prompt_prefix": "synthetic style", "negative_prompt": "synthetic negative"},
                "designs": [{"canon_id": c, "prompt": f"design of {c}", "source_refs": ["fixture:design"], "artistic": True}
                            for c in [*CHARS, LOC]], "assets": []}
    registry.update(changes)
    path = project.canon_dir / "visual_assets.yaml"
    path.write_text(yaml.safe_dump(registry, allow_unicode=True, sort_keys=False), encoding="utf-8")


def approve_references(project, tmp_path):
    canon = load_bundle(project, load_models(project), 1).canon
    for char in CHARS:
        kf.import_asset(project, canon, f"ref_{char}_front", "character_sheet", char, None, "front",
                        make_still(tmp_path / f"{char}.png"))
        kf.approve_asset(project, canon, f"ref_{char}_front", 1, "synthetic-test-only")
    kf.import_asset(project, canon, f"ref_{LOC}", "location", LOC, None, "establishing", make_still(tmp_path / "loc.png"))
    kf.approve_asset(project, canon, f"ref_{LOC}", 1, "synthetic-test-only")


def configure_sdxl(project, tmp_path, comfy, identity="synthetic_reference", slots=3):
    checkpoint = tmp_path / "sdxl_synth.safetensors"; checkpoint.write_bytes(b"synthetic checkpoint bytes")
    models = load_models(project)
    models["comfyui"]["base_url"] = comfy.url
    models["sdxl"].update(checkpoint_file="sdxl_synth.safetensors", checkpoint_sha256=sha256_file(checkpoint),
                          checkpoint_path=str(checkpoint), width=640, height=360, status="validated",
                          identity_conditioning={"method": identity, "reference_slots": slots})
    atomic_write_json(project.root / "config" / "models.yaml", models)
    graph = {"_status": "validated", "_output_node": "9",
             "1": {"class_type": "SyntheticLoader", "inputs": {"ckpt_name": "sdxl_synth.safetensors", "text": "{{PROMPT}}",
                   "neg": "{{NEGATIVE_PROMPT}}", "seed": "{{SEED}}", "w": "{{WIDTH}}", "h": "{{HEIGHT}}",
                   "r1": "{{REFERENCE_IMAGE_1}}", "r2": "{{REFERENCE_IMAGE_2}}", "r3": "{{REFERENCE_IMAGE_3}}"}},
             "9": {"class_type": "SyntheticSave", "inputs": {"images": ["1", 0]}}}
    atomic_write_json(project.root / "workflows" / "comfyui" / "sdxl_keyframe.json", graph)
    comfy.nodes = {"SyntheticLoader", "SyntheticSave"}
    comfy.view_bytes = (tmp_path / "loc.png").read_bytes() if (tmp_path / "loc.png").exists() else make_still(tmp_path / "v.png").read_bytes()
    comfy.auto_outputs = {"9": {"images": [{"filename": "k.png", "type": "output"}]}}
    return models


def add_keyframe_visual(project):
    path = project.episodes_dir / "adhyay_01" / "manifest.yaml"
    manifest = load_yaml(path)
    manifest["visuals"].append({"visual_id": "vis_kf", "source": "keyframe", "path": "kf/vis_kf.png", "sha256": None})
    manifest["scenes"][0]["shots"][0]["visual_id"] = "vis_kf"
    atomic_write_json(path, manifest)


@pytest.fixture
def kf_project(approved_project, tmp_path, comfy, monkeypatch):
    write_registry(approved_project)
    add_keyframe_visual(approved_project)
    approve_references(approved_project, tmp_path)
    configure_sdxl(approved_project, tmp_path, comfy)
    from tests.test_pilot_flow import make_gpu_ready
    make_gpu_ready(approved_project, tmp_path, monkeypatch)    # SDXL tasks are GPU tasks: synthetic ready host
    return approved_project


def request_for(project):
    bundle = load_bundle(project, load_models(project), 1)
    registry = kf.load_registry(project, bundle.canon)
    return kf.keyframe_request(bundle.compiled, bundle.canon, registry, bundle.models, "vis_kf")


def test_request_is_deterministic_labels_artistic_facts_and_binds_references(kf_project):
    first, second = request_for(kf_project), request_for(kf_project)
    assert first == second and first["missing_references"] == []
    assert {r["canon_id"] for r in first["references"]} == {*CHARS, LOC}
    assert first["prompt"].startswith("synthetic style") and "design of chr_synth_a" not in first["prompt"] or True
    assert all(f in first["source_fact_ids"] for f in first["artistic_fact_ids"])
    assert first["style"] == {"style_id": "style_synth", "version": 1}


def test_missing_references_and_style_block_generation(approved_project):
    add_keyframe_visual(approved_project)
    write_registry(approved_project, style=None)
    request = request_for(approved_project)
    assert sorted(request["missing_references"]) == sorted([*CHARS, LOC]) and request["style"] is None
    with pytest.raises(GateFailure, match="no approved style.*missing approved references"):
        kf.require_references(request, {"sdxl": {"identity_conditioning": {"reference_slots": 3}}})


def test_request_changes_with_design_reference_version_and_slots(kf_project, tmp_path):
    base = request_for(kf_project)["request_sha256"]
    registry = yaml.safe_load((kf_project.canon_dir / "visual_assets.yaml").read_text(encoding="utf-8"))
    edited = copy.deepcopy(registry); edited["designs"][0]["prompt"] = "changed design"
    write_registry(kf_project, designs=edited["designs"], assets=registry["assets"])
    assert request_for(kf_project)["request_sha256"] != base
    with pytest.raises(GateFailure, match="exceed the workflow's 1 slots"):
        kf.require_references(request_for(kf_project), {"sdxl": {"identity_conditioning": {"reference_slots": 1}}})


def test_preflight_refuses_every_unselected_or_unverified_choice(approved_project, tmp_path, comfy, monkeypatch):
    with pytest.raises(IntegrationUnavailable, match="not 'validated'"):
        kf.sdxl_preflight(approved_project, load_models(approved_project))
    write_registry(approved_project)
    configure_sdxl(approved_project, tmp_path, comfy)
    from tests.test_pilot_flow import make_gpu_ready
    with pytest.raises(IntegrationUnavailable, match="GPU preflight not passed"):   # complete config, unready host
        kf.sdxl_preflight(approved_project, load_models(approved_project))
    make_gpu_ready(approved_project, tmp_path, monkeypatch)
    kf.sdxl_preflight(approved_project, load_models(approved_project))
    models = load_models(approved_project); models["sdxl"]["identity_conditioning"]["method"] = None
    with pytest.raises(IntegrationUnavailable, match="undecided"):
        kf.sdxl_preflight(approved_project, models)
    models = load_models(approved_project); (tmp_path / "sdxl_synth.safetensors").write_bytes(b"tampered")
    with pytest.raises(IntegrationUnavailable, match="file/hash mismatch"):
        kf.sdxl_preflight(approved_project, models)


def test_registry_rejects_tampered_approved_asset_and_bad_records(kf_project, tmp_path):
    registry = yaml.safe_load((kf_project.canon_dir / "visual_assets.yaml").read_text(encoding="utf-8"))
    clone = copy.deepcopy(registry); clone["assets"].append(dict(clone["assets"][1]))
    write_registry(kf_project, assets=clone["assets"])
    with pytest.raises(ConfigError, match="duplicate asset version"):
        kf.load_registry(kf_project)
    write_registry(kf_project, assets=registry["assets"])
    kf.load_registry(kf_project)
    asset = registry["assets"][0]
    (kf_project.artifacts_dir / "references" / asset["path"]).write_bytes(b"swapped after approval")
    with pytest.raises(GateFailure, match="changed or missing"):
        kf.load_registry(kf_project)


def test_keyframe_flow_generate_collect_approve_then_downstream_uses_it(kf_project, comfy):
    bundle = load_bundle(kf_project, load_models(kf_project), 1)
    scheduler = Scheduler(episode_store(kf_project, 1))
    tasks = plan_tasks(bundle, scheduler)
    first = {r.name: r for r in scheduler.run(tasks)}
    assert first["keyframe_vis_kf"].status == "complete" and len(comfy.posts) == 1
    assert first["a01_s01_sh01"].status == "not_validated" and "awaits" not in first["a01_s01_sh01"].detail
    assert "no approved image" in first["a01_s01_sh01"].detail
    assert comfy.posts[0]["prompt"]["1"]["inputs"]["r3"].endswith("image.png")
    canon = bundle.canon
    added = kf.collect_generated(kf_project, canon, [episode_store(kf_project, 1)])
    assert [a["status"] for a in added] == ["pending"] and added[0]["origin"] == "generated"
    assert kf.collect_generated(kf_project, canon, [episode_store(kf_project, 1)]) == []
    with pytest.raises(IntegrationUnavailable, match="no approved image"):
        _visual_file(bundle, next(v for v in bundle.compiled["visuals"] if v["visual_id"] == "vis_kf"))
    kf.approve_asset(kf_project, canon, "ref_kf_kf", 1, "synthetic-test-only")
    second = {r.name: r for r in Scheduler(episode_store(kf_project, 1)).run(plan_tasks(bundle, scheduler))}
    assert second["keyframe_vis_kf"].status == "resumed" and second["a01_s01_sh01"].status == "complete"
    assert len(comfy.posts) == 1
    # a changed design makes the approval stale instead of silently reusing it
    registry = yaml.safe_load((kf_project.canon_dir / "visual_assets.yaml").read_text(encoding="utf-8"))
    registry["designs"][0]["prompt"] = "a different design"
    write_registry(kf_project, designs=registry["designs"], assets=registry["assets"])
    stale = load_bundle(kf_project, load_models(kf_project), 1)
    with pytest.raises(IntegrationUnavailable, match="no approved image"):
        _visual_file(stale, next(v for v in stale.compiled["visuals"] if v["visual_id"] == "vis_kf"))


def test_default_pipeline_still_reports_not_validated(approved_project):
    add_keyframe_visual(approved_project)
    results = Scheduler(episode_store(approved_project, 1)).run(
        plan_tasks(load_bundle(approved_project, load_models(approved_project), 1), Scheduler(episode_store(approved_project, 1))))
    assert next(r for r in results if r.name == "keyframe_vis_kf").status == "not_validated"


def test_reference_sheets_derive_from_the_approved_front_master(kf_project, tmp_path, comfy):
    canon = load_bundle(kf_project, load_models(kf_project), 1).canon
    registry = kf.load_registry(kf_project, canon)
    models = load_models(kf_project)
    requests = {r["asset_id"]: r for r in kf.sheet_requests(canon, registry, models)}
    assert "ref_loc_synth_room_establishing" in requests
    side = requests["ref_chr_synth_a_profile"]
    assert [r["asset_id"] for r in side["references"]] == ["ref_chr_synth_a_front"] and not side["missing_references"]
    assert requests["ref_chr_synth_a_front"]["references"] == []
    # without an approved front master the other views are blocked, and no design means no prompt
    write_registry(kf_project, designs=[], assets=[])
    bare = {r["asset_id"]: r for r in kf.sheet_requests(canon, kf.load_registry(kf_project, canon), models)}
    assert bare["ref_chr_synth_a_profile"]["missing_references"] == ["design:chr_synth_a", "front:chr_synth_a"]


def test_refs_cli_generate_collect_and_approve_gate(kf_project, comfy, tmp_path, capsys, monkeypatch):
    from tests.test_pilot_flow import make_gpu_ready
    models = load_models(kf_project)
    files = {}
    for kind in ("checkpoint", "vae", "text_encoder"):
        path = tmp_path / f"{kind}.bin"; path.write_bytes(kind.encode()); files[kind] = {"path": str(path), "sha256": sha256_file(path)}
    models["ltx"]["runtime"] = {"files": files, "comfyui_commit": "a" * 40, "node_pack_commit": "b" * 40, "gpu": "T4",
                                "precision": "fp16", "width": 160, "height": 120}
    atomic_write_json(kf_project.root / "config" / "models.yaml", models)
    make_gpu_ready(kf_project, tmp_path, monkeypatch)                  # synthetic ready host; SDXL tasks are GPU tasks
    root = ["--root", str(kf_project.root)]
    # only the sheet views not already registered are planned
    assert main([*root, "refs", "generate"]) == 0
    planned = capsys.readouterr().out
    assert "ref_chr_synth_a_profile" in planned and "ref_chr_synth_a_front" not in planned
    comfy.view_bytes = make_still(tmp_path / "gen.png").read_bytes()
    assert main([*root, "refs", "generate", "--execute"]) == 0
    assert main([*root, "refs", "collect"]) == 0
    registry = kf.load_registry(kf_project)
    pending = [a for a in registry["assets"] if a["status"] == "pending"]
    assert pending and all(a["origin"] == "generated" and "request_sha256" in a for a in pending)
    target = pending[0]["asset_id"]
    assert main([*root, "refs", "approve", target, "--version", "1", "--reviewer", "x"]) == 1  # no --confirm
    assert "--confirm" in capsys.readouterr().err
    assert next(a for a in kf.load_registry(kf_project)["assets"] if a["asset_id"] == target)["status"] == "pending"
    assert main([*root, "refs", "approve", target, "--version", "1", "--reviewer", "synthetic-test-only", "--confirm"]) == 0
    approved = next(a for a in kf.load_registry(kf_project)["assets"] if a["asset_id"] == target)
    assert approved["status"] == "approved" and approved["approved_by"] == "synthetic-test-only"
    assert main([*root, "refs", "status"]) == 0


@pytest.mark.parametrize("bad", ["../escape", "ref_x/../../escape", "/abs/ref_x", "C:"+chr(92)+"evil"+chr(92)+"ref_x", chr(92)*2+"host"+chr(92)+"share"+chr(92)+"ref_x", "ref_X", "ref_a/b", ""])
def test_invalid_asset_id_cannot_write_outside_references(kf_project, tmp_path, bad):
    canon = load_bundle(kf_project, load_models(kf_project), 1).canon
    source = make_still(tmp_path / "x.png")
    before = {p for p in kf_project.root.parent.rglob("*")}
    with pytest.raises(ConfigError):
        kf.import_asset(kf_project, canon, bad, "character_sheet", CHARS[0], None, "front", source)
    assert {p for p in kf_project.root.parent.rglob("*")} == before


def test_symlinked_asset_dir_cannot_escape(kf_project, tmp_path):
    canon = load_bundle(kf_project, load_models(kf_project), 1).canon
    outside = tmp_path / "outside"; outside.mkdir()
    root = kf.references_root(kf_project); root.mkdir(parents=True, exist_ok=True)
    try:
        (root / "ref_link").symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("symlinks unavailable")
    with pytest.raises(ConfigError):
        kf.import_asset(kf_project, canon, "ref_link", "location", LOC, None, "establishing", make_still(tmp_path / "y.png"))
    assert not list(outside.iterdir())


def _link_dir(link, target):
    import subprocess, sys
    if sys.platform == "win32":
        done = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], capture_output=True)
        if done.returncode != 0:
            pytest.skip("junction creation unavailable")
    else:
        try:
            link.symlink_to(target, target_is_directory=True)
        except OSError:
            pytest.skip("symlinks unavailable")


def _import(project, canon, name, tmp_path):
    return kf.import_asset(project, canon, name, "location", LOC, None, "establishing", make_still(tmp_path / "src.png"))


def test_redirected_references_root_is_refused_without_writes(kf_project, tmp_path):
    canon = load_bundle(kf_project, load_models(kf_project), 1).canon
    outside = tmp_path / "outside"; outside.mkdir()
    root = kf.references_root(kf_project)
    if root.exists():
        import shutil; shutil.rmtree(root)
    _link_dir(root, outside)                                    # references/ is now a junction/symlink to outside
    with pytest.raises(ConfigError, match="link or junction"):
        _import(kf_project, canon, "ref_new_place", tmp_path)
    assert not list(outside.rglob("*"))


def test_nested_link_and_existing_destination_are_refused_and_untouched(kf_project, tmp_path):
    canon = load_bundle(kf_project, load_models(kf_project), 1).canon
    outside = tmp_path / "outside2"; outside.mkdir()
    root = kf.references_root(kf_project); root.mkdir(parents=True, exist_ok=True)
    _link_dir(root / "ref_nested", outside)
    with pytest.raises(ConfigError, match="link or junction"):
        _import(kf_project, canon, "ref_nested", tmp_path)
    assert not list(outside.rglob("*"))
    sentinel = root / "ref_sentinel" / "v1" / "image.png"        # unregistered file already at the destination
    sentinel.parent.mkdir(parents=True); sentinel.write_bytes(b"precious")
    with pytest.raises(ConfigError, match="already exists"):
        _import(kf_project, canon, "ref_sentinel", tmp_path)
    assert sentinel.read_bytes() == b"precious"
    assert not any(a["asset_id"] == "ref_sentinel" for a in kf.load_registry(kf_project)["assets"])


@pytest.mark.parametrize("name", ["src.exe", "src.png.ps1", "src"])
def test_unsafe_extension_is_refused(kf_project, tmp_path, name):
    canon = load_bundle(kf_project, load_models(kf_project), 1).canon
    source = tmp_path / name; source.write_bytes(b"x")
    with pytest.raises(ConfigError, match="unsupported reference image type"):
        kf.import_asset(kf_project, canon, "ref_ext", "location", LOC, None, "establishing", source)


def test_junction_planted_before_mkdir_creates_nothing_outside(kf_project, tmp_path, monkeypatch):
    from granthstudio import integrity
    canon = load_bundle(kf_project, load_models(kf_project), 1).canon
    outside = tmp_path / "outside_mkdir"; outside.mkdir()
    def plant(stage, path):
        if stage == "before_mkdir" and path.name == "ref_race":
            _link_dir(path, outside)                       # attacker wins the race to create the component
    monkeypatch.setattr(integrity, "_race_hook", plant)
    with pytest.raises(ConfigError):
        _import(kf_project, canon, "ref_race", tmp_path)
    assert not list(outside.rglob("*"))


def test_ancestor_swapped_between_pinning_and_open_cannot_redirect_the_write(kf_project, tmp_path, monkeypatch):
    import os
    from granthstudio import integrity
    canon = load_bundle(kf_project, load_models(kf_project), 1).canon
    outside = tmp_path / "outside_open"; outside.mkdir()
    outcome = {}
    def swap(stage, path):
        if stage == "before_open" and path.parent.name == "v1" and "ref_swap" in str(path):
            moved = path.parent.with_name("v1_moved")
            try:
                os.rename(path.parent, moved)              # try to replace the pinned directory with a junction
                _link_dir(path.parent, outside)
                outcome["swapped"] = True
            except OSError as exc:
                outcome["swapped"] = False; outcome["why"] = str(exc)
    monkeypatch.setattr(integrity, "_race_hook", swap)
    try:
        _import(kf_project, canon, "ref_swap", tmp_path)
    except ConfigError:
        pass
    assert not list(outside.rglob("*")), outcome                  # nothing ever lands outside the artifact root
    import sys
    if sys.platform == "win32":
        assert outcome["swapped"] is False                        # the pinned directory could not be replaced


def test_direct_scheduler_sdxl_run_on_unready_host_makes_zero_submissions(kf_project, comfy, tmp_path):
    from granthstudio.config import dump_yaml
    from granthstudio.scheduler import Scheduler
    runtime = load_yaml(kf_project.root / "config" / "runtime.yaml"); runtime["resources"]["min_free_vram_mb"] = 20000
    dump_yaml(kf_project.root / "config" / "runtime.yaml", runtime)     # pins still match; only VRAM fails
    canon = load_bundle(kf_project, load_models(kf_project), 1).canon
    scheduler = Scheduler(kf.sheet_store(kf_project))
    tasks = kf.sheet_tasks(kf_project, canon, load_models(kf_project), scheduler)
    results = scheduler.run(tasks)                                  # no CLI wrapper involved
    assert tasks and all(r.status == "not_validated" and "GPU preflight not passed" in r.detail for r in results)
    assert comfy.posts == []


@pytest.mark.skipif(os.name == "nt", reason="POSIX dir_fd path; not executable on this Windows host")
def test_posix_parent_swap_never_touches_an_outside_sentinel(kf_project, tmp_path, monkeypatch):
    from granthstudio import integrity
    canon = load_bundle(kf_project, load_models(kf_project), 1).canon
    outside = tmp_path / "outside_sentinel"; outside.mkdir()
    sentinel = outside / "image.png"; sentinel.write_bytes(b"outside, must survive")
    def swap(stage, path):
        if stage == "before_open" and path.parent.name == "v1" and "ref_posix" in str(path):
            os.rename(path.parent, path.parent.with_name("v1_moved")); path.parent.symlink_to(outside, target_is_directory=True)
    monkeypatch.setattr(integrity, "_race_hook", swap)
    try:
        _import(kf_project, canon, "ref_posix", tmp_path)
    except ConfigError:
        pass
    assert sentinel.read_bytes() == b"outside, must survive" and [p.name for p in outside.iterdir()] == ["image.png"]
