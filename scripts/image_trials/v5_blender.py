"""Guarded runner for Kimi-written Blender scene scripts (D-015 Phase 1). Blender Python can touch the whole machine, so:
1. `check()` parses the script with `ast` and refuses anything outside a small allowlist: imports only bpy/math/mathutils/random; no file, process,
   network, exec/eval, dunder, driver, handler, addon, preference or save access; no path-like string literals. Assets are reached only through the
   runner-provided `ASSET("name")`, which maps whitelisted names to files.
2. `build()` runs Blender headless (--factory-startup, --disable-autoexec) with a sanitised environment (no API keys), a hard timeout and process-tree kill;
   the runner (not Kimi) fixes resolution/fps/frame range and saves the .blend.
3. `render()` renders in chunks of <= 48 frames with fixed command-line output paths, checks the frame count, encodes each chunk with ffmpeg and joins them.
Usage (by v5_shots.py): check(code) -> list of problems; build(code, assets, out_dir); render(out_dir) -> mp4 path."""
from __future__ import annotations

import ast
import json
import os
import subprocess
from pathlib import Path

BLENDER = "D:/tools/blender/blender.exe"
ALLOWED_IMPORTS = {"bpy", "math", "mathutils", "random"}
BANNED_CALLS = {"open", "exec", "eval", "compile", "__import__", "getattr", "setattr", "delattr", "globals", "locals", "vars", "input", "breakpoint", "help", "print_function"}
BANNED_ATTRS = {"wm", "script", "utils", "handlers", "preferences", "extensions", "addon", "addons", "save_as", "save", "save_mainfile", "save_as_mainfile",
                "filepath_raw", "driver_namespace", "driver_add", "drivers", "expression", "url_open", "file_slots", "base_path", "texts", "libraries",
                "library", "app", "path", "ops_module", "context_override", "path_resolve", "save_render", "pack", "unpack", "reload",
                "as_module", "register_class", "unregister_class", "sound", "movie", "external", "url"}   # os/subprocess-style names are unreachable: only bpy/math/mathutils/random import
FPS, FRAMES, RES = 24, 144, (1280, 720)
CHUNK = 48


def check(code: str) -> list[str]:
    problems = []
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return [f"syntax error line {exc.lineno}: {exc.msg}"]
    doc_strings = {id(n.value) for n in ast.walk(tree) if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str)}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split(".")[0] not in ALLOWED_IMPORTS:
                    problems.append(f"import {a.name} not allowed")
        elif isinstance(node, ast.ImportFrom):
            problems.append(f"from {node.module} import not allowed (use plain import)")
        elif isinstance(node, ast.Name) and (node.id in BANNED_CALLS or node.id.startswith("_")):
            problems.append(f"name {node.id} not allowed")
        elif isinstance(node, ast.Attribute):
            if node.attr in BANNED_ATTRS or node.attr.startswith("_") or (node.attr == "render" and isinstance(node.value, ast.Attribute) and node.value.attr == "ops"):
                problems.append(f"attribute .{node.attr} not allowed")
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in doc_strings:   # bare docstrings cannot be used as paths
            v = node.value
            if any(t in v for t in (":/", ":\\", "\\", "..", "/")) or v.startswith(("~", ".")) or v in ("ShaderNodeScript", "CompositorNodeOutputFile"):
                problems.append(f"path-like string {v[:30]!r} not allowed")
        elif isinstance(node, (ast.Global, ast.Nonlocal, ast.AsyncFunctionDef, ast.Await)):
            problems.append(f"{type(node).__name__} not allowed")
    return sorted(set(problems))


def clean_env() -> dict:
    keep = {"path", "systemroot", "temp", "tmp", "userprofile", "localappdata", "appdata", "programfiles", "windir", "comspec", "pathext"}
    return {k: v for k, v in os.environ.items() if k.lower() in keep}


def run(cmd: list, cwd: Path, timeout: float) -> tuple[int, str]:
    p = subprocess.Popen(cmd, cwd=cwd, env=clean_env(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace")
    try:
        out, _ = p.communicate(timeout=max(5, timeout))
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True, timeout=30)
        p.kill()
        try:
            p.communicate(timeout=15)
        except subprocess.TimeoutExpired:
            pass
        return 124, "timeout"
    return p.returncode, (out or "")[-4000:]


def build(code: str, assets: dict, out_dir: Path, timeout: float = 600, shot: dict | None = None) -> tuple[bool, str]:
    """Runs the checked scene script; the runner prepends ASSET() and appends the fixed render settings and the save."""
    problems = check(code)
    if problems:
        return False, "refused by guard: " + "; ".join(problems)
    out_dir.mkdir(parents=True, exist_ok=True)
    amap = {k: str(Path(v).resolve()).replace("\\", "/") for k, v in assets.items()}
    blend = str((out_dir / "scene.blend").resolve()).replace("\\", "/")
    prelude = f"_ASSETS = {json.dumps(amap)}\ndef ASSET(name):\n    return _ASSETS[name]\n"
    if shot is not None:                                  # shot data for the approved builder, embedded as a Python literal (no file reading)
        prelude += f"SHOT = {shot!r}\n"
    epilogue = (f"\nimport bpy as _b\n_s = _b.context.scene\n_s.render.resolution_x, _s.render.resolution_y, _s.render.resolution_percentage = {RES[0]}, {RES[1]}, 100\n"
                f"_s.render.fps = {FPS}\n_s.frame_start, _s.frame_end = 1, {FRAMES}\n_b.ops.wm.save_as_mainfile(filepath={json.dumps(blend)})\n")
    script = out_dir / "build_scene.py"
    script.write_text(prelude + "\n# ---- Kimi code (guard-checked) ----\n" + code + "\n# ---- runner ----" + epilogue, encoding="utf-8")
    rc, log = run([BLENDER, "-b", "--factory-startup", "--disable-autoexec", "--python-exit-code", "3", "--python", str(script)], out_dir, timeout)
    (out_dir / "build_log.txt").write_text(log, encoding="utf-8")
    return rc == 0 and Path(blend).exists(), log[-1500:]


def render(out_dir: Path, timeout_per_chunk: float = 300) -> tuple[Path | None, str]:
    frames = out_dir / "frames"
    frames.mkdir(exist_ok=True)
    for old in frames.glob("*.png"):
        old.unlink()
    parts = []
    for a in range(1, FRAMES + 1, CHUNK):
        b = min(FRAMES, a + CHUNK - 1)
        rc, log = run([BLENDER, "-b", str(out_dir / "scene.blend"), "--disable-autoexec", "-o", str(frames / "f_####"), "-F", "PNG",
                       "-s", str(a), "-e", str(b), "-a"], out_dir, timeout_per_chunk)
        got = sorted(frames.glob("f_*.png"))
        want = [frames / f"f_{i:04d}.png" for i in range(a, b + 1)]
        if rc != 0 or not all(w.exists() for w in want):
            return None, f"render chunk {a}-{b} failed (rc {rc}): {log[-800:]}"
        part = out_dir / f"part_{a:04d}.mp4"
        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-start_number", str(a), "-i", str(frames / "f_%04d.png"),
                            "-frames:v", str(b - a + 1), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", str(part)], capture_output=True, text=True, timeout=300)
        if r.returncode != 0:
            return None, f"ffmpeg chunk {a}-{b} failed"
        parts.append(part)
    lst = out_dir / "parts.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in parts))
    mp4 = out_dir / "shot.mp4"
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(mp4)], cwd=out_dir, capture_output=True, text=True, timeout=300)
    return (mp4 if r.returncode == 0 and mp4.exists() else None), ("ok" if r.returncode == 0 else "concat failed")
