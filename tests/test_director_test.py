"""Synthetic checks for the director validator, reviewer rubric, shot-locked repair and the one-repair pipeline. No network, no keys."""
import copy
import importlib.util
import json
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("dt", Path(__file__).resolve().parents[1] / "scripts" / "source" / "director_test.py")
dt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dt)

PRESETS = {"03_slow_cinematic_push": ["img"], "09_dialogue_composition": ["left", "right"]}
PJ = {"03_slow_cinematic_push": {"segments": [{"layers": [{"asset": "img"}], "camera": {"start": {"zoom": 1.0}, "end": {"zoom": 1.2}}}]},
      "09_dialogue_composition": {"segments": [{"layers": [{"asset": "left"}, {"asset": "right"}], "camera": {"start": {"zoom": 1.0}, "end": {"zoom": 1.13}}}]}}
OVIS = {10: "अ ब क ड", 11: "इ ई उ ऊ"}
CTX = {"packet_text": "Maharaj sits on the temple road with a brass pot. Bankatlal watches him.", "speakers": {"Shri Gajanan Maharaj", "Bankatlal"},
       "preset_json": PJ, "prop_materials": {}, "speaker_rows": {}}
PUSH, DIALOGUE = "03_slow_cinematic_push", "09_dialogue_composition"


def shot(i, preset=PUSH, assets=None, **kw):
    s = {"shot_id": f"S1-{i}", "ovi_ids": ["A1:10"], "preset": preset, "assets": assets or {"img": f"road{i}"}, "action": "The camera pushes in on the seated figure",
         "held_pose": "Maharaj seated, hands on knees", "needs": ["none"], "performance": "calm held pose", "camera": "slow push in", "dialogue": [],
         "claims": [{"kind": "person", "term": "Maharaj", "source": "PACKET"}], "staging": ["STAGING: warm light"], "transition_out": "cut"}
    s.update(kw)
    return s


def scene(shots, images=None):
    used = sorted({v for s in shots for v in s["assets"].values()})
    return {"scene_id": "S1", "chapter": 1, "ovi_range": [10, 11], "goal": "g", "turn": {"ovi": "A1:10", "text": "t"}, "shots": shots,
            "images_needed": images or [{"image_id": u, "description": f"{u} picture"} for u in used]}


def good():
    return scene([shot(1), shot(2, DIALOGUE, {"left": "left_pose", "right": "right_pose"}, ovi_ids=["A1:11"])])


def check(sc, ctx=None, chapter=1):
    return dt.validate_scene(sc, PRESETS, OVIS, (10, 11), ctx or CTX, chapter)


def errs(sc, ctx=None):
    return " | ".join(check(sc, ctx)[0])


# ----------------------------------------------------------------------------- clean controls: zero false alarms

def test_clean_scene_has_no_errors_and_no_warnings():
    assert check(good()) == ([], [])


def test_clean_dialogue_with_registered_speaker_and_exact_quote():
    d = [{"speaker": "Bankatlal", "ovi": "A1:10", "marathi": "अ ब क", "meaning_en": "m"}]
    assert check(scene([shot(1, dialogue=d), shot(2)]))[0] == []
    d = [{"speaker": "Shri Gajanan Maharaj", "ovi": "A1:10", "marathi": "ब क ड", "meaning_en": "m"}, {"speaker": "unclear", "ovi": "A1:10", "marathi": "अ ब क", "meaning_en": "m"}]
    assert check(scene([shot(1, dialogue=d), shot(2)]))[0] == []


def test_scenery_the_research_names_is_not_invented():
    ctx = {**CTX, "packet_text": CTX["packet_text"] + " A branch hangs over the road under the sky."}
    sc = scene([shot(1, performance="a branch hangs over the road under the sky"), shot(2)])
    assert check(sc, ctx)[0] == []


def test_labelled_staging_scenery_passes_but_asks_for_the_owner():
    sc = scene([shot(1, camera="slow push in under the sky", claims=[{"kind": "scenery", "term": "sky", "source": "STAGING"}]), shot(2)])
    e, w = check(sc)
    assert e == [] and any("needs the owner's approval" in x for x in w)


def test_need_new_with_reason_is_valid_structure_but_unresolved():
    sc = scene([shot(1, "NEED_NEW", {}, need_new_reason="needs a walking cycle", needs=["walking"]), shot(2)])
    e, _ = check(sc)
    assert e == [] and dt.scene_status(sc, e) == "UNRESOLVED"
    assert dt.scene_status(good(), []) == "VALID" and dt.scene_status(good(), ["x"]) == "INVALID"


# ----------------------------------------------------------------------------- seeded failures: every one must be caught

