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
