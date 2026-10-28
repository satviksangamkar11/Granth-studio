# Haiku final read-only review: Stage 1 units (scenes focus)

Scope: `scripts/pipeline/stage1/{story_map,coverage,scenes,shots,briefs,looks,voices,sounds,questions}.py`, tests `tests/test_stage1_*.py`, against `docs/pilot/REVIEW_PROMPT_STAGE1_FINAL.md` STOP RULE. Evidence: `docs/pilot/TEST_RUN_STAGE1.txt` plus my own run of `uv run pytest -q --tb=short tests/test_stage1_*.py` (509 passed, 0 failed). `malformed structure` sentinel treated as the project-defined design rule, not reported.

## Scenes: re-verification of prior findings (in-memory checks)

- Gap-walk false error fixed. Chapter {1-4,6-9}, S1 [1,4], S2 [6,9] returns `[]`. No "ovi 5" error.
- Real gaps still reported. Chapter {1..9}, S1 [1,3], S2 [6,9] reports `ovi 4` and `ovi 5: not covered by any scene`. Chapter {1,2,3,6,7,8,9}, S1 [1,9] reports `ovi 4` and `ovi 5: outside chapter ovis`.
- Gap at start, end, and before/after the inside ovis are covered by the existing gap tests (`test_validate_gap_at_start_of_range`, `..._at_end_of_range`, `..._before_first_inside`, `..._after_last_inside`), all passing.
- Huge ranges return immediately. [1, 10**12] with chapter {1,2,3} gives `extends above chapter ovis` in 0.0 s. [-10**12, 10**12] with chapter {1,5,10**12} returns in 0.0 s. Sparse chapter {1, 10**12} with range [1, 10**12] gives one summary message `contains 999999999998 ovis outside chapter ovis (gap)` in 0.0 s.
- Unfilmed ovi inside a range is reported (`S1: ovi 3 is unfilmed but inside the range`). Unfilmed ovi outside every range is not reported (correct).
- Overlap check catches non-adjacent overlaps (S1 [1,10] vs S2 [2,3] vs S3 [4,5] reports `S1: ovi_range overlaps with S2`). Consecutive-pair check is sufficient after sorting by lo.
- Every semantic rule of the unit has a parametrized failing test in `test_semantic_errors` (duplicate id, lo>hi, overlap, uncovered chapter ovi, unfilmed inside range, outside chapter, turn ovi outside range, unknown line, duplicate line, script order, core line missing, discourse none, story with treatment, adhyay mismatch).

## Class 2 (validate or schema_errors raises) check

- Targeted odd inputs (None, str, int, bool, float, list/dict nesting, unhashable scene_id and line_id, non-int bounds, non-int chapter ovis, ctx of None/str/list/dict forms, docs of None): 0 raises from `validate` or `schema_errors`.
- Random structured fuzz, 20000 iterations on scenes: 0 raises.
- Shallow random fuzz (3000 iterations per unit) on all nine units' `validate` and `schema_errors`: 0 raises.

## Per unit BLOCKING defects

- story_map: none
- coverage: none
- scenes: none
- shots: none
- briefs: none
- looks: none
- voices: none
- sounds: none
- questions: none

## Non-blocking notes

- `scripts/pipeline/stage1/scenes.py:282-283`: the per-gap cap of 1000 messages does not cap the total. A sparse chapter of 5000 ovis spaced 1001 apart against one range produces 4,999,000 messages in about 0.58 s. Nothing raises and the case is unrealistic, so this is not blocking and no hardening is recommended.
- `scripts/pipeline/stage1/scenes.py:137`: `isinstance(True, int)` lets a bool chapter ovi through the semantic layer. The schema rejects bools for integer fields, so no defect in practice.
- Enum values and numeric bounds beyond `ovi_range` minimum are only partly tested in scenes (for example `maxItems` and `maximum` for adhyay are not tested). Per STOP RULE these are notes, not defects.

## Verdict

The scenes fix holds, real gaps are still reported, huge ranges return quickly, and no CLASS 1, 2 or 3 defect was verified in any unit.

## Verdict: READY
