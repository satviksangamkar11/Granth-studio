from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGG_PATH = ROOT / "scripts" / "pipeline" / "stage1" / "aggregate.py"
BASE_PATH = ROOT / "docs" / "pilot" / "nemotron_specs" / "stage1_base.json"

spec = importlib.util.spec_from_file_location("stage1_aggregate", AGG_PATH)
assert spec is not None and spec.loader is not None
agg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agg)

BASE = json.loads(BASE_PATH.read_text(encoding="utf-8"))
BASE_DOCS = BASE["docs"]
BASE_CTX = BASE["ctx"]


def _make_minimal_valid_docs(ovis_covered: list[int] | None = None) -> tuple[dict, dict]:
    """Create a minimal valid set of documents and ctx for the given ovis.
    This is used to isolate cross-rule tests."""
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # We'll adjust the base to only involve the ovis we care about.
    # But the base is already valid. We'll instead modify the base in the tests.
    return docs, ctx


def test_base_valid():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    errs = agg.validate_all(1, docs, ctx)
    assert errs == []


def test_x1_story_ovi_not_in_story_event():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Make ovi 3 STORY but events only cover [4,5] as discourse
    docs["story_map"]["ovi_types"] = [{"ovi": 3, "type": "STORY"}, {"ovi": 4, "type": "STORY"}]
    docs["story_map"]["events"] = [{"event_id": "E1", "kind": "discourse", "title": "t", "ovi_range": [4, 5], "key_ovis": [4], "closure": "RESOLVED_IN_ADHYAY"}]
    # Adjust ctx chapter_ovis to only 3,4 so story_map unit validation passes
    ctx["chapter_ovis"] = [3, 4]
    # Ensure coverage for 3,4 is not PROPOSE_OMISSION and they are in shots/scenes
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] in (3, 4):
            c["disposition"] = "VISUALISED"
    # Ensure scenes cover 3,4
    for sc in docs["scenes"]["scenes"]:
        sc["ovi_range"] = [3, 4]
    # Ensure shots include 3,4
    for sh in docs["shots"]["shots"]:
        sh["ovi_ids"] = [3, 4]
    # No unfilmed ovis
    ctx["unfilmed_ovis"] = []
    errs = agg.validate_all(1, docs, ctx)
    assert any("story_map: ovi 3 is typed STORY but is in no story event" in e for e in errs)
    # Corrected twin: expand event range to cover 3 and make it story kind
    docs["story_map"]["events"][0]["ovi_range"] = [3, 5]
    docs["story_map"]["events"][0]["kind"] = "story"
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any("story_map: ovi 3 is typed STORY but is in no story event" in e for e in errs2)


def test_x1_teaching_ovi_not_in_discourse_event():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Make ovi 6 TEACHING but events only cover [1,5] as story
    docs["story_map"]["ovi_types"] = [{"ovi": 6, "type": "TEACHING"}, {"ovi": 4, "type": "TEACHING"}]
    docs["story_map"]["events"] = [{"event_id": "E1", "kind": "story", "title": "t", "ovi_range": [1, 5], "key_ovis": [4], "closure": "RESOLVED_IN_ADHYAY"}]
    ctx["chapter_ovis"] = [4, 6]
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] in (4, 6):
            c["disposition"] = "VISUALISED"
    for sc in docs["scenes"]["scenes"]:
        sc["ovi_range"] = [4, 6]
    for sh in docs["shots"]["shots"]:
        sh["ovi_ids"] = [4, 6]
    ctx["unfilmed_ovis"] = []
    errs = agg.validate_all(1, docs, ctx)
    assert any("story_map: ovi 6 is typed TEACHING but is in no discourse event" in e for e in errs)
    # Corrected twin: add discourse event covering 6
    docs["story_map"]["events"].append({"event_id": "E2", "kind": "discourse", "title": "t2", "ovi_range": [6, 6], "key_ovis": [6], "closure": "RESOLVED_IN_ADHYAY"})
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any("story_map: ovi 6 is typed TEACHING but is in no discourse event" in e for e in errs2)


