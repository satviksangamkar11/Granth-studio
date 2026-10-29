from __future__ import annotations

import json
import sys
from pathlib import Path
from copy import deepcopy

import pytest


def load_module(name: str, path: Path):
    from importlib.util import spec_from_file_location, module_from_spec

    spec = spec_from_file_location(name, path)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


REPO_ROOT = Path(__file__).resolve().parents[1]
CROSSCHECK_PATH = REPO_ROOT / "scripts" / "pipeline" / "stage1" / "crosscheck.py"
PROMPTS_PATH = REPO_ROOT / "scripts" / "pipeline" / "stage1" / "prompts.py"
RUNNER_PATH = REPO_ROOT / "scripts" / "pipeline" / "stage1" / "runner.py"

crosscheck = load_module("crosscheck", CROSSCHECK_PATH)
prompts = load_module("prompts", PROMPTS_PATH)
runner = load_module("runner", RUNNER_PATH)


@pytest.fixture
def base_docs_and_ctx(tmp_path: Path):
    base_file = REPO_ROOT / "docs" / "pilot" / "nemotron_specs" / "stage1_base.json"
    with base_file.open("r", encoding="utf-8") as f:
        data = json.load(f)
    docs = deepcopy(data["docs"])
    ctx = deepcopy(data["ctx"])

    for unit in docs:
        if isinstance(docs[unit], dict):
            docs[unit]["adhyay"] = 2

    stage1_dir = tmp_path / "stage1"
    stage1_dir.mkdir()
    for unit, content in docs.items():
        (stage1_dir / f"{unit}.json").write_text(json.dumps(content), encoding="utf-8")

    root = tmp_path / "root"
    canon = root / "canon" / "adhyay_02"
    (canon / "source").mkdir(parents=True)
    (canon / "script").mkdir(parents=True)

    ovis_lines = []
    for i in range(1, 10):
        ovis_lines.append(json.dumps({"adhyay": 2, "ovi": i, "text": f"OVI {i} content", "type": "event"}))
    (canon / "source" / "ovis.jsonl").write_text("\n".join(ovis_lines), encoding="utf-8")

    easy_md = (
        "## S1\n"
        "**S1-L1** | narrator | ovi 1 | core\n"
        "- Marathi: मराठी लाइन १\n"
        "- Hindi: हिंदी लाइन १\n"
        "**S1-L2** | narrator | ovi 2 | core\n"
        "- Marathi: मराठी लाइन २\n"
        "- Hindi: हिंदी लाइन २\n"
        "## S2\n"
        "**S2-L1** | narrator | ovi 3 | core\n"
        "- Marathi: मराठी लाइन ३\n"
        "- Hindi: हिंदी लाइन ३\n"
    )
    (canon / "script" / "easy.md").write_text(easy_md, encoding="utf-8")

    preset_index = {
        "presets": [
            {"id": "01", "name": "wide", "limits": {}},
            {"id": "06", "name": "hand_raise", "limits": {"cannot_raise_lowered_hand": True}},
            {"id": "09", "name": "lip_sync", "limits": {"cannot_lip_sync": True}},
        ]
    }
    (root / "preset_index.json").write_text(json.dumps(preset_index), encoding="utf-8")

    voice_lib = {
        "voices": [
            {"id": "v1", "name": "Narrator", "description": "calm male"},
            {"id": "v2", "name": "Krishna", "description": "deep resonant"},
        ]
    }
    (root / "voice_library.json").write_text(json.dumps(voice_lib), encoding="utf-8")

    return stage1_dir, root, docs, ctx


def test_scene_slice(base_docs_and_ctx):
    stage1_dir, root, docs, ctx = base_docs_and_ctx
    packet, _ = prompts.build_packet(2, root)

    slice_s1 = crosscheck.scene_slice(docs, packet, "S1")
    assert slice_s1["scene"].get("scene_id") == "S1"
    assert len(slice_s1["script_lines"]) == 2
    assert all(l["id"] in ("S1-L1", "S1-L2") for l in slice_s1["script_lines"])
    # The base file's S1 has ovi_range [1,5] so we expect 5 ovis (1..5)
    assert len(slice_s1["ovis"]) == 5
    assert all(o["ovi"] in (1, 2, 3, 4, 5) for o in slice_s1["ovis"])
    assert all(s.get("scene_id") == "S1" for s in slice_s1["shots"])
    assert all(b.get("scene_id") == "S1" for b in slice_s1["briefs"])
    assert all(c.get("scene_id") == "S1" for c in slice_s1["cues"])
    assert all(q.get("scene_id") == "S1" for q in slice_s1["questions"])

    slice_s2 = crosscheck.scene_slice(docs, packet, "S2")
    assert slice_s2["scene"].get("scene_id") == "S2"
    assert len(slice_s2["script_lines"]) == 1
    assert slice_s2["script_lines"][0]["id"] == "S2-L1"
    # The base file's S2 has ovi_range [6,9] so we expect 4 ovis (6..9)
    assert len(slice_s2["ovis"]) == 4
    assert all(o["ovi"] in (6, 7, 8, 9) for o in slice_s2["ovis"])

    slice_unknown = crosscheck.scene_slice(docs, packet, "S99")
    assert slice_unknown["scene"] == {}
    assert slice_unknown["script_lines"] == []
    assert slice_unknown["ovis"] == []

    slice_bad = crosscheck.scene_slice("not a dict", packet, "S1")
    assert slice_bad["scene"] == {}
    assert slice_bad["script_lines"] == []

    huge_range_docs = deepcopy(docs)
    huge_range_docs["scenes"]["scenes"][0]["ovi_range"] = [1, 10**12]
    slice_huge = crosscheck.scene_slice(huge_range_docs, packet, "S1")
    assert len(slice_huge["ovis"]) == 9


