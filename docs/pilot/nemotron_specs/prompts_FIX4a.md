# SPEC: NEW `scripts/pipeline/stage1/prompts.py` + NEW `tests/test_stage1_prompts.py`. Return exactly these TWO files in full; do not output or change any other file.
Purpose (checklist S4/V3): build, by CODE and for ANY Adhyay (1..21), the prompts of the three Stage 1 planning calls from the chapter data, so the model gets the same rules every time. This module only builds text and a data packet; it makes no model call, reads no key and writes nothing. Standard library only; `from __future__ import annotations`; nothing at import time except imports and definitions; plain functions, no classes. Do not over-engineer. Nothing may be specific to one chapter.

## Existing code you may use (load by importlib BY PATH; do not modify)
- `scripts/pipeline/chapter.py`: `chapter_paths(adhyay, root) -> dict[str, Path]` (keys `source_ovis`, `research_packet`, `script`, ...).
- `scripts/pipeline/check_script.py`: `parse_script(text) -> list[dict]`; each record has `id` (like S1-L1), `scene` (like S1), `voice`, `ovi` (int), `priority` (core|optional), `marathi`, `hindi`, `heading`.
- `scripts/pipeline/stage1/<unit>.py` for unit in story_map, coverage, scenes, shots, briefs, looks, voices, sounds, questions: each has a dict `SCHEMA` (the JSON Schema of its document, with the field `adhyay`).
- `scripts/pipeline/stage1/context.py`: `build_ctx(adhyay, root) -> (ctx, problems)`.
Repo root in this module: `Path(__file__).resolve().parents[3]`; in tests `Path(__file__).resolve().parents[1]`.
Data files relative to `root`: ovis `chapter_paths(...)["source_ovis"]` (jsonl; each object has `ovi` and either the fields `original_marathi`, `simple_marathi`, `hindi`, `easy_english`, `section`, or a single `text`); research packet `chapter_paths(...)["research_packet"]` (a JSON file for chapters after 1; for Adhyay 1 it is a folder: then skip it); script `chapter_paths(...)["script"]` (markdown in the EASY format); presets `assets/v5_presets/index.json` (list of objects with `preset`, `use`, `assets`, `simplest_renderer`); sound palette `canon/series/sounds/palette.json` (object with a list `sounds` of objects with `id`, or a plain list; may be absent); voice library `canon/series/voices.json` (object with a list `voices`; each has `voice_key`, `voice_id`, `name`, `gender`, `age`, `accent`, `description`, `owner_note`, `marathi_verified`, `hindi_verified`, `assigned_to`, `status`).

## Constants
- `SHARED_RULE_BLOCK` = exactly this text: `Use only locked source, research and owner decisions. Cite chapter-qualified ovis for facts. Reuse registered IDs; report missing identities. Never invent events, motives, miracles, dialogue or closure. Reference immutable EASY line IDs; never write, edit, translate or critique their wording. Thoughts and unclear speech remain narrator material. Separate sourced facts from STAGING and inferred visual looks. Preserve required teachings and explicit coverage; only the owner approves omissions. Use supplied preset capabilities and sound availability; report NEED_NEW honestly. Output only this call's schema. No timings, hashes, approvals, API calls or code.`
- `CALLS = ("map", "plan", "scene")`.
- `OUTPUT_KEYS = {"map": ("story_map",), "plan": ("coverage", "scenes"), "scene": ("shots", "briefs", "looks", "voices", "sounds", "questions")}`.

