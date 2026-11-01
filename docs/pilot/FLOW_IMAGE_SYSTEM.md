# Flow image system v2 — the ONE fixed system for every Adhyay (owner 2026-11-01)

**STATUS: FINAL — this is the official image-generation and image-correction system for every Adhyay (owner 2026-11-01). Every other image brief is superseded. Change it only with the owner's OK and log the change in `DECISION_LOG.md`.**

Current settings: model **Nano Banana 2.1** (only; no fallback), count **x2**, 16:9; Haiku agents at effort **HIGH**; Codex `gpt-6.1-sol` effort **medium**, read-only; one agent per scene in parallel, each in its own browser tab; no downloads until the owner's OK.

Replaces the scattered `HAIKU_FLOW_AGENT_BRIEF.md` updates 1-17 and `FIX_PASS_BRIEF_UPDATE16.md` for all new work. Keeps what worked on 27 Oct (saved Flow characters with `@`, edit-first, neighbour shots, exact-title filing) and fixes what `CODEX_IMAGE_LESSONS.md` found. Owner rules (2026-11-01): one model only, always x2, Haiku AND Codex review, Haiku decides, **no download until the end**, no flow-mcp.

## Two separate phases
**Phase 1 — make and review (no downloads at all).** Haiku agents (effort HIGH), one per scene in parallel, each in its own browser tab, generates x2 per submit, takes a screenshot of each new image, Codex + Haiku review both, Haiku keeps one (renames the tile, queues it) or fixes and resubmits.
**Phase 2 — download (only the kept images, once, at the end).** When every job is DONE, Claude tells the owner **OK**, opens each queued tile and clicks 2K Upscaled; the owner clicks **Save** on each prompt; `download_queue.py collect` files every saved image by its exact title and checks it.

## Who does what
| Step | Who | Tool |
|---|---|---|
| Shot spec (people, place, action, light, film order) | Claude, owner approves | `canon/drafts/A<N>_image_spec_*.json` |
| Series data (characters + strict sheet sentences, places, style chip, model, forbidden words) | Claude, owner approves sheets | `config/flow_series.json` |
| Jobs (prompt, chips, next free version, previous/next shot) | script | `python scripts/flow/build_jobs_v2.py --adhyay N --spec <spec> --out canon/drafts/A<N>_flow_jobs_v2.json` |
| Generate / edit, screenshot, rename, queue | Haiku agents, effort HIGH, one per scene, own tab each | this brief |
| Review of both x2 images in ONE call | Codex `gpt-6.1-sol` medium, read-only | `python scripts/flow/review_shot.py --jobs <jobs> --shot <ID> --candidate <A> <B>` |
| Second review + decision (keep / edit / regenerate) | Haiku agent | this brief |
| Check of every kept image beside its neighbours | Claude | the `__neighbours.jpg` sheets |
| Download pass | Claude clicks 2K, owner clicks Save | `python scripts/flow/download_queue.py status|collect --adhyay N` |
| Final approval of the set | owner | contact sheet + exceptions |

## Parallel agents (owner 2026-11-01)
- Split the job list by scene: one Haiku agent per scene group (e.g. A = S2, B = S7), each told its shot ids and its OWN tab id (`preview_start` with the project URL opens a new tab). Pass that `tabId` on EVERY browser call; never touch another agent's tab or shots.
- All agents share one Flow project: new tiles of the other agent appear at the top of the grid. Identify YOUR tiles only by the edit id in the URL and the title; before reviewing or renaming, check the picture matches your shot (people, place).
- Attach a chip only after the `@` search shows ONE exact row. The progress file and the download queue are append-only: one line at a time.
- A shot is finished only when the progress file has a `DONE` line with that job's exact `flow_title`; older versions' lines (e.g. `BLOCKED_BY_REVIEW`) never count.
- Claude can change a running agent's rules by message (model, prompt fix, stuck rule); the agent re-reads its job before each submit.

## Settings (before the first job and after every PC restart)
- Account `sangeetasangamkar@gmail.com`; project `https://flow.google.com/project/31b2d7e8-5ad8-41ba-a878-50860b49a03e`.
- Model chip = `config/flow_series.json` -> `model.name` exactly, count **x2**, 16:9; credits shown must be 0. After a restart Flow resets the chip (it showed `Nano Banana 2.1 x2`): fix it (FLOW_RUNBOOK section 13). Usage limit reached: STOP and report (never switch model).

