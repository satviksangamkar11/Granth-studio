"""Endpoint probe: find out which request fields the NVIDIA chat endpoint
accepts to set the reasoning strength / thinking of the coder models.

The tool sends small test chats with different extra body fields (one probe
per model x variant) and reports what happened. It changes no existing code.

Keys are loaded the same way as scripts/source/nemotron_code.py does it
(draft_source.py loaded by path, then ds.nt.load_keys() and ds.nt.KeyPool()).
A key is never printed, logged, written or put in an exception: every error
string is scrubbed of key-like text before it is stored in a row.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

_ENDPOINT_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
_TIMEOUT_S = 300
_ERROR_MAX_CHARS = 200
_TABLE_ERROR_MAX_CHARS = 60
_PROTECTED_BODY_KEYS = ("model", "messages", "stream")

VARIANTS: list[dict] = [
    {"name": "baseline", "extra": {}},
    {"name": "reasoning_effort=low", "extra": {"reasoning_effort": "low"}},
    {"name": "reasoning_effort=medium", "extra": {"reasoning_effort": "medium"}},
    {"name": "reasoning_effort=high", "extra": {"reasoning_effort": "high"}},
    {
        "name": "enable_thinking=true",
        "extra": {"chat_template_kwargs": {"enable_thinking": True}},
    },
    {
        "name": "enable_thinking=false",
        "extra": {"chat_template_kwargs": {"enable_thinking": False}},
    },
    {
        "name": "enable_thinking+effort_high",
        "extra": {
            "chat_template_kwargs": {"enable_thinking": True, "reasoning_effort": "high"}
        },
    },
    {"name": "thinking=enabled", "extra": {"thinking": {"type": "enabled"}}},
    {"name": "thinking=disabled", "extra": {"thinking": {"type": "disabled"}}},
]

_TABLE_COLUMNS = (
    "model",
    "variant",
    "status",
    "accepted",
    "seconds",
    "reasoning_chars",
    "completion_tokens",
    "finish",
    "error",
)

# Keys actually used by the real transport are kept only in memory so that
# _scrub_keys can remove them from error text before it is stored anywhere.
_SEEN_KEYS: set[str] = set()

_BEARER_RE = re.compile(r"(?i)(\bbearer\s+)[A-Za-z0-9._\-]+")
_NVAPI_RE = re.compile(r"nvapi-[A-Za-z0-9._\-]+")
_LONG_TOKEN_RE = re.compile(r"\b[A-Za-z0-9][A-Za-z0-9_\-]{31,}\b")
_ASTERISK_RE = re.compile(r"\*{3,}")

_DRAFT_SOURCE = None


def _scrub_keys(text: str) -> str:
    """Return text with every key-like string replaced by "[key]"."""
    scrubbed = text
    for key in sorted(_SEEN_KEYS, key=len, reverse=True):
        if key:
            scrubbed = scrubbed.replace(key, "[key]")
    scrubbed = _BEARER_RE.sub(r"\g<1>[key]", scrubbed)
    scrubbed = _NVAPI_RE.sub("[key]", scrubbed)
    scrubbed = _LONG_TOKEN_RE.sub("[key]", scrubbed)
    scrubbed = _ASTERISK_RE.sub("[key]", scrubbed)
    return scrubbed


def build_body(model: str, prompt: str, max_tokens: int, extra: dict | None) -> dict:
    """Chat request body; `extra` is merged in but cannot override protected keys."""
    body: dict = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": max_tokens,
        "stream": True,
    }
    for key, value in (extra or {}).items():
        if key in _PROTECTED_BODY_KEYS:
            continue
        body[key] = value
    return body


def parse_stream(lines: list[str]) -> dict:
    """Parse SSE lines of a streamed chat reply.

    Ignores blank lines, non-data lines, malformed JSON lines and the final
    "data: [DONE]" sentinel.
    """
    content_parts: list[str] = []
    reasoning_parts: list[str] = []
    completion_tokens: int | None = None
    finish: str | None = None
    for line in lines:
        if not isinstance(line, str):
            continue
        stripped = line.strip()
        if not stripped.startswith("data:"):
            continue
        payload = stripped[len("data:"):].strip()
        if not payload or payload == "[DONE]":
            continue
        try:
            event = json.loads(payload)
        except ValueError:
            continue
        if not isinstance(event, dict):
            continue
        choices = event.get("choices")
        if isinstance(choices, list):
            for choice in choices:
                if not isinstance(choice, dict):
                    continue
                delta = choice.get("delta")
                if isinstance(delta, dict):
                    piece = delta.get("content")
                    if isinstance(piece, str):
                        content_parts.append(piece)
                    piece = delta.get("reasoning_content")
                    if not isinstance(piece, str):
                        piece = delta.get("reasoning")
                    if isinstance(piece, str):
                        reasoning_parts.append(piece)
                reason = choice.get("finish_reason")
                if isinstance(reason, str):
                    finish = reason
        usage = event.get("usage")
        if isinstance(usage, dict):
            value = usage.get("completion_tokens")
            if isinstance(value, int) and not isinstance(value, bool):
                completion_tokens = value
    return {
        "content": "".join(content_parts),
        "reasoning": "".join(reasoning_parts),
        "completion_tokens": completion_tokens,
        "finish": finish,
    }


def probe_once(model: str, variant: dict, prompt: str, max_tokens: int, transport) -> dict:
    """Run one variant against one model through the injectable transport."""
    body = build_body(model, prompt, max_tokens, variant.get("extra") or {})
    started = time.perf_counter()
    status, lines, error_text = transport(body)
    wall_s = time.perf_counter() - started
    parsed = parse_stream(lines)
    status_code = int(status)
    error = _scrub_keys(error_text)[:_ERROR_MAX_CHARS] if error_text else ""
    return {
        "model": model,
        "variant": variant.get("name", ""),
        "status": status_code,
        "accepted": status_code == 200,
        "wall_s": wall_s,
        "content_chars": len(parsed["content"]),
        "reasoning_chars": len(parsed["reasoning"]),
        "completion_tokens": parsed["completion_tokens"],
        "finish": parsed["finish"],
        "error": error,
    }


def run_probe(models: list[str], prompt: str, max_tokens: int, transport) -> list[dict]:
    """Probe every model x every variant sequentially; failures become rows."""
    rows: list[dict] = []
    for model in models:
        for variant in VARIANTS:
            try:
                rows.append(probe_once(model, variant, prompt, max_tokens, transport))
            except Exception as exc:
                rows.append(
                    {
                        "model": model,
                        "variant": variant.get("name", ""),
                        "status": 0,
                        "accepted": False,
                        "wall_s": 0.0,
                        "content_chars": 0,
                        "reasoning_chars": 0,
                        "completion_tokens": None,
                        "finish": None,
                        "error": type(exc).__name__,
                    }
                )
    return rows


def _row_cells(row: dict) -> list[str]:
    completion_tokens = row.get("completion_tokens")
    finish = row.get("finish")
    return [
        str(row.get("model", "")),
        str(row.get("variant", "")),
        str(row.get("status", "")),
        str(bool(row.get("accepted", False))),
        "{:.2f}".format(float(row.get("wall_s") or 0.0)),
        str(row.get("reasoning_chars", 0)),
        "" if completion_tokens is None else str(completion_tokens),
        "" if finish is None else str(finish),
        str(row.get("error", "") or "")[:_TABLE_ERROR_MAX_CHARS],
    ]


def format_table(rows: list[dict]) -> str:
    """Plain text table, one header line plus one line per row."""
    table_rows = [_row_cells(row) for row in rows]
    widths = [len(column) for column in _TABLE_COLUMNS]
    for cells in table_rows:
        for index, cell in enumerate(cells):
            widths[index] = max(widths[index], len(cell))
    lines = [
        " | ".join(
            column.ljust(widths[index]) for index, column in enumerate(_TABLE_COLUMNS)
        )
    ]
    for cells in table_rows:
        lines.append(
            " | ".join(cell.ljust(widths[index]) for index, cell in enumerate(cells))
        )
    return "\n".join(lines)


def _load_draft_source():
    """Load the existing draft_source.py by path (same as nemotron_code.py)."""
    global _DRAFT_SOURCE
    if _DRAFT_SOURCE is not None:
        return _DRAFT_SOURCE
    here = Path(__file__).resolve()
    roots = list(here.parents)[:3]
    candidates: list[Path] = []
    for root in roots:
        candidates.append(root / "draft_source.py")
        candidates.append(root / "scripts" / "draft_source.py")
        candidates.append(root / "scripts" / "source" / "draft_source.py")
        candidates.append(root / "source" / "draft_source.py")
    checked: set[Path] = set()
    for candidate in candidates:
        if candidate in checked or not candidate.is_file():
            continue
        checked.add(candidate)
        spec = importlib.util.spec_from_file_location("draft_source", candidate)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        try:
            spec.loader.exec_module(module)
        except Exception:
            sys.modules.pop(spec.name, None)
            raise
        _DRAFT_SOURCE = module
        return module
    raise RuntimeError("draft_source.py not found; cannot load the NVIDIA key pool")


def _make_real_transport():
    """Build the real HTTP transport using a key from the pool."""
    draft_source = _load_draft_source()
    keys = draft_source.nt.load_keys()
    pool = draft_source.nt.KeyPool(keys)

    def transport(body: dict) -> tuple[int, list[str], str]:
        index, key = pool.acquire()
        if key:
            _SEEN_KEYS.add(key)
        request = urllib.request.Request(
            _ENDPOINT_URL,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
                "Authorization": "Bearer " + key,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=_TIMEOUT_S) as response:
                status = int(response.status)
                raw = response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            try:
                body_text = exc.read().decode("utf-8", errors="replace")
            except Exception:
                body_text = ""
            pool.report(index, exc.code)
            return int(exc.code), [], body_text
        except Exception as exc:
            pool.report(index, 0)
            return 0, [], str(exc)
        else:
            pool.report(index, status)
            return status, raw.splitlines(), ""

    return transport


def _parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="endpoint_probe",
        description=(
            "Probe which request fields the NVIDIA endpoint accepts to set "
            "reasoning strength / thinking of the coder models."
        ),
    )
    parser.add_argument(
        "--models",
        default="z-ai/glm-5.3-flash,z-ai/glm-5.3",
        help="comma separated model ids",
    )
    parser.add_argument(
        "--prompt",
        default="What is 17*23? Think carefully, then answer with just the number.",
    )
    parser.add_argument("--max-tokens", type=int, default=1500)
    parser.add_argument(
        "--out",
        default=None,
        help="optional JSON file for the rows; refuses to overwrite an existing file",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = _parse_args(argv)
    models = [model.strip() for model in args.models.split(",") if model.strip()]
    out_path = Path(args.out) if args.out else None
    if out_path is not None and out_path.exists():
        raise FileExistsError("refusing to overwrite existing file: {}".format(out_path))
    transport = _make_real_transport()
    rows = run_probe(models, args.prompt, args.max_tokens, transport)
    print(format_table(rows))
    if out_path is not None:
        out_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
