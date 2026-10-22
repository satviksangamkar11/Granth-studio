# Decisions log

Each entry: ID, date, status (APPROVED / PROPOSED / OPEN), source, decision. Only APPROVED entries bind implementation. Edits to the frozen core need an approved architectural revision (frozen section 16).

## Approved

- **D-001 (2026-10-22, APPROVED, user):** GranthStudio Zero-DB v3.1 is the architectural baseline. Copy at `docs/ARCHITECTURE_V3_1.md`, sha256 `decd0af573e7b0c882d9dc5e8c98788bcecedd924a31dfc264ec1f883404f7c1`, identical to the freeze receipt `docs/ARCHITECTURE_V3_1.FREEZE.json` (staged originally under `C:\Users\Satvik\Documents\Codex\2026-10-22\use-d-drive-aai-work-granthstudio\freeze-staging\`).
- **D-002 (2026-10-22, APPROVED, user):** Roles. Claude Code is the sole developer and test executor; Codex is a read-only reviewer invoked at milestones. No other agent frameworks, planners or orchestration layers.
- **D-003 (2026-10-22, APPROVED, user):** Gate order: architecture audit → CPU production runner → LTX runtime validation on Kaggle T4 → six-shot A-F pilot → Codex review → user GO/NO-GO for production.
- **D-004 (2026-10-22, APPROVED, user):** Throughput accounting. Accepted sec/GPU-hour = accepted video seconds ÷ total GPU-hours consumed. Total GPU-hours include failed renders, retries and rework; two T4s for one hour = 2 GPU-hours. No numerical acceptance threshold has been set (still OPEN, see O-004).

## Proposed (need the user's GO)

- **P-001 (frozen §11, repository structure):** use the layout from the user's execution plan (`config/`, `canon/`, `research/adhyay_NN/`, `episodes/adhyay_NN/{manifest,shots,mr,hi}.yaml`, `workflows/comfyui/`, `src/granthstudio/`, `tests/`, `scripts/`, `benchmarks/pilot_af/`, `artifacts/` outside Git for media). Create directories only when a milestone needs them.
- **P-002 (pilot shot definitions):** the user's execution plan proposed a different A-F mapping (A ordinary I2V … F recovery). The frozen §15 mapping takes precedence (A Tier 0, B I2V recurring character, C FLF of the same shot, D gesture/dialogue coverage, E recurring character in different lighting, F shared-visual MR/HI edits). Recovery-after-interrupt becomes a mandatory pilot test alongside A-F, not a shot.
- **P-003 (pilot source):** use Adhyay 1 as the pilot chapter. It has the most checking (print verification of 26 items plus web verification); recurring characters Gajanan Maharaj, Bankatlal, Damodarpant; location the street outside Devidas Paturkar's house. Its remaining open questions must be answered and the chapter approved before the pilot's source lock.

## Open (no decision yet)

- **O-001 (frozen §12):** episode manifest schema (fields, provenance links, dependency invalidation, workflow versions, receipts). To be drafted in milestone M1 for approval; not invented here.
- **O-002 (frozen §14):** CLI commands and options. To be drafted in M1 for approval.
- **O-003 (frozen §7):** LTX frame-count and resolution rule. The freeze lists example frame counts 49, 65, 81, 89, 97, 121 without a formula. Confirm the exact rule from the pinned workflow and model code before use.
- **O-004:** numerical acceptance budget for accepted sec/GPU-hour and per-shot render time.
- **O-005:** human acceptance protocol for the pilot (who judges identity continuity and sacred fidelity, with what rubric). Automated metrics are diagnostics only (frozen §9).
- **O-006:** exact SDXL checkpoint, identity-conditioning method, art style (frozen §17 GATE OPEN).
- **O-007:** IndicTrans2 and IndicF5 exact versions, licences, and T4 compatibility; licensed or consented voice references (frozen §5.3).
- **O-008:** persistent artifact storage outside Kaggle (frozen §8, §9).
