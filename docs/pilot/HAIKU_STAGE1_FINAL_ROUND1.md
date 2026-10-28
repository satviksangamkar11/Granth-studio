# Haiku final review: Stage 1 unit modules (read-only)

Scope: `scripts/pipeline/stage1/{story_map,coverage,scenes,shots,briefs,looks,voices,sounds,questions}.py`, tests `tests/test_stage1_*.py`, specs `docs/pilot/nemotron_specs/unit_<unit>.md`, `stage1_base.json`, `docs/pilot/STAGE1_RULES.md`.

## Evidence
- `uv run pytest -q --tb=short tests/test_stage1_*.py`: 463 passed (per-unit counts match `docs/pilot/TEST_RUN_STAGE1.txt`).
- In-memory fuzz (no files written): about 430,000 calls mutating the nine base documents and the ctx dict, with random JSON-shaped values and special numbers (NaN, Infinity, huge ints, bools, zero, negative). Raises were found only in coverage and scenes, and only in the two cases below.
- Class 1 (spec rules): every semantic rule in the nine specs was checked against its module. No rule is missing or wrong.
- Class 3 (rules without a failing test): every semantic rule has at least one test with a matching assertion. Some assertions are weak (see notes), but none is absent.
- The `malformed structure` sentinel is treated as the project design rule and is not reported.

## Per-unit BLOCKING defects

### story_map
none

### coverage
1. `scripts/pipeline/stage1/coverage.py:69-141` (`validate`): no catch-all, unlike story_map, shots, briefs, sounds and voices. It raises on JSON-shaped ctx values (CLASS 2).
   - Verified: `validate(1, base coverage, base docs, None)` raises `AttributeError: 'NoneType' object has no attribute 'get'` (line 84).
   - Verified: ctx `chapter_ovis=[[1]]` raises `TypeError: unhashable type: 'list'` (line 85).
   - Exact fix: rename the body to `_validate_impl` and add `validate(adhyay, doc, docs, ctx)` that does `try: return _validate_impl(...)` and on `(TypeError, AttributeError, KeyError, ValueError, IndexError)` returns `["coverage: malformed structure"]`, as the sibling units do. Add tests for `ctx=None` and `chapter_ovis=[[1]]` asserting no exception.

### scenes
1. `scripts/pipeline/stage1/scenes.py:228-229` (`validate`): no catch-all. It raises on JSON-shaped ctx values (CLASS 2).
   - Verified: ctx `None` raises `AttributeError` (line 109). ctx `script_line_ids=5` raises `TypeError: 'int' object is not iterable` (line 109).
   - Exact fix: same wrapper as coverage item 1, returning `["scenes: malformed structure"]`, plus no-raise tests for these two ctx values.
2. `scripts/pipeline/stage1/scenes.py:148-149` (`for ovi in range(lo, hi + 1): all_covered_ovis.add(ovi)`): the schema sets no maximum on `ovi_range` values, so a document can force enumeration of any span (CLASS 2: the call does not finish or fails with MemoryError).
   - Verified: `[1, 2000000]` takes 0.36 s. `[1, 10**7]` takes 1.7 s and returns 9,999,992 messages. A span of `10**30` did not finish; the probe was stopped after it hung (not a completed run, so it is stated as unverified to completion).
   - Exact fix: do not enumerate the range. Either reject any span wider than the chapter (for example `if hi - lo > 1000: errors.append(f"{sid}: ovi_range too wide"); continue`), or compute coverage by checking only each chapter ovi against the ranges, and emit one message per out-of-chapter range instead of one per ovi. The second option changes the "ovi 10" message, so update `tests/test_stage1_scenes.py` (the `ovi outside chapter` row, around line 232) with it.

### shots
none

### briefs
none

### looks
none

### voices
none

### sounds
none

### questions
none

## Non-blocking notes
- `sounds.py:64`: ctx `sound_ids` is accepted only as a list or set. A tuple or frozenset becomes an empty set and produces false "not in sound_ids" errors. `looks.py` `_as_set` handles these types. Low risk, since ctx comes from JSON.
- `briefs.py:171-174`: a non-object entry in `people` makes the loop raise, and the catch-all returns only the sentinel. The schema already rejects such entries, so this is not a defect in the validate path, but the item is not reported by name.
- Schema bounds without a test: `scenes` `ovi_range` has no maximum (root of scenes item 2); `shots` `ovi_ids` has no maximum. Enum values are present and tested.
- Weak test assertions (rule tests exist): `test_scenes` "unfilmed inside range" and "ovi not covered" match keywords `S1` and `9`, which appear in many messages. `test_briefs` `test_validate_malformed_structure_returns_error` only asserts `len(errs) >= 1`.
- `looks.py` and `questions.py` have no catch-all, but the fuzz found no raises in either.
- `sounds.py`: the rule "a non-NEED_NEW cue must not carry sound_prompt" is enforced by the schema only, as the spec says.

Two units have CLASS 2 blocking defects (coverage 1, scenes 2). Fix those and add the no-raise tests, then re-run the stage1 suites.

## Verdict: FIX FIRST
