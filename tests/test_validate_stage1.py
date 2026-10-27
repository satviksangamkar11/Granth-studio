import copy
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("validate_stage1", ROOT / "scripts" / "pipeline" / "validate_stage1.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

SCRIPT_IDS = ["S1-L1", "S1-L2", "S2-L1"]
CORE = {"S1-L1", "S2-L1"}
OVIS = set(range(1, 11))
UNF = {10}
PALETTE = {"bed_village", "fx_bell"}


def good():
    return {
        "scenes": {"adhyay": 1, "scenes": [
            {"scene_id": "S1", "ovi_range": [1, 5], "goal": "g", "turn": {"ovi": 3, "text": "t"}, "line_ids": ["S1-L1", "S1-L2"]},
            {"scene_id": "S2", "ovi_range": [6, 9], "goal": "g", "turn": {"ovi": 7, "text": "t"}, "line_ids": ["S2-L1"]}]},
        "shots": {"adhyay": 1, "shots": [
            {"shot_id": "S1-1", "scene_id": "S1", "ovi_ids": [1, 2], "beat_line_ids": ["S1-L1"], "preset_hint": "03_slow_cinematic_push", "needs_cutout": False, "pose": "p", "framing": "f"},
            {"shot_id": "S1-2", "scene_id": "S1", "ovi_ids": [3], "beat_line_ids": ["S1-L2"], "preset_hint": "03_slow_cinematic_push", "needs_cutout": False, "pose": "p", "framing": "f"},
            {"shot_id": "S2-1", "scene_id": "S2", "ovi_ids": [6], "beat_line_ids": ["S2-L1"], "preset_hint": "03_slow_cinematic_push", "needs_cutout": False, "pose": "p", "framing": "f"}]},
        "briefs": {"adhyay": 1, "images": [{"image_id": "s1_maharaj_seated", "scene_id": "S1", "shot_ids": ["S1-1"], "people": [{"name": "Maharaj", "position": "centre", "pose": "seated", "gaze": "forward"}],
                                            "place_id": "road", "prop": None, "camera": "medium", "reason_new": "new"}]},
        "sounds": {"adhyay": 1, "cues": [{"scene_id": "S1", "anchor_line_id": "S1-L1", "palette_id": "bed_village", "kind": "bed"}]},
        "questions": {"adhyay": 1, "questions": [{"id": "Q1", "text": "q", "scene_id": "S1"}]},
    }


def run(d, adhyay=1, script=SCRIPT_IDS, core=CORE, ovis=OVIS, unf=UNF, palette=PALETTE):
    return v.validate_stage1(adhyay, d["scenes"], d["shots"], d["briefs"], d["sounds"], d["questions"], script, core, ovis, unf, palette)


def has(errs, *words):
    return any(all(w in e for w in words) for e in errs)


def mutated(fn):
    d = good()
    fn(d)
    return run(d)


def test_valid_set_is_empty():
    assert run(good()) == []


def test_schema_failure_returns_at_once_for_all_five_documents():
    for doc in ("scenes", "shots", "briefs", "sounds", "questions"):
        d = good()
        d[doc]["surprise"] = 1
        errs = run(d)
        assert errs and not has(errs, "outside")
    d = good()
    d["shots"]["shots"][0]["start_s"] = 1.5                                   # a timing key from Kimi
    errs = run(d)
    assert has(errs, "start_s") and len(errs) == len([e for e in errs if "start_s" in e])
    d = good()
    d["scenes"]["scenes"][0]["extra"] = {"nested": 1}
    assert run(d)


def test_adhyay_must_match_in_every_document():
    assert has(run(good(), adhyay=2), "adhyay")
    for doc in ("scenes", "shots", "briefs", "sounds", "questions"):
        d = good()
        d[doc]["adhyay"] = 2
        assert has(run(d), "adhyay"), doc


@pytest.mark.parametrize("fn,words", [
    (lambda d: d["scenes"]["scenes"].__setitem__(1, dict(d["scenes"]["scenes"][1], scene_id="S1")), ("S1", "duplicate")),
    (lambda d: d["scenes"]["scenes"][0].__setitem__("ovi_range", [5, 1]), ("S1", "range")),
    (lambda d: d["scenes"]["scenes"][1].__setitem__("ovi_range", [5, 9]), ("overlap",)),
    (lambda d: d["scenes"]["scenes"][1].__setitem__("ovi_range", [6, 8]), ("ovi 9",)),
    (lambda d: d["scenes"]["scenes"][1].__setitem__("ovi_range", [6, 10]), ("ovi 10",)),
    (lambda d: d["scenes"]["scenes"][0].__setitem__("ovi_range", [1, 11]), ("ovi 11",)),
    (lambda d: d["scenes"]["scenes"][0].__setitem__("turn", {"ovi": 9, "text": "t"}), ("S1", "turn")),
    (lambda d: d["scenes"]["scenes"][0].__setitem__("line_ids", ["S1-L1", "S1-L9"]), ("S1-L9",)),
    (lambda d: d["scenes"]["scenes"][0].__setitem__("line_ids", ["S1-L1", "S1-L1"]), ("S1-L1", "twice")),
    (lambda d: d["scenes"]["scenes"][1].__setitem__("line_ids", ["S2-L1", "S1-L2"]), ("S1-L2", "twice")),
    (lambda d: d["scenes"]["scenes"][0].__setitem__("line_ids", ["S1-L2", "S1-L1"]), ("order",)),
    (lambda d: d["scenes"]["scenes"][1].__setitem__("line_ids", ["S1-L2"]), ("S2-L1", "core")),
])
def test_scene_rules(fn, words):
    assert has(mutated(fn), *words)


@pytest.mark.parametrize("fn,words", [
    (lambda d: d["shots"]["shots"].__setitem__(1, dict(d["shots"]["shots"][1], shot_id="S1-1")), ("S1-1", "duplicate")),
    (lambda d: d["shots"]["shots"][2].__setitem__("scene_id", "S9"), ("S2-1", "scene")),
    (lambda d: d["shots"]["shots"][0].__setitem__("ovi_ids", [1, 8]), ("S1-1", "ovi 8")),
    (lambda d: d["shots"]["shots"][0].__setitem__("beat_line_ids", ["S2-L1"]), ("S1-1", "S2-L1")),
    (lambda d: d["shots"]["shots"].__setitem__(1, dict(d["shots"]["shots"][1], shot_id="S1-3")), ("S1-3", "consecutive")),
    (lambda d: d["shots"]["shots"].pop(2), ("S2", "no shots")),
    (lambda d: d["shots"]["shots"][1].__setitem__("beat_line_ids", []), ("S1-L2", "no shot")),
])
def test_shot_rules(fn, words):
    assert has(mutated(fn), *words)


@pytest.mark.parametrize("fn,words", [
    (lambda d: d["briefs"]["images"][0].__setitem__("image_id", "s2_maharaj_seated"), ("s2_maharaj_seated", "prefix")),
    (lambda d: d["briefs"]["images"].append(copy.deepcopy(d["briefs"]["images"][0])), ("s1_maharaj_seated", "duplicate")),
    (lambda d: d["briefs"]["images"][0].__setitem__("scene_id", "S7"), ("S7",)),
    (lambda d: d["briefs"]["images"][0].__setitem__("shot_ids", ["S9-1"]), ("S9-1",)),
    (lambda d: d["briefs"]["images"][0].__setitem__("shot_ids", ["S2-1"]), ("S2-1", "same scene")),
])
def test_image_brief_rules(fn, words):
    assert has(mutated(fn), *words)


@pytest.mark.parametrize("fn,words", [
    (lambda d: d["sounds"]["cues"][0].__setitem__("scene_id", "S7"), ("S7",)),
    (lambda d: d["sounds"]["cues"][0].__setitem__("anchor_line_id", "S2-L1"), ("S2-L1", "anchor")),
    (lambda d: d["sounds"]["cues"][0].__setitem__("palette_id", "bed_unknown"), ("bed_unknown", "palette")),
    (lambda d: d["sounds"]["cues"][0].update({"palette_id": "NEED_NEW"}), ("NEED_NEW", "reason")),
    (lambda d: d["sounds"]["cues"][0].__setitem__("kind", "fx"), ("kind",)),
    (lambda d: d["questions"]["questions"].append({"id": "Q1", "text": "again"}), ("Q1", "duplicate")),
    (lambda d: d["questions"]["questions"][0].__setitem__("scene_id", "S7"), ("S7",)),
])
def test_sound_and_question_rules(fn, words):
    assert has(mutated(fn), *words)


def test_need_new_with_a_reason_is_valid_and_messages_are_stable():
    d = good()
    d["sounds"]["cues"][0].update({"palette_id": "NEED_NEW", "reason": "silence cue"})
    assert run(d) == []
    d = good()
    d["scenes"]["scenes"][1]["ovi_range"] = [5, 9]
    d["shots"]["shots"][0]["ovi_ids"] = [1, 8]
    assert run(d) == run(copy.deepcopy(d)) and len(run(d)) >= 2              # same input, same messages, same order; one problem never hides another
    assert isinstance(run(good(), script=[]), list)                           # missing foreign keys give messages, never exceptions
