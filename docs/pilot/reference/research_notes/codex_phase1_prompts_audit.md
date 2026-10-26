NOT SAFE

The normal completion path reserves money before dispatch, but the prompts, recovery behavior, and Phase 1 acceptance are not ready for approval. No files were modified, no credentials were inspected, and no model calls were made.

**BLOCKER findings**

1. **The reconcile-first gate is still closed.**  
   [kimi_adapter.py:49](</D:/aai work/granthstudio/scripts/source/kimi_adapter.py:49>) correctly refuses any open/UNKNOWN reservation. Reading the ledger by **latest record per ID** confirms:
   
   - Settled: **$0.857142**
   - Open: **$0.327824**, P1, ID `f9eb956d7f094fb69415e36b1070151e`
   
   **Required correction:** reconcile this reservation against the owner’s Moonshot dashboard. Do not clear it from an estimate.

2. **Reconciliation can disable the money caps.**  
   [v5_ledger.py:115](</D:/aai work/granthstudio/scripts/image_trials/v5_ledger.py:115>) accepts negative amounts, `NaN`, and infinity. An in-memory probe accepted `NaN`; subsequently, `committed + reservation > cap` evaluated false. Negative amounts similarly create artificial budget.
   
   **Required correction:** reject amounts that are not finite and nonnegative; require a meaningful reconciliation note. Add refusal tests.

3. **Shot-locked repair is not guaranteed, and its instructions conflict.**  
   [director_test.py:525](</D:/aai work/granthstudio/scripts/source/director_test.py:525>) requests a **full corrected scene** for scene-level errors. This permits unrelated shots, goal, turn, and image descriptions to change. Schema errors mentioning array paths and scene-wide material errors take this route.
   
   The targeted branch at [line 532](</D:/aai work/granthstudio/scripts/source/director_test.py:532>) requests a partial `{shots, images_needed}` object while the unchanged **system prompt requires the complete scene object** at line 335. A model following the higher-priority system instruction can therefore return something `splice()` rejects.
   
   **Required correction:** give repairs a consistent output contract and enforce unchanged content outside the identified repair scope. Scene-level uncertainty must not silently unlock the scene.

**MAJOR findings**

4. **Credential protection regresses previously reviewed safeguards.**  
   [kimi_adapter.py:39](</D:/aai work/granthstudio/scripts/source/kimi_adapter.py:39>) uses default `urllib` redirect handling. An offline probe confirmed that a cross-origin redirect retains the Authorization header.
   
   At [lines 79–80](</D:/aai work/granthstudio/scripts/source/kimi_adapter.py:79>), only literal key occurrences in raw content are scrubbed. A fake-key probe confirmed that Unicode-escaped content becomes the key after JSON decoding, and `finish_reason` can retain it unchanged in receipts.
   
   **Required correction:** refuse redirects, allowlist response metadata, and scrub decoded strings recursively before recording or forwarding them. This repeats concerns already documented in `codex_draft_source.md` and `codex_review9.md`.

