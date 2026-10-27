# GranthStudio pipeline README (fixed pipeline for Adhyay 1-21)

Written 2026-10-27 from the owner's answers. This file is the single place that says WHAT each stage takes in and gives out, WHO runs it, and WHAT must be approved. Details and history: `FINAL_ARCHITECTURE_PLAN.md`, `DECISION_LOG.md`, `IMAGE_PROMPT_RULES.md`, `CODEX_KIMI_WORK_PLAN.md`. Status: PLAN. Nothing marked "to build" exists yet.

## 0. Rules (owner)
1. The pipeline is FIXED after Adhyay 1: a new Adhyay supplies DATA only. Test: Adhyay 2 runs with zero code change.
2. The owner supplies the finished, perfect EASY Marathi + Hindi script. Kimi never writes, edits or replaces a line of it. (Code only checks it, see section 3.)
3. Kimi works in two stages. Stage 1 = chapter planning (scenes, shots, image briefs/prompts, sound suggestions, questions) at effort HIGH. Stage 2 = animation choice, effort LOW (HIGH only as one retry the owner agrees to).
4. Same kind of animation exists = reuse the saved preset/shot plan (exact hash match), no Kimi. New animation = Kimi drafts JSON DATA only (shot plan / preset), tested and owner-approved, then saved and reused. Nobody writes Blender/animation code (D-017, Builder v2 frozen).
5. Adhyay 1: Stage 1 is NOT repeated. Its Stage 1 outputs already exist (split rev9, bible, image jobs, 59 images, audio plan). Stage 1 is for Adhyay 2+ and is tested on Adhyay 1 data with no paid call.
6. Two videos: one Marathi, one Hindi. Same picture, same length, same shared beat timeline (sized to the longer measured line; the shorter language rests in silence/ambience; speech never sped up or cut).
7. Money: every paid call goes through the existing ledger; one call, no automatic repair; the owner decides after a failure. The owner removed the per-chapter cap idea (2026-10-28): no new cap numbers; the existing ledger guards stay unchanged.
8. The owner is the only approver (batch per chapter: contact sheet + exceptions list). Claude reviews harness/validators; Codex reads read-only; Nemotron drafts code (section 6).

**Stage 1 in full: read `docs/pilot/STAGE1_RULES.md`** (directors/roles, story vs philosophy, calls, input packet, shared rule block, preset and sound use, image-brief lessons, must-nots). Stage 1 now has NINE outputs: story_map, coverage, scenes, shots, image_briefs, canon_looks, voice_cast, sound_suggestions, questions.

## 1. Layout (a chapter is a folder of data)
`canon/adhyay_NN/` : `source/ovis.jsonl`, `research/packet.json`, `script/easy.md` (owner), `bible/` , `stage1/*.json`, `audio/`, `images/catalog.json`, `approvals.json`. Series-wide: `canon/series/` (characters by chapter state, places, props, voices, glossary, `sounds/palette.json`), `assets/v5_presets/` (presets), `canon/shot_plans/A<N>/S<x>.json`. Adhyay 1 files keep today's paths until migrated (B6).

