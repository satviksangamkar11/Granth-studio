# Spec: write ONE file `scripts/pipeline/check_script.py`. The frozen tests are in `tests/test_check_script.py` (shown below; they load your module by path with importlib).
Style: `from __future__ import annotations`, standard library (plus `jsonschema` where stated), short docstrings, no print, no network, no file writes by the module (tests may write under pytest `tmp_path`), nothing at import time. The module never raises for bad DATA: it returns error strings (stable order, each message starts with the item id such as a line id, shot id, image id or document name). Type/argument misuse (wrong argument types) may raise TypeError/ValueError only where the API says so. The tests below are FROZEN: make them pass, do not change them. Messages are plain English and MUST contain the keywords the tests look for (case-sensitive).

## Purpose and format
Check the owner's EASY script text. The owner's script is final and perfect: this module only REPORTS; it never changes, rewrites or suggests different wording, and has no function that opens or writes files (it takes text). Format:
```
## S1
**S1-L1** | narrator | ovi 70 | core
- Marathi: <text>
- Hindi: <text>
caption S1-K1 (on screen): <text>
```
## API
- `parse_script(text) -> list[dict]`: walk the lines with 1-based `line_no`. A line starting with `## S` sets the current heading (e.g. "S1"). ANY stripped line that starts with `**S` is a header candidate; it must match `^\*\*(S(\d+)-L(\d+))\*\* \| (\S+) \| ovi (\d+) \| (\S+)$` (priority text is captured as is and checked later). A candidate that does not match yields {"bad_header": raw_line, "line_no": n} (never dropped). A matching header yields {"id","scene" ("S1"),"voice","ovi" (int),"priority","marathi","hindi","heading" (current heading or ""),"line_no","n_marathi","n_hindi"}; lines `- Marathi: ...` / `- Hindi: ...` after a header belong to it until the next header or heading; the text is the rest of the line stripped; count each bullet in n_marathi/n_hindi (keep the first text). Caption and other lines are ignored.
- `check_script(lines, chapter_ovis, unfilmed_ovis, voices, glossary) -> list[str]`: `glossary` maps a WRONG spelling to the RIGHT one. Messages (the id first; bad headers use "line <n>:"): "bad header" for each bad_header record; "<id>: duplicate id"; "<id>: line numbers must be consecutive from 1 within the scene" (L numbers consecutive from 1 per scene, and scenes in increasing order: report "scene order" if a scene number is lower than an earlier one); "<id>: heading <heading> does not match the scene"; "<id>: voice <v> is not registered"; "<id>: ovi <n> is not in the chapter"; "<id>: priority <p> must be core or optional"; "<id>: Marathi must have exactly one bullet" / "Hindi must have exactly one bullet" (when n != 1); "<id>: Marathi is empty" / "Hindi is empty"; "<id>: Marathi has no Devanagari letter" / Hindi (a Devanagari LETTER means a character in U+0900-U+097F whose unicodedata category starts with "L"; digits and marks alone do not count; the word "letter" must appear); "<id>: Marathi contains a Latin letter" / Hindi; "<id>: Marathi contains an ASCII digit" / Hindi (word "digit"); glossary: "<id>: Marathi contains '<wrong>', glossary says '<right>'" (plain substring match); coverage: "ovi <n> has no core line" for every ovi in chapter_ovis minus unfilmed_ovis with no CORE line; "note: ovi <n> is unfilmed but line <id> uses it" for a line using an unfilmed ovi. An empty list of lines yields "script has no lines" plus the coverage messages. Check order: all per-line checks in file order, then coverage in ovi order.
- `script_sha256(text) -> str`: sha256 hex of text.encode("utf-8") with no normalisation.

