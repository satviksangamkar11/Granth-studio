# SPEC: PATCH `scripts/source/fix_loop.py` + `tests/test_fix_loop.py` (retry empty or incomplete coder replies without using a fix round)

You receive the CURRENT full source of both files as reference. Output BOTH files COMPLETE (every existing function, constant and test must remain; nothing dropped or shortened). All existing tests must still pass unchanged, and the new tests must pass.

PROBLEM: in `run_job`, a coder or fixer call that returns an empty reply (status 0, empty text) or a reply that does not contain every expected file (files_ok False) is counted as one of the `max_rounds` fix rounds. Transient API failures therefore escalate pieces that were fixable.

CHANGE:
1. Add a helper `call_with_retries(call, retries=3, sleep=time.sleep, wait_s=5)` that invokes the supplied zero-argument callable up to `retries` times. A result counts as USABLE when its reply text is non-empty and parse_files(reply) contains EVERY path in expected_files. It returns (result, attempts, usable). It sleeps `wait_s` between attempts via the injected sleep (default time.sleep) and never sleeps after the last attempt.
2. In `run_job`, wrap each coder/fixer call (round 0 and every fix round) with call_with_retries. A round is counted ONLY when the call was usable or all retries were used. Record in the round's status entry the extra field `"retries": attempts - 1`. If all retries fail, the round is recorded exactly as today (coder_status "0", files_ok False) so the old behaviour and old tests still hold when retries are exhausted.
3. The job file may set `"call_retries": N` (int 1..5, default 3) and `"retry_wait_s": S` (number 0..60, default 5); invalid values raise ValueError in the existing job validation function with a clear message. `call_retries` = 1 reproduces the old behaviour exactly.
4. Add tests (fake callers and a fake sleep recording its arguments; no real waiting, no network): (a) first reply empty then usable -> one round used, retries == 1, sleep called once with wait_s; (b) reply missing one expected file then complete -> retried; (c) all 3 attempts empty -> round recorded as failure with retries == 2 and the existing failure fields; (d) call_retries == 1 behaves like before (no sleep); (e) invalid call_retries / retry_wait_s rejected; (f) a usable first reply never sleeps.

HARD RULES: stdlib only; no network in tests; no Kimi; do not change the default `fixers` list or any public signature except adding the optional keyword arguments; no absolute drive paths.

OUTPUT FORMAT (mandatory, the parser rejects anything else): reply with ONLY these two blocks, no other text. Each block is the line `FILE: <path>` followed immediately by a fenced code block that starts with ```python on its own line and ends with ``` on its own line:
FILE: scripts/source/fix_loop.py
```python
<complete module source>
```
FILE: tests/test_fix_loop.py
```python
<complete test source>
```
