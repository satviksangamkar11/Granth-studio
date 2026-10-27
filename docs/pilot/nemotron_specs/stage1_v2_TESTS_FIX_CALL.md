# THIS IS A FIX CALL for the TEST files. Write ONLY the two corrected test files `tests/test_stage1_schemas.py` and `tests/test_validate_stage1.py` (do NOT write the modules). Apply EVERY item of the Codex review below to your previous tests (shown after it), following the updated spec. Keep the good tests, repair the faulty ones, add the missing ones. Tests must be synthetic/tmp only, each rule must have its own isolated failing case, positive cases must assert `[]` exactly, and nothing may depend on which implementation passes. Reply with exactly two FILE blocks.

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


## CODEX REVIEW OF YOUR FIRST TESTS (apply all 14 items)
**FIX FIRST.** No: several rules lack independent failing cases, and some tests would reject a conforming implementation.

References: **S** = [test_stage1_schemas.py](/D:/aai%20work/granthstudio/docs/pilot/nemotron_specs/review_stage1_tests/test_stage1_schemas.py); **V** = [test_validate_stage1.py](/D:/aai%20work/granthstudio/docs/pilot/nemotron_specs/review_stage1_tests/test_validate_stage1.py). Line numbers below identify supporting evidence.

1. **HIGH — Fix the baseline fixture and `test_fully_valid_returns_empty` (V:47–86, 276–280).** `make_valid_docs()` includes `PROPOSE_OMISSION` for ovi 5, which must return a note; asserting `[]` contradicts the spec. Make the baseline note-free. Have `test_propose_omission_note` introduce the omission explicitly and assert the exact note, including its required `note:` prefix.

2. **HIGH — Resolve the canon-state contract before freezing three tests (V:602–631, 788–923).** The spec says a known character must keep its state “unchanged unless the entry is a new state (state_id different),” but `known_entities` contains only entity IDs. There is no prior state against which to compare. The tests invent knowledge of `battle_ready`; the zero-story fixture also contains a known character. Specify either a context mapping of existing entity/state pairs or an explicit entity-only rejection rule. Then rewrite `test_known_entity_redecided_same_state_id`, `test_known_entity_new_state_id_allowed`, and the positive fixtures accordingly.

3. **HIGH — Repair invalid schema fixtures.** In `test_merged_equivalent_requires_covered_by` (S:203–225), supply `reason` in both cases; the supposed passing example currently violates the spec. Add `test_merged_equivalent_requires_reason`, retaining valid `covered_by`. In `test_gender_enum` and `test_status_enum` (S:729–761), replace five-character `v_001` with a valid 10–40-character ID.

4. **HIGH — Make semantic-reference tests reach semantics.** `test_covered_by_invalid_reference` (V:382–387) uses schema-invalid `INVALID-LINE`; a schema-only implementation can pass it. Use well-formed, nonexistent `S1-L99`, preserve other context, and add an integer outside `chapter_ovis`. `test_voice_id_mismatch_saved` (V:665–670) similarly needs a schema-valid mismatching ID instead of eight-character `wrong_id`; retain the complete saved cast.

5. **HIGH — Replace the legacy-schema checks (S:964–998).** `test_beats_schema_keys` incorrectly expects top-level `beats`; the current schema has `scenes`. `test_animation_scene_schema_keys` incorrectly expects `scenes`; it has `scene_id` and `shots`. All four tests permit nested definitions, constraints, and required fields to change. Embed independent frozen expected schemas, write those expected copies under `tmp_path`, and compare complete parsed definitions. Do not derive expectations from candidate output.

6. **HIGH — Fix `make_ctx` and `test_missing_references_no_exception` (V:22–44, 936–954).** Every `value or default` discards intentionally empty values. An in-memory probe confirmed that empty script IDs, chapter ovis, saved voices, and known entities become populated defaults. Default only when the argument is `None`. Assert that empties survive, then require specific missing-reference diagnostics: `[]` currently passes both assertions.

7. **HIGH — Strengthen phase-control tests (V:282–293).** `test_schema_error_stops_early` asserts absence of an adhyay mismatch without introducing one. Add that mismatch plus schema errors in multiple documents; require all schema errors and no semantic errors. Add `test_collects_all_semantic_steps` with independent violations across steps 2–11, asserting each diagnostic. No current test proves semantic validation continues after an earlier failure.

