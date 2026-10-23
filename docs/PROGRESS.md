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

## Seven safety corrections after the Codex re-review (base `fa32a5a`)

CPU/synthetic evidence only; frozen architecture SHA-256 `decd0af5…f7c1` unchanged. Source commit `10c007d`:
**310 passed, 2 skipped** (both symlink-creation tests; unprivileged symlinks are unavailable here, the Windows junction tests ran).
JUnit `benchmarks/cpu_final_seven.xml`, receipt `benchmarks/cpu_final_seven_receipt.json`.

- **F4** `comfy.owned`: an OS lock (`msvcrt.locking` / `fcntl.flock`) on a persistent lock file, held for the transaction and
  released by the OS when the process dies. No age-based takeover exists. Tests use two real child processes
  (`tests/_comfy_child.py`): a live owner paused before writing intent is not displaced; crash before/after POST recovers
  through reconcile with no duplicate; journal write failure submits nothing.
- **F7** `integrity.create_new_file`: POSIX walks `dir_fd` with `O_NOFOLLOW`; Windows pins every ancestor without
  `FILE_SHARE_DELETE` and rejects reparse points; `O_EXCL` destination; partial copies removed; fails closed elsewhere.
  Deterministic race tests (junction planted before mkdir; ancestor swap before open) create nothing outside the root.
- **F6** `runtime.require_host_ready` is called from the GPU task boundary (`_ltx_ready`, `sdxl_preflight`, `usable_runner`), so a
  direct `Scheduler.run` with matching pins but failed VRAM/session submits nothing and blocks dependents.
  `gate_gpu_tasks` still adds CPU-only refusal and the session abort.
- **F2** `comfy.generation_evidence`: freshness is judged on the closure upstream of the designated output (fingerprint plus seed
  inputs found on that path). A disconnected `{{SEED}}` or a seedless path cannot satisfy the retry gate. Fingerprint, seed
  inputs and attempt are stored in the journal history and clip metrics. The fake ComfyUI now has a node-level dependency cache.
- **F3** the established `max_attempts` is stored in the journal and is authoritative; callers can only tighten it. Only
  `comfy reset-budget` spends more.
- **F5** the namespace is bound to the store location. Same location keeps it across restarts/restores; a copy elsewhere forks to
  a new namespace (`forked_from`), cannot touch parent journals, and needs `comfy adopt` (named reviewer; `--original-inactive`
  for outstanding prompts).
- **F8** every runner execution is recorded as content-addressed run evidence (request, response, configured and reported
  identity, outputs hashes) under `artifacts/evidence/model_runs`. Candidates, approvals and release provenance carry
  `model_identity` and `evidence_sha256` per candidate; approval re-verifies the evidence. This makes tampering detectable, not
  impossible: nothing authenticates the runner. Real-library `_commit_hash` behaviour stays NOT VALIDATED.

## Round 2 after the seven-fix acceptance review (base `46f1ab2`)

Source commit `6b0b999`: **315 passed, 3 skipped** (two symlink-creation tests, plus a POSIX-only parent-swap sentinel test that cannot run on this Windows host, so POSIX behaviour remains untested). JUnit `benchmarks/cpu_final_round2.xml`, receipt `benchmarks/cpu_final_round2_receipt.json`.

- F7: POSIX length/validation/cleanup now use the open descriptor and pinned parent (no pathname after creation).
- F2: freshness ignores the save node's own fields; seed inputs are read from upstream nodes only.
- F5: BASE plain-text namespaces migrate in place; adoption keeps `submission_namespace` so an uncertain submission is still found.
- F8: approval recomputes the candidate text hash; evidence also binds request inputs (speech request/text hash, translation Marathi hash); release re-verifies evidence for generated audio and model-candidate translations.

## Round 3 after the narrow re-review (base `97f34ea`)

Source commit `3a3195e`: **318 passed, 3 skipped** (two symlink-creation tests and one POSIX-only sentinel test; POSIX behaviour is not executed on this Windows host). JUnit `benchmarks/cpu_final_round3.xml`, receipt `benchmarks/cpu_final_round3_receipt.json`.

