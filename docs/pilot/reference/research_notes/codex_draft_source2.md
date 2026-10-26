NOT SAFE

- **MAJOR — scripts/source/draft_source.py:115:** `evidence_ovis: [{}]` raises `TypeError`; the character path aborts before saving its receipt. **Fix:** use only validated integer citations for lookup and record malformed replies as failures.
- **MAJOR — scripts/source/draft_source.py:220:** Character/place entries still preserve `approved: true` and `status: "APPROVED"`. Reproduced in saved-output mocks. **Fix:** allowlist fields within each entry and enforce unapproved status.
- **MAJOR — scripts/source/draft_source.py:220:** `{"characters":"garbage","places":17}` becomes empty lists with zero problems and exit code 0. **Fix:** reject malformed collection types and return a recorded failure.

Other prior fixes check out: escaped-secret scrubbing, meaning-row/envelope failure handling, failed-row display, JSON bracket parsing, and SOURCE.json preservation/hash labeling.

Five test functions passed in isolation; full pytest was blocked by the inaccessible repository environment. No files changed.