1. **GENERIC — PARTIAL.** The importer accepts an Adhyay number, and the aggregator runs the same nine units for each chapter (`scripts/pipeline/import_canon_docx.py:393`, `scripts/pipeline/stage1/aggregate.py:112`). The data-driven Stage 1 runner is still deferred under N9 (`docs/pilot/CHECKLIST_BUILD_PIPELINE.md:120`). **Change:** complete that runner and demonstrate another Adhyay with data-only changes.

2. **NOT EVERY OVI IS FILMED — PARTIAL.** X2’s removal correctly permits approved omissions regardless of type; X3 checks the supplied approval list, and X4 checks visualised ovis against shots (`aggregate.py:190`, `:205`). But `coverage.py:141` emits an approval-needed note for *every* omission, and `aggregate.py:150` treats it as a blocking result even after approval; narrated coverage also need not identify a script line (`coverage.py:148`). **Change:** stop blocking an approved omission and link narrated or quoted coverage to its script evidence.

3. **UNDERSTAND THE ADHYAY FIRST — PARTIAL.** Kind-aware X1 and X9 close the earlier event-kind and chapter-bound gaps; discourse scenes require a treatment (`aggregate.py:158`, `:344`; `scenes.py:54`). Event kind still is not connected to scene kind, so a story event can be represented solely by a discourse scene. **Change:** check that scene treatment matches the mapped content, allowing mixed ranges where appropriate.

4. **EASY SCRIPT — MET.** The rules prohibit Kimi from writing, editing or critiquing the script (`docs/pilot/STAGE1_RULES.md:39`). X8 now checks six-word copied runs even when a document fails schema, closing both earlier guard gaps (`aggregate.py:317`). The deferred N9 runner must supply the script texts for that guard to work.

5. **SHOTS — MET.** The shot contract restricts choices to supplied preset IDs or `NEED_NEW`, with a reason and class; it has no animation-code output (`scripts/pipeline/stage1/shots.py:48`, `:155`). The generation, testing, approval and reuse path is specified for Stage 2 (`docs/pilot/PIPELINE_README.md:36`).

6. **SOUND — MET.** Cues select a supplied sound ID or `NEED_NEW`, which requires a sound prompt (`scripts/pipeline/stage1/sounds.py:23`, `:33`, `:113`). The pipeline specifies separate effect files, not speech tags (`docs/pilot/PIPELINE_README.md:108`). Deferred N14 leaves version-change detection for later.

7. **VOICES — PARTIAL.** Saved keys and IDs are checked, and X7 closes the recurring-voice mismatch when the series assignment is supplied (`scripts/pipeline/stage1/voices.py:123`; `aggregate.py:298`). Description-based selection still depends on the deferred runner, and a speaking character has no explicit no-fit route to an owner question (`voices.py:110`). **Change:** supply the library descriptions and assignments, and allow a no-fit question instead of forcing a cast.

8. **CANON AND LOOKS — PARTIAL.** Looks are proposals with source and basis, and owner approval is planned (`scripts/pipeline/stage1/looks.py:24`; `docs/pilot/PIPELINE_README.md:89`). The deferred N11 records a real intent hole: briefs lack the required preset slot, layer/full-frame need and safe crop, and are not linked to approved looks. **Change:** complete N11’s fields and approval linkage.

9. **QUESTIONS — PARTIAL.** X6 closes the earlier missing-question case for explicitly ambiguous events, but any question on an overlapping scene satisfies it, even if unrelated (`aggregate.py:260`). Deferred N12 covers other proposal types. **Change:** identify the event or issue each question resolves.

10. **ONE PICTURE, TWO AUDIO LANGUAGES — MET.** The importer keeps Marathi and Hindi separately (`scripts/pipeline/import_canon_docx.py:254`); Stage 1 uses line anchors rather than assigning one language’s timing. The sound design calls for placement against both speech windows (`docs/pilot/PIPELINE_README.md:109`). Deferred N13 remains relevant to voice suitability; the documented current rule prefers bilingual verification rather than requiring it (`PIPELINE_README.md:114`).

The supplied test receipt was treated as evidence of the recorded run, not proof of intent. My in-memory checks could not load the validators: the project Python failed to start under the read-only environment, and the available system Python lacked their dependencies. Findings above are based on the inspected contracts and code.

## Closest gaps

- Make approved omissions non-blocking and require evidence for narrated or quoted coverage.
- Connect event kinds to scene kinds so story and teaching receive the intended treatment.
- Complete the deferred generic runner and authoritative context wiring; until then, approval and script-copy checks depend on caller-supplied data.
- Complete deferred N11 and provide a no-fit voice question.
- Link ambiguity questions to the actual issue they resolve.

## Verdict: GAPS