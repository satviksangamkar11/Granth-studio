# Image prompt and review rules, every Adhyay (from the Adhyay 1 lessons; sources: `CODEX_IMAGE_LESSONS.md`, checked by Opus and Claude, 2026-10-27)

> **SUPERSEDED 2026-11-01 (owner):** image generation and correction now use ONLY the final system in `docs/pilot/FLOW_IMAGE_SYSTEM.md` (jobs from `scripts/flow/build_jobs_v2.py`, review by `scripts/flow/review_shot.py`, downloads only via `scripts/flow/download_queue.py` after the owner's OK). Its prompt template and review rubric are now built into `build_jobs_v2.py` and `review_shot.py`.


Owner approves story facts, reference sheets and final images. Claude builds versioned jobs from data. Flow agents generate and file candidates. A PASS belongs to ONE exact image version.

## 1. What went wrong in Adhyay 1 (so we do not repeat it)
- Character drift, mostly Maharaj (tank top, wrong vest, child look): the first cue was imprecise ("short dark hair, worn grey-white vest"). Fix: a precise per-chapter character block in series data, and the accepted sheet attached.
- Story notes and bracketed narration leaked into the picture prompt. Fix: build the prompt only from the shot's `on_screen` facts.
- Corrective sentences stacked on the original prompt and sometimes contradicted it. Fix: rewrite the whole prompt for a regeneration, do not append.
- Wrong or too many chips attached (three style chips by habit, a neighbouring shot, a character only mentioned). Fix: attach only visible characters, one place, one style anchor, one central prop; one exact search match per chip, verified by name.
- Five jobs had no place chip. Fix: the job builder refuses a job without a place.
- Download faults: first click does nothing, edit-then-rename returned the old image, two agents mis-filed one image. Fix: exact-title filing (fail closed), download immediately after an edit, one download folder per agent.
- Watermark: small star on all, large on 17; cleaner calibration is per chapter data.
- Provenance holes: the recorded prompt hash was the catalog prompt, the model came from an environment value, the edit id was per shot not per chosen version. Fix: record actual prompt, model read from the screen, references and edit id per version.
- Review mistakes: hand side flagged (S7_05, S7_06, S9_01) although the script does not say which hand; PASS at v01 later REGENERATE (identity, vest, place jump); a gaze direction (S9_11) read wrongly once. Fix: the rubric below.

## 2. Prompt template (filled by code from data; never hand-written per shot)
```
STYLE: [approved style anchor text]. Match [anchor image].
CHARACTERS: Exactly [N] people. [Name]: [age/build, face, hair, clothes, screen position] ... (visible people only; blocks come from series character data for THIS chapter's state)
PLACE AND PROP: [accepted place id + fixed features]. [story prop and its exact state]
ACTION: one visible action and one gaze target per person.
CAMERA: framing, angle, screen-left/right, subject size, what fills the foreground, link to previous/next shot.
PRESET SLOT: [preset id; full frame or separate layers; crop-safe area; room for the camera move/caption]
LIGHT: [approved scene light]
EXCLUDE: no extra people, text, letters, inset, border, modern objects.
REFERENCES: visible character chips, one place, one style anchor, prop if central; at most 1-2 neighbouring shots for a specific continuity fix.
```
A hand side is optional unless the approved shot or the adjoining cut requires it. English prompts are fine. Use 2K, x1 by default (x2 only for a hard shot and when the daily limit allows; fallback Nano Banana 2.1 x1). Seeds are not recorded; do not rely on them.

## 3. Review rubric (answer in order, with shot id + version)
1. Is this the intended file, version, actual prompt and shot contract?
2. Exactly the required people, each once, right face, age, clothes? Zoom every face, torso, partial figure.
3. Required action and gaze direction? Look at previous and next shots beside it.
4. Story prop, place, light, cut position right? Put the character/place/prop sheet beside it.
5. Fits its preset input and crop (insert at native size and at the display crop)?
6. At native size: letters, inset, watermark residue, cleanup damage?
BLOCKER = wrong person, story fact, critical prop, action, direction, place jump, unusable composition, visible text, material mark. A harmless detail the source does not specify is ADVISORY: fix the prompt, do not regenerate. Record PASS / BLOCK / ADVISORY / UNSURE with the crop used. UNSURE goes to a second reviewer or the owner, never a silent pass or reject.
Who: Claude checks every image and the cut to its neighbours (full size). The owner approves the set from a contact sheet plus an exceptions list (batch, not per image). Codex only for disputes or changed images after a failed review (the owner said no more Codex for the finals). The first three images of each new scene are reviewed before the batch continues. Edit-first for a local defect; review the WHOLE image after an edit.

## 4. Automatic gates (no image model)
Exists: `file_flow_download.py` (complete JPEG, 2752x1536, fresh, no overwrite), `audit_flow_outputs.py`, `wm_clean_v2.py` (pixels outside the mask unchanged), `build_image_binding.py` (sha256). To build: provenance record per version, exact id/count check, duplicate sha256, perceptual near-duplicate WARNING, crop-safe geometry from preset data, watermark-mask contrast warning. Face count, identity, garment, gaze, text and watermark residue over dark art stay human checks (a detector may nominate crops, never decide).
