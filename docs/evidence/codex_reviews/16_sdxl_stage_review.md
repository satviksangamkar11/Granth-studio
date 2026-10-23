Blocking issues remain; **do not authorize the pinned GPU run yet.**

- **MAJOR — `scripts/kaggle/sdxl_first_test.sh:33,154`: stale success survives failure.** `$OUT` and the workdir’s receipt/outputs are reused without clearing them. After a successful run, a wrong-commit refusal republishes the old PASS receipt/images beside the new refusal log. An exception before `finish()` can likewise copy an old receipt. **Required:** invalidate prior results at invocation start and publish a fresh final stage verdict incorporating client exit and GPU attribution.

- **MAJOR — `scripts/sdxl_first_test.py:180`: direct execution bypasses safeguards.** The reused gate checks approver, host and deadline, but never checks `LTX_EXPECTED_COMMIT`, checkout cleanliness, actual node-pack commit, port ownership or worker CUDA isolation. `--worker-pid` and `--cuda-visible-devices` are merely recorded. A different server can receive submissions while the receipt names the requested GPU/pins. **Required:** enforce these checks at this executable entry point.

- **MAJOR — `scripts/kaggle/sdxl_first_test.sh:71,72`: extra node packs remain enabled.** Only ComfyUI and IPAdapter are checked; startup does not restrict custom-node loading to the approved inventory. Additional ignored packs in a reused checkout can execute or override classes. **Required:** reject extra executable packs or explicitly restrict loading to verified packs.

- **MAJOR — `scripts/sdxl_first_test.py:94,137`: temporary approval confinement is unenforced.** An existing project is trusted, including configured canon/research paths. Pointing those paths at repository files makes runtime approval write there; changed workdir research is automatically approved under the owner’s name. **Required:** enforce resolved path confinement and verify reused project content against the authorized pilot before approving it.

- **MINOR — `scripts/kaggle/build_sdxl_notebook.py:44`: early-refusal ordering is incomplete.** Package downloads happen before the shell’s GPU/RAM/disk/media checks. **Required:** perform those refusals before installation.

Checks passed: in-memory pruning for contiguous 0–5 references, rewiring, removed-LoadImage refusal, unchanged graphs without slot metadata, Python syntax and diff whitespace. Pinned-file mismatches abort; identical-control bytes correctly fail. Authorization wording does not claim licence acceptance; the painting remains explicitly external, and PASS leaves likeness/style awaiting human review. Review-15 generator fixes are present.

No files changed, GPU used or downloads performed. Full tests and live compatibility were not rerun.