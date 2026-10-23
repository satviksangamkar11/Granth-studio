No blocking issue remains in `620e936`; a pinned SDXL GPU test run may be authorized.

- `scripts/kaggle/sdxl_first_test.sh:18–19`: defaults off; validation rejects values outside `0|1` before stage side effects.
- `scripts/kaggle/sdxl_first_test.sh:121–124`: fixed, quoted launch array prevents argument injection; opt-in appends exactly `--lowvram` and records it in `worker0/launch.txt`. The false `if` branch does not trigger `set -e`.
- Notebook and generator preserve scene 1’s default and explicitly override inherited `COMFY_LOWVRAM`.
- Pins, gates, port ownership, attribution, and failure handling remain unchanged.

No repository-visible compatibility conflict found. Pinned upstream source is not vendored, so compatibility and OOM relief remain GPU-test questions. Tests were read, not run; no saved execution evidence for the new test was found.