# FIX CALL: return BOTH files in full: `scripts/pipeline/stage1/context.py` and `tests/test_stage1_context.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
FF........FFF                                                            [100%]
================================== FAILURES ===================================
_______________________________ test_happy_path _______________________________
tests\test_stage1_context.py:116: in test_happy_path
    assert problems == []
E   AssertionError: assert ['source_ovis...: bad line 5'] == []
E     
E     Left contains 2 more items, first extra item: 'source_ovis: bad line 4'
E     Use -v to get more diff
___________________________ test_omissions_approved ___________________________
tests\test_stage1_context.py:151: in test_omissions_approved
    assert ctx["unfilmed_ovis"] == [5, 6]
E   assert [] == [5, 6]
E     
E     Right contains 2 more items, first extra item: 5
E     Use -v to get more diff
____________________________ test_generic_adhyay_3 ____________________________
tests\test_stage1_context.py:272: in test_generic_adhyay_3
    assert problems == []
E   AssertionError: assert ['source_ovis...: bad line 5'] == []
E     
E     Left contains 2 more items, first extra item: 'source_ovis: bad line 4'
E     Use -v to get more diff
____________________________ test_main_writes_json ____________________________
tests\test_stage1_context.py:283: in test_main_writes_json
    assert ret == 0
E   assert 1 == 0
---------------------------- Captured stderr call -----------------------------
problem: source_ovis: bad line 4
problem: source_ovis: bad line 5
_______________________________ test_real_repo ________________________________
tests\test_stage1_context.py:350: in test_real_repo
    aggregate_spec.loader.exec_module(aggregate_mod)
<frozen importlib._bootstrap_external>:995: in exec_module
    ???
<frozen importlib._bootstrap_external>:1132: in get_code
    ???
<frozen importlib._bootstrap_external>:1190: in get_data
    ???