- F2: the output node is excluded unconditionally; an output-only graph yields no seed evidence and a rejected retry is refused.
- F8: `_verify_audio` and `_verify_assembly` re-verify generated-audio and model-translation evidence on every resume; translation release is checked against the current Hindi text hash and the current Marathi hash.

## Linux CPU verification on Kaggle (executed 2026-10-22)

Notebook `notebooks/kaggle_linux_cpu_verify.ipynb` (Kaggle kernel `sangeetasangamkar/granthstudio-linux-cpu-verify`, version 2, private,
accelerator None, internet off, dataset `granthstudio-cpu-baseline`) ran the accepted baseline `f8d5d02f609a68806e8272617d1e04c98cf6040c`
(detached) with harness scripts from bundle tip `942932d`. Receipt verdict: **LINUX_CPU_PASS_ON_KAGGLE**.

- Host: Linux 6.18.48 x86_64, Python 3.13.15, ffmpeg 6.1.1, 4 CPUs, ext4, no GPU, running as root (uid 0).
- Full suite: **319 passed, 0 failed, 0 errors, 2 skipped**; the two skips are Windows-only tests (case-insensitive paths, Windows junctions).
- All 10 required POSIX tests passed without skips (two-process journal lock, crash recovery, parent-swap sentinel, symlink/redirect refusals);
  5 supplementary POSIX primitive tests passed (fcntl flock, dir_fd, second-process lock contention, symlink, dangling symlink).
- Architecture SHA-256 equals the frozen value. Evidence: `benchmarks/linux/` (receipt, environment, JUnit, log, zip).
- Limits: the session ran as root, so permission-based refusals were not exercised; Kaggle version 1 of the notebook failed in its first cell
  (an unguarded `nvidia-smi` call, fixed in `454734f`) and is not a test result. This does not validate any GPU, model, ComfyUI or LTX behaviour.

### Linux CPU verification, run 2 with the corrected harness (executed 2026-10-23, Kaggle kernel version 3)

Supersedes run 1 (kept in `benchmarks/linux/run1_superseded/`), which used a harness that ignored pytest exit codes and accepted a reduced
collection (Codex findings, fixed in `1e563e1`). Code under test: the accepted baseline `f8d5d02f609a68806e8272617d1e04c98cf6040c`
(detached); harness: bundle tip `1e563e1`. Receipt verdict **LINUX_CPU_PASS_ON_KAGGLE**.

- Pytest exit codes: full suite 0, supplementary 0. Collected 321 of the expected 321 baseline tests; 319 passed, 0 failed, 0 errors, 2 skipped
  (the Windows-only case-variant and Windows-junction tests).
- Required POSIX tests 10/10 passed, supplementary POSIX checks 5/5 passed, none skipped.
- Host: Linux 6.18.48, Python 3.13.15, ffmpeg 6.1.1, CPU only, root (uid 0). Architecture SHA-256 equals the frozen value; every artifact hash in the
  receipt matches the files and the zip (`benchmarks/linux/`).
- Rerun safety is covered by a unit test that executes the notebook's setup cell twice; this Kaggle run was a fresh kernel, not a second Run All.
- Not validated: any GPU, model, ComfyUI or LTX behaviour.

## Stage 2: LTX 0.9.8 integration blockers (code commit `4881340`, base `5077465`)

Windows CPU suite at that commit: **367 passed, 3 skipped**, JUnit `benchmarks/cpu_stage2.xml`, receipt `benchmarks/cpu_stage2_receipt.json`. Not run on Linux again; no GPU,
model, ComfyUI or Kaggle GPU run. All real model capabilities remain NOT VALIDATED. Nothing was downloaded.

- Research: pinned ComfyUI `2f74e17`, ComfyUI-LTXVideo `36fdaf5`, VideoHelperSuite `9e963ff`, KJNodes `ad37ce6`; input signatures of all 15 node classes read from source;
  `FloatToSigmas` is in KJNodes `nodes/curve_nodes.py` (input `float_list`). See `docs/LTX_098_RESEARCH.md` (blocker matrix, section 7).
