# Haiku (low effort, read-only) review of the nine unit test files, 2026-10-28 (verbatim findings; every unit FIX FIRST)

## story_map
(1) Lines 137 and 139 use "ovi_types.9", but the base list has indices 0-8. mutate() then raises IndexError. (4) Line 139 asserts "outside" and line 141 asserts "ovi_range"; the spec quotes neither. Line 143 asserts "outside" for key_ovis, also not quoted. Fix: use "ovi_types.8" for both rows (or append); drop the unquoted wording.

## coverage
(2) Line 148 ("ovis/0/disposition", "VISUALISED", "ovi 1 twice") is a no-op on the valid base, so the "twice" rule has no working test. Fix: append a second entry for ovi 1. (4) Line 172 asserts "line is not in the script" and line 181 asserts "ovi not in chapter"; neither is quoted in the spec. (2) Lines 178 and 185 pass covered_by as strings ("99", "3"), but the spec types an ovi as an integer. Use integers, or clarify the spec.

## scenes
(1) Lines 70 and 98 target "scenes/0" (a list index). mutate() does cur["0"] on a list, which raises TypeError. (3) No test shows that a story scene carrying teaching_treatment is rejected; the comment at line 102 leaves it untested. (5) No required-field deletion rows for adhyay, scenes, scene_id, section_kind, ovi_range, goal, turn, line_ids, turn.ovi or turn.text; no root extra-key row.

## shots
(2) Line 206 ("S1-1" on shot 0) changes nothing, so the duplicate-shot_id rule never fails. (1) Lines 125, 135 and 169 expect "shots shots/0/<field>" or "shots adhyay" in messages. jsonschema reports required and additionalProperties errors at the parent path ("shots doc" or "shots shots/0"), so these assertions fail on a correct implementation. (4) Line 213 asserts "unique"/"consecutive", line 219 "scene", line 231 "beat_line", line 270 "not in the script"; none are quoted, and line 270 is not a shots rule. (5) No root extra-key row and no need_new nested extra-key row.

## briefs
(4) Line 214 asserts "unique" and line 217 "prefix"; neither is quoted in the spec. (5) Lines 190-192 replace whole objects with {"extra": 1} instead of adding a key, so they do not isolate the extra-key rule. No deletion rows for root "images" or "adhyay". (3) The "image ids unique" rule has no isolated failing row (the duplicate case in the table is valid input).

## looks
(2) Line 110 changes entries[1].state_id but leaves entity_id "bankatlal", so no entity+state duplicate exists. Fix: set entries[1].entity_id = "gajanan_maharaj" with state adult_youth_v2. (4) Line 108 asserts "source_ovis"; "duplicate" on line 110 is not quoted.

## voices
(1) Line 129 path "docs.ctx.speaking_characters" raises KeyError, because ctx is b["ctx"], not b["docs"]["ctx"]. (2) Lines 124 and 128 have identical input with contradictory expectations (error vs none). The spec allows narrator to share a voice_key, so drop the error expectation on line 124. (4) Line 120 asserts "duplicate RECURRING character", which is not quoted.

## sounds
(2) Line 119 expects NEED_NEW without sound_prompt to be valid; the spec makes sound_prompt required there. Expect "sound_prompt" instead. (2) Line 150 sets an fx sound on a bed kind, so validate() reports a kind mismatch but the row expects none. Set kind to fx as well. (2) Line 151 ("cues.0.kind", "bed") is a no-op on the base, so the kind-mismatch assertion can never pass. Set the kind to fx on a bed sound instead. (3) The NEED_NEW-needs-sound_prompt rule has no working failing row. (4) Line 154 is labelled "valid with prompt", but a non-NEED_NEW cue with sound_prompt is schema-forbidden.

## questions
(1) Line 104 ("docs.questions.questions.1") indexes a one-item list, so mutate() raises IndexError. (3) The ids-unique rule has no working test. Fix: append a second Q1 entry. (4) "unique" on line 104 is not quoted in the spec. Weak substring checks: line 86 matches "id" against any message.
