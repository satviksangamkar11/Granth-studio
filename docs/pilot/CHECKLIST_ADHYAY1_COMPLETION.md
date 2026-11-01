# Checklist: complete Adhyay 1 (2026-11-01)

Goal: one finished Adhyay 1 film, Marathi + Hindi, from ONE picture timeline, with every preset choice and every approved plan SAVED so it is replayed (zero model calls) and reused by Adhyay 2-21.
Legend: [x] done and verified, [~] partial, [ ] open. Item numbers in brackets point to `CHECKLIST_BUILD_PIPELINE.md` (master) or `CHECKLIST_REUSE_SHOT_PLANS.md` (R#). This file is the working order; the master keeps the detail.
Rules kept: coder model writes code + tests, Claude specs/runs/reviews; Codex (medium) review; no Kimi call without the owner's yes; record decisions in `DECISION_LOG.md`; keep `_moss/`, `_tango/` and the loop experiments out of pipeline changes.

## What Adhyay 1 already has (verified 2026-11-01)
- [x] 59 FINAL shot images + clean copies (`flow_outputs/adhyay_01/final_clean/`), bound with sha256 in `canon/packets/adhyay_01/final_image_binding.json`
- [x] Owner's real split rev9: 9 scenes, 61 shots, 73 omissions (NOT yet locked: item 15)
- [x] Voices accepted; voice library `canon/series/voices.json` (35 voices)
- [x] 11 JSON presets + index (`assets/v5_presets/`, `canon/packets/adhyay_01/presets_index.json`), Builder v2 frozen (D-017)
- [x] Docx input format fixed (I1-I3; 60 tests pass) - matters for Adhyay 2+, not for Adhyay 1
- [~] 46 MOSS sound effects for Adhyay 1+2 generated on Kaggle (`_moss/`), not yet listened to or hashed into a palette
- Note: the Nemotron Stage 1 trial (11 scenes, 34 shots, 84 omissions; 71/84 match rev9) is a TEST of the pipeline for later chapters. Adhyay 1 is built from the owner's rev9, NOT from the trial.

## Phase A - freeze and baseline
- [ ] A1 Back up + hash all Adhyay 1 data/media; byte-for-byte baseline list (item 3)
- [ ] A2 Record the frozen code commit (today `3adb09d`) in the decision log

## Phase B - owner locks (one batch, one sitting)
- [ ] B1 Lock rev9 split + EASY script + 52 core / 10 optional + look questions -> `approvals.json` via `approve.py` (item 15)
- [ ] B2 Decide each of the 73 rev9 omissions explicitly (S5: rev9 coverage receipt is NO_CHECK; "narrator or omitted" ranges; ovis 58-60)
- [ ] B3 Review the 102 `check_script` findings on the real Adhyay 1 script (item 17)
- [ ] B4 Rights route recorded (Flow clean export, ElevenLabs, platform) - required before PUBLIC release, not before rendering (item 4)

## Phase C - preset usage (the main gap)
Problem: presets 01, 02, 04, 05, 09, 11 need layer images (sky/far/mid/fg or transparent poses). Adhyay 1 has flat finals only; the 49 layer images were never made.
- [ ] C1 Shot-to-preset table for all 61 shots: preset id, roles needed, image id(s) available, flat-OK or layers-needed, NEED_NEW reason+class. Built by code from rev9 + preset index; owner reviews
- [ ] C2 Bounded preset-03 JSON variants (push in / push out / slow pan / hold), full-frame render pass, so most shots work on ONE flat image (item 30)
- [ ] C3 Test presets 05/06/07 on full frames; one real NEED_NEW (bow/blessing) (item 32)
- [ ] C4 Decide layers shot by shot: flat first; cut layers from the final only where depth is needed (A1 checklist E7)
- [ ] C5 Every NEED_NEW gets a question to the owner, never a silent fallback (N12, only for shots/cues)

## Phase D - save (so nothing is planned or paid twice)
- [ ] D1 Shot-plan records in `canon/shot_plans/`: plan id/version, ovi + beat ids, preset id + preset file hash, role -> image id + sha256, transition, source/script/timing hashes (R3)
- [ ] D2 Exact-hash replay: same inputs -> zero Kimi calls; changed input never matches silently (item 29, R4)
- [ ] D3 Role binding check against `final_image_binding.json`; missing/changed image blocks rendering (R5)
- [ ] D4 Save to series data once accepted: voices per character (21a, N2 safe refresh, N13 verified MR/HI flags), approved looks (N5), sound palette with versions (E2, N14), preset variants from C2
- [ ] D5 Retire the stale `validate_stage1.py` + old shot/sound schemas (`preset_hint`, `palette_id`) so only one preset contract exists (N10)

## Phase E - sound and speech
- [ ] E1 Owner listens to the 46 MOSS effects; keep/reject; hash the kept ones into `canon/series/sounds/palette.json` (E2, E6)
- [ ] E2 Voice clips per line, Marathi + Hindi, exact reuse key, credit receipts; Hindi labelled NOT_VALIDATED until heard (item 23)
- [ ] E3 Shared beats from both measured speech windows (item 24); cue timing "after line" = after both languages (E4)
- [ ] E4 Mix: ducking against the union of both windows, owner listening sets gain/fade (E5, S9)

## Phase F - one proof scene S4, end to end
- [ ] F1 Bind + approve S4 flat finals; decide the 3 staging warnings (daylight S4-1, pose S4-2, halo S4-4) (item 31, R7)
- [ ] F2 Render S4 from saved shot plans; mix; subtitles; both languages (item 33)
- [ ] F3 Interrupt/resume test at shot level + changed-input invalidation (R10)
- [ ] F4 Owner accepts the picture; Codex reviews the evidence (R9, R11)

## Phase G - rest of Adhyay 1
- [ ] G1 Kimi ONLY for genuinely missing shots, each with a reason, owner gate first (item 20, R8; ledger left $0.315)
- [ ] G2 Render + mix the remaining 8 scenes from saved plans; GPU/render receipts (item 34)
- [ ] G3 Export Marathi MP4 + Hindi MP4 from one picture timeline: equal frames and length (item 35)
- [ ] G4 Full test suite in one go + validate (items 38, N15); Codex review; commit + push (item 39)
- [ ] G5 One-page per-chapter runbook from what actually worked (item 36)

## Deferred to Adhyay 2 (not needed to finish Adhyay 1)
Stage 1 fidelity on new chapters (trial: 13 extra + 2 missed omissions, about 44% fewer shots than the reference; Adhyay 2 trial: missing core lines, a scene with no shots, voice collisions): N1, N3, N6, N11, S7, S10 live run, `--adhyay N` wiring (13), Adhyay 2 dry run (37), the 3 Adhyay 2 omissions (ovis 48, 142, 143).

## Owner decisions needed first
1. Go for this order (A -> G)?
2. Proof scene stays S4?
3. Layers: flat-first with preset-03 variants, layers only where needed (recommended), or make all 49 layers?
4. One sitting for the Phase B locks (73 omissions + 102 findings)?
