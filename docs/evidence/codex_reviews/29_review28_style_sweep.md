- **MAJOR — scripts/sdxl_first_test.py:179–183,215:** Sweep copies inherit `_status: validated`; changing `_note` does not change how the workflow loader reads them. Success also produces the ordinary stage `PASS`. Keep experiment status distinguishable in machine-readable workflow metadata and final receipts/verdicts.

- **MAJOR — scripts/sdxl_first_test.py:186:** Reference-free requests retain `missing_references`. With `--visual vis_s3_kf --style-sweep`, `require_references()` rejects the missing character sheets before submission. Clear reference requirements specifically for these experimental requests.

- **MINOR — scripts/sdxl_first_test.py:209–215:** An allowed one-image sweep constructs `xstack=inputs=1`, which fails, yet returns `PASS`. Duplicate cfg values also collapse dictionary entries and misrepresent the contact-sheet rows. Handle one image directly, reject/deduplicate cfg values, and record contact-sheet failure explicitly.

Static inspection supports unchanged frozen prompt/negative/style identity, deterministic recorded seed offsets, numeric bounds, and the first-submission host gate. Default flags and empty-array expansion are sound for Kaggle’s Bash.

**Blocking issues remain.** No tests or GPU execution performed; no files changed.