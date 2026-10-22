"""Phase E: Markdown research importer. Synthetic Markdown in the same shape as the real analysis
files; no Granth text is used. The importer must never invent, answer or approve anything."""
from __future__ import annotations

import pytest

from granthstudio import importer
from granthstudio.canon import load_canon
from granthstudio.cli import main
from granthstudio.config import dump_yaml, load_yaml
from granthstudio.errors import ConfigError, GateFailure, ResearchNotApproved
from granthstudio.importer import DRAFT_FILE, REPORT_FILE
from granthstudio.integrity import sha256_file
from granthstudio.research import adhyay_research_dir, approve, load_research

EPISODE_MD = """\
## 00. v3 web verification

Not part of the body.

# Synthetic Granth - Adhyay 1 - Analysis

## 1. Chapter overview

A synthetic overview line. It continues here.

---

## 2. Story list

### Frame (not counted as story)

- **A. Invocation** - ovi 1-4. Synthetic praise.

### Episode 1 - The first synthetic event

- **Ovi range:** 5-9.
- **Retelling:** SYNTH-A waits (ovi 5). SYNTH-B arrives (ovi 7-8) and the outcome is unclear.
- **Moral/teaching:** Synthetic moral.

### Episode 2 - The second synthetic event

- **Ovi range:** 10-12.
- **Retelling:** Another thing happens (ovi 11).

## 3. Characters

### 3.1 Story characters (named)

**SYNTH-A (सिंथ-ए) - synthetic host**
- **Role:** host
- Clothing: not mentioned.

**SYNTH-B Patil (सिंथ-बी), a neighbour**
- **Role:** guest, inferred from the verse

**Synth Patil**
- **Role:** another person with a shared name

## 4. Places, objects, time and season

### Places
- **Synth Village (सिंथगाव)**, a small village (ovi 3).

### Objects
- **Synth pot** (सिंथ, ovi 6): a pot.
- **Unsourced thing**: no reference given.

### Time and season
- **Season:** winter (inferred).

## 5. Open questions and uncertain words

1. **"term one" (ovi 8):** RESOLVED (user, 2026-10-22): a meaning that nobody re-checked.
2. **"term two" (ovi 9):** still unclear.
"""

SCENE_MD = """\
# Synthetic Granth - Adhyay 2 - Analysis

## 1. Chapter overview

Overview.

## 3. Characters

### 3.1 Story characters (named)

**SYNTH-A (सिंथ-ए)**
- **Role:** the same name in another chapter

## 6. Scene-by-scene breakdown (text only)

### Scene 1 - Synthetic opening (ovi 5-10)
- **Location:** a lane, "synthetic" (ovi 10).
- **Present:** SYNTH-A (alone).
- **Action beats:** (1) SYNTH-A walks (ovi 5). (2) SYNTH-A pauses.
- **Miracle:** none.

### Scene 2 - Synthetic talk (ovi 11-15)
- **Location:** a house.
- **Action beats:** (1) They speak (ovi 11-14).

## 7. Dialogue (who speaks to whom)

| Ovi | Speaker -> listener | Faithful paraphrase | Marathi anchor |
|---|---|---|---|
| 11-14 | SYNTH-A -> SYNTH-B | Why so restless? | "fragment one" (ovi 11) |
| 6 | SYNTH-B (unclear) -> himself | An aside. | "fragment two" (ovi 6) |
"""

QUESTIONS_MD = """\
# Open questions (synthetic)

# PART A: Open questions (answer these)

## Adhyay 1 (3 questions)

**A1-1** · ovi 8 · synthetic term
- Context: x
- Answer:

**A1-2b** [STILL-OPEN] · ovi 9-10 · another term
- Answer: a draft answer that must not be applied

**A1-3** [CONFLICT] · ovi 11 · conflicting term
- Answer:

## Adhyay 2 (1 question)

**A2-1** · ovi 5 · other chapter
- Answer:

# PART B: PROVISIONAL items (confirm or correct)

## Adhyay 1 (2)

**A1-10** [PROVISIONAL] · ovi 12 · provisional term
- Answer:

**A1-11** [PROVISIONAL, CORRECTED] · ovi 13 · corrected term
- Answer:
"""


