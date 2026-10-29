# SPEC: change `scripts/source/coder_run.py` and its test `tests/test_coder_run.py`; ADD a NEW test file `tests/test_coder_tools.py`. Return exactly these THREE files in full (existing code and tests shown below must keep working except the one stated change).
Checklist rows N8 and N16 (owner rules): (1) thinking ON is the default for the coder; (2) the client's 120 s idle socket timeout kills long thinking calls: make it 600 s and configurable; (3) the length limit must never silently stop a call: automatic bounded continuation when a reply ends with finish=length; (4) record a receipt per call. Standard library only; `from __future__ import annotations`; nothing at import time except imports and definitions; no key or secret is ever printed, logged or stored.

## Facts about the code you build on (do not change them)
- `scripts/source/draft_source.py` is loaded by path (module name `ds`). It has `ds.nt` (key pool module with `load_keys`, `KeyPool`, `scrub`, and `ds.nt._OPENER`, an `urllib` opener whose method `open(req, timeout=...)` is called by `ds._stream_once(key, body)` with a hard-coded `timeout=120` (the per-read idle timeout)). `ds.chat_stream(pool, keys, model, system, user, max_tokens=40000) -> (reply_text, info)`; `info` has `status`, `wall_s`, `finish`, `usage`, `error`; a reply cut by the token limit is returned as `("", info)` with `info["finish"] == "length"` (a failed call).
- `scripts/source/nemotron_code.py` has `_ds()` which loads draft_source as a NEW module object each call, and `main()` which reads `sys.argv`, calls `ds.chat_stream(...)` once and writes files. It must NOT be changed.

## Changes in coder_run.py
1. DEFAULT THINKING ON: `split_args` default for `--thinking` becomes `"on"` (effort default stays `medium`). Update the existing test that asserted the old default.
2. `with_idle_timeout(ds, seconds: int | None = None)`: reads the seconds from the argument, else from the environment variable `CODER_IDLE_S` (an int; invalid or missing -> 600). Replaces `ds.nt._OPENER` by a small proxy object whose `open(req, *args, **kwargs)` forces `kwargs["timeout"] = seconds` (also overriding a positional timeout) and forwards to the original opener; every other attribute is forwarded unchanged (`__getattr__`). Idempotent (wrapping twice keeps one proxy). Returns `ds`. Never raises when `ds` has no `nt` or `_OPENER` (then it returns `ds` unchanged).
3. `wrap_ds(original_ds, thinking, effort)` keeps its behaviour (adds the profile to the request body) and ALSO: (a) applies `with_idle_timeout` to the module it returns; (b) wraps `mod.chat_stream` so that: it calls the original; if the call failed (empty reply) and `info.get("finish") == "length"` it retries with `max_tokens` doubled, at most 2 retries and never above 128000 (a retry that would exceed 128000 is not made); every attempt is appended to the module-level list `RECEIPTS` as a dict `{"model", "attempt" (1-based), "max_tokens", "status", "wall_s", "finish", "usage", "error", "thinking", "effort"}` taken from `info` (never the prompt, reply or any key); the wrapper returns the LAST attempt's `(reply, info)` and adds `info["attempts"] = <number of attempts>`.
4. `write_receipt(out_dir: Path | str, receipts: list[dict]) -> Path`: writes `RECEIPT.json` (json, indent 1, sort_keys, utf-8) inside the folder if it exists; returns the path; never raises (returns the path even if writing failed silently is NOT acceptable: on failure return `None`).
5. `main`: after `nc.main()` returns, find the value of `--out` in the remaining args (the argument after `--out`); if present and the folder exists, call `write_receipt(out, RECEIPTS)` (a receipt is also useful when nothing was drafted: the tool creates the folder in that case). Print `coder profile: thinking=<..> effort=<..>` exactly as before and return nc.main()'s return code.

## Tests
`tests/test_coder_run.py`: keep every existing test; only the default-thinking assertion changes to `on`. `tests/test_coder_tools.py` (NEW, offline, no network, no key; load coder_run by importlib BY PATH, `ROOT = Path(__file__).resolve().parents[1]`): with fake objects only:
- `with_idle_timeout`: a fake ds whose `nt._OPENER` records the kwargs of `open(req, timeout=120)`; after wrapping, calling `ds.nt._OPENER.open(object(), timeout=120)` forwards `timeout == 600`; `seconds=45` argument wins; env `CODER_IDLE_S=90` is used when no argument (monkeypatch.setenv); invalid env value -> 600; wrapping twice keeps one proxy layer; other attributes (e.g. `addheaders`) are forwarded; a fake ds without `nt` is returned unchanged.
- `wrap_ds` with a fake `original_ds` returning a namespace that has `_stream_once` and `chat_stream`: the profile is still applied to the body; a `chat_stream` that returns `("", {"finish": "length", "status": 0})` is retried with doubled `max_tokens` (check the values passed: 1000 -> 2000 -> 4000) at most 2 retries; success on the second attempt returns that reply and `info["attempts"] == 2`; a failure with another finish value is NOT retried; the 128000 ceiling blocks a further retry (start at 100000: second attempt would be 200000 -> no retry); `RECEIPTS` receives one dict per attempt with the documented keys and contains no key (use a fake key string in the fake call's arguments and assert it appears nowhere in the receipts' json).
- `write_receipt`: writes valid JSON in a tmp folder; returns None for a missing folder.
- `main` argument handling: with the wrapped `nemotron_code` replaced by a fake module (monkeypatch `importlib.util.spec_from_file_location` or set up a tiny fake file path) is hard: instead test the helper that finds `--out` in an argument list: expose `find_out_arg(args: list[str]) -> str | None` (value after `--out`, also `--out=VALUE`; None when absent) and test it.
Use plain assignment and `copy.deepcopy`; never a helper that rejects no-effect mutations.

