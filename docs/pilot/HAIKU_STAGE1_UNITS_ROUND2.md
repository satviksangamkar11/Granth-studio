# Stage 1 unit modules: Round 2 review (read-only)

Scope: `scripts/pipeline/stage1/{story_map,coverage,scenes,shots,briefs,looks,voices,sounds,questions}.py`, `tests/test_stage1_<unit>.py`, against `docs/pilot/nemotron_specs/unit_<unit>.md`, `stage1_base.json`, `STAGE1_RULES.md`.

Evidence: `uv run pytest -q --tb=short tests/test_stage1_*.py` gives **400 passed** (the brief states 415; the count here is what the run printed). Every defect below was reproduced by calling the module in memory with a small input (no project file written, no network). No print, env, key or secret handling was found in any module or test.

## Verdict: FIX FIRST

---

## Round 1 findings: status

| Unit | Round 1 finding | Status |
|---|---|---|
| story_map | `ovi_types: [null]` raises | FIXED (returns "ovi N is untyped") |
| story_map | tests assert `lo > hi`, `key_ovi`, `outside` wording | FIXED (rows assert "E1") |
| story_map | `key_ovis` below range branch untested | FIXED (row `key_ovis: [0]` present) |
| coverage | `ovis: [null]` raises | FIXED. Note: Round 1 said "Tests: none"; `tests/test_stage1_coverage.py` exists (243 lines) |
| scenes | out-of-order check lost after unknown line id | FIXED |
| scenes | `ovi_range: ["a", 2]` turn check raises TypeError | FIXED |
| scenes | unhashable `scene_id` / `line_id` raises | FIXED |
| scenes | story `teaching_treatment: "none"` rejected by schema | FIXED (schema `const: none`; positive test present) |
| scenes | no isolated test for forbidden story treatment | FIXED (`test_schema_story_scene_forbidden_treatment`) |
| scenes | duplicate-scene test passes through collateral match | FIXED (now asserts "duplicate scene id"; wording see defect S1) |
| shots | `shots: [null]` raises | FIXED |
| shots | `preset` accepts any string | FIXED (pattern `^([0-9]{2}_[a-z0-9_]+\|NEED_NEW)$`) |
| shots | class-enum row uses non-NEED_NEW preset | STILL OPEN (defect H4) |
| shots | scene-has-shots test collateral "S2" | FIXED (asserts "scene has no shots") |
| shots | "consecutive" wording asserted | FIXED (asserts "S1"; the test fails if the rule is removed) |
| shots | preset check skipped when scene missing | FIXED (verified: "S1-1: unknown preset bogus" is reported) |
| briefs | non-string `image_id` / `shot_id` / `scene_id` raises | PARTLY: `image_id`/`shot_id` FIXED; `scene_id` in scenes still raises (defect B1) |
| briefs | `prop`/`prop_state` empty accepted; text bounds missing | FIXED for listed fields; `references.characters` items still unbounded (defect B2) |
| briefs | asserted wording not quoted by spec | FIXED (asserts item id) |
| voices | `cast: [1]` / `cast: None` / non-dict entries raise | FIXED |
| voices | two NEW_PROPOSED entries not flagged; recurring duplicate outside speaking set | FIXED (verified) |
| voices | narrator suppresses error for two other sharers | FIXED (verified: both `x` and `y` flagged) |
| voices | required fields never tested by deletion | FIXED (DELETE rows present) |
| voices | asserted wording not quoted | FIXED (asserts item id) |
| sounds | cue without `sound_id` raises AttributeError | FIXED (verified) |
| sounds | asserted wording not quoted | PARTLY: `cue[0]` used in the main table; guard-message asserts remain (defect SO1) |
| questions | unhashable `id` / `scene_id` raises | FIXED (verified) |
| questions | odd-data test lacks unhashable cases | FIXED (cases present) |
| looks | none | n/a |

---

## story_map

1. `scripts/pipeline/stage1/story_map.py:83-85`: `ovi_types` is not type-checked. `{"ovi_types": None}` raises `TypeError: 'NoneType' object is not iterable` (verified). Fix: `ovi_types = doc.get("ovi_types"); if not isinstance(ovi_types, list): ovi_types = []`.
2. `scripts/pipeline/stage1/story_map.py:106-107`: `events` is not type-checked. `{"events": 5}` raises `TypeError` (verified). Fix: `events = doc.get("events"); if not isinstance(events, list): events = []`.
3. `scripts/pipeline/stage1/story_map.py:112, 122`: `key_ovis` is not type-checked. `key_ovis: 5` raises `TypeError` (verified). Fix: `key_ovis = event.get("key_ovis"); if not isinstance(key_ovis, list): key_ovis = []`.
4. `tests/test_stage1_story_map.py:163` (class 4): the odd-data row asserts `"not an object"`, which the spec does not quote. Fix: assert the item id, for example `["doc"]`, instead of the wording.

## coverage

none.

## scenes

