# GranthStudio v3.1: instructions for Claude

ROLE: you are the only code writer. Codex is a read-only reviewer; it never writes code.

AUTHORITY
- Frozen architecture: `docs/ARCHITECTURE_V3_1.md` (sha256 decd0af5…f7c1). Do not edit it. Frozen wins over every other document.
- Decisions: `docs/DECISIONS.md`. Only APPROVED entries bind you. Proposals and OPEN items wait for the user.

RULES
- No database, agent framework, or orchestration layer. No subagents.
- Dependencies: pyyaml, jsonschema, pytest only. Add a new one only with user approval.
- Never claim LTX, ComfyUI, IndicF5, IndicTrans2 or SDXL works without real execution evidence. Mark them NOT VALIDATED.
- Never approve research with open or provisional items. Never invent Granth content, canon, or dialogue.
- Tests use synthetic fixtures only.
- Commit at each checkpoint. Never push or merge without approval.

CHECKS BEFORE A COMMIT
- `uv run pytest -q` passes.
- `uv run granthstudio validate` passes on the repository.
- Update `docs/PROGRESS.md` after each phase.

RESUME
Read `docs/PROGRESS.md`, then `git status`. Continue from the last recorded checkpoint. Do not repeat verified work.