def seeded(name):
    sc = good()
    s1 = sc["shots"][0]
    if name == "unsupported_action":
        s1["action"] = "Maharaj raises his hand"
    elif name == "hand_raised_state":
        s1["action"] = "Maharaj's hand raised"
    elif name == "lips_move":
        s1["performance"] = "his lips move silently"
    elif name == "needs_lip_sync":
        s1["needs"] = ["lip_sync"]
    elif name == "wrong_speaker":
        s1["dialogue"] = [{"speaker": "Sultan", "ovi": "A1:10", "marathi": "अ ब क", "meaning_en": "m"}]
    elif name == "broken_asset_ref":
        s1["assets"]["img"] = "ghost"
    elif name == "dialogue_outside_shot":
        s1["dialogue"] = [{"speaker": "Bankatlal", "ovi": "A1:11", "marathi": "इ ई उ", "meaning_en": "m"}]
    elif name == "quote_not_in_ovi":
        s1["dialogue"] = [{"speaker": "Bankatlal", "ovi": "A1:10", "marathi": "ज्ञ ज्ञ ज्ञ", "meaning_en": "m"}]
    elif name == "invented_branch":
        s1["performance"] = "a branch hangs over his head"
    elif name == "invented_sky":
        s1["camera"] = "tilt up to the sky"
    elif name == "hand_at_throat":
        s1["held_pose"] = "his hand at his throat"
    elif name == "staging_adds_person":
        s1["claims"] = [{"kind": "person", "term": "a crowd", "source": "STAGING"}]
    elif name == "unprefixed_staging":
        s1["staging"] = ["warm light"]
    elif name == "packet_claim_not_in_research":
        s1["claims"] = [{"kind": "prop", "term": "golden sword", "source": "PACKET"}]
    elif name == "event_from_other_shot":
        s1["ovi_ids"] = ["A1:10"]
        s1["claims"] = [{"kind": "event", "term": "he laughs", "source": "A1:11"}]
    elif name == "wrong_chapter_ref":
        s1["ovi_ids"] = ["A2:10"]
    elif name == "unused_declared_image":
        sc["images_needed"].append({"image_id": "spare", "description": "spare picture"})
    elif name == "prop_material_drift":
        sc["shots"][0]["claims"] = [{"kind": "prop", "term": "gadva", "source": "PACKET"}]
        sc["shots"][1]["claims"] = [{"kind": "prop", "term": "gadva", "source": "PACKET"}]
        for im in sc["images_needed"]:
            im["description"] = ("a brass gadva on the ground" if im["image_id"] == "road1" else "a clay gadva in his hand" if im["image_id"] == "left_pose" else im["description"])
    return sc


EXPECT = {"unsupported_action": "motion", "hand_raised_state": "motion", "lips_move": "motion", "needs_lip_sync": "needs ['lip_sync']", "wrong_speaker": "not a registered character",
          "broken_asset_ref": "does not declare", "dialogue_outside_shot": "own ovi_ids", "quote_not_in_ovi": "not a substring", "invented_branch": "'branch'",
          "invented_sky": "'sky'", "hand_at_throat": "'throat'", "staging_adds_person": "may not add a person", "unprefixed_staging": "must start with 'STAGING:'",
          "packet_claim_not_in_research": "not in the owner's research", "event_from_other_shot": "does not show", "wrong_chapter_ref": "outside the scene",
          "unused_declared_image": "no shot uses it", "prop_material_drift": "different materials"}


@pytest.mark.parametrize("name", sorted(EXPECT))
def test_every_seeded_failure_is_caught(name):
    assert EXPECT[name] in errs(seeded(name)), (name, errs(seeded(name)))


def test_old_schema_shape_is_rejected():
    sc = good()
    del sc["shots"][0]["held_pose"]
    assert any("held_pose" in e for e in check(sc)[0])
    sc = good()
    sc["shots"][0]["dialogue"] = [{"speaker": "Bankatlal", "ovi": "A1:10", "marathi": "अ ब क", "meaning_en": "m", "paraphrase": True}]
    assert check(sc)[0]


def test_ids_presets_roles_and_long_text():
    e = errs(scene([shot(1, assets={"wrong": "road1"}), shot(2, preset="99_nope"), shot(3, ovi_ids=["A1:99"])]))
    assert "exactly the roles" in e and "unknown preset" in e and "outside the scene" in e
    assert any("must be S1-1" in x for x in check(scene([shot(1), shot(3)]))[0])
    assert check(scene([shot(1, performance="x" * 250), shot(2)]))[0] == []
    assert check(scene([shot(1, performance="x" * 301), shot(2)]))[0] != []


def test_presets_repeat_and_camera_contradiction_warn():
    _, w = check(scene([shot(1), shot(2), shot(3)]))
    assert any("3 times in a row" in x for x in w)
    _, w = check(scene([shot(1, camera="pull back wide"), shot(2)]))
    assert any("contradicts the preset's zoom" in x for x in w)


def test_frame_ends_come_from_the_preset():
    assert dt.frame_ends(PJ[DIALOGUE]) == {"first_roles": ["left", "right"], "last_roles": ["left", "right"], "zoom": [1.0, 1.13]}


def test_quote_matching_ignores_spacing_and_danda_but_not_letters():
    assert dt.quote_in("राम आला", "तो राम आला । घरी") and dt.quote_in("आला घरी", "तो राम आला । घरी")
    assert not dt.quote_in("रामा ला", "तो राम आला । घरी") and not dt.quote_in("राम आ", "तो राम आला । घरी")
    assert not dt.quote_in("", "x") and not dt.quote_in("।।", "x")


