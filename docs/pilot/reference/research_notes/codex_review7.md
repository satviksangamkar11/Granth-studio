NOT SAFE

- **MAJOR — [draft_source.py:198](/D:/aai%20work/granthstudio/scripts/source/draft_source.py:198):** `load_done` accepts identical drafter/checker values. Reproduced: review displays `OK [drafted by same, checked by same]`. Reject such rows; also validate the meanings pair independently of character overrides.
- **MAJOR — [draft_source.py:299](/D:/aai%20work/granthstudio/scripts/source/draft_source.py:299):** Characters model check still receives the entire Adhyay, defeating `--char-range` and retaining the reported token-exhaustion risk. Pass `char_ovis` here; retain whole-Adhyay `name_check`.

Tests could not run: system Python lacks PyYAML; virtualenv execution was denied. Both files are untracked, preventing patch-only comparison.