def test_x1_empty_events():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    docs["story_map"]["ovi_types"] = [{"ovi": 1, "type": "STORY"}, {"ovi": 2, "type": "TEACHING"}]
    docs["story_map"]["events"] = []
    ctx["chapter_ovis"] = [1, 2]
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] in (1, 2):
            c["disposition"] = "VISUALISED"
    for sc in docs["scenes"]["scenes"]:
        sc["ovi_range"] = [1, 2]
    for sh in docs["shots"]["shots"]:
        sh["ovi_ids"] = [1, 2]
    ctx["unfilmed_ovis"] = []
    errs = agg.validate_all(1, docs, ctx)
    assert any("story_map: ovi 1 is typed STORY but is in no story event" in e for e in errs)
    assert any("story_map: ovi 2 is typed TEACHING but is in no discourse event" in e for e in errs)


def test_x3_proposed_not_in_unfilmed():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    ovi = docs["coverage"]["ovis"][0]["ovi"]
    docs["coverage"]["ovis"][0]["disposition"] = "PROPOSE_OMISSION"
    docs["coverage"]["ovis"][0]["reason"] = "test"
    ctx["unfilmed_ovis"] = []
    for c in docs["coverage"]["ovis"][1:]:
        if c["disposition"] == "PROPOSE_OMISSION":
            c["disposition"] = "VISUALISED"
    errs = agg.validate_all(1, docs, ctx)
    assert any(f"coverage: ovi {ovi} omission is not approved by the owner" in e for e in errs)


def test_x3_unfilmed_without_proposal():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    ovi = 999
    ctx["unfilmed_ovis"] = [ovi]
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] == ovi:
            c["disposition"] = "VISUALISED"
    for c in docs["coverage"]["ovis"]:
        if c["disposition"] == "PROPOSE_OMISSION":
            c["disposition"] = "VISUALISED"
    errs = agg.validate_all(1, docs, ctx)
    assert any(f"coverage: ovi {ovi} is approved as unfilmed but has no omission proposal" in e for e in errs)


def test_x4_visualised_not_in_shot():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    ovi = docs["coverage"]["ovis"][0]["ovi"]
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] == ovi:
            c["disposition"] = "VISUALISED"
            break
    for sh in docs["shots"]["shots"]:
        if ovi in sh.get("ovi_ids", []):
            sh["ovi_ids"] = [x for x in sh["ovi_ids"] if x != ovi]
    for sc in docs["scenes"]["scenes"]:
        if sc["ovi_range"][0] <= ovi <= sc["ovi_range"][1]:
            break
    else:
        docs["scenes"]["scenes"][0]["ovi_range"] = [ovi, ovi]
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] != ovi and c["disposition"] == "VISUALISED":
            if ovi not in docs["shots"]["shots"][0]["ovi_ids"]:
                docs["shots"]["shots"][0]["ovi_ids"].append(c["ovi"])
    errs = agg.validate_all(1, docs, ctx)
    assert any(f"coverage: ovi {ovi} is VISUALISED but is in no shot" in e for e in errs)
    docs["shots"]["shots"][0]["ovi_ids"].append(ovi)
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any(f"coverage: ovi {ovi} is VISUALISED but is in no shot" in e for e in errs2)


def test_x4_non_omitted_not_in_scene():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    ovi = docs["coverage"]["ovis"][0]["ovi"]
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] == ovi:
            c["disposition"] = "NARRATED"
            break
    for sc in docs["scenes"]["scenes"]:
        sc["ovi_range"] = [100, 200]
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] == ovi:
            c["disposition"] = "NARRATED"
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] != ovi and c["disposition"] != "PROPOSE_OMISSION":
            docs["scenes"]["scenes"][0]["ovi_range"] = [c["ovi"], c["ovi"]]
    errs = agg.validate_all(1, docs, ctx)
    assert any(f"coverage: ovi {ovi} is in no scene" in e for e in errs)
    docs["scenes"]["scenes"][0]["ovi_range"] = [ovi, ovi]
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any(f"coverage: ovi {ovi} is in no scene" in e for e in errs2)


