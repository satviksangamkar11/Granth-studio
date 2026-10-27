# FINAL ARCHITECTURE PLAN: the fixed pipeline for Adhyay 1-21 (merged 2026-10-27)

> **CURRENT OWNER RULES (2026-10-27) override any older text in this file:** the EASY script is the owner's only (Kimi never writes, edits or flags it); Kimi Stage 1 = HIGH effort, Stage 2 = LOW; delivery = TWO videos (Marathi, Hindi), same picture, same length (a multi-track master is optional); Nemotron drafts the next code, Claude verifies; Adhyay 1 Stage 1 is not repeated; 59 shots (not 61); Codex runs at medium effort. Master checklist: `CHECKLIST_BUILD_PIPELINE.md`; contracts: `PIPELINE_README.md`.


Sources argued claim by claim: Codex GPT-6-Sol high (`CODEX_FULL_ARCHITECTURE.md`, `CODEX_IMAGE_LESSONS.md`), Opus 5.5 reviews, Claude's own checks. Facts mostly held (about 60 of 71 claims checked held; weak: "Kimi invented images" is really a contract fault because the prompt tells Kimi to declare images; line `v5_blender.py:133` is really 99-100; template matching and 5 status labels are over-built). Status: a PLAN. Nothing here is built or approved yet.

## 1. The owner's rules, fixed
- After Adhyay 1 the pipeline is FIXED: a chapter supplies DATA, the same commands run it, zero code diff for Adhyay 2 is the freeze test.
- Same kind of animation = reuse the saved preset / shot plan, no Kimi. New animation = Kimi writes it (as JSON data only), tests + owner approve, saved. No model writes Blender/animation code (D-017; Builder v2 frozen).
- Kimi works in TWO stages. Stage 1 (all references in -> scenes, image briefs, EASY Marathi+Hindi draft lines, voice/audio plan, sound-effect suggestions, open questions). Stage 2 (animation: reuse lookup first; Kimi only for unresolved shots; picks catalog ids + preset; NEED_NEW otherwise).
- ElevenLabs makes the voices and a reusable sound-effect pack once; the pipeline suggests the effects per scene.
- One picture track, two audio tracks (one master for both languages; the owner does not want separate videos). Shared beat sized to the longer measured line; speech never sped up or cut.

## 2. Pipeline (stage: runner -> gate)
0 Source lock: code -> owner approves hashes (A2 needs its Marathi text checked against the printed book).
1 Kimi Stage 1 (capped ledger) -> code checks ovi coverage/duplicates -> owner edits + approves split, EASY wording, look questions as ONE batch.
2 Script and canon: code -> owner.
3 Voices + measurement: ElevenLabs eleven_v4, one call per line, credit ledger -> owner listens, accepts.
4 Shared beats + image jobs: code (--no-floor timing, both durations, crossings) -> owner approves count/timing/briefs.
5 Images: Flow agents (exact-title filing, first-three-per-scene check) -> Claude review + owner contact sheet -> clean (per-chapter watermark data) -> catalog with sha256.
6 Kimi Stage 2: code reuse lookup first (exact hash match replays a saved scene file); Kimi only for gaps, ids only, NEED_NEW with reason/class -> owner approves each scene.
7 Render + mix: motion.py (flat) / Builder v2 (layers) -> both language mixes, subtitles, effect cues checked against both speech windows.
8 Master: one file with 1 picture, 2 audio, 2 subtitle streams; if a platform cannot switch tracks, export per-language copies from the SAME picture master.
Receipts only where money, owner approval or images are at stake (paid calls, approvals, image provenance, shot render hash). Statuses: DRAFT / APPROVED(hash); STALE is computed from hashes.

## 3. Libraries that persist
`assets/v5_presets/` (11 recipes + index, versioned, sha256, render receipt); `canon/shot_plans/A<N>/S<x>.json` (one file per scene; exact replay only); `canon/series/` (character/place/prop data versioned by chapter state, voices, glossary, sound palette `sounds/palette.json` with hashed WAVs and a rights note); per chapter `canon/adhyay_NN/` (source, EASY script, bible, image catalog, audio data, `approvals.json`).

