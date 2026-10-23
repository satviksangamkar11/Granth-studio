# Model and dependency manifest for the 45-second pilot (FOR REVIEW; nothing downloaded, nothing accepted)

Read on 2026-10-23 from the public Hugging Face and GitHub APIs (metadata only). "VERIFIED" = value read from the API now. "TO VERIFY" = must be read and recorded (with SHA-256) before any execution. **Model selection is not licence acceptance**: the licence rows below are what each repository declares; the named approver, **Satvik Sangamkar**, must accept each one personally, and the pinned manifest below must be signed like `docs/LTX_098_DOWNLOAD_APPROVAL.md` section E before any download. Style v1 stays active.

Kaggle environment seen in earlier runs: Python 3.13.15, torch 2.11.0+cu128, two Tesla T4 (15 360 MiB each, sm_75, no native bf16), ComfyUI v0.3.47 (pinned `2f74e179...`), 30 GB RAM, large scratch disk (`/kaggle/temp`), 20 GB `/kaggle/working`.

## B. Native keyframes (SDXL + identity conditioning)
| Item | Pin (VERIFIED) | Size | Licence (declared) | Notes |
|---|---|---|---|---|
| SDXL Base 1.0 `sd_xl_base_1.0.safetensors` | repo `stabilityai/stable-diffusion-xl-base-1.0` @ `462165984030d82259a11f4367a4eed129e94a7b`; sha256 `31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b` | 6 938 078 334 B | CreativeML Open RAIL++-M (not gated) | use restrictions apply; approver must read and accept |
| IP-Adapter Plus SDXL ViT-H `sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors` | repo `h94/IP-Adapter` @ `018e402774aeeddd60609b4ecdb7e298259dc729`; sha256 `3f5062b8400c94b7159665b21ba5c62acdcd7682262743d7f2aefedef00e6581` | 847 517 512 B | Apache-2.0 | |
| Image encoder (ViT-H/14 laion2B, the one Plus ViT-H needs) `models/image_encoder/model.safetensors` | same repo/revision; sha256 `6ca9667da1ca9e0b0f75e46bb030f7e011f44f86cbfb8d5a36590fcd7507b030` | 2 528 373 448 B | model files from `laion/CLIP-ViT-H-14-laion2B-s32B-b79K` (MIT declared; trained on LAION data) | do NOT use `sdxl_models/image_encoder` (bigG, 3.69 GB) with this adapter |
| fp16-safe SDXL VAE (recommended on T4, avoids fp16 NaN) `sdxl.vae.safetensors` | repo `madebyollin/sdxl-vae-fp16-fix` @ `207b116dae70ace3637169f1ddd2434b91b3a8cd`; sha256 `235745af8d86bf4a4c1b5b4f529868b37019a10f7c0b2e79ad0abca3a22bc6e1` | 334 641 162 B | MIT | alternative: run the base VAE in fp32 (slower, VRAM) |
| ComfyUI node pack `cubiq/ComfyUI_IPAdapter_plus` | latest commit `a0f451a5113cf9becb0847b92884cb10cbdec0ef` (2025-04-14, "wording"; the repo announced "maintenance mode" two commits earlier) | source | GPL-3.0 | compatibility with ComfyUI v0.3.47 is TO VERIFY; GPL-3.0 applies to the node pack only (used as a tool, not shipped in an output) |
| ComfyUI core | existing pin `2f74e17975696d829af455845c584574bbc85774` | | GPL-3.0 | unchanged |
Total download about 10.65 GB (scratch disk). Not decided here: no LoRA (as instructed); a candidate API graph now exists (`workflows/comfyui/sdxl_ipadapter_keyframe.candidate.json`, UNVALIDATED; `sdxl_keyframe.json` remains an empty stub) and must be validated on Kaggle; Gemini images enter only as provisional identity/style reference inputs and never count as SDXL validation.

## C. Translation, speech, recognition, alignment
| Item | Pin (VERIFIED) | Size | Licence | Access |
|---|---|---|---|---|
| IndicTrans2 Marathi -> Hindi, `ai4bharat/indictrans2-indic-indic-1B` | @ `24d732922a0a91d0998d5568e3af37b7a21cd705` (distilled option `...-dist-320M` @ `ffb7582b6d43...`, 2.58 GB) | 9.68 GB repo (safetensors 4.83 GB) | MIT declared | **gated "auto"**: a logged-in Hugging Face account must accept access |
| IndicF5 TTS `ai4bharat/IndicF5` | @ `fb652a96e508091045890dae5bb99fe511facbcf`; `model.safetensors` sha256 `ba7f3671180fb778...` (full hash TO RECORD) | 1.41 GB repo | MIT declared | **gated "auto"**; its model card could not be read without login, so reference-audio requirements and the permission status of the bundled `prompts/*_F_*.wav` voices are TO VERIFY. **No voice may be used without documented permission** (see D1 below) |
| IndicConformer ASR (multilingual 600M) `ai4bharat/indic-conformer-600m-multilingual` | @ `2a77d305038dfc502fd9464e7d028b90381976cb` (404 files, ONNX + weights) | 2.56 GB | MIT declared | **gated "auto"**, `trust_remote_code` TO REVIEW before running |
| Alignment | proposal: forced alignment of the actually generated audio against the approved text using the IndicConformer CTC output with torchaudio's forced aligner (no extra model) | | torchaudio is BSD | needs its own validation on real generated audio (the alternative common aligners are non-commercial or lack Marathi, so I do not propose them) |
Not downloaded: the Hugging Face access acceptances and a token are human steps (the token goes into Kaggle Secrets; I will not read or handle it). Python dependencies (IndicTransToolkit, f5-tts, onnxruntime, transformers versions) are TO PIN from each model card after access is granted.

## D. Lip-sync candidate (only if a natural speaking shot exists)
`TMElyralab/MuseTalk` @ `2bcb936e2fddb4d86db4c62fd45b387d0c061571`; v1.5 weights `musetalkV15/unet.pth` sha256 `7ebf6c98c181e20838e4c0054e96e944ac60d5d692cc01db42839fe11b787007` (3.40 GB); repository licence declared MIT; not gated. It also needs whisper-tiny, DWPose, face-parse-bisent, sd-vae-ft-mse, S3FD/face-alignment: licences and hashes of each TO VERIFY (several are fetched from Google Drive/third-party mirrors). RISKS: the project pins an older Python/torch/mmcv/mmpose stack that is unlikely to install on Kaggle's Python 3.13 / torch 2.11 without a separate environment; it was trained for photographic faces, so painted faces may fail detection. If it cannot run, lip-sync is reported NOT_VALIDATED as you instructed. The passage's only natural speaking shot is Bankatlal's question (ovi 109); no scene is invented for it.

## D1. Decisions still needed from the approver before any of this runs
1. Whose voice references for Marathi and Hindi (documented permission/consent record), or explicit acceptance of IndicF5's bundled prompt voices once their permission status is read.
2. Acceptance of each licence above, and Hugging Face access requests for the three gated AI4Bharat repositories.
3. Hindi text policy: IndicTrans2 output is a candidate; you review sacred terms and names (the Hindi stage stays "reviewed translation").
4. Confirm ComfyUI_IPAdapter_plus (GPL-3.0, maintenance mode) is acceptable, or name an alternative identity-conditioning method.

## Execution gates (unchanged)
CPU tests green, Codex re-check, exact commit + bundle hash, explicit pin approval per Kaggle run, large files only on Kaggle scratch, small verified evidence copied back.
