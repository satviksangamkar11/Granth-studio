# FIX CALL (THIS ONE RETURNS FOUR FILES: scripts/pipeline/stage1/aggregate.py, tests/test_stage1_aggregate.py, scripts/pipeline/stage1/context.py, tests/test_stage1_context.py, each complete): the first two are given first; the context module and its tests are appended at the END. Return: `scripts/pipeline/stage1/aggregate.py` and `tests/test_stage1_aggregate.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
.......................................                                  [100%]
39 passed in 0.27s

```

## SPEC
# SPEC: NEW `scripts/pipeline/stage1/aggregate.py` + NEW `tests/test_stage1_aggregate.py`. Return exactly these TWO files in full; do not output or change any other file.
Purpose: one entry point that validates the nine Stage 1 documents TOGETHER, including the cross-document rules that no single unit can check. Two independent reviewers (Codex, Haiku) found these intent gaps; each X-rule below closes one. Standard library only; `from __future__ import annotations`; nothing at import time except imports and definitions; no print except in `main()`; no key or secret is ever read. Do not over-engineer: plain functions, no classes, no config.

## Units and their API (already written, do NOT modify them)
The nine modules `scripts/pipeline/stage1/<unit>.py` for unit in `story_map, coverage, scenes, shots, briefs, looks, voices, sounds, questions` each expose `SCHEMA` (dict), `schema_errors(doc) -> list[str]` and `validate(adhyay, doc, docs, ctx) -> list[str]` (semantic checks; they never raise). Load them with importlib BY PATH from the folder of this file (`Path(__file__).resolve().parent / f"{unit}.py"`, unique module names such as `stage1_unit_<unit>`, cached in a module-level dict after the first load; a unit that cannot be loaded gives the single error `aggregate: cannot load <unit>`).
`docs` is a dict unit -> document (dict). `ctx` is a dict. The shared valid base used by all unit tests is `docs/pilot/nemotron_specs/stage1_base.json` with the keys `docs` and `ctx`; ctx has script_line_ids, core_line_ids, chapter_ovis, unfilmed_ovis, preset_ids, sound_ids, saved_voices, speaking_characters, known_states. Additional OPTIONAL ctx keys used here: `series_voices` (dict character_id -> voice_key of voices already assigned in the series; absent = {}) and `script_texts` (list of str, the owner's script line texts; absent = []).
Field names you need:
- story_map: `ovi_types` [{ovi:int, type in STORY|TEACHING|PHILOSOPHY|INVOCATION|RECAP|PHALASHRUTI|OTHER}], `events` [{event_id, kind story|discourse, title, ovi_range [lo,hi], key_ovis [int], closure RESOLVED_IN_ADHYAY|CONTINUES_NEXT_ADHYAY|STARTED_EARLIER|SOURCE_INCOMPLETE_OR_AMBIGUOUS|NA}].
- coverage: `ovis` [{ovi, disposition VISUALISED|NARRATED|QUOTED|MERGED_EQUIVALENT|PROPOSE_OMISSION, reason?, covered_by?}].
- scenes: `scenes` [{scene_id, section_kind, ovi_range [lo,hi], line_ids, ...}].
- shots: `shots` [{shot_id, scene_id, ovi_ids [int], beat_line_ids, ...}].
- questions: `questions` [{id, text, scene_id}].
- voices: `cast` [{character_id, voice_key, voice_id, gender, status RECURRING|NEW_PROPOSED}].

## API
- `UNITS`: the tuple of the nine unit names in the order above.
- `validate_all(adhyay: int, docs: Any, ctx: Any) -> list[str]`: returns ALL errors (empty list = valid). Never raises: any unexpected exception inside a step becomes the single error `aggregate: internal error in <step>`; a non-dict `docs` or `ctx` is reported once (`aggregate: docs must be an object` / `aggregate: ctx must be an object`) and then treated as `{}`.
  Step 1, per unit in order: if the document is missing or not a dict, the error is `<unit>: document missing`; else `errs = schema_errors(doc)`; if errs, add them and skip that unit's `validate` and its cross rules; else add the messages of `validate(adhyay, doc, docs, ctx)`. Remember which units are schema-valid.
  Step 2, cross rules. Each rule runs only when ALL the documents it reads are present and schema-valid (otherwise it is skipped silently). Ranges are inclusive [lo, hi] of ints; NEVER enumerate a range (compare lo <= n <= hi). Treat bool as not an int. Messages are exactly as quoted (tests assert the ovi number / id appears, not extra wording):
  - X1 `story_map`: every ovi typed STORY or TEACHING must lie inside the ovi_range of at least one event, else `story_map: ovi N is typed <TYPE> but is in no event` (so a chapter typed all story with an empty events list fails).
  - X2 `coverage` + `story_map`: an ovi typed STORY or TEACHING must not have the disposition PROPOSE_OMISSION, else `coverage: ovi N is <TYPE> but an omission is proposed`.
  - X3 `coverage` + ctx `unfilmed_ovis` (the owner-approved omissions): every PROPOSE_OMISSION ovi must be in ctx `unfilmed_ovis`, else `coverage: ovi N omission is not approved by the owner`; every ovi in ctx `unfilmed_ovis` must have the disposition PROPOSE_OMISSION in coverage, else `coverage: ovi N is approved as unfilmed but has no omission proposal`.
  - X4 `coverage` + `shots` + `scenes`: every ovi with the disposition VISUALISED must appear in the `ovi_ids` of at least one shot, else `coverage: ovi N is VISUALISED but is in no shot`; every ovi whose disposition is NOT PROPOSE_OMISSION must lie in some scene ovi_range, else `coverage: ovi N is in no scene`.
  - X5 `story_map` + `scenes`: every key ovi of every event must lie in some scene ovi_range, else `story_map: key ovi N of event <event_id> is in no scene`.
  - X6 `story_map` + `questions` + `scenes`: an event with closure SOURCE_INCOMPLETE_OR_AMBIGUOUS needs at least one question whose scene_id names a scene whose ovi_range overlaps the event ovi_range (overlap: lo1 <= hi2 and lo2 <= hi1), else `story_map: ambiguous event <event_id> has no question`.
  - X7 `voices` + ctx `series_voices`: for a cast entry whose character_id is a key of series_voices: status RECURRING requires voice_key == series_voices[character_id], else `voices: recurring character <character_id> has a different voice than the series`; status NEW_PROPOSED is the error `voices: character <character_id> already has a series voice`.
  - X8 EASY script guard, ctx `script_texts`: walk every string value (any depth, lists and dicts, depth limit 8) of all nine documents; normalise both sides (casefold, collapse whitespace); if a normalised script text of at least 20 characters is a substring of the normalised string value, add `<unit>: free text copies script wording (<key path>)` where the key path looks like `scenes/0/goal`.
- `export_schemas(out_dir: Path) -> list[Path]`: writes `stage1_<unit>.schema.json` (json.dumps with sort_keys and indent 2, utf-8, trailing newline) for each unit from its `SCHEMA` into `out_dir` (created if missing); raises `FileExistsError` BEFORE writing anything if any target file already exists; returns the nine paths.
- `main(argv=None) -> int`: `--adhyay N` (int, required), `--docs-dir PATH` (required; reads `<unit>.json` for each unit; a missing file is simply an absent document), `--ctx PATH` (optional JSON file, default {}), optional `--export-schemas DIR`. Prints one error per line, then `N error(s)`; returns 0 when there are no errors and 1 otherwise; returns 2 after printing `refused: <reason>` for unreadable JSON or an existing schema file. `if __name__ == "__main__": raise SystemExit(main())`.

## Tests (`tests/test_stage1_aggregate.py`)
Load the module by path with importlib (`ROOT = Path(__file__).resolve().parents[1]`); load `BASE = json.load(...stage1_base.json)` with `BASE["docs"]` and `BASE["ctx"]`; use `copy.deepcopy` and plain assignment for EVERY mutation (never a helper that rejects "no effect" mutations; make sure each mutation really changes the value; remember `True == 1` in Python).
1. The unmodified base is valid: `validate_all(1, docs, ctx) == []`.
2. One isolated test per rule X1..X8, each violating ONLY that rule (verify by hand that no other rule fires; assert that the ovi number / event id / character id appears in an error, and that the corrected twin gives []):
   - X1: make ovi 3 fall outside every event (E1 ovi_range [4,5], key_ovis [4]); also the empty-events case (events set to [] while ovi_types has STORY ovis).
   - X2: set the coverage disposition of a STORY ovi to PROPOSE_OMISSION with a reason and add that ovi to ctx unfilmed_ovis (so X3 is satisfied); make sure X4 does not also fire for it.
   - X3: both directions (a proposed omission not in unfilmed_ovis; an unfilmed ovi without a proposal).
   - X4: both parts (a VISUALISED ovi in no shot; a non-omitted ovi in no scene).
   - X5: a key ovi in no scene.
   - X6: set event E2 closure to SOURCE_INCOMPLETE_OR_AMBIGUOUS: without a question on S2 it errors; with a question whose scene_id is S2 it is valid.
   - X7: with ctx `series_voices` = {"gajanan_maharaj": "other_key"} the RECURRING entry errors; with the matching key it is valid; a NEW_PROPOSED entry for a series character errors.
   - X8: ctx `script_texts` contains a 25-character script line that is copied into `scenes[0].goal`: error naming the path; a short text (under 20 characters) must NOT trigger.
3. Robustness: docs None, docs {} (nine `document missing` errors), ctx None, a document that is a list, a unit that fails its schema (its validate and cross rules are skipped, no exception), huge ranges [1, 10**12] in scenes and events return quickly.
4. `export_schemas` writes nine files in tmp_path and raises FileExistsError on the second call leaving the files unchanged; `main` exit codes 0, 1 and 2 using tmp_path files and capsys.

Reply with only the two FILE blocks:
FILE: scripts/pipeline/stage1/aggregate.py
FILE: tests/test_stage1_aggregate.py


## AMENDMENTS 2026-10-28 (AUTHORITATIVE over everything above; made after the Codex + Haiku code and intent reviews)
- X1 is kind-aware: a STORY ovi must lie in an event of kind `story`, a TEACHING ovi in an event of kind `discourse` (message `story_map: ovi N is typed <TYPE> but is in no <kind> event`).
- X2 was REMOVED on purpose: STAGE1_RULES.md says the ovi type does not decide omission; only the owner approval (X3, via ctx `unfilmed_ovis`) decides.
- X8 flags any contiguous 6-word run copied from a script text (casefold, punctuation stripped), over every document that is a dict, whatever the schema status.
- New X9: event ovi_range inside min..max of ctx `chapter_ovis` and key ovis members of it. New X10: for each scene, at least one overlapping event has kind equal to the scene section_kind. X7 also rejects a NEW_PROPOSED character whose voice_key equals a series voice of another character. New X11: optional ctx `verified_voices` (list of voice keys verified for Marathi and Hindi); when it is a list every cast voice_key must be in it.
- Any ctx value of the wrong type is read as empty (never raises); `aggregate: internal error in X<n>` is a last-resort sentinel only.
- `main --export-schemas DIR` exports AND then validates and reports like without the flag.
- `voices` documents: a NEW_PROPOSED cast entry requires a non-empty `reason` (selection by description); RECURRING entries do not.


## CURRENT MODULE scripts/pipeline/stage1/aggregate.py
```python
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

