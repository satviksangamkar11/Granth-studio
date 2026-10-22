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
    if manifest["episode_id"] != f"ep{adhyay:02d}":
        raise ConfigError("episode_id does not match adhyay")
    expected_scenes = [s["scene_id"] for s in research["scenes"]]
    actual_scenes = [s["research_scene"] for s in manifest["scenes"]]
    if actual_scenes != expected_scenes:
        raise GateFailure("manifest must cover every approved scene exactly once in approved order")
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
        source_scene = scenes_by_id[scene["research_scene"]]
        if scene["scene_id"] != scene["research_scene"]:
            raise GateFailure("scene_id must equal its research_scene")
        if scene["location"] != source_scene["location"] or set(scene["characters"]) != set(source_scene["characters"]):
            raise CanonReferenceError("scene location/speaker/cast differs from approved research")
        if scene.get("props", []) != source_scene.get("props", []):
            raise GateFailure("scene props differ from approved research")
        expected_lines = [line["id"] for line in source_scene["dialogue"]]
        actual_lines = [line for shot in scene["shots"] for line in shot["dialogue_ids"]]
        if actual_lines != expected_lines:
            raise GateFailure("shots must cover all approved dialogue once in approved order")
        for prop in scene.get("props", []):
            canon.require(prop, "props")
        canon.require(scene["location"], "locations")
        for char_id in scene["characters"]:
            canon.require(char_id, "characters")
        action_facts = {fact["id"]: fact for fact in source_scene["actions"]}
        if len(action_facts) != len(source_scene["actions"]):
            raise ConfigError("duplicate approved action ID")
        required_actions = {key for key, fact in action_facts.items() if not fact["artistic"]}
        covered_actions = {key for shot in scene["shots"] for key in shot.get("action_ids", [])}
        if not required_actions <= covered_actions or not covered_actions <= set(action_facts):
            raise GateFailure("shots must reference every required approved action and no invented actions")
        for shot in scene["shots"]:
            action_ids = shot.get("action_ids", [])
            approved_motion = "; ".join(action_facts[key]["text"] for key in action_ids)
            if shot.get("motion_prompt", approved_motion) != approved_motion:
                raise GateFailure("motion prompt differs from referenced approved action text")
            if shot["tier"] in (1, 2) and not approved_motion:
                raise GateFailure("motion generation requires approved action references")
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
            if shot.get("cutaway") and shot["dialogue_ids"]:
                raise ConfigError(f"{shot_id}: a cutaway shot carries no dialogue")
            cover = shot.get("coverage")
            if cover and cover["mode"] == "cutaway":
                target = next((o for o in scene["shots"] if o["shot_id"] == cover["shot_id"]), None)
                if cover["shot_id"] == shot_id:
                    raise ConfigError(f"{shot_id}: a shot cannot be its own cutaway")
                if target is None:
                    raise ConfigError(f"{shot_id}: cutaway shot {cover['shot_id']} is not in scene {scene['scene_id']}")
                if not target.get("cutaway"):
                    raise ConfigError(f"{shot_id}: cutaway target {cover['shot_id']} is not flagged cutaway: true")
                if target["dialogue_ids"]:
                    raise ConfigError(f"{shot_id}: cutaway target {cover['shot_id']} must carry no dialogue")
                if target.get("coverage"):
                    raise ConfigError(f"{shot_id}: cutaway target {cover['shot_id']} must not have coverage of its own")
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
            fallback = shot.get("fallback")
            if fallback is not None:
                if shot["tier"] == 0:
                    raise ConfigError(f"{shot_id}: a Tier 0 shot has nothing to fall back from")
                if fallback["kind"] == "ambient" and set(action_ids) & required_actions:
                    raise GateFailure(f"{shot_id}: an ambient fallback cannot replace a required approved action; "
                                      "use kind 'faithful' only if a reviewer attests Tier 0 still shows the action")
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
                    "motion_prompt": approved_motion,
                    "action_ids": list(action_ids),
                    "dialogue_ids": list(shot["dialogue_ids"]),
                    "research_scene": dict(source_scene),
                    "location": scene["location"],
                    "characters": list(scene["characters"]),
                    "props": list(scene.get("props", [])),
                    "lighting": scene.get("lighting", "unspecified"),
                    "artistic_flags": list(scene.get("artistic_flags", [])),
                    "cutaway": bool(shot.get("cutaway")),
                    "coverage": shot.get("coverage"),
                    "fallback": shot.get("fallback"),
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
        "shots": shots,
        "research_scenes": research["scenes"],
        "pilot": dict(sorted(pilot.items())),
    }


def compiled_digest(compiled: dict[str, Any]) -> str:
    return sha256_obj(compiled)


def ensure_complete(compiled: dict[str, Any]) -> None:
    if not compiled["shots"]:
        raise GateFailure("episode has no shots")
