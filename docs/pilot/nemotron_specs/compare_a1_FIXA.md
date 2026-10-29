# FIX CALL: return BOTH files in full: `scripts/pipeline/stage1/compare_a1.py` and `tests/test_stage1_compare_a1.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
......F..............                                                    [100%]
================================== FAILURES ===================================
___________________ TestScore.test_synthetic_exact_numbers ____________________
tests\test_stage1_compare_a1.py:183: in test_synthetic_exact_numbers
    assert result["scenes"]["real"] == 2  # synthetic has 2 scenes
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   assert 9 == 2
============================== warnings summary ===============================
tests/test_stage1_compare_a1.py::TestRealFiles::test_real_unfilmed_contains_expected
  D:\aai work\granthstudio\.venv\Lib\site-packages\_pytest\fixtures.py:1313: PytestRemovedIn10Warning: Class-scoped fixture defined as instance method is deprecated.
  Instance attributes set in this fixture will NOT be visible to test methods,
  as each test gets a new instance while the fixture runs only once per class.
  Use @classmethod decorator and set attributes on cls instead.
  See https://docs.pytest.org/en/stable/deprecations.html#class-scoped-fixture-as-instance-method
    fixturefunc = resolve_fixture_function(fixturedef, request)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED tests/test_stage1_compare_a1.py::TestScore::test_synthetic_exact_numbers
1 failed, 20 passed, 1 warning in 0.27s

