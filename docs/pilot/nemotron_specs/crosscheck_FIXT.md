# TASK: return ONLY ONE FILE: tests/test_stage1_crosscheck.py (complete). Reply with exactly one block `FILE: tests/test_stage1_crosscheck.py` then the python fenced. The MODULE was just fixed for the defects below (it is shown for reference, do NOT return it). ADD one isolated regression test per defect (it must FAIL on the old behaviour and pass now; build inputs with plain assignment/deepcopy, never a helper that rejects no-effect mutations) and fix any existing assertion that the fix legitimately changed. Keep every other test. Spec: docs/pilot/nemotron_specs/crosscheck.md.
## Defects fixed in the module
1. `scripts/pipeline/stage1/crosscheck.py:36-38`, `:54`, `:59`, `:62-63`, `:70` (`scene_slice`): raises on odd data, though the spec says it never raises. Verified: `ovi_range: None` (TypeError), `ovi_range: ["a","b"]` (`'<=' not supported`), `line_ids: None` (`argument of type 'NoneType' is not iterable`), `scenes: None` (`'NoneType' object is not iterable`). Fix: type-check each value before use: `scenes_list` must be a list, `line_ids` must be a list, and `ovi_range` must be a list of two ints (otherwise return the empty slice). Or wrap the body in `try/except Exception` returning the empty slice.
2. `scripts/pipeline/stage1/crosscheck.py:201`: `if sc.get("scene_id")` accepts non-string ids. Verified: a scene with `"scene_id": 5` yields scene id `5`. The spec says strings only. Fix: `isinstance(sc.get("scene_id"), str) and sc.get("scene_id")`.
3. `scripts/pipeline/stage1/crosscheck.py:187-188`: a missing or unreadable document becomes `{}` with no problem recorded anywhere. The output keys are only `adhyay, advisory, note, scenes, summary` (verified). The spec says a missing document "is a problem". Fix: collect `doc_problems.append(f"missing: {unit}.json")` (or the parse error) and return it as a new key `doc_problems` in the result dict.

