"""Acceptance tests pinned to the REAL Adhyay 1 revision (canon/story_split_edits/A1_rev1.json): the owner's rules, the computed counts, and that the scene limit is nine (single-digit ids S1-S9, a tenth is rejected) while every other rule still bites."""
import copy
import importlib.util
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ss", ROOT / "scripts" / "source" / "story_split.py")
ss = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ss)
EDITS = json.loads((ROOT / "canon" / "story_split_edits" / "A1_rev1.json").read_text(encoding="utf-8"))
OVIS = {json.loads(l)["ovi"]: json.loads(l)["text"] for l in (ROOT / "canon" / "packets" / "adhyay_01" / "adhyay_01_ovis_hj.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
OUT = {"stories": EDITS["stories"], "unfilmed_ranges": EDITS["unfilmed_ranges"]}
NUMS = sorted(OVIS)
PLANNED = [s["shot_budget"] for s in EDITS["stories"][0]["scenes"]]          # the canonical planned shots (from the audio timing)


def facing_text() -> str:
    """Everything that can reach the film: titles, briefs, evidence reasons, direction notes (NOT the research-evidence block)."""
    st = EDITS["stories"][0]
    parts = [st["title"]] + [s["brief"] for s in st["scenes"]] + [e["reason"] for e in st["boundary_evidence"]] + EDITS["direction_notes"] + [u["reason"] for u in EDITS["unfilmed_ranges"]]
    return "\n".join(parts)


def test_the_real_revision_validates_and_owns_every_ovi_once():
    assert ss.validate_split(OUT, NUMS, 1)[0] == []
    assert len(NUMS) == 146 and NUMS == list(range(1, 147))


def test_one_story_nine_scenes_and_the_exact_title():
    st = EDITS["stories"][0]
    assert len(EDITS["stories"]) == 1 and len(st["scenes"]) == 9 and st["arc"] == "complete"
    assert st["title"] == "First Appearance in Shegaon and Recognition at Devidas's Feast"


def test_counts_come_from_the_data_not_from_text():
    macro = ss.build_macro(OUT, 1, NUMS, "a" * 64)
    sm = ss.split_summary(macro)
    assert [r["shots"] for r in sm["rows"]] == PLANNED
    assert sm["scenes"] == 9 and sm["shots"] == sum(PLANNED) and sm["seconds"] == 6 * sum(PLANNED)
    assert sm["rows"][0]["shots"] == 2                                                       # the opening is exactly two shots
    assert len(ss.parts(macro)) >= 1 and sum(p["shot_budget"] for p in ss.parts(macro)) == sum(PLANNED)


def test_the_rendered_story_text_carries_the_computed_numbers():
    macro = ss.build_macro(OUT, 1, NUMS, "a" * 64)
    text = ss.render_doc((ROOT / "docs" / "pilot" / "A1_story_template.md").read_text(encoding="utf-8"), macro, ss.sha_of(macro), EDITS)
    assert "{{" not in text and f"9 scenes, {sum(PLANNED)} shots" in text and ss.fmt_runtime(6 * sum(PLANNED)) in text
    assert "First Appearance in Shegaon and Recognition at Devidas's Feast" in text
    for sc in EDITS["stories"][0]["scenes"]:
        assert sc["brief"] in text                                                           # the canonical briefs appear verbatim


def test_year_only_no_day_or_month_anywhere_the_film_can_see():
    t = facing_text()
    assert "1878" in t and not re.search(r"magh|saptami|vadya|february|january|\b\d{1,2} (feb|jan|mar)", t, re.I)


def test_sajjangad_samarth_and_nath_yogis_are_not_film_facing_but_the_evidence_is_kept():
    t = facing_text()
    assert not re.search(r"sajjangad|samarth ramdas|nath|gorakh|kanifa|changdev", t, re.I) or "no Sajjangad" in t     # only the prohibition itself may name them
    for banned in ("came from Sajjangad", "return of Samarth", "unusual births"):
        assert banned not in t
    ev = EDITS["research_evidence_not_narrated"]
    assert set(ev) == {"A1:75-76", "A1:77-79", "A1:80-82"} and "Sajjangad" in ev["A1:75-76"] and "no strong proof" in ev["A1:75-76"]


def test_the_owners_story_rules_are_in_the_briefs_and_notes():
    sc = {s["scene_id"]: s for s in EDITS["stories"][0]["scenes"]}
    assert sc["S1"]["ovi_range"] == [70, 83] and "historical Shegaon" in sc["S1"]["brief"] and "No birthplace, childhood, parents or journey" in sc["S1"]["brief"]
    assert sc["S2"]["ovi_range"] == [84, 96] and "food is Brahman" in sc["S2"]["brief"] and "bandi" in sc["S2"]["brief"] and "digambar" in sc["S2"]["brief"]
    assert "bow to him in silence" in sc["S4"]["brief"] and "112" in sc["S4"]["brief"]
    assert sc["S5"]["ovi_range"] == [113, 118] and "mixes all the dishes together" in sc["S5"]["brief"]
    assert "speaker unclear" in sc["S6"]["brief"] and "bless" not in sc["S6"]["brief"].lower()
    assert "Damodarpant" in sc["S7"]["brief"] and "Bankatlal" not in sc["S7"]["brief"] and "Devidas's house" in sc["S7"]["brief"]
    assert "Damodarpant" in sc["S8"]["brief"]
    assert sc["S9"]["ovi_range"] == [138, 144] and sc["S9"]["shot_budget"] >= 5 and "runs off like the wind" in sc["S9"]["brief"] and "destination" not in sc["S9"]["brief"].lower().replace("no destination", "")
    notes = "\n".join(EDITS["direction_notes"])
    assert "NO destination" in notes and "unclear speaker" in notes and "READY to fall" in notes and "do not shorten it" in notes


def test_every_brief_is_within_300_characters_and_evidence_cites_the_boundaries():
    st = EDITS["stories"][0]
    assert all(len(s["brief"]) <= 300 for s in st["scenes"])
    assert {e["ovi"] for e in st["boundary_evidence"]} >= {"A1:70", "A1:144"} and st["ovi_range"] == [70, 144]


def test_nine_scenes_pass_a_tenth_is_rejected_and_no_other_rule_is_weaker():
    base = copy.deepcopy(OUT)
    # the limit itself: nine scenes (single-digit ids S1-S9, as the director's shot ids need) pass the schema, a tenth does not
    nine = {"stories": [{"story_id": "A1-T1", "title": "t", "ovi_range": [1, 9], "arc": "complete",
                         "boundary_evidence": [{"ovi": "A1:1", "reason": "r"}, {"ovi": "A1:9", "reason": "r"}],
                         "scenes": [{"scene_id": f"S{k}", "ovi_range": [k, k], "brief": "b", "context_ovi_ids": [], "shot_budget": 2} for k in range(1, 10)]}], "unfilmed_ranges": []}
    assert ss.validate_split(nine, list(range(1, 10)), 1)[0] == []
    tenth = copy.deepcopy(nine)
    tenth["stories"][0]["ovi_range"] = [1, 10]
    tenth["stories"][0]["boundary_evidence"][1]["ovi"] = "A1:10"
    tenth["stories"][0]["scenes"].append({"scene_id": "S10", "ovi_range": [10, 10], "brief": "b", "context_ovi_ids": [], "shot_budget": 2})
    assert any("too long" in e or "does not match" in e for e in ss.validate_split(tenth, list(range(1, 11)), 1)[0])
    # every other rule still bites on the real revision
    for name, mutate, expect in [
        ("overlap", lambda o: o["stories"][0]["scenes"][2].__setitem__("ovi_range", [96, 105]), "already owned"),
        ("gap", lambda o: o["unfilmed_ranges"].pop(), "not owned"),
        ("scene id skip", lambda o: o["stories"][0]["scenes"][3].__setitem__("scene_id", "S5"), "consecutive"),
        ("budget 17", lambda o: o["stories"][0]["scenes"][0].__setitem__("shot_budget", 17), "maximum"),
        ("context inside scene", lambda o: o["stories"][0]["scenes"][1].__setitem__("context_ovi_ids", ["A1:90"]), "inside the scene"),
        ("evidence missing last", lambda o: o["stories"][0]["boundary_evidence"].pop(), "first and last ovi"),
    ]:
        bad = copy.deepcopy(base)
        mutate(bad)
        assert any(expect in e for e in ss.validate_split(bad, NUMS, 1)[0]), name


def test_the_macro_review_records_why_it_is_no_check():
    r = ss.clean_macro_review({"answers": [{"q": "M1", "where": "A1-T1, S1, S3", "answer": "no", "evidence": "ovi 70 says so"}]}, {"A1-T1", "S1", "S3"})
    assert r["verdict"] == "NO_CHECK" and "not 'macro' or a real story/scene id" in r["why"]
    assert "not a JSON object" in ss.clean_macro_review("junk")["why"] or "no usable answers" in ss.clean_macro_review("junk")["why"]


def test_every_number_in_the_story_text_comes_from_the_data_including_each_scene_heading():
    macro = ss.build_macro(OUT, 1, NUMS, "a" * 64)
    text = ss.render_doc((ROOT / "docs" / "pilot" / "A1_story_template.md").read_text(encoding="utf-8"), macro, ss.sha_of(macro), EDITS)
    sm = ss.split_summary(macro)
    heads = {int(m.group(1)): (m.group(2), int(m.group(3))) for m in re.finditer(r"\*\*Scene (\d) \(ovi ([0-9-]+), (\d+) shots\)\.", text)}
    assert len(heads) == 9
    for r in sm["rows"]:
        n = int(r["scene_id"][1:])
        assert heads[n] == (f"{r['ovi_range'][0]}-{r['ovi_range'][1]}", r["shots"]), n          # the heading of every scene equals the split
    assert f"{sm['shots']} shots" in text and not re.search(r"\b37 shots\b|\b222 seconds\b", text)
    committed = (ROOT / "docs" / "pilot" / "A1_story_for_approval.md").read_text(encoding="utf-8")
    assert re.findall(r"\*\*Scene \d \(ovi [0-9-]+, \d+ shots\)", committed) == re.findall(r"\*\*Scene \d \(ovi [0-9-]+, \d+ shots\)", text)      # the saved document matches the data
