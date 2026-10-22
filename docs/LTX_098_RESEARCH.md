# LTX 0.9.8 — official source research (pre-validation)

Date of research: 2026-10-22. Status: **research only. Nothing was downloaded, installed or run.** Every pin below is
PROPOSED (`config/ltx_098_pins.yaml`, `status: PROPOSED_NOT_APPROVED`) and nothing here validates LTX, ComfyUI or any
model. Facts were read from GitHub and Hugging Face through a summarising fetch tool (not by cloning or hashing locally),
so each is marked with how it was confirmed. `scripts/verify_ltx_pins.py` re-checks them against real local files.

## 1. What is pinned

| Item | Proposed pin | How it was confirmed |
|---|---|---|
| ComfyUI | tag `v0.3.47`, commit `2f74e17975696d829af455845c584574bbc85774` | tag list read; compare API says commit `9bc2798` ("LTXV VAE decoder: switch default padding mode", 2025-07-16) is an ancestor (ahead_by 42). `v0.3.46` also contains it (ahead_by 38). The choice of 47 over 46 is mine, not an upstream recommendation. |
| ComfyUI-LTXVideo (custom nodes) | `36fdaf500b3cd6f7fa8b2dfec36e984746e630a2` (2025-07-16) | newest commit at/before the 0.9.8 release; its README lists the `ltxv-*-0.9.8` files. Its only change vs the previous commit is one 13B workflow. |
| Official workflow | `example_workflows/low_level/ltxvideo-i2v-distilled.json` at that commit; git blob `2260170f4ebacb077b938302b825e6e5a97b1290`, 18 595 bytes | contents API read twice, same sha and size |
| LTX checkpoint | `ltxv-2b-0.9.8-distilled.safetensors`, 6 340 744 492 bytes, SHA-256 `76aa8c47…cad8f`, repo `Lightricks/LTX-Video` @ `8984fa25007f376c1a299016d0957a37a2f797bb` | HF tree API oid and the raw git-LFS pointer file agree |
| Text encoder | `t5xxl_fp16.safetensors`, 9 787 841 024 bytes, SHA-256 `6e480b09…67635`, repo `comfyanonymous/flux_text_encoders` @ `6af2a98e3f615bdfa612fbd85da93d1ed5f69ef5` | tree API oid and raw LFS pointer agree |
| VideoHelperSuite (`VHS_VideoCombine`) | `9e963ff5ed0b69e588ee3d965711766b0f3cf829` (2025-07-14) | newest commit before 2025-07-17; **not checked against the workflow** |
| ComfyUI-KJNodes (`StringToFloatList`) | `ad37ce656c13e9abea002b46e3a89be3dba32355` (2025-07-16) | newest commit before 2025-07-17; the class was seen at KJNodes `main`, **not at this commit** |

Full 64-character hashes are in the pins file. The 2026 "latest" states of these repositories target LTX-2.x (the
workflow folder is now `2.0/2.3/2.5`); the 0.9.8-era files only exist at the old commits pinned above.

## 2. The official workflow, as read

`ltxvideo-i2v-distilled.json` is in **ComfyUI UI format** (`nodes`/`links` arrays), not the API format
(`class_type`/`inputs`) that `src/granthstudio/comfy.py` renders and submits. 18 nodes, 21 links:

