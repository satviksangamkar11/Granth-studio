"""Generate notebooks/kaggle_audio_translate_test.ipynb: IndicTrans2 Marathi -> Hindi on the pilot's narration lines (PROVISIONAL technical test, one GPU).

The Hugging Face token is read ONLY from the Kaggle Secret named HF_TOKEN at run time; it is never a parameter, never printed and never written to a file.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CELLS = [
    ("markdown", """# GranthStudio: IndicTrans2 Marathi -> Hindi test (provisional 45-second pilot)

**Before running:** Add-ons > Secrets: add `HF_TOKEN` (a NEW read-only Hugging Face token, access to `ai4bharat/indictrans2-indic-indic-1B` accepted) and tick it for this notebook. Accelerator GPU T4 x2, Internet On, dataset `granthstudio-pilot-bundle` attached.
The run translates the pilot's six narration lines at a pinned model revision and shows the model's Hindi next to the assistant's draft. It validates nothing: a human reviews the Hindi."""),
    ("code", """APPROVER = ""            # the owner's name
EXPECTED_COMMIT = ""     # reviewed GranthStudio commit, 40 hex characters
import re
assert APPROVER.strip(), "fill APPROVER"
assert re.fullmatch(r"[0-9a-f]{40}", EXPECTED_COMMIT), "EXPECTED_COMMIT must be the full 40-character commit sha\""""),
    ("code", """import glob, os, shutil, subprocess, sys
WORK, TMP = "/kaggle/working", "/kaggle/temp/audio"
os.makedirs(TMP, exist_ok=True)
assert shutil.disk_usage(TMP).free > 20e9, "less than 20 GB free on scratch"
bundles = glob.glob("/kaggle/input/**/granthstudio.bundle", recursive=True)
assert bundles, "attach the granthstudio-pilot-bundle dataset"
shutil.rmtree(f"{WORK}/granthstudio", ignore_errors=True)
subprocess.run(["git", "clone", "-q", "-b", "sprint/remaining-pipeline", bundles[0], f"{WORK}/granthstudio"], check=True)
head = subprocess.run(["git", "-C", f"{WORK}/granthstudio", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
assert head == EXPECTED_COMMIT, f"bundle is at {head}, not the reviewed {EXPECTED_COMMIT}: refusing"
assert not os.environ.get("HF_TOKEN"), "HF_TOKEN must not be in the environment while packages are installed"
SAFE = ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR", "SSL_CERT_FILE", "REQUESTS_CA_BUNDLE", "LD_LIBRARY_PATH", "CUDA_VISIBLE_DEVICES")
env = {k: v for k, v in os.environ.items() if k in SAFE or k.startswith(("NVIDIA", "CUDA"))}        # an explicit allowlist: no credential of any name reaches pip or the model run
env["PIP_CACHE_DIR"] = f"{TMP}/pip"
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pyyaml", "jsonschema", "pytest", "transformers", "sentencepiece", "sacremoses", "IndicTransToolkit"], check=True, env=env)"""),
    ("code", """try:
    from kaggle_secrets import UserSecretsClient
    HF_TOKEN = UserSecretsClient().get_secret("HF_TOKEN")
except Exception as exc:
    raise SystemExit(f"Secret HF_TOKEN is not available ({type(exc).__name__}). Add-ons > Secrets: add HF_TOKEN and tick it for this notebook, then run again.")
assert HF_TOKEN and len(HF_TOKEN.strip()) >= 8, "HF_TOKEN is empty"
os.environ["HF_TOKEN"] = HF_TOKEN.strip()
del HF_TOKEN
out = f"{WORK}/audio_translate_evidence"
shutil.rmtree(out, ignore_errors=True)
run_env = {**env, "HF_TOKEN": os.environ["HF_TOKEN"], "HF_HOME": f"{TMP}/hf", "PYTHONPATH": f"{WORK}/granthstudio/src"}
process = subprocess.Popen([sys.executable, f"{WORK}/granthstudio/scripts/audio_translate_test.py", "--execute", "--expected-commit", EXPECTED_COMMIT, "--workdir", f"{TMP}/work", "--out", out],
                           env=run_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
for line in process.stdout:
    print(line.replace(os.environ["HF_TOKEN"], "***"), end="")
print("exit status:", process.wait())"""),
    ("code", """import json
secret = os.environ["HF_TOKEN"].encode()
leaked = [p for p in glob.glob(f"{out}/**/*", recursive=True) + glob.glob(f"{TMP}/work/**/*", recursive=True) if os.path.isfile(p) and secret in open(p, "rb").read()]
if leaked:
    shutil.rmtree(out, ignore_errors=True); shutil.rmtree(f"{TMP}/work", ignore_errors=True)
    raise SystemExit("token found in the evidence: evidence deleted, nothing shown")
receipt = json.load(open(f"{out}/translate_receipt.json", encoding="utf-8"))
print("VERDICT:", receipt["verdict"], "-", receipt["reason"])
for row in receipt.get("lines", []):
    print(row["dialogue_id"]); print("  MR:", row["marathi"]); print("  MODEL HI:", row["candidate"]); print("  DRAFT HI:", row["assistant_hindi_draft"]); print("  checks:", row["problems"])
print("evidence:", out)"""),
]


def cell(kind: str, source: str) -> dict:
    base = {"cell_type": kind, "metadata": {}, "source": source.splitlines(keepends=True)}
    return {**base, "outputs": [], "execution_count": None} if kind == "code" else base


def main() -> None:
    notebook = {"cells": [cell(k, s) for k, s in CELLS], "nbformat": 4, "nbformat_minor": 5,
                "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python"}}}
    target = ROOT / "notebooks" / "kaggle_audio_translate_test.ipynb"
    target.write_text(json.dumps(notebook, indent=1), encoding="utf-8")
    print(target)


if __name__ == "__main__":
    main()