def test_x5_key_ovi_not_in_scene():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    docs["story_map"]["events"][0]["key_ovis"] = [999]
    for sc in docs["scenes"]["scenes"]:
        sc["ovi_range"] = [1, 10]
    if not any(c["ovi"] == 999 for c in docs["coverage"]["ovis"]):
        docs["coverage"]["ovis"].append({"ovi": 999, "disposition": "NARRATED"})
    else:
        for c in docs["coverage"]["ovis"]:
            if c["ovi"] == 999:
                c["disposition"] = "NARRATED"
    errs = agg.validate_all(1, docs, ctx)
    assert any("story_map: key ovi 999 of event" in e and "is in no scene" in e for e in errs)
    docs["scenes"]["scenes"][0]["ovi_range"] = [999, 999]
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any("story_map: key ovi 999 of event" in e and "is in no scene" in e for e in errs2)


def test_x6_ambiguous_event_no_question():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    for ev in docs["story_map"]["events"]:
        if ev["event_id"] == "E2":
            ev["closure"] = "SOURCE_INCOMPLETE_OR_AMBIGUOUS"
            break
    docs["questions"]["questions"] = [q for q in docs["questions"]["questions"] if q.get("scene_id") != "S2"]
    e2_range = None
    for ev in docs["story_map"]["events"]:
        if ev["event_id"] == "E2":
            e2_range = ev["ovi_range"]
            break
    if e2_range:
        s2_found = False
        for sc in docs["scenes"]["scenes"]:
            if sc.get("scene_id") == "S2":
                s2_found = True
                sc["ovi_range"] = [e2_range[0], e2_range[1]]
                break
        if not s2_found:
            docs["scenes"]["scenes"].append({"scene_id": "S2", "section_kind": "story", "ovi_range": e2_range, "line_ids": []})
    errs = agg.validate_all(1, docs, ctx)
    assert any("story_map: ambiguous event E2 has no question" in e for e in errs)
    docs["questions"]["questions"].append({"id": "Q99", "text": "test", "scene_id": "S2"})
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any("story_map: ambiguous event E2 has no question" in e for e in errs2)


def test_x7_recurring_voice_mismatch():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    ctx["series_voices"] = {"gajanan_maharaj": "other_key"}
    saved = list(ctx.get("saved_voices", []))
    if "different_key" not in saved:
        saved.append("different_key")
    ctx["saved_voices"] = saved
    for cast in docs["voices"]["cast"]:
        if cast["character_id"] == "gajanan_maharaj":
            cast["status"] = "RECURRING"
            cast["voice_key"] = "different_key"
            break
    errs = agg.validate_all(1, docs, ctx)
    assert any("voices: recurring character gajanan_maharaj has a different voice than the series" in e for e in errs)
    for cast in docs["voices"]["cast"]:
        if cast["character_id"] == "gajanan_maharaj":
            cast["voice_key"] = "other_key"
            break
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any("voices: recurring character gajanan_maharaj has a different voice than the series" in e for e in errs2)


def test_x7_new_proposed_for_series_char():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    ctx["series_voices"] = {"gajanan_maharaj": "some_key"}
    saved = list(ctx.get("saved_voices", []))
    if "some_key" not in saved:
        saved.append("some_key")
    ctx["saved_voices"] = saved
    for cast in docs["voices"]["cast"]:
        if cast["character_id"] == "gajanan_maharaj":
            cast["status"] = "NEW_PROPOSED"
            cast["voice_key"] = "some_key"
            cast["reason"] = "new voice for series character"
            break
    errs = agg.validate_all(1, docs, ctx)
    assert any("voices: character gajanan_maharaj already has a series voice" in e for e in errs)
    for cast in docs["voices"]["cast"]:
        if cast["character_id"] == "gajanan_maharaj":
            cast["status"] = "RECURRING"
            cast["voice_key"] = "some_key"
            break
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any("voices: character gajanan_maharaj already has a series voice" in e for e in errs2)


