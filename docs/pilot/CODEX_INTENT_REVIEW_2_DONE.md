1. **GENERIC — PARTIAL.** The reader accepts an Adhyay number as input and writes to an Adhyay-specific path (`scripts/pipeline/import_canon_docx.py:338`, `:393`); the aggregator validates the same nine units for any Adhyay (`scripts/pipeline/stage1/aggregate.py:9`). The fixed end-to-end prompt and command wiring is still listed as unbuilt (`docs/pilot/PIPELINE_README.md:79`). **Smallest change:** wire the same Stage 1 sequence to chapter data and demonstrate it on another Adhyay without code changes.

2. **NOT EVERY OVI IS FILMED — PARTIAL.** X3 now compares proposals with the owner-approved omission list, and X4 checks visualised ovis against shots (`aggregate.py:149`, `:161`). But X2 forbids *any* STORY or TEACHING omission, although the rules say type alone does not decide omission (`aggregate.py:137`; `docs/pilot/STAGE1_RULES.md:21`). Also, `coverage.validate` returns an approval-needed note even for an approved omission, and the aggregator treats it as an error (`coverage.py:140`, `:166`; `aggregate.py:114`). **Smallest change:** permit owner-approved omissions regardless of type, and treat the approval-needed note as pending only until approval. Link narrated or quoted coverage to the relevant script ovi so a scene range alone cannot claim it.

3. **UNDERSTAND THE ADHYAY FIRST — PARTIAL.** X1 closes the empty-event gap for STORY and TEACHING ovis, and X5 puts event key ovis in scenes (`aggregate.py:122`, `:191`); discourse scenes require a treatment (`scenes.py:213`). X1 accepts *any* event kind for either type, so a story ovi can be accounted for solely by a discourse event; scene kinds are likewise not tied to the mapped content. **Smallest change:** connect story and teaching ovis to the appropriate event and scene kinds, allowing explicitly mixed ranges where needed.

4. **EASY SCRIPT — MET.** The shared rule expressly prohibits Kimi from writing, editing, translating or critiquing the locked script (`docs/pilot/STAGE1_RULES.md:39`), and scene plans reference line IDs (`scenes.py:191`). X8 adds a useful copy check when script text is supplied, but it only catches complete supplied lines of at least 20 characters (`aggregate.py:261`); it is a guard, not proof that every possible script violation is caught.

5. **SHOTS — MET.** The shot validator rejects unknown preset IDs and the schema requires details for `NEED_NEW` (`shots.py:48`, `:54`, `:155`). The specified downstream path is to generate JSON, test it, obtain owner approval and save it for reuse (`docs/pilot/PIPELINE_README.md:36`). That Stage 2 path is planned, not evidenced as completed here.

6. **SOUND — MET.** Sound cues select a supplied ID or `NEED_NEW`, which requires a prompt (`sounds.py:23`, `:33`, `:113`). The rules specify separate effects files and no effects tags in speech (`docs/pilot/STAGE1_RULES.md:48`). Palette version and availability validation remain implementation details from the first review, but the missing version field does not by itself defeat the stated sound intent.

7. **VOICES — PARTIAL.** X7 closes the recurring-voice mismatch **when** `series_voices` is supplied; saved keys and IDs are checked, and `NEW_PROPOSED` now requires a reason (`aggregate.py:245`; `voices.py:23`, `:123`). However, the context is optional, and the validator receives no availability or description data; a no-fit case has no way to leave a speaking character uncast while asking the owner (`voices.py:110`). **Smallest change:** supply the current library assignments and availability as required casting context, and allow an explicit no-fit owner question.

8. **CANON AND LOOKS — PARTIAL.** Look proposals carry entity kind, source ovis and stated/inferred basis (`looks.py:24`); the planned owner approval gate is explicit (`docs/pilot/PIPELINE_README.md:89`). The image brief schema omits material A1 planning details including preset slot, layer/full-frame need and safe crop, although the rules require them (`briefs.py:23`; `docs/pilot/STAGE1_RULES.md:57`). **Smallest change:** capture those missing brief details and pass the proposals through the owner approval gate.

9. **QUESTIONS — PARTIAL.** X6 closes the specific first-review gap where an explicitly ambiguous event had no question (`aggregate.py:210`). It accepts any question on an overlapping scene, even one unrelated to the ambiguity (`aggregate.py:232`); other unclear source points rely on the prompt rule rather than a recorded link. **Smallest change:** have the question identify the ambiguous event or issue it asks the owner to resolve.

10. **ONE PICTURE, TWO AUDIO LANGUAGES — MET.** The reader preserves Marathi and Hindi separately (`import_canon_docx.py:254`), and Stage 1 uses line anchors without assigning one language’s timing. The design calls for shared picture and cue placement against both speech windows (`docs/pilot/STAGE1_RULES.md:53`). The library’s bilingual verification flags are a casting preference, not a requirement that both flags be true (`docs/pilot/PIPELINE_README.md:116`).

The saved receipt reports 610 passing tests (`docs/pilot/TEST_RUN_STAGE1.txt:17`). An attempted read-only in-memory check in the available Python environment could not load the unit validators, so the findings above are based on the code and the supplied test evidence, not a claimed successful rerun.

## Closest gaps

- Allow approved omissions and stop treating their approval-needed notes as blocking errors; verify narrated and quoted coverage against script ovis.
- Connect story and teaching classifications to appropriate events and scenes.
- Finish the chapter-generic Stage 1 execution wiring.
- Require current series voice assignments and support a no-fit owner question.
- Link ambiguity questions to the issue and include the missing A1 image-brief details.

## Verdict: GAPS