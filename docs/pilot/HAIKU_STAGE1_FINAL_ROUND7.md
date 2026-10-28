# HAIKU read-only review: Stage 1 final (round 7), 2026-10-28

Scope: `scripts/pipeline/stage1/aggregate.py` (main focus), the amendments in `docs/pilot/nemotron_specs/aggregate.md`, and `tests/test_stage1_*.py`. Checks run:
- `uv run pytest -q --tb=short tests/test_stage1_*.py`: 563 passed, 0 failed.
- In-memory checks against `docs/pilot/nemotron_specs/stage1_base.json`: base document is valid (`validate_all` returns `[]`).
- Robustness fuzz: 1190 mutated cases (every top-level field and first-list-element field of all nine documents replaced by None, bool, int, float, str, list, dict, nested list, and an unexpected key; plus ctx of wrong types and adhyay of wrong types). No exception escaped `validate_all`.
- The nine unit modules were not re-read line by line; they are covered only by their own tests (passing) and the fuzz above.

## Per-unit BLOCKING defects

1. story_map: none.
2. coverage: none.
3. scenes: none (total gap-message cap present, bounded enumeration; test run and fuzz clean).
4. shots: none.
5. briefs: none.
6. looks: none.
7. voices: none (`reason` required for NEW_PROPOSED via schema, per amendment).
8. sounds: none.
9. questions: none.
10. aggregate: 2 BLOCKING defects.

### aggregate

A1. X1 is not kind-aware (spec AMENDMENTS, first bullet). Class 1.
- Location: `scripts/pipeline/stage1/aggregate.py` lines 158-176. `event_ranges` is built as `(lo, hi)` and drops `kind`, so a STORY ovi inside a `discourse` event passes.
- Verified: story_map with `ovi_types=[{ovi:3,type:STORY}]` and one event `kind:"discourse"`, `ovi_range:[1,5]` returns no X1 error (expected: `story_map: ovi 3 is typed STORY but is in no story event`).
- Exact fix: collect `(lo, hi, kind)` per event. For STORY require an event with `kind == "story"` covering the ovi; for TEACHING require `kind == "discourse"`. Message: `story_map: ovi {ovi} is typed {typ} but is in no {kind} event` with `kind` = `story` or `discourse`.
- Test gap (Class 3): `tests/test_stage1_aggregate.py` `test_x1_story_ovi_not_in_story_event` and `test_x1_teaching_ovi_not_in_discourse_event` place the ovi outside every range, so they never exercise the kind rule. Add a case where the ovi is inside a range of the wrong kind. Also update the expected text in the two X1 tests (current asserts `is in no event`, which the amended message does not contain).

A2. X2 is still implemented, but the amendment REMOVED it on purpose. Class 1.
- Location: `scripts/pipeline/stage1/aggregate.py` lines 180-199 (the whole X2 block).
- Verified: an approved STORY omission (ovi 1, in `ctx.unfilmed_ovis`) produces `coverage: ovi 1 is STORY but an omission is proposed`. Under the amendment this must produce no X2 error.
- Exact fix: delete the X2 block. Per STAGE1_RULES.md, only the owner approval (X3 via `unfilmed_ovis`) decides omission.
- Test gap (Class 1 in the tests): `tests/test_stage1_aggregate.py` `test_x2_story_teaching_propose_omission` (line 111) and `test_propose_omission_story_ovi_no_error` (line 506, asserts the X2 error). They pass today only because they encode the removed rule. Rewrite them to assert that an approved STORY omission gives no X2 error and no X3 error.

Confirmed correct in this round (no defect): X3 both directions; X4 both parts; X5; X6 overlap; X7 RECURRING mismatch, NEW_PROPOSED for series character, and NEW_PROPOSED reusing another character's series voice; X8 6-word run with punctuation stripped, all dict documents, schema status ignored; X9 range and key ovi inside chapter; X10 section_kind vs overlapping event kinds; X11 `verified_voices` when ctx value is a list; ctx values of wrong type read as empty; `main` exit codes 0/1/2; `export_schemas` raises before writing anything; huge ranges [1, 10**12] do not enumerate.

## Non-blocking notes

- `validate_all` calls `module.schema_errors(doc)` outside a try block. The fuzz found no raise, so this is a spec-wording point only, not a defect. Do not harden further per the STOP RULE.
- `_normalize` in aggregate.py is unused (style only).
- Deferred items N9-N15 (per the review prompt) were not reported.
- The `malformed structure` sentinel is by design and was not reported.

## Verdict

Two Class 1 defects in aggregate.py (X1 kind-awareness missing; X2 still enforced after removal) plus two stale tests that encode the removed rule. Fix A1 and A2 and re-run the stage1 test suite.

## Verdict: FIX FIRST
