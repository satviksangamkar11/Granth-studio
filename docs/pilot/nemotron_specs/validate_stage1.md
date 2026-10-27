# Spec: write ONE file `scripts/pipeline/validate_stage1.py`. The frozen tests are in `tests/test_validate_stage1.py` (shown below; they load your module by path with importlib).
Style: `from __future__ import annotations`, standard library (plus `jsonschema` where stated), short docstrings, no print, no network, no file writes by the module (tests may write under pytest `tmp_path`), nothing at import time. The module never raises for bad DATA: it returns error strings (stable order, each message starts with the item id such as a line id, shot id, image id or document name). Type/argument misuse (wrong argument types) may raise TypeError/ValueError only where the API says so. The tests below are FROZEN: make them pass, do not change them. Messages are plain English and MUST contain the keywords the tests look for (case-sensitive).

## Inputs and schemas relied on
Schemas are `ROOT/"schemas"/"<name>.schema.json"` with ROOT = parent of the `scripts` folder (the module computes it from `__file__`): stage1_scenes, stage1_shots, stage1_image_briefs, stage1_sound_suggestions, stage1_questions; validate with `jsonschema.Draft202012Validator`. Shapes: scenes {adhyay, scenes:[{scene_id, ovi_range:[lo,hi], goal, turn:{ovi,text}, line_ids}]}; shots {adhyay, shots:[{shot_id, scene_id, ovi_ids, beat_line_ids, preset_hint, needs_cutout, pose, framing}]}; briefs {adhyay, images:[{image_id, scene_id, shot_ids, people, place_id, prop, camera, reason_new}]}; sounds {adhyay, cues:[{scene_id, anchor_line_id, palette_id, kind, reason?}]}; questions {adhyay, questions:[{id, text, scene_id?}]}.
## API
`validate_stage1(adhyay, scenes, shots, briefs, sounds, questions, script_line_ids, core_line_ids, chapter_ovis, unfilmed_ovis, palette_ids) -> list[str]` (`script_line_ids` is an ordered list; the others are sets).
1. Schema step: one message per error, "<document name> <path>: <message>" (document names: scenes, shots, briefs, sounds, questions). If ANY schema error exists, return all of them at once (no later check runs). A nested unknown key is a schema error.
2. "<document> adhyay <n> does not match <adhyay>" for each document whose adhyay differs.
3. Scenes: "<scene_id>: duplicate scene id"; "<scene_id>: range [lo, hi] is invalid" if lo > hi; "scenes <a> and <b> overlap" for overlapping ranges; "ovi <n> is in no scene and not unfilmed" for each chapter ovi not covered and not unfilmed (ascending); "<scene_id>: ovi <n> is not in the chapter" for each ovi of a range outside chapter_ovis; "<scene_id>: ovi <n> is unfilmed but inside the range" for each ovi of a range that is in unfilmed_ovis (unfilmed ovis belong to no scene); "<scene_id>: turn ovi <n> is outside its range"; "<scene_id>: line <id> is not in the script"; "<id>: line used twice" (within or across scenes); "<scene_id>: lines are not in script order" (each scene's line_ids must appear in the order of script_line_ids); "<id>: core line is in no scene" for each core id in no scene.
4. Shots: "<shot_id>: duplicate shot id"; "<shot_id>: scene <s> does not exist"; "<shot_id>: ovi <n> is outside scene <s> range [lo, hi]"; "<shot_id>: beat line <id> is not a line of scene <s>"; "<scene_id>: shot ids must be consecutive from <scene_id>-1" (per scene, file order; the message must contain the word consecutive and the offending shot id); "<scene_id>: scene has no shots"; "<id>: core line is in no shot beat" for each core line missing from every shot's beat_line_ids (the message must contain the line id and the words "no shot").
5. Briefs: "<image_id>: id must start with the scene prefix <s4_>" (word "prefix"); "<image_id>: duplicate image id"; "<image_id>: scene <s> does not exist" (use the scene id text, e.g. "S7"); "<image_id>: shot <shot_id> does not exist" (use the shot id text); "<image_id>: shot <shot_id> is not in the same scene" (words "same scene").
6. Sounds: "<scene_id>: cue scene does not exist" (contains the scene id); "<anchor>: anchor line is not a line of scene <s>" (word "anchor"); "<palette_id>: not in the palette" (word "palette") unless it is "NEED_NEW"; "NEED_NEW needs a reason" when palette_id is NEED_NEW and reason is missing or blank; "<palette_id>: kind <kind> does not match" (word "kind") for bed_/fx_ prefix mismatches.
7. Questions: "<id>: duplicate question id"; "<id>: scene <s> does not exist" (scene id text).
Collect errors from ALL of steps 3-7 (one problem never hides another), in the order above, each step in file order. Missing references never raise exceptions.

## The frozen tests (do not change)
FILE tests/test_validate_stage1.py:
```python
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

```

Reply with only: FILE: scripts/pipeline/validate_stage1.py followed by its code block.
