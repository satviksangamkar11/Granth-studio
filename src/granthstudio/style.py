"""The project-wide art style (canon/style.yaml): one file, several immutable versions, exactly one ACTIVE and FROZEN.

Prompts are composed deterministically: v1 ``{prefix} {shot_description} {suffix}``; the video-safe version ``{prefix} {shot_description} {lighting} {suffix}`` where the
lighting phrase comes from a small approved table keyed by the manifest's lighting bucket (never free text). Style id, version, content hash, lighting bucket and, for the
video-safe version, the border overlay SHA-256 travel in every request, task identity and receipt. Every version is sealed by ``content_sha256``: editing it without a new
version is refused, a PROPOSED version can never be used for generation, and activating a version needs status 'frozen' with an approver and date. Characters, locations and
props may stay provisional.
"""
from __future__ import annotations

from typing import Any

from .config import Project, load_yaml
from .errors import ConfigError, GateFailure
from .integrity import contained_path, sha256_file, sha256_obj

STYLE_FILE = "style.yaml"
REQUIRED_ENFORCEMENT = ("lock_style_globally", "use_same_style_for_marathi_and_hindi", "require_negative_prompt", "forbid_text_in_image", "forbid_watermarks")
REQUIRED_BINDING = ("record_style_id", "record_style_version", "record_style_hash")
VIDEO_SAFE_BINDING = ("record_lighting_bucket", "record_overlay_sha256")
TEMPLATE_V1 = "{prefix} {shot_description} {suffix}"
TEMPLATE_LIGHTING = "{prefix} {shot_description} {lighting} {suffix}"
LIGHTING_BUCKETS = ("day_outdoor", "day_indoor", "dusk", "night", "lamplight", "unspecified")   # = the episode manifest enum
UNSEALED = ("notes", "content_sha256")


