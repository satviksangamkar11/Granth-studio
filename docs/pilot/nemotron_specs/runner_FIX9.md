# TASK: return ONLY ONE FILE: tests/test_stage1_runner.py (complete). Reply with exactly one block `FILE: tests/test_stage1_runner.py` then the python fenced. The module is correct. ONE test fails (test_run_stage1_end_to_end): the fake caller replays the shared base documents, whose `adhyay` field is 1, but the test runs Adhyay 2, so the runner correctly reports 'story_map adhyay 1 does not match 2'. FIX THE TEST: when the fake caller builds each reply (and in any helper that builds the documents), deep-copy the base documents and set `doc['adhyay'] = 2` on EVERY document (story_map, coverage, scenes, shots, briefs, looks, voices, sounds, questions) before returning them; also use adhyay 2 for the context. Keep all other tests unchanged.
```
E   AssertionError: assert ['story_map a...ic_push', ...] == []
E     
E     Left contains 11 more items, first extra item: 'story_map adhyay 1 does not match 2'
E     Use -v to get more diff
```
## CURRENT tests/test_stage1_runner.py
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

# Load aggregate module for UNITS
AGGREGATE_PATH = REPO_ROOT / "scripts" / "pipeline" / "stage1" / "aggregate.py"
aggregate_mod = _load_module_by_path("aggregate", AGGREGATE_PATH)

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
    script_content = """# Adhyay 2 test script

## S1
**S1-L1** | narrator | ovi 1 | core
- Marathi: मराठी 1
- Hindi: हिंदी 1

**S1-L2** | gajanan_maharaj | ovi 3 | core
- Marathi: मराठी 3
- Hindi: हिंदी 3

## S2
**S2-L1** | narrator | ovi 7 | core
- Marathi: मराठी 7
- Hindi: हिंदी 7
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
def make_fake_caller(base_docs: Dict[str, Any], base_ctx: Dict[str, Any], scene_groups: List[List[str]]):
    """Return a caller that returns appropriate replies for each call in order."""
    call_counter = [0]
    scene_call_index = [0]

    def caller(call_name: str, system: str, user: str) -> Tuple[str, Dict[str, Any]]:
        call_counter[0] += 1
        info = {"status": 200, "wall_s": 0.1, "finish": "stop", "usage": {"prompt_tokens": 10, "completion_tokens": 20}}
        if call_name == "map":
            reply = json.dumps({"story_map": base_docs["story_map"]})
        elif call_name == "plan":
            reply = json.dumps({
                "coverage": base_docs["coverage"],
                "scenes": base_docs["scenes"]
            })
        elif call_name.startswith("scene_"):
            if scene_call_index[0] < len(scene_groups):
                group = scene_groups[scene_call_index[0]]
                scene_call_index[0] += 1
                # Build reply with filtered docs
                shots = [s for s in base_docs["shots"]["shots"] if s.get("scene_id") in group]
                briefs = [b for b in base_docs["briefs"]["images"] if b.get("scene_id") in group]
                # looks and voices: whole in first scene call, empty afterwards
                if scene_call_index[0] == 1:
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
    # Attach call_counter to the function for test access
    caller.call_counter = call_counter
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
    text = "{\"a\": }"  # invalid JSON but has closing brace
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
    assert fake_caller.call_counter[0] == 4  # map, plan, scene_01, scene_02
    assert [c["name"] for c in report["calls"]] == ["map", "plan", "scene_01", "scene_02"]
    for call in report["calls"]:
        assert call["status"] == "ok"
    # Nine documents written
    assert len(report["documents_written"]) == 9
    assert set(report["documents_written"]) == set(aggregate_mod.UNITS)
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
    assert fake_caller.call_counter[0] == 3  # map, plan, scene_01
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
    assert "error: ValueError" in report["calls"][0]["reason"]
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
    assert report["calls"][0]["info"]["status"] == 500
    assert isinstance(report["calls"][0]["reason"], str) and report["calls"][0]["reason"] != ""

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
    # Check report.json
    report_file = out_dir / "report.json"
    report_content = report_file.read_text(encoding="utf-8")
    assert fake_key not in report_content
    # Also check that the key is not in any other written document
    for doc_file in out_dir.glob("*.json"):
        doc_content = doc_file.read_text(encoding="utf-8")
        assert fake_key not in doc_content
    # Check prompts directory as well
    for prompt_file in (out_dir / "prompts").glob("*.txt"):
        prompt_content = prompt_file.read_text(encoding="utf-8")
        assert fake_key not in prompt_content
```
