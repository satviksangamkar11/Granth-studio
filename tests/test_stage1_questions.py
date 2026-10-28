import copy
import importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "pipeline" / "stage1" / "questions.py"
spec = importlib.util.spec_from_file_location("questions", MODULE_PATH)
questions = importlib.util.module_from_spec(spec)
spec.loader.exec_module(questions)

SCHEMA = questions.SCHEMA
schema_errors = questions.schema_errors
validate = questions.validate


def base():
    return {
        "docs": {
            "questions": {
                "adhyay": 1,
                "questions": [
                    {"id": "Q1", "text": "Which hand holds the gourd?", "scene_id": "S1"}
                ],
            },
            "scenes": {
                "adhyay": 1,
                "scenes": [
                    {
                        "scene_id": "S1",
                        "section_kind": "story",
                        "ovi_range": [1, 5],
                        "goal": "arrival",
                        "turn": {"ovi": 3, "text": "he sits"},
                        "line_ids": ["S1-L1", "S1-L2"],
                    },
                    {
                        "scene_id": "S2",
                        "section_kind": "discourse",
                        "ovi_range": [6, 9],
                        "goal": "teaching",
                        "turn": {"ovi": 7, "text": "the saying"},
                        "line_ids": ["S2-L1"],
                        "teaching_treatment": "narration_over_typography",
                    },
                ],
            },
        },
        "ctx": {
            "script_line_ids": ["S1-L1", "S1-L2", "S2-L1"],
            "core_line_ids": ["S1-L1", "S2-L1"],
            "chapter_ovis": [1, 2, 3, 4, 5, 6, 7, 8, 9],
            "unfilmed_ovis": [],
            "preset_ids": ["01_establishing_shot", "03_slow_cinematic_push"],
            "sound_ids": ["bed_roadside_quiet", "fx_door_wood_creak"],
            "saved_voices": {"narrator": "CXkeo30p0Sk4Lr0TAzeo", "gajanan": "8fqGzH80bdkm2UseeV9f"},
            "speaking_characters": ["narrator", "gajanan_maharaj"],
            "known_states": {"gajanan_maharaj": ["adult_youth_v1"]},
        },
    }


def get_parent(doc, path):
    cur = doc
    for p in path[:-1]:
        cur = cur[int(p)] if isinstance(cur, list) else cur[p]
    return cur, path[-1]


def set_at(base, path, value):
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    if isinstance(parent, list):
        parent[int(key)] = value
    else:
        parent[key] = value
    assert doc != base
    return doc


def delete_at(base, path):
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    if isinstance(parent, list):
        del parent[int(key)]
    else:
        del parent[key]
    assert doc != base
    return doc


def append_at(base, path, value):
    doc = copy.deepcopy(base)
    parent, key = get_parent(doc, path)
    target = parent[key] if isinstance(parent, dict) else parent[int(key)]
    assert isinstance(target, list)
    target.append(value)
    assert doc != base
    return doc


@pytest.mark.parametrize("path,field", [
    (["docs", "questions", "adhyay"], "adhyay"),
    (["docs", "questions", "questions"], "questions"),
    (["docs", "questions", "questions", 0, "id"], "id"),
    (["docs", "questions", "questions", 0, "text"], "text"),
])
def test_schema_errors_required(path, field):
    doc = delete_at(base(), path)
    errs = schema_errors(doc["docs"]["questions"])
    assert any(field in e for e in errs)


@pytest.mark.parametrize("path,value,field", [
    (["docs", "questions", "questions", 0, "id"], "X1", "id"),
    (["docs", "questions", "questions", 0, "id"], "Q", "id"),
    (["docs", "questions", "questions", 0, "id"], "Qx", "id"),
    (["docs", "questions", "questions", 0, "text"], "", "text"),
    (["docs", "questions", "questions", 0, "text"], "x" * 401, "text"),
    (["docs", "questions", "questions", 0, "scene_id"], "X1", "scene_id"),
    (["docs", "questions", "questions", 0, "extra"], "bad", "extra"),
    (["docs", "questions", "extra"], "bad", "extra"),
    (["docs", "questions", "adhyay"], 0, "adhyay"),
    (["docs", "questions", "adhyay"], 22, "adhyay"),
    (["docs", "questions", "adhyay"], "not-int", "adhyay"),
])
def test_schema_errors_format(path, value, field):
    doc = set_at(base(), path, value)
    errs = schema_errors(doc["docs"]["questions"])
    assert any(field in e for e in errs)


