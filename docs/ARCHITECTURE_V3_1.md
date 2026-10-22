# GranthStudio Zero-DB v3.1 — Frozen Architecture

Project: Shri Gajanan Maharaj Vijay Granth AI Series  
Scope: 21 adhyays → 21 episodes → 42 Marathi/Hindi video releases  
Target compute: Kaggle Dual NVIDIA T4 GPUs (2 × 16 GB VRAM)  
Core infrastructure: Python + YAML/JSON + ComfyUI + FFmpeg  
Status: CORE FROZEN; video-model performance subject to benchmark gates  
Freeze date: 2026-10-22 (Asia/Calcutta)  
Project root: `D:\aai work`

This is the approved architectural baseline supplied by the user. Freezing the
plan does not claim that implementation, research approval, model validation,
Kaggle benchmarking, or production rendering has been completed. Existing
chapter research remains separate and is not approved or modified by this freeze.

## 1. Project objective

Produce a visually consistent, historically and spiritually respectful adaptation
of Shri Gajanan Maharaj Vijay Granth. Each adhyay becomes one complete episode:

- Original Marathi dialogue and narration.
- Meaning-preserving Hindi adaptation.
- Consistent recurring character designs and voices.
- Consistent locations, attire, objects, artistic style, and continuity.
- Shared visual assets between languages.
- Automated rendering, technical checks, and final assembly.
- Recoverable production runs using free or near-zero-cost compute resources.

The user's primary responsibility is reviewing and correcting research files.
Routine storyboard, image, video, and audio generation runs automatically after
source approval. Do not build a creative screenplay-generation system: researched
chapter narratives, scene breakdowns, characters, and dialogue already exist.
Episode duration follows the approved script and editorial pacing; there is no
fixed five-second shot requirement or arbitrary ten-minute episode limit.

## 2. Non-negotiable principles

### A. Sacred source integrity

Approved Marathi source text and researched facts are immutable production inputs.
The system must not silently invent miracles, dialogue, historical events, or
relationships; remove required characters or scenes; change chronology or spiritual
teachings; replace unfamiliar words with model interpretations; or present artistic
interpretations as verified Granth facts. Every factual scene element must reference
its source. Unspecified visual details must be labeled artistic interpretation.

### B. Global series continuity

All 21 adhyays share one canonical character, location, prop, and style registry.
Recurring characters retain identity across scenes, camera angles, clothing, and
lighting changes.

### C. One visual production, two releases

Marathi and Hindi share character sheets, backgrounds, keyframes, and general
animation clips. Only language-dependent assets—dialogue, narration, subtitles,
timing edits, and selected lip-sync shots—are created separately. Generate one
visual master for each shared shot and reuse accepted assets in both timelines.

### D. Minimal orchestration

Use filesystem manifests and existing ComfyUI workflows. Do not introduce SQLite
or another application database, multi-agent screenplay/director systems, a custom
inference server, a custom distributed GPU scheduler, or elaborate model routing.

### E. Measured performance

No video model is production-ready before testing on the actual Kaggle T4 setup.
Measure speed, VRAM use, accepted render quality, and retry frequency.

## 3. System stages

- Input — Approved adhyay research: verified chapter text, scene breakdowns,
  dialogue, and provenance tags.
- Stage 00 — Series canon: global characters, locations, props, appearance
  references, fixed art direction, and source provenance.
- Stage 01 — Bilingual audio: Marathi master → IndicTrans2 Hindi adaptation →
  terminology checks → IndicF5 MR/HI TTS → measured audio durations.
- Stage 02 — Keyframes: canonical SDXL model, character conditioning, lighting
  presets, start-frame generation, and optional end-frame generation.
- Stage 03 — Motion: Tier 0 animated stills; Tier 1 LTX 2B I2V; Tier 2 LTX 2B
  guided first/last-frame conditioning (FLF), gated. Outputs are shared clips.
- Stage 04 — Automated QA: source checks, output integrity, audio verification,
  visual diagnostics, bounded retries, and SHA-256 receipts.
- Stage 05 — Bilingual assembly: independent Marathi and Hindi timelines reusing
  shared visual masters.

## 4. Stage 00 — Global canon and research lock

### 4.1 Research ingestion

