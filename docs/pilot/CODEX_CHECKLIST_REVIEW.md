# CODEX_CHECKLIST_REVIEW.md — read-only review

## 1. Summary

The build checklist is **incomplete**. Review verdict: **NOT PASS**.
Phase 1 created `nemotron_code.py`, `chapter.py`, `approvals.py`, `caps.py`, nine schemas and their tests; these are standalone pieces.
The checklist marks chapter caps and stale approval handling done, but neither is connected to the running pipeline.
The latest owner rules are recorded, yet older plan and proof rows still contradict them.
Adhyay 1 preservation, full-stage tests, the two finished videos and the Adhyay 2 zero-code-change proof remain open.

## 2. Missing checklist items and contract holes

- **All stages — `PIPELINE_README.md:20-30`:** The table names files but does not assign a schema and validator to each file, define its input fingerprint, or say which command writes and consumes it. `CHECKLIST_BUILD_PIPELINE.md` covers nine schemas, not the complete file chain. Add the source, research, EASY script, bible, audio clips, image jobs, sound palette, sound files, subtitles, mixes, render receipts and delivery receipts to the contract.
- **Source, script and canon — README stages 0/S/2:** Specify source citation and hash format, research packet checks, explicit unfilmed ovis, core/optional line selection, scene-to-line coverage, chapter-state changes and the owner’s approval record. The EASY checker must *report* issues without changing the owner’s words. The checklist lacks a distinct A1 approval of rev9, optional lines and the 16 look questions.
- **Audio and sound — README stages 1/3/7:** Define voice and clip schemas, exact reuse key, credit reservation and interrupted-call recovery. Define the reusable ElevenLabs effect pack: palette IDs, hashed files, model/settings, rights note, credit receipts, new-sound approval, cue timing and checks against both speech windows. Hindi must remain labelled `NOT_VALIDATED` while measured and used.
- **Timing, images and delivery — README stages 4/5/7/8:** `beats.json` needs pauses, shot crossings and scene tails. Image jobs and catalog need raw *and* clean hashes, actual version-specific prompt/model/chips/edit ID, dimensions and an explicit chosen version. Define per-chapter watermark data. Specify subtitles, both language mixes, exact picture and duration equality, complete speech, shot-level render resume, failed-child recovery and output hashes.
- **Paid calls and approvals — `CHECKLIST_BUILD_PIPELINE.md:10-14`:** Add integration of `caps.py` with `kimi_adapter.py` and its locked ledger, including worst-case reservation, settlement, UNKNOWN reconciliation and stage/chapter attribution. Define when `caps.py.record()` is called; a post-call spend row alone cannot guard a call. Wire `approvals.py` into each stage and downstream hash invalidation. The provisional $5/$1/$3/$1 allocation does not replace the active P4 cap without the owner’s decision.
- **A1 preservation and closeout — `FINAL_ARCHITECTURE_PLAN.md` B6/B7/B18:** The proposed data migration conflicts operationally with “do not disturb A1” until a byte-for-byte baseline and rollback copy exist. Add old-versus-new A1 output comparisons, an inventory and backup receipt for ignored media, housekeeping by explicit selection, the full test/validate evidence and a reviewed commit. Record local render/GPU measurements if claiming resource suitability. There is no demonstrated LTX checkpoint hash, family or node-version compatibility; make no LTX success claim.
- **Prompt proof — `CHECKLIST_BUILD_PIPELINE.md` phases 2–3:** Add a prompt fixture for every input/output contract and forbidden field, free A1-data comparison with recorded scores, and an owner gate before any new paid Kimi call. A1 Stage 1 must not run again.

## 3. Wrong or conflicting text

