# Stage 1 intent review (read-only)

Scope: `docs/pilot/REVIEW_PROMPT_INTENT.md`, checked against `scripts/pipeline/stage1/*.py`, `scripts/pipeline/validate_stage1.py`, `scripts/pipeline/chapter.py`, `scripts/pipeline/import_canon_docx.py`, `schemas/stage1_*.schema.json`, `scripts/pipeline/make_schemas.py`, `canon/series/voices.json`.

In-memory checks were run with `python -B` and no file writes (`PYTHONDONTWRITEBYTECODE=1`). Results are quoted per intent as "check Tn". Unit tests were not re-run; `docs/pilot/TEST_RUN_STAGE1.txt` is taken as given.

## Intent status

### 1. GENERIC (one pipeline, data only for each Adhyay): MET
- No Chapter 2 literal in `scripts/pipeline/stage1/` or `import_canon_docx.py` (grep for "chapter 2", "adhyay_02", "adhyay 2" returned nothing).
- `scripts/pipeline/chapter.py:14-16` has an `adhyay == 1` branch that points at A1-only packet paths. Adhyay 2-21 use the generic layout at `chapter.py:37-54`. The A1 branch is a path table, not logic, so it does not block a new Adhyay. It does mean A1 is not read from the same location as the others.
- `import_canon_docx.py:339` writes `canon/adhyay_NN/` for any Adhyay number.
- Caveat: the cross-unit driver and schemas are stale (see Closest gaps 1). Generic in code, not yet generic in contracts.

### 2. NOT EVERY OVI IS FILMED (approved omissions only): PARTIAL
- Evidence: `stage1/coverage.py:23-25` (exactly one of five dispositions), `:141-142` (PROPOSE_OMISSION adds a "owner approval needed" note), `:145-146` (unfilmed + VISUALISED is an error), `scenes.py:229-234` (every non-unfilmed ovi must sit in a scene range).
- Check T2: an ovi with no scene and not in `unfilmed_ovis` returns "not covered by any scene". So an unapproved omission cannot be left uncovered. Good.
- Gap: the owner's approval is not recorded anywhere. `unfilmed_ovis` is a plain caller-supplied set (`scenes.py:134`, `coverage.py:111`). Nothing distinguishes a proposed omission from an approved one, and no schema field carries an approval. Smallest change: add an `approved_by_owner` field (or an approved-omissions file) and make `unfilmed_ovis` come only from it.

### 3. UNDERSTAND THE ADHYAY FIRST (complete stories, closure, story vs discourse): PARTIAL
- Evidence: `stage1/story_map.py:47` (closure enum), `:19`-`:23` (ovi types), `:46` (kind story|discourse), `:136-140` (validate). Discourse scenes need a teaching treatment: `scenes.py:206-208`, enforced in schema at `stage1/scenes.py:52-70`.
- Gap (T3): `story_map.py:65-133` never checks that STORY or TEACHING ovis fall inside an event, and never checks that event ranges lie inside the chapter. A STORY ovi 3 with no event, and an event at ovi 900-905 in a 5-ovi chapter, both return `[]`.
- Gap: nothing reads `story_map` at all. A grep for `story_map` across `stage1/*.py` and `validate_stage1.py` returns only its own file. Scene kinds are never checked against event kinds.

### 4. EASY SCRIPT never written, edited or flagged by Kimi: PARTIAL
- Evidence: scripts reference immutable line IDs only (`scenes.py:190-203`, line ids must exist in the script order). Schemas constrain line ids to `^S[0-9]{1,2}-L[0-9]{1,3}$`.
- Gap (T-G): free-text fields accept any prose up to 400 characters: `scenes.py` `goal` and `turn.text` (schema at `stage1/scenes.py:33-40`), `coverage.py` `reason` (`:27`), `questions.py` `text` (`:23`). Check T-G: `turn.text` = `Maharaj says: 'Come, let us walk.'` returns `[]`. No code compares free text with script wording, so a Kimi-written line or critique can pass.
- Smallest change: pass the script text in ctx and reject any free-text field that contains a run of N or more words from one script line.

### 5. SHOTS (preset list only, else NEED_NEW): MET
- Evidence: `stage1/shots.py:48` (preset pattern), `:120` and `:157-158` (preset must be in `ctx["preset_ids"]`), `:54-68` (NEED_NEW requires `need_new` with reason and class from the three allowed values).
- Check T-D: `preset: "99_made_up"` gives `unknown preset 99_made_up`. A NEED_NEW shot with `need_new: null` is caught by `schema_errors`.
- No animation or Blender field exists in the shot schema, so none can be written. The cross-unit driver is stale (Closest gaps 1); that does not change this unit's result.

### 6. SOUND (palette sound or NEED_NEW plus prompt; effects are separate files): MET
- Evidence: `stage1/sounds.py:27` (`sound_id` is `bed_*`, `fx_*` or NEED_NEW), `:33-35` (NEED_NEW requires `sound_prompt`, others must not carry one), `:116-117` (unknown id is an error), `:120-123` (kind must match prefix).
- No Stage 1 document has a speech or dialogue field, so effect tags cannot be placed inside speech by Stage 1 output.
- Note: `canon/series/sounds/palette.json` does not exist, so the palette is supplied only through ctx. The cross-unit driver still expects `palette_id` (`validate_stage1.py:255`).

