# Adhyay 1 image lessons — proposed `CODEX_IMAGE_LESSONS.md`

## 1. Summary

1. All 59 shot images were filed, but 33 shots needed a version after v01; SH_S9_11 reached v06.
2. Maharaj’s age, face and clothing drift caused the most repeated work. The original job cue said only “short dark hair, worn grey-white vest.”
3. Composition and continuity failed even when characters looked right: people faced the wrong way, props changed, and nearby shots showed different places.
4. Review missed real defects and also demanded three hand-side corrections that the story did not require.
5. The final list records 57 Codex passes and two images checked only by Claude. Filing metadata needs repair before it can reliably prove which prompt, model and Flow tile produced each version.

**Counting note:** Categories below overlap. They count distinct shots or logged events, not every generation attempt. The headline in [IMAGE_REVIEW_A1.md](<D:/aai work/flow_outputs/adhyay_01/IMAGE_REVIEW_A1.md>) says 43 PASS, 5 REGENERATE and 9 DOWNLOAD_FAILED, while its updated 59-row table contains **46 PASS, 11 REGENERATE and 2 UNSURE**. Use the rows and versioned records, not that headline.

## 2. Problem table

| Problem | How often, from the records | Cause and what happened | Permanent fix |
|---|---:|---|---|
| Maharaj identity and garment drift | Eight tank-top shots listed in `FINAL_CHECK_A1.md`; later checks also caught SH_S2_08 and SH_S5_01. SH_S9_02, SH_S9_08 and SH_S9_10 had boyish or wrong-cloth versions. | A saved character chip and the short original description did not hold an open vest, short hip cloth, adult build and flat face style. Edits and regenerations fixed selected versions. | Put the full accepted-sheet identity in **every** Maharaj job; compare face, open vest and cloth against `CH_GM__v03__accepted.png` at full size. |
| Bankatlal, Damodarpant and Devidas drift | Duplicate Damodarpant in SH_S4_03 and SH_S9_11; modern shirt in SH_S5_01; giver confused with Maharaj in SH_S5_03. | Several characters, similar pale clothes and crowded views made roles ambiguous. | Give each person one position, costume cue and visible action. Count each named person; inspect hands and partial bodies. |
| Extra, merged or missing people | Four confirmed extra-person shots: SH_S4_03, SH_S7_04, SH_S7_07 and SH_S9_11; SH_S8_03 was flagged as a possible fourth-person frame. SH_S5_03 merged two roles visually. No confirmed missing-person count. | Story notes mentioned people outside the intended frame; generation also invented bystanders. Some early checks counted only prominent faces. | Derive attachments from `on_screen`; state the **exact visible people** and positions. Review the entire frame, including background and cropped limbs. |
| Gaze, direction and pose | SH_S3_03 repeatedly faced camera rather than each other; SH_S9_11 v03–v05 looked right after Maharaj exited left. SH_S9_06 had the wrong camera side. | “Talking” and “looking after him” did not specify screen direction or camera position clearly enough. | State “camera behind…,” “faces toward screen-left,” and the prior shot’s exit direction; check the adjoining shot beside it. |
| Place and cut continuity | At least nine shot findings across SH_S2_05, SH_S5_03/05/06, SH_S6_01, SH_S7_04/07, SH_S8_04 and SH_S9_04. | Place sheets were sometimes absent; a close crop changed a doorway, road, well or background. | Attach the accepted place sheet and, when needed, one **correct** neighbouring shot; check house, ground, positions and light across the cut. |
| Props and story facts | At least five material prop cases: meal/plate in SH_S5_05/06, broken gourd in SH_S7_02, roots/gadva in SH_S9_03, pot in SH_S9_10. | Prompts mixed story facts with invented detail; edits could remove a defect and the needed prop together. | Use a short prop-state ledger per beat: intact/empty gourd; stitched-leaf plate and meal; brass gadva and roots. Check the source script before treating a detail as canon. |
| Style and age shading | At least five review findings involving SH_S2_08, SH_S4_04, SH_S5_01/06 and SH_S9_04. | Flat navy-ink style refs competed with character and scene instructions; edits sometimes softened faces or backgrounds. | Use one approved style anchor, then compare full-size face and background with the sheet. Treat visible realism or child/adult jumps as blockers. |
| Framing, inserts and preset fit | At least seven cited shots: SH_S3_03, SH_S4_03, SH_S5_06, SH_S9_03/06/09/11. | “Close insert,” “over shoulder” and “single frame” were underspecified; the animation preset’s required input was not always checked. | Specify camera, subject size, foreground edges and safe crop. Confirm the selected preset can use that full image or needs separate layers/figures. |
| Repeated regeneration | 33 of 59 final shots use v02 or later; 17 use v03 or later; six use v04 or later. SH_S9_11 reached v06. | Defects were fixed one at a time, and later changes introduced new ones. | Prefer a bounded local edit when composition is sound; compare **all** acceptance questions after each edit. Stop and escalate after the attempt cap. |
| Watermarks and cleanup | Small sparkle on all 59; large sparkle on 17. The later corner check found 49 clean, nine smudged and one residual star, SH_S8_04. | The first cleaner covered only the small mark; automatic detection struggles over dark art and clone patches can smear lines. | Reuse the masked-pixel assertion, but recalibrate templates per Adhyay and inspect every doubtful corner at native size. Do not call cleanup complete from a contact sheet alone. |
| Text or letters inside art | No confirmed letter defect in the reviewed final shots; five regen prompts were called out for stray parenthetical story notes. | Notes such as “who can stop the wind” were mixed into visual instructions and could be drawn literally. | Remove narration and bracketed commentary before submission; keep “no text or letters” and inspect likely sign, wall and sky areas. |
| Flow, filing and agent faults | Three `DOWNLOAD_FAILED` progress entries, one usage-limit stop, one confirmed cross-agent misfile, one wrong chip caught before submission, a trash/restore event and 91 loose root downloads in `AUDIT_LOCAL.md`. | UI state, tabs, search rows, model settings and download timing changed. Two agents shared a download area. | One tab per agent; exact chip and tile checks; file by the download’s title and edit ID; download an edit before renaming; fail closed on stale or duplicate bytes. |

