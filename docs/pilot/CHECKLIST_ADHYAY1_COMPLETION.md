# Checklist: complete Adhyay 1 (rev 3.1, 2026-11-01)

Goal: one finished Adhyay 1 film, Marathi + Hindi, from ONE picture timeline. Every approved shot binding is SAVED so it replays with zero new director/planning model calls, and reusable preset templates are saved SEPARATELY so Adhyay 2-21 can use them.
Legend: [x] done and verified, [~] partial, [ ] open. Item numbers in brackets point to `CHECKLIST_BUILD_PIPELINE.md` (master) or `CHECKLIST_REUSE_SHOT_PLANS.md` (R#). This file is the working order; the master keeps the detail.
Rules kept: the coder model writes code + tests, Claude specs/runs/reviews; Codex (medium) review; no Kimi call without the owner's yes; decisions recorded in `DECISION_LOG.md`; `_moss/`, `_tango/` and the loop experiments are READ-ONLY for this work (no broad cleanup, reset or `git add -A`); commit after review, push only with the owner's separate OK. Never insert artificial script lines to make a validator pass.
Rev 3 applies the owner's second audit (all points checked against the files, see the end).

## What Adhyay 1 already has (verified from files 2026-11-01)
- [x] rev9 split (`canon/director_runs/a1_split_rev9/macro_A1.json`): 9 scenes, 1 story (ovi 70-144); 73 proposed-unfilmed ovis in SIX ranges: 1-32 invocation, 33-38 commentary, 39-57 background, 58-69 background (one Shegaon view drawn from 58-60 for Scene S1 shot 1), 106-107 commentary, 145-146 closing. NOT yet approved
- [x] 59 shots (timing plan `canon/audio/A1_timing_plan.json`: planned 59, allocated 59): S1 2, S2 8, S3 6, S4 5, S5 7, S6 6, S7 9, S8 5, S9 11. The "61" in older notes and in `compare_a1.py` is the rev8 count and is WRONG for rev9
- [x] 59 FINAL clean images, one per shot, sha256-bound in `canon/packets/adhyay_01/final_image_binding.json` (same per-scene counts)
- [x] Speech: 62 lines, 124 clips (Marathi + Hindi) measured in `canon/audio/A1_eleven_measured.json`; owner accepted the voices 2026-10-26 (decision log: "do not regenerate these clips"); Hindi NOT VALIDATED. The file's status label still says DRAFT: reconcile the label, do NOT regenerate
- [x] 11 JSON presets + index (`assets/v5_presets/`, `canon/packets/adhyay_01/presets_index.json`), Builder v2 frozen (D-017)
- [~] 46 MOSS sound effects for Adhyay 1+2 (`_moss/`), not yet listened to or hashed into a palette
- Not used for Adhyay 1: the Nemotron Stage 1 trial (test of the pipeline for later chapters) and the old paid Kimi director runs of 2026-10-26. A FRESH Kimi director call is allowed (Phase K)

## Preset input contract (from the index; decides what a flat final can feed)
| Preset | Needs | Can a flat final feed it? |
|---|---|---|
| 01, 02 | several depth layers (sky/far/mid/near/fx/fg) | no |
| 03 | one flat image | YES |
| 04, 05, 06, 07, 08, 09 | transparent character / pose / face cut-outs | no, unless a NEW flat variant is built and tested separately |
| 10 | one full-frame insert | YES |
| 11 | two scene images (scene_a, scene_b) | YES (two finals) |

## Phase 0 - coder safety (before any coder-written A1 fix)
- [x] 0.1 DONE 2026-11-01 (38 tests, Codex medium READY after 3 rounds, `CODEX_N1_REVIEW.md`; policy in protected `config/codegen_policy.json`; 0 new failures vs the 5 `test_fix_loop` + 8 queue/coder baseline failures, which stay open as their own item). Close N1 (`nemotron_code.py`: approved spec root, no scratch output in `scripts/ src/ tests/ schemas/`, refuse any unfinished/unexpected FILE block) - `fix_loop.py` loads it, so it is on the A1 path. Until N1 passes, A1 code goes only through `coder_run.py` with Claude checking every written file

## Phase A - freeze and baseline
- [x] A1 Back up + hash the actual 59-shot baseline (split, binding, images, speech, timing); byte-for-byte list (item 3) DONE 2026-11-01: `canon/baselines/a1_baseline_2026-11-01.json`; 59/59 images match the binding, 124/124 speech clips match `eleven_manifest.json`, script hash = checker + measured hash, backup `D:/aai work/backups/a1_baseline_2026-11-01` 210/210 identical (189 MB)
- [x] A2 Record in the decision log: pushed baseline `3adb09d` (on GitHub) and every later local commit by hash

## Phase B - coverage, then lock (order B2 -> B3 -> B1; ONE consolidated owner sheet)
- [ ] B2 Owner approves the SIX proposed unfilmed ranges as ranges (master item S5); check ovis 58-60, which feed Scene S1 shot 1 (historical Shegaon)
- [ ] B3a The 102 checker findings = 100 "ovi has no core line" + 2 line-numbering errors (S4-L4, S4-L5). 73 of the 100 are the B2 ranges. The other 27 are ovis OUTSIDE the six ranges that lack core-line coverage: 71-83, 85, 86, 89-93, 100, 101, 103, 105, 111, 125, 131
- [ ] B3b Classify each of the 27 against the actual film treatment (`A1_story_for_approval.md`), with the source line as evidence: research-only (known: 75-82, not narrated or shown), visual-only, merged into a neighbouring line, or genuinely missing a line
- [ ] B3c Checker change (coder writes, item 17): accept approved dispositions with source-linked evidence. Smallest change: research-only and intentionally-unfilmed ovis use the EXISTING unfilmed set; only visual-only and merged-equivalent need a new disposition. No artificial script lines
- [ ] B3e Coverage count changes and must be approved, not silently redefined: the research-only ovis (75-82, eight, outside the rev9 ranges) are NEW omission decisions. If all 73 + these 8 are approved the unfilmed total is 81 (plus any other B3b research-only ovi). The owner sheet shows rev9's 73, each addition with its source evidence, and the new total; `approvals.json` records the new list and its hash
- [ ] B3d The 2 S4 numbering errors: S4-L4 = ovi 112 (core, in the timing plan), S4-L5 = ovi 111 (optional, not in the timing plan); BOTH already have Marathi + Hindi clips under these ids (`A1_eleven_measured.json`, `A1_voice_measured.json`, `A1_audio_plan.json`). Do NOT just swap ids. Either (a) a tested, lossless id migration across every dependent manifest, timing record and the script, audio bytes unchanged and hash-verified before/after, or (b) the owner approves the legacy order as an explicit checker exception. Spoken wording and audio bytes never change; no speech regeneration. Then rerun the checker; only what is left goes to the owner
- [ ] B1 ONLY THEN lock rev9 split + EASY script + 52 core / 10 optional + look questions + the dispositions -> `approvals.json` via `approve.py`, hash-based (item 15)
- [ ] B4 Rights route recorded - mandatory before PUBLIC release, not before rendering (item 4)

## Phase C - preset usage, flat-first (owner decision 2026-11-01)
Code-only preset experiments (C2) may run in parallel with Phase B.
- [ ] C1 Shot-to-preset table for all 59 shots, decided per shot from its source beat, its actual final image and the preset contract above: preset id, roles, image id + sha256, flat-OK or cut-out-needed, NEED_NEW reason + class. Code builds the draft; owner reviews
- [ ] C2 Bounded flat variants of preset 03 (push in, pull out, slow pan, hold) + full-frame render pass; use 10 and 11 where they fit (item 30)
- [ ] C3 Transparent-asset presets (04-09) only with valid cut-outs, OR a separately built and tested flat variant. Cutting a figure out of a finished image needs background repair and is never assumed lossless (items 32, A1-E7)
- [ ] C4 Cut-outs only where story or picture quality demonstrably needs them; no bulk generation of the 49 layers
- [ ] C5 Every NEED_NEW gets an owner question, never a silent fallback (N12, shots/cues only)

## Phase E-speech - freeze timing BEFORE saving shot bindings
- [ ] E2 Confirm the 124 accepted clips by hash; reconcile the DRAFT label with the 2026-10-26 acceptance; owner listens to Hindi (item 23). Reuse only, no regeneration
- [ ] E3 Freeze the shared bilingual beat timeline from both measured speech windows; cue "after line" = after both languages (items 24, E4)

## Phase I - put Adhyay 1 into the Adhyay 2 input format (needed before Phase K; found 2026-11-01)
Today `scripts/pipeline/chapter.py` special-cases Adhyay 1 with legacy files: `canon/packets/adhyay_01/adhyay_01_ovis_hj.jsonl` (fields adhyay, ovi, printed_no, text only), research = a `frozen_copies` folder, script in `docs/pilot/`. Adhyay 2+ uses the docx format: `source/ovis.jsonl` (ovi, section, original_marathi, simple_marathi, hindi, easy_english, printed_number, adhyay), `source/sections.json`, `research/packet.json` (characters, locations, objects), `script/easy.md`.
- [x] I1 DONE 2026-11-01: owner supplied `canon/test_inputs/Shri_Gajanan_Vijay_Chapter_1_Final.docx` (sha256 352fffa3...), same layout as Chapter 2. Source for Adhyay 1 in the Audited Canon docx format: the owner supplies a Chapter 1 docx like Chapter 2 (recommended: same importer, already tested), OR a code conversion of the existing data (leaves simple_marathi/hindi/easy_english/section EMPTY: nothing may be invented)
- [x] I2 DONE 2026-11-01 (canon/adhyay_01/source + research written; importer fixed: source note kept apart, colon-first names, bare PART 2 / stray table / malformed later header refused; 30 tests; Chapter 2 output byte-identical). Scratch-run findings: 146 ovis, 12 sections, 0 mismatches, no empty fields; Marathi text differs from the legacy file at exactly 5 ovis (4, 49, 91, 96, 139: one letter each = the variant readings the docx declares); the legacy file had wrong printed numbers for 41 ovis 101-145 (leading 1 dropped), the docx is right; importer gaps: the "Source register" note is parsed as a glossary object (11 objects, should be 10 + a source note) and the name of the 10th object is not split from its text. Not yet written to canon/. Run `import_canon_docx.py --adhyay 1` -> `canon/adhyay_01/source/` + `research/packet.json`; compare its 146 ovis against `adhyay_01_ovis_hj.jsonl` and report every text difference and printed-number mismatch to the owner
- [x] I3 DONE 2026-11-01 (sha256 e884d3fe... unchanged). Copy (never move) the owner's EASY script to `canon/adhyay_01/script/easy.md` (same line format already: `**S1-L1** | narrator | ovi 70 | core`); its sha256 must stay `e884d3fe...` so the 124 clips and the timing stay valid
- [x] I4 DONE 2026-11-01 (`chapter.py` + `stage1/prompts.py` A1 research special case removed; 136 tests across chapter/prompts/checker/approve/context/runner pass). Coder: drop the Adhyay 1 special case in `chapter.py` for source_ovis, research_packet and script only; audio, timing, measured, image binding keep their current paths (no file moves, Phase A hashes unchanged); tests prove A1 and A2 resolve the same way (item 13)
- [x] I5 DONE 2026-11-01 (new receipt reads canon/adhyay_01/script/easy.md: same 102 findings, same hash; old receipt kept as script_check_receipt_2026-10-29_legacy_layout.json). Run `check_script_cli.py --adhyay 1` on the new layout: same 102 findings as before (proves nothing changed), then Phase B continues on it

## Phase K - fresh Kimi director call for Adhyay 1 (owner decision 2026-11-01: allowed, same fixed rules as Adhyay 2)
Kimi directs; it does not re-split the chapter, write dialogue or timings, or replace existing assets. Its output is data only, validated by code and approved by the owner.
- [ ] K1 Contract fixes first, so the output is checked by the same rules Adhyay 2 will use: preset field = preset-index id or NEED_NEW with reason + class (21c), stale schemas retired (N10 = D6), foreign/unknown ovi rejected (N3 coverage part), only verified MR+HI voices (N13), sound ids carry a palette version (N14), questions for every NEED_NEW (N12 = C5)
- [ ] K2 Inputs fixed and hashed (from B1, E3, C2): locked rev9 split + approved dispositions, the owner's EASY script (owner gives it, not Kimi; decision 2026-10-27 #5), the 59-image catalog with sha256, the preset index + tested flat variants, the frozen beat timeline, the voice cast
- [ ] K3 Owner sets the spend before the call (provisional $5 per chapter, decision 2026-10-27 #8; total ledger cap $50 in `v5_ledger.py`); one call per scene with receipts; failed scenes rerun alone (`--reuse-from`)
- [ ] K4 Gate on the output: aggregator + advisory cross-check; zero unknown image/preset/voice/sound ids, every shot bound to one of the 59 images or a NEED_NEW, no scene without shots, no uncovered core line; then the owner reviews the shot-to-preset table (C1). A call that returns 200 but fails the gate counts as FAILED
- [ ] K5 Accepted output becomes the D1 shot bindings; NEED_NEW items listed for the owner (new image / cut-out / new preset variant)

## Phase D - save (after B1, E3 and K5, so the hashes are final)
- [ ] D1 Shot-specific approved bindings in `canon/shot_plans/`: plan id/version, ovi + beat ids, preset id + preset file hash, role -> image id + sha256, transition, source/script/timing hashes (R3)
- [ ] D2 Exact-hash replay of D1: same inputs -> zero new director/planning calls; a changed input never matches silently (item 29, R4). This only stops REPEATING a plan
- [ ] D3 Reusable preset TEMPLATES saved separately (the C2 variants + any tested flat variant), with bounds and test renders, for Adhyay 2-21
- [ ] D4 Role binding check against `final_image_binding.json`; missing/changed image blocks rendering (R5)
- [ ] D5 Series data once accepted: voices per character (21a, N2, N13), approved looks (N5)
- [ ] D6 Retire the stale `validate_stage1.py` + old shot/sound schemas (`preset_hint`, `palette_id`) (N10)
- [ ] D7 Fix `compare_a1.py` REAL_SHOTS = 61 (rev8) -> read 59 from the rev9 timing plan; write a NEW scoring receipt; keep the old `scores_receipt.json` as historical evidence

## Phase E-sound - sound palette and mix
- [ ] E1 Owner listens to the 46 MOSS effects; COPY the kept ones out of `_moss/` (read-only) and hash them into `canon/series/sounds/palette.json` with versions (E2, E6, N14)
- [ ] E4 Mix: ducking against the union of both windows, gain/fade set by owner listening (E5, S9)

## Phase F - proof scene S4 (5 shots, about 30 s; owner decision 2026-11-01)
- [ ] F1 Bind + approve the 5 S4 finals; decide the staging warnings (daylight S4-1, pose S4-2, halo S4-4) (item 31, R7)
- [ ] F2 Render S4 from saved plans; mix; subtitles; both languages (item 33). No rerun of the old paid director call
- [ ] F3 Interrupt/resume test at shot level + changed-input invalidation (R10)
- [ ] F4 TECHNICAL milestone: 5 S4 plans replayed from approved data, 5 renders, 2 synchronized language outputs, zero new director/planning model calls (review calls tracked separately), resume test passes; Codex reviews the evidence (R9, R11)
- [ ] F5 VISUAL milestone: the owner judges that the staging and shot progression do not read as a slideshow. A technical pass alone does not pass S4; if it fails, decide cut-outs or new variants for the failing shots before Phase G

## Phase G - the other 54 shots (only after F4 AND F5)
- [ ] G1 Phase K output covers the other 8 scenes; extra Kimi calls only for NEED_NEW shots, inside the owner's chapter spend (item 20, R8)
- [ ] G2 Render + mix the remaining 8 scenes from saved plans; render receipts (item 34)
- [ ] G3 Marathi MP4 + Hindi MP4 from one picture timeline: equal frames and length (item 35)
- [ ] G4 Full test suite in one go + validate (items 38, N15); Codex review; commit; push only with the owner's OK (item 39)
- [ ] G5 One-page per-chapter runbook from what actually worked (item 36)

## Go / no-go (owner 2026-11-01)
- GO: Phase 0, baseline, coverage reconciliation, code-only flat-preset work.
- GO (owner 2026-11-01): a fresh Kimi director call for Adhyay 1 under the Adhyay 2 rules, once K1-K3 are met; no need to avoid Kimi at any cost.
- NO-GO until the gates pass: declaring the A1 script locked (needs B3d), Kimi calls before K1-K3, bulk layer generation, full-film rendering (needs F4 + F5).

## Deferred to Adhyay 2 (not needed to finish Adhyay 1)
Stage 1 fidelity on new chapters (trial: 13 extra + 2 missed omissions; Adhyay 2 trial: missing core lines, a scene with no shots, voice collisions): N3, N6, N11, S7, S10 live run, `--adhyay N` wiring (13), Adhyay 2 dry run (37), the 3 Adhyay 2 omissions (ovis 48, 142, 143). (N1 moved to Phase 0.)

## Corrections log
Rev 2 (first owner audit): 59 shots not 61; 102 findings split; preset contract table; replay vs templates separated; speech reused; `_moss/` read-only; push only with OK.
Rev 3 (second owner audit, checked against the files):
1. The 27 are not proven filmed: 75-82 are research-only (`A1_story_for_approval.md` lines 113-115). `check_script.py` line 203 requires a core line for every ovi not in the unfilmed set and has no visual-only disposition -> B3b/B3c added.
2. Phase B order is now B2 -> B3 -> B1 so the lock hash is not invalidated by the S4 numbering fix.
3. Speech/timing (E2, E3) moved before D so the saved timing hashes are final.
4. B2 "S5" = master item S5; the Shegaon image is Scene S1 shot 1.
5. D7 keeps the old receipt; F4 says "zero new director/planning calls"; F5 visual (anti-slideshow) gate added.
6. N1 moved from deferred to Phase 0 (`fix_loop.py` line 130 loads `nemotron_code.py`).
Claude's refinement on point 1: research-only ovis can use the existing unfilmed mechanism; only visual-only and merged-equivalent need new checker code (smaller change).
Rev 3.1 (third owner audit, checked against the files): B3d no plain id swap for S4-L4 (ovi 112, core, timed) / S4-L5 (ovi 111, optional, untimed), both have clips -> lossless tested migration or approved legacy order; B3e research-only ovis are new omission decisions (73 -> 81 if all approved), shown and approved explicitly. Owner authorized Phase 0 and Phase A only; rev 3.1 is not yet approved as final.
