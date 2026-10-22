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
| VideoHelperSuite (`VHS_VideoCombine`) | `9e963ff5ed0b69e588ee3d965711766b0f3cf829` (2025-07-14) | newest commit before 2025-07-17; `VideoCombine` inputs and `h264-mp4` format widgets read AT this commit (Stage 2) |
| ComfyUI-KJNodes (`StringToFloatList`, `FloatToSigmas`) | `ad37ce656c13e9abea002b46e3a89be3dba32355` (2025-07-16) | newest commit before 2025-07-17; both classes read AT this commit (Stage 2): `nodes/nodes.py` and `nodes/curve_nodes.py`, registered in `__init__.py` |

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
- `LoadImage` takes an image **name inside ComfyUI's input folder**, and the adapter used to pass `START_IMAGE` as a filesystem path. **Stage 2:** fixed by staging the image through POST `/upload/image` (B4).
- The positive/negative prompts are widget text in the workflow; the adapter's placeholders are `START_IMAGE MOTION_PROMPT
  FRAMES SEED FPS WIDTH HEIGHT` only. **Stage 2:** the candidate uses exactly these seven (`MOTION_PROMPT` = positive prompt, `WIDTH`/`HEIGHT`
  = LTXVImgToVideo, `FRAMES` = `length`, `FPS` = both frame_rate fields); the negative prompt, sigma list and checkpoint name are literals.
- The designated output would be `VHS_VideoCombine`. `comfy.select_video` accepts mp4 items under `videos` or `gifs`; whether
  VHS reports under `gifs` on this ComfyUI was not verified.
- The seed lives in `RandomNoise` (`noise_seed`) upstream of the sampler, so `comfy.generation_seed` would change a
  cache-relevant input (the retry freshness gate is satisfied by that path).

## 3. Required node classes (updated in Stage 2)

All 15 classes now have a source-read input signature (`scripts/comfy/node_signatures.yaml`); the file/commit each was read from is
recorded per entry. ComfyUI core at `2f74e17`: `CheckpointLoaderSimple`, `CLIPLoader` (type list includes `ltxv`), `CLIPTextEncode`, `LoadImage`,
`VAEDecode`, `LTXVPreprocess`, `LTXVImgToVideo`, `LTXVConditioning`, `RandomNoise`, `CFGGuider`, `KSamplerSelect`, `SamplerCustomAdvanced`.
ComfyUI-KJNodes at `ad37ce6` (GPL-3.0): `StringToFloatList` (`nodes/nodes.py`: one `string` input) and `FloatToSigmas`
(`nodes/curve_nodes.py`: input `float_list`, FLOAT with `forceInput` so it is a link; returns SIGMAS; both registered in `__init__.py`
`NODE_CONFIG`). ComfyUI-VideoHelperSuite at `9e963ff`: `VHS_VideoCombine` (required: images, frame_rate, loop_count, filename_prefix,
format, pingpong, save_output; the `h264-mp4` format adds pix_fmt, crf, save_metadata, trim_to_audio; OUTPUT_NODE; returns `ui.gifs`).
Every entry was read through a summarising fetch tool; the authoritative cross-check is the converter run against the live
server's `/object_info` (section 8, step 6 of the GPU script).

## 4. Frame, size and FPS rules (O-003) — source-supported

From `LTXVImgToVideo` in ComfyUI core: `length` has `min 9, step 8`; latent frames `= ((length − 1) // 8) + 1` (97 → 13);
`width`/`height` have `min 64, step 32` and the latent is `size // 32`. So **frames = 8n + 1** (9, 17, …, 97, 121) and
**width/height must be multiples of 32** (768×512 is the official default). The repository's frame list
`[49, 65, 81, 89, 97, 121]` all satisfy 8n+1 (checked by the verify script). The adapter does not enforce the rule or the
multiple-of-32 size; it only checks list membership (see blocker B5). FPS: the official example uses 24, equal to `FPS = 24` in
`pipeline.py`. The rule is from reading source, not from a run.

## 5. T4 precision and memory plan (read from ComfyUI `2f74e17` source; nothing measured)

- **The diffusion model will not run in fp16.** `supported_models.LTXV.supported_inference_dtypes = [bfloat16, float32]` (no fp16 entry). A T4
  (compute capability 7.5) has no native bf16, and `model_management.should_use_bf16` is False below capability 8. In `unet_dtype()` the first
  pass finds nothing; the second pass (manual cast) picks bf16 only if `torch.cuda.is_bf16_supported()` AND the weights in fp32 would not fit
  (`model_params * 4 > maximum_vram_for_weights`, about 12 GiB on a 15 GB card); otherwise **float32**. For a ~2B-parameter DiT that means fp32
  weights of roughly 7-11 GB. The shipped `precision: fp16` therefore does not describe what happens on a T4; the schema now allows
  `fp16|bf16|fp32`, the first-test project records `fp32` as the *expected* value, and the ComfyUI log excerpt in the receipt is the evidence.
- **VAE:** the LTXV VAE's `working_dtypes = [bfloat16, float32]`; on a T4 `vae_dtype()` falls to **float32** (no flag needed). The "flat output from an
  fp16 decode" risk in the architecture is therefore *expected* not to arise (the VAE is expected to decode in fp32); this is a source-derived expectation, the log must confirm it, and the flat-output check stays on.
- **Text encoder:** `text_encoder_dtype()` is fp16; `t5xxl_fp16.safetensors` (9.8 GB) goes to the GPU at encode time when `model_size * 1.2` fits in free
  memory (a fresh 15 GB card), then ComfyUI's model manager is expected to offload it to host RAM to make room for the DiT (`NORMAL_VRAM`: partial loading;
  `minimum_inference_memory` about 1.2 GiB). The two models are not expected to need to be resident together, but overlap or partial offload is possible and unmeasured; host RAM (~29 GB on Kaggle) must hold the encoder.
