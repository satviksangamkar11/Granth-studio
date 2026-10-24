Blocking issue remains.

- **MAJOR — [build_gpu_all_notebook.py:141](</D:/aai work/granthstudio/scripts/kaggle/build_gpu_all_notebook.py:141>):** A timeout during HiDream PNG writing can leave a truncated file. `blank(fp)` raises an uncaught decoding error, aborting the comparison even when another model has usable images. Reproduced with a simulated decoder failure. Catch per-file decoding errors, log and skip invalid images.

- **MINOR — [build_gpu_all_notebook.py:38](</D:/aai work/granthstudio/scripts/kaggle/build_gpu_all_notebook.py:38>):** `l[:400]` still truncates child output entering `notebook.log`. Per-model logs preserve full lines. Pass the full line to file logging.

Prior findings: blank detection, incremental atomic receipts, stale-output cleanup, and setup failure handling are closed; logging is partially closed. Completed images remain usable when a later image times out. Model-card text uses `log`. Cleanup precedes log opening; the list comprehension executes correctly.

Cells and nested HiDream script compile. Read-only, memory-only checks; no network or GPU execution.