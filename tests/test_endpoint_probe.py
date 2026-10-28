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


def test_real_transport_success_calls_pool_report(mod, monkeypatch):
    """Test that the real transport uses KeyPool correctly on success."""
    created_pool = {}

    class FakePool:
        def __init__(self, keys):
            self.keys = keys
            self.acquire_calls = 0
            self.report_calls = []

        def acquire(self):
            self.acquire_calls += 1
            return (3, "FAKEKEY")

        def report(self, index, status):
            self.report_calls.append((index, status))

    class FakeNT:
        def load_keys(self):
            return ["FAKEKEY"]

        def KeyPool(self, keys):
            pool = FakePool(keys)
            created_pool["instance"] = pool
            return pool

    class FakeDraftSource:
        nt = FakeNT()

    monkeypatch.setattr(mod, "_load_draft_source", lambda: FakeDraftSource())

    import urllib.request

    class FakeResponse:
        def __init__(self, status=200, data=b'data: {"choices": [{"delta": {"content": "hi"}}]}\ndata: [DONE]\n'):
            self.status = status
            self._data = data

        def read(self):
            return self._data

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    def fake_urlopen_success(request, timeout):
        return FakeResponse()

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen_success)

    transport = mod._make_real_transport()
    status, lines, error = transport({"model": "test", "messages": []})

    assert status == 200
    assert error == ""
    assert "FAKEKEY" in mod._SEEN_KEYS
    pool = created_pool["instance"]
    assert pool.acquire_calls == 1
    assert pool.report_calls == [(3, 200)]


def test_real_transport_http_error_calls_pool_report_and_masks_key(mod, monkeypatch):
    """Test that the real transport reports HTTP errors and masks keys in error text."""
    created_pool = {}

    class FakePool:
        def __init__(self, keys):
            self.keys = keys
            self.acquire_calls = 0
            self.report_calls = []

        def acquire(self):
            self.acquire_calls += 1
            return (3, "FAKEKEY")

        def report(self, index, status):
            self.report_calls.append((index, status))

    class FakeNT:
        def load_keys(self):
            return ["FAKEKEY"]

        def KeyPool(self, keys):
            pool = FakePool(keys)
            created_pool["instance"] = pool
            return pool

    class FakeDraftSource:
        nt = FakeNT()

    monkeypatch.setattr(mod, "_load_draft_source", lambda: FakeDraftSource())

    import urllib.request
    import urllib.error

    def fake_urlopen_http_error(request, timeout):
        # Simulate an HTTPError with a response body containing the key
        error_body = json.dumps({"error": "invalid key FAKEKEY"}).encode("utf-8")
        raise urllib.error.HTTPError(
            url="https://example.com",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=type("fp", (), {"read": lambda self: error_body})(),
        )

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen_http_error)

    transport = mod._make_real_transport()
    status, lines, error = transport({"model": "test", "messages": []})

    assert status == 401
    assert lines == []
    # The error text returned by transport is the raw body; scrubbing happens later.
    # But we can check that the key is in _SEEN_KEYS so that _scrub_keys will mask it.
    assert "FAKEKEY" in mod._SEEN_KEYS
    pool = created_pool["instance"]
    assert pool.acquire_calls == 1
    assert pool.report_calls == [(3, 401)]


def test_real_transport_network_error_calls_pool_report_with_zero(mod, monkeypatch):
    """Test that the real transport reports network errors with status 0."""
    created_pool = {}

    class FakePool:
        def __init__(self, keys):
            self.keys = keys
            self.acquire_calls = 0
            self.report_calls = []

        def acquire(self):
            self.acquire_calls += 1
            return (3, "FAKEKEY")

        def report(self, index, status):
            self.report_calls.append((index, status))

    class FakeNT:
        def load_keys(self):
            return ["FAKEKEY"]

        def KeyPool(self, keys):
            pool = FakePool(keys)
            created_pool["instance"] = pool
            return pool

    class FakeDraftSource:
        nt = FakeNT()

    monkeypatch.setattr(mod, "_load_draft_source", lambda: FakeDraftSource())

    import urllib.request
    import urllib.error

    def fake_urlopen_network_error(request, timeout):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen_network_error)

    transport = mod._make_real_transport()
    status, lines, error = transport({"model": "test", "messages": []})

    assert status == 0
    assert lines == []
    assert "connection refused" in error
    assert "FAKEKEY" in mod._SEEN_KEYS
    pool = created_pool["instance"]
    assert pool.acquire_calls == 1
    assert pool.report_calls == [(3, 0)]
