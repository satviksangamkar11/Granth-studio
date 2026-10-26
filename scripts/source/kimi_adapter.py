"""Kimi (Moonshot) provider adapter for the director: the ONLY paid path of the director, behind the money guard (scripts/image_trials/v5_ledger.py, phase P4, $1 hard cap).
Per call: refuse if any earlier reservation is unreconciled (checked again INSIDE the reservation lock); COUNT the input tokens with Moonshot's endpoint (refuse if counting fails);
reserve the worst case on disk BEFORE dispatch; settle from the provider-reported usage; any error, timeout or reply without usage is recorded UNKNOWN at full reservation, which
stops the run (the next call is refused). No automatic retry of a paid call. HTTP redirects are refused (the Authorization header never leaves api.moonshot.ai). The key is read at
run time from the owner's key file or MOONSHOT_API_KEY, never printed; the reply is scrubbed of it and the director scrubs every parsed value too. Returned info is normalised and
allowlisted: provider, model, status, wall_s, finish, usage, cost_usd, reservation, error. Nothing here has been called live yet (prices and limits UNVERIFIED)."""
from __future__ import annotations

import importlib.util
import json
import os
import re
import time
import urllib.error
import urllib.request
from collections import namedtuple
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("v5_ledger", ROOT / "scripts" / "image_trials" / "v5_ledger.py")
ledger_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ledger_mod)

API = "https://api.moonshot.ai/v1"
MODEL = "kimi-k3.1-pro"
PHASE = "P4"
LEDGER = Path("D:/kaggle_upload/v5_ledger.jsonl")
KEY_FILE = Path("D:/aai work/secrets/kimi/kimi_api_key.txt")
MAX_TOKENS = 32000
FINISH = {"stop", "length", "content_filter", "tool_calls"}
Agent = namedtuple("Agent", "name call secrets paid", defaults=(False,))


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None                                             # a 3xx becomes an HTTPError (recorded UNKNOWN); the key is never re-sent elsewhere


_OPENER = urllib.request.build_opener(_NoRedirect)


def load_key() -> str:
    k = os.environ.get("MOONSHOT_API_KEY", "").strip() or (KEY_FILE.read_text(encoding="utf-8").strip() if KEY_FILE.exists() else "")
    if not re.fullmatch(r"[A-Za-z0-9_.\-]{20,}", k):
        raise ledger_mod.Refused("no usable Kimi key")
    return k


def _post(path: str, body: dict, key: str, timeout: float) -> dict:
    req = urllib.request.Request(API + path, data=json.dumps(body).encode(), headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    return json.loads(_OPENER.open(req, timeout=timeout).read())


def make_agent(model: str = MODEL, effort: str = "high", ledger=None, key: str | None = None, post=_post, phase: str = PHASE, max_tokens: int = MAX_TOKENS, json_mode: bool = False) -> Agent:
    led = ledger or ledger_mod.Ledger(LEDGER)
    k = key or load_key()

    def call(system: str, user: str, max_tokens_override=None):
        stuck = led.unreconciled()
        if stuck:
            raise ledger_mod.Refused(f"{len(stuck)} earlier reservation(s) are unreconciled; reconcile them against the Moonshot dashboard first")
        mt = max_tokens_override or max_tokens
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        try:
            counted = int(post("/tokenizers/estimate-token-count", {"model": model, "messages": messages}, k, 120)["data"]["total_tokens"])
        except Exception as exc:
            raise ledger_mod.Refused(f"token count failed ({type(exc).__name__})")
        rid = led.reserve(phase, model, counted, mt, require_reconciled=True)
        info = {"provider": "moonshot", "model": model, "status": None, "wall_s": None, "finish": None, "usage": None, "cost_usd": None, "reservation": rid, "error": None}
        t0 = time.time()
        try:
            body = {"model": model, "reasoning_effort": effort, "messages": messages, "max_tokens": mt}
            if json_mode:                                               # only the probe exercises this (UNVERIFIED feature); scenes parse JSON from plain text
                body["response_format"] = {"type": "json_object"}
            data = post("/chat/completions", body, k, 900)
        except urllib.error.HTTPError as exc:
            led.unknown(rid, f"HTTP {exc.code}")                       # no status is assumed to be free
            return "", {**info, "status": exc.code, "wall_s": round(time.time() - t0, 1), "error": f"HTTP {exc.code}"}
        except Exception as exc:
            led.unknown(rid, type(exc).__name__)
            return "", {**info, "wall_s": round(time.time() - t0, 1), "error": type(exc).__name__}
        info.update(status=200, wall_s=round(time.time() - t0, 1))
        usage = data.get("usage") if isinstance(data, dict) else None
        usage = usage if isinstance(usage, dict) else {}
        if all(isinstance(usage.get(x), int) and not isinstance(usage.get(x), bool) and usage.get(x) >= 0 for x in ("prompt_tokens", "completion_tokens")):
            led.settle(rid, usage)
            info.update(usage={"prompt_tokens": usage["prompt_tokens"], "completion_tokens": usage["completion_tokens"]},
                        cost_usd=round(ledger_mod.cost(model, usage["prompt_tokens"], usage["completion_tokens"]), 6))
        else:
            led.unknown(rid, "no usage in reply")
            info["error"] = "no usage in reply"
        choices = data.get("choices") if isinstance(data, dict) else None
        choice = choices[0] if isinstance(choices, list) and choices and isinstance(choices[0], dict) else {}
        fr = choice.get("finish_reason")
        info["finish"] = fr if fr in FINISH else ("other" if fr else None)           # allowlisted: nothing free-form from the provider reaches the receipts
        content = (choice.get("message") or {}).get("content") if isinstance(choice.get("message"), dict) else None
        return (content if isinstance(content, str) else "").replace(k, "***"), info

    return Agent(model, call, (k,), True)


def probe(agent: Agent) -> dict:
    """ONE tiny paid call (a few hundred tokens, about a cent) to confirm that the model id answers; reserved and settled like any other call."""
    reply, info = agent.call("Reply with JSON only.", 'Return exactly {"ok": true}', 200)
    try:
        ok = json.loads(reply.strip().strip("`").removeprefix("json").strip()).get("ok") is True
    except ValueError:
        ok = False
    return {"model": agent.name, "answered_ok_json": ok, "finish": info["finish"], "usage": info["usage"], "cost_usd": info["cost_usd"], "error": info["error"]}
