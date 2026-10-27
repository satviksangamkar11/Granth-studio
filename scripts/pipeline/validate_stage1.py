from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema import Draft202012Validator

# ----------------------------------------------------------------------
# Schema loading (lazy, cached)
# ----------------------------------------------------------------------
_SCHEMA_CACHE: dict[str, dict[str, Any]] = {}
_ROOT = Path(__file__).resolve().parents[2]  # ROOT = parent of scripts/
_SCHEMA_DIR = _ROOT / "schemas"


def _load_schema(name: str) -> dict[str, Any]:
    if name not in _SCHEMA_CACHE:
        path = _SCHEMA_DIR / f"{name}.schema.json"
        _SCHEMA_CACHE[name] = json.loads(path.read_text(encoding="utf-8"))
    return _SCHEMA_CACHE[name]


# ----------------------------------------------------------------------
# Main validation function
# ----------------------------------------------------------------------
def validate_stage1(
    adhyay: int,
    scenes: dict[str, Any],
    shots: dict[str, Any],
    briefs: dict[str, Any],
    sounds: dict[str, Any],
    questions: dict[str, Any],
    script_line_ids: list[str],
    core_line_ids: set[str],
    chapter_ovis: set[int],
    unfilmed_ovis: set[int],
    palette_ids: set[str],
) -> list[str]:
    errors: list[str] = []

    # ------------------------------------------------------------------
    # Step 1: Schema validation for all five documents
    # ------------------------------------------------------------------
    schema_map = {
        "scenes": "stage1_scenes",
        "shots": "stage1_shots",
        "briefs": "stage1_image_briefs",
        "sounds": "stage1_sound_suggestions",
        "questions": "stage1_questions",
    }
    for doc_name, schema_name in schema_map.items():
        doc = locals()[doc_name]
        validator = Draft202012Validator(_load_schema(schema_name))
        for err in validator.iter_errors(doc):
            # json_path like "$.scenes[0].extra" -> we want "scenes[0].extra"
            path = err.json_path.lstrip("$.")
            errors.append(f"{doc_name} {path}: {err.message}")

    if errors:
        return errors

    # ------------------------------------------------------------------
    # Step 2: Adhyay consistency
    # ------------------------------------------------------------------
    for doc_name in schema_map:
        doc = locals()[doc_name]
        if doc.get("adhyay") != adhyay:
            errors.append(f"{doc_name} adhyay {doc.get('adhyay')} does not match {adhyay}")

    # ------------------------------------------------------------------
    # Helper structures for later steps
    # ------------------------------------------------------------------
    scene_list = scenes.get("scenes", [])
    shot_list = shots.get("shots", [])
    image_list = briefs.get("images", [])
    cue_list = sounds.get("cues", [])
    question_list = questions.get("questions", [])

    # Scene lookup by id
    scene_by_id: dict[str, dict[str, Any]] = {s["scene_id"]: s for s in scene_list}
    # Shot lookup by id
    shot_by_id: dict[str, dict[str, Any]] = {sh["shot_id"]: sh for sh in shot_list}
    # Shots grouped by scene_id in file order
    shots_by_scene: dict[str, list[dict[str, Any]]] = {}
    for sh in shot_list:
        shots_by_scene.setdefault(sh["scene_id"], []).append(sh)

    # Script line order index
    script_order = {lid: i for i, lid in enumerate(script_line_ids)}

    # ------------------------------------------------------------------
    # Step 3: Scenes validation
    # ------------------------------------------------------------------
    seen_scene_ids: set[str] = set()
    seen_line_ids: set[str] = set()
    covered_ovis: set[int] = set()

    for idx, sc in enumerate(scene_list):
        sid = sc["scene_id"]
        # duplicate scene id
        if sid in seen_scene_ids:
            errors.append(f"{sid}: duplicate scene id")
        seen_scene_ids.add(sid)

        lo, hi = sc["ovi_range"]
        # range invalid
        if lo > hi:
            errors.append(f"{sid}: range [{lo}, {hi}] is invalid")

        # overlap with previous scenes (file order)
        for prev in scene_list[:idx]:
            plo, phi = prev["ovi_range"]
            if not (hi < plo or lo > phi):
                errors.append(f"scenes {prev['scene_id']} and {sid} overlap")

        # ovi coverage checks
        for ovi in range(lo, hi + 1):
            covered_ovis.add(ovi)
            if ovi not in chapter_ovis:
                errors.append(f"{sid}: ovi {ovi} is not in the chapter")
            if ovi in unfilmed_ovis:
                errors.append(f"{sid}: ovi {ovi} is unfilmed but inside the range")

        # turn ovi
        turn_ovi = sc["turn"]["ovi"]
        if not (lo <= turn_ovi <= hi):
            errors.append(f"{sid}: turn ovi {turn_ovi} is outside its range")

        # line_ids checks
        line_ids = sc["line_ids"]
        # line not in script
        for lid in line_ids:
            if lid not in script_order:
                errors.append(f"{sid}: line {lid} is not in the script")
        # duplicate line within or across scenes
        for lid in line_ids:
            if lid in seen_line_ids:
                errors.append(f"{lid}: line used twice")
            seen_line_ids.add(lid)
        # script order
        if line_ids:
            indices = [script_order[lid] for lid in line_ids if lid in script_order]
            if indices != sorted(indices):
                errors.append(f"{sid}: lines are not in script order")

    # ovi not covered and not unfilmed
    for ovi in sorted(chapter_ovis):
        if ovi not in covered_ovis and ovi not in unfilmed_ovis:
            errors.append(f"ovi {ovi} is in no scene and not unfilmed")

    # core line in no scene
    for core in sorted(core_line_ids):
        if core not in seen_line_ids:
            errors.append(f"{core}: core line is in no scene")

    # ------------------------------------------------------------------
    # Step 4: Shots validation
    # ------------------------------------------------------------------
    seen_shot_ids: set[str] = set()
    core_in_shot_beat: set[str] = set()

    for sh in shot_list:
        shid = sh["shot_id"]
        # duplicate shot id
        if shid in seen_shot_ids:
            errors.append(f"{shid}: duplicate shot id")
        seen_shot_ids.add(shid)

        scid = sh["scene_id"]
        # scene exists
        if scid not in scene_by_id:
            errors.append(f"{shid}: scene {scid} does not exist")
            continue  # further checks need scene

        scene = scene_by_id[scid]
        lo, hi = scene["ovi_range"]

        # ovi_ids outside scene range
        for ovi in sh["ovi_ids"]:
            if not (lo <= ovi <= hi):
                errors.append(f"{shid}: ovi {ovi} is outside scene {scid} range [{lo}, {hi}]")

        # beat_line_ids are lines of the scene
        scene_line_ids = set(scene["line_ids"])
        for bline in sh["beat_line_ids"]:
            if bline not in scene_line_ids:
                errors.append(f"{shid}: beat line {bline} is not a line of scene {scid}")
            core_in_shot_beat.add(bline)

    # consecutive shot ids per scene (file order); every scene needs shots
    for scid in scene_by_id:
        own = [sh for sh in shot_list if sh["scene_id"] == scid]
        if not own:
            errors.append(f"{scid}: scene has no shots")
            continue
        for i, sh in enumerate(own):
            if sh["shot_id"] != f"{scid}-{i + 1}":
                errors.append(f"{scid}: shot ids must be consecutive from {scid}-1 (found {sh['shot_id']})")

    # every line of every scene (core or optional) must be spoken in some shot
    for scid, scene in scene_by_id.items():
        for lid in scene["line_ids"]:
            if lid not in core_in_shot_beat:
                errors.append(f"{lid}: core line is in no shot beat" if lid in core_line_ids else f"{lid}: line is in no shot beat")

    # ------------------------------------------------------------------
    # Step 5: Briefs validation
    # ------------------------------------------------------------------
    seen_image_ids: set[str] = set()

    for img in image_list:
        iid = img["image_id"]
        # prefix check
        scid = img["scene_id"]
        expected_prefix = scid.lower() + "_"
        if not iid.startswith(expected_prefix):
            errors.append(f"{iid}: id must start with the scene prefix {expected_prefix}")

        # duplicate image id
        if iid in seen_image_ids:
            errors.append(f"{iid}: duplicate image id")
        seen_image_ids.add(iid)

        # scene exists
        if scid not in scene_by_id:
            errors.append(f"{iid}: scene {scid} does not exist")
            continue

        # shot_ids exist and belong to same scene
        for shot_id in img["shot_ids"]:
            if shot_id not in shot_by_id:
                errors.append(f"{iid}: shot {shot_id} does not exist")
            else:
                if shot_by_id[shot_id]["scene_id"] != scid:
                    errors.append(f"{iid}: shot {shot_id} is not in the same scene")

    # ------------------------------------------------------------------
    # Step 6: Sounds validation
    # ------------------------------------------------------------------
    for cue in cue_list:
        scid = cue["scene_id"]
        # cue scene exists
        if scid not in scene_by_id:
            errors.append(f"{scid}: cue scene does not exist")
            continue

        scene = scene_by_id[scid]
        anchor = cue["anchor_line_id"]
        # anchor line is a line of the scene
        if anchor not in scene["line_ids"]:
            errors.append(f"{anchor}: anchor line is not a line of scene {scid}")

        palette = cue["palette_id"]
        # palette check
        if palette != "NEED_NEW":
            if palette not in palette_ids:
                errors.append(f"{palette}: not in the palette")
        else:
            reason = cue.get("reason", "").strip()
            if not reason:
                errors.append("NEED_NEW needs a reason")

        # kind mismatch
        kind = cue.get("kind", "")
        if palette.startswith("bed_") and kind != "bed":
            errors.append(f"{palette}: kind {kind} does not match")
        elif palette.startswith("fx_") and kind != "fx":
            errors.append(f"{palette}: kind {kind} does not match")

    # ------------------------------------------------------------------
    # Step 7: Questions validation
    # ------------------------------------------------------------------
    seen_question_ids: set[str] = set()

    for q in question_list:
        qid = q["id"]
        # duplicate question id
        if qid in seen_question_ids:
            errors.append(f"{qid}: duplicate question id")
        seen_question_ids.add(qid)

        scid = q.get("scene_id")
        if scid is not None and scid not in scene_by_id:
            errors.append(f"{qid}: scene {scid} does not exist")

    return errors
