from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# Type aliases
Caller = Callable[[str, str, str], Tuple[str, Dict[str, Any]]]

# ----------------------------------------------------------------------
# Helper: load a module by file path
# ----------------------------------------------------------------------
def _load_module_by_path(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module {module_name} from {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# ----------------------------------------------------------------------
# Scrubbing helper
# ----------------------------------------------------------------------
def _scrub_text(text: str, keys: List[str]) -> str:
    for k in keys:
        if k and k in text:
            text = text.replace(k, "[REDACTED]")
    return text

def _scrub_dict(obj: Any, keys: List[str]) -> Any:
    if isinstance(obj, str):
        return _scrub_text(obj, keys)
    if isinstance(obj, dict):
        return {k: _scrub_dict(v, keys) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_scrub_dict(v, keys) for v in obj]
    return obj

# ----------------------------------------------------------------------
# Bracket completion helper
# ----------------------------------------------------------------------
def close_missing_brackets(text: str) -> Tuple[str, int]:
    """Scan text once, tracking strings and backslash escapes.
    Collect stack of unmatched '{' and '['. If not in a string at end and
    1-4 unmatched openers remain, append matching closers in reverse order.
    Returns (possibly extended text, number of closers added)."""
    in_string = False
    escape = False
    stack: List[str] = []
    for ch in text:
        if in_string:
            if escape:
                escape = False
            elif ch == '\\':
                escape = True
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch == '{' or ch == '[':
                stack.append(ch)
            elif ch == '}':
                if stack and stack[-1] == '{':
                    stack.pop()
            elif ch == ']':
                if stack and stack[-1] == '[':
                    stack.pop()
    if in_string:
        return text, 0
    if not (1 <= len(stack) <= 4):
        return text, 0
    closers = []
    for opener in reversed(stack):
        if opener == '{':
            closers.append('}')
        elif opener == '[':
            closers.append(']')
    extended = text + ''.join(closers)
    return extended, len(closers)

# ----------------------------------------------------------------------
# parse_reply
# ----------------------------------------------------------------------
def parse_reply(text: str, expected_keys: Tuple[str, ...], adhyay: int) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    problems: List[str] = []
    stripped = text.strip()
    # First try to parse the whole text as JSON
    try:
        obj = json.loads(stripped)
    except json.JSONDecodeError:
        obj = None
    if obj is not None:
        if not isinstance(obj, dict):
            problems.append("reply: not an object")
            return None, problems
        # It's a dict, use it
    else:
        # Extract from first { to last }
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end < start:
            problems.append("reply: no json object")
            return None, problems
        json_text = text[start:end+1]
        try:
            obj = json.loads(json_text)
        except json.JSONDecodeError:
            # Try conservative bracket completion once
            extended_text, added = close_missing_brackets(json_text)
            if added > 0:
                try:
                    obj = json.loads(extended_text)
                except json.JSONDecodeError:
                    obj = None
            if obj is None:
                problems.append("reply: bad json")
                return None, problems
        if not isinstance(obj, dict):
            problems.append("reply: not an object")
            return None, problems

    # Unwrapped document handling: if exactly one key expected, that key is absent,
    # and the object has an 'adhyay' key, treat the whole object as that document.
    if len(expected_keys) == 1:
        expected_key = expected_keys[0]
        if expected_key not in obj and "adhyay" in obj:
            # Wrap the object
            obj = {expected_key: obj}
            # Do not add a problem; silently wrap per spec

    # Check keys
    for k in expected_keys:
        if k not in obj:
            problems.append(f"reply: missing key {k}")
    for k in obj.keys():
        if k not in expected_keys:
            problems.append(f"reply: unexpected key {k}")
    # Fix adhyay in nested dicts: always set to the run's chapter number,
    # but record mismatch if the model supplied a different value.
    for k in expected_keys:
        if k in obj and isinstance(obj[k], dict):
            if "adhyay" in obj[k] and obj[k]["adhyay"] != adhyay:
                problems.append(f"{k}: adhyay {obj[k]['adhyay']} is not {adhyay}")
            obj[k]["adhyay"] = adhyay
    return obj, problems

# ----------------------------------------------------------------------
# merge_scene_parts
# ----------------------------------------------------------------------
def merge_scene_parts(adhyay: int, parts: List[Dict[str, Any]]) -> Dict[str, Any]:
    merged = {
        "shots": {"adhyay": adhyay, "shots": []},
        "briefs": {"adhyay": adhyay, "images": []},
        "looks": {"adhyay": adhyay, "entries": []},
        "voices": {"adhyay": adhyay, "cast": []},
        "sounds": {"adhyay": adhyay, "cues": []},
        "questions": {"adhyay": adhyay, "questions": []},
    }
    seen_looks = set()
    seen_voices = set()
    q_counter = 0
    for part in parts:
        if not isinstance(part, dict):
            continue
        # shots
        shots_doc = part.get("shots")
        if isinstance(shots_doc, dict) and isinstance(shots_doc.get("shots"), list):
            merged["shots"]["shots"].extend(shots_doc["shots"])
        # briefs
        briefs_doc = part.get("briefs")
        if isinstance(briefs_doc, dict) and isinstance(briefs_doc.get("images"), list):
            merged["briefs"]["images"].extend(briefs_doc["images"])
        # looks
        looks_doc = part.get("looks")
        if isinstance(looks_doc, dict) and isinstance(looks_doc.get("entries"), list):
            for entry in looks_doc["entries"]:
                if not isinstance(entry, dict):
                    continue
                key = (entry.get("entity_id"), entry.get("state_id"))
                if key not in seen_looks:
                    seen_looks.add(key)
                    merged["looks"]["entries"].append(entry)
        # voices
        voices_doc = part.get("voices")
        if isinstance(voices_doc, dict) and isinstance(voices_doc.get("cast"), list):
            for entry in voices_doc["cast"]:
                if not isinstance(entry, dict):
                    continue
                cid = entry.get("character_id")
                if cid not in seen_voices:
                    seen_voices.add(cid)
                    merged["voices"]["cast"].append(entry)
        # sounds
        sounds_doc = part.get("sounds")
        if isinstance(sounds_doc, dict) and isinstance(sounds_doc.get("cues"), list):
            merged["sounds"]["cues"].extend(sounds_doc["cues"])
        # questions
        questions_doc = part.get("questions")
        if isinstance(questions_doc, dict) and isinstance(questions_doc.get("questions"), list):
            for q in questions_doc["questions"]:
                if not isinstance(q, dict):
                    continue
                q_counter += 1
                new_q = dict(q)
                new_q["id"] = f"Q{q_counter}"
                merged["questions"]["questions"].append(new_q)
    return merged

# ----------------------------------------------------------------------
# Unit module loader cache
# ----------------------------------------------------------------------
_unit_module_cache: Dict[str, Any] = {}

def _get_unit_module(unit_name: str, repo_root: Path):
    if unit_name in _unit_module_cache:
        return _unit_module_cache[unit_name]
    unit_path = repo_root / "scripts" / "pipeline" / "stage1" / f"{unit_name}.py"
    mod = _load_module_by_path(unit_name, unit_path)
    _unit_module_cache[unit_name] = mod
    return mod

# ----------------------------------------------------------------------
# nemotron_caller
# ----------------------------------------------------------------------
def nemotron_caller(
    model: str = "nvidia/nemotron-3-ultra-550b-a55b",
    thinking: str = "on",
    effort: str = "high",
    max_tokens: int = 64000,
    json_mode: bool = True,
) -> Caller:
    # Load draft_source.py by path
    repo_root = Path(__file__).resolve().parents[3]
    ds_path = repo_root / "scripts" / "source" / "draft_source.py"
    ds = _load_module_by_path("ds", ds_path)
    # Load keys and key pool once
    keys = ds.nt.load_keys()
    pool = ds.nt.KeyPool(keys)
    # Wrap _stream_once with apply_profile and optionally json_mode
    coder_run_path = repo_root / "scripts" / "source" / "coder_run.py"
    coder_run = _load_module_by_path("coder_run", coder_run_path)
    original_stream_once = ds._stream_once
    def wrapped_stream_once(key: str, body: Dict[str, Any]):
        profiled_body = coder_run.apply_profile(body, thinking, effort)
        if json_mode:
            # Add response_format without overwriting existing keys
            profiled_body = dict(profiled_body)
            profiled_body.setdefault("response_format", {"type": "json_object"})
        return original_stream_once(key, profiled_body)
    ds._stream_once = wrapped_stream_once

    def caller(call_name: str, system: str, user: str) -> Tuple[str, Dict[str, Any]]:
        reply, info = ds.chat_stream(pool, keys, model, system, user, max_tokens=max_tokens)
        # Scrub reply with loaded keys
        scrubbed_reply = ds.nt.scrub(reply, keys)
        return scrubbed_reply, info
    return caller

# ----------------------------------------------------------------------
# run_stage1
# ----------------------------------------------------------------------
def run_stage1(
    adhyay: int,
    root: Union[Path, str],
    caller: Optional[Caller],
    out_dir: Union[Path, str],
    *,
    scene_group: int = 1,
    only_scenes: Optional[List[str]] = None,
    provider_name: str = "unknown",
    dry_run: bool = False,
    scrub_keys: List[str] = [],
    reuse_from: Optional[Union[Path, str]] = None,
) -> Dict[str, Any]:
    root = Path(root)
    out_dir = Path(out_dir)
    reuse_from_path = Path(reuse_from) if reuse_from is not None else None

    # Validate adhyay
    if adhyay <= 0:
        raise ValueError("adhyay must be positive")

    # Check out_dir
    if out_dir.exists() and any(out_dir.iterdir()):
        raise FileExistsError(f"Output directory {out_dir} exists and is not empty")

    # Load required modules by path
    repo_root = Path(__file__).resolve().parents[3]
    prompts_mod = _load_module_by_path("prompts", repo_root / "scripts" / "pipeline" / "stage1" / "prompts.py")
    aggregate_mod = _load_module_by_path("aggregate", repo_root / "scripts" / "pipeline" / "stage1" / "aggregate.py")
    context_mod = _load_module_by_path("context", repo_root / "scripts" / "pipeline" / "stage1" / "context.py")
    check_script_mod = _load_module_by_path("check_script", repo_root / "scripts" / "pipeline" / "check_script.py")
    chapter_mod = _load_module_by_path("chapter", repo_root / "scripts" / "pipeline" / "chapter.py")

    # 1. Build packet
    packet, packet_problems = prompts_mod.build_packet(adhyay, root)

    # Prepare output directories
    out_dir.mkdir(parents=True, exist_ok=True)
    prompts_dir = out_dir / "prompts"
    replies_dir = out_dir / "replies"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    replies_dir.mkdir(parents=True, exist_ok=True)

    # Report structure
    report = {
        "adhyay": adhyay,
        "provider": provider_name,
        "dry_run": dry_run,
        "packet_problems": packet_problems,
        "calls": [],
        "aggregate_errors": [],
        "documents_written": [],
        "counts": {
            "ovis": 0,
            "script_lines": 0,
            "scenes": 0,
            "shots": 0,
            "briefs": 0,
            "voices": 0,
            "cues": 0,
            "questions": 0,
        },
    }

    # Helper to write prompt file
    def write_prompt(name: str, system: str, user: str):
        prompt_path = prompts_dir / f"{name}.txt"
        with prompt_path.open("w", encoding="utf-8") as f:
            f.write(system)
            f.write("\n" + "-" * 40 + "\n")
            f.write(user)

    # Helper to write reply file
    def write_reply(name: str, reply: str):
        reply_path = replies_dir / f"{name}.txt"
        with reply_path.open("w", encoding="utf-8") as f:
            f.write(reply)

    # Helper to record call
    def record_call(name: str, status: str, reason: str, info: Dict[str, Any], parse_problems: List[str], schema_errors: List[str]):
        # Scrub info strings
        scrubbed_info = _scrub_dict(info, scrub_keys)
        report["calls"].append({
            "name": name,
            "status": status,
            "reason": reason,
            "info": scrubbed_info,
            "parse_problems": parse_problems,
            "schema_errors": schema_errors,
        })

    # Helper to compute counts from available data
    def compute_counts(packet: Dict[str, Any], parsed_docs: Dict[str, Any], merged: Dict[str, Any]) -> Dict[str, int]:
        counts = {
            "ovis": len(packet.get("ovis", [])),
            "script_lines": len(packet.get("script", [])),
            "scenes": 0,
            "shots": 0,
            "briefs": 0,
            "voices": 0,
            "cues": 0,
            "questions": 0,
        }
        # scenes from scenes document (from plan call)
        scenes_doc = parsed_docs.get("scenes")
        if isinstance(scenes_doc, dict):
            scenes_list = scenes_doc.get("scenes")
            if isinstance(scenes_list, list):
                counts["scenes"] = len(scenes_list)
        # shots, briefs, voices, cues, questions from merged scene parts
        counts["shots"] = len(merged.get("shots", {}).get("shots", []))
        counts["briefs"] = len(merged.get("briefs", {}).get("images", []))
        counts["voices"] = len(merged.get("voices", {}).get("cast", []))
        counts["cues"] = len(merged.get("sounds", {}).get("cues", []))
        counts["questions"] = len(merged.get("questions", {}).get("questions", []))
        return counts

    # Helper to try reuse a reply
    def try_reuse(call_name: str, expected_keys: Tuple[str, ...]) -> Tuple[Optional[Dict[str, Any]], List[str], List[str], Dict[str, Any], str]:
        """Returns (parsed, parse_problems, schema_errors, info, reason) if reused, else (None, [], [], {}, '')"""
        if reuse_from_path is None or dry_run:
            return None, [], [], {}, ""
        reply_file = reuse_from_path / "replies" / f"{call_name}.txt"
        if not reply_file.exists():
            return None, [], [], {}, ""
        try:
            reply_text = reply_file.read_text(encoding="utf-8")
        except Exception:
            return None, [], [], {}, ""
        # Parse and validate
        parsed, parse_problems = parse_reply(reply_text, expected_keys, adhyay)
        schema_errors = []
        if parsed is not None:
            for key in expected_keys:
                doc = parsed.get(key)
                if isinstance(doc, dict):
                    unit_mod = _get_unit_module(key, repo_root)
                    schema_errors.extend(unit_mod.schema_errors(doc))
        if parsed is not None and not schema_errors:
            info = {"status": 200, "wall_s": 0.0, "finish": "reused", "usage": {}}
            reason = f"reused from {reuse_from_path}"
            return parsed, parse_problems, schema_errors, info, reason
        return None, [], [], {}, ""

    # ------------------------------------------------------------------
    # Dry-run mode: write prompts only, no calls
    # ------------------------------------------------------------------
    if dry_run:
        # map
        system, user = prompts_mod.build_prompt("map", packet)
        write_prompt("map", system, user)
        record_call("map", "dry-run", "", {"status": 0, "wall_s": 0.0, "finish": "dry-run", "usage": {}}, [], [])
        # plan with empty prior
        empty_prior = {"story_map": {}}
        system, user = prompts_mod.build_prompt("plan", packet, prior=empty_prior)
        write_prompt("plan", system, user)
        record_call("plan", "dry-run", "", {"status": 0, "wall_s": 0.0, "finish": "dry-run", "usage": {}}, [], [])
        # scene calls: get scene ids from script headings
        script_path = chapter_mod.chapter_paths(adhyay, root).get("script")
        scene_ids = []
        if script_path and script_path.exists():
            script_text = script_path.read_text(encoding="utf-8")
            script_lines = check_script_mod.parse_script(script_text)
            for line in script_lines:
                # Try multiple possible keys for scene id
                sid = line.get("scene") or line.get("scene_id")
                if sid is None and "id" in line:
                    # Extract scene from id like "S1-L1"
                    parts = line["id"].split("-")
                    if parts:
                        sid = parts[0]
                if sid:
                    scene_ids.append(sid)
        # Deduplicate preserving order
        seen = set()
        unique_scene_ids = []
        for sid in scene_ids:
            if sid not in seen:
                seen.add(sid)
                unique_scene_ids.append(sid)
        if only_scenes is not None:
            unique_scene_ids = [sid for sid in unique_scene_ids if sid in only_scenes]
        # Group
        for i in range(0, len(unique_scene_ids), scene_group):
            group = unique_scene_ids[i:i+scene_group]
            name = f"scene_{i//scene_group + 1:02d}"
            empty_prior_scene = {"story_map": {}, "coverage": {}, "scenes": {"scenes": []}}
            system, user = prompts_mod.build_prompt("scene", packet, prior=empty_prior_scene, scene_ids=group)
            write_prompt(name, system, user)
            record_call(name, "dry-run", "", {"status": 0, "wall_s": 0.0, "finish": "dry-run", "usage": {}}, [], [])
        # Compute counts for dry_run (only ovis and script_lines non-zero)
        report["counts"] = compute_counts(packet, {}, {"shots": {"shots": []}, "briefs": {"images": []}, "voices": {"cast": []}, "sounds": {"cues": []}, "questions": {"questions": []}})
        # Write report
        report_path = out_dir / "report.json"
        with report_path.open("w", encoding="utf-8") as f:
            json.dump(_scrub_dict(report, scrub_keys), f, ensure_ascii=False, indent=1, sort_keys=True)
        return report

    # ------------------------------------------------------------------
    # Normal mode with caller
    # ------------------------------------------------------------------
    if caller is None:
        raise ValueError("caller must be provided when not in dry_run mode")

    # Store parsed documents for merging
    parsed_docs: Dict[str, Any] = {}
    scene_parts: List[Dict[str, Any]] = []

    # 2. Call map
    system, user = prompts_mod.build_prompt("map", packet)
    write_prompt("map", system, user)
    # Try reuse
    reused_parsed, parse_problems, schema_errors, info, reason = try_reuse("map", prompts_mod.OUTPUT_KEYS["map"])
    if reused_parsed is not None:
        parsed = reused_parsed
        scrubbed_reply = ""  # we don't have the raw reply, but we can write the parsed JSON? Spec says parse stored reply exactly like live reply. We'll write the stored reply text to replies_dir.
        # Write the stored reply to our replies_dir for consistency
        reply_file = reuse_from_path / "replies" / "map.txt"
        if reply_file.exists():
            stored_reply = reply_file.read_text(encoding="utf-8")
            write_reply("map", _scrub_text(stored_reply, scrub_keys))
        else:
            write_reply("map", "")
        record_call("map", "ok", reason, info, parse_problems, schema_errors)
    else:
        try:
            reply, info = caller("map", system, user)
        except Exception as e:
            info = {"status": 0, "wall_s": 0.0, "finish": "error", "usage": {}, "error": type(e).__name__}
            reply = ""
        scrubbed_reply = _scrub_text(reply, scrub_keys)
        write_reply("map", scrubbed_reply)
        parsed, parse_problems = parse_reply(scrubbed_reply, prompts_mod.OUTPUT_KEYS["map"], adhyay)
        schema_errors = []
        if parsed is not None:
            story_map_doc = parsed.get("story_map")
            if isinstance(story_map_doc, dict):
                unit_mod = _get_unit_module("story_map", repo_root)
                schema_errors = unit_mod.schema_errors(story_map_doc)
        if info.get("status") != 200 or parsed is None or schema_errors:
            reason = ""
            if info.get("status") != 200:
                if "error" in info:
                    reason = f"error: {info['error']}"
                else:
                    reason = f"status {info.get('status')}"
            elif parsed is None:
                reason = "parse failed"
            else:
                reason = "schema errors"
            record_call("map", "failed", reason, info, parse_problems, schema_errors)
            # Skip plan and scene
            parsed = None
        else:
            record_call("map", "ok", "", info, parse_problems, schema_errors)

    if parsed is not None:
        story_map_val = parsed.get("story_map")
        if isinstance(story_map_val, dict):
            parsed_docs["story_map"] = story_map_val

        # 3. Call plan
        prior_for_plan = {"story_map": parsed_docs.get("story_map", {})}
        system, user = prompts_mod.build_prompt("plan", packet, prior=prior_for_plan)
        write_prompt("plan", system, user)
        # Try reuse
        reused_parsed, parse_problems, schema_errors, info, reason = try_reuse("plan", prompts_mod.OUTPUT_KEYS["plan"])
        if reused_parsed is not None:
            parsed = reused_parsed
            reply_file = reuse_from_path / "replies" / "plan.txt"
            if reply_file.exists():
                stored_reply = reply_file.read_text(encoding="utf-8")
                write_reply("plan", _scrub_text(stored_reply, scrub_keys))
            else:
                write_reply("plan", "")
            record_call("plan", "ok", reason, info, parse_problems, schema_errors)
        else:
            try:
                reply, info = caller("plan", system, user)
            except Exception as e:
                info = {"status": 0, "wall_s": 0.0, "finish": "error", "usage": {}, "error": type(e).__name__}
                reply = ""
            scrubbed_reply = _scrub_text(reply, scrub_keys)
            write_reply("plan", scrubbed_reply)
            parsed, parse_problems = parse_reply(scrubbed_reply, prompts_mod.OUTPUT_KEYS["plan"], adhyay)
            schema_errors = []
            if parsed is not None:
                coverage_doc = parsed.get("coverage")
                scenes_doc = parsed.get("scenes")
                if isinstance(coverage_doc, dict):
                    unit_mod = _get_unit_module("coverage", repo_root)
                    schema_errors.extend(unit_mod.schema_errors(coverage_doc))
                if isinstance(scenes_doc, dict):
                    unit_mod = _get_unit_module("scenes", repo_root)
                    schema_errors.extend(unit_mod.schema_errors(scenes_doc))
            if info.get("status") != 200 or parsed is None or schema_errors:
                reason = ""
                if info.get("status") != 200:
                    if "error" in info:
                        reason = f"error: {info['error']}"
                    else:
                        reason = f"status {info.get('status')}"
                elif parsed is None:
                    reason = "parse failed"
                else:
                    reason = "schema errors"
                record_call("plan", "failed", reason, info, parse_problems, schema_errors)
                # Skip scene calls
                parsed = None
            else:
                record_call("plan", "ok", "", info, parse_problems, schema_errors)

        if parsed is not None:
            coverage_val = parsed.get("coverage")
            scenes_val = parsed.get("scenes")
            if isinstance(coverage_val, dict):
                parsed_docs["coverage"] = coverage_val
            if isinstance(scenes_val, dict):
                parsed_docs["scenes"] = scenes_val

            # 4. Call scene for each group
            scenes_doc = parsed_docs.get("scenes")
            scene_ids = []
            if isinstance(scenes_doc, dict):
                # Try multiple possible keys for the scene list
                for key in ("scenes", "scene_ids", "scene_list", "scene"):
                    val = scenes_doc.get(key)
                    if isinstance(val, list):
                        for s in val:
                            if isinstance(s, str):
                                scene_ids.append(s)
                        break
            if only_scenes is not None:
                scene_ids = [sid for sid in scene_ids if sid in only_scenes]

            # Fallback: if no scene ids from scenes doc, extract from script (like dry_run)
            if not scene_ids:
                script_path = chapter_mod.chapter_paths(adhyay, root).get("script")
                if script_path and script_path.exists():
                    script_text = script_path.read_text(encoding="utf-8")
                    script_lines = check_script_mod.parse_script(script_text)
                    for line in script_lines:
                        sid = line.get("scene") or line.get("scene_id")
                        if sid is None and "id" in line:
                            parts = line["id"].split("-")
                            if parts:
                                sid = parts[0]
                        if sid:
                            scene_ids.append(sid)
                    # Deduplicate preserving order
                    seen = set()
                    unique_scene_ids = []
                    for sid in scene_ids:
                        if sid not in seen:
                            seen.add(sid)
                            unique_scene_ids.append(sid)
                    scene_ids = unique_scene_ids
                    if only_scenes is not None:
                        scene_ids = [sid for sid in scene_ids if sid in only_scenes]

            for i in range(0, len(scene_ids), scene_group):
                group = scene_ids[i:i+scene_group]
                name = f"scene_{i//scene_group + 1:02d}"
                prior_for_scene = {
                    "story_map": parsed_docs.get("story_map", {}),
                    "coverage": parsed_docs.get("coverage", {}),
                    "scenes": parsed_docs.get("scenes", {}),
                }
                system, user = prompts_mod.build_prompt(
                    "scene", packet,
                    prior=prior_for_scene,
                    scene_ids=group
                )
                write_prompt(name, system, user)
                # Try reuse
                reused_parsed, parse_problems, schema_errors, info, reason = try_reuse(name, prompts_mod.OUTPUT_KEYS["scene"])
                if reused_parsed is not None:
                    parsed = reused_parsed
                    reply_file = reuse_from_path / "replies" / f"{name}.txt"
                    if reply_file.exists():
                        stored_reply = reply_file.read_text(encoding="utf-8")
                        write_reply(name, _scrub_text(stored_reply, scrub_keys))
                    else:
                        write_reply(name, "")
                    record_call(name, "ok", reason, info, parse_problems, schema_errors)
                else:
                    try:
                        reply, info = caller(name, system, user)
                    except Exception as e:
                        info = {"status": 0, "wall_s": 0.0, "finish": "error", "usage": {}, "error": type(e).__name__}
                        reply = ""
                    scrubbed_reply = _scrub_text(reply, scrub_keys)
                    write_reply(name, scrubbed_reply)
                    parsed, parse_problems = parse_reply(scrubbed_reply, prompts_mod.OUTPUT_KEYS["scene"], adhyay)
                    schema_errors = []
                    if parsed is not None:
                        # Validate each document in the scene reply
                        for key in prompts_mod.OUTPUT_KEYS["scene"]:
                            doc = parsed.get(key)
                            if isinstance(doc, dict):
                                unit_mod = _get_unit_module(key, repo_root)
                                schema_errors.extend(unit_mod.schema_errors(doc))
                    if info.get("status") != 200 or parsed is None or schema_errors:
                        reason = ""
                        if info.get("status") != 200:
                            if "error" in info:
                                reason = f"error: {info['error']}"
                            else:
                                reason = f"status {info.get('status')}"
                        elif parsed is None:
                            reason = "parse failed"
                        else:
                            reason = "schema errors"
                        record_call(name, "failed", reason, info, parse_problems, schema_errors)
                        # Continue to next scene group (do not break)
                        continue
                    else:
                        record_call(name, "ok", "", info, parse_problems, schema_errors)
                if parsed is not None:
                    scene_parts.append(parsed)

    # ------------------------------------------------------------------
    # Merge scene parts and write documents
    # ------------------------------------------------------------------
    merged = merge_scene_parts(adhyay, scene_parts)
    # Combine with story_map, coverage, scenes from earlier calls
    all_docs = {
        "story_map": parsed_docs.get("story_map"),
        "coverage": parsed_docs.get("coverage"),
        "scenes": parsed_docs.get("scenes"),
        **merged,
    }
    # Write each document that exists
    for unit_name in aggregate_mod.UNITS:
        doc = all_docs.get(unit_name)
        if doc is not None:
            out_path = out_dir / f"{unit_name}.json"
            with out_path.open("w", encoding="utf-8") as f:
                json.dump(_scrub_dict(doc, scrub_keys), f, ensure_ascii=False, indent=1, sort_keys=True)
            report["documents_written"].append(unit_name)

    # ------------------------------------------------------------------
    # Build context and validate
    # ------------------------------------------------------------------
    # Gather extra info for context
    script_path = chapter_mod.chapter_paths(adhyay, root).get("script")
    script_lines = []
    if script_path and script_path.exists():
        script_text = script_path.read_text(encoding="utf-8")
        script_lines = check_script_mod.parse_script(script_text)
    script_line_ids = [line["id"] for line in script_lines if "id" in line]
    core_line_ids = [line["id"] for line in script_lines if line.get("priority") == "core"]
    script_texts = []
    for line in script_lines:
        if line.get("marathi"):
            script_texts.append(line["marathi"])
        if line.get("hindi"):
            script_texts.append(line["hindi"])
    speaking_characters = sorted(set(line.get("voice", "") for line in script_lines if line.get("voice")) | {"narrator"})

    extra = {
        "script_line_ids": script_line_ids,
        "core_line_ids": core_line_ids,
        "script_texts": script_texts,
        "speaking_characters": speaking_characters,
        "known_states": {},
    }
    ctx, ctx_problems = context_mod.build_ctx(adhyay, root, extra=extra)
    # Validate all
    aggregate_errors = aggregate_mod.validate_all(adhyay, all_docs, ctx)
    report["aggregate_errors"] = aggregate_errors

    # Update counts from actual data used
    report["counts"] = compute_counts(packet, parsed_docs, merged)

    # Write report
    report_path = out_dir / "report.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(_scrub_dict(report, scrub_keys), f, ensure_ascii=False, indent=1, sort_keys=True)

    return report

# ----------------------------------------------------------------------
# main
# ----------------------------------------------------------------------
def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run Stage 1 planning for an Adhyay")
    parser.add_argument("--adhyay", type=int, required=True, help="Adhyay number")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3], help="Repository root")
    parser.add_argument("--out", type=Path, required=True, help="Output directory (must not exist or be empty)")
    parser.add_argument("--provider", choices=["nemotron", "dry-run", "kimi"], default="dry-run", help="Provider to use")
    parser.add_argument("--model", default="nvidia/nemotron-3-ultra-550b-a55b", help="Model name for nemotron")
    parser.add_argument("--thinking", choices=["on", "off"], default="on", help="Thinking mode for nemotron")
    parser.add_argument("--effort", choices=["low", "medium", "high", "none"], default="high", help="Effort for nemotron")
    parser.add_argument("--max-tokens", type=int, default=64000, help="Max tokens for nemotron")
    parser.add_argument("--scene-group", type=int, default=1, help="Number of scenes per scene call")
    parser.add_argument("--only-scenes", type=str, default="", help="Comma-separated list of scene ids to process")
    parser.add_argument("--json-mode", choices=["on", "off"], default="on", help="Enable JSON response format for nemotron")
    parser.add_argument("--reuse-from", type=Path, default=None, help="Directory to reuse replies from (previous out directory)")
    args = parser.parse_args(argv)

    if args.provider == "kimi":
        print("refused: Kimi calls need the credit ledger and the owner's go; not available in this module")
        return 2

    only_scenes = [s.strip() for s in args.only_scenes.split(",") if s.strip()] if args.only_scenes else None

    if args.provider == "dry-run":
        caller = None
        dry_run = True
        provider_name = "dry-run"
    else:  # nemotron
        caller = nemotron_caller(
            model=args.model,
            thinking=args.thinking,
            effort=args.effort,
            max_tokens=args.max_tokens,
            json_mode=(args.json_mode == "on"),
        )
        dry_run = False
        provider_name = "nemotron"

    try:
        report = run_stage1(
            adhyay=args.adhyay,
            root=args.root,
            caller=caller,
            out_dir=args.out,
            scene_group=args.scene_group,
            only_scenes=only_scenes,
            provider_name=provider_name,
            dry_run=dry_run,
            reuse_from=args.reuse_from,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Print summary
    for call in report["calls"]:
        print(f"{call['name']} {call['status']}")
    print(f"aggregate errors: {len(report['aggregate_errors'])}")

    # Determine exit code
    all_ok = all(call["status"] in ("ok", "dry-run") for call in report["calls"])
    no_aggregate_errors = len(report["aggregate_errors"]) == 0
    if all_ok and no_aggregate_errors:
        return 0
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
