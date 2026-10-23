"""Generate notebooks/kaggle_sdxl_first_test.ipynb: the notebook for the PROVISIONAL pilot's first SDXL + IP-Adapter keyframe test (one T4 of a "GPU T4 x2" session).

The approver name and the expected commit are NOT baked in: the owner types them into the parameter cell. Nothing runs until that cell is filled.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CELLS = [
    ("markdown", """# GranthStudio — SDXL + IP-Adapter keyframe test for the provisional 45-second pilot (ONE Tesla T4)

**Session settings:** Accelerator **GPU T4 x2**, Internet **On**, dataset `granthstudio-cpu-baseline` attached.
This downloads about 10.7 GB of pinned weights (SHA-256 checked, any mismatch aborts) onto scratch storage and generates ONE keyframe for the chosen scene through the existing GranthStudio pipeline,
plus a no-reference control image. It is a PROVISIONAL TECHNICAL TEST: the painting used as identity/style reference is an external Gemini image and never counts as SDXL validation, and a decoded
PNG does not validate SDXL: a human judges style fidelity and identity. Authorization record: `docs/pilot/SDXL_DOWNLOAD_APPROVAL.md` (the owner's instruction; licences were not individually reviewed by the assistant)."""),
    ("code", """# --- parameters: filled by the owner ----------------------------------------------------------------------------
APPROVER = ""            # the owner's name, as in docs/pilot/SDXL_DOWNLOAD_APPROVAL.md (not a placeholder, not an assistant)
EXPECTED_COMMIT = ""     # the reviewed GranthStudio commit (BUNDLE_INFO.json branch_tip), 40 hex characters
VISUAL = "vis_s1_kf"     # vis_s1_kf first; vis_s2_kf and vis_s3_kf only after the first keyframe has been reviewed
SESSION_MINUTES = 240    # a maximum, not a target
STYLE_SWEEP = False      # True: EXPERIMENT, reference-free style sweep of the chosen scene
SWEEP_SEEDS = 4          # seed offsets 0..N-1 (1-6)
SWEEP_CFGS = "6.5,9.0"   # KSampler cfg values (1-4)
REFERENCE_SET = ""       # e.g. "assets/pilot_refs/set_v1": owner-supplied references (manifest.json with sha256), replaces the single painting
STYLE_ANCHOR = False     # True: one style-only anchor reference (the location plate) instead of identity references; the scene text decides who appears
FP16_VAE = False         # True: decode in fp16 with the pinned fp16-fix VAE (needed next to 5 references on a T4)
LOW_VRAM = False         # True for vis_s2_kf and vis_s3_kf (4-5 IP-Adapter references): ComfyUI --lowvram
# ----------------------------------------------------------------------------------------------------------------
import re
assert APPROVER.strip(), "fill APPROVER with the owner's name"
assert re.fullmatch(r"[0-9a-f]{40}", EXPECTED_COMMIT), "EXPECTED_COMMIT must be the full 40-character commit sha"
assert VISUAL in ("vis_s1_kf", "vis_s2_kf", "vis_s3_kf")
assert 30 <= SESSION_MINUTES <= 720
assert isinstance(LOW_VRAM, bool) and isinstance(FP16_VAE, bool) and isinstance(STYLE_ANCHOR, bool) and isinstance(STYLE_SWEEP, bool) and 1 <= SWEEP_SEEDS <= 6"""),
    ("code", """import glob, os, shutil, subprocess, sys
print(subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True).stdout or "NO GPU VISIBLE: stop here")
gpus = subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True).stdout
assert gpus.count("Tesla T4") == 2, f"expected exactly two Tesla T4, saw: {gpus!r}"
idle = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"], capture_output=True, text=True).stdout.split()
assert len(idle) == 2 and all(float(v) < 800 for v in idle), f"both GPUs must be idle, memory used: {idle}"
ram_mb = next(int(line.split()[1]) / 1024 for line in open("/proc/meminfo") if line.startswith("MemAvailable:"))
assert ram_mb >= 24000, f"only {ram_mb:.0f} MiB RAM available, need 24000"
assert shutil.which("ffmpeg"), "ffmpeg is required"
os.makedirs("/kaggle/temp/sdxl", exist_ok=True)
assert shutil.disk_usage("/kaggle/temp/sdxl").free > 40e9, "less than 40 GB free on the scratch disk"
bundles = glob.glob("/kaggle/input/**/granthstudio.bundle", recursive=True)
assert bundles, "attach the granthstudio-cpu-baseline dataset"
WORK = "/kaggle/working"                      # small: the repo checkout and the published evidence (20 GB limit)
TMP = "/kaggle/temp/sdxl"                     # large scratch disk: ComfyUI, ~10.7 GB of weights, projects
os.makedirs(TMP, exist_ok=True)
shutil.rmtree(f"{WORK}/granthstudio", ignore_errors=True)
subprocess.run(["git", "clone", "-q", "-b", "sprint/remaining-pipeline", bundles[0], f"{WORK}/granthstudio"], check=True)
head = subprocess.run(["git", "-C", f"{WORK}/granthstudio", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
print("bundle HEAD:", head)
assert head == EXPECTED_COMMIT, f"the attached bundle is at {head}, not the reviewed {EXPECTED_COMMIT}: refusing"
assert not subprocess.run(["git", "-C", f"{WORK}/granthstudio", "status", "--porcelain"], capture_output=True, text=True).stdout, "dirty checkout"
os.makedirs(f"{TMP}/cache/pip", exist_ok=True)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pyyaml", "jsonschema", "pytest"], check=True, env={**os.environ, "PIP_CACHE_DIR": f"{TMP}/cache/pip"})"""),
    ("code", """env = {**os.environ, "LTX_DOWNLOAD_APPROVED": APPROVER.strip(), "LTX_EXPECTED_COMMIT": EXPECTED_COMMIT, "SESSION_MINUTES": str(SESSION_MINUTES), "VISUAL": VISUAL, "COMFY_LOWVRAM": "1" if LOW_VRAM else "0", "COMFY_FP16_VAE": "1" if FP16_VAE else "0", "STYLE_ANCHOR": "1" if STYLE_ANCHOR else "0", "STYLE_SWEEP": "1" if STYLE_SWEEP else "0", "REFERENCE_SET": REFERENCE_SET, "SWEEP_SEEDS": str(SWEEP_SEEDS), "SWEEP_CFGS": SWEEP_CFGS, "W": TMP, "EVIDENCE_DEST": WORK}
process = subprocess.Popen(["bash", f"{WORK}/granthstudio/scripts/kaggle/sdxl_first_test.sh"], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
for line in process.stdout:
    print(line, end="")
exit_code = process.wait()
print("script exit status:", exit_code)"""),
    ("code", """import json
receipt = f"{TMP}/sdxl_work_{VISUAL}/sdxl_receipt.json"
if os.path.exists(receipt):
    r = json.load(open(receipt))
    print("VERDICT:", r["verdict"], "-", r["reason"])
    print("live check:", r.get("live_check")); print("wall_s:", r.get("wall_s"), "oom:", r.get("out_of_memory"))
    for label, item in (r.get("results") or {}).items():
        print(" ", label, item.get("image"), item.get("sha256"), item.get("decoded"), item.get("wall_s"))
    print("reference influence:", r.get("reference_influence"))
else:
    print("no receipt: the script stopped before the test (see the output above)")
evidence = f"{WORK}/sdxl_{VISUAL}_evidence.tgz"      # published copy
print("evidence bundle:", evidence, os.path.exists(evidence))"""),
]


def cell(kind: str, source: str) -> dict:
    base = {"cell_type": kind, "metadata": {}, "source": source.splitlines(keepends=True)}
    return {**base, "outputs": [], "execution_count": None} if kind == "code" else base


def main() -> None:
    notebook = {"cells": [cell(k, s) for k, s in CELLS], "nbformat": 4, "nbformat_minor": 5,
                "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python"}}}
    target = ROOT / "notebooks" / "kaggle_sdxl_first_test.ipynb"
    target.write_text(json.dumps(notebook, indent=1), encoding="utf-8")
    print(target)


if __name__ == "__main__":
    main()
