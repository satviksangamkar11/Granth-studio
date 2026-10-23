"""The proposed video-safe style (devotional_gouache_1950s_v2): full-bleed keyframes, closed lighting buckets, one static border at final assembly.
v2 stays PROPOSED in the shipped file; these tests simulate the owner's approval with a synthetic approver on a copy."""
from __future__ import annotations

import copy
import shutil
import subprocess

import pytest
import yaml

from granthstudio import ffmpeg
from granthstudio import keyframes as kf
from granthstudio import style as st
from granthstudio.config import load_models
from granthstudio.errors import ConfigError, GateFailure
from granthstudio.integrity import read_json, sha256_file
from granthstudio.pipeline import _border_for_assembly, episode_store, load_bundle, plan_tasks
from granthstudio.scheduler import Scheduler
from tests.conftest import REPO, have_tool
from tests.test_keyframes import comfy, kf_project, request_for, write_registry   # noqa: F401  (fixtures)
from tests.test_review_regressions import make_cpu_project
from tests.test_style import V1, V1_SEAL, V2, REAL, activate_v2, shipped, shipped_root, write_root

pytestmark = pytest.mark.skipif(not (have_tool("ffmpeg") and have_tool("ffprobe")), reason="media tools missing")
OVERLAY_REL = "canon/overlays/vintage_double_line_border_1080p.png"
LIGHTING = ("day_outdoor", "day_indoor", "dusk", "night", "lamplight", "unspecified")


def video_safe_project(project):
    """A synthetic project whose active style is the (simulated-approved) v2, with the real overlay installed at its pinned path."""
    write_registry(project, style=None)
    shutil.copyfile(REAL, project.canon_dir / "style.yaml")
    activate_v2(project)
    (project.root / "canon" / "overlays").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(REPO / OVERLAY_REL, project.root / OVERLAY_REL)
    return project


def test_v2_is_proposed_the_original_is_preserved_and_a_proposed_version_cannot_be_active(kf_project):
    root = shipped_root()
    assert root["active"] == V1 and shipped(V1)["content_sha256"] == V1_SEAL
    v2 = shipped(V2)
    assert v2["status"] == "proposed" and v2["approved_by"] is None and v2["supersedes"] == V1 and v2["supersedes_sha256"] == V1_SEAL
    assert st.seal(v2) == v2["content_sha256"] and v2["border"]["overlay_sha256"] == sha256_file(REPO / OVERLAY_REL)
    shutil.copyfile(REAL, kf_project.canon_dir / "style.yaml")
    assert [p["style_id"] for p in st.load_proposed(kf_project)] == [V2] and st.load_style(kf_project)["style_id"] == V1
    root["active"] = V2                                                    # activating an unapproved version
    write_root(kf_project, root)
    with pytest.raises(ConfigError, match="must be a frozen version"):
        st.load_style(kf_project)
    root = shipped_root()
    next(d for d in root["versions"] if d["style_id"] == V1)["negative_style"] += " tampered"      # the earlier frozen version altered
    write_root(kf_project, root)
    with pytest.raises(ConfigError):
        st.load_style(kf_project)


def test_prompt_is_prefix_scene_lighting_suffix_with_full_bleed_wording_and_a_border_blocking_negative(kf_project):
    video_safe_project(kf_project)
    request = request_for(kf_project)
    style = st.load_style(kf_project)
    phrase = style["lighting_phrases"][request["lighting_bucket"]]
    prompt = request["prompt"]
    assert prompt.startswith(style["prompt_prefix"] + " Characters: ") and prompt.endswith(" " + style["prompt_suffix"])
    middle = prompt[len(style["prompt_prefix"]) + 1:-(len(style["prompt_suffix"]) + 1)]
    expected_tail = f" {phrase}" if phrase else ""
    assert middle.endswith(expected_tail) and "Lighting:" not in prompt                  # the phrase sits in its own slot, not as free text in the description
    assert request["template_version"] == kf.VIDEO_SAFE_TEMPLATE_VERSION and request["full_bleed"] is True
    assert "full-bleed" in prompt and "no border" in prompt and "deep indigo reserved for dusk and night shadows" in prompt
    assert all(word in request["negative_prompt"] for word in ("border", "frame", "picture mount", "vignette"))
    assert "double-line paper border mount" not in prompt                                # the v1 wording that baked a border into the painting is gone
    assert request["style"] == {"style_id": V2, "version": 2, "sha256": st.load_style(kf_project)["content_sha256"], "overlay_sha256": style["border"]["overlay_sha256"]}
    assert request_for(kf_project) == request                                            # deterministic


