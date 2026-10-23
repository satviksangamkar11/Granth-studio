**Four MAJOR issues remain at `6c6a43d`; do not authorize the pinned run yet.**

- **MAJOR — `scripts/audio_translate_test.py:91–95`:** Contaminated receipts are withheld, but `print(..., reason)` still prints the original secret-bearing error. An in-memory probe confirmed the exact synthetic token reaches stdout. Sanitize the reason before every output.

- **MAJOR — `src/granthstudio/translation.py:75`, `scripts/audio_translate_test.py:113,135`:** Candidates reach the workdir’s `translation_candidates.json` before contamination checking. A token returned as candidate text remains on disk even when exported evidence is withheld. Check before the first write. The notebook scan covers only `out`, missing this file.

- **MAJOR — `scripts/kaggle/build_audio_translate_notebook.py:33–35`:** Pip’s environment excludes names containing `TOKEN` or `SECRET`, but retains other credentials. A synthetic probe retained `HF_API_KEY`, `KAGGLE_KEY`, and `SERVICE_PASSWORD`. Use an explicitly permitted environment for installation.

- **MAJOR — `scripts/audio_translate_test.py:78–79,102`:** The git helper ignores exit status. A failing `git status` with empty stdout is treated as clean; an in-memory probe reached preparation after simulated exit 128. Require successful git commands and refuse execution on failure.

**Closed:** notebook syntax; six expected IDs with nonblank candidates and verified pinned identity; in-memory validation override and in-repository workdir refusal. The notebook now scans exported evidence before displaying it, but the broader secret finding remains open above.

Read-only inspection and in-memory probes only. No files changed, GPU, downloads, or network; full tests were not run.