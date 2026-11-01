# SPEC: PATCH `scripts/pipeline/import_canon_docx.py` + `tests/test_import_canon_docx.py` (checklist Phase I2, 2026-11-01)

You receive the CURRENT full source of both files; every existing test passes. Output BOTH files COMPLETE (keep every function, constant and test; change only what is listed). The Adhyay 1 file `canon/test_inputs/Shri_Gajanan_Vijay_Chapter_1_Final.docx` has the same layout as the Chapter 2 file and imports today (146 ovis, 12 sections, 0 mismatches), with two parsing gaps in Part 1:

GAP 1 (name split). `_parse_item_line` splits the name at the FIRST " (" even when a ": " comes earlier. Example line: `Name A / Name B: The teaching (94-95), and more.` -> today name = everything up to " (94-95)". FIX: if `": "` occurs in the line and its index is smaller than the index of the first `" ("` (or there is no `" ("`), split at that `": "`: name = text before it (stripped), name_mr = "", description = text after it (stripped). Otherwise behave exactly as today. (Checked: no Chapter 2 item has a colon before its first " (", so Chapter 2 output is unchanged.)

GAP 2 (source note). A Part 1 bullet whose text starts with `Source register` (case-sensitive) is a note about the source, not a glossary object. FIX: such a bullet is NOT appended to any Part 1 list; its full text is kept as `parsed["source_note"]` (string; `None` when the docx has no such bullet; if there are several, join them with "\n"). `write_outputs` adds `"source_note": parsed["source_note"]` to `import_report.json` (always present, may be null). `packet.json` is unchanged in shape.

TESTS to add (synthetic docx fixtures built the same way the existing tests build them; plus the real files when present):
(a) `_parse_item_line("A / B: The text (94-95) more")` -> name "A / B", name_mr "", description "The text (94-95) more"; `_parse_item_line("Name (Marathi): desc")` unchanged; `_parse_item_line("Name: desc")` unchanged.
(b) synthetic docx whose objects list has one normal bullet and one bullet starting "Source register & boundary: note text" -> objects has ONE item, `parsed["source_note"]` equals that bullet text, and `import_report.json` written by `write_outputs` contains it; a docx without such a bullet gives `source_note` None and `"source_note": null` in the report.
(c) real Chapter 1 file (skip if missing, like the existing Chapter 2 test): 146 ovis 1..146 in order, 12 sections, sections contiguous 1..146, 0 mismatches, 8 characters, 5 locations, 10 objects, `source_note` starts with "Source register", and no object name contains ": ".
(d) real Chapter 2 file: the existing assertions keep passing, AND the parsed characters/locations/objects equal the committed `canon/adhyay_02/research/packet.json` lists exactly (proves Chapter 2 output is unchanged), and `source_note` is None.

HARD RULES: stdlib only (zipfile + xml, as now); no network; no other behaviour change; never write into `canon/` from tests (tmp_path only); no absolute drive paths.

OUTPUT FORMAT (mandatory): ONLY these two blocks, no other text; each is the line `FILE: <path>` then a fenced block starting with ```python on its own line and ending with ``` on its own line:
FILE: scripts/pipeline/import_canon_docx.py
```python
<complete module source>
```
FILE: tests/test_import_canon_docx.py
```python
<complete test source>
```