```

## SPEC
# SPEC: NEW `scripts/pipeline/stage1/compare_a1.py` + NEW `tests/test_stage1_compare_a1.py`. Return exactly these TWO files in full; do not output or change any other file.
Checklist row 19: score a free Stage 1 trial of Adhyay 1 against the owner's REAL, already-decided split (never repeat the paid Stage 1). Pure comparison, read only, writes one receipt. Standard library only; `from __future__ import annotations`; nothing at import time except imports and definitions; plain functions; no key or secret.

## Inputs (all paths relative to a `root`)
- The trial documents: a folder with `coverage.json` (`{"adhyay": 1, "ovis": [{"ovi", "disposition", ...}]}`), `scenes.json` (`{"scenes": [{"scene_id", "ovi_range": [lo, hi], "line_ids": [...]}]}`), `shots.json` (`{"shots": [...]}`), `briefs.json` (`{"images": [...]}`).
- The REAL decisions: (a) `canon/story_split_edits/A1_rev1.json`: `unfilmed_ranges` = list of `{"ovi_range": [lo, hi], ...}`: the real unfilmed ovis; (b) the real script `docs/pilot/A1_full_script_simple.md` parsed with `scripts/pipeline/check_script.py` `parse_script(text) -> list[dict]` (records `id, scene, ovi, priority`): the real scenes are the script's scenes and each real scene's ovis are the ovis of its lines; (c) the real image jobs `canon/drafts/A1_flow_shot_jobs.json` (a JSON list of 59 jobs); (d) the real planned shot count constant `REAL_SHOTS = 61` (from the owner's measured plan) and `REAL_SCENES = 9`.
Repo root in this module: `Path(__file__).resolve().parents[3]`; in tests `Path(__file__).resolve().parents[1]`.

## API
- `real_unfilmed(root) -> set[int]`: the union of the ranges in `unfilmed_ranges` (inclusive; the ranges are small: expand them with `range`, but ignore a range wider than 5000 or with non-int ends).
- `real_scenes(root) -> dict[str, set[int]]`: scene id (like `S1`) -> set of the ovis of its script lines.
- `score(trial_dir, root) -> dict`: NEVER raises; a missing or unreadable file gives the field `null` and an entry in `problems`. Returns `{"omissions": {"trial": n, "real": n, "both": n, "precision": float|null, "recall": float|null, "jaccard": float|null}, "scenes": {"trial": n, "real": 9, "per_real_scene": [{"scene": "S1", "ovis": n, "best_trial_scene": "S2"|null, "covered_fraction": float}]}, "scene_agreement": float|null, "shots": {"trial": n, "real": 61}, "images": {"trial": n, "real": 59}, "core_lines": {"total": n, "in_trial_scene_ranges": n}, "problems": [...]}` where: omissions compare the set of ovis with disposition PROPOSE_OMISSION (trial) against `real_unfilmed` (precision = both/trial, recall = both/real, jaccard = both/union; null when a denominator is 0); for each real scene its `covered_fraction` is the largest share of its ovis that lies inside ONE trial scene's inclusive `ovi_range` (never enumerate a trial range: test membership with lo <= ovi <= hi); `scene_agreement` is the mean of the covered fractions over the real scenes; `core_lines.in_trial_scene_ranges` counts the real core lines whose ovi lies in some trial scene range. Every float is rounded to 3 decimals.
- `write_receipt(result: dict, out_path: Path | str, today: str | None = None) -> Path`: writes json (indent 1, sort_keys, `ensure_ascii=False`) with `"date"` and `"note": "free Nemotron trial scored against the owner's real Adhyay 1 split; no Kimi call"`; raises `FileExistsError` if it exists; creates parent folders.
- `main(argv=None) -> int`: `--trial-dir DIR` (required), `--root PATH` (default repo root), `--receipt PATH` (optional). Prints a short readable table (omissions precision/recall, scene agreement, counts trial vs real) and returns 0; with `--receipt` writes it (an existing file -> `refused: receipt exists`, return 2).

## Tests (`tests/test_stage1_compare_a1.py`; synthetic data in tmp_path plus real-file tests)
1. Build a synthetic root with a tiny `A1_rev1.json` (unfilmed ranges [1,3] and [8,8]), a script in the REAL EASY format (`## S1`, `**S1-L1** | narrator | ovi 4 | core`, `- Marathi: ..`, `- Hindi: ..`; two scenes), `canon/drafts/A1_flow_shot_jobs.json` as a list of 3 items, and a trial dir with the four documents. Check exact numbers: omissions precision/recall/jaccard on hand-computed sets; each real scene's covered fraction; the mean agreement; counts; core lines.
2. Edge cases each isolated: an empty trial omission set (precision null, recall 0.0), identical sets (all 1.0), disjoint sets (jaccard 0.0), a trial scene with a huge range `[1, 10**12]` (fast, no enumeration), missing trial files -> null fields and problems, a corrupt JSON file -> problem not exception.
3. `write_receipt` content and the refusal on a second write; `main` output and return codes (capsys).
4. REAL files (skipif a file is missing): `real_unfilmed(ROOT)` contains ovi 1 and 32 and 145 and does not contain 70; `real_scenes(ROOT)` has 9 scenes; `score(trial_dir, ROOT)` on a tiny fake trial dir does not raise.
Use plain assignment and `copy.deepcopy`; never a helper that rejects no-effect mutations.

Reply with only the two FILE blocks:
FILE: scripts/pipeline/stage1/compare_a1.py
FILE: tests/test_stage1_compare_a1.py


