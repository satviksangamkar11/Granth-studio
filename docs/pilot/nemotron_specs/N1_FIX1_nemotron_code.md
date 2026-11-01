# SPEC: FIX ROUND for N1 - `scripts/source/nemotron_code.py` + `tests/test_nemotron_code.py` (2026-11-01)

You receive the CURRENT full source of both files (the N1 version, all 25 tests pass). Output BOTH files COMPLETE; keep every function, constant and test; change only what is listed. Same ABSOLUTE OUTPUT RULE as before: nothing in either file may match the pattern in `config/codegen_policy.json` (refer to it only as "the policy pattern"); never write that file.

Claude's review found three defects, each proven by running the current code:

1. BYPASS of the protected policy file. `check_path("./config/codegen_policy.json")`, `check_path("config//codegen_policy.json")` and `check_path("config/./codegen_policy.json")` all return None today. Fix: compare the NORMALISED parts, not the raw string: `"/".join(x for x in Path(rel.replace("\\", "/")).parts if x not in ("", ".")).lower() == "config/codegen_policy.json"`. Keep the absolute-path and parent-folder checks first, as now.
2. NOT FAIL-CLOSED. `load_policy` lets other exceptions escape: a directory path raises PermissionError/IsADirectoryError, an unreadable file raises OSError, and valid JSON that is not an object (for example `[1, 2]`) raises AttributeError. Fix: catch `OSError` (and `UnicodeDecodeError`) around reading and turn it into ValueError("policy file unreadable: ..."); after json.loads, if the result is not a dict raise ValueError("policy file must be a JSON object"). Every failure of load_policy must be a ValueError, so the module-level try/except always sets POLICY = None and POLICY_ERROR instead of crashing the import.
3. SPEC DEVIATION. An unfinished `FILE:` header is currently not refused when the same path also has a complete block elsewhere. Fix: count headers per path (regex `^FILE:\s*(\S+)`, re.M, keep order) and count complete BLOCK matches per path; for each path, append `(path, "unfinished block")` once for every header beyond the number of complete blocks for that path.

TESTS to add (each must FAIL on the current code and PASS after the fix; no network; tmp_path only):
(a) parametrized: "./config/codegen_policy.json", "config//codegen_policy.json", "config/./codegen_policy.json", "CONFIG/./Codegen_Policy.json" -> "protected policy file"; "config/other.json" and "configx/codegen_policy.json" -> None.
(b) `load_policy(tmp_path)` (a directory) raises ValueError; `load_policy(<file containing [1, 2]>)` raises ValueError; `load_policy(<file with invalid UTF-8 bytes b"\xff\xfe">)` raises ValueError.
(c) a reply with a complete `a.py` block followed by a second `FILE: a.py` header whose fence never closes -> refused contains ("a.py", "unfinished block") and `exact_set(ok, refused, ["a.py"])` is not None.
All 25 existing tests keep passing unchanged.

HARD RULES: stdlib only; no network in tests; no Kimi; no other behaviour change; no absolute drive paths; never write `config/codegen_policy.json`.

OUTPUT FORMAT (mandatory): reply with ONLY these two blocks, no other text. Each block is the line `FILE: <path>` followed immediately by a fenced code block that starts with ```python on its own line and ends with ``` on its own line:
FILE: scripts/source/nemotron_code.py
```python
<complete module source>
```
FILE: tests/test_nemotron_code.py
```python
<complete test source>
```
