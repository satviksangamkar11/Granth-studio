### story_map

none

### coverage

1. **Class 2 — exception on JSON-shaped context** ([coverage.py:84](</D:/aai work/granthstudio/scripts/pipeline/stage1/coverage.py:84>)). An in-memory call to `validate(1, {"adhyay": 1, "ovis": []}, {}, {"script_line_ids": None})` raises `TypeError` when converting `None` to a set. **Fix:** handle non-iterable and unhashable context values before converting them, so `validate` returns a list for JSON-shaped input.

### scenes

1. **Class 2 — exception on JSON-shaped context** ([scenes.py:109](</D:/aai work/granthstudio/scripts/pipeline/stage1/scenes.py:109>)). An in-memory call to `validate(1, {"adhyay": 1, "scenes": []}, {}, {"script_line_ids": None})` raises `TypeError` when converting `None` to a list. **Fix:** handle non-iterable and unhashable context values before constructing the list and sets, so `validate` returns a list for JSON-shaped input.

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

The supplied test evidence reports **529 passed**. The two exception checks above executed the module source in memory using a stub for `jsonschema`; they did not run the project’s Python environment or write files.

## Verdict: FIX FIRST