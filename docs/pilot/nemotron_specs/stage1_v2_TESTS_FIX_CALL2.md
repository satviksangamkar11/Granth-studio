# FIX CALL 2 for the TEST files. Write ONLY `tests/test_stage1_schemas.py` and `tests/test_validate_stage1.py` (not the modules). Two independent reviewers (Codex and a Haiku agent) both said FIX FIRST on your second tests. Apply EVERY point below. IMPORTANT quality rules: (a) make the tests COMPACT and TABLE-DRIVEN: one baseline valid fixture builder (note-free, uses NEW look states so it validates to []), and a mutation helper that deep-copies the baseline and applies ONE change; each rule = one parametrized row asserting the mandated keyword/item id; target under 900 lines per file; (b) positive cases assert `[]` exactly; (c) required-field tests must DELETE the field from a deep copy of a valid document; (d) assert rejection + the offending field name for jsonschema errors (never the literal text of jsonschema messages); (e) a scene id `S0` and an image id `s9_wrong` are SCHEMA-valid (prefix and scene matching are semantic); (f) the ACTUAL legacy schemas are given below, use them verbatim as the frozen expectation; (g) validator tests generate schemas into tmp_path with `write_all` and pass `schema_dir=`; (h) the aggregate test must produce each violation it asserts (verify by reading your own fixture: nothing may overwrite or delete the violating item); (i) test_overwrite_replaces must corrupt a generated file first and check restoration. Reply with exactly two FILE blocks.

## UPDATED SPEC
# Spec (shared by the TEST call and the CODE call): Stage 1 contract v2 = schemas + semantic validator

Files (replace the old ones; the old frozen tests are superseded and will be replaced by the new tests):
- `scripts/pipeline/make_schemas.py`: writes `schemas/<name>.schema.json` (JSON Schema draft 2020-12) for the names below; refuses to overwrite unless `--overwrite`; `additionalProperties: false` on EVERY Stage 1 object (nested ones too); the old four non-Stage-1 schemas (beats, image_catalog, animation_scene, shot_plan) stay EXACTLY as they are today (copy their definitions unchanged).
- `scripts/pipeline/validate_stage1.py`: `validate_stage1(...)` (below).
- Tests: `tests/test_stage1_schemas.py` and `tests/test_validate_stage1.py`.

Style: `from __future__ import annotations`, standard library plus `jsonschema`; tests use only synthetic data and `tmp_path`; modules load by path with importlib (`ROOT = Path(__file__).resolve().parents[1]`). No print, no network. The validator never raises for bad data: it returns a list of error strings (stable order; each message starts with the item id or the document name).

## Ids and common types
scene_id `^S[0-9]{1,2}$`; shot_id `^S[0-9]{1,2}-[0-9]{1,2}$`; line_id `^S[0-9]{1,2}-L[0-9]{1,3}$`; image id (Stage 1 brief) `^s[0-9]{1,2}_[a-z][a-z0-9_]{0,40}$`; ovi = integer >= 1; adhyay = integer 1..21; text = string 1..400 chars; preset id = string matching `^[0-9]{2}_[a-z0-9_]+$`; sound id `^(bed|fx)_[a-z0-9_]+$`.

## The nine Stage 1 documents (every one has `adhyay` plus the fields below)
1. `stage1_story_map`: `ovi_types`: array of {ovi, type: STORY|TEACHING|PHILOSOPHY|INVOCATION|RECAP|PHALASHRUTI|OTHER}; `events`: array of {event_id `^E[0-9]{1,2}$`, title, ovi_range [lo,hi], key_ovis [ovi...], kind: story|discourse, closure: RESOLVED_IN_ADHYAY|CONTINUES_NEXT_ADHYAY|STARTED_EARLIER|SOURCE_INCOMPLETE_OR_AMBIGUOUS|NA}.
2. `stage1_coverage`: `ovis`: array of {ovi, disposition: VISUALISED|NARRATED|QUOTED|MERGED_EQUIVALENT|PROPOSE_OMISSION, reason (text, REQUIRED when PROPOSE_OMISSION or MERGED_EQUIVALENT, else optional), covered_by (line_id or ovi, REQUIRED when MERGED_EQUIVALENT, else optional)}. The schema enforces the REQUIRED rules with `if/then`.
3. `stage1_scenes`: `scenes`: array of {scene_id, section_kind: story|discourse, ovi_range [lo,hi], goal, turn {ovi, text}, line_ids [line_id...], teaching_treatment: none|narration_over_typography|contemplative_hold|symbol_from_text (REQUIRED when section_kind is discourse; must be absent or "none" for story)}.
4. `stage1_shots`: `shots`: array of {shot_id, scene_id, ovi_ids [ovi...], beat_line_ids [line_id...], preset: a preset id OR the exact string NEED_NEW, need_new: null OR {reason text, class: missing_image|json_arrangement|renderer_gap}, needs_cutout boolean, pose text, framing text}. If preset is NEED_NEW then need_new must be an object; otherwise it must be null (schema `if/then`). NO free-text preset hint field.
5. `stage1_image_briefs`: `images`: array of {image_id, scene_id, shot_ids [shot_id...], people [{name, position, pose, gaze}], place_id, prop (text or null), prop_state (text or null), camera, light, reason_new, on_screen_facts [text...] (only things visible), references {characters [text...], place text, style_anchor text, prop text or null}}.
6. `stage1_canon_looks`: `entries`: array of {entity_id, kind: character|place|prop, state_id, look text, source_ovis [ovi...] (min 1), basis: stated|inferred}. No other fields (no events, no dialogue).
7. `stage1_voice_cast`: `cast`: array of {character_id, voice_key, voice_id (string 10..40 chars), gender: male|female, status: RECURRING|NEW_PROPOSED}.
8. `stage1_sound_suggestions`: `cues`: array of {scene_id, anchor_line_id (line_id), sound_id (sound id OR the exact string NEED_NEW), kind: bed|fx, sound_prompt (text, REQUIRED when sound_id is NEED_NEW, else absent), purpose text, basis: stated|staging}. NO duration/loop/timing fields.
9. `stage1_questions`: `questions`: array of {id `^Q[0-9]+$`, text, scene_id (optional)}.

## `validate_stage1(adhyay, docs, ctx) -> list[str]`
`docs` = dict with the nine documents under the keys story_map, coverage, scenes, shots, briefs, looks, voices, sounds, questions. `ctx` = dict with: `script_line_ids` (ordered list), `core_line_ids` (set), `chapter_ovis` (set of int), `unfilmed_ovis` (set of int), `preset_ids` (set), `sound_ids` (set of AVAILABLE sound ids), `saved_voices` (dict voice_key -> voice_id), `speaking_characters` (set of character ids that speak in the script), `known_states` (dict entity_id -> set of state_ids already in series data).
Steps (collect errors of ALL semantic steps; return at once only if a schema step fails):
1. Schema: each document against its schema; message "<document> <path>: <message>". If any schema error, return them all and stop.
2. adhyay equal in every document ("<document> adhyay <n> does not match <adhyay>").
3. story_map: each ovi in `chapter_ovis` typed exactly once ("ovi <n> is untyped" / "ovi <n> is typed twice"); typed ovis outside the chapter reported; events ovi_range lo <= high; key_ovis inside their range.
4. coverage: every ovi of `chapter_ovis` has exactly one disposition ("ovi <n> has no disposition" / "twice"); PROPOSE_OMISSION is allowed but reported as a NOTE message starting "note: ovi <n> omission proposed, owner approval needed" (notes are returned in the list after the errors); an ovi in `unfilmed_ovis` must not be VISUALISED ("ovi <n> is unfilmed but VISUALISED"); covered_by must refer to a script line id or a chapter ovi.
5. scenes: scene ids unique; ranges ordered lo <= hi and non-overlapping; every chapter ovi not unfilmed is inside a scene range; an unfilmed ovi inside a range is an error ("<scene>: ovi <n> is unfilmed but inside the range"); ovis outside the chapter are errors; turn ovi inside its range; line ids exist in `script_line_ids`, none used twice, in script order within a scene, and every core line is in a scene; a discourse scene has a teaching_treatment other than none.
6. shots: shot ids unique and consecutive per scene from 1; scene exists; ovi_ids inside the scene range; beat_line_ids belong to the scene; every scene has shots; every line of every scene is in some shot's beat_line_ids (message "<line>: line is in no shot beat"); `preset` is in `preset_ids` or NEED_NEW ("<shot>: unknown preset <p>").
7. briefs: image ids unique with scene prefix (scene S4 -> `s4_`); scene exists; shot_ids exist and belong to the same scene; every brief's people has no empty name; on_screen_facts non-empty.
8. looks: source_ovis inside `chapter_ovis`; an entry whose entity_id is a key of `known_states` and whose state_id is already in `known_states[entity_id]` is an error ("<entity>: known state <state_id> redecided"); a state_id that is NOT yet known for a known entity is allowed (a new state); entity_id+state_id unique inside the document.
9. voices: every `speaking_characters` member has exactly one cast entry ("<character>: no voice assigned"); voice_key must be a key of `saved_voices` and voice_id must equal `saved_voices[voice_key]` ("<character>: voice not in the saved cast"); a character already RECURRING must not be listed twice; two characters must not share a voice_key unless one is the narrator.
10. sounds: scene exists; anchor line belongs to the scene; sound_id in `sound_ids` or NEED_NEW; NEED_NEW needs sound_prompt (schema) — and a non-NEED_NEW cue must not carry sound_prompt; kind matches the id prefix.
11. questions: ids unique; scene exists if given.
The messages must contain the keywords written in quotes above.

## Tests required (write them adversarially; each rule has its own failing case; also deliberately-broken-implementation style cases)
Schema tests per document (valid example passes; extra key fails; each enum value; each `if/then` rule: PROPOSE_OMISSION without reason, MERGED_EQUIVALENT without covered_by, discourse scene without treatment, NEED_NEW shot without need_new, non-NEED_NEW shot with need_new, NEED_NEW sound without sound_prompt, sound with a timing key `duration_seconds`, canon look with an `events` key, shot with the old key `preset_hint`). Validator tests: a fully valid set returns []; every numbered rule above fails on its own with its keyword; zero-story chapter (all ovis TEACHING/PHILOSOPHY, one discourse scene, no story events) validates; messages are stable (same input, same output); missing references never raise; the old four schemas are unchanged (compare to saved copies written in the test from their expected key sets).


## Clarifications added after the Codex review of the first tests (binding for tests and code)
- API: `make_schemas.py` exposes `write_all(out_dir, overwrite=False) -> list[Path]` (writes the 13 schemas: nine Stage 1 + the four legacy ones unchanged; raises FileExistsError if a target exists and overwrite is False) and `main()` (CLI `--out`, `--overwrite`) calling it. Legacy schemas keep their current definitions exactly (beats: top-level keys adhyay + scenes; image_catalog: adhyay + images; animation_scene: adhyay + scene_id + shots; shot_plan: adhyay, scene_id, fingerprints, shots, approved_by, approved_date). Schemas use dialect `https://json-schema.org/draft/2020-12/schema`.
- Validator tests generate the schemas into tmp_path and pass that folder to the validator through a keyword argument `schema_dir=None` (default: the repository `schemas/` folder next to `scripts`).
- The baseline valid fixture must be NOTE-FREE (no PROPOSE_OMISSION) and `validate_stage1` must return `[]` for it. A PROPOSE_OMISSION adds exactly one message that STARTS with `note: ` (notes come after all error messages; an omission is not an error).
- Messages: tests assert only the quoted keywords/phrases of this spec plus the item id; for rules without a quoted phrase the message is `<item id>: <condition in plain words>` and tests only check that the item id appears.
- story_map `events` may be an empty array (zero-story chapter): valid. A zero-story chapter = every ovi typed TEACHING/PHILOSOPHY/INVOCATION/..., one `discourse` scene, empty events.
- Context defaults in test helpers: use `None` as the default and replace only when the argument is None, so intentionally empty sets/dicts survive; tests must include empty-context cases that produce specific missing-reference messages (e.g. "<line>: line is not in the script").
- Tests live at their final location `tests/` (so `ROOT = Path(__file__).resolve().parents[1]` is correct there); the review staging copy is relocated before running.
- Keyword rule for sound: a non-NEED_NEW cue carrying `sound_prompt` is a SCHEMA error (the schema forbids it).


## CODEX ROUND-2 REVIEW (apply all 14)
**FIX FIRST.**

S = [test_stage1_schemas.py](</D:/aai work/granthstudio/docs/pilot/nemotron_specs/review_stage1_tests_v2/test_stage1_schemas.py>); V = [test_validate_stage1.py](</D:/aai work/granthstudio/docs/pilot/nemotron_specs/review_stage1_tests_v2/test_validate_stage1.py>). References below are file:line.

1. **HIGH — Items 2, 10: invalid positive fixtures** (V:44, 205, 213, 221). `make_valid_docs()` redecides all three default known states. Consequently `test_fully_valid_returns_empty`, `test_known_entity_new_state_id_allowed` and `test_narrator_can_share_voice_key` reject conforming behavior. Use new states throughout the baseline; introduce known-state collisions only in negative tests. The new-state positive must also repair Krishna and battlefield.

2. **HIGH — Item 5: invented legacy definitions** (S:46–188; `test_*_schema_exact`). All four embedded expectations differ from repository schemas. Examples: beats invents `beat_id/description`; image_catalog replaces the images dictionary with an array; animation_scene invents duration/camera fields; shot_plan replaces its fingerprints. Embed accurate, complete frozen definitions, including titles and constraints.

3. **HIGH — Item 6: contradictory empty-context expectation** (V:1239, `test_missing_references_no_exception`). With `chapter_ovis=set()`, no chapter ovi requires typing or disposition; ovi 1 already has both anyway. Replace line 1259 with an actual missing-reference diagnostic, such as the mandated unknown-preset or saved-cast error.

4. **HIGH — Item 7: contradictory phase-control assertions** (V:287, `test_schema_error_stops_early`). Line 301 requires the semantic adhyay mismatch that line 310 forbids. Remove line 301 and assert absence of *all* semantic diagnostics while retaining both schema errors.

5. **HIGH — Item 7: aggregate test asserts nonexistent violations** (V:312, `test_collects_all_semantic_steps`). The `[99]` look source is overwritten; voices are empty, so there is no saved-cast mismatch or duplicate; sound kind remains consistent; renaming `S1-2` before filtering leaves its beat present. Construct the violations actually asserted, or assert one deliberately introduced violation per semantic step.

6. **HIGH — Item 11: required-field tests never remove fields** (S:1408, `test_required_fields`). Every `doc_base` still contains `missing_field`. Deep-copy it, delete the field, then validate. Extend coverage to required `adhyay` and nested fields, including turn, people, references and `need_new`.

7. **HIGH — New spec contradictions** (S:889, `test_image_id_pattern`; S:1343/1353, `test_common_type_boundaries`). `S0` satisfies the specified scene-ID regex. `s9_wrong` satisfies the image-ID regex; scene-prefix matching is semantic. Accept these schema cases and retain prefix rejection in validator tests.

8. **HIGH — New runtime failure** (V:718, `test_brief_image_id_scene_prefix`). The first `any(...)` has no iterable and references undefined `e`; an isolated probe raises `NameError`. Replace it with a generator over `errs`, checking the actual mutated ID `s9_wrong_prefix`.

