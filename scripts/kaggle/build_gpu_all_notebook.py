"""Generate the Kaggle GPU notebook that runs the whole reference-conditioned image benchmark (T4 x2) and builds one comparison sheet.

Lessons built in (from the failed runs): library races (HiDream's pinned libraries go into their own folder), memory (Qwen-Image-2.1 is stored in NF4; HiDream gets both
GPUs), gated access (probe a gated config file with the token and say clearly which account/permission is missing), invisible failures (every line is teed to a file in the
output folder because the Kaggle log page can stay empty; every step has a deadline; a summary is always written; the notebook ends with an error when nothing usable exists).

Usage: python scripts/kaggle/build_gpu_all_notebook.py OUTDIR
"""
import json
import os
import sys

CELL1 = '''import subprocess, sys, glob, os, json, time, shutil, threading, queue, signal, re
T0 = time.time()
def scrub(s):
    """Redact anything that looks like a Hugging Face token, and the exact value once it is loaded, from EVERY log line (page and files)."""
    s = re.sub(r"hf_[A-Za-z0-9]{10,}", "hf_***", s)
    v = os.environ.get("HF_TOKEN", "")
    return s.replace(v, "***") if len(v) > 8 else s
OUT = "/kaggle/working/all"; shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT, exist_ok=True)   # a rerun can never reuse an older run's files
LOGF = open(OUT + "/notebook.log", "a", encoding="utf-8")
def log(m):
    line = scrub("[%7.1fs] %s" % (time.time() - T0, m)); print(line[:400], flush=True); LOGF.write(line + chr(10)); LOGF.flush()   # page: shortened line, file: whole line
def sh(cmd, tag, timeout=1800, env=None, cwd=None, tee=None):
    """Run a command (list or shell string) in its own process group, stream every line to the page and to the log files, enforce the deadline on every pass, kill the whole group on timeout."""
    log("%s: START %s" % (tag, (cmd if isinstance(cmd, str) else " ".join(cmd))[:220]))
    q = queue.Queue(); p = None; rc = None; timed_out = False; tail = []
    side = open(tee, "a", encoding="utf-8") if tee else None
    try:
        p = subprocess.Popen(cmd, shell=isinstance(cmd, str), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1,
                             env={**os.environ, "PYTHONUNBUFFERED": "1", **(env or {})}, cwd=cwd, start_new_session=True)
        def pump():
            for l in p.stdout: q.put(l.rstrip())
            q.put(None)
        threading.Thread(target=pump, daemon=True).start()
        deadline = time.time() + timeout; eof = False
        while not eof:
            if time.time() > deadline: timed_out = True; log("%s: TIMEOUT after %ss, killing the process group" % (tag, timeout)); break
            try: l = q.get(timeout=2)
            except queue.Empty: continue
            if l is None: eof = True
            else:
                log("[%s] %s" % (tag, l)); tail = (tail + [l])[-12:]
                if side: side.write(scrub(l) + chr(10)); side.flush()
        if eof:
            try: rc = p.wait(timeout=max(1.0, deadline - time.time()))
            except subprocess.TimeoutExpired: timed_out = True; log("%s: TIMEOUT (output closed, process still running)" % tag)
    except Exception as e:
        log("%s: LAUNCH FAILURE %s: %s" % (tag, type(e).__name__, e)); tail = [str(e)]
    finally:
        if p is not None:
            try: os.killpg(p.pid, signal.SIGKILL)
            except Exception: pass
            try: rc = p.wait(timeout=30) if rc is None else rc
            except Exception: rc = None
        if side: side.close()
    if timed_out: rc = -9
    log("%s: END exit=%s%s" % (tag, rc, " (TIMED OUT)" if timed_out else "")); return rc, tail
log("STEP 0 accelerator check")
rc, tail = sh("nvidia-smi -L", "gpu", timeout=60)
if rc != 0 or "GPU" not in " ".join(tail): raise SystemExit("STOP: no NVIDIA GPU. In the editor choose Session options > Accelerator > GPU T4 (not a TPU), then Save and Run All (Commit).")
sh("df -h /kaggle/working /kaggle/temp /dev/shm; free -g", "disk", timeout=60)
os.makedirs("/kaggle/temp/hf", exist_ok=True); os.environ["HF_HOME"] = "/kaggle/temp/hf"
'''

