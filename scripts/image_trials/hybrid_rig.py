"""Hybrid puppet, step B: Kimi K3.1 Pro designs the RIG and the ANIMATION for image-model parts, then a fixed driver renders it.
Kimi sees the parts (an inspection sheet with pixel grids) and returns ONE JSON document: where each part goes, its parent, its pivot, and keyframed rotations. The driver validates the JSON,
builds nested SVG groups with the parts embedded, renders frames with resvg and encodes an MP4 with ffmpeg. Nothing Kimi writes is executed (JSON only, strictly validated); the key is read from
D:/aai work/secrets/kimi/kimi_api_key.txt and never printed. Up to N correction rounds: Kimi sees rest and peak renders and fixes seams.
Usage: python hybrid_rig.py --parts DIR --out DIR [--corrections 2] [--effort high]"""
from __future__ import annotations

import argparse
import base64
import io
import json
import math
import os
import re
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

KEY_FILE = Path(os.environ.get("KIMI_KEY_FILE", "D:/aai work/secrets/kimi/kimi_api_key.txt"))
URL = "https://api.moonshot.ai/v1/chat/completions"
CANVAS = 1000
MAX_LAYERS, MAX_KEYS, MAX_ANGLE, MAX_DURATION = 16, 12, 130, 6.0

TASK = (
    "You are the rigger and animator for a 2D cut-out puppet. The attached image is an inspection sheet: each numbered panel shows one body part (id and pixel size in the title) with a pixel grid every 50 px "
    "(coordinates are in the part's own pixels, origin top-left). The parts come from one character: a seated young man. Build a puppet on a {c}x{c} canvas (origin top-left) so that at rest he sits cross-legged facing the viewer "
    "with the head centred above the torso, both arms hanging naturally with hands resting near the knees, and the legs/cloth at the bottom. Then animate a 3-second BLESSING gesture: his right arm (the character's right, "
    "which is the viewer's LEFT) lifts the forearm and open hand up in a blessing, holds, then returns; add a very slight head nod and a slow breathing sway of the torso.\n"
    "Return ONLY one JSON object in one ```json block, no prose, with this exact schema:\n"
    "{{\"layers\":[{{\"id\":\"snake_case_name\",\"part\":\"partN\",\"x\":number,\"y\":number,\"scale\":number,\"pivot\":[px,py],\"parent\":null or \"layer id\",\"z\":integer}}],"
    "\"animation\":{{\"duration\":seconds,\"tracks\":[{{\"layer\":\"id\",\"keys\":[[time_seconds,rotation_degrees],...]}}]}}}}\n"
    "Rules: x,y = canvas position of the part's top-left corner; scale = uniform scale applied to the part image; pivot = the joint position in the PART's own pixels (shoulder for an upper arm, elbow for a forearm, "
    "base of the neck for the head, etc.); parent = the layer this one rotates with (forearm -> upper arm -> torso; head -> torso); z = stacking order, higher is in front. Rotation is in degrees, positive = clockwise on screen. "
    "Use at most {ml} layers, at most {mk} keys per track, angles within +-{ma}, duration <= {md}. Every part may be used once; place overlapping joints so no gap shows at rest or when rotated "
    "(parts have extra length at the joints for that; put the joint under the neighbouring part with a larger z where needed). Use every part you can identify; leave out only parts that are not body parts.")

FIX = ("Here are renders of YOUR rig: top row LEFT = rest pose at t=0, top row RIGHT = the peak of the motion, bottom row = a filmstrip of the key moments (full canvas, uncropped). The inspection sheet is attached first. Look carefully and list concrete defects "
       "(parts floating or misplaced, gaps or seams at the shoulder, elbow or neck, wrong stacking, arm not lifting like a blessing, hands cut off, anything outside the canvas). Then return the corrected full JSON in one ```json block.")


def load_key() -> str:
    key = os.environ.get("MOONSHOT_API_KEY", "").strip()
    if not key and KEY_FILE.is_file():
        key = KEY_FILE.read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"[A-Za-z0-9_.\-]{20,}", key):
        raise SystemExit("no usable Kimi key found")
    return key


def call(key: str, messages: list, effort: str):
    body = {"model": "kimi-k3.1-pro", "reasoning_effort": effort, "messages": messages, "max_tokens": 24000}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    t0 = time.time()
    try:
        data = json.loads(urllib.request.urlopen(req, timeout=900).read())
        usage = dict(data.get("usage") or {})
        usage["finish_reason"] = data["choices"][0].get("finish_reason")
        return data["choices"][0]["message"]["content"] or "", usage, round(time.time() - t0, 1), None
    except urllib.error.HTTPError as exc:
        return "", None, round(time.time() - t0, 1), f"HTTP {exc.code} {exc.read().decode('utf-8', 'replace').replace(key, '***')[:300]}"
    except Exception as exc:
        return "", None, round(time.time() - t0, 1), f"{type(exc).__name__}: {str(exc).replace(key, '***')[:200]}"


