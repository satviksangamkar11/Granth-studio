# Batch 2 read-only review

Scope note: only three units were actually included in the payload (`crosscheck`, `compare_a1`, `approve`). `coder_run.py`, `review_run.py` and `check_script_cli.py` (+ their tests/specs) were not pasted, so they could not be reviewed and no claim is made about them. All findings below are verified by semantic trace of the pasted sources against the pasted specs (the raising paths are plain Python iteration semantics: `for x in None` / `for x in 5` raise `TypeError`, and `dict.get(k, default)` returns `None` — not the default — when the key exists with a `null` JSON value).

## scripts/pipeline/stage1/crosscheck.py (+ tests/test_stage1_crosscheck.py)

1. **`scene_slice` raises `TypeError` on odd data — spec says "never raises" (CLASS 2, and CLASS 3: no failing test).** `scripts/pipeline/stage1/crosscheck.py:95-97`: `items = doc.get(list_key, []) if isinstance(doc, dict) else []` is iterated (`for item in items:`) without a list check. If `shots.json` contains `{"adhyay": 2, "shots": null}` (or a number), `docs["shots"]` parses fine, `doc.get("shots", [])` returns `None` (key exists), and `for item in None` raises `TypeError`, both from `scene_slice` directly and out of `run_crosscheck` (which calls `scene_slice` unguarded at line 231). Same hole for `briefs`/`sounds`/`questions`. Fix (mirrors the guard already applied to `scenes_list` at lines 49-50):
   ```python
   items = doc.get(list_key, []) if isinstance(doc, dict) else []
   if not isinstance(items, list):
       items = []
   ```
   Add a case to `test_scene_slice_odd_data_no_raise` with `bad_docs["shots"] = {"shots": None}`.

2. **`run_crosscheck` raises `TypeError` on odd data — spec says "NEVER raises for data or model problems" (CLASS 2, and CLASS 3: no failing test).** `scripts/pipeline/stage1/crosscheck.py:224-225`: `scenes_list = scenes_doc.get("scenes", []) if isinstance(scenes_doc, dict) else []` is fed straight into `[sc.get("scene_id") for sc in scenes_list ...]`. A `scenes.json` containing `{"adhyay": 2, "scenes": null}` (or a number/bool) makes `scenes_list = None` and the comprehension raises `TypeError`. Note `scene_slice` guards exactly this (lines 49-50) but `run_crosscheck` re-derives `scenes_list` unguarded. Fix, after line 224:
   ```python
   if not isinstance(scenes_list, list):
       scenes_list = []
   ```
   Add a `run_crosscheck` test with `scenes.json` = `{"adhyay": 2, "scenes": null}` asserting it completes with zero scenes and a `doc_problems`-style record (or at least does not raise).

## scripts/pipeline/stage1/compare_a1.py (+ tests/test_stage1_compare_a1.py)

1. **`score` raises `TypeError` on odd data — spec says "`score(trial_dir, root) -> dict`: NEVER raises" (CLASS 2, and CLASS 3: no failing test).** `scripts/pipeline/stage1/compare_a1.py:31-32`: `unfilmed_ranges = data.get("unfilmed_ranges", [])` is iterated (`for item in unfilmed_ranges:`) without a list check. `A1_rev1.json` containing `{"unfilmed_ranges": null}` or `{"unfilmed_ranges": 5}` → `TypeError`, propagated out of `score` via the unconditional `real_omissions = real_unfilmed(root)`. The sibling guards exist (non-dict top level at line 28, non-dict items at line 33, non-int ends at line 39) — only the list-level guard is missing. Fix, after line 31:
   ```python
   if not isinstance(unfilmed_ranges, list):
       unfilmed_ranges = []
   ```
   Add a regression test (scalar/`null` `unfilmed_ranges` → empty set, `score` completes).

## scripts/pipeline/approve.py (+ tests/test_approve.py)

none

## Not reviewed (not in payload)

`scripts/source/coder_run.py` + tests + `coder_tools_a.md`; `scripts/source/review_run.py` + tests + `review_run.md`; `scripts/pipeline/check_script_cli.py` + tests + spec. No verdict possible for these units from the material provided.

## Non-blocking notes

- **crosscheck tests**: in `test_run_crosscheck_fake_caller`, the "stage1 documents unchanged" check reads `before` and `after` *after* `run_crosscheck` has already run, so it cannot detect a mid-run write. Snapshot `before` before the call. (The code itself has no write path into `stage1_dir`, so the spec rule holds.)
- **crosscheck.py:121-122**: `build_check_prompt` prepends a role sentence identical to the first line of `CHECK_RULES`, so every prompt carries the sentence twice. Cosmetic; costs tokens.
- **crosscheck.py:185 / 234**: pathological inputs not covered by the spec: `out_dir` existing as a regular file makes `any(out_path.iterdir())` raise `NotADirectoryError` (not the spec'd `FileExistsError`), and a `scene_id` containing `/` would break the prompt/reply file writes. Optional hardening only.
- **compare_a1**: `canon/drafts/A1_flow_shot_jobs.json` is created by the tests and named as a spec input, but never read — `images.real` is the constant `59`, which is exactly what the API section specifies. Harmless.
- **compare_a1.py:52-57**: `real_scenes` calls `parse_script(text)` outside its `try/except`, while the core-lines path in `score` wraps the same call in one. If `parse_script` can raise on odd text, `score` would propagate it; wrapping it would make the two paths symmetric (could not be verified — `check_script.py` source not provided).
- **approve.py**: `main` prints `refused: refused: <path> already exists` on the `FileExistsError` path, because `write_omissions`' message already starts with `refused:` and `main` prepends another. Cosmetic.
- **approve.py (`main`, omissions)**: `--ovis abc` crashes with a traceback (`int(x)` `ValueError` is re-raised because it doesn't start with `refused:`) instead of a clean refusal. Argparse itself exits 2 for a bad `--adhyay`, so parse-level errors sit outside the spec's refusal clause; a `try/except` or `type=` converter would make it consistent.
- **approve.py (`item_status`)**: its "never raises" guarantee depends on `approvals.load` tolerating a corrupt (non-JSON) `approvals.json`; `approvals.py` source was not provided, so this could not be verified.

## Verdict: FIX FIRST