**Sensible as a pilot; the measurements don’t yet establish GLM as the better writer.**

1. **Roles:** Keep the current meanings run. Blind-test both models on the same S1/S2 inputs and five narration samples before fixing roles. One permanent writer offers no proven advantage. **S4 needs another-model semantic review:** code validates IDs and timing, but cannot detect an invented action. Preserve D-018’s S6 review of scene cards **and shots**.

2. **Operational risks:** Two families can share misconceptions, especially when checking the same English interpretation. Check against original Marathi plus relevant context. GLM’s two-ovi timing does not predict full-Adhyay performance. Test streaming on long calls; it is [SSE-based](https://docs.nvidia.com/nim/large-language-models/latest/get-started/quickstart.html#streaming), but does not prove gateway timeouts disappear. Bound concurrency, back off on 429/503/504, and measure account limits; don’t assume keys multiply quota.

3. **Cheap tests:** Use five owner-verified passages covering negation, speaker ambiguity, names/numbers, miracles, and teaching. Seed errors: omitted clause, reversed cause, invented motive, wrong speaker, plausible-but-unsupported detail, misleading STAGING. Include correct controls to measure false alarms. Require every seeded factual error caught. Run one full-Adhyay S1/S2 and the longest expected scene. Simulate truncated JSON, timeout, and interruption/resume. Judge Marathi/Hindi aloud, separately for fidelity and naturalness.

4. **Concrete gaps:** High: [draft_source.py:239](/D:/aai%20work/granthstudio/scripts/source/draft_source.py:239) performs no character-model check; add it. High: [line 196](/D:/aai%20work/granthstudio/scripts/source/draft_source.py:196) omits speaker/context from checker input; include both. Medium: [line 237](/D:/aai%20work/granthstudio/scripts/source/draft_source.py:237) saves meanings only after all batches finish; checkpoint completed batches.

Require claim-level evidence, explicit uncertainty, printed-source verification, and owner-approved canon. Hindi drafting must respect the frozen Marathi-master/IndicTrans2 path or receive an approved revision.

Read-only assessment; no calls or recovery tests executed.