1. `tests/test_stage1_scenes.py:177` (class 4): the duplicate-id test asserts `"duplicate scene id"`, which the spec does not quote. Fix: keep the test but assert the item id only, e.g. `any(e.startswith("S1:") for e in errs)`, and assert that the message set differs from the valid baseline. The collateral-match problem is fixed, so the wording is the only remaining issue.
2. `tests/test_stage1_scenes.py:239` (class 4): asserts `"order"`, which the spec does not quote ("in script order" is rule prose, not a message). Fix: `assert any("S1" in e for e in errs)`.

## shots

1. `scripts/pipeline/stage1/shots.py:168` (class 2): `shot.get("ovi_ids", [])` is iterated without a type check. A shot with `ovi_ids: 5` inside a valid scene raises `TypeError` (verified). Fix: `ovi_ids = shot.get("ovi_ids"); if isinstance(ovi_ids, list): for ovi in ovi_ids: ...`.
2. `scripts/pipeline/stage1/shots.py:179` (class 2): `beat_line_ids` iterated without a type check. `beat_line_ids: None` raises `TypeError` (verified). Fix: `beat_line_ids = shot.get("beat_line_ids"); if not isinstance(beat_line_ids, list): beat_line_ids = []`.
3. `scripts/pipeline/stage1/shots.py:205` (class 2): scene `line_ids` iterated in the "line is in no shot beat" loop with no type check. A scene with `line_ids: 5` raises `TypeError` (verified). Fix: `line_ids = scene.get("line_ids"); if not isinstance(line_ids, list): line_ids = []` before the loop.
4. `tests/test_stage1_shots.py:170` (class 3, Round 1 still open): the row `{"reason": "x", "class": "bad_class"}` sits in a table where `preset` is the base value `01_establishing_shot`. The failure comes from the `else` branch ("is not of type 'null'", verified), so the class enum is never exercised by this row. Fix: set `preset` to `"NEED_NEW"` for this row, as `test_need_new_class_enum` already does, and check the message names `class`.
5. `tests/test_stage1_shots.py:268` (class 4): asserts `"scene has no shots"`, which the spec does not quote. Fix: assert `"S2"` in the error and that the `has no shots` item is the only one for S2, or use the item id only.

## briefs

1. `scripts/pipeline/stage1/briefs.py:118` (class 2, Round 1 still open): `scene_ids = {s.get("scene_id") ...}` builds a set from unvalidated values. A scenes entry with `scene_id: ["S1"]` raises `TypeError: unhashable type: 'list'` (verified). Fix: `scene_ids = {sid for s in scenes_list if isinstance(s, dict) for sid in [s.get("scene_id")] if isinstance(sid, str)}`. Add a regression case.
2. `scripts/pipeline/stage1/briefs.py:78` (class 1): the spec's `references.characters` is `[text...]` (text = 1..400 chars). The schema gives items `{"type": "string"}` with no bounds, so `references.characters: [""]` produces no schema error (verified). Fix: `"characters": {"type": "array", "items": {"type": "string", "minLength": 1, "maxLength": 400}}`. Add a schema test.

## looks

none.

## voices

1. `scripts/pipeline/stage1/voices.py:51` and `:60` (class 2, new): `validate` calls `doc.get` without checking `doc`. `validate(1, [1], ...)` and `validate(1, None, ...)` raise `AttributeError` (verified). Fix: first line of `validate`: `if not isinstance(doc, dict): return ["voices doc: document must be an object"]`.
2. `scripts/pipeline/stage1/voices.py:147` (class 1, false positive, new): when one character is listed twice with the same non-narrator `voice_key`, the code reports `"<char>: voice key shared with another character"` once per entry. Repro: entries `extra_char`, `extra_char` both with key `gajanan` produce two "shared" messages for `extra_char` (verified). The spec's rule is about two different characters. Fix: `non_narrator_chars = sorted({c for c in chars if c != "narrator"})` so repeated entries of one character count once.

## sounds

1. `tests/test_stage1_sounds.py:229, 241, 247, 253, 259` (class 4, partly Round 1 open): the guard and rule asserts include wording the spec does not quote ("document must be an object", "cue must be an object", "scene does not exist", "anchor_line_id must be a string", "sound_id must be a string"). Fix: assert `"cue[0]"` (or `"sounds"` for the document row) only, as the spec requires.

## questions

none.

---

## Defects per unit (Round 2)

| Unit | Defects |
|---|---|
| story_map | 4 |
| coverage | 0 |
| scenes | 2 |
| shots | 5 |
| briefs | 2 |
| looks | 0 |
| voices | 2 |
| sounds | 1 |
| questions | 0 |
| **Total** | **16** |

Notes:
- Three of the new raises (story_map 1-3, shots 1-3, briefs 1, voices 1) would have been caught by the odd-data tests the spec asks for. Those tests should gain the cases listed above when the fixes land.
- The pytest count printed is 400 (the brief says 415). Confirm which run the coder counted.