1. `FINAL_ARCHITECTURE_PLAN.md:8,14,49,63` assigns EASY drafting or wording approval to Kimi. Sections 8/10, `PIPELINE_README.md:7` and `docs/DECISIONS.md:94-100` supersede this: the owner supplies the confirmed script; Kimi never writes, edits or flags its lines.
2. `FINAL_ARCHITECTURE_PLAN.md:10,21,30,57,63` and `CHECKLIST_PROOF_SCENE_S4.md:34` make one selectable-track master the goal. The later owner rule requires **two videos**, Marathi and Hindi, with identical picture and length; a multi-track master is optional.
3. `CODEX_KIMI_WORK_PLAN.md:20,31` proposes low effort or a low/high test for Stage 1. The owner chose **HIGH** for Stage 1 and **LOW** for Stage 2. A Stage 2 HIGH retry or paid comparison needs a separate owner decision; it is not a prerequisite.
4. `FINAL_ARCHITECTURE_PLAN.md:3,36-37,41,63`, `PIPELINE_README.md:3` and `CHECKLIST_BUILD_PIPELINE.md:4,10-13,42` mix historical proposals with current status. Flow agents and `opencv-python` were approved; Phase 1 files now exist; cap *integration* is unfinished although item 1.4 is ticked.
5. Older 61-shot/Parler directions are superseded by the measured ElevenLabs **59-shot** rev9 plan (`DECISION_LOG.md:56-58`). `CLAUDE.md:3` still calls Claude the only code writer; `PIPELINE_README.md:56` and `docs/DECISIONS.md:96` record Nemotron drafting the next harness code, with Claude verifying and landing it. Reconcile the instruction before further code work.
6. `CODEX_FULL_ARCHITECTURE.md` and older S4 notes describe `VALID` or Nemotron `PASS`; neither means image binding, render fit or owner approval. The old S4 plan’s layered choices cannot be treated as approved for flat finals.

## 4. Phase 1 code review

1. **High — `scripts/source/nemotron_code.py:80-99`.** `--spec` can point at any readable file and `--out` at any new directory, including a repository folder. Repro: pass a sensitive file as `--spec`, or a new folder under the repo as `--out`; the claimed “never sees `secrets/`” and “scratch only” rules are not enforced. Validate both resolved paths against explicit allowed roots *before* loading keys or calling the model.
2. **High — `scripts/pipeline/caps.py:53-111`.** `check()` does not reserve, and `record()` appends after the fact without a lock, unique request ID check or UNKNOWN state. Two callers can both pass against the same balance; interruption can leave no charge recorded. Connect chapter/stage checks to the locked reservation lifecycle in `v5_ledger.py`, then test concurrent and interrupted calls. `kimi_adapter.py:54-68` currently uses only P4.
3. **High — `scripts/pipeline/approvals.py:29-82`.** Any caller can supply an arbitrary `owner` string and replace an existing approval. `status()` compares one supplied hash; no stage calls it or invalidates dependent approvals. A changed upstream file can therefore leave a downstream approval apparently usable. Define the approval authority and wire input fingerprints into stage gates.
4. **Medium — `scripts/pipeline/chapter.py:6-55`.** This resolver is not connected to existing commands, so the `--adhyay N` and zero-code-change claims are premature. For A1, `images_catalog` points to `canon/adhyay_01/images/catalog.json`, which does not exist; the test checks other paths but misses this one (`tests/test_pipeline_chapter.py:32-42`). Correct the mapping and compare actual A1 outputs byte for byte before migration.
5. **Medium — `scripts/pipeline/make_schemas.py:30-51`.** Structural schemas permit duplicate or missing ovis, unknown line IDs, unsupported claims and invalid foreign keys. `beats` can accept an end before its start; `image_catalog` permits arbitrary image keys and lacks raw/clean provenance; animation assets have no preset-role or live-hash check. `shot_plan` omits source and renderer fingerprints. Add semantic validators and failing fixtures before treating a schema pass as a gate.
6. **Medium — `scripts/pipeline/approvals.py:85-110`.** `stale_dependents()` says changed items are excluded, but a dependency cycle returns the starting item. Repro: `{"a":["b"],"b":["a"]}`, changed `{"a"}` returns `a` as well. Remove changed items from the result and test that contract.
7. **Medium — `scripts/source/nemotron_code.py:24-52,94-104`.** The file-block parser silently ignores malformed blocks and writes accepted blocks even when others were refused. The text search catches literal Blender words, not all animation code. Require an exact expected file list from the spec, reject a partial reply, and have Claude inspect the full draft as the owner rule requires.

