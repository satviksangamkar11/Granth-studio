# Read-only review (do NOT edit any file except your own report). Batch 2 of the owner's "finish the partly-done checklist rows" work.

Units under review (module + tests + spec = the only authority):
- `scripts/source/coder_run.py` + `tests/test_coder_run.py` + `tests/test_coder_tools.py`: spec `docs/pilot/nemotron_specs/coder_tools_a.md` (thinking ON default, idle-timeout proxy, bounded continuation on finish=length, receipts).
- `scripts/source/review_run.py` + `tests/test_review_run.py`: spec `docs/pilot/nemotron_specs/review_run.md` (read-only GLM reviewer tool; never prints a key; skips secrets files).
- `scripts/pipeline/stage1/crosscheck.py` + `tests/test_stage1_crosscheck.py`: spec `crosscheck.md` (advisory per-scene second opinion, never repairs).
- `scripts/pipeline/stage1/compare_a1.py` + `tests/test_stage1_compare_a1.py`: spec `compare_a1.md` (scores a trial against the real Adhyay 1 split).
- `scripts/pipeline/approve.py` + `tests/test_approve.py`: spec `approve_cli.md` (the ONLY approval write path), if present.
- `scripts/pipeline/check_script_cli.py` + `tests/test_check_script_cli.py`: spec `check_script_cli.md`, if present.
Real test results are in `docs/pilot/TEST_RUN_BATCH2.txt` (run outside your sandbox; trust it).

## STOP RULE (what READY means; the owner wants no over-engineering)
READY = no verified CLASS 1 defect (a spec rule not implemented or implemented wrongly), no verified CLASS 2 defect (any of the public functions can RAISE on odd input where the spec says it never raises, or any key/secret can be printed, logged or stored), and no verified CLASS 3 defect that leaves a spec rule with no failing test. Style, extra hardening and missing nice-to-have tests are NON-blocking notes. Verify every claim with a small in-memory check; never guess.

## Output
Markdown ending with exactly one line `## Verdict: READY` or `## Verdict: FIX FIRST`; per unit a numbered list of BLOCKING defects (file:line, what, exact fix) or `none`; then `## Non-blocking notes`.


## UPDATE for the FINAL round (all units now exist)
Additional units: `scripts/pipeline/approve.py` (spec `approve_cli.md`), `scripts/pipeline/check_script_cli.py` (spec `check_script_cli.md`), and two CHANGED existing units: `scripts/pipeline/stage1/aggregate.py` (new rule X12: cast gender vs ctx `voice_genders`; spec `docs/pilot/nemotron_specs/aggregate.md`, the AMENDMENTS section at the end is authoritative; rules X1, X3-X11 unchanged and X2 does NOT exist on purpose) and `scripts/pipeline/stage1/context.py` (new ctx key `voice_genders`; spec `context.md`). Earlier findings that were fixed: receipts scrub keys passed to chat_stream; the reviewer tool skips any path containing `secrets`, keeps file content verbatim and normalises the verdict; null lists no longer crash crosscheck or compare_a1; approve refuses non-integer ovis and never raises in item_status. Do NOT re-report anything already fixed; report only BLOCKING defects per the STOP RULE.
