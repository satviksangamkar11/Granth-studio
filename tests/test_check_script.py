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

**S1-L2** | bankatlal | ovi 2 | core
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
    bad = GOOD.replace("**S1-L2** | bankatlal | ovi 2 | core", "**S1-L2** | bankatlal | ovi two | optional")
    assert any("bad_header" in l for l in cs.parse_script(bad))
    assert has(run(bad), "bad header")
    assert has(run(GOOD.replace("**S1-L2** | bankatlal | ovi 2 | core", "**S1-L2** | bankatlal | ovi 2")), "bad header")


@pytest.mark.parametrize("old,new,words", [
    ("**S1-L2**", "**S1-L1**", ("S1-L1", "duplicate")),
    ("**S1-L2**", "**S1-L3**", ("S1-L3", "consecutive")),
    ("## S2", "## S5", ("S2-L1", "heading")),
    ("| bankatlal |", "| nobody |", ("S1-L2", "voice")),
    ("ovi 2 | core", "ovi 99 | core", ("S1-L2", "ovi 99")),
    ("ovi 2 | core", "ovi 2 | maybe", ("S1-L2", "priority")),
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