def test_composition_is_deterministic_for_every_bucket_and_free_text_lighting_is_refused(kf_project):
    video_safe_project(kf_project)
    style = st.load_style(kf_project)
    for bucket in LIGHTING:
        text = st.compose(style, "A figure stands.", bucket)
        assert text == " ".join(p for p in (style["prompt_prefix"], "A figure stands.", style["lighting_phrases"][bucket], style["prompt_suffix"]) if p)
        assert "  " not in text                                                           # the empty 'unspecified' phrase leaves no gap
    with pytest.raises(GateFailure, match="free-text lighting is refused"):
        st.compose(style, "A figure stands.", "golden hour with lens flare")
    with pytest.raises(GateFailure, match="lighting bucket is required"):
        st.compose(style, "A figure stands.")
    assert style["lighting_phrases"]["dusk"] != style["lighting_phrases"]["day_outdoor"] and "indigo" in style["lighting_phrases"]["night"]


def test_a_keyframe_shared_by_shots_with_different_lighting_is_refused(kf_project):
    video_safe_project(kf_project)
    bundle = load_bundle(kf_project, load_models(kf_project), 1)
    registry = kf.load_registry(kf_project, bundle.canon)
    compiled = copy.deepcopy(bundle.compiled)
    shot = next(s for s in compiled["shots"] if s["visual_id"] == "vis_kf")
    other = copy.deepcopy(shot); other["shot_id"] = "extra"; other["lighting"] = "night" if shot["lighting"] != "night" else "dusk"
    compiled["shots"].append(other)
    with pytest.raises(GateFailure, match="exactly one lighting bucket"):
        kf.keyframe_request(compiled, bundle.canon, registry, bundle.models, "vis_kf")


def test_reference_sheets_use_the_full_bleed_style_without_a_lighting_clause(kf_project):
    video_safe_project(kf_project)
    bundle = load_bundle(kf_project, load_models(kf_project), 1)
    registry = kf.load_registry(kf_project, bundle.canon)
    sheets = kf.sheet_requests(bundle.canon, registry, bundle.models)
    assert sheets and all("full-bleed" in s["prompt"] and "  " not in s["prompt"] and s["style"]["style_id"] == V2 for s in sheets)


def moving_clip(path, source, seconds=1):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", source, "-t", str(seconds), "-c:v", "libx264", "-pix_fmt", "yuv420p", str(path)], check=True, timeout=60)
    return path


def test_the_static_border_is_present_and_identical_from_first_to_last_frame_whatever_moves_behind_it(tmp_path):
    overlay = REPO / OVERLAY_REL
    results = []
    for index, source in enumerate(("testsrc2=size=640x360:rate=24", "gradients=size=640x360:rate=24:speed=0.5:seed=5", "mandelbrot=size=640x360:rate=24")):
        clip = moving_clip(tmp_path / f"in{index}.mp4", source)
        out = tmp_path / f"out{index}.mp4"
        ffmpeg.assemble([clip, clip], out, overlay=overlay)
        samples = ffmpeg.border_samples(out)
        assert samples["ok"], samples
        results.append(samples["samples"])
    luma = lambda rgb: 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
    assert all(abs(luma(r[key]) - luma(results[0][key])) <= 24 for r in results[1:] for key in r)                    # the border does not depend on the picture behind it
    plain = ffmpeg.assemble([moving_clip(tmp_path / "p.mp4", "testsrc2=size=640x360:rate=24")], tmp_path / "plain.mp4")
    assert ffmpeg.border_samples(tmp_path / "plain.mp4")["ok"] is False                                           # no overlay: the check notices


