## Verdict: FIX FIRST

### story_map

none found.

### coverage

none found.

### scenes

1. **Low — [test_stage1_scenes.py:186](</D:/aai work/granthstudio/tests/test_stage1_scenes.py:186>):** The reversed-range test passes for a collateral turn-outside-range error. With the reversed-range check disabled in memory, the assertion still passes on `S1: turn ovi outside range`. **Fix:** isolate the range check, for example by removing the turn from the semantic fixture, and confirm the test fails when that check is disabled.

### shots

none found.

### briefs

1. **Low — [test_stage1_briefs.py:298](</D:/aai work/granthstudio/tests/test_stage1_briefs.py:298>):** The missing-scene case also has a shot assigned to a different scene. With the scene-existence check disabled in memory, it still passes on the shot-reference error. **Fix:** remove the shot references in this case, as the separate test at line 405 already does, or remove the redundant collateral case.

### looks

none found.

### voices

none found.

### sounds

none found.

### questions

none found.

The Round 7 shots grouping and wording findings are fixed: an in-memory prefix-grouping mutant no longer satisfies the revised grouping assertion.

The review was not exhaustive. I could not rerun the suite or independently check schema behavior: the project Python could not start in the sandbox, and system Python lacks the dependencies. Reproductions used an in-memory `jsonschema` stub. The read-only sandbox also prevented creation of a report file.