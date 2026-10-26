NEEDS FIXES

- **MAJOR — HANDOFF.md:21,43:** Commands are not executable as written in the documented PowerShell environment: `PYTHONIOENCODING=utf-8 python …` uses POSIX syntax; `< prompt.txt` is unsupported PowerShell input redirection. Supply PowerShell-compatible commands using `uv run`.

- **MAJOR — HANDOFF.md:21:** Warn that `director_test.py` makes live NVIDIA calls and overwrites existing scene JSON, `REVIEW.md`, and `receipt.json`; it has no resume or run-history preservation. Preserve Run #2 before rerunning. Its `--model` changes only the NVIDIA model name; Moonshot/Kimi requires separate provider and ledger integration.

- **MAJOR — HANDOFF.md:12,16,24:** The paid-call instructions omit mandatory safeguards: reserve worst-case cost before dispatch, reconcile the outstanding charge before further paid use, and stop on cap, timeout, or unreconciled charge. `v5_ledger.py` enforces historical P1/P2/P3 caps and $50 overall; it does **not** enforce the new $3 bake-off cap. State how that cap will be enforced.

- **MAJOR — HANDOFF.md:20,28:** Explicitly retain A1/A2’s “frozen is not source approval.” Packet manifests say this too. Identify source approval as a gate before voice or shot production; otherwise a fresh session could treat frozen research as approved canon.

- **MINOR — HANDOFF.md:28:** “Invented scenery/props … pass unless labelled `STAGING:`” misdescribes the implementation. `validate_scene()` checks neither provenance nor the `STAGING:` prefix; it merely warns when the staging list is empty. State the actual gap.

- **MINOR — HANDOFF.md:22:** “NEVER … read [keys]” conflicts with `load_keys()`. Specify that scripts may load credentials while assistants must not inspect or expose their contents.