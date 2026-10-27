from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Import the module under test
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "pipeline"))
import voice_library as vl


# ---------- load_key tests ----------

def test_load_key_env_wins(tmp_path: Path):
    env = {"ELEVENLABS_API_KEY": "env_key_123"}
    assert vl.load_key(env=env) == "env_key_123"


def test_load_key_fallback_first_file(tmp_path: Path):
    secrets = tmp_path / "secrets"
    secrets.mkdir()
    (secrets / "a_key.txt").write_text("  first_key  ")
    (secrets / "b_key.txt").write_text("second_key")
    assert vl.load_key(env={}, secrets_dir=secrets) == "first_key"


def test_load_key_ignores_subfolders(tmp_path: Path):
    secrets = tmp_path / "secrets"
    secrets.mkdir()
    sub = secrets / "sub"
    sub.mkdir()
    (sub / "key.txt").write_text("should_not_use")
    (secrets / "real_key.txt").write_text("real_key")
    assert vl.load_key(env={}, secrets_dir=secrets) == "real_key"


def test_load_key_no_key_exits(tmp_path: Path):
    with pytest.raises(SystemExit) as exc:
        vl.load_key(env={}, secrets_dir=tmp_path / "nonexistent")
    assert "NOT_RUN" in str(exc.value)
    # Ensure no key-like value in message
    msg = str(exc.value).lower()
    assert "key" not in msg or "not_run" in msg


# ---------- fetch_voices tests ----------

def test_fetch_voices_sends_header_and_url():
    captured = {}

    def fake_http(url: str, headers: dict) -> tuple[int, bytes]:
        captured["url"] = url
        captured["headers"] = headers
        return 200, b'{"voices": [{"voice_id": "v1", "name": "Voice One"}]}'

    voices = vl.fetch_voices("test_key", http=fake_http)
    assert captured["url"] == "https://api.elevenlabs.io/v1/voices"
    assert captured["headers"]["xi-api-key"] == "test_key"
    assert captured["headers"]["Accept"] == "application/json"
    assert len(voices) == 1
    assert voices[0]["voice_id"] == "v1"


def test_fetch_voices_non_200_raises_without_key():
    def fake_http(url: str, headers: dict) -> tuple[int, bytes]:
        return 401, b"Unauthorized"

    with pytest.raises(RuntimeError) as exc:
        vl.fetch_voices("secret_key", http=fake_http)
    assert "HTTP 401" in str(exc.value)
    assert "secret_key" not in str(exc.value)


def test_fetch_voices_missing_voices_key_returns_empty():
    def fake_http(url: str, headers: dict) -> tuple[int, bytes]:
        return 200, b'{}'

    voices = vl.fetch_voices("key", http=fake_http)
    assert voices == []


# ---------- normalize tests ----------

def test_normalize_full_record():
    raw = {
        "voice_id": "v1",
        "name": "Test Voice",
        "category": "premade",
        "labels": {"gender": "female", "age": "young", "accent": "indian", "descriptive": "calm", "use_case": "narration"},
        "description": "A nice voice",
        "verified_languages": [{"language": "mr"}, {"language": "hi"}],
    }
    norm = vl.normalize(raw)
    assert norm["voice_id"] == "v1"
    assert norm["name"] == "Test Voice"
    assert norm["gender"] == "female"
    assert norm["age"] == "young"
    assert norm["accent"] == "indian"
    assert norm["descriptive"] == "calm"
    assert norm["use_case"] == "narration"
    assert norm["description"] == "A nice voice"
    assert norm["marathi_verified"] is True
    assert norm["hindi_verified"] is True


def test_normalize_all_fields_missing():
    raw = {}
    norm = vl.normalize(raw)
    assert norm["voice_id"] == ""
    assert norm["name"] == ""
    assert norm["gender"] == ""
    assert norm["marathi_verified"] is False
    assert norm["hindi_verified"] is False


def test_normalize_description_none():
    raw = {"description": None}
    norm = vl.normalize(raw)
    assert norm["description"] == ""


