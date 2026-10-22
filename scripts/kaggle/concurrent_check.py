"""Judge the CONCURRENT dual-T4 stage from the two workers' own receipts (no GPU needed to run this).

  python concurrent_check.py --receipt0 gpu0/test_receipt.json --receipt1 gpu1/test_receipt.json [--min-overlap-s 20] [--json FILE]

Passes only when, for the two receipts: both verdicts are PASS; they belong to physical GPUs 0 and 1 (one each); they ran different synthetic shots in different
workdirs on different ComfyUI ports; their journals have distinct store namespaces, job tokens and prompt ids and each shows exactly ONE submission (no duplicate);
their outputs are different decoded files; and ComfyUI's own execution timestamps for the two prompts genuinely overlapped (otherwise it was sequential, not concurrent).
Per-card memory evidence is judged separately by gpu_attribution.py.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def window(receipt: dict) -> tuple[float, float]:
    """Seconds, from ComfyUI's own execution_start/execution_success of the submitted prompt (not the scheduler's wider wall-clock window)."""
    e = receipt["comfy_execution"]
    return float(e["start_ms"]) / 1000, float(e["end_ms"]) / 1000


def check(r0: dict, r1: dict, min_overlap_s: float) -> tuple[list[str], dict]:
    problems: list[str] = []
    for name, r in (("worker 0", r0), ("worker 1", r1)):
        if r.get("verdict") != "PASS":
            problems.append(f"{name} verdict is {r.get('verdict')!r}: {r.get('reason')}")
        journal = r.get("journal") or {}
        if journal.get("attempt") != 1 or len(journal.get("history", [])) != 1:
            problems.append(f"{name} shows {journal.get('attempt')} attempt(s) / {len(journal.get('history', []))} submission record(s), expected exactly one")
        if not r.get("clip") or not r["clip"].get("sha256"):
            problems.append(f"{name} has no decoded clip")
    if (r0.get("gpu_index"), r1.get("gpu_index")) != (0, 1):
        problems.append(f"receipts belong to GPUs {r0.get('gpu_index')} and {r1.get('gpu_index')}, expected 0 and 1")
    if r0.get("variant") == r1.get("variant"):
        problems.append("both workers ran the same synthetic variant: not two distinct shots")
    if r0.get("workdir") == r1.get("workdir"):
        problems.append("both workers used the same workdir")
    if r0.get("comfy_url") == r1.get("comfy_url"):
        problems.append("both workers talked to the same ComfyUI server")
    j0, j1 = r0.get("journal") or {}, r1.get("journal") or {}
    for field in ("namespace", "job_token", "prompt_id"):
        if not j0.get(field) or j0.get(field) == j1.get(field):
            problems.append(f"journals share or lack {field}: {j0.get(field)!r} / {j1.get(field)!r}")
    if (r0.get("clip") or {}).get("sha256") == (r1.get("clip") or {}).get("sha256"):
        problems.append("both outputs are byte-identical: not two distinct generations")
    overlap = 0.0
    try:
        (s0, e0), (s1, e1) = window(r0), window(r1)
        overlap = min(e0, e1) - max(s0, s1)
    except (KeyError, TypeError, ValueError):
        problems.append("ComfyUI execution timestamps are missing from a receipt: concurrency cannot be shown")
    else:
        if overlap < min_overlap_s:
            problems.append(f"execution windows overlap {overlap:.1f}s (< {min_overlap_s}s): sequential, not concurrent")
    return problems, {"overlap_s": round(overlap, 1), "wall_s": [r0.get("wall_s"), r1.get("wall_s")],
                      "peak_vram_mb": [((r.get("metrics") or {}).get("peak_vram_mb") or {}).get("value") for r in (r0, r1)]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--receipt0", required=True, type=Path)
    parser.add_argument("--receipt1", required=True, type=Path)
    parser.add_argument("--min-overlap-s", type=float, default=20)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args(argv)
    r0, r1 = (json.loads(p.read_text(encoding="utf-8")) for p in (args.receipt0, args.receipt1))
    problems, facts = check(r0, r1, args.min_overlap_s)
    report = {"ok": not problems, "problems": problems, **facts}
    if args.json:
        args.json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
