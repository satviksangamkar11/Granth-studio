### story_map

1. none

### coverage

1. none

### scenes

1. none

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

### aggregate

1. **Class 1 — X1 ignores event kind.** [aggregate.py:163](</D:/aai work/granthstudio/scripts/pipeline/stage1/aggregate.py:163>) stores only event ranges. An in-memory check of that condition accepts a STORY ovi covered solely by a discourse event, although the amendment requires a story event. **Fix:** retain each event’s kind and require the kind corresponding to the ovi type. Add failing tests for both STORY and TEACHING kind mismatches.

2. **Class 1 — removed X2 still rejects approved omissions.** [aggregate.py:180](</D:/aai work/granthstudio/scripts/pipeline/stage1/aggregate.py:180>) emits an error for a STORY or TEACHING ovi marked `PROPOSE_OMISSION`, even when it is owner-approved in `unfilmed_ovis`. The current tests at [test_stage1_aggregate.py:111](</D:/aai work/granthstudio/tests/test_stage1_aggregate.py:111>) assert that obsolete error. **Fix:** remove X2 and change the tests to assert that type alone does not reject an approved omission.

3. **Class 1 — X10 accepts a scene with no overlapping event.** [aggregate.py:405](</D:/aai work/granthstudio/scripts/pipeline/stage1/aggregate.py:405>) only reports a mismatch when `overlapping_kinds` is non-empty. An empty overlap therefore passes the condition, although the amendment requires at least one matching overlapping event. The test at [test_stage1_aggregate.py:455](</D:/aai work/granthstudio/tests/test_stage1_aggregate.py:455>) expects the opposite. **Fix:** report an error whenever no matching overlapping event exists, and correct that test.

4. **Class 1 — X8 misses punctuation-separated copied wording.** [aggregate.py:77](</D:/aai work/granthstudio/scripts/pipeline/stage1/aggregate.py:77>) strips a limited punctuation list. An in-memory check using `one/two three four five six seven` against `one two three four five six` does not match because `/` remains attached, contrary to the amended punctuation-stripping rule. **Fix:** normalize punctuation consistently for both script and document text, and add a failing test for punctuation outside the current list.

## Non-blocking notes

- The supplied test record reports **629 passed, 1 warning**. I did not run the project’s Python; the checks described above exercised the relevant conditions in memory rather than executing the modules.
- The current scene tests cover the late-range false positive, real internal gaps, unfilmed ovis inside ranges, and huge ranges. The previous round’s in-memory review also reported those cases passing. The current source retains the bounded gap walk, boolean exclusions, and input guards.
- The export path now continues to validation. The voices schema requires a non-empty `reason` for `NEW_PROPOSED`; X7’s new-character series-voice check and X11 are present.
- The prior round-six READY report describes X1 and X2 behavior that does not match the current files. The recorded passing tests do not establish the amended behavior for those rules.

## Verdict: FIX FIRST