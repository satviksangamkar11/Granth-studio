"""Frozen 8: weight files visible to ComfyUI, and degenerate (all-flat) output rejection. Synthetic only."""
from __future__ import annotations

import shutil
import subprocess

import pytest

from granthstudio import pilotrun
from granthstudio.comfy import ComfyBackend
from granthstudio.diagnostics import flat_frames, is_degenerate
from granthstudio.errors import IntegrationUnavailable, TaskFailed
from granthstudio.pipeline import _verify_clip
from tests.conftest import have_tool
from tests.test_ltx_integration import FakeComfy, GRAPH
from tests.test_pilot_flow import comfy, pilot, T4  # noqa: F401  (fixtures)

media = pytest.mark.skipif(not (have_tool("ffmpeg") and have_tool("ffprobe")), reason="media tools missing")


def info(options):
    return {"SyntheticLoader": {"input": {"required": {"ckpt_name": [options, {}]}}}, "SyntheticSave": {}}


def test_weight_file_must_be_listed_by_comfyui():
    server = FakeComfy()
    try:
        backend = ComfyBackend(server.url, timeout_s=2)
        backend.require_model_files(GRAPH)  # default object_info has no definitions: tolerant
        server.object_info_override = info(["ltxv-2b-0.9.8-distilled.safetensors", "b.safetensors"])
        backend.require_model_files(GRAPH)
        server.object_info_override = info(["b.safetensors"])
        with pytest.raises(IntegrationUnavailable, match=r"cannot see weight file ltxv-2b.*node 1.*NOT VALIDATED"):
            backend.require_model_files(GRAPH)
        server.object_info_override = {"SyntheticLoader": {"input": {"required": {"ckpt_name": ["STRING", {}]}}}}
        backend.require_model_files(GRAPH)  # no option list: skipped
        server.object_info_override = {"SyntheticLoader": {"input": {"optional": {"ckpt_name": [["x.ckpt"], {}]}}}}
        with pytest.raises(IntegrationUnavailable):
            backend.require_model_files(GRAPH)
    finally:
        server.close()


def make(path, source, frames=10):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", source, "-frames:v", str(frames),
                    "-c:v", "libx264", "-threads", "1", "-pix_fmt", "yuv420p", str(path)], check=True, timeout=30)
    return path


@media
def test_flat_detection(tmp_path):
    assert not is_degenerate(make(tmp_path / "t.mp4", "testsrc=size=160x120:rate=24"))
    flat = make(tmp_path / "f.mp4", "color=c=blue:s=160x120:r=24")
    assert is_degenerate(flat) and flat_frames(flat) == 10
    # one non-flat frame among flat ones is not degenerate
    mixed = tmp_path / "m.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "color=c=blue:s=160x120:r=24",
                    "-f", "lavfi", "-i", "testsrc=size=160x120:rate=24", "-filter_complex",
                    "[0:v]trim=end_frame=4[a];[1:v]trim=end_frame=1[b];[a][b]concat=n=2:v=1", "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", str(mixed)], check=True, timeout=30)
    assert not is_degenerate(mixed) and 0 < flat_frames(mixed) < 5


@media
def test_flag_controls_clip_rejection(pilot, tmp_path):  # noqa: F811
    directory = tmp_path / "work"
    directory.mkdir()
    make(directory / "clip.mp4", "color=c=blue:s=160x120:r=24", frames=24)
    with pytest.raises(TaskFailed, match="every frame is one flat colour"):
        _verify_clip(directory, 1.0, pilot)
    _verify_clip(directory, 1.0)  # Tier 0 / no project: not checked
    (directory / "fallback.json").write_text("{}", encoding="utf-8")
    _verify_clip(directory, 1.0, pilot)  # declared fallback: not checked
    (directory / "fallback.json").unlink()
    text = (pilot.root / "config" / "runtime.yaml").read_text(encoding="utf-8")
    (pilot.root / "config" / "runtime.yaml").write_text(text.replace("reject_flat_output: true", "reject_flat_output: false"),
                                                        encoding="utf-8")
    _verify_clip(directory, 1.0, pilot)


@media
def test_flat_ltx_render_fails_without_fallback(pilot, comfy, tmp_path):  # noqa: F811
    make(tmp_path / "flat.mp4", "color=c=blue:s=160x120:r=24", frames=49)
    comfy.view_bytes = (tmp_path / "flat.mp4").read_bytes()
    _, _, _, results, _ = pilotrun.run_pilot(pilot, 1, None, execute=True, require_gpu=False)
    ltx = [r for r in results if r.stage in ("tier1", "tier2")]
    assert ltx and all(r.status == "failed" and "flat colour" in r.detail and "FALLBACK" not in r.detail for r in ltx), \
        [(r.name, r.status, r.detail) for r in results]
    assert all(r.attempts > 1 for r in ltx)  # retried before failing
