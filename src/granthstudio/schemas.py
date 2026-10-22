"""JSON Schema validation for every document type the pipeline reads or writes."""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources
from typing import Any

import jsonschema

from .errors import SchemaError

KNOWN = (
    "project",
    "models",
    "quality_gates",
    "canon",
    "research",
    "source_receipt",
    "episode_manifest",
    "timeline",
    "benchmark_receipt",
    "task_receipt",
    "production_approval",
    "recovery_evidence",
)


@lru_cache(maxsize=None)
def _schema(name: str) -> dict[str, Any]:
    if name not in KNOWN:
        raise SchemaError(f"unknown schema {name!r}")
    text = (resources.files("granthstudio") / "schemas" / f"{name}.schema.json").read_text(encoding="utf-8")
    return json.loads(text)


def validate_document(name: str, document: Any) -> None:
    validator = jsonschema.Draft202012Validator(_schema(name))
    errors = sorted(validator.iter_errors(document), key=lambda e: [str(p) for p in e.absolute_path])
    if errors:
        parts = []
        for err in errors[:20]:
            location = "/".join(str(p) for p in err.absolute_path) or "<root>"
            parts.append(f"{location}: {err.message}")
        raise SchemaError(f"{name} schema violation: " + "; ".join(parts))
