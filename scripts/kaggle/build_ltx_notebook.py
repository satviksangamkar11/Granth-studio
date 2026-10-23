"""Generate notebooks/kaggle_ltx_first_test.ipynb: the notebook for the staged LTX 0.9.8 I2V compatibility tests on Kaggle GPU T4 x2.

The approver name and the expected commit are deliberately NOT baked in: the responsible human types them into the parameter cell
(that act is the licence acceptance / signature recorded in docs/LTX_098_DOWNLOAD_APPROVAL.md section E). Nothing runs until that cell is filled.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CELLS = [
    ("markdown", """# GranthStudio — LTX 0.9.8 I2V compatibility tests (two Tesla T4, one worker per card)

**Session settings:** Accelerator **GPU T4 x2**, Internet **On**, dataset `granthstudio-cpu-baseline` attached.
This downloads ~16.1 GB of weights (two pinned files, SHA-256 checked) and runs ONE synthetic image-to-video clip per stage through the existing GranthStudio pipeline.
It is a technical prerequisite, not the Phase 1 milestone. A decoded clip does **not** validate LTX. Not approved: batch rendering, Granth scenes, production.

Before running, the responsible human must have read and accepted the LTXV Open Weights License 0.X and signed section E of `docs/LTX_098_DOWNLOAD_APPROVAL.md`.
Fill the next cell with that person's real name and the reviewed commit; the script aborts on any mismatch, missing node, failed hash or insufficient resource,
and stops (no retry) on a CUDA out-of-memory error."""),
    ("code", """# --- parameters: filled by the responsible human --------------------------------------------------------------
APPROVER = ""            # the name that signed section E and accepted the licence (not a placeholder, not an assistant)
EXPECTED_COMMIT = ""     # the reviewed GranthStudio commit (BUNDLE_INFO.json branch_tip), 40 hex characters
PAINTED_INPUT = ""       # optional: repo folder of a painted start image + prompt (gpu0/retry only); empty = the synthetic test pattern
PAINTED_PROMPT = "prompt.txt"   # which prompt file of PAINTED_INPUT to use (a plain file name)
STAGE = "gpu0"           # gpu0 (always first) -> gpu1 -> concurrent -> retry; later stages need earlier PASS receipts
SESSION_MINUTES = 240    # a maximum, not a target
# ----------------------------------------------------------------------------------------------------------------
import re
assert APPROVER.strip(), "fill APPROVER with the authorised person's name (licence acceptance + manifest section E)"
assert re.fullmatch(r"[0-9a-f]{40}", EXPECTED_COMMIT), "EXPECTED_COMMIT must be the full 40-character commit sha"
assert STAGE in ("gpu0", "gpu1", "concurrent", "retry")
assert 30 <= SESSION_MINUTES <= 720"""),
    ("code", """import glob, os, shutil, subprocess, sys
print(subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True).stdout or "NO GPU VISIBLE: stop here")
bundles = glob.glob("/kaggle/input/**/granthstudio.bundle", recursive=True)
assert bundles, "attach the granthstudio-cpu-baseline dataset"
WORK = "/kaggle/working"                      # small: the repo checkout and the published evidence (20 GB limit)
TMP = "/kaggle/temp/ltx"                      # large scratch disk: ComfyUI, 16 GB of weights, projects
os.makedirs(TMP, exist_ok=True)
shutil.rmtree(f"{WORK}/granthstudio", ignore_errors=True)
subprocess.run(["git", "clone", "-q", "-b", "sprint/remaining-pipeline", bundles[0], f"{WORK}/granthstudio"], check=True)
head = subprocess.run(["git", "-C", f"{WORK}/granthstudio", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
print("bundle HEAD:", head)
assert head == EXPECTED_COMMIT, f"the attached bundle is at {head}, not the reviewed {EXPECTED_COMMIT}: refusing"
assert not subprocess.run(["git", "-C", f"{WORK}/granthstudio", "status", "--porcelain"], capture_output=True, text=True).stdout, "dirty checkout"
os.makedirs(f"{TMP}/cache/pip", exist_ok=True)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pyyaml", "jsonschema", "pytest"], check=True, env={**os.environ, "PIP_CACHE_DIR": f"{TMP}/cache/pip"})"""),
    ("code", """env = {**os.environ, "LTX_DOWNLOAD_APPROVED": APPROVER.strip(), "LTX_EXPECTED_COMMIT": EXPECTED_COMMIT, "SESSION_MINUTES": str(SESSION_MINUTES), "STAGE": STAGE, "PAINTED_INPUT": PAINTED_INPUT, "PAINTED_PROMPT": PAINTED_PROMPT, "W": TMP, "EVIDENCE_DEST": WORK}
process = subprocess.Popen(["bash", f"{WORK}/granthstudio/scripts/kaggle/ltx_first_test.sh"], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
for line in process.stdout:
    print(line, end="")
exit_code = process.wait()
print("script exit status:", exit_code)"""),
    ("code", """import json
receipts = {"gpu0": "ltx_gpu0/test_receipt.json", "gpu1": "ltx_gpu1/test_receipt.json", "retry": "ltx_gpu0/retry_receipt.json"}
for label in ([STAGE] if STAGE != "concurrent" else ["conc0", "conc1"]):
    path = f"{TMP}/" + receipts.get(label, f"ltx_{label}/test_receipt.json")
    if os.path.exists(path):
        r = json.load(open(path))
        print(label, "VERDICT:", r["verdict"], "-", r["reason"])
        print("  gpu_index:", r.get("gpu_index"), "clip:", r.get("clip"), "wall_s:", r.get("wall_s"), "oom:", r.get("out_of_memory"))
        print("  peak VRAM / generation:", (r.get("metrics") or {}).get("peak_vram_mb"), (r.get("metrics") or {}).get("generation"))
    else:
        print(label, "no receipt: the script stopped before the test (see the output above)")
evidence = f"{WORK}/ltx_evidence_{STAGE}.tgz"      # published copy
print("evidence bundle:", evidence, os.path.exists(evidence))"""),
]


def cell(kind: str, source: str) -> dict:
    base = {"cell_type": kind, "metadata": {}, "source": source.splitlines(keepends=True)}
    return {**base, "outputs": [], "execution_count": None} if kind == "code" else base


def main() -> None:
    notebook = {"cells": [cell(k, s) for k, s in CELLS], "nbformat": 4, "nbformat_minor": 5,
                "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python"}}}
    target = ROOT / "notebooks" / "kaggle_ltx_first_test.ipynb"
    target.write_text(json.dumps(notebook, indent=1), encoding="utf-8")
    print(target)


if __name__ == "__main__":
    main()
