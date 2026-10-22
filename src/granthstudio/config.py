"""Configuration loading and the LTX capability gate.

A capability (i2v or flf) runs only when models.yaml marks it validated, the checkpoint
hash is pinned, and a passing benchmark receipt exists for this exact checkpoint.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .errors import CapabilityDisabled, ConfigError, SchemaError
from .integrity import read_json, sha256_file, sha256_obj
from .schemas import validate_document

CAPABILITIES = ("i2v", "flf")


@dataclass(frozen=True)
class Project:
    root: Path
    artifacts_dir: Path
    research_dir: Path
    canon_dir: Path
    episodes_dir: Path
    benchmarks_dir: Path


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ConfigError(f"missing file: {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"invalid YAML in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"{path} must contain a mapping")
    return data


def load_project(root: Path) -> Project:
    root = root.resolve()
    raw = load_yaml(root / "config" / "project.yaml")
    validate_document("project", raw)

    def at(key: str) -> Path:
        return (root / raw[key]).resolve()

    return Project(
        root=root,
        artifacts_dir=at("artifacts_dir"),
        research_dir=at("research_dir"),
        canon_dir=at("canon_dir"),
        episodes_dir=at("episodes_dir"),
        benchmarks_dir=at("benchmarks_dir"),
    )


def _load_checked(project: Project, schema: str, filename: str) -> dict[str, Any]:
    data = load_yaml(project.root / "config" / filename)
    validate_document(schema, data)
    return data


def load_models(project: Project) -> dict[str, Any]:
    return _load_checked(project, "models", "models.yaml")


def load_quality_gates(project: Project) -> dict[str, Any]:
    return _load_checked(project, "quality_gates", "quality_gates.yaml")


def passing_receipts(benchmarks_dir: Path, capability: str, checkpoint_sha256: str, workflow_version: str | None = None, runtime_sha256: str | None = None) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if not benchmarks_dir.is_dir():
        return found
    for path in sorted(benchmarks_dir.rglob("*.json")):
        try:
            data = read_json(path)
            validate_document("benchmark_receipt", data)
        except (SchemaError, ValueError):
            continue
        if (
            data["capability"] == capability
            and data["checkpoint_sha256"] == checkpoint_sha256
            and data["outcome"] == "pass"
            and data["accepted"] is True
            and (workflow_version is None or data["workflow_version"] == workflow_version)
            and (runtime_sha256 is None or data.get("runtime_sha256") == runtime_sha256)
            and (runtime_sha256 is None or (data["gpu"] == "T4" and data["video_seconds"] > 0
                 and data["gpu_seconds_total"] > 0 and (data.get("peak_vram_mb") or 0) > 0
                 and len(data.get("output_sha256") or "") == 64))
        ):
            found.append(data)
    return found


def require_capability(models: dict[str, Any], capability: str, benchmarks_dir: Path, workflow_version: str | None = None) -> dict[str, Any]:
    if capability not in CAPABILITIES:
        raise ConfigError(f"unknown capability {capability!r}")
    ltx = models["ltx"]
    status = ltx["capabilities"][capability]
    if status != "validated":
        raise CapabilityDisabled(f"LTX {capability} status is '{status}': NOT VALIDATED")
    pin = ltx["checkpoint_sha256"]
    if pin is None:
        raise CapabilityDisabled("LTX checkpoint_sha256 is not pinned: NOT VALIDATED")
    if workflow_version is None:
        raise CapabilityDisabled("current workflow hash is required: NOT VALIDATED")
    runtime = ltx.get("runtime")
    if runtime is None:
        raise CapabilityDisabled("runtime inventory is missing: NOT VALIDATED")
    validate_document("models", models)
    for kind, file in runtime["files"].items():
        path = Path(file["path"])
        if not path.is_absolute() or not path.is_file() or sha256_file(path) != file["sha256"]:
            raise CapabilityDisabled(f"{kind} runtime file/hash mismatch: NOT VALIDATED")
    if runtime["files"]["checkpoint"]["sha256"] != pin:
        raise CapabilityDisabled("runtime checkpoint differs from model pin: NOT VALIDATED")
    runtime_hash = sha256_obj({"runtime": runtime, "frame_counts": ltx["frame_counts"],
                               "family": ltx["family"], "version": ltx["version"], "variant": ltx["variant"]})
    found = passing_receipts(benchmarks_dir, capability, pin, workflow_version, runtime_hash)
    if not found:
        raise CapabilityDisabled(
            f"no passing benchmark receipt for LTX {capability} with this checkpoint: NOT VALIDATED"
        )
    return found[0]


def dump_yaml(path: Path, data: dict[str, Any]) -> None:
    """Atomic YAML write for human-edited files that tools update (comments are not preserved)."""
    from .integrity import atomic_write_bytes
    atomic_write_bytes(path, yaml.safe_dump(data, allow_unicode=True, sort_keys=False).encode("utf-8"))