## The frozen tests (do not change)
FILE tests/test_check_script.py:
```python
import copy
import hashlib
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_script", ROOT / "scripts" / "pipeline" / "check_script.py")
cs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cs)

GOOD = """# title
## S1
**S1-L1** | narrator | ovi 1 | core
- Marathi: हे पहिले वाक्य आहे.
- Hindi: यह पहला वाक्य है।

caption S1-K1 (on screen): १८७८

**S1-L2** | bankatlal | ovi 2 | optional
- Marathi: दुसरे वाक्य.
- Hindi: दूसरा वाक्य।
## S2
**S2-L1** | narrator | ovi 3 | core
- Marathi: तिसरे वाक्य.
- Hindi: तीसरा वाक्य।
"""
OVIS, UNF, VOICES, GLOS = {1, 2, 3, 4}, {4}, {"narrator", "bankatlal"}, {"अगरवाला": "अग्रवाल"}


def run(text, ovis=OVIS, unf=UNF, voices=VOICES, glos=GLOS):
    return cs.check_script(cs.parse_script(text), ovis, unf, voices, glos)


def has(errs, *words):
    return any(all(w in e for w in words) for e in errs)


def test_valid_script_has_no_problems_and_parse_shape():
    assert run(GOOD) == []
    lines = cs.parse_script(GOOD)
    assert [l["id"] for l in lines] == ["S1-L1", "S1-L2", "S2-L1"]
    l0 = lines[0]
    assert (l0["scene"], l0["heading"], l0["voice"], l0["ovi"], l0["priority"]) == ("S1", "S1", "narrator", 1, "core")
    assert l0["marathi"].startswith("हे") and l0["hindi"].startswith("यह") and l0["n_marathi"] == 1 and l0["n_hindi"] == 1 and l0["line_no"] == 3


def test_malformed_headers_are_never_silently_dropped():
    bad = GOOD.replace("**S1-L2** | bankatlal | ovi 2 | optional", "**S1-L2** | bankatlal | ovi two | optional")
    assert any("bad_header" in l for l in cs.parse_script(bad))
    assert has(run(bad), "bad header")
    assert has(run(GOOD.replace("**S1-L2** | bankatlal | ovi 2 | optional", "**S1-L2** | bankatlal | ovi 2")), "bad header")


@pytest.mark.parametrize("old,new,words", [
    ("**S1-L2**", "**S1-L1**", ("S1-L1", "duplicate")),
    ("**S1-L2**", "**S1-L3**", ("S1-L3", "consecutive")),
    ("## S2", "## S5", ("S2-L1", "heading")),
    ("| bankatlal |", "| nobody |", ("S1-L2", "voice")),
    ("ovi 2 | optional", "ovi 99 | optional", ("S1-L2", "ovi 99")),
    ("ovi 2 | optional", "ovi 2 | maybe", ("S1-L2", "priority")),
    ("- Hindi: दूसरा वाक्य।", "- Hindi: ", ("S1-L2", "Hindi", "empty")),
    ("- Hindi: दूसरा वाक्य।", "- Hindi: second line।", ("S1-L2", "Latin")),
    ("- Marathi: दुसरे वाक्य.", "- Marathi: दुसरे 5 वाक्य.", ("S1-L2", "digit")),
    ("- Marathi: दुसरे वाक्य.", "- Marathi: १२३.", ("S1-L2", "letter")),
    ("- Marathi: तिसरे वाक्य.", "- Marathi: तिसरे अगरवाला वाक्य.", ("S2-L1", "अगरवाला", "अग्रवाल")),
])
def test_each_rule_fails_on_its_own(old, new, words):
    assert has(run(GOOD.replace(old, new, 1)), *words)


def test_duplicate_or_missing_bullets_and_scene_order():
    dup = GOOD.replace("- Hindi: यह पहला वाक्य है।", "- Hindi: यह पहला वाक्य है।\n- Hindi: कुछ और।")
    assert has(run(dup), "S1-L1", "Hindi", "exactly one")
    nomr = GOOD.replace("- Marathi: दुसरे वाक्य.\n", "")
    assert has(run(nomr), "S1-L2", "Marathi", "exactly one")
    swapped = GOOD.replace("## S1", "## SX").replace("## S2", "## S1").replace("## SX", "## S2")
    assert has(run(swapped), "scene", "order") or has(run(swapped), "heading")


def test_coverage_and_unfilmed():
    only = GOOD.replace("ovi 3 | core", "ovi 1 | core")
    assert has(run(only), "ovi 3", "no core line")
    assert not has(run(GOOD), "ovi 4")                                        # unfilmed ovi 4 needs no line
    withline = GOOD.replace("ovi 3 | core", "ovi 4 | core")
    errs = run(withline)
    assert any(e.startswith("note:") and "ovi 4" in e for e in errs)


def test_empty_script_and_hash_and_no_mutation(tmp_path):
    assert has(run(""), "no lines") or has(run(""), "ovi 1")
    text = GOOD
    assert cs.script_sha256(text) == hashlib.sha256(text.encode("utf-8")).hexdigest()
    lines = cs.parse_script(GOOD)
    before = copy.deepcopy(lines)
    cs.check_script(lines, set(OVIS), set(UNF), set(VOICES), dict(GLOS))
    assert lines == before
    src = (ROOT / "scripts" / "pipeline" / "check_script.py").read_text(encoding="utf-8")
    for forbidden in ("write_text", "write_bytes", ".write(", "open(", "os.remove", "unlink"):
        assert forbidden not in src                                           # it reports, it never edits the owner's script

```

Reply with only: FILE: scripts/pipeline/check_script.py followed by its code block.
