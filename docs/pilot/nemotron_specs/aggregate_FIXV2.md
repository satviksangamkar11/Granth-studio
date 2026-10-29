# TASK: return ONLY ONE FILE: scripts/pipeline/stage1/aggregate.py (complete). Reply with exactly one block `FILE: scripts/pipeline/stage1/aggregate.py` then the python fenced. ADD ONE rule and change NOTHING ELSE.
The current file is correct: X1 is kind-aware, rule X2 does NOT exist and must NOT come back, X3-X11 stay exactly as they are, wrong-typed ctx never raises and never shows the 'internal error' sentinel, `main --export-schemas` exports AND validates. The AUTHORITATIVE spec is the AMENDMENTS section at the END of `docs/pilot/nemotron_specs/aggregate.md`; do not re-derive anything from older text.

## New rule X12 (checklist V2): voices + optional ctx `voice_genders`
`voice_genders` is a dict voice_key -> 'male' or 'female' (built from the voice library). Apply the rule only when it is a dict. For every cast entry whose `voice_key` is a key of voice_genders, whose cast `gender` is 'male' or 'female', and whose library gender is 'male' or 'female': if they differ add the error `voices: <character_id> is <cast gender> but voice <voice_key> is <library gender>`. Entries with an unknown key, a non-string gender or any other value are skipped. A ctx value that is not a dict means the rule is skipped (it never raises and never shows 'internal error'). Wrap it in the same last-resort guard as the other rules (`aggregate: internal error in X12`). Read `voice_genders` through the same safe-ctx helper style as `series_voices` (str keys and str values only). The rule runs only when the voices document is present and schema-valid, like the other voice rules.

## CURRENT scripts/pipeline/stage1/aggregate.py
```python
from __future__ import annotations

import importlib.util
import json
import sys
import unicodedata
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


def _get_int_list(ctx: dict, key: str) -> list[int]:
    val = ctx.get(key)
    if not isinstance(val, list):
        return []
    result = []
    for item in val:
        if _is_int(item):
            result.append(item)
    return result


def _get_str_list(ctx: dict, key: str) -> list[str]:
    val = ctx.get(key)
    if not isinstance(val, list):
        return []
    return [item for item in val if isinstance(item, str)]


def _get_dict(ctx: dict, key: str) -> dict:
    val = ctx.get(key)
    if isinstance(val, dict):
        return val
    return {}


def _get_str_dict(ctx: dict, key: str) -> dict[str, str]:
    """Extract a dict from ctx[key] keeping only entries with str keys and str values."""
    val = ctx.get(key)
    if not isinstance(val, dict):
        return {}
    result: dict[str, str] = {}
    for k, v in val.items():
        if isinstance(k, str) and isinstance(v, str):
            result[k] = v
    return result


def _normalize_words(text: str) -> list[str]:
    """Normalize text: split on whitespace, casefold, strip leading/trailing punctuation/symbols from each token."""
    tokens = text.split()
    out: list[str] = []
    for tok in tokens:
        tok = tok.casefold()
        # strip leading punctuation/symbols
        while tok and unicodedata.category(tok[0])[0] in ("P", "S"):
            tok = tok[1:]
        # strip trailing punctuation/symbols
        while tok and unicodedata.category(tok[-1])[0] in ("P", "S"):
            tok = tok[:-1]
        if tok:
            out.append(tok)
    return out


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
            series_voices = _get_str_dict(ctx, "series_voices")
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
