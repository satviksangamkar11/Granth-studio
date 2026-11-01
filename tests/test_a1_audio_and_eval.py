"""Deterministic checks of the Adhyay 1 audio plan, the timing estimate, and the evaluation scorer. No model, no network."""
import copy
import importlib.util
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


a1 = load("a1_audio_t", "scripts/source/a1_audio.py")
ev = load("a1_eval_t", "scripts/source/a1_eval.py")
ss = load("ss_t", "scripts/source/story_split.py")
dt = a1.dt
files, OVIS, INDEX = dt.load_inputs()
ROWS = dt.speaker_rows(files["addendum"].splitlines())                  # frozen table + owner overrides, as in a1_audio.main
EDITS = json.loads((ROOT / "canon" / "story_split_edits" / "A1_rev1.json").read_text(encoding="utf-8"))
MACRO = ss.build_macro({"stories": EDITS["stories"], "unfilmed_ranges": EDITS["unfilmed_ranges"]}, 1, sorted(OVIS), "x" * 64)
EXPECTED = json.loads((ROOT / "canon" / "eval" / "A1_expected.json").read_text(encoding="utf-8"))


def plan():
    return a1.build_plan(OVIS)


def errs(p):
    return " | ".join(a1.validate_plan(p, OVIS, MACRO, ROWS)[0])


# ----------------------------------------------------------------------------- the audio plan

def test_the_real_plan_validates_every_marathi_line_is_an_exact_verse_segment():
    e, w = a1.validate_plan(plan(), OVIS, MACRO, ROWS)
    assert e == [], e
    p = plan()
    assert len(p["lines"]) >= 55 and all(dt.quote_in(l["marathi"], OVIS[l["ovi"]]) for l in p["lines"])


def test_no_day_month_or_sajjangad_material_in_any_narration_and_the_year_is_a_caption_only():
    p = plan()
    blob = " ".join(l["marathi"] + " " + l["hindi"] for l in p["lines"])
    assert not a1.NOT_FILM_FACING.search(blob) and "1878" not in blob and "१८७८" not in blob
    assert [(k["id"], k["marathi"], k["hindi"]) for k in p["captions"]] == [("S1-K1", "१८७८", "1878")]


def test_voices_follow_the_owners_dialogue_table_and_unclear_speech_stays_with_the_narrator():
    p = plan()
    by = {}
    for l in p["lines"]:
        by.setdefault(l["voice"], set()).add(l["ovi"])
    assert by["damodarpant"] <= {126, 136, 137} and by["gajanan"] <= {128, 129, 130, 131, 138, 139, 140, 141, 142} and by["bankatlal"] <= {102, 109, 119, 120, 121, 122, 125, 132}         # 122, 125: owner directive 2026-11-01
    unclear = {103, 104, 113, 123, 124, 99, 100, 101}                  # 122 and 125 settled by the owner (2026-11-01)
    assert not [l for l in p["lines"] if l["voice"] != "narrator" and l["ovi"] in unclear]


def test_every_meaningful_event_and_both_teachings_are_in_the_core_narration():
    core = {l["ovi"] for l in plan()["lines"] if l["priority"] == "core"}
    assert {87, 88, 94, 95, 96} <= core                                              # plates, the bandi, grain-picking, 'food is Brahman' and its explanation (94-96)
    assert {112, 114, 115, 116, 117, 118} <= core                                    # the silent bow, the plate, the eating, both narrator comparisons, the mixing
    assert {126, 128, 129, 130, 133, 134, 135, 136, 137} <= core                     # the offer, the practical-conduct teaching, Damodarpant fetches water, the trough
    assert {138, 139, 140, 141, 142, 143, 144} <= core                               # the whole second teaching, the readiness to fall, the run


@pytest.mark.parametrize("name", ["bad_marathi", "wrong_voice", "unclear_to_character", "unknown_sound", "cue_over_line", "verse_cue_outside_scene", "two_beds", "date_word",
                                  "no_hindi", "bad_caption", "line_out_of_order", "bad_anchor_line", "bed_as_event"])