E   FileNotFoundError: [Errno 2] No such file or directory: 'D:\\aai work\\granthstudio\\scripts\\pipeline\\aggregate.py'
=========================== short test summary info ===========================
FAILED tests/test_stage1_context.py::test_happy_path - AssertionError: assert...
FAILED tests/test_stage1_context.py::test_omissions_approved - assert [] == [...
FAILED tests/test_stage1_context.py::test_generic_adhyay_3 - AssertionError: ...
FAILED tests/test_stage1_context.py::test_main_writes_json - assert 1 == 0
FAILED tests/test_stage1_context.py::test_real_repo - FileNotFoundError: [Err...
5 failed, 8 passed in 0.24s

```

## SPEC
# SPEC: NEW `scripts/pipeline/stage1/context.py` + NEW `tests/test_stage1_context.py`. Return exactly these TWO files in full; do not output or change any other file.
Purpose (checklist N9): build the Stage 1 context dict `ctx` for `aggregate.validate_all(adhyay, docs, ctx)` from REAL data instead of by hand, for ANY Adhyay (1..21): nothing in the code may be specific to one chapter. Standard library only; `from __future__ import annotations`; nothing at import time except imports and definitions; no print except in `main()`; this module never reads, prints or writes any key or secret (the voice library contains voice ids and descriptions only). Plain functions, no classes, no config. Do not over-engineer.

## Existing code you may use (load by importlib BY PATH; do not modify them)
- `scripts/pipeline/chapter.py`: `chapter_paths(adhyay: int, root: Path) -> dict[str, Path]` with, among others, the keys `source_ovis` (jsonl, one JSON object per line with an int field `ovi`), `approvals` (json file), `stage1_dir` (folder). It raises ValueError for an adhyay outside 1..21.
- `scripts/pipeline/approvals.py`: `sha256_file(path) -> str`, `load(path) -> dict` (the approvals mapping; may raise on a missing file: handle that yourself), `status(approvals: dict, item: str, current_sha256) -> "DRAFT" | "APPROVED" | "STALE"` (APPROVED only when the recorded and the current sha256 are both valid and equal).
- The repo root in this module: `Path(__file__).resolve().parents[3]` (this file is `scripts/pipeline/stage1/context.py`). In tests the repo root is `Path(__file__).resolve().parents[1]`.
Data files (all relative to a `root` argument so tests can use tmp_path):
- Voice library `root/canon/series/voices.json`: `{"generated":..,"source":..,"version":..,"voices":[{"voice_key": str, "voice_id": str, "assigned_to": [character_id, ...], "marathi_verified": bool, "hindi_verified": bool, "status": str, "description": str, ...}, ...]}` (a list of 35 entries in the real file).
- Preset index `root/assets/v5_presets/index.json`: a JSON list of objects each with a string field `preset` (the preset id).
- Sound palette `root/canon/series/sounds/palette.json` (may not exist yet): a JSON object with a list `sounds` of objects with a string field `id`; or a plain list of such objects. When the file is absent the sound ids are [].
- Owner-approved omissions `chapter_paths(...)["stage1_dir"] / "omissions_approved.json"`: `{"adhyay": N, "ovis": [int, ...]}`; the approval item name is `stage1_omissions` (hash = sha256 of that file).

## API
- `build_ctx(adhyay: int, root: Path | str, extra: dict | None = None) -> tuple[dict, list[str]]`: returns `(ctx, problems)`; NEVER raises (any exception inside a source read becomes a problem string `<source>: <ExceptionClass>`); an invalid adhyay returns `({}, ["adhyay must be an int in 1..21"])`. ctx keys and sources:
  - `chapter_ovis`: sorted unique int values of the field `ovi` of every JSON line of `source_ovis` (skip blank lines; a bad line adds the problem `source_ovis: bad line <n>` and is skipped; bool is not an int). Missing file: `[]` and the problem `source_ovis: missing`.
  - `unfilmed_ovis`: if `omissions_approved.json` is absent -> `[]` and NO problem. If it exists: read its `ovis` (ints only); load the approvals mapping (a missing or unreadable approvals file means empty); compute `status(approvals, "stage1_omissions", sha256_file(omissions file))`; when it is `APPROVED` use the ovis, else use `[]` and add the problem `omissions: <status> (the owner has not approved the current omissions file)`.
  - `saved_voices`: dict `{voice_key: voice_id}` of every library entry (both strings). `series_voices`: dict `{character_id: voice_key}` built from the `assigned_to` lists (a character assigned to two voices keeps the first and adds the problem `voices: character <id> is assigned to more than one voice`). `verified_voices`: list of voice_keys with `marathi_verified` AND `hindi_verified` both exactly True. Missing or unreadable library: `{}`, `{}`, `[]` and the problem `voice_library: missing`.
  - `preset_ids`: list of the `preset` strings of the preset index, in file order (missing -> `[]` and the problem `presets: missing`).
  - `sound_ids`: the ids of the sound palette as above (`[]` when absent, no problem).
  - Keys NOT built here (they come from the script and from the Stage 1 documents): `script_line_ids`, `core_line_ids`, `script_texts`, `speaking_characters`, `known_states`; they default to `[]`/`{}` (known_states `{}`) and are overridden by the optional `extra` dict: `ctx.update(extra)` for a dict `extra` (a non-dict is ignored), applied LAST.
- `main(argv=None) -> int`: `--adhyay N` (int, required), `--root PATH` (default the repo root), optional `--out PATH`. Builds the ctx, writes it as JSON (`ensure_ascii=False`, `indent=2`, sorted keys) to `--out` (refusing with `refused: file exists` and returning 2 if it exists) or prints it to stdout, prints each problem on its own line to stderr as `problem: <text>`, and returns 0 when there are no problems, 1 otherwise. `if __name__ == "__main__": raise SystemExit(main())`.

## Tests (`tests/test_stage1_context.py`; synthetic data in tmp_path, plus ONE real-file test against the repo; load the module by path with importlib)
Build a small synthetic root in tmp_path with helpers (write files by `json.dumps`): `canon/adhyay_02/source/ovis.jsonl` (use `chapter_paths(2, root)` conventions: for adhyay 2 the paths are `canon/adhyay_02/source/ovis.jsonl`, `canon/adhyay_02/approvals.json`, `canon/adhyay_02/stage1/`), a voice library of 3 voices (one with assigned_to ["gajanan_maharaj"] and both flags True, one unverified, one unassigned), a preset index of 2 presets, no sound palette.
1. Happy path: chapter_ovis sorted unique ints; presets in order; saved_voices dict; series_voices maps the character to its key; verified_voices has only the fully verified key; sound_ids []; unfilmed_ovis [] with no problems; script keys default.
2. Omissions: file present + approvals item `stage1_omissions` with the CURRENT sha256 -> ovis returned and no problem; present but approvals empty (DRAFT) -> [] and a problem containing `DRAFT`; approved then the omissions file edited (STALE) -> [] and a problem containing `STALE`; absent file -> [] and no problem.
3. Missing sources each give their problem and an empty value without raising: no ovis file, no voice library, no preset index; a bad jsonl line is skipped with its problem; a character assigned to two voices.
4. `extra` overrides (e.g. `script_texts`, `unfilmed_ovis`) and a non-dict extra is ignored; invalid adhyay (0, 22, True, "x") returns the problem and `{}`.
5. Generic: the same synthetic data for adhyay 3 under `canon/adhyay_03/...` works with no code difference.
6. `main`: writes the JSON to `--out`, refuses an existing file with return 2, prints problems to stderr and returns 1; returns 0 with no problems (capsys).
7. REAL repo test (use `skipif` if a file is missing): `build_ctx(1, ROOT)` and the real voice library: `saved_voices` has 35 keys, `verified_voices` contains only keys whose two flags are True in the file, `series_voices` has no more entries than characters assigned in the file, and `preset_ids` contains `01_establishing_shot`. Also `aggregate.validate_all` accepts the produced ctx without raising (call it with empty docs and assert it returns a list).

Reply with only the two FILE blocks:
FILE: scripts/pipeline/stage1/context.py
FILE: tests/test_stage1_context.py


## CURRENT MODULE scripts/pipeline/stage1/context.py
```python
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

    # Compute status
    try:
        current_sha = sha256_file(omissions_path)
    except Exception as e:
        problems.append(f"omissions: {e.__class__.__name__}")
        return [], problems

    status = approval_status(approvals, "stage1_omissions", current_sha)
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

    voices = data.get("voices", [])
    if not isinstance(voices, list):
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

    preset_ids: list[str] = []
    if isinstance(data, list):
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
        "script_texts": {},
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

```

## CURRENT TESTS tests/test_stage1_context.py
```python
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import pytest

# Load the context module by path
TEST_DIR = Path(__file__).resolve().parent
REPO_ROOT = TEST_DIR.parent
CONTEXT_PATH = REPO_ROOT / "scripts" / "pipeline" / "stage1" / "context.py"

import importlib.util

spec = importlib.util.spec_from_file_location("context", CONTEXT_PATH)
assert spec is not None and spec.loader is not None
context_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(context_mod)

build_ctx = context_mod.build_ctx
main = context_mod.main


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def _write_jsonl(path: Path, lines: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for line in lines:
            f.write(json.dumps(line) + "\n")


def _setup_synthetic_root(tmp_path: Path, adhyay: int) -> Path:
    """Create a synthetic repo structure for the given adhyay under tmp_path."""
    root = tmp_path
    # Chapter paths follow chapter.py conventions: canon/adhyay_XX/
    adhyay_dir = root / "canon" / f"adhyay_{adhyay:02d}"
    source_dir = adhyay_dir / "source"
    stage1_dir = adhyay_dir / "stage1"

    # ovis.jsonl
    _write_jsonl(source_dir / "ovis.jsonl", [
        {"ovi": 1, "text": "line 1"},
        {"ovi": 2, "text": "line 2"},
        {"ovi": 1, "text": "duplicate"},
        {"ovi": "not an int"},  # bad line
        {},  # missing ovi
        {"ovi": 3},
    ])

    # approvals.json (empty initially)
    _write_json(adhyay_dir / "approvals.json", {})

    # stage1 directory exists
    stage1_dir.mkdir(parents=True, exist_ok=True)

    # Voice library
    voice_lib = root / "canon" / "series" / "voices.json"
    _write_json(voice_lib, {
        "generated": "2024-01-01",
        "source": "test",
        "version": 1,
        "voices": [
            {
                "voice_key": "vk_gajanan",
                "voice_id": "vid_1",
                "assigned_to": ["gajanan_maharaj"],
                "marathi_verified": True,
                "hindi_verified": True,
                "status": "active",
                "description": "Gajanan Maharaj"
            },
            {
                "voice_key": "vk_unverified",
                "voice_id": "vid_2",
                "assigned_to": ["other_char"],
                "marathi_verified": False,
                "hindi_verified": True,
                "status": "active",
                "description": "Unverified"
            },
            {
                "voice_key": "vk_unassigned",
                "voice_id": "vid_3",
                "assigned_to": [],
                "marathi_verified": True,
                "hindi_verified": True,
                "status": "active",
                "description": "Unassigned"
            }
        ]
    })

    # Preset index
    preset_index = root / "assets" / "v5_presets" / "index.json"
    _write_json(preset_index, [
        {"preset": "01_establishing_shot"},
        {"preset": "02_close_up"}
    ])

    # No sound palette file

    return root


def test_happy_path(tmp_path: Path):
    root = _setup_synthetic_root(tmp_path, 2)
    ctx, problems = build_ctx(2, root)

    assert problems == []
    assert ctx["chapter_ovis"] == [1, 2, 3]
    assert ctx["preset_ids"] == ["01_establishing_shot", "02_close_up"]
    assert ctx["saved_voices"] == {
        "vk_gajanan": "vid_1",
        "vk_unverified": "vid_2",
        "vk_unassigned": "vid_3"
    }
    assert ctx["series_voices"] == {"gajanan_maharaj": "vk_gajanan", "other_char": "vk_unverified"}
    assert ctx["verified_voices"] == ["vk_gajanan", "vk_unassigned"]
    assert ctx["sound_ids"] == []
    assert ctx["unfilmed_ovis"] == []
    # Default script keys
    assert ctx["script_line_ids"] == []
    assert ctx["core_line_ids"] == []
    assert ctx["script_texts"] == {}
    assert ctx["speaking_characters"] == []
    assert ctx["known_states"] == {}


def test_omissions_approved(tmp_path: Path):
    root = _setup_synthetic_root(tmp_path, 2)
    adhyay_dir = root / "canon" / "adhyay_02"
    stage1_dir = adhyay_dir / "stage1"
    approvals_file = adhyay_dir / "approvals.json"

    # Create omissions file with ovis [5, 6]
    omissions_file = stage1_dir / "omissions_approved.json"
    _write_json(omissions_file, {"adhyay": 2, "ovis": [5, 6]})

    # Compute its sha256 and put into approvals
    sha = hashlib.sha256(omissions_file.read_bytes()).hexdigest()
    _write_json(approvals_file, {"stage1_omissions": sha})

    ctx, problems = build_ctx(2, root)
    assert ctx["unfilmed_ovis"] == [5, 6]
    assert problems == []


def test_omissions_draft(tmp_path: Path):
    root = _setup_synthetic_root(tmp_path, 2)
    adhyay_dir = root / "canon" / "adhyay_02"
    stage1_dir = adhyay_dir / "stage1"
    # approvals.json is empty (DRAFT)
    omissions_file = stage1_dir / "omissions_approved.json"
    _write_json(omissions_file, {"adhyay": 2, "ovis": [5, 6]})

    ctx, problems = build_ctx(2, root)
    assert ctx["unfilmed_ovis"] == []
    assert any("DRAFT" in p for p in problems)


def test_omissions_stale(tmp_path: Path):
    root = _setup_synthetic_root(tmp_path, 2)
    adhyay_dir = root / "canon" / "adhyay_02"
    stage1_dir = adhyay_dir / "stage1"
    approvals_file = adhyay_dir / "approvals.json"

    omissions_file = stage1_dir / "omissions_approved.json"
    _write_json(omissions_file, {"adhyay": 2, "ovis": [5, 6]})
    sha = hashlib.sha256(omissions_file.read_bytes()).hexdigest()
    _write_json(approvals_file, {"stage1_omissions": sha})

    # Now modify omissions file (make it stale)
    _write_json(omissions_file, {"adhyay": 2, "ovis": [7, 8]})

    ctx, problems = build_ctx(2, root)
    assert ctx["unfilmed_ovis"] == []
    assert any("STALE" in p for p in problems)


def test_omissions_absent(tmp_path: Path):
    root = _setup_synthetic_root(tmp_path, 2)
    # No omissions file
    ctx, problems = build_ctx(2, root)
    assert ctx["unfilmed_ovis"] == []
    assert not any(p.startswith("omissions:") for p in problems)


def test_missing_sources(tmp_path: Path):
    root = tmp_path
    # No ovis file, no voice library, no preset index
    adhyay_dir = root / "canon" / "adhyay_02"
    adhyay_dir.mkdir(parents=True)
    (adhyay_dir / "approvals.json").write_text("{}")
    (adhyay_dir / "stage1").mkdir(parents=True)

    ctx, problems = build_ctx(2, root)
    assert ctx["chapter_ovis"] == []
    assert ctx["saved_voices"] == {}
    assert ctx["series_voices"] == {}
    assert ctx["verified_voices"] == []
    assert ctx["preset_ids"] == []
    assert ctx["sound_ids"] == []
    assert "source_ovis: missing" in problems
    assert "voice_library: missing" in problems
    assert "presets: missing" in problems


def test_bad_jsonl_line(tmp_path: Path):
    root = _setup_synthetic_root(tmp_path, 2)
    # The synthetic root already has a bad line in ovis.jsonl (line 4)
    ctx, problems = build_ctx(2, root)
    assert any("source_ovis: bad line 4" in p for p in problems)


def test_character_assigned_to_two_voices(tmp_path: Path):
    root = _setup_synthetic_root(tmp_path, 2)
    # Modify voice library to assign same character to two voices
    voice_lib = root / "canon" / "series" / "voices.json"
    data = json.loads(voice_lib.read_text())
    data["voices"].append({
        "voice_key": "vk_duplicate",
        "voice_id": "vid_4",
        "assigned_to": ["gajanan_maharaj"],  # already assigned to vk_gajanan
        "marathi_verified": True,
        "hindi_verified": True,
        "status": "active",
        "description": "Duplicate"
    })
    _write_json(voice_lib, data)

    ctx, problems = build_ctx(2, root)
    assert any("voices: character gajanan_maharaj is assigned to more than one voice" in p for p in problems)
    # The first assignment should remain
    assert ctx["series_voices"]["gajanan_maharaj"] == "vk_gajanan"


def test_extra_overrides(tmp_path: Path):
    root = _setup_synthetic_root(tmp_path, 2)
    extra = {
        "script_texts": {"1": "hello"},
        "unfilmed_ovis": [99],  # override
        "new_key": "value"
    }
    ctx, problems = build_ctx(2, root, extra=extra)
    assert ctx["script_texts"] == {"1": "hello"}
    assert ctx["unfilmed_ovis"] == [99]
    assert ctx["new_key"] == "value"

    # Non-dict extra is ignored
    ctx2, _ = build_ctx(2, root, extra="not a dict")
    assert "new_key" not in ctx2


def test_invalid_adhyay(tmp_path: Path):
    root = _setup_synthetic_root(tmp_path, 2)
    for bad in [0, 22, True, "x", -1]:
        ctx, problems = build_ctx(bad, root)  # type: ignore
        assert ctx == {}
        assert problems == ["adhyay must be an int in 1..21"]


def test_generic_adhyay_3(tmp_path: Path):
    root = _setup_synthetic_root(tmp_path, 3)
    ctx, problems = build_ctx(3, root)
    assert problems == []
    assert ctx["chapter_ovis"] == [1, 2, 3]
    # All other keys should be populated similarly


def test_main_writes_json(tmp_path: Path, capsys: pytest.CaptureFixture):
    root = _setup_synthetic_root(tmp_path, 2)
    out_file = tmp_path / "ctx.json"

    # Test writing to file
    ret = main(["--adhyay", "2", "--root", str(root), "--out", str(out_file)])
    assert ret == 0
    assert out_file.exists()
    data = json.loads(out_file.read_text())
    assert data["chapter_ovis"] == [1, 2, 3]

    # Test refusing existing file
    ret = main(["--adhyay", "2", "--root", str(root), "--out", str(out_file)])
    assert ret == 2
    captured = capsys.readouterr()
    assert "refused: file exists" in captured.err

    # Test stdout output
    ret = main(["--adhyay", "2", "--root", str(root)])
    assert ret == 0
    captured = capsys.readouterr()
    assert "chapter_ovis" in captured.out

    # Test problems printed to stderr and return 1
    # Create a root with missing voice library to generate a problem
    bad_root = tmp_path / "bad"
    bad_root.mkdir()
    (bad_root / "canon" / "adhyay_02" / "source").mkdir(parents=True)
    (bad_root / "canon" / "adhyay_02" / "approvals.json").write_text("{}")
    (bad_root / "canon" / "adhyay_02" / "stage1").mkdir(parents=True)
    _write_jsonl(bad_root / "canon" / "adhyay_02" / "source" / "ovis.jsonl", [{"ovi": 1}])
    # No voice library, no preset index
    ret = main(["--adhyay", "2", "--root", str(bad_root)])
    assert ret == 1
    captured = capsys.readouterr()
    assert "problem: voice_library: missing" in captured.err
    assert "problem: presets: missing" in captured.err


@pytest.mark.skipif(
    not (REPO_ROOT / "canon" / "series" / "voices.json").exists(),
    reason="Real repo voices.json not found"
)
@pytest.mark.skipif(
    not (REPO_ROOT / "assets" / "v5_presets" / "index.json").exists(),
    reason="Real repo preset index not found"
)
def test_real_repo():
    """Test against the real repository (Adhyay 1)."""
    ctx, problems = build_ctx(1, REPO_ROOT)
    # Real voice library has 35 entries
    assert len(ctx["saved_voices"]) == 35
    # verified_voices only those with both flags True
    # We can't know exact count, but ensure it's a subset of saved_voices keys
    assert all(vk in ctx["saved_voices"] for vk in ctx["verified_voices"])
    # series_voices entries <= total assigned characters in file
    # Load the real file to check
    with open(REPO_ROOT / "canon" / "series" / "voices.json", "r", encoding="utf-8") as f:
        real_data = json.load(f)
    assigned_chars = set()
    for voice in real_data.get("voices", []):
        for char in voice.get("assigned_to", []):
            assigned_chars.add(char)
    assert len(ctx["series_voices"]) <= len(assigned_chars)
    # preset_ids contains "01_establishing_shot"
    assert "01_establishing_shot" in ctx["preset_ids"]

    # Now test that aggregate.validate_all accepts this ctx
    # Load aggregate module by path
    AGGREGATE_PATH = REPO_ROOT / "scripts" / "pipeline" / "aggregate.py"
    aggregate_spec = importlib.util.spec_from_file_location("aggregate", AGGREGATE_PATH)
    assert aggregate_spec is not None and aggregate_spec.loader is not None
    aggregate_mod = importlib.util.module_from_spec(aggregate_spec)
    aggregate_spec.loader.exec_module(aggregate_mod)
    validate_all = aggregate_mod.validate_all

    # Call with empty docs
    result = validate_all(1, {}, ctx)
    assert isinstance(result, list)

```

## DIAGNOSIS of the 5 failing tests (verified by running them): the TESTS are wrong; change the module only if a corrected test still fails. Return BOTH complete FILE blocks.
1. test_happy_path and test_generic_adhyay_3 (and test_main_writes_json, which returns 1 because of the same problems): the shared synthetic fixture `_setup_synthetic_root` writes an ovis.jsonl that CONTAINS bad lines (a string `ovi`, line 4 and 5), so `problems` is never empty. The shared fixture must contain ONLY valid lines (duplicates of a valid ovi are fine and test the uniqueness); create the bad-line case ONLY inside its own dedicated test by writing a separate jsonl (valid lines plus one `{"ovi": "x"}` and one blank line, and one line that is not JSON) and assert the problem `source_ovis: bad line <n>` for each bad line (blank lines are skipped without a problem).
2. test_omissions_approved: it writes approvals as `{"stage1_omissions": sha}`, but the real approvals shape is `{"stage1_omissions": {"sha256": <64 hex>, "owner": "x", "date": "2026-10-28"}}`. Write the approvals file with exactly that shape (or call `approvals.approve(path, item, sha, owner, date)` from `scripts/pipeline/approvals.py` loaded by importlib). The STALE test must edit the omissions file AFTER approving and expect a problem containing STALE; the DRAFT test an empty approvals file.
3. In the default-keys assertions `script_texts` must be `[]` (a list), not `{}`.
4. test_real_repo loads `scripts/pipeline/aggregate.py` (FileNotFoundError); the real file is `scripts/pipeline/stage1/aggregate.py`. Fix the path.
