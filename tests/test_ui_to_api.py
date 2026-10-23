"""scripts/comfy/ui_to_api.py: UI-to-API conversion without invention. Synthetic and reconstructed inputs only; no ComfyUI runs."""
from __future__ import annotations

import copy
import importlib.util
import json
import sys

import pytest
import yaml

from tests.conftest import REPO

SPEC = importlib.util.spec_from_file_location("ui_to_api", REPO / "scripts" / "comfy" / "ui_to_api.py")
conv = importlib.util.module_from_spec(SPEC)
sys.modules["ui_to_api"] = conv
SPEC.loader.exec_module(conv)

RECIPE = REPO / "workflows" / "comfyui" / "source" / "ltx_i2v_098.recipe.yaml"
SIGNATURES = REPO / "scripts" / "comfy" / "node_signatures.yaml"
CANDIDATE = REPO / "workflows" / "comfyui" / "ltx_i2v_098.candidate.json"
UI = json.loads((REPO / "workflows" / "comfyui" / "source" / "ltxvideo_i2v_distilled.ui_inventory.json").read_text(encoding="utf-8"))


def sigs():
    return conv.load_signatures(SIGNATURES)


def test_committed_candidate_is_exactly_what_the_converter_produces():
    graph, report = conv.build(RECIPE, None, None, SIGNATURES)
    committed = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    assert graph == committed
    assert any(line.startswith("DEFAULTED node 95 LTXVImgToVideo.strength = 1.0") for line in report)   # reported, not silent
    assert sum(line.startswith("OVERRIDE") for line in report) == 11
    assert committed["_status"] == "unvalidated" and "NOT VALIDATED" in committed["_note"]


def test_every_connection_comes_from_the_ui_links():
    api, _ = conv.convert(UI, sigs())
    expected = {(str(src), str(dst)) for _, src, _, dst, _, _ in UI["links"]}
    produced = {(value[0], node_id) for node_id, node in api.items() for value in node["inputs"].values()
                if isinstance(value, list) and len(value) == 2 and isinstance(value[0], str)}
    assert produced == expected and len(api) == 16                          # 18 UI nodes minus 2 Notes
    # spot checks that slot numbers survive: VAE is output 2 of the checkpoint loader, 'denoised_output' is slot 1 of the sampler
    assert api["8"]["inputs"] == {"samples": ["101", 1], "vae": ["44", 2]}
    assert api["95"]["inputs"]["vae"] == ["44", 2] and api["101"]["inputs"]["latent_image"] == ["95", 2]


def test_widget_values_are_matched_by_signature_and_ui_only_values_dropped():
    api, _ = conv.convert(UI, sigs())
    assert api["102"]["inputs"] == {"noise_seed": 45}                       # 'fixed' (control_after_generate) dropped
    assert api["78"]["inputs"] == {"image": "fox.jpg"}                      # upload-widget values dropped
    assert api["38"]["inputs"] == {"clip_name": "t5xxl_fp16.safetensors", "type": "ltxv", "device": "default"}
    assert api["103"]["inputs"]["pix_fmt"] == "yuv420p" and api["103"]["inputs"]["crf"] == 20   # format-defined widgets, in order
    assert "videopreview" not in json.dumps(api)


@pytest.mark.parametrize("mutate,message", [
    (lambda ui: ui["nodes"][0].update(type="MysteryNode"), "no signature for class MysteryNode"),
    (lambda ui: next(n for n in ui["nodes"] if n["id"] == 82).update(widgets_values=[]), "no stored value for widget img_compression"),
    (lambda ui: next(n for n in ui["nodes"] if n["id"] == 82).update(widgets_values=[38, 7]), "1 unexplained widget value"),
    (lambda ui: next(n for n in ui["nodes"] if n["id"] == 99)["inputs"][0].update(link=None), None),   # unconnected required link: skipped, not invented
])
def test_conversion_refuses_to_guess(mutate, message):
    ui = copy.deepcopy(UI); mutate(ui)
    if message is None:
        api, _ = conv.convert(ui, sigs())
        assert "model" not in api["99"]["inputs"]                           # a missing connection is never filled in
        return
    with pytest.raises(conv.ConversionError, match=message):
        conv.convert(ui, sigs())


