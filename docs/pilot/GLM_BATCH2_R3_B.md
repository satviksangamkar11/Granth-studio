# Batch 2 — final-round read-only review

Coverage note: only `crosscheck.py` (+ tests + spec) and `compare_a1.py` (+ tests + spec) were included in this round. The other units named in the update (`coder_run.py`, `review_run.py`, `approve.py`, `check_script_cli.py`, `aggregate.py`, `context.py`) were **not** provided as files, so nothing about them could be verified here; per the stop rule I report no defects for them (only verified defects block).

## scripts/pipeline/stage1/crosscheck.py + tests/test_stage1_crosscheck.py

1. **BLOCKING (CLASS 3 — leaves a spec rule with no failing test).** `tests/test_stage1_crosscheck.py:255-258` (the byte-compare loop in `test_run_crosscheck_fake_caller`):
   ```python
   result = crosscheck.run_crosscheck(2, stage1_dir, root, fake_caller, out_dir)   # line 242
   ...
   for unit in ["story_map", "coverage", "scenes", "shots", "briefs", "looks", "voices", "sounds", "questions"]:
       before = (stage1_dir / f"{unit}.json").read_bytes()
       after = (stage1_dir / f"{unit}.json").read_bytes()
       assert before == after
   ```
   Both reads happen **after** `run_crosscheck` has finished, so the assertion compares a file to itself and can never fail. The spec (module header "It NEVER repairs, edits or rewrites anything"; test item 4 "the stage1 documents on disk unchanged (compare bytes before/after)") is therefore left with **no effective test**: if `run_crosscheck` rewrote/normalized any of the nine documents, the whole suite would still pass. Verified by reading the code — no other test in the file touches the stage1 docs after a run.
   **Exact fix:** snapshot before the call and compare against the snapshot:
   ```python
   units = ["story_map", "coverage", "scenes", "shots", "briefs", "looks",
            "voices", "sounds", "questions"]
   before = {u: (stage1_dir / f"{u}.json").read_bytes() for u in units}

   result = crosscheck.run_crosscheck(2, stage1_dir, root, fake_caller, out_dir)
   ...
   for unit in units:
       assert (stage1_dir / f"{unit}.json").read_bytes() == before[unit]
   ```

Otherwise the unit conforms to the spec: `CHECK_RULES` verbatim; `scene_slice` guards every odd shape (None/`["a","b"]` ranges, None `line_ids`, non-dict docs, non-string scene ids) and never enumerates; `build_check_prompt` role+rules+output paragraph and compact `ensure_ascii=False` user; `parse_verdict` implements the own first-`{`-to-last-`}` parse with all four problem kinds; `run_crosscheck` records `doc_problems`, per-scene failed reasons, dry-run, `FileExistsError` on non-empty out_dir, `only_scenes`, exact summary/note keys; `main` flags, prints and exit code match; no key/secret handling. No CLASS 1/2 defect found.

## scripts/pipeline/stage1/compare_a1.py + tests/test_stage1_compare_a1.py

none

(Verified: `real_unfilmed` guards top-level lists, string items, non-int ends (`type(...) is int`, so booleans are rejected), >5000-wide ranges; `real_scenes`/`score` never raise on missing/corrupt/non-UTF-8 inputs and record problems; `scenes.real` is the `REAL_SCENES = 9` constant; covered fractions use membership tests, no enumeration; rounding, receipt refusal/return-2, and all spec-mandated test cases are present and non-vacuous.)

## Non-blocking notes

- `scripts/pipeline/stage1/crosscheck.py:4,6` — `import sys` and `from typing import Any` are unused.
- `crosscheck.run_crosscheck`: a reply whose JSON parses but has an invalid/missing `verdict` (e.g. `"MAYBE"`) is recorded `status: "ok"` with the raw verdict string; it counts in neither pass/block/failed and `main` exits 0 (only `parse_problems` flags it). The spec's schema says `verdict` is `PASS|BLOCK|None`; consider coercing to `None` (or `failed`) when `parse_problems` is non-empty.
- `crosscheck.py:187` — if `out_dir` exists as a regular **file**, `out_path.iterdir()` raises `NotADirectoryError` instead of the spec's `FileExistsError`; similarly a `scene_id` containing `/` would raise on the prompt/reply write. Both are outside the spec's "data or model problems" scope (its own `<scene_id>.txt` layout assumes filename-safe ids) — noting only.
- `scene_slice` uses `isinstance(x, int)` for `ovi_range`/`ovi`, so booleans pass (`True == 1`); `compare_a1` consistently uses the stricter `type(x) is int`. No raise and no realistic impact with the owner's data.
- `tests/test_stage1_crosscheck.py:27` loads `runner.py` but never uses it; `test_main_dry_run` mutates `sys.argv` without restoring. Harmless in this suite.
- `compare_a1.py:10` — `sys.path.insert(...)` at module top is an import-time side effect (spec: "nothing at import time except imports and definitions"); importlib-by-path would match the sibling units. Benign.
- `compare_a1.real_unfilmed`: a missing/corrupt `canon/story_split_edits/A1_rev1.json` is silently treated as "no real unfilmed ovis" (`omissions.real = 0`, `recall` null) with no entry in `problems`; the null+problems rule is implemented only for the four trial files (which matches the spec's test list). A problem entry for the missing real file would be nicer.
- `compare_a1.score()` — `real_scene_count` is assigned and never used.
- `compare_a1` never reads `canon/drafts/A1_flow_shot_jobs.json`; `images.real` is the constant 59 — consistent with the spec's return schema (`"real": 59`), noted in case the count should later be read from the file.

## Verdict: FIX FIRST