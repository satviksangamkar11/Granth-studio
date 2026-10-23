No blocking issue remains at `04b1cfa8cd52fd196af7283b7b23fe78794444bf`. A pinned SDXL GPU run may be authorized.

- Other callers retain the default full gate (`keyframes.py:474`, `pipeline.py:103`).
- The first image passes the full gate before submission; failure stops the batch (`sdxl_first_test.py:306`).
- `check_host=False` preserves checkpoint hash, workflow status, reference integrity, style drift, and live node/model checks (`keyframes.py:259–323`).
- The control retains the same generation settings, changing only references, asset ID, and request hash (`sdxl_first_test.py:295`).
- The regression detects an ignored parameter. Its body passed with in-memory substitutes and failed under that mutation (`test_style.py:144`).

Full pytest was not rerun. No files modified, GPU used, or downloads performed.