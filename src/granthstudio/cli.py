"""Command-line entry point: ``granthstudio <command>``.

Exit codes: 0 ok, 1 configuration or usage error, 2 refused or gate failed,
3 NOT VALIDATED integration (nothing was produced).
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import __version__
from .canon import load_canon
from .config import Project, load_models, load_project, load_quality_gates
from .episodes import compile_episode, episode_dir, load_manifest
from .errors import ConfigError, GranthError
from .ffmpeg import probe
from .integrity import atomic_write_json, read_json
from .pilot import RECOVERY_CHECK, plan_pilot, score_receipts
from .pipeline import episode_store, hard_gates, load_bundle, plan_tasks, snapshot
from .qa import write_report
from .research import approve, load_research, require_approved, verify_source
from .runtime import (bootstrap_plan, fetch, get_storage, gpu_status, load_runtime, preflight, ram_available_mb,
                      require_gpu_ready, require_single_worker, stop_before_deadline, verify_downloads, write_run_receipt)
from .scheduler import Scheduler

EXIT_OK, EXIT_ERROR, EXIT_REFUSED, EXIT_NOT_VALIDATED = 0, 1, 2, 3


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _find_root() -> Path:
    env = os.environ.get("GRANTHSTUDIO_ROOT")
    if env:
        return Path(env)
    here = Path.cwd().resolve()
    for candidate in (here, *here.parents):
        if (candidate / "config" / "project.yaml").is_file():
            return candidate
    raise ConfigError("project root not found: run inside the repository, set GRANTHSTUDIO_ROOT or pass --root")


def _project(args: argparse.Namespace) -> Project:
    return load_project(Path(args.root) if args.root else _find_root())


def cmd_version(_args: argparse.Namespace) -> int:
    print(f"granthstudio {__version__}")
    return EXIT_OK


def cmd_config(args: argparse.Namespace) -> int:
    project = _project(args)
    models = load_models(project)
    summary = {
        "root": str(project.root),
        "artifacts_dir": str(project.artifacts_dir),
        "research_dir": str(project.research_dir),
        "canon_dir": str(project.canon_dir),
        "episodes_dir": str(project.episodes_dir),
        "benchmarks_dir": str(project.benchmarks_dir),
        "comfyui_base_url": models["comfyui"]["base_url"],
        "ltx_capabilities": models["ltx"]["capabilities"],
        "ltx_checkpoint_pinned": models["ltx"]["checkpoint_sha256"] is not None,
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return EXIT_OK


def cmd_validate(args: argparse.Namespace) -> int:
    project = _project(args)
    load_models(project)
    load_quality_gates(project)
    load_canon(project)
    print("config, models, quality gates and canon: valid")
    for folder in sorted(project.research_dir.glob("adhyay_*")):
        number = int(folder.name.split("_")[1])
        load_research(project, number)
        print(f"research adhyay {number}: schema valid")
    for folder in sorted(project.episodes_dir.glob("adhyay_*")):
        number = int(folder.name.split("_")[1])
        load_manifest(project, number)
        print(f"episode manifest adhyay {number}: schema valid")
    return EXIT_OK


def cmd_research_status(args: argparse.Namespace) -> int:
    status = verify_source(_project(args), args.adhyay)
    print(json.dumps(asdict(status), indent=2))
    return EXIT_OK


def cmd_research_approve(args: argparse.Namespace) -> int:
    if not args.confirm:
        raise ConfigError("approval needs --confirm after a human has reviewed research.yaml")
    receipt = approve(_project(args), args.adhyay, args.reviewer, _now())
    print(f"approved adhyay {args.adhyay} as version {receipt['version']}")
    return EXIT_OK


def cmd_canon_check(args: argparse.Namespace) -> int:
    canon = load_canon(_project(args))
    counts = {kind: len(doc["entries"]) for kind, doc in canon.documents.items()}
    print(f"canon valid: {counts}; digest {canon.digest()[:16]}")
    return EXIT_OK


def cmd_episode_compile(args: argparse.Namespace) -> int:
    project = _project(args)
    models = load_models(project)
    canon = load_canon(project)
    research = load_research(project, args.adhyay)
    receipt = require_approved(project, args.adhyay)
    compiled = compile_episode(project, models, canon, args.adhyay, research, receipt)
    target = episode_dir(project, args.adhyay) / "compiled.json"
    atomic_write_json(target, compiled)
    print(f"compiled {compiled['episode_id']}: {len(compiled['shots'])} shots -> {target}")
    return EXIT_OK


def cmd_timeline_check(args: argparse.Namespace) -> int:
    project = _project(args)
    bundle = load_bundle(project, load_models(project), args.adhyay)
    print(f"timelines valid: {len(bundle.compiled['shots'])} shots, MR and HI aligned")
    return EXIT_OK


def cmd_plan(args: argparse.Namespace) -> int:
    project = _project(args)
    bundle = load_bundle(project, load_models(project), args.adhyay)
    tasks = plan_tasks(bundle, Scheduler(episode_store(project, args.adhyay)))
    for task in tasks:
        print(f"planned  {task.stage:<9} {task.name:<26} {task.task_id()}")
    print("dry run: nothing executed. Use 'run --execute' to run it.")
    return EXIT_OK


def _execute_plan(project, args, kind="episode_run", require_gpu=False):
    """Run the plan with a session-deadline stop, then write the run receipt and QA report."""
    started = _now()
    runtime = load_runtime(project)
    require_single_worker(runtime)
    models = load_models(project)
    report = preflight(project, models, runtime, gpu_status(), ram_available_mb())
    if require_gpu:
        require_gpu_ready(report)
    bundle = load_bundle(project, models, args.adhyay)
    scheduler = Scheduler(episode_store(project, args.adhyay))
    tasks = plan_tasks(bundle, scheduler)
    results = scheduler.run(tasks, should_stop=stop_before_deadline(runtime))
    for result in results:
        print(f"{result.status:<13} {result.stage:<9} {result.name:<26} {result.detail}")
    gates = hard_gates(bundle, results)
    path = write_report(project, args.adhyay, gates, snapshot(bundle))
    receipt = write_run_receipt(project, kind, args.adhyay, started, results, gates, snapshot(bundle), report,
                                scheduler.store)
    released = all(g.passed for g in gates)
    print(f"QA report {path}: released={released}")
    print(f"run receipt {receipt}")
    if any(r.status == "not_validated" for r in results):
        return EXIT_NOT_VALIDATED
    return EXIT_OK if released else EXIT_REFUSED


def cmd_run(args: argparse.Namespace) -> int:
    project = _project(args)
    if not args.execute:
        bundle = load_bundle(project, load_models(project), args.adhyay)
        for task in plan_tasks(bundle, Scheduler(episode_store(project, args.adhyay))):
            print(f"planned  {task.stage:<9} {task.name:<26} {task.task_id()}")
        print("dry run: nothing executed. Add --execute to run; NOT VALIDATED stages will refuse.")
        return EXIT_OK
    return _execute_plan(project, args)


def cmd_session(args: argparse.Namespace) -> int:
    """Kaggle entry point: restore durable artifacts, GPU preflight, run, export (frozen sections 8-9)."""
    project = _project(args)
    storage = get_storage(load_runtime(project))
    if (storage.root / args.export_name / "export_manifest.json").is_file():
        storage.restore(args.export_name, project.artifacts_dir)
    try:
        return _execute_plan(project, args, require_gpu=not args.cpu_only)
    finally:
        storage.export(project.artifacts_dir, args.export_name)
        print(f"exported artifacts to {storage.root / args.export_name}")


def _journal(project, args):
    """The durable submission journal of one LTX shot task in the episode store."""
    bundle = load_bundle(project, load_models(project), args.adhyay)
    scheduler = Scheduler(episode_store(project, args.adhyay))
    task = next((t for t in plan_tasks(bundle, scheduler) if t.name == args.shot), None)
    if task is None or task.stage not in ("tier1", "tier2"):
        raise ConfigError(f"{args.shot} is not an LTX shot task in adhyay {args.adhyay}")
    path = scheduler.store / "pending" / f"{task.task_id()}.json"
    if not path.is_file():
        raise ConfigError(f"no submission journal for {args.shot}")
    return bundle, path


def cmd_comfy_inspect(args: argparse.Namespace) -> int:
    """Server and workflow compatibility: required nodes and the pinned checkpoint binding."""
    from .comfy import ComfyBackend, check_checkpoint_binding, load_template, node_types
    from .integrity import contained_path
    project = _project(args)
    models = load_models(project)
    backend = ComfyBackend(models["comfyui"]["base_url"])
    available = set(backend.object_info())
    report = {"system_stats": backend.system_stats(), "workflows": {}}
    for capability, relative in models["ltx"]["workflow_templates"].items():
        template = load_template(contained_path(project.root, relative))
        entry = {"status": template.status, "version": template.version}
        try:
            graph = json.loads(template.text)
            entry["missing_nodes"] = sorted(node_types(graph) - available)
            check_checkpoint_binding(template, models["ltx"]["checkpoint_file"])
            entry["checkpoint_binding"] = "ok"
        except (ConfigError, KeyError, TypeError, ValueError) as exc:
            entry["checkpoint_binding"] = f"NOT VALIDATED: {exc}"
        report["workflows"][capability] = entry
    print(json.dumps(report, indent=2, ensure_ascii=False))
    ok = all(w["status"] == "validated" and not w.get("missing_nodes") and w["checkpoint_binding"] == "ok"
             for w in report["workflows"].values())
    return EXIT_OK if ok else EXIT_NOT_VALIDATED


def cmd_comfy_reconcile(args: argparse.Namespace) -> int:
    from .comfy import ComfyBackend, reconcile
    bundle, path = _journal(_project(args), args)
    state = reconcile(ComfyBackend(bundle.models["comfyui"]["base_url"]), path, args.declare_lost)
    print(f"{args.shot}: journal state {state['state']}")
    return EXIT_OK


def cmd_comfy_cancel(args: argparse.Namespace) -> int:
    from .comfy import ComfyBackend, cancel
    bundle, path = _journal(_project(args), args)
    state = cancel(ComfyBackend(bundle.models["comfyui"]["base_url"]), path)
    print(f"{args.shot}: cancellation requested for prompt {state['prompt_id']}; run 'comfy reconcile' next")
    return EXIT_OK


def _canon_models(project):
    return load_canon(project), load_models(project)


def cmd_refs_status(args: argparse.Namespace) -> int:
    from . import keyframes
    project = _project(args)
    canon, models = _canon_models(project)
    registry = keyframes.load_registry(project, canon)
    style = registry["style"]
    print(f"style: {'none' if style is None else style['style_id'] + ' v' + str(style['version']) + ' ' + style['status']}")
    print(f"sdxl: {(models.get('sdxl') or {}).get('status', 'not configured')} (NOT VALIDATED unless 'validated' after a real run)")
    for asset in registry["assets"]:
        print(f"{asset['asset_id']:<34} v{asset['version']:<3} {asset['kind']:<16} {asset['status']:<9} {asset['sha256'][:12]}")
    for request in keyframes.sheet_requests(canon, registry, models):
        if request["missing_references"]:
            print(f"blocked  {request['asset_id']}: missing {request['missing_references']}")
    return EXIT_OK


def cmd_refs_import(args: argparse.Namespace) -> int:
    from . import keyframes
    project = _project(args)
    asset = keyframes.import_asset(project, load_canon(project), args.asset_id, args.kind, args.canon_id,
                                   args.visual_id, args.view, args.file)
    print(f"registered {asset['asset_id']} v{asset['version']} as {asset['status']} ({asset['sha256'][:12]}); approve it after review")
    return EXIT_OK


def cmd_refs_generate(args: argparse.Namespace) -> int:
    from . import keyframes
    project = _project(args)
    canon, models = _canon_models(project)
    scheduler = Scheduler(keyframes.sheet_store(project))
    tasks = keyframes.sheet_tasks(project, canon, models, scheduler)
    if not args.execute:
        for task in tasks:
            print(f"planned  {task.name:<40} {task.task_id()}")
        print("dry run: add --execute (needs a validated SDXL setup)")
        return EXIT_OK
    results = scheduler.run(tasks, should_stop=stop_before_deadline(load_runtime(project)))
    for result in results:
        print(f"{result.status:<13} {result.name:<40} {result.detail}")
    return EXIT_NOT_VALIDATED if any(r.status == "not_validated" for r in results) else (
        EXIT_OK if all(r.status in ("complete", "resumed") for r in results) else EXIT_REFUSED)


def cmd_refs_collect(args: argparse.Namespace) -> int:
    from . import keyframes
    project = _project(args)
    stores = [keyframes.sheet_store(project), *(episode_store(project, n) for n in args.adhyay)]
    added = keyframes.collect_generated(project, load_canon(project), [s for s in stores if s.is_dir()])
    for asset in added:
        print(f"registered pending {asset['asset_id']} v{asset['version']}")
    print(f"{len(added)} new generated asset(s); none are approved")
    return EXIT_OK


def cmd_refs_approve(args: argparse.Namespace) -> int:
    from . import keyframes
    if not args.confirm:
        raise ConfigError("approval needs --confirm after a human has reviewed the image")
    project = _project(args)
    asset = keyframes.approve_asset(project, load_canon(project), args.asset_id, args.version, args.reviewer)
    print(f"approved {asset['asset_id']} v{asset['version']} bound to sha256 {asset['sha256'][:16]}")
    return EXIT_OK


def cmd_runtime_preflight(args: argparse.Namespace) -> int:
    project = _project(args)
    report = preflight(project, load_models(project), load_runtime(project), gpu_status(), ram_available_mb())
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.gpu:
        require_gpu_ready(report)
    return EXIT_OK


def _download(project, name):
    item = next((d for d in load_runtime(project)["downloads"] if d["name"] == name), None)
    if item is None:
        raise ConfigError(f"no download named {name!r} in runtime.yaml")
    return item


def cmd_runtime_fetch(args: argparse.Namespace) -> int:
    from .integrity import contained_path
    item = _download(_project(args), args.name)
    digest = fetch(item["url"], contained_path(args.base, item["dest"]), item["sha256"], record=args.record)
    note = "" if item["sha256"] else " (RECORD ONLY: review, then pin it; nothing validated)"
    print(f"{args.name}: sha256 {digest}{note}")
    return EXIT_OK


def cmd_runtime_verify(args: argparse.Namespace) -> int:
    status = verify_downloads(load_runtime(_project(args)), args.base)
    print(json.dumps(status, indent=2))
    return EXIT_OK if status and all(v == "verified" for v in status.values()) else EXIT_NOT_VALIDATED


def cmd_runtime_export(args: argparse.Namespace) -> int:
    project = _project(args)
    manifest = get_storage(load_runtime(project)).export(project.artifacts_dir, args.name)
    print(f"exported {len(manifest['files'])} files as {args.name}")
    return EXIT_OK


def cmd_runtime_restore(args: argparse.Namespace) -> int:
    project = _project(args)
    manifest = get_storage(load_runtime(project)).restore(args.name, project.artifacts_dir)
    print(f"restored and verified {len(manifest['files'])} files from {args.name}")
    return EXIT_OK


def cmd_runtime_bootstrap(args: argparse.Namespace) -> int:
    import subprocess
    commands = bootstrap_plan(load_runtime(_project(args)), args.workdir)
    for command in commands:
        print(" ".join(command))
        if args.execute:
            subprocess.run(command, check=True)
    if not args.execute:
        print("dry run: add --execute on the GPU host")
    return EXIT_OK


def cmd_report(args: argparse.Namespace) -> int:
    project = _project(args)
    bundle = load_bundle(project, load_models(project), args.adhyay)
    scheduler = Scheduler(episode_store(project, args.adhyay))
    results = scheduler.status(plan_tasks(bundle, scheduler))
    gates = hard_gates(bundle, results)
    path = write_report(project, args.adhyay, gates, snapshot(bundle))
    released = all(g.passed for g in gates)
    print(f"QA report {path}: released={released}")
    return EXIT_OK if released else EXIT_REFUSED


def cmd_ffprobe(args: argparse.Namespace) -> int:
    print(json.dumps(asdict(probe(args.file)), indent=2))
    return EXIT_OK


def cmd_pilot_plan(args: argparse.Namespace) -> int:
    project = _project(args)
    bundle = load_bundle(project, load_models(project), args.adhyay)
    mapping = plan_pilot(bundle.compiled)
    for label, shot_id in mapping.items():
        print(f"{label}  {shot_id}")
    print(f"recovery: {RECOVERY_CHECK}")
    return EXIT_OK


def cmd_pilot_score(args: argparse.Namespace) -> int:
    receipts: list[dict[str, Any]] = []
    for path in sorted(args.receipts_dir.rglob("*.json")):
        receipts.append(read_json(path))
    print(json.dumps(score_receipts(receipts), indent=2))
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="granthstudio", description="GranthStudio Zero-DB v3.1 runner")
    parser.add_argument("--root", help="project root (default: search upward for config/project.yaml)")
    parser.add_argument("-v", "--verbose", action="store_true", help="debug logging")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("version", help="print version").set_defaults(handler=cmd_version)
    commands.add_parser("config", help="show resolved configuration").set_defaults(handler=cmd_config)
    commands.add_parser("validate", help="validate schemas, canon, research and manifests").set_defaults(handler=cmd_validate)

    research = commands.add_parser("research", help="research approval")
    research_actions = research.add_subparsers(dest="action", required=True)
    status = research_actions.add_parser("status", help="show approval state")
    status.add_argument("adhyay", type=int)
    status.set_defaults(handler=cmd_research_status)
    approve_cmd = research_actions.add_parser("approve", help="record an approval version")
    approve_cmd.add_argument("adhyay", type=int)
    approve_cmd.add_argument("--reviewer", required=True)
    approve_cmd.add_argument("--confirm", action="store_true")
    approve_cmd.set_defaults(handler=cmd_research_approve)

    canon = commands.add_parser("canon", help="canon registry")
    canon.add_subparsers(dest="action", required=True).add_parser("check").set_defaults(handler=cmd_canon_check)

    episode = commands.add_parser("episode", help="episode manifests")
    episode_actions = episode.add_subparsers(dest="action", required=True)
    compile_cmd = episode_actions.add_parser("compile", help="compile the manifest for one adhyay")
    compile_cmd.add_argument("adhyay", type=int)
    compile_cmd.set_defaults(handler=cmd_episode_compile)

    timeline = commands.add_parser("timeline", help="Marathi and Hindi timelines")
    timeline_actions = timeline.add_subparsers(dest="action", required=True)
    timeline_check = timeline_actions.add_parser("check", help="run the bilingual gates")
    timeline_check.add_argument("adhyay", type=int)
    timeline_check.set_defaults(handler=cmd_timeline_check)

    for name, handler, text in (
        ("plan", cmd_plan, "list the stage plan (no execution)"),
        ("run", cmd_run, "run the stage plan"),
        ("report", cmd_report, "write the QA report from existing receipts"),
    ):
        sub = commands.add_parser(name, help=text)
        sub.add_argument("adhyay", type=int)
        if name == "run":
            sub.add_argument("--execute", action="store_true", help="really run the tasks")
        sub.set_defaults(handler=handler)

    session = commands.add_parser("session", help="Kaggle session: restore, preflight, run, export")
    session.add_argument("adhyay", type=int)
    session.add_argument("--export-name", default="artifacts")
    session.add_argument("--cpu-only", action="store_true", help="skip the GPU preflight requirement")
    session.set_defaults(handler=cmd_session)

    runtime = commands.add_parser("runtime", help="GPU host preflight, weights and durable storage")
    runtime_actions = runtime.add_subparsers(dest="action", required=True)
    pre = runtime_actions.add_parser("preflight", help="resource and configuration checks")
    pre.add_argument("--gpu", action="store_true", help="fail unless every GPU check passes")
    pre.set_defaults(handler=cmd_runtime_preflight)
    models_dir = Path("/kaggle/working/ComfyUI/models")
    fetch_cmd = runtime_actions.add_parser("fetch", help="download one pinned weight file and verify it")
    fetch_cmd.add_argument("name")
    fetch_cmd.add_argument("--base", type=Path, default=models_dir)
    fetch_cmd.add_argument("--record", action="store_true", help="unpinned: download and print the hash only")
    fetch_cmd.set_defaults(handler=cmd_runtime_fetch)
    verify_cmd = runtime_actions.add_parser("verify", help="verify downloaded weights against pins")
    verify_cmd.add_argument("--base", type=Path, default=models_dir)
    verify_cmd.set_defaults(handler=cmd_runtime_verify)
    for name, handler in (("export", cmd_runtime_export), ("restore", cmd_runtime_restore)):
        sub_cmd = runtime_actions.add_parser(name, help=f"{name} artifacts to/from durable storage")
        sub_cmd.add_argument("--name", default="artifacts")
        sub_cmd.set_defaults(handler=handler)
    boot = runtime_actions.add_parser("bootstrap", help="reproduce the GPU host from pins")
    boot.add_argument("--workdir", type=Path, default=Path("/kaggle/working"))
    boot.add_argument("--execute", action="store_true")
    boot.set_defaults(handler=cmd_runtime_bootstrap)

    refs = commands.add_parser("refs", help="visual canon: reference sheets and keyframe assets")
    refs_actions = refs.add_subparsers(dest="action", required=True)
    refs_actions.add_parser("status", help="style, assets and blocked requests").set_defaults(handler=cmd_refs_status)
    imp = refs_actions.add_parser("import", help="register a hand-supplied reference image (pending)")
    imp.add_argument("asset_id")
    imp.add_argument("--kind", required=True, choices=["character_sheet", "location", "prop", "keyframe"])
    imp.add_argument("--canon-id")
    imp.add_argument("--visual-id")
    imp.add_argument("--view", required=True)
    imp.add_argument("--file", required=True, type=Path)
    imp.set_defaults(handler=cmd_refs_import)
    gen = refs_actions.add_parser("generate", help="plan or run reference-sheet generation")
    gen.add_argument("--execute", action="store_true")
    gen.set_defaults(handler=cmd_refs_generate)
    col = refs_actions.add_parser("collect", help="register generated images as pending assets")
    col.add_argument("--adhyay", type=int, action="append", default=[])
    col.set_defaults(handler=cmd_refs_collect)
    appr = refs_actions.add_parser("approve", help="human approval bound to the image hash")
    appr.add_argument("asset_id")
    appr.add_argument("--version", type=int, required=True)
    appr.add_argument("--reviewer", required=True)
    appr.add_argument("--confirm", action="store_true")
    appr.set_defaults(handler=cmd_refs_approve)

    comfy = commands.add_parser("comfy", help="ComfyUI server compatibility and job control")
    comfy_actions = comfy.add_subparsers(dest="action", required=True)
    comfy_actions.add_parser("inspect", help="required nodes, workflow status and checkpoint binding").set_defaults(
        handler=cmd_comfy_inspect)
    for name, handler in (("reconcile", cmd_comfy_reconcile), ("cancel", cmd_comfy_cancel)):
        sub_cmd = comfy_actions.add_parser(name, help=f"{name} one LTX shot's ComfyUI job")
        sub_cmd.add_argument("adhyay", type=int)
        sub_cmd.add_argument("shot")
        if name == "reconcile":
            sub_cmd.add_argument("--declare-lost", action="store_true",
                                 help="operator confirmed the job is not on the server; allow resubmission")
        sub_cmd.set_defaults(handler=handler)

    ffprobe = commands.add_parser("ffprobe", help="probe a media file")
    ffprobe.add_argument("file", type=Path)
    ffprobe.set_defaults(handler=cmd_ffprobe)

    pilot = commands.add_parser("pilot", help="A-F pilot")
    pilot_actions = pilot.add_subparsers(dest="action", required=True)
    pilot_plan = pilot_actions.add_parser("plan", help="map shots A-F for one adhyay")
    pilot_plan.add_argument("adhyay", type=int)
    pilot_plan.set_defaults(handler=cmd_pilot_plan)
    pilot_score = pilot_actions.add_parser("score", help="accepted seconds per GPU-hour from receipts")
    pilot_score.add_argument("receipts_dir", type=Path)
    pilot_score.set_defaults(handler=cmd_pilot_score)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING, format="%(levelname)s %(message)s")
    try:
        return int(args.handler(args))
    except GranthError as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return int(getattr(exc, "exit_code", EXIT_REFUSED))
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_ERROR
