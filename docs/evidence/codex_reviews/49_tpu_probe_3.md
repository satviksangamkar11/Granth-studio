The three prior findings are closed in the code, but one new issue remains:

- **MAJOR — `scripts/kaggle/tpu_probe.py:60–75`:** Output EOF immediately triggers unconditional `killpg`, even if the child is still finishing normally. A child that closes stdout/stderr before completing is killed and recorded as `exit=-9, timed_out=false`. An in-memory POSIX mock reproduced this. **Required correction:** continue waiting for process completion under the deadline; kill remaining processes and reap during cleanup afterward.

No files changed, network accessed, or accelerators used. Real Linux process-group behavior was not executed; the reported Windows tests cannot validate that branch.