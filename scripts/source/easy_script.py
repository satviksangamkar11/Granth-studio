"""The owner's EASY spoken script (canon/adhyay_01/script/easy.md since 2026-11-01; the docs/pilot copy is the original of 2026-10-26): one reader shared by the director and the ElevenLabs runner.
Approved spoken wording = this file. The Granth verse stays the source of meaning (ovi numbers are kept per line); a changed file changes `script_sha256`."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT = ROOT / "canon" / "adhyay_01" / "script" / "easy.md"
HEAD = re.compile(r"^\*\*(S\d+-L\d+)\*\*")


def load_simple(path: Path = DEFAULT) -> dict:
    """{line id: {"mr": ..., "hi": ...}} from the markdown script."""
    out, cur = {}, None
    for ln in path.read_text(encoding="utf-8").splitlines():
        m = HEAD.match(ln)
        if m:
            cur = m.group(1)
            out[cur] = {}
        elif cur and ln.startswith("- Marathi: "):
            out[cur]["mr"] = ln[len("- Marathi: "):].strip()
        elif cur and ln.startswith("- Hindi: "):
            out[cur]["hi"] = ln[len("- Hindi: "):].strip()
    return out


def script_sha256(path: Path = DEFAULT) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def overlay(audio: dict, simple: dict) -> dict:
    """A copy of the audio plan whose lines carry `spoken_marathi` / `spoken_hindi` (the easy wording). Every line must have both; no silent fallback."""
    import json
    a = json.loads(json.dumps(audio))
    for l in a["lines"]:
        t = simple.get(l["id"])
        if not t or not t.get("mr") or not t.get("hi"):
            raise SystemExit(f"{l['id']}: no easy wording in the simple script")
        l["spoken_marathi"], l["spoken_hindi"] = t["mr"], t["hi"]
    return a
