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

## PROPOSED (not approved) 2026-10-23: video-safe style version `devotional_gouache_1950s_v2`

Same file, `canon/style.yaml` (`active` stays `devotional_gouache_1950s_v1`, frozen, sealed hash `2346c837…b7c1`, never edited; a test pins it). v2 is a sealed PROPOSED version that cannot drive generation until approved:
- keyframes are full-bleed: no border in the generated image (the v1 wording "vintage double-line paper border mount" is dropped; the negative prompt blocks border, frame, picture mount, drop shadow, vignette);
- one static RGBA double-line border (`canon/overlays/vintage_double_line_border_1080p.png`, sha256 `0992144c…899e`, generated by `scripts/make_border_overlay.py`) applied ONCE at final FFmpeg assembly, after motion and lip-sync, scaled to the assembled size with bicubic scaling; the receipt records size and aspect mismatch (the overlay is 16:9; LTX tests run 3:2, so a 3:2 overlay is the owner's call);
- gouache, egg tempera, ivory cardstock, sepia contours and the earthy palette are kept; deep indigo is added for dusk and night shadows only;
- composition `{prefix} {shot_description} {lighting} {suffix}`; the lighting phrase comes from a closed table keyed by the manifest's six lighting buckets (the phrases are DRAFTS written by the assistant: owner review required); free-text lighting and per-shot style overrides are refused; a keyframe shared by shots with different lighting is refused;
- style id/version/hash, lighting bucket and overlay SHA-256 enter keyframe requests, task inputs, LTX metrics, the assembly provenance and the production snapshot (both languages share one tag).
To approve: the owner sets status `frozen`, `approved_by`, `approved_on`, re-seals (`granthstudio.style.seal`) and switches `active`. Characters stay provisional; the frozen architecture and the LTX integration are untouched.
