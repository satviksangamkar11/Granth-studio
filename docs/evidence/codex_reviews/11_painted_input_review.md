Not cleared for gpu0 yet. Reviewed `30bd194..ba59a2e`; the commit after `b6572da` adds only the review prompt.

- **MAJOR — `scripts/ltx_first_test.py:104–111,458–465`: misleading receipts on reused workdirs.** An existing project skips `use_painted_start`, retaining its old image, prompt and style, but the receipt records the newly supplied files. Reproduce by running painted gpu0 in a workdir previously prepared without it. Require existing inputs to match or refuse before submission.

- **MAJOR — `scripts/ltx_first_test.py:501–502,417`: painted retry bypasses diagnostics.** `_retry_test` returns before frame extraction and screening. Shell evidence copies can therefore pair the new clip with the first run’s previews. Run diagnostics on the retry output before its verdict and copy those previews.

- **MAJOR — `scripts/ltx_first_test.py:259–265`: input similarity never affects screening.** A read-only mocked check with input SSIM `0.0`, internal SSIM `1.0`, and luma step `0.1` returned `drift_suspected=False`. An unrelated stable clip can clear the screen. Include input mismatch/missing measurement in the screen result; retain human review as a separate requirement.

- **MINOR — `scripts/ltx_first_test.py:79,458–459`; input `README.md:5`: “verbatim” is inaccurate.** `.strip()` removes surrounding whitespace, including the committed prompt’s final newline. Internal newlines survive approval, compilation and substitution into node 6. Preserve the text exactly or document the normalization.

- **MINOR — `.gitignore:25–27`: exceptions are broader than intended.** They admit arbitrary PNG/MP4 files throughout those directories, without size or hash restrictions. Restrict exceptions to the intended files.

- **MINOR — `scripts/kaggle/offline_validate_gpu_evidence.py:93`: hard-link aliases remain writable.** `resolve()` catches identical paths and symlinks, but an output hard-linked to an input still overwrites original evidence. Check existing outputs with `samefile()` too.

Verified: committed image hashes match docs; workflow, checkpoint and sampling parameters remain unchanged; upload uses the existing pipeline; node 7 remains the workflow’s negative. Early painted refusal and empty-array expansion work. Normal drift FAIL retains previews.

No files changed, GPU use or downloads. Media tests were not rerun; saved 466-test evidence predates this change.