import copy
import pytest
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "pipeline" / "stage1" / "looks.py"
spec = importlib.util.spec_from_file_location("looks", MODULE_PATH)
looks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(looks)

BASE_DOCS = {
    "looks": {
        "adhyay": 1,
        "entries": [
            {
                "entity_id": "gajanan_maharaj",
                "kind": "character",
                "state_id": "adult_youth_v2",
                "look": "slim adult, cropped hair, open frayed grey-white vest",
                "source_ovis": [1],
                "basis": "stated",
            },
            {
                "entity_id": "bankatlal",
                "kind": "character",
                "state_id": "merchant_v1",
                "look": "cream turban, sage coat",
                "source_ovis": [2],
                "basis": "inferred",
            },
        ],
    }
}
CTX = {
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


def base():
    return {"docs": copy.deepcopy(BASE_DOCS), "ctx": copy.deepcopy(CTX)}


def mutate(obj, path, value):
    parts = path.split(".")
    target = obj
    for part in parts[:-1]:
        target = target[int(part)] if part.isdigit() else target[part]
    last = parts[-1]
    if value is None:
        del target[last]
    else:
        target[last] = value
    return obj


SCHEMA_CASES = [
    ("valid", None, None, []),
    ("missing_adhyay", "docs.looks.adhyay", None, "adhyay"),
    ("adhyay_zero", "docs.looks.adhyay", 0, "adhyay"),
    ("adhyay_22", "docs.looks.adhyay", 22, "adhyay"),
    ("adhyay_string", "docs.looks.adhyay", "1", "adhyay"),
    ("missing_entries", "docs.looks.entries", None, "entries"),
    ("entries_not_array", "docs.looks.entries", "x", "entries"),
    ("entries_empty", "docs.looks.entries", [], []),  # valid per spec
    ("missing_entity_id", "docs.looks.entries.0.entity_id", None, "entity_id"),
    ("missing_kind", "docs.looks.entries.0.kind", None, "kind"),
    ("missing_state_id", "docs.looks.entries.0.state_id", None, "state_id"),
    ("missing_look", "docs.looks.entries.0.look", None, "look"),
    ("missing_source_ovis", "docs.looks.entries.0.source_ovis", None, "source_ovis"),
    ("missing_basis", "docs.looks.entries.0.basis", None, "basis"),
    ("kind_invalid", "docs.looks.entries.0.kind", "invalid", "kind"),
    ("basis_invalid", "docs.looks.entries.0.basis", "invalid", "basis"),
    ("source_ovis_not_array", "docs.looks.entries.0.source_ovis", "x", "source_ovis"),
    ("source_ovis_empty", "docs.looks.entries.0.source_ovis", [], "source_ovis"),
    ("source_ovis_zero", "docs.looks.entries.0.source_ovis", [0], "source_ovis"),
    ("source_ovis_string", "docs.looks.entries.0.source_ovis", ["1"], "source_ovis"),
    ("look_empty", "docs.looks.entries.0.look", "", "look"),
    ("look_too_long", "docs.looks.entries.0.look", "x" * 401, "look"),
    ("extra_root_field", "docs.looks.extra", "x", "extra"),
    ("extra_entry_field", "docs.looks.entries.0.extra", "x", "extra"),
]


@pytest.mark.parametrize("name,path,value,expected_field", SCHEMA_CASES)
def test_schema_errors(name, path, value, expected_field):
    b = base()
    if path:
        mutate(b, path, value)
    errors = looks.schema_errors(b["docs"]["looks"])
    if expected_field == []:
        assert errors == []
    else:
        assert any(expected_field in e for e in errors), f"{name}: {errors}"


SEMANTIC_CASES = [
    ("valid", None, None, []),
    ("adhyay_mismatch", "docs.looks.adhyay", 2, "adhyay"),
    ("source_ovi_unknown", "docs.looks.entries.0.source_ovis", [99], "source_ovis"),
    ("known_state_redecided", "docs.looks.entries.0.state_id", "adult_youth_v1", "redecided"),
    ("duplicate_entity_state", "docs.looks.entries.1.state_id", "adult_youth_v2", "duplicate"),
    ("new_state_known_entity", "docs.looks.entries.0.state_id", "adult_youth_v3", []),
    ("unknown_entity", "docs.looks.entries.0.entity_id", "new_entity", []),
]


@pytest.mark.parametrize("name,path,value,expected_keyword", SEMANTIC_CASES)
def test_validate_errors(name, path, value, expected_keyword):
    b = base()
    if path:
        mutate(b, path, value)
    errors = looks.validate(1, b["docs"]["looks"], b["docs"], b["ctx"])
    if expected_keyword == []:
        assert errors == [], f"{name}: {errors}"
    else:
        assert any(expected_keyword in e for e in errors), f"{name}: {errors}"
