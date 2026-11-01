"""Owner 2026-11-01 'add new shots': the S2/S7 slot order fits the re-timed plan, reuses every existing image once, and adds only the proposed new ids."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NEW = ROOT / "docs" / "pilot" / "A1_NEW_SHOTS_S2_S7.json"
pytestmark = pytest.mark.skipif(not NEW.is_file(), reason="new-shot proposal not present")


def test_slot_order_matches_the_retimed_scenes_and_reuses_every_image_once():
    new = json.loads(NEW.read_text(encoding="utf-8"))
    timing = {s["scene"]: s for s in json.loads((ROOT / "canon" / "audio" / "A1_timing_plan.json").read_text(encoding="utf-8"))["scenes"]}
    bound = json.loads((ROOT / "canon" / "packets" / "adhyay_01" / "final_image_binding.json").read_text(encoding="utf-8"))["images"]
    new_ids = {j["shot_id"] for j in new["jobs"]}
    for scene, order in new["slot_order"].items():
        assert len(order) == timing[scene]["planned_shots"]
        existing = sorted(i for i in bound if i.startswith(f"SH_{scene}_"))
        assert sorted(i for i in order if i not in new_ids) == existing, "every existing image once, none dropped"
        assert len(order) == len(set(order))
    assert not new_ids & set(bound), "new shots never reuse an existing id"


def test_new_jobs_attach_only_the_people_they_name_and_keep_the_shared_rules():
    for j in json.loads(NEW.read_text(encoding="utf-8"))["jobs"]:
        head = j["prompt"][: j["prompt"].find("Setting:")]
        assert [x for x in j["characters"] if x in head] == j["characters"] and head.count("_v01") == len(j["characters"])
        assert j["prompt"].endswith("No text, no letters, no modern objects, no halo.") and "PROPOSED" in j["status"]
