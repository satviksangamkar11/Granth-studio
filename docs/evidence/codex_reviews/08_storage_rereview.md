**1 MAJOR + 1 MINOR remain.**

- **MAJOR — [ltx_first_test.sh:21](/D:/aai%20work/granthstudio/scripts/kaggle/ltx_first_test.sh:21): stale PASS survives early refusal.** After a successful run, rerun with either required variable unset: lines 21–22 abort before invalidation, preserving the local verdict and both published copies. Also, failure of `mkdir` at line 43 precedes local-verdict removal. Move invalidation of all success markers before these failure paths.

- **MINOR — [build_ltx_notebook.py:47](/D:/aai%20work/granthstudio/scripts/kaggle/build_ltx_notebook.py:47): notebook bootstrap caches remain outside `W`.** Bootstrap pip runs before the shell exports its cache settings. Create scratch directories and pass cache/TMPDIR settings before bootstrap pip; update the generated notebook.

The publication race is closed: Bash **5.3.9** verified that closing stdout/stderr inside the EXIT trap succeeds under `set -euo pipefail`, `wait "$TEE_PID"` returns 0 after flushing, and exit status 7 is preserved. TMPDIR exists before shell consumers. The later trap retains publication, and `need_pass` is unchanged. Both focused source assertions passed.

No files modified; Kaggle execution not performed.