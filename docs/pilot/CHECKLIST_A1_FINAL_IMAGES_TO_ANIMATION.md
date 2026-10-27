# CHECKLIST: Adhyay 1 final images -> clean images -> animation (owner rule 2026-10-27: always work from a checklist, tick as done, never redo or skip)

Legend: [x] done and verified, [ ] open, [~] in progress. Update this file after every step.

## A. Final shot images (DONE)
- [x] 59 shots chosen, copied to `flow_outputs/adhyay_01/final/<SHOT>.png` (2752x1536), list `FINAL_IMAGE_LIST_A1.md/.json`
- [x] Codex end check passed 57/59 in the final rounds; SH_S9_11 v06 and SH_S2_08 v04 checked by Claude only
- [x] Folder audit ALL OK; raw downloads match filed copies
- [x] Decisions + lessons written to DECISION_LOG.md, NEXT_STEPS_PLAN.md

## B. Watermark removal (Flow sparkle, bottom-right) with `scripts/image_trials/v5_watermark.py` (OpenCV masked repair; owner permission 2026-10-25)
- [x] Inbox built: `flow_outputs/adhyay_01/_wm_inbox/` (59 finals + template C2_p2_hands.png)
- [x] v1 script run (v5_watermark.py): INCOMPLETE - it removed only the small sparkle and left faint traces; the BIG sparkle (on 17 shots) stayed. Superseded.
- [x] v2 written: `scripts/image_trials/wm_clean_v2.py` (two sparkle templates, small on all 59, big on the 17 shots listed in BIG_ON; outside-mask pixels asserted identical)
- [x] 59 v2 results in `flow_outputs/adhyay_01/final_clean/<SHOT>.png` (template file not included)
- [x] Verified: size 2752x1536, changes only inside the bottom-right 340 px; corner before/after sheets viewed (59 small + 17 big removed). Minor smudges where the star sat on detailed art: SH_S5_03, SH_S5_06, SH_S7_02, SH_S9_01, SH_S9_07 (optional manual touch-up)
- [x] Haiku agent corner check (`final_clean/HAIKU_CORNER_CHECK.md`): 49 clean, 9 smudge, 1 residual (SH_S8_04 big star, not in my list) -> fixed: SH_S8_04 added, clone-patch repair added for textured art (SH_S6_05 roof blotch fixed); re-saved final_clean
- [x] Remaining faint smears (acceptable; corner is mostly cropped by camera pushes; optional manual touch-up): SH_S5_03, SH_S5_06, SH_S7_02, SH_S8_04, SH_S9_01
- [x] Final clean list + hashes: `final_clean/FINAL_CLEAN_LIST_A1.json` (59 entries, changes only in the bottom-right 340 px)
- [ ] Terms note recorded: Codex warned that Google may require an officially permitted watermark-free export; owner confirmed removal for his account (2026-10-25) - keep that evidence

## B2. Full watermark removal CONFIRMED (2026-10-27 21:40)
- [x] Numeric test on all 59: small-star contrast ~30 -> ~1.5 after; big star (17 shots) ~32 -> ~3.5; 8 worst frames checked at 3x zoom: no star remains
- [x] 4 tiny line-art blemishes where a star sat on a crack/fold (optional touch-up): SH_S7_02, SH_S5_03, SH_S5_06, SH_S9_06

## C0. Study of the last two animation renders (v5_phase1_v2/SB/gen13 + SC/gen13, 2026-10-25)
- [x] What: 6 s (144 frames, 24 fps, 1280x720) slow camera move over ONE held picture + tiny breathing/drift, gradient backdrop, subtle gloss/dust/vignette; no limb or face animation
- [x] How: shot.json (data) -> frozen Builder v2 (build_scene.py, Blender 5.2.3 EEVEE, alpha image planes at depths, dolly camera, compositor glow) -> frames rendered in 3 chunks of 48 -> ffmpeg join -> shot.mp4 + validation.txt; 117-201 s per shot; same builder, only the preset JSON + one asset mapping changed (reuse proof)
- [ ] Proof render of 3 of OUR final_clean shots (motion.py preset 03, 6 s CPU each) to judge the look in motion (needs owner yes)

## C. Understand the film pipeline (Kimi director -> JSON -> Blender)
- [x] Codex (read-only) advice: `final_clean/CODEX_PIPELINE_ADVICE.md` (last Kimi call = macro repair in a1_kimi_plan2, 2026-10-26 15:50, kimi-k3.1-pro, 28.9 s, 15,295+1,064 tokens, $0.04123; result superseded by rev9)
- [x] Claude explained to the owner (chat, 2026-10-27)
- [ ] Decide the layers question (49 layers: cut from finals vs Flow)
- [ ] Open owner decisions listed in NEXT_STEPS_PLAN.md

## D. Then (not started)
- [ ] Kimi director per scene with the final clean image ids (cap, effort low, cached prefix)
- [ ] Blender render of one scene as a test (frozen builder v2, JSON presets)
- [ ] Sound + mix, captions, bilingual
- [ ] Commit (tests, validate, Codex review; never push)

## E. Codex recommended order (prove ONE scene first; do NOT generate all 49 layers, direct all scenes or start full production yet)
- [ ] E1 owner picks the proof scene + gate (D-017 quality test)
- [ ] E2 owner: source/timing gates for that scene (EASY lines vs source, voices, Marathi+Hindi timing)
- [ ] E3 owner: reconcile Kimi spend on the dashboard, decide the cap (P4 test cap $1 now)
- [ ] E4 Claude: bind shot ids -> final_clean files + hashes, expand preset roles into builder records, add bounded sound cues; Codex reviews
- [ ] E5 Kimi directs only that scene; validator + owner review
- [ ] E6 Blender render + mix of the proof (few shots), check recovery after interruption
- [ ] E7 layers decided shot by shot: try flat image first; cut layers from the final only where depth is needed
- [ ] E8 only after the proof passes: remaining scenes
