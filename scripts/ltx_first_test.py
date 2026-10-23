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
sys.path.insert(0, str(ROOT / "scripts" / "kaggle"))
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


VARIANT_B_ACTION = "slow camera push-in"


def make_variant_b(project) -> None:
    """A different synthetic shot: another test pattern and another (synthetic) approved action text. Runs BEFORE the synthetic research approval."""
    from granthstudio.config import dump_yaml, load_yaml
    from granthstudio.integrity import sha256_file as digest
    research_path = project.research_dir / "adhyay_01" / "research.yaml"
    research = load_yaml(research_path)
    research["scenes"][0]["actions"][0]["text"] = VARIANT_B_ACTION
    dump_yaml(research_path, research)
    manifest_path = project.episodes_dir / "adhyay_01" / "manifest.yaml"
    manifest = load_yaml(manifest_path)
    for shot in manifest["scenes"][0]["shots"]:
        if shot.get("motion_prompt"):
            shot["motion_prompt"] = VARIANT_B_ACTION
    visual = project.artifacts_dir / "visuals" / "vis" / "room.png"
    done = subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=640x360", "-frames:v", "1", str(visual)],
                          capture_output=True, text=True)
    if done.returncode != 0:
        raise RuntimeError(f"cannot create the variant-b still: {done.stderr}")
    manifest["visuals"][0]["sha256"] = digest(visual)
    dump_yaml(manifest_path, manifest)


def use_painted_start(project, args: argparse.Namespace) -> None:
    """Replace ONLY the synthetic start image and its text conditioning with the supplied painting and prompt. Runs BEFORE the synthetic research approval."""
    import shutil
    from granthstudio.config import dump_yaml, load_yaml
    from granthstudio.integrity import sha256_file as digest
    prompt = args.prompt_file.read_text(encoding="utf-8").strip()
    research_path = project.research_dir / "adhyay_01" / "research.yaml"
    research = load_yaml(research_path)
    research["scenes"][0]["actions"][0]["text"] = prompt
    dump_yaml(research_path, research)
    manifest_path = project.episodes_dir / "adhyay_01" / "manifest.yaml"
    manifest = load_yaml(manifest_path)
    for shot in manifest["scenes"][0]["shots"]:
        if shot.get("motion_prompt"):
            shot["motion_prompt"] = prompt
    visual = project.artifacts_dir / "visuals" / "vis" / "room.png"
    shutil.copyfile(args.start_image, visual)
    manifest["visuals"][0]["sha256"] = digest(visual)
    dump_yaml(manifest_path, manifest)
    style_source = ROOT / "canon" / "style.yaml"
    if style_source.is_file():                                   # the frozen project style governs this test's task identities and receipts
        shutil.copyfile(style_source, project.canon_dir / "style.yaml")


