# SPEC: NEW `scripts/pipeline/stage1/script_from_docx.py` + NEW `tests/test_stage1_script_from_docx.py`. Return exactly these TWO files in full; do not output or change any other file.
Purpose: Adhyay 2 (and every later Adhyay) arrives as the owner's Audited Canon docx, which has NO script in the pipeline's line format. For dry runs and trials, build a DRAFT script MECHANICALLY from the docx columns that the owner already supplied (Simple Marathi and Hindi), without changing a single word. This is NOT the owner's final script; the file says so in its heading. Standard library only; `from __future__ import annotations`; nothing at import time except imports and definitions; no print except in `main()`. Plain functions, no classes.

## Input
The ovis written by `scripts/pipeline/import_canon_docx.py` into `canon/adhyay_NN/source/ovis.jsonl`: one JSON object per line with the fields `adhyay` (int), `ovi` (int), `section` (int, the docx section number), `original_marathi`, `simple_marathi`, `hindi`, `easy_english`, `printed_number` (int or null).

## API
- `ovis_to_script(adhyay: int, ovis: list[dict]) -> str`: returns the script text. Sort the ovis by `ovi`. Output exactly this format (it is parsed by `scripts/pipeline/check_script.parse_script`, whose header regex is `^\*\*(S(\d+)-L(\d+))\*\* \| (\S+) \| ovi (\d+) \| (\S+)$`):
  ```
  # Adhyay <N>: DRAFT script built mechanically from the owner's docx columns (Simple Marathi, Hindi). NOT the owner's final script; speakers are all narrator; every line is core.
  
  ## S<section>
  **S<section>-L<k>** | narrator | ovi <ovi> | core
  - Marathi: <simple_marathi on ONE line>
  - Hindi: <hindi on ONE line>
  
  ```
  where `<section>` is the record's `section`, `<k>` counts the lines inside that section from 1 in ovi order, a `## S<section>` heading is written once when the section changes, and a blank line follows each line block. The text of a cell is used UNCHANGED except that every run of whitespace (including newlines) is collapsed to one space and the ends are stripped. Never translate, shorten, correct or add words.
  Errors: raise `ValueError` (clear message) when `ovis` is empty, when a record lacks an int `ovi` or an int `section`, when `simple_marathi` or `hindi` is missing or empty after collapsing, or when two records share an ovi. A bool is not an int.
- `main(argv=None) -> int`: `--adhyay N` (int, required), `--root PATH` (default the repo root `Path(__file__).resolve().parents[3]`). Reads `<root>/canon/adhyay_<NN>/source/ovis.jsonl`, writes `<root>/canon/adhyay_<NN>/script/easy.md` (creating the folder); refuses with `refused: <reason>` and returns 2 if the output exists, the input is missing or a record is invalid; prints one line `adhyay N: <lines> lines, <sections> sections` and returns 0. `if __name__ == "__main__": raise SystemExit(main())`.

## Tests (`tests/test_stage1_script_from_docx.py`; synthetic data only, plus ONE real-file test)
Load the module and `scripts/pipeline/check_script.py` by importlib BY PATH (`ROOT = Path(__file__).resolve().parents[1]`).
1. A small synthetic ovis list (3 sections, 6 ovis, short invented Devanagari words) gives the exact expected text (compare the full string) and `parse_script` returns one record per ovi with the right id, scene, voice `narrator`, ovi, priority `core`, and the Marathi/Hindi texts equal to the collapsed cell texts.
2. Whitespace collapsing: a cell with newlines and double spaces becomes one line with single spaces; nothing else changes (assert the other characters are identical).
3. Ordering and numbering: ovis given unsorted are sorted by ovi; `k` restarts at 1 in every section; a section number that jumps (1, 3) is kept as given.
4. Each error case raises ValueError (empty list, missing ovi, missing section, bool ovi, empty hindi, duplicate ovi), each in its own isolated test.
5. `main`: writes the file in tmp_path, refuses to overwrite (return 2), refuses a missing input (return 2) (use capsys).
6. REAL file (skip with `pytest.mark.skipif` if the file is missing): `canon/test_inputs/Shri_Gajanan_Vijay_Chapter_2_Audited_Canon_Edition.docx` through `scripts/pipeline/import_canon_docx.py` (`parse_docx(Path)` returns a dict with `ovis`), then `ovis_to_script(2, parsed["ovis"])`: `parse_script` gives exactly 148 records, 12 distinct scenes, every record has non-empty Marathi and Hindi, `check_script.check_script` is NOT required.
Use `copy.deepcopy` and plain assignment for any mutation; never a helper that rejects "no effect" mutations.

Reply with only the two FILE blocks:
FILE: scripts/pipeline/stage1/script_from_docx.py
FILE: tests/test_stage1_script_from_docx.py
