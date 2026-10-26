"""Evaluation of an Adhyay 1 director run against canon/eval/A1_expected.json: deterministic, free, no model. Scores each directed scene plan for meaningful events, the two teachings,
continuity (bandi, digambar, silent bow), attribution (no invented or wrong speaker), the planned shot count, and forbidden inventions. A scene result must be VALID or UNRESOLVED.
  python scripts/source/a1_eval.py score --run <run-folder-name>     (reads canon/director_runs/<run>/a01_scene<N>.json; writes nothing into the run)"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import importlib.util

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = ROOT / "canon" / "eval" / "A1_expected.json"
_spec = importlib.util.spec_from_file_location("director_test", ROOT / "scripts" / "source" / "director_test.py")
dt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dt)


def hit(rx, text: str):
    """First match that is not negated ('no birthplace or childhood shown' does not show a birthplace). rx is a regex string, or {"re", "unless_before"}: a match is
    exempt when a readiness phrase ('ready ... to') precedes it in the same clause ('ready to humbly prostrate' is a readiness, 'prostrate themselves' is not)."""
    pat, unless = (rx["re"], rx.get("unless_before")) if isinstance(rx, dict) else (rx, None)
    for m in re.finditer(pat, text, re.I):
        if dt.negated(text, m.start(), m.group(0)):
            continue
        if unless and re.search(unless, text[max(0, m.start() - 80):m.start()], re.I):
            continue
        return m
    return None


def wrong_actor(text: str, verbs: str, wrong: str, right: str):
    """A verb whose actor (the nearest preceding person in its clause) is the WRONG person: 'Bankatlal watches as Damodarpant fetches' is fine, 'Bankatlal fetches' is not.
    A RECIPIENT ('hands the gourd to Damodarpant') is not the actor; after ', who' the actor is the person named just before 'who' (the recipient)."""
    for m in re.finditer(verbs, text, re.I):
        raw = re.split(r"[.;\n]", text[max(0, m.start() - 90):m.start()])[-1]
        if dt.negated(text, m.start(), m.group(0)):
            continue
        who = re.search(r"\bwho\b[^,]*$", raw)
        if who:
            ref = raw[:who.start()]
            if ref.rfind(wrong) > ref.rfind(right):
                return m
            continue
        clause = re.sub(rf"\b(to|with|for|beside|near|toward|towards) \w*({wrong}|{right})\w*", " ", raw)
        if clause.rfind(wrong) > clause.rfind(right):
            return m
    return None


def plan_text(plan: dict) -> str:
    """Everything a viewer or the renderer could be told: titles, goals, per-shot texts, claims, staging and the image descriptions."""
    imgs = {i["image_id"]: i["description"] for i in plan.get("images_needed", [])}
    parts = [plan.get("goal", ""), plan.get("turn", {}).get("text", "")]
    for sh in plan.get("shots", []):
        parts += [sh.get("action", ""), sh.get("held_pose", ""), sh.get("performance", ""), sh.get("camera", ""), sh.get("need_new_reason", "")]
        parts += [c.get("term", "") for c in sh.get("claims", [])] + list(sh.get("staging", [])) + [imgs.get(v, "") for v in sh.get("assets", {}).values()]
    return "\n".join(p for p in parts if p).lower()


def shown_ovis(plan: dict) -> set:
    return {int(r.split(":")[1]) for sh in plan.get("shots", []) for r in sh.get("ovi_ids", [])}


def dialogue(plan: dict) -> list:
    return [(int(d["ovi"].split(":")[1]), d["speaker"].lower()) for sh in plan.get("shots", []) for d in sh.get("dialogue", [])]


def score_scene(sid: str, result: str, plan: dict | None, spec: dict, glob: dict, planned_shots: int | None = None, planned_lines: dict | None = None) -> list:
    """[(check id, passed, detail)] for one scene."""
    out = []
    out.append((f"{sid}-result", result in glob["result_ok"], f"result {result}"))
    if not plan:
        return out + [(f"{sid}-plan", False, "no plan to score")]
    text, ovis, dlg = plan_text(plan), shown_ovis(plan), dialogue(plan)
    want = spec.get("shots") or planned_shots
    if want:
        out.append((f"{sid}-shots", len(plan["shots"]) == want, f"{len(plan['shots'])} shots, expected {want}"))
    for b in spec.get("beats", []):
        miss = [o for o in b.get("must_show", []) if o not in ovis]
        out.append((b["id"] + "-ovis", not miss, f"ovis not shown: {miss}" if miss else "shown"))
        for grp in b.get("text_all", []):
            out.append((b["id"] + "-text:" + "/".join(grp), any(re.search(rf"\b{re.escape(w)}", text) for w in grp), f"none of {grp} in the plan text"))
    spoken = [(int(d["ovi"].split(":")[1]), dt.qnorm(d["marathi"])) for sh in plan.get("shots", []) for d in sh.get("dialogue", [])]
    for o in spec.get("must_dialogue", []):
        want = [dt.qnorm(t) for t in (planned_lines or {}).get(o, [])]
        ok = any(ov == o and (not want or txt in want) for ov, txt in spoken)
        out.append((f"{sid}-dialogue-{o}", ok, f"ovi {o} must be spoken by its character in the planned words" if not ok else "present"))
    for ac in spec.get("actor_checks", []):
        m = wrong_actor(text, ac["verbs"], ac["wrong"], ac["right"])
        out.append((f"{sid}-actor:{ac['wrong']}", not m, f"wrong person does it: {m.group(0)!r}" if m else "right person"))
    for o in spec.get("no_named_dialogue", []):
        named = [s for ov, s in dlg if ov == o and s != "unclear"]
        out.append((f"{sid}-unclear-{o}", not named, f"ovi {o} given to {named}" if named else "unclear stays unclear"))
    for o in spec.get("no_dialogue", []):
        out.append((f"{sid}-silent-{o}", not [1 for ov, _ in dlg if ov == o], f"ovi {o} has spoken dialogue"))
    for o, allowed in spec.get("speaker_only", {}).items():
        bad = [s for ov, s in dlg if ov == int(o) and not any(a in s for a in allowed)]                 # 'shri gajanan maharaj' contains 'gajanan'
        out.append((f"{sid}-speaker-{o}", not bad, f"ovi {o} spoken by {bad}, allowed {allowed}" if bad else "speaker ok"))
    for rx in glob["forbidden_text"] + spec.get("forbidden_text", []):
        m = hit(rx, text)
        out.append((f"{sid}-forbidden:{(rx['re'] if isinstance(rx, dict) else rx)[:30]}", not m, f"forbidden text found: {m.group(0)!r}" if m else "absent"))
    return out


def score_run(plans: dict, expected: dict, timing: dict | None = None, dry_run: bool = False, audio: dict | None = None) -> dict:
    """plans: {scene number: {"result":..., "plan":...}}. Returns {"checks": [...], "passed": n, "failed": n}."""
    checks = []
    if dry_run:                                                                     # a run without reviewers is UNREVIEWED by design; only a real run must reach VALID/UNRESOLVED
        expected = {**expected, "global": {**expected["global"], "result_ok": expected["global"]["result_ok"] + ["UNREVIEWED"]}}
    planned = {s["scene"]: s["planned_shots"] for s in (timing or {}).get("scenes", [])}
    lines_by_scene = {}
    for l in (audio or {}).get("lines", []):
        if l["voice"] != "narrator" and l["priority"] == "core":
            lines_by_scene.setdefault(l["scene"], {}).setdefault(l["ovi"], []).append(l["marathi"])
    for sid, spec in expected["scenes"].items():
        n = int(sid[1:])
        r = plans.get(n)
        checks += score_scene(sid, r["result"] if r else "MISSING", r["plan"] if r else None, spec, expected["global"], planned.get(sid), lines_by_scene.get(sid))
    return {"checks": [{"id": c, "passed": p, "detail": d} for c, p, d in checks], "passed": sum(1 for _, p, _ in checks if p), "failed": sum(1 for _, p, _ in checks if not p)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["score"])
    ap.add_argument("--run", required=True)
    ap.add_argument("--dry-run", action="store_true", help="accept UNREVIEWED results (a free structural dry run with no reviewers)")
    a = ap.parse_args()
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    tpath = ROOT / "canon" / "audio" / "A1_timing_plan.json"
    timing = json.loads(tpath.read_text(encoding="utf-8")) if tpath.exists() else None
    base = ROOT / "canon" / "director_runs" / a.run
    plans = {}
    for f in sorted(base.glob("a01_scene*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        plans[d["scene"]] = {"result": d["result"], "plan": d.get("plan")}
    apath = ROOT / "canon" / "audio" / "A1_audio_plan.json"
    rep = score_run(plans, expected, timing, a.dry_run, json.loads(apath.read_text(encoding="utf-8")) if apath.exists() else None)
    for c in rep["checks"]:
        if not c["passed"]:
            print("FAIL", c["id"], "-", c["detail"])
    print(f"{rep['passed']} passed, {rep['failed']} failed over {len(plans)} scene(s)")
    return 0 if rep["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
