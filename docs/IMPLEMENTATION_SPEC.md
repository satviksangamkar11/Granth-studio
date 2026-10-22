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