9. **HIGH — Item 12: schema assertions reject normal jsonschema diagnostics.** S’s `test_nested_extra_keys_rejected_in_event`, several `test_extra_key_rejected` cases and `test_entity_state_unique_within_document` require literal `additionalProperties`. The helper returns messages such as “Additional properties are not allowed”. Assert rejection and the offending field, or retain structured errors and inspect `error.validator`.

10. **MEDIUM — Item 12: unmandated semantic wording remains.** Examples: `test_scene_range_lo_gt_hi` (V:521), `test_sound_kind_mismatch_prefix` (V:929), `test_brief_empty_person_name` (V:747), and `test_brief_empty_on_screen_facts` (V:754). Apply the clarification: quoted phrases where specified; otherwise check the item ID without prescribing synonyms. Apply this throughout V, including the aggregate test.

11. **MEDIUM — Items 1, 10: ineffective note checks.** `test_propose_omission_note` permits duplicate notes and unrelated errors. Require exactly one note and no errors. `test_notes_follow_errors` (V:1214) deletes its omission, then conditionally skips its assertion. Preserve an omission plus an error; require both before comparing positions.

12. **MEDIUM — Items 4, 9: collateral failures remain.** `test_covered_by_invalid_reference` truncates script context; `test_voice_id_mismatch_saved` removes Krishna’s saved voice; `test_chapter_ovi_not_in_any_scene` leaves ovi 6 untyped and undispositioned. Preserve valid context and repair dependent references in range, line and missing-shot cases.

13. **MEDIUM — Items 8, 11: missing independent failing cases.** `test_core_line_not_in_any_shot_beat` targets non-core `S1-L2`. `test_shot_sequence_starts_at_one` creates duplicate `S1-2`. Repair both. Add invalid-value rejection for every remaining enum, missing-`need_new`, overlong scene ranges, and extra keys in every Stage 1 object, especially turn, people, references and `need_new`.

14. **HIGH — Item 14: validator harness still uses default repository schemas.** V never generates temporary schemas or supplies `schema_dir`. Add that fixture and pass its directory to every validation call. Also strengthen `test_overwrite_replaces` (S:1447): corrupt a generated file first and verify restoration; the current test accepts a no-op overwrite.

Read-only inspection and isolated in-memory probes only; no suite execution, edits, secret access or web use. No definite test-order dependence found.

## HAIKU (low effort, read-only) REVIEW of your second tests, verdict FIX FIRST:
1. Weak: test_shot_need_new_accepted and test_sound_need_new_accepted only assert absence of an id ("S1" also matches "S1-L1"); they must assert errs == []. test_notes_follow_errors is vacuous (its fixture yields no note so its guard skips the check). test_missing_references_no_exception expects an "ovi 1 ... no disposition/untyped" message that the spec never emits when chapter_ovis is empty. Enums with no invalid-value test: scenes section_kind and teaching_treatment, coverage disposition, sound kind and basis, canon kind, voice gender and status, story_map closure and kind (only ovi type has one). covered_by has no negative schema case.
2. test_brief_image_id_scene_prefix: `any("s1_arjuna_standing" in e or "image_id" in e)` uses an undefined `e` (NameError). test_schema_error_stops_early requires a "scenes ... adhyay ... does not match" message at line ~301 that step 1 forbids, then forbids it at ~310. test_collects_all_semantic_steps: renames S1-2 to S1-3 then deletes S1-2, so "consecutive" is never produced; fx_conch is overwritten so "mismatch" is never produced; the cast is empty so "twice"/"voice not in the saved cast" are never produced. test_chapter_ovi_not_in_any_scene leaves ovi 6 untyped. test_brief_empty_on_screen_facts / test_brief_empty_person_name require schema rejection so step 7 is never reached. Invented wording: "outside", "mismatch", "prefix", "shared", "not belong", "no shots", a hard-coded prefix allow-list in test_message_prefixes. Validator tests still use the repository schemas folder (no schema_dir=tmp_path).


## ACTUAL LEGACY SCHEMAS
### schemas/beats.schema.json (the ACTUAL frozen definition; legacy schemas must stay byte-for-byte equal to these; embed them in the test as expected dicts and compare the generated files by json equality)
```json
{
 "$schema": "https://json-schema.org/draft/2020-12/schema",
 "title": "beats",
 "type": "object",
 "additionalProperties": false,
 "required": [
  "adhyay",
  "scenes"
 ],
 "properties": {
  "adhyay": {
   "type": "integer",
   "minimum": 1,
   "maximum": 21
  },
  "scenes": {
   "type": "array",
   "minItems": 0,
   "items": {
    "type": "object",
    "additionalProperties": false,
    "required": [
     "scene_id",
     "beats"
    ],
    "properties": {
     "scene_id": {
      "type": "string",
      "pattern": "^S[0-9]{1,2}$"
     },
     "beats": {
      "type": "array",
      "minItems": 0,
      "items": {
       "type": "object",
       "additionalProperties": false,
       "required": [
        "line_id",
        "voice",
        "mr_s",
        "hi_s",
        "start_s",
        "end_s",
        "shot"
       ],
       "properties": {
        "line_id": {
         "type": "string",
         "pattern": "^S[0-9]{1,2}-L[0-9]{1,3}$"
        },
        "voice": {
         "type": "string",
         "minLength": 1,
         "maxLength": 400
        },
        "mr_s": {
         "type": "number",
         "exclusiveMinimum": 0
        },
        "hi_s": {
         "type": "number",
         "exclusiveMinimum": 0
        },
        "start_s": {
         "type": "number",
         "minimum": 0
        },
        "end_s": {
         "type": "number",
         "exclusiveMinimum": 0
        },
        "shot": {
         "type": "integer",
         "minimum": 1
        }
       }
      }
     }
    }
   }
  }
 }
}
```
### schemas/image_catalog.schema.json (the ACTUAL frozen definition; legacy schemas must stay byte-for-byte equal to these; embed them in the test as expected dicts and compare the generated files by json equality)
```json
{
 "$schema": "https://json-schema.org/draft/2020-12/schema",
 "title": "image_catalog",
 "type": "object",
 "additionalProperties": false,
 "required": [
  "adhyay",
  "images"
 ],
 "properties": {
  "adhyay": {
   "type": "integer",
   "minimum": 1,
   "maximum": 21
  },
  "images": {
   "type": "object",
   "additionalProperties": {
    "type": "object",
    "additionalProperties": false,
    "required": [
     "file",
     "sha256",
     "chosen_version",
     "prompt_sha256",
     "model",
     "edit_id",
     "approved"
    ],
    "properties": {
     "file": {
      "type": "string",
      "minLength": 1,
      "maxLength": 400
     },
     "sha256": {
      "type": "string",
      "pattern": "^[0-9a-f]{64}$"
     },
     "chosen_version": {
      "type": "integer",
      "minimum": 1
     },
     "prompt_sha256": {
      "type": "string",
      "pattern": "^[0-9a-f]{64}$"
     },
     "model": {
      "type": "string",
      "minLength": 1,
      "maxLength": 400
     },
     "edit_id": {
      "type": [
       "string",
       "null"
      ]
     },
     "approved": {
      "type": "boolean"
     }
    }
   }
  }
 }
}
```
### schemas/animation_scene.schema.json (the ACTUAL frozen definition; legacy schemas must stay byte-for-byte equal to these; embed them in the test as expected dicts and compare the generated files by json equality)
```json
{
 "$schema": "https://json-schema.org/draft/2020-12/schema",
 "title": "animation_scene",
 "type": "object",
 "additionalProperties": false,
 "required": [
  "adhyay",
  "scene_id",
  "shots"
 ],
 "properties": {
  "adhyay": {
   "type": "integer",
   "minimum": 1,
   "maximum": 21
  },
  "scene_id": {
   "type": "string",
   "pattern": "^S[0-9]{1,2}$"
  },
  "shots": {
   "type": "array",
   "minItems": 1,
   "items": {
    "type": "object",
    "additionalProperties": false,
    "required": [
     "shot_id",
     "preset",
     "assets",
     "held_pose",
     "transition_out",
     "need_new"
    ],
    "properties": {
     "shot_id": {
      "type": "string",
      "pattern": "^S[0-9]{1,2}-[0-9]{1,2}$"
     },
     "preset": {
      "type": "string",
      "minLength": 1
     },
     "assets": {
      "type": "object",
      "additionalProperties": {
       "type": "string",
       "pattern": "^SH_S[0-9]{1,2}_[0-9]{2}$"
      }
     },
     "held_pose": {
      "type": "string",
      "minLength": 1,
      "maxLength": 400
     },
     "transition_out": {
      "enum": [
       "cut",
       "slide",
       "pan_bridge"
      ]
     },
     "need_new": {
      "anyOf": [
       {
        "type": "null"
       },
       {
        "type": "object",
        "additionalProperties": false,
        "required": [
         "reason",
         "class"
        ],
        "properties": {
         "reason": {
          "type": "string",
          "minLength": 1,
          "maxLength": 400
         },
         "class": {
          "enum": [
           "missing_image",
           "json_arrangement",
           "renderer_gap"
          ]
         }
        }
       }
      ]
     }
    }
   }
  }
 }
}
```
### schemas/shot_plan.schema.json (the ACTUAL frozen definition; legacy schemas must stay byte-for-byte equal to these; embed them in the test as expected dicts and compare the generated files by json equality)
```json
{
 "$schema": "https://json-schema.org/draft/2020-12/schema",
 "title": "shot_plan",
 "type": "object",
 "additionalProperties": false,
 "required": [
  "adhyay",
  "scene_id",
  "fingerprints",
  "shots",
  "approved_by",
  "approved_date"
 ],
 "properties": {
  "adhyay": {
   "type": "integer",
   "minimum": 1,
   "maximum": 21
  },
  "scene_id": {
   "type": "string",
   "pattern": "^S[0-9]{1,2}$"
  },
  "fingerprints": {
   "type": "object",
   "additionalProperties": false,
   "required": [
    "script",
    "timing",
    "presets",
    "images"
   ],
   "properties": {
    "script": {
     "type": "string",
     "pattern": "^[0-9a-f]{64}$"
    },
    "timing": {
     "type": "string",
     "pattern": "^[0-9a-f]{64}$"
    },
    "presets": {
     "type": "string",
     "pattern": "^[0-9a-f]{64}$"
    },
    "images": {
     "type": "object",
     "additionalProperties": {
      "type": "string",
      "pattern": "^[0-9a-f]{64}$"
     }
    }
   }
  },
  "shots": {
   "type": "array",
   "minItems": 1,
   "items": {
    "type": "object",
    "additionalProperties": false,
    "required": [
     "shot_id",
     "preset",
     "assets",
     "held_pose",
     "transition_out",
     "need_new"
    ],
    "properties": {
     "shot_id": {
      "type": "string",
      "pattern": "^S[0-9]{1,2}-[0-9]{1,2}$"
     },
     "preset": {
      "type": "string",
      "minLength": 1
     },
     "assets": {
      "type": "object",
      "additionalProperties": {
       "type": "string",
       "pattern": "^SH_S[0-9]{1,2}_[0-9]{2}$"
      }
     },
     "held_pose": {
      "type": "string",
      "minLength": 1,
      "maxLength": 400
     },
     "transition_out": {
      "enum": [
       "cut",
       "slide",
       "pan_bridge"
      ]
     },
     "need_new": {
      "anyOf": [
       {
        "type": "null"
       },
       {
        "type": "object",
        "additionalProperties": false,
        "required": [
         "reason",
         "class"
        ],
        "properties": {
         "reason": {
          "type": "string",
          "minLength": 1,
          "maxLength": 400
         },
         "class": {
          "enum": [
           "missing_image",
           "json_arrangement",
           "renderer_gap"
          ]
         }
        }
       }
      ]
     }
    }
   }
  },
  "approved_by": {
   "type": "string",
   "minLength": 1,
   "maxLength": 400
  },
  "approved_date": {
   "type": "string",
   "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
  }
 }
}
```