@pytest.fixture
def md(tmp_path):
    files = {"episode": EPISODE_MD, "scene": SCENE_MD, "questions": QUESTIONS_MD}
    paths = {}
    for name, text in files.items():
        paths[name] = tmp_path / f"{name}.md"
        paths[name].write_text(text, encoding="utf-8")
    return paths


def report_for(project, md, adhyay=1, source="episode", questions=True, write=False, **kwargs):
    return importer.import_markdown(project, md[source], adhyay, md["questions"] if questions else None,
                                    kwargs.get("compare", []), kwargs.get("canon"), write)


def test_episodes_become_unfilled_scenes_with_no_invented_fields(project, md):
    parsed = importer.parse_markdown(md["episode"], 1)
    draft, todo = importer.build_draft(parsed, [])
    assert [s["scene_id"] for s in draft["scenes"]] == ["a01_s01", "a01_s02"]
    first = draft["scenes"][0]
    assert first["source_refs"] == ["ovi 5-9"] and first["description"].startswith("SYNTH-A waits (ovi 5).")
    assert first["location"] is None and first["characters"] == [] and first["dialogue"] == [] and first["visual_details"] == []
    assert draft["overview"].startswith("A synthetic overview line.")
    assert todo["scenes"]["a01_s01"]["moral"] == "Synthetic moral."
    assert todo["frame_sections"] == [{"label": "A", "title": "Invocation", "ovi": "1-4"}]
    assert "location" in todo["scenes"]["a01_s01"]["missing"] and "dialogue" in todo["scenes"]["a01_s01"]["missing"]


def test_scene_breakdown_supersedes_episodes_and_dialogue_text_is_never_filled(project, md):
    parsed = importer.parse_markdown(md["scene"], 2)
    draft, todo = importer.build_draft(parsed, [])
    scene = draft["scenes"][0]
    assert scene["scene_id"] == "a02_s01" and scene["source_refs"] == ["ovi 5-10"]
    assert [(a["id"], a["artistic"]) for a in scene["actions"]] == [("a02_s01_act01", False), ("a02_s01_act02", None)]
    assert scene["dialogue"] == [] and draft["scenes"][1]["dialogue"] == []
    rows = todo["dialogue"]
    assert [r["scene_id"] for r in rows] == ["a02_s02", "a02_s01"] and all(r["text"] is None for r in rows)
    assert "exact Marathi" in rows[0]["status"] and rows[1]["speaker_unclear"] is True
    assert rows[0]["marathi_anchor"] == '"fragment one" (ovi 11)'


def test_questions_are_never_answered_and_keep_every_item(project, md):
    parsed = importer.parse_markdown(md["episode"], 1)
    questions = importer.parse_questions(md["questions"], 1)
    assert [(q["id"], q["status"]) for q in questions] == [("A1-1", "open"), ("A1-2b", "open"), ("A1-3", "open"),
                                                           ("A1-10", "provisional"), ("A1-11", "provisional")]
    draft, _ = importer.build_draft(parsed, questions)
    by_id = {q["id"]: q for q in draft["open_questions"]}
    assert by_id["a01_n01"]["status"] == "provisional"  # source says RESOLVED: still needs a human
    assert by_id["a01_n02"]["status"] == "open" and by_id["a01_n01"]["ovi"] == "8"
    assert {q["status"] for q in draft["open_questions"]} == {"open", "provisional"}
    assert len(draft["open_questions"]) == 7


