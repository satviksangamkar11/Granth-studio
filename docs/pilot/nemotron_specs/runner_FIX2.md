# SPEC: NEW `scripts/pipeline/stage1/runner.py` + NEW `tests/test_stage1_runner.py`. Return exactly these TWO files in full; do not output or change any other file.
Purpose (checklist S4 runner): run the three Stage 1 planning calls for ANY Adhyay with an injected model caller, validate every answer, merge the per-scene answers, check the nine documents together, and write the result with a report. NO automatic repair: one call each, a failure is recorded and later calls that depend on it are skipped. The default provider is the free Nemotron endpoint (used for all trials); a paid Kimi provider is NOT part of this module and is refused. Standard library only; `from __future__ import annotations`; nothing at import time except imports and definitions; plain functions, no classes. Do not over-engineer. Nothing may be specific to one chapter. No key or secret is ever printed, logged, stored in a file or put in an exception.

## Existing code you may use (load by importlib BY PATH; do not modify them)
- `scripts/pipeline/stage1/prompts.py`: `CALLS`, `OUTPUT_KEYS`, `build_packet(adhyay, root) -> (packet, problems)`, `build_prompt(call, packet, *, scene_ids=None, prior=None) -> (system, user)` (calls `map`, `plan`, `scene`; `plan` needs prior {"story_map"}, `scene` needs prior {"story_map","coverage","scenes"} and `scene_ids`).
- `scripts/pipeline/stage1/aggregate.py`: `validate_all(adhyay, docs, ctx) -> list[str]`, `UNITS` (the nine unit names); each unit module `scripts/pipeline/stage1/<unit>.py` has `schema_errors(doc) -> list[str]`.
- `scripts/pipeline/stage1/context.py`: `build_ctx(adhyay, root, extra=None) -> (ctx, problems)`.
- `scripts/pipeline/check_script.py`: `parse_script(text) -> list[dict]` with `id, scene, voice, ovi, priority, marathi, hindi`.
- `scripts/pipeline/chapter.py`: `chapter_paths(adhyay, root)`.
- `scripts/source/coder_run.py`: `apply_profile(body: dict, thinking: str, effort: str) -> dict` (adds the Nemotron thinking and effort request fields only for `nvidia/nemotron` models).
- `scripts/source/draft_source.py` (load by path with module name `ds`): `ds.nt.load_keys()`, `ds.nt.KeyPool(keys)`, `ds.nt.scrub(text, keys)`, `ds.chat_stream(pool, keys, model, system, user, max_tokens=N) -> (reply_text, info)` where `info` has `status`, `wall_s`, `finish`, `usage`, `error`; it builds the request through the module-level function `ds._stream_once(key, body)` which you may wrap (`ds._stream_once = lambda key, body: orig(key, apply_profile(body, thinking, effort))`). A usable reply needs `info["status"] == 200`.
Repo root in this module: `Path(__file__).resolve().parents[3]`; in tests `Path(__file__).resolve().parents[1]`.