def test_overrides_must_name_real_inputs_and_link_from_ui_only_nodes_is_refused():
    with pytest.raises(conv.ConversionError, match="no such node input"):
        conv.convert(UI, sigs(), {"78.nonexistent": 1})
    ui = copy.deepcopy(UI)
    ui["links"].append([999, 76, 0, 82, 0, "IMAGE"])                         # a link whose source is a Note
    next(n for n in ui["nodes"] if n["id"] == 82)["inputs"][0]["link"] = 999
    with pytest.raises(conv.ConversionError, match="UI-only or missing node"):
        conv.convert(ui, sigs())


def fake_object_info():
    """What a running server would report, derived from the signature table (so a mismatch in either path shows up)."""
    info = {}
    for name, sig in sigs().items():
        required = {}
        for entry in sig["inputs"]:
            if name == "VHS_VideoCombine" and entry["name"] in ("pix_fmt", "crf", "save_metadata", "trim_to_audio"):
                continue
            if entry["kind"] == "link":
                required[entry["name"]] = ["LINKTYPE"] if not (name == "FloatToSigmas") else ["FLOAT", {"default": 0.0, "forceInput": True}]
            elif entry["name"] == "format":
                formats = {"video/h264-mp4": [["pix_fmt", [["yuv420p"]]], ["crf", "INT"], ["save_metadata", "BOOLEAN"], ["trim_to_audio", "BOOLEAN"]]}
                required["format"] = [["video/h264-mp4"], {"formats": formats}]
            else:
                options = {k: v for k, v in entry.items() if k in ("default", "control_after_generate")}
                required[entry["name"]] = ["INT", options]
        info[name] = {"input": {"required": required}, "input_order": {"required": list(required)}, "output_name": sig["outputs"]}
    return info


def test_object_info_path_reproduces_the_same_graph(tmp_path):
    from_table, _ = conv.build(RECIPE, None, None, SIGNATURES)
    info = tmp_path / "object_info.json"; info.write_text(json.dumps(fake_object_info()), encoding="utf-8")
    from_server, report = conv.build(RECIPE, None, info, SIGNATURES)
    assert from_server == from_table                                         # live signatures and the source table agree
    assert report[0].startswith("signatures: live /object_info")
    out_a, out_b = tmp_path / "a.json", tmp_path / "b.json"
    out_a.write_text(json.dumps(from_server), encoding="utf-8"); out_b.write_text(json.dumps(from_table), encoding="utf-8")
    assert conv.main(["compare", str(out_a), str(out_b)]) == 0
    from_table["99"]["inputs"]["cfg"] = 7
    out_b.write_text(json.dumps(from_table), encoding="utf-8")
    assert conv.main(["compare", str(out_a), str(out_b)]) == 1


def test_the_candidate_loads_through_the_real_adapter_helpers(tmp_path):
    """Placeholders render, the pinned checkpoint binding passes, and freshness is judged on the sampler path."""
    from granthstudio.comfy import check_checkpoint_binding, generation_evidence, load_template, render_graph, node_types
    template = load_template(CANDIDATE)
    check_checkpoint_binding(template, "ltxv-2b-0.9.8-distilled.safetensors")
    values = {"START_IMAGE": "granth_x.png", "MOTION_PROMPT": "a slow push in", "WIDTH": 768, "HEIGHT": 512, "FRAMES": 49, "FPS": 24, "SEED": 5}
    graph = render_graph(template, values)
    assert graph["95"]["inputs"]["length"] == 49 and graph["102"]["inputs"]["noise_seed"] == 5 and graph["78"]["inputs"]["image"] == "granth_x.png"
    assert node_types(graph) == {n["class_type"] for n in graph.values()} and len(node_types(graph)) == 15
    one = generation_evidence(graph, template.output_node)
    assert one["seed_inputs"] == [{"node": "102", "input": "noise_seed", "value": 5}]
    other = generation_evidence(render_graph(template, {**values, "SEED": 6}), template.output_node)
    assert other["fingerprint"] != one["fingerprint"]                         # a new seed is a new generation
    prefix = copy.deepcopy(graph); prefix["103"]["inputs"]["filename_prefix"] = "changed"
    assert generation_evidence(prefix, template.output_node)["fingerprint"] == one["fingerprint"]   # the save node does not count
    with pytest.raises(Exception, match="unresolved placeholders"):
        render_graph(template, {k: v for k, v in values.items() if k != "SEED"})


