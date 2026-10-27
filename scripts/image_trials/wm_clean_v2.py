"""Flow sparkle remover v2 (owner permission for his account, 2026-10-25). Flow puts TWO sparkles at fixed offsets in the bottom-right corner of 2752x1536 exports:
a small one (~113/114 px in from the right/bottom edges) on every image and a big one (~195/195 px in) on some. v1 (v5_watermark.py) handled only the small one and left faint traces.
Each star has a shape template learned from a flat-background frame (lighter than a LARGE-window local median: the window must be bigger than the star). A star is repainted only if it is really present
(its whole shape lighter than the surroundings while the ring just outside it is not); repaired pixels are composited through the (dilated) template only and every decoded pixel outside it is asserted identical.
Originals untouched.  Usage: python wm_clean_v2.py --src <dir of PNGs> --out <NEW dir>
A1-SPECIFIC: the learn image (SH_S5_05) and BIG_ON are Adhyay 1 data; another chapter needs its own learn image and a visually verified big-star list before use.
The script refuses --out equal to/overlapping --src and refuses to overwrite existing output files unless --overwrite."""
import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).parent))
from v5_watermark import repair  # noqa: E402  (auto-selects rows / cols / mirror / Telea fill)

W, H = 2752, 1536
CORNER = 480                      # work on the bottom-right 480x480 px
SMALL_C = (W - 113, H - 114)
BIG_C = (W - 195, H - 195)
DIL = 5
CLONE_MAX = {"SH_S6_05": 45}   # repetitive roof tiles: any matching tile is better than a smear
CLONE_FOR = {"SH_S6_05", "SH_S5_03", "SH_S5_06", "SH_S9_01", "SH_S9_07", "SH_S7_02", "SH_S5_04"}   # shots where Telea/rows smudged textured art
# Shots whose export carries the BIG sparkle (checked by eye on every shot + contrast ~27-36 on flat ground; automatic detection fails over dark artwork). Small sparkle: every shot.
BIG_ON = {"SH_S2_04", "SH_S2_06", "SH_S3_01", "SH_S3_04", "SH_S3_05", "SH_S4_02", "SH_S5_03", "SH_S5_04", "SH_S5_05", "SH_S5_06", "SH_S6_01", "SH_S7_02", "SH_S7_04", "SH_S9_01", "SH_S9_03", "SH_S9_07", "SH_S8_04"}
K = 201                           # median window, bigger than the big star (~100 px)


def corner(rgb):
    return np.ascontiguousarray(rgb[H - CORNER:, W - CORNER:])


def diff_map(rgb):
    g = cv2.cvtColor(corner(rgb), cv2.COLOR_RGB2GRAY)
    return g.astype(np.int16) - cv2.medianBlur(g, K).astype(np.int16)


def learn(path: Path, centre, r, thr=8):
    d = diff_map(np.asarray(Image.open(path).convert("RGB")))
    cx, cy = centre[0] - (W - CORNER), centre[1] - (H - CORNER)
    yy, xx = np.ogrid[:CORNER, :CORNER]
    m = (d > thr) & ((xx - cx) ** 2 + (yy - cy) ** 2 <= r * r)
    lab, n = ndimage.label(m)
    sizes = ndimage.sum(m, lab, range(1, n + 1))
    m = ndimage.binary_fill_holes(lab == 1 + int(np.argmax(sizes)))
    ys, xs = np.where(m)
    t = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    off = ((xs.min() + xs.max()) / 2 - cx, (ys.min() + ys.max()) / 2 - cy)
    return t, off


def place(t, off, centre):
    """Template mask in corner coordinates."""
    m = np.zeros((CORNER, CORNER), bool)
    cx, cy = centre[0] - (W - CORNER), centre[1] - (H - CORNER)
    y0 = int(round(cy + off[1] - t.shape[0] / 2))
    x0 = int(round(cx + off[0] - t.shape[1] / 2))
    m[y0:y0 + t.shape[0], x0:x0 + t.shape[1]] = t
    return m


def present(d, m):
    inner = ndimage.binary_erosion(m, iterations=2)
    ring = ndimage.binary_dilation(m, iterations=14) & ~ndimage.binary_dilation(m, iterations=7)
    frac = float((d[inner] > 5).mean())
    return (frac > 0.8 and float(d[ring].mean()) < 4.0), round(frac, 2), round(float(d[inner].mean()), 1), round(float(d[ring].mean()), 1)


