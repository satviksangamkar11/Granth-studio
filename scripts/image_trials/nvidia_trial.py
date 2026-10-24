"""Try reference-based image models through the free NVIDIA API catalog from this PC (no GPU, no Kaggle). Personal prototyping only (owner decision D-012).

  python scripts/image_trials/nvidia_trial.py check-key
  python scripts/image_trials/nvidia_trial.py probe  --model flux2-klein-4b
  python scripts/image_trials/nvidia_trial.py run    --model flux2-klein-4b --scenes 1,2,3 --out D:/kaggle_upload/trial_klein

KEYS: read ONLY from the environment, never from a file, never printed, never written to a receipt:
  NVIDIA_API_KEY            one key, or
  NVIDIA_API_KEYS           several keys separated by commas (accounts of the owner)
A later key is used only when the earlier one is rejected as invalid (HTTP 401/403); the script never rotates keys to get around a rate limit (429 stops the run).

What it does: sends the owner's reference images (assets/pilot_refs/set_v1, first = the person in image 1 ...) with a scene prompt built from the frozen style v1 prefix/suffix
(canon/style.yaml) plus a plain description of who stands where, saves each result as a PNG and writes receipt.json (model, endpoint, reference hashes, prompt, seed, output
hash, time). A PASS means an image came back: whether it looks right and keeps each person's identity is judged by the owner.

The request field names of the hosted endpoints could not be read from NVIDIA's script-rendered pages, so BODY_BUILDERS are best guesses; `probe` sends one real request and prints the
server's own answer (status and the first 600 characters of the body, with any key-like text removed) so the builder can be corrected.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from granthstudio.style import compose, load_style  # noqa: E402

REFS = ROOT / "assets" / "pilot_refs" / "set_v1"
HOST = "https://ai.api.nvidia.com/v1/genai"
KEY_PATTERN = re.compile(r"nvapi-[A-Za-z0-9_\-]{10,}")
KEY_SYNTAX = re.compile(r"nvapi-[A-Za-z0-9_\-]{20,}")
ALLOWED_PREFIXES = ("https://ai.api.nvidia.com/", "https://integrate.api.nvidia.com/")


# ------------------------------------------------------------------ keys

def keys_from_env(environ: dict | None = None) -> list[str]:
    """Keys in order; a value that is not exactly one well-formed key (stray spaces, newlines, extra text) is dropped, never sent and never echoed."""
    environ = os.environ if environ is None else environ
    found = [k.strip() for k in environ.get("NVIDIA_API_KEYS", "").split(",") if k.strip()]
    single = environ.get("NVIDIA_API_KEY", "").strip()
    candidates = ([single] if single else []) + [k for k in found if k != single]
    return [k for k in candidates if KEY_SYNTAX.fullmatch(k)]


def scrub(text: str, keys: list[str]) -> str:
    text = KEY_PATTERN.sub("***", text)
    for key in keys:
        text = text.replace(key, "***") if len(key) >= 8 else text
    return text


# ------------------------------------------------------------------ models (field names unverified: see the module docstring)

def data_uri(path: Path) -> str:
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def body_klein(prompt: str, refs: list[Path], seed: int, size: tuple[int, int]) -> dict:
    return {"prompt": prompt, "image": [data_uri(p) for p in refs], "width": size[0], "height": size[1], "seed": seed, "steps": 4}


def body_kontext(prompt: str, refs: list[Path], seed: int, size: tuple[int, int]) -> dict:
    return {"prompt": prompt, "image": data_uri(refs[0]), "aspect_ratio": "match_input_image", "seed": seed, "steps": 30, "cfg_scale": 3.5}


MODELS = {
    "flux2-klein-4b": {"url": f"{HOST}/black-forest-labs/flux.2-klein-4b", "builder": body_klein, "max_refs": 4, "size": (1152, 768), "note": "multi-reference editing; up to 4 images"},
    "flux1-kontext-dev": {"url": f"{HOST}/black-forest-labs/flux.1-kontext-dev", "builder": body_kontext, "max_refs": 1, "size": (1024, 1024), "note": "single image only: baseline"},
}


def extract_image(response: dict) -> bytes | None:
    """The generated image from any of the response shapes the NVIDIA genai endpoints use."""
    candidates = []
    if isinstance(response.get("artifacts"), list) and response["artifacts"]:
        candidates.append(response["artifacts"][0].get("base64"))
    candidates += [response.get("image"), response.get("b64_json")]
    if isinstance(response.get("images"), list) and response["images"]:
        candidates.append(response["images"][0] if isinstance(response["images"][0], str) else response["images"][0].get("base64"))
    if isinstance(response.get("data"), list) and response["data"]:
        candidates.append(response["data"][0].get("b64_json"))
    for value in candidates:
        if isinstance(value, str) and len(value) > 100:
            try:
                return base64.b64decode(value.split(",", 1)[-1])
            except ValueError:
                return None
    return None


PNG_MAGIC = bytes([0x89]) + b"PNG" + bytes([13, 10, 26, 10])
JPEG_MAGIC = bytes([0xFF, 0xD8, 0xFF])


def looks_like_an_image_without_a_secret(data: bytes, keys: list[str]) -> bool:
    """PNG or JPEG magic bytes, and no key bytes anywhere inside (a response must never be able to write a secret into a saved file)."""
    if not (data[:8] == PNG_MAGIC or data[:3] == JPEG_MAGIC):
        return False
    if any(key.encode() in data for key in keys):
        return False
    return KEY_PATTERN.search(data.decode("latin-1")) is None


# ------------------------------------------------------------------ scenes (what the TEXT of Adhyay 1 says; the old SDXL keyframes had content gaps)

STYLE_CLAUSE = ("Keep the exact illustration style, line weight, colours and aged paper of the reference images. Each person must look exactly like his reference image: "
                "same face, age, build and clothing.")
SCENES = {
    1: {"refs": ["maharaj.jpg", "location.jpg"],
        "text": ("Image 1 is the young man, image 2 is the village road and house. Draw him sitting cross-legged on the dusty road in front of the house, among scattered used leaf plates, "
                 "lifting a few grains of rice from a leaf plate toward his mouth, a small clay pipe in his other hand, calm face. Bright daylight.")},
    2: {"refs": ["maharaj.jpg", "bankatlal.jpg", "damodarpant.jpg", "location.jpg"],
        "text": ("Image 1 is the young man, image 2 is the merchant in the turban and long coat, image 3 is the clerk in the cap, image 4 is the village road and house. "
                 "The young man sits cross-legged on the road among scattered leaf plates, eating a grain of rice. The merchant and the clerk stand on the road a few steps away, watching him in amazement. "
                 "Bright daylight.")},
    3: {"refs": ["maharaj.jpg", "devidas.jpg", "bankatlal.jpg", "damodarpant.jpg", "location.jpg"],
        "text": ("Image 1 is the young man, image 2 is the householder with the sacred thread, image 3 is the merchant in the turban, image 4 is the clerk in the cap, image 5 is the house and road. "
                 "At the doorway of the house the householder sets a large plate of sweet dishes on the ground before the young man, who sits cross-legged and eats calmly. "
                 "The merchant and the clerk stand nearby, watching with respect. Bright daylight.")},
}


def scene_prompt(scene: int) -> str:
    style = load_style(_Project())
    return compose(style, f"{SCENES[scene]['text']} {STYLE_CLAUSE}")


class _Project:                                                        # load_style only needs the canon directory
    canon_dir = ROOT / "canon"


# ------------------------------------------------------------------ HTTP

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """A redirect would forward the Authorization header to wherever it points: refuse them all (the answer becomes an HTTP 3xx error)."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


