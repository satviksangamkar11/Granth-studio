# FIX CALL: return BOTH files in full: `scripts/source/coder_run.py` and `tests/test_coder_run.py`. They were run; the pytest output below is the mechanical truth. For every failure decide, using the SPEC as the only authority, whether the TEST or the MODULE is wrong and fix that side. Do not weaken a test to make it pass: if the spec requires the behaviour, fix the module. A key or secret must never appear in any output. Reply with exactly two FILE blocks.

## PYTEST OUTPUT
```
...F                                                                     [100%]
================================== FAILURES ===================================
_______________________________ test_split_args _______________________________
tests\test_coder_run.py:98: in test_split_args
    assert rest == []
E   AssertionError: assert ['-q', '--tb=...coder_run.py'] == []
E     
E     Left contains 3 more items, first extra item: '-q'
E     Use -v to get more diff
=========================== short test summary info ===========================
FAILED tests/test_coder_run.py::test_split_args - AssertionError: assert ['-q...
1 failed, 3 passed in 0.12s

```

## SPEC
# SPEC: NEW wrapper `scripts/source/coder_run.py` + NEW `tests/test_coder_run.py`. Return exactly these TWO files in full. Do NOT output or modify any existing file.
Purpose (owner 2026-10-28): run the existing coder tool with thinking OFF and reasoning effort MEDIUM, without editing it. Evidence (live probe): for `nvidia/nemotron-3-ultra-550b-a55b` the endpoint accepts the top-level `reasoning_effort` ("low"|"medium"|"high") and `chat_template_kwargs: {"enable_thinking": true|false}`. These fields are NOT proven for other models and must never be sent to them.
## Facts about the existing code (do not change them)
- `scripts/source/nemotron_code.py` has `main() -> int` (parses sys.argv with argparse: --spec --out --expect --allow-root --model --max-tokens) and a function `_ds()` that loads `scripts/source/draft_source.py` as a NEW module object on every call and returns it. `draft_source.chat_stream` builds the request through the module-level function `_stream_once(key: str, body: dict) -> tuple[int, str, dict]` (looked up in that module's globals at call time).
- `ROOT = Path(__file__).resolve().parents[2]`; tests locate files with `ROOT = Path(__file__).resolve().parents[1]`.
## coder_run.py API
- `profile_extra(model: str, thinking: str, effort: str) -> dict`: if `model` does not start with `nvidia/nemotron` return `{}`. Else `{"chat_template_kwargs": {"enable_thinking": thinking == "on"}}` plus `"reasoning_effort": effort` when effort in ("low","medium","high"). (thinking "on"/"off"; effort "none" omits the effort field.)
- `apply_profile(body: dict, thinking: str, effort: str) -> dict`: returns a COPY of `body` with `profile_extra(body.get("model", ""), thinking, effort)` merged in, never overwriting the keys `model`, `messages`, `stream`, `max_tokens`, `temperature`.
- `wrap_ds(original_ds, thinking: str, effort: str)`: returns a function `ds()` that calls `original_ds()` to get the module, replaces its attribute `_stream_once` by a wrapper `lambda key, body: orig(key, apply_profile(body, thinking, effort))` (keeping the original for the call) and returns the module.
- `main(argv=None) -> int`: parse ONLY `--thinking` (on|off, default off) and `--effort` (low|medium|high|none, default medium) with `parse_known_args`; load `nemotron_code.py` BY PATH with importlib (module name `nemotron_code_wrapped`); set its `_ds` to `wrap_ds(its original _ds, ...)`; set `sys.argv = ["nemotron_code"] + the remaining args`; return `nc.main()`. Print one line before the call: `coder profile: thinking=<on|off> effort=<value>` (never any key).
- Bottom: `if __name__ == "__main__": sys.exit(main())`.
- Style: `from __future__ import annotations`, stdlib only, nothing at import time except imports and definitions; no key is ever printed or stored.
## Tests (synthetic, no network, no key; load coder_run by path with importlib)
profile_extra: nemotron + off + medium gives exactly `{"chat_template_kwargs": {"enable_thinking": False}, "reasoning_effort": "medium"}`; on gives enable_thinking True; effort none gives only chat_template_kwargs; a GLM id (`z-ai/glm-5.3-flash`) gives {}; an unknown id gives {}. apply_profile: copy not mutated original; protected keys cannot be overwritten (body temperature stays 0.2, stream True); non-nemotron body unchanged. wrap_ds with a fake original_ds returning a simple namespace object that has `_stream_once` recording the body it receives: after wrapping, calling `_stream_once("FAKEKEY", {"model": "nvidia/nemotron-3-ultra-550b-a55b", "messages": []})` makes the recorded body contain both fields; for a GLM model body the recorded body is unchanged. main: with a monkeypatched fake `nemotron_code` module is hard, so test only the argument split: expose a helper `split_args(argv) -> (thinking, effort, rest)` and test it (defaults off/medium; `--thinking on --effort high --spec x` gives on, high, ["--spec","x"]; unknown flags are left in rest).
Reply with only the two FILE blocks:
FILE: scripts/source/coder_run.py
FILE: tests/test_coder_run.py


## CURRENT MODULE scripts/source/coder_run.py
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
    args, rest = parser.parse_known_args(argv or sys.argv[1:])
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

## CURRENT TESTS tests/test_coder_run.py
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