5. **Part A — the prompt contract does not exactly match validation.**  
   References below are to [director_test.py](</D:/aai work/granthstudio/scripts/source/director_test.py>).

   - **RULES F1/F2, lines 315–316:** chapter-qualified refs and dialogue membership are stated correctly. Missing restrictions include the actual reference format limits and the minimum three normalized Marathi characters. “Exact words” also permits punctuation/spacing differences in code; state that explicitly.
   - **F3, line 317:** does not explicitly route **thoughts and not-clearly-spoken lines to the narrator**, as A3’s follow-up requires. Exact quotation alone does not establish that a character spoke it aloud.
   - **F4, line 318:** the prohibition against added miraculous causes is correct and reviewable through Q3/Q4.
   - **F5, line 319:** permits STAGING scenery, then forbids unnamed places/sky unless materials name them. Those instructions conflict with each other and the owner’s permission to propose neutral scenery for approval.
   - **F5 versus lines 220–224:** PACKET validation uses an unstated English-word membership test. A faithful description using a synonym can fail; an unsupported non-English term can evade that test. The prompt restricts PACKET to people/props/scenery, but code also accepts light/pose/camera.
   - **F6, line 320:** says *every text field* is capped at 300. Schema allows Marathi up to 600 and leaves fields such as `need_new_reason` without that cap. Required nonempty strings are not fully explained.
   - **F7, line 321:** promises consistent material **and look**. Code checks a small material vocabulary only; `main()` supplies an empty `prop_materials` map at line 687. Packet-fixed material, colour, and appearance consistency remain dependent on review.
   - **T1, line 323:** goal/turn are present and editorially reviewable.
   - **T2, line 324:** “shorter beats” is unresolved when every shot is exactly six seconds. Repeated presets and close-ups produce warnings, while the prompt phrases them as prohibitions. The reviewer does not explicitly check both numerical limits.
   - **T3, line 325:** held performance can be falsely rejected by motion vocabulary. For example, `performance: "smiling held pose"` describes a static expression but matches `smiling` at lines 178–180. State-based capability checks have not replaced this ambiguity.
   - **T4, line 326:** metaphor/sermon restrictions are judgeable, but are not explicitly mapped to the current reviewer questions.
   - **CAPS, lines 328–333:** six seconds, held poses, preset roles, declared/used images, NEED_NEW and transition names are substantially aligned. It should explicitly require **exactly** the preset’s role set and explain the image-ID pattern.
   - **SCHEMA_TEXT, lines 335–344:** missing constraints include consecutive unique shot IDs, single-digit scene IDs, image-ID length/character limits, duplicate-image prohibition, nonempty `images_needed`, and several nonempty-string requirements. It correctly excludes `used_in` and dialogue `paraphrase` through its exact-key contract.
   - **`build_prompt`, lines 347–365:** supplies the scene/range, registry, presets, ovis, continuity, final answers and glossary. Code does **not** verify that returned `scene_id` equals the requested scene; internally consistent `S9` shots can accompany scene 1’s range.
   - **REVIEW_SYS, lines 390–409:** Q2 demands **owner-approved** STAGING, although this call produces proposals and receives no approval records. Q5 rejects every NEED_NEW shot as undoable, tending to turn the intended UNRESOLVED result into REVIEW_BLOCKED. Q8 permits material left to narration, but there is no narration/disposition field documenting that choice.
   - **Both repair prompts, lines 526–533:** omit the additional content-preservation requirements enforced at lines 503–516. Even targeted repair receives the entire plan. Its partial-output/system-output conflict and full-scene escape are finding 3.

   **Required correction:** align these instructions and checks before paid use; add clean controls for supported held expressions and permitted STAGING.

   The harmful research permissions—minimal dialogue invention, reasonable inference, plausible features, spicy/no-moral instructions, mandatory lip-sync and emotion invention—are absent from the live inline prompt blocks. The exact word **`invent` does not occur there**; “no invented cause” is a prohibition.

6. **A skipped cross-check can still produce success.**  
   [director_test.py:595](</D:/aai work/granthstudio/scripts/source/director_test.py:595>) returns `VALID` with `reviewed=False` when `--reviewers ''` is supplied. `main()` can then exit zero. This contradicts A3’s “skipped check never passes.”
   
   `clean_review()` also accepts missing shot IDs and missing advisory answers despite REVIEW_SYS requesting every question. The wrong-speaker seed at [test_director_test.py:93](</D:/aai work/granthstudio/tests/test_director_test.py:93>) tests an **unregistered** speaker, not misattribution between registered characters—the failure earlier research identified.
   
   **Required correction:** return NO_CHECK when required review is absent; validate review references; include registered-speaker swaps in acceptance evidence.

7. **Resume does not authenticate the actual inputs.**  
   [director_test.py:688](</D:/aai work/granthstudio/scripts/source/director_test.py:688>) hashes `MANIFEST.json`, but never verifies the files it describes. Editing a packet file without updating that manifest does not invalidate resume. Changes to `build_prompt`, repair instructions, validator code, preset transforms or provider settings are also absent from the input fingerprint.
   
   Current packet hashes **do match**; the defect is the missing enforcement.
   
   **Required correction:** bind resume to verified consumed inputs, effective prompts/settings and relevant implementation/preset versions.