- Adapter: `config.ltx_dimension_problems` (8n+1 frames, multiples of 32) enforced on config load and in `validate_ltx_inputs`; `ltx.runtime.files.vae` may be null (embedded VAE);
  `ComfyBackend.upload_image` stages START/END images through POST `/upload/image` (fake-server tested; the real endpoint is unverified); test fixtures that used 160x120 now use 160x96.
- Workflow: `scripts/comfy/ui_to_api.py` + recipe produce `workflows/comfyui/ltx_i2v_098.candidate.json` from a reconstructed inventory (the official file was only read, not saved);
  one defaulted widget (`strength`) and 11 overrides are reported. The shipped stub templates are unchanged.
- Tools: `scripts/verify_ltx_pins.py` gained API-workflow structure checks; `scripts/ltx_first_test.py` runs one Tier-1 shot through the existing pipeline;
  `scripts/kaggle/ltx_first_test.sh` is the guarded GPU command (refuses without `LTX_DOWNLOAD_APPROVED`).
- Open: B1 (0.9.6 workflow vs 0.9.8 checkpoint), live proof of the converter, download approval (docs/LTX_098_DOWNLOAD_APPROVAL.md), O-004/O-005, T4 fit, unpinned custom-node requirements.

### Stage 2 review round (Codex narrow review of `5077465..ecd231d`: FAIL, 4 blocking + 4 other findings; all 8 fixed)

Blocking: (1) `ltx_first_test.py` could submit without approval/one T4/static verification -> `main()` now enforces `LTX_DOWNLOAD_APPROVED`, exactly one Tesla T4, no `--skip-static-verify`,
a valid session deadline; (2) dirty pinned checkouts were used before the cleanliness check -> every clone is checked clean immediately, before any install or launch; (3) an unrelated server on the
ComfyUI port could be accepted -> port must be free, launched process must stay alive, argv marker checked when reported; (4) the documented command lacked the session deadline -> the script
computes and validates it before any clone/download and also requires `LTX_EXPECTED_COMMIT`. Others: converter now refuses unconsumed/misdirected UI wires and wired-widget mismatches; verifier rejects
negative slots and judges the seed on the output's dependency path; the upload reply must echo the requested name; a resumed identical run is accepted. Also from source reading: LTXV runs fp32 on a T4
(research section 5), so `precision` accepts fp16|bf16|fp32 and the first test records `fp32` as expected; ComfyUI-LTXVideo is no longer installed as a node pack.

## Stage 2 final (pre-download) status — code commit `0860a32df877adc57d7712648c001ce3f147140a`

- Windows CPU suite: **390 passed, 4 skipped** (`benchmarks/cpu_stage2d.xml`). Linux CPU run on Kaggle (kernel version 4, baseline `f8d5d02` + harness at this commit): **LINUX_CPU_PASS_ON_KAGGLE**,
  319 passed / 2 Windows-only skips, 10/10 required POSIX tests, **6/6 supplementary** including `port_owner.py` against the real Linux /proc (`benchmarks/linux/stage2_run3/`).
- Fresh Kaggle bundle published: private dataset `sangeetasangamkar/granthstudio-cpu-baseline`, branch tip `0860a32df877adc57d7712648c001ce3f147140a`, bundle SHA-256 `0da9607e…49df10` (538 708 bytes). That bundle is SUPERSEDED (see the next section): the dataset now holds the later reviewed commit `2a5865b`.
- Codex: Stage 2 narrow reviews FAIL -> fixes -> PASS WITH ISSUES; final delta check: SAFE FOR THE FIRST T4 TEST = yes (one low, non-blocking note on `port_owner.py` exit codes for unreadable /proc tables).
- Nothing downloaded; no GPU use; the LTXV licence has not been accepted by a human; all real capabilities remain NOT VALIDATED.

### Owner decision on the first T4 test (2026-10-23): approve with edits
Approved in principle: download the two pinned weights after human licence acceptance, one Kaggle T4, a 240-minute maximum session, one synthetic I2V clip, a controlled cache/retry experiment after a first
successful clip. Not approved: full Adhyay scenes, production validation. Added in response: one attempt per run and a clean stop on CUDA out-of-memory (no automatic retry or variant),
`notebooks/kaggle_ltx_first_test.ipynb` (approver name and expected commit are typed by the human; nothing is pre-signed). Phase 1 remains the source-backed short video through the complete pipeline;
this clip is only a technical prerequisite.