## API
- `Caller` = a function `caller(call_name: str, system: str, user: str) -> tuple[str, dict]` returning the model reply text and an info dict (`status`, `wall_s`, `finish`, `usage` when known, `error`). Any exception inside a caller is caught by the runner and recorded as a failed call (`error: <ExceptionClass>`).
- `nemotron_caller(model: str = "nvidia/nemotron-3-ultra-550b-a55b", thinking: str = "on", effort: str = "high", max_tokens: int = 64000) -> Caller`: loads `draft_source.py` by path, wraps `_stream_once` with `apply_profile`, loads the keys and the key pool ONCE (inside this function, not at import), and returns a caller that sends the system and user text through `ds.chat_stream`; the reply is scrubbed with `ds.nt.scrub(reply, keys)` and the info dict never contains a key. A reply that is empty or has `status != 200` is returned with the info as is (the runner decides).
- `parse_reply(text: str, expected_keys: tuple[str, ...], adhyay: int) -> tuple[dict | None, list[str]]`: tolerate a markdown fence or leading/trailing prose: take the substring from the first `{` to the last `}`; `json.loads` it; problems: `reply: no json object`, `reply: bad json`, `reply: not an object`, `reply: missing key <k>` for each missing expected key, `reply: unexpected key <k>` for each extra key. For each expected key whose value is a dict without `adhyay`, set `adhyay` to the given number; if `adhyay` is present and differs: problem `<k>: adhyay <x> is not <N>`. Returns `(object, problems)`; the object is None when the JSON could not be read.
- `merge_scene_parts(adhyay: int, parts: list[dict]) -> dict`: parts are the parsed objects of the `scene` calls (keys shots, briefs, looks, voices, sounds, questions). Returns the six merged documents `{ "shots": {"adhyay": N, "shots": [...]}, "briefs": {"adhyay": N, "images": [...]}, "looks": {"adhyay": N, "entries": [...]}, "voices": {"adhyay": N, "cast": [...]}, "sounds": {"adhyay": N, "cues": [...]}, "questions": {"adhyay": N, "questions": [...]} }`: lists are concatenated in part order; `looks.entries` are de-duplicated by the pair (`entity_id`, `state_id`) keeping the first; `voices.cast` is de-duplicated by `character_id` keeping the first; `questions` get new ids `Q1, Q2, ...` in order (keep text and scene_id). A part or a document that is not the expected shape is skipped (never raises).
- `run_stage1(adhyay: int, root: Path | str, caller: Caller | None, out_dir: Path | str, *, scene_group: int = 1, only_scenes: list[str] | None = None, provider_name: str = "unknown", dry_run: bool = False) -> dict`: NEVER raises for model or data problems (only `ValueError` for an invalid adhyay or `FileExistsError` if `out_dir` already exists and is not empty). Steps:
  1. `build_packet`; record its problems in the report.
  2. Create `out_dir`, `out_dir/prompts`, `out_dir/replies`. For every call write the prompt as `prompts/<name>.txt` (system, a line of 40 dashes, user) BEFORE calling.
  3. Call `map` (prior none): parse with `OUTPUT_KEYS["map"]`, then `story_map.schema_errors` on the document; call `plan` only if `map` succeeded (reply parsed and its document has no schema errors), with prior {"story_map": ...}; call `scene` calls only if `plan` succeeded: scene ids come from the `scenes` document (in its order, only those that are strings; `only_scenes` filters), grouped `scene_group` at a time; each `scene` call gets prior {"story_map","coverage","scenes"} and `scene_ids` of its group. Name the prompt/reply files `map`, `plan`, `scene_01`, `scene_02`, ....
  4. Write each raw reply (already scrubbed) to `replies/<name>.txt`. A call whose reply could not be parsed, whose info status is not 200, or whose documents have schema errors is FAILED: record the reason and skip the calls that depend on it (`skipped: map failed` etc.). Never re-ask the model.
  5. With `dry_run=True` (caller may be None) only the prompt files and the report are written, no call is made, each call is reported `dry-run`; for `plan` and `scene` the prompts use EMPTY placeholder priors `{"story_map": {}, "coverage": {}, "scenes": {"scenes": []}}` and for `scene` the scene ids from the script headings (`parse_script` scene ids in order, filtered by `only_scenes`) so every prompt can be inspected.
  6. When all calls succeeded: merge the scene parts, write every document that exists as `out_dir/<unit>.json` (utf-8, `ensure_ascii=False`, indent 1, sorted keys), build the context `build_ctx(adhyay, root, extra=...)` with extra = `script_line_ids` (script ids), `core_line_ids` (ids whose priority is core), `script_texts` (all Marathi and Hindi line texts), `speaking_characters` (the sorted distinct script voices plus `narrator`), `known_states` `{}`; run `validate_all(adhyay, docs, ctx)` and put the errors in the report. With some calls failed, still write the documents that exist and run `validate_all` on what exists (it reports missing documents).
  7. Write `out_dir/report.json` and return the same dict: `{"adhyay", "provider", "dry_run", "packet_problems", "calls": [{"name", "status": "ok"|"failed"|"skipped"|"dry-run", "reason", "info": {status, wall_s, finish, usage}, "parse_problems", "schema_errors"}], "aggregate_errors": [...], "documents_written": [...], "counts": {"ovis", "script_lines", "scenes", "shots", "briefs", "voices", "cues", "questions"}}`. The report never contains a key; scrub is applied to every string that came from the provider.
