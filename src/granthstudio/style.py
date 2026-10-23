"""The project-wide frozen art style (canon/style.yaml).

One style for every shot, every language and every stage (storyboard, keyframes, images, video prompts): prompts are composed as
``{prefix} {shot_description} {suffix}``, the negative prompt is fixed, and the style id, version and content hash travel in every request, task input and receipt.
Editing the file without re-sealing it (``content_sha256``) is refused, so a style change is always a deliberate new style_id/version with explicit approval and
never silent per-shot drift. Characters, locations and props may stay provisional; only the look is frozen here.
"""
from __future__ import annotations

from typing import Any

from .config import Project, load_yaml
from .errors import ConfigError
from .integrity import sha256_obj

STYLE_FILE = "style.yaml"
REQUIRED_ENFORCEMENT = ("lock_style_globally", "use_same_style_for_marathi_and_hindi", "require_negative_prompt" , "forbid_text_in_image", "forbid_watermarks")
REQUIRED_BINDING = ("record_style_id", "record_style_version", "record_style_hash")
TEMPLATE = "{prefix} {shot_description} {suffix}"


def _text(value: Any) -> str:
    return str(value).strip()


def sealed_content(document: dict[str, Any]) -> dict[str, Any]:
    """Everything that defines the style except the seal itself (folded YAML scalars normalised by strip)."""
    positive = document["positive_style"]
    return {"style_id": document["style_id"], "version": document["version"], "status": document["status"], "scope": document["scope"],
            "approved_by": _text(document["approved_by"]), "approved_on": str(document["approved_on"]),
            "positive_style": {k: _text(positive[k]) for k in ("prefix", "suffix", "combined")}, "negative_style": _text(document["negative_style"]),
            "runner_prompt_rule": document["runner_prompt_rule"], "enforcement": document["enforcement"], "receipt_binding": document["receipt_binding"]}


def seal(document: dict[str, Any]) -> str:
    return sha256_obj(sealed_content(document))


def load_style(project: Project) -> dict[str, Any] | None:
    """The frozen style, or None when the project has no canon/style.yaml. Any inconsistency is a hard refusal."""
    path = project.canon_dir / STYLE_FILE
    if not path.is_file():
        return None
    document = load_yaml(path)
    try:
        content = sealed_content(document)
        sealed = document["content_sha256"]
    except KeyError as exc:
        raise ConfigError(f"{path.name}: missing {exc}") from exc
    if content["status"] != "frozen" or content["scope"] != "global":
        raise ConfigError(f"{path.name}: needs status 'frozen' and scope 'global', found {content['status']!r}/{content['scope']!r}")
    if not content["approved_by"] or not content["approved_on"]:
        raise ConfigError(f"{path.name}: a frozen style records who approved it and when")
    if document["runner_prompt_rule"].get("mode") != "prefix_middle_suffix" or _text(document["runner_prompt_rule"].get("final_prompt_template")) != TEMPLATE:
        raise ConfigError(f"{path.name}: runner_prompt_rule must be prefix_middle_suffix with the template {TEMPLATE!r}")
    if any(document["enforcement"].get(key) is not True for key in REQUIRED_ENFORCEMENT) or document["enforcement"].get("allow_per_shot_override") is not False:
        raise ConfigError(f"{path.name}: enforcement must lock the style globally, forbid per-shot overrides and keep the negative prompt, no text and no watermarks")
    if any(document["receipt_binding"].get(key) is not True for key in REQUIRED_BINDING):
        raise ConfigError(f"{path.name}: receipts must record style id, version and hash")
    positive = content["positive_style"]
    if positive["combined"] != f"{positive['prefix']} {positive['suffix']}":
        raise ConfigError(f"{path.name}: combined is not prefix + suffix")
    if seal(document) != sealed:
        raise ConfigError(f"{path.name}: content changed without a new sealed version (content_sha256 mismatch): style drift refused")
    return {"style_id": content["style_id"], "version": content["version"], "status": content["status"], "scope": content["scope"],
            "approved_by": content["approved_by"], "approved_on": content["approved_on"], "prompt_prefix": positive["prefix"],
            "prompt_suffix": positive["suffix"], "positive_prompt": positive["combined"], "negative_prompt": content["negative_style"],
            "content_sha256": sealed}


def identity(style: dict[str, Any] | None) -> dict[str, Any] | None:
    """What goes into requests, task inputs and receipts."""
    if style is None:
        return None
    return {"style_id": style["style_id"], "version": style["version"], "sha256": style["content_sha256"]}


def compose(style: dict[str, Any], shot_description: str) -> str:
    """{prefix} {shot_description} {suffix}, exactly as frozen."""
    return TEMPLATE.format(prefix=style["prompt_prefix"], shot_description=shot_description.strip(), suffix=style["prompt_suffix"])