## Phase 1, per job (read the job again from the jobs file before each job; read this brief once)
1. **Look first, once per job.** Read with the Read tool: `previous_shot.file`, `next_shot.file` and every file in `sheets`. Write one line: what the new picture must continue from and cut into.
2. **Attach chips** (`@` method, FLOW_RUNBOOK section 12): exactly the job's `chips` in order (characters, place, story props such as the leaf-plate sheet, then ONE style chip). Each search must show ONE exact row before you click. Screenshot (scale 0.5): the chip names under the thumbnails = `chips`; model chip = `model.name x2`.
3. **Paste the job `prompt` exactly** (for an `edit` job: open `.../edit/<base_edit_id>` and type the `edit_instruction` instead). Submit ONCE. Wait about 60 s; if no new tile, reload and look before submitting again.
4. **Open each of the two new tiles** (click twice until the URL has `/edit/`). On its page `read_page` and `zoom` on the picture area (full image, nothing else): the zoom image is saved as a file (its path is printed in the result) — that file is the candidate. Note both edit ids. Do NOT download.
5. **Codex review (one call for both):** `python scripts/flow/review_shot.py --jobs <jobs> --shot <ID> --candidate <A file> <B file>` (several minutes; run it and wait). It prints A/B answers, `CHOICE` and the sheet path.
6. **Your review (Haiku):** Read the sheet `<A>__neighbours.jpg` (PREVIOUS | A | B | NEXT + reference sheets). For each of A and B answer Q1 people, Q2 action/gaze, Q3 place/props, Q4 continuity with PREVIOUS and NEXT, Q5 style/framing, Q6 nothing invented, in one line each.
7. **Decide — and if both are not good, FIX IN A LOOP until one passes (the 27 Oct fix-pass method, owner 2026-11-01):**
   - Codex PASS for one and you agree -> keep it (step 8).
   - Both not good (Codex BLOCK on both, or you see a blocker Codex missed) -> fix, review again (steps 4-7), repeat:
     a. **Edit first** when the review says `FIX: edit` (one local defect in a good picture): open that tile's edit page, type the review's `EDIT_INSTRUCTION`. The edit result is reviewed like a new candidate (one candidate).
     b. **Edit failed once** -> try the edit ONCE more with a sharper instruction AND attach the neighbours (see c).
     c. **Neighbour chips** (for continuity, place or prop jumps — Q3/Q4 BLOCK — and for the second try of anything): attach the job's `neighbour_chips` (accepted neighbouring shots) with `@`: type the exact title, attach ONLY if the search shows that exact title as ONE row (an edited final may keep an older tile title: if there is no exact row, skip that chip); add the job's `neighbour_sentence` to the prompt/instruction.
     d. **Regenerate** when the review says `FIX: regenerate` (wrong person, identity, age, framing, pose) or after the edits failed: submit again (x2) with the job prompt + the latest review's `REGEN_SENTENCE` (replace the previous added sentence, never stack sentences) + neighbour chips/sentence from the second regeneration on.
     e. Keep looping. Every new image gets BOTH reviews. The loop ends when an image passes both reviews.
   - **Stuck rule:** if the SAME question fails for the SAME reason on 2 submits in a row, or the failure cannot be fixed by retrying (the two neighbours disagree with each other; the attached place sheet's framing always wins over the prompt's framing), stop that shot, mark `NEEDS_REVIEW` with that reason and go on: Claude fixes the job (prompt, chips, rule), then the shot is resumed.
   - Safety stop: `attempt_cap` (8) submits/edits per shot (Flow's daily limit). Only then keep the closest, mark `NEEDS_REVIEW` with the failed questions and the attempts, and go to the next job; Claude takes it from there.
   - Codex says UNSURE, or you and Codex still disagree after one more look at the full-size image -> mark `NEEDS_REVIEW`, go to the next job.
8. **Keep:** rename the kept tile to `flow_title` (title = the FIRST "Editable text" on the edit page; NEVER type into "What do you want to change?"). Queue it:
   `python scripts/flow/download_queue.py add --adhyay N --shot <ID> --version <file_version> --edit-id <id> --jobs <jobs> --model "<model chip text>"`
9. **Progress line** (append to `D:\aai work\flow_outputs\adhyay_<NN>\shots_progress.jsonl`): `{"shot_id","status":"DONE"|"NEEDS_REVIEW"|"FAILED","flow_title","edit_id","attempts","codex":"<CHOICE>","haiku":"<one line>","time","notes"}`. DONE only when both reviews pass. The file is filed later (phase 2).

## Phase 2 — download pass (only after the owner's OK)
1. `python scripts/flow/download_queue.py status --adhyay N` lists PENDING tiles with their edit URLs.
2. For each: open the URL, menu -> Download media -> **2K Upscaled** (the first attempt after a page load often does nothing: repeat once); the owner clicks **Save**. Flow names the file `<flow_title>_<hash>_2K.jpg` in `C:\Users\Satvik\Downloads`.
3. `python scripts/flow/download_queue.py collect --adhyay N` files every saved image by EXACT title (never by time), via `file_flow_download.py` (checks 2752x1536, refuses duplicates, logs the actual prompt hash, chips, model). Repeat until `0 pending`.

## Mistakes to avoid (from CODEX_IMAGE_LESSONS.md, FLOW_RUNBOOK sections 7, 9, 17, HANDOFF section 8)
| Mistake seen in Adhyay 1 | Rule now |
|---|---|
| Weak Maharaj cue -> tank top, child face, long trousers (33 of 59 needed redos) | Every prompt carries the strict accepted-sheet sentence (built from `config/flow_series.json`); Q1 checks it |
| Three style chips by habit; wrong or extra chips; a neighbouring tile attached by mistake | Attach exactly `chips` (ONE style chip); one exact search row; screenshot the chip list before submit |
| Story notes and brackets drawn into the picture; corrective sentences contradicting the prompt | Paste the job prompt exactly; append a review's REGEN_SENTENCE once, never stack fixes |
| People facing the wrong way, place jumps, props appearing/disappearing between cuts | Q4 continuity against PREVIOUS and NEXT on the sheet, for every candidate |
| Haiku "full colour, no text" passes that missed real defects | Two reviews (Codex + Haiku), six questions each, fail closed |
| Codex hand-side overcalls | A hand side is not a blocker unless the prompt requires it |
| Duplicate Damodarpant, extra tiny people, merged roles | Exact head-count in the prompt; Q1 counts partial and distant figures |
| Edit downloaded the OLD image (rename/Done clicked first) | No downloads in phase 1; phase 2 downloads from the kept tile's own edit URL |
| Filing the previous download under a new name; two agents mis-filing | Filing only by exact title in phase 2; filer refuses identical bytes and wrong size |
| Log recorded the catalog prompt and a wrong model | Filer logs the job's actual prompt hash, chips and the model chip text |
| Wrong tile opened from a search with several rows | Identify tiles by edit id; check the header title and the picture before renaming |
| "Failed ... not charged" card next to a result | Open the tile with an image, ignore the failed card; resubmit only if no image came |
| Accidental "Move to trash" | Never click near trash; if the toast appears click Undo at once and report |
| Safety filter blocked "loincloth", "bare", "naked" | Forbidden words are refused when jobs are built |
| Settings reset after restart (2.1 x2) | Check the model chip before the first job and after any restart |

## Token plan (least tokens, no shortcut)
- Haiku at HIGH effort (owner 2026-11-01: quality first); read this brief once; per job re-read only that job's entry.
- `read_page`/`find` for navigation; screenshots at scale 0.5 except the one `zoom` capture per candidate.
- `browser_batch` for click sequences (at most 25 actions per batch).
- ONE Codex call per submit for both images (not two); every question still answered for each image.
- Haiku reads ONE sheet per submit (neighbours, both candidates and references together) instead of five separate images.
- Claude checks the kept images from their sheets at the end of a scene, not every attempt.
- No downloads in phase 1 (saves the download/filing/retry cycles of 27 Oct).

## For a new Adhyay
1. Add new characters/places to `config/flow_series.json` (strict sentence + accepted sheet); make and accept their sheets first.
2. Write the shot spec (`slot_order` + shots) from the approved shot list.
3. Build jobs, run phase 1, then phase 2 after the owner's OK. Scripts take `--adhyay N`; folders are created as needed.
