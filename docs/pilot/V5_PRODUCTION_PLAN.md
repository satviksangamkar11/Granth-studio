# GranthStudio V5 production plan — DRAFT rev 4 for owner approval

Status: DRAFT 2026-10-25, rev 4. Reviews: Codex `D:\kaggle_upload\repo_research\codex_plan_review*.md`; owner-pasted research verdicts (rev 3 and rev 4). Not approved. Owner is the only approver. Frozen V3.1/V4 documents and tags stay untouched.

Approving = new decision **D-015**. It keeps D-014's renderer decision (**Blender only, 2.5D, no full 3D, no extra renderers or paid services**) and amends D-014 in exactly two points: (1) D-014's "2.5D rigged illustrations only" becomes "2.5D illustrations; rigging is optional and limited to an action that A+C cannot communicate"; (2) D-014's first milestone ("one complete Maharaj blessing scene" with a rigged illustration) is replaced by the **A+C blessing-performance audit** (Phase 1). No other D-014 rule changes.

## 1. Format (stated explicitly)
GranthStudio produces a **motion-comic-style devotional film**: approved illustrations, camera movement, staged poses, cuts, effects, narration and music. It does **not** promise fully animated continuous character performance. Each of the 21 films is judged against this format.

## 2. Decided vs measured vs unproven
**Owner decisions:** 21 films, one per Adhyay, 10–20 min; Hindi and Marathi share assets; riso print look, simple styled figures; Kimi K3.1 Pro writes all code and shot plans; Codex reviews before code runs; owner approves everything. **The owner generates all images himself in Nano Banana (manual, no API calls from this project).**

**Measured:** Kimi K3.1 Pro produced an approved-looking 6-s riso Maharaj (drawn-by-code, ~$1.4). Free NVIDIA coders failed the same task. Blender 5.2.3 portable is installed at `D:\tools\blender`.

**Unproven:** riso look inside Blender; EEVEE on this PC; voices (all TTS options); cost per accepted finished shot; owner image time per shot.

## 3. Shot methods
| Method | Priority | Used for |
|---|---|---|
| A. Layered art + camera | High (default) | Narration, places, atmosphere — with varied moves, deliberate holds, reveals and sound, not repeated slow zooms |
| C. Pose-to-pose | High (default) | Meaningful character actions, told by staging, timing, a reaction shot and continuity |
| B. Rigged puppet | Low (optional) | Only for a specific action that A+C cannot communicate, as a limited test of that one action |
No fixed percentages: Kimi's shot planner chooses per beat; the pilot measures the real mix.

## 4. Roles
| Who | Does | Never |
|---|---|---|
| Owner | Approves text; generates images in Nano Banana to the image spec (§5); approves every gate | — |
| Kimi K3.1 Pro | Blender scene scripts, riso compositor pass, manifest interpreter, shot planner, manifests | Approves |
| Free NVIDIA models | Only after passing a JSON-only test (5 approved beats, 15 min, all must pass) | Code |
| Nemotron 3.5 Super VL | Flags defects on contact sheets | Approves |
| Claude | Harness, validators, budget ledger, sandbox, assembly glue, image-spec checklists | Animation code |
| Codex | Read-only review before any new code or add-on runs | Writes code |

## 5. Image spec (what the owner generates)
For each shot Kimi's planner lists the images needed. Defaults:
- **Method A:** one scene as separate layers — background, midground, foreground (each on plain white or transparent), same size, same framing; or one full image if layers are not possible (simpler camera move).
- **Method C:** each pose of the character on a plain background, same scale and framing as the approved reference; plus reaction/close-up images named in the shot list.
- File names follow the shot list (e.g. `A1_S02_pose2.png`), saved to one inbox folder. A checker reports missing, wrong-size or wrong-name files before Kimi starts.
- Track per accepted shot: images requested, images rejected, owner minutes.

## 6. Budget guard (Kimi only; enforced in code)
One JSON-lines ledger is the only path to Kimi; retries go through it.
1. Worst-case reservation before dispatch: counted input tokens × $2/M + `max_tokens` × $10/M (exact model ID), written to disk **before** the request.
2. Refuse if phase spent + open reservations + this reservation > phase cap, or the $50 total would be exceeded.
3. After the reply, replace with provider-reported usage. Timeout or unclear result = UNKNOWN, kept at full reservation until reconciled.
4. Proven before any paid use: synthetic test of refusal at the phase cap, the $50 cap, and after an UNKNOWN call.
Gemini is not called by this project (owner generates images manually), so no Gemini spend enters the ledger.

## 7. Phases (each needs the owner's "pass")
### Phase 0 — Prepare (cap $0, 1 day)
- Owner approves D-015 and the exact Adhyay 1 pilot passage, Marathi and Hindi lines, speakers, costume, allowed actions (`docs/pilot/SOURCE_APPROVAL_SHEET.md` pending).
- Hardware: does Blender 5.2.3 EEVEE render here; RAM; free space on D:.
- Storage rule: render in chunks of ≤ 48 frames; preflight needs 48 × frame size + 5 GB free; each chunk encoded, decoded and frame-counted before its PNGs are deleted; verified copies (size + hash) of assets, manifests, receipts and accepted clips on the owner-named backup drive before deleting anything needed to rebuild a shot.
- If EEVEE cannot render: stop; fallback §8 needs the owner's yes.

