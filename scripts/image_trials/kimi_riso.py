"""Kimi K3.1 Pro draws a risograph scene by writing JavaScript (the drawn-by-code engine, MIT). Kimi has NO file or shell tools here: it only returns a text reply. This harness
sends it the style rules + riso.js API + a reference image, extracts ONE scene.js, statically refuses obviously dangerous code, writes it into a staged copy of the engine (no repo, no
secrets, network aborted for everything except the local render server, Chromium sandbox on) and runs engine/review.mjs there with a sanitised environment and a hard timeout. The
contact sheet goes back to Kimi for up to --corrections fixes; the final scene is rendered to MP4. Key from D:/aai work/secrets/kimi/kimi_api_key.txt, never printed.
Usage: python kimi_riso.py --stage D:/kaggle_upload/riso_stage --ref IMG --out DIR [--corrections 3] [--effort high]"""
from __future__ import annotations

import argparse
import base64
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

KEY_FILE = Path(os.environ.get("KIMI_KEY_FILE", "D:/aai work/secrets/kimi/kimi_api_key.txt"))
PROVIDERS = {"moonshot": ("https://api.moonshot.ai/v1/chat/completions", "kimi-k3.1-pro"),
             "nvidia": ("https://integrate.api.nvidia.com/v1/chat/completions", "moonshotai/kimi-k2.6")}   # NVIDIA build: free, rate-limited trial endpoints
DBC = Path("D:/kaggle_upload/dbc")                       # read-only source of the style docs for the PROMPT
SCENE_REL = "sandbox/maharaj/scene.js"
DEADLINE_S = 3000
TOTAL_S = 4500                                           # hard cap for the whole run including the final render
MAX_SCENE_BYTES = 200_000
BANNED = re.compile(r"\b(fetch|XMLHttpRequest|WebSocket|EventSource|importScripts|eval|sendBeacon|postMessage|indexedDB|localStorage|sessionStorage|navigator|location|document\.cookie|window\.open|require|process|import)\b\s*[(.\[]?|RTC\w*|WebTransport|globalThis|\bself\b|\bwindow\s*\[|\[\s*['\"][^'\"]*['\"]\s*\+|\bnew\s+Function\b|\bFunction\s*\(|<script|Math\.random|Date\.now|new\s+Date|\bnew\s+Worker\b|https?://|\.\./")

BRIEF = """You are the animator. You write ALL the code. A scene is a pure JavaScript function of time t that paints a canvas, in the repo "drawn-by-code" (engine + risograph style). Make a 6-second, 1:1 (logical [1000,1000]), 24 fps scene in the RISOGRAPH style: a SIMPLE STYLED FIGURE of a young Indian saint (Maharaj), seated cross-legged, facing the viewer. The reference image (attached) is the parts sheet of this character (head, torso, arms, crossed legs with a white waist cloth, warm brown skin, short dark hair, calm lowered eyes): match the identity in simplified riso shapes.

The style rules, the Riso API (riso.js), the template, the hands skill and an example of how this repo draws simple riso people follow as DOCUMENTS below.

THE SCENE
- Warm paper ground. A big halftone sun/halo disc behind the head (yellow + pink overprint).
- Flat simple shapes, bold navy brush contour lines, warm brown skin by overprint (pink + yellow screens, a navy shade screen on one side), short dark hair as solid navy, calm lowered eyes, small mouth, bare torso, white waist cloth (paper knockout with navy folds), crossed legs, hands resting on knees.
- Motion on twos, small, 6 s: gentle breathing (torso and shoulders rise 3-4 px); the RIGHT hand (viewer's left) lifts to a blessing gesture (open palm facing the viewer, fingers together) around 2-4 s, holds, lowers by 6 s; the halo pulses slowly; one slow blink; the head stays steady.
- Detail that must read at 1000 px is solid ink or a knockout >= 2.4 px, never a screen. Hands simple but readable.

HARD RULES FOR YOUR REPLY
- Reply with ONE complete file in a single ```js block: the full contents of scene.js (Motion.scene({...}) exactly like the template: fps 24, duration 6, logical [1000,1000], uses ['styles/risograph/riso.js']). No other files, no helper scripts.
- Pure drawing code only: no network, no fetch, no eval, no imports, no URLs, no Date or Math.random (use a seeded deterministic generator if you need noise), no state carried between frames except what the template does.
- The ```js block with the COMPLETE file is mandatory: never stop after the plan. Before the block write at most 5 lines of plan. Keep the code well structured: small functions per body part.
"""

