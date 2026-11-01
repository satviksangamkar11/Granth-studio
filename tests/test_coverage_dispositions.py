"""Owner-approved coverage dispositions and numbering exceptions (Phase B3c, 2026-11-01): they count only when approved, and only when they point at real lines."""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT / "scripts" / "pipeline"))

import approve  # type: ignore  # noqa: E402
import check_script  # type: ignore  # noqa: E402
import check_script_cli  # type: ignore  # noqa: E402

PHRASE = approve.CONFIRM_PHRASE
SCRIPT = (
    "## S1\n\n"
    "**S1-L1** | narrator | ovi 1 | core\n- Marathi: अ\n- Hindi: अ\n\n"
    "**S1-L3** | narrator | ovi 2 | optional\n- Marathi: ब\n- Hindi: ब\n\n"
    "**S1-L2** | narrator | ovi 3 | core\n- Marathi: क\n- Hindi: क\n\n"
)


def _root(tmp_path: Path, dispositions: dict | None, approve_it: bool) -> Path:
    root = tmp_path / "repo"
    base = root / "canon" / "adhyay_01"
    (base / "source").mkdir(parents=True)
    rows = [{"adhyay": 1, "ovi": i, "section": 1, "original_marathi": "x", "simple_marathi": "x", "hindi": "x", "easy_english": "x", "printed_number": i} for i in range(1, 6)]
    (base / "source" / "ovis.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    (base / "script").mkdir()
    (base / "script" / "easy.md").write_text(SCRIPT, encoding="utf-8")
    (root / "canon" / "series").mkdir(parents=True)
    (root / "canon" / "series" / "voices.json").write_text(json.dumps({"voices": []}), encoding="utf-8")
    (root / "assets" / "v5_presets").mkdir(parents=True)
    (root / "assets" / "v5_presets" / "index.json").write_text("[]", encoding="utf-8")
    (base / "stage1").mkdir()
    if dispositions is not None:
        f = base / "stage1" / "coverage_dispositions.json"
        f.write_text(json.dumps(dispositions), encoding="utf-8")
        if approve_it:
            approve.approve_file(1, "coverage_dispositions", f, "tester", root, confirm=PHRASE)
    return root


def _errors(root: Path) -> tuple[list[str], list[str]]:
    r = check_script_cli.run_check(1, root)
    return r["errors"], r["problems"]


GOOD = {"dispositions": [{"ovi": 2, "kind": "optional_line", "line": "S1-L3", "evidence": "own optional line"},
                         {"ovi": 4, "kind": "visual_only", "evidence": "shown in shot 1"},
                         {"ovi": 5, "kind": "merged", "line": "S1-L2", "evidence": "said in S1-L2"}],
        "numbering_exceptions": [{"lines": ["S1-L3", "S1-L2"], "reason": "ids name existing clips"}]}


def test_check_script_defaults_are_unchanged():
    lines = check_script.parse_script(SCRIPT)
    errs = check_script.check_script(lines, {1, 2, 3, 4}, set(), {"narrator"}, {})
    assert "ovi 2 has no core line" in errs and "ovi 4 has no core line" in errs
    assert any(e.startswith("S1-L3: line numbers") for e in errs) and any(e.startswith("S1-L2: line numbers") for e in errs)


def test_check_script_covered_and_exceptions_remove_only_what_they_name():
    lines = check_script.parse_script(SCRIPT)
    errs = check_script.check_script(lines, {1, 2, 3, 4}, set(), {"narrator"}, {}, covered_ovis={2}, numbering_exceptions={"S1-L3"})
    assert "ovi 2 has no core line" not in errs and "ovi 4 has no core line" in errs
    assert not any(e.startswith("S1-L3:") for e in errs) and any(e.startswith("S1-L2: line numbers") for e in errs)


def test_unapproved_dispositions_are_ignored_and_reported(tmp_path):
    errs, probs = _errors(_root(tmp_path, GOOD, approve_it=False))
    assert {"ovi 2 has no core line", "ovi 4 has no core line", "ovi 5 has no core line"} <= set(errs)
    assert any("dispositions: NOT_APPROVED" in p or "dispositions:" in p and "not approved" in p for p in probs)


def test_approved_dispositions_cover_and_clear_the_numbering(tmp_path):
    errs, probs = _errors(_root(tmp_path, GOOD, approve_it=True))
    assert errs == [] and probs == []


def test_a_changed_file_after_approval_is_ignored(tmp_path):
    root = _root(tmp_path, GOOD, approve_it=True)
    f = root / "canon" / "adhyay_01" / "stage1" / "coverage_dispositions.json"
    f.write_text(json.dumps({**GOOD, "numbering_exceptions": []}), encoding="utf-8")
    errs, probs = _errors(root)
    assert "ovi 4 has no core line" in errs and probs


def test_optional_line_must_be_that_ovis_optional_line_and_merged_must_exist(tmp_path):
    bad = {"dispositions": [{"ovi": 4, "kind": "optional_line", "line": "S1-L1", "evidence": "x"},
                            {"ovi": 5, "kind": "merged", "line": "S9-L9", "evidence": "x"}], "numbering_exceptions": []}
    errs, _ = _errors(_root(tmp_path, bad, approve_it=True))
    assert any("disposition ovi 4" in e for e in errs) and any("disposition ovi 5" in e for e in errs)
    assert "ovi 4 has no core line" in errs and "ovi 5 has no core line" in errs


def test_malformed_entries_mean_nothing_is_used(tmp_path):
    for bad in ({"dispositions": [{"ovi": 4, "kind": "research_only", "evidence": "x"}], "numbering_exceptions": []},
                {"dispositions": [{"ovi": 4, "kind": "visual_only", "evidence": " "}], "numbering_exceptions": []},
                {"dispositions": [{"ovi": True, "kind": "visual_only", "evidence": "x"}], "numbering_exceptions": []},
                {"dispositions": [], "numbering_exceptions": [{"lines": ["S1-L3"], "reason": ""}]}):
        errs, probs = _errors(_root(tmp_path / str(id(bad)), bad, approve_it=True))
        assert "ovi 4 has no core line" in errs and any(p.startswith("dispositions:") for p in probs), bad