def test_scene_slice_odd_data_no_raise(base_docs_and_ctx):
    """Defect 1: scene_slice must never raise on odd data; return empty slice."""
    stage1_dir, root, docs, ctx = base_docs_and_ctx
    packet, _ = prompts.build_packet(2, root)

    # ovi_range: None
    bad_docs = deepcopy(docs)
    bad_docs["scenes"]["scenes"][0]["ovi_range"] = None
    slice_ = crosscheck.scene_slice(bad_docs, packet, "S1")
    assert slice_["ovis"] == []

    # ovi_range: ["a","b"]
    bad_docs = deepcopy(docs)
    bad_docs["scenes"]["scenes"][0]["ovi_range"] = ["a", "b"]
    slice_ = crosscheck.scene_slice(bad_docs, packet, "S1")
    assert slice_["ovis"] == []

    # line_ids: None
    bad_docs = deepcopy(docs)
    bad_docs["scenes"]["scenes"][0]["line_ids"] = None
    slice_ = crosscheck.scene_slice(bad_docs, packet, "S1")
    assert slice_["script_lines"] == []

    # scenes: None (top-level scenes key missing or not a dict)
    bad_docs = deepcopy(docs)
    bad_docs["scenes"] = None
    slice_ = crosscheck.scene_slice(bad_docs, packet, "S1")
    assert slice_["scene"] == {}
    assert slice_["script_lines"] == []
    assert slice_["ovis"] == []


def test_build_check_prompt(base_docs_and_ctx):
    stage1_dir, root, docs, ctx = base_docs_and_ctx
    packet, _ = prompts.build_packet(2, root)
    slice_s1 = crosscheck.scene_slice(docs, packet, "S1")
    system, user = crosscheck.build_check_prompt(2, "S1", slice_s1)

    assert "read-only reviewer" in system
    assert crosscheck.CHECK_RULES in system
    assert "PASS" in system and "BLOCK" in system
    assert "problems" in system
    assert user.startswith("SCENE S1\n")
    assert "S1-L1" in user
    assert "nvapi-" not in system
    assert "nvapi-" not in user


def test_parse_verdict():
    valid_pass = '{"scene_id": "S1", "verdict": "PASS", "problems": []}'
    obj, probs = crosscheck.parse_verdict(valid_pass, "S1")
    assert obj is not None
    assert obj["verdict"] == "PASS"
    assert probs == []

    valid_block = '{"scene_id": "S1", "verdict": "BLOCK", "problems": [{"where": "S1-1", "what": "missing teaching"}]}'
    obj, probs = crosscheck.parse_verdict(valid_block, "S1")
    assert obj is not None
    assert obj["verdict"] == "BLOCK"
    assert probs == []

    fenced = "```json\n" + valid_pass + "\n```"
    obj, probs = crosscheck.parse_verdict(fenced, "S1")
    assert obj is not None
    assert probs == []

    prose = "Here is the result:\n" + valid_pass + "\nEnd."
    obj, probs = crosscheck.parse_verdict(prose, "S1")
    assert obj is not None
    assert probs == []

    obj, probs = crosscheck.parse_verdict("no json here", "S1")
    assert obj is None
    assert "no json object found" in probs

    obj, probs = crosscheck.parse_verdict("{not valid json}", "S1")
    assert obj is None
    assert "bad json" in probs

    obj, probs = crosscheck.parse_verdict('{"scene_id": "S1", "verdict": "MAYBE", "problems": []}', "S1")
    assert obj is not None
    assert "verdict: invalid" in probs

    obj, probs = crosscheck.parse_verdict('{"scene_id": "S1", "verdict": "PASS", "problems": [{"where": "S1-1", "what": "x"}]}', "S1")
    assert obj is not None
    assert "verdict: inconsistent" in probs

    obj, probs = crosscheck.parse_verdict('{"scene_id": "S1", "verdict": "BLOCK", "problems": []}', "S1")
    assert obj is not None
    assert "verdict: inconsistent" in probs

    obj, probs = crosscheck.parse_verdict('{"scene_id": "S1", "verdict": "BLOCK", "problems": [{"where": 1, "what": "x"}]}', "S1")
    assert obj is not None
    assert "problems: invalid" in probs

    obj, probs = crosscheck.parse_verdict('{"scene_id": "S2", "verdict": "PASS", "problems": []}', "S1")
    assert obj is not None
    assert "scene_id: mismatch" in probs


