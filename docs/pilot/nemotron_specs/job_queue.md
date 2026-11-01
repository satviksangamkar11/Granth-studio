# JOB SPEC: make `scripts/source/fix_loop_queue.py` and `tests/test_fix_loop_queue.py` fully green (they already exist; 8 of 23 tests fail).
The authoritative spec is `docs/pilot/nemotron_specs/fix_loop_queue.md` (reference file). Run the tests, read each failure, decide from that spec whether the module or the test is wrong, and fix that side (known: `TestMain::test_output_lines` fails with a TypeError; keep every passing test). The module must also have the script entry point `if __name__ == "__main__": raise SystemExit(main())`. Never write any word related to 3D animation software.
Reply with only the FILE blocks: FILE: scripts/source/fix_loop_queue.py and FILE: tests/test_fix_loop_queue.py (both complete).

FORMAT (mandatory): each file is a line 'FILE: path', then a line with three backticks plus python, the COMPLETE file, then a line with three backticks. Replies without the fenced blocks are discarded.


SUPERVISOR DIAGNOSIS (escalation opinion): the remaining failures are a TEST bug. The fixture/helper write_valid_job writes job_a_spec.md into tmp_root which is never created (FileNotFoundError). Fix the TEST only: create tmp_root (mkdir parents, exist_ok) in the tmp_root fixture and the jobs dir in tmp_jobs_dir, before any write. Change the module only if a corrected test still fails and the spec requires it. Keep the FORMAT rule above.

