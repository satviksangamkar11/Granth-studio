## 1. SUMMARY

The 67-row checklist is substantially improved, but it is not complete or internally consistent.
Most owner rules now have rows, including nine Stage 1 outputs, automatic cleanup, sound reuse and voice casting.
Several completion claims exceed the evidence, particularly item 11 and the “FIXED” drafting-tool findings.
Missing acceptance checks cover review enforcement, voice-library refresh and promotion of approved looks into series data.
**Verdict: FIX FIRST.** Unfinished implementation alone is expected; inaccurate status and conflicting instructions need correction now.

## 2. STATUS CHECK

Reviewed the working tree on `pipeline/stage1-architecture-2026-10-28`, alongside commit `f3abc29` and its parent. No BASE/CANDIDATE pair was supplied.

**Supported by files, subject to execution evidence:**

- Items 6–9: `scripts/pipeline/chapter.py`, `approvals.py`, `caps.py`, nine JSON schemas and their tests exist. The A1 catalog mapping now uses `canon/packets/adhyay_01/final_image_binding.json`; cycle handling excludes changed items.
- S1 and E1: `docs/pilot/STAGE1_RULES.md`, `PIPELINE_README.md`, `docs/DECISIONS.md` and `docs/pilot/DECISION_LOG.md` contain the relevant rules.
- V1: `canon/series/voices.json` contains 35 voices, four ASSIGNED, 35 nonempty descriptions and nine flagged as verified Marathi/Hindi. The four saved cast IDs and five named female voices are present.
- Items 10, 12, 17, S2/S3 and V2 correctly acknowledge partial implementation.

**Unsupported or overstated claims:**

1. **High — item 5 and “FIXED” findings, `scripts/source/nemotron_code.py:57,69,83`.**  
   `check_spec()` accepts any small `.md`/`.txt` outside prohibited folders; it has no explicit approved spec root. Supplying the repository as `--allow-root` permits a new output folder under `scripts/`. Also, an expected valid block followed by an unfinished unexpected block can pass `exact_set()`, because parsing ignores the unfinished block.  
   **Correction:** finish the promised path restrictions and malformed-response rejection; add regression tests before calling these findings fixed.

2. **Medium — item 11, `docs/pilot/CHECKLIST_BUILD_PIPELINE.md:18`; `docs/pilot/PIPELINE_README.md:65`.**  
   The matrix omits four Stage 1 outputs, bible, sound palette/files, subtitles, mixes and render/delivery receipts. It supplies no complete command or schema mapping.  
   **Correction:** mark partial and finish the fields already required by item 11.

3. **High — V1 refresh behavior, `scripts/pipeline/voice_library.py:150,195,260,267`.**  
   Refresh rebuilds from the A1 cast, clears owner notes and gives other voices empty assignments and AVAILABLE status. After V3 saves a new recurring character, `--overwrite` can lose that assignment. Edited descriptions are also replaced.  
   **Correction:** preserve existing series assignments and owner edits when refreshing; test refresh after a later-chapter assignment.

4. **Medium — S2/S3 evidence, `scripts/pipeline/validate_stage1.py:24`.**  
   Nine unit modules exist, but the current aggregator still validates five documents using old schemas. `schemas/stage1_shots.schema.json` still requires `preset_hint`; newer `shots.py` requires `preset` and `need_new`. New sound units use `sound_id`; the old schema uses `palette_id`.  
   **Correction:** keep partial; require one integrated nine-document contract before completion.

5. **High — semantic acceptance remains incomplete.**  
   `scripts/pipeline/stage1/coverage.py:75` accepts an extra foreign ovi when all chapter ovis are present. `looks.py:29,97` permits event/dialogue prose inside `look`; it checks citations and known states, not the visual-only promise. `sounds.py` checks membership in an ID set without checking availability/version. V2 accurately leaves recurring-voice enforcement open.  
   **Correction:** add these cases to items 10/S3/21b/E2; do not equate structural validity with source fidelity.

6. **Medium — test evidence needs repair and capture.**  
   `tests/test_stage1_looks.py:136` changes only `entity_id`, leaving different state IDs, yet expects a duplicate entity/state error. `tests/test_stage1_coverage.py` expects schema rejection of `"bad-id"`, although `covered_by` permits any string. Its integer-reference semantic test also conflicts with that string-only schema.  
   **Correction:** fix fixtures and settle the contract before freezing tests.

7. **Medium — progress log, `docs/pilot/CHECKLIST_BUILD_PIPELINE.md:105`.**  
   “All work committed” is false for the current tree: checklist, code, tests and specs have uncommitted changes. The branch and WIP commit exist; no remote is configured.  
   **Correction:** distinguish the committed checkpoint from later changes.

The reported 120 passes, V1’s 24 passes and “5/9 units pass” were **not independently reproduced**. No completed test execution resulted in this review; many tests create temporary files, so I did not run the full suite under “edit nothing.” The counts are reported history, not fresh acceptance evidence. Current cap tests contain nine test functions, making “7 pass” stale.

External media, backup recovery, live account state, rights, GPU measurements, LTX pins/node compatibility and final bilingual exports were not verified.

