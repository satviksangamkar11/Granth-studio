# SPEC: FIX ROUND 4 for N1 - `scripts/source/nemotron_code.py` + `tests/test_nemotron_code.py` (2026-11-01, Codex BLOCKING finding)

You receive the CURRENT full source of both files; all 36 tests pass. Output BOTH files COMPLETE; change only what is listed. Same ABSOLUTE OUTPUT RULE as before: nothing in either file may match the pattern in `config/codegen_policy.json`; never write that file.

DEFECT (proven): a valid but deeply nested JSON policy (for example 100000 `[` then 100000 `]`) makes `json.loads` raise RecursionError. `load_policy` only converts some errors to ValueError, so the import-time `except ValueError` misses it and importing the module crashes instead of setting POLICY = None.

FIX (close the whole class, not one more exception): keep every existing check and message, but make `load_policy` guarantee that EVERY failure is a ValueError: wrap its body so that any exception that is not already a ValueError (for example RecursionError, MemoryError excluded, OSError, TypeError, AttributeError) is re-raised as `ValueError(f"policy unusable: {type(e).__name__}: {e}")` chained with `from e`. Also make the module-level try/except catch `Exception` (not only ValueError) and set POLICY = None and POLICY_ERROR to the message, so importing this module can never crash on a bad policy. Do not catch BaseException (KeyboardInterrupt/SystemExit must still propagate).

TESTS to add (each must FAIL on the current code and PASS after the fix; tmp_path only): `load_policy` raises ValueError for a file of 100000 `[` followed by 100000 `]`; `load_policy` raises ValueError when `forbidden_text.pattern` is valid JSON but the regex compile raises a non-re.error exception is NOT needed (skip); a monkeypatched `json.loads` that raises TypeError inside load_policy yields ValueError. All 36 existing tests keep passing unchanged.

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
