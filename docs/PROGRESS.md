# Progress

## M0: architecture audit (2026-10-22). Commit a2eea9c. Complete.

Frozen architecture copied and hash-verified; audit docs and instruction files written.

## Implementation phase (2026-10-22, approved GO)

### Phase 1: foundations
- Changed: `pyproject.toml` (setuptools src layout, console script `granthstudio`); dependencies `pyyaml`, `jsonschema`; dev `pytest`.
- Changed: `src/granthstudio/{errors,integrity,schemas,config,cli}.py`; 10 JSON Schemas under `src/granthstudio/schemas/`.
- Checks: `granthstudio --help`, `version`, `config`, `validate` run on the repository and pass.

### Phase 2: research approval and source integrity
- Changed: `research.py` (receipts with version and SHA-256; any open or provisional item blocks; edits after approval raise SourceChanged).
- Checks: `test_governance.py` (approval gates, change detection, re-approval version 2).

### Phase 3: canon and identities
- Changed: `canon.py` (permanent IDs by kind; possible matches and shared names need explicit decisions; 'same' refused without a curated merge).
- Checks: `test_governance.py` (conflict, decision, pending-status refusal).

### Phase 4: manifests, compiler and timelines
- Changed: `episodes.py` (manifest contract; pins research version and canon digest; frames must be pinned; speaker must belong to scene), `timelines.py` (Marathi lock, Hindi alignment, protected terms, numeric facts, SRT with measured durations).
- Checks: `test_governance.py`, `test_timelines_and_scheduler.py`.

### Phase 5: scheduler
- Changed: `scheduler.py` (deterministic 20-hex task IDs; work folder renamed atomically; receipts re-verified on resume; retries; NOT VALIDATED never retried; stale work removed; run log).
- Checks: resume, tamper detection, retry, dependency blocking, interrupted-run recovery (`test_timelines_and_scheduler.py`).

### Phase 6: ComfyUI and FFmpeg adapters
- Changed: `comfy.py` (templates must be validated; placeholder rendering with escaping; backend with submit, wait, fetch), `ffmpeg.py` (probe, validate, Tier 0 motion, assembly; 300 s limit per call).
- Checks: real FFmpeg clips in `test_media_comfy_pilot.py`. ComfyUI NOT VALIDATED (no server run).

### Phase 7: quality gates, pilot, pipeline and CLI
- Changed: `qa.py` (six hard gates; diagnostics logged as not_computed), `pilot.py` (A-F mapping, D-004 throughput), `pipeline.py` (frozen stage order, plan, hard gates), `cli.py` (14 commands).
- Checks: `test_pipeline.py` (plan order, refusals, tier 0 real output and resume, CLI exit codes 3 and 2, report from receipts).

### Phase 8: documentation
- Changed: `docs/SPEC_SECTIONS_11_12_14.md`, `docs/OPERATOR.md`, `docs/COVERAGE_MATRIX.md`, `docs/DECISIONS.md` (P-001..P-003 approved; D-005..D-009).

## Test status
- `uv run pytest -q`: 58 passed in about 4 s (synthetic fixtures, real FFmpeg for media tests).
- Real repository: `validate` passes; `plan` and `run` refuse because no research is approved (expected).

## NOT DONE (deferred, by the user's rules)
- Kaggle T4 execution, LTX 0.9.8 2B runs, GPU benchmarks, the A-F pilot, human visual and sacred-accuracy review.
- Research approval for any adhyay (104 open and 75 provisional items remain blocked).
- Model downloads (LTX checkpoint, SDXL, IndicF5, IndicTrans2): none downloaded.
- Codex review: see the installation note below.

## Codex
- Installation: attempted once; see the final report for the exact result. Not blocking.

## Resume instructions
1. `cd "D:/aai work/granthstudio"`; `uv sync`; `uv run pytest -q` should report 58 passed.
2. `uv run granthstudio validate` and `uv run granthstudio config`.
3. Next work: (a) answer the Adhyay 1 open questions in `D:\aai work\v3_final\open_questions_ALL_1to12_FINAL.md` and approve Adhyay 1 with `research approve 1 --reviewer NAME --confirm` only after a human has reviewed `research/adhyay_01/research.yaml`; (b) on the Kaggle T4 runtime, pin the LTX checkpoint hash and export a validated ComfyUI graph; (c) then run the A-F pilot.
