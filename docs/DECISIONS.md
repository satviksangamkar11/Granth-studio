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