def prepare_project(args: argparse.Namespace, pins: dict) -> "Project":  # noqa: F821
    from granthstudio.config import dump_yaml, load_models, load_project
    from granthstudio.research import approve
    from tests.conftest import FIXED_TIME, make_project

    root = args.workdir / "project"
    if (root / "config" / "project.yaml").is_file():                   # rerun in the same workdir: keep the project (and its receipts) as it is
        project = load_project(root)
    else:
        project = make_project(root)
        if args.variant == "b":
            make_variant_b(project)
        if args.start_image:
            use_painted_start(project, args)
        approve(project, 1, "synthetic-ltx-first-test", FIXED_TIME)   # synthetic fixture research only; never Granth content
    template = root / "workflows" / "comfyui" / "ltx_i2v_098.json"
    template.write_bytes((ROOT / pins["workflow"]["api_candidate"]).read_bytes())   # project-local copy; the shipped stub stays a stub
    checkpoint = next(f for f in pins["files"] if f["role"].startswith("ltx_checkpoint"))
    encoder = next(f for f in pins["files"] if f["role"] == "text_encoder")
    ckpt_path, enc_path = args.checkpoint_path, args.text_encoder_path
    ckpt_sha = sha256_file(ckpt_path)                                    # hashed from the real bytes, never copied from the pins
    models = load_models(project)
    models["comfyui"]["base_url"] = args.comfy_url
    models["ltx"].update(checkpoint_file=checkpoint["name"], checkpoint_sha256=ckpt_sha, precision=args.precision,
                         capabilities={"i2v": "unvalidated", "flf": "disabled"})   # FLF stays off; i2v stays unvalidated
    models["ltx"]["workflow_templates"] = {"i2v": "workflows/comfyui/ltx_i2v_098.json", "flf": "workflows/comfyui/ltx_flf_098.json"}
    models["ltx"]["runtime"] = {
        "files": {"checkpoint": {"path": str(ckpt_path), "sha256": ckpt_sha}, "vae": None,   # VAE is embedded in the checkpoint
                  "text_encoder": {"path": str(enc_path), "sha256": sha256_file(enc_path)}},
        "comfyui_commit": git_head(args.source["comfyui"]) if "comfyui" in args.source else pins["sources"]["comfyui"]["commit"],
        "node_pack_commit": git_head(args.source["ltxvideo_nodes"]) if "ltxvideo_nodes" in args.source else pins["sources"]["ltxvideo_nodes"]["commit"],
        "gpu": "T4", "precision": args.precision, "width": args.width, "height": args.height}
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--workdir", required=True, type=Path)
    parser.add_argument("--comfy-url", default="http://127.0.0.1:8188")
    parser.add_argument("--models-dir", required=True, type=Path, help="ComfyUI root holding models/checkpoints and models/text_encoders")
    parser.add_argument("--checkpoint-path", type=Path)
    parser.add_argument("--text-encoder-path", type=Path)
    parser.add_argument("--source", action="append", default=[], metavar="NAME=PATH", help=f"git checkouts: {', '.join(SOURCES)}")
    parser.add_argument("--node-inventory", type=Path, help="saved /object_info of the running server")
    parser.add_argument("--official-workflow", type=Path, help="the official ui workflow file inside the LTXVideo checkout")
    parser.add_argument("--comfy-log", type=Path, help="ComfyUI's log; dtype/offload lines are copied into the receipt")
    parser.add_argument("--width", type=int, default=768)
    parser.add_argument("--height", type=int, default=512)
    parser.add_argument("--precision", default="fp32", choices=["fp16", "bf16", "fp32"],
                        help="EXPECTED working precision recorded in the config. On a T4 ComfyUI picks fp32 for LTXV (bf16/fp32 only, no native bf16); the log is the evidence")
    parser.add_argument("--min-free-vram-mb", type=float, default=10000)
    parser.add_argument("--min-ram-mb", type=float, default=12000)
    parser.add_argument("--min-disk-gb", type=float, default=30)
    parser.add_argument("--min-session-s", type=float, default=1800)
    parser.add_argument("--gpu-index", type=int, choices=[0, 1], help="PHYSICAL index of the one T4 this worker owns (required with --execute)")
    parser.add_argument("--variant", choices=["a", "b"], default="a", help="which synthetic shot: a = head-turn on a test pattern, b = camera push-in on another pattern")
    parser.add_argument("--start-image", type=Path, help="painted start image (PNG) used INSTEAD of the synthetic test pattern; hashed and recorded")
    parser.add_argument("--prompt-file", type=Path, help="descriptive positive text conditioning for the shot (with --start-image)")
    parser.add_argument("--negative-prompt-file", type=Path, help="recorded in the receipt; NOT applied while the workflow runs at cfg 1 (the workflow is deliberately unchanged)")
    parser.add_argument("--other-gpu-idle-mb", type=float, default=800, help="the OTHER card must show at most this much memory in use at start (isolation)")
    parser.add_argument("--allow-other-gpu-busy", action="store_true", help="concurrent stage: the other card is another worker's, so do not require it idle")
    parser.add_argument("--worker-pid", type=int, help="pid of the ComfyUI process this worker talks to (recorded in the receipt)")
    parser.add_argument("--cuda-visible-devices", help="CUDA_VISIBLE_DEVICES the ComfyUI worker was started with (recorded)")
    parser.add_argument("--retry-test", action="store_true",
                        help="after a PASS in the same --workdir: reject that output in the journal and run once more; the sampler must execute again with a changed seed")
    parser.add_argument("--skip-static-verify", action="store_true", help="CPU plumbing tests only (never accepted together with --execute by main())")
    parser.add_argument("--execute", action="store_true", help="really submit to ComfyUI (GPU); without it only prepare and print the plan")
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = build_parser()
    args = parser.parse_args(argv)
    if bool(args.start_image) != bool(args.prompt_file):
        parser.error("--start-image and --prompt-file go together: the painting and its descriptive text are the ONLY things that change")
    for name in ("start_image", "prompt_file", "negative_prompt_file"):
        path = getattr(args, name)
        if path is not None and not path.is_file():
            parser.error(f"--{name.replace('_', '-')} {path} is not a file")
    args.source = {k: Path(v) for k, v in (item.split("=", 1) for item in args.source)}
    args.checkpoint_path = args.checkpoint_path or args.models_dir / "models" / "checkpoints" / "ltxv-2b-0.9.8-distilled.safetensors"
    args.text_encoder_path = args.text_encoder_path or args.models_dir / "models" / "text_encoders" / "t5xxl_fp16.safetensors"
    return args