def test_seeded_audio_failures_are_all_caught(name):
    p = plan()
    L = {l["id"]: l for l in p["lines"]}
    C = {c["id"]: c for c in p["cues"]}
    expect = {
        "bad_marathi": lambda: L["S2-L8"].__setitem__("marathi", L["S2-L8"]["marathi"].replace("शीत", "शीतं")),
        "wrong_voice": lambda: L["S7-L8"].__setitem__("voice", "damodarpant"),
        "unclear_to_character": lambda: L["S5-L1"].__setitem__("voice", "bankatlal"),
        "unknown_sound": lambda: C["C3"].__setitem__("sound", "fx_laser"),
        "cue_over_line": lambda: C["C7"].__setitem__("anchor_type", "during_line"),
        "verse_cue_outside_scene": lambda: C["C9"].__setitem__("ovi", 140),
        "two_beds": lambda: p["cues"].append({"id": "CX", "scene": "S2", "sound": "bed_roadside_quiet", "anchor_type": "scene_bed", "anchor": "", "label": "STAGING", "ovi": None}),
        "date_word": lambda: L["S1-L1"].__setitem__("hindi", L["S1-L1"]["hindi"] + " माघ वद्य सप्तमी"),
        "no_hindi": lambda: L["S2-L9"].__setitem__("hindi", " "),
        "bad_caption": lambda: p["captions"][0].__setitem__("marathi", "माघ १८७८"),
        "line_out_of_order": lambda: p["lines"].insert(1, L["S1-L1"].copy() | {"id": "S1-LX", "ovi": 74, "marathi": OVIS[74].split("।")[0].strip()}),
        "bad_anchor_line": lambda: C["C15"].__setitem__("anchor", "S2-L1"),
        "bed_as_event": lambda: C["C1"].__setitem__("anchor_type", "picture_event"),
    }[name]
    expect()
    if name == "line_out_of_order":
        p["lines"].insert(1, p["lines"].pop())                                      # a line of ovi 74 placed before 70 in the same scene
    assert errs(p), name


def test_the_closed_palette_has_a_generous_list_and_every_cue_uses_it():
    p = plan()
    ids = {x["id"] for x in p["palette"]}
    assert len(ids) >= 20 and all(c["sound"] in ids for c in p["cues"]) and all("UNSOURCED" in x["source_status"] for x in p["palette"])
    assert {c["scene"] for c in p["cues"]} == {f"S{k}" for k in range(1, 10)}


# ----------------------------------------------------------------------------- timing

def test_syllable_and_duration_estimates_are_sane():
    assert a1.syllables("राम") == 2 and a1.syllables("क्ष") == 1 and a1.syllables("सन् १८७८") >= 9
    assert 3.0 < a1.seconds("या महापुरुषाचा । ठावठिकाण कोणचा । वा पत्ता त्यांच्या जातीचा । इतिहासदृष्टया न लागे कीं", "mr") < 10.0


def test_timing_follows_the_longer_language_and_partitions_every_core_line_into_exactly_one_shot():
    tm = a1.timing(plan(), MACRO)
    assert tm["estimate"] is True and tm["planned_shots"] == sum(s["planned_shots"] for s in tm["scenes"])
    p = plan()
    for s in tm["scenes"]:
        core = [l["id"] for l in p["lines"] if l["scene"] == s["scene"] and l["priority"] == "core"]
        starts = [i for sh in s["shots"] for i in sh["lines_starting"]]
        assert sorted(starts) == sorted(core) and len(s["shots"]) == s["planned_shots"] >= s["audio_needs"]
        assert [b["start_s"] for b in s["beats"]] == sorted(b["start_s"] for b in s["beats"])
        assert s["common_s"] >= max(s["marathi_s"], s["hindi_s"]) - 0.06                  # the common timeline follows the LONGER language (rounding only)
        gaps = a1.PAUSE * (len(core) - 1)
        assert abs(s["marathi_s"] - (a1.LEAD + sum(l["seconds"]["mr"] for l in p["lines"] if l["id"] in core) + gaps + a1.TAIL)) < 0.06 * len(core)      # lead + lines + gaps + tail
    assert tm["scenes"][0]["planned_shots"] == 2                                      # the opening stays two shots with the full verse 70
    assert tm["scenes"][-1]["planned_shots"] >= 12                                    # the teaching and the run are not cut to fit