### Bundle in the dataset now (supersedes the one above) and the last Codex micro-check
- Private dataset `sangeetasangamkar/granthstudio-cpu-baseline` holds the bundle with branch tip **`2a5865b96045612d7893e7d0f1929926668b38be`** (SHA-256 `f18b3c04…0b611a62`, 578 250 bytes). That is the value
  to type as `EXPECTED_COMMIT` in `notebooks/kaggle_ltx_first_test.ipynb`. Docs/evidence commits made after it are not in the bundle and need no rebuild; do not rebuild before the run.
- Windows CPU suite at `2a5865b`: 394 passed, 4 skipped (JUnit kept outside the repo at D:/kaggle_upload/stage2_evidence/cpu_stage2e.xml). The Linux/Kaggle run of `0860a32` still covers the POSIX harness, which did not change after it.
- Codex micro-check of `0860a32..2a5865b` raised one blocker (docs named the older bundle - fixed here) and two non-blocking notes: a rerun in the same workdir after a failure can spend more of the durable
  3-generation budget (now documented), and the OOM message says "CUDA" for any memory error (left as is; wording only).

## Dual-T4 preparation (uncommitted -> committed in the next checkpoint)
- Staged dual-worker orchestration (`ltx_first_test.sh` STAGE=gpu0|gpu1|concurrent|retry), `host_check.py`, `gpu_attribution.py`, `concurrent_check.py`, per-card VRAM selection (`GRANTHSTUDIO_GPU_INDEX`), variant-b shot, controlled retry test; notebook gains `STAGE`.
- Windows suite: 439 tests, all passing after an autouse fixture stopped `GRANTHSTUDIO_GPU_INDEX` leaking between tests. No weights downloaded, no Kaggle kernel pushed.
- Blocked on a human: a named approver for `LTX_DOWNLOAD_APPROVED` / manifest section E (licence acceptance). Mini-film stages additionally need research approval, canon/style approval and model choices (O-006/O-007, voice consent): all NOT VALIDATED.

## Codex dual-T4 review (docs/evidence/codex_reviews/05_dual_t4_review.md): FAIL, all four findings fixed
1. BLOCKER retry lost the completed task (random port is part of task identity): ports are now chosen once per workspace (`ltx_ports.env`) and reused, still re-verified free each stage.
2. MAJOR failed isolation stage unlocked later stages: stages unlock only through `ltx_evidence_<stage>/stage_verdict.json`, written after client PASS + attribution (+ concurrent check), bound to the receipt sha256 and commit.
3. MAJOR concurrent overlap used scheduler windows: now ComfyUI's own execution_start/execution_success timestamps (receipt `comfy_execution`); missing -> refusal.
4. MAJOR missing process telemetry weakened attribution: sampler writes #OK/#FAIL markers; no successful sample or any failure -> problem; the memory-only fallback also needs verified per-worker isolation evidence (`worker_evidence.json`).

Codex re-review (06_dual_t4_rereview.md): no blocking issue; one MINOR (stale telemetry across reruns) fixed by truncating traces per invocation.

## First Kaggle dual-T4 attempt (2026-10-23, kernel sangeetasangamkar/granthstudio-ltx-dual-t4 v1, bundle tip 9755413): REFUSED before any download
- The script refused at step 0: `/kaggle/working` has only 20 GB free (need 40). Nothing was cloned or downloaded; no GPU work ran. Log: docs/evidence/kaggle_dual_t4/gpu0_attempt1_refused_disk.txt.
- Fix: the heavy workspace now lives on `/kaggle/temp/ltx` (notebook `TMP`); only the small evidence is published to `/kaggle/working` (`EVIDENCE_DEST`, `publish()` also runs on early refusal).

