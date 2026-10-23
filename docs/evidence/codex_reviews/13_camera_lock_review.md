**Not cleared yet.**

- **MAJOR — [camera_motion_analysis.py:88](</D:/aai work/granthstudio/scripts/kaggle/camera_motion_analysis.py:88>):** SSIM uses the coverage mask’s bounding rectangle, including uncovered black corners after rotation. This can falsely lower compensated similarity and produce CONTENT_DRIFT. Compute the SSIM map and average only pixels whose full SSIM window is covered; regenerate analysis evidence.

- **MAJOR — [style_v2_suite.xml:1](</D:/aai work/granthstudio/docs/evidence/cpu_tests/style_v2_suite.xml:1>):** Saved evidence reports **490 tests, one failure**, specifically the painted-retry visual screen at `tests/test_ltx_first_test.py:607`. It also lists `test_video_safe_style.py`, absent from this branch. Supply passing evidence bound to the reviewed candidate; this receipt cannot establish regression clearance.

- **MINOR — [REPORT.md:10](</D:/aai work/granthstudio/docs/evidence/kaggle_dual_t4/gpu0_attempt5_painted/REPORT.md:10>):** Calling this definitively a “camera-motion FAIL” exceeds the JSON’s **INCONCLUSIVE** result. Three fits are unreliable. The attempt-4 control JSON and evidence establishing thresholds before inspection are absent. Qualify the causal claim and attach supporting evidence or remove unsupported claims.

- **MINOR — [ltx_first_test.py:275](</D:/aai work/granthstudio/scripts/ltx_first_test.py:275>):** Extraction retries accept file existence regardless of command success. A pre-existing preview surviving failed extraction can supply stale measurements. Require successful extraction of a fresh output. `_ssim` retries missing scores, not low scores; it also lacks a return-code check.

- **MINOR — [camera_motion_analysis.py:159](</D:/aai work/granthstudio/scripts/kaggle/camera_motion_analysis.py:159>):** `--json` can name and overwrite the harness receipt; only overwriting the clip is refused. Protect existing receipts/verdict files to support “never edits verdicts.”

Verified: prompt selection reaches `--prompt-file`; reused-project mismatches refuse differing prompts. Clip/input hashes match, harness **FAIL** remains preserved, style v1 is frozen, and workflow/checkpoint/postflight are unchanged. Ignore exceptions are file-specific.

Read-only review only; no files modified, GPU work, downloads, or test-suite execution.