- `main(argv=None) -> int`: `--adhyay N` (required), `--root PATH` (default repo root), `--out DIR` (required, must not exist or be empty), `--provider {nemotron,dry-run,kimi}` (default dry-run), `--model` (default the Nemotron Ultra id), `--thinking {on,off}` (default on), `--effort {low,medium,high,none}` (default high), `--max-tokens` (default 64000), `--scene-group N` (default 1), `--only-scenes S1,S2`. Provider `kimi`: print `refused: Kimi calls need the credit ledger and the owner's go; not available in this module` and return 2 without any call. Provider `dry-run`: `run_stage1(... caller=None, dry_run=True)`. Provider `nemotron`: build `nemotron_caller(...)` and run. Prints one summary line per call (`name status`) and the number of aggregate errors; returns 0 when every call is ok (or dry-run) and there are no aggregate errors, 1 otherwise, 2 for a refusal. `if __name__ == "__main__": raise SystemExit(main())`.

## Tests (`tests/test_stage1_runner.py`; offline, no network, no key; load modules by importlib BY PATH)
Use the shared valid documents `docs/pilot/nemotron_specs/stage1_base.json` (keys `docs` and `ctx`, tiny chapter of 9 ovis, 3 script lines S1-L1, S1-L2, S2-L1, scenes S1 and S2). Build a synthetic root in tmp_path that matches those documents: `canon/adhyay_02/source/ovis.jsonl` with ovis 1..9 (fields ovi, section, original_marathi, simple_marathi, hindi, easy_english), `canon/adhyay_02/script/easy.md` in the EASY format with lines S1-L1 (ovi 1), S1-L2 (ovi 3), S2-L1 (ovi 7) voices narrator/gajanan_maharaj as in the base ctx, the preset index with the base `preset_ids`, a voice library whose `saved_voices` match the base ctx, and no sound palette. Write a fake caller that replays the base documents by call name: `map` -> {"story_map": base}, `plan` -> {"coverage", "scenes"}, each `scene` call -> the base shots/briefs/looks/voices/sounds/questions restricted to its scene ids (filter lists by `scene_id`; looks and voices are not per scene: give them whole in the first scene call and empty lists afterwards).
1. End to end with the fake caller (scene_group=1): all calls `ok`, nine documents written, `aggregate_errors == []`, report counts right, prompts and replies files exist; a recorded call count of exactly 1 + 1 + 2.
2. `scene_group=2` makes ONE scene call.
3. `parse_reply`: fenced JSON, prose around JSON, no json, bad json, array, missing key, extra key, adhyay mismatch, adhyay filled when missing (each in its own test).
4. Failure handling: a caller that returns invalid JSON for `map` -> `map` failed, `plan` and `scene` skipped, report written, no second call to the model (count calls); a caller that raises -> failed with the exception class name and no exception escapes; a `plan` reply whose scenes document violates its schema -> failed and scenes skipped; info status 500 -> failed.
5. `merge_scene_parts`: concatenation order, de-duplication of looks and voices, questions renumbered `Q1..`, a malformed part skipped without raising.
6. `dry_run=True` with `caller=None` writes the prompts for map, plan and the scenes from the script headings and calls nothing (use a caller that fails the test if invoked); `out_dir` existing and non-empty raises FileExistsError; invalid adhyay raises ValueError.
7. `main`: `--provider kimi` returns 2 and prints the refusal and makes no call; `--provider dry-run` returns 0 and writes prompts; missing arguments handled by argparse. A source-level test: the module source contains no `kimi_adapter` import and no literal key prefix `nvapi-`.
8. Secrets: the report and every written file contain no `nvapi-` and no `sk-` strings even when the fake caller returns a reply containing a fake key string `nvapi-FAKEKEY1234567890` (the runner must scrub it from the stored reply and the report when it is one of the loaded keys: monkeypatch/inject the key list for this test, e.g. by letting `run_stage1` accept an optional `scrub_keys: list[str] = []` parameter applied to every stored provider string).
Use `copy.deepcopy` and plain assignment for mutations; never a helper that rejects no-effect mutations; remember `True == 1`.

Reply with only the two FILE blocks:
FILE: scripts/pipeline/stage1/runner.py
FILE: tests/test_stage1_runner.py


