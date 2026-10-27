# Prompt for Argon (copy everything below the line). Task: argue about restructuring the audio side around ElevenLabs

---

You are an independent senior reviewer. I am the owner of a solo project. Your job is to ARGUE: take a clear position, then attack it, and say what evidence would change your mind. Do not just agree with me. Cite sources (URL + date) for every ElevenLabs fact and mark what you could not verify. Do not ask for or use any API keys. Research and advise only.

## The project in one paragraph
GranthStudio makes ONE 10-20 minute motion-comic film of Adhyay 1 + Adhyay 2 of "Shri Gajanan Vijay" (a Marathi devotional text about Shri Gajanan Maharaj of Shegaon): ONE picture track, TWO audio tracks (Marathi and Hindi), plus sound effects. Adhyay 1 alone is 61 shots x 6 s = 366 s (SUPERSEDED 2026-10-27: 59 shots after measured ElevenLabs timing). I (the owner) am the only approver. An AI coding assistant writes the glue code; other models only review. No model output becomes canon until I approve it. No invented dialogue or Granth content.

## Architecture (what exists today)
1. **Story split**: one Kimi (paid, capped at $1 for testing, $50 total) planning call splits Adhyay 1 (146 verses/ovis) into ONE story of NINE scenes (S1-S9), 61 shots; code validates every verse is owned exactly once; Nemotron (free) gives an advisory cross-check; I approve the exact hash.
2. **Audio plan**: 62 spoken lines. Marathi lines are exact verse segments of the Granth cut by code; speakers (narrator, Gajanan, Bankatlal, Damodarpant) follow my dialogue table, unclear speakers stay narrator. Hindi is a draft adaptation, not validated. The year 1878 is an on-screen caption. I have now supplied an EASY Marathi and Hindi version of all 62 lines (about 9,200 characters in total).
3. **Voices today**: Indic Parler-TTS (free, gated model) on a Kaggle GPU: 124 clips in about 22 minutes; the Hugging Face token must be a Kaggle secret and only runs started from Kaggle's page can see it; only two male Hindi voices; I find the voices unnatural and the wording too hard. Timing is MEASURED from the generated wavs: each line's beat = the longer of Marathi and Hindi; shots per scene = ceil(timeline / 6 s). Shot counts feed the director.
4. **Director**: Kimi directs each scene once (exact shot count, narration timeline, dialogue only from the planned lines); validator and reviewer rubric; money ledger reserves worst case before each paid call. Picture rendering: 6 s shots, 24 fps, 11 presets, a frozen builder; I make every image myself. THE VIDEO SIDE IS SETTLED; do not re-plan it.
5. **Sounds today**: a closed palette of 22 sounds and 18 cues (anchors: scene bed, picture event, before/after a line; never over a spoken line), all unsourced: each would need my recording or a licence-checked CC0/CC-BY file.
6. **Mix today**: our own script places each clip at its beat inside its scene and writes one full track per language, in sync with the picture.
7. **Gates**: approvals are separate records and go stale when anything upstream changes; human review of the film is still to do.

## The decision
I will buy ElevenLabs PREMIUM (the 30,000-credit Starter plan is the entry point; Creator or higher is possible) and do ALL audio there: Marathi and Hindi speech with distinct character voices, AND sound effects (and ambience/music if it fits), aiming for a full-fledged, good-quality soundtrack. I believe Marathi is supported (speech, cloning, speech-to-text) but have not verified it from ElevenLabs' own pages. Known facts (verify!): Starter 30,000 credits (~30 min speech), commercial licence, instant voice cloning, 74 languages; speech about 1 credit per character; a sound effect about 200 credits; auto-dubbing 2,000-10,000 credits per minute; Creator has professional cloning.

## What I want from you
1. Your position: which plan, which models (v3 vs multilingual v2 vs flash), speech-to-text/forced alignment for timing, text-to-speech from my exact text versus auto-dubbing, sound-effects workflow (turn my 22 sounds/18 cues into prompts, durations, looping, quality, licence for commercial release), mixing and ducking, loudness targets, and the final assembly (our own script vs ElevenLabs Studio/Dubbing Studio).
2. Which of my current steps disappear or shrink (Kaggle job, secrets, estimated-vs-measured timing, sound sourcing and licence logging, Hindi review burden) and which new ones I need (job builder, spend guard for credits like my Kimi money ledger, provenance record: text + voice id + model + settings + output hash).
3. Credits needed for Adhyay 1 and Adhyay 2 including re-takes and all sound effects, and the right plan size (monthly vs one-off, rollover, overage, rights if the plan lapses).
4. **Argue**: the strongest case AGAINST your own recommendation (Marathi quality for sacred verse and names, lock-in, cost, voice-cloning consent, price changes, reproducibility, cheaper hybrids such as keeping the free voices for drafts), what free-tier test (6-8 lines, success criteria) would settle it, and what evidence would change your mind.
5. A one-page executive summary first, then detail, then an ordered plan: free test, my purchase decision, small coding steps.

Be blunt and practical. I am a solo owner on a Windows PC.
