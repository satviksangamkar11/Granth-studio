# Model download approval manifest — LTX 0.9.8 first I2V test

**Status: NOT APPROVED. Nothing listed here has been downloaded.** Approve by writing your name and date in the last
section. Hashes and sizes below were read from Hugging Face (tree API and the raw git-LFS pointer file, which agree); they
must be re-computed from the downloaded bytes with `scripts/verify_ltx_pins.py` before anything is treated as verified.
Total download ≈ **16.1 GB** (weights) plus three or four small git checkouts.

## A. Weights (the only large downloads)

| # | File | Repo @ revision | Size (bytes) | SHA-256 (published) | Goes to | Licence |
|---|---|---|---|---|---|---|
| 1 | `ltxv-2b-0.9.8-distilled.safetensors` | `Lightricks/LTX-Video` @ `8984fa25007f376c1a299016d0957a37a2f797bb` | 6 340 744 492 (6.3 GB) | `76aa8c4786af752fa6f951947129d5290c3c6c0b2fadcadea6b5e114ae2cad8f` | `models/checkpoints/` | LTXV Open Weights License 0.X (≥ US$10 M revenue needs a commercial agreement; see research §6) |
| 2 | `t5xxl_fp16.safetensors` | `comfyanonymous/flux_text_encoders` @ `6af2a98e3f615bdfa612fbd85da93d1ed5f69ef5` | 9 787 841 024 (9.8 GB) | `6e480b09fae049a72d2a8c5fbccb8d3e92febeb233bbe9dfe7256958a9167635` | `models/text_encoders/` | Apache-2.0 (HF metadata) |

No separate VAE download: the VAE is inside file 1 for the official workflow. Not requested: 13B models, fp8 files,
latent upscalers, IC-LoRA, any FLF/keyframe workflow (FLF stays disabled).

## B. Code to fetch (small, git, pinned by commit)

| Source | Commit | Licence |
|---|---|---|
| ComfyUI v0.3.47 | `2f74e17975696d829af455845c584574bbc85774` | GPL-3.0 |
| ComfyUI-LTXVideo | `36fdaf500b3cd6f7fa8b2dfec36e984746e630a2` | not asserted by GitHub — read its LICENSE |
| ComfyUI-VideoHelperSuite | `9e963ff5ed0b69e588ee3d965711766b0f3cf829` (proposed, unvalidated) | GPL-3.0 |
| ComfyUI-KJNodes | `ad37ce656c13e9abea002b46e3a89be3dba32355` (proposed, unvalidated) | GPL-3.0 |
| Official workflow file (inside the LTXVideo checkout) | blob `2260170f4ebacb077b938302b825e6e5a97b1290` | with ComfyUI-LTXVideo |

Python requirements of the custom nodes (`requirements.txt` of each) are unversioned in the sources read and would be
installed with pip on the GPU host; their versions are an **unresolved dependency pin** (research §7).

## C. Conditions attached to this approval request

1. Downloads happen only on the Kaggle session you start, after the Linux CPU verification notebook has been run and
   its receipt reviewed (docs/KAGGLE_RUNBOOK.md, Stage 1).
2. After download, run `python scripts/verify_ltx_pins.py` with `--models-dir`, `--source` for each checkout and the
   `/object_info` inventory; every file must be `PASS`. Only then may `ltx.checkpoint_sha256` in `config/models.yaml` be set.
3. Unresolved blockers B1–B8 in `docs/LTX_098_RESEARCH.md` are known; approving the download does not resolve them.
4. No Granth content is generated; the test image is synthetic.

## D. Approval

| Decision | Name | Date |
|---|---|---|
| Approve downloads A and B as listed (yes/no, with edits) | | |
