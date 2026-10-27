# CHECKLIST: ONE picture track, TWO audio tracks (Marathi + Hindi), no separate videos (owner request 2026-10-27; always tick as done)

Owner rule for this job: Claude does NOT research; only Codex is asked (read-only, from the repo files it can read).

- [x] Question written for Codex (`CODEX_ONE_VIDEO_TWO_LANGUAGES_PROMPT.md`)
- [x] Codex run -> `docs/pilot/CODEX_ONE_VIDEO_TWO_LANGUAGES.md`
- [x] Answer relayed to the owner in plain words
- [x] Items it says to change in audio / timing / director contract / mix / delivery written here as TODO with owner/Claude tags
- [ ] Owner decisions from the answer recorded in DECISION_LOG.md
- [ ] HANDOFF.md + FINAL_PLAN.md updated if the answer changes the plan

## TODO items from Codex (answer in `CODEX_ONE_VIDEO_TWO_LANGUAGES.md`; verdict: YES, one picture track serves both languages)
- [ ] T1 owner: confirm EASY wording, voice performances, and whether the 10 OPTIONAL lines (not in the 59-shot timeline) belong in the film
- [ ] T2 Claude: rebuild + verify timing from the accepted clip hashes; owner approves shot count/timeline (Hindi longer in 35 of 62 lines; 52 core lines fit every scene's picture time; rule = each beat sized to the LONGER language + pause, shorter language rests in silence/ambience; never speed speech up)
- [ ] T3 Claude: director prompt + validator: pass shared beat ids, start/end windows, BOTH measured durations, lines crossing each cut; use approved EASY line ids (validator still expects verse substrings); owner reviews the contract
- [ ] T4 Kimi: direct ONE scene (Codex suggests S4: 5 shots, 3 crossings, Hindi ~1.3 s longer); owner approves before the rest
- [ ] T5 Claude: verify WAV export + `a1_voice.py mix`; fix final loudness (-22 dBFS after whole-track peak normalization is NOT established: measure the finished tracks); add shared beds/effects with checks against BOTH speech windows
- [ ] T6 Claude: separate selectable Marathi and Hindi subtitle tracks (no burned-in captions); language-neutral year '1878' if the owner approves
- [ ] T7 Claude: assemble ONE master: 1 video + 2 labelled audio + 2 labelled subtitle streams; owner tests the real destinations (MP4/MKV players, YouTube, WhatsApp support UNKNOWN); fallback = two delivery copies exported from the SAME picture master (not two films)
- [ ] T8 Claude + owner: one-scene interrupt/resume + listening test (render recovery is still TODO in the backlog)
