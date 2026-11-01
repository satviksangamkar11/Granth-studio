# SPEC: FIX ROUND 2 for N1 - `tests/test_nemotron_code.py` ONLY (2026-11-01)

You receive the CURRENT full source of `scripts/source/nemotron_code.py` and `tests/test_nemotron_code.py`. 31 of 32 tests pass. Output BOTH files COMPLETE. `scripts/source/nemotron_code.py` must be returned BYTE-FOR-BYTE UNCHANGED. Same ABSOLUTE OUTPUT RULE as before: nothing in either file may match the pattern in `config/codegen_policy.json`; never write that file.

The one failing test, `test_unfinished_block_count_matches_excess_headers`, has a WRONG fixture in its second part: `reply2 = block("b.py") + "FILE: b.py\n```python\nx" + "FILE: b.py\n```python\ny"` has no newline before the third `FILE:`, so that header does not start a line and the second fence line is taken as a closing fence. Fix ONLY the fixture: `reply2 = block("b.py") + "FILE: b.py\n```python\nx\n" + "FILE: b.py\n```python\ny"`. Then compute the expected result from the CURRENT code's documented behaviour and assert it; do not change the code to fit the test. If the current code then refuses at least one `("b.py", ...)` entry and `nc.exact_set(ok2, refused2, ["b.py"])` is not None, assert exactly that instead of a fixed count of 2, and add a one-line comment that the block pattern treats a fence line that starts with three backticks as a closing fence (known limitation, out of scope).

Every other test stays unchanged. All 32 tests must pass.

OUTPUT FORMAT (mandatory): ONLY these two blocks, no other text; each is the line `FILE: <path>` then a fenced block starting with ```python on its own line and ending with ``` on its own line:
FILE: scripts/source/nemotron_code.py
```python
<complete module source, unchanged>
```
FILE: tests/test_nemotron_code.py
```python
<complete test source>
```
