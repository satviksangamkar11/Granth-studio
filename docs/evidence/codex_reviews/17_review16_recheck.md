**Blocking issues remain: 2 MAJOR, 1 MINOR. Do not authorize the pinned GPU run yet.**

- **MAJOR — `scripts/kaggle/sdxl_first_test.sh:75`: inventory glob misses `..extra_pack`.** Neither `*` nor `.[!.]*` includes names beginning with two dots. Such a custom-node directory can execute during ComfyUI startup; the Python inventory check runs afterward. **Correction:** enumerate every entry, including double-dot names, before starting ComfyUI.

- **MAJOR — `scripts/sdxl_first_test.py:188`: ownership proof is disconnected from the requested server.** With `--comfy-url http://remote-host:8188`, the check proves only that the supplied local PID owns port 8188. An in-memory probe confirmed this URL produces no extra-check refusal when local ownership/CUDA checks pass. Submissions can therefore reach another server while recording local pins and GPU identity. **Correction:** constrain the endpoint to the verified local worker and bind ownership proof to its address and port.

- **MINOR — `scripts/kaggle/build_sdxl_notebook.py:49`: pre-install refusals remain incomplete.** GPU names, ffmpeg and disk are checked, but RAM and GPU idleness are checked only by the shell after `pip install`. **Correction:** perform those checks before installation.

Prior findings: stale evidence invalidation/final verdict and fresh-project approval confinement are closed on the normal shell path. Direct `--execute` does invoke `execution_extra_problems`; commit, cleanliness, source pins and CUDA checks are present, subject to the endpoint defect above.

Python/notebook syntax and diff whitespace checks passed. Saved JUnit evidence predates the fixes and excludes both new regression tests. No files modified, GPU used or downloads performed.