CELL2 = '''log("STEP 1 install diffusers (git main) and text-model libraries; torch is pinned so it cannot change")
frozen = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True).stdout.splitlines()
pins = [l for l in frozen if l.split("==")[0].lower().replace("_", "-") in ("torch", "torchvision", "torchaudio")]
open(OUT + "/constraints.txt", "w").write(chr(10).join(pins) + chr(10)); log("pinned: %s" % pins)
rc, _ = sh([sys.executable, "-m", "pip", "install", "-q", "-c", OUT + "/constraints.txt", "git+https://github.com/huggingface/diffusers", "transformers>=5.17", "accelerate", "bitsandbytes", "sentencepiece", "protobuf", "huggingface_hub"], "pip", timeout=1200)
if rc != 0: raise SystemExit("STOP: package install failed")
vers = subprocess.run([sys.executable, "-c", "import torch, diffusers, transformers; print(torch.__version__, diffusers.__version__, transformers.__version__, torch.cuda.device_count())"], capture_output=True, text=True).stdout.strip()
log("versions (torch diffusers transformers gpus): " + vers)
log("STEP 2 Hugging Face token and access to the gated repos (FLUX 3 Image Klein, FLUX.1 Kontext)")
ACCESS = {"flux3": False, "kontext": False}
LABELS = ("HF_TOKEN", "HF_KEY", "HF-TOKEN", "hf_token", "HUGGINGFACE_TOKEN", "HUGGING_FACE_HUB_TOKEN", "HF")
try:
    from kaggle_secrets import UserSecretsClient
    client = UserSecretsClient(); found = None
    for label in LABELS:
        try:
            value = client.get_secret(label)
        except Exception as e:
            log("secret label %r: not available (%s: %s)" % (label, type(e).__name__, str(e)[:160])); continue
        if not value:
            log("secret label %r: attached but EMPTY" % label); continue
        if value:
            os.environ["HF_TOKEN"] = value; found = label; log("secret %r found and used as HF_TOKEN (value never printed; length %d)" % (label, len(value))); break
    if not found: raise RuntimeError("none of the labels %s is attached to THIS notebook session: in the editor open Add-ons > Secrets, add a secret labelled exactly HF_TOKEN, tick its checkbox for this notebook, then Save and Run All" % (LABELS,))
    from huggingface_hub import HfApi, hf_hub_download
    log("token belongs to Hugging Face user: %s" % HfApi().whoami().get("name"))
    for key, repo, f in (("flux3", "black-forest-labs/flux-3-image-klein", "config.json"), ("kontext", "black-forest-labs/FLUX.1-Kontext-dev", "model_index.json")):
        try:
            hf_hub_download(repo, f); ACCESS[key] = True; log("access OK (gated file downloaded): " + repo)
            if key == "flux3":
                txt = open(hf_hub_download(repo, "README.md"), encoding="utf-8").read(); i = txt.lower().find("diffusers"); log("FLUX 3 model-card usage follows:"); [log("  | " + l) for l in txt[max(0, i - 300):i + 3000].splitlines()]
        except Exception as e:
            log("NO ACCESS to %s: %s. Use a token from the account that was granted access (fine-grained tokens must allow reading public gated repos). Skipped." % (repo, type(e).__name__))
except Exception as e:
    log("HF token not available (%s: %s). FLUX 3 and Kontext are skipped." % (type(e).__name__, str(e)[:400]))
inp = os.path.dirname(glob.glob("/kaggle/input/**/open_edit_bench.py", recursive=True)[0]); log("inputs at %s: %s" % (inp, sorted(os.listdir(inp))))
'''

