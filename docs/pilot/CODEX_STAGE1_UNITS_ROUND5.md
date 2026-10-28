## Verdict: FIX FIRST

### story_map

none

### coverage

none

### scenes

none

### shots

1. **Medium — [shots.py:133](</D:/aai work/granthstudio/scripts/pipeline/stage1/shots.py:133>):** Consecutiveness is grouped by the scene prefix in `shot_id`, rather than by the shot’s `scene_id`. Swapping the scene assignments of baseline shots `S1-1` and `S2-1`, with their ovis and lines adjusted to match the assigned scenes, returns `[]` even though the shot numbers assigned to each scene are not consecutive from 1. Group numbers by `scene_id` and reject a shot ID whose prefix does not match its assigned scene; add an isolated test.

### briefs

none

### looks

none

### voices

1. **Low — [test_stage1_voices.py:234](</D:/aai work/granthstudio/tests/test_stage1_voices.py:234>):** The new mixed `RECURRING`/`NEW_PROPOSED` duplicate test also shares `gajanan` with `gajanan_maharaj`. It therefore passes on the collateral `other_char: voice key shared with another character` error if recurring-duplicate detection is removed. Use the same narrator voice for both `other_char` entries, or otherwise isolate the duplicate rule.

### sounds

none

### questions

none

The Round 4 mixed-status voice behavior is fixed, but its new test is not isolated. The other reported Round 4 changes are present; I reproduced the scene duplicate case and inspected the revised shots, briefs, and looks checks.

The workspace is read-only, so I could not write a report file. I reproduced the findings in memory with a stub for `jsonschema`; I could not run the suite or independently verify schema behavior because the available Python lacks `jsonschema` and the project virtual environment could not start. The remaining units were not exhaustively verified.