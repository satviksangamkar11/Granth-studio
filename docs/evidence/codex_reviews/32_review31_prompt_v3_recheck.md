No BLOCKER/MAJOR remains in `55d7d94`. The prior three findings are closed: names/aliases and bookkeeping are checked, Scene 1 and its manifest place the chilam in his hand, and sweep limits precede provisioning. No new research contradiction found. Bash quoting and the `|| … exit 2` failure path are sound under `set -euo pipefail`.

Two MINOR issues remain:

- **MINOR — `src/granthstudio/keyframes.py:157`:** Python `\w` excludes Devanagari combining marks. With alias `राम`, ordinary `विराम` incorrectly matches because the preceding `ि` is treated as a boundary. Include combining marks in name-boundary handling and add a regression.
- **MINOR — `src/granthstudio/keyframes.py:146`:** Bare `provisional` rejects visible descriptions such as “a provisional wooden shelter.” Restrict that check to bookkeeping context. `cannon` correctly avoids matching `canon`; snake_case rejection is intentional.

A pinned SDXL GPU experiment may be authorized; these issues do not block the current pilot descriptions.

Static inspection only. No test suite, GPU, downloads, network, or file changes; a brief local check stalled and was stopped without results.