def test_section_dialogue_rows_and_speaker_registry():
    lines = ["## A", "### Scene 1 - x (ovi 10-12)", "body", "### Scene 2 - y", "| 11 | a |", "| 20-22 | b |", "| 9-10 | c |"]
    assert dt.section(lines, r"^### Scene 1 - ", r"^### Scene |^## ") == "### Scene 1 - x (ovi 10-12)\nbody"
    assert dt.dialogue_rows(lines, 10, 12).splitlines() == ["| 11 | a |", "| 9-10 | c |"]
    names = dt.speaker_registry(["## 3. Characters", "**Shri Gajanan Maharaj (श्री गजानन महाराज)**", "- Role: x", "**Bankatlal**", "## 4. Places"])
    assert names == {"Shri Gajanan Maharaj (श्री गजानन महाराज)", "Shri Gajanan Maharaj", "Bankatlal"}


def test_finalize_derives_used_in():
    f = dt.finalize(good())
    assert [im["used_in"] for im in f["images_needed"]] == [["S1-2"], ["S1-2"], ["S1-1"]] or all(im["used_in"] for im in f["images_needed"])


# ----------------------------------------------------------------------------- shot-locked repair

def test_splice_replaces_only_the_failing_shot_and_drops_unused_images():
    old = good()
    fixed = shot(1, assets={"img": "road9"})
    new, why = dt.splice(old, {"shots": [fixed], "images_needed": [{"image_id": "road9", "description": "road9 picture"}]}, {"S1-1"})
    assert why == "" and new["shots"][1] == old["shots"][1] and new["shots"][0] == fixed
    assert {im["image_id"] for im in new["images_needed"]} == {"road9", "left_pose", "right_pose"}


@pytest.mark.parametrize("reply", [
    {"shots": [shot(1), shot(2)]},                                          # touches a locked shot
    {"shots": [shot(1)], "goal": "changed"},                                # goal is scene-level only
    {"shots": [shot(1)], "turn": {"ovi": "A1:11", "text": "x"}},
    {"shots": []},                                                          # nothing returned
    {"shots": [shot(2)]},                                                   # wrong shot
    "not an object"])
def test_splice_refuses_collateral_changes(reply):
    assert dt.splice(good(), reply, {"S1-1"})[0] is None


def test_splice_refuses_to_rewrite_an_image_a_locked_shot_uses():
    reply = {"shots": [shot(1)], "images_needed": [{"image_id": "left_pose", "description": "a different picture"}]}
    new, why = dt.splice(good(), reply, {"S1-1"})
    assert new is None and "locked shot" in why


def test_repair_that_drops_content_is_detected():
    d = [{"speaker": "Bankatlal", "ovi": "A1:10", "marathi": "ब क", "meaning_en": "m"}]
    old = scene([shot(1, dialogue=d, ovi_ids=["A1:10", "A1:11"]), shot(2)])
    assert dt.preserves_content(old, copy.deepcopy(old)) == []
    dropped = copy.deepcopy(old)
    dropped["shots"][0]["dialogue"], dropped["shots"][0]["ovi_ids"] = [], ["A1:10"]
    why = " | ".join(dt.preserves_content(old, dropped))
    assert "dropped dialogue for ovis ['A1:10']" in why and "dropped ovis ['A1:11']" in why


# ----------------------------------------------------------------------------- reviewer rubric

def answers(**over):
    rows = [{"q": q, "shot_id": "scene", "answer": "yes", "evidence": "e"} for q in sorted(dt.RUBRIC_IDS)]
    return {"answers": [r for r in rows if r["q"] not in over] + [v for vs in over.values() for v in vs]}


def no(q, sid="S1-1"):
    return {"q": q, "shot_id": sid, "answer": "no", "evidence": "the ovi says otherwise", "fix": "f"}


def test_review_passes_only_when_every_blocking_question_is_answered_yes():
    assert dt.clean_review(answers())["verdict"] == "PASS"
    r = dt.clean_review(answers(Q2=[no("Q2")]))
    assert r["verdict"] == "BLOCK" and r["problems"][0]["kind"] == "Q2" and r["problems"][0]["shot_id"] == "S1-1"


def test_advisory_no_never_blocks():
    r = dt.clean_review(answers(Q9=[no("Q9", "scene")]))
    assert r["verdict"] == "PASS" and r["advisory"][0]["kind"] == "Q9"


def test_missing_or_malformed_answers_are_no_check_never_pass():
    full = answers()
    assert dt.clean_review({"answers": [a for a in full["answers"] if a["q"] != "Q4"]}) ["verdict"] == "NO_CHECK"
    assert dt.clean_review({"answers": [a for a in full["answers"] if a["q"] != "Q4"]})["missing"] == ["Q4"]
    for bad in (None, {}, {"answers": []}, {"answers": ["junk"]}, {"verdict": "OK", "problems": []},
                {"answers": [{"q": "Q1", "shot_id": "scene", "answer": "yes", "evidence": "  "}]},
                {"answers": [{"q": "Q99", "shot_id": "scene", "answer": "yes", "evidence": "e"}]},
                {"answers": [{"q": "Q1", "shot_id": "scene", "answer": "maybe", "evidence": "e"}]}):
        assert dt.clean_review(bad)["verdict"] == "NO_CHECK"


# ----------------------------------------------------------------------------- pipeline: one repair round, no loops

FILES = {"addendum": "### Scene 1 - X (ovi 10-11)\nbrief\n## C. Visual\nvisual\n## D. Continuity\ncont\n## E. End\n", "analysis": "## 3. Characters\n**Bankatlal**\n## 4. Places\nplaces\n## 5. End\n",
         "answers": "answers", "glossary": "glossary"}
