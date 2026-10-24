# GranthStudio v4 — Frozen Architecture (animation-studio design)

Project: Shri Gajanan Maharaj Vijay Granth series — 21 Adhyays, 21 episodes, 42 Marathi/Hindi releases
Status: FROZEN by the owner ("FREEZE THE NEW PLANS", 2026-10-24, Asia/Calcutta). AMENDED the same day by D-014 (renderer fixed to Blender, section 12). Checksum receipt: `docs/ARCHITECTURE_V4.FREEZE.json`. The original freeze is preserved at git tag `arch-v4-freeze-2026-10-24` (commit 818fe6b); the amendment is a new commit and a new tag.
Supersedes for new work: `docs/ARCHITECTURE_V3_1.md` (kept unedited, D-001/D-005) and the v3.2 proposal (D-010).
Freezing records the design. It does not claim that anything below is implemented, benchmarked, validated or reviewed by a human.

## 1. Objective

A pipeline that, once built, takes the approved research for an Adhyay and produces finished Marathi and Hindi films end to end:
illustrated 2D/2.5D animation with real character acting, cinematic direction, motion graphics, narration, music and sound. Not an animated slideshow, and not generative video for every second.

Unchanged principles from v3.1: sacred source integrity (no invented events, dialogue, relationships or teachings; every factual element cites its ovi; unspecified visuals are labelled artistic interpretation), one global canon for all 21 Adhyays, one visual production with two language releases, filesystem manifests with SHA-256 receipts and no database, measured performance before any production claim.

## 2. Owner decisions (2026-10-24)

- Images: Nano Banana API (owner provides a billed key) is the production image backend; use as many images as the work needs.
- Code: Kimi K3.1 Pro writes the pipeline code; Codex reviews every change.
- Renderer: Blender (headless, Python API) is the primary and only planned production renderer (D-014). No Blender-versus-HyperFrames bake-off. HyperFrames is outside the production path and exists only as a separately approved fallback if Blender fails the defined quality test in section 12.
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

## 4. Five subsystems, one renderer (Blender)

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

### 4.3 Character Performance Engine and cinematography (inside Blender)
Character acting is a first-class system, not an effect added to paintings.
- Performance library per character: reusable actions, each defined by pose keys, pivots or bones, timing arcs and facial states. Maharaj (seated first): rest, listen, eat, blessing, fold hands, turn, smile. Bankatlal: listen, folded hands, speak, stand, approach.
- Three methods in the one renderer: layered 2.5D puppet (the Nano Banana parts as image planes with bones and mesh deformation: head, arms, hands, torso, garment, eyes, mouth) for subtle acting; authored pose animation (approved drawings switched on deliberate keys, poses may run "on twos" while camera and environment run at 24 fps); cinematic action coverage (several generated angles and action stages joined by cuts, cut-on-action) for complex actions and object handling.
- Physical constraints are part of the performance asset: anchor points, prop attachments, pivots, occlusion order, gaze targets.
- The stage (camera, entrances, environment, 2.5D depth, transitions, manuscript graphics) is a separate track from the body.
- Determinism contract: every motion is a function of the frame number (keyframed actions, drivers, fixed seeds for any noise); no wall-clock or live network inputs; all assets local; the same frame rendered twice must match within a stated tolerance; renderer and add-on versions pinned and recorded.
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

This PC (RTX 3050 6 GB): manifests, headless Blender rendering (EEVEE), FFmpeg, QA. Google API: Nano Banana. Kimi API: planner and screener. Kaggle T4: Qwen-Image-2.1 fallback, segmentation or depth only when needed, with logs teed to files, one model at a time and caches cleared. No TPU path.

## 8. Work order (riskiest first; each phase ends in something the owner can watch)

| Phase | Deliverable | Gate |
|---|---|---|
| P0 | This document, D-013/D-014, JSON schemas, Kimi pack (AGENTS.md and seven skills: source-to-shots, nano-banana-assets, character-performance, cinematic-direction, manuscript-graphics, audio-timing, render-qa; Blender-specific skills written for this project, community skills read and adapted, not installed wholesale) | Codex review |
| P1 | Blender headless proof on this PC: 10 s at 1080p24 = 240 frames, the same frame rendered twice matches, local assets only, RAM/VRAM/time recorded; Devanagari caption via FFmpeg/libass | technical pass |
| P2 | **Maharaj blessing scene prototype**: Nano Banana Pro animation assets for one character (head, eyes, mouth shapes, torso, both arms, hands, garment, clean background), a minimal Blender Python rig (arm, hand, head, facial movement), one complete seated blessing scene with a visible hand gesture, believable movement and camera coverage; then the audit in section 12 | owner approves, or fails the quality test |
| P3 | Asset automation: runner, packets, anchored branches, lifecycle with UNKNOWN, cost, mattes, clean plates, reconstruction test, lineage | reassembly and identity pass |
| P4 | Coverage planner for the Adhyay 1 pilot beats; refuses unsupported events | adversarial beats refused |
| P5 | Cinematic presets: camera, environment, 2.5D, manuscript graphics with character tracks | visual pass |
| P6 | Bilingual sound: approved voice (a labelled scratch voice only for timing work), speech-anchored events, MR/HI timelines | sync pass |
| P7 | 60-90 s pilot: opening, two-character exchange, physical action, manuscript transition, MR and HI | owner scorecard |
| P8 | Continuous 5-8 min sequence | no repetition fatigue, drift or resource failure |
| P9 | One Adhyay unattended from approved research to both masters | owner approval |
| P10 | Remaining Adhyays | repeated QA and release gates |

