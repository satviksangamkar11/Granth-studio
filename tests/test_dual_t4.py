"""Dual-T4 helpers: host check, per-card attribution and the concurrent verdict, all on synthetic data (no GPU involved)."""
from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timedelta, timezone

import pytest

from tests.conftest import REPO


def load(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / "kaggle" / f"{name}.py")
    module = importlib.util.module_from_spec(spec); sys.modules[name] = module; spec.loader.exec_module(module)
    return module


hc, ga, cc = load("host_check"), load("gpu_attribution"), load("concurrent_check")
NL = chr(10)
SMI = "0, GPU-aaaa, Tesla T4, 15360, 3" + NL + "1, GPU-bbbb, Tesla T4, 15360, 3" + NL
TORCH = {"torch": "2.x", "cuda": "12.x", "available": True, "count": 2, "devices": [{"name": "Tesla T4", "capability": [7, 5]}] * 2}


def host(**changes):
    args = dict(gpus=hc.parse_nvidia_smi(SMI), torch_info=dict(TORCH), ram_mb=29000, disk_gb=100, min_ram_mb=24000, min_disk_gb=40, max_idle_mb=800)
    args.update(changes)
    return hc.evaluate_host(**args)


def smi(*rows):
    return hc.parse_nvidia_smi(NL.join(rows) + NL)


def test_good_dual_t4_host_has_no_problems():
    assert host() == []


@pytest.mark.parametrize("name,changes,fragment", [
    ("one gpu", dict(gpus=smi("0, GPU-aaaa, Tesla T4, 15360, 3")), "exactly two GPUs"),
    ("three gpus", dict(gpus=smi("0, GPU-aaaa, Tesla T4, 15360, 3", "1, GPU-bbbb, Tesla T4, 15360, 3", "2, GPU-cccc, Tesla T4, 15360, 3")), "exactly two GPUs"),
    ("indices", dict(gpus=smi("0, GPU-aaaa, Tesla T4, 15360, 3", "2, GPU-bbbb, Tesla T4, 15360, 3")), "physical indices"),
    ("same uuid", dict(gpus=smi("0, GPU-aaaa, Tesla T4, 15360, 3", "1, GPU-aaaa, Tesla T4, 15360, 3")), "UUIDs are not distinct"),
    ("a100", dict(gpus=smi("0, GPU-aaaa, Tesla T4, 15360, 3", "1, GPU-bbbb, NVIDIA A100, 40960, 3")), "not a Tesla T4"),
    ("small vram", dict(gpus=smi("0, GPU-aaaa, Tesla T4, 8192, 3", "1, GPU-bbbb, Tesla T4, 15360, 3")), "below 14000"),
    ("busy", dict(gpus=smi("0, GPU-aaaa, Tesla T4, 15360, 5000", "1, GPU-bbbb, Tesla T4, 15360, 3")), "not idle"),
    ("no smi", dict(gpus=None), "nvidia-smi is unavailable"),
    ("no torch", dict(torch_info=None), "PyTorch could not be probed"),
    ("torch sees one", dict(torch_info={**TORCH, "count": 1}), "sees 1 CUDA device"),
    ("wrong capability", dict(torch_info={**TORCH, "devices": [{"name": "Tesla T4", "capability": [8, 0]}] * 2}), "compute capability"),
    ("no cuda build", dict(torch_info={**TORCH, "cuda": None}), "no CUDA runtime"),
    ("low ram", dict(ram_mb=8000), "available RAM"),
    ("no ram info", dict(ram_mb=None), "available RAM"),
    ("low disk", dict(disk_gb=10), "free disk"),
])
def test_host_check_refuses_everything_that_is_not_the_planned_dual_t4_host(name, changes, fragment):
    assert any(fragment in p for p in host(**changes)), (name, host(**changes))


def attribute(tmp_path, a1, b1, apps, workers):
    vram = tmp_path / "v.csv"
    vram.write_text(NL.join(["t,0,GPU-aaaa,3", "t,1,GPU-bbbb,3", f"t,0,GPU-aaaa,{a1}", f"t,1,GPU-bbbb,{b1}"]), encoding="utf-8")
    trace = tmp_path / "a.csv"; trace.write_text(apps, encoding="utf-8")
    notes = []
    return ga.attribute(ga.read_vram(vram), ga.read_apps(trace), workers, 300, 1000, notes), notes


def test_gpu0_worker_with_gpu1_idle_passes(tmp_path):
    problems, _ = attribute(tmp_path, 9000, 5, "GPU-aaaa, 111, 9000" + NL, {0: (111, True), 1: (0, False)})
    assert problems == []


def test_gpu1_touched_during_a_gpu0_only_stage_is_caught(tmp_path):
    problems, _ = attribute(tmp_path, 9000, 4000, "GPU-aaaa, 111, 9000" + NL + "GPU-bbbb, 222, 4000" + NL, {0: (111, True), 1: (0, False)})
    assert any("meant to stay idle" in p for p in problems)


