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