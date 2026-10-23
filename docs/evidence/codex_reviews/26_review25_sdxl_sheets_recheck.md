No blocking issue remains in this narrow re-check of `2739d2b`.

- `flags == [True, False, False, False, False]` detects a wrong gate flag on any of the five generations.
- `gate_calls == [0]` detects a skipped or repeated gate, or a gate invoked after any submission. Both wrappers call the real functions.

Verified by code inspection only; tests were not executed. A pinned SDXL GPU run may be authorized.