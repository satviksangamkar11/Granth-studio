# GranthStudio V5 final architecture — DRAFT D-018 rev 2 (not approved)

Inputs: owner's 19 reference screenshots, analysed by three agents (`D:\kaggle_upload\repo_research\style_pramana.md`, `style_others.md`, `style_gap.md`) and spot-checked by Claude; Phase 1 results; D-012 to D-017; Codex review `codex_d018.md` (7 MAJOR, all addressed below). Values marked (obs) are visible in the stills; (inf) are inferred or estimated pixel values.

## 1. What the references do that we don't
| Reference technique | Ours today |
|---|---|
| Many layers: sky, far, mid, subject, props, foreground framing (obs; pramana ≈8–10 inf) | 1–4 layers; SB/SC backgrounds empty |
| Soft drop shadow under pieces (≈8–10 px offset, 12 px blur, 40 %, inf) + paper grain (obs) | none — figures float |
| Graded blur: background slight, foreground strong (obs) | none |
| One tinted palette per scene + gold accent (obs) | uneven |
| Hinged limbs swing while the rest is locked (Madhubani arms/sword 20–45°, inf from frame pairs) | rigid poses; soft_warp invisible |
| Ambient life: 12–20 particles, scrolling water/ribbon, drifting flags (obs/inf) | dust barely visible |
| Captions 2–3 words, bold, lower third, gold keyword (obs) | none |
| Title cards, counters, decorative border (obs) | none |
| Short beats 3.5–6 s, small dolly (inf) | 6 s shots |
**Conclusion:** the gap is mostly art density and finishing (no code), then one motion capability (hinged rotation), not the renderer.

## 2. Pipeline (keeps D-017: simplest renderer, JSON only, no per-shot Kimi)
Approved text → shot list (by hand from style-pack shot types; Kimi optional, cents) → owner makes images in Flow from the pack's prompt templates → asset prep scripts ($0) → render per shot (motion.py | parallax.py | Blender v2 or v2.1) → ffmpeg finishing ($0: grade, grain, border, particle overlay, captions, title cards) → owner review → JSON-only fixes.

## 3. Eight-layer scene recipe (fits schema v2's 8-layer limit)
| Layer | Content | Depth | Notes |
|---|---|---|---|
| L1 | sky + far hills (one plate) | 10 | slight blur baked in prep |
| L2 | mid environment (temple / village / trees) | 6 | |
| L3 | ground plate **with baked contact shadows** for static figures | 4 | shadows made in prep from the figure alpha |
| L4 | character A (clean body plate) | 2.5 | if hinged: arm removed, overlap area painted |
| L5 | character A hinged part (arm/forearm), only when needed | 2.4 | its own transform-matched shadow or none |
| L6 | character B | 2.5 | |
| L7 | props (lamp, pot, flags) | 2 | |
| L8 | foreground framing (pillars/leaves), **pre-blurred in prep** | 0.5 | |
Particles, grain, vignette, grade, border and captions are added in ffmpeg, so they cost no layer. Dolly: references use about 4–6 % (inf); our validator demands ≥0.12 zoom change per shot (owner's "no basic zooms" rule) — kept as is; a pan can carry motion in segments, and the rule can be relaxed only on the owner's word.

## 4. Style pack — reuse with zero Kimi
`style_packs/<name>_v1/` with a `manifest.json` that pins: schema version, builder sha256, renderer versions, font files and hashes, every asset role → file mapping with pixel size and pivot (for hinged parts), and the sha256 of every file. Contents: `style.md` (rules, do/don't, approved frames), `palette.json` (per mood + accent), `prompts/` (Flow templates per asset type: environment plates, pose ladder, hinged part sheet, props), `refs/` (character sheets), `recipes.yaml` (shot type → preset + layer roles), `presets/` (the 11 + hinged ones), `fx.json` (prep shadow/blur, grain, grade per mood), `captions.ass`, `cards/`, `qa.md`.
**Worked reuse (required before approval of the pack):** one recipe → exact commands: `v5_prep.py` (prep) → preset fill (role→file) → render → `ffmpeg` finish; then a **second shot made only by swapping images and text**, with zero Kimi calls, recorded in the manifest.

## 5. Builder v2.1 — one change only, and only on the owner's word
D-015 allows rigging only for an action that A+C cannot communicate; the owner accepted the blessing as a held pose (2026-10-25). Therefore hinged rotation is proposed as **an exception for gestures (blessing, bow, arm swing) only if the owner now wants visible limb motion**.
- Change: per-layer `rot` keyframes about a pivot (single hinge, no parenting in v2.1).
- Requirements: clean body plate with the arm removed; overlapping registered limb asset with a defined pivot; its shadow transform-matched or omitted; full rotation range and close-up seams inspected.
- Deferred (workarounds exist): opacity fades (cuts/overlays), live shadow/blur (prep plates), variable duration (trim in assembly), slide first-frame fix (use cuts), 9:16 output size (decide format first).
- Process unchanged: Kimi writes once (estimate ~$0.3), Codex reads every line, owner approves the fingerprint; ledger cap unchanged. The OPEN $0.328 reservation from Phase 1 must be reconciled first.

## 6. Format, workload and captions
- **Choose the primary format before any image generation** (16:9 YouTube or 9:16 Reels). A 9:16 crop of a 16:9 frame keeps only 31.6 % of the width, so "both" means composing for both. Each language release stays one size (D-012 R4).
- **Image workload per location is inventoried and capped:** reusable location kit (L1–L3, L8) made once per place; per scene only new characters/props/poses. Track attempts and minutes per accepted image; cap at, e.g., 3 attempts per asset before simplifying the shot.
- **Captions:** Noto Sans Devanagari (OFL) — file and hash pinned in the manifest, rendered via libass with `fontsdir`; verified with real conjuncts, matras and highlighted words; phone-size safe margins checked.

## 7. Proof before scaling: 15-second clip (owner's yes required)
Timed plan: 3 shots × 5 s from one location kit (establishing, Maharaj + devotee, close-up), approved narration line (Hindi), particles, prep shadows and blur, grade, grain, border, captions. If the owner wants hinged motion: one blessing arm via v2.1.
Gate (owner checks at normal speed, next to the pramana reference): looks full; gesture readable; identity consistent; no seams; captions correct and in time; reproducible from the manifest. Record fingerprints, render time, image attempts/minutes, Kimi spend (expected $0 without v2.1).

## 8. Decisions needed from the owner
1. Style direction: (a) paper-cutout relief like pramana, (b) flat folk poster with border, (c) current flat illustration plus depth/finish. Shadows/grain/blur amend D-016 ("flat colours") — explicit amendment.
2. Primary format: 16:9 or 9:16 (or both, composed for both).
3. Captions: Hindi, Marathi or both; always or key lines only.
4. Hinged limb motion now (Builder v2.1, exception to D-015) or keep held poses.
5. Shot lists: by hand from the style pack, or Kimi per chapter.
