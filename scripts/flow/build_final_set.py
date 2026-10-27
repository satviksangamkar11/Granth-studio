"""Builds the FINAL image folder (best version = highest vNN per shot) + FINAL_IMAGE_LIST_A1.md/.json (sha256, Flow edit id, Codex status) + FINAL_CONTACT_*.jpg for Adhyay 1.
A1-specific paths; copies only, never deletes. Run after the last fix and after build_final_manifest.py."""
import json, shutil, hashlib, re, glob, os
from pathlib import Path
from PIL import Image
A = Path("D:/aai work/flow_outputs/adhyay_01")
SH = A / "shots"
FIN = A / "final"
FIN.mkdir(exist_ok=True)
jobs = json.loads(Path("D:/aai work/granthstudio/canon/drafts/A1_flow_shot_jobs.json").read_text(encoding="utf-8"))
# last progress line per (shot, version-in-file-name) is not reliable for edit ids; take the latest edit id seen for the shot
edit = {}
for l in open(A / "shots_progress.jsonl", encoding="utf-8"):
    try:
        r = json.loads(l)
    except Exception:
        continue
    if r.get("shot_id") and r.get("edit_id"):
        edit[r["shot_id"]] = r["edit_id"]
# Codex status from the final review rounds
codex = {}
for f in sorted([f for f in glob.glob(str(A / "final_review" / "CODEX_FINAL_*.md")) if not f.endswith("REVIEW.md")] + glob.glob(str(A / "final_review" / "CODEX_R2_*.md")) + glob.glob(str(A / "final_review" / "CODEX_R3_*.md"))):
    for line in open(f, encoding="utf-8"):
        m = re.match(r"\|\s*(SH_S\d_\d+)\s*\|\s*(v\d+)\s*\|\s*(PASS|REGENERATE)", line)
        if m:
            codex[m.group(1)] = (m.group(2), m.group(3))
rows = []
by_scene = {}
for j in jobs:
    s = j["shot_id"]
    vs = sorted(int(re.search(r"candidate_v(\d+)\.png", f).group(1)) for f in glob.glob(str(SH / (s + "__candidate_v*.png"))))
    v = "v%02d" % vs[-1]
    png = SH / f"{s}__candidate_{v}.png"
    jpg = SH / f"{s}__candidate_{v}__2K_source.jpg"
    assert Image.open(png).size == (2752, 1536), s
    dst = FIN / f"{s}.png"
    shutil.copyfile(png, dst)
    sha = hashlib.sha256(dst.read_bytes()).hexdigest()
    cx = codex.get(s)
    status = "Codex PASS (final round)" if cx and cx[1] == "PASS" and cx[0] == v else ("not re-reviewed by Codex after the last change" if cx else "no Codex record")
    rows.append({"order": len(rows) + 1, "scene": j["scene"], "shot_id": s, "version": v, "final_file": str(dst), "source_png": str(png), "source_2k_jpg": str(jpg), "sha256": sha, "flow_edit_id": edit.get(s), "characters": j["characters"], "place": j["place_search"], "review": status})
(FIN / "FINAL_IMAGE_LIST_A1.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
md = ["# Adhyay 1: FINAL shot images for the animation (59)", "",
      "Folder: `D:\\aai work\\flow_outputs\\adhyay_01\\final\\` (one 2752x1536 PNG per shot, file name = shot id). Copies only: nothing in `shots/` was changed or deleted; every version stays there.", "",
      "| # | scene | shot | version used | review | file |", "|---|---|---|---|---|---|"]
for r in rows:
    md.append(f"| {r['order']} | S{r['scene']} | {r['shot_id']} | {r['version']} | {r['review']} | final/{r['shot_id']}.png |")
(FIN / "FINAL_IMAGE_LIST_A1.md").write_text("\n".join(md), encoding="utf-8")
print(len(rows), "final images")
print([ (r['shot_id'], r['review']) for r in rows if not r['review'].startswith('Codex PASS')])
# contact sheets for a final look
W, H = 480, 270
out = A / "final"
for k in range(0, 59, 12):
    sheet = Image.new("RGB", (W * 4, (H + 16) * 3), "white")
    from PIL import ImageDraw
    d = ImageDraw.Draw(sheet)
    for i, r in enumerate(rows[k:k + 12]):
        x, y = (i % 4) * W, (i // 4) * (H + 16)
        d.text((x + 4, y + 2), f"{r['shot_id']} {r['version']}", fill="black")
        sheet.paste(Image.open(r["final_file"]).convert("RGB").resize((W, H)), (x, y + 16))
    sheet.save(out / f"FINAL_CONTACT_{k // 12 + 1}.jpg", quality=88)
