from __future__ import annotations
import copy
import importlib.util
import json
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


def base() -> tuple[dict, dict]:
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


def mutate(obj: dict, path: str, value):
    """Set or delete a single key in a nested dict/list. path like 'a/b/0/c'."""
    parts = path.split("/")
    cur = obj
    for p in parts[:-1]:
        if p.isdigit():
            cur = cur[int(p)]
        else:
            cur = cur[p]
    last = parts[-1]
    if value is None:
        if last.isdigit():
            del cur[int(last)]
        else:
            del cur[last]
    else:
        if last.isdigit():
            cur[int(last)] = value
        else:
            cur[last] = value


# ---------- schema_errors tests ----------
@pytest.mark.parametrize(
    "path,value,expect_field",
    [
        # valid
        (None, None, None),
        # missing required root fields
        ("adhyay", None, "adhyay"),
        ("ovis", None, "ovis"),
        # adhyay type/range
        ("adhyay", 0, "adhyay"),
        ("adhyay", 22, "adhyay"),
        ("adhyay", "1", "adhyay"),
        # ovis not array
        ("ovis", {}, "ovis"),
        # ovi entry missing ovi
        ("ovis/0/ovi", None, "ovi"),
        # ovi entry missing disposition
        ("ovis/0/disposition", None, "disposition"),
        # invalid disposition enum
        ("ovis/0/disposition", "INVALID", "disposition"),
        # ovi type/range
        ("ovis/0/ovi", 0, "ovi"),
        ("ovis/0/ovi", -1, "ovi"),
        ("ovis/0/ovi", "1", "ovi"),
        # reason required for PROPOSE_OMISSION
        ("ovis/0/disposition", "PROPOSE_OMISSION", "reason"),
        ("ovis/0/reason", None, "reason"),
        # reason required for MERGED_EQUIVALENT
        ("ovis/4/disposition", "MERGED_EQUIVALENT", "reason"),
        ("ovis/4/reason", None, "reason"),
        # covered_by required for MERGED_EQUIVALENT
        ("ovis/4/covered_by", None, "covered_by"),
        # covered_by invalid format (not line_id or ovi)
        ("ovis/4/covered_by", "bad-id", "covered_by"),
        # extra keys
        ("ovis/0/extra", "x", "extra"),
        ("extra_root", "x", "extra_root"),
    ],
)
def test_schema_errors(path, value, expect_field):
    docs, _ = base()
    doc = docs["coverage"]
    if path is not None:
        mutate(doc, path, value)
    errs = schema_errors(doc)
    if expect_field is None:
        assert errs == []
    else:
        assert any(expect_field in e for e in errs), f"expected field {expect_field} in {errs}"


# ---------- validate tests ----------
@pytest.mark.parametrize(
    "adhyay,mutations,expect_keywords",
    [
        # valid baseline
        (1, [], []),
        # adhyay mismatch
        (2, [], ["coverage adhyay 1 does not match 2"]),
        # missing ovi disposition
        (1, [("ovis/0", None, "ovi 1 has no disposition")]),
        # duplicate ovi disposition
        (1, [("ovis/0/disposition", "VISUALISED", "ovi 1 twice")]),
        # PROPOSE_OMISSION -> note
        (
            1,
            [
                ("ovis/0/disposition", "PROPOSE_OMISSION", None),
                ("ovis/0/reason", "omit reason", None),
            ],
            ["note: ovi 1 omission proposed, owner approval needed"],
        ),
        # unfilmed but VISUALISED
        (
            1,
            [
                ("ctx/unfilmed_ovis", [1], None),
            ],
            ["ovi 1 is unfilmed but VISUALISED"],
        ),
        # covered_by invalid line_id
        (
            1,
            [
                ("ovis/4/covered_by", "S9-L99", None),
            ],
            ["S9-L99: line is not in the script"],
        ),
        # covered_by invalid ovi
        (
            1,
            [
                ("ovis/4/covered_by", "99", None),
            ],
            ["99: ovi not in chapter"],
        ),
        # covered_by valid line_id (no error)
        (1, [("ovis/4/covered_by", "S1-L1", None)], []),
        # covered_by valid ovi (no error)
        (1, [("ovis/4/covered_by", "3", None)], []),
        # empty chapter_ovis (zero-story chapter)
        (1, [("ctx/chapter_ovis", [], None)], []),
        # empty unfilmed_ovis
        (1, [("ctx/unfilmed_ovis", [], None)], []),
        # ctx values as sets (should work)
        (
            1,
            [
                ("ctx/script_line_ids", {"S1-L1", "S1-L2"}, None),
                ("ctx/chapter_ovis", {1, 2, 3}, None),
            ],
            [],
        ),
    ],
)
def test_validate(adhyay, mutations, expect_keywords):
    docs, ctx = base()
    for path, value, _ in mutations:
        if path.startswith("ctx/"):
            mutate(ctx, path[4:], value)
        else:
            mutate(docs["coverage"], path, value)
    errs = validate(adhyay, docs["coverage"], docs, ctx)
    # notes come after errors; check all expected keywords appear in order
    for kw in expect_keywords:
        assert any(kw in e for e in errs), f"expected '{kw}' in {errs}"
    if not expect_keywords:
        assert errs == []


# ---------- extra: ensure base is valid ----------
def test_base_valid():
    docs, ctx = base()
    assert schema_errors(docs["coverage"]) == []
    assert validate(1, docs["coverage"], docs, ctx) == []
