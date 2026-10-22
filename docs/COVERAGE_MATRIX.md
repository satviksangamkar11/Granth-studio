# Architecture coverage after CPU audit corrections

Statuses: IMPLEMENTED = executable CPU behavior with regression evidence; PARTIAL =
some requirements remain; STUB = deliberate refusal; NOT VALIDATED = external runtime
evidence absent; MISSING = no implementation. CPU evidence is synthetic, not production.

- Sections 1 / 2A: PARTIAL overall. Chapter/episode IDs, complete research coverage,
  approved order and provenance contracts implemented. Curated research for production
  is not supplied or approved. Full 21 episodes / 42 releases are not produced.
- Section 2B / 4.2: IMPLEMENTED registry/reference/identity checks for global characters,
  locations, props and terminology. Semantic identity and visual continuity NOT VALIDATED.
- Sections 2C / 10: IMPLEMENTED CPU bilingual edit assembly with shared motion masters,
  measured audio, reviewed final-frame holds and independent MR/HI durations/subtitles.
  Real speech and rendered series content NOT VALIDATED.
- Section 2D: IMPLEMENTED YAML/JSON/filesystem design; no DB or agent framework added.
- Section 2E / 15: IMPLEMENTED receipt arithmetic, structural A-F checks, runtime pin
  binding, explicit FLF decision and production authorization checks. Actual pilot,
  numerical acceptance decisions and GPU performance NOT VALIDATED / not supplied.
- Section 3 / 8: IMPLEMENTED sequential stage-batch planning, dependencies and receipts, plus the
  Kaggle runtime layer: GPU/VRAM/RAM/disk/session/package-pin preflight (nvidia-smi), pinned weight
  fetch with SHA-256 verification, explicit `local_dir` durable storage with hash-manifest export and
  restore, session-deadline stop that defers unstarted tasks, schema-valid run receipts, pin-only
  bootstrap plan. Single GPU only: dual-T4 execution is refused (gate disabled). All of it is
  NOT VALIDATED on a real Kaggle host; no storage provider is chosen (O-008) and every minimum in
  `config/runtime.yaml` is unset until measured.
- Section 4.1: IMPLEMENTED curated research contract, approval/version/hash checks,
  completeness and provenance preservation, and a Markdown importer (`research import`,
  `check-draft`, `promote`). The importer writes an unloadable `research.draft.yaml`: it never fills
  dialogue text (the Markdown only has paraphrases and verse fragments), location or the artistic
  flag where the source gives no reference, never marks a question answered, never merges
  identities, and never approves. It reproduces exactly the 104 open and 75 provisional items of
  the FINAL question file. Exact Marathi text, locations and cast must be entered by a human.
- Sections 4.3 / 4.4: IMPLEMENTED global visual registry (`canon/visual_assets.yaml`: versioned art
  direction, human-written design prompts, immutable hashed reference assets), reference-sheet
  requests derived from an approved front master, generated-asset collection and hash-bound human
  approval. Generation is NOT VALIDATED: no SDXL checkpoint, identity-conditioning method or style is
  chosen (O-006), so every sheet and keyframe job refuses.
- Section 5.1: IMPLEMENTED normalized approved Marathi text lock and scene/dialogue order.
- Section 5.2: IMPLEMENTED IndicTrans2 runner contract, stored candidates, deterministic
  numeric-fact and protected-term checks, and hash-bound named human approval into `hi.yaml`. The
  IndicTrans2 model is NOT VALIDATED (O-007) and automatic semantic comparison is MISSING; the
  report marks it `not_computed`. Approval is never inferred from term or number matches.
- Section 5.3: IMPLEMENTED IndicF5 runner contract, voice registry that requires a licence or consent
  record per speaker and language, speech candidates, and a listening approval bound to the audio hash
  and script text. IndicF5 itself, voice licences and real pronunciation are NOT VALIDATED (O-007).
- Section 5.4: IMPLEMENTED decoding/measuring imported or generated audio, measured placement, SRT, ASR
  runner contract and word-level comparison reports (diagnostic only, never approves or blocks). No ASR
  model is chosen: NOT VALIDATED. Validated word alignment is MISSING.
