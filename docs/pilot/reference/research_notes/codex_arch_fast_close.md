**A. Architecture review — sound core; NOT production-ready.** Keep the frozen renderer, held poses, shared artwork and audio-first editing. Ranked risks:

1. **BLOCKER — validation cannot establish fidelity.** [director_test.py:84](</D:/aai work/granthstudio/scripts/source/director_test.py:84>) accepts scene-valid citations outside a shot’s coverage, unregistered speakers/assets and unsupported staging; repairs escape semantic re-review. Run #2 demonstrates these gaps. **Smallest fix:** explicit capability/reference checks, claim evidence, shot-locked repairs, re-review and seeded failures with clean controls. Owner judgment remains necessary.

2. **BLOCKER — disconnected production contracts.** Director `S1-1` IDs fail [v5_schema2.py:41](</D:/aai work/granthstudio/scripts/image_trials/v5_schema2.py:41>)’s `SA` pattern; asset descriptions are not executable bindings. Packet hashes authenticate copies, not approvals. **Fix:** deterministic preset expansion and one film manifest linking chapter-qualified sources, canon IDs, assets, dependencies and separate owner approval records. Reuse existing manifest machinery.

3. **MAJOR — experimental outputs lack durable recovery.** [director_test.py:391](</D:/aai work/granthstudio/scripts/source/director_test.py:391>) overwrites runs; [v5_blender.py:100](</D:/aai work/granthstudio/scripts/image_trials/v5_blender.py:100>) deletes prior frames. **Fix:** immutable run directories, input/output receipts, approval invalidation and verified resume; test interruption on this actual route.

4. **BLOCKER — bilingual timing is unresolved.** The [approved plan](</C:/Users/Satvik/.claude/plans/elegant-doodling-dream.md>) allows independent language timelines, but one selectable-dual-audio film needs a common picture schedule. **Fix:** reserve sufficient coverage for both measured utterances at each beat; align picture-event SFX and captions separately. Two language edits are a different deliverable.

5. **BLOCKER — production provider/budget boundary is incomplete.** `--model` remains NVIDIA-only; [v5_ledger.py:19](</D:/aai work/granthstudio/scripts/image_trials/v5_ledger.py:19>) lacks P4’s $3 cap. **Fix:** one small provider adapter with normalized receipts, verified pricing/terms and reservation enforcement. Resolve production permission before generating final material.

**Over-engineered:** extensive prompt archaeology, three-model repeated comparisons, optional slow reviewers and a 24-item sound palette before one finished sequence. **Missing on this route:** integrated approval/dependency manifest, durable run history and proven bilingual finishing/recovery—not another orchestration framework.

**B. Fastest honest path**

Critical path: printed-source approval → combined coverage/omissions approval → Marathi narration lock → reviewed Hindi → validated voices and measured timing → shared picture schedule → approved storyboard → artwork/render batches → bilingual mix, captions and complete-film approval.

**Parallel:** assistant fixes contracts/validators/recovery and prepares cited narration; owner verifies Adhyay 2 and settles voice/provider decisions; compute tests voices on approved passages. After storyboard approval, owner draws subsequent batches while compute renders accepted artwork and assistant prepares captions/SFX.

Planning minimums, **not measurements**:

- Source/canon approval: **4–8 owner hours**.
- Combined plan and Marathi narration: **3–6 hours**.
- Every Hindi line, pronunciation and audio: **3–6 hours**.
- Artwork: assume **60–140 accepted assets × 20–40 minutes = 20–93 hours**.
- Final continuity, sound and bilingual approval: **4–8 hours**.

Owner artwork dominates. Measure accepted-image time immediately; Run #2’s 21 images/90 seconds would otherwise extrapolate to 140–280 images.

**Safely reduce, through an explicit A2 amendment:** start with one representative comparison scene, escalate only if inconclusive, retain unseen checks; reuse approved poses/crops where events remain clear; approve narration by scene with line citations; review all Hindi meaning once, then only changed lines after fixes; start with 2 ambience beds and 4–6 necessary effects.

**Never cut:** source/speaker/quote checks, causal events and teachings, approved omissions, complete Hindi semantic review, pronunciation listening, continuity, rights evidence, measured timing, recovery or final owner approval. STAGING labels alone, seeded-test success and forced runtime compression are hidden shortcuts.

At **2 owner hours/day**, budget **6–10 owner-days** for the first sequence and roughly **20–60** for completion, conditional on reuse, passing integrations and engineering availability; external permissions can extend elapsed time.

Three speed decisions: settle production provider, choose voice fallback after one bounded test, and approve a measured artwork budget/reuse policy.

Read-only assessment; no new tests, renders or external-term verification performed.