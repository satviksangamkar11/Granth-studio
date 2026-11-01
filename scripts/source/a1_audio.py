"""Adhyay 1 audio plan and timing (DRAFT, owner-reviewable; nothing here is approved, nothing is recorded or synthesised).
- Marathi lines are EXACT verse segments cut from the packet ovis by (ovi, charans); the one paraphrase (the year line) is labelled. The code verifies every segment is a substring of its ovi.
- Hindi is a DRAFT adaptation, NOT VALIDATED. Voices: the narrator reads all verse narration and every unclear or joint speech; a character voice only where the owner's dialogue table names that one speaker.
- Sound: a CLOSED palette; cues anchor to a scene bed, a picture event, or the start/end of a line (never over a spoken line); verse-named cues cite an ovi of their scene, everything else is STAGING.
- Durations are ESTIMATES from syllable counts at assumed speaking rates (hypotheses to calibrate with the TTS test); the common picture timeline follows the LONGER of the Marathi and Hindi line.
  python scripts/source/a1_audio.py build --run a1_split_rev4"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


spec_mod = _load("a1_audio_spec", ROOT / "scripts" / "source" / "a1_audio_spec.py")
dt = _load("director_test", ROOT / "scripts" / "source" / "director_test.py")

RATE = {"mr": 3.8, "hi": 4.6}          # syllables per second: ASSUMED narration speeds (hypotheses; calibrate with the TTS test)
PAUSE, LEAD, TAIL, SHOT_S = 0.5, 0.5, 0.5, 6.0
NOT_FILM_FACING = re.compile(r"माघ|सप्तमी|वद्य|सज्जनगड|मत्स्येंद्र|गोरख|कानीफा|चांगदेव|रामदास|फरवरी|जनवरी")   # day/month and the Sajjangad/Samarth/Nath material stay out of narration
CHARACTER_VOICES = {"bankatlal", "damodarpant", "gajanan"}


def charans(text: str) -> list:
    return [p.strip() for p in text.split("।") if p.strip()]


def syllables(text: str) -> int:
    """Rough syllable count of Devanagari (and digits): consonants not followed by a virama, plus independent vowels; a 4-digit year counts as 8. An ESTIMATE (no schwa deletion)."""
    n, i = 0, 0
    for _ in re.findall(r"[0-9०-९]{4}", text):
        n += 8
    text = re.sub(r"[0-9०-९]+", " ", text)
    while i < len(text):
        c = text[i]
        if "ऄ" <= c <= "औ" or c == "ॠ":
            n += 1
        elif "क" <= c <= "ह" or "क़" <= c <= "य़":
            n += 0 if text[i + 1:i + 2] == "्" else 1
        i += 1
    return n


def seconds(text: str, lang: str) -> float:
    return syllables(text) / RATE[lang]


def build_plan(ovis: dict) -> dict:
    lines = []
    for lid, scene, ovi, (a, b), voice, prio, hindi, note in spec_mod.LINES:
        parts = charans(ovis[ovi])
        marathi = " । ".join(parts[a - 1:b])
        lines.append({"id": lid, "scene": scene, "kind": "verse", "ovi": ovi, "charans": [a, b], "voice": voice, "priority": prio, "marathi": marathi, "hindi": hindi, "note": note})
    for ln in lines:
        ln["syllables"] = {"mr": syllables(ln["marathi"]), "hi": syllables(ln["hindi"])}
        ln["seconds"] = {"mr": round(ln["syllables"]["mr"] / RATE["mr"], 2), "hi": round(ln["syllables"]["hi"] / RATE["hi"], 2)}
    cues = [{"id": c[0], "scene": c[1], "sound": c[2], "anchor_type": c[3], "anchor": c[4], "label": c[5], "ovi": c[6]} for c in spec_mod.CUES]
    palette = [{"id": p[0], "kind": p[1], "description": p[2], "source_status": "UNSOURCED: the owner records it or a licence-checked CC0/CC-BY file is logged (URL + licence) before use"} for p in spec_mod.PALETTE]
    captions = [{"id": k[0], "scene": k[1], "where": k[2], "marathi": k[3], "hindi": k[4], "note": k[5]} for k in spec_mod.CAPTIONS]
    return {"version": 1, "status": "DRAFT, not approved. Marathi = exact verse segments. Hindi = draft adaptation, NOT VALIDATED. Durations = ESTIMATES.",
            "assumed_rates_syllables_per_second": RATE, "voices": spec_mod.VOICES, "lines": lines, "captions": captions, "palette": palette, "cues": cues}


def validate_plan(plan: dict, ovis: dict, macro: dict, speaker_rows: dict) -> tuple:
    errors, warnings = [], []
    scenes = {sc["scene_id"]: sc for st in macro["stories"] for sc in st["scenes"]}
    ids, last_ovi = set(), {}
    for ln in plan["lines"]:
        lid, sc = ln["id"], scenes.get(ln["scene"])
        if lid in ids:
            errors.append(f"{lid}: duplicate line id")
        ids.add(lid)
        if not sc:
            errors.append(f"{lid}: scene {ln['scene']} is not in the split")
            continue
        lo, hi = sc["ovi_range"]
        if not lo <= ln["ovi"] <= hi:
            errors.append(f"{lid}: ovi {ln['ovi']} is outside {ln['scene']} (ovi {lo}-{hi})")
        if ln["voice"] not in spec_mod.VOICES:
            errors.append(f"{lid}: unknown voice {ln['voice']!r}")
        if ln["priority"] not in ("core", "optional"):
            errors.append(f"{lid}: priority must be core or optional")
        if ln["kind"] == "verse" and not dt.quote_in(ln["marathi"], ovis[ln["ovi"]]):
            errors.append(f"{lid}: the Marathi is not an exact segment of ovi {ln['ovi']}")
        if not ln["hindi"].strip():
            errors.append(f"{lid}: no Hindi")
        if NOT_FILM_FACING.search(ln["marathi"]) or NOT_FILM_FACING.search(ln["hindi"]):
            errors.append(f"{lid}: a day, month or Sajjangad/Samarth/Nath-yogi word is in film-facing narration")
        row = speaker_rows.get(ln["ovi"], "").lower()
        if ln["voice"] in CHARACTER_VOICES:
            if not row or row.startswith("unclear") or " and " in row or not any(ln["voice"].startswith(w) or w.startswith(ln["voice"]) for w in re.findall(r"[a-z]{4,}", row)):
                errors.append(f"{lid}: voice {ln['voice']} is not what the owner's table gives for ovi {ln['ovi']} ({row or 'no row'}); unclear or joint speech goes to the narrator")
        if ln["ovi"] < last_ovi.get(ln["scene"], 0):
            errors.append(f"{lid}: lines must follow the order of the ovis")
        last_ovi[ln["scene"]] = ln["ovi"]
    for sid in scenes:
        if not any(l["scene"] == sid and l["priority"] == "core" for l in plan["lines"]):
            errors.append(f"{sid}: no core narration line")
    for k in plan["captions"]:
        if k["scene"] not in scenes or not re.fullmatch(r"[0-9]{4}|[०-९]{4}", k["marathi"]) or not re.fullmatch(r"[0-9]{4}", k["hindi"]):
            errors.append(f"{k['id']}: a caption is a four-digit YEAR only (no day, no month) in a real scene")
    pal = {p["id"]: p for p in plan["palette"]}
    per_scene = {}
    for c in plan["cues"]:
        sc = scenes.get(c["scene"])
        if c["sound"] not in pal:
            errors.append(f"{c['id']}: sound {c['sound']!r} is not in the closed palette")
            continue
        if not sc:
            errors.append(f"{c['id']}: unknown scene {c['scene']}")
            continue
        if c["anchor_type"] not in ("scene_bed", "picture_event", "before_line", "after_line"):
            errors.append(f"{c['id']}: anchor type {c['anchor_type']!r} (a cue may never sit over a spoken line)")
        if c["anchor_type"] in ("before_line", "after_line") and not any(l["id"] == c["anchor"] and l["scene"] == c["scene"] for l in plan["lines"]):
            errors.append(f"{c['id']}: anchor line {c['anchor']!r} is not a line of {c['scene']}")
        if c["anchor_type"] == "picture_event" and not c["anchor"].strip():
            errors.append(f"{c['id']}: a picture event needs a description")
        if (c["anchor_type"] == "scene_bed") != (pal[c["sound"]]["kind"] == "bed"):
            errors.append(f"{c['id']}: only a bed may be a scene bed, and every bed must be one")
        if c["label"] not in ("verse-named", "STAGING"):
            errors.append(f"{c['id']}: label must be verse-named or STAGING")
        if c["label"] == "verse-named" and not (c["ovi"] and sc["ovi_range"][0] <= c["ovi"] <= sc["ovi_range"][1]):
            errors.append(f"{c['id']}: a verse-named cue must cite an ovi of its scene")
        s = per_scene.setdefault(c["scene"], {"beds": 0, "fx": 0})
        s["beds" if pal[c["sound"]]["kind"] == "bed" else "fx"] += 1
    for sid, s in per_scene.items():
        if s["beds"] > 1:
            errors.append(f"{sid}: more than one bed at a time")
        if s["fx"] > 3:
            warnings.append(f"{sid}: {s['fx']} spot effects (more than 3)")
    return errors, warnings


def with_measured(plan: dict, measured: dict | None) -> tuple:
    """A copy of the plan whose line durations are the MEASURED seconds of the generated speech (per language) where they exist. Returns (plan, how many lines are measured)."""
    p = json.loads(json.dumps(plan))
    n = 0
    for l in p["lines"]:
        m = (measured or {}).get(l["id"])
        if m and m.get("mr") and m.get("hi"):
            l["seconds"] = {"mr": round(m["mr"], 2), "hi": round(m["hi"], 2)}
            n += 1
    return p, n


def timing(plan: dict, macro: dict, floor: bool = True) -> dict:
    """Per scene: the common picture timeline sized to the LONGER of the Marathi and Hindi line; shots needed at 6 s; the planned shots = max(audio need, allocation)."""
    out, total_mr, total_hi, total_common, total_shots = [], 0.0, 0.0, 0.0, 0
    for st in macro["stories"]:
        for sc in st["scenes"]:
            core = [l for l in plan["lines"] if l["scene"] == sc["scene_id"] and l["priority"] == "core"]
            t, beats = LEAD, []
            for l in core:
                dur = max(l["seconds"]["mr"], l["seconds"]["hi"])
                beats.append({"line": l["id"], "ovi": l["ovi"], "voice": l["voice"], "start_s": round(t, 2), "end_s": round(t + dur, 2), "shot": int(t // SHOT_S) + 1})
                t += dur + PAUSE
            common = t - PAUSE + TAIL
            gaps = PAUSE * max(len(core) - 1, 0)
            mr, hi = LEAD + sum(l["seconds"]["mr"] for l in core) + gaps + TAIL, LEAD + sum(l["seconds"]["hi"] for l in core) + gaps + TAIL
            need = max(2, math.ceil(common / SHOT_S))
            planned = max(need, sc["shot_budget"]) if floor else need
            shots = [{"shot": k, "from_s": round((k - 1) * SHOT_S, 2), "to_s": round(k * SHOT_S, 2), "lines_starting": [b["line"] for b in beats if b["shot"] == k],
                      "ovis": sorted({b["ovi"] for b in beats if b["shot"] == k})} for k in range(1, planned + 1)]
            out.append({"scene": sc["scene_id"], "ovi_range": sc["ovi_range"], "allocation": sc["shot_budget"], "audio_needs": need, "planned_shots": planned,
                        "marathi_s": round(mr, 1), "hindi_s": round(hi, 1), "common_s": round(common, 1), "visual_only_shots": [s["shot"] for s in shots if not s["lines_starting"]], "beats": beats, "shots": shots})
            total_mr, total_hi, total_common, total_shots = total_mr + mr, total_hi + hi, total_common + common, total_shots + planned
    measured_n = sum(1 for l in plan["lines"] if l.get("measured"))
    return {"estimate": not (measured_n and measured_n == len(plan["lines"])), "basis": f"{measured_n} of {len(plan['lines'])} lines MEASURED from generated speech; the rest are estimates at the assumed rates", "assumed_rates": RATE, "scenes": out, "marathi_s": round(total_mr, 1), "hindi_s": round(total_hi, 1), "common_audio_s": round(total_common, 1),
            "planned_shots": total_shots, "planned_picture_s": total_shots * 6, "allocated_shots": sum(s["allocation"] for s in out)}


def mmss(s: float) -> str:
    return f"{int(s // 60)} min {int(round(s % 60))} s"


def render_md(plan: dict, tm: dict, split_hash: str) -> str:
    L = ["# Adhyay 1: audio plan and timing (DRAFT; durations MEASURED from generated speech when available)", "",
         f"Split hash: `{split_hash}`. Nothing here is approved. Draft speech was synthesised (voices NOT VALIDATED until the owner listens). **Marathi** lines are exact verse segments cut from the ovis by code (the year 1878 is an on-screen caption only). "
         "**Hindi** is a draft adaptation and is NOT VALIDATED. **Durations** (where not measured) are estimates from syllable counts at assumed speaking rates "
         f"(Marathi {RATE['mr']} and Hindi {RATE['hi']} syllables per second: hypotheses to calibrate with the TTS test). One video, one picture timeline: it follows the LONGER of the two languages per line.", "",
         f"**Whole story (core narration):** Marathi about {mmss(tm['marathi_s'])}, Hindi about {mmss(tm['hindi_s'])}, common picture timeline about {mmss(tm['common_audio_s'])}. "
         f"Planned shots: **{tm['planned_shots']}** ({mmss(tm['planned_picture_s'])} of picture) against {tm['allocated_shots']} allocated by the split. Optional lines are NOT counted.", ""]
    L += ["| Scene | Ovi | Allocated | Audio needs | Planned shots | Marathi s | Hindi s | Common s |", "|---|---|---|---|---|---|---|---|"]
    L += [f"| {s['scene']} | {s['ovi_range'][0]}-{s['ovi_range'][1]} | {s['allocation']} | {s['audio_needs']} | {s['planned_shots']} | {s['marathi_s']} | {s['hindi_s']} | {s['common_s']} |" for s in tm["scenes"]]
    for s in tm["scenes"]:
        L += ["", f"## {s['scene']} (ovi {s['ovi_range'][0]}-{s['ovi_range'][1]}), {s['planned_shots']} shots", ""]
        L += ["| Line | Voice | Ovi | Marathi (exact verse) | Hindi (draft, NOT VALIDATED) | Est. s mr/hi | Priority |", "|---|---|---|---|---|---|---|"]
        for l in plan["lines"]:
            if l["scene"] == s["scene"]:
                tag = " (PARAPHRASE)" if l["kind"] == "paraphrase" else ""
                L.append(f"| {l['id']} | {l['voice']} | {l['ovi']} | {l['marathi']}{tag} | {l['hindi']} | {l['seconds']['mr']}/{l['seconds']['hi']} | {l['priority']} |")
        L += [f"| caption {k['id']} | on screen | | {k['marathi']} | {k['hindi']} | none | {k['where']} |" for k in plan["captions"] if k["scene"] == s["scene"]]
        L += ["", "Timecoded picture plan (common timeline):", ""] + [f"- shot {x['shot']} ({x['from_s']:.0f}-{x['to_s']:.0f} s): " + (", ".join(x["lines_starting"]) if x["lines_starting"] else "visual only (a held or moving picture, no new line starts)") for x in s["shots"]]
        cues = [c for c in plan["cues"] if c["scene"] == s["scene"]]
        L += ["", "Sound cues (closed palette, nothing sourced yet):", ""] + [f"- {c['id']} `{c['sound']}`: " + (f"under the whole scene" if c["anchor_type"] == "scene_bed" else f"{c['anchor_type'].replace('_', ' ')} {c['anchor']}") + f" [{c['label']}" + (f", ovi {c['ovi']}" if c["ovi"] else "") + "]" for c in cues]
    L += ["", "## Closed sound palette", ""] + [f"- `{p['id']}` ({p['kind']}): {p['description']}" for p in plan["palette"]]
    L += ["", "Every sound is UNSOURCED: the owner records it, or a CC0/CC-BY file is licence-checked and logged (URL and licence), before use. No cue sits over a spoken line."]
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["build"])
    ap.add_argument("--run", required=True, help="split run holding macro_A1.json (e.g. a1_split_rev4)")
    ap.add_argument("--out-dir", default=str(ROOT / "canon" / "audio"))
    ap.add_argument("--out-md", default=str(ROOT / "docs" / "pilot" / "A1_audio_plan.md"))
    ap.add_argument("--measured", default=None, help="canon/audio/A1_voice_measured.json: use the measured durations of the generated speech instead of estimates")
    ap.add_argument("--no-floor", action="store_true", help="planned shots = the measured audio need only (do NOT keep the old allocation as a minimum); use after the final voices are measured")
    a = ap.parse_args()
    res = json.loads((dt.RUNS / a.run / "macro_A1.json").read_text(encoding="utf-8"))
    files, ovis, _ = dt.load_inputs()
    plan = build_plan(ovis)
    if a.measured:
        mj = json.loads(Path(a.measured).read_text(encoding="utf-8"))
        if mj.get("problems"):
            print("ERROR the measured file records problems; refusing")
            return 1
        import importlib.util as _iu
        _sp = _iu.spec_from_file_location("a1_voices", ROOT / "scripts" / "source" / "a1_voices.py")
        _v = _iu.module_from_spec(_sp)
        _sp.loader.exec_module(_v)
        if mj.get("engine") == "elevenlabs":                                        # ElevenLabs speech of the owner's EASY wording
            _es = _iu.spec_from_file_location("easy_script", ROOT / "scripts" / "source" / "easy_script.py")
            _e = _iu.module_from_spec(_es)
            _es.loader.exec_module(_e)
            if mj.get("script_sha256") != _e.script_sha256():
                print("ERROR the measured speech was made from a different easy script; regenerate or re-measure")
                return 1
            _ov = _e.overlay(plan, _e.load_simple(_e.DEFAULT))
            want = {f"{l['id']}.{lg}": _v.prep_text(l["spoken_marathi" if lg == "mr" else "spoken_hindi"]) for l in _ov["lines"] for lg in ("mr", "hi")}
            stale = [k for k, t in want.items() if mj["clips"].get(k, {}).get("text") != t]
        else:
            stale = [j["id"] for j in _v.build_jobs(plan) if mj["clips"].get(j["id"], {}).get("text") != j["text"]]
        if stale:
            print(f"ERROR measured speech does not match the current script/voices for {len(stale)} clips (first: {stale[0]}); regenerate the voices")
            return 1
        meas = mj["lines"]
        plan, n = with_measured(plan, meas)
        for l in plan["lines"]:
            l["measured"] = l["id"] in meas and bool(meas[l["id"]].get("mr") and meas[l["id"]].get("hi"))
        print(f"measured durations used for {n} of {len(plan['lines'])} lines")
    rows = dt.speaker_rows(files["addendum"].splitlines())                  # frozen table + owner overrides
    errors, warnings = validate_plan(plan, ovis, res["macro"], rows)
    for w in warnings:
        print("WARN", w)
    if errors:
        print("\n".join("ERROR " + e for e in errors))
        return 1
    tm = timing(plan, res["macro"], floor=not a.no_floor)
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    plan["split_sha256"] = tm["split_sha256"] = res["macro_sha256"]
    (out / "A1_audio_plan.json").write_text(json.dumps(plan, indent=1, ensure_ascii=False), encoding="utf-8")
    (out / "A1_timing_plan.json").write_text(json.dumps(tm, indent=1, ensure_ascii=False), encoding="utf-8")
    Path(a.out_md).write_text(render_md(plan, tm, res["macro_sha256"]), encoding="utf-8")
    print(f"audio plan OK: {len(plan['lines'])} lines, {len(plan['cues'])} cues; Marathi ~{mmss(tm['marathi_s'])}, Hindi ~{mmss(tm['hindi_s'])}, common ~{mmss(tm['common_audio_s'])}; "
          f"planned shots {tm['planned_shots']} ({mmss(tm['planned_picture_s'])}) vs allocated {tm['allocated_shots']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
