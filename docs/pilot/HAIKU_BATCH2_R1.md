# Haiku review R1: Batch 2 (read-only)

Method: read `REVIEW_PROMPT_BATCH2.md`, each spec, each module and its test file. Real test results taken from `docs/pilot/TEST_RUN_BATCH2.txt` (not re-run). Every defect below was checked with a small in-memory script (no repo file written, bytecode off, temp dirs only). Skipped: `scripts/pipeline/approve.py` and `scripts/pipeline/check_script_cli.py` (absent).

## 1. coder_run (`scripts/source/coder_run.py`, `tests/test_coder_run.py`, `tests/test_coder_tools.py`)

Blocking defects:
1. `scripts/source/coder_run.py:126`: when the length retry would exceed 128000, the code `break`s before `last_reply`/`last_info` are set. The wrapper returns `("", {"attempts": 1})`, losing `status`, `finish`, `error`. The spec says the wrapper returns the LAST attempt's `(reply, info)`. Verified: `chat_stream(..., max_tokens=100000)` with a length-finish fake returns `('', {'attempts': 1})`. Fix: before the `break` on line 126 add `last_reply, last_info = reply, info`. The existing ceiling test (`test_coder_tools.py`) only checks `attempts`, so it does not catch this.
2. `scripts/source/coder_run.py:66-67` (`ProxyOpener.open`): `return self._opener.open(req, **kwargs)` discards every positional argument. The spec requires forwarding to the original opener and overriding a positional timeout. Verified: `open("U", None, 120)` on a real-signature opener reaches the inner call as `(data=None, timeout=600)`, so the caller's positional timeout is dropped with no error. Fix: `return self._opener.open(req, *args[:1], **kwargs)` (keeps a positional `data`, drops the positional timeout). Current callers use keyword `timeout=` only, so there is no visible failure today.

Non-blocking: `test_coder_tools.py` has no case for a positional argument.

## 2. review_run (`scripts/source/review_run.py`, `tests/test_review_run.py`)

Blocking defects:
1. `scripts/source/review_run.py:197-218` (and the scrub at `:222-227`): an error text from the caller is written to `out_path` before `scrub_keys` is applied to it. Verified: a caller raising `RuntimeError("auth failed for <key>")` with `scrub_keys=[<key>]` leaves the key in the out file (`REVIEW FAILED: RuntimeError: auth failed for <key>`). Fix: apply the `scrub_keys` replacement to `info["error"]` (or to `error_msg`) before line 218, not after it. This is a key leak (class 2).
2. `scripts/source/review_run.py:59-62` (`build_prompt`): only `UnicodeDecodeError` is caught around `read_text`. Verified: a `PermissionError` on read propagates out of `build_prompt`, which the spec says never raises. Fix: `except (OSError, UnicodeDecodeError)` with `problems.append(f"skipped {f}: not text")` (or a `not readable` reason).
3. `scripts/source/review_run.py:94-125` (truncation): the cut content gets `"\n[truncated]"` appended, and the `[truncated]` line gets a leading space, but the overhead on line 94-101 does not count those 13 bytes. Verified: `build_prompt("P", [file of 5000 chars], max_total_bytes=1000)` returns 1013 bytes. The spec says the cut happens at the limit. Fix: add `len(b"\n [truncated]")` (13) to `overhead`, or reduce `avail` by 13.
4. `scripts/source/review_run.py:300`: `return 0 if result["status"] == 200 else 1`. A 200 status with an empty reply is written as `REVIEW FAILED` by `run_review`, yet `main` returns 0. The spec says 1 when the call failed, and failure includes an empty reply. Verified with `run_review` stubbed to return `status=200, chars=0`: `main` returns 0. Fix: `ok = result["status"] == 200 and result["chars"] > 0`, then `return 0 if ok else 1`.

## 3. crosscheck (`scripts/pipeline/stage1/crosscheck.py`, `tests/test_stage1_crosscheck.py`)

