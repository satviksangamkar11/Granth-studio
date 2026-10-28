from __future__ import annotations

import jsonschema
from jsonschema import Draft202012Validator

SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "stage1_voice_cast",
    "type": "object",
    "additionalProperties": False,
    "required": ["adhyay", "cast"],
    "properties": {
        "adhyay": {
            "type": "integer",
            "minimum": 1,
            "maximum": 21
        },
        "cast": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["character_id", "voice_key", "voice_id", "gender", "status"],
                "properties": {
                    "character_id": {"type": "string"},
                    "voice_key": {"type": "string"},
                    "voice_id": {"type": "string", "minLength": 10, "maxLength": 40},
                    "gender": {"type": "string", "enum": ["male", "female"]},
                    "status": {"type": "string", "enum": ["RECURRING", "NEW_PROPOSED"]},
                    "reason": {"type": "string", "minLength": 1}
                },
                "if": {
                    "properties": {"status": {"const": "NEW_PROPOSED"}}
                },
                "then": {
                    "required": ["reason"]
                }
            }
        }
    }
}

_validator = Draft202012Validator(SCHEMA)


def schema_errors(doc) -> list[str]:
    errors = []
    for err in _validator.iter_errors(doc):
        path = "/".join(str(p) for p in err.path) if err.path else "doc"
        errors.append(f"voices {path}: {err.message}")
    return errors


def _validate_impl(adhyay: int, doc: dict, docs: dict, ctx: dict) -> list[str]:
    messages = []

    # Adhyay check
    doc_adhyay = doc.get("adhyay")
    if doc_adhyay != adhyay:
        messages.append(f"voices adhyay {doc_adhyay} does not match {adhyay}")

    # Convert ctx lists/sets to sets
    speaking_characters = set(ctx.get("speaking_characters", []))
    saved_voices = ctx.get("saved_voices", {})

    # Handle cast safely - validate structure
    cast_raw = doc.get("cast")
    if not isinstance(cast_raw, list):
        messages.append("cast: must be a list")
        cast = []
    else:
        cast = []
        for i, entry in enumerate(cast_raw):
            if not isinstance(entry, dict):
                messages.append(f"cast[{i}]: must be an object")
                continue
            # Check required fields
            for field in ["character_id", "voice_key", "voice_id", "gender", "status"]:
                if field not in entry:
                    messages.append(f"cast[{i}].{field}: required field missing")
            # Check types
            if "character_id" in entry and not isinstance(entry["character_id"], str):
                messages.append(f"cast[{i}].character_id: must be string")
            if "voice_key" in entry and not isinstance(entry["voice_key"], str):
                messages.append(f"cast[{i}].voice_key: must be string")
            if "voice_id" in entry and not isinstance(entry["voice_id"], str):
                messages.append(f"cast[{i}].voice_id: must be string")
            if "gender" in entry and not isinstance(entry["gender"], str):
                messages.append(f"cast[{i}].gender: must be string")
            if "status" in entry and not isinstance(entry["status"], str):
                messages.append(f"cast[{i}].status: must be string")
            # Only add to cast if it has all required fields with correct types
            if (isinstance(entry.get("character_id"), str) and
                isinstance(entry.get("voice_key"), str) and
                isinstance(entry.get("voice_id"), str) and
                isinstance(entry.get("gender"), str) and
                isinstance(entry.get("status"), str)):
                cast.append(entry)

    # Build lookup: character_id -> list of entries
    char_entries = {}
    for entry in cast:
        cid = entry.get("character_id")
        if not isinstance(cid, str):
            continue
        if cid not in char_entries:
            char_entries[cid] = []
        char_entries[cid].append(entry)

    # Rule: every speaking_character has exactly one cast entry
    for char in speaking_characters:
        entries = char_entries.get(char, [])
        if len(entries) == 0:
            messages.append(f"{char}: no voice assigned")
        elif len(entries) > 1:
            messages.append(f"{char}: listed more than once")

    # Rule: a character already RECURRING must not be listed twice (any status combination)
    for char, entries in char_entries.items():
        if len(entries) > 1 and any(e.get("status") == "RECURRING" for e in entries):
            messages.append(f"{char}: recurring character listed twice")

    # Rule: voice_key must be in saved_voices and voice_id must match
    for entry in cast:
        char = entry.get("character_id")
        if not isinstance(char, str):
            continue
        vkey = entry.get("voice_key")
        vid = entry.get("voice_id")
        if not isinstance(vkey, str) or vkey not in saved_voices:
            messages.append(f"{char}: voice not in the saved cast")
        elif saved_voices[vkey] != vid:
            messages.append(f"{char}: voice not in the saved cast")

    # Rule: two characters must not share a voice_key unless one is the narrator
    voice_key_to_chars = {}
    for entry in cast:
        vkey = entry.get("voice_key")
        char = entry.get("character_id")
        if not isinstance(vkey, str) or not isinstance(char, str):
            continue
        if vkey not in voice_key_to_chars:
            voice_key_to_chars[vkey] = set()
        voice_key_to_chars[vkey].add(char)

    for vkey, chars in voice_key_to_chars.items():
        # Get unique non-narrator characters sharing this key
        non_narrator_chars = [c for c in chars if c != "narrator"]
        if len(non_narrator_chars) > 1:
            # Multiple different non-narrator characters share this key - error for each
            for char in non_narrator_chars:
                messages.append(f"{char}: voice key shared with another character")

    return messages


def validate(adhyay: int, doc: dict, docs: dict, ctx: dict) -> list[str]:
    try:
        if not isinstance(doc, dict):
            return ["voices doc: document must be an object"]
        return _validate_impl(adhyay, doc, docs, ctx)
    except (TypeError, AttributeError, KeyError, ValueError, IndexError):
        return ["voices: malformed structure"]
