"""V5 Phase 0.5 step 2(b): remove the small visible Flow sparkle in the bottom-right corner (owner confirmed removal is permitted for his account, 2026-10-25).
Only an auto-detected, dilated mask inside the bottom-right search box is repainted (OpenCV Telea); repaired pixels are composited through the mask and every decoded
pixel outside it is verified identical. Originals untouched; cleaned images to <inbox>/clean/, before/after corner crops with the mask outline for owner approval.
Usage: python v5_watermark.py [--inbox "D:/aai work/v5_inbox"]"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

BOX = 0.12          # search box = last 12 % of width and height
MIN_PX, MAX_PX = 40, 6000


TEMPLATE = None     # star-shaped mask learned once from a clean detection on a flat background (C2_p2_hands)


def learn_template(inbox: Path) -> np.ndarray:
    rgb = np.asarray(Image.open(inbox / "C2_p2_hands.png").convert("RGB"))
    m = fixed_mask(rgb)
    ys, xs = np.where(m)
    t = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return ndimage.binary_fill_holes(ndimage.binary_closing(t, iterations=3))


def template_mask(rgb: np.ndarray) -> np.ndarray | None:
    """The same star template, placed at Flow's measured sparkle centre (2K: 0.9588 w, 0.9260 h; 1376x768: 0.929 w, 0.892 h), scaled for 1K exports."""
    h, w = rgb.shape[:2]
    if w >= 2000 and w > h:
        cx, cy, scale = 0.9588 * w, 0.9260 * h, 1.0
    elif w > h:
        cx, cy, scale = 0.929 * w, 0.874 * h, 1.2
    else:
        return None                                                          # portrait references: no visible mark
    t = TEMPLATE if scale == 1.0 else np.asarray(Image.fromarray(TEMPLATE.astype(np.uint8) * 255).resize(
        (max(1, int(TEMPLATE.shape[1] * scale)), max(1, int(TEMPLATE.shape[0] * scale))))) > 127
    m = np.zeros((h, w), bool)
    y0, x0 = int(round(cy - t.shape[0] / 2)), int(round(cx - t.shape[1] / 2))
    m[y0:y0 + t.shape[0], x0:x0 + t.shape[1]] = t
    return ndimage.binary_dilation(m, iterations=2)


def directional_fill(rgb: np.ndarray, mask: np.ndarray, rows: bool) -> np.ndarray:
    """Fills each masked run by linear interpolation between its two unmasked neighbours along rows (keeps horizontal lines) or columns."""
    a = rgb.astype(np.float32).copy()
    m = mask
    if not rows:
        a, m = a.transpose(1, 0, 2).copy(), m.T
    for y in np.where(m.any(axis=1))[0]:
        xs = np.where(m[y])[0]
        runs = np.split(xs, np.where(np.diff(xs) > 1)[0] + 1)
        for r in runs:
            l, rr = r[0] - 1, r[-1] + 1
            if l < 0 or rr >= a.shape[1]:
                continue
            t = (np.arange(1, len(r) + 1) / (len(r) + 1))[:, None]
            a[y, r] = a[y, l] * (1 - t) + a[y, rr] * t
    if not rows:
        a = a.transpose(1, 0, 2)
    return np.clip(a + 0.5, 0, 255).astype(np.uint8)


def repair(rgb: np.ndarray, mask: np.ndarray) -> tuple[np.ndarray, str]:
    """Picks the fill by the structure around the mark: horizontal lines -> row fill, vertical -> column fill, otherwise Telea."""
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
    ring = ndimage.binary_dilation(mask, iterations=5) & ~mask
    gy = np.abs(cv2.Sobel(gray, cv2.CV_32F, 0, 1))[ring].mean()
    gx = np.abs(cv2.Sobel(gray, cv2.CV_32F, 1, 0))[ring].mean()
    if gy > 1.5 * gx and gy > 4:
        return directional_fill(rgb, mask, rows=True), "rows"
    if gx > 1.5 * gy and gx > 4:
        return directional_fill(rgb, mask, rows=False), "cols"
    bgr = cv2.inpaint(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), mask.astype(np.uint8) * 255, 3, cv2.INPAINT_TELEA)
    telea = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    # detailed corners (carved pillars): framing art is often mirror-symmetric, so the mirrored opposite corner is tried as a clone source;
    # it wins only if it matches the untouched ring around the mark much better than Telea's smooth fill
    mirror = rgb[:, ::-1]
    inner = mask & ~ndimage.binary_erosion(mask, iterations=3)
    ring_err = lambda img: float(np.abs(img[ring].astype(int) - mirror[ring].astype(int)).mean())   # how well the mirror predicts the known ring
    if gx + gy > 8 and ring_err(rgb) < 12:
        return np.where(mask[..., None], mirror, rgb), "mirror"
    return telea, "telea"


