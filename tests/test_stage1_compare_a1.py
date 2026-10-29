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

    # Regression test for defect 1: real_unfilmed guards against non-dict data and non-dict items
    def test_top_level_list_does_not_raise(self):
        """A1_rev1.json containing a top-level list must not raise AttributeError."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            canon_dir = root / "canon" / "story_split_edits"
            canon_dir.mkdir(parents=True)
            # Top-level list instead of dict
            (canon_dir / "A1_rev1.json").write_text(json.dumps([
                {"ovi_range": [1, 3]},
                {"ovi_range": [8, 8]},
            ]), encoding="utf-8")
            # Old behavior: AttributeError: 'list' object has no attribute 'get'
            # New behavior: returns empty set
            result = real_unfilmed(root)
            assert result == set()

    def test_string_item_in_unfilmed_ranges_does_not_raise(self):
        """An unfilmed_ranges item that is a string must not raise AttributeError."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            canon_dir = root / "canon" / "story_split_edits"
            canon_dir.mkdir(parents=True)
            # One valid item, one string item
            (canon_dir / "A1_rev1.json").write_text(json.dumps({
                "unfilmed_ranges": [
                    {"ovi_range": [1, 3]},
                    "not a dict",
                ]
            }), encoding="utf-8")
            # Old behavior: AttributeError: 'str' object has no attribute 'get'
            # New behavior: skips the string, processes the valid dict
            result = real_unfilmed(root)
            assert result == {1, 2, 3}


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
            # FIXED: scenes.real is now the constant REAL_SCENES = 9 (spec), not len(real_scenes_map)
            assert result["scenes"]["real"] == REAL_SCENES

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
            # When files are missing, trial fields are None (not 0)
            assert result["omissions"]["trial"] is None
            assert result["omissions"]["precision"] is None
            assert result["omissions"]["recall"] is None
            assert result["omissions"]["jaccard"] is None
            assert result["scenes"]["trial"] is None
            assert result["scene_agreement"] is None
            assert result["shots"]["trial"] is None
            assert result["images"]["trial"] is None
            assert len(result["problems"]) == 4
            assert all("missing" in p for p in result["problems"])

    def test_missing_coverage_only(self):
        """Only coverage.json missing: omissions trial fields None, others have values."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_synthetic_root(Path(tmp))
            trial = Path(tmp) / "trial"
            trial.mkdir()
            # Create only scenes.json, shots.json, briefs.json
            (trial / "scenes.json").write_text(json.dumps({"scenes": []}), encoding="utf-8")
            (trial / "shots.json").write_text(json.dumps({"shots": []}), encoding="utf-8")
            (trial / "briefs.json").write_text(json.dumps({"images": []}), encoding="utf-8")

            result = score(trial, root)
            # Omissions: trial fields None
            assert result["omissions"]["trial"] is None
            assert result["omissions"]["precision"] is None
            assert result["omissions"]["recall"] is None
            assert result["omissions"]["jaccard"] is None
            # Scenes: readable
            assert result["scenes"]["trial"] == 0
            assert result["scene_agreement"] is not None
            # Shots: readable
            assert result["shots"]["trial"] == 0
            # Images: readable
            assert result["images"]["trial"] == 0
            # Problems: only coverage missing
            missing_problems = [p for p in result["problems"] if "missing" in p and "coverage.json" in p]
            assert len(missing_problems) == 1

    def test_missing_scenes_only(self):
        """Only scenes.json missing: scenes trial fields None, others have values."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_synthetic_root(Path(tmp))
            trial = Path(tmp) / "trial"
            trial.mkdir()
            # Create only coverage.json, shots.json, briefs.json
            (trial / "coverage.json").write_text(json.dumps({"adhyay": 1, "ovis": []}), encoding="utf-8")
            (trial / "shots.json").write_text(json.dumps({"shots": []}), encoding="utf-8")
            (trial / "briefs.json").write_text(json.dumps({"images": []}), encoding="utf-8")

            result = score(trial, root)
            # Omissions: readable
            assert result["omissions"]["trial"] == 0
            assert result["omissions"]["precision"] is None
            assert result["omissions"]["recall"] == 0.0
            # Scenes: trial fields None
            assert result["scenes"]["trial"] is None
            assert result["scene_agreement"] is None
            # Shots: readable
            assert result["shots"]["trial"] == 0
            # Images: readable
            assert result["images"]["trial"] == 0
            # Problems: only scenes missing
            missing_problems = [p for p in result["problems"] if "missing" in p and "scenes.json" in p]
            assert len(missing_problems) == 1

    def test_missing_shots_only(self):
        """Only shots.json missing: shots.trial None, others have values."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_synthetic_root(Path(tmp))
            trial = Path(tmp) / "trial"
            trial.mkdir()
            # Create only coverage.json, scenes.json, briefs.json
            (trial / "coverage.json").write_text(json.dumps({"adhyay": 1, "ovis": []}), encoding="utf-8")
            (trial / "scenes.json").write_text(json.dumps({"scenes": []}), encoding="utf-8")
            (trial / "briefs.json").write_text(json.dumps({"images": []}), encoding="utf-8")

            result = score(trial, root)
            # Omissions: readable
            assert result["omissions"]["trial"] == 0
            assert result["omissions"]["precision"] is None
            assert result["omissions"]["recall"] == 0.0
            # Scenes: readable
            assert result["scenes"]["trial"] == 0
            assert result["scene_agreement"] is not None
            # Shots: trial None
            assert result["shots"]["trial"] is None
            # Images: readable
            assert result["images"]["trial"] == 0
            # Problems: only shots missing
            missing_problems = [p for p in result["problems"] if "missing" in p and "shots.json" in p]
            assert len(missing_problems) == 1

    def test_missing_briefs_only(self):
        """Only briefs.json missing: images.trial None, others have values."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_synthetic_root(Path(tmp))
            trial = Path(tmp) / "trial"
            trial.mkdir()
            # Create only coverage.json, scenes.json, shots.json
            (trial / "coverage.json").write_text(json.dumps({"adhyay": 1, "ovis": []}), encoding="utf-8")
            (trial / "scenes.json").write_text(json.dumps({"scenes": []}), encoding="utf-8")
            (trial / "shots.json").write_text(json.dumps({"shots": []}), encoding="utf-8")

            result = score(trial, root)
            # Omissions: readable
            assert result["omissions"]["trial"] == 0
            assert result["omissions"]["precision"] is None
            assert result["omissions"]["recall"] == 0.0
            # Scenes: readable
            assert result["scenes"]["trial"] == 0
            assert result["scene_agreement"] is not None
            # Shots: readable
            assert result["shots"]["trial"] == 0
            # Images: trial None
            assert result["images"]["trial"] is None
            # Problems: only briefs missing
            missing_problems = [p for p in result["problems"] if "missing" in p and "briefs.json" in p]
            assert len(missing_problems) == 1

    def test_corrupt_json_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_synthetic_root(Path(tmp))
            trial = _make_trial_dir(Path(tmp), coverage_ovis=[], scenes=[], shots_count=0, images_count=0)
            (trial / "coverage.json").write_text("{ not json }", encoding="utf-8")

            result = score(trial, root)
            assert any("corrupt" in p and "coverage.json" in p for p in result["problems"])
            # Should not raise

    # Regression test for defect 2: score() guards script read with try/except
    def test_non_utf8_script_does_not_raise(self):
        """A non-UTF-8 A1_full_script_simple.md must not raise UnicodeDecodeError out of score()."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            # canon/story_split_edits/A1_rev1.json
            canon_dir = root / "canon" / "story_split_edits"
            canon_dir.mkdir(parents=True)
            (canon_dir / "A1_rev1.json").write_text(json.dumps({
                "unfilmed_ranges": [{"ovi_range": [1, 3]}]
            }), encoding="utf-8")

            # docs/pilot/A1_full_script_simple.md with invalid UTF-8
            docs_dir = root / "docs" / "pilot"
            docs_dir.mkdir(parents=True)
            # Write raw bytes that are not valid UTF-8
            (docs_dir / "A1_full_script_simple.md").write_bytes(b"\xff\xfe\x00\x00")

            trial = _make_trial_dir(Path(tmp), coverage_ovis=[], scenes=[], shots_count=0, images_count=0)

            # Old behavior: UnicodeDecodeError raised from score()
            # New behavior: returns result with problems list containing the error, script_lines = []
            result = score(trial, root)
            assert "core_lines" in result
            assert result["core_lines"]["total"] == 0
            assert result["core_lines"]["in_trial_scene_ranges"] == 0
            assert any("corrupt" in p and "A1_full_script_simple.md" in p for p in result["problems"])

    # Regression test for defect 3: scenes.real uses REAL_SCENES constant (9)
    def test_scenes_real_uses_constant_not_map_length(self):
        """scenes.real must be REAL_SCENES (9) even when script is missing or has fewer scenes."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            # canon/story_split_edits/A1_rev1.json
            canon_dir = root / "canon" / "story_split_edits"
            canon_dir.mkdir(parents=True)
            (canon_dir / "A1_rev1.json").write_text(json.dumps({
                "unfilmed_ranges": []
            }), encoding="utf-8")

            # docs/pilot/A1_full_script_simple.md with only 2 scenes (synthetic)
            docs_dir = root / "docs" / "pilot"
            docs_dir.mkdir(parents=True)
            script_content = """## S1
**S1-L1** | narrator | ovi 4 | core
- Marathi: line 1
- Hindi: line 1

## S2
**S2-L1** | narrator | ovi 7 | core
- Marathi: line 4
- Hindi: line 4
"""
            (docs_dir / "A1_full_script_simple.md").write_text(script_content, encoding="utf-8")

            trial = _make_trial_dir(Path(tmp), coverage_ovis=[], scenes=[], shots_count=0, images_count=0)

            result = score(trial, root)
            # Old behavior: scenes.real == len(real_scenes_map) == 2
            # New behavior: scenes.real == REAL_SCENES == 9
            assert result["scenes"]["real"] == REAL_SCENES
            assert result["scenes"]["real"] == 9


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
