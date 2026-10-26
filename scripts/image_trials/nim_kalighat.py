"""Free NVIDIA hosted image models, text-only (the hosted endpoints reject reference images), Kalighat folk style. Keys from the secrets folder via nvidia_trial.load_keys (never printed).
Usage: python nim_kalighat.py pick --out DIR   (one Maharaj image per model)   |   run --model NAME --out DIR   (Maharaj, Bankatlal, Devidas)"""
import argparse, base64, importlib.util, io, json, sys, time, urllib.request, urllib.error
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
spec = importlib.util.spec_from_file_location("nt", Path(__file__).with_name("nvidia_trial.py")); nt = importlib.util.module_from_spec(spec); spec.loader.exec_module(nt)
KEYS = nt.load_keys()
G = "https://ai.api.nvidia.com/v1/genai/black-forest-labs/"
MODELS = {"flux1-dev": (G + "flux.1-dev", {"steps": 40, "cfg_scale": 3.5, "width": 1024, "height": 1024}),
          "flux2-klein": (G + "flux.2-klein-4b", {"steps": 4, "width": 1024, "height": 1024}),
          "flux3-klein": (G + "flux-3-image-klein", {})}
STYLE = ("Kalighat folk painting in the Bengal Pattachitra tradition, confident flowing brush contours, flat bold colour fills with a soft wash for rounded volume, minimal shading, "
         "simplified large almond eyes and stylised features, sparse composition with the figure large and a plain textured paper ground, no text")
SUBJECTS = {"maharaj": "a young man seated cross-legged, calm lowered eyes, wearing a plain white cloth, short dark hair, hands resting on his knees, full body",
            "bankatlal": "a young merchant standing with folded hands, humble expression, neat moustache, terracotta-red turban, cream knee-length coat, white dhoti with a thin red border, full body",
            "devidas": "a devout householder standing calm and dignified, greying temples, small round forehead mark, sacred thread across the chest, white dhoti and white shoulder cloth, full body"}

SCENES = {1: "A young man in plain white cloth sits cross-legged on a dusty village road in front of a small house, among scattered leaf plates, lifting a few grains of rice to his mouth, calm face, bright daylight",
          2: "A young man in plain white cloth sits cross-legged on a village road eating rice, while a merchant in a terracotta-red turban and a clerk in a white cap stand a few steps away watching in amazement, a small house behind, bright daylight",
          3: "At the doorway of a house a householder in a white dhoti with a sacred thread sets a large plate of sweets on the ground before a young man in plain white cloth sitting cross-legged and eating calmly, a merchant in a red turban and a clerk in a white cap stand nearby watching with respect, bright daylight"}
WIDE = {"flux1-dev": {"width": 1344, "height": 768}, "flux2-klein": {"width": 1344, "height": 768}, "flux3-klein": {"width": 1344, "height": 768}}   # the endpoints only accept listed sizes; 1344x768 is the widest

def gen(model, subject, key, seed=7, wide=False):
    url, extra = MODELS[model]
    extra = {**extra, **WIDE[model]} if wide else extra
    body = {"prompt": f"{STYLE}. {subject}.", "seed": seed, **extra}
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    try:
        a = json.loads(urllib.request.urlopen(req, timeout=300).read())["artifacts"][0]
        return a.get("finishReason"), (base64.b64decode(a["base64"]) if a.get("base64") else None)
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code}", None
    except Exception as e:
        return type(e).__name__, None

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["pick", "run", "scenes"]); ap.add_argument("--out", required=True); ap.add_argument("--model")
    a = ap.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    if a.cmd == "pick":
        jobs = [(m, "maharaj") for m in MODELS]
    elif a.cmd == "scenes":
        jobs = [(m, f"scene{n}") for m in MODELS for n in SCENES]
    else:
        jobs = [(a.model, c) for c in SUBJECTS]
    for i, (m, c) in enumerate(jobs):
        t = time.time(); fr, img = gen(m, SCENES[int(c[5:])] if c.startswith("scene") else SUBJECTS[c], KEYS[i % len(KEYS)], wide=c.startswith("scene"))
        print(m, c, fr, round(time.time() - t, 1), flush=True)
        if img: (out / f"{m}__{c}.jpg").write_bytes(img)
main()
