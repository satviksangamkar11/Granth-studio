"""First real LTX 0.9.8 I2V compatibility test, run through the EXISTING GranthStudio pipeline.

What it does (on the GPU host, after the pinned sources and weights are in place and ComfyUI is running):
  1. static pin verification (scripts/verify_ltx_pins.py) - must exit 0, otherwise nothing is submitted;
  2. builds a SYNTHETIC project (tests/conftest.py fixtures: invented names, a test-pattern image; no Granth content);
  3. points models.yaml/runtime.yaml at the real files with hashes it computes from the bytes on disk;
  4. runs only the one Tier-1 shot task through load_bundle(benchmark=True) -> plan_tasks -> gate_gpu_tasks -> Scheduler.run,
     i.e. the same code path production would use (image staging, journal, readiness, frame/size rule, clip validation);
  5. writes test_receipt.json with a verdict. Even PASS only means "one clip decoded"; the capability stays `unvalidated`
     until a human reviews the clip (frozen section 15). FLF is not touched. Recovery / retry tests come later.

Without --execute it only prepares the project and prints the plan (no ComfyUI request, no GPU use).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402

SHOT = "a01_s01_sh02"                  # the synthetic Tier-1 (I2V) shot in tests/conftest.make_project
SOURCES = ("comfyui", "ltxvideo_nodes", "videohelpersuite", "kjnodes")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 22), b""):
            digest.update(block)
    return digest.hexdigest()


def git_head(path: Path) -> str:
    done = subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"], capture_output=True, text=True)
    return done.stdout.strip() if done.returncode == 0 else ""


def prepare_project(args: argparse.Namespace, pins: dict) -> "Project":  # noqa: F821
    from granthstudio.config import dump_yaml, load_models, load_project
    from granthstudio.research import approve
    from tests.conftest import FIXED_TIME, make_project

    root = args.workdir / "project"
    project = make_project(root)
    approve(project, 1, "synthetic-ltx-first-test", FIXED_TIME)       # synthetic fixture research only; never Granth content
    template = root / "workflows" / "comfyui" / "ltx_i2v_098.json"
    template.write_bytes((ROOT / pins["workflow"]["api_candidate"]).read_bytes())   # project-local copy; the shipped stub stays a stub
    checkpoint = next(f for f in pins["files"] if f["role"].startswith("ltx_checkpoint"))
    encoder = next(f for f in pins["files"] if f["role"] == "text_encoder")
    ckpt_path, enc_path = args.checkpoint_path, args.text_encoder_path
    ckpt_sha = sha256_file(ckpt_path)                                    # hashed from the real bytes, never copied from the pins
    models = load_models(project)
    models["comfyui"]["base_url"] = args.comfy_url
    models["ltx"].update(checkpoint_file=checkpoint["name"], checkpoint_sha256=ckpt_sha, precision="fp16",
                         capabilities={"i2v": "unvalidated", "flf": "disabled"})   # FLF stays off; i2v stays unvalidated
    models["ltx"]["workflow_templates"] = {"i2v": "workflows/comfyui/ltx_i2v_098.json", "flf": "workflows/comfyui/ltx_flf_098.json"}
    models["ltx"]["runtime"] = {
        "files": {"checkpoint": {"path": str(ckpt_path), "sha256": ckpt_sha}, "vae": None,   # VAE is embedded in the checkpoint
                  "text_encoder": {"path": str(enc_path), "sha256": sha256_file(enc_path)}},
        "comfyui_commit": git_head(args.source["comfyui"]) if "comfyui" in args.source else pins["sources"]["comfyui"]["commit"],
        "node_pack_commit": git_head(args.source["ltxvideo_nodes"]) if "ltxvideo_nodes" in args.source else pins["sources"]["ltxvideo_nodes"]["commit"],
        "gpu": "T4", "precision": "fp16", "width": args.width, "height": args.height}
    dump_yaml(root / "config" / "models.yaml", models)
    runtime = yaml.safe_load((root / "config" / "runtime.yaml").read_text(encoding="utf-8"))
    runtime["sources"].update(comfyui_commit=models["ltx"]["runtime"]["comfyui_commit"], node_pack_commit=models["ltx"]["runtime"]["node_pack_commit"],
                              comfyui_repo=pins["sources"]["comfyui"]["repo"], node_pack_repo=pins["sources"]["ltxvideo_nodes"]["repo"])
    runtime["resources"] = {"min_free_vram_mb": args.min_free_vram_mb, "min_ram_mb": args.min_ram_mb, "min_disk_gb": args.min_disk_gb,
                            "min_session_remaining_s": args.min_session_s}      # first-test floors, NOT throughput budgets (O-004)
    runtime["storage"] = {"provider": "local_dir", "path": str(args.workdir / "durable")}
    runtime["python_packages"] = installed_versions(("pyyaml", "jsonschema"))      # recorded from this host at test time
    dump_yaml(root / "config" / "runtime.yaml", runtime)
    return load_project(root)


def installed_versions(names) -> dict[str, str]:
    from importlib import metadata
    return {n: metadata.version(n) for n in names}


# UNVERIFIED items the first test is allowed to carry, because running it is exactly what verifies them.
TOLERATED_UNVERIFIED = {"workflow:model_names"}


def static_ok(report: Path, exit_code: int) -> tuple[bool, str]:
    if exit_code == 0:
        return True, "all checks PASS"
    if exit_code != 2 or not report.is_file():
        return False, f"verify_ltx_pins exited {exit_code} (MISSING/MISMATCH or no report)"
    open_items = {r["check"] for r in json.loads(report.read_text(encoding="utf-8"))["results"] if r["status"] != "PASS"}
    extra = sorted(open_items - TOLERATED_UNVERIFIED)
    return (not extra), (f"only tolerated UNVERIFIED items remain: {sorted(open_items)}" if not extra else f"unverified/other items: {extra}")


def static_verification(args: argparse.Namespace, workflow_source: Path | None, out: Path, models_yaml: Path) -> dict:
    cmd = [sys.executable, str(ROOT / "scripts" / "verify_ltx_pins.py"), "--models-dir", str(args.models_dir),
           "--api-workflow", str(ROOT / "workflows" / "comfyui" / "ltx_i2v_098.candidate.json"),
           "--models-yaml", str(models_yaml), "--json", str(out)]
    for name, path in args.source.items():
        cmd += ["--source", f"{name}={path}"]
    if workflow_source:
        cmd += ["--workflow", str(workflow_source)]
    if args.node_inventory:
        cmd += ["--node-inventory", str(args.node_inventory)]
    done = subprocess.run(cmd, capture_output=True, text=True)
    return {"command": cmd, "exit": done.returncode, "output": done.stdout[-6000:]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--workdir", required=True, type=Path)
    parser.add_argument("--comfy-url", default="http://127.0.0.1:8188")
    parser.add_argument("--models-dir", required=True, type=Path, help="ComfyUI root holding models/checkpoints and models/text_encoders")
    parser.add_argument("--checkpoint-path", type=Path)
    parser.add_argument("--text-encoder-path", type=Path)
    parser.add_argument("--source", action="append", default=[], metavar="NAME=PATH", help=f"git checkouts: {', '.join(SOURCES)}")
    parser.add_argument("--node-inventory", type=Path, help="saved /object_info of the running server")
    parser.add_argument("--official-workflow", type=Path, help="the official ui workflow file inside the LTXVideo checkout")
    parser.add_argument("--width", type=int, default=768)
    parser.add_argument("--height", type=int, default=512)
    parser.add_argument("--min-free-vram-mb", type=float, default=10000)
    parser.add_argument("--min-ram-mb", type=float, default=12000)
    parser.add_argument("--min-disk-gb", type=float, default=30)
    parser.add_argument("--min-session-s", type=float, default=1800)
    parser.add_argument("--skip-static-verify", action="store_true", help="CPU plumbing tests only: the verdict can then never be PASS")
    parser.add_argument("--execute", action="store_true", help="really submit to ComfyUI (GPU); without it only prepare and print the plan")
    args = parser.parse_args(argv)
    args.source = {k: Path(v) for k, v in (item.split("=", 1) for item in args.source)}
    models_dir = args.models_dir
    args.checkpoint_path = args.checkpoint_path or models_dir / "models" / "checkpoints" / "ltxv-2b-0.9.8-distilled.safetensors"
    args.text_encoder_path = args.text_encoder_path or models_dir / "models" / "text_encoders" / "t5xxl_fp16.safetensors"
    args.workdir.mkdir(parents=True, exist_ok=True)
    pins = yaml.safe_load((ROOT / "config" / "ltx_098_pins.yaml").read_text(encoding="utf-8"))
    receipt: dict = {"schema_version": 1, "kind": "ltx_first_i2v_test", "started": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                     "harness_commit": git_head(ROOT), "pins_status": pins["status"], "shot": SHOT,
                     "note": "A PASS means one clip decoded through the existing pipeline. The i2v capability stays 'unvalidated' until a human reviews the clip."}

    def finish(verdict: str, reason: str) -> int:
        receipt.update(verdict=verdict, reason=reason, finished=datetime.now(timezone.utc).isoformat(timespec="seconds"))
        (args.workdir / "test_receipt.json").write_text(json.dumps(receipt, indent=2, default=str), encoding="utf-8")
        print(f"VERDICT: {verdict} - {reason}\nreceipt: {args.workdir / 'test_receipt.json'}")
        return 0 if verdict == "PASS" else 1

    for path in (args.checkpoint_path, args.text_encoder_path):
        if not path.is_file():
            return finish("NOT_RUN", f"missing file {path} (downloads need the signed approval manifest)")
    project = prepare_project(args, pins)
    if args.skip_static_verify:
        receipt["static_verification"] = {"exit": None, "note": "SKIPPED by flag: this run can never be a PASS"}
    else:
        receipt["static_verification"] = static_verification(args, args.official_workflow, args.workdir / "pin_report.json",
                                                            project.root / "config" / "models.yaml")
        verdict_ok, why = static_ok(args.workdir / "pin_report.json", receipt["static_verification"]["exit"])
        receipt["static_verification"]["accepted"], receipt["static_verification"]["why"] = verdict_ok, why
        if not verdict_ok:
            return finish("NOT_RUN", f"static pin verification not acceptable: {why}")
    from granthstudio.config import load_models
    from granthstudio.pipeline import episode_store, load_bundle, plan_tasks
    from granthstudio.runtime import gate_gpu_tasks, gpu_status, load_runtime, preflight, ram_available_mb, write_run_receipt  # noqa: F401
    from granthstudio.scheduler import Scheduler

    models = load_models(project)
    bundle = load_bundle(project, models, 1, benchmark=True)         # benchmark mode: may run an unvalidated capability, pins still enforced
    scheduler = Scheduler(episode_store(project, 1))
    tasks = plan_tasks(bundle, scheduler)
    by_id = {t.task_id(): t for t in tasks}
    wanted = {t.task_id() for t in tasks if t.name == SHOT}
    stack = list(wanted)
    while stack:
        for dep in by_id[stack.pop()].depends_on:
            if dep not in wanted:
                wanted.add(dep); stack.append(dep)
    selected = [t for t in tasks if t.task_id() in wanted]
    print("plan:", [(t.stage, t.name) for t in selected])
    report = preflight(project, models, load_runtime(project), gpu_status(), ram_available_mb())
    receipt["preflight"] = report
    receipt["inputs"] = {"checkpoint_sha256": models["ltx"]["checkpoint_sha256"], "text_encoder_sha256": models["ltx"]["runtime"]["files"]["text_encoder"]["sha256"],
                         "comfyui_commit": models["ltx"]["runtime"]["comfyui_commit"], "node_pack_commit": models["ltx"]["runtime"]["node_pack_commit"],
                         "width": args.width, "height": args.height, "frames": 49, "fps": 24}
    if not args.execute:
        return finish("NOT_RUN", f"dry run (no --execute); preflight gpu_ready={report['gpu_ready']}")
    gate_gpu_tasks(selected, report)
    began = time.monotonic()
    results = scheduler.run(selected)
    receipt["wall_s"] = round(time.monotonic() - began, 1)
    receipt["results"] = [r.__dict__ for r in results]
    task = next(t for t in selected if t.name == SHOT)
    result = next(r for r in results if r.name == SHOT)
    directory = scheduler.task_dir(task)
    journal = scheduler.store / "pending" / f"{task.task_id()}.json"
    receipt["journal"] = json.loads(journal.read_text(encoding="utf-8")) if journal.is_file() else None
    if result.status == "not_validated":
        return finish("NOT_VALIDATED", result.detail)
    if result.status != "complete":
        return finish("FAIL", f"{result.status}: {result.detail}")
    from granthstudio.ffmpeg import probe
    info = probe(directory / "clip.mp4")
    receipt["clip"] = {"sha256": sha256_file(directory / "clip.mp4"), "width": info.width, "height": info.height,
                       "duration_s": info.video_duration_s if info.video_duration_s is not None else info.duration_s}
    receipt["metrics"] = json.loads((directory / "metrics.json").read_text(encoding="utf-8"))
    if (info.width, info.height) != (args.width, args.height):
        return finish("FAIL", f"decoded clip is {info.width}x{info.height}, requested {args.width}x{args.height}")
    if receipt["static_verification"]["exit"] is None:
        return finish("NOT_RUN", "clip decoded, but static verification was skipped, so this cannot be a PASS")
    return finish("PASS", "one clip decoded through the existing pipeline; the capability remains unvalidated pending human review")


if __name__ == "__main__":
    sys.exit(main())
