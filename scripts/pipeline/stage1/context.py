from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

# Load dependent modules by absolute path to avoid package installation issues.
_REPO_ROOT = Path(__file__).resolve().parents[3]
_CHAPTER_PATH = _REPO_ROOT / "scripts" / "pipeline" / "chapter.py"
_APPROVALS_PATH = _REPO_ROOT / "scripts" / "pipeline" / "approvals.py"

import importlib.util

def _load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module {module_name} from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

_chapter_mod = _load_module("chapter", _CHAPTER_PATH)
_approvals_mod = _load_module("approvals", _APPROVALS_PATH)

chapter_paths = _chapter_mod.chapter_paths
sha256_file = _approvals_mod.sha256_file
load_approvals = _approvals_mod.load
approval_status = _approvals_mod.status


def _read_ovis(source_ovis: Path) -> tuple[list[int], list[str]]:
    """Read OVI numbers from a JSONL file."""
    ovis: set[int] = set()
    problems: list[str] = []
    if not source_ovis.is_file():
        problems.append("source_ovis: missing")
        return [], problems
    try:
        with source_ovis.open("r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    problems.append(f"source_ovis: bad line {i}")
                    continue
                if not isinstance(obj, dict):
                    problems.append(f"source_ovis: bad line {i}")
                    continue
                ovi = obj.get("ovi")
                if isinstance(ovi, bool) or not isinstance(ovi, int):
                    problems.append(f"source_ovis: bad line {i}")
                    continue
                ovis.add(ovi)
    except Exception as e:
        problems.append(f"source_ovis: {e.__class__.__name__}")
    return sorted(ovis), problems


def _read_omissions(
    omissions_path: Path, approvals_path: Path
) -> tuple[list[int], list[str]]:
    """Read approved omissions OVI list."""
    problems: list[str] = []
    if not omissions_path.is_file():
        return [], problems  # absent file -> empty list, no problem

    # Read omissions file
    try:
        with omissions_path.open("r", encoding="utf-8") as f:
            omissions_data = json.load(f)
    except Exception as e:
        problems.append(f"omissions: {e.__class__.__name__}")
        return [], problems

    if not isinstance(omissions_data, dict):
        problems.append("omissions: not an object")
        return [], problems

    ovis = omissions_data.get("ovis", [])
    if not isinstance(ovis, list):
        ovis = []
    else:
        ovis = [int(v) for v in ovis if isinstance(v, int) and not isinstance(v, bool)]

    # Load approvals mapping
    try:
        approvals = load_approvals(approvals_path)
    except Exception:
        approvals = {}
    if not isinstance(approvals, dict):
        approvals = {}

    # Compute status
    try:
        current_sha = sha256_file(omissions_path)
    except Exception as e:
        problems.append(f"omissions: {e.__class__.__name__}")
        return [], problems

    try:
        status = approval_status(approvals, "stage1_omissions", current_sha)
    except Exception as e:
        problems.append(f"omissions: {e.__class__.__name__}")
        return [], problems

    if status == "APPROVED":
        return ovis, problems
    else:
        problems.append(f"omissions: {status} (the owner has not approved the current omissions file)")
        return [], problems


def _read_voice_library(voice_lib_path: Path) -> tuple[dict[str, str], dict[str, str], list[str], list[str]]:
    """Read voice library and return saved_voices, series_voices, verified_voices, problems."""
    saved_voices: dict[str, str] = {}
    series_voices: dict[str, str] = {}
    verified_voices: list[str] = []
    problems: list[str] = []

    if not voice_lib_path.is_file():
        problems.append("voice_library: missing")
        return saved_voices, series_voices, verified_voices, problems

    try:
        with voice_lib_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        problems.append(f"voice_library: {e.__class__.__name__}")
        return saved_voices, series_voices, verified_voices, problems

    if not isinstance(data, dict):
        problems.append("voice_library: not an object")
        return saved_voices, series_voices, verified_voices, problems

    voices = data.get("voices", [])
    if not isinstance(voices, list):
        problems.append("voice_library: bad voices")
        voices = []

    for entry in voices:
        if not isinstance(entry, dict):
            continue
        voice_key = entry.get("voice_key")
        voice_id = entry.get("voice_id")
        if isinstance(voice_key, str) and isinstance(voice_id, str):
            saved_voices[voice_key] = voice_id

        assigned = entry.get("assigned_to", [])
        if isinstance(assigned, list):
            for char_id in assigned:
                if not isinstance(char_id, str):
                    continue
                if char_id in series_voices:
                    problems.append(f"voices: character {char_id} is assigned to more than one voice")
                else:
                    series_voices[char_id] = voice_key

        marathi = entry.get("marathi_verified")
        hindi = entry.get("hindi_verified")
        if marathi is True and hindi is True and isinstance(voice_key, str):
            verified_voices.append(voice_key)

    return saved_voices, series_voices, verified_voices, problems


def _read_presets(preset_index_path: Path) -> tuple[list[str], list[str]]:
    """Read preset IDs from index.json."""
    problems: list[str] = []
    if not preset_index_path.is_file():
        problems.append("presets: missing")
        return [], problems
    try:
        with preset_index_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        problems.append(f"presets: {e.__class__.__name__}")
        return [], problems

    if not isinstance(data, list):
        problems.append("presets: not a list")
        return [], problems

    preset_ids: list[str] = []
    for item in data:
        if isinstance(item, dict):
            preset = item.get("preset")
            if isinstance(preset, str):
                preset_ids.append(preset)
    return preset_ids, problems


def _read_sound_palette(sound_palette_path: Path) -> tuple[list[str], list[str]]:
    """Read sound IDs from palette.json."""
    problems: list[str] = []
    if not sound_palette_path.is_file():
        return [], problems  # absent -> empty, no problem
    try:
        with sound_palette_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        problems.append(f"sound_palette: {e.__class__.__name__}")
        return [], problems

    sound_ids: list[str] = []
    sounds_list: list[Any] = []
    if isinstance(data, dict):
        sounds_list = data.get("sounds", [])
    elif isinstance(data, list):
        sounds_list = data
    else:
        problems.append("sounds: bad palette")
        sounds_list = []

    if isinstance(sounds_list, list):
        for item in sounds_list:
            if isinstance(item, dict):
                sid = item.get("id")
                if isinstance(sid, str):
                    sound_ids.append(sid)
    return sound_ids, problems


def build_ctx(adhyay: int, root: Path | str, extra: dict | None = None) -> tuple[dict, list[str]]:
    """Build the Stage 1 context dictionary for the given adhyay."""
    root_path = Path(root)
    problems: list[str] = []

    # Validate adhyay
    if type(adhyay) is not int or not (1 <= adhyay <= 21):
        return {}, ["adhyay must be an int in 1..21"]

    # Get chapter-specific paths
    try:
        paths = chapter_paths(adhyay, root_path)
    except Exception as e:
        problems.append(f"chapter_paths: {e.__class__.__name__}")
        paths = {}

    # 1. chapter_ovis
    source_ovis = paths.get("source_ovis")
    chapter_ovis: list[int] = []
    if source_ovis:
        chapter_ovis, ovi_problems = _read_ovis(source_ovis)
        problems.extend(ovi_problems)

    # 2. unfilmed_ovis
    omissions_path = paths.get("stage1_dir")
    approvals_path = paths.get("approvals")
    unfilmed_ovis: list[int] = []
    if omissions_path and approvals_path:
        omissions_file = omissions_path / "omissions_approved.json"
        unfilmed_ovis, om_problems = _read_omissions(omissions_file, approvals_path)
        problems.extend(om_problems)

    # 3. Voice library
    voice_lib_path = root_path / "canon" / "series" / "voices.json"
    saved_voices, series_voices, verified_voices, voice_problems = _read_voice_library(voice_lib_path)
    problems.extend(voice_problems)

    # 4. Preset IDs
    preset_index_path = root_path / "assets" / "v5_presets" / "index.json"
    preset_ids, preset_problems = _read_presets(preset_index_path)
    problems.extend(preset_problems)

    # 5. Sound IDs
    sound_palette_path = root_path / "canon" / "series" / "sounds" / "palette.json"
    sound_ids, sound_problems = _read_sound_palette(sound_palette_path)
    problems.extend(sound_problems)

    # Build base context
    ctx: dict = {
        "chapter_ovis": chapter_ovis,
        "unfilmed_ovis": unfilmed_ovis,
        "saved_voices": saved_voices,
        "series_voices": series_voices,
        "verified_voices": verified_voices,
        "preset_ids": preset_ids,
        "sound_ids": sound_ids,
        # Defaults for keys that come from Stage 1 documents
        "script_line_ids": [],
        "core_line_ids": [],
        "script_texts": [],
        "speaking_characters": [],
        "known_states": {},
    }

    # Apply extra overrides
    if isinstance(extra, dict):
        ctx.update(extra)

    return ctx, problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Stage 1 context for an Adhyay")
    parser.add_argument("--adhyay", type=int, required=True, help="Adhyay number (1..21)")
    parser.add_argument("--root", type=Path, default=_REPO_ROOT, help="Repository root")
    parser.add_argument("--out", type=Path, help="Output JSON file (default: stdout)")
    args = parser.parse_args(argv)

    ctx, problems = build_ctx(args.adhyay, args.root)

    # Output JSON
    json_str = json.dumps(ctx, ensure_ascii=False, indent=2, sort_keys=True)
    if args.out:
        if args.out.exists():
            print("refused: file exists", file=sys.stderr)
            return 2
        args.out.write_text(json_str, encoding="utf-8")
    else:
        print(json_str)

    # Print problems to stderr
    for prob in problems:
        print(f"problem: {prob}", file=sys.stderr)

    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
