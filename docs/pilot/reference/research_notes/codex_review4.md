NOT SAFE

- **MAJOR — scripts/source/seeded_check_test.py:51–54:** Same-length reordered responses silently attach verdicts to the wrong cases. Mock reproduction mis-scored 6/13 correct answers; scores can also inflate. Fix: send unique case IDs, require exactly one valid answer per ID, and match by ID. Count mismatches already become `NO_ANSWER`.

- **MAJOR — scripts/source/draft_source.py:240:** Restarting truncates the existing partial checkpoint before any batch completes, destroying saved results from an interrupted run. Fix: preserve and validate the checkpoint, then resume unfinished batches.

- **MAJOR — scripts/source/draft_source.py:261:** `{"problems":["unable to check"]}` becomes `model_check: []`, indistinguishable from a successful check finding no problems. Fix: validate every problem object; mark malformed responses `NO_CHECK`.

Verification used isolated, in-memory mocks. Full tests were blocked by Python environment issues. No files modified.