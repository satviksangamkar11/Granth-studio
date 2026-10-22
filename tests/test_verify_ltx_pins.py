"""scripts/verify_ltx_pins.py with synthetic files only: no checkpoint, ComfyUI or network is involved."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys

import pytest
import yaml

from tests.conftest import REPO, have_tool

SPEC = importlib.util.spec_from_file_location("verify_ltx_pins", REPO / "scripts" / "verify_ltx_pins.py")
vp = importlib.util.module_from_spec(SPEC)
sys.modules["verify_ltx_pins"] = vp
SPEC.loader.exec_module(vp)

WORKFLOW = {"nodes": [
    {"id": 1, "type": "Loader", "outputs": [{"name": "MODEL"}], "inputs": [], "widgets_values": ["model.safetensors"]},
    {"id": 2, "type": "Sink", "outputs": [], "inputs": [{"name": "model", "link": 7}], "widgets_values": []}],
    "links": [[7, 1, 0, 2, 0, "MODEL"]]}


@pytest.fixture
def env(tmp_path):
    model = tmp_path / "models" / "checkpoints" / "model.safetensors"
    model.parent.mkdir(parents=True); model.write_bytes(b"synthetic weights")
    wf = tmp_path / "wf.json"; wf.write_text(json.dumps(WORKFLOW), encoding="utf-8")
    pins = {"frame_rule": {"frames": "8n+1", "min_frames": 9, "frame_step": 8},
            "sources": {"nodes": {"commit": "0" * 40}},
            "workflow": {"git_blob_sha": vp.git_blob_sha(wf.read_bytes()), "size_bytes": wf.stat().st_size, "checkpoint_substitution_verified": True},
            "files": [{"name": "model.safetensors", "role": "ltx_checkpoint", "dest_dir": "models/checkpoints",
                       "size_bytes": model.stat().st_size, "sha256": hashlib.sha256(model.read_bytes()).hexdigest()}],
            "required_nodes": [{"class": "Loader", "provider": "core", "status": "x"}, {"class": "Sink", "provider": "core", "status": "x"}]}
    path = tmp_path / "pins.yaml"; path.write_text(yaml.safe_dump(pins), encoding="utf-8")
    return tmp_path, pins, model, wf, path


def statuses(results):
    return {r["check"]: r["status"] for r in results}


def make_repo(path):
    path.mkdir()
    for cmd in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(path), *cmd], check=True)
    (path / "a.txt").write_text("a"); subprocess.run(["git", "-C", str(path), "add", "."], check=True)
    subprocess.run(["git", "-C", str(path), "commit", "-qm", "c"], check=True)
    return subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()


def test_files_pass_mismatch_missing_and_unverified(env):
    tmp, pins, model, *_ = env
    assert statuses(vp.check_files(pins, tmp))["file:model.safetensors"] == vp.PASS
    assert statuses(vp.check_files(pins, None))["file:model.safetensors"] == vp.UNVERIFIED
    assert statuses(vp.check_files(pins, tmp / "empty"))["file:model.safetensors"] == vp.MISSING
    model.write_bytes(b"synthetic WEIGHTS")                                       # same size, different content
    assert statuses(vp.check_files(pins, tmp))["file:model.safetensors"] == vp.MISMATCH
    model.write_bytes(b"short")
    assert "size" in vp.check_files(pins, tmp)[0]["detail"]
    nohash = {**pins, "files": [{**pins["files"][0], "sha256": None}]}
    assert statuses(vp.check_files(nohash, tmp / "models"))["file:model.safetensors"] == vp.UNVERIFIED


@pytest.mark.skipif(not have_tool("git"), reason="git missing")
def test_source_commit_checks(env):
    tmp, pins, *_ = env
    commit = make_repo(tmp / "nodes")
    assert statuses(vp.check_sources(pins, {}))["source:nodes"] == vp.UNVERIFIED
    assert statuses(vp.check_sources(pins, {"nodes": tmp / "none"}))["source:nodes"] == vp.MISSING
    assert statuses(vp.check_sources(pins, {"nodes": tmp / "nodes"}))["source:nodes"] == vp.MISMATCH     # pin is 000...
    pins["sources"]["nodes"]["commit"] = commit
    assert statuses(vp.check_sources(pins, {"nodes": tmp / "nodes"}))["source:nodes"] == vp.PASS
    (tmp / "nodes" / "a.txt").write_text("dirty")
    assert statuses(vp.check_sources(pins, {"nodes": tmp / "nodes"}))["source:nodes"] == vp.MISMATCH     # modified checkout
    (tmp / "plain").mkdir()
    assert statuses(vp.check_sources(pins, {"nodes": tmp / "plain"}))["source:nodes"] == vp.UNVERIFIED


def test_node_inventory(env):
    _, pins, *_ = env
    assert set(statuses(vp.check_nodes(pins, None)).values()) == {vp.UNVERIFIED}
    assert set(statuses(vp.check_nodes(pins, vp.inventory_classes({"Loader": {}, "Sink": {}}))).values()) == {vp.PASS}
    assert statuses(vp.check_nodes(pins, vp.inventory_classes(["Loader"])))["node:Sink"] == vp.MISSING
    with pytest.raises(ValueError):
        vp.inventory_classes("nope")


def test_workflow_identity_links_and_names(env):
    tmp, pins, _, wf, _ = env
    got = statuses(vp.check_workflow(pins, wf))
    assert got["workflow:identity"] == got["workflow:links"] == got["workflow:node_classes"] == vp.PASS
    assert got["workflow:model_names"] == vp.MISMATCH or got["workflow:model_names"] == vp.PASS
    assert statuses(vp.check_workflow(pins, None))["workflow"] == vp.UNVERIFIED
    assert statuses(vp.check_workflow(pins, tmp / "nope.json"))["workflow"] == vp.MISSING
    broken = json.loads(wf.read_text()); broken["links"][0][1] = 99                  # dangling reference
    wf.write_text(json.dumps(broken)); got = statuses(vp.check_workflow(pins, wf))
    assert got["workflow:identity"] == vp.MISMATCH and got["workflow:links"] == vp.MISMATCH
    wf.write_text("{not json")
    assert statuses(vp.check_workflow(pins, wf))["workflow:structure"] == vp.MISMATCH


def test_configuration_is_never_proof(env, tmp_path):
    _, pins, *_ = env
    pins["files"][0].update(name="ltx.safetensors", sha256="a" * 64)
    models = tmp_path / "models.yaml"
    models.write_text(yaml.safe_dump({"ltx": {"frame_counts": [49, 97], "checkpoint_file": "ltx.safetensors", "checkpoint_sha256": None}}))
    got = statuses(vp.check_config(pins, models))
    assert got["config:frame_counts"] == vp.PASS and got["config:checkpoint_file"] == vp.PASS
    assert got["config:checkpoint_sha256"] == vp.UNVERIFIED                           # a missing hash is not a pass
    models.write_text(yaml.safe_dump({"ltx": {"frame_counts": [49, 50], "checkpoint_file": "other", "checkpoint_sha256": "a" * 64}}))
    got = statuses(vp.check_config(pins, models))
    assert got["config:frame_counts"] == got["config:checkpoint_file"] == vp.MISMATCH
    assert all(r["kind"] == "CONFIG" for r in vp.check_config(pins, models))


def test_exit_codes_and_report(env, capsys):
    tmp, pins, model, wf, path = env
    out = tmp / "report.json"
    assert vp.main(["--pins", str(path), "--json", str(out)]) == 2                    # nothing local given: UNVERIFIED only
    assert json.loads(out.read_text())["exit"] == 2
    assert vp.main(["--pins", str(path), "--models-dir", str(tmp / "nowhere")]) == 1  # MISSING dominates UNVERIFIED
    model.write_bytes(b"synthetic WEIGHTS")
    assert vp.main(["--pins", str(path), "--models-dir", str(tmp)]) == 1   # MISMATCH


def test_shipped_pins_are_consistent_and_never_pass_without_local_evidence():
    pins = yaml.safe_load((REPO / "config" / "ltx_098_pins.yaml").read_text(encoding="utf-8"))
    assert pins["status"] == "PROPOSED_NOT_APPROVED"
    for source in pins["sources"].values():
        assert len(source["commit"]) == 40
    assert all(len(f["sha256"]) == 64 for f in pins["files"])
    rule = pins["frame_rule"]
    assert all(n >= rule["min_frames"] and (n - 1) % rule["frame_step"] == 0 for n in (49, 65, 81, 89, 97, 121))
    assert vp.main(["--models-yaml", str(REPO / "config" / "models.yaml")]) == 2        # config matches, but nothing local is proven
    results, _ = vp.run(vp.argparse.Namespace(pins=str(REPO / "config" / "ltx_098_pins.yaml"), source=[], models_dir=None,
                                               workflow=None, node_inventory=None, models_yaml=None,
                                               api_workflow=None, signatures=str(REPO / "scripts" / "comfy" / "node_signatures.yaml")))
    assert vp.PASS not in {r["status"] for r in results}


CANDIDATE = REPO / "workflows" / "comfyui" / "ltx_i2v_098.candidate.json"


def api_checks(path, pins=None):
    pins = pins or yaml.safe_load((REPO / "config" / "ltx_098_pins.yaml").read_text(encoding="utf-8"))
    return statuses(vp.check_api_workflow(pins, path, vp.flat_signatures(str(REPO / "scripts" / "comfy" / "node_signatures.yaml"))))


def test_shipped_candidate_workflow_passes_every_structural_check():
    got = api_checks(CANDIDATE)
    assert set(got.values()) == {vp.PASS}, got
    assert {"api:node_classes", "api:links", "api:output_node", "api:checkpoint_name", "api:model_files",
            "api:placeholders", "api:seed_on_generation_path"} <= set(got)


def test_api_workflow_mutations_are_caught(tmp_path):
    base = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    def mutated(mutate):
        doc = json.loads(json.dumps(base)); mutate(doc)
        path = tmp_path / "m.json"; path.write_text(json.dumps(doc), encoding="utf-8")
        return api_checks(path)
    assert mutated(lambda d: d["99"]["inputs"].update(model=["999", 0]))["api:links"] == vp.MISMATCH            # dangling node
    assert mutated(lambda d: d["99"]["inputs"].update(model=["44", 7]))["api:links"] == vp.MISMATCH             # impossible slot
    assert mutated(lambda d: d["44"]["inputs"].update(ckpt_name="ltxv-2b-0.9.6-distilled-04-25.safetensors"))["api:checkpoint_name"] == vp.MISMATCH
    assert mutated(lambda d: d["38"]["inputs"].update(clip_name="other_encoder.safetensors"))["api:model_files"] == vp.MISMATCH
    assert mutated(lambda d: d.update(_output_node="8"))["api:output_node"] == vp.MISMATCH
    assert mutated(lambda d: d["102"]["inputs"].update(noise_seed=45))["api:placeholders"] == vp.MISMATCH      # SEED no longer wired
    assert mutated(lambda d: d["102"]["inputs"].pop("noise_seed"))["api:seed_on_generation_path"] == vp.MISMATCH
    assert mutated(lambda d: d.update({"500": {"class_type": "Surprise", "inputs": {}}}))["api:node_classes"] == vp.MISMATCH
    assert api_checks(None)["api_workflow"] == vp.UNVERIFIED and api_checks(tmp_path / "nope.json")["api_workflow"] == vp.MISSING
