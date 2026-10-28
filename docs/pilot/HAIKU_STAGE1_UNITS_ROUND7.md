# Stage 1 unit modules: Round 7 review (read-only)

Scope: `scripts/pipeline/stage1/{story_map,coverage,scenes,shots,briefs,looks,voices,sounds,questions}.py`, `tests/test_stage1_<unit>.py`, against `docs/pilot/nemotron_specs/unit_<unit>.md`, `stage1_base.json`, `STAGE1_RULES.md`.

Evidence:
- `uv run pytest -q --tb=short tests/test_stage1_*.py`: **426 passed** (the brief said 460; the current count is 426).
- Round 6 findings reproduced (status table below).
- Mutation check (scratch copy, project untouched): `shots.py` line 150 changed from `key = scene_id` to `key = f"S{scene_num}"`; `test_consecutive_grouped_by_scene_id` still passes.
- Scope limit: the spec-by-spec audit was done for shots and voices. The other seven units were checked only by the existing suite and the Round 6 notes; "none" for those means no defect was found in the checks run, not a full audit.
- No print, env, key or secret handling found in any module or test.

## Verdict: FIX FIRST

---

## Round 6 status

| Unit | Round 6 finding | Status (Round 7) |
|---|---|---|
| shots (Haiku 1) | `test_stage1_shots.py:400-401` asserts "shot id prefix does not match scene_id" | FIXED: lines 400-403 assert `e.startswith("S1-1:")` and `e.startswith("S2-1:")` |
| shots (Codex 1) | `test_stage1_shots.py:250` missing-scene test also fires a prefix error | FIXED: lines 248-252 use shot `S9-1` with `scene_id` `S9`; the only error is the missing-scene one |
| shots (Codex 2) | prefix-mismatch assertion not quoted in spec; grouping not isolated | Wording FIXED. Grouping isolation NOT FIXED: see shots 1 below |
| voices (Haiku 1, Codex 1) | collateral tuple rows with voice_key `other` not in `saved_voices` | FIXED: those rows are gone; isolated tests at lines 265-304 use `saved_voices["other"]` and fail without the rule (verified by reading: empty `errs` fails `any(...)`) |
| voices (Haiku 2, Codex 2) | isolated cases assert "recurring character listed twice" (not quoted in spec) | FIXED: lines 283 and 304 assert only `"other_char" in e` |

---

## story_map

none

## coverage

none

## scenes

none

## shots

1. `tests/test_stage1_shots.py:405-416` (class 3, a test that can never fail for the rule it names): `test_consecutive_grouped_by_scene_id` says it isolates grouping by `scene_id`. Its fixture is prefix-consistent (`S1-1`, `S1-3` with scene `S1`; `S2-1` with scene `S2`), so grouping by the shot-id prefix gives the same groups. Verified: with `shots.py:150` changed to `key = f"S{scene_num}"`, the test still passes (`S1: shot numbers not consecutive from 1` is produced under both rules). Fix: make the fixture prefix-inconsistent so the two groupings differ, for example set `shots[1]` to `shot_id "S1-3"` with `scene_id "S2"`, and assert that the gap error names `S2`, not `S1`: `assert any(e.startswith("S2:") and "not consecutive" in e for e in errs)` and `assert not any(e.startswith("S1:") and "not consecutive" in e for e in errs)`. Delete the comment's false claim ("If grouped by prefix, S1 would have 1,2,3") and replace it with what the test now checks. Then re-run the mutant to confirm it fails.

## briefs

none

## looks

none

## voices

none

## sounds

none

## questions

none

---

## Defects per unit (Round 7)

| Unit | Defects |
|---|---|
| story_map | 0 |
| coverage | 0 |
| scenes | 0 |
| shots | 1 |
| briefs | 0 |
| looks | 0 |
| voices | 0 |
| sounds | 0 |
| questions | 0 |
| **Total** | **1** |
