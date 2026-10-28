1. **story_map:** none.
2. **coverage:** none.
3. **scenes:** none.
4. **shots:** none.
5. **briefs:** none.
6. **looks:** none.
7. **voices:** none.
8. **sounds:** none.
9. **questions:** none.
10. **aggregate:**
    1. **Class 1 — X10 misses scenes with no overlapping event.** [aggregate.py:395](</D:/aai work/granthstudio/scripts/pipeline/stage1/aggregate.py:395>) only reports a mismatch when `overlapping_kinds` is nonempty. With the base scenes and an empty events list, an in-memory check returned no X10 scene error, although the amendment requires every scene to match an overlapping event. Remove the nonempty-set condition and correct the contrary assertion in [test_stage1_aggregate.py:410](</D:/aai work/granthstudio/tests/test_stage1_aggregate.py:410>).
    2. **Class 1 — malformed series voice values trigger the forbidden sentinel.** [aggregate.py:304](</D:/aai work/granthstudio/scripts/pipeline/stage1/aggregate.py:304>) constructs a set from unfiltered dictionary values. With `series_voices = {"x": []}`, an in-memory check returned `aggregate: internal error in X7`. Filter invalid entries before constructing the set and add a nested wrong-type test.
    3. **Class 1 — X8 does not strip all punctuation.** [aggregate.py:79](</D:/aai work/granthstudio/scripts/pipeline/stage1/aggregate.py:79>) omits `/` from its punctuation handling. With script text `one two three four five six` and document text `one two three four five six/`, an in-memory check returned no copy error. Normalize punctuation consistently for both strings and test this case.
11. **context:**
    1. **Class 1 — malformed source objects can escape instead of becoming problems.** [context.py:78](</D:/aai work/granthstudio/scripts/pipeline/stage1/context.py:78>) and [context.py:123](</D:/aai work/granthstudio/scripts/pipeline/stage1/context.py:123>) call `.get()` outside their read exception handlers. In-memory checks using valid JSON `[]` for either the omissions file or voice library raised `AttributeError`. Handle non-object data as a source problem and return the corresponding empty values; add tests for both sources.

## Non-blocking notes

The supplied test evidence reports **641 passed**. The project environment was unavailable for this review, so the aggregate checks used in-memory unit stubs; they exercised the cross-rule code but did not rerun schema validation.

The scene range checks returned no false gap for `[1,4]` and `[6,9]` over chapter ovis `{1–4, 6–9}`; they reported a real internal gap and an unfilmed ovi, and completed for `[1, 10**12]`.

## Verdict: FIX FIRST