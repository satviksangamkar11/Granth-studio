"""The retrospective offline validator for GPU-stage evidence, on synthetic clips only."""
from __future__ import annotations

import importlib.util
import subprocess
import sys

import pytest

from tests.conftest import REPO, have_tool

pytestmark = pytest.mark.skipif(not (have_tool("ffmpeg") and have_tool("ffprobe")), reason="media tools missing")
spec = importlib.util.spec_from_file_location("offline_validate", REPO / "scripts" / "kaggle" / "offline_validate_gpu_evidence.py")
ov = importlib.util.module_from_spec(spec); sys.modules["offline_validate"] = ov; spec.loader.exec_module(ov)
RECEIPT = {"inputs": {"width": 64, "height": 64, "frames": 9, "fps": 24}, "verdict": "NOT_VALIDATED"}
JOURNAL = {"state": "completed", "attempt": 1, "prompt_id": "p", "history": [{"seed_inputs": [{"node": "102", "input": "noise_seed", "value": 1}]}]}


def make(path, source):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", source, "-frames:v", "9", "-c:v", "libx264", "-threads", "1", "-pix_fmt", "yuv420p", str(path)],
                   check=True, timeout=60)
    return path


def test_a_smooth_clip_passes_and_the_original_verdict_is_only_restated(tmp_path):
    clip = make(tmp_path / "ok.mp4", "gradients=size=64x64:rate=24:speed=0.05:seed=7")
    problems, facts = ov.validate(clip, RECEIPT, JOURNAL, {"ok": True})
    assert problems == [] and facts["frames"] == 9 and facts["fps"] == "24/1"


def test_a_hard_cut_after_the_first_frame_is_reported_for_human_review(tmp_path):
    first = make(tmp_path / "a.mp4", "color=c=black:size=64x64:rate=24")
    second = make(tmp_path / "b.mp4", "color=c=white:size=64x64:rate=24")
    cut = tmp_path / "cut.mp4"
    listing = tmp_path / "l.txt"; listing.write_text(f"file '{first.as_posix()}'\nfile '{second.as_posix()}'\n", encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(listing), "-frames:v", "18", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(cut)], check=True, timeout=60)
    problems, _ = ov.validate(cut, RECEIPT, JOURNAL, {"ok": True})
    assert any("discontinuity" in p for p in problems)


@pytest.mark.parametrize("receipt,journal,attribution,fragment", [
    ({"inputs": {"width": 64, "height": 64, "frames": 17, "fps": 24}}, JOURNAL, {"ok": True}, "9 frames != requested 17"),
    (RECEIPT, {**JOURNAL, "state": "submitting"}, {"ok": True}, "not one completed submission"),
    (RECEIPT, {**JOURNAL, "history": [{"seed_inputs": []}]}, {"ok": True}, "no sampler seed"),
    (RECEIPT, JOURNAL, {"ok": False, "problems": ["x"]}, "attribution"),
])
def test_other_gaps_are_reported(tmp_path, receipt, journal, attribution, fragment):
    clip = make(tmp_path / "ok.mp4", "gradients=size=64x64:rate=24:speed=0.05:seed=7")
    problems, _ = ov.validate(clip, receipt, journal, attribution)
    assert any(fragment in p for p in problems), problems


def test_the_output_path_may_not_alias_an_input_and_hash_bindings_are_keyed_by_role(tmp_path):
    import json
    clip = make(tmp_path / "ok.mp4", "gradients=size=64x64:rate=24:speed=0.05:seed=7")
    (tmp_path / "a").mkdir(); (tmp_path / "b").mkdir()
    receipt, journal, attribution = tmp_path / "a" / "evidence.json", tmp_path / "b" / "evidence.json", tmp_path / "attr.json"
    receipt.write_text(json.dumps(RECEIPT), encoding="utf-8"); journal.write_text(json.dumps(JOURNAL), encoding="utf-8"); attribution.write_text(json.dumps({"ok": True}), encoding="utf-8")
    base = [str(tmp_path), "--clip", str(clip), "--receipt", str(receipt), "--journal", str(journal), "--attribution", str(attribution)]
    before = receipt.read_bytes()
    with pytest.raises(SystemExit):
        ov.main([*base, "--out", str(receipt)])                      # would have replaced the original verdict file
    assert receipt.read_bytes() == before
    out = tmp_path / "report.json"
    assert ov.main([*base, "--out", str(out)]) == 0
    bound = json.loads(out.read_text(encoding="utf-8"))["bound_inputs"]
    assert set(bound) == {"clip", "receipt", "journal", "attribution"} and bound["receipt"]["sha256"] != bound["journal"]["sha256"]   # same basename, two bindings
