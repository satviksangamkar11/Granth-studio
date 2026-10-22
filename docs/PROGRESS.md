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


## Claude H1/M1/L1/R1 correction round — 2026-10-22

- Parent: `c2c7daaa77c6fde9d6f1143bace40a6c974038e4` (review verdict FAIL).
- H1 (F08): an HTTP 4xx is definitive only outside `/history/` polling. A 403/404/429 while
  polling stays `JobPending`, keeps the `submitted` journal and original `prompt_id`, and
  never re-POSTs, including across scheduler retries (`max_attempts=3`).
- M1: recovery evidence is refused when any two clean/resumed or Marathi/Hindi records
  are one file (same normalized path, Windows case variant, or same device/inode, which
  covers hard links). Hash checks unchanged. Not done: binding outputs to scheduler
  task receipts (no such field in the recovery contract; needs a decision).
- L1: Tier-0 stills render `ceil` whole frames, so off-frame durations (1.3 s) no longer
  fall a frame short; a short clip now reports a visual-duration error, not "extra speech".
- R1 (demonstrated defect): 44.1/22.05 kHz speech drifted 4 samples over 12 shots and
  was refused. Speech is now resampled whole and measured; silence is sized in samples
  to land on the planned timeline. No speech trimming.
- D6 follow-up (demonstrated defect): MP4's default 1/1000 s movie timescale cut the
  muxed audio edit list to whole ms (8 samples short), failing the 2-sample check for
  most chapter lengths. `assemble` now sets `-movie_timescale` to the audio rate.
- Tests: D4 cases now assert the exact refusal reason; added Adhyay-1 D3 binding test.
- Full CPU suite, run once: **130 passed, 1 skipped** (symlink test, host lacks symlinks).
  Evidence: `benchmarks/claude_h_cpu.xml` (clean == recovered final video hashes, both
  languages). `validate`: exit 0.
- No dependency install, model download, Kaggle/GPU execution or research/production GO.
  LTX/ComfyUI/IndicF5 behaviour behind real tunnels remains NOT VALIDATED.
- Follow-up (user-approved): recovery evidence is now bound to real scheduler runs. Each
  output must be listed with its hash in a valid `task_receipt.json` of the matching
  `assemble_<lang>` task; clean and resumed come from different stores with the same task
  ids; the resumed store's run log must show a resumed task and the clean store's none.
  Copies outside task folders, swapped languages, shared stores, never-resumed or reused
  "clean" runs are refused with specific reasons. Synthetic fixtures now produce evidence
  by running the scheduler (clean run; interrupted then resumed run), not hand-written files.
  Full CPU suite after this follow-up: **137 passed, 1 skipped** (symlink test); `validate` exit 0.


## Remaining-pipeline sprint (Phases A-F) — 2026-10-22

Branch `sprint/remaining-pipeline`, parent `0964494`. One writer, one checkpoint commit per phase. The frozen
architecture (sha256 `decd0af5…f7c1`) is unchanged; `pyproject.toml` and `uv.lock` are unchanged (no new
dependencies). Nothing was run on a GPU, no model was downloaded, no research was approved, no production GO exists.

- **A — Kaggle runtime** (`d100feb`): `runtime.py`, `config/runtime.yaml`. Preflight, pinned fetch, `local_dir` durable
  storage with hash-manifest export/restore, session-deadline stop (`deferred` tasks), run receipts, pin-only
  bootstrap, dual-T4 refused. CLI `runtime …`, `session N`.
- **B — LTX/ComfyUI** (`05bbd3d`): checkpoint-binding check, node availability, token-tagged submissions with
  `comfy reconcile|cancel|inspect`, input validation interface, per-clip metrics. Shipped workflows remain stubs; the
  0.9.8 graph, frame rule (O-003) and VAE were NOT invented.
- **C — SDXL / visual canon** (`3e9919b`): `keyframes.py`, `canon/visual_assets.yaml`, `refs …`. Refuses while checkpoint,
  identity method and style are unselected (O-006).
- **D — language and audio** (`20e0ed0`): `runners.py`, `translation.py`, `speech.py`; consent-gated voices, hash-bound
  approvals, ASR reports, provenance into `provenance.json`. Models unselected (O-007).
- **E — research importer** (`b534a57`): `importer.py`, `research import|check-draft|promote`. Reproduces exactly 104 open
  and 75 provisional items; writes only an unloadable draft; never approves, answers or merges.
- **F — pilot and diagnostics** (`7f0bc58`): `pilotrun.py`, `diagnostics.py`, `config/pilot.yaml`. Found and closed a
  circularity (the pilot could not run because LTX needed receipts only a pilot produces) with an explicit benchmark mode.
  Receipts from run data, hash-bound rubric reviews, evidence report with no verdict, recovery evidence from two real runs.

Testing: fake ComfyUI server over real sockets, fake subprocess runners, synthetic fixtures. Full CPU suite is recorded
in `benchmarks/sprint_cpu.xml`. These tests show interfaces and refusals work; they do not show any real model, workflow,
GPU timing or translation/voice quality works.