UNITS = (
    "story_map",
    "coverage",
    "scenes",
    "shots",
    "briefs",
    "looks",
    "voices",
    "sounds",
    "questions",
)

_UNIT_MODULES: dict[str, Any] = {}


def _load_unit(unit: str) -> Any:
    if unit in _UNIT_MODULES:
        return _UNIT_MODULES[unit]
    path = Path(__file__).resolve().parent / f"{unit}.py"
    module_name = f"stage1_unit_{unit}"
    try:
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot load {unit}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _UNIT_MODULES[unit] = module
        return module
    except Exception:
        _UNIT_MODULES[unit] = None
        return None


def _is_int(val: Any) -> bool:
    return isinstance(val, int) and not isinstance(val, bool)


def _in_range(val: int, lo: int, hi: int) -> bool:
    return lo <= val <= hi


def _ranges_overlap(lo1: int, hi1: int, lo2: int, hi2: int) -> bool:
    return lo1 <= hi2 and lo2 <= hi1


def _walk_strings(obj: Any, path: str = "", depth: int = 0, out: list[tuple[str, str]] | None = None) -> list[tuple[str, str]]:
    if out is None:
        out = []
    if depth > 8:
        return out
    if isinstance(obj, str):
        out.append((path, obj))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            new_path = f"{path}/{k}" if path else str(k)
            _walk_strings(v, new_path, depth + 1, out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            new_path = f"{path}/{i}"
            _walk_strings(v, new_path, depth + 1, out)
    return out


def _normalize(text: str) -> str:
    return " ".join(text.casefold().split())


def _normalize_words(text: str) -> list[str]:
    """Normalize text: casefold, strip punctuation, split into words."""
    cleaned = re.sub(r"[.,;:!?।॥\"'()\-]", " ", text)
    return cleaned.casefold().split()


def _get_int_list(ctx: dict, key: str) -> list[int]:
    """Safely extract a list of ints from ctx[key], excluding bool and unhashable items."""
    val = ctx.get(key)
    if not isinstance(val, list):
        return []
    result = []
    for item in val:
        if _is_int(item):
            result.append(item)
    return result


def _get_str_list(ctx: dict, key: str) -> list[str]:
    """Safely extract a list of strings from ctx[key]."""
    val = ctx.get(key)
    if not isinstance(val, list):
        return []
    return [item for item in val if isinstance(item, str)]


def _get_dict(ctx: dict, key: str) -> dict:
    """Safely extract a dict from ctx[key]."""
    val = ctx.get(key)
    if isinstance(val, dict):
        return val
    return {}


def validate_all(adhyay: int, docs: Any, ctx: Any) -> list[str]:
    errors: list[str] = []

    if not isinstance(docs, dict):
        errors.append("aggregate: docs must be an object")
        docs = {}
    if not isinstance(ctx, dict):
        errors.append("aggregate: ctx must be an object")
        ctx = {}

    schema_valid: dict[str, bool] = {}
    unit_docs: dict[str, Any] = {}

    for unit in UNITS:
        doc = docs.get(unit)
        if doc is None or not isinstance(doc, dict):
            errors.append(f"{unit}: document missing")
            schema_valid[unit] = False
            unit_docs[unit] = None
            continue

        module = _load_unit(unit)
        if module is None:
            errors.append(f"aggregate: cannot load {unit}")
            schema_valid[unit] = False
            unit_docs[unit] = None
            continue

        schema_errs = module.schema_errors(doc)
        if schema_errs:
            errors.extend(schema_errs)
            schema_valid[unit] = False
            unit_docs[unit] = None
            continue

        unit_docs[unit] = doc
        schema_valid[unit] = True
        try:
            val_errs = module.validate(adhyay, doc, docs, ctx)
            errors.extend(val_errs)
        except Exception:
            errors.append(f"aggregate: internal error in {unit}.validate")

    def all_valid(*units: str) -> bool:
        return all(schema_valid.get(u, False) for u in units)

    # X1: story_map - every ovi typed STORY must lie in a story event; every ovi typed TEACHING must lie in a discourse event
    if all_valid("story_map"):
        try:
            sm = unit_docs["story_map"]
            ovi_types = sm.get("ovi_types", [])
            events = sm.get("events", [])
            story_event_ranges = []
            discourse_event_ranges = []
            for e in events:
                rng = e.get("ovi_range")
                kind = e.get("kind")
                if isinstance(rng, list) and len(rng) == 2 and _is_int(rng[0]) and _is_int(rng[1]):
                    if kind == "story":
                        story_event_ranges.append((rng[0], rng[1]))
                    elif kind == "discourse":
                        discourse_event_ranges.append((rng[0], rng[1]))
            for ot in ovi_types:
                ovi = ot.get("ovi")
                typ = ot.get("type")
                if not _is_int(ovi):
                    continue
                if typ == "STORY":
                    found = any(_in_range(ovi, lo, hi) for lo, hi in story_event_ranges)
                    if not found:
                        errors.append(f"story_map: ovi {ovi} is typed STORY but is in no story event")
                elif typ == "TEACHING":
                    found = any(_in_range(ovi, lo, hi) for lo, hi in discourse_event_ranges)
                    if not found:
                        errors.append(f"story_map: ovi {ovi} is typed TEACHING but is in no discourse event")
        except Exception:
            errors.append("aggregate: internal error in X1")

    # X2 REMOVED: ovi type does not decide omission; only owner approval (X3) decides.

    # X3: coverage + ctx.unfilmed_ovis
    if all_valid("coverage"):
        try:
            cov = unit_docs["coverage"]
            unfilmed = set(_get_int_list(ctx, "unfilmed_ovis"))
            proposed = {c.get("ovi") for c in cov.get("ovis", []) if c.get("disposition") == "PROPOSE_OMISSION" and _is_int(c.get("ovi"))}
            for ovi in proposed:
                if ovi not in unfilmed:
                    errors.append(f"coverage: ovi {ovi} omission is not approved by the owner")
            for ovi in unfilmed:
                if ovi not in proposed:
                    errors.append(f"coverage: ovi {ovi} is approved as unfilmed but has no omission proposal")
        except Exception:
            errors.append("aggregate: internal error in X3")

    # X4: coverage + shots + scenes
    if all_valid("coverage", "shots", "scenes"):
        try:
            cov = unit_docs["coverage"]
            shots = unit_docs["shots"]
            scenes = unit_docs["scenes"]

            shot_ovis = set()
            for sh in shots.get("shots", []):
                for ovi in sh.get("ovi_ids", []):
                    if _is_int(ovi):
                        shot_ovis.add(ovi)

            scene_ranges = []
            for sc in scenes.get("scenes", []):
                rng = sc.get("ovi_range")
                if isinstance(rng, list) and len(rng) == 2 and _is_int(rng[0]) and _is_int(rng[1]):
                    scene_ranges.append((rng[0], rng[1]))

            for c in cov.get("ovis", []):
                ovi = c.get("ovi")
                disp = c.get("disposition")
                if not _is_int(ovi):
                    continue
                if disp == "VISUALISED" and ovi not in shot_ovis:
                    errors.append(f"coverage: ovi {ovi} is VISUALISED but is in no shot")
                if disp != "PROPOSE_OMISSION":
                    in_scene = any(_in_range(ovi, lo, hi) for lo, hi in scene_ranges)
                    if not in_scene:
                        errors.append(f"coverage: ovi {ovi} is in no scene")
        except Exception:
            errors.append("aggregate: internal error in X4")

    # X5: story_map + scenes - key ovis of events must be in some scene
    if all_valid("story_map", "scenes"):
        try:
            sm = unit_docs["story_map"]
            scenes = unit_docs["scenes"]
            scene_ranges = []
            for sc in scenes.get("scenes", []):
                rng = sc.get("ovi_range")
                if isinstance(rng, list) and len(rng) == 2 and _is_int(rng[0]) and _is_int(rng[1]):
                    scene_ranges.append((rng[0], rng[1]))
            for ev in sm.get("events", []):
                ev_id = ev.get("event_id")
                key_ovis = ev.get("key_ovis", [])
                for kovi in key_ovis:
                    if not _is_int(kovi):
                        continue
                    in_scene = any(_in_range(kovi, lo, hi) for lo, hi in scene_ranges)
                    if not in_scene:
                        errors.append(f"story_map: key ovi {kovi} of event {ev_id} is in no scene")
        except Exception:
            errors.append("aggregate: internal error in X5")

    # X6: story_map + questions + scenes - ambiguous events need questions on overlapping scenes
    if all_valid("story_map", "questions", "scenes"):
        try:
            sm = unit_docs["story_map"]
            questions = unit_docs["questions"]
            scenes = unit_docs["scenes"]

            scene_by_id = {sc.get("scene_id"): sc for sc in scenes.get("scenes", []) if isinstance(sc.get("scene_id"), str)}
            questions_by_scene: dict[str, list[dict]] = {}
            for q in questions.get("questions", []):
                sid = q.get("scene_id")
                if isinstance(sid, str):
                    questions_by_scene.setdefault(sid, []).append(q)

            for ev in sm.get("events", []):
                if ev.get("closure") != "SOURCE_INCOMPLETE_OR_AMBIGUOUS":
                    continue
                ev_id = ev.get("event_id")
                ev_range = ev.get("ovi_range", [0, -1])
                if not (isinstance(ev_range, list) and len(ev_range) == 2 and _is_int(ev_range[0]) and _is_int(ev_range[1])):
                    continue
                ev_lo, ev_hi = ev_range
                has_question = False
                for q_scene_id, q_list in questions_by_scene.items():
                    sc = scene_by_id.get(q_scene_id)
                    if not sc:
                        continue
                    sc_range = sc.get("ovi_range", [0, -1])
                    if not (isinstance(sc_range, list) and len(sc_range) == 2 and _is_int(sc_range[0]) and _is_int(sc_range[1])):
                        continue
                    if _ranges_overlap(ev_lo, ev_hi, sc_range[0], sc_range[1]):
                        has_question = True
                        break
                if not has_question:
                    errors.append(f"story_map: ambiguous event {ev_id} has no question")
        except Exception:
            errors.append("aggregate: internal error in X6")

    # X7: voices + ctx.series_voices
    if all_valid("voices"):
        try:
            voices = unit_docs["voices"]
            series_voices = _get_dict(ctx, "series_voices")
            series_voice_keys = set(series_voices.values())
            for cast in voices.get("cast", []):
                char_id = cast.get("character_id")
                status = cast.get("status")
                voice_key = cast.get("voice_key")
                if not isinstance(char_id, str) or not isinstance(voice_key, str):
                    continue
                if char_id in series_voices:
                    series_key = series_voices[char_id]
                    if status == "RECURRING" and voice_key != series_key:
                        errors.append(f"voices: recurring character {char_id} has a different voice than the series")
                    elif status == "NEW_PROPOSED":
                        errors.append(f"voices: character {char_id} already has a series voice")
                else:
                    # NEW_PROPOSED for a character not in series_voices, but voice_key reuses a series voice
                    if status == "NEW_PROPOSED" and voice_key in series_voice_keys:
                        errors.append(f"voices: character {char_id} reuses the series voice {voice_key}")
        except Exception:
            errors.append("aggregate: internal error in X7")

    # X8: script text guard - 6-word runs
    # Run on all nine documents that are dicts, regardless of schema validity
    try:
        script_texts = _get_str_list(ctx, "script_texts")
        script_runs: set[tuple[str, ...]] = set()
        for script in script_texts:
            words = _normalize_words(script)
            if len(words) >= 6:
                for i in range(len(words) - 5):
                    script_runs.add(tuple(words[i:i+6]))
        if script_runs:
            for unit in UNITS:
                doc = docs.get(unit)
                if not isinstance(doc, dict):
                    continue
                for path, val in _walk_strings(doc):
                    val_words = _normalize_words(val)
                    if len(val_words) < 6:
                        continue
                    for i in range(len(val_words) - 5):
                        run = tuple(val_words[i:i+6])
                        if run in script_runs:
                            errors.append(f"{unit}: free text copies script wording ({path})")
                            break
    except Exception:
        errors.append("aggregate: internal error in X8")

    # X9: story_map + ctx chapter_ovis
    if all_valid("story_map"):
        try:
            sm = unit_docs["story_map"]
            chapter_ovis = _get_int_list(ctx, "chapter_ovis")
            if chapter_ovis:
                ch_min = min(chapter_ovis)
                ch_max = max(chapter_ovis)
                chapter_set = set(chapter_ovis)
                for ev in sm.get("events", []):
                    ev_id = ev.get("event_id")
                    ev_range = ev.get("ovi_range")
                    if isinstance(ev_range, list) and len(ev_range) == 2 and _is_int(ev_range[0]) and _is_int(ev_range[1]):
                        lo, hi = ev_range
                        if lo < ch_min or hi > ch_max:
                            errors.append(f"story_map: event {ev_id} range is outside the chapter")
                    key_ovis = ev.get("key_ovis", [])
                    for kovi in key_ovis:
                        if _is_int(kovi) and kovi not in chapter_set:
                            errors.append(f"story_map: key ovi {kovi} of event {ev_id} is outside the chapter")
        except Exception:
            errors.append("aggregate: internal error in X9")

    # X10: story_map + scenes - scene section_kind must match at least one overlapping event's kind
    if all_valid("story_map", "scenes"):
        try:
            sm = unit_docs["story_map"]
            scenes = unit_docs["scenes"]
            events = sm.get("events", [])
            for sc in scenes.get("scenes", []):
                scene_id = sc.get("scene_id")
                section_kind = sc.get("section_kind")
                sc_range = sc.get("ovi_range")
                if not (isinstance(scene_id, str) and isinstance(section_kind, str) and isinstance(sc_range, list) and len(sc_range) == 2 and _is_int(sc_range[0]) and _is_int(sc_range[1])):
                    continue
                sc_lo, sc_hi = sc_range
                overlapping_kinds = set()
                for ev in events:
                    ev_range = ev.get("ovi_range")
                    ev_kind = ev.get("kind")
                    if not (isinstance(ev_range, list) and len(ev_range) == 2 and _is_int(ev_range[0]) and _is_int(ev_range[1]) and isinstance(ev_kind, str)):
                        continue
                    if _ranges_overlap(sc_lo, sc_hi, ev_range[0], ev_range[1]):
                        overlapping_kinds.add(ev_kind)
                if overlapping_kinds and section_kind not in overlapping_kinds:
                    errors.append(f"scenes: scene {scene_id} is {section_kind} but its events are not {section_kind}")
        except Exception:
            errors.append("aggregate: internal error in X10")

    # X11: voices + ctx.verified_voices
    if all_valid("voices"):
        try:
            voices = unit_docs["voices"]
            verified_voices = ctx.get("verified_voices")
            if isinstance(verified_voices, list):
                verified_set = {v for v in verified_voices if isinstance(v, str)}
                for cast in voices.get("cast", []):
                    voice_key = cast.get("voice_key")
                    if isinstance(voice_key, str) and voice_key not in verified_set:
                        errors.append(f"voices: voice {voice_key} is not verified for Marathi and Hindi")
        except Exception:
            errors.append("aggregate: internal error in X11")

    return errors


def export_schemas(out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    target_paths = [out_dir / f"stage1_{unit}.schema.json" for unit in UNITS]
    for p in target_paths:
        if p.exists():
            raise FileExistsError(f"refused: {p} already exists")
    written: list[Path] = []
    for unit, target in zip(UNITS, target_paths):
        module = _load_unit(unit)
        if module is None or not hasattr(module, "SCHEMA"):
            raise RuntimeError(f"aggregate: cannot load {unit} for schema export")
        schema = module.SCHEMA
        content = json.dumps(schema, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
        target.write_text(content, encoding="utf-8")
        written.append(target)
    return written


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--adhyay", type=int, required=True)
    parser.add_argument("--docs-dir", type=Path, required=True)
    parser.add_argument("--ctx", type=Path, default=None)
    parser.add_argument("--export-schemas", type=Path, default=None)
    args = parser.parse_args(argv)

    docs: dict[str, Any] = {}
    for unit in UNITS:
        path = args.docs_dir / f"{unit}.json"
        if path.exists():
            try:
                docs[unit] = json.loads(path.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"refused: cannot read {path}: {e}")
                return 2

    ctx: dict[str, Any] = {}
    if args.ctx and args.ctx.exists():
        try:
            ctx = json.loads(args.ctx.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"refused: cannot read {args.ctx}: {e}")
            return 2

    if args.export_schemas:
        try:
            export_schemas(args.export_schemas)
        except FileExistsError as e:
            print(f"refused: {e}")
            return 2
        except Exception as e:
            print(f"refused: {e}")
            return 2
        # Continue to validation after successful export

    errors = validate_all(args.adhyay, docs, ctx)
    for err in errors:
        print(err)
    print(f"{len(errors)} error(s)")
    return 0 if len(errors) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

```

## CURRENT TESTS tests/test_stage1_aggregate.py
```python
from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGG_PATH = ROOT / "scripts" / "pipeline" / "stage1" / "aggregate.py"
BASE_PATH = ROOT / "docs" / "pilot" / "nemotron_specs" / "stage1_base.json"

spec = importlib.util.spec_from_file_location("stage1_aggregate", AGG_PATH)
assert spec is not None and spec.loader is not None
agg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agg)

BASE = json.loads(BASE_PATH.read_text(encoding="utf-8"))
BASE_DOCS = BASE["docs"]
BASE_CTX = BASE["ctx"]


def _make_minimal_valid_docs(ovis_covered: list[int] | None = None) -> tuple[dict, dict]:
    """Create a minimal valid set of documents and ctx for the given ovis.
    This is used to isolate cross-rule tests."""
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # We'll adjust the base to only involve the ovis we care about.
    # But the base is already valid. We'll instead modify the base in the tests.
    return docs, ctx


def test_base_valid():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    errs = agg.validate_all(1, docs, ctx)
    assert errs == []


def test_x1_story_ovi_not_in_story_event():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Make ovi 3 STORY but events only cover [4,5] as discourse
    docs["story_map"]["ovi_types"] = [{"ovi": 3, "type": "STORY"}, {"ovi": 4, "type": "STORY"}]
    docs["story_map"]["events"] = [{"event_id": "E1", "kind": "discourse", "title": "t", "ovi_range": [4, 5], "key_ovis": [4], "closure": "RESOLVED_IN_ADHYAY"}]
    # Adjust ctx chapter_ovis to only 3,4 so story_map unit validation passes
    ctx["chapter_ovis"] = [3, 4]
    # Ensure coverage for 3,4 is not PROPOSE_OMISSION and they are in shots/scenes
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] in (3, 4):
            c["disposition"] = "VISUALISED"
    # Ensure scenes cover 3,4
    for sc in docs["scenes"]["scenes"]:
        sc["ovi_range"] = [3, 4]
    # Ensure shots include 3,4
    for sh in docs["shots"]["shots"]:
        sh["ovi_ids"] = [3, 4]
    # No unfilmed ovis
    ctx["unfilmed_ovis"] = []
    errs = agg.validate_all(1, docs, ctx)
    assert any("story_map: ovi 3 is typed STORY but is in no story event" in e for e in errs)
    # Corrected twin: expand event range to cover 3 and make it story kind
    docs["story_map"]["events"][0]["ovi_range"] = [3, 5]
    docs["story_map"]["events"][0]["kind"] = "story"
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any("story_map: ovi 3 is typed STORY but is in no story event" in e for e in errs2)


def test_x1_teaching_ovi_not_in_discourse_event():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Make ovi 6 TEACHING but events only cover [1,5] as story
    docs["story_map"]["ovi_types"] = [{"ovi": 6, "type": "TEACHING"}, {"ovi": 4, "type": "TEACHING"}]
    docs["story_map"]["events"] = [{"event_id": "E1", "kind": "story", "title": "t", "ovi_range": [1, 5], "key_ovis": [4], "closure": "RESOLVED_IN_ADHYAY"}]
    ctx["chapter_ovis"] = [4, 6]
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] in (4, 6):
            c["disposition"] = "VISUALISED"
    for sc in docs["scenes"]["scenes"]:
        sc["ovi_range"] = [4, 6]
    for sh in docs["shots"]["shots"]:
        sh["ovi_ids"] = [4, 6]
    ctx["unfilmed_ovis"] = []
    errs = agg.validate_all(1, docs, ctx)
    assert any("story_map: ovi 6 is typed TEACHING but is in no discourse event" in e for e in errs)
    # Corrected twin: add discourse event covering 6
    docs["story_map"]["events"].append({"event_id": "E2", "kind": "discourse", "title": "t2", "ovi_range": [6, 6], "key_ovis": [6], "closure": "RESOLVED_IN_ADHYAY"})
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any("story_map: ovi 6 is typed TEACHING but is in no discourse event" in e for e in errs2)


