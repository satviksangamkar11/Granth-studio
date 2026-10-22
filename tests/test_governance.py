"""Research approval, source-change detection, canon identity and the compiler's reference checks."""

from __future__ import annotations

import pytest

from granthstudio.canon import load_canon
from granthstudio.config import load_yaml
from granthstudio.episodes import compile_episode
from granthstudio.errors import (
    CanonReferenceError,
    ConfigError,
    IdentityConflict,
    ResearchNotApproved,
    SourceChanged,
)
from granthstudio.research import approve, require_approved, verify_source
from granthstudio.integrity import atomic_write_json
from tests.conftest import FIXED_TIME
from granthstudio.config import Project
from granthstudio.research import adhyay_research_dir
from granthstudio.schemas import validate_document


def _research_path(project: Project):
    return adhyay_research_dir(project, 1) / "research.yaml"


def test_approval_blocked_by_open_and_provisional_items(project):
    doc = load_yaml(_research_path(project))
    doc["open_questions"] = [{"id": "Q-open", "status": "open"}, {"id": "Q-prov", "status": "provisional"}]
    atomic_write_json(_research_path(project), doc)
    with pytest.raises(ResearchNotApproved, match="Q-open"):
        approve(project, 1, "tester", FIXED_TIME)
    assert verify_source(project, 1).approved is False


def test_approval_records_version_and_hash(project):
    receipt = approve(project, 1, "tester", FIXED_TIME)
    assert receipt["version"] == 1
    assert verify_source(project, 1).changed is False
    assert require_approved(project, 1)["version"] == 1


def test_edit_after_approval_is_detected_and_blocks(approved_project):
    doc = load_yaml(_research_path(approved_project))
    doc["scenes"][0]["dialogue"][0]["text"] = "SYNTH-A says 3 things"
    atomic_write_json(_research_path(approved_project), doc)
    assert verify_source(approved_project, 1).changed is True
    with pytest.raises(SourceChanged):
        require_approved(approved_project, 1)


def test_reapproval_creates_next_version(approved_project):
    doc = load_yaml(_research_path(approved_project))
    doc["scenes"][0]["dialogue"][0]["text"] = "SYNTH-A says 3 things"
    atomic_write_json(_research_path(approved_project), doc)
    receipt = approve(approved_project, 1, "tester", FIXED_TIME)
    assert receipt["version"] == 2


def test_canon_unresolved_possible_match_is_conflict(project):
    doc = load_yaml(project.canon_dir / "characters.yaml")
    doc["entries"][0]["possible_matches"] = ["chr_synth_b"]
    atomic_write_json(project.canon_dir / "characters.yaml", doc)
    with pytest.raises(IdentityConflict):
        load_canon(project)


def test_canon_shared_name_needs_different_decision(project):
    doc = load_yaml(project.canon_dir / "characters.yaml")
    doc["entries"][1]["aliases"] = ["SYN-A"]
    atomic_write_json(project.canon_dir / "characters.yaml", doc)
    with pytest.raises(IdentityConflict):
        load_canon(project)
    doc["identity_decisions"] = [{"ids": ["chr_synth_a", "chr_synth_b"], "decision": "different"}]
    atomic_write_json(project.canon_dir / "characters.yaml", doc)
    assert "chr_synth_b" in load_canon(project).entries


def test_canon_same_decision_refused_without_curated_merge(project):
    doc = load_yaml(project.canon_dir / "characters.yaml")
    doc["entries"][0]["possible_matches"] = ["chr_synth_b"]
    doc["identity_decisions"] = [{"ids": ["chr_synth_a", "chr_synth_b"], "decision": "same"}]
    atomic_write_json(project.canon_dir / "characters.yaml", doc)
    with pytest.raises(IdentityConflict):
        load_canon(project)


def test_pending_canon_entry_cannot_be_referenced(approved_project, models):
    doc = load_yaml(approved_project.canon_dir / "characters.yaml")
    doc["entries"][1]["status"] = "pending"
    atomic_write_json(approved_project.canon_dir / "characters.yaml", doc)
    with pytest.raises(CanonReferenceError, match="pending"):
        compile_episode(approved_project, models, load_canon(approved_project), 1,
                        _research(approved_project), require_approved(approved_project, 1))


def _research(project):
    from granthstudio.research import load_research
    return load_research(project, 1)


def _compile(project, models):
    return compile_episode(project, models, load_canon(project), 1, _research(project),
                           require_approved(project, 1))


def test_compile_is_deterministic(approved_project, models):
    assert _compile(approved_project, models) == _compile(approved_project, models)


def test_unknown_character_reference_blocked(approved_project, models):
    path = approved_project.episodes_dir / "adhyay_01" / "manifest.yaml"
    doc = load_yaml(path)
    doc["scenes"][0]["characters"].append("chr_ghost")
    atomic_write_json(path, doc)
    with pytest.raises(CanonReferenceError):
        _compile(approved_project, models)


def test_frames_must_match_pinned_list(approved_project, models):
    path = approved_project.episodes_dir / "adhyay_01" / "manifest.yaml"
    doc = load_yaml(path)
    doc["scenes"][0]["shots"][1]["frames"] = 50
    atomic_write_json(path, doc)
    with pytest.raises(ConfigError, match="frame_counts"):
        _compile(approved_project, models)


def test_manifest_research_version_mismatch_blocked(approved_project, models):
    path = approved_project.episodes_dir / "adhyay_01" / "manifest.yaml"
    doc = load_yaml(path)
    doc["research_version"] = 9
    validate_document("episode_manifest", doc)
    atomic_write_json(path, doc)
    with pytest.raises(SourceChanged):
        _compile(approved_project, models)


def test_speaker_must_belong_to_scene(approved_project, models):
    path = approved_project.episodes_dir / "adhyay_01" / "manifest.yaml"
    doc = load_yaml(path)
    doc["scenes"][0]["characters"] = ["chr_synth_a"]
    atomic_write_json(path, doc)
    with pytest.raises(CanonReferenceError, match="speaker"):
        _compile(approved_project, models)
