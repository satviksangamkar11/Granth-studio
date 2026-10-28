# Stage 1 unit modules: Round 4 review (read-only)

Scope: `scripts/pipeline/stage1/{story_map,coverage,scenes,shots,briefs,looks,voices,sounds,questions}.py`, `tests/test_stage1_<unit>.py`, against `docs/pilot/nemotron_specs/unit_<unit>.md`, `stage1_base.json`, `STAGE1_RULES.md`.

Evidence: `uv run pytest -q --tb=short tests/test_stage1_*.py` gives **418 passed**. Defects below were reproduced by calling the module in memory (no project file written, no network). Fuzzing: about 6,600 validate and schema_errors calls, with every leaf of each document replaced by 14 odd values (None, 0, 7, -1, str, list, dict, bool, float, nested list), plus top-level None/list/str/{} documents. No raise was found from document data in any module. Out of scope and not counted: `coverage.validate` and `scenes.validate` raise TypeError when a ctx list (e.g. `chapter_ovis`) is None. No print, env, key or secret handling was found in any module or test.

## Verdict: FIX FIRST

---

## Round 3 findings: status

| Unit | Round 3 finding | Status |
|---|---|---|
| coverage | High: `covered_by: "²"` raises ValueError | FIXED (verified: returns the covered_by error, no raise) |
| scenes | 1 nine `isinstance`-only checks (catch-all) | FIXED (tests now assert no "malformed structure"; scenes.validate has no catch-all) |
| scenes | 2 duplicate-scene test asserts "S1" with overlaps | FIXED (verified: only "S1: duplicate scene id" contains S1) |
| scenes | 3 order test asserts "S1" also matched by unknown-line error | FIXED (verified: `S1: line_ids not in script order` is the only S1 message) |
| shots | 1 twelve `isinstance`-only checks | FIXED |
| shots | 2 class enum row uses preset `01_establishing_shot` | FIXED by `test_need_new_class_enum` (preset NEED_NEW; message contains "class"). The table row at line 170 still exercises only the null-type branch (residual, not a defect) |
| shots | 3 "S2" matched uncovered-line error | FIXED (verified: S2 line_ids emptied; only "S2: scene has no shots" contains S2) |
| shots | 4 test asserts "not in scene" | STILL OPEN (defect S-1) |
| briefs | 1 six `isinstance`-only checks | FIXED |
| briefs | 2 test asserts "scene exists" | FIXED (test asserts "s99_test"). The message itself is wrong, see B-1 |
| voices | 1 RECURRING + NEW_PROPOSED not flagged when not speaking | STILL OPEN (defect V-1, verified) |
| sounds | 1 test asserts "document must be an object" | FIXED (asserts "sounds" prefix) |
| sounds | 2 seven `isinstance`-only checks | FIXED |
| questions | none | n/a |
| looks | none | n/a |

---

## story_map

none.

## coverage

none.

## scenes

none.

## shots

1. `tests/test_stage1_shots.py:381` (class 4): `assert any("S1-1" in e and "not in scene" in e for e in errs)`. The spec quotes no "not in scene" phrase; the rule is only "beat_line_ids belong to the scene". Verified: the message is `S1-1: beat line S2-L1 not in scene S1`. Fix: `assert any("S1-1" in e for e in errs)` and keep the separate `"S2-L1" in e and "line is in no shot beat" in e` check.

## briefs

1. `scripts/pipeline/stage1/briefs.py:160` (class 1, message wrong): the missing-scene message is `f"{img_id}: scene exists"`. It is emitted when the scene does NOT exist. Verified: a brief with scene_id S99 returns `['s99_x: scene exists', ...]`. Fix: `messages.append(f"{img_id}: scene {scene_id} does not exist")`. The test at `tests/test_stage1_briefs.py:415` asserts only "s99_test" and still passes after the fix.

## looks

1. `tests/test_stage1_looks.py` (class 3, spec no-raise requirement has no test): the spec requires validate to "never raise on odd data", but the file has no odd-data test (grep for odd/raise/no_raise finds nothing). `looks.validate` has no catch-all, so a future regression would go unnoticed. Fix: add a parametrized test that passes `validate(1, doc, docs, ctx)` with doc set to None, [], "x", a dict whose `entries` is None, and entries containing `None`, `1`, `{"entity_id": ["x"]}`, and asserts the result is a list.

## voices

1. `scripts/pipeline/stage1/voices.py:111-114` (class 1): the rule "a character already RECURRING must not be listed twice" counts only RECURRING entries (`recurring_count > 1`). Verified: cast entries `gajanan_maharaj` RECURRING plus `gajanan_maharaj` NEW_PROPOSED, with speaking_characters = `["narrator"]`, returns `[]`. Fix:
   ```python
   for char, entries in char_entries.items():
       if len(entries) > 1 and any(e.get("status") == "RECURRING" for e in entries):
           messages.append(f"{char}: recurring character listed twice")
   ```
   Add a test row for this case (non-speaking character, one RECURRING and one NEW_PROPOSED entry, expecting "recurring character listed twice").

## sounds

none.

## questions

none.

---

## Defects per unit (Round 4)

| Unit | Defects |
|---|---|
| story_map | 0 |
| coverage | 0 |
| scenes | 0 |
| shots | 1 |
| briefs | 1 |
| looks | 1 |
| voices | 1 |
| sounds | 0 |
| questions | 0 |
| **Total** | **4** |
