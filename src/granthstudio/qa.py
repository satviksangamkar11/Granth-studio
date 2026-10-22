"""Quality gates (frozen section 9).

Hard gates block release. Diagnostics are logged for later calibration and are never enforced:
the frozen plan forbids enforcing thresholds that have not been calibrated.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from .config import Project
from .integrity import atomic_write_json

HARD_GATES = ("source_integrity", "canon_identity", "marathi_lock", "hindi_terms", "task_outputs", "video_decode")
DIAGNOSTICS = (
    "face_embedding_similarity",
    "clip_style_similarity",
    "color_distribution",
    "edge_sharpness",
    "motion_instability",
    "anachronism_suspicion",
    "object_presence",
)


@dataclass(frozen=True)
class GateResult:
    name: str
    passed: bool
    detail: str


def gate(name: str, problems: list[str]) -> GateResult:
    return GateResult(name, not problems, "ok" if not problems else "; ".join(problems))


def report_path(project: Project, adhyay: int) -> Path:
    return project.artifacts_dir / "reports" / f"adhyay_{adhyay:02d}_qa.json"


def write_report(project: Project, adhyay: int, gates: list[GateResult]) -> Path:
    names = {g.name for g in gates}
    released = set(HARD_GATES) <= names and all(g.passed for g in gates)
    report = {
        "schema_version": 1,
        "adhyay": adhyay,
        "released": released,
        "hard_gates": [asdict(g) for g in gates],
        "diagnostics": {name: {"status": "not_computed", "enforced": False} for name in DIAGNOSTICS},
        "notes": "Diagnostics are logged only. No threshold is calibrated or enforced.",
    }
    path = report_path(project, adhyay)
    atomic_write_json(path, report)
    return path
