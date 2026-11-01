# SPEC: PATCH `scripts/source/nemotron_code.py` + `tests/test_nemotron_code.py` (checklist row N1: coder-tool safety; rev 2, 2026-11-01)

You receive the CURRENT full source of both files as reference. Output BOTH files COMPLETE (every existing function and constant must remain unless this spec says otherwise; nothing dropped or shortened). Every existing test must keep its meaning; tests may be adapted only where this spec says so. The new tests must pass.

`scripts/source/fix_loop.py` and `scripts/source/fix_loop_stable.py` import `parse_files(reply)` and `check_path(rel)` from this module: keep both names, keep `parse_files(reply)` callable with ONE argument returning `(dict, list)`, keep `check_path(rel) -> str | None`.

## ABSOLUTE OUTPUT RULE (read first)
Your reply is scanned with the regex stored in `config/codegen_policy.json` key `forbidden_text.pattern` (case-insensitive). If ANY line of either file matches it, the whole reply is refused. The current reference files contain such matches at exactly these places, and ALL of them must be gone from your output:
- `scripts/source/nemotron_code.py` line 7 (docstring), line 20 (the `FORBIDDEN_TEXT` regex literal), line 22 (one sentence of `SYSTEM`), line 47 (the refusal reason string literal).
- `tests/test_nemotron_code.py` line 22 (the test FUNCTION NAME), line 23 (the sample source string), line 25 (the expected reason string literal).
Do not spell, abbreviate, split, encode or comment on those words anywhere (code, comments, docstrings, test names, messages). Refer to them only as "the policy pattern", "the policy reason", "the policy rule", "the policy examples". Splitting a word into pieces to get past the scan is forbidden.

## The policy file (already exists; maintained by hand; you must NEVER write it)
`config/codegen_policy.json`:
```json
{"_note": "...", "version": 1,
 "forbidden_text": {"pattern": "<regex>", "ignore_case": true, "refusal_reason": "<text>", "system_rule": "<one sentence>", "refused_examples": ["<python source that must be refused>"]}}
```

## CHANGES
1. Policy loading, FAIL CLOSED.
   - `POLICY_PATH = ROOT / "config" / "codegen_policy.json"`.
   - `load_policy(path=None) -> dict` returns `{"pattern": compiled regex (re.I when ignore_case is true), "reason": str, "rule": str, "examples": list[str]}`. Raise `ValueError` with a clear message if the file is missing, unreadable, not valid JSON, `version` is not 1, any of the five `forbidden_text` keys is missing or of the wrong type (`pattern`/`refusal_reason`/`system_rule` non-empty str, `ignore_case` bool, `refused_examples` non-empty list of str), or the pattern does not compile.
   - At import, the module must NOT crash when the policy is bad (other modules import it): set `POLICY` and `POLICY_ERROR` (one is None) by calling `load_policy()` inside try/except ValueError.
   - `parse_files(reply, policy=None)`: `policy` defaults to the module `POLICY`. If no usable policy (module POLICY is None and no argument given), refuse EVERY block (and every `FILE:` header) with reason `"policy unavailable: " + POLICY_ERROR` and accept nothing. Otherwise the content check uses `policy["pattern"]` and the refusal reason is `policy["reason"]` (same text as today).
   - `SYSTEM` is built from the policy rule: where the current `SYSTEM` has its one forbidden sentence, insert `POLICY["rule"]` when POLICY is loaded, else the text `"Follow config/codegen_policy.json."`. Every other sentence of `SYSTEM` stays exactly as it is.
   - `main()`: if `POLICY` is None, raise `SystemExit("refused before any call: policy unavailable: ...")` before any network call.
   - Remove the `FORBIDDEN_TEXT` constant (it would contain the literal). Nothing else in the repository uses it.
