**MAJOR — [open_edit_bench.py:134](</D:/aai work/granthstudio/scripts/image_trials/open_edit_bench.py:134>): the OOM retry retains failed-call tensors.**  
`last = exc` keeps the exception’s traceback and pipeline frames alive when the 384 attempt begins. `empty_cache()` cannot release those live tensors. A CPU-only weak-reference reproduction using the actual retry function confirmed this.

**Required correction:** detach the saved exception’s traceback, leave the exception handler, collect unreachable frames, then empty the CUDA cache before retrying. Add a behavioral regression that verifies the first attempt’s payload is released before the fallback starts; the current test only checks source strings.

Other checks:

- All four cells, nested HiDream script, and patched supplied `inference.py` compile correctly.
- Chain tuples, GPU assignments, and cache folder names are correct. Current literal deletion targets stay within intended caches and do not overlap between chains. The helper itself does not enforce containment.
- HiDream’s exclusions match the locally available older Transformers substring predicate, including nested custom-head paths. NF4 with those heads retained in bf16 is plausible; **the exact pinned 4.57.1 integration was unavailable locally**.
- Qwen’s resolution argument matches the supplied pipeline; `log` exists, and the run evidence confirms `torch.OutOfMemoryError` exists.
- Kontext remains bf16. FLUX 3 is excluded from execution.
- Four non-writing existing tests and the chain dry-run passed.

**Verdict: fix the retry before proceeding.** No files changed, network calls, or GPU work. Full pytest and successful corrected GPU execution remain unverified; the disk evidence establishes a read-only error, not its underlying cause.