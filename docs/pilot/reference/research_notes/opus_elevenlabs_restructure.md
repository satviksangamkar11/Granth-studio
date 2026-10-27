# ElevenLabs restructure of the GranthStudio audio side (research only; reviewer: Claude Opus)

Date: 2026-10-26. Scope: the brief `docs/pilot/BRIEF_elevenlabs_restructure.md` plus its ADDENDUM (audio entirely on ElevenLabs, speech + character voices + sound effects + optional music; the picture/Kimi side is settled and out of scope) and the DEBATE RULE. Nothing was run, bought or called. No repository file except this one was changed.

Labels used throughout: **[V]** verified on an ElevenLabs page on 2026-10-26 (URL given); **[C]** vendor claim (ElevenLabs says it, nothing independent); **[I]** my inference; **[U]** unverified or contradictory. All URLs accessed 2026-10-26.

---

## 1. Executive summary (one page)

**Position.** Adopt ElevenLabs for ALL audio, but through the **API from our own scripts**, with **our own numpy/ffmpeg mix as the final assembly**, and buy the **Starter monthly plan** (not Creator, not annual) only AFTER a free-tier test passes. Upgrade to Creator for one month only if a measured shortfall appears (credits, or an audible 128 kbps problem). Never use Dubbing for the film. Lock the voices BEFORE the paid Kimi director run, because the director consumes the measured timing.