Import reviewed chapter data without regenerating the story. Support chapter
overview and episodes; characters and aliases; locations, objects, time, and seasons;
scene descriptions; dialogue and speaker relationships; explicitly stated visual
details; continuity and cross-chapter links; uncertain words and unanswered
questions; corrections and user clarifications.

Create a SHA-256 source receipt with a schema version. A modification to an
approved file produces a new source version.

### 4.2 Global character registry

Use permanent character IDs. Merge cross-adhyay references using aliases and
evidence; never merge uncertain matches automatically. Scene-specific clothing,
posture, or age changes require source support or an explicit artistic-interpretation
label.

### 4.3 Global visual style

Use one versioned art direction across the series. Keep style configurable; no
watercolor, oil-painting, or photorealism selection is implied by this freeze. Use a
fixed checkpoint, references, prompt conventions, and approved lighting presets.
A style LoRA is optional and trained only if the pilot shows material consistency
improvement.

### 4.4 Canonical reference sheets

Generate front, three-quarter, profile, and full-body views for major recurring
characters wherever useful. Derive related views from a common reference rather
than independently inventing faces. Generation and selection remain automated;
record that artistic representations have not been manually authenticated.

## 5. Stage 01 — Bilingual script, translation, and audio

Marathi is the source-language master.

### 5.1 Marathi dialogue lock

Import exact approved lines with speaker IDs, scene IDs, and source references.
Never rewrite approved Marathi dialogue during rendering. Keep original verses
distinct from narration and dialogue when research distinguishes them.

### 5.2 Hindi adaptation

Use IndicTrans2 initially. A pronunciation and translation glossary protects sacred
terminology, names, relationships, numbers, and quotations. Validate protected terms,
speakers, and factual fields deterministically, alongside semantic comparison.
Block significantly discrepant lines and do not generate their audio. Semantic
verification reduces risk; it does not prove perfect translation.

### 5.3 Voice generation

Use IndicF5 first for Marathi and Hindi. Maintain stable reference audio, transcripts,
pronunciation settings, and voice-model versions per recurring character. References
must be appropriately licensed or consented. Do not imply a synthetic voice is an
authentic historical recording.

### 5.4 Audio timing

Generate speech first and measure actual playback duration from audio metadata.
Use ASR to check missing/incorrect words, not as a definitive pronunciation judge.
Subtitle text comes from the approved script with measured utterance timing. Begin
with sentence/phrase timing; word-level alignment requires a validated aligner for
the specific language.

## 6. Stage 02 — Style-locked keyframe batch

Load the image workflow and generate episode keyframes as a batch. Default to one
start keyframe per shot. Generate an end frame only for an explicitly defined final
pose or composition.

Conditioning uses an SDXL FP16-compatible workflow, canonical character references,
scene lighting, at most one optional style LoRA, one identity-conditioning mechanism
where needed, and fixed versioned prompt templates and seeds. Do not stack competing
face/style adapters by default.

Each image request includes character IDs and appearance references; location ID and
required objects; permitted attire and required action/pose; lighting bucket, camera
framing, and art direction; source facts, artistic-choice flags, and seed. Never
regenerate a character/location without its canonical references. Do not require
global histogram matching: preserve natural scene-specific lighting. Validate the
keyframe batch before video generation.

## 7. Stage 03 — Three-tier motion

Accepted keyframes enter a batch queue by tier.

### Tier 0 — Animated stills

Use FFmpeg pan, zoom, and tilt; simple depth parallax only if validated; static or
gently animated sacred tableaux; establishing shots, landscapes, objects, and
narration coverage. This tier requires no diffusion-video inference.

### Tier 1 — LTX-Video 2B single-image I2V

The default motion candidate is `ltxv-2b-0.9.8-distilled`. Intended uses include
gentle movement, walking/turning when reliable, ambient movement, simple expressions,
and physical interactions. Inputs: canonical start image, motion-only prompt, seed,
supported width/height and frame count, and a validated FP16-compatible workflow.
Motion prompts must not introduce new story elements.

### Tier 2 — LTX-Video 2B guided FLF

Use for a defined starting and ending pose: a bow, hand gesture, or controlled
framing change. Enable `LTXVAddGuide` multi-frame conditioning only after a working
workflow is validated against the pinned 0.9.8 2B checkpoint. Derive the end image
from the same composition through controlled editing/inpainting.

Tier 2 stays disabled until quality, stability, and efficiency pass the T4 benchmark.
If FLF fails, conventional I2V plus editorial coverage is permitted only when it
faithfully conveys the approved event.

