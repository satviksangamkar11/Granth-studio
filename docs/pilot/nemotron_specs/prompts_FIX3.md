# FIX CALL: return BOTH files in full: `scripts/pipeline/stage1/prompts.py` and `tests/test_stage1_prompts.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
F..FF..F.F..s                                                            [100%]
================================== FAILURES ===================================
_________________________ test_build_packet_synthetic _________________________
tests\test_stage1_prompts.py:101: in test_build_packet_synthetic
    assert len(packet["script"]) == 3
E   assert 0 == 3
E    +  where 0 = len([])
________________________ test_build_packet_bad_shapes _________________________
tests\test_stage1_prompts.py:169: in test_build_packet_bad_shapes
    assert any("research: bad shape" in p for p in problems)
E   assert False
E    +  where False = any(<generator object test_build_packet_bad_shapes.<locals>.<genexpr> at 0x000001E520578EE0>)
____________________ test_build_packet_adhyay1_text_field _____________________
tests\test_stage1_prompts.py:200: in test_build_packet_adhyay1_text_field
    assert problems == []
E   AssertionError: assert ['ovis: missi...ipt: missing'] == []
E     
E     Left contains 2 more items, first extra item: 'ovis: missing'
E     Use -v to get more diff
________________________ test_scene_call_filters_data _________________________
tests\test_stage1_prompts.py:281: in test_scene_call_filters_data
    assert "S1-L1" in line_ids
E   AssertionError: assert 'S1-L1' in []
__________________________ test_map_and_plan_content __________________________
tests\test_stage1_prompts.py:353: in test_map_and_plan_content
    assert "S1-L1" in line_ids
E   AssertionError: assert 'S1-L1' in []
=========================== short test summary info ===========================
FAILED tests/test_stage1_prompts.py::test_build_packet_synthetic - assert 0 == 3
FAILED tests/test_stage1_prompts.py::test_build_packet_bad_shapes - assert False
FAILED tests/test_stage1_prompts.py::test_build_packet_adhyay1_text_field - A...
FAILED tests/test_stage1_prompts.py::test_scene_call_filters_data - Assertion...
FAILED tests/test_stage1_prompts.py::test_map_and_plan_content - AssertionErr...
5 failed, 7 passed, 1 skipped in 0.25s

```

## SPEC
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


## CURRENT MODULE scripts/pipeline/stage1/prompts.py
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

## CURRENT TESTS tests/test_stage1_prompts.py
```python
import importlib.util
import json
import tempfile
from pathlib import Path

import pytest

# Load the prompts module by path
PROMPTS_PATH = Path(__file__).resolve().parents[1] / "scripts" / "pipeline" / "stage1" / "prompts.py"
spec = importlib.util.spec_from_file_location("prompts", PROMPTS_PATH)
prompts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prompts)


