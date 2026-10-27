# Codex: READ-ONLY final review of the 59 Adhyay 1 shot images (end check)

You are Codex, a READ-ONLY reviewer. Do not edit, move, rename, delete or generate any file, and do not operate Google Flow. The ONLY file you may create is the report `D:\aai work\flow_outputs\adhyay_01\final_review\CODEX_FINAL_REVIEW.md`. Goal: state whether these images are FINAL and need no regeneration, or list exactly which shots still need regeneration.

## What to read
- Manifest (best version of every shot, with the prompt used, attached characters and place): `D:\aai work\flow_outputs\adhyay_01\final_review\final_manifest.json`; contact sheets `sheet_1.jpg` ... `sheet_7.jpg` in the same folder (9 shots each, labelled); full-size files are the `file` paths in the manifest (2752x1536 PNG).
- Truth for looks: accepted reference sheets in `D:\aai work\flow_outputs\adhyay_01\references\` (CH_GM__v03__accepted.png = Maharaj; CH_BA__candidate_v01 = Bankatlal; CH_DK__candidate_v01 = Damodarpant; CH_DV__candidate_v01 = Devidas; LOC_ROAD_REF, LOC_WELL_REF, LOC_SHEGAON_REF; PR_GADVA_VETIVER, PR_LEAF_PLATES). Style target: `D:\aai work\granthstudio\assets\pilot_refs\style_v2\`. Story text: `D:\aai work\granthstudio\docs\pilot\A1_full_script_simple.md`. Earlier reviews to compare against (do not trust them blindly): `FINAL_CHECK_A1.md`, `IMAGE_REVIEW_A1.md`, `REGENERATE_LIST_A1.md`.

## Check every one of the 59 shots (open the full-size file for any doubtful shot)
1. CHARACTER CONSISTENCY: Maharaj = slim adult youth, cropped short dark hair, narrow face, OPEN frayed grey-white vest over the chest, SHORT white cloth at the hips, legs bare below the knee (FAIL: grey sleeveless tank top/undershirt, shirt, long trousers, boyish round face, long hair, bare-chested with no vest). Bankatlal = cream turban, sage-green coat, cream shoulder cloth. Damodarpant = terracotta-red turban, white shirt, white dhoti, slightly taller. Devidas = shaved head with small tuft, red tilak, shoulders uncovered, white dhoti. Same faces/ages across all scenes.
2. HEAD-COUNT AND POSITIONS as the prompt states (no duplicates, no extras, none missing); poses/gaze/who-faces-whom as the prompt says.
3. PLACE CONTINUITY: same house, door, step, leaf plates, neem tree, road; same well, trough, cattle, village in S8-S9.
4. STYLE: flat colour, navy-ink outlines, full frame (no empty plain backgrounds), warm palette; no text/letters, no modern objects, no halo, no inset or border; no extra limbs, melted faces or cropped heads. IGNORE the small Flow sparkle watermark at lower right (accepted by the owner).
5. SHOT-TO-SHOT: consecutive shots of a scene cut together without a visible jump in look; light and time of day per scene (S9 high noon).
6. PROP/STORY ACCURACY: the key prop in the prompt is visible (leaf plates, gourd/gadva, vetiver roots, cattle, well).
7. FILE: every file exists, 2752x1536, not a duplicate of another shot.

## Report format (write the file and paste it in chat)
A. One row per shot (all 59): `shot_id | version | verdict PASS or REGENERATE | defects | severity`.
B. Final line, exactly one of: `END CHECK: NO REGENERATION NEEDED` or `END CHECK: REGENERATION NEEDED FOR: <shot ids>`.
C. If regeneration is needed: for each shot, the exact sentence to add to the prompt, characters to attach/drop, place sheet, new title. Filter-safe wording only (never "loincloth", "bare", "naked"; say "short white cloth wrapped at the hips, legs uncovered from above the knee down").
D. Systemic problems and any other issue you notice (style, consistency across scenes, anything that would hurt the film). Do not guess: if an image cannot be viewed say UNSURE and why.