def test_worker_pid_on_the_wrong_card_or_on_both_is_caught(tmp_path):
    problems, _ = attribute(tmp_path, 9000, 5, "GPU-bbbb, 111, 9000" + NL, {0: (111, True), 1: (0, False)})
    assert any("never appears as a compute app on GPU 0" in p for p in problems)
    apps = NL.join(["GPU-aaaa, 111, 9000", "GPU-bbbb, 111, 9000", "GPU-bbbb, 222, 9000"]) + NL
    problems, _ = attribute(tmp_path, 9000, 9000, apps, {0: (111, True), 1: (222, True)})
    assert any("also appears on another card" in p for p in problems)


def test_a_card_that_never_filled_did_not_do_the_work(tmp_path):
    problems, _ = attribute(tmp_path, 400, 5, "GPU-aaaa, 111, 400" + NL, {0: (111, True), 1: (0, False)})
    assert any("no evidence it did the work" in p for p in problems)


def test_without_visible_process_ids_only_memory_evidence_counts_and_says_so(tmp_path):
    problems, notes = attribute(tmp_path, 9000, 5, "", {0: (111, True), 1: (0, False)})
    assert problems == [] and any("no compute apps" in n for n in notes)
    problems, _ = attribute(tmp_path, 9000, 5000, "", {0: (111, True), 1: (0, False)})
    assert problems                                                                  # memory on the idle card still betrays it


def receipt(index, variant, start, seconds, **over):
    t0 = datetime(2026, 10, 24, 12, 0, 0, tzinfo=timezone.utc) + timedelta(seconds=start)
    base = {"verdict": "PASS", "gpu_index": index, "variant": variant, "workdir": f"/w/gpu{index}", "comfy_url": f"http://127.0.0.1:{9000 + index}",
            "exec_started": t0.isoformat(), "exec_finished": (t0 + timedelta(seconds=seconds)).isoformat(), "wall_s": seconds,
            "journal": {"attempt": 1, "history": [{}], "namespace": f"ns{index}", "job_token": f"tok{index}", "prompt_id": f"p{index}"},
            "clip": {"sha256": f"{index}" * 64}, "metrics": {"peak_vram_mb": {"value": 9000 + index}}, "reason": "ok"}
    base.update(over)
    return base


def test_concurrent_stage_passes_only_for_two_distinct_overlapping_passing_workers():
    problems, facts = cc.check(receipt(0, "a", 0, 300), receipt(1, "b", 20, 300), 20)
    assert problems == [] and facts["overlap_s"] == 280 and facts["peak_vram_mb"] == [9000, 9001]


@pytest.mark.parametrize("name,r0,r1,fragment", [
    ("sequential", receipt(0, "a", 0, 100), receipt(1, "b", 200, 100), "sequential, not concurrent"),
    ("a failed worker", receipt(0, "a", 0, 300, verdict="FAIL", reason="boom"), receipt(1, "b", 0, 300), "verdict is 'FAIL'"),
    ("same gpu", receipt(0, "a", 0, 300), receipt(0, "b", 0, 300), "expected 0 and 1"),
    ("same variant", receipt(0, "a", 0, 300), receipt(1, "a", 0, 300), "same synthetic variant"),
    ("same workdir", receipt(0, "a", 0, 300), receipt(1, "b", 0, 300, workdir="/w/gpu0"), "same workdir"),
    ("same server", receipt(0, "a", 0, 300), receipt(1, "b", 0, 300, comfy_url="http://127.0.0.1:9000"), "same ComfyUI server"),
    ("shared namespace", receipt(0, "a", 0, 300), receipt(1, "b", 0, 300, journal={"attempt": 1, "history": [{}], "namespace": "ns0", "job_token": "t", "prompt_id": "q"}),
     "share or lack namespace"),
    ("duplicate submission", receipt(0, "a", 0, 300, journal={"attempt": 2, "history": [{}, {}], "namespace": "n", "job_token": "t", "prompt_id": "p"}),
     receipt(1, "b", 0, 300), "expected exactly one"),
    ("identical outputs", receipt(0, "a", 0, 300), receipt(1, "b", 0, 300, clip={"sha256": "0" * 64}), "byte-identical"),
    ("no clip", receipt(0, "a", 0, 300, clip=None), receipt(1, "b", 0, 300), "no decoded clip"),
    ("no windows", {k: v for k, v in receipt(0, "a", 0, 300).items() if k != "exec_started"}, receipt(1, "b", 0, 300), "windows are missing"),
])
def test_concurrent_stage_refuses_every_gap(name, r0, r1, fragment):
    problems, _ = cc.check(r0, r1, 20)
    assert any(fragment in p for p in problems), (name, problems)
