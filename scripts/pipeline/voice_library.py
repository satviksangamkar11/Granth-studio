from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any, Callable, Optional

# Module-level hooks for tests to monkeypatch
_http: Optional[Callable[[str, dict], tuple[int, bytes]]] = None
_env: Optional[dict[str, str]] = None


def load_key(
    env: Optional[dict[str, str]] = None,
    secrets_dir: Path = Path("D:/aai work/secrets/elevenlabs"),
) -> str:
    """Load ElevenLabs API key from environment or secrets directory."""
    # Use provided env or the module-level hook or os.environ
    env_map = env if env is not None else (_env if _env is not None else os.environ)
    key = env_map.get("ELEVENLABS_API_KEY")
    if key:
        return key.strip()

    # Fallback to secrets directory
    if secrets_dir.is_dir():
        for entry in sorted(secrets_dir.iterdir()):
            if entry.is_file():
                try:
                    content = entry.read_text(encoding="utf-8").strip()
                    if content:
                        return content
                except OSError:
                    continue

    raise SystemExit("NOT_RUN: no ElevenLabs key found in env or secrets directory")


def fetch_voices(
    key: str,
    http: Optional[Callable[[str, dict], tuple[int, bytes]]] = None,
) -> list[dict]:
    """Fetch voices from ElevenLabs API."""
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": key, "Accept": "application/json"}

    # Use injected http, module hook, or default urllib
    caller = http if http is not None else (_http if _http is not None else _default_http)
    status, body = caller(url, headers)

    if status != 200:
        raise RuntimeError(f"ElevenLabs list voices failed: HTTP {status}")

    try:
        data = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        return []

    return data.get("voices", [])


def _default_http(url: str, headers: dict) -> tuple[int, bytes]:
    """Default HTTP GET using urllib with 60s timeout."""
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.status, resp.read()


def normalize(raw: dict) -> dict:
    """Normalize a raw voice dict to the library schema."""
    labels = raw.get("labels") or {}
    verified = raw.get("verified_languages") or []

    marathi_verified = False
    hindi_verified = False
    for entry in verified:
        lang = (entry.get("language") or "").lower()
        locale = (entry.get("locale") or "").lower()
        if lang.startswith("mr") or lang == "marathi" or locale.startswith("mr"):
            marathi_verified = True
        if lang.startswith("hi") or lang == "hindi" or locale.startswith("hi"):
            hindi_verified = True

    desc = raw.get("description")
    if desc is None:
        desc = ""

    return {
        "voice_id": str(raw.get("voice_id", "")),
        "name": str(raw.get("name", "")),
        "category": str(raw.get("category", "")),
        "gender": str(labels.get("gender", "")),
        "age": str(labels.get("age", "")),
        "accent": str(labels.get("accent", "")),
        "descriptive": str(labels.get("descriptive", "")),
        "use_case": str(labels.get("use_case", "")),
        "description": str(desc),
        "marathi_verified": marathi_verified,
        "hindi_verified": hindi_verified,
    }


def _slugify(name: str) -> str:
    """Create a slug from a name: lowercase, non-alphanumerics -> '_', strip underscores."""
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower())
    return slug.strip("_")


