"""Free route for the hybrid puppet test while the Gemini credit is depleted: FLUX 3 Image Klein on NVIDIA's free hosted endpoint, text only (no reference image). The parts sheet is ONE generation,
so the pieces share one character and one style. Usage: python hybrid_nim_parts.py --out DIR [--tries 3]"""
import argparse, base64, importlib.util, json, sys, urllib.request, urllib.error
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
spec = importlib.util.spec_from_file_location("nt", Path(__file__).with_name("nvidia_trial.py")); nt = importlib.util.module_from_spec(spec); spec.loader.exec_module(nt)
KEYS = nt.load_keys()
URL = "https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux-3-image-klein"
PROMPT = ("Flat Kalighat Bengal folk painting style asset sheet for a jointed paper puppet toy, on a pure white background: seven separate flat pieces laid out in two rows with wide white gaps between them, none touching. "
          "Row one: a calm young monk's head with neck and ears and short dark hair; a plain torso piece wearing a draped cloth with rounded shoulder ends; a long straight upper-arm piece; a forearm piece ending in an open raised hand with fingers together. "
          "Row two: a second long straight upper-arm piece; a second forearm piece with a relaxed hand; a piece of crossed legs and feet with a white waist cloth. "
          "Warm brown skin, bold flowing contour lines, flat colour fills, no text, no shadows, each piece appears exactly once.")
ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--tries", type=int, default=3); a = ap.parse_args()
out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
ok = False
for i in range(a.tries):
    body = {"prompt": PROMPT, "seed": 11 + i, "width": 1344, "height": 768}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"Authorization": "Bearer " + KEYS[i % len(KEYS)], "Content-Type": "application/json"})
    try:
        art = json.loads(urllib.request.urlopen(req, timeout=300).read())["artifacts"][0]
        print(i, art.get("finishReason"), flush=True)
        if art.get("base64"):
            (out / "nim_parts_sheet.jpg").write_bytes(base64.b64decode(art["base64"]))
            ok = True
            break                                    # one good sheet is enough: stop spending requests
    except urllib.error.HTTPError as e:
        print(i, "HTTP", e.code, flush=True)         # status only: no response body is printed
    except Exception as e:
        print(i, type(e).__name__, flush=True)
sys.exit(0 if ok else 1)