def test_x1_empty_events():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    docs["story_map"]["ovi_types"] = [{"ovi": 1, "type": "STORY"}, {"ovi": 2, "type": "TEACHING"}]
    docs["story_map"]["events"] = []
    ctx["chapter_ovis"] = [1, 2]
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] in (1, 2):
            c["disposition"] = "VISUALISED"
    for sc in docs["scenes"]["scenes"]:
        sc["ovi_range"] = [1, 2]
    for sh in docs["shots"]["shots"]:
        sh["ovi_ids"] = [1, 2]
    ctx["unfilmed_ovis"] = []
    errs = agg.validate_all(1, docs, ctx)
    assert any("story_map: ovi 1 is typed STORY but is in no story event" in e for e in errs)
    assert any("story_map: ovi 2 is typed TEACHING but is in no discourse event" in e for e in errs)


def test_x3_proposed_not_in_unfilmed():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    ovi = docs["coverage"]["ovis"][0]["ovi"]
    docs["coverage"]["ovis"][0]["disposition"] = "PROPOSE_OMISSION"
    docs["coverage"]["ovis"][0]["reason"] = "test"
    ctx["unfilmed_ovis"] = []
    for c in docs["coverage"]["ovis"][1:]:
        if c["disposition"] == "PROPOSE_OMISSION":
            c["disposition"] = "VISUALISED"
    errs = agg.validate_all(1, docs, ctx)
    assert any(f"coverage: ovi {ovi} omission is not approved by the owner" in e for e in errs)


