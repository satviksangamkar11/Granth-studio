"""The pilot's SDXL + IP-Adapter candidate workflow and its pins: static structure only. NOT a validation: the graph has never run (no checkpoint downloaded, no licence accepted)."""
from __future__ import annotations

import json
import re

import pytest
import yaml

from granthstudio.comfy import load_template, render_graph
from granthstudio.errors import IntegrationUnavailable
from tests.conftest import REPO

PINS = yaml.safe_load((REPO / "config" / "pilot_sdxl_pins.yaml").read_text(encoding="utf-8"))
GRAPH_PATH = REPO / PINS["workflow"]["api_candidate"]
GRAPH = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
NODES = {k: v for k, v in GRAPH.items() if not k.startswith("_")}
# Required inputs and option lists read from the node pack source at the pinned commit (cubiq/ComfyUI_IPAdapter_plus a0f451a5, IPAdapterPlus.py) and ComfyUI 0.3.47.
REQUIRED = {
    "IPAdapterAdvanced": {"model", "ipadapter", "image", "weight", "weight_type", "combine_embeds", "start_at", "end_at", "embeds_scaling"},
    "IPAdapterModelLoader": {"ipadapter_file"}, "CLIPVisionLoader": {"clip_name"}, "VAELoader": {"vae_name"}, "CheckpointLoaderSimple": {"ckpt_name"},
    "CLIPTextEncode": {"text", "clip"}, "EmptyLatentImage": {"width", "height", "batch_size"}, "LoadImage": {"image"}, "VAEDecode": {"samples", "vae"},
    "SaveImage": {"images", "filename_prefix"},
    "KSampler": {"model", "seed", "steps", "cfg", "sampler_name", "scheduler", "positive", "negative", "latent_image", "denoise"}}
WEIGHT_TYPES = ["linear", "ease in", "ease out", "ease in-out", "reverse in-out", "weak input", "weak output", "weak middle", "strong middle", "style transfer", "composition",
                "strong style transfer", "style and composition", "style transfer precise", "composition precise"]
COMBINE = ["concat", "add", "subtract", "average", "norm average"]
SCALING = ["V only", "K+V", "K+V w/ C penalty", "K+mean(V) w/ C penalty"]
OUTPUTS = {"CheckpointLoaderSimple": 3, "VAELoader": 1, "CLIPVisionLoader": 1, "IPAdapterModelLoader": 1, "LoadImage": 2, "IPAdapterAdvanced": 1, "CLIPTextEncode": 1,
           "EmptyLatentImage": 1, "KSampler": 1, "VAEDecode": 1, "SaveImage": 0}


def test_pins_are_complete_and_not_approved():
    assert PINS["status"] == "pinned_not_approved" and PINS["approved_by"] is None and PINS["style"] == "devotional_gouache_1950s_v1"
    for item in PINS["files"]:
        assert re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) and re.fullmatch(r"[0-9a-f]{40}", item["revision"]) and item["size_bytes"] > 0 and item["dest_dir"].startswith("models/")
    assert [i["role"] for i in PINS["files"]] == ["sdxl_checkpoint", "ip_adapter", "clip_vision", "vae_fp16_fix"]
    assert re.fullmatch(r"[0-9a-f]{40}", PINS["custom_nodes"][0]["commit"]) and PINS["custom_nodes"][0]["licence"] == "GPL-3.0"
    assert PINS["comfyui"]["commit"] == yaml.safe_load((REPO / "config" / "ltx_098_pins.yaml").read_text(encoding="utf-8"))["sources"]["comfyui"]["commit"]


def test_graph_is_unvalidated_every_link_resolves_and_every_required_input_is_present():
    assert GRAPH["_status"] == "unvalidated" and "NOT VALIDATED" in GRAPH["_note"] and NODES[GRAPH["_output_node"]]["class_type"] == "SaveImage"
    for node_id, node in NODES.items():
        assert REQUIRED[node["class_type"]] <= set(node["inputs"]), (node_id, node["class_type"])
        for name, value in node["inputs"].items():
            if isinstance(value, list):
                source, slot = value
                assert source in NODES and slot < OUTPUTS[NODES[source]["class_type"]], (node_id, name, value)


def test_filenames_in_the_graph_are_exactly_the_pinned_files_and_enums_are_legal():
    names = {i["name"] for i in PINS["files"]}
    used = {NODES["4"]["inputs"]["ckpt_name"], NODES["10"]["inputs"]["vae_name"], NODES["11"]["inputs"]["clip_name"], NODES["12"]["inputs"]["ipadapter_file"]}
    assert used == names
    ip = NODES["14"]["inputs"]
    assert ip["weight_type"] in WEIGHT_TYPES and ip["combine_embeds"] in COMBINE and ip["embeds_scaling"] in SCALING and 0 <= ip["start_at"] <= ip["end_at"] <= 1
    assert NODES["3"]["inputs"]["model"] == ["14", 0]                                       # the sampler uses the IP-Adapter-patched model, not the raw checkpoint


def test_placeholders_match_the_adapter_contract_and_render_with_the_existing_helper(tmp_path):
    template = load_template(GRAPH_PATH)
    assert template.status == "unvalidated"
    assert set(re.findall(r"\{\{([A-Z_0-9]+)\}\}", template.text)) == {"PROMPT", "NEGATIVE_PROMPT", "SEED", "WIDTH", "HEIGHT", "REFERENCE_IMAGE_1"}
    graph = render_graph(template, {"PROMPT": "p", "NEGATIVE_PROMPT": "n", "SEED": 7, "WIDTH": 1216, "HEIGHT": 832, "REFERENCE_IMAGE_1": "ref.png"})
    assert graph["5"]["inputs"]["width"] == 1216 and graph["3"]["inputs"]["seed"] == 7 and graph["13"]["inputs"]["image"] == "ref.png"
    from granthstudio.comfy import ensure_validated
    with pytest.raises(IntegrationUnavailable):
        ensure_validated(template)                                                        # an unvalidated template can never be used for a real job


def test_the_audio_environment_probe_reports_missing_packages_without_raising():
    import importlib.util, sys
    spec = importlib.util.spec_from_file_location("audio_deps_probe", REPO / "scripts" / "kaggle" / "audio_deps_probe.py")
    mod = importlib.util.module_from_spec(spec); sys.modules["audio_deps_probe"] = mod; spec.loader.exec_module(mod)
    def importer(name):
        if name == "f5_tts":
            raise ModuleNotFoundError("No module named 'f5_tts'")
        if name == "torch":
            raise OSError("broken binary")
        return object()
    report = mod.probe({"numpy": "numpy", "f5_tts": "f5-tts", "torch": "torch"}, importer=importer, version=lambda dist: "1.2.3")
    assert report["missing"] == ["f5_tts", "torch"] and report["packages"]["numpy"] == {"ok": True, "version": "1.2.3"}
    assert report["packages"]["torch"]["error"].startswith("OSError") and report["cuda"] == {"available": False, "devices": []}
