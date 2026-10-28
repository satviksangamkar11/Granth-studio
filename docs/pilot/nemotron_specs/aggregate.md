# SPEC: NEW `scripts/pipeline/stage1/aggregate.py` + NEW `tests/test_stage1_aggregate.py`. Return exactly these TWO files in full; do not output or change any other file.
Purpose: one entry point that validates the nine Stage 1 documents TOGETHER, including the cross-document rules that no single unit can check. Two independent reviewers (Codex, Haiku) found these intent gaps; each X-rule below closes one. Standard library only; `from __future__ import annotations`; nothing at import time except imports and definitions; no print except in `main()`; no key or secret is ever read. Do not over-engineer: plain functions, no classes, no config.

## Units and their API (already written, do NOT modify them)
The nine modules `scripts/pipeline/stage1/<unit>.py` for unit in `story_map, coverage, scenes, shots, briefs, looks, voices, sounds, questions` each expose `SCHEMA` (dict), `schema_errors(doc) -> list[str]` and `validate(adhyay, doc, docs, ctx) -> list[str]` (semantic checks; they never raise). Load them with importlib BY PATH from the folder of this file (`Path(__file__).resolve().parent / f"{unit}.py"`, unique module names such as `stage1_unit_<unit>`, cached in a module-level dict after the first load; a unit that cannot be loaded gives the single error `aggregate: cannot load <unit>`).
`docs` is a dict unit -> document (dict). `ctx` is a dict. The shared valid base used by all unit tests is `docs/pilot/nemotron_specs/stage1_base.json` with the keys `docs` and `ctx`; ctx has script_line_ids, core_line_ids, chapter_ovis, unfilmed_ovis, preset_ids, sound_ids, saved_voices, speaking_characters, known_states. Additional OPTIONAL ctx keys used here: `series_voices` (dict character_id -> voice_key of voices already assigned in the series; absent = {}) and `script_texts` (list of str, the owner's script line texts; absent = []).
Field names you need:
- story_map: `ovi_types` [{ovi:int, type in STORY|TEACHING|PHILOSOPHY|INVOCATION|RECAP|PHALASHRUTI|OTHER}], `events` [{event_id, kind story|discourse, title, ovi_range [lo,hi], key_ovis [int], closure RESOLVED_IN_ADHYAY|CONTINUES_NEXT_ADHYAY|STARTED_EARLIER|SOURCE_INCOMPLETE_OR_AMBIGUOUS|NA}].
- coverage: `ovis` [{ovi, disposition VISUALISED|NARRATED|QUOTED|MERGED_EQUIVALENT|PROPOSE_OMISSION, reason?, covered_by?}].
- scenes: `scenes` [{scene_id, section_kind, ovi_range [lo,hi], line_ids, ...}].
- shots: `shots` [{shot_id, scene_id, ovi_ids [int], beat_line_ids, ...}].
- questions: `questions` [{id, text, scene_id}].
- voices: `cast` [{character_id, voice_key, voice_id, gender, status RECURRING|NEW_PROPOSED}].

## API
- `UNITS`: the tuple of the nine unit names in the order above.
- `validate_all(adhyay: int, docs: Any, ctx: Any) -> list[str]`: returns ALL errors (empty list = valid). Never raises: any unexpected exception inside a step becomes the single error `aggregate: internal error in <step>`; a non-dict `docs` or `ctx` is reported once (`aggregate: docs must be an object` / `aggregate: ctx must be an object`) and then treated as `{}`.
  Step 1, per unit in order: if the document is missing or not a dict, the error is `<unit>: document missing`; else `errs = schema_errors(doc)`; if errs, add them and skip that unit's `validate` and its cross rules; else add the messages of `validate(adhyay, doc, docs, ctx)`. Remember which units are schema-valid.
  Step 2, cross rules. Each rule runs only when ALL the documents it reads are present and schema-valid (otherwise it is skipped silently). Ranges are inclusive [lo, hi] of ints; NEVER enumerate a range (compare lo <= n <= hi). Treat bool as not an int. Messages are exactly as quoted (tests assert the ovi number / id appears, not extra wording):
  - X1 `story_map`: every ovi typed STORY or TEACHING must lie inside the ovi_range of at least one event, else `story_map: ovi N is typed <TYPE> but is in no event` (so a chapter typed all story with an empty events list fails).
  - X2 `coverage` + `story_map`: an ovi typed STORY or TEACHING must not have the disposition PROPOSE_OMISSION, else `coverage: ovi N is <TYPE> but an omission is proposed`.
  - X3 `coverage` + ctx `unfilmed_ovis` (the owner-approved omissions): every PROPOSE_OMISSION ovi must be in ctx `unfilmed_ovis`, else `coverage: ovi N omission is not approved by the owner`; every ovi in ctx `unfilmed_ovis` must have the disposition PROPOSE_OMISSION in coverage, else `coverage: ovi N is approved as unfilmed but has no omission proposal`.
  - X4 `coverage` + `shots` + `scenes`: every ovi with the disposition VISUALISED must appear in the `ovi_ids` of at least one shot, else `coverage: ovi N is VISUALISED but is in no shot`; every ovi whose disposition is NOT PROPOSE_OMISSION must lie in some scene ovi_range, else `coverage: ovi N is in no scene`.
  - X5 `story_map` + `scenes`: every key ovi of every event must lie in some scene ovi_range, else `story_map: key ovi N of event <event_id> is in no scene`.
  - X6 `story_map` + `questions` + `scenes`: an event with closure SOURCE_INCOMPLETE_OR_AMBIGUOUS needs at least one question whose scene_id names a scene whose ovi_range overlaps the event ovi_range (overlap: lo1 <= hi2 and lo2 <= hi1), else `story_map: ambiguous event <event_id> has no question`.
  - X7 `voices` + ctx `series_voices`: for a cast entry whose character_id is a key of series_voices: status RECURRING requires voice_key == series_voices[character_id], else `voices: recurring character <character_id> has a different voice than the series`; status NEW_PROPOSED is the error `voices: character <character_id> already has a series voice`.
  - X8 EASY script guard, ctx `script_texts`: walk every string value (any depth, lists and dicts, depth limit 8) of all nine documents; normalise both sides (casefold, collapse whitespace); if a normalised script text of at least 20 characters is a substring of the normalised string value, add `<unit>: free text copies script wording (<key path>)` where the key path looks like `scenes/0/goal`.
- `export_schemas(out_dir: Path) -> list[Path]`: writes `stage1_<unit>.schema.json` (json.dumps with sort_keys and indent 2, utf-8, trailing newline) for each unit from its `SCHEMA` into `out_dir` (created if missing); raises `FileExistsError` BEFORE writing anything if any target file already exists; returns the nine paths.
- `main(argv=None) -> int`: `--adhyay N` (int, required), `--docs-dir PATH` (required; reads `<unit>.json` for each unit; a missing file is simply an absent document), `--ctx PATH` (optional JSON file, default {}), optional `--export-schemas DIR`. Prints one error per line, then `N error(s)`; returns 0 when there are no errors and 1 otherwise; returns 2 after printing `refused: <reason>` for unreadable JSON or an existing schema file. `if __name__ == "__main__": raise SystemExit(main())`.

## Tests (`tests/test_stage1_aggregate.py`)
Load the module by path with importlib (`ROOT = Path(__file__).resolve().parents[1]`); load `BASE = json.load(...stage1_base.json)` with `BASE["docs"]` and `BASE["ctx"]`; use `copy.deepcopy` and plain assignment for EVERY mutation (never a helper that rejects "no effect" mutations; make sure each mutation really changes the value; remember `True == 1` in Python).
1. The unmodified base is valid: `validate_all(1, docs, ctx) == []`.
2. One isolated test per rule X1..X8, each violating ONLY that rule (verify by hand that no other rule fires; assert that the ovi number / event id / character id appears in an error, and that the corrected twin gives []):
   - X1: make ovi 3 fall outside every event (E1 ovi_range [4,5], key_ovis [4]); also the empty-events case (events set to [] while ovi_types has STORY ovis).
   - X2: set the coverage disposition of a STORY ovi to PROPOSE_OMISSION with a reason and add that ovi to ctx unfilmed_ovis (so X3 is satisfied); make sure X4 does not also fire for it.
   - X3: both directions (a proposed omission not in unfilmed_ovis; an unfilmed ovi without a proposal).
   - X4: both parts (a VISUALISED ovi in no shot; a non-omitted ovi in no scene).
   - X5: a key ovi in no scene.
   - X6: set event E2 closure to SOURCE_INCOMPLETE_OR_AMBIGUOUS: without a question on S2 it errors; with a question whose scene_id is S2 it is valid.
   - X7: with ctx `series_voices` = {"gajanan_maharaj": "other_key"} the RECURRING entry errors; with the matching key it is valid; a NEW_PROPOSED entry for a series character errors.
   - X8: ctx `script_texts` contains a 25-character script line that is copied into `scenes[0].goal`: error naming the path; a short text (under 20 characters) must NOT trigger.
3. Robustness: docs None, docs {} (nine `document missing` errors), ctx None, a document that is a list, a unit that fails its schema (its validate and cross rules are skipped, no exception), huge ranges [1, 10**12] in scenes and events return quickly.
4. `export_schemas` writes nine files in tmp_path and raises FileExistsError on the second call leaving the files unchanged; `main` exit codes 0, 1 and 2 using tmp_path files and capsys.

Reply with only the two FILE blocks:
FILE: scripts/pipeline/stage1/aggregate.py
FILE: tests/test_stage1_aggregate.py


## AMENDMENTS 2026-10-28 (AUTHORITATIVE over everything above; made after the Codex + Haiku code and intent reviews)
- X1 is kind-aware: a STORY ovi must lie in an event of kind `story`, a TEACHING ovi in an event of kind `discourse` (message `story_map: ovi N is typed <TYPE> but is in no <kind> event`).
- X2 was REMOVED on purpose: STAGE1_RULES.md says the ovi type does not decide omission; only the owner approval (X3, via ctx `unfilmed_ovis`) decides.
- X8 flags any contiguous 6-word run copied from a script text (casefold, punctuation stripped), over every document that is a dict, whatever the schema status.
- New X9: event ovi_range inside min..max of ctx `chapter_ovis` and key ovis members of it. New X10: for each scene, at least one overlapping event has kind equal to the scene section_kind. X7 also rejects a NEW_PROPOSED character whose voice_key equals a series voice of another character. New X11: optional ctx `verified_voices` (list of voice keys verified for Marathi and Hindi); when it is a list every cast voice_key must be in it.
- Any ctx value of the wrong type is read as empty (never raises); `aggregate: internal error in X<n>` is a last-resort sentinel only.
- `main --export-schemas DIR` exports AND then validates and reports like without the flag.
- `voices` documents: a NEW_PROPOSED cast entry requires a non-empty `reason` (selection by description); RECURRING entries do not.
