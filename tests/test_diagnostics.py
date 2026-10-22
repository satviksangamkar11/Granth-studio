"""Diagnostics are descriptive and never enforced; model-based ones are not_computed until validated."""
from __future__ import annotations

import sys

import pytest

from granthstudio.config import load_models
from granthstudio.diagnostics import measure_media, measure_shot, runner_diagnostic
from granthstudio.qa import DIAGNOSTICS
from tests.conftest import have_tool, make_clip, make_still

pytestmark = pytest.mark.skipif(not (have_tool("ffmpeg") and have_tool("ffprobe")), reason="media tools missing")

RUNNER = '''
import json, sys
payload = json.load(sys.stdin)
print(json.dumps({"value": {"metric": payload["metric"], "refs": len(payload["reference_paths"])}}))
'''


def test_video_measurements_are_descriptive_statistics(tmp_path):
    clip = make_clip(tmp_path / "c.mp4", seconds=0.5)
    result = measure_media(clip)
    color = result["color_distribution"]
    assert color["status"] == "computed" and color["enforced"] is False and color["value"]["frames"] >= 10
    assert 0 <= color["value"]["YAVG"]["mean"] <= 255 and color["value"]["YAVG"]["std"] >= 0
    assert result["motion_instability"]["value"]["ydif"]["max"] >= 0
    assert "not a calibrated sharpness metric" in result["edge_sharpness"]["method"]


def test_a_still_has_no_frame_difference(tmp_path):
    result = measure_media(make_still(tmp_path / "s.png"))
    assert result["color_distribution"]["value"]["frames"] == 1
    assert result["motion_instability"]["status"] == "not_computed" and "single frame" in result["motion_instability"]["reason"]


def test_all_frozen_diagnostics_are_reported_and_model_ones_wait_for_a_validated_runner(project, tmp_path):
    clip = make_clip(tmp_path / "c.mp4", seconds=0.3)
    models = load_models(project)
    result = measure_shot(models, clip, [])
    assert list(result) == list(DIAGNOSTICS)
    for name in ("face_embedding_similarity", "clip_style_similarity", "anachronism_suspicion", "object_presence"):
        assert result[name]["status"] == "not_computed" and "no validated diagnostics runner" in result[name]["reason"]
    script = tmp_path / "diag.py"; script.write_text(RUNNER, encoding="utf-8")
    models["diagnostics"] = {"status": "validated", "command": [sys.executable, str(script)], "model": "synthetic",
                             "revision": "1", "timeout_s": 30}
    answer = runner_diagnostic(models, "object_presence", clip, [clip])
    assert answer["status"] == "computed" and answer["enforced"] is False
    assert answer["value"] == {"metric": "object_presence", "refs": 1}
    assert measure_shot(models, clip, [])["clip_style_similarity"]["status"] == "computed"