- **Speed:** fp32 on a T4 (~8 TFLOPS) is far slower than fp16 would be; 8 distilled steps at 768x512, 49 frames is expected to be slow but finite.
  This is an estimate, not a measurement. If the DiT does not fit, ComfyUI streams weights (slower); a hard out-of-memory is a FAIL with evidence.
- **Not equivalent to Lightricks' own inference config:** their 2B 0.9.8 config uses multi-scale generation, the spatial upscaler and bf16. The ComfyUI
  low-level path used here is single-stage, no upscaler, and (on a T4) fp32. Quality equivalence is not claimed.
- **Extra artifacts:** none. The T5 tokenizer files are in the ComfyUI repo (`comfy/text_encoders/t5_tokenizer`), the VAE is in the checkpoint,
  `LTXVPreprocess`/VHS/KJNodes load no models. ComfyUI-LTXVideo is used only as the source of the workflow file and is not installed as a node pack
  (its `requirements.txt` would add `diffusers`, `transformers[timm]`, `ninja`). Verified only by reading source; the run log would show any download attempt.
- **Abort rules, enforced before any submission:** unmet source pin, missing/mismatched hash, class absent from the live `/object_info`, converter
  output different from the committed candidate, fewer free VRAM/RAM/disk than the floors, not exactly one Tesla T4, no valid session deadline.

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

## 7. Stage 2 blocker matrix