## YOUR PREVIOUS tests/test_stage1_schemas.py (to repair, or rewrite more compactly)
```python
from __future__ import annotations

import json
import importlib.util
import sys
from pathlib import Path

import pytest
import jsonschema

ROOT = Path(__file__).resolve().parents[1]

# Load make_schemas module by path
spec = importlib.util.spec_from_file_location(
    "make_schemas", ROOT / "scripts" / "pipeline" / "make_schemas.py"
)
make_schemas = importlib.util.module_from_spec(spec)
sys.modules["make_schemas"] = make_schemas
spec.loader.exec_module(make_schemas)


@pytest.fixture(scope="session")
def schemas_dir(tmp_path_factory):
    """Generate all schemas into a temp directory once per session."""
    out_dir = tmp_path_factory.mktemp("schemas")
    written = make_schemas.write_all(out_dir, overwrite=False)
    assert written, "no schemas written"
    return out_dir


def load_schema(schemas_dir: Path, name: str) -> dict:
    path = schemas_dir / f"{name}.schema.json"
    assert path.exists(), f"schema {name} not found at {path}"
    return json.loads(path.read_text())


def validate(instance: dict, schema: dict) -> list[str]:
    """Return list of validation error messages (empty if valid)."""
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)
    return [f"{'.'.join(str(p) for p in e.path) or 'root'}: {e.message}" for e in errors]


# ======================================================================
# Expected frozen legacy schemas (copied from current repository state)
# ======================================================================
EXPECTED_BEATS_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["adhyay", "scenes"],
    "properties": {
        "adhyay": {"type": "integer", "minimum": 1, "maximum": 21},
        "scenes": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["scene_id", "beats"],
                "properties": {
                    "scene_id": {"type": "string", "pattern": "^S[0-9]{1,2}$"},
                    "beats": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["beat_id", "line_id", "description"],
                            "properties": {
                                "beat_id": {"type": "string", "pattern": "^B[0-9]{1,3}$"},
                                "line_id": {"type": "string", "pattern": "^S[0-9]{1,2}-L[0-9]{1,3}$"},
                                "description": {"type": "string", "minLength": 1, "maxLength": 400},
                            },
                        },
                    },
                },
            },
        },
    },
}

EXPECTED_IMAGE_CATALOG_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["adhyay", "images"],
    "properties": {
        "adhyay": {"type": "integer", "minimum": 1, "maximum": 21},
        "images": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["image_id", "scene_id", "shot_id", "prompt", "negative_prompt", "width", "height", "seed", "model", "approved"],
                "properties": {
                    "image_id": {"type": "string", "pattern": "^s[0-9]{1,2}_[a-z][a-z0-9_]{0,40}$"},
                    "scene_id": {"type": "string", "pattern": "^S[0-9]{1,2}$"},
                    "shot_id": {"type": "string", "pattern": "^S[0-9]{1,2}-[0-9]{1,2}$"},
                    "prompt": {"type": "string", "minLength": 1, "maxLength": 2000},
                    "negative_prompt": {"type": "string", "maxLength": 2000},
                    "width": {"type": "integer", "minimum": 64, "maximum": 2048},
                    "height": {"type": "integer", "minimum": 64, "maximum": 2048},
                    "seed": {"type": "integer", "minimum": 0, "maximum": 2147483647},
                    "model": {"type": "string", "minLength": 1},
                    "approved": {"type": "boolean"},
                },
            },
        },
    },
}

EXPECTED_ANIMATION_SCENE_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["adhyay", "scene_id", "shots"],
    "properties": {
        "adhyay": {"type": "integer", "minimum": 1, "maximum": 21},
        "scene_id": {"type": "string", "pattern": "^S[0-9]{1,2}$"},
        "shots": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["shot_id", "duration_frames", "camera", "lighting", "assets"],
                "properties": {
                    "shot_id": {"type": "string", "pattern": "^S[0-9]{1,2}-[0-9]{1,2}$"},
                    "duration_frames": {"type": "integer", "minimum": 1},
                    "camera": {"type": "string", "minLength": 1},
                    "lighting": {"type": "string", "minLength": 1},
                    "assets": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["asset_id", "transform"],
                            "properties": {
                                "asset_id": {"type": "string", "minLength": 1},
                                "transform": {"type": "object"},
                            },
                        },
                    },
                },
            },
        },
    },
}

EXPECTED_SHOT_PLAN_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["adhyay", "scene_id", "fingerprints", "shots", "approved_by", "approved_date"],
    "properties": {
        "adhyay": {"type": "integer", "minimum": 1, "maximum": 21},
        "scene_id": {"type": "string", "pattern": "^S[0-9]{1,2}$"},
        "fingerprints": {
            "type": "object",
            "additionalProperties": False,
            "required": ["story_map", "coverage", "scenes", "shots", "briefs", "looks", "voices", "sounds", "questions"],
            "properties": {
                "story_map": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
                "coverage": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
                "scenes": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
                "shots": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
                "briefs": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
                "looks": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
                "voices": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
                "sounds": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
                "questions": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
            },
        },
        "shots": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["shot_id", "image_id", "animation_shot_id"],
                "properties": {
                    "shot_id": {"type": "string", "pattern": "^S[0-9]{1,2}-[0-9]{1,2}$"},
                    "image_id": {"type": "string", "pattern": "^s[0-9]{1,2}_[a-z][a-z0-9_]{0,40}$"},
                    "animation_shot_id": {"type": "string", "pattern": "^S[0-9]{1,2}-[0-9]{1,2}$"},
                },
            },
        },
        "approved_by": {"type": "string", "minLength": 1},
        "approved_date": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"},
    },
}


class TestStage1StoryMapSchema:
    def test_valid_minimal(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_story_map")
        doc = {
            "adhyay": 1,
            "ovi_types": [
                {"ovi": 1, "type": "STORY"},
                {"ovi": 2, "type": "TEACHING"},
            ],
            "events": [
                {
                    "event_id": "E1",
                    "title": "Arjuna's dilemma",
                    "ovi_range": [1, 2],
                    "key_ovis": [1],
                    "kind": "story",
                    "closure": "RESOLVED_IN_ADHYAY",
                }
            ],
        }
        assert validate(doc, schema) == []

    def test_valid_empty_events(self, schemas_dir):
        """Zero-story chapter: events array may be empty."""
        schema = load_schema(schemas_dir, "stage1_story_map")
        doc = {
            "adhyay": 1,
            "ovi_types": [{"ovi": 1, "type": "TEACHING"}],
            "events": [],
        }
        assert validate(doc, schema) == []

    def test_extra_key_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_story_map")
        doc = {
            "adhyay": 1,
            "ovi_types": [{"ovi": 1, "type": "STORY"}],
            "events": [],
            "extra_field": "not allowed",
        }
        errs = validate(doc, schema)
        assert any("extra_field" in e or "additionalProperties" in e for e in errs)

    def test_all_ovi_type_enums(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_story_map")
        for t in [
            "STORY",
            "TEACHING",
            "PHILOSOPHY",
            "INVOCATION",
            "RECAP",
            "PHALASHRUTI",
            "OTHER",
        ]:
            doc = {"adhyay": 1, "ovi_types": [{"ovi": 1, "type": t}], "events": []}
            assert validate(doc, schema) == [], f"enum {t} failed"

    def test_event_closure_enums(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_story_map")
        for c in [
            "RESOLVED_IN_ADHYAY",
            "CONTINUES_NEXT_ADHYAY",
            "STARTED_EARLIER",
            "SOURCE_INCOMPLETE_OR_AMBIGUOUS",
            "NA",
        ]:
            doc = {
                "adhyay": 1,
                "ovi_types": [{"ovi": 1, "type": "STORY"}],
                "events": [
                    {
                        "event_id": "E1",
                        "title": "t",
                        "ovi_range": [1, 1],
                        "key_ovis": [1],
                        "kind": "story",
                        "closure": c,
                    }
                ],
            }
            assert validate(doc, schema) == [], f"closure {c} failed"

    def test_event_kind_enum(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_story_map")
        for k in ["story", "discourse"]:
            doc = {
                "adhyay": 1,
                "ovi_types": [{"ovi": 1, "type": "STORY"}],
                "events": [
                    {
                        "event_id": "E1",
                        "title": "t",
                        "ovi_range": [1, 1],
                        "key_ovis": [1],
                        "kind": k,
                        "closure": "NA",
                    }
                ],
            }
            assert validate(doc, schema) == [], f"kind {k} failed"

    def test_invalid_ovi_type_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_story_map")
        doc = {
            "adhyay": 1,
            "ovi_types": [{"ovi": 1, "type": "INVALID"}],
            "events": [],
        }
        errs = validate(doc, schema)
        assert errs

    def test_invalid_event_id_pattern(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_story_map")
        doc = {
            "adhyay": 1,
            "ovi_types": [{"ovi": 1, "type": "STORY"}],
            "events": [
                {
                    "event_id": "X1",
                    "title": "t",
                    "ovi_range": [1, 1],
                    "key_ovis": [1],
                    "kind": "story",
                    "closure": "NA",
                }
            ],
        }
        errs = validate(doc, schema)
        assert errs

    def test_event_ovi_range_exactly_two_items(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_story_map")
        # too few
        doc = {
            "adhyay": 1,
            "ovi_types": [{"ovi": 1, "type": "STORY"}],
            "events": [{"event_id": "E1", "title": "t", "ovi_range": [1], "key_ovis": [1], "kind": "story", "closure": "NA"}],
        }
        errs = validate(doc, schema)
        assert errs
        # too many
        doc["events"][0]["ovi_range"] = [1, 2, 3]
        errs = validate(doc, schema)
        assert errs

    def test_nested_extra_keys_rejected_in_event(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_story_map")
        doc = {
            "adhyay": 1,
            "ovi_types": [{"ovi": 1, "type": "STORY"}],
            "events": [
                {
                    "event_id": "E1",
                    "title": "t",
                    "ovi_range": [1, 1],
                    "key_ovis": [1],
                    "kind": "story",
                    "closure": "NA",
                    "extra_nested": "no",
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("additionalProperties" in e for e in errs)


class TestStage1CoverageSchema:
    def test_valid_minimal(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_coverage")
        doc = {
            "adhyay": 1,
            "ovis": [
                {"ovi": 1, "disposition": "VISUALISED"},
                {"ovi": 2, "disposition": "NARRATED"},
            ],
        }
        assert validate(doc, schema) == []

    def test_extra_key_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_coverage")
        doc = {
            "adhyay": 1,
            "ovis": [{"ovi": 1, "disposition": "VISUALISED", "extra": "x"}],
        }
        errs = validate(doc, schema)
        assert any("additionalProperties" in e for e in errs)

    def test_all_disposition_enums(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_coverage")
        for d in [
            "VISUALISED",
            "NARRATED",
            "QUOTED",
            "MERGED_EQUIVALENT",
            "PROPOSE_OMISSION",
        ]:
            doc = {"adhyay": 1, "ovis": [{"ovi": 1, "disposition": d}]}
            if d in ("MERGED_EQUIVALENT", "PROPOSE_OMISSION"):
                continue
            assert validate(doc, schema) == [], f"disposition {d} failed"

    def test_propose_omission_requires_reason(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_coverage")
        # missing reason -> error
        doc = {"adhyay": 1, "ovis": [{"ovi": 1, "disposition": "PROPOSE_OMISSION"}]}
        errs = validate(doc, schema)
        assert any("reason" in e.lower() for e in errs)
        # with reason -> ok
        doc = {
            "adhyay": 1,
            "ovis": [
                {"ovi": 1, "disposition": "PROPOSE_OMISSION", "reason": "too brief"}
            ],
        }
        assert validate(doc, schema) == []

    def test_merged_equivalent_requires_covered_by(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_coverage")
        # missing covered_by -> error (with reason present)
        doc = {"adhyay": 1, "ovis": [{"ovi": 1, "disposition": "MERGED_EQUIVALENT", "reason": "same"}]}
        errs = validate(doc, schema)
        assert any("covered_by" in e.lower() for e in errs)
        # with covered_by -> ok
        doc = {
            "adhyay": 1,
            "ovis": [
                {
                    "ovi": 1,
                    "disposition": "MERGED_EQUIVALENT",
                    "reason": "same",
                    "covered_by": "S1-L5",
                }
            ],
        }
        assert validate(doc, schema) == []

    def test_merged_equivalent_requires_reason(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_coverage")
        # missing reason -> error (with covered_by present)
        doc = {"adhyay": 1, "ovis": [{"ovi": 1, "disposition": "MERGED_EQUIVALENT", "covered_by": "S1-L5"}]}
        errs = validate(doc, schema)
        assert any("reason" in e.lower() for e in errs)
        # with reason -> ok
        doc = {
            "adhyay": 1,
            "ovis": [
                {
                    "ovi": 1,
                    "disposition": "MERGED_EQUIVALENT",
                    "reason": "same",
                    "covered_by": "S1-L5",
                }
            ],
        }
        assert validate(doc, schema) == []

    def test_visualised_no_extra_required(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_coverage")
        doc = {
            "adhyay": 1,
            "ovis": [
                {"ovi": 1, "disposition": "VISUALISED", "reason": "x", "covered_by": "S1-L1"}
            ],
        }
        assert validate(doc, schema) == []

    def test_covered_by_accepts_ovi_or_line_id(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_coverage")
        for covered in ["S1-L5", 3]:
            doc = {
                "adhyay": 1,
                "ovis": [
                    {
                        "ovi": 1,
                        "disposition": "MERGED_EQUIVALENT",
                        "reason": "same",
                        "covered_by": covered,
                    }
                ],
            }
            assert validate(doc, schema) == [], f"covered_by {covered} failed"


class TestStage1ScenesSchema:
    def test_valid_story_scene(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_scenes")
        doc = {
            "adhyay": 1,
            "scenes": [
                {
                    "scene_id": "S1",
                    "section_kind": "story",
                    "ovi_range": [1, 5],
                    "goal": "Establish conflict",
                    "turn": {"ovi": 3, "text": "Arjuna drops bow"},
                    "line_ids": ["S1-L1", "S1-L2"],
                    "teaching_treatment": "none",
                }
            ],
        }
        assert validate(doc, schema) == []

    def test_valid_discourse_scene_requires_treatment(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_scenes")
        for treatment in [
            "narration_over_typography",
            "contemplative_hold",
            "symbol_from_text",
        ]:
            doc = {
                "adhyay": 1,
                "scenes": [
                    {
                        "scene_id": "S1",
                        "section_kind": "discourse",
                        "ovi_range": [1, 5],
                        "goal": "Teach dharma",
                        "turn": {"ovi": 3, "text": "Krishna speaks"},
                        "line_ids": ["S1-L1"],
                        "teaching_treatment": treatment,
                    }
                ],
            }
            assert validate(doc, schema) == [], f"treatment {treatment} failed"

    def test_discourse_scene_without_treatment_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_scenes")
        doc = {
            "adhyay": 1,
            "scenes": [
                {
                    "scene_id": "S1",
                    "section_kind": "discourse",
                    "ovi_range": [1, 5],
                    "goal": "Teach",
                    "turn": {"ovi": 3, "text": "x"},
                    "line_ids": ["S1-L1"],
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("teaching_treatment" in e for e in errs)

    def test_story_scene_with_treatment_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_scenes")
        doc = {
            "adhyay": 1,
            "scenes": [
                {
                    "scene_id": "S1",
                    "section_kind": "story",
                    "ovi_range": [1, 5],
                    "goal": "Story",
                    "turn": {"ovi": 3, "text": "x"},
                    "line_ids": ["S1-L1"],
                    "teaching_treatment": "narration_over_typography",
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("teaching_treatment" in e for e in errs)

    def test_story_scene_treatment_absent_accepted(self, schemas_dir):
        """Story scene may omit teaching_treatment entirely (defaults to none via schema)."""
        schema = load_schema(schemas_dir, "stage1_scenes")
        doc = {
            "adhyay": 1,
            "scenes": [
                {
                    "scene_id": "S1",
                    "section_kind": "story",
                    "ovi_range": [1, 5],
                    "goal": "Story",
                    "turn": {"ovi": 3, "text": "x"},
                    "line_ids": ["S1-L1"],
                }
            ],
        }
        assert validate(doc, schema) == []

    def test_extra_key_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_scenes")
        doc = {
            "adhyay": 1,
            "scenes": [
                {
                    "scene_id": "S1",
                    "section_kind": "story",
                    "ovi_range": [1, 5],
                    "goal": "x",
                    "turn": {"ovi": 3, "text": "x"},
                    "line_ids": [],
                    "teaching_treatment": "none",
                    "extra": "no",
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("additionalProperties" in e for e in errs)

    def test_ovi_range_exactly_two_items(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_scenes")
        doc = {
            "adhyay": 1,
            "scenes": [
                {
                    "scene_id": "S1",
                    "section_kind": "story",
                    "ovi_range": [1],
                    "goal": "x",
                    "turn": {"ovi": 1, "text": "x"},
                    "line_ids": [],
                    "teaching_treatment": "none",
                }
            ],
        }
        errs = validate(doc, schema)
        assert errs


class TestStage1ShotsSchema:
    def test_valid_shot_with_preset(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_shots")
        doc = {
            "adhyay": 1,
            "shots": [
                {
                    "shot_id": "S1-1",
                    "scene_id": "S1",
                    "ovi_ids": [1, 2],
                    "beat_line_ids": ["S1-L1"],
                    "preset": "01_wide_establishing",
                    "need_new": None,
                    "needs_cutout": False,
                    "pose": "standing",
                    "framing": "wide",
                }
            ],
        }
        assert validate(doc, schema) == []

    def test_valid_shot_need_new(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_shots")
        doc = {
            "adhyay": 1,
            "shots": [
                {
                    "shot_id": "S1-1",
                    "scene_id": "S1",
                    "ovi_ids": [1],
                    "beat_line_ids": ["S1-L1"],
                    "preset": "NEED_NEW",
                    "need_new": {"reason": "unique composition", "class": "missing_image"},
                    "needs_cutout": True,
                    "pose": "kneeling",
                    "framing": "close",
                }
            ],
        }
        assert validate(doc, schema) == []

    def test_need_new_requires_object(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_shots")
        doc = {
            "adhyay": 1,
            "shots": [
                {
                    "shot_id": "S1-1",
                    "scene_id": "S1",
                    "ovi_ids": [1],
                    "beat_line_ids": ["S1-L1"],
                    "preset": "NEED_NEW",
                    "need_new": None,
                    "needs_cutout": False,
                    "pose": "x",
                    "framing": "x",
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("need_new" in e for e in errs)

    def test_non_need_new_forbids_need_new_object(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_shots")
        doc = {
            "adhyay": 1,
            "shots": [
                {
                    "shot_id": "S1-1",
                    "scene_id": "S1",
                    "ovi_ids": [1],
                    "beat_line_ids": ["S1-L1"],
                    "preset": "01_wide",
                    "need_new": {"reason": "x", "class": "missing_image"},
                    "needs_cutout": False,
                    "pose": "x",
                    "framing": "x",
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("need_new" in e for e in errs)

    def test_preset_hint_old_key_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_shots")
        doc = {
            "adhyay": 1,
            "shots": [
                {
                    "shot_id": "S1-1",
                    "scene_id": "S1",
                    "ovi_ids": [1],
                    "beat_line_ids": ["S1-L1"],
                    "preset": "01_wide",
                    "preset_hint": "old field",
                    "need_new": None,
                    "needs_cutout": False,
                    "pose": "x",
                    "framing": "x",
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("preset_hint" in e or "additionalProperties" in e for e in errs)

    def test_extra_key_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_shots")
        doc = {
            "adhyay": 1,
            "shots": [
                {
                    "shot_id": "S1-1",
                    "scene_id": "S1",
                    "ovi_ids": [1],
                    "beat_line_ids": ["S1-L1"],
                    "preset": "01_wide",
                    "need_new": None,
                    "needs_cutout": False,
                    "pose": "x",
                    "framing": "x",
                    "extra": "no",
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("additionalProperties" in e for e in errs)

    def test_need_new_class_enum(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_shots")
        for c in ["missing_image", "json_arrangement", "renderer_gap"]:
            doc = {
                "adhyay": 1,
                "shots": [
                    {
                        "shot_id": "S1-1",
                        "scene_id": "S1",
                        "ovi_ids": [1],
                        "beat_line_ids": ["S1-L1"],
                        "preset": "NEED_NEW",
                        "need_new": {"reason": "r", "class": c},
                        "needs_cutout": False,
                        "pose": "x",
                        "framing": "x",
                    }
                ],
            }
            assert validate(doc, schema) == [], f"class {c} failed"

    def test_preset_pattern(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_shots")
        # valid preset pattern
        doc = {
            "adhyay": 1,
            "shots": [
                {
                    "shot_id": "S1-1",
                    "scene_id": "S1",
                    "ovi_ids": [1],
                    "beat_line_ids": ["S1-L1"],
                    "preset": "01_wide_shot",
                    "need_new": None,
                    "needs_cutout": False,
                    "pose": "x",
                    "framing": "x",
                }
            ],
        }
        assert validate(doc, schema) == []
        # invalid preset pattern (not NEED_NEW and not matching pattern)
        doc["shots"][0]["preset"] = "invalid_preset"
        errs = validate(doc, schema)
        assert errs


class TestStage1ImageBriefsSchema:
    def test_valid_minimal(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_image_briefs")
        doc = {
            "adhyay": 1,
            "images": [
                {
                    "image_id": "s1_arjuna_bow",
                    "scene_id": "S1",
                    "shot_ids": ["S1-1"],
                    "people": [
                        {"name": "Arjuna", "position": "center", "pose": "holding bow", "gaze": "down"}
                    ],
                    "place_id": "battlefield",
                    "prop": "bow",
                    "prop_state": "strung",
                    "camera": "eye level",
                    "light": "harsh noon",
                    "reason_new": "first appearance",
                    "on_screen_facts": ["Arjuna holds bow", "chariot behind"],
                    "references": {
                        "characters": ["Arjuna"],
                        "place": "battlefield",
                        "style_anchor": "epic realism",
                        "prop": "bow",
                    },
                }
            ],
        }
        assert validate(doc, schema) == []

    def test_extra_key_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_image_briefs")
        doc = {
            "adhyay": 1,
            "images": [
                {
                    "image_id": "s1_x",
                    "scene_id": "S1",
                    "shot_ids": ["S1-1"],
                    "people": [{"name": "A", "position": "c", "pose": "p", "gaze": "g"}],
                    "place_id": "p",
                    "prop": None,
                    "prop_state": None,
                    "camera": "c",
                    "light": "l",
                    "reason_new": "r",
                    "on_screen_facts": ["f"],
                    "references": {"characters": [], "place": "p", "style_anchor": "s", "prop": None},
                    "extra": "no",
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("additionalProperties" in e for e in errs)

    def test_empty_on_screen_facts_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_image_briefs")
        doc = {
            "adhyay": 1,
            "images": [
                {
                    "image_id": "s1_x",
                    "scene_id": "S1",
                    "shot_ids": ["S1-1"],
                    "people": [{"name": "A", "position": "c", "pose": "p", "gaze": "g"}],
                    "place_id": "p",
                    "prop": None,
                    "prop_state": None,
                    "camera": "c",
                    "light": "l",
                    "reason_new": "r",
                    "on_screen_facts": [],
                    "references": {"characters": [], "place": "p", "style_anchor": "s", "prop": None},
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("on_screen_facts" in e for e in errs)

    def test_empty_person_name_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_image_briefs")
        doc = {
            "adhyay": 1,
            "images": [
                {
                    "image_id": "s1_x",
                    "scene_id": "S1",
                    "shot_ids": ["S1-1"],
                    "people": [{"name": "", "position": "c", "pose": "p", "gaze": "g"}],
                    "place_id": "p",
                    "prop": None,
                    "prop_state": None,
                    "camera": "c",
                    "light": "l",
                    "reason_new": "r",
                    "on_screen_facts": ["f"],
                    "references": {"characters": [], "place": "p", "style_anchor": "s", "prop": None},
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("name" in e for e in errs)

    def test_image_id_pattern(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_image_briefs")
        # valid
        doc = {
            "adhyay": 1,
            "images": [
                {
                    "image_id": "s1_valid_name",
                    "scene_id": "S1",
                    "shot_ids": ["S1-1"],
                    "people": [{"name": "A", "position": "c", "pose": "p", "gaze": "g"}],
                    "place_id": "p",
                    "prop": None,
                    "prop_state": None,
                    "camera": "c",
                    "light": "l",
                    "reason_new": "r",
                    "on_screen_facts": ["f"],
                    "references": {"characters": [], "place": "p", "style_anchor": "s", "prop": None},
                }
            ],
        }
        assert validate(doc, schema) == []
        # invalid - wrong prefix
        doc["images"][0]["image_id"] = "s9_wrong"
        errs = validate(doc, schema)
        assert errs
        # invalid - uppercase
        doc["images"][0]["image_id"] = "S1_wrong"
        errs = validate(doc, schema)
        assert errs


class TestStage1CanonLooksSchema:
    def test_valid_minimal(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_canon_looks")
        doc = {
            "adhyay": 1,
            "entries": [
                {
                    "entity_id": "arjuna",
                    "kind": "character",
                    "state_id": "battle_ready",
                    "look": "armored, bow in hand",
                    "source_ovis": [1, 2],
                    "basis": "stated",
                }
            ],
        }
        assert validate(doc, schema) == []

    def test_extra_key_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_canon_looks")
        doc = {
            "adhyay": 1,
            "entries": [
                {
                    "entity_id": "arjuna",
                    "kind": "character",
                    "state_id": "battle_ready",
                    "look": "armored",
                    "source_ovis": [1],
                    "basis": "stated",
                    "events": ["E1"],
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("events" in e or "additionalProperties" in e for e in errs)

    def test_kind_enum(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_canon_looks")
        for k in ["character", "place", "prop"]:
            doc = {
                "adhyay": 1,
                "entries": [
                    {
                        "entity_id": "e",
                        "kind": k,
                        "state_id": "s",
                        "look": "l",
                        "source_ovis": [1],
                        "basis": "stated",
                    }
                ],
            }
            assert validate(doc, schema) == [], f"kind {k} failed"

    def test_basis_enum(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_canon_looks")
        for b in ["stated", "inferred"]:
            doc = {
                "adhyay": 1,
                "entries": [
                    {
                        "entity_id": "e",
                        "kind": "character",
                        "state_id": "s",
                        "look": "l",
                        "source_ovis": [1],
                        "basis": b,
                    }
                ],
            }
            assert validate(doc, schema) == [], f"basis {b} failed"

    def test_source_ovis_min_one(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_canon_looks")
        doc = {
            "adhyay": 1,
            "entries": [
                {
                    "entity_id": "e",
                    "kind": "character",
                    "state_id": "s",
                    "look": "l",
                    "source_ovis": [],
                    "basis": "stated",
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("source_ovis" in e for e in errs)

    def test_entity_state_unique_within_document(self, schemas_dir):
        """Schema enforces unique entity_id+state_id via uniqueItems on entries? Actually not at schema level - semantic check."""
        # Schema alone cannot enforce cross-entry uniqueness; this is a semantic rule.
        # But we test that extra keys are rejected.
        schema = load_schema(schemas_dir, "stage1_canon_looks")
        doc = {
            "adhyay": 1,
            "entries": [
                {
                    "entity_id": "arjuna",
                    "kind": "character",
                    "state_id": "battle_ready",
                    "look": "armored",
                    "source_ovis": [1],
                    "basis": "stated",
                    "extra": "no",
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("additionalProperties" in e for e in errs)


class TestStage1VoiceCastSchema:
    def test_valid_minimal(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_voice_cast")
        doc = {
            "adhyay": 1,
            "cast": [
                {
                    "character_id": "arjuna",
                    "voice_key": "arjuna_voice",
                    "voice_id": "v_arjuna_001_valid_id",
                    "gender": "male",
                    "status": "RECURRING",
                }
            ],
        }
        assert validate(doc, schema) == []

    def test_extra_key_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_voice_cast")
        doc = {
            "adhyay": 1,
            "cast": [
                {
                    "character_id": "arjuna",
                    "voice_key": "k",
                    "voice_id": "v_arjuna_001_valid_id",
                    "gender": "male",
                    "status": "RECURRING",
                    "extra": "no",
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("additionalProperties" in e for e in errs)

    def test_gender_enum(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_voice_cast")
        for g in ["male", "female"]:
            doc = {
                "adhyay": 1,
                "cast": [
                    {
                        "character_id": "c",
                        "voice_key": "k",
                        "voice_id": "v_valid_voice_id_001",
                        "gender": g,
                        "status": "RECURRING",
                    }
                ],
            }
            assert validate(doc, schema) == [], f"gender {g} failed"

    def test_status_enum(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_voice_cast")
        for s in ["RECURRING", "NEW_PROPOSED"]:
            doc = {
                "adhyay": 1,
                "cast": [
                    {
                        "character_id": "c",
                        "voice_key": "k",
                        "voice_id": "v_valid_voice_id_001",
                        "gender": "male",
                        "status": s,
                    }
                ],
            }
            assert validate(doc, schema) == [], f"status {s} failed"

    def test_voice_id_length(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_voice_cast")
        # too short (min 10)
        doc = {
            "adhyay": 1,
            "cast": [
                {
                    "character_id": "c",
                    "voice_key": "k",
                    "voice_id": "short",
                    "gender": "male",
                    "status": "RECURRING",
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("voice_id" in e for e in errs)
        # too long (max 40)
        doc["cast"][0]["voice_id"] = "x" * 41
        errs = validate(doc, schema)
        assert any("voice_id" in e for e in errs)
        # valid boundaries
        doc["cast"][0]["voice_id"] = "x" * 10
        assert validate(doc, schema) == []
        doc["cast"][0]["voice_id"] = "x" * 40
        assert validate(doc, schema) == []


class TestStage1SoundSuggestionsSchema:
    def test_valid_bed_existing(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_sound_suggestions")
        doc = {
            "adhyay": 1,
            "cues": [
                {
                    "scene_id": "S1",
                    "anchor_line_id": "S1-L1",
                    "sound_id": "bed_battlefield",
                    "kind": "bed",
                    "purpose": "ambience",
                    "basis": "staging",
                }
            ],
        }
        assert validate(doc, schema) == []

    def test_valid_fx_need_new(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_sound_suggestions")
        doc = {
            "adhyay": 1,
            "cues": [
                {
                    "scene_id": "S1",
                    "anchor_line_id": "S1-L1",
                    "sound_id": "NEED_NEW",
                    "kind": "fx",
                    "sound_prompt": "conch blow",
                    "purpose": "signal",
                    "basis": "stated",
                }
            ],
        }
        assert validate(doc, schema) == []

    def test_need_new_requires_sound_prompt(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_sound_suggestions")
        doc = {
            "adhyay": 1,
            "cues": [
                {
                    "scene_id": "S1",
                    "anchor_line_id": "S1-L1",
                    "sound_id": "NEED_NEW",
                    "kind": "fx",
                    "purpose": "signal",
                    "basis": "stated",
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("sound_prompt" in e for e in errs)

    def test_non_need_new_forbids_sound_prompt(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_sound_suggestions")
        doc = {
            "adhyay": 1,
            "cues": [
                {
                    "scene_id": "S1",
                    "anchor_line_id": "S1-L1",
                    "sound_id": "bed_ambience",
                    "kind": "bed",
                    "sound_prompt": "should not be here",
                    "purpose": "ambience",
                    "basis": "staging",
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("sound_prompt" in e for e in errs)

    def test_duration_seconds_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_sound_suggestions")
        doc = {
            "adhyay": 1,
            "cues": [
                {
                    "scene_id": "S1",
                    "anchor_line_id": "S1-L1",
                    "sound_id": "bed_ambience",
                    "kind": "bed",
                    "purpose": "ambience",
                    "basis": "staging",
                    "duration_seconds": 5.0,
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("duration_seconds" in e or "additionalProperties" in e for e in errs)

    def test_extra_key_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_sound_suggestions")
        doc = {
            "adhyay": 1,
            "cues": [
                {
                    "scene_id": "S1",
                    "anchor_line_id": "S1-L1",
                    "sound_id": "bed_ambience",
                    "kind": "bed",
                    "purpose": "ambience",
                    "basis": "staging",
                    "extra": "no",
                }
            ],
        }
        errs = validate(doc, schema)
        assert any("additionalProperties" in e for e in errs)

    def test_kind_enum(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_sound_suggestions")
        for k in ["bed", "fx"]:
            doc = {
                "adhyay": 1,
                "cues": [
                    {
                        "scene_id": "S1",
                        "anchor_line_id": "S1-L1",
                        "sound_id": "NEED_NEW",
                        "kind": k,
                        "sound_prompt": "p",
                        "purpose": "p",
                        "basis": "stated",
                    }
                ],
            }
            assert validate(doc, schema) == [], f"kind {k} failed"

    def test_basis_enum(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_sound_suggestions")
        for b in ["stated", "staging"]:
            doc = {
                "adhyay": 1,
                "cues": [
                    {
                        "scene_id": "S1",
                        "anchor_line_id": "S1-L1",
                        "sound_id": "NEED_NEW",
                        "kind": "fx",
                        "sound_prompt": "p",
                        "purpose": "p",
                        "basis": b,
                    }
                ],
            }
            assert validate(doc, schema) == [], f"basis {b} failed"

    def test_sound_id_pattern(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_sound_suggestions")
        # valid bed
        doc = {
            "adhyay": 1,
            "cues": [
                {
                    "scene_id": "S1",
                    "anchor_line_id": "S1-L1",
                    "sound_id": "bed_ambience",
                    "kind": "bed",
                    "purpose": "p",
                    "basis": "stated",
                }
            ],
        }
        assert validate(doc, schema) == []
        # valid fx
        doc["cues"][0]["sound_id"] = "fx_conch"
        doc["cues"][0]["kind"] = "fx"
        assert validate(doc, schema) == []
        # invalid prefix
        doc["cues"][0]["sound_id"] = "invalid_sound"
        errs = validate(doc, schema)
        assert errs


class TestStage1QuestionsSchema:
    def test_valid_minimal(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_questions")
        doc = {
            "adhyay": 1,
            "questions": [
                {"id": "Q1", "text": "Why does Arjuna hesitate?", "scene_id": "S1"},
                {"id": "Q2", "text": "What is dharma?"},
            ],
        }
        assert validate(doc, schema) == []

    def test_extra_key_rejected(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_questions")
        doc = {
            "adhyay": 1,
            "questions": [{"id": "Q1", "text": "t", "extra": "no"}],
        }
        errs = validate(doc, schema)
        assert any("additionalProperties" in e for e in errs)

    def test_id_pattern(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_questions")
        doc = {"adhyay": 1, "questions": [{"id": "X1", "text": "t"}]}
        errs = validate(doc, schema)
        assert any("id" in e for e in errs)


class TestCommonTypeBoundaries:
    """Parameterized tests for all common type boundaries across schemas."""

    @pytest.mark.parametrize("name,schema_name,instance,should_pass", [
        # scene_id
        ("scene_id_valid", "stage1_scenes", {"adhyay": 1, "scenes": [{"scene_id": "S1", "section_kind": "story", "ovi_range": [1,1], "goal": "g", "turn": {"ovi": 1, "text": "t"}, "line_ids": [], "teaching_treatment": "none"}]}, True),
        ("scene_id_invalid_S0", "stage1_scenes", {"adhyay": 1, "scenes": [{"scene_id": "S0", "section_kind": "story", "ovi_range": [1,1], "goal": "g", "turn": {"ovi": 1, "text": "t"}, "line_ids": [], "teaching_treatment": "none"}]}, False),
        ("scene_id_invalid_S100", "stage1_scenes", {"adhyay": 1, "scenes": [{"scene_id": "S100", "section_kind": "story", "ovi_range": [1,1], "goal": "g", "turn": {"ovi": 1, "text": "t"}, "line_ids": [], "teaching_treatment": "none"}]}, False),
        # shot_id
        ("shot_id_valid", "stage1_shots", {"adhyay": 1, "shots": [{"shot_id": "S1-1", "scene_id": "S1", "ovi_ids": [1], "beat_line_ids": ["S1-L1"], "preset": "01_wide", "need_new": None, "needs_cutout": False, "pose": "x", "framing": "x"}]}, True),
        ("shot_id_invalid", "stage1_shots", {"adhyay": 1, "shots": [{"shot_id": "S1_1", "scene_id": "S1", "ovi_ids": [1], "beat_line_ids": ["S1-L1"], "preset": "01_wide", "need_new": None, "needs_cutout": False, "pose": "x", "framing": "x"}]}, False),
        # line_id
        ("line_id_valid", "stage1_scenes", {"adhyay": 1, "scenes": [{"scene_id": "S1", "section_kind": "story", "ovi_range": [1,1], "goal": "g", "turn": {"ovi": 1, "text": "t"}, "line_ids": ["S1-L1"], "teaching_treatment": "none"}]}, True),
        ("line_id_invalid", "stage1_scenes", {"adhyay": 1, "scenes": [{"scene_id": "S1", "section_kind": "story", "ovi_range": [1,1], "goal": "g", "turn": {"ovi": 1, "text": "t"}, "line_ids": ["S1-L"], "teaching_treatment": "none"}]}, False),
        # image_id
        ("image_id_valid", "stage1_image_briefs", {"adhyay": 1, "images": [{"image_id": "s1_valid_name", "scene_id": "S1", "shot_ids": ["S1-1"], "people": [{"name": "A", "position": "c", "pose": "p", "gaze": "g"}], "place_id": "p", "prop": None, "prop_state": None, "camera": "c", "light": "l", "reason_new": "r", "on_screen_facts": ["f"], "references": {"characters": [], "place": "p", "style_anchor": "s", "prop": None}}]}, True),
        ("image_id_invalid_prefix", "stage1_image_briefs", {"adhyay": 1, "images": [{"image_id": "s9_wrong", "scene_id": "S1", "shot_ids": ["S1-1"], "people": [{"name": "A", "position": "c", "pose": "p", "gaze": "g"}], "place_id": "p", "prop": None, "prop_state": None, "camera": "c", "light": "l", "reason_new": "r", "on_screen_facts": ["f"], "references": {"characters": [], "place": "p", "style_anchor": "s", "prop": None}}]}, False),
        # ovi minimum
        ("ovi_min_1", "stage1_story_map", {"adhyay": 1, "ovi_types": [{"ovi": 1, "type": "STORY"}], "events": []}, True),
        ("ovi_min_0_invalid", "stage1_story_map", {"adhyay": 1, "ovi_types": [{"ovi": 0, "type": "STORY"}], "events": []}, False),
        # adhyay bounds
        ("adhyay_1", "stage1_story_map", {"adhyay": 1, "ovi_types": [{"ovi": 1, "type": "STORY"}], "events": []}, True),
        ("adhyay_21", "stage1_story_map", {"adhyay": 21, "ovi_types": [{"ovi": 1, "type": "STORY"}], "events": []}, True),
        ("adhyay_0_invalid", "stage1_story_map", {"adhyay": 0, "ovi_types": [{"ovi": 1, "type": "STORY"}], "events": []}, False),
        ("adhyay_22_invalid", "stage1_story_map", {"adhyay": 22, "ovi_types": [{"ovi": 1, "type": "STORY"}], "events": []}, False),
        # text length 1..400
        ("text_min_1", "stage1_story_map", {"adhyay": 1, "ovi_types": [{"ovi": 1, "type": "STORY"}], "events": [{"event_id": "E1", "title": "x", "ovi_range": [1,1], "key_ovis": [1], "kind": "story", "closure": "NA"}]}, True),
        ("text_max_400", "stage1_story_map", {"adhyay": 1, "ovi_types": [{"ovi": 1, "type": "STORY"}], "events": [{"event_id": "E1", "title": "x"*400, "ovi_range": [1,1], "key_ovis": [1], "kind": "story", "closure": "NA"}]}, True),
        ("text_0_invalid", "stage1_story_map", {"adhyay": 1, "ovi_types": [{"ovi": 1, "type": "STORY"}], "events": [{"event_id": "E1", "title": "", "ovi_range": [1,1], "key_ovis": [1], "kind": "story", "closure": "NA"}]}, False),
        ("text_401_invalid", "stage1_story_map", {"adhyay": 1, "ovi_types": [{"ovi": 1, "type": "STORY"}], "events": [{"event_id": "E1", "title": "x"*401, "ovi_range": [1,1], "key_ovis": [1], "kind": "story", "closure": "NA"}]}, False),
        # preset_id pattern
        ("preset_id_valid", "stage1_shots", {"adhyay": 1, "shots": [{"shot_id": "S1-1", "scene_id": "S1", "ovi_ids": [1], "beat_line_ids": ["S1-L1"], "preset": "01_wide_shot", "need_new": None, "needs_cutout": False, "pose": "x", "framing": "x"}]}, True),
        ("preset_id_invalid", "stage1_shots", {"adhyay": 1, "shots": [{"shot_id": "S1-1", "scene_id": "S1", "ovi_ids": [1], "beat_line_ids": ["S1-L1"], "preset": "wide_shot", "need_new": None, "needs_cutout": False, "pose": "x", "framing": "x"}]}, False),
        # sound_id pattern
        ("sound_id_bed_valid", "stage1_sound_suggestions", {"adhyay": 1, "cues": [{"scene_id": "S1", "anchor_line_id": "S1-L1", "sound_id": "bed_ambience", "kind": "bed", "purpose": "p", "basis": "stated"}]}, True),
        ("sound_id_fx_valid", "stage1_sound_suggestions", {"adhyay": 1, "cues": [{"scene_id": "S1", "anchor_line_id": "S1-L1", "sound_id": "fx_conch", "kind": "fx", "purpose": "p", "basis": "stated"}]}, True),
        ("sound_id_need_new_valid", "stage1_sound_suggestions", {"adhyay": 1, "cues": [{"scene_id": "S1", "anchor_line_id": "S1-L1", "sound_id": "NEED_NEW", "kind": "fx", "sound_prompt": "p", "purpose": "p", "basis": "stated"}]}, True),
        ("sound_id_invalid", "stage1_sound_suggestions", {"adhyay": 1, "cues": [{"scene_id": "S1", "anchor_line_id": "S1-L1", "sound_id": "invalid", "kind": "bed", "purpose": "p", "basis": "stated"}]}, False),
        # voice_id length 10..40
        ("voice_id_min_10", "stage1_voice_cast", {"adhyay": 1, "cast": [{"character_id": "c", "voice_key": "k", "voice_id": "x"*10, "gender": "male", "status": "RECURRING"}]}, True),
        ("voice_id_max_40", "stage1_voice_cast", {"adhyay": 1, "cast": [{"character_id": "c", "voice_key": "k", "voice_id": "x"*40, "gender": "male", "status": "RECURRING"}]}, True),
        ("voice_id_9_invalid", "stage1_voice_cast", {"adhyay": 1, "cast": [{"character_id": "c", "voice_key": "k", "voice_id": "x"*9, "gender": "male", "status": "RECURRING"}]}, False),
        ("voice_id_41_invalid", "stage1_voice_cast", {"adhyay": 1, "cast": [{"character_id": "c", "voice_key": "k", "voice_id": "x"*41, "gender": "male", "status": "RECURRING"}]}, False),
        # question_id pattern
        ("question_id_valid", "stage1_questions", {"adhyay": 1, "questions": [{"id": "Q1", "text": "t"}]}, True),
        ("question_id_invalid", "stage1_questions", {"adhyay": 1, "questions": [{"id": "X1", "text": "t"}]}, False),
    ])
    def test_common_type_boundaries(self, schemas_dir, name, schema_name, instance, should_pass):
        schema = load_schema(schemas_dir, schema_name)
        errs = validate(instance, schema)
        if should_pass:
            assert errs == [], f"{name}: expected pass, got errors: {errs}"
        else:
            assert errs, f"{name}: expected failure, got none"


class TestRequiredFields:
    """Each required field missing should cause a schema error."""

    @pytest.mark.parametrize("schema_name,doc_base,missing_field", [
        ("stage1_story_map", {"adhyay": 1, "ovi_types": [], "events": []}, "ovi_types"),
        ("stage1_story_map", {"adhyay": 1, "ovi_types": [{"ovi": 1, "type": "STORY"}], "events": []}, "events"),
        ("stage1_coverage", {"adhyay": 1, "ovis": []}, "ovis"),
        ("stage1_scenes", {"adhyay": 1, "scenes": []}, "scenes"),
        ("stage1_shots", {"adhyay": 1, "shots": []}, "shots"),
        ("stage1_image_briefs", {"adhyay": 1, "images": []}, "images"),
        ("stage1_canon_looks", {"adhyay": 1, "entries": []}, "entries"),
        ("stage1_voice_cast", {"adhyay": 1, "cast": []}, "cast"),
        ("stage1_sound_suggestions", {"adhyay": 1, "cues": []}, "cues"),
        ("stage1_questions", {"adhyay": 1, "questions": []}, "questions"),
    ])
    def test_required_fields(self, schemas_dir, schema_name, doc_base, missing_field):
        schema = load_schema(schemas_dir, schema_name)
        errs = validate(doc_base, schema)
        assert any(missing_field in e and ("required" in e or "missing" in e) for e in errs), f"{schema_name}.{missing_field}"


class TestOldSchemasUnchanged:
    """Ensure the four non-Stage-1 schemas are exactly as they were (frozen copies)."""

    def test_beats_schema_exact(self, schemas_dir):
        schema = load_schema(schemas_dir, "beats")
        assert schema == EXPECTED_BEATS_SCHEMA

    def test_image_catalog_schema_exact(self, schemas_dir):
        schema = load_schema(schemas_dir, "image_catalog")
        assert schema == EXPECTED_IMAGE_CATALOG_SCHEMA

    def test_animation_scene_schema_exact(self, schemas_dir):
        schema = load_schema(schemas_dir, "animation_scene")
        assert schema == EXPECTED_ANIMATION_SCENE_SCHEMA

    def test_shot_plan_schema_exact(self, schemas_dir):
        schema = load_schema(schemas_dir, "shot_plan")
        assert schema == EXPECTED_SHOT_PLAN_SCHEMA


class TestMakeSchemasCLI:
    def test_write_all_returns_paths(self, tmp_path):
        written = make_schemas.write_all(tmp_path, overwrite=False)
        assert len(written) == 13  # 9 stage1 + 4 legacy
        for p in written:
            assert p.exists()
            assert p.suffix == ".json"

    def test_refuses_overwrite(self, tmp_path):
        make_schemas.write_all(tmp_path, overwrite=False)
        with pytest.raises(FileExistsError):
            make_schemas.write_all(tmp_path, overwrite=False)

    def test_overwrite_replaces(self, tmp_path):
        make_schemas.write_all(tmp_path, overwrite=False)
        # Should not raise with overwrite=True
        written = make_schemas.write_all(tmp_path, overwrite=True)
        assert len(written) == 13

    def test_generated_schema_dialect(self, tmp_path):
        make_schemas.write_all(tmp_path, overwrite=False)
        for p in tmp_path.glob("*.schema.json"):
            data = json.loads(p.read_text())
            assert data.get("$schema") == "https://json-schema.org/draft/2020-12/schema"

    def test_main_cli(self, tmp_path, monkeypatch, capsys):
        # Test CLI --out and --overwrite
        monkeypatch.setattr(sys, "argv", ["make_schemas.py", "--out", str(tmp_path), "--overwrite"])
        make_schemas.main()
        assert len(list(tmp_path.glob("*.schema.json"))) == 13

```

