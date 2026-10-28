# FIX CALL: return BOTH files in full: `scripts/pipeline/endpoint_probe.py` and `tests/test_endpoint_probe.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
......F.....                                                             [100%]
================================== FAILURES ===================================
________________ test_probe_once_truncates_error_and_masks_key ________________
tests\test_endpoint_probe.py:173: in test_probe_once_truncates_error_and_masks_key
    assert fake_key not in row["error"]
E   AssertionError: assert '***' not in 'bad key ***...sum lorem ip'
E     
E     '***' is contained here:
E       bad key *** lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ip
=========================== short test summary info ===========================
FAILED tests/test_endpoint_probe.py::test_probe_once_truncates_error_and_masks_key
1 failed, 11 passed in 0.24s

```

## SPEC
# Spec: write TWO files: `scripts/pipeline/endpoint_probe.py` and `tests/test_endpoint_probe.py`.
Purpose (owner 2026-10-28: "set the strength and thinking at mid or high"): find out which request fields the NVIDIA endpoint ACCEPTS to set the reasoning strength / thinking of the coder models, WITHOUT changing any existing code. The tool sends small test chats with different extra fields and reports what happened. It is a free endpoint; keys are loaded the same way as `scripts/source/nemotron_code.py` does it (import `draft_source.py` by path, use `ds.nt.load_keys()` and `ds.nt.KeyPool`); a key is NEVER printed, logged, written or put in an exception.
Style: `from __future__ import annotations`; standard library plus the existing `draft_source` loaded by path; no print except in `main()`; nothing at import time; tests are synthetic with an injected fake transport (no network, no real key). Tests load the module by path with importlib (`ROOT = Path(__file__).resolve().parents[1]`).

## API
- `VARIANTS`: list of dicts {"name": str, "extra": dict} merged into the JSON request body. Include exactly: baseline `{}`; `{"reasoning_effort": "low"}`; `{"reasoning_effort": "medium"}`; `{"reasoning_effort": "high"}`; `{"chat_template_kwargs": {"enable_thinking": True}}`; `{"chat_template_kwargs": {"enable_thinking": False}}`; `{"chat_template_kwargs": {"enable_thinking": True, "reasoning_effort": "high"}}`; `{"thinking": {"type": "enabled"}}`; `{"thinking": {"type": "disabled"}}`.
- `build_body(model, prompt, max_tokens, extra) -> dict`: {"model", "messages": [{"role": "user", "content": prompt}], "temperature": 0.2, "max_tokens": max_tokens, "stream": True} updated with `extra` (the key `model`, `messages`, `stream` cannot be overridden by `extra`: ignore those keys).
- `parse_stream(lines) -> dict`: parse server-sent-event lines ("data: {...}" and "data: [DONE]") of a streamed chat reply; return {"content": str (concatenated delta.content), "reasoning": str (concatenated delta.reasoning_content or delta.reasoning), "completion_tokens": int | None (from a usage object if present), "finish": str | None}. Ignore blank lines and malformed JSON lines.
- `probe_once(model, variant, prompt, max_tokens, transport) -> dict`: `transport(body: dict) -> (status: int, lines: list[str], error_text: str)` is injectable (the real one uses a key from the pool, POSTs to `https://integrate.api.nvidia.com/v1/chat/completions` with a 300 s timeout and reads the stream; on a non-200 status it returns the response body text as error_text). Return {"model", "variant": name, "status": int, "accepted": bool (status == 200), "wall_s": float, "content_chars": int, "reasoning_chars": int, "completion_tokens": int | None, "finish": str | None, "error": first 200 chars of error_text with any key-like string removed (replace every occurrence of the key by "[key]") or ""}.
- `run_probe(models, prompt, max_tokens, transport) -> list[dict]`: every model x every variant, sequentially, one probe_once each (catching any exception into a row with accepted False and the exception class name as error).
- `format_table(rows) -> str`: plain text table, columns model | variant | status | accepted | seconds | reasoning_chars | completion_tokens | finish | error(first 60 chars); one line per row.
- `main(argv=None) -> int`: CLI `--models` (comma separated, default `z-ai/glm-5.3-flash,z-ai/glm-5.3`), `--prompt` (default "What is 17*23? Think carefully, then answer with just the number."), `--max-tokens` (default 1500), `--out PATH` (optional JSON file of the rows; refuses to overwrite an existing file). Uses the real transport, prints `format_table(rows)` only. Never prints keys. Returns 0.

