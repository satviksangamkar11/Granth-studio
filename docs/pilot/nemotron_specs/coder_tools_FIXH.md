# TASK: return ONLY ONE FILE: tests/test_coder_tools.py (complete). Reply with exactly one block `FILE: tests/test_coder_tools.py` then the python fenced. Your new tests are good but: (1) one compares floats exactly (`assert 0.30000000000000004 == 0.3`): use `pytest.approx` or round; (2) the module scripts/source/coder_run.py is being fixed in parallel so that receipts scrub every key passed in the `keys` argument of chat_stream (key strings of length >= 8 replaced by `[key]` in every string value of a receipt, nested dicts included): keep the no-key tests as they are (they will pass once the module is fixed); (3) check the other new tests by hand against the spec. Keep every other test.

## CURRENT tests/test_coder_tools.py (the version from the previous call)
```python
from __future__ import annotations

import sys
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import tempfile
import os
import json
import copy


def load_coder_run():
    root = Path(__file__).resolve().parents[1]
    cr_path = root / "scripts" / "source" / "coder_run.py"
    spec = importlib.util.spec_from_file_location("coder_run_tools_test", cr_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {cr_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_with_idle_timeout():
    cr = load_coder_run()
    cr.RECEIPTS.clear()

    # Fake ds with nt._OPENER that records calls
    class FakeOpener:
        def __init__(self):
            self.calls = []
            self.addheaders = [("User-Agent", "test")]

        def open(self, req, *args, **kwargs):
            self.calls.append((args, kwargs.copy()))
            return "response"

    fake_opener = FakeOpener()
    fake_ds = SimpleNamespace(nt=SimpleNamespace(_OPENER=fake_opener))

    # Default (env not set) -> 600
    wrapped = cr.with_idle_timeout(fake_ds)
    assert wrapped is fake_ds
    # Call the proxied opener
    fake_ds.nt._OPENER.open(object(), timeout=120)
    assert fake_opener.calls[-1][1]["timeout"] == 600

    # Explicit seconds argument wins
    fake_opener.calls.clear()
    cr.with_idle_timeout(fake_ds, seconds=45)
    fake_ds.nt._OPENER.open(object(), timeout=120)
    assert fake_opener.calls[-1][1]["timeout"] == 45

    # Environment variable used when no argument
    fake_opener.calls.clear()
    os.environ["CODER_IDLE_S"] = "90"
    try:
        cr.with_idle_timeout(fake_ds)
        fake_ds.nt._OPENER.open(object(), timeout=120)
        assert fake_opener.calls[-1][1]["timeout"] == 90
    finally:
        del os.environ["CODER_IDLE_S"]

    # Invalid env value -> 600
    fake_opener.calls.clear()
    os.environ["CODER_IDLE_S"] = "notanint"
    try:
        cr.with_idle_timeout(fake_ds)
        fake_ds.nt._OPENER.open(object(), timeout=120)
        assert fake_opener.calls[-1][1]["timeout"] == 600
    finally:
        del os.environ["CODER_IDLE_S"]

    # Wrapping twice keeps one proxy layer
    fake_opener.calls.clear()
    cr.with_idle_timeout(fake_ds, seconds=30)
    cr.with_idle_timeout(fake_ds, seconds=999)  # should not add another layer
    fake_ds.nt._OPENER.open(object(), timeout=120)
    assert fake_opener.calls[-1][1]["timeout"] == 30

    # Other attributes forwarded
    assert hasattr(fake_ds.nt._OPENER, "addheaders")
    assert fake_ds.nt._OPENER.addheaders == [("User-Agent", "test")]

    # Fake ds without nt returned unchanged
    plain_ds = SimpleNamespace()
    assert cr.with_idle_timeout(plain_ds) is plain_ds


def test_with_idle_timeout_positional_args_forwarded():
    """
    Regression test for Defect 2: ProxyOpener.open must forward positional arguments
    (keeping the first positional 'data' argument, dropping the positional timeout).
    """
    cr = load_coder_run()
    cr.RECEIPTS.clear()

    class FakeOpener:
        def __init__(self):
            self.calls = []

        def open(self, req, data=None, timeout=600, **kwargs):
            # Record exactly what we received
            self.calls.append({"data": data, "timeout": timeout, "kwargs": kwargs})
            return "response"

    fake_opener = FakeOpener()
    fake_ds = SimpleNamespace(nt=SimpleNamespace(_OPENER=fake_opener))

    cr.with_idle_timeout(fake_ds, seconds=45)

    # Call with positional arguments: (req, data, timeout)
    fake_ds.nt._OPENER.open("request_obj", "my_data", 120)

    assert len(fake_opener.calls) == 1
    call = fake_opener.calls[0]
    # The first positional after req (data) should be forwarded
    assert call["data"] == "my_data"
    # The positional timeout should be dropped and replaced by the proxy's timeout
    assert call["timeout"] == 45
    # No extra kwargs leaked
    assert call["kwargs"] == {}


def test_wrap_ds_retries_and_receipts():
    cr = load_coder_run()
    cr.RECEIPTS.clear()

    # Fake original_ds returning a module with _stream_once and chat_stream
    stream_once_calls = []

    def fake_stream_once(key, body):
        stream_once_calls.append(body.copy())
        return (200, "", {})

    chat_stream_calls = []

    def fake_chat_stream(pool, keys, model, system, user, max_tokens=40000):
        chat_stream_calls.append(max_tokens)
        # First call: length finish, empty reply
        if len(chat_stream_calls) == 1:
            return "", {"finish": "length", "status": 0, "wall_s": 0.1, "usage": {}, "error": None}
        # Second call: success
        return "ok", {"finish": "stop", "status": 0, "wall_s": 0.2, "usage": {}, "error": None}

    def original_ds():
        return SimpleNamespace(
            _stream_once=fake_stream_once,
            chat_stream=fake_chat_stream,
        )

    wrapped_ds = cr.wrap_ds(original_ds, "on", "high")
    mod = wrapped_ds()

    # Check profile applied to _stream_once
    mod._stream_once("FAKEKEY", {"model": "nvidia/nemotron-3-ultra-550b-a55b", "messages": []})
    assert stream_once_calls[-1]["chat_template_kwargs"] == {"enable_thinking": True}
    assert stream_once_calls[-1]["reasoning_effort"] == "high"

    # Now test chat_stream retry logic
    reply, info = mod.chat_stream("pool", "keys", "nvidia/nemotron-3-ultra-550b-a55b", "sys", "user", max_tokens=1000)
    assert reply == "ok"
    assert info["attempts"] == 2
    assert chat_stream_calls == [1000, 2000]  # doubled once

    # Check receipts
    assert len(cr.RECEIPTS) == 2
    for r in cr.RECEIPTS:
        assert set(r.keys()) == {"model", "attempt", "max_tokens", "status", "wall_s", "finish", "usage", "error", "thinking", "effort"}
        assert r["thinking"] == "on"
        assert r["effort"] == "high"
        # Ensure no key material leaked
        assert "FAKEKEY" not in str(r)

    # Test: failure with another finish value is NOT retried
    cr.RECEIPTS.clear()
    chat_stream_calls.clear()

    def fake_chat_stream2(pool, keys, model, system, user, max_tokens=40000):
        chat_stream_calls.append(max_tokens)
        return "", {"finish": "error", "status": 1, "wall_s": 0.1, "usage": {}, "error": "boom"}

    def original_ds2():
        return SimpleNamespace(
            _stream_once=fake_stream_once,
            chat_stream=fake_chat_stream2,
        )

    wrapped_ds2 = cr.wrap_ds(original_ds2, "off", "medium")
    mod2 = wrapped_ds2()
    reply2, info2 = mod2.chat_stream("pool", "keys", "nvidia/nemotron-3-ultra-550b-a55b", "sys", "user", max_tokens=1000)
    assert reply2 == ""
    assert info2["attempts"] == 1
    assert chat_stream_calls == [1000]
    assert len(cr.RECEIPTS) == 1

    # Test: 128000 ceiling blocks further retry
    cr.RECEIPTS.clear()
    chat_stream_calls.clear()

    def fake_chat_stream3(pool, keys, model, system, user, max_tokens=40000):
        chat_stream_calls.append(max_tokens)
        return "", {"finish": "length", "status": 0, "wall_s": 0.1, "usage": {}, "error": None}

    def original_ds3():
        return SimpleNamespace(
            _stream_once=fake_stream_once,
            chat_stream=fake_chat_stream3,
        )

    wrapped_ds3 = cr.wrap_ds(original_ds3, "on", "low")
    mod3 = wrapped_ds3()
    reply3, info3 = mod3.chat_stream("pool", "keys", "nvidia/nemotron-3-ultra-550b-a55b", "sys", "user", max_tokens=100000)
    assert reply3 == ""
    assert info3["attempts"] == 1  # no retry because next would be 200000 > 128000
    assert chat_stream_calls == [100000]
    assert len(cr.RECEIPTS) == 1


def test_wrap_ds_ceiling_returns_last_attempt_info():
    """
    Regression test for Defect 1: when the length retry would exceed 128000,
    the wrapper must return the LAST attempt's (reply, info) including status,
    finish, error, not just ("", {"attempts": 1}).
    """
    cr = load_coder_run()
    cr.RECEIPTS.clear()

    chat_stream_calls = []

    def fake_chat_stream(pool, keys, model, system, user, max_tokens=40000):
        chat_stream_calls.append(max_tokens)
        # Always return length finish with specific status/error
        return "", {
            "finish": "length",
            "status": 42,
            "wall_s": 0.5,
            "usage": {"prompt_tokens": 10, "completion_tokens": 20},
            "error": "max_tokens_exceeded",
        }

    def original_ds():
        return SimpleNamespace(
            _stream_once=lambda k, b: (200, "", {}),
            chat_stream=fake_chat_stream,
        )

    wrapped_ds = cr.wrap_ds(original_ds, "on", "high")
    mod = wrapped_ds()

    # max_tokens=100000 -> next would be 200000 > 128000, so no retry
    reply, info = mod.chat_stream("pool", "keys", "nvidia/nemotron-3-ultra-550b-a55b", "sys", "user", max_tokens=100000)

    # The reply is empty (as returned by the attempt)
    assert reply == ""
    # But info must contain the last attempt's details, not just attempts=1
    assert info["attempts"] == 1
    assert info["status"] == 42
    assert info["finish"] == "length"
    assert info["wall_s"] == 0.5
    assert info["usage"] == {"prompt_tokens": 10, "completion_tokens": 20}
    assert info["error"] == "max_tokens_exceeded"
    # And the receipt should also have these fields
    assert len(cr.RECEIPTS) == 1
    receipt = cr.RECEIPTS[0]
    assert receipt["status"] == 42
    assert receipt["finish"] == "length"
    assert receipt["error"] == "max_tokens_exceeded"


def test_write_receipt():
    cr = load_coder_run()
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        receipts = [{"a": 1}, {"b": 2}]
        result = cr.write_receipt(tmp_path, receipts)
        assert result is not None
        assert result == tmp_path / "RECEIPT.json"
        assert result.exists()
        import json
        with open(result, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data == receipts

    # Missing folder -> None
    assert cr.write_receipt("/nonexistent/path", []) is None


def test_find_out_arg():
    cr = load_coder_run()
    assert cr.find_out_arg([]) is None
    assert cr.find_out_arg(["--out", "dir"]) == "dir"
    assert cr.find_out_arg(["--out=dir"]) == "dir"
    assert cr.find_out_arg(["--other", "x", "--out", "dir"]) == "dir"
    assert cr.find_out_arg(["--out"]) is None
    assert cr.find_out_arg(["--out", "--another"]) == "--another"


# ===== NEW TESTS FOR GAP 1: Length continuation retry bound (at most 2 retries = 3 attempts) =====

def test_length_retry_max_three_attempts_always_length():
    """
    When chat_stream always returns finish='length', it must be called exactly 3 times
    (initial + 2 retries) with max_tokens 1000, 2000, 4000. Never a 4th call with 8000.
    """
    cr = load_coder_run()
    cr.RECEIPTS.clear()

    chat_stream_calls = []

    def fake_chat_stream(pool, keys, model, system, user, max_tokens=40000):
        chat_stream_calls.append(max_tokens)
        return "", {"finish": "length", "status": 0, "wall_s": 0.1, "usage": {}, "error": None}

    def original_ds():
        return SimpleNamespace(
            _stream_once=lambda k, b: (200, "", {}),
            chat_stream=fake_chat_stream,
        )

    wrapped_ds = cr.wrap_ds(original_ds, "on", "high")
    mod = wrapped_ds()

    reply, info = mod.chat_stream("pool", "keys", "nvidia/nemotron-3-ultra-550b-a55b", "sys", "user", max_tokens=1000)

    # Exactly 3 calls: 1000, 2000, 4000
    assert chat_stream_calls == [1000, 2000, 4000], f"Expected [1000, 2000, 4000], got {chat_stream_calls}"
    # 3 attempts recorded
    assert info["attempts"] == 3
    # Final reply empty, finish still length
    assert reply == ""
    assert info["finish"] == "length"
    # 3 receipts
    assert len(cr.RECEIPTS) == 3
    assert [r["attempt"] for r in cr.RECEIPTS] == [1, 2, 3]
    assert [r["max_tokens"] for r in cr.RECEIPTS] == [1000, 2000, 4000]


def test_length_retry_success_on_third_attempt():
    """
    When chat_stream returns length twice then success on third call,
    the wrapper returns the success reply with attempts == 3.
    """
    cr = load_coder_run()
    cr.RECEIPTS.clear()

    chat_stream_calls = []

    def fake_chat_stream(pool, keys, model, system, user, max_tokens=40000):
        chat_stream_calls.append(max_tokens)
        if len(chat_stream_calls) <= 2:
            return "", {"finish": "length", "status": 0, "wall_s": 0.1, "usage": {}, "error": None}
        # Third call succeeds
        return "success on third", {"finish": "stop", "status": 0, "wall_s": 0.3, "usage": {}, "error": None}

    def original_ds():
        return SimpleNamespace(
            _stream_once=lambda k, b: (200, "", {}),
            chat_stream=fake_chat_stream,
        )

    wrapped_ds = cr.wrap_ds(original_ds, "on", "high")
    mod = wrapped_ds()

    reply, info = mod.chat_stream("pool", "keys", "nvidia/nemotron-3-ultra-550b-a55b", "sys", "user", max_tokens=1000)

    # Called 3 times: 1000, 2000, 4000
    assert chat_stream_calls == [1000, 2000, 4000]
    # Success reply returned
    assert reply == "success on third"
    # Attempts recorded as 3
    assert info["attempts"] == 3
    assert info["finish"] == "stop"
    # 3 receipts
    assert len(cr.RECEIPTS) == 3
    assert cr.RECEIPTS[2]["finish"] == "stop"


def test_length_retry_all_three_fail_returns_last_info():
    """
    When all 3 attempts return finish='length', the wrapper returns the last attempt's
    info with attempts == 3 and finish 'length'.
    """
    cr = load_coder_run()
    cr.RECEIPTS.clear()

    chat_stream_calls = []

    def fake_chat_stream(pool, keys, model, system, user, max_tokens=40000):
        chat_stream_calls.append(max_tokens)
        return "", {
            "finish": "length",
            "status": 99,
            "wall_s": 0.1 * len(chat_stream_calls),
            "usage": {"attempt": len(chat_stream_calls)},
            "error": "still_length",
        }

    def original_ds():
        return SimpleNamespace(
            _stream_once=lambda k, b: (200, "", {}),
            chat_stream=fake_chat_stream,
        )

    wrapped_ds = cr.wrap_ds(original_ds, "on", "high")
    mod = wrapped_ds()

    reply, info = mod.chat_stream("pool", "keys", "nvidia/nemotron-3-ultra-550b-a55b", "sys", "user", max_tokens=1000)

    # Exactly 3 calls
    assert chat_stream_calls == [1000, 2000, 4000]
    # Reply empty
    assert reply == ""
    # Info has attempts=3 and last attempt's details
    assert info["attempts"] == 3
    assert info["finish"] == "length"
    assert info["status"] == 99
    assert info["wall_s"] == 0.3
    assert info["usage"] == {"attempt": 3}
    assert info["error"] == "still_length"
    # 3 receipts, last one has the final details
    assert len(cr.RECEIPTS) == 3
    assert cr.RECEIPTS[2]["attempt"] == 3
    assert cr.RECEIPTS[2]["status"] == 99
    assert cr.RECEIPTS[2]["error"] == "still_length"


# ===== NEW TESTS FOR GAP 2: Receipts no-key test (key passed through keys/pool args) =====

def test_receipts_no_key_material_leaked_via_keys_arg():
    """
    The fake key string passed through the `keys` argument of chat_stream
    must not appear anywhere in the JSON-serialized RECEIPTS.
    """
    cr = load_coder_run()
    cr.RECEIPTS.clear()

    FAKE_KEY = "sk-FAKEKEY-FOR-TESTING-12345"
    chat_stream_calls = []

    def fake_chat_stream(pool, keys, model, system, user, max_tokens=40000):
        chat_stream_calls.append((pool, keys, max_tokens))
        # Record the key in the returned info to simulate potential leakage
        return "ok", {
            "finish": "stop",
            "status": 0,
            "wall_s": 0.1,
            "usage": {},
            "error": f"key_was_{keys}",  # deliberately include key in error text
        }

    def original_ds():
        return SimpleNamespace(
            _stream_once=lambda k, b: (200, "", {}),
            chat_stream=fake_chat_stream,
        )

    wrapped_ds = cr.wrap_ds(original_ds, "on", "high")
    mod = wrapped_ds()

    # Pass the fake key through the `keys` parameter (second positional arg)
    reply, info = mod.chat_stream("my_pool", FAKE_KEY, "nvidia/nemotron-3-ultra-550b-a55b", "sys", "user", max_tokens=1000)

    assert reply == "ok"
    assert info["attempts"] == 1
    assert chat_stream_calls == [("my_pool", FAKE_KEY, 1000)]

    # Now verify the fake key appears NOWHERE in the JSON-serialized receipts
    receipts_json = json.dumps(cr.RECEIPTS)
    assert FAKE_KEY not in receipts_json, f"Fake key leaked into receipts: {receipts_json}"

    # Also verify the key doesn't appear in any individual receipt field
    for r in cr.RECEIPTS:
        for v in r.values():
            assert FAKE_KEY not in str(v), f"Fake key leaked in receipt field: {r}"


def test_receipts_no_key_material_leaked_via_pool_arg():
    """
    The fake key string passed through the `pool` argument of chat_stream
    must not appear anywhere in the JSON-serialized RECEIPTS.
    """
    cr = load_coder_run()
    cr.RECEIPTS.clear()

    FAKE_KEY = "pool-FAKEKEY-ABCDE-67890"
    chat_stream_calls = []

    def fake_chat_stream(pool, keys, model, system, user, max_tokens=40000):
        chat_stream_calls.append((pool, keys, max_tokens))
        # Record the key in the returned info to simulate potential leakage
        return "ok", {
            "finish": "stop",
            "status": 0,
            "wall_s": 0.1,
            "usage": {},
            "error": f"pool_was_{pool}",
        }

    def original_ds():
        return SimpleNamespace(
            _stream_once=lambda k, b: (200, "", {}),
            chat_stream=fake_chat_stream,
        )

    wrapped_ds = cr.wrap_ds(original_ds, "off", "medium")
    mod = wrapped_ds()

    # Pass the fake key through the `pool` parameter (first positional arg)
    reply, info = mod.chat_stream(FAKE_KEY, "my_keys", "nvidia/nemotron-3-ultra-550b-a55b", "sys", "user", max_tokens=1000)

    assert reply == "ok"
    assert info["attempts"] == 1
    assert chat_stream_calls == [(FAKE_KEY, "my_keys", 1000)]

    # Verify the fake key appears NOWHERE in the JSON-serialized receipts
    receipts_json = json.dumps(cr.RECEIPTS)
    assert FAKE_KEY not in receipts_json, f"Fake key leaked into receipts via pool: {receipts_json}"

    for r in cr.RECEIPTS:
        for v in r.values():
            assert FAKE_KEY not in str(v), f"Fake key leaked in receipt field: {r}"


def test_receipts_no_key_material_leaked_with_retries():
    """
    Even with retries (length finish), the fake key passed via keys/pool
    must not leak into any receipt across all attempts.
    """
    cr = load_coder_run()
    cr.RECEIPTS.clear()

    FAKE_KEY = "retry-FAKEKEY-XYZ-999"
    chat_stream_calls = []

    def fake_chat_stream(pool, keys, model, system, user, max_tokens=40000):
        chat_stream_calls.append((pool, keys, max_tokens))
        if len(chat_stream_calls) < 3:
            return "", {
                "finish": "length",
                "status": 0,
                "wall_s": 0.1,
                "usage": {},
                "error": f"attempt_{len(chat_stream_calls)}_key_{keys}_pool_{pool}",
            }
        return "final", {
            "finish": "stop",
            "status": 0,
            "wall_s": 0.3,
            "usage": {},
            "error": f"final_key_{keys}_pool_{pool}",
        }

    def original_ds():
        return SimpleNamespace(
            _stream_once=lambda k, b: (200, "", {}),
            chat_stream=fake_chat_stream,
        )

    wrapped_ds = cr.wrap_ds(original_ds, "on", "low")
    mod = wrapped_ds()

    # Pass fake key in both pool and keys
    reply, info = mod.chat_stream(FAKE_KEY, FAKE_KEY, "nvidia/nemotron-3-ultra-550b-a55b", "sys", "user", max_tokens=1000)

    assert reply == "final"
    assert info["attempts"] == 3
    assert chat_stream_calls == [
        (FAKE_KEY, FAKE_KEY, 1000),
        (FAKE_KEY, FAKE_KEY, 2000),
        (FAKE_KEY, FAKE_KEY, 4000),
    ]

    # Verify the fake key appears NOWHERE in the JSON-serialized receipts
    receipts_json = json.dumps(cr.RECEIPTS)
    assert FAKE_KEY not in receipts_json, f"Fake key leaked into receipts with retries: {receipts_json}"

    for r in cr.RECEIPTS:
        for v in r.values():
            assert FAKE_KEY not in str(v), f"Fake key leaked in receipt field: {r}"
```
