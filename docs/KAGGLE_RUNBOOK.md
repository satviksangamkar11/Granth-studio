# Kaggle execution runbook (preparation phase)

Nothing in this runbook has been executed on Kaggle yet. **Do not record a Linux PASS anywhere until the notebook has run on
Kaggle and its own `receipt.json` says so.** No GPU, no model download and no Granth content are involved in Stage 1.

## Account

Use the Kaggle account **`sangeetasangamkar`** (owner decision, 2026-10-22). It is the Kaggle CLI default on this PC, so plain
`kaggle …` commands act on it. Do **not** set a `KAGGLE_API_TOKEN` override for this project (that selects the other account,
`satviksangamkar54321`). Token files are never read, printed or committed by this project; only their file names are known
(`C:\Users\Satvik\.kaggle\`). That the default token belongs to `sangeetasangamkar` is an inference from another session's
report, so before the first upload confirm the account with `kaggle datasets list --mine` (it prints dataset names, not the
token). The remaining weekly quota of this account is unknown; Stage 1 needs no GPU quota. The choice is also saved in the
assistant's project memory (`kaggle-account-granthstudio`).

## Stage 0 — package the accepted baseline (on this PC)

The repository has no git remote, so the code travels as a **git bundle** in a private Kaggle dataset.

```powershell
cd "D:\aai work\granthstudio"
git status --short                     # must print nothing
python scripts/kaggle/make_bundle.py --out D:\kaggle_upload\granthstudio-bundle
```

This writes `granthstudio.bundle`, `BUNDLE_INFO.json` (branch tip, bundle SHA-256) and `dataset-metadata.json`
(`sangeetasangamkar/granthstudio-cpu-baseline`). It refuses to run on a dirty tree or if the accepted baseline
`f8d5d02f609a68806e8272617d1e04c98cf6040c` is not an ancestor of the branch.

```powershell
kaggle datasets create -p D:\kaggle_upload\granthstudio-bundle      # private unless --public is given
```

Keep `BUNDLE_INFO.json`: it ties the uploaded bytes to a branch tip.

## Stage 1 — Linux CPU verification (notebook)

1. kaggle.com → New Notebook → File → Import Notebook → `notebooks/kaggle_linux_cpu_verify.ipynb`.
2. Add Data → *Your datasets* → `granthstudio-cpu-baseline`.
3. Session options: **Accelerator: None** (CPU). **Internet: On** only if the first run reports a missing test dependency
   (pyyaml, jsonschema, pytest); turn it off again afterwards.
4. Run All. The notebook: clones the bundle, copies the harness scripts, checks out the exact accepted commit
   (`f8d5d02…`, detached), runs the **complete** CPU suite, then runs `scripts/kaggle/posix_primitives_tests.py` (fcntl
   journal lock, `dir_fd` primitives, a real second process contending for the lock, symlink and dangling-symlink refusal).
5. Read the last cell. The verdict is computed by `scripts/kaggle/linux_cpu_verify.py`:

| Verdict | Meaning |
|---|---|
| `LINUX_CPU_PASS_ON_KAGGLE` | POSIX host that looks like Kaggle, zero failures/errors, **all 10 required POSIX tests passed (none skipped)**, supplementary tests passed |
| `LINUX_CPU_PASS_NON_KAGGLE_HOST` | same, but the host did not look like Kaggle — not a Kaggle result |
| `LINUX_CPU_FAIL` | any failure/error, or a required test skipped/not collected (e.g. no ffmpeg) |
| `INCOMPLETE_NOT_LINUX` | run on Windows/macOS — never a Linux PASS |
| `NOT_RUN_*` | wrong commit, dirty tree, changed architecture file, Python < 3.12, or dependencies unavailable |

6. Download the artifacts: `linux_cpu_evidence.zip` from the notebook's Output tab, or
   `kaggle kernels output sangeetasangamkar/<notebook-slug> -p D:\kaggle_upload\evidence`.
   Contents: `junit_full.xml`, `junit_supplementary.xml`, `full_log.txt`, `environment.json` (kernel, Python, ffmpeg, filesystem,
   memory, GPU visibility), `receipt.json` (source SHA, harness SHA, architecture SHA-256 vs the frozen value, per-artifact
   SHA-256, pip freeze, evaluation, skips with reasons).
7. Save the zip under `benchmarks/linux/` in the repository and hand the receipt to the independent reviewer. Record the
   verdict in `docs/PROGRESS.md` **as printed by the receipt**, with the notebook run's date and Kaggle version number.

If Python on the image is older than 3.12 the harness stops with `NOT_RUN_PYTHON_TOO_OLD`; it does not fall back to a
different interpreter silently. Resolving that (for example installing Python 3.12 with `uv`) is a decision to take after seeing
the receipt.

## Stage 2 — static pin verification on the GPU host (after Stage 1 and after approval; NOT part of this phase)

Only after `docs/LTX_098_DOWNLOAD_APPROVAL.md` section D is signed: fetch the pinned sources and the two weight files into a
GPU session, then, before starting ComfyUI inference:

```bash
python scripts/verify_ltx_pins.py \
  --source comfyui=/kaggle/working/ComfyUI --source ltxvideo_nodes=/kaggle/working/ComfyUI/custom_nodes/ComfyUI-LTXVideo \
  --source videohelpersuite=/kaggle/working/ComfyUI/custom_nodes/ComfyUI-VideoHelperSuite \
  --source kjnodes=/kaggle/working/ComfyUI/custom_nodes/ComfyUI-KJNodes \
  --models-dir /kaggle/working/ComfyUI --workflow /kaggle/working/ComfyUI/custom_nodes/ComfyUI-LTXVideo/example_workflows/low_level/ltxvideo-i2v-distilled.json \
  --node-inventory object_info.json --models-yaml config/models.yaml --json pin_report.json
```

`object_info.json` is the saved response of the running server's `/object_info`. Exit 0 requires every check PASS; exit 1 means
MISSING/MISMATCH; exit 2 means only UNVERIFIED items remain. A PASS is a static match, not evidence the model runs. The GPU
steps that follow (resource preflight, one I2V shot, recovery) are listed in the task brief and are **not** prepared or run here.

## What is not claimed

No Linux result, no GPU result, no LTX compatibility, no workflow validity. Blockers B1–B10 are listed in
`docs/LTX_098_RESEARCH.md`.
