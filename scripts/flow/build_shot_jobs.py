"""Builds the Flow job list for Adhyay 1 shot images (one job per shot, short prompts for saved-character generation).
Input : canon/drafts/A1_image_catalog_v2_DRAFT.json + canon/bible/adhyay_01/bible_DRAFT.json (identity paragraphs, used to cut the shot sentence out of the long prompt)
Output: canon/drafts/A1_flow_shot_jobs.json  (list of jobs; see docs/pilot/FLOW_RUNBOOK.md section 8 for how a job is executed)
Wording filter: Flow's safety filter blocked a prompt that said 'loincloth'; the short prompts say 'young ascetic' / 'vest' and never 'loincloth/bare/naked'."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAT = ROOT / "canon" / "drafts" / "A1_image_catalog_v2_DRAFT.json"
BIBLE = ROOT / "canon" / "bible" / "adhyay_01" / "bible_DRAFT.json"
OUT = ROOT / "canon" / "drafts" / "A1_flow_shot_jobs.json"

CHAR = {"GM": ("GM_v01", "the calm young ascetic (short dark hair, worn grey-white vest)"),
        "BA": ("BA_v01", "Bankatlal (cream turban, sage-green coat, cream shoulder cloth)"),
        "DK": ("DK_v01", "Damodarpant (terracotta-red turban, white shirt, white dhoti, slightly taller)"),
        "DV": ("DV_v01", "Devidas (shaved head with a small tuft, red tilak, bare shoulders, white dhoti)")}
PLACE = {"ROAD": ("Village road", "the attached road picture in front of Devidas's house (same house, door, leaf plates)"),
         "WELL": ("Cattle drinking", "the attached well and cattle trough picture"),
         "SHEGAON": ("landscape illustration", "the attached Shegaon village picture")}
SWAPS = [(r"Shri Gajanan Maharaj", "the young ascetic"), (r"Gajanan Maharaj", "the young ascetic"), (r"Maharaj", "the young ascetic"), (r"\bbandi\b", "vest"),
         (r"\bloincloth\b", "waist cloth"), (r"\balmost naked\b", "simply dressed"), (r"\bdigambar\b", "simply dressed"), (r"\bnaked\b", "simply dressed")]
STYLE = ("Flat-colour 2D Indian devotional storybook illustration: clean dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines, warm earth palette, "
         "a FULL richly drawn frame with foreground, midground and background filled in.")
TAIL = " Full-frame 16:9 landscape picture, edge to edge, no border. No text, no letters, no modern objects, no halo."


def clean(t: str) -> str:
    for a, b in SWAPS:
        t = re.sub(a, b, t)
    return re.sub(r"\s+", " ", t).strip()


def build() -> list:
    cat = json.loads(CAT.read_text(encoding="utf-8"))
    bible = json.loads(BIBLE.read_text(encoding="utf-8"))
    ident = {k: v["identity_paragraph"] for k, v in {**bible["characters"], **bible["places"]}.items()}
    jobs = []
    for it in cat:
        if it["kind"] != "shot_image":
            continue
        p = it["prompt"]
        end = max([p.find(ident[e]) + len(ident[e]) for e in it["entities"] if e in ident and p.find(ident[e]) >= 0] or [0])
        li = p.find(" Light:")
        fi = p.find(" Full-frame")
        body, light = p[end:li].strip(), p[li:fi].strip()
        body = re.sub(r"\s*Screen geography:.*$", "", body, flags=re.S).strip()                  # a continuity note about people who may be off-screen: it made Flow draw extra people
        on = [c for c in ("GM", "BA", "DK", "DV") if c in str(it.get("on_screen") or "").split()[0:0] + re.findall(r"[A-Z]{2}", str(it.get("on_screen") or ""))]
        chars = [e for e in dict.fromkeys(list(it["entities"]) + on) if e in CHAR]
        places = [e for e in it["entities"] if e in PLACE]
        cue = "; ".join(f"{CHAR[c][0]} ({CHAR[c][1]})" for c in chars)
        place_txt = f" Setting: {PLACE[places[0]][1]}." if places else ""
        only = " Show only the attached characters and no other people." if chars else " No people in the picture."
        prompt = f"{STYLE}" + (f" Use the attached characters exactly as in their reference sheets: {cue}; same faces, costumes, proportions." if chars else "") + place_txt + " " + clean(body) + only + " " + clean(light) + TAIL
        jobs.append({"shot_id": it["shot_id"], "scene": it["scene"], "flow_title": f"{it['shot_id']}__v01", "preset_suggested": it["preset_suggested"], "characters": [CHAR[c][0] for c in chars],
                     "place_search": PLACE[places[0]][0] if places else None, "style_ref_search": "ref_temple", "prompt": prompt, "chars_in_prompt": len(prompt), "source_refs": it["source_refs"], "status": "TODO"})
    return jobs


if __name__ == "__main__":
    jobs = build()
    OUT.write_text(json.dumps(jobs, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(jobs), "jobs ->", OUT)
    bad = [j["shot_id"] for j in jobs if re.search(r"loincloth|naked|bare-chested|Maharaj|bandi", j["prompt"])]
    print("prompts still containing filtered words:", bad)
    print("max prompt length", max(j["chars_in_prompt"] for j in jobs))
    if len(sys.argv) > 1:
        for j in jobs:
            if j["shot_id"] == sys.argv[1]:
                print(json.dumps(j, ensure_ascii=False, indent=1))
