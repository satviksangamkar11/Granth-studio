"""Decisive test of the code-first plan: can Kimi K3.1 Pro draw Maharaj (seated) as a LAYERED SVG puppet that survives a gesture, and improve it when it SEES its own render?
Round 0: Kimi sees the owner's reference image and draws the SVG. Then the script poses the right arm (rotation about the arm's own pivot), renders rest and raised side by side,
and sends that picture back for up to 2 corrections. The SVG is treated as data only (scripts, foreignObject and external links are refused); nothing the model writes is executed.
Key from D:/aai work/secrets/kimi/kimi_api_key.txt, never printed. Usage: python kimi_character_svg.py --out DIR [--ref PATH] [--corrections 2]"""
from __future__ import annotations

import argparse
import base64
import io
import json
import os
import re
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

KEY_FILE = Path(os.environ.get("KIMI_KEY_FILE", "D:/aai work/secrets/kimi/kimi_api_key.txt"))
URL = "https://api.moonshot.ai/v1/chat/completions"
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REF = ROOT / "assets" / "pilot_refs" / "set_v1" / "maharaj.jpg"
LIMB = "arm_right"

SPEC = ("Draw this person as a LAYERED SVG puppet, viewBox 0 0 1000 1000, transparent background, seated cross-legged, facing the viewer, hands resting on the knees. "
        "Style: flat Kalighat / Bengal folk painting: confident flowing contour lines drawn as filled paths of varying width, flat bold colour fills with one soft darker wash band per form for rounded volume, "
        "simplified large almond eyes with lowered calm gaze, minimal detail. Keep the identity of the reference: young man, short dark hair, radiant warm brown skin, strong neck and broad chest, plain white cloth tied at the waist, no other clothing. "
        "Required top-level groups with these exact ids, in back-to-front order: legs_cloth, torso, arm_left, hand_left, arm_right, hand_right, neck, head, hair, eyes, mouth. "
        "Every moving group (arm_left, arm_right and the hands, head) must carry a data-pivot=\"x,y\" attribute with its joint position (shoulder, wrist, neck) in viewBox units. "
        f"The group {LIMB} must contain the WHOLE right arm including its own hand, drawn so that when the group is rotated about its data-pivot (shoulder) the arm swings away from the body with NO visible gap or seam at the shoulder: "
        "draw the upper arm start well inside the torso outline. No text. Output ONLY the SVG in one ```svg block.")

FIX = ("Here are two renders of YOUR SVG: left = rest pose, right = the right arm group (id=" + LIMB + ") rotated -70 degrees about its data-pivot (a blessing gesture). The reference photo is attached first. "
       "Look carefully. List concrete defects (identity vs reference, anatomy of face, hands and fingers, proportions, seams or gaps at the shoulder when raised, clipped or floating pieces, style). "
       "Then output the corrected full SVG in one ```svg block, keeping the same group ids and data-pivot attributes.")


def load_key() -> str:
    key = os.environ.get("MOONSHOT_API_KEY", "").strip()
    if not key and KEY_FILE.is_file():
        key = KEY_FILE.read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"[A-Za-z0-9_.\-]{20,}", key):
        raise SystemExit("no usable Kimi key found")
    return key


def data_url(png_or_jpg: bytes, mime: str) -> str:
    return f"data:{mime};base64,{base64.b64encode(png_or_jpg).decode()}"


def call(key: str, messages: list, effort: str = "high"):
    body = {"model": "kimi-k3.1-pro", "reasoning_effort": effort, "messages": messages, "max_tokens": 24000}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    t0 = time.time()
    try:
        data = json.loads(urllib.request.urlopen(req, timeout=900).read())
        return data["choices"][0]["message"]["content"] or "", data.get("usage"), round(time.time() - t0, 1), None
    except urllib.error.HTTPError as exc:
        return "", None, round(time.time() - t0, 1), f"HTTP {exc.code} {exc.read().decode('utf-8', 'replace')[:300].replace(key, '***')}"
    except Exception as exc:
        return "", None, round(time.time() - t0, 1), f"{type(exc).__name__}: {str(exc)[:200]}".replace(key, "***")


