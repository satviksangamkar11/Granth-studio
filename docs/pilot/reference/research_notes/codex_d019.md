**Recommendation: keep D-018’s production approach and add a small source-fidelity layer from D-019. Do not adopt D-019 wholesale.** D-018 is ready for owner choices; neither proposal has evidence supporting production PASS.

This is a proposal review at repository HEAD `f196c38`. D-019 is untracked; no BASE/CANDIDATE pair was supplied. Existing pilot results are evidence of limited capabilities, not completed bilingual films.

**What D-019 adds that should survive**

- **Source-led structure.** Chapters may contain stories, teachings, invocations, or continuations. D-019 explicitly prevents forcing these into a standard plot. This matters already: Adhyay 1 contains substantial framing material and one continuous incident divided into editorial sections. [D-019:5](D:/aai%20work/granthstudio/docs/pilot/D019_PROPOSAL_FROM_OWNER.md:5), [chapter analysis:39](D:/aai%20work/adhyay_01/adhyay_01_analysis.md:39).
- **Story and teaching relationships.** Keep thread IDs, sequence, teaching references, and continuation status. These can be lists in one episode plan; they do not require separate “Director” systems. [D-019:11](D:/aai%20work/granthstudio/docs/pilot/D019_PROPOSAL_FROM_OWNER.md:11).
- **Coverage and closure accounting.** Every source span needs an explicit disposition and a link to the narration or visuals carrying it. A chapter boundary must not manufacture a story ending. D-018 starts with “approved text” but does not specify this accounting. [D-018:20](D:/aai%20work/granthstudio/docs/pilot/V5_FINAL_ARCHITECTURE_DRAFT.md:20).
- **Motion appropriate to meaning.** Expressive holds, staged pose changes, and narration-led philosophy are useful categories. Philosophy does not need invented conversations to create movement. [D-019:13](D:/aai%20work/granthstudio/docs/pilot/D019_PROPOSAL_FROM_OWNER.md:13), [motion modes:19](D:/aai%20work/granthstudio/docs/pilot/D019_PROPOSAL_FROM_OWNER.md:19).
- **Separate reusable art from episode content.** Style rules, character identities, location kits, and shot recipes have different purposes. Preserve those distinctions inside the existing pack/manifest approach.
- **Three meaningful gates:** source/editorial before new art, technical feasibility, and final visual/bilingual acceptance. These improve D-018 without requiring more approval documents. [D-019:25](D:/aai%20work/granthstudio/docs/pilot/D019_PROPOSAL_FROM_OWNER.md:25).

These strengthen requirements already present in the frozen baseline: factual provenance, marked artistic interpretation, global continuity, and shared bilingual visuals. [Frozen architecture:38](D:/aai%20work/granthstudio/docs/ARCHITECTURE_V3_1.md:38).

**Must-fix findings**

1. **HIGH — D-019 restores superseded production choices.**  
   Its missing-art API contradicts D-015’s owner-generated images/no project image API. Blender as sole renderer contradicts D-017’s simplest-renderer choice. Its new Kimi-written Blender compiler would replace or duplicate a frozen capability without demonstrating why that is necessary.  
   **Correction:** manual Flow/Nano Banana art; retain `motion.py`, `parallax.py`, and frozen Builder v2; default to JSON presets and zero Kimi calls. Any exception needs a demonstrated missing capability and explicit owner approval. [D-019:9–21](D:/aai%20work/granthstudio/docs/pilot/D019_PROPOSAL_FROM_OWNER.md:9), [D-015–D-017](D:/aai%20work/granthstudio/docs/DECISIONS.md:67).

2. **HIGH — the assumed approved corpus does not exist.**  
   The approval sheet is entirely pending; character, location, prop, and terminology registries have empty entries. The source work is not simply importing readable PDF text. Using your measured PDF finding, approximately **3,630 ovis remain outside the 38-ovi draft transcription; all approximately 3,668 still require approved coverage.**  
   **Correction:** add OCR/font-conversion, page/number mapping, proofreading, meaning review, and approval as explicit work. Start chapter by chapter. [Transcription method:3](D:/aai%20work/granthstudio/docs/pilot/OVI_84_121_TRANSCRIPTION_AND_SCENES.md:3), [approval status:1](D:/aai%20work/granthstudio/docs/pilot/SOURCE_APPROVAL_SHEET.md:1), [canon](D:/aai%20work/granthstudio/canon/characters.yaml:3).