## Tests to write (each isolated, adversarial)
build_body: extra merged; protected keys ignored; stream True. parse_stream: content and reasoning_content and reasoning concatenated across chunks; usage tokens; finish reason; blank/malformed lines ignored; [DONE] ignored. probe_once with a fake transport: 200 with content+reasoning -> accepted True and counts; 400 with error text -> accepted False and error text truncated to 200 chars; the key string (give the fake transport a fake key it echoes in the error) is replaced by "[key]". run_probe: iterates models x len(VARIANTS) rows in order; a transport that raises produces a row with accepted False and the exception class name. VARIANTS contains exactly the nine names/extras above. format_table: one header plus one line per row, error truncated to 60 chars. main: with a monkeypatched transport and `--out` in tmp_path writes JSON rows and refuses to overwrite.

Reply with only two FILE blocks:
FILE: scripts/pipeline/endpoint_probe.py
FILE: tests/test_endpoint_probe.py


## CURRENT MODULE scripts/pipeline/endpoint_probe.py
```python
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


def _pool_key(pool) -> str:
    """Pull one key from ds.nt.KeyPool without ever exposing it."""
    for method_name in ("get", "get_key", "next", "next_key", "acquire", "pick"):
        method = getattr(pool, method_name, None)
        if not callable(method):
            continue
        try:
            key = method()
        except TypeError:
            continue
        if isinstance(key, str) and key:
            return key
    try:
        items = iter(pool)
    except TypeError:
        items = None
    if items is not None:
        for key in items:
            if isinstance(key, str) and key:
                return key
    raise RuntimeError("KeyPool provided no usable key")


def _make_real_transport():
    """Build the real HTTP transport using a key from the pool."""
    draft_source = _load_draft_source()
    draft_source.nt.load_keys()
    try:
        pool = draft_source.nt.KeyPool()
    except TypeError:
        pool = draft_source.nt.KeyPool(draft_source.nt.load_keys())

    def transport(body: dict) -> tuple[int, list[str], str]:
        key = _pool_key(pool)
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
            return int(exc.code), [], body_text
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

```