2. Protected policy file: `check_path(rel)` returns `"protected policy file"` when the normalised relative path (forward slashes, lower case) equals `config/codegen_policy.json`. (The loop also calls `check_path`, so no coder can write it there either.)
3. Approved spec root: `SPEC_ROOTS = [ROOT / "docs" / "pilot" / "nemotron_specs"]`; `check_spec(path, roots=None)` (roots default `SPEC_ROOTS`) additionally returns `"spec outside the approved spec root"` unless the resolved path lies strictly inside a resolved root. CLI option `--spec-root` (append, default empty -> `SPEC_ROOTS`) passed to `check_spec` in `main`.
4. Code folders: `CODE_DIRS = {"scripts", "src", "tests", "schemas"}`; `check_out(path, roots, repo_root=None)` (repo_root default `ROOT`) additionally returns `"scratch folder inside a repository code folder"` when the resolved path equals or lies inside `repo_root / d` for any `d` in `CODE_DIRS`.
5. Unfinished blocks: in `parse_files`, also find every line starting with `FILE:` (regex `^FILE:\s*(\S+)`, re.M). For each header that does not begin a complete BLOCK match, append `(path, "unfinished block")` to refused (even if the same path has a complete block elsewhere). A reply with N headers and fewer than N complete blocks always has a refused entry, so `exact_set` fails.
6. Module docstring: describe the refusals as "paths outside the scratch folder, secrets, the protected policy file, anything matching config/codegen_policy.json, anything but .py/.json/.md; specs only from the approved spec root; never into repository code folders; unfinished FILE blocks refused".

## TESTS (no network; tmp_path fixtures; the test file must itself contain no policy match)
- Read the REAL policy in the test file with `json.load(open(ROOT / "config" / "codegen_policy.json"))` to get the reason and the examples; never write them as literals.
- Rename the current line-22 test to `test_good_files_pass_and_policy_code_is_refused`; it uses `policy_example = <first refused example from the real file>` and asserts the refused reasons equal `{<real refusal_reason>, "duplicate"}`.
- `load_policy` fail-closed cases, each with a tmp file: missing file; invalid JSON; `version` 2; a missing key; `ignore_case` not bool; empty `refused_examples`; a pattern that does not compile -> each raises ValueError. For these fixtures use a harmless pattern such as `"zz_forbidden_zz"`.
- `parse_files(reply, policy=<tmp policy with pattern "zz_forbidden_zz">)` refuses a block containing `zz_forbidden_zz` with that tmp policy's reason, accepts a clean block.
- Fail closed at use: monkeypatch the module's `POLICY` to None and `POLICY_ERROR` to "x"; `parse_files` of a valid reply returns `({}, [(path, "policy unavailable: x")])`.
- `check_path("config/codegen_policy.json")` and `check_path("CONFIG/codegen_policy.json")` -> "protected policy file"; `check_path("config/other.json")` -> None.
- `check_spec` refuses a valid .md outside the given roots and accepts it inside; `SPEC_ROOTS` default is `[ROOT/"docs"/"pilot"/"nemotron_specs"]`. Adapt the existing `test_spec_and_out_paths_are_checked` by passing `roots=[tmp_path]` where it expects acceptance; keep every existing assertion's meaning.
- `check_out(repo/d/"new", [repo], repo_root=repo)` refused for each d in scripts, src, tests, schemas and for `repo/d` itself; `check_out(repo/"_scratch"/"new", [repo], repo_root=repo)` accepted.
- Unfinished blocks: one valid block + a `FILE: b.py` header whose fence never closes -> `("b.py", "unfinished block")` refused and `exact_set(ok, refused, ["a.py"])` is not None; a reply whose only block is unfinished -> ok empty; a complete two-block reply still gives `exact_set(...) is None`.
- All existing tests keep passing.

HARD RULES: stdlib only; no network in tests; no Kimi; do not change `ALLOWED`, `FORBIDDEN_PART`, `MODEL`, `BLOCK`, the model call, or any public signature except the optional keyword arguments named above; no absolute drive paths; never write `config/codegen_policy.json`.

OUTPUT FORMAT (mandatory, the parser rejects anything else): reply with ONLY these two blocks, no other text. Each block is the line `FILE: <path>` followed immediately by a fenced code block that starts with ```python on its own line and ends with ``` on its own line:
FILE: scripts/source/nemotron_code.py
```python
<complete module source>
```
FILE: tests/test_nemotron_code.py
```python
<complete test source>
```
