"""Kaggle TPU VM probe (a SCRIPT kernel on the proven TPU image): what does this TPU session provide, and can PyTorch/XLA run on it?

Why a script and not a notebook: notebooks pushed with the TPU setting were converted to HTML without executing a single cell ("Successfully ran in 10 s",
0 B output), while the owner's earlier TPU work ran as script kernels on the python-tpuvm image. Everything is written to /kaggle/working/probe/probe.log as
well as stdout, flushed after every line, and a summary JSON is written at the end whatever happens, so a run can never again finish silently.
"""
import json
import os
import queue
import signal
import subprocess
import sys
import threading
import time
import traceback

OUT = "/kaggle/working/probe"
os.makedirs(OUT, exist_ok=True)
T0 = time.time()
LOG = open(f"{OUT}/probe.log", "a", encoding="utf-8")
SUMMARY = {"steps": {}}


def log(msg):
    line = f"[{time.time() - T0:7.1f}s] {msg}"
    print(line, flush=True)
    LOG.write(line + "\n")
    LOG.flush()


def persist():
    with open(f"{OUT}/summary.json", "w", encoding="utf-8") as f:
        json.dump(SUMMARY, f, indent=2)


def sh(cmd, tag, timeout=900):
    """Run a shell command in its own process group; stream its output into the log; the deadline is checked on EVERY loop pass (a chatty or a silent child both time out);
    on timeout the whole group is killed and reaped. Returns (exit code, last lines). A launch failure is recorded as an infrastructure failure, not as a diagnosis."""
    log(f"{tag}: START {cmd}")
    tail, lines, rc, timed_out, p = [], queue.Queue(), None, False, None
    try:
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1,
                             env={**os.environ, "PYTHONUNBUFFERED": "1"}, start_new_session=True)

        def pump():
            for line in p.stdout:
                lines.put(line.rstrip()[:300])
            lines.put(None)
        threading.Thread(target=pump, daemon=True).start()
        deadline, eof = time.time() + timeout, False
        while not eof:
            if time.time() > deadline:
                timed_out = True
                log(f"{tag}: TIMEOUT after {timeout}s, killing the process group")
                break
            try:
                line = lines.get(timeout=2)
            except queue.Empty:
                continue
            if line is None:
                eof = True
            else:
                log(f"[{tag}] {line}")
                tail = (tail + [line])[-15:]
        if eof:                                                      # output closed: the child may still be finishing, so wait for it under the same deadline
            try:
                rc = p.wait(timeout=max(1.0, deadline - time.time()))
            except subprocess.TimeoutExpired:
                timed_out = True
                log(f"{tag}: TIMEOUT after {timeout}s (output closed but the process kept running)")
    except Exception as exc:
        tail = [f"{type(exc).__name__}: {exc}"]
        SUMMARY["infrastructure_failures"] = SUMMARY.get("infrastructure_failures", []) + [tag]
    finally:
        if p is not None:
            try:
                os.killpg(p.pid, signal.SIGKILL)                   # nothing of this step may keep the TPU or the pipe
            except Exception:
                pass
            try:
                rc = p.wait(timeout=30) if rc is None else rc        # reap
            except Exception:
                rc = None
    if timed_out:
        rc = -9
        SUMMARY["timeouts"] = SUMMARY.get("timeouts", []) + [tag]
    log(f"{tag}: END exit={rc}{' (TIMED OUT)' if timed_out else ''}")
    SUMMARY["steps"][tag] = {"exit": rc, "timed_out": timed_out, "tail": tail}
    persist()
    return rc, tail


def main():
    log("TPU PROBE START")
    sh("uname -a; python --version; nproc; free -g; df -h /kaggle/working /tmp /dev/shm", "system")
    sh("env | grep -i -E 'tpu|xla|pjrt|libtpu' | cut -c1-200", "tpu-env")
    sh("pip list 2>/dev/null | grep -i -E '^(torch|torch-xla|torch_xla|jax|jaxlib|libtpu|diffusers|transformers|accelerate|flax|vllm|tpu)'", "packages")
    jax_check = ("import jax; d = jax.devices(); print('JAX', jax.__version__, len(d), d[0].platform, getattr(d[0], 'device_kind', ''));"
                 " print([str(x) for x in d]); print('memory_stats', d[0].memory_stats())")
    sh(f"env -u TPU_LIBRARY_PATH python -c \"{jax_check}\"", "jax")
    xla_check = ("import torch, torch_xla, torch_xla.core.xla_model as xm; d = xm.xla_device();"
                 " a = torch.randn(2048, 2048, dtype=torch.bfloat16, device=d); b = (a @ a).sum(); xm.mark_step();"
                 " print('TORCH', torch.__version__, 'TORCH_XLA', torch_xla.__version__, 'device', d, 'HW', xm.xla_device_hw(d), 'sum', float(b))")
    rc, tail = sh(f"env -u TPU_LIBRARY_PATH python -c \"{xla_check}\"", "torch_xla-in-base-env")
    on_tpu = rc == 0 and any("HW TPU" in line for line in tail)
    SUMMARY["torch_xla_in_base_env_on_tpu"] = on_tpu
    if not on_tpu:
        log("torch_xla is not usable in the base environment: trying a separate virtual environment (the base packages stay untouched)")
        sh("python -m venv /tmp/xl", "venv")
        sh("/tmp/xl/bin/pip install -q torch 'torch_xla[tpu]' -f https://storage.googleapis.com/libtpu-releases/index.html", "pip-torch_xla", timeout=1500)
        rc2, tail2 = sh(f"env -u TPU_LIBRARY_PATH /tmp/xl/bin/python -c \"{xla_check}\"", "torch_xla-in-venv")
        SUMMARY["torch_xla_in_venv_on_tpu"] = rc2 == 0 and any("HW TPU" in line for line in tail2)
        sh("/tmp/xl/bin/pip list 2>/dev/null | grep -i -E '^(torch|torch-xla|torch_xla|libtpu|jax)'", "venv-packages")
    log("TPU PROBE END")


if __name__ == "__main__":
    code = 0
    try:
        main()
        if SUMMARY.get("infrastructure_failures"):
            code = 1
    except Exception:
        SUMMARY["fatal"] = traceback.format_exc()[-1500:]
        log("FATAL " + SUMMARY["fatal"])
        code = 1
    finally:
        SUMMARY["finished"] = True
        persist()
        log(f"summary.json written (exit code {code})")
    sys.exit(code)
