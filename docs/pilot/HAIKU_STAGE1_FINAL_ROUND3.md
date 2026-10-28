# Stage 1 FINAL read-only review (round 3, scenes rewrite)

Reviewer: Haiku 5.5, read-only. Only this file was written.

## Checks performed
- `uv run pytest -q tests/test_stage1_*.py`: 502 passed, 0 failed.
- Codex round 2 Class 1 finding A (chapter gap inside a range missed, e.g. `chapter_ovis = [1,2,3,4,5,6,8,9]` with S2 covering 7): FIXED. Gap check in `scenes.py` (lines 262-297) reports `ovi 7: outside chapter ovis`. Confirmed by direct run.
- Codex round 2 Class 1 finding B (unfilmed ovi inside a range not reported): FIXED. `scenes.py` lines 236-243 report `S2: ovi 10 is unfilmed but inside the range`. Confirmed by direct run.
- Huge ovi_range, in memory, timed: `[1, 10**12]` returns in under 1 ms with 2 messages; `[-10**12, 10**12]` returns in under 1 ms with 3 messages; `[1, 10**100]` returns in under 1 ms. Sparse chapter `{1, 10**12}` with range `[1, 10**12]` returns one gap message, no enumeration. FIXED.
- Class 2 fuzz (3000 random JSON-shaped inputs for `scenes.validate` and `scenes.schema_errors`, including odd ctx values): 0 raises. Not fuzzed for the other eight units in this round.

## Verified defects

### scenes
1. BLOCKING (Class 1, spec rule implemented wrongly, false error on a valid document). `scripts/pipeline/stage1/scenes.py:277-278` (the `gap_start = prev + 1` line inside the gap walk) and `:291` (the tail gap). The walk starts from `prev = check_lo - 1`, but chapter ovis below `check_lo` update `prev` to values below `check_lo`. So a gap that lies outside the scene range is reported against that range.
   - Repro (verified, in memory): `chapter_ovis = {1,2,3,4,6,7,8,9}`, S1 `ovi_range = [1,4]`, S2 `ovi_range = [6,9]`, rest of base unchanged. Result: `['ovi 5: outside chapter ovis']`. Expected: `[]`, because ovi 5 is in no scene range and the spec only errors on ovis inside a range.
   - Exact fix: at line 277 use `gap_start = max(prev + 1, check_lo)`. The tail branch at line 289-291 needs no change because `prev` is then at least `check_lo - 1` and the walk now clamps. Verified in memory: the valid case returns `[]`, and a true gap inside a range (`[1,5]`) is still reported.
   - Test gap: no test covers a gap outside a range. Add one with the repro above, expecting `[]`.

## Verdict per unit (BLOCKING count)
- story_map: 0 (tests pass; not re-audited this round)
- coverage: 0 (tests pass; not re-audited this round)
- scenes: 1
- shots: 0 (tests pass; not re-audited this round)
- briefs: 0 (tests pass; not re-audited this round)
- looks: 0 (tests pass; not re-audited this round)
- voices: 0 (tests pass; not re-audited this round)
- sounds: 0 (tests pass; not re-audited this round)
- questions: 0 (tests pass; not re-audited this round)

## Non-blocking notes
- Performance: `scenes.validate` is O(ranges x chapter_ovis). Fine for chapter sizes in practice. Gap messages can be many (up to 1000 per gap, one message per gap for larger gaps).
- Duplicate gap messages are possible when the same gap is reached from two ranges. After the fix above this should not occur for gaps outside ranges.
- Schema enum or numeric bound gaps in other units: not blockers per the STOP RULE.
- The `malformed structure` sentinel is used as designed and was not reported.

## Verdict
Scenes has one BLOCKING Class 1 defect (false error on a valid document). Other units showed no blocking issue in this round, but they were not re-audited beyond the test run.

## Verdict: FIX FIRST