def test_run_crosscheck_fake_caller(base_docs_and_ctx, tmp_path: Path):
    stage1_dir, root, docs, ctx = base_docs_and_ctx
    out_dir = tmp_path / "out"

    def fake_caller(call_name, system, user):
        if "S1" in user:
            reply = '{"scene_id": "S1", "verdict": "PASS", "problems": []}'
        else:
            reply = '{"scene_id": "S2", "verdict": "BLOCK", "problems": [{"where": "S2-1", "what": "missing teaching"}]}'
        return reply, {"status": 200, "wall_s": 0.1, "finish": "stop", "error": None}

    units = ["story_map", "coverage", "scenes", "shots", "briefs", "looks",
             "voices", "sounds", "questions"]
    before_snapshots = {unit: (stage1_dir / f"{unit}.json").read_bytes() for unit in units}

    result = crosscheck.run_crosscheck(2, stage1_dir, root, fake_caller, out_dir)
    assert result["adhyay"] == 2
    assert result["advisory"] is True
    assert result["note"] == "advice only; nothing was changed"
    assert result["summary"]["pass"] == 1
    assert result["summary"]["block"] == 1
    assert result["summary"]["failed"] == 0
    assert len(result["scenes"]) == 2
    assert result["scenes"][0]["status"] == "ok"
    assert result["scenes"][0]["verdict"] == "PASS"
    assert result["scenes"][1]["status"] == "ok"
    assert result["scenes"][1]["verdict"] == "BLOCK"

    for unit in units:
        after = (stage1_dir / f"{unit}.json").read_bytes()
        assert before_snapshots[unit] == after

    assert (out_dir / "prompts" / "S1.txt").exists()
    assert (out_dir / "prompts" / "S2.txt").exists()
    assert (out_dir / "replies" / "S1.txt").exists()
    assert (out_dir / "replies" / "S2.txt").exists()
    assert (out_dir / "crosscheck.json").exists()


def test_run_crosscheck_caller_raises(base_docs_and_ctx, tmp_path: Path):
    stage1_dir, root, docs, ctx = base_docs_and_ctx
    out_dir = tmp_path / "out2"

    def raising_caller(call_name, system, user):
        if "S1" in user:
            raise RuntimeError("network down")
        return '{"scene_id": "S2", "verdict": "PASS", "problems": []}', {"status": 200, "wall_s": 0.1, "finish": "stop", "error": None}

    result = crosscheck.run_crosscheck(2, stage1_dir, root, raising_caller, out_dir)
    assert result["scenes"][0]["status"] == "failed"
    assert "caller exception" in result["scenes"][0]["parse_problems"][0]
    assert result["scenes"][1]["status"] == "ok"
    assert result["scenes"][1]["verdict"] == "PASS"


def test_run_crosscheck_bad_json_reply(base_docs_and_ctx, tmp_path: Path):
    stage1_dir, root, docs, ctx = base_docs_and_ctx
    out_dir = tmp_path / "out3"

    def bad_json_caller(call_name, system, user):
        return "not json at all", {"status": 200, "wall_s": 0.1, "finish": "stop", "error": None}

    result = crosscheck.run_crosscheck(2, stage1_dir, root, bad_json_caller, out_dir)
    assert result["scenes"][0]["status"] == "failed"
    assert "no json object found" in result["scenes"][0]["parse_problems"][0] or "bad json" in result["scenes"][0]["parse_problems"][0]


def test_run_crosscheck_only_scenes(base_docs_and_ctx, tmp_path: Path):
    stage1_dir, root, docs, ctx = base_docs_and_ctx
    out_dir = tmp_path / "out4"

    def fake_caller(call_name, system, user):
        return '{"scene_id": "S2", "verdict": "PASS", "problems": []}', {"status": 200, "wall_s": 0.1, "finish": "stop", "error": None}

    result = crosscheck.run_crosscheck(2, stage1_dir, root, fake_caller, out_dir, only_scenes=["S2"])
    assert len(result["scenes"]) == 1
    assert result["scenes"][0]["scene_id"] == "S2"


