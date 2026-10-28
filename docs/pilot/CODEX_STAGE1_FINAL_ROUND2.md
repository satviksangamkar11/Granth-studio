### story_map

none

### coverage

none

### scenes

1. **Class 1 — gaps in chapter ovis are accepted** ([scenes.py:241](</D:/aai work/granthstudio/scripts/pipeline/stage1/scenes.py:241>)). The outside-chapter check compares ranges only with the chapter’s minimum and maximum. With the baseline scenes and `chapter_ovis = [1,2,3,4,5,6,8,9]`, `validate` returns `[]` even though scene S2 includes ovi 7, which is outside the chapter. **Fix:** detect missing chapter members inside each range without enumerating an arbitrarily large range; add a regression test with a gap.

2. **Class 1 — an unfilmed ovi can be missed** ([scenes.py:232](</D:/aai work/granthstudio/scripts/pipeline/stage1/scenes.py:232>)). The check only considers `all_covered_ovis`, which contains chapter members. With baseline chapter ovis, `unfilmed_ovis = [10]`, and S2’s range changed to `[6,10]`, the result reports the range outside the chapter but does not report that unfilmed ovi 10 is inside S2. **Fix:** check each unfilmed ovi directly against scene ranges and report the matching scene; add a regression test.

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

The supplied pytest evidence reports **566 passed**. In-memory checks confirmed that the previously reported `ctx=None` and `script_line_ids=None` cases return lists for coverage and scenes, and that a scenes range ending at `10**30` returns promptly. The checks used the system Python with a `jsonschema` stub; they did not run the project environment or verify schema validation. No files were edited.

## Verdict: FIX FIRST