CELL3 = '''bench = lambda m: [sys.executable, "-u", inp + "/open_edit_bench.py", "--inputs", inp, "--out", OUT + "/" + m, "--models", m, "--seeds", "1"]
HID = r"""
import json, os, subprocess, sys, time
T0 = time.time()
def log(m): print("[%7.1fs] hidream: %s" % (time.time() - T0, m), flush=True)
def run(c, must=False, **kw):
    r = subprocess.run(c, **kw); log("exit %s: %s" % (r.returncode, " ".join(c)[:120]))
    if must and r.returncode != 0: raise SystemExit("HiDream setup step failed, stopping this stage")
    return r.returncode
OUT = "/kaggle/working/all/hidream"; os.makedirs(OUT, exist_ok=True); SITE = "/kaggle/temp/hid_site"
log("installing HiDream's pinned libraries into its OWN folder (the shared environment stays untouched)")
run([sys.executable, "-m", "pip", "install", "-q", "--target", SITE, "transformers==4.57.1", "tokenizers>=0.22,<=0.23.0", "huggingface-hub>=0.34,<1.0", "diffusers==0.39.0", "einops", "flask", "openai", "python-dotenv", "scipy"], must=True)
run(["git", "clone", "-q", "https://github.com/HiDream-ai/HiDream-O1-Image.git", OUT + "/repo"], must=True)
pp = OUT + "/repo/models/pipeline.py"; s = open(pp).read(); assert '"use_flash_attn": True' in s; open(pp, "w").write(s.replace('"use_flash_attn": True', '"use_flash_attn": False'))
ip = OUT + "/repo/inference.py"; s = open(ip).read(); assert 'device_map="cuda"' in s; open(ip, "w").write(s.replace('device_map="cuda"', 'device_map="cuda", quantization_config=__import__("transformers").BitsAndBytesConfig(load_in_8bit=True)'))
log("patched: flash-attn off, 8-bit weights on ONE GPU (a split over two GPUs failed with a cuda:0/cuda:1 tensor mismatch inside HiDream's own code)")
sys.path.insert(0, SITE)
from huggingface_hub import snapshot_download
log("downloading HiDream-O1-Image-Dev weights (about 16 GB)"); mp = snapshot_download("HiDream-ai/HiDream-O1-Image-Dev", local_dir="/kaggle/temp/hidream_dev"); log("weights ready")
inp = sys.argv[1]; spec = json.load(open(inp + "/prompts.json"))["scenes"]
env = {**os.environ, "PYTHONPATH": SITE + ":" + os.environ.get("PYTHONPATH", "")}
failures = 0
for s_, item in spec.items():
    log("scene %s: generating" % s_); t = time.time()
    rc = run([sys.executable, "-u", "inference.py", "--model_path", mp, "--model_type", "dev", "--shift", "1", "--prompt", item["prompt"], "--ref_images", *[inp + "/" + x for x in item["refs"]], "--output_image", "%s/hidream_s%s.png" % (OUT, s_), "--height", "768", "--width", "1024"], env=env, cwd=OUT + "/repo")
    log("scene %s: exit %s in %.0fs" % (s_, rc, time.time() - t)); failures += rc != 0
if failures: raise SystemExit("HiDream: %d of %d scenes failed" % (failures, len(spec)))
"""
os.makedirs(OUT + "/hidream", exist_ok=True); open(OUT + "/hid.py", "w").write(HID)
log("STEP 3 run in parallel: GPU0 = HiDream-O1-Image-Dev (8-bit); GPU1 = Qwen-Image-2.1 (NF4), then FLUX 3 Image Klein and FLUX.1 Kontext if the token has access")
def chain(tag, cmds, gpu):
    for c in cmds: sh(c, tag, timeout=3600, env={"CUDA_VISIBLE_DEVICES": str(gpu)}, tee=OUT + "/" + tag + ".log")
g1 = [bench("qwen21")] + ([bench("flux3")] if ACCESS["flux3"] else []) + ([bench("kontext")] if ACCESS["kontext"] else [])
ts = [threading.Thread(target=chain, args=("hidream", [[sys.executable, "-u", OUT + "/hid.py", inp]], 0)), threading.Thread(target=chain, args=("gpu1", g1, 1))]
[t.start() for t in ts]; [t.join() for t in ts]
'''

