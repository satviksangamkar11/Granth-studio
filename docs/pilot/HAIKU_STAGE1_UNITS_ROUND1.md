# Stage 1 unit modules: review (read-only)

Scope: `scripts/pipeline/stage1/{story_map,coverage,scenes,shots,briefs,looks,voices,sounds,questions}.py` and `tests/test_stage1_<unit>.py`, against `docs/pilot/nemotron_specs/unit_<unit>.md`, `stage1_base.json` and `STAGE1_RULES.md`.

Evidence: `uv run pytest -q --tb=short tests/test_stage1_*.py` gives 333 passed. Raises and misses below were reproduced by calling the modules in memory (no files written, no network). No print, env, key or secret handling was found in any module or test.

## Verdict: FIX FIRST

---

## story_map

Module `scripts/pipeline/stage1/story_map.py`

1. L70, L81-83, L106-116: `validate` raises on odd data. `doc` not a dict, an `ovi_types` item not a dict, or `ovi_range` holding non-ints gives AttributeError/TypeError (reproduced: `ovi_types: [1]` and `ovi_range: ["a", 5]`). Fix: return early if `doc` is not a dict; skip non-dict items; before `lo > hi` (L108) and `kovi < lo` (L115) require `isinstance(lo, int) and isinstance(hi, int)`; require `isinstance(ovi, int)` before L82.

Tests `tests/test_stage1_story_map.py`

2. L153 and L155: assert `"lo > hi"`, `"key_ovi"`, `"outside"`. The spec quotes none of these (class 4). Fix: assert `"E1"` only.
3. L155 (`key_ovis` below range): the `kovi < lo` branch has no failing test; removing it passes the suite (class 3). Fix: add row `(1, [(["events", 0, "key_ovis"], [0])], ["E1"])`.

## coverage

Module `scripts/pipeline/stage1/coverage.py`

1. L74, L85-88, L94, L103: `validate` raises. `doc` not a dict or `ovis` items not dicts gives AttributeError (reproduced: `ovis: ["x"]`); an unhashable `ovi` (list) gives TypeError at `ovi not in ovi_dispositions` (reproduced). Fix: return early if `doc` is not a dict; if `ovis` is not a list use `[]`; skip non-dict entries; skip entries whose `ovi` is not an int before using it as a key.

Tests: none.

## scenes

Module `scripts/pipeline/stage1/scenes.py`

1. L155-157: out-of-order check is lost after an unknown line id. `prev_idx` is set to -1 for a line not in the script, so `['S1-L2','S9-L9','S1-L1']` reports only `S9-L9` and misses the order error (reproduced; class 1). Fix: update `prev_idx` only when `idx != -1`, and compare only in that case.
2. L136-138: `turn` check raises when `ovi_range` bounds are not ints (reproduced: `ovi_range: ["1", 5]`, turn ovi 3 gives TypeError). Fix: check `isinstance(lo, int) and isinstance(hi, int)` before `lo <= turn_ovi <= hi`.
3. L116, L145, L147: unhashable `scene_id` or `line_id` raises TypeError (reproduced with `scene_id: ["S1"]`). Fix: skip or report non-string ids before set membership.
4. L59-61 (schema, story `then`): `teaching_treatment: "none"` is rejected for story scenes. The spec says "must be absent or none for story"; `validate` L164 accepts it, so schema and semantics disagree (reproduced). Fix: replace the story `then` with `{"properties": {"teaching_treatment": {"const": "none"}}}`.

Tests `tests/test_stage1_scenes.py`

5. L165-167 (duplicate scene id): the case passes with the duplicate-id rule removed, because `"S1"` also matches `"S1-L1: line used in multiple scenes"` and `"S1: ovi_range overlaps with S1"` (both reproduced). Fix: assert `"duplicate scene id"` in errs.

## shots

Module `scripts/pipeline/stage1/shots.py`

1. L131-133: `continue` for a shot whose scene is missing skips the preset check (L154-155). Reproduced: shot `S9-1` with preset `bogus` and no scene S9 reports only `scene S9 does not exist`; the spec requires `preset` to be in `preset_ids` or NEED_NEW for every shot. Fix: run the preset check (and beat coverage, L147-150) before the `continue`.
2. L96, L99, L118, L131, L139-142: raises on odd data. `docs["scenes"]` not a dict gives AttributeError (reproduced); unhashable `scene_id` or `shot_id` gives TypeError (reproduced); scene `ovi_range` that is not a 2-int list gives TypeError. Fix: type-guard `docs["scenes"]`, scenes, shots, ids and bounds before use.
3. L48 (schema): `preset` is any string. The spec's preset id pattern `^[0-9]{2}_[a-z0-9_]+$` (or the exact string NEED_NEW) is not enforced. Fix: `"preset": {"type": "string", "pattern": "^([0-9]{2}_[a-z0-9_]+|NEED_NEW)$"}`.

Tests `tests/test_stage1_shots.py`

