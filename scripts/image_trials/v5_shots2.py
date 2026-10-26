"""V5 Phase 1, JSON route (D-015 + owner choice 2026-10-25). Kimi K3.1 Pro writes ONE Blender shot builder once plus shot JSON files; after that only JSON.
  author  - one Kimi call: builder.py + SA/SB/SC JSON. Saved, JSON validated, builder guard-checked. NOTHING is executed.
  run     - only if APPROVED.json holds the builder's sha256 (written after Codex's full review and the owner's yes): builds and renders each valid shot.
  revise  - Kimi sees a shot's contact sheet + its JSON and returns a new JSON only (builder unchanged); max 4 generations per shot incl. author.
Every Kimi call: input tokens counted by Moonshot's endpoint, worst case reserved in the ledger (phase P1, $15 cap) before dispatch.
Usage: python v5_shots.py author | run [--shot SA] | revise --shot SA"""
from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import io
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
INBOX = Path("D:/aai work/v5_inbox")
OUT = Path("D:/kaggle_upload/v5_phase1_v2")
LEDGER = Path("D:/kaggle_upload/v5_ledger.jsonl")
KEY_FILE = Path("D:/aai work/secrets/kimi/kimi_api_key.txt")
API = "https://api.moonshot.ai/v1"
MODEL, MAX_TOKENS, PHASE, MAX_GEN = "kimi-k3.1-pro", 32000, "P1", 4
LOOK_REF = Path("D:/kaggle_upload/v5_phase1/SB/gen2/contact.jpg")      # owner-approved flat-colour look (D-016)


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


blender, ledger_mod, schema = load("v5_blender"), load("v5_ledger"), load("v5_schema2")

P, C = INBOX / "prepped", INBOX / "clean"
SHOTS = {
    "SA": {"assets": {"sky": C / "A1_bg_sky.png", "temple": P / "A1_mid_temple.png", "frame": P / "A1_fg_frame.png", "fx": C / "FX_light_smoke.png"},
           "brief": "Temple establishing shot, one segment. A real cinematic dolly: zoom 1.0 to at least 1.2 with ease_in_out and a slight pan, parallax so the far sky "
                    "barely moves, the temple moves moderately and the pillar frame moves most (it must visibly sweep outward). Leaves in the frame layer sway. "
                    "Warm golden gloss and a little dust. The fx image (light rays and smoke on black) added with blend add at low opacity. Grounded and alive."},
    "SB": {"assets": {"wide": P / "C1_p1_wide.png", "bow": P / "C1_p2_bow.png", "bless": P / "C1_p3_bless.png", "react": P / "C1_p4_react.png",
                      "sky": C / "A1_bg_sky.png"},
           "brief": "Maharaj blesses a devotee, told by four staged poses (frames 1-36 wide approach, 37-72 bow, 73-108 bless, 109-144 devotee reaction). "
                    "NO slow cross-dissolve between full-body poses (it makes ghosts): use a short slide or pan_bridge transition (3-6 frames) or a cut on a camera "
                    "push. Give it a grounded backdrop (warm parchment gradient, a floor line, a soft halo behind Maharaj in the blessing segment). Camera moves in every "
                    "segment: pan toward Maharaj in the approach, tilt down at the bow, push in on the raised hand at the blessing, slow push on the face at the end. "
                    "Characters breathe gently (idle). In the blessing segment try a soft_warp on the right hand region of the bless pose (a small lift) - it is optional."},
    "SC": {"assets": {"offer": C / "C2_p1_offer.png", "hands": C / "C2_p2_hands.png", "hold": C / "C2_p3_hold.png"},
           "brief": "Maharaj receives a brass pot: frames 1-48 offer, 49-96 hands close-up, 97-144 Maharaj holding the pot. Full-frame images. Real camera moves "
                    "in every segment (push, drift, pull-back) with eased motion; a short slide or pan_bridge between segments (no slow dissolve); warm gloss and a little dust."},
}

