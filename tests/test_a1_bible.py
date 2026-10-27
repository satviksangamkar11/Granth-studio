"""Draft bible builder checks (synthetic input + the real draft catalog counts)."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_s = importlib.util.spec_from_file_location("a1_bible", ROOT / "scripts" / "source" / "a1_bible.py")
bb = importlib.util.module_from_spec(_s)
_s.loader.exec_module(bb)

MD = """- **Hero** (`GM`): a tall man.
- **Village** (`VIL`): flat plain.
| OC-01 | How old is he? | about 30 |
"""
CAT = [{"image_id": "CH_GM", "kind": "character_ref", "scenes": ["S1-S2"], "preset_roles": [], "entities": ["GM"], "references": [], "source_refs": ["A1:70"], "owner_choice": ["OC-01 age look"], "covers_shots": 0},
       {"image_id": "LOC_VIL", "kind": "location", "scenes": ["S2"], "preset_roles": ["bg"], "entities": ["VIL"], "references": [], "source_refs": [], "owner_choice": [], "covers_shots": 2},
       {"image_id": "PR_POT", "kind": "prop", "scenes": ["S2"], "preset_roles": [], "entities": [], "references": [], "source_refs": ["A1:96"], "owner_choice": [], "covers_shots": 1}]


def test_scene_ranges_expand_and_entities_split_into_characters_places_props():
    assert bb.scenes_of(["S1-S3", "S2"]) == ["S1", "S2", "S3"]
    r = bb.build(MD, CAT, {"mr": {"gajanan": "v1"}, "hi": {}})
    assert set(r["bible"]["characters"]) == {"GM"} and r["bible"]["characters"]["GM"]["voice_ids"]["mr"] == "v1"
    assert "VIL" in r["bible"]["places"] and "PR_POT" in r["bible"]["props"]
    assert r["unresolved"]["items"][0]["code"] == "OC-01" and r["unresolved"]["items"][0]["proposed_default"] == "about 30"


def test_a_scene_packet_holds_only_what_that_scene_needs():
    r = bb.build(MD, CAT)
    assert [i["image_id"] for i in r["packets"]["S1"]["catalog"]] == ["CH_GM"]
    assert {i["image_id"] for i in r["packets"]["S2"]["catalog"]} == {"CH_GM", "LOC_VIL", "PR_POT"} and r["packets"]["S9"]["catalog"] == []


def test_the_real_draft_catalog_builds_nine_packets_and_every_open_question_is_listed_once():
    cat = json.loads((ROOT / "canon" / "drafts" / "A1_image_catalog_DRAFT.json").read_text(encoding="utf-8"))
    r = bb.build((ROOT / "docs" / "pilot" / "A1_image_prompts.md").read_text(encoding="utf-8"), cat)
    codes = [i["code"] for i in r["unresolved"]["items"]]
    assert len(r["packets"]) == 9 and len(codes) == len(set(codes)) and len(r["bible"]["images"]) == len(cat)