INDEX = [{"preset": PUSH, "use": "u", "assets": ["img"]}, {"preset": DIALOGUE, "use": "u", "assets": ["left", "right"]}]
INFO = {"status": 200, "wall_s": 0.0, "finish": "stop"}


class Fake:
    """Stands in for an Agent: replays canned replies and records every call."""
    def __init__(self, name, replies, info=None):
        self.name, self.replies, self.calls, self.secrets, self.info = name, replies, [], (), info or dict(INFO)
        self.paid = False

    def call(self, system, user, max_tokens=None):
        self.calls.append(user)
        r = self.replies[min(len(self.calls) - 1, len(self.replies) - 1)]
        return (r if isinstance(r, str) else json.dumps(r, ensure_ascii=False)), dict(self.info)


def fake(name, replies, info=None):
    return Fake(name, replies, info)


def run(director, reviewers):
    return dt.direct_scene(director, reviewers, 1, (10, 11), 1, FILES, OVIS, INDEX, CTX)


def counting(agent):
    return len(agent.calls)


def test_clean_path_is_valid_with_no_repair():
    d, r = fake("kimi", [good()]), fake("nemo", [answers()])
    out = run(d, [r])
    assert out["result"] == "VALID" and out["repairs"] == [] and counting(d) == 1


def test_validator_error_gets_one_shot_locked_repair_then_review_checks_it():
    bad = good()
    bad["shots"][0]["action"] = "Maharaj raises his hand"
    d, r = fake("kimi", [bad, {"shots": [shot(1, assets={"img": "road1"})]}]), fake("nemo", [answers()])
    out = run(d, [r])
    assert out["result"] == "VALID" and out["repairs"][0]["status"] == "USED" and out["repairs"][0]["scope"] == ["S1-1"]
    assert out["plan"]["shots"][1] == good()["shots"][1] and counting(d) == 2 and counting(r) == 1


def test_reviewer_block_gets_exactly_one_repair_then_a_check_only():
    d = fake("kimi", [good(), {"shots": [shot(1, assets={"img": "road1"}, held_pose="Maharaj seated, calm")]}])
    r = fake("nemo", [answers(Q2=[no("Q2")]), answers()])
    out = run(d, [r])
    assert out["result"] == "VALID" and [x["status"] for x in out["repairs"]] == ["USED"] and counting(d) == 2 and counting(r) == 2
    assert out["reviews"][0]["verdict"] == "BLOCK" and out["final_reviews"][0]["verdict"] == "PASS"


def test_still_blocked_after_the_one_repair_stops_for_the_owner():
    d = fake("kimi", [good(), {"shots": [shot(1, assets={"img": "road1"}, held_pose="Maharaj seated, calm")]}, good()])
    r = fake("nemo", [answers(Q2=[no("Q2")])])
    out = run(d, [r])
    assert out["result"] == "REVIEW_BLOCKED" and counting(d) == 2                 # no third director call: no loops


def test_validator_repair_uses_up_the_only_repair():
    bad = good()
    bad["shots"][0]["action"] = "Maharaj raises his hand"
    d = fake("kimi", [bad, {"shots": [shot(1, assets={"img": "road1"})]}, good()])
    r = fake("nemo", [answers(Q2=[no("Q2")])])
    out = run(d, [r])
    assert out["result"] == "REVIEW_BLOCKED" and counting(d) == 2 and len(out["repairs"]) == 1


def test_collateral_repair_is_rejected_and_the_original_kept():
    d = fake("kimi", [good(), {"shots": [shot(1, assets={"img": "road1"}), shot(2, DIALOGUE, {"left": "left_pose", "right": "right_pose"})]}])
    r = fake("nemo", [answers(Q2=[no("Q2")])])
    out = run(d, [r])
    assert out["repairs"][0]["status"].startswith("REJECTED") and out["plan"] == good() and out["result"] == "REVIEW_BLOCKED"


def test_missing_review_is_no_check_never_valid():
    out = run(fake("kimi", [good()]), [fake("nemo", ["garbage, not json"])])
    assert out["result"] == "NO_CHECK" and out["reviews"][0]["verdict"] == "NO_CHECK"


def test_need_new_shot_is_unresolved_even_when_reviewers_pass():
    sc = scene([shot(1, "NEED_NEW", {}, need_new_reason="needs a walking cycle", needs=["walking"]), shot(2)])
    out = run(fake("kimi", [sc]), [fake("nemo", [answers()])])
    assert out["result"] == "UNRESOLVED"


def test_unrepairable_validator_errors_end_invalid_after_one_round():
    bad = good()
    bad["shots"][0]["action"] = "Maharaj raises his hand"
    d = fake("kimi", [bad, {"shots": [shot(1, assets={"img": "road1"}, action="Maharaj raises his hand")]}, good()])
    out = run(d, [fake("nemo", [answers()])])
    assert out["result"] == "INVALID" and counting(d) == 2


def test_non_json_reply_is_retried_once_only():
    d = fake("kimi", ["no json here"])
    out = run(d, [])
    assert out["result"] == "FAILED" and counting(d) == 2


# ----------------------------------------------------------------------------- Codex findings (2026-10-26): added controls and seeded failures

def test_held_expression_in_performance_is_not_motion():
    assert check(scene([shot(1, performance="smiling held pose, eyes closed"), shot(2)]))[0] == []
    assert any("motion" in e for e in check(scene([shot(1, action="Maharaj starts smiling"), shot(2)]))[0])


