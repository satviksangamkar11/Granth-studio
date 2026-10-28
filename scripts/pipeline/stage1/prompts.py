from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]

SHARED_RULE_BLOCK = (
    "Use only locked source, research and owner decisions. Cite chapter-qualified ovis for facts. "
    "Reuse registered IDs; report missing identities. Never invent events, motives, miracles, dialogue or closure. "
    "Reference immutable EASY line IDs; never write, edit, translate or critique their wording. "
    "Thoughts and unclear speech remain narrator material. "
    "Separate sourced facts from STAGING and inferred visual looks. "
    "Preserve required teachings and explicit coverage; only the owner approves omissions. "
    "Use supplied preset capabilities and sound availability; report NEED_NEW honestly. "
    "Output only this call's schema. No timings, hashes, approvals, API calls or code."
)

CALLS = ("map", "plan", "scene")

OUTPUT_KEYS = {
    "map": ("story_map",),
    "plan": ("coverage", "scenes"),
    "scene": ("shots", "briefs", "looks", "voices", "sounds", "questions"),
}

_UNIT_MODULES = {
    "story_map": "scripts/pipeline/stage1/story_map.py",
    "coverage": "scripts/pipeline/stage1/coverage.py",
    "scenes": "scripts/pipeline/stage1/scenes.py",
    "shots": "scripts/pipeline/stage1/shots.py",
    "briefs": "scripts/pipeline/stage1/briefs.py",
    "looks": "scripts/pipeline/stage1/looks.py",
    "voices": "scripts/pipeline/stage1/voices.py",
    "sounds": "scripts/pipeline/stage1/sounds.py",
    "questions": "scripts/pipeline/stage1/questions.py",
}


def _load_module(name: str, rel_path: str):
    path = REPO_ROOT / rel_path
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _get_unit_schema(key: str) -> dict:
    rel = _UNIT_MODULES[key]
    mod = _load_module(key, rel)
    return mod.SCHEMA


def _read_jsonl(path: Path) -> tuple[list[dict], list[str]]:
    records = []
    problems = []
    if not path.exists():
        return records, problems
    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                problems.append(f"ovis: bad line {i} ({e.__class__.__name__})")
                continue
            if not isinstance(obj, dict):
                problems.append(f"ovis: bad line {i} (not an object)")
                continue
            ovi = obj.get("ovi")
            if not isinstance(ovi, int):
                problems.append(f"ovis: bad line {i} (missing or non-int ovi)")
                continue
            rec = {"ovi": ovi}
            for field in ("original_marathi", "simple_marathi", "hindi", "easy_english", "section", "text"):
                if field in obj:
                    rec[field] = obj[field]
            records.append(rec)
    records.sort(key=lambda r: r["ovi"])
    return records, problems


def _read_json_file(path: Path, source: str) -> tuple[Any, list[str]]:
    problems = []
    if not path.exists():
        return None, [f"{source}: missing"]
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return None, [f"{source}: {e.__class__.__name__}"]
    return data, problems


def _extract_list(doc: Any, key: str) -> list:
    """Extract a list from a document that may be a dict with `key` or a bare list."""
    if isinstance(doc, list):
        return doc
    if isinstance(doc, dict):
        val = doc.get(key)
        if isinstance(val, list):
            return val
    return []


