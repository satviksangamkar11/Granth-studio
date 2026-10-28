# Stage 1 unit modules: Round 8 review (read-only)

Scope: `scripts/pipeline/stage1/{story_map,coverage,scenes,shots,briefs,looks,voices,sounds,questions}.py`, `tests/test_stage1_<unit>.py`, against `docs/pilot/nemotron_specs/unit_<unit>.md`, `stage1_base.json`, `STAGE1_RULES.md`.

Evidence:
- `uv run pytest -q --tb=short tests/test_stage1_*.py`: 426 passed.
- Round 7 finding reproduced in memory (no file written): `shots.py` line 150 changed from `key = scene_id` to `key = f"S{scene_num}"`. The test assertion `any(e.startswith("S1:") ...)` in `test_consecutive_grouped_by_scene_id` is then False, so the test fails. FIXED.
- Briefs scene-existence rule removed in memory (`briefs.py:159-160`): the row at `test_stage1_briefs.py:298-305` still passes (see briefs 1).
- Fuzzed `scenes`, `coverage`, `looks`, `questions` `validate` with odd document values (None, bool, float, str, list, dict, unhashable items). No exception escapes for any document value.
- Grep: no print, environment read, key, token or secret handling in any module or test.

## Round 7 status

| Unit | Round 7 finding | Status (Round 8) |
|---|---|---|
| shots | `test_consecutive_grouped_by_scene_id` cannot fail for grouping by scene_id | FIXED (verified by in-memory mutant) |

## story_map

none

## coverage

none

(Not counted: `coverage.validate` raises AttributeError when `ctx` itself is None. `ctx` is not a document, and the spec defines it as a dict.)

## scenes

1. `tests/test_stage1_scenes.py:225,227,229,232,235,238,241,244,247` (class 4): the tests assert `not any("malformed structure" in e ...)`. The spec does not quote that wording. Fix: in each of these nine lines remove the clause `and not any("malformed structure" in e for e in errs)` and keep `isinstance(errs, list)`.

(Not counted: `scenes.validate` has no catch-all, but no document value raises in fuzzing. A huge `ovi_range` makes `range(lo, hi+1)` slow, which is out of class.)

## shots

1. `tests/test_stage1_shots.py:310,314,318,322,327,332,337,342,359,367,375` (class 4): the tests assert `not any("malformed structure" in e ...)`. The spec does not quote that wording. Fix: delete these eleven `assert not any("malformed structure" in e for e in errs)` lines; the `isinstance(errs, list)` assertions remain.

## briefs

1. `tests/test_stage1_briefs.py:298-305`, row "scene does not exist" in `SEMANTIC_CASES` (class 3, a test that passes for a collateral reason). With the scene-existence check removed (`briefs.py:159-160`), the row still passes because `s99_test: shot_ids exist and belong to the same scene` is produced (shot `S1-2` belongs to S1). The isolated test at `test_stage1_briefs.py:406-415` does fail without the rule, so the rule is covered; this row is not. Fix: delete rows lines 298-305.
2. `tests/test_stage1_briefs.py:340,350,360,367,385` (class 4): the tests assert `not any("malformed structure" in e ...)`. The spec does not quote that wording. Fix: delete these five `assert not any("malformed structure" in e for e in errs)` lines.

## looks

1. `tests/test_stage1_looks.py:178-179` (class 4): the test asserts `not any("malformed structure" in e for e in result)`, wording the spec does not quote. Fix: delete lines 178 and 179; keep `assert isinstance(result, list)` on line 177.

## voices

none

## sounds

1. `tests/test_stage1_sounds.py:235,241,247,253,259,264,269,274,281,288,296` (class 4): the tests assert `not any("malformed structure" in e ...)`. The spec does not quote that wording. Fix: in each line remove the clause `and not any("malformed structure" in e for e in errs)`; keep `isinstance(errs, list)` and the `"cue[0]"` checks on lines 241, 247, 253, 259.

## questions

none

---

## Defects per unit (Round 8)

| Unit | Defects |
|---|---|
| story_map | 0 |
| coverage | 0 |
| scenes | 1 |
| shots | 1 |
| briefs | 2 |
| looks | 1 |
| voices | 0 |
| sounds | 1 |
| questions | 0 |
| **Total** | **6** |

## Verdict: FIX FIRST
