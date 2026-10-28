# Read-only INTENT review: is Stage 1 what the owner actually intended? (do NOT edit any file except your own report)

You are checking MEANING, not test hygiene. The unit tests are already green (see `docs/pilot/TEST_RUN_STAGE1.txt`, a real run). Judge whether the Stage 1 design and code actually do what the OWNER intended. Sources, in order of authority: the owner's intents below, `docs/DECISIONS.md`, `docs/pilot/DECISION_LOG.md`, `docs/pilot/STAGE1_RULES.md`, `docs/pilot/PIPELINE_README.md`; code: `scripts/pipeline/stage1/{story_map,coverage,scenes,shots,briefs,looks,voices,sounds,questions}.py`, specs `docs/pilot/nemotron_specs/unit_<unit>.md` and `stage1_base.json`; reader `scripts/pipeline/import_canon_docx.py`. Note: `scenes.py` may be edited by a small fix while you read; ignore transient states.

## UPDATE for this SECOND intent review
A nine-document aggregator now exists: `scripts/pipeline/stage1/aggregate.py` (spec `docs/pilot/nemotron_specs/aggregate.md`, tests `tests/test_stage1_aggregate.py`) with cross-document rules X1-X8 written to close the gaps of the FIRST intent review (reports `docs/pilot/*_INTENT_REVIEW_1.md`): story ovis must sit in events, story/teaching ovis cannot be omitted, omissions need the owner approval list, coverage vs shots/scenes, key ovis in scenes, ambiguous events need a question, recurring voices keep the series voice, and free text may not copy the owner's script. `voices` also got a `reason` field (required for NEW_PROPOSED). Re-judge each intent with that in mind, say which first-review gaps are now closed and which remain, and keep the remaining-gap list to what truly matters (the owner does not want over-engineering).

## THIRD intent review: what changed since the second (reports `*_INTENT_REVIEW_2*.md`)
X2 removed on purpose; X1 kind-aware; new X9 (events inside the chapter); X8 = any 6-word copied run and not skipped on schema failure; ctx type robustness. Deferred ON PURPOSE and recorded as checklist rows N9-N14 in `docs/pilot/CHECKLIST_BUILD_PIPELINE.md` (do not report them as new gaps; judge only whether the INTENT is met within Stage 1 as scoped, and say clearly if a deferred row hides a real hole): ctx built from approvals/voice library by the Stage 1 runner, retiring the stale validator and old schemas, briefs fields, wider questions, voice verified flags, sound palette version.

## The owner's intents (each must be checked)
1. GENERIC: one fixed pipeline for ALL 21 Adhyays; a new Adhyay needs DATA only, no code change. Nothing may be hard-wired to Chapter 2 (the Chapter 2 docx is only a test input and the format of every later Adhyay).
2. NOT EVERY OVI IS FILMED: only what contributes to the story and to the teaching is shown; the rest may be omitted. Every ovi gets exactly one disposition; omissions are PROPOSED by Kimi with a reason and APPROVED by the owner; only approved omissions may be left uncovered.
3. UNDERSTAND THE ADHYAY FIRST: Stage 1 identifies the COMPLETE stories (events with their ovis and closure) and the scenes, and separates story from philosophy/teaching (discourse) scenes, with a teaching treatment for discourse scenes.
4. EASY SCRIPT: the owner's confirmed script is never written, edited or flagged by Kimi.
5. SHOTS: the cinematographer step picks an existing preset id from the preset list, else marks NEED_NEW (to be generated in Stage 2, then tested, owner-approved and saved for reuse). It never writes animation or Blender code.
6. SOUND: reuse a palette sound if one fits, else NEED_NEW plus an ElevenLabs sound prompt; effects are separate files, not tags in speech.
7. VOICES: chosen by DESCRIPTION from the owner's saved voice library; a recurring character keeps the same voice; Kimi does not invent voice ids.
8. CANON AND LOOKS: Kimi proposes the character/place/prop looks; image briefs follow the Adhyay 1 image lessons; owner approves.
9. QUESTIONS: ambiguities become explicit questions for the owner, never silent guesses.
10. ONE PICTURE, TWO AUDIO LANGUAGES (Marathi master, Hindi): nothing in Stage 1 may assume a single language or timing from one language.

## Output (markdown)
For each intent 1-10: `MET`, `PARTIAL` or `MISSING`, one or two lines of evidence with file:line, and, if not MET, the smallest concrete change that would meet it. Verify by a small in-memory check when you can (for example build a document that violates the intent and see whether `validate` catches it). Then `## Closest gaps` listing at most five items, most important first, each one line. Finish with exactly one line: `## Verdict: ALIGNED` (all ten MET, or only wording-level gaps) or `## Verdict: GAPS`. Be honest: PARTIAL is a normal answer. No praise, no rewriting of files.