## 2. Stage contracts (input -> output -> who -> gate)
| # | Stage | Input | Output (file) | Runs | Gate / owner |
|---|---|---|---|---|---|
| 0 | Source lock | printed-book-checked Marathi ovis; research packet; glossary | `source/ovis.jsonl`, `research/packet.json` (each with sha256) | code | owner approves hashes |
| S | Script | owner's EASY script | `script/easy.md` (format in section 3) | owner | code checks coverage/format; owner confirms (already perfect) |
| 1 | Kimi Stage 1 (HIGH) | ovis, research, script, series bible, character/place/prop catalog, glossary, voice cast, style, sound palette, preset index | `stage1/story_map.json` (ovi types, events, closure), `stage1/coverage.json` (disposition of every ovi), `stage1/scenes.json` (scene id, section kind story|discourse, ovi range, goal, turn, ordered script line ids), `stage1/shots.json` (shot slots with beat/pose/framing/preset type hint: flat or needs cut-out), `stage1/image_briefs.json` (per image: people, place, pose, camera, reason new), `stage1/sound_suggestions.json` (palette id or NEED_NEW + anchor), `stage1/questions.json`, `stage1/voice_cast.json` (character -> saved voice id), `stage1/canon_looks.json` (new/changed characters, places, props: look + source ovi + stated/inferred) | Kimi (per scene or small group), capped ledger; free NVIDIA pre-check + dry run first | code validates coverage, ids, claims; owner approves split, briefs, questions as one batch |
| 2 | Canon | approved Stage 1 + owner decisions | `bible/entities.json`, final scene split | code | owner |
| 3 | Voices + measurement | script + `canon/series/voices.json` | per-line audio, `audio/clips.json` (text/voice/model/settings/hash, measured seconds, credits) | ElevenLabs eleven_v4, 1 call/line, credit ledger | owner listens, accepts |
| 4 | Shared beats + image jobs | measured clips + stage 1 | `timing/beats.json` (MR/HI seconds, common start/end, pause, crossings), `images/jobs.json` (Flow prompt built by CODE from approved data + references) | code | owner approves count/timing/briefs |
| 5 | Images | jobs + sheets | versioned Flow candidates; `images/catalog.json` (id, chosen version, actual prompt, model, edit id, sha256 raw/clean, approval) | Flow agents (approved), code filing | Claude reviews, owner approves set; clean with per-chapter watermark data |
| 6 | Kimi Stage 2 (LOW) | beats, catalog ids + one-line descriptions, preset + shot-plan libraries | `animation/scenes/S<x>.json` per scene: ids only | code replay first; Kimi only unresolved shots; NEED_NEW with reason/class | validator (ids, roles, sha256); owner approves per scene |
| 7 | Render + mix | approved scene files | shot videos (144 f, 24 fps, 1280x720), Marathi mix, Hindi mix, subtitles | motion.py / Builder v2, ffmpeg | owner watches/listens |
| 8 | Delivery | shots + mixes | `delivery/<chapter>_marathi.mp4`, `delivery/<chapter>_hindi.mp4` (same picture, same length) | ffmpeg | owner checks both |

Resume/interrupt: a stage reruns only when its input hash changed; paid calls and approvals are the only things with receipts; an unknown paid result stops everything until the owner reconciles.

**Cinematographer rule (owner 2026-10-28):** in Stage 1 the shot plan uses a shot/preset from the preset list WHENEVER one exists (`assets/v5_presets/index.json`, the 11 presets, given to Kimi with their roles). If nothing in the list fits a beat, the shot is marked `NEED_NEW` with a short reason and class (missing image/pose, JSON arrangement, renderer gap); it is NOT invented in Stage 1. Stage 2 then generates it: Kimi drafts the new preset/shot plan as JSON data, which is tested, owner-approved and saved into the preset library for reuse. Kimi never invents a preset name in Stage 1.

## 3. What the owner's EASY script must contain (answer to "what do you want in the script?")
Format (same as `A1_full_script_simple.md`, read by `easy_script.py`):
```
## S<scene number>
**S<scene>-L<line>** | <voice id> | ovi <number> | core|optional
- Marathi: <spoken text, Devanagari>
- Hindi: <spoken text, Devanagari>
caption S1-K1 (on screen): <text>   (only where a caption is wanted)
```
Requirements per line: a unique id in reading order; one speaker voice id (`narrator` or a registered character voice); the ovi number it renders; core or optional; BOTH Marathi and Hindi present, no empty line; spelled exactly as it should be spoken (names as in the glossary, numbers/years written the way you want them read, punctuation for the pauses); one idea per line, about 4-10 s when spoken (the longest A1 lines are about 10 s); no English words, no stage directions, no timings. Character lines are separate lines with the character's voice; narrator lines are never put in a character's mouth. The Marathi and Hindi must mean the same thing as the ovi. Please also give: the list of speakers/voices used, which lines are optional, and any caption text (e.g. the year). Code checks: every ovi of the chapter is covered or marked unfilmed, ids unique and ordered, both languages present, glossary spellings, speaker registered. Code only REPORTS problems to you; it never edits the script.

