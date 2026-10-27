1. SUMMARY

Stage 1 should plan the exact story and important teachings around the owner’s locked EASY script.
Reuse D-018’s director roles and fidelity rules; D-019 remains a proposal.
Give Kimi both preset lists during HIGH-effort planning; reserve new animation JSON for Stage 2.
Build Flow prompts in code; Haiku agents at LOW effort generate images for owner approval.
This is proposed text for `docs/pilot/CODEX_STAGE1_PLAN.md`; nothing was saved or changed.

2. WHAT RESEARCH ALREADY EXISTS

`docs/pilot/DIRECTOR_PROMPT_CHAIN.md` records approved D-018 and its research sources:

- **Story editor, S1:** types every ovi and identifies events and continuations.
- **Episode director, S2:** chooses presentation, scene order, coverage, hook and ending.
- **Screenwriter, S3:** builds scene beats. Its original narration-writing assignment is superseded.
- **Cinematographer, S4:** maps beats to supported shots, assets and presets.
- **Validator, S5:** code checks coverage, references, quotations, IDs and feasibility.
- **Cross-check, S6:** another model checks source fidelity and storytelling; the owner resolves disagreements.

D-018 addressed invented facts/dialogue, missing coverage, unsupported miracles, repetitive presentation and teaching that becomes an invented scene. A1–A3 and their follow-ups replaced the original model selection, revision loops, audio route and dialogue wording.

`docs/pilot/D019_PROPOSAL_FROM_OWNER.md` proposes a source compiler, richer passage types, story/teaching graphs and a **Discourse Director** for philosophy. Its new compiler, renderer, style and code-writing assignments are not approved.

A1 practice was simpler: Kimi’s `a1_kimi_plan2` split, owner-directed edits in `canon/story_split_edits/A1_rev1.json`, code validation, then Nemotron review. Rev9 uses one story, nine scenes, 59 shots: **2,8,6,5,7,6,9,5,11**. It did not execute all six original roles as separate calls.

Evidence caveat: `canon/director_runs/a1_split_rev9/receipt.json` says `NO_CHECK`, awaiting owner hash approval. `MACRO_REVIEW.md` records malformed reviewer answers. Treat rev9 as the requested working baseline, but do not claim these files prove a passing cross-check or formal approval.

3. PHILOSOPHY VS STORY

Proposed explicit rule:

Every ovi receives one primary type: `STORY`, `TEACHING`, `PHILOSOPHY`, `INVOCATION`, `RECAP`, `PHALASHRUTI`, `OTHER`. Add passage tags for dialogue, devotion, description, metaphor, explanation and transition. D-018 supplies the original primary types; adding `PHILOSOPHY` and tags needs a recorded contract amendment.

Type does **not** decide omission:

- Film source-supported story events; never invent connecting events or closure.
- Keep teachings required by the EASY script, owner notes or the story’s meaning.
- For sustained discourse, use existing narration over approved typography, source-named symbols and contemplative holds. Typography is composited later, never generated inside illustration art.
- Preserve existing character speech where the script assigns it. Never fabricate conversations to animate philosophy.
- List every proposed omission with its reason. Only the owner approves it.
- If required coverage is absent from the script, code reports the gap to the owner; Kimi neither drafts replacement wording nor critiques the script.

Record types/events in proposed `stage1/story_map.json`; coverage in proposed `stage1/coverage.json`; treatment and line references in `stage1/scenes.json`; unresolved presentation questions in `stage1/questions.json`; hash-bound approval in `approvals.json`.

Every ovi needs one primary disposition: `VISUALISED`, `NARRATED`, `QUOTED`, `MERGED_EQUIVALENT`, or `PROPOSE_OMISSION`. Approved omissions require an owner receipt. Merges identify the covering lines/ovis; contextual references do not create duplicate ownership.

A1 confirms this approach: S2 keeps 94–96 with grain-picking; S9 keeps **all 138–142**, then readiness at 143 and departure at 144. Teaching is not disposable because it lacks action.

A1’s unfilmed ranges are **1–32, 33–38, 39–57, 58–69, 106–107, 145–146**. However, “narrator or omitted” and “narrator-only coverage” are ambiguous. Resolve each explicitly; 58–60 also supplies opening context.

