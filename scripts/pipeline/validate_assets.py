from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS_DIR = ROOT / "schemas"


def _load_schema(name: str) -> dict:
    path = SCHEMAS_DIR / f"{name}.schema.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _validate_schema(document: str, data: dict, schema_name: str) -> list[str]:
    schema = _load_schema(schema_name)
    validator = Draft202012Validator(schema)
    errors = []
    for err in sorted(validator.iter_errors(data), key=lambda e: e.path):
        path = ".".join(str(p) for p in err.path) if err.path else "(root)"
        errors.append(f"{document} {path}: {err.message}")
    return errors


def validate_beats(
    adhyay: int,
    beats: dict,
    script_line_ids: set[str],
    shot_seconds: float = 6.0,
    tolerance: float = 0.01,
) -> list[str]:
    errors = []

    if not (isinstance(shot_seconds, (int, float)) and math.isfinite(shot_seconds) and shot_seconds > 0):
        return ["shot_seconds must be a finite number > 0"]
    if not (isinstance(tolerance, (int, float)) and math.isfinite(tolerance) and tolerance >= 0):
        return ["tolerance must be a finite number >= 0"]

    errors.extend(_validate_schema("beats", beats, "beats"))
    if errors:
        return errors

    if beats.get("adhyay") != adhyay:
        return [f"beats adhyay {beats.get('adhyay')} does not match {adhyay}"]

    seen_scenes = set()
    seen_lines = set()
    for scene in beats.get("scenes", []):
        scene_id = scene.get("scene_id")
        if scene_id in seen_scenes:
            errors.append(f"{scene_id}: duplicate scene")
        seen_scenes.add(scene_id)

        beats_list = scene.get("beats", [])
        if not beats_list:
            errors.append(f"{scene_id}: no beats")

        prev_start = None
        prev_end = None
        prev_line = None
        for beat in beats_list:
            line_id = beat.get("line_id")
            if line_id not in script_line_ids:
                errors.append(f"{line_id}: line is not in the script")
            if line_id in seen_lines:
                errors.append(f"{line_id}: duplicate line")
            seen_lines.add(line_id)

            start_s = beat.get("start_s")
            end_s = beat.get("end_s")
            if end_s <= start_s:
                errors.append(f"{line_id}: end must be after start")

            mr_s = beat.get("mr_s", 0)
            hi_s = beat.get("hi_s", 0)
            longer = max(mr_s, hi_s)
            if end_s - start_s < longer - tolerance:
                errors.append(f"{line_id}: beat is shorter than the longer language")

            shot = beat.get("shot")
            expected_shot = int(math.floor(start_s / shot_seconds)) + 1
            if shot != expected_shot:
                errors.append(f"{line_id}: shot {shot} does not match start (expected {expected_shot})")

            if prev_start is not None:
                if start_s < prev_start:
                    errors.append(f"{scene_id}: beats are not in time order")
                elif start_s < prev_end:
                    errors.append(f"{scene_id}: beats {prev_line} and {line_id} overlap")
            prev_start = start_s
            prev_end = end_s
            prev_line = line_id

    return errors


def validate_catalog(
    adhyay: int,
    catalog: dict,
    image_dir: Path,
    check_files: bool = True,
) -> list[str]:
    errors = []

    errors.extend(_validate_schema("catalog", catalog, "image_catalog"))
    if errors:
        return errors

    if catalog.get("adhyay") != adhyay:
        return [f"catalog adhyay {catalog.get('adhyay')} does not match {adhyay}"]

    images = catalog.get("images", {})
    id_pattern = re.compile(r"^SH_S\d{1,2}_\d{2}$")
    sha256_to_id = {}
    for key, entry in images.items():
        if not id_pattern.match(key):
            errors.append(f"{key}: bad catalog id")
        file_name = entry.get("file", "")
        if "/" in file_name or "\\" in file_name or file_name == "..":
            errors.append(f"{key}: file name must not contain a path")
        sha = entry.get("sha256")
        if sha in sha256_to_id:
            errors.append(f"{key}: duplicate image (same sha256 as {sha256_to_id[sha]})")
        else:
            sha256_to_id[sha] = key

    if check_files:
        for key, entry in images.items():
            file_name = entry.get("file", "")
            file_path = (image_dir / file_name).resolve()
            try:
                if not file_path.is_relative_to(image_dir.resolve()):
                    errors.append(f"{key}: file missing or unreadable")
                    continue
                if not file_path.is_file():
                    errors.append(f"{key}: file missing or unreadable")
                    continue
                hasher = hashlib.sha256()
                with file_path.open("rb") as f:
                    for chunk in iter(lambda: f.read(65536), b""):
                        hasher.update(chunk)
                if hasher.hexdigest() != entry.get("sha256"):
                    errors.append(f"{key}: sha256 does not match the file")
            except OSError:
                errors.append(f"{key}: file missing or unreadable")

    return errors


