from __future__ import annotations
from pathlib import Path
from typing import Dict


def chapter_paths(adhyay: int, root: Path, flow_root: Path = Path("D:/aai work/flow_outputs")) -> Dict[str, Path]:
    """Return all canonical paths for a given adhyay (1..21)."""
    if not isinstance(adhyay, int) or isinstance(adhyay, bool) or not (1 <= adhyay <= 21):
        raise ValueError("adhyay must be an int in 1..21")

    nn = f"{adhyay:02d}"
    base = root / "canon" / f"adhyay_{nn}"
    shot_plans_dir = root / "canon" / "shot_plans" / f"A{adhyay}"
    images_dir = flow_root / f"adhyay_{nn}"

    if adhyay == 1:
        return {
            "base": base,
            "source_ovis": root / "canon" / "packets" / "adhyay_01" / "adhyay_01_ovis_hj.jsonl",
            "research_packet": root / "canon" / "packets" / "adhyay_01" / "frozen_copies",
            "script": root / "docs" / "pilot" / "A1_full_script_simple.md",
            "bible": root / "canon" / "bible" / "adhyay_01",
            "stage1_dir": root / "canon" / "adhyay_01" / "stage1",
            "audio_plan": root / "canon" / "audio" / "A1_audio_plan.json",
            "timing_plan": root / "canon" / "audio" / "A1_timing_plan.json",
            "measured": root / "canon" / "audio" / "A1_eleven_measured.json",
            "images_catalog": root / "canon" / "packets" / "adhyay_01" / "final_image_binding.json",   # A1 catalog = the binding file until B6 migrates it
            "image_binding": root / "canon" / "packets" / "adhyay_01" / "final_image_binding.json",
            "flow_jobs": root / "canon" / "drafts" / "A1_flow_shot_jobs.json",
            "approvals": base / "approvals.json",
            "caps": base / "caps.json",
            "spend": base / "spend.jsonl",
            "shot_plans_dir": shot_plans_dir,
            "images_dir": images_dir,
        }

    return {
        "base": base,
        "source_ovis": base / "source" / "ovis.jsonl",
        "research_packet": base / "research" / "packet.json",
        "script": base / "script" / "easy.md",
        "bible": base / "bible",
        "stage1_dir": base / "stage1",
        "audio_plan": base / "audio" / "plan.json",
        "timing_plan": base / "audio" / "timing.json",
        "measured": base / "audio" / "measured.json",
        "images_catalog": base / "images" / "catalog.json",
        "image_binding": base / "images" / "binding.json",
        "flow_jobs": base / "images" / "jobs.json",
        "approvals": base / "approvals.json",
        "caps": base / "caps.json",
        "spend": base / "spend.jsonl",
        "shot_plans_dir": shot_plans_dir,
        "images_dir": images_dir,
    }
