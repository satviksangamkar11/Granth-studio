# TASK: return ONLY ONE FILE: scripts/pipeline/check_script_cli.py (complete). Reply with exactly one block `FILE: scripts/pipeline/check_script_cli.py` then the python fenced. Keep everything that works (12 tests pass); fix EXACTLY the two defects below reported by the GLM reviewer (verified against the spec); change nothing else. Spec: docs/pilot/nemotron_specs/check_script_cli.md.
## Defects
1. **CLASS 2 — `run_check` can raise; the spec says "NEVER raises".**
   - `scripts/pipeline/check_script_cli.py:66` guards only `script_path.exists()`. A **directory** placed at `chapter_paths(...)["script"]` passes that guard and reaches `read_text` at `:81`, which raises `IsADirectoryError` (POSIX) / `PermissionError` (Windows).
   - `scripts/pipeline/check_script_cli.py:81` `script_path.read_text(encoding="utf-8")` raises `UnicodeDecodeError` for any non-UTF-8 bytes at the script path.
   Both are odd but trivially reachable inputs (e.g. `mkdir canon/adhyay_02/script/easy.md`, or one bad byte in the script), and the spec's contract for `run_check` is explicitly "NEVER raises".
   **Exact fix:** at `:66` change the guard to `if not script_path.is_file():` (keeps the `script: missing` problem and the same empty-result dict), and wrap the read at `:81`:
   ```python
   try:
       script_text = script_path.read_text(encoding="utf-8")
   except (OSError, UnicodeDecodeError) as e:
       own_problems.append(f"script: unreadable ({e.__class__.__name__})")
       return {
           "adhyay": adhyay,
           "script": script_rel,
           "script_sha256": "",
           "lines": 0,
           "scenes": 0,
           "core": 0,
           "optional": 0,
           "errors": [],
           "problems": own_problems,
           "ok": False,
       }
   ```

2. **CLASS 1 — `main` crashes instead of returning 1 when `--write-receipt` is combined with an invalid adhyay.** Spec: "Returns 0 when ok, 1 otherwise." For `--adhyay 999 --write-receipt`, `run_check` correctly returns `ok=False`, but `main` (`scripts/pipeline/check_script_cli.py:171-177`) then calls `write_receipt`, whose `chapter_paths(adhyay, root)` (`:129`) raises `ValueError` for an adhyay outside 1..21 (stated in both specs and proven by `test_invalid_adhyay` passing through that exact branch). Only `FileExistsError` is caught (`:175`), so the `ValueError` escapes and `main` dies with a traceback instead of returning a code.
   **Exact fix:** add one branch after the `FileExistsError` handler at `:175`:
   ```python
   except ValueError as e:
       print(f"refused: {e}")
       return 2
   ```
   (`2` is the refusal code the spec already assigns in `main` for an existing receipt; `write_receipt` can raise nothing else but `FileExistsError` and this `ValueError`.)

