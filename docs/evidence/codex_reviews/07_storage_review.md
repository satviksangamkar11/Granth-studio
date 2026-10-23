**Two MAJOR issues remain in `9755413..8ed5ed1`.**

- **MAJOR — `scripts/kaggle/ltx_first_test.sh:29–30,239–242`: publication races `tee`.** Neither EXIT trap closes the logging pipe or waits for `tee`. Early refusal can publish an incomplete `run_log.txt`; normal completion archives before the final status message and copies the live log without synchronization. Close redirected stdout/stderr and wait for `tee` before archiving/publishing.

- **MAJOR — `scripts/kaggle/ltx_first_test.sh:29,241`: failed reruns retain published success evidence.** Reproduce: publish a successful stage, then rerun that stage and refuse early. The source verdict is deleted at line 30, but `cp -r` leaves the previous destination `stage_verdict.json`, and the previous `.tgz` remains. Replace/invalidate prior published evidence so a failed invocation cannot appear successful.

- **MINOR — `scripts/kaggle/ltx_first_test.sh:105–108`; `scripts/kaggle/build_ltx_notebook.py:47–48`: caches remain outside `W`.** No pip/HuggingFace/torch cache or temporary-directory overrides are set. Pip cache/build scratch can consume hundreds of MB to several GB if large dependencies change; installed packages also remain in the Python environment. HF/torch cache growth depends on runtime downloads; the two pinned weights use direct curl targets and do **not** duplicate into HF cache. Set cache variables and `TMPDIR` under `W` before both notebook bootstrap and shell installation.

Other checks:

- Notebook passes `W=TMP`: ComfyUI, curl weights, worker temp/output/input/user directories, projects, source clone, and both disk checks follow `/kaggle/temp/ltx`. Direct shell invocation still defaults to `/kaggle/working`.
- Trap replacement preserves publication attempts for exits 2/3/4 after installation, worker exit 5, `set -e` aborts, and normal completion. Invalid-stage exit 2 and missing-variable refusals occur **before** trap installation. Copy failures are silently suppressed.
- WORK/TMP receipt paths are consistent. Publish targets are siblings of the repo checkout and do not dirty it. Notebook matches its generator; all code cells compile.
- Approval, hash, clean-tree, GPU-isolation, prerequisite, and retry safeguards are unchanged. The stale published PASS is the identified evidence safeguard regression.

Static review only; no Kaggle execution or filesystem changes.