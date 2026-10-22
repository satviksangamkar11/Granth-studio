# Current task contract: CPU correction and verification

The user explicitly authorized Codex to edit code and run CPU tests after the read-only
audit of `a2eea9c...a96b7de`. This is a task-specific override of the earlier reviewer-only
role; instruction files and the frozen architecture are preserved.

Scope: correct F01-F12 from the audit; add focused synthetic regression coverage;
complete CPU bilingual assembly and actual process-interruption recovery verification;
preserve honest STUB/NOT VALIDATED status for external integrations; update documentation.

Restrictions retained: no subagents, commits/push/merge/branch changes, dependency installs,
model downloads, GPU/Kaggle workloads, research/canon approval or production authorization.

Acceptance evidence:
- CPU regression suite and saved JUnit receipt under `benchmarks/`.
- Actual FFmpeg MR/HI assembly with measured unequal audio durations, complete speech
  coverage, shared visuals, valid streams and independent subtitles.
- Kill a child CPU process mid-batch; resume verified work and compare both final video
  hashes against a clean run.
- Regressions for dependency invalidation, receipt binding, live-input tampering,
  source coverage/provenance, Hindi review, model pins, prompt recovery, path safety,
  timeouts and snapshot-bound QA.
- Technical completion cannot authorize production without existing human evidence.

Real model/runtime/pilot acceptance remains deferred and must not be inferred from CPU
test passes. See `COVERAGE_MATRIX.md` for remaining partial, stub and missing components.


## Current round: Claude D1-D7 corrections (2026-10-22)

The user explicitly assigned Codex sole authorship, CPU test execution and committing
this correction round. The earlier no-commit restriction is superseded for this task.
Claude is the subsequent independent read-only reviewer. Preserve the frozen architecture,
original F01-F12 protections and real research; no Kaggle, GPU, models, frameworks or agents.

Required checks: focused regressions, one full CPU run, repository validation, diff and
accidental-file review, saved evidence/progress, complete correction commit, then stop.
The formerly uncommitted reviewed F01-F12 work is recorded as parent commit
`a85e070147bc759ad890b86c39c4fff81a469ce6` to keep this correction diff independent.