def build_library(
    raw_voices: list[dict],
    cast: dict[str, str],
    assignments: Optional[dict[str, list[str]]] = None,
    generated: str = "",
) -> dict:
    """Build the voice library from raw voices and cast mapping."""
    if assignments is None:
        assignments = {k: [k] for k in cast}

    # Map voice_id -> cast key (for quick lookup)
    cast_by_id = {v_id: k for k, v_id in cast.items()}

    # Normalize and deduplicate by voice_id
    seen_ids = set()
    normalized = []
    for raw in raw_voices:
        v_id = raw.get("voice_id")
        if not v_id:
            continue
        if v_id in seen_ids:
            continue
        seen_ids.add(v_id)
        norm = normalize(raw)
        norm["voice_id"] = v_id
        normalized.append(norm)

    # Build records
    records = []
    used_slugs = set()

    # First, process cast voices (they keep their cast key)
    for cast_key, cast_id in cast.items():
        # Find matching normalized voice
        match = next((n for n in normalized if n["voice_id"] == cast_id), None)
        if match:
            record = match.copy()
            record["voice_key"] = cast_key
            record["assigned_to"] = assignments.get(cast_key, [cast_key])
            record["status"] = "ASSIGNED"
            record["owner_note"] = ""
            records.append(record)
        else:
            # Missing from account: create minimal record
            record = {
                "voice_id": cast_id,
                "voice_key": cast_key,
                "name": cast_key,
                "category": "",
                "gender": "",
                "age": "",
                "accent": "",
                "descriptive": "",
                "use_case": "",
                "description": "",
                "marathi_verified": False,
                "hindi_verified": False,
                "assigned_to": assignments.get(cast_key, [cast_key]),
                "status": "MISSING_FROM_ACCOUNT",
                "owner_note": "",
            }
            records.append(record)

    # Then, process remaining normalized voices (non-cast)
    for norm in normalized:
        v_id = norm["voice_id"]
        if v_id in cast_by_id:
            continue  # already handled as cast

        base_slug = _slugify(norm["name"])
        slug = base_slug
        if slug in used_slugs or not slug:
            slug = f"{base_slug}_{v_id[:4]}" if base_slug else v_id[:4]
        # Ensure uniqueness
        counter = 1
        original_slug = slug
        while slug in used_slugs:
            slug = f"{original_slug}_{counter}"
            counter += 1
        used_slugs.add(slug)

        record = norm.copy()
        record["voice_key"] = slug
        record["assigned_to"] = []
        record["status"] = "AVAILABLE"
        record["owner_note"] = ""
        records.append(record)

    # Sort by voice_key
    records.sort(key=lambda r: r["voice_key"])

    return {
        "version": 1,
        "generated": generated or date.today().isoformat(),
        "source": "elevenlabs list voices",
        "voices": records,
    }


def write_library(path: Path, library: dict, overwrite: bool = False) -> None:
    """Write library to JSON file atomically."""
    path = Path(path)
    if path.exists() and not overwrite:
        raise FileExistsError(f"File exists: {path}")

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    try:
        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(library, f, indent=1, ensure_ascii=False, sort_keys=True)
        os.replace(tmp_path, path)
    finally:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass


def main(argv: Optional[list[str]] = None) -> int:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Build voice library from ElevenLabs")
    parser.add_argument(
        "--cast",
        type=Path,
        default=Path("canon/audio/A1_eleven_voices.json"),
        help="Path to cast mapping JSON (default: canon/audio/A1_eleven_voices.json)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("canon/series/voices.json"),
        help="Output path for voice library (default: canon/series/voices.json)",
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output")
    parser.add_argument("--dry-run", action="store_true", help="Build and print summary, do not write")
    args = parser.parse_args(argv)

    # Load cast mapping (mr section)
    cast_path = args.cast
    if not cast_path.is_absolute():
        # Resolve relative to repository root (parent of scripts/pipeline)
        root = Path(__file__).resolve().parents[2]
        cast_path = root / cast_path
    with cast_path.open("r", encoding="utf-8") as f:
        cast_data = json.load(f)
    cast = cast_data.get("mr", {})

    # Load key and fetch voices
    key = load_key()
    raw_voices = fetch_voices(key)

    # Build library
    library = build_library(raw_voices, cast, generated=date.today().isoformat())

    # Print summary (never print key)
    print(f"Voices: {len(library['voices'])}")
    for v in library["voices"]:
        print(
            f"{v['voice_key']} | {v['name']} | {v['gender']} | {v['age']} | "
            f"{v['marathi_verified']} | {v['hindi_verified']} | {v['status']}"
        )

    if not args.dry_run:
        write_library(args.out, library, overwrite=args.overwrite)

    return 0


if __name__ == "__main__":
    sys.exit(main())