8. **HIGH — Add missing independent semantic cases.** Add `test_image_ids_unique`, `test_brief_shot_missing`, `test_line_id_used_twice_within_scene`, `test_shot_sequence_starts_at_one`, `test_speaking_character_duplicate_new_proposed`, and `test_core_line_not_in_any_shot_beat`. Existing related cases cover cross-scene duplicates, sequence gaps, recurring duplicates, and an optional line only. Parameterize `test_adhyay_mismatch_in_document` over all nine documents. Add accepted semantic `NEED_NEW` shot/sound cases.

9. **MEDIUM — Remove collateral failures from targeted tests.** `test_two_characters_share_voice_key` (V:687–692) also creates a saved-ID mismatch: update both key and ID. `test_shot_unknown_preset` (V:551–556) removes other valid presets from context: preserve them. In `test_chapter_ovi_not_in_any_scene` (V:421–426), type and disposition ovi 6 first. Apply the same isolation principle to range, line, and missing-shot cases by repairing dependent references.

10. **MEDIUM — Strengthen permissive positive and stability assertions.** After fixing the baseline, require `[]` in `test_known_entity_new_state_id_allowed` and `test_narrator_can_share_voice_key` (V:631, 718); unrelated schema errors currently satisfy them. In `test_messages_stable_order` (V:926–933), assert expected diagnostics before comparing outputs; two empty lists pass. Add `test_notes_follow_errors` and `test_message_prefixes`; neither contract is currently checked.

11. **MEDIUM — Complete schema adversarial coverage.** Add parameterized `test_common_type_boundaries` for every specified ID pattern, ovi minimum, adhyay bounds, text limits, and voice-ID accepted boundaries. Add `test_required_fields`, `test_range_has_exactly_two_items`, `test_nested_extra_keys_rejected`, and invalid-value cases for every enum. Only the ovi-type enum has an explicit invalid-value rejection test. Add missing-`need_new` rejection and story-treatment-absent acceptance cases. Current extra-key tests do not prove `additionalProperties: false` everywhere.

12. **MEDIUM — Remove invented message requirements.** The spec requires quoted keywords, not arbitrary synonyms. Tests such as `test_event_ovi_range_invalid`, `test_scene_range_order`, `test_brief_image_id_scene_prefix`, `test_sound_kind_mismatch_prefix`, and `test_sound_non_need_new_with_prompt` require unmandated literal words. V:580–592 also assumes particular schema wording for empty names/facts. Assert mandated phrases exactly; otherwise identify the document/item/path and violated condition without imposing undocumented prose.

13. **MEDIUM — Clarify two further spec ambiguities.** “additionalProperties: false everywhere” conflicts with preserving legacy dictionary schemas. Specify “every Stage 1 object,” with legacy schemas unchanged. “No print” conflicts with “message starts with the item id or the document name” only indirectly, while omission notes explicitly start `note:`: state the note exception and define diagnostic templates for currently unquoted rules. Specify empty-event acceptance; retain the discourse-event zero-story case and add `test_zero_story_empty_events_validates`.

14. **MEDIUM — Fix harness and generator-contract gaps.** Both files’ `ROOT` resolves incorrectly in their present staging location; V:9–17 points to a nonexistent nested `scripts` path. It matches the specified eventual `tests/` location, so document that relocation before execution. `write_all` (S:27) is an unspecified API assumption: define it or test the documented CLI. Add `test_refuses_overwrite`, `test_overwrite_replaces`, and `test_generated_schema_dialect`. Generate validator schemas under temporary storage and isolate schema caches; current validator tests inherit repository schema loading.

Data fixtures are synthetic; no definite test-order dependence was established. Review and in-memory probes only—no suite execution, edits, secret access, or web use. Current implementation failures alone were not treated as test defects.