3. **HIGH — existing source notes cannot safely become canon unchanged.**  
   Reproducible examples:
   - The transcription calls 84–121 “closed at both ends”; the chapter analysis continues the incident through water, teaching, departure, and a next-chapter promise. An excerpt ending is not proof of whole-story closure.
   - The analysis attributes ovi 113 to Bankatlal; the approval sheet explicitly leaves its speaker unresolved.
   - The analysis’s feast retelling retains “leaving only a little,” while its verification note flags the corrected reading as no craving for taste.

   **Correction:** resolve these against page evidence and record the approved reading once. If a speaker remains ambiguous, preserve the ambiguity through neutral narration. [Transcription:48](D:/aai%20work/granthstudio/docs/pilot/OVI_84_121_TRANSCRIPTION_AND_SCENES.md:48), [analysis:63](D:/aai%20work/adhyay_01/adhyay_01_analysis.md:63), [analysis:75](D:/aai%20work/adhyay_01/adhyay_01_analysis.md:75), [verification caveat:27](D:/aai%20work/adhyay_01/adhyay_01_analysis.md:27), [speaker uncertainty:21](D:/aai%20work/granthstudio/docs/pilot/SOURCE_APPROVAL_SHEET.md:21).

4. **MEDIUM — D-019 makes one owner maintain too many representations.**  
   Passage typing, understanding graphs, treatments, scene contracts, screenplay folders, performance packs, and multiple directors each create another consistency obligation. Its three editorial samples are useful tests; requiring three complete chapter-compilation exercises before visual proof is unnecessary.  
   **Correction:** one source ledger, one episode plan, existing pack manifests and receipts. Use source tags only where they affect an editorial decision. Test three short contextual samples as they become available. [D-019:11](D:/aai%20work/granthstudio/docs/pilot/D019_PROPOSAL_FROM_OWNER.md:11), [data tree/phases:27](D:/aai%20work/granthstudio/docs/pilot/D019_PROPOSAL_FROM_OWNER.md:27).

5. **MEDIUM — motion labels do not prove motion capability.**  
   Phase 1 demonstrated failed hand-raise tuning, successful preset reuse, and a slide/bridge first-frame defect. D-019’s head turns, blinks, folded hands, and hinged arms remain proposals. D-018’s restrained camera reference also conflicts with the current validator’s mandatory minimum zoom.  
   **Correction:** held poses and pose cuts first; use cuts around the known transition defect. Decide explicitly whether contemplative holds may bypass/amend the minimum-zoom rule. [Measured results:8](D:/aai%20work/granthstudio/docs/pilot/V5_PHASE1_TEST_RESULTS.md:8), [reuse:21](D:/aai%20work/granthstudio/docs/pilot/V5_PHASE1_TEST_RESULTS.md:21), [validator:56](D:/aai%20work/granthstudio/scripts/image_trials/v5_schema2.py:56).

**The real critical path**

Approved readable source → approved meaning, coverage and depiction → approved Marathi/Hindi narration → measured audio → owner art → preset rendering → bilingual assembly and review.

**The biggest risk now is owner editorial and image-production capacity.** Renderer replacement does not remove either workload.

Illustrative estimate: **1–2 minutes of proofreading per ovi alone means approximately 61–122 owner hours**, excluding OCR correction, difficult meanings, Hindi review, art, and film review. Measure a small batch before scheduling the series.

D-018’s inferred 3.5–6-second beats would imply approximately **100–343 shots per 10–20-minute episode** if applied throughout. These are shot counts, not unique-image counts. Long teaching holds and asset reuse are essential workload choices. [D-018:16](D:/aai%20work/granthstudio/docs/pilot/V5_FINAL_ARCHITECTURE_DRAFT.md:16).

**One merged plan**

The following caps are recommendations unless already approved.

1. **Source foundation and pilot lock.**  
   Deliver one page-linked Unicode source ledger for 84–121, approved Marathi/Hindi pilot lines, depiction decisions, and necessary canon entries. Include surrounding context for closure. Trial OCR/font conversion on 2–3 representative pages; measure correction minutes.  
   **Gate:** no unresolved discrepancy affecting the selected content; every pilot assertion traceable.  
   **Cap:** $0 model/API spend; one extraction trial before choosing the method.  
   **Owner:** proofread, settle interpretations, approve wording, costume/modesty, and voice route.

