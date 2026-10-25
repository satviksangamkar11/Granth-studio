"""V5 money guard (D-015 section 6). The only path to paid Kimi calls.
- Input tokens are COUNTED by the provider's token-count endpoint for the exact payload (refuse if counting fails), plus a 10 % + 200-token margin;
  output is charged at max_tokens. That worst case is reserved on disk (flushed and fsync'd) BEFORE dispatch.
- Check-and-reserve runs under an exclusive interprocess file lock, so two runs cannot both slip under a cap.
- Refused if (phase committed + this reservation) > phase cap, or > $50 total. Committed = settled actual cost + open and UNKNOWN reservations in full.
- After a reply with usage: settled at the provider-reported usage. Any error, timeout or reply without usage: UNKNOWN, kept in full until reconciled
  by hand against the provider's usage page (no status code is assumed to be free). Append-only JSON lines."""
from __future__ import annotations

import json
import msvcrt
import os
import time
import uuid
from contextlib import contextmanager
from pathlib import Path

PRICES = {"kimi-k3.1-pro": (2.0, 10.0)}            # USD per million tokens (input, output)
PHASE_CAPS = {"P1": 15.0, "P2": 20.0, "P3": 15.0}  # Phases 0 and 0.5 are $0
TOTAL_CAP = 50.0
MARGIN = (1.10, 200)                               # counted input tokens x 1.10 + 200


class Refused(Exception):
    pass


def cost(model: str, input_tokens: int, output_tokens: int) -> float:
    pin, pout = PRICES[model]
    return input_tokens * pin / 1e6 + output_tokens * pout / 1e6


class Ledger:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock_path = self.path.with_suffix(".lock")

    @contextmanager
    def _locked(self):
        f = open(self.lock_path, "a+b")
        try:
            for _ in range(600):                       # wait up to ~60 s for another run
                try:
                    f.seek(0)
                    msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                    break
                except OSError:
                    time.sleep(0.1)
            else:
                raise Refused("ledger is locked by another run")
            yield
        finally:
            try:
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
            except OSError:
                pass
            f.close()

    def _state(self) -> dict:
        state = {}
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    e = json.loads(line)
                    state[e["id"]] = {**state.get(e["id"], {}), **e}
        return state

    def _append(self, entry: dict):
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
            f.flush()
            os.fsync(f.fileno())

    def committed(self, phase: str | None = None) -> float:
        total = 0.0
        for e in self._state().values():
            if phase and e["phase"] != phase:
                continue
            total += e["actual"] if e["status"] == "settled" else e["reserved"]
        return total

    def reserve(self, phase: str, model: str, counted_input_tokens: int, max_tokens: int) -> str:
        if phase not in PHASE_CAPS:
            raise Refused(f"phase {phase} has no money cap")
        if not isinstance(counted_input_tokens, int) or counted_input_tokens <= 0:
            raise Refused("input tokens were not counted")
        worst = cost(model, int(counted_input_tokens * MARGIN[0]) + MARGIN[1], max_tokens)
        with self._locked():
            if self.committed(phase) + worst > PHASE_CAPS[phase] + 1e-9:
                raise Refused(f"{phase} cap ${PHASE_CAPS[phase]} would be exceeded (committed ${self.committed(phase):.3f} + worst ${worst:.3f})")
            if self.committed() + worst > TOTAL_CAP + 1e-9:
                raise Refused(f"total cap ${TOTAL_CAP} would be exceeded")
            rid = uuid.uuid4().hex
            self._append({"id": rid, "time": time.time(), "phase": phase, "model": model, "counted_input": counted_input_tokens,
                          "max_tokens": max_tokens, "reserved": worst, "status": "open"})
        return rid

    def settle(self, rid: str, usage: dict):
        with self._locked():
            e = self._state()[rid]
            actual = cost(e["model"], int(usage["prompt_tokens"]), int(usage["completion_tokens"]))
            self._append({"id": rid, "status": "settled", "actual": actual,
                          "usage": {k: usage[k] for k in ("prompt_tokens", "completion_tokens")}})

    def unknown(self, rid: str, why: str):
        with self._locked():
            self._append({"id": rid, "status": "UNKNOWN", "why": why[:80]})
