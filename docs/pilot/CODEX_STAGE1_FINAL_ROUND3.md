### story_map

1. none

### coverage

1. none

### scenes

1. **Class 1 — valid scene range reports ovis outside that range** ([scenes.py:271](</D:/aai work/granthstudio/scripts/pipeline/stage1/scenes.py:271>)). With chapter ovis `[1, 10]`, unfilmed ovis `[1]`, and one scene covering `[10, 10]`, the scene covers the only filmed chapter ovi. The gap scan nevertheless reports ovis 2 through 9 as outside the chapter: it replaces `prev = check_lo - 1` with the earlier chapter ovi `1`, then examines the gap before the scene’s range. An in-memory reproduction of the scan produced those eight errors. **Fix:** keep the gap scan clipped to `[check_lo, check_hi]`, and add a regression test for this valid sparse-chapter case.

### shots

1. none

### briefs

1. none

### looks

1. none

### voices

1. none

### sounds

1. none

### questions

1. none

## Non-blocking notes

- The supplied test log reports **568 passed**, including all nine Stage 1 unit suites.
- Source inspection confirms that the prior `ctx=None` and catch-all fixes are present. The scenes code now checks unfilmed ovis directly, detects gaps inside ranges, and avoids enumerating the full `[1, 10**12]` range; tests for the two round-2 cases and the huge range are present.
- The project Python could not be started in this sandbox. The blocking finding was checked with an in-memory reproduction of the relevant scan, rather than by executing the module itself. No files were edited.

## Verdict: FIX FIRST