def test_scene_id_must_be_the_requested_scene():
    sc = good()
    assert dt.validate_scene(sc, PRESETS, OVIS, (10, 11), CTX, 1, "S1")[0] == []
    assert any("scene_id must be S2" in e for e in dt.validate_scene(sc, PRESETS, OVIS, (10, 11), CTX, 1, "S2")[0])


def test_uncovered_ovis_are_warned_for_the_owner():
    _, w = check(scene([shot(1), shot(2)]))
    assert any("ovis not shown in any shot" in x and "11" in x for x in w)


def test_speaker_table_is_enforced_for_registered_speakers():
    rows = dt.speaker_table(["| Ovi | Speaker → listener |", "| 10 | Bankatlal and Damodar → each other | x | y |", "| 11 | unclear: master says Bankatlal → Devidas | x | y |", "| 12-13 | Gajanan → (none) | x | y |"])
    assert rows == {10: "Bankatlal and Damodar", 11: "unclear: master says Bankatlal", 12: "Gajanan", 13: "Gajanan"}
    ctx = {**CTX, "speaker_rows": rows}
    d = lambda who, ovi: [{"speaker": who, "ovi": f"A1:{ovi}", "marathi": "अ ब क" if ovi == 10 else "इ ई उ", "meaning_en": "m"}]
    sc = lambda who, ovi: scene([shot(1, ovi_ids=[f"A1:{ovi}"], dialogue=d(who, ovi)), shot(2)])
    assert check(sc("Bankatlal", 10), ctx)[0] == [] and check(sc("unclear", 11), ctx)[0] == []                         # clean controls
    assert any("table gives" in e for e in check(sc("Shri Gajanan Maharaj", 10), ctx)[0])                              # a registered speaker, but the wrong one
    assert any("marks the speaker" in e and "unclear" in e for e in check(sc("Bankatlal", 11), ctx)[0])
    assert check(sc("unclear", 10), ctx)[0] == []                                                                       # ovi 10 is JOINT speech: 'unclear' is allowed (new rule)


def test_splice_scene_level_patch_unlocks_only_goal_turn_and_images():
    old = good()
    new, why = dt.splice(old, {"goal": "a better goal"}, set(), scene_level=True)
    assert why == "" and new["goal"] == "a better goal" and new["shots"] == old["shots"]
    assert dt.splice(old, {"goal": "a better goal"}, set(), scene_level=False)[0] is None
    assert dt.splice(old, {"shots": [shot(1)]}, set(), scene_level=True)[0] is None                                   # shots not named as failing stay locked


def test_review_answers_must_cover_all_ten_questions_and_real_shot_ids():
    full = answers()
    assert dt.clean_review({"answers": [a for a in full["answers"] if a["q"] != "Q10"]})["verdict"] == "NO_CHECK"          # advisory answers are required too
    assert dt.clean_review({"answers": full["answers"]}, {"S1-1", "S1-2"})["verdict"] == "PASS"
    ghost = answers(Q2=[no("Q2", "S9-9")])
    assert dt.clean_review(ghost, {"S1-1", "S1-2"})["verdict"] == "NO_CHECK"
    assert dt.clean_review({"answers": [{"q": "Q1", "answer": "yes", "evidence": "e"}]})["verdict"] == "NO_CHECK"          # no shot_id


def test_wrong_registered_speaker_caught_by_the_cross_check_route():
    d = fake("kimi", [good(), {"shots": [shot(1, assets={"img": "road1"}, held_pose="Maharaj seated, calm")]}])
    r = fake("nemo", [answers(Q1=[no("Q1")])])
    assert run(d, [r])["result"] == "REVIEW_BLOCKED"


def test_without_reviewers_the_result_is_unreviewed_never_valid():
    out = run(fake("kimi", [good()]), [])
    assert out["result"] == "UNREVIEWED" and out["status"] == "VALID" and out["reviewed"] is False


def test_json_retry_spends_the_only_second_director_call():
    bad = good()
    bad["shots"][0]["action"] = "Maharaj raises his hand"
    d = fake("kimi", ["not json", bad, {"shots": [shot(1, assets={"img": "road1"})]}])
    out = run(d, [fake("nemo", [answers()])])
    assert out["result"] == "INVALID" and counting(d) == 2 and out["repairs"] == []                                      # no repair left: never a third call


def test_provider_error_or_truncation_stops_the_director():
    for info in ({"status": 200, "wall_s": 0, "finish": "stop", "error": "no usage in reply"}, {"status": 200, "wall_s": 0, "finish": "length"}):
        d = fake("kimi", [good()], info)
        with pytest.raises(dt.DirectorStop):
            run(d, [fake("nemo", [answers()])])
        assert counting(d) == 1


def test_an_unreachable_reviewer_is_a_missing_check_not_a_crash():
    out = run(fake("kimi", [good()]), [fake("nemo", [answers()], {"status": 500, "wall_s": 0, "finish": None, "error": "HTTP 500"})])
    assert out["result"] == "NO_CHECK"


def test_parsed_replies_are_scrubbed_of_secrets_even_when_escaped():
    secret = "SECRETKEY1234567890ABCDEFGH"
    escaped = "".join("\\u%04x" % ord(c) for c in secret)
    obj = dt._json('{"goal": "' + escaped + '"}', (secret,))
    assert secret not in json.dumps(obj)