## 4. Decisions I made where the reviewers differed
- No new 10-command CLI: add `--adhyay N` + a data path to the existing scripts, plus a one-page runbook (less new code to test).
- Exact-hash replay only; no cross-scene template matching (Kimi Stage 2 costs about $0.04-0.12 a scene; reuse buys consistency, which comes from the catalog and presets).
- ONE master for both languages stays the goal (owner's wish); two language copies only as fallback.
- Image review: Claude + owner contact sheet; Codex only for disputes (owner: no more Codex for finals).
- Render resume at shot level (a shot is 2-3 min) not chunk level.
- Keep Codex's point: S4 flat proof is not enough; one real NEED_NEW case (bow/blessing pose) must work before Adhyay 1 closes.
- parallax.py is out of the A1 pipeline until a depth map exists.

## 5. Gaps both Codex answers missed (now in the checklist)
Who writes A2's EASY script (Kimi drafts, owner edits: needs the owner's yes); Flow agents not yet authorised (A3 follow-up 9 PROPOSED); no per-chapter cap ($50 Kimi cap covers phases 0-3; first full Adhyay needs its own approval; ElevenLabs Starter 30,000 credits/month vs about 4-9k per chapter); about 1,250 images over 21 chapters need batch approval; `opencv-python` used by `wm_clean_v2.py` is not an approved dependency; `easy_script.py` defaults to the A1 file; rights/terms (Flow watermark-free export, ElevenLabs sound use after cancelling, platform track switching).

## 6. MASTER CHECKLIST (B = before Adhyay 1 is declared complete; D = Adhyay 2 dry run). Tick when done; never skip.
### B
- [ ] B1 owner: confirm Flow agents (A3 follow-up 9) + decide `opencv-python` | done: both in DECISIONS.md
- [ ] B2 owner+Claude: per-chapter caps (Kimi $, ElevenLabs credits); reconcile both dashboards; fix Kimi ledger rates | done: no open reservation, caps in ledger config
- [ ] B3 owner: approve ONE batch: rev9 split hash, EASY script (52 core / 10 optional), 16 look questions | done: `approvals.json`
- [ ] B4 owner: choose remaining voices, accept clips | done: voice map complete, hashes
- [ ] B5 owner+Claude: approve 59 images by contact sheet + exceptions; fix SH_S8_04 star | done: hashes in `approvals.json`
- [ ] B6 Claude: create `canon/adhyay_01/`; move data out of `a1_audio_spec`, `build_shot_jobs`, `build_final_set`, `wm_clean_v2`, `easy_script` default; `--adhyay N` | done: A1 outputs byte-identical
- [ ] B7 Claude: character/place/style cues into versioned series data; code fills the prompt template | done: no A1 names in code
- [ ] B8 Claude: provenance fix (actual prompt hash, model from screen, edit id per chosen version) | done: test
- [ ] B9 Claude+owner: Kimi Stage 1 contract (scenes, image briefs, EASY drafts, sound suggestions, questions) | done: missing/duplicate ovi fails, fixture passes
- [ ] B10 Claude+owner: Stage 2 catalog-id contract (remove `images_needed`) | done: unknown id / changed hash / wrong role fail (DONE already: scene-prefix rule, packet bilingual beats)
- [ ] B11 Claude: shot-plan files per scene, exact replay | done: same inputs -> no Kimi call; changed input blocks
- [ ] B12 Claude+owner: test presets 05/06/07 with full frames (free renders) | done: owner verdict
- [ ] B13 Claude: render resume at shot level | done: killed run resumes equal to a clean run
- [ ] B14 Claude+owner: S4 end to end, flat images, both audio, subtitles | done: owner watches, all speech complete
- [ ] B15 Kimi+owner: one real NEED_NEW (bow/blessing) | done: approved, no Builder change
- [ ] B16 owner+Claude: sound pack v1 (about 25 sounds, defaults per preset/beat type, rights note) | done: hashed files + credit receipts
- [ ] B17 Claude+owner: render+mix rest of A1; one master (fallback per-language copies) | done: owner accepts full film
- [ ] B18 Claude (Codex reads): one-page per-chapter runbook; tests; commit | done: fresh session can run it
### D (Adhyay 2 proof)
- [ ] D1 A2 Marathi text checked vs printed book | D2 Kimi Stage 1 on A2; owner edits | D3 voices + timing | D4 sheets + Flow images (first-three check) | D5 watermark data for A2 | D6 Stage 2 + one scene render; `git diff` shows no change under scripts/ or src/ -> freeze

