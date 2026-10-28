# Stage 1 unit modules: Round 6 review (read-only)

Scope: `scripts/pipeline/stage1/{story_map,coverage,scenes,shots,briefs,looks,voices,sounds,questions}.py`, `tests/test_stage1_<unit>.py`, against `docs/pilot/nemotron_specs/unit_<unit>.md`, `stage1_base.json`, `STAGE1_RULES.md`.

Evidence:
- `uv run pytest -q --tb=short tests/test_stage1_*.py`: **427 passed**.
- Round 5 findings reproduced (see status table).
- Fuzz (about 3,000 random odd-document mutations per unit, document-only, ctx unchanged): no raise from `schema_errors` or `validate` in story_map, shots, briefs, looks, voices, sounds, questions. coverage and scenes: 0 raises from document-only mutations (5,000 each).
- Not counted (ctx is not document data, per Round 5): coverage and scenes raise TypeError when a ctx list is a non-iterable value (e.g. `chapter_ovis: None`).
- Scope limit: the spec-by-spec review of story_map, coverage, scenes, looks, sounds and questions was not repeated in full in this round. Their "none" entries mean no defect was found in the checks run, not a complete audit.
- No print, env, key or secret handling found in any module or test.

## Verdict: FIX FIRST

---

## Round 5 status

| Unit | Round 5 finding | Status (Round 6) |
|---|---|---|
| briefs | `test_stage1_briefs.py:423` asserts "malformed structure" (not quoted in spec) | FIXED (line 423 is now `assert len(errs) >= 1`) |
| shots | consecutiveness grouped by shot_id prefix, not scene_id; swap of S1-1 and S2-1 returns `[]` | FIXED (`shots.py:133-153` groups by `scene_id` and rejects prefix mismatch; swap now returns "shot id prefix does not match scene_id" for S1-1 and S2-1) |
| voices | row at `test_stage1_voices.py:208-214` shares key with `gajanan` so the rule is not isolated | STILL OPEN (see voices 1). Standalone isolated tests were added (`test_validate_recurring_duplicate_isolated`, `test_validate_recurring_newproposed_duplicate_isolated`), so the rule now has an isolated test; the tuple rows are still collateral |
| voices | row at `test_stage1_voices.py:234-240` same collateral | STILL OPEN (see voices 2) |

---

## story_map

none found in the checks run.

## coverage

none found in the checks run.

## scenes

none found in the checks run.

## shots

1. `tests/test_stage1_shots.py:400-401` (class 4): asserts "shot id prefix does not match scene_id". This wording is not in `unit_shots.md` (grep finds no "prefix" or "does not match" except the adhyay line). The prefix rule itself is also not in the spec's rule 6 (it is an extra check added in Round 5). Fix: keep the check, but assert only the item id per the spec convention: `assert any(e.startswith("S1-1:") for e in errs)` and `assert any(e.startswith("S2-1:") for e in errs)`.

## briefs

none found in the checks run.

## looks

none found in the checks run.

## voices

1. `tests/test_stage1_voices.py:208-214` (class 3): the tuple row "Recurring character outside speaking_characters listed twice" uses voice_key `other`, which is not in `saved_voices`. Verified: with the recurring-duplicate rule disabled (`voices.py` line with `if len(entries) > 1 and any(e.get("status") == "RECURRING" ...)` replaced by `if False:`), this row still returns `other_char: voice not in the saved cast`, and the row passes because the keyword `other_char` matches. Fix: delete this tuple row (it is covered by `test_validate_recurring_duplicate_isolated`), or add `"other": "ZZZZZZZZZZ"` to the ctx used for that row and assert the exact list `["other_char: recurring character listed twice"]`.
2. `tests/test_stage1_voices.py:234-240` (class 3): the tuple row "Non-speaking character with RECURRING + NEW_PROPOSED" has the same collateral. Verified: with the same rule disabled it returns `['other_char: voice not in the saved cast', 'other_char: voice not in the saved cast']`, and the row still passes. Fix: delete this tuple row (it is covered by `test_validate_recurring_newproposed_duplicate_isolated`).

## sounds

none found in the checks run.

## questions

none found in the checks run.

---

## Defects per unit (Round 6)

| Unit | Defects |
|---|---|
| story_map | 0 |
| coverage | 0 |
| scenes | 0 |
| shots | 1 |
| briefs | 0 |
| looks | 0 |
| voices | 2 |
| sounds | 0 |
| questions | 0 |
| **Total** | **3** |
