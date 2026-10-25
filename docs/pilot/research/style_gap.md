# GranthStudio style gap analysis (read-only, 2026-10-25)

Basis: I read the schema (`v5_schema2.py`), preset README + preset 01, V5_PHASE1_TEST_RESULTS.md, D-015/016/017, the three contact sheets, `hand_compare.jpg`, `before_after.jpg`, frames SB f_0090 / SA f_0072 / SC f_0060, source images C1_p1_wide, C1_p3_bless, A1_full, and the 7 reference screenshots. I did NOT read the Blender builder source, so every statement about "what the builder can do" is inferred from the frozen schema and the test-results doc; items marked (verify) need a check against the builder before anyone commits to them. Nothing was run or edited.

Short verdict: our best shot (SA temple) already has 4 planes (sky, temple, pillars, leaves) and is the closest to the references. SB and SC look empty because they are one character plate on a flat gradient (SB) or on a washed-out white-sky plate (SC), with no foreground, no shadow, no ambient motion and one slow push per 6 s. Most of the gap is composition and finishing, not renderer capability, and can be closed without touching the frozen builder.

---

## 1. Honest gap list

Severity: H = visible in every frame and decides "pro vs amateur"; M = noticeable; L = polish.

| # | Gap | What we see (evidence) | What the references do | Sev |
|---|---|---|---|---|
| 1 | Empty backgrounds | SB: a cream gradient plus one brown floor band, nothing else; two small figures float in it (SB contact f1-f72). SC f120/f144: top 40 % is blank white sky. | Every frame has 5-10 identifiable planes: sun disc with concentric rings, far dunes, cloud ledges, platform, trees, huts, light shafts, stars. No more than ~15 % of the frame is empty, and the empty part is deliberate (caption space). | H |
| 2 | Low layer density per shot | Layer cap is 8 but we use 1-4. In SB/SC the "scene" is effectively 2 planes (backdrop + one flat plate that contains character AND ground). Camera "parallax" on a plate with one depth is just a zoom. | Paper-cutout reels: sky / sun / far hills / cloud ledge / mid ledge / character / near ledge = 7+ planes, each drifting at its own speed. | H |
| 3 | No foreground elements | SA has pillars and leaves (works well). SB, SC have none; the viewer looks straight at the subject with nothing between lens and subject. | Foreground framing in every reel: giant leaf cluster, tree trunk, blurred reeds, ledge in front, border. It frames the subject and sells depth. | H |
| 4 | Weak depth cues | No atmospheric perspective (far hills same saturation as near), no scale cues, no overlap, no blur, no light falloff. Camera push scales everything almost uniformly. | Far layers hazier/lighter, near layers blurred (painterly reel: out-of-focus reeds), big overlaps (cloud ledge cutting the legs). | H |
| 5 | No shadows, characters float | Neither SB (devotee, Maharaj) nor SC (boy, pot) has a contact shadow or cast shadow; SB floor is a flat brown band with a hard top edge. Hands/pot in SC cast nothing on the ground. | Paper-cutout: a soft drop shadow under every cutout (this is 80 % of the "tactile" look). Cartoon reel: oval ground shadows/mats under each figure. Folk/Madhubani: not needed (flat style), they use borders instead. | H |
| 6 | Surface texture | Flat vector fills; only the faint Flow noise. Looks like clip-art/vector animation. | Paper fibre, embossed edges, grain over the whole frame; painterly reel has soft brush grain and bloom. | M-H |
| 7 | Lighting is a single soft blob | SB has one radial halo behind the head. No rim light, no light rays, no colour grade per scene; the SA/SB/SC shots read as three different films (saturated sunset blue/orange, cream, washed beige-white). | Strict 4-6 colour palette per reel with one accent; sun disc with rings; rim glow on the figure (painterly); light shafts through trees (cartoon); vignette dark corners; consistent grade. | M-H |
| 8 | Almost no secondary motion | Leaf sway change 0.75 to 1.4 deg was "no measurable change" (results doc); dust "barely visible by design"; breathing amplitude 0.003. In practice every shot is one slow push on an otherwise frozen picture. | Constant ambient motion on 4-5 things at once: drifting clouds, twinkling stars/fireflies (Madhubani), floating petals/leaves (folk), water ripples + lily (painterly), light shafts (cartoon), sun glow pulsing. Something is always moving, at different speeds. | H |
| 9 | Character performance / construction | Each character is one flat pose image. Blessing raise cannot be warped (documented). Pose changes happen via slide/pan_bridge that produces a blank or blurred first frame (SC f49, SB f73). Maharaj looks younger in some images. | Paper-puppet characters are built from separate head/torso/arm/forearm pieces with visible joints; arms rotate at the shoulder. They are crude but move. The folk reel's Shiva sways, hair flows. Cartoon reel has simple stiff poses but bright eyes and strong silhouettes. | H |
| 10 | No captions or title cards | None. | Word-by-word highlighted captions in every reel (bold, outlined, centre-low, highlight colour from palette); title cards ("KACHA", "42 YEARS OF SERVICE") with serif type and a spaced subtitle; Hindi captions in the cartoon reel. | H (retention, accessibility) |
| 11 | Aspect ratio 16:9 vs 9:16 | Our frames are 1280x720. Subject often sits small in a wide frame. | All refs are 9:16: one big subject fills ~50 % of the height, top third is sky/title, bottom third is caption. NOTE: their density is partly a consequence of the narrow frame (few big shapes); in 16:9 you must fill the extra width with real environment (planes 1-3 above) or it will always feel empty. | M-H, depends on delivery (see section 4, item 5) |
| 12 | Shot length and pace | Fixed 144 frames (6.0 s at 24 fps; `frames` is a schema const) and usually one segment, one slow move per shot. | New visual information every 1.5-3 s (cut, new caption phrase, pop, camera change). | M-H |
| 13 | Transition artefacts | slide/pan_bridge first frame blank or blurred (SC f49 std 24.6 vs 62.5; SB f73). Visible as a flash. | Clean cuts, quick dissolves or wipes. | M (known defect, bug-class) |
| 14 | No framing devices | No borders. | Madhubani and folk reels use ornamental borders (triangle strip, dotted frame): cheap, brand-defining, and they hide the edges of camera moves. | M |
| 15 | Image-level inconsistency | C1 plates are on white with a thin ground line; the line is removed/replaced by a band; character scale differs between plates (devotee vs Maharaj in SB f1 vs f72). | Each reel uses one rigid scale and palette. | M |
| 16 | Resolution headroom | Output 1280x720 (verify whether configurable). Source plates are ~2000 px wide, so zoom 1.3-1.6 is safe; zoom to 3 on a 2000 px plate is soft. | n/a | L-M |
| 17 | Strength to keep | Heavy consistent navy outline and flat fills (D-016 approved) give a clean "Amar Chitra Katha" feel; SA's temple + pillars + leaves frame is already close to the reference level. | | + |

