"""Hybrid puppet, step A: image-model art in a flat folk style, as SEPARATE PARTS. Nano Banana (owner's key, never printed) makes (1) a master seated figure and (2) a parts sheet: the same
character cut into pieces laid out apart on a plain white ground. The pieces are then cut out by connected components (flat colours key cleanly) and saved as transparent PNGs.
Usage: python hybrid_puppet_parts.py gen --out DIR [--model gemini-nano-banana-2.1] | cut --sheet FILE --out DIR"""
from __future__ import annotations

import argparse
import base64
import importlib.util
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = Path(__file__).resolve().parent
gt = None


def _gt():
    """The Gemini helper loads the API key at import time, so it is imported only by the commands that call the API."""
    global gt
    if gt is None:
        spec = importlib.util.spec_from_file_location("gemini_test", HERE / "gemini_test.py")
        gt = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gt)
    return gt


STYLE = ("flat Kalighat / Bengal folk painting style: confident flowing brush-like contour lines of varying width, flat bold colour fills, one soft darker wash band per form for rounded volume, "
         "minimal detail, simplified large almond eyes with a calm lowered gaze")
MASTER = ("Use the attached image ONLY to know who this person is (young man, short dark hair, radiant warm brown skin, strong neck and broad chest, bare torso, plain white cloth tied at the waist). "
          f"Redraw him from scratch in {STYLE}. One figure, seated cross-legged, facing the viewer, hands resting on the knees, centred, plain white background, no shadow, no text, no border. Square image.")
PARTS = ("The attached image is the finished character. Make a 2D CUT-OUT PUPPET PART SHEET of exactly this same character in exactly this same style and colours, on a PURE WHITE background, "
         "with every part drawn SEPARATELY, spaced well apart, NOT touching or overlapping each other, no shadows, no text, no labels. Parts, arranged in a loose grid: "
         "(1) head with neck and ears and short hair, eyes open and calm, mouth closed; (2) bare torso from the base of the neck to the waist, with NO arms attached and a flat straight-cut bottom and plain shoulder stumps; "
         "(3) right upper arm (the character's right) hanging straight, with a rounded top that is longer than needed so it can hide a joint; (4) right forearm with the hand held open, palm facing the viewer, fingers together, blessing gesture, drawn pointing straight up; "
         "(5) left upper arm hanging straight; (6) left forearm with the hand relaxed, pointing straight down; (7) the crossed legs and feet with the white waist cloth, as one piece, with a flat straight-cut top. "
         "All parts the same scale as in the finished character. Landscape image.")


def b64(path: Path, side=1024) -> dict:
    return _gt().b64_image(path, side)


def gen_one(model: str, parts: list, aspect: str, out: Path):
    body = {"contents": [{"parts": parts}], "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": aspect}}}
    status, data = _gt().call(f"/v1beta/models/{model}:generateContent", body, timeout=240)
    if status != 200:
        err = data.get("error") if isinstance(data, dict) else None
        raise SystemExit(f"HTTP {status}: {err.get('status') if isinstance(err, dict) else 'error'}")   # status only: no response text is printed
    for cand in data.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                out.write_bytes(base64.b64decode(inline["data"]))
                return data.get("usageMetadata")
    raise SystemExit("no image in the response")


def cmd_gen(a):
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    master = out / "master.png"
    u1 = gen_one(a.model, [b64(_gt().V1 / "maharaj.jpg"), {"text": MASTER}], "1:1", master)
    print("master ok", u1, flush=True)
    sheet = out / "parts_sheet.png"
    u2 = gen_one(a.model, [{"inline_data": {"mime_type": "image/png", "data": base64.b64encode(master.read_bytes()).decode()}}, {"text": PARTS}], "16:9", sheet)
    print("sheet ok", u2, flush=True)
    return 0


def cmd_cut(a):
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    im = Image.open(a.sheet).convert("RGB")
    arr = np.asarray(im).astype(int)
    nearwhite = (np.abs(arr - 255).sum(axis=2) <= 60)
    lab_bg, n_bg = ndimage.label(nearwhite)
    border = set(np.unique(np.concatenate([lab_bg[0, :], lab_bg[-1, :], lab_bg[:, 0], lab_bg[:, -1]]))) - {0}
    background = np.isin(lab_bg, list(border))      # only white connected to the border is background: white clothing enclosed by an outline is kept
    fg = ~background
    fg = ndimage.binary_opening(fg, iterations=1)
    lab, n = ndimage.label(fg)
    sizes = ndimage.sum(fg, lab, range(1, n + 1))
    keep = [i + 1 for i, sz in enumerate(sizes) if sz > 3000]
    parts = []
    for k in keep:
        ys, xs = np.where(lab == k)
        x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        mask = lab[y0:y1, x0:x1] == k
        rgba = np.dstack([np.asarray(im)[y0:y1, x0:x1], (mask * 255).astype(np.uint8)])
        parts.append({"bbox": [int(x0), int(y0), int(x1), int(y1)], "area": int(sizes[k - 1]), "rgba": rgba})
    if parts:                                       # stable reading order: rows by real vertical position, then left to right
        med_h = float(np.median([p["bbox"][3] - p["bbox"][1] for p in parts]))
        parts.sort(key=lambda p: p["bbox"][1])
        rows, cur = [], [parts[0]]
        for p in parts[1:]:
            if p["bbox"][1] - cur[0]["bbox"][1] < 0.5 * med_h:
                cur.append(p)
            else:
                rows.append(cur)
                cur = [p]
        rows.append(cur)
        parts = [p for row in rows for p in sorted(row, key=lambda p: p["bbox"][0])]
    meta = []
    for i, p in enumerate(parts, 1):
        f = out / f"part{i}.png"
        Image.fromarray(p["rgba"]).save(f)
        meta.append({"id": f"part{i}", "file": f.name, "bbox_in_sheet": p["bbox"], "size": [p["bbox"][2] - p["bbox"][0], p["bbox"][3] - p["bbox"][1]], "area": p["area"]})
    (out / "parts.json").write_text(json.dumps(meta, indent=2))
    print(len(meta), "parts:", [(m["id"], m["size"]) for m in meta])
    if len(meta) != 7:
        print("INVENTORY WARNING: the sheet asks for exactly 7 parts; merged, split or missing pieces are likely. Look at the parts before rigging.")
        return 2
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen"); g.add_argument("--out", required=True); g.add_argument("--model", default="gemini-nano-banana-2.1")
    c = sub.add_parser("cut"); c.add_argument("--sheet", required=True); c.add_argument("--out", required=True)
    a = ap.parse_args()
    return {"gen": cmd_gen, "cut": cmd_cut}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
