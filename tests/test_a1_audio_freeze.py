"""Adhyay 1 speech + timing freeze (checklist E2/E3, 2026-11-01): the frozen files are unchanged and the timing fits both languages' measured speech."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FREEZE = ROOT / "canon" / "adhyay_01" / "audio_freeze.json"
pytestmark = pytest.mark.skipif(not FREEZE.is_file(), reason="Adhyay 1 freeze record not present")


def _json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def _path(name: str) -> Path:
    p = Path(name)
    return p if p.is_absolute() else ROOT / p


def test_frozen_files_are_byte_unchanged():
    for name, sha in json.loads(FREEZE.read_text(encoding="utf-8"))["sha256"].items():
        p = _path(name)
        if not p.is_file():
            pytest.skip(f"{name} not on this machine")
        assert hashlib.sha256(p.read_bytes()).hexdigest() == sha, f"{name} changed after the freeze"


def test_timing_fits_both_languages_and_tiles_every_scene():
    timing, measured = _json("canon/audio/A1_timing_plan.json"), _json("canon/audio/A1_eleven_measured.json")
    assert timing["split_sha256"] == _json("canon/director_runs/a1_split_rev9/macro_A1.json")["macro_sha256"]
    timed, shots = set(), 0
    for scene in timing["scenes"]:
        sh = scene["shots"]
        shots += len(sh)
        assert [s["shot"] for s in sh] == list(range(1, len(sh) + 1)) == list(range(1, scene["planned_shots"] + 1))
        assert sh[0]["from_s"] == 0 and all(a["to_s"] == b["from_s"] for a, b in zip(sh, sh[1:]))
        prev_end = 0.0
        for beat in scene["beats"]:
            timed.add(beat["line"])
            need = max(measured["lines"][beat["line"]]["mr"], measured["lines"][beat["line"]]["hi"])
            assert beat["end_s"] - beat["start_s"] + 0.011 >= need, f"{beat['line']} window shorter than its longer language"
            assert beat["start_s"] >= prev_end - 1e-9, f"{beat['line']} overlaps the previous line"
            prev_end = beat["end_s"]
            home = next(s for s in sh if s["from_s"] - 1e-9 <= beat["start_s"] < s["to_s"])
            assert home["shot"] == beat["shot"]
        if scene["beats"]:
            assert sh[-1]["to_s"] + 1e-9 >= scene["beats"][-1]["end_s"], f"{scene['scene']} picture ends before its speech"
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    assert shots == freeze["counts"]["shots"]
    assert sorted(set(measured["lines"]) - timed) == sorted(freeze["untimed_optional_lines"])
    assert len(timed) == freeze["counts"]["timed_core_lines"]