def img_part(img: Image.Image, fmt="PNG", side=1600) -> dict:
    img = img.copy()
    img.thumbnail((side, side))
    buf = io.BytesIO()
    img.convert("RGB").save(buf, fmt, **({"quality": 90} if fmt == "JPEG" else {}))
    mime = "image/png" if fmt == "PNG" else "image/jpeg"
    return {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{base64.b64encode(buf.getvalue()).decode()}"}}


def inspection_sheet(parts: list[dict], pdir: Path) -> Image.Image:
    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 18)
    small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 12)
    panel = 460
    cols = 3
    rows = (len(parts) + cols - 1) // cols
    sheet = Image.new("RGB", (panel * cols, (panel + 30) * rows), "white")
    d = ImageDraw.Draw(sheet)
    for i, p in enumerate(parts):
        im = Image.open(pdir / p["file"]).convert("RGBA")
        w, h = im.size
        s = min((panel - 10) / w, (panel - 10) / h, 1.0)
        shown = im.resize((max(1, int(w * s)), max(1, int(h * s))))
        x0, y0 = (i % cols) * panel, (i // cols) * (panel + 30)
        d.text((x0 + 4, y0 + 4), f"{p['id']}  {w}x{h}px", fill="black", font=font)
        bg = Image.new("RGBA", shown.size, (235, 235, 235, 255))
        bg.alpha_composite(shown)
        sheet.paste(bg.convert("RGB"), (x0 + 5, y0 + 30))
        step = 50
        for gx in range(0, w + 1, step):
            X = x0 + 5 + int(gx * s)
            d.line([(X, y0 + 30), (X, y0 + 30 + shown.height)], fill=(255, 0, 0) if gx % 100 == 0 else (255, 170, 170), width=1)
            if gx % 100 == 0:
                d.text((X + 2, y0 + 30), str(gx), fill=(200, 0, 0), font=small)
        for gy in range(0, h + 1, step):
            Y = y0 + 30 + int(gy * s)
            d.line([(x0 + 5, Y), (x0 + 5 + shown.width, Y)], fill=(0, 0, 255) if gy % 100 == 0 else (170, 170, 255), width=1)
            if gy % 100 == 0:
                d.text((x0 + 7, Y + 1), str(gy), fill=(0, 0, 200), font=small)
    return sheet


def extract_json(reply: str):
    m = re.search(r"```json\s*(.*?)```", reply, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


def num(v, lo, hi, what):
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or not lo <= v <= hi:
        raise ValueError(f"{what} must be a finite number in [{lo}, {hi}]")
    return float(v)


def validate(rig, part_ids: set, sizes: dict) -> dict:
    """Strict schema: unknown fields are DROPPED (the returned rig contains only the fields below), values are bounded, parts and track layers are unique."""
    if not isinstance(rig, dict) or not isinstance(rig.get("layers"), list) or not isinstance(rig.get("animation"), dict):
        raise ValueError("missing layers or animation")
    layers = rig["layers"]
    if not 1 <= len(layers) <= MAX_LAYERS:
        raise ValueError("layer count out of range")
    clean, ids, used = [], set(), set()
    for L in layers:
        if not isinstance(L, dict) or not re.fullmatch(r"[a-z][a-z0-9_]{0,31}", str(L.get("id", ""))):
            raise ValueError("bad layer id")
        lid = L["id"]
        if lid in ids:
            raise ValueError("duplicate layer id")
        ids.add(lid)
        part = L.get("part")
        if not isinstance(part, str) or part not in part_ids:
            raise ValueError("unknown part")
        if part in used:
            raise ValueError("a part is used twice")
        used.add(part)
        x, y, sc = num(L.get("x"), -2000, 3000, "x"), num(L.get("y"), -2000, 3000, "y"), num(L.get("scale"), 0.02, 5, "scale")
        piv = L.get("pivot")
        if not (isinstance(piv, list) and len(piv) == 2):
            raise ValueError("bad pivot")
        px, py = num(piv[0], -500, 3000, "pivot x"), num(piv[1], -500, 3000, "pivot y")
        z = L.get("z")
        if not isinstance(z, int) or isinstance(z, bool) or not -50 <= z <= 50:
            raise ValueError("bad z")
        w, h = sizes[part]
        if x + w * sc <= 0 or y + h * sc <= 0 or x >= CANVAS or y >= CANVAS:
            raise ValueError("a part lies entirely outside the canvas")
        parent = L.get("parent")
        if parent is not None and not isinstance(parent, str):
            raise ValueError("bad parent")
        clean.append({"id": lid, "part": part, "x": x, "y": y, "scale": sc, "pivot": [px, py], "parent": parent, "z": z})
    byid = {L["id"]: L for L in clean}
    for L in clean:
        if L["parent"] is not None and L["parent"] not in byid:
            raise ValueError("unknown parent")
    for L in clean:                                                    # no parent cycles
        seen, cur = set(), L["id"]
        while cur is not None:
            if cur in seen:
                raise ValueError("parent cycle")
            seen.add(cur)
            cur = byid[cur]["parent"]
    anim = rig["animation"]
    dur = num(anim.get("duration"), 0.5, MAX_DURATION, "duration")
    tracks = anim.get("tracks")
    if not isinstance(tracks, list) or not 1 <= len(tracks) <= MAX_LAYERS:
        raise ValueError("tracks missing or out of range")
    ctracks, tl = [], set()
    for T in tracks:
        if not isinstance(T, dict) or T.get("layer") not in byid or T["layer"] in tl:
            raise ValueError("track for an unknown or repeated layer")
        tl.add(T["layer"])
        keys = T.get("keys")
        if not isinstance(keys, list) or not 1 <= len(keys) <= MAX_KEYS:
            raise ValueError("bad keys")
        last, ck = -1.0, []
        for k in keys:
            if not (isinstance(k, list) and len(k) == 2):
                raise ValueError("bad key")
            t = num(k[0], 0, dur, "key time")
            ang = num(k[1], -MAX_ANGLE, MAX_ANGLE, "angle")
            if t < last:
                raise ValueError("keys must be in time order")
            last = t
            ck.append([t, ang])
        ctracks.append({"layer": T["layer"], "keys": ck})
    if max(max(a for _, a in T["keys"]) - min(a for _, a in T["keys"]) for T in ctracks) < 20:
        raise ValueError("no visible motion: no track changes its angle by 20 degrees")
    return {"layers": clean, "animation": {"duration": dur, "tracks": ctracks}}


def angle_at(track, t):
    keys = track["keys"]
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, a0), (t1, a1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            u = 0 if t1 == t0 else (t - t0) / (t1 - t0)
            u = u * u * (3 - 2 * u)
            return a0 + (a1 - a0) * u
    return keys[-1][1]


def build_svg(rig: dict, uris: dict, sizes: dict, t: float) -> str:
    angles = {T["layer"]: angle_at(T, t) for T in rig["animation"].get("tracks", [])}
    layers = {L["id"]: L for L in rig["layers"]}
    children = {}
    for L in rig["layers"]:
        children.setdefault(L.get("parent"), []).append(L)

    def group(L):
        w, h = sizes[L["part"]]
        sc = L["scale"]
        px, py = L["x"] + L["pivot"][0] * sc, L["y"] + L["pivot"][1] * sc
        own = f'<image x="{L["x"]}" y="{L["y"]}" width="{w * sc}" height="{h * sc}" href="{uris[L["part"]]}"/>'
        items = [(L["z"], 0, own)] + [(c["z"], 1, group(c)) for c in children.get(L["id"], [])]    # the part's own image sits at its z among its children
        inner = "".join(x[2] for x in sorted(items, key=lambda i: (i[0], i[1])))
        return f'<g transform="rotate({angles.get(L["id"], 0):.3f} {px:.2f} {py:.2f})">{inner}</g>'
    # z only orders siblings within a parent; roots are ordered by z too
    body = "".join(group(L) for L in sorted(children.get(None, []), key=lambda c: c["z"]))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CANVAS} {CANVAS}" width="{CANVAS}" height="{CANVAS}"><rect width="{CANVAS}" height="{CANVAS}" fill="#f4ecd6"/>{body}</svg>'


def render(svg: str) -> Image.Image:
    import resvg_py
    return Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=svg, width=CANVAS)))).convert("RGB")


