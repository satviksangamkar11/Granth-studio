# Stage 1 intent review 3 (read-only, Haiku 5.5 low)

Scope: `docs/pilot/REVIEW_PROMPT_INTENT.md` (UPDATE sections, rows N9-N14 of `CHECKLIST_BUILD_PIPELINE.md`), checked against `scripts/pipeline/stage1/aggregate.py` (X1, X3-X9; X2 removed), `coverage.py`, `scenes.py`, `story_map.py`, `voices.py`, `shots.py`, `sounds.py`, `looks.py`, `briefs.py`, `questions.py`.

Method: code reading with file:line evidence. I did not run in-memory fixtures this round; each "hole" below is a code-path claim that a fixture should confirm. Deferred rows N9-N14 are not counted as new gaps; where a deferred row carries a real hole, it is said so.

## Intent status

### 1. GENERIC: MET
- `aggregate.py:112` takes `adhyay` as an argument; `aggregate.py:125-150` and `:159-365` run the same checks for any Adhyay. No Chapter 2 literal in the Stage 1 units (review 2 grep result stands).
- `chapter.py:16-35` keeps an A1 legacy path table. It is data, not logic.
- Stale, non-blocking: `validate_stage1.py` and `schemas/stage1_shots.schema.json` still carry `preset_hint`/`palette_id` (N10).

### 2. NOT EVERY OVI IS FILMED (approved omissions only): PARTIAL
- MET part: one disposition per ovi and omissions need a reason (`coverage.py:42`); an unlisted ovi fails X4 (`aggregate.py:224-234`); a PROPOSE_OMISSION not in `ctx.unfilmed_ovis` fails X3 (`aggregate.py:194-198`).
- Deferred hole (N9): the approved set is caller-supplied (`aggregate.py:194`). Nothing reads `approvals.json`. Until N9 lands, any caller can approve an omission.
- REAL HOLE (not deferred): NARRATED has no `covered_by` and no script line. The schema requires `covered_by` only for MERGED_EQUIVALENT (`coverage.py:45-50`); `coverage.py:148-156` checks `covered_by` only when present. A NARRATED ovi with nothing narrating it passes.

### 3. UNDERSTAND THE ADHYAY FIRST (complete stories, story vs discourse): PARTIAL
- MET part: a STORY ovi must sit in a story event and a TEACHING ovi in a discourse event (`aggregate.py:159-186`); an ambiguous event needs a question on an overlapping scene (`aggregate.py:260-294`); discourse scenes need a `teaching_treatment` (`scenes.py:214-216`).
- Closed since review 2: event ranges outside the chapter (X9, `aggregate.py:344-365`), but only when `ctx.chapter_ovis` is supplied (N9).
- REAL HOLE (not deferred): a story event can sit over a discourse scene. X1 checks only ovi types against event kinds; no code compares `events[].kind` (`story_map.py:46`) with `scenes[].section_kind` (`scenes.py:26`). Nothing in `aggregate.py` mentions `section_kind`.

### 4. EASY SCRIPT never written, edited or flagged by Kimi: MET (within scope)
- X8 now runs on all nine documents regardless of schema status (`aggregate.py:317-342`), and matches any 6-word normalised run (`aggregate.py:323-340`). Review 2 gaps T6a and the skip-on-schema-failure gap are closed.
- Depends on `ctx.script_texts`, which is caller-supplied (N9). Scenes and shots use line ids only (`scenes.py:43-46`).

### 5. SHOTS (preset list or NEED_NEW): MET
- `shots.py:48` allows only `NN_name` or `NEED_NEW`; `shots.py:54` requires `need_new` for NEED_NEW; `shots.py:157` rejects a preset not in `ctx.preset_ids`. No animation or Blender field in the schema.

### 6. SOUND (palette sound or NEED_NEW plus prompt; separate effects): MET
- `sounds.py:27` restricts `sound_id` to `bed_*`, `fx_*` or `NEED_NEW`; `sounds.py:116-117` checks membership in `sound_ids`; `sounds.py:120` checks kind against prefix. No speech field on cues.
- Version check (N14) is deferred; it does not block the intent as scoped.