CELL4 = '''log("STEP 5 summary and comparison sheet")
from PIL import Image, ImageDraw
def blank(path):
    """True for a blank picture; None when the file cannot be decoded (for example truncated by a timeout)."""
    try:
        lo, hi = Image.open(path).convert("L").getextrema(); return hi - lo < 8
    except Exception as e:
        log("unreadable image %s: %s" % (path, type(e).__name__)); return None
usable = {}
for m in ("qwen21", "flux3", "kontext"):
    f = "%s/%s/receipt.json" % (OUT, m)
    if os.path.exists(f):
        e = json.load(open(f))["models"].get(m, {})
        log("%s: load=%ss error=%s results=%s" % (m, e.get("load_s"), e.get("error"), [((x.get("file") or x.get("error", "")[:90]) + (" BLANK" if x.get("blank") else "")) for x in e.get("results", [])]))
        usable[m] = {x["scene"]: "%s/%s" % (m, x["file"]) for x in e.get("results", []) if x.get("file") and not x.get("blank") and os.path.exists("%s/%s/%s" % (OUT, m, x["file"])) and blank("%s/%s/%s" % (OUT, m, x["file"])) is False}
    else: log("%s: no receipt (not run or crashed before writing)" % m)
usable["hidream"] = {}
for s in "123":
    fp = "%s/hidream/hidream_s%s.png" % (OUT, s)
    if os.path.exists(fp):
        b = blank(fp)
        if b is None: log("hidream scene %s: unreadable image, not used" % s)
        elif b: log("hidream scene %s: BLANK IMAGE, not used" % s)
        else: usable["hidream"][s] = "hidream/hidream_s%s.png" % s
log("hidream images: %s" % sorted(usable["hidream"].values()))
names = [m for m, v in usable.items() if v]
if names:
    W, H = 480, 360; sheet = Image.new("RGB", (W * len(names), (H + 16) * 3), "white"); d = ImageDraw.Draw(sheet)
    for c, m in enumerate(names):
        for r, s in enumerate("123"):
            d.text((c * W + 4, r * (H + 16) + 2), "%s scene %s" % (m, s), fill="black"); fn = usable[m].get(s)
            if fn: sheet.paste(Image.open(OUT + "/" + fn).convert("RGB").resize((W, H)), (c * W, r * (H + 16) + 16))
    sheet.save(OUT + "/compare.png"); log("saved " + OUT + "/compare.png")
shutil.rmtree(OUT + "/hidream/repo", ignore_errors=True)
log("DONE")
if not names: raise SystemExit("no usable image from any model: see " + OUT + "/notebook.log and the per-model logs")
'''


def main(outdir):
    cells = [CELL1, CELL2, CELL3, CELL4]
    for i, c in enumerate(cells):
        compile(c, "cell%d" % i, "exec")
    os.makedirs(outdir, exist_ok=True)
    slug = "granthstudio-bench-gpu-all"
    nb = {"cells": [{"cell_type": "code", "metadata": {}, "source": c.splitlines(True), "outputs": [], "execution_count": None} for c in cells],
          "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}, "nbformat": 4, "nbformat_minor": 5}
    json.dump(nb, open(os.path.join(outdir, slug + ".ipynb"), "w"))
    meta = {"id": "satviksangamkar54321/" + slug, "title": slug, "code_file": slug + ".ipynb", "language": "python", "kernel_type": "notebook", "is_private": True,
            "enable_gpu": True, "enable_tpu": False, "enable_internet": True, "machine_shape": "NvidiaTeslaT4",
            "dataset_sources": ["satviksangamkar54321/granthstudio-bench-inputs"], "competition_sources": [], "kernel_sources": [], "model_sources": []}
    json.dump(meta, open(os.path.join(outdir, "kernel-metadata.json"), "w"))
    print("written", outdir)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "kernel_gpu_all")
