from __future__ import annotations

from typing import Any

from jsonschema import Draft202012Validator

SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "stage1_questions",
    "type": "object",
    "additionalProperties": False,
    "required": ["adhyay", "questions"],
    "properties": {
        "adhyay": {"type": "integer", "minimum": 1, "maximum": 21},
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["id", "text"],
                "properties": {
                    "id": {"type": "string", "pattern": "^Q[0-9]+$"},
                    "text": {"type": "string", "minLength": 1, "maxLength": 400},
                    "scene_id": {"type": "string", "pattern": "^S[0-9]{1,2}$"},
                },
            },
        },
    },
}

_validator = Draft202012Validator(SCHEMA)


def schema_errors(doc: Any) -> list[str]:
    errors: list[str] = []
    for err in _validator.iter_errors(doc):
        path = "/".join(str(p) for p in err.path) if err.path else "doc"
        errors.append(f"questions {path}: {err.message}")
    return errors


def validate(adhyay: int, doc: dict[str, Any], docs: dict[str, Any], ctx: dict[str, Any]) -> list[str]:
    messages: list[str] = []

    # adhyay check first
    doc_adhyay = doc.get("adhyay") if isinstance(doc, dict) else None
    if doc_adhyay != adhyay:
        messages.append(f"questions adhyay {doc_adhyay} does not match {adhyay}")

    questions = doc.get("questions", []) if isinstance(doc, dict) else []
    if not isinstance(questions, list):
        return messages

    # unique ids
    seen_ids: set[str] = set()
    for q in questions:
        if not isinstance(q, dict):
            continue
        qid = q.get("id")
        if not isinstance(qid, str):
            continue
        if qid in seen_ids:
            messages.append(f"{qid}: duplicate question id")
        seen_ids.add(qid)

    # scene exists if given
    scenes_doc = docs.get("scenes", {}) if isinstance(docs, dict) else {}
    if not isinstance(scenes_doc, dict):
        scenes_doc = {}
    raw_scenes = scenes_doc.get("scenes", [])
    if not isinstance(raw_scenes, list):
        raw_scenes = []

    scene_ids: set[str] = set()
    for sc in raw_scenes:
        if isinstance(sc, dict):
            sid = sc.get("scene_id")
            if isinstance(sid, str):
                scene_ids.add(sid)

    for q in questions:
        if not isinstance(q, dict):
            continue
        qid = q.get("id")
        scene_id = q.get("scene_id")
        if not isinstance(scene_id, str):
            continue
        if scene_id and scene_id not in scene_ids:
            messages.append(f"{qid}: scene_id '{scene_id}' does not exist")

    return messages