## 4. Kimi: what it may and may not do
Stage 1 may: group ovis into scenes and shots, write short image briefs and pose/framing notes, flag flat vs cut-out need, suggest sound palette ids, list open questions, based on the locked source + your script. It may not: write or alter script lines, invent canon, write timings (code owns them), make images, or write code. Stage 2 may: pick catalog image ids and preset ids, held pose/staging, transition, or NEED_NEW; draft new preset-03 variants/shot plans as bounded JSON. It may not: invent image ids, move a limb from a held pose, change Builder v2, write Python/Blender code.
Settings: Stage 1 effort HIGH, small per-scene calls (output ceiling about 8,192 tokens so the ledger reservation stays small; raise only with the owner), stable references first (identical bytes help prefix caching). Stage 2 effort LOW, ceiling about 2,048-4,096. Every request: free schema/catalog pre-check, free NVIDIA dry run, ledger reservation, ONE call, no repair, receipt. S4 proof (Adhyay 1): one call, effort low, $0.0724 (not repeated).

## 5. Prompts: how we test them (nothing paid until these pass)
1. Each Kimi prompt is built by code from data and has a fixture test on synthetic data (missing/duplicate ovi, unknown id, timing key in output, invented image id, edited script line all fail).
2. Run it for FREE on Adhyay 1 data (known answers: split rev9, bible, 59 jobs) with the NVIDIA pool (Nemotron) and compare with the real A1 outputs: coverage, schema validity, claims, accept-rate.
3. Image prompts: build from data with the template in `IMAGE_PROMPT_RULES.md`; compare against the 59 accepted A1 jobs; a prompt test fails if it contains narration/story notes, a missing place chip, or a wrong chip count.
4. Only then one paid Kimi call for one new scene (Adhyay 2), owner reads the result. The low-vs-high comparison (Stage 2) is optional and only with the owner's yes before spending.

## 6. Who writes the code
Owner rule (2026-10-28, replaces the 2026-10-27 wording): Claude writes NO code. Nemotron (free NVIDIA pool, 14 keys, several drafts in parallel) writes all code AND tests. Method: Claude writes the spec; a SEPARATE Nemotron call writes adversarial tests from the spec; Codex reads those tests; the tests are frozen; a second Nemotron call writes the code into a scratch folder; Claude only runs the tests and copies a passing file into the repository after reading it; a defect goes back to Nemotron as a fix spec plus the failing output (never a hand patch); Codex (medium effort) AND a Haiku 5.5 agent (low effort), both read-only, review every spec, test set and code; findings go back to Nemotron as a fix spec. Nemotron never writes Blender/animation code (D-017) and never sees `secrets/`. NOTE: `CLAUDE.md` still says Claude is the only code writer; the owner decision is recorded in DECISIONS.md and the file is left unchanged unless the owner asks for the amendment.

## 7. Build order and checklist
`CHECKLIST_BUILD_PIPELINE.md` (this job) lists every item with its test. Old lists stay valid: `FINAL_ARCHITECTURE_PLAN.md` section 6 (B1-B18, D1-D6) and section 9 (K1-K14), `CHECKLIST_PROOF_SCENE_S4.md`, `CHECKLIST_REUSE_SHOT_PLANS.md`.