def test_recorded_calls_are_replayed_on_resume_and_never_paid_twice(tmp_path):
    spec2 = importlib.util.spec_from_file_location("dr", Path(__file__).resolve().parents[1] / "scripts" / "source" / "director_run.py")
    dr = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(dr)
    d = fake("kimi", [good()])
    run1 = dr.open_run(tmp_path, "r", {"x": 1})
    assert dt.recorded(d, run1, 1).call("sys", "user")[0] and counting(d) == 1
    run1.release()
    run2 = dr.open_run(tmp_path, "r", {"x": 1}, resume=True)
    reply, info = dt.recorded(d, run2, 1).call("sys", "user")
    assert counting(d) == 1 and info["replayed"] is True and json.loads(reply)["scene_id"] == "S1"
    dt.recorded(d, run2, 1).call("sys", "different user text")
    assert counting(d) == 2


# ----------------------------------------------------------------------------- Codex audit v2 findings

def test_same_rows_inherit_and_prefix_matching_accepts_both_joint_speakers():
    rows = dt.speaker_table(["| 99 | Bankatlal and Damodar → each other | x | y |", "| 100-101 | same (joint reasoning, speaker not split) | x | y |"])
    assert rows[100] == rows[101] == "Bankatlal and Damodar"
    ctx = {**CTX, "speaker_rows": rows, "speakers": {"Bankatlal", "Damodarpant", "Shri Gajanan Maharaj"}}
    for who in ("Bankatlal", "Damodarpant"):
        d = [{"speaker": who, "ovi": "A1:10", "marathi": "अ ब क", "meaning_en": "m"}]
        assert check(scene([shot(1, dialogue=d), shot(2)]), {**ctx, "speaker_rows": {10: rows[100]}})[0] == []
    d = [{"speaker": "Shri Gajanan Maharaj", "ovi": "A1:10", "marathi": "अ ब क", "meaning_en": "m"}]
    assert any("table gives" in e for e in check(scene([shot(1, dialogue=d), shot(2)]), {**ctx, "speaker_rows": {10: rows[100]}})[0])


def test_repair_may_not_delete_one_of_two_lines_citing_the_same_ovi():
    two = [{"speaker": "Bankatlal", "ovi": "A1:10", "marathi": "अ ब क", "meaning_en": "m"}, {"speaker": "Bankatlal", "ovi": "A1:10", "marathi": "ब क ड", "meaning_en": "m"}]
    old = scene([shot(1, dialogue=two), shot(2)])
    new = copy.deepcopy(old)
    new["shots"][0]["dialogue"] = two[:1]
    assert "1 line(s)" in " ".join(dt.preserves_content(old, new))
    assert dt.preserves_content(old, copy.deepcopy(old)) == []


def test_empty_staging_string_is_refused():
    assert check(scene([shot(1, staging=[""]), shot(2)]))[0]


@pytest.mark.parametrize("finish", [None, "other", "content_filter", "tool_calls", "length"])
def test_only_a_complete_reply_is_used(finish):
    d = fake("kimi", [good()], {"status": 200, "wall_s": 0, "finish": finish})
    with pytest.raises(dt.DirectorStop):
        run(d, [fake("nemo", [answers()])])


def test_reviewer_reply_that_is_not_complete_is_a_missing_check():
    out = run(fake("kimi", [good()]), [fake("nemo", [answers()], {"status": 200, "wall_s": 0, "finish": "length"})])
    assert out["result"] == "NO_CHECK"


def load_dr(tmp=None):
    spec2 = importlib.util.spec_from_file_location("dr2", Path(__file__).resolve().parents[1] / "scripts" / "source" / "director_run.py")
    mod = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(mod)
    return mod


def test_a_paid_attempt_is_saved_before_dispatch_and_never_re_bought(tmp_path):
    dr = load_dr()
    d = fake("kimi", [good()])
    d.paid = True
    run1 = dr.open_run(tmp_path, "r", {"x": 1})
    seen = {}
    real = d.call

    def crash(system, user, max_tokens=None):
        seen["attempt_saved_first"] = any(".attempt" in f for f in run1.receipt["files"])
        raise KeyboardInterrupt                                                   # killed after dispatch, before the reply was saved
    d.call = crash
    with pytest.raises(KeyboardInterrupt):
        dt.recorded(d, run1, 1).call("sys", "user")
    assert seen["attempt_saved_first"] is True
    d.call = real
    run1.release()                                                                # the crashed process is gone
    run2 = dr.open_run(tmp_path, "r", {"x": 1}, resume=True)
    with pytest.raises(dt.DirectorStop):
        dt.recorded(d, run2, 1).call("sys", "user")                              # refuses to buy the same request again
    assert counting(d) == 0


def test_a_crashed_paid_attempt_still_counts_as_directed_in_other_runs(tmp_path):
    dr = load_dr()
    run1 = dr.open_run(tmp_path, "r1", {"director": "kimi-k3.1-pro"})
    run1.write_once("calls/scene4__kimi-k3.1-pro__abc123.json.attempt1", "{}")
    assert dr.directed_elsewhere(tmp_path, "r2", "kimi-k3.1-pro", [1, 4]) == ["r1:scene4"]