def build_packet(adhyay: int, root: Path | str) -> tuple[dict, list[str]]:
    problems: list[str] = []
    packet: dict = {"adhyay": adhyay}

    if not isinstance(adhyay, int) or not (1 <= adhyay <= 21):
        return {}, ["adhyay must be an int in 1..21"]

    root = Path(root)
    chapter_mod = _load_module("chapter", "scripts/pipeline/chapter.py")
    paths = chapter_mod.chapter_paths(adhyay, root)

    # ovis
    ovis_path = paths.get("source_ovis")
    if ovis_path and ovis_path.exists():
        ovis, ovis_probs = _read_jsonl(ovis_path)
        packet["ovis"] = ovis
        problems.extend(ovis_probs)
    else:
        packet["ovis"] = []
        problems.append("ovis: missing")

    # research
    if adhyay == 1:
        packet["research"] = {}
    else:
        research_path = paths.get("research_packet")
        if research_path and research_path.exists():
            research_data, research_probs = _read_json_file(research_path, "research")
            if research_probs:
                problems.extend(research_probs)
                packet["research"] = {}
            elif isinstance(research_data, dict):
                packet["research"] = research_data
            else:
                problems.append("research: bad shape")
                packet["research"] = {}
        else:
            packet["research"] = {}

    # script
    script_path = paths.get("script")
    script_records = []
    if script_path and script_path.exists():
        try:
            check_mod = _load_module("check_script", "scripts/pipeline/check_script.py")
            text = script_path.read_text(encoding="utf-8")
            parsed = check_mod.parse_script(text)
            for rec in parsed:
                script_records.append({
                    "id": rec.get("id"),
                    "scene": rec.get("scene"),
                    "voice": rec.get("voice"),
                    "ovi": rec.get("ovi"),
                    "priority": rec.get("priority"),
                    "marathi": rec.get("marathi"),
                    "hindi": rec.get("hindi"),
                })
        except Exception as e:
            problems.append(f"script: {e.__class__.__name__}")
            script_records = []
    else:
        problems.append("script: missing")
    packet["script"] = script_records

    # presets
    presets_path = root / "assets" / "v5_presets" / "index.json"
    if presets_path.exists():
        presets_data, presets_probs = _read_json_file(presets_path, "presets")
        if presets_probs:
            problems.extend(presets_probs)
            packet["presets"] = []
        elif isinstance(presets_data, list):
            packet["presets"] = presets_data
        else:
            problems.append("presets: bad shape")
            packet["presets"] = []
    else:
        problems.append("presets: missing")
        packet["presets"] = []

    # sounds
    sounds_path = root / "canon" / "series" / "sounds" / "palette.json"
    if sounds_path.exists():
        sounds_data, sounds_probs = _read_json_file(sounds_path, "sounds")
        if sounds_probs:
            problems.extend(sounds_probs)
            packet["sounds"] = []
        elif isinstance(sounds_data, dict) and isinstance(sounds_data.get("sounds"), list):
            packet["sounds"] = sounds_data["sounds"]
        elif isinstance(sounds_data, list):
            packet["sounds"] = sounds_data
        else:
            problems.append("sounds: bad shape")
            packet["sounds"] = []
    else:
        packet["sounds"] = []

    # voices
    voices_path = root / "canon" / "series" / "voices.json"
    if voices_path.exists():
        voices_data, voices_probs = _read_json_file(voices_path, "voice_library")
        if voices_probs:
            problems.extend(voices_probs)
            packet["voices"] = []
        elif isinstance(voices_data, dict) and isinstance(voices_data.get("voices"), list):
            kept = []
            for v in voices_data["voices"]:
                if isinstance(v, dict):
                    kept.append({
                        "voice_key": v.get("voice_key"),
                        "voice_id": v.get("voice_id"),
                        "name": v.get("name"),
                        "gender": v.get("gender"),
                        "age": v.get("age"),
                        "accent": v.get("accent"),
                        "description": v.get("description"),
                        "owner_note": v.get("owner_note"),
                        "marathi_verified": v.get("marathi_verified"),
                        "hindi_verified": v.get("hindi_verified"),
                        "assigned_to": v.get("assigned_to"),
                        "status": v.get("status"),
                    })
            packet["voices"] = kept
        else:
            problems.append("voice_library: bad shape")
            packet["voices"] = []
    else:
        problems.append("voice_library: missing")
        packet["voices"] = []

    return packet, problems


