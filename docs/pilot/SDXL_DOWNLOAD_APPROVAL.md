# SDXL pilot stage: download and use authorization (owner instruction recorded verbatim; licences NOT individually reviewed by the assistant)

Date 2026-10-23. Owner and sole licensee of this personal project: **Satvik Sangamkar**.

Owner's words (chat): "Proceed with the SDXL stage first. ... This is my personal project, so skip the license part. And focus on the completion of steps now."
Earlier the owner approved the GPL-3.0 IP-Adapter node "as the technical choice for internal pilot evaluation" and asked that acceptance not be recorded until explicitly confirmed. This instruction is recorded here as the owner's explicit decision to proceed with the downloads below without a licence-review step. It is **not** a statement that the assistant read, summarised or accepted any licence on the owner's behalf: the licences remain whatever each repository declares (listed in `config/pilot_sdxl_pins.yaml`), and the use restrictions of CreativeML Open RAIL++-M and the GPL-3.0 terms of the node pack apply to this work whether or not they were reviewed. The owner is responsible for compliance.

Authorized downloads (exact pins and SHA-256 in `config/pilot_sdxl_pins.yaml`; every file is hash-verified after download, any mismatch aborts): `sd_xl_base_1.0.safetensors`, `ip-adapter-plus_sdxl_vit-h.safetensors`, the ViT-H image encoder (renamed `CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors`), `sdxl.vae.safetensors` (fp16-fix VAE), and the `cubiq/ComfyUI_IPAdapter_plus` commit `a0f451a5113cf9becb0847b92884cb10cbdec0ef`, onto Kaggle scratch storage only.

Scope: PROVISIONAL TECHNICAL TEST of the SDXL stage for the three-scene pilot. The story, characters and shot plan are confirmed by the owner for this test only; this does not approve the final Granth adaptation, any canon, or a release. Style v1 stays active; style v2 stays proposed. Each GPU execution still needs the exact-commit authorization (`LTX`-style pin) from the owner.
Not covered: the AI4Bharat audio models (gated on Hugging Face; the owner's account must grant access), any voice, any other model.

Approver (named human): Satvik Sangamkar   Date: 2026-10-23 (chat instruction above)
