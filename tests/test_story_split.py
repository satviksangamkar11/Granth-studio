"""Synthetic checks for the story-first planner: split validation (seeded failures + clean controls), code-derived parts, the macro review, and the one-repair pipeline. No network."""
import copy
import importlib.util
import json
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("ss", Path(__file__).resolve().parents[1] / "scripts" / "source" / "story_split.py")
ss = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ss)

NUMS = list(range(1, 11))
INFO = {"status": 200, "wall_s": 0.0, "finish": "stop"}


def scene(no, a, b, budget=3, ctx=None):
    return {"scene_id": f"S{no}", "ovi_range": [a, b], "brief": f"scene {no}", "context_ovi_ids": ctx or [], "shot_budget": budget}


def story(k, a, b, scenes, arc="complete"):
    return {"story_id": f"A1-T{k}", "title": f"story {k}", "ovi_range": [a, b], "arc": arc,
            "boundary_evidence": [{"ovi": f"A1:{a}", "reason": "it begins here"}, {"ovi": f"A1:{b}", "reason": "it ends here"}], "scenes": scenes}


def split():
    return {"stories": [story(1, 4, 8, [scene(1, 4, 6), scene(2, 7, 8)])],
            "unfilmed_ranges": [{"ovi_range": [1, 3], "kind": "invocation", "reason": "praise"}, {"ovi_range": [9, 10], "kind": "closing", "reason": "author's closing"}]}


def check(out):
    return ss.validate_split(out, NUMS, 1)


def errs(out):
    return " | ".join(check(out)[0])


# ----------------------------------------------------------------------------- clean controls

def test_clean_single_story_split_has_no_errors():
    assert check(split()) == ([], [])


def test_half_story_two_stories_and_a_context_ovi_are_fine():
    out = split()
    out["stories"][0]["arc"] = "begins"
    assert check(out)[0] == []
    two = {"stories": [story(1, 1, 3, [scene(1, 1, 3, 2, ["A1:4"])]), story(2, 4, 8, [scene(2, 4, 8, 4, ["A1:3"])], "ends")],
           "unfilmed_ranges": [{"ovi_range": [9, 10], "kind": "closing", "reason": "x"}]}
    assert check(two) == ([], [])                                                        # shared boundary read as context, owned once


def test_an_unfilmed_range_inside_a_story_is_allowed():
    out = {"stories": [story(1, 1, 10, [scene(1, 1, 4), scene(2, 8, 10)])], "unfilmed_ranges": [{"ovi_range": [5, 7], "kind": "commentary", "reason": "author's comment"}]}
    assert check(out)[0] == []


# ----------------------------------------------------------------------------- seeded failures: all must be caught

def seeded(name):
    out = split()
    st = out["stories"][0]
    if name == "gap":
        out["unfilmed_ranges"][1]["ovi_range"] = [10, 10]                                # ovi 9 owned by nobody
    elif name == "overlap_scenes":
        st["scenes"][1]["ovi_range"] = [6, 8]
    elif name == "unfilmed_overlaps_scene":
        out["unfilmed_ranges"][0]["ovi_range"] = [1, 4]
    elif name == "story_range_mismatch":
        st["ovi_range"] = [4, 9]
    elif name == "missing_last_boundary_evidence":
        st["boundary_evidence"][1]["ovi"] = "A1:7"
    elif name == "evidence_wrong_chapter":
        st["boundary_evidence"][0]["ovi"] = "A2:4"
    elif name == "evidence_outside_story":
        st["boundary_evidence"].append({"ovi": "A1:2", "reason": "x"})
    elif name == "scene_numbers_skip":
        st["scenes"][1]["scene_id"] = "S3"
    elif name == "story_id_out_of_order":
        st["story_id"] = "A1-T2"
    elif name == "budget_too_big":
        st["scenes"][0]["shot_budget"] = 17
    elif name == "unknown_key":
        st["scenes"][0]["notes"] = "x"
    elif name == "outside_chapter":
        out["unfilmed_ranges"][1]["ovi_range"] = [9, 12]
    elif name == "reversed_range":
        st["scenes"][0]["ovi_range"] = [6, 4]
    elif name == "context_outside_chapter":
        st["scenes"][0]["context_ovi_ids"] = ["A1:99"]
    elif name == "scenes_out_of_order":
        st["scenes"][0]["ovi_range"], st["scenes"][1]["ovi_range"] = [7, 8], [4, 6]
        st["scenes"][0]["scene_id"], st["scenes"][1]["scene_id"] = "S1", "S2"
    elif name == "bad_kind":
        out["unfilmed_ranges"][0]["kind"] = "boring"
    elif name == "no_stories":
        out["stories"] = []
    elif name == "empty_text":
        st["title"] = ""
    return out