### 7. VOICES (by description, same voice for a recurring character, no invented ids): PARTIAL
- Evidence: `stage1/voices.py:56-57` takes only `speaking_characters` and `saved_voices` (key to id). `:111-114` rejects duplicate listing of a recurring character, and `:116-126` checks that each `voice_id` matches the library. `:126` is the only id check.
- Gap (T-C): the "same voice every Adhyay" rule is not checked. A RECURRING character moved to a different saved key returns `[]`.
- Gap: `canon/series/voices.json` carries `description`, `assigned_to`, `marathi_verified` and `hindi_verified` (lines 14-15 and per voice). None of these reach `voices.py`, so selection by description is not checkable.
- Gap: the voice schema (`voices.py:23-29`) has no `reason` field, so the "short reason" the rules require has nowhere to live.

### 8. CANON AND LOOKS (Kimi proposes; owner approves; briefs follow the A1 image lessons): PARTIAL
- Evidence: `stage1/looks.py:110-117` (source ovis must be in chapter), `:119-122` (a known state cannot be redecided), `:24` and `:35` (basis stated|inferred).
- Gap: there is no owner-approval field in the looks schema (`looks.py:24`), so an unapproved look is indistinguishable from an approved one.
- Gap: `briefs.py` never reads `canon_looks` at all (grep). A brief's `people` names are free text (`briefs.py:55`), not linked to a registered character.
- Gap (T-E): the A1 image lessons are enforced only as a prompt rule. `on_screen_facts` accepts `Narrator: he is wise and glowing` with no error (check T-E: semantic returns `[]`, schema returns `[]`).

### 9. QUESTIONS (ambiguities become questions, never silent guesses): PARTIAL
- Evidence: `stage1/questions.py:42-91` checks ids are unique and that `scene_id` exists. That is all.
- Gap: no unit requires a question when it meets an ambiguity. A grep for "question" outside `questions.py` shows only the cross-unit driver. Cases that should raise a question and currently pass silently: `story_map` closure `SOURCE_INCOMPLETE_OR_AMBIGUOUS` (`story_map.py:47`), a `NEW_PROPOSED` voice (`voices.py:29`), NEED_NEW shots (`shots.py:54-68`), NEED_NEW sounds (`sounds.py:33-35`), and PROPOSE_OMISSION (`coverage.py:141-142`).

### 10. ONE PICTURE, TWO AUDIO LANGUAGES (no single-language or single-timing assumption): PARTIAL
- Evidence: a grep for marathi, hindi, mr_s, hi_s, timing, duration and seconds across `stage1/*.py` and `validate_stage1.py` returned nothing. Stage 1 documents carry no timings. Line IDs and ovi IDs are language-neutral. The importer keeps both languages per ovi (`import_canon_docx.py:255-258`). So the stage-1 units make no single-language assumption.
- Gap: voices are not checked for language coverage. `canon/series/voices.json` has `marathi_verified` and `hindi_verified` per voice (lines 14-15), and `voices.py` never reads them. A voice verified only for Hindi can be cast for a Marathi-master line with no error.

## Closest gaps

1. The cross-unit validator and its schemas are stale and incomplete. `schemas/stage1_shots`, `stage1_sound_suggestions` and `stage1_scenes` still use `preset_hint`, `palette_id` and no `section_kind`. Check A: `validate_stage1` rejects a valid Kimi shots/sounds/scenes set with "preset_hint is a required property" and "palette_id is a required property". `scripts/pipeline/make_schemas.py:27-41` defines only five stage-1 schemas, and there are no files for story_map, coverage, canon_looks or voice_cast. Smallest fix: generate schemas from each unit's own `SCHEMA`, and have `validate_stage1.py` call each unit's `validate`, passing all nine documents.
2. `story_map` is isolated and under-checked. No other unit reads it (T3). STORY/TEACHING ovis need not sit in an event, and event ranges are not bounded by the chapter. Smallest fix: in `story_map.py` require every STORY/TEACHING ovi to fall in one event and bound event ranges by `chapter_ovis`; pass `story_map` into `scenes`/`coverage` and check `section_kind` against event `kind`.
3. Voice rules are not enforced in code. No check that a RECURRING character keeps its library `voice_key` (T-C), no `reason` field, and no Marathi/Hindi verified check. Smallest fix: pass `assigned_to` and the verified flags in ctx, require `voice_key == assigned` for RECURRING, and add `reason` plus a per-language verified check.
4. Questions are not required. Nothing forces a question for SOURCE_INCOMPLETE closures, NEW_PROPOSED voices, NEED_NEW or PROPOSE_OMISSION. Smallest fix: in `validate_stage1.py`, for each such item require a question whose `scene_id` or id references it.
5. Owner approval and script wording are unguarded. Omissions and looks have no approval record (intents 2 and 8), and free-text fields can carry script wording (T-G). Smallest fix: add an approval field or approved-omissions file that is the only source of `unfilmed_ovis`, and reject free text that copies a run of script words.

## Summary

Seven intents are PARTIAL (2, 3, 4, 7, 8, 9, 10) and three are MET (1, 5, 6). Stage 1 units are individually sound on structure. The cross-unit contract is stale and the semantic links the intents depend on are missing.

## Verdict: GAPS
