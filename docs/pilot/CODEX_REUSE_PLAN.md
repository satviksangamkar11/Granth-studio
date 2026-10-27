The S4 run is a useful **draft**, not an approved or render-ready reusable plan.  
The 59 flat images and 11 preset recipes exist; connecting approved plans to those images is still missing.  
For S4, keep the story treatment, adapt it to the flat images first, and call Kimi only for shots that cannot be resolved from approved material.

### 1. What is reusable today

- **Preset recipes:** Eleven JSON recipes exist in [assets/v5_presets](</D:/aai work/granthstudio/assets/v5_presets/README.md>). They describe reusable camera and layer arrangements; they are not saved story-specific shot plans. Builder v2 remains frozen under D-017.
- **Images:** The 59 `SH_*.png` flat finals exist. [final_image_binding.json](</D:/aai work/granthstudio/canon/packets/adhyay_01/final_image_binding.json>) records their filenames and SHA-256 hashes. Their existence and recorded hashes do not establish owner approval or that each image fits a particular S4 shot.
- **S4 draft and evidence:** The five-shot plan, call and receipt are recorded in [REVIEW.md](</D:/aai work/granthstudio/canon/director_runs/a1_s4_kimi_one/REVIEW.md>) and [receipt.json](</D:/aai work/granthstudio/canon/director_runs/a1_s4_kimi_one/receipt.json>). One Kimi generation cost $0.0724; an advisory Nemotron review passed. `VALID` means the checks passed, **not** that the owner approved it or that it was rendered.
- **Prior rendering technique:** The handoff records a proof that changing preset JSON and asset mappings can reuse the frozen builder. It does not prove this S4 plan works with the final images.

S4 falls short of the new rule in specific ways. It declares **nine new image IDs**, with descriptions, instead of selecting the existing `SH_*` finals. Shots 1 and 2 select layered presets 01 and 02; shot 4 selects preset 08, which needs a transparent face cut-out. Those layers have not been made. Shots 3 and 5 select flat-image preset 03, but still refer to newly declared IDs, not verified `SH_*` bindings. Three staging warnings need owner decisions: S4-1 daylight, S4-2 pose, and S4-4 halo.

The current [director schema](</D:/aai work/granthstudio/scripts/source/director_test.py:71>) requires full action, pose, performance, camera, claims, staging, dialogue and `images_needed`. It requires asset IDs to be declared there and currently restricts them to a scene-specific namespace. It therefore does not implement either saved-plan lookup or the compact catalog-ID contract. The handoff says the `SH_*`-to-renderer connection is also still TODO.

### 2. Minimum design and order

First lock the relevant source, wording, measured bilingual timing and image choices with the owner. Then add a small file-based library, for example `canon/shot_plans/`, with one versioned JSON record per approved shot. No database or animation-code generator is needed.

Each record should contain: a stable plan ID and version; chapter, scene and shot ID; source/ovi and shared beat IDs; the intended visible action and held pose; preset ID and preset hash; role-to-image IDs and image hashes; transition and any approved staging; source, canon, script and timing version hashes; owner approval and date; and references to validation/render receipts. Keep approval separate from technical validation. Preserve old versions rather than overwriting them.

**Match by exact chapter + scene + shot/beat ID and approved input-version hashes first.** An exact match can be replayed without Kimi after the asset and preset hashes are checked. For a different shot or chapter, search by a small set of explicit attributes—beat purpose, required pose, framing, characters and preset roles—and present a candidate as a **template**, not an automatic match. Code checks compatibility; the owner approves the adapted record. A matching ID alone never proves that a changed story or image still fits.

For each asset role, resolve an approved catalog ID such as `SH_S4_01` through the chapter binding file, verify the actual file’s SHA-256 against the binding and the saved record, and pass that file to the renderer. Stop on missing files, mismatched hashes, incompatible roles or missing approval. A changed source, canon, timing, image or preset makes affected records require revalidation; an unchanged completed render is resumed only when its input and output receipts match.