EXPECT = {"gap": "not owned by any scene", "overlap_scenes": "already owned", "unfilmed_overlaps_scene": "already owned", "story_range_mismatch": "must equal its first scene start",
          "missing_last_boundary_evidence": "must cite the story's first and last ovi", "evidence_wrong_chapter": "must cite the story's first and last ovi", "evidence_outside_story": "outside the story",
          "scene_numbers_skip": "consecutive", "story_id_out_of_order": "story ids must be", "budget_too_big": "maximum", "unknown_key": "notes", "outside_chapter": "outside the chapter",
          "reversed_range": "reversed", "context_outside_chapter": "outside chapter 1", "scenes_out_of_order": "in order", "bad_kind": "boring", "no_stories": "non-empty", "empty_text": "title"}


@pytest.mark.parametrize("name", sorted(EXPECT))
def test_every_seeded_split_failure_is_caught(name):
    assert EXPECT[name] in errs(seeded(name)), (name, errs(seeded(name)))


def test_many_stories_and_big_stories_warn_the_owner():
    four = {"stories": [story(k, 2 * k - 1, 2 * k, [scene(k, 2 * k - 1, 2 * k)]) for k in range(1, 5)],
            "unfilmed_ranges": [{"ovi_range": [9, 10], "kind": "closing", "reason": "x"}]}
    e, w = check(four)
    assert e == [] and any("4 stories" in x for x in w)
    big = {"stories": [story(1, 1, 10, [scene(1, 1, 3, 6), scene(2, 4, 6, 6), scene(3, 7, 10, 6)])], "unfilmed_ranges": []}
    assert any("several ordered parts" in x for x in check(big)[1])


# ----------------------------------------------------------------------------- hash and parts

def test_macro_is_completed_by_code_and_hash_changes_with_any_edit():
    m = ss.build_macro(split(), 1, NUMS, "a" * 64)
    assert m["source_range"] == [1, 10] and m["chapter"] == 1 and m["schema_version"] == 1 and m["source_sha256"] == "a" * 64
    h = ss.sha_of(m)
    assert h == ss.sha_of(copy.deepcopy(m))
    m2 = copy.deepcopy(m)
    m2["stories"][0]["title"] = "other"
    assert ss.sha_of(m2) != h


def test_parts_group_whole_scenes_within_two_scenes_and_twelve_shots():
    m = {"stories": [story(1, 1, 8, [scene(1, 1, 2, 6), scene(2, 3, 4, 6), scene(3, 5, 6, 2), scene(4, 7, 8, 2)]), story(2, 9, 10, [scene(5, 9, 10, 4)])]}
    got = [(p["part_id"], p["scene_ids"], p["shot_budget"]) for p in ss.parts(m)]
    assert got == [("A1-T1-P1", ["S1", "S2"], 12), ("A1-T1-P2", ["S3", "S4"], 4), ("A1-T2-P1", ["S5"], 4)]
    m3 = {"stories": [story(1, 1, 6, [scene(1, 1, 2, 6), scene(2, 3, 4, 6), scene(3, 5, 6, 6)])]}
    assert [p["scene_ids"] for p in ss.parts(m3)] == [["S1", "S2"], ["S3"]]


# ----------------------------------------------------------------------------- macro review

def yes_all(where="macro"):
    return {"answers": [{"q": q, "where": where, "answer": "yes", "evidence": "ovi 4 says so"} for q in sorted(ss.MACRO_IDS)]}


def no(q, where="S1"):
    return {"q": q, "where": where, "answer": "no", "evidence": "ovi 5 contradicts it", "fix": "move the boundary"}


def test_macro_review_needs_all_six_answers_with_evidence_and_real_ids():
    assert ss.clean_macro_review(yes_all(), {"A1-T1", "S1"})["verdict"] == "PASS"
    blocked = yes_all()
    blocked["answers"] = [a for a in blocked["answers"] if a["q"] != "M3"] + [no("M3")]
    r = ss.clean_macro_review(blocked, {"A1-T1", "S1"})
    assert r["verdict"] == "BLOCK" and r["problems"][0]["kind"] == "M3"
    short = yes_all()
    short["answers"] = short["answers"][:-1]
    assert ss.clean_macro_review(short)["verdict"] == "NO_CHECK" and ss.clean_macro_review(short)["missing"] == ["M6"]
    for bad in (None, {}, {"answers": []}, {"answers": [{"q": "M1", "where": "macro", "answer": "yes", "evidence": " "}]},
                {"answers": [{"q": "M9", "where": "macro", "answer": "yes", "evidence": "e"}]}):
        assert ss.clean_macro_review(bad)["verdict"] == "NO_CHECK"
    assert ss.clean_macro_review({"answers": [dict(yes_all()["answers"][0], where="S9")] + yes_all()["answers"][1:]}, {"S1"})["verdict"] == "NO_CHECK"