8. **Paid attempts are not checkpointed before the complete scene finishes.**  
   [director_test.py:574](</D:/aai work/granthstudio/scripts/source/director_test.py:574>) permits an extra generation after non-JSON output, independently of the one repair budget. Thus a scene can make **three director calls**.
   
   Scene output is saved only at [line 701](</D:/aai work/granthstudio/scripts/source/director_test.py:701>). A crash after settlement but before that write loses the answer and attempt history; resume can direct the scene again. `ThreadPoolExecutor.map()` also queues later scenes, which may continue while the main thread exits following another failure.
   
   **Required correction:** durably record attempts and completed paid responses, enforce the owner’s total round limit, and test interruption on this route.

9. **Provider failure metadata does not stop plan processing.**  
   [director_test.py:451](</D:/aai work/granthstudio/scripts/source/director_test.py:451>) parses content without checking `error`, HTTP status or finish reason. A response containing valid JSON but missing usage becomes UNKNOWN in the adapter yet can still receive reviews and be reported VALID. The next paid call refuses, but a one-scene run can finish successfully.
   
   **Required correction:** stop on ambiguous paid outcomes and unsuccessful/incomplete provider responses, preserving their evidence.

10. **Manifest acceptance is incomplete and dependency invalidation is defective.**  
    [director_run.py:120](</D:/aai work/granthstudio/scripts/source/director_run.py:120>) supplies in-memory helpers only. No production caller creates or persists the required film manifest; the runner also never calls `map_shot_ids()`.
    
    At [line 156](</D:/aai work/granthstudio/scripts/source/director_run.py:156>), approval checks compare only dependencies captured originally. A probe added a new dependency after approval and still obtained **APPROVED**.
    
    **Required correction:** connect and persist the required manifest, invalidate approval when dependency membership changes, and demonstrate h–k through the actual runner.

11. **The acceptance suite has not established the requested PASS.**  
    Four pure `test_director_run.py` tests passed in isolation; all six scoped Python files parse. Full tests were unavailable: Python 3.12 execution is permission-blocked; Python 3.14 cannot load the installed `jsonschema` dependency. The filesystem-writing tests were not run.
    
    Existing tests do not cover the failures above, actual interrupted paid-call recovery, or a wrong registered speaker. Earlier SAFE verdicts concern older, narrower implementations.
    
    **Required correction:** supply executed evidence for the corrected seeded suite, clean controls and h–k acceptance. Test existence is not execution evidence.

**MINOR findings**

12. **The controlling documents still describe superseded behavior.**  
    [HANDOFF.md:28](</D:/aai work/granthstudio/docs/pilot/HANDOFF.md:28>) and line 39 retain $3; this request sets **$1**. Sections 1/6 retain old CLI, overwrite and reviewer behavior. `DIRECTOR_PROMPT_CHAIN.md` retains character paraphrase, variable shot lengths and two repairs. A3 also requires outside references copied into the repository; that preservation work is still missing.

**Part B — research coverage**

`R` = `D:\kaggle_upload\repo_research`; `DP`/`SP` = its `director_prompts`/`story_prompts`. `DT` = `scripts/source/director_test.py`; `DR` = `scripts/source/director_run.py`. Related recommendations are grouped; status refers to implementation, not endorsement of historical alternatives.

