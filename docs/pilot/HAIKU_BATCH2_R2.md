# Haiku review R2: Batch 2 (read-only, round 2)

Method: read `REVIEW_PROMPT_BATCH2.md`, `HAIKU_BATCH2_R1.md`, `TEST_RUN_BATCH2.txt`, the specs (`coder_tools_a.md`, `review_run.md`, `crosscheck.md`, `compare_a1.md`, `approve_cli.md`), each module, and `approvals.py`, `chapter.py`, `tests/test_approve.py`. Every claim below was checked with an in-memory script (`uv run python -B -I`, temp dirs only, no repo file written). Test results were taken from `TEST_RUN_BATCH2.txt`, not re-run. `check_script_cli` skipped as instructed.

## Round 1 defects re-verified

| R1 | Unit | Item | Status | Evidence |
|---|---|---|---|---|
| 1 | coder_run | length retry over 128000 loses last reply/info | FIXED | `coder_run.py:126` sets `last_reply, last_info` before `break`. Check: returns `('', {... finish: length, attempts: 1})`. |
| 2 | coder_run | positional timeout dropped | FIXED | `coder_run.py:67` forwards `*args[:1]`, `kwargs["timeout"]=600`. Check: `open("U", None, 120)` reaches inner as `('U', None, 600)`. |
| 1 | review_run | key from caller error written to out file | FIXED | `review_run.py:257-260` scrubs `error_msg`. Check: out file reads `REVIEW FAILED: RuntimeError: auth failed for [key]`. |
| 2 | review_run | PermissionError escapes `build_prompt` | FIXED | `review_run.py:94` catches `OSError`. Check: returns `skipped ...: not readable`, no raise. |
| 3 | review_run | truncation exceeds limit by 13 bytes | FIXED | `review_run.py:135` adds 13 to overhead. Check: 1000 bytes with `max_total_bytes=1000`. |
| 4 | review_run | 200 with empty reply returns 0 | FIXED | `review_run.py:351-352`. Check: stubbed `chars=0` gives return 1. |
| 1 | crosscheck | `scene_slice` raises on odd data | STILL OPEN (partly fixed) | `ovi_range: None`, `line_ids: None`, `scenes: None` now return an empty slice. A `null` document list still raises, see crosscheck defect 1 below. |
| 2 | crosscheck | non-string `scene_id` accepted | FIXED | `crosscheck.py:225` and `:56` require `str`. |
| 3 | crosscheck | missing document not recorded | FIXED | `crosscheck.py:212` appends to `doc_problems`; returned at `:320`. Check: empty stage1 dir gives 9 `missing or unreadable` entries. |
| 1 | compare_a1 | `real_unfilmed` raises on top-level list or string item | FIXED | `compare_a1.py:28` and `:33-34`. Check: returns `set()` in both cases. |
| 2 | compare_a1 | non-UTF-8 script raises out of `score` | FIXED | `compare_a1.py:207-212`. Check: returns a `corrupt:` problem, no raise. |
| 3 | compare_a1 | `scenes.real` is 0 without the script | FIXED | `compare_a1.py:183` uses `REAL_SCENES`. Check: `real` is 9 with the script missing. |

## 1. coder_run (`scripts/source/coder_run.py`, `tests/test_coder_run.py`, `tests/test_coder_tools.py`)

Blocking defects: none.

Non-blocking: none new.

## 2. review_run (`scripts/source/review_run.py`, `tests/test_review_run.py`)

Blocking defects: none.

Non-blocking:
- The real path's error text is already scrubbed inside draft_source (`draft_source.py:205`, `:223`, `:325`), so no key leak was found on the live path.
- The `secrets` check in `build_prompt` (`review_run.py:85`) is case-sensitive. Literal spec wording, not a defect.

## 3. crosscheck (`scripts/pipeline/stage1/crosscheck.py`, `tests/test_stage1_crosscheck.py`)

Blocking defects:
1. `scripts/pipeline/stage1/crosscheck.py:95` (`filter_by_scene_id`): `items = doc.get(list_key, [])` is not checked for type, so a document whose list is `null` raises. Verified: `scene_slice({..., "shots": {"shots": None}}, packet, "S1")` raises `TypeError: 'NoneType' object is not iterable`. The same happens with `"briefs": {"images": None}`. The spec says `scene_slice` never raises, and `run_crosscheck` would crash on one bad file. Fix: after line 95 add `if not isinstance(items, list): items = []`.