## CURRENT MODULE scripts/pipeline/stage1/compare_a1.py
```python
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


def real_unfilmed(root: Path) -> set[int]:
    """Return the set of real unfilmed ovis from A1_rev1.json."""
    path = root / "canon" / "story_split_edits" / "A1_rev1.json"
    result: set[int] = set()
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return result

    unfilmed_ranges = data.get("unfilmed_ranges", [])
    for item in unfilmed_ranges:
        ovi_range = item.get("ovi_range")
        if not isinstance(ovi_range, list) or len(ovi_range) != 2:
            continue
        lo, hi = ovi_range
        if not isinstance(lo, int) or not isinstance(hi, int):
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
    scenes: dict[str, set[int]] = {}
    for line in lines:
        scene_id = line.get("scene")
        ovi = line.get("ovi")
        if scene_id is None or ovi is None:
            continue
        if not isinstance(scene_id, str) or not isinstance(ovi, int):
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
    if coverage_data and isinstance(coverage_data, dict):
        ovis = coverage_data.get("ovis", [])
        if isinstance(ovis, list):
            for item in ovis:
                if isinstance(item, dict) and item.get("disposition") == "PROPOSE_OMISSION":
                    ovi = item.get("ovi")
                    if isinstance(ovi, int):
                        trial_omissions.add(ovi)

    real_omissions = real_unfilmed(root)
    both = trial_omissions & real_omissions
    union = trial_omissions | real_omissions

    trial_count = len(trial_omissions)
    real_count = len(real_omissions)
    both_count = len(both)
    union_count = len(union)

    precision = _round3(both_count / trial_count) if trial_count else None
    recall = _round3(both_count / real_count) if real_count else None
    jaccard = _round3(both_count / union_count) if union_count else None

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
    if scenes_data and isinstance(scenes_data, dict):
        scenes_list = scenes_data.get("scenes", [])
        if isinstance(scenes_list, list):
            for s in scenes_list:
                if isinstance(s, dict):
                    scene_id = s.get("scene_id")
                    ovi_range = s.get("ovi_range")
                    if isinstance(scene_id, str) and isinstance(ovi_range, list) and len(ovi_range) == 2:
                        lo, hi = ovi_range
                        if isinstance(lo, int) and isinstance(hi, int) and lo <= hi:
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

    scene_agreement = _round3(sum(covered_fractions) / len(covered_fractions)) if covered_fractions else None

    scenes = {
        "trial": len(trial_scenes),
        "real": REAL_SCENES,
        "per_real_scene": per_real_scene,
    }

    # --- Shots ---
    trial_shots = 0
    if shots_data and isinstance(shots_data, dict):
        shots_list = shots_data.get("shots", [])
        if isinstance(shots_list, list):
            trial_shots = len(shots_list)

    shots = {"trial": trial_shots, "real": REAL_SHOTS}

    # --- Images ---
    trial_images = 0
    if briefs_data and isinstance(briefs_data, dict):
        images_list = briefs_data.get("images", [])
        if isinstance(images_list, list):
            trial_images = len(images_list)

    images = {"trial": trial_images, "real": 59}

    # --- Core lines ---
    script_lines = parse_script((root / "docs" / "pilot" / "A1_full_script_simple.md").read_text(encoding="utf-8")) if (root / "docs" / "pilot" / "A1_full_script_simple.md").exists() else []
    core_lines = [line for line in script_lines if line.get("priority") == "core"]
    total_core = len(core_lines)

    in_trial_ranges = 0
    for line in core_lines:
        ovi = line.get("ovi")
        if not isinstance(ovi, int):
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

```