Only unmatched shots go to Kimi. Give it the fixed shot IDs, approved shared beats, relevant catalog and preset IDs, and compatibility constraints. Its output should be **shot ID plus existing plan/preset, image-role and other allowed choice IDs**, or `NEED_NEW` with a short reason and classification: missing image or pose, supported JSON arrangement, or renderer gap. Code supplies and validates dialogue, source claims, timing and expansion. `NEED_NEW` remains unresolved until the owner decides; it is not permission to change Builder v2 or to generate an image automatically. Any new preset needs the owner’s ruling, test render and approval.

For Adhyay 2–21, repeat this against each chapter’s approved research, catalog and measured audio; carry forward the library and global canon, not assumptions that the chapter assets already exist. One approved visual plan serves both languages using shared beat IDs sized for the longer measured line. Keep each language’s approved speech and subtitles separate; check speech crossing cuts and cues against both tracks. Reuse footage only while the visual meaning and timing remain valid.

Do not blindly reuse a pose, character appearance, location, prop, factual claim, staging choice, timing, translation, image, preset effect or prior approval in a different context. Nor should reuse force a poor image or omit a required event.

### 3. Checklist

| # | Item | File or location | Who | Owner decision? | Done-test |
|---|---|---|---|---|---|
| 1 | Lock S4 source, EASY lines, voices and shared timing | `docs/pilot/FINAL_PLAN.md`, audio manifests | Owner | Yes | Approved versions and hashes recorded; Hindi status explicit |
| 2 | Review S4 finals against each beat | `final_clean/SH_S4_*.png`, binding JSON | Owner | Yes | Each selected image and hash approved for its use |
| 3 | Define record and approval format | `canon/shot_plans/` | Claude | Yes | Example record contains fields above and owner approval |
| 4 | Implement exact lookup and candidate matching | Director harness | Claude | No | Exact match skips Kimi; changed inputs do not silently match |
| 5 | Bind roles to files and verify hashes | `final_image_binding.json`, render harness | Claude | No | Missing, changed or incompatible input blocks rendering |
| 6 | Shrink Kimi contract; retain `NEED_NEW` | `scripts/source/director_test.py` | Claude | Yes, contract | Existing IDs accepted; new descriptions rejected; unresolved blocks |
| 7 | Adapt S4 using fitting flat images | S4 plan and binding | Claude, owner | Yes | Five beats covered; staging warnings resolved; approved record saved |
| 8 | Request only genuinely missing shots, if any | S4 unresolved list | Kimi, owner | Yes | Each request has reason; resulting record approved |
| 9 | Render S4 and verify both language tracks | Builder harness and S4 receipts | Claude, owner | Yes | Owner accepts picture; complete speech, subtitles and cue checks pass |
| 10 | Test interruption and reuse | S4 receipts and harness | Claude, Codex | No | Resume skips verified work; changed inputs invalidate affected work |
| 11 | Review evidence before expanding | S4 records and receipts | Codex, owner | Yes | Reviewer reports supported results; owner approves next scenes |

### 4. S4 recommendation

**Hybrid:** retain the recorded draft as evidence and reuse its five story beats where the owner accepts them. Rebind or adapt each shot to an appropriate existing flat final, using preset 03 where suitable; use 10 or 11 only when their specific insert or transition fits. Do not assume the named `SH_S4_*` images actually depict the required moments until reviewed. If a crucial beat cannot be conveyed faithfully, mark only that shot `NEED_NEW`; make layers or another image only after the owner chooses. A held bow is not evidence of a moving bow.

### 5. Main risks

The images, split, wording, bible and plan are not yet owner-approved; the final plan itself is also a proposal. A technically valid plan can still misrepresent the sacred source or produce weak visuals. Flat-only treatment may become repetitive, but adding layers indiscriminately costs work without proving improvement. Reuse must fail closed on changed hashes and approvals. Finally, S4’s existing timing analysis assumes the measured clips are accepted; the bilingual master, recovery and actual S4 render still need evidence.