**Not PASS yet.** `author` does not execute generated code, and the revised ledger addresses the prior reservation, locking and UNKNOWN findings on inspection. Two author-step MAJORs remain:

- **MAJOR — attempts are not durably counted before dispatch.** [v5_shots.py:182](</D:/aai work/granthstudio/scripts/image_trials/v5_shots.py:182>) calls Kimi before saving generation state. Timeout, missing Python block, or interruption leaves counters unchanged; repeating `author` permits more paid calls. Persist an author-attempt marker and counters under a lock before dispatch; retain them on failure.
- **MAJOR — incomplete author output reports success.** [v5_shots.py:198](</D:/aai work/granthstudio/scripts/image_trials/v5_shots.py:198>) accepts missing/duplicate shot IDs and returns zero even with invalid shots. Require exactly one validated SA, SB and SC; preserve failed output but report failure.

Separately, before **`run`**:

- **BLOCKER — generated builder approval remains outstanding.** [v5_shots.py:214](</D:/aai work/granthstudio/scripts/image_trials/v5_shots.py:214>): complete the full builder review and obtain the owner’s yes before creating the hash-bound approval. The AST guard remains insufficient as a sandbox.
- **MAJOR — storage/output verification remains incomplete.** [v5_blender.py:92](</D:/aai work/granthstudio/scripts/image_trials/v5_blender.py:92>): no disk preflight, PNGs accumulate across chunks, and encoder success substitutes for decoded frame counts. Implement the approved storage rule and verify 48 frames per chunk and 144 in the final clip.
- **MAJOR — revise has the same recovery gap.** [v5_shots.py:273](</D:/aai work/granthstudio/scripts/image_trials/v5_shots.py:273>): persist attempts before dispatch, with concurrency protection.

Read-only inspection completed; no paid call or Blender execution. I could not independently rerun the reported 39 tests in the available environment.