## 3. MISSING ITEMS

Add these concrete sub-items; expand existing rows where possible:

- **Both independent reviews throughout development.**  
  File: `docs/pilot/CHECKLIST_BUILD_PIPELINE.md`, linked review records. Who: Claude records; Codex MEDIUM and Haiku LOW review read-only; Nemotron fixes. Owner decision: already settled. Done-test: every spec, frozen test set and code version has both reviews tied to hashes, with findings resolved. Item 39 names only Codex; the progress log is not a completion gate.

- **Safe voice-library refresh.**  
  Files: `scripts/pipeline/voice_library.py`, `tests/test_voice_library.py`. Who: Nemotron. Owner decision: no new policy decision. Done-test: refresh preserves later assignments, stable keys, descriptions and owner notes; missing voices cannot silently become selectable.

- **Approved looks become persistent series data.**  
  Files: `canon/series/`, the Stage 2 canon writer and its tests. Who: Nemotron; Claude specifies. Owner decision: image/sheet acceptance. Done-test: an unapproved look cannot become canon; an accepted look is saved once and reused next chapter; changed source/state invalidates dependent assets.

Everything else listed in the request has at least a broad checklist home. Several homes need stronger done-tests rather than additional rows.

## 4. DUPLICATES / CONFLICTS

- **Caps:** item 14 drops integration, but item 20 still requires a “cap gate”; the open-findings paragraph still points integration to dropped item 14. `PIPELINE_README.md` section 2b still lists caps integration as unfinished work. Replace these with the unchanged existing ledger and owner spending gate.
- **Automatic cleanup:** item 26b conflicts with item 27’s “per-chapter watermark data” and README stage 5. Retain automatic detection plus corner review; remove owner calibration requirements.
- **Code authorship:** rows naming Claude or “Nemotron+Claude” for implementation need explicit separation of specification, execution and authorship. Historical Claude edits may remain documented. Future code/tests belong to Nemotron.
- **Old lists:** README section 7 says old lists “stay valid,” while `FINAL_ARCHITECTURE_PLAN.md` still contains caps, EASY drafting, one-master delivery and Claude coding assignments. Its banner predates the October 28 rules. Mark old checkboxes historical and point execution solely to the master.
- **S4 proof:** `CHECKLIST_PROOF_SCENE_S4.md` retains a full-scene director flow and layered draft choices. `CHECKLIST_REUSE_SHOT_PLANS.md` correctly requires rebinding flat finals and reuse first. Preserve the completed paid call as evidence; do not repeat it to satisfy obsolete rows.
- **Duplicates:** 18/S4; 21c/S2/S3; 21a/V2/V3; 22/E2/E6; 24/E4; S9/E5. Use parent rows with linked sub-items and one completion record.
- **Optional work:** “never skip” conflicts with optional E8. Label it outside required completion.

## 5. ORDER / DEPENDENCIES

A1 baseline precedes migration. Contracts and approved fixtures precede prompts. Current preset/sound/voice data precedes prompt testing. Approval wiring precedes production use. Measured bilingual clips precede timing and ducking. S4 acceptance precedes the remaining film. The A2 freeze proof follows A1 completion.

**Next ten work packages:**

1. Reconcile current rules/status: items 1–2 and the conflicts above.
2. Capture A1 inventory, hashes and recovery copy: item 3.
3. Complete the producer/consumer contract: item 11.
4. Resolve A1 coverage and obtain the required locks: S5 and item 15.
5. Repair and independently review unit tests/code: S2/S3, V2, item 10.
6. Consolidate nine-output schemas and aggregator.
7. Finish approval authority and stage wiring: item 12.
8. Publish versioned preset/sound/voice context: S6, E2, V3.
9. Build chapter-aware wiring, zero-story support and prompts: 13, S7, 18/S4.
10. Run free A1 comparisons and capture scores: item 19; update S8 before image execution.

Strengthen item 37: compare the frozen commit against **all code-bearing paths**, tests, schema definitions and dependency configuration. Checking only `scripts/` and `src/` does not prove zero code change.

I1–I3 remain ON HOLD. Obtain A2 inputs through the existing supported route when the owner supplies them.

## 6. WHAT CAN BE DROPPED

- Drop new cap integration from required work; retain the existing module without expanding it.
- Move E8 to optional future experiments.
- Do not generate unused sounds merely to fill a pack.
- Retire duplicate active checklists and avoid separate acceptance records for the same work.
- Do not add D-019 machinery, template matching or renderer redesign.

**Verdict: FIX FIRST**

1. Correct item 11, the committed-work claim and unsupported “FIXED” wording.
2. Remove cap, calibration, authorship and obsolete-S4 contradictions.
3. Add the three missing acceptance sub-items.
4. Repair tests and integrate one nine-output contract with the identified negative cases.
5. Capture reproducible test/review evidence tied to the reviewed files.
6. Preserve A1, then complete gates, bilingual recovery/delivery and the strengthened A2 freeze proof.

No files were changed, no `secrets/` directory was opened, and no web or paid calls were made. `docs/pilot/CODEX_CHECKLIST_REVIEW2.md` was **not saved** because this task explicitly requires read-only operation.