**Why this, concretely.**
1. **Marathi is listed** for Eleven v3 and Eleven v4 (code `mr`) and NOT for Multilingual v2 / Flash v2.5 [V, models page]. Hindi is in all of them. So the only usable models are **`eleven_v4`** (released 28 Sep / 7 Oct 2026, very new) and **`eleven_v3`**. Marathi speech-to-text (Scribe v2) is in the "High Accuracy" tier, 5-10 % WER [V]. Marathi Dubbing exists [V]. **Marathi quality is NOT proven anywhere independent**: every Marathi quality statement I found is vendor or reseller marketing [C].
2. **Money is not the issue.** The whole film's audio (speech with three takes, 22-33 sounds with re-takes, a little music, speech-to-text QA) costs roughly **$15-20 at the published API rates**, or about **130-165k website credits** [I, section 5]. Starter is $6/month; Creator $22/month [V]. The real costs are integration work (about 1-2 days of Claude code + Codex reviews) and re-locking timing.
3. **The API billing question (owner's pasted summary) is mostly right.** ElevenLabs' own API pricing page says "API usage is billed in US dollars, not credits", lists v4 $0.08 / 1K chars, v4 Turbo and Flash $0.04, Scribe v2 $0.22 / hour, Sound Effects $0.12 / minute, Music $0.15 / minute, Dubbing v1 $0.33-0.50 and v2 $2.20 per minute, and a "Free / Pay as you go" tier [V, pricing/api]. BUT: the billing doc says API calls draw from the same credit pool as the website [V, billing], the API page also shows subscription API plans (Starter $6 includes 75,000 v4 characters) [V], and **whether pay-as-you-go WITHOUT a paid subscription carries a commercial licence is not stated**; the help centre says content "created outside of a paid subscription (before or after) cannot be used commercially" [V]. So: **PAYG-only is cheaper by a few dollars but legally unsafe for a published film; Starter is the safe floor.**
4. **What disappears:** the Kaggle TTS job, the HF gated-model token and its "only page-started runs see the secret" trap, the Kaggle dataset/kernel push, the 22-sound sourcing and URL+licence log (replaced by a generation provenance record), and the two-male-Hindi-voice limit (one designed voice per character can speak both languages [I, to test]).
5. **What stays exactly the same:** owner approval gates; exact-text rule (characters speak only exact Marathi words, A3(7)); no invented dialogue; Hindi stays NOT VALIDATED (ElevenLabs does not validate a translation); D-017 renderer; one video, two audio tracks; shots = ceil(common timeline / 6 s) from MEASURED decoded audio; ledger-style spend guard before every paid call.
6. **New stages:** ElevenLabs job builder + runner (stdlib `urllib`, no new dependency), ingest reusing `a1_voice.py ingest`, per-clip provenance (text, text hash, voice id, model id, settings, seed, output format, response alignment, audio hash), a separate ElevenLabs spend cap in the ledger, a sound-effects generator + owner pick sheet, an M&E (music and effects) bed in our mixer with deterministic ducking, Scribe back-transcription as an advisory word check.
7. **First step (free, this week):** 8 lines x 2 languages x 2 models (v3, v4) on the free tier + 3 sound-effect prompts, about 6-7k of the 10,000 free credits [I]. Owner listens blind against Parler. Pass criteria in section 9. Only then the owner buys Starter.

**Strongest objections (section 8):** Marathi sacred-verse quality is unproven and v4 is a month old; Parler voices exist already and the owner has not even listened yet; prices and rates visibly drift (the per-second sound-effect rate appears as 11, 20 and 40 credits in different versions of ElevenLabs' own docs); designed voices are account-bound and the Default voices expire on 31 Dec 2026 [V]; nondeterminism means a re-take is never byte-identical. Evidence that would change my mind is listed there.

---

## 2. Facts gathered (with sources)

### 2.1 Plans (https://elevenlabs.io/pricing, accessed 2026-10-26)
| Plan | Price/month | Credits/month | Notes [V unless marked] |
|---|---|---|---|
| Free | $0 | 10,000 | no commercial licence; published content must credit "elevenlabs.io" in the title (help centre, 2.6); 2 concurrent |
| Starter | $6 (promo: $1 first month "until Nov 1") | 30,000 | commercial licence; Instant Voice Cloning; 10 voice slots; 3 concurrent; 128 kbps / 44.1 kHz; Studio 20 projects; Dubbing Studio |
| Creator | $22 ($11 first month) | 121,000 | Professional Voice Cloning; 30 slots; 5 concurrent; 128 and 192 kbps |
| Pro | $99 | 600,000 | 10 concurrent; "44.1 kHz PCM via API" |
| Annual | 10 x monthly | | not useful for a one-off film [I] |

- Rollover: unused credits roll over up to two months while the subscription stays active; **not** rolled over after a downgrade or cancellation; cancel takes effect at the end of the cycle; account then returns to Free [V, https://elevenlabs.io/docs/overview/administration/billing.md].
- Overage: usage-based billing is "no longer offered on new self-serve subscriptions"; extra usage = pay-as-you-go top-ups that last 12 months, stored as dollar values [V, billing].
- Brief's "~1 credit per character": confirmed for Eleven v3 **on the website**; "API generations are discounted" [V, https://elevenlabs.io/docs/help-center/product/core-capabilities/text-to-speech/how-much-does-it-cost-to-generate-using-eleven-v3-alpha.md].
- Website credit costs (pricing FAQ): sound effect 200 credits per generation; speech-to-text 330/min; music 900/min; Automatic dubbing 2,000 (watermark) / 3,000 per minute; Dubbing Studio 5,000 / 10,000 per minute; Voice Changer and Voice Isolator 1,000/min [V, https://elevenlabs.io/pricing?price.section=sound_effects]. Voice Design cost: not listed [U].

### 2.2 API pricing (https://elevenlabs.io/pricing/api, accessed 2026-10-26)
- "API usage is billed in US dollars, not credits" [V]. A "Free / Pay as you go" tier, "No commitment, cancel anytime" [V]. Minimum top-up: not stated [U].
- TTS per 1K characters: v4 $0.08, v4 Turbo $0.04, v3 $0.08, v3 Conversational $0.04, Multilingual v2 $0.08, Flash/Turbo $0.04 [V].
- Scribe v2 $0.22 per hour (keyterm prompting +$0.05/h) [V]. Forced alignment: not listed on this page; the forced-alignment doc says its price matches speech-to-text [V].
- Sound effects $0.12 per minute in the table, but the FAQ says sound effects are "billed per generation": **the unit is inconsistent on the page** [U].
- Music $0.15/min; Dubbing v1 $0.33 (watermark) / $0.50, v2 $2.20 per minute; Voice Changer $0.12/min; Voice Isolator $0.12/min [V].
- Subscription API plans: Starter $6 includes 75,000 v4 characters, Creator $22 includes 275,000 [V for Creator, my row matching for Starter is an inference from the order of rows, I]. 30,000 credits ≈ 75,000 API characters implies about 0.4 credit per API character [I].
- Commercial licence is stated only for Music ("Starter+"); sound effects are called "Royalty-free" [V]. The page does not say whether PAYG-only output is commercially licensed [U].

**Reconciling the owner's pasted third-party summary:** model names v4 / v4 Turbo / Flash v2.5 / Scribe v2 / Dubbing v1 and v2 exist; the dollar rates match ElevenLabs' own page; "zero-retention option" exists only for select Enterprise customers ("Zero Retention Mode (Enterprise)", https://elevenlabs.io/docs/eleven-api/resources/zero-retention-mode) [V], so it is NOT available to us. "Credits vs dollars" is not a contradiction: website = credits, API = dollars or the subscription's included API amount [V/I].

### 2.3 Models and Marathi (https://elevenlabs.io/docs/overview/models)
- `eleven_v4`: "state of the art", 90+ languages, 10,000 characters per request, multi-speaker dialogue; list includes "Marathi (mr)" [V]. Launch 28 Sep 2026 per press (https://datanorth.ai/news/elevenlabs-releases-eleven-v4-and-eleven-v4-turbo), OpenRouter lists 7 Oct 2026 [U on the exact date].
- `eleven_v3`: "previous generation", 70+ languages, 5,000 characters, includes "Marathi (mr)" [V].
- `eleven_multilingual_v2` (29 languages) and `eleven_flash_v2_5` (32): Hindi yes, **Marathi no** [V].
- No model on the page is labelled alpha/beta; deprecated: turbo v2/v2.5, scribe v1 [V]. (The v3 help URL still contains "alpha", so v3's label changed at some point [V/I].)
- TTS is "nondeterministic"; `seed` gives best-effort determinism, "subtle differences may still occur" [V, https://elevenlabs.io/docs/capabilities/text-to-speech].
- TTS `/with-timestamps` returns per-character `character_start_times_seconds` / `character_end_times_seconds` for the input text plus `normalized_alignment` [V, https://elevenlabs.io/docs/api-reference/text-to-speech/convert-with-timestamps]. Request parameters: `language_code` (ignored if unsupported), `voice_settings` (stability, similarity_boost, style, speed, use_speaker_boost), up to 3 `pronunciation_dictionary_locators`, `seed`, `previous_text`/`next_text`, `apply_text_normalization` [V]. **Whether v4 returns alignment for Marathi is not stated** [U, test it].
- Text-to-Dialogue `/with-timestamps` exists (default `eleven_v3`, up to 10 voices, ~2,000 characters) with `voice_segments` [V, https://elevenlabs.io/docs/api-reference/text-to-dialogue/convert-with-timestamps]. Not needed: our lines are single-speaker [I].
- Controls (https://elevenlabs.io/docs/best-practices/prompting/controls) [V]: "Eleven v4 and Eleven v3 do not support SSML break tags"; SSML phoneme tags only with `eleven_flash_v2`; pronunciation dictionaries support phoneme (IPA/CMU) and **alias** rules, are case-sensitive, first match wins, work in Studio, Dubbing Studio and the API; v4 accepts inline IPA in slashes; speed 0.7-1.2; audio tags like `[whispers]` (v3/v4), "some experimental tags are less consistent". **No non-English guidance**; whether IPA or alias rules work on Devanagari words is not stated [U].
- Forced alignment: languages = the 29 Multilingual v2 languages, which **excludes Marathi** [V, https://elevenlabs.io/docs/capabilities/forced-alignment]. So for Marathi we would use the TTS response's own alignment or Scribe's word timestamps, not the forced-alignment API [I].
- Scribe v2: 90+ languages, word-level timestamps, diarization, keyterm prompting; Marathi and Hindi both in "High Accuracy (>5 % to ≤10 % WER)" [V, https://elevenlabs.io/docs/capabilities/speech-to-text]. A vendor page cites 5.6 % WER on Marathi FLEURS for Scribe v1 [C, https://elevenlabs.io/speech-to-text/marathi].

### 2.4 Voices (https://elevenlabs.io/docs/capabilities/voices)
- Voice Design: v4 recommended; description 20-1,000 characters, 3 previews per design; which languages Voice Design covers is not listed [V/U].
- Voice Library: 10,000+ community voices; "not available via the API to free tier users" [V]. Removed shared voices stay usable for the notice period (help pages give a minimum of 30 days or 3 months, maximum 2 years: contradictory) and outputs made before removal stay usable [V/U, https://elevenlabs.io/docs/help-center/product/voices/voice-library/what-is-a-notice-period].
- **Default voices "will expire on December 31, 2026"** [V]. Do not build the film on Default voices.
- Professional Voice Cloning uses voice-captcha verification of your own voice [V]. The use policy bans cloning a living person's voice "without their explicit and informed consent" and any deceased person "in a manner that is reasonably likely to cause harm" [V, https://elevenlabs.io/use-policy]. No clause about religious content; the hate section bans attacks on protected groups [V]. We clone nobody (A3(13): no owner recording) [I].

### 2.5 Sound effects (https://elevenlabs.io/docs/capabilities/sound-effects, https://elevenlabs.io/docs/api-reference/text-to-sound-effects/convert)
- Duration 0.5-30 s via API (`duration_seconds`; the product doc says 0.1-30 s) or automatic when unset [V; the two pages disagree on the minimum, U].
- `loop` (boolean): "a sound effect that loops smoothly"; the doc suggests generating 30 s and looping for longer ambience [V].
- `prompt_influence` 0-1, default 0.3 (higher = more literal, less varied) [V].
- `model_id`: `eleven_text_to_sound_v2` (default) or `eleven_text_to_sound_v3` [V]; v3's status and differences are not documented on these pages [U].
- `output_format`: mp3_44100_128 default; mp3_44100_192 needs Creator+; "PCM and WAV at 44.1 kHz require the Pro tier"; the capability page says WAV 48 kHz is available for non-looping effects [V] (which tier may request `wav_48000` is unclear, U).
- Cost: website 200 credits per generation (4 variations per generation on the website per a help-article version) [V/U]; per-second rate when duration is set appears as **11, 20 and 40 credits per second** in different versions of ElevenLabs' pages; the current capability page says 40 [V that the versions disagree].
- Prompting tips: concise descriptions; describe sequences in order; terms like ambience, one-shot, loop, whoosh, drone [V].
- Licence: royalty-free per the API page; covered by the paid-plan commercial licence; content from Beta Services "cannot be used for any commercial purpose" [V, https://elevenlabs.io/docs/help-center/legal/can-i-publish-the-content-i-generate-on-the-platform.md]. Whether `eleven_text_to_sound_v3` counts as Beta is not stated [U].

### 2.6 Rights and terms
- Paid-plan content can be used commercially "indefinitely", subject to the Service-Specific Terms; Beta Services excluded; content made before or after a paid subscription cannot be used commercially [V, help centre link above]. So **everything that goes into the film must be generated during a paid month** (free-tier test clips are throwaway) [I].
- Do not strip ElevenLabs watermarks/metadata/provenance signals; disclose AI use where the law requires or where not disclosing would materially mislead [V, use policy]. A devotional film narrated by synthetic voices should say so in its description/credits [I, owner's call].
- The Granth's rights (Sansthan) are a separate, existing open item (NEXT_STEPS D3) that ElevenLabs does not change [I].

### 2.7 Music (https://elevenlabs.io/docs/capabilities/music)
3 s to 5 min; vocals or instrumental; MP3 44.1 kHz 128-192 kbps and WAV; "cleared for nearly all commercial uses" including film; Starter+ for commercial use [V]; models `music_v2_5`, `music_v2` [V]. Quality for Indian devotional idioms (tanpura, harmonium, bhajan) is unknown [U].

### 2.8 Dubbing (https://elevenlabs.io/docs/capabilities/dubbing)
Marathi and Hindi supported in v1 and v2 [V]; Dubbing Studio (v1) is "in maintenance mode", "critical bug fixes only"; transcript editing via API for v2 is Enterprise-only [V]. Dubbing translates the source speech; our Hindi wording is the owner's text [I].

### 2.9 Not found / could not verify
API concurrency per plan beyond the pricing table (the rate-limit doc URL returned 404); India-specific availability, INR pricing or GST; whether Designed voices survive a cancelled subscription; whether the API response carries a per-request character-cost header; whether alias dictionaries match Devanagari; v4 Marathi alignment; any independent Marathi TTS evaluation of v3/v4.

---

## 3. Question 1: which features replace or shorten our steps

| Feature | Use it? | Replaces / shortens | Why / caveat |
|---|---|---|---|
| TTS `eleven_v4` (and `eleven_v3` as A/B) | **YES (pending test)** | Kaggle Parler job, HF token, dataset/kernel push, page-only runs | Only models with Marathi [V]. Choose by the free test, not by the vendor's "state of the art" label. |
| Multilingual v2 / Flash v2.5 | NO for Marathi; maybe Hindi | | No Marathi [V]. Mixing models across languages changes voice timbre between tracks [I]; prefer one model for both. |
| Voice Design (one voice per character, used for BOTH languages) | **YES** | Parler speaker-name + description hack; the "Aman for two characters" problem | Voices are generated, so no consent issue [I]. Must be saved to our account; record voice_id. Don't use Default voices (expire 31 Dec 2026) [V]. |
| Voice Library voices | Avoid for main characters | | Removable with a notice period [V]; owner of the voice can withdraw. Acceptable only for a minor voice with outputs saved. |
| Instant / Professional cloning | NO | | No consented recording exists; A3(13) says no owner recording [I]. |
| `/with-timestamps` character alignment | **YES, as secondary data** | Nothing removed: decoded-wav duration stays the authority | Gives speech start/end inside each clip (trims leading/trailing silence for tighter beats) and caption timing; flags truncated clips (last aligned char ends early) [I]. |
| Forced-alignment API | NO for Marathi | | Marathi not supported [V]. |
| Pronunciation dictionary (alias rules) | YES, only if the test shows mispronounced names | | Alias = respelling, so it never changes the on-screen or canonical text [I]. Devanagari support U. Store the dictionary version id per clip. |
| Inline IPA (v4) / audio tags | Sparingly | | Tags can be read aloud or as sounds [V]; verse narration needs none. A tag inside the text breaks the exact-text rule unless it is stripped from the canonical text and recorded separately [I]. |
| SSML `<break>` | NO | Our `prep_text` comma pauses | Not supported on v3/v4 [V]. Use line-level gaps in the mixer (already `PAUSE`). |
| `speed` 0.7-1.2 | YES, per voice, fixed | | Must be a recorded setting; never used to squeeze lines into shots (owner rule: never speed speech to fit) [I]. |
| Speech-to-speech / Voice Changer | NO | | Needs a human recording [I]. |
| Dubbing (auto or Studio) | **NO for production** | | Translates audio instead of speaking the owner's Hindi wording; Studio is in maintenance mode; API transcript editing Enterprise-only; 2,000-10,000 credits/min [V]. At most a curiosity comparison, never canon. |
| Sound Effects generator | **YES** | Sourcing 22 files + licence-checking + URL logging | See section 6. Provenance replaces licence URLs. |
| Music generator | Optional, small | | Instrumental drone/intro only; owner taste decides (section 6.6). |
| Scribe v2 speech-to-text | YES, advisory | Part of the listening burden | Back-transcribe every clip, diff against the input text, list mismatches for the owner. 5-10 % WER tier means it flags, it never certifies [V/I]. Do NOT use keyterm prompting for QA: it biases the transcript toward the expected names [I]. |
| Studio / Projects | NO | | Our manifest/timing/two-track mux is code; a UI project is not reproducible or diffable [I]. |
| Dubbing Studio as assembler | NO | | Same reason; plus it would re-time speech [I]. |
| API vs UI | **API** for production; UI only for the free test and for designing voices | | API keeps text hashes, settings and outputs in our receipts [I]. Voice Library via API is not available on Free [V]. |
| Concurrency | 1-3 parallel calls | | Starter allows 3 [V]; 124 clips are minutes of work, so sequential is fine and simpler for the ledger [I]. |
| Batch | None needed | | No documented batch TTS endpoint found [U]; a loop is enough. |

---

## 4. Question 2: language quality risk and the cheapest decisive test

**Evidence that Marathi is good enough for sacred verse: none independent.** What exists: the model page lists Marathi for v3/v4 [V]; marketing pages promise "clear, high-quality" Marathi [C, https://elevenlabs.io/text-to-speech/marathi]; resellers repeat it [C]; Scribe's Marathi WER tier [V] is about recognition, not synthesis. v4 is about one month old [V/U on date]. Specific risks [I]: Sanskrit inside Marathi verse (`"अन्नम् ब्रह्मेति"`, `’अन्नपरब्रह्म’`), archaic verse forms (`साचार`, `जाहले`, `तें`), the schwa-deletion differences between Marathi and Hindi (a multilingual model may read Marathi with Hindi phonology), names (`गजानन`, `देविदास`, `बंकटलाल आगरवाला`, `दामोदरपंत कुलकर्णी`), the danda and nukta handling, and silent word drops or repeats (a known failure class of neural TTS).

**Settle it on the free tier (website, 10,000 credits, no commercial use, nothing kept for the film):**
- Lines (exist in `canon/audio/A1_audio_plan.json`; 8 lines cover all four voices, names, Sanskrit, long narration, a teaching): `S1-L1` (narrator, long), `S2-L4` (names + `बंडी`), `S2-L9` (Upanishad quotation), `S3-L2` (`दामोदरपंत कुलकर्णी`), `S3-L7` (Bankatlal), `S7-L6` (Damodarpant), `S9-L4` (Maharaj teaching), `S9-L8` (the run). About 640 Marathi + 650 Hindi characters in the verse wording [measured from the plan file]; the simple wording is about 12 % longer.
- Runs: both languages x {v4, v3} with one designed voice per character = about 2,600-2,900 characters; voice design previews (cost unknown, budget about 2,000); 3 sound-effect prompts at 200 = 600; total about 5,500-6,500 of 10,000 [I].
- Owner listens BLIND: each line as Parler (existing clip), v3, v4 in shuffled order (file names A/B/C; the key kept by code).
- Code checks: Scribe transcript of each clip diffed against the input; alignment end vs decoded length; two identical requests with the same seed compared by hash (measures reproducibility).

---

## 5. Question 3: plan sizing (credits and dollars)

Measured inputs (from the repository): verse-wording script = 62 lines, Marathi 4,088 + Hindi 4,154 = **8,242 characters** (core only 6,631); owner's simple script = Marathi 4,639 + Hindi 4,592 = **9,231 characters**. Picture 366 s. Adhyay 2 has no text yet; the film target is 10-20 min, so A2 is assumed at 1.0-2.0 x A1 [I].

Assumptions [I]: 3 full-pass equivalents of speech (first pass + re-takes + one voice change); voice design 4 characters x ~5 attempts; sound effects = full palette (6 beds as 30 s loops, 16 effects) x 3 candidate rounds; music 3 min per pass x 2; Scribe QA 2 passes over ~11 min of A1 speech.

| Item | Adhyay 1, website credits | Adhyay 1, API dollars |
|---|---|---|
| Speech 3 x 9,231 chars | 27,700 (1 credit/char) | $2.20 ($0.08/1K) |
| Voice design | ~5,000 [U price] | [U] |
| Sound effects: beds 6 x 30 s x 40 cr/s = 7,200; effects 16 x 200 = 3,200; x3 | 31,200 | ~$3-6 (3-4 min of audio per round x 4 candidates x 3 at $0.12/min; unit U) |
| Music 2 x 3 min | 5,400 | $0.90 |
| Scribe QA 2 x 11 min | 7,300 | $0.08 |
| **Total A1** | **~77,000** | **~$7-10** |
| Adhyay 2 (1-2 x speech, +50 % new sounds) | ~53,000-86,000 | ~$6-10 |
| **Whole film** | **~130,000-165,000** | **~$13-20** |

What this means:
- **Website-credit route:** Starter's 30,000 cannot hold Adhyay 1 in one month; Creator's 121,000 holds A1, and two Creator months (with rollover) hold the film: about $33-44 [I].
- **API route:** Starter's included API amount (75,000 v4 characters = ~$6 of API usage [I]) covers A1's speech three times; sound effects and music add a few dollars of top-up. Two Starter months + top-ups ≈ $12-25 [I]. **PAYG without any subscription** ≈ $13-20 total but the commercial licence for PAYG-only output is not stated [U] while the help centre ties commercial use to a paid subscription [V]: **not safe for a published film**.
- **Which plan:** Starter monthly via the API for the production months; Creator for one month only if the test shows 192 kbps is audibly needed for sound effects (speech at 128 kbps is very unlikely to be the weak link [I]) or credits run short. Pro ($99) only if lossless 44.1 kHz WAV is demanded; a lossless check: request `pcm_24000` for speech on Starter (the docs restrict only 44.1 kHz PCM to Pro [V]; 24 kHz is ample for speech [I]).
- **Annual:** no. **Rollover:** helps across two active months only; lost on cancel/downgrade [V]. **Overage:** PAYG top-ups, valid 12 months [V]. **Watermark:** only Dubbing on free/discount modes [V]; TTS and SFX carry no audible watermark that I found, but provenance metadata must not be stripped [V]. **After the plan lapses:** outputs made during the paid period stay commercially usable indefinitely [V]; new generations after lapse are not commercial [V]; whether designed voices remain usable on Free is unknown [U] (so finish all re-takes before cancelling).

---

## 6. Sound effects and the full soundtrack (ADDENDUM)

### 6.1 What we have
`scripts/source/a1_audio_spec.py`: PALETTE of 22 sounds (6 beds, 16 effects, several marked "growth"); CUES C1-C18 with anchors `scene_bed | picture_event | before_line | after_line`, label `verse-named | STAGING`. Rule: never over a spoken line.

### 6.2 Prompt construction (deterministic, from the palette; no free-text sound design by any model)
Template [I]: `"{description}. Rural Maharashtra village, late 19th century. {kind_suffix} No music. No human voices or speech. No modern sounds (engines, electricity hum)."`
- beds: `kind_suffix = "Continuous ambience, seamless loop."`, `loop=true`, `duration_seconds=30`, `prompt_influence=0.5`.
- effects: `kind_suffix = "Single one-shot sound, close and dry."`, `loop=false`, duration unset (auto) or the palette's expected length, `prompt_influence=0.6-0.7` for literal results.
- murmur beds (`bed_courtyard_feast_murmur`, `fx_distant_crowd_murmur`) are the riskiest: generated "crowd" may contain pseudo-words in a wrong language [I]. Ask for "indistinct, far-off", and the owner must listen for intelligible words.
- Every prompt string, model id, parameters, output format, request time, plan tier and audio sha256 are written to `canon/audio/A1_sfx_sources.json` (the licence evidence replaces URL+licence); the palette id stays the key so the director's cue list does not change.

### 6.3 Candidates and choice
3-4 candidates per sound; a generated listening sheet; the owner picks one per palette id; the pick is recorded with its hash. Same approval pattern as voices [I].

### 6.4 Mixing (our own mixer, extended)
- **Stems:** `dialogue_mr`, `dialogue_hi`, and one shared **M&E** stem (beds + effects + music). Because every beat window is the LONGER language and lines start at the same beat start (`a1_audio.timing`), an `after_line` cue placed at the beat-window END and a `before_line` cue at the beat START land at the same time in both languages: **one M&E for both tracks** [I, follows from the existing timing code].
- **Ducking:** deterministic gain automation in numpy, not a sidechain compressor: beds -12 dB (assumed starting value, owner tunes) under every speech window with 300 ms ramps; effects are only placed in gaps (the existing `busy` window check rejects overlaps) [I].
- **Loudness:** two-pass ffmpeg `loudnorm` on each final language mix to one target, e.g. -16 LUFS integrated, -1.5 dBTP [I: common online-delivery convention, not an ElevenLabs fact; a broadcast master would use -23 LUFS EBU R128]. Both tracks get the same target so switching tracks does not jump in level.
- **Format:** the current mixer writes mono 16-bit 44.1 kHz and rejects anything else; ElevenLabs outputs mp3 (or PCM 24 kHz on Starter) [V], so ingest must decode/resample with ffmpeg to the mixer's format; final film audio 48 kHz stereo AAC is the usual video convention [I].
- **Mux:** one MP4/MKV: `-map 0:v -map 1:a -map 2:a`, `-metadata:s:a:0 language=mar`, `-metadata:s:a:1 language=hin` [I, standard ffmpeg]. Whether the publishing platform shows two tracks is a publishing question (YouTube's multi-language audio availability per channel is U); fallback is two uploads from the same picture.

### 6.5 Final assembly choice
**Our numpy/ffmpeg mix**, not Studio/Dubbing Studio: ours is deterministic, hash-recorded, already enforces "never over a spoken line", builds both tracks from one timing plan, and Dubbing Studio is in maintenance mode [V]. Studio would re-introduce manual, unrecorded timing [I].

### 6.6 Music in a devotional film
Fits as (a) a short instrumental intro/outro under titles and the 1878 caption, (b) a very low tanpura-style drone between scenes; NOT under verse narration by default (it competes with the words of a sacred text) [I, owner's taste]. Eleven Music is cleared for film on Starter+ [V]; whether it renders Indian classical/devotional instruments convincingly is U; test one 30 s prompt during the paid pilot before planning more.

### 6.7 How ElevenLabs timing feeds shot budgets
Unchanged formula: shots per scene = ceil(common timeline / 6 s), common beat = longer language [V in repo]. New: duration per clip = decoded wav length (authority, as today); the alignment gives the speech span so leading/trailing silence can be trimmed consistently [I]. Any re-take that changes a duration flows through the existing `a1_audio.py build --measured` -> `story_split.py revise` route. **Hence voices must be locked before the paid Kimi director run** (the director receives exact shot counts and the narration timeline).

---

## 7. Question 4 and 5: restructure, time and money

### 7.1 Stages
| Stage | Fate |
|---|---|
| Kaggle TTS job (`a1_voice.py package`, `scripts/audio/a1_tts_run.py`, dataset + kernel push, page-only Save & Run, output download) | **Disappears** for production; code kept frozen as the documented fallback (do not delete). |
| HF gated-model token as a Kaggle secret | **Disappears** (replaced by one ElevenLabs API key read at run time from an env var or the owner's key file under `D:\aai work\secrets`, never opened by an assistant; D-012(c1)). |
| `a1_voice.py ingest` (hash verify, re-measure, listening sheet) | **Stays**; the ElevenLabs runner writes the same manifest schema (`lines[]` with id, lang, speaker, voice, text, text_sha256, seed, wav, seconds, wav_sha256) plus new provenance fields, so ingest needs only small additions. |
| Estimated-vs-measured timing | Already measured; **stays** measured. |
| Hindi review burden | **Unchanged**: Hindi stays NOT VALIDATED (A3(14)); Scribe diff catches dropped words only. |
| Sound sourcing + licence log | **Replaced** by generation + owner pick + provenance JSON. |
| Director's sound-cue list | **Unchanged** (closed palette ids). |
| Which script is spoken | **Owner decision needed**: the owner's simple script (`A1_full_script_simple.md`) is not wired in and conflicts with A3(7) for character lines (characters speak only exact Marathi words). A DECISIONS.md amendment must say which wording each voice line uses. |

### 7.2 New stages (small, no new dependencies)
1. `scripts/audio/el_client.py`: stdlib `urllib`, no-redirect opener (same pattern as `kimi_adapter.py`), key from env/secret file, scrubbed from every log.
2. Spend guard: reuse `scripts/image_trials/v5_ledger.py` `Ledger` with a new phase (e.g. `EL1`) and a character-priced cost function; separate cap set by the owner (it must NOT eat the $50 Kimi cap of D-015). Reserve the worst case (characters x rate, or 30 s x rate for SFX) before the call; settle by reading the subscription usage before/after each serial call (endpoint fields U, verify), or keep UNKNOWN at full reservation.
3. `scripts/audio/el_tts_run.py`: one request per job, `/with-timestamps`, fixed model/voice/settings/seed, writes wav + alignment + manifest.
4. `scripts/audio/el_sfx.py`: prompts from PALETTE, N candidates, listening sheet, owner pick.
5. Mixer: M&E stem, ducking, loudnorm, two-track mux.
6. `scripts/audio/el_stt_check.py`: Scribe back-transcription diff (advisory report).

### 7.3 Time and money saved (honest)
- Per voice iteration today: ~22 min Kaggle GPU + about 10-15 owner minutes (open the page, Save & Run, download, ingest) [measured 1,332 s in HANDOFF; owner minutes I]. ElevenLabs: 124 short requests, a few minutes, no owner clicks [I]. With 3-5 iterations: about 1-2 h wall and about 1 owner-hour saved.
- Sound sourcing: 22 sounds x 15-30 min (search, audition, licence check, log) = 5.5-11 h, against about 2-3 h of listening to candidates: **net 4-8 h saved** [I].
- Integration cost: about 1-2 days of Claude code + 2-3 Codex rounds; owner about 2-3 h for the test and picks [I].
- Net: **about 5-10 hours saved over the film, plus better character voices**; artwork (20-93 owner hours, HANDOFF/NEXT_STEPS planning minimums) still dominates the schedule.
- Money: about $12-45 for the whole film depending on plan route. **Nothing to cancel elsewhere**: Kaggle GPU is free, Parler is free, no paid sound library was planned. The plan does not save money; it buys quality and owner time.

---

## 8. Strongest case AGAINST my recommendation

1. **Marathi quality is the whole bet and it is unproven.** No independent Marathi evaluation of v3/v4 exists that I could find; v4 is weeks old; the vendor groups Marathi recognition at 5-10 % WER (not its best tier), a hint that Marathi data is thinner [V/I]. Sacred verse with Sanskrit quotations is the hardest case. A multilingual model may read Marathi with Hindi phonology.
2. **The owner has not listened to Parler yet.** Parler is free, already integrated, Apache-2.0, all 124 clips exist and are measured [repo]. Switching before hearing it is deciding without evidence. A cheaper path: keep Parler, fix only what the owner dislikes.
3. **Hybrid may beat all-ElevenLabs:** Parler (or Indic-Speak) for Marathi narration, ElevenLabs only for Hindi character voices (where Parler has two males) and sound effects. Downside: timbre differs between languages, but each language track is heard alone.
4. **Sound effects need not cost anything:** CC0 libraries (e.g. Freesound CC0 filter) give real recordings with clear licences; generated ambience can contain pseudo-speech and "generic" textures; the per-second price has already changed between doc versions (11 -> 20 -> 40 credits/s) [V], so prices drift.
5. **Lock-in and reproducibility:** voices live in the ElevenLabs account; Default voices expire 31 Dec 2026 [V]; Library voices can be withdrawn [V]; TTS is nondeterministic [V]; a re-take next year may sound different or need a paid month. With Parler, model commit + seed reproduce the clip locally/on Kaggle.
6. **Licence edge cases:** Beta-service output is non-commercial [V]; nothing marks v4 or `eleven_text_to_sound_v3` as beta today, but labels changed before (v3 was "alpha" per its help URL) [V/I]. PAYG-only commercial status is unstated [U].
7. **Data:** scripts and audio are retained in history; Zero Retention is Enterprise-only [V]. Low risk for a public scripture, but it is a change from "everything on the owner's PC" (A3 follow-up 2).
8. **Not using Dubbing may be wrong for Hindi:** if the owner's Hindi text stays NOT VALIDATED anyway, an automatic Hindi dub would at least be a native-sounding translation. Counter: it would replace the owner's wording, violate script control, and cost 2,000-10,000 credits/min [V].

**Evidence that would change my mind:**
- The owner prefers Parler on at least 5 of the 8 Marathi test lines, or ElevenLabs drops/adds/repeats a word in more than 1 of 16 clips, or mispronounces any name that an alias rule cannot fix -> keep Parler for Marathi (hybrid route 3).
- Hindi character voices from ElevenLabs not preferred over Parler's two males -> no ElevenLabs speech at all; ElevenLabs only for SFX, or none.
- Over half of the sound-effect candidates contain intelligible speech, music or modern sounds -> CC0 recordings for those sounds.
- ElevenLabs states that PAYG output is commercially licensed -> PAYG-only becomes the cheapest safe route.
- Starter refuses `pcm_24000` and 128 kbps artefacts are audible after the AAC encode -> Creator.

---

## 9. Prioritised plan (ordered; owner gates marked GATE)

0. **Owner listens to the existing Parler tracks** (HANDOFF step 1). This is the baseline; the comparison is meaningless without it.
1. **Free-tier test (website, no API key needed, no spend):** design 4 voices (narrator, Maharaj, Bankatlal, Damodarpant; each used for both languages); generate the 8 lines (section 4) in both languages on v4 and v3; 3 SFX prompts (`bed_village_noon_heat` loop 30 s, `fx_leaf_plate_rustle`, `bed_courtyard_feast_murmur`). Save clips outside the repo (throwaway; free-tier output is non-commercial [V]).
   **Success criteria:** (a) owner blind preference ElevenLabs over Parler on >= 6/8 Marathi and >= 6/8 Hindi lines; (b) zero dropped/added/repeated words (owner listening; Scribe diff as helper later); (c) every name and the Sanskrit quotation acceptable to the owner, with at most an alias fix; (d) Bankatlal and Damodarpant clearly distinct in Hindi; (e) SFX: at least 2 of 3 usable without intelligible voices.
2. **GATE (owner):** pass -> buy Starter monthly (the $1 promo ends 1 Nov; do not let a $5 saving skip step 1). Fail on Marathi only -> hybrid. Fail overall -> stay on Parler + CC0.
3. **DECISIONS.md amendment (proposal text by Claude, owner approves):** ElevenLabs = audio route (speech, SFX, optional music); Parler kept as fallback; separate ElevenLabs spend cap; which wording (verse vs simple) each line uses, reconciling A3(7); Hindi stays NOT VALIDATED; voices locked before the paid director run. `ARCHITECTURE_V3_1.md` untouched.
4. **Code, small steps, each with synthetic-fixture tests and a Codex review before any paid call:** (4a) `el_client.py` + ledger phase and cost function + tests with a fake HTTP server (refuse on cap, on redirect, on missing usage); (4b) `el_tts_run.py` writing the existing manifest schema + alignment; ingest additions; resample to the mixer format; (4c) one paid probe line, reconcile the ledger against the dashboard; (4d) the 124 clips; ingest; `a1_audio.py build --measured`; `story_split.py revise`; owner listening sheet.
5. **GATE (owner):** voices approved (draft status lifted for Marathi; Hindi stays NOT VALIDATED); split hash approved; only then the paid Kimi director run (HANDOFF step 3).
6. **SFX:** `el_sfx.py` candidates for the 22-sound palette, owner picks, provenance JSON; one 30 s music test.
7. **Mixer:** M&E stem, ducking, loudnorm, two-track mux; test on the S1+S4 pilot render (HANDOFF step 5). **GATE:** owner approves the pilot audio-visual sequence.
8. **Adhyay 2** repeats 4d-7 once its Marathi text exists; cancel the subscription only after every re-take is done (rollover and new commercial generation end with the plan [V]).

Records per clip (reproducibility): text, text_sha256, language, voice_id, voice name, model_id, voice_settings, speed, seed, pronunciation dictionary id + version, output_format, request time, plan tier, alignment JSON hash, audio sha256. Expect re-generation to differ; the stored audio, not the recipe, is canon.

---

## 10. Sources (all accessed 2026-10-26)
- https://elevenlabs.io/pricing
- https://elevenlabs.io/pricing?price.section=sound_effects (credit costs FAQ)
- https://elevenlabs.io/pricing/api
- https://elevenlabs.io/docs/overview/administration/billing.md
- https://elevenlabs.io/docs/overview/models
- https://elevenlabs.io/docs/capabilities/text-to-speech
- https://elevenlabs.io/docs/api-reference/text-to-speech/convert-with-timestamps
- https://elevenlabs.io/docs/api-reference/text-to-dialogue/convert-with-timestamps
- https://elevenlabs.io/docs/best-practices/prompting/controls
- https://elevenlabs.io/docs/capabilities/forced-alignment
- https://elevenlabs.io/docs/capabilities/speech-to-text
- https://elevenlabs.io/speech-to-text/marathi (vendor claim)
- https://elevenlabs.io/text-to-speech/marathi (vendor claim)
- https://elevenlabs.io/docs/capabilities/voices
- https://elevenlabs.io/docs/help-center/product/voices/voice-library/what-is-a-notice-period
- https://elevenlabs.io/docs/capabilities/sound-effects ; https://elevenlabs.io/docs/overview/capabilities/sound-effects
- https://elevenlabs.io/docs/api-reference/text-to-sound-effects/convert
- https://elevenlabs.io/docs/help-center/product/content-production/sound-effects/how-much-does-it-cost-to-generate-sound-effects
- https://elevenlabs.io/docs/capabilities/music
- https://elevenlabs.io/docs/capabilities/dubbing
- https://elevenlabs.io/docs/help-center/legal/can-i-publish-the-content-i-generate-on-the-platform.md
- https://elevenlabs.io/docs/help-center/product/core-capabilities/text-to-speech/how-much-does-it-cost-to-generate-using-eleven-v3-alpha.md
- https://elevenlabs.io/docs/eleven-api/resources/zero-retention-mode
- https://elevenlabs.io/use-policy
- Third-party (launch date only): https://datanorth.ai/news/elevenlabs-releases-eleven-v4-and-eleven-v4-turbo ; https://openrouter.ai/models/elevenlabs/eleven-v4
- Repository (read-only): HANDOFF.md, DECISIONS.md, NEXT_STEPS_PLAN.md, A1_audio_plan.md, A1_full_script_simple.md, scripts/source/a1_voices.py, a1_voice.py, a1_audio.py, a1_audio_spec.py, scripts/audio/a1_tts_run.py, scripts/source/kimi_adapter.py, scripts/image_trials/v5_ledger.py, canon/audio/A1_audio_plan.json.
