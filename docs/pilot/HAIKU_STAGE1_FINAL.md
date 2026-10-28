# Haiku final read-only review: Stage 1 aggregate and context units

Scope: `scripts/pipeline/stage1/aggregate.py` (rules X1, X3-X11) and `scripts/pipeline/stage1/context.py`. Base document: `docs/pilot/nemotron_specs/stage1_base.json`. Nothing was edited except this report. No network use. `secrets\` was not opened.

## Test evidence

- `uv run pytest -q --tb=short tests/test_stage1_*.py`: 585 passed, 0 failed.
- `docs/pilot/TEST_RUN_STAGE1.txt` (real run outside the sandbox): ALL 651 passed, 1 warning.
- Test functions present for X1, X3-X11, the robustness cases and context sources (`tests/test_stage1_aggregate.py`, `tests/test_stage1_context.py`).

## Aggregate (`aggregate.py`)

In-memory checks on the live module:

- Base document with `ctx` from the base file: no errors.
- X1 is kind-aware: STORY ovi 1 typed TEACHING gives "is in no discourse event"; TEACHING ovi 6 typed STORY gives "is in no story event". Pass.
- X2 is absent: an ovi of type STORY/TEACHING with no omission proposal raises nothing from the aggregator. Pass.
- X3: a PROPOSE_OMISSION ovi not in `unfilmed_ovis` gives "omission is not approved by the owner"; approved with no proposal gives "approved as unfilmed but has no omission proposal". Pass.
- X4: VISUALISED ovi not in any shot gives an error. Pass.
- X5: key ovi outside every scene gives an error. Pass.
- X7: recurring voice mismatch, NEW_PROPOSED for a series character, and NEW_PROPOSED reusing another character's series voice each give an error. Wrong-typed `series_voices` (None, int, str, lists, dicts with non-str keys or values) is read as empty and does not raise. Pass.
- X8: a 6-word run copied from the script is flagged after punctuation normalisation; 6 words in a script with no copied run is not flagged. Pass.
- X9: event range beyond the chapter and key ovi outside the chapter each give an error. Pass.
- X10: a story scene over only discourse events gives "scene S1 is story but its events are not story". A scene with no overlapping event reports nothing, as the round 8 note says on purpose. Pass.
- X11: a cast voice_key not in `verified_voices` gives an error; NEW_PROPOSED without `reason` is rejected by the voices schema. Pass.

Robustness fuzz on the live module:

- 562 cases of `ctx` key and whole-`ctx` values of every wrong type (None, bool, int, float, str, list, dict, nested lists, huge int): no raise and no `aggregate: internal error` sentinel.
- 3712 cases that mutate every leaf and every node of each of the nine base documents to 16 different JSON-shaped values: no raise and no sentinel.
- Each of the nine documents replaced by None, list, int or str: no raise and no sentinel.

Blocking defects: none.

## Context (`context.py`)

In-memory checks on the live module, with fake file objects, no files written:

- Each reader (`_read_ovis`, `_read_omissions`, `_read_voice_library`, `_read_presets`, `_read_sound_palette`) was run on 15 source texts: `null`, `1`, `"s"`, `[]`, `{}`, `[1]`, `true`, `[[1]]`, dicts with wrong-typed fields, JSONL with mixed lines, `1e400`, and 3000-deep nested arrays. 150 cases, 0 raises. Non-object JSON is reported as a problem.
- `build_ctx` with each source file replaced by those texts, covering the source, omissions and approvals paths: 45 cases, 0 raises, and a dict is always returned.

Blocking defects: none.

## Non-blocking notes

1. `aggregate.py` `_walk_strings` stops at depth 8 (line 58), so an X8 copy located deeper than 8 levels would not be flagged. Not verified whether any unit schema allows strings that deep. Style-level, not a blocker under the STOP RULE.
2. `context.py` `_read_ovis`: a JSONL integer longer than Python's int-digit limit raises `ValueError` inside `json.loads`, which is caught by the outer `except`. Reading stops at that point, but the problem is recorded, so it is not silent.
3. `context.py` `_read_voice_library`: a character listed twice in the same entry's `assigned_to` is reported as "assigned to more than one voice". Wording is loose, not a rule failure.
4. `aggregate.py` `validate_all` calls `module.schema_errors(doc)` (line 155) outside a try block. No raise was found in the fuzz above, so this is not a defect, but a try block would match the rest of the file.
5. `X7` only applies when `series_voices` is a usable dict. Wrong types are treated as empty, as the round 8 amendment specifies.

## Verdict basis

No verified CLASS 1, CLASS 2 or CLASS 3 defect in either unit. The `malformed structure` sentinel was not reported, per the design rule.

## Blocking defects per unit

- aggregate: 0
- context: 0

## Verdict: READY
