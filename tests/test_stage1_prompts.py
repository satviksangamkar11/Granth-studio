import importlib.util
import json
import tempfile
from pathlib import Path

import pytest

# Load the prompts module by path
PROMPTS_PATH = Path(__file__).resolve().parents[1] / "scripts" / "pipeline" / "stage1" / "prompts.py"
spec = importlib.util.spec_from_file_location("prompts", PROMPTS_PATH)
prompts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prompts)


def _write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def _write_jsonl(path: Path, lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for obj in lines:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def _make_synthetic_root(tmp: Path) -> Path:
    root = tmp / "repo"
    # adhyay 2
    adhyay_dir = root / "canon" / "adhyay_02"
    # ovis
    ovis = [
        {"ovi": 1, "original_marathi": "om1", "simple_marathi": "sm1", "hindi": "h1", "easy_english": "ee1", "section": "sec1"},
        {"ovi": 2, "original_marathi": "om2", "simple_marathi": "sm2", "hindi": "h2", "easy_english": "ee2", "section": "sec1"},
        {"ovi": 3, "original_marathi": "om3", "simple_marathi": "sm3", "hindi": "h3", "easy_english": "ee3", "section": "sec2"},
        {"ovi": 4, "original_marathi": "om4", "simple_marathi": "sm4", "hindi": "h4", "easy_english": "ee4", "section": "sec2"},
    ]
    _write_jsonl(adhyay_dir / "source" / "ovis.jsonl", ovis)
    # script (REAL EASY format)
    script_md = (
        "# Adhyay 2\n\n"
        "## S1\n\n"
        "**S1-L1** | narrator | ovi 1 | core\n"
        "- Marathi: mar1\n"
        "- Hindi: hin1\n\n"
        "**S1-L2** | narrator | ovi 2 | core\n"
        "- Marathi: mar2\n"
        "- Hindi: hin2\n\n"
        "## S2\n\n"
        "**S2-L1** | narrator | ovi 3 | core\n"
        "- Marathi: mar3\n"
        "- Hindi: hin3\n"
    )
    (adhyay_dir / "script").mkdir(parents=True, exist_ok=True)
    (adhyay_dir / "script" / "easy.md").write_text(script_md, encoding="utf-8")
    # presets
    presets = [
        {"preset": "p1", "use": "bg", "assets": ["a1"], "simplest_renderer": "flat"},
        {"preset": "p2", "use": "char", "assets": ["a2"], "simplest_renderer": "flat"},
    ]
    _write_json(root / "assets" / "v5_presets" / "index.json", presets)
    # voices
    voices = {
        "voices": [
            {"voice_key": "v1", "voice_id": "id1", "name": "N1", "gender": "M", "age": "30", "accent": "Indian", "description": "desc1", "owner_note": "", "marathi_verified": True, "hindi_verified": True, "assigned_to": "char1", "status": "active"},
            {"voice_key": "v2", "voice_id": "id2", "name": "N2", "gender": "F", "age": "25", "accent": "Indian", "description": "desc2", "owner_note": "", "marathi_verified": True, "hindi_verified": True, "assigned_to": "char2", "status": "active"},
            {"voice_key": "v3", "voice_id": "id3", "name": "N3", "gender": "M", "age": "40", "accent": "Indian", "description": "desc3", "owner_note": "", "marathi_verified": False, "hindi_verified": False, "assigned_to": "", "status": "available"},
        ]
    }
    _write_json(root / "canon" / "series" / "voices.json", voices)
    # no sound palette
    return root


def _make_full_prior(adhyay: int) -> dict:
    """Return a prior dict with full document shapes."""
    return {
        "story_map": {"adhyay": adhyay, "ovi_types": [], "events": []},
        "coverage": {"adhyay": adhyay, "ovis": []},
        "scenes": {"adhyay": adhyay, "scenes": [{"scene_id": "S1"}, {"scene_id": "S2"}]},
    }


def _extract_chapter_data(usr: str) -> dict:
    """Extract the JSON from the CHAPTER DATA section of the user prompt."""
    marker = "CHAPTER DATA\n"
    idx = usr.find(marker)
    if idx == -1:
        return {}
    json_str = usr[idx + len(marker):]
    # The JSON is compact (no newlines) and ends before the next section (double newline)
    end = json_str.find("\n\n")
    if end != -1:
        json_str = json_str[:end]
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return {}


def test_build_packet_synthetic():
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_synthetic_root(Path(tmp))
        packet, problems = prompts.build_packet(2, root)
        assert problems == []
        assert packet["adhyay"] == 2
        assert len(packet["ovis"]) == 4
        assert packet["ovis"][0]["ovi"] == 1
        assert packet["ovis"][-1]["ovi"] == 4
        assert "original_marathi" in packet["ovis"][0]
        assert packet["research"] == {}
        assert len(packet["script"]) == 3
        assert packet["script"][0]["id"] == "S1-L1"
        assert packet["script"][1]["id"] == "S1-L2"
        assert packet["script"][2]["id"] == "S2-L1"
        assert len(packet["presets"]) == 2
        assert packet["presets"][0]["preset"] == "p1"
        assert packet["presets"][1]["preset"] == "p2"
        assert packet["sounds"] == []
        assert len(packet["voices"]) == 3
        assert packet["voices"][0]["description"] == "desc1"


def test_build_packet_missing_files():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "repo"
        root.mkdir()
        # No files at all
        packet, problems = prompts.build_packet(2, root)
        assert "ovis: missing" in problems
        assert "script: missing" in problems
        assert "presets: missing" in problems
        assert "voice_library: missing" in problems
        # research and sounds should not produce missing problems
        assert not any("research: missing" in p for p in problems)
        assert not any("sounds: missing" in p for p in problems)
        assert packet["ovis"] == []
        assert packet["script"] == []
        assert packet["presets"] == []
        assert packet["voices"] == []


def test_build_packet_invalid_adhyay():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        packet, problems = prompts.build_packet(0, root)
        assert packet == {}
        assert problems == ["adhyay must be an int in 1..21"]
        packet, problems = prompts.build_packet(22, root)
        assert packet == {}
        assert problems == ["adhyay must be an int in 1..21"]


def test_build_packet_bad_shapes():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "repo"
        root.mkdir()
        adhyay_dir = root / "canon" / "adhyay_02"
        adhyay_dir.mkdir(parents=True)
        # bad ovis jsonl
        (adhyay_dir / "source").mkdir()
        (adhyay_dir / "source" / "ovis.jsonl").write_text("not json\n", encoding="utf-8")
        # bad script (will be handled by parse_script, but we can't control that; we just test our wrapper)
        (adhyay_dir / "script").mkdir()
        (adhyay_dir / "script" / "easy.md").write_text("", encoding="utf-8")
        # bad presets
        (root / "assets" / "v5_presets").mkdir(parents=True)
        _write_json(root / "assets" / "v5_presets" / "index.json", "not a list")
        # bad voices
        (root / "canon" / "series").mkdir(parents=True)
        _write_json(root / "canon" / "series" / "voices.json", "not a dict")
        # bad sounds
        (root / "canon" / "series" / "sounds").mkdir(parents=True)
        _write_json(root / "canon" / "series" / "sounds" / "palette.json", 5)

        # Test multiple bad research shapes at the correct path: canon/adhyay_02/research/packet.json
        research_dir = adhyay_dir / "research"
        research_dir.mkdir(parents=True)
        bad_shapes = ["not a dict", [], 5, None]
        for bad in bad_shapes:
            research_file = research_dir / "packet.json"
            _write_json(research_file, bad)
            packet, problems = prompts.build_packet(2, root)
            assert any("ovis: bad line" in p for p in problems)
            assert any("research: bad shape" in p for p in problems)
            assert any("presets: bad shape" in p for p in problems)
            assert any("voice_library: bad shape" in p for p in problems)
            assert any("sounds: bad shape" in p for p in problems)
            assert packet["sounds"] == []


def test_build_packet_adhyay1_uses_the_docx_layout():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "repo"
        root.mkdir()
        # Adhyay 1 now uses the same docx-imported layout as Adhyay 2+ (owner 2026-11-01)
        base = root / "canon" / "adhyay_01"
        (base / "source").mkdir(parents=True)
        ovis = [{"adhyay": 1, "ovi": 1, "section": 1, "original_marathi": "mar", "simple_marathi": "smar",
                 "hindi": "hin", "easy_english": "eng", "printed_number": 1}]
        _write_jsonl(base / "source" / "ovis.jsonl", ovis)
        (base / "research").mkdir(parents=True)
        _write_json(base / "research" / "packet.json", {"adhyay": 1, "characters": [{"name": "C"}], "locations": [], "objects": []})
        (base / "script").mkdir(parents=True)
        script_md = (
            "## S1\n\n"
            "**S1-L1** | narrator | ovi 1 | core\n"
            "- Marathi: mar1\n"
            "- Hindi: hin1\n"
        )
        (base / "script" / "easy.md").write_text(script_md, encoding="utf-8")
        # presets
        (root / "assets" / "v5_presets").mkdir(parents=True)
        _write_json(root / "assets" / "v5_presets" / "index.json", [])
        # voices
        (root / "canon" / "series").mkdir(parents=True)
        _write_json(root / "canon" / "series" / "voices.json", {"voices": []})
        # sounds
        (root / "canon" / "series" / "sounds").mkdir(parents=True)
        _write_json(root / "canon" / "series" / "sounds" / "palette.json", {"sounds": []})

        packet, problems = prompts.build_packet(1, root)
        assert problems == []
        assert packet["ovis"][0]["original_marathi"] == "mar"
        assert packet["research"]["characters"] == [{"name": "C"}]
        assert len(packet["script"]) == 1
        assert packet["script"][0]["id"] == "S1-L1"


def test_shared_rule_block_and_output_keys():
    assert prompts.SHARED_RULE_BLOCK == (
        "Use only locked source, research and owner decisions. Cite chapter-qualified ovis for facts. "
        "Reuse registered IDs; report missing identities. Never invent events, motives, miracles, dialogue or closure. "
        "Reference immutable EASY line IDs; never write, edit, translate or critique their wording. "
        "Thoughts and unclear speech remain narrator material. "
        "Separate sourced facts from STAGING and inferred visual looks. "
        "Preserve required teachings and explicit coverage; only the owner approves omissions. "
        "Use supplied preset capabilities and sound availability; report NEED_NEW honestly. "
        "Output only this call's schema. No timings, hashes, approvals, API calls or code."
    )
    for call in prompts.CALLS:
        if call == "scene":
            sys, usr = prompts.build_prompt(call, {"adhyay": 1, "ovis": [], "research": {}, "script": [], "presets": [], "sounds": [], "voices": []}, scene_ids=["S1"], prior=_make_full_prior(1))
        elif call == "plan":
            sys, usr = prompts.build_prompt(call, {"adhyay": 1, "ovis": [], "research": {}, "script": [], "presets": [], "sounds": [], "voices": []}, prior=_make_full_prior(1))
        else:
            sys, usr = prompts.build_prompt(call, {"adhyay": 1, "ovis": [], "research": {}, "script": [], "presets": [], "sounds": [], "voices": []})
        assert prompts.SHARED_RULE_BLOCK in sys
        for key in prompts.OUTPUT_KEYS[call]:
            assert key in sys


def test_user_prompt_structure_and_schemas():
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_synthetic_root(Path(tmp))
        packet, _ = prompts.build_packet(2, root)
        # Load unit schemas to compare
        story_map_schema = prompts._get_unit_schema("story_map")
        coverage_schema = prompts._get_unit_schema("coverage")
        scenes_schema = prompts._get_unit_schema("scenes")
        shots_schema = prompts._get_unit_schema("shots")
        briefs_schema = prompts._get_unit_schema("briefs")
        looks_schema = prompts._get_unit_schema("looks")
        voices_schema = prompts._get_unit_schema("voices")
        sounds_schema = prompts._get_unit_schema("sounds")
        questions_schema = prompts._get_unit_schema("questions")

        # map
        sys, usr = prompts.build_prompt("map", packet)
        assert "TASK" in usr
        assert "OUTPUT SCHEMAS" in usr
        assert "CHAPTER DATA" in usr
        assert "MUST NOT" in usr
        # check schemas present
        assert json.dumps(story_map_schema, ensure_ascii=False, sort_keys=True, indent=1) in usr
        # ensure other schemas not present
        assert json.dumps(coverage_schema, ensure_ascii=False, sort_keys=True, indent=1) not in usr

        # plan
        prior = _make_full_prior(2)
        sys, usr = prompts.build_prompt("plan", packet, prior=prior)
        assert json.dumps(coverage_schema, ensure_ascii=False, sort_keys=True, indent=1) in usr
        assert json.dumps(scenes_schema, ensure_ascii=False, sort_keys=True, indent=1) in usr
        assert json.dumps(story_map_schema, ensure_ascii=False, sort_keys=True, indent=1) not in usr

        # scene
        prior = _make_full_prior(2)
        sys, usr = prompts.build_prompt("scene", packet, scene_ids=["S1"], prior=prior)
        for schema in (shots_schema, briefs_schema, looks_schema, voices_schema, sounds_schema, questions_schema):
            assert json.dumps(schema, ensure_ascii=False, sort_keys=True, indent=1) in usr
        assert json.dumps(coverage_schema, ensure_ascii=False, sort_keys=True, indent=1) not in usr

        # headings order
        headings = ["TASK", "OUTPUT SCHEMAS", "CHAPTER DATA", "MUST NOT"]
        idx = [usr.find(h) for h in headings]
        assert all(i != -1 for i in idx)
        assert idx == sorted(idx)


def test_scene_call_filters_data():
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_synthetic_root(Path(tmp))
        packet, _ = prompts.build_packet(2, root)
        prior = _make_full_prior(2)
        sys, usr = prompts.build_prompt("scene", packet, scene_ids=["S1"], prior=prior)
        # Extract chapter data JSON
        data = _extract_chapter_data(usr)
        # Only S1 lines should appear
        script_lines = data.get("script_lines", [])
        line_ids = [ln.get("id") for ln in script_lines]
        assert "S1-L1" in line_ids
        assert "S1-L2" in line_ids
        assert "S2-L1" not in line_ids
        # Only ovis 1,2
        ovis = data.get("ovis", [])
        ovi_nums = [ov.get("ovi") for ov in ovis]
        assert 1 in ovi_nums
        assert 2 in ovi_nums
        assert 3 not in ovi_nums
        # All preset ids
        presets = data.get("presets", [])
        preset_ids = [p.get("preset") for p in presets]
        assert "p1" in preset_ids
        assert "p2" in preset_ids
        # All voice descriptions
        voices = data.get("voice_library", [])
        descriptions = [v.get("description") for v in voices]
        assert "desc1" in descriptions
        assert "desc2" in descriptions
        assert "desc3" in descriptions
        # Empty palette sentence
        assert data.get("sound_palette_note") == "The sound palette is empty: every sound is NEED_NEW."
        # Image-brief lessons key phrases (check in the whole user prompt)
        assert "flat-colour" in usr
        assert "full chapter-state identity" in usr
        assert "exactly the visible people" in usr
        assert "ONE action and gaze target" in usr
        assert "critical prop" in usr
        assert "framing, angle, screen directions" in usr
        assert "preset slot" in usr
        assert "approved light" in usr
        assert "ONLY on-screen facts" in usr
        assert "exclude extra people" in usr
        assert "references are the visible characters" in usr
        # Prior documents appear
        prior_data = data.get("PRIOR", {})
        assert "story_map_events" in prior_data
        assert "coverage" in prior_data
        assert "scene_cards" in prior_data
        # The selected scene card should be present
        scene_cards = prior_data.get("scene_cards", [])
        assert any(sc.get("scene_id") == "S1" for sc in scene_cards)
        assert not any(sc.get("scene_id") == "S2" for sc in scene_cards)


def test_scene_call_with_sounds():
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_synthetic_root(Path(tmp))
        # Add a sound palette
        _write_json(root / "canon" / "series" / "sounds" / "palette.json", {"sounds": [{"id": "snd1", "desc": "wind"}]})
        packet, _ = prompts.build_packet(2, root)
        prior = _make_full_prior(2)
        sys, usr = prompts.build_prompt("scene", packet, scene_ids=["S1"], prior=prior)
        data = _extract_chapter_data(usr)
        sounds = data.get("sound_palette", [])
        sound_ids = [s.get("id") for s in sounds]
        assert "snd1" in sound_ids
        assert data.get("sound_palette_note") is None


def test_map_and_plan_content():
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_synthetic_root(Path(tmp))
        packet, _ = prompts.build_packet(2, root)
        # map
        sys, usr = prompts.build_prompt("map", packet)
        data = _extract_chapter_data(usr)
        ovis = data.get("ovis", [])
        ovi_nums = [ov.get("ovi") for ov in ovis]
        assert 1 in ovi_nums
        assert "research" in data
        # plan
        prior = _make_full_prior(2)
        prior["story_map"]["events"] = [{"event_id": "E1", "ovi_range": [1, 2]}]
        sys, usr = prompts.build_prompt("plan", packet, prior=prior)
        data = _extract_chapter_data(usr)
        script_lines = data.get("script", [])
        line_ids = [ln.get("id") for ln in script_lines]
        assert "S1-L1" in line_ids
        assert "S1-L2" in line_ids
        assert "S2-L1" in line_ids
        prior_map = data.get("PRIOR", {})
        assert prior_map.get("events", [])[0].get("event_id") == "E1"


def test_errors():
    packet = {"adhyay": 1, "ovis": [], "research": {}, "script": [], "presets": [], "sounds": [], "voices": []}
    with pytest.raises(ValueError):
        prompts.build_prompt("unknown", packet)
    with pytest.raises(ValueError):
        prompts.build_prompt("scene", packet)  # no scene_ids
    with pytest.raises(ValueError):
        prompts.build_prompt("plan", packet)  # no prior
    with pytest.raises(ValueError):
        prompts.build_prompt("scene", packet, scene_ids=["S1"])  # no prior


def test_no_secrets_or_chapter_specific():
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_synthetic_root(Path(tmp))
        packet, _ = prompts.build_packet(2, root)
        for call in prompts.CALLS:
            if call == "scene":
                sys, usr = prompts.build_prompt(call, packet, scene_ids=["S1"], prior=_make_full_prior(2))
            elif call == "plan":
                sys, usr = prompts.build_prompt(call, packet, prior=_make_full_prior(2))
            else:
                sys, usr = prompts.build_prompt(call, packet)
            assert "nvapi-" not in sys and "nvapi-" not in usr
            assert "sk-" not in sys and "sk-" not in usr
            assert "secrets" not in sys and "secrets" not in usr
    # Check module source for forbidden literals
    source = PROMPTS_PATH.read_text(encoding="utf-8")
    assert "Gajanan" not in source
    assert "Bankatlal" not in source
    assert "adhyay_02" not in source


def test_scene_call_with_full_prior_documents():
    """Test that scene call works with full prior documents and includes the selected scene card."""
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_synthetic_root(Path(tmp))
        packet, _ = prompts.build_packet(2, root)
        prior = _make_full_prior(2)
        # Add a scene card with some content
        prior["scenes"]["scenes"] = [
            {"scene_id": "S1", "section_kind": "story", "ovi_range": [1, 2], "goal": "Introduce characters"},
            {"scene_id": "S2", "section_kind": "discourse", "ovi_range": [3, 3], "goal": "Teaching"},
        ]
        sys, usr = prompts.build_prompt("scene", packet, scene_ids=["S1"], prior=prior)
        # Should not raise
        assert sys and usr
        data = _extract_chapter_data(usr)
        prior_data = data.get("PRIOR", {})
        scene_cards = prior_data.get("scene_cards", [])
        assert len(scene_cards) == 1
        assert scene_cards[0]["scene_id"] == "S1"
        assert scene_cards[0]["goal"] == "Introduce characters"


@pytest.mark.skipif(
    not (Path(__file__).resolve().parents[1] / "canon" / "adhyay_01" / "source" / "ovis.jsonl").exists()
    or not (Path(__file__).resolve().parents[1] / "canon" / "adhyay_01" / "script" / "easy.md").exists()
    or not (Path(__file__).resolve().parents[1] / "assets" / "v5_presets" / "index.json").exists()
    or not (Path(__file__).resolve().parents[1] / "canon" / "series" / "voices.json").exists(),
    reason="Real repo not present"
)
def test_real_repo():
    ROOT = Path(__file__).resolve().parents[1]
    packet, problems = prompts.build_packet(1, ROOT)
    assert problems == []
    assert len(packet["ovis"]) == 146
    assert len(packet["research"]["characters"]) == 8
    assert len(packet["script"]) == 61
    assert len(packet["presets"]) == 17
    assert len(packet["voices"]) == 35
    sys, usr = prompts.build_prompt("map", packet)
    assert sys and usr
    assert prompts.estimate_tokens(usr) > 0
