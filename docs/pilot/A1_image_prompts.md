# Adhyay 1 image prompts for Nano Banana (Google Flow): DRAFT, NOT APPROVED

Every item below is a draft for the owner. Nothing is approved. Prompts are self-contained English; paste the whole prompt and attach the listed reference images. Sources: `A1_story_for_approval.md`, `A1_rev1.json`, `A1_full_script_simple.md`, `A1_audio_plan.json`, the frozen research in `canon/packets/adhyay_01/frozen_copies` (FINAL answers win), the 11 V5 presets and D-016/D-017. Shot counts follow the current 61-shot plan (2, 9, 6, 5, 8, 5, 9, 6, 11) and are organised by scene beat, so they survive re-timing. Generated from one table, so this file and `canon/drafts/A1_image_catalog_DRAFT.json` always agree.

## (a) Style paragraph (repeated verbatim at the start of every prompt)

> Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person.

Negative line (repeated verbatim at the end of every prompt):

> Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).

Visual-identity paragraphs (repeated verbatim in every prompt for that subject):

- **Gajanan Maharaj** (`GM`): Shri Gajanan Maharaj: a young man in the prime of youth (looks about 25 to 30), strong and well built, muscular upper arms and neck, broad chest, radiant calm handsome face, eyes half-lowered with the gaze resting on the tip of his nose, short cropped dark hair, clean-shaven, warm medium-brown skin. He wears only one old, worn, torn sleeveless bandi (a short open-front vest) of faded grey-white cloth with frayed edges, and a minimal plain off-white loincloth; otherwise bare. Barefoot, no jewellery, no beads, no forehead mark. His only belongings: a dried bottle-gourd water vessel (natural tan, narrow neck) and a small hand-made unfired clay chilim (a straight conical clay pipe, matte raw grey-brown clay, never kiln-fired).
- **Bankatlal** (`BA`): Bankatlal Agarwal: an adult man of about 35, medium height, slightly full build, kind attentive face, small neat moustache, warm brown skin. He wears a cream-white turban wound in a round pagadi, a long sage-green cotton angarkha coat to below the knee, tied at the side, over a white dhoti, and a cream shoulder cloth (uparna) over his left shoulder. Barefoot. Nothing in his hands unless stated.
- **Damodarpant** (`DK`): Damodarpant Kulkarni: an adult man of about 35, lean and slightly taller than Bankatlal, narrow face, thin moustache, warm brown skin. He wears a terracotta-red Maharashtrian pagadi turban, a plain white long-sleeved cotton angarkha shirt to the knee, a white dhoti, and an off-white uparna over one shoulder. Barefoot.
- **Devidas** (`DV`): Devidas: a Brahmin householder of about 45, medium build, gentle devout face, clean-shaven, shaved head with a small tuft (shikha) at the crown, greying at the temples, a small red tilak on the forehead, a white sacred thread across the chest. Bare-chested, a white dhoti, and an off-white uparna across one shoulder. Barefoot.
- **Shegaon** (`SHEGAON`): Shegaon in the 1870s: a small village on the flat open plain of Varhad, dark-brown soil, a cluster of low houses with mud-plastered walls in ochre and earth tones, some roofs of terracotta clay tiles and some thatched, a few neem and babul trees, dusty lanes, no temple spire, no large buildings, no people in view.
- **Road before Devidas's house** (`ROAD`): The road in front of Devidas's house in Shegaon: a dusty unpaved village road running across the picture; on the left a modest but solid village house with thick mud-plastered ochre walls, a terracotta clay-tile roof, a raised earthen plinth step (ota) and a heavy plain wooden door standing half open onto a dark interior; neighbouring low houses and neem trees further down the road. On the road in front of the door lie several used leaf plates (round plates of stitched dry leaves) with a few scattered grains of leftover white rice.
- **Well and cattle trough** (`WELL`): A village well a short way along the same road: a round open well with a low parapet of rough grey-brown stone, and beside it a long rectangular stone water trough (haal) for cattle, its water muddy brown and shallow; dusty trampled ground around it, a neem tree giving a little shade; two or three plain humped Deccan cattle drinking at the far end of the trough.

Layer rules: Nano Banana does not output transparency. Every image marked **cut-out** is made on plain white and goes through the existing background-removal prep step (as `v5_inbox/prepped`). Layer images (sky, far, mid, fg) leave everything outside the layer white for the same step; `FX_SUN` is on black for additive blending. Generate at 16:9 (1280x720 or larger). No text, captions or Marathi letters in any image: the 1878 caption and all captions are added later.

## (b) Generation order

Make them in this order, so each image can be attached as a reference to the later ones:

**character_ref** (4): 1. `CH_GM`, 2. `CH_BA`, 3. `CH_DK`, 4. `CH_DV`

**prop** (3): 5. `PR_GOURD_CHILIM`, 6. `PR_GADVA_VETIVER`, 7. `PR_LEAF_PLATES`

**location** (11): 8. `LOC_SHEGAON_REF`, 9. `LOC_ROAD_REF`, 10. `LOC_WELL_REF`, 11. `SKY_MORNING`, 12. `SKY_NOON`, 13. `FX_SUN`, 14. `FG_NEEM`, 15. `FAR_VILLAGE`, 16. `MID_SHEGAON`, 17. `MID_ROAD_HOUSE`, 18. `MID_WELL_TROUGH`

**pose** (24): 19. `P_GM_SEATED_CALM`, 20. `P_GM_PICKING`, 21. `P_GM_LOOK_UP`, 22. `P_GM_EATING`, 23. `P_GM_SPEAKING`, 24. `P_GM_RUN`, 25. `F_GM_CALM`, 26. `F_GM_LOOK_UP`, 27. `F_GM_LAUGH`, 28. `PAIR_BA_DK_WALK`, 29. `PAIR_BA_DK_STAND`, 30. `P_BA_TALK`, 31. `P_DK_LISTEN`, 32. `P_BA_ASK`, 33. `P_DK_OFFER`, 34. `P_DK_WALK_TO_HOUSE`, 35. `P_DK_WALK_GADVA`, 36. `P_DK_HOLD_GADVA`, 37. `P_DV_CARRY_PLATE`, 38. `F_BA_AMAZED`, 39. `F_BA_REVERENT`, 40. `F_DK_ALARM`, 41. `POSE_SILENT_BOW`, 42. `POSE_READY_TO_FALL`

**beat_still** (12): 43. `INS_FEAST_PREP`, 44. `INS_LEAF_PLATES`, 45. `INS_CHILIM_GOURD`, 46. `INS_PICK_GRAIN`, 47. `INS_PLATE_SET`, 48. `INS_MIXING`, 49. `INS_EMPTY_GOURD`, 50. `INS_TROUGH_WATER`, 51. `INS_GADVA_VETIVER`, 52. `BEAT_S3_TWO_MEN_SEE`, 53. `BEAT_S7_BIRDS`, 54. `BEAT_S8_GM_DRINKS`

Within `location`: the three place references first, then the layers derived from them. Within `pose`: Maharaj's seated pose first (it becomes the reference for his other poses), then faces, then the other men, then the group poses.

## (c) The images

### character_ref

#### `CH_GM`

- kind: character_ref | scenes: S1-S9 | covers about **0** shot(s) in the current plan
- preset roles: reference only (not placed in a shot)
- attach as reference: optional style look: D:/aai work/v5_inbox/clean/M1_young_ref.png (face/build only; add the bandi)
- aspect / layer: full frame / layer; Not a shot image: the master identity reference for every Maharaj image.
- source refs: A1:74 prime of youth; A1:88 old bandi; A1:89 gourd; A1:90 unfired self-made chilim; A1:91 nose-tip gaze, calm; A1:92 digambar; A1:111 radiant, arms, neck, chest; analysis_v3 l.125 owner: almost naked, minimal loincloth
- OWNER_CHOICE: OC-01 age look 25-30, OC-02 hair/beard/skin, OC-03 bandi colour and shown throughout
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Shri Gajanan Maharaj: a young man in the prime of youth (looks about 25 to 30), strong and well built, muscular upper arms and neck, broad chest, radiant calm handsome face, eyes half-lowered with the gaze resting on the tip of his nose, short cropped dark hair, clean-shaven, warm medium-brown skin. He wears only one old, worn, torn sleeveless bandi (a short open-front vest) of faded grey-white cloth with frayed edges, and a minimal plain off-white loincloth; otherwise bare. Barefoot, no jewellery, no beads, no forehead mark. His only belongings: a dried bottle-gourd water vessel (natural tan, narrow neck) and a small hand-made unfired clay chilim (a straight conical clay pipe, matte raw grey-brown clay, never kiln-fired). Character reference sheet: the same man shown three times side by side at the same scale, front view standing, three-quarter view seated cross-legged on the ground, and side view seated, with the gourd and the unfired clay chilim drawn once beside him. 16:9 landscape, plain white background. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `CH_BA`

- kind: character_ref | scenes: S3-S9 | covers about **0** shot(s) in the current plan
- preset roles: reference only (not placed in a shot)
- attach as reference: optional: D:/aai work/granthstudio/assets/pilot_refs/set_v1/bankatlal.jpg (costume colours only; drop the money pouch)
- aspect / layer: full frame / layer; Master identity reference.
- source refs: A1:97 Bankatlal Agarwal; characters_1to12_FINAL row 2: physical details none stated
- OWNER_CHOICE: OC-04 Bankatlal costume and age
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Bankatlal Agarwal: an adult man of about 35, medium height, slightly full build, kind attentive face, small neat moustache, warm brown skin. He wears a cream-white turban wound in a round pagadi, a long sage-green cotton angarkha coat to below the knee, tied at the side, over a white dhoti, and a cream shoulder cloth (uparna) over his left shoulder. Barefoot. Nothing in his hands unless stated. Character reference sheet: the same man shown front view, three-quarter view and side view, standing, at the same scale. 16:9 landscape, plain white background. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `CH_DK`

- kind: character_ref | scenes: S3-S9 | covers about **0** shot(s) in the current plan
- preset roles: reference only (not placed in a shot)
- attach as reference: optional: D:/aai work/granthstudio/assets/pilot_refs/set_v1/damodarpant.jpg (build only; replace the white cap with the red pagadi)
- aspect / layer: full frame / layer; Master identity reference.
- source refs: A1:97-98 Damodarpant Kulkarni; characters_1to12_FINAL row 4: none stated
- OWNER_CHOICE: OC-05 Damodarpant costume; must not look like Devidas
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Damodarpant Kulkarni: an adult man of about 35, lean and slightly taller than Bankatlal, narrow face, thin moustache, warm brown skin. He wears a terracotta-red Maharashtrian pagadi turban, a plain white long-sleeved cotton angarkha shirt to the knee, a white dhoti, and an off-white uparna over one shoulder. Barefoot. Character reference sheet: the same man shown front view, three-quarter view and side view, standing, at the same scale. 16:9 landscape, plain white background. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `CH_DV`

