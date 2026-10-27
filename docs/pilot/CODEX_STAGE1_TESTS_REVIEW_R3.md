**FIX FIRST.**

**S** = [test_stage1_schemas.py](</D:/aai work/granthstudio/docs/pilot/nemotron_specs/review_stage1_tests_v3/test_stage1_schemas.py>); **V** = [test_validate_stage1.py](</D:/aai work/granthstudio/docs/pilot/nemotron_specs/review_stage1_tests_v3/test_validate_stage1.py>). References are file:line.

1. **HIGH — Mutation cases crash before validation.** S:390, 413–414 in `test_single_mutation_rejected` call three-argument `mutate()` with five arguments, producing `TypeError`. S:393 traverses baseline `need_new=None`, also producing `TypeError`. In-memory probes reproduced all four failures. Nest mutations correctly; initialize a valid NEED_NEW shot before mutating its class.

2. **HIGH — Invalid scene ID expected to pass.** `test_boundaries` (S:527) accepts `S100`, although the specified regex permits only one or two digits. Change this case to rejection; `S0` remains valid.

3. **HIGH — Schema tests demand semantic validation.** `test_single_mutation_rejected` requires schema rejection of reversed event ranges (S:371), event key ovis outside their range (372), and reversed scene ranges (386). The spec assigns these checks to validator steps 3 and 5. S:384 similarly demands schema rejection of discourse treatment `"none"`, whose rejection is explicitly semantic. Remove these schema-negative expectations and retain their semantic tests.

4. **HIGH — Aggregate assertions still describe nonexistent violations.** In `test_collects_all_semantic_steps`, V:218 renames `S1-2`, so filtering that old ID at 220 leaves `S1-L2` covered. V:226–233 overwrites `[99]` with `[1]`; 235 empties the cast; 239–240 leaves sound prefix and kind consistent. Nevertheless, 261–265 require missing-beat, outside-source, saved-cast, duplicate and kind-mismatch diagnostics. In-memory fixture capture confirmed these states. Construct each asserted violation without overwriting it, or remove the unsupported assertions.

5. **MEDIUM — Unmandated wording still rejects conforming implementations.** Examples include `test_scene_range_lo_gt_hi` (V:416: `"ovi_range"`), `test_two_characters_share_voice_key` (721: `"voice_key"`/`"shared"`), and `test_sound_kind_mismatch_prefix` (783: `"mismatch"`/`"prefix"`). The aggregate keyword list has the same problem. `test_brief_empty_person_name` (624) requires `"empty"`/`"missing"`, rejecting ordinary jsonschema wording such as “should be non-empty.” Apply the binding clarification throughout: mandated quoted phrases plus IDs; otherwise IDs only, with schema assertions checking the offending field.

6. **MEDIUM — Required independent cases remain contaminated.** `test_covered_by_invalid_reference` truncates script context (V:393); `test_voice_key_not_in_saved` and `test_voice_id_mismatch_saved` remove Krishna’s saved voice (684, 691); `test_chapter_ovi_not_in_any_scene` leaves ovi 6 untyped and undispositioned (427). Preserve baseline context and add ovi 6’s typing/disposition so each case isolates its intended rule.

7. **MEDIUM — Start-at-one and core-beat cases remain incorrect.** `test_shot_sequence_starts_at_one` (V:507) creates duplicate `S1-2` and a dangling brief reference. Use unique consecutive IDs starting at 2 and update references. `test_core_line_not_in_any_shot_beat` (550–554) still targets non-core `S1-L2`; add a distinct core-line case while retaining optional-line coverage.

8. **MEDIUM — Previously requested schema coverage is still absent.** S:367–420 and `test_required_field_missing` (434–512) omit accepted enum-value coverage, several invalid enums, invalid `covered_by`, missing discourse treatment, conditional MERGED reason isolation, missing `adhyay`, nested `need_new` required fields, and extra-key checks for turn/people/references/need_new. Add the independent cases requested in R2/Haiku.

9. **MEDIUM — Weak checks remain.** `test_message_prefixes` (V:882) passes with `errs=[]`, confirmed by an in-memory probe. Require expected diagnostics first. `test_schema_error_stops_early` (197) forbids only the adhyay mismatch, allowing other semantic diagnostics alongside schema errors; assert that every returned error belongs to schema validation.

Read-only inspection and in-memory probes only; no edits, secret access, web, or full-suite execution.