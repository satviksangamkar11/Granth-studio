# Read-only review: Stage 1 unit modules (do NOT edit any file)

Review these nine modules and their tests against their specs. The spec is the only authority.

- Modules: `scripts/pipeline/stage1/{story_map,coverage,scenes,shots,briefs,looks,voices,sounds,questions}.py`
- Tests: `tests/test_stage1_<unit>.py` (nine files)
- Specs: `docs/pilot/nemotron_specs/unit_<unit>.md`, shared base `docs/pilot/nemotron_specs/stage1_base.json`
- Rules context: `docs/pilot/STAGE1_RULES.md`
- Round 9: this is the ninth review. Earlier reports: `docs/pilot/*_STAGE1_UNITS_ROUND1.md` and `*_ROUND2*.md`; the coder applied fixes to story_map, scenes, shots, briefs, voices, sounds (each validate has a catch-all guard; round 9 fixes (tests only): scenes reversed-range test isolated; briefs collateral missing-scene row removed). Check each Round 8 finding is really fixed (reproduce it), then look for new defects. The test suite is green (460 pass).

KNOWN DESIGN RULE (do not report): the catch-all sentinel text `malformed structure` is project-defined (see `docs/pilot/STAGE1_RULES.md`, section "Catch-all sentinel"); tests assert it absent on purpose.

Find only REAL, verified defects, in these classes:
1. A spec rule (schema rule, enum, conditional, required field, extra-key rule, semantic rule) that the module does not implement.
2. `validate` or `schema_errors` that can RAISE (KeyError, TypeError, AttributeError) on a malformed or partial document instead of returning errors.
3. A test that can never fail (no-op mutation, assertion always true), a test that fails for a collateral reason, or a spec rule with no isolated failing test.
4. Wording asserted in a test that the spec does not quote.
5. Any place a key or secret could be printed or stored.

Output (write only your own report file): a markdown report with `## Verdict: READY | FIX FIRST`, then per unit a numbered defect list (file:line, what is wrong, exact fix) or `none`. Be short and precise. No praise, no rewriting of files.
