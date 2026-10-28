# Stage 1 intent review 2 (read-only)

Scope: `docs/pilot/REVIEW_PROMPT_INTENT.md`, checked against the nine units in `scripts/pipeline/stage1/` (including the new `aggregate.py`), `approvals.py`, `gates.py`, `chapter.py`, `import_canon_docx.py`, `canon/series/voices.json` and `voice_library.py`. `validate_stage1.py` and the five `schemas/stage1_*.schema.json` files were read as the older contract.

Method: in-memory checks only, run with `python -B` and no file writes. Each check builds a fixture document and calls `aggregate.validate_all` (or a unit's `validate`). Results are quoted as "check Tn". Unit tests were not re-run; `docs/pilot/TEST_RUN_STAGE1.txt` (610 passed, 1 warning) is taken as given.

Note on the prompt: `REVIEW_PROMPT_INTENT.md` has no "Update" paragraph. I could not find a list of what changed since review 1. I inferred the additions from the code: `stage1/aggregate.py` (new cross-unit checks X1-X8), `approvals.py` and `gates.py` (owner approval records, not yet wired to Stage 1), and the new `voice_library.py` fields.

## Intent status

### 1. GENERIC (one pipeline, data only per Adhyay): MET
- The unit checks and `aggregate.py` contain no Chapter 2 literal (grep for "chapter 2", "adhyay_02", "adhyay 2" in `scripts/pipeline/stage1/` and `import_canon_docx.py` returned nothing).
- `aggregate.py:76` takes `adhyay` as an argument and `aggregate.py:89-117` runs the same nine checks for any number.
- `chapter.py:16-35` has an `adhyay == 1` path table. It is data, not logic, but A1 is still read from a different layout (`chapter.py:37-54` for the others).
- Stale, not blocking: `validate_stage1.py:255` still expects `palette_id`, and nothing imports it. `schemas/stage1_shots.schema.json` and `schemas/stage1_sound_suggestions.schema.json` still contain `preset_hint` and `palette_id`. `aggregate.py:280` can export the nine schemas, but this was not run. The live contract is in each unit's `SCHEMA`.

### 2. NOT EVERY OVI IS FILMED (approved omissions only): PARTIAL
- Good: exactly one disposition per ovi (`coverage.py:23-25`, `:298-304`). An ovi outside every scene and not unfilmed fails (`scenes.py:238-242`, `aggregate.py:179-189` for non-omitted ovis). A proposed omission produces a "owner approval needed" note (`coverage.py:281-282`). Check T5: a proposed omission not in `ctx.unfilmed_ovis` gives "omission is not approved by the owner" (`aggregate.py:153-156`).
- Gap, approval is still a caller-supplied set: `aggregate.py:152` reads `ctx["unfilmed_ovis"]`. T5b: putting ovi 3 in `ctx.unfilmed_ovis` makes the omission pass X3. The approval mechanism exists (`approvals.py:29` `approve`, `:75` `status`, `gates.py:76` `require_approved`), but `aggregate.py` never reads `approvals.json` (grep returned nothing). No approval record is checked.
- Gap, NARRATED is not tied to the script: check T4, a NARRATED ovi with no `covered_by` and no script line passes all checks (`coverage.py:288-296` only checks `covered_by` when it is present).
- Smallest change: derive `unfilmed_ovis` from `approvals.json` items with `status() == "APPROVED"` (via `gates`), and require `covered_by` (a line id) for NARRATED and QUOTED.

### 3. UNDERSTAND THE ADHYAY FIRST (complete stories, closure, story vs discourse): PARTIAL
- Closed since review 1: a STORY or TEACHING ovi must sit in an event (`aggregate.py:122-135`). Check T1, an empty event list with story ovis, now fails with five errors. An ambiguous event needs a question on an overlapping scene (`aggregate.py:210-243`, check T11 passes as expected). Discourse scenes need a `teaching_treatment` (`scenes.py:213-216`, schema `scenes.py:47-70`).
- Gap, event ranges are not bounded by the chapter: `story_map.py:65-133` never checks `ovi_range` against `chapter_ovis`. Check T2, an event at ovi 900-905 in a 5-ovi chapter, returns no error.
- Gap, event kind is not checked against scene kind: `aggregate.py` never compares `events[].kind` (`story_map.py:46`) with `scenes[].section_kind` (`scenes.py:26`). Check T3, a story event over a discourse scene, returns no error.
- Smallest change: in `story_map.py` require each `ovi_range` to lie inside `chapter_ovis`. In `aggregate.py` add a check that the `section_kind` of each scene matches the `kind` of the events that overlap its range.

### 4. EASY SCRIPT never written, edited or flagged by Kimi: PARTIAL
- Good: scenes and shots reference immutable line ids only (`scenes.py:43-46`, `shots.py:43-47` in the older schema, `scenes.py:198-205` order and membership).
- Closed in part since review 1: `aggregate.py:261-275` (X8) rejects a free-text field that copies a full script line, normalised. Check T6b, a full line copied into `scenes/0/turn/text`, is flagged.
- Gap, partial copies pass: check T6a, a 6-word run of a script line in `turn.text`, returns no error because the test is `script in norm_val` (`aggregate.py:273`) on whole lines.
- Gap, the guard is skipped when any unit fails schema: `aggregate.py:262` runs X8 only if `all_valid(*UNITS)`. A schema-invalid document disables the check.
- Gap, `script_texts` is optional: `aggregate.py:263` defaults to an empty list, so a caller that does not pass the script text gets no check.
- Smallest change: scan the raw documents for any run of about six normalised script words, and run this check whatever the schema status.

### 5. SHOTS (preset list only, else NEED_NEW): MET
- `shots.py:139` allows only `NN_name` or `NEED_NEW`. `shots.py:145-159` requires `need_new` with reason and class for NEED_NEW. `shots.py:248-249` rejects a preset not in `ctx["preset_ids"]`.
- Check, `preset: "99_made_up"` gives "unknown preset 99_made_up" (check T6c). No animation or Blender field exists in the shot schema (`shots.py:102-125`).
- Note: Stage 2 generation, testing and owner-approved saving are not in Stage 1 and are not checked here.

### 6. SOUND (palette sound or NEED_NEW plus prompt; effects are separate files): MET
- `sounds.py:346` restricts `sound_id` to `bed_*`, `fx_*` or `NEED_NEW`. `sounds.py:352-354` requires `sound_prompt` only for NEED_NEW. `sounds.py:438-442` checks the kind matches the prefix.
- The cue schema has no speech or dialogue field, so effects cannot be placed inside speech by Stage 1 output.
- Caveat: palette availability and version are checked only as membership in `ctx["sound_ids"]` (`sounds.py:383`). That is enough for Stage 1 intent, but not a version check.

### 7. VOICES (by description, same voice for a recurring character, no invented ids): PARTIAL
- Closed since review 1: a RECURRING character with a different voice key than the series fails (`aggregate.py:245-259`). Check T7: `Maharaj` moved from `voice_a` to `voice_b` gives "has a different voice than the series". A NEW_PROPOSED entry needs a `reason` (`voices.py:23-36`). Voice ids must match the saved library (`voices.py:123-133`).
- Gap, `series_voices` is never built: nothing reads `canon/series/voices.json` or its `assigned_to` (grep returned nothing outside `aggregate.py:248`). A caller must pass the map.
- Gap, a RECURRING character missing from `series_voices` passes: check T7b returns no error (`aggregate.py:253` skips unknown characters).
- Gap, description-based casting is not checkable: `voices.py:56-64` never reads `description`, `gender` matching or a use case, and `voice_library.py` writes them but Stage 1 does not read them.
- Gap, a NEW_PROPOSED voice raises no question (check T12 returns no error).

### 8. CANON AND LOOKS (Kimi proposes; owner approves; briefs follow the A1 image lessons): PARTIAL
- Good: looks must cite chapter ovis (`looks.py:110-117`), known states cannot be redecided (`looks.py:119-122`), and the basis is stated or inferred (`looks.py:198`).
- Gap, no owner-approval field: `looks.py:184-190` has no approval field, and grep for "approv" in `looks.py` returned nothing (check T14).
- Gap, briefs are not linked to looks or to registered people and places: `aggregate.py` has no check that brief `people` or `place_id` exist in the looks entries. Check T9, a brief with person "Stranger" at place "nowhere" passes.
- Gap, the brief schema lacks the required planning fields. `briefs.py:23-36` has no preset slot, full-frame or layer need, or safe crop. These are required by `STAGE1_RULES.md:58`.
- Gap, the A1 "only on-screen facts" lesson is a prompt rule only. Check T9 passes `on_screen_facts: ["Narrator: he is wise and glowing"]` (`briefs.py:68-72` checks only that the list is non-empty).

### 9. QUESTIONS (ambiguities become questions, never silent guesses): PARTIAL
- Closed since review 1: a SOURCE_INCOMPLETE_OR_AMBIGUOUS event needs a question on an overlapping scene (`aggregate.py:210-243`, check T11 flags the missing question).
- Gap, not required for the other ambiguity kinds: a NEED_NEW shot (check T8 passes), a NEED_NEW sound, a NEW_PROPOSED voice (check T12 passes), and a PROPOSE_OMISSION (`coverage.py:141-142` only adds a note) all pass with no question. `questions.py:42-91` checks only ids and `scene_id`.
- Smallest change: in `aggregate.py` require a question with a matching `scene_id` for each NEED_NEW shot and cue, each NEW_PROPOSED voice and each PROPOSE_OMISSION.

### 10. ONE PICTURE, TWO AUDIO LANGUAGES: PARTIAL
- Good: Stage 1 documents carry no timing fields (grep for marathi, hindi, timing, duration, seconds across `stage1/*.py` returned nothing). Line ids and ovi ids are language-neutral. The importer keeps both languages per ovi (`import_canon_docx.py:255-258`).
- Gap, voices ignore language coverage: `voice_library.py:77-101` writes `marathi_verified` and `hindi_verified`, and `voices.py` never reads them (check T13: the string "verified" does not occur in `voices.py`). A voice verified only for Hindi can be cast on a Marathi-master line with no error.
- Smallest change: pass each voice's verified flags in `ctx` and require `marathi_verified` for Marathi lines and `hindi_verified` for Hindi lines.

## Closed since review 1
- Story ovi with no event (review 1 gap 2, check T1): closed by `aggregate.py:122-135`.
- Ambiguous story closure with no question (review 1 gap 4, partly): closed for SOURCE_INCOMPLETE by `aggregate.py:210-243`.
- Recurring voice moved (review 1 gap 3, partly): closed by `aggregate.py:245-259`, but only when `series_voices` is passed.
- Cross-unit validator stale (review 1 gap 1): closed for the live path by `aggregate.py` (nine units, schema from each unit's `SCHEMA`). Still open as cleanup: `validate_stage1.py` and the older `schemas/stage1_*.json` files.

## Still open
- Omission approval is a caller-supplied set, not an approval record (intent 2).
- NARRATED dispositions need no script line (intent 2, check T4).
- Event ranges outside the chapter and event kind against scene kind (intent 3, checks T2, T3).
- Partial script copies, and a guard that is skipped on schema failure (intent 4, checks T6a, T6c).
- `series_voices` is not built from the voice library, recurring characters missing from it pass, and no description or language check (intent 7, 10; checks T7b, T13).
- No question for NEED_NEW shots, NEW_PROPOSED voices or PROPOSE_OMISSION (intent 9; checks T8, T12).
- Brief planning fields (preset slot, layer or full-frame, safe crop) and the looks link are missing (intent 8; check T9).

## Closest gaps
1. Owner approval is not recorded: `unfilmed_ovis` is a caller-supplied set (`aggregate.py:152`), and `approvals.py`/`gates.py` are not wired to Stage 1. Derive omissions from APPROVED records in `approvals.json`.
2. Voices: `series_voices` is never built from `canon/series/voices.json`, a RECURRING character absent from it passes (T7b), and there is no Marathi/Hindi verified check (T13). Build the map and require the verified flag per language.
3. Questions are not required for NEED_NEW shots or cues, NEW_PROPOSED voices or PROPOSE_OMISSION (T8, T12). Add the check in `aggregate.py`.
4. Script wording: a six-word run of a script line passes (T6a), and the guard is skipped when any unit fails schema. Scan raw documents for runs of about six words.
5. Story bounds and kinds: event ranges outside the chapter pass (T2), and story events over discourse scenes pass (T3). Bound ranges in `story_map.py` and compare kinds in `aggregate.py`.

## Verdict: GAPS
