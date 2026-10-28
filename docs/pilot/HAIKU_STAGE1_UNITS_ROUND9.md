# Stage 1 unit modules: Round 9 review (read-only)

Scope: `scripts/pipeline/stage1/{story_map,coverage,scenes,shots,briefs,looks,voices,sounds,questions}.py`, `tests/test_stage1_<unit>.py`, against `docs/pilot/nemotron_specs/unit_<unit>.md`, `stage1_base.json`, `STAGE1_RULES.md`.

## Method and evidence

- `uv run pytest -q --tb=short tests/test_stage1_*.py`: 425 passed (the review prompt says 460; the suite reports 425).
- Mutation checks run in memory only (a patched loader substitutes one source string per run; no file was written). Each run is one pytest invocation on the unit's test file. A "killed" mutant means at least one test fails.
  - 81 semantic-rule mutants (every `validate` rule, adhyay check included): all killed. Single-test kills for most rules, so the rule-specific test is isolated.
  - 38 schema-rule mutants (conditionals, required lists, patterns, object shapes): 6 survived as recorded below.
  - Every schema `enum` value removed one at a time: the survivors are recorded below.
  - Every `minItems`, `minimum`, `minLength` bound relaxed one at a time: the survivors are recorded below.
- Fuzz (in-process, no writes): 14,782 calls of `validate` and `schema_errors` with odd values (None, bool, numbers, strings, lists, dicts, nested wrong types, missing keys) on every document path (depth up to 4) and on every `docs` entry. No exception escaped from any document input. Not counted: `coverage.validate` and `scenes.validate` raise TypeError when a `ctx` list is None or a bool (`ctx` is the context dict, not a document). Not counted: `coverage.validate` raises AttributeError when `ctx` itself is None (Round 8 treatment).
- Grep: no print, environment read, key, token or secret handling in any module or test.

## Round 8 status

| Round 8 finding | Status (Round 9) |
|---|---|
| scenes 1: `malformed structure` assertions | Sentinel class, excluded per KNOWN DESIGN RULE |
| shots 1: `malformed structure` assertions | Sentinel class, excluded |
| briefs 1: collateral "scene does not exist" row | FIXED. Row is absent from `SEMANTIC_CASES`. Removing the scene-existence rule now fails only `test_semantic_scene_not_exist_no_shot_refs` (verified) |
| briefs 2: `malformed structure` assertions | Sentinel class, excluded |
| looks 1: `malformed structure` assertion | Sentinel class, excluded |
| sounds 1: `malformed structure` assertions | Sentinel class, excluded |
| Round 7 shots: `test_consecutive_grouped_by_scene_id` cannot fail | FIXED. Grouping by `f"S{scene_num}"` now fails that test (verified) |
| Round 9 scenes: reversed-range test isolated | Verified. Removing the `lo > hi` rule fails exactly one test |

## story_map

1. `story_map.py:23` (class 3): schema `type` enum values INVOCATION, OTHER, PHILOSOPHY, RECAP and PHALASHRUTI have no failing test when removed. Fix: add a schema-valid case per value to the schema-valid test, e.g. `ovi_types[0].type = "PHALASHRUTI"` must give `schema_errors == []`.
2. `story_map.py:47` (class 3): schema `closure` enum values CONTINUES_NEXT_ADHYAY, STARTED_EARLIER and SOURCE_INCOMPLETE_OR_AMBIGUOUS have no failing test when removed. Fix: same as item 1 for `events[0].closure`.
3. `story_map.py:22`, `:40`, `:44` (class 3): the `ovi >= 1` bound (ovi_types item `ovi`, events `ovi_range` items, events `key_ovis` items) is untested. Fix: add schema rows with `0` for each path.
4. `story_map.py:35` (class 3): `events[].title` minLength 1 is untested. Fix: add a schema row with `title = ""`.

## coverage