def test_x7_new_proposed_reuses_series_voice():
    """NEW_PROPOSED character (not in series_voices) reuses a voice_key that belongs to a series character."""
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Base fixture: ctx['saved_voices'] is a dict {voice_key: voice_id}
    # Base cast: narrator (RECURRING, key narrator), gajanan_maharaj (RECURRING, key gajanan)
    ctx["series_voices"] = {"gajanan_maharaj": "gajanan"}
    # Add a new saved voice for the new character
    ctx["saved_voices"]["villager"] = "ABCDEFGHIJ"
    # Append a NEW_PROPOSED entry for a character not in series_voices, reusing the series voice 'gajanan'
    new_char = {
        "character_id": "villager",
        "voice_key": "gajanan",
        "voice_id": "8fqGzH80bdkm2UseeV9f",
        "gender": "male",
        "status": "NEW_PROPOSED",
        "reason": "older villager voice chosen from the description"
    }
    docs["voices"]["cast"].append(new_char)
    errs = agg.validate_all(1, docs, ctx)
    assert any("villager" in e and "reuses the series voice" in e for e in errs)
    # Corrected twin: use a different voice_key that matches the new saved_voices entry
    new_char["voice_key"] = "villager"
    new_char["voice_id"] = "ABCDEFGHIJ"
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any("reuses the series voice" in e for e in errs2)


def test_x7_series_voices_bad_types():
    """series_voices with non-str keys/values should be treated as empty, no internal error."""
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    for bad_val in [{"x": []}, {"x": {"a": 1}}, {"x": None}, {1: "k"}, {"a": "b", "c": []}]:
        ctx["series_voices"] = bad_val
        errs = agg.validate_all(1, docs, ctx)
        assert isinstance(errs, list)
        assert not any("internal error in X7" in e for e in errs)


def test_x8_script_text_copied():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # 6-word run from script line
    script_line = "This is a long enough script line for testing purposes"
    ctx["script_texts"] = [script_line]
    # Copy into scenes[0].goal - contains the 6-word run "a long enough script line for"
    docs["scenes"]["scenes"][0]["goal"] = "Here is a long enough script line for the scene"
    errs = agg.validate_all(1, docs, ctx)
    assert any("scenes: free text copies script wording (scenes/0/goal)" in e for e in errs)
    # Five words should not trigger
    docs["scenes"]["scenes"][0]["goal"] = "Here is a long enough"
    ctx["script_texts"] = ["Here is a long enough"]
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any("free text copies script wording" in e for e in errs2)


def test_x8_script_text_copied_other_unit():
    """X8 should run on all 9 documents even if another unit fails schema."""
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    script_line = "This is a long enough script line for testing purposes"
    ctx["script_texts"] = [script_line]
    # Break coverage schema
    docs["coverage"] = {"ovis": "invalid"}
    # Put script text in questions[0].text (a different unit)
    # Ensure there is at least one question
    if not docs["questions"]["questions"]:
        docs["questions"]["questions"].append({"id": "Q1", "text": "", "scene_id": "S1"})
    docs["questions"]["questions"][0]["text"] = "Here is a long enough script line for the question"
    errs = agg.validate_all(1, docs, ctx)
    # Should have schema error for coverage
    assert any("coverage" in e for e in errs)
    # Should still catch X8 in questions
    assert any("questions: free text copies script wording (questions/0/text)" in e for e in errs)


def test_x8_punctuation_normalization():
    """Punctuation should be stripped from both ends of tokens before word matching."""
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    script_line = "This is a long enough script line for testing purposes"
    ctx["script_texts"] = [script_line]
    # With punctuation differences on both sides
    docs["scenes"]["scenes"][0]["goal"] = "Here is a long, enough script; line: for the scene!"
    errs = agg.validate_all(1, docs, ctx)
    assert any("scenes: free text copies script wording (scenes/0/goal)" in e for e in errs)


def test_x8_punctuation_surrounding_quotes():
    """Quotes and brackets around words should be stripped."""
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    script_line = "one two three four five six"
    ctx["script_texts"] = [script_line]
    # With surrounding quotes/brackets
    docs["scenes"]["scenes"][0]["goal"] = '"one two three four five six"'
    errs = agg.validate_all(1, docs, ctx)
    assert any("scenes: free text copies script wording (scenes/0/goal)" in e for e in errs)


def test_x8_five_words_not_trigger():
    """Five word run should not trigger."""
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    script_line = "one two three four five"
    ctx["script_texts"] = [script_line]
    docs["scenes"]["scenes"][0]["goal"] = "one two three four five"
    errs = agg.validate_all(1, docs, ctx)
    assert not any("free text copies script wording" in e for e in errs)


