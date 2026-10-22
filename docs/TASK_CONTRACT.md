# Task contract

## Current task: M0, architecture audit (no implementation)

Status: COMPLETE, waiting for the user's GO on `docs/DECISIONS.md` P-001..P-003 and on starting M1.

Allowed in M0: reading the frozen architecture and project materials; writing planning documents; creating this repository and its instruction files; web reads to check model identity.
Not allowed in M0: implementation code, package installs, downloads of models, Kaggle or GPU execution, subagents.

## Next task when approved: M1, CPU production runner

Scope (frozen §§3, 4, 9, 10, 16; no model inference):
1. Draft for approval: episode manifest schema (O-001) and CLI contract (O-002).
2. YAML/JSON schema validation for project config, canon (characters, locations, terminology) and episode manifests.
3. Research lock: SHA-256 source receipts with schema version; an edit to a locked file creates a new source version.
4. Global canon registry with permanent IDs and aliases; uncertain matches are never merged automatically.
5. Stage scheduler (frozen §8 batch order) with per-job receipts: input hashes, workflow version, output hash; temporary output → verify → atomic rename; on restart verify receipts, skip valid jobs, resume the rest.
6. Tier 0 animated stills with FFmpeg and ffprobe duration checks (CPU only).
7. Bilingual assembly stub: two independent timelines from shared clips and per-language audio placeholders.
8. Dependency invalidation per frozen §16 (research edit, Hindi-only edit, canon edit, style or model version edit).

Acceptance (all with saved evidence under `benchmarks/` or `artifacts/reports/`):
- Unit tests pass for schemas, receipts, invalidation rules and resume (`uv run pytest`).
- An interrupted CPU run (killed mid-batch) resumes without redoing verified jobs, and the final outputs' hashes match a clean run.
- A modified locked research file is detected and blocks the dependent scenes.
- Tier 0 clip durations match ffprobe within one frame.
- Codex review returns PASS on the M1 diff, or every finding is fixed and re-reviewed.

Out of scope for M1: any GPU model, ComfyUI execution, TTS, translation, downloads.
