# Stage 1 unit modules: final read-only review (round 2)

Scope: `scripts/pipeline/stage1/{story_map,coverage,scenes,shots,briefs,looks,voices,sounds,questions}.py`, tests `tests/test_stage1_<unit>.py`, specs `docs/pilot/nemotron_specs/unit_<unit>.md`, `docs/pilot/STAGE1_RULES.md`, `stage1_base.json`. No files were edited.

## Evidence
- `uv run pytest -q --tb=short tests/test_stage1_*.py`: 500 passed in this review run (0.61 s). `docs/pilot/TEST_RUN_STAGE1.txt` records the earlier external run with the same per-unit suites passing.
- In-memory checks (no files written): the round-1 blocking inputs were re-run directly against the current code. Every case returned a value and none raised.

## Re-verification of round-1 blocking findings (`HAIKU_STAGE1_FINAL_ROUND1.md`)

| # | Finding | Status | Evidence |
|---|---------|--------|----------|
| 1 | coverage: no catch-all, raises on ctx `None` | FIXED | `coverage.py:107-108` treats non-dict ctx as `{}`; `coverage.py:169-176` wraps the body in `try` with the `malformed structure` sentinel. `validate(1, base, {}, None)` returns without raising. |
| 2 | coverage: raises on `chapter_ovis=[[1]]` | FIXED | `coverage.py:61-73` `_safe_iterable_to_set` skips unhashable items. `chapter_ovis=[[1]]` returns without raising. |
| 3 | scenes: no catch-all, raises on ctx `None` | FIXED | `scenes.py:266-267` normalises ctx; `scenes.py:263-272` wraps the body with the sentinel. |
| 4 | scenes: raises on `script_line_ids=5` | FIXED | `scenes.py:97-108` `_as_usable_set` and `_as_usable_list` return empty collections for non-collections. `script_line_ids=5` returns without raising. |
| 5 | scenes: `ovi_range` enumeration (`range(lo, hi+1)`) | FIXED | `scenes.py:217-223` now checks each chapter ovi against each range (`lo <= ovi <= hi`). No range is enumerated. `ovi_range=[1, 10**30]` returned in 0.00 s with `S1: ovi_range extends above chapter ovis`. |

All three round-1 blocking defect groups (coverage 1, scenes 1, scenes 2) are FIXED. The round-1 requirement to add no-raise tests is not fully met for `scenes` `ovi_range` and `coverage` ctx `None`. Those tests were not found by name in the suite, so this is listed as a non-blocking note.

## Per-unit BLOCKING defects
Each unit was checked for: (a) any `validate` or `schema_errors` path that can raise on JSON-shaped input (CLASS 2), (b) any spec rule not implemented or implemented wrongly (CLASS 1), (c) any semantic rule with no failing test (CLASS 3).

### story_map
none

### coverage
none

### scenes
none

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

Notes on the no-raise checks for units without a catch-all:
- `questions.validate` (`questions.py:42-91`): every access is guarded by an `isinstance` check (dict, list, str). No raising path was found.
- `looks.validate` (`looks.py:63-125`): the only operations that can raise on unhashable values (`in chapter_ovis`, `set(...)`) are wrapped in `try/except TypeError`. No raising path was found.

## Non-blocking notes
- `coverage` and `scenes`: no test named for the `ctx=None` or huge-span inputs. The behaviour is correct, but a regression test would protect it. Same for `chapter_ovis=[[1]]` in `coverage`.
- `scenes.py` `ovi_range`: the schema sets no maximum. Semantics are now bounded by the chapter check, so the schema bound is a style or schema-tightening item only.
- `shots.py`: schema `ovi_ids` has no maximum. Enum values are present and tested.
- `sounds.py:64`: ctx `sound_ids` is accepted only as a list or set. A tuple or frozenset becomes an empty set and yields false "not in sound_ids" errors. `looks.py` `_as_set` handles these types. Low risk, since ctx comes from JSON.
- `briefs.py:171-174`: a non-object entry in `people` makes the loop raise, and the catch-all returns only the sentinel. The schema rejects such entries first, so this is not a defect.
- Weak test assertions (rule tests exist): `test_scenes` "unfilmed inside range" and "ovi not covered" match on keywords `S1` and `9`. `test_briefs` `test_validate_malformed_structure_returns_error` only asserts `len(errs) >= 1`.
- `looks.py` and `questions.py` have no catch-all. They pass the checks above, but adding the same wrapper as the sibling units would make the design uniform.
- `sounds.py`: the rule "a non-NEED_NEW cue must not carry sound_prompt" is enforced by the schema only, as the spec says. No test ties it to `validate`.
- The `malformed structure` sentinel is the project design rule and was not reported.

## Verdict
No verified CLASS 1, CLASS 2 or CLASS 3 blocking defect remains in any of the nine units. All round-1 blocking findings are FIXED.

## Verdict: READY