`CHECKLIST_BUILD_PIPELINE.md:42` reports “22 + 28 pass,” but supplies no captured command output or test environment. I did not run tests in this read-only review. The new Phase 1 files are untracked, so a `BASE...CANDIDATE` diff cannot yet prove their scope. The worktree also contains modifications to A1 files; the new standalone modules do not themselves prove A1 behavior stayed identical.

## 5. Corrected master checklist

“Done” below means the named artifact exists or the owner decision is recorded, **not** that the whole pipeline gate passes. Owner? identifies a decision or acceptance gate.

| # | Item and file(s) | Who | Owner? | Done-test | Status |
|---:|---|---|---|---|---|
| **Decisions and baseline** ||||||
| 1 | Record current rules — `DECISION_LOG.md`, `docs/DECISIONS.md` | Owner/Claude | Yes | Latest answers recorded | done |
| 2 | Reconcile superseded instructions — `FINAL_ARCHITECTURE_PLAN.md`, `CLAUDE.md`, S4 checklist | Claude | No | One current rule per topic | to build |
| 3 | Inventory, hash and back up A1 data/media; capture baseline outputs | Claude | Yes for disposal | Recovery copy and comparison list | to build |
| 4 | Verify rights route for Flow cleanup and ElevenLabs effects; retain rights notes | Owner/Claude | Yes | Recorded permitted-use basis | to build |
| **Phase 1 contracts** ||||||
| 5 | Nemotron scratch draft tool — `scripts/source/nemotron_code.py` | Nemotron/Claude | No | File and tests exist; fix review findings | done |
| 6 | Chapter path module — `scripts/pipeline/chapter.py` | Nemotron/Claude | No | File and tests exist | done |
| 7 | Approval/hash module — `scripts/pipeline/approvals.py` | Nemotron/Claude | No | File and tests exist | done |
| 8 | Cap/spend module — `scripts/pipeline/caps.py` | Nemotron/Claude | No | File and tests exist | done |
| 9 | Nine JSON schemas — `scripts/pipeline/make_schemas.py`, `schemas/*.schema.json` | Claude | No | Nine files validate structurally | done |
| 10 | Phase 1 tests — `tests/test_nemotron_code.py`, `tests/test_pipeline_*.py` | Claude | No | Capture reproducible run output | done |
| 11 | Repair findings 1–7; add semantic and malformed-input fixtures | Nemotron/Claude; Codex reviews | No | Each repro fails before and passes after | to build |
| 12 | Define every stage file, validator, receipt and dependency — `PIPELINE_README.md` | Claude | Yes for contract | Complete producer/consumer matrix | to build |
| 13 | Wire `--adhyay N` and series data into existing commands; preserve A1 | Nemotron/Claude | No | A1 byte-identical; A2 uses data paths | to build |
| 14 | Wire approval gates and stale propagation into stages | Nemotron/Claude | Yes at each gate | Changed input blocks downstream use | to build |
| 15 | Integrate chapter/stage caps into `kimi_adapter.py`/`v5_ledger.py` | Nemotron/Claude | Yes for cap change | Reserve, UNKNOWN, reconcile, concurrency tests | to build |
| **Source, planning and assets** ||||||
| 16 | Lock A1 rev9, EASY script, optional lines, look questions and hashes | Owner/Claude | Yes | Exact approval receipt | to build |
| 17 | Lock A2 printed-book source and owner EASY script | Owner/Claude | Yes | Source and script hashes approved | to build |
| 18 | Build source/EASY checker and canon-state registry | Nemotron/Claude | Yes for meaning | Coverage, speaker, glossary and state fixtures | to build |
| 19 | Build Stage 1 HIGH prompt, five outputs and semantic validator | Nemotron/Claude | Yes for contract | All forbidden/missing/claim fixtures fail | to build |
| 20 | Test Stage 1 free on A1 data; do **not** repeat A1 paid Stage 1 | NVIDIA/Claude | Yes for comparison | Scores against rev9/59 jobs recorded | to build |
| 21 | Run only needed A2 Stage 1 groups after cap gate | Kimi/Claude | Yes | One-call receipts; owner approves batch | to build |
| 22 | Build versioned series character/place/prop/voice/style data | Nemotron/Claude | Yes for canon | No A1 names embedded in code | to build |
| 23 | Build sound palette and reusable ElevenLabs effect pack | Claude/ElevenLabs | Yes | Hashed WAVs, cues, credits, rights | to build |
| 24 | Accept/reuse per-line MR/HI voice clips and measure them | Claude/ElevenLabs | Yes | Exact reuse keys; listening and credit receipts | to build |
| 25 | Compute shared beats, pauses, crossings and tails | Nemotron/Claude | Yes for timing | Complete speech in both languages | to build |
| 26 | Build image prompts/jobs from approved data — `IMAGE_PROMPT_RULES.md` | Nemotron/Claude | Yes for briefs | 59 A1 structure checks; chip/place failures | to build |
| 27 | Repair version-specific Flow provenance and catalog binding | Claude/Flow agents | Yes for selection | Actual prompt/model/edit ID and live hashes | to build |
| 28 | Review first three per scene, full set and contact sheet | Flow agents/Claude | Yes | Rubric, exceptions and chosen versions | to build |
| 29 | Make watermark settings chapter data; clean and inspect corners | Claude | Yes for exceptions | Mask-only changes; A2 calibration | to build |
| **Animation and proof** ||||||
| 30 | Build compact Stage 2 LOW prompt and catalog/role validator | Nemotron/Claude | Yes for scene | Unknown ID, role, hash, timing fail | to build |
| 31 | Save shot plans and exact-hash replay | Nemotron/Claude | Yes for new plans | Same inputs use zero Kimi calls | to build |
| 32 | Define bounded preset-03 JSON and three `NEED_NEW` classes | Nemotron/Claude | Yes for each new version | Bounds and full-frame render pass | to build |
| 33 | Bind and approve S4 flat finals; decide staging warnings | Claude/Owner | Yes | Five live files/roles/hashes accepted | to build |
| 34 | Test presets 05/06/07 and one real `NEED_NEW` | Claude/Kimi if needed | Yes | Full frames and owner viewing | to build |
| 35 | Render/mix/subtitle S4; test interrupted shot resume | Claude | Yes | Clean-run equality; complete bilingual speech | to build |
| 36 | Render/mix remaining A1; capture render/GPU receipts | Claude | Yes | Owner accepts full film | to build |
| **Delivery and freeze** ||||||
| 37 | Export Marathi and Hindi MP4s from one picture timeline | Claude | Yes | Same frames/length; audio/subtitle inspection | to build |
| 38 | Run A2 through one rendered scene with data-only changes | Claude | Yes | No `scripts/` or `src/` diff | to build |
| 39 | Run full tests and `granthstudio validate`; review and commit runbook | Claude; Codex reviews | Yes for release | Captured results, recovery drill, reviewed commit | to build |

## 6. Top five open risks

1. A paid call can bypass the proposed chapter/stage cap because the new module is not integrated with the locked ledger.
2. A `VALID` S4 plan can select image roles or layered presets the approved flat files cannot render.
3. A1 migration or hard-coded-data extraction can silently change the existing 59-shot result without a baseline comparison.
4. Missing version-specific Flow provenance and unverified cleanup rights can undermine final-image approval.
5. Unfinished timing, sound, resume and export gates can yield two videos with different pictures, lengths or incomplete speech.