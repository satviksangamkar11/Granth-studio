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
from .pipeline import episode_store, hard_gates, load_bundle, plan_tasks
from .qa import write_report
from .research import approve, load_research, require_approved, verify_source
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


def cmd_run(args: argparse.Namespace) -> int:
    project = _project(args)
    bundle = load_bundle(project, load_models(project), args.adhyay)
    scheduler = Scheduler(episode_store(project, args.adhyay))
    tasks = plan_tasks(bundle, scheduler)
    if not args.execute:
        for task in tasks:
            print(f"planned  {task.stage:<9} {task.name:<26} {task.task_id()}")
        print("dry run: nothing executed. Add --execute to run; NOT VALIDATED stages will refuse.")
        return EXIT_OK
    results = scheduler.run(tasks)
    for result in results:
        print(f"{result.status:<13} {result.stage:<9} {result.name:<26} {result.detail}")
    gates = hard_gates(bundle, results)
    path = write_report(project, args.adhyay, gates)
    released = all(g.passed for g in gates)
    print(f"QA report {path}: released={released}")
    if any(r.status == "not_validated" for r in results):
        return EXIT_NOT_VALIDATED
    return EXIT_OK if released else EXIT_REFUSED


def cmd_report(args: argparse.Namespace) -> int:
    project = _project(args)
    bundle = load_bundle(project, load_models(project), args.adhyay)
    scheduler = Scheduler(episode_store(project, args.adhyay))
    results = scheduler.status(plan_tasks(bundle, scheduler))
    gates = hard_gates(bundle, results)
    path = write_report(project, args.adhyay, gates)
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
