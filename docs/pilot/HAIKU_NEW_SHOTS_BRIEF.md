# Brief for the Haiku Flow agent (effort LOW): make 6 NEW Adhyay 1 shot images (2026-11-01)

> **SUPERSEDED 2026-11-01 (owner):** image generation and correction now use ONLY the final system in `docs/pilot/FLOW_IMAGE_SYSTEM.md` (jobs from `scripts/flow/build_jobs_v2.py`, review by `scripts/flow/review_shot.py`, downloads only via `scripts/flow/download_queue.py` after the owner's OK). This file is kept as history and for the click details it references.


You are the Haiku agent. Claude does NOT operate Flow for this job (owner order). Use ONLY your own browser tab: pass your `tabId` on every browser call. Tools: `mcp__Claude_Browser__*` and Bash (only for `ls`, the filing script, and appending to the progress file).

## Read first (once)
1. `D:\aai work\granthstudio\docs\pilot\HAIKU_FLOW_AGENT_BRIEF.md`: UPDATE 4 (method = runbook section 12 A-G), UPDATE 5, UPDATE 6 (account `sangeetasangamkar@gmail.com`), the SAFETY rule and the Hard rules. Everything there applies unchanged.
2. `D:\aai work\granthstudio\docs\pilot\FLOW_RUNBOOK.md`: sections 12 (the @ method), 13 (model chip), 3 and 17 (download pitfalls).
3. Job list: `D:\aai work\granthstudio\canon\drafts\A1_flow_new_shots_jobs.json` (6 jobs, re-read before each). Fields: `shot_id`, `flow_title` (name the tile exactly this), `characters` (attach each as an @ chip), `place_search` (attach), `prompt` (paste EXACTLY, never rephrase).
4. Progress file: `D:\aai work\flow_outputs\adhyay_01\shots_progress.jsonl` (append only). Skip any shot_id of these 6 that already has a DONE line.

## Settings (check before the first job)
Project: `https://flow.google.com/project/31b2d7e8-5ad8-41ba-a878-50860b49a03e`. The model chip must read `Nano Banana Pro  x1` (16:9). The pane currently shows `Nano Banana 2.1  x2`: fix it per runbook section 13. If Pro is at its daily limit, use `Nano Banana 2.1  x1` (never x2). Credits must stay 0.

## Per job (6 jobs, in file order)
A-C. Navigate, `read_page`, attach with @: every name in `characters`, then the place `place_search`, then `ref_temple`, `ref_pot`, `ref_figures`. Screenshot: the chip list must be EXACTLY that (no extra chip). Paste the job `prompt`, check the model chip.
D. Submit once; wait ~60 s. E. Open the new tile (click the image twice until the URL contains `/edit/`). F. Rename it to `flow_title`.
G. LOOK at the picture. It PASSES only if: exactly the people in `characters` (no others), flat-colour navy-ink style, no text, no halo, no modern objects, and, for Maharaj, the strict check of UPDATE 10 (slim adult youth, cropped hair, OPEN frayed grey-white vest, short white hip cloth, legs bare below the knee, NOT a tank top), Damodarpant terracotta turban + plain white shirt (no collar/pockets), Bankatlal cream turban + sage coat. If it fails, regenerate (same prompt, new attempt), up to 3 attempts; keep the closest and mark NEEDS_REVIEW if none passes.
H. Download at 2K: menu (677,38) -> "Download media" -> "2K Upscaled" (the size menu appears to the LEFT of the item; use `find`/`read_page` refs, the pane size changes). The browser saves it as `C:\Users\Satvik\Downloads\<title>_<hash>_2K.jpg` (or a `.tmp`). The first attempt after a page load often does nothing: check a NEW file arrived, repeat once.
I. File it: `cd "D:/aai work" && PYTHONIOENCODING=utf-8 python "D:/aai work/granthstudio/scripts/flow/file_flow_download.py" "<the newest downloaded file>" <shot_id> v01 "edit/<edit id>" "<characters joined by |>|<place_search>|ref_temple" "haiku new shot" shots` (refuses stale/duplicate files: wait 10 s and retry once). Append ONE progress line: `{"shot_id": ..., "status": "DONE" | "NEEDS_REVIEW" | "FAILED" | "DOWNLOAD_FAILED", "edit_id": ..., "file": <png path>, "flow_title": ..., "time": <iso>, "notes": <attempts; which checks failed>}`.

## Stop rules
Stop and report on: sign-in / CAPTCHA / payment / terms page, a trash toast (click Undo first), credits above 0, 3 jobs in a row FAILED. Never delete, trash, share or upgrade. Do not touch any tile that is not yours.

## Final report
Per shot: status, attempts, file path, edit id, and what you saw in the picture (people, clothes, anything odd). Claude will view every image before accepting it.
