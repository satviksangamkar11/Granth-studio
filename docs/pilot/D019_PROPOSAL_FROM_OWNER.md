# D-019 proposal as pasted by the owner on 2026-10-25 (condensed faithfully by Claude for review; not approved)

Status in the paste: PROPOSED. Purpose: convert the approved Shri Gajanan Vijay Granth text, meanings and research into faithful, complete Marathi and Hindi films with reusable 2.5D/papercut assets and deterministic Blender production.

Governing requirement (owner): an Adhyay can hold zero, one, two or three stories, each must be properly completed; some Adhyays are mostly philosophy; the system must understand and present the actual source faithfully, not impose one structure. Never invent closure; continuations stay continuations.

Pre-mortem: (1) doctrinal/narrative distortion (invented events, miracles, dialogue, teachings); (2) incomplete story/teaching coverage; (3) ornate but inert visuals.

Principles: canon = approved Marathi transcription + approved meanings/annotations/research; generated material is never truth. 1 Adhyay -> 1 episode -> Marathi + Hindi releases; length from content. Evidence discipline for costume/iconography too. Bilingual versions share shots/assets/canon; timing/captions may differ, meaning not. File-driven JSON/YAML, hashes, receipts, no database. Kimi implements reusable functions and may generate structured story/shot plans, not per-shot Blender scripts; renders run offline. Nano Banana generates only missing art, with spend caps and UNKNOWN handling. D-018 not silently overwritten.

Architecture: approved corpus -> SOURCE COMPILER (typed passage ledger per ovi: STORY_EVENT, DIALOGUE, PHILOSOPHY, DEVOTIONAL, DESCRIPTION, METAPHOR, EXPLANATION, TRANSITION; global character/place canon) -> ADHYAY UNDERSTANDING (story-thread graph with closure values RESOLVED_IN_ADHYAY / CONTINUES_NEXT_ADHYAY / STARTED_EARLIER / SOURCE_INCOMPLETE_OR_AMBIGUOUS, plus a teaching graph) -> STORY & TEACHING DIRECTOR (episode_treatment.json: sections, threads, coverage, voice-led vs action-led, runtime from narration words) -> SOURCE FIDELITY GATE (coverage ledger: every span VISUALIZED/NARRATED/QUOTED/MERGED_EQUIVALENT/APPROVED_OMISSION; closure verdicts) -> CINEMATIC DIRECTOR (scene_contracts/*.json: blocking, performances, camera, asset IDs, continuity, interpretive vs factual assertions) -> SCENE CONTRACT VALIDATOR -> ASSET RESOLVER (style pack + character/location/prop/performance/shot-recipe packs; Nano Banana only for missing assets) -> BLENDER SHOT COMPILER (Kimi-written typed compiler with reusable bpy primitives load_pack, place_layer, stage_actor, play_performance, attach_prop, set_camera, set_lighting, render_frames) -> RENDER + FFmpeg finish -> MARATHI MASTER + HINDI MASTER -> structural, source, visual and human release gates.

Philosophy segments: Discourse Director (voiceover, manuscript typography, symbols tied to stated metaphors, contemplative holds, restrained camera); never fake Maharaj conversations for movement.

Universal shot contract (JSON): episode_id, section_id, section_kind, story_thread_ids, source_span_ids, source_status, interpretive_additions, purpose, visual_assertions with source_refs and type, performance presets with times, camera preset, render_mode, asset_refs, continuity in/out, audio_anchor_id, qa.

Style: benchmark paper-cutout relief with restrained Indian folk border, paper grain, controlled palette, gold accent (a test, not approved). Eight-layer recipe as a preferred composition, not mandatory. Asset packs carry ID/version/hash, anchors/pivots, occlusion order, permitted transforms, lineage; flattened PNG is not a riggable character.

Motion modes: M0 expressive static (camera, cuts, ambient); M1 limited mechanical (head turn, gaze, blink, breathing, hinged blessing arm, folded hands); M2 authored multi-pose action via cuts; M3 bespoke with budget gate. No image-to-video models.

Blender is the SOLE animation/staging renderer; FFmpeg for assembly/finishing; reuse motion.py/parallax.py algorithms where compatible; HyperFrames excluded.

Voice: narration frozen per language after source approval; language-validated forced alignment or manual timestamps; Devanagari shaping tested.

Three QA gates: (1) source/editorial before image spend; (2) render feasibility/technical; (3) visual and human. Release blockers: unsupported event/dialogue/miracle/teaching, unresolved discrepancy, wrongly closed story, wrong sacred identity/costume, major continuity errors, translation drift.

Data tree: canon/adhyay_NN/{ovis.jsonl, meanings_mr.jsonl, meanings_hi.jsonl, approvals.json}, canon/global; production/adhyay_NN/{understanding, direction, screenplay, shots, assets, audio, renders, qa}; asset_library/{style_packs, characters, locations, props, performances, shot_recipes}; receipts.

Phases: P0 D-018 evidence audit; P1 Source Director dry-run on three samples (a complete story, a 2-3 story Adhyay, a philosophy-heavy Adhyay) with no image spend; P2 15-second visual proof + second shot from only new art/text; P3 Blender scene compiler (Kimi codes reusable operators), M0+M1; P4 60-90 s narrative pilot MR/HI; P5 5-8 min section; P6 full Adhyay both languages; P7 series.

Decisions proposed: papercut relief benchmark; 16:9 master, 9:16 only after recomposition test; Marathi captions on Marathi release, Hindi on Hindi; hinged arms yes as one approved preset; shot lists model-generated from approved treatment then validated; Blender production renderer; Kimi for bounded planning and reusable code, cached per Adhyay.

External research cited (not executed): ViMax (HKUDS), CineCrew (Ironieser), Look-Before-Move (EngineeringAI-LAB, dataset CC BY-NC), FilmAgent, Storytools (Pullusb), VideoClaw (HITsz-TMG).
