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

Confirmed a third time on 2026-10-23 by HTTP `HEAD` on the pinned `resolve/<revision>/<file>` URLs (no body downloaded): `X-Repo-Commit` equals the pinned revision, `X-Linked-Size` and `X-Linked-ETag` (the SHA-256) equal the table for both files.

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

## C. Conditions of this approval (as amended by the owner's "approve with edits" decision)

1. **Reviewed code only.** The GPU command pins the GranthStudio commit (`LTX_EXPECTED_COMMIT`); it must equal the commit that passed the narrow Codex
   review of Stage 2 and is contained in the refreshed Kaggle bundle (BUNDLE_INFO.json `branch_tip`). A different or dirty checkout is refused.
2. **The responsible human accepts the LTXV Open Weights License 0.X** (and has read the ComfyUI-LTXVideo LICENSE) before section E is signed; the script has no way to check this.
3. Everything that can be refused is refused before the first clone or download (approval, commit, clean tree, session deadline, ffmpeg, 40 GB disk, one Tesla T4, free port).
4. The workflow is a **candidate**: the 0.9.6-named checkpoint in the official example is substituted by the 0.9.8 file. This is a compatibility experiment (B1), not an
   official configuration; the model card lists no workflow for the 2B 0.9.8 distilled model. A decoded clip still does not validate the capability.
5. **Precision (T4):** expected fp32 diffusion model and fp32 VAE, fp16 text encoder with automatic offload (research section 5). Recorded in the receipt together with a
   ComfyUI log excerpt and an nvidia-smi VRAM trace. A hard out-of-memory is a FAIL, not a reason to change flags silently.
6. Step 6 of the script rebuilds the API workflow from the official file and the live `/object_info`; anything other than IDENTICAL aborts before inference.
7. FLF stays disabled; no batch or production rendering; only a synthetic test-pattern image and the synthetic project; no research approval; no Granth scenes.
8. **After the first decoded clip** (a separate, later step, not in this script): one controlled output-rejection test must show the real sampler executing again with a
   changed effective seed, plus recovery evidence.
9. Estimated GPU time: unknown (B13); weights and fp32 sampling both take real time. Plan one full session and expect to rerun.

## D. Exact way to run the first Kaggle T4 compatibility test

Notebook `notebooks/kaggle_ltx_first_test.ipynb` (import it as a new Kaggle notebook): accelerator **GPU T4 x1**, Internet **On**, dataset
`sangeetasangamkar/granthstudio-cpu-baseline` attached (private; the version whose `BUNDLE_INFO.json` `branch_tip` equals the reviewed commit). In its first cell the responsible human types
`APPROVER` (the real name that accepted the licence and signed section E) and `EXPECTED_COMMIT` (the reviewed commit, full sha, from `BUNDLE_INFO.json`); the notebook stops at that cell until both are
filled, then clones the bundle, refuses any other commit or a dirty tree, and runs `scripts/kaggle/ltx_first_test.sh` with those values. Equivalent shell form:

```bash
cd /kaggle/working && git clone -q -b sprint/remaining-pipeline /kaggle/input/granthstudio-cpu-baseline/granthstudio.bundle granthstudio
cd granthstudio && pip install -q pyyaml jsonschema pytest
LTX_DOWNLOAD_APPROVED="<approver name>" LTX_EXPECTED_COMMIT="<reviewed sha>" SESSION_MINUTES=240 bash scripts/kaggle/ltx_first_test.sh
```

`SESSION_MINUTES` is a maximum, not a target. The reviewed commit to type is **`2a5865b96045612d7893e7d0f1929926668b38be`** (the bundle now in the dataset). The first test allows **one attempt**: on a CUDA out-of-memory error (or any failure) it stops and records the evidence; it never retries automatically or tries
another configuration. This is one attempt per INVOCATION: a human who reruns in the same workdir after a failure can spend another generation from the journal's durable budget of 3, so decide deliberately before rerunning. Evidence: `/kaggle/working/ltx_first_test_evidence.tgz` (receipt, pin report, live node inventory, rebuilt workflow, converter report, ComfyUI log and launch arguments, pip freeze,
nvidia-smi before/after, VRAM trace, the journal, the clip). Verdicts: `PASS` (one clip decoded through the pipeline, capability still unvalidated), `FAIL` (task failed, out of memory, or wrong dimensions),
`NOT_VALIDATED` (pipeline refused, e.g. unready host), `NOT_RUN` (a precondition failed before any request).

## E. Approval — to be completed by the responsible human (an assistant cannot sign or accept a licence)

| Decision | Name | Date |
|---|---|---|
| I accepted the LTXV Open Weights License 0.X (commercial use below US$10 M annual revenue; AI-generated content disclosed when published; use restrictions) and read the ComfyUI-LTXVideo LICENSE | Satvik Sangamkar | 2026-10-23 |
| Approve downloads A and B as listed, and one controlled Kaggle GPU T4 x2 testing session (stages gpu0, gpu1, concurrent, retry) to run section D | Satvik Sangamkar | 2026-10-23 |

Owner decision recorded 2026-10-23 (chat): *approve with edits* - approved in principle: the two weights, one Kaggle T4, a 240-minute maximum, one synthetic I2V clip, and (after a first successful clip) a controlled
cache/retry test. Not approved: full Adhyay scenes, marking LTX production-validated. The signature rows above stay blank until the named person fills them; `LTX_DOWNLOAD_APPROVED`/`APPROVER` must carry that same name.

Approval recorded 2026-10-23 from the owner's own chat statement: "I, Satvik Sangamkar, have read and accepted the LTXV Open Weights License 0.X. I authorize the two approved model downloads and one controlled
Kaggle T4 x2 testing session." Recorded by the assistant at the owner's explicit instruction; the acceptance is the owner's, not the assistant's. `LTX_DOWNLOAD_APPROVED` / `APPROVER` = `Satvik Sangamkar`.
Order set by the owner: CPU tests, commit, focused Codex review, and only then GPU execution. Scope unchanged: synthetic clips only, no full Adhyay, LTX not marked validated from clips.