SAMPLE_FRAMES = (0, 1, 12, 24, 36, 48)
# Automatic drift screen for a supplied painting (a screen for a human, never an acceptance): similarity to frame 0 and the largest luma step between frames.
MIN_SSIM_FRAME_1, MIN_SSIM_LAST, MAX_LUMA_STEP = 0.60, 0.30, 40.0


def _ffmpeg(*cmd: str) -> subprocess.CompletedProcess:
    return subprocess.run(["ffmpeg", "-y", "-v", "error", *cmd], capture_output=True, text=True, timeout=300)


def _ssim(a: Path, b: Path) -> float | None:
    done = subprocess.run(["ffmpeg", "-v", "info", "-i", str(a), "-i", str(b), "-lavfi", "ssim", "-f", "null", "-"], capture_output=True, text=True, timeout=120)
    import re
    found = re.findall(r"SSIM .*All:([0-9.]+)", done.stderr)
    return float(found[-1]) if found else None


def visual_diagnostics(clip: Path, outdir: Path, start_image: Path | None) -> dict:
    """Frames 0, 1, 12, 24, 36, 48 as PNGs and a contact sheet, plus similarity numbers. Evidence for a human reviewer; it accepts nothing."""
    import re
    outdir.mkdir(parents=True, exist_ok=True)
    report: dict = {"sample_frames": list(SAMPLE_FRAMES), "contact_sheet": None, "ssim_vs_frame_0": {}, "ssim_frame_0_vs_input": None, "max_luma_step": None,
                    "thresholds": {"min_ssim_frame_1": MIN_SSIM_FRAME_1, "min_ssim_last": MIN_SSIM_LAST, "max_luma_step": MAX_LUMA_STEP},
                    "drift_suspected": None, "human_visual_review": "NOT_DONE"}
    pick = "+".join(f"eq(n,{n})" for n in SAMPLE_FRAMES)
    for n in SAMPLE_FRAMES:
        _ffmpeg("-i", str(clip), "-vf", f"select='eq(n,{n})'", "-frames:v", "1", str(outdir / f"frame_{n:02d}.png"))
    sheet = _ffmpeg("-i", str(clip), "-vf", f"select='{pick}',scale=384:-1,tile={len(SAMPLE_FRAMES)}x1", "-frames:v", "1", str(outdir / "contact_sheet.png"))
    report["contact_sheet"] = "contact_sheet.png" if sheet.returncode == 0 else None
    first = outdir / "frame_00.png"
    if first.is_file():
        for n in SAMPLE_FRAMES[1:]:
            frame = outdir / f"frame_{n:02d}.png"
            report["ssim_vs_frame_0"][str(n)] = _ssim(first, frame) if frame.is_file() else None
        if start_image is not None:
            report["ssim_frame_0_vs_input"] = _ssim(first, start_image)
    stats = subprocess.run(["ffmpeg", "-v", "error", "-i", str(clip), "-vf", "signalstats,metadata=print:file=-", "-an", "-f", "null", "-"], capture_output=True, text=True, timeout=300).stdout
    steps = [float(v) for v in re.findall(r"signalstats[.]YDIF=([0-9.]+)", stats)]
    report["max_luma_step"] = max(steps) if steps else None
    ssim = report["ssim_vs_frame_0"]
    if report["max_luma_step"] is not None and ssim.get("1") is not None and ssim.get("48") is not None:
        report["drift_suspected"] = bool(report["max_luma_step"] > MAX_LUMA_STEP or ssim["1"] < MIN_SSIM_FRAME_1 or ssim["48"] < MIN_SSIM_LAST)
    return report


