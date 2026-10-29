# TASK: return ONLY ONE FILE: tests/test_coder_tools.py (complete). Reply with exactly one block `FILE: tests/test_coder_tools.py` then the python fenced. The MODULE scripts/source/coder_run.py is correct (shown for reference, do NOT return it). Fix two test gaps reported by the GLM reviewer (verified by mutation) and keep every other test:
1. The rule 'at most 2 retries' of the length continuation is unprotected: add isolated tests with a fake chat_stream that ALWAYS returns ("", {"finish": "length", "status": 0}): starting at max_tokens=1000 it is called exactly THREE times with 1000, 2000, 4000 (so 2 retries, never a 4th call with 8000); a variant where success comes on the THIRD attempt returns that reply with info['attempts'] == 3; a variant where all three fail returns ("" , info with attempts == 3 and finish 'length'). These must fail if the bound is changed to 2 attempts or removed.
2. The receipts no-key test is vacuous (FAKEKEY is only passed to _stream_once, never to chat_stream): pass the fake key string through the `keys` / pool arguments of the wrapped chat_stream call (the real signature is chat_stream(pool, keys, model, system, user, max_tokens=...)) and in the fake's recorded info/error text, then assert the string appears NOWHERE in json.dumps(RECEIPTS).
Use copy.deepcopy and plain assignment; never a helper that rejects no-effect mutations.

