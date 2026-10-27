import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("chapter", ROOT / "scripts" / "pipeline" / "chapter.py")
ch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ch)

KEYS = {"base", "source_ovis", "research_packet", "script", "bible", "stage1_dir", "audio_plan", "timing_plan", "measured", "images_catalog",
        "image_binding", "flow_jobs", "approvals", "caps", "spend", "shot_plans_dir", "images_dir"}


def test_standard_layout_for_a_new_chapter(tmp_path):
    p = ch.chapter_paths(2, tmp_path, flow_root=tmp_path / "flow")
    assert set(p) == KEYS
    base = tmp_path / "canon" / "adhyay_02"
    assert p["base"] == base and p["script"] == base / "script" / "easy.md" and p["audio_plan"] == base / "audio" / "plan.json"
    assert p["approvals"] == base / "approvals.json" and p["caps"] == base / "caps.json" and p["spend"] == base / "spend.jsonl"
    assert p["shot_plans_dir"] == tmp_path / "canon" / "shot_plans" / "A2" and p["images_dir"] == tmp_path / "flow" / "adhyay_02"
    assert p["source_ovis"] == base / "source" / "ovis.jsonl" and p["images_catalog"] == base / "images" / "catalog.json"


def test_two_digit_chapters_and_bad_numbers(tmp_path):
    assert ch.chapter_paths(12, tmp_path)["base"].name == "adhyay_12"
    for bad in (0, 22, -1, "1", 1.5, True, None):
        with pytest.raises(ValueError):
            ch.chapter_paths(bad, tmp_path)


def test_adhyay_1_keeps_its_existing_paths_and_they_exist():
    p = ch.chapter_paths(1, ROOT)
    assert set(p) == KEYS
    assert p["script"] == ROOT / "docs" / "pilot" / "A1_full_script_simple.md"
    assert p["audio_plan"] == ROOT / "canon" / "audio" / "A1_audio_plan.json"
    assert p["timing_plan"] == ROOT / "canon" / "audio" / "A1_timing_plan.json"
    assert p["measured"] == ROOT / "canon" / "audio" / "A1_eleven_measured.json"
    assert p["image_binding"] == ROOT / "canon" / "packets" / "adhyay_01" / "final_image_binding.json"
    assert p["flow_jobs"] == ROOT / "canon" / "drafts" / "A1_flow_shot_jobs.json"
    assert p["images_catalog"] == p["image_binding"]
    for k in ("script", "audio_plan", "timing_plan", "measured", "image_binding", "flow_jobs", "images_catalog"):
        assert p[k].exists(), k


def test_paths_are_pure_nothing_is_created(tmp_path):
    ch.chapter_paths(3, tmp_path)
    assert list(tmp_path.iterdir()) == []