## Kaggle dual-T4 attempt 2 (kernel granthstudio-ltx-dual-t4 v2, pinned 30f6277): refused at worker start, safely
- Host check passed (2x Tesla T4, torch 2.11.0+cu128, 30.7 GB RAM). Both weights downloaded and the full SHA-256 of each verified OK (ltxv-2b-0.9.8-distilled 6047 MB, t5xxl_fp16 9334 MB). ComfyUI started on its random port.
- Refused: `pid 302 does NOT own a listener on port 59039`. Cause: `$!` was the launching subshell, not the python process. The /proc ownership proof did its job; no inference ran, no GPU memory was used.
- Fix: launch the worker with `exec` so the recorded pid is the ComfyUI process. Log: docs/evidence/kaggle_dual_t4/gpu0_attempt2_pid_proof_refused.txt. ComfyUI also logged a non-fatal sqlite "unable to open database file" warning (user-directory DB), noted, not acted on.

## Kaggle dual-T4 attempt 3 (v3, pinned df6d018): worker proof PASSED, refused at live compatibility (step 7), no inference
- Host: GPU 0 `GPU-65b27b0f…`, GPU 1 `GPU-72251c6c…` (Tesla T4, 15360 MiB, idle), torch 2.11.0+cu128. Both weights re-downloaded and SHA-256 OK.
- Worker 0: `pid 303 owns a listener on port 55325`; ComfyUI reported exactly one device, `cuda:0 Tesla T4 : cudaMallocAsync`, matching physical GPU 0. (The exec fix worked.)
- Refused: `ConversionError: node 103 VHS_VideoCombine: 5 unexplained widget value(s)`. Cause: the REAL official workflow file (blob 2260170f, verified) stores VideoHelperSuite widgets as `{name: value}`; our committed positional "ui_inventory" had hidden that. The converter correctly aborted rather than guess.
- Fix: converter accepts name-keyed widget values (unknown keys refused; only `videopreview` is UI-only). Checked offline against the real official file + the live /object_info from this very Kaggle server: rebuilt graph is IDENTICAL to the committed candidate. New regression test in tests/test_ui_to_api.py. Log: docs/evidence/kaggle_dual_t4/gpu0_attempt3_converter_refused.txt. Still no inference, no VRAM used.

## Frozen provisional style (owner decision 2026-10-23)
- `canon/style.yaml` (`devotional_gouache_1950s_v1`, v1, frozen, sealed) + `src/granthstudio/style.py`; keyframes compose prefix + scene + suffix; id and sha256 in requests, metrics, task inputs, snapshot; conflicting registry style, unsealed edit or request built under another style are refused. `tests/test_style.py` (8 tests).
- No `runner.py` exists in this repo; wired into keyframes.py/pipeline.py instead. Characters still provisional; SDXL checkpoint and identity conditioning still undecided, SDXL NOT VALIDATED.

## Kaggle dual-T4 attempt 4 (v4, pinned fce4e21): FIRST REAL LTX GENERATION ON GPU 0; harness verdict NOT_VALIDATED (post-run check bug), not PASS
Evidence: docs/evidence/kaggle_dual_t4/gpu0_attempt4/ (receipt, attribution, journal, traces, ComfyUI log, the clip and its last frame image).
- Host: GPU 0 `GPU-5ee11fb5-a8f7-865d-c5ae-b9f0539cfee1`, GPU 1 `GPU-7e55ff31…`, both Tesla T4 15360 MiB idle at start; torch 2.11.0+cu128; ComfyUI 0.3.47 (pinned commit); worker 0 pid 303 owned its listener; ComfyUI saw exactly one device `cuda:0 Tesla T4 : cudaMallocAsync`.
- Live compatibility: rebuilt API workflow from the official file + live /object_info is IDENTICAL to the committed candidate (0.9.6 -> 0.9.8 checkpoint override recorded).
- Precision as logged by ComfyUI: diffusion model `torch.float32` (manual cast none), VAE `torch.float32`, text encoder `torch.float16`; LTXV loaded completely (7.3 GB), VideoVAE 4.8 GB, T5 9.1 GB (offloaded between stages). Matches the source-derived expectation (T4 has no native bf16).
- Prompt executed in 114.28 s (8 steps, ~3.44 s/it). Scheduler wall clock 345 s (cold model loading from disk before the first VRAM rise at 05:29:21). Sampled peak memory.used on GPU 0: 14 873 MiB (lower bound of the true peak; allocator-cached). GPU 1 stayed at 0 MiB with no compute app: attribution ok (pid 303 only on GPU 0).
- Output: `granthstudio_ltx_i2v_00001.mp4`, h264, 768x512, 49 frames, 24 fps, 2.04 s; journal state `completed`, one submission (attempt 1, seed 1732128765, noise_seed on the sampler path).
- Why NOT_VALIDATED: after the run the scheduler repeated the PRE-run preflight, which includes `free_vram >= 10000`; ComfyUI still held ~14.8 GB, so the finished render was discarded as "GPU preflight not passed: free_vram". Fix: `Task.postflight` (state checks without the free-VRAM gate) for LTX and SDXL tasks; regression test reproduces the bug and the fix. No clip decoding was performed by the harness for this attempt, so nothing here is a PASS. Capability stays NOT VALIDATED; a human has not reviewed the clip.
- Also seen: ComfyUI logged a non-fatal sqlite "unable to open database file" warning (user DB), no effect on the run.