def test_assembly_applies_the_border_once_records_it_and_binds_both_languages(approved_project):
    make_cpu_project(approved_project)
    video_safe_project(approved_project)
    bundle = load_bundle(approved_project, load_models(approved_project), 1)
    scheduler = Scheduler(episode_store(approved_project, 1))
    tasks = plan_tasks(bundle, scheduler)
    assert all(r.status == "complete" for r in scheduler.run(tasks)), "pipeline did not complete"
    overlay_sha = sha256_file(REPO / OVERLAY_REL)
    tags = {t.name: t.inputs["style"] for t in tasks if t.stage == "assembly"}
    assert tags["assemble_mr"] == tags["assemble_hi"] and tags["assemble_mr"].endswith(f"+{overlay_sha}")      # same style, overlay hash in the task identity
    for lang in ("mr", "hi"):
        task = next(t for t in tasks if t.name == f"assemble_{lang}")
        provenance = read_json(scheduler.task_dir(task) / "provenance.json")
        assert provenance["style"]["style_id"] == V2 and provenance["style"]["overlay_sha256"] == overlay_sha
        assert provenance["border"]["overlay_sha256"] == overlay_sha and provenance["border"]["applied_at"] == "final_visual_assembly"
        assert provenance["border"]["applied_after"][:2] == ["ltx_motion", "lipsync"] and provenance["border"]["edge_samples"]["ok"] is True
        assert provenance["border"]["aspect_mismatch"] is False and set(provenance["lighting_buckets"].values()) <= set(LIGHTING)
        assert ffmpeg.border_samples(next(scheduler.task_dir(task).glob("*.mp4")))["ok"]
    # the video-safe keyframes/shots carry their lighting bucket in the task identity
    assert all("lighting" in t.inputs for t in tasks if t.stage in ("tier1", "tier2"))


def test_changing_lighting_or_the_overlay_invalidates_cached_work_and_a_swapped_overlay_is_refused(approved_project):
    video_safe_project(approved_project)
    bundle = load_bundle(approved_project, load_models(approved_project), 1)
    scheduler = Scheduler(episode_store(approved_project, 1))
    ids = lambda b: {t.name: t.task_id() for t in plan_tasks(b, Scheduler(episode_store(approved_project, 1)))}
    before = ids(bundle)
    manifest_path = approved_project.episodes_dir / "adhyay_01" / "manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest["scenes"][0]["lighting"] = "night" if manifest["scenes"][0].get("lighting") != "night" else "dusk"      # a different approved bucket
    from granthstudio.integrity import atomic_write_json
    atomic_write_json(manifest_path, manifest)
    relit = ids(load_bundle(approved_project, load_models(approved_project), 1))
    assert relit["a01_s01_sh01"] != before["a01_s01_sh01"] if "a01_s01_sh01" in before else relit != before
    # a different overlay hash (a re-sealed, re-approved style) changes the assembly identity
    root = shipped_root()
    document = next(d for d in root["versions"] if d["style_id"] == V2)
    document.update(status="frozen", approved_by="synthetic-test-only", approved_on="2026-10-24")
    document["border"]["overlay_sha256"] = "0" * 64
    document["content_sha256"] = st.seal(document)
    root["active"] = V2
    write_root(approved_project, root)
    other = load_bundle(approved_project, load_models(approved_project), 1)
    assert {n: i for n, i in ids(other).items() if n.startswith("assemble")} != {n: i for n, i in relit.items() if n.startswith("assemble")}
    with pytest.raises(GateFailure, match="missing or differs from the approved SHA-256"):
        _border_for_assembly(other)                                                  # the file on disk is not the overlay this style pins
    video_safe_project(approved_project)                                             # restore the genuine overlay and style
    assert _border_for_assembly(load_bundle(approved_project, load_models(approved_project), 1))[0] is not None
    (approved_project.root / OVERLAY_REL).write_bytes(b"not the approved overlay")
    with pytest.raises(GateFailure, match="missing or differs"):
        _border_for_assembly(load_bundle(approved_project, load_models(approved_project), 1))


def test_a_style_changed_after_loading_blocks_the_border(approved_project):
    video_safe_project(approved_project)
    bundle = load_bundle(approved_project, load_models(approved_project), 1)
    shutil.copyfile(REAL, approved_project.canon_dir / "style.yaml")                   # back to the shipped v1-active file
    with pytest.raises(GateFailure, match="style changed after this bundle was loaded"):
        _border_for_assembly(bundle)
