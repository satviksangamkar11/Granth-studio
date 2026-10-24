- **MAJOR — [docs/ARCHITECTURE_V4.md:143](</D:/aai work/granthstudio/docs/ARCHITECTURE_V4.md:143>):** The quality test lists audit categories but never defines failure, including an acceptable render-cost limit. This leaves the fallback trigger ambiguous. Define an explicit owner-recorded pass/fail decision and how each category affects it; retain separate approval for HyperFrames.

- **MAJOR — [docs/ARCHITECTURE_V4.md:116](</D:/aai work/granthstudio/docs/ARCHITECTURE_V4.md:116>):** P3 runs alongside P2 preparation, and P4 starts after P0, allowing pipeline expansion before the scene audit is approved. This conflicts with section 12 and D-014’s “no expansion” gate. Explicitly gate P3/P4 behind approval or define permitted prototype-only preparation.

Verified: JSON is valid; current SHA-256 matches `58a7107c…ff0a0b5`; `original_freeze` retains the old hash and tag; the freeze tag points to `818fe6bd396f954dfc77b6b49421da56e7821c91`.

No active Node/Chromium requirement or renderer bake-off remains. D-013’s historical wording is explicitly superseded by D-014. No further contradiction found in determinism, prerequisites, or compute placement. No files changed.