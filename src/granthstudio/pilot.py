"""Six-shot A-F pilot (frozen section 15): mapping checks and throughput accounting (decision D-004).

Accepted sec/GPU-hour = accepted video seconds / total GPU-hours consumed. Total GPU time includes
failed renders, retries and rework. A receipt with no human acceptance decision blocks scoring.
"""

from __future__ import annotations

from typing import Any

from .errors import ConfigError, GateFailure
from .schemas import validate_document

PILOT_DEFINITIONS: dict[str, dict[str, Any]] = {
    "A": {"focus": "Tier 0 establishing / ambient shot", "tier": 0},
    "B": {"focus": "single-image I2V with a major recurring character", "tier": 1},
    "C": {"focus": "FLF variant of the same shot and character", "tier": 2},
    "D": {"focus": "character gesture / dialogue coverage", "tier": 1},
    "E": {"focus": "recurring character in different lighting", "tier": 1},
    "F": {"focus": "shared-visual Marathi and Hindi final edits", "tier": None},
}

RECOVERY_CHECK = "Interrupt during a run, resume, verify artifacts (required in addition to A-F)"


def plan_pilot(compiled: dict[str, Any]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    by_id = {shot["shot_id"]: shot for shot in compiled["shots"]}
    for shot in compiled["shots"]:
        label = shot.get("pilot_shot")
        if label:
            mapping[label] = shot["shot_id"]
    missing = sorted(set(PILOT_DEFINITIONS) - set(mapping))
    if missing:
        raise ConfigError(f"pilot shots missing from the manifest: {missing}")
    for label, shot_id in mapping.items():
        expected = PILOT_DEFINITIONS[label]["tier"]
        if expected is not None and by_id[shot_id]["tier"] != expected:
            raise ConfigError(f"pilot shot {label} must be tier {expected}")
    return dict(sorted(mapping.items()))


def score_receipts(receipts: list[dict[str, Any]]) -> dict[str, float]:
    accepted_seconds = 0.0
    gpu_seconds = 0.0
    undecided: list[str] = []
    for receipt in receipts:
        validate_document("benchmark_receipt", receipt)
        gpu_seconds += receipt["gpu_seconds_total"]
        if receipt["accepted"] is None:
            undecided.append(receipt["shot"])
        elif receipt["accepted"]:
            accepted_seconds += receipt["video_seconds"]
    if undecided:
        raise GateFailure(f"human acceptance decision missing for shots {sorted(undecided)}")
    if gpu_seconds <= 0:
        raise GateFailure("no GPU time recorded")
    gpu_hours = gpu_seconds / 3600
    return {
        "accepted_video_seconds": accepted_seconds,
        "gpu_hours": gpu_hours,
        "accepted_sec_per_gpu_hour": accepted_seconds / gpu_hours,
    }
