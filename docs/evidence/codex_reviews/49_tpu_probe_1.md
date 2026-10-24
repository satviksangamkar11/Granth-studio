- **BLOCKER — `scripts/kaggle/tpu_probe.py:35–43`: Timeout can hang indefinitely.** Reading `p.stdout` blocks until a newline or EOF; the deadline is checked only after a line arrives. A silent JAX/XLA initialization hang prevents the fallback and final summary. `p.wait()` is also unbounded. **Correction:** enforce the deadline independently of output, including process waiting.

- **MAJOR — `scripts/kaggle/tpu_probe.py:33–46`: Cleanup can leave TPU processes alive.** With `shell=True`, `p.kill()` targets the shell; its Python child can survive and retain the TPU or stdout pipe. Exception handling also leaves spawned processes running. The proven runbook explicitly requires process-group cleanup. **Correction:** terminate and reap the entire process group on timeout/error and clean up remaining descendants after completion.

- **MAJOR — `scripts/kaggle/tpu_probe.py:78–85`: Fatal failures report successful exit.** Even an unexpected exception recorded as `"fatal"` ends with `sys.exit(0)`. Summary writing occurs only at completion, so a hang or external termination leaves no summary. **Correction:** persist step results as they finish and return nonzero for fatal/incomplete execution; distinguish a completed negative XLA diagnosis from probe failure.

- **MAJOR — `scripts/kaggle/tpu_probe.py:60–70`: XLA success does not establish TPU execution.** Any working XLA backend makes the boolean true; the code never verifies its device type. A CPU backend can therefore skip the fallback and appear successful. **Correction:** record the actual backend and require TPU execution for TPU success.

Quoting checks passed: all three generated `python -c` payloads tokenize correctly and compile, including their single quotes. There is no heredoc. Parent log writes flush immediately, but child Python output can remain buffered; use unbuffered child execution for live diagnostics.

The default separate venv and its explicit pip path isolate installs from base packages. Unsetting `TPU_LIBRARY_PATH` for both runtime checks matches the runbook.

Read-only CPU checks only; no network, accelerators, or file changes. Real Kaggle execution remains unverified.