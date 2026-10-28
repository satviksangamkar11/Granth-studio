# HAIKU STAGE 1 FINAL review (read-only)

Scope: `scripts/pipeline/stage1/aggregate.py` (new, with `tests/test_stage1_aggregate.py`), `voices.py` (`reason` field), `scenes.py` (gap walk, total gap-message cap, bool ovi exclusion, closures), plus the full stage1 unit set.

Evidence:
- `uv run pytest -q --tb=short tests/test_stage1_*.py`: 544 passed, 0 failed.
- In-memory probes of `validate_all` against `docs/pilot/nemotron_specs/stage1_base.json` (base returns `[]`).

## Per unit

### aggregate (1 BLOCKING defect)
1. `scripts/pipeline/stage1/aggregate.py:122-274` (X1 to X8 blocks, no try/except). `validate_all` raises instead of returning an error when `ctx` has a JSON-shaped value of the wrong type. Reproduced:
   - X3: `ctx["unfilmed_ovis"] = [[1]]` raises `TypeError: unhashable type: 'list'` (line 152). `ctx["unfilmed_ovis"] = 5` raises `TypeError: 'int' object is not iterable`.
   - X7: `ctx["series_voices"] = ["gajanan_maharaj"]` with a cast entry for `gajanan_maharaj` raises `TypeError: list indices must be integers` (line 255).
   - X8: `ctx["script_texts"] = 5` or `None` raises `TypeError` (line 263).

   Spec requires that `validate_all` never raise, with any unexpected exception becoming `aggregate: internal error in <step>`.
   Exact fix: wrap the body of each cross-rule block (X1 through X8) in `try: ... except Exception: errors.append("aggregate: internal error in X<n>")`. Equivalently, guard the ctx reads (`isinstance` checks on `unfilmed_ovis`, `series_voices` as dict, `script_texts` as list) before use. The try/except form is the smaller diff.

   No test covers this; add one test that passes `ctx` with `unfilmed_ovis: [[1]]` and asserts a return list with no exception.

### story_map, coverage, scenes, shots, briefs, looks, voices, sounds, questions
none

## Verified cross rules (aggregate)
- X1: fires for ovi 3 when E1 is [4,5] (and for every STORY/TEACHING ovi when events is `[]`). Base returns `[]`.
- X2: fires for a STORY ovi with PROPOSE_OMISSION. X4 does not fire for it.
- X3: fires in both directions (proposed but not approved; approved but no proposal).
- X4: fires for a VISUALISED ovi in no shot and for a non-omitted ovi in no scene.
- X5: fires for key ovi 10 of E2 (in no scene).
- X6: fires without a question on S2 and is valid with a question whose scene_id is S2.
- X7: fires for a RECURRING mismatch and for NEW_PROPOSED on a series character; valid on match.
- X8: fires for a 25-plus-character script line copied into `scenes/0/goal`; does not fire for a 7-character text.
- Huge range `[1, 10**12]` in scenes: returns in 0.002 s, no enumeration.
- Scenes gap walk: chapter `{1-4,6-9}` with S1 `[1,4]`, S2 `[6,9]` gives no false error; chapter `{1,2,4}` with S1 `[1,4]` reports ovi 3.
- Robustness: `docs={}` gives nine `document missing`; `docs=None` and `ctx=None` give the single documented message and continue; a list document is reported as missing.

## Non-blocking notes
- X3 test isolation: the spec's X3 example uses ovi 8, which is TEACHING, so X2 also fires. The code is correct; the test should use a NARRATED ovi outside story/teaching types to isolate X3.
- Unit-level messages (for example `S1: ovi 3 is unfilmed but inside the range`) appear alongside X2 and X3 in the same run. This is expected, not a defect.
- `series_voices` as a non-dict string does not raise (returns `[]`) only by accident; the X7 fix above covers it.
- Voices `reason` requirement for NEW_PROPOSED is enforced by the schema `if/then`; the unit `validate` does not re-check it. Not verified beyond the passing tests.

## Verdict
Aggregate has one BLOCKING defect (never-raise contract broken for ctx inputs). All other units: none.

## Verdict: FIX FIRST
