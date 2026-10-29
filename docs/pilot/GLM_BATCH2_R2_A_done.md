# Batch 2 — read-only review

Scope: only the files shown in the payload were reviewable (`coder_run.py`, `test_coder_run.py`, `test_coder_tools.py`, `review_run.py`, `test_review_run.py` + the two specs). `TEST_RUN_BATCH2.txt` was not included; every claim below is from line-by-line tracing/mutation analysis of the shown code, not guessing.

## Unit 1 — `scripts/source/coder_run.py` + `tests/test_coder_run.py` + `tests/test_coder_tools.py` (spec `coder_tools_a.md`)

1. **BLOCKING (CLASS 3): the spec rule "at most 2 retries" for the length continuation has no failing test.**
   - What: spec change 3b and the Tests bullet explicitly require the check *"retried with doubled `max_tokens` (check the values passed: 1000 -> 2000 -> 4000) at most 2 retries"*. The suite never observes the second retry: the only retry-sequence assertion is `assert chat_stream_calls == [1000, 2000]` (`tests/test_coder_tools.py:161`, in `test_wrap_ds_retries_and_receipts` — success on attempt 2), and both ceiling tests start at `max_tokens=100000`, where the 128000 ceiling alone stops the loop after one attempt.
   - Verified by mutation on `scripts/source/coder_run.py:123` (`... and attempts < 3`):
     - change to `attempts < 2` (only 1 retry) → every existing test still passes;
     - delete the attempt bound entirely (retry until the ceiling) → every existing test still passes.
     So the "at most 2 retries" rule is currently unprotected.
   - Exact fix — add to `tests/test_coder_tools.py` (after `test_wrap_ds_retries_and_receipts`); it passes against the current implementation and fails under both mutations above:
     ```python
     def test_wrap_ds_at_most_two_retries():
         cr = load_coder_run()
         cr.RECEIPTS.clear()
         calls = []

         def fake_chat_stream(pool, keys, model, system, user, max_tokens=40000):
             calls.append(max_tokens)
             return "", {"finish": "length", "status": 0, "wall_s": 0.1, "usage": {}, "error": None}

         def original_ds():
             return SimpleNamespace(_stream_once=lambda k, b: (200, "", {}), chat_stream=fake_chat_stream)

         mod = cr.wrap_ds(original_ds, "on", "high")()
         reply, info = mod.chat_stream("pool", "FAKEKEY", "nvidia/nemotron-3-ultra-550b-a55b", "sys", "user", max_tokens=1000)
         assert calls == [1000, 2000, 4000]          # exactly 2 retries
         assert reply == ""
         assert info["attempts"] == 3
         assert info["finish"] == "length"
         assert len(cr.RECEIPTS) == 3
         assert [r["attempt"] for r in cr.RECEIPTS] == [1, 2, 3]
         assert "FAKEKEY" not in str(cr.RECEIPTS)    # fake key travels through the keys argument
     ```

Everything else in this unit verifies against the spec: thinking default `on` with the old test assertion updated; idle-timeout proxy (default 600, `seconds` arg wins, `CODER_IDLE_S` with invalid→600, positional-timeout override with `data` preserved, idempotent single layer, `__getattr__` forwarding, no-`nt` no-op); receipt dict exactly as specified, taken from `info` only; `write_receipt` (indent 1, sort_keys, utf-8, `None` on failure); `find_out_arg`; `main` flow and profile line; stdlib-only, no import-time work, no key printed/stored.

## Unit 2 — `scripts/source/review_run.py` + `tests/test_review_run.py` (spec `review_run.md`)

none

## Unit 3 — `scripts/pipeline/stage1/crosscheck.py` + `tests/test_stage1_crosscheck.py` (spec `crosscheck.md`)

none — module, tests and spec were not included in this review payload; nothing verifiable, so no defects are reported.

## Unit 4 — `scripts/pipeline/stage1/compare_a1.py` + `tests/test_stage1_compare_a1.py` (spec `compare_a1.md`)

none — not included in this payload; nothing verifiable.

## Unit 5 — `scripts/pipeline/approve.py` + `tests/test_approve.py` (spec `approve_cli.md`)

none — not present in this payload ("if present"); nothing verifiable.

## Unit 6 — `scripts/pipeline/check_script_cli.py` + `tests/test_check_script_cli.py` (spec `check_script_cli.md`)

none — not present in this payload ("if present"); nothing verifiable.

## Non-blocking notes

- `tests/test_coder_tools.py:170` — the receipts no-key assertion (`"FAKEKEY" not in str(r)`) is vacuous as written: `FAKEKEY` is only ever passed to `_stream_once`, never to `chat_stream`, so it can never reach the receipts. The test in the fix above passes it through the `keys` argument and closes this gap.
- `scripts/source/coder_run.py:170` (`write_receipt`) — "never raises" holds for a missing folder and IO failures; a path containing a NUL byte would raise `ValueError` from `Path.exists()`. Unreachable via `main` (argv cannot contain NUL); wrap in try/except only if direct-call robustness is wanted.
- `scripts/source/review_run.py:100` (`build_prompt`) — every content line is prefixed with one space before fencing, so the reviewed code is delivered modified (leading space is significant in Python). The spec says "the file content in a fenced block" and the longer-than-any-backtick-run fence already protects the block; tests only assert substrings, so they pass. Consider dropping the indent or documenting it.
- `scripts/source/review_run.py:247-252` — a last line `## Verdict: <anything else>` is returned verbatim instead of `NONE`; the spec says the verdict is `READY`, `FIX FIRST` or `NONE`. Consider normalizing unknown values to `NONE`.
- `scripts/source/review_run.py:196-208, 230-233` — `run_review` returns extra keys (`reply`, `error`, `effort`, `thinking`) beyond the spec'd set, and the real path injects a thinking/effort profile into the request body, which the spec's real-path description doesn't mention. Harmless superset / extra hardening.
- `scripts/source/review_run.py:84-85` — the secret-name skip checks the basename only; a file inside a `secrets/` directory (e.g. `secrets/keys.txt`) is read and sent. This matches the spec's literal "whose name contains `secrets`" and the test, but checking `rel.as_posix()` as well would be stricter.

## Verdict: FIX FIRST