def test_x3_unfilmed_without_proposal():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    ovi = 999
    ctx["unfilmed_ovis"] = [ovi]
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] == ovi:
            c["disposition"] = "VISUALISED"
    for c in docs["coverage"]["ovis"]:
        if c["disposition"] == "PROPOSE_OMISSION":
            c["disposition"] = "VISUALISED"
    errs = agg.validate_all(1, docs, ctx)
    assert any(f"coverage: ovi {ovi} is approved as unfilmed but has no omission proposal" in e for e in errs)


def test_x4_visualised_not_in_shot():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    ovi = docs["coverage"]["ovis"][0]["ovi"]
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] == ovi:
            c["disposition"] = "VISUALISED"
            break
    for sh in docs["shots"]["shots"]:
        if ovi in sh.get("ovi_ids", []):
            sh["ovi_ids"] = [x for x in sh["ovi_ids"] if x != ovi]
    for sc in docs["scenes"]["scenes"]:
        if sc["ovi_range"][0] <= ovi <= sc["ovi_range"][1]:
            break
    else:
        docs["scenes"]["scenes"][0]["ovi_range"] = [ovi, ovi]
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] != ovi and c["disposition"] == "VISUALISED":
            if ovi not in docs["shots"]["shots"][0]["ovi_ids"]:
                docs["shots"]["shots"][0]["ovi_ids"].append(c["ovi"])
    errs = agg.validate_all(1, docs, ctx)
    assert any(f"coverage: ovi {ovi} is VISUALISED but is in no shot" in e for e in errs)
    docs["shots"]["shots"][0]["ovi_ids"].append(ovi)
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any(f"coverage: ovi {ovi} is VISUALISED but is in no shot" in e for e in errs2)


def test_x4_non_omitted_not_in_scene():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    ovi = docs["coverage"]["ovis"][0]["ovi"]
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] == ovi:
            c["disposition"] = "NARRATED"
            break
    for sc in docs["scenes"]["scenes"]:
        sc["ovi_range"] = [100, 200]
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] == ovi:
            c["disposition"] = "NARRATED"
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] != ovi and c["disposition"] != "PROPOSE_OMISSION":
            docs["scenes"]["scenes"][0]["ovi_range"] = [c["ovi"], c["ovi"]]
    errs = agg.validate_all(1, docs, ctx)
    assert any(f"coverage: ovi {ovi} is in no scene" in e for e in errs)
    docs["scenes"]["scenes"][0]["ovi_range"] = [ovi, ovi]
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any(f"coverage: ovi {ovi} is in no scene" in e for e in errs2)


def test_x5_key_ovi_not_in_scene():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    docs["story_map"]["events"][0]["key_ovis"] = [999]
    for sc in docs["scenes"]["scenes"]:
        sc["ovi_range"] = [1, 10]
    if not any(c["ovi"] == 999 for c in docs["coverage"]["ovis"]):
        docs["coverage"]["ovis"].append({"ovi": 999, "disposition": "NARRATED"})
    else:
        for c in docs["coverage"]["ovis"]:
            if c["ovi"] == 999:
                c["disposition"] = "NARRATED"
    errs = agg.validate_all(1, docs, ctx)
    assert any("story_map: key ovi 999 of event" in e and "is in no scene" in e for e in errs)
    docs["scenes"]["scenes"][0]["ovi_range"] = [999, 999]
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any("story_map: key ovi 999 of event" in e and "is in no scene" in e for e in errs2)


def test_x6_ambiguous_event_no_question():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    for ev in docs["story_map"]["events"]:
        if ev["event_id"] == "E2":
            ev["closure"] = "SOURCE_INCOMPLETE_OR_AMBIGUOUS"
            break
    docs["questions"]["questions"] = [q for q in docs["questions"]["questions"] if q.get("scene_id") != "S2"]
    e2_range = None
    for ev in docs["story_map"]["events"]:
        if ev["event_id"] == "E2":
            e2_range = ev["ovi_range"]
            break
    if e2_range:
        s2_found = False
        for sc in docs["scenes"]["scenes"]:
            if sc.get("scene_id") == "S2":
                s2_found = True
                sc["ovi_range"] = [e2_range[0], e2_range[1]]
                break
        if not s2_found:
            docs["scenes"]["scenes"].append({"scene_id": "S2", "section_kind": "story", "ovi_range": e2_range, "line_ids": []})
    errs = agg.validate_all(1, docs, ctx)
    assert any("story_map: ambiguous event E2 has no question" in e for e in errs)
    docs["questions"]["questions"].append({"id": "Q99", "text": "test", "scene_id": "S2"})
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any("story_map: ambiguous event E2 has no question" in e for e in errs2)


def test_x7_recurring_voice_mismatch():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    ctx["series_voices"] = {"gajanan_maharaj": "other_key"}
    saved = list(ctx.get("saved_voices", []))
    if "different_key" not in saved:
        saved.append("different_key")
    ctx["saved_voices"] = saved
    for cast in docs["voices"]["cast"]:
        if cast["character_id"] == "gajanan_maharaj":
            cast["status"] = "RECURRING"
            cast["voice_key"] = "different_key"
            break
    errs = agg.validate_all(1, docs, ctx)
    assert any("voices: recurring character gajanan_maharaj has a different voice than the series" in e for e in errs)
    for cast in docs["voices"]["cast"]:
        if cast["character_id"] == "gajanan_maharaj":
            cast["voice_key"] = "other_key"
            break
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any("voices: recurring character gajanan_maharaj has a different voice than the series" in e for e in errs2)


def test_x7_new_proposed_for_series_char():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    ctx["series_voices"] = {"gajanan_maharaj": "some_key"}
    saved = list(ctx.get("saved_voices", []))
    if "some_key" not in saved:
        saved.append("some_key")
    ctx["saved_voices"] = saved
    for cast in docs["voices"]["cast"]:
        if cast["character_id"] == "gajanan_maharaj":
            cast["status"] = "NEW_PROPOSED"
            cast["voice_key"] = "some_key"
            cast["reason"] = "new voice for series character"
            break
    errs = agg.validate_all(1, docs, ctx)
    assert any("voices: character gajanan_maharaj already has a series voice" in e for e in errs)
    for cast in docs["voices"]["cast"]:
        if cast["character_id"] == "gajanan_maharaj":
            cast["status"] = "RECURRING"
            cast["voice_key"] = "some_key"
            break
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any("voices: character gajanan_maharaj already has a series voice" in e for e in errs2)