## YOUR PREVIOUS tests/test_validate_stage1.py
```python
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# Load validate_stage1 module by path
spec = importlib.util.spec_from_file_location(
    "validate_stage1", ROOT / "scripts" / "pipeline" / "validate_stage1.py"
)
validate_stage1_mod = importlib.util.module_from_spec(spec)
sys.modules["validate_stage1"] = validate_stage1_mod
spec.loader.exec_module(validate_stage1_mod)

validate_stage1 = validate_stage1_mod.validate_stage1


def make_ctx(
    *,
    script_line_ids=None,
    core_line_ids=None,
    chapter_ovis=None,
    unfilmed_ovis=None,
    preset_ids=None,
    sound_ids=None,
    saved_voices=None,
    speaking_characters=None,
    known_states=None,
):
    """Build context dict. Only apply defaults when argument is None (not empty)."""
    return {
        "script_line_ids": script_line_ids if script_line_ids is not None else ["S1-L1", "S1-L2", "S2-L1"],
        "core_line_ids": core_line_ids if core_line_ids is not None else {"S1-L1", "S2-L1"},
        "chapter_ovis": chapter_ovis if chapter_ovis is not None else {1, 2, 3, 4, 5},
        "unfilmed_ovis": unfilmed_ovis if unfilmed_ovis is not None else set(),
        "preset_ids": preset_ids if preset_ids is not None else {"01_wide", "02_medium", "03_close"},
        "sound_ids": sound_ids if sound_ids is not None else {"bed_battlefield", "fx_conch"},
        "saved_voices": saved_voices if saved_voices is not None else {"arjuna_voice": "v_arjuna_001_valid_id", "krishna_voice": "v_krishna_001_valid_id"},
        "speaking_characters": speaking_characters if speaking_characters is not None else {"arjuna", "krishna"},
        "known_states": known_states if known_states is not None else {"arjuna": {"battle_ready"}, "krishna": {"charioteer"}, "battlefield": {"dawn_armies"}},
    }


def make_valid_docs(adhyay=1):
    """Return a fully valid set of nine documents for the given adhyay.
    NOTE-FREE: no PROPOSE_OMISSION entries.
    """
    return {
        "story_map": {
            "adhyay": adhyay,
            "ovi_types": [
                {"ovi": 1, "type": "STORY"},
                {"ovi": 2, "type": "TEACHING"},
                {"ovi": 3, "type": "PHILOSOPHY"},
                {"ovi": 4, "type": "INVOCATION"},
                {"ovi": 5, "type": "RECAP"},
            ],
            "events": [
                {
                    "event_id": "E1",
                    "title": "Opening",
                    "ovi_range": [1, 2],
                    "key_ovis": [1],
                    "kind": "story",
                    "closure": "RESOLVED_IN_ADHYAY",
                },
                {
                    "event_id": "E2",
                    "title": "Teaching",
                    "ovi_range": [3, 5],
                    "key_ovis": [3, 4],
                    "kind": "discourse",
                    "closure": "RESOLVED_IN_ADHYAY",
                },
            ],
        },
        "coverage": {
            "adhyay": adhyay,
            "ovis": [
                {"ovi": 1, "disposition": "VISUALISED"},
                {"ovi": 2, "disposition": "NARRATED"},
                {"ovi": 3, "disposition": "QUOTED"},
                {"ovi": 4, "disposition": "MERGED_EQUIVALENT", "reason": "same as 3", "covered_by": 3},
                {"ovi": 5, "disposition": "QUOTED"},  # not PROPOSE_OMISSION
            ],
        },
        "scenes": {
            "adhyay": adhyay,
            "scenes": [
                {
                    "scene_id": "S1",
                    "section_kind": "story",
                    "ovi_range": [1, 2],
                    "goal": "Setup",
                    "turn": {"ovi": 1, "text": "Arjuna sees armies"},
                    "line_ids": ["S1-L1", "S1-L2"],
                    "teaching_treatment": "none",
                },
                {
                    "scene_id": "S2",
                    "section_kind": "discourse",
                    "ovi_range": [3, 5],
                    "goal": "Teaching",
                    "turn": {"ovi": 3, "text": "Krishna speaks"},
                    "line_ids": ["S2-L1"],
                    "teaching_treatment": "contemplative_hold",
                },
            ],
        },
        "shots": {
            "adhyay": adhyay,
            "shots": [
                {
                    "shot_id": "S1-1",
                    "scene_id": "S1",
                    "ovi_ids": [1],
                    "beat_line_ids": ["S1-L1"],
                    "preset": "01_wide",
                    "need_new": None,
                    "needs_cutout": False,
                    "pose": "standing",
                    "framing": "wide",
                },
                {
                    "shot_id": "S1-2",
                    "scene_id": "S1",
                    "ovi_ids": [2],
                    "beat_line_ids": ["S1-L2"],
                    "preset": "02_medium",
                    "need_new": None,
                    "needs_cutout": False,
                    "pose": "kneeling",
                    "framing": "medium",
                },
                {
                    "shot_id": "S2-1",
                    "scene_id": "S2",
                    "ovi_ids": [3, 4, 5],
                    "beat_line_ids": ["S2-L1"],
                    "preset": "03_close",
                    "need_new": None,
                    "needs_cutout": True,
                    "pose": "seated",
                    "framing": "close",
                },
            ],
        },
        "briefs": {
            "adhyay": adhyay,
            "images": [
                {
                    "image_id": "s1_arjuna_standing",
                    "scene_id": "S1",
                    "shot_ids": ["S1-1"],
                    "people": [
                        {"name": "Arjuna", "position": "center", "pose": "standing", "gaze": "forward"}
                    ],
                    "place_id": "battlefield",
                    "prop": "bow",
                    "prop_state": "strung",
                    "camera": "eye level",
                    "light": "harsh noon",
                    "reason_new": "first shot",
                    "on_screen_facts": ["Arjuna stands", "bow visible"],
                    "references": {
                        "characters": ["Arjuna"],
                        "place": "battlefield",
                        "style_anchor": "epic realism",
                        "prop": "bow",
                    },
                },
                {
                    "image_id": "s2_krishna_seated",
                    "scene_id": "S2",
                    "shot_ids": ["S2-1"],
                    "people": [
                        {"name": "Krishna", "position": "center", "pose": "seated", "gaze": "at Arjuna"}
                    ],
                    "place_id": "chariot",
                    "prop": None,
                    "prop_state": None,
                    "camera": "low angle",
                    "light": "divine glow",
                    "reason_new": "teaching moment",
                    "on_screen_facts": ["Krishna seated", "chariot interior"],
                    "references": {
                        "characters": ["Krishna"],
                        "place": "chariot",
                        "style_anchor": "epic realism",
                        "prop": None,
                    },
                },
            ],
        },
        "looks": {
            "adhyay": adhyay,
            "entries": [
                {
                    "entity_id": "arjuna",
                    "kind": "character",
                    "state_id": "battle_ready",
                    "look": "armored, bow in hand",
                    "source_ovis": [1, 2],
                    "basis": "stated",
                },
                {
                    "entity_id": "krishna",
                    "kind": "character",
                    "state_id": "charioteer",
                    "look": "peacock feather, yellow garment",
                    "source_ovis": [3, 4, 5],
                    "basis": "stated",
                },
                {
                    "entity_id": "battlefield",
                    "kind": "place",
                    "state_id": "dawn_armies",
                    "look": "two armies arrayed",
                    "source_ovis": [1],
                    "basis": "stated",
                },
            ],
        },
        "voices": {
            "adhyay": adhyay,
            "cast": [
                {
                    "character_id": "arjuna",
                    "voice_key": "arjuna_voice",
                    "voice_id": "v_arjuna_001_valid_id",
                    "gender": "male",
                    "status": "RECURRING",
                },
                {
                    "character_id": "krishna",
                    "voice_key": "krishna_voice",
                    "voice_id": "v_krishna_001_valid_id",
                    "gender": "male",
                    "status": "RECURRING",
                },
            ],
        },
        "sounds": {
            "adhyay": adhyay,
            "cues": [
                {
                    "scene_id": "S1",
                    "anchor_line_id": "S1-L1",
                    "sound_id": "bed_battlefield",
                    "kind": "bed",
                    "purpose": "ambience",
                    "basis": "staging",
                },
                {
                    "scene_id": "S2",
                    "anchor_line_id": "S2-L1",
                    "sound_id": "fx_conch",
                    "kind": "fx",
                    "purpose": "signal start",
                    "basis": "stated",
                },
            ],
        },
        "questions": {
            "adhyay": adhyay,
            "questions": [
                {"id": "Q1", "text": "Why does Arjuna hesitate?", "scene_id": "S1"},
                {"id": "Q2", "text": "What is the nature of the self?"},
            ],
        },
    }


class TestValidateStage1:
    # --- Baseline ---
    def test_fully_valid_returns_empty(self):
        docs = make_valid_docs(1)
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert errs == [], f"expected no errors, got: {errs}"

    # --- Phase control ---
    def test_schema_error_stops_early(self):
        """Schema errors in multiple docs; adhyay mismatch also present.
        Should return ALL schema errors and NO semantic errors."""
        docs = make_valid_docs(1)
        # Introduce schema errors in two documents
        docs["story_map"]["ovi_types"] = [{"ovi": 1}]  # missing type
        docs["coverage"]["ovis"] = [{"ovi": 1}]  # missing disposition
        # Also introduce adhyay mismatch in a third document
        docs["scenes"]["adhyay"] = 2
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        # All schema errors present
        assert any("story_map" in e and "type" in e for e in errs)
        assert any("coverage" in e and "disposition" in e for e in errs)
        assert any("scenes" in e and "adhyay" in e and "does not match" in e for e in errs)
        # No semantic errors (adhyay mismatch is a semantic step 2 check, but schema errors stop early)
        # Actually adhyay mismatch is step 2 (semantic), so it should NOT appear if schema errors stop early
        semantic_errs = [e for e in errs if "adhyay" in e and "does not match" in e]
        # The spec says: "return at once only if a schema step fails" - so semantic steps don't run
        # But wait: adhyay mismatch is step 2, which is semantic. Schema is step 1.
        # So if step 1 has errors, step 2 doesn't run. The adhyay mismatch in scenes is a semantic check.
        # However, the schema for scenes requires adhyay field - but the value 2 is valid for schema.
        # So the adhyay mismatch is NOT a schema error, it's semantic. It should NOT appear.
        assert not any("scenes adhyay 2 does not match 1" in e for e in errs)

    def test_collects_all_semantic_steps(self):
        """Independent violations across steps 2-11; all should be reported."""
        docs = make_valid_docs(1)
        # Step 2: adhyay mismatch in coverage
        docs["coverage"]["adhyay"] = 2
        # Step 3: ovi untyped
        docs["story_map"]["ovi_types"] = [{"ovi": 1, "type": "STORY"}]  # missing 2-5
        # Step 4: coverage missing disposition for ovi 2, unfilmed but VISUALISED
        docs["coverage"]["ovis"] = [
            {"ovi": 1, "disposition": "VISUALISED"},
            {"ovi": 3, "disposition": "QUOTED"},
            {"ovi": 4, "disposition": "MERGED_EQUIVALENT", "reason": "r", "covered_by": 3},
            {"ovi": 5, "disposition": "QUOTED"},
        ]
        # Step 5: scene range overlap, core line missing, discourse without treatment
        docs["scenes"]["scenes"][1]["ovi_range"] = [2, 4]  # overlaps S1 [1,2]
        docs["scenes"]["scenes"][1]["line_ids"] = []  # S2-L1 core but missing
        docs["scenes"]["scenes"][1]["teaching_treatment"] = "none"
        # Step 6: shot not consecutive, unknown preset, line not in any shot beat
        docs["shots"]["shots"][1]["shot_id"] = "S1-3"  # skip S1-2
        docs["shots"]["shots"][0]["preset"] = "99_unknown"
        docs["shots"]["shots"] = [s for s in docs["shots"]["shots"] if s["shot_id"] != "S1-2"]  # S1-L2 not in any shot
        # Step 7: brief image_id wrong prefix, shot not in scene
        docs["briefs"]["images"][0]["image_id"] = "s9_wrong"
        docs["briefs"]["images"][0]["shot_ids"] = ["S2-1"]
        # Step 8: look source_ovi outside chapter, known entity redecided same state
        docs["looks"]["entries"][0]["source_ovis"] = [99]
        docs["looks"]["entries"][0] = {
            "entity_id": "arjuna",
            "kind": "character",
            "state_id": "battle_ready",  # known state
            "look": "different",
            "source_ovis": [1],
            "basis": "inferred",
        }
        # Step 9: speaking character no voice, voice_key not in saved, recurring duplicate
        docs["voices"]["cast"] = []
        # Step 10: sound scene not exist, anchor not in scene, unknown sound_id, kind mismatch
        docs["sounds"]["cues"][0]["scene_id"] = "S99"
        docs["sounds"]["cues"][0]["anchor_line_id"] = "S2-L1"
        docs["sounds"]["cues"][0]["sound_id"] = "bed_unknown"
        docs["sounds"]["cues"][0]["kind"] = "bed"  # fx_conch is fx but kind bed
        # Step 11: question duplicate id, scene not exist
        docs["questions"]["questions"].append({"id": "Q1", "text": "dup"})
        docs["questions"]["questions"][0]["scene_id"] = "S99"

        ctx = make_ctx(
            chapter_ovis={1, 2, 3, 4, 5},
            unfilmed_ovis={1},
            preset_ids={"01_wide", "02_medium", "03_close"},
            sound_ids={"bed_battlefield", "fx_conch"},
            saved_voices={"arjuna_voice": "v_arjuna_001_valid_id", "krishna_voice": "v_krishna_001_valid_id"},
            speaking_characters={"arjuna", "krishna"},
            known_states={"arjuna": {"battle_ready"}, "krishna": {"charioteer"}, "battlefield": {"dawn_armies"}},
        )
        errs = validate_stage1(1, docs, ctx)
        # Check each step's keywords appear
        keywords = [
            "coverage adhyay 2 does not match 1",  # step 2
            "ovi 2 is untyped", "ovi 3 is untyped", "ovi 4 is untyped", "ovi 5 is untyped",  # step 3
            "ovi 2 has no disposition", "ovi 1 is unfilmed but VISUALISED",  # step 4
            "overlap", "S2-L1", "core", "discourse", "teaching_treatment",  # step 5
            "consecutive", "unknown preset", "S1-L2", "line is in no shot beat",  # step 6
            "prefix", "S2-1", "not belong",  # step 7
            "source_ovis", "99", "outside", "arjuna", "known state", "battle_ready", "redecided",  # step 8
            "arjuna", "no voice assigned", "voice not in the saved cast", "twice",  # step 9
            "S99", "anchor_line_id", "bed_unknown", "kind", "mismatch",  # step 10
            "Q1", "duplicate", "S99",  # step 11
        ]
        for kw in keywords:
            assert any(kw in e for e in errs), f"missing keyword: {kw} in {errs}"

    # --- Step 2: adhyay mismatch ---
    @pytest.mark.parametrize("doc_key", [
        "story_map", "coverage", "scenes", "shots", "briefs", "looks", "voices", "sounds", "questions"
    ])
    def test_adhyay_mismatch_in_document(self, doc_key):
        docs = make_valid_docs(1)
        docs[doc_key]["adhyay"] = 2
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any(f"{doc_key} adhyay 2 does not match 1" in e for e in errs)

    # --- Step 3: story_map semantic ---
    def test_ovi_untyped(self):
        docs = make_valid_docs(1)
        docs["story_map"]["ovi_types"] = [{"ovi": 1, "type": "STORY"}]
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi 2 is untyped" in e for e in errs)
        assert any("ovi 3 is untyped" in e for e in errs)
        assert any("ovi 4 is untyped" in e for e in errs)
        assert any("ovi 5 is untyped" in e for e in errs)

    def test_ovi_typed_twice(self):
        docs = make_valid_docs(1)
        docs["story_map"]["ovi_types"] = [
            {"ovi": 1, "type": "STORY"},
            {"ovi": 1, "type": "TEACHING"},
            {"ovi": 2, "type": "TEACHING"},
            {"ovi": 3, "type": "PHILOSOPHY"},
            {"ovi": 4, "type": "INVOCATION"},
            {"ovi": 5, "type": "RECAP"},
        ]
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi 1 is typed twice" in e for e in errs)

    def test_typed_ovi_outside_chapter_reported(self):
        docs = make_valid_docs(1)
        docs["story_map"]["ovi_types"].append({"ovi": 99, "type": "STORY"})
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi 99" in e and "outside" in e for e in errs)

    def test_event_ovi_range_lo_gt_hi(self):
        docs = make_valid_docs(1)
        docs["story_map"]["events"][0]["ovi_range"] = [5, 1]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        # Message must contain item id (event_id or document) and condition
        assert any("E1" in e and ("ovi_range" in e or "range" in e) for e in errs)

    def test_event_key_ovis_outside_range(self):
        docs = make_valid_docs(1)
        docs["story_map"]["events"][0]["key_ovis"] = [99]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("E1" in e and "key_ovis" in e and "range" in e for e in errs)

    # --- Step 4: coverage semantic ---
    def test_coverage_missing_disposition(self):
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"] = [{"ovi": 1, "disposition": "VISUALISED"}]
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi 2 has no disposition" in e for e in errs)
        assert any("ovi 3 has no disposition" in e for e in errs)
        assert any("ovi 4 has no disposition" in e for e in errs)
        assert any("ovi 5 has no disposition" in e for e in errs)

    def test_coverage_duplicate_disposition(self):
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"] = [
            {"ovi": 1, "disposition": "VISUALISED"},
            {"ovi": 1, "disposition": "NARRATED"},
            {"ovi": 2, "disposition": "NARRATED"},
            {"ovi": 3, "disposition": "QUOTED"},
            {"ovi": 4, "disposition": "MERGED_EQUIVALENT", "reason": "r", "covered_by": 3},
            {"ovi": 5, "disposition": "QUOTED"},
        ]
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi 1" in e and "twice" in e for e in errs)

    def test_propose_omission_note(self):
        """PROPOSE_OMISSION adds a NOTE message starting with 'note: '."""
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"][4] = {"ovi": 5, "disposition": "PROPOSE_OMISSION", "reason": "redundant"}
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        notes = [e for e in errs if e.startswith("note: ")]
        assert any("note: ovi 5 omission proposed, owner approval needed" in e for e in notes)
        # Notes come after errors
        error_msgs = [e for e in errs if not e.startswith("note: ")]
        note_msgs = [e for e in errs if e.startswith("note: ")]
        assert all(not e.startswith("note: ") for e in error_msgs)
        assert all(e.startswith("note: ") for e in note_msgs)

    def test_unfilmed_ovi_visualised_error(self):
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"][0]["disposition"] = "VISUALISED"
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5}, unfilmed_ovis={1})
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi 1 is unfilmed but VISUALISED" in e for e in errs)

    def test_covered_by_invalid_reference(self):
        """Well-formed but nonexistent line_id and ovi outside chapter."""
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"][3]["covered_by"] = "S1-L99"  # well-formed, not in script
        ctx = make_ctx(script_line_ids=["S1-L1"], chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        assert any("covered_by" in e and "S1-L99" in e for e in errs)
        # Also test integer outside chapter_ovis
        docs["coverage"]["ovis"][3]["covered_by"] = 99
        errs = validate_stage1(1, docs, ctx)
        assert any("covered_by" in e and "99" in e for e in errs)

    # --- Step 5: scenes semantic ---
    def test_scene_ids_unique(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"].append({
            "scene_id": "S1",
            "section_kind": "story",
            "ovi_range": [3, 3],
            "goal": "dup",
            "turn": {"ovi": 3, "text": "x"},
            "line_ids": [],
            "teaching_treatment": "none",
        })
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S1" in e and "duplicate" in e.lower() for e in errs)

    def test_scene_range_lo_gt_hi(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][0]["ovi_range"] = [3, 1]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S1" in e and "ovi_range" in e for e in errs)

    def test_scene_ranges_overlap(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][1]["ovi_range"] = [2, 4]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("overlap" in e.lower() for e in errs)

    def test_chapter_ovi_not_in_any_scene(self):
        docs = make_valid_docs(1)
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5, 6})
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi 6" in e and ("not in any scene" in e or "uncovered" in e.lower()) for e in errs)

    def test_unfilmed_ovi_inside_scene_range_error(self):
        docs = make_valid_docs(1)
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5}, unfilmed_ovis={2})
        errs = validate_stage1(1, docs, ctx)
        assert any("S1" in e and "ovi 2 is unfilmed but inside the range" in e for e in errs)

    def test_ovi_outside_chapter_in_scene(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][0]["ovi_range"] = [1, 99]
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        assert any("S1" in e and "ovi 99" in e and "outside" in e for e in errs)

    def test_turn_ovi_outside_scene_range(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][0]["turn"]["ovi"] = 99
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S1" in e and "turn" in e and "ovi" in e and "range" in e for e in errs)

    def test_line_id_not_in_script(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][0]["line_ids"] = ["S1-L99"]
        ctx = make_ctx(script_line_ids=["S1-L1"])
        errs = validate_stage1(1, docs, ctx)
        assert any("S1-L99" in e and ("not in the script" in e or "not in script" in e) for e in errs)

    def test_line_id_used_twice_across_scenes(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][1]["line_ids"] = ["S1-L1"]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S1-L1" in e and ("twice" in e or "duplicate" in e.lower()) for e in errs)

    def test_line_id_used_twice_within_scene(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][0]["line_ids"] = ["S1-L1", "S1-L1"]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S1-L1" in e and ("twice" in e or "duplicate" in e.lower()) for e in errs)

    def test_line_ids_not_in_script_order_within_scene(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][0]["line_ids"] = ["S1-L2", "S1-L1"]
        ctx = make_ctx(script_line_ids=["S1-L1", "S1-L2", "S2-L1"])
        errs = validate_stage1(1, docs, ctx)
        assert any("S1" in e and "order" in e.lower() for e in errs)

    def test_core_line_missing_from_scenes(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][1]["line_ids"] = []
        ctx = make_ctx(core_line_ids={"S1-L1", "S2-L1"})
        errs = validate_stage1(1, docs, ctx)
        assert any("S2-L1" in e and "core" in e.lower() and ("missing" in e.lower() or "not in any scene" in e) for e in errs)

    def test_discourse_scene_requires_treatment(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][1]["teaching_treatment"] = "none"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S2" in e and "discourse" in e.lower() and "teaching_treatment" in e for e in errs)

    # --- Step 6: shots semantic ---
    def test_shot_ids_unique(self):
        docs = make_valid_docs(1)
        docs["shots"]["shots"].append({
            "shot_id": "S1-1",
            "scene_id": "S1",
            "ovi_ids": [1],
            "beat_line_ids": ["S1-L1"],
            "preset": "01_wide",
            "need_new": None,
            "needs_cutout": False,
            "pose": "x",
            "framing": "x",
        })
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S1-1" in e and "duplicate" in e.lower() for e in errs)

    def test_shot_sequence_starts_at_one(self):
        """Shots per scene must be consecutive starting from 1."""
        docs = make_valid_docs(1)
        docs["shots"]["shots"][0]["shot_id"] = "S1-2"  # S1-1 missing
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S1" in e and ("consecutive" in e.lower() or "starts at 1" in e.lower() or "sequence" in e.lower()) for e in errs)

    def test_shot_not_consecutive(self):
        docs = make_valid_docs(1)
        docs["shots"]["shots"][1]["shot_id"] = "S1-3"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S1" in e and ("consecutive" in e.lower() or "sequence" in e.lower()) for e in errs)

    def test_shot_scene_not_exist(self):
        docs = make_valid_docs(1)
        docs["shots"]["shots"][0]["scene_id"] = "S99"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S99" in e and ("scene" in e and "not exist" in e or "unknown" in e.lower()) for e in errs)

    def test_shot_ovi_ids_outside_scene_range(self):
        docs = make_valid_docs(1)
        docs["shots"]["shots"][0]["ovi_ids"] = [99]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S1-1" in e and "ovi" in e and "99" in e and ("range" in e or "scene" in e) for e in errs)

    def test_shot_beat_line_ids_not_in_scene(self):
        docs = make_valid_docs(1)
        docs["shots"]["shots"][0]["beat_line_ids"] = ["S2-L1"]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S1-1" in e and "beat_line_ids" in e and ("scene" in e or "not belong" in e) for e in errs)

    def test_scene_with_no_shots(self):
        docs = make_valid_docs(1)
        docs["shots"]["shots"] = [s for s in docs["shots"]["shots"] if s["scene_id"] != "S2"]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S2" in e and ("no shots" in e or "has no shots" in e) for e in errs)

    def test_core_line_not_in_any_shot_beat(self):
        """Every line of every scene must be in some shot's beat_line_ids."""
        docs = make_valid_docs(1)
        docs["shots"]["shots"] = [s for s in docs["shots"]["shots"] if s["shot_id"] != "S1-2"]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S1-L2" in e and "line is in no shot beat" in e for e in errs)

    def test_shot_unknown_preset(self):
        docs = make_valid_docs(1)
        docs["shots"]["shots"][0]["preset"] = "99_unknown"
        ctx = make_ctx(preset_ids={"01_wide", "02_medium", "03_close"})
        errs = validate_stage1(1, docs, ctx)
        assert any("S1-1" in e and "unknown preset" in e and "99_unknown" in e for e in errs)

    def test_shot_need_new_accepted(self):
        """NEED_NEW shot with valid need_new object is accepted."""
        docs = make_valid_docs(1)
        docs["shots"]["shots"][0] = {
            "shot_id": "S1-1",
            "scene_id": "S1",
            "ovi_ids": [1],
            "beat_line_ids": ["S1-L1"],
            "preset": "NEED_NEW",
            "need_new": {"reason": "unique", "class": "missing_image"},
            "needs_cutout": False,
            "pose": "x",
            "framing": "x",
        }
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert not any("S1-1" in e for e in errs)

    # --- Step 7: briefs semantic ---
    def test_image_ids_unique(self):
        docs = make_valid_docs(1)
        docs["briefs"]["images"].append({
            "image_id": "s1_arjuna_standing",  # duplicate
            "scene_id": "S1",
            "shot_ids": ["S1-1"],
            "people": [{"name": "A", "position": "c", "pose": "p", "gaze": "g"}],
            "place_id": "p",
            "prop": None,
            "prop_state": None,
            "camera": "c",
            "light": "l",
            "reason_new": "r",
            "on_screen_facts": ["f"],
            "references": {"characters": [], "place": "p", "style_anchor": "s", "prop": None},
        })
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("s1_arjuna_standing" in e and "duplicate" in e.lower() for e in errs)

    def test_brief_image_id_scene_prefix(self):
        docs = make_valid_docs(1)
        docs["briefs"]["images"][0]["image_id"] = "s9_wrong_prefix"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("s1_arjuna_standing" in e or "image_id" in e) and any("prefix" in e or "s1" in e.lower() for e in errs)

    def test_brief_scene_not_exist(self):
        docs = make_valid_docs(1)
        docs["briefs"]["images"][0]["scene_id"] = "S99"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S99" in e and ("scene" in e and "not exist" in e or "unknown" in e.lower()) for e in errs)

    def test_brief_shot_missing(self):
        """Shot referenced in brief does not exist."""
        docs = make_valid_docs(1)
        docs["briefs"]["images"][0]["shot_ids"] = ["S1-99"]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S1-99" in e and ("shot" in e and "not exist" in e or "unknown" in e.lower()) for e in errs)

    def test_brief_shot_not_in_scene(self):
        docs = make_valid_docs(1)
        docs["briefs"]["images"][0]["shot_ids"] = ["S2-1"]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S2-1" in e and ("scene" in e or "not belong" in e) for e in errs)

    def test_brief_empty_person_name(self):
        docs = make_valid_docs(1)
        docs["briefs"]["images"][0]["people"][0]["name"] = ""
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("name" in e and ("empty" in e or "missing" in e) for e in errs)

    def test_brief_empty_on_screen_facts(self):
        docs = make_valid_docs(1)
        docs["briefs"]["images"][0]["on_screen_facts"] = []
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("on_screen_facts" in e and ("empty" in e or "non-empty" in e) for e in errs)

    # --- Step 8: looks semantic ---
    def test_look_source_ovi_outside_chapter(self):
        docs = make_valid_docs(1)
        docs["looks"]["entries"][0]["source_ovis"] = [99]
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        assert any("arjuna" in e and "source_ovis" in e and "99" in e and "outside" in e for e in errs)

    def test_known_entity_redecided_same_state_id(self):
        """Known entity with same state_id is an error."""
        docs = make_valid_docs(1)
        docs["looks"]["entries"][0] = {
            "entity_id": "arjuna",
            "kind": "character",
            "state_id": "battle_ready",  # known state for arjuna
            "look": "different look",
            "source_ovis": [1],
            "basis": "inferred",
        }
        ctx = make_ctx(known_states={"arjuna": {"battle_ready"}, "krishna": {"charioteer"}, "battlefield": {"dawn_armies"}})
        errs = validate_stage1(1, docs, ctx)
        assert any("arjuna" in e and "known state" in e and "battle_ready" in e and "redecided" in e for e in errs)

    def test_known_entity_new_state_id_allowed(self):
        """Known entity with NEW state_id is allowed (no error)."""
        docs = make_valid_docs(1)
        docs["looks"]["entries"][0] = {
            "entity_id": "arjuna",
            "kind": "character",
            "state_id": "new_state",  # not in known_states
            "look": "different",
            "source_ovis": [1],
            "basis": "inferred",
        }
        ctx = make_ctx(known_states={"arjuna": {"battle_ready"}, "krishna": {"charioteer"}, "battlefield": {"dawn_armies"}})
        errs = validate_stage1(1, docs, ctx)
        assert not any("redecided" in e for e in errs)
        assert errs == []  # fully valid otherwise

    def test_entity_state_unique(self):
        docs = make_valid_docs(1)
        docs["looks"]["entries"].append({
            "entity_id": "arjuna",
            "kind": "character",
            "state_id": "battle_ready",
            "look": "dup",
            "source_ovis": [2],
            "basis": "stated",
        })
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("arjuna" in e and "battle_ready" in e and ("duplicate" in e.lower() or "unique" in e.lower()) for e in errs)

    # --- Step 9: voices semantic ---
    def test_speaking_character_no_voice(self):
        docs = make_valid_docs(1)
        docs["voices"]["cast"] = []
        ctx = make_ctx(speaking_characters={"arjuna", "krishna"})
        errs = validate_stage1(1, docs, ctx)
        assert any("arjuna" in e and "no voice assigned" in e for e in errs)
        assert any("krishna" in e and "no voice assigned" in e for e in errs)

    def test_voice_key_not_in_saved(self):
        docs = make_valid_docs(1)
        docs["voices"]["cast"][0]["voice_key"] = "unknown_key"
        ctx = make_ctx(saved_voices={"arjuna_voice": "v_arjuna_001_valid_id"})
        errs = validate_stage1(1, docs, ctx)
        assert any("arjuna" in e and "voice not in the saved cast" in e for e in errs)

    def test_voice_id_mismatch_saved(self):
        """Schema-valid voice_id that doesn't match saved_voices."""
        docs = make_valid_docs(1)
        docs["voices"]["cast"][0]["voice_id"] = "v_different_valid_id_001"
        ctx = make_ctx(saved_voices={"arjuna_voice": "v_arjuna_001_valid_id"})
        errs = validate_stage1(1, docs, ctx)
        assert any("arjuna" in e and "voice not in the saved cast" in e for e in errs)

    def test_recurring_character_listed_twice(self):
        docs = make_valid_docs(1)
        docs["voices"]["cast"].append({
            "character_id": "arjuna",
            "voice_key": "arjuna_voice",
            "voice_id": "v_arjuna_001_valid_id",
            "gender": "male",
            "status": "RECURRING",
        })
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("arjuna" in e and ("twice" in e or "duplicate" in e.lower()) for e in errs)

    def test_speaking_character_duplicate_new_proposed(self):
        """Two NEW_PROPOSED entries for same character is an error."""
        docs = make_valid_docs(1)
        docs["voices"]["cast"] = [
            {"character_id": "arjuna", "voice_key": "k1", "voice_id": "v_valid_id_001", "gender": "male", "status": "NEW_PROPOSED"},
            {"character_id": "arjuna", "voice_key": "k2", "voice_id": "v_valid_id_002", "gender": "male", "status": "NEW_PROPOSED"},
        ]
        ctx = make_ctx(speaking_characters={"arjuna"}, saved_voices={"k1": "v_valid_id_001", "k2": "v_valid_id_002"})
        errs = validate_stage1(1, docs, ctx)
        assert any("arjuna" in e and ("twice" in e or "duplicate" in e.lower()) for e in errs)

    def test_two_characters_share_voice_key(self):
        docs = make_valid_docs(1)
        docs["voices"]["cast"][1]["voice_key"] = "arjuna_voice"
        docs["voices"]["cast"][1]["voice_id"] = "v_arjuna_001_valid_id"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("voice_key" in e and "shared" in e.lower() for e in errs)

    def test_narrator_can_share_voice_key(self):
        docs = make_valid_docs(1)
        docs["voices"]["cast"] = [
            {"character_id": "arjuna", "voice_key": "shared_voice", "voice_id": "v_shared_valid_id_001", "gender": "male", "status": "RECURRING"},
            {"character_id": "narrator", "voice_key": "shared_voice", "voice_id": "v_shared_valid_id_001", "gender": "male", "status": "RECURRING"},
        ]
        ctx = make_ctx(
            speaking_characters={"arjuna", "narrator"},
            saved_voices={"shared_voice": "v_shared_valid_id_001"},
        )
        errs = validate_stage1(1, docs, ctx)
        assert not any("shared" in e.lower() for e in errs)
        assert errs == []

    # --- Step 10: sounds semantic ---
    def test_sound_scene_not_exist(self):
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0]["scene_id"] = "S99"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S99" in e and ("scene" in e and "not exist" in e or "unknown" in e.lower()) for e in errs)

    def test_sound_anchor_line_not_in_scene(self):
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0]["anchor_line_id"] = "S2-L1"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S1" in e and "anchor_line_id" in e and ("scene" in e or "not belong" in e) for e in errs)

    def test_sound_id_unknown(self):
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0]["sound_id"] = "bed_unknown"
        ctx = make_ctx(sound_ids={"bed_battlefield"})
        errs = validate_stage1(1, docs, ctx)
        assert any("bed_unknown" in e and ("unknown" in e.lower() or "not in" in e) for e in errs)

    def test_sound_need_new_without_prompt_schema_catches(self):
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0] = {
            "scene_id": "S1",
            "anchor_line_id": "S1-L1",
            "sound_id": "NEED_NEW",
            "kind": "fx",
            "purpose": "test",
            "basis": "stated",
        }
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("sound_prompt" in e for e in errs)

    def test_sound_non_need_new_with_prompt(self):
        """Non-NEED_NEW cue carrying sound_prompt is a SCHEMA error."""
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0]["sound_prompt"] = "should not be here"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("sound_prompt" in e for e in errs)

    def test_sound_kind_mismatch_prefix(self):
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0]["sound_id"] = "fx_conch"
        docs["sounds"]["cues"][0]["kind"] = "bed"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("fx_conch" in e and "kind" in e and ("mismatch" in e or "prefix" in e) for e in errs)

    def test_sound_need_new_accepted(self):
        """NEED_NEW sound with sound_prompt is accepted."""
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0] = {
            "scene_id": "S1",
            "anchor_line_id": "S1-L1",
            "sound_id": "NEED_NEW",
            "kind": "fx",
            "sound_prompt": "conch blow",
            "purpose": "signal",
            "basis": "stated",
        }
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert not any("S1" in e for e in errs)

    # --- Step 11: questions semantic ---
    def test_question_duplicate_id(self):
        docs = make_valid_docs(1)
        docs["questions"]["questions"].append({"id": "Q1", "text": "dup"})
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("Q1" in e and ("duplicate" in e.lower() or "unique" in e.lower()) for e in errs)

    def test_question_scene_not_exist(self):
        docs = make_valid_docs(1)
        docs["questions"]["questions"][0]["scene_id"] = "S99"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S99" in e and ("scene" in e and "not exist" in e or "unknown" in e.lower()) for e in errs)

    # --- Zero-story chapter ---
    def test_zero_story_chapter_validates(self):
        """All ovis TEACHING/PHILOSOPHY, one discourse scene, no story events."""
        docs = {
            "story_map": {
                "adhyay": 2,
                "ovi_types": [
                    {"ovi": 1, "type": "TEACHING"},
                    {"ovi": 2, "type": "PHILOSOPHY"},
                ],
                "events": [
                    {
                        "event_id": "E1",
                        "title": "Teaching",
                        "ovi_range": [1, 2],
                        "key_ovis": [1, 2],
                        "kind": "discourse",
                        "closure": "RESOLVED_IN_ADHYAY",
                    }
                ],
            },
            "coverage": {
                "adhyay": 2,
                "ovis": [
                    {"ovi": 1, "disposition": "NARRATED"},
                    {"ovi": 2, "disposition": "QUOTED"},
                ],
            },
            "scenes": {
                "adhyay": 2,
                "scenes": [
                    {
                        "scene_id": "S1",
                        "section_kind": "discourse",
                        "ovi_range": [1, 2],
                        "goal": "Teaching",
                        "turn": {"ovi": 1, "text": "Krishna teaches"},
                        "line_ids": ["S1-L1"],
                        "teaching_treatment": "contemplative_hold",
                    }
                ],
            },
            "shots": {
                "adhyay": 2,
                "shots": [
                    {
                        "shot_id": "S1-1",
                        "scene_id": "S1",
                        "ovi_ids": [1, 2],
                        "beat_line_ids": ["S1-L1"],
                        "preset": "01_wide",
                        "need_new": None,
                        "needs_cutout": False,
                        "pose": "seated",
                        "framing": "medium",
                    }
                ],
            },
            "briefs": {
                "adhyay": 2,
                "images": [
                    {
                        "image_id": "s1_krishna_teaching",
                        "scene_id": "S1",
                        "shot_ids": ["S1-1"],
                        "people": [
                            {"name": "Krishna", "position": "center", "pose": "seated", "gaze": "forward"}
                        ],
                        "place_id": "chariot",
                        "prop": None,
                        "prop_state": None,
                        "camera": "eye level",
                        "light": "soft",
                        "reason_new": "teaching",
                        "on_screen_facts": ["Krishna teaches"],
                        "references": {
                            "characters": ["Krishna"],
                            "place": "chariot",
                            "style_anchor": "epic realism",
                            "prop": None,
                        },
                    }
                ],
            },
            "looks": {
                "adhyay": 2,
                "entries": [
                    {
                        "entity_id": "krishna",
                        "kind": "character",
                        "state_id": "teacher",
                        "look": "peacock feather",
                        "source_ovis": [1, 2],
                        "basis": "stated",
                    }
                ],
            },
            "voices": {
                "adhyay": 2,
                "cast": [
                    {
                        "character_id": "krishna",
                        "voice_key": "krishna_voice",
                        "voice_id": "v_krishna_001_valid_id",
                        "gender": "male",
                        "status": "RECURRING",
                    }
                ],
            },
            "sounds": {
                "adhyay": 2,
                "cues": [
                    {
                        "scene_id": "S1",
                        "anchor_line_id": "S1-L1",
                        "sound_id": "bed_battlefield",
                        "kind": "bed",
                        "purpose": "ambience",
                        "basis": "staging",
                    }
                ],
            },
            "questions": {"adhyay": 2, "questions": [{"id": "Q1", "text": "What is yoga?"}]},
        }
        ctx = make_ctx(
            script_line_ids=["S1-L1"],
            core_line_ids={"S1-L1"},
            chapter_ovis={1, 2},
            unfilmed_ovis=set(),
            preset_ids={"01_wide"},
            sound_ids={"bed_battlefield"},
            saved_voices={"krishna_voice": "v_krishna_001_valid_id"},
            speaking_characters={"krishna"},
            known_states={"krishna": {"charioteer"}, "chariot": {"interior"}},
        )
        errs = validate_stage1(2, docs, ctx)
        assert errs == [], f"zero-story chapter failed: {errs}"

    def test_zero_story_empty_events_validates(self):
        """Zero-story chapter with empty events array is valid."""
        docs = {
            "story_map": {
                "adhyay": 3,
                "ovi_types": [
                    {"ovi": 1, "type": "TEACHING"},
                    {"ovi": 2, "type": "PHILOSOPHY"},
                ],
                "events": [],  # empty
            },
            "coverage": {
                "adhyay": 3,
                "ovis": [
                    {"ovi": 1, "disposition": "NARRATED"},
                    {"ovi": 2, "disposition": "QUOTED"},
                ],
            },
            "scenes": {
                "adhyay": 3,
                "scenes": [
                    {
                        "scene_id": "S1",
                        "section_kind": "discourse",
                        "ovi_range": [1, 2],
                        "goal": "Teaching",
                        "turn": {"ovi": 1, "text": "Krishna teaches"},
                        "line_ids": ["S1-L1"],
                        "teaching_treatment": "contemplative_hold",
                    }
                ],
            },
            "shots": {
                "adhyay": 3,
                "shots": [
                    {
                        "shot_id": "S1-1",
                        "scene_id": "S1",
                        "ovi_ids": [1, 2],
                        "beat_line_ids": ["S1-L1"],
                        "preset": "01_wide",
                        "need_new": None,
                        "needs_cutout": False,
                        "pose": "seated",
                        "framing": "medium",
                    }
                ],
            },
            "briefs": {
                "adhyay": 3,
                "images": [
                    {
                        "image_id": "s1_krishna_teaching",
                        "scene_id": "S1",
                        "shot_ids": ["S1-1"],
                        "people": [{"name": "Krishna", "position": "center", "pose": "seated", "gaze": "forward"}],
                        "place_id": "chariot",
                        "prop": None,
                        "prop_state": None,
                        "camera": "eye level",
                        "light": "soft",
                        "reason_new": "teaching",
                        "on_screen_facts": ["Krishna teaches"],
                        "references": {"characters": ["Krishna"], "place": "chariot", "style_anchor": "epic realism", "prop": None},
                    }
                ],
            },
            "looks": {
                "adhyay": 3,
                "entries": [
                    {"entity_id": "krishna", "kind": "character", "state_id": "teacher", "look": "peacock feather", "source_ovis": [1, 2], "basis": "stated"}
                ],
            },
            "voices": {
                "adhyay": 3,
                "cast": [{"character_id": "krishna", "voice_key": "krishna_voice", "voice_id": "v_krishna_001_valid_id", "gender": "male", "status": "RECURRING"}],
            },
            "sounds": {
                "adhyay": 3,
                "cues": [{"scene_id": "S1", "anchor_line_id": "S1-L1", "sound_id": "bed_battlefield", "kind": "bed", "purpose": "ambience", "basis": "staging"}],
            },
            "questions": {"adhyay": 3, "questions": [{"id": "Q1", "text": "What is yoga?"}]},
        }
        ctx = make_ctx(
            script_line_ids=["S1-L1"],
            core_line_ids={"S1-L1"},
            chapter_ovis={1, 2},
            unfilmed_ovis=set(),
            preset_ids={"01_wide"},
            sound_ids={"bed_battlefield"},
            saved_voices={"krishna_voice": "v_krishna_001_valid_id"},
            speaking_characters={"krishna"},
            known_states={"krishna": {"charioteer"}, "chariot": {"interior"}},
        )
        errs = validate_stage1(3, docs, ctx)
        assert errs == [], f"zero-story empty events failed: {errs}"

    # --- Stability ---
    def test_messages_stable_order(self):
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"] = []
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs1 = validate_stage1(1, docs, ctx)
        errs2 = validate_stage1(1, docs, ctx)
        assert errs1 == errs2, "error order not stable"
        # Also verify expected diagnostics are present
        assert any("ovi 1 has no disposition" in e for e in errs1)
        assert any("ovi 2 has no disposition" in e for e in errs1)

    def test_notes_follow_errors(self):
        """Notes (PROPOSE_OMISSION) come after all error messages."""
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"][4] = {"ovi": 5, "disposition": "PROPOSE_OMISSION", "reason": "redundant"}
        # Also add a real error
        docs["coverage"]["ovis"] = [{"ovi": 1, "disposition": "VISUALISED"}]  # missing 2-5
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        # Find first note index
        note_indices = [i for i, e in enumerate(errs) if e.startswith("note: ")]
        error_indices = [i for i, e in enumerate(errs) if not e.startswith("note: ")]
        if note_indices and error_indices:
            assert max(error_indices) < min(note_indices), "notes must follow errors"

    def test_message_prefixes(self):
        """Each message starts with item id or document name."""
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"] = []
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        for e in errs:
            # Either starts with document name (story_map, coverage, etc.) or item id (S1, E1, Q1, ovi N, etc.)
            # or "note: "
            assert e.startswith("note: ") or any(e.startswith(prefix) for prefix in [
                "story_map", "coverage", "scenes", "shots", "briefs", "looks", "voices", "sounds", "questions",
                "S1", "S2", "E1", "E2", "Q1", "Q2", "ovi 1", "ovi 2", "ovi 3", "ovi 4", "ovi 5",
                "s1_", "s2_", "arjuna", "krishna", "battlefield"
            ]), f"message lacks required prefix: {e}"

    # --- Missing references never raise ---
    def test_missing_references_no_exception(self):
        """Validator never raises, only returns error strings.
        Empty context should produce specific missing-reference diagnostics."""
        docs = make_valid_docs(1)
        ctx = make_ctx(
            script_line_ids=[],
            core_line_ids=set(),
            chapter_ovis=set(),
            unfilmed_ovis=set(),
            preset_ids=set(),
            sound_ids=set(),
            saved_voices={},
            speaking_characters=set(),
            known_states={},
        )
        errs = validate_stage1(1, docs, ctx)
        assert isinstance(errs, list)
        assert all(isinstance(e, str) for e in errs)
        # Should have specific missing-reference errors
        assert any("S1-L1" in e and "not in the script" in e for e in errs)
        assert any("ovi 1" in e and ("no disposition" in e or "untyped" in e) for e in errs)

    def test_empty_context_survives(self):
        """Intentionally empty sets/dicts in context are not replaced by defaults."""
        ctx = make_ctx(
            script_line_ids=[],
            core_line_ids=set(),
            chapter_ovis=set(),
            unfilmed_ovis=set(),
            preset_ids=set(),
            sound_ids=set(),
            saved_voices={},
            speaking_characters=set(),
            known_states={},
        )
        assert ctx["script_line_ids"] == []
        assert ctx["core_line_ids"] == set()
        assert ctx["chapter_ovis"] == set()
        assert ctx["unfilmed_ovis"] == set()
        assert ctx["preset_ids"] == set()
        assert ctx["sound_ids"] == set()
        assert ctx["saved_voices"] == {}
        assert ctx["speaking_characters"] == set()
        assert ctx["known_states"] == {}

    # --- Deliberately broken implementation style cases ---
    def test_broken_implementation_extra_fields_ignored(self):
        docs = make_valid_docs(1)
        docs["story_map"]["extra_top_level"] = "ignored"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("additionalProperties" in e or "extra_top_level" in e for e in errs)

    def test_broken_implementation_wrong_type_not_caught_by_schema(self):
        docs = make_valid_docs(1)
        docs["story_map"]["ovi_types"] = [{"ovi": "one", "type": "STORY"}]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi" in e and ("type" in e or "integer" in e) for e in errs)

    def test_broken_implementation_missing_required_field(self):
        docs = make_valid_docs(1)
        del docs["scenes"]["scenes"][0]["goal"]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("goal" in e and ("required" in e or "missing" in e) for e in errs)

```
