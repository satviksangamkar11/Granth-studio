# Spec: write ONE file `scripts/pipeline/caps.py` (replaces an older version). Style: `from __future__ import annotations`, standard library only, short docstring, no print, no network, nothing at import time.

## API (all spend state lives in ONE append-only JSON-lines file `spend_path`; one line per event; the state of a request is derived by replaying the lines)
- `class CapRefused(Exception)`.
- `load_caps(path) -> {"total": float, "stages": {name: float}}`: JSON {"total": number, "stages": {name: number}}; FileNotFoundError if missing; ValueError unless total is a finite number > 0 (bool rejected), stages a non-empty object, every stage cap a finite number >= 0 (bool rejected), and the stage caps sum to <= total (+1e-9).
- `check(caps, spent_by_stage, stage, worst_usd) -> float`: PURE. ValueError if worst_usd is not a finite number >= 0 (bool rejected). CapRefused if the stage is unknown, or sum(spent_by_stage.values()) + worst > total (+1e-9), or spent_by_stage.get(stage, 0) + worst > stages[stage] (+1e-9). Returns the stage's remaining budget after this request.
- `reserve(spend_path, caps, stage, worst_usd, rid, require_reconciled=False) -> float`: runs under an exclusive lock so two callers cannot both pass the same balance. Lock = create `<spend_path>.lock` with os.open(O_CREAT|O_EXCL|O_WRONLY); if it exists retry every 20 ms for up to 10 s, then raise CapRefused("locked"); always remove the lock in `finally`. Inside the lock: ValueError if rid is empty or already used; if require_reconciled and any request is open/UNKNOWN raise CapRefused; compute spent by replaying the file; call check(); then append {"id": rid, "stage": stage, "status": "open", "reserved": worst_usd} (create the parent folder if needed). Returns what check returned.
- `settle(spend_path, rid, actual_usd)`: ValueError if rid unknown, or its status is not "open", or actual_usd is not a finite number >= 0 (bool rejected). Appends {"id": rid, "status": "settled", "actual": actual_usd}. (Same lock.)
- `unknown(spend_path, rid, why)`: ValueError unless rid is "open"; appends {"id": rid, "status": "UNKNOWN", "why": why[:80]}. The reservation keeps counting. (Same lock.)
- `reconcile(spend_path, rid, actual_usd, note)`: only status "open" or "UNKNOWN"; ValueError otherwise, or actual invalid as above, or len(note.strip()) < 5. Appends {"id": rid, "status": "settled", "actual": actual_usd, "reconciled": note[:80]}. (Same lock.)
- `state(spend_path) -> {rid: {"stage", "status", "reserved", "actual"}}` replayed from the file ("actual" is None until settled; status is the latest one; a missing file gives {}).
- `spent(spend_path) -> {stage: usd}`: for each request the actual amount if settled, else the reserved amount (open and UNKNOWN count at the reservation). Missing file -> {}.
- `unreconciled(spend_path) -> list of rids` whose status is "open" or "UNKNOWN", in file order.
Use one private helper that reads and replays (tolerate a blank line; any other bad line raises ValueError). Do not keep the old `record` function.

## The tests it must pass (do not change them; the tests load the file by path with importlib)
FILE tests/test_pipeline_caps.py: see the tests described by the API above; the key behaviours are: reserved money counts immediately; settle replaces the reservation by the actual; duplicate ids refused; UNKNOWN keeps the reservation until reconcile (note >= 5 chars); require_reconciled refuses a new reservation while another is open/UNKNOWN; and 6 threads each reserving 0.6 against a stage cap of 1.0 give exactly one success and five CapRefused.

Reply with only: FILE: scripts/pipeline/caps.py followed by the code block.


CORRECTED 2026-10-28: create the spend folder before acquiring the lock; reject a second open event for the same id and any illegal transition in the replay; every reader (state, spent, unreconciled) uses the same validated replay; a crashed lock is never deleted automatically (the owner removes it after checking no run is active). The frozen tests are in tests/test_pipeline_caps.py.
