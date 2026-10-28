# GLM review: questions

## Verdict: FIX FIRST

All 14 pytest tests pass, but several spec rules have no isolated test, one test asserts message wording the spec does not quote, and `validate` can raise on odd `docs` (spec: "must still never raise on odd data").

## Spec rules

| rule | module implements it (yes/no, line) | isolated failing test exists (yes/no, test name) | notes |
|---|---|---|---|
| `SCHEMA["$schema"]` = "https://json-schema.org/draft/2020-12/schema" | yes, L11 | no | constant; a direct equality assert would cover it |
| `SCHEMA["title"]` = "stage1_questions" | yes, L12 | no | constant; same |
| top-level `type: object` | yes, L13 | no | no case feeds a non-object doc (minor, T6/T7) |
| top-level extra-key rule `additionalProperties: false` | yes, L14 | yes, test_schema_errors_format (`questions/extra` case) | ok |
| required top-level `adhyay` | yes, L15 | yes, test_schema_errors_required | ok; BASE carries `adhyay` and the semantic adhyay check presupposes it, so requiring it is correct |
| required top-level `questions` | yes, L15 | yes, test_schema_errors_required | ok |
| `adhyay` integer 1..21 | yes, L17 | no | missing row: no 0/22/non-integer case (T3) |
| `questions` is an array | yes, L19 | no | no non-array case (minor, T7) |
| item `type: object` | yes, L21 | no | no non-dict item case; the extra-key case does not isolate it (minor, T7) |
| item extra-key rule `additionalProperties: false` | yes, L22 | yes, test_schema_errors_format (`questions/0/extra` case) | ok |
| item required `id` | yes, L23 | yes, test_schema_errors_required | ok |
| item required `text` | yes, L23 | yes, test_schema_errors_required | ok |
| `id` pattern `^Q[0-9]+$` | yes, L25 | yes, test_schema_errors_format ("X1") | ok |
| `text` string 1..400 chars | yes, L26 | yes, test_schema_errors_format ("" and 401 chars) | ok |
| `scene_id` optional | yes (absent from required, L23) | no | missing row: no test deletes scene_id and expects no errors (T4) |
| `scene_id` pattern `^S[0-9]{1,2}$` | yes, L27 | yes, test_schema_errors_format ("X1") | ok |
| schema_errors: one message per error, "questions <path>: <message>", "/"-joined path, "doc" when empty | yes, L37-42 | no | tests only do `field in e`, which passes with any prefix/separator (T6) |
| BASE doc must yield `schema_errors(BASE) == []` | yes (BASE validates clean) | no | missing row; without it the `any(field in e)` asserts are not isolated (T2) |
| semantic: adhyay check first, message "questions adhyay <n> does not match <adhyay>" | yes, L48-51 | yes, test_validate_adhyay_mismatch | check itself isolated; "does not match" is the quoted phrase; first-position ordering untested (T8, minor) |
| semantic: question ids unique | yes, L57-65 | yes, test_validate_duplicate_id | ok; item-id-only assert, compliant |
| semantic: scene exists if given | yes, L67-82 | yes, test_validate_scene_missing | test asserts "scene" — wording not quoted in spec (T1) |
| API: missing docs key counts as empty | yes, L68 | no | missing row: no test deletes `docs["scenes"]` (T5) |
| API: validate never raises on odd data | no — L68-70 raises if `docs`/`docs["scenes"]` is not a dict or `scenes` is not a list | no | module defect M1 |
| API: notes come after error messages | n/a (unit emits no notes) | n/a | trivially satisfied |
| API: ctx lists may arrive as sets (convert with set()) | n/a (no rule of this unit reads ctx) | n/a | ok |

## Defects in the MODULE

1. `validate` violates "must still never raise on odd data" at L68-70: if `docs` is not a dict, or `docs["scenes"]` is not a dict (e.g. `None` or a list), `docs.get`/`scenes_doc.get` raises AttributeError; if `scenes_doc["scenes"]` is not a list (e.g. `None`), `for sc in ...` raises TypeError. Fix in `validate`: after `scenes_doc = docs.get("scenes", {})` add `if not isinstance(scenes_doc, dict): scenes_doc = {}`; replace `scenes_doc.get("scenes", [])` with a local `raw = scenes_doc.get("scenes", [])` plus `if not isinstance(raw, list): raw = []` and iterate `raw`. Optionally guard non-dict `doc`/`docs` at the top (`if not isinstance(doc, dict): return []`).
2. Minor cleanup: unused imports `json` (L3), `re` (L4) and `jsonschema` (L7) — only `Draft202012Validator` is used; remove all three.

## Defects in the TESTS

1. test_validate_scene_missing — asserts `any("Q1" in e and "scene" in e ...)`: "scene" is message wording not quoted in the spec; rule 11 ("scene exists if given") has no quoted phrase, so per the message convention the test may only check the item id. Change to `assert any("Q1" in e for e in errs)`.
2. Missing row — no test asserts the BASE questions doc is schema-valid, although the spec requires `schema_errors(BASE) == []`; without it every `any(field in e)` assertion in the two schema tests can be satisfied by an unrelated base-level error (e.g. a wrong `id` pattern on BASE makes the path fragment `questions/0/id` satisfy the "id" case). Add `test_schema_baseline_valid`: `assert schema_errors(base()["docs"]["questions"]) == []`.
3. Missing row — `adhyay` integer 1..21 has no schema case. Add to test_schema_errors_format: `(["docs", "questions", "adhyay"], 0, "adhyay")` and `(["docs", "questions", "adhyay"], 22, "adhyay")` (optionally a non-integer value).
4. Missing row — `scene_id` optional is untested. Add a test deleting `["docs", "questions", "questions", 0, "scene_id"]` and asserting `schema_errors(...) == []` and `validate(...) == []`.
5. Missing row — "a missing one counts as empty" is untested for `scenes`. Add a test deleting `["docs", "scenes"]` and asserting validate returns a message containing "Q1" (scene_id "S1" no longer resolves) without raising; optionally also a `docs["scenes"] = None` case to pin the never-raise rule (module defect M1).
6. Missing row — the schema_errors message format is untested (prefix "questions ", "/"-joined path, "doc" for the empty path). Add: `errs = schema_errors([])` and assert one message starting with `"questions doc: "`; for one mutated doc assert the path fragment (e.g. `"questions/0/id"`) appears.
7. Missing row (minor) — the `type` keywords are untested: add a non-array `questions` (e.g. `set_at(..., ["docs", "questions", "questions"], {})`) and a non-dict item (append a string to the questions array); the non-object doc case is covered by T6's `schema_errors([])`.
8. Missing row (minor) — "adhyay check first" ordering is untested. Add a case with both an adhyay mismatch and a duplicate id and assert `errs[0]` contains "does not match".

## Failing tests

None — 14/14 pass. The defects above are gaps the current suite cannot detect: the wording assertion in test_validate_scene_missing passes only because the module happens to emit "scene_id ... does not exist", and the missing rows mean the corresponding schema/semantic rules (adhyay range, scene_id optionality, missing-docs handling, message format, odd-data robustness) could be removed or broken without any test failing.