- CPU suite at this checkpoint: 457 passed, 4 skipped (Windows, 617 s); `granthstudio validate` clean.

## Codex review 09 (90c59cd..56a6fd9, docs/evidence/codex_reviews/09_postrun_style_review.md): FAIL, three defects fixed in f78d051
1. HIGH style change escaped require_current (both snapshots reloaded the live style): the bundle now captures the style identity at load (`Bundle.style`) and snapshots compare that. Test: tests/test_style.py.
2. MEDIUM reference-sheet SDXL tasks had no postflight: added (state checks, no resource gate).
3. MEDIUM resume/fallback: `Scheduler.run/status` do the state check (postflight or preflight) first, the resource preflight only before NEW execution; the CPU fallback seal uses the state check. Tests in tests/test_ltx_first_test.py.
Codex also said: safe for a fresh gpu0 execution; offline validation of attempt 4 is possible without regeneration; the earlier "457 passed" line had no candidate-bound JUnit. Candidate-bound JUnit is now saved in docs/evidence/cpu_tests/.

## Attempt 4 retrospective OFFLINE validation (separate record; the original NOT_VALIDATED verdict is unchanged)
`scripts/kaggle/offline_validate_gpu_evidence.py` (tests: tests/test_offline_validator.py) -> docs/evidence/kaggle_dual_t4/gpu0_attempt4/retrospective_offline_validation.json, hash-bound to the clip, receipt, journal and attribution file.
- Confirmed offline: decodes cleanly; h264 768x512, 49 frames, 24 fps, 2.04 s; one completed submission with the sampler seed on the generation path; GPU 0 did the work, GPU 1 untouched.
- NOT ok: the picture jumps between frame 0 and frame 1 (mean luma step 90 on a 0-255 scale). Frame 0 is the synthetic colour-bar start image; frames 1-48 are a different, text-like "TV collage" that never returns to the start image (frames_0_12_24_36_48.png). So the model ran, but the clip does NOT animate the start image: a visual/semantic problem that numeric checks cannot excuse. Possible causes to investigate before any claim (not yet tested): an out-of-distribution synthetic start image, the image-conditioning strength/wiring of the converted workflow, the motion prompt, fp32 path on T4. Needs human review; LTX I2V is not validated and this is evidence against calling it so.

- Candidate-bound CPU evidence: docs/evidence/cpu_tests/f78d051_suite.xml = full suite on commit f78d051 (466 tests, 0 failures, 0 errors, 4 skipped, 629 s). Later commits add only the offline validator, its tests and docs.
- Likely cause of the attempt-4 drift, read offline from the executed prompt in the ComfyUI PNG: the positive prompt was only "slight head turn" on a synthetic colour-bar start image; the graph wiring (LoadImage -> LTXVPreprocess -> LTXVImgToVideo strength 1.0 -> sampler latent) matches the official workflow. Hypothesis only, untested: next gpu0 run = one painted start image with a descriptive caption prompt, everything else unchanged.

## Codex re-check 10 (docs/evidence/codex_reviews/10_review09_fixes_recheck.md): runtime fixes CLOSED; two validator defects (output path aliasing an input, basename-keyed hashes) fixed; "no blocking issue remains for a fresh isolated gpu0 test"