## 7. Owner decisions needed (my recommendation first)
1 Flow agents authorised (A3 f/u 9): yes. 2 Kimi drafts new preset/shot-plan JSON only (never code), tested + approved: yes. 3 Bounded JSON-only variants of preset 03 (push in/out, pan L/R, start framing): yes, each tested. 4 Layers: flat first, cut layers only where a beat needs depth. 5 Kimi drafts EASY Marathi/Hindi for A2+, owner edits: yes. 6 Batch approval per chapter (contact sheet + exceptions): yes. 7 Hindi stays NOT_VALIDATED but measured and used: decide release status. 8 Per-chapter caps: you set the numbers. 9 `opencv-python` as an approved dependency: yes. 10 Delivery: one master, fallback copies; test your real destinations. 11 Rights checks (Flow clean export route, ElevenLabs sound terms).

## 8. OWNER ANSWERS (2026-10-27) - see DECISION_LOG.md. Changes to this plan: item 5 = owner supplies the EASY script (no Kimi draft); delivery = TWO videos, same picture + same length, Marathi and Hindi (B17 changes; multi-track master optional); caps provisional Kimi $5/chapter, ElevenLabs 12,000 credits; B1 Flow agents + opencv-python = DONE (approved).

## 9. KIMI WORK PLAN (Codex GPT-6-Sol, `CODEX_KIMI_WORK_PLAN.md`; accepted by Claude 2026-10-27). Tick when done.
Findings on the pasted advice: Kimi never touches the EASY script (the owner gives the confirmed perfect script; code only checks format/coverage and reports); effort high is UNPROVEN (S4 at low was VALID + Nemotron PASS for $0.0724) so test low vs high on one fixed scene before changing; max_tokens 32768 reserves $0.357 and is REFUSED by the P4 cap ($0.315 left); the pasted per-chapter prices are forecasts, not measurements; prefix caching needs identical bytes and is not "sent once".
Plan: Stage 1 = compact scene map (scene id, ovi ids, goal/turn, owner-script line ids, short image briefs, existing character/place ids, sound-palette ids, open questions), effort HIGH (owner 2026-10-27: good shot planning and prompts), about 8,192 completion tokens per scene or small group; Adhyay 1 Stage 1 is NOT repeated; code builds the full Flow prompts from approved data. Stage 2 = unresolved shots only, ids + held pose/staging + transition or NEED_NEW, low effort, 2,048-4,096 tokens. Every paid call: free schema/catalog pre-check, free NVIDIA dry run, ledger reservation, ONE call, no auto repair. Provisional chapter budget $1 Stage 1 + $3 Stage 2 + $1 contingency.
- [ ] K1 owner script = Stage 1 input only | [ ] K2 delivery names both same-length exports | [ ] K3 lock source/script/canon hashes | [ ] K4 chapter + stage Kimi caps in the ledger (owner sets allocation) | [ ] K5 compact Stage 1 schema + fixtures | [ ] K6 free NVIDIA image briefs vs owner review | [ ] K7 run only needed Stage 1 scene groups | [ ] K8 Flow prompts built from approved data | [ ] K9 catalog-id-only Stage 2 schema | [ ] K10 exact-hash replay | [ ] K11 low/high A/B on one fixed small scene (owner agrees before spending) | [ ] K12 one preset-03 variant + one real NEED_NEW | [ ] K13 save approved JSON + render receipts | [ ] K14 export + inspect Marathi and Hindi videos (same picture, same length)
Experiments are cheap (each about $0.02-0.08, A/B pair expected under $0.20, unverified). Kimi cannot create images, move a limb from a held pose, change Builder v2 or write code.


## 10. Latest owner changes (2026-10-27): Stage 1 effort HIGH; Stage 2 LOW; EASY script is the owner's only; Adhyay 1 Stage 1 not repeated; Nemotron drafts the next code (Claude verifies); full pipeline contracts in `PIPELINE_README.md`; build order in `CHECKLIST_BUILD_PIPELINE.md`.