# ----------------------------------------------------------------------------- real Kimi scene 1 (2026-10-26): defaults and negation

def test_missing_needs_defaults_to_none_for_preset_shots_only():
    sc = good()
    del sc["shots"][0]["needs"]
    fixed, notes = dt.normalise(sc)
    assert fixed["shots"][0]["needs"] == ["none"] and "defaulted" in notes[0] and "needs" not in sc["shots"][0]
    nn = scene([shot(1, "NEED_NEW", {}, need_new_reason="walking", needs=["walking"]), shot(2)])
    del nn["shots"][0]["needs"]
    assert "needs" not in dt.normalise(nn)[0]["shots"][0]                      # a NEED_NEW shot must still say what is missing


def test_negated_motion_and_scenery_words_are_not_violations():
    ok = scene([shot(1, performance="held moment; no hand, head or lip movement occurs", camera="slow push in without any clouds or sky"), shot(2)])
    assert check(ok)[0] == []
    assert any("motion" in e for e in check(scene([shot(1, performance="his lip movement is visible"), shot(2)]))[0])      # not negated: still caught
    assert any("'clouds'" in e for e in check(scene([shot(1, camera="slow push in under clouds"), shot(2)]))[0])


# ----------------------------------------------------------------------------- Codex scene 1 review (2026-10-26)

def test_negation_reaches_only_its_own_phrase():
    assert check(scene([shot(1, performance="held moment; no hand, head or lip movement occurs"), shot(2)]))[0] == []
    for text in ("No lip movement, but he raises his hand", "Without walking he raises his hand"):
        assert any("motion" in e for e in check(scene([shot(1, performance=text), shot(2)]))[0]), text
    assert any("motion" in e for e in check(scene([shot(1, action="Maharaj claps both hands"), shot(2)]))[0])
    assert check(scene([shot(1, camera="slow push in, never with clouds"), shot(2)]))[0] == []
    assert any("'clouds'" in e for e in check(scene([shot(1, camera="slow push in, never idle, then clouds drift in"), shot(2)]))[0])


def test_camera_staging_needs_no_approval_but_other_staging_still_does():
    cam = [{"kind": "camera", "term": "slow dolly", "source": "STAGING"}]
    assert check(scene([shot(1, claims=cam), shot(2, ovi_ids=["A1:11"])])) == ([], [])
    sky = [{"kind": "scenery", "term": "sky", "source": "STAGING"}]
    assert any("needs the owner's approval" in w for w in check(scene([shot(1, claims=sky), shot(2)]))[1])


def test_zoom_values_in_the_camera_text_must_match_the_preset():
    _, w = check(scene([shot(1, camera="slow push from 1.00 to 1.16"), shot(2)]))
    assert any("states zoom values" in x for x in w)
    assert not any("states zoom" in x for x in check(scene([shot(1, camera="slow push from 1.00 to 1.20"), shot(2)]))[1])


def test_the_prompt_tells_kimi_what_each_preset_really_does_and_asks_for_coverage():
    files = {"addendum": "### Scene 1 - X (ovi 10-11)\nbrief\n## C. Visual\nvisual\n## D. Continuity\ncont\n## E. End\n", "analysis": "## 3. Characters\n**Bankatlal**\n## 4. Places\nplaces\n## 5. End\n",
             "answers": "a", "glossary": "g"}
    pj = {"01_x": {"segments": [{"layers": [{"asset": "mid"}], "camera": {"start": {"zoom": 1.0}, "end": {"zoom": 1.28}}}], "atmosphere": {"gloss": 0.3, "dust": 0.12, "vignette": 0.0}, "backdrop": {"halo": {"x": 0}}}}
    system, user = dt.build_prompt(1, (10, 11), files, OVIS, [{"preset": "01_x", "use": "u", "assets": ["mid"]}], ["Bankatlal"], 1, pj)
    assert "FIXED zoom 1.00->1.28; fixed effects: gloss 0.3, dust 0.12, halo" in user and "BEFORE YOU ANSWER" in user
    assert '"needs": ["none"] explicitly; never omit it' in system and "every ovi of the scene's range appears in some shot's ovi_ids" in system and "T5. Economy" in system


# ----------------------------------------------------------------------------- Codex planner review: director_test heuristics

def test_negation_counter_examples_from_the_planner_review():
    for text in ("Without walking, Bankatlal raises his hand", "No lip movement and raises his hand"):
        assert any("motion" in e for e in check(scene([shot(1, performance=text), shot(2)]))[0]), text
    assert check(scene([shot(1, performance="no hand, head or lip movement occurs"), shot(2)]))[0] == []


def test_a_camera_staging_claim_cannot_license_scenery_words():
    cam = [{"kind": "camera", "term": "slow push in under trees", "source": "STAGING"}]
    e, w = check(scene([shot(1, camera="slow push in under trees", claims=cam), shot(2)]))
    assert any("'trees'" in x for x in e) and any("needs the owner's approval" in x for x in w)


def test_zoom_endpoints_are_compared_in_order_and_long_decimals_count():
    assert any("states zoom values" in x for x in check(scene([shot(1, camera="push from 1.2 to 1.0"), shot(2)]))[1])
    assert any("states zoom values" in x for x in check(scene([shot(1, camera="push from 1.000 to 1.2999"), shot(2)]))[1])
    assert not any("states zoom values" in x for x in check(scene([shot(1, camera="push from 1.00 to 1.20"), shot(2)]))[1])


