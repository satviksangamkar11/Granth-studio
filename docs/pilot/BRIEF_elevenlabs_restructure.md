# Brief: restructure GranthStudio around ElevenLabs premium plans (research only; shared by two reviewers)

## Who and what
GranthStudio makes ONE 10-20 minute motion-comic film of Adhyay 1 + Adhyay 2 of "Shri Gajanan Vijay" (Marathi devotional text) with ONE picture track and TWO audio tracks (Marathi, Hindi) plus sound effects. The owner (Satvik Sangamkar) is the only approver. Claude writes harness/validators/glue only; Codex and other agents are read-only reviewers; no model writes animation or Blender code (D-017); no model output becomes canon until the owner approves it.

## The decision on the table
The owner intends to buy ElevenLabs PREMIUM plans (the 30,000-credit Starter plan is the entry point; Creator and above are candidates) and wants the architecture restructured so we SAVE TIME AND MONEY elsewhere. Marathi is stated by the owner to be supported by ElevenLabs speech synthesis, voice cloning and speech-to-text (NOT yet verified by us from ElevenLabs' own documentation; verify it).

## Read first (repository `D:\aai work\granthstudio`, read-only)
`docs/pilot/HANDOFF.md` (current state, pipeline, commands, pitfalls), `docs/ARCHITECTURE_V3_1.md` (frozen; never edit), `docs/DECISIONS.md` (D-015..D-019, A1-A3 and follow-ups), `docs/pilot/NEXT_STEPS_PLAN.md`, `docs/pilot/A1_audio_plan.md`, `docs/pilot/A1_full_script.md` (original verse wording) and `docs/pilot/A1_full_script_simple.md` (owner's easy wording), `scripts/source/a1_voices.py`, `a1_voice.py`, `a1_audio.py`, `a1_audio_spec.py`, `scripts/audio/a1_tts_run.py`, `scripts/source/director_test.py`, `story_split.py`, `kimi_adapter.py`, `scripts/image_trials/v5_ledger.py`.

## What exists today (what could be replaced or simplified)
- Voices: Indic Parler-TTS on a Kaggle GPU (free, gated model, token as a Kaggle secret that only UI-started runs can see, ~22 min per 124 clips, voices only "OK", Hindi male voices limited to two). Timing is MEASURED from generated wavs; shots = ceil(common timeline / 6 s); budgets drive the story split and the Kimi director (paid, capped, ledger-guarded).
- Sounds: a closed palette of 22 UNSOURCED sounds and 18 cues; each needs a recording or a licence-checked CC0/CC-BY file with URL + licence logged.
- Hindi: a draft adaptation, NOT VALIDATED. Dubbing was rejected so far because the owner fixes the Marathi/Hindi wording himself.
- Pipeline gates: story split -> audio plan/timing -> voices -> Kimi director (once per scene) -> images (owner-made) -> render (6 s shots, 24 fps, 11 presets) -> human review.
- Hardware: RTX 3050 6 GB, 15 GB RAM, ~13 GB free disk; heavy generation goes to Kaggle.

## ElevenLabs facts we have (verify and extend from ElevenLabs' OWN pages; mark anything unverified)
Starter: 30,000 credits/month (~30 min TTS), commercial licence, instant voice cloning, 10 voice slots, Studio 20 projects, Dubbing Studio, 128 kbps/44.1 kHz, 3 concurrent requests, 74 languages; Creator ~100-121k credits with professional cloning. Credits: TTS ~1 credit/character (multilingual v2), sound effect 200/generation, music 900/min, speech-to-text 330/min, dubbing 2,000-10,000/min depending on mode. Sources disagree on some numbers.

## Questions to answer (research with sources; be concrete)
1. Which ElevenLabs features could REPLACE or SHORTEN our current steps, and which should NOT: text-to-speech models (v3, multilingual v2, flash) for Marathi and Hindi quality and pronunciation control (pronunciation dictionaries, phoneme tags, audio tags, SSML), voice design/library/cloning for distinct characters, character-level timestamps / forced-alignment (could replace our wav-measuring and give exact timing for sync), speech-to-speech, dubbing (and why we keep script control), sound-effects generator (could fill the 22-sound palette; licensing of outputs), music generator, speech-to-text for QA of pronunciation, projects/Studio, API vs UI, concurrency, batch.
2. Language quality risk: Is Marathi (and Hindi) quality good enough for sacred verse/names? What evidence exists? What test would settle it cheaply (free tier first)?
3. Plan sizing: how many credits does Adhyay 1 (about 9,200 characters of simple script in both languages, 62 lines, 366 s picture) really need including re-takes and 18 sound effects; then Adhyay 2; which plan (Starter/Creator/Pro) is justified for the whole film, per month vs one-off; rollover, overage, commercial rights, watermark rules, what happens to generated audio rights if the plan lapses.
4. Restructure proposal: which stages disappear, shrink or move (Kaggle TTS job, HF gating/secrets, sound sourcing and licence logging, the estimated-vs-measured timing step, the Hindi review burden, director's sound-cue list), what new stages are needed (ElevenLabs job builder + ingest + hash/provenance record; secret handling; ledger-style SPEND guard for ElevenLabs credits like our Kimi ledger; alignment-based timing), and what must stay the same (owner approval gates, exact-text rule for Marathi, no invented dialogue, D-017 renderer, single video with two audio tracks).
5. Time and money saved: estimate honestly (hours of pipeline work and rupees/dollars) versus costs and lock-in; call out any extra spending on OTHER services that the ElevenLabs plan could cancel (e.g. paid sound libraries, GPU time, re-runs).
6. Risks: licence/terms for religious content and voice cloning (consent: never clone a real person's voice without consent), data retention/privacy of the scripts, rate limits, regional restrictions, price changes, reproducibility (voices/models change; we must store text + voice id + model + seed/settings + output hash), failure modes of the dubbing and alignment features.
7. A prioritised, ordered plan: first free-tier test (which 6-8 lines, which success criteria), then purchase decision gates (owner only), then code changes in small steps with tests.

## Rules for you
- Research and propose ONLY. Do not modify repository files except your own report file named below. Do not run anything paid. Never ask for, read or print API keys; never open the `D:\aai work\secrets` folders.
- Cite sources (URL + date) for every ElevenLabs fact; separate verified facts, vendor claims, and your inferences. Say plainly what you could not verify.
- Do not invent Granth content. Do not recommend changing the frozen architecture file; recommend a DECISIONS.md amendment instead if needed.
- Keep it practical for a solo owner with a Windows PC. Give a one-page executive summary first, then the detail.

## ADDENDUM from the owner (2026-10-26, binds this research)
- The VIDEO side is settled: Kimi is the director and the picture pipeline stays as it is. Do NOT re-plan the picture/animation part.
- The AUDIO side will be done ENTIRELY with ElevenLabs on a premium plan: speech (Marathi and Hindi), character voices, AND SOUND EFFECTS (and, if useful, music/ambience). The goal is a full-fledged, GOOD QUALITY film soundtrack, not a minimal one.
- So research sound effects in depth: the sound-effects generator (prompt style, duration limits, looping, prompt-influence, quality, batch/API, credits per generation, output format/sample rate), whether outputs are licensed for commercial release, how to turn our closed palette (22 sounds, 18 cues, anchors scene_bed/picture_event/before_line/after_line, never over a spoken line) into generation prompts, how to mix (ducking under speech, loudness targets, stems per language), whether music/ambient beds fit a devotional film, and how many credits the full soundtrack needs for Adhyay 1 and 2 including re-takes.
- Also decide what the final audio assembly should be (our own numpy/ffmpeg mix versus ElevenLabs Studio/Dubbing Studio) and how timing from ElevenLabs (alignment/timestamps) feeds the shot budgets.

## DEBATE RULE (owner, 2026-10-26)
Do not just agree. Take a clear position, then argue AGAINST it yourself ("strongest case against my recommendation" and "what evidence would change my mind"). After both reviewers finish, each will rebut the other's report in a second round; make claims sourced and falsifiable.
