from __future__ import annotations
import copy
import importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "pipeline" / "stage1" / "coverage.py"
spec = importlib.util.spec_from_file_location("coverage", MODULE_PATH)
cov = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cov)

SCHEMA = cov.SCHEMA
schema_errors = cov.schema_errors
validate = cov.validate


def get_parent(doc, path):
    cur = doc
    for part in path[:-1]:
        cur = cur[part] if isinstance(part, str) else cur[part]
    return cur, path[-1]


def set_at(base, path, value):
    mutated = copy.deepcopy(base)
    parent, key = get_parent(mutated, path)
    parent[key] = value
    assert mutated != base, "mutation had no effect"
    return mutated


def delete_at(base, path):
    mutated = copy.deepcopy(base)
    parent, key = get_parent(mutated, path)
    del parent[key]
    assert mutated != base, "mutation had no effect"
    return mutated


def append_at(base, path, value):
    mutated = copy.deepcopy(base)
    parent, key = get_parent(mutated, path)
    parent[key].append(value)
    assert mutated != base, "mutation had no effect"
    return mutated


def base_docs_ctx():
    docs = {
        "coverage": {
            "adhyay": 1,
            "ovis": [
                {"ovi": 1, "disposition": "VISUALISED"},
                {"ovi": 2, "disposition": "VISUALISED"},
                {"ovi": 3, "disposition": "NARRATED"},
                {"ovi": 4, "disposition": "QUOTED"},
                {
                    "ovi": 5,
                    "disposition": "MERGED_EQUIVALENT",
                    "reason": "same meaning as the line",
                    "covered_by": "S1-L2",
                },
                {"ovi": 6, "disposition": "NARRATED"},
                {"ovi": 7, "disposition": "NARRATED"},
                {"ovi": 8, "disposition": "NARRATED"},
                {"ovi": 9, "disposition": "NARRATED"},
            ],
        },
        "story_map": {},
        "scenes": {},
        "shots": {},
        "briefs": {},
        "looks": {},
        "voices": {},
        "sounds": {},
        "questions": {},
    }
    ctx = {
        "script_line_ids": ["S1-L1", "S1-L2", "S2-L1"],
        "core_line_ids": ["S1-L1", "S2-L1"],
        "chapter_ovis": [1, 2, 3, 4, 5, 6, 7, 8, 9],
        "unfilmed_ovis": [],
        "preset_ids": ["01_establishing_shot", "03_slow_cinematic_push"],
        "sound_ids": ["bed_roadside_quiet", "fx_door_wood_creak"],
        "saved_voices": {"narrator": "CXkeo30p0Sk4Lr0TAzeo", "gajanan": "8fqGzH80bdkm2UseeV9f"},
        "speaking_characters": ["narrator", "gajanan_maharaj"],
        "known_states": {"gajanan_maharaj": ["adult_youth_v1"]},
    }
    return copy.deepcopy(docs), copy.deepcopy(ctx)


# ---------- schema_errors tests ----------
@pytest.mark.parametrize(
    "mutator,expect_field",
    [
        (lambda d: d, None),  # valid
        (lambda d: delete_at(d, ["adhyay"]), "adhyay"),
        (lambda d: delete_at(d, ["ovis"]), "ovis"),
        (lambda d: set_at(d, ["adhyay"], 0), "adhyay"),
        (lambda d: set_at(d, ["adhyay"], 22), "adhyay"),
        (lambda d: set_at(d, ["adhyay"], "1"), "adhyay"),
        (lambda d: set_at(d, ["ovis"], {}), "ovis"),
        (lambda d: delete_at(d, ["ovis", 0, "ovi"]), "ovi"),
        (lambda d: delete_at(d, ["ovis", 0, "disposition"]), "disposition"),
        (lambda d: set_at(d, ["ovis", 0, "disposition"], "INVALID"), "disposition"),
        (lambda d: set_at(d, ["ovis", 0, "ovi"], 0), "ovi"),
        (lambda d: set_at(d, ["ovis", 0, "ovi"], -1), "ovi"),
        (lambda d: set_at(d, ["ovis", 0, "ovi"], "1"), "ovi"),
        # reason required for PROPOSE_OMISSION (ovi 1 has no reason in base)
        (lambda d: set_at(d, ["ovis", 0, "disposition"], "PROPOSE_OMISSION"), "reason"),
        # reason required for MERGED_EQUIVALENT (ovi 5)
        (lambda d: delete_at(d, ["ovis", 4, "reason"]), "reason"),
        # covered_by required for MERGED_EQUIVALENT (ovi 5)
        (lambda d: delete_at(d, ["ovis", 4, "covered_by"]), "covered_by"),
        # covered_by invalid format (not line_id pattern, not integer)
        (lambda d: set_at(d, ["ovis", 4, "covered_by"], "bad-id"), "covered_by"),
        # extra keys
        (lambda d: set_at(d, ["ovis", 0, "extra"], "x"), "extra"),
        (lambda d: set_at(d, ["extra_root"], "x"), "extra_root"),
        # PROPOSE_OMISSION with reason is schema-valid
        (lambda d: set_at(set_at(d, ["ovis", 0, "disposition"], "PROPOSE_OMISSION"), ["ovis", 0, "reason"], "omit"), None),
        # reason minLength 1 (empty string should fail)
        (lambda d: set_at(d, ["ovis", 0, "reason"], ""), "reason"),
        # covered_by integer minimum 1 (0 should fail)
        (lambda d: set_at(set_at(set_at(d, ["ovis", 0, "disposition"], "MERGED_EQUIVALENT"), ["ovis", 0, "reason"], "test"), ["ovis", 0, "covered_by"], 0), "covered_by"),
    ],
)
def test_schema_errors(mutator, expect_field):
    docs, _ = base_docs_ctx()
    doc = mutator(docs["coverage"])
    errs = schema_errors(doc)
    if expect_field is None:
        assert errs == []
    else:
        assert any(expect_field in e for e in errs), f"expected field {expect_field} in {errs}"