## CURRENT TESTS tests/test_stage1_compare_a1.py
```python
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from scripts.pipeline.stage1.compare_a1 import (
    real_unfilmed,
    real_scenes,
    score,
    write_receipt,
    main,
    REAL_SHOTS,
    REAL_SCENES,
)


def _make_synthetic_root(tmp: Path) -> Path:
    """Create a synthetic root with minimal real files."""
    root = tmp / "repo"
    # canon/story_split_edits/A1_rev1.json
    canon_dir = root / "canon" / "story_split_edits"
    canon_dir.mkdir(parents=True)
    (canon_dir / "A1_rev1.json").write_text(json.dumps({
        "unfilmed_ranges": [
            {"ovi_range": [1, 3]},
            {"ovi_range": [8, 8]},
        ]
    }), encoding="utf-8")

    # docs/pilot/A1_full_script_simple.md (REAL EASY format)
    docs_dir = root / "docs" / "pilot"
    docs_dir.mkdir(parents=True)
    script_content = """## S1
**S1-L1** | narrator | ovi 4 | core
- Marathi: line 1
- Hindi: line 1
**S1-L2** | narrator | ovi 5 | core
- Marathi: line 2
- Hindi: line 2
**S1-L3** | narrator | ovi 6 | support
- Marathi: line 3
- Hindi: line 3

## S2
**S2-L1** | narrator | ovi 7 | core
- Marathi: line 4
- Hindi: line 4
**S2-L2** | narrator | ovi 9 | core
- Marathi: line 5
- Hindi: line 5
"""
    (docs_dir / "A1_full_script_simple.md").write_text(script_content, encoding="utf-8")

    # canon/drafts/A1_flow_shot_jobs.json
    drafts_dir = root / "canon" / "drafts"
    drafts_dir.mkdir(parents=True)
    (drafts_dir / "A1_flow_shot_jobs.json").write_text(json.dumps([{}, {}, {}]), encoding="utf-8")

    return root


def _make_trial_dir(tmp: Path, coverage_ovis: list[dict], scenes: list[dict], shots_count: int, images_count: int) -> Path:
    """Create a trial directory with the four documents."""
    trial = tmp / "trial"
    trial.mkdir()

    (trial / "coverage.json").write_text(json.dumps({
        "adhyay": 1,
        "ovis": coverage_ovis
    }), encoding="utf-8")

    (trial / "scenes.json").write_text(json.dumps({
        "scenes": scenes
    }), encoding="utf-8")

    (trial / "shots.json").write_text(json.dumps({
        "shots": [{} for _ in range(shots_count)]
    }), encoding="utf-8")

    (trial / "briefs.json").write_text(json.dumps({
        "images": [{} for _ in range(images_count)]
    }), encoding="utf-8")

    return trial


class TestRealUnfilmed:
    def test_synthetic(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_synthetic_root(Path(tmp))
            result = real_unfilmed(root)
            assert result == {1, 2, 3, 8}

    def test_ignores_wide_range(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            canon_dir = root / "canon" / "story_split_edits"
            canon_dir.mkdir(parents=True)
            (canon_dir / "A1_rev1.json").write_text(json.dumps({
                "unfilmed_ranges": [{"ovi_range": [1, 10000]}]
            }), encoding="utf-8")
            result = real_unfilmed(root)
            assert result == set()

    def test_ignores_non_int_ends(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            canon_dir = root / "canon" / "story_split_edits"
            canon_dir.mkdir(parents=True)
            (canon_dir / "A1_rev1.json").write_text(json.dumps({
                "unfilmed_ranges": [{"ovi_range": [1, "x"]}]
            }), encoding="utf-8")
            result = real_unfilmed(root)
            assert result == set()

    def test_missing_file_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            result = real_unfilmed(root)
            assert result == set()


class TestRealScenes:
    def test_synthetic(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_synthetic_root(Path(tmp))
            result = real_scenes(root)
            assert result == {
                "S1": {4, 5, 6},
                "S2": {7, 9},
            }

    def test_missing_file_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            result = real_scenes(root)
            assert result == {}


class TestScore:
    def test_synthetic_exact_numbers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_synthetic_root(Path(tmp))
            trial = _make_trial_dir(Path(tmp), coverage_ovis=[
                {"ovi": 1, "disposition": "PROPOSE_OMISSION"},
                {"ovi": 2, "disposition": "PROPOSE_OMISSION"},
                {"ovi": 8, "disposition": "PROPOSE_OMISSION"},
                {"ovi": 99, "disposition": "PROPOSE_OMISSION"},
                {"ovi": 4, "disposition": "KEEP"},
            ], scenes=[
                {"scene_id": "T1", "ovi_range": [4, 6], "line_ids": ["S1-L1", "S1-L2", "S1-L3"]},
                {"scene_id": "T2", "ovi_range": [7, 9], "line_ids": ["S2-L1", "S2-L2"]},
            ], shots_count=5, images_count=4)

            result = score(trial, root)

            # Omissions: trial={1,2,8,99}, real={1,2,3,8}, both={1,2,8}, union={1,2,3,8,99}
            assert result["omissions"]["trial"] == 4
            assert result["omissions"]["real"] == 4
            assert result["omissions"]["both"] == 3
            assert result["omissions"]["precision"] == 0.750
            assert result["omissions"]["recall"] == 0.750
            assert result["omissions"]["jaccard"] == 0.600

            # Scenes: real S1={4,5,6}, S2={7,9}
            # T1 covers [4,6] -> S1: 3/3=1.0, S2: 0/2=0.0
            # T2 covers [7,9] -> S1: 0/3=0.0, S2: 2/2=1.0
            per_scene = result["scenes"]["per_real_scene"]
            assert len(per_scene) == 2
            s1 = next(p for p in per_scene if p["scene"] == "S1")
            s2 = next(p for p in per_scene if p["scene"] == "S2")
            assert s1["ovis"] == 3
            assert s1["best_trial_scene"] == "T1"
            assert s1["covered_fraction"] == 1.000
            assert s2["ovis"] == 2
            assert s2["best_trial_scene"] == "T2"
            assert s2["covered_fraction"] == 1.000
            assert result["scene_agreement"] == 1.000
            assert result["scenes"]["trial"] == 2
            assert result["scenes"]["real"] == 2  # synthetic has 2 scenes

            assert result["shots"]["trial"] == 5
            assert result["shots"]["real"] == REAL_SHOTS
            assert result["images"]["trial"] == 4
            assert result["images"]["real"] == 59

            # Core lines: S1-L1(ovi4), S1-L2(ovi5), S2-L1(ovi7), S2-L2(ovi9) = 4 core
            # All 4 are in trial ranges [4,6] and [7,9]
            assert result["core_lines"]["total"] == 4
            assert result["core_lines"]["in_trial_scene_ranges"] == 4

    def test_empty_trial_omissions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_synthetic_root(Path(tmp))
            trial = _make_trial_dir(Path(tmp), coverage_ovis=[
                {"ovi": 4, "disposition": "KEEP"},
            ], scenes=[], shots_count=0, images_count=0)

            result = score(trial, root)
            om = result["omissions"]
            assert om["trial"] == 0
            assert om["real"] == 4
            assert om["both"] == 0
            assert om["precision"] is None
            assert om["recall"] == 0.0
            assert om["jaccard"] == 0.0

    def test_identical_omission_sets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_synthetic_root(Path(tmp))
            trial = _make_trial_dir(Path(tmp), coverage_ovis=[
                {"ovi": 1, "disposition": "PROPOSE_OMISSION"},
                {"ovi": 2, "disposition": "PROPOSE_OMISSION"},
                {"ovi": 3, "disposition": "PROPOSE_OMISSION"},
                {"ovi": 8, "disposition": "PROPOSE_OMISSION"},
            ], scenes=[], shots_count=0, images_count=0)

            result = score(trial, root)
            om = result["omissions"]
            assert om["precision"] == 1.0
            assert om["recall"] == 1.0
            assert om["jaccard"] == 1.0

    def test_disjoint_omission_sets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_synthetic_root(Path(tmp))
            trial = _make_trial_dir(Path(tmp), coverage_ovis=[
                {"ovi": 100, "disposition": "PROPOSE_OMISSION"},
                {"ovi": 200, "disposition": "PROPOSE_OMISSION"},
            ], scenes=[], shots_count=0, images_count=0)

            result = score(trial, root)
            om = result["omissions"]
            assert om["precision"] == 0.0
            assert om["recall"] == 0.0
            assert om["jaccard"] == 0.0

    def test_huge_trial_scene_range_fast(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_synthetic_root(Path(tmp))
            trial = _make_trial_dir(Path(tmp), coverage_ovis=[], scenes=[
                {"scene_id": "HUGE", "ovi_range": [1, 10**12], "line_ids": []},
            ], shots_count=0, images_count=0)

            result = score(trial, root)
            # Should not hang, should compute correctly
            s1 = next(p for p in result["scenes"]["per_real_scene"] if p["scene"] == "S1")
            s2 = next(p for p in result["scenes"]["per_real_scene"] if p["scene"] == "S2")
            assert s1["covered_fraction"] == 1.0
            assert s2["covered_fraction"] == 1.0

    def test_missing_trial_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_synthetic_root(Path(tmp))
            trial = Path(tmp) / "trial"
            trial.mkdir()
            # No files created

            result = score(trial, root)
            assert result["omissions"]["trial"] == 0
            assert result["scenes"]["trial"] == 0
            assert result["shots"]["trial"] == 0
            assert result["images"]["trial"] == 0
            assert len(result["problems"]) == 4
            assert all("missing" in p for p in result["problems"])

    def test_corrupt_json_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_synthetic_root(Path(tmp))
            trial = _make_trial_dir(Path(tmp), coverage_ovis=[], scenes=[], shots_count=0, images_count=0)
            (trial / "coverage.json").write_text("{ not json }", encoding="utf-8")

            result = score(trial, root)
            assert any("corrupt" in p and "coverage.json" in p for p in result["problems"])
            # Should not raise


class TestWriteReceipt:
    def test_write_receipt_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "receipt.json"
            result = {"omissions": {"trial": 1}, "test": "value"}
            write_receipt(result, out, today="2025-01-15")

            data = json.loads(out.read_text(encoding="utf-8"))
            assert data["date"] == "2025-01-15"
            assert data["note"] == "free Nemotron trial scored against the owner's real Adhyay 1 split; no Kimi call"
            assert data["omissions"]["trial"] == 1
            assert data["test"] == "value"

    def test_write_receipt_refusal_on_existing(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "receipt.json"
            out.write_text("{}", encoding="utf-8")
            with pytest.raises(FileExistsError):
                write_receipt({}, out)


class TestMain:
    def test_main_output_and_return_code(self, capsys):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_synthetic_root(Path(tmp))
            trial = _make_trial_dir(Path(tmp), coverage_ovis=[
                {"ovi": 1, "disposition": "PROPOSE_OMISSION"},
            ], scenes=[], shots_count=0, images_count=0)

            rc = main(["--trial-dir", str(trial), "--root", str(root)])
            assert rc == 0
            out = capsys.readouterr().out
            assert "Stage 1 Trial vs Real" in out
            assert "Omissions:" in out

    def test_main_with_receipt_write(self, capsys):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_synthetic_root(Path(tmp))
            trial = _make_trial_dir(Path(tmp), coverage_ovis=[], scenes=[], shots_count=0, images_count=0)
            receipt = Path(tmp) / "receipt.json"

            rc = main(["--trial-dir", str(trial), "--root", str(root), "--receipt", str(receipt)])
            assert rc == 0
            assert receipt.exists()

    def test_main_receipt_refusal(self, capsys):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_synthetic_root(Path(tmp))
            trial = _make_trial_dir(Path(tmp), coverage_ovis=[], scenes=[], shots_count=0, images_count=0)
            receipt = Path(tmp) / "receipt.json"
            receipt.write_text("{}", encoding="utf-8")

            rc = main(["--trial-dir", str(trial), "--root", str(root), "--receipt", str(receipt)])
            assert rc == 2
            out = capsys.readouterr().out
            assert "refused: receipt exists" in out


class TestRealFiles:
    @pytest.fixture(scope="class")
    def repo_root(self) -> Path:
        return Path(__file__).resolve().parents[1]

    def test_real_unfilmed_contains_expected(self, repo_root):
        # Skip if real file missing
        path = repo_root / "canon" / "story_split_edits" / "A1_rev1.json"
        if not path.exists():
            pytest.skip("Real A1_rev1.json not found")
        result = real_unfilmed(repo_root)
        assert 1 in result
        assert 32 in result
        assert 145 in result
        assert 70 not in result

    def test_real_scenes_has_9_scenes(self, repo_root):
        path = repo_root / "docs" / "pilot" / "A1_full_script_simple.md"
        if not path.exists():
            pytest.skip("Real script not found")
        result = real_scenes(repo_root)
        assert len(result) == 9

    def test_score_on_fake_trial_does_not_raise(self, repo_root):
        path = repo_root / "docs" / "pilot" / "A1_full_script_simple.md"
        if not path.exists():
            pytest.skip("Real script not found")
        with tempfile.TemporaryDirectory() as tmp:
            trial = _make_trial_dir(Path(tmp), coverage_ovis=[], scenes=[], shots_count=0, images_count=0)
            result = score(trial, repo_root)
            assert "omissions" in result
            assert "scenes" in result

```
