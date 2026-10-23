import importlib.util
import json
import subprocess
import sys

import pytest

from tests.conftest import REPO, have_tool


@pytest.mark.skipif(not have_tool("ffmpeg"), reason="ffmpeg required")
def test_the_silent_preview_places_every_planned_shot_at_one_size_and_writes_both_subtitle_files(tmp_path):
    spec = importlib.util.spec_from_file_location("silent_preview", REPO / "scripts" / "pilot" / "silent_preview.py")
    sp = importlib.util.module_from_spec(spec); sys.modules["silent_preview"] = sp; spec.loader.exec_module(sp)
    clips = []
    for n in (1, 2, 3):                                                                               # synthetic stand-ins for the LTX clips (768x512, 49 frames)
        clip = tmp_path / f"ltx{n}.mp4"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=768x512:rate=24", "-frames:v", "49", "-pix_fmt", "yuv420p", str(clip)], check=True)
        clips.append(f"{n}={clip}")
    out = tmp_path / "preview"
    assert sp.main(["--ltx", *clips, "--out", str(out)]) == 0
    report = json.loads((out / "preview_report.json").read_text(encoding="utf-8"))
    assert [s["shot_id"] for s in report["shots"]] == [f"a01_s0{n}_sh0{k}" for n in (1, 2, 3) for k in (1, 2, 3)]
    assert (report["width"], report["height"]) == (1152, 768) and report["audio"] is None and abs(report["duration_s"] - 42.125) < 0.05
    assert [s["kind"] for s in report["shots"]][:3] == ["tier0_still_motion", "ltx_i2v", "tier0_still_motion"]
    for lang in ("mr", "hi"):
        srt = (out / f"pilot_silent_preview.{lang}.srt").read_text(encoding="utf-8")
        assert srt.count(" --> ") == 6                                                                # six narration lines, on the shots that carry them
    assert "SILENT PREVIEW" in report["note"] and "NOT_DONE" in report["note"]
