"""The SDXL first-keyframe harness against a fake ComfyUI: plumbing and refusals only. Nothing here shows that SDXL or IP-Adapter works."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys

import pytest

from tests.conftest import REPO, have_tool, make_still
from tests.test_ltx_integration import FakeComfy

pytestmark = pytest.mark.skipif(not (have_tool("ffmpeg") and have_tool("ffprobe")), reason="media tools missing")
spec = importlib.util.spec_from_file_location("sdxl_first_test", REPO / "scripts" / "sdxl_first_test.py")
sx = importlib.util.module_from_spec(spec); sys.modules["sdxl_first_test"] = sx; spec.loader.exec_module(sx)
T4 = [{"index": 0, "name": "Tesla T4", "memory_total_mb": 15360.0, "memory_used_mb": 100.0, "memory_free_mb": 15260.0}]


@pytest.fixture
def host(tmp_path, monkeypatch):
    import copy
    server = FakeComfy()
    classes = {"CheckpointLoaderSimple", "VAELoader", "CLIPVisionLoader", "IPAdapterModelLoader", "LoadImage", "IPAdapterAdvanced", "CLIPTextEncode", "EmptyLatentImage", "KSampler", "VAEDecode", "SaveImage"}
    server.nodes = classes
    models = tmp_path / "comfy"
    pins = copy.deepcopy(sx.PINS)
    for item in pins["files"]:                                          # tiny stand-in files; the pins are re-pointed at their real hashes for this fake host
        path = models / item["dest_dir"] / item["name"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(f"synthetic {item['name']}".encode())
        item["sha256"] = sx.lt.sha256_file(path)
    monkeypatch.setattr(sx, "PINS", pins)
    def options(*names):
        return {"input": {"required": {key: [[name]] for key, name in names}}}
    files = {i["role"]: i["name"] for i in pins["files"]}
    server.object_info_override = {**{c: {} for c in classes}, "CheckpointLoaderSimple": options(("ckpt_name", files["sdxl_checkpoint"])), "VAELoader": options(("vae_name", files["vae_fp16_fix"])),
                                   "CLIPVisionLoader": options(("clip_name", files["clip_vision"])), "IPAdapterModelLoader": options(("ipadapter_file", files["ip_adapter"]))}
    image = tmp_path / "k.png"
    w, h = pins["workflow"]["size"]
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"testsrc2=size={w}x{h}", "-frames:v", "1", str(image)], check=True, timeout=60)
    server.view_bytes = image.read_bytes()
    server.auto_outputs = {"9": {"images": [{"filename": "k.png", "type": "output"}]}}
    for module in ("runtime",):
        monkeypatch.setattr(f"granthstudio.{module}.gpu_status", lambda: T4)
    monkeypatch.setattr("granthstudio.runtime.ram_available_mb", lambda: 20000)
    monkeypatch.setenv("GRANTHSTUDIO_SESSION_DEADLINE", "2999-01-01T00:00:00+00:00")
    monkeypatch.setenv("LTX_DOWNLOAD_APPROVED", "Satvik Sangamkar")
    reference = make_still(tmp_path / "ref.png")
    yield server, models, tmp_path / "work", reference
    server.close()


def run(host, *extra):
    server, models, work, reference = host
    args = sx.build_parser().parse_args(["--workdir", str(work), "--models-dir", str(models), "--comfy-url", server.url, "--reference-image", str(reference),
                                         "--min-disk-gb", "0.001", *extra])
    code = sx._run(args, enforce_gates=False)
    return code, json.loads((work / "sdxl_receipt.json").read_text(encoding="utf-8"))


def test_dry_run_builds_the_request_from_the_pilot_project_with_the_frozen_style_and_two_provisional_references(host):
    code, receipt = run(host)
    assert code == 1 and receipt["verdict"] == "NOT_RUN" and "dry run" in receipt["reason"] and host[0].posts == []
    request = receipt["request"]
    assert request["style"]["style_id"] == "devotional_gouache_1950s_v1" and request["template_version"] == "keyframe-prompt-v2-frozen-style"
    assert request["prompt"].startswith("1950s vintage Indian devotional book illustration") and "Narrator" not in request["prompt"] and "Gajanan Maharaj" in request["prompt"]
    assert [r["asset_id"] for r in request["references"]] == ["ref_chr_gajanan_maharaj_front", "ref_loc_devidas_house_road"] and request["missing_references"] == []
    assert all("PROVISIONAL external reference" in a["approved_by"] and "Satvik Sangamkar" in a["approved_by"] for a in receipt["reference_assets"])
    assert receipt["reference_image"]["role"].startswith("PROVISIONAL external") and "docs/pilot/SDXL_DOWNLOAD_APPROVAL.md" in receipt["authorization_record"]


def different_image_per_submission(monkeypatch, server, tmp_path):
    """The fake server normally returns one fixed image; here each fetched image differs, as two different generations would."""
    w, h = sx.PINS["workflow"]["size"]
    images = []
    for index, source in enumerate((f"testsrc2=size={w}x{h}", f"smptebars=size={w}x{h}")):
        path = tmp_path / f"gen{index}.png"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", source, "-frames:v", "1", str(path)], check=True, timeout=60)
        images.append(path.read_bytes())
    calls = iter(range(100))
    monkeypatch.setattr(type(server), "view_bytes", property(lambda self: images[(next(calls) // 2) % 2], lambda self, value: None), raising=False)


def test_execute_generates_with_and_without_the_reference_through_the_existing_pipeline(host, monkeypatch, tmp_path):
    server, models, work, _ = host
    different_image_per_submission(monkeypatch, server, tmp_path)
    code, receipt = run(host, "--execute")
    assert receipt["verdict"] == "PASS", receipt["reason"]
    assert receipt["live_check"]["ok"] and "IPAdapterAdvanced" in receipt["live_check"]["node_classes"]
    assert len(server.posts) == 2 and set(receipt["results"]) == {"with_reference", "no_reference_control"}
    graphs = [post["prompt"] if "prompt" in post else post for post in server.posts]
    with_ref, control = graphs
    assert sum(1 for n in with_ref.values() if n["class_type"] == "IPAdapterAdvanced") == 2                    # unused slots were removed from the graph
    assert not any(n["class_type"] in ("IPAdapterAdvanced", "LoadImage") for n in control.values())            # the control is the plain checkpoint
    assert receipt["results"]["with_reference"]["decoded"] == {"width": 1216, "height": 832}
    assert "ssim_with_reference_vs_control" in receipt["reference_influence"]


def test_a_byte_identical_control_means_the_reference_had_no_effect_and_fails(host):
    code, receipt = run(host, "--execute")
    # the fake server returns the same bytes for both submissions, which is exactly the "reference had no effect" signature
    assert receipt["reference_influence"]["identical_bytes"] is True or receipt["verdict"] == "FAIL"
    assert receipt["verdict"] == "FAIL" and "no effect" in receipt["reason"]


def test_a_changed_model_file_stops_everything_before_any_submission(host):
    server, models, work, _ = host
    next(models.rglob("sdxl.vae.safetensors")).write_bytes(b"tampered")
    code, receipt = run(host, "--execute")
    assert code == 1 and receipt["verdict"] == "NOT_RUN" and "SHA-256 differs" in receipt["reason"] and server.posts == []


def test_a_missing_loader_file_or_node_is_not_validated_and_nothing_is_submitted(host):
    server, models, work, _ = host
    server.object_info_override["IPAdapterModelLoader"] = {"input": {"required": {"ipadapter_file": [["something_else.safetensors"]]}}}
    code, receipt = run(host, "--execute")
    assert receipt["verdict"] == "NOT_VALIDATED" and "live node/model check failed" in receipt["reason"] and server.posts == []


def test_the_gates_refuse_without_an_approver_name(host, monkeypatch):
    monkeypatch.delenv("LTX_DOWNLOAD_APPROVED")
    server, models, work, reference = host
    args = sx.build_parser().parse_args(["--workdir", str(work), "--models-dir", str(models), "--comfy-url", server.url, "--reference-image", str(reference), "--execute"])
    assert sx._run(args, enforce_gates=True) == 1
    receipt = json.loads((work / "sdxl_receipt.json").read_text(encoding="utf-8"))
    assert receipt["verdict"] == "NOT_RUN" and "execution gate" in receipt["reason"] and server.posts == []


def test_the_kaggle_script_and_notebook_are_valid_refuse_early_and_stay_unfilled():
    import ast
    script = (REPO / "scripts" / "kaggle" / "sdxl_first_test.sh").read_text(encoding="utf-8")
    assert subprocess.run(["bash", "-n", str(REPO / "scripts" / "kaggle" / "sdxl_first_test.sh")]).returncode == 0
    assert script.index("== 0. refusals") < script.index("git clone") < script.index("curl -L") and "sha256sum -c" in script and 'CUDA_VISIBLE_DEVICES=0 exec' in script
    assert script.index("rev-parse HEAD") < script.index("== 1. host") and "port_owner.py" in script and "gpu_attribution.py" in script
    nb = json.loads((REPO / "notebooks" / "kaggle_sdxl_first_test.ipynb").read_text(encoding="utf-8"))
    code = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]
    for source in code:
        ast.parse(source)
    assert 'APPROVER = ""' in code[0] and 'EXPECTED_COMMIT = ""' in code[0]
    with pytest.raises(AssertionError, match="APPROVER"):
        exec(code[0], {})
    spec2 = importlib.util.spec_from_file_location("build_sdxl_notebook", REPO / "scripts" / "kaggle" / "build_sdxl_notebook.py")
    mod = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(mod)
    assert json.dumps(nb, indent=1) == json.dumps({"cells": [mod.cell(k, s) for k, s in mod.CELLS], "nbformat": 4, "nbformat_minor": 5,
                                                   "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python"}}}, indent=1)


def test_the_pinned_download_list_matches_what_the_script_fetches():
    script = (REPO / "scripts" / "kaggle" / "sdxl_first_test.sh").read_text(encoding="utf-8")
    assert "for i in 0 1 2 3; do fetch" in script and len(sx.PINS["files"]) == 4
    assert all(("path_in_repo" in item) or item["name"] for item in sx.PINS["files"])


def test_the_direct_entry_point_enforces_the_pins_the_clean_tree_the_node_inventory_and_worker_ownership(host, monkeypatch):
    server, models, work, reference = host
    (models / "custom_nodes" / "some_other_pack").mkdir(parents=True)
    monkeypatch.delenv("LTX_EXPECTED_COMMIT", raising=False)
    args = sx.build_parser().parse_args(["--workdir", str(work), "--models-dir", str(models), "--comfy-url", server.url, "--reference-image", str(reference), "--execute"])
    problems = " | ".join(sx.execution_extra_problems(args))
    assert "LTX_EXPECTED_COMMIT is not set" in problems and "not at its pinned commit" in problems                      # the fake checkouts are not the pinned ones
    assert "unapproved entries in custom_nodes: ['some_other_pack']" in problems and "--worker-pid and --gpu-index are required" in problems
    monkeypatch.setenv("LTX_EXPECTED_COMMIT", "0" * 40)
    assert "expected " + "0" * 40 in " | ".join(sx.execution_extra_problems(args))


def test_a_workdir_that_already_holds_a_project_is_refused_so_approvals_never_touch_foreign_files(host):
    first_code, first = run(host)
    again_code, again = run(host)
    assert again["verdict"] == "NOT_RUN" and "fresh --workdir is required" in again["reason"]


def test_a_remote_or_odd_endpoint_is_refused_and_every_custom_node_entry_including_dot_names_is_listed(host):
    server, models, work, reference = host
    for url in ("http://remote-host:8188", "https://127.0.0.1:8188", "http://127.0.0.1:8188/api", "http://127.0.0.1", "http://localhost:8188", "http://user@127.0.0.1:8188", "http://[::1:8188",
                "http://127.0.0.1:65536", "http://127.0.0.1:0", "http://[::1]:8188", "http://127.0.0.1:8188?", "http://127.0.0.1:8188#"):
        args = sx.build_parser().parse_args(["--workdir", str(work), "--models-dir", str(models), "--comfy-url", url, "--reference-image", str(reference), "--worker-pid", "1", "--gpu-index", "0", "--execute"])
        assert any("must be exactly http://127.0.0.1:" in p for p in sx.execution_extra_problems(args)), url
    script = (REPO / "scripts" / "kaggle" / "sdxl_first_test.sh").read_text(encoding="utf-8")
    assert "find \"$COMFY/custom_nodes\" -mindepth 1 -maxdepth 1 -print0 > " in script and ".[!.]*" not in script and "--address 127.0.0.1" in script
    notebook = (REPO / "scripts" / "kaggle" / "build_sdxl_notebook.py").read_text(encoding="utf-8")
    install = notebook.index('"install", "-q"')
    assert notebook.index("MemAvailable") < install and notebook.index("memory.used") < install


def test_scene_3_first_generates_provisional_sheets_for_the_characters_without_a_reference_then_uses_all_five_references(host, monkeypatch, tmp_path):
    server, models, work, _ = host
    different_image_per_submission(monkeypatch, server, tmp_path)
    code, receipt = run(host, "--execute", "--visual", "vis_s3_kf")
    assert receipt["verdict"] == "PASS", receipt["reason"]
    assert receipt["missing_before_sheets"] == ["chr_bankatlal", "chr_damodarpant", "chr_devidas"]
    assert set(receipt["bootstrapped_sheets"]) == {"chr_bankatlal", "chr_damodarpant", "chr_devidas"}
    assert all("PROVISIONAL" in s["asset"]["approved_by"] and "appearance not given in the text" in s["asset"]["approved_by"] for s in receipt["bootstrapped_sheets"].values())
    assert len(server.posts) == 5                                                                   # three sheets, the keyframe with references, the control
    graphs = [post["prompt"] if "prompt" in post else post for post in server.posts]
    sheets, with_ref, control = graphs[:3], graphs[3], graphs[4]
    assert not any(n["class_type"] in ("IPAdapterAdvanced", "LoadImage") for graph in sheets for n in graph.values())      # sheets come from the design prompts alone
    assert sum(1 for n in with_ref.values() if n["class_type"] == "IPAdapterAdvanced") == 5
    assert len(receipt["request"]["references"]) == 5 and receipt["request"]["missing_references"] == []