FIX = """Here is the contact sheet of YOUR scene (frames across the 6 seconds) and the engine's automatic review notes (auto.md) below. Look carefully against the reference and the style checklist. List concrete defects first (anatomy of face, hands, arms and shoulder joints, proportions, floating or clipped pieces, ink/overprint rules, readability at 1000 px, motion). Then output the corrected FULL scene.js in one ```js block. Keep the same rules (single file, pure drawing code, deterministic).

AUTO REVIEW:
{auto}
"""


def load_keys(provider: str) -> list:
    if provider == "nvidia":
        spec = importlib.util.spec_from_file_location("nt", Path(__file__).with_name("nvidia_trial.py"))
        nt = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(nt)
        keys = nt.load_keys()
        if not keys:
            raise SystemExit("no usable NVIDIA key found")
        return keys
    key = os.environ.get("MOONSHOT_API_KEY", "").strip()
    if not key and KEY_FILE.is_file():
        key = KEY_FILE.read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"[A-Za-z0-9_.\-]{20,}", key):
        raise SystemExit("no usable Kimi key found")
    return [key]


def scrub(text: str, keys: list) -> str:
    for k in keys:
        text = text.replace(k, "***")
    return text


ALL_KEYS: list = []                                       # every key in use; every model reply is scrubbed against all of them
RUN_END = float("inf")                                   # absolute deadline for model calls, set in main()


def call(keys: list, rnd: int, messages: list, effort: str, provider: str, model: str):
    url = PROVIDERS[provider][0]
    key = keys[rnd % len(keys)]
    body = {"model": model, "messages": messages, "max_tokens": 32000}
    if provider == "moonshot":
        body["reasoning_effort"] = effort
    else:
        body["max_tokens"] = 65536                                 # reasoning models spend 16k+ tokens thinking before the code
        body["stream"] = True                                      # NVIDIA's gateway cuts non-streamed replies at ~300 s (HTTP 504)
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    t0 = time.time()
    scrub_ = lambda s: scrub(s, keys)
    try:
        left = RUN_END - time.time()
        if left < 10:
            return "", None, 0.0, "deadline"
        resp = urllib.request.urlopen(req, timeout=min(900, left))
        if body.get("stream"):
            parts, usage, finish = [], {}, None
            for raw in resp:                                       # server-sent events: "data: {json}" lines, ending with "data: [DONE]"
                if time.time() > RUN_END:
                    return "", None, round(time.time() - t0, 1), "deadline"
                line = raw.decode("utf-8", "replace").strip()
                if not line.startswith("data:") or line == "data: [DONE]":
                    continue
                chunk = json.loads(line[5:])
                usage = chunk.get("usage") or usage
                for ch in chunk.get("choices") or []:
                    parts.append((ch.get("delta") or {}).get("content") or "")
                    finish = ch.get("finish_reason") or finish
            usage = dict(usage or {})
            usage["finish_reason"] = finish
            return scrub("".join(parts), ALL_KEYS + keys), usage, round(time.time() - t0, 1), None
        data = json.loads(resp.read())
        usage = dict(data.get("usage") or {})
        usage["finish_reason"] = data["choices"][0].get("finish_reason")
        return scrub(data["choices"][0]["message"]["content"] or "", ALL_KEYS + keys), usage, round(time.time() - t0, 1), None
    except urllib.error.HTTPError as exc:
        return "", None, round(time.time() - t0, 1), scrub_(f"HTTP {exc.code}")[:60]
    except Exception as exc:
        return "", None, round(time.time() - t0, 1), scrub_(f"{type(exc).__name__}")[:60]


CRITIC_REF = "Describe this character reference sheet precisely for an illustrator who cannot see it: every body part, proportions, hair, face, eyes, skin, clothing, colours. Plain text, at most 150 words."
CRITIC_SHEET = ("The first image is a contact sheet of frames from an animation that should show a young Indian saint seated cross-legged in risograph print style, lifting his right hand in blessing; "
                "the second image is the character reference. List the concrete visual defects you see (face, hands, arms, shoulder joints, legs, proportions, floating or clipped pieces, readability, motion between frames). Plain text, at most 200 words.")


def critique(keys: list, rnd: int, images: list, prompt: str, model: str) -> str:
    """A free vision model looks at images and returns text, for coder models that cannot read images."""
    reply, _, _, err = call(keys, rnd + 1, [{"role": "user", "content": [*images, {"type": "text", "text": prompt}]}], "low", "nvidia", model)
    return reply.strip() if not err else f"(vision critique unavailable: {err})"


def img_part(img: Image.Image, side=1600) -> dict:
    img = img.copy()
    img.thumbnail((side, side))
    buf = io.BytesIO()
    img.convert("RGB").save(buf, "JPEG", quality=90)
    return {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()}}