Sources: [FLOW_RUNBOOK.md](<D:/aai work/granthstudio/docs/pilot/FLOW_RUNBOOK.md>), [HANDOFF.md §9](<D:/aai work/granthstudio/docs/pilot/HANDOFF.md>), [AUDIT_LOCAL.md](<D:/aai work/flow_outputs/adhyay_01/final_review/AUDIT_LOCAL.md>), [HAIKU_CORNER_CHECK.md](<D:/aai work/flow_outputs/adhyay_01/final_clean/HAIKU_CORNER_CHECK.md>) and the `CODEX_CHUNK_*`, `CODEX_FINAL_*`, `CODEX_R2_*` reviews in `final_review/`.

## 3. Prompting style for Adhyay 2+

The original 59 Flow jobs average about **1,182 characters**; 31 regen jobs average **1,708**. Length alone is not the proven failure. The costly pattern was stacking an imprecise character cue, scene prose, three style chips and then corrective sentences that sometimes contradicted the original. Five jobs had no place chip. The jobs record no seeds, so seed advice is unsupported. English prompts worked; the language issue was stray story commentary, not English itself. Pro x1 worked until its limit; Pro x2 offered choices but used capacity twice as fast, after which the approved fallback was Nano Banana 2.1 x1. Neither model nor x2 guaranteed consistency. The accepted 2K download was 2752×1536.

Use this **job template**, filled from the approved shot and preset:

```text
STYLE: Flat-colour 2D Indian devotional storybook; steady dark
navy-ink outlines, light hatching, warm earth palette, richly drawn
foreground, middle and background. Match [approved style anchor].

CHARACTERS: Exactly [N] people.
[Name/accepted sheet]: [age and build, face and hair, distinctive
clothes, screen position]. [Repeat only for visible people.]
For Maharaj: slim adult youth, narrow face, cropped dark hair,
open frayed grey-white vest in two front panels, chest visible,
short white cloth at hips, legs visible below the knee.

PLACE AND PROP: [accepted place ID; fixed doorway/road/well features].
[Story-critical prop and its exact state.]

ACTION: [one visible action per person; gaze target; pose].
CAMERA: [wide/medium/insert; angle; screen-left/right; subject size;
what occupies foreground; previous-shot exit or position].
PRESET SLOT: [preset ID; required full-frame image or separate assets;
crop-safe area; space needed for camera move or later caption].
LIGHT: [approved scene light].

EXCLUDE: No extra people, text, letters, inset, border or modern objects.
REFERENCES TO ATTACH: [only visible character chips], [one accepted
place], [one approved style anchor], [central prop if needed].
Add one correct neighbouring shot only for a specific continuity fix.
```

