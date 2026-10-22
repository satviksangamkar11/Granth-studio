"""Generate notebooks/kaggle_ltx_first_test.ipynb: the notebook for the first real LTX 0.9.8 I2V compatibility test on ONE Kaggle T4.

The approver name and the expected commit are deliberately NOT baked in: the responsible human types them into the parameter cell
(that act is the licence acceptance / signature recorded in docs/LTX_098_DOWNLOAD_APPROVAL.md section E). Nothing runs until that cell is filled.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CELLS = [
    ("markdown", """# GranthStudio — first LTX 0.9.8 I2V compatibility test (ONE Tesla T4)

**Session settings:** Accelerator **GPU T4 x1**, Internet **On**, dataset `granthstudio-cpu-baseline` attached.
This downloads ~16.1 GB of weights (two pinned files, SHA-256 checked) and runs ONE synthetic image-to-video clip through the existing GranthStudio pipeline.
It is a technical prerequisite, not the Phase 1 milestone. A decoded clip does **not** validate LTX. Not approved: batch rendering, Granth scenes, production.

Before running, the responsible human must have read and accepted the LTXV Open Weights License 0.X and signed section E of `docs/LTX_098_DOWNLOAD_APPROVAL.md`.
Fill the next cell with that person's real name and the reviewed commit; the script aborts on any mismatch, missing node, failed hash or insufficient resource,
and stops (no retry) on a CUDA out-of-memory error."""),
    ("code", """# --- parameters: filled by the responsible human --------------------------------------------------------------
APPROVER = ""            # the name that signed section E and accepted the licence (not a placeholder, not an assistant)
EXPECTED_COMMIT = ""     # the reviewed GranthStudio commit (BUNDLE_INFO.json branch_tip), 40 hex characters
SESSION_MINUTES = 240    # a maximum, not a target
# ----------------------------------------------------------------------------------------------------------------
import re
assert APPROVER.strip(), "fill APPROVER with the authorised person's name (licence acceptance + manifest section E)"
assert re.fullmatch(r"[0-9a-f]{40}", EXPECTED_COMMIT), "EXPECTED_COMMIT must be the full 40-character commit sha"
assert 30 <= SESSION_MINUTES <= 720"""),
    ("code", """import glob, os, shutil, subprocess, sys
print(subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True).stdout or "NO GPU VISIBLE: stop here")
bundles = glob.glob("/kaggle/input/**/granthstudio.bundle", recursive=True)
assert bundles, "attach the granthstudio-cpu-baseline dataset"
WORK = "/kaggle/working"
shutil.rmtree(f"{WORK}/granthstudio", ignore_errors=True)
subprocess.run(["git", "clone", "-q", "-b", "sprint/remaining-pipeline", bundles[0], f"{WORK}/granthstudio"], check=True)
head = subprocess.run(["git", "-C", f"{WORK}/granthstudio", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
print("bundle HEAD:", head)
assert head == EXPECTED_COMMIT, f"the attached bundle is at {head}, not the reviewed {EXPECTED_COMMIT}: refusing"
assert not subprocess.run(["git", "-C", f"{WORK}/granthstudio", "status", "--porcelain"], capture_output=True, text=True).stdout, "dirty checkout"
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pyyaml", "jsonschema", "pytest"], check=True)"""),
    ("code", """env = {**os.environ, "LTX_DOWNLOAD_APPROVED": APPROVER.strip(), "LTX_EXPECTED_COMMIT": EXPECTED_COMMIT, "SESSION_MINUTES": str(SESSION_MINUTES), "W": WORK}
process = subprocess.Popen(["bash", f"{WORK}/granthstudio/scripts/kaggle/ltx_first_test.sh"], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
for line in process.stdout:
    print(line, end="")
exit_code = process.wait()
print("script exit status:", exit_code)"""),
    ("code", """import json
receipt = f"{WORK}/ltx_first_test/test_receipt.json"
if os.path.exists(receipt):
    r = json.load(open(receipt))
    print("VERDICT:", r["verdict"], "-", r["reason"])
    print("clip:", r.get("clip")); print("wall_s:", r.get("wall_s")); print("out_of_memory:", r.get("out_of_memory"))
    print("peak VRAM / generation:", (r.get("metrics") or {}).get("peak_vram_mb"), (r.get("metrics") or {}).get("generation"))
else:
    print("no receipt: the script stopped before the test (see the output above)")
print("evidence bundle:", f"{WORK}/ltx_first_test_evidence.tgz", os.path.exists(f"{WORK}/ltx_first_test_evidence.tgz"))"""),
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