def validate_animation(
    adhyay: int,
    scene: dict,
    catalog: dict,
    presets: dict[str, list[str]],
    expected_shots: int | None = None,
) -> list[str]:
    errors = []

    errors.extend(_validate_schema("animation", scene, "animation_scene"))
    if errors:
        return errors

    if scene.get("adhyay") != adhyay:
        return [f"animation adhyay {scene.get('adhyay')} does not match {adhyay}"]

    scene_id = scene.get("scene_id")
    shots = scene.get("shots", [])
    if expected_shots is not None and len(shots) != expected_shots:
        errors.append(f"expected {expected_shots} shots, found {len(shots)}")

    for idx, shot in enumerate(shots, 1):
        shot_id = shot.get("shot_id")
        expected_id = f"{scene_id}-{idx}"
        if shot_id != expected_id:
            errors.append(f"{shot_id}: shot ids must be consecutive")

        preset = shot.get("preset")
        need_new = shot.get("need_new")
        assets = shot.get("assets", {})

        if preset != "NEED_NEW":
            if need_new is not None:
                errors.append(f"{shot_id}: need_new must be null unless preset is NEED_NEW")
            if preset not in presets:
                errors.append(f"{shot_id}: unknown preset {preset}")
            else:
                required_roles = set(presets[preset])
                if set(assets.keys()) != required_roles:
                    errors.append(f"{shot_id}: assets must have exactly the roles {sorted(required_roles)}")
            for role, img_id in assets.items():
                if img_id not in catalog.get("images", {}):
                    errors.append(f"{shot_id}: {img_id} is not in the catalog")
                elif not catalog["images"][img_id].get("approved", False):
                    errors.append(f"{shot_id}: {img_id} is not approved")
        else:
            if not isinstance(need_new, dict) or need_new is None:
                errors.append(f"{shot_id}: NEED_NEW needs need_new")
            if assets:
                errors.append(f"{shot_id}: NEED_NEW shot must have empty assets")

    return errors


def fingerprint_images(catalog: dict, ids: list[str]) -> dict[str, str]:
    images = catalog.get("images", {})
    result = {}
    for id_ in ids:
        if id_ not in images:
            raise KeyError(id_)
        result[id_] = images[id_]["sha256"]
    return result


def validate_shot_plan_fresh(plan: dict, current: dict) -> list[str]:
    errors = []
    fp = plan.get("fingerprints", {})

    if fp.get("script") != current.get("script"):
        errors.append("script changed")
    if fp.get("timing") != current.get("timing"):
        errors.append("timing changed")
    if fp.get("presets") != current.get("presets"):
        errors.append("presets changed")

    fp_images = fp.get("images", {})
    cur_images = current.get("images", {})
    for img_id, fp_hash in fp_images.items():
        cur_hash = cur_images.get(img_id)
        if cur_hash is None:
            errors.append(f"image {img_id} is missing from the current images")
        elif cur_hash != fp_hash:
            errors.append(f"image {img_id} changed")

    used_images = set()
    for shot in plan.get("shots", []):
        for img_id in shot.get("assets", {}).values():
            used_images.add(img_id)
    for img_id in used_images:
        if img_id not in fp_images:
            errors.append(f"image {img_id} is used but not fingerprinted")

    return errors