## Painted-image gpu0 test: harness support (this checkpoint)
- Input: image 4 of the owner's four Gemini "Nano Banana" storyboard paintings. The owner-named `04_ltx_start_768x512.png` was not received; `assets/ltx_test_inputs/painted_courtyard_01/04_ltx_start_768x512.png` (sha256 775b9805424c5c7987ea0041d3c2b3dd5d3103defb6ce5eedfe2f9cbc75bdf83) is a lanczos rescale of the received `04_source_1024x687.webp` (sha256 c121173dba081270a5efd973cebe9c1b85a5b3327566147a25bcfcd5da7301a8). Prompt and negative prompt are the owner's texts verbatim.
- `scripts/ltx_first_test.py --start-image --prompt-file [--negative-prompt-file]` replaces ONLY the start image and its descriptive text (workflow, 768x512, 49 frames, 24 fps, seed 1732128765, strength 1.0, cfg 1 unchanged). The negative text is recorded but NOT applied (the workflow runs CFGGuider at cfg 1, where negative conditioning has no effect). The frozen style identity enters task identities/receipts; the style prefix/suffix are not added to this prompt, which already carries the style wording.
- Every LTX test now exports frames 0, 1, 12, 24, 36, 48, a contact sheet and SSIM-to-frame-0 / luma-step numbers; for a supplied painting, suspected drift makes the verdict FAIL (a screen for the human, never an acceptance; `human_visual_review` stays NOT_DONE). Shell: `PAINTED_INPUT` (notebook parameter) checked before any network step, gpu0/retry only; previews and the start image are copied into the evidence.
- .gitignore exceptions so the small evidence clips/frames and the painted input live in the git bundle.

## Codex review 11 (painted-input delta, docs/evidence/codex_reviews/11_painted_input_review.md): not cleared; 3 major + 3 minor fixed
- Suite at b6572da: 473 passed, 4 skipped (docs/evidence/cpu_tests/b6572da_suite.xml).
- MAJOR reused workdirs recorded inputs that were never used: now refused unless the project holds the supplied image, prompt and current style (NOT_RUN). MAJOR painted retry skipped diagnostics: retry now writes `preview_retry/` and is screened. MAJOR input similarity never entered the screen: frame 0 vs the supplied image (SSIM >= 0.50, and measurable) is now part of drift_suspected.
- MINOR "verbatim" -> documented whitespace strip; .gitignore exceptions narrowed to the named files; validator output also refused when hard-linked to an input.

## Codex re-check 12 (docs/evidence/codex_reviews/12_review11_recheck.md): no blocking issue; a fresh painted gpu0 run may proceed. One minor (.gitignore exceptions by file name) fixed here.
- Candidate-bound suite: docs/evidence/cpu_tests/55ca9f1_suite.xml = full suite on 55ca9f1, 481 tests, 0 failures, 0 errors, 4 skipped (649 s). This checkpoint commit adds only that evidence, the review file and the .gitignore tightening.

