Blocking issues remain:

- **MAJOR — `src/granthstudio/episodes.py:175`, `src/granthstudio/keyframes.py:250`:** Setting `voice_only: true` on an existing visible actor removes their visual identity and sheet requirements without rejecting their approved actions. For example, flagging Maharaj excludes him from visual character lists, while `keyframes.py:175` still inserts “Gajanan Maharaj sits…” from research into the prompt. The actor can therefore be drawn without identity references. **Required:** reject contradictory visible-action use of voice-only characters; add this regression case.

- **MAJOR — `scripts/pilot/build_pilot_project.py:55`:** Every generated canon entry receives `status: approved` without a named human. The provisional evidence string does not affect `Canon.require()`, which accepts that status. **Required:** ship entries pending; confine synthetic approval to temporary test fixtures.

- **MINOR — `scripts/pilot/build_pilot_project.py:47`:** `ref(90)` produces “printed page 10–11; PDF page 5,” dropping PDF page 6 despite the documented split. This appears twice in shipped research. **Required:** preserve both page ranges.

- **MINOR — `pilot/episodes/adhyay_01/mr.yaml:1`, `pilot/episodes/adhyay_01/hi.yaml:1`:** Standalone timelines lack provisional/not-canon labels. Readers must find the README to learn their status. **Required:** generate explicit draft notices in these files.

- **MINOR — `docs/pilot/STORAGE_READINESS.md:1`, `docs/pilot/MODEL_AND_DEPENDENCY_MANIFEST.md:16`:** Stale claims say nothing was deleted and no SDXL graph exists, contradicting the cleanup appendix and candidate graph. **Required:** distinguish the initial assessment from the current state.

The six Marathi/Hindi strings match the approval sheet, and shipped pilot data matches the generator. Visual additions cite surrounding ovis; modest framing is flagged artistic. Speaker, bilingual, audio/voice, and canon-digest checks remain intact. Candidate filenames match pins; its status remains explicitly unvalidated.

No files changed, GPU used, or models downloaded. Full tests were not rerun; HF API hash retrieval failed, so those hashes and historical cleanup execution remain independently unverified.