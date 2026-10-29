from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any
from datetime import date

# Import parse_script from check_script
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pipeline"))
from check_script import parse_script  # type: ignore[import-not-found]


REAL_SHOTS = 61
REAL_SCENES = 9


def real_unfilmed(root: Path, problems: list[str] | None = None) -> set[int]:
    """Return the set of real unfilmed ovis from A1_rev1.json."""
    path = root / "canon" / "story_split_edits" / "A1_rev1.json"
    result: set[int] = set()
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return result

    if not isinstance(data, dict):
        return result

    unfilmed_ranges = data.get("unfilmed_ranges")
    if not isinstance(unfilmed_ranges, list):
        if problems is not None:
            problems.append("unfilmed_ranges: bad shape")
        unfilmed_ranges = []

    for item in unfilmed_ranges:
        if not isinstance(item, dict):
            continue
        ovi_range = item.get("ovi_range")
        if not isinstance(ovi_range, list) or len(ovi_range) != 2:
            continue
        lo, hi = ovi_range
        if type(lo) is not int or type(hi) is not int:
            continue
        if hi - lo > 5000:
            continue
        if lo > hi:
            continue
        result.update(range(lo, hi + 1))
    return result


def real_scenes(root: Path) -> dict[str, set[int]]:
    """Return mapping of real scene id -> set of ovis from the script."""
    path = root / "docs" / "pilot" / "A1_full_script_simple.md"
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return {}

    lines = parse_script(text)
    if not isinstance(lines, list):
        return {}

    scenes: dict[str, set[int]] = {}
    for line in lines:
        scene_id = line.get("scene")
        ovi = line.get("ovi")
        if scene_id is None or ovi is None:
            continue
        if not isinstance(scene_id, str) or type(ovi) is not int:
            continue
        scenes.setdefault(scene_id, set()).add(ovi)
    return scenes


def _read_json_safe(path: Path) -> tuple[Any | None, list[str]]:
    """Read JSON file, return (data, problems)."""
    problems: list[str] = []
    if not path.exists():
        problems.append(f"missing: {path.name}")
        return None, problems
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f), problems
    except Exception as e:
        problems.append(f"corrupt: {path.name} ({e})")
        return None, problems


def _round3(x: float | None) -> float | None:
    if x is None:
        return None
    return round(x, 3)


