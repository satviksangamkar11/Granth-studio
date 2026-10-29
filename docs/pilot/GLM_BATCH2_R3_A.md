# Batch 2 — final-round read-only review

Scope: only the files actually pasted in this round were reviewable (`coder_run.py`, `tests/test_coder_run.py`, `tests/test_coder_tools.py`, spec `coder_tools_a.md`; `review_run.py`, `tests/test_review_run.py`, spec `review_run.md`). The other listed units (`crosscheck.py`, `compare_a1.py`, `approve.py`, `check_script_cli.py`, `aggregate.py`/X12, `context.py`/`voice_genders`) were **not included** in this message, so their earlier fixes and new rules could not be re-verified here — no defects are reported for them for lack of evidence, not because they were checked. Every claim below was verified by hand-tracing the code against the spec and the provided tests (no execution).

## 1. `scripts/source/coder_run.py` (+ `tests/test_coder_run.py`, `tests/test_coder_tools.py`, spec `coder_tools_a.md`)

Blocking defects:

none

Verification performed:
- Rule 1 (thinking ON default): `coder_run.py:172` `default="on"`; both default assertions in `test_split_args` updated to `"on"`; all other pre-existing tests kept verbatim, as the spec requires.
- Rule 2 (`with_idle_timeout`): argument wins, else env `CODER_IDLE_S`, invalid/missing → 600 (`coder_run.py:37-44`); proxy forces `kwargs["timeout"]` and drops a positional timeout while keeping the first positional (`:65-67`, matches `test_with_idle_timeout_positional_args_forwarded`); `__getattr__` forwards other attributes (`:69-70`); idempotent single proxy layer via `_coder_idle_proxied`/`_coder_idle_explicit` (`:50-56`, traced through the full 8-step sequence in `test_with_idle_timeout` — 600/45/90/600/30/30 all match); no `nt`/`_OPENER` → returns `ds` unchanged (`:46-47`).
- Rule 3 (`wrap_ds`): profile still applied to `_stream_once` (`:104-105`); `with_idle_timeout` applied (`:108`); retry loop: `attempts < 3` = at most 2 retries, doubling 1000→2000→4000, ceiling `next > 128000` aborts with the **last attempt's** reply/info (`:148-158`, matches the three length-retry tests and the ceiling regression test); receipts contain exactly the 10 documented keys, 1-based attempt, nothing from prompt/reply/pool (`:132-146`, matches `test_receipts_pool_object_never_stored`); `_sanitize_receipt` recursively scrubs every string value (incl. nested dicts/lists in `usage`/`error`) with the keys passed via the `keys` argument — traced against both no-leak tests (`FAKE_KEY` absent from `json.dumps(RECEIPTS)`).
- Rule 4 (`write_receipt`): indent=1, sort_keys, utf-8, `None` for missing dir / non-dir / write failure, never raises (`:193-203`).
- Rule 5 (`main`): resets `RECEIPTS`, prints the profile line unchanged, `find_out_arg` handles `--out V` and `--out=V` (`:180-190`), receipt written whenever `--out` is present (folder-existence check delegated to `write_receipt`, equivalent), returns `nc.main()`'s code.
- No key path to stdout/stderr; the only stored artifact (`RECEIPT.json`) contains sanitized receipts only.

## 2. `scripts/source/review_run.py` (+ `tests/test_review_run.py`, spec `review_run.md`)

Blocking defects:

none