Attach chips by **one exact search match** and verify their visible names before submitting. Do not attach all three style images by habit, a wrong neighbouring image, or a character merely mentioned in narration. Keep the 2K setting and record the actual model, count, prompt and references used for that version. Use x1 by default; use x2 when a difficult shot benefits from choosing between alternatives and the usage limit allows it. The successful local edit of SH_S2_08 supports edit-first for a garment detail; its later background-blur edit shows why the entire image still needs review. See [A1_flow_shot_jobs.json](<D:/aai work/granthstudio/canon/drafts/A1_flow_shot_jobs.json>), [A1_flow_regen_jobs.json](<D:/aai work/granthstudio/canon/drafts/A1_flow_regen_jobs.json>) and [A1_flow_edit_jobs.json](<D:/aai work/granthstudio/canon/drafts/A1_flow_edit_jobs.json>).

## 4. Review errors and a tighter rubric

**False positives or overcalls.** Codex flagged the left hand in SH_S7_05, SH_S7_06 and SH_S9_01 because the catalog said “right.” [STORY_CHECK_GROUP_C.md](<D:/aai work/flow_outputs/adhyay_01/STORY_CHECK_GROUP_C.md>) found that the checked script does **not** specify a hand. Unless an approved direction or cut requires it, amend the prompt; do not regenerate solely for that choice. SH_S2_04 and SH_S3_05 were initially UNSURE and later kept after a closer look: uncertainty was appropriate, but should not become a rejection by default. A complaint that the SH_S7_02 gourd’s emptiness was not visibly readable needs an owner story-clarity decision; the source says empty, not broken. The nine reported cleanup smudges are inspection candidates, not nine proven blockers.

**False negatives.** Fourteen v01 images marked PASS in the updated first table were later marked REGENERATE at the *same version* in `CODEX_CHUNK_*`. Three of those were the unsupported hand-side calls; the other eleven include real-looking misses such as SH_S2_08’s closed vest, SH_S4_04’s changed face, SH_S5_01’s child appearance, SH_S7_02’s broken gourd and SH_S8_04’s place jump. Haiku’s quick “full colour, no text” checks similarly let framing and identity faults through. For SH_S9_11 v04, Codex repeatedly identified a rightward gaze against a leftward dust trail; the progress note says Claude confirmed it on a crop. I opened v04 and v06: v04 looks right and v06 looks left. Codex was right there.

**Rubric: answer in order, with shot ID and version.**

1. Is this the intended file, version, actual prompt and approved shot contract?
2. Are exactly the required people present, each once, with correct face, age and clothes? Zoom every face, torso and partial figure.
3. Does each person perform the required visible action and look in the required direction? Put prior and next shots beside it.
4. Are the story prop, place, light and cut positions correct? Show the character, place and prop sheets beside the full-size image.
5. Does the image fit its preset input and crop? Check an insert at native size and at the intended display crop.
6. At native size, are there letters, inset frames, watermark residue or cleanup damage?

A **blocker** is a wrong person, story fact, critical prop, action, direction, place jump, unusable preset composition, visible text, or material mark. A harmless hand choice or tiny non-story variation is **advisory** unless the approved shot contract requires it. Haiku checks chips and obvious failures; Claude checks every generated image and neighbouring cut; Codex reviews the versioned pack independently. A second full-size reviewer is needed for uncertainty, disputed facts, close faces/hands/props and every changed image after a failed review. Record PASS, BLOCK, ADVISORY or UNSURE with the exact crop and reference used.

## 5. Checks to automate without an image model

- **Reuse now:** `file_flow_download.py` checks complete JPEG, 2752×1536, freshness, overwrite and identical bytes; `audit_flow_outputs.py` checks planned files, pairs, sizes and log coverage; `wm_clean_v2.py` asserts pixels outside its mask stay unchanged; `build_image_binding.py` hashes clean images.
- **Build a provenance gate:** bind each accepted **shot + version + source SHA-256 + Flow edit ID + actual prompt SHA-256 + model + chip list**. Currently `file_flow_download.py` hashes the *catalog* prompt even for regenerated or edited images, while its recorded model can come from an environment value. The log labels later 2.1 work as Pro. `build_final_manifest.py` puts the original job prompt beside the highest version, and `build_final_set.py` takes the latest edit ID per shot rather than per chosen version. Those are review hazards, not proof of the actual generation inputs.
- **Build deterministic gates:** exact expected IDs and counts; PNG/JPEG decode and dimensions; allowed native 2752×1536 ratio (do not reject it for differing slightly from mathematical 16:9); accepted-hash verification; duplicate SHA-256; perceptual near-duplicate **warning**; crop-safe geometry from preset metadata; known watermark-mask change and contrast warnings.
- **Keep human checks:** face count, character identity, garment, gaze, text and watermark residue over dark art cannot be made reliable binary gates here without an image model. A simple detector or OCR can nominate crops, but must not silently PASS or reject a shot. The A1-specific watermark templates and 17-image big-star list require fresh calibration for A2.