SEMANTICS = """SHOT JSON MEANING (the builder must implement exactly this; the look is the ORIGINAL flat colours of the images, no print effect):
- Frame units: at camera zoom 1 the visible frame spans x -1..1 (left..right) and y -0.5625..0.5625 (bottom..top), 16:9. Layer x,y is the image centre.
- scale 1 = the image's width equals the frame width at zoom 1; height follows the image aspect.
- depth 0 (near) .. 10 (far): true parallax - when the camera pans or zooms a layer moves less the larger its depth. Larger depth is drawn behind.
- opacity default 1; blend "normal" (alpha over) or "add" (additive light).
- move: dx, dy, dscale applied with easing across the segment (layer drift).
- backdrop: a vertical gradient top->bottom behind everything; floor_y (optional) draws a soft floor band below that height in floor_color; halo (optional) a soft
  radial glow at x,y with radius and colour, intensity and a slow pulse of pulse_period_sec.
- idle (per layer): breathing - scale the layer about its BOTTOM edge by 1 +/- amplitude with the given period (seated figures breathe, they do not float).
- sway (per layer): rotate the layer about its TOP edge by +/- angle_deg with the period and a phase offset (hanging leaves).
- soft_warp (per layer, optional): subdivide the plane (e.g. 16x16) and, between its frames, smoothly lift/rotate the region around uv (u,v in 0..1 of the image, v up)
  within radius by rotate_deg and dx,dy using a falloff (Hook-style or vertex-group deformation). Keep it small. No seams, no extra images.
- segments are contiguous hard cuts at their boundaries unless a transition says otherwise; only that segment's layers are visible.
- transitions: after_segment N (0-based) joins segment N to N+1: kind cut | slide (the incoming layers slide in from `direction` over `frames`, with a quick
  directional motion blur) | pan_bridge (the camera pans/tilts quickly over `frames` while the incoming pose appears). NEVER a slow cross-dissolve of two full-body poses.
- camera start/end: x, y pan in frame units, zoom >1 = closer; ease linear | ease_in_out | ease_out | ease_in (Bezier keyframes).
- atmosphere: gloss 0..1 = warm glow/bloom made in the compositor (Glare node, type 'Fog Glow' or 'Bloom', tinted warm_tint, default #FFB84D); dust 0..1 = slow
  drifting soft golden motes (no particle systems: use drifting small transparent planes or a noise-based overlay); vignette 0..1 = gentle edge darkening.
- on_twos true: hold each drawing for 2 frames."""

AUTHOR = """You are the animator and Blender technical artist; you write ALL the code. Write ONE reusable Blender 5.2 Python BUILDER (version 2) that turns a
shot JSON into a scene, plus the three shot JSON files below. The owner found the first builder's shots too basic (tiny zooms, static poses, empty
backgrounds); this one must make shots feel alive. The builder will be reviewed line by line and then reused for every future shot, so make it
clean, general and well commented. It runs headless with EEVEE; 1280x720, 24 fps and frames 1-144 are set by the runner after your code.

THE BUILDER RECEIVES (already defined before your code runs):
- SHOT: the shot dictionary (already parsed, same structure as the JSON).
- ASSET(name): returns the image file path for an asset name. Load images ONLY as bpy.data.images.load(ASSET(name)).

{semantics}

JSON SCHEMA (shot files must validate):
{schema}

HARD RULES (a guard refuses the builder otherwise)
- Imports only bpy, math, mathutils, random. No os, no files, no paths in strings, no open/exec/eval/getattr/setattr, no names starting with
  an underscore, no bpy.ops.wm, bpy.app, bpy.utils, bpy.path, no drivers, no handlers, no text blocks, no libraries, no saving, no File Output node,
  no image save/save_render, no render.render. Delete the default objects first; create the camera and set scene.camera.
- Image planes use unlit/emission shading so colours stay flat; respect alpha. Keyframes only (no per-frame Python). Fixed random seed if any.
- Keep the images' ORIGINAL flat colours (no print effect). The attached sheet shows the approved look from builder 1.
- BLENDER 5.2.3 FACTS (queried from the owner's Blender; use only these, names not indices): the compositor node tree is created with bpy.data.node_groups.new(name,'CompositorNodeTree') and assigned to scene.compositing_node_group; compositor math/mix/texture nodes are ShaderNodeMath, ShaderNodeMix, ShaderNodeMixRGB, ShaderNodeTexNoise; CompositorNodeAlphaOver sockets Background, Foreground, Factor; CompositorNodeGlare is driven by INPUT sockets: 'Type' (menu; set .default_value to the string 'Fog Glow', 'Bloom', 'Simple Star', 'Streaks' or 'Ghosts'), 'Quality' ('Medium'), 'Threshold', 'Smoothness', 'Strength', 'Saturation', 'Tint' (RGBA), 'Size'; CompositorNodeBlur sockets Image, Size (vector), Type (menu 'Gaussian' or 'Flat'); CompositorNodeDBlur sockets Image, Samples, Center, Rotation, Scale, Amount, Direction; CompositorNodeVecBlur; CompositorNodeColorBalance, CompositorNodeHueSat, CompositorNodeBrightContrast, CompositorNodeTranslate, CompositorNodeScale, CompositorNodeTransform (Image, X, Y, Angle, Scale), CompositorNodeRGB, CompositorNodeRLayers, CompositorNodeSetAlpha. Render engine name is 'BLENDER_EEVEE'. Camera types PERSP/ORTHO. Keyframe interpolation names LINEAR, BEZIER, SINE, QUAD, CUBIC and easing AUTO/EASE_IN/EASE_OUT/EASE_IN_OUT. Modifiers SUBSURF, HOOK (props object, vertex_group, falloff_type, falloff_radius, strength, center) and LATTICE exist; vertex groups work.

SHOTS (assets with pixel sizes; thumbnails attached in this order after the reference sheet)
{shots}

REPLY FORMAT: at most 6 lines of plan, then ONE ```python block (the builder), then three ```json blocks, each starting with its "shot_id" (SA, SB, SC)."""

