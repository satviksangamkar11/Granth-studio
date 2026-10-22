# Implementation contract after the CPU audit corrections

Authority: `ARCHITECTURE_V3_1.md` remains frozen. The layout and original CLI decisions
remain in `SPEC_SECTIONS_11_12_14.md`. This file describes enforcement corrections;
it does not approve research, checkpoints, visual style or production.

## Research and compilation

`research.yaml` preserves `overview`, structured scenes, source references, actions,
visual details, continuity, objects, time/season, uncertain words, corrections,
clarifications and cross-chapter links. Each scene requires a description, location,
cast, dialogue, and actions/visual_details/continuity arrays (empty where appropriate).
Facts have `id`, `text`, `source_refs`, and `artistic`; non-artistic facts need sources.
This is a curated machine-readable export, not autonomous story generation.

Every approved research scene and dialogue line must appear once, in approved order.
Shots reference approved `action_ids`; all non-artistic actions require coverage.
Motion text is derived from those approved action records. Conflicting free-form motion
text or invented action IDs are rejected; this is a provenance check, not visual proof.
Manifest location, cast and props must match that research. Scenes keep their IDs;
episode IDs must match the chapter. Compiled shots retain source facts, canon IDs,
lighting, artistic flags and approved coverage instructions. Canon includes a global
props registry as well as characters, locations and protected terminology. Global
style generation/reference sheets remain unimplemented and gated.

## Hindi and speech review

Hindi alignment requires `reviewed: true` and `verification` with a nonblank `reviewer`
and `mr_sha256`/`hi_sha256`. Those hashes use `sha256_obj(normalize_text(text))`.
Changing either text invalidates that record. This records human semantic review;
it does not claim that lexical checks prove correct translation. IndicTrans2 is absent.

IndicF5 generation remains a refusal stub. CPU integration can import reviewed audio
through each timeline entry's `audio` object: `path`, `sha256`, `language`, `speaker`,
`text_sha256`, `speech_reviewed_by`. Paths are relative to `artifacts/audio/`.
Text hashes use the same normalized-text convention. No review is created automatically.
Files are hashed, decoded and measured; declared duration is never trusted as a clock.
Audio tasks preserve per-utterance files and measured metadata in `timings.json`.
Speech review is an external human check; automated ASR is not integrated.

## Editorial timing and validation

Each language gets an edit plan driven by measured utterances. The complete primary
action is preserved at natural speed. Extra duration requires shot `coverage`:
`{mode: hold_final_frame, reviewed_by: <human>}`. Holds extend the last frame and never
repeat the action. Silent shots and trailing silent coverage are represented explicitly.
Subtitles use actual utterance placement. Final video and audio must cover the same edit;
assembly refuses mismatched lengths and never uses `-shortest`.

Media validation reads streams and executes a bounded FFmpeg decode, requiring audio
for final releases. FFmpeg and ffprobe calls use a 300-second per-call timeout. A timeout
fails the task and incomplete work is discarded. Larger production encodes may require
an explicitly validated timeout policy; none is inferred from small CPU tests.

## Recovery and invalidation

Task IDs include dependency IDs. Receipts bind current inputs, workflow version,
dependencies, dependency output hashes and output hashes. Relevant source-scene/canon
facts enter visual-task fingerprints; language-only edits leave shared visuals reusable.
Model/runtime and workflow changes invalidate affected motion and downstream assembly.
Preflight checks run before reuse; output validators run on both fresh and resumed tasks.
Final QA compares current inputs against the execution snapshot, including approvals,
canon, manifests, timelines and model configuration. Old receipt formats are invalidated.

ComfyUI intent and prompt IDs live under `tasks/.../pending/` outside temporary work.
Restart resumes polling the known prompt. A lost POST response leaves an ambiguous
submission journal and blocks another POST until an operator reconciles it. A polling
timeout is pending work, not evidence of server cancellation. Terminal server errors may
be retried. Only a designated `_output_node` with exactly one MP4 is accepted.

## Runtime gate (not runtime validation)

Validated API graphs require `_output_node`, node `class_type` and `inputs`; placeholders
preserve numeric types. `ltx.runtime` records files for `checkpoint`, `vae`, `text_encoder`
(absolute runtime path and SHA-256), exact ComfyUI and node-pack commits, T4, FP16,
width and height. The checkpoint hash must match the top-level model pin.

Each passing benchmark receipt must match capability, current workflow hash and
`runtime_sha256 = sha256_obj({runtime, frame_counts, family, version, variant})`, with
positive GPU time/video duration/VRAM and an output hash. Files are checked before use.
This enforces recorded evidence; actual model loading, precision and compatibility
remain NOT VALIDATED until executed on the approved runtime. I2V and FLF stay separate.

## Release authorization

Technical completion is distinct from `released`. Production needs an existing human
approval at `approvals/adhyay_NN.json`; the runner never writes that approval. Exact keys:
`schema_version` (1), `adhyay`, `approved` (true), `reviewed_by`, `input_sha256`,
`pilot_plan`, `pilot_receipts`, `recovery_evidence`, `minimum_accepted_sec_per_gpu_hour`,
`flf_decision` (`go` or `no_go`). `input_sha256` is the hash of `pipeline.snapshot(bundle)`.
Evidence references are `{path, sha256}` relative to `benchmarks/`.