def test_normalize_marathi_hindi_from_various_codes():
    # language codes
    raw1 = {"verified_languages": [{"language": "mr"}, {"language": "hi"}]}
    assert vl.normalize(raw1)["marathi_verified"] is True
    assert vl.normalize(raw1)["hindi_verified"] is True

    # full names
    raw2 = {"verified_languages": [{"language": "Marathi"}, {"language": "Hindi"}]}
    assert vl.normalize(raw2)["marathi_verified"] is True
    assert vl.normalize(raw2)["hindi_verified"] is True

    # locale
    raw3 = {"verified_languages": [{"locale": "mr-IN"}, {"locale": "hi-IN"}]}
    assert vl.normalize(raw3)["marathi_verified"] is True
    assert vl.normalize(raw3)["hindi_verified"] is True

    # absent
    raw4 = {"verified_languages": [{"language": "en"}]}
    assert vl.normalize(raw4)["marathi_verified"] is False
    assert vl.normalize(raw4)["hindi_verified"] is False


# ---------- build_library tests ----------

def test_build_library_cast_keeps_key_and_assigned():
    raw = [{"voice_id": "cast1", "name": "Narrator", "labels": {"gender": "male"}}]
    cast = {"narrator": "cast1"}
    lib = vl.build_library(raw, cast)
    assert len(lib["voices"]) == 1
    v = lib["voices"][0]
    assert v["voice_key"] == "narrator"
    assert v["assigned_to"] == ["narrator"]
    assert v["status"] == "ASSIGNED"


def test_build_library_non_cast_gets_slug():
    raw = [{"voice_id": "v2", "name": "Extra Voice", "labels": {}}]
    cast = {"narrator": "cast1"}
    lib = vl.build_library(raw, cast)
    # Two voices: cast (missing) + extra
    assert len(lib["voices"]) == 2
    extra = next(v for v in lib["voices"] if v["voice_id"] == "v2")
    assert extra["voice_key"] == "extra_voice"
    assert extra["assigned_to"] == []
    assert extra["status"] == "AVAILABLE"


def test_build_library_same_name_distinct_keys():
    raw = [
        {"voice_id": "v3", "name": "Duplicate", "labels": {}},
        {"voice_id": "v4", "name": "Duplicate", "labels": {}},
    ]
    cast = {}
    lib = vl.build_library(raw, cast)
    keys = [v["voice_key"] for v in lib["voices"]]
    assert keys[0] == "duplicate"
    assert keys[1] == "duplicate_v4"  # first 4 of v4


def test_build_library_missing_cast_kept_as_missing():
    raw = [{"voice_id": "other", "name": "Other"}]
    cast = {"narrator": "missing_id", "gajanan": "missing_id2"}
    lib = vl.build_library(raw, cast)
    missing = [v for v in lib["voices"] if v["status"] == "MISSING_FROM_ACCOUNT"]
    assert len(missing) == 2
    for v in missing:
        assert v["name"] == v["voice_key"]
        assert v["description"] == ""
        assert v["marathi_verified"] is False
        assert v["hindi_verified"] is False


def test_build_library_duplicates_collapsed():
    raw = [
        {"voice_id": "dup", "name": "First"},
        {"voice_id": "dup", "name": "Second"},  # duplicate id
    ]
    cast = {}
    lib = vl.build_library(raw, cast)
    assert len(lib["voices"]) == 1
    assert lib["voices"][0]["name"] == "First"


def test_build_library_sorted_by_voice_key():
    raw = [
        {"voice_id": "b", "name": "Beta"},
        {"voice_id": "a", "name": "Alpha"},
    ]
    cast = {}
    lib = vl.build_library(raw, cast)
    keys = [v["voice_key"] for v in lib["voices"]]
    assert keys == ["alpha", "beta"]