REVISE = """Here is the contact sheet of shot {sid} rendered by the approved builder v2 from the JSON below (frames 1, 24, 48, 72, 96, 120, 144).
The builder can no longer change; improve the shot ONLY by changing the JSON (positions, scales, depths, camera moves, segment timing, atmosphere).
List the concrete visual problems first (framing, layer order, parallax, cut timing, readability of the action, life and motion), then reply with the
complete corrected JSON in ONE ```json block.

BRIEF: {brief}

CURRENT JSON:
{current}"""


def key() -> str:
    k = KEY_FILE.read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"[A-Za-z0-9_.\-]{20,}", k):
        raise SystemExit("no usable Kimi key")
    return k


def img_part(src, side=1600) -> dict:
    im = Image.open(src) if isinstance(src, (str, Path)) else src.copy()
    im.thumbnail((side, side))
    if im.mode == "RGBA":
        bg = Image.new("RGBA", im.size, (200, 200, 200, 255))
        bg.alpha_composite(im)
        im = bg
    buf = io.BytesIO()
    im.convert("RGB").save(buf, "JPEG", quality=85)
    return {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()}}


def post(path: str, body: dict, k: str, timeout: float):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode(), headers={"Authorization": "Bearer " + k, "Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())


def call(k: str, led, messages: list, effort: str):
    try:                                                                # exact input count for this payload; refuse if counting fails
        counted = int(post("/tokenizers/estimate-token-count", {"model": MODEL, "messages": messages}, k, 120)["data"]["total_tokens"])
    except Exception as exc:
        raise ledger_mod.Refused(f"token count failed ({type(exc).__name__})")
    rid = led.reserve(PHASE, MODEL, counted, MAX_TOKENS)
    t0 = time.time()
    try:
        data = post("/chat/completions", {"model": MODEL, "reasoning_effort": effort, "messages": messages, "max_tokens": MAX_TOKENS}, k, 900)
    except urllib.error.HTTPError as exc:
        led.unknown(rid, f"HTTP {exc.code}")                            # no status is assumed to be free
        return None, None, f"HTTP {exc.code}", round(time.time() - t0, 1)
    except Exception as exc:
        led.unknown(rid, type(exc).__name__)
        return None, None, type(exc).__name__, round(time.time() - t0, 1)
    usage = data.get("usage") or {}
    if "prompt_tokens" in usage and "completion_tokens" in usage:
        led.settle(rid, usage)
    else:
        led.unknown(rid, "no usage in reply")
    return (data["choices"][0]["message"]["content"] or "").replace(k, "***"), usage, None, round(time.time() - t0, 1)


def blocks(reply: str, lang: str) -> list[str]:
    return [b.strip() for b in re.findall(rf"```{lang}\s*(.*?)```", reply, re.S)]


def state() -> dict:
    f = OUT / "state.json"
    return json.loads(f.read_text()) if f.exists() else {"generations": {s: 0 for s in SHOTS}}


def save_state(st: dict):
    (OUT / "state.json").write_text(json.dumps(st, indent=2))


def save_shot(sid: str, shot: dict, gen: int) -> list[str]:
    problems = schema.validate(shot, set(SHOTS[sid]["assets"]))
    d = OUT / sid / f"gen{gen}"
    d.mkdir(parents=True, exist_ok=True)
    (d / "shot.json").write_text(json.dumps(shot, indent=2))
    (d / "validation.txt").write_text("\n".join(problems) or "valid")
    return problems


def claim(led, sid_list: list, need_zero: bool, limit: int) -> dict:
    """Counts the attempt durably BEFORE the paid call (under the ledger lock), so a crash or retry cannot buy extra generations."""
    with led._locked():
        st = state()
        for sid in sid_list:
            g = st["generations"].get(sid, 0)
            if (need_zero and g) or g >= limit:
                raise SystemExit(f"{sid}: generation limit reached or author already attempted (gen {g})")
        for sid in sid_list:
            st["generations"][sid] = st["generations"].get(sid, 0) + 1
        OUT.mkdir(parents=True, exist_ok=True)
        save_state(st)
    return st


def cmd_author(a, k, led) -> int:
    st = claim(led, list(SHOTS), need_zero=True, limit=MAX_GEN)        # author = generation 1 of every shot, counted before dispatch
    shots_txt = "\n".join(f"{sid}: {s['brief']}\n  assets: " + ", ".join(f"{n} {Image.open(p).size[0]}x{Image.open(p).size[1]}"
                          + (" (transparent)" if Image.open(p).mode == "RGBA" else "") for n, p in s["assets"].items()) for sid, s in SHOTS.items())
    text = AUTHOR.format(semantics=SEMANTICS, schema=json.dumps(schema.SCHEMA), shots=shots_txt)
    content = [{"type": "text", "text": text}, img_part(LOOK_REF)] + [img_part(p, 640) for s in SHOTS.values() for p in s["assets"].values()]
    reply, usage, err, wall = call(k, led, [{"role": "user", "content": content}], a.effort)
    OUT.mkdir(parents=True, exist_ok=True)
    if err:
        print("author call failed:", err)
        return 1
    (OUT / "author_reply.txt").write_text(reply, encoding="utf-8")
    py = blocks(reply, "python")
    if len(py) != 1:
        print("expected exactly one python block, got", len(py))
        return 1
    builder = py[0]
    (OUT / "builder.py").write_text(builder, encoding="utf-8")
    sha = hashlib.sha256(builder.encode()).hexdigest()
    guard = blender.check(builder)
    (OUT / "builder_guard.txt").write_text("\n".join(guard) or "guard: no findings")
    result = {"usage": usage, "wall_s": wall, "builder_sha256": sha, "guard_findings": guard, "shots": {}}
    seen = {}
    for raw in blocks(reply, "json"):
        try:
            shot = json.loads(raw)
        except json.JSONDecodeError:
            continue
        sid = shot.get("shot_id") if isinstance(shot, dict) else None
        if sid in SHOTS:
            seen[sid] = seen.get(sid, 0) + 1
            result["shots"][sid] = save_shot(sid, shot, 1) or "valid"
    complete = all(seen.get(sid) == 1 and result["shots"].get(sid) == "valid" for sid in SHOTS)
    result["complete"] = complete
    (OUT / "author_result.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2)[:1500])
    print("NOTHING executed.", "Next: Codex full review of builder.py, then owner approval -> APPROVED.json" if complete
          else "INCOMPLETE author output (missing, duplicate or invalid shot JSON); kept for review.")
    return 0 if complete else 1


def approved_builder() -> str:
    builder = (OUT / "builder.py").read_text(encoding="utf-8")
    ok = OUT / "APPROVED.json"
    if not ok.exists() or json.loads(ok.read_text()).get("builder_sha256") != hashlib.sha256(builder.encode()).hexdigest():
        raise SystemExit("builder is not approved (APPROVED.json missing or hash mismatch)")
    return builder


def contact(frames_dir: Path) -> Image.Image:
    picks = [1, 24, 48, 72, 96, 120, 144]
    sheet = Image.new("RGB", (448 * 4, 272 * 2), "white")
    d = ImageDraw.Draw(sheet)
    for n, i in enumerate(picks):
        x, y = (n % 4) * 448, (n // 4) * 272
        sheet.paste(Image.open(frames_dir / f"f_{i:04d}.png").convert("RGB").resize((448, 252)), (x, y + 20))
        d.text((x + 4, y + 4), f"frame {i}  ({(i - 1) / 24:.2f} s)", fill="black")
    return sheet


def run_shot(builder: str, sid: str, gen: int) -> tuple[bool, str]:
    d = OUT / sid / f"gen{gen}"
    shot = json.loads((d / "shot.json").read_text())
    if schema.validate(shot, set(SHOTS[sid]["assets"])):
        return False, "invalid JSON"
    ok, log = blender.build(builder, SHOTS[sid]["assets"], d, shot=shot)
    if not ok:
        return False, "build failed: " + log[-600:]
    t0 = time.time()
    mp4, msg = blender.render(d)
    if not mp4:
        return False, msg[:600]
    contact(d / "frames").save(d / "contact.jpg", quality=88)
    return True, f"rendered in {time.time() - t0:.0f} s"


def cmd_run(a, k, led) -> int:
    builder = approved_builder()
    st = state()
    for sid in ([a.shot] if a.shot else SHOTS):
        gen = st["generations"].get(sid, 0)
        if not gen:
            print(sid, "no JSON yet")
            continue
        ok, msg = run_shot(builder, sid, gen)
        print(sid, f"gen{gen}", "OK" if ok else "FAILED", msg)
    return 0


def cmd_revise(a, k, led) -> int:
    builder = approved_builder()
    sid, count = a.shot, state()["generations"].get(a.shot, 0)
    gen = count
    while gen > 1 and not (OUT / sid / f"gen{gen}" / "contact.jpg").exists():     # latest generation that actually rendered
        gen -= 1
    d = OUT / sid / f"gen{gen}"
    sheet = d / "contact.jpg"
    if not sheet.exists():
        raise SystemExit(f"{sid} gen{gen} has no render yet; run it first")
    text = REVISE.format(sid=sid, brief=SHOTS[sid]["brief"], current=(d / "shot.json").read_text())
    if a.note:
        text += "\n\nOWNER FEEDBACK (measured on the render): " + a.note
    claim(led, [sid], need_zero=False, limit=MAX_GEN)                  # counted before dispatch; a failed paid attempt still counts
    reply, usage, err, wall = call(k, led, [{"role": "user", "content": [img_part(sheet, 1800), img_part(LOOK_REF, 900), {"type": "text", "text": text}]}], a.effort)
    if err:
        print("revise call failed:", err)
        return 1
    nd = OUT / sid / f"gen{count + 1}"
    nd.mkdir(parents=True, exist_ok=True)
    (nd / "reply.txt").write_text(reply, encoding="utf-8")
    js = blocks(reply, "json")
    if len(js) != 1:
        print("expected one json block")
        return 1
    try:
        problems = save_shot(sid, json.loads(js[0]), count + 1)
    except json.JSONDecodeError as exc:
        print("bad JSON:", exc)
        return 1
    if problems:
        print("invalid JSON:", problems[:5])
        return 1
    ok, msg = run_shot(builder, sid, count + 1)
    print(sid, f"gen{count + 1}", "OK" if ok else "FAILED", msg, "| P1 committed $", round(led.committed(PHASE), 4))
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["author", "run", "revise"])
    ap.add_argument("--shot", choices=sorted(SHOTS))
    ap.add_argument("--effort", default="high", choices=["low", "high", "max"])
    ap.add_argument("--note", default="", help="owner feedback appended to the revise prompt")
    a = ap.parse_args()
    if a.cmd == "revise" and not a.shot:
        raise SystemExit("revise needs --shot")
    k, led = key(), ledger_mod.Ledger(LEDGER)
    try:
        return {"author": cmd_author, "run": cmd_run, "revise": cmd_revise}[a.cmd](a, k, led)
    except ledger_mod.Refused as exc:
        print("REFUSED by money guard:", exc)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