def test_x7_new_proposed_reuses_series_voice():
    """NEW_PROPOSED character (not in series_voices) reuses a voice_key that belongs to a series character."""
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Base fixture: ctx['saved_voices'] is a dict {voice_key: voice_id}
    # Base cast: narrator (RECURRING, key narrator), gajanan_maharaj (RECURRING, key gajanan)
    ctx["series_voices"] = {"gajanan_maharaj": "gajanan"}
    # Add a new saved voice for the new character
    ctx["saved_voices"]["villager"] = "ABCDEFGHIJ"
    # Append a NEW_PROPOSED entry for a character not in series_voices, reusing the series voice 'gajanan'
    new_char = {
        "character_id": "villager",
        "voice_key": "gajanan",
        "voice_id": "8fqGzH80bdkm2UseeV9f",
        "gender": "male",
        "status": "NEW_PROPOSED",
        "reason": "older villager voice chosen from the description"
    }
    docs["voices"]["cast"].append(new_char)
    errs = agg.validate_all(1, docs, ctx)
    assert any("villager" in e and "reuses the series voice" in e for e in errs)
    # Corrected twin: use a different voice_key that matches the new saved_voices entry
    new_char["voice_key"] = "villager"
    new_char["voice_id"] = "ABCDEFGHIJ"
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any("reuses the series voice" in e for e in errs2)


def test_x8_script_text_copied():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # 6-word run from script line
    script_line = "This is a long enough script line for testing purposes"
    ctx["script_texts"] = [script_line]
    # Copy into scenes[0].goal - contains the 6-word run "a long enough script line for"
    docs["scenes"]["scenes"][0]["goal"] = "Here is a long enough script line for the scene"
    errs = agg.validate_all(1, docs, ctx)
    assert any("scenes: free text copies script wording (scenes/0/goal)" in e for e in errs)
    # Five words should not trigger
    docs["scenes"]["scenes"][0]["goal"] = "Here is a long enough"
    ctx["script_texts"] = ["Here is a long enough"]
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any("free text copies script wording" in e for e in errs2)


def test_x8_script_text_copied_other_unit():
    """X8 should run on all 9 documents even if another unit fails schema."""
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    script_line = "This is a long enough script line for testing purposes"
    ctx["script_texts"] = [script_line]
    # Break coverage schema
    docs["coverage"] = {"ovis": "invalid"}
    # Put script text in questions[0].text (a different unit)
    # Ensure there is at least one question
    if not docs["questions"]["questions"]:
        docs["questions"]["questions"].append({"id": "Q1", "text": "", "scene_id": "S1"})
    docs["questions"]["questions"][0]["text"] = "Here is a long enough script line for the question"
    errs = agg.validate_all(1, docs, ctx)
    # Should have schema error for coverage
    assert any("coverage" in e for e in errs)
    # Should still catch X8 in questions
    assert any("questions: free text copies script wording (questions/0/text)" in e for e in errs)


def test_x8_punctuation_normalization():
    """Punctuation should be stripped before word matching."""
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    script_line = "This is a long enough script line for testing purposes"
    ctx["script_texts"] = [script_line]
    # With punctuation differences
    docs["scenes"]["scenes"][0]["goal"] = "Here is a long, enough script; line: for the scene!"
    errs = agg.validate_all(1, docs, ctx)
    assert any("scenes: free text copies script wording (scenes/0/goal)" in e for e in errs)


def test_x9_event_range_outside_chapter():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Chapter ovis 1-9, event at 900-905
    ctx["chapter_ovis"] = list(range(1, 10))
    docs["story_map"]["events"][0]["ovi_range"] = [900, 905]
    docs["story_map"]["events"][0]["event_id"] = "E99"
    errs = agg.validate_all(1, docs, ctx)
    assert any("story_map: event E99 range is outside the chapter" in e for e in errs)


def test_x9_key_ovi_outside_chapter():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    ctx["chapter_ovis"] = list(range(1, 10))
    docs["story_map"]["events"][0]["key_ovis"] = [999]
    docs["story_map"]["events"][0]["event_id"] = "E99"
    errs = agg.validate_all(1, docs, ctx)
    assert any("story_map: key ovi 999 of event E99 is outside the chapter" in e for e in errs)


def test_x9_valid_base_clean():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    errs = agg.validate_all(1, docs, ctx)
    assert not any("outside the chapter" in e for e in errs)


def test_x10_scene_kind_mismatch():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Base has S1 as story, E1 as story - should be clean
    errs = agg.validate_all(1, docs, ctx)
    assert not any("scenes: scene" in e and "but its events are not" in e for e in errs)
    # Change E1 kind to discourse, S1 stays story -> error
    for ev in docs["story_map"]["events"]:
        if ev["event_id"] == "E1":
            ev["kind"] = "discourse"
            break
    errs = agg.validate_all(1, docs, ctx)
    assert any("scenes: scene S1 is story but its events are not story" in e for e in errs)
    # Corrected twin: add another event E3 with kind story overlapping S1
    docs["story_map"]["events"].append({"event_id": "E3", "kind": "story", "title": "t3", "ovi_range": [1, 5], "key_ovis": [1], "closure": "RESOLVED_IN_ADHYAY"})
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any("scenes: scene S1 is story but its events are not story" in e for e in errs2)


def test_x10_scene_no_overlapping_event():
    """Scene with no overlapping event should not trigger X10 (X5 handles key ovis)."""
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Add a scene with ovi_range that doesn't overlap any event
    docs["scenes"]["scenes"].append({"scene_id": "S99", "section_kind": "story", "ovi_range": [900, 900], "line_ids": []})
    # Ensure coverage has this ovi so X4 doesn't fire
    docs["coverage"]["ovis"].append({"ovi": 900, "disposition": "NARRATED"})
    errs = agg.validate_all(1, docs, ctx)
    assert not any("scenes: scene S99" in e for e in errs)


def test_x11_verified_voices_absent():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # verified_voices absent -> rule skipped
    errs = agg.validate_all(1, docs, ctx)
    assert not any("verified for Marathi and Hindi" in e for e in errs)


def test_x11_verified_voices_all_present():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Collect all voice_keys from base
    voice_keys = [cast["voice_key"] for cast in docs["voices"]["cast"]]
    ctx["verified_voices"] = voice_keys
    errs = agg.validate_all(1, docs, ctx)
    assert not any("verified for Marathi and Hindi" in e for e in errs)


def test_x11_verified_voices_missing():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    voice_keys = [cast["voice_key"] for cast in docs["voices"]["cast"]]
    # Remove one
    ctx["verified_voices"] = voice_keys[:-1]
    missing_key = voice_keys[-1]
    errs = agg.validate_all(1, docs, ctx)
    assert any(f"voices: voice {missing_key} is not verified for Marathi and Hindi" in e for e in errs)


def test_x11_verified_voices_wrong_types():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    for bad_val in [None, 5, "x", [[1]]]:
        ctx["verified_voices"] = bad_val
        errs = agg.validate_all(1, docs, ctx)
        assert isinstance(errs, list)
        assert not any("internal error in X11" in e for e in errs)


def test_propose_omission_story_ovi_no_x2_error():
    """A STORY ovi with PROPOSE_OMISSION that IS in unfilmed_ovis produces NO X2 error (X2 removed) and NO X3 error."""
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Find a STORY ovi in base
    story_ovi = None
    for ot in docs["story_map"]["ovi_types"]:
        if ot["type"] == "STORY":
            story_ovi = ot["ovi"]
            break
    assert story_ovi is not None
    # Set coverage to PROPOSE_OMISSION for that ovi
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] == story_ovi:
            c["disposition"] = "PROPOSE_OMISSION"
            c["reason"] = "test"
            break
    # Add to unfilmed so X3 passes
    ctx["unfilmed_ovis"] = [story_ovi]
    # Ensure it's in a scene and shot so X4 doesn't fire
    for sc in docs["scenes"]["scenes"]:
        if sc["ovi_range"][0] <= story_ovi <= sc["ovi_range"][1]:
            break
    else:
        docs["scenes"]["scenes"][0]["ovi_range"] = [story_ovi, story_ovi]
    for sh in docs["shots"]["shots"]:
        if story_ovi in sh.get("ovi_ids", []):
            break
    else:
        docs["shots"]["shots"][0]["ovi_ids"].append(story_ovi)
    # Ensure no other PROPOSE_OMISSION
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] != story_ovi and c["disposition"] == "PROPOSE_OMISSION":
            c["disposition"] = "VISUALISED"
    errs = agg.validate_all(1, docs, ctx)
    # No X2 error (rule removed): no message containing 'omission is proposed'
    assert not any("omission is proposed" in e for e in errs)
    # No X3 error for this ovi
    assert not any(f"coverage: ovi {story_ovi} omission is not approved" in e for e in errs)
    assert not any(f"coverage: ovi {story_ovi} is approved as unfilmed but has no omission proposal" in e for e in errs)


def test_robustness_docs_none():
    errs = agg.validate_all(1, None, {})
    assert any("aggregate: docs must be an object" in e for e in errs)
    assert sum(1 for e in errs if "document missing" in e) == 9


def test_robustness_docs_empty():
    errs = agg.validate_all(1, {}, {})
    assert sum(1 for e in errs if "document missing" in e) == 9


def test_robustness_ctx_none():
    docs = copy.deepcopy(BASE_DOCS)
    errs = agg.validate_all(1, docs, None)
    assert any("aggregate: ctx must be an object" in e for e in errs)
    assert not any("internal error" in e for e in errs)


def test_robustness_doc_is_list():
    docs = copy.deepcopy(BASE_DOCS)
    docs["story_map"] = []
    errs = agg.validate_all(1, docs, {})
    assert any("story_map: document missing" in e for e in errs)
    assert not any("internal error" in e for e in errs)


def test_robustness_schema_failure_skips_validate_and_cross():
    docs = copy.deepcopy(BASE_DOCS)
    docs["coverage"] = {"ovis": "invalid"}
    errs = agg.validate_all(1, docs, {})
    cov_module = agg._load_unit("coverage")
    schema_errs = cov_module.schema_errors(docs["coverage"]) if cov_module else []
    assert schema_errs, "coverage schema should produce errors for invalid ovis"
    assert any(any(se in e for e in errs) for se in schema_errs)
    assert not any("internal error in coverage.validate" in e for e in errs)
    assert not any("coverage: ovi" in e and ("omission" in e or "VISUALISED" in e or "in no scene" in e) for e in errs)


