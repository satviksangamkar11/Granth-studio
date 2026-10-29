# Proposed update of `CLAUDE.md` (checklist row 2). NOT applied: `CLAUDE.md` is the owner's file; the owner decides.

## Lines that contradict the owner's later rules (2026-10-26 to 2026-10-29)
1. `ROLE: you are the only code writer. Codex is a read-only reviewer; it never writes code.`
   -> owner rule 2026-10-28: Claude writes NO code. Nemotron 3 Ultra writes all code and tests (thinking ON, effort medium), through `scripts/source/coder_run.py`. Claude writes specs, runs the tests, copies passing files, and reviews. Reviewers (read-only): Haiku 5.5 at low effort, and GLM 5.3 flash while Codex is out of limit (Codex medium again when available).
2. `No database, agent framework, or orchestration layer. No subagents.`
   -> read-only Haiku reviewer agents and a Haiku-low Flow image agent are approved by the owner (2026-10-27/28/29). Keep "no database, agent framework or orchestration layer".
3. `Dependencies: pyyaml, jsonschema, pytest only.` -> still true for the repo code; unchanged.
4. `Tests use synthetic fixtures only.` -> real-file tests against the owner's own data (Adhyay 1 files, the Chapter 2 docx in `canon/test_inputs/`) are used where the owner asked for them; keep synthetic fixtures as the default.
5. Add: no Kimi call in any test or trial (Nemotron only); every paid call goes through the credit ledger and needs the owner's go.

## Suggested replacement text (ROLE and RULES blocks)
```
ROLE: Claude writes no code. The coder model (Nemotron 3 Ultra, thinking on, effort medium) writes code and tests; Claude writes specs, runs tests, copies passing files and reviews. Reviewers are read-only: Haiku 5.5 (low) and GLM 5.3 flash (Codex medium when available).
RULES
- No database, agent framework, or orchestration layer. Read-only reviewer agents and the owner-approved Haiku-low Flow image agent are allowed.
- No Kimi call in tests or trials. Every paid call needs the credit ledger and the owner's go.
```
