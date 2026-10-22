"""Kaggle runtime infrastructure (frozen section 8): preflight, weights, durable storage, receipts.

Nothing here claims a GPU, model or provider works. Unset requirements are reported as
``not_configured`` and a GPU preflight refuses until every required check passes.
"""
from __future__ import annotations

import importlib.metadata
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .config import Project, load_yaml
from .errors import ConfigError, IntegrationUnavailable, TaskFailed
from .integrity import atomic_write_json, contained_path, read_json, sha256_file
from .schemas import validate_document

GPU_STAGES = ("keyframe", "tier1", "tier2", "lipsync")   # stages whose tasks can submit to a GPU runtime
GPU_CHECKS = ("gpu", "free_vram", "ram", "disk", "session", "python_packages", "storage", "workers", "sources")
DEADLINE_ENV = "GRANTHSTUDIO_SESSION_DEADLINE"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_runtime(project: Project) -> dict[str, Any]:
    data = load_yaml(project.root / "config" / "runtime.yaml")
    validate_document("runtime", data)
    return data


# ---------------------------------------------------------------- measurements

GPU_INDEX_ENV = "GRANTHSTUDIO_GPU_INDEX"


def gpu_status(runner: Callable[[list[str]], str] | None = None) -> list[dict[str, Any]] | None:
    """GPUs from nvidia-smi, or None when nvidia-smi is absent (not measured, not 'no GPU').

    On a multi-GPU host each worker sets GRANTHSTUDIO_GPU_INDEX to the PHYSICAL index it owns (the same index it hides the other cards from with
    CUDA_VISIBLE_DEVICES); preflight and VRAM sampling then look at that card only. An index that does not exist yields an empty list (not ready)."""
    command = ["nvidia-smi", "--query-gpu=index,name,memory.total,memory.used,memory.free",
               "--format=csv,noheader,nounits"]
    try:
        text = runner(command) if runner else subprocess.run(
            command, capture_output=True, text=True, timeout=30, check=True).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    gpus = []
    for line in text.strip().splitlines():
        index, name, total, used, free = (part.strip() for part in line.split(","))
        gpus.append({"index": int(index), "name": name, "memory_total_mb": float(total),
                     "memory_used_mb": float(used), "memory_free_mb": float(free)})
    selected = os.environ.get(GPU_INDEX_ENV)
    if selected is not None:
        try:
            wanted = int(selected)
        except ValueError as exc:
            raise ConfigError(f"{GPU_INDEX_ENV} must be a physical GPU index, not {selected!r}") from exc
        gpus = [g for g in gpus if g["index"] == wanted]
    return gpus


def ram_available_mb(meminfo: Path = Path("/proc/meminfo")) -> float | None:
    try:
        for line in meminfo.read_text().splitlines():
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) / 1024
    except OSError:
        return None
    return None


def session_remaining_s(now: datetime | None = None) -> float | None:
    """Seconds until GRANTHSTUDIO_SESSION_DEADLINE (ISO 8601 with offset); None when unset."""
    value = os.environ.get(DEADLINE_ENV)
    if not value:
        return None
    try:
        deadline = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ConfigError(f"{DEADLINE_ENV} must be ISO 8601 with a UTC offset: {value!r}") from exc
    if deadline.tzinfo is None:
        raise ConfigError(f"{DEADLINE_ENV} needs a UTC offset: {value!r}")
    return (deadline - (now or datetime.now(timezone.utc))).total_seconds()


def stop_before_deadline(runtime: dict[str, Any]) -> Callable[[], bool] | None:
    """Scheduler hook: stop launching tasks once the session is within the configured margin."""
    margin = runtime["resources"]["min_session_remaining_s"]
    if os.environ.get(DEADLINE_ENV) is None or margin is None:
        return None
    return lambda: (session_remaining_s() or 0) < margin