4. L263-267 (`test_every_scene_has_shots`): the assertion `"S2" in e` also matches `"S2-L1: line is in no shot beat"`, so the test passes without the "scene has no shots" rule (reproduced messages: `['S2: scene has no shots', 'S2-L1: line is in no shot beat']`). Fix: assert `"scene has no shots"` in errs.
5. L243: asserts `"consecutive"`, which the spec does not quote (class 4). Fix: assert `"S1"` and the item id only.
6. L169 (`test_shot_field_types_and_formats`): the `need_new` row with class `bad_class` uses a non-NEED_NEW preset, so the error comes from the `else` branch and the class enum is never exercised (class 3). Fix: set `preset` to `"NEED_NEW"` first, as `test_need_new_class_enum` does.

## briefs

Module `scripts/pipeline/stage1/briefs.py`

1. L118, L127-128, L139, L145, L148, L157: non-string `scene_id`, `image_id` or `shot_id` raises. Reproduced: `scene_id: ["S1"]` gives TypeError; `image_id: 5` gives AttributeError at `.startswith`. Fix: type-guard these values with `isinstance(x, str)` before set, dict and regex use.

Schema `briefs.py`

2. L55-58, L62, L65-67, L79-80: the spec's common type `text = string 1..400 chars` is not enforced. `people.position/pose/gaze`, `camera`, `light`, `reason_new`, `place_id`, `references.place` and `references.style_anchor` have no 1..400 bounds. Reproduced: `pose: ""` gives no schema error. Fix: add `"minLength": 1, "maxLength": 400` to each, and `"maxLength": 400` to `people.name`.

Tests `tests/test_stage1_briefs.py`

3. L263, L265, L267, L269, L271, L273, L275: asserts `"unique with scene prefix"`, `"scene exists"`, `"shot_ids exist and belong to the same scene"`, `"no empty name"` and `"non-empty"`. The spec quotes none of these (class 4). Fix: assert the item id only.

## looks

Module `scripts/pipeline/stage1/looks.py`: none.

Tests `tests/test_stage1_looks.py`: none.

## voices

Module `scripts/pipeline/stage1/voices.py`

1. L76-81: the spec's "every speaking_character has exactly one cast entry" is enforced only for RECURRING duplicates. Two non-RECURRING entries for one character pass silently (reproduced: two NEW_PROPOSED entries for `a` with keys `narrator` and `gajanan` return `[]`). Fix: for any `len(entries) > 1` add `f"{char}: listed more than once"`, and keep the RECURRING branch.
2. L59, L63-69, L84-104: raises on odd data. `cast` None gives TypeError (reproduced); non-dict entries give AttributeError; unhashable `character_id` or `voice_key` gives TypeError (reproduced). Fix: `cast = doc.get("cast")`; if not a list use `[]`; skip non-dict entries; type-guard `character_id` and `voice_key` as strings.

Tests `tests/test_stage1_voices.py`

3. L134-146 (schema): required fields are never tested by deletion. Every row sets the value to None, which only exercises the type rule, so removing `required` from SCHEMA passes the suite (class 3). Fix: add rows that delete `cast.0.character_id`, `cast.0.voice_key`, `cast.0.voice_id`, `cast.0.gender` and `cast.0.status`.
4. L180, L186, L192: asserts `"recurring character listed twice"` and `"voice key shared with another character"`, which the spec does not quote (class 4). Fix: assert the item id only (`"narrator"`, `"extra_char"`, `"char1"`).

## sounds

Module `scripts/pipeline/stage1/sounds.py`

1. L98: `sound_id.startswith` raises AttributeError when a cue lacks `sound_id` or it is not a string (reproduced). Also L62-63, L67-68, L75 and L81 raise on non-dict scenes or cues, or unhashable `scene_id`. Fix: guard `sound_id` with `isinstance(sound_id, str)` before L98, and skip non-dict cues and scenes.

Tests `tests/test_stage1_sounds.py`

2. L178, L180, L182, L184, L186 and L219: assert `"scene exists"`, `"anchor line belongs to the scene"`, `"sound_id in sound_ids or NEED_NEW"` and `"kind matches the id prefix"`, which the spec does not quote (class 4). Fix: assert `"cue[0]"` only.

## questions

Module `scripts/pipeline/stage1/questions.py`

1. L60, L62 and L84: the earlier fix guards non-dict `doc`, `docs` and `scenes` only. An unhashable `id` (L60) or `scene_id` (L84) still raises TypeError (reproduced with `id: ["Q1"]` and `scene_id: ["S1"]`). Fix: `if not isinstance(qid, str)` before L60, and `if not isinstance(scene_id, str)` before L84.

Tests `tests/test_stage1_questions.py`

2. L208-220 (`test_validate_odd_data_no_raise`): no case uses an unhashable `id` or `scene_id`, which is why defect 1 is not caught (class 3). Fix: add `{"id": ["Q1"], "text": "t"}` and `{"id": "Q1", "text": "t", "scene_id": ["S1"]}` cases asserting `isinstance(errs, list)`.

---

## Defects per unit

| Unit | Defects |
|---|---|
| story_map | 3 |
| coverage | 1 |
| scenes | 5 |
| shots | 6 |
| briefs | 3 |
| looks | 0 |
| voices | 4 |
| sounds | 2 |
| questions | 2 |
| Total | 26 |
