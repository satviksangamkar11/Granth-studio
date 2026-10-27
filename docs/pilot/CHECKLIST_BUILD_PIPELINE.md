# MASTER CHECKLIST: build the full fixed pipeline (corrected after the Codex review of 2026-10-27, `CODEX_CHECKLIST_REVIEW.md`). THIS is the one list; it merges `FINAL_ARCHITECTURE_PLAN.md` sections 6 (B1-B18, D1-D6) and 9 (K1-K14), `CHECKLIST_PROOF_SCENE_S4.md` and `CHECKLIST_REUSE_SHOT_PLANS.md`. Contracts: `PIPELINE_README.md`. Tick when done; never skip. "done" = the artifact exists and its test passes, NOT that the whole stage gate passes.
Order: baseline and decisions -> contracts and wiring (no model calls) -> prompts tested FREE -> assets -> animation and S4 proof -> delivery and freeze.

| # | Item and files | Who | Owner? | Done-test | Status |
|--:|---|---|---|---|---|
| **Decisions and baseline** |||||
| 1 | Record the owner's latest rules (`DECISION_LOG.md`, `docs/DECISIONS.md`) | Claude | yes | answers recorded | [x] |
| 2 | Reconcile superseded text: override banners on 6 plan files (done); `CLAUDE.md` "only code writer" line left for the owner to amend | Claude | yes (CLAUDE.md) | one current rule per topic | [~] |
| 3 | Inventory + hash + back up A1 data/media; capture BASELINE outputs (byte-for-byte list) BEFORE any migration | Claude | yes (disposal) | recovery copy + comparison list | [ ] |
| 4 | Rights route: Flow clean export, ElevenLabs effects and speech after cancelling, platform use; notes kept (owner said "all permitted", not yet verified) | owner | yes | recorded basis | [ ] |
| **Contracts, wiring (no model calls)** |||||
| 5 | `scripts/source/nemotron_code.py` (drafting tool: spec/out path allow-list, exact expected-file set, no partial writes, no Blender code) | Claude | no | `tests/test_nemotron_code.py` 12 pass | [x] |
| 6 | `scripts/pipeline/chapter.py` (chapter paths; A1 legacy map incl. catalog = binding) | Nemotron+Claude | no | `tests/test_pipeline_chapter.py` | [x] |
| 7 | `scripts/pipeline/approvals.py` (hash approvals, STALE, dependents; cycle result excludes changed) | Nemotron+Claude | no | `tests/test_pipeline_approvals.py` | [x] |
| 8 | `scripts/pipeline/caps.py` v2 (locked reserve / settle / UNKNOWN / reconcile, replayed state, threads test) | Nemotron+Claude | no | `tests/test_pipeline_caps.py` 7 pass | [x] |
| 9 | Nine structural schemas `schemas/*.schema.json` (`make_schemas.py`) | Claude | no | `tests/test_pipeline_schemas.py` 28 pass | [x] |
| 10 | Semantic validators + failing fixtures (duplicate/missing ovi, unknown line ids, foreign keys, end before start, asset role vs preset, live hash, beats/catalog provenance, shot_plan source+renderer fingerprints) | Nemotron+Claude | no | each repro fails before, passes after | [~] built: `validate_stage1.py`, `validate_assets.py` (+ frozen tests, 2026-10-28); still missing: canon/source-evidence, measured-clip comparison, schema provenance fields |
| 11 | Producer/consumer matrix: every file in the chain (source, research, script, bible, clips, jobs, catalog, sound palette + files, subtitles, mixes, render receipts, delivery receipts): schema, validator, command, input fingerprint | Claude | yes (contract) | matrix in `PIPELINE_README.md` section 2b, Codex re-check | [x] written, Codex re-check pending |
| 12 | Approval authority: who may write `approvals.json`; stage gates call `status()`; stale propagation blocks downstream | Nemotron+Claude | yes (each gate) | changed input blocks downstream use | [~] `gates.py` built + tested; still missing: the approval write path + wiring into stages |
| 13 | `--adhyay N` + chapter paths wired into the existing commands, A1 byte-identical vs the item-3 baseline | Nemotron+Claude | no | A1 identical; A2 uses data paths | [ ] |
| 14 | DROPPED by the owner (2026-10-28: remove the caps part). `caps.py` stays as built but is not wired into `kimi_adapter.py`; the existing ledger guards are unchanged | - | - | - | [-] |
| **Source, planning, assets** |||||
| 15 | Lock A1: rev9 split hash, EASY script, 52 core / 10 optional choice, 16 look questions, hashes (ONE batch) | owner | yes | `approvals.json` receipt | [ ] |
| 16 | Lock A2: printed-book source + the owner's EASY script (README section 3 format) | owner | yes | hashes approved | [ ] |
| 17 | Source/EASY checker (format, ids, both languages, speakers, glossary, ovi coverage, unfilmed ovis, state changes) - reports only, never edits | Nemotron+Claude | yes (meaning) | fixtures + real A1 script pass | [~] `check_script.py` built + frozen tests pass; real A1 script run + source receipts still to do |
| 18 | Stage 1 HIGH prompt builder (`stage1_prompts.py`: shared rule block, packet incl. both preset lists, per-call prompts per `STAGE1_RULES.md`) + NINE outputs + semantic validator (no script lines, no timings) | Nemotron+Claude | yes (contract) | forbidden/missing/claim fixtures fail | [ ] |
| 19 | Stage 1 tested FREE on A1 data (NVIDIA) vs real rev9 split and 59 jobs; scores recorded; A1 paid Stage 1 NEVER repeated | NVIDIA+Claude | yes (comparison) | scores in a receipt | [ ] |
| 20 | Owner gate before any new paid Kimi call; run only needed A2 Stage 1 groups after the cap gate | Kimi+owner | yes | one-call receipts; batch approval | [ ] |
| 21c | `stage1_shots` schema + validator: `preset` is an id from the preset index OR `NEED_NEW` with `need_new` {reason, class}; no invented preset names (replaces the free-text `preset_hint`) | Nemotron | no | unknown preset name fails; NEED_NEW without reason fails | [ ] |
| 21b | Stage 1 `canon_looks.json` (new/changed characters, places, props; look + source ovi + stated/inferred; known series data never redecided) + schema + validator (every entry cites an ovi in the chapter; no events/dialogue fields) | Nemotron | yes (images at the gate) | unknown ovi / missing stated-inferred flag / event text fails | [ ] |
| 21a | Stage 1 `voice_cast.json` (character -> saved voice id; recurring keep theirs; new character gets an unused saved voice) + schema + validator; save fixed voices to series data | Nemotron | yes (listening) | every speaking character has one voice; unknown id fails | [ ] |
| 21 | Versioned series data: characters by chapter state, places, props, voices, glossary, style; no A1 names in code | Nemotron+Claude | yes (canon) | grep finds no A1 names in code | [ ] |
| 22 | Sound pack: palette ids, hashed WAVs, ElevenLabs model/settings, credits, rights note, cue timing checked against BOTH speech windows, ducking rule | Claude+ElevenLabs | yes | hashed files + receipts | [ ] |
| 23 | Voice clips per line MR/HI: exact reuse key, credit reservation, interrupted-call recovery; Hindi labelled NOT_VALIDATED | Claude+ElevenLabs | yes (listening) | listening + credit receipts | [ ] |
| 24 | Shared beats: pauses, crossings, scene tails; both languages complete | Nemotron+Claude | yes (timing) | beats.json validates | [ ] |
| 25 | Image prompts/jobs built by code from approved data (`IMAGE_PROMPT_RULES.md`) | Nemotron+Claude | yes (briefs) | matches the 59 A1 job structure; fails on story notes / missing place / chip count | [ ] |
| 26 | Flow provenance: actual prompt hash, model, chips, edit id per chosen version; raw + clean hashes; dimensions; explicit chosen version | Claude | yes (selection) | catalog validates against live files | [ ] |
| 26b | Make the watermark cleaner AUTOMATIC (detect small + big star per image with a verification report; no per-chapter big-star list or learn image) | Nemotron | yes (corner check) | cleans all A1 images identically to today's output or better; report lists every corner | [ ] |
| 27 | Image review: first three per scene, rubric, contact sheet + exceptions; per-chapter watermark data; fix SH_S8_04 star | Flow agents+Claude | yes | exceptions list, chosen versions | [ ] |
| **Animation and proof** |||||
| 28 | Stage 2 LOW compact prompt + catalog/role/hash validator | Nemotron+Claude | yes | unknown id / role / hash / timing key fail | [ ] |
| 29 | Shot-plan files + exact-hash replay | Nemotron+Claude | yes (new plans) | same inputs: zero Kimi calls | [ ] |
| 30 | Bounded preset-03 JSON variants + three NEED_NEW classes | Nemotron+Claude | yes (each) | bounds + full-frame render pass | [ ] |
| 31 | Bind and approve S4 flat finals; decide the 3 staging warnings (daylight S4-1, pose S4-2, halo S4-4) | owner+Claude | yes | five files/roles/hashes accepted | [ ] |
| 32 | Test presets 05/06/07 with full frames; one real NEED_NEW (bow/blessing) | Claude(+Kimi) | yes | full frames + owner viewing | [ ] |
| 33 | Render + mix + subtitles S4 (both languages); interrupt/resume at shot level | Claude | yes | clean-run equality; complete speech | [ ] |
| 34 | Render + mix the remaining A1 scenes; capture render/GPU receipts | Claude | yes | owner accepts the film | [ ] |
| **Delivery and freeze** |||||
| 35 | Export Marathi MP4 and Hindi MP4 from ONE picture timeline (same frames, same length) | Claude | yes | frame/length equality; audio + subtitle inspection | [ ] |
| 36 | Per-chapter runbook (one page); housekeeping by explicit selection; backup | Claude | yes | a fresh session can run it | [ ] |
| 37 | A2 dry run through one rendered scene with data-only changes | Claude | yes | no diff under `scripts/` or `src/` | [ ] |
| 38 | `uv run pytest -q`, `uv run granthstudio validate`, captured results, recovery drill | Claude | no | output saved | [ ] |
| 39 | Codex read-only review (medium) of the diff, then a reviewed commit (never push, no attribution lines) | Codex+Claude | yes (release) | READY + commit | [ ] |

