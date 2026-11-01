import math
"""Structural dry run (no model, no network, no cost): the director consumes the REAL nine-scene split, audio plan and timing plan; a compliant plan exists for every scene and the validator holds."""
import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("dt", ROOT / "scripts" / "source" / "director_test.py")
dt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dt)
a_spec = importlib.util.spec_from_file_location("a1a", ROOT / "scripts" / "source" / "a1_audio.py")
a1 = importlib.util.module_from_spec(a_spec)
a_spec.loader.exec_module(a1)

files, OVIS, INDEX = dt.load_inputs()
PJ = dt.load_preset_json(INDEX)
SPEAKERS = dt.speaker_registry(files["analysis"].splitlines())
ROWS = dt.speaker_rows(files["addendum"].splitlines())                  # frozen table + owner overrides (2026-11-01)
EDITS = json.loads((ROOT / "canon" / "story_split_edits" / "A1_rev1.json").read_text(encoding="utf-8"))
AUDIO = json.loads((ROOT / "canon" / "audio" / "A1_audio_plan.json").read_text(encoding="utf-8"))
TIMING = json.loads((ROOT / "canon" / "audio" / "A1_timing_plan.json").read_text(encoding="utf-8"))
SPLIT_HASH = AUDIO["split_sha256"]
ss_spec = importlib.util.spec_from_file_location("ss", ROOT / "scripts" / "source" / "story_split.py")
ss = importlib.util.module_from_spec(ss_spec)
ss_spec.loader.exec_module(ss)
MACRO = ss.build_macro({"stories": EDITS["stories"], "unfilmed_ranges": EDITS["unfilmed_ranges"]}, 1, sorted(OVIS), "x" * 64)
es_spec = importlib.util.spec_from_file_location("easy", ROOT / "scripts" / "source" / "easy_script.py")
easy = importlib.util.module_from_spec(es_spec)
es_spec.loader.exec_module(easy)
SIMPLE = easy.load_simple()
SPLIT = {"macro": MACRO, "hash": SPLIT_HASH, "edits": EDITS, "audio": easy.overlay(AUDIO, SIMPLE), "timing": TIMING, "script_sha256": easy.script_sha256()}      # the director speaks the owner's EASY wording
PRESETS = {p["preset"]: p["assets"] for p in INDEX}
SCENES = [(int(sc["scene_id"][1:]), sc) for st in MACRO["stories"] for sc in st["scenes"]]


SPEAKER_NAME = {"bankatlal": "Bankatlal Agarwal", "damodarpant": "Damodarpant Kulkarni", "gajanan": "Shri Gajanan Maharaj"}      # the registered names


def planned_dialogue(ov, shot):
    """The character lines the audio plan starts in this shot, spoken by their character in exact Marathi."""
    return [{"speaker": SPEAKER_NAME[w["voice"]], "ovi": f"A1:{w['ovi']}", "marathi": w["marathi"], "meaning_en": "m"} for w in ov["dialogue_plan"].get(shot, [])]


