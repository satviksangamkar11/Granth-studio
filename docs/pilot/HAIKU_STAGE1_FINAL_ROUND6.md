# Stage 1 FINAL read-only review (Haiku)

Scope: `scripts/pipeline/stage1/{story_map,coverage,scenes,shots,briefs,looks,voices,sounds,questions,aggregate}.py`, tests `tests/test_stage1_*.py`.

## Evidence

- `uv run pytest -q --tb=short tests/test_stage1_*.py` (run here, cache disabled): 554 passed, 0 failed.
- Fuzz, in memory, 3000 random JSON-shaped docs and ctx values per unit: `schema_errors` and `validate` raised 0 exceptions for all nine units.
- Fuzz, in memory, 1500 runs of `validate_all` with wrong-type ctx values (`unfilmed_ovis`, `chapter_ovis`, `series_voices`, `script_texts`, and others) and 1500 runs with wrong-type unit documents: 0 `aggregate: internal error` messages.
- `validate_all(1, None, ctx)` gives the docs error plus nine `document missing` errors. `ctx` of None, 5, "x" or [1] gives `aggregate: ctx must be an object` and treats ctx as `{}`.
- Base fixture (`stage1_base.json`) validates to `[]`.

## Aggregate changes since round 5, checked

- Wrong-type ctx values are handled with no raise and no `aggregate: internal error` sentinel.
- X1 is kind-aware. A STORY ovi with only discourse events fails, and a TEACHING ovi with only story events fails. Verified both directions.
- X2 is absent. A STORY ovi with PROPOSE_OMISSION and owner approval produces no `coverage: ... omission proposed` message. The only remaining message comes from the scenes unit (unfilmed ovi inside a range), which is that unit's own rule.
- X8 runs on any dict-shaped unit document, including a schema-invalid one. A 6-word run copied from `script_texts` is flagged (`questions/0/text`). A short text does not trigger.
- X9 flags an event range outside the chapter and a key ovi outside the chapter, and checks `key_ovis` against the chapter set. Verified.
- Bool ovi values are excluded from ctx int lists (`_is_int` / `_get_int_list`).
- Huge range `[1, 10**12]` in scenes and in aggregate returns in about 0.002 s.

## Scenes and voices changes, checked

- scenes: total gap-message cap is 1000 per-ovi messages plus one summary (`S1: more ovis outside chapter ovis (message limit reached)`). Verified by an 10^12-wide range; output is 1002 messages. Gap detection for [1,3] with chapter [1,3] minus ovi 2 reports `ovi 2`. Bool chapter ovi is excluded.
- voices: `reason` is required for NEW_PROPOSED through the schema `if/then`. Tests exist for missing and empty reason. This matches the owner rule in `STAGE1_RULES.md` line 36.

## Per-unit BLOCKING defects

1. story_map: none
2. coverage: none
3. scenes: none
4. shots: none
5. briefs: none
6. looks: none
7. voices: none
8. sounds: none
9. questions: none
10. aggregate: none

Total BLOCKING: 0 (aggregate included: 0).

## Non-blocking notes

- `docs/pilot/nemotron_specs/unit_voices.md` (line 14) does not mention the `reason` field that the module now requires for NEW_PROPOSED. The module follows `STAGE1_RULES.md`. Suggest syncing the spec text.
- aggregate X8 uses a 6-word run instead of the 20-character substring in `docs/pilot/nemotron_specs/aggregate.md`. This follows the round-5 change in the review prompt. Short common phrases could false-positive; no test covers this, and it is not a blocker.
- aggregate spec text still lists X2. The prompt says X2 was removed on purpose; the code and tests match the prompt. Spec file not updated.
- Schema enum and bound gaps (for example voice_id length bounds and the `ovi_range` minimum) are not separately tested. Not blocking per the STOP RULE.
- The `malformed structure` sentinel is project-defined and was not reported, per the known design rule.

## Verdict

## Verdict: READY
