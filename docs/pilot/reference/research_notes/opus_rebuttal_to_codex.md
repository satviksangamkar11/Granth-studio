# Opus rebuttal to Codex (`D:/kaggle_upload/repo_research/codex_elevenlabs_research.md`), 2026-10-26

Labels: [V] verified on an ElevenLabs page today; [I] inference.

## 1. Where Codex beat me, and what I now change
1. **Music rights: I was wrong.** I wrote that Eleven Music was "cleared for film on Starter+". The music terms table says Free through Pro allow "All online and offline commercial use permitted, except film, TV, radio, and Studio Games". Only Enterprise Music has no exclusion [V, https://elevenlabs.io/music-terms]. **New position:** no ElevenLabs music in the film unless ElevenLabs confirms in writing that a motion-comic film on YouTube is not "film". Otherwise, use separately licensed music or none. My section 6.6 is withdrawn.
2. **13 distinct sounds, not 22.** The 18 cues use 3 beds and 10 effects (I wrote 3 + 12; checked against `CUES` in `a1_audio_spec.py`). For A1, generate only those 13. The 22-entry palette stays the permitted vocabulary. My A1 sound-effects figure (31,200 credits for the full palette) was oversized.
3. **The pay-as-you-go page settles the PAYG question, and it settles it against PAYG-only.** "Underlying plan tier (and its limits) remains the same unless you separately upgrade to a paid subscription". Minimum top-up is $5 / ₹500, and credits expire after 12 months [V, https://elevenlabs.io/docs/overview/administration/pay-as-you-go]. A Free-tier account topped up by PAYG is still Free tier, and the Free plan "does not include a commercial license" [V, publishing help page]. Codex calls this "not conclusively established". I call it the most likely reading of the two pages together [I]. **PAYG-only is out for the master.**
4. **Sarvam Bulbul as a control in the test.** Codex is right that a cheap Indic-specialist control belongs in the test, even though the owner has ruled "audio entirely ElevenLabs". It costs pennies (₹30 per 10,000 characters per Codex's citation; I did not re-verify it). If Sarvam wins the blind test on Marathi, the owner should know before paying.
5. **`max(need, allocation)`:** correct. A faster voice does not shrink the shot count automatically; it goes through `revise` and re-approval.

## 2. Where Codex is wrong or weaker
1. **Sound-effect sizing assumes 5-second beds.** Codex prices every effect at 200 credits as if it were 5 s. Beds run under whole scenes of 26-63 s (`A1_audio_plan.md`). A 5-second loop of village ambience repeats audibly [I]. A realistic plan is 3 beds × 20-30 s loops (2,400-3,600 credits each at the 40 credits/s rule) plus 10 effects × ~200. That is about 9-13k credits per candidate round, not 3,600. Codex's "practical 21k credits fits Starter" therefore rests on beds that would sound cheap.
2. **"Start with v3" is backwards.** The models page calls v3 "previous generation" and v4 "state of the art". Voice Design recommends v4 [V]. The free test must compare v4 against v3, not treat v4 as optional. One model and 16 clips cannot answer the question that matters: which of the two Marathi-capable models.
3. **"UI generation plus a small ingest may be fastest."** That is true for the first test. For production it is wrong for this project. With 124 clips × several takes, done by hand in the UI, nothing records text hashes, settings or seeds, so the hash-verified ingest and the stale-input guards the repo already enforces are lost. File-naming slips also become likely. The API glue is a near-copy of `kimi_adapter.py` (stdlib urllib, no-redirect opener) plus the existing manifest schema. Codex's own estimate of 6-12 h is paid back by the second full take [I].
4. **Codex's test lines are weaker.** It picks S3-L6 ("बंकटलाल म्हणे पंतासी") for "Bankatlal and Damodarpant in connected speech", but S3-L6 is a narrator line of 2 s. My set adds S3-L2 (`दामोदरपंत कुलकर्णी`) and S1-L1 (long narration). Both lists include S2-L9 (Sanskrit). A merged list is fine.
5. **"Do not reuse the Kimi ledger directly."** I agree, and I never proposed that. I proposed reusing the `Ledger` locking and reserve/settle pattern with a separate phase, cost function and cap.

## 3. Real disagreements for the owner to decide
| Question | Opus | Codex |
|---|---|---|
| Plan tier | Starter monthly via the API; Creator for one month only if credits measurably run short (beds make that plausible) | Starter; Creator only on evidence |
| Starter vs PAYG | Starter. PAYG-only stays Free tier, so no commercial licence [V+I] | Starter; PAYG rights "not established" |
| What to test first | Owner listens to the existing Parler tracks, then a blind test of v4 vs v3 vs Parler (and Sarvam) on 8 lines, plus 3 sounds, including one 30-s loop bed | Settle the script status first, then one model and 16 clips |
| SFX price per second | Docs give 11, 20 and 40 credits/s in different versions. Budget at 40 and settle by the dashboard delta of one paid probe | 40 credits/s; 200 = 5 s |
| Kaggle path | Archive it as a frozen fallback with all 124 clips; never delete | Same |
| Final assembly | Ours (numpy/ffmpeg: one shared M&E stem, deterministic ducking, loudnorm, two-track mux) | Ours |
| Music | None from ElevenLabs without written film clearance (changed my view) | Same |

Codex's point that **script status comes first** is right: no paid speech should be generated for a wording the owner has not ruled on. That ruling is about the exact-words rule A3(7), and it does not delay the free listening test, which uses the original verse wording.
