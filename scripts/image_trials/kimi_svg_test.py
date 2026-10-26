"""Kimi K3.1 Pro "image by code" test: ask for flat SVG assets, save the SVG, render to PNG with resvg. The key is read from D:/aai work/secrets/kimi/kimi_api_key.txt (or MOONSHOT_API_KEY),
never printed, scrubbed from every message. The SVG is data only; nothing the model writes is executed. Usage: python kimi_svg_test.py --out DIR [--model kimi-k3.1-pro] [--effort high]"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

KEY_FILE = Path(os.environ.get("KIMI_KEY_FILE", "D:/aai work/secrets/kimi/kimi_api_key.txt"))
URL = "https://api.moonshot.ai/v1/chat/completions"

TASKS = {
    "border": ("Draw an ornamental page border for a devotional Indian storybook illustration as a single SVG, viewBox 0 0 1600 900. Flat vector style: a thick outer frame with a repeating "
               "lotus-petal and diamond pattern band, small corner flourishes, colours terracotta red, deep blue, mustard yellow and ivory. The centre must be empty (transparent) so a picture can sit inside. "
               "No text. Output ONLY the SVG code in one ```svg block."),
    "house": ("Draw a flat-vector background plate for a village scene as a single SVG, viewBox 0 0 1600 900: a single-storey mud-walled village house with a red clay-tiled sloping roof, a wooden door "
              "with a dark open doorway, one small barred window, a dirt road curving from the lower right towards the horizon, a few round green trees and a pale sky. Warm earthy flat colours, simple shapes, "
              "thin dark outlines, no gradients, no people, no text. Output ONLY the SVG code in one ```svg block."),
    "house_kalighat": ("Draw the same kind of village scene as a single SVG, viewBox 0 0 1600 900, in the style of a Kalighat / Bengal Pattachitra folk painting: a single-storey mud-walled house with a red clay-tiled sloping roof, a wooden door with a dark open doorway, a small barred window, a dirt road curving from the lower right, two or three simple trees. "
                       "Style rules: confident flowing brush-like contour lines with varying width (use filled paths for the contours, not uniform strokes), flat bold colour fills in terracotta red, ochre, indigo, green and ivory, "
                       "a soft darker wash band on one side of each form to suggest rounded volume, minimal detail, sparse composition with the house large and the background reduced to a few simple shapes, "
                       "a plain warm ivory paper ground with a very subtle paper texture using an SVG feTurbulence filter. No people, no text. Output ONLY the SVG code in one ```svg block."),
}


def balance(key):
    req = urllib.request.Request("https://api.moonshot.ai/v1/users/me/balance", headers={"Authorization": "Bearer " + key})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=30).read()).get("data")
    except Exception as exc:
        return {"error": type(exc).__name__}


def load_key() -> str:
    key = os.environ.get("MOONSHOT_API_KEY", "").strip()
    if not key and KEY_FILE.is_file():
        key = KEY_FILE.read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"[A-Za-z0-9_.\-]{20,}", key):
        raise SystemExit("no usable Kimi key found")
    return key


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="kimi-k3.1-pro")
    ap.add_argument("--tasks", default="border,house")
    ap.add_argument("--effort", default="high", choices=["low", "high", "max"])
    a = ap.parse_args()
    key = load_key()
    scrub = lambda s: s.replace(key, "***")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    receipt = []
    before = balance(key)
    print("balance before:", before, flush=True)
    for name in a.tasks.split(","):
        prompt = TASKS[name]
        body = {"model": a.model, "reasoning_effort": a.effort, "messages": [{"role": "user", "content": prompt}], "max_tokens": 16000}
        req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
        t0 = time.time()
        row = {"task": name, "model": a.model, "effort": a.effort}
        try:
            data = json.loads(urllib.request.urlopen(req, timeout=600).read())
            msg = data["choices"][0]["message"]["content"] or ""
            row["usage"] = data.get("usage")
            m = re.search(r"```svg\s*(.*?)```", msg, re.S) or re.search(r"(<svg.*?</svg>)", msg, re.S)
            svg = (m.group(1) if m else "").strip()
            if svg.startswith("<svg") and svg.endswith("</svg>"):
                (out / f"{name}.svg").write_text(svg, encoding="utf-8")
                row["svg_chars"] = len(svg)
                try:
                    import resvg_py
                    png = resvg_py.svg_to_bytes(svg_string=svg, width=1600)
                    (out / f"{name}.png").write_bytes(bytes(png))
                    row["rendered"] = True
                except Exception as exc:
                    row["render_error"] = f"{type(exc).__name__}: {exc}"[:200]
            else:
                row["error"] = "no complete <svg> in the reply: " + msg[:200]
        except urllib.error.HTTPError as exc:
            row["error"] = scrub(f"HTTP {exc.code} {exc.read().decode('utf-8', 'replace')[:300]}")
        except Exception as exc:
            row["error"] = scrub(f"{type(exc).__name__}: {exc}"[:300])
        row["wall_s"] = round(time.time() - t0, 1)
        print(scrub(json.dumps(row))[:500], flush=True)
        receipt.append(row)
        (out / "receipt.json").write_text(scrub(json.dumps(receipt, indent=2)), encoding="utf-8")
    after = balance(key)
    print("balance after:", after, flush=True)
    receipt.append({"balance_before": before, "balance_after": after})
    (out / "receipt.json").write_text(scrub(json.dumps(receipt, indent=2)), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
