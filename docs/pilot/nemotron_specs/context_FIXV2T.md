# TASK: return ONLY ONE FILE: tests/test_stage1_context.py (complete). Reply with exactly one block `FILE: tests/test_stage1_context.py` then the python fenced. The module scripts/pipeline/stage1/context.py gained the ctx key `voice_genders` (checklist V2): a dict voice_key -> gender for every voice library entry whose voice_key is a string and whose gender is the string 'male' or 'female'; other entries are left out; a missing or bad library gives {} (the existing library problems stay); an `extra` override still wins. Keep EVERY existing test unchanged and ADD isolated tests: (1) the happy synthetic root: voice_genders has exactly the male/female entries; (2) an entry with gender 'other', a missing gender, a non-string gender and a non-string voice_key are left out; (3) a missing library file -> {} plus the `voice_library: missing` problem; (4) the JSON `[]`, `5`, `"x"`, `null` as the library -> {} and no exception; (5) `extra={'voice_genders': {'zzz': 'male'}}` overrides; (6) the REAL repo test (skipif a file is missing): `build_ctx(1, ROOT)` has voice_genders with 35 or fewer entries whose values are all 'male' or 'female'. Use copy.deepcopy and plain assignment; never a helper that rejects no-effect mutations.

## CURRENT tests/test_stage1_context.py
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

    # ovis.jsonl - only valid lines (duplicates allowed)
    _write_jsonl(source_dir / "ovis.jsonl", [
        {"ovi": 1, "text": "line 1"},
        {"ovi": 2, "text": "line 2"},
        {"ovi": 1, "text": "duplicate"},
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
    assert ctx["script_texts"] == []
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

    # Compute its sha256 and put into approvals with correct structure
    sha = hashlib.sha256(omissions_file.read_bytes()).hexdigest()
    _write_json(approvals_file, {"stage1_omissions": {"sha256": sha, "owner": "test", "date": "2026-10-28"}})

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
    _write_json(approvals_file, {"stage1_omissions": {"sha256": sha, "owner": "test", "date": "2026-10-28"}})

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


def test_omissions_not_an_object(tmp_path: Path):
    """omissions_approved.json that is valid JSON but not an object -> problem, empty list."""
    root = _setup_synthetic_root(tmp_path, 2)
    adhyay_dir = root / "canon" / "adhyay_02"
    stage1_dir = adhyay_dir / "stage1"
    approvals_file = adhyay_dir / "approvals.json"
    omissions_file = stage1_dir / "omissions_approved.json"

    for bad_val in [[], 5, "x", None]:
        _write_json(omissions_file, bad_val)
        sha = hashlib.sha256(omissions_file.read_bytes()).hexdigest()
        _write_json(approvals_file, {"stage1_omissions": {"sha256": sha, "owner": "test", "date": "2026-10-28"}})
        ctx, problems = build_ctx(2, root)
        assert ctx["unfilmed_ovis"] == []
        assert any("omissions: not an object" in p for p in problems)


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
    root = tmp_path
    adhyay_dir = root / "canon" / "adhyay_02"
    source_dir = adhyay_dir / "source"
    source_dir.mkdir(parents=True)
    # Write a jsonl with a bad line (line 2) and a blank line (line 3) and a good line (line 4)
    _write_jsonl(source_dir / "ovis.jsonl", [
        {"ovi": 1},
        {"ovi": "not an int"},  # bad line 2
        {},  # missing ovi line 3
        {"ovi": 2},
    ])
    # approvals and stage1 dir
    (adhyay_dir / "approvals.json").write_text("{}")
    (adhyay_dir / "stage1").mkdir(parents=True)
    # voice library, preset index minimal
    voice_lib = root / "canon" / "series" / "voices.json"
    voice_lib.parent.mkdir(parents=True)
    _write_json(voice_lib, {"voices": []})
    preset_index = root / "assets" / "v5_presets" / "index.json"
    preset_index.parent.mkdir(parents=True)
    _write_json(preset_index, [])

    ctx, problems = build_ctx(2, root)
    assert any("source_ovis: bad line 2" in p for p in problems)
    assert any("source_ovis: bad line 3" in p for p in problems)
    assert ctx["chapter_ovis"] == [1, 2]


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


def test_voice_library_not_an_object(tmp_path: Path):
    """voice_library.json that is valid JSON but not an object -> problem, empty dicts."""
    root = _setup_synthetic_root(tmp_path, 2)
    voice_lib = root / "canon" / "series" / "voices.json"
    for bad_val in [[], 5, "x", None]:
        _write_json(voice_lib, bad_val)
        ctx, problems = build_ctx(2, root)
        assert ctx["saved_voices"] == {}
        assert ctx["series_voices"] == {}
        assert ctx["verified_voices"] == []
        assert any("voice_library: not an object" in p for p in problems)


def test_voice_library_bad_voices(tmp_path: Path):
    """voice_library.json with voices not a list -> problem, empty dicts."""
    root = _setup_synthetic_root(tmp_path, 2)
    voice_lib = root / "canon" / "series" / "voices.json"
    _write_json(voice_lib, {"voices": "not a list"})
    ctx, problems = build_ctx(2, root)
    assert ctx["saved_voices"] == {}
    assert ctx["series_voices"] == {}
    assert ctx["verified_voices"] == []
    assert any("voice_library: bad voices" in p for p in problems)


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


def test_presets_not_a_list(tmp_path: Path):
    """preset index.json that is valid JSON but not a list -> problem, empty list."""
    root = _setup_synthetic_root(tmp_path, 2)
    preset_index = root / "assets" / "v5_presets" / "index.json"
    for bad_val in [{}, 5, "x", None]:
        _write_json(preset_index, bad_val)
        ctx, problems = build_ctx(2, root)
        assert ctx["preset_ids"] == []
        assert any("presets: not a list" in p for p in problems)


def test_sound_palette_bad_types(tmp_path: Path):
    """sound palette that is valid JSON but not dict/list -> problem, empty list."""
    root = _setup_synthetic_root(tmp_path, 2)
    sound_palette = root / "canon" / "series" / "sounds" / "palette.json"
    sound_palette.parent.mkdir(parents=True)
    for bad_val in [5, "x", None, True]:
        _write_json(sound_palette, bad_val)
        ctx, problems = build_ctx(2, root)
        assert ctx["sound_ids"] == []
        assert any("sounds: bad palette" in p for p in problems)


def test_sound_palette_dict_without_sounds(tmp_path: Path):
    """sound palette as dict without 'sounds' key -> empty list, no problem."""
    root = _setup_synthetic_root(tmp_path, 2)
    sound_palette = root / "canon" / "series" / "sounds" / "palette.json"
    sound_palette.parent.mkdir(parents=True)
    _write_json(sound_palette, {"other": "data"})
    ctx, problems = build_ctx(2, root)
    assert ctx["sound_ids"] == []
    assert not any("sounds:" in p for p in problems)


def test_approvals_not_an_object(tmp_path: Path):
    """approvals.json that is valid JSON but not an object -> treated as empty."""
    root = _setup_synthetic_root(tmp_path, 2)
    adhyay_dir = root / "canon" / "adhyay_02"
    approvals_file = adhyay_dir / "approvals.json"
    for bad_val in [[], 5, "x", None]:
        _write_json(approvals_file, bad_val)
        # Create omissions file
        stage1_dir = adhyay_dir / "stage1"
        omissions_file = stage1_dir / "omissions_approved.json"
        _write_json(omissions_file, {"adhyay": 2, "ovis": [5, 6]})
        ctx, problems = build_ctx(2, root)
        # Should treat approvals as empty -> DRAFT
        assert ctx["unfilmed_ovis"] == []
        assert any("DRAFT" in p for p in problems)


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
    # Load aggregate module by path (correct path is stage1/aggregate.py)
    AGGREGATE_PATH = REPO_ROOT / "scripts" / "pipeline" / "stage1" / "aggregate.py"
    aggregate_spec = importlib.util.spec_from_file_location("aggregate", AGGREGATE_PATH)
    assert aggregate_spec is not None and aggregate_spec.loader is not None
    aggregate_mod = importlib.util.module_from_spec(aggregate_spec)
    aggregate_spec.loader.exec_module(aggregate_mod)
    validate_all = aggregate_mod.validate_all

    # Call with empty docs
    result = validate_all(1, {}, ctx)
    assert isinstance(result, list)
```
## scripts/pipeline/stage1/context.py (reference only)
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


def _read_voice_library(voice_lib_path: Path) -> tuple[dict[str, str], dict[str, str], list[str], dict[str, str], list[str]]:
    """Read voice library and return saved_voices, series_voices, verified_voices, voice_genders, problems."""
    saved_voices: dict[str, str] = {}
    series_voices: dict[str, str] = {}
    verified_voices: list[str] = []
    voice_genders: dict[str, str] = {}
    problems: list[str] = []

    if not voice_lib_path.is_file():
        problems.append("voice_library: missing")
        return saved_voices, series_voices, verified_voices, voice_genders, problems

    try:
        with voice_lib_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        problems.append(f"voice_library: {e.__class__.__name__}")
        return saved_voices, series_voices, verified_voices, voice_genders, problems

    if not isinstance(data, dict):
        problems.append("voice_library: not an object")
        return saved_voices, series_voices, verified_voices, voice_genders, problems

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

        gender = entry.get("gender")
        if isinstance(voice_key, str) and gender in ("male", "female"):
            voice_genders[voice_key] = gender

    return saved_voices, series_voices, verified_voices, voice_genders, problems


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
    saved_voices, series_voices, verified_voices, voice_genders, voice_problems = _read_voice_library(voice_lib_path)
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
        "voice_genders": voice_genders,
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
```