## 2b. Producer / consumer matrix (who writes each file, what checks it, what it depends on)
| File | Written by | Checked by | Depends on (fingerprint) |
|---|---|---|---|
| `source/ovis.jsonl`, `research/packet.json` | owner + code import | owner approves hash | printed book |
| `script/easy.md` | owner | `scripts/pipeline/check_script.py` (reports only) | source, voices, glossary |
| `stage1/scenes|shots|image_briefs|sound_suggestions|questions.json` | Kimi Stage 1 | schemas + `validate_stage1.py` | source, script, series data, sound palette |
| `audio/clips.json` (+ audio files) | ElevenLabs via credit ledger | owner listens; caps | script, voices |
| `audio/timing.json` (`beats`) | code | `validate_assets.validate_beats` | clips, script |
| `images/jobs.json` | code (from approved data) | image prompt rules tests (to build) | stage1 briefs, series data |
| `images/catalog.json` | code after owner approval | `validate_assets.validate_catalog` (live sha256) | images, jobs |
| `animation/scenes/S<x>.json` | Kimi Stage 2 (or replay) | `validate_assets.validate_animation` | beats, catalog, presets |
| `canon/shot_plans/A<N>/S<x>.json` | code after owner approval | `validate_assets.validate_shot_plan_fresh` | script, timing, presets, images |
| `approvals.json` | owner (write path to define, checklist item 12) | `scripts/pipeline/gates.py` (stages call `require_approved`) | every file above |
| `spend.jsonl` | `scripts/pipeline/caps.py` (reserve/settle/unknown/reconcile) | caps.check | `caps.json` |
Paths for any chapter come from `scripts/pipeline/chapter.py` (`chapter_paths`); Adhyay 1 keeps its legacy paths. Built and tested: nemotron_code, chapter, approvals, caps, gates, check_script, validate_stage1, validate_assets, nine schemas. Still to build: wiring into the existing commands (`--adhyay N`), caps into `kimi_adapter.py`, the approval write path, prompt builders, replay, render/export.

## 8. WHAT A NEW ADHYAY NEEDS FROM THE OWNER (final input list, 2026-10-28)
You supply only these five (canon and look decisions are Kimi's, see below):
1. **Source text:** the chapter's Marathi ovis, checked against the printed book (ovi number + text).
2. **Research packet:** characters, places, objects, time, who speaks which ovi (dialogue table), glossary additions, your direction notes, and the list of ovis that will NOT be filmed.
3. **EASY script** (section 3 format): Marathi + Hindi for every line, voice id, ovi, core/optional, captions.
4. **Approvals at the gates** (you approve, nobody else): script/split, images, scene plans, final videos. HOW they are grouped (one by one, or a contact sheet) is the pipeline's presentation, not an input.
5. **Rights notes** only if something changed (a new image route or sound source).

**Canon and look decisions are made by Kimi Stage 1** (owner 2026-10-28): every NEW character, place or prop and every change of a known character's state (age, clothes) is decided in `stage1/canon_looks.json`. Each entry cites the source ovi it comes from and is marked `stated` (the text says it) or `inferred` (Kimi's choice where the text is silent, so you can see it); known cast, places and style come from the series data and are never redecided. Kimi may not invent events, facts or dialogue: only the visual look. The reference sheets are generated from these entries and you approve the images at the gate (approval stays yours).