## CURRENT scripts/source/coder_run.py
```python
from __future__ import annotations

import sys
import importlib.util
from pathlib import Path
from argparse import ArgumentParser
from typing import Callable, Any


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


def wrap_ds(original_ds: Callable[[], Any], thinking: str, effort: str) -> Callable[[], Any]:
    def ds() -> Any:
        mod = original_ds()
        orig_stream_once = mod._stream_once
        mod._stream_once = lambda key, body: orig_stream_once(key, apply_profile(body, thinking, effort))
        return mod
    return ds


def split_args(argv: list[str] | None = None) -> tuple[str, str, list[str]]:
    parser = ArgumentParser(add_help=False)
    parser.add_argument("--thinking", choices=("on", "off"), default="off")
    parser.add_argument("--effort", choices=("low", "medium", "high", "none"), default="medium")
    if argv is None:
        argv = sys.argv[1:]
    args, rest = parser.parse_known_args(argv)
    return args.thinking, args.effort, rest


def main(argv: list[str] | None = None) -> int:
    thinking, effort, rest = split_args(argv)
    print(f"coder profile: thinking={thinking} effort={effort}")

    # Load nemotron_code.py by path
    root = Path(__file__).resolve().parents[2]
    nc_path = root / "scripts" / "source" / "nemotron_code.py"
    spec = importlib.util.spec_from_file_location("nemotron_code_wrapped", nc_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {nc_path}")
    nc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(nc)

    # Wrap its _ds
    nc._ds = wrap_ds(nc._ds, thinking, effort)

    # Replace sys.argv for the wrapped main
    sys.argv = ["nemotron_code"] + rest
    return nc.main()


if __name__ == "__main__":
    sys.exit(main())

```
## CURRENT tests/test_coder_run.py
```python
from __future__ import annotations

import sys
import importlib.util
from pathlib import Path
from types import SimpleNamespace


def load_coder_run():
    root = Path(__file__).resolve().parents[1]
    cr_path = root / "scripts" / "source" / "coder_run.py"
    spec = importlib.util.spec_from_file_location("coder_run_test", cr_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {cr_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_profile_extra():
    cr = load_coder_run()
    # nemotron + off + medium
    assert cr.profile_extra("nvidia/nemotron-3-ultra-550b-a55b", "off", "medium") == {
        "chat_template_kwargs": {"enable_thinking": False},
        "reasoning_effort": "medium",
    }
    # nemotron + on + high
    assert cr.profile_extra("nvidia/nemotron-3-ultra-550b-a55b", "on", "high") == {
        "chat_template_kwargs": {"enable_thinking": True},
        "reasoning_effort": "high",
    }
    # nemotron + off + none (effort omitted)
    assert cr.profile_extra("nvidia/nemotron-3-ultra-550b-a55b", "off", "none") == {
        "chat_template_kwargs": {"enable_thinking": False},
    }
    # GLM id
    assert cr.profile_extra("z-ai/glm-5.3-flash", "on", "high") == {}
    # unknown id
    assert cr.profile_extra("some/other-model", "on", "high") == {}


def test_apply_profile():
    cr = load_coder_run()
    body = {
        "model": "nvidia/nemotron-3-ultra-550b-a55b",
        "messages": [],
        "stream": True,
        "max_tokens": 100,
        "temperature": 0.2,
    }
    # copy not mutated
    new_body = cr.apply_profile(body, "on", "medium")
    assert new_body is not body
    assert body["temperature"] == 0.2
    # protected keys not overwritten
    assert new_body["temperature"] == 0.2
    assert new_body["stream"] is True
    # extra fields added
    assert new_body["chat_template_kwargs"] == {"enable_thinking": True}
    assert new_body["reasoning_effort"] == "medium"

    # non-nemotron body unchanged
    body2 = {"model": "z-ai/glm-5.3-flash", "messages": [], "temperature": 0.5}
    new_body2 = cr.apply_profile(body2, "on", "high")
    assert new_body2 == body2


def test_wrap_ds():
    cr = load_coder_run()
    recorded = {}

    def fake_stream_once(key, body):
        recorded["key"] = key
        recorded["body"] = body
        return (200, "", {})

    def original_ds():
        return SimpleNamespace(_stream_once=fake_stream_once)

    wrapped_ds = cr.wrap_ds(original_ds, "on", "high")
    mod = wrapped_ds()
    mod._stream_once("FAKEKEY", {"model": "nvidia/nemotron-3-ultra-550b-a55b", "messages": []})
    assert recorded["key"] == "FAKEKEY"
    assert recorded["body"]["chat_template_kwargs"] == {"enable_thinking": True}
    assert recorded["body"]["reasoning_effort"] == "high"

    recorded.clear()
    mod._stream_once("FAKEKEY2", {"model": "z-ai/glm-5.3-flash", "messages": []})
    assert recorded["body"] == {"model": "z-ai/glm-5.3-flash", "messages": []}


def test_split_args():
    cr = load_coder_run()
    # defaults
    thinking, effort, rest = cr.split_args([])
    assert thinking == "off"
    assert effort == "medium"
    assert rest == []
    # with flags
    thinking, effort, rest = cr.split_args(["--thinking", "on", "--effort", "high", "--spec", "x"])
    assert thinking == "on"
    assert effort == "high"
    assert rest == ["--spec", "x"]
    # unknown flags left in rest
    thinking, effort, rest = cr.split_args(["--unknown", "foo"])
    assert thinking == "off"
    assert effort == "medium"
    assert rest == ["--unknown", "foo"]

```

Reply with only the three FILE blocks:
FILE: scripts/source/coder_run.py
FILE: tests/test_coder_run.py
FILE: tests/test_coder_tools.py