def test_x9_event_range_outside_chapter():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Chapter ovis 1-9, event at 900-905
    ctx["chapter_ovis"] = list(range(1, 10))
    docs["story_map"]["events"][0]["ovi_range"] = [900, 905]
    docs["story_map"]["events"][0]["event_id"] = "E99"
    errs = agg.validate_all(1, docs, ctx)
    assert any("story_map: event E99 range is outside the chapter" in e for e in errs)


def test_x9_key_ovi_outside_chapter():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    ctx["chapter_ovis"] = list(range(1, 10))
    docs["story_map"]["events"][0]["key_ovis"] = [999]
    docs["story_map"]["events"][0]["event_id"] = "E99"
    errs = agg.validate_all(1, docs, ctx)
    assert any("story_map: key ovi 999 of event E99 is outside the chapter" in e for e in errs)


def test_x9_valid_base_clean():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    errs = agg.validate_all(1, docs, ctx)
    assert not any("outside the chapter" in e for e in errs)


def test_x10_scene_kind_mismatch():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Base has S1 as story, E1 as story - should be clean
    errs = agg.validate_all(1, docs, ctx)
    assert not any("scenes: scene" in e and "but its events are not" in e for e in errs)
    # Change E1 kind to discourse, S1 stays story -> error
    for ev in docs["story_map"]["events"]:
        if ev["event_id"] == "E1":
            ev["kind"] = "discourse"
            break
    errs = agg.validate_all(1, docs, ctx)
    assert any("scenes: scene S1 is story but its events are not story" in e for e in errs)
    # Corrected twin: add another event E3 with kind story overlapping S1
    docs["story_map"]["events"].append({"event_id": "E3", "kind": "story", "title": "t3", "ovi_range": [1, 5], "key_ovis": [1], "closure": "RESOLVED_IN_ADHYAY"})
    errs2 = agg.validate_all(1, docs, ctx)
    assert not any("scenes: scene S1 is story but its events are not story" in e for e in errs2)


def test_x10_scene_no_overlapping_event():
    """Scene with no overlapping event should not trigger X10 (X1 already fails story/teaching ovis in no event)."""
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Add a scene with ovi_range that doesn't overlap any event
    docs["scenes"]["scenes"].append({"scene_id": "S99", "section_kind": "story", "ovi_range": [900, 900], "line_ids": []})
    # Ensure coverage has this ovi so X4 doesn't fire
    docs["coverage"]["ovis"].append({"ovi": 900, "disposition": "NARRATED"})
    errs = agg.validate_all(1, docs, ctx)
    assert not any("scenes: scene S99" in e for e in errs)


def test_x11_verified_voices_absent():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # verified_voices absent -> rule skipped
    errs = agg.validate_all(1, docs, ctx)
    assert not any("verified for Marathi and Hindi" in e for e in errs)


def test_x11_verified_voices_all_present():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Collect all voice_keys from base
    voice_keys = [cast["voice_key"] for cast in docs["voices"]["cast"]]
    ctx["verified_voices"] = voice_keys
    errs = agg.validate_all(1, docs, ctx)
    assert not any("verified for Marathi and Hindi" in e for e in errs)


def test_x11_verified_voices_missing():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    voice_keys = [cast["voice_key"] for cast in docs["voices"]["cast"]]
    # Remove one
    ctx["verified_voices"] = voice_keys[:-1]
    missing_key = voice_keys[-1]
    errs = agg.validate_all(1, docs, ctx)
    assert any(f"voices: voice {missing_key} is not verified for Marathi and Hindi" in e for e in errs)


def test_x11_verified_voices_wrong_types():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    for bad_val in [None, 5, "x", [[1]]]:
        ctx["verified_voices"] = bad_val
        errs = agg.validate_all(1, docs, ctx)
        assert isinstance(errs, list)
        assert not any("internal error in X11" in e for e in errs)