def conditioning_from_workflow(pins: dict) -> dict:
    """The image-conditioning and sampling parameters of the (unchanged) workflow candidate, for the receipt."""
    graph = json.loads((ROOT / pins["workflow"]["api_candidate"]).read_text(encoding="utf-8"))
    pick = lambda node, *keys: {k: graph[node]["inputs"][k] for k in keys}
    return {"workflow": pins["workflow"]["api_candidate"], "LTXVImgToVideo": pick("95", "strength", "batch_size"), "LTXVPreprocess": pick("82", "img_compression"),
            "CFGGuider": pick("99", "cfg"), "sampler": pick("97", "sampler_name"), "sigmas": graph["100"]["inputs"]["string"], "checkpoint": graph["44"]["inputs"]["ckpt_name"]}


def physical_gpus() -> list[dict] | None:
    """All GPUs on the host with uuid (never filtered by GRANTHSTUDIO_GPU_INDEX)."""
    import host_check
    try:
        return host_check.parse_nvidia_smi(subprocess.run(host_check.QUERY, capture_output=True, text=True, timeout=30, check=True).stdout)
    except (OSError, subprocess.SubprocessError, ValueError):
        return None


def execution_gate_problems(args: argparse.Namespace) -> list[str]:
    """Refusals that apply to every real submission, whichever way this file is started."""
    import os
    problems = []
    if not os.environ.get("LTX_DOWNLOAD_APPROVED", "").strip():
        problems.append("LTX_DOWNLOAD_APPROVED is not set (the signed docs/LTX_098_DOWNLOAD_APPROVAL.md section E)")
    if args.skip_static_verify:
        problems.append("--skip-static-verify cannot be combined with --execute")
    from granthstudio.runtime import session_remaining_s
    gpus = physical_gpus()
    if gpus is None or sorted(g["index"] for g in gpus) != [0, 1] or any("Tesla T4" not in g["name"] for g in gpus):
        problems.append(f"the host must have exactly two Tesla T4 (physical indices 0 and 1), saw {[(g['index'], g['name']) for g in gpus] if gpus else gpus}")
    elif args.gpu_index is None:
        problems.append("--gpu-index (the physical card this worker owns) is required with --execute")
    elif not args.allow_other_gpu_busy:
        other = next(g for g in gpus if g["index"] != args.gpu_index)
        if other["memory_used_mb"] > args.other_gpu_idle_mb:
            problems.append(f"GPU {other['index']} must stay idle for this stage but already uses {other['memory_used_mb']:.0f} MiB")
    try:
        remaining = session_remaining_s()
    except Exception as exc:                       # an unparsable deadline is a refusal, not a crash
        remaining = None
        problems.append(f"invalid GRANTHSTUDIO_SESSION_DEADLINE: {exc}")
    if remaining is None or remaining < args.min_session_s:
        problems.append(f"GRANTHSTUDIO_SESSION_DEADLINE is missing/invalid or leaves {remaining} s (< {args.min_session_s})")
    return problems


OOM_PATTERNS = ("out of memory", "outofmemoryerror", "oom due to", "cuda error: out of memory", "cublas_status_alloc_failed")


def oom_markers(log: Path | None, detail: str = "") -> list[str]:
    """Lines of the ComfyUI log (and the task detail) that show a CUDA out-of-memory failure."""
    lines = [detail] if detail else []
    if log is not None and log.is_file():
        lines += log.read_text(encoding="utf-8", errors="replace").splitlines()[-400:]
    return [line.strip() for line in lines if any(p in line.lower() for p in OOM_PATTERNS)]


def comfy_log_excerpt(path: Path | None, limit: int = 120) -> list[str]:
    if path is None or not path.is_file():
        return []
    keys = ("dtype", "vram", "device", "offload", "loaded", "lowvram", "cast", "memory")
    return [line.rstrip()[:240] for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
            if any(k in line.lower() for k in keys)][:limit]


def _history_cached_nodes(base_url: str, prompt_id: str) -> list[str] | None:
    """Node ids ComfyUI reports as served from cache for this prompt ('execution_cached' status message), or None when it reports nothing."""
    from granthstudio.comfy import ComfyBackend
    entry = json.loads(ComfyBackend(base_url)._request("GET", f"/history/{prompt_id}")).get(prompt_id, {})
    for message in entry.get("status", {}).get("messages", []):
        if isinstance(message, list) and len(message) == 2 and message[0] == "execution_cached":
            return [str(n) for n in message[1].get("nodes", [])]
    return None


