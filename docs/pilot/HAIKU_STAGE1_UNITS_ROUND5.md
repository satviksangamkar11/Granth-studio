# Stage 1 unit modules: Round 5 review (read-only)

Scope: `scripts/pipeline/stage1/{story_map,coverage,scenes,shots,briefs,looks,voices,sounds,questions}.py`, `tests/test_stage1_<unit>.py`, against `docs/pilot/nemotron_specs/unit_<unit>.md`, `stage1_base.json`, `STAGE1_RULES.md`.

Evidence:
- `uv run pytest -q tests/test_stage1_*.py` (nine files): **424 passed**.
- Mutation check: 54 single-rule mutations were applied to copies of the modules in the scratchpad (project files untouched) and each unit's test file was run against them. 53 were killed. One survived: the voices rule "a character already RECURRING must not be listed twice" (see voices 2 and 3).
- Round 4 findings were reproduced in memory where applicable (coverage `covered_by "²"`, briefs missing-scene message, voices mixed-status cast).
- No print, env, key or secret handling was found in any module or test.
- Not counted (out of the five classes): `coverage.validate` and `scenes.validate` raise TypeError when a ctx list is None (e.g. `chapter_ovis: None`); ctx is not document data. Verified for coverage.
- Not counted, observation: `scenes.py:148-149` expands `range(lo, hi+1)` for every scene, and `scenes.py:216-218` emits one message per covered ovi outside the chapter. `ovi_range [1, 5000000]` took 1.0 s and produced 4,999,997 messages. No raise was reproduced; scenes.validate has no catch-all.
- Not counted, observation: in briefs, a non-object entry in `people` raises inside the try block, so the whole document returns only `briefs: malformed structure` and all other semantic errors are hidden.

## Verdict: FIX FIRST

---

## Round 4 status

| Unit | Round 4 finding | Status (Round 5) |
|---|---|---|
| coverage | `covered_by "²"` raised ValueError | FIXED (reproduced: returns the covered_by error, no raise) |
| scenes | duplicate-scene test passes without duplicate detection | FIXED (mutation of duplicate-id check now fails the test) |
| shots | class enum row only exercises null branch | FIXED (`test_need_new_class_enum` uses NEED_NEW with schema_errors) |
| shots | test asserts "not in scene" (not quoted in spec) | FIXED (no such assertion remains in the test file) |
| shots | catch-all assertions only check for a list | FIXED (odd-data tests assert no "malformed structure") |
| briefs | missing-scene message says "scene exists" | FIXED (reproduced: `s99_x: scene S99 does not exist`) |
| looks | no odd-data test | FIXED (`test_validate_odd_doc_no_raise`, ODD_DOCS list) |
| voices | RECURRING + NEW_PROPOSED not flagged when not speaking | Code FIXED (reproduced: `gajanan_maharaj: recurring character listed twice`). The test for it is not isolated: see voices 2 and 3 |

---

## story_map

none.

## coverage

none.

## scenes

none.

## shots

none.

## briefs

1. `tests/test_stage1_briefs.py:423` (class 4): `assert any("malformed structure" in e for e in errs)` asserts wording the spec does not quote (grep of `unit_briefs.md` finds no "malformed"). Fix: `assert isinstance(errs, list) and len(errs) >= 1`.

## looks

none.

## voices

1. `tests/test_stage1_voices.py:209-214` (class 3): the row labelled "distinct voice_keys to isolate rule" reuses the keys `narrator` and `gajanan`, so `other_char` also triggers "voice key shared with another character" (`voices.py:145`). Verified: with `voices.py:113-114` removed, this row still passes on the shared-key message (the row asserts keyword `other_char`). Fix: give `other_char` its own key. Verified fix: add `"other": "ZZZZZZZZZZ"` to a copy of `ctx["saved_voices"]`, and use `voice_key "other"`, `voice_id "ZZZZZZZZZZ"` for both `other_char` entries. The original code then returns exactly `["other_char: recurring character listed twice"]`, and with the rule removed it returns `[]`, so the test becomes isolated. Because the row's keyword is in the tuple, this needs a standalone test function, not a new tuple row.
2. `tests/test_stage1_voices.py:235-240` (class 3): the Round 4 test for "non-speaking RECURRING + NEW_PROPOSED" has the same collateral. With the rule removed it still returns `other_char: voice key shared with another character`. Fix as in item 1 (distinct key `other` for both `other_char` entries, ctx `saved_voices` extended), and assert that the only message is `other_char: recurring character listed twice`.

## sounds

none.

## questions

none.

---

## Defects per unit (Round 5)

| Unit | Defects |
|---|---|
| story_map | 0 |
| coverage | 0 |
| scenes | 0 |
| shots | 0 |
| briefs | 1 |
| looks | 0 |
| voices | 2 |
| sounds | 0 |
| questions | 0 |
| **Total** | **3** |
