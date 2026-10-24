"""Nano Banana (Gemini image) API test with the owner's key. The key is read from D:/aai work/secrets/gemini/gemini_api_key.txt (or GEMINI_API_KEY),
never printed, never written to a file, scrubbed from every message. Usage: python gemini_test.py models | run --model ID --out DIR [--scenes 1,2,3]"""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

KEY_FILE = Path(os.environ.get("GEMINI_KEY_FILE", "D:/aai work/secrets/gemini/gemini_api_key.txt"))
HOST = "https://generativelanguage.googleapis.com"
ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "assets" / "pilot_refs" / "set_v2"
V1 = ROOT / "assets" / "pilot_refs" / "set_v1"


def load_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key and KEY_FILE.is_file():
        key = KEY_FILE.read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"[A-Za-z0-9_.\-]{20,}", key):
        raise SystemExit("no usable Gemini key found (looked in GEMINI_API_KEY and the key file)")
    return key


KEY = load_key()


def scrub(text: str) -> str:
    return text.replace(KEY, "***") if KEY else text


def call(path: str, body: dict | None = None, timeout: int = 300):
    req = urllib.request.Request(HOST + path, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"x-goog-api-key": KEY, "Content-Type": "application/json"}, method="POST" if body is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as exc:
        return exc.code, {"error": scrub(exc.read().decode("utf-8", "replace")[:600])}
    except Exception as exc:
        return 0, {"error": scrub(f"{type(exc).__name__}: {exc}"[:300])}


def b64_image(path: Path, side: int = 1024) -> dict:
    from PIL import Image
    im = Image.open(path).convert("RGB")
    im.thumbnail((side, side))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=92)
    return {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(buf.getvalue()).decode()}}


# the three pilot scenes: references and text (same scene text the other backends used)
SCENES = {
    1: (["maharaj_youth.webp"], ["location.jpg"],
        "Image 1 is the young man, image 2 is the village road and house. He sits cross-legged on the dusty road in front of the house, among scattered used leaf plates, lifting a few grains of rice from a leaf plate toward his mouth, a small clay pipe in his other hand, calm face. Bright daylight."),
    2: (["maharaj_youth.webp", "bankatlal.webp", "damodarpant.webp"], ["location.jpg"],
        "Image 1 is the young man, image 2 the merchant in the turban, image 3 the clerk in the cap, image 4 the village road and house. The young man sits cross-legged on the road among scattered leaf plates, eating a grain of rice. The merchant and the clerk stand on the road a few steps away, watching in amazement. Bright daylight."),
    3: (["maharaj_youth.webp", "devidas.webp", "bankatlal.webp", "damodarpant.webp"], ["location.jpg"],
        "Image 1 is the young man, image 2 the householder with the sacred thread, image 3 the merchant in the turban, image 4 the clerk in the cap, image 5 the house and road. At the doorway the householder sets a large plate of sweets on the ground before the young man, who sits cross-legged and eats calmly. The merchant and the clerk stand nearby, watching with respect. Bright daylight."),
}
PREFIX = ("1950s vintage Indian devotional book illustration, authentic mid-century opaque gouache and egg tempera painting on aged matte ivory cardstock, "
          "soft hand-painted sepia contour linework, chalky matte gouache wash shading, flat hand-brushed tonal planes,")
SUFFIX = ("warm natural mineral pigments of raw sienna, burnt umber, warm ochre, terracotta, and muted sage green, subtle paper grain texture, "
          "vintage double-line paper border mount, clean traditional graphic composition, text-free, no labels, no watermarks.")
NEGATIVE = ("Avoid: photorealistic, 3D render, CGI, digital painting gloss, airbrushed gradients, shiny plastic skin, modern photography, harsh lens flare, neon colors, "
            "oil impasto, loose watercolour blotches, heavy black comic ink, blurry contours, text, typography, signature, watermarks.")


def cmd_models(_a) -> int:
    status, data = call("/v1beta/models?pageSize=200")
    print("HTTP", status)
    if status != 200:
        print(json.dumps(data)[:500])
        return 1
    for m in data.get("models", []):
        name = m.get("name", "")
        if re.search(r"image|banana|imagen", name + m.get("displayName", ""), re.I):
            print(name, "|", m.get("displayName"), "|", m.get("supportedGenerationMethods"))
    return 0


def cmd_run(a) -> int:
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    receipt = {"model": a.model, "note": "technical trial of the owner's Gemini key; outputs are NOT validated; human review NOT_DONE", "results": []}
    for s in [int(x) for x in a.scenes.split(",")]:
        chars, locs, text = SCENES[s]
        parts = [{"text": f"{PREFIX} {text} Match the style, faces, builds and clothing of the reference images exactly. {SUFFIX} {NEGATIVE} Output one 4:3 landscape painting."}]
        for name in chars + locs:
            p = (V2 if (V2 / name).exists() else V1) / name
            parts.append(b64_image(p))
        body = {"contents": [{"parts": parts}], "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "4:3"}}}
        t0 = time.time()
        status, data = call(f"/v1beta/models/{a.model}:generateContent", body)
        row = {"scene": s, "http": status, "wall_s": round(time.time() - t0, 1), "references": len(parts) - 1}
        if status == 200:
            usage = data.get("usageMetadata", {})
            row["usage"] = {k: usage.get(k) for k in ("promptTokenCount", "candidatesTokenCount", "totalTokenCount")}
            img = None
            for cand in data.get("candidates", []):
                for part in cand.get("content", {}).get("parts", []):
                    inline = part.get("inlineData") or part.get("inline_data")
                    if inline and inline.get("data"):
                        img = base64.b64decode(inline["data"])
                    elif part.get("text"):
                        row["text"] = part["text"][:200]
                row["finish"] = cand.get("finishReason")
            if img:
                f = out / f"nb_s{s}.png"
                f.write_bytes(img)
                row.update(file=f.name, sha256=hashlib.sha256(img).hexdigest(), bytes=len(img))
            else:
                row["error"] = "no image in the response: " + json.dumps(data)[:300]
        else:
            row["error"] = data.get("error")
        print(scrub(json.dumps({k: v for k, v in row.items() if k != "sha256"}))[:400], flush=True)
        receipt["results"].append(row)
        (out / "receipt.json").write_text(scrub(json.dumps(receipt, indent=2)), encoding="utf-8")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("models")
    r = sub.add_parser("run")
    r.add_argument("--model", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--scenes", default="1,2,3")
    a = ap.parse_args()
    return {"models": cmd_models, "run": cmd_run}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
