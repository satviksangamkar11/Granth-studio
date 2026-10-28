1. **GENERIC — PARTIAL.** The schemas accept Adhyays 1–21, and the DOCX reader takes `--adhyay` as data (`story_map.py:14`; `import_canon_docx.py:393-402`). But the Stage 1 calls and consolidation are specified as a plan, while prompt builders and command wiring are still listed as unbuilt (`STAGE1_RULES.md:25-29`; `PIPELINE_README.md:79`). **Correction:** wire the fixed Stage 1 sequence to chapter-specific data and run it against another Adhyay without code changes.

2. **OVI DISPOSITIONS — PARTIAL.** Each chapter ovi must have one disposition, and proposed omissions produce an approval-needed note (`coverage.py:140-164`). **High:** a `NARRATED` disposition with no script lines passes semantic validation; omission proposals are not matched to an owner approval (`coverage.py:148-156`). **Correction:** verify actual coverage and require an owner-approved omission before an ovi is left uncovered.

3. **UNDERSTAND THE ADHYAY — PARTIAL.** The design records ovi types, events and closure, and distinguishes discourse scenes with a teaching treatment (`story_map.py:19-47`; `scenes.py:23-59`). **High:** a chapter typed entirely as story with an empty event list passes semantic validation (`story_map.py:94-133`), so the output can omit the stories it was meant to identify. **Correction:** require story-typed ovis to be accounted for by source-linked story events, with unresolved closure surfaced for review.

4. **EASY SCRIPT — MET.** The shared rule prohibits Kimi from writing, editing, translating or critiquing script wording; scene and shot schemas refer to line IDs (`STAGE1_RULES.md:38-39`; `scenes.py:43-46`; `shots.py:43-47`). The rules assign any missing-coverage report to code (`STAGE1_RULES.md:22-23`).

5. **SHOTS — PARTIAL.** Shots select a supplied preset or `NEED_NEW`, and unknown preset IDs are rejected (`shots.py:48-68,155-158`). The intended Stage 2 generation, testing and owner approval are specified, but their completed reusable workflow is not evidenced here (`STAGE1_RULES.md:44-45`; `PIPELINE_README.md:79`). **Correction:** complete that downstream path, including saving an approved new preset for reuse.

6. **SOUND — PARTIAL.** The schema requires an effect prompt for `NEED_NEW`, and the rules specify separate effect files (`sounds.py:23-35`; `STAGE1_RULES.md:47-50`). **Medium:** validation checks only membership in an ID set, and the cue has no version field, so it cannot establish that the selected palette version is available (`sounds.py:63-64,113-117`). **Correction:** carry and validate the available palette version.

7. **VOICES — PARTIAL.** Unknown saved voice IDs are rejected (`voices.py:116-126`). **High:** the validator has no character-to-existing-assignment input; a recurring character assigned a different saved voice passes semantic validation. The schema also has no selection reason, despite the description-based rule (`voices.py:23-29`; `STAGE1_RULES.md:35-36`). **Correction:** validate against saved character assignments and available voice descriptions, and record the selection reason or an owner question when none fits.

8. **CANON AND LOOKS — PARTIAL.** Look proposals distinguish character, place and prop, cite ovis, and mark stated versus inferred; known states are rejected (`looks.py:24-35,110-122`). **Medium:** briefs capture several A1 fields but omit required planning details such as preset slot, layer/full-frame need and safe crop (`briefs.py:23-35`; `STAGE1_RULES.md:57-58`). **Correction:** add the missing brief fields and use them in the owner-approval flow.

9. **QUESTIONS — PARTIAL.** An explicit question output exists and checks IDs and scene references (`questions.py:12-25,54-89`). **Medium:** an event marked `SOURCE_INCOMPLETE_OR_AMBIGUOUS` and an empty question list both pass semantic validation (`story_map.py:47`; `questions.py:42-91`). **Correction:** require a linked owner question for explicitly flagged source ambiguities.

10. **ONE PICTURE, TWO AUDIO LANGUAGES — MET.** Stage 1 uses shared script-line anchors without duration fields; the rules reserve timing for code and require cue resolution against both languages’ measured speech windows (`STAGE1_RULES.md:38-39,47-53`; `sounds.py:23-31`).

The saved test receipt reports 575 passed (`docs/pilot/TEST_RUN_STAGE1.txt`). The four counterexamples above were checked in memory against semantic `validate` functions; the project virtual environment could not start in this sandbox, so those checks used a stub for the unavailable schema library. The examples are consistent with the visible schemas, but I did not rerun the full suite or execute Kimi.

## Closest gaps

- **High:** Bind claimed ovi coverage and omissions to actual coverage and owner approval.
- **High:** Prevent a story map from passing with story ovis but no mapped events.
- **High:** Enforce recurring voice assignments and description-based casting.
- **Medium:** Turn flagged source ambiguities into linked owner questions.
- **Medium:** Complete the chapter-generic Stage 1 execution and approved reusable-preset path.

## Verdict: GAPS