def installed_versions(names: list[str]) -> dict[str, str | None]:
    found = {}
    for name in names:
        try:
            found[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            found[name] = None
    return found


def _check(status: str, measured: Any = None, required: Any = None, detail: str = "") -> dict[str, Any]:
    return {"status": status, "measured": measured, "required": required, "detail": detail}


def _minimum(measured: float | None, required: float | None, what: str) -> dict[str, Any]:
    if required is None:
        return _check("not_configured", measured, None, f"set a minimum {what} from a measured run")
    if measured is None:
        return _check("not_measured", None, required, f"{what} could not be measured on this host")
    return _check("pass" if measured >= required else "fail", measured, required)


def preflight(project: Project, models: dict[str, Any], runtime: dict[str, Any],
              gpus: list[dict[str, Any]] | None = None, ram_mb: float | None = None,
              comfy_stats: dict[str, Any] | None = None) -> dict[str, Any]:
    """Resource and configuration checks before a GPU batch (frozen section 8)."""
    resources = runtime["resources"]
    checks: dict[str, dict[str, Any]] = {}
    expected_gpu = (models["ltx"].get("runtime") or {}).get("gpu", "T4")
    if gpus is None:
        checks["gpu"] = _check("not_measured", None, expected_gpu, "nvidia-smi unavailable")
        checks["free_vram"] = _minimum(None, resources["min_free_vram_mb"], "free VRAM (MB)")
    else:
        first = gpus[0] if gpus else None
        ok = first is not None and expected_gpu in first["name"]
        checks["gpu"] = _check("pass" if ok else "fail", [g["name"] for g in gpus], expected_gpu,
                               "single-GPU default uses GPU 0")
        checks["free_vram"] = _minimum(first["memory_free_mb"] if first else None,
                                       resources["min_free_vram_mb"], "free VRAM (MB)")
    checks["ram"] = _minimum(ram_mb, resources["min_ram_mb"], "available RAM (MB)")
    project.artifacts_dir.mkdir(parents=True, exist_ok=True)
    checks["disk"] = _minimum(shutil.disk_usage(project.artifacts_dir).free / 1e9,
                              resources["min_disk_gb"], "free disk (GB)")
    checks["session"] = _minimum(session_remaining_s(), resources["min_session_remaining_s"],
                                 f"session time remaining (s, from {DEADLINE_ENV})")
    pins = runtime["python_packages"]
    versions = installed_versions(sorted(pins))
    wrong = {name: versions[name] for name, version in pins.items() if versions[name] != version}
    checks["python_packages"] = _check(
        "not_configured" if not pins else ("fail" if wrong else "pass"), versions, pins,
        "no package pins recorded" if not pins else (f"mismatched: {wrong}" if wrong else ""))
    checks["python"] = _check("info", sys.version.split()[0], ">=3.12 (pyproject)")
    try:
        storage = get_storage(runtime)
        checks["storage"] = _check("pass" if storage.writable() else "fail", str(storage.root), None)
    except IntegrationUnavailable as exc:
        checks["storage"] = _check("not_configured", None, None, str(exc))
    try:
        require_single_worker(runtime)
        checks["workers"] = _check("pass", "single", "single")
    except IntegrationUnavailable as exc:
        checks["workers"] = _check("fail", runtime["workers"]["dual_t4"], "disabled", str(exc))
    checks["sources"] = source_consistency(models, runtime)
    if comfy_stats is not None:
        checks["comfyui"] = _check("info", comfy_stats.get("system", {}), None, "from /system_stats")
    ready = all(checks[name]["status"] == "pass" for name in GPU_CHECKS)
    return {"schema_version": 1, "measured_at": _now(), "gpu_ready": ready, "checks": checks}


def require_gpu_ready(report: dict[str, Any]) -> None:
    if not report["gpu_ready"]:
        failing = {k: v["status"] + (f" ({v['detail']})" if k == "sources" and v.get("detail") else "")
                   for k, v in report["checks"].items() if k in GPU_CHECKS and v["status"] != "pass"}
        raise IntegrationUnavailable(f"GPU preflight not passed: {failing}: NOT VALIDATED")


def require_host_ready(project: Project, models: dict[str, Any]) -> dict[str, Any]:
    """Task-boundary readiness: measured VRAM/RAM/disk/session/package/storage checks and source pins, taken now.
    Every GPU-capable task calls this from its own preflight, so no caller (CLI or direct Scheduler.run) skips it."""
    report = preflight(project, models, load_runtime(project), gpu_status(), ram_available_mb())
    require_gpu_ready(report)
    return report


def require_source_pins(project: Project, models: dict[str, Any]) -> None:
    check = source_consistency(models, load_runtime(project))
    if check["status"] != "pass":
        raise IntegrationUnavailable(f"ComfyUI/node source pins {check['status']}: {check['detail'] or 'unrecorded'}: NOT VALIDATED")


def gate_gpu_tasks(tasks, report: dict[str, Any], cpu_only: bool = False, abort: bool = False) -> list[str]:
    """Every executing path calls this on the tasks it is about to run. A task that can invoke GPU generation
    keeps running only if the preflight report passed (source pins included); otherwise its preflight is replaced
    by a refusal (``abort=True``, used by the Kaggle session, raises before any task starts instead), so the scheduler records it as not_validated with zero submissions while CPU tasks still run.
    CPU-only mode refuses GPU tasks the same way. Returns the names of the gated tasks."""
    gated = []
    for task in tasks:
        if task.stage not in GPU_STAGES:
            continue
        try:
            if cpu_only:
                raise IntegrationUnavailable(f"CPU-only mode refuses GPU task {task.name}: run without --cpu-only on a GPU-ready host")
            require_gpu_ready(report)
            continue
        except IntegrationUnavailable as exc:
            if abort:
                raise
            reason = str(exc)
        def refuse(reason=reason):
            raise IntegrationUnavailable(reason)
        task.preflight = refuse
        gated.append(task.name)
    return gated


def source_consistency(models: dict[str, Any], runtime: dict[str, Any]) -> dict[str, Any]:
    pinned = models["ltx"].get("runtime")
    sources = runtime["sources"]
    if pinned is None:
        return _check("not_configured", None, None, "models.yaml ltx.runtime is not recorded yet")
    pairs = {"comfyui_commit": pinned["comfyui_commit"], "node_pack_commit": pinned["node_pack_commit"]}
    wrong = {k: (sources[k], v) for k, v in pairs.items() if sources[k] != v}
    return _check("fail" if wrong else "pass", sources, pairs, f"runtime.yaml/models.yaml differ: {wrong}" if wrong else "")


def require_single_worker(runtime: dict[str, Any]) -> None:
    if runtime["workers"]["dual_t4"] != "disabled":
        raise IntegrationUnavailable(
            "dual-T4 concurrent execution is not implemented; execution is sequential on one GPU "
            "(D-009). Benchmark one GPU first, then approve a concurrency design")


# ---------------------------------------------------------------- weights

def fetch(url: str, dest: Path, sha256: str | None, record: bool = False,
          opener: Callable[[str], Any] | None = None) -> str:
    """Download to a temporary file, verify SHA-256, then atomically rename.

    Without a pin only ``record`` mode downloads; it prints the hash for a human to pin and
    validates nothing.
    """
    if sha256 is None and not record:
        raise ConfigError(f"{dest.name}: no sha256 pin; use record mode to obtain the hash for review")
    if dest.is_file() and sha256 is not None and sha256_file(dest) == sha256:
        return sha256
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(f".{dest.name}.{uuid.uuid4().hex}.part")
    try:
        with (opener or urllib.request.urlopen)(url) as response, tmp.open("wb") as handle:
            shutil.copyfileobj(response, handle, 1 << 20)
        digest = sha256_file(tmp)
        if sha256 is not None and digest != sha256:
            raise TaskFailed(f"{dest.name}: sha256 {digest} != pinned {sha256}; file discarded")
        os.replace(tmp, dest)
        return digest
    except (urllib.error.URLError, OSError) as exc:
        raise IntegrationUnavailable(f"download failed for {dest.name}: {exc}") from exc
    finally:
        tmp.unlink(missing_ok=True)


def verify_downloads(runtime: dict[str, Any], base: Path) -> dict[str, str]:
    status = {}
    for item in runtime["downloads"]:
        path = contained_path(base, item["dest"])
        if item["sha256"] is None:
            status[item["name"]] = "not_pinned"
        elif not path.is_file():
            status[item["name"]] = "missing"
        else:
            status[item["name"]] = "verified" if sha256_file(path) == item["sha256"] else "hash_mismatch"
    return status


# ---------------------------------------------------------------- durable storage

class LocalDirStorage:
    """A mounted directory that outlives the Kaggle session. Each export is a tree plus a
    hash manifest written last, so an interrupted export is never mistaken for a complete one."""

    def __init__(self, root: Path):
        self.root = root

    def writable(self) -> bool:
        try:
            self.root.mkdir(parents=True, exist_ok=True)
            probe = self.root / f".probe-{uuid.uuid4().hex}"
            probe.write_bytes(b"ok")
            probe.unlink()
            return True
        except OSError:
            return False

    def export(self, source: Path, name: str) -> dict[str, Any]:
        target = contained_path(self.root, name)
        previous = self._manifest(target) or {}
        files = {}
        for path in sorted(p for p in source.rglob("*") if p.is_file() and ".work-" not in str(p)):
            relative = path.relative_to(source).as_posix()
            digest = sha256_file(path)
            files[relative] = digest
            copy = target / relative
            if previous.get(relative) != digest or not copy.is_file():
                copy.parent.mkdir(parents=True, exist_ok=True)
                tmp = copy.with_name(f".{copy.name}.{uuid.uuid4().hex}.tmp")
                shutil.copyfile(path, tmp)
                os.replace(tmp, copy)
        manifest = {"schema_version": 1, "exported_at": _now(), "files": files}
        atomic_write_json(target / "export_manifest.json", manifest)
        return manifest

    def restore(self, name: str, dest: Path) -> dict[str, Any]:
        target = contained_path(self.root, name)
        manifest = self._manifest(target)
        if manifest is None:
            raise IntegrationUnavailable(f"no complete export named {name!r} in {self.root}")
        for relative, digest in manifest["files"].items():
            stored = contained_path(target, relative)
            if sha256_file(stored) != digest:
                raise TaskFailed(f"stored artifact {relative} does not match its export hash")
            local = contained_path(dest, relative)
            if not local.is_file() or sha256_file(local) != digest:
                local.parent.mkdir(parents=True, exist_ok=True)
                tmp = local.with_name(f".{local.name}.{uuid.uuid4().hex}.tmp")
                shutil.copyfile(stored, tmp)
                os.replace(tmp, local)
        return manifest

    @staticmethod
    def _manifest(target: Path) -> dict[str, Any] | None:
        path = target / "export_manifest.json"
        return read_json(path) if path.is_file() else None


def get_storage(runtime: dict[str, Any]) -> LocalDirStorage:
    storage = runtime["storage"]
    if storage["provider"] is None:
        raise IntegrationUnavailable("no durable storage provider configured (O-008); set storage in runtime.yaml")
    if storage["provider"] == "local_dir":
        if not storage["path"] or not Path(storage["path"]).is_absolute():
            raise ConfigError("local_dir storage needs an absolute mounted path")
        return LocalDirStorage(Path(storage["path"]))
    raise ConfigError(f"unknown storage provider {storage['provider']!r}")


# ---------------------------------------------------------------- receipts and bootstrap

def git_commit(root: Path) -> str | None:
    try:
        out = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True,
                             text=True, timeout=10, check=True).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
    return out if len(out) == 40 else None


