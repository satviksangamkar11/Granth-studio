# FLOW RUNBOOK: how Claude operated Google Flow (built-in browser) for GranthStudio, step by step (written 2026-10-27 so a small agent, e.g. Haiku, can repeat it)

Recorded from the real run for Adhyay 1 reference sheets. Everything below WORKED on the real project. Project: `GranthStudio`, id `31b2d7e8-5ad8-41ba-a878-50860b49a03e`, URL base `https://flow.google.com/project/<id>`. Account is signed in by the OWNER (never type a password; stop at any CAPTCHA/verify screen). Tools: the Claude built-in browser (`mcp__Claude_Browser__*`): `navigate`, `computer` (actions: `left_click` with `ref` or `coordinate`, `type`, `key`, `wait` max 10 s, `scroll`, `screenshot`), `find` (returns a `ref_N`), `read_page` (filter `interactive`), `browser_batch` (runs a list of actions in one call: USE IT). Screenshot coordinate frame is 800x638; `scale` 0.5 screenshots are enough. Prefer `ref` clicks (the page layout moves) and the fixed coordinates listed here only where marked "fixed".

## 0. Rules (do not break)
1. Only paste the prompt text exactly as in `canon/drafts/A1_image_catalog_v2_DRAFT.json` (field `prompt`; for sheets with attachments see `references`). Never rephrase, never add story content.
2. Model: Nano Banana Pro, 16:9, outputs x1 (the model chip at the bottom right of the prompt box shows `Nano Banana Pro  x1`; if it shows x2 click it and pick x1). Credits shown: 0.
3. ALWAYS download at 2K ("2K Upscaled"), never 1K, never 4K (4K needs an upgrade).
4. Save into the structure: `D:\aai work\flow_outputs\adhyay_NN\references\` (sheets), `...\shots\`, `...\layers\`, `...\rejected\`; names `<ID>__candidate_vNN__2K_source.jpg` + `<ID>__candidate_vNN.png`; after the owner accepts: `<ID>__vNN__accepted.png`. One log line per file in `adhyay_NN\flow_log.jsonl` (done by `file_flow_download.py`, section 5). Never overwrite.
5. Do not delete anything in Flow. Do not click Upgrade/Buy. Do not click "+" twice at the same spot (the second click lands on a list row and attaches it). Do not cross-check steps that are confirmed here: only check the result image.
6. Waiting: `wait` at most 10 s per call; generation takes about 30-60 s.

## 1. Attach reference images to the prompt box (verified, deterministic)
1. `navigate` to the project URL, `wait 5`.
2. `find` query `Add ingredients to the prompt box` -> a ref (it was `ref_157`; it can change per page load, but stays the same within one page load).
3. `left_click` that ref (it is the "+" at the bottom-left of the prompt box). A full-screen picker opens: search box at the top (fixed click at (400, 95)).
4. `wait 3`, `left_click` (400, 95), `type` the asset name (see names below), `wait 2`. The single matching row appears at about (100, 140).
5. `left_click` (100, 140) -> the image is attached (thumbnail appears in the prompt box); the picker closes.
6. Repeat 3-5 for each reference. Attachments persist while the page is not reloaded (the setting "Clear prompt on submit" is OFF, so after a generation both text and attachments stay).
Asset search names: style refs `ref_temple`, `ref_pot`, `ref_figures`; a sheet generated earlier is searched by its Flow auto-name, e.g. `Storybook illustration prop` (leaf plates sheet), `Devotional storybook illustratio` (gadva sheet), `Devidas character turnaround`, `Damodarpant Kulkarni character`, `Man turnaround sheet` (Maharaj / Bankatlal / 2nd Damodarpant sheets: several rows: look at the thumbnails). Characters are listed first when the picker is on "All".
To remove a wrong attachment: hover its thumbnail, a circled x appears at its centre, click it (this only removes it from the prompt).

## 2. Type the prompt and generate
1. Click into the text area (fixed, about (300, 534) when 0-3 thumbnails are shown; if the box has grown, click at (300, 420)).
2. If old text is present: `key ctrl+a`.
3. `type` the whole prompt (about 2,100-2,500 characters is fine in one call).
4. Click the round arrow (fixed (680, 580)) to submit. A grey tile with a percentage appears at the top of the grid. `wait` until it disappears (30-60 s; do 3-5 waits of 10 s, or generate the next one meanwhile).
5. The prompt box stays as it was: for the next sheet only change the attachments you need and replace the text.

## 3. Open a result and download it at 2K (VERIFIED; do not improvise these coordinates)
Fixed coordinates in the 800x638 frame. ALWAYS put `wait 2` between the three menu clicks (a click made before a menu has opened can hit "Move to trash" or another tile: this happened once; if a toast says "1 item moved to trash", click Undo at once).
1. The newest tile is first in the grid (top-left). After generating, press `Escape` (collapses the prompt box), `left_click` (100, 125), `wait 5`. The URL becomes `.../edit/<edit id>`: note the id.
2. `left_click` (677, 38) [three-dot menu], `wait 2`.
3. `left_click` (590, 164) ["Download media"], `wait 2`. A small size menu opens at its left: 1K Original / 2K Upscaled / 4K (Upgrade).
4. `left_click` (350, 236) ["2K Upscaled"]. `wait 10`, `wait 10` (the 2K upscale takes 15-30 s).
5. The file lands in `C:/Users/Satvik/Downloads/<guid>.tmp` (a COMPLETE JPEG 2752x1536; the browser keeps the temporary name). The NEWEST `.tmp` (`ls -t`) is the one, but only if it is NEWER than your click: the filing script (section 5) refuses a file identical to an already filed one or older than 5 minutes. If it refuses, wait 10 s and run it again.

## 4. Save a character in Flow (verified)
1. `navigate` to `<project url>/character` -> this opens the "New character" page.
2. `find` `Add from project` -> click its ref (it was `ref_53`). A picker opens listing IMAGES (newest first). Click the row of the sheet (one click adds it AND opens the character editor, no "Add media" button on this path).
3. `read_page` interactive: in the editor the refs were stable: `ref_70` Edit name, `ref_72` Character personality (info) box, `ref_68` Done editing.
4. One batch: `left_click ref_70`, `key ctrl+a`, `type <NAME>_v01`, `key Return`, `left_click ref_72`, `type <one-line identity>`, `left_click ref_68`, `wait 3`. Leave "Select a voice" empty. The character appears in Characters and All media (tile with the name).
Names/info used: `GM_v01`, `BA_v01`, `DK_v01`, `DV_v01` (identity lines in `docs/pilot/DECISION_LOG.md` and in the catalog identity paragraphs).

## 5. File the download (script in the repo: `scripts/flow/file_flow_download.py`)
`PYTHONIOENCODING=utf-8 python scripts/flow/file_flow_download.py "<tmp path>" <IMAGE_ID> <vNN> "edit/<edit id>" "<refs joined by |>" "<notes>" [references|shots|layers]` (default folder `references`; use `shots` or `layers` for those). It checks the file is a complete JPEG of 2752x1536, refuses to overwrite, refuses a file identical to an already filed one or older than 5 minutes, writes the 2K JPG + PNG copy, hashes both and appends the log line.

## 6. Order for Adhyay 1 reference sheets (done = [x])
[x] CH_GM (Maharaj 4 views + gourd + chilim + seated; owner supplied references) [x] PR_GADVA_VETIVER [x] PR_LEAF_PLATES [x] CH_BA [x] CH_DK (2 candidates) [x] CH_DV [x] characters GM_v01, BA_v01, DK_v01, DV_v01 saved; [x] LOC_SHEGAON_REF [x] LOC_ROAD_REF [x] LOC_WELL_REF (the well had the road sheet attached). All 2K-filed, candidates until the owner accepts. Head sheets (CH_*_HEAD) and a separate gourd sheet were skipped: the 4-5 view sheets already contain the faces and the props.

## 7. Pitfalls met (and the fix)
- Clicking "Add from project" while a picker was loading attached a style image to a new character: wait 3 s, take one screenshot, then click a row.
- A coordinate click on the character page's bottom buttons hit the model dropdown (layout differs): use `find` + `ref` click there.
- `@name` typed in the prompt does not open an autocomplete in this pane: attach with "+" instead.
- The downloads appear as `.tmp`: not an error.
- A new Flow tile may be named by Flow ("Man turnaround sheet illustration"): identify by thumbnail/time, then note the `edit/<id>` in the log.
- The pane is small: clicks at fixed coordinates are only valid in the 800x638 frame; if a screenshot shows a different frame (e.g. 800x404) use refs.

## 8. Make a SHOT image with saved characters (the "@" method) - TESTED 3/3 (identity held)
Saved Flow Characters are attached from the same "+" picker (characters are listed first; search by name `GM_v01`, `BA_v01`, `DK_v01`, `DV_v01`): this is the working equivalent of typing @name (typing @ in this pane shows no menu). Do NOT attach the 14 reference sheets: the characters carry the look.
1. `navigate` to the project URL (reloading clears old attachments), `wait 6`, `find` "Add ingredients to the prompt box" -> ref.
2. For each character in the shot, then the PLACE sheet (search `Village road` / `Cattle drinking` / `Village`), then optionally one style image (`ref_temple`): the 7-action sequence of section 1 (click ref, wait 3, click (400,95), type name, wait 2, click (100,140), wait 2). One batch holds at most 25 actions = 3 attachments; use two batches.
3. Click the text area (300, 534), `type` the SHORT shot prompt (template below), click the arrow (680, 580), `wait` 4 x 10 s, then section 3 (open, 2K download), then section 5 (file with `shots`).
Short prompt template (about 1,100-1,250 characters; used in the tests): `Flat-colour 2D Indian devotional storybook illustration: clean dark navy-ink contour lines of steady medium weight, flat colour fills with a few fine hatch lines, warm earth palette, a FULL richly drawn frame with foreground, midground and background filled in. Use the attached characters exactly as in their reference sheets: <NAME_v01 (one-line costume cue)>, ... same faces, costumes, proportions. Setting: the attached <place>. <the shot sentence from the catalog: framing, who stands where, pose, gaze, screen geography>. Light: <light block of the scene>. Full-frame 16:9 landscape picture, edge to edge, no border. No text, no letters, no modern objects, no halo.`
Tests (files in `flow_outputs/adhyay_01/shots/`): TEST_chip_S2_03 (GM_v01 seated on the road), TEST_chip_S3_01 (BA_v01 + DK_v01 walking), TEST_chip_S4_03 (GM + BA + DK over-the-shoulder). All three kept the faces, costumes and proportions of the sheets and the house/door/leaf plates of the road sheet.
SAFETY FILTER: the first attempt (Maharaj, wording "bare ... loincloth") returned "Failed: This generation might violate our policies ... You have not been charged". Wording that passed: describe him as "the calm young ascetic ... worn grey-white vest" and do not write "loincloth/bare/almost naked" in the shot prompt (the character sheet still draws the loincloth). If a prompt fails: do NOT keep retrying; reword that one phrase once, log both attempts, and stop if it fails again.

## 9. Extra pitfalls (found later)
- Never run the filing script right after clicking 2K without waiting: it once filed the PREVIOUS download under a new name (fixed: the script now refuses identical or stale files).
- An accidental "Move to trash" has an Undo toast for a few seconds; the image URL still opens afterwards. Check that the tile is still in All media.
- Generation sometimes shows two tiles (a failed one with the red "Failed" card and a good one): open the one with a title, not the failed card.
- Flow names new tiles itself ("Two men walking on road"): the edit id in the URL is the stable handle; log it.

## 10. NAMING and the progress file (owner rule: generated images carry their catalog id)
- In Flow: after opening the new tile, click the title at (160, 38), `ctrl+a`, type `<catalog id>__vNN` (e.g. `SH_S3_01__v01`, `CH_DK__v01`), `Return`. Verified: the new title persists after a page reload. This is how the owner can ask for a download later ("download SH_S3_01").
- On disk: `<ID>__candidate_vNN__2K_source.jpg` + `<ID>__candidate_vNN.png` (same id, done by `scripts/flow/file_flow_download.py`).
- Job list for the 59 shots: `canon/drafts/A1_flow_shot_jobs.json` (built by `scripts/flow/build_shot_jobs.py`); progress is appended to `D:\aai work\flow_outputs\adhyay_01\shots_progress.jsonl` (status DONE / NEEDS_REVIEW / FAILED / DOWNLOAD_FAILED). A DOWNLOAD_FAILED image is still in Flow under its catalog title: to recover, the owner (or Claude) opens it by title and downloads 2K.
- Test image already renamed in Flow: `TEST_chip_S3_01_two_friends__v01`.

## 11. FINAL SAVING PASS (owner rule 2026-10-27: saving is done at the end, not per image)
1. Generation phase: attach with `@` (type `@`, click the menu search box, type the name, click the first row -> a NAMED chip), submit, wait, open the new tile, rename it `<catalog id>__vNN`, log status `GENERATED`. No downloads.
2. Final pass (after all shots are GENERATED): for each GENERATED job open its tile (search the title in the project search box), `More options` -> `Download media` -> `2K Upscaled`, wait 20 s, then `scripts/flow/file_flow_download.py` with the newest `.tmp` (it refuses stale/duplicate files), then append a progress line with status `DONE`. Use element refs (`read_page` interactive) for the menu items, not fixed coordinates: the pane size changes after a restart.
3. Lessons (verified 2026-10-27): after `navigate` call `read_page` before using refs; a new tile can have an auto name until renamed; the tile's hover card lists the chips that were attached (use it to verify `@` worked); "Failed" cards with "not charged" can appear: just resubmit once.

## 12. THE EXACT @ METHOD, as Claude did it by hand (2026-10-27, examples SH_S2_07 and SH_S2_08; use this, it supersedes the "+" picker steps for characters/places/styles)
Pane size changes after a restart, so: after EVERY `navigate` call `read_page` (interactive) first; refs differ per page type (home page: text box `ref_14`, submit `ref_17`; edit page: title is the FIRST "Editable text", the box "What do you want to change?" is a DIFFERENT ref: NEVER type a title into it, Return would start an edit generation). Frame 800x675.
A. Navigate to `https://flow.google.com/project/<id>`, `wait 7`, `read_page`, `left_click ref_14` (text box).
B. For each reference (characters first, then the place sheet, then `ref_temple`, `ref_pot`, `ref_figures`): `type "@"`, `wait 3` (a full-screen asset menu opens), `left_click (400, 100)` (its search box), `type <name>` (`GM_v01`, `BA_v01`, `DK_v01`, `DV_v01`, `Village road`, `Cattle drinking`, `ref_temple`, `ref_pot`, `ref_figures`), `wait 2`, `left_click (100, 146)` (the only row). A NAMED chip appears in the prompt box (verify once with a screenshot: labels under the thumbnails). Max 25 actions per batch: 3 references per batch.
C. `type` the prompt text (the job prompt, starting with a space after the last chip). Model chip must read `Nano Banana Pro` and `x1`; if not, click it and fix.
D. `left_click ref_17` (Start generation). `wait 10` x4. (If a grey "Failed ... not charged" card appears next to the result, ignore it or resubmit once.)
E. Open the result: `navigate` to the project again, `wait 7`, `read_page`; the newest tile is first. A single click only shows a hover card: click the image TWICE (second click about (400, 200)) until the URL becomes `.../edit/<id>`; `read_page`; the title is the first "Editable text" ref.
F. Rename: `left_click <title ref>`, `ctrl+a`, `type <flow_title>`, `Return`, `wait 2`, screenshot to confirm the header shows the new title and the picture is the right one (a wrong tile was opened once: always check the header title and the picture before typing).
G. Log the progress line (status GENERATED, edit id from the URL). No download now (owner rule); the final pass downloads.
Results: SH_S2_07 (one character small on the road) and SH_S2_08 (close insert with gourd and chilim) both matched the character and place sheets.

