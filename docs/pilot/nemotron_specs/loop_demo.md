# SPEC: NEW `scripts/source/loop_demo.py` + NEW `tests/test_loop_demo.py` (proof job for the automated loop).
`scripts/source/loop_demo.py`: `from __future__ import annotations`; a pure function `word_count(text: str) -> int` that counts whitespace-separated words (a non-string returns 0); a pure function `clean_ids(items: list) -> list[str]` that returns the sorted unique non-empty string items after stripping whitespace (non-strings and empty strings are skipped; a non-list input returns []). Nothing at import time except definitions.
`tests/test_loop_demo.py`: tests for both functions (empty, whitespace only, normal text, non-string input, duplicates, order, non-list input). Load the module with importlib by path (`Path(__file__).resolve().parents[1] / "scripts" / "source" / "loop_demo.py"`).
Reply with only the two FILE blocks:
FILE: scripts/source/loop_demo.py
FILE: tests/test_loop_demo.py
