# Checklist: complete Adhyay 1 (rev 2, 2026-11-01)

Goal: one finished Adhyay 1 film, Marathi + Hindi, from ONE picture timeline. Every approved shot binding is SAVED so it replays with zero model calls, and reusable preset templates are saved SEPARATELY so Adhyay 2-21 can use them.
Legend: [x] done and verified, [~] partial, [ ] open. Item numbers in brackets point to `CHECKLIST_BUILD_PIPELINE.md` (master) or `CHECKLIST_REUSE_SHOT_PLANS.md` (R#). This file is the working order; the master keeps the detail.
Rules kept: the coder model writes code + tests, Claude specs/runs/reviews; Codex (medium) review; no Kimi call without the owner's yes; decisions recorded in `DECISION_LOG.md`; `_moss/`, `_tango/` and the loop experiments are READ-ONLY for this work (no broad cleanup, reset or `git add -A`); commit after review, push only with the owner's separate OK.
Rev 2 corrects rev 1 after the owner's accuracy audit (all points checked against the files, see the end).

## What Adhyay 1 already has (verified from files 2026-11-01)
- [x] rev9 split (`canon/director_runs/a1_split_rev9/macro_A1.json`): 9 scenes, 1 story; 73 unfilmed ovis in SIX ranges: 1-32 invocation, 33-38 commentary, 39-57 background, 58-69 background (one Shegaon view drawn from 58-60), 106-107 commentary, 145-146 closing. NOT yet approved (item 15)
- [x] 59 shots (timing plan `canon/audio/A1_timing_plan.json`: planned 59, allocated 59): S1 2, S2 8, S3 6, S4 5, S5 7, S6 6, S7 9, S8 5, S9 11. The "61" in older notes and in `compare_a1.py` is the rev8 count and is WRONG for rev9
- [x] 59 FINAL clean images, one per shot, sha256-bound in `canon/packets/adhyay_01/final_image_binding.json` (same per-scene counts)
- [x] Speech: 62 lines, 124 clips (Marathi + Hindi) measured in `canon/audio/A1_eleven_measured.json`; owner accepted the voices 2026-10-26 (decision log line 26: "do not regenerate these clips"); Hindi NOT VALIDATED. The file's status label still says DRAFT: reconcile the label, do NOT regenerate
- [x] 11 JSON presets + index (`assets/v5_presets/`, `canon/packets/adhyay_01/presets_index.json`), Builder v2 frozen (D-017)
- [~] 46 MOSS sound effects for Adhyay 1+2 (`_moss/`), not yet listened to or hashed into a palette
- Not used for Adhyay 1: the Nemotron Stage 1 trial (test of the pipeline for later chapters) and the old paid Kimi director runs of 2026-10-26 (made before the images were final and before the preset-id contract)

## Preset input contract (from the index; decides what a flat final can feed)
| Preset | Needs | Can a flat final feed it? |
|---|---|---|
| 01, 02 | several depth layers (sky/far/mid/near/fx/fg) | no |
| 03 | one flat image | YES |
| 04, 05, 06, 07, 08, 09 | transparent character / pose / face cut-outs | no, unless a NEW flat variant is built and tested separately |
| 10 | one full-frame insert | YES |
| 11 | two scene images (scene_a, scene_b) | YES (two finals) |

## Phase A - freeze and baseline
- [ ] A1 Back up + hash all Adhyay 1 data/media; byte-for-byte baseline list (item 3)
- [ ] A2 Record in the decision log: pushed baseline `3adb09d` (on GitHub) and every later local commit by hash

## Phase B - owner approvals: ONE consolidated sheet, one sitting
- [ ] B1 Lock rev9 split + EASY script + 52 core / 10 optional + look questions -> `approvals.json` via `approve.py` (item 15)
- [ ] B2 Approve the SIX unfilmed ranges as ranges (not 73 separate items); check ovis 58-60, which feed the opening Shegaon image (S5)
- [ ] B3 The 102 checker findings are 100 "ovi has no core line" + 2 line-numbering errors (S4-L4, S4-L5). 73 of the 100 are the unfilmed ranges (closed by B2). The other 27 are FILMED ovis with no core line: 71-83, 85, 86, 89-93, 100, 101, 103, 105, 111, 125, 131. Each needs a disposition (visual-only / narrated / line missing). Fix the 2 numbering errors. Rerun the checker after B2; only what is left goes to the owner (item 17)
- [ ] B4 Rights route recorded - mandatory before PUBLIC release, not before rendering (item 4)

## Phase C - preset usage, flat-first (owner decision 2026-11-01)
- [ ] C1 Shot-to-preset table for all 59 shots, decided per shot from its source beat, its actual final image and the preset contract above: preset id, roles, image id + sha256, flat-OK or cut-out-needed, NEED_NEW reason + class. Code builds the draft; owner reviews
- [ ] C2 Bounded flat variants of preset 03 (push in, pull out, slow pan, hold) + full-frame render pass; use 10 and 11 where they fit (item 30)
- [ ] C3 Transparent-asset presets (04-09) only with valid cut-outs, OR a separately built and tested flat variant. Cutting a figure out of a finished image needs background repair and is never assumed lossless (items 32, A1-E7)
- [ ] C4 Cut-outs made only for shots where story or picture quality demonstrably needs them; no bulk generation of the 49 layers
- [ ] C5 Every NEED_NEW gets an owner question, never a silent fallback (N12, shots/cues only)

## Phase D - save
- [ ] D1 Shot-specific approved bindings in `canon/shot_plans/`: plan id/version, ovi + beat ids, preset id + preset file hash, role -> image id + sha256, transition, source/script/timing hashes (R3)
- [ ] D2 Exact-hash replay of D1: same inputs -> zero model calls; a changed input never matches silently (item 29, R4). This only stops REPEATING a plan; it does not make plans reusable across chapters
- [ ] D3 Reusable preset TEMPLATES saved separately (the C2 variants + any tested flat variant), with bounds and test renders, for Adhyay 2-21 where images and timings change
- [ ] D4 Role binding check against `final_image_binding.json`; missing/changed image blocks rendering (R5)
- [ ] D5 Series data once accepted: voices per character (21a, N2, N13), approved looks (N5), sound palette with versions (E2, N14)
- [ ] D6 Retire the stale `validate_stage1.py` + old shot/sound schemas (`preset_hint`, `palette_id`) (N10)
- [ ] D7 Fix `compare_a1.py`: REAL_SHOTS = 61 is the rev8 count; read 59 from the rev9 timing plan, rescore the trial (it is 34 vs 59 shots, not 34 vs 61)

## Phase E - sound and speech (REUSE, no regeneration)
- [ ] E1 Owner listens to the 46 MOSS effects; COPY the kept ones out of `_moss/` (read-only) and hash them into `canon/series/sounds/palette.json` (E2, E6)
- [ ] E2 Reuse the 124 accepted clips; reconcile the DRAFT label with the 2026-10-26 acceptance; owner listens to Hindi (item 23)
- [ ] E3 Shared beats from both measured speech windows; cue "after line" = after both languages (items 24, E4)
- [ ] E4 Mix: ducking against the union of both windows, gain/fade set by owner listening (E5, S9)

## Phase F - proof scene S4 (5 shots, about 30 s; owner decision 2026-11-01)
- [ ] F1 Bind + approve the 5 S4 finals; decide the staging warnings (daylight S4-1, pose S4-2, halo S4-4) (item 31, R7)
- [ ] F2 Render S4 from saved plans; mix; subtitles; both languages (item 33). No rerun of the old paid director call
- [ ] F3 Interrupt/resume test at shot level + changed-input invalidation (R10)
- [ ] F4 MILESTONE: 5 S4 plans replayed from approved data, 5 renders, 2 synchronized language outputs, zero model calls, resume test passes; owner accepts; Codex reviews the evidence (R9, R11)

## Phase G - the other 54 shots
- [ ] G1 Kimi ONLY for genuinely missing shots, each with a reason, owner gate first (item 20, R8; ledger left $0.315)
- [ ] G2 Render + mix the remaining 8 scenes from saved plans; render receipts (item 34)
- [ ] G3 Marathi MP4 + Hindi MP4 from one picture timeline: equal frames and length (item 35)
- [ ] G4 Full test suite in one go + validate (items 38, N15); Codex review; commit; push only with the owner's OK (item 39)
- [ ] G5 One-page per-chapter runbook from what actually worked (item 36)

## Go / no-go (owner 2026-11-01)
- GO: baseline, approval reconciliation, flat-first preset mapping, deterministic shot-plan saving, the S4 proof. Code-only preset experiments (C2) may run while Phase B waits.
- NO-GO until the gates pass: more Kimi spending, bulk layer generation, full-film rendering.

## Deferred to Adhyay 2 (not needed to finish Adhyay 1)
Stage 1 fidelity on new chapters (trial: 13 extra + 2 missed omissions; Adhyay 2 trial: missing core lines, a scene with no shots, voice collisions): N1, N3, N6, N11, S7, S10 live run, `--adhyay N` wiring (13), Adhyay 2 dry run (37), the 3 Adhyay 2 omissions (ovis 48, 142, 143).

## Rev 2 corrections (owner audit 2026-11-01, each checked against the files)
1. 59 shots, not 61 (timing plan + image binding agree; 61 = rev8).
2. 102 findings = 100 no-core-line + 2 S4 numbering; 73 are the unfilmed ranges, 27 are filmed ovis needing a disposition (this last split is Claude's addition).
3. Preset contract: 04-09 need transparent cut-outs, 10 and 11 take full frames; rev 1 wrongly listed 11 as layered and missed 07/08.
4. Exact replay and reusable templates are separate items (D2, D3).
5. Speech is reused, not regenerated; `_moss/` read-only; push only with the owner's OK.
