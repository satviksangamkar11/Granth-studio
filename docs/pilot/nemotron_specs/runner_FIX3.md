# FIX CALL: return BOTH files in full: `scripts/pipeline/stage1/runner.py` and `tests/test_stage1_runner.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
...FF.........FFFFFFF......F                                             [100%]
================================== FAILURES ===================================
__________________________ test_parse_reply_bad_json __________________________
tests\test_stage1_runner.py:218: in test_parse_reply_bad_json
    assert "reply: bad json" in probs
E   AssertionError: assert 'reply: bad json' in ['reply: no json object']
___________________________ test_parse_reply_array ____________________________
tests\test_stage1_runner.py:224: in test_parse_reply_array
    assert "reply: not an object" in probs
E   AssertionError: assert 'reply: not an object' in ['reply: no json object']
_________________________ test_run_stage1_end_to_end __________________________
tests\test_stage1_runner.py:309: in test_run_stage1_end_to_end
    report = runner.run_stage1(
scripts\pipeline\stage1\runner.py:327: in run_stage1
    schema_errors = aggregate_mod.schema_errors(story_map_doc)  # type: ignore[attr-defined]
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: module 'aggregate' has no attribute 'schema_errors'
________________________ test_run_stage1_scene_group_2 ________________________
tests\test_stage1_runner.py:349: in test_run_stage1_scene_group_2
    report = runner.run_stage1(
scripts\pipeline\stage1\runner.py:327: in run_stage1
    schema_errors = aggregate_mod.schema_errors(story_map_doc)  # type: ignore[attr-defined]
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: module 'aggregate' has no attribute 'schema_errors'
______________________ test_run_stage1_map_invalid_json _______________________
tests\test_stage1_runner.py:373: in test_run_stage1_map_invalid_json
    report = runner.run_stage1(
scripts\pipeline\stage1\runner.py:467: in run_stage1
    ovis_path = chapter_mod.chapter_paths(adhyay, root)["ovis"]
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   KeyError: 'ovis'
________________________ test_run_stage1_caller_raises ________________________
tests\test_stage1_runner.py:394: in test_run_stage1_caller_raises
    report = runner.run_stage1(
scripts\pipeline\stage1\runner.py:319: in run_stage1
    reply, info = caller("map", system, user)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\test_stage1_runner.py:393: in raising_caller
    raise ValueError("boom")
E   ValueError: boom
______________________ test_run_stage1_plan_schema_error ______________________
tests\test_stage1_runner.py:417: in test_run_stage1_plan_schema_error
    report = runner.run_stage1(
scripts\pipeline\stage1\runner.py:327: in run_stage1
    schema_errors = aggregate_mod.schema_errors(story_map_doc)  # type: ignore[attr-defined]
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: module 'aggregate' has no attribute 'schema_errors'
_________________________ test_run_stage1_status_500 __________________________
tests\test_stage1_runner.py:438: in test_run_stage1_status_500
    report = runner.run_stage1(
scripts\pipeline\stage1\runner.py:467: in run_stage1
    ovis_path = chapter_mod.chapter_paths(adhyay, root)["ovis"]
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   KeyError: 'ovis'
___________________________ test_run_stage1_dry_run ___________________________
tests\test_stage1_runner.py:470: in test_run_stage1_dry_run
    assert len(report["calls"]) == 4
E   AssertionError: assert 2 == 4
E    +  where 2 = len([{'name': 'map', 'status': 'dry-run', 'reason': '', 'info': {'status': 0, 'wall_s': 0.0, 'finish': 'dry-run', 'usage':...plan', 'status': 'dry-run', 'reason': '', 'info': {'status': 0, 'wall_s': 0.0, 'finish': 'dry-run', 'usage': {}}, ...}])
____________________________ test_secrets_scrubbed ____________________________
tests\test_stage1_runner.py:558: in test_secrets_scrubbed
    report = runner.run_stage1(
scripts\pipeline\stage1\runner.py:327: in run_stage1
    schema_errors = aggregate_mod.schema_errors(story_map_doc)  # type: ignore[attr-defined]
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: module 'aggregate' has no attribute 'schema_errors'
=========================== short test summary info ===========================
FAILED tests/test_stage1_runner.py::test_parse_reply_bad_json - AssertionErro...
FAILED tests/test_stage1_runner.py::test_parse_reply_array - AssertionError: ...
FAILED tests/test_stage1_runner.py::test_run_stage1_end_to_end - AttributeErr...
FAILED tests/test_stage1_runner.py::test_run_stage1_scene_group_2 - Attribute...
FAILED tests/test_stage1_runner.py::test_run_stage1_map_invalid_json - KeyErr...
FAILED tests/test_stage1_runner.py::test_run_stage1_caller_raises - ValueErro...
FAILED tests/test_stage1_runner.py::test_run_stage1_plan_schema_error - Attri...
FAILED tests/test_stage1_runner.py::test_run_stage1_status_500 - KeyError: 'o...
FAILED tests/test_stage1_runner.py::test_run_stage1_dry_run - AssertionError:...
FAILED tests/test_stage1_runner.py::test_secrets_scrubbed - AttributeError: m...
10 failed, 18 passed in 0.49s

```

## SPEC
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


## CURRENT MODULE scripts/pipeline/stage1/runner.py
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
    scrub_keys: List[str] = [],
) -> Dict[str, Any]:
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

## CURRENT TESTS tests/test_stage1_runner.py
```python
from __future__ import annotations

import json
import sys
import importlib.util
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple, Optional

import pytest

# ----------------------------------------------------------------------
# Helper to load modules by path
# ----------------------------------------------------------------------
def _load_module_by_path(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module {module_name} from {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# ----------------------------------------------------------------------
# Locate repo root and load the runner module
# ----------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = REPO_ROOT / "scripts" / "pipeline" / "stage1" / "runner.py"
runner = _load_module_by_path("runner", RUNNER_PATH)

# Load base spec data
BASE_JSON_PATH = REPO_ROOT / "docs" / "pilot" / "nemotron_specs" / "stage1_base.json"
with BASE_JSON_PATH.open("r", encoding="utf-8") as f:
    BASE = json.load(f)
BASE_DOCS = BASE["docs"]
BASE_CTX = BASE["ctx"]

# ----------------------------------------------------------------------
# Synthetic root builder
# ----------------------------------------------------------------------
def build_synthetic_root(tmp_path: Path) -> Path:
    """Create a minimal canon/adhyay_02 tree that matches BASE_DOCS and BASE_CTX."""
    adhyay_dir = tmp_path / "canon" / "adhyay_02"
    # ovis.jsonl
    source_dir = adhyay_dir / "source"
    source_dir.mkdir(parents=True)
    ovis_lines = []
    for ovi in range(1, 10):
        ovis_lines.append(json.dumps({
            "ovi": ovi,
            "section": "test",
            "original_marathi": f"मराठी {ovi}",
            "simple_marathi": f"सरल मराठी {ovi}",
            "hindi": f"हिंदी {ovi}",
            "easy_english": f"Easy English {ovi}"
        }))
    (source_dir / "ovis.jsonl").write_text("\n".join(ovis_lines), encoding="utf-8")

    # script/easy.md
    script_dir = adhyay_dir / "script"
    script_dir.mkdir(parents=True)
    # EASY format lines as in BASE_CTX
    script_content = """# Adhyay 2

## Scene S1
### Line S1-L1 (ovi 1)
**Voice:** narrator
**Marathi:** मराठी 1
**Hindi:** हिंदी 1
**Priority:** core

### Line S1-L2 (ovi 3)
**Voice:** gajanan_maharaj
**Marathi:** मराठी 3
**Hindi:** हिंदी 3
**Priority:** core

## Scene S2
### Line S2-L1 (ovi 7)
**Voice:** narrator
**Marathi:** मराठी 7
**Hindi:** हिंदी 7
**Priority:** extra
"""
    (script_dir / "easy.md").write_text(script_content, encoding="utf-8")

    # preset_index.json
    preset_index = {"preset_ids": BASE_CTX.get("preset_ids", [])}
    (adhyay_dir / "preset_index.json").write_text(json.dumps(preset_index), encoding="utf-8")

    # voice_library.json
    voice_lib = {"saved_voices": BASE_CTX.get("saved_voices", {})}
    (adhyay_dir / "voice_library.json").write_text(json.dumps(voice_lib), encoding="utf-8")

    # no sound palette
    return tmp_path

# ----------------------------------------------------------------------
# Fake caller that replays base documents
# ----------------------------------------------------------------------
class FakeCaller:
    def __init__(self, base_docs: Dict[str, Any], base_ctx: Dict[str, Any]):
        self.base_docs = base_docs
        self.base_ctx = base_ctx
        self.call_count = 0
        self.calls: List[str] = []

    def __call__(self, call_name: str, system: str, user: str) -> Tuple[str, Dict[str, Any]]:
        self.call_count += 1
        self.calls.append(call_name)
        info = {"status": 200, "wall_s": 0.1, "finish": "stop", "usage": {"prompt_tokens": 10, "completion_tokens": 20}}
        if call_name == "map":
            reply = json.dumps({"story_map": self.base_docs["story_map"]})
        elif call_name == "plan":
            reply = json.dumps({
                "coverage": self.base_docs["coverage"],
                "scenes": self.base_docs["scenes"]
            })
        elif call_name.startswith("scene_"):
            # Extract scene ids from the call name? We'll filter by scene_id in the base docs.
            # For simplicity, we return the full docs for the first scene call, empty for others.
            # But the spec says: filter lists by scene_id; looks and voices are not per scene: give them whole in the first scene call and empty lists afterwards.
            # We'll need to know which scene ids this call is for. Since we don't have them here, we'll assume the first scene call gets all, others empty.
            # However, the test will control scene_group and only_scenes. We'll make a more sophisticated fake that uses the scene_ids from the prompt? 
            # Instead, we'll make the fake caller stateful: it expects to be called in order and we'll pass the scene groups via a closure.
            # But the fake caller is created per test. We'll instead create a factory that knows the scene groups.
            raise NotImplementedError("Fake caller for scene calls needs scene groups")
        else:
            reply = "{}"
        return reply, info

def make_fake_caller(base_docs: Dict[str, Any], base_ctx: Dict[str, Any], scene_groups: List[List[str]]):
    """Return a caller that returns appropriate replies for each call in order."""
    call_index = 0
    scene_call_index = 0

    def caller(call_name: str, system: str, user: str) -> Tuple[str, Dict[str, Any]]:
        nonlocal call_index, scene_call_index
        call_index += 1
        info = {"status": 200, "wall_s": 0.1, "finish": "stop", "usage": {"prompt_tokens": 10, "completion_tokens": 20}}
        if call_name == "map":
            reply = json.dumps({"story_map": base_docs["story_map"]})
        elif call_name == "plan":
            reply = json.dumps({
                "coverage": base_docs["coverage"],
                "scenes": base_docs["scenes"]
            })
        elif call_name.startswith("scene_"):
            if scene_call_index < len(scene_groups):
                group = scene_groups[scene_call_index]
                scene_call_index += 1
                # Build reply with filtered docs
                shots = [s for s in base_docs["shots"]["shots"] if s.get("scene_id") in group]
                briefs = [b for b in base_docs["briefs"]["images"] if b.get("scene_id") in group]
                # looks and voices: whole in first scene call, empty afterwards
                if scene_call_index == 1:
                    looks = base_docs["looks"]["entries"]
                    voices = base_docs["voices"]["cast"]
                else:
                    looks = []
                    voices = []
                sounds = [c for c in base_docs["sounds"]["cues"] if c.get("scene_id") in group]
                questions = [q for q in base_docs["questions"]["questions"] if q.get("scene_id") in group]
                reply = json.dumps({
                    "shots": {"adhyay": 2, "shots": shots},
                    "briefs": {"adhyay": 2, "images": briefs},
                    "looks": {"adhyay": 2, "entries": looks},
                    "voices": {"adhyay": 2, "cast": voices},
                    "sounds": {"adhyay": 2, "cues": sounds},
                    "questions": {"adhyay": 2, "questions": questions}
                })
            else:
                reply = json.dumps({
                    "shots": {"adhyay": 2, "shots": []},
                    "briefs": {"adhyay": 2, "images": []},
                    "looks": {"adhyay": 2, "entries": []},
                    "voices": {"adhyay": 2, "cast": []},
                    "sounds": {"adhyay": 2, "cues": []},
                    "questions": {"adhyay": 2, "questions": []}
                })
        else:
            reply = "{}"
        return reply, info
    return caller

# ----------------------------------------------------------------------
# Test fixtures
# ----------------------------------------------------------------------
@pytest.fixture
def synthetic_root(tmp_path: Path) -> Path:
    return build_synthetic_root(tmp_path)

# ----------------------------------------------------------------------
# Test parse_reply
# ----------------------------------------------------------------------
def test_parse_reply_fenced_json():
    text = "```json\n{\"story_map\": {\"adhyay\": 2}}\n```"
    obj, probs = runner.parse_reply(text, ("story_map",), 2)
    assert obj is not None
    assert obj["story_map"]["adhyay"] == 2
    assert probs == []

def test_parse_reply_prose_around():
    text = "Here is the JSON: {\"story_map\": {}} and that's it."
    obj, probs = runner.parse_reply(text, ("story_map",), 2)
    assert obj is not None
    assert obj["story_map"]["adhyay"] == 2
    assert probs == []

def test_parse_reply_no_json():
    text = "no json here"
    obj, probs = runner.parse_reply(text, ("story_map",), 2)
    assert obj is None
    assert "reply: no json object" in probs

def test_parse_reply_bad_json():
    text = "{\"story_map\": {"
    obj, probs = runner.parse_reply(text, ("story_map",), 2)
    assert obj is None
    assert "reply: bad json" in probs

def test_parse_reply_array():
    text = "[1,2,3]"
    obj, probs = runner.parse_reply(text, ("story_map",), 2)
    assert obj is None
    assert "reply: not an object" in probs

def test_parse_reply_missing_key():
    text = "{\"other\": {}}"
    obj, probs = runner.parse_reply(text, ("story_map",), 2)
    assert obj is not None
    assert "reply: missing key story_map" in probs

def test_parse_reply_extra_key():
    text = "{\"story_map\": {}, \"extra\": 1}"
    obj, probs = runner.parse_reply(text, ("story_map",), 2)
    assert obj is not None
    assert "reply: unexpected key extra" in probs

def test_parse_reply_adhyay_mismatch():
    text = "{\"story_map\": {\"adhyay\": 3}}"
    obj, probs = runner.parse_reply(text, ("story_map",), 2)
    assert obj is not None
    assert "story_map: adhyay 3 is not 2" in probs

def test_parse_reply_adhyay_filled():
    text = "{\"story_map\": {}}"
    obj, probs = runner.parse_reply(text, ("story_map",), 2)
    assert obj is not None
    assert obj["story_map"]["adhyay"] == 2
    assert probs == []

# ----------------------------------------------------------------------
# Test merge_scene_parts
# ----------------------------------------------------------------------
def test_merge_scene_parts_concatenation_order():
    parts = [
        {"shots": {"adhyay": 2, "shots": [{"id": "S1"}]}, "briefs": {"adhyay": 2, "images": [{"id": "B1"}]}},
        {"shots": {"adhyay": 2, "shots": [{"id": "S2"}]}, "briefs": {"adhyay": 2, "images": [{"id": "B2"}]}}
    ]
    merged = runner.merge_scene_parts(2, parts)
    assert [s["id"] for s in merged["shots"]["shots"]] == ["S1", "S2"]
    assert [b["id"] for b in merged["briefs"]["images"]] == ["B1", "B2"]

def test_merge_scene_parts_dedupe_looks():
    parts = [
        {"looks": {"adhyay": 2, "entries": [{"entity_id": "e1", "state_id": "s1", "data": 1}]}},
        {"looks": {"adhyay": 2, "entries": [{"entity_id": "e1", "state_id": "s1", "data": 2}, {"entity_id": "e2", "state_id": "s2", "data": 3}]}}
    ]
    merged = runner.merge_scene_parts(2, parts)
    assert len(merged["looks"]["entries"]) == 2
    assert merged["looks"]["entries"][0]["data"] == 1  # first kept
    assert merged["looks"]["entries"][1]["entity_id"] == "e2"

def test_merge_scene_parts_dedupe_voices():
    parts = [
        {"voices": {"adhyay": 2, "cast": [{"character_id": "c1", "voice": "v1"}]}},
        {"voices": {"adhyay": 2, "cast": [{"character_id": "c1", "voice": "v2"}, {"character_id": "c2", "voice": "v3"}]}}
    ]
    merged = runner.merge_scene_parts(2, parts)
    assert len(merged["voices"]["cast"]) == 2
    assert merged["voices"]["cast"][0]["voice"] == "v1"
    assert merged["voices"]["cast"][1]["character_id"] == "c2"

def test_merge_scene_parts_questions_renumbered():
    parts = [
        {"questions": {"adhyay": 2, "questions": [{"text": "q1", "scene_id": "S1"}, {"text": "q2", "scene_id": "S1"}]}},
        {"questions": {"adhyay": 2, "questions": [{"text": "q3", "scene_id": "S2"}]}}
    ]
    merged = runner.merge_scene_parts(2, parts)
    assert [q["id"] for q in merged["questions"]["questions"]] == ["Q1", "Q2", "Q3"]
    assert [q["text"] for q in merged["questions"]["questions"]] == ["q1", "q2", "q3"]

def test_merge_scene_parts_malformed_part_skipped():
    parts = [
        {"shots": {"adhyay": 2, "shots": [{"id": "S1"}]}},
        "not a dict",
        {"shots": {"adhyay": 2, "shots": [{"id": "S2"}]}}
    ]
    merged = runner.merge_scene_parts(2, parts)
    assert [s["id"] for s in merged["shots"]["shots"]] == ["S1", "S2"]

# ----------------------------------------------------------------------
# Test run_stage1 end-to-end with fake caller
# ----------------------------------------------------------------------
def test_run_stage1_end_to_end(synthetic_root: Path, tmp_path: Path):
    out_dir = tmp_path / "out"
    # Determine scene groups: two scenes S1, S2, scene_group=1 -> two scene calls
    scene_groups = [["S1"], ["S2"]]
    fake_caller = make_fake_caller(BASE_DOCS, BASE_CTX, scene_groups)
    report = runner.run_stage1(
        adhyay=2,
        root=synthetic_root,
        caller=fake_caller,
        out_dir=out_dir,
        scene_group=1,
        only_scenes=None,
        provider_name="test",
        dry_run=False,
    )
    # Check calls
    assert fake_caller.call_count == 4  # map, plan, scene_01, scene_02
    assert [c["name"] for c in report["calls"]] == ["map", "plan", "scene_01", "scene_02"]
    for call in report["calls"]:
        assert call["status"] == "ok"
    # Nine documents written
    assert len(report["documents_written"]) == 9
    assert set(report["documents_written"]) == set(runner.aggregate_mod.UNITS)  # type: ignore[attr-defined]
    # Aggregate errors empty
    assert report["aggregate_errors"] == []
    # Counts
    assert report["counts"]["ovis"] == 9
    assert report["counts"]["script_lines"] == 3
    assert report["counts"]["scenes"] == 2
    # Prompts and replies files exist
    prompts_dir = out_dir / "prompts"
    replies_dir = out_dir / "replies"
    assert (prompts_dir / "map.txt").exists()
    assert (prompts_dir / "plan.txt").exists()
    assert (prompts_dir / "scene_01.txt").exists()
    assert (prompts_dir / "scene_02.txt").exists()
    assert (replies_dir / "map.txt").exists()
    assert (replies_dir / "plan.txt").exists()
    assert (replies_dir / "scene_01.txt").exists()
    assert (replies_dir / "scene_02.txt").exists()

def test_run_stage1_scene_group_2(synthetic_root: Path, tmp_path: Path):
    out_dir = tmp_path / "out2"
    scene_groups = [["S1", "S2"]]
    fake_caller = make_fake_caller(BASE_DOCS, BASE_CTX, scene_groups)
    report = runner.run_stage1(
        adhyay=2,
        root=synthetic_root,
        caller=fake_caller,
        out_dir=out_dir,
        scene_group=2,
        only_scenes=None,
        provider_name="test",
        dry_run=False,
    )
    assert fake_caller.call_count == 3  # map, plan, scene_01
    assert [c["name"] for c in report["calls"]] == ["map", "plan", "scene_01"]
    for call in report["calls"]:
        assert call["status"] == "ok"

# ----------------------------------------------------------------------
# Test failure handling
# ----------------------------------------------------------------------
def test_run_stage1_map_invalid_json(synthetic_root: Path, tmp_path: Path):
    out_dir = tmp_path / "out3"
    def bad_caller(call_name: str, system: str, user: str) -> Tuple[str, Dict[str, Any]]:
        if call_name == "map":
            return "not json", {"status": 200, "wall_s": 0.1, "finish": "stop", "usage": {}}
        raise AssertionError("Should not be called")
    report = runner.run_stage1(
        adhyay=2,
        root=synthetic_root,
        caller=bad_caller,
        out_dir=out_dir,
        scene_group=1,
        only_scenes=None,
        provider_name="test",
        dry_run=False,
    )
    assert report["calls"][0]["status"] == "failed"
    assert report["calls"][0]["reason"] == "parse failed"
    # plan and scene should be skipped (not in calls)
    assert len(report["calls"]) == 1
    # Report written
    assert (out_dir / "report.json").exists()

def test_run_stage1_caller_raises(synthetic_root: Path, tmp_path: Path):
    out_dir = tmp_path / "out4"
    def raising_caller(call_name: str, system: str, user: str) -> Tuple[str, Dict[str, Any]]:
        raise ValueError("boom")
    report = runner.run_stage1(
        adhyay=2,
        root=synthetic_root,
        caller=raising_caller,
        out_dir=out_dir,
        scene_group=1,
        only_scenes=None,
        provider_name="test",
        dry_run=False,
    )
    assert report["calls"][0]["status"] == "failed"
    assert "ValueError" in report["calls"][0]["reason"]
    assert len(report["calls"]) == 1

def test_run_stage1_plan_schema_error(synthetic_root: Path, tmp_path: Path):
    out_dir = tmp_path / "out5"
    def caller_with_bad_plan(call_name: str, system: str, user: str) -> Tuple[str, Dict[str, Any]]:
        if call_name == "map":
            return json.dumps({"story_map": BASE_DOCS["story_map"]}), {"status": 200, "wall_s": 0.1, "finish": "stop", "usage": {}}
        elif call_name == "plan":
            # Return a scenes document that violates schema (missing required field)
            return json.dumps({"coverage": BASE_DOCS["coverage"], "scenes": {"scenes": [123]}}), {"status": 200, "wall_s": 0.1, "finish": "stop", "usage": {}}
        raise AssertionError("Should not be called")
    report = runner.run_stage1(
        adhyay=2,
        root=synthetic_root,
        caller=caller_with_bad_plan,
        out_dir=out_dir,
        scene_group=1,
        only_scenes=None,
        provider_name="test",
        dry_run=False,
    )
    statuses = {c["name"]: c["status"] for c in report["calls"]}
    assert statuses["map"] == "ok"
    assert statuses["plan"] == "failed"
    assert "schema errors" in report["calls"][1]["reason"]
    # No scene calls
    assert len(report["calls"]) == 2

def test_run_stage1_status_500(synthetic_root: Path, tmp_path: Path):
    out_dir = tmp_path / "out6"
    def caller_500(call_name: str, system: str, user: str) -> Tuple[str, Dict[str, Any]]:
        return "{}", {"status": 500, "wall_s": 0.1, "finish": "error", "usage": {}, "error": "server error"}
    report = runner.run_stage1(
        adhyay=2,
        root=synthetic_root,
        caller=caller_500,
        out_dir=out_dir,
        scene_group=1,
        only_scenes=None,
        provider_name="test",
        dry_run=False,
    )
    assert report["calls"][0]["status"] == "failed"
    assert "status 500" in report["calls"][0]["reason"]

# ----------------------------------------------------------------------
# Test dry_run
# ----------------------------------------------------------------------
def test_run_stage1_dry_run(synthetic_root: Path, tmp_path: Path):
    out_dir = tmp_path / "out_dry"
    # Caller that fails if called
    def failing_caller(call_name: str, system: str, user: str) -> Tuple[str, Dict[str, Any]]:
        raise AssertionError("Caller should not be invoked in dry_run")
    report = runner.run_stage1(
        adhyay=2,
        root=synthetic_root,
        caller=failing_caller,
        out_dir=out_dir,
        scene_group=1,
        only_scenes=None,
        provider_name="dry-run",
        dry_run=True,
    )
    # Should have map, plan, scene_01, scene_02 (two scenes)
    assert len(report["calls"]) == 4
    for call in report["calls"]:
        assert call["status"] == "dry-run"
    # Prompts written
    prompts_dir = out_dir / "prompts"
    assert (prompts_dir / "map.txt").exists()
    assert (prompts_dir / "plan.txt").exists()
    assert (prompts_dir / "scene_01.txt").exists()
    assert (prompts_dir / "scene_02.txt").exists()
    # No replies directory? Actually replies dir is created but empty? The spec says only prompt files and report are written.
    # Our implementation creates replies dir but doesn't write files. That's fine.

def test_run_stage1_out_dir_exists_nonempty(synthetic_root: Path, tmp_path: Path):
    out_dir = tmp_path / "out_exist"
    out_dir.mkdir()
    (out_dir / "dummy.txt").write_text("x")
    with pytest.raises(FileExistsError):
        runner.run_stage1(
            adhyay=2,
            root=synthetic_root,
            caller=None,
            out_dir=out_dir,
            dry_run=True,
        )

def test_run_stage1_invalid_adhyay(synthetic_root: Path, tmp_path: Path):
    out_dir = tmp_path / "out_inv"
    with pytest.raises(ValueError):
        runner.run_stage1(
            adhyay=0,
            root=synthetic_root,
            caller=None,
            out_dir=out_dir,
            dry_run=True,
        )

# ----------------------------------------------------------------------
# Test main function
# ----------------------------------------------------------------------
def test_main_kimi_refusal(capsys, synthetic_root: Path, tmp_path: Path):
    out_dir = tmp_path / "out_kimi"
    # We need to call main with argv
    # Since main uses argparse, we can call it directly
    exit_code = runner.main([
        "--adhyay", "2",
        "--root", str(synthetic_root),
        "--out", str(out_dir),
        "--provider", "kimi"
    ])
    assert exit_code == 2
    captured = capsys.readouterr()
    assert "refused: Kimi calls need the credit ledger and the owner's go; not available in this module" in captured.out

def test_main_dry_run(synthetic_root: Path, tmp_path: Path):
    out_dir = tmp_path / "out_main_dry"
    exit_code = runner.main([
        "--adhyay", "2",
        "--root", str(synthetic_root),
        "--out", str(out_dir),
        "--provider", "dry-run"
    ])
    assert exit_code == 0
    assert (out_dir / "prompts" / "map.txt").exists()
    assert (out_dir / "report.json").exists()

def test_main_missing_args():
    # argparse will raise SystemExit
    with pytest.raises(SystemExit):
        runner.main([])

# ----------------------------------------------------------------------
# Source-level test: no kimi_adapter import, no nvapi- literal
# ----------------------------------------------------------------------
def test_source_no_kimi_adapter():
    source = RUNNER_PATH.read_text(encoding="utf-8")
    assert "kimi_adapter" not in source
    assert "nvapi-" not in source

# ----------------------------------------------------------------------
# Test secrets scrubbing
# ----------------------------------------------------------------------
def test_secrets_scrubbed(synthetic_root: Path, tmp_path: Path):
    out_dir = tmp_path / "out_secrets"
    fake_key = "***"
    def caller_with_key(call_name: str, system: str, user: str) -> Tuple[str, Dict[str, Any]]:
        # Return a reply containing the fake key
        reply = json.dumps({"story_map": {"adhyay": 2, "secret": fake_key}})
        return reply, {"status": 200, "wall_s": 0.1, "finish": "stop", "usage": {}}
    report = runner.run_stage1(
        adhyay=2,
        root=synthetic_root,
        caller=caller_with_key,
        out_dir=out_dir,
        scene_group=1,
        only_scenes=None,
        provider_name="test",
        dry_run=False,
        scrub_keys=[fake_key],
    )
    # Check that the reply file does not contain the key
    reply_file = out_dir / "replies" / "map.txt"
    assert reply_file.exists()
    content = reply_file.read_text(encoding="utf-8")
    assert fake_key not in content
    assert "[REDACTED]" in content
    # Check report.json
    report_file = out_dir / "report.json"
    report_content = report_file.read_text(encoding="utf-8")
    assert fake_key not in report_content
    assert "[REDACTED]" in report_content
    # Also check that the key is not in any other written document
    for doc_file in out_dir.glob("*.json"):
        doc_content = doc_file.read_text(encoding="utf-8")
        assert fake_key not in doc_content

```

## DIAGNOSIS of the 10 failing tests (verified by running them). Fix the MODULE for 1-4 and the clarified spec point 5; fix a TEST only where stated. Return BOTH complete FILE blocks.
1. `AttributeError: module 'aggregate' has no attribute 'schema_errors'` (end_to_end, scene_group_2, plan_schema_error, secrets_scrubbed): the runner calls `schema_errors` on the aggregate module. `schema_errors(doc)` lives on each UNIT module: load `scripts/pipeline/stage1/<unit>.py` BY PATH (a small helper with a module-level cache, unit in story_map, coverage, scenes, shots, briefs, looks, voices, sounds, questions) and call `unit.schema_errors(document)` for the document of that unit. `aggregate` only offers `validate_all` and `UNITS`.
2. `ValueError: boom` escapes in test_run_stage1_caller_raises: the SPEC says any exception inside a caller is caught and recorded as a failed call (`reason: <ExceptionClass>` or `error: <ExceptionClass>`); wrap EVERY caller invocation in try/except Exception and never let it out of run_stage1.
3. `KeyError: 'ovis'` at the counts step (map_invalid_json, status_500): when the map failed the packet or documents may be incomplete; build the report counts with `.get(..., [])` everywhere; counts of missing documents are 0. Never index a key that may be absent.
4. test_run_stage1_dry_run: the dry run wrote only 2 prompts (map, plan) instead of 4 (map, plan, scene_01, scene_02). SPEC: with dry_run the scene prompts ARE written, scene ids taken from the script headings (`parse_script` scene ids in order, `only_scenes` filter, grouped by `scene_group`), using the empty placeholder priors named in the spec.
5. parse_reply clarification (the spec was ambiguous): first try `json.loads(text.strip())` on the whole stripped text; if that succeeds and the value is NOT a dict return `(None, ["reply: not an object"])`; if it is a dict use it. Otherwise (the whole text is not JSON) take the substring from the first `{` to the last `}`; if there is no `{` or no `}` -> `reply: no json object`; if json.loads of the substring fails -> `reply: bad json`. So: text `[1, 2]` -> `reply: not an object`; text `{"a": }` -> `reply: bad json`; text `no braces here` -> `reply: no json object`; prose around a valid object, and fenced JSON, still work. Update test_parse_reply_bad_json and test_parse_reply_array to these three inputs.
