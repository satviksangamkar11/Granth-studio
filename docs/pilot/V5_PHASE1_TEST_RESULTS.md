# V5 Phase 1 test results after the owner's "Option 3" instruction (2026-10-25)

Constraints kept: Builder v2 frozen (sha256 eb99652815498d8501de4d0fe2ad84db7cba7ef3295d1bd69a4e72ecefa927ff, owner-approved, Codex SAFE); no Kimi call after the instruction; JSON-only changes; motion.py and parallax.py untouched.

## Revised test shots (JSON only)
| Shot | Change | Result |
|---|---|---|
| SB blessing | soft_warp re-aimed at the forearm/hand (u .66, v .40, radius .20), rotate -10 (gen11) and +10 (gen12) | **No visible change.** Mean grey-level difference in the hand region vs the original: 0.92 (-10) and 2.35 (+10) on a 0-255 scale; region change over the gesture 13.21 / 13.33 / 13.62. Judged on side-by-side frames 73-108 (`SB/hand_compare.jpg`). |
| SA temple | leaf sway 0.75 -> 1.4 deg (gen11) | **No measurable change** (leaf-area change 19.82 vs 19.79). |
| SC pot | unchanged | nothing demonstrated inadequate in the shot itself |
Dust, gloss and halo kept at their subtle values; not raised.

## Critical condition triggered
The blessing source image already shows the hand raised. Warping a few degrees cannot create a believable raise; the arm does not read as lifting. **Stop tuning.** This is a missing character-performance capability (needs an extra pose image, e.g. hand mid-raise, or a separate forearm layer), not a camera or renderer problem. Not fixed by code, per the owner's rule.

## Other defects found (builder behaviour, not fixable by JSON values)
- Slide/pan_bridge start frame is nearly empty or blurred: SC frame 49 (std 24.6 vs 62.5 before), SB frame 73 blurred silhouettes. Mitigation by JSON: use `cut` where a one-frame blank is unacceptable.
- Maharaj looks a little younger in some Flow images; this is image consistency, not the builder.

## Presets and reuse
11 presets in `assets/v5_presets/` (all validate with schema v2). Reuse test through the frozen builder: preset 10 on the SC "hands" image (1 asset mapping, 0 other edits) and preset 07 on the SB "react" image (1 asset mapping, 0 other edits) both rendered first time (`SC/gen13`, `SB/gen13`). motion.py preset 03 equivalent on `A1_full.png`: 144 frames, 1280x720, 6 s CPU time.

## Render times (noisy, other work running at times)
SA gen1 105 s, gen11 277 s; SB gen1 252 s, gen11 83 s, gen12 163 s, gen13 201 s; SC gen1 288 s, gen13 117 s; motion.py push 6 s.

## Kimi spend
Ledger shows $1.185 committed in P1, of which $0.857 is settled and one $0.328 reservation is OPEN (a revise call interrupted by the owner at 17:12; it may or may not have been billed). **No Kimi call was made after the owner's instruction.** Reconcile the open item against Moonshot's usage page.

## Remaining limitations
Believable hand raise (asset needed); blank/blurred first frame on slides; dust/glow barely visible at subtle settings (by design); full-motion quality not judged by metrics, only by the owner's viewing; pilot and full episodes not started.
