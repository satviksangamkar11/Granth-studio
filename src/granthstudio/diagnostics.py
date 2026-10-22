"""QA diagnostics (frozen section 9): logged for later calibration, never enforced.

Three diagnostics are measured with FFmpeg alone. They are descriptive statistics, not quality
judgments, and no threshold exists for any of them. The model-based ones (face embedding, CLIP
style, anachronism, object presence) go through the optional ``diagnostics`` runner and report
``not_computed`` until a runner has been validated by a human.
"""
from __future__ import annotations

import math
import statistics
from pathlib import Path
from typing import Any

from .errors import ConfigError
from .ffmpeg import _run, _tool
from .qa import DIAGNOSTICS
from .runners import run_json

FFMPEG_DIAGNOSTICS = ("color_distribution", "edge_sharpness", "motion_instability")
RUNNER_DIAGNOSTICS = tuple(d for d in DIAGNOSTICS if d not in FFMPEG_DIAGNOSTICS)
_EDGE_FILTER = "edgedetect=low=0.1:high=0.4"


def _frames(path: Path, video_filter: str) -> list[dict[str, float]]:
    chain = f"{video_filter},signalstats" if video_filter else "signalstats"
    out = _run([_tool("ffmpeg"), "-v", "error", "-i", str(path), "-vf", f"{chain},metadata=print:file=-",
                "-an", "-f", "null", "-"]).stdout
    frames: list[dict[str, float]] = []
    for line in out.splitlines():
        if line.startswith("frame:"):
            frames.append({})
        elif line.startswith("lavfi.signalstats.") and frames:
            key, _, value = line.removeprefix("lavfi.signalstats.").partition("=")
            try:
                number = float(value)
            except ValueError:
                continue
            if math.isfinite(number):  # ffmpeg can print nan/inf; those are not measurements
                frames[-1][key] = number
    if not frames:
        raise ConfigError(f"{path.name}: ffmpeg produced no frame statistics")
    return frames


def _flat_flags(path: Path) -> list[bool]:
    return [all(f.get(f"{p}MIN") is not None and f.get(f"{p}MIN") == f.get(f"{p}MAX") for p in "YUV")
            for f in _frames(path, "")]


def flat_frames(path: Path) -> int:
    """Frames that are one flat colour (min == max on all three planes)."""
    return sum(_flat_flags(path))


def is_degenerate(path: Path) -> bool:
    """True when every frame is flat: the output of a failed decode, not an image."""
    return all(_flat_flags(path))


def _summary(values: list[float]) -> dict[str, float]:
    return {"mean": statistics.fmean(values), "min": min(values), "max": max(values),
            "std": statistics.pstdev(values) if len(values) > 1 else 0.0}


def _entry(value: dict[str, Any], method: str) -> dict[str, Any]:
    return {"status": "computed", "enforced": False, "method": method, "value": value}


def measure_media(path: Path) -> dict[str, dict[str, Any]]:
    """Descriptive FFmpeg statistics for a video or still image."""
    frames = _frames(path, "")
    color = {key: _summary([f[key] for f in frames if key in f]) for key in ("YAVG", "UAVG", "VAVG", "SATAVG", "HUEMED")
             if any(key in f for f in frames)}
    edges = _frames(path, _EDGE_FILTER)
    result = {
        "color_distribution": _entry({"frames": len(frames), **color}, "ffmpeg signalstats per frame"),
        "edge_sharpness": _entry({"edge_density_yavg": _summary([f["YAVG"] for f in edges])},
                                 f"proxy: mean luma of ffmpeg {_EDGE_FILTER} output; not a calibrated sharpness metric"),
    }
    differences = [f["YDIF"] for f in frames if "YDIF" in f]
    if len(frames) > 1 and differences:
        result["motion_instability"] = _entry({"ydif": _summary(differences)},
                                              "frame-to-frame luma difference (signalstats YDIF); descriptive only")
    else:
        result["motion_instability"] = {"status": "not_computed", "enforced": False,
                                        "reason": "single frame: no frame-to-frame difference exists"}
    return result


def runner_diagnostic(models: dict[str, Any], metric: str, media: Path, references: list[Path]) -> dict[str, Any]:
    section = models.get("diagnostics")
    if not section or section["status"] != "validated" or not all(section[k] for k in ("command", "model", "revision")):
        return {"status": "not_computed", "enforced": False,
                "reason": "no validated diagnostics runner (model and version undecided)"}
    answer = run_json(section, {"metric": metric, "media_path": str(media), "reference_paths": [str(r) for r in references]})
    return {"status": "computed", "enforced": False, "method": f"{section['model']} @ {section['revision']}",
            "value": answer.get("value")}


def measure_shot(models: dict[str, Any], media: Path, references: list[Path]) -> dict[str, dict[str, Any]]:
    """All seven frozen diagnostics for one clip: measured where possible, otherwise not_computed."""
    result = measure_media(media)
    for metric in RUNNER_DIAGNOSTICS:
        result[metric] = runner_diagnostic(models, metric, media, references)
    return {name: result[name] for name in DIAGNOSTICS}