## CURRENT scripts/pipeline/stage1/runner.py (your previous reply contained ONLY this module; the test file was missing). THIS CALL MUST RETURN BOTH FILES, each complete: the module (correct anything the spec requires that it misses) AND tests/test_stage1_runner.py written per the Tests section above. Do not skip the test file.
```python
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
# parse_reply
# ----------------------------------------------------------------------
def parse_reply(text: str, expected_keys: Tuple[str, ...], adhyay: int) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    problems: List[str] = []
    # Extract JSON object from first { to last }
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        problems.append("reply: no json object")
        return None, problems
    json_text = text[start:end+1]
    try:
        obj = json.loads(json_text)
    except json.JSONDecodeError:
        problems.append("reply: bad json")
        return None, problems
    if not isinstance(obj, dict):
        problems.append("reply: not an object")
        return None, problems
    # Check keys
    for k in expected_keys:
        if k not in obj:
            problems.append(f"reply: missing key {k}")
    for k in obj.keys():
        if k not in expected_keys:
            problems.append(f"reply: unexpected key {k}")
    # Fix adhyay in nested dicts
    for k in expected_keys:
        if k in obj and isinstance(obj[k], dict):
            if "adhyay" not in obj[k]:
                obj[k]["adhyay"] = adhyay
            elif obj[k]["adhyay"] != adhyay:
                problems.append(f"{k}: adhyay {obj[k]['adhyay']} is not {adhyay}")
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
# nemotron_caller
# ----------------------------------------------------------------------
def nemotron_caller(
    model: str = "nvidia/nemotron-3-ultra-550b-a55b",
    thinking: str = "on",
    effort: str = "high",
    max_tokens: int = 64000,
) -> Caller:
    # Load draft_source.py by path
    repo_root = Path(__file__).resolve().parents[3]
    ds_path = repo_root / "scripts" / "source" / "draft_source.py"
    ds = _load_module_by_path("ds", ds_path)
    # Load keys and key pool once
    keys = ds.nt.load_keys()
    pool = ds.nt.KeyPool(keys)
    # Wrap _stream_once with apply_profile
    coder_run_path = repo_root / "scripts" / "source" / "coder_run.py"
    coder_run = _load_module_by_path("coder_run", coder_run_path)
    original_stream_once = ds._stream_once
    def wrapped_stream_once(key: str, body: Dict[str, Any]):
        profiled_body = coder_run.apply_profile(body, thinking, effort)
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
    scrub_keys: Optional[List[str]] = None,
) -> Dict[str, Any]:
    if scrub_keys is None:
        scrub_keys = []
    root = Path(root)
    out_dir = Path(out_dir)

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
        script_path = chapter_mod.chapter_paths(adhyay, root)["script"]
        script_text = script_path.read_text(encoding="utf-8")
        script_lines = check_script_mod.parse_script(script_text)
        scene_ids = [line["scene"] for line in script_lines if "scene" in line]
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
    reply, info = caller("map", system, user)
    scrubbed_reply = _scrub_text(reply, scrub_keys)
    write_reply("map", scrubbed_reply)
    parsed, parse_problems = parse_reply(scrubbed_reply, prompts_mod.OUTPUT_KEYS["map"], adhyay)
    schema_errors = []
    if parsed is not None:
        story_map_doc = parsed.get("story_map")
        if isinstance(story_map_doc, dict):
            schema_errors = aggregate_mod.schema_errors(story_map_doc)  # type: ignore[attr-defined]
    if info.get("status") != 200 or parsed is None or schema_errors:
        reason = ""
        if info.get("status") != 200:
            reason = f"status {info.get('status')}"
        elif parsed is None:
            reason = "parse failed"
        else:
            reason = "schema errors"
        record_call("map", "failed", reason, info, parse_problems, schema_errors)
        # Skip plan and scene
        for call_name in ["plan"] + [f"scene_{i:02d}" for i in range(1, 100)]:
            # We don't know how many scenes, but we'll just skip all future calls by not making them.
            pass
    else:
        record_call("map", "ok", "", info, parse_problems, schema_errors)
        parsed_docs["story_map"] = parsed["story_map"]

        # 3. Call plan
        system, user = prompts_mod.build_prompt("plan", packet, prior={"story_map": parsed_docs["story_map"]})
        write_prompt("plan", system, user)
        reply, info = caller("plan", system, user)
        scrubbed_reply = _scrub_text(reply, scrub_keys)
        write_reply("plan", scrubbed_reply)
        parsed, parse_problems = parse_reply(scrubbed_reply, prompts_mod.OUTPUT_KEYS["plan"], adhyay)
        schema_errors = []
        if parsed is not None:
            coverage_doc = parsed.get("coverage")
            scenes_doc = parsed.get("scenes")
            if isinstance(coverage_doc, dict):
                schema_errors.extend(aggregate_mod.schema_errors(coverage_doc))  # type: ignore[attr-defined]
            if isinstance(scenes_doc, dict):
                schema_errors.extend(aggregate_mod.schema_errors(scenes_doc))  # type: ignore[attr-defined]
        if info.get("status") != 200 or parsed is None or schema_errors:
            reason = ""
            if info.get("status") != 200:
                reason = f"status {info.get('status')}"
            elif parsed is None:
                reason = "parse failed"
            else:
                reason = "schema errors"
            record_call("plan", "failed", reason, info, parse_problems, schema_errors)
            # Skip scene calls
        else:
            record_call("plan", "ok", "", info, parse_problems, schema_errors)
            parsed_docs["coverage"] = parsed["coverage"]
            parsed_docs["scenes"] = parsed["scenes"]

            # 4. Call scene for each group
            scenes_doc = parsed_docs["scenes"]
            scene_ids = []
            if isinstance(scenes_doc, dict) and isinstance(scenes_doc.get("scenes"), list):
                for s in scenes_doc["scenes"]:
                    if isinstance(s, str):
                        scene_ids.append(s)
            if only_scenes is not None:
                scene_ids = [sid for sid in scene_ids if sid in only_scenes]

            for i in range(0, len(scene_ids), scene_group):
                group = scene_ids[i:i+scene_group]
                name = f"scene_{i//scene_group + 1:02d}"
                system, user = prompts_mod.build_prompt(
                    "scene", packet,
                    prior={"story_map": parsed_docs["story_map"], "coverage": parsed_docs["coverage"], "scenes": parsed_docs["scenes"]},
                    scene_ids=group
                )
                write_prompt(name, system, user)
                reply, info = caller(name, system, user)
                scrubbed_reply = _scrub_text(reply, scrub_keys)
                write_reply(name, scrubbed_reply)
                parsed, parse_problems = parse_reply(scrubbed_reply, prompts_mod.OUTPUT_KEYS["scene"], adhyay)
                schema_errors = []
                if parsed is not None:
                    # Validate each document in the scene reply
                    for key in prompts_mod.OUTPUT_KEYS["scene"]:
                        doc = parsed.get(key)
                        if isinstance(doc, dict):
                            schema_errors.extend(aggregate_mod.schema_errors(doc))  # type: ignore[attr-defined]
                if info.get("status") != 200 or parsed is None or schema_errors:
                    reason = ""
                    if info.get("status") != 200:
                        reason = f"status {info.get('status')}"
                    elif parsed is None:
                        reason = "parse failed"
                    else:
                        reason = "schema errors"
                    record_call(name, "failed", reason, info, parse_problems, schema_errors)
                    # Skip remaining scene calls
                    break
                else:
                    record_call(name, "ok", "", info, parse_problems, schema_errors)
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
    for unit_name in aggregate_mod.UNITS:  # type: ignore[attr-defined]
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
    script_path = chapter_mod.chapter_paths(adhyay, root)["script"]
    script_text = script_path.read_text(encoding="utf-8")
    script_lines = check_script_mod.parse_script(script_text)
    script_line_ids = [line["id"] for line in script_lines]
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
    aggregate_errors = aggregate_mod.validate_all(adhyay, all_docs, ctx)  # type: ignore[attr-defined]
    report["aggregate_errors"] = aggregate_errors

    # Update counts
    ovis_path = chapter_mod.chapter_paths(adhyay, root)["ovis"]
    ovis_count = 0
    if ovis_path.exists():
        with ovis_path.open("r", encoding="utf-8") as f:
            for _ in f:
                ovis_count += 1
    report["counts"]["ovis"] = ovis_count
    report["counts"]["script_lines"] = len(script_lines)
    report["counts"]["scenes"] = len(set(line.get("scene") for line in script_lines if line.get("scene")))
    report["counts"]["shots"] = len(merged["shots"]["shots"])
    report["counts"]["briefs"] = len(merged["briefs"]["images"])
    report["counts"]["voices"] = len(merged["voices"]["cast"])
    report["counts"]["cues"] = len(merged["sounds"]["cues"])
    report["counts"]["questions"] = len(merged["questions"]["questions"])

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
```