| ID | Blocker | Status | Evidence / where it lives |
|---|---|---|---|
| B1 | 0.9.8 checkpoint inside a workflow that names the 0.9.6 file | **OPEN, UNVERIFIED** (substitution recorded, never silent) | No official 2B-0.9.8 workflow exists (model card: "N/A"). Circumstantial: the official 13B-distilled workflows at the pinned commit use the same `CheckpointLoaderSimple` + `CLIPLoader(t5xxl_fp16, ltxv)` + `euler_ancestral` + identical 8-step sigma string with 0.9.7/0.9.8 file names. The verifier reports `workflow:model_names` UNVERIFIED and the first GPU test is the actual check. |
| B2 | `FloatToSigmas` source and inputs | **RESOLVED by source** | KJNodes `ad37ce6` `nodes/curve_nodes.py`, input `float_list`, registered in `NODE_CONFIG`. |
| B3 | UI-format workflow to API format | **RESOLVED in tooling, UNVERIFIED on the live server** | `scripts/comfy/ui_to_api.py` + recipe produce `workflows/comfyui/ltx_i2v_098.candidate.json` (16 nodes) from the reconstructed inventory; every connection comes from the UI links, every literal from `widgets_values`; 11 listed overrides and 1 defaulted widget (`strength = 1.0`, absent from the older UI file) are printed. Proof on the GPU host: rebuild from the official file and the live `/object_info`, then `compare` must say IDENTICAL. |
| B4 | `LoadImage` needs a name in ComfyUI's input folder | **RESOLVED in code** (fake-server tested) | `ComfyBackend.upload_image` (POST `/upload/image`, content-addressed name) used by `pipeline._ltx_run` for `START_IMAGE`/`END_IMAGE`. The real endpoint is unverified until the GPU run. |
| B5 | Frame and size rule not enforced | **RESOLVED in code** | `config.ltx_dimension_problems` (frames 8n+1 ≥ 9; width/height multiples of 32 ≥ 64) is enforced when `models.yaml` loads and again in `validate_ltx_inputs`. |
| B6 | Embedded vs separate VAE | **RESOLVED** | Embedded (official workflow takes VAE from `CheckpointLoaderSimple` output 2). `ltx.runtime.files.vae` may now be `null`; text encoder stays mandatory. |
| B7 | T5 packaging | **RESOLVED for the first test** | The example's `t5xxl_fp16.safetensors` (type `ltxv`) is pinned; the README's encoder-only alternative is not used. |
| B8 | VHS/KJNodes commits, licences, LTX revenue clause | **OPEN: owner approval** | Commits are the newest before the 0.9.8 release, not validated against the workflow beyond the class registrations above. |
| B9 | O-004 throughput budget, O-005 rubric | **OPEN: owner decisions** | The first test uses explicit floors (10 GB free VRAM, 12 GB RAM, 30 GB disk, 30 min session), which are safety floors, not budgets. |
| B10 | `_commit_hash` evidence behaviour in real libraries | **OUT OF SCOPE here** | Speech/translation validation. |
| B11 | Negative prompt | **GranthStudio's own text** | The official one exceeded the 125-character read limit and was not reproduced; effect on quality unknown. Positive prompt = the shot's `motion_prompt` only (LTX-2B prefers long descriptive prompts). |
| B12 | Custom-node Python requirements are unpinned | **OPEN** | The GPU script records `pip freeze`; no version pin exists in the sources read. |
| B13 | Whether 2B fp16 + T5-XXL fp16 fit and finish on a T4 | **UNMEASURED** | The test records peak VRAM, wall time, and the preflight report. |
| B14 | VHS reports the mp4 under `gifs` | **Source-supported, unverified live** | `comfy.select_video` accepts `gifs`; the real history shape is checked by the run. |

## 8. Exact sequence the GPU script follows (scripts/kaggle/ltx_first_test.sh)

1 require approval variable and exactly one Tesla T4 → 2 clone the four sources at pinned commits (checked) → 3 install requirements,
record `pip freeze` → 4 download the two weight files from pinned revisions and `sha256sum -c` against the pins → 5 start ComfyUI,
save `/system_stats` and `/object_info` → 6 rebuild the API workflow from the official file + live `/object_info` and require
IDENTICAL to the committed candidate → 7 `scripts/ltx_first_test.py --execute`: static pin verification, synthetic project, readiness,
one Tier-1 shot through `load_bundle(benchmark=True) → plan_tasks → gate_gpu_tasks → Scheduler.run`, clip probe, receipt.
Recovery and fresh-render retry are NOT part of this first run; they follow only after a decoded clip.