def test_robustness_huge_ranges():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    for i, sc in enumerate(docs["scenes"]["scenes"]):
        start = 1 + i * 10**12
        end = start + 10**12 - 1
        sc["ovi_range"] = [start, end]
    for i, ev in enumerate(docs["story_map"]["events"]):
        start = 1 + i * 10**12
        end = start + 10**12 - 1
        ev["ovi_range"] = [start, end]
    errs = agg.validate_all(1, docs, ctx)
    assert isinstance(errs, list)


def test_robustness_ctx_unfilmed_ovis_bad_types():
    """ctx.unfilmed_ovis with bad types should not raise, just be treated as empty."""
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    for bad_val in [None, 5, "x", [[1]], [1, {}], [1, 2, "three"], [True, False]]:
        ctx["unfilmed_ovis"] = bad_val
        errs = agg.validate_all(1, docs, ctx)
        assert isinstance(errs, list)
        assert not any("internal error in X3" in e for e in errs)


def test_robustness_ctx_series_voices_bad_types():
    """ctx.series_voices with bad types should not raise, just be treated as empty."""
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    for bad_val in [None, 5, "x", ["a", "b"], [{"a": 1}]]:
        ctx["series_voices"] = bad_val
        errs = agg.validate_all(1, docs, ctx)
        assert isinstance(errs, list)
        assert not any("internal error in X7" in e for e in errs)


def test_robustness_ctx_script_texts_bad_types():
    """ctx.script_texts with bad types should not raise, just be treated as empty."""
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    for bad_val in [None, 5, "x", [1, 2], [{"a": 1}]]:
        ctx["script_texts"] = bad_val
        errs = agg.validate_all(1, docs, ctx)
        assert isinstance(errs, list)
        assert not any("internal error in X8" in e for e in errs)


def test_robustness_ctx_chapter_ovis_bad_types():
    """ctx.chapter_ovis with bad types should not raise, just be treated as empty."""
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    for bad_val in [None, 5, "x", [[1]], [1, {}], [1, 2, "three"], [True, False]]:
        ctx["chapter_ovis"] = bad_val
        errs = agg.validate_all(1, docs, ctx)
        assert isinstance(errs, list)
        assert not any("internal error in X9" in e for e in errs)


def test_robustness_ctx_verified_voices_bad_types():
    """ctx.verified_voices with bad types should not raise, just be treated as absent (rule skipped)."""
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    for bad_val in [None, 5, "x", [[1]], [1, {}], [1, 2, "three"], [True, False]]:
        ctx["verified_voices"] = bad_val
        errs = agg.validate_all(1, docs, ctx)
        assert isinstance(errs, list)
        assert not any("internal error in X11" in e for e in errs)


def test_export_schemas(tmp_path):
    out_dir = tmp_path / "schemas"
    paths = agg.export_schemas(out_dir)
    assert len(paths) == 9
    for p in paths:
        assert p.exists()
        content = p.read_text(encoding="utf-8")
        assert content.endswith("\n")
        json.loads(content)
    try:
        agg.export_schemas(out_dir)
        assert False, "expected FileExistsError"
    except FileExistsError:
        pass
    for p in paths:
        assert p.exists()