| Consideration | Source file | Status | Note / first-call gate |
|---|---|---|---|
| Source-bound events; no added facts/causes | DP/ViMax/story_decomposition.txt; codex_d019.md | COVERED NOW — DT:315–319,390–398 | Core rule present; semantic review still required. |
| Reuse frozen research; final answers override earlier interpretations | codex_oneepisode.md; prior_work/adhyay_01_FINAL_answers.md | COVERED NOW — DT:357–365 | Includes Devidas-house correction. Frozen remains unapproved. |
| Printed Marathi authority; chapter-qualified references | codex_oneepisode.md; DP/REPORT.md | COVERED NOW — DT:62,142–151,197–208 | Printed-source approval remains a production gate. |
| Canonical character/place/prop IDs and aliases | DP/CineCrew/character_continuity_bible.txt; codex_arch_fast_close.md | MISSING | Speaker-name registry and local image IDs are partial substitutes. Phase 2 canon integration; h/i incomplete now. |
| Verbatim dialogue; narrator carries paraphrase | DP/CineCrew/critic_verification.txt E7; codex_audio_design.md | COVERED NOW — DT:197–210,316 | Thought/unspoken classification still needs correction before call. |
| **E1:** closed enum values | DP/CineCrew/critic_verification.txt:308 | COVERED NOW — DT:74,78,80,168–177 | Prompt must expose all constraints. |
| **E2:** null/required-field discipline | Same:309 | COVERED NOW — DT:65–90,135 | Nonempty restrictions need prompt alignment. |
| **E3:** unknown asset references | Same:310 | COVERED NOW — DT:174–190 | Local image bindings covered; global canon IDs missing. |
| **E4:** location versus character/prop typing | Same:311 | MISSING | No typed canonical asset registry integration. Phase 2. |
| **E5:** bounded shot durations | Same:312 | COVERED NOW — DT:329 | Adapted to fixed 6 s; no model duration field. |
| **E6:** separate attribution for multiple speakers | Same:313 | COVERED NOW — DT:75–76,197–210 | Per-line speakers exist; correct attribution needs owner/reviewer evidence. |
| **E8:** complete JSON/truncation handling | Same:315; codex_review9–11.md | MISSING | Provider finish/error checks and durable response recovery incomplete. **Block.** |
| Targeted repair, preserve unaffected shots/images | DP/CineCrew/critic_verification.txt; codex_best_director.md | MISSING | Splice works for targeted branch; full-scene escape and prompt conflict remain. **Block.** |
| Feedback re-check | DP/VideoClaw/critic_verification.txt, director_4/6 | COVERED NOW — DT:598–607 | Accepted reviewer repairs get re-reviewed. |
| Binary evidence, fidelity/doability blocking, storytelling advisory | outside_suggestion.md; codex_best_director.md | COVERED NOW — DT:390–429 | Current rubric is 8+2, not planned 14+2; no-review bypass remains. **Block.** |
| Purposeful, spatially explicit shots; framing/focal subject | DP/ViMax/shot_list_camera.txt; codex_best_director.md | PLANNED PHASE 2-3 — `scene_director_v2.md` | Goal/turn present; purpose and spatial guidance incomplete. Can wait. |
| Actual first/last compositions; preset-derived motion | codex_best_director.md; outside_suggestion.md | MISSING | DT:124 derives roles/zoom only, not compositions. Phase 1 g partial. |
| Fixed held poses; explicit capability fields; NEED_NEW unresolved | codex_arch_fast_close.md; codex_best_director.md | COVERED NOW — DT:46,73–74,176–180,258–262 | Regex false positives and reviewer Q5 conflict remain. **Block.** |
| Prop material/colour/costume continuity | DP/CineCrew/character_continuity_bible.txt; codex_arch_fast_close.md | MISSING | Material heuristic and Q6 partial; packet constraints not bound. |
| Macro S1/S2: causal chains, hook, question/payoff, ending, chapter seam | SP/REPORT.md; outside_suggestion.md; codex_oneepisode.md | PLANNED PHASE 2-3 — `macro_planner_s1s2.md` | Can wait for a scene test; Adhyay 2 planning needs its checked source. |
| Scene-local versus macro prompt separation | outside_suggestion.md; codex_best_director.md | COVERED NOW — DT:314–365 | Inline prompt is scene-local; versioned layers remain Phase 2. |
| Narration voice, exact refrains, teaching after stakes, sentence-aware cuts, callbacks | SP/REPORT.md; codex_audio_design.md | PLANNED PHASE 2-3 — `narration_writer.md`, `scene_director_v2.md` | Can wait; narration must precede final picture timing. |
| Re3/DOC/LongWriter/Dramatron plan-before-prose; avoid formulaic writing | SP/REPORT.md and saved prompts | PLANNED PHASE 2-3 — macro/narration prompts | Adapt ideas to fixed facts; no autonomous story expansion. |
| EQ negative criteria, clarity/engagement, audience comprehension | SP/EQ-bench/*; codex_best_director.md | PLANNED PHASE 2-3 — `reviewer_rubric_v2.json` | Current Q9/Q10 cover only part. |
| Shot grammar, widest-first, medium bridges, camera reuse | DP/VideoClaw/critic_verification.txt; outside_suggestion.md | PLANNED PHASE 2-3 — `scene_director_v2.md` | Preferences/warnings, not fidelity blockers. |
| Mandatory motion every second, variable short shots/climaxes | SP/REPORT.md; outside_suggestion.md | CONFLICTS WITH A DECISION | Rewrite for fixed 6 s held-pose renderer; current T2 still unresolved. |
| Harmful creative clauses removed | DP/ViMax/*; SP/ShortGPT/*; VideoClaw prompts | COVERED NOW — DT:314–344 | Absent from live inline instructions; automated phrase test missing. |
| Versioned prompts, hashes, rule-to-check mapping | HANDOFF §4; approved plan:39–48 | PLANNED PHASE 2-3 — seven `prompts/director/` deliverables | Directory absent. Resume fingerprint needs fixing now. |
| Exhaustive research adoption/drop map | Same; codex_handoff_audit.md | PLANNED PHASE 2-3 — `RESEARCH_MAP.md` | This review is not the missing versioned repository artifact. |
| Licence headers, commits, MIT/Apache notices | DP/REPORT.md; SP/REPORT.md | MISSING | Archive headers exist externally; adopted inline rules lack the planned provenance/NOTICE mapping. |
| MovieAgent, Anim-Director, Look-Before-Move: ideas only | Their DP files’ SOURCE headers | COVERED NOW — DT:314–344 | No verbatim unlicensed block identified in live prompts. Keep paraphrase-only policy. |
| Copy approved plan/research/licence references into repo | codex_handoff_audit.md; DECISIONS A3 | MISSING | Owner-directed preservation not completed. |
| Code-expanded schema-v2 render payload; bounded parameters | codex_arch_fast_close.md; approved plan:36 | PLANNED PHASE 2-3 — unified contract/preset expansion | No `render_payload` now; ID mapper has no caller. |
| One dependency manifest; separate approvals; stale invalidation | codex_arch_fast_close.md | MISSING | Helpers/tests partial; no persisted integration; dependency-addition defect. **Block under h–k acceptance.** |
| Immutable runs, verified resume, attempts/checkpoints | codex_local.md; codex_p1b.md; codex_review4.md | MISSING | File receipts exist; input/attempt/interruption gaps remain. **Block.** |
| Money reservation, lock, fsync, UNKNOWN retention, reconcile-first | codex_p1.md; codex_plan_review2–5.md | COVERED NOW — adapter:49–77; ledger:84–113 | Numeric reconciliation and concurrent reconcile-first gaps remain. **Block.** |
| Exact provider/prices; tiny JSON-mode probe; normalized receipts | codex_arch_fast_close.md; approved plan:10,22 | MISSING | Adapter exists; official rate evidence remains unverified; request omits `response_format`; default is not a tiny probe. |
| Secret scrubbing, malformed envelopes, finish/deadline handling | codex_draft_source*.md; codex_review4–11.md | MISSING | NVIDIA plumbing has prior fixes; Kimi repeats scrub/metadata gaps. **Block.** |
| Seeded factual errors plus clean controls; no checker claims from speed alone | codex_two_model_plan.md; codex_models.md | MISSING | Synthetic tests present, registered-speaker error and executed full evidence missing. **Block.** |
| Audio utterance IDs, citations, voices, statuses, captions, extension-safe coverage | codex_audio_design.md | PLANNED PHASE 2-3 — contract + `narration_writer.md` | Can wait; voices/translation remain NOT VALIDATED. |
| Common picture schedule from longer measured MR/HI utterance; no accelerated speech | codex_arch_fast_close.md; codex_audio_design.md | PLANNED PHASE 2-3 — bilingual mini-test/timing contract | Independent language-picture timelines conflict with A3. |
| Indic Parler first; pronunciation/duration tests; glossary-protected Hindi | outside_models.md; codex_models.md | PLANNED PHASE 2-3 — audio-first mini-test | Owner recording and mandatory per-line human Hindi review **DROPPED BY OWNER**; Hindi remains NOT VALIDATED. |
| Generous closed sound palette; symbolic verse/STAGING anchors | HANDOFF §4; approved plan:53–58 | PLANNED PHASE 2-3 — `sound_cue_rules.md`, `sound_palette.json` | Small starter palette superseded by A3 follow-up. |
| Deterministic cue compiler, bilingual resolution, rights, quote protection, music/bed/cue limits | Approved plan:54–58; audio research summarized there | PLANNED PHASE 2-3 — sound validator/compiler + mini-test | No free-text sound engineering; internal-word events need approved markers/alignment. |
| Cut-point foley, automatic pre-roll, preset envelopes, fixed loudness claims | Approved plan:56–58 | CONFLICTS WITH A DECISION | Explicitly not adopted; calibrate listening hypotheses later. |
| Image reuse, existing stills before new art, workload measurement | codex_best_director.md; codex_arch_fast_close.md | PLANNED PHASE 2-3 — reuse rules + bilingual still storyboard | Hard image limits dropped by owner; owner supplies all images. |
| Three-model bake-off, repeated/blind/holdout comparisons | codex_models.md; codex_best_director.md | DROPPED BY OWNER | A3 follow-up 3. Preserve ordinary quality checks; no comparison prerequisite. |
| Alternative directors, automatic GLM replacement, reviewer/cinematographer ensembles | outside_models.md; codex_models.md; outside_suggestion.md | DROPPED BY OWNER | Kimi directs; Nemotron cross-checks. |
| Per-ovi disposition ledger | DP/REPORT.md; outside_suggestion.md; codex_d019.md | CONFLICTS WITH A DECISION | Use planned scene/range coverage and owner-approved omissions. |
| New rigs/renderers, riso, generated animation code, image APIs | codex_findings*.md; codex_d018*.md; codex_d019.md | CONFLICTS WITH A DECISION | D-015–017: owner art, flat look, frozen builder, simplest existing renderer. |
| Builder exact hashes, runtime compatibility, bounded resources | codex_builder*.md; codex_v2.md; codex_local.md | MISSING | Historical reviews exist; this director route does not bind renderer/schema/font versions. Needed before rendering. |
| Frame deletion, disk preflight, decoded counts, backup restoration, actual render recovery | codex_p1*.md; codex_local.md; codex_plan_review2–5.md | MISSING | Later render gate; `v5_blender.py:100` still deletes frames. |
| Devanagari font pin/shaping, captions, phone-size QA, contact-sheet limitations | codex_d018.md; codex_findings2.md | MISSING | Later audiovisual/render acceptance; manual captions planned, exact font proof not supplied. |
| Watermark-mask approval, unchanged pixels outside mask, transparency edge checks | codex_wm.md | MISSING | Existing intake scripts named; their execution evidence is outside this review. Not first-call blocking. |
| Wan/LTX/FLUX/image generation, Cosmos, Docker/Vane | outside_models.md; codex_cosmos.md; codex_findings*.md | CONFLICTS WITH A DECISION | Dropped/deferred; no GPU/checkpoint validation claimed by this review. |
| Source approval, omissions, rights, owner film review; estimates versus measurements | codex_d019.md; codex_arch_fast_close.md; codex_handoff*.md | COVERED NOW — DT:618,708; HANDOFF:7–8 | Draft status retained. Film review remains NOT_DONE; no production approval. |

**Part C — Phase 1 acceptance, HANDOFF §5**

“Tests” below means coverage exists unless execution is explicitly stated.

- **(a) Dialogue inside its shot’s ovis — implemented.** DT:197–208; tests:97–100,128–137. Full execution unverified.
- **(b) Explicit pose/capability — partial.** DT:73–74,176–180. `held_pose`/`needs` exist; motion detection still has state-word false positives. Tests:85–92,140–146.
- **(c) Claim provenance/STAGING — partial.** DT:212–240; tests:61–70,101–115. Prefix and selected claims checked; provenance remains heuristic plus semantic review.
- **(d) Re-review repairs — implemented.** DT:598–607; tests:302–307. Full execution unverified.
- **(e) Shot-locked repair — partial.** DT:475–500; tests:189–210,324–328. Full-scene escape and conflicting prompts remain.
- **(f) Binary evidence/missing checks — partial.** DT:390–429; tests:234–253,331–334. `--reviewers ''` bypass remains.
- **(g) References/assets/frames/props/NEED_NEW — partial.** Reference and image-use checks implemented; tests:73–77,149–184. First/last output is roles/zoom only; packet-fixed appearance consistency incomplete.
- **(h) Builder ID mapping and bindings — partial.** DR:105–115; test_director_run.py:69–79. **Mapper test passed in isolation.** Nothing calls it from the runner; no render-payload expansion.
- **(i) One film manifest — not completed.** DR:120–161 has in-memory helpers. Three pure approval tests passed, but no actual film manifest is created on disk, no production caller populates it, and added dependencies do not invalidate approval.
- **(j) Immutable runs/resume — partial.** DR:26–101; tests:25–64. Input authentication, paid-attempt recovery and actual interruption tests missing. **`v5_blender.py:99–100` still deletes previous PNG frames.**
- **(k) Kimi adapter/P4 cap — partial.** Adapter:44–80; ledger:19,84–121; tests:124–204. **$1 is implemented**, superseding the documents’ $3. Cap/reconciliation/transport tests were not executed; defects above remain.

Consequently, “every seeded failure caught, zero false alarms, h–k accepted” is **not established**.

**Part D — first paid-call walkthrough**

Assuming a new `--run-name` is supplied:

1. `main()` parses arguments, imports `director_run`, and loads NVIDIA credentials for the cross-check. Missing NVIDIA credentials abort before Kimi initialization.
2. `--director kimi` requires `--allow-paid`; the adapter initializes Kimi. Default reviewer is Nemotron Ultra. Kimi remains the director on the normal default route.
3. The runner loads packet text, ovis and presets; defaults to scenes **1,4,6**. It creates/checks a run receipt, skips hash-verified scene files on resume, and checks other runs for previously saved directing results.
4. Paid scenes execute with **one worker**. Reviewers can run concurrently within a scene. This serialization is per process; it is not a global paid-call lock.
5. Before token estimation or completion, `call()` checks `unreconciled()`. **With today’s ledger it refuses immediately because of the $0.327824 P1 reservation.** No completion is dispatched. The runner records STOPPED and returns 2.
6. After legitimate reconciliation, the adapter estimates input tokens. Counting failure refuses dispatch. Reservation is:

   `0.32 + 2 × (floor(1.10 × counted_input) + 200) / 1,000,000`

   The **$0.32** is 32,000 output tokens at the code’s **$10/M** rate. Input uses its **$2/M** rate. These are configured rates, not independently verified provider billing evidence.
7. `reserve()` locks, checks **P4 $1** and **total $50**, appends the reservation, flushes and `fsync`s **before** `/chat/completions`.
8. This is a full scene request with `max_tokens=32000`, **not the planned roughly $0.01 probe**. It sends no `response_format`, so it does not exercise strict JSON mode.
9. Reported usage settles the reservation. HTTP errors, exceptions or missing usage retain an UNKNOWN charge. There is no adapter retry of the completion; however, the director pipeline retries non-JSON generation and may then make its separate repair call.
10. Code validates; Nemotron cross-checks; one accepted repair is checked again; the completed scene result is finally written. A crash before that write can lose settled-call output and permit repeated direction on resume.
11. The $1 limit does **not guarantee** three scenes plus repairs. Actual settlements release unused reservations, so affordable call count depends on usage. The old P1 reservation counts toward the global limit, not P4.
12. Every explicit `/chat/completions` dispatch in this adapter has a prior reservation. However, the reconcile-first check is **outside** the reservation lock: two processes can both observe a clear ledger and proceed. The cap lock protects arithmetic reservations, but not the global “stop while another charge is open” rule.

No paid run should proceed until the blockers and major defects above are corrected and the corresponding acceptance evidence is supplied.