def test_schema_baseline_valid():
    errs = schema_errors(base()["docs"]["questions"])
    assert errs == []


def test_schema_scene_id_optional():
    doc = delete_at(base(), ["docs", "questions", "questions", 0, "scene_id"])
    errs = schema_errors(doc["docs"]["questions"])
    assert errs == []
    val_errs = validate(1, doc["docs"]["questions"], doc["docs"], doc["ctx"])
    assert val_errs == []


def test_schema_errors_message_format():
    # empty path -> "questions doc: "
    errs = schema_errors([])
    assert len(errs) == 1
    assert errs[0].startswith("questions doc: ")
    # mutated doc -> path fragment appears
    doc = set_at(base(), ["docs", "questions", "questions", 0, "id"], "X1")
    errs = schema_errors(doc["docs"]["questions"])
    assert any("questions/0/id" in e for e in errs)


def test_schema_non_array_questions():
    doc = set_at(base(), ["docs", "questions", "questions"], {})
    errs = schema_errors(doc["docs"]["questions"])
    assert any("questions" in e for e in errs)


def test_schema_non_dict_item():
    doc = append_at(base(), ["docs", "questions", "questions"], "not-a-dict")
    errs = schema_errors(doc["docs"]["questions"])
    assert any("questions" in e for e in errs)


def test_validate_ok():
    doc = base()
    errs = validate(1, doc["docs"]["questions"], doc["docs"], doc["ctx"])
    assert errs == []


def test_validate_adhyay_mismatch():
    doc = set_at(base(), ["docs", "questions", "adhyay"], 2)
    errs = validate(1, doc["docs"]["questions"], doc["docs"], doc["ctx"])
    assert any("does not match" in e for e in errs)


def test_validate_adhyay_check_first():
    # both adhyay mismatch and duplicate id -> adhyay message first
    dup = {"id": "Q1", "text": "duplicate?", "scene_id": "S1"}
    doc = append_at(base(), ["docs", "questions", "questions"], dup)
    doc = set_at(doc, ["docs", "questions", "adhyay"], 2)
    errs = validate(1, doc["docs"]["questions"], doc["docs"], doc["ctx"])
    assert errs[0].startswith("questions adhyay")


def test_validate_duplicate_id():
    dup = {"id": "Q1", "text": "duplicate?", "scene_id": "S1"}
    doc = append_at(base(), ["docs", "questions", "questions"], dup)
    errs = validate(1, doc["docs"]["questions"], doc["docs"], doc["ctx"])
    assert any("Q1" in e for e in errs)


def test_validate_scene_missing():
    doc = set_at(base(), ["docs", "questions", "questions", 0, "scene_id"], "S99")
    errs = validate(1, doc["docs"]["questions"], doc["docs"], doc["ctx"])
    assert any("Q1" in e for e in errs)


def test_validate_missing_scenes_doc():
    # missing scenes key counts as empty -> scene_id S1 no longer resolves
    doc = delete_at(base(), ["docs", "scenes"])
    errs = validate(1, doc["docs"]["questions"], doc["docs"], doc["ctx"])
    assert any("Q1" in e for e in errs)


def test_validate_odd_data_no_raise():
    # docs not a dict
    errs = validate(1, base()["docs"]["questions"], None, base()["ctx"])
    assert isinstance(errs, list)
    # scenes not a dict
    errs = validate(1, base()["docs"]["questions"], {"scenes": "not-a-dict"}, base()["ctx"])
    assert isinstance(errs, list)
    # scenes list not a list
    errs = validate(1, base()["docs"]["questions"], {"scenes": {"scenes": "not-a-list"}}, base()["ctx"])
    assert isinstance(errs, list)
    # doc not a dict
    errs = validate(1, "not-a-dict", base()["docs"], base()["ctx"])
    assert isinstance(errs, list)
    # unhashable id (list)
    doc = {"adhyay": 1, "questions": [{"id": ["Q1"], "text": "t"}]}
    errs = validate(1, doc, base()["docs"], base()["ctx"])
    assert isinstance(errs, list)
    # unhashable scene_id (list)
    doc = {"adhyay": 1, "questions": [{"id": "Q1", "text": "t", "scene_id": ["S1"]}]}
    errs = validate(1, doc, base()["docs"], base()["ctx"])
    assert isinstance(errs, list)