def documents() -> str:
    def rd(p: str, limit=None):
        t = (DBC / p).read_text(encoding="utf-8")
        return t[:limit] if limit else t
    docs = [("STYLE RULES: .claude/skills/style-risograph/SKILL.md", rd(".claude/skills/style-risograph/SKILL.md")),
            ("API: styles/risograph/riso.js", rd("styles/risograph/riso.js")),
            ("TEMPLATE: styles/risograph/template.js", rd("styles/risograph/template.js")),
            ("HANDS SKILL: .claude/skills/hands/SKILL.md", rd(".claude/skills/hands/SKILL.md", 9000)),
            ("EXAMPLE of simple riso people in this repo (excerpt): sandbox/2026-09-25-physics-history/figure.js", rd("sandbox/2026-09-25-physics-history/figure.js", 14000))]
    return "\n\n".join(f"===== {name} =====\n{text}" for name, text in docs)


def extract_scene(reply: str):
    m = re.search(r"```js\s*(.*?)```", reply, re.S)
    if not m:
        return None, "no ```js block"
    code = m.group(1).strip()
    if len(code.encode()) > MAX_SCENE_BYTES:
        return None, "scene too large"
    if not code.startswith(("Motion.scene", "//", "const", "function", "let", "var")):
        return None, "does not look like a scene"
    bare = re.sub(r"/\*.*?\*/", "", code, flags=re.S)
    bare = re.sub(r"(?m)(^|\s)//[^\n]*", " ", bare)        # words in comments are not code
    bad = BANNED.search(bare)
    if bad:
        return None, f"banned token in scene: {bad.group(0)[:20]!r}"
    if "Motion.scene" not in code:
        return None, "no Motion.scene"
    return code, None


def clean_env() -> dict:
    keep = ("PATH", "SystemRoot", "TEMP", "TMP", "USERPROFILE", "LOCALAPPDATA", "APPDATA", "ProgramFiles", "ProgramFiles(x86)", "WINDIR", "COMSPEC", "PATHEXT")
    keepl = {k.lower() for k in keep}                        # Windows env names are case-insensitive (Python upper-cases them)
    env = {k: v for k, v in os.environ.items() if k.lower() in keepl}
    env["CHROME_PATH"] = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    return env