def _send(request: urllib.request.Request, timeout: int) -> tuple[int, str]:
    """(status, body). Never raises with a secret in the message: any transport or header problem becomes (0, 'request failed: <ExceptionType>')."""
    if not request.full_url.startswith(ALLOWED_PREFIXES):
        return 0, "request failed: URL outside the approved NVIDIA hosts"
    try:
        with _OPENER.open(request, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")
    except (urllib.error.URLError, OSError, ValueError) as exc:
        return 0, f"request failed: {type(exc).__name__}"


def http_post(url: str, key: str, body: dict, timeout: int = 180) -> tuple[int, str]:
    request = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), method="POST",
                                     headers={"Authorization": f"Bearer {key}", "Accept": "application/json", "Content-Type": "application/json"})
    return _send(request, timeout)


def call(model: dict, body: dict, keys: list[str], post=http_post) -> tuple[int, dict | str, int]:
    """(status, parsed response or text, index of the key used). Moves to the next key only on 401/403; stops on anything else (429 included)."""
    last: tuple[int, str] = (0, "no key")
    for index, key in enumerate(keys):
        status, text = post(model["url"], key, body)
        last = (status, text)
        if status in (401, 403):
            continue
        try:
            return status, json.loads(text), index
        except json.JSONDecodeError:
            return status, text, index
    return last[0], last[1], len(keys) - 1


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def cmd_check_key(args, opener=None) -> int:
    keys = keys_from_env()
    if not keys:
        print("no usable key: set NVIDIA_API_KEY (or NVIDIA_API_KEYS) to well-formed nvapi-... keys in your Windows environment, then open a new terminal")
        return 2
    send = opener or (lambda request: _send(request, 30))
    for index, key in enumerate(keys):
        status, _ = send(urllib.request.Request("https://integrate.api.nvidia.com/v1/models", headers={"Authorization": f"Bearer {key}"}))
        if status in (401, 403):
            print(f"key {index + 1} of {len(keys)}: rejected (HTTP {status}); trying the next one")
            continue
        print(f"key {index + 1} of {len(keys)}: " + ("accepted (HTTP 200)" if status == 200 else f"HTTP {status}" + (" (rate limit: stopping)" if status == 429 else "")))
        return 0 if status == 200 else 1
    print("every key was rejected")
    return 1