### Video frame rules

The supplied plan lists supported examples `49, 65, 81, 89, 97, 121`. At nominal
24 fps, 121 frames is approximately 5.0 seconds and 89 frames approximately 3.7
seconds. Verify decoded duration with ffprobe and match the timeline with holds,
cutaways, or trimming. The source message's frame-count formula was absent; its
exact constraint must be confirmed against the pinned workflow before implementation.

## 8. Kaggle GPU execution

Use two independently configured ComfyUI worker processes where memory/software
compatibility permits. Both accept compatible independent jobs. Two 16 GB GPUs do
not behave as one 32 GB GPU. Worker concurrency remains benchmark-dependent.

Stage batch order:

1. Marathi and Hindi audio.
2. All required keyframes.
3. Tier 0 animation.
4. Tier 1 LTX video.
5. Tier 2 FLF, if enabled.
6. QA and episode assembly.

Group model loads to reduce switching. CPU assembly/file validation may overlap GPU
rendering without oversubscribing resources. Before a batch verify available VRAM
and RAM; model/VAE load success; disk capacity for frames/checkpoints; precision and
numerical stability; remaining Kaggle runtime; and a working persistent-output
destination. Do not assume FP8 is faster on Turing T4.

## 9. Stage 04 — QA and recovery

Routine human image/video review is not required. Automatic checks do not guarantee
visual accuracy.

Hard rules and failure behavior:

- Source integrity: every scene references locked research; otherwise block.
- Character identity: every referenced ID exists in canon; otherwise block.
- Marathi dialogue: approved text unchanged; otherwise block.
- Hindi script: required terms and factual fields valid; otherwise block.
- Audio: valid file, language/speaker metadata, and acceptable speech checks;
  retry, then block.
- Video: correctly decoded MP4, expected stream, acceptable duration; retry.
- Output receipt: current-input and output hashes match; regenerate if invalid.
- Required sacred event: no permitted faithful output after attempts; block scene.

Log diagnostics in `qa_report.json` without enforcing uncalibrated thresholds:
face embeddings and reference consistency; CLIP/style similarity, color distribution,
edge sharpness; motion instability; suspected anachronisms; possible missing/extra
objects.

Retryable video failures receive an initial attempt plus up to two additional
attempts. Reuse the accepted candidate with the best validated outcome. Noncritical
ambient motion may fall back to Tier 0. Required physical events may fall back only
if the required action remains faithfully represented. Otherwise block; never
silently substitute an invented miracle or event.

A completed asset is reusable only if receipt, inputs, workflow version, and output
checksum match. Write temporary outputs, verify them, atomically rename to final
paths, and save receipts to durable external storage. On restart reload manifests,
verify receipts, skip valid completed jobs, and resume the remaining queue.

## 10. Stage 05 — Bilingual editorial assembly

Render each approved primary action once. Example shared footage:
`shot_014_main.mp4` (3.7 s) and `shot_014_cutaway.mp4` (2.5 s). A Marathi edit can
use 3.7 s main action + 0.5 s coverage = 4.2 s; Hindi can use the same 3.7 s action
+ 1.9 s coverage = 5.6 s. Action retains natural speed; cover extra speech with
appropriate footage without cutting required gestures.

Default to language-neutral coverage: over-the-shoulder angles, wide conversations,
listener reactions, cutaways, and narration over scenery/actions. Essential visible
speech close-ups receive separate Marathi/Hindi lip-sync renders only through a
pipeline validated for the chosen visual style.

FFmpeg assembles each language independently. Required chapter outputs:

- `adhyay_XX_marathi.mp4`
- `adhyay_XX_hindi.mp4`
- `adhyay_XX_marathi.srt`
- `adhyay_XX_hindi.srt`

## 11. Final repository structure — reserved

The supplied plan contains this heading without a structure. Repository paths and
layout are not frozen by this document. Define them during implementation within
the frozen file-driven architecture; do not infer that a layout was approved.

## 12. Episode manifest contract — reserved

The supplied plan contains this heading without fields or a schema. The detailed
contract remains to be specified. It must enforce the frozen provenance, canon,
language separation, dependency invalidation, workflow versioning, and receipt rules.

## 13. Starting technology stack