## CURRENT tests/test_coder_tools.py
```python
from __future__ import annotations

import sys
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import tempfile
import os


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
```
## scripts/source/coder_run.py (reference only)
```python
from __future__ import annotations

import sys
import importlib.util
import os
import json
from pathlib import Path
from argparse import ArgumentParser
from typing import Callable, Any, List, Dict, Optional


RECEIPTS: List[Dict[str, Any]] = []


def profile_extra(model: str, thinking: str, effort: str) -> dict:
    if not model.startswith("nvidia/nemotron"):
        return {}
    extra = {"chat_template_kwargs": {"enable_thinking": thinking == "on"}}
    if effort in ("low", "medium", "high"):
        extra["reasoning_effort"] = effort
    return extra


def apply_profile(body: dict, thinking: str, effort: str) -> dict:
    model = body.get("model", "")
    extra = profile_extra(model, thinking, effort)
    if not extra:
        return body.copy()
    protected = {"model", "messages", "stream", "max_tokens", "temperature"}
    new_body = body.copy()
    for k, v in extra.items():
        if k not in protected:
            new_body[k] = v
    return new_body


def with_idle_timeout(ds: Any, seconds: Optional[int] = None) -> Any:
    explicit = seconds is not None
    if seconds is None:
        val = os.environ.get("CODER_IDLE_S")
        try:
            seconds = int(val) if val is not None else 600
        except ValueError:
            seconds = 600

    if not hasattr(ds, "nt") or not hasattr(ds.nt, "_OPENER"):
        return ds

    original_opener = ds.nt._OPENER
    if getattr(original_opener, "_coder_idle_proxied", False):
        current_explicit = getattr(original_opener, "_coder_idle_explicit", False)
        if explicit and current_explicit:
            return ds
        original_opener._timeout = seconds
        original_opener._coder_idle_explicit = explicit
        return ds

    class ProxyOpener:
        def __init__(self, opener: Any, timeout: int, explicit: bool):
            self._opener = opener
            self._timeout = timeout
            self._coder_idle_proxied = True
            self._coder_idle_explicit = explicit

        def open(self, req: Any, *args: Any, **kwargs: Any) -> Any:
            kwargs["timeout"] = self._timeout
            return self._opener.open(req, *args[:1], **kwargs)

        def __getattr__(self, name: str) -> Any:
            return getattr(self._opener, name)

    ds.nt._OPENER = ProxyOpener(original_opener, seconds, explicit)
    return ds


def wrap_ds(original_ds: Callable[[], Any], thinking: str, effort: str) -> Callable[[], Any]:
    def ds() -> Any:
        mod = original_ds()

        # Keep existing behaviour: apply profile to _stream_once
        orig_stream_once = mod._stream_once
        mod._stream_once = lambda key, body: orig_stream_once(key, apply_profile(body, thinking, effort))

        # Apply idle timeout (safe: no-op if nt/_OPENER missing)
        mod = with_idle_timeout(mod)

        # Wrap chat_stream for retries and receipts ONLY if it exists
        if hasattr(mod, "chat_stream"):
            orig_chat_stream = mod.chat_stream

            def wrapped_chat_stream(
                pool: Any,
                keys: Any,
                model: str,
                system: str,
                user: str,
                max_tokens: int = 40000,
            ) -> tuple[str, dict]:
                global RECEIPTS
                attempts = 0
                current_max_tokens = max_tokens
                last_reply = ""
                last_info: dict = {}

                while True:
                    attempts += 1
                    reply, info = orig_chat_stream(pool, keys, model, system, user, current_max_tokens)

                    receipt = {
                        "model": model,
                        "attempt": attempts,
                        "max_tokens": current_max_tokens,
                        "status": info.get("status"),
                        "wall_s": info.get("wall_s"),
                        "finish": info.get("finish"),
                        "usage": info.get("usage"),
                        "error": info.get("error"),
                        "thinking": thinking,
                        "effort": effort,
                    }
                    RECEIPTS.append(receipt)

                    if reply == "" and info.get("finish") == "length" and attempts < 3:
                        next_max_tokens = current_max_tokens * 2
                        if next_max_tokens > 128000:
                            last_reply, last_info = reply, info
                            break
                        current_max_tokens = next_max_tokens
                        continue
                    else:
                        last_reply = reply
                        last_info = info
                        break

                last_info["attempts"] = attempts
                return last_reply, last_info

            mod.chat_stream = wrapped_chat_stream

        return mod

    return ds


def split_args(argv: list[str] | None = None) -> tuple[str, str, list[str]]:
    parser = ArgumentParser(add_help=False)
    parser.add_argument("--thinking", choices=("on", "off"), default="on")
    parser.add_argument("--effort", choices=("low", "medium", "high", "none"), default="medium")
    if argv is None:
        argv = sys.argv[1:]
    args, rest = parser.parse_known_args(argv)
    return args.thinking, args.effort, rest


def find_out_arg(args: list[str]) -> str | None:
    i = 0
    while i < len(args):
        if args[i] == "--out":
            if i + 1 < len(args):
                return args[i + 1]
            return None
        elif args[i].startswith("--out="):
            return args[i][6:]
        i += 1
    return None


def write_receipt(out_dir: Path | str, receipts: list[dict]) -> Path | None:
    out_path = Path(out_dir)
    if not out_path.exists() or not out_path.is_dir():
        return None
    receipt_file = out_path / "RECEIPT.json"
    try:
        with open(receipt_file, "w", encoding="utf-8") as f:
            json.dump(receipts, f, indent=1, sort_keys=True)
        return receipt_file
    except Exception:
        return None


def main(argv: list[str] | None = None) -> int:
    global RECEIPTS
    RECEIPTS = []

    thinking, effort, rest = split_args(argv)
    print(f"coder profile: thinking={thinking} effort={effort}")

    root = Path(__file__).resolve().parents[2]
    nc_path = root / "scripts" / "source" / "nemotron_code.py"
    spec = importlib.util.spec_from_file_location("nemotron_code_wrapped", nc_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {nc_path}")
    nc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(nc)

    nc._ds = wrap_ds(nc._ds, thinking, effort)

    sys.argv = ["nemotron_code"] + rest
    ret = nc.main()

    out_dir = find_out_arg(rest)
    if out_dir:
        write_receipt(out_dir, RECEIPTS)

    return ret


if __name__ == "__main__":
    sys.exit(main())
```