### Phase 1 — 18-second A+C proof (cap $15, 2 days)
Uses existing approved art first; any new images are generated by the owner to the §5 spec. Temporary approved narration track for timing.
1. **Test 1 (A), 6 s:** temple establishing shot — layered depth, camera move, ambient effects (light, smoke or petals).
2. **Test 2 (C), 6 s:** Maharaj blesses a devotee — three staged poses, cinematic cuts, a devotee reaction shot.
3. **Test 3 (C), 6 s:** Maharaj interacts with an object or another character — continuity across poses and camera angles.
Same riso compositor pass on all three. Limits: max 4 Kimi generations per test; 15 min per request; 1 render retry per shot; Codex reviews each code version.
- **A+C blessing-performance audit (replaces D-014's rigged blessing milestone):** owner watches the 18 s **with audio and once without audio**. Pass needs all: approved riso appearance; stable identity; each action understandable **without narration**; no distracting continuity errors; render ≤ 10 min per 6-s shot; spend ≤ $15. Written audit of joins/seams, hands, staging, continuity, render time and cost, cost per accepted shot and owner image minutes; owner signs.
- If an essential action fails: **limited B test for that one action only** (inside the Phase 1 cap). No rigging framework.
  - **COA Tools 2 test first (max 3 active hours, 3 attempts):** release v2.3.0 zip, its sha256 recorded before install; Codex reviews before install; upstream tests Blender 5.1, so 5.2.3 compatibility is unproven until this test passes. Fixture = the owner's approved parts for that action. **Pass needs all of:** parts import as one character; the failing action's limbs bend to the approved pose without tearing or gaps at the joints; file saves and reopens intact; Blender renders the 144-frame test shot **headless** from the command line with exactly 144 frames written; results saved.
  - **Any item fails → COA Tools 2 is rejected**; Kimi writes a custom rig for that one action within the same cap. If that also fails the audit, the action is told by C with extra staging, or blocked for owner decision.

### Phase 2 — Reusable kit + JSON driver (cap +$20, 3 days)
Approved Maharaj pose library, temple set layers, camera-move and effect presets, cut/hold rules, one manifest interpreter. Manifests hold only IDs, times and bounded numbers — no code.
- Gate: shot changed through JSON alone; identical re-render of any frame; kill and resume; corrupt cached clip rejected; an asset change re-renders only dependent shots.

### Phase 3 — Bilingual 60-second pilot (cap +$15, 2 days)
- Exact Marathi and Hindi scripts approved first.
- TTS: one candidate + one fallback chosen by an owner listening test from Indic Parler-TTS, IndicF5, Indic-Speak (Indic Open Model License v1.0 + Llama 3.2 licence; owner reads and accepts licences himself) — **all NOT VALIDATED until executed**; ≤ 2 h setup, ≤ 2 Kaggle GPU-hours. Scratch narration is timing-only; released audio needs recorded licence/consent.
- Timing: beats = owner-marked meaning units measured from each language's aligned audio; plan with `max(Hindi, Marathi) + 0.4 s`; for the shorter language trim only holds/cutaways at assembly, never speech or a required gesture.
- Lip-sync only for an on-screen speaker; Rhubarb phonetic test on one real line per language, owner pass/fail recorded; fail → loudness-driven open/closed mouth.
- Gate: both releases complete, correct meaning and Devanagari, stable riso texture, actions readable, owner approval; ≤ $1 Kimi spend per finished minute; owner review ≤ 10 min per finished minute (both languages); owner image minutes per finished minute recorded.

### Phase 4 — First full Adhyay (separate approval, cap +$40, 10 working days)
After a chapter shot/image list. Measure accepted minutes, method mix, cost per accepted shot, owner image and review time, storage; only then quote the remaining 20 films.

**Total authorised by approving: $50 Kimi spend for Phases 0–3.** Phase 4 needs a new yes.

## 8. Fallback
If Blender fails Phase 0 (no working EEVEE) or the Phase 1 riso-look gate: drawn-by-code (MIT, CPU + Chrome, produced the approved riso reference) with the same shot grammar, only with the owner's yes.

## 9. Risks and controls
| Risk | Control |
|---|---|
| Films feel like slideshows | Varied camera grammar, holds, reveals, sound design; watched with and without audio at each gate |
| Pose changes don't tell the action | Staging + reaction shot + timing; "understandable without narration" gate |
| Image work underestimated | Cost/time per accepted shot measured; image spec + checker; approved poses reused |
| Identity drift across images | Owner uses the approved reference each time; poses approved and frozen |
| Riso look fails in Blender | Phase 1 gate; fallback §8 |
| Overspend | Ledger refuses Kimi calls; no project Gemini calls |
| Wrong meaning | Owner approves exact text first |
| Disk full | Chunked renders, preflight, verified backup |
| Free endpoints fail | Kimi default |

## 10. Not doing
Full 3D, Hunyuan, Mixamo, diffusion video, Spine, AGPL code, API image generation, a rigging framework before an action needs it, new style exploration before Phase 4.
