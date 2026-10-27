# GranthStudio FINAL PLAN v1 (2026-10-26) - proposal for the owner's approval

Merges: the owner's rulings, the Opus and Codex ElevenLabs research (with rebuttals), Codex's director-contract report, Codex's advocate and critic audits of the local project, and the Kimi documentation check. Nothing here is approved until the owner says so. Sources: `docs/pilot/reference/research_notes/opus_*.md`, `D:/kaggle_upload/repo_research/codex_*.md`.

## 1. Principles (why this order)
1. **Fix the cheap, fixable things first; spend the dear, irreversible things last.** Order by cost of change: wording -> audio -> timing -> shots -> images -> render. A late change costs the owner hours of artwork; an early change costs nothing.
2. **Code decides everything that is fixed; Kimi decides only what needs judgement** (shot treatment). Fixed = scenes, shot slots, narration timeline, the owner's EASY lines and speakers, sound palette, characters, props, places, image ids.
3. **Libraries grow and are reused for CONSISTENCY, not to cap images (owner, 2026-10-26: no budget for images, as many as needed).** The film must look full; a purpose-made image per shot is welcome where it improves the picture. **Libraries grow and are reused** (presets, sounds, images/character sheets). Anything new is created ONCE, tested, owner-approved, versioned by hash, then reused by all 21 Adhyayas.
4. **Cheap checks stay in code** (validators, ledgers, locks, manifests). No extra checking agents.
5. **One paid generation per accepted result.** Never regenerate what is accepted; every paid call is recorded and replayable.

## 2. Roles
- **Owner:** approves every gate; makes all images (Nano Banana / Google Flow); chooses voices (with his mother); decides spending caps.
- **Kimi (director):** per scene, picks preset, catalog images, pose, staging, transition, sound ids from the palette; says NEED_NEW with a reason when nothing fits. Never writes dialogue, translations, timings, facts, appearance, image descriptions.
- **Code (Claude writes the harness only):** bible, catalog, packets, expansion of Kimi's ids into full records, validators, ledgers, timing, mix.
- **ElevenLabs:** all speech (Marathi, Hindi) and sound effects. No music, no dubbing.
- **Codex:** read-only reviewer. **Nemotron:** advisory only.
- **Blender builder v2 (frozen, D-017):** renders from JSON presets. No model writes Blender/animation code.

## 3. Pipeline with gates and exit tests
| # | Stage | Cost | Exit test (gate) |
|---|---|---|---|
| 1 | Final wording: the owner's EASY Marathi/Hindi (`A1_full_script_simple.md`), checked line by line against the verse meaning | free | owner approves script version + hash; Hindi stays NOT VALIDATED unless the owner says otherwise |
| 2 | Production bible + image catalog for Adhyay 1 from the frozen research (field-level source notes; conflicts become owner choices) | free | owner approves bible; unresolved list answered once |
| 3 | Voices: owner + mother pick 4 voices (narrator, Gajanan, Bankatlal, Damodarpant); generate the 62 lines x 2 languages once; owner listens | ~4-5k credits | every name/term right; 4/5 score; accepted clips hashed and frozen |
| 4 | Measured timing from the accepted clips; reconcile shot budgets (drop the old `max(audio, old budget)` floor deliberately) | free | owner approves the new timeline and shot count |
| 5 | Kimi writes image prompts for the catalog ONCE (per image, not per shot); owner makes character/place reference sheets | small Kimi + owner hours | reference sheets approved and hashed |
| 6 | Director, one scene first then the rest, with the compact contract (section 4) | Kimi, see below | scene validates, no omitted teaching, owner reviews the plan |
| 7 | Owner makes only the missing shot images | owner hours | images pass the existing inbox check |
| 8 | Pilot render (S1 + S4), then the rest scene by scene | free | owner reviews look and motion |
| 9 | Sound effects: generate only the 13 needed sounds once; resolve cue ids to accepted hashed files; mix in code | credits | no cue over a spoken line (or an owner-approved ducking exception) |
Freeze point: after stage 4 no speech is regenerated; after stage 6 no scene is redirected, unless the owner opens it.

