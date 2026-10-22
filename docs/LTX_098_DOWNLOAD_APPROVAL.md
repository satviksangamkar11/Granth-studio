# Model download approval manifest — LTX 0.9.8 first I2V test (final proposal, Stage 2)

**Status: NOT APPROVED. Nothing listed here has been downloaded or executed.** The GPU script refuses to start unless the
environment variable `LTX_DOWNLOAD_APPROVED` is set, so signing section D is the only thing that unlocks a download.
Hashes and sizes were read from Hugging Face (tree API and the raw git-LFS pointer file, which agree) and are re-checked
against the downloaded bytes with `sha256sum -c` by the script, then again by `scripts/verify_ltx_pins.py`.
Total download ≈ **16.1 GB** of weights plus four small git checkouts. No other model, LoRA, upscaler, VAE or FLF/keyframe file is fetched.

## A. Weights (the only large downloads)

| # | File | Repo @ revision | Size (bytes) | SHA-256 (published) | Destination | Licence |
|---|---|---|---|---|---|---|
| 1 | `ltxv-2b-0.9.8-distilled.safetensors` | `Lightricks/LTX-Video` @ `8984fa25007f376c1a299016d0957a37a2f797bb` | 6 340 744 492 (6.3 GB) | `76aa8c4786af752fa6f951947129d5290c3c6c0b2fadcadea6b5e114ae2cad8f` | `ComfyUI/models/checkpoints/` | **LTXV Open Weights License 0.X** (Lightricks): commercial use free below US$10 M annual revenue, otherwise a paid agreement; use restrictions pass to downstream users; disclose machine-generated content |
| 2 | `t5xxl_fp16.safetensors` | `comfyanonymous/flux_text_encoders` @ `6af2a98e3f615bdfa612fbd85da93d1ed5f69ef5` | 9 787 841 024 (9.8 GB) | `6e480b09fae049a72d2a8c5fbccb8d3e92febeb233bbe9dfe7256958a9167635` | `ComfyUI/models/text_encoders/` | Apache-2.0 (HF metadata) |

The VAE is **embedded in file 1** (the official workflow reads it from the checkpoint loader); there is no VAE download.

## B. Code (git, pinned by full commit, verified after checkout)

| Source | Commit | Licence | What was read at this commit |
|---|---|---|---|
| ComfyUI `v0.3.47` | `2f74e17975696d829af455845c584574bbc85774` | GPL-3.0 | LTX nodes, sampler nodes, `LoadImage`/`CLIPLoader`; contains the 2025-07-16 LTXV VAE-decoder padding fix |
| ComfyUI-LTXVideo | `36fdaf500b3cd6f7fa8b2dfec36e984746e630a2` | GitHub: no recognised licence (`NOASSERTION`) — read its LICENSE before use | README lists the 0.9.8 files; holds the official workflow (blob `2260170f…`, 18 595 bytes) |
| ComfyUI-VideoHelperSuite | `9e963ff5ed0b69e588ee3d965711766b0f3cf829` | GPL-3.0 | `VHS_VideoCombine` inputs and `h264-mp4` widgets |
| ComfyUI-KJNodes | `ad37ce656c13e9abea002b46e3a89be3dba32355` | GPL-3.0 | `StringToFloatList`, `FloatToSigmas` |

Python requirements of these four packs are **not version-pinned** by their sources; the script records `pip freeze` with the evidence.
GPL-3.0 components are used as separate processes/nodes on a rented notebook; no redistribution is planned (legal review is the owner's call).

## C. Conditions of this approval

1. Run only after `LINUX_CPU_PASS_ON_KAGGLE` is accepted (done for the baseline) and on **one Tesla T4** (the script checks).
2. The workflow is a **candidate**: the 0.9.6-named checkpoint in the official example is substituted by the 0.9.8 file. This is the
   one recorded, unverified assumption (B1); the run itself is its test. A decoded clip still does not validate the capability.
3. Step 6 of the script rebuilds the API workflow from the official file and the live `/object_info`; anything other than IDENTICAL
   to the committed candidate aborts before inference.
4. FLF stays disabled; no recovery/retry test in this run; only a synthetic test-pattern image and the synthetic project; no research approval.
5. Estimated GPU time: unknown (B13). Weights alone take a large share of a session; budget one full session and expect to rerun.

## D. Exact command for the first Kaggle T4 compatibility test

Kaggle notebook: accelerator **GPU T4 x1**, Internet **On**, dataset `granthstudio-cpu-baseline` attached (or any clone of this branch).

```bash
cd /kaggle/working && git clone -q -b sprint/remaining-pipeline /kaggle/input/granthstudio-cpu-baseline/granthstudio.bundle granthstudio
cd granthstudio && pip install -q pyyaml jsonschema pytest
LTX_DOWNLOAD_APPROVED="<approver name>" bash scripts/kaggle/ltx_first_test.sh
```

Evidence: `/kaggle/working/ltx_first_test_evidence.tgz` (receipt, pin report, live node inventory, rebuilt workflow, converter report, ComfyUI log,
pip freeze, nvidia-smi before/after, the clip). Verdicts: `PASS` (one clip decoded through the pipeline, capability still unvalidated),
`FAIL` (task failed or wrong dimensions), `NOT_VALIDATED` (pipeline refused, e.g. unready host), `NOT_RUN` (a precondition failed before any request).

## E. Approval

| Decision | Name | Date |
|---|---|---|
| Approve downloads A and B as listed, and a Kaggle T4 session to run section D (yes/no, with edits) | | |
