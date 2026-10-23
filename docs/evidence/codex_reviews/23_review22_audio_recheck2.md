**Two MAJOR issues remain at `74819d2`; hold pinned-run authorization.**

- **MAJOR — `src/granthstudio/runners.py:39`, `scripts/audio_translate_test.py:135`:** Errors are truncated before redaction. A synthetic token followed by 480 punctuation characters leaves its final 17 characters in runner stderr; redaction misses that fragment, allowing it into stdout and the receipt. Redact before truncating, or suppress raw runner stderr.

- **MAJOR — `scripts/kaggle/build_audio_translate_notebook.py:34` and generated notebook:** The allowlist admits every `NVIDIA*`/`CUDA*` variable, including `NVIDIA_API_KEY` and `CUDA_SECRET`. These reach pip and the model. Enumerate the required variable names explicitly.

**Closed:** the `tr.run_json` guard precedes candidate/evidence writes; nonzero Git exits refuse execution. The original unrelated credentials are excluded. PATH, HOME, CUDA settings, HF_HOME, HF_TOKEN and PYTHONPATH remain available.

Read-only inspection and synthetic string probes only. Python probes stalled and were stopped; no full test pass claimed. No files changed, GPU, downloads or network used.