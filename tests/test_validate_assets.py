import copy
import hashlib
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("validate_assets", ROOT / "scripts" / "pipeline" / "validate_assets.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

LINES = {"S4-L1", "S4-L2", "S4-L3"}
PRESETS = {"03_slow_cinematic_push": ["img"], "10_object_insert": ["insert"]}


def has(errs, *words):
    return any(all(w in e for w in words) for e in errs)


def beats():
    return {"adhyay": 1, "scenes": [{"scene_id": "S4", "beats": [
        {"line_id": "S4-L1", "voice": "narrator", "mr_s": 2.8, "hi_s": 2.88, "start_s": 0.5, "end_s": 3.38, "shot": 1},
        {"line_id": "S4-L2", "voice": "bankatlal", "mr_s": 6.96, "hi_s": 7.92, "start_s": 3.88, "end_s": 11.8, "shot": 1},
        {"line_id": "S4-L3", "voice": "narrator", "mr_s": 7.6, "hi_s": 7.52, "start_s": 12.3, "end_s": 19.9, "shot": 3}]}]}


def test_beats_valid_and_each_rule():
    assert v.validate_beats(1, beats(), LINES) == []
    assert has(v.validate_beats(2, beats(), LINES), "adhyay")
    assert has(v.validate_beats(1, beats(), {"S4-L1"}), "S4-L2", "script")
    b = beats()
    b["scenes"][0]["beats"][1]["line_id"] = "S4-L1"
    assert has(v.validate_beats(1, b, LINES), "S4-L1", "duplicate")
    b = beats()
    b["scenes"][0]["beats"][0]["end_s"] = 0.4
    assert has(v.validate_beats(1, b, LINES), "S4-L1", "end")
    b = beats()
    b["scenes"][0]["beats"][1]["end_s"] = 10.0                                # 6.12 s < Hindi 7.92 s: the beat must fit the LONGER language
    assert has(v.validate_beats(1, b, LINES), "S4-L2", "longer")
    b = beats()
    b["scenes"][0]["beats"][1]["start_s"] = 3.0                               # overlaps the first beat
    assert has(v.validate_beats(1, b, LINES), "overlap")
    b = beats()
    b["scenes"][0]["beats"][2]["shot"] = 2
    assert has(v.validate_beats(1, b, LINES), "S4-L3", "shot")
    b = beats()
    b["scenes"][0]["beats"].reverse()
    assert has(v.validate_beats(1, b, LINES), "order")
    assert v.validate_beats(1, beats(), LINES, shot_seconds=12.0) != []       # the shot number follows shot_seconds
    for bad in (0, -1, float("nan")):
        assert has(v.validate_beats(1, beats(), LINES, shot_seconds=bad), "shot_seconds")
    assert has(v.validate_beats(1, beats(), LINES, tolerance=-1), "tolerance")
    empty = {"adhyay": 1, "scenes": [{"scene_id": "S4", "beats": []}]}
    assert has(v.validate_beats(1, empty, LINES), "S4", "no beats")
    dup_scene = copy.deepcopy(beats())
    dup_scene["scenes"].append(copy.deepcopy(dup_scene["scenes"][0]))
    assert has(v.validate_beats(1, dup_scene, LINES), "duplicate")


def catalog(tmp_path):
    files = {"SH_S4_01.png": b"one", "SH_S4_02.png": b"two"}
    for n, data in files.items():
        (tmp_path / n).write_bytes(data)
    imgs = {n[:-4]: {"file": n, "sha256": hashlib.sha256(d).hexdigest(), "chosen_version": 1, "prompt_sha256": "a" * 64, "model": "m", "edit_id": None, "approved": True} for n, d in files.items()}
    return {"adhyay": 1, "images": imgs}


def test_catalog_checks_live_files(tmp_path):
    c = catalog(tmp_path)
    assert v.validate_catalog(1, c, tmp_path) == []
    assert has(v.validate_catalog(2, c, tmp_path), "adhyay")
    bad = copy.deepcopy(c)
    bad["images"]["SH_S4_01"]["sha256"] = "0" * 64
    assert has(v.validate_catalog(1, bad, tmp_path), "SH_S4_01", "sha256")
    assert v.validate_catalog(1, bad, tmp_path, check_files=False) == []
    (tmp_path / "SH_S4_02.png").unlink()
    assert has(v.validate_catalog(1, c, tmp_path), "SH_S4_02", "missing")
    c2 = catalog(tmp_path)
    c2["images"]["bad_key"] = c2["images"]["SH_S4_01"]
    assert has(v.validate_catalog(1, c2, tmp_path), "bad_key")
    c3 = catalog(tmp_path)
    c3["images"]["SH_S4_01"]["file"] = "../x.png"
    assert has(v.validate_catalog(1, c3, tmp_path), "SH_S4_01", "file")
    c4 = catalog(tmp_path)
    c4["images"]["SH_S4_02"]["sha256"] = c4["images"]["SH_S4_01"]["sha256"]
    (tmp_path / "SH_S4_02.png").write_bytes(b"one")
    assert has(v.validate_catalog(1, c4, tmp_path), "duplicate")
    (tmp_path / "SH_S4_01.png").unlink()
    (tmp_path / "SH_S4_01.png").mkdir()                                       # an unreadable file is an error message, never an exception
    assert has(v.validate_catalog(1, c, tmp_path), "SH_S4_01")


def anim():
    return {"adhyay": 1, "scene_id": "S4", "shots": [
        {"shot_id": "S4-1", "preset": "03_slow_cinematic_push", "assets": {"img": "SH_S4_01"}, "held_pose": "p", "transition_out": "cut", "need_new": None},
        {"shot_id": "S4-2", "preset": "NEED_NEW", "assets": {}, "held_pose": "bow", "transition_out": "cut", "need_new": {"reason": "bow", "class": "missing_image"}}]}


def test_animation_rules(tmp_path):
    c = catalog(tmp_path)
    assert v.validate_animation(1, anim(), c, PRESETS, expected_shots=2) == []
    assert has(v.validate_animation(1, anim(), c, PRESETS, expected_shots=5), "expected")
    a = anim()
    a["shots"][0]["assets"] = {"insert": "SH_S4_01"}
    assert has(v.validate_animation(1, a, c, PRESETS), "S4-1", "role")
    a = anim()
    a["shots"][0]["assets"] = {"img": "SH_S4_09"}
    assert has(v.validate_animation(1, a, c, PRESETS), "SH_S4_09", "catalog")
    c2 = copy.deepcopy(c)
    c2["images"]["SH_S4_01"]["approved"] = False
    assert has(v.validate_animation(1, anim(), c2, PRESETS), "SH_S4_01", "approved")
    a = anim()
    a["shots"][0]["preset"] = "99_unknown"
    assert has(v.validate_animation(1, a, c, PRESETS), "99_unknown")
    a = anim()
    a["shots"][1]["need_new"] = None
    assert has(v.validate_animation(1, a, c, PRESETS), "S4-2", "need_new")
    a = anim()
    a["shots"][0]["need_new"] = {"reason": "r", "class": "renderer_gap"}
    assert has(v.validate_animation(1, a, c, PRESETS), "S4-1", "need_new")
    a = anim()
    a["shots"][1]["assets"] = {"img": "SH_S4_02"}
    assert has(v.validate_animation(1, a, c, PRESETS), "S4-2", "assets")
    a = anim()
    a["shots"][1]["shot_id"] = "S4-3"
    assert has(v.validate_animation(1, a, c, PRESETS), "consecutive")
    a = anim()
    a["shots"][0]["dialogue"] = "x"                                           # Kimi may not add dialogue
    assert v.validate_animation(1, a, c, PRESETS)
    assert has(v.validate_animation(2, anim(), c, PRESETS), "adhyay")


def test_fingerprints_and_freshness(tmp_path):
    c = catalog(tmp_path)
    fp = v.fingerprint_images(c, ["SH_S4_01", "SH_S4_02"])
    assert fp == {k: c["images"][k]["sha256"] for k in ("SH_S4_01", "SH_S4_02")}
    with pytest.raises(KeyError):
        v.fingerprint_images(c, ["SH_S9_99"])
    plan = {"adhyay": 1, "scene_id": "S4", "fingerprints": {"script": "1" * 64, "timing": "2" * 64, "presets": "3" * 64, "images": {"SH_S4_01": fp["SH_S4_01"]}},
            "shots": anim()["shots"], "approved_by": "owner", "approved_date": "2026-10-28"}
    cur = {"script": "1" * 64, "timing": "2" * 64, "presets": "3" * 64, "images": dict(fp)}
    assert v.validate_shot_plan_fresh(plan, cur) == []
    assert has(v.validate_shot_plan_fresh(plan, dict(cur, script="9" * 64)), "script changed")
    assert has(v.validate_shot_plan_fresh(plan, dict(cur, timing="9" * 64)), "timing changed")
    assert has(v.validate_shot_plan_fresh(plan, dict(cur, presets="9" * 64)), "presets changed")
    assert has(v.validate_shot_plan_fresh(plan, dict(cur, images={"SH_S4_01": "9" * 64})), "image SH_S4_01 changed")
    assert has(v.validate_shot_plan_fresh(plan, dict(cur, images={})), "SH_S4_01", "missing")
    incomplete = copy.deepcopy(plan)
    incomplete["fingerprints"]["images"] = {}                                 # a plan that omits the asset its shot uses can never replay
    assert has(v.validate_shot_plan_fresh(incomplete, cur), "SH_S4_01", "not fingerprinted")
