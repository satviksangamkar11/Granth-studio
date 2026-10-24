Blocking issues remain.

1. **MAJOR — Black images count as usable.** [open_edit_bench.py:151](</D:/aai work/granthstudio/scripts/image_trials/open_edit_bench.py:151>), [build_gpu_all_notebook.py:131](</D:/aai work/granthstudio/scripts/kaggle/build_gpu_all_notebook.py:131>). The benchmark records `min_max` but never writes `blank`; the summary tests the missing field. HiDream accepts any existing PNG without checking pixels. **Reproduced in memory:** a result with `min_max=[0,0]` produces `compare.png` and `DONE`. Decode and reject blank outputs for every model before counting them.

2. **MAJOR — A timeout hides already completed images.** [open_edit_bench.py:166](</D:/aai work/granthstudio/scripts/image_trials/open_edit_bench.py:166>), [build_gpu_all_notebook.py:127](</D:/aai work/granthstudio/scripts/kaggle/build_gpu_all_notebook.py:127>). Receipts are written only after all scenes finish. If scene 1 succeeds and scene 2 reaches the one-hour deadline, the PNG survives but the summary reports “no receipt” and ignores it. Persist each result atomically as it completes, including failures.

3. **MAJOR — Old outputs can make a failed rerun succeed.** [build_gpu_all_notebook.py:15](</D:/aai work/granthstudio/scripts/kaggle/build_gpu_all_notebook.py:15>), [build_gpu_all_notebook.py:133](</D:/aai work/granthstudio/scripts/kaggle/build_gpu_all_notebook.py:133>). The fixed output directory retains receipts and HiDream PNGs. If the current attempts fail before replacing them, CELL4 accepts previous artifacts without checking their provenance or hashes. Use a run-specific directory or explicitly verify reusable artifacts against current inputs and configuration.

4. **MINOR — HiDream continues after failed setup commands.** [build_gpu_all_notebook.py:97](</D:/aai work/granthstudio/scripts/kaggle/build_gpu_all_notebook.py:97>). The pip and clone return codes are ignored. A failed target installation can leave inference using missing, partial, or shared packages instead of the intended pins. Stop the HiDream stage immediately on either setup failure. The patch assertions themselves correctly reject missing literal matches.

5. **MINOR — File logs are incomplete.** [build_gpu_all_notebook.py:28](</D:/aai work/granthstudio/scripts/kaggle/build_gpu_all_notebook.py:28>), [build_gpu_all_notebook.py:80](</D:/aai work/granthstudio/scripts/kaggle/build_gpu_all_notebook.py:80>). Child lines are truncated to 400 characters before either file receives them; model-card usage uses plain `print`, bypassing `notebook.log`. Preserve full diagnostic lines in files and route that output through logging.

Checks and limits:

- All generated cells **and the nested HiDream script compile**. No nested-quote or `%` formatting defect found.
- Mocked checks confirm `CUDA_VISIBLE_DEVICES` and `HF_TOKEN` reach children, separate sessions are requested, cleanup runs, and closed-stdout timeouts are handled. No inherent stage-B deadlock found; command failures are logged, although return codes are discarded.
- Process exit/group cleanup should release model GPU allocations between stages. Actual Linux process-group behavior was not exercised.
- Torch constraints are correctly passed to the shared pip installation for ordinary `package==version` freeze entries. HiDream’s target install does not receive those constraints.
- **T4 precision remains unverified.** T4 lacks native BF16 support. NF4 reduces weight storage; it does not prove BF16 kernel compatibility, activation-memory fit, or numerical stability. BF16 alone is not evidence that images will silently become black. Require finite-output/blank checks and measured inference evidence before claiming the OOM fix works.
- HiDream’s actual multi-GPU execution and FLUX3’s explicitly guessed API remain unverified.
- Both supplied tests pass with filesystem operations mocked in memory, despite finding 1. Add behavioral regressions for these failures.

No changes, network access, or GPU execution performed.