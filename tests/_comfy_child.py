"""Child process for real two-process journal tests: python _comfy_child.py MODE URL JOURNAL SIGNAL_DIR."""
import os
import pathlib
import sys
import time

from granthstudio import comfy
from granthstudio.errors import JobPending

mode, url, journal, signal = sys.argv[1], sys.argv[2], pathlib.Path(sys.argv[3]), pathlib.Path(sys.argv[4])
GRAPH = {"1": {"class_type": "SyntheticLoader", "inputs": {"ckpt_name": "ltxv-2b-0.9.8-distilled.safetensors"}},
         "2": {"class_type": "SyntheticSave", "inputs": {"images": ["1", 0]}}}
comfy.LOCK_WAIT_S = 1.0 if mode != "hold" else 60.0
original_write, original_submit = comfy.atomic_write_json, comfy.ComfyBackend.submit

if mode == "hold":      # owns the journal and pauses before it writes submission intent
    def slow(path, obj):
        if obj.get("state") == "submitting":
            (signal / "held").write_text("1")
            deadline = time.time() + 60
            while not (signal / "release").exists() and time.time() < deadline:
                time.sleep(0.05)
        original_write(path, obj)
    comfy.atomic_write_json = slow
elif mode == "crash_before_post":
    comfy.ComfyBackend.submit = lambda *a, **k: os._exit(9)
elif mode == "crash_after_post":
    def submit_then_die(*a, **k):
        original_submit(*a, **k)
        os._exit(9)
    comfy.ComfyBackend.submit = submit_then_die

try:
    comfy.ComfyBackend(url, timeout_s=5, poll_s=0.01, max_wait_s=0.3).execute(GRAPH, journal)
    code = 0
except JobPending as exc:
    print(exc)
    code = 5
sys.exit(code)