## 6. Next Adhyay checklist

| # | Item | Who | Owner decision? | Done-test |
|---:|---|---|---|---|
| 1 | Approve story facts and shot list | Owner | Yes | Signed shot IDs and source refs |
| 2 | Approve recurring and new character sheets | Owner | Yes | Named, hashed sheets |
| 3 | Approve place and critical prop states | Owner | Yes | One reference per state |
| 4 | Check each shot’s visible-person list | Claude | No | Count and positions recorded |
| 5 | Check preset input and crop space | Claude | Exception only | Every shot has a feasible slot |
| 6 | Generate concise versioned jobs | Claude | No | No story notes or contradictions |
| 7 | Verify actual prompt and reference hashes | Claude | No | Bound to each job version |
| 8 | Verify account, model, x1 and 16:9 | Flow agent | No | Settings captured before first shot and after restart |
| 9 | Verify each `@` chip search | Flow agent | No | One exact matching row and correct chip list |
| 10 | Review first three images of each new scene | Claude | No | Full-size checks passed before batch continues |
| 11 | Inspect every result before choosing | Flow agent | No | Failures noted, attempt cap respected |
| 12 | Rename tile and record edit ID | Flow agent | No | Title, image and URL agree |
| 13 | Download and file at 2K | Flow agent | No | Fresh titled file; JPEG/PNG pair and hashes |
| 14 | Check full image and adjoining cut | Claude | No | Six rubric answers recorded |
| 15 | Review sheets, then doubtful native crops | Codex | No | Version-specific verdicts |
| 16 | Resolve story or direction disputes | Owner | Yes | Contract or verdict amended |
| 17 | Edit a local defect, then recheck all six questions | Flow agent/Claude | No | New version accepted or marked UNSURE |
| 18 | Explicitly select final version | Owner | Yes | Version, edit ID and SHA-256 bound |
| 19 | Check clean corners and source-to-clean hashes | Claude | Residue only | Full-size check; masked changes only |
| 20 | Accept the final contact set | Owner | Yes | Every ID reviewed; exceptions listed |

## 7. Proposed full text for `docs/pilot/IMAGE_PROMPT_RULES.md`

```markdown
# Image prompt rules — every Adhyay

The owner approves the story facts, reference sheets and final images.
Claude builds versioned jobs. Flow agents generate and file candidates.
Codex reviews read-only. A PASS belongs to one exact image version.

Before prompting, record the shot ID, source fact, visible people and
their positions, critical prop state, place, camera direction and
animation preset input. Do not put narration or bracketed story notes
in the visual prompt. A hand side is optional unless the approved shot
or adjoining cut requires it.

Use the approved flat-colour, navy-ink style anchor. Attach only the
visible character chips, one accepted place image, and a central prop
reference when needed. For a continuity repair, attach at most one or
two correct neighbouring shots. Check that each @ search has one exact
match and that the named chips are visible before submission.

For Maharaj, require the accepted slim adult face and cropped hair,
an open frayed grey-white vest in two front panels with chest visible,
and a short white cloth at the hips with legs visible below the knee.
Compare him with CH_GM__v03__accepted.png at full size. Keep Bankatlal's
cream turban and sage coat, Damodarpant's terracotta turban and plain
white clothes, and Devidas's accepted sheet features.

State the exact number of people, one action and gaze target per
person, screen direction, framing and subject size. Preserve the
approved house, road, well and props between neighbouring shots.
Specify one full-frame image; no inset, letters or modern objects.
Leave safe room for the chosen preset's camera move or caption.

Use the approved model at x1 by default, download 2K, and keep every
version. After a local edit, download while the edited result is on
screen, before renaming. Bind the actual prompt, model, references,
Flow edit ID and source hash to that version. Never select the highest
version automatically: select the reviewed version explicitly.

Review every image at full size against the shot, accepted sheets,
previous and next shots, and preset crop. Count all people, inspect
faces, clothing, hands, props, letters and both watermark corners.
Fix only demonstrated blockers. Send uncertain story choices and
visible cleanup damage to the owner. Final approval is the owner's.
```

This analysis was read-only; no file was created or changed.