# ----------------------------------------------------------------------------- pipeline: at most two director calls

FILES = {"analysis": "## 1. Chapter overview\nover\n## 2. Story list\nstories\n## 3. Characters\nc\n", "addendum": "## D. Continuity\ncont\n## E. End\n", "answers": "answers",
         "glossary": "## Adhyay 1\ng\n## Adhyay 2\nh\n"}
OVIS = {n: f"ovi text {n}" for n in NUMS}


class Fake:
    def __init__(self, name, replies, info=None):
        self.name, self.replies, self.calls, self.secrets, self.paid, self.info = name, replies, [], (), False, info or dict(INFO)

    def call(self, system, user, max_tokens=None):
        self.calls.append((user, max_tokens))
        r = self.replies[min(len(self.calls) - 1, len(self.replies) - 1)]
        return (r if isinstance(r, str) else json.dumps(r, ensure_ascii=False)), dict(self.info)


def plan(director, reviewers=(), max_tokens=16000):
    return ss.plan_stories(director, list(reviewers), FILES, OVIS, 1, "b" * 64, max_tokens)


def test_prompt_has_every_ovi_the_minimal_research_and_no_old_scene_split():
    system, user = ss.build_macro_prompt(FILES, OVIS, 1)
    assert all(f"A1:{n}: ovi text {n}" in user for n in NUMS) and "over" in user and "stories" in user and "cont" in user and "answers" in user and "g\n" in user
    assert "Scene 1" not in user and "UNIQUE" not in system and "EVERY ovi" in system


def test_clean_plan_is_valid_with_a_hash_parts_and_one_director_call():
    d, r = Fake("kimi", [split()]), Fake("nemo", [yes_all()])
    out = plan(d, [r])
    assert out["result"] == "VALID" and len(out["macro_sha256"]) == 64 and out["macro"]["source_sha256"] == "b" * 64 and out["parts"][0]["part_id"] == "A1-T1-P1"
    assert len(d.calls) == 1 and d.calls[0][1] == 16000


def test_validator_failure_gets_one_repair_and_then_stops_being_repairable():
    d, r = Fake("kimi", [seeded("gap"), split(), seeded("gap")]), Fake("nemo", [yes_all()])
    out = plan(d, [r])
    assert out["result"] == "VALID" and out["repairs"][0]["status"] == "USED" and len(d.calls) == 2
    d2 = Fake("kimi", [seeded("gap"), seeded("gap"), split()])
    assert plan(d2, [r])["result"] == "INVALID" and len(d2.calls) == 2


def test_reviewer_block_gets_one_repair_and_a_check_only():
    blocked = yes_all()
    blocked["answers"] = [a for a in blocked["answers"] if a["q"] != "M3"] + [no("M3", "S1")]
    d, r = Fake("kimi", [split(), split()]), Fake("nemo", [blocked, yes_all()])
    out = plan(d, [r])
    assert out["result"] == "VALID" and len(d.calls) == 2 and len(r.calls) == 2 and out["reviews"][0]["verdict"] == "BLOCK" and out["final_reviews"][0]["verdict"] == "PASS"
    d2, r2 = Fake("kimi", [split(), split(), split()]), Fake("nemo", [blocked])
    assert plan(d2, [r2])["result"] == "REVIEW_BLOCKED" and len(d2.calls) == 2


def test_missing_review_and_no_reviewers_are_never_valid():
    assert plan(Fake("kimi", [split()]), [Fake("nemo", ["not json"])])["result"] == "NO_CHECK"
    assert plan(Fake("kimi", [split()]))["result"] == "UNREVIEWED"


def test_json_retry_uses_the_second_call_and_leaves_no_repair():
    d = Fake("kimi", ["no json", seeded("gap"), split()])
    out = plan(d, [Fake("nemo", [yes_all()])])
    assert out["result"] == "INVALID" and len(d.calls) == 2 and out["repairs"] == []