def _history_execution_window(base_url: str, prompt_id: str) -> dict | None:
    """ComfyUI's own execution_start / execution_success timestamps (epoch ms) for a prompt, or None when it reports none: the only evidence of when the
    GPU job itself ran, as opposed to the scheduler's surrounding preflight/hash/transfer time."""
    from granthstudio.comfy import ComfyBackend
    try:
        entry = json.loads(ComfyBackend(base_url)._request("GET", f"/history/{prompt_id}")).get(prompt_id, {})
    except Exception:  # noqa: BLE001 - evidence is optional here; the concurrent verdict refuses when it is missing
        return None
    stamps = {}
    for message in entry.get("status", {}).get("messages", []):
        if isinstance(message, list) and len(message) == 2 and message[0] in ("execution_start", "execution_success"):
            stamps[message[0]] = message[1].get("timestamp")
    if not isinstance(stamps.get("execution_start"), (int, float)) or not isinstance(stamps.get("execution_success"), (int, float)):
        return None
    return {"prompt_id": prompt_id, "start_ms": stamps["execution_start"], "end_ms": stamps["execution_success"]}


def _retry_test(args, receipt, finish, scheduler, selected, models) -> int:
    """Controlled output-rejection test, only after a PASS in the same workdir: reject the first output in the journal, drop its task receipt,
    run once more. The real sampler must execute again (not be served from cache) with a changed effective seed."""
    import shutil
    from granthstudio.comfy import reject_output
    from granthstudio.ffmpeg import probe
    task = next(t for t in selected if t.name == SHOT)
    directory = scheduler.task_dir(task)
    journal = scheduler.store / "pending" / f"{task.task_id()}.json"
    if not journal.is_file() or not (directory / "clip.mp4").is_file():
        return finish("NOT_RUN", "no completed first run in this workdir: nothing to reject")
    before = json.loads(journal.read_text(encoding="utf-8"))
    if before.get("state") != "completed":
        return finish("NOT_RUN", f"journal state is {before.get('state')!r}, not 'completed': the retry test needs a finished first clip")
    first = {"prompt_id": before["prompt_id"], "attempt": before["attempt"], "seed": before["history"][-1]["generation"].get("seed"),
             "fingerprint": before["history"][-1]["fingerprint"], "clip_sha256": sha256_file(directory / "clip.mp4"), "namespace": before.get("namespace")}
    receipt["first_output"] = first
    if not reject_output(journal, "controlled output-rejection test (synthetic): the decoded clip was fine; this checks the retry path"):
        return finish("FAIL", "the journal refused the rejection")
    shutil.rmtree(directory)                           # the sealed receipt described the rejected output; a fresh render must replace it
    began = time.monotonic()
    results = scheduler.run(selected)
    receipt["wall_s"] = round(time.monotonic() - began, 1)
    receipt["results"] = [r.__dict__ for r in results]
    result = next(r for r in results if r.name == SHOT)
    after = json.loads(journal.read_text(encoding="utf-8"))
    receipt["journal"] = after
    if result.status != "complete":
        oom = oom_markers(args.comfy_log, result.detail)
        receipt["out_of_memory"] = bool(oom)
        return finish("FAIL", ("CUDA out of memory; not retried further. " if oom else "") + f"{result.status}: {result.detail}")
    new = {"prompt_id": after["prompt_id"], "attempt": after["attempt"], "seed": after["history"][-1]["generation"].get("seed"),
           "fingerprint": after["history"][-1]["fingerprint"], "clip_sha256": sha256_file(scheduler.task_dir(task) / "clip.mp4")}
    receipt["second_output"] = new
    cached = _history_cached_nodes(args.comfy_url, new["prompt_id"])
    sampler_nodes = {item["node"] for item in after["history"][-1]["seed_inputs"]} | {"101"}
    checks = {
        "new_prompt_id": new["prompt_id"] != first["prompt_id"],
        "attempt_incremented": new["attempt"] == first["attempt"] + 1,
        "rejection_recorded": len(after.get("rejections", [])) == len(before.get("rejections", [])) + 1,
        "seed_changed": new["seed"] != first["seed"],
        "generation_fingerprint_changed": new["fingerprint"] != first["fingerprint"],
        "same_store_namespace": after.get("namespace") == first["namespace"],
        "output_differs": new["clip_sha256"] != first["clip_sha256"],
        "history_reports_cache": cached is not None,
        "sampler_executed_not_cached": cached is not None and not (sampler_nodes & set(cached)),
    }
    info = probe(scheduler.task_dir(task) / "clip.mp4")
    checks["decodes_at_requested_size"] = (info.width, info.height) == (args.width, args.height)
    receipt["retry_checks"] = checks
    receipt["cached_nodes_reported"] = cached
    failed = sorted(k for k, ok in checks.items() if not ok)
    if failed:
        return finish("FAIL", f"retry checks failed: {failed}")
    return finish("PASS", "the rejected output was replaced by a fresh generation: new prompt, changed seed on the sampler path, sampler executed (not cached)")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    return _run(args, enforce_gates=args.execute)


