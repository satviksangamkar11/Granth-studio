# Stage 1 unit modules: Round 3 review (read-only)

Scope: `scripts/pipeline/stage1/{story_map,coverage,scenes,shots,briefs,looks,voices,sounds,questions}.py`, `tests/test_stage1_<unit>.py`, against `docs/pilot/nemotron_specs/unit_<unit>.md`, `stage1_base.json`, `STAGE1_RULES.md`.

Evidence: `uv run pytest -q --tb=short tests/test_stage1_*.py` gives **418 passed**. Every defect below was checked by calling the module in memory with a small input (no project file written, no network). Fuzzing: every leaf of every document and every ctx key was replaced with 13 odd values (None, int, str, list, dict, bool, nested lists), and each validate/schema_errors call was made with empty and None docs/ctx. The only raises were from `coverage.validate` when a ctx list (`script_line_ids`, `chapter_ovis`, `unfilmed_ovis`) was None or an int. That is ctx, not document data, so it is not counted. No print, env, key or secret handling was found in any module or test.

## Verdict: FIX FIRST

---

## Round 2 findings: status

| Unit | Round 2 finding | Status |
|---|---|---|
| story_map | 1 `ovi_types` not type-checked | FIXED (story_map.py:84-85) |
| story_map | 2 `events` not type-checked | FIXED (story_map.py:108-110) |
| story_map | 3 `key_ovis` not type-checked | FIXED (story_map.py:117-118) |
| story_map | 4 test asserts "not an object" | FIXED (test row now asserts "doc") |
| scenes | 1 test asserts "duplicate scene id" | FIXED (test asserts "S1") |
| scenes | 2 test asserts "order" | FIXED (test asserts "S1") |
| shots | 1 `ovi_ids: 5` raises | FIXED (shots.py:169-170) |
| shots | 2 `beat_line_ids: None` raises | FIXED (shots.py:181-182) |
| shots | 3 scene `line_ids: 5` raises | FIXED (shots.py:177) |
| shots | 4 class-enum row uses preset `01_establishing_shot` | STILL OPEN (defect S-2) |
| shots | 5 test asserts "scene has no shots" | FIXED (test asserts "S2") |
| briefs | 1 `scene_id: ["S1"]` raises | FIXED (briefs.py:121-126, verified) |
| briefs | 2 `references.characters: [""]` accepted | FIXED (briefs.py:78-81, schema error verified) |
| voices | 1 `validate(1, 1, ...)` / `None` raises | FIXED (voices.py:153-154, verified) |
| voices | 2 duplicate entries of one character reported twice | FIXED (voices.py:136-138 uses sets, verified) |
| sounds | 1 test asserts non-quoted wording | PARTLY FIXED (cue[0] now used; line 229 still open, defect O-1) |
| coverage, looks, questions | none | n/a |

---

## story_map

none.

## coverage

none.

## scenes

1. `tests/test_stage1_scenes.py:217-231` (class 3): nine `assert isinstance(M.validate(...), list)` checks. `scenes.validate` wraps `_validate_semantic` in a catch-all that returns `["scenes: malformed structure"]`, so `validate` can never raise and these asserts can never fail. Fix: for each call, assert `not any("malformed structure" in e for e in errs)`, as `test_stage1_sounds.py:290` already does.

## shots

1. `tests/test_stage1_shots.py:305-360` (class 3): twelve `assert isinstance(errs, list)` checks inside `test_validate_odd_data_no_raise`. `shots.validate` has a catch-all, so these can never fail. Fix: replace each with `assert not any("malformed structure" in e for e in errs)`.
2. `tests/test_stage1_shots.py:170` (class 3, Round 2 item 4 still open, verified): the row `(["shots", 0, "need_new"], {"reason": "x", "class": "bad_class"})` sits in a table where `preset` is `01_establishing_shot`. `schema_errors` returns only `shots shots/0/need_new: ... is not of type 'null'` (the else branch), so the class enum is never exercised. With preset `NEED_NEW` the same value gives `shots shots/0/need_new/class: 'bad_class' is not one of [...]`. Fix: move this row to a separate test with `preset` set to `"NEED_NEW"` and assert `"class"` in the message.

## briefs

1. `tests/test_stage1_briefs.py:339, 348, 357, 363, 369, 380` (class 3): six `assert isinstance(errs, list)` checks. `briefs.validate` has a catch-all, so these can never fail. Fix: assert `not any("malformed structure" in e for e in errs)`.
2. `tests/test_stage1_briefs.py:412` (class 4): asserts `"scene exists"`. The spec gives "scene exists" only as rule prose, not as a quoted message. Fix: `assert any("s99_test" in e for e in errs)`.

## looks

none.

## voices

1. `scripts/pipeline/stage1/voices.py:111-115` (class 1): the spec says "a character already RECURRING must not be listed twice". The code counts only RECURRING entries, so a character with one RECURRING entry and one NEW_PROPOSED entry is not flagged when not speaking. Verified: `validate` with `gajanan_maharaj` listed as RECURRING and again as NEW_PROPOSED, and `speaking_characters` set to `["narrator"]`, returns `[]`. Fix: `for char, entries in char_entries.items(): if len(entries) > 1 and any(e.get("status") == "RECURRING" for e in entries): messages.append(f"{char}: recurring character listed twice")`. Add a test row for this case. (The rule is worded in plain prose, so if the owner reads it as "two RECURRING entries only", close this as none.)

## sounds

1. `tests/test_stage1_sounds.py:229` (class 4, Round 2 item 1 partly open, verified): asserts `"document must be an object"`, which the spec does not quote. Fix: `assert isinstance(errs, list) and any("sounds" in e for e in errs)`, or assert the item id only.
2. `tests/test_stage1_sounds.py:235, 264, 269, 274, 281, 288, 297` (class 3): seven `assert isinstance(errs, list)` checks after calls to `validate`, which has a catch-all. These can never fail. Fix: assert `not any("malformed structure" in e for e in errs)`.

## questions

none.

---

## Defects per unit (Round 3)

| Unit | Defects |
|---|---|
| story_map | 0 |
| coverage | 0 |
| scenes | 1 |
| shots | 2 |
| briefs | 2 |
| looks | 0 |
| voices | 1 |
| sounds | 2 |
| questions | 0 |
| **Total** | **8** |

Notes:
- Class 2 (raise) is clean for document data. Every raise found in Round 2 is fixed. The catch-all in six modules hides any future raise, which is why the isinstance-only tests in scenes, shots, briefs and sounds cannot fail. Fixing those tests (items above) is the way to make the no-raise checks real.
- The pytest count is now 418 (Round 2 printed 400).
