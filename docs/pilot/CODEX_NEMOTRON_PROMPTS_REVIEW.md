What this change does: These prompts delegate pipeline modules to Nemotron. **Verdict: FIX FIRST for all eight prompts** before reuse or execution; several can produce code that passes its own tests while violating the pipeline contract.

I reviewed the requested prompts, runner, README, checklist, previous review, nine schemas, pipeline modules, and tests. No files were changed; no web or `secrets/` access occurred.

1. **High — `_system_prompt.txt:3` — FIX FIRST.**  
   The shared prompt omits the owner’s main restrictions and says “no Blender code,” which does not exclude other animation code. `nemotron_code.py:129` sends only `SYSTEM` and the spec text: referenced files and tests are **not automatically supplied**.

   Add to both the recorded prompt and actual `SYSTEM`:
   > “Never access secrets/. Never edit the owner’s EASY script or existing Adhyay 1 artifacts. Never generate animation implementation code. Kimi outputs contain no timings, dialogue or claims; Stage 2 selects existing catalog image IDs only. Stage 1 effort is HIGH; Stage 2 LOW. Tests use synthetic inputs and temporary files only. Follow narrower dependencies and I/O restrictions in the spec.”

   Each request must include the schema/API definitions it relies on. Clarify that “no writes” applies to the module; test fixture writes under `tmp_path` are permitted.

2. **Medium — `_landed_spec_chapter.md:5,41–51` — FIX FIRST.**  
   The prompt assigns A1’s catalog to `canon/adhyay_01/images/catalog.json`. Current code and tests correctly use `final_image_binding.json`. Rerunning the saved prompt would undo that correction.

   Replace with:
   > “For Adhyay 1, images_catalog equals image_binding, both pointing to final_image_binding.json.”

   Replace repository-file existence assertions with complete expected-path assertions using a synthetic root. The current existence test violates the synthetic-only requirement. Specify `root` and `flow_root` as `Path` inputs and assert every returned path, not selected examples.

3. **Medium — `_landed_spec_approvals.md:5,62` — FIX FIRST.**  
   Cycle behavior remains underspecified: the embedded test allows the changed item itself in the result, although current code/tests exclude it.

   Add:
   > “stale_dependents always excludes changed items; for a↔b and changed={a}, return exactly {b}.”

   Also define malformed approval handling:
   > “load rejects malformed records with ValueError; status never approves a missing or invalid recorded/current SHA-256.”

   Present `status({"x": {}}, "x", None)` evaluates as APPROVED by inspection. Add regression coverage. Approval authority is still missing: an arbitrary `owner` string is metadata, not proof of owner authorization; item 12 must define the authorized write path.

4. **High — `_landed_spec_caps2.md:7,14,17` — FIX FIRST.**  
   Three concrete holes remain:
   - A fresh nested spend directory fails when creating the lock, before the promised parent creation.
   - Replay accepts a second `open` event for the same ID, overwriting its reservation.
   - `unreconciled()` implements separate replay and can accept malformed transitions rejected by `state()`.

   Add:
   > “Create the spend parent before lock acquisition. Remove only a lock acquired by this invocation. Reject duplicate open IDs and illegal transitions. Every reader uses the same validated replay helper.”

   Require tests for those cases, malformed/truncated records, process interruption, and lock recovery. State explicitly that a crashed lock requires verified operator recovery, never automatic deletion. Include the actual fixed tests: “see the tests described by the API” supplies no independent test oracle.

5. **High — `validate_stage1.md:8–20` — FIX FIRST.**  
   One failing case per **numbered paragraph** leaves most individual rules untested. Duplicate line IDs within one scene and reordered script lines can pass. The API cannot verify person/place/prop canon or substantive claims; forbidding a `claims` key does not validate prose in `goal`, `turn.text`, or `pose`.

   Add:
   > “Test every individual rule independently. Scene line IDs are unique within and across scenes and preserve script_line_ids order. Every core line appears in shot beat_line_ids.”

   Supply approved entity IDs and a defined source-evidence contract before claiming canon/claim validation. Otherwise explicitly mark those checks deferred and retain an approval block. Define whether scenes without shots are invalid. Add forbidden-key tests for all five documents and nested records. Define document/path prefixes where no item ID exists, stable error ordering, and behavior for missing foreign keys without exceptions.

