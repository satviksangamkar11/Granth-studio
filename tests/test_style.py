"""The frozen provisional global style: exact prompt composition, sealing, no drift, same style for both languages."""
from __future__ import annotations

import shutil

import pytest
import yaml

from granthstudio import keyframes as kf
from granthstudio import style as st
from granthstudio.config import load_models, load_project
from granthstudio.errors import ConfigError, GateFailure
from granthstudio.pipeline import load_bundle, plan_tasks, snapshot
from granthstudio.scheduler import Scheduler
from tests.conftest import REPO, have_tool
from tests.test_keyframes import comfy, kf_project, request_for, write_registry   # noqa: F401  (fixtures)

pytestmark = pytest.mark.skipif(not (have_tool("ffmpeg") and have_tool("ffprobe")), reason="media tools missing")
REAL = REPO / "canon" / "style.yaml"
PREFIX = ("1950s vintage Indian devotional book illustration, authentic mid-century opaque gouache and egg tempera painting on aged matte ivory cardstock, "
          "soft hand-painted sepia contour linework, chalky matte gouache wash shading, flat hand-brushed tonal planes,")
SUFFIX = ("warm natural mineral pigments of raw sienna, burnt umber, warm ochre, terracotta, and muted sage green, subtle paper grain texture, "
          "vintage double-line paper border mount, clean traditional graphic composition, text-free, no labels, no watermarks.")
NEGATIVE = ("photorealistic, 3D render, CGI, digital painting gloss, airbrushed gradients, shiny plastic skin, modern photography, harsh lens flare, neon colors, "
            "oil impasto, heavy black comic ink, blurry contours, text, typography, signature, watermarks.")


def install_style(project, reseal=True, **changes):
    document = yaml.safe_load(REAL.read_text(encoding="utf-8"))
    for key, value in changes.items():
        if isinstance(value, dict) and isinstance(document.get(key), dict):
            document[key] = {**document[key], **value}
        else:
            document[key] = value
    if reseal:
        document["content_sha256"] = st.seal(document)
    (project.canon_dir / "style.yaml").write_text(yaml.safe_dump(document, allow_unicode=True, sort_keys=False, width=10000), encoding="utf-8")


def frozen_project(project):
    write_registry(project, style=None)
    shutil.copyfile(REAL, project.canon_dir / "style.yaml")
    return project


def test_the_shipped_style_is_exactly_the_one_the_owner_froze():
    document = yaml.safe_load(REAL.read_text(encoding="utf-8"))
    assert (document["style_id"], document["status"], document["version"]) == ("devotional_gouache_1950s_v1", "frozen", 1)
    assert (document["scope"], document["approved_by"], str(document["approved_on"])) == ("global", "Satvik Sangamkar", "2026-10-23")
    positive = document["positive_style"]
    assert positive["prefix"] == PREFIX and positive["suffix"] == SUFFIX and positive["combined"] == f"{PREFIX} {SUFFIX}" and document["negative_style"] == NEGATIVE
    assert document["enforcement"]["allow_per_shot_override"] is False and document["enforcement"]["lock_style_globally"] is True
    assert st.seal(document) == document["content_sha256"]


def test_prompt_is_prefix_then_scene_then_suffix_and_negative_is_unchanged(kf_project):
    frozen_project(kf_project)
    request = request_for(kf_project)
    assert request["prompt"].startswith(PREFIX + " Characters: ") and request["prompt"].endswith(" " + SUFFIX)
    middle = request["prompt"][len(PREFIX) + 1:-(len(SUFFIX) + 1)]
    assert request["prompt"] == f"{PREFIX} {middle} {SUFFIX}" and middle.startswith("Characters: ")        # {prefix} {shot_description} {suffix}
    assert request["negative_prompt"] == NEGATIVE and request["template_version"] == kf.FROZEN_TEMPLATE_VERSION
    document = yaml.safe_load(REAL.read_text(encoding="utf-8"))
    assert request["style"] == {"style_id": "devotional_gouache_1950s_v1", "version": 1, "sha256": document["content_sha256"]}


def test_every_request_of_the_project_carries_the_same_style(kf_project):
    frozen_project(kf_project)
    bundle = load_bundle(kf_project, load_models(kf_project), 1)
    registry = kf.load_registry(kf_project, bundle.canon)
    styles = {str(r["style"]) for r in kf.sheet_requests(bundle.canon, registry, bundle.models)}
    styles.add(str(request_for(kf_project)["style"]))
    assert len(styles) == 1 and "devotional_gouache_1950s_v1" in styles.pop()


