# SPEC: FIX ROUND 3 for N1 - `scripts/source/nemotron_code.py` + `tests/test_nemotron_code.py` (2026-11-01, Codex BLOCKING finding)

You receive the CURRENT full source of both files; all 32 tests pass. Output BOTH files COMPLETE; change only what is listed. Same ABSOLUTE OUTPUT RULE as before: nothing in either file may match the pattern in `config/codegen_policy.json`; never write that file.

DEFECT (proven): `load_policy` checks `data.get("version") != 1`. Python treats `True == 1` and `1.0 == 1`, so a policy with `"version": true` or `"version": 1.0` is ACCEPTED instead of failing closed.

FIX: accept the version only when `type(data.get("version")) is int` and it equals 1 (a bool is not accepted, a float is not accepted); otherwise raise ValueError("policy version must be the integer 1, got ...").

TESTS to add (each must FAIL on the current code and PASS after the fix; tmp_path only): `load_policy` raises ValueError for `"version": true`, `"version": 1.0`, `"version": "1"`; a policy identical to the real one with `"version": 1` still loads. All 32 existing tests keep passing unchanged.

HARD RULES: stdlib only; no network; no other behaviour change.

OUTPUT FORMAT (mandatory): ONLY these two blocks, no other text; each is the line `FILE: <path>` then a fenced block starting with ```python on its own line and ending with ``` on its own line:
FILE: scripts/source/nemotron_code.py
```python
<complete module source>
```
FILE: tests/test_nemotron_code.py
```python
<complete test source>
```