def test_truncated_or_failed_director_reply_stops():
    from_dt = ss.dt
    with pytest.raises(from_dt.DirectorStop):
        plan(Fake("kimi", [split()], {"status": 200, "wall_s": 0, "finish": "length"}))
    with pytest.raises(from_dt.DirectorStop):
        plan(Fake("kimi", [split()], {"status": 200, "wall_s": 0, "finish": "stop", "error": "no usage in reply"}))


# ----------------------------------------------------------------------------- Codex planner review (2026-10-26)

def test_split_ownership_must_equal_the_chapter_and_context_must_point_outside():
    gappy = ss.validate_split(split(), [1, 2, 3, 4, 6, 7, 8, 9, 10], 1)[0]
    assert any("does not exist in this chapter" in e for e in gappy) or any("contiguous" in e for e in gappy)
    assert any("contiguous" in e for e in ss.validate_split(split(), [], 1)[0])
    out = split()
    out["stories"][0]["scenes"][0]["context_ovi_ids"] = ["A1:4"]
    assert any("lies inside the scene's own range" in e for e in check(out)[0])
    out["stories"][0]["scenes"][0]["context_ovi_ids"] = ["A1:3", "A1:3"]
    assert any("must be unique" in e for e in check(out)[0])
    out = split()
    out["unfilmed_ranges"][0]["reason"] = "   "
    assert check(out)[0]


def test_an_invalid_plan_keeps_the_raw_output_apart_and_the_report_does_not_crash():
    d = Fake("kimi", [seeded("gap"), seeded("gap")])
    out = plan(d, [Fake("nemo", [yes_all()])])
    assert out["result"] == "INVALID" and out["macro"] is None and out["raw_split"]["stories"]
    text = ss.macro_text(out)
    assert "Rejected raw output" in text and "INVALID" in text


def test_macro_review_evidence_must_cite_an_ovi_number():
    bad = yes_all()
    bad["answers"][0]["evidence"] = "looks fine"
    assert ss.clean_macro_review(bad)["verdict"] == "NO_CHECK"


def test_macro_approval_goes_stale_when_any_packet_file_changes():
    spec2 = importlib.util.spec_from_file_location("dr3", Path(__file__).resolve().parents[1] / "scripts" / "source" / "director_run.py")
    dr = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(dr)
    m = dr.new_manifest("film")
    packet = {"adhyay_01_ovis_hj.jsonl": "h1", "frozen_copies/x.md": "h2"}
    dr.set_item(m, "macro:A1", "m1")
    dr.add_dep(m, "macro:A1", dr.set_packet_items(m, packet))
    dr.approve(m, "story_split", "A1", ["macro:A1"], "owner")
    assert dr.approval_state(m, "story_split", "A1") == "APPROVED"
    dr.set_packet_items(m, {**packet, "frozen_copies/x.md": "CHANGED"})
    assert dr.approval_state(m, "story_split", "A1") == "STALE"


def test_a_refused_resume_does_not_leave_the_run_locked(tmp_path):
    spec2 = importlib.util.spec_from_file_location("dr4", Path(__file__).resolve().parents[1] / "scripts" / "source" / "director_run.py")
    dr = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(dr)
    dr.open_run(tmp_path, "r", {"x": 1}).release()
    with pytest.raises(dr.RunError):
        dr.open_run(tmp_path, "r", {"x": 2}, resume=True)
    dr.open_run(tmp_path, "r", {"x": 1}, resume=True).release()


# ----------------------------------------------------------------------------- owner-directed revision (no director call)

def test_a_revision_is_validated_and_cross_checked_without_any_director_call():
    r = Fake("nemo", [yes_all()])
    out = ss.revise_split(split(), [r], FILES, OVIS, 1, "b" * 64, "c" * 64, "owner edit")
    assert out["result"] == "VALID" and out["revised_from"] == "c" * 64 and out["note"] == "owner edit" and len(out["macro_sha256"]) == 64 and out["repairs"] == []
    assert len(r.calls) == 1


def test_a_bad_revision_is_invalid_and_never_repaired_or_reviewed():
    r = Fake("nemo", [yes_all()])
    out = ss.revise_split(seeded("gap"), [r], FILES, OVIS, 1, "b" * 64, "c" * 64, "x")
    assert out["result"] == "INVALID" and out["macro"] is None and out["raw_split"] and len(r.calls) == 0
    assert ss.revise_split(split(), [], FILES, OVIS, 1, "b" * 64, "c" * 64, "x")["result"] == "UNREVIEWED"
    assert ss.revise_split(split(), [Fake("nemo", ["no json"])], FILES, OVIS, 1, "b" * 64, "c" * 64, "x")["result"] == "NO_CHECK"