def write_run_receipt(project: Project, kind: str, adhyay: int, started_at: str, results: list,
                      gates: list, input_snapshot: dict, preflight_report: dict | None,
                      store: Path | None = None) -> Path:
    receipt = {"schema_version": 1, "kind": kind, "adhyay": adhyay, "started_at": started_at,
               "finished_at": _now(), "git_commit": git_commit(project.root),
               "input_snapshot": input_snapshot, "preflight": preflight_report,
               "results": [asdict(r) for r in results], "gates": [asdict(g) for g in gates]}
    if store is not None:
        receipt["store"] = str(store)
    validate_document("run_receipt", receipt)
    stamp = receipt["finished_at"].replace(":", "").replace("+", "Z")
    path = project.artifacts_dir / "runs" / f"{stamp}_adhyay_{adhyay:02d}_{kind}_{uuid.uuid4().hex[:6]}.json"
    atomic_write_json(path, receipt)
    return path


def bootstrap_plan(runtime: dict[str, Any], workdir: Path) -> list[list[str]]:
    """Commands that reproduce the GPU host from pins only. Refuses while any pin is missing."""
    sources = runtime["sources"]
    missing = [key for key, value in sources.items() if value is None]
    missing += [f"download {d['name']} sha256" for d in runtime["downloads"] if d["sha256"] is None]
    if not runtime["python_packages"]:
        missing.append("python_packages pins")
    if missing:
        raise ConfigError(f"bootstrap refuses unpinned inputs: {missing}")
    comfy = workdir / "ComfyUI"
    nodes = comfy / "custom_nodes" / Path(sources["node_pack_repo"].rstrip("/")).name.removesuffix(".git")
    commands = [
        ["git", "clone", sources["comfyui_repo"], str(comfy)],
        ["git", "-C", str(comfy), "checkout", "--detach", sources["comfyui_commit"]],
        ["git", "clone", sources["node_pack_repo"], str(nodes)],
        ["git", "-C", str(nodes), "checkout", "--detach", sources["node_pack_commit"]],
        [sys.executable, "-m", "pip", "install", "--no-deps",
         *(f"{name}=={version}" for name, version in sorted(runtime["python_packages"].items()))],
    ]
    for item in runtime["downloads"]:
        commands.append([sys.executable, "-m", "granthstudio", "runtime", "fetch", item["name"]])
    return commands