`LoadImage` → `LTXVPreprocess` → `LTXVImgToVideo`(+ VAE from `CheckpointLoaderSimple`, text from `CLIPTextEncode` ×2 via
`CLIPLoader`) → `LTXVConditioning` → `CFGGuider` (cfg 1) → `SamplerCustomAdvanced` (noise `RandomNoise` [45, fixed], sampler
`KSamplerSelect` euler_ancestral, sigmas `StringToFloatList` "1.0000, 0.9937, 0.9875, 0.9812, 0.9750, 0.9094, 0.7250,
0.4219, 0.0" → `FloatToSigmas`) → `VAEDecode` → `VHS_VideoCombine` (24 fps, h264-mp4, crf 20). Two `Note` nodes are UI-only.
Defaults: `LTXVImgToVideo` widgets `[768, 512, 97, 1]` = width, height, length, batch. The note says the distilled model expects
that 8-step sigma list and `euler_ancestral`.

Facts that matter for the repository's adapter:
- It names the checkpoint **`ltxv-2b-0.9.6-distilled-04-25.safetensors`**, not 0.9.8. No official *2B 0.9.8* low-level workflow
  was found at the pinned commit (the 0.9.8 distilled workflows in `13b-distilled/` are for the 13B model). Replacing the
  file name with the 0.9.8 file is an inference that **has not been verified** (`checkpoint_substitution_verified: false`).
- The VAE comes from the checkpoint (`CheckpointLoaderSimple` output 2); no separate VAE file exists for this path.
- `LoadImage` takes an image **name inside ComfyUI's input folder**, but the adapter passes `START_IMAGE` as a filesystem path.
- The positive/negative prompts are widget text in the workflow; the adapter's placeholders are `START_IMAGE MOTION_PROMPT
  FRAMES SEED FPS WIDTH HEIGHT` only (no `NEGATIVE_PROMPT`, no sigma list, no checkpoint name placeholder).
- The designated output would be `VHS_VideoCombine`. `comfy.select_video` accepts mp4 items under `videos` or `gifs`; whether
  VHS reports under `gifs` on this ComfyUI was not verified.
- The seed lives in `RandomNoise` (`noise_seed`) upstream of the sampler, so `comfy.generation_seed` would change a
  cache-relevant input (the retry freshness gate is satisfied by that path).

## 3. Required node classes

Verified in ComfyUI source (`comfy_extras/nodes_lt.py` and `nodes_custom_sampler.py` at the pinned commit):
`LTXVImgToVideo`, `LTXVConditioning`, `LTXVPreprocess`, `SamplerCustomAdvanced`, `KSamplerSelect`, `CFGGuider`, `RandomNoise`.
Assumed core, not checked: `CheckpointLoaderSimple`, `CLIPLoader`, `CLIPTextEncode`, `LoadImage`, `VAEDecode`.
Third-party: `VHS_VideoCombine` (VideoHelperSuite, GPL-3.0, needs ffmpeg). `StringToFloatList` and `FloatToSigmas` are both
registered by ComfyUI-KJNodes at the pinned commit (`__init__.py` `NODE_CONFIG` entries read on 2026-10-22; they are absent from
ComfyUI core's `nodes_custom_sampler.py`). `StringToFloatList` takes one `string` input (multiline); the `FloatToSigmas` class body and its
input names were **not** read, so its API-format inputs are still unknown.
The pins file records these statuses honestly; the real answer comes from `/object_info` on a running server, which the verify
script compares class by class.

## 4. Frame, size and FPS rules (O-003) — source-supported

From `LTXVImgToVideo` in ComfyUI core: `length` has `min 9, step 8`; latent frames `= ((length − 1) // 8) + 1` (97 → 13);
`width`/`height` have `min 64, step 32` and the latent is `size // 32`. So **frames = 8n + 1** (9, 17, …, 97, 121) and
**width/height must be multiples of 32** (768×512 is the official default). The repository's frame list
`[49, 65, 81, 89, 97, 121]` all satisfy 8n+1 (checked by the verify script). The adapter does not enforce the rule or the
multiple-of-32 size; it only checks list membership (see blocker B5). FPS: the official example uses 24, equal to `FPS = 24` in
`pipeline.py`. The rule is from reading source, not from a run.

## 5. Expected T4 limits (estimates, not measurements)

- Checkpoint fp16 file is 6.3 GB; the T5-XXL fp16 encoder is 9.8 GB. A Kaggle T4 has ~15 GB VRAM and ~29 GB host RAM, so
  ComfyUI must offload the encoder; expect a long first-load time. fp8 files exist (2B fp8 4.46 GB) but T4 has no native fp8
  and their use here is unevaluated; the repo's `precision: fp16` is consistent with the fp16 file.
- 768×512×97 frames on a T4 is untested; peak VRAM, seconds per clip and flat-output (FP16 decode) risk are exactly what
  the first GPU run must measure. Kaggle sessions are time-limited; downloads of ~16 GB happen inside that budget.

## 6. Licences (summaries, not legal advice)

- **LTX weights:** "LTXV Open Weights License 0.X" (Lightricks, dated 2025-04-15, covers v0.9.6 onward): free for any purpose
  including commercial use, except entities with annual revenue ≥ US$10 M need a separate paid commercial agreement
  (ltxv-licensing@lightricks.com); redistribution needs the licence text and use restrictions passed on; prohibited uses
  include undisclosed machine-generated publication and deepfake impersonation; outputs are the user's responsibility.
  The licence text itself says the version date and release-date clause disagree (2025 vs 2024). **Owner/commercial status of
  the project needs a human decision before publishing generated video.**
- ComfyUI, VideoHelperSuite, KJNodes: GPL-3.0 (GitHub API). ComfyUI-LTXVideo: GitHub reports no recognised licence
  (`NOASSERTION`); read its LICENSE file. T5-XXL encoder repo: Apache-2.0 per HF metadata (underlying Google T5 licence not
  separately checked).

## 7. Unresolved questions and blockers

| ID | Question / blocker | Needed to resolve |
|---|---|---|
| B1 | Is the 2B **0.9.8** distilled checkpoint compatible with the 0.9.6-2B workflow graph unchanged? | A real run, or Lightricks' statement; no official 2B 0.9.8 low-level workflow found |
| B2 | `FloatToSigmas` provider is KJNodes (registered at the pinned commit), but its input names and the output slot semantics are unread | read the class in KJNodes at the pinned commit and compare with `/object_info` |
| B3 | UI-format workflow must become API-format with every widget value in the right slot | Export from a running ComfyUI with these nodes installed (or convert mechanically using `/object_info`); do not hand-write |
| B4 | `LoadImage` needs an uploaded/input-folder image name; adapter passes a path | Adapter change (upload via `/upload/image` or copy into the input folder) — a code change not made here |
| B5 | Adapter does not enforce 8n+1 or multiple-of-32 sizes; `config` `ltx.runtime.width/height` unset; test fixtures use 160×120 | Small validation change after the first run confirms the rule |
| B6 | `models.yaml` schema requires a separate `vae` file in `ltx.runtime.files`; this path has none | Decide: reuse the checkpoint entry, or make `vae` optional |
| B7 | Which T5 encoder packaging is "official": README names `google_t5-v1_1-xxl_encoderonly`; the example workflow uses `t5xxl_fp16.safetensors` | Owner choice; the example's file is pinned here |
| B8 | VHS and KJNodes commits are unvalidated proposals; GPL/other licences of the stack and the LTX revenue clause | Owner review |
| B9 | O-004 throughput budget and O-005 rubric still open | Owner decisions; the first test can only be recorded as "NOT VALIDATED" until set |
| B10 | Real-library behaviour of the model-identity evidence (`_commit_hash`) | Out of scope for LTX; part of later speech/translation validation |
