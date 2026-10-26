NOT SAFE

- **MAJOR — `scripts/source/draft_source.py:105,165,176,201`:** Scrubbing before JSON parsing misses escaped secrets: `"\u006evapi-..."` becomes `nvapi-...` after parsing and can reach draft files and REVIEW.md. **Fix:** scrub decoded strings recursively and scrub every final serialized output.

- **MAJOR — `scripts/source/draft_source.py:102,129,162`:** HTTP 200 with `choices: []` raises `IndexError`; a complete set of ovi IDs without `meaning_en` raises `KeyError`. A worker exception aborts the run before the receipt is saved. **Fix:** validate response envelopes and row schemas; convert malformed replies into recorded failures and preserve completed batches.

- **MAJOR — `scripts/source/draft_source.py:195–198`:** `DRAFT_FAILED` rows have no check field, so REVIEW.md displays **OK** beside their empty meanings. **Fix:** render failure status explicitly; show OK only for a valid checker verdict.

- **MAJOR — `scripts/source/draft_source.py:121,138`:** Model dictionaries retain arbitrary fields, including `approved: true`; null/empty meanings also pass ID-only validation. **Fix:** construct output rows from allowed, validated fields and enforce unapproved status independently of model output.

- **MINOR — `scripts/source/draft_source.py:84–89`:** Missing `names_in_text` or `[""]` passes the name check; invalid citation types are silently discarded. **Fix:** require nonempty string names and integer citations, rejecting malformed entries explicitly.

- **MINOR — `scripts/source/draft_source.py:65–68`:** Taking the last closing bracket can reject a valid array followed by another bracketed fragment, then return an inner object instead. **Fix:** use `JSONDecoder.raw_decode` and require the expected top-level type.

- **MINOR — `scripts/source/fetch_hj.py:63–68`:** `--from-raw 1` replaces SOURCE.json with chapter 1 only and labels its text hash like the normal fetch’s HTML hash. **Fix:** preserve untouched chapter records and identify raw-text provenance/hash type.

Static tracing supports the fixed NVIDIA URL, blocked redirects, fixed output paths, non-execution of replies, thread-safe KeyPool, ordered batch collection, and correct three-argument timeout lambda. The normal fetch branch is unchanged.

No network calls or file modifications. Runtime checks were not completed: default Python lacks PyYAML, and the repository environment was inaccessible.