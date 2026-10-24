"""P1 driver (D-014): headless Blender proof on this PC. Renders the P1 scene (240 frames, 1920x1080, 24 fps), renders ONE frame twice in two separate Blender
processes and compares them, encodes the MP4 with FFmpeg, and writes receipt.json with times, frame counts and peak memory. Everything is also logged to run.log.

Usage: python p1_run.py --image IMG --out DIR [--frames 240] [--width 1920 --height 1080] [--blender D:/tools/blender/blender.exe]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCENE = HERE / "p1_scene.py"
LOG = None
T0 = time.time()


def log(msg: str) -> None:
    line = f"[{time.time() - T0:7.1f}s] {msg}"
    print(line, flush=True)
    if LOG:
        LOG.write(line + "\n")
        LOG.flush()


class Sampler(threading.Thread):
    """Peak GPU memory (nvidia-smi) and peak RAM of the Blender process tree while a step runs."""

    def __init__(self, pid: int):
        super().__init__(daemon=True)
        self.pid, self.stop, self.vram, self.ram = pid, threading.Event(), 0, 0

    def run(self):
        try:
            import psutil
        except ImportError:
            psutil = None
        while not self.stop.wait(1.0):
            try:
                out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=5).stdout
                self.vram = max(self.vram, int(out.split()[0]))
            except Exception:
                pass
            if psutil:
                try:
                    proc = psutil.Process(self.pid)
                    total = proc.memory_info().rss + sum(c.memory_info().rss for c in proc.children(recursive=True))
                    self.ram = max(self.ram, total // 2**20)
                except Exception:
                    pass


def run(cmd: list[str], tag: str, timeout: int) -> tuple[int, float, dict]:
    log(f"{tag}: START {' '.join(str(c) for c in cmd)[:200]}")
    t = time.time()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    s = Sampler(p.pid)
    s.start()
    deadline = time.time() + timeout
    timer = threading.Timer(timeout, p.kill)
    timer.start()
    for line in p.stdout:
        line = line.rstrip()
        if line and any(k in line for k in ("Saved", "Error", "Traceback", "DONE")):
            log(f"[{tag}] {line[:200]}")
    rc = p.wait()
    timer.cancel()
    s.stop.set()
    wall = time.time() - t
    timed_out = time.time() > deadline
    log(f"{tag}: END exit={rc} wall={wall:.1f}s peak_vram_mib={s.vram} peak_ram_mib={s.ram}{' (TIMED OUT)' if timed_out else ''}")
    return rc, wall, {"peak_vram_mib": s.vram, "peak_ram_mib": s.ram, "timed_out": timed_out}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    global LOG
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--frames", type=int, default=240)
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--blender", default="D:/tools/blender/blender.exe")
    ap.add_argument("--repeat-frame", type=int, default=100)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    LOG = open(out / "run.log", "a", encoding="utf-8")
    receipt: dict = {"note": "P1 technical proof; not a quality approval; human review NOT_DONE", "frames_expected": a.frames, "size": [a.width, a.height], "steps": {}}
    base = [a.blender, "-b", "--python", str(SCENE), "--", "--image", a.image, "--width", str(a.width), "--height", str(a.height), "--frames", str(a.frames)]

    for tag in ("rep1", "rep2"):                                           # same frame, two separate processes
        rc, wall, info = run(base + ["--out", str(out / tag), "--only-frame", str(a.repeat_frame), "--tag", tag], tag, 900)
        receipt["steps"][tag] = {"exit": rc, "wall_s": round(wall, 1), **info}
    f1, f2 = out / "rep1" / f"rep1_{a.repeat_frame:04d}.png", out / "rep2" / f"rep2_{a.repeat_frame:04d}.png"
    if f1.exists() and f2.exists():
        from PIL import Image, ImageChops
        diff = ImageChops.difference(Image.open(f1).convert("RGB"), Image.open(f2).convert("RGB")).getextrema()
        receipt["repeatability"] = {"frame": a.repeat_frame, "sha256_equal": sha(f1) == sha(f2), "max_channel_difference": max(hi for _, hi in diff)}
        log(f"repeatability: {receipt['repeatability']}")
    else:
        receipt["repeatability"] = {"error": "a repeat render is missing"}

    seq = out / "frames"
    rc, wall, info = run(base + ["--out", str(seq)], "sequence", 6 * 3600)
    n = len(list(seq.glob("f_*.png"))) if seq.exists() else 0
    receipt["steps"]["sequence"] = {"exit": rc, "wall_s": round(wall, 1), "frames_written": n, "seconds_per_frame": round(wall / max(n, 1), 2), **info}
    log(f"frames written: {n} of {a.frames}")

    mp4 = out / "p1.mp4"
    rc, wall, info = run(["ffmpeg", "-y", "-framerate", "24", "-i", str(seq / "f_%04d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", str(mp4)], "ffmpeg", 1800)
    receipt["steps"]["ffmpeg"] = {"exit": rc, "wall_s": round(wall, 1)}
    if mp4.exists():
        probe = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames,width,height,r_frame_rate", "-of", "json", str(mp4)],
                               capture_output=True, text=True).stdout
        receipt["mp4"] = {"path": str(mp4), "sha256": sha(mp4), "probe": json.loads(probe)["streams"][0] if probe else None}
        log(f"mp4: {receipt['mp4']['probe']}")
    ok = (n == a.frames and receipt["repeatability"].get("max_channel_difference", 99) <= 1 and mp4.exists()
          and receipt["mp4"]["probe"] and int(receipt["mp4"]["probe"]["nb_read_frames"]) == a.frames)
    receipt["technical_pass"] = bool(ok)
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    log(f"P1 technical pass: {ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