4. STAGE 1 STEPS AND PROMPTS

Use separate chapter planning and scene calls, not one enormous response:

1. **Chapter map:** whole chapter; types, events, teachings and continuations. No scene prose or script drafting.
2. **Episode/coverage plan:** map plus locked script; story/discourse sections, dispositions and scene order. No silent omissions, forced hook or invented closure.
3. **Per-scene direction packet:** ordered scene card → shot plan → image briefs → new/changed looks → voice assignments → sound suggestions → questions. These are ordered tasks inside one HIGH-effort call per scene or bounded group. No final timing, media generation or animation code.
4. Code consolidates the seven contracted outputs, validates them, and checks chapter-wide consistency. Nemotron cross-checks; the owner approves. No automatic paid repair.

Chapter calls establish shared IDs and references; subsequent scenes reuse them. Existing script IDs and order remain immutable. If proposed scene grouping conflicts with script headings, report the mapping problem rather than renumbering lines.

The packet contains:

- `canon/adhyay_NN/source/ovis.jsonl`, `research/packet.json`, `script/easy.md`.
- Series entities, chapter states, glossary, approved style/sheets and image catalog.
- Saved voices, beginning with `canon/audio/A1_eleven_voices.json`.
- `assets/v5_presets/index.json`, `README.md`, and code-extracted capabilities/effects from each preset JSON.
- `canon/series/sounds/palette.json`, including availability and provenance.
- Owner direction, unfilmed decisions, previous ending and approved earlier outputs.

For A1 fixtures use `canon/packets/adhyay_01/`, rev9, `A1_rev1.json`, `docs/pilot/A1_full_script_simple.md`, `canon/bible/`, and `canon/drafts/A1_flow_shot_jobs.json`. Do not rerun paid A1 planning.

Paste this shared block into **every** call:

> Use only locked source, research and owner decisions. Cite chapter-qualified ovis for facts. Reuse registered IDs; report missing identities. Never invent events, motives, miracles, dialogue or closure. Reference immutable EASY line IDs; never write, edit, translate or critique their wording. Thoughts and unclear speech remain narrator material. Separate sourced facts from STAGING and inferred visual looks. Preserve required teachings and explicit coverage; only the owner approves omissions. Use supplied preset capabilities and sound availability; report NEED_NEW honestly. Output only this call’s schema. No timings, hashes, approvals, API calls or code.

Rule migration, using **D-018 document numbering**:

- Keep F1–F2, F4–F10; extend F8 for the approved `stated/inferred` look exception.
- Replace F3’s paraphrase permission with exact locked EASY wording by reference. Exact verse quotation still applies when presenting a verse quote.
- Keep T3–T5, T9, T12, T14, T18–T19, T21–T22, T24.
- Adapt T1–T2, T11, T15–T16, T20 to the actual source and locked script; do not force narrative devices on discourse.
- Replace T6–T8’s variable durations and constant-action demands with six-second renders, held poses and code-owned measured timing.
- T10 becomes a visual-note style rule, not narration drafting.
- T13/T23 cannot add refrains or spoken quotations absent from the script.
- T17 becomes a preference: supported narration may cross cuts without interruption.

`director_test.py` uses **different F/T numbering**. Migrate by meaning. Its `RULES`, `CAPS`, `SCHEMA_TEXT` remain an executable legacy scene contract, not the new Stage 1 contract.

Missing schemas: proposed `schemas/stage1_voice_cast.schema.json`, `stage1_canon_looks.schema.json`, `stage1_story_map.schema.json`, `stage1_coverage.schema.json`.

Extend existing schemas with section kind, teaching treatment, source claims, continuity, context references, disposition reasons/approval links, image state/reference requirements and sound anchor types. Voice casting needs stable character/voice IDs; looks need entity/state IDs, source ovis and `stated/inferred`.

5. HOW KIMI USES PRESETS

Animation names and roles, all from `assets/v5_presets/index.json`:

- `01_establishing_shot`: sky, mid, fx, fg.
- `02_environmental_parallax`: sky, far, mid, near.
- `03_slow_cinematic_push`: img.
- `04_character_entrance`: char, other.
- `05_bowing_prayer`: pose.
- `06_blessing_gesture`: pose.
- `07_character_reaction`: face.
- `08_emotional_closeup`: face.
- `09_dialogue_composition`: left, right.
- `10_object_hand_insert`: insert.
- `11_scene_transition`: scene_a, scene_b.

Stage 1 gives a preset hint and flat/cut-out requirements. Flat first; do not request layers automatically. Preset 06 cannot raise a lowered hand; 09 cannot lip-sync. Fixed halos/effects may conflict with fidelity—prose cannot disable them.

Stage 2 replays matching approved plans first; LOW-effort Kimi receives unresolved shots only. `NEED_NEW` means missing art, bounded JSON variation, or unsupported capability. New supported JSON requires validation, test render and owner approval; Builder v2 stays frozen.

Sound starts with `scripts/source/a1_audio_spec.py`: **22 proposed sounds, 18 cues**, not evidence of generated WAVs. Reuse an available, approved sound ID. Otherwise emit `NEED_NEW` plus description, purpose and symbolic anchor. ElevenLabs generates it once through the credit ledger; save settings, receipt, hash and rights note before adding it to the pack.

Recommended defaults: location bed for establishing/quiet shots; supported footsteps for entrance; cloth rustle for an actual bow; water/plate/pot effects for matching actions; silence or quiet bed for teaching/reaction. No automatic blessing chime, halo sound or transition whoosh. Defaults are suggestions requiring contextual checks, not mandatory effects per preset.

Code resolves scene/line/picture-event anchors from measured audio. Duck against both languages’ speech windows; preferably use their union for consistent mixes. Exact gain/fade values remain to specify and listening-test. No ElevenLabs music.

6. IMAGE BRIEFS: A1 LESSONS

Put these requirements inside the image-brief prompt, from `IMAGE_PROMPT_RULES.md` and `CODEX_IMAGE_LESSONS.md`:

- Approved flat-colour style, steady navy outlines, light hatching, warm palette, filled scene depth; one style anchor.
- Full chapter-state identity: age/build, face/hair, exact costume; accepted-sheet reference.
- Exactly the visible people, each once, with position, one action and gaze target.
- Accepted place and fixed features; critical prop and its state/material.
- Explicit framing, angle, foreground, subject size and screen directions across adjoining cuts.
- Preset slot, full-frame/layer need, safe crop, camera/caption room and approved light.
- Only on-screen facts: no narration, bracketed commentary or literalised comparisons.
- Exclude extra people, text, letters, inset frames, borders and modern objects.
- References: visible characters, mandatory place, one style anchor, central prop; at most one–two correct neighbours for a specific continuity fix.
- Do not prescribe a hand side unless source, approved direction or continuity requires it.
- Rewrite regeneration prompts completely; bounded local edits preserve sound composition.
- No seed assumptions or guarantee from model/count choice.

For A1 Maharaj, retain the accepted adult-youth identity, cropped hair, open frayed grey-white vest and short white hip cloth; never reduce it to “vest.”

**Code** builds final Flow prompts from approved briefs and series blocks. Missing structured fields today include light, prop state, preset/crop requirements, continuity, references and explicit on-screen/source separation.

Keep Haiku LOW effort, exact prompt execution, assigned tab/range, progress/resume, versioning, account/payment stops and no approval authority.

Update `HAIKU_FLOW_AGENT_BRIEF.md` and `FLOW_RUNBOOK.md`: remove mandatory three-style chips, nullable place, newest-download guessing, accumulated A1 exceptions and stale medium-effort wording. Use exact chip/title matching, separate download folders, 2K/x1 default, approved fallback, per-version actual prompt/model/references/edit ID and hashes. Download edits before renaming; inspect the whole image afterward. Haiku’s quick check cannot replace Claude’s full-size review and owner approval.

7. GAPS AND CONFLICTS