- Canon/state: YAML/JSON + SHA-256.
- Source validation: Python schema validation.
- Marathi-to-Hindi translation: IndicTrans2.
- Marathi/Hindi TTS: IndicF5.
- Character keyframes: SDXL with reference conditioning.
- Optional image LoRA training: Kohya SS.
- Image/video execution: ComfyUI.
- Tier 0 animation: FFmpeg.
- Tier 1 motion: LTX-Video 0.9.8 2B distilled candidate.
- Tier 2: gated LTXVAddGuide workflow.
- Optional lip-sync: tested language-specific pipeline.
- Technical QA: ffprobe, FFmpeg, Python validators.
- Assembly: FFmpeg.
- Compute: Kaggle Dual T4.
- Persistence: verified external artifact storage.

## 14. Production flow and CLI interface — reserved

The supplied plan contains this heading without commands. The stage flow elsewhere
in this document is frozen; exact CLI commands/options remain to be designed.

## 15. Pre-production benchmark gate

Before a complete episode, execute a fixed six-shot benchmark on actual Kaggle T4s:

- A: Tier 0 establishing/ambient shot.
- B: Single-image I2V with a major recurring character.
- C: FLF variant of the same shot and character.
- D: Character gesture/dialogue coverage.
- E: Recurring character in different lighting.
- F: Shared-visual Marathi and Hindi final edits.

Measure accepted visual seconds per GPU-hour. The supplied primary-throughput
heading has no formula or numerical threshold; define the accounting method and
acceptance budget before execution, without claiming a frozen performance target.
Measure VRAM, render time, quality/continuity acceptance, and retries.

- Tier 1 GO: pinned I2V workflow loads and produces technically valid, acceptable
  clips within the available GPU budget.
- Tier 2 GO: FLF provides useful improvement on comparable shots without
  unacceptable memory, time, or continuity costs.
- Tier 2 NO-GO: leave FLF disabled and use Tier 0/Tier 1 editorial techniques.
- Production NO-GO: if neither available motion workflow supplies acceptable
  recurring-character continuity, do not begin the 21-episode batch. Preserve the
  architecture and replace only the rendering workflow.

## 16. Release and change control

- Research edit: invalidate affected source-derived scenes, dialogue, and assets.
- Hindi-only dialogue edit: regenerate affected Hindi TTS, subtitles, and timeline;
  reuse shared footage when visuals do not change.
- Character canon edit: invalidate dependent keyframes/clips across affected episodes.
- Style-model edit: create a new style version; rerender intended affected material.
- Generation-model edit: update workflow version; regenerate affected shots only.
- Failed critical source, translation, or visual generation: episode remains incomplete.
- Completed episode: release only with all required scenes and both valid language
  timelines, all hard QA gates passed, and successfully decoded final videos.

Edits to this frozen baseline require an explicit approved architectural revision.
Record the revision and regenerate its checksum receipt. Benchmark configuration
choices may resolve the open items below without changing the frozen core.

## 17. Freeze matrix

### LOCKED

21 chapter episodes; 42 MR/HI releases; research-first source-locked storytelling;
global character/world canon; Zero-DB YAML/JSON manifests and SHA-256 receipts;
bilingual audio-first planning; shared visuals; SDXL canonical keyframes;
stage-batched ComfyUI execution; Tier 0 still animation; LTX 2B I2V default
candidate; FLF behind a benchmark gate; automated QA with bounded retries;
per-shot recovery; independent FFmpeg timelines; no routine manual visual review.

### GATE OPEN

Exact image/video checkpoints; T4-compatible precision/workflows; FLF enablement;
generation resolution and steps; character LoRA requirement; GPU worker concurrency;
accepted-video throughput and total production cost; final art style.

### MONITORED RISK — explicit non-guarantees

Historical authenticity of unspecified visuals; 100% facial identity in every frame;
perfect Hindi semantic equivalence; error-free Marathi pronunciation; zero visual
hallucinations; fixed GPU-hours per episode.

## 18. Next execution milestone

Implement a small file-driven batch runner, then run Shots A–F on Kaggle Dual T4s
with recurring characters, one shared animated action, verified crash recovery,
and measured accepted visual seconds per GPU-hour. Scale to 21 adhyays only after
the pilot passes the benchmark gates; the core architecture remains unchanged.

This freeze authorizes preservation of the plan. It does not initiate implementation,
downloads, model training, paid services, Kaggle execution, or production rendering.