`pilot_plan` pins the compiled Adhyay 1 pilot. B/C compare the same scene/start visual/
characters; E changes lighting for a recurring character; D includes dialogue.
Six receipts must match labels A-F, their capabilities, and `pilot_plan_sha256`.
Accepted I2V/FLF receipts must match current validated runtime/workflow pins. The human
must supply a positive throughput acceptance budget and reviewed recovery evidence.
With FLF GO, C must pass. With FLF NO-GO, C must be recorded rejected/failed, FLF disabled,
and production must contain no Tier 2 shots. Failed/retry GPU time still counts.

No actual approval, acceptance budget or model validation was supplied by these fixes.
Current model generation and real production remain gated.


## Claude audit corrections D1-D7 (2026-10-22)

- HTTP 4xx is a definitive ComfyUI rejection (`TaskFailed`) and leaves a retryable failed
  journal. Transport errors, timeouts and HTTP 5xx retain ambiguous submission handling.
- SRT overlap comparison permits only 1e-9 seconds of arithmetic noise, clamped forward;
  genuine overlaps remain blocked and timestamps retain millisecond rounding.
- The approved pilot-plan file must equal the current compiled Adhyay 1 manifest, not
  merely carry a valid self-hash. For another production chapter, the current approved
  Adhyay 1 inputs are reloaded/compiled. Changed A-F assignments invalidate approval.
- Recovery evidence now follows `recovery_evidence.schema.json`: `schema_version: 1`,
  `passed: true`, nonblank `reviewed_by`, `pilot_plan_sha256`, `clean_outputs`, and
  `resumed_outputs`. Each output map requires `mr_video` and `hi_video`; additional
  outputs may be included but the sets must match. Values are `{path, sha256}`, with paths
  relative to the configured artifacts directory. Every file is rehashed; corresponding
  clean/resumed hashes must match. A pass flag alone or stale/missing output is refused.
- Recovery outputs must be sealed scheduler outputs (`<store>/<stage>/<task_id>/<file>`
  under artifacts): listed with the same hash in a valid, complete `task_receipt.json`;
  `mr_video`/`hi_video` must be the `assemble_mr`/`assemble_hi` releases. All clean
  records share one store and all resumed records another; matching outputs must have the
  same task id. The resumed store's `run_log.jsonl` must record a `resumed` task and the
  clean store's must not. No two records may be the same file (path, case or hard link).
- `GateFailure` fails immediately, without rendering retries or a NOT VALIDATED label.
- AV checks prefer `duration_ts * time_base` (then stream duration) over rounded container
  duration. Synchronization tolerance is two audio samples; missing stream timing/rate
  falls back to a 2 ms metadata allowance. This replaces the blanket 1/24-second margin.
  No `-shortest` or speech trimming is introduced. Coverage extensions still need review,
  and primary actions cannot be shortened by a frame-sized tolerance.
- Coverage reviewers must contain a non-whitespace character.
- A Windows junction escape is tested independently of the existing symlink test.

These are CPU-tested enforcement corrections. Real GPU, ComfyUI/model execution,
historical/semantic correctness, research approval and production GO remain deferred.


## Remaining-pipeline contracts (sprint after the H1/M1/L1/R1 round)

- **Runner contract.** Translation, speech, ASR and diagnostics are argv lists in `models.yaml` (no shell) that read
  one JSON object on stdin and print one JSON object on stdout. A section is used only when `status: validated`
  with `command`, `model` and `revision` set; otherwise exit 3 NOT VALIDATED (O-007). Payloads: translation
  `{src_lang, tgt_lang, texts}` -> `{translations}`; speech `{text, language, reference_audio, reference_transcript,
  out_path, ...}` -> writes `out_path`; ASR `{audio_path, language}` -> `{text}`; diagnostics `{metric,
  media_path, reference_paths}` -> `{value}`.
- **Translation.** Candidates live in `translation_candidates.json` bound to the Marathi text hash. Approval writes
  one `hi.yaml` line after `hindi_line_problems` (numeric facts, protected terms) passes, with the reviewer and the
  exact Marathi and Hindi hashes and an `alignment.source` (`model_candidate` or `human_text`).
- **Voices and speech.** A voice needs `consent` (basis, granted_by, document_ref, recorded_at) and a hashed
  reference. Candidates are bound to the request hash; approval requires the script text hash to be unchanged and
  writes the timeline `audio` block with `provenance` (voice, model, revision, request, optional ASR report hash).
  `assemble_*` outputs include `provenance.json` tying video, subtitle and voice hashes to per-line sources.
- **Visual canon.** Requests contain only approved research facts, canon names and human-written designs. A
  keyframe is usable only when an approved asset exists for the exact current request hash (`approved_keyframe`).
  SDXL runs only with status validated, a pinned and locally verified checkpoint, a decided identity method and a
  validated workflow (O-006).
- **Benchmark mode.** `load_bundle(..., benchmark=True)` is used only by `pilot` commands. It keeps pins, runtime
  file hashes, the checkpoint-binding check and a real `_output_node`, and waives only the capability `validated`
  status, the passing-receipt requirement and the workflow `_status`. Without it the pilot could never produce the
  evidence that validates LTX. Strict mode is unchanged and is what production approval uses.
- **Receipt accounting (D-004).** `gpu_seconds_total` is the wall-clock sum of every logged attempt of the task across
  sessions, failed attempts included, one GPU; it is an estimate, not utilisation. `peak_vram_mb` is the highest
  `nvidia-smi` sample at poll time, a lower bound. Tier 0 and assembly use no GPU. Shot F (assembly) reports
  `video_seconds` 0 because edits re-use footage counted once; the user may change that (O-004).
- **Review binding.** A review stores the digest of the measured fields it saw; receipts take `accepted`/`outcome`
  only from a review whose digest still matches. Criteria come from `config/pilot.yaml` (O-005).
