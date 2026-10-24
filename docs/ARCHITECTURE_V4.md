# GranthStudio v4 — Frozen Architecture (animation-studio design)

Project: Shri Gajanan Maharaj Vijay Granth series — 21 Adhyays, 21 episodes, 42 Marathi/Hindi releases
Status: FROZEN by the owner ("FREEZE THE NEW PLANS", 2026-10-24, Asia/Calcutta). Checksum receipt: `docs/ARCHITECTURE_V4.FREEZE.json`.
Supersedes for new work: `docs/ARCHITECTURE_V3_1.md` (kept unedited, D-001/D-005) and the v3.2 proposal (D-010).
Freezing records the design. It does not claim that anything below is implemented, benchmarked, validated or reviewed by a human.

## 1. Objective

A pipeline that, once built, takes the approved research for an Adhyay and produces finished Marathi and Hindi films end to end:
illustrated 2D/2.5D animation with real character acting, cinematic direction, motion graphics, narration, music and sound. Not an animated slideshow, and not generative video for every second.

Unchanged principles from v3.1: sacred source integrity (no invented events, dialogue, relationships or teachings; every factual element cites its ovi; unspecified visuals are labelled artistic interpretation), one global canon for all 21 Adhyays, one visual production with two language releases, filesystem manifests with SHA-256 receipts and no database, measured performance before any production claim.

## 2. Owner decisions (2026-10-24)

- Images: Nano Banana API (owner provides a billed key) is the production image backend; use as many images as the work needs.
- Code: Kimi K3.1 Pro writes the pipeline code; Codex reviews every change.
- Renderer: ONE renderer, chosen by a same-scene acting bake-off between Blender (headless, Python) and HyperFrames (Node + Chromium, GSAP). The loser is removed.
- Assembly: FFmpeg.
- Nano Banana 2.1 supplies separate body parts (arms, legs and other elements) on request.

## 3. Evidence behind the design (measured in this project)

| Finding | Where |
|---|---|
| SDXL + IP-Adapter cannot hold the painted style and several identities | docs/pilot/SDXL_STYLE_AUDIT.md |
| LTX 0.9.8 on a T4 adds a push-in no prompt stops and smears faces | docs/evidence/pilot_video, docs/evidence/kaggle_dual_t4 |
| The owner's Nano Banana sheets give the target look and consistent characters | assets/pilot_refs/set_v1, set_v2 |
| Qwen-Image-2.1 (open, 4-bit, references at 512) made all three pilot scenes with references on a free T4, 10-13 min per image | Kaggle granthstudio-bench-gpu-all v7 |
| Code-driven camera paths and depth parallax work | src/granthstudio/motion.py, scripts/animation/parallax.py |
| NVIDIA free image endpoints are text-only; HiDream and FLUX 3 Klein do not fit a T4; Kaggle TPU sessions did not execute | scripts/image_trials, Kaggle runs 2026-10-24 |
| Kaggle notebook logs can be empty: evidence must be written to files | scripts/kaggle/build_gpu_all_notebook.py |

Not verified here: Kimi K3.1 Pro on this repository (released 2026-10-23/24); Nano Banana 2.1 prices (secondary sources: about USD 0.034 / 0.050 / 0.113 per 1K / 2K / 4K image, batch about half) until read on Google's pricing page.

## 4. Five subsystems, one renderer

### 4.1 Source-locked Cinematic Coverage Planner (Kimi at runtime, bounded)
Input: approved ovi research and beats. Output per beat: a coverage plan (establishing, action stages, reaction, insert, hold), what the viewer notices first, the event communicated, screen direction, what moves and what stays still, and timing anchors on narration words.
It decides HOW the audience sees an event, never WHAT happened: no new events, characters, objects or gestures. An unsupported or ambiguous depiction stops that beat for review. Artistic choices are labelled. Output is schema-validated, cached by input hash and stored as the shot manifest.

