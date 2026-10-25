# Decisions log

Each entry: ID, date, status (APPROVED / PROPOSED / OPEN), source, decision. Only APPROVED entries bind implementation. Edits to the frozen core need an approved architectural revision (frozen section 16).

## Approved

- **D-001 (2026-10-22, APPROVED, user):** GranthStudio Zero-DB v3.1 is the architectural baseline. Copy at `docs/ARCHITECTURE_V3_1.md`, sha256 `decd0af573e7b0c882d9dc5e8c98788bcecedd924a31dfc264ec1f883404f7c1`, identical to the freeze receipt `docs/ARCHITECTURE_V3_1.FREEZE.json` (staged originally under `C:\Users\Satvik\Documents\Codex\2026-10-22\use-d-drive-aai-work-granthstudio\freeze-staging\`).
- **D-002 (2026-10-22, APPROVED, user):** Roles. Claude Code is the sole developer and test executor; Codex is a read-only reviewer invoked at milestones. No other agent frameworks, planners or orchestration layers.
- **D-003 (2026-10-22, APPROVED, user):** Gate order: architecture audit → CPU production runner → LTX runtime validation on Kaggle T4 → six-shot A-F pilot → Codex review → user GO/NO-GO for production.
- **D-004 (2026-10-22, APPROVED, user):** Throughput accounting. Accepted sec/GPU-hour = accepted video seconds ÷ total GPU-hours consumed. Total GPU-hours include failed renders, retries and rework; two T4s for one hour = 2 GPU-hours. No numerical acceptance threshold has been set (still OPEN, see O-004).

- **P-001 (repository structure, APPROVED 2026-10-22, user):** the layout in `docs/SPEC_SECTIONS_11_12_14.md`. Media lives outside Git in `../granthstudio-artifacts`.
- **P-002 (pilot shot definitions, APPROVED 2026-10-22, user):** frozen §15 defines A-F (A Tier 0, B I2V recurring character, C FLF, D gesture/dialogue coverage, E different lighting, F shared-visual MR/HI edits). Recovery is a required test beside A-F.
- **P-003 (pilot chapter, APPROVED 2026-10-22, user):** Adhyay 1. Its source lock needs all open and provisional items answered and the chapter approved; until then the pipeline refuses to compile it.

## Implementation decisions (2026-10-22, approved with the implementation GO)

- **D-005:** Sections 11, 12 and 14 are implemented as the specification in `docs/SPEC_SECTIONS_11_12_14.md`. The frozen document is not edited.
- **D-006:** Runtime dependencies are limited to `pyyaml` and `jsonschema`; test dependency `pytest`. No database, no agent framework, no orchestration platform.
- **D-007:** Every external integration that has not been run here is an explicit NOT VALIDATED stage (LTX I2V/FLF, SDXL keyframes, IndicF5, IndicTrans2, ComfyUI). It raises and never reports success.
- **D-008:** Synthetic fixtures are used for tests only (`tests/conftest.py`). No Granth text is committed as fixture or canon.
- **D-009:** Execution is sequential. Worker concurrency stays benchmark-dependent (frozen §8).

## Open (no decision yet)

- **O-001 (frozen §12):** derived manifest contract implemented under D-005; CPU enforcement corrections in `IMPLEMENTATION_SPEC.md`. This does not approve production research or model configuration.
- **O-002 (frozen §14):** CLI contract implemented under D-005; model execution remains gated.
- **O-003 (frozen §7):** LTX frame-count and resolution rule. The freeze lists example frame counts 49, 65, 81, 89, 97, 121 without a formula. Confirm the exact rule from the pinned workflow and model code before use.
- **O-004:** numerical acceptance budget for accepted sec/GPU-hour and per-shot render time.
- **O-005:** human acceptance protocol for the pilot (who judges identity continuity and sacred fidelity, with what rubric). Automated metrics are diagnostics only (frozen §9).
- **O-006:** exact SDXL checkpoint, identity-conditioning method, art style (frozen §17 GATE OPEN).
- **O-007:** IndicTrans2 and IndicF5 exact versions, licences, and T4 compatibility; licensed or consented voice references (frozen §5.3).
- **O-008:** persistent artifact storage outside Kaggle (frozen §8, §9).

## Task-specific correction authorization

The user explicitly authorized Codex code edits and CPU tests after the independent audit.
No frozen-core revision, research approval, model compatibility decision, acceptance budget
or production GO was supplied by that authorization.

## Owner decision 2026-10-23: provisional global art style (art-style part of O-006 only)

The owner froze `devotional_gouache_1950s_v1` (canon/style.yaml, sealed by `content_sha256`) as the project-wide look for all current pilot and mini-film work, identical for Marathi and Hindi.
Prompts compose as {prefix} {shot_description} {suffix} (src/granthstudio/keyframes.py; the request said `runner.py`, which does not exist in this repository, so the composition lives where every SDXL prompt is built).
Style id and hash are recorded in keyframe requests, `metrics.json`, task inputs (keyframe, LTX shots, both assembly tasks) and the production snapshot, so a change cannot happen silently. A second style in `visual_assets.yaml` is refused.
Not decided here: the SDXL checkpoint, the identity-conditioning method (rest of O-006) and any character design. Characters stay provisional; SDXL stays NOT VALIDATED.

## Replan 2026-10-24 (after the pilot freeze)

- **D-010 (2026-10-24, PROPOSED, assistant; direction approved by the owner when they approved the replan plan):** architecture revision v3.2 as written in `docs/ARCHITECTURE_V3_2_PROPOSAL.md` (R1-R6: backend-neutral keyframes, reference library spec, code-driven Tier 0 animation toolkit, one episode size, style score against an approved anchor). `ARCHITECTURE_V3_1.md` is not edited. Binds only after the owner approves the text and a checksum receipt is recorded (frozen §16).
- **D-011 (2026-10-24, APPROVED, owner choices while approving the plan):** (a) keyframe backend decided by a benchmark of Nano Banana, FLUX.2 klein and Qwen-Image-Edit on the same three pilot scenes, owner picks; (b) code animation is the default motion, AI video only for real actions; (c) the free NVIDIA LLM instead of Claude is a bounded experiment only (NVIDIA terms: evaluation use).

## Owner decisions 2026-10-24 on the v3.2 proposal

- **D-012 (2026-10-24, APPROVED, owner):** (a) **R3** (code-driven Tier 0 animation) and **R4** (one clip size at assembly) of `docs/ARCHITECTURE_V3_2_PROPOSAL.md` are approved now; **R1** (non-SDXL keyframe backend) waits for the benchmark; R2 (reference library) is approved as the working spec; R5 (style score) and R6 (no orchestration layer) stay as proposed with no objection recorded. (b) The reference prompts omit the frozen "double-line border" clause (approved exception); keyframe prompts keep the full frozen text. (c) The keyframe benchmark uses OPEN models on Kaggle only (FLUX.2 klein, Qwen-Image-Edit, others the research recommends); the paid Gemini API is not used. Free NVIDIA API-catalog endpoints may be called with the owner's own keys for quick prototyping (owner: personal, non-commercial work). (c1) Keys are never pasted into chat, stored in a repository file or printed: they are read from environment variables on the owner's PC. (d) Start the reference library with a 5-image test (Maharaj 3/4, Maharaj seated eating, Bankatlal 3/4, a distinct Damodarpant, one house plate) and expand only if they look right. (e) New host-script dependencies (torch, transformers, Pillow, numpy, Depth-Anything-V2-Small) are accepted for scripts/animation; they stay out of the granthstudio package (D-006).

## Architecture v4 freeze 2026-10-24

- **D-013 (2026-10-24, APPROVED, owner: "FREEZE THE NEW PLANS"):** `docs/ARCHITECTURE_V4.md` is the frozen architecture for new work (receipt `docs/ARCHITECTURE_V4.FREEZE.json`). Owner choices recorded in it: Nano Banana API as the production image backend (owner supplies a billed key, kept outside the repository); Kimi K3.1 Pro writes the code with Codex review; one renderer chosen by a same-scene acting bake-off between Blender and HyperFrames; FFmpeg assembly; Nano Banana supplies separate body parts on request. Mandatory additions: Character Performance Engine, source-locked Cinematic Coverage Planner, shot asset packages with a reconstruction test, request lifecycle with UNKNOWN, three QA levels with risk routing. This supersedes D-010 (v3.2 proposal) and replaces the paid-API exclusion in D-012(c) for images. `docs/ARCHITECTURE_V3_1.md` stays unedited. Not implied: implementation, benchmarks, renderer choice, research approval or human review.

## Architecture v4 amendment 2026-10-24

- **D-014 (2026-10-24, APPROVED, owner):** Blender is the primary and only planned production renderer for GranthStudio v4; the Blender-versus-HyperFrames bake-off in D-013/`ARCHITECTURE_V4.md` is removed. HyperFrames stays outside the production pipeline, available only as a separately approved fallback if Blender fails the quality test in `ARCHITECTURE_V4.md` section 12. Nano Banana Pro (owner's key), Kimi (coding and planning) and FFmpeg stay as decided in D-013. First milestone: one complete Maharaj blessing scene with an audit (seams, hand anatomy, motion, consistency, render cost); no expansion and no full-episode pipeline before the owner approves that audit. 2.5D rigged illustrations only; no full 3D modelling; no additional renderers or paid services. The original freeze tag `arch-v4-freeze-2026-10-24` (commit 818fe6b) is preserved; this is a new amendment commit and tag. Receipt updated in `docs/ARCHITECTURE_V4.FREEZE.json`.

## V5 production plan 2026-10-25

- **D-015 (2026-10-25, APPROVED, owner: "freeze the plan and start"):** `docs/pilot/V5_PRODUCTION_PLAN.md` rev 4 is the working plan for V5 production. The format is a **motion-comic-style devotional film** (approved illustrations, camera moves, staged poses, cuts, effects, narration), not fully animated continuous performance. Methods: A (layered art + camera) and C (pose-to-pose cuts) are the defaults; B (rigged puppet) is optional and limited to one action A+C cannot communicate. **Amends D-014 in exactly two points:** (1) "2.5D rigged illustrations only" becomes "2.5D illustrations; rigging optional"; (2) D-014's first milestone (a rigged Maharaj blessing scene) is replaced by the **A+C blessing-performance audit** (Phase 1, owner-signed). Blender-only, 2.5D, no full 3D, no extra renderers or paid services stay. Kimi K3.1 Pro writes all animation code and shot plans (Codex reviews first); Claude writes only harness, validators, ledger and glue. **The owner generates all images himself in Nano Banana / Google Flow; the project makes no image-API calls.** Money cap: **$50 Kimi spend for Phases 0-3**, enforced by a local reservation ledger that must be tested before any paid use; Phase 4 (first full Adhyay, +$40) needs a separate approval. drawn-by-code is a fallback only with the owner's yes. Source text approvals come before any voice or shot. TTS candidates (Indic Parler-TTS, IndicF5, Indic-Speak) are all NOT VALIDATED until executed. Not implied: Blender riso look works, voices work, any cost figure beyond the caps, or human review of any film (NOT_DONE).

- **D-016 (2026-10-25, APPROVED, owner: "I approve the look"):** the V5 look is the **original flat-colour illustrations as generated (no riso print)**; D-015's riso print effect is dropped (the builder's `riso.strength` stays at 0). Phase 1 JSON route produced three 6-second shots (SA temple, SB blessing, SC pot) from builder sha256 `bf7d3266...` then `c671ab16f9d0f0af671c76236f914bd704ef406c7b867f313943694c9853598b` (owner-approved, Codex SAFE); Phase 1 Kimi spend $0.38 of $15 (provider token counts). Recorded as done, not yet done: larger zoom values via JSON, a "glossy" effect (needs a reviewed builder change), the written A+C blessing audit, Phase 2 onwards. No human review of any film (NOT_DONE). The owner said do nothing further until told.