def _system_prompt(call: str, adhyay: int) -> str:
    role = (
        "You are a planning assistant for a motion-comic film pipeline. "
        "You plan only; you never write the owner's script."
    )
    output_keys = OUTPUT_KEYS[call]
    # Build wrapper skeleton for this call
    wrapper_parts = []
    for key in output_keys:
        wrapper_parts.append(f'"{key}": {{ "adhyay": <N>, ... }}')
    wrapper_str = "{" + ", ".join(wrapper_parts) + "}"

    # Adhyay sentence for every call
    adhyay_sentence = (
        f'In every document the field "adhyay" is the CHAPTER number {adhyay} '
        '(the same number in every call and every document; never the scene number or any other number).'
    )

    output_para = (
        "Reply with ONE JSON object only (no markdown fences, no prose) "
        f"whose top-level keys are exactly {list(output_keys)}, "
        "each value a complete document that includes \"adhyay\": <N>. "
        f"The response must be wrapped exactly as: {wrapper_str}. "
        "Do NOT return a document directly; every document must sit under its key. "
        f"{adhyay_sentence}"
    )

    if call == "scene":
        # One-line skeleton for the six keys
        skeleton = (
            '{"shots": {"adhyay": <N>, ...}, "briefs": {"adhyay": <N>, ...}, '
            '"looks": {"adhyay": <N>, ...}, "voices": {"adhyay": <N>, ...}, '
            '"sounds": {"adhyay": <N>, ...}, "questions": {"adhyay": <N>, ...}}'
        )
        scene_extra = (
            "The reply object has SIX separate top-level keys: shots, briefs, looks, voices, sounds, questions. "
            "Never nest one document inside another. "
            f"The top-level structure is: {skeleton}."
        )
        output_para += " " + scene_extra

    return f"{role}\nRULES:\n{SHARED_RULE_BLOCK}\n{output_para}"


