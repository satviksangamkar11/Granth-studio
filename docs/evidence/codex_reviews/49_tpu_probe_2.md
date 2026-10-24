Blocking issues remain in `scripts/kaggle/tpu_probe.py`:

- **BLOCKER — :51–58:** Deadline is checked only on `queue.Empty`. A child producing output continuously never times out, preventing step persistence and completion. Check the deadline every iteration.
- **MAJOR — :65–74:** After timeout, `p.wait(0.1)` can return `0`, incorrectly recording success. If it raises, the subsequent group kill has no reap. Preserve an explicit timeout result, kill the group, then reap the child.
- **MAJOR — :68–78, :106–117:** Launch/reader setup exceptions become `rc=-1`; callers continue and the script exits `0` with `finished=true`. Propagate infrastructure failures or track incomplete execution and return nonzero.

Verified closures: `PYTHONUNBUFFERED`, persistence after completed steps, nonzero exit for exceptions reaching the outer handler, and requiring `HW TPU`. Process-group creation/kill is present; cleanup remains incomplete as above.

Undefined `p` in `finally` is caught by its inner handler. Shell payloads tokenize and compile correctly. A partial line without newline leaves the pump blocked, but the consumer’s empty-queue timeout still works.

Read-only CPU mocks reproduced the deadline bypass and timeout returning `0`. No files changed, network accessed, or accelerators used.