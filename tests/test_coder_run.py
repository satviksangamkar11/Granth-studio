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