def compliant_plan(n, sc, ov):
    """A minimal plan that obeys the timeline: the exact shot count, every narration ovi listed in the shot where it starts, every ovi of the scene shown, one declared image per shot."""
    lo, hi = sc["ovi_range"]
    k = ov["shots_target"]
    shown = [[] for _ in range(k)]
    for shot, ovis in ov["timeline"].items():
        shown[shot - 1] += ovis
    for i, o in enumerate(range(lo, hi + 1)):                                    # spread the rest so every ovi of the scene is shown somewhere
        if not any(o in s for s in shown):
            shown[min(i * k // (hi - lo + 1), k - 1)].append(o)
    for i in range(k):                                                           # visual-only shots continue the previous ovi
        if not shown[i]:
            shown[i] = [shown[i - 1][-1] if i else lo]
    shots = [{"shot_id": f"S{n}-{i + 1}", "ovi_ids": sorted({f"A1:{o}" for o in shown[i]}), "preset": "03_slow_cinematic_push", "assets": {"img": f"s{n}_img{i + 1}"},
              "action": "The camera pushes in on the held picture", "held_pose": "Maharaj seated in a worn old bandi", "needs": ["none"], "performance": "calm held pose",
              "camera": "slow push in", "dialogue": planned_dialogue(ov, i + 1), "claims": [{"kind": "person", "term": "Maharaj", "source": "PACKET"}], "staging": ["STAGING: held picture"], "transition_out": "cut"} for i in range(k)]
    return {"scene_id": f"S{n}", "chapter": 1, "ovi_range": [lo, hi], "goal": "g", "turn": {"ovi": f"A1:{lo}", "text": "t"}, "shots": shots,
            "images_needed": [{"image_id": s["assets"]["img"], "description": "Maharaj seated, held picture"} for s in shots]}


def check(n, sc, ov, plan):
    ctx = {"packet_text": dt.build_prompt(n, tuple(sc["ovi_range"]), files, OVIS, INDEX, [], 1, PJ, ov)[1], "speakers": SPEAKERS, "preset_json": PJ, "prop_materials": {},
           "speaker_rows": ROWS, "shots_target": ov["shots_target"], "timeline": ov["timeline"], "dialogue_plan": ov["dialogue_plan"], "scene_image_prefix": True}
    ovi_text = {k: v for k, v in OVIS.items() if sc["ovi_range"][0] <= k <= sc["ovi_range"][1]}
    return dt.validate_scene(plan, PRESETS, ovi_text, tuple(sc["ovi_range"]), ctx, 1, f"S{n}")


@pytest.mark.parametrize("n,sc", SCENES)
def test_a_compliant_plan_exists_and_validates_for_every_scene(n, sc):
    ov = dt.split_scene_override(n, SPLIT, OVIS)
    errors, warnings = check(n, sc, ov, compliant_plan(n, sc, ov))
    assert errors == [], errors
    assert not [w for w in warnings if "ovis not shown" in w]                      # every ovi of the scene is covered


@pytest.mark.parametrize("n,sc", SCENES)
def test_the_prompt_carries_the_scene_narration_timeline_and_notes(n, sc):
    ov = dt.split_scene_override(n, SPLIT, OVIS)
    system, user = dt.build_prompt(n, tuple(sc["ovi_range"]), files, OVIS, INDEX, ["Bankatlal"], 1, PJ, ov)
    tm = next(s for s in TIMING["scenes"] if s["scene"] == f"S{n}")
    assert f"direct EXACTLY {tm['planned_shots']} shots" in user and ov["shots_target"] == tm["planned_shots"] >= sc["shot_budget"]      # owner 2026-11-01: S2/S7 grew to fit the speech
    for l in [l for l in AUDIO["lines"] if l["scene"] == f"S{n}" and l["priority"] == "core"]:
        assert l["id"] in user and l["marathi"] in user                              # the exact verse is in the prompt
    for k in range(sc["ovi_range"][0], sc["ovi_range"][1] + 1):
        assert f"A1:{k}: {OVIS[k]}" in user                                          # every ovi of the scene is in the materials
    assert "DIRECTION NOTES" in user and "Damodarpant (not Bankatlal)" in user and "approved split" in user and sc["brief"] in user


def test_the_wrong_shot_count_and_a_missing_narration_ovi_are_caught():
    n, sc = SCENES[4]                                                                # scene 5 (the eating scene)
    ov = dt.split_scene_override(n, SPLIT, OVIS)
    good = compliant_plan(n, sc, ov)
    short = copy.deepcopy(good)
    short["shots"].pop()
    short["images_needed"].pop()
    assert any("exactly" in e for e in check(n, sc, ov, short)[0])
    bad = copy.deepcopy(good)
    first_with_narration = min(ov["timeline"])
    bad["shots"][first_with_narration - 1]["ovi_ids"] = [f"A1:{sc['ovi_range'][0]}"] if sc["ovi_range"][0] not in ov["timeline"][first_with_narration] else [f"A1:{sc['ovi_range'][1]}"]
    assert any("narration timeline starts" in e for e in check(n, sc, ov, bad)[0])


def test_the_opening_is_exactly_two_shots_and_the_teaching_scene_has_the_room_it_needs():
    ov1 = dt.split_scene_override(1, SPLIT, OVIS)
    ov9 = dt.split_scene_override(9, SPLIT, OVIS)
    assert ov1["shots_target"] == 2 and ov9["shots_target"] >= 10
    covered = {o for v in ov9["timeline"].values() for o in v}
    assert {138, 139, 140, 141, 142, 143, 144} <= covered                            # the whole teaching, the readiness to fall and the run are in the timeline


def test_a_split_whose_audio_plan_was_built_for_another_hash_is_refused(tmp_path):
    runs = tmp_path / "runs"
    (runs / "r").mkdir(parents=True)
    (runs / "r" / "macro_A1.json").write_text(json.dumps({"macro": MACRO, "macro_sha256": "f" * 64}), encoding="utf-8")
    old = dt.RUNS
    dt.RUNS = runs
    try:
        with pytest.raises(SystemExit):
            dt.load_split("r")
    finally:
        dt.RUNS = old


def scene_with_dialogue(ovi):
    for n, sc in SCENES:
        if sc["ovi_range"][0] <= ovi <= sc["ovi_range"][1]:
            return n, sc, dt.split_scene_override(n, SPLIT, OVIS)


def shot_index_with_dialogue(ov, ovi):
    return next(k for k, ws in ov["dialogue_plan"].items() if any(w["ovi"] == ovi for w in ws))


def test_dialogue_is_bound_to_the_planned_character_lines_exactly():
    n, sc, ov = scene_with_dialogue(119)
    good = compliant_plan(n, sc, ov)
    assert check(n, sc, ov, good)[0] == []
    k = shot_index_with_dialogue(ov, 119)
    # (a) Bankatlal 'speaking' the narrator's introduction of ovi 119 (charans 1-2) is NOT a planned line
    bad = copy.deepcopy(good)
    bad["shots"][k - 1]["dialogue"] = [{"speaker": "Bankatlal Agarwal", "ovi": "A1:119", "marathi": OVIS[119].split("।")[0].strip() + " । " + OVIS[119].split("।")[1].strip(), "meaning_en": "m"}]
    assert any("not one of the character lines planned" in e for e in check(n, sc, ov, bad)[0])
    # (b) the planned line missing
    missing = copy.deepcopy(good)
    missing["shots"][k - 1]["dialogue"] = []
    assert any("is missing from this shot's dialogue" in e for e in check(n, sc, ov, missing)[0])
    # (c) the right words from the wrong person
    wrong = copy.deepcopy(good)
    wrong["shots"][k - 1]["dialogue"][0]["speaker"] = "Damodarpant Kulkarni"
    assert any("not one of the character lines planned" in e for e in check(n, sc, ov, wrong)[0])
    # (d) the right line in the wrong shot
    moved = copy.deepcopy(good)
    other = 0 if k != 1 else 1
    moved["shots"][other]["dialogue"] = moved["shots"][k - 1]["dialogue"]
    moved["shots"][k - 1]["dialogue"] = []
    assert check(n, sc, ov, moved)[0]


def test_joint_reasoning_100_101_cannot_be_given_to_one_named_man():
    n, sc, ov = scene_with_dialogue(100)
    plan = compliant_plan(n, sc, ov)
    plan["shots"][0]["dialogue"] = [{"speaker": "Bankatlal Agarwal", "ovi": "A1:100", "marathi": OVIS[100], "meaning_en": "m"}]
    assert any("not one of the character lines planned" in e for e in check(n, sc, ov, plan)[0])


def test_dialogue_entries_exist_only_for_character_voices_in_the_plan():
    voices = {w["voice"] for n, sc in SCENES for ws in dt.split_scene_override(n, SPLIT, OVIS)["dialogue_plan"].values() for w in ws}
    assert voices == {"bankatlal", "damodarpant", "gajanan"}
    assert sum(len(ws) for n, sc in SCENES for ws in dt.split_scene_override(n, SPLIT, OVIS)["dialogue_plan"].values()) == len([l for l in AUDIO["lines"] if l["voice"] != "narrator" and l["priority"] == "core"])


def run_with(tmp_path, macro=None, edits=None):
    runs = tmp_path / "runs"
    (runs / "r").mkdir(parents=True, exist_ok=True)
    res = {"macro": macro or MACRO, "macro_sha256": SPLIT_HASH}
    (runs / "r" / "macro_A1.json").write_text(json.dumps(res), encoding="utf-8")
    ep = tmp_path / "edits.json"
    ep.write_text(json.dumps(edits or EDITS), encoding="utf-8")
    return runs, ep


def test_load_split_recomputes_the_hash_and_checks_the_edits_against_it(tmp_path):
    old = dt.RUNS
    try:
        # the recorded hash is not the hash of the saved macro: refused (a changed brief under an unchanged label)
        runs, ep = run_with(tmp_path)
        dt.RUNS = runs
        with pytest.raises(SystemExit):
            dt.load_split("r", ep)
        # a macro whose recorded hash is right but whose audio plan was built for another hash: refused
        res = {"macro": MACRO, "macro_sha256": dt._sha_obj(MACRO)}
        (runs / "r" / "macro_A1.json").write_text(json.dumps(res), encoding="utf-8")
        with pytest.raises(SystemExit):
            dt.load_split("r", ep)
        # edits that differ from the macro: refused
        bad_edits = copy.deepcopy(EDITS)
        bad_edits["stories"][0]["scenes"][0]["brief"] = "a changed brief"
        ep.write_text(json.dumps(bad_edits), encoding="utf-8")
        with pytest.raises(SystemExit):
            dt.load_split("r", ep)
    finally:
        dt.RUNS = old


def test_the_hash_helper_equals_the_story_split_hash():
    assert dt._sha_obj(MACRO) == ss.sha_of(MACRO)


def test_the_director_plan_uses_the_easy_wording_not_the_verse():
    n, sc, ov = scene_with_dialogue(next(w["ovi"] for l in AUDIO["lines"] if l["voice"] != "narrator" and l["priority"] == "core" for w in [l]))
    ws = [w for ws_ in ov["dialogue_plan"].values() for w in ws_]
    assert ws and all(w["marathi"] == SIMPLE[w["id"]]["mr"] and w["marathi"] != next(l for l in AUDIO["lines"] if l["id"] == w["id"])["marathi"] for w in ws)
    assert SPLIT["script_sha256"][:12] in ov["brief_block"]


def test_easy_dialogue_passes_but_the_old_verse_wording_or_an_invented_line_is_rejected():
    n, sc, ov = scene_with_dialogue(next(l["ovi"] for l in AUDIO["lines"] if l["voice"] != "narrator" and l["priority"] == "core"))
    plan = compliant_plan(n, sc, ov)
    assert check(n, sc, ov, plan)[0] == []
    shot = next(s for s in plan["shots"] if s["dialogue"])
    verse = next(l["marathi"] for l in AUDIO["lines"] if l["ovi"] == int(shot["dialogue"][0]["ovi"].split(":")[1]) and l["voice"] != "narrator")
    shot["dialogue"][0]["marathi"] = verse
    assert any("not one of the character lines planned" in e for e in check(n, sc, ov, plan)[0])


def test_the_easy_overlay_refuses_a_line_that_has_no_easy_wording():
    simple = {k: v for k, v in SIMPLE.items() if k != "S2-L4"}
    with pytest.raises(SystemExit):
        easy.overlay(AUDIO, simple)


@pytest.mark.parametrize("n,sc", SCENES)
def test_the_prompt_carries_both_measured_durations_and_cut_crossings(n, sc):
    ov = dt.split_scene_override(n, SPLIT, OVIS)
    user = dt.build_prompt(n, tuple(sc["ovi_range"]), files, OVIS, INDEX, [], 1, PJ, ov)[1]
    tm = next(s for s in TIMING["scenes"] if s["scene"] == f"S{n}")
    assert "SHARED BEATS" in user
    for b in tm["beats"]:
        l = next(x for x in AUDIO["lines"] if x["id"] == b["line"])
        assert f"{b['line']} starts shot {b['shot']}" in user and f"Marathi {l['seconds']['mr']:.2f} s, Hindi {l['seconds']['hi']:.2f} s" in user
        crossing = min(math.ceil(b["end_s"] / 6 - 1e-9), tm["planned_shots"]) > b["shot"]
        row = next(r for r in user.splitlines() if r.startswith(f"{b['line']} starts shot"))
        assert ("CONTINUES over the cut" in row) == crossing


def test_a_director_plan_that_writes_a_timing_is_rejected():
    n, sc = SCENES[3]                                                                # S4
    ov = dt.split_scene_override(n, SPLIT, OVIS)
    plan = compliant_plan(n, sc, ov)
    plan["shots"][0]["start_s"] = 1.5
    errors, _ = check(n, sc, ov, plan)
    assert any("start_s" in e for e in errors)


def test_a_line_ending_exactly_on_a_cut_does_not_continue_and_a_long_one_lists_every_shot():
    n, sc = SCENES[3]
    tm = copy.deepcopy(TIMING)
    s4 = next(s for s in tm["scenes"] if s["scene"] == "S4")
    s4["beats"][0].update(start_s=0.5, end_s=6.0)
    s4["beats"][2].update(shot=1, start_s=0.5, end_s=14.0)
    ov = dt.split_scene_override(n, {**SPLIT, "timing": tm}, OVIS)
    rows = {r.split()[0]: r for r in ov["brief_block"].splitlines() if " starts shot " in r}
    assert "CONTINUES" not in rows["S4-L1"]
    assert "shots 2, 3" in rows["S4-L3"]


def test_an_image_id_without_the_scene_prefix_is_rejected():
    n, sc = SCENES[3]
    ov = dt.split_scene_override(n, SPLIT, OVIS)
    plan = compliant_plan(n, sc, ov)
    old = plan["shots"][0]["assets"]["img"]
    plan["shots"][0]["assets"]["img"] = "sky_morning"
    plan["images_needed"][0]["image_id"] = "sky_morning"
    errors, _ = check(n, sc, ov, plan)
    assert any("must start with 's4_'" in e for e in errors) and old.startswith("s4_")


def test_one_call_mode_never_asks_the_director_twice(monkeypatch):
    n, sc = SCENES[3]
    ov = dt.split_scene_override(n, SPLIT, OVIS)
    calls = []

    class Dir:
        name = "fake"
        def __call__(self, *a, **k):
            calls.append(1)
            return None
    monkeypatch.setattr(dt, "ONE_CALL", True)
    monkeypatch.setattr(dt, "_ask", lambda *a, **k: (calls.append(1), None)[1])
    ctx = {"speakers": SPEAKERS, "preset_json": PJ, "prop_materials": {}, "speaker_rows": ROWS}
    out = dt.direct_scene(Dir(), [], n, tuple(sc["ovi_range"]), 1, files, OVIS, INDEX, ctx, ov)
    assert len(calls) == 1 and out["result"] == "FAILED"