def test_a_refused_paid_attempt_never_blocks_a_later_retry_but_a_real_one_does(tmp_path):
    spec2 = importlib.util.spec_from_file_location("dr5", Path(__file__).resolve().parents[1] / "scripts" / "source" / "director_run.py")
    dr = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(dr)

    class Refused(Exception):
        pass
    d = fake("kimi", [good()])
    d.paid = True
    real = d.call

    def refuse(system, user, max_tokens=None):
        raise Refused("an earlier reservation is unreconciled")
    d.call = refuse
    run1 = dr.open_run(tmp_path, "r", {"x": 1})
    with pytest.raises(Refused):
        dt.recorded(d, run1, 0).call("sys", "user")                              # the guard said no before anything was sent
    run1.release()
    d.call = real
    run2 = dr.open_run(tmp_path, "r", {"x": 1}, resume=True)
    assert json.loads(dt.recorded(d, run2, 0).call("sys", "user")[0])["scene_id"] == "S1" and counting(d) == 1      # the retry is allowed and paid once
    run2.release()
    run3 = dr.open_run(tmp_path, "r", {"x": 1}, resume=True)
    reply, info = dt.recorded(d, run3, 0).call("sys", "user")
    assert info["replayed"] is True and counting(d) == 1


# ----------------------------------------------------------------------------- lessons of the free dry run (2026-10-26)

def test_joint_speech_may_stay_unclear_but_a_single_named_speaker_may_not():
    ctx = {**CTX, "speaker_rows": {10: "Bankatlal and Damodar", 11: "Bankatlal"}}
    d = lambda ovi, who, m: [{"speaker": who, "ovi": f"A1:{ovi}", "marathi": m, "meaning_en": "m"}]
    ok = scene([shot(1, dialogue=d(10, "unclear", "अ ब क")), shot(2, ovi_ids=["A1:11"])])
    assert check(ok, ctx)[0] == []                                                   # joint speech: 'unclear' is fine
    assert check(scene([shot(1, dialogue=d(10, "Bankatlal", "अ ब क")), shot(2, ovi_ids=["A1:11"])]), ctx)[0] == []
    bad = scene([shot(1, ovi_ids=["A1:11"], dialogue=d(11, "unclear", "इ ई उ")), shot(2)])
    assert any("table gives" in e for e in check(bad, ctx)[0])                       # a single named speaker may not be dropped to 'unclear'


def test_walking_words_are_allowed_only_for_the_walking_entrance_preset():
    presets = {**PRESETS, "04_character_entrance": ["char", "other"]}
    walk = "A man walks in toward the seated figure"
    sc4 = scene([shot(1, "04_character_entrance", {"char": "man_walking", "other": "man_seated"}, action=walk), shot(2, ovi_ids=["A1:11"])])
    assert dt.validate_scene(sc4, presets, OVIS, (10, 11), CTX, 1)[0] == []
    sc3 = scene([shot(1, action=walk), shot(2, ovi_ids=["A1:11"])])
    assert any("motion" in e for e in dt.validate_scene(sc3, presets, OVIS, (10, 11), CTX, 1)[0])
    sc4b = scene([shot(1, "04_character_entrance", {"char": "man_walking", "other": "man_seated"}, action="He raises his hand"), shot(2, ovi_ids=["A1:11"])])
    assert any("motion" in e for e in dt.validate_scene(sc4b, presets, OVIS, (10, 11), CTX, 1)[0])      # only walking/entering is exempt


# ----------------------------------------------------------------------------- dry run 2 (2026-10-26): a day or month leaked into the turn text

@pytest.mark.parametrize("field,text", [("turn", "Gajanan arrives in Shegaon on Magh Vadya Saptami"), ("goal", "The 23rd of February"), ("performance", "in February 1878"), ("camera", "slow push, 14 January")])
def test_a_day_or_month_anywhere_in_the_plan_is_an_error(field, text):
    sc = good()
    if field in ("turn",):
        sc["turn"]["text"] = text
    elif field == "goal":
        sc["goal"] = text
    else:
        sc["shots"][0][field] = text
    assert any("a day or month" in e for e in check(sc)[0]), field


def test_the_year_alone_and_shaka_1800s_are_not_a_date_leak():
    sc = good()
    sc["shots"][0]["performance"] = "the year 1878, within Shaka 1800s; he may be young"
    assert check(sc)[0] == []


def test_the_rules_forbid_dates_and_completing_a_readiness():
    assert "F8. Never write a day or a month" in dt.RULES and "F9. Show a state the verse gives as a state" in dt.RULES


# ----------------------------------------------------------------------------- Codex re-review 2: exact counter-examples

@pytest.mark.parametrize("text", ["in March 1878", "in May 1878", "on Monday", "since March", "the 5th of May"])
def test_march_may_and_weekday_dates_are_errors_in_the_validator(text):
    sc = good()
    sc["shots"][0]["performance"] = text
    assert any("a day or month" in e for e in check(sc)[0]), text


def test_the_word_may_and_a_marching_walk_are_not_a_date():
    sc = good()
    sc["shots"][0]["performance"] = "he may be young; a march of days is not shown"
    assert not any("a day or month" in e for e in check(sc)[0])
