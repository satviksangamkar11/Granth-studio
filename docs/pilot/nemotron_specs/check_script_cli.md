# SPEC: NEW `scripts/pipeline/check_script_cli.py` + NEW `tests/test_check_script_cli.py`. Return exactly these TWO files in full; do not output or change any other file.
Checklist row 17: run the existing source/EASY script checker on a REAL script and write a receipt. The checker only reports; it never edits the script. Standard library only; `from __future__ import annotations`; nothing at import time except imports and definitions; no print except in `main()`; plain functions.

## Existing code (load by importlib BY PATH; do not modify)
- `scripts/pipeline/check_script.py`: `parse_script(text) -> list[dict]` (records with `id, scene, voice, ovi, priority, marathi, hindi, ...`), `check_script(lines, chapter_ovis: set[int], unfilmed_ovis: set[int], voices: set[str], glossary: dict[str, str]) -> list[str]` (error messages), `script_sha256(text) -> str`.
- `scripts/pipeline/chapter.py`: `chapter_paths(adhyay, root)` with the keys `script`, `source_ovis`, `stage1_dir` (ValueError for an invalid adhyay).
- `scripts/pipeline/stage1/context.py`: `build_ctx(adhyay, root, extra=None) -> (ctx, problems)`; ctx keys used here: `chapter_ovis` (list of int), `unfilmed_ovis` (list of int, the owner-APPROVED omissions), `saved_voices` (dict voice_key -> voice_id), `series_voices` (dict character_id -> voice_key).
Repo root in this module: `Path(__file__).resolve().parents[2]`; in tests `Path(__file__).resolve().parents[1]`.

## API
- `run_check(adhyay: int, root: Path | str, glossary: dict[str, str] | None = None, extra_voices: list[str] | None = None) -> dict`: NEVER raises. Reads the script text from `chapter_paths(...)["script"]` (missing -> a problem `script: missing` and an empty result), parses it, builds the ctx, and the allowed voice set = `{"narrator"}` plus `saved_voices` keys plus `series_voices` keys plus `extra_voices`; calls `check_script(lines, set(chapter_ovis), set(unfilmed_ovis), voices, glossary or {})`. Returns `{"adhyay", "script": <path relative to root with forward slashes>, "script_sha256", "lines": len(lines), "scenes": number of distinct scene ids, "core": count of priority core, "optional": count of the others, "errors": [...], "problems": ctx problems + own problems, "ok": errors == [] and no own problem}`.
- `write_receipt(result: dict, root: Path | str, today: str | None = None) -> Path`: writes `<stage1_dir>/script_check_receipt.json` (json, indent 1, sort_keys, `ensure_ascii=False`) with the result plus `"date"` (today or ISO today) and the field `"note": "report only; the script was never edited"`; raises `FileExistsError` if the file exists; creates the folder.
- `main(argv=None) -> int`: `--adhyay N` (required), `--root PATH` (default repo root), `--write-receipt` (flag), `--extra-voice ID` (repeatable). Prints one line `adhyay N: <lines> lines, <scenes> scenes, <core> core, <errors> errors, <problems> problems` then each error as `error: <text>` (at most 40, then `... and <k> more`); with `--write-receipt` writes the receipt (an existing receipt -> prints `refused: receipt exists` and returns 2) and prints `receipt <path>`. Returns 0 when ok, 1 otherwise.

## Tests (`tests/test_check_script_cli.py`; synthetic data in tmp_path plus real-file tests)
Synthetic root for adhyay 2: `canon/adhyay_02/source/ovis.jsonl` (`{"ovi": n}` for n in 1..4), `canon/adhyay_02/script/easy.md` in the REAL EASY format (`## S1`, then `**S1-L1** | narrator | ovi 1 | core`, `- Marathi: ...`, `- Hindi: ...`, blank line, and so on; lines for ovis 1, 2, 3 and 4 with 2 scenes), `canon/series/voices.json` with `{"voices": [ {"voice_key": "narrator", "voice_id": "id1"} ]}`.
1. Happy path: counts right, `errors == []`, `ok` True, `script_sha256` equals `script_sha256(text)`.
2. Each defect in its own isolated test (verified by the checker itself): a duplicate line id, a missing Hindi line, an unknown voice (`stranger`), an ovi not in the chapter; assert the result is not ok and the error mentions the line id.
3. Missing script -> problem `script: missing`, no exception; invalid adhyay -> no exception and a problem.
4. `write_receipt`: file content, the note, refusal on a second write; `main` output and return codes (capsys), `--write-receipt`, the refusal returning 2.
5. REAL files (skipif a file is missing): `run_check(1, ROOT)` returns 62 lines and 9 scenes (Adhyay 1 script `docs/pilot/A1_full_script_simple.md` through chapter_paths); `run_check(2, ROOT)` returns 148 lines and 12 scenes; neither raises. Do NOT assert that the real errors list is empty (the checker may report real findings); assert only the counts and that every error is a string.
Use plain assignment and `copy.deepcopy`; never a helper that rejects no-effect mutations.

Reply with only the two FILE blocks:
FILE: scripts/pipeline/check_script_cli.py
FILE: tests/test_check_script_cli.py
