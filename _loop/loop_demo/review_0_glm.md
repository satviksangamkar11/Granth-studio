# Final review — loop_demo proof job (read-only)

**Scope note:** The only files present in this round's payload are `scripts/source/loop_demo.py`, `tests/test_loop_demo.py`, and their spec `docs/pilot/nemotron_specs/loop_demo.md`. None of the Stage 1 files (`aggregate.py`, `context.py`, the nine units) were included, so per the "verify every claim, do not guess" rule no claims are made about them here; this report covers the provided proof job against its spec, which is the only authority for it.

**Verification (in-memory simulation of every test assertion against the live code):**

- `word_count`: `""`→0, `"   \t\n  "`→0 (`str.split()` on whitespace-only yields `[]`), `"hello world"`→2, `"one two three"`→3, `"  leading and trailing  "`→3 (`split()` ignores leading/trailing and collapses runs), `None`/`123`/`["a","b"]`→0 via the `isinstance` guard (scripts/source/loop_demo.py:6-8). Matches spec "counts whitespace-separated words (a non-string returns 0)".
- `clean_ids`: non-list inputs `"not a list"`, `123`, `None`, `{"a":1}` all hit the `isinstance(items, list)` guard → `[]` (scripts/source/loop_demo.py:16-17); `[1,"a",None,"b",2.5]`→`["a","b"]` (non-strings skipped at loop_demo.py:19-20); `["   ","\t","\n"]`→`[]` (strip-to-empty skipped at loop_demo.py:20-21); duplicates `["a","b","a","c","b"]`→`["a","b","c"]` via set + `sorted` (loop_demo.py:18,22); order `["z","a","m"]`→`["a","m","z"]`; stripped inputs `["  a  "," b ","c "]`→`["a","b","c"]`. Matches spec exactly.
- Import-time: module contains only the required `from __future__ import annotations` and two function definitions — "nothing at import time except definitions" satisfied.
- Test harness: `Path(__file__).resolve().parents[1] / "scripts" / "source" / "loop_demo.py"` resolves to `<repo>/scripts/source/loop_demo.py` (tests/test_loop_demo.py:8), loaded via `spec_from_file_location` + `module_from_spec` + `exec_module` (tests/test_loop_demo.py:9-11) — exactly the spec-required importlib-by-path pattern; no `sys.modules` registration needed (no dataclasses/self-references in the target).
- Spec-required test categories all present: empty, whitespace-only, normal text, non-string input, duplicates, order, non-list input — for both functions.
- No raise path exists in either function for any input (guards cover non-str / non-list / non-str items; `str.split`/`str.strip` cannot raise on a `str`).

## Per-unit blocking defects

1. `scripts/source/loop_demo.py` — none
2. `tests/test_loop_demo.py` — none

## Non-blocking notes

- The Stage 1 units, `aggregate.py`, and `context.py` named in the round history were not part of this message's payload; their round-8 state is not re-verified in this report.
- `clean_ids` accepts `list` subclasses as lists (`isinstance`), consistent with the spec's "non-list input returns []" wording; no test pins a subclass case, and none is required.
- Both functions use Unicode whitespace semantics via `str.split()`/`str.strip()` (e.g., NBSP is stripped/split); consistent with the spec's "whitespace" wording, and no non-ASCII whitespace test is required by the spec.

## Verdict: READY