def fixed_mask(rgb: np.ndarray) -> np.ndarray:
    """Flow puts the sparkle at a fixed offset from the bottom-right corner (measured on 4 images: 2K exports ~106 px in from both edges,
    star ~45 px; 1376x768 exports ~98/83 px in). A disc covering it is repainted; contrast-based detection missed faint marks and once hit artwork."""
    h, w = rgb.shape[:2]
    (dx, dy, r) = (106, 106, 34) if w >= 2000 else (98, 83, 22)
    yy, xx = np.ogrid[:h, :w]
    disc = (xx - (w - dx)) ** 2 + (yy - (h - dy)) ** 2 <= r * r
    # inside the disc keep only the sparkle itself: it is LIGHTER than its local background (also over dark lines); a whole-disc repaint smeared lines
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.int16)
    local = cv2.medianBlur(cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY), 31).astype(np.int16)
    star = ndimage.binary_fill_holes(((gray - local) > 8) & disc)
    star = ndimage.binary_opening(star, iterations=1)
    return ndimage.binary_dilation(star, iterations=2) & disc


def find_mask(rgb: np.ndarray) -> np.ndarray | None:
    h, w = rgb.shape[:2]
    y0, x0 = int(h * (1 - BOX)), int(w * (1 - BOX))
    crop = rgb[y0:, x0:].astype(np.int16)
    local = cv2.medianBlur(rgb[y0:, x0:], 31).astype(np.int16)        # local background without the small mark
    diff = np.abs(crop - local).sum(axis=2)
    lab, n = ndimage.label(diff > 18)
    best = None
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        size = len(ys)
        bh, bw = np.ptp(ys) + 1, np.ptp(xs) + 1
        if not MIN_PX <= size <= MAX_PX or not 0.6 <= bh / bw <= 1.6 or max(bh, bw) > 0.06 * w:
            continue
        dist = (crop.shape[0] - ys.mean()) + (crop.shape[1] - xs.mean())       # prefer the blob nearest the corner
        if best is None or dist < best[0]:
            best = (dist, lab == i)
    if best is None:
        return None
    m = np.zeros((h, w), bool)
    m[y0:, x0:] = ndimage.binary_dilation(best[1], iterations=6)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inbox", default="D:/aai work/v5_inbox")
    a = ap.parse_args()
    inbox = Path(a.inbox)
    out = inbox / "clean"
    out.mkdir(exist_ok=True)
    global TEMPLATE
    TEMPLATE = learn_template(inbox)
    report, crops = [], []
    for src in sorted(p for p in inbox.glob("*.png") if not p.name.startswith("_")):
        rgb = np.asarray(Image.open(src).convert("RGB"))
        mask = template_mask(rgb)
        if mask is None:
            Image.fromarray(rgb).save(out / src.name)
            report.append({"file": src.stem, "mark": False})
            print(src.stem, "no visible mark (copied unchanged)")
            continue
        fixed, method = repair(rgb, mask)
        result = np.where(mask[..., None], fixed, rgb)                      # composite only through the mask
        assert np.array_equal(result[~mask], rgb[~mask]), "pixels outside the mask changed"
        Image.fromarray(result).save(out / src.name)
        Image.open(out / src.name).load()
        assert np.array_equal(np.asarray(Image.open(out / src.name))[~mask], rgb[~mask])  # decoded file check
        h, w = rgb.shape[:2]
        y0, x0 = int(h * (1 - BOX)), int(w * (1 - BOX))
        before = Image.fromarray(rgb[y0:, x0:]).copy()
        ImageDraw.Draw(before).text((4, 4), src.stem, fill=(255, 0, 0))
        outline = Image.fromarray(rgb[y0:, x0:]).copy()
        edge = ndimage.binary_dilation(mask[y0:, x0:]) & ~mask[y0:, x0:]
        o = np.asarray(outline).copy()
        o[edge] = (255, 0, 0)
        tiles = [before, Image.fromarray(o), Image.fromarray(result[y0:, x0:])]
        tw, th = 300, int(300 * tiles[0].height / tiles[0].width)
        row = Image.new("RGB", (tw * 3, th), "white")
        for i, t in enumerate(tiles):
            row.paste(t.resize((tw, th)), (i * tw, 0))
        crops.append(row)
        report.append({"file": src.stem, "mark": True, "mask_px": int(mask.sum()), "method": method})
        print(src.stem, "cleaned,", method, "mask", int(mask.sum()), "px, outside-mask pixels identical")
    if crops:
        sheet = Image.new("RGB", (crops[0].width, sum(c.height for c in crops)), "white")
        y = 0
        for c in crops:
            sheet.paste(c, (0, y))
            y += c.height
        sheet.save(out / "_before_mask_after.jpg", quality=90)
    (out / "watermark_report.json").write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
