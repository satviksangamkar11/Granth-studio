# Batch 2 — FINAL round review (read-only)

Reviewable this round from the provided materials: `approve.py` + tests + spec, `check_script_cli.py` + tests + spec, `context.py` + tests + spec. `scripts/pipeline/stage1/aggregate.py` (rule X12), its spec AMENDMENTS and its tests were **not included** in the provided files, so X12 could not be verified in either direction (see unit entry and notes). Earlier-batch units were not re-opened per the update (fixes declared done; trusted `TEST_RUN_BATCH2.txt`).

## scripts/pipeline/approve.py + tests/test_approve.py (spec `approve_cli.md`)

none

(All refusal branches, the single write path, log append semantics, `item_status` never-raise paths reachable from the given code, `write_omissions` validation/existence refusal, `main` outputs/return codes, and the no-`input(`/no-`subprocess` source rule check out against the spec.)

## scripts/pipeline/check_script_cli.py + tests/test_check_script_cli.py (spec `check_script_cli.md`)

1. **CLASS 2 — `run_check` can raise; the spec says "NEVER raises".**
   - `scripts/pipeline/check_script_cli.py:66` guards only `script_path.exists()`. A **directory** placed at `chapter_paths(...)["script"]` passes that guard and reaches `read_text` at `:81`, which raises `IsADirectoryError` (POSIX) / `PermissionError` (Windows).
   - `scripts/pipeline/check_script_cli.py:81` `script_path.read_text(encoding="utf-8")` raises `UnicodeDecodeError` for any non-UTF-8 bytes at the script path.
   Both are odd but trivially reachable inputs (e.g. `mkdir canon/adhyay_02/script/easy.md`, or one bad byte in the script), and the spec's contract for `run_check` is explicitly "NEVER raises".
   **Exact fix:** at `:66` change the guard to `if not script_path.is_file():` (keeps the `script: missing` problem and the same empty-result dict), and wrap the read at `:81`:
   ```python
   try:
       script_text = script_path.read_text(encoding="utf-8")
   except (OSError, UnicodeDecodeError) as e:
       own_problems.append(f"script: unreadable ({e.__class__.__name__})")
       return {
           "adhyay": adhyay,
           "script": script_rel,
           "script_sha256": "",
           "lines": 0,
           "scenes": 0,
           "core": 0,
           "optional": 0,
           "errors": [],
           "problems": own_problems,
           "ok": False,
       }
   ```

2. **CLASS 1 — `main` crashes instead of returning 1 when `--write-receipt` is combined with an invalid adhyay.** Spec: "Returns 0 when ok, 1 otherwise." For `--adhyay 999 --write-receipt`, `run_check` correctly returns `ok=False`, but `main` (`scripts/pipeline/check_script_cli.py:171-177`) then calls `write_receipt`, whose `chapter_paths(adhyay, root)` (`:129`) raises `ValueError` for an adhyay outside 1..21 (stated in both specs and proven by `test_invalid_adhyay` passing through that exact branch). Only `FileExistsError` is caught (`:175`), so the `ValueError` escapes and `main` dies with a traceback instead of returning a code.
   **Exact fix:** add one branch after the `FileExistsError` handler at `:175`:
   ```python
   except ValueError as e:
       print(f"refused: {e}")
       return 2
   ```
   (`2` is the refusal code the spec already assigns in `main` for an existing receipt; `write_receipt` can raise nothing else but `FileExistsError` and this `ValueError`.)

## scripts/pipeline/stage1/context.py + tests/test_stage1_context.py (spec `context.md` + `voice_genders` amendment)

none

(`build_ctx` never raises on any path in the given code; invalid adhyay → `({}, ["adhyay must be an int in 1..21"])` with the strict `type(adhyay) is not int` check; every source read is wrapped and becomes `<source>: <detail>`; `voice_genders` is populated exactly as the amendment/tests require — only string `voice_key`s with `gender` exactly `"male"`/`"female"`, `{}` on missing/bad library, `extra` override applied last; `main` output/refusal/return codes match.)

## scripts/pipeline/stage1/aggregate.py (rule X12, spec `aggregate.md` AMENDMENTS)

Not reviewable: the module, the AMENDMENTS text and its tests were not provided in this round's materials. No defect can be claimed and none can be ruled out. `context.py` does supply `ctx["voice_genders"]` in the shape the amendment needs (see above), so the consumer side's input exists; the aggregate side itself is unverified.

## Non-blocking notes

- **aggregate.py / X12:** please include the file (plus the AMENDMENTS section and its tests) if you want a verdict on rule X12; it is the only listed unit with zero verification this round.
- `approve.item_status` (`approve.py`, the `try: approvals_dict = approvals.load(...)` block) relies on `approvals.status` tolerating whatever `approvals.load` returns for a valid-JSON-but-not-an-object `approvals.json`. `context.py` defensively coerces non-dict loads to `{}`; `approve.py` does not. If `approvals.status` assumes a dict (e.g. calls `.get`), `item_status` could raise `AttributeError`, violating "Never raises". Unverifiable without `approvals.py`; the one-line mirror of context.py (`if not isinstance(approvals_dict, dict): approvals_dict = {}`) would remove the doubt.
- `test_approve_file_happy_path` compares the recorded sha via `approvals.sha256_file` rather than the spec's independent `hashlib.sha256(bytes).hexdigest()`. The rule is still guarded (a wrongly recorded sha would fail), but the check is not independent as specified.
- Missing nice-to-have tests (non-blocking per the brief): `main` default root = repo root (approve, check_script_cli — deliberately untested to avoid touching the real repo); log `file` field for a file outside root (name-only branch); check_script_cli's 40-error cap and `... and <k> more` line, `--extra-voice`, `glossary` parameter, receipt folder creation; context's bool-`ovi` jsonl line and plain-list sound palette.
- `context.md` says "Missing or unreadable library → … the problem `voice_library: missing`", while the implementation reports `voice_library: <ExceptionClass>` for unreadable/bad JSON (consistent with the spec's general `<source>: <ExceptionClass>` rule) and reserves `missing` for absence. The tests lock the implemented behavior; ambiguous spec sentence, no action needed.
- `test_approve.py`'s `main` tests reassign `sys.argv` without saving/restoring; harmless here (each test sets it fully before calling `main`), just fragile style.

## Verdict: FIX FIRST