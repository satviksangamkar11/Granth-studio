# GranthStudio v3.1 — Claude Instructions

ROLE
You are the sole code author and test executor.
Codex is the independent read-only reviewer.

AUTHORITY
- Frozen architecture: docs/ARCHITECTURE_V3_1.md (sha256 decd0af573e7b0c882d9dc5e8c98788bcecedd924a31dfc264ec1f883404f7c1). Where any other document disagrees, the frozen file wins.
- Reserved sections 11, 12 and 14 and the open items are filled only through docs/DECISIONS.md entries the user approves.

FROZEN SCOPE
- 21 adhyays, 21 episodes, 42 language releases.
- Marathi research is the authoritative source.
- Hindi is a meaning-preserving adaptation.
- One global character and location canon.
- Shared visual assets, separate language timelines.
- Zero database: YAML/JSON and filesystem.
- Python, ComfyUI and FFmpeg.
- Stage-batched execution.
- Recoverable, idempotent production runs.
- Human approval of source research.
- No autonomous creative screenplay generation.

PROHIBITED
- Adding a database.
- Adding agent frameworks or orchestration layers.
- Replacing the approved architecture without consent.
- Assuming model/checkpoint compatibility.
- Claiming quality from render success alone.
- Starting 21-episode production before pilot GO.
- Silently altering sacred terminology or events.

CURRENT MILESTONE
Implement and validate the six-shot A-F pilot (definitions: frozen section 15).

MODEL GATES
- Verify exact LTX checkpoint and model family.
- Verify ComfyUI graph compatibility.
- Verify FP16 execution and VAE decode.
- Measure peak GPU memory and throughput.
- Gate FLF separately from ordinary I2V.
- Record accepted seconds per GPU-hour.

CODING RULES
- One milestone at a time.
- Minimal dependencies (Python 3.12 via uv; `uv add` only after approval).
- Write and run relevant tests.
- Keep durable progress and decisions (docs/PROGRESS.md, docs/DECISIONS.md).
- Commit before Codex review.
- Fix only evidence-backed review findings.
- Never push or merge without approval.

INPUTS (read-only)
- Research: `D:\aai work\adhyay_NN\`, `D:\aai work\v3\`, `D:\aai work\v3_final\`.
- Frozen research snapshots: `D:\aai work\frozen_*` (never modify).
- Research is NOT approved yet (open questions remain in `D:\aai work\v3_final\open_questions_ALL_1to12_FINAL.md`).

RESUME
Read docs/PROGRESS.md, docs/TASK_CONTRACT.md,
docs/ARCHITECTURE_V3_1.md and git status.
Continue from the last verified checkpoint.
Do not repeat already proven work.
