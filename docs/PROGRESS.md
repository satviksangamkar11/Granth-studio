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


## CPU audit corrections (Codex, explicitly authorized by the user)

- Corrected F01-F12: dependency/current-input receipt binding; approved research
  coverage/provenance; text-bound Hindi review; measured bilingual edits; actual media
  decode; runtime/workflow binding; durable ComfyUI prompt recovery; designated video
  selection; production GO; path containment; execution snapshot checks.
- Added reviewed imported-audio CPU path. TTS/translation/image generation remain absent
  or refusal stubs, and real ComfyUI/LTX remains NOT VALIDATED.
- Added global empty props registry, curated fact contracts, CPU timeout regression,
  and actual killed-process recovery checks including clean-vs-resumed final video hashes.
- Actual CPU test result: **95 passed, 1 skipped**. JUnit: `benchmarks/cpu_review_fixes.xml`.
  Skip reason is recorded in that receipt (host symlink creation unavailable).
- Actual repository CLI verification: `validate` exits 0; `plan 1` and `run 1 --execute`
  exit 2 because no research is approved. No real production outputs are generated.
- A complete synthetic CPU bilingual run is technically complete with independent
  durations; `released=false` without human production GO, as required.
- Documentation corrected: `IMPLEMENTATION_SPEC.md`, coverage matrix, operator guide,
  task contract and historical plan/decision status.
- No dependencies installed, real research approved, model downloaded, GPU/Kaggle
  accessed, commits made or branches changed. Frozen files/instruction files preserved.

### Remaining work

Actual curated research approval, human Hindi/speech acceptance, SDXL/style/reference
sheets, IndicTrans2/IndicF5, real LTX/ComfyUI validation, calibrated pilot acceptance,
voice licences, resource preflight and persistent Kaggle storage remain deferred.
CPU correction evidence is not a production readiness claim.


## Claude D1-D7 correction round — 2026-10-22

- User authorized Codex as sole author and authorized committing this round.
- Parent: `a85e070147bc759ad890b86c39c4fff81a469ce6` (receipt-verified, previously reviewed F01-F12 baseline).
- D1: definitive HTTP 4xx failures leave retryable journals; ambiguous network failures
  remain pending. D2: SRT floating-point overlap tolerance is 1 ns, with forward clamping.
- D3: approved pilot plan binds to the current compiled Adhyay 1 manifest. D4: recovery
  proof pins and rehashes actual matching clean/resumed outputs and the pilot plan.
- D5: GateFailure stops on its first attempt. D6: AV comparison uses measured stream
  timing and a two-sample allowance (2 ms fallback), never a blanket video frame.
- D7: whitespace-only coverage reviewer names fail schema validation.
- Added a real Windows junction-containment test; existing symlink test remains intact.
- Added 23 parameterized regression cases. The existing positive FLF NO-GO
  policy test retains its assertions; only its invalid legacy fixtures were migrated to
  current compiled pilot data and actual synthetic recovery files for the stricter gate.
- Focused run: 26 passed. Full CPU suite, run once:
  **118 passed, 1 skipped** (119 total).
- Full media recovery test again verifies both recovered final video hashes against clean
  runs. JUnit stores those hashes. Windows junction test ran; symlink creation is skipped
  on this host, with the precise reason preserved in the evidence receipt.
- Repository `validate`: exit 0. `plan 1` and `run 1 --execute`: exit 2 for missing approved
  research, preserving refusal behavior without starting production.
- Evidence: `benchmarks/claude_d_focused.xml`, `benchmarks/claude_d_cpu.xml`, and
  `benchmarks/claude_d_receipt.json`. Frozen files and real research remain untouched.
- No dependency install, model download, Kaggle/GPU execution or research/production GO.
- Next: independent read-only Claude review per `docs/CLAUDE_REVIEW_D1_D7.md`.
