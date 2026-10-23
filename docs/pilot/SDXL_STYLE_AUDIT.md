# SDXL style-consistency audit (2026-10-23): why the images do not look like frozen style v1

Scope: the Scene 1 runs at commits 84b4ce17 (with/without reference) and 15afa0d1 (8-image reference-free sweep), plus the provisional character sheets from c9ee672b. No GPU was used for this audit; everything below was read from the saved evidence. Nothing is validated; human review is NOT_DONE. The frozen style v1 file was not edited.

Evidence: `docs/evidence/sdxl_style_audit/` (labeled contact sheets, the graph ComfyUI actually executed, read from the PNG metadata, the sweep receipt, sha256 of all 8 sweep PNGs). The full-size sweep PNGs stay in `D:\kaggle_upload\out_sweep\sdxl_vis_s1_kf_evidence\outputs\` (hashes in `sweep_png_sha256.txt`).

## 1. What ComfyUI actually received (read from the saved PNGs, not from the YAML)

All 8 sweep images: identical positive and negative text, no IP-Adapter or LoadImage nodes; KSampler dpmpp_2m / karras / 30 steps; seeds 1408754645..48; cfg 6.5 (images 1-4) and 9.0 (images 5-8).

Positive (1613 characters, 360 CLIP tokens):

> 1950s vintage Indian devotional book illustration, authentic mid-century opaque gouache and egg tempera painting on aged matte ivory cardstock, soft hand-painted sepia contour linework, chalky matte gouache wash shading, flat hand-brushed tonal planes, **Characters: Shri Gajanan Maharaj. Location: The road in front of Devidas's house. Props: Clay chilam, Gourd water vessel, Used leaf plates. Lighting: day_outdoor.** Shri Gajanan Maharaj: a young man in the prime of youth with a radiant complexion, strong upper arms and neck and a broad chest, wearing only an old worn vest, seated calmly with a steady, inward gaze at the tip of the nose, shown seated and framed from the waist up. The road in front of Devidas's house: a village road in front of a house, midday sun, used leaf plates on the ground **(the rest of the setting is an artistic interpretation)**. **Source detail:** He picks leftover grains of rice from the leaf plates and puts them in his mouth. **Source detail:** Gajanan Maharaj sits on the road in front of Devidas's house among the thrown leaf plates. **Artistic interpretation:** Shown seated and framed from the waist up, a modest composition. **Source detail:** His gaze rests steadily on the tip of his nose and his expression is calm. **Source detail:** He wears an old vest of worn cloth; he has a gourd for drinking water and a hand-made clay chilam in his hand warm natural mineral pigments of raw sienna, burnt umber, warm ochre, terracotta, and muted sage green, subtle paper grain texture, vintage double-line paper border mount, clean traditional graphic composition, text-free, no labels, no watermarks.

Negative (56 tokens): exactly the frozen `negative_style`.

Composition check: the prefix and suffix are byte-exact, in the right order, once each; nothing truncated, nothing overridden. `positive_style.combined` is not used (the runner composes prefix + description + suffix; the two agree). So the frozen TEXT was delivered correctly. The problems are around it.

## 2. Root causes, most important first

| # | Cause | Evidence | Effect |
|---|---|---|---|
| 1 | **The reference image is not in the frozen style, and it is applied twice.** The only reference is the Gemini picture: a modern clean-ink, flat-colour digital illustration (the opposite of "heavy black comic ink / digital painting gloss" in the frozen negative). The harness imports it as BOTH the Maharaj character reference and the location reference; the graph applies it in two IPAdapterAdvanced nodes, each weight 0.6, linear, start 0 to end 1. | `scene1_reference_effect_labeled.png`; graph nodes 21/22/31/32 | IP-Adapter Plus copies style as well as content. With about 1.2 combined weight for every step it overrides the text: the Scene 1 keyframe is a copy of the Gemini look. Same seed without the reference gives a sepia photograph instead. |
| 2 | **The scene description is pipeline metadata, not a picture description.** It carries internal labels and codes ("Lighting: day_outdoor", "Source detail:", "Artistic interpretation:", "(the rest of the setting is an artistic interpretation)"), repeats itself (seated/waist-up twice, nose-tip gaze twice, the road three times), and is about 290 tokens long. | prompt above | Noise words compete with the style words; nothing in it describes the PAINTING, only provenance. |
| 3 | **The frozen suffix lands alone in the last chunk.** SDXL's text encoders read 75 tokens at a time; ComfyUI splits this prompt into 5 chunks and concatenates them. Chunk 1 = style prefix + "shri gajanan maharaj" + location; chunks 2-4 = the description; chunk 5 = the entire suffix (pigments, paper grain, double-line border, text-free). | token split in section 4 | The palette, paper, border and "text-free" instructions are the weakest part of the conditioning. Consistent with what we see: no double-line border in any image, stray pseudo-signatures in 5 of 8 images. |
| 4 | **The saint's name pulls SDXL toward old photographs.** "Shri Gajanan Maharaj" sits in the first, strongest chunk. SDXL has seen the well-known historical photographs; together with "vintage" and "sepia" it produces an elderly man in an albumen photograph. "photorealistic" and "modern photography" in the negative do not exclude an OLD photograph. | 3 of 8 sweep images are sepia photographs of an elderly bearded man; all 8 show an elderly man although the text says "a young man in the prime of youth" | Wrong medium (photo, not painting) and wrong age. The same mechanism made the reference-free character sheets look like icons ("devotional" + names + "front view"). |
| 5 | **No style anchor, so the seed decides the medium.** SDXL base with text only: the same prompt gave photograph, engraving, loose watercolour and tinted drawing depending on the seed. | sweep, columns | Even with perfect text, independent images will not be homogeneous without a shared visual anchor. |
| 6 | CFG is not the lever. | matched seeds: seed+0 is a photo at both 6.5 and 9.0; 9.0 moves seeds +1/+2 from photo/engraving toward painted, seed+3 barely changes | Raising CFG alone will not fix it. |

### Why the architecture did not prevent this

The architecture (sections 4.3, 6) locks the style **text** (sealed `content_sha256`, one style per project, no per-shot override, receipts carry the style identity). That works: the text was delivered exactly. But a style is only as consistent as **everything** that conditions the image, and three inputs were never style-locked:
- **References:** nothing requires a reference to be in the frozen style. IP-Adapter was added for identity, but it carries style too ("do not stack competing face/style adapters", section 6, is the exact risk we hit).
- **Scene description format:** the frozen template is `{prefix} {shot_description} {suffix}`, but `keyframe_request` fills the middle with research provenance instead of a short visual description, so the frozen parts are diluted and pushed to the end.
- **No visual check:** `clip_style_similarity` exists as a diagnostic name, but nothing measures generated images against an approved style example before they are used as references or keyframes.

## 3. Per-image assessment against frozen v1 (cfg / seed offset)

Criteria: (a) opaque gouache/tempera, flat hand-brushed planes; (b) soft sepia contours; (c) chalky matte, aged ivory paper, paper grain; (d) restrained sienna/umber/ochre/terracotta/sage; (e) double-line border; (f) no text; (g) subject correct (young, almost bare, seated among leaf plates).

| Image | Medium actually produced | a | b | c | d | e | f | g | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 6.5 / +0 | sepia albumen photograph | no | no | partial (mount) | sepia only | no | no (scrawl) | no (elderly) | FAIL |
| 6.5 / +1 | sepia photograph | no | no | partial | sepia only | no | yes | no | FAIL |
| 6.5 / +2 | tinted engraving / travel-book lithograph | no | yes | yes | partial | single rule | yes | no (turban, clothed) | FAIL (closest graphic line) |
| 6.5 / +3 | loose transparent watercolour | no | partial | yes | yes | no | no | no | FAIL |
| 9.0 / +0 | sepia photograph | no | no | partial | sepia only | no | no | no | FAIL |
| 9.0 / +1 | tinted sepia drawing with flat washes | partial | yes | yes | yes | no | no (seal/scrawl) | partial (bare chest, seated, grains; elderly) | CLOSEST |
| 9.0 / +2 | company-school watercolour, flat planes | partial | yes | yes | yes (ochre, sage, terracotta) | single rule | yes | no (jewellery, turban, teapot) | CLOSE (palette) |
| 9.0 / +3 | watercolour | no | partial | yes | yes | no | no | no | FAIL |

STYLE PASS: none. Best existing outputs: cfg 9.0 seed+1 (technique) and cfg 9.0 seed+2 (palette and flat planes). Both show the wrong person (elderly), so neither is usable as a character reference.

Style consistency vs identity consistency: these are different questions. The sweep was reference-free, so different faces and costumes across seeds are expected and are NOT the failure. The failure is that the painting **medium** changes across seeds (photo, engraving, watercolour, drawing).

The Gemini reference itself: clean dark ink outlines, flat bright digital colour, smooth gradients. It does not satisfy frozen v1 either (it matches the negative prompt's "heavy black comic ink / digital painting gloss"). Using it as an identity reference will always fight the frozen style.

## 4. Token split (CLIP tokenizer, 75-token chunks as ComfyUI encodes them)

1. 0-74: style prefix ... "characters : shri gajanan maharaj . location : the road in front of devidas 's house ."
2. 75-149: "props : clay chilam ... lighting : day _ outdoor . shri gajanan maharaj : a young man ..."
3. 150-224: "... ( the rest of the setting is an artistic interpretation ). source detail : ..."
4. 225-299: "... artistic interpretation : ... source detail : ..."
5. 300-359: the whole frozen suffix (pigments, paper grain, double-line border, text-free).

## 5. Can the current stack reproduce the art direction?

Partly. Reference-free images 9.0/+1 and 9.0/+2 show that SDXL base + this prompt CAN produce aged paper, sepia contours, flat washes and the mineral palette. It does not do so reliably, and the current inputs actively push it away (Gemini reference, name prior, buried suffix, noisy middle). Not proven either way until the minimum corrections below are tried.

## 6. Minimum corrections (proposed, nothing applied; the frozen style text stays untouched)

1. **Stop using the Gemini image as an IP-Adapter reference** for frozen-style generation (it is off-style), and never apply one image twice. References must themselves be owner-approved frozen-style images.
2. **Shot description = short visual prose** (target: whole prompt within about 2 chunks, at most 150 tokens): who is visible described by appearance, pose, setting, props, light in words ("bright midday sun", not "day_outdoor"). Provenance labels, artistic-interpretation notes and repeats stay in the request metadata and receipt, not in the prompt text.
3. **Describe characters, do not name them in the image prompt** (names stay in the metadata). Removes the historical-photograph prior.
4. **Then one small test**, same 8 seeds, cfg 6.5 and 9.0, reference-free, compare with this sweep. Only after the owner picks frozen-style reference images: add references back, one per character, with lower weight or a later start (identity, not style), and run Scene 1 again.
5. Only if that still fails: a style anchor (one owner-approved frozen-style image as an IP-Adapter style reference for every image) or the optional style LoRA (architecture 4.3). Both are bigger decisions for the owner.

Items 2 and 3 change how `keyframe_request` writes the scene description (a new prompt-template version). The frozen prefix/suffix/negative stay exactly as sealed.
