Proposed content for `docs/pilot/CODEX_ELEVENLABS_SOUND.md`, researched **2026-10-28**. Not saved: your explicit “edit no repo file” instruction takes precedence. No secrets opened or paid calls made.

## 1. SUMMARY

Yes: Kimi Stage 1 plans sound and selects reusable sound IDs.  
When something is missing, Kimi writes an ElevenLabs-ready **sound-effect prompt**; your speech script stays yours.  
Use separate ElevenLabs sound files, mixed by our code against both languages’ measured speech windows.  
Load the current sound palette and animation preset capabilities into every relevant chapter-planning packet.  
Reuse approved files; generate missing sounds once, with credit receipts, hashes and listening approval.

## 2. WHAT WE USE TODAY

These are repository findings, not account-dashboard verification:

- **Speech:** `a1_eleven.py` defaults to `eleven_v4`; empty voice settings mean the voice’s defaults.
- **Cast:** narrator Tukaram, Maharaj Sharad, Bankatlal Bipin, Damodarpant Vinayak. `A1_eleven_voices.json` records identical voice IDs for Marathi and Hindi.
- **Calls:** one request per line **per language**: 62 bilingual lines mean 124 clips when all lines are generated.
- **Plan:** the decision log records Starter, monthly, no annual subscription or automatic top-up. Current account status/balance: **UNKNOWN**. Official pricing currently lists Starter at $6/month and 30,000 shared credits/month, before taxes/promotions. [Pricing](https://elevenlabs.io/pricing)
- **Credits:** code estimates `len(text)`, reserves before submission, and uses the response’s `character-cost` when available. Otherwise the amount remains estimated. It checkpoints clips and reuses matching text/language/voice/model/settings plus a verified file hash. Open reservations block further spending. Actual historical total: **UNKNOWN here**.

**Measurement/export/mix:** generation probes decoded duration; `measured()` exports recorded clip durations and provenance—it does not itself reopen and remeasure every file. `export_wavs()` decodes accepted MP3s to mono 16-bit WAV, normally 44.1 kHz.

`a1_audio.py` builds common beats using the longer language. The current timing file records **59 shots, 354 seconds**. `a1_voice.py mix` places speech at common starts, rejects overlap/overflow and pads to picture length. Optional active-speech balancing precedes whole-track peak normalization; therefore `--target-dbfs -22` does not establish final delivery loudness.

**Sound:** `a1_audio_spec.py` contains **22 proposed sounds, 18 cues using 13 distinct sounds**, all described as unsourced. The reviewed mixer does not implement the proposed effects/bed layer or bilingual ducking. Stage 1 rules already require reuse, NEED_NEW, ledger-controlled generation and no ElevenLabs music. Older recording/CC-licence instructions need reconciliation.

The decision log records owner acceptance of voices; measured manifests retain generic draft warnings. Hindi remains NOT VALIDATED. Preserve the existing clips and approval evidence.

## 3. ELEVENLABS RESEARCH

### Separate Sound Effects API

Endpoint: `POST https://api.elevenlabs.io/v1/sound-generation`.

Request fields:

- `text`: sound description.
- `duration_seconds`: optional; **0.5–30 seconds**; omitted/null lets the model choose.
- `prompt_influence`: **0–1**, default **0.3**.
- `loop`: boolean, default false.
- `model_id`: defaults to `eleven_text_to_sound_v2`; the reference also lists `eleven_text_to_sound_v3`.

The response is audio bytes; optional `character-cost` reports billing. No seed parameter is documented: deterministic regeneration is **UNKNOWN**. [API reference](https://elevenlabs.io/docs/api-reference/text-to-sound-effects/convert)

`output_format` defaults to `mp3_44100_128`. The reference describes MP3, PCM/WAV and μ-law options, with subscription restrictions; the changelog lists WAV rates through 48 kHz. The capability guide specifically promises MP3 for all effects and 48-kHz WAV for non-looping effects. Starter access to every WAV/loop combination is **UNKNOWN**; begin with the existing MP3 format and decode locally. [API](https://elevenlabs.io/docs/api-reference/text-to-sound-effects/convert), [changelog](https://elevenlabs.io/docs/changelog), [capabilities](https://elevenlabs.io/docs/overview/capabilities/sound-effects)

Looping supports reusable ambience: generate a short bed and repeat it locally; the maximum single generation remains 30 seconds. The capability guide’s 0.1-second minimum conflicts with the endpoint’s 0.5: use **0.5**. [Capabilities](https://elevenlabs.io/docs/overview/capabilities/sound-effects), [API](https://elevenlabs.io/docs/api-reference/text-to-sound-effects/convert)

Exact SFX requests/minute and Starter concurrency are **UNKNOWN**. The published concurrency table identifies speech/STT/music limits, not an explicit SFX limit; do not transfer its “3” speech figure to SFX. [Limits](https://elevenlabs.io/docs/overview/models)

Good prompts describe the audible source, material, action, distance, environment and intensity; simple effects benefit from concise wording, and sequences should state event order. [Prompting guide](https://elevenlabs.io/docs/overview/capabilities/sound-effects)

Proposed example:

> Two people walking slowly on dry dusty earth, soft irregular footfalls, close perspective, outdoors; isolated footsteps, no speech, music, bells or modern traffic.

### Tags inside the speech script

**They can produce environmental effects—not only vocal expressions.** Official examples include:

- Vocal: `[laughs]`, `[whispers]`, `[sighs]`, `[crying]`.
- Environmental: `[gunshot]`, `[applause]`, `[explosion]`; the vendor’s tag guide also demonstrates `[footsteps]`, `[door creaking]` and `[thunder rumbling]`.

Tags are natural-language directions, not a closed guaranteed vocabulary. [Best practices](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices), [tag examples](https://elevenlabs.io/blog/elevenlabs-audio-tags-list)

Both **v3 and v4 support tags**. `eleven_v4` is the official expressive speech model, not a repository nickname; its documented language list includes Marathi and Hindi. [Tag support](https://elevenlabs.io/docs/help-center/product/core-capabilities/text-to-speech/how-do-audio-tags-work-with-eleven-v3-and-v4), [models](https://elevenlabs.io/docs/overview/models)

The vendor acknowledges imperfect tag following and ambiguity between delivery instructions and effects. Guaranteed six-second placement or matching environmental effects across Marathi/Hindi generations: **UNKNOWN**. [Best practices](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices)

### Commercial rights

Paid users may use outputs commercially, subject to applicable terms and prohibited-use rules. Sound Effects terms **explicitly permit incorporation into films**. They also prohibit standalone exploitation and making outputs available as isolated files or sound libraries. [General terms](https://elevenlabs.io/terms-of-use), [Sound Effects terms, Exhibit 4](https://elevenlabs.io/creative-terms)

Keep our pack private as production assets; distribute finished films. This is the proposed implementation boundary, not a verified exemption for external pack sharing. Contractor/cloud-library sharing permissions: **UNKNOWN**.

The help centre says commercial licences for material generated during a paid subscription continue after cancellation, but continued online file availability is not guaranteed. Download and preserve outputs and receipts. [Cancellation rights](https://elevenlabs.io/docs/help-center/account/general/what-happens-to-my-content-after-my-subscription-ends)

The repo’s music exclusion remains supported: the current Music Terms table excludes film on Starter and other listed self-service tiers. Broad marketing statements do not override that table. Sound Effects have separate terms expressly allowing film incorporation. [Music Terms, Exhibit A](https://elevenlabs.io/music-terms), [Sound Effects terms](https://elevenlabs.io/creative-terms)

### Cost estimates

Official pages conflict:

- Capability guide: **40 credits/second when duration is specified**. [Source](https://elevenlabs.io/docs/overview/capabilities/sound-effects)
- General pricing FAQ: approximately **200 credits/generation**. [Source](https://elevenlabs.io/pricing)
- API pricing: **$0.12/minute**; help says costs vary by platform/settings. These are different billing presentations, not interchangeable guarantees. [API pricing](https://elevenlabs.io/pricing/api), [billing explanation](https://elevenlabs.io/docs/help-center/product/core-capabilities/sound-effects/how-much-does-it-cost-to-generate-sound-effects)

Therefore, use conditional estimates, then reconcile actual charges:

- **25-sound pack**, assuming six 20-second beds plus nineteen 3-second effects: 177 generated seconds. At 40 credits/second: **7,080 credits**; two attempts each: **14,160**.
- At the approximate flat rate: `25 × 200 = 5,000 credits`; applicability to our API requests is **UNKNOWN**.
- **Illustrative later chapter:** two new 3-second effects: **240 credits** at the duration rate. Fully reused chapter: **zero new SFX-generation credits**.
- Speech: `Σ characters per submitted MR/HI line × applicable model/voice rate`; total chapter = speech + newly generated SFX + approved retakes. Exact v4 account rate: **UNKNOWN**. The repo’s one-credit/character calculation remains an estimate.

These are forecasts, not spending caps. Eighteen cue placements do not require eighteen generations.

## 4. DESIGN

### One method

Use **separate Sound Effects generation, mixed by our code**.

It gives one reusable environmental track, independent level/timing control and the same effects in both exports. Embedded effects would be attached to language-specific speech files and require speech regeneration to change them.

The strongest case for tags is convenience. Reconsider only if an owner-approved bilingual test demonstrates adequate timing, isolation and reuse. Keep environmental tags out of production speech requests; vocal direction requires a separate owner decision.

### Preset pack

Use `canon/series/sounds/palette.json`. Each record needs:

`id`, `version`, `kind`, `prompt`, requested/measured duration, `loop`, settings including prompt influence/output format, explicit model ID, estimated/actual credits and confirmation flag, receipt/request ID, file path, original/decoded SHA-256, creation date, rights-note URL/date/paid-plan evidence, approval reference, matching tags and status.

Statuses:

- **AVAILABLE:** file decodes, hashes match, rights basis recorded, owner accepted.
- **NEED_NEW:** missing or awaiting generation/approval.
- **REJECTED:** retained for evidence, never selected.

Keep existing `bed_*`/`fx_*` IDs; filenames such as `fx_plate_set_down__v001.mp3`. Never overwrite accepted versions. Pin the palette version/hash and selected asset versions per chapter.

Code loads the latest approved palette summary and animation capabilities into Kimi’s packet. Kimi returns an existing ID/version, or NEED_NEW with purpose, source/STAGING basis, symbolic anchor and sound prompt. **Kimi supplies no numeric timing or paid-call settings**; code applies approved settings.

Deduplicate by canonical prompt/model/settings/output-format request hash. Reserve credits, submit once, decode/check/hash, retain the candidate and receipt, then obtain listening approval before AVAILABLE. On timeout or uncertain charge, stop for reconciliation; “once” cannot guarantee remote exactly-once execution.

### Stage 1 rules and starting map

Suggest sounds only for supported events or explicitly labelled staging. No invented dialogue, ceremonies, crowds or miracles. No music, automatic blessing chime, halo sound or transition whoosh. Silence is valid.

Use the existing 18 cues as the starting map:

- C1/C4/C6/C10, roadside establishes/holds → `bed_roadside_quiet`.
- C2/C8, feast → `bed_courtyard_feast_murmur`.
- C11/C17, noon → `bed_village_noon_heat`.
- C3 leaf plates → `fx_leaf_plate_rustle`; C5 walking → `fx_footsteps_road_dust`.
- C7 bow → `fx_cloth_bow_rustle`; C9 plate placement → `fx_plate_set_down`.
- C12 birds → `fx_birds_flutter_to_trees`; C13 door → `fx_door_wood_creak`.
- C14 cattle → `fx_cattle_distant`; C15 drinking → `fx_water_trough_drink`.
- C16 pot → `fx_brass_pot_clink`; C18 departure → `fx_wind_rush_run`.

C13/C16 remain staging proposals. C18 requires listening review: avoid a supernatural whoosh.

The other nine proposals remain NEED_NEW until needed: morning/interior/well-and-cattle beds; gourd tap, well bucket, distant crowd, soft gust, cow bell and sandal steps. Do not invent three additions merely to reach 25.

Camera/animation presets trigger no sound automatically. Teaching/reaction defaults to silence or an appropriate quiet location bed.

Code resolves scene/line/event anchors after measurement. “After line” means after **both** language windows; effects crossing speech must duck against their union, including speech continuing across cuts. Proposed listening-test settings: 12 dB attenuation, 100 ms attack, 300 ms release; owner approval pending. Otherwise move, mute or reject the cue.

### Synthetic validation and owner checks

Test invalid IDs/statuses, missing evidence, forbidden timings/script edits, malformed NEED_NEW, parameter bounds, request deduplication, concurrent reservations, interrupted/ambiguous calls, corrupt audio/hash changes and stale approvals.

Test unequal bilingual speech, cross-cut narration, insufficient gaps, loop seams, fades, clipping, unchanged speech samples, identical shared effects and equal export lengths.

Owner checks: actual billing/rates, accepted formats, pack-sharing interpretation, sound quality, ducking/loudness and Hindi release approval.

## 5. FILE CHANGES AND MERGE CHECKLIST

All unchecked. Each entry gives file, responsibility, owner decision and done-test. Claude writes specs/docs; Nemotron writes **all code/tests**; Codex reviews.

1. **Rules:** `docs/DECISIONS.md`, `DECISION_LOG.md` — Claude; owner: yes; test: dated sound decision recorded.
2. **Stage 1:** `STAGE1_RULES.md` — Claude; owner: yes; test: selection/NEED_NEW limits explicit.
3. **Contracts:** `PIPELINE_README.md`, `FINAL_ARCHITECTURE_PLAN.md` — Claude; owner: yes; test: inputs, outputs and gates agree.
4. **Historical advice:** `CODEX_ONE_VIDEO_TWO_LANGUAGES.md`, `BRIEF_elevenlabs_restructure.md` — Claude; owner: no; test: dated supersession notes.
5. **Pack:** `canon/series/sounds/palette.json`, `a1_audio_spec.py` — Nemotron; owner: assets; test: 22 IDs/18 cues preserved.
6. **Schemas/prompts:** `schemas/`, `stage1_prompts.py`, `validate_stage1.py` — Nemotron; owner: contract; test: forbidden-output fixtures fail.
7. **Generation:** `a1_eleven.py` — Nemotron; owner: spending; test: mocked SFX requests/resume/ledger pass.
8. **Timing:** `a1_audio.py` — Nemotron; owner: timing; test: bilingual anchors and collision checks pass.
9. **Mix:** `a1_voice.py` — Nemotron; owner: listening settings; test: ducking, peaks, seams and speech integrity pass.
10. **Migration:** `canon/audio/*` — Nemotron; owner: approvals; test: accepted speech preserved, stale labels reconciled.
11. **Review:** focused synthetic tests and receipts — Codex; owner: no; test: independent read-only acceptance review.
12. **Proof/checklist:** `CHECKLIST_BUILD_PIPELINE.md` — Claude; owner: both exports; test: interruption/resume and bilingual listening pass.

## 6. EXACT DECISIONS.MD SECTION TEXT

### Sound planning and generation

Kimi Stage 1 plans sound from the supplied, versioned sound palette and animation preset capabilities. It selects approved AVAILABLE sound IDs or emits NEED_NEW with a sound-effect prompt, purpose, source/STAGING basis and symbolic anchor. The owner’s EASY Marathi/Hindi speech script remains unchanged. Kimi writes no timings or paid-call settings.

ElevenLabs generates separate effects and ambience files through the existing credit ledger. Code deduplicates requests, submits once, records settings, credits, receipts and hashes, and stops on uncertain results for reconciliation. Owner-accepted files join the private production palette and are reused across Adhyays. No ElevenLabs music or environmental effects embedded in TTS are used.

Code resolves cues from measured bilingual timing and ducks overlapping sounds against the union of both speech windows. No automatic halo/chime/whoosh or invented event is permitted. Both videos use the same picture and environmental cues. Film incorporation is permitted subject to the paid-plan terms; isolated pack distribution is restricted. [Sound Effects terms](https://elevenlabs.io/creative-terms)

Claude writes specifications/documentation, Nemotron all code/tests, and Codex reviews. Adhyay 1 paid planning and accepted speech are not regenerated.

---

No generation, listening or runtime tests were performed. Account-specific billing, output quality and external pack-sharing rights remain unverified.