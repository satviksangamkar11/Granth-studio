Blocking issue remains.

- **MAJOR — `scripts/image_trials/nvidia_trial.py:163`: secret-free exception handling is incomplete.** `http.client.BadStatusLine` escapes this catch and includes the server’s raw status line in the traceback. A malformed status line containing key text therefore exposes it. Catch `HTTPException` and return a secret-free failure.

- **MINOR — `scripts/image_trials/nvidia_trial.py:282`: argparse can echo keys.** `check-key --key nvapi-…` prints the supplied key in “unrecognized arguments.” Scrub parser diagnostics before emitting them.

- **MINOR — `tests/test_episode_output_size.py:95`: odd-width regression remains missing.** The new fixture is **130×128**, so it cannot detect the original 65×64 rounding defect. Add an actual odd-width image and independent geometry comparison.

The original redirect, embedded-newline key, fallback, and decoded-secret image paths are corrected statically. The square-pixel filter fix has appropriate expression quoting; anamorphic-pad and still-geometry assertions were added. Status `0` stops key fallback; `probe` fails, `check-key` fails, and `run` records failure while continuing subsequent scenes.

Static review only; interpreter probes could not execute successfully. No matching saved test evidence found. No files changed, GPU, downloads, or network used.