def test_the_saved_timing_matches_the_split_budgets_and_the_split_hash():
    audio = json.loads((ROOT / "canon" / "audio" / "A1_audio_plan.json").read_text(encoding="utf-8"))
    tm = json.loads((ROOT / "canon" / "audio" / "A1_timing_plan.json").read_text(encoding="utf-8"))
    assert audio["split_sha256"] == tm["split_sha256"] and len(tm["split_sha256"]) == 64
    budgets = [sc["shot_budget"] for st in EDITS["stories"] for sc in st["scenes"]]
    assert [s["planned_shots"] for s in tm["scenes"]] == [max(s["audio_needs"], b) for s, b in zip(tm["scenes"], budgets)]   # owner 2026-11-01: add shots where the speech needs them
    assert all(s["planned_shots"] >= b for s, b in zip(tm["scenes"], budgets))
    assert tm["planned_shots"] == sum(s["planned_shots"] for s in tm["scenes"]) and tm["allocated_shots"] == sum(budgets)


# ----------------------------------------------------------------------------- the evaluation scorer

def good_run():
    """A synthetic run that satisfies the rubric: proves the rubric is satisfiable and that each seeded defect below is what makes it fail."""
    tm = json.loads((ROOT / "canon" / "audio" / "A1_timing_plan.json").read_text(encoding="utf-8"))
    run = {}
    for sid, spec in EXPECTED["scenes"].items():
        n = int(sid[1:])
        k = next(s["planned_shots"] for s in tm["scenes"] if s["scene"] == sid)
        words = [g[0] for b in spec.get("beats", []) for g in b.get("text_all", [])]
        ovis = sorted({o for b in spec.get("beats", []) for o in b.get("must_show", [])})
        shots = [{"shot_id": f"S{n}-{i + 1}", "ovi_ids": [f"A1:{ovis[i % len(ovis)] if ovis else 70}"], "assets": {"img": f"i{i}"}, "action": "camera pushes in", "held_pose": " ".join(words) if i == 0 else "held",
                  "performance": "calm", "camera": "push", "claims": [], "staging": [], "dialogue": []} for i in range(k)]
        shots[0]["ovi_ids"] = [f"A1:{o}" for o in ovis] or ["A1:70"]
        voice = {102: "Bankatlal", 109: "Bankatlal", 119: "Bankatlal", 120: "Bankatlal", 121: "Bankatlal", 132: "Bankatlal", 126: "Damodarpant", 136: "Damodarpant", 137: "Damodarpant"}
        for o in spec.get("must_dialogue", []):
            shots[0]["dialogue"].append({"speaker": voice.get(o, "Shri Gajanan Maharaj"), "ovi": f"A1:{o}", "marathi": "x", "meaning_en": "m"})
        run[n] = {"result": "VALID", "plan": {"goal": "g", "turn": {"text": "t"}, "shots": shots, "images_needed": [{"image_id": f"i{i}", "description": "picture"} for i in range(k)]}}
    return run, tm


def test_the_rubric_is_satisfiable_and_counts_every_scene():
    run, tm = good_run()
    rep = ev.score_run(run, EXPECTED, tm)
    assert rep["failed"] == 0, [c for c in rep["checks"] if not c["passed"]]
    assert set(EXPECTED["scenes"]) == {f"S{k}" for k in range(1, 10)}


@pytest.mark.parametrize("name", ["no_mixing", "bankatlal_fetches_water", "run_has_destination", "named_113", "spoken_bow", "wrong_shot_count", "date_text", "elaborate_robe",
                                  "teaching_ovi_missing", "invalid_result", "missing_scene", "maharaj_drinks_vetiver", "sajjangad_picture", "birth_scene"])
def test_every_seeded_direction_defect_is_caught(name):
    run, tm = good_run()
    sh = lambda n, i=0: run[n]["plan"]["shots"][i]
    if name == "no_mixing":
        sh(5)["held_pose"] = sh(5)["held_pose"].replace("mix", "eat")
    elif name == "bankatlal_fetches_water":
        sh(7)["action"] = "Bankatlal goes to fetch the water"
    elif name == "run_has_destination":
        sh(9, 1)["action"] = "he runs to the temple"
    elif name == "named_113":
        sh(5)["dialogue"] = [{"speaker": "Bankatlal", "ovi": "A1:113", "marathi": "x", "meaning_en": "m"}]
    elif name == "spoken_bow":
        sh(4)["dialogue"] = [{"speaker": "Bankatlal", "ovi": "A1:112", "marathi": "x", "meaning_en": "m"}]
    elif name == "wrong_shot_count":
        run[2]["plan"]["shots"].pop()
    elif name == "date_text":
        sh(1)["performance"] = "arrives on Magh Vadya Saptami"
    elif name == "elaborate_robe":
        sh(2)["held_pose"] += " in a saffron robe"
    elif name == "teaching_ovi_missing":
        for x in run[9]["plan"]["shots"]:
            x["ovi_ids"] = [r for r in x["ovi_ids"] if r != "A1:141"]
    elif name == "invalid_result":
        run[3]["result"] = "INVALID"
    elif name == "missing_scene":
        del run[6]
    elif name == "maharaj_drinks_vetiver":
        sh(8)["action"] = "he drinks the vetiver water Damodarpant brings"
    elif name == "sajjangad_picture":
        sh(1)["performance"] = "a journey from Sajjangad"
    elif name == "birth_scene":
        sh(1)["performance"] = "his birth and childhood"
    rep = ev.score_run(run, EXPECTED, tm)
    assert rep["failed"] >= 1, name