- Section 6: IMPLEMENTED SDXL adapter through ComfyUI, deterministic keyframe requests bound to
  approved references and style, identity-conditioning interface (`reference_slots`), approved-keyframe
  resolution for downstream shots. NOT VALIDATED: the stub workflow, checkpoint and conditioning method
  are unselected, and distributed input transfer is unproven.
- Section 7 Tier 0: IMPLEMENTED bounded CPU FFmpeg still animation.
- Section 7 Tier 1 / Tier 2: IMPLEMENTED adapter with graph/runtime gates, checkpoint-binding check (rejects other LTX
  families), `/object_info` node checks, token-tagged submissions with `comfy reconcile` and `cancel`,
  input validation interface, per-clip metrics, and a benchmark mode for the pilot. Shipped workflows
  remain STUBS: the 0.9.8 graph, frame rule (O-003), VAE and node interface are not invented. T4 LTX
  I2V and FLF NOT VALIDATED.
- Section 7 frame rules: IMPLEMENTED pinned-list validation; actual frame/resolution rules
  remain NOT VALIDATED against the real model/workflow.
- Section 9: IMPLEMENTED current-input/dependency/output checks, atomic task receipts,
  bounded retries, process-interruption recovery, actual media decode, script metadata
  checks and snapshot-bound QA. ComfyUI recovery tested with a fake backend only.
  Durable external Kaggle storage and real speech/visual quality NOT VALIDATED.
- Section 9 diagnostics: IMPLEMENTED FFmpeg-measured colour statistics, an edge-density proxy and frame-to-frame
  difference, logged and never enforced; an optional model runner for face embedding, CLIP style,
  anachronism and object presence reports `not_computed` until a human validates one. No threshold
  is calibrated or imposed.
- Sections 11 / 12 / 14: IMPLEMENTED CPU layout/contracts/CLI; details in
  `IMPLEMENTATION_SPEC.md`. Model commands still expose explicit STUB/NOT VALIDATED stages.
- Section 13: PARTIAL stack. Runtime dependencies are unchanged (pyyaml, jsonschema). Model stacks run as
  external commands behind a JSON-over-stdio contract; the IndicTrans2 and IndicF5 reference runners in
  `scripts/runners/` were written from published usage and have never been executed.
- Section 16: IMPLEMENTED relevant task invalidation, independent language changes,
  current snapshot checks and separate technical/authorized release status. Acceptance
  evidence must be supplied by people and the real runtime.
- Section 17: Frozen document and checksum preserved; open model/style decisions unchanged.
- Section 18: IMPLEMENTED pilot orchestration (`pilot run|receipts|review|report|recovery-evidence`) with
  benchmark mode, receipts built from run data, a user-defined review rubric (O-005) and an evidence
  report that separates measured, estimated, not_computed and unvalidated values. The actual Kaggle
  pilot is NOT VALIDATED / not run; production is not authorized.
## Verification

See `benchmarks/cpu_review_fixes.xml` and `benchmarks/cpu_review_fixes_receipt.json`.
All research, names, review records, tones and model pins in tests are synthetic.
No claim of completed GPU/model/semantic production validation follows from CPU passes.


## Follow-up D1-D7 verification

Definitive HTTP rejection/retry handling, SRT arithmetic tolerance, current pilot-plan
binding, actual clean/resumed recovery hashes, immediate gate failure, measured AV
synchronization and nonblank coverage reviewers are IMPLEMENTED with CPU regressions.
Windows junction containment has a dedicated test; unsupported symlink hosts still skip
only the separate symlink test. External runtime/semantic/production status is unchanged.
Evidence: `benchmarks/claude_d_receipt.json` and its focused/full JUnit receipts.


## Follow-up sprint (Phases A-F), CPU evidence only

Everything above marked IMPLEMENTED for runtime, model, pilot and importer work is verified against
synthetic fixtures, fake local servers (ComfyUI) and fake subprocess runners. None of it shows that a
real GPU, checkpoint, workflow, translation, voice or ASR model works. Evidence: `benchmarks/sprint_cpu.xml`.
Remaining hardware-dependent work is listed in `PROGRESS.md`.
