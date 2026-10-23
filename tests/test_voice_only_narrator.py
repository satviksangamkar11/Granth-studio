"""A narrator is heard, never drawn: voice-only canon characters stay in the scene cast (speech is attributed to them) but not in any picture prompt or reference sheet."""
from __future__ import annotations

import yaml

from granthstudio import keyframes as kf
from granthstudio.config import load_models, load_yaml
from granthstudio.integrity import atomic_write_json
from granthstudio.pipeline import load_bundle
from granthstudio.research import approve
from tests.conftest import FIXED_TIME
from tests.test_keyframes import comfy, write_registry   # noqa: F401  (fixture import keeps the module self-contained)

NARRATOR = "chr_narrator_synth"


def add_narrator(project, voice_only=True):
    canon = project.canon_dir / "characters.yaml"
    document = load_yaml(canon)
    document["entries"].append({"id": NARRATOR, "canonical_name": "SYNTH-NARRATOR", "aliases": [], "status": "approved", **({"voice_only": True} if voice_only else {})})
    canon.write_text(yaml.safe_dump(document, allow_unicode=True, sort_keys=False), encoding="utf-8")
    research = project.research_dir / "adhyay_01" / "research.yaml"
    doc = load_yaml(research)
    scene = doc["scenes"][0]
    scene["characters"].append(NARRATOR)
    scene["dialogue"].append({"id": "d_0003", "speaker": NARRATOR, "text": "SYNTH narration line", "source_ref": "fixture:4"})
    research.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
    manifest_path = project.episodes_dir / "adhyay_01" / "manifest.yaml"
    manifest = load_yaml(manifest_path)
    manifest["scenes"][0]["characters"].append(NARRATOR)
    manifest["scenes"][0]["shots"][1]["dialogue_ids"].append("d_0003")
    atomic_write_json(manifest_path, manifest)
    for lang, text in (("mr", "SYNTH narration line"), ("hi", "SYNTH narration line HI")):
        path = project.episodes_dir / "adhyay_01" / f"{lang}.yaml"
        timeline = load_yaml(path)
        entry = {"dialogue_id": "d_0003", "shot_id": "a01_s01_sh02", "speaker": NARRATOR, "text": text}
        if lang == "hi":
            entry["alignment"] = {"mr_dialogue_id": "d_0003", "match": "adapted", "reviewed": True}
        timeline["entries"].append(entry)
        path.write_text(yaml.safe_dump(timeline, allow_unicode=True, sort_keys=False), encoding="utf-8")
        if lang == "hi":                         # re-seal the reviewer evidence the way the test fixtures do
            from tests.conftest import _dump
            _dump(path, load_yaml(path))


def test_a_voice_only_narrator_is_attributed_speech_but_never_drawn(project):
    add_narrator(project)
    approve(project, 1, "synthetic-tester", FIXED_TIME)
    bundle = load_bundle(project, load_models(project), 1)
    assert all(NARRATOR not in shot["characters"] for shot in bundle.compiled["shots"])             # not in any visual character list
    assert any(line["speaker"] == NARRATOR for scene in bundle.compiled["research_scenes"] for line in scene["dialogue"])   # but his line is in the approved research
    registry = kf.load_registry(project, bundle.canon)
    assert all(NARRATOR not in r.get("asset_id", "") for r in kf.sheet_requests(bundle.canon, registry, bundle.models))     # no reference sheet for him
    manifest = load_yaml(project.episodes_dir / "adhyay_01" / "manifest.yaml")
    assert NARRATOR in manifest["scenes"][0]["characters"]                                           # still part of the scene cast (research parity is enforced)


def test_without_the_flag_the_same_character_is_drawn_exactly_as_before(project):
    add_narrator(project, voice_only=False)
    approve(project, 1, "synthetic-tester", FIXED_TIME)
    bundle = load_bundle(project, load_models(project), 1)
    assert all(NARRATOR in shot["characters"] for shot in bundle.compiled["shots"])
    registry = kf.load_registry(project, bundle.canon)
    assert any(r.get("canon_id") == NARRATOR for r in kf.sheet_requests(bundle.canon, registry, bundle.models))


def test_a_voice_only_character_named_in_a_visible_action_is_refused(project):
    import pytest
    from granthstudio.errors import GateFailure
    add_narrator(project)
    research = project.research_dir / "adhyay_01" / "research.yaml"
    doc = load_yaml(research)
    doc["scenes"][0]["actions"][0]["text"] = "SYNTH-NARRATOR slight head turn"                   # the narrator would now be an actor
    research.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
    approve(project, 1, "synthetic-tester", FIXED_TIME)
    with pytest.raises(GateFailure, match="voice-only"):
        load_bundle(project, load_models(project), 1)