def test_a_wrong_signature_name_cannot_silently_drop_a_wire():
    bad = copy.deepcopy(sigs())
    bad["CFGGuider"]["inputs"][0]["name"] = "mdl"                        # 'model' is wired in the UI file
    with pytest.raises(conv.ConversionError, match=r"UI connection\(s\) \['model'\] match no signature input"):
        conv.convert(UI, bad)


def test_a_wired_input_the_signature_calls_a_widget_is_refused_not_defaulted():
    bad = copy.deepcopy(sigs())
    entry = next(e for e in bad["LTXVImgToVideo"]["inputs"] if e["name"] == "image")
    entry["kind"] = "widget"
    with pytest.raises(conv.ConversionError, match="wired in the UI but the signature treats it as a widget"):
        conv.convert(UI, bad)


@pytest.mark.parametrize("mutate,message", [
    (lambda ui: ui["links"][[l[0] for l in ui["links"]].index(87)].__setitem__(4, 0), "ends at node 8 slot 0, not here"),
    (lambda ui: ui["links"][[l[0] for l in ui["links"]].index(87)].__setitem__(3, 95), "ends at node 95"),
    (lambda ui: ui["links"][[l[0] for l in ui["links"]].index(87)].__setitem__(2, 9), "output slot 9 that node 44 lacks"),
    (lambda ui: next(n for n in ui["nodes"] if n["id"] == 8)["inputs"][0].update(link=12345), "not declared"),
])
def test_inconsistent_link_endpoints_are_refused(mutate, message):
    ui = copy.deepcopy(UI); mutate(ui)
    with pytest.raises(conv.ConversionError, match=message):
        conv.convert(ui, sigs())


def test_negative_source_slot_and_two_linked_inputs_with_one_name_are_refused():
    ui = copy.deepcopy(UI)
    ui["links"][[l[0] for l in ui["links"]].index(87)][2] = -1
    with pytest.raises(conv.ConversionError, match="output slot -1"):
        conv.convert(ui, sigs())
    ui = copy.deepcopy(UI)                                                   # two DIFFERENT, correctly addressed links into inputs both named float_list
    node = next(n for n in ui["nodes"] if n["id"] == 98)
    node["inputs"][0]["link"] = 900
    ui["links"].append([900, 100, 0, 98, 0, "FLOAT"])
    with pytest.raises(conv.ConversionError, match="two linked inputs are both named 'float_list'"):
        conv.convert(ui, sigs())
    ui = copy.deepcopy(UI)
    ui["links"][[l[0] for l in ui["links"]].index(87)][2] = True              # a JSON boolean is not a slot number
    with pytest.raises(conv.ConversionError, match="output slot True"):
        conv.convert(ui, sigs())


def dict_form_ui():
    """The official file stores VideoHelperSuite widgets as {name: value} (found on Kaggle: the positional inventory had hidden this)."""
    ui = copy.deepcopy(UI)
    node = next(n for n in ui["nodes"] if n["id"] == 103)
    names = ["frame_rate", "loop_count", "filename_prefix", "format", "pix_fmt", "crf", "save_metadata", "trim_to_audio", "pingpong", "save_output", "videopreview"]
    node["widgets_values"] = dict(zip(names, node["widgets_values"]))
    return ui


def test_dict_form_widget_values_convert_to_the_same_graph_and_unknown_keys_are_refused():
    positional, _ = conv.convert(UI, sigs(), None)
    named, _ = conv.convert(dict_form_ui(), sigs(), None)
    assert named == positional
    bad = dict_form_ui()
    next(n for n in bad["nodes"] if n["id"] == 103)["widgets_values"]["surprise"] = 1
    with pytest.raises(conv.ConversionError, match="match no widget"):
        conv.convert(bad, sigs(), None)
    missing = dict_form_ui()
    del next(n for n in missing["nodes"] if n["id"] == 103)["widgets_values"]["crf"]
    with pytest.raises(conv.ConversionError):
        conv.convert(missing, sigs(), None)