Verification performed:
- `SYSTEM_PROMPT` contains exactly the required reviewer text; no `nvapi-` literal, no `kimi_adapter` import (module hygiene tests pass by inspection).
- `build_prompt`: skip reasons (not found / is a directory / not under root / secrets — any path component containing `secrets`, case-insensitive, plus `.env`/`.key`) all fire **before** the file is read (`review_run.py:62-93`); binary → `not text`, `OSError` → `not readable` (`:95-102`); fence grows past any backtick run (`:112-114`); content appended verbatim (`:174`); byte accounting hand-verified: per-block accounting is conservative by exactly one join-newline, and the truncation branch (`:129-170`) lands at ≤ `max_total_bytes` (checked with the 500 000-byte, 5000-`x`, and 200×`€` test cases); later files → `skipped …: size limit`. All enumerated failure modes are guarded (`f.resolve()` wrapped in `except Exception`, `relative_to` catches `ValueError`), so it never raises for any condition the spec lists or the tests exercise.
- `run_review`: `FileExistsError` refusal before any work (`:214-215`); injectable caller; real path = load `ds` → `with_idle_timeout(ds, idle_s)` → keys/pool → `chat_stream(...)` → `ds.nt.scrub` (`:230-242`), plus the `_stream_once` profile wrapper the tests require (traced through `TestStreamOnceWrapper`: key passed through, `enable_thinking=True`, `reasoning_effort` set, protected keys preserved); caller exception → `error: "<Class>: msg"`, `REVIEW FAILED: <scrubbed error>` file, verdict `NONE`, no raise (`:243-245, 271-281`); verdict read from the **last** `## Verdict:` line and normalised (READY / FIX FIRST / otherwise NONE, `:252-266`); `scrub_keys` applied to the reply before the out-file write and to every returned string incl. nested list/dict values (`:247-250, 283-288, 306-317`) — traced against `test_error_message_scrubbed_before_write` and `test_scrub_keys_removes_from_output_and_dict`.
- `main`: refusals → 2, one summary line, 0 iff status 200 and non-empty reply (any verdict), 1 otherwise (`:321-360`); traced against all five `TestMain` tests including the empty-reply-returns-1 regression.

## 3. `scripts/pipeline/stage1/crosscheck.py` (+ tests, spec `crosscheck.md`)

Files not provided in this round — nothing verifiable; no defects reported.

## 4. `scripts/pipeline/stage1/compare_a1.py` (+ tests, spec `compare_a1.md`)

Files not provided in this round — nothing verifiable; no defects reported.

## 5. `scripts/pipeline/approve.py` (+ tests, spec `approve_cli.md`)

Files not provided in this round — the "refuses non-integer ovis / `item_status` never raises" fix could not be re-verified; no defects reported.

## 6. `scripts/pipeline/check_script_cli.py` (+ tests, spec `check_script_cli.md`)

Files not provided in this round — nothing verifiable; no defects reported.

## 7. `scripts/pipeline/stage1/aggregate.py` (rule X12) and `scripts/pipeline/stage1/context.py` (`voice_genders`)

Files not provided in this round — the X12 amendment and the new ctx key could not be verified against their specs; no defects reported.

## Non-blocking notes

1. `review_run.py:56` — `root = root.resolve()` is the only unguarded call in `build_prompt`. A pathological `root` (e.g. an embedded NUL byte) would raise `ValueError` from `os.lstat` inside `realpath`, technically breaching "Never raises". No realistic input triggers it and no test requires it. Exact fix if desired: `try: root = root.resolve()\nexcept Exception: pass` (files then simply report `not under root`).
2. `review_run.py:241-245, 271-274` — in the real (caller=None) path, `info["error"]` written to the `REVIEW FAILED` file is scrubbed only against the test-injected `scrub_keys`, not against the loaded `keys` (the reply *is* scrubbed via `ds.nt.scrub`). No verified leak (it would require `draft_source` to place a key into an error message, which I cannot check without that file). Optional hardening: after the real path, also run the loaded `keys` through the `error_msg` scrub.
3. `coder_run.py:80` — `_sanitize_receipt` scrubs only keys of length ≥ 8 and only str/dict/list values (a tuple inside `usage` would pass through). Fine for real `nvapi-…` keys and the current `info` shape; note only.
4. `tests/test_coder_tools.py::test_with_idle_timeout` — the "Default (env not set) → 600" step assumes `CODER_IDLE_S` is unset but never clears it before that first check. Robustness only (the batch run passed).
5. `review_run.py:211` — `scrub_keys: list[str] = []` mutable default; never mutated by the function, so harmless; a `None` sentinel would be cleaner. Style only.
6. `review_run.py:86-89` — the secrets check also inspects **absolute** path components, so a checkout located under a directory whose name contains "secrets" would skip every file. This matches the owner's stated fix ("skips any path containing `secrets`"), so recorded as intended; flagged only in case it over-skips on such machines.
7. Unused imports: `tests/test_coder_tools.py` (`copy`, `sys`), `tests/test_review_run.py` (`shutil`, `patch`). Cosmetic.
8. `review_run.py` returns extra keys (`reply`, `error`, `effort`, `thinking`) beyond the spec's dict; the provided tests require `effort`/`thinking`, and extras are additive, so not a defect.

## Verdict: READY