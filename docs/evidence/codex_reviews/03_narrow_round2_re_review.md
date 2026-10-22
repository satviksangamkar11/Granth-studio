# Codex review 3 — narrow round-2 re-review (FAIL, merge after specific fixes)

- **Origin:** verbatim output of `codex exec --sandbox read-only` (codex-cli 0.163.0) run from this session by Claude Code on 2026-10-22.
- **Reviewed range:** 46f1ab2..97f34ea
- **Prompt:** the 'NARROW ROUND-2 RE-REVIEW' brief (not stored in the repository)
- **Integrity:** the text below is unedited; Claude did not re-run or rewrite it.

---

**FAIL — MERGE AFTER SPECIFIC FIXES.** Four defects are fixed; two remain partial. Three concrete gaps remain within the requested scope.

**Repository and evidence checks**

- HEAD: `97f34ea71611235764e5f4fb61495092ca159c68`, branch `sprint/remaining-pipeline`; working tree clean.
- BASE `46f1ab2` and code commit `6b0b999` are ancestors of CANDIDATE.
- Changes after `6b0b999` are limited to the two benchmark evidence files and `docs/PROGRESS.md`.
- JUnit SHA-256 matches the receipt: `68477d2ca6cbcee74080678dc5ba6d0d7fd05a5d675242ef617eaeb9e8f31dfa`.
- Frozen architecture SHA-256 also matches the receipt.
- Reviewed `46f1ab2...97f34ea`; `git diff --check` passed.

**Six-defect matrix**

1. **F7 cleanup — FIXED, by inspection.** [integrity.py:141](</D:/aai work/granthstudio/src/granthstudio/integrity.py:141>) uses descriptor-relative creation, `fstat` link-count validation, and cleanup through the pinned parent `dir_fd`. POSIX no longer performs the dangerous pathname-based post-resolve unlink. Windows ancestor pinning and cleanup routing remain; shared validation now uses `fstat`. POSIX execution remains unconfirmed.

2. **F2 freshness — PARTIAL.** [comfy.py:170](</D:/aai work/granthstudio/src/granthstudio/comfy.py:170>) excludes output-node fields when upstream nodes exist. Its output-only fallback restores those fields and seed inputs, leaving the bypass described below.

3. **F5 legacy namespace — FIXED.** [comfy.py:47](</D:/aai work/granthstudio/src/granthstudio/comfy.py:47>) preserves the plain-text identity and writes the JSON record in place. The second unconditional JSON parse that caused `JSONDecodeError` is gone.

4. **F5 uncertain adoption — FIXED.** [comfy.py:82](</D:/aai work/granthstudio/src/granthstudio/comfy.py:82>) retains `submission_namespace`; [comfy.py:530](</D:/aai work/granthstudio/src/granthstudio/comfy.py:530>) uses it for uncertain-submission lookup. Execution, reconciliation and cancellation retain the explicit-adoption ownership checks.

5. **F8 actual translation text — FIXED at approval.** [translation.py:110](</D:/aai work/granthstudio/src/granthstudio/translation.py:110>) recomputes the normalized text hash before evidence verification. Updating both text and candidate hash still fails the evidence-output comparison.

6. **F8 request/release binding — PARTIAL.** Speech request/text inputs and per-line Marathi hashes are recorded and enforced at approval. Initial release execution rechecks evidence, but resumed releases and translation release binding remain incomplete.

**Confirmed remaining defects**

1. **Medium — Output-only fallback still permits a save-only retry.**  
   File: [comfy.py:170](</D:/aai work/granthstudio/src/granthstudio/comfy.py:170>).

   Reproduction: use an output-only graph with `inputs={"seed": 1, "filename_prefix": "a"}`, reject it, then change only the prefix to `"b"`. The fallback fingerprints the output node and treats its seed as generation evidence. A read-only probe with journal writes and submission mocked in memory reached one new POST.

   **Required correction:** exclude the output node unconditionally; an empty upstream closure should provide no seed evidence and refuse this retry.

2. **Medium — Completed tasks bypass evidence revalidation on resume.**  
   Files: [pipeline.py:167](</D:/aai work/granthstudio/src/granthstudio/pipeline.py:167>), [pipeline.py:384](</D:/aai work/granthstudio/src/granthstudio/pipeline.py:384>), [scheduler.py:159](</D:/aai work/granthstudio/src/granthstudio/scheduler.py:159>).

   Reproduction: complete a release, then remove or alter its model-run evidence without changing timelines or sealed task outputs. Evidence is absent from task identity and preflight checks. `_verify_audio` and `_verify_assembly` do not revalidate it, so existing receipts remain reusable. A completed audio task can also supply stored verified provenance to a later assembly without another audio evidence check.

   **Required correction:** revalidate generated-audio and model-translation evidence in the verification/preflight paths used for resumed tasks.

3. **Medium — Translation release checks a stored hash rather than current text/request.**  
   File: [pipeline.py:141](</D:/aai work/granthstudio/src/granthstudio/pipeline.py:141>).

   `_release_translation` supplies the stored `candidate_sha256` as the expected output and supplies no Marathi input hash. With current review hashes updated, changed Hindi text can retain the old model provenance; changed Marathi inputs can likewise retain unrelated translation evidence.

   A read-only probe executing the extracted helper against intact, mocked evidence returned `verified` while the current text hash differed from the evidence output.

   **Required correction:** compare evidence with the normalized current Hindi text hash and the current aligned Marathi hash.

**Test and receipt credibility**

The XML contains **318 tests, zero failures/errors, three skips**, consistent with **315 passed, 3 skipped**. The receipt binds those bytes to the stated code commit and architecture; it remains a recorded execution claim, not an independently reproduced run.

- **F7:** the sentinel test would fail against BASE on POSIX: the redirected pathname resolves outside, and the old cleanup deletes the sentinel. It is meaningful but skipped here.
- **F2:** the new test catches the ordinary upstream save-prefix bypass and would fail before the fix. It misses the output-only fallback.
- **Legacy namespace:** the new migration test exercises the prior parse failure and would fail before the fix.
- **Uncertain adoption:** the new test exercises a lost response under the original namespace and would fail before the fix.
- **Translation text:** the text-only edit catches the original defect; the self-consistent edit checks evidence-output enforcement.
- **Request/release:** the speech request mismatch and pre-release evidence removal/alteration tests exercise prior failures. They omit successful-release-then-resume tampering and translation release input/text mismatches.

The three skips are the two symlink-creation tests and the POSIX parent-swap sentinel. **POSIX descriptor creation, cleanup and sentinel behavior were not executed on this host.**

No full suite was rerun during this read-only review. No files were modified.

**Immediate regression checks**

No round-2 regression found in F3’s durable attempt cap, F4’s OS ownership lock, F6’s task-boundary readiness checks, required-action coverage, Marathi lock, Hindi approval, FLF gating, benchmark-versus-production isolation, or uncertain-submission duplicate prevention.

Legacy records without evidence and without verified claims remain unverified. Older evidence records lacking required input bindings fail closed at approval; imported audio and `human_text` bypass model-evidence verification as intended.

**Merge verdict: MERGE AFTER SPECIFIC FIXES.**

Smallest handoff: correct the three checks above and add regressions for output-only retry, evidence tampering after successful completion, and translation release text/Marathi mismatches.

External gates remain unchanged: exact checkpoint/hash and workflow/node-version validation, real model execution, measured Kaggle T4 resources and quality, separate FLF decision, durable external recovery, translation/voice review, and human production authorization. CPU evidence satisfies none of those external gates.