def test_the_scorer_matches_a_registered_name_to_a_short_allowed_name_and_accepts_unreviewed_only_in_a_dry_run():
    run, tm = good_run()
    d = run[7]["plan"]["shots"][0]["dialogue"]
    assert ev.score_run(run, EXPECTED, tm)["failed"] == 0                             # 'shri gajanan maharaj' contains 'gajanan'
    next(x for x in d if x["ovi"] == "A1:128")["speaker"] = "Bankatlal"
    assert ev.score_run(run, EXPECTED, tm)["failed"] >= 1
    run, tm = good_run()
    run[2]["result"] = "UNREVIEWED"
    assert ev.score_run(run, EXPECTED, tm)["failed"] == 1 and ev.score_run(run, EXPECTED, tm, dry_run=True)["failed"] == 0


def test_the_scene_prompt_says_narrator_lines_are_not_dialogue():
    spec_i = importlib.util.spec_from_file_location("dti", ROOT / "scripts" / "source" / "director_test.py")
    d = importlib.util.module_from_spec(spec_i)
    spec_i.loader.exec_module(d)
    text = (ROOT / "scripts" / "source" / "director_test.py").read_text(encoding="utf-8")
    assert "narrator lines are read over the picture and are NOT dialogue" in text


# ----------------------------------------------------------------------------- Codex final review: rubric counter-examples

def test_the_rubric_rejects_a_bare_plan_with_no_teaching_dialogue():
    run, tm = good_run()
    for n in (4, 6, 7, 8, 9):
        for sh in run[n]["plan"]["shots"]:
            sh["dialogue"] = []
    rep = ev.score_run(run, EXPECTED, tm)
    assert rep["failed"] >= 5 and any("dialogue" in c["id"] for c in rep["checks"] if not c["passed"])


def test_ready_to_fall_passes_but_a_completed_prostration_fails():
    run, tm = good_run()
    run[9]["plan"]["shots"][0]["performance"] = "the two men are ready to fall at his feet"
    assert ev.score_run(run, EXPECTED, tm)["failed"] == 0
    run[9]["plan"]["shots"][0]["performance"] = "the two men fall at his feet and prostrate themselves"
    assert ev.score_run(run, EXPECTED, tm)["failed"] >= 1


def test_any_month_name_with_the_year_fails_even_when_the_day_is_numeric():
    for text in ("on 14 January 1878", "in February 1878", "23rd of February"):
        run, tm = good_run()
        run[1]["plan"]["shots"][0]["performance"] = text
        assert ev.score_run(run, EXPECTED, tm)["failed"] >= 1, text
    run, tm = good_run()
    run[1]["plan"]["shots"][0]["performance"] = "the year 1878, he may be young"
    assert ev.score_run(run, EXPECTED, tm)["failed"] == 0


def test_negated_inventions_pass_and_the_right_actor_passes():
    run, tm = good_run()
    run[1]["plan"]["shots"][0]["performance"] = "No birthplace or childhood is shown; no journey"
    run[7]["plan"]["shots"][0]["action"] = "Bankatlal watches as Damodarpant fetches water from the house"
    assert ev.score_run(run, EXPECTED, tm)["failed"] == 0
    run[7]["plan"]["shots"][0]["action"] = "Bankatlal fetches the water"
    assert ev.score_run(run, EXPECTED, tm)["failed"] >= 1


