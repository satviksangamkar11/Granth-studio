"""ComfyUI capability gates and template handling, FFmpeg media checks, pilot mapping and throughput."""

from __future__ import annotations

from pathlib import Path

import pytest

from granthstudio.comfy import ComfyBackend, collect_outputs, ensure_validated, load_template, render_graph
from granthstudio.config import passing_receipts, require_capability
from granthstudio.errors import CapabilityDisabled, ConfigError, GateFailure, IntegrationUnavailable
from granthstudio.ffmpeg import assemble, probe, validate_video
from granthstudio.integrity import atomic_write_json
from granthstudio.pilot import PILOT_DEFINITIONS, plan_pilot, score_receipts
from tests.conftest import have_tool, make_clip


def _template(tmp_path: Path, status: str = "unvalidated") -> Path:
    path = tmp_path / "t.json"
    path.write_text('{"_status": "%s", "1": {"inputs": {"image": "{{START_IMAGE}}", "n": "{{FRAMES}}"}}}' % status,
                    encoding="utf-8")
    return path


def test_unvalidated_template_refused(tmp_path):
    with pytest.raises(IntegrationUnavailable, match="NOT VALIDATED"):
        ensure_validated(load_template(_template(tmp_path)))


def test_validated_template_renders_and_strips_metadata(tmp_path):
    template = load_template(_template(tmp_path, status="validated"))
    ensure_validated(template)
    graph = render_graph(template, {"START_IMAGE": 'C:\\pa"th.png', "FRAMES": "49"})
    assert "_status" not in graph
    assert graph["1"]["inputs"]["image"] == 'C:\\pa"th.png'
    assert graph["1"]["inputs"]["n"] == "49"


def test_unresolved_placeholder_is_error(tmp_path):
    template = load_template(_template(tmp_path, status="validated"))
    with pytest.raises(ConfigError, match="FRAMES"):
        render_graph(template, {"START_IMAGE": "x"})


def test_capability_refused_when_unvalidated(models, tmp_path):
    with pytest.raises(CapabilityDisabled, match="NOT VALIDATED"):
        require_capability(models, "i2v", tmp_path)


def test_capability_refused_when_checkpoint_unpinned(models, tmp_path):
    models["ltx"]["capabilities"]["i2v"] = "validated"
    with pytest.raises(CapabilityDisabled, match="not pinned"):
        require_capability(models, "i2v", tmp_path)


def test_capability_needs_passing_receipt(models, tmp_path):
    models["ltx"]["capabilities"]["i2v"] = "validated"
    models["ltx"]["checkpoint_sha256"] = "a" * 64
    with pytest.raises(CapabilityDisabled, match="benchmark receipt"):
        require_capability(models, "i2v", tmp_path)
    receipt = {
        "schema_version": 1, "capability": "i2v", "shot": "B", "checkpoint_sha256": "a" * 64,
        "workflow_version": "v", "gpu": "T4", "gpu_count": 1, "gpu_seconds_total": 60.0, "attempts": 1,
        "video_seconds": 2.0, "accepted": True, "outcome": "pass", "recorded_at": "2026-10-22T00:00:00Z",
    }
    atomic_write_json(tmp_path / "b.json", receipt)
    assert require_capability(models, "i2v", tmp_path)["shot"] == "B"
    assert passing_receipts(tmp_path, "flf", "a" * 64) == []


def test_collect_outputs_tracks_files():
    history = {"outputs": {"9": {"videos": [{"filename": "a.mp4", "subfolder": "", "type": "output"}]},
                           "3": {"images": [{"filename": "k.png"}]}}}
    assert [o["filename"] for o in collect_outputs(history)] == ["k.png", "a.mp4"]


def test_backend_reports_unreachable_as_not_validated():
    backend = ComfyBackend("http://127.0.0.1:9", timeout_s=0.5)
    with pytest.raises(IntegrationUnavailable, match="unreachable"):
        backend.submit({})


@pytest.mark.skipif(not (have_tool("ffmpeg") and have_tool("ffprobe")), reason="ffmpeg/ffprobe not on PATH")
def test_probe_validate_and_assemble_real_clips(tmp_path):
    a = make_clip(tmp_path / "a.mp4", 1.0)
    b = make_clip(tmp_path / "b.mp4", 1.0)
    assert abs(probe(a).duration_s - 1.0) < 0.1
    assert validate_video(a, 1.0, tolerance_s=0.1) == []
    out = tmp_path / "joined.mp4"
    assemble([a, b], out)
    assert validate_video(out, 2.0, tolerance_s=0.2) == []


@pytest.mark.skipif(not have_tool("ffprobe"), reason="ffprobe not on PATH")
def test_validate_reports_wrong_duration(tmp_path):
    clip = make_clip(tmp_path / "c.mp4", 1.0)
    assert validate_video(clip, 3.0, tolerance_s=0.1)


def test_pilot_requires_all_labels(approved_project, models):
    from granthstudio.canon import load_canon
    from granthstudio.episodes import compile_episode
    from granthstudio.research import load_research, require_approved

    compiled = compile_episode(approved_project, models, load_canon(approved_project), 1,
                               load_research(approved_project, 1), require_approved(approved_project, 1))
    with pytest.raises(ConfigError, match="missing"):
        plan_pilot(compiled)


def test_pilot_definitions_match_frozen_section_15():
    assert set(PILOT_DEFINITIONS) == {"A", "B", "C", "D", "E", "F"}
    assert PILOT_DEFINITIONS["A"]["tier"] == 0 and PILOT_DEFINITIONS["C"]["tier"] == 2


def _receipt(shot, seconds, gpu, accepted):
    return {
        "schema_version": 1, "capability": "i2v", "shot": shot, "checkpoint_sha256": None,
        "workflow_version": "v", "gpu": "T4", "gpu_count": 2, "gpu_seconds_total": gpu, "attempts": 1,
        "video_seconds": seconds, "accepted": accepted, "outcome": "pending", "recorded_at": "2026-10-22T00:00:00Z",
    }


def test_throughput_counts_failed_and_retry_gpu_time():
    score = score_receipts([_receipt("A", 4.0, 1800.0, True), _receipt("B", 9.0, 1800.0, False)])
    assert score["accepted_video_seconds"] == 4.0
    assert score["gpu_hours"] == 1.0
    assert score["accepted_sec_per_gpu_hour"] == 4.0


def test_throughput_blocks_without_human_decision():
    with pytest.raises(GateFailure, match="acceptance"):
        score_receipts([_receipt("A", 4.0, 60.0, None)])