def test_run_crosscheck_dry_run(base_docs_and_ctx, tmp_path: Path):
    stage1_dir, root, docs, ctx = base_docs_and_ctx
    out_dir = tmp_path / "out5"

    result = crosscheck.run_crosscheck(2, stage1_dir, root, None, out_dir, dry_run=True)
    assert result["scenes"][0]["status"] == "dry-run"
    assert result["scenes"][1]["status"] == "dry-run"
    assert (out_dir / "prompts" / "S1.txt").exists()
    assert (out_dir / "prompts" / "S2.txt").exists()
    assert not (out_dir / "replies" / "S1.txt").exists()
    assert result["summary"]["failed"] == 0


def test_run_crosscheck_existing_nonempty_outdir(base_docs_and_ctx, tmp_path: Path):
    stage1_dir, root, docs, ctx = base_docs_and_ctx
    out_dir = tmp_path / "out6"
    out_dir.mkdir()
    (out_dir / "existing.txt").write_text("x")

    with pytest.raises(FileExistsError):
        crosscheck.run_crosscheck(2, stage1_dir, root, None, out_dir, dry_run=True)


def test_run_crosscheck_missing_document_records_problem(base_docs_and_ctx, tmp_path: Path):
    """Defect 3: missing/unreadable document must be recorded in doc_problems."""
    stage1_dir, root, docs, ctx = base_docs_and_ctx
    (stage1_dir / "shots.json").unlink()
    out_dir = tmp_path / "out7"

    def fake_caller(call_name, system, user):
        return '{"scene_id": "S1", "verdict": "PASS", "problems": []}', {"status": 200, "wall_s": 0.1, "finish": "stop", "error": None}

    result = crosscheck.run_crosscheck(2, stage1_dir, root, fake_caller, out_dir)
    assert result["scenes"][0]["status"] == "ok"
    # The fix adds doc_problems key
    assert "doc_problems" in result
    assert any("shots.json" in p for p in result["doc_problems"])


def test_run_crosscheck_unreadable_document_records_problem(base_docs_and_ctx, tmp_path: Path):
    """Defect 3: unreadable (invalid JSON) document must be recorded in doc_problems."""
    stage1_dir, root, docs, ctx = base_docs_and_ctx
    (stage1_dir / "shots.json").write_text("not json", encoding="utf-8")
    out_dir = tmp_path / "out8"

    def fake_caller(call_name, system, user):
        return '{"scene_id": "S1", "verdict": "PASS", "problems": []}', {"status": 200, "wall_s": 0.1, "finish": "stop", "error": None}

    result = crosscheck.run_crosscheck(2, stage1_dir, root, fake_caller, out_dir)
    assert result["scenes"][0]["status"] == "ok"
    assert "doc_problems" in result
    assert any("shots.json" in p for p in result["doc_problems"])


def test_scene_slice_non_string_scene_id_ignored(base_docs_and_ctx):
    """Defect 2: scene_id must be string; non-string ids are ignored."""
    stage1_dir, root, docs, ctx = base_docs_and_ctx
    packet, _ = prompts.build_packet(2, root)

    # Add a scene with integer scene_id
    bad_docs = deepcopy(docs)
    bad_docs["scenes"]["scenes"].append({"scene_id": 5, "line_ids": ["S1-L1"], "ovi_range": [1, 2]})
    # The integer scene_id should not be picked up by run_crosscheck's scene_ids list
    # We test scene_slice directly: it should not find the scene because scene_id is not string
    slice_ = crosscheck.scene_slice(bad_docs, packet, "5")
    assert slice_["scene"] == {}
    # Also test that the string "5" is not found (since the scene_id is int 5)
    slice_ = crosscheck.scene_slice(bad_docs, packet, 5)  # type: ignore[arg-type]
    assert slice_["scene"] == {}


def test_main_dry_run(base_docs_and_ctx, capsys):
    stage1_dir, root, docs, ctx = base_docs_and_ctx
    out_dir = stage1_dir.parent / "out_main"

    sys.argv = ["crosscheck.py", "--adhyay", "2", "--stage1-dir", str(stage1_dir), "--out", str(out_dir), "--root", str(root), "--provider", "dry-run"]
    exit_code = crosscheck.main()
    assert exit_code == 0

    captured = capsys.readouterr()
    assert "S1 dry-run" in captured.out
    assert "S2 dry-run" in captured.out
    assert "summary: pass=0 block=0 failed=0" in captured.out


def test_no_kimi_import_and_no_nvapi_literal():
    source = CROSSCHECK_PATH.read_text(encoding="utf-8")
    assert "kimi_adapter" not in source
    assert "nvapi-" not in source