### 7. VOICES (by description, recurring keeps voice, no invented ids): PARTIAL
- MET part: a RECURRING character with a different voice fails (`aggregate.py:307-311`); a NEW_PROPOSED entry needs a reason; a voice key must be in the saved library (`voices.py:123-133`); two characters in one document may not share a voice key (`voices.py:135-146`).
- Deferred hole (N9): `series_voices` is caller-supplied. A RECURRING character missing from it passes (`aggregate.py:307`, `continue`).
- Deferred hole (N13): descriptions and gender are not read, so casting by description is not checked.
- REAL HOLE (not deferred): a NEW_PROPOSED character may take a voice key already assigned to a different series character. `voices.py:135-146` checks only within the one document, and X7 (`aggregate.py:312-313`) checks only the same character. The V2 done-test "assigned voice reused for a new character fails" is not met.

### 8. CANON AND LOOKS: PARTIAL
- MET part: looks cite chapter ovis (`looks.py:110-117`); known states cannot be redecided (`looks.py:119-122`); basis is stated or inferred (`looks.py:198`).
- Deferred (N11): no owner-approval field on looks; briefs lack preset slot, full-frame or layer need, safe crop, and link to looks.
- Hole: the brief `on_screen_facts` rule (A1 lesson) is prompt-only; `briefs.py:68-72` checks only non-empty.
- Note: N5 (unapproved look can never become canon) is an open row not listed as deferred; it is needed for this intent.

### 9. QUESTIONS (ambiguities become questions): PARTIAL
- MET part: SOURCE_INCOMPLETE_OR_AMBIGUOUS events need a question (X6).
- Deferred (N12): no question required for NEED_NEW shots or cues, NEW_PROPOSED voices, or PROPOSE_OMISSION. `coverage.py:142` only adds a note. This is an explicit deferral, not a silent guess in code, so it does not block the aggregate as scoped.

### 10. ONE PICTURE, TWO AUDIO LANGUAGES: PARTIAL
- MET part: Stage 1 documents carry no timing or per-language fields; line ids and ovi ids are language-neutral.
- Deferred hole (N13): `voice_library.py` writes `marathi_verified`/`hindi_verified`, but `voices.py` never reads them. A voice verified only for Hindi can be cast on a Marathi-master line. Intent not met until N13 lands.

## Closed since review 2
- X8 covers 6-word runs and runs on schema-invalid documents (review 2 gaps T6a and skip-on-failure).
- X9 bounds event ranges and key ovis to `chapter_ovis` (review 2 gap T2), when ctx supplies it.
- X1 story/teaching typing against event kinds (review 2 gap T1), already in review 2.

## Deferred rows that hide a real hole
- N9 is the whole approval and ctx gate: `unfilmed_ovis`, `series_voices`, `script_texts`, `chapter_ovis` all come from the caller. Until the runner builds them, intents 2, 4, 7 and 3 rely on the caller. This is a real hole for intent 2, the owner approval.
- N13 hides the language gap in intent 10.

## Closest gaps
1. Story event over a discourse scene passes: add a `section_kind` vs event `kind` check in X1 (`aggregate.py:159`, `scenes.py:26`). Intent 3.
2. NARRATED has no `covered_by` or script line: require `covered_by` for NARRATED and QUOTED in `coverage.py:45-50`. Intent 2.
3. A new character can take another character's assigned voice: check NEW_PROPOSED voice keys against the values of `series_voices` in X7 (`aggregate.py:299-315`). Intent 7.
4. Owner approval is caller-supplied (N9): derive `unfilmed_ovis` from APPROVED items in `approvals.json` via `gates.py`. Intent 2.
5. Marathi/Hindi verified flags unread (N13): require `marathi_verified` for Marathi lines and `hindi_verified` for Hindi lines. Intent 10.

## Verdict: GAPS
