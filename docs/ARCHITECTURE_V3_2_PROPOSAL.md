# GranthStudio architecture revision proposal v3.2 (PROPOSED, not approved)

Status: PROPOSED by the assistant on 2026-10-24 after the owner's freeze ("we need to change the architecture for quality") and approval of the replan (plan file `C:\Users\Satvik\.claude\plans\frolicking-forging-hippo.md`). `docs/ARCHITECTURE_V3_1.md` (sha256 decd0af5…f7c1) is NOT edited (D-001, D-005 precedent). Per frozen §16 a revision binds only after the owner approves it and a new checksum receipt is recorded. Until then the v3.1 behaviour stays the default and every item below is opt-in.

## Why (evidence, not opinion)

All from the frozen pilot (`freeze/pilot-v1-2026-10-24`, `docs/pilot/SDXL_STYLE_AUDIT.md` §1-11):
1. SDXL base + IP-Adapter could not hold the 1950s gouache look and several identities at once: global references collapse multi-person scenes; style-only conditioning loses faces between scenes.
2. LTX 0.9.8 on a T4 adds a push-in the prompt cannot stop and smears faces (`docs/evidence/pilot_video`).
3. Tier 0 and LTX clips have different sizes and nothing conforms them.
4. The style lock covers the prompt text only; references and outputs are never measured against the target look.

## Changes against the frozen document

| # | v3.1 text | Proposed v3.2 | Reason |
|---|---|---|---|
| R1 | §6/§13/§17 LOCKED: "SDXL canonical keyframes" | Keyframes come from a backend chosen by benchmark among: Nano Banana (owner session or Gemini API), FLUX.2 klein 4B, Qwen-Image-Edit-2511, SDXL (kept as fallback). The backend sits behind the existing JSON-over-stdio runner contract (`src/granthstudio/runners.py`), not ComfyUI-only. | One identity mechanism must hold several characters; SDXL+IP-Adapter did not. §15 already allows replacing the rendering workflow after a NO-GO. |
| R2 | §4.4 reference sheets "front, three-quarter, profile, full body" | Reference library per character with views, poses and costumes derived from the Adhyay 1-6 needs (`docs/pilot/REFERENCE_LIBRARY_SPEC.md`), one hashed manifest per set. | The text needs seated poses, a back view and costume changes, not only four standing views. |
| R3 | §7 Tier 0 "animated stills" (slow zoom) and Tier 1 LTX I2V default | Tier 0 becomes a code-driven animation toolkit (exact camera paths, 2.5D parallax, layered figure motion, particles) driven by a per-shot JSON motion spec; AI image-to-video is used only for shots that need a real action, and any AI clip is reframed by the same toolkit. Candidate AI models: Wan 2.2 TI2V-5B, FramePack, LTX 0.9.8 (benchmarked, not assumed). | Deterministic motion, no push-in or face smear, runs on CPU/T4. |
| R4 | §10 assembly | One episode output size from config; every clip is scaled/padded to it before assembly. | Remove the 768x512 vs 1280x720 mismatch. |
| R5 | §9 QA diagnostics (CLIP/style similarity listed, not computed) | A computed style score of each reference and keyframe against an owner-approved style anchor image, recorded as a diagnostic (no threshold enforced until calibrated). | The picture, not only the text, must stay on style. |
| R6 | §2D "minimal orchestration" | Unchanged. The animation toolkit is a Python + FFmpeg script collection, not an orchestration layer; no Node/Remotion/HyperFrames. | Keeps D-006. |

Not changed: Marathi lock, Hindi adaptation review, IndicF5/IndicTrans2/IndicConformer, receipts and gates, frozen style v1 text, Codex review, exact-commit pins, human review rule.

## Constraints that stay

- New heavy dependencies (depth model, segmentation model, HTTP clients, API keys) live only in runner/host scripts, never in the package (D-006). Each needs an owner entry in DECISIONS.
- NVIDIA hosted endpoints are "evaluation and prototyping" only (NVIDIA FAQ): never used for final frames. Gemini API is paid (~USD 0.03-0.07 per image) and its output terms must be read before any final use.
- A backend that cannot prove which model and revision produced an image records `unverified` and stays NOT VALIDATED.
- Frozen style v1 stays ACTIVE; style v2 stays PROPOSED.

## Approval needed from the owner

Approve (or amend) R1-R6. Until approved: work proceeds on the branch `replan/quality-v3_2` as opt-in code and documents; nothing changes on `sprint/remaining-pipeline` or the freeze branch.