## Painted gpu0 attempt 5 (kernel v5, pinned d6b9c6f): harness FAIL kept; scheduler complete (post-run fix confirmed on hardware)
Evidence: docs/evidence/kaggle_dual_t4/gpu0_attempt5_painted/ (REPORT.md, receipt, journal, attribution, traces, clip, contact sheet, frames 0/48, camera_analysis/). The drift screen failed (SSIM vs frame 0 0.58 -> 0.17); the offline camera-motion analysis is INCONCLUSIVE by preset thresholds, but synthetic calibration and the aligned examples show the raw collapse is what a ~1.04x-1.2x push-in produces, with the scene preserved and part of the difference not explained by camera motion. The prompt asked for a stationary camera; LTX pushed in.
Next experiment (not yet run, needs explicit pin authorization): assets/ltx_test_inputs/painted_courtyard_01/prompt_camera_lock.txt (owner's camera-lock prompt, 195 words; the pinned ComfyUI LTXV tokenizer has max_length 99999999, so nothing is truncated), PAINTED_PROMPT=prompt_camera_lock.txt; everything else identical.

## Codex review 13 (camera-lock preparation): not cleared; 2 major + 3 minor fixed
- MAJOR masked SSIM (black corners after warping lowered the compensated score): now averaged only where the whole SSIM window is covered; analysis evidence regenerated (attempt 5 compensated 0.42; unreliable 0.32/0.28/0.23; pure-zoom calibration 0.93-0.95). MAJOR a failed v2-branch JUnit (style_v2_suite.xml, from branch style-v2-proposal) had leaked into this branch: removed (kept outside the repo). Candidate-bound passing evidence: docs/evidence/cpu_tests/camera_lock_suite.xml (478 passed, 4 skipped on 18a984a) and the suite for the final candidate below.
- MINOR REPORT wording qualified (reading, not proven cause), control JSON and threshold provenance attached; extraction retries require a successful fresh output (stale previews removed); `--json` of the camera tool refuses anything but its own earlier report.

## Review 14 (re-check of review 13): no blocker or major; one minor (SSIM on a crop narrower than its window) fixed.
- The first final-candidate suite run (23c6806) showed 14 failures, ALL "GPU preflight not passed: disk fail" and downstream: the PC's C: drive was full (3.3 MB free), not a code defect. After freeing the pytest scratch directory the affected files pass; the final suite is rerun with its temp directory on D:. The failed JUnit from that run is not claimed as evidence.
- Root cause of the two intermittent painted-test failures (test_the_painted_retry..., test_a_supplied_painting...): the test fixture built the start image and the server clip from two separate runs of ffmpeg's `gradients` source, which is NOT reproducible (same seed, different bytes), so frame 0 vs the input SSIM sometimes fell below 0.5 and the drift screen correctly said "suspected". The clip is now derived from the still itself (8/8 stable). The e2e6c23 JUnit with that failure is not kept as evidence.

## Final candidate CPU evidence: docs/evidence/cpu_tests/final_candidate_6efb017.xml = full suite on 6efb017, 484 tests, 0 failures, 0 errors, 4 skipped (636 s). The commit that adds this file changes no code.

## Phase 1 camera-lock gpu0 run (kernel v6, pinned 840dd6a, bundle 068b32fd): ONE run, harness FAIL, prompt-only camera control failed this comparison
Evidence docs/evidence/kaggle_dual_t4/gpu0_attempt6_camera_lock/ (REPORT.md, receipt, clip, frames 0/1/12/24/36/48, contact sheet, camera analysis, calibration, control, telemetry). Attempt 5's FAIL evidence untouched. Stopped as instructed: no gpu1, no concurrency, no further prompt rewrites, style v2 untouched.

## 45-second pilot, Phase A: capability audit written (docs/PILOT_45S_READINESS.md). Blockers B1 source approval, B2 SDXL stack, B3 audio stack, B4 lip-sync, B5 depiction of Gajanan Maharaj, B6 full C: drive. Nothing implemented yet; waiting for decisions.

## 45-second pilot, first action (decisions A-G received): storage assessed (docs/pilot/STORAGE_READINESS.md, nothing deleted), exact ovi 84-121 text transcribed from the printed page images with a three-scene breakdown and a narration proposal (docs/pilot/OVI_84_121_TRANSCRIPTION_AND_SCENES.md, awaiting proofreading and approval by Satvik Sangamkar; the print drops the hundreds digit after ovi 100), model/dependency manifest with verified revisions, sizes and hashes (docs/pilot/MODEL_AND_DEPENDENCY_MANIFEST.md, nothing downloaded, no licence accepted). No source approval, no model execution.

## Pilot blocker decisions received: scoped cleanup done (C: free 0.195 -> 4.081 GB; npm cache kept because the Desktop Commander MCP server runs from it), source-approval sheet prepared and UNSIGNED (docs/pilot/SOURCE_APPROVAL_SHEET.md; ovi 113 speaker left UNRESOLVED with the printed-page evidence image), SDXL pins + 12-node candidate workflow + static tests prepared (config/pilot_sdxl_pins.yaml, workflows/comfyui/sdxl_ipadapter_keyframe.candidate.json, tests/test_sdxl_candidate.py), audio dependency probe and test plans written (docs/pilot/SDXL_AND_AUDIO_TEST_PLANS.md). Nothing downloaded, nothing approved, no GPU used.