def test_main_exit_codes(tmp_path, capsys):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    for unit in agg.UNITS:
        (docs_dir / f"{unit}.json").write_text(json.dumps(BASE_DOCS[unit]), encoding="utf-8")
    ctx_file = tmp_path / "ctx.json"
    ctx_file.write_text(json.dumps(BASE_CTX), encoding="utf-8")

    # Valid docs, export schemas -> should validate and return 0
    schema_dir = tmp_path / "schemas"
    rc = agg.main(["--adhyay", "1", "--docs-dir", str(docs_dir), "--ctx", str(ctx_file), "--export-schemas", str(schema_dir)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "0 error(s)" in out
    # Schemas should be written
    assert (schema_dir / "stage1_story_map.schema.json").exists()

    # Valid docs, export schemas to existing dir -> refused
    rc = agg.main(["--adhyay", "1", "--docs-dir", str(docs_dir), "--ctx", str(ctx_file), "--export-schemas", str(schema_dir)])
    assert rc == 2
    out = capsys.readouterr().out
    assert "refused:" in out

    # Invalid docs, export schemas -> should validate and return 1
    bad_docs = copy.deepcopy(BASE_DOCS)
    bad_docs["story_map"]["ovi_types"] = [{"ovi": 999, "type": "STORY"}]
    bad_docs["story_map"]["events"] = []
    (docs_dir / "story_map.json").write_text(json.dumps(bad_docs["story_map"]), encoding="utf-8")
    schema_dir2 = tmp_path / "schemas2"
    rc = agg.main(["--adhyay", "1", "--docs-dir", str(docs_dir), "--ctx", str(ctx_file), "--export-schemas", str(schema_dir2)])
    assert rc == 1
    out = capsys.readouterr().out
    assert "error(s)" in out
    # Schemas should still be written
    assert (schema_dir2 / "stage1_story_map.schema.json").exists()

    # Unreadable JSON -> refused (exit 2)
    (docs_dir / "coverage.json").write_text("not json", encoding="utf-8")
    rc = agg.main(["--adhyay", "1", "--docs-dir", str(docs_dir), "--ctx", str(ctx_file)])
    assert rc == 2
    out = capsys.readouterr().out
    assert "refused:" in out

```


## ROUND 9 FINDINGS (Codex + Haiku final review). IGNORE older text of X1/X2 in this spec: the AMENDMENTS section is authoritative (X1 kind-aware, X2 removed). Change NOTHING else in the modules. Tests: copy.deepcopy + plain assignment; never a no-effect-rejecting helper; True == 1. Return FOUR complete FILE blocks.
A. aggregate.py (X7): `set(series_voices.values())` raises on unhashable values (series_voices = {"x": []} gives the forbidden `aggregate: internal error in X7`). Read series_voices through the helper that keeps ONLY entries whose key and value are both str; use that cleaned dict everywhere in X7. Test: series_voices {"x": []}, {"x": {"a": 1}}, {"x": None}, {1: "k"} each give a list and no 'internal error'.
B. aggregate.py (X8): the normaliser must treat punctuation the same on both sides. Normalise by splitting on whitespace, casefolding, then stripping from BOTH ENDS of every token all characters whose `unicodedata.category` starts with 'P' or 'S' (this covers '/', '|', quotes, danda marks and so on); drop empty tokens. Do NOT use the regex \w (it splits Devanagari words at vowel signs). Test: script text 'one two three four five six' and a document string 'one two three four five six/' IS flagged; the same with surrounding quotes/brackets is flagged; five words are not.
C. context.py: valid JSON that is not an object must become a source problem, never an exception: the omissions file (`omissions: not an object`), the voice library (`voice_library: not an object`, or its `voices` not a list: `voice_library: bad voices`), a JSONL line that is valid JSON but not an object (`source_ovis: bad line <n>`, skipped), the preset index not being a list (`presets: not a list`), the sound palette (`sounds: bad palette`), the approvals file containing a non-object (treated as empty). All `.get()` calls must be inside the guarded reads. Tests (one per source): the JSON `[]`, `5`, `"x"`, `null` for each of those files -> no exception, the documented empty value and the problem text.
D. FYI do not change: X10 intentionally reports nothing for a scene with no overlapping event (X1 already fails story/teaching ovis in no event).

## CURRENT scripts/pipeline/stage1/context.py
```python
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

# Load dependent modules by absolute path to avoid package installation issues.
_REPO_ROOT = Path(__file__).resolve().parents[3]
_CHAPTER_PATH = _REPO_ROOT / "scripts" / "pipeline" / "chapter.py"
_APPROVALS_PATH = _REPO_ROOT / "scripts" / "pipeline" / "approvals.py"

import importlib.util

def _load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module {module_name} from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

_chapter_mod = _load_module("chapter", _CHAPTER_PATH)
_approvals_mod = _load_module("approvals", _APPROVALS_PATH)

chapter_paths = _chapter_mod.chapter_paths
sha256_file = _approvals_mod.sha256_file
load_approvals = _approvals_mod.load
approval_status = _approvals_mod.status


def _read_ovis(source_ovis: Path) -> tuple[list[int], list[str]]:
    """Read OVI numbers from a JSONL file."""
    ovis: set[int] = set()
    problems: list[str] = []
    if not source_ovis.is_file():
        problems.append("source_ovis: missing")
        return [], problems
    try:
        with source_ovis.open("r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    problems.append(f"source_ovis: bad line {i}")
                    continue
                ovi = obj.get("ovi")
                if isinstance(ovi, bool) or not isinstance(ovi, int):
                    problems.append(f"source_ovis: bad line {i}")
                    continue
                ovis.add(ovi)
    except Exception as e:
        problems.append(f"source_ovis: {e.__class__.__name__}")
    return sorted(ovis), problems


def _read_omissions(
    omissions_path: Path, approvals_path: Path
) -> tuple[list[int], list[str]]:
    """Read approved omissions OVI list."""
    problems: list[str] = []
    if not omissions_path.is_file():
        return [], problems  # absent file -> empty list, no problem

    # Read omissions file
    try:
        with omissions_path.open("r", encoding="utf-8") as f:
            omissions_data = json.load(f)
    except Exception as e:
        problems.append(f"omissions: {e.__class__.__name__}")
        return [], problems

    ovis = omissions_data.get("ovis", [])
    if not isinstance(ovis, list):
        ovis = []
    else:
        ovis = [int(v) for v in ovis if isinstance(v, int) and not isinstance(v, bool)]

    # Load approvals mapping
    try:
        approvals = load_approvals(approvals_path)
    except Exception:
        approvals = {}

    # Compute status
    try:
        current_sha = sha256_file(omissions_path)
    except Exception as e:
        problems.append(f"omissions: {e.__class__.__name__}")
        return [], problems

    status = approval_status(approvals, "stage1_omissions", current_sha)
    if status == "APPROVED":
        return ovis, problems
    else:
        problems.append(f"omissions: {status} (the owner has not approved the current omissions file)")
        return [], problems


def _read_voice_library(voice_lib_path: Path) -> tuple[dict[str, str], dict[str, str], list[str], list[str]]:
    """Read voice library and return saved_voices, series_voices, verified_voices, problems."""
    saved_voices: dict[str, str] = {}
    series_voices: dict[str, str] = {}
    verified_voices: list[str] = []
    problems: list[str] = []

    if not voice_lib_path.is_file():
        problems.append("voice_library: missing")
        return saved_voices, series_voices, verified_voices, problems

    try:
        with voice_lib_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        problems.append(f"voice_library: {e.__class__.__name__}")
        return saved_voices, series_voices, verified_voices, problems

    voices = data.get("voices", [])
    if not isinstance(voices, list):
        voices = []

    for entry in voices:
        if not isinstance(entry, dict):
            continue
        voice_key = entry.get("voice_key")
        voice_id = entry.get("voice_id")
        if isinstance(voice_key, str) and isinstance(voice_id, str):
            saved_voices[voice_key] = voice_id

        assigned = entry.get("assigned_to", [])
        if isinstance(assigned, list):
            for char_id in assigned:
                if not isinstance(char_id, str):
                    continue
                if char_id in series_voices:
                    problems.append(f"voices: character {char_id} is assigned to more than one voice")
                else:
                    series_voices[char_id] = voice_key

        marathi = entry.get("marathi_verified")
        hindi = entry.get("hindi_verified")
        if marathi is True and hindi is True and isinstance(voice_key, str):
            verified_voices.append(voice_key)

    return saved_voices, series_voices, verified_voices, problems


def _read_presets(preset_index_path: Path) -> tuple[list[str], list[str]]:
    """Read preset IDs from index.json."""
    problems: list[str] = []
    if not preset_index_path.is_file():
        problems.append("presets: missing")
        return [], problems
    try:
        with preset_index_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        problems.append(f"presets: {e.__class__.__name__}")
        return [], problems

    preset_ids: list[str] = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                preset = item.get("preset")
                if isinstance(preset, str):
                    preset_ids.append(preset)
    return preset_ids, problems


def _read_sound_palette(sound_palette_path: Path) -> tuple[list[str], list[str]]:
    """Read sound IDs from palette.json."""
    problems: list[str] = []
    if not sound_palette_path.is_file():
        return [], problems  # absent -> empty, no problem
    try:
        with sound_palette_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        problems.append(f"sound_palette: {e.__class__.__name__}")
        return [], problems

    sound_ids: list[str] = []
    sounds_list: list[Any] = []
    if isinstance(data, dict):
        sounds_list = data.get("sounds", [])
    elif isinstance(data, list):
        sounds_list = data

    if isinstance(sounds_list, list):
        for item in sounds_list:
            if isinstance(item, dict):
                sid = item.get("id")
                if isinstance(sid, str):
                    sound_ids.append(sid)
    return sound_ids, problems


def build_ctx(adhyay: int, root: Path | str, extra: dict | None = None) -> tuple[dict, list[str]]:
    """Build the Stage 1 context dictionary for the given adhyay."""
    root_path = Path(root)
    problems: list[str] = []

    # Validate adhyay
    if type(adhyay) is not int or not (1 <= adhyay <= 21):
        return {}, ["adhyay must be an int in 1..21"]

    # Get chapter-specific paths
    try:
        paths = chapter_paths(adhyay, root_path)
    except Exception as e:
        problems.append(f"chapter_paths: {e.__class__.__name__}")
        paths = {}

    # 1. chapter_ovis
    source_ovis = paths.get("source_ovis")
    chapter_ovis: list[int] = []
    if source_ovis:
        chapter_ovis, ovi_problems = _read_ovis(source_ovis)
        problems.extend(ovi_problems)

    # 2. unfilmed_ovis
    omissions_path = paths.get("stage1_dir")
    approvals_path = paths.get("approvals")
    unfilmed_ovis: list[int] = []
    if omissions_path and approvals_path:
        omissions_file = omissions_path / "omissions_approved.json"
        unfilmed_ovis, om_problems = _read_omissions(omissions_file, approvals_path)
        problems.extend(om_problems)

    # 3. Voice library
    voice_lib_path = root_path / "canon" / "series" / "voices.json"
    saved_voices, series_voices, verified_voices, voice_problems = _read_voice_library(voice_lib_path)
    problems.extend(voice_problems)

    # 4. Preset IDs
    preset_index_path = root_path / "assets" / "v5_presets" / "index.json"
    preset_ids, preset_problems = _read_presets(preset_index_path)
    problems.extend(preset_problems)

    # 5. Sound IDs
    sound_palette_path = root_path / "canon" / "series" / "sounds" / "palette.json"
    sound_ids, sound_problems = _read_sound_palette(sound_palette_path)
    problems.extend(sound_problems)

    # Build base context
    ctx: dict = {
        "chapter_ovis": chapter_ovis,
        "unfilmed_ovis": unfilmed_ovis,
        "saved_voices": saved_voices,
        "series_voices": series_voices,
        "verified_voices": verified_voices,
        "preset_ids": preset_ids,
        "sound_ids": sound_ids,
        # Defaults for keys that come from Stage 1 documents
        "script_line_ids": [],
        "core_line_ids": [],
        "script_texts": [],
        "speaking_characters": [],
        "known_states": {},
    }

    # Apply extra overrides
    if isinstance(extra, dict):
        ctx.update(extra)

    return ctx, problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Stage 1 context for an Adhyay")
    parser.add_argument("--adhyay", type=int, required=True, help="Adhyay number (1..21)")
    parser.add_argument("--root", type=Path, default=_REPO_ROOT, help="Repository root")
    parser.add_argument("--out", type=Path, help="Output JSON file (default: stdout)")
    args = parser.parse_args(argv)

    ctx, problems = build_ctx(args.adhyay, args.root)

    # Output JSON
    json_str = json.dumps(ctx, ensure_ascii=False, indent=2, sort_keys=True)
    if args.out:
        if args.out.exists():
            print("refused: file exists", file=sys.stderr)
            return 2
        args.out.write_text(json_str, encoding="utf-8")
    else:
        print(json_str)

    # Print problems to stderr
    for prob in problems:
        print(f"problem: {prob}", file=sys.stderr)

    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

## CURRENT tests/test_stage1_context.py
```python
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import pytest

# Load the context module by path
TEST_DIR = Path(__file__).resolve().parent
REPO_ROOT = TEST_DIR.parent
CONTEXT_PATH = REPO_ROOT / "scripts" / "pipeline" / "stage1" / "context.py"

import importlib.util

spec = importlib.util.spec_from_file_location("context", CONTEXT_PATH)
assert spec is not None and spec.loader is not None
context_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(context_mod)

build_ctx = context_mod.build_ctx
main = context_mod.main


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def _write_jsonl(path: Path, lines: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for line in lines:
            f.write(json.dumps(line) + "\n")


def _setup_synthetic_root(tmp_path: Path, adhyay: int) -> Path:
    """Create a synthetic repo structure for the given adhyay under tmp_path."""
    root = tmp_path
    # Chapter paths follow chapter.py conventions: canon/adhyay_XX/
    adhyay_dir = root / "canon" / f"adhyay_{adhyay:02d}"
    source_dir = adhyay_dir / "source"
    stage1_dir = adhyay_dir / "stage1"

    # ovis.jsonl - only valid lines (duplicates allowed)
    _write_jsonl(source_dir / "ovis.jsonl", [
        {"ovi": 1, "text": "line 1"},
        {"ovi": 2, "text": "line 2"},
        {"ovi": 1, "text": "duplicate"},
        {"ovi": 3},
    ])

    # approvals.json (empty initially)
    _write_json(adhyay_dir / "approvals.json", {})

    # stage1 directory exists
    stage1_dir.mkdir(parents=True, exist_ok=True)

    # Voice library
    voice_lib = root / "canon" / "series" / "voices.json"
    _write_json(voice_lib, {
        "generated": "2024-01-01",
        "source": "test",
        "version": 1,
        "voices": [
            {
                "voice_key": "vk_gajanan",
                "voice_id": "vid_1",
                "assigned_to": ["gajanan_maharaj"],
                "marathi_verified": True,
                "hindi_verified": True,
                "status": "active",
                "description": "Gajanan Maharaj"
            },
            {
                "voice_key": "vk_unverified",
                "voice_id": "vid_2",
                "assigned_to": ["other_char"],
                "marathi_verified": False,
                "hindi_verified": True,
                "status": "active",
                "description": "Unverified"
            },
            {
                "voice_key": "vk_unassigned",
                "voice_id": "vid_3",
                "assigned_to": [],
                "marathi_verified": True,
                "hindi_verified": True,
                "status": "active",
                "description": "Unassigned"
            }
        ]
    })

    # Preset index
    preset_index = root / "assets" / "v5_presets" / "index.json"
    _write_json(preset_index, [
        {"preset": "01_establishing_shot"},
        {"preset": "02_close_up"}
    ])

    # No sound palette file

    return root


def test_happy_path(tmp_path: Path):
    root = _setup_synthetic_root(tmp_path, 2)
    ctx, problems = build_ctx(2, root)

    assert problems == []
    assert ctx["chapter_ovis"] == [1, 2, 3]
    assert ctx["preset_ids"] == ["01_establishing_shot", "02_close_up"]
    assert ctx["saved_voices"] == {
        "vk_gajanan": "vid_1",
        "vk_unverified": "vid_2",
        "vk_unassigned": "vid_3"
    }
    assert ctx["series_voices"] == {"gajanan_maharaj": "vk_gajanan", "other_char": "vk_unverified"}
    assert ctx["verified_voices"] == ["vk_gajanan", "vk_unassigned"]
    assert ctx["sound_ids"] == []
    assert ctx["unfilmed_ovis"] == []
    # Default script keys
    assert ctx["script_line_ids"] == []
    assert ctx["core_line_ids"] == []
    assert ctx["script_texts"] == []
    assert ctx["speaking_characters"] == []
    assert ctx["known_states"] == {}


def test_omissions_approved(tmp_path: Path):
    root = _setup_synthetic_root(tmp_path, 2)
    adhyay_dir = root / "canon" / "adhyay_02"
    stage1_dir = adhyay_dir / "stage1"
    approvals_file = adhyay_dir / "approvals.json"

    # Create omissions file with ovis [5, 6]
    omissions_file = stage1_dir / "omissions_approved.json"
    _write_json(omissions_file, {"adhyay": 2, "ovis": [5, 6]})

    # Compute its sha256 and put into approvals with correct structure
    sha = hashlib.sha256(omissions_file.read_bytes()).hexdigest()
    _write_json(approvals_file, {"stage1_omissions": {"sha256": sha, "owner": "test", "date": "2026-10-28"}})

    ctx, problems = build_ctx(2, root)
    assert ctx["unfilmed_ovis"] == [5, 6]
    assert problems == []


def test_omissions_draft(tmp_path: Path):
    root = _setup_synthetic_root(tmp_path, 2)
    adhyay_dir = root / "canon" / "adhyay_02"
    stage1_dir = adhyay_dir / "stage1"
    # approvals.json is empty (DRAFT)
    omissions_file = stage1_dir / "omissions_approved.json"
    _write_json(omissions_file, {"adhyay": 2, "ovis": [5, 6]})

    ctx, problems = build_ctx(2, root)
    assert ctx["unfilmed_ovis"] == []
    assert any("DRAFT" in p for p in problems)


def test_omissions_stale(tmp_path: Path):
    root = _setup_synthetic_root(tmp_path, 2)
    adhyay_dir = root / "canon" / "adhyay_02"
    stage1_dir = adhyay_dir / "stage1"
    approvals_file = adhyay_dir / "approvals.json"

    omissions_file = stage1_dir / "omissions_approved.json"
    _write_json(omissions_file, {"adhyay": 2, "ovis": [5, 6]})
    sha = hashlib.sha256(omissions_file.read_bytes()).hexdigest()
    _write_json(approvals_file, {"stage1_omissions": {"sha256": sha, "owner": "test", "date": "2026-10-28"}})

    # Now modify omissions file (make it stale)
    _write_json(omissions_file, {"adhyay": 2, "ovis": [7, 8]})

    ctx, problems = build_ctx(2, root)
    assert ctx["unfilmed_ovis"] == []
    assert any("STALE" in p for p in problems)


def test_omissions_absent(tmp_path: Path):
    root = _setup_synthetic_root(tmp_path, 2)
    # No omissions file
    ctx, problems = build_ctx(2, root)
    assert ctx["unfilmed_ovis"] == []
    assert not any(p.startswith("omissions:") for p in problems)


def test_missing_sources(tmp_path: Path):
    root = tmp_path
    # No ovis file, no voice library, no preset index
    adhyay_dir = root / "canon" / "adhyay_02"
    adhyay_dir.mkdir(parents=True)
    (adhyay_dir / "approvals.json").write_text("{}")
    (adhyay_dir / "stage1").mkdir(parents=True)

    ctx, problems = build_ctx(2, root)
    assert ctx["chapter_ovis"] == []
    assert ctx["saved_voices"] == {}
    assert ctx["series_voices"] == {}
    assert ctx["verified_voices"] == []
    assert ctx["preset_ids"] == []
    assert ctx["sound_ids"] == []
    assert "source_ovis: missing" in problems
    assert "voice_library: missing" in problems
    assert "presets: missing" in problems


def test_bad_jsonl_line(tmp_path: Path):
    root = tmp_path
    adhyay_dir = root / "canon" / "adhyay_02"
    source_dir = adhyay_dir / "source"
    source_dir.mkdir(parents=True)
    # Write a jsonl with a bad line (line 2) and a blank line (line 3) and a good line (line 4)
    _write_jsonl(source_dir / "ovis.jsonl", [
        {"ovi": 1},
        {"ovi": "not an int"},  # bad line 2
        {},  # missing ovi line 3
        {"ovi": 2},
    ])
    # approvals and stage1 dir
    (adhyay_dir / "approvals.json").write_text("{}")
    (adhyay_dir / "stage1").mkdir(parents=True)
    # voice library, preset index minimal
    voice_lib = root / "canon" / "series" / "voices.json"
    voice_lib.parent.mkdir(parents=True)
    _write_json(voice_lib, {"voices": []})
    preset_index = root / "assets" / "v5_presets" / "index.json"
    preset_index.parent.mkdir(parents=True)
    _write_json(preset_index, [])

    ctx, problems = build_ctx(2, root)
    assert any("source_ovis: bad line 2" in p for p in problems)
    assert any("source_ovis: bad line 3" in p for p in problems)
    assert ctx["chapter_ovis"] == [1, 2]


def test_character_assigned_to_two_voices(tmp_path: Path):
    root = _setup_synthetic_root(tmp_path, 2)
    # Modify voice library to assign same character to two voices
    voice_lib = root / "canon" / "series" / "voices.json"
    data = json.loads(voice_lib.read_text())
    data["voices"].append({
        "voice_key": "vk_duplicate",
        "voice_id": "vid_4",
        "assigned_to": ["gajanan_maharaj"],  # already assigned to vk_gajanan
        "marathi_verified": True,
        "hindi_verified": True,
        "status": "active",
        "description": "Duplicate"
    })
    _write_json(voice_lib, data)

    ctx, problems = build_ctx(2, root)
    assert any("voices: character gajanan_maharaj is assigned to more than one voice" in p for p in problems)
    # The first assignment should remain
    assert ctx["series_voices"]["gajanan_maharaj"] == "vk_gajanan"


def test_extra_overrides(tmp_path: Path):
    root = _setup_synthetic_root(tmp_path, 2)
    extra = {
        "script_texts": {"1": "hello"},
        "unfilmed_ovis": [99],  # override
        "new_key": "value"
    }
    ctx, problems = build_ctx(2, root, extra=extra)
    assert ctx["script_texts"] == {"1": "hello"}
    assert ctx["unfilmed_ovis"] == [99]
    assert ctx["new_key"] == "value"

    # Non-dict extra is ignored
    ctx2, _ = build_ctx(2, root, extra="not a dict")
    assert "new_key" not in ctx2


def test_invalid_adhyay(tmp_path: Path):
    root = _setup_synthetic_root(tmp_path, 2)
    for bad in [0, 22, True, "x", -1]:
        ctx, problems = build_ctx(bad, root)  # type: ignore
        assert ctx == {}
        assert problems == ["adhyay must be an int in 1..21"]


def test_generic_adhyay_3(tmp_path: Path):
    root = _setup_synthetic_root(tmp_path, 3)
    ctx, problems = build_ctx(3, root)
    assert problems == []
    assert ctx["chapter_ovis"] == [1, 2, 3]
    # All other keys should be populated similarly


def test_main_writes_json(tmp_path: Path, capsys: pytest.CaptureFixture):
    root = _setup_synthetic_root(tmp_path, 2)
    out_file = tmp_path / "ctx.json"

    # Test writing to file
    ret = main(["--adhyay", "2", "--root", str(root), "--out", str(out_file)])
    assert ret == 0
    assert out_file.exists()
    data = json.loads(out_file.read_text())
    assert data["chapter_ovis"] == [1, 2, 3]

    # Test refusing existing file
    ret = main(["--adhyay", "2", "--root", str(root), "--out", str(out_file)])
    assert ret == 2
    captured = capsys.readouterr()
    assert "refused: file exists" in captured.err

    # Test stdout output
    ret = main(["--adhyay", "2", "--root", str(root)])
    assert ret == 0
    captured = capsys.readouterr()
    assert "chapter_ovis" in captured.out

    # Test problems printed to stderr and return 1
    # Create a root with missing voice library to generate a problem
    bad_root = tmp_path / "bad"
    bad_root.mkdir()
    (bad_root / "canon" / "adhyay_02" / "source").mkdir(parents=True)
    (bad_root / "canon" / "adhyay_02" / "approvals.json").write_text("{}")
    (bad_root / "canon" / "adhyay_02" / "stage1").mkdir(parents=True)
    _write_jsonl(bad_root / "canon" / "adhyay_02" / "source" / "ovis.jsonl", [{"ovi": 1}])
    # No voice library, no preset index
    ret = main(["--adhyay", "2", "--root", str(bad_root)])
    assert ret == 1
    captured = capsys.readouterr()
    assert "problem: voice_library: missing" in captured.err
    assert "problem: presets: missing" in captured.err


@pytest.mark.skipif(
    not (REPO_ROOT / "canon" / "series" / "voices.json").exists(),
    reason="Real repo voices.json not found"
)
@pytest.mark.skipif(
    not (REPO_ROOT / "assets" / "v5_presets" / "index.json").exists(),
    reason="Real repo preset index not found"
)
def test_real_repo():
    """Test against the real repository (Adhyay 1)."""
    ctx, problems = build_ctx(1, REPO_ROOT)
    # Real voice library has 35 entries
    assert len(ctx["saved_voices"]) == 35
    # verified_voices only those with both flags True
    # We can't know exact count, but ensure it's a subset of saved_voices keys
    assert all(vk in ctx["saved_voices"] for vk in ctx["verified_voices"])
    # series_voices entries <= total assigned characters in file
    # Load the real file to check
    with open(REPO_ROOT / "canon" / "series" / "voices.json", "r", encoding="utf-8") as f:
        real_data = json.load(f)
    assigned_chars = set()
    for voice in real_data.get("voices", []):
        for char in voice.get("assigned_to", []):
            assigned_chars.add(char)
    assert len(ctx["series_voices"]) <= len(assigned_chars)
    # preset_ids contains "01_establishing_shot"
    assert "01_establishing_shot" in ctx["preset_ids"]

    # Now test that aggregate.validate_all accepts this ctx
    # Load aggregate module by path (correct path is stage1/aggregate.py)
    AGGREGATE_PATH = REPO_ROOT / "scripts" / "pipeline" / "stage1" / "aggregate.py"
    aggregate_spec = importlib.util.spec_from_file_location("aggregate", AGGREGATE_PATH)
    assert aggregate_spec is not None and aggregate_spec.loader is not None
    aggregate_mod = importlib.util.module_from_spec(aggregate_spec)
    aggregate_spec.loader.exec_module(aggregate_mod)
    validate_all = aggregate_mod.validate_all

    # Call with empty docs
    result = validate_all(1, {}, ctx)
    assert isinstance(result, list)
```