- **High — `story_split.py:30,163`:** requires a story and treats commentary as unfilmed. A zero-story philosophy chapter cannot fit honestly. Add discourse sections and explicit coverage.
- **High — `FINAL_ARCHITECTURE_PLAN.md:11,66`:** still assigns EASY drafting to Kimi; later decisions prohibit it. Remove superseded instructions.
- **Medium — same file:13:** contradicts required two-video delivery.
- D-018 exact-verse character speech was amended by A3 follow-up 8. Preserve exact owner EASY wording, not the obsolete universal verse test.
- Original two-round repairs, A3 one-repair allowance and current README no automatic retry differ; current one-call rule governs.
- Checklist item 18 still says five outputs; current contract has seven.
- Voice/look schemas, philosophy typing, explicit omission treatment and reusable/generated sound states remain missing.
- Sound defaults/ducking values are unspecified; female voice IDs are not in `A1_eleven_voices.json`.
- Claude code authorship is superseded: Nemotron writes all code/tests.
- D-019 does not authorize its compiler, style or Blender changes. No runtime/GPU acceptance is established by this review.

8. CHECKLIST TO MERGE

All proposed; Claude writes specs/docs, Nemotron writes code/tests, Codex reviews.

1. Reconcile authority — `docs/DECISIONS.md`, `PIPELINE_README.md`; Claude; owner: amendment; test: one current rule/topic.
2. Specify calls/rules — `DIRECTOR_PROMPT_CHAIN.md`; Claude; owner: contract; test: script never generated.
3. Add types/coverage — proposed schemas above; Nemotron; owner: omissions; test: zero-story and missing-ovi fixtures.
4. Add voice/look contracts — proposed schemas above; Nemotron; owner: listening/sheets; test: recurring identity stable.
5. Extend scene/image/sound schemas — existing Stage 1 schemas; Nemotron; owner: contract; test: invalid references rejected.
6. Build prompts/validators — `scripts/pipeline/validate_stage1.py`, proposed `stage1_prompts.py`; Nemotron; owner: no; test: forbidden output rejected.
7. Resolve A1 coverage evidence — `A1_rev1.json`, `approvals.json`; Claude documents; owner: yes; test: every disposition explicit.
8. Publish preset/sound packet — preset index, `canon/series/sounds/palette.json`; Nemotron; owner: new assets; test: roles/availability verified.
9. Build Flow jobs/provenance — `scripts/flow/build_shot_jobs.py`; Nemotron; owner: briefs; test: missing place/wrong chips fail.
10. Consolidate Haiku instructions — brief/runbook; Claude; owner: settings exceptions; test: LOW effort, exact jobs, safe resume.
11. Test timing/sound/recovery — `tests/test_validate_assets.py`; Nemotron; owner: listening; test: unequal speech, replay, unknown charge stops.
12. Record acceptance — `CHECKLIST_BUILD_PIPELINE.md`; Claude, Codex reviews; owner: gates; test: offline A1 fixtures and data-only A2, no paid A1 repeat.

9. EXACT PROPOSED DECISION TEXT

> **Stage 1 clarification, 2026-10-28 — proposed for owner acceptance:** Kimi Stage 1 runs at HIGH effort. It maps all ovis, plans actual stories and important teachings, then produces scenes.json, shots.json, image_briefs.json, canon_looks.json, voice_cast.json, sound_suggestions.json and questions.json. Add story_map.json and coverage.json for explicit typing and dispositions. Chapters may contain zero stories. Teaching uses the locked script, source-grounded images, typography or contemplative holds; no invented scenes or conversations. Only the owner approves omissions.
>
> The EASY Marathi/Hindi script remains exclusively the owner’s. Kimi references its lines without writing, editing, translating or critiquing them. Both preset lists accompany planning. Existing animation and sound assets are reused; unmatched requirements are NEED_NEW. New sound effects are generated once through ElevenLabs’ ledger and catalogued with hashes and rights notes. Stage 2 remains LOW effort, supported JSON only; Builder v2 remains frozen.
>
> Code builds Flow prompts from approved data using the A1 image lessons. Haiku image agents remain LOW effort; the owner approves images. Claude writes specifications/documentation; Nemotron writes all code/tests; Codex reviews read-only. No automatic paid retries, new cap amounts or repeated paid A1 Stage 1 are authorized. D-019 remains a proposal.