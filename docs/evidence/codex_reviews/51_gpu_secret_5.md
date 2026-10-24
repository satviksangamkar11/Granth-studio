- **BLOCKER — `scripts/kaggle/build_gpu_all_notebook.py:44`:** Tee files receive raw child output, bypassing `scrub()`. Reproduced with a fake token: page output and `notebook.log` redact it, but the side file retains it. Real callers create `hidream.log`, `qwen21.log`, and `gated.log` (lines 132–135). Required: scrub before writing side files and add a tee regression check.

Prior exception redaction and the **MINOR** empty-value diagnostic pass isolated checks. No other blocking defect found within scope.

Verification used in-memory mocks only; no files changed, network, or GPU use.