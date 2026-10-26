NOT SAFE

- **MAJOR — scripts/source/director_test.py:107:** Empty or whitespace-only Marathi normalizes to `""`, which matches every ovi. A missing spoken line can therefore pass as an exact quote with `paraphrase=false`. **Fix:** reject normalized-empty quotes; require `null` plus `paraphrase=true` for unquoted lines. Add regression tests.

- **MAJOR — scripts/source/director_test.py:284–287:** A repair can delete dialogue and replace all `ovi_ids` with one in-range ovi and still be accepted as VALID. No required-content comparison prevents this; displayed reviewer verdicts concern the original plan. **Fix:** enforce required dialogue/ovi dispositions before accepting repairs, and explicitly identify which plan the reviews assessed. Test a repair that drops content.

Tests could not run: system Python lacks pytest/jsonschema; the project Python launcher was permission-blocked. No files modified or model calls made.