# TASK: return ONLY ONE FILE: scripts/pipeline/stage1/crosscheck.py (complete). Reply with exactly one block `FILE: scripts/pipeline/stage1/crosscheck.py` then the python fenced. Keep everything that works; apply EXACTLY the fixes below (verified defects from an independent reviewer; each has an exact fix) and change nothing else. The spec is the authority: docs/pilot/nemotron_specs/crosscheck.md.

## Defects to fix
1. `scripts/pipeline/stage1/crosscheck.py:36-38`, `:54`, `:59`, `:62-63`, `:70` (`scene_slice`): raises on odd data, though the spec says it never raises. Verified: `ovi_range: None` (TypeError), `ovi_range: ["a","b"]` (`'<=' not supported`), `line_ids: None` (`argument of type 'NoneType' is not iterable`), `scenes: None` (`'NoneType' object is not iterable`). Fix: type-check each value before use: `scenes_list` must be a list, `line_ids` must be a list, and `ovi_range` must be a list of two ints (otherwise return the empty slice). Or wrap the body in `try/except Exception` returning the empty slice.
2. `scripts/pipeline/stage1/crosscheck.py:201`: `if sc.get("scene_id")` accepts non-string ids. Verified: a scene with `"scene_id": 5` yields scene id `5`. The spec says strings only. Fix: `isinstance(sc.get("scene_id"), str) and sc.get("scene_id")`.
3. `scripts/pipeline/stage1/crosscheck.py:187-188`: a missing or unreadable document becomes `{}` with no problem recorded anywhere. The output keys are only `adhyay, advisory, note, scenes, summary` (verified). The spec says a missing document "is a problem". Fix: collect `doc_problems.append(f"missing: {unit}.json")` (or the parse error) and return it as a new key `doc_problems` in the result dict.


## CURRENT scripts/pipeline/stage1/crosscheck.py
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
    script_lines = []
    packet_script = packet.get("script", [])
    if isinstance(packet_script, list):
        for rec in packet_script:
            if isinstance(rec, dict) and rec.get("id") in line_ids:
                script_lines.append(rec)

    ovi_range = scene_card.get("ovi_range", [1, 0])
    ovi_start, ovi_end = ovi_range[0], ovi_range[1]
    ovis = []
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
    for unit in unit_names:
        fpath = stage1_path / f"{unit}.json"
        try:
            with fpath.open("r", encoding="utf-8") as f:
                docs[unit] = json.load(f)
        except Exception:
            docs[unit] = {}

    from importlib.util import spec_from_file_location, module_from_spec

    prompts_path = Path(__file__).resolve().parents[0] / "prompts.py"
    spec = spec_from_file_location("prompts", prompts_path)
    prompts_mod = module_from_spec(spec)
    spec.loader.exec_module(prompts_mod)

    packet, _ = prompts_mod.build_packet(adhyay, root_path)

    scenes_doc = docs.get("scenes", {})
    scenes_list = scenes_doc.get("scenes", []) if isinstance(scenes_doc, dict) else []
    scene_ids = [sc.get("scene_id") for sc in scenes_list if isinstance(sc, dict) and sc.get("scene_id")]
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