def extract_svg(reply: str) -> str | None:
    m = re.search(r"```svg\s*(.*?)```", reply, re.S) or re.search(r"(<svg.*?</svg>)", reply, re.S)
    svg = (m.group(1) if m else "").strip()
    if not (svg.startswith("<svg") and svg.endswith("</svg>")):
        return None
    low = svg.lower()
    if "<script" in low or "<foreignobject" in low or re.search(r"(href|src)\s*=\s*[\"']\s*(https?:|data:|file:)", low) or re.search(r"\son\w+\s*=", low):
        return None                                                # data only: no scripts, external links or event handlers
    return svg


def pose(svg: str, limb_id: str, degrees: float) -> str | None:
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    root = ET.fromstring(svg)
    for el in root.iter():
        if el.attrib.get("id") == limb_id:
            px, py = (float(v) for v in el.attrib.get("data-pivot", "500,500").split(","))
            el.set("transform", f"rotate({degrees} {px} {py})")
            return ET.tostring(root, encoding="unicode")
    return None


def render(svg: str, width: int = 800) -> Image.Image:
    import resvg_py
    png = bytes(resvg_py.svg_to_bytes(svg_string=svg, width=width))
    im = Image.open(io.BytesIO(png)).convert("RGBA")
    bg = Image.new("RGBA", im.size, (244, 236, 214, 255))
    bg.alpha_composite(im)
    return bg.convert("RGB")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--ref", default=str(DEFAULT_REF))
    ap.add_argument("--corrections", type=int, default=2)
    a = ap.parse_args()
    key = load_key()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    ref = Path(a.ref)
    ref_img = Image.open(ref).convert("RGB")
    ref_img.thumbnail((768, 768))
    buf = io.BytesIO()
    ref_img.save(buf, "JPEG", quality=90)
    ref_part = {"type": "image_url", "image_url": {"url": data_url(buf.getvalue(), "image/jpeg")}}
    receipt = []
    messages = [{"role": "user", "content": [ref_part, {"type": "text", "text": SPEC}]}]
    for rnd in range(a.corrections + 1):
        reply, usage, wall, err = call(key, messages)
        row = {"round": rnd, "usage": usage, "wall_s": wall}
        if err:
            row["error"] = err
            receipt.append(row)
            break
        (out / f"round{rnd}_reply.txt").write_text(reply.replace(key, "***"), encoding="utf-8")
        svg = extract_svg(reply)
        if not svg:
            row["error"] = "no safe complete SVG in the reply"
            receipt.append(row)
            break
        (out / f"round{rnd}.svg").write_text(svg, encoding="utf-8")
        try:
            rest = render(svg)
            posed = pose(svg, LIMB, -70)
            raised = render(posed) if posed else None
            row["pose_ok"] = posed is not None
            if raised is None:
                row["error"] = f"group id {LIMB} not found"
                receipt.append(row)
                break
            sheet = Image.new("RGB", (rest.width * 2, rest.height), "white")
            sheet.paste(rest, (0, 0))
            sheet.paste(raised, (rest.width, 0))
            sheet.save(out / f"round{rnd}_rest_vs_raised.png")
        except Exception as exc:
            row["error"] = f"render failed: {type(exc).__name__}: {str(exc)[:200]}"
            receipt.append(row)
            break
        receipt.append(row)
        print(json.dumps(row), flush=True)
        if rnd == a.corrections:
            break
        sb = io.BytesIO()
        sheet.thumbnail((1400, 800))
        sheet.save(sb, "PNG")
        messages = [{"role": "user", "content": [ref_part, {"type": "text", "text": SPEC}]},
                    {"role": "assistant", "content": reply},
                    {"role": "user", "content": [{"type": "image_url", "image_url": {"url": data_url(sb.getvalue(), "image/png")}}, {"type": "text", "text": FIX}]}]
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print("done", json.dumps(receipt)[:600])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