- kind: character_ref | scenes: S2, S5 | covers about **0** shot(s) in the current plan
- preset roles: reference only (not placed in a shot)
- attach as reference: optional: D:/aai work/granthstudio/assets/pilot_refs/set_v1/devidas.jpg
- aspect / layer: full frame / layer; Master identity reference.
- source refs: A1:84-85 devout Brahmin householder, head of a math; FINAL S5-3 son aged 13-16 (father's age inferred); characters_1to12_FINAL row 3: none stated
- OWNER_CHOICE: OC-06 Devidas look and age
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Devidas: a Brahmin householder of about 45, medium build, gentle devout face, clean-shaven, shaved head with a small tuft (shikha) at the crown, greying at the temples, a small red tilak on the forehead, a white sacred thread across the chest. Bare-chested, a white dhoti, and an off-white uparna across one shoulder. Barefoot. Character reference sheet: the same man shown front view, three-quarter view and side view, standing, at the same scale. 16:9 landscape, plain white background. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

### prop

#### `PR_GOURD_CHILIM`

- kind: prop | scenes: S1-S9 | covers about **0** shot(s) in the current plan
- preset roles: reference only (not placed in a shot)
- attach as reference: CH_GM
- aspect / layer: full frame / layer; Feeds every Maharaj image and the gourd/chilim inserts.
- source refs: A1:89 gourd (bhopla); A1:125-126 the same gourd (tumba); A1:90 unfired chilim
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Prop reference sheet on white: (1) a dried bottle-gourd water vessel, natural tan with darker speckles, narrow neck, shown upright and lying on its side empty; (2) a small straight conical smoking pipe (chilim) hand-shaped from raw unfired clay, matte grey-brown, uneven finger marks, never kiln-fired. 16:9, plain white background. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `PR_GADVA_VETIVER`

- kind: prop | scenes: S7-S9 | covers about **0** shot(s) in the current plan
- preset roles: reference only (not placed in a shot)
- attach as reference: none (first image of its kind)
- aspect / layer: full frame / layer
- source refs: A1:135 gadva; analysis_v3 l.125 owner production decision: brass; A1:137 sweet, clear, cool, vetiver-scented water; glossary: vala = vetiver
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Prop reference sheet on white: (1) a round-bellied brass water pot (gadva) with a short flared neck, polished warm yellow brass, shown alone; (2) the same gadva full of clear cool water with a small bundle of pale golden vetiver (khus) roots floating in it, seen from slightly above. 16:9, plain white background. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `PR_LEAF_PLATES`

- kind: prop | scenes: S2-S5 | covers about **0** shot(s) in the current plan
- preset roles: reference only (not placed in a shot)
- attach as reference: none (first image of its kind)
- aspect / layer: full frame / layer
- source refs: A1:87 used leaf plates on the road; A1:94 rice grains; A1:114 plate full of pakvanna; A1_full_script_simple S5-L2 patraval
- OWNER_CHOICE: OC-07 Devidas's plate: leaf (default) or metal; which dishes
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Prop reference sheet on white: (1) three used leaf plates (round plates of dry leaves stitched with twigs), crumpled at the edges, with a few scattered grains of leftover white rice; (2) one fresh leaf plate fully served with several rich cooked dishes in small heaps: white rice, yellow dal, a vegetable, fried puris and two round sweets. 16:9, plain white background. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

### location

#### `LOC_SHEGAON_REF`

- kind: location | scenes: S1, S6 | covers about **0** shot(s) in the current plan
- preset roles: reference only (not placed in a shot)
- attach as reference: none (first image of its kind)
- aspect / layer: full frame / layer; Master place reference; the layers below are derived from it.
- source refs: A1:58-60 small village, famous, Khamgaon taluka (context ovi of S1); story S1 shot 1
- OWNER_CHOICE: OC-08 time of day / light of the opening
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Shegaon in the 1870s: a small village on the flat open plain of Varhad, dark-brown soil, a cluster of low houses with mud-plastered walls in ochre and earth tones, some roofs of terracotta clay tiles and some thatched, a few neem and babul trees, dusty lanes, no temple spire, no large buildings, no people in view. Wide establishing view of the village from its edge, soft clear late-morning light, pale blue sky. Full-frame 16:9 landscape picture, edge to edge, no border, no frame mount. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `LOC_ROAD_REF`

- kind: location | scenes: S2-S7 | covers about **0** shot(s) in the current plan
- preset roles: reference only (not placed in a shot)
- attach as reference: optional look: D:/aai work/granthstudio/assets/pilot_refs/set_v1/location.jpg, PR_LEAF_PLATES
- aspect / layer: full frame / layer; Master place reference.
- source refs: A1:87 leaf plates on the road before the house; A1:113-114 door and outside are separate spaces; FINAL A1-5 the house is Devidas's
- OWNER_CHOICE: OC-09 look of Devidas's house
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. The road in front of Devidas's house in Shegaon: a dusty unpaved village road running across the picture; on the left a modest but solid village house with thick mud-plastered ochre walls, a terracotta clay-tile roof, a raised earthen plinth step (ota) and a heavy plain wooden door standing half open onto a dark interior; neighbouring low houses and neem trees further down the road. On the road in front of the door lie several used leaf plates (round plates of stitched dry leaves) with a few scattered grains of leftover white rice. Wide view across the road, the house on the left third, the road and the leaf plates in the centre, empty space on the right third of the road where figures will be placed later; soft clear late-morning light. No people. Full-frame 16:9 landscape picture, edge to edge, no border, no frame mount. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `LOC_WELL_REF`

- kind: location | scenes: S8, S9 | covers about **0** shot(s) in the current plan
- preset roles: reference only (not placed in a shot)
- attach as reference: LOC_ROAD_REF (same village, same palette)
- aspect / layer: full frame / layer; Master place reference.
- source refs: A1:134 haal beside the well, all the animals drink; analysis_v3 G-1 haal = cattle watering trough
- OWNER_CHOICE: OC-10 well/trough design; kind and number of animals
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. A village well a short way along the same road: a round open well with a low parapet of rough grey-brown stone, and beside it a long rectangular stone water trough (haal) for cattle, its water muddy brown and shallow; dusty trampled ground around it, a neem tree giving a little shade; two or three plain humped Deccan cattle drinking at the far end of the trough. Wide view, the well on the left, the trough across the centre, the cattle at the right end, open space in front of the trough for figures; strong high noon sun, short shadows. No people. Full-frame 16:9 landscape picture, edge to edge, no border, no frame mount. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `SKY_MORNING`

- kind: location | scenes: S1-S6 | covers about **20** shot(s) in the current plan
- preset roles: 01:sky, 02:sky, 08/09/04/05:bg
- attach as reference: LOC_ROAD_REF
- aspect / layer: full frame / layer; Shared sky for every morning shot.
- source refs: STAGING light (story runs from before noon to noon: addendum D time continuity)
- OWNER_CHOICE: OC-08
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Background layer: only a clear pale-blue late-morning sky with a few soft flat cream clouds over a thin, very low line of flat distant plain at the bottom edge. Nothing else. 16:9 (generate wide; 1.3x scale is used), full frame. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `SKY_NOON`

- kind: location | scenes: S7-S9 | covers about **14** shot(s) in the current plan
- preset roles: 01:sky, 02:sky, bg
- attach as reference: SKY_MORNING (same horizon line and composition)
- aspect / layer: full frame / layer; Shared sky for every noon shot.
- source refs: A1:123 sun at midday, ground heated; A1:124 full sun
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Background layer: only a hard, bleached, almost white-blue high-noon sky, no clouds, faint heat haze over a very low flat plain line at the bottom edge. Nothing else. 16:9, full frame. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `FX_SUN`

- kind: location | scenes: S1, S6, S7 | covers about **3** shot(s) in the current plan
- preset roles: 01:fx
- attach as reference: none (first image of its kind)
- aspect / layer: full frame / layer; Natural sunlight, not a halo; never placed over Maharaj alone.
- source refs: STAGING light only
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Light layer: three or four broad, soft, warm cream-yellow diagonal sunlight shafts coming from the upper right on a pure black background; no objects, no smoke, no people. 16:9, black background (used with additive blend at low opacity). Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `FG_NEEM`

- kind: location | scenes: S1-S9 | covers about **8** shot(s) in the current plan
- preset roles: 01:fg, 02:near
- attach as reference: LOC_SHEGAON_REF
- aspect / layer: full frame / layer; Shared foreground frame; sways in presets 01/02.
- source refs: STAGING scenery (birds in trees: A1:123)
- OWNER_CHOICE: OC-11 neem as the village tree
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Foreground frame layer: a few hanging neem branches with small serrated leaves entering from the top-left and top-right corners, dark sage-green, drawn large and close to camera. Everything that is not part of this layer is plain pure white (to be removed into transparency). 16:9. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `FAR_VILLAGE`

- kind: location | scenes: S1-S9 | covers about **31** shot(s) in the current plan
- preset roles: 02:far, bg
- attach as reference: LOC_SHEGAON_REF
- aspect / layer: full frame / layer
- source refs: A1:58-60 context
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Shegaon in the 1870s: a small village on the flat open plain of Varhad, dark-brown soil, a cluster of low houses with mud-plastered walls in ochre and earth tones, some roofs of terracotta clay tiles and some thatched, a few neem and babul trees, dusty lanes, no temple spire, no large buildings, no people in view. Far layer: only a distant row of low village houses and rounded neem and babul tree crowns along the horizon band, lower half of the picture. Sky area and the ground in front are plain white. Everything that is not part of this layer is plain pure white (to be removed into transparency). 16:9. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `MID_SHEGAON`

- kind: location | scenes: S1, S6 | covers about **2** shot(s) in the current plan
- preset roles: 01:mid
- attach as reference: LOC_SHEGAON_REF
- aspect / layer: full frame / layer
- source refs: A1:58-60
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Shegaon in the 1870s: a small village on the flat open plain of Varhad, dark-brown soil, a cluster of low houses with mud-plastered walls in ochre and earth tones, some roofs of terracotta clay tiles and some thatched, a few neem and babul trees, dusty lanes, no temple spire, no large buildings, no people in view. Mid layer: the village cluster of houses and lanes from the reference, ground included, sky area plain white. Everything that is not part of this layer is plain pure white (to be removed into transparency). 16:9. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `MID_ROAD_HOUSE`

- kind: location | scenes: S1-S7 | covers about **23** shot(s) in the current plan
- preset roles: 01:mid, 02:mid, bg (all character shots on the road)
- attach as reference: LOC_ROAD_REF, PR_LEAF_PLATES
- aspect / layer: full frame / layer; Main stage of S2-S7; composite SKY + FAR + MID (+ FG) = the road background for every cut-out shot.
- source refs: A1:87; A1:113-114; FINAL A1-5
- OWNER_CHOICE: OC-09
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. The road in front of Devidas's house in Shegaon: a dusty unpaved village road running across the picture; on the left a modest but solid village house with thick mud-plastered ochre walls, a terracotta clay-tile roof, a raised earthen plinth step (ota) and a heavy plain wooden door standing half open onto a dark interior; neighbouring low houses and neem trees further down the road. On the road in front of the door lie several used leaf plates (round plates of stitched dry leaves) with a few scattered grains of leftover white rice. Mid layer: Devidas's house, the road and the used leaf plates exactly as in the reference, ground included to the bottom edge; sky area and distant houses plain white. Keep the right third of the road empty for figures. Everything that is not part of this layer is plain pure white (to be removed into transparency). 16:9. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `MID_WELL_TROUGH`

- kind: location | scenes: S8, S9 | covers about **8** shot(s) in the current plan
- preset roles: 02:mid, bg (character shots at the well)
- attach as reference: LOC_WELL_REF
- aspect / layer: full frame / layer
- source refs: A1:134
- OWNER_CHOICE: OC-10
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. A village well a short way along the same road: a round open well with a low parapet of rough grey-brown stone, and beside it a long rectangular stone water trough (haal) for cattle, its water muddy brown and shallow; dusty trampled ground around it, a neem tree giving a little shade; two or three plain humped Deccan cattle drinking at the far end of the trough. Mid layer: the well, the trough, the cattle and the trampled ground exactly as in the reference, ground to the bottom edge; sky plain white. Keep open ground in front of the trough for figures. Everything that is not part of this layer is plain pure white (to be removed into transparency). 16:9. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

### pose

#### `P_GM_SEATED_CALM`

- kind: pose | scenes: S2, S5, S7, S8 | covers about **6** shot(s) in the current plan
- preset roles: 02:extra char layer, 04:other, 09:right
- attach as reference: CH_GM, PR_GOURD_CHILIM
- aspect / layer: cut-out (white background to remove); The most reused image: the same cut-out goes over the road (morning or noon sky) and the well by changing only the background layers.
- source refs: A1:88 seated there; A1:89-91; A1:124 sits in full sun, joyful, fearless
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Shri Gajanan Maharaj: a young man in the prime of youth (looks about 25 to 30), strong and well built, muscular upper arms and neck, broad chest, radiant calm handsome face, eyes half-lowered with the gaze resting on the tip of his nose, short cropped dark hair, clean-shaven, warm medium-brown skin. He wears only one old, worn, torn sleeveless bandi (a short open-front vest) of faded grey-white cloth with frayed edges, and a minimal plain off-white loincloth; otherwise bare. Barefoot, no jewellery, no beads, no forehead mark. His only belongings: a dried bottle-gourd water vessel (natural tan, narrow neck) and a small hand-made unfired clay chilim (a straight conical clay pipe, matte raw grey-brown clay, never kiln-fired). Pose: seated cross-legged on the ground in three-quarter view facing screen-left, back straight, calm face, gaze on the tip of his nose, the unfired clay chilim held loosely in his right hand resting on his knee, the gourd standing on the ground by his left knee. Show the subject in full, isolated on a plain pure white background, with no ground, no scenery, no cast shadow, and a clear white margin all round, so the background can be removed into a transparent cut-out. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `P_GM_PICKING`

- kind: pose | scenes: S2, S3, S4 | covers about **4** shot(s) in the current plan
- preset roles: 02:extra char layer, 04:other
- attach as reference: CH_GM, PR_LEAF_PLATES, PR_GOURD_CHILIM
- aspect / layer: cut-out (white background to remove)
- source refs: A1:93 searches the plates seated on the road; A1:94 picks each grain he sees
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Shri Gajanan Maharaj: a young man in the prime of youth (looks about 25 to 30), strong and well built, muscular upper arms and neck, broad chest, radiant calm handsome face, eyes half-lowered with the gaze resting on the tip of his nose, short cropped dark hair, clean-shaven, warm medium-brown skin. He wears only one old, worn, torn sleeveless bandi (a short open-front vest) of faded grey-white cloth with frayed edges, and a minimal plain off-white loincloth; otherwise bare. Barefoot, no jewellery, no beads, no forehead mark. His only belongings: a dried bottle-gourd water vessel (natural tan, narrow neck) and a small hand-made unfired clay chilim (a straight conical clay pipe, matte raw grey-brown clay, never kiln-fired). Pose: seated on the ground in three-quarter view facing screen-left, leaning slightly forward over three used leaf plates on the ground in front of him, picking up a single grain of rice between the fingers of his right hand, face calm and absorbed; the chilim lies beside the gourd at his side. The leaf plates are part of this cut-out. Show the subject in full, isolated on a plain pure white background, with no ground, no scenery, no cast shadow, and a clear white margin all round, so the background can be removed into a transparent cut-out. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `P_GM_LOOK_UP`

- kind: pose | scenes: S4 | covers about **2** shot(s) in the current plan
- preset roles: 09:right, 02:extra char layer
- attach as reference: CH_GM, P_GM_PICKING
- aspect / layer: cut-out (white background to remove)
- source refs: A1:110 no answer, only looks up at both faces; A1:111
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Shri Gajanan Maharaj: a young man in the prime of youth (looks about 25 to 30), strong and well built, muscular upper arms and neck, broad chest, radiant calm handsome face, eyes half-lowered with the gaze resting on the tip of his nose, short cropped dark hair, clean-shaven, warm medium-brown skin. He wears only one old, worn, torn sleeveless bandi (a short open-front vest) of faded grey-white cloth with frayed edges, and a minimal plain off-white loincloth; otherwise bare. Barefoot, no jewellery, no beads, no forehead mark. His only belongings: a dried bottle-gourd water vessel (natural tan, narrow neck) and a small hand-made unfired clay chilim (a straight conical clay pipe, matte raw grey-brown clay, never kiln-fired). Pose: seated among the leaf plates facing screen-left, head raised, looking steadily up at the faces of two standing men (not drawn), silent, radiant, utterly calm, hands resting on his knees. Show the subject in full, isolated on a plain pure white background, with no ground, no scenery, no cast shadow, and a clear white margin all round, so the background can be removed into a transparent cut-out. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `P_GM_EATING`

- kind: pose | scenes: S5 | covers about **2** shot(s) in the current plan
- preset roles: 02:extra char layer
- attach as reference: CH_GM, PR_LEAF_PLATES
- aspect / layer: cut-out (white background to remove)
- source refs: A1:115 sits to eat, no craving for taste; A1:118 mixes all dishes into one
- OWNER_CHOICE: OC-07
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Shri Gajanan Maharaj: a young man in the prime of youth (looks about 25 to 30), strong and well built, muscular upper arms and neck, broad chest, radiant calm handsome face, eyes half-lowered with the gaze resting on the tip of his nose, short cropped dark hair, clean-shaven, warm medium-brown skin. He wears only one old, worn, torn sleeveless bandi (a short open-front vest) of faded grey-white cloth with frayed edges, and a minimal plain off-white loincloth; otherwise bare. Barefoot, no jewellery, no beads, no forehead mark. His only belongings: a dried bottle-gourd water vessel (natural tan, narrow neck) and a small hand-made unfired clay chilim (a straight conical clay pipe, matte raw grey-brown clay, never kiln-fired). Pose: seated cross-legged facing screen-left before one fresh leaf plate served with several rich dishes, his right hand mixing all the dishes together into one heap, face calm and indifferent, no relish. Show the subject in full, isolated on a plain pure white background, with no ground, no scenery, no cast shadow, and a clear white margin all round, so the background can be removed into a transparent cut-out. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `P_GM_SPEAKING`

- kind: pose | scenes: S7, S9 | covers about **6** shot(s) in the current plan
- preset roles: 09:right, 02:extra char layer
- attach as reference: CH_GM, PR_GOURD_CHILIM
- aspect / layer: cut-out (white background to remove); Used at the road (S7) and at the well (S9) by changing only the background layers.
- source refs: A1:127-131 laughs and speaks to both; A1:138-142 teaching
- OWNER_CHOICE: OC-12 posture at the trough during the teaching (seated default)
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Shri Gajanan Maharaj: a young man in the prime of youth (looks about 25 to 30), strong and well built, muscular upper arms and neck, broad chest, radiant calm handsome face, eyes half-lowered with the gaze resting on the tip of his nose, short cropped dark hair, clean-shaven, warm medium-brown skin. He wears only one old, worn, torn sleeveless bandi (a short open-front vest) of faded grey-white cloth with frayed edges, and a minimal plain off-white loincloth; otherwise bare. Barefoot, no jewellery, no beads, no forehead mark. His only belongings: a dried bottle-gourd water vessel (natural tan, narrow neck) and a small hand-made unfired clay chilim (a straight conical clay pipe, matte raw grey-brown clay, never kiln-fired). Pose: seated cross-legged facing screen-left, speaking gently, right hand raised a little with the palm open in explanation, a faint smile, the gourd beside him. Show the subject in full, isolated on a plain pure white background, with no ground, no scenery, no cast shadow, and a clear white margin all round, so the background can be removed into a transparent cut-out. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `P_GM_RUN`

- kind: pose | scenes: S9 | covers about **1** shot(s) in the current plan
- preset roles: 04:char, 02:extra char layer
- attach as reference: CH_GM
- aspect / layer: cut-out (white background to remove)
- source refs: A1:144 runs off like the wind, no destination (FINAL A1-11)
- OWNER_CHOICE: OC-13 carries the gourd while running (default yes)
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Shri Gajanan Maharaj: a young man in the prime of youth (looks about 25 to 30), strong and well built, muscular upper arms and neck, broad chest, radiant calm handsome face, eyes half-lowered with the gaze resting on the tip of his nose, short cropped dark hair, clean-shaven, warm medium-brown skin. He wears only one old, worn, torn sleeveless bandi (a short open-front vest) of faded grey-white cloth with frayed edges, and a minimal plain off-white loincloth; otherwise bare. Barefoot, no jewellery, no beads, no forehead mark. His only belongings: a dried bottle-gourd water vessel (natural tan, narrow neck) and a small hand-made unfired clay chilim (a straight conical clay pipe, matte raw grey-brown clay, never kiln-fired). Pose: running fast in full side view toward screen-left, long stride, body leaning forward, the gourd held in his left hand, the bandi flapping, face calm. Show the subject in full, isolated on a plain pure white background, with no ground, no scenery, no cast shadow, and a clear white margin all round, so the background can be removed into a transparent cut-out. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `F_GM_CALM`

- kind: pose | scenes: S1, S2, S5, S9 | covers about **4** shot(s) in the current plan
- preset roles: 08:face, 07:face
- attach as reference: CH_GM
- aspect / layer: cut-out (white background to remove); Use preset 08 with its halo at low intensity or off (no supernatural glow unless the owner decides).
- source refs: A1:91 nose-tip gaze, calm, shining like the young sun (simile only)
- OWNER_CHOICE: OC-14 preset 08 halo
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Shri Gajanan Maharaj: a young man in the prime of youth (looks about 25 to 30), strong and well built, muscular upper arms and neck, broad chest, radiant calm handsome face, eyes half-lowered with the gaze resting on the tip of his nose, short cropped dark hair, clean-shaven, warm medium-brown skin. He wears only one old, worn, torn sleeveless bandi (a short open-front vest) of faded grey-white cloth with frayed edges, and a minimal plain off-white loincloth; otherwise bare. Barefoot, no jewellery, no beads, no forehead mark. His only belongings: a dried bottle-gourd water vessel (natural tan, narrow neck) and a small hand-made unfired clay chilim (a straight conical clay pipe, matte raw grey-brown clay, never kiln-fired). Face close-up: three-quarter view facing screen-left, eyes half-lowered with the gaze on the tip of the nose, serene, very calm. Head-and-shoulders close-up, face filling the upper two thirds, isolated on a plain pure white background, no shadow, white margin all round (for a transparent cut-out). Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `F_GM_LOOK_UP`

- kind: pose | scenes: S4, S9 | covers about **2** shot(s) in the current plan
- preset roles: 07:face, 08:face
- attach as reference: CH_GM, F_GM_CALM
- aspect / layer: cut-out (white background to remove)
- source refs: A1:110-111
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Shri Gajanan Maharaj: a young man in the prime of youth (looks about 25 to 30), strong and well built, muscular upper arms and neck, broad chest, radiant calm handsome face, eyes half-lowered with the gaze resting on the tip of his nose, short cropped dark hair, clean-shaven, warm medium-brown skin. He wears only one old, worn, torn sleeveless bandi (a short open-front vest) of faded grey-white cloth with frayed edges, and a minimal plain off-white loincloth; otherwise bare. Barefoot, no jewellery, no beads, no forehead mark. His only belongings: a dried bottle-gourd water vessel (natural tan, narrow neck) and a small hand-made unfired clay chilim (a straight conical clay pipe, matte raw grey-brown clay, never kiln-fired). Face close-up: three-quarter view facing screen-left, head slightly raised, eyes open and steady, attention gathered between the eyebrows, radiant, silent. Head-and-shoulders close-up, face filling the upper two thirds, isolated on a plain pure white background, no shadow, white margin all round (for a transparent cut-out). Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `F_GM_LAUGH`

- kind: pose | scenes: S7 | covers about **1** shot(s) in the current plan
- preset roles: 07:face
- attach as reference: CH_GM, F_GM_CALM
- aspect / layer: cut-out (white background to remove)
- source refs: A1:127 laughs and looks at both
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Shri Gajanan Maharaj: a young man in the prime of youth (looks about 25 to 30), strong and well built, muscular upper arms and neck, broad chest, radiant calm handsome face, eyes half-lowered with the gaze resting on the tip of his nose, short cropped dark hair, clean-shaven, warm medium-brown skin. He wears only one old, worn, torn sleeveless bandi (a short open-front vest) of faded grey-white cloth with frayed edges, and a minimal plain off-white loincloth; otherwise bare. Barefoot, no jewellery, no beads, no forehead mark. His only belongings: a dried bottle-gourd water vessel (natural tan, narrow neck) and a small hand-made unfired clay chilim (a straight conical clay pipe, matte raw grey-brown clay, never kiln-fired). Face close-up: three-quarter view facing screen-left, a warm open laugh, eyes creased with amusement, looking at the two men. Head-and-shoulders close-up, face filling the upper two thirds, isolated on a plain pure white background, no shadow, white margin all round (for a transparent cut-out). Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `PAIR_BA_DK_WALK`

- kind: pose | scenes: S3 | covers about **1** shot(s) in the current plan
- preset roles: 04:char
- attach as reference: CH_BA, CH_DK
- aspect / layer: cut-out (white background to remove)
- source refs: A1:97 walking along the road; A1:98 both astonished
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Bankatlal Agarwal: an adult man of about 35, medium height, slightly full build, kind attentive face, small neat moustache, warm brown skin. He wears a cream-white turban wound in a round pagadi, a long sage-green cotton angarkha coat to below the knee, tied at the side, over a white dhoti, and a cream shoulder cloth (uparna) over his left shoulder. Barefoot. Nothing in his hands unless stated. Damodarpant Kulkarni: an adult man of about 35, lean and slightly taller than Bankatlal, narrow face, thin moustache, warm brown skin. He wears a terracotta-red Maharashtrian pagadi turban, a plain white long-sleeved cotton angarkha shirt to the knee, a white dhoti, and an off-white uparna over one shoulder. Barefoot. Pose: the two men walking together side by side toward screen-right, Bankatlal nearer to camera, Damodarpant just behind him, both turning their heads toward something ahead and down to the right, beginning to be astonished. Show the subject in full, isolated on a plain pure white background, with no ground, no scenery, no cast shadow, and a clear white margin all round, so the background can be removed into a transparent cut-out. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `PAIR_BA_DK_STAND`

- kind: pose | scenes: S3, S5, S7, S9 | covers about **6** shot(s) in the current plan
- preset roles: 09:left, 02:extra char layer
- attach as reference: CH_BA, CH_DK
- aspect / layer: cut-out (white background to remove); Neutral pair: safe for lines whose speaker is unclear (103-104, 113, 122-124).
- source refs: A1:102 they stand on the road to watch; A1:113 plural request (no single speaker shown); A1:132; A1:138-142 listening
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Bankatlal Agarwal: an adult man of about 35, medium height, slightly full build, kind attentive face, small neat moustache, warm brown skin. He wears a cream-white turban wound in a round pagadi, a long sage-green cotton angarkha coat to below the knee, tied at the side, over a white dhoti, and a cream shoulder cloth (uparna) over his left shoulder. Barefoot. Nothing in his hands unless stated. Damodarpant Kulkarni: an adult man of about 35, lean and slightly taller than Bankatlal, narrow face, thin moustache, warm brown skin. He wears a terracotta-red Maharashtrian pagadi turban, a plain white long-sleeved cotton angarkha shirt to the knee, a white dhoti, and an off-white uparna over one shoulder. Barefoot. Pose: the two men standing side by side facing screen-right, Bankatlal nearer to camera, both quiet and attentive, hands at rest, neither speaking. Show the subject in full, isolated on a plain pure white background, with no ground, no scenery, no cast shadow, and a clear white margin all round, so the background can be removed into a transparent cut-out. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `P_BA_TALK`

- kind: pose | scenes: S3, S6 | covers about **5** shot(s) in the current plan
- preset roles: 09:left
- attach as reference: CH_BA
- aspect / layer: cut-out (white background to remove)
- source refs: A1:102 Bankatlal to Pant; A1:119-121 Bankatlal to Pant
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Bankatlal Agarwal: an adult man of about 35, medium height, slightly full build, kind attentive face, small neat moustache, warm brown skin. He wears a cream-white turban wound in a round pagadi, a long sage-green cotton angarkha coat to below the knee, tied at the side, over a white dhoti, and a cream shoulder cloth (uparna) over his left shoulder. Barefoot. Nothing in his hands unless stated. Pose: standing in three-quarter view facing screen-right, speaking earnestly to a friend, one hand raised a little, open palm. Show the subject in full, isolated on a plain pure white background, with no ground, no scenery, no cast shadow, and a clear white margin all round, so the background can be removed into a transparent cut-out. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `P_DK_LISTEN`

- kind: pose | scenes: S3, S6 | covers about **5** shot(s) in the current plan
- preset roles: 09:right
- attach as reference: CH_DK
- aspect / layer: cut-out (white background to remove)
- source refs: A1:102; A1:119-121 listener
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Damodarpant Kulkarni: an adult man of about 35, lean and slightly taller than Bankatlal, narrow face, thin moustache, warm brown skin. He wears a terracotta-red Maharashtrian pagadi turban, a plain white long-sleeved cotton angarkha shirt to the knee, a white dhoti, and an off-white uparna over one shoulder. Barefoot. Pose: standing in three-quarter view facing screen-left, listening thoughtfully, hands loosely joined in front. Show the subject in full, isolated on a plain pure white background, with no ground, no scenery, no cast shadow, and a clear white margin all round, so the background can be removed into a transparent cut-out. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `P_BA_ASK`

- kind: pose | scenes: S4 | covers about **2** shot(s) in the current plan
- preset roles: 04:char, 09:left
- attach as reference: CH_BA
- aspect / layer: cut-out (white background to remove)
- source refs: A1:108 steps forward first, humbly; A1:109 asks, offers food
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Bankatlal Agarwal: an adult man of about 35, medium height, slightly full build, kind attentive face, small neat moustache, warm brown skin. He wears a cream-white turban wound in a round pagadi, a long sage-green cotton angarkha coat to below the knee, tied at the side, over a white dhoti, and a cream shoulder cloth (uparna) over his left shoulder. Barefoot. Nothing in his hands unless stated. Pose: stepping forward in three-quarter view facing screen-right, leaning slightly down toward a seated person (not drawn), palms joined humbly at the chest, gentle concerned face, as if asking a polite question. Show the subject in full, isolated on a plain pure white background, with no ground, no scenery, no cast shadow, and a clear white margin all round, so the background can be removed into a transparent cut-out. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `P_DK_OFFER`

- kind: pose | scenes: S7 | covers about **1** shot(s) in the current plan
- preset roles: 09:left
- attach as reference: CH_DK
- aspect / layer: cut-out (white background to remove)
- source refs: A1:126 this servant is ready to bring water
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Damodarpant Kulkarni: an adult man of about 35, lean and slightly taller than Bankatlal, narrow face, thin moustache, warm brown skin. He wears a terracotta-red Maharashtrian pagadi turban, a plain white long-sleeved cotton angarkha shirt to the knee, a white dhoti, and an off-white uparna over one shoulder. Barefoot. Pose: standing in three-quarter view facing screen-right, bending a little toward a seated person (not drawn), one hand on his chest in humble offer of service, eager face. Show the subject in full, isolated on a plain pure white background, with no ground, no scenery, no cast shadow, and a clear white margin all round, so the background can be removed into a transparent cut-out. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `P_DK_WALK_TO_HOUSE`

- kind: pose | scenes: S7 | covers about **1** shot(s) in the current plan
- preset roles: 04:char
- attach as reference: CH_DK
- aspect / layer: cut-out (white background to remove)
- source refs: A1:132 both rejoice; A1:133 goes into Devidas's house (FINAL A1-5)
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Damodarpant Kulkarni: an adult man of about 35, lean and slightly taller than Bankatlal, narrow face, thin moustache, warm brown skin. He wears a terracotta-red Maharashtrian pagadi turban, a plain white long-sleeved cotton angarkha shirt to the knee, a white dhoti, and an off-white uparna over one shoulder. Barefoot. Pose: walking briskly away from camera toward screen-left, seen from behind in three-quarter back view, joyful hurry. Show the subject in full, isolated on a plain pure white background, with no ground, no scenery, no cast shadow, and a clear white margin all round, so the background can be removed into a transparent cut-out. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `P_DK_WALK_GADVA`

- kind: pose | scenes: S8 | covers about **1** shot(s) in the current plan
- preset roles: 04:char
- attach as reference: CH_DK, PR_GADVA_VETIVER
- aspect / layer: cut-out (white background to remove)
- source refs: A1:135 Pant arrives with water in a gadva
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Damodarpant Kulkarni: an adult man of about 35, lean and slightly taller than Bankatlal, narrow face, thin moustache, warm brown skin. He wears a terracotta-red Maharashtrian pagadi turban, a plain white long-sleeved cotton angarkha shirt to the knee, a white dhoti, and an off-white uparna over one shoulder. Barefoot. Pose: hurrying in side view toward screen-right, carrying the brass gadva of water carefully in both hands before his chest. Show the subject in full, isolated on a plain pure white background, with no ground, no scenery, no cast shadow, and a clear white margin all round, so the background can be removed into a transparent cut-out. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `P_DK_HOLD_GADVA`

- kind: pose | scenes: S8, S9 | covers about **2** shot(s) in the current plan
- preset roles: 09:left
- attach as reference: CH_DK, PR_GADVA_VETIVER
- aspect / layer: cut-out (white background to remove)
- source refs: A1:136-137 do not drink that muddy water; see, I brought clean water
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Damodarpant Kulkarni: an adult man of about 35, lean and slightly taller than Bankatlal, narrow face, thin moustache, warm brown skin. He wears a terracotta-red Maharashtrian pagadi turban, a plain white long-sleeved cotton angarkha shirt to the knee, a white dhoti, and an off-white uparna over one shoulder. Barefoot. Pose: standing in three-quarter view facing screen-right, holding the brass gadva out with both hands toward a seated person (not drawn), worried, pleading face. Show the subject in full, isolated on a plain pure white background, with no ground, no scenery, no cast shadow, and a clear white margin all round, so the background can be removed into a transparent cut-out. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `P_DV_CARRY_PLATE`

- kind: pose | scenes: S5 | covers about **1** shot(s) in the current plan
- preset roles: 04:char
- attach as reference: CH_DV, PR_LEAF_PLATES
- aspect / layer: cut-out (white background to remove)
- source refs: A1:114 Devidas brings the plate and sets it at the door before the Swami
- OWNER_CHOICE: OC-07
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Devidas: a Brahmin householder of about 45, medium build, gentle devout face, clean-shaven, shaved head with a small tuft (shikha) at the crown, greying at the temples, a small red tilak on the forehead, a white sacred thread across the chest. Bare-chested, a white dhoti, and an off-white uparna across one shoulder. Barefoot. Pose: walking in side view toward screen-right, coming out of a doorway, carrying one fresh leaf plate served with rich dishes in both hands, quick and willing, silent. Show the subject in full, isolated on a plain pure white background, with no ground, no scenery, no cast shadow, and a clear white margin all round, so the background can be removed into a transparent cut-out. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `F_BA_AMAZED`

- kind: pose | scenes: S3 | covers about **1** shot(s) in the current plan
- preset roles: 07:face
- attach as reference: CH_BA
- aspect / layer: cut-out (white background to remove)
- source refs: A1:98 astonished; A1:99
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Bankatlal Agarwal: an adult man of about 35, medium height, slightly full build, kind attentive face, small neat moustache, warm brown skin. He wears a cream-white turban wound in a round pagadi, a long sage-green cotton angarkha coat to below the knee, tied at the side, over a white dhoti, and a cream shoulder cloth (uparna) over his left shoulder. Barefoot. Nothing in his hands unless stated. Face close-up: three-quarter view facing screen-right, eyebrows raised, eyes wide in astonishment and puzzlement. Head-and-shoulders close-up, face filling the upper two thirds, isolated on a plain pure white background, no shadow, white margin all round (for a transparent cut-out). Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `F_BA_REVERENT`

- kind: pose | scenes: S6, S7 | covers about **1** shot(s) in the current plan
- preset roles: 07:face, 08:face
- attach as reference: CH_BA, F_BA_AMAZED
- aspect / layer: cut-out (white background to remove)
- source refs: A1:119 our mistake; A1:121; A1:132 our fortune is blessed
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Bankatlal Agarwal: an adult man of about 35, medium height, slightly full build, kind attentive face, small neat moustache, warm brown skin. He wears a cream-white turban wound in a round pagadi, a long sage-green cotton angarkha coat to below the knee, tied at the side, over a white dhoti, and a cream shoulder cloth (uparna) over his left shoulder. Barefoot. Nothing in his hands unless stated. Face close-up: three-quarter view facing screen-right, soft moved expression of realisation and reverence, a slight humble smile. Head-and-shoulders close-up, face filling the upper two thirds, isolated on a plain pure white background, no shadow, white margin all round (for a transparent cut-out). Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `F_DK_ALARM`

- kind: pose | scenes: S8 | covers about **1** shot(s) in the current plan
- preset roles: 07:face
- attach as reference: CH_DK
- aspect / layer: cut-out (white background to remove)
- source refs: A1:136 haa haa, do not drink
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Damodarpant Kulkarni: an adult man of about 35, lean and slightly taller than Bankatlal, narrow face, thin moustache, warm brown skin. He wears a terracotta-red Maharashtrian pagadi turban, a plain white long-sleeved cotton angarkha shirt to the knee, a white dhoti, and an off-white uparna over one shoulder. Barefoot. Face close-up: three-quarter view facing screen-right, sudden alarm and concern, mouth open as if calling out 'stop'. Head-and-shoulders close-up, face filling the upper two thirds, isolated on a plain pure white background, no shadow, white margin all round (for a transparent cut-out). Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `POSE_SILENT_BOW`

- kind: pose | scenes: S4 | covers about **1** shot(s) in the current plan
- preset roles: 05:pose
- attach as reference: CH_GM, CH_BA, CH_DK, P_GM_LOOK_UP
- aspect / layer: cut-out (white background to remove)
- source refs: A1:112 silent namaskar (two men: analysis_v3 A1-1 RESOLVED-PRINT)
- OWNER_CHOICE: OC-15 bow type: standing folded-hands bow (default), not prostration
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Shri Gajanan Maharaj: a young man in the prime of youth (looks about 25 to 30), strong and well built, muscular upper arms and neck, broad chest, radiant calm handsome face, eyes half-lowered with the gaze resting on the tip of his nose, short cropped dark hair, clean-shaven, warm medium-brown skin. He wears only one old, worn, torn sleeveless bandi (a short open-front vest) of faded grey-white cloth with frayed edges, and a minimal plain off-white loincloth; otherwise bare. Barefoot, no jewellery, no beads, no forehead mark. His only belongings: a dried bottle-gourd water vessel (natural tan, narrow neck) and a small hand-made unfired clay chilim (a straight conical clay pipe, matte raw grey-brown clay, never kiln-fired). Bankatlal Agarwal: an adult man of about 35, medium height, slightly full build, kind attentive face, small neat moustache, warm brown skin. He wears a cream-white turban wound in a round pagadi, a long sage-green cotton angarkha coat to below the knee, tied at the side, over a white dhoti, and a cream shoulder cloth (uparna) over his left shoulder. Barefoot. Nothing in his hands unless stated. Damodarpant Kulkarni: an adult man of about 35, lean and slightly taller than Bankatlal, narrow face, thin moustache, warm brown skin. He wears a terracotta-red Maharashtrian pagadi turban, a plain white long-sleeved cotton angarkha shirt to the knee, a white dhoti, and an off-white uparna over one shoulder. Barefoot. Pose group: Maharaj seated among the leaf plates on the right, facing screen-left, calm and silent; on the left Bankatlal and Damodarpant standing, bowing their heads with palms joined at the chest in a silent namaskar, content faces. No one speaks. Show the subject in full, isolated on a plain pure white background, with no ground, no scenery, no cast shadow, and a clear white margin all round, so the background can be removed into a transparent cut-out. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `POSE_READY_TO_FALL`

- kind: pose | scenes: S9 | covers about **1** shot(s) in the current plan
- preset roles: 05:pose
- attach as reference: CH_GM, CH_BA, CH_DK, PR_GADVA_VETIVER
- aspect / layer: cut-out (white background to remove)
- source refs: A1:143 overcome, READY to fall at his feet (direction note)
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Shri Gajanan Maharaj: a young man in the prime of youth (looks about 25 to 30), strong and well built, muscular upper arms and neck, broad chest, radiant calm handsome face, eyes half-lowered with the gaze resting on the tip of his nose, short cropped dark hair, clean-shaven, warm medium-brown skin. He wears only one old, worn, torn sleeveless bandi (a short open-front vest) of faded grey-white cloth with frayed edges, and a minimal plain off-white loincloth; otherwise bare. Barefoot, no jewellery, no beads, no forehead mark. His only belongings: a dried bottle-gourd water vessel (natural tan, narrow neck) and a small hand-made unfired clay chilim (a straight conical clay pipe, matte raw grey-brown clay, never kiln-fired). Bankatlal Agarwal: an adult man of about 35, medium height, slightly full build, kind attentive face, small neat moustache, warm brown skin. He wears a cream-white turban wound in a round pagadi, a long sage-green cotton angarkha coat to below the knee, tied at the side, over a white dhoti, and a cream shoulder cloth (uparna) over his left shoulder. Barefoot. Nothing in his hands unless stated. Damodarpant Kulkarni: an adult man of about 35, lean and slightly taller than Bankatlal, narrow face, thin moustache, warm brown skin. He wears a terracotta-red Maharashtrian pagadi turban, a plain white long-sleeved cotton angarkha shirt to the knee, a white dhoti, and an off-white uparna over one shoulder. Barefoot. Pose group: Maharaj seated on the right facing screen-left; Bankatlal and Damodarpant on the left, deeply moved, eyes moist, palms joined, both beginning to kneel forward toward his feet but not yet down; Damodarpant's brass gadva set on the ground beside him. Show the subject in full, isolated on a plain pure white background, with no ground, no scenery, no cast shadow, and a clear white margin all round, so the background can be removed into a transparent cut-out. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

### beat_still

#### `INS_FEAST_PREP`

- kind: beat_still | scenes: S2 | covers about **1** shot(s) in the current plan
- preset roles: 10:insert
- attach as reference: MID_ROAD_HOUSE, PR_LEAF_PLATES
- aspect / layer: full frame / layer
- source refs: A1:86 meal being prepared for his son's Ritushanti (FINAL S5-3)
- OWNER_CHOICE: OC-16 show feast preparation only through objects (no household members)
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Close insert inside Devidas's house: brass cooking vessels on a clay hearth with a low wood fire, a heap of cooked white rice, a neat stack of fresh leaf plates, warm interior light from a doorway. No people, no hands, no faces. Full-frame 16:9 landscape picture, edge to edge, no border, no frame mount. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `INS_LEAF_PLATES`

- kind: beat_still | scenes: S2 | covers about **1** shot(s) in the current plan
- preset roles: 10:insert
- attach as reference: PR_LEAF_PLATES, MID_ROAD_HOUSE
- aspect / layer: full frame / layer
- source refs: A1:87
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Close insert at ground level: used leaf plates thrown on the dusty road, crumpled edges, a few scattered grains of white rice; the base of the house's plinth step at the top of the frame. No people. Full-frame 16:9 landscape picture, edge to edge, no border, no frame mount. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `INS_CHILIM_GOURD`

- kind: beat_still | scenes: S2 | covers about **1** shot(s) in the current plan
- preset roles: 10:insert
- attach as reference: CH_GM, PR_GOURD_CHILIM
- aspect / layer: full frame / layer
- source refs: A1:88-90; A1:89 no possessions but these (FINAL G-4)
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Shri Gajanan Maharaj: a young man in the prime of youth (looks about 25 to 30), strong and well built, muscular upper arms and neck, broad chest, radiant calm handsome face, eyes half-lowered with the gaze resting on the tip of his nose, short cropped dark hair, clean-shaven, warm medium-brown skin. He wears only one old, worn, torn sleeveless bandi (a short open-front vest) of faded grey-white cloth with frayed edges, and a minimal plain off-white loincloth; otherwise bare. Barefoot, no jewellery, no beads, no forehead mark. His only belongings: a dried bottle-gourd water vessel (natural tan, narrow neck) and a small hand-made unfired clay chilim (a straight conical clay pipe, matte raw grey-brown clay, never kiln-fired). Close insert: Maharaj's right hand (only the hand, wrist and knee visible) resting on his crossed knee holding the small unfired clay chilim; the dried gourd water vessel stands on the dusty ground beside the knee; the frayed hem of the old bandi at the top edge. Full-frame 16:9 landscape picture, edge to edge, no border, no frame mount. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `INS_PICK_GRAIN`

- kind: beat_still | scenes: S2 | covers about **1** shot(s) in the current plan
- preset roles: 10:insert
- attach as reference: CH_GM, PR_LEAF_PLATES
- aspect / layer: full frame / layer
- source refs: A1:94
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Shri Gajanan Maharaj: a young man in the prime of youth (looks about 25 to 30), strong and well built, muscular upper arms and neck, broad chest, radiant calm handsome face, eyes half-lowered with the gaze resting on the tip of his nose, short cropped dark hair, clean-shaven, warm medium-brown skin. He wears only one old, worn, torn sleeveless bandi (a short open-front vest) of faded grey-white cloth with frayed edges, and a minimal plain off-white loincloth; otherwise bare. Barefoot, no jewellery, no beads, no forehead mark. His only belongings: a dried bottle-gourd water vessel (natural tan, narrow neck) and a small hand-made unfired clay chilim (a straight conical clay pipe, matte raw grey-brown clay, never kiln-fired). Close insert: Maharaj's fingers picking up one single grain of white rice from a used leaf plate on the dusty road. Full-frame 16:9 landscape picture, edge to edge, no border, no frame mount. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `INS_PLATE_SET`

- kind: beat_still | scenes: S5 | covers about **1** shot(s) in the current plan
- preset roles: 10:insert
- attach as reference: CH_DV, PR_LEAF_PLATES, MID_ROAD_HOUSE
- aspect / layer: full frame / layer
- source refs: A1:114 plate set at the door before the Swami
- OWNER_CHOICE: OC-07
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Devidas: a Brahmin householder of about 45, medium build, gentle devout face, clean-shaven, shaved head with a small tuft (shikha) at the crown, greying at the temples, a small red tilak on the forehead, a white sacred thread across the chest. Bare-chested, a white dhoti, and an off-white uparna across one shoulder. Barefoot. Close insert: Devidas's hands (only the hands and forearms with the edge of a white dhoti) setting the fresh leaf plate of rich dishes down on the ground just in front of the wooden door's plinth step. Full-frame 16:9 landscape picture, edge to edge, no border, no frame mount. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `INS_MIXING`

- kind: beat_still | scenes: S5 | covers about **2** shot(s) in the current plan
- preset roles: 10:insert
- attach as reference: CH_GM, PR_LEAF_PLATES, P_GM_EATING
- aspect / layer: full frame / layer
- source refs: A1:118 all dishes made one; no like or dislike
- OWNER_CHOICE: OC-07
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Shri Gajanan Maharaj: a young man in the prime of youth (looks about 25 to 30), strong and well built, muscular upper arms and neck, broad chest, radiant calm handsome face, eyes half-lowered with the gaze resting on the tip of his nose, short cropped dark hair, clean-shaven, warm medium-brown skin. He wears only one old, worn, torn sleeveless bandi (a short open-front vest) of faded grey-white cloth with frayed edges, and a minimal plain off-white loincloth; otherwise bare. Barefoot, no jewellery, no beads, no forehead mark. His only belongings: a dried bottle-gourd water vessel (natural tan, narrow neck) and a small hand-made unfired clay chilim (a straight conical clay pipe, matte raw grey-brown clay, never kiln-fired). Close insert from above: Maharaj's right hand mixing all the rich dishes on the leaf plate together into one single heap. Full-frame 16:9 landscape picture, edge to edge, no border, no frame mount. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `INS_EMPTY_GOURD`

- kind: beat_still | scenes: S7 | covers about **1** shot(s) in the current plan
- preset roles: 10:insert
- attach as reference: PR_GOURD_CHILIM, SKY_NOON
- aspect / layer: full frame / layer
- source refs: A1:125-126 no water in the gourd
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Close insert: the dried gourd water vessel lying on its side on hot, pale, cracked dusty ground in harsh noon sun, its mouth open and dry, clearly empty; a short hard shadow. Full-frame 16:9 landscape picture, edge to edge, no border, no frame mount. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `INS_TROUGH_WATER`

- kind: beat_still | scenes: S8, S9 | covers about **2** shot(s) in the current plan
- preset roles: 10:insert
- attach as reference: MID_WELL_TROUGH
- aspect / layer: full frame / layer; Reused in S9 for 'muddy, clear or scented: the same water'.
- source refs: A1:134; A1:136 muddy water fit for animals; A1:139-140 muddy or clear, the same water
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Close insert: the stone cattle trough, its shallow water muddy brown, a cow's muzzle drinking at one end, ripples on the surface. Full-frame 16:9 landscape picture, edge to edge, no border, no frame mount. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `INS_GADVA_VETIVER`

- kind: beat_still | scenes: S8, S9 | covers about **2** shot(s) in the current plan
- preset roles: 10:insert
- attach as reference: PR_GADVA_VETIVER, CH_DK
- aspect / layer: full frame / layer; Reused in S9 next to INS_TROUGH_WATER.
- source refs: A1:137
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Damodarpant Kulkarni: an adult man of about 35, lean and slightly taller than Bankatlal, narrow face, thin moustache, warm brown skin. He wears a terracotta-red Maharashtrian pagadi turban, a plain white long-sleeved cotton angarkha shirt to the knee, a white dhoti, and an off-white uparna over one shoulder. Barefoot. Close insert: two hands (Damodarpant's, white angarkha sleeves) holding the brass gadva forward, seen from slightly above: clear cool water with a small bundle of pale golden vetiver roots in it. Full-frame 16:9 landscape picture, edge to edge, no border, no frame mount. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `BEAT_S3_TWO_MEN_SEE`

- kind: beat_still | scenes: S3 | covers about **2** shot(s) in the current plan
- preset roles: 03:img
- attach as reference: CH_BA, CH_DK, P_GM_PICKING, LOC_ROAD_REF
- aspect / layer: full frame / layer
- source refs: A1:97-98; A1:102 stand on the road to watch
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Bankatlal Agarwal: an adult man of about 35, medium height, slightly full build, kind attentive face, small neat moustache, warm brown skin. He wears a cream-white turban wound in a round pagadi, a long sage-green cotton angarkha coat to below the knee, tied at the side, over a white dhoti, and a cream shoulder cloth (uparna) over his left shoulder. Barefoot. Nothing in his hands unless stated. Damodarpant Kulkarni: an adult man of about 35, lean and slightly taller than Bankatlal, narrow face, thin moustache, warm brown skin. He wears a terracotta-red Maharashtrian pagadi turban, a plain white long-sleeved cotton angarkha shirt to the knee, a white dhoti, and an off-white uparna over one shoulder. Barefoot. Shri Gajanan Maharaj: a young man in the prime of youth (looks about 25 to 30), strong and well built, muscular upper arms and neck, broad chest, radiant calm handsome face, eyes half-lowered with the gaze resting on the tip of his nose, short cropped dark hair, clean-shaven, warm medium-brown skin. He wears only one old, worn, torn sleeveless bandi (a short open-front vest) of faded grey-white cloth with frayed edges, and a minimal plain off-white loincloth; otherwise bare. Barefoot, no jewellery, no beads, no forehead mark. His only belongings: a dried bottle-gourd water vessel (natural tan, narrow neck) and a small hand-made unfired clay chilim (a straight conical clay pipe, matte raw grey-brown clay, never kiln-fired). The road in front of Devidas's house in Shegaon: a dusty unpaved village road running across the picture; on the left a modest but solid village house with thick mud-plastered ochre walls, a terracotta clay-tile roof, a raised earthen plinth step (ota) and a heavy plain wooden door standing half open onto a dark interior; neighbouring low houses and neem trees further down the road. On the road in front of the door lie several used leaf plates (round plates of stitched dry leaves) with a few scattered grains of leftover white rice. Over-the-shoulder view: Bankatlal and Damodarpant in the left foreground seen from behind in three-quarter back view, standing on the road and looking toward Maharaj, who sits small in the middle distance among the used leaf plates before Devidas's house, picking rice grains. Morning light. Full-frame 16:9 landscape picture, edge to edge, no border, no frame mount. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `BEAT_S7_BIRDS`

- kind: beat_still | scenes: S7 | covers about **1** shot(s) in the current plan
- preset roles: 03:img
- attach as reference: FG_NEEM, SKY_NOON
- aspect / layer: full frame / layer
- source refs: A1:123 birds went to the trees for shelter
- OWNER_CHOICE: none
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Noon view up into a neem tree: small brown village birds (sparrows and mynas) settling on the shaded branches; bleached noon sky beyond; below, the empty hot road. No people. Full-frame 16:9 landscape picture, edge to edge, no border, no frame mount. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

#### `BEAT_S8_GM_DRINKS`

- kind: beat_still | scenes: S8 | covers about **1** shot(s) in the current plan
- preset roles: 03:img
- attach as reference: CH_GM, LOC_WELL_REF, PR_GOURD_CHILIM
- aspect / layer: full frame / layer
- source refs: A1:134-135 goes to the trough, drinks, belches with satisfaction
- OWNER_CHOICE: OC-12 how he drinks (cupped hands default)
- status: DRAFT_NOT_APPROVED

```text
Flat-colour 2D Indian devotional storybook illustration in exactly the look of the attached style reference images: clean, confident dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines for folds, stone and brick texture and one soft shade tone, no gradients, no paper texture, no painterly brushwork, warm earth palette of raw sienna, burnt umber, warm ochre, terracotta, golden brass, off-white cotton with thin orange border stripes, deep indigo and sunset orange-and-gold skies, a FULL, richly drawn frame: every picture is a complete composed scene with foreground, midground and background all filled in (sky, ground, buildings, trees, carved stone, small village details), never an empty or plain background, except that single figures made as cut-outs are drawn on plain white, readable simple shapes with detailed line work on buildings and carved stone, calm respectful mood, a rural village of the Varhad region of Maharashtra in the 1870s, no modern objects of any kind, no text, no letters, no numbers, no writing in any script, no signature, no watermark, no halo, no glow around any person. Shri Gajanan Maharaj: a young man in the prime of youth (looks about 25 to 30), strong and well built, muscular upper arms and neck, broad chest, radiant calm handsome face, eyes half-lowered with the gaze resting on the tip of his nose, short cropped dark hair, clean-shaven, warm medium-brown skin. He wears only one old, worn, torn sleeveless bandi (a short open-front vest) of faded grey-white cloth with frayed edges, and a minimal plain off-white loincloth; otherwise bare. Barefoot, no jewellery, no beads, no forehead mark. His only belongings: a dried bottle-gourd water vessel (natural tan, narrow neck) and a small hand-made unfired clay chilim (a straight conical clay pipe, matte raw grey-brown clay, never kiln-fired). A village well a short way along the same road: a round open well with a low parapet of rough grey-brown stone, and beside it a long rectangular stone water trough (haal) for cattle, its water muddy brown and shallow; dusty trampled ground around it, a neem tree giving a little shade; two or three plain humped Deccan cattle drinking at the far end of the trough. Maharaj kneeling at the cattle trough beside the well, in side view facing screen-left, drinking the muddy water from his cupped hands, content; the cattle drinking at the far end; his gourd on the ground beside him; high noon sun. Full-frame 16:9 landscape picture, edge to edge, no border, no frame mount. Avoid: photorealism, 3D render, glossy digital painting, airbrushed gradients, neon colours, thick black comic outlines, text or lettering, watermark, halo, aura, light rays from a person, extra people, modern items (electric poles, plastic, metal sheets, glass windows, printed cloth, wristwatches, spectacles, footwear on Maharaj).
```

## (d) Questions for the owner (every unsettled look, with the proposed default)

| Id | Question | Proposed default |
|---|---|---|
| OC-00 | Visual style: the approved V5 look (D-016, flat colour, as in v5_inbox) or the frozen canon/style.yaml wording (1950s gouache on ivory card, as in pilot_refs/set_v1)? The two differ. | D-016 flat-colour V5 look (newest approved decision); the style paragraph keeps the style.yaml palette and its text-free rule. |
| OC-01 | Maharaj's apparent age: the Granth says only 'in the prime of youth' (74); 'about 30' is a web figure. | Looks 25-30. |
| OC-02 | Maharaj's hair, beard and skin tone are not stated anywhere. | Short cropped dark hair, clean-shaven, warm medium-brown skin (as in your M1_young_ref / set_v1). |
| OC-03 | The old bandi (88) with otherwise digambar (92): your set_v1 Maharaj has a loincloth and no bandi. | Show the worn grey-white open bandi plus a minimal off-white loincloth in every image (direction note: 'throughout'). |
| OC-04 | Bankatlal's look (none stated). | Your set_v1 colours: cream turban, sage-green angarkha, white dhoti, uparna, about 35; money pouch removed (it is an Adhyay 2 detail). |
| OC-05 | Damodarpant's look (none stated). set_v1 gave him a white cap that reads as a 20th-century 'Gandhi cap' and the same body/costume as Devidas. | Terracotta-red pagadi, white angarkha, lean, about 35: clearly different from Devidas. |
| OC-06 | Devidas's look and age (none stated; his son is 13-16 by FINAL S5-3). | About 45, shaved head with shikha, sacred thread, red tilak, bare-chested with uparna (set_v1 based). |
| OC-07 | Devidas's plate (114): the verse says 'patra' (material not stated); your easy script says 'patraval' (leaf plate). Which dishes? | Fresh leaf plate; rice, yellow dal, a vegetable, puris, two round sweets. |
| OC-08 | Time of day of S1-S6 (not stated; the story only reaches noon at 118/123). | Clear late-morning light for S1-S6, hard noon for S7-S9. |
| OC-09 | Devidas's house (not described; he heads a math). | A solid mud-plastered house with clay-tile roof, plinth step and heavy wooden door (as in your set_v1 location). |
| OC-10 | Well and trough design; which animals and how many (134 says 'all the animals'). | Round stone well, long stone trough, two or three humped Deccan cattle. |
| OC-11 | Village trees. | Neem (and babul in the distance). |
| OC-12 | How Maharaj drinks at the trough and his posture during the teaching (not stated). | Kneels and drinks from cupped hands; sits cross-legged by the trough for the teaching. |
| OC-13 | Does he carry the gourd when he runs (144)? | Yes, in his left hand. |
| OC-14 | Preset 08 adds a soft backdrop halo; the brief forbids a halo unless the research states it (91 and 111 speak of radiance, as similes). | Keep preset 08 but set its halo intensity to 0 (or at most 0.1 as plain backlight) for Maharaj. |
| OC-15 | The silent bow (112): standing namaskar or prostration? | Standing, heads bowed, palms joined (prostration would anticipate 143). |
| OC-16 | Feast preparation (86) and Devidas's son/household: show people? | Objects only (hearth, rice, leaf plates); no household members, no guests. |
| OC-17 | Narrator comparisons (116-117 jaggery-water, emperor's estate; 120-121 Arjuna and Subhadra): illustrate them? | No: cover them with Maharaj/Bankatlal images; no emperor, Arjuna or Subhadra figures. |
| OC-18 | Character presets (04/05/07/08/09) ship with a plain colour backdrop only. | Add the road or well layers as extra JSON layers behind the cut-outs (schema allows up to 8 layers; no code change); validate each shot. |

Research notes that affected this list: the house is Devidas's (FINAL A1-5); the gadva is brass (owner production decision, analysis_v3); 'haal' is a cattle trough (analysis_v3 G-1, glossary still says provisional); the muddy water is the trough's, never Damodarpant's (addendum F1); the two visitors bow at 112 (analysis_v3 A1-1); Maharaj runs with no destination (FINAL A1-11); no Sajjangad / Ramdas / Nath imagery (direction notes); the easy script is itself NOT VALIDATED against the verse.

## (e) Totals and reuse map

**Total unique images: 54** (de-duplicated). By kind: character_ref 4, prop 3, location 11, pose 24, beat_still 12. No separate costume images: costume is fixed inside each character reference sheet (one costume per character in Adhyay 1).

Shot-placed images: 44; reference-only images: 10. Shots planned: 61.

**Derived by changing only the background layer** (same cut-out, different place/sky):

- `P_GM_SEATED_CALM`: road morning (S2, S5) -> road noon (S7) -> well noon (S8).
- `P_GM_SPEAKING`: road noon (S7) -> well noon (S9).
- `PAIR_BA_DK_STAND`: road morning (S5) -> road noon (S7) -> well noon (S9).
- `P_BA_TALK` + `P_DK_LISTEN`: S3 and S6, same road background.
- `F_GM_CALM`, `F_GM_LOOK_UP`: S1/S2/S5/S9 and S4/S9.
- Road layers `MID_ROAD_HOUSE` + `FAR_VILLAGE`: under `SKY_MORNING` for S2-S6, under `SKY_NOON` for S7; `MID_SHEGAON` set reused in S6 (122). `INS_TROUGH_WATER` and `INS_GADVA_VETIVER` reused in S9.
- `11_scene_transition` needs no new images: scene_a / scene_b are flattened from the layer stacks above.

**Shot -> image ids per preset role, by scene beat** (shots = current allocation; a beat may gain or lose shots after re-timing without new images):

**S1** (2 shots)

| Beat | Preset | Roles -> image ids | Shots | Covers (ovi) |
|---|---|---|---|---|
| S1-B1 | 01_establishing_shot | sky=SKY_MORNING, mid=MID_SHEGAON, fx=FX_SUN, fg=FG_NEEM | 1 | Shegaon (58-60); caption 1878 added later |
| S1-B2 | 08_emotional_closeup | face=F_GM_CALM; bg=SKY_MORNING + FAR_VILLAGE | 1 | the young Gajanan seen there (74, 83) |

**S2** (9 shots)

| Beat | Preset | Roles -> image ids | Shots | Covers (ovi) |
|---|---|---|---|---|
| S2-B1 | 02_environmental_parallax | sky/far/mid = SKY_MORNING + FAR_VILLAGE + MID_ROAD_HOUSE, near=FG_NEEM | 1 | Devidas's house (84) |
| S2-B2 | 10_object_hand_insert | insert=INS_FEAST_PREP | 1 | feast preparation (86) |
| S2-B3 | 10_object_hand_insert | insert=INS_LEAF_PLATES | 1 | plates on the road (87) |
| S2-B4 | 02_environmental_parallax | SKY_MORNING + FAR_VILLAGE + MID_ROAD_HOUSE, near=FG_NEEM, + char layer P_GM_SEATED_CALM | 1 | seated there, bandi (88) |
| S2-B5 | 08_emotional_closeup | face=F_GM_CALM; bg road layers | 1 | nose-tip gaze, calm (91) |
| S2-B6 | 10_object_hand_insert | insert=INS_CHILIM_GOURD | 1 | gourd, chilim, digambar (89-92) |
| S2-B7 | 02_environmental_parallax | SKY_MORNING + FAR_VILLAGE + MID_ROAD_HOUSE + char layer P_GM_PICKING | 2 | searching plates; food is Brahman (93, 95-96) |
| S2-B8 | 10_object_hand_insert | insert=INS_PICK_GRAIN | 1 | picks each grain (94) |

**S3** (6 shots)

| Beat | Preset | Roles -> image ids | Shots | Covers (ovi) |
|---|---|---|---|---|
| S3-B1 | 04_character_entrance | char=PAIR_BA_DK_WALK, other=P_GM_PICKING; bg SKY_MORNING + FAR_VILLAGE + MID_ROAD_HOUSE | 1 | two men walking (97-98) |
| S3-B2 | 03_slow_cinematic_push | img=BEAT_S3_TWO_MEN_SEE | 2 | they see him; reasoning (98, 104-105) |
| S3-B3 | 07_character_reaction | face=F_BA_AMAZED | 1 | 'he looks mad' (99) |
| S3-B4 | 09_dialogue_composition | left=P_BA_TALK, right=P_DK_LISTEN; bg SKY_MORNING + FAR_VILLAGE + MID_ROAD_HOUSE | 2 | reasoning; Bankatlal: let us watch (100-102) |

**S4** (5 shots)

| Beat | Preset | Roles -> image ids | Shots | Covers (ovi) |
|---|---|---|---|---|
| S4-B1 | 04_character_entrance | char=P_BA_ASK, other=P_GM_PICKING; bg SKY_MORNING + FAR_VILLAGE + MID_ROAD_HOUSE | 1 | steps forward (108) |
| S4-B2 | 09_dialogue_composition | left=P_BA_ASK, right=P_GM_LOOK_UP; bg SKY_MORNING + FAR_VILLAGE + MID_ROAD_HOUSE | 1 | the question (109) |
| S4-B3 | 07_character_reaction | face=F_GM_LOOK_UP | 1 | no answer, looks up (110) |
| S4-B4 | 02_environmental_parallax | SKY_MORNING + FAR_VILLAGE + MID_ROAD_HOUSE + char layer P_GM_LOOK_UP | 1 | radiant, arms, chest (111) |
| S4-B5 | 05_bowing_prayer | pose=POSE_SILENT_BOW; bg road layers | 1 | silent bow (112) |

**S5** (8 shots)

| Beat | Preset | Roles -> image ids | Shots | Covers (ovi) |
|---|---|---|---|---|
| S5-B1 | 02_environmental_parallax | SKY_MORNING + FAR_VILLAGE + MID_ROAD_HOUSE + char layers PAIR_BA_DK_STAND, P_GM_SEATED_CALM | 1 | request to Devidas, speaker unnamed (113) |
| S5-B2 | 04_character_entrance | char=P_DV_CARRY_PLATE, other=P_GM_SEATED_CALM; bg SKY_MORNING + FAR_VILLAGE + MID_ROAD_HOUSE | 1 | Devidas brings the plate (114) |
| S5-B3 | 10_object_hand_insert | insert=INS_PLATE_SET | 1 | plate set at the door (114) |
| S5-B4 | 02_environmental_parallax | SKY_MORNING + FAR_VILLAGE + MID_ROAD_HOUSE + char layer P_GM_EATING | 2 | sits to eat; emperor comparison (115, 117) |
| S5-B5 | 08_emotional_closeup | face=F_GM_CALM | 1 | jaggery-water comparison (116) |
| S5-B6 | 10_object_hand_insert | insert=INS_MIXING | 2 | mixes all dishes (118) |

**S6** (5 shots)

| Beat | Preset | Roles -> image ids | Shots | Covers (ovi) |
|---|---|---|---|---|
| S6-B1 | 09_dialogue_composition | left=P_BA_TALK, right=P_DK_LISTEN; bg SKY_MORNING + FAR_VILLAGE + MID_ROAD_HOUSE | 3 | 'our mistake'; Arjuna; no more test (119-121) |
| S6-B2 | 07_character_reaction | face=F_BA_REVERENT | 1 | Arjuna/Subhadra (120) |
| S6-B3 | 01_establishing_shot | sky=SKY_MORNING, mid=MID_SHEGAON, fx=FX_SUN, fg=FG_NEEM (reuse of S1) | 1 | blessed is Shegaon (122) |

**S7** (9 shots)

| Beat | Preset | Roles -> image ids | Shots | Covers (ovi) |
|---|---|---|---|---|
| S7-B1 | 01_establishing_shot | sky=SKY_NOON, mid=MID_ROAD_HOUSE, fx=FX_SUN, fg=FG_NEEM | 1 | noon, ground hot (123) |
| S7-B2 | 03_slow_cinematic_push | img=BEAT_S7_BIRDS | 1 | birds to the trees (123) |
| S7-B3 | 02_environmental_parallax | SKY_NOON + FAR_VILLAGE + MID_ROAD_HOUSE + char layer P_GM_SEATED_CALM | 1 | joyful in full sun (124) |
| S7-B4 | 10_object_hand_insert | insert=INS_EMPTY_GOURD | 1 | no water in the gourd (125) |
| S7-B5 | 09_dialogue_composition | left=P_DK_OFFER, right=P_GM_SEATED_CALM; bg SKY_NOON + FAR_VILLAGE + MID_ROAD_HOUSE | 1 | Damodarpant offers (126) |
| S7-B6 | 07_character_reaction | face=F_GM_LAUGH | 1 | he laughs (127) |
| S7-B7 | 09_dialogue_composition | left=PAIR_BA_DK_STAND, right=P_GM_SPEAKING; bg SKY_NOON + FAR_VILLAGE + MID_ROAD_HOUSE | 2 | one Brahman; worldly conduct (128-131) |
| S7-B8 | 04_character_entrance | char=P_DK_WALK_TO_HOUSE (walks away to the door), other=PAIR_BA_DK_STAND; bg SKY_NOON + FAR_VILLAGE + MID_ROAD_HOUSE | 1 | fortune blessed; Damodarpant goes in (132-133) |

**S8** (6 shots)

| Beat | Preset | Roles -> image ids | Shots | Covers (ovi) |
|---|---|---|---|---|
| S8-B1 | 02_environmental_parallax | sky/far/mid = SKY_NOON + FAR_VILLAGE + MID_WELL_TROUGH, near=FG_NEEM | 1 | trough beside the well (134) |
| S8-B2 | 03_slow_cinematic_push | img=BEAT_S8_GM_DRINKS | 1 | drinks, belches (135) |
| S8-B3 | 04_character_entrance | char=P_DK_WALK_GADVA, other=P_GM_SEATED_CALM; bg SKY_NOON + FAR_VILLAGE + MID_WELL_TROUGH | 1 | Pant arrives with the gadva (135) |
| S8-B4 | 07_character_reaction | face=F_DK_ALARM | 1 | 'do not drink that' (136) |
| S8-B5 | 10_object_hand_insert | insert=INS_TROUGH_WATER | 1 | muddy water fit for animals (136) |
| S8-B6 | 10_object_hand_insert | insert=INS_GADVA_VETIVER | 1 | sweet, clear, cool, vetiver (137) |

**S9** (11 shots)

| Beat | Preset | Roles -> image ids | Shots | Covers (ovi) |
|---|---|---|---|---|
| S9-B1 | 09_dialogue_composition | left=P_DK_HOLD_GADVA, right=P_GM_SPEAKING; bg SKY_NOON + FAR_VILLAGE + MID_WELL_TROUGH | 2 | 'no worldly tales' (138) |
| S9-B2 | 08_emotional_closeup | face=F_GM_CALM | 1 | all pervaded by Brahman (139) |
| S9-B3 | 10_object_hand_insert | insert=INS_TROUGH_WATER (reuse) | 1 | muddy or clear (139-140) |
| S9-B4 | 10_object_hand_insert | insert=INS_GADVA_VETIVER (reuse) | 1 | scent and stench, its forms (140) |
| S9-B5 | 02_environmental_parallax | SKY_NOON + FAR_VILLAGE + MID_WELL_TROUGH, near=FG_NEEM, + char layer P_GM_SPEAKING | 1 | the drinker not apart (141) |
| S9-B6 | 07_character_reaction | face=F_GM_LOOK_UP | 1 | you dropped that (142) |
| S9-B7 | 09_dialogue_composition | left=PAIR_BA_DK_STAND, right=P_GM_SPEAKING; bg SKY_NOON + FAR_VILLAGE + MID_WELL_TROUGH | 1 | reflect on the origin (142) |
| S9-B8 | 05_bowing_prayer | pose=POSE_READY_TO_FALL; bg well layers | 1 | ready to fall at his feet (143) |
| S9-B9 | 04_character_entrance | char=P_GM_RUN (exits screen-left), other=PAIR_BA_DK_STAND; bg SKY_NOON + FAR_VILLAGE + MID_WELL_TROUGH | 1 | runs like the wind (144) |
| S9-B10 | 02_environmental_parallax | SKY_NOON + FAR_VILLAGE + MID_WELL_TROUGH, near=FG_NEEM (empty, no figures) | 1 | no one can stop him (144) |

**Shots each image serves** (from the table above): `FAR_VILLAGE` 31, `MID_ROAD_HOUSE` 23, `SKY_MORNING` 20, `SKY_NOON` 14, `FG_NEEM` 8, `MID_WELL_TROUGH` 8, `P_GM_SEATED_CALM` 6, `PAIR_BA_DK_STAND` 6, `P_GM_SPEAKING` 6, `P_BA_TALK` 5, `P_DK_LISTEN` 5, `F_GM_CALM` 4, `P_GM_PICKING` 4, `FX_SUN` 3, `MID_SHEGAON` 2, `BEAT_S3_TWO_MEN_SEE` 2, `P_BA_ASK` 2, `P_GM_LOOK_UP` 2, `F_GM_LOOK_UP` 2, `P_GM_EATING` 2, `INS_MIXING` 2, `INS_TROUGH_WATER` 2, `INS_GADVA_VETIVER` 2, `P_DK_HOLD_GADVA` 2, `INS_FEAST_PREP` 1, `INS_LEAF_PLATES` 1, `INS_CHILIM_GOURD` 1, `INS_PICK_GRAIN` 1, `PAIR_BA_DK_WALK` 1, `F_BA_AMAZED` 1, `POSE_SILENT_BOW` 1, `P_DV_CARRY_PLATE` 1, `INS_PLATE_SET` 1, `F_BA_REVERENT` 1, `BEAT_S7_BIRDS` 1, `INS_EMPTY_GOURD` 1, `P_DK_OFFER` 1, `F_GM_LAUGH` 1, `P_DK_WALK_TO_HOUSE` 1, `BEAT_S8_GM_DRINKS` 1, `P_DK_WALK_GADVA` 1, `F_DK_ALARM` 1, `POSE_READY_TO_FALL` 1, `P_GM_RUN` 1.

All of the above is DRAFT, NOT APPROVED. The owner approves the looks (section d) before any image is made.
