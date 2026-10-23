The three prior runtime findings are closed: captured style is compared by `require_current()`; sheet postflight retains state checks while skipping the host gate; scheduler reuse/fallback still validates receipts and outputs. Tasks without postflight retain their previous behavior, and GPU execution paths retain full preflight. Remaining live style reads are guarded by current-state checks.

Two new validator defects remain:

- **MAJOR — `scripts/kaggle/offline_validate_gpu_evidence.py:101`: original evidence can be overwritten.** Passing `--out` equal to `--receipt` replaces the original verdict file while reporting `"original_verdict_unchanged": true`. Confirmed with an intercepted write; no file was changed. Reject output paths that alias any input, including resolved links, before writing. Add a CLI regression.

- **MINOR — `scripts/kaggle/offline_validate_gpu_evidence.py:97`: hash bindings can disappear.** Hashes use basenames as keys. Two inputs named `evidence.json` in different directories produce one entry, silently losing a binding. Key by input role and record its path/hash; test duplicate basenames.

The discontinuity threshold sensibly flags human review without upgrading the original verdict. All four hashes in the saved retrospective report match the current evidence.

Saved JUnit records **466 tests, 0 failures/errors, 4 skipped** for the runtime-fix candidate. Tests were not rerun. No files changed, GPU use, or downloads.

No blocking issue remains in the runtime fixes for a fresh isolated gpu0 test; the validator’s preservation guarantee needs the correction above.