def test_propose_omission_story_ovi_no_x2_error():
    """A STORY ovi with PROPOSE_OMISSION that IS in unfilmed_ovis produces NO X2 error (X2 removed) and NO X3 error."""
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    # Find a STORY ovi in base
    story_ovi = None
    for ot in docs["story_map"]["ovi_types"]:
        if ot["type"] == "STORY":
            story_ovi = ot["ovi"]
            break
    assert story_ovi is not None
    # Set coverage to PROPOSE_OMISSION for that ovi
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] == story_ovi:
            c["disposition"] = "PROPOSE_OMISSION"
            c["reason"] = "test"
            break
    # Add to unfilmed so X3 passes
    ctx["unfilmed_ovis"] = [story_ovi]
    # Ensure it's in a scene and shot so X4 doesn't fire
    for sc in docs["scenes"]["scenes"]:
        if sc["ovi_range"][0] <= story_ovi <= sc["ovi_range"][1]:
            break
    else:
        docs["scenes"]["scenes"][0]["ovi_range"] = [story_ovi, story_ovi]
    for sh in docs["shots"]["shots"]:
        if story_ovi in sh.get("ovi_ids", []):
            break
    else:
        docs["shots"]["shots"][0]["ovi_ids"].append(story_ovi)
    # Ensure no other PROPOSE_OMISSION
    for c in docs["coverage"]["ovis"]:
        if c["ovi"] != story_ovi and c["disposition"] == "PROPOSE_OMISSION":
            c["disposition"] = "VISUALISED"
    errs = agg.validate_all(1, docs, ctx)
    # No X2 error (rule removed): no message containing 'omission is proposed'
    assert not any("omission is proposed" in e for e in errs)
    # No X3 error for this ovi
    assert not any(f"coverage: ovi {story_ovi} omission is not approved" in e for e in errs)
    assert not any(f"coverage: ovi {story_ovi} is approved as unfilmed but has no omission proposal" in e for e in errs)


def test_robustness_docs_none():
    errs = agg.validate_all(1, None, {})
    assert any("aggregate: docs must be an object" in e for e in errs)
    assert sum(1 for e in errs if "document missing" in e) == 9


def test_robustness_docs_empty():
    errs = agg.validate_all(1, {}, {})
    assert sum(1 for e in errs if "document missing" in e) == 9


def test_robustness_ctx_none():
    docs = copy.deepcopy(BASE_DOCS)
    errs = agg.validate_all(1, docs, None)
    assert any("aggregate: ctx must be an object" in e for e in errs)
    assert not any("internal error" in e for e in errs)


def test_robustness_doc_is_list():
    docs = copy.deepcopy(BASE_DOCS)
    docs["story_map"] = []
    errs = agg.validate_all(1, docs, {})
    assert any("story_map: document missing" in e for e in errs)
    assert not any("internal error" in e for e in errs)


def test_robustness_schema_failure_skips_validate_and_cross():
    docs = copy.deepcopy(BASE_DOCS)
    docs["coverage"] = {"ovis": "invalid"}
    errs = agg.validate_all(1, docs, {})
    cov_module = agg._load_unit("coverage")
    schema_errs = cov_module.schema_errors(docs["coverage"]) if cov_module else []
    assert schema_errs, "coverage schema should produce errors for invalid ovis"
    assert any(any(se in e for e in errs) for se in schema_errs)
    assert not any("internal error in coverage.validate" in e for e in errs)
    assert not any("coverage: ovi" in e and ("omission" in e or "VISUALISED" in e or "in no scene" in e) for e in errs)


def test_robustness_huge_ranges():
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    for i, sc in enumerate(docs["scenes"]["scenes"]):
        start = 1 + i * 10**12
        end = start + 10**12 - 1
        sc["ovi_range"] = [start, end]
    for i, ev in enumerate(docs["story_map"]["events"]):
        start = 1 + i * 10**12
        end = start + 10**12 - 1
        ev["ovi_range"] = [start, end]
    errs = agg.validate_all(1, docs, ctx)
    assert isinstance(errs, list)


def test_robustness_ctx_unfilmed_ovis_bad_types():
    """ctx.unfilmed_ovis with bad types should not raise, just be treated as empty."""
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    for bad_val in [None, 5, "x", [[1]], [1, {}], [1, 2, "three"], [True, False]]:
        ctx["unfilmed_ovis"] = bad_val
        errs = agg.validate_all(1, docs, ctx)
        assert isinstance(errs, list)
        assert not any("internal error in X3" in e for e in errs)


def test_robustness_ctx_series_voices_bad_types():
    """ctx.series_voices with bad types should not raise, just be treated as empty."""
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    for bad_val in [None, 5, "x", ["a", "b"], [{"a": 1}]]:
        ctx["series_voices"] = bad_val
        errs = agg.validate_all(1, docs, ctx)
        assert isinstance(errs, list)
        assert not any("internal error in X7" in e for e in errs)