def test_an_unsealed_edit_or_a_non_frozen_status_is_refused(kf_project):
    frozen_project(kf_project)
    install_style(kf_project, reseal=False, negative_style="photorealistic")                         # edited, not re-sealed
    with pytest.raises(ConfigError, match="style drift refused"):
        st.load_style(kf_project)
    install_style(kf_project, reseal=False, positive_style={"suffix": SUFFIX + " extra", "combined": f"{PREFIX} {SUFFIX} extra"})
    with pytest.raises(ConfigError, match="style drift refused"):
        st.load_style(kf_project)
    install_style(kf_project, status="draft")
    with pytest.raises(ConfigError, match="status 'frozen'"):
        st.load_style(kf_project)
    install_style(kf_project, positive_style={"combined": "something else"})
    with pytest.raises(ConfigError, match="combined"):
        st.load_style(kf_project)
    install_style(kf_project, enforcement={"allow_per_shot_override": True})
    with pytest.raises(ConfigError, match="per-shot overrides"):
        st.load_style(kf_project)
    install_style(kf_project, receipt_binding={"record_style_hash": False})
    with pytest.raises(ConfigError, match="receipts must record"):
        st.load_style(kf_project)
    install_style(kf_project, approved_by="")
    with pytest.raises(ConfigError, match="who approved"):
        st.load_style(kf_project)
    install_style(kf_project, runner_prompt_rule={"final_prompt_template": "{prefix}, {shot_description}, {suffix}"})
    with pytest.raises(ConfigError, match="prefix_middle_suffix"):
        st.load_style(kf_project)


def test_a_second_style_in_the_registry_is_refused_not_silently_mixed(kf_project):
    shutil.copyfile(REAL, kf_project.canon_dir / "style.yaml")
    write_registry(kf_project)                                   # the synthetic registry still defines its own style block
    with pytest.raises(ConfigError, match="two styles"):
        kf.load_registry(kf_project)


def test_registry_saves_never_write_the_frozen_style_into_visual_assets(kf_project):
    frozen_project(kf_project)
    bundle = load_bundle(kf_project, load_models(kf_project), 1)
    registry = kf.load_registry(kf_project, bundle.canon)
    assert registry["frozen_style"]["style_id"] == "devotional_gouache_1950s_v1"
    kf.save_registry(kf_project, registry)
    assert "frozen_style" not in yaml.safe_load((kf_project.canon_dir / "visual_assets.yaml").read_text(encoding="utf-8"))


def test_changing_the_style_changes_the_production_snapshot_and_task_ids_and_both_languages_share_it(kf_project):
    frozen_project(kf_project)
    bundle = load_bundle(kf_project, load_models(kf_project), 1)
    before_snapshot = snapshot(bundle)
    tasks = plan_tasks(bundle, Scheduler(kf_project.artifacts_dir / "tasks" / "adhyay_01"))
    carriers = [t for t in tasks if t.stage in ("keyframe", "assembly") or t.stage in ("tier1", "tier2")]
    assert carriers and all("style" in t.inputs for t in carriers)
    assembly = {t.name: t.inputs["style"] for t in tasks if t.stage == "assembly"}
    assert assembly["assemble_mr"] == assembly["assemble_hi"] and assembly["assemble_mr"].startswith("devotional_gouache_1950s_v1@1:")
    install_style(kf_project, version=2, style_id="devotional_gouache_1950s_v2")   # a deliberate new, re-sealed style version
    changed = load_bundle(kf_project, load_models(kf_project), 1)
    assert snapshot(changed) != before_snapshot                    # in-flight work notices the new style instead of drifting
    assert {t.task_id() for t in plan_tasks(changed, Scheduler(kf_project.artifacts_dir / "tasks" / "adhyay_01"))
            if t.stage == "keyframe"}.isdisjoint({t.task_id() for t in tasks if t.stage == "keyframe"})


def test_generation_refuses_a_request_built_under_another_style(kf_project, comfy, tmp_path):
    frozen_project(kf_project)
    request = request_for(kf_project)
    request["style"] = {"style_id": "devotional_gouache_1950s_v1", "version": 1, "sha256": "0" * 64}
    with pytest.raises(GateFailure, match="style drift refused"):
        kf.sdxl_generate(kf_project, load_models(kf_project), request, tmp_path / "j.json", tmp_path)


