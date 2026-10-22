# Implementation plan (historical M0 audit, 2026-10-22)

Current correction scope and evidence: `TASK_CONTRACT.md`, `PROGRESS.md`, `IMPLEMENTATION_SPEC.md`. The inventory below records the pre-implementation M0 state.

Authority: `docs/ARCHITECTURE_V3_1.md` (frozen). This plan does not change it.

## 1. What exists

- Frozen architecture and freeze receipt (hash verified, D-001).
- Research for Adhyays 1-12 as Markdown, not machine-readable: `D:\aai work\adhyay_NN\adhyay_NN_analysis.md`, `D:\aai work\v3\` (Adhyays 1-4 and 8-12 v3 files), `D:\aai work\v3_final\` (Adhyays 5-7 v3b, the combined character table, and the final question list). Read-only snapshots in `D:\aai work\frozen_*`.
- Research is NOT approved: 104 open questions (Part A) and 75 provisional items (Part B) in `D:\aai work\v3_final\open_questions_ALL_1to12_FINAL.md`. Adhyays 13-21 are not researched.
- No code, manifests, ComfyUI workflows or tests exist yet. Nothing reusable beyond the research files.
- Local tools present: git, Node.js, uv (Python 3.12), FFmpeg 8.1.1, Claude Code. Codex CLI and the Codex plugin are NOT installed (installing needs the user's yes).

## 2. Missing specifications (reported, not invented)

| Item | State | Handling |
|---|---|---|
| §11 repository structure | reserved, no content | proposal P-001 (user's layout) |
| §12 episode manifest contract | reserved, no fields | draft in M1 for approval (O-001) |
| §14 CLI interface | reserved, no commands | draft in M1 for approval (O-002) |
| Throughput formula | absent from freeze | supplied by the user, recorded D-004; threshold still open (O-004) |
| Frame-count formula | absent from freeze | confirm from the pinned workflow and model code (O-003) |
| Pilot shot mapping | two versions | frozen §15 wins (P-002) |

## 3. Biggest implementation risks (worst first)

1. **False model compatibility for LTX 0.9.8 2B.** The official checkpoint exists: `Lightricks/LTX-Video` has `ltxv-2b-0.9.8-distilled.safetensors` (6.34 GB) and `ltxv-2b-0.9.8-distilled-fp8.safetensors` (4.46 GB). But the current `ComfyUI-LTXVideo` example workflows on its default branch are only for the LTX-2 family (folders 2.0, 2.3, 2.5), so a "latest" workflow is the wrong family. The 0.9.8 graph must come from a pinned older node-pack revision or from ComfyUI's native LTXV nodes, both pinned by commit. The FP8 file is unsuitable for a Turing T4 and a user report describes a visible watermark with the 2B 0.9.8 distilled FP8 weights. T4 has no native BF16, so FP16 execution and VAE decode must be shown to be numerically stable on a real clip. Licence: the repository carries an LTX-Video open-weights licence that must be read before use.
2. **Unapproved, non-structured research.** The architecture requires locked, approved research with provenance. The research is free-form Markdown with 179 unresolved items and identity questions (for example Bankatlal Agarwal against "बंकटलाल पाटील हरी" in Adhyay 11, three Bhaskars, Dadasaheb against Khaparde). Converting it into canon and manifests needs a manual curation step for the pilot chapter; automatic merging of uncertain identities is forbidden (frozen §4.2).
3. **Acceptance that cannot be measured automatically.** Identity continuity, sacred fidelity and Hindi meaning cannot be proven by metrics (frozen §§9, 17). Without a written human acceptance protocol (O-005) and a numerical budget (O-004), the pilot cannot honestly return PASS. Kaggle session length and weekly GPU quota also bound every run; they must be measured, not assumed.

Other stack items are unverified and gated: the SDXL checkpoint and identity conditioning (O-006), IndicTrans2 and IndicF5 versions, licences and T4 behaviour, plus voice-reference consent (O-007), and persistent storage outside Kaggle (O-008).

## 4. LTX identity and compatibility requirements (for M2)

Record in `config/models.yaml` and the run receipt: model family (LTX-Video 0.9.8, not LTX-2); exact file `ltxv-2b-0.9.8-distilled.safetensors`, its Hugging Face revision and SHA-256; text encoder and VAE files with hashes; ComfyUI commit; node-pack name and commit (or native nodes); the workflow JSON hash; precision (FP16) and any cast; resolution and frame count accepted by the pinned code; decoded output checked with ffprobe (codec, frames, duration); peak VRAM per GPU; wall time. FLF (`LTXVAddGuide`) is tested separately and stays disabled unless it passes (frozen §7, §15).

## 5. Milestones

| ID | Milestone | Gate (evidence required) |
|---|---|---|
| M0 | Architecture audit (this) | user approves P-001..P-003 and GO for M1 |
| M1 | CPU production runner (`docs/TASK_CONTRACT.md`) | CPU tests and interrupt-resume test pass, Codex PASS |
| M2 | LTX 0.9.8 2B runtime validation on Kaggle T4 | one real I2V clip decoded, all identity fields recorded, VRAM and time measured; FLF tested separately |
| M3 | Audio and image stack validation on Kaggle (IndicTrans2, IndicF5, SDXL keyframes) | real outputs, licences recorded, terminology check blocks a seeded error |
| M4 | Six-shot A-F pilot (frozen §15) plus interrupt-recovery test | receipts, accepted sec/GPU-hour, human acceptance per O-005, Codex review |
| M5 | Production GO/NO-GO | user decision; research for the episode approved |

Kaggle steps need the user's GO and an upload approval for any data (the code bundle; no secrets).

## 6. First implementation milestone

M1, step 1: draft the episode manifest schema (O-001) and CLI contract (O-002) for the user's approval, then implement schemas, research lock and receipts with tests. Starts only after the user's GO.
