"""Visual canon and SDXL keyframes (frozen sections 4.3, 4.4 and 6).

The global registry (canon/visual_assets.yaml) holds the style, human-written design prompts
and versioned reference assets with immutable hashes. Generation is NOT VALIDATED: no SDXL
checkpoint, identity-conditioning method or art style is selected (O-006). Every gate below
refuses rather than assuming a choice.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from .canon import Canon
from .comfy import ComfyBackend, generation_seed, load_template, render_graph, select_image
from .config import Project, load_yaml
from .errors import ConfigError, GateFailure, IntegrationUnavailable, TaskFailed
from .ffmpeg import probe
from .runtime import require_host_ready
from .scheduler import Scheduler, Task
from .integrity import create_new_file, reject_link_components, atomic_write_bytes, atomic_write_json, contained_path, read_json, sha256_bytes, sha256_file, sha256_obj
from .schemas import validate_document

PROMPT_TEMPLATE_VERSION = "keyframe-prompt-v1"
SHEET_VIEWS = ("front", "three_quarter", "profile", "full_body")
REFERENCE_DIR = "references"
ASSET_ID = re.compile(r"^ref_[a-z0-9_]+$")
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
EMPTY_REGISTRY = {"schema_version": 1, "style": None, "designs": [], "assets": []}


def registry_path(project: Project) -> Path:
    return project.canon_dir / "visual_assets.yaml"


def references_root(project: Project) -> Path:
    return project.artifacts_dir / REFERENCE_DIR


def load_registry(project: Project, canon: Canon | None = None) -> dict[str, Any]:
    path = registry_path(project)
    if not path.is_file():
        return dict(EMPTY_REGISTRY)
    registry = load_yaml(path)
    validate_document("visual_assets", registry)
    seen: set[tuple[str, int]] = set()
    for asset in registry["assets"]:
        key = (asset["asset_id"], asset["version"])
        if key in seen:
            raise ConfigError(f"duplicate asset version {key}")
        seen.add(key)
        if asset["kind"] == "keyframe":
            if "visual_id" not in asset or asset.get("canon_id"):
                raise ConfigError(f"{asset['asset_id']}: keyframes carry a visual_id, not a canon_id")
        elif "canon_id" not in asset:
            raise ConfigError(f"{asset['asset_id']}: reference assets need a canon_id")
        elif canon is not None and asset["canon_id"] not in canon.entries:
            raise ConfigError(f"{asset['asset_id']}: unknown canon id {asset['canon_id']}")
        if asset["status"] == "approved":
            if "approved_by" not in asset:
                raise GateFailure(f"{asset['asset_id']} v{asset['version']}: approval has no reviewer")
            file = contained_path(references_root(project), asset["path"])
            if not file.is_file() or sha256_file(file) != asset["sha256"]:
                raise GateFailure(f"{asset['asset_id']} v{asset['version']}: approved file changed or missing")
    for design in registry["designs"]:
        if canon is not None and design["canon_id"] not in canon.entries:
            raise ConfigError(f"design for unknown canon id {design['canon_id']}")
    return registry


def save_registry(project: Project, registry: dict[str, Any]) -> None:
    validate_document("visual_assets", registry)
    text = yaml.safe_dump(registry, allow_unicode=True, sort_keys=False)
    atomic_write_bytes(registry_path(project), text.encode("utf-8"))


def approved_assets(registry: dict[str, Any], **match: str) -> list[dict[str, Any]]:
    """Highest approved version of each asset matching the fields."""
    best: dict[str, dict[str, Any]] = {}
    for asset in registry["assets"]:
        if asset["status"] == "approved" and all(asset.get(k) == v for k, v in match.items()):
            if asset["asset_id"] not in best or asset["version"] > best[asset["asset_id"]]["version"]:
                best[asset["asset_id"]] = asset
    return sorted(best.values(), key=lambda a: (a["asset_id"], a["version"]))


def _view_rank(asset: dict[str, Any]) -> int:
    return SHEET_VIEWS.index(asset["view"]) if asset.get("view") in SHEET_VIEWS else len(SHEET_VIEWS)


def _design(registry: dict[str, Any], canon_id: str) -> dict[str, Any] | None:
    return next((d for d in registry["designs"] if d["canon_id"] == canon_id), None)


def _style(registry: dict[str, Any]) -> dict[str, Any] | None:
    style = registry["style"]
    return style if style and style["status"] == "approved" else None


def _seed(key: str) -> int:
    return int(sha256_bytes(key.encode())[:8], 16) % 2**31


def _ref(asset: dict[str, Any]) -> dict[str, Any]:
    return {"asset_id": asset["asset_id"], "version": asset["version"], "sha256": asset["sha256"],
            "path": asset["path"], "view": asset.get("view"), "canon_id": asset.get("canon_id")}


def _common(models: dict[str, Any]) -> dict[str, Any]:
    sdxl = models.get("sdxl") or {}
    return {"width": sdxl.get("width"), "height": sdxl.get("height"),
            "identity_method": (sdxl.get("identity_conditioning") or {}).get("method")}


def _prompt(style: dict[str, Any] | None, parts: list[str]) -> str:
    return ". ".join([style["prompt_prefix"] if style else "", *parts]).strip(". ")


def keyframe_request(compiled: dict[str, Any], canon: Canon, registry: dict[str, Any],
                     models: dict[str, Any], visual_id: str) -> dict[str, Any]:
    """Deterministic request for one keyframe: only approved research facts, canon names and
    human-written designs. References that are not approved yet are listed as missing."""
    shots = [s for s in compiled["shots"] if visual_id in (s["visual_id"], s.get("end_visual_id"))]
    if not shots:
        raise ConfigError(f"no shot uses visual {visual_id}")
    role = "start" if any(s["visual_id"] == visual_id for s in shots) else "end"
    characters = sorted({c for s in shots for c in s["characters"]})
    locations = sorted({s["location"] for s in shots})
    props = sorted({p for s in shots for p in s["props"]})
    lightings = sorted({s["lighting"] for s in shots})
    action_ids = sorted({a for s in shots for a in s["action_ids"]})
    facts, artistic_ids = {}, set()
    for shot in shots:
        scene = shot["research_scene"]
        for fact in [*scene["actions"], *scene["visual_details"]]:
            facts[fact["id"]] = fact
    wanted = [facts[f] for f in sorted(facts) if f in action_ids or f in {v["id"] for s in shots
              for v in s["research_scene"]["visual_details"]}]
    for fact in wanted:
        if fact["artistic"]:
            artistic_ids.add(fact["id"])
    style = _style(registry)
    names = lambda ids: ", ".join(canon.entries[i]["canonical_name"] for i in ids)
    designs = [d for i in [*characters, *locations, *props] if (d := _design(registry, i))]
    prompt = _prompt(style, [
        f"Characters: {names(characters)}" if characters else "", f"Location: {names(locations)}",
        f"Props: {names(props)}" if props else "", f"Lighting: {', '.join(lightings)}",
        *[f"{canon.entries[d['canon_id']]['canonical_name']}: {d['prompt']}" for d in designs],
        *[f"{'Artistic interpretation' if f['artistic'] else 'Source detail'}: {f['text']}" for f in wanted]])
    references, missing = [], []
    for char in characters:
        sheets = sorted(approved_assets(registry, kind="character_sheet", canon_id=char), key=_view_rank)
        (references.append(_ref(sheets[0])) if sheets else missing.append(char))
    for loc in locations:
        found = approved_assets(registry, kind="location", canon_id=loc)
        (references.append(_ref(found[0])) if found else missing.append(loc))
    request = {
        "template_version": PROMPT_TEMPLATE_VERSION, "asset_kind": "keyframe", "visual_id": visual_id, "role": role,
        "view": role, "asset_id": "ref_kf_" + visual_id.removeprefix("vis_"), "characters": characters,
        "locations": locations, "props": props, "lighting": lightings, "action_ids": action_ids,
        "source_fact_ids": [f["id"] for f in wanted], "artistic_fact_ids": sorted(artistic_ids),
        "artistic_flags": sorted({f for s in shots for f in s["artistic_flags"]}),
        "prompt": prompt, "negative_prompt": style["negative_prompt"] if style else "", "seed": _seed(visual_id),
        "style": {"style_id": style["style_id"], "version": style["version"]} if style else None,
        "references": references, "missing_references": missing, **_common(models)}
    if role == "end":  # frozen 7 Tier 2: derive the end image from the start image (start hashes unchanged)
        request["derived_from"] = _derived_from(compiled, canon, registry, models, shots)
        if request["derived_from"]["sha256"] is None:
            missing.append(f"start_image:{request['derived_from']['visual_id']}")
    request["request_sha256"] = sha256_obj(request)
    return request


def _derived_from(compiled, canon, registry, models, shots) -> dict[str, Any]:
    starts = sorted({s["visual_id"] for s in shots})
    if len(starts) != 1:
        raise GateFailure(f"end visual {shots[0]['end_visual_id']} must derive from exactly one start visual, found {starts}")
    visual = next(v for v in compiled["visuals"] if v["visual_id"] == starts[0])
    if visual["source"] == "file":
        return {"visual_id": starts[0], "kind": "file", "path": visual["path"], "sha256": visual["sha256"]}
    start = keyframe_request(compiled, canon, registry, models, starts[0])
    found = [a for a in approved_assets(registry, kind="keyframe", visual_id=starts[0])
             if a.get("request_sha256") == start["request_sha256"]]
    return {"visual_id": starts[0], "kind": "keyframe", "path": found[-1]["path"] if found else None,
            "sha256": found[-1]["sha256"] if found else None}


def derived_file(project: Project, derived: dict[str, Any]) -> Path:
    root = project.artifacts_dir / "visuals" if derived["kind"] == "file" else references_root(project)
    path = contained_path(root, derived["path"])
    if not path.is_file() or sha256_file(path) != derived["sha256"]:
        raise GateFailure(f"start image {derived['visual_id']} changed or is missing")
    return path


def sheet_request(canon: Canon, registry: dict[str, Any], models: dict[str, Any], canon_id: str, view: str) -> dict[str, Any]:
    """Reference-sheet view for one canon entry. Non-front views derive from the approved
    front master (frozen 4.4: derive related views from a common reference)."""
    entry = canon.entries[canon_id]
    kind = {"chr": "character_sheet", "loc": "location", "prp": "prop"}[canon_id[:3]]
    style, design = _style(registry), _design(registry, canon_id)
    references, missing = [], []
    if not design:
        missing.append(f"design:{canon_id}")
    if kind == "character_sheet" and view != "front":
        front = [a for a in approved_assets(registry, kind=kind, canon_id=canon_id) if a["view"] == "front"]
        (references.append(_ref(front[0])) if front else missing.append(f"front:{canon_id}"))
    request = {
        "template_version": PROMPT_TEMPLATE_VERSION, "asset_kind": kind, "canon_id": canon_id, "view": view,
        "asset_id": f"ref_{canon_id}_{view}", "prompt": _prompt(style, [
            f"{entry['canonical_name']}, {view.replace('_', ' ')} view" if kind == "character_sheet" else entry["canonical_name"],
            design["prompt"] if design else ""]),
        "design_artistic": design["artistic"] if design else None, "design_source_refs": design["source_refs"] if design else [],
        "negative_prompt": style["negative_prompt"] if style else "", "seed": _seed(f"{canon_id}:{view}"),
        "style": {"style_id": style["style_id"], "version": style["version"]} if style else None,
        "references": references, "missing_references": missing, **_common(models)}
    request["request_sha256"] = sha256_obj(request)
    return request


def sheet_requests(canon: Canon, registry: dict[str, Any], models: dict[str, Any]) -> list[dict[str, Any]]:
    requests = []
    for entry_id, entry in sorted(canon.entries.items()):
        if canon.kinds[entry_id] == "characters" and entry["status"] == "approved":
            requests += [sheet_request(canon, registry, models, entry_id, v) for v in SHEET_VIEWS]
        elif canon.kinds[entry_id] == "locations" and entry["status"] == "approved":
            requests.append(sheet_request(canon, registry, models, entry_id, "establishing"))
    return requests


# ---------------------------------------------------------------- SDXL adapter

def sdxl_preflight(project: Project, models: dict[str, Any], request: dict[str, Any] | None = None):
    """Every selection must be explicit, pinned and locally verified before any SDXL job."""
    sdxl = models.get("sdxl")
    if not sdxl or sdxl["status"] != "validated":
        raise IntegrationUnavailable("SDXL status is not 'validated' (no checkpoint, conditioning or style chosen, O-006): NOT VALIDATED")
    for key in ("checkpoint_file", "checkpoint_sha256", "checkpoint_path", "width", "height"):
        if sdxl[key] is None:
            raise IntegrationUnavailable(f"SDXL {key} is not set (O-006): NOT VALIDATED")
    if sdxl["identity_conditioning"]["method"] is None:
        raise IntegrationUnavailable("SDXL identity-conditioning method is undecided (O-006; 'none' must be explicit): NOT VALIDATED")
    path = Path(sdxl["checkpoint_path"])
    if not path.is_absolute() or not path.is_file() or sha256_file(path) != sdxl["checkpoint_sha256"]:
        raise IntegrationUnavailable("SDXL checkpoint file/hash mismatch: NOT VALIDATED")
    end = bool(request and request.get("role") == "end")
    name = sdxl.get("edit_workflow_template") if end else sdxl["workflow_template"]
    if not name:
        raise IntegrationUnavailable("SDXL end-frame derivation workflow not selected: NOT VALIDATED")
    template = load_template(contained_path(project.root, name))
    if template.status != "validated" or not template.output_node:
        what = "end-frame derivation workflow" if end else "workflow"
        raise IntegrationUnavailable(f"SDXL {what} status is '{template.status}': NOT VALIDATED")
    if sdxl["checkpoint_file"] not in template.text:
        raise ConfigError(f"SDXL workflow {template.name} does not load the pinned checkpoint {sdxl['checkpoint_file']}")
    require_host_ready(project, models)    # this is the GPU task boundary: no SDXL job on an unready host
    return template


def require_references(request: dict[str, Any], models: dict[str, Any]) -> None:
    """Frozen section 6: never generate without the canonical references and approved style."""
    problems = []
    if request["style"] is None:
        problems.append("no approved style")
    if request.get("role") == "end" and not (request.get("derived_from") or {}).get("sha256"):
        problems.append("no approved start image to derive from")
    if request["missing_references"]:
        problems.append(f"missing approved references {request['missing_references']}")
    slots = models["sdxl"]["identity_conditioning"]["reference_slots"]
    if len(request["references"]) > slots:
        problems.append(f"{len(request['references'])} references exceed the workflow's {slots} slots")
    if problems:
        raise GateFailure(f"{request['asset_id']}: " + "; ".join(problems))


def sdxl_generate(project: Project, models: dict[str, Any], request: dict[str, Any], journal: Path, work: Path) -> dict[str, str]:
    """Run one request through ComfyUI and leave keyframe.png, request.json and metrics.json in work."""
    template = sdxl_preflight(project, models, request)
    require_references(request, models)
    slots = models["sdxl"]["identity_conditioning"]["reference_slots"]
    values = {"PROMPT": request["prompt"], "NEGATIVE_PROMPT": request["negative_prompt"], "SEED": generation_seed(journal, request["seed"]),
              "WIDTH": request["width"], "HEIGHT": request["height"]}
    if request.get("role") == "end":
        values["START_IMAGE"] = str(derived_file(project, request["derived_from"]))
    for index in range(1, slots + 1):
        ref = request["references"][index - 1] if index <= len(request["references"]) else None
        values[f"REFERENCE_IMAGE_{index}"] = str(approved_file(project, ref)) if ref else ""
    backend = ComfyBackend(models["comfyui"]["base_url"])
    graph = render_graph(template, values)
    backend.require_nodes(graph)
    backend.require_model_files(graph)
    history = backend.execute(graph, journal, max_attempts=3, output_node=template.output_node, generation={
        "seed": values["SEED"], "seed_offset": values["SEED"] - request["seed"]})
    backend.fetch(select_image(history, template.output_node), work / "keyframe.png")
    info = probe(work / "keyframe.png")
    if (info.width, info.height) != (request["width"], request["height"]):
        raise TaskFailed(f"keyframe is {info.width}x{info.height}, requested {request['width']}x{request['height']}")
    atomic_write_json(work / "request.json", request)
    atomic_write_json(work / "metrics.json", {"schema_version": 1, "prompt_id": read_json(journal)["prompt_id"],
        "request_sha256": request["request_sha256"], "checkpoint_sha256": models["sdxl"]["checkpoint_sha256"],
        "workflow_version": template.version})
    return {"image": "keyframe.png", "request": "request.json", "metrics": "metrics.json"}


def approved_file(project: Project, ref: dict[str, Any]) -> Path:
    path = contained_path(references_root(project), ref["path"])
    if not path.is_file() or sha256_file(path) != ref["sha256"]:
        raise GateFailure(f"reference {ref['asset_id']} v{ref['version']} changed or is missing")
    return path


def approved_keyframe(project: Project, registry: dict[str, Any], request: dict[str, Any]) -> Path:
    """The approved image for a keyframe visual, only if it was generated for this exact request."""
    found = [a for a in approved_assets(registry, kind="keyframe", visual_id=request["visual_id"])
             if a.get("request_sha256") == request["request_sha256"]]
    if not found:
        raise IntegrationUnavailable(
            f"keyframe {request['visual_id']} has no approved image for the current request: generate, "
            "'refs collect' and 'refs approve' it")
    return contained_path(references_root(project), found[-1]["path"])


# ---------------------------------------------------------------- registration and approval

def _next_version(registry: dict[str, Any], asset_id: str) -> int:
    return max((a["version"] for a in registry["assets"] if a["asset_id"] == asset_id), default=0) + 1


def _register(project: Project, registry: dict[str, Any], source: Path, meta: dict[str, Any], origin: str) -> dict[str, Any]:
    asset_id = meta["asset_id"]
    suffix = source.suffix.lower()
    if not isinstance(asset_id, str) or not ASSET_ID.fullmatch(asset_id):
        raise ConfigError(f"invalid asset id {asset_id!r}: must match {ASSET_ID.pattern}")
    if suffix not in IMAGE_SUFFIXES:
        raise ConfigError(f"unsupported reference image type {suffix!r}")
    for key in ("canon_id", "visual_id", "view", "request_sha256"):
        if meta.get(key) is not None and not isinstance(meta[key], str):
            raise ConfigError(f"{key} must be a string")
    digest = sha256_file(source)
    duplicate = next((a for a in registry["assets"] if a["asset_id"] == asset_id and a["sha256"] == digest), None)
    if duplicate:
        return duplicate
    version = _next_version(registry, asset_id)
    relative = f"{asset_id}/v{version}/image{suffix}"
    # Anchored to the trusted artifact root: a redirected references directory is rejected before any write.
    trusted = project.artifacts_dir.resolve()
    reject_link_components(project.artifacts_dir, f"{REFERENCE_DIR}/{relative}")
    create_new_file(trusted, f"{REFERENCE_DIR}/{relative}", source)
    asset = {"asset_id": asset_id, "version": version, "kind": meta["kind"], "path": relative, "sha256": digest,
             "status": "pending", "origin": origin}
    for key in ("canon_id", "visual_id", "view", "request_sha256"):
        if meta.get(key):
            asset[key] = meta[key]
    registry["assets"].append(asset)
    return asset


def import_asset(project: Project, canon: Canon, asset_id: str, kind: str, canon_id: str | None,
                 visual_id: str | None, view: str, source: Path) -> dict[str, Any]:
    reject_link_components(project.artifacts_dir, REFERENCE_DIR)
    registry = load_registry(project, canon)
    asset = _register(project, registry, source, {"asset_id": asset_id, "kind": kind, "canon_id": canon_id,
                                                   "visual_id": visual_id, "view": view}, "imported")
    save_registry(project, registry)
    load_registry(project, canon)
    return asset


def collect_generated(project: Project, canon: Canon, stores: list[Path]) -> list[dict[str, Any]]:
    """Register generated images from completed, receipt-valid task folders as pending assets."""
    reject_link_components(project.artifacts_dir, REFERENCE_DIR)
    registry = load_registry(project, canon)
    added = []
    for store in stores:
        for receipt_path in sorted(store.glob("*/*/task_receipt.json")):
            directory, receipt = receipt_path.parent, read_json(receipt_path)
            outputs = receipt.get("outputs", {})
            if "image" not in outputs or "request" not in outputs:
                continue
            if any(sha256_file(contained_path(directory, o["path"])) != o["sha256"] for o in outputs.values()):
                raise GateFailure(f"{directory.name}: outputs do not match their receipt")
            request = read_json(directory / outputs["request"]["path"])
            known = any(a.get("request_sha256") == request["request_sha256"] and a["asset_id"] == request["asset_id"]
                        for a in registry["assets"])
            if not known:
                added.append(_register(project, registry, directory / outputs["image"]["path"], {
                    "asset_id": request["asset_id"], "kind": request["asset_kind"], "canon_id": request.get("canon_id"),
                    "visual_id": request.get("visual_id"), "view": request["view"],
                    "request_sha256": request["request_sha256"]}, "generated"))
    save_registry(project, registry)
    return added


def approve_asset(project: Project, canon: Canon, asset_id: str, version: int, reviewer: str) -> dict[str, Any]:
    if not reviewer.strip():
        raise ConfigError("a reviewer name is required")
    registry = load_registry(project, canon)
    asset = next((a for a in registry["assets"] if a["asset_id"] == asset_id and a["version"] == version), None)
    if asset is None:
        raise ConfigError(f"unknown asset {asset_id} v{version}")
    file = contained_path(references_root(project), asset["path"])
    if not file.is_file() or sha256_file(file) != asset["sha256"]:
        raise GateFailure(f"{asset_id} v{version}: file does not match its recorded hash")
    asset["status"], asset["approved_by"] = "approved", reviewer.strip()
    save_registry(project, registry)
    return asset


# ---------------------------------------------------------------- reference-sheet tasks

def sheet_store(project: Project) -> Path:
    return project.artifacts_dir / "tasks" / "references"


def sheet_tasks(project: Project, canon: Canon, models: dict[str, Any], scheduler: Scheduler) -> list[Task]:
    """One task per (canon id, view) that has no registered image for its current request."""
    registry = load_registry(project, canon)
    tasks = []
    for request in sheet_requests(canon, registry, models):
        if any(a["asset_id"] == request["asset_id"] and (
                a["status"] == "approved" or a.get("request_sha256") == request["request_sha256"])
               for a in registry["assets"]):
            continue  # already approved, or already generated for exactly this request
        def preflight(request=request):
            sdxl_preflight(project, models)
            fresh = next(r for r in sheet_requests(canon, load_registry(project, canon), models)
                         if r["asset_id"] == request["asset_id"])
            if fresh["request_sha256"] != request["request_sha256"]:
                raise GateFailure(f"{request['asset_id']}: references changed since planning")
            require_references(fresh, models)
        def verify(directory, request=request):
            if read_json(directory / "request.json") != request:
                raise TaskFailed(f"{request['asset_id']}: stored request differs from the planned request")
            info = probe(directory / "keyframe.png")
            if (info.width, info.height) != (request["width"], request["height"]):
                raise TaskFailed(f"{request['asset_id']}: decoded size differs from the request")
        task = Task("keyframe", f"sheet_{request['asset_id']}", {"request": request["request_sha256"],
                    "sdxl": sha256_obj(models.get("sdxl"))}, "reference-sheet-v1", lambda work: {},
                    max_attempts=1, preflight=preflight, verify=verify)
        journal = scheduler.store / "pending" / f"{task.task_id()}.json"
        task.journal = journal
        task.run = lambda work, request=request, journal=journal: sdxl_generate(project, models, request, journal, work)
        tasks.append(task)
    return tasks