## Open Codex findings from the first review (CODEX_CHECKLIST_REVIEW.md section 4)
1 nemotron_code paths: FIXED (check_spec/check_out/exact_set). 2 caps: module FIXED (lock + states), integration = item 14. 3 approvals authority: item 12. 4 chapter A1 catalog: FIXED. 5 schema semantics: item 10. 6 approvals cycle: FIXED. 7 partial reply: FIXED (exact set).

## Progress log
- 2026-10-27: items 5-9 built (A1 untouched; new files only). Tests: nemotron 12, chapter, approvals, caps 7, schemas 28 all pass.
- 2026-10-28: Codex prompt review (CODEX_NEMOTRON_PROMPTS_REVIEW.md): all 8 prompts FIX FIRST -> system prompt updated, landed specs corrected, tests-first restored (Claude wrote frozen tests; Nemotron wrote code only). Four modules landed after Claude fixes of 5 defects the frozen tests caught (cycle/hash handling, missing 'no shots', unknown preset KeyError, gates reimplemented status). 120 tests pass. caps/approvals holes fixed (nested folder, duplicate open, invalid hash).

## STAGE 1 additions (Codex `CODEX_STAGE1_PLAN.md`, merged 2026-10-28; Nemotron writes all code and tests, Claude specs/docs, Codex reviews)
| # | Item | Who | Owner? | Done-test | Status |
|--:|---|---|---|---|---|
| S1 | `STAGE1_RULES.md` written (roles, story vs philosophy, calls, packet, shared block, rule migration, presets, sound, image lessons) | Claude | yes (contract) | file exists, README links it | [x] |
| S2 | New schemas `stage1_story_map`, `stage1_coverage`, `stage1_voice_cast`, `stage1_canon_looks`; extend `stage1_scenes` (section kind, teaching treatment) and `stage1_shots` (preset id or NEED_NEW + reason/class; no free-text hint) | Nemotron | yes | zero-story + missing-ovi + invented-preset fixtures | [ ] |
| S3 | Validators for the four new docs + extended ones: every ovi typed once and has one disposition; omissions listed with reason; voice ids exist in the saved cast; looks cite chapter ovis and stated/inferred; preset in the index or NEED_NEW | Nemotron | no | failing fixtures per rule | [ ] |
| S4 | `stage1_prompts.py` (code-built prompts, shared rule block, packet with both preset lists and the sound palette, image-brief lessons) | Nemotron | yes (contract) | forbidden output (script text, timings, invented ids) rejected | [ ] |
| S5 | Resolve A1 coverage evidence (rev9 receipt is NO_CHECK; ambiguous "narrator or omitted" ranges; 58-60 opening context) | Claude documents | yes | every disposition explicit in `approvals.json` | [ ] |
| S6 | Publish preset + sound packet: capabilities extracted from preset JSON; `canon/series/sounds/palette.json` with availability/provenance; add the female voice ids to series data | Nemotron | yes (new assets) | roles/availability verified | [ ] |
| S7 | `story_split.py` cannot fit a zero-story chapter (requires a story, treats commentary as unfilmed): add discourse sections + explicit coverage (no change to A1 results) | Nemotron | no | zero-story fixture passes; A1 split unchanged | [ ] |
| S8 | Update `HAIKU_FLOW_AGENT_BRIEF.md` + `FLOW_RUNBOOK.md`: remove mandatory three style chips, nullable place, newest-download guessing, accumulated A1 exceptions, stale effort wording; per-agent download folder; record actual prompt/model/references/edit id | Claude | yes (settings) | LOW effort, exact jobs, safe resume | [ ] |
| S9 | Sound defaults + ducking (union of both languages' windows) specified and listen-tested | Nemotron + owner | yes (listening) | gain/fade values recorded | [ ] |
| S10 | Nemotron cross-check of Stage 1 outputs (different family) wired as advisory | Nemotron | no | BLOCK/PASS per scene recorded, never auto-repair | [ ] |

## SOUND additions (Codex `CODEX_ELEVENLABS_SOUND.md`, 2026-10-28; Claude specs/docs, Nemotron all code and tests, Codex reviews)
| # | Item | Who | Owner? | Done-test | Status |
|--:|---|---|---|---|---|
| E1 | Sound rules in DECISIONS.md, STAGE1_RULES.md section 8, README section 10, decision log | Claude | yes | dated sound decision recorded | [x] |
| E2 | `canon/series/sounds/palette.json` (22 ids / 18 cues preserved from `a1_audio_spec.py`, statuses, no sourced audio yet) + schema + validator | Nemotron | yes (assets) | invalid id/status/missing evidence fail | [ ] |
| E3 | SFX generation in `a1_eleven.py` (mocked tests first): dedupe hash, ledger reservation, decode/hash, candidate + receipt, uncertain charge stops | Nemotron | yes (spending) | mocked requests, resume, ledger pass | [ ] |
| E4 | Timing: cue anchors resolved from measured bilingual windows ("after line" = after both) | Nemotron | yes (timing) | collision checks pass | [ ] |
| E5 | Mix: effects/beds layer + ducking against the union of both windows (12 dB / 100 ms / 300 ms proposed), loop seams, fades, peaks, speech samples unchanged, equal export lengths | Nemotron | yes (listening) | synthetic tests + owner listening | [ ] |
| E6 | Pack v1: generate NEED_NEW sounds once (start with the 13 sounds used by the 18 cues), owner listens, rights note + hashes + receipts, files copied locally | Nemotron + owner | yes | each file AVAILABLE with receipt | [ ] |
| E7 | Reconcile older docs (`CODEX_ONE_VIDEO_TWO_LANGUAGES.md`, `BRIEF_elevenlabs_restructure.md`, recording/CC-licence instructions): supersession notes | Claude | no | dated notes | [ ] |
| E8 | Optional later: owner-approved bilingual test of tags-in-speech vs separate effects | Claude + owner | yes | recorded verdict | [ ] |

## VOICE LIBRARY additions (owner 2026-10-28; Nemotron writes all code and tests)
| # | Item | Who | Owner? | Done-test | Status |
|--:|---|---|---|---|---|
| V1 | `scripts/pipeline/voice_library.py`: fetch the owner's saved voices + descriptions from the ElevenLabs account (list voices, no credits, key read at run time, injectable HTTP for tests), merge with `A1_eleven_voices.json` assignments, write `canon/series/voices.json` (voice_key, voice_id, name, gender, age feel, description, verified Marathi/Hindi, assigned_to, status); never prints or stores the key | Nemotron | yes (edit descriptions) | mocked-API tests; existing 4 voice ids unchanged; female voices added with their ids | [x] 2026-10-28: Nemotron wrote it, 24 tests pass; live read-only run wrote `canon/series/voices.json` (35 voices, 4 ASSIGNED, 35 with descriptions, 9 verified Marathi+Hindi, no key in the file) |
| V2 | `stage1_voice_cast` schema + validator v2.1: add `reason`; ctx gets the library (descriptions, gender, assignments); recurring characters must equal the library assignment; a new character may only take an unassigned voice or raise a question | Nemotron | no | recurring change fails; unknown voice fails; assigned voice reused for a new character fails | [ ] |
| V3 | Stage 1 prompt builder passes the whole voice library with descriptions to Kimi and the casting rule; saved assignments are written back to the library after owner acceptance of the clips | Nemotron | yes (listening) | prompt contains every voice description; assignment saved once, never changed | [ ] |

## SOURCE IMPORT additions (owner uploaded the Chapter 2 docx, 2026-10-28; ON HOLD: the owner said the docx is for reference only, 'leave it'; do NOT build I1-I3 unless the owner asks)
| # | Item | Who | Owner? | Done-test | Status |
|--:|---|---|---|---|---|
| I1 | `scripts/pipeline/import_canon_docx.py`: read the Audited Canon Edition docx (zipfile + XML only, no new dependency) into `canon/adhyay_NN/source/ovis.jsonl` (+ section id/title/context) and `research/packet.json` (characters, locations, objects/glossary); schema for both; refuse a deviating layout; use the row number as the ovi number and REPORT every printed-number mismatch (Chapter 2: ovi 118 and 129) | Nemotron | yes (confirm mismatches vs the printed book) | synthetic docx fixtures; real Chapter 2 file gives 148 ovis, 12 sections, 2 reported mismatches | [ ] |
| I2 | Owner supplies for Chapter 2: speaker/dialogue per ovi, unfilmed candidates, direction notes (Part 3 or a short file), and the EASY script (README section 3 format) | owner | yes | files present, checked by `check_script.py` | [ ] |
| I3 | Owner confirms against the printed book: Chapter 2 ovis 118 and 129 (printed number 119 in both) and approves the source hash (`approvals.json`) | owner | yes | approval receipt | [ ] |