## API
- `build_packet(adhyay: int, root: Path | str) -> tuple[dict, list[str]]`: NEVER raises. Returns `(packet, problems)`; an invalid adhyay gives `({}, ["adhyay must be an int in 1..21"])`. packet keys: `adhyay`; `ovis` (list of the ovi records, each reduced to `ovi` plus the text fields that exist; sorted by ovi; bad lines skipped with a problem `ovis: bad line <n>`); `research` (the JSON object or `{}`); `script` (list of the parse_script records reduced to `id, scene, voice, ovi, priority, marathi, hindi`; `[]` if the script file is missing with the problem `script: missing`); `presets` (the list from the index, in file order; missing -> `[]` and problem `presets: missing`); `sounds` (list of palette sound objects, `[]` if absent, no problem); `voices` (the library list reduced to the fields `voice_key, voice_id, name, gender, age, accent, description, owner_note, marathi_verified, hindi_verified, assigned_to, status`; missing -> `[]` and problem `voice_library: missing`). Every file read is guarded: any exception becomes a problem `<source>: <ExceptionClass>`; valid JSON of the wrong shape becomes a problem `<source>: bad shape`.
- `build_prompt(call: str, packet: dict, *, scene_ids: list[str] | None = None, prior: dict | None = None) -> tuple[str, str]`: returns `(system, user)`; raises `ValueError` for an unknown call name, for call `scene` without `scene_ids`, or for call `plan`/`scene` without `prior` (`plan` needs prior {"story_map": ...}; `scene` needs prior {"story_map": ..., "coverage": ..., "scenes": ...}).
  - `system` (all calls) = one short role paragraph (a planning assistant for a motion-comic film pipeline; it plans only, never writes the owner's script) + the line `RULES:` + `SHARED_RULE_BLOCK` + an output paragraph: reply with ONE JSON object only (no markdown fences, no prose) whose top-level keys are exactly the names in `OUTPUT_KEYS[call]`, each value a complete document that includes `"adhyay": <N>`.
  - `user` always contains, in this order, clearly headed sections: `TASK` (call-specific, below), `OUTPUT SCHEMAS` (for every key in OUTPUT_KEYS[call]: its name and `json.dumps(SCHEMA, ensure_ascii=False, sort_keys=True, indent=1)` from the unit module), `CHAPTER DATA` (the call-specific slice of the packet, as compact JSON with `ensure_ascii=False`), and `MUST NOT` (a bullet list from the rules: never write/edit/translate/critique the EASY script; no timings, hashes or approvals; no invented events, dialogue or closure; no images or voices; no code; no invented preset or image or voice id; no redeciding of known cast, place or style; omissions are only PROPOSED, the owner decides).
  - TASK for `map`: classify EVERY ovi once (types STORY, TEACHING, PHILOSOPHY, INVOCATION, RECAP, PHALASHRUTI, OTHER), identify the COMPLETE events (each with an event_id, kind story or discourse, title, ovi_range, key_ovis and closure: RESOLVED_IN_ADHYAY, CONTINUES_NEXT_ADHYAY, STARTED_EARLIER, SOURCE_INCOMPLETE_OR_AMBIGUOUS or NA); every STORY ovi must lie in an event of kind story and every TEACHING ovi in an event of kind discourse; type does not decide omission. CHAPTER DATA = ovis and research.
  - TASK for `plan`: give every ovi exactly one disposition (VISUALISED, NARRATED, QUOTED, MERGED_EQUIVALENT with covered_by and reason, PROPOSE_OMISSION with a reason) and order the scenes (scene_id, section_kind story|discourse, ovi_range, goal, line_ids from the script in reading order, teaching_treatment for discourse scenes, the `turn` field as the schema requires); film what contributes to the story and the teaching, propose omissions only for the rest; existing script ids and order are immutable. CHAPTER DATA = ovis, script, and PRIOR (the story_map).
  - TASK for `scene`: for ONLY the scenes in `scene_ids` produce shots (use a preset id from the preset list when one fits, flat images first, else NEED_NEW with reason and class), image briefs (include the image-brief lessons below), canon looks (stated vs inferred), voice casting (by DESCRIPTION from the voice library; a RECURRING character keeps the voice it is assigned to; a new character gets the best-matching unassigned voice with a short `reason`; if no saved voice fits raise a question, never invent a voice id), sound suggestions (reuse an available palette sound id else NEED_NEW with an ElevenLabs-ready sound prompt; silence is valid; no music; nothing automatic from presets), and questions for every ambiguity (never a silent guess). CHAPTER DATA = the script lines, ovis and scene cards of the selected scenes only (lines/ovis of other scenes must NOT appear), the whole preset list, the sound palette (when it is empty say in words `The sound palette is empty: every sound is NEED_NEW.`), the voice library, the research packet, and PRIOR (story_map events overlapping those scenes, the coverage entries of their ovis, and the scene cards).
  - The image-brief lessons paragraph (included in the `scene` task) must contain these points in your own compact wording: approved flat-colour style; full chapter-state identity of each character; exactly the visible people, each once with position, ONE action and gaze target; accepted place and fixed features; critical prop and its state; framing, angle, screen directions across adjoining cuts; preset slot, full-frame or layer need, safe crop; approved light; ONLY on-screen facts (no narration or commentary); exclude extra people, text, inset frames and modern objects; references are the visible characters, the place, one style anchor and the central prop.
- `estimate_tokens(text: str) -> int`: `max(1, len(text) // 3)` (rough; Devanagari is token-heavy).

## Tests (`tests/test_stage1_prompts.py`; synthetic data in tmp_path, plus one real-file test; load modules by importlib BY PATH)
Build a tiny synthetic root in tmp_path (`canon/adhyay_02/source/ovis.jsonl` with 4 ovis having section and the four text fields; `canon/adhyay_02/script/easy.md` with 2 scenes and 3 lines in the EASY format; a preset index of 2 presets; a voice library of 3 voices with descriptions; no sound palette).
1. `build_packet`: all keys present with the right contents; sorting by ovi; the voice records keep `description`; a missing file gives its documented problem and an empty value without raising; invalid adhyay; wrong-shape JSON for each source (`[]`, `5`, `"x"`, `null`) never raises and gives `bad shape`; Adhyay 1 style (`text` field) records are accepted.
2. `SHARED_RULE_BLOCK` text equals the quoted text and appears in the `system` of every call; `OUTPUT_KEYS` names appear in the output paragraph.
3. For each call the `user` contains the schemas of exactly its documents (assert `json.dumps(unit SCHEMA, sort_keys=True, ensure_ascii=False, indent=1)` of each is a substring and the schema of a document NOT in the call is not), the headings in order, and the MUST NOT list.
4. `scene` call: only the selected scene lines/ovis appear (assert ids of lines of the other scene are absent), every preset id and every voice description appears, the empty-palette sentence appears when `sounds` is empty and is absent when the palette has a sound (whose id then appears), the image-brief lessons key phrases appear, the prior documents appear.
5. `map` and `plan` call content checks (the ovis appear; plan has the script line ids and the story_map prior).
6. Errors: unknown call, `scene` without scene_ids, `plan` without prior, `scene` without prior: each raises ValueError in its own test.
7. No secret and nothing chapter-specific: the produced prompts contain no `nvapi-`, `sk-` or `secrets`; the module source contains no literal `Gajanan`, `Bankatlal` or `adhyay_02`.
8. REAL repo (skipif a file is missing): `build_packet(1, ROOT)` has 146 ovis, 62 script lines, the 35 voices, the presets; `build_prompt("map", packet)` returns non-empty strings and `estimate_tokens` of the user text is above 0.
Use `copy.deepcopy` and plain assignment for mutations; never a helper that rejects no-effect mutations; remember `True == 1`.

Reply with only the two FILE blocks:
FILE: scripts/pipeline/stage1/prompts.py
FILE: tests/test_stage1_prompts.py

## THIS CALL RETURNS ONLY ONE FILE: scripts/pipeline/stage1/prompts.py (complete). The tests are fixed in a separate call. FIX (verified on real data by calling the runner's dry run): the scene call crashes with `AttributeError: 'str' object has no attribute 'get'` at `scene_cards = [sc for sc in prior.get("scenes", []) ...]` because the prior values are DOCUMENTS, not lists: `prior` is {"story_map": <story_map document>, "coverage": <coverage document>, "scenes": <scenes document>} where the scenes document is `{"adhyay": N, "scenes": [ {scene card}, ... ]}`, the coverage document is `{"adhyay": N, "ovis": [...]}` and the story_map document is `{"adhyay": N, "ovi_types": [...], "events": [...]}`. Read them that way: scene cards = `prior["scenes"]["scenes"]` (only dict entries whose scene_id is in scene_ids), coverage entries = `prior["coverage"]["ovis"]` for the ovis of the selected scenes, events = `prior["story_map"]["events"]` overlapping them (inclusive ranges, no enumeration). For robustness also ACCEPT a bare list for scenes (cards) and tolerate empty placeholder documents `{}`; build_prompt must never raise except the documented ValueErrors. Keep everything else as it is. Return only that one FILE block.

## CURRENT scripts/pipeline/stage1/prompts.py
```python
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


def _system_prompt(call: str) -> str:
    role = (
        "You are a planning assistant for a motion-comic film pipeline. "
        "You plan only; you never write the owner's script."
    )
    output_keys = OUTPUT_KEYS[call]
    output_para = (
        "Reply with ONE JSON object only (no markdown fences, no prose) "
        f"whose top-level keys are exactly {list(output_keys)}, "
        "each value a complete document that includes \"adhyay\": <N>."
    )
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
        scene_cards = [sc for sc in prior.get("scenes", []) if sc.get("scene_id") in scene_set]
        events = []
        for ev in prior.get("story_map", {}).get("events", []):
            ev_ovis = set(range(ev["ovi_range"][0], ev["ovi_range"][1] + 1))
            if ev_ovis & ovi_set:
                events.append(ev)
        coverage = [c for c in prior.get("coverage", []) if c.get("ovi") in ovi_set]

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

    system = _system_prompt(call)
    user = _user_prompt(call, packet, scene_ids, prior)
    return system, user


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 3)
```