def _write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def _write_jsonl(path: Path, lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for obj in lines:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def _make_synthetic_root(tmp: Path) -> Path:
    root = tmp / "repo"
    # adhyay 2
    adhyay_dir = root / "canon" / "adhyay_02"
    # ovis
    ovis = [
        {"ovi": 1, "original_marathi": "om1", "simple_marathi": "sm1", "hindi": "h1", "easy_english": "ee1", "section": "sec1"},
        {"ovi": 2, "original_marathi": "om2", "simple_marathi": "sm2", "hindi": "h2", "easy_english": "ee2", "section": "sec1"},
        {"ovi": 3, "original_marathi": "om3", "simple_marathi": "sm3", "hindi": "h3", "easy_english": "ee3", "section": "sec2"},
        {"ovi": 4, "original_marathi": "om4", "simple_marathi": "sm4", "hindi": "h4", "easy_english": "ee4", "section": "sec2"},
    ]
    _write_jsonl(adhyay_dir / "source" / "ovis.jsonl", ovis)
    # script (EASY format)
    script_md = (
        "# Adhyay 2\n\n"
        "## S1\n\n"
        "S1-L1 | narrator | 1 | core | mar1 | hin1\n"
        "S1-L2 | narrator | 2 | core | mar2 | hin2\n\n"
        "## S2\n\n"
        "S2-L1 | narrator | 3 | core | mar3 | hin3\n"
    )
    (adhyay_dir / "script").mkdir(parents=True, exist_ok=True)
    (adhyay_dir / "script" / "easy.md").write_text(script_md, encoding="utf-8")
    # presets
    presets = [
        {"preset": "p1", "use": "bg", "assets": ["a1"], "simplest_renderer": "flat"},
        {"preset": "p2", "use": "char", "assets": ["a2"], "simplest_renderer": "flat"},
    ]
    _write_json(root / "assets" / "v5_presets" / "index.json", presets)
    # voices
    voices = {
        "voices": [
            {"voice_key": "v1", "voice_id": "id1", "name": "N1", "gender": "M", "age": "30", "accent": "Indian", "description": "desc1", "owner_note": "", "marathi_verified": True, "hindi_verified": True, "assigned_to": "char1", "status": "active"},
            {"voice_key": "v2", "voice_id": "id2", "name": "N2", "gender": "F", "age": "25", "accent": "Indian", "description": "desc2", "owner_note": "", "marathi_verified": True, "hindi_verified": True, "assigned_to": "char2", "status": "active"},
            {"voice_key": "v3", "voice_id": "id3", "name": "N3", "gender": "M", "age": "40", "accent": "Indian", "description": "desc3", "owner_note": "", "marathi_verified": False, "hindi_verified": False, "assigned_to": "", "status": "available"},
        ]
    }
    _write_json(root / "canon" / "series" / "voices.json", voices)
    # no sound palette
    return root


def _extract_chapter_data(usr: str) -> dict:
    """Extract the JSON from the CHAPTER DATA section of the user prompt."""
    marker = "CHAPTER DATA\n"
    idx = usr.find(marker)
    if idx == -1:
        return {}
    json_str = usr[idx + len(marker):]
    # The next section starts with a heading (e.g., "MUST NOT\n")
    # Find the next double newline that precedes a heading? Simpler: the JSON is compact and ends before the next section.
    # We'll parse by finding the first occurrence of a known next heading.
    # But the JSON may contain newlines? We used separators=(",", ":") so no newlines.
    # So the JSON ends at the next "\n\n" (since sections are joined by "\n\n").
    end = json_str.find("\n\n")
    if end != -1:
        json_str = json_str[:end]
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return {}


def test_build_packet_synthetic():
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_synthetic_root(Path(tmp))
        packet, problems = prompts.build_packet(2, root)
        assert problems == []
        assert packet["adhyay"] == 2
        assert len(packet["ovis"]) == 4
        assert packet["ovis"][0]["ovi"] == 1
        assert packet["ovis"][-1]["ovi"] == 4
        assert "original_marathi" in packet["ovis"][0]
        assert packet["research"] == {}
        assert len(packet["script"]) == 3
        assert packet["script"][0]["id"] == "S1-L1"
        assert packet["script"][1]["id"] == "S1-L2"
        assert packet["script"][2]["id"] == "S2-L1"
        assert len(packet["presets"]) == 2
        assert packet["presets"][0]["preset"] == "p1"
        assert packet["presets"][1]["preset"] == "p2"
        assert packet["sounds"] == []
        assert len(packet["voices"]) == 3
        assert packet["voices"][0]["description"] == "desc1"


def test_build_packet_missing_files():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "repo"
        root.mkdir()
        # No files at all
        packet, problems = prompts.build_packet(2, root)
        assert "ovis: missing" in problems
        assert "script: missing" in problems
        assert "presets: missing" in problems
        assert "voice_library: missing" in problems
        # research and sounds should not produce missing problems
        assert not any("research: missing" in p for p in problems)
        assert not any("sounds: missing" in p for p in problems)
        assert packet["ovis"] == []
        assert packet["script"] == []
        assert packet["presets"] == []
        assert packet["voices"] == []


def test_build_packet_invalid_adhyay():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        packet, problems = prompts.build_packet(0, root)
        assert packet == {}
        assert problems == ["adhyay must be an int in 1..21"]
        packet, problems = prompts.build_packet(22, root)
        assert packet == {}
        assert problems == ["adhyay must be an int in 1..21"]


def test_build_packet_bad_shapes():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "repo"
        root.mkdir()
        adhyay_dir = root / "canon" / "adhyay_02"
        adhyay_dir.mkdir(parents=True)
        # bad ovis jsonl
        (adhyay_dir / "source").mkdir()
        (adhyay_dir / "source" / "ovis.jsonl").write_text("not json\n", encoding="utf-8")
        # bad research
        _write_json(adhyay_dir / "research_packet.json", "not a dict")
        # bad script (will be handled by parse_script, but we can't control that; we just test our wrapper)
        (adhyay_dir / "script").mkdir()
        (adhyay_dir / "script" / "easy.md").write_text("", encoding="utf-8")
        # bad presets
        (root / "assets" / "v5_presets").mkdir(parents=True)
        _write_json(root / "assets" / "v5_presets" / "index.json", "not a list")
        # bad voices
        (root / "canon" / "series").mkdir(parents=True)
        _write_json(root / "canon" / "series" / "voices.json", "not a dict")
        # bad sounds
        (root / "canon" / "series" / "sounds").mkdir(parents=True)
        _write_json(root / "canon" / "series" / "sounds" / "palette.json", 5)

        packet, problems = prompts.build_packet(2, root)
        assert any("ovis: bad line" in p for p in problems)
        assert any("research: bad shape" in p for p in problems)
        assert any("presets: bad shape" in p for p in problems)
        assert any("voice_library: bad shape" in p for p in problems)
        assert any("sounds: bad shape" in p for p in problems)
        assert packet["sounds"] == []


def test_build_packet_adhyay1_text_field():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "repo"
        root.mkdir()
        adhyay_dir = root / "canon" / "adhyay_01"
        adhyay_dir.mkdir(parents=True)
        ovis = [{"ovi": 1, "text": "some text"}]
        _write_jsonl(adhyay_dir / "source" / "ovis.jsonl", ovis)
        # research is folder -> skip
        (adhyay_dir / "research_packet").mkdir()
        # script
        (adhyay_dir / "script").mkdir()
        (adhyay_dir / "script" / "easy.md").write_text("", encoding="utf-8")
        # presets
        (root / "assets" / "v5_presets").mkdir(parents=True)
        _write_json(root / "assets" / "v5_presets" / "index.json", [])
        # voices
        (root / "canon" / "series").mkdir(parents=True)
        _write_json(root / "canon" / "series" / "voices.json", {"voices": []})
        # sounds
        (root / "canon" / "series" / "sounds").mkdir(parents=True)
        _write_json(root / "canon" / "series" / "sounds" / "palette.json", {"sounds": []})

        packet, problems = prompts.build_packet(1, root)
        assert problems == []
        assert packet["ovis"][0]["text"] == "some text"
        assert packet["research"] == {}


def test_shared_rule_block_and_output_keys():
    assert prompts.SHARED_RULE_BLOCK == (
        "Use only locked source, research and owner decisions. Cite chapter-qualified ovis for facts. "
        "Reuse registered IDs; report missing identities. Never invent events, motives, miracles, dialogue or closure. "
        "Reference immutable EASY line IDs; never write, edit, translate or critique their wording. "
        "Thoughts and unclear speech remain narrator material. "
        "Separate sourced facts from STAGING and inferred visual looks. "
        "Preserve required teachings and explicit coverage; only the owner approves omissions. "
        "Use supplied preset capabilities and sound availability; report NEED_NEW honestly. "
        "Output only this call's schema. No timings, hashes, approvals, API calls or code."
    )
    for call in prompts.CALLS:
        sys, usr = prompts.build_prompt(call, {"adhyay": 1, "ovis": [], "research": {}, "script": [], "presets": [], "sounds": [], "voices": []}, scene_ids=["S1"] if call == "scene" else None, prior={"story_map": {}, "coverage": [], "scenes": []} if call in ("plan", "scene") else None)
        assert prompts.SHARED_RULE_BLOCK in sys
        for key in prompts.OUTPUT_KEYS[call]:
            assert key in sys


def test_user_prompt_structure_and_schemas():
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_synthetic_root(Path(tmp))
        packet, _ = prompts.build_packet(2, root)
        # Load unit schemas to compare
        story_map_schema = prompts._get_unit_schema("story_map")
        coverage_schema = prompts._get_unit_schema("coverage")
        scenes_schema = prompts._get_unit_schema("scenes")
        shots_schema = prompts._get_unit_schema("shots")
        briefs_schema = prompts._get_unit_schema("briefs")
        looks_schema = prompts._get_unit_schema("looks")
        voices_schema = prompts._get_unit_schema("voices")
        sounds_schema = prompts._get_unit_schema("sounds")
        questions_schema = prompts._get_unit_schema("questions")

        # map
        sys, usr = prompts.build_prompt("map", packet)
        assert "TASK" in usr
        assert "OUTPUT SCHEMAS" in usr
        assert "CHAPTER DATA" in usr
        assert "MUST NOT" in usr
        # check schemas present
        assert json.dumps(story_map_schema, ensure_ascii=False, sort_keys=True, indent=1) in usr
        # ensure other schemas not present
        assert json.dumps(coverage_schema, ensure_ascii=False, sort_keys=True, indent=1) not in usr

        # plan
        prior = {"story_map": {"events": []}}
        sys, usr = prompts.build_prompt("plan", packet, prior=prior)
        assert json.dumps(coverage_schema, ensure_ascii=False, sort_keys=True, indent=1) in usr
        assert json.dumps(scenes_schema, ensure_ascii=False, sort_keys=True, indent=1) in usr
        assert json.dumps(story_map_schema, ensure_ascii=False, sort_keys=True, indent=1) not in usr

        # scene
        prior = {"story_map": {"events": []}, "coverage": [], "scenes": []}
        sys, usr = prompts.build_prompt("scene", packet, scene_ids=["S1"], prior=prior)
        for schema in (shots_schema, briefs_schema, looks_schema, voices_schema, sounds_schema, questions_schema):
            assert json.dumps(schema, ensure_ascii=False, sort_keys=True, indent=1) in usr
        assert json.dumps(coverage_schema, ensure_ascii=False, sort_keys=True, indent=1) not in usr

        # headings order
        headings = ["TASK", "OUTPUT SCHEMAS", "CHAPTER DATA", "MUST NOT"]
        idx = [usr.find(h) for h in headings]
        assert all(i != -1 for i in idx)
        assert idx == sorted(idx)


def test_scene_call_filters_data():
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_synthetic_root(Path(tmp))
        packet, _ = prompts.build_packet(2, root)
        prior = {"story_map": {"events": []}, "coverage": [], "scenes": [{"scene_id": "S1"}, {"scene_id": "S2"}]}
        sys, usr = prompts.build_prompt("scene", packet, scene_ids=["S1"], prior=prior)
        # Extract chapter data JSON
        data = _extract_chapter_data(usr)
        # Only S1 lines should appear
        script_lines = data.get("script_lines", [])
        line_ids = [ln.get("id") for ln in script_lines]
        assert "S1-L1" in line_ids
        assert "S1-L2" in line_ids
        assert "S2-L1" not in line_ids
        # Only ovis 1,2
        ovis = data.get("ovis", [])
        ovi_nums = [ov.get("ovi") for ov in ovis]
        assert 1 in ovi_nums
        assert 2 in ovi_nums
        assert 3 not in ovi_nums
        # All preset ids
        presets = data.get("presets", [])
        preset_ids = [p.get("preset") for p in presets]
        assert "p1" in preset_ids
        assert "p2" in preset_ids
        # All voice descriptions
        voices = data.get("voice_library", [])
        descriptions = [v.get("description") for v in voices]
        assert "desc1" in descriptions
        assert "desc2" in descriptions
        assert "desc3" in descriptions
        # Empty palette sentence
        assert data.get("sound_palette_note") == "The sound palette is empty: every sound is NEED_NEW."
        # Image-brief lessons key phrases (check in the whole user prompt)
        assert "flat-colour" in usr
        assert "full chapter-state identity" in usr
        assert "exactly the visible people" in usr
        assert "ONE action and gaze target" in usr
        assert "critical prop" in usr
        assert "framing, angle, screen directions" in usr
        assert "preset slot" in usr
        assert "approved light" in usr
        assert "ONLY on-screen facts" in usr
        assert "exclude extra people" in usr
        assert "references are the visible characters" in usr
        # Prior documents appear
        assert "story_map_events" in data.get("PRIOR", {})
        assert "coverage" in data.get("PRIOR", {})
        assert "scene_cards" in data.get("PRIOR", {})


def test_scene_call_with_sounds():
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_synthetic_root(Path(tmp))
        # Add a sound palette
        _write_json(root / "canon" / "series" / "sounds" / "palette.json", {"sounds": [{"id": "snd1", "desc": "wind"}]})
        packet, _ = prompts.build_packet(2, root)
        prior = {"story_map": {"events": []}, "coverage": [], "scenes": [{"scene_id": "S1"}]}
        sys, usr = prompts.build_prompt("scene", packet, scene_ids=["S1"], prior=prior)
        data = _extract_chapter_data(usr)
        sounds = data.get("sound_palette", [])
        sound_ids = [s.get("id") for s in sounds]
        assert "snd1" in sound_ids
        assert data.get("sound_palette_note") is None


def test_map_and_plan_content():
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_synthetic_root(Path(tmp))
        packet, _ = prompts.build_packet(2, root)
        # map
        sys, usr = prompts.build_prompt("map", packet)
        data = _extract_chapter_data(usr)
        ovis = data.get("ovis", [])
        ovi_nums = [ov.get("ovi") for ov in ovis]
        assert 1 in ovi_nums
        assert "research" in data
        # plan
        prior = {"story_map": {"events": [{"event_id": "E1", "ovi_range": [1, 2]}]}}
        sys, usr = prompts.build_prompt("plan", packet, prior=prior)
        data = _extract_chapter_data(usr)
        script_lines = data.get("script", [])
        line_ids = [ln.get("id") for ln in script_lines]
        assert "S1-L1" in line_ids
        assert "S1-L2" in line_ids
        assert "S2-L1" in line_ids
        prior_map = data.get("PRIOR", {})
        assert prior_map.get("events", [])[0].get("event_id") == "E1"


def test_errors():
    packet = {"adhyay": 1, "ovis": [], "research": {}, "script": [], "presets": [], "sounds": [], "voices": []}
    with pytest.raises(ValueError):
        prompts.build_prompt("unknown", packet)
    with pytest.raises(ValueError):
        prompts.build_prompt("scene", packet)  # no scene_ids
    with pytest.raises(ValueError):
        prompts.build_prompt("plan", packet)  # no prior
    with pytest.raises(ValueError):
        prompts.build_prompt("scene", packet, scene_ids=["S1"])  # no prior


def test_no_secrets_or_chapter_specific():
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_synthetic_root(Path(tmp))
        packet, _ = prompts.build_packet(2, root)
        for call in prompts.CALLS:
            if call == "scene":
                sys, usr = prompts.build_prompt(call, packet, scene_ids=["S1"], prior={"story_map": {}, "coverage": [], "scenes": []})
            elif call == "plan":
                sys, usr = prompts.build_prompt(call, packet, prior={"story_map": {}})
            else:
                sys, usr = prompts.build_prompt(call, packet)
            assert "nvapi-" not in sys and "nvapi-" not in usr
            assert "sk-" not in sys and "sk-" not in usr
            assert "secrets" not in sys and "secrets" not in usr
    # Check module source for forbidden literals
    source = PROMPTS_PATH.read_text(encoding="utf-8")
    assert "Gajanan" not in source
    assert "Bankatlal" not in source
    assert "adhyay_02" not in source


@pytest.mark.skipif(
    not (Path(__file__).resolve().parents[3] / "canon" / "adhyay_01" / "source" / "ovis.jsonl").exists(),
    reason="Real repo not present"
)
def test_real_repo():
    ROOT = Path(__file__).resolve().parents[3]
    packet, problems = prompts.build_packet(1, ROOT)
    assert len(packet["ovis"]) == 146
    assert len(packet["script"]) == 62
    assert len(packet["voices"]) == 35
    assert len(packet["presets"]) > 0
    sys, usr = prompts.build_prompt("map", packet)
    assert sys and usr
    assert prompts.estimate_tokens(usr) > 0

```

## DIAGNOSIS (verified): the MODULE is correct (on the real Adhyay 1 files `build_packet(1, root)` returns 146 ovis, 62 script lines, 11 presets, 35 voices and no problems). The 5 failures come from the TEST FIXTURE: `_make_synthetic_root` writes the script in a made-up one-line form (`S1-L1 | narrator | 1 | core | mar1 | hin1`) that `check_script.parse_script` cannot parse, so the packet has 0 script lines. Write the synthetic script EXACTLY in the real EASY format (blank lines optional, the header line must match the regex `^\*\*(S(\d+)-L(\d+))\*\* \| (\S+) \| ovi (\d+) \| (\S+)$`):
```
# Adhyay 2 test script

## S1
**S1-L1** | narrator | ovi 1 | core
- Marathi: mar1
- Hindi: hin1

**S1-L2** | narrator | ovi 2 | core
- Marathi: mar2
- Hindi: hin2

## S2
**S2-L1** | narrator | ovi 3 | core
- Marathi: mar3
- Hindi: hin3
```
Then re-check every assertion that depends on the script lines (counts, ids `S1-L1`, scene filtering, the plan/map content tests) and the section-less ovis (`section` may be a string or an int in the fixture; the module must tolerate both). Where a test matches JSON text by spacing, parse the CHAPTER DATA JSON and assert on the parsed structure instead. Fix the TESTS; change the module only if a corrected test still fails and the SPEC requires it. Return BOTH complete FILE blocks.
