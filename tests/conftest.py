"""Synthetic fixtures only. Nothing here is Granth content: names and lines are invented test markers."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import pytest
import yaml

from granthstudio.config import Project, load_models, load_project
from granthstudio.integrity import sha256_file, sha256_obj, normalize_text
from granthstudio.research import approve

REPO = Path(__file__).resolve().parents[1]

FIXED_TIME = "2026-10-22T00:00:00+00:00"


def _dump(path: Path, document: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.name == "hi.yaml":
        master = yaml.safe_load((path.parent / "mr.yaml").read_text(encoding="utf-8"))
        lines = {line["dialogue_id"]: line for line in master["entries"]}
        for entry in document["entries"]:
            entry["alignment"]["verification"] = {"reviewer": "synthetic-test-only",
                "mr_sha256": sha256_obj(normalize_text(lines[entry["dialogue_id"]]["text"])),
                "hi_sha256": sha256_obj(normalize_text(entry["text"]))}
    path.write_text(yaml.safe_dump(document, allow_unicode=True, sort_keys=False), encoding="utf-8")


def make_project(root: Path) -> Project:
    root.mkdir(parents=True, exist_ok=True)
    artifacts = root / "artifacts"
    _dump(root / "config" / "project.yaml", {
        "schema_version": 1, "artifacts_dir": str(artifacts), "research_dir": "research", "canon_dir": "canon",
        "episodes_dir": "episodes", "benchmarks_dir": "benchmarks", "timezone": "Asia/Calcutta",
    })
    _dump(root / "config" / "models.yaml", {
        "schema_version": 1,
        "comfyui": {"base_url": "http://127.0.0.1:8188"},
        "ltx": {
            "family": "LTX-Video", "version": "0.9.8", "variant": "2b-distilled",
            "checkpoint_file": "ltxv-2b-0.9.8-distilled.safetensors", "checkpoint_sha256": None, "precision": "fp16",
            "workflow_templates": {"i2v": "workflows/comfyui/ltx_i2v_098.json", "flf": "workflows/comfyui/ltx_flf_098.json"},
            "frame_counts": [49, 65, 81, 89, 97, 121],
            "capabilities": {"i2v": "unvalidated", "flf": "unvalidated"},
        },
        **{k: v for k, v in yaml.safe_load((REPO / "config" / "models.yaml").read_text(encoding="utf-8")).items() if k in ("sdxl", "translation", "speech", "asr", "aligner", "diagnostics")},
    })
    _dump(root / "config" / "quality_gates.yaml", {
        "schema_version": 1,
        "hard_gates": ["source_integrity", "canon_identity", "marathi_lock", "hindi_terms", "task_outputs", "video_decode"],
        "diagnostics": ["face_embedding_similarity"], "enforced_thresholds": [],
    })
    # Infrastructure config is copied from the repository so tests follow the shipped contract.
    for name in ("runtime.yaml", "pilot.yaml"):
        shutil.copyfile(REPO / "config" / name, root / "config" / name)
    template_dir = root / "workflows" / "comfyui"
    template_dir.mkdir(parents=True, exist_ok=True)
    for name in ("ltx_i2v_098.json", "ltx_flf_098.json", "sdxl_keyframe.json"):
        (template_dir / name).write_text('{"_status": "unvalidated"}', encoding="utf-8")

    _dump(root / "canon" / "characters.yaml", {
        "schema_version": 1, "kind": "characters", "identity_decisions": [],
        "entries": [
            {"id": "chr_synth_a", "canonical_name": "SYNTH-A", "aliases": ["SYN-A"], "status": "approved"},
            {"id": "chr_synth_b", "canonical_name": "SYNTH-B", "aliases": [], "status": "approved"},
        ],
    })
    _dump(root / "canon" / "locations.yaml", {
        "schema_version": 1, "kind": "locations", "identity_decisions": [],
        "entries": [{"id": "loc_synth_room", "canonical_name": "SYNTH-ROOM", "aliases": [], "status": "approved"}],
    })
    _dump(root / "canon" / "props.yaml", {"schema_version": 1, "kind": "props", "entries": [], "identity_decisions": []})
    _dump(root / "canon" / "terminology.yaml", {
        "schema_version": 1, "kind": "terminology", "identity_decisions": [],
        "entries": [{"id": "term_synth_x", "canonical_name": "TERMX", "aliases": [], "status": "approved",
                     "protected": True, "hi_allowed": ["TERMX-HI"]}],
    })

    research_dir = root / "research" / "adhyay_01"
    _dump(research_dir / "research.yaml", {
        "schema_version": 1, "adhyay": 1,
        "scenes": [{
            "scene_id": "a01_s01", "source_refs": ["fixture:s01"], "location": "loc_synth_room",
            "characters": ["chr_synth_a", "chr_synth_b"],
            "description": "Synthetic scene for CPU tests only",
            "actions": [{"id": "action_turn", "text": "slight head turn", "source_refs": ["fixture:3"], "artistic": False}],
            "visual_details": [], "continuity": [],
            "dialogue": [
                {"id": "d_0001", "speaker": "chr_synth_a", "text": "SYNTH-A says 2 things", "source_ref": "fixture:1"},
                {"id": "d_0002", "speaker": "chr_synth_b", "text": "TERMX is named", "source_ref": "fixture:2"},
            ],
        }],
        "open_questions": [{"id": "SYN-Q1", "status": "answered"}],
    })

    visual = artifacts / "visuals" / "vis" / "room.png"
    make_still(visual)
    visual_sha = sha256_file(visual)

    _dump(root / "episodes" / "adhyay_01" / "manifest.yaml", {
        "schema_version": 1, "episode_id": "ep01", "adhyay": 1, "research_version": 1,
        "visuals": [{"visual_id": "vis_room_still", "source": "file", "path": "vis/room.png", "sha256": visual_sha}],
        "scenes": [{
            "scene_id": "a01_s01", "research_scene": "a01_s01", "location": "loc_synth_room",
            "characters": ["chr_synth_a", "chr_synth_b"], "lighting": "day_indoor",
            "shots": [
                {"shot_id": "a01_s01_sh01", "tier": 0, "visual_id": "vis_room_still", "duration_s": 1.0,
                 "dialogue_ids": ["d_0001"], "pilot_shot": "A"},
                {"shot_id": "a01_s01_sh02", "tier": 1, "visual_id": "vis_room_still", "duration_s": 2.04,
                 "frames": 49, "motion_prompt": "slight head turn", "action_ids": ["action_turn"], "dialogue_ids": ["d_0002"], "pilot_shot": "B"},
            ],
        }],
    })
    _dump(root / "episodes" / "adhyay_01" / "mr.yaml", {
        "schema_version": 1, "language": "mr", "adhyay": 1, "entries": [
            {"dialogue_id": "d_0001", "shot_id": "a01_s01_sh01", "speaker": "chr_synth_a", "text": "SYNTH-A says 2 things"},
            {"dialogue_id": "d_0002", "shot_id": "a01_s01_sh02", "speaker": "chr_synth_b", "text": "TERMX is named"},
        ],
    })
    _dump(root / "episodes" / "adhyay_01" / "hi.yaml", {
        "schema_version": 1, "language": "hi", "adhyay": 1, "entries": [
            {"dialogue_id": "d_0001", "shot_id": "a01_s01_sh01", "speaker": "chr_synth_a",
             "text": "SYNTH-A 2 बातें कहता है",
             "alignment": {"mr_dialogue_id": "d_0001", "match": "adapted", "reviewed": True}},
            {"dialogue_id": "d_0002", "shot_id": "a01_s01_sh02", "speaker": "chr_synth_b",
             "text": "TERMX-HI नामित है",
             "alignment": {"mr_dialogue_id": "d_0002", "match": "adapted", "reviewed": True}},
        ],
    })
    return load_project(root)


@pytest.fixture
def project(tmp_path: Path) -> Project:
    return make_project(tmp_path / "proj")


@pytest.fixture
def approved_project(project: Project) -> Project:
    approve(project, 1, "synthetic-tester", FIXED_TIME)
    return project


@pytest.fixture
def models(project: Project) -> dict[str, Any]:
    return load_models(project)


def have_tool(name: str) -> bool:
    return shutil.which(name) is not None


def make_still(path: Path) -> Path:
    """A real PNG (synthetic colour field) when FFmpeg exists; placeholder bytes otherwise."""
    import subprocess

    path.parent.mkdir(parents=True, exist_ok=True)
    if have_tool("ffmpeg"):
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc=size=640x360",
             "-frames:v", "1", str(path)],
            check=True, timeout=120,
        )
    else:
        path.write_bytes(b"SYNTHETIC-STILL-BYTES")
    return path


def make_clip(path: Path, seconds: float = 1.0) -> Path:
    """Create a small real H.264 clip with FFmpeg's test source (cheap)."""
    import subprocess

    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"color=c=red:s=320x240:d={seconds}",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", str(path)],
        check=True, timeout=120,
    )
    return path