Open decisions that block real execution: O-003 frame rule, O-004 throughput budget, O-005 review rubric, O-006 SDXL
checkpoint/identity/style, O-007 IndicTrans2/IndicF5/ASR choices, voice licences, O-008 storage provider; plus the
research approval itself (Adhyay 1 still has unresolved items).

Handoff for the independent re-review: diff `0964494..HEAD`; check (1) strict mode is unchanged and benchmark mode is
reachable only from `pilot`; (2) no code path writes `approvals/adhyay_NN.json`, sets a status to `validated`, or
answers/approves research; (3) every runner/ComfyUI refusal is exit 3 and produces no output; (4) the two refactors
(`verified_runtime_hash`, `check_recovery_evidence`) are behaviour-neutral.

## Final integration audit corrections (H1–H7, M8–M10)

Base `0964494`, audited `42e2917`. No architecture change; frozen SHA-256 `decd0af5…f7c1` verified unchanged.
CPU/synthetic evidence only; no model, GPU, Kaggle run or research approval.

- **H6** `keyframes._register`: asset id must match `^ref_[a-z0-9_]+$`, image suffix whitelisted, destination built with
  `contained_path` (resolves symlinks/junctions) before any mkdir/copy.
- **H5** `speech.generate_speech`: consent check for every line, then the full `load_bundle` gate (approved research,
  Marathi lock, Hindi review hashes, protected terms, numeric facts, speaker/shot attribution) before any TTS call.
- **H1** `episodes.compile_episode` counts cutaway actions only for cutaways referenced by coverage;
  `episodes.unplaced_required_actions` is enforced at assembly (`pipeline._assembly_run`) and in `_verify_assembly`.
- **H4** `runtime.GPU_CHECKS` now includes `sources`; `require_gpu_ready` names the failing source pin.
- **H3** `comfy.execute` journals `completed`; `comfy.reject_output` (called by the scheduler on a `TaskFailed` from run/verify,
  via `Task.journal`) turns a completed-but-invalid render into `rejected`, so the next attempt posts with a new attempt
  token. Uncertain submission/polling states are never rejected, so no duplicate POST.
- **H2** `pilotrun.selection` takes the dependency closure after adding assembly tasks.
- **H7** `lipsync.style_identity`; runner section needs `validated_style_version` + `validated_style_sha256`
  (fail closed when unset); the style digest is part of the lip-sync task inputs, so a style change invalidates outputs.
- **M8** `speech.align_words(source="release"|"candidate")`; release uses current approved timeline audio with text/audio
  hash checks; candidates write `*.align.candidate.json` and stale candidate records are refused.
- **M9** `pilotrun._language_report` requires both audio SHA-256 and normalized-text SHA-256; otherwise kind `stale`.
- **M10** `scripts/runners/_identity.py`: runners load the approved model at the approved revision, require
  `config._commit_hash` evidence, refuse env substitution, and print `verified` (stored as `runner_verified` on candidates).

Full CPU suite at source revision `5f8152d`: **279 passed, 2 skipped** (the symlink test skips without privilege). JUnit: `benchmarks/cpu_final_audit.xml`.

Remaining external limitations: the real IndicF5/IndicTrans2/ComfyUI/LTX/lip-sync runtimes were not run; the M10
evidence field (`_commit_hash`) is verified only against fake libraries.

## Closing the final eight audit findings (base `6998608`)

CPU/synthetic evidence only; frozen architecture SHA-256 `decd0af5…f7c1` unchanged. Source commit `8688853`:
**295 passed, 2 skipped**. JUnit `benchmarks/cpu_final_eight.xml`, receipt `benchmarks/cpu_final_eight_receipt.json`.

1. **Trimmed cutaways** `episodes.trimmed_required_actions`: a cutaway that is the only credit for a required action must be placed whole, checked per language at assembly and on resume (`source_duration_s` in the edit plan).
2. **Rejected-output cache** `comfy.generation_seed`: after a rejection the sampler seed is offset by the rejection count and recorded; an identical rejected graph is refused (ComfyUI caches by node inputs, not prompt id).
3. **Durable budget** `comfy.execute(max_attempts)` counts POSTs in the journal; exhaustion refuses until `comfy reset-budget --reviewer --confirm`. Polling/reconcile never spend it.
4. **Ownership** `comfy.owned`: O_EXCL lock file around the decision+POST; a lock older than 300 s is moved aside, and an owner that died after intent leaves state `submitting`, which still forces reconcile.
5. **Namespace** `comfy.store_namespace`: per-store id in tokens and `extra_data`; reconcile only matches its own namespace.
6. **GPU readiness** `runtime.gate_gpu_tasks` on `run`, `session` (aborts), `refs generate` and `pilot run`; unready or CPU-only runs turn GPU tasks into `not_validated`; LTX preflight also checks source pins.
7. **Reference paths** `integrity.create_new_file`/`reject_link_components`: anchored to the artifact root, no link/junction components, O_EXCL destination, link-count check.
8. **Model provenance** `runners.identity_block`: `model_identity` (verified/unverified) from runner → candidate → approval → release provenance; mismatch rejected, missing evidence stays `unverified`. Real-library `_commit_hash` behaviour remains unvalidated.

Skipped: two symlink-creation tests (symlinks unavailable without privilege on this host; the junction tests ran).
