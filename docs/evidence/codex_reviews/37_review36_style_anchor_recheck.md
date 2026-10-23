No blocking issue remains by inspection at `f950f4a`: the harness rejects style-anchor mode without a reference set; Kaggle rejects it before downloads; the pipeline rejects an anchor sharing another request reference’s SHA-256. A pinned SDXL GPU run may be authorized.

**MINOR — `tests/test_sdxl_first_test.py:425`:** The pipeline regression only checks for an error-message string; it never passes the constructed duplicate-image request to `sdxl_generate`. A disabled guard would still pass. Replace this with a behavioral rejection assertion.

No files changed; no tests, GPU, downloads, or network run.