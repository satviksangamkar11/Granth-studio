"""Generate notebooks/kaggle_linux_cpu_verify.ipynb (so the notebook source is reviewable as plain code)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CELLS = [
    ("markdown", """# GranthStudio v3.1 — Linux CPU verification (no GPU)

Runs the accepted CPU baseline on Linux and writes an evidence bundle. **Session settings:** accelerator **None** (CPU),
Internet **On** only if pip must install a missing test dependency. The dataset `granthstudio-cpu-baseline` (git bundle,
see docs/KAGGLE_RUNBOOK.md) must be attached. Nothing here downloads a model or uses a GPU. The verdict printed at the
end is computed from what actually ran; do not copy a PASS from anywhere else."""),
    ("code", """import glob, json, os, platform, shutil, subprocess, sys
BASELINE = "f8d5d02f609a68806e8272617d1e04c98cf6040c"   # accepted CPU baseline (Codex-reviewed)
bundles = glob.glob("/kaggle/input/**/granthstudio.bundle", recursive=True)
assert bundles, "attach the granthstudio-cpu-baseline dataset (granthstudio.bundle) to this notebook"
BUNDLE = bundles[0]
print("python", sys.version.split()[0], "| platform", platform.platform(), "| bundle", BUNDLE)
print(subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True).stdout if shutil.which("nvidia-smi") else "no nvidia-smi: CPU session (expected)")"""),
    ("code", """WORK = "/kaggle/working"
def run(*cmd, cwd=None):
    done = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    print("$", " ".join(cmd), "->", done.returncode); print((done.stdout + done.stderr).strip()[-1500:])
    assert done.returncode == 0
    return done.stdout.strip()
for stale in ("harness_repo", "harness", "granthstudio", "linux_cpu_evidence"):   # safe to Run All repeatedly
    shutil.rmtree(f"{WORK}/{stale}", ignore_errors=True)
os.path.exists(f"{WORK}/linux_cpu_evidence.zip") and os.remove(f"{WORK}/linux_cpu_evidence.zip")
run("git", "clone", "-q", "-b", "sprint/remaining-pipeline", BUNDLE, f"{WORK}/harness_repo")                 # branch tip: contains the harness scripts
HARNESS_SHA = run("git", "rev-parse", "HEAD", cwd=f"{WORK}/harness_repo")
shutil.copytree(f"{WORK}/harness_repo/scripts/kaggle", f"{WORK}/harness")   # copy before the code under test is checked out
run("git", "clone", "-q", "-b", "sprint/remaining-pipeline", BUNDLE, f"{WORK}/granthstudio")
run("git", "checkout", "-q", "--detach", BASELINE, cwd=f"{WORK}/granthstudio")   # the exact accepted commit
print("code under test:", run("git", "rev-parse", "HEAD", cwd=f"{WORK}/granthstudio"), "| harness:", HARNESS_SHA)"""),
    ("code", """done = subprocess.run([sys.executable, f"{WORK}/harness/linux_cpu_verify.py", "--repo", f"{WORK}/granthstudio",
    "--harness-dir", f"{WORK}/harness", "--baseline", BASELINE, "--harness-sha", HARNESS_SHA, "--out", f"{WORK}/linux_cpu_evidence"],
    capture_output=True, text=True)
print(done.stdout[-3000:]); print(done.stderr[-2000:])"""),
    ("code", """receipt = json.load(open(f"{WORK}/linux_cpu_evidence/receipt.json"))
print("VERDICT:", receipt["verdict"], receipt.get("reason", ""))
ev = receipt.get("evaluation", {})
print("counts:", ev.get("counts")); print("problems:", ev.get("problems"))
print("skipped:"); [print("  ", s) for s in ev.get("skipped", [])]
print("required POSIX tests:"); [print("  ", v, k) for k, v in ev.get("required", {}).items()]
print("supplementary:", ev.get("supplementary"))
print("\\nDownload: /kaggle/working/linux_cpu_evidence.zip (or the folder). Keep this notebook version and its output with it.")"""),
]


def cell(kind: str, source: str) -> dict:
    base = {"cell_type": kind, "metadata": {}, "source": source.splitlines(keepends=True)}
    return {**base, "outputs": [], "execution_count": None} if kind == "code" else base


def main() -> None:
    notebook = {"cells": [cell(k, s) for k, s in CELLS], "nbformat": 4, "nbformat_minor": 5,
                "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                             "language_info": {"name": "python"}}}
    target = ROOT / "notebooks" / "kaggle_linux_cpu_verify.ipynb"
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(notebook, indent=1), encoding="utf-8")
    print(target)


if __name__ == "__main__":
    main()
