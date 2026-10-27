# CHECKLIST: reuse approved shot plans; Kimi writes only the new ones (owner rule 2026-10-27). Source: `CODEX_REUSE_PLAN.md`. Tick as done; never skip.

> **CURRENT OWNER RULES (2026-10-27) override any older text in this file:** the EASY script is the owner's only (Kimi never writes, edits or flags it); Kimi Stage 1 = HIGH effort, Stage 2 = LOW; delivery = TWO videos (Marathi, Hindi), same picture, same length (a multi-track master is optional); Nemotron drafts the next code, Claude verifies; Adhyay 1 Stage 1 is not repeated; 59 shots (not 61); Codex runs at medium effort. Master checklist: `CHECKLIST_BUILD_PIPELINE.md`; contracts: `PIPELINE_README.md`.


Order is fixed: 1-2 owner first, then code, then S4 as the proof. Hybrid for S4: keep the recorded draft as evidence, rebind to flat finals (preset 03; 10/11 only where they fit), NEED_NEW only for a beat that cannot be told faithfully.

- [ ] 1 owner: lock S4 source, EASY lines, voices, shared timing (Hindi status explicit)
- [ ] 2 owner: review SH_S4_* finals per beat; approve image + hash for each use
- [ ] 3 Claude + owner: shot-plan record + approval format in `canon/shot_plans/` (plan id/version, ovi + beat ids, action/pose, preset + hash, role -> image id + hash, transition, approved staging, source/script/timing hashes, owner approval + date, receipts)
- [ ] 4 Claude: exact lookup (chapter+scene+shot+input hashes) skips Kimi; candidate matching = template only; changed input never matches silently
- [ ] 5 Claude: bind roles to `final_image_binding.json` files, verify sha256; missing/changed/incompatible blocks rendering
- [ ] 6 Claude + owner: shrink Kimi contract to ids + NEED_NEW (reason + class: missing image/pose, JSON arrangement, renderer gap); code owns dialogue/claims/timing; new descriptions rejected
- [ ] 7 Claude + owner: adapt S4 to the flat finals; staging warnings (S4-1 daylight, S4-2 pose, S4-4 halo) decided; approved records saved
- [ ] 8 Kimi + owner: ONLY genuinely missing shots, each with a reason (ledger cap P4: $0.315 left)
- [ ] 9 Claude + owner: render S4; both language tracks, subtitles, cue checks; owner accepts picture
- [ ] 10 Claude + Codex: interrupt/resume + changed-input invalidation test
- [ ] 11 Codex + owner: review S4 evidence, then approve the next scenes

NOT reused blindly: pose, character look, place, prop, claim, staging, timing, translation, image, preset effect, prior approval in a new context.