def test_the_narrator_comparisons_116_117_are_in_the_rubric():
    assert any(b.get("must_show") == [116, 117] for b in EXPECTED["scenes"]["S5"]["beats"])
    run, tm = good_run()
    for sh in run[5]["plan"]["shots"]:
        sh["ovi_ids"] = [r for r in sh["ovi_ids"] if r not in ("A1:116", "A1:117")]
    assert ev.score_run(run, EXPECTED, tm)["failed"] >= 1


# ----------------------------------------------------------------------------- Codex re-review 2

def authored_run():
    """Dialogue taken from the PLANNED audio lines (source verse) with the registered names, so the scorer is tested against real words rather than 'x'."""
    run, tm = good_run()
    audio = json.loads((ROOT / "canon" / "audio" / "A1_audio_plan.json").read_text(encoding="utf-8"))
    names = {"bankatlal": "Bankatlal Agarwal", "damodarpant": "Damodarpant Kulkarni", "gajanan": "Shri Gajanan Maharaj"}
    for n in run:
        for sh in run[n]["plan"]["shots"]:
            sh["dialogue"] = []
    for l in audio["lines"]:
        if l["voice"] != "narrator" and l["priority"] == "core":
            n = int(l["scene"][1:])
            run[n]["plan"]["shots"][0]["dialogue"].append({"speaker": names[l["voice"]], "ovi": f"A1:{l['ovi']}", "marathi": l["marathi"], "meaning_en": "m"})
    return run, tm, audio


def test_the_scorer_checks_the_spoken_words_against_the_planned_line():
    run, tm, audio = authored_run()
    assert ev.score_run(run, EXPECTED, tm, audio=audio)["failed"] == 0
    d = next(x for x in run[9]["plan"]["shots"][0]["dialogue"] if x["ovi"] == "A1:140")
    d["marathi"] = "x"                                                               # right ovi, right speaker, invented words
    rep = ev.score_run(run, EXPECTED, tm, audio=audio)
    assert any(c["id"] == "S9-dialogue-140" and not c["passed"] for c in rep["checks"])


@pytest.mark.parametrize("text", ["in March 1878", "in May 1878", "on Monday"])
def test_the_scorer_catches_march_may_and_weekdays(text):
    run, tm = good_run()
    run[1]["plan"]["shots"][0]["performance"] = text
    assert ev.score_run(run, EXPECTED, tm)["failed"] >= 1, text


def test_readiness_with_an_adverb_passes_and_completed_prostration_fails():
    run, tm = good_run()
    run[9]["plan"]["shots"][0]["performance"] = "The men are ready to humbly prostrate themselves at his feet"
    assert ev.score_run(run, EXPECTED, tm)["failed"] == 0
    run[9]["plan"]["shots"][0]["performance"] = "The men prostrate themselves at his feet"
    assert ev.score_run(run, EXPECTED, tm)["failed"] >= 1
    run[9]["plan"]["shots"][0]["performance"] = "Both men on their knees, prostrated, ready to rise"
    assert ev.score_run(run, EXPECTED, tm)["failed"] >= 1


def test_a_recipient_is_not_the_actor():
    run, tm = good_run()
    run[7]["plan"]["shots"][0]["action"] = "Bankatlal hands the gourd to Damodarpant, then enters the house"
    assert ev.score_run(run, EXPECTED, tm)["failed"] >= 1
    run[7]["plan"]["shots"][0]["action"] = "Bankatlal hands the gourd to Damodarpant, who goes into the house to fetch water"
    assert ev.score_run(run, EXPECTED, tm)["failed"] == 0


def test_a_completed_action_after_a_readiness_is_not_exempt():
    run, tm = good_run()
    run[9]["plan"]["shots"][0]["performance"] = "The men are ready to bow, then prostrated themselves at his feet"
    assert ev.score_run(run, EXPECTED, tm)["failed"] >= 1
    run[9]["plan"]["shots"][0]["performance"] = "The men are ready to bow and humbly fall at his feet"
    assert ev.score_run(run, EXPECTED, tm)["failed"] == 0


def test_who_resolves_to_the_person_named_just_before_it():
    run, tm = good_run()
    run[7]["plan"]["shots"][0]["action"] = "Damodarpant hands the gourd to Bankatlal, who enters the house to fetch water"
    assert ev.score_run(run, EXPECTED, tm)["failed"] >= 1
    run[7]["plan"]["shots"][0]["action"] = "Bankatlal hands the gourd to Damodarpant, who enters the house to fetch water"
    assert ev.score_run(run, EXPECTED, tm)["failed"] == 0