## YOUR PREVIOUS tests/test_stage1_schemas.py
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
            # MERGED_EQUIVALENT and PROPOSE_OMISSION need extra fields per if/then
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
        # missing covered_by -> error
        doc = {"adhyay": 1, "ovis": [{"ovi": 1, "disposition": "MERGED_EQUIVALENT"}]}
        errs = validate(doc, schema)
        assert any("covered_by" in e.lower() for e in errs)
        # with covered_by -> ok
        doc = {
            "adhyay": 1,
            "ovis": [
                {
                    "ovi": 1,
                    "disposition": "MERGED_EQUIVALENT",
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
        # extra fields allowed but not required; should still validate
        assert validate(doc, schema) == []


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
                    # teaching_treatment missing
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
                    "events": ["E1"],  # old field, must be rejected
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


class TestStage1VoiceCastSchema:
    def test_valid_minimal(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_voice_cast")
        doc = {
            "adhyay": 1,
            "cast": [
                {
                    "character_id": "arjuna",
                    "voice_key": "arjuna_voice",
                    "voice_id": "v_arjuna_001",
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
                    "voice_id": "v_arjuna_001",
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
                        "voice_id": "v_001",
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
                        "voice_id": "v_001",
                        "gender": "male",
                        "status": s,
                    }
                ],
            }
            assert validate(doc, schema) == [], f"status {s} failed"

    def test_voice_id_length(self, schemas_dir):
        schema = load_schema(schemas_dir, "stage1_voice_cast")
        # too short
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
        # too long
        doc["cast"][0]["voice_id"] = "x" * 41
        errs = validate(doc, schema)
        assert any("voice_id" in e for e in errs)


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


class TestOldSchemasUnchanged:
    """Ensure the four non-Stage-1 schemas are exactly as they were."""

    def test_beats_schema_keys(self, schemas_dir):
        schema = load_schema(schemas_dir, "beats")
        # Check required top-level keys exist
        assert "properties" in schema
        props = schema["properties"]
        assert "adhyay" in props
        assert "beats" in props
        assert schema.get("additionalProperties") is False

    def test_image_catalog_schema_keys(self, schemas_dir):
        schema = load_schema(schemas_dir, "image_catalog")
        assert "properties" in schema
        props = schema["properties"]
        assert "adhyay" in props
        assert "images" in props
        assert schema.get("additionalProperties") is False

    def test_animation_scene_schema_keys(self, schemas_dir):
        schema = load_schema(schemas_dir, "animation_scene")
        assert "properties" in schema
        props = schema["properties"]
        assert "adhyay" in props
        assert "scenes" in props
        assert schema.get("additionalProperties") is False

    def test_shot_plan_schema_keys(self, schemas_dir):
        schema = load_schema(schemas_dir, "shot_plan")
        assert "properties" in schema
        props = schema["properties"]
        assert "adhyay" in props
        assert "shots" in props
        assert schema.get("additionalProperties") is False

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
    known_entities=None,
):
    return {
        "script_line_ids": script_line_ids or ["S1-L1", "S1-L2", "S2-L1"],
        "core_line_ids": core_line_ids or {"S1-L1", "S2-L1"},
        "chapter_ovis": chapter_ovis or {1, 2, 3, 4, 5},
        "unfilmed_ovis": unfilmed_ovis or set(),
        "preset_ids": preset_ids or {"01_wide", "02_medium", "03_close"},
        "sound_ids": sound_ids or {"bed_battlefield", "fx_conch"},
        "saved_voices": saved_voices or {"arjuna_voice": "v_arjuna_001", "krishna_voice": "v_krishna_001"},
        "speaking_characters": speaking_characters or {"arjuna", "krishna"},
        "known_entities": known_entities or {"arjuna", "krishna", "battlefield"},
    }


def make_valid_docs(adhyay=1):
    """Return a fully valid set of nine documents for the given adhyay."""
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
                {"ovi": 5, "disposition": "PROPOSE_OMISSION", "reason": "redundant"},
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
                    "voice_id": "v_arjuna_001",
                    "gender": "male",
                    "status": "RECURRING",
                },
                {
                    "character_id": "krishna",
                    "voice_key": "krishna_voice",
                    "voice_id": "v_krishna_001",
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
    def test_fully_valid_returns_empty(self):
        docs = make_valid_docs(1)
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert errs == [], f"expected no errors, got: {errs}"

    def test_schema_error_stops_early(self):
        # Invalid story_map (missing required field)
        docs = make_valid_docs(1)
        docs["story_map"] = {"adhyay": 1, "ovi_types": [], "events": []}
        # Remove required ovi_types entries to trigger schema error
        docs["story_map"]["ovi_types"] = [{"ovi": 1}]  # missing type
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        # Should have schema errors and stop
        assert any("story_map" in e and "type" in e for e in errs)
        # Should not proceed to semantic checks
        assert not any("adhyay" in e and "does not match" in e for e in errs)

    def test_adhyay_mismatch_in_document(self):
        docs = make_valid_docs(1)
        docs["coverage"]["adhyay"] = 2
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("coverage adhyay 2 does not match 1" in e for e in errs)

    # --- Story map semantic tests ---
    def test_ovi_untyped(self):
        docs = make_valid_docs(1)
        docs["story_map"]["ovi_types"] = [{"ovi": 1, "type": "STORY"}]  # missing 2-5
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi 2 is untyped" in e for e in errs)
        assert any("ovi 3 is untyped" in e for e in errs)

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

    def test_event_ovi_range_invalid(self):
        docs = make_valid_docs(1)
        docs["story_map"]["events"][0]["ovi_range"] = [5, 1]  # lo > hi
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi_range" in e and ("lo" in e or "high" in e or "order" in e) for e in errs)

    def test_event_key_ovis_outside_range(self):
        docs = make_valid_docs(1)
        docs["story_map"]["events"][0]["key_ovis"] = [99]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("key_ovis" in e and "range" in e for e in errs)

    # --- Coverage semantic tests ---
    def test_coverage_missing_disposition(self):
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"] = [{"ovi": 1, "disposition": "VISUALISED"}]  # missing 2-5
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi 2 has no disposition" in e for e in errs)

    def test_coverage_duplicate_disposition(self):
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"] = [
            {"ovi": 1, "disposition": "VISUALISED"},
            {"ovi": 1, "disposition": "NARRATED"},
            {"ovi": 2, "disposition": "NARRATED"},
            {"ovi": 3, "disposition": "QUOTED"},
            {"ovi": 4, "disposition": "MERGED_EQUIVALENT", "reason": "r", "covered_by": 3},
            {"ovi": 5, "disposition": "PROPOSE_OMISSION", "reason": "r"},
        ]
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi 1" in e and "twice" in e for e in errs)

    def test_propose_omission_note(self):
        docs = make_valid_docs(1)
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        # PROPOSE_OMISSION for ovi 5 should produce a note
        assert any("note: ovi 5 omission proposed, owner approval needed" in e for e in errs)

    def test_unfilmed_ovi_visualised_error(self):
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"][0]["disposition"] = "VISUALISED"  # ovi 1
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5}, unfilmed_ovis={1})
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi 1 is unfilmed but VISUALISED" in e for e in errs)

    def test_covered_by_invalid_reference(self):
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"][3]["covered_by"] = "INVALID-LINE"
        ctx = make_ctx(script_line_ids=["S1-L1"], chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        assert any("covered_by" in e and ("INVALID-LINE" in e or "invalid" in e.lower()) for e in errs)

    # --- Scenes semantic tests ---
    def test_scene_ids_unique(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"].append(
            {
                "scene_id": "S1",
                "section_kind": "story",
                "ovi_range": [3, 3],
                "goal": "dup",
                "turn": {"ovi": 3, "text": "x"},
                "line_ids": [],
                "teaching_treatment": "none",
            }
        )
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("scene" in e.lower() and "duplicate" in e.lower() for e in errs)

    def test_scene_range_order(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][0]["ovi_range"] = [3, 1]  # lo > hi
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi_range" in e and ("order" in e or "lo" in e or "high" in e) for e in errs)

    def test_scene_ranges_overlap(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][1]["ovi_range"] = [2, 4]  # overlaps with S1 [1,2]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("overlap" in e.lower() for e in errs)

    def test_chapter_ovi_not_in_any_scene(self):
        docs = make_valid_docs(1)
        # S1 covers 1-2, S2 covers 3-5, but chapter has 6
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5, 6})
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi 6" in e and ("not in any scene" in e or "uncovered" in e.lower()) for e in errs)

    def test_unfilmed_ovi_inside_scene_range_error(self):
        docs = make_valid_docs(1)
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5}, unfilmed_ovis={2})
        # S1 covers 1-2, ovi 2 is unfilmed but inside range
        errs = validate_stage1(1, docs, ctx)
        assert any("S1" in e and "ovi 2 is unfilmed but inside the range" in e for e in errs)

    def test_ovi_outside_chapter_in_scene(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][0]["ovi_range"] = [1, 99]
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        assert any("ovi 99" in e and "outside" in e for e in errs)

    def test_turn_ovi_outside_scene_range(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][0]["turn"]["ovi"] = 99
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("turn" in e and "ovi" in e and "range" in e for e in errs)

    def test_line_id_not_in_script(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][0]["line_ids"] = ["S1-L99"]
        ctx = make_ctx(script_line_ids=["S1-L1"])
        errs = validate_stage1(1, docs, ctx)
        assert any("S1-L99" in e and ("not in script" in e or "unknown" in e.lower()) for e in errs)

    def test_line_id_used_twice_across_scenes(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][1]["line_ids"] = ["S1-L1"]  # already in S1
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S1-L1" in e and ("twice" in e or "duplicate" in e.lower()) for e in errs)

    def test_line_ids_not_in_script_order_within_scene(self):
        docs = make_valid_docs(1)
        # Script order: S1-L1, S1-L2, S2-L1
        # Scene S1 uses L2 then L1 (wrong order)
        docs["scenes"]["scenes"][0]["line_ids"] = ["S1-L2", "S1-L1"]
        ctx = make_ctx(script_line_ids=["S1-L1", "S1-L2", "S2-L1"])
        errs = validate_stage1(1, docs, ctx)
        assert any("order" in e.lower() and "S1" in e for e in errs)

    def test_core_line_missing_from_scenes(self):
        docs = make_valid_docs(1)
        # S2-L1 is core but not in any scene
        docs["scenes"]["scenes"][1]["line_ids"] = []
        ctx = make_ctx(core_line_ids={"S1-L1", "S2-L1"})
        errs = validate_stage1(1, docs, ctx)
        assert any("S2-L1" in e and ("core" in e.lower() and "missing" in e.lower() or "not in any scene" in e) for e in errs)

    def test_discourse_scene_requires_treatment(self):
        docs = make_valid_docs(1)
        docs["scenes"]["scenes"][1]["teaching_treatment"] = "none"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("discourse" in e.lower() and "teaching_treatment" in e for e in errs)

    # --- Shots semantic tests ---
    def test_shot_ids_unique_and_consecutive(self):
        docs = make_valid_docs(1)
        # Duplicate shot id
        docs["shots"]["shots"].append(
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
            }
        )
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("shot" in e.lower() and "duplicate" in e.lower() for e in errs)

    def test_shot_not_consecutive(self):
        docs = make_valid_docs(1)
        docs["shots"]["shots"][1]["shot_id"] = "S1-3"  # skip S1-2
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("consecutive" in e.lower() or "sequence" in e.lower() for e in errs)

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
        assert any("ovi" in e and "99" in e and ("range" in e or "scene" in e) for e in errs)

    def test_shot_beat_line_ids_not_in_scene(self):
        docs = make_valid_docs(1)
        docs["shots"]["shots"][0]["beat_line_ids"] = ["S2-L1"]  # belongs to S2
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("beat_line_ids" in e and ("scene" in e or "not belong" in e) for e in errs)

    def test_scene_with_no_shots(self):
        docs = make_valid_docs(1)
        docs["shots"]["shots"] = [s for s in docs["shots"]["shots"] if s["scene_id"] != "S2"]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S2" in e and ("no shots" in e or "has no shots" in e) for e in errs)

    def test_line_not_in_any_shot_beat(self):
        docs = make_valid_docs(1)
        # S1-L2 is in scene S1 but not in any shot's beat_line_ids
        docs["shots"]["shots"] = [s for s in docs["shots"]["shots"] if s["shot_id"] != "S1-2"]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S1-L2" in e and "line is in no shot beat" in e for e in errs)

    def test_shot_unknown_preset(self):
        docs = make_valid_docs(1)
        docs["shots"]["shots"][0]["preset"] = "99_unknown"
        ctx = make_ctx(preset_ids={"01_wide"})
        errs = validate_stage1(1, docs, ctx)
        assert any("unknown preset" in e and "99_unknown" in e for e in errs)

    # --- Briefs semantic tests ---
    def test_brief_image_id_scene_prefix(self):
        docs = make_valid_docs(1)
        docs["briefs"]["images"][0]["image_id"] = "s9_wrong_prefix"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("image_id" in e and "prefix" in e and "s1" in e.lower() for e in errs)

    def test_brief_scene_not_exist(self):
        docs = make_valid_docs(1)
        docs["briefs"]["images"][0]["scene_id"] = "S99"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S99" in e and ("scene" in e and "not exist" in e or "unknown" in e.lower()) for e in errs)

    def test_brief_shot_not_in_scene(self):
        docs = make_valid_docs(1)
        docs["briefs"]["images"][0]["shot_ids"] = ["S2-1"]  # belongs to S2
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("shot" in e and "S2-1" in e and ("scene" in e or "not belong" in e) for e in errs)

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

    # --- Looks semantic tests ---
    def test_look_source_ovi_outside_chapter(self):
        docs = make_valid_docs(1)
        docs["looks"]["entries"][0]["source_ovis"] = [99]
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs = validate_stage1(1, docs, ctx)
        assert any("source_ovis" in e and "99" in e and "outside" in e for e in errs)

    def test_known_entity_redecided_same_state_id(self):
        docs = make_valid_docs(1)
        # arjuna is in known_entities with state_id battle_ready
        # Entry has same entity_id and same state_id -> error
        docs["looks"]["entries"][0] = {
            "entity_id": "arjuna",
            "kind": "character",
            "state_id": "battle_ready",
            "look": "different look",
            "source_ovis": [1],
            "basis": "inferred",
        }
        ctx = make_ctx(known_entities={"arjuna"})
        errs = validate_stage1(1, docs, ctx)
        assert any("arjuna" in e and "known entity redecided with the same state id" in e for e in errs)

    def test_known_entity_new_state_id_allowed(self):
        docs = make_valid_docs(1)
        # New state_id for known entity should be OK
        docs["looks"]["entries"][0] = {
            "entity_id": "arjuna",
            "kind": "character",
            "state_id": "new_state",
            "look": "different",
            "source_ovis": [1],
            "basis": "inferred",
        }
        ctx = make_ctx(known_entities={"arjuna"})
        errs = validate_stage1(1, docs, ctx)
        assert not any("redecided" in e for e in errs)

    def test_entity_state_unique(self):
        docs = make_valid_docs(1)
        docs["looks"]["entries"].append(
            {
                "entity_id": "arjuna",
                "kind": "character",
                "state_id": "battle_ready",
                "look": "dup",
                "source_ovis": [2],
                "basis": "stated",
            }
        )
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("arjuna" in e and "battle_ready" in e and ("duplicate" in e.lower() or "unique" in e.lower()) for e in errs)

    # --- Voices semantic tests ---
    def test_speaking_character_no_voice(self):
        docs = make_valid_docs(1)
        docs["voices"]["cast"] = []  # no cast entries
        ctx = make_ctx(speaking_characters={"arjuna", "krishna"})
        errs = validate_stage1(1, docs, ctx)
        assert any("arjuna" in e and "no voice assigned" in e for e in errs)
        assert any("krishna" in e and "no voice assigned" in e for e in errs)

    def test_voice_key_not_in_saved(self):
        docs = make_valid_docs(1)
        docs["voices"]["cast"][0]["voice_key"] = "unknown_key"
        ctx = make_ctx(saved_voices={"arjuna_voice": "v_arjuna_001"})
        errs = validate_stage1(1, docs, ctx)
        assert any("arjuna" in e and "voice not in the saved cast" in e for e in errs)

    def test_voice_id_mismatch_saved(self):
        docs = make_valid_docs(1)
        docs["voices"]["cast"][0]["voice_id"] = "wrong_id"
        ctx = make_ctx(saved_voices={"arjuna_voice": "v_arjuna_001"})
        errs = validate_stage1(1, docs, ctx)
        assert any("arjuna" in e and "voice not in the saved cast" in e for e in errs)

    def test_recurring_character_listed_twice(self):
        docs = make_valid_docs(1)
        docs["voices"]["cast"].append(
            {
                "character_id": "arjuna",
                "voice_key": "arjuna_voice",
                "voice_id": "v_arjuna_001",
                "gender": "male",
                "status": "RECURRING",
            }
        )
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("arjuna" in e and ("twice" in e or "duplicate" in e.lower()) for e in errs)

    def test_two_characters_share_voice_key(self):
        docs = make_valid_docs(1)
        docs["voices"]["cast"][1]["voice_key"] = "arjuna_voice"  # same as arjuna
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("voice_key" in e and "shared" in e.lower() for e in errs)

    def test_narrator_can_share_voice_key(self):
        # Narrator is allowed to share voice_key
        docs = make_valid_docs(1)
        docs["voices"]["cast"] = [
            {
                "character_id": "arjuna",
                "voice_key": "shared_voice",
                "voice_id": "v_shared_001",
                "gender": "male",
                "status": "RECURRING",
            },
            {
                "character_id": "narrator",
                "voice_key": "shared_voice",
                "voice_id": "v_shared_001",
                "gender": "male",
                "status": "RECURRING",
            },
        ]
        ctx = make_ctx(
            speaking_characters={"arjuna", "narrator"},
            saved_voices={"shared_voice": "v_shared_001"},
        )
        errs = validate_stage1(1, docs, ctx)
        assert not any("shared" in e.lower() for e in errs)

    # --- Sounds semantic tests ---
    def test_sound_scene_not_exist(self):
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0]["scene_id"] = "S99"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("S99" in e and ("scene" in e and "not exist" in e or "unknown" in e.lower()) for e in errs)

    def test_sound_anchor_line_not_in_scene(self):
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0]["anchor_line_id"] = "S2-L1"  # belongs to S2
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("anchor_line_id" in e and ("scene" in e or "not belong" in e) for e in errs)

    def test_sound_id_unknown(self):
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0]["sound_id"] = "bed_unknown"
        ctx = make_ctx(sound_ids={"bed_battlefield"})
        errs = validate_stage1(1, docs, ctx)
        assert any("unknown" in e.lower() and "bed_unknown" in e for e in errs)

    def test_sound_need_new_without_prompt_schema_catches(self):
        # This is caught by schema validation, not semantic
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
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0]["sound_prompt"] = "should not be here"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("sound_prompt" in e and ("not allowed" in e or "forbidden" in e or "unexpected" in e) for e in errs)

    def test_sound_kind_mismatch_prefix(self):
        docs = make_valid_docs(1)
        docs["sounds"]["cues"][0]["sound_id"] = "fx_conch"
        docs["sounds"]["cues"][0]["kind"] = "bed"  # prefix fx but kind bed
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("kind" in e and ("mismatch" in e or "prefix" in e) for e in errs)

    # --- Questions semantic tests ---
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

    # --- Zero-story chapter test ---
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
                        "voice_id": "v_krishna_001",
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
            saved_voices={"krishna_voice": "v_krishna_001"},
            speaking_characters={"krishna"},
            known_entities={"krishna", "chariot"},
        )
        errs = validate_stage1(2, docs, ctx)
        assert errs == [], f"zero-story chapter failed: {errs}"

    # --- Stability test ---
    def test_messages_stable_order(self):
        """Same input produces same error list order."""
        docs = make_valid_docs(1)
        docs["coverage"]["ovis"] = []  # missing all dispositions
        ctx = make_ctx(chapter_ovis={1, 2, 3, 4, 5})
        errs1 = validate_stage1(1, docs, ctx)
        errs2 = validate_stage1(1, docs, ctx)
        assert errs1 == errs2, "error order not stable"

    # --- Missing references never raise ---
    def test_missing_references_no_exception(self):
        """Validator never raises, only returns error strings."""
        docs = make_valid_docs(1)
        # Remove all context references
        ctx = make_ctx(
            script_line_ids=[],
            core_line_ids=set(),
            chapter_ovis=set(),
            unfilmed_ovis=set(),
            preset_ids=set(),
            sound_ids=set(),
            saved_voices={},
            speaking_characters=set(),
            known_entities=set(),
        )
        # Should not raise
        errs = validate_stage1(1, docs, ctx)
        assert isinstance(errs, list)
        assert all(isinstance(e, str) for e in errs)

    # --- Deliberately broken implementation style cases ---
    def test_broken_implementation_extra_fields_ignored(self):
        """If implementation ignores extra fields, schema should catch it."""
        docs = make_valid_docs(1)
        docs["story_map"]["extra_top_level"] = "ignored"
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("additionalProperties" in e or "extra_top_level" in e for e in errs)

    def test_broken_implementation_wrong_type_not_caught_by_schema(self):
        """If implementation passes wrong type, semantic check should catch."""
        docs = make_valid_docs(1)
        docs["story_map"]["ovi_types"] = [{"ovi": "one", "type": "STORY"}]  # ovi as string
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        # Schema should catch type mismatch
        assert any("ovi" in e and ("type" in e or "integer" in e) for e in errs)

    def test_broken_implementation_missing_required_field(self):
        """If implementation omits required field, schema catches it."""
        docs = make_valid_docs(1)
        del docs["scenes"]["scenes"][0]["goal"]
        ctx = make_ctx()
        errs = validate_stage1(1, docs, ctx)
        assert any("goal" in e and ("required" in e or "missing" in e) for e in errs)

```