# ---------- validate tests ----------
@pytest.mark.parametrize(
    "adhyay,mutator,expect_keywords",
    [
        # valid baseline
        (1, lambda d, c: (d, c), []),
        # adhyay mismatch
        (2, lambda d, c: (d, c), ["coverage adhyay 1 does not match 2"]),
        # missing ovi disposition (remove entire ovi entry for ovi 1)
        (1, lambda d, c: (delete_at(d, ["ovis", 0]), c), ["ovi 1 has no disposition"]),
        # duplicate ovi disposition (append second ovi=1)
        (1, lambda d, c: (append_at(d, ["ovis"], {"ovi": 1, "disposition": "VISUALISED"}), c), ["ovi 1 twice"]),
        # PROPOSE_OMISSION -> note (exactly one note, after errors)
        (1, lambda d, c: (set_at(set_at(d, ["ovis", 0, "disposition"], "PROPOSE_OMISSION"), ["ovis", 0, "reason"], "omit"), c), ["note: ovi 1 omission proposed, owner approval needed"]),
        # unfilmed but VISUALISED
        (1, lambda d, c: (d, set_at(c, ["unfilmed_ovis"], [1])), ["ovi 1 is unfilmed but VISUALISED"]),
        # covered_by invalid line_id
        (1, lambda d, c: (set_at(d, ["ovis", 4, "covered_by"], "S9-L99"), c), ["S9-L99"]),
        # covered_by invalid ovi (integer)
        (1, lambda d, c: (set_at(d, ["ovis", 4, "covered_by"], 99), c), ["99"]),
        # covered_by valid line_id (no error)
        (1, lambda d, c: (set_at(d, ["ovis", 4, "covered_by"], "S1-L1"), c), []),
        # covered_by valid ovi (integer, no error)
        (1, lambda d, c: (set_at(d, ["ovis", 4, "covered_by"], 3), c), []),
        # empty chapter_ovis (zero-story chapter)
        (1, lambda d, c: (d, set_at(c, ["chapter_ovis"], [])), []),
        # unfilmed_ovis with non-VISUALISED ovi (no error)
        (1, lambda d, c: (d, set_at(c, ["unfilmed_ovis"], [3])), []),
        # ctx values as sets (should work)
        (1, lambda d, c: (d, set_at(set_at(c, ["script_line_ids"], {"S1-L1", "S1-L2"}), ["chapter_ovis"], {1, 2, 3})), []),
    ],
)
def test_validate(adhyay, mutator, expect_keywords):
    docs, ctx = base_docs_ctx()
    doc, ctx = mutator(docs["coverage"], ctx)
    errs = validate(adhyay, doc, docs, ctx)
    # notes come after errors; check all expected keywords appear
    for kw in expect_keywords:
        assert any(kw in e for e in errs), f"expected '{kw}' in {errs}"
    if not expect_keywords:
        assert errs == []


# ---------- extra: ensure base is valid ----------
def test_base_valid():
    docs, ctx = base_docs_ctx()
    assert schema_errors(docs["coverage"]) == []
    assert validate(1, docs["coverage"], docs, ctx) == []


# ---------- note ordering and count ----------
def test_propose_omission_note_comes_after_errors():
    docs, ctx = base_docs_ctx()
    # Create a doc with both an error and a PROPOSE_OMISSION
    doc = copy.deepcopy(docs["coverage"])
    # Add an error: unfilmed but VISUALISED
    ctx = set_at(ctx, ["unfilmed_ovis"], [1])
    # Add a PROPOSE_OMISSION on ovi 2
    doc = set_at(doc, ["ovis", 1, "disposition"], "PROPOSE_OMISSION")
    doc = set_at(doc, ["ovis", 1, "reason"], "omit")
    errs = validate(1, doc, docs, ctx)
    # Should have error first, then note
    assert len(errs) == 2
    assert "ovi 1 is unfilmed but VISUALISED" in errs[0]
    assert errs[1].startswith("note: ")
    assert "ovi 2 omission proposed" in errs[1]


