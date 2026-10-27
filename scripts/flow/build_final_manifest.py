"""NOTE: "best" = HIGHEST version number, which equals the reviewed selection only if the highest version was the one chosen (true for Adhyay 1 on 2026-10-27); the FINAL set + hash list is built by build_final_set.py.
Builds the read-only review pack for the final Adhyay 1 shot images: best version per shot (highest vNN), manifest + 3x3 contact sheets.
Output: flow_outputs/adhyay_01/final_review/{final_manifest.json,sheet_N.jpg}. Never modifies images."""
import json, os
from pathlib import Path
from PIL import Image, ImageDraw
ROOT = Path(__file__).resolve().parents[2]
SH = Path("D:/aai work/flow_outputs/adhyay_01/shots")
OUT = Path("D:/aai work/flow_outputs/adhyay_01/final_review"); OUT.mkdir(exist_ok=True)
jobs = json.loads((ROOT / "canon/drafts/A1_flow_shot_jobs.json").read_text(encoding="utf-8"))
man = []
for j in jobs:
    for v in sorted({"v%02d" % int(f.name.split("candidate_v")[1].split(".")[0]) for f in SH.glob(j["shot_id"] + "__candidate_v*.png")}, reverse=True)[:1]:
        f = SH / f"{j['shot_id']}__candidate_{v}.png"
        if f.exists():
            man.append({"shot_id": j["shot_id"], "version": v, "file": str(f), "characters": j["characters"], "place": j["place_search"], "prompt": j["prompt"], "size": Image.open(f).size})
            break
    else:
        man.append({"shot_id": j["shot_id"], "version": None, "file": None})
(OUT / "final_manifest.json").write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
W, H = 520, 293
for k in range(0, len(man), 9):
    sheet = Image.new("RGB", (W * 3, (H + 18) * 3), "white"); d = ImageDraw.Draw(sheet)
    for i, m in enumerate(man[k:k + 9]):
        x, y = (i % 3) * W, (i // 3) * (H + 18)
        d.text((x + 4, y + 3), f"{m['shot_id']} {m['version']}", fill="black")
        if m["file"]:
            sheet.paste(Image.open(m["file"]).convert("RGB").resize((W, H)), (x, y + 18))
    sheet.save(OUT / f"sheet_{k // 9 + 1}.jpg", quality=88)
print(len(man), "shots;", sum(1 for m in man if m["file"]), "with files ->", OUT)