def score(trial_dir: Path, root: Path) -> dict:
    """Score a trial directory against real decisions."""
    problems: list[str] = []

    # Read trial files
    coverage_data, cov_problems = _read_json_safe(trial_dir / "coverage.json")
    problems.extend(cov_problems)
    scenes_data, sc_problems = _read_json_safe(trial_dir / "scenes.json")
    problems.extend(sc_problems)
    shots_data, sh_problems = _read_json_safe(trial_dir / "shots.json")
    problems.extend(sh_problems)
    briefs_data, br_problems = _read_json_safe(trial_dir / "briefs.json")
    problems.extend(br_problems)

    # --- Omissions ---
    trial_omissions: set[int] = set()
    coverage_readable = coverage_data is not None
    if coverage_readable and isinstance(coverage_data, dict):
        ovis = coverage_data.get("ovis")
        if isinstance(ovis, list):
            for item in ovis:
                if isinstance(item, dict) and item.get("disposition") == "PROPOSE_OMISSION":
                    ovi = item.get("ovi")
                    if type(ovi) is int:
                        trial_omissions.add(ovi)

    real_omissions = real_unfilmed(root, problems)
    both = trial_omissions & real_omissions
    union = trial_omissions | real_omissions

    if coverage_readable:
        trial_count = len(trial_omissions)
        real_count = len(real_omissions)
        both_count = len(both)
        union_count = len(union)

        precision = _round3(both_count / trial_count) if trial_count else None
        recall = _round3(both_count / real_count) if real_count else None
        jaccard = _round3(both_count / union_count) if union_count else None
    else:
        trial_count = None
        real_count = len(real_omissions)
        both_count = 0
        precision = None
        recall = None
        jaccard = None

    omissions = {
        "trial": trial_count,
        "real": real_count,
        "both": both_count,
        "precision": precision,
        "recall": recall,
        "jaccard": jaccard,
    }

    # --- Scenes ---
    trial_scenes: list[dict] = []
    scenes_readable = scenes_data is not None
    if scenes_readable and isinstance(scenes_data, dict):
        scenes_list = scenes_data.get("scenes")
        if isinstance(scenes_list, list):
            for s in scenes_list:
                if isinstance(s, dict):
                    scene_id = s.get("scene_id")
                    ovi_range = s.get("ovi_range")
                    if isinstance(scene_id, str) and isinstance(ovi_range, list) and len(ovi_range) == 2:
                        lo, hi = ovi_range
                        if type(lo) is int and type(hi) is int and lo <= hi:
                            trial_scenes.append({"scene_id": scene_id, "lo": lo, "hi": hi})

    real_scenes_map = real_scenes(root)
    real_scene_count = len(real_scenes_map)

    per_real_scene: list[dict] = []
    covered_fractions: list[float] = []

    for real_scene_id, real_ovis in real_scenes_map.items():
        best_fraction = 0.0
        best_trial_scene: str | None = None
        real_ovi_count = len(real_ovis)

        for ts in trial_scenes:
            lo, hi = ts["lo"], ts["hi"]
            covered = sum(1 for ovi in real_ovis if lo <= ovi <= hi)
            if real_ovi_count > 0:
                fraction = covered / real_ovi_count
                if fraction > best_fraction:
                    best_fraction = fraction
                    best_trial_scene = ts["scene_id"]

        per_real_scene.append({
            "scene": real_scene_id,
            "ovis": real_ovi_count,
            "best_trial_scene": best_trial_scene,
            "covered_fraction": _round3(best_fraction),
        })
        covered_fractions.append(best_fraction)

    if scenes_readable:
        scene_agreement = _round3(sum(covered_fractions) / len(covered_fractions)) if covered_fractions else None
        trial_scene_count = len(trial_scenes)
    else:
        scene_agreement = None
        trial_scene_count = None

    scenes = {
        "trial": trial_scene_count,
        "real": REAL_SCENES,
        "per_real_scene": per_real_scene,
    }

    # --- Shots ---
    shots_readable = shots_data is not None
    if shots_readable and isinstance(shots_data, dict):
        shots_list = shots_data.get("shots")
        if isinstance(shots_list, list):
            trial_shots = len(shots_list)
        else:
            trial_shots = 0
    else:
        trial_shots = None

    shots = {"trial": trial_shots, "real": REAL_SHOTS}

    # --- Images ---
    briefs_readable = briefs_data is not None
    if briefs_readable and isinstance(briefs_data, dict):
        images_list = briefs_data.get("images")
        if isinstance(images_list, list):
            trial_images = len(images_list)
        else:
            trial_images = 0
    else:
        trial_images = None

    images = {"trial": trial_images, "real": 59}

    # --- Core lines ---
    script_path = root / "docs" / "pilot" / "A1_full_script_simple.md"
    try:
        script_text = script_path.read_text(encoding="utf-8")
        script_lines = parse_script(script_text)
    except Exception as e:
        problems.append(f"corrupt: {script_path.name} ({e})")
        script_lines = []

    if not isinstance(script_lines, list):
        script_lines = []

    core_lines = [line for line in script_lines if line.get("priority") == "core"]
    total_core = len(core_lines)

    in_trial_ranges = 0
    for line in core_lines:
        ovi = line.get("ovi")
        if type(ovi) is not int:
            continue
        for ts in trial_scenes:
            if ts["lo"] <= ovi <= ts["hi"]:
                in_trial_ranges += 1
                break

    core_lines_result = {"total": total_core, "in_trial_scene_ranges": in_trial_ranges}

    return {
        "omissions": omissions,
        "scenes": scenes,
        "scene_agreement": scene_agreement,
        "shots": shots,
        "images": images,
        "core_lines": core_lines_result,
        "problems": problems,
    }


def write_receipt(result: dict, out_path: Path | str, today: str | None = None) -> Path:
    """Write receipt JSON file."""
    path = Path(out_path)
    if path.exists():
        raise FileExistsError(f"receipt exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)

    output = dict(result)
    output["date"] = today or date.today().isoformat()
    output["note"] = "free Nemotron trial scored against the owner's real Adhyay 1 split; no Kimi call"

    with path.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=1, sort_keys=True, ensure_ascii=False)
    return path


def _print_table(result: dict) -> None:
    """Print a short readable table."""
    om = result["omissions"]
    sc = result["scenes"]
    sh = result["shots"]
    im = result["images"]
    cl = result["core_lines"]

    print("=== Stage 1 Trial vs Real (Adhyay 1) ===")
    print(f"Omissions:  trial={om['trial']} real={om['real']} both={om['both']}  "
          f"P={om['precision']} R={om['recall']} J={om['jaccard']}")
    print(f"Scenes:     trial={sc['trial']} real={sc['real']}  agreement={result['scene_agreement']}")
    print(f"Shots:      trial={sh['trial']} real={sh['real']}")
    print(f"Images:     trial={im['trial']} real={im['real']}")
    print(f"Core lines: total={cl['total']} in_trial_ranges={cl['in_trial_scene_ranges']}")
    if result["problems"]:
        print("Problems:")
        for p in result["problems"]:
            print(f"  - {p}")


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Score a Stage 1 trial against real Adhyay 1 split")
    parser.add_argument("--trial-dir", required=True, help="Path to trial directory")
    parser.add_argument("--root", default=None, help="Repo root (default: auto)")
    parser.add_argument("--receipt", default=None, help="Optional receipt output path")
    args = parser.parse_args(argv)

    if args.root is None:
        root = Path(__file__).resolve().parents[3]
    else:
        root = Path(args.root)

    trial_dir = Path(args.trial_dir)

    result = score(trial_dir, root)
    _print_table(result)

    if args.receipt:
        receipt_path = Path(args.receipt)
        try:
            write_receipt(result, receipt_path)
            print(f"Receipt written to {receipt_path}")
        except FileExistsError:
            print("refused: receipt exists")
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
