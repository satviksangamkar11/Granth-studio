PASS — prior MAJOR is closed. The retry leaves the exception handler before logging, GC and cache release, retains no exception, and is used by `build_qwen21`.

The exact weakref regression and exhausted-retry check passed with Torch stubbed to prevent GPU access. No BLOCKER/MAJOR remains within this narrow re-check.

No changes, network or GPU use. Actual GPU recovery remains unverified.