def build(model_name: str, scene: int, seed: int):
    model = MODELS[model_name]
    refs = [REFS / name for name in SCENES[scene]["refs"]][: model["max_refs"]]
    missing = [p.name for p in refs if not p.is_file()]
    if missing:
        raise SystemExit(f"reference images missing in {REFS}: {missing}")
    prompt = scene_prompt(scene)
    return model, refs, prompt, model["builder"](prompt, refs, seed, model["size"])


def cmd_probe(args, post=http_post) -> int:
    keys = keys_from_env()
    if not keys:
        print("no key: set NVIDIA_API_KEY (or NVIDIA_API_KEYS) first")
        return 2
    model, refs, prompt, body = build(args.model, 1, args.seed)
    status, response, _ = call(model, body, keys, post)
    shown = json.dumps(response)[:600] if isinstance(response, dict) else str(response)[:600]
    print(f"HTTP {status}\n{scrub(shown, keys)}\nrequest fields sent: {sorted(body)}")
    return 0 if status == 200 else 1


def cmd_run(args, post=http_post) -> int:
    keys = keys_from_env()
    if not keys and not args.dry_run:
        print("no key: set NVIDIA_API_KEY (or NVIDIA_API_KEYS) first")
        return 2
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    receipt = {"schema_version": 1, "model": args.model, "endpoint": MODELS[args.model]["url"], "schema_confidence": "unverified request field names",
               "note": "PROTOTYPE via the NVIDIA API catalog (personal use, D-012); human review NOT_DONE", "scenes": []}
    exit_code = 0
    for scene in [int(s) for s in args.scenes.split(",")]:
        model, refs, prompt, body = build(args.model, scene, args.seed + scene)
        item = {"scene": scene, "seed": args.seed + scene, "prompt": prompt, "references": [{"file": p.name, "sha256": sha256(p.read_bytes())} for p in refs],
                "request_fields": sorted(body)}
        if args.dry_run:
            item["status"] = "DRY_RUN"
        else:
            started = time.monotonic()
            status, response, key_index = call(model, body, keys, post)
            item.update(status=status, wall_s=round(time.monotonic() - started, 1), key_number_used=key_index + 1)
            image = extract_image(response) if isinstance(response, dict) else None
            if status == 200 and image and looks_like_an_image_without_a_secret(image, keys):
                target = out / f"scene{scene}_{args.model}.png"
                target.write_bytes(image)
                item.update(output=target.name, output_sha256=sha256(image), verdict="IMAGE_RETURNED")
            else:
                item.update(verdict="FAILED", detail=scrub((json.dumps(response) if isinstance(response, dict) else str(response))[:600], keys))
                exit_code = 1
                if status == 429:
                    receipt["scenes"].append(item)
                    print("HTTP 429: rate limit reached; stopping (no key rotation to get around it)")
                    break
        receipt["scenes"].append(item)
        print(f"scene {scene}: {item.get('verdict', item['status'])}")
    text = scrub(json.dumps(receipt, indent=2, ensure_ascii=False), keys)
    (out / "receipt.json").write_text(text, encoding="utf-8")
    return exit_code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check-key")
    for name in ("probe", "run"):
        one = sub.add_parser(name)
        one.add_argument("--model", choices=sorted(MODELS), required=True)
        one.add_argument("--seed", type=int, default=20261024)
        if name == "run":
            one.add_argument("--scenes", default="1,2,3")
            one.add_argument("--out", required=True)
            one.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    return {"check-key": cmd_check_key, "probe": cmd_probe, "run": cmd_run}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