6. **High — `validate_beats_catalog.md:5–18` — FIX FIRST.**  
   This combines four validators and a helper but leaves several acceptance holes:
   - Empty beats pass; missing required speech is unchecked; uniqueness is only per scene.
   - Recorded durations/voices are not compared with measured clips.
   - `fingerprints.images={}` can omit referenced assets and still satisfy the requested freshness comparison.
   - Source/renderer fingerprints and raw/clean image provenance remain absent from schemas.
   - Missing/unreadable files can raise despite “never raises for bad data.”

   Add:
   > “Validate shot_plan schema first. Fingerprint image keys equal the assets referenced by its shots. Compare source and renderer fingerprints as well as script, timing, presets and images.”

   Add required/selected line IDs and measured-clip inputs; require complete coverage, global uniqueness, scene ownership, and matching measurements/voices. Define scene-local versus global time, finite numeric arguments, positive `shot_seconds`, and nonnegative tolerance. Require live-file read failures as errors and resolved paths confined to `image_dir`.

   Update schemas for the checklist’s provenance fields. State that `fingerprint_images` returns a dict and raises the documented `KeyError`; it cannot satisfy “each function returns errors/never raises.”

7. **High — `check_script.md:20–29` — FIX FIRST.**  
   “Other lines ignored” conflicts with detecting malformed headers: a parser may silently discard a broken core line. Duplicate language bullets can silently overwrite text. U+0900–U+097F includes digits and marks, so it does not mean “letter.”

   Add:
   > “Any line beginning a script-header marker is a header candidate; malformed candidates produce bad_header records with source line numbers. Require exactly one Marathi and one Hindi bullet before the next header. Missing headings and duplicate bullets are errors.”

   Require a Unicode letter within the Devanagari block, define glossary substring versus word matching, and specify exact error strings, ordering, and warning behavior. Add scene-order, invalid-priority, duplicate-bullet, digits-only, empty-script, and known SHA-256 tests. Hashing must preserve the input text without normalization.

8. **High — `gates.md:10–16` — FIX FIRST.**  
   `pipeline_state` detects stale ancestors, but `require_approved` and `ready_stages` receive no dependency graph. Thus an unchanged approved `jobs` item can pass while upstream `script` is stale. Cycle wording also contradicts DRAFT/STALE precedence.

   Replace with:
   > “require_approved and ready_stages receive deps and use pipeline_state. Preserve each item’s DRAFT/STALE status; only locally APPROVED items become BLOCKED through dependencies, including cycles.”

   Define all-approved cycles, missing-hash precedence, and BLOCKED reasons. Test stale-ancestor refusal through **both public gate functions**, plus self-cycles and mixed-status cycles.

Missing specs against the current master checklist:

- **10, partial:** Complete provenance, measured-input, canon/source-evidence, and replay validation beyond these drafts.
- **11:** Define every producer/consumer file’s schema, validator, command, and input fingerprint.
- **12, partial:** Authorize owner approval writes and wire dependency-aware gates into every stage.
- **13:** Wire `--adhyay` into existing commands with A1 baseline equality and A2 data-only operation.
- **14:** Integrate chapter/stage reservations with the locked paid-call ledger and interrupted-call reconciliation.
- **17, partial:** Validate source receipts, explicit unfilmed ovis, and chapter-state changes beyond EASY formatting.
- **21:** Load versioned character/place/prop/voice/glossary/style data without embedded A1 names.
- **24:** Produce shared beats, pauses, crossings, and tails from both measured languages.
- **25:** Build approved image jobs with chip/place checks and synthetic structural fixtures.
- **26:** Record and verify chosen-version Flow provenance, dimensions, and raw/clean hashes.
- **28, partial:** Build compact Stage 2 LOW requests with catalog/role/hash validation.
- **29, partial:** Save and replay approved plans using complete exact fingerprints, with zero Kimi calls.
- **30:** Validate bounded preset-03 JSON and route the three NEED_NEW classes without generating animation code.

Nemotron writing code **and tests is not acceptable as the sole acceptance mechanism**, and changes README’s tests-first workflow. It can draft supplemental tests if that workflow change is approved. The extra safeguard is independently authored, frozen acceptance tests, including adversarial cases that fail deliberately broken implementations, followed by Claude’s full review and Codex’s read-only review.

Execution was not verified: the local Python launcher failed with permission denied. No test-pass, GPU, LTX, recovery, or A1-preservation claim is established.