def run_node(stage: Path, script: str, extra: list, timeout: float):
    """Runs node with a hard timeout and kills the whole process tree (node, Chrome, ffmpeg) on expiry."""
    p = subprocess.Popen(["node", f"engine/{script}", SCENE_REL, *extra], cwd=stage, env=clean_env(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        outp, _ = p.communicate(timeout=max(5, timeout))
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True, timeout=30)
        p.kill()
        try:
            p.communicate(timeout=15)
        except subprocess.TimeoutExpired:
            pass
        raise
    return p.returncode, (outp or "")[-3000:]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--corrections", type=int, default=3)
    ap.add_argument("--effort", default="high", choices=["low", "high", "max"])
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--provider", default="moonshot", choices=sorted(PROVIDERS))
    ap.add_argument("--model", help="model id; default per provider")
    ap.add_argument("--critic", help="free NVIDIA vision model that looks at the images for a text-only coder (e.g. nvidia/nemotron-3.5-super-vl-120b-a12b)")
    a = ap.parse_args()
    if not 0 <= a.corrections <= 3:
        raise SystemExit("--corrections must be 0..3")
    model = a.model or PROVIDERS[a.provider][1]
    keys = load_keys(a.provider)
    critic_keys = load_keys("nvidia") if a.critic else []
    global RUN_END
    ALL_KEYS[:] = keys + critic_keys
    t_start = time.time()
    RUN_END = t_start + DEADLINE_S
    stage, out = Path(a.stage), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    scene_path = stage / SCENE_REL
    ref = img_part(Image.open(a.ref))
    task = BRIEF + "\n\nDOCUMENTS\n" + documents()
    if a.critic:                                                   # text-only coder: the reference arrives as a description
        desc = critique(critic_keys, 0, [ref], CRITIC_REF, a.critic)
        (out / "reference_description.txt").write_text(desc, encoding="utf-8")
        messages = [{"role": "user", "content": "REFERENCE (described, the image is not available to you):\n" + desc + "\n\n" + task}]
    else:
        messages = [{"role": "user", "content": [ref, {"type": "text", "text": task}]}]
    receipt, last_ok, status = [], None, "ok"
    for rnd in range(a.corrections + 1):
        if time.time() - t_start > DEADLINE_S:
            status = "degraded: deadline" if last_ok else "failed: deadline"
            break
        reply, usage, wall, err = call(keys, rnd, messages, a.effort, a.provider, model)
        row = {"round": rnd, "usage": usage, "wall_s": wall}
        receipt.append(row)
        if err:
            row["error"] = err
            status = "degraded: model call failed" if last_ok else "failed: model call"
            break
        (out / f"round{rnd}_reply.txt").write_text(scrub(reply, keys), encoding="utf-8")
        code, why = extract_scene(reply)
        if not code:
            row["error"] = why
            print(json.dumps(row), flush=True)
            if rnd < a.corrections:
                messages = [messages[0], {"role": "assistant", "content": reply},
                            {"role": "user", "content": [{"type": "text", "text": f"Your reply was rejected by the safety filter: {why}. Output the full scene.js again in one ```js block, avoiding that construct (pure drawing code only)."}]}]
                continue
            status = "degraded: unusable scene" if last_ok else "failed: unusable scene"
            break
        scene_path.write_text(code, encoding="utf-8")
        (out / f"round{rnd}_scene.js").write_text(code, encoding="utf-8")
        try:
            rc, log = run_node(stage, "review.mjs", [], min(600, DEADLINE_S - (time.time() - t_start)))
        except subprocess.TimeoutExpired:
            row["error"] = "review timed out"
            status = "degraded: review timeout" if last_ok else "failed: review timeout"
            break
        sheet = stage / "sandbox/maharaj/review/sheet.jpg"
        auto = stage / "sandbox/maharaj/review/auto.md"
        row["review_rc"] = rc
        if rc != 0 or not sheet.exists():
            row["review_log"] = log[-800:]
            (out / f"round{rnd}_review_error.txt").write_text(log, encoding="utf-8")
            if last_ok is None:
                messages = [messages[0], {"role": "assistant", "content": reply},
                            {"role": "user", "content": [{"type": "text", "text": "Your scene failed to run. Engine output:\n" + log[-2500:] + "\nFix it and output the full corrected scene.js in one ```js block."}]}]
                print(json.dumps(row), flush=True)
                continue
            status = "degraded: a correction failed to run"
            break
        last_ok = code
        sh = Image.open(sheet)
        sh.save(out / f"round{rnd}_sheet.jpg")
        autot = auto.read_text(encoding="utf-8")[:3000] if auto.exists() else ""
        (out / f"round{rnd}_auto.md").write_text(autot, encoding="utf-8")
        print(json.dumps(row), flush=True)
        if rnd < a.corrections:
            if a.critic:
                notes = critique(critic_keys, rnd, [img_part(sh, 1800), ref], CRITIC_SHEET, a.critic)
                (out / f"round{rnd}_critique.txt").write_text(notes, encoding="utf-8")
                fix = FIX.replace("Here is the contact sheet of YOUR scene", "A reviewer looked at the contact sheet of YOUR scene").format(auto=autot) + "\nREVIEWER NOTES:\n" + notes
                messages = [messages[0], {"role": "assistant", "content": reply}, {"role": "user", "content": fix}]
            else:
                messages = [messages[0], {"role": "assistant", "content": reply},
                            {"role": "user", "content": [img_part(sh, 1800), ref, {"type": "text", "text": FIX.format(auto=autot)}]}]
    if last_ok is None and status == "ok":
        status = "failed: no scene ran"
    if last_ok and not a.no_render:
        scene_path.write_text(last_ok, encoding="utf-8")
        mp4 = stage / "sandbox/maharaj/out/maharaj_riso.mp4"
        if mp4.exists():
            mp4.unlink()                                                   # never accept a stale file
        left = TOTAL_S - (time.time() - t_start)
        try:
            if left < 60:
                raise subprocess.TimeoutExpired("render", 0)
            rc, log = run_node(stage, "render.mjs", ["--size", "1080", "--out", "sandbox/maharaj/out/maharaj_riso.mp4"], min(1500, TOTAL_S - (time.time() - t_start)))
        except subprocess.TimeoutExpired:
            rc, log = 1, "render timed out"
        ok = rc == 0 and mp4.exists() and mp4.stat().st_size > 10_000
        receipt.append({"render_rc": rc, "mp4": ok})
        if ok:
            (out / "maharaj_riso.mp4").write_bytes(mp4.read_bytes())
        else:
            status = "failed: render"
            (out / "render_error.txt").write_text(log, encoding="utf-8")
    receipt.append({"status": status})
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2))
    print("status:", status, flush=True)
    return 0 if status == "ok" else (3 if status.startswith("degraded") else 1)


if __name__ == "__main__":
    raise SystemExit(main())