def test_identity_findings_flag_without_merging(project, md):
    canon = load_canon(project)
    report = report_for(project, md, canon=canon, compare=[(md["scene"], 2)])
    kinds = {(f["kind"], tuple(f["between"])) for f in report["identity_findings"]}
    assert any(kind == "shared_name_token" and "adhyay 1: SYNTH-B Patil" in between and "adhyay 1: Synth Patil" in between
               for kind, between in kinds)
    assert any(kind == "canon_match" and "chr_synth_a" in between for kind, between in kinds)
    assert any(kind == "same_name" and any("SYNTH-A" in b for b in between) for kind, between in kinds)
    assert all("nothing is merged" in f["detail"] or f["kind"].startswith("canon") for f in report["identity_findings"])


def test_dry_run_writes_nothing_and_write_creates_only_an_unloadable_draft(project, md):
    folder = adhyay_research_dir(project, 1)
    before = sorted(p.name for p in folder.iterdir())
    report = report_for(project, md)
    assert report["written"] is False and sorted(p.name for p in folder.iterdir()) == before
    assert report["approved"] is False and report["counts"]["answered"] == 0 and report["dialogue_text_imported"] == 0
    assert report["source_sha256"] == sha256_file(md["episode"])
    folder_new = adhyay_research_dir(project, 3)
    report3 = importer.import_markdown(project, md["episode"], 3, md["questions"], [], None, write=True)
    assert report3["written"] is True
    assert sorted(p.name for p in folder_new.iterdir()) == [REPORT_FILE, DRAFT_FILE]
    with pytest.raises(ConfigError, match="missing file"):
        load_research(project, 3)
    with pytest.raises(ConfigError):
        approve(project, 3, "synthetic-test-only", "2026-10-22T00:00:00+00:00")
    draft = load_yaml(folder_new / DRAFT_FILE)
    assert "_import" in draft and draft["adhyay"] == 3


def test_promotion_needs_a_complete_draft_and_is_not_approval(project, md, tmp_path):
    importer.import_markdown(project, md["episode"], 3, md["questions"], [], None, write=True)
    blockers = importer.draft_blockers(project, 3)
    assert any("_import block is still present" in b for b in blockers) and any(b.startswith("schema:") for b in blockers)
    with pytest.raises(GateFailure, match="draft is not ready"):
        importer.promote_draft(project, 3)
    # a human completes the draft: use the valid fixture research content, with its questions unresolved
    valid = load_yaml(adhyay_research_dir(project, 1) / "research.yaml")
    valid["adhyay"] = 3
    for scene in valid["scenes"]:
        scene["scene_id"] = scene["scene_id"].replace("a01_", "a03_")
    valid["open_questions"] = [{"id": "A3-1", "status": "open"}]
    dump_yaml(adhyay_research_dir(project, 3) / DRAFT_FILE, valid)
    assert importer.draft_blockers(project, 3) == []
    target = importer.promote_draft(project, 3)
    assert target.name == "research.yaml" and not (target.parent / DRAFT_FILE).exists()
    assert not (target.parent / "source_receipt.json").exists()
    with pytest.raises(ResearchNotApproved):
        approve(project, 3, "synthetic-test-only", "2026-10-22T00:00:00+00:00")  # the open question still blocks
    dump_yaml(target.parent / DRAFT_FILE, valid)
    with pytest.raises(GateFailure, match="already exists"):
        importer.promote_draft(project, 3)


def test_cli_import_check_and_promote(project, md, capsys):
    root = ["--root", str(project.root)]
    args = ["research", "import", str(md["scene"]), "--adhyay", "2", "--questions", str(md["questions"])]
    assert main([*root, *args]) == 0
    out = capsys.readouterr().out
    assert "2 scene(s)" in out and "dry run: nothing written" in out and "dialogue text imported: 0" in out
    assert main([*root, *args, "--write"]) == 0
    assert main([*root, "research", "check-draft", "2"]) == 2
    assert "blocker:" in capsys.readouterr().out
    assert main([*root, "research", "promote", "2"]) == 2
    assert main([*root, "research", "import", str(md["scene"]), "--adhyay", "2", "--compare", "bad"]) == 1