Reality check on cost: the references are 30-90 s reels reusing one set. We need 10-20 min x 21 films. Density has to come from a reusable per-location "environment kit" and from cutting several coverages out of one plate, not from fresh art per shot.

---

## 2. What closes with NO builder change vs what needs one

The builder is frozen (D-017: needs a demonstrated missing capability and the owner's yes). Schema reading: per layer we have depth, x, y, scale, opacity, blend add/normal, move (dx, dy, dscale), idle (breathing), sway (rotation about top edge, max 6 deg), soft_warp; per segment 1-8 layers, camera start/end with ease; backdrop gradient/floor/halo; atmosphere gloss, warm_tint, dust, vignette; transitions cut/slide/pan_bridge; up to 8 segments per shot.

### 2a. Closable with no code change

**A. Better images (owner asks Google Flow; this is the biggest lever)**
- Environment kit per location (5 plates, same palette, same horizon height, each on pure white or chroma so the existing clean/matting step works):
  1. sky + sun/moon disc with concentric rings (own plate, no ground).
  2. far layer: hills/dunes/skyline, lighter and less saturated.
  3. mid layer: the main structure (temple, hut, ghat) with ground.
  4. near layer: ground strip / ledge that will overlap the figures' feet.
  5. foreground frame: big leaves, tree trunk, pillars, reeds, left and right, mostly empty in the centre (A1_fg_frame is already this).
  Ask for plates 1-2 as 20-30 % wider than 16:9 so the camera has pan room.
- Character poses as a ladder, same canvas position and scale: neutral, mid-raise, full-raise (blessing); bow start / bow mid / bow end; listen; speak; close-up. This replaces the missing "rotate arm" capability with pose-to-pose cuts, exactly the A+C method in D-015. Use quick `cut` segments (8-16 frames each), never slow dissolves between full-body poses (preset rule).
- Prop/FX sheets: marigold petals, diyas, leaves, birds, smoke, sparkles, 12 items per sheet on white, to be cut into particle layers.
- Prompt hygiene (goes into the style pack): palette hex codes in the prompt, "flat colour, uniform dark navy outline weight, no gradients, no text, no watermark, pure white background" and always attach the approved reference frames.
- Compose empty space on purpose (rule of thirds, subject off-centre, caption band at bottom 20 %), not accidental.

**B. Better JSON presets / shot recipes (existing schema)**
- Use all planes: sky@10, far@8, mid@4.5, shadow@4.4, character@3, near@1.2, fg_left/right@0.4, light/particle layers@2 and @0.8. Raise from 1-4 to 6-8 layers.
- Faux atmospheric perspective: lower opacity on far layers (0.8-0.9 lets the backdrop gradient bleed through).
- Contact and drop shadows as separate pre-made PNG layers (soft dark ellipse or a blurred copy of the cutout), normal blend with opacity 0.25-0.4, placed at an intermediate depth with a small x/y offset. See asset prep below.
- Light: additive (`blend: add`) PNGs for light shafts, sun rings, glow; stack 2 on different depths.
- Ambient motion by drifting layers: clouds with dx 0.03-0.06 over the shot, particle layers at two depths with different dx/dy, halo pulse, idle breathing raised to ~0.006-0.01 (results doc says 0.003 is invisible).
- Coverage from one plate: split a 6 s shot into 2-3 segments of 48-72 frames (schema allows 8), each with its own camera (wide, medium, tight on the same plate) joined with `cut`. Gives a new picture every 2-3 s at zero art cost. Mind MIN_SEGMENT_MOTION (0.04) and MIN_SHOT_ZOOM (0.12).
- Pose-to-pose "animation": segments of 6-12 frames each holding a pose image, `on_twos: true`, `cut` between, for blessing, bow, walk-in.
- Use `cut`, not slide/pan_bridge, where the blank first frame is unacceptable (already recommended in the results doc); do real transitions in ffmpeg (below).

**C. ffmpeg assembly (no builder, no Kimi)**
- Captions: ASS/SRT burned with libass. Word-by-word highlight with karaoke tags (needs word timings from the TTS/forced aligner, not from an LLM). Fonts: an OFL Devanagari font (Hindi and Marathi share script; check Marathi conjuncts/shaping render correctly). Style: bold, outline + soft shadow, highlight colour from palette, max 2 lines, safe margins.
- Title cards: pre-rendered PNG or drawtext with fade in/out, serif title + spaced-caps subtitle.
- Film grain / paper texture: `noise` filter, or a tiled paper PNG blended (overlay/multiply/soft-light) over the whole frame; subtle (strength 6-10 of 255).
- One shared colour grade: a single `.cube` LUT or `curves`/`eq`/`colorbalance` chain applied to every shot. This alone fixes "three different films".
- Bloom/glow: split, gblur, blend screen at low opacity.
- Whole-frame handheld drift (crop with sin(t) expressions) and light flicker (`eq` brightness with an expression).
- Borders: PNG with alpha overlay (Madhubani triangle strip, dotted frame, per-saint motif).
- Particle loops: a few pre-rendered seamless loops (fireflies, petals, embers) as black-background videos composited with blend screen: gives twinkle and independent motion without a builder particle system.
- Transitions: `xfade` (fade, wipeleft, slideleft, circleopen ...) between shots, trimmed shot lengths (`-t`, `trim`) to vary from 6 s down to 2-3 s, speed changes.
- Vertical teaser from 16:9: `crop`/`scale`/`pad` with a per-shot x offset, with the caveat below.

**D. Asset prep outside the builder (small script, not part of the frozen file)**
- Bake shadow PNGs (alpha extract, offset, gaussian blur, darken), contact-shadow ellipses sized from the character bbox, blurred copies of the foreground plate for fake DOF (static blur is fine because the foreground blur does not change), light-ray and ring-halo generators, haze-tinted copies of far layers. ImageMagick or ffmpeg can do all of this. If Pillow/numpy is used, check CLAUDE.md first: the allowed dependency list is pyyaml, jsonschema, pytest, and motion.py/parallax.py probably already import more (verify) so a new dependency would need the owner's approval.

### 2b. Needs a builder change (each needs the owner's yes under D-017; evidence noted)

| # | New capability | Why no-code cannot do it | Evidence | Effort / priority |
|---|---|---|---|---|
| B1 | Keyframed layer rotation with pivot (`rot`: pivot_u, pivot_v, from_deg, to_deg, start, end, ease, range up to +/-90) | `sway` is a sinusoid about the top edge limited to 6 deg; `soft_warp` is bounded and proved ineffective. An arm raise, head nod, bow or limb swing needs a real, eased, large rotation of a separate limb layer. | SB blessing audit (hand_compare.jpg, results doc "missing character-performance capability") | Small in Blender (rotation keyframes about a pivot); HIGH, the only item that unlocks real performance together with a limb-split asset |
| B2 | Keyframed layer opacity (`fade`: from, to, start, end; optional `twinkle` with period and seed) | `opacity` is static, so no fade in/out of a layer, no glow pulse on a single object, no pop-in. | Reference twinkling stars/fireflies; light-up diya | Small; MEDIUM |
| B3 | Output size and aspect parameters (`out_w`, `out_h`; 1920x1080 and 1080x1920; make `floor_y` and coordinates aspect-relative; schema currently hard-codes +/-0.5625 for 16:9) | A 16:9 render cannot be turned into a good 9:16 by cropping: central 31.6 % width = 607x1080 px at best, and at 1280x720 only 405 px wide. Also (verify) 1280x720 may be hard-coded. | Section 1 gap 11, 16 | Small to medium; HIGH only if vertical or 1080p is a delivery target |
| B4 | Variable `frames` (24-240) | `frames` is a const 144; ffmpeg trimming covers shorter shots, but a longer move or a 3 s shot should not need a 6 s render. | Gap 12 | Small; LOW-MEDIUM (ffmpeg trims are a workable substitute) |
| B5 | Fix blank/blurred first frame of slide/pan_bridge | Defect in the builder, not JSON. Workaround: `cut` + ffmpeg xfade. | SC f49, SB f73 | Small bug fix; MEDIUM (becomes LOW if all transitions go to ffmpeg) |
| B6 | Native live drop shadow (shadow follows breathing/rotation, derived from layer alpha) | Baked shadow PNGs (2a-D) cover static shadows well; only needed once B1 rotates limbs, otherwise the baked shadow of an arm will not follow the arm. | Gap 5 | Medium; LOW now, MEDIUM after B1 |
| B7 | Particle emitter (`emitter`: asset, count, area, drift, size, twinkle, seed, depth) | Baked loops (2a-C) cover most uses. Needed only if you want particles that react to camera depth. | Gap 8 | Medium; LOW |
| B8 | Per-layer blur/rack focus (animated) | Static blurred PNG copies cover the painterly look; animated rack focus is a luxury. | Gap 4 | Medium; LOW |
| B9 | Looping scroll/UV-wrap layer (endless clouds, water) | `move` drift over 6 s suffices for short shots. | Gap 8 | Small; LOW |

Do NOT put into the builder: captions, grain, grading, borders, transitions, title cards. They belong in ffmpeg where they are cheaper, replaceable per style, and do not touch the frozen hash.

---

## 3. "Style pack" concept: approve a look once, reuse with zero Kimi calls

Idea: a versioned, hash-pinned folder that contains everything that defines the look. An episode only says "use style pack X v1.0". All creative decisions about LOOK are made once (owner approval, like D-016); only story content (what is shown in each shot) varies.

```
style_packs/devotional_flat_v1/
  style.yaml            id, version, status (draft|APPROVED + owner date), fps, out size/aspect,
                        builder sha256 it was proven against, manifest sha256 of every file
  palette.json          named colours with roles: outline_navy, skin tones (child/man), cloth white,
                        accent saffron, 1 accent per scene; time-of-day gradient pairs
                        (dawn, noon, sunset, night, lamp-lit interior) + floor/halo colours
  prompts/              plain-text templates with {placeholders}; no LLM needed
    style_preamble.txt  constant block pasted into every Flow prompt (flat, outline weight, palette hex,
                        white bg, no text/watermark)
    plate_sky / plate_far / plate_mid / plate_near / plate_fg_frame.txt   ({location}, {time_of_day}, {landmarks})
    character_pose.txt, pose_ladder.txt   ({character_id}, {pose}); blessing/bow/listen/speak/walk
    prop_sheet.txt, fx_sheet.txt          petals, diyas, birds, smoke
    negative_and_checks.txt               what to reject on receipt (text, watermark, wrong outline, lit background)
  refs/                 owner-approved style anchor frames (3-5), per-character sheets
                        (turnaround, expressions, pose ladder), colour chips, do/don't board:
                        attach these to Flow every time for consistency
  layer_recipes.yaml    per shot type (establishing, entrance, bow, bless, dialogue, reaction,
                        close-up, insert, transition): the role list, depths, which roles get
                        shadow / haze / glow, particle set, coverage plan (wide-medium-close)
  presets/              the shot JSONs (today's 11 plus: 3-pose blessing, bow ladder,
                        2-3 segment coverage cuts), role names not file names, validated against schema v2
  fx/                   shadow_blob.png, light_rays.png, ring_halo.png, paper.png, grain settings,
                        particle loops (fireflies, petals, dust), border_*.png, lut.cube
  captions/             caption_hi.ass / caption_mr.ass templates (font file + licence, size, outline,
                        highlight colour from palette, max chars per line, safe zone), title_card
                        template, lower-third template
  post/post.json        ffmpeg chain per shot kind: grade, grain, vignette, bloom, border; transition
                        table by beat type (cut, fade 8f, wipe); shot-length rules; audio ducking
  prep/prep.yaml        asset prep recipe: matting rule, shadow params, haze/blur copies, naming rules
  qa/checklist.md       contact-sheet checks, min layers per shot type, palette-drift check, caption
                        overflow check, blank-first-frame check
  CHANGELOG.md
```

How a new episode uses it (no Kimi):
1. `episodes/<id>/episode.yaml` names the style pack and version; the manifest hash is recorded so later pack edits cannot silently change an old episode.
2. Script/narration is approved text (source approvals precede any shot per D-015). Shot list = one row per narration chunk with: shot type, location, characters, pose. This is a table the owner (or Kimi once, optionally, as source-based planning) fills; a deterministic mapping from shot type to preset/recipe needs no LLM.
3. A small generator fills `prompts/*.txt` placeholders and emits a numbered "image request list" for the owner to paste into Flow. Location kits and character pose ladders are generated once per location/character and reused across all episodes of that saint.
4. Owner drops images into the inbox; the existing clean/matting step runs; asset prep bakes shadows, haze, blur, rays per `prep.yaml`.
5. Preset roles are mapped to files (the one-find-and-replace flow already proven in preset reuse tests), validated with `v5_schema2.validate`, rendered with the frozen builder.
6. `post.json` runs: grade, grain, borders, xfade transitions, captions from the approved text plus TTS word timings, title cards. Output is the episode.
7. QA uses `qa/checklist.md` and contact sheets. Style changes only by releasing a new pack version with a new owner approval; episodes in flight stay pinned.

Approval gate: build the pack from one location + one character + one 20-30 s proof clip, have the owner sign it, then freeze (hash + date), parallel to how Builder v2 is frozen.

Honest limits: the pack removes LLM calls for look decisions and for asset requests; it cannot decide what each shot depicts for a new story. Quality still depends on Flow output matching refs; the QA checklist and attaching refs are the control, not a guarantee.

---

## 4. Prioritised plan: 5 highest-value changes

1. **Environment kit + density + coverage cuts (no code).** Rebuild SB and SC as proof: 5 plates per location (sky, far, mid, near, foreground frame), caption band reserved, 6-8 layers, and 2-3 coverage segments (wide/medium/tight) per shot. Address gaps 1-4, 12, 15. Cost: roughly 10-12 Flow images per location, JSON only. Test: re-run the same contact-sheet comparison next to the references.
2. **ffmpeg finishing pack (no builder change).** One shared LUT grade, subtle grain + paper texture, border overlay, Hindi/Marathi word-highlight captions, title cards, xfade transitions, shot trimming. Addresses gaps 6, 7, 10, 13, 14 and visually unifies the three shots. Cost: filter chains and ASS templates; font licence check.
3. **Shadows, light and ambient-motion assets (asset prep, no builder change).** Contact + drop shadows, light shafts, ring halos, haze-tinted far layers, blurred foreground copies, particle loops (twinkling via black-background overlay), drifting clouds via `move`. Gaps 4, 5, 7, 8. Cost: one prep recipe, a handful of generated PNGs/loops, reused in every episode.
4. **One reviewed Builder v2.1 change request (owner's yes + Codex review).** Smallest set with demonstrated need: keyframed `rot` with pivot (B1, the documented blessing/bow gap, paired with a limb-split or pose-ladder asset), `fade` opacity (B2), `out_w/out_h` incl. 9:16 and 1080p (B3, only if the delivery decision needs it), `frames` variable (B4), blank-first-frame fix (B5). Everything else (particles, live shadow, blur, scroll) deferred until a shot proves it needed.
5. **Wrap 1-3 into a style pack and decide the format, then run a one-minute proof.** Create `style_packs/devotional_flat_v1` (section 3), include the delivery-format decision before generating more plates: if the films are 16:9 YouTube, keep 16:9 as primary and make vertical teasers from dedicated 9:16 hero plates (do not crop 16:9, it leaves 31.6 % width); if the main release is vertical, compose all new plates 9:16 from now on. Owner signs the pack on the proof clip (a look decision that extends D-016: shadows, grain, grade and borders keep the flat-outline look; a move to a true paper-cutout style would be a different look and needs its own approval).

Open questions for the owner: (a) primary delivery format and whether vertical teasers are wanted; (b) whether texture/shadows are acceptable additions to the D-016 flat look or must stay strictly flat; (c) willingness to let one builder change request (item 4) go to Codex; (d) captions: Hindi only, Marathi only, or both burned in per version.
