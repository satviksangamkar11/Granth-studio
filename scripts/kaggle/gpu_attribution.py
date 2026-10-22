"""Prove which physical GPU each ComfyUI worker really used, and that the other card stayed untouched, from nvidia-smi traces.

Inputs (written by scripts/kaggle/ltx_first_test.sh while the workers run):
  --vram-trace      CSV from `nvidia-smi --query-gpu=timestamp,index,uuid,memory.used --format=csv,noheader,nounits -l 2`
  --apps-trace      CSV from `nvidia-smi --query-compute-apps=timestamp?,gpu_uuid,pid,used_memory --format=csv,noheader,nounits` samples,
                    one block per sample, lines: gpu_uuid, pid, used_memory
  --worker INDEX=PID[:active]   a worker (physical GPU index and ComfyUI pid); `:idle` marks a card that must stay idle
Verdicts (all must hold, otherwise exit 1):
  * each active worker's pid appears under ITS card's uuid in the compute-apps trace and under no other card's uuid;
  * a card declared idle has no compute app at all and peak memory.used within --idle-slack-mb of its first sample;
  * each active card's peak memory.used rose above its first sample by at least --min-rise-mb (it really did the work).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


def read_vram(path: Path) -> dict[str, dict]:
    cards: dict[str, dict] = {}
    for row in csv.reader(path.read_text(encoding="utf-8").splitlines()):
        if len(row) < 4 or not row[3].strip().replace(".", "").isdigit():
            continue
        _, index, uuid, used = (c.strip() for c in row[:4])
        card = cards.setdefault(uuid, {"index": int(index), "first": float(used), "peak": float(used)})
        card["peak"] = max(card["peak"], float(used))
    return cards


def read_apps(path: Path) -> dict[str, set[int]]:
    seen: dict[str, set[int]] = {}
    for row in csv.reader(path.read_text(encoding="utf-8").splitlines()):
        if len(row) >= 2 and row[1].strip().isdigit():
            seen.setdefault(row[0].strip(), set()).add(int(row[1]))
    return seen


def attribute(cards: dict[str, dict], apps: dict[str, set[int]], workers: dict[int, tuple[int, bool]], idle_slack_mb: float, min_rise_mb: float,
              notes: list[str] | None = None) -> list[str]:
    problems = []
    pids_visible = any(apps.values())      # inside a container nvidia-smi may list no processes (or host pids): then only memory evidence is available
    if not pids_visible and notes is not None:
        notes.append("nvidia-smi listed no compute apps: attribution rests on per-card memory rise, CUDA_VISIBLE_DEVICES and ComfyUI's own device report")
    uuid_of = {c["index"]: u for u, c in cards.items()}
    for index, (pid, active) in sorted(workers.items()):
        uuid = uuid_of.get(index)
        if uuid is None:
            problems.append(f"GPU {index} is absent from the VRAM trace")
            continue
        card = cards[uuid]
        if active:
            if pids_visible and pid not in apps.get(uuid, set()):
                problems.append(f"worker pid {pid} never appears as a compute app on GPU {index} ({uuid})")
            for other_uuid, pids in apps.items():
                if other_uuid != uuid and pid in pids:
                    problems.append(f"worker pid {pid} (GPU {index}) also appears on another card {other_uuid}")
            if card["peak"] - card["first"] < min_rise_mb:
                problems.append(f"GPU {index} memory.used rose only {card['peak'] - card['first']:.0f} MiB: no evidence it did the work")
        else:
            if apps.get(uuid):
                problems.append(f"GPU {index} was meant to stay idle but has compute apps {sorted(apps[uuid])}")
            if card["peak"] - card["first"] > idle_slack_mb:
                problems.append(f"GPU {index} was meant to stay idle but memory.used rose {card['peak'] - card['first']:.0f} MiB")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--vram-trace", required=True, type=Path)
    parser.add_argument("--apps-trace", required=True, type=Path)
    parser.add_argument("--worker", action="append", required=True, metavar="INDEX=PID[:idle]")
    parser.add_argument("--idle-slack-mb", type=float, default=300)
    parser.add_argument("--min-rise-mb", type=float, default=1000)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args(argv)
    workers = {}
    for item in args.worker:
        left, _, flag = item.partition(":")
        index, pid = left.split("=")
        workers[int(index)] = (int(pid or 0), flag != "idle")
    cards, apps = read_vram(args.vram_trace), read_apps(args.apps_trace)
    notes: list[str] = []
    problems = attribute(cards, apps, workers, args.idle_slack_mb, args.min_rise_mb, notes)
    report = {"notes": notes, "cards": cards, "compute_apps": {k: sorted(v) for k, v in apps.items()}, "workers": {str(k): {"pid": v[0], "active": v[1]} for k, v in workers.items()},
              "problems": problems, "ok": not problems}
    if args.json:
        args.json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