## scripts/pipeline/stage1/context.py + tests/test_stage1_context.py (spec `context.md` + `voice_genders` amendment)
## CURRENT scripts/pipeline/check_script_cli.py
```python
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

# Load existing modules by path
_REPO_ROOT = Path(__file__).resolve().parents[2]

def _load_module(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {module_name} from {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

_check_script_mod = _load_module("check_script", _REPO_ROOT / "scripts" / "pipeline" / "check_script.py")
_chapter_mod = _load_module("chapter", _REPO_ROOT / "scripts" / "pipeline" / "chapter.py")
_context_mod = _load_module("context", _REPO_ROOT / "scripts" / "pipeline" / "stage1" / "context.py")

parse_script = _check_script_mod.parse_script
check_script = _check_script_mod.check_script
script_sha256 = _check_script_mod.script_sha256
chapter_paths = _chapter_mod.chapter_paths
build_ctx = _context_mod.build_ctx


def run_check(
    adhyay: int,
    root: Path | str,
    glossary: dict[str, str] | None = None,
    extra_voices: list[str] | None = None,
) -> dict[str, Any]:
    root_path = Path(root)
    own_problems: list[str] = []
    script_rel = ""
    script_text = ""
    lines: list[dict] = []
    script_hash = ""

    try:
        paths = chapter_paths(adhyay, root_path)
    except ValueError as e:
        own_problems.append(f"invalid adhyay: {e}")
        return {
            "adhyay": adhyay,
            "script": "",
            "script_sha256": "",
            "lines": 0,
            "scenes": 0,
            "core": 0,
            "optional": 0,
            "errors": [],
            "problems": own_problems,
            "ok": False,
        }

    script_path = paths["script"]
    script_rel = script_path.relative_to(root_path).as_posix()

    if not script_path.exists():
        own_problems.append("script: missing")
        return {
            "adhyay": adhyay,
            "script": script_rel,
            "script_sha256": "",
            "lines": 0,
            "scenes": 0,
            "core": 0,
            "optional": 0,
            "errors": [],
            "problems": own_problems,
            "ok": False,
        }

    script_text = script_path.read_text(encoding="utf-8")
    script_hash = script_sha256(script_text)
    lines = parse_script(script_text)

    ctx, ctx_problems = build_ctx(adhyay, root_path, extra=None)
    chapter_ovis = ctx.get("chapter_ovis", [])
    unfilmed_ovis = ctx.get("unfilmed_ovis", [])
    saved_voices = ctx.get("saved_voices", {})
    series_voices = ctx.get("series_voices", {})

    allowed_voices: set[str] = {"narrator"}
    allowed_voices.update(saved_voices.keys())
    allowed_voices.update(series_voices.keys())
    if extra_voices:
        allowed_voices.update(extra_voices)

    errors = check_script(
        lines,
        set(chapter_ovis),
        set(unfilmed_ovis),
        allowed_voices,
        glossary or {},
    )

    scenes = len({line.get("scene") for line in lines if line.get("scene") is not None})
    core = sum(1 for line in lines if line.get("priority") == "core")
    optional = len(lines) - core

    all_problems = ctx_problems + own_problems
    ok = (len(errors) == 0) and (len(own_problems) == 0)

    return {
        "adhyay": adhyay,
        "script": script_rel,
        "script_sha256": script_hash,
        "lines": len(lines),
        "scenes": scenes,
        "core": core,
        "optional": optional,
        "errors": errors,
        "problems": all_problems,
        "ok": ok,
    }


def write_receipt(result: dict[str, Any], root: Path | str, today: str | None = None) -> Path:
    root_path = Path(root)
    adhyay = result["adhyay"]
    paths = chapter_paths(adhyay, root_path)
    stage1_dir = paths["stage1_dir"]
    stage1_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = stage1_dir / "script_check_receipt.json"
    if receipt_path.exists():
        raise FileExistsError(receipt_path)

    receipt_data = dict(result)
    receipt_data["date"] = today or date.today().isoformat()
    receipt_data["note"] = "report only; the script was never edited"

    receipt_path.write_text(
        json.dumps(receipt_data, indent=1, sort_keys=True, ensure_ascii=False),
        encoding="utf-8",
    )
    return receipt_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check EASY script for an adhyay")
    parser.add_argument("--adhyay", type=int, required=True, help="Adhyay number")
    parser.add_argument("--root", type=Path, default=_REPO_ROOT, help="Repository root")
    parser.add_argument("--write-receipt", action="store_true", help="Write receipt JSON")
    parser.add_argument("--extra-voice", action="append", default=[], help="Extra allowed voice IDs")
    args = parser.parse_args(argv)

    result = run_check(args.adhyay, args.root, extra_voices=args.extra_voice)

    print(
        f"adhyay {result['adhyay']}: {result['lines']} lines, "
        f"{result['scenes']} scenes, {result['core']} core, "
        f"{len(result['errors'])} errors, {len(result['problems'])} problems"
    )

    errors = result["errors"]
    for i, err in enumerate(errors):
        if i >= 40:
            remaining = len(errors) - 40
            print(f"... and {remaining} more")
            break
        print(f"error: {err}")

    if args.write_receipt:
        try:
            receipt_path = write_receipt(result, args.root)
            print(f"receipt {receipt_path}")
        except FileExistsError:
            print("refused: receipt exists")
            return 2

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
```