def test_build_library_no_key_in_output():
    raw = [{"voice_id": "v1", "name": "Test"}]
    cast = {}
    lib = vl.build_library(raw, cast)
    json_str = json.dumps(lib)
    # The fake key "test_key" should not appear anywhere
    assert "test_key" not in json_str


# ---------- write_library tests ----------

def test_write_library_refuses_overwrite(tmp_path: Path):
    path = tmp_path / "lib.json"
    path.write_text("{}")
    with pytest.raises(FileExistsError):
        vl.write_library(path, {"version": 1}, overwrite=False)


def test_write_library_overwrite_replaces(tmp_path: Path):
    path = tmp_path / "lib.json"
    path.write_text("{}")
    vl.write_library(path, {"version": 2}, overwrite=True)
    assert json.loads(path.read_text())["version"] == 2


def test_write_library_atomic_no_tmp_left(tmp_path: Path):
    path = tmp_path / "lib.json"
    vl.write_library(path, {"version": 1})
    # No .tmp file should remain
    tmp_files = list(tmp_path.glob("*.tmp"))
    assert len(tmp_files) == 0


def test_write_library_utf8_devanagari_preserved(tmp_path: Path):
    path = tmp_path / "lib.json"
    lib = {"voices": [{"name": "नरेटर", "description": "हिंदी आवाज़"}]}
    vl.write_library(path, lib)
    content = path.read_text(encoding="utf-8")
    assert "नरेटर" in content
    assert "हिंदी आवाज़" in content


# ---------- main tests ----------

def test_main_dry_run_prints_summary_no_write(tmp_path: Path, capsys):
    # Prepare fake cast file
    cast_dir = tmp_path / "canon" / "audio"
    cast_dir.mkdir(parents=True)
    cast_file = cast_dir / "A1_eleven_voices.json"
    cast_file.write_text(json.dumps({"mr": {"narrator": "cast1"}}))

    # Prepare fake HTTP
    def fake_http(url: str, headers: dict) -> tuple[int, bytes]:
        return 200, b'{"voices": [{"voice_id": "cast1", "name": "Narrator", "labels": {"gender": "male", "age": "middle"}, "verified_languages": [{"language": "mr"}]}]}'

    # Monkeypatch module hooks
    vl._http = fake_http
    vl._env = {"ELEVENLABS_API_KEY": "test_key"}

    # Run main with dry-run, using tmp paths
    out_file = tmp_path / "canon" / "series" / "voices.json"
    argv = [
        "--cast", str(cast_file),
        "--out", str(out_file),
        "--dry-run",
    ]
    ret = vl.main(argv)
    assert ret == 0

    # Check output
    captured = capsys.readouterr()
    assert "Voices: 1" in captured.out
    assert "narrator | Narrator | male | middle | True | False | ASSIGNED" in captured.out
    # No description printed
    assert "description" not in captured.out.lower()
    # No key printed
    assert "test_key" not in captured.out
    # File not written
    assert not out_file.exists()

    # Cleanup hooks
    vl._http = None
    vl._env = None


def test_main_real_run_writes_file(tmp_path: Path):
    cast_dir = tmp_path / "canon" / "audio"
    cast_dir.mkdir(parents=True)
    cast_file = cast_dir / "A1_eleven_voices.json"
    cast_file.write_text(json.dumps({"mr": {"narrator": "cast1"}}))

    def fake_http(url: str, headers: dict) -> tuple[int, bytes]:
        return 200, b'{"voices": [{"voice_id": "cast1", "name": "Narrator", "labels": {"gender": "female"}}]}'

    vl._http = fake_http
    vl._env = {"ELEVENLABS_API_KEY": "test_key"}

    out_file = tmp_path / "canon" / "series" / "voices.json"
    argv = [
        "--cast", str(cast_file),
        "--out", str(out_file),
        "--overwrite",
    ]
    ret = vl.main(argv)
    assert ret == 0
    assert out_file.exists()
    lib = json.loads(out_file.read_text())
    assert lib["version"] == 1
    assert len(lib["voices"]) == 1

    vl._http = None
    vl._env = None
