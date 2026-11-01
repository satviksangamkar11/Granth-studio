# JOB SPEC: make `scripts/source/codex_review.py` and `tests/test_codex_review.py` fully green (they already exist; 20 of 21 tests pass).
The authoritative spec for the module is `docs/pilot/nemotron_specs/codex_review.md` (reference file). The ONE failing test is `test_run_codex_review_secrets_skipped`. Supervisor diagnosis: the module is correct; the test calls `run_codex_review(prompt_file, [normal_file, secret_file], out_path, runner=fake_runner)` WITHOUT `root=tmp_path`, so the default root (the repo) makes the tmp files count as outside the root and they are skipped. Fix the TEST: pass `root=tmp_path`, assert the normal file text IS in the captured runner input and the secret text `SUPER_SECRET` is NOT; check every other test that passes files for the same missing `root=`. Change the module only if a corrected test still fails and the spec requires it. Never write any word related to 3D animation software.
Reply with only the FILE blocks: FILE: scripts/source/codex_review.py and FILE: tests/test_codex_review.py (both complete).

FORMAT (mandatory): each file is a line 'FILE: path', then a line with three backticks plus python, the COMPLETE file, then a line with three backticks. Replies without the fenced blocks are discarded.


SUPERVISOR DIAGNOSIS (Sonnet 5.5 high review, authoritative; it REPLACES the earlier diagnosis above, which was wrong):
# Diagnosis a_codex_review (pytest: 20 passed, 1 failed)
Failing: tests/test_codex_review.py::test_run_codex_review_secrets_skipped
Assertion that fails (line 224): "print('ok')" in captured_input["text"]  -> text is only 'Review.'
Secret check passes (SUPER_SECRET absent); the NORMAL file is wrongly dropped too.

ROOT CAUSE (verified in scripts/source/review_run.py lines 85-93): build_prompt flags a file as
secret when "secrets" occurs (case-insensitive) in ANY part of rel.parts + the ABSOLUTE path parts.
pytest builds tmp_path from the test function name, so the directory is
.../test_run_codex_review_secrets_0, which contains "secrets". Every file under tmp_path is
therefore skipped as "secrets", including normal.py. This is a test-design bug, not a module bug.

The earlier supervisor diagnosis (missing root=) is WRONG: the test already passes root=tmp_path.
The module is correct against spec: it filters .secrets dirs, calls build_prompt, uses the runner,
parses verdict, writes REVIEW FAILED file, returns codes 0/1/2. Do NOT change codex_review.py
(review_run.py must not be changed either; its absolute-path rule is existing behaviour).

WHAT THE CODER MUST CHANGE (TEST only, tests/test_codex_review.py):
1. Make the temp root path free of the substring "secrets". Easiest: in this one test take
   tmp_path_factory instead of tmp_path and use a neutral directory name:
       base = tmp_path_factory.mktemp("rcr")      # dir name "rcr0", no "secrets"
   then replace every tmp_path in this test with base (prompt.txt, report.md, .secrets/,
   normal.py, root=base).
   (Alternative: rename the test to e.g. test_run_codex_review_skips_hidden_dirs and keep tmp_path;
   pytest truncates tmp dir names to 30 chars, so the name must not contain "secrets" in its first
   30 characters.)
2. Keep: the ".secrets" subfolder, secret text SUPER_SECRET, root=base, and both assertions
   (SUPER_SECRET not in text; "print('ok')" in text). Optionally also assert
   any("secrets" in p for p in result["problems"]).
3. Add a short comment explaining why the temp dir name must avoid "secrets".
No other test needs a change; all other tests pass and none depend on this rule.

Remember the FORMAT rule.