def _normal(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _normal(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normal(v) for v in value]
    return value.strip() if isinstance(value, str) else str(value) if hasattr(value, "isoformat") else value


def seal(document: dict[str, Any]) -> str:
    """Hash of everything that defines one version except its notes and the seal itself."""
    return sha256_obj(_normal({k: v for k, v in document.items() if k not in UNSEALED}))


def _check_version(document: dict[str, Any], where: str) -> None:
    for key in ("style_id", "version", "status", "scope", "positive_style", "negative_style", "runner_prompt_rule", "enforcement", "receipt_binding", "content_sha256"):
        if key not in document:
            raise ConfigError(f"{where}: missing {key}")
    if document["status"] not in ("frozen", "proposed") or document["scope"] != "global":
        raise ConfigError(f"{where}: needs status 'frozen' or 'proposed' and scope 'global'")
    positive = _normal(document["positive_style"])
    if positive["combined"] != f"{positive['prefix']} {positive['suffix']}":
        raise ConfigError(f"{where}: combined is not prefix + suffix")
    if any(document["enforcement"].get(key) is not True for key in REQUIRED_ENFORCEMENT) or document["enforcement"].get("allow_per_shot_override") is not False:
        raise ConfigError(f"{where}: enforcement must lock the style globally, forbid per-shot overrides and keep the negative prompt, no text and no watermarks")
    if any(document["receipt_binding"].get(key) is not True for key in REQUIRED_BINDING):
        raise ConfigError(f"{where}: receipts must record style id, version and hash")
    rule = document["runner_prompt_rule"]
    template = str(rule.get("final_prompt_template", "")).strip()
    if rule.get("mode") == "prefix_middle_suffix" and template == TEMPLATE_V1:
        pass
    elif rule.get("mode") == "prefix_middle_lighting_suffix" and template == TEMPLATE_LIGHTING:
        table = document.get("lighting_buckets")
        if not isinstance(table, dict) or set(table) != set(LIGHTING_BUCKETS) or not all(isinstance(v, str) for v in table.values()):
            raise ConfigError(f"{where}: lighting_buckets must map exactly {list(LIGHTING_BUCKETS)} to approved phrases")
        border = document.get("border")
        if not isinstance(border, dict) or not all(border.get(k) for k in ("overlay_path", "overlay_sha256", "width", "height")):
            raise ConfigError(f"{where}: a video-safe style needs border.overlay_path, overlay_sha256, width and height")
        enforcement = document["enforcement"]
        if border.get("applied_at") != "final_visual_assembly" or enforcement.get("border_baked_into_generated_images") is not False \
                or enforcement.get("keyframes_full_bleed") is not True or enforcement.get("allow_free_text_lighting") is not False:
            raise ConfigError(f"{where}: the border belongs to final assembly only, keyframes are full-bleed and lighting is a closed set")
        if any(document["receipt_binding"].get(key) is not True for key in VIDEO_SAFE_BINDING):
            raise ConfigError(f"{where}: receipts must record the lighting bucket and the overlay SHA-256")
    else:
        raise ConfigError(f"{where}: unknown runner_prompt_rule {rule!r}")
    if seal(document) != document["content_sha256"]:
        raise ConfigError(f"{where}: content changed without a new sealed version (content_sha256 mismatch): style drift refused")
    if document["status"] == "frozen" and not (_normal(document.get("approved_by")) and _normal(document.get("approved_on"))):
        raise ConfigError(f"{where}: a frozen style records who approved it and when")


def load_versions(project: Project) -> tuple[str, dict[str, dict[str, Any]]] | None:
    path = project.canon_dir / STYLE_FILE
    if not path.is_file():
        return None
    root = load_yaml(path)
    versions: dict[str, dict[str, Any]] = {}
    for document in root.get("versions", []):
        _check_version(document, f"{path.name}:{document.get('style_id')}")
        if document["style_id"] in versions:
            raise ConfigError(f"{path.name}: duplicate style_id {document['style_id']}")
        versions[document["style_id"]] = document
    for document in versions.values():
        parent = document.get("supersedes")
        if parent and (parent not in versions or versions[parent]["content_sha256"] != document.get("supersedes_sha256")):
            raise ConfigError(f"{path.name}:{document['style_id']}: supersedes {parent} but its sealed hash differs: an earlier frozen version was altered")
    active = root.get("active")
    if active not in versions or versions[active]["status"] != "frozen":
        raise ConfigError(f"{path.name}: the active style {active!r} must be a frozen version; a proposed version cannot be used for generation")
    return active, versions


def _flat(document: dict[str, Any]) -> dict[str, Any]:
    positive, doc = _normal(document["positive_style"]), _normal(document)
    flat = {"style_id": doc["style_id"], "version": doc["version"], "status": doc["status"], "scope": doc["scope"],
            "approved_by": doc.get("approved_by"), "approved_on": doc.get("approved_on"), "prompt_prefix": positive["prefix"],
            "prompt_suffix": positive["suffix"], "positive_prompt": positive["combined"], "negative_prompt": doc["negative_style"],
            "content_sha256": doc["content_sha256"], "template": doc["runner_prompt_rule"]["final_prompt_template"]}
    if document["runner_prompt_rule"]["mode"] == "prefix_middle_lighting_suffix":
        flat["lighting_phrases"] = dict(doc["lighting_buckets"])
        flat["border"] = dict(doc["border"])
    return flat


def load_style(project: Project) -> dict[str, Any] | None:
    """The ACTIVE frozen style, or None when the project has no canon/style.yaml. Any inconsistency anywhere in the file is a hard refusal."""
    loaded = load_versions(project)
    if loaded is None:
        return None
    active, versions = loaded
    return _flat(versions[active])


def load_proposed(project: Project) -> list[dict[str, Any]]:
    loaded = load_versions(project)
    return [] if loaded is None else [_flat(d) for d in loaded[1].values() if d["status"] == "proposed"]


def identity(style: dict[str, Any] | None) -> dict[str, Any] | None:
    """What goes into requests, task inputs and receipts (video-safe styles add the overlay hash)."""
    if style is None:
        return None
    result = {"style_id": style["style_id"], "version": style["version"], "sha256": style["content_sha256"]}
    if "border" in style:
        result["overlay_sha256"] = style["border"]["overlay_sha256"]
    return result


def style_tag(style_identity: dict[str, Any] | None) -> str | None:
    """One string for Task.inputs: id@version:hash[+overlay]."""
    if style_identity is None:
        return None
    tag = f"{style_identity['style_id']}@{style_identity['version']}:{style_identity['sha256']}"
    return tag + (f"+{style_identity['overlay_sha256']}" if "overlay_sha256" in style_identity else "")


def lighting_phrase(style: dict[str, Any], bucket: str) -> str:
    table = style.get("lighting_phrases")
    if table is None:
        return ""
    if bucket not in table:
        raise GateFailure(f"lighting {bucket!r} is not an approved bucket {sorted(table)}: free-text lighting is refused")
    return table[bucket]


def compose(style: dict[str, Any], shot_description: str, lighting_bucket: str | None = None) -> str:
    """v1: {prefix} {shot_description} {suffix}; video-safe: {prefix} {shot_description} {lighting} {suffix} (an empty lighting phrase leaves no double space)."""
    description = shot_description.strip()
    if "lighting_phrases" not in style:
        return TEMPLATE_V1.format(prefix=style["prompt_prefix"], shot_description=description, suffix=style["prompt_suffix"])
    if lighting_bucket is None:
        raise GateFailure("this style composes a lighting clause: an approved lighting bucket is required")
    phrase = lighting_phrase(style, lighting_bucket)
    parts = [style["prompt_prefix"], description, phrase, style["prompt_suffix"]]
    return " ".join(part for part in parts if part)


def overlay_file(project: Project, style: dict[str, Any]) -> Any:
    """The approved border overlay, verified by content hash (video-safe styles only)."""
    border = style.get("border")
    if border is None:
        return None
    path = contained_path(project.root, border["overlay_path"])
    if not path.is_file() or sha256_file(path) != border["overlay_sha256"]:
        raise GateFailure(f"border overlay {border['overlay_path']} is missing or differs from the approved SHA-256: refused")
    return path
