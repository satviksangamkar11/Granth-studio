# FIX CALL: return BOTH files in full: `scripts/pipeline/stage1/aggregate.py` and `tests/test_stage1_aggregate.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
...............................                                          [100%]
31 passed in 0.19s

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
    # Remove punctuation: .,;:!?।॥"'()-
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

    # X1: story_map - STORY ovis in story events, TEACHING ovis in discourse events
    if all_valid("story_map"):
        try:
            sm = unit_docs["story_map"]
            ovi_types = sm.get("ovi_types", [])
            events = sm.get("events", [])
            story_ranges = []
            discourse_ranges = []
            for e in events:
                rng = e.get("ovi_range")
                kind = e.get("kind")
                if isinstance(rng, list) and len(rng) == 2 and _is_int(rng[0]) and _is_int(rng[1]):
                    if kind == "story":
                        story_ranges.append((rng[0], rng[1]))
                    elif kind == "discourse":
                        discourse_ranges.append((rng[0], rng[1]))
            for ot in ovi_types:
                ovi = ot.get("ovi")
                typ = ot.get("type")
                if not _is_int(ovi):
                    continue
                if typ == "STORY":
                    found = any(_in_range(ovi, lo, hi) for lo, hi in story_ranges)
                    if not found:
                        errors.append(f"story_map: ovi {ovi} is typed STORY but is in no story event")
                elif typ == "TEACHING":
                    found = any(_in_range(ovi, lo, hi) for lo, hi in discourse_ranges)
                    if not found:
                        errors.append(f"story_map: ovi {ovi} is typed TEACHING but is in no discourse event")
        except Exception:
            errors.append("aggregate: internal error in X1")

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


def test_propose_omission_story_ovi_no_error():
    """A STORY ovi with PROPOSE_OMISSION that IS in unfilmed_ovis produces no X2 error (X2 removed) and no X3 error."""
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
    # No error about omission being proposed (X2 removed)
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

    rc = agg.main(["--adhyay", "1", "--docs-dir", str(docs_dir), "--ctx", str(ctx_file)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "0 error(s)" in out

    bad_docs = copy.deepcopy(BASE_DOCS)
    bad_docs["story_map"]["ovi_types"] = [{"ovi": 999, "type": "STORY"}]
    bad_docs["story_map"]["events"] = []
    (docs_dir / "story_map.json").write_text(json.dumps(bad_docs["story_map"]), encoding="utf-8")
    rc = agg.main(["--adhyay", "1", "--docs-dir", str(docs_dir), "--ctx", str(ctx_file)])
    assert rc == 1
    out = capsys.readouterr().out
    assert "error(s)" in out

    (docs_dir / "coverage.json").write_text("not json", encoding="utf-8")
    rc = agg.main(["--adhyay", "1", "--docs-dir", str(docs_dir), "--ctx", str(ctx_file)])
    assert rc == 2
    out = capsys.readouterr().out
    assert "refused:" in out

    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()
    (schema_dir / "stage1_story_map.schema.json").write_text("{}", encoding="utf-8")
    rc = agg.main(["--adhyay", "1", "--docs-dir", str(docs_dir), "--export-schemas", str(schema_dir)])
    assert rc == 2
    out = capsys.readouterr().out
    assert "refused:" in out

```

## ROUND 3 CHANGES to aggregate.py (Codex code review + three intent reviews). Return BOTH complete FILE blocks. Keep it simple: plain functions. Tests: copy.deepcopy + plain assignment, never a no-effect-rejecting helper, remember True == 1. Keep every existing test and the ctx-type robustness (no raise, no 'internal error' sentinel for wrong-typed ctx).
1. main(): after `--export-schemas DIR` succeeded, CONTINUE: validate the documents, print the errors and the `N error(s)` line, and return 0/1 as without export (export only adds files). If the export is refused (file exists) keep returning 2 with `refused: ...`. Test: export plus a document with an error returns 1 and prints the count; export plus valid documents returns 0.
2. NEW rule X10 `story_map` + `scenes`: for each scene, collect the events whose ovi_range overlaps the scene ovi_range (lo1 <= hi2 and lo2 <= hi1, no enumeration). If at least one event overlaps and NONE of them has kind equal to the scene section_kind, add `scenes: scene <scene_id> is <section_kind> but its events are not <section_kind>`. Scenes with no overlapping event are not reported here (X5 and the units handle those). Tests: the valid base is clean; change event E1 kind to discourse (scene S1 stays story) -> the message names S1; a scene overlapping two events of which one matches is clean.
3. Extend X7 (series voices): for a cast entry with status NEW_PROPOSED (a character NOT a key of series_voices) whose voice_key equals a value of series_voices, add `voices: character <character_id> reuses the series voice <voice_key>`. Test: ctx series_voices {"gajanan_maharaj": "gajanan"}; a NEW_PROPOSED character with voice_key "gajanan" errors; with another key it does not. (Keep this isolated from the existing X7 messages.)
4. NEW rule X11 `voices` + ctx `verified_voices`: ctx `verified_voices` is OPTIONAL, a list of voice_key strings verified for BOTH Marathi and Hindi (from the voice library). Only when it is a list (even an empty one) apply the rule: every cast entry voice_key must be in it, else `voices: voice <voice_key> is not verified for Marathi and Hindi`. When the key is absent or not a list the rule is skipped. Tests: absent -> clean; present with all base voice keys -> clean; present without one of the keys -> that message names the key; wrong types (None, 5, 'x', [[1]]) -> no exception and no 'internal error'.
5. Docs: do NOT touch docs here (the spec file is updated separately).