Voices are NOT an input you prepare. The saved voice cast (`canon/audio/A1_eleven_voices.json`, owner-approved 2026-10-26) is reused: narrator Tukaram `CXkeo30p0Sk4Lr0TAzeo`, Gajanan Sharad `8fqGzH80bdkm2UseeV9f`, Bankatlal Bipin `fqdB7wf4ETj9FXQ8wkLu`, Damodarpant Vinayak `rXW8MF4nX2gHMvBmCDnr` (the same voice speaks Marathi and Hindi). Female voices kept for later Adhyayas: Mugdha, Roopa, Radha K, Kalyani, Mukta. **Kimi Stage 1 assigns a voice to every speaking character** (`stage1/voice_cast.json`: character -> voice id from the saved cast; recurring characters keep their voice for all Adhyayas; a new character gets a proposed voice from the unused saved voices, male/female and age matched). Kimi sees the descriptions of ALL saved voices and chooses by description; recurring characters keep the same voice; no fitting voice = a question to you, never an invented id (see `STAGE1_RULES.md`, Voice casting detail). Once fixed it is saved to series data and never changes. You only listen and accept (or reject) the generated clips.
Removed from your list (owner 2026-10-28): per-chapter caps (the existing ledger guards stay as they are; no new cap numbers to set), watermark calibration (done after image generation by the pipeline's cleaner; see item 9 of the checklist: make it automatic), and batch approval as an "input".
Already in the pipeline (not needed again): the 11 presets, style anchor, voice cast, sound-effect pack, glossary, schemas, checkers, ledgers.
Produced by the pipeline (you only approve): scene/shot plan, voice casting, image briefs and Flow prompts, sound suggestions, measured timing, scene animation files, the Marathi and Hindi videos.

## 9. IMAGE GENERATION RUNNER (Haiku agents, effort LOW; owner 2026-10-28: "we use the same")
Stage 5 (images) is run exactly as in Adhyay 1. Facts to keep (read these, do not rely on memory):
- **Who:** Haiku agents at effort LOW operate Google Flow in the Claude built-in browser (tools `mcp__Claude_Browser__*`), ONE TAB PER AGENT; the owner signs in himself (nobody types passwords); Claude writes the job files and watches the first 2-3 results, then reviews. Codex reviews contact sheets read-only (medium effort).
- **Briefs and runbook:** `docs/pilot/HAIKU_FLOW_AGENT_BRIEF.md` (UPDATE 1-16), `docs/pilot/FIX_PASS_BRIEF_UPDATE16.md`, `docs/pilot/FLOW_RUNBOOK.md` (sections 1, 3, 5, 8-18: every click coordinate verified on this PC, after-restart settings, multi-agent rules, edit-first, review loop, download pitfalls).
- **Job files (per chapter, built by code from approved data):** shot jobs (`canon/drafts/A1_flow_shot_jobs.json` is the A1 example: shot_id, flow_title `<ID>__vNN`, characters, place_search, style_ref_search, prompt), regen jobs, edit jobs with previous/next shot. Scripts: `scripts/flow/build_shot_jobs.py`, `build_regen_jobs.py`, `file_flow_download.py`, `file_regen.sh` (exact-title filing, fail closed), `build_final_manifest.py`, `build_final_set.py`, `audit_flow_outputs.py`.
- **Settings:** model Nano Banana Pro x1 (when Pro hits its daily limit: Nano Banana 2.1 x1), 16:9, 2K download; after every PC restart the browser forgets login and settings (runbook section 13).
- **Method:** attach @ chips (one exact search match each), type the prompt, generate, rename the tile to `<ID>__vNN`, download 2K to `D:ai worklow_outputs\` (the file keeps the title in its name), file it with the script; EDIT-FIRST for a local defect (download IMMEDIATELY after the edit, before renaming), regenerate for identity/framing faults; the strict Maharaj check; first three images of each new scene reviewed before the batch continues.
- **Hard rules:** stop on sign-in, CAPTCHA, payment or terms pages; never click Trash/Delete/Share/Upgrade; 3 failures in a row = stop and report.
- **Lessons and prompt template:** `docs/pilot/IMAGE_PROMPT_RULES.md` (and `CODEX_IMAGE_LESSONS.md`). Outputs of Adhyay 1: `D:ai worklow_outputsdhyay_01\` (`final`, `final_clean`, `shots`, `references`, `final_review`).
- Authorisation of Flow agents: approved by the owner 2026-10-27 (`docs/DECISIONS.md`, A3 follow-up 9).

## 10. SOUND PLANNING, SOUND PACK AND ELEVENLABS (owner 2026-10-28; full text `STAGE1_RULES.md` section 8, research `CODEX_ELEVENLABS_SOUND.md`)
- **Kimi Stage 1** plans sound: it receives the CURRENT sound palette (`canon/series/sounds/palette.json`, loaded fresh for every chapter) and picks an existing sound id, or emits NEED_NEW with an ElevenLabs-ready sound-effect prompt (the only "script for ElevenLabs" Kimi writes). **Stage 2** receives the current animation presets the same way. Same logic for both: reuse if it fits; if not, generate (sound by ElevenLabs once; animation as JSON by Kimi), then save to the library.
- **Method:** separate ElevenLabs Sound Effects files mixed by code (`POST /v1/sound-generation`, 0.5-30 s, loop supported); effects are NOT put inside the speech script (tags exist but are unreliable for placement and tied to each language's file). Ducking against the union of both languages' speech windows. No music.
- **Pack record:** id (`bed_*`/`fx_*`), version, kind, prompt, duration, loop, settings, model, credits, receipt, file hash, rights note, approval, tags, status AVAILABLE | NEED_NEW | REJECTED. Never overwrite an accepted version.
- **Rights:** film use of sound effects allowed under the paid-plan terms; do not distribute the pack as a library; keep every file and receipt locally.

## 11. VOICE LIBRARY (built 2026-10-28)
`canon/series/voices.json` is the library Kimi Stage 1 receives for voice casting: 35 saved ElevenLabs voices with name, gender, age, accent, description, Marathi/Hindi verified flags, `assigned_to` and status (ASSIGNED | AVAILABLE | MISSING_FROM_ACCOUNT). Rebuild or refresh with `uv run python scripts/pipeline/voice_library.py [--dry-run] [--overwrite]` (read-only, no credits; the API key is read at run time and never printed). Recurring characters keep their assigned voice in every Adhyay; a new character gets the best-matching AVAILABLE voice by description; the owner edits `owner_note` and descriptions; verified Marathi AND Hindi voices are preferred because one voice speaks both languages.

## 12. (REFERENCE ONLY, ON HOLD: owner 2026-10-28 'just for reference, leave it') SOURCE INPUT FORMAT: the "Audited Canon Edition" docx (owner uploaded Chapter 2, 2026-10-28)
File: `Shri_Gajanan_Vijay_Chapter_2_Audited_Canon_Edition.docx` (uploaded to the session; copy it to `canon/adhyay_02/source/` when the importer exists). Structure checked by Claude: PART 1 = story bible (1 Characters, 2 Locations, 3 Key objects and cultural glossary, as bullet lists with Marathi names); PART 2 = trilingual table for ovis 1-148 in 12 sections ("Section N: aaa-bbb | Marathi title (English title)" plus a one-line context), one row per ovi with FIVE cells: ovi number (001..148), original Marathi verse (ends with the printed number between double dandas), Simple Marathi meaning, Hindi translation, Easy English translation. Verified: 148 rows, consecutive, no duplicates, no empty cell, every verse carries a printed number.
Findings for the owner: (1) printed verse numbers differ from the row number at TWO rows: ovi 118 prints 119 and ovi 129 prints 119 (they look like printed-edition numbering slips kept as printed): the importer must use the ROW number and report every mismatch for the owner to confirm against the printed book. (2) The doc has no speaker/dialogue table, no unfilmed/omission list, no direction notes, and no EASY SPOKEN SCRIPT (the Simple Marathi/Hindi columns are meanings per ovi, not spoken lines with line id, voice, core/optional): those stay separate owner inputs (section 8: research packet items and the EASY script). (3) This layout is a good STANDARD for every Adhyay IF it stays identical (same Part 1 headings, same 5-column table, same "Section N: a-b | title" lines); a Nemotron-written importer (checklist item I1) reads it into `source/ovis.jsonl` (chapter, ovi, original, simple_marathi, hindi, english, section id/title/context) and `research/packet.json` (characters, locations, objects/glossary), refuses a table that deviates, and reports mismatches. Part 3 recommended for later chapters (owner or Kimi-drafted for owner approval): Speakers per ovi, Unfilmed candidates, Direction notes.