def _user_prompt(call: str, packet: dict, scene_ids: list[str] | None, prior: dict | None) -> str:
    sections = []

    # TASK
    if call == "map":
        task = (
            "Classify EVERY ovi once (types STORY, TEACHING, PHILOSOPHY, INVOCATION, RECAP, PHALASHRUTI, OTHER), "
            "identify the COMPLETE events (each with an event_id, kind story or discourse, title, ovi_range, key_ovis "
            "and closure: RESOLVED_IN_ADHYAY, CONTINUES_NEXT_ADHYAY, STARTED_EARLIER, "
            "SOURCE_INCOMPLETE_OR_AMBIGUOUS or NA); "
            "every STORY ovi must lie in an event of kind story and every TEACHING ovi in an event of kind discourse; "
            "type does not decide omission."
        )
        chapter_data = {"ovis": packet["ovis"], "research": packet["research"]}
    elif call == "plan":
        task = (
            "Give every ovi exactly one disposition (VISUALISED, NARRATED, QUOTED, MERGED_EQUIVALENT with covered_by "
            "and reason, PROPOSE_OMISSION with a reason) and order the scenes (scene_id, section_kind story|discourse, "
            "ovi_range, goal, line_ids from the script in reading order, teaching_treatment for discourse scenes, "
            "the `turn` field as the schema requires); "
            "film what contributes to the story and the teaching, propose omissions only for the rest; "
            "existing script ids and order are immutable."
        )
        chapter_data = {
            "ovis": packet["ovis"],
            "script": packet["script"],
            "PRIOR": prior.get("story_map") if prior else None,
        }
    elif call == "scene":
        if not scene_ids:
            raise ValueError("scene call requires scene_ids")
        if not prior or not all(k in prior for k in ("story_map", "coverage", "scenes")):
            raise ValueError("scene call requires prior with story_map, coverage, scenes")
        scene_set = set(scene_ids)
        script_lines = [ln for ln in packet["script"] if ln.get("scene") in scene_set]
        ovi_set = {ln["ovi"] for ln in script_lines if ln.get("ovi") is not None}
        ovis = [ov for ov in packet["ovis"] if ov["ovi"] in ovi_set]

        # Extract lists from prior documents (which may be dicts with a key or bare lists)
        scene_cards_doc = prior.get("scenes", {})
        scene_cards_all = _extract_list(scene_cards_doc, "scenes")
        scene_cards = [sc for sc in scene_cards_all if sc.get("scene_id") in scene_set]

        coverage_doc = prior.get("coverage", {})
        coverage_all = _extract_list(coverage_doc, "ovis")
        coverage = [c for c in coverage_all if c.get("ovi") in ovi_set]

        story_map_doc = prior.get("story_map", {})
        events_all = _extract_list(story_map_doc, "events")
        events = []
        for ev in events_all:
            ev_ovis = set(range(ev["ovi_range"][0], ev["ovi_range"][1] + 1))
            if ev_ovis & ovi_set:
                events.append(ev)

        task = (
            "For ONLY the scenes in scene_ids produce shots (use a preset id from the preset list when one fits, "
            "flat images first, else NEED_NEW with reason and class), image briefs (include the image-brief lessons "
            "below), canon looks (stated vs inferred), voice casting (by DESCRIPTION from the voice library; a "
            "RECURRING character keeps the voice it is assigned to; a new character gets the best-matching unassigned "
            "voice with a short `reason`; if no saved voice fits raise a question, never invent a voice id), sound "
            "suggestions (reuse an available palette sound id else NEED_NEW with an ElevenLabs-ready sound prompt; "
            "silence is valid; no music; nothing automatic from presets), and questions for every ambiguity (never a "
            "silent guess)."
        )
        sounds = packet["sounds"]
        if not sounds:
            palette_msg = "The sound palette is empty: every sound is NEED_NEW."
        else:
            palette_msg = None

        chapter_data = {
            "script_lines": script_lines,
            "ovis": ovis,
            "scene_cards": scene_cards,
            "presets": packet["presets"],
            "sound_palette": sounds,
            "sound_palette_note": palette_msg,
            "voice_library": packet["voices"],
            "research": packet["research"],
            "PRIOR": {
                "story_map_events": events,
                "coverage": coverage,
                "scene_cards": scene_cards,
            },
        }
    else:
        raise ValueError(f"Unknown call: {call}")

    sections.append(f"TASK\n{task}")

    # OUTPUT SCHEMAS
    schema_lines = []
    for key in OUTPUT_KEYS[call]:
        schema = _get_unit_schema(key)
        schema_str = json.dumps(schema, ensure_ascii=False, sort_keys=True, indent=1)
        schema_lines.append(f"{key}\n{schema_str}")
    sections.append("OUTPUT SCHEMAS\n" + "\n\n".join(schema_lines))

    # CHAPTER DATA
    chapter_json = json.dumps(chapter_data, ensure_ascii=False, separators=(",", ":"))
    sections.append(f"CHAPTER DATA\n{chapter_json}")

    # MUST NOT
    must_not = (
        "- never write/edit/translate/critique the EASY script\n"
        "- no timings, hashes or approvals\n"
        "- no invented events, dialogue or closure\n"
        "- no images or voices\n"
        "- no code\n"
        "- no invented preset or image or voice id\n"
        "- no redeciding of known cast, place or style\n"
        "- omissions are only PROPOSED, the owner decides"
    )
    sections.append(f"MUST NOT\n{must_not}")

    # Image-brief lessons for scene call
    if call == "scene":
        lessons = (
            "Image-brief lessons: approved flat-colour style; full chapter-state identity of each character; "
            "exactly the visible people, each once with position, ONE action and gaze target; accepted place and "
            "fixed features; critical prop and its state; framing, angle, screen directions across adjoining cuts; "
            "preset slot, full-frame or layer need, safe crop; approved light; ONLY on-screen facts (no narration "
            "or commentary); exclude extra people, text, inset frames and modern objects; references are the visible "
            "characters, the place, one style anchor and the central prop."
        )
        sections.append(f"IMAGE BRIEF LESSONS\n{lessons}")

    return "\n\n".join(sections)


def build_prompt(call: str, packet: dict, *, scene_ids: list[str] | None = None, prior: dict | None = None) -> tuple[str, str]:
    if call not in CALLS:
        raise ValueError(f"Unknown call: {call}")
    if call == "plan" and (not prior or "story_map" not in prior):
        raise ValueError("plan call requires prior with story_map")
    if call == "scene":
        if not scene_ids:
            raise ValueError("scene call requires scene_ids")
        if not prior or not all(k in prior for k in ("story_map", "coverage", "scenes")):
            raise ValueError("scene call requires prior with story_map, coverage, scenes")

    system = _system_prompt(call, packet["adhyay"])
    user = _user_prompt(call, packet, scene_ids, prior)
    return system, user


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 3)