## 13. AFTER EVERY PC RESTART (the built-in browser forgets the login AND the settings)
1. The owner signs in to Google in the pane (never type a password). Project URL: `https://flow.google.com/project/<id>`.
2. Settings reset to `Nano Banana 2.1  x2`. Fix them: `read_page`, `left_click` the "Settings trigger" ref (it was `ref_16`, bottom-right of the prompt box). A popover opens: keep Image + 16:9; click `x1` at about (401, 519); click the model dropdown at about (515, 478): the model becomes `Nano Banana Pro` (check the chip in the prompt box reads `Nano Banana Pro  x1`, and "Generating will use 0 credits"). `Escape` closes it.
3. Check once with a screenshot before generating. If the chip is not Pro x1, fix it again.

## 14. MULTI-AGENT AUTOMATION (2026-10-27): who does what
- Claude writes job files in `canon/drafts/` (shot jobs, regen jobs, edit jobs with previous/next shot images) and the agent brief `HAIKU_FLOW_AGENT_BRIEF.md` (UPDATE 1-16) + `FIX_PASS_BRIEF_UPDATE16.md`. Haiku agents (effort low) run Flow in the built-in browser: one agent per tab (`tabs_create`, pass its tab id on every call). Claude watches the first 2-3 results, then leaves them; reads each agent's final report and VIEWS the pictures (never trust the agent's PASS alone).
- Per shot: attach with @ (type @, wait 4, click search (400,100), type name, wait 3, screenshot: ONE row, click (100,146)); chips = job characters + place sheet + ref_temple/ref_pot/ref_figures; model chip Nano Banana Pro x1 (or 2.1 x1 when Pro is at its limit); submit arrow ~(695,621); wait 60-90 s; reload the project and read the newest tiles; open the tile (click twice), rename to `<ID>__vNN`; download 2K (menu (677,38), Download media (590,164), 2K (350,236), wait 18 s; the FIRST attempt after a page load often does nothing: repeat once); the file lands in `D:\aai work\flow_outputs\<title>_2K_<time>.jpg`; `bash scripts/flow/file_regen.sh <ID> <vNN> <edit id>` files it (jpg+png, log line); append the progress line.
- Failure modes met: usage limit (Pro), silent no-submit (reload and look), wrong tile picked from a search with several rows, tab id renamed, stray clicks opening character/edit pages, Maharaj tank-top drift.