def key_times(rig: dict) -> list:
    dur = rig["animation"]["duration"]
    ts = {0.0, dur}
    for T in rig["animation"]["tracks"]:
        ts.update(k[0] for k in T["keys"])
    return sorted(ts)


def make_board(rig: dict, uris: dict, sizes: dict) -> Image.Image:
    ts = key_times(rig)
    total = lambda t: sum(abs(angle_at(T, t)) for T in rig["animation"]["tracks"])
    peak_t = max(ts, key=total)
    rest = render(build_svg(rig, uris, sizes, 0.0))
    peak = render(build_svg(rig, uris, sizes, peak_t))
    strip_ts = ts if len(ts) <= 6 else [ts[round(i * (len(ts) - 1) / 5)] for i in range(6)]
    cell = 2 * CANVAS // len(strip_ts)
    board = Image.new("RGB", (2 * CANVAS, CANVAS + cell), "white")
    board.paste(rest, (0, 0))
    board.paste(peak, (CANVAS, 0))
    for i, t in enumerate(strip_ts):
        board.paste(render(build_svg(rig, uris, sizes, t)).resize((cell, cell)), (i * cell, CANVAS))
    return board


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--corrections", type=int, default=2)
    ap.add_argument("--effort", default="high", choices=["low", "high", "max"])
    a = ap.parse_args()
    if not 0 <= a.corrections <= 2:
        raise SystemExit("--corrections must be 0, 1 or 2")
    key = load_key()
    t_start = time.time()
    pdir, out = Path(a.parts), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    parts = json.loads((pdir / "parts.json").read_text())
    sizes = {p["id"]: tuple(p["size"]) for p in parts}
    uris = {p["id"]: "data:image/png;base64," + base64.b64encode((pdir / p["file"]).read_bytes()).decode() for p in parts}
    sheet = inspection_sheet(parts, pdir)
    sheet.save(out / "inspection.png")
    insp = img_part(sheet)
    task = TASK.format(c=CANVAS, ml=MAX_LAYERS, mk=MAX_KEYS, ma=MAX_ANGLE, md=MAX_DURATION)
    messages = [{"role": "user", "content": [insp, {"type": "text", "text": task}]}]
    receipt, last_valid, status = [], None, "ok"
    for rnd in range(a.corrections + 1):
        if time.time() - t_start > 2400:
            status = "degraded: run deadline reached" if last_valid else "failed: run deadline reached"
            break
        reply, usage, wall, err = call(key, messages, a.effort)
        row = {"round": rnd, "usage": usage, "wall_s": wall}
        receipt.append(row)
        if err:
            row["error"] = err
            status = "degraded: a correction round failed" if last_valid else "failed: no valid rig"
            break
        (out / f"round{rnd}_reply.txt").write_text(reply.replace(key, "***"), encoding="utf-8")
        try:
            rig = validate(extract_json(reply), set(sizes), sizes)
        except Exception as exc:
            row["error"] = "invalid rig JSON: " + str(exc)[:150].replace(key, "***")
            status = "degraded: a correction round returned an invalid rig" if last_valid else "failed: no valid rig"
            break
        last_valid = rig
        (out / f"round{rnd}_rig.json").write_text(json.dumps(rig, indent=2).replace(key, "***"))
        board = make_board(rig, uris, sizes)
        board.save(out / f"round{rnd}_board.png")
        print(json.dumps(row), flush=True)
        if rnd < a.corrections:
            messages = [{"role": "user", "content": [insp, {"type": "text", "text": task}]}, {"role": "assistant", "content": reply},
                        {"role": "user", "content": [insp, img_part(board, side=1800), {"type": "text", "text": FIX}]}]
    if last_valid is not None:
        frames = out / "frames"
        if frames.exists():
            for old in frames.glob("f_*.png"):
                old.unlink()
        frames.mkdir(exist_ok=True)
        mp4 = out / "blessing.mp4"
        if mp4.exists():
            mp4.unlink()
        fps = 24
        dur = last_valid["animation"]["duration"]
        n = round(dur * fps) + 1                                   # includes the final frame at t = duration
        for i in range(n):
            render(build_svg(last_valid, uris, sizes, min(i / fps, dur))).save(frames / f"f_{i:04d}.png")
        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", str(frames / "f_%04d.png"), "-frames:v", str(n),
                            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", str(mp4)], capture_output=True, text=True, timeout=300)
        ok = r.returncode == 0 and mp4.exists()
        receipt.append({"frames": n, "mp4": ok, "ffmpeg_exit": r.returncode})
        if not ok:
            status = "failed: ffmpeg"
    receipt.append({"status": status})
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2))
    print("status:", status, flush=True)
    return 0 if status == "ok" else (3 if status.startswith("degraded") else 1)


if __name__ == "__main__":
    raise SystemExit(main())