def test_propose_omission_exactly_one_note_per_entry():
    docs, ctx = base_docs_ctx()
    doc = copy.deepcopy(docs["coverage"])
    # Add two PROPOSE_OMISSION entries for same ovi (should produce two notes)
    doc = set_at(doc, ["ovis", 0, "disposition"], "PROPOSE_OMISSION")
    doc = set_at(doc, ["ovis", 0, "reason"], "omit1")
    doc = append_at(doc, ["ovis"], {"ovi": 1, "disposition": "PROPOSE_OMISSION", "reason": "omit2"})
    errs = validate(1, doc, docs, ctx)
    notes = [e for e in errs if e.startswith("note: ")]
    assert len(notes) == 2
    assert all("omission proposed" in n for n in notes)


# ---------- regression: validate never raises on odd data ----------
@pytest.mark.parametrize(
    "doc,ctx",
    [
        # doc not a dict
        (None, {}),
        ("not a dict", {}),
        (123, {}),
        ([], {}),
        # ovis not a list
        ({"adhyay": 1, "ovis": "not a list"}, {}),
        ({"adhyay": 1, "ovis": 123}, {}),
        ({"adhyay": 1, "ovis": None}, {}),
        # ovis entries not dicts
        ({"adhyay": 1, "ovis": ["not a dict", 123, None]}, {}),
        # ovi not an int (unhashable)
        ({"adhyay": 1, "ovis": [{"ovi": [1, 2], "disposition": "VISUALISED"}]}, {}),
        # ovi not an int (string)
        ({"adhyay": 1, "ovis": [{"ovi": "1", "disposition": "VISUALISED"}]}, {}),
        # ovi not an int (float)
        ({"adhyay": 1, "ovis": [{"ovi": 1.5, "disposition": "VISUALISED"}]}, {}),
        # disposition not a string
        ({"adhyay": 1, "ovis": [{"ovi": 1, "disposition": 123}]}, {}),
    ],
)
def test_validate_odd_data_no_raise(doc, ctx):
    """validate must never raise; it should return a list of errors (possibly empty)."""
    docs = {"coverage": {}, "story_map": {}, "scenes": {}, "shots": {}, "briefs": {}, "looks": {}, "voices": {}, "sounds": {}, "questions": {}}
    errs = validate(1, doc, docs, ctx)
    assert isinstance(errs, list)


# ---------- regression: validate handles malformed ctx values without raising ----------
@pytest.mark.parametrize(
    "ctx_key,bad_value",
    [
        ("script_line_ids", None),
        ("script_line_ids", "not a list"),
        ("script_line_ids", 123),
        ("script_line_ids", [[]]),
        ("chapter_ovis", None),
        ("chapter_ovis", "not a list"),
        ("chapter_ovis", 123),
        ("chapter_ovis", [[]]),
        ("unfilmed_ovis", None),
        ("unfilmed_ovis", "not a list"),
        ("unfilmed_ovis", 123),
        ("unfilmed_ovis", [[]]),
    ],
)
def test_validate_malformed_ctx_no_raise(ctx_key, bad_value):
    """validate must handle non-collection ctx values gracefully."""
    docs, ctx = base_docs_ctx()
    ctx = copy.deepcopy(ctx)
    ctx[ctx_key] = bad_value
    doc = copy.deepcopy(docs["coverage"])
    errs = validate(1, doc, docs, ctx)
    assert isinstance(errs, list)
    # Should not contain any "malformed structure" sentinel
    assert not any("malformed structure" in e for e in errs)


# ---------- regression: validate handles None/non-dict ctx and docs ----------
def test_validate_none_ctx_no_raise():
    """validate must handle ctx=None without raising."""
    docs, _ = base_docs_ctx()
    doc = copy.deepcopy(docs["coverage"])
    errs = validate(1, doc, docs, None)
    assert isinstance(errs, list)
    # Should not contain any "malformed structure" sentinel
    assert not any("malformed structure" in e for e in errs)


def test_validate_string_ctx_no_raise():
    """validate must handle ctx='x' (string) without raising."""
    docs, _ = base_docs_ctx()
    doc = copy.deepcopy(docs["coverage"])
    errs = validate(1, doc, docs, "not a dict")
    assert isinstance(errs, list)
    assert not any("malformed structure" in e for e in errs)


def test_validate_none_docs_no_raise():
    """validate must handle docs=None without raising."""
    docs, ctx = base_docs_ctx()
    doc = copy.deepcopy(docs["coverage"])
    errs = validate(1, doc, None, ctx)
    assert isinstance(errs, list)
    assert not any("malformed structure" in e for e in errs)


def test_validate_chapter_ovis_unhashable_no_raise():
    """validate must handle chapter_ovis containing unhashable items (e.g., list) without raising."""
    docs, ctx = base_docs_ctx()
    ctx = copy.deepcopy(ctx)
    ctx["chapter_ovis"] = [[1], [2]]  # unhashable list items
    doc = copy.deepcopy(docs["coverage"])
    errs = validate(1, doc, docs, ctx)
    assert isinstance(errs, list)
    assert not any("malformed structure" in e for e in errs)
