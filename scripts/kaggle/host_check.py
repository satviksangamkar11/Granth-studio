"""Dual-T4 host check for the LTX tests (Kaggle accelerator "GPU T4 x2"). Exits 0 only when the host is exactly what the plan assumes.

  python host_check.py [--min-ram-mb N] [--min-disk-gb N] [--path DIR] [--json FILE] [--max-idle-mb N]

Checks (each failure is listed; any failure -> exit 1):
  * exactly two NVIDIA GPUs, physical indices {0, 1}, both named "Tesla T4", distinct UUIDs, >= 14 000 MiB total each;
  * both idle (memory.used <= --max-idle-mb) so a measurement cannot be polluted by a foreign process;
  * PyTorch really sees two CUDA devices of compute capability 7.5 whose names match (a different driver/CUDA stack is a refusal);
  * system RAM and free disk.
It never assumes two T4s behave as one 32 GB device: each worker later owns exactly one card.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

TORCH_PROBE = ("import json,torch;print(json.dumps({'torch':torch.__version__,'cuda':torch.version.cuda,'available':torch.cuda.is_available(),"
               "'count':torch.cuda.device_count(),'devices':[{'name':torch.cuda.get_device_name(i),'capability':list(torch.cuda.get_device_capability(i))}"
               " for i in range(torch.cuda.device_count())]}))")
QUERY = ["nvidia-smi", "--query-gpu=index,uuid,name,memory.total,memory.used", "--format=csv,noheader,nounits"]


def parse_nvidia_smi(text: str) -> list[dict[str, Any]]:
    gpus = []
    for line in text.strip().splitlines():
        index, uuid, name, total, used = (part.strip() for part in line.split(","))
        gpus.append({"index": int(index), "uuid": uuid, "name": name, "memory_total_mb": float(total), "memory_used_mb": float(used)})
    return gpus


def evaluate_host(gpus: list[dict[str, Any]] | None, torch_info: dict[str, Any] | None, ram_mb: float | None, disk_gb: float | None,
                  min_ram_mb: float, min_disk_gb: float, max_idle_mb: float, min_total_mb: float = 14000.0) -> list[str]:
    problems: list[str] = []
    if gpus is None:
        return ["nvidia-smi is unavailable: cannot identify the GPUs"]
    if len(gpus) != 2:
        problems.append(f"expected exactly two GPUs, nvidia-smi lists {len(gpus)}")
    if sorted(g["index"] for g in gpus) != [0, 1]:
        problems.append(f"expected physical indices [0, 1], got {sorted(g['index'] for g in gpus)}")
    if len({g["uuid"] for g in gpus}) != len(gpus):
        problems.append("GPU UUIDs are not distinct")
    for g in gpus:
        if "Tesla T4" not in g["name"]:
            problems.append(f"GPU {g['index']} is {g['name']!r}, not a Tesla T4")
        if g["memory_total_mb"] < min_total_mb:
            problems.append(f"GPU {g['index']} reports {g['memory_total_mb']:.0f} MiB total, below {min_total_mb:.0f}")
        if g["memory_used_mb"] > max_idle_mb:
            problems.append(f"GPU {g['index']} is not idle: {g['memory_used_mb']:.0f} MiB already in use (limit {max_idle_mb:.0f})")
    if torch_info is None:
        problems.append("PyTorch could not be probed (not importable or CUDA stack broken)")
    else:
        if not torch_info.get("available") or torch_info.get("count") != 2:
            problems.append(f"PyTorch sees {torch_info.get('count')} CUDA device(s) (available={torch_info.get('available')}), expected 2")
        for i, device in enumerate(torch_info.get("devices", [])):
            if device.get("capability") != [7, 5]:
                problems.append(f"torch device {i} has compute capability {device.get('capability')}, expected [7, 5]")
            if "T4" not in device.get("name", ""):
                problems.append(f"torch device {i} is {device.get('name')!r}, not a T4")
        if not torch_info.get("cuda"):
            problems.append("this PyTorch build has no CUDA runtime")
    if ram_mb is None or ram_mb < min_ram_mb:
        problems.append(f"available RAM {ram_mb} MiB is below {min_ram_mb:.0f}")
    if disk_gb is None or disk_gb < min_disk_gb:
        problems.append(f"free disk {disk_gb} GB is below {min_disk_gb:.0f}")
    return problems


def collect(path: Path) -> tuple[list[dict[str, Any]] | None, dict[str, Any] | None, float | None, float | None]:
    try:
        gpus = parse_nvidia_smi(subprocess.run(QUERY, capture_output=True, text=True, timeout=30, check=True).stdout)
    except (OSError, subprocess.SubprocessError, ValueError):
        gpus = None
    try:
        torch_info = json.loads(subprocess.run([sys.executable, "-c", TORCH_PROBE], capture_output=True, text=True, timeout=180, check=True).stdout)
    except (OSError, subprocess.SubprocessError, ValueError):
        torch_info = None
    ram = None
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemAvailable:"):
                ram = int(line.split()[1]) / 1024
    except OSError:
        pass
    path.mkdir(parents=True, exist_ok=True)
    return gpus, torch_info, ram, shutil.disk_usage(path).free / 1e9


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--min-ram-mb", type=float, default=24000)
    parser.add_argument("--min-disk-gb", type=float, default=40)
    parser.add_argument("--max-idle-mb", type=float, default=800)
    parser.add_argument("--path", type=Path, default=Path("."))
    parser.add_argument("--json", type=Path)
    args = parser.parse_args(argv)
    gpus, torch_info, ram, disk = collect(args.path)
    problems = evaluate_host(gpus, torch_info, ram, disk, args.min_ram_mb, args.min_disk_gb, args.max_idle_mb)
    report = {"gpus": gpus, "torch": torch_info, "ram_available_mb": ram, "disk_free_gb": disk, "problems": problems, "ok": not problems}
    if args.json:
        args.json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
