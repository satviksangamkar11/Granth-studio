# CHECKLIST: full-pipeline architecture + lessons learned (owner 2026-10-27). Tick as done; never skip; reply to the owner only when the list is complete.

> **CURRENT OWNER RULES (2026-10-27) override any older text in this file:** the EASY script is the owner's only (Kimi never writes, edits or flags it); Kimi Stage 1 = HIGH effort, Stage 2 = LOW; delivery = TWO videos (Marathi, Hindi), same picture, same length (a multi-track master is optional); Nemotron drafts the next code, Claude verifies; Adhyay 1 Stage 1 is not repeated; 59 shots (not 61); Codex runs at medium effort. Master checklist: `CHECKLIST_BUILD_PIPELINE.md`; contracts: `PIPELINE_README.md`.


Owner asks, in his words: plan the whole architecture from what we built, reuse everything, fix all problems NOW so Adhyay 2-21 meet none; after Adhyay 1 the pipeline is FIXED (no new code to run it; only Kimi writes NEW animation); Kimi in two stages (stage 1 = everything for audio, images, scenes; stage 2 = animation); ElevenLabs + a reusable sound-effect preset pack, pipeline suggests the sound effects; analyse the IMAGE-GENERATION problems (prompting style, false positives in review) and remember them for next time.

## A. Research asks (all read-only, Codex)
- [x] A1 Opus 5.5 (medium) advice on reuse approach -> relayed (in this session)
- [x] A2 Codex GPT-6-Sol (high): full architecture + problems table + two-stage Kimi + libraries + sound pack + no-new-code + master checklist + owner decisions -> `CODEX_FULL_ARCHITECTURE.md` (done, 3,601 words)
- [x] A3 Codex GPT-6-Sol (high): IMAGE-GENERATION lessons (prompt style, what failed, false positives and false negatives in review, what to put in prompts / reference rules / checks so Adhyay 2+ do not repeat) -> `CODEX_IMAGE_LESSONS.md` (done)
- [x] A3b Opus 5.5 (medium, read-only) reviews the problem statement + BOTH Codex answers AFTER they finish: agree/disagree, gaps, simplifications -> `OPUS_ARCHITECTURE_REVIEW.md`
- [x] A4 Claude reads both, checks claims against the repo (no blind copy), merges into the plan

## B. Record
- [x] B1 lessons turned into a rules file the pipeline reads: `docs/pilot/IMAGE_PROMPT_RULES.md` (prompt template, reference-image rules, review rubric, known false-positive causes)
- [x] B2 FINAL_PLAN / HANDOFF / PIPELINE_ALL_ADHYAYS updated with the fixed architecture + two-stage Kimi + sound pack
- [x] B3 DECISION_LOG entries; owner decisions list from the Codex answer
- [ ] B4 memory updated (image lessons + architecture pointer)
- [ ] B5 reply to the owner: summary, list of owner decisions, next step

## C. Not in this job (stay in the other checklists)
S4 proof (`CHECKLIST_PROOF_SCENE_S4.md`), reuse build (`CHECKLIST_REUSE_SHOT_PLANS.md`), commit.

## Result
Merged plan: `FINAL_ARCHITECTURE_PLAN.md` (master checklist B1-B18, D1-D6, owner decisions). Rules: `IMAGE_PROMPT_RULES.md`. Pending in this job: B4 memory, B5 reply (done by this message).