Non-blocking:
- An invalid verdict string (for example `"MAYBE"`) gives `status: ok` with the verdict counted in no bucket, so `main` can return 0. Consider `status: failed` when `parse_verdict` reports `verdict: invalid`.
- `run_crosscheck` raises `NotADirectoryError` when `out_dir` is an existing file.

## 4. compare_a1 (`scripts/pipeline/stage1/compare_a1.py`, `tests/test_stage1_compare_a1.py`)

Blocking defects:
1. `scripts/pipeline/stage1/compare_a1.py:105-135, 179, 183, 194, 203` (`score`): a missing or unreadable trial file does not produce `null` fields as the spec requires. The spec says "a missing or unreadable file gives the field `null` and an entry in `problems`". Verified with an empty trial dir: `omissions` gives `trial: 0`, `recall: 0.0`, `jaccard: 0.0`; `scenes.trial: 0`, `scene_agreement: 0.0`; `shots.trial: 0`; `images.trial: 0`. Only the problems list is correct. Fix: when `coverage_data is None`, set `trial`, `precision`, `recall`, `jaccard` to `None`; when `scenes_data is None`, set `scenes.trial` and `scene_agreement` to `None`; when `shots_data is None`, set `shots.trial` to `None`; when `briefs_data is None`, set `images.trial` to `None`. The spec test "missing trial files -> null fields" cannot pass as written.

Non-blocking:
- `isinstance(True, int)` lets a boolean ovi through (`compare_a1.py:112`, `:148`). Cosmetic.
- `parse_script` did not raise on the odd inputs tried (empty, malformed headers, huge ovi number), so `real_scenes` is not a defect.

## 5. approve (`scripts/pipeline/approve.py`, `tests/test_approve.py`)

Blocking defects:
1. `scripts/pipeline/approve.py:12-13`: `import approvals` and `import chapter` are plain imports. The spec says existing code is loaded by importlib by path. Verified in a clean process: `spec_from_file_location` on `approve.py` raises `ModuleNotFoundError: No module named 'approvals'`. The module only works when `scripts/pipeline` is already on `sys.path` or when the test pre-registers the modules. Fix: load `approvals.py` and `chapter.py` from `Path(__file__).resolve().parent` with `spec_from_file_location` and register them in `sys.modules` before use.
2. `scripts/pipeline/approve.py:186` (`main`, `omissions` branch): `int(x)` on `--ovis a` raises `ValueError: invalid literal for int()`. The `except ValueError` at `:207-212` re-raises any message not starting with `refused:`, so the CLI crashes with a traceback instead of printing `refused:` and returning 2. Verified. Fix: wrap line 186 in `try` and on `ValueError` print `refused: ovis must be integers` and return 2.
3. `scripts/pipeline/approve.py:105` (`item_status`): `approvals.load` raises `JSONDecodeError` on a corrupt `approvals.json`, and `_sha256_file` at `:109` can raise `OSError`. The spec says `item_status` never raises. Verified: a file containing `{bad` raises `JSONDecodeError`. Fix: wrap the `approvals.load` call and the `_sha256_file` call in `try/except (OSError, ValueError)`; return `"STALE"` (fail closed, never `APPROVED`).
4. `tests/test_approve.py:119-214` (refusal tests): the spec requires that each refusal writes nothing (no approvals file, no log). Only the wrong-confirm and empty-owner tests assert this. The whitespace-owner, item-with-space, empty-item, missing-file, directory and adhyay tests (`:134-214`) do not. The rule is untested for those cases. Fix: add `assert not (tmp_root / "canon" / "adhyay_02" / "approvals.json").exists()` and the same for `approvals_log.jsonl` to each of those tests.

Non-blocking:
- `approve_file` raises `AttributeError` for `owner=None` and `TypeError` for `item=None`. The spec only covers empty and whitespace strings.
- `write_omissions(2, 5, root)` raises `TypeError` for a non-list `ovis`. Not in the spec.

## Non-blocking notes (all units)
- `review_run.run_review` returns extra keys `reply` and `error`. Harmless.
- `with_idle_timeout`: a second implicit call overwrites an earlier explicit timeout (`coder_run.py:54-55`). The spec does not cover this order.
- `check_script_cli` skipped as instructed.

## Blocking defect counts
- coder_run: 0
- review_run: 0
- crosscheck: 1
- compare_a1: 1
- approve: 4

## Verdict: FIX FIRST