## CURRENT scripts/pipeline/stage1/crosscheck.py (reference only)
```python
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

CHECK_RULES = (
    "You are a read-only reviewer of a film plan. You advise; you never repair.\n"
    "Report ONLY real problems of these kinds:\n"
    "(1) an event, motive, miracle, dialogue or closure that the source ovis do not support;\n"
    "(2) script wording rewritten, translated, quoted at length or critiqued in a free-text field "
    "(the owner's EASY lines are immutable);\n"
    "(3) a shot that uses a preset against its stated limits (06 cannot raise a lowered hand; "
    "09 cannot lip-sync; fixed halos cannot be switched off by wording) or an invented preset id;\n"
    "(4) a teaching the source requires that the scene leaves out;\n"
    "(5) an image brief that contains narration, commentary, extra people, text or modern objects;\n"
    "(6) a voice or sound choice that contradicts the supplied voice descriptions or palette.\n"
    "Say PASS when you find none. Never propose rewritten text; point to the exact id and say what is wrong."
)


def scene_slice(docs: dict, packet: dict, scene_id: str) -> dict:
    if not isinstance(docs, dict) or not isinstance(packet, dict):
        return {
            "scene": {},
            "script_lines": [],
            "ovis": [],
            "shots": [],
            "briefs": [],
            "cues": [],
            "questions": [],
        }

    scenes_doc = docs.get("scenes", {})
    scenes_list = scenes_doc.get("scenes", []) if isinstance(scenes_doc, dict) else []
    if not isinstance(scenes_list, list):
        scenes_list = []
    scene_card = None
    for sc in scenes_list:
        if isinstance(sc, dict) and sc.get("scene_id") == scene_id:
            scene_card = sc
            break

    if not scene_card:
        return {
            "scene": {},
            "script_lines": [],
            "ovis": [],
            "shots": [],
            "briefs": [],
            "cues": [],
            "questions": [],
        }

    line_ids = scene_card.get("line_ids", [])
    if not isinstance(line_ids, list):
        line_ids = []
    script_lines = []
    packet_script = packet.get("script", [])
    if isinstance(packet_script, list):
        for rec in packet_script:
            if isinstance(rec, dict) and rec.get("id") in line_ids:
                script_lines.append(rec)

    ovi_range = scene_card.get("ovi_range", [1, 0])
    ovis = []
    if isinstance(ovi_range, list) and len(ovi_range) == 2 and all(isinstance(x, int) for x in ovi_range):
        ovi_start, ovi_end = ovi_range[0], ovi_range[1]
        packet_ovis = packet.get("ovis", [])
        if isinstance(packet_ovis, list):
            for ovi in packet_ovis:
                if isinstance(ovi, dict):
                    ovi_num = ovi.get("ovi")
                    if isinstance(ovi_num, int) and ovi_start <= ovi_num <= ovi_end:
                        ovis.append(ovi)

    def filter_by_scene_id(doc_key: str, list_key: str) -> list:
        doc = docs.get(doc_key, {})
        items = doc.get(list_key, []) if isinstance(doc, dict) else []
        result = []
        for item in items:
            if isinstance(item, dict) and item.get("scene_id") == scene_id:
                result.append(item)
        return result

    shots = filter_by_scene_id("shots", "shots")
    briefs = filter_by_scene_id("briefs", "images")
    cues = filter_by_scene_id("sounds", "cues")
    questions = filter_by_scene_id("questions", "questions")

    return {
        "scene": scene_card,
        "script_lines": script_lines,
        "ovis": ovis,
        "shots": shots,
        "briefs": briefs,
        "cues": cues,
        "questions": questions,
    }


def build_check_prompt(adhyay: int, scene_id: str, slice_: dict) -> tuple[str, str]:
    system = (
        "You are a read-only reviewer of a film plan. You advise; you never repair.\n"
        + CHECK_RULES
        + "\n\nReply with ONE JSON object "
        '{"scene_id": "<id>", "verdict": "PASS" or "BLOCK", '
        '"problems": [{"where": "<id such as S2-1 or S2-L3>", "what": "<one sentence>"}]}'
    )
    user = f"SCENE {scene_id}\n" + json.dumps(slice_, ensure_ascii=False, separators=(",", ":"))
    return system, user


def parse_verdict(text: str, scene_id: str) -> tuple[dict | None, list[str]]:
    problems = []
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None, ["no json object found"]
    json_text = text[start : end + 1]
    try:
        obj = json.loads(json_text)
    except json.JSONDecodeError:
        return None, ["bad json"]

    if not isinstance(obj, dict):
        return None, ["verdict: not an object"]

    if obj.get("scene_id") != scene_id:
        problems.append("scene_id: mismatch")

    verdict = obj.get("verdict")
    if verdict not in ("PASS", "BLOCK"):
        problems.append("verdict: invalid")

    probs = obj.get("problems")
    if not isinstance(probs, list):
        problems.append("problems: invalid")
    else:
        for p in probs:
            if not isinstance(p, dict) or not isinstance(p.get("where"), str) or not isinstance(p.get("what"), str):
                problems.append("problems: invalid")
                break

    if verdict == "PASS" and probs:
        problems.append("verdict: inconsistent")
    if verdict == "BLOCK" and not probs:
        problems.append("verdict: inconsistent")

    return obj, problems


def run_crosscheck(
    adhyay: int,
    stage1_dir: Path | str,
    root: Path | str,
    caller,
    out_dir: Path | str,
    *,
    only_scenes: list[str] | None = None,
    dry_run: bool = False,
) -> dict:
    stage1_path = Path(stage1_dir)
    root_path = Path(root)
    out_path = Path(out_dir)

    if out_path.exists() and any(out_path.iterdir()):
        raise FileExistsError(f"out_dir {out_path} exists and is not empty")

    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "prompts").mkdir(exist_ok=True)
    (out_path / "replies").mkdir(exist_ok=True)

    unit_names = [
        "story_map",
        "coverage",
        "scenes",
        "shots",
        "briefs",
        "looks",
        "voices",
        "sounds",
        "questions",
    ]
    docs = {}
    doc_problems = []
    for unit in unit_names:
        fpath = stage1_path / f"{unit}.json"
        try:
            with fpath.open("r", encoding="utf-8") as f:
                docs[unit] = json.load(f)
        except Exception as e:
            docs[unit] = {}
            doc_problems.append(f"missing or unreadable: {unit}.json ({e})")

    from importlib.util import spec_from_file_location, module_from_spec

    prompts_path = Path(__file__).resolve().parents[0] / "prompts.py"
    spec = spec_from_file_location("prompts", prompts_path)
    prompts_mod = module_from_spec(spec)
    spec.loader.exec_module(prompts_mod)

    packet, _ = prompts_mod.build_packet(adhyay, root_path)

    scenes_doc = docs.get("scenes", {})
    scenes_list = scenes_doc.get("scenes", []) if isinstance(scenes_doc, dict) else []
    scene_ids = [sc.get("scene_id") for sc in scenes_list if isinstance(sc, dict) and isinstance(sc.get("scene_id"), str) and sc.get("scene_id")]
    if only_scenes is not None:
        scene_ids = [sid for sid in scene_ids if sid in only_scenes]

    results = []
    for sid in scene_ids:
        slice_ = scene_slice(docs, packet, sid)
        system, user = build_check_prompt(adhyay, sid, slice_)
        prompt_text = f"SYSTEM:\n{system}\n\nUSER:\n{user}"
        prompt_file = out_path / "prompts" / f"{sid}.txt"
        prompt_file.write_text(prompt_text, encoding="utf-8")

        if dry_run:
            results.append(
                {
                    "scene_id": sid,
                    "status": "dry-run",
                    "verdict": None,
                    "problems": [],
                    "parse_problems": [],
                    "info": {},
                }
            )
            continue

        try:
            reply_text, info = caller("crosscheck", system, user)
        except Exception as e:
            results.append(
                {
                    "scene_id": sid,
                    "status": "failed",
                    "verdict": None,
                    "problems": [],
                    "parse_problems": [f"caller exception: {e}"],
                    "info": {"status": "error", "wall_s": 0.0, "finish": "error", "error": str(e)},
                }
            )
            (out_path / "replies" / f"{sid}.txt").write_text("", encoding="utf-8")
            continue

        reply_file = out_path / "replies" / f"{sid}.txt"
        reply_file.write_text(reply_text, encoding="utf-8")

        if info.get("status") != 200:
            results.append(
                {
                    "scene_id": sid,
                    "status": "failed",
                    "verdict": None,
                    "problems": [],
                    "parse_problems": [f"caller status {info.get('status')}: {info.get('error', '')}"],
                    "info": info,
                }
            )
            continue

        verdict_obj, parse_problems = parse_verdict(reply_text, sid)
        if verdict_obj is None:
            results.append(
                {
                    "scene_id": sid,
                    "status": "failed",
                    "verdict": None,
                    "problems": [],
                    "parse_problems": parse_problems,
                    "info": info,
                }
            )
            continue

        verdict = verdict_obj.get("verdict")
        probs = verdict_obj.get("problems", [])
        results.append(
            {
                "scene_id": sid,
                "status": "ok",
                "verdict": verdict,
                "problems": probs,
                "parse_problems": parse_problems,
                "info": info,
            }
        )

    pass_count = sum(1 for r in results if r.get("verdict") == "PASS")
    block_count = sum(1 for r in results if r.get("verdict") == "BLOCK")
    failed_count = sum(1 for r in results if r.get("status") == "failed")

    summary = {"pass": pass_count, "block": block_count, "failed": failed_count}
    output = {
        "adhyay": adhyay,
        "scenes": results,
        "summary": summary,
        "advisory": True,
        "note": "advice only; nothing was changed",
        "doc_problems": doc_problems,
    }

    (out_path / "crosscheck.json").write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    return output


def main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--adhyay", type=int, required=True)
    parser.add_argument("--stage1-dir", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[3]))
    parser.add_argument("--provider", choices=["nemotron", "dry-run"], default="dry-run")
    parser.add_argument("--model", default="nvidia/nemotron-3-ultra-550b-a55b")
    parser.add_argument("--only-scenes", default="")
    args = parser.parse_args(argv)

    only_scenes = [s.strip() for s in args.only_scenes.split(",") if s.strip()] or None

    if args.provider == "dry-run":
        caller = None
        dry_run = True
    else:
        from importlib.util import spec_from_file_location, module_from_spec

        runner_path = Path(__file__).resolve().parents[0] / "runner.py"
        spec = spec_from_file_location("runner", runner_path)
        runner_mod = module_from_spec(spec)
        spec.loader.exec_module(runner_mod)
        caller = runner_mod.nemotron_caller(model=args.model, thinking="on", effort="medium", json_mode=True)
        dry_run = False

    result = run_crosscheck(
        adhyay=args.adhyay,
        stage1_dir=args.stage1_dir,
        root=args.root,
        caller=caller,
        out_dir=args.out,
        only_scenes=only_scenes,
        dry_run=dry_run,
    )

    for scene in result["scenes"]:
        status = scene["status"]
        if status == "ok":
            print(f"{scene['scene_id']} {scene['verdict']}")
        else:
            print(f"{scene['scene_id']} {status}")

    summary = result["summary"]
    print(f"summary: pass={summary['pass']} block={summary['block']} failed={summary['failed']}")

    return 0 if summary["failed"] == 0 else 1
```
## CURRENT tests/test_stage1_crosscheck.py
```python
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

    for unit in ["story_map", "coverage", "scenes", "shots", "briefs", "looks", "voices", "sounds", "questions"]:
        before = (stage1_dir / f"{unit}.json").read_bytes()
        after = (stage1_dir / f"{unit}.json").read_bytes()
        assert before == after

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


def test_run_crosscheck_missing_document(base_docs_and_ctx, tmp_path: Path):
    stage1_dir, root, docs, ctx = base_docs_and_ctx
    (stage1_dir / "shots.json").unlink()
    out_dir = tmp_path / "out7"

    def fake_caller(call_name, system, user):
        return '{"scene_id": "S1", "verdict": "PASS", "problems": []}', {"status": 200, "wall_s": 0.1, "finish": "stop", "error": None}

    result = crosscheck.run_crosscheck(2, stage1_dir, root, fake_caller, out_dir)
    assert result["scenes"][0]["status"] == "ok"


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
```