Blocking defects:
1. `scripts/pipeline/stage1/crosscheck.py:36-38`, `:54`, `:59`, `:62-63`, `:70` (`scene_slice`): raises on odd data, though the spec says it never raises. Verified: `ovi_range: None` (TypeError), `ovi_range: ["a","b"]` (`'<=' not supported`), `line_ids: None` (`argument of type 'NoneType' is not iterable`), `scenes: None` (`'NoneType' object is not iterable`). Fix: type-check each value before use: `scenes_list` must be a list, `line_ids` must be a list, and `ovi_range` must be a list of two ints (otherwise return the empty slice). Or wrap the body in `try/except Exception` returning the empty slice.
2. `scripts/pipeline/stage1/crosscheck.py:201`: `if sc.get("scene_id")` accepts non-string ids. Verified: a scene with `"scene_id": 5` yields scene id `5`. The spec says strings only. Fix: `isinstance(sc.get("scene_id"), str) and sc.get("scene_id")`.
3. `scripts/pipeline/stage1/crosscheck.py:187-188`: a missing or unreadable document becomes `{}` with no problem recorded anywhere. The output keys are only `adhyay, advisory, note, scenes, summary` (verified). The spec says a missing document "is a problem". Fix: collect `doc_problems.append(f"missing: {unit}.json")` (or the parse error) and return it as a new key `doc_problems` in the result dict.

Non-blocking: an invalid verdict string (for example `"MAYBE"`) makes the scene `status: ok` with `verdict` not counted in pass/block/failed, so `main` returns 0. Consider `status: failed` when `parse_verdict` reports `verdict: invalid`. `run_crosscheck` raises `NotADirectoryError` (not `FileExistsError`) when `out_dir` is an existing file.

## 4. compare_a1 (`scripts/pipeline/stage1/compare_a1.py`, `tests/test_stage1_compare_a1.py`)

Blocking defects:
1. `scripts/pipeline/stage1/compare_a1.py:24-40` (`real_unfilmed`): `data.get(...)` and `item.get(...)` are unguarded. Verified: A1_rev1.json containing a top-level list raises `AttributeError`, and an `unfilmed_ranges` item that is a string raises `AttributeError`. `score()` calls this at line 110, and the spec says `score` never raises. Fix: `if not isinstance(data, dict): return result`, and `if not isinstance(item, dict): continue` in the loop.
2. `scripts/pipeline/stage1/compare_a1.py:201` (`score`): the script read is unguarded. Verified: a non-UTF-8 `docs/pilot/A1_full_script_simple.md` raises `UnicodeDecodeError` out of `score`. Fix: read it inside `try/except Exception` and treat a failure as `[]` plus a problem, as `real_scenes` does on line 47-50.
3. `scripts/pipeline/stage1/compare_a1.py:147` and `:178` (`"real"` for scenes): the value is `len(real_scenes_map)`, which is 0 when the script is missing (verified: `score()` returns `"scenes": {"trial": 0, "real": 0, ...}`). The spec gives `"real": 9` and defines `REAL_SCENES = 9`, which is unused. Fix: `"real": REAL_SCENES`.

Non-blocking: `isinstance(True, int)` lets a `true` ovi through (cosmetic). `real_scenes` calls `parse_script` outside a `try`; I did not test whether `parse_script` can raise on odd text.

## Non-blocking notes (all units)
- `review_run.run_review` returns extra keys `reply` and `error` beyond the spec list. Harmless.
- The `"secrets"` check in `review_run.build_prompt` is case-sensitive (`SECRETS.txt` is not skipped). Spec wording is literal, so this is not a defect.
- Skipped units: `approve` and `check_script_cli` (modules absent).

## Verdict counts (BLOCKING)
- coder_run: 2
- review_run: 4
- crosscheck: 3
- compare_a1: 3

## Verdict: FIX FIRST
