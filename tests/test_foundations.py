"""Foundations: integrity helpers, schemas, repository configuration and the CLI surface."""

from __future__ import annotations

import pytest

from granthstudio.cli import build_parser, main
from granthstudio.config import load_models, load_project, load_quality_gates
from granthstudio.errors import SchemaError
from granthstudio.integrity import atomic_write_json, normalize_text, read_json, sha256_obj
from granthstudio.schemas import validate_document
from pathlib import Path


def test_canonical_hash_ignores_key_order():
    assert sha256_obj({"a": 1, "b": [2, 3]}) == sha256_obj({"b": [2, 3], "a": 1})


def test_normalize_text_uses_nfc_and_collapses_spaces():
    decomposed = "क़"  # two code points
    assert normalize_text(f"  {decomposed}\n  x  ") == normalize_text("क़ x")


def test_atomic_json_round_trip(tmp_path: Path):
    target = tmp_path / "a" / "b.json"
    atomic_write_json(target, {"x": 1})
    assert read_json(target) == {"x": 1}
    assert not list(target.parent.glob("*.tmp"))


def test_schema_rejects_unpinned_capability_value(models):
    models["ltx"]["capabilities"]["i2v"] = "maybe"
    with pytest.raises(SchemaError):
        validate_document("models", models)


def test_schema_rejects_wrong_checkpoint_file(models):
    models["ltx"]["checkpoint_file"] = "ltxv-2b-0.9.8-distilled-fp8.safetensors"
    with pytest.raises(SchemaError):
        validate_document("models", models)


def test_schema_rejects_unknown_quality_threshold(project):
    gates = load_quality_gates(project)
    gates["enforced_thresholds"] = [{"name": "x"}]
    with pytest.raises(SchemaError):
        validate_document("quality_gates", gates)


def test_repository_configuration_is_valid():
    root = Path(__file__).resolve().parents[1]
    project = load_project(root)
    models = load_models(project)
    assert models["ltx"]["capabilities"] == {"i2v": "unvalidated", "flf": "unvalidated"}
    assert models["ltx"]["checkpoint_sha256"] is None
    load_quality_gates(project)


def test_cli_help_parses_every_command():
    parser = build_parser()
    for argv in (["version"], ["config"], ["validate"], ["research", "status", "1"],
                 ["research", "approve", "1", "--reviewer", "r", "--confirm"], ["canon", "check"],
                 ["episode", "compile", "1"], ["timeline", "check", "1"], ["plan", "1"], ["run", "1"],
                 ["report", "1"], ["ffprobe", "x.mp4"], ["pilot", "plan", "1"], ["pilot", "score", "d"]):
        parser.parse_args(argv)


def test_cli_version_exit_code(capsys):
    assert main(["version"]) == 0
    assert "granthstudio" in capsys.readouterr().out


def test_ltx_frame_and_size_rule_and_embedded_vae(project):
    from granthstudio.config import ltx_dimension_problems, load_models
    from granthstudio.errors import ConfigError
    assert ltx_dimension_problems(frames=97, width=768, height=512) == []
    assert ltx_dimension_problems(frames=9) == []
    assert len(ltx_dimension_problems(frames=96, width=770, height=500)) == 3
    assert ltx_dimension_problems(frames=8) and ltx_dimension_problems(width=32)          # below the minimum
    from granthstudio.integrity import atomic_write_json
    path = project.root / "config" / "models.yaml"
    models = load_models(project)
    original = [*models["ltx"]["frame_counts"]]
    models["ltx"]["frame_counts"] = [49, 50]
    atomic_write_json(path, models)
    with pytest.raises(ConfigError, match=r"frames 50 is not 8n\+1"):
        load_models(project)
    models["ltx"]["frame_counts"] = original
    atomic_write_json(path, models)
    assert load_models(project)["ltx"]["frame_counts"] == original


def test_runtime_vae_may_be_null_meaning_embedded(project, tmp_path):
    from granthstudio.schemas import validate_document
    from granthstudio.config import load_models
    models = load_models(project)
    files = {k: {"path": str(tmp_path / k), "sha256": "a" * 64} for k in ("checkpoint", "text_encoder")}
    models["ltx"]["runtime"] = {"files": {**files, "vae": None}, "comfyui_commit": "a" * 40, "node_pack_commit": "b" * 40,
                                "gpu": "T4", "precision": "fp16", "width": 768, "height": 512}
    validate_document("models", models)                       # embedded VAE: accepted
    del models["ltx"]["runtime"]["files"]["text_encoder"]
    with pytest.raises(Exception):
        validate_document("models", models)                   # the text encoder is still mandatory