P1 may run in parallel with P2's art preparation. Gate (D-014): P3 onward is blocked until the owner approves the P2 audit (section 12). Before that approval only prototype-only preparation is allowed: schemas, documentation, the Nano Banana asset runner scaffold and Blender rig code needed by the P2 scene; no production runners, no planner, no episode pipeline, no batch asset generation beyond the P2 scene.

## 9. Prerequisites from the owner

Nano Banana API key (billed) in a secrets folder; Kimi API access for the runtime planner and screener; permission to install Blender (current LTS) for P1/P2; a Marathi narration source (recording or an approved TTS voice; IndicF5 is on hold pending consent).

## 10. Verification rules

Every change: synthetic-fixture tests, the full suite, a Codex review with no blocking issue, a clean tree. P1: frame counts, repeatability, Devanagari compared with a reference image, resource numbers. P3: reconstruction numbers, complete lineage, a forced ambiguous timeout lands in UNKNOWN without a second paid call. P4: adversarial beats refused. P7-P9: owner scorecard, receipts, one changed shot re-rendered without regenerating unrelated assets, both language masters from the same visuals.

## 11. Explicit non-guarantees

Perfect facial identity in every frame; fully fluid feature-film acting; historical authenticity of unspecified visuals; error-free pronunciation; fixed cost or render hours per episode. These are measured and reviewed, never assumed.

## 12. Amendment D-014 (2026-10-24): Blender is the renderer

Owner decision: Blender is the primary and only planned production renderer. The Blender-versus-HyperFrames bake-off is removed. HyperFrames is not part of the normal production path; it may be considered only as a separately approved fallback if Blender fails the quality test below. No additional renderers, paid services or infrastructure are introduced by this amendment (Nano Banana Pro via the owner's key, Kimi and FFmpeg stay as decided).

Design consequence: the pipeline is Approved research → source-grounded cinematic coverage → Kimi shot plans and code → Nano Banana Pro assets (character sheets, body-part images, backgrounds, props) → Blender 2.5D rigs, character performance, camera and lighting, rendered headless by Python → FFmpeg (audio, subtitles, assembly, exports).

2.5D first, not full 3D: generated paintings are mapped onto image planes or low-poly meshes with bones; full 3D modelling (topology, materials, rigging) is out of scope because an image-first pipeline does not remove that work.

Ranked risks:
1. Character reconstruction: Nano Banana Pro produces images, not animation-ready rigs. Separated arms, hands, faces and clothing can show seams and anatomical errors. Mitigation: parts generated as edits of the approved master, the reconstruction test (parts re-assembled vs the master) before any rigging.
2. Acting quality: Blender can animate but cannot turn a static illustration into believable acting by itself. Mitigation: a reusable rig and the Character Performance Engine (library of actions with timing arcs, pivots, facial states).
3. Production speed: unique animation per scene across 21 episodes would remove the time savings. Mitigation: reusable actions, camera setups and rigs are mandatory; the production path is manifest → headless Blender Python with no agent in the loop.

Quality test (decides whether the decision stands): the first milestone, ONE complete Maharaj blessing scene, is audited and the OWNER records PASS or FAIL in writing (docs/pilot, with the audit evidence). Categories: (a) image seams and halos at joints, (b) hand anatomy, (c) motion believability with a visible gesture, (d) visual consistency with the approved master and style, (e) rendering cost per second of video on this PC (measured and reported; the owner sets any acceptable limit before the audit, and records FAIL if the measured cost makes the series unaffordable by that limit). Rule: a severe error in (a)-(d), meaning a visible seam or halo at rest, a malformed hand, a broken or floating limb, or a face that no longer reads as the approved character, is an automatic FAIL; minor issues are listed and fixed before PASS. PASS is the owner's decision, never a model's. On FAIL the renderer question is reopened by the owner; the fallback to HyperFrames needs a separate written owner approval and is not automatic.

Not in scope now: the full episode pipeline, extra renderers, paid services beyond those already approved, 3D character modelling.