### 4.2 Nano Banana Visual Studio (image runner)
Produces a **shot asset package**, not a single picture: master composition, clean background, character matte, body parts and pose sequence, prop and interaction layers, alternate coverage angles, optional environment plates.
- Anchored branches: every pose or part is an edit from the canonical master (and at most its approved parent). An experimental edit never becomes a master.
- A reference packet travels with every request (identity, costume, style, location), within the documented reference limits. Chat memory is never relied on.
- Reconstruction test for every layered shot: background plus parts re-composited against the approved master (alignment, holes, halos, joint overlap). Failure blocks the shot.
- Lineage per image: parents, prompt, model id, input hashes, cost, approval.
- Request lifecycle PREPARED → SENT → ACKNOWLEDGED → COMPLETED; an ambiguous outcome becomes UNKNOWN and is recovered by interaction id where the API allows, reconciled, or re-sent only by an explicit decision. SDK retries are configured deliberately. Duplicate protection is strong; exactly-once billing is not promised.
- Qwen-Image-2.1 on Kaggle is the outage/quota fallback only, checked for equivalence before its output is used.
- Mattes: masks or keying first (parts generated on a flat ground); a segmentation model only when a real shot needs it.

### 4.3 Character Performance Engine and cinematography (inside the chosen renderer)
Character acting is a first-class system, not an effect added to paintings.
- Performance library per character: reusable actions, each defined by pose keys, pivots or bones, timing arcs and facial states. Maharaj (seated first): rest, listen, eat, blessing, fold hands, turn, smile. Bankatlal: listen, folded hands, speak, stand, approach.
- Three methods in the one renderer: layered puppet (head, arms, torso, garment, eyes; bones with mesh deformation if Blender wins) for subtle acting; authored pose animation (approved drawings switched on deliberate keys, poses may run "on twos" while camera and environment run at 24 fps); cinematic action coverage (several generated angles and action stages joined by cuts, cut-on-action) for complex actions and object handling.
- Physical constraints are part of the performance asset: anchor points, prop attachments, pivots, occlusion order, gaze targets.
- The stage (camera, entrances, environment, 2.5D depth, transitions, manuscript graphics) is a separate track from the body.
- Determinism contract: frame-addressable, seekable timelines only; no wall-clock timers or live network assets; seeded randomness; all assets local and preloaded; random-access frame test per preset.
- Every shot carries an approved visual event, a reaction or a deliberate hold. Camera motion alone is not acting.
- Token rule: reusable performances and a manifest runner. No per-shot code generation and no per-shot interactive tool sessions in production (interactive control, e.g. Blender MCP, only while building rigs).

### 4.4 Render, audio and bilingual assembly
Short cached shot clips. Dependency hashes decide what re-renders: changed narration never triggers image jobs; a changed pose re-renders only its shots; a renderer version change invalidates renders, not images.
Narration is measured per language; acting events are anchored to approved speech timestamps; Hindi reuses the visuals with its own timing. Tracks: narration, dialogue, ambience, effects, music. Captions through FFmpeg/libass (HarfBuzz shaping for Devanagari); manuscript titles rendered as images by a shaping-aware tool. FFmpeg makes the masters.

### 4.5 Quality, recovery and release
- Structural checks (automatic): schemas, files, frame counts, sizes, decoding, durations, blank images.
- Visual screening: CV metrics plus Kimi image understanding, given the exact reference packet and sampled frames, with separate questions for identity, costume, action, objects, style and artifacts; every flag saved with evidence. Calibrated on known pilot failures; a category it misses cannot be cleared automatically.
- Artistic approval (owner scorecard): identity, performance, art consistency, direction, audio. A severe identity, source or anatomy error blocks regardless of score.
- Risk routing: reused approved combinations render automatically; a new shot with a known character and tested pose is created and screened; a new complex action or prop interaction gets stronger checks and review on uncertainty; a new character or costume, or an unresolved source interpretation, stops; any severe mismatch stops with a blocker. Random samples of automatically accepted shots go to the owner's review queue.
- Nothing is marked approved by a model. Every release needs the owner.

## 5. Roles

| Actor | Does | Never |
|---|---|---|
| Claude | architecture, Kimi brief, design critique | runtime story writing |
| Kimi K3.1 Pro (coding) | implementation, tests, skills, schemas | alter frozen canon, mark reviews done |
| Codex | independent review: correctness, determinism, data dependencies, secrets, billing, recovery | competing edits in the same worktree |
| Kimi (runtime planner) | shot coverage from approved beats | invent events, dialogue or facts |
| Kimi (runtime screener) | flag identity, costume, action, style issues | claim historical or theological correctness |
| Nano Banana runner | requested, reference-grounded assets | change approved identity or costume |
| Pipeline | validate, cache, render, retry safely, assemble | bypass an open approval blocker |
| Owner | approve research, canon, pilot, releases | — |