## 15. EDIT-FIRST (tested on SH_S2_08)
On the tile's edit page set the model chip (click chip (595,620), dropdown (508,527), row 2.1 or Pro, click an empty margin (25,350) to close the popover), click the box (372,572), type 'Change only <defect>. Keep everything else exactly the same: <pose, props, background, style>.', screenshot, click the arrow (695,625), wait 30 s. The page keeps the same URL and shows the edited image; download 2K and file as the NEXT version number. Edit for local defects, regenerate for identity/age/framing.

## 16. REVIEW LOOP
Contact sheets (`scripts/flow/build_final_manifest.py` -> `flow_outputs/adhyay_NN/final_review/sheet_N.jpg`), Codex per sheet (`codex exec --sandbox read-only --skip-git-repo-check -C <dir> -i sheet_N.jpg -o CODEX_CHUNK_N.md - < chunk_prompt`), merge into `FINAL_LIST_A1.md` (A real defects / B minor / C story questions), fix pass with edit jobs, rebuild pack, Codex again on the changed shots. Local audit: `scripts/flow/audit_flow_outputs.py` (read-only) writes `final_review/AUDIT_LOCAL.md`.

## 17. EDIT DOWNLOAD PITFALL (found 2026-10-27, SH_S5_03)
After an edit, DOWNLOAD IMMEDIATELY while the edited image is on screen (wait ~30 s after the arrow, close the edit box with its X, then menu (677,38) -> Download media -> 2K). Renaming the tile or clicking the Done-editing check BEFORE the download made Flow download the OLD image (byte-identical to the previous version: the filing script then refuses it as 'identical'). Rename the tile after the download. Always compare the new download's hash/size with the previous version before filing.

## 18. CLEAN IMAGES (after the final set exists)
`python scripts/image_trials/wm_clean_v2.py --src <adhyay>/final --out <adhyay>/_wm_v2` then copy to `final_clean/` and check: (a) changes only inside the bottom-right 340 px, (b) before/after corner sheets viewed, (c) Haiku corner check, (d) numeric test (star contrast ~30 -> ~1.5). Two sparkles exist: small on every shot (always repainted), big on some (list `BIG_ON` in the script; decide by eye + contrast, automatic detection fails over dark art). Textured art uses a cloned patch (`CLONE_FOR`).

