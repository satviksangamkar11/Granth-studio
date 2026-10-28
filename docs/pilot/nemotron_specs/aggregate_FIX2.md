# FIX CALL: return BOTH files in full: `scripts/pipeline/stage1/aggregate.py` and `tests/test_stage1_aggregate.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
.F.....FF.FF.....FF.F                                                    [100%]
================================== FAILURES ===================================
_____________________ test_x1_story_ovi_not_in_any_event ______________________
tests\test_stage1_aggregate.py:41: in test_x1_story_ovi_not_in_any_event
    assert errs2 == []
E   AssertionError: assert ['ovi 1 is un...untyped', ...] == []
E     
E     Left contains 7 more items, first extra item: 'ovi 1 is untyped'
E     Use -v to get more diff
______________________ test_x4_non_omitted_not_in_scene _______________________
tests\test_stage1_aggregate.py:150: in test_x4_non_omitted_not_in_scene
    assert errs2 == []
E   AssertionError: assert ['S1: turn ov...y scene', ...] == []
E     
E     Left contains 25 more items, first extra item: 'S1: turn ovi outside range'
E     Use -v to get more diff
________________________ test_x5_key_ovi_not_in_scene _________________________
tests\test_stage1_aggregate.py:165: in test_x5_key_ovi_not_in_scene
    assert errs2 == []
E   AssertionError: assert ['E1: key_ovi...9, 999]', ...] == []
E     
E     Left contains 7 more items, first extra item: 'E1: key_ovi 999 outside ovi_range'
E     Use -v to get more diff
______________________ test_x7_recurring_voice_mismatch _______________________
tests\test_stage1_aggregate.py:204: in test_x7_recurring_voice_mismatch
    assert errs2 == []
E   AssertionError: assert ['gajanan_mah...e saved cast'] == []
E     
E     Left contains one more item: 'gajanan_maharaj: voice not in the saved cast'
E     Use -v to get more diff
____________________ test_x7_new_proposed_for_series_char _____________________
tests\test_stage1_aggregate.py:224: in test_x7_new_proposed_for_series_char
    assert errs2 == []
E   AssertionError: assert ['gajanan_mah...e saved cast'] == []
E     
E     Left contains one more item: 'gajanan_maharaj: voice not in the saved cast'
E     Use -v to get more diff
___________ test_robustness_schema_failure_skips_validate_and_cross ___________
tests\test_stage1_aggregate.py:277: in test_robustness_schema_failure_skips_validate_and_cross
    assert any(e.startswith("story_map:") for e in errs)
E   assert False
E    +  where False = any(<generator object test_robustness_schema_failure_skips_validate_and_cross.<locals>.<genexpr> at 0x00000246EB45BE00>)
_________________________ test_robustness_huge_ranges _________________________
tests\test_stage1_aggregate.py:293: in test_robustness_huge_ranges
    assert errs == []
E   AssertionError: assert ['S1: ovi_ran...chapter ovis'] == []
E     
E     Left contains 3 more items, first extra item: 'S1: ovi_range overlaps with S2'
E     Use -v to get more diff
____________________________ test_main_exit_codes _____________________________
tests\test_stage1_aggregate.py:346: in test_main_exit_codes
    assert "refused:" in out
E   AssertionError: assert 'refused:' in ''
=========================== short test summary info ===========================
FAILED tests/test_stage1_aggregate.py::test_x1_story_ovi_not_in_any_event - A...
FAILED tests/test_stage1_aggregate.py::test_x4_non_omitted_not_in_scene - Ass...
FAILED tests/test_stage1_aggregate.py::test_x5_key_ovi_not_in_scene - Asserti...
FAILED tests/test_stage1_aggregate.py::test_x7_recurring_voice_mismatch - Ass...
FAILED tests/test_stage1_aggregate.py::test_x7_new_proposed_for_series_char
FAILED tests/test_stage1_aggregate.py::test_robustness_schema_failure_skips_validate_and_cross
FAILED tests/test_stage1_aggregate.py::test_robustness_huge_ranges - Assertio...
FAILED tests/test_stage1_aggregate.py::test_main_exit_codes - AssertionError:...
8 failed, 13 passed in 0.31s

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


