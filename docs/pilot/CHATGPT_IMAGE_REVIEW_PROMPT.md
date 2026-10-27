# Prompt for ChatGPT: review all 59 Adhyay 1 shot images and make a REGENERATE list

Copy everything below the line into the ChatGPT app (Codex / desktop with file access). You are a reviewer. The ONLY thing you may change is: download missing images as described in "Download while you check" at the end (owner's instruction). Do not edit, delete, rename or generate anything else. Do not open Google Flow's Trash, Share, Upgrade or any edit box.

---

## Task
Review every shot image of Adhyay 1 (motion-comic film "Shri Gajanan Vijay") for (1) consistency across all 59 shots and (2) match to its own prompt. Judge each image PASS / REGENERATE / UNSURE and give a regenerate list with a short fix for each.

## Where things are
- Images (2K PNG + JPG source): `D:\aai work\flow_outputs\adhyay_01\shots\` named `SH_Sx_yy__candidate_v01__2K_source.png`. Log of every filed file: `D:\aai work\flow_outputs\adhyay_01\flow_log.jsonl`. If a shot has no file there, it is not downloaded yet: open it in the Flow project by its TITLE (`SH_Sx_yy__v01`), project `https://flow.google.com/project/31b2d7e8-5ad8-41ba-a878-50860b49a03e` (account sangeetasangamkar@gmail.com; look only, never type in boxes).
- Edit ids / status per shot: `D:\aai work\flow_outputs\adhyay_01\shots_progress.jsonl` (use the LAST line per shot_id; SH_S4_03, SH_S7_04, SH_S9_11 are already flagged NEEDS_REVIEW by the operator).
- The exact prompt used for each shot: `D:\aai work\granthstudio\canon\drafts\A1_flow_shot_jobs.json` (field `prompt`; also `characters`, `place_search`). The fuller story intent (framing, who stands where): `D:\aai work\granthstudio\canon\drafts\A1_image_catalog_v2_DRAFT.json` (kind `shot_image`) and the scene text `D:\aai work\granthstudio\docs\pilot\A1_full_script_simple.md`.
- Reference sheets (the truth for faces/costumes), 2K: `D:\aai work\flow_outputs\adhyay_01\references\` : CH_GM v03 (Gajanan Maharaj, young ascetic: short dark hair, worn grey-white vest, waist cloth), CH_BA v01 (Bankatlal: cream turban, sage-green coat, cream shoulder cloth), CH_DK v01 (Damodarpant: terracotta-red turban, white shirt, white dhoti, slightly taller), CH_DV v01 (Devidas: shaved head with small tuft, red tilak, bare shoulders, white dhoti), PR_GADVA_VETIVER, PR_LEAF_PLATES, LOC_ROAD_REF, LOC_WELL_REF, LOC_SHEGAON_REF.
- Style target: the owner's three reference clips/stills in `D:\aai work\granthstudio\assets\pilot_refs\style_v2\` (flat-colour 2D Indian devotional storybook, navy ink contours, warm earth palette, FULL richly drawn frame, no text, no modern objects, no halo).

## How the images were made (so you can judge fairly)
Google Flow, model Nano Banana Pro x1, 16:9. Per shot, saved Flow Characters were attached with @ chips (GM_v01, BA_v01, DK_v01, DV_v01 as needed), then the place sheet (Village road / Cattle drinking / Village landscape) and three style images (ref_temple, ref_pot, ref_figures), then the short prompt from the jobs file. Prompts say "Show only the attached characters and no other people", so extra people are a defect. Three operators-flagged shots: SH_S4_03 (Damodarpant drawn twice), SH_S7_04 (two extra men), SH_S9_11 (three figures instead of two).

## Check each of the 59 images for
1. CHARACTER CONSISTENCY: same face, hair, costume, colours and proportions as the sheet (GM vest + waist cloth; BA cream turban/sage coat; DK terracotta turban, taller; DV shaved head, tilak). Same character must not change age, build or clothing between shots or scenes.
2. HEAD-COUNT AND WHO IS WHERE: exactly the characters named in the prompt (no duplicates, no extra villagers, none missing); positions, gaze and pose as the prompt says; left/right continuity between neighbouring shots of one scene.
3. PLACE CONTINUITY: the same house, doorway, leaf plates, road, neem tree, well/trough across the shots of one place; time of day / light as the scene's Light line.
4. STYLE: matches the reference style; full frame, no empty plain background, no text/letters, no modern objects, no halo, no watermark; no cropped heads or hands; no extra limbs or melted faces.
5. PROP/STORY ACCURACY: the key prop in the prompt is visible (leaf plates, gadva/gourd, cattle, well, grains etc.).
6. FILM USE: would two consecutive shots cut together without a visible jump in look?

## Output (write it as ONE markdown file `D:\aai work\flow_outputs\adhyay_01\IMAGE_REVIEW_A1.md`, and also paste it in chat)
A. Table, one row per shot (all 59): `shot_id | verdict (PASS/REGENERATE/UNSURE) | defects (short) | severity (high/med/low)`.
B. REGENERATE LIST, most severe first: `shot_id | what is wrong | exact fix to add to the prompt (one sentence) | attach changes (e.g. drop DV_v01, add place sheet)`. Keep the fix wording safe for Flow's filter (never "loincloth", "bare", "naked"; say "young ascetic", "vest").
C. Cross-scene consistency notes: any character drifting between scenes, and any shot pair that will not cut together.
D. Systemic issues (for example one character repeatedly drawn too old) and a suggested prompt/reference change that would fix many shots at once.
Do not guess when an image is not viewable: mark UNSURE and say why. Do not invent shots; there are exactly 59 (S1 2, S2 8, S3 6, S4 5, S5 7, S6 6, S7 9, S8 5, S9 11).

## Download while you check (owner's instruction)
For every shot with NO file in `shots\` (check `flow_log.jsonl`; all shots from SH_S2_08 onward are probably missing), download it at 2K yourself while reviewing it:
1. Open `https://flow.google.com/project/31b2d7e8-5ad8-41ba-a878-50860b49a03e/edit/<edit id>` (ids are in `shots_progress.jsonl`; last line per shot), or find the tile by its title `SH_Sx_yy__v01`.
2. Confirm the title in the header, review the picture, then top-right three-dot menu -> Download media -> **2K Upscaled** (2752x1536). Never pick 1K/original. Wait until the file appears in `C:\Users\Satvik\Downloads\` (the browser may leave a complete JPEG as `<guid>.tmp`).
3. File it with the script (it checks size, freshness, duplicates):
   `cd "D:\aai work" && PYTHONIOENCODING=utf-8 python "D:\aai work\granthstudio\scripts\flow\file_flow_download.py" "<newest Downloads file>" <shot_id> v01 "edit/<edit id>" "<characters>|<place>|ref_temple" "chatgpt review download" shots`
   If it refuses as identical/stale, wait 10 s and retry once; if it fails again write DOWNLOAD_FAILED in the table and move on.
4. Never click Move to trash / Delete / Share / Upgrade; never type in "What do you want to change?"; on a sign-in, CAPTCHA or payment page stop and tell the owner.
Add a `file` column to table A (the filed path or DOWNLOAD_FAILED).
