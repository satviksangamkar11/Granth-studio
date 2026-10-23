"""The provisional 45-second pilot project definition compiles through the existing gates (research -> canon -> manifest -> timelines -> task plan). Nothing is executed and no model runs."""
from __future__ import annotations

import importlib.util
import sys

import pytest

from granthstudio import keyframes as kf
from granthstudio.config import load_models, load_project, load_yaml
from granthstudio.errors import GateFailure
from granthstudio.pipeline import episode_store, load_bundle, plan_tasks
from granthstudio.research import approve
from granthstudio.scheduler import Scheduler
from tests.conftest import FIXED_TIME, REPO, _dump

spec = importlib.util.spec_from_file_location("build_pilot_project", REPO / "scripts" / "pilot" / "build_pilot_project.py")
bp = importlib.util.module_from_spec(spec); sys.modules["build_pilot_project"] = bp; spec.loader.exec_module(bp)


@pytest.fixture
def pilot(tmp_path):
    root = bp.build(tmp_path / "pilot")
    return load_project(root)


def review_hindi_synthetically(project):
    """What the named human reviewer's sign-off would add; here a synthetic reviewer so the compiler can be exercised."""
    path = project.episodes_dir / "adhyay_01" / "hi.yaml"
    document = load_yaml(path)
    for entry in document["entries"]:
        entry["alignment"]["reviewed"] = True
    _dump(path, document)


def test_hindi_review_is_a_real_gate_the_shipped_pilot_files_do_not_pass(pilot):
    approve(pilot, 1, "synthetic-tester", FIXED_TIME)
    with pytest.raises(GateFailure, match="Hindi semantic review is not approved"):
        load_bundle(pilot, load_models(pilot), 1)


def test_the_pilot_compiles_with_three_scenes_nine_shots_and_the_narrator_never_drawn(pilot):
    review_hindi_synthetically(pilot)
    approve(pilot, 1, "synthetic-tester", FIXED_TIME)
    bundle = load_bundle(pilot, load_models(pilot), 1)
    shots = bundle.compiled["shots"]
    assert [s["scene_id"] for s in shots] == ["a01_s01"] * 3 + ["a01_s02"] * 3 + ["a01_s03"] * 3
    assert [s["tier"] for s in shots] == [0, 1, 0] * 3
    assert all("chr_narrator" not in s["characters"] and s["lighting"] == "day_outdoor" for s in shots)
    assert [d for s in shots for d in s["dialogue_ids"]] == [f"d_000{i}" for i in range(1, 7)]
    planned = sum(s["duration_s"] for s in shots)
    assert 40 <= planned <= 55                                                                    # the planned holds; the audio decides the real length
    marathi = {e["dialogue_id"]: e["text"] for e in load_yaml(pilot.episodes_dir / "adhyay_01" / "mr.yaml")["entries"]}
    assert marathi == {d: bp.OVI[o][1] for d, o, _, _ in bp.LINES}                                  # the timeline is the transcription, verbatim
    assert "provisional" in " ".join(load_yaml(pilot.canon_dir / "characters.yaml")["entries"][0]["evidence"]).lower()


def test_every_required_action_has_a_source_reference_and_a_shot(pilot):
    research = load_yaml(pilot.research_dir / "adhyay_01" / "research.yaml")
    assert research["open_questions"] == []
    for scene in research["scenes"]:
        for fact in [*scene["actions"], *scene["visual_details"]]:
            assert fact["artistic"] or all(r.startswith("Adhyay 1 ovi ") for r in fact["source_refs"]) and fact["source_refs"]
    manifest = load_yaml(pilot.episodes_dir / "adhyay_01" / "manifest.yaml")
    used = {a for sc in manifest["scenes"] for sh in sc["shots"] for a in sh["action_ids"]}
    assert used == {a["id"] for sc in research["scenes"] for a in sc["actions"]}


def test_the_task_plan_has_native_keyframes_three_ltx_shots_and_both_languages_and_keyframe_prompts_use_style_v1(pilot):
    review_hindi_synthetically(pilot)
    approve(pilot, 1, "synthetic-tester", FIXED_TIME)
    models = load_models(pilot)
    bundle = load_bundle(pilot, models, 1)
    tasks = plan_tasks(bundle, Scheduler(episode_store(pilot, 1)))
    stages = [t.stage for t in tasks]
    assert stages.count("keyframe") == 3 and stages.count("tier1") == 3 and stages.count("tier0") == 6 and stages.count("audio") == 2 and stages.count("assembly") == 2
    assert bundle.style["style_id"] == "devotional_gouache_1950s_v1"
    registry = kf.load_registry(pilot, bundle.canon)
    request = kf.keyframe_request(bundle.compiled, bundle.canon, registry, models, "vis_s2_kf")
    assert request["style"]["style_id"] == "devotional_gouache_1950s_v1" and "Narrator" not in request["prompt"]
    assert "Bankatlal Agarwal" in request["prompt"] and "Damodarpant Kulkarni" in request["prompt"] and request["prompt"].startswith("1950s vintage Indian devotional book illustration")
    assert {t.stage for t in tasks if t.name.startswith("sheet_")} == set()                       # reference sheets are a separate task list


def test_the_committed_pilot_files_are_what_the_generator_produces_and_carry_the_one_frozen_style_unchanged(tmp_path):
    fresh = bp.build(tmp_path / "fresh")
    committed = REPO / "pilot"
    names = sorted(p.relative_to(fresh).as_posix() for p in fresh.rglob("*") if p.is_file())
    assert names == sorted(p.relative_to(committed).as_posix() for p in committed.rglob("*") if p.is_file())
    for name in names:
        assert (fresh / name).read_bytes().replace(b"\r\n", b"\n") == (committed / name).read_bytes().replace(b"\r\n", b"\n"), name
    assert (committed / "canon" / "style.yaml").read_bytes().replace(b"\r\n", b"\n") == (REPO / "canon" / "style.yaml").read_bytes().replace(b"\r\n", b"\n")     # a copy, never a second style
