"""Adhyay 1 production bible DRAFT (free, deterministic; nothing here is approved or canon until the owner says so).
Built once from: the image prompt list (docs/pilot/A1_image_prompts.md: identity paragraphs and the owner questions), the draft image catalog (canon/drafts/A1_image_catalog_DRAFT.json)
and the frozen research file hashes. Output (canon/bible/adhyay_01/): bible_DRAFT.json (characters, places, props, image catalog), unresolved.json (every OWNER_CHOICE once),
packets/S1.json..S9.json (the slice of the bible ONE scene needs: what the director receives instead of the whole research), receipt.json (input hashes).
  python scripts/source/a1_bible.py build"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MD = ROOT / "docs" / "pilot" / "A1_image_prompts.md"
CATALOG = ROOT / "canon" / "drafts" / "A1_image_catalog_DRAFT.json"
FROZEN = ROOT / "canon" / "packets" / "adhyay_01" / "frozen_copies"
OUT = ROOT / "canon" / "bible" / "adhyay_01"
IDENT = re.compile(r"^- \*\*(.+?)\*\* \(`([A-Z_]+)`\): (.+)$")
QROW = re.compile(r"^\| (OC-\d+) \| (.+?) \| (.+) \|$")
CHARACTERS = {"GM": "gajanan", "BA": "bankatlal", "DK": "damodarpant", "DV": None}          # speaking voice ids (Devidas has no spoken line in Adhyay 1)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def scenes_of(tokens: list) -> list:
    out = []
    for t in tokens:
        m = re.fullmatch(r"S(\d)-S(\d)", t)
        out += [f"S{i}" for i in range(int(m.group(1)), int(m.group(2)) + 1)] if m else [t]
    return sorted(set(out), key=lambda s: int(s[1:]))


def parse_md(text: str) -> tuple:
    ents, qs = {}, {}
    for ln in text.splitlines():
        m = IDENT.match(ln)
        if m:
            ents[m.group(2)] = {"name": m.group(1), "identity": m.group(3)}
        q = QROW.match(ln)
        if q:
            qs[q.group(1)] = {"question": q.group(2), "proposed_default": q.group(3)}
    return ents, qs


def build(md_text: str, catalog: list, voices: dict | None = None) -> dict:
    ents, qs = parse_md(md_text)
    by_ent = {}
    for im in catalog:
        for e in im["entities"]:
            by_ent.setdefault(e, []).append(im["image_id"])
    bible = {"status": "DRAFT, NOT APPROVED: the owner approves every field; unresolved looks are listed in unresolved.json", "chapter": 1, "characters": {}, "places": {}, "props": {}, "images": {}}
    for code, e in ents.items():
        rec = {"code": code, "name": e["name"], "identity_paragraph": e["identity"], "images": sorted(set(by_ent.get(code, [])))}
        if code in CHARACTERS:
            rec["voice_role"] = CHARACTERS[code]
            rec["voice_ids"] = {lg: (voices or {}).get(lg, {}).get(CHARACTERS[code]) for lg in ("mr", "hi")} if CHARACTERS[code] else {}
            bible["characters"][code] = rec
        else:
            bible["places"][code] = rec
    for im in catalog:
        if im["kind"] == "prop":
            bible["props"][im["image_id"]] = {"image_id": im["image_id"], "scenes": scenes_of(im["scenes"]), "source_refs": im["source_refs"], "owner_choice": im["owner_choice"]}
        bible["images"][im["image_id"]] = {k: im[k] for k in ("image_id", "kind", "scenes", "preset_roles", "entities", "references", "source_refs", "owner_choice", "covers_shots")}
        bible["images"][im["image_id"]]["scenes"] = scenes_of(im["scenes"])
    used = {}
    for im in catalog:
        for oc in im["owner_choice"]:
            code = oc.split(" ", 1)[0]
            used.setdefault(code, {"code": code, "text": oc.split(" ", 1)[1] if " " in oc else "", "images": []})["images"].append(im["image_id"])
    unresolved = {"status": "OPEN: answer once; defaults are proposals, not decisions",
                  "items": [{**v, **qs.get(k, {})} for k, v in sorted(used.items())],
                  "resolved_by_owner": [{"code": "OC-00", "decision": "Style: the flat-colour look of the owner's reference clips (assets/pilot_refs/style_v2), full-frame rich backgrounds (2026-10-26)"}]}
    packets = {}
    for sid in [f"S{i}" for i in range(1, 10)]:
        imgs = [i for i in bible["images"].values() if sid in i["scenes"]]
        codes = sorted({e for i in imgs for e in i["entities"]})
        packets[sid] = {"scene": sid, "characters": {c: bible["characters"][c] for c in codes if c in bible["characters"]}, "places": {c: bible["places"][c] for c in codes if c in bible["places"]},
                        "catalog": [{k: i[k] for k in ("image_id", "kind", "preset_roles", "entities", "covers_shots", "owner_choice")} for i in imgs],
                        "open_questions": sorted({oc.split(" ", 1)[0] for i in imgs for oc in i["owner_choice"]})}
    return {"bible": bible, "unresolved": unresolved, "packets": packets}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["build"])
    ap.parse_args()
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    vp = ROOT / "canon" / "audio" / "A1_eleven_voices.json"
    res = build(MD.read_text(encoding="utf-8"), catalog, json.loads(vp.read_text(encoding="utf-8")) if vp.exists() else None)
    (OUT / "packets").mkdir(parents=True, exist_ok=True)
    wr = lambda p, o: p.write_text(json.dumps(o, ensure_ascii=False, indent=1), encoding="utf-8")
    wr(OUT / "bible_DRAFT.json", res["bible"])
    wr(OUT / "unresolved.json", res["unresolved"])
    for sid, p in res["packets"].items():
        wr(OUT / "packets" / f"{sid}.json", p)
    frozen = {f.name: sha(f) for f in sorted(FROZEN.glob("*.md"))}
    wr(OUT / "receipt.json", {"inputs": {"image_prompts_md": sha(MD), "image_catalog_draft": sha(CATALOG), "frozen_copies": frozen}, "note": "derived data; rebuild with a1_bible.py build"})
    b = res["bible"]
    print(f"characters {len(b['characters'])}, places {len(b['places'])}, props {len(b['props'])}, images {len(b['images'])}, open questions {len(res['unresolved']['items'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