## 6. Data contracts (filesystem, JSON Schema, SHA-256 receipts)

- `canon/`: characters, costumes, locations, props, style anchor; each with source refs and approval state.
- Asset package manifest: file, sha256, kind (master, background, matte, part, pose, prop, coverage), parents, prompt, model id, input hashes, cost, approval.
- Shot manifest = performance contract: `source_refs`, `event_id`, `characters`, `performance {library_action, start_pose, end_pose, gaze_target, prop_constraints, screen_direction, timing_anchor}`, `camera {framing, movement, intensity}`, `animation {body_mode, environment_mode, fps}`, `assets {master, pose_package, background}` hashes, `approval`.
- Request journal per API call with the lifecycle states above; cost per approved shot includes input, retries and rejected images.

Keys (Nano Banana, Kimi) live outside the repository (a secrets folder or environment), are never printed, and are scrubbed from every log, receipt and error message. Gemini and Kimi terms (ownership, SynthID) are recorded with each release. Hosted NVIDIA endpoints remain evaluation-only.

## 7. Compute placement

This PC (RTX 3050 6 GB): manifests, rendering, FFmpeg, QA. Google API: Nano Banana. Kimi API: planner and screener. Kaggle T4: Qwen-Image-2.1 fallback, segmentation or depth only when needed, with logs teed to files, one model at a time and caches cleared. No TPU path.

## 8. Work order (riskiest first; each phase ends in something the owner can watch)

| Phase | Deliverable | Gate |
|---|---|---|
| P0 | This document, D-013, JSON schemas, Kimi pack (AGENTS.md and seven skills: source-to-shots, nano-banana-assets, character-performance, cinematic-direction, manuscript-graphics, audio-timing, render-qa, adapted from HyperFrames' official skills and the ClaudeAnimationBase guide, read not installed wholesale) | Codex review |
| P1 | Renderer proofs on this PC, Blender headless and HyperFrames: 10 s at 1080p24 = 240 frames, the same frame rendered twice is identical, local assets only, RAM/VRAM/time recorded; Devanagari caption via FFmpeg/libass | technical pass |
| P2 | Acting bake-off: the same Maharaj seated blessing or eating shot from the same Nano Banana parts in both renderers; then one Bankatlal folded-hands/listen in the winner | owner picks the renderer |
| P3 | Asset automation: runner, packets, anchored branches, lifecycle with UNKNOWN, cost, mattes, clean plates, reconstruction test, lineage | reassembly and identity pass |
| P4 | Coverage planner for the Adhyay 1 pilot beats; refuses unsupported events | adversarial beats refused |
| P5 | Cinematic presets: camera, environment, 2.5D, manuscript graphics with character tracks | visual pass |
| P6 | Bilingual sound: approved voice (a labelled scratch voice only for timing work), speech-anchored events, MR/HI timelines | sync pass |
| P7 | 60-90 s pilot: opening, two-character exchange, physical action, manuscript transition, MR and HI | owner scorecard |
| P8 | Continuous 5-8 min sequence | no repetition fatigue, drift or resource failure |
| P9 | One Adhyay unattended from approved research to both masters | owner approval |
| P10 | Remaining Adhyays | repeated QA and release gates |

P1 and P3 run in parallel with the P2 art preparation; P4 starts once the P0 schemas are frozen.

## 9. Prerequisites from the owner

Nano Banana API key (billed) in a secrets folder; Kimi API access for the runtime planner and screener; permission to install Blender (current LTS) and Node 22 + Chromium for P1/P2; a Marathi narration source (recording or an approved TTS voice; IndicF5 is on hold pending consent).

## 10. Verification rules

Every change: synthetic-fixture tests, the full suite, a Codex review with no blocking issue, a clean tree. P1: frame counts, repeatability, Devanagari compared with a reference image, resource numbers. P3: reconstruction numbers, complete lineage, a forced ambiguous timeout lands in UNKNOWN without a second paid call. P4: adversarial beats refused. P7-P9: owner scorecard, receipts, one changed shot re-rendered without regenerating unrelated assets, both language masters from the same visuals.

## 11. Explicit non-guarantees

Perfect facial identity in every frame; fully fluid feature-film acting; historical authenticity of unspecified visuals; error-free pronunciation; fixed cost or render hours per episode. These are measured and reviewed, never assumed.