## CURRENT MODULE scripts/pipeline/stage1/aggregate.py
```python
from __future__ import annotations

import importlib.util
import json
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

    # X1: story_map - every STORY/TEACHING ovi must be in at least one event's ovi_range
    if all_valid("story_map"):
        sm = unit_docs["story_map"]
        ovi_types = sm.get("ovi_types", [])
        events = sm.get("events", [])
        event_ranges = [(e.get("ovi_range", [0, -1])[0], e.get("ovi_range", [0, -1])[1]) for e in events if isinstance(e.get("ovi_range"), list) and len(e.get("ovi_range")) == 2]
        for ot in ovi_types:
            ovi = ot.get("ovi")
            typ = ot.get("type")
            if not _is_int(ovi) or typ not in ("STORY", "TEACHING"):
                continue
            found = any(_in_range(ovi, lo, hi) for lo, hi in event_ranges)
            if not found:
                errors.append(f"story_map: ovi {ovi} is typed {typ} but is in no event")

    # X2: coverage + story_map - STORY/TEACHING ovi must not have PROPOSE_OMISSION
    if all_valid("coverage", "story_map"):
        cov = unit_docs["coverage"]
        sm = unit_docs["story_map"]
        story_teaching_ovis = {ot.get("ovi") for ot in sm.get("ovi_types", []) if _is_int(ot.get("ovi")) and ot.get("type") in ("STORY", "TEACHING")}
        for c in cov.get("ovis", []):
            ovi = c.get("ovi")
            disp = c.get("disposition")
            if _is_int(ovi) and ovi in story_teaching_ovis and disp == "PROPOSE_OMISSION":
                errors.append(f"coverage: ovi {ovi} is {sm.get('ovi_types', [{}])[0].get('type', 'STORY')} but an omission is proposed")

    # X3: coverage + ctx.unfilmed_ovis
    if all_valid("coverage"):
        cov = unit_docs["coverage"]
        unfilmed = set(ctx.get("unfilmed_ovis", []))
        proposed = {c.get("ovi") for c in cov.get("ovis", []) if c.get("disposition") == "PROPOSE_OMISSION" and _is_int(c.get("ovi"))}
        for ovi in proposed:
            if ovi not in unfilmed:
                errors.append(f"coverage: ovi {ovi} omission is not approved by the owner")
        for ovi in unfilmed:
            if ovi not in proposed:
                errors.append(f"coverage: ovi {ovi} is approved as unfilmed but has no omission proposal")

    # X4: coverage + shots + scenes
    if all_valid("coverage", "shots", "scenes"):
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

    # X5: story_map + scenes - key ovis of events must be in some scene
    if all_valid("story_map", "scenes"):
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

    # X6: story_map + questions + scenes - ambiguous events need questions on overlapping scenes
    if all_valid("story_map", "questions", "scenes"):
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

    # X7: voices + ctx.series_voices
    if all_valid("voices"):
        voices = unit_docs["voices"]
        series_voices = ctx.get("series_voices", {})
        for cast in voices.get("cast", []):
            char_id = cast.get("character_id")
            status = cast.get("status")
            voice_key = cast.get("voice_key")
            if not isinstance(char_id, str) or char_id not in series_voices:
                continue
            series_key = series_voices[char_id]
            if status == "RECURRING" and voice_key != series_key:
                errors.append(f"voices: recurring character {char_id} has a different voice than the series")
            elif status == "NEW_PROPOSED":
                errors.append(f"voices: character {char_id} already has a series voice")

    # X8: script text guard
    if all_valid(*UNITS):
        script_texts = ctx.get("script_texts", [])
        long_scripts = [_normalize(t) for t in script_texts if isinstance(t, str) and len(_normalize(t)) >= 20]
        if long_scripts:
            for unit in UNITS:
                doc = unit_docs.get(unit)
                if doc is None:
                    continue
                for path, val in _walk_strings(doc):
                    norm_val = _normalize(val)
                    for script in long_scripts:
                        if script in norm_val:
                            errors.append(f"{unit}: free text copies script wording ({path})")
                            break

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
                print(f"refused: cannot read {path}: {e}", file=sys.stderr)
                return 2

    ctx: dict[str, Any] = {}
    if args.ctx and args.ctx.exists():
        try:
            ctx = json.loads(args.ctx.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"refused: cannot read {args.ctx}: {e}", file=sys.stderr)
            return 2

    if args.export_schemas:
        try:
            export_schemas(args.export_schemas)
        except FileExistsError as e:
            print(f"refused: {e}", file=sys.stderr)
            return 2
        except Exception as e:
            print(f"refused: {e}", file=sys.stderr)
            return 2
        return 0

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


def test_base_valid():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    errs = agg.validate_all(1, docs, ctx)
    assert errs == []


def test_x1_story_ovi_not_in_any_event():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Make ovi 3 STORY but events only cover [4,5]
    docs["story_map"]["ovi_types"] = [{"ovi": 3, "type": "STORY"}, {"ovi": 4, "type": "STORY"}]
    docs["story_map"]["events"] = [{"event_id": "E1", "kind": "story", "title": "t", "ovi_range": [4, 5], "key_ovis": [4], "closure": "RESOLVED_IN_ADHYAY"}]
    errs = agg.validate_all(1, docs, ctx)
    assert any("story_map: ovi 3 is typed STORY but is in no event" in e for e in errs)
    # Corrected twin
    docs["story_map"]["events"][0]["ovi_range"] = [3, 5]
    errs2 = agg.validate_all(1, docs, ctx)
    assert errs2 == []


def test_x1_empty_events():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    docs["story_map"]["ovi_types"] = [{"ovi": 1, "type": "STORY"}, {"ovi": 2, "type": "TEACHING"}]
    docs["story_map"]["events"] = []
    errs = agg.validate_all(1, docs, ctx)
    assert any("story_map: ovi 1 is typed STORY but is in no event" in e for e in errs)
    assert any("story_map: ovi 2 is typed TEACHING but is in no event" in e for e in errs)


def test_x2_story_ovi_propose_omission():
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
    # (base already has it in scene/shot presumably)
    errs = agg.validate_all(1, docs, ctx)
    assert any(f"coverage: ovi {story_ovi} is STORY but an omission is proposed" in e for e in errs)
    # Corrected twin
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] == story_ovi:
            c["disposition"] = "VISUALISED"
            break
    ctx["unfilmed_ovis"] = []
    errs2 = agg.validate_all(1, docs, ctx)
    assert errs2 == []


def test_x3_proposed_not_in_unfilmed():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Pick an ovi, set PROPOSE_OMISSION but don't add to unfilmed
    ovi = docs["coverage"]["ovis"][0]["ovi"]
    docs["coverage"]["ovis"][0]["disposition"] = "PROPOSE_OMISSION"
    docs["coverage"]["ovis"][0]["reason"] = "test"
    ctx["unfilmed_ovis"] = []
    errs = agg.validate_all(1, docs, ctx)
    assert any(f"coverage: ovi {ovi} omission is not approved by the owner" in e for e in errs)


def test_x3_unfilmed_without_proposal():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Add an ovi to unfilmed that has no PROPOSE_OMISSION
    ovi = 999
    ctx["unfilmed_ovis"] = [ovi]
    # Ensure no coverage entry has PROPOSE_OMISSION for 999
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] == ovi:
            c["disposition"] = "VISUALISED"
    errs = agg.validate_all(1, docs, ctx)
    assert any(f"coverage: ovi {ovi} is approved as unfilmed but has no omission proposal" in e for e in errs)


def test_x4_visualised_not_in_shot():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Pick an ovi, set VISUALISED but remove from all shots
    ovi = docs["coverage"]["ovis"][0]["ovi"]
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] == ovi:
            c["disposition"] = "VISUALISED"
            break
    # Remove ovi from all shots
    for sh in docs["shots"]["shots"]:
        if ovi in sh.get("ovi_ids", []):
            sh["ovi_ids"] = [x for x in sh["ovi_ids"] if x != ovi]
    errs = agg.validate_all(1, docs, ctx)
    assert any(f"coverage: ovi {ovi} is VISUALISED but is in no shot" in e for e in errs)
    # Corrected twin
    docs["shots"]["shots"][0]["ovi_ids"].append(ovi)
    errs2 = agg.validate_all(1, docs, ctx)
    assert errs2 == []


def test_x4_non_omitted_not_in_scene():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Pick an ovi that's not PROPOSE_OMISSION, remove from all scene ranges
    ovi = docs["coverage"]["ovis"][0]["ovi"]
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] == ovi:
            c["disposition"] = "NARRATED"
            break
    # Make all scene ranges not cover this ovi
    for sc in docs["scenes"]["scenes"]:
        sc["ovi_range"] = [100, 200]
    errs = agg.validate_all(1, docs, ctx)
    assert any(f"coverage: ovi {ovi} is in no scene" in e for e in errs)
    # Corrected twin
    docs["scenes"]["scenes"][0]["ovi_range"] = [ovi, ovi]
    errs2 = agg.validate_all(1, docs, ctx)
    assert errs2 == []


def test_x5_key_ovi_not_in_scene():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Set event key_ovi to 999, make scenes not cover it
    docs["story_map"]["events"][0]["key_ovis"] = [999]
    for sc in docs["scenes"]["scenes"]:
        sc["ovi_range"] = [1, 10]
    errs = agg.validate_all(1, docs, ctx)
    assert any("story_map: key ovi 999 of event" in e and "is in no scene" in e for e in errs)
    # Corrected twin
    docs["scenes"]["scenes"][0]["ovi_range"] = [999, 999]
    errs2 = agg.validate_all(1, docs, ctx)
    assert errs2 == []


def test_x6_ambiguous_event_no_question():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Set event E2 closure to SOURCE_INCOMPLETE_OR_AMBIGUOUS, remove questions on S2
    for ev in docs["story_map"]["events"]:
        if ev["event_id"] == "E2":
            ev["closure"] = "SOURCE_INCOMPLETE_OR_AMBIGUOUS"
            break
    # Remove questions on S2
    docs["questions"]["questions"] = [q for q in docs["questions"]["questions"] if q.get("scene_id") != "S2"]
    errs = agg.validate_all(1, docs, ctx)
    assert any("story_map: ambiguous event E2 has no question" in e for e in errs)
    # Corrected twin: add question on S2
    docs["questions"]["questions"].append({"id": "Q99", "text": "test", "scene_id": "S2"})
    errs2 = agg.validate_all(1, docs, ctx)
    assert errs2 == []


def test_x7_recurring_voice_mismatch():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    ctx["series_voices"] = {"gajanan_maharaj": "other_key"}
    # Ensure cast has gajanan_maharaj as RECURRING with different key
    for cast in docs["voices"]["cast"]:
        if cast["character_id"] == "gajanan_maharaj":
            cast["status"] = "RECURRING"
            cast["voice_key"] = "different_key"
            break
    errs = agg.validate_all(1, docs, ctx)
    assert any("voices: recurring character gajanan_maharaj has a different voice than the series" in e for e in errs)
    # Corrected twin: matching key
    for cast in docs["voices"]["cast"]:
        if cast["character_id"] == "gajanan_maharaj":
            cast["voice_key"] = "other_key"
            break
    errs2 = agg.validate_all(1, docs, ctx)
    assert errs2 == []


def test_x7_new_proposed_for_series_char():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    ctx["series_voices"] = {"gajanan_maharaj": "some_key"}
    for cast in docs["voices"]["cast"]:
        if cast["character_id"] == "gajanan_maharaj":
            cast["status"] = "NEW_PROPOSED"
            break
    errs = agg.validate_all(1, docs, ctx)
    assert any("voices: character gajanan_maharaj already has a series voice" in e for e in errs)
    # Corrected twin: change to RECURRING with matching key
    for cast in docs["voices"]["cast"]:
        if cast["character_id"] == "gajanan_maharaj":
            cast["status"] = "RECURRING"
            cast["voice_key"] = "some_key"
            break
    errs2 = agg.validate_all(1, docs, ctx)
    assert errs2 == []


def test_x8_script_text_copied():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    script_line = "This is a long enough script line for testing purposes"
    ctx["script_texts"] = [script_line]
    # Copy into scenes[0].goal
    docs["scenes"]["scenes"][0]["goal"] = script_line
    errs = agg.validate_all(1, docs, ctx)
    assert any("scenes: free text copies script wording (scenes/0/goal)" in e for e in errs)
    # Short text should not trigger
    docs["scenes"]["scenes"][0]["goal"] = "Short"
    ctx["script_texts"] = ["Short"]
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any("free text copies script wording" in e for e in errs2)


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
    # Should still validate base
    assert not any("internal error" in e for e in errs)


def test_robustness_doc_is_list():
    docs = copy.deepcopy(BASE_DOCS)
    docs["story_map"] = []
    errs = agg.validate_all(1, docs, {})
    assert any("story_map: document missing" in e for e in errs)
    # Other units should still be checked
    assert not any("internal error" in e for e in errs)


def test_robustness_schema_failure_skips_validate_and_cross():
    docs = copy.deepcopy(BASE_DOCS)
    # Break story_map schema by removing required field (assuming ovi_types is required)
    docs["story_map"] = {"events": []}
    errs = agg.validate_all(1, docs, {})
    # Should have schema errors for story_map
    assert any(e.startswith("story_map:") for e in errs)
    # Should not have internal error from validate
    assert not any("internal error in story_map.validate" in e for e in errs)
    # Cross rules needing story_map should be skipped silently


def test_robustness_huge_ranges():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Set huge ranges
    for sc in docs["scenes"]["scenes"]:
        sc["ovi_range"] = [1, 10**12]
    for ev in docs["story_map"]["events"]:
        ev["ovi_range"] = [1, 10**12]
    errs = agg.validate_all(1, docs, ctx)
    # Should complete quickly (no timeout) and base should still be valid
    assert errs == []


def test_export_schemas(tmp_path):
    out_dir = tmp_path / "schemas"
    paths = agg.export_schemas(out_dir)
    assert len(paths) == 9
    for p in paths:
        assert p.exists()
        content = p.read_text(encoding="utf-8")
        assert content.endswith("\n")
        json.loads(content)  # valid JSON
    # Second call should raise FileExistsError
    try:
        agg.export_schemas(out_dir)
        assert False, "expected FileExistsError"
    except FileExistsError:
        pass
    # Files unchanged
    for p in paths:
        assert p.exists()


def test_main_exit_codes(tmp_path, capsys):
    # Create minimal valid docs
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    for unit in agg.UNITS:
        (docs_dir / f"{unit}.json").write_text(json.dumps(BASE_DOCS[unit]), encoding="utf-8")
    ctx_file = tmp_path / "ctx.json"
    ctx_file.write_text(json.dumps(BASE_CTX), encoding="utf-8")

    # Exit 0: valid
    rc = agg.main(["--adhyay", "1", "--docs-dir", str(docs_dir), "--ctx", str(ctx_file)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "0 error(s)" in out

    # Exit 1: invalid (break X1)
    bad_docs = copy.deepcopy(BASE_DOCS)
    bad_docs["story_map"]["ovi_types"] = [{"ovi": 999, "type": "STORY"}]
    bad_docs["story_map"]["events"] = []
    (docs_dir / "story_map.json").write_text(json.dumps(bad_docs["story_map"]), encoding="utf-8")
    rc = agg.main(["--adhyay", "1", "--docs-dir", str(docs_dir), "--ctx", str(ctx_file)])
    assert rc == 1
    out = capsys.readouterr().out
    assert "1 error(s)" in out or "error(s)" in out

    # Exit 2: unreadable JSON
    (docs_dir / "coverage.json").write_text("not json", encoding="utf-8")
    rc = agg.main(["--adhyay", "1", "--docs-dir", str(docs_dir), "--ctx", str(ctx_file)])
    assert rc == 2
    out = capsys.readouterr().out
    assert "refused:" in out

    # Exit 2: export-schemas with existing file
    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()
    (schema_dir / "stage1_story_map.schema.json").write_text("{}", encoding="utf-8")
    rc = agg.main(["--adhyay", "1", "--docs-dir", str(docs_dir), "--export-schemas", str(schema_dir)])
    assert rc == 2
    out = capsys.readouterr().out
    assert "refused:" in out

```

## NOTE: 8 tests fail (pytest output above). For each failing test decide from the SPEC whether the test case or the module is wrong and fix that side. Typical causes to check first: (a) a mutation that also violates ANOTHER rule so the asserted message is absent or extra errors appear; (b) a rule that must run only when all its documents are schema-valid but is skipped (or runs when it should not); (c) main() printing nothing for the `refused:` case (print to stdout, not stderr); (d) huge ranges must not be enumerated anywhere in the module. Do not weaken tests; keep the base-valid test and the clean-twin assertions. Return BOTH complete FILE blocks.
