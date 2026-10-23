# 45-second, 3-scene bilingual pilot: capability audit, blockers and shortest path (Phase A)

Date 2026-10-23. Evidence base: repository at 840dd6a (+ docs-only commits), `config/models.yaml`, the CPU suite (480 passed, 4 skipped), Kaggle attempts 1-6. Nothing below is a claim that a real model works unless it cites a run.

## 1. What exists and what has been shown

| Stage | State | Evidence / limit |
|---|---|---|
| Frozen architecture, manifests, Zero-DB scheduler, receipts, recovery logic, QA gates | IMPLEMENTED, CPU-TESTED | 480 tests; resume/fallback/recovery paths are tested on synthetic fixtures only |
| Research import (Markdown -> draft) and approval gate | IMPLEMENTED | `research/` in the repo is EMPTY; approval is a named human step; the importer never fills Marathi dialogue text (it must come from the printed edition) |
| Source material | EXISTS OUTSIDE THE REPO | `D:\aai work\adhyay_01\adhyay_01_analysis.md` (5 episodes, characters, places, 17 questions, most RESOLVED by you), `adhyay_01_FINAL_answers.md`, the printed PDF |
| Canon (characters, locations, props, terminology) | EMPTY BY DESIGN | 0 entries; canon comes only from approved research |
| Style | v1 ACTIVE and frozen (hash 2346c837...); v2 proposed on a separate branch | not touched |
| SDXL keyframes | **NOT OPERATIONAL** | no checkpoint, `identity_conditioning.method` null, `sdxl_keyframe.json` is an empty stub (0 nodes); O-006 undecided |
| LTX 0.9.8 image-to-video on a T4 | RUNS | attempts 4-6: decodable 768x512, 49-frame, 2.04 s clips, ~108 s sampling, ~2.5 min cold load, peak ~14.9 GB. Capability still `unvalidated`: scene survives but the camera pushes in (est. 1.2x-1.5x), human review NOT_DONE |
| Tier 0 FFmpeg stills/holds | IMPLEMENTED, CPU-TESTED | visual quality on real keyframes untested |
| Translation (Marathi -> Hindi) | **NOT OPERATIONAL** | `translation.status` unvalidated; IndicTrans2 version/licence/T4 fit open (O-007). A hand-written, human-approved Hindi script is a supported alternative path |
| Speech (Marathi and Hindi TTS) | **NOT OPERATIONAL** | `speech.status` unvalidated (IndicF5 named by the architecture, not set up); needs licensed/consented voice references. Imported (human-recorded) audio with a named reviewer is a supported alternative path |
| ASR check / forced alignment | **NOT OPERATIONAL** | `asr`, `aligner` unvalidated, no models chosen |
| Lip-sync | **NOT OPERATIONAL** | `lipsync.status` unvalidated, no runner, no validated style |
| Subtitles (SRT), audio assembly, final FFmpeg assembly, QA | IMPLEMENTED, CPU-TESTED | with synthetic test tones; real-model audio untested |
| Dual-T4 | gpu0 stage exercised; gpu1, concurrent, retry NEVER RUN | kept on hold |
| Real interruption/recovery on Kaggle | NOT RUN | journal/ownership logic is CPU-tested; the planned `retry` stage has not executed |

## 2. Blockers to the pilot, in dependency order (only what the pilot needs)

1. **B1 Source approval (human).** Pick the passage; the pilot cannot start from the Markdown alone. Candidate: **Adhyay 1 episodes 1-3, ovi 84-121** (leaf plates on the road -> the two observers test the stranger -> the feast at the door), three consecutive source-backed scenes, characters Devidas, Bankatlal Agarwal, Damodarpant Kulkarni and Gajanan Maharaj. Needed: import the draft, resolve its `_import` items against the printed text, verify the Marathi dialogue lines from the PDF, run `research approve` under your name.
2. **B2 SDXL stack (decision + download + validation).** Choose the checkpoint (licence) and the identity-conditioning method (or explicit `none` with reference images), after which I build the ComfyUI workflow, validate it on Kaggle, and generate keyframes and provisional reference sheets.
3. **B3 Audio stack (decisions).** Marathi speech, Hindi text and speech, ASR/alignment: choose either real models (IndicF5, IndicTrans2 and an aligner: versions, licences, T4 fit, voice consent) or the human routes (your approved Hindi script, human-recorded audio). The human routes keep the speech stage NOT_VALIDATED for models but let the film be finished.
4. **B4 Lip-sync.** Only if the approved passage has spoken dialogue and a model is chosen; otherwise NOT_TESTED (as you set).
5. **B5 Depiction (decision).** The source describes Gajanan Maharaj as "digambar" (almost naked) with an old vest in ovi 87-92. A reverent, modest visual treatment must be decided before any image of him is generated. The Gemini paintings show a generic young figure and are NOT Gajanan Maharaj; they can only be labelled provisional external assets.
6. **B6 Environment.** C: has 0.24 GB free (tests need free space there); D: has 9.6 GB. Clean up C: before the next long test run.

## 3. Shortest path (each step behind the normal gates: tests, Codex re-check, explicit commit pin)

1. You: approve the passage and name the person who approves it (B1); decide B5.
2. Me: import the draft, list the open items for you, prepare canon and the 3-scene shot plan (about 9 shots: LTX for 3-4 selected shots, Tier 0 for the rest), all CPU work.
3. You: decide B2 and B3 (including download approvals).
4. Me: SDXL workflow + validation run, keyframes and reference sheets (contact sheet for review).
5. Me: LTX clips for the selected shots on GPU 0 (and GPU 1 after a separate stage check), Tier 0 for the rest.
6. Audio: per B3; alignment and subtitles; lip-sync if applicable.
7. Assembly of both releases, QA, one real interruption/recovery test, review package, GO / CONDITIONAL GO / NO-GO.

Realistic expectation: B1-B3 are decisions only you can make; with them settled, the CPU steps are quick and the GPU steps are hours, not days. Without B2 the film cannot meet the "native SDXL" requirement; without B3 it can only be finished with human-supplied audio.
