"""Universal Flow job builder (owner 2026-11-01: the one fixed image system for every Adhyay).

  python scripts/flow/build_jobs_v2.py --adhyay 1 --spec canon/drafts/A1_image_spec_new_shots.json --out canon/drafts/A1_flow_jobs_v2.json

Spec (per Adhyay, data only):
  {"adhyay": 1, "slot_order": {"S2": ["SH_S2_01", ...]},            # film order inside each scene (neighbours come from here)
   "shots": [{"shot_id": "SH_S2_09", "scene": "S2", "method": "generate" | "edit",
              "characters": ["GM_v01"], "place": "ROAD", "action": "...", "light": "...",
              "base_edit_id": null, "edit_instruction": null}]}
Series data (characters, places, style, forbidden words): config/flow_series.json.
Each job gets: the lessons template (exact head-count + the strict accepted-sheet sentence of every visible person, one place, ONE style anchor),
the chips to attach, the next free version number, and the previous / next shot (current best file + Flow title) for the continuity check."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SERIES = ROOT / "config" / "flow_series.json"
CAPS = {"generate": 8, "edit": 8}          # owner 2026-11-01: fix in a loop until it passes (27 Oct fix pass used up to 5); 8 submits/edits per shot is the safety stop
NEIGHBOUR_SENTENCE = "Match the attached neighbouring shot for the house, road, props and positions."


class SpecError(ValueError):
    pass


def load_series(path: Path = SERIES) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def chapter_dir(series: dict, adhyay: int) -> Path:
    return Path(series["outputs_root"]) / f"adhyay_{adhyay:02d}"


def sheet_path(series: dict, entry: dict) -> str:
    return str(chapter_dir(series, entry["sheet_adhyay"]) / "references" / entry["sheet"])


def final_list(series: dict, adhyay: int) -> dict:
    p = chapter_dir(series, adhyay) / "final" / f"FINAL_IMAGE_LIST_A{adhyay}.json"
    return {x["shot_id"]: x for x in json.loads(p.read_text(encoding="utf-8"))} if p.is_file() else {}


def candidates(series: dict, adhyay: int, shot: str) -> list[tuple[int, Path]]:
    shots = chapter_dir(series, adhyay) / "shots"
    out = []
    for p in shots.glob(f"{shot}__candidate_v*.png"):
        m = re.fullmatch(rf"{re.escape(shot)}__candidate_v(\d+)\.png", p.name)
        if m:
            out.append((int(m[1]), p))
    return sorted(out)


def best(series: dict, adhyay: int, shot: str, finals: dict) -> dict | None:
    """The image a neighbour comparison should use: the accepted final if any, else the newest candidate, else None."""
    if shot in finals:
        f = finals[shot]
        return {"shot_id": shot, "file": f["final_file"], "flow_title": f"{shot}__{f['version']}", "source": "final"}
    c = candidates(series, adhyay, shot)
    if c:
        v, p = c[-1]
        return {"shot_id": shot, "file": str(p), "flow_title": f"{shot}__v{v:02d}", "source": "newest candidate"}
    return None


def next_version(series: dict, adhyay: int, shot: str) -> str:
    c = candidates(series, adhyay, shot)
    return f"v{(c[-1][0] + 1) if c else 1:02d}"


def build_prompt(series: dict, chars: list, place: str | None, action: str, light: str, props: list | None = None) -> str:
    cs = series["characters"]
    people = (f"Exactly {len(chars)} {'person' if len(chars) == 1 else 'people'}: " + "; ".join(cs[c]["sentence"] for c in chars) + "."
              if chars else "No people in the picture.")
    setting = f" Setting: {series['places'][place]['text']}." if place else ""
    objects = "".join(f" {series['props'][p]['sentence'][0].upper()}{series['props'][p]['sentence'][1:]}." for p in props or [])
    only = " Show only these people and no others." if chars else ""
    return re.sub(r"\s+", " ", f"{series['style']['text']} {people}{setting} {action.strip()}{objects}{only} {light.strip()} {series['tail']}").strip()


def check_shot(series: dict, s: dict) -> None:
    for k in ("shot_id", "scene", "method", "characters", "action", "light"):
        if k not in s:
            raise SpecError(f"{s.get('shot_id', '?')}: missing {k}")
    if s["method"] not in CAPS:
        raise SpecError(f"{s['shot_id']}: method must be generate or edit")
    bad = [c for c in s["characters"] if c not in series["characters"]]
    if bad:
        raise SpecError(f"{s['shot_id']}: characters not in config/flow_series.json: {bad}")
    if s.get("place") and s["place"] not in series["places"]:
        raise SpecError(f"{s['shot_id']}: unknown place {s['place']}")
    badp = [p for p in s.get("props", []) if p not in series.get("props", {})]
    if badp:
        raise SpecError(f"{s['shot_id']}: props not in config/flow_series.json: {badp}")
    if s["method"] == "edit":
        ins = s.get("edit_instruction") or ""
        if not s.get("base_edit_id") or not ins.startswith("Change only") or "Keep everything else exactly the same" not in ins:
            raise SpecError(f"{s['shot_id']}: an edit needs base_edit_id and an instruction 'Change only ... Keep everything else exactly the same: ...'")


def build(spec: dict, series: dict, adhyay: int) -> list[dict]:
    if spec.get("adhyay") != adhyay:
        raise SpecError(f"spec is for Adhyay {spec.get('adhyay')}, not {adhyay}")
    finals = final_list(series, adhyay)
    order = spec.get("slot_order", {})
    jobs = []
    for s in spec["shots"]:
        check_shot(series, s)
        sid, scene = s["shot_id"], s["scene"]
        seq = order.get(scene, [])
        if sid not in seq:
            raise SpecError(f"{sid}: not in slot_order[{scene}] (neighbours unknown)")
        i = seq.index(sid)
        prev = best(series, adhyay, seq[i - 1], finals) if i > 0 else None
        nxt = best(series, adhyay, seq[i + 1], finals) if i + 1 < len(seq) else None
        props = list(s.get("props", []))
        prompt = build_prompt(series, s["characters"], s.get("place"), s["action"], s["light"], props)
        if s.get("reference_sentence"):
            prompt = prompt.replace(series["tail"], s["reference_sentence"].strip() + " " + series["tail"])
        hits = [w for w in series["forbidden_words"] if re.search(w, prompt + " " + (s.get("edit_instruction") or ""), re.I)]
        if hits:
            raise SpecError(f"{sid}: forbidden words for Flow's filter: {hits}")
        ver = next_version(series, adhyay, sid)
        place = series["places"].get(s.get("place") or "", None)
        prop_entries = [series["props"][p] for p in props]
        refs = list(s.get("reference_chips", []))                          # accepted shots attached for framing/style (e.g. a close-up for an insert)
        style_chip = series["style"].get("chip")                               # None = no style image (owner 2026-11-01: the temple picture leaked its content)
        chips = list(s["characters"]) + ([place["chip"]] if place else []) + [e["chip"] for e in prop_entries] + refs + ([style_chip] if style_chip else [])
        sheets = ([sheet_path(series, series["characters"][c]) for c in s["characters"]] + ([sheet_path(series, place)] if place else [])
                  + [sheet_path(series, e) for e in prop_entries])
        jobs.append({"adhyay": adhyay, "shot_id": sid, "scene": scene, "method": s["method"], "file_version": ver, "flow_title": f"{sid}__{ver}",
                     "characters": list(s["characters"]), "people_count": len(s["characters"]), "props": props, "chips": chips,
                     "unaccepted_sheets": [c for c in s["characters"] if not series["characters"][c].get("accepted")],
                     "prompt": prompt, "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                     "base_edit_id": s.get("base_edit_id"), "edit_instruction": s.get("edit_instruction"),
                     "previous_shot": prev, "next_shot": nxt, "sheets": sheets, "attempt_cap": CAPS[s["method"]],
                     "neighbour_chips": [n["flow_title"] for n in (prev, nxt) if n and n.get("source") == "final"],   # only ACCEPTED neighbours may be attached (27 Oct rule)
                     "neighbour_sentence": NEIGHBOUR_SENTENCE,
                     "model": series["model"], "status": "TODO"})
    return jobs


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--adhyay", type=int, required=True)
    ap.add_argument("--spec", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--series", type=Path, default=SERIES)
    a = ap.parse_args(argv)
    try:
        jobs = build(json.loads(a.spec.read_text(encoding="utf-8")), load_series(a.series), a.adhyay)
    except SpecError as e:
        print("REFUSED:", e)
        return 2
    a.out.write_text(json.dumps(jobs, ensure_ascii=False, indent=1), encoding="utf-8")
    for j in jobs:
        warn = f"  WARNING unaccepted sheet(s): {j['unaccepted_sheets']}" if j["unaccepted_sheets"] else ""
        print(f"{j['flow_title']}  {j['method']}  chips={j['chips']}  prev={(j['previous_shot'] or {}).get('flow_title')}  next={(j['next_shot'] or {}).get('flow_title')}{warn}")
    print(len(jobs), "jobs ->", a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
