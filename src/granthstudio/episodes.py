"""Episode manifest contract (frozen section 12, specified in docs/SPEC_SECTIONS_11_12_14.md).

The compiler checks every reference against approved research and approved canon, pins
the research version and the canon digest, and produces a deterministic compiled plan.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .canon import Canon
from .config import Project, load_yaml
from .errors import CanonReferenceError, ConfigError, GateFailure, SourceChanged
from .integrity import sha256_file, sha256_obj
from .research import dialogue_index
from .schemas import validate_document

TIER_KIND = {0: "still", 1: "i2v", 2: "flf"}


def episode_dir(project: Project, adhyay: int) -> Path:
    return project.episodes_dir / f"adhyay_{adhyay:02d}"


def load_manifest(project: Project, adhyay: int) -> dict[str, Any]:
    document = load_yaml(episode_dir(project, adhyay) / "manifest.yaml")
    validate_document("episode_manifest", document)
    if document["adhyay"] != adhyay:
        raise ConfigError(f"episode folder adhyay {adhyay} declares adhyay {document['adhyay']}")
    return document


def compile_episode(
    project: Project,
    models: dict[str, Any],
    canon: Canon,
    adhyay: int,
    research: dict[str, Any],
    receipt: dict[str, Any],
) -> dict[str, Any]:
    manifest = load_manifest(project, adhyay)
    if manifest["research_version"] != receipt["version"]:
        raise SourceChanged(
            f"manifest pins research version {manifest['research_version']}, approved is {receipt['version']}"
        )
    scenes_by_id = {scene["scene_id"]: scene for scene in research["scenes"]}
    dialogue = dialogue_index(research)
    visuals: dict[str, dict[str, Any]] = {}
    for visual in manifest["visuals"]:
        if visual["visual_id"] in visuals:
            raise ConfigError(f"duplicate visual id {visual['visual_id']}")
        if visual["source"] == "file" and visual["sha256"] is None:
            raise ConfigError(f"{visual['visual_id']}: file visuals must carry a sha256")
        visuals[visual["visual_id"]] = visual
    frame_counts = models["ltx"]["frame_counts"]
    shots: list[dict[str, Any]] = []
    pilot: dict[str, str] = {}
    seen_shots: set[str] = set()
    for scene in manifest["scenes"]:
        if scene["research_scene"] not in scenes_by_id:
            raise CanonReferenceError(f"research scene {scene['research_scene']} is not in approved research")
        canon.require(scene["location"], "locations")
        for char_id in scene["characters"]:
            canon.require(char_id, "characters")
        for shot in scene["shots"]:
            shot_id = shot["shot_id"]
            if shot_id in seen_shots:
                raise ConfigError(f"duplicate shot id {shot_id}")
            seen_shots.add(shot_id)
            if not shot_id.startswith(scene["scene_id"] + "_sh"):
                raise ConfigError(f"{shot_id} does not belong to scene {scene['scene_id']}")
            if shot["visual_id"] not in visuals:
                raise CanonReferenceError(f"{shot_id}: unknown visual {shot['visual_id']}")
            for line_id in shot["dialogue_ids"]:
                line = dialogue.get(line_id)
                if line is None or line["scene_id"] != scene["research_scene"]:
                    raise CanonReferenceError(f"{shot_id}: dialogue {line_id} is not in research scene {scene['research_scene']}")
                if line["speaker"] not in scene["characters"]:
                    raise CanonReferenceError(f"{line_id}: speaker {line['speaker']} is not in scene {scene['scene_id']}")
            kind = TIER_KIND[shot["tier"]]
            if kind == "still":
                if "frames" in shot or "end_visual_id" in shot:
                    raise ConfigError(f"{shot_id}: still shots carry no frames or end visual")
            else:
                if shot.get("frames") not in frame_counts:
                    raise ConfigError(f"{shot_id}: frames {shot.get('frames')} not in pinned frame_counts {frame_counts}")
                if kind == "flf":
                    if "end_visual_id" not in shot or shot["end_visual_id"] not in visuals:
                        raise CanonReferenceError(f"{shot_id}: flf shots need a known end_visual_id")
                elif "end_visual_id" in shot:
                    raise ConfigError(f"{shot_id}: only flf shots take an end_visual_id")
            label = shot.get("pilot_shot")
            if label is not None:
                if label in pilot:
                    raise ConfigError(f"pilot label {label} used by more than one shot")
                pilot[label] = shot_id
            shots.append(
                {
                    "shot_id": shot_id,
                    "scene_id": scene["scene_id"],
                    "tier": shot["tier"],
                    "kind": kind,
                    "visual_id": shot["visual_id"],
                    "end_visual_id": shot.get("end_visual_id"),
                    "duration_s": shot["duration_s"],
                    "frames": shot.get("frames"),
                    "motion_prompt": shot.get("motion_prompt", ""),
                    "dialogue_ids": sorted(shot["dialogue_ids"]),
                    "pilot_shot": label,
                }
            )
    return {
        "schema_version": 1,
        "episode_id": manifest["episode_id"],
        "adhyay": adhyay,
        "research_version": receipt["version"],
        "research_sha256": receipt["research_sha256"],
        "manifest_sha256": sha256_file(episode_dir(project, adhyay) / "manifest.yaml"),
        "canon_sha256": canon.digest(),
        "visuals": sorted((dict(v) for v in visuals.values()), key=lambda v: v["visual_id"]),
        "shots": sorted(shots, key=lambda s: s["shot_id"]),
        "pilot": dict(sorted(pilot.items())),
    }


def compiled_digest(compiled: dict[str, Any]) -> str:
    return sha256_obj(compiled)


def ensure_complete(compiled: dict[str, Any]) -> None:
    if not compiled["shots"]:
        raise GateFailure("episode has no shots")
