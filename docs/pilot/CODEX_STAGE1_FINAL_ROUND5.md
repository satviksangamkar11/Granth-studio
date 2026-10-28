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

1. **Class 2 — malformed context can raise.** At [aggregate.py:152](</D:/aai work/granthstudio/scripts/pipeline/stage1/aggregate.py:152>), `set(ctx.get("unfilmed_ovis", []))` raises `TypeError` for JSON-shaped inputs such as `{"unfilmed_ovis": null}` or `{"unfilmed_ovis": [1, {}]}`. An in-memory call to `validate_all` reproduced both exceptions with the unit interfaces stubbed. The spec requires it never to raise and requires unexpected step exceptions to become internal-error messages. **Fix:** guard each validation step, including schema validation and cross rules, so exceptions produce the specified error and validation continues.

2. **Class 1 — X8 skips valid documents when any other document fails schema validation.** At [aggregate.py:262](</D:/aai work/granthstudio/scripts/pipeline/stage1/aggregate.py:262>), X8 requires all nine units to be schema-valid. In an in-memory check, a valid scenes document copied a long script line, but making coverage schema-invalid suppressed the scenes copy error. X8 reads each document independently, so an unrelated invalid document must not prevent checking a valid one. **Fix:** run X8 separately for each present, schema-valid document.

3. **Class 1 — schema export bypasses validation and reporting.** At [aggregate.py:326](</D:/aai work/granthstudio/scripts/pipeline/stage1/aggregate.py:326>), successful `--export-schemas` returns immediately. An in-memory check with export and validation stubbed returned `0` and printed nothing even though validation would have returned an error. The spec requires `main` to print validation errors and their count, and return `1` when errors exist. **Fix:** continue to validation after successful export.

## Non-blocking notes

- The supplied test record reports **610 passed**, including all 21 aggregate tests. The full repository run recorded there predates the latest changes.
- In-memory checks of the current scenes semantic function confirmed that the sparse valid ranges do not report ovi 5, a real internal gap and an unfilmed ovi are reported, and `[1, 10**12]` returns promptly. The check used a stub for the unavailable schema library.
- Earlier `ctx=None` normalization and the coverage and scenes exception guards remain present. The project-defined `malformed structure` sentinel was treated as instructed.
- The aggregate reproductions used the actual aggregate code with unit interfaces stubbed because the system Python could not load the project’s schema dependency. No files were edited.

## Verdict: FIX FIRST