1. `coverage.py:25` (class 3): the enum value PROPOSE_OMISSION is never asserted as schema-valid; removing it from the enum fails no test. The omission tests call `validate` only. Fix: add a `schema_errors(doc) == []` case for a document with one PROPOSE_OMISSION entry that has a reason.
2. `coverage.py:27` (class 3): `reason` minLength 1 is untested. Fix: add a schema row with `reason = ""` for a VISUALISED entry, expecting a `reason` error.
3. `coverage.py:31` (class 3): `covered_by` integer minimum 1 is untested. Fix: add a schema row with `covered_by = 0` on a MERGED_EQUIVALENT entry.

## scenes

1. `scenes.py:49` (class 3): enum values `contemplative_hold` and `symbol_from_text` have no failing test when removed. Fix: add a schema-valid case per value to the discourse-scene schema test.
2. `scenes.py:58` (class 3): the schema clause `"teaching_treatment": {"not": {"const": "none"}}` for discourse scenes is untested (removing it fails no test). The semantic rule for the same case is tested, so only the schema clause is uncovered. Fix: add `schema_errors` non-empty for a discourse scene with `teaching_treatment = "none"`.
3. `scenes.py:31` (class 3): `ovi_range` item minimum 1 is untested. Fix: add a schema row with `ovi_range = [0, 5]`.

## shots

1. `shots.py:63` (class 3): enum values `missing_image`, `json_arrangement` and `renderer_gap` of `need_new.class` have no failing test when removed (only the required-field check is tested). Fix: add a schema-valid NEED_NEW case per class value.
2. `shots.py:18` (class 3): `adhyay` minimum 1 is untested (`adhyay = 0` passes the schema). Fix: add a schema row with `adhyay = 0` expecting an `adhyay` error.
3. `shots.py:62` (class 3): `need_new.reason` minLength 1 is untested. Fix: add a schema row with `need_new.reason = ""`.

## briefs

1. `briefs.py:17` (class 3): `adhyay` minimum 1 is untested. Fix: add a schema row with `adhyay = 0`.

## looks

1. `looks.py:27` (class 3): enum values `place` and `prop` of `kind` have no failing test when removed. Fix: add a schema-valid case per value (`kind = "place"`, `kind = "prop"`).

## voices

1. `voices.py:28` (class 3): enum value `female` of `gender` has no failing test when removed. Fix: add a schema-valid case with `gender = "female"`.
2. `voices.py:29` (class 3): enum value `NEW_PROPOSED` of `status` has no failing test when removed. Fix: add a schema-valid case with `status = "NEW_PROPOSED"`.

## sounds

1. `sounds.py:28` (class 3): enum value `fx` of `kind` has no failing test when removed. Fix: add a schema-valid cue with `kind = "fx"` and an `fx_` sound id.
2. `sounds.py:31` (class 3): enum value `stated` of `basis` has no failing test when removed. Fix: add a schema-valid cue with `basis = "stated"`.
3. `sounds.py:17` (class 3): `adhyay` minimum 1 is untested. Fix: add a schema row with `adhyay = 0`.
4. `sounds.py:29` (class 3): `sound_prompt` minLength 1 is untested. Fix: add a schema row with `sound_prompt = ""` on a NEED_NEW cue.
5. `sounds.py:30` (class 3): `purpose` minLength 1 is untested. Fix: add a schema row with `purpose = ""`.

## questions

1. `questions.py:22` (class 3): the id pattern `^Q[0-9]+$` is untested. Changing it to `^Q` fails no test. Fix: add a schema row with `id = "Qx"` (and one with `id = "Q"`) expecting an `id` error.

## Items checked and found implemented

Every semantic rule of every unit in its unit spec (`validate`) is implemented and has a failing test. The schema conditionals (scenes discourse/story, shots NEED_NEW/else, coverage PROPOSE_OMISSION and MERGED_EQUIVALENT, sounds NEED_NEW/else) and the spec-quoted messages match. No class 1 or class 2 defect was verified.

## Defects per unit (Round 9)

| Unit | Defects |
|---|---|
| story_map | 4 |
| coverage | 3 |
| scenes | 3 |
| shots | 3 |
| briefs | 1 |
| looks | 1 |
| voices | 2 |
| sounds | 5 |
| questions | 1 |
| **Total** | **23** |

All 23 are class 3 (test gaps). None is a missing rule or a raise on document data.

## Verdict: FIX FIRST
