"""Seeded-error test for the meaning checker (Codex advice, 2026-10-25). 8 wrong meanings (omission, reversal, wrong object, invented motive, wrong speaker, wrong date,
unsupported detail, invented agent) and 5 correct controls for ovis of Adhyay 1 are given to a checker model; it must flag every seeded error and leave the controls alone.
The correct readings are Claude's own reading of the ovis, NOT owner-verified: this tests the checkers, it does not approve anything.
  python scripts/source/seeded_check_test.py --models z-ai/glm-5.3-flash nvidia/nemotron-3-ultra-550b-a55b"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("ds", ROOT / "scripts" / "source" / "draft_source.py")
ds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ds)
nt = ds.nt

# (ovi, meaning, speaker, expected, label)
CASES = [
    (84, "I will now tell you the story of that time; listen. There was a devout householder named Devidas.", "Dasganu", "OK", "control"),
    (90, "A rough unbaked clay pipe was in his hand, made by himself, which had never seen a potter's kiln.", "Dasganu", "OK", "control"),
    (97, "Bankatlal Agarwala was walking along the road; he saw this scene together with his friend.", "Dasganu", "OK", "control"),
    (123, "The sun reached midday and the ground grew hot; the birds went to take shelter on the trees.", "Dasganu", "OK", "control"),
    (146, "May this Gajanan Vijay book give joy to the devout; with folded hands Dasganu prays to God for this.", "Dasganu", "OK", "control"),
    (84, "I will now tell you the story of that time; listen.", "Dasganu", "ISSUE", "omitted clause (Devidas)"),
    (128, "Since you have no need of it, do not bring water; Brahma is not found in the world.", "Maharaj", "ISSUE", "reversed meaning"),
    (89, "He had no title or name to his credit; for drinking water he carried a copper pot.", "Dasganu", "ISSUE", "wrong object (gourd -> copper pot)"),
    (98, "Damodarpant Kulkarni was the friend's name; seeing this, both were astonished and angry.", "Dasganu", "ISSUE", "invented motive (angry)"),
    (99, "They began to say to each other that his actions were perverse, like a madman's.", "Devidas", "ISSUE", "wrong speaker (Devidas)"),
    (74, "In the prime of youth Gajanan came to the town of Shegaon, in Shake eighteen hundred, on Magh Shuddha Saptami.", "Dasganu", "ISSUE", "wrong date (Shuddha for Vadya)"),
    (94, "Whenever a grain caught his eye he picked it up and put it in his mouth, because he was starving; his purpose was also to show 'food is Brahma'.", "Dasganu", "ISSUE", "unsupported detail (starving)"),
    (87, "Used leaf plates, thrown by his servants, lay on the road in front of the house of the Brahmin Devidas.", "Dasganu", "ISSUE", "invented agent (servants)"),
]


def run(model: str, pool, keys) -> list[dict]:
    ovis = {o["ovi"]: o for o in ds.load_ovis(1)}
    order = sorted(range(len(CASES)), key=lambda i: (i * 7) % len(CASES))            # fixed shuffle so errors and controls are mixed
    results = []
    for b in range(0, len(order), 5):
        idx = order[b:b + 5]
        user = "CONTEXT:\n(none)\n\nCHECK:\n" + "\n\n".join(
            f"{100 + i}: {ovis[CASES[i][0]]['text']}\nMEANING: {CASES[i][1]}\nSPEAKER: {CASES[i][2]}" for i in idx)    # unique label per case (the real ovi number repeats)
        reply, info = ds.chat(pool, keys, model, ds.CHECK_SYS, user)
        try:
            got = ds.extract_json(reply, list)
        except ValueError:
            got = []
        ids = [g.get("ovi") for g in got if isinstance(g, dict)]
        by_id = {g["ovi"]: g.get("verdict") for g in got if isinstance(g, dict) and ids.count(g.get("ovi")) == 1}      # a label answered twice counts as no answer
        for i in idx:
            v = by_id.get(100 + i)
            v = v if v in ("OK", "ISSUE") else "NO_ANSWER"
            results.append({"case": i, "ovi": CASES[i][0], "label": CASES[i][4], "expected": CASES[i][3], "verdict": v, "wall_s": info.get("wall_s"), "status": info.get("status")})
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", nargs="+", required=True)
    a = ap.parse_args()
    keys = nt.load_keys()
    pool = nt.KeyPool(keys)
    with ThreadPoolExecutor(max_workers=len(a.models)) as ex:
        allres = dict(zip(a.models, ex.map(lambda m: run(m, pool, keys), a.models)))
    out = ROOT / "canon" / "drafts" / "seeded_check_results.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(nt.scrub(json.dumps(allres, indent=2, ensure_ascii=False), keys), encoding="utf-8")
    for m, res in allres.items():
        seeded = [r for r in res if r["expected"] == "ISSUE"]
        controls = [r for r in res if r["expected"] == "OK"]
        caught = [r for r in seeded if r["verdict"] == "ISSUE"]
        false = [r for r in controls if r["verdict"] == "ISSUE"]
        noans = [r for r in res if r["verdict"] not in ("OK", "ISSUE")]
        print(f"{m}: caught {len(caught)}/{len(seeded)}; false alarms {len(false)}/{len(controls)}; no answer {len(noans)}; calls {sorted({r['wall_s'] for r in res})} s")
        for r in seeded:
            if r["verdict"] != "ISSUE":
                print(f"   MISSED: {r['label']} (ovi {r['ovi']}) -> {r['verdict']}")
        for r in false:
            print(f"   FALSE ALARM on control ovi {r['ovi']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