def _run(args: argparse.Namespace, enforce_gates: bool = True) -> int:
    """Everything after argument parsing. ``enforce_gates=False`` exists only so CPU plumbing tests can drive a fake server; main() always
    enforces the gates for --execute."""
    import os
    args.workdir.mkdir(parents=True, exist_ok=True)
    if args.gpu_index is not None:
        os.environ["GRANTHSTUDIO_GPU_INDEX"] = str(args.gpu_index)      # preflight and VRAM sampling then watch THIS physical card only
    pins = yaml.safe_load((ROOT / "config" / "ltx_098_pins.yaml").read_text(encoding="utf-8"))
    receipt: dict = {"schema_version": 1, "kind": "ltx_first_i2v_test", "started": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                     "harness_commit": git_head(ROOT), "pins_status": pins["status"], "shot": SHOT,
                     "approved_by": __import__("os").environ.get("LTX_DOWNLOAD_APPROVED", ""),
                     "expected_precision": args.precision, "variant": args.variant, "gpu_index": args.gpu_index,
                     "workdir": str(args.workdir), "cuda_visible_devices_of_worker": args.cuda_visible_devices, "worker_pid": args.worker_pid, "comfy_url": args.comfy_url,
                     "physical_gpus_at_start": physical_gpus() if args.execute else None,
                     "note": "A PASS means one clip decoded through the existing pipeline. The i2v capability stays 'unvalidated' until a human reviews the clip."}

    def finish(verdict: str, reason: str) -> int:
        receipt.update(verdict=verdict, reason=reason, finished=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                       comfyui_log_excerpt=comfy_log_excerpt(args.comfy_log))
        name = "retry_receipt.json" if args.retry_test else "test_receipt.json"       # the retry run never overwrites the first test's receipt
        (args.workdir / name).write_text(json.dumps(receipt, indent=2, default=str), encoding="utf-8")
        print(f"VERDICT: {verdict} - {reason}\nreceipt: {args.workdir / name}")
        return 0 if verdict == "PASS" else 1

    if enforce_gates:
        problems = execution_gate_problems(args)
        if problems:
            return finish("NOT_RUN", "execution gate: " + "; ".join(problems))
    for path in (args.checkpoint_path, args.text_encoder_path):
        if not path.is_file():
            return finish("NOT_RUN", f"missing file {path} (downloads need the signed approval manifest)")
    project = prepare_project(args, pins)
    receipt["conditioning"] = conditioning_from_workflow(pins)
    if args.start_image:
        from granthstudio.ffmpeg import probe as probe_image
        shown = probe_image(args.start_image)
        negative = args.negative_prompt_file.read_text(encoding="utf-8").strip() if args.negative_prompt_file else None
        positive = args.prompt_file.read_text(encoding="utf-8").strip()
        receipt["start_image"] = {"path": str(args.start_image), "sha256": sha256_file(args.start_image), "width": shown.width, "height": shown.height,
                                  "staged_as": "project visual vis/room.png, uploaded by the existing upload_image step"}
        receipt["text_conditioning"] = {"positive": positive, "positive_sha256": hashlib.sha256(positive.encode("utf-8")).hexdigest(), "negative_recorded": negative,
                                        "negative_applied": False, "negative_note": "the workflow runs CFGGuider at cfg 1, where negative conditioning has no effect; the workflow was deliberately not changed",
                                        "style_prefix_suffix_added": False,
                                        "style": {"style_id": "devotional_gouache_1950s_v1", "applied_via": "identity in task inputs/receipts; the supplied text already carries the style wording"}}
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
    from granthstudio.runtime import gate_gpu_tasks, gpu_status, load_runtime, preflight, ram_available_mb
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
    for t in selected:                    # first test: one attempt per run, no automatic retries and no fallback stand-in
        t.max_attempts, t.fallback = 1, None
    receipt["attempts_allowed_per_task"] = 1
    print("plan:", [(t.stage, t.name) for t in selected])
    report = preflight(project, models, load_runtime(project), gpu_status(), ram_available_mb())
    receipt["preflight"] = report
    receipt["inputs"] = {"checkpoint_sha256": models["ltx"]["checkpoint_sha256"], "text_encoder_sha256": models["ltx"]["runtime"]["files"]["text_encoder"]["sha256"],
                         "comfyui_commit": models["ltx"]["runtime"]["comfyui_commit"], "node_pack_commit": models["ltx"]["runtime"]["node_pack_commit"],
                         "width": args.width, "height": args.height, "frames": 49, "fps": 24, "precision_expected": args.precision}
    if not args.execute:
        return finish("NOT_RUN", f"dry run (no --execute); preflight gpu_ready={report['gpu_ready']}")
    gate_gpu_tasks(selected, report)
    if args.retry_test:
        return _retry_test(args, receipt, finish, scheduler, selected, models)
    began = time.monotonic()
    receipt["exec_started"] = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
    results = scheduler.run(selected)
    receipt["exec_finished"] = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
    receipt["wall_s"] = round(time.monotonic() - began, 1)
    receipt["results"] = [r.__dict__ for r in results]
    task = next(t for t in selected if t.name == SHOT)
    result = next(r for r in results if r.name == SHOT)
    directory = scheduler.task_dir(task)
    journal = scheduler.store / "pending" / f"{task.task_id()}.json"
    receipt["journal"] = json.loads(journal.read_text(encoding="utf-8")) if journal.is_file() else None
    if result.status == "not_validated":
        return finish("NOT_VALIDATED", result.detail)
    if result.status not in ("complete", "resumed"):             # 'resumed' = a verified receipt from an earlier identical run was reused
        oom = oom_markers(args.comfy_log, result.detail)
        receipt["out_of_memory"] = bool(oom)
        if oom:                           # stop cleanly: no retry, no cheaper/costlier variant is tried automatically
            return finish("FAIL", f"CUDA out of memory ({oom[0][:120]!r}); not retried. Decide on a lower-memory plan before another run. {result.status}: {result.detail}")
        return finish("FAIL", f"{result.status}: {result.detail}")
    receipt["reused_earlier_output"] = result.status == "resumed"
    from granthstudio.ffmpeg import probe
    info = probe(directory / "clip.mp4")
    receipt["clip"] = {"sha256": sha256_file(directory / "clip.mp4"), "width": info.width, "height": info.height,
                       "duration_s": info.video_duration_s if info.video_duration_s is not None else info.duration_s}
    receipt["metrics"] = json.loads((directory / "metrics.json").read_text(encoding="utf-8"))
    if receipt["journal"]:
        receipt["comfy_execution"] = _history_execution_window(args.comfy_url, receipt["journal"]["prompt_id"])
    if (info.width, info.height) != (args.width, args.height):
        return finish("FAIL", f"decoded clip is {info.width}x{info.height}, requested {args.width}x{args.height}")
    receipt["visual_diagnostics"] = visual_diagnostics(directory / "clip.mp4", args.workdir / "preview", args.start_image)
    if args.start_image and receipt["visual_diagnostics"]["drift_suspected"] is not False:
        diag = receipt["visual_diagnostics"]
        return finish("FAIL", f"visual drift suspected (or not measurable): SSIM vs frame 0 {diag['ssim_vs_frame_0']}, max luma step {diag['max_luma_step']}; "
                              "see preview/contact_sheet.png; a decoded MP4 is not a visual PASS")
    if receipt["static_verification"]["exit"] is None:
        return finish("NOT_RUN", "clip decoded, but static verification was skipped, so this cannot be a PASS")
    return finish("PASS", "one clip decoded through the existing pipeline; the capability remains unvalidated pending human review")


if __name__ == "__main__":
    sys.exit(main())