def clone_fill(rgb, mask, search=170, step=3):
    """Textured art (roof tiles, hatching, line work): copy a matching patch from nearby. The shift is chosen by how well the shifted image predicts the untouched ring around the mask."""
    ys, xs = np.where(mask)
    ring = ndimage.binary_dilation(mask, iterations=9) & ~mask
    ry, rx = np.where(ring)
    best = None
    for dy in range(-search, search + 1, step):
        for dx in range(-search, search + 1, step):
            if abs(dx) < 14 and abs(dy) < 14:
                continue
            sy, sx = ys + dy, xs + dx
            qy, qx = ry + dy, rx + dx
            if sy.min() < 0 or qy.min() < 0 or sy.max() >= H or qy.max() >= H or sx.min() < 0 or qx.min() < 0 or sx.max() >= W or qx.max() >= W:
                continue
            if mask[sy, sx].any() or mask[qy, qx].any():
                continue
            err = float(np.abs(rgb[qy, qx].astype(np.int16) - rgb[ry, rx].astype(np.int16)).mean())
            if best is None or err < best[0]:
                best = (err, dy, dx)
    if best is None:
        return None, 99.0
    err, dy, dx = best
    out = rgb.copy()
    out[ys, xs] = rgb[ys + dy, xs + dx]
    return out, err


def ring_error(img, ref, mask):
    ring = ndimage.binary_dilation(mask, iterations=9) & ~mask
    return float(np.abs(img[ring].astype(np.int16) - ref[ring].astype(np.int16)).mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--learn", default="SH_S5_05.png")      # flat ground, both stars visible (A1 data)
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args()
    src, out = Path(a.src).resolve(), Path(a.out).resolve()
    if src == out or src in out.parents or out in src.parents:
        sys.exit("refusing: --out must be a separate directory that does not overlap --src")
    out.mkdir(parents=True, exist_ok=True)
    existing = [q.name for q in out.glob("SH_*.png")]
    if existing and not a.overwrite:
        sys.exit(f"refusing to overwrite {len(existing)} existing outputs in {out} (use a new directory or --overwrite)")
    ts, so = learn(src / a.learn, SMALL_C, 40)
    tb, bo = learn(src / a.learn, BIG_C, 90)
    print("templates: small", ts.shape, "| big", tb.shape)
    report = []
    for p in sorted(src.glob("SH_*.png")):
        rgb = np.asarray(Image.open(p).convert("RGB"))
        assert rgb.shape == (H, W, 3), p.name
        d = diff_map(rgb)
        ms, mb = place(ts, so, SMALL_C), place(tb, bo, BIG_C)
        (_ps, *si), (_pb, *bi) = present(d, ms), present(d, mb)
        pb = p.stem in BIG_ON
        ps = True                                              # the small star is on every export: always repaint it
        full = np.zeros((H, W), bool)
        res = rgb.copy()
        methods = []
        for part, flag in ((ms, ps), (mb, pb)):
            if not flag:
                continue
            mk_c = ndimage.binary_dilation(part, iterations=DIL)
            mk = np.zeros((H, W), bool)
            mk[H - CORNER:, W - CORNER:] = mk_c
            fixed, method = repair(res, mk)
            if p.stem in CLONE_FOR:                                # textured art: prefer a cloned patch when it predicts the ring well
                cl, err = clone_fill(res, mk)
                if cl is not None and err < CLONE_MAX.get(p.stem, 14):
                    fixed, method = cl, f"clone({err:.1f})"
            res = np.where(mk[..., None], fixed, res)
            full |= mk
            methods.append(method)
        assert np.array_equal(res[~full], rgb[~full]), p.name + ": pixels outside the mask changed"
        Image.fromarray(res).save(out / p.name)
        assert np.array_equal(np.asarray(Image.open(out / p.name).convert("RGB"))[~full], rgb[~full])
        report.append({"shot_id": p.stem, "small": ps, "small_stats": si, "big": pb, "big_stats": bi, "methods": methods, "mask_px": int(full.sum())})
        print(p.stem, "small" if ps else "-", si, "| big" if pb else "| -", bi, methods)
    (out / "wm_clean_v2_report.json").write_text(json.dumps(report, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
