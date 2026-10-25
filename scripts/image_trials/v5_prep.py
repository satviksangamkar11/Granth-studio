"""V5 Phase 0.5 image prep, step 2 only: border-connected plain white -> transparent for layer images (enclosed whites such as white clothing stay).
Originals are never modified; outputs go to <inbox>/prepped/ with a preview on dark and on saffron backgrounds for the owner's edge check.
The watermark step is NOT here: it waits for the owner's decision on Google's watermark terms.
Usage: python v5_prep.py [--inbox "D:/aai work/v5_inbox"]"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

LAYERS = ["A1_mid_temple", "A1_fg_frame", "C1_p1_wide", "C1_p2_bow", "C1_p3_bless", "C1_p4_react"]


def to_alpha(im: Image.Image) -> tuple[Image.Image, float]:
    arr = np.asarray(im.convert("RGB")).astype(int)
    white = np.abs(arr - 255).sum(axis=2) <= 36
    lab, _ = ndimage.label(white)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(border))
    alpha = np.where(bg, 0, 255).astype(np.uint8)
    alpha = ndimage.grey_erosion(alpha, size=2)                 # trims the 1-px white fringe at outline edges
    out = np.dstack([arr.astype(np.uint8), alpha])
    return Image.fromarray(out, "RGBA"), float(bg.mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inbox", default="D:/aai work/v5_inbox")
    a = ap.parse_args()
    inbox = Path(a.inbox)
    out = inbox / "prepped"
    out.mkdir(exist_ok=True)
    report = []
    for name in LAYERS:
        src = inbox / "clean" / f"{name}.png"          # watermark-cleaned copy (v5_watermark.py)
        im = Image.open(src)
        rgba, frac = to_alpha(im)
        rgba.save(out / f"{name}.png")
        tiles = []
        for colour in [(25, 30, 60), (238, 150, 40)]:
            bg = Image.new("RGBA", rgba.size, colour + (255,))
            bg.alpha_composite(rgba)
            tiles.append(bg.convert("RGB").resize((rgba.width // 3, rgba.height // 3)))
        prev = Image.new("RGB", (tiles[0].width * 2, tiles[0].height))
        prev.paste(tiles[0], (0, 0))
        prev.paste(tiles[1], (tiles[0].width, 0))
        prev.save(out / f"{name}_preview.jpg", quality=88)
        report.append({"file": name, "size": im.size, "background_fraction": round(frac, 3),
                       "source_sha256": hashlib.sha256(src.read_bytes()).hexdigest()})
        print(name, im.size, "background", round(frac, 3))
    (out / "prep_report.json").write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