def test_robustness_ctx_script_texts_bad_types():
    """ctx.script_texts with bad types should not raise, just be treated as empty."""
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    for bad_val in [None, 5, "x", [1, 2], [{"a": 1}]]:
        ctx["script_texts"] = bad_val
        errs = agg.validate_all(1, docs, ctx)
        assert isinstance(errs, list)
        assert not any("internal error in X8" in e for e in errs)


def test_robustness_ctx_chapter_ovis_bad_types():
    """ctx.chapter_ovis with bad types should not raise, just be treated as empty."""
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    for bad_val in [None, 5, "x", [[1]], [1, {}], [1, 2, "three"], [True, False]]:
        ctx["chapter_ovis"] = bad_val
        errs = agg.validate_all(1, docs, ctx)
        assert isinstance(errs, list)
        assert not any("internal error in X9" in e for e in errs)


def test_robustness_ctx_verified_voices_bad_types():
    """ctx.verified_voices with bad types should not raise, just be treated as absent (rule skipped)."""
    docs = copy.deepcopy(BASE_DOCS)
    ctx = copy.deepcopy(BASE_CTX)
    for bad_val in [None, 5, "x", [[1]], [1, {}], [1, 2, "three"], [True, False]]:
        ctx["verified_voices"] = bad_val
        errs = agg.validate_all(1, docs, ctx)
        assert isinstance(errs, list)
        assert not any("internal error in X11" in e for e in errs)


def test_export_schemas(tmp_path):
    out_dir = tmp_path / "schemas"
    paths = agg.export_schemas(out_dir)
    assert len(paths) == 9
    for p in paths:
        assert p.exists()
        content = p.read_text(encoding="utf-8")
        assert content.endswith("\n")
        json.loads(content)
    try:
        agg.export_schemas(out_dir)
        assert False, "expected FileExistsError"
    except FileExistsError:
        pass
    for p in paths:
        assert p.exists()


def test_main_exit_codes(tmp_path, capsys):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    for unit in agg.UNITS:
        (docs_dir / f"{unit}.json").write_text(json.dumps(BASE_DOCS[unit]), encoding="utf-8")
    ctx_file = tmp_path / "ctx.json"
    ctx_file.write_text(json.dumps(BASE_CTX), encoding="utf-8")

    # Valid docs, export schemas -> should validate and return 0
    schema_dir = tmp_path / "schemas"
    rc = agg.main(["--adhyay", "1", "--docs-dir", str(docs_dir), "--ctx", str(ctx_file), "--export-schemas", str(schema_dir)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "0 error(s)" in out
    # Schemas should be written
    assert (schema_dir / "stage1_story_map.schema.json").exists()

    # Valid docs, export schemas to existing dir -> refused
    rc = agg.main(["--adhyay", "1", "--docs-dir", str(docs_dir), "--ctx", str(ctx_file), "--export-schemas", str(schema_dir)])
    assert rc == 2
    out = capsys.readouterr().out
    assert "refused:" in out

    # Invalid docs, export schemas -> should validate and return 1
    bad_docs = copy.deepcopy(BASE_DOCS)
    bad_docs["story_map"]["ovi_types"] = [{"ovi": 999, "type": "STORY"}]
    bad_docs["story_map"]["events"] = []
    (docs_dir / "story_map.json").write_text(json.dumps(bad_docs["story_map"]), encoding="utf-8")
    schema_dir2 = tmp_path / "schemas2"
    rc = agg.main(["--adhyay", "1", "--docs-dir", str(docs_dir), "--ctx", str(ctx_file), "--export-schemas", str(schema_dir2)])
    assert rc == 1
    out = capsys.readouterr().out
    assert "error(s)" in out
    # Schemas should still be written
    assert (schema_dir2 / "stage1_story_map.schema.json").exists()

    # Unreadable JSON -> refused (exit 2)
    (docs_dir / "coverage.json").write_text("not json", encoding="utf-8")
    rc = agg.main(["--adhyay", "1", "--docs-dir", str(docs_dir), "--ctx", str(ctx_file)])
    assert rc == 2
    out = capsys.readouterr().out
    assert "refused:" in out