## CURRENT TESTS tests/test_endpoint_probe.py
```python
"""Synthetic, offline tests for scripts/pipeline/endpoint_probe.py.

Every test injects a fake transport; no network, no real key, and no files
written outside tmp_path.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "pipeline" / "endpoint_probe.py"

EXPECTED_VARIANTS = {
    "baseline": {},
    "reasoning_effort=low": {"reasoning_effort": "low"},
    "reasoning_effort=medium": {"reasoning_effort": "medium"},
    "reasoning_effort=high": {"reasoning_effort": "high"},
    "enable_thinking=true": {"chat_template_kwargs": {"enable_thinking": True}},
    "enable_thinking=false": {"chat_template_kwargs": {"enable_thinking": False}},
    "enable_thinking+effort_high": {
        "chat_template_kwargs": {"enable_thinking": True, "reasoning_effort": "high"}
    },
    "thinking=enabled": {"thinking": {"type": "enabled"}},
    "thinking=disabled": {"thinking": {"type": "disabled"}},
}


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "endpoint_probe_under_test", MODULE_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def mod():
    return _load_module()


def _sse(*events):
    return ["data: " + json.dumps(event) for event in events] + ["data: [DONE]"]


def test_build_body_merges_extra_over_defaults(mod):
    body = mod.build_body(
        "z-ai/glm-5.3",
        "17*23?",
        1500,
        {"reasoning_effort": "high", "temperature": 0.7, "top_p": 0.9},
    )
    assert body == {
        "model": "z-ai/glm-5.3",
        "messages": [{"role": "user", "content": "17*23?"}],
        "temperature": 0.7,
        "max_tokens": 1500,
        "stream": True,
        "reasoning_effort": "high",
        "top_p": 0.9,
    }


def test_build_body_protected_keys_cannot_be_overridden(mod):
    body = mod.build_body(
        "z-ai/glm-5.3",
        "prompt",
        10,
        {
            "model": "other/model",
            "messages": [{"role": "user", "content": "hijacked"}],
            "stream": False,
            "reasoning_effort": "low",
        },
    )
    assert body["model"] == "z-ai/glm-5.3"
    assert body["messages"] == [{"role": "user", "content": "prompt"}]
    assert body["stream"] is True
    assert body["reasoning_effort"] == "low"


def test_build_body_empty_extra_keeps_defaults(mod):
    body = mod.build_body("m", "p", 5, {})
    assert body["temperature"] == 0.2
    assert body["stream"] is True
    assert set(body) == {"model", "messages", "temperature", "max_tokens", "stream"}


def test_parse_stream_concatenates_content_and_both_reasoning_fields(mod):
    lines = _sse(
        {"choices": [{"delta": {"role": "assistant", "content": "Hel"}}]},
        {"choices": [{"delta": {"content": "lo ", "reasoning_content": "think "}}]},
        {"choices": [{"delta": {"content": "world", "reasoning": "more "}}]},
        {
            "choices": [{"delta": {}, "finish_reason": "stop"}],
            "usage": {"completion_tokens": 42},
        },
    )
    parsed = mod.parse_stream(lines)
    assert parsed["content"] == "Hello world"
    assert parsed["reasoning"] == "think more "
    assert parsed["completion_tokens"] == 42
    assert parsed["finish"] == "stop"


def test_parse_stream_ignores_blank_malformed_and_done(mod):
    good = json.dumps({"choices": [{"delta": {"content": "ok"}}]})
    lines = [
        "",
        "   ",
        ": keep-alive comment",
        "event: ping",
        "data:",
        "data: [DONE]",
        "data: not-json-at-all",
        "data: " + good,
        "data: [DONE]",
    ]
    parsed = mod.parse_stream(lines)
    assert parsed["content"] == "ok"
    assert parsed["reasoning"] == ""
    assert parsed["completion_tokens"] is None
    assert parsed["finish"] is None


def test_probe_once_accepts_200_and_counts_output(mod):
    lines = _sse(
        {"choices": [{"delta": {"reasoning_content": "thinking..."}}]},
        {
            "choices": [{"delta": {"content": "391"}}],
            "usage": {"completion_tokens": 7},
        },
    )
    seen_bodies = []

    def transport(body):
        seen_bodies.append(body)
        return 200, lines, ""

    row = mod.probe_once(
        "z-ai/glm-5.3", {"name": "baseline", "extra": {}}, "17*23?", 1500, transport
    )
    assert seen_bodies == [mod.build_body("z-ai/glm-5.3", "17*23?", 1500, {})]
    assert row["model"] == "z-ai/glm-5.3"
    assert row["variant"] == "baseline"
    assert row["status"] == 200
    assert row["accepted"] is True
    assert isinstance(row["wall_s"], float)
    assert row["wall_s"] >= 0.0
    assert row["content_chars"] == 3
    assert row["reasoning_chars"] == len("thinking...")
    assert row["completion_tokens"] == 7
    assert row["finish"] is None
    assert row["error"] == ""


def test_probe_once_truncates_error_and_masks_key(mod):
    fake_key = "***"
    error_text = "bad key " + fake_key + " " + "lorem ipsum " * 30

    def transport(body):
        return 400, [], error_text

    row = mod.probe_once("m", {"name": "v", "extra": {}}, "p", 10, transport)
    assert row["status"] == 400
    assert row["accepted"] is False
    assert fake_key not in row["error"]
    assert "[key]" in row["error"]
    assert len(row["error"]) == 200
    assert row["content_chars"] == 0
    assert row["reasoning_chars"] == 0
    assert row["completion_tokens"] is None
    assert row["finish"] is None


def test_run_probe_covers_models_x_variants_in_order(mod):
    bodies = []

    def transport(body):
        bodies.append(body)
        return 200, _sse({"choices": [{"delta": {"content": "ok"}}]}), ""

    models = ["z-ai/model-a", "z-ai/model-b"]
    rows = mod.run_probe(models, "p", 10, transport)
    assert len(rows) == len(models) * len(mod.VARIANTS)
    assert [row["model"] for row in rows] == (
        ["z-ai/model-a"] * len(mod.VARIANTS) + ["z-ai/model-b"] * len(mod.VARIANTS)
    )
    assert [row["variant"] for row in rows] == [v["name"] for v in mod.VARIANTS] * 2
    assert bodies == [
        mod.build_body(model, "p", 10, variant["extra"])
        for model in models
        for variant in mod.VARIANTS
    ]
    assert all(row["accepted"] is True for row in rows)


def test_run_probe_turns_transport_exception_into_failed_row(mod):
    def transport(body):
        raise ConnectionError("boom ***")

    rows = mod.run_probe(["m"], "p", 10, transport)
    assert len(rows) == len(mod.VARIANTS)
    for row in rows:
        assert row["accepted"] is False
        assert row["status"] == 0
        assert row["error"] == "ConnectionError"
    assert "***" not in json.dumps(rows)


def test_variants_exactly_nine_expected(mod):
    assert len(mod.VARIANTS) == 9
    assert [variant["name"] for variant in mod.VARIANTS] == list(EXPECTED_VARIANTS)
    for variant in mod.VARIANTS:
        assert variant["extra"] == EXPECTED_VARIANTS[variant["name"]]


def test_format_table_header_and_rows_with_truncated_error(mod):
    rows = [
        {
            "model": "z-ai/glm-5.3",
            "variant": "baseline",
            "status": 200,
            "accepted": True,
            "wall_s": 1.234,
            "content_chars": 3,
            "reasoning_chars": 11,
            "completion_tokens": 7,
            "finish": "stop",
            "error": "",
        },
        {
            "model": "z-ai/glm-5.3-flash",
            "variant": "reasoning_effort=low",
            "status": 400,
            "accepted": False,
            "wall_s": 0.1,
            "content_chars": 0,
            "reasoning_chars": 0,
            "completion_tokens": None,
            "finish": None,
            "error": "e" * 100,
        },
    ]
    table = mod.format_table(rows)
    lines = table.splitlines()
    assert len(lines) == 1 + len(rows)
    header_cells = [cell.strip() for cell in lines[0].split("|")]
    assert header_cells == [
        "model",
        "variant",
        "status",
        "accepted",
        "seconds",
        "reasoning_chars",
        "completion_tokens",
        "finish",
        "error",
    ]
    for line in lines[1:]:
        assert len(line.split("|")) == 9
    assert "1.23" in lines[1]
    assert "stop" in lines[1]
    assert "True" in lines[1]
    assert "False" in lines[2]
    assert "e" * 60 in lines[2]
    assert "e" * 61 not in lines[2]


def test_main_writes_json_then_refuses_overwrite(mod, tmp_path, monkeypatch, capsys):
    lines = _sse({"choices": [{"delta": {"content": "391"}}]})
    calls = []

    def fake_transport(body):
        calls.append(body)
        return 200, lines, ""

    monkeypatch.setattr(mod, "_make_real_transport", lambda: fake_transport)
    out = tmp_path / "rows.json"

    rc = mod.main(["--models", "test/model-a,test/model-b", "--out", str(out)])

    assert rc == 0
    assert out.exists()
    rows = json.loads(out.read_text(encoding="utf-8"))
    assert len(rows) == 2 * len(mod.VARIANTS)
    assert {row["model"] for row in rows} == {"test/model-a", "test/model-b"}
    assert all(row["accepted"] is True for row in rows)
    assert len(calls) == 2 * len(mod.VARIANTS)
    table_out = capsys.readouterr().out
    assert "baseline" in table_out
    assert "nvapi-" not in table_out

    with pytest.raises(FileExistsError):
        mod.main(["--models", "test/model-a", "--out", str(out)])
    assert len(calls) == 2 * len(mod.VARIANTS)

```