def test_sdxl_generate_asks_for_the_host_gate_by_default_and_a_later_batch_image_may_skip_it(kf_project, comfy, tmp_path, monkeypatch):
    from granthstudio.errors import IntegrationUnavailable
    frozen_project(kf_project)
    request = request_for(kf_project)
    request["style"] = {"style_id": "devotional_gouache_1950s_v1", "version": 1, "sha256": "0" * 64}      # stops right after the preflight
    def busy(project, models):
        raise IntegrationUnavailable("free_vram fail")
    monkeypatch.setattr(kf, "require_host_ready", busy)
    models = load_models(kf_project)
    with pytest.raises(IntegrationUnavailable, match="free_vram"):
        kf.sdxl_generate(kf_project, models, request, tmp_path / "j.json", tmp_path)
    with pytest.raises(GateFailure, match="style drift refused"):                 # gate skipped: got past the preflight
        kf.sdxl_generate(kf_project, models, request, tmp_path / "j.json", tmp_path, check_host=False)


def test_a_shot_cannot_carry_its_own_style_the_manifest_schema_refuses_unknown_fields(kf_project):
    from granthstudio.schemas import validate_document
    import copy
    manifest = yaml.safe_load((kf_project.episodes_dir / "adhyay_01" / "manifest.yaml").read_text(encoding="utf-8"))
    validate_document("episode_manifest", manifest)
    tampered = copy.deepcopy(manifest)
    tampered["scenes"][0]["shots"][0]["style"] = "my_own_look"
    with pytest.raises(Exception):
        validate_document("episode_manifest", tampered)


def test_a_style_change_after_the_bundle_was_loaded_is_caught_by_require_current(kf_project):
    from granthstudio.pipeline import require_current
    frozen_project(kf_project)
    bundle = load_bundle(kf_project, load_models(kf_project), 1)
    require_current(bundle)                                                   # unchanged: fine
    install_style(kf_project, version=2, style_id="devotional_gouache_1950s_v2")
    with pytest.raises(GateFailure, match="snapshot changed"):
        require_current(bundle)                                               # the live style differs from the identity captured at load
    assert bundle.style["style_id"] == "devotional_gouache_1950s_v1"


def test_sheet_tasks_check_state_without_the_host_gate_after_a_render(kf_project, monkeypatch):
    frozen_project(kf_project)
    bundle = load_bundle(kf_project, load_models(kf_project), 1)
    scheduler = Scheduler(kf_project.artifacts_dir / "tasks" / "references")
    tasks = kf.sheet_tasks(kf_project, bundle.canon, load_models(kf_project), scheduler)
    assert tasks and all(t.postflight is not None for t in tasks)
    calls = []
    monkeypatch.setattr(kf, "require_host_ready", lambda *a, **k: calls.append("host"))
    tasks[0].preflight(); assert calls == ["host"]
    calls.clear(); tasks[0].postflight(); assert calls == []                  # no resource gate after the render


def test_a_visual_description_becomes_the_whole_middle_of_the_frozen_prompt_and_may_not_name_anyone(kf_project):
    from granthstudio.config import load_yaml
    from granthstudio.integrity import atomic_write_json
    frozen_project(kf_project)
    before = request_for(kf_project)
    assert before["template_version"] == "keyframe-prompt-v2-frozen-style" and before["visual_description"] is None     # no description: earlier behaviour
    path = kf_project.episodes_dir / "adhyay_01" / "manifest.yaml"
    manifest = load_yaml(path)
    description = "A calm young man sits on a dusty road among scattered leaf plates. Bright daylight."
    next(v for v in manifest["visuals"] if v["visual_id"] == "vis_kf")["description"] = description
    atomic_write_json(path, manifest)
    request = request_for(kf_project)
    style = st.load_style(kf_project)
    assert request["prompt"] == st.compose(style, description) and request["template_version"] == "keyframe-prompt-v3-visual-description"
    assert request["characters"] == before["characters"] and request["references"] == before["references"]                  # identities and references stay in the metadata
    assert request["request_sha256"] != before["request_sha256"]
    named = load_yaml(path)
    name = before["characters"] and next(iter(before["characters"]))
    from granthstudio.canon import load_canon
    canonical = load_canon(kf_project).entries[name]["canonical_name"]
    next(v for v in named["visuals"] if v["visual_id"] == "vis_kf")["description"] = f"{canonical} sits on the road."
    atomic_write_json(path, named)
    with pytest.raises(ConfigError, match="names"):
        request_for(kf_project)
