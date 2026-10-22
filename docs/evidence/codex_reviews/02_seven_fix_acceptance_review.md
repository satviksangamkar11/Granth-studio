# Codex review 2 — seven-fix acceptance review (FAIL, merge after specific fixes)

- **Origin:** verbatim output of `codex exec --sandbox read-only` (codex-cli 0.163.0) run from this session by Claude Code on 2026-10-22.
- **Reviewed range:** fa32a5a..46f1ab2
- **Prompt:** the 'FINAL SEVEN-FIX ACCEPTANCE REVIEW' brief (not stored in the repository)
- **Integrity:** the text below is unedited; Claude did not re-run or rewrite it.

---

**FAIL — MERGE AFTER SPECIFIC FIXES.** Four findings remain partially resolved.

1. **F2–F8 acceptance matrix**

   - **F2 — PARTIAL:** disconnected seeds are rejected, but output-only changes can still qualify as fresh generation.
   - **F3 — FIXED:** the persisted cap survives reconstructed backends; omission/increase cannot bypass it. Polling preserves attempts; reset targets one journal.
   - **F4 — FIXED:** persistent OS locks replace timeout takeover. Descriptor lifetime and exception cleanup preserve ownership; process death releases it.
   - **F5 — PARTIAL:** copied stores fork correctly, but legacy recovery and adoption of uncertain submissions remain broken.
   - **F6 — FIXED:** LTX, SDXL and lip-sync enforce readiness at task boundaries. Resource failure and CPU-only tests prevent submissions and block dependents.
   - **F7 — PARTIAL:** Windows pinning has credible coverage; POSIX validation and cleanup still follow mutable paths.
   - **F8 — PARTIAL:** incremental evidence survives, but approval and release do not fully enforce its binding.

2. **Confirmed remaining defects**

   - **High — F7: POSIX cleanup can delete an external file.**  
     [integrity.py:172](</D:/aai work/granthstudio/src/granthstudio/integrity.py:172>), [integrity.py:205](</D:/aai work/granthstudio/src/granthstudio/integrity.py:205>)  
     After a parent is renamed and replaced with an outside symlink, creation correctly uses the pinned directory descriptor. Subsequent `target.stat()`, resolution and `target.unlink()` use the redirected pathname. If an outside file already has the destination name, the containment-failure cleanup deletes that outside file. With no outside file, pathname validation can instead raise `FileNotFoundError` and leave the created file behind.  
     **Correction:** keep validation and cleanup relative to the pinned directory descriptor; add a swap test containing an outside sentinel.

   - **Medium — F2: changing a save-node input permits cached generation.**  
     [comfy.py:416](</D:/aai work/granthstudio/src/granthstudio/comfy.py:416>)  
     The gate checks that seed inputs exist and that the whole output-closure fingerprint changed. Changing only `filename_prefix` satisfies this without changing generation inputs. A completed in-memory probe using the repository’s dependency-aware fake showed: fingerprint changed, seed inputs identical, **zero additional sampler executions**.  
     **Correction:** require a demonstrated change to effective generation inputs; reject save-only changes.

   - **Medium — F5: existing plaintext namespaces cannot migrate.**  
     [comfy.py:57](</D:/aai work/granthstudio/src/granthstudio/comfy.py:57>)  
     The legacy parser handles the old plaintext UUID, then this line parses the same plaintext again without handling failure. A completed in-memory probe reproduced `JSONDecodeError`. This blocks legitimate stores created by BASE.  
     **Correction:** reuse the parsed record and explicitly persist its migration; test a BASE-format namespace.

   - **Medium — F5: adopting an uncertain submission prevents its recovery.**  
     [comfy.py:79](</D:/aai work/granthstudio/src/granthstudio/comfy.py:79>), [comfy.py:527](</D:/aai work/granthstudio/src/granthstudio/comfy.py:527>)  
     Adoption replaces namespace A with B. For a `submitting` journal, reconciliation searches the original token with namespace B, while the server retains namespace A. The prompt cannot match. The adoption test covers a journal already containing `prompt_id`, bypassing this condition.  
     **Correction:** retain the original submission namespace for locating the adopted outstanding prompt.

   - **High — F8: approval validates a stored translation hash, not the actual text.**  
     [translation.py:111](</D:/aai work/granthstudio/src/granthstudio/translation.py:111>)  
     Edit candidate `text` while retaining its original `candidate_sha256` and evidence pointer. Approval checks that stored hash against evidence, then approves the edited text. Deterministic terminology checks do not establish equality with the evidenced output. The tampering test changes the hash instead of exercising this condition.  
     **Correction:** recompute the normalized text hash before evidence verification.

   - **Medium — F8: request and release binding remain unenforced.**  
     [runners.py:80](</D:/aai work/granthstudio/src/granthstudio/runners.py:80>), [speech.py:264](</D:/aai work/granthstudio/src/granthstudio/speech.py:264>), [pipeline.py:133](</D:/aai work/granthstudio/src/granthstudio/pipeline.py:133>)  
     Verification accepts no expected request hash and never compares the evidence request with candidate metadata. Release copies provenance without re-verifying evidence. Consequently, altered request metadata—or missing/tampered evidence after approval—can retain a verified claim through release.  
     **Correction:** enforce the request binding during approval and recheck generated provenance before release.

3. **Regression-test credibility**

   Real subprocess contention and abrupt before/after-POST exits credibly test OS ownership and uncertain-submission recovery against a synthetic HTTP server. No timeout-based displacement remains in either locking implementation.

   The journal-write-failure test is weaker than advertised: its patched writer can fail first while creating the namespace, before journal ownership is exercised.

   The fake cache models dependencies credibly, but existing assertions miss save-only invalidation. Windows junction and ancestor-swap tests ran and check that pinned-directory replacement fails. POSIX behavior was not executed in this receipt; two symlink tests were skipped.

4. **Receipt and revision verification**

   - HEAD: `46f1ab25c541273e2871bd3c9706a19ec8101d2c`
   - Branch: `sprint/remaining-pipeline`; working tree clean.
   - Verified ancestry: BASE → `10c007d…` → CANDIDATE.
   - Only documentation/evidence changed after `10c007d…`.
   - XML reports **312 tests, zero failures/errors, two skips**, supporting **310 passed**.
   - XML SHA-256 matches the receipt: `d00104f9…12b15278`.
   - Frozen architecture is unchanged; its hash matches: `decd0af5…404f7c1`.

   This is consistent source-bound repository evidence, not independent attestation of execution.

5. **Preservation and merge verdict**

   No additional regression was identified in required-action coverage, research/Marathi locking, Hindi approval, benchmark isolation, FLF qualification, speech duration, final QA, production GO or uncertain-submission safeguards. Saved CPU evidence supports their existing coverage, subject to the provenance defects above.

   **MERGE AFTER SPECIFIC FIXES:** correct the six cases listed above and add focused regressions. No architecture redesign is required.

6. **Remaining external gates**

   Real GPU/model capabilities remain **NOT VALIDATED**: exact checkpoint hashes and workflow/node compatibility, T4 resource and session measurements, I2V/FLF quality, SDXL continuity, bilingual speech/translation, lip-sync and real-library `_commit_hash` behavior. Human research, Hindi, voice and production approvals remain required. Integrity hashes do not independently authenticate model weights.

No files were modified; no full-suite rerun, GPU/model execution, installs, downloads, agents, commits or merges were performed.