2. **15–18-second visual proof and reuse.**  
   One location kit, three shots, one restrained finishing treatment; then a second shot through image/text substitution without Kimi. Treat eight layers as an available recipe, not a minimum. Use held poses or pose cuts.  
   **Gate:** owner accepts density, identity, readable staging, seams, caption shaping and pacing at normal speed; reproduce from pinned inputs.  
   **Caps:** three image attempts per asset, then simplify; one render retry per shot; $0 Kimi by default.  
   **Owner:** make/select art and approve the look once. D-018 already supplies most of this proof design. [D-018:35](D:/aai%20work/granthstudio/docs/pilot/V5_FINAL_ARCHITECTURE_DRAFT.md:35).

3. **Approximately 60-second bilingual narrative pilot.**  
   One episode-plan file records ordered beats, source spans, thread/teaching IDs, closure, coverage disposition, artistic interpretations, audio anchors, assets and preset IDs. Keep it separate from strict existing schemas unless a small extension is approved. Use measured audio; manual sentence timestamps are acceptable.  
   **Gate:** both languages preserve meaning and complete speech; required gestures survive timing changes; source coverage is accounted for. Verify interruption/resume, corrupt-cache rejection, dependency invalidation, and backup restoration on the actual chosen path.  
   **Caps:** reconcile the **OPEN $0.328** first; retain D-015’s phase allocations and **$50 cumulative Kimi ceiling**, counting earlier spend. Voice trial: existing limit of two setup hours/two GPU-hours, then owner decision.  
   **Owner:** approve script/contact sheet, hear both voice samples, supply manual images, watch both finished versions. [Spend evidence:27](D:/aai%20work/granthstudio/docs/pilot/V5_PHASE1_TEST_RESULTS.md:27).

4. **First complete Adhyay, produced in sections.**  
   Approve the whole chapter’s source and plan before episode production. Every ovi receives a disposition; merged passages need an equivalence explanation, omissions explicit approval, and continuations remain open. Render/review the first 3–5-minute section before completing the episode; it becomes part of the episode.  
   **Gate:** acceptable source fidelity, pacing, image workload, render/rework cost and both language releases.  
   **Caps:** separate **+$40 Kimi authorization**; retain the proposed ≤10 minutes rendering per six-second shot as a test ceiling. Before new art, approve a chapter-specific image/hour budget from pilot measurements.  
   **Owner:** approve full coverage and both scripts, generate the capped missing art, then review both masters.

5. **Remaining 20 chapters, one at a time.**  
   Reuse accepted packs, poses, presets and receipts. Sample a multi-story passage and a philosophy-heavy passage before their first production use. Add capabilities only when an approved scene cannot be communicated with existing tools.  
   **Gate:** the same three gates per chapter; no series-wide batch GO from a short pilot.  
   **Owner:** approve source/scripts, new or changed designs, and final bilingual releases—not each intermediate machine file.

For phases 3–5, measure **combined review time for both language versions per shared finished minute**; use the existing 10-minute target. Exceeding it triggers simplification or rescheduling, never abbreviated fidelity checks. Source proofreading and manual art time remain separate measurements.

**Exact owner decisions, with recommendations**

1. **Which proposal governs?** Approve this merged scope: D-018 production plus D-019 editorial accounting. Explicitly retain D-015/D-017.
2. **Source preparation and approver?** Chapter-by-chapter extraction and proofreading; owner remains approver. Measure the first batch before committing dates.
3. **Coverage versus 10–20 minutes?** Target 10–20 minutes; protect story/teaching completeness. Approve faithful condensation explicitly; allow a documented duration exception rather than inventing closure or rushing speech.
4. **Look and format?** Test restrained papercut depth/finish; approve before replacing D-016. Use **16:9**, with vertical excerpts deferred. Reconcile the chosen pack with the separately sealed legacy [style canon](D:/aai%20work/granthstudio/canon/style.yaml:33).
5. **Motion and camera policy?** Held poses and pose cuts now; no hinge upgrade. Permit deliberate contemplative holds through an explicit narrow policy decision.
6. **Images, renderer and Kimi?** Owner-made art; simplest existing renderer; manual/preset planning first. Kimi only for a specifically approved planning need. No new compiler.
7. **Narration and captions?** Marathi master, owner-reviewed Hindi; matching-language captions in each release. Use manual timestamps initially; approve voice consent/licensing and pronunciation samples.
8. **Start authority, money and time?** Authorize phases 1–2 first. Name the backup destination and an owner-hours budget; retain existing monetary ceilings and separate full-chapter approval.

**Verdict: fix the source and scope blockers before production GO.** No files changed or tests/renders rerun; GPU, TTS, alignment and final-film quality remain unvalidated by this review.