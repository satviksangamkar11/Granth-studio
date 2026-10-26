"""Style finalists in 16:9 scenes: the 3 pilot scenes in two styles (Pahari miniature, Phad scroll) with Nano Banana Pro. The owner's approved references (set_v2 + house plate) give identity and place;
the STYLE comes only from the text. Reference images first, then the instruction. Request journal PREPARED -> SENT -> COMPLETED/UNKNOWN (a timeout is not re-sent automatically).
Usage: python gemini_scene_styles.py --out DIR [--model gemini-3-pro-image] [--styles pahari,phad]"""
from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("gemini_test", HERE / "gemini_test.py")
gt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gt)

STYLES = {
    "pahari": ("Pahari (Basohli / Kangra) hill-court miniature painting",
               "flat-colour devotional miniature painting, bold colour fields in deep blue, saffron yellow and vermilion red, fine flowing ink contour lines, pale monochrome sky band at the top, simplified schematic landscape and architecture with a high horizon, stylised figures with almond-shaped eyes, gold accents on textiles, tempera on handmade paper, no shading gradients, an ornamental border band"),
    "kalighat": ("Kalighat / Bengal Pattachitra folk painting",
                 "confident flowing brush contours, flat bold colour fills with a soft wash for rounded volume, minimal shading, simplified large almond eyes and stylised features, sparse composition with the figures large and the background reduced to a few simple shapes, plain textured paper ground"),
    "phad": ("Rajasthani phad scroll painting",
             "painting on cloth with bold dark outlines, flat two-dimensional figures mostly in profile or frontal, vegetable-dye reds, ochres, indigo and mustard, dense folk ornamentation, small banner flags, a few simple tree shapes, visible cloth texture, no perspective depth, no shading, a thin ornamental border, horizontal narrative composition"),
}
TASK = ("Use the attached reference images ONLY to know who each person is (face, age, build, costume) and what the house and road look like. Ignore their painting style completely and redraw the whole scene from scratch in the style below. "
        "Keep each person recognisable and different from the others. {scene} Art style: {style_name}: {style_desc}. No text, no labels, no watermark. One 16:9 landscape image.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="gemini-3-pro-image")
    ap.add_argument("--styles", default="pahari,phad")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    journal = out / "journal.json"

    def save():
        journal.write_text(gt.scrub(json.dumps(rows, indent=2)), encoding="utf-8")

    for sk in a.styles.split(","):
        sname, sdesc = STYLES[sk]
        for s, (chars, locs, text) in gt.SCENES.items():
            row = {"style": sk, "scene": s, "state": "PREPARED", "model": a.model}
            rows.append(row)
            save()
            images = []
            for name in chars + locs:
                p = (gt.V2 if (gt.V2 / name).exists() else gt.V1) / name
                images.append(gt.b64_image(p))
            parts = images + [{"text": TASK.format(scene=text, style_name=sname, style_desc=sdesc)}]
            body = {"contents": [{"parts": parts}], "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "16:9"}}}
            row["state"] = "SENT"
            save()
            t0 = time.time()
            status, data = gt.call(f"/v1beta/models/{a.model}:generateContent", body, timeout=240)
            row["wall_s"], row["http"] = round(time.time() - t0, 1), status
            if status == 0:
                row["state"], row["error"] = "UNKNOWN", data.get("error")
            elif status != 200:
                row["state"], row["error"] = "FAILED", data.get("error")
            else:
                img = None
                for cand in data.get("candidates", []):
                    for part in cand.get("content", {}).get("parts", []):
                        inline = part.get("inlineData") or part.get("inline_data")
                        if inline and inline.get("data"):
                            img = base64.b64decode(inline["data"])
                if img:
                    f = out / f"{sk}__scene{s}.png"
                    f.write_bytes(img)
                    row.update(state="COMPLETED", file=f.name, sha256=hashlib.sha256(img).hexdigest(), usage=data.get("usageMetadata", {}).get("totalTokenCount"))
                else:
                    row["state"], row["error"] = "FAILED", "no image: " + json.dumps(data)[:200]
            save()
            print(gt.scrub(json.dumps({k: row[k] for k in ("style", "scene", "state", "wall_s") if k in row})), flush=True)
    return 0 if all(r["state"] == "COMPLETED" for r in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
