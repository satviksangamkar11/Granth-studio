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
                    "status": {"type": "string", "enum": ["RECURRING", "NEW_PROPOSED"]}
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


def validate(adhyay: int, doc: dict, docs: dict, ctx: dict) -> list[str]:
    messages = []

    # Adhyay check
    doc_adhyay = doc.get("adhyay")
    if doc_adhyay != adhyay:
        messages.append(f"voices adhyay {doc_adhyay} does not match {adhyay}")

    # Convert ctx lists/sets to sets
    speaking_characters = set(ctx.get("speaking_characters", []))
    saved_voices = ctx.get("saved_voices", {})

    cast = doc.get("cast", [])

    # Build lookup: character_id -> list of entries
    char_entries = {}
    for entry in cast:
        cid = entry.get("character_id")
        if cid not in char_entries:
            char_entries[cid] = []
        char_entries[cid].append(entry)

    # Rule: every speaking_character has exactly one cast entry
    for char in speaking_characters:
        entries = char_entries.get(char, [])
        if len(entries) == 0:
            messages.append(f"{char}: no voice assigned")
        elif len(entries) > 1:
            # Check if any is RECURRING - but the rule says "a character already RECURRING must not be listed twice"
            # This means if a character has multiple entries and any is RECURRING, it's an error
            for e in entries:
                if e.get("status") == "RECURRING":
                    messages.append(f"{char}: recurring character listed twice")
                    break

    # Rule: voice_key must be in saved_voices and voice_id must match
    for entry in cast:
        char = entry.get("character_id")
        vkey = entry.get("voice_key")
        vid = entry.get("voice_id")
        if vkey not in saved_voices:
            messages.append(f"{char}: voice not in the saved cast")
        elif saved_voices[vkey] != vid:
            messages.append(f"{char}: voice not in the saved cast")

    # Rule: two characters must not share a voice_key unless one is the narrator
    voice_key_to_chars = {}
    for entry in cast:
        vkey = entry.get("voice_key")
        char = entry.get("character_id")
        if vkey not in voice_key_to_chars:
            voice_key_to_chars[vkey] = []
        voice_key_to_chars[vkey].append(char)

    for vkey, chars in voice_key_to_chars.items():
        if len(chars) > 1:
            # Check if one is narrator
            if "narrator" not in chars:
                # Report for each character sharing the key
                for char in chars:
                    messages.append(f"{char}: voice key shared with another character")

    return messages