## 4. Kimi contract and token plan
- **Input (per scene):** stable prefix first (rules, preset library, sound palette, catalog index), then the scene packet (goal, verse refs, fixed shot slots, narration timeline including speech crossing shot boundaries, the bible slice for only that scene's characters/props/places, allowed preset roles, cue slots).
- **Output (minimal JSON):** per shot: status READY | NEED_NEW; preset; asset roles -> catalog image ids; held pose id; staging choice id; transition; plus cue choices for unresolved slots. Code expands dialogue (approved line ids and text), claims and image descriptions.
- **NEED_NEW** is classified: missing image/pose | new JSON arrangement the frozen builder supports | demonstrated renderer gap (needs separate owner approval). Never an automatic permission to change Blender code.
- **Levers (from Kimi's docs):** `reasoning_effort` low/high/max (default max; test `low`); caching is automatic on identical prefixes (hit about one tenth of the input price, 5 min default TTL, 1 h option at 2x write cost); output is the expensive part ($15/M vs $3/M input, third-party figures); batch is not available for kimi-k3.1-pro; keep the prefix byte-stable, no timestamps.
- **Estimate (unmeasured):** a 6-shot scene falls from about 22k tokens (~$0.12-0.18) to about 6-8k; Adhyay 1 from about $1.2-1.6 to about $0.2-0.4. Test on ONE scene before the rest. Update the ledger rates after the owner checks the dashboard.
- **Libraries in the prompt:** presets and sounds are given to Kimi as ids; slice by relevance; record the reuse rate per Adhyay (share of shots that reuse an existing preset, sound or image). Expect presets and sounds to saturate in about 2-3 Adhyayas, images more slowly.

## 5. Audit findings to fix before any paid run (backlog, in order)
1. **EASY script vs director (BLOCKER):** the validator requires dialogue to be a substring of the verse; all 18 character lines fail. Bind dialogue to approved line ids and script hash; keep verse refs for meaning review; update validator, prompt and reviewer rubric together.
2. **ElevenLabs runner:** reuse accepted clips (key = text + lang + voice + model + settings), keep retakes separate, checkpoint each result, never overwrite; decode and measure each MP3 before marking ok; lock the ledger across processes; keep estimated vs confirmed credits separate; connect the measured manifest to the timing builder.
3. **Sound selection:** add cue slots and palette ids to the director contract; validate membership/anchors; resolve ids to hashed files; brass-vs-earthen vessel is an owner choice (the cue `fx_brass_pot_clink` assumes brass).
4. **Preset exposure:** the director reads presets from the chapter packet, not the library index; make the library index the source. Define who authors a new preset (proposal: Kimi writes JSON data only, test-rendered with the frozen builder, owner approves) - needs an owner decision against D-017.
5. **Timing floor:** replace `max(audio_need, old_budget)` with an explicit reconciliation.
6. **Handoff:** relabel the Kaggle/Parler commands as fallback history; point the next steps at this plan.
7. **Render recovery (harness only):** keep completed chunks for unchanged inputs; propagate failure exit codes.
8. **Ledger rates:** correct the Kimi rates after confirming the real prices.

## 6. Local project hygiene (audit, nothing deleted)
- D: has about 12.5 GB free. Biggest cleanup: old frame sequences in `v5_phase1`, `v5_phase1_v2`, `v5_smoke` (about 2.5 GB of PNGs). Archive them to another drive after keeping the approved builder, approval receipt, shot JSON, source images, selected MP4s and failure evidence. Archiving on D: does not free space.
- Duplicates (identical hashes): two `granthstudio.bundle` files (8.8 MB), five reference JPEGs, five `v3_final` documents, one inbox PNG. Safe to archive, owner decides.
- Media lives in the repo's ignored `artifacts` folder while `granthstudio-artifacts` is empty: document one storage location and back up ignored media.
- Frozen research copies are small and verified (A1 9 files, A2 3 files match their manifests); builder v2 matches its approved hash.

## 7. Decisions needed from the owner
1. Approve this plan as the working order (or change it).
2. Spoken wording = EASY script everywhere (already ruled); approve the line-by-line check against the verses.
3. Who authors new presets (Kimi writes JSON presets only, Blender code stays frozen)?
4. Sound cues: pre-approve the existing assignments, or let Kimi choose from the palette each scene?
5. Ducking exception: may a bed sit under speech, or must no sound overlap speech?
6. Kimi cap for the rerun (recommend: first one scene, then raise to what the measured cost needs).
7. ElevenLabs: keep Starter monthly; finish all retakes before cancelling; no music.
8. Archive plan for old frame folders.

## 8. How we improve (measure, then change)
After the pilot and each Adhyay record: Kimi tokens and cost per scene (with cached-token counts), reuse rate (presets, sounds, images), number of NEED_NEW, repair rounds, ElevenLabs credits per Adhyay, owner image hours. Change a rule only when a number shows a problem (for example: repeated repairs -> enlarge that scene's packet slice; low reuse -> widen the library offer; high credits -> shorter beds).

## 9. Do next (free, can start now)
Stage 1 check of the EASY script against the verses; stage 2 draft bible and catalog (list of unresolved looks for the owner); backlog items 1, 2, 5, 6 (code and docs, no paid calls).

## 9. Status update 2026-10-27 (not an approval)
Stage 5/7/9 (images) are DONE for Adhyay 1: 59 final shot images, cleaned copies in `flow_outputs/adhyay_01/final_clean/`; the 14 reference sheets exist; the 49 layers are not made and are decided shot by shot after a proof render. Codex advice: prove ONE scene end to end before directing the rest (checklist `CHECKLIST_A1_FINAL_IMAGES_TO_ANIMATION.md`, section E). Stages 1-4 and 6, 8, 10, 11 are unchanged and the plan itself is still awaiting the owner's approval.

