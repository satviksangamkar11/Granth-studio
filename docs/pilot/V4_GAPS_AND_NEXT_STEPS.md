# GranthStudio v4: gaps and next steps (Codex review, 2026-10-24) — KEPT ASIDE, not acted on

Status: independent review by Codex of ARCHITECTURE_V4 (incl. D-014), the P1 Blender scripts and gemini_test.py. The owner asked to keep this aside; no change was made because of it. Findings are unverified until fixed and re-reviewed. Prices, terms and provider capabilities remain unverified.

**Verdict: NOT PASS for P1 acceptance or production readiness.** The Blender 2.5D direction is plausible, but acting quality, recovery, affordability and bilingual correctness remain unproven. D-014 correctly blocks expansion until the owner approves P2.

Reviewed the requested documents, scripts, `6265c33...d4bffd8`, and local trial receipts. The v4 checksum matches its freeze receipt. D-013’s renderer bake-off is historical and explicitly superseded by D-014; it is **not** a remaining contradiction.

**Architecture gaps and contradictions, ranked**

1. **BLOCKER — Source approval does not yet connect to P2.**  
   [v4:40](</D:/aai work/granthstudio/docs/ARCHITECTURE_V4.md:40>) requires approved research and forbids unsupported gestures; [v4:106](</D:/aai work/granthstudio/docs/ARCHITECTURE_V4.md:106>) commissions a blessing scene without naming its approved ovi, beat or depiction receipt. The existing [source sheet:1](</D:/aai work/granthstudio/docs/pilot/SOURCE_APPROVAL_SHEET.md:1>) remains pending.  
   **Required:** bind P2 to an owner-approved source passage, master image and permitted gesture. Separate source facts from artistic movement choices. A prototype approval must not imply chapter-wide approval.

2. **BLOCKER — Hindi semantic approval remains unresolved.**  
   [v4:65](</D:/aai work/granthstudio/docs/ARCHITECTURE_V4.md:65>) specifies bilingual assembly but omits the exact Marathi lock, line-to-line Hindi correspondence, speaker checks and semantic approval rules retained from [v3.1 §5](</D:/aai work/granthstudio/docs/ARCHITECTURE_V3_1.md:123>). This is a demonstrated failure class: [Hindi review sheet:5](</D:/aai work/granthstudio/docs/pilot/HINDI_REVIEW_SHEET.md:5>) records a meaning reversal.  
   **Required:** hash-bound approval of each working Hindi line against the exact Marathi line. Protected-term checks alone cannot clear translation.

3. **BLOCKER before voiced release — Audio permission is unresolved and inconsistent.**  
   IndicF5 remains on hold. Furthermore, [audio requirements:25](</D:/aai work/granthstudio/docs/pilot/AUDIO_ACCESS_AND_NARRATOR_REQUIREMENTS.md:25>) describes permission extending to the project, while [consent checklist:19](</D:/aai work/granthstudio/docs/pilot/VOICE_REFERENCE_CHECKLIST_AND_CONSENT.md:19>) limits permission to the private pilot and excludes release.  
   **Required:** one explicit consent scope covering languages, synthesis, publication, commercial status, retention and withdrawal. Record rights for music, recordings and effects separately. A licensed, labelled scratch track may support timing; it cannot clear release.

4. **MAJOR — Data contracts are descriptions, not yet enforceable v4 contracts.**  
   [v4 §6](</D:/aai work/granthstudio/docs/ARCHITECTURE_V4.md:87>) lists fields; [progress:495](</D:/aai work/granthstudio/docs/PROGRESS.md:495>) confirms P0 schemas remain unfinished. Missing definitions include stable IDs, schema versions, approval evidence, permitted transitions, path rules, rig coordinates/pivots, texture/alpha conventions and reconstruction thresholds.  
   **Required:** minimal P1/P2 schemas and valid/invalid fixtures first. Map existing schemas and integrity code to v4 instead of rebuilding them.

5. **MAJOR — Recovery principles were lost in the summary.**  
   [v3.1:260](</D:/aai work/granthstudio/docs/ARCHITECTURE_V3_1.md:260>) requires verified temporary outputs, atomic publication, durable receipts and restart verification. V4 specifies image-request UNKNOWN states but not crash-safe publication, corrupt-output handling, concurrent invocation or backup restoration. A research/canon edit must also invalidate affected approvals and derived artifacts.  
   **Required:** specify these retained guarantees explicitly and prove interruption/resume. Local Git tags without a remote or separate backup do not protect against loss of D:.

6. **MAJOR — “Shared visuals” conflicts with unspecified speech anchoring.**  
   [v4:64–65](</D:/aai work/granthstudio/docs/ARCHITECTURE_V4.md:64>) says Hindi gets its own timing, but does not define whether this retimes shared clips or produces language-specific animation. Word anchors also assume validated MR/HI alignment, which [v3.1:150](</D:/aai work/granthstudio/docs/ARCHITECTURE_V3_1.md:150>) explicitly gates.  
   **Required:** preserve natural-speed action clips; define permitted holds, cutaways and language-specific exceptions. Test unequal speech durations without truncated narration, interrupted gestures or unnatural action speed.

7. **MAJOR — Model, reference and style authority are ambiguous.**  
   [v4:21](</D:/aai work/granthstudio/docs/ARCHITECTURE_V4.md:21>) names Nano Banana 2.1, while §12 specifies Pro; [progress:496](</D:/aai work/granthstudio/docs/PROGRESS.md:496>) still lists model-output preference as pending. Existing sheets demonstrate a look, not animation-ready parts or approved cross-angle identity. The [style audit §2](</D:/aai work/granthstudio/docs/pilot/SDXL_STYLE_AUDIT.md:35>) already demonstrated that correct style text does not control incompatible references.  
   **Required:** record the exact production model ID, approved master/reference hashes, style version, reference limits and output specification. Treat fallback equivalence as a separate gate.

8. **MAJOR — Affordability and storage feasibility lack an acceptance model.**  
   [v4:35](</D:/aai work/granthstudio/docs/ARCHITECTURE_V4.md:35>) explicitly leaves prices unverified. [§12:143](</D:/aai work/granthstudio/docs/ARCHITECTURE_V4.md:143>) requires an owner-set render-cost limit, but none is recorded. “As many images as needed” is not a spending ceiling.  
   **Required:** count reference/input charges, rejected images, retries, UNKNOWN requests, Kimi planning/screening, rig preparation, render failures, storage and owner review time. Report cost per **accepted shot/second**, with low/base/high series estimates. Set disk reserves and retention rules before rendering.

9. **MAJOR — The only human reviewer is an unmeasured production dependency.**  
   [v4:69–72](</D:/aai work/granthstudio/docs/ARCHITECTURE_V4.md:69>) requires calibration, uncertainty review, samples and owner release approval, without sample size, review workload or escalation rules. “Automatically accepted” versus “nothing approved by a model” also needs distinct machine statuses.  
   **Required:** distinguish technical validation, screening and owner approval; retain evidence for each. Measure review minutes and rejection rates during P2/P7. Do not count an unreviewed output as accepted production footage.

10. **MAJOR — Typography, rights and release specifications are incomplete.**  
    [v4:65](</D:/aai work/granthstudio/docs/ARCHITECTURE_V4.md:65>) names libass/HarfBuzz but does not pin the actual build, font/hash/license, subtitle format, wrapping or safe areas. [v4:94](</D:/aai work/granthstudio/docs/ARCHITECTURE_V4.md:94>) mentions terms/SynthID without a release checklist.  
    **Required:** test real MR/HI conjuncts and matras against an owner-approved reference; specify aspect-ratio conforming without stretching, audio format and subtitle outputs. Record applicable model/service terms, reference-image rights, fonts, music/effects, attribution and SynthID handling. “No watermarks” in a prompt proves none of these.

11. **MINOR — Governance documents still describe different projects/tasks.**  
    [AGENTS.md:7](</D:/aai work/granthstudio/AGENTS.md:7>) names v3.1 authority and LTX review requirements; [TASK_CONTRACT.md:1](</D:/aai work/granthstudio/docs/TASK_CONTRACT.md:1>) concerns an older CPU correction round.  
    **Required:** prepare a current P1/P2 review contract and supersession map. Preserve frozen documents. D-014 does not require reviving the old LTX gate.

Beyond §12’s three ranked risks, explicitly rank: **source/translation/consent blockers; false acceptance and paid-request recovery; disk/backup failure; owner workload; subtitle correctness and rights; provider/model changes and fallback availability.**

**Script defects and evidence**

12. **MAJOR — P1 can pass failed runs using stale files.**  
    [p1_run.py:101](</D:/aai work/granthstudio/scripts/blender/p1_run.py:101>) records failures but continues; [line 127](</D:/aai work/granthstudio/scripts/blender/p1_run.py:127>) ignores every subprocess exit code and timeout. Output directories are reused.  
    **Reproduce:** populate valid outputs, rerun into that directory with a Blender executable that exits unsuccessfully. Existing repeats and frames can satisfy the pass predicate.  
    **Correction:** require successful steps and current-run, input-bound outputs; validate exact contiguous frame names, dimensions, fps and duration. A configurable smoke test must not claim the full P1 gate.

13. **MAJOR — P1 acceptance omits mandatory captions and receipt bindings.**  
    [p1_run.py:120](</D:/aai work/granthstudio/scripts/blender/p1_run.py:120>) encodes video without captions. Its receipt lacks source-image/script hashes and pinned Blender/FFmpeg versions. Resource availability is not part of acceptance.  
    **Correction:** implement the Devanagari reference check required by v4 §10 and bind the receipt to exact inputs/tools. Retain “smoke pass” separately from “P1 accepted.”

14. **MAJOR — Process failure handling can lose the evidence needed to diagnose failure.**  
    [p1_run.py:58](</D:/aai work/granthstudio/scripts/blender/p1_run.py:58>) kills only the immediate process, has no `try/finally` cleanup and discards most output. FFmpeg’s ordinary lowercase `error` messages can be filtered out. [ffprobe:123](</D:/aai work/granthstudio/scripts/blender/p1_run.py:123>) has no timeout or exit check; invalid JSON can prevent receipt writing.  
    **Correction:** bounded process-tree termination, sampler shutdown/join, full logs and a final failure receipt even on exceptions or interruption.

15. **MAJOR — Reported “peak memory” can mean unavailable or unrelated memory.**  
    [Sampler:39](</D:/aai work/granthstudio/scripts/blender/p1_run.py:39>) silently ignores missing tools and errors; zero then appears as a measurement. GPU sampling reports the first GPU’s total usage, not Blender-specific consumption, and one-second polling can miss peaks.  
    **Correction:** record device, baseline, scope and sampling interval; distinguish unavailable from zero. Call the result a sampled maximum. Measure representative layered P2 scenes before extrapolating to the laptop’s 6 GB limit.

16. **MAJOR — Frames accumulate without disk preflight or verified cleanup.**  
    [p1_run.py:113](</D:/aai work/granthstudio/scripts/blender/p1_run.py:113>) retains all PNGs and has no capacity reserve. For scale, 240 RGB frames at 1080p represent **1.39 GiB uncompressed**; five to eight minutes represent about **42–67 GiB**. PNG size varies—these are budgeting figures, not predicted file sizes.  
    **Correction:** preflight measured storage needs, render in bounded shots, and remove temporary frames only after verified encoding under an explicit retention policy.

17. **MAJOR — Gemini failures return success; ambiguous paid outcomes are not journalled.**  
    [gemini_test.py:104](</D:/aai work/granthstudio/scripts/image_trials/gemini_test.py:104>) sends before persisting request intent; [line 129](</D:/aai work/granthstudio/scripts/image_trials/gemini_test.py:129>) returns zero even when every request fails.  
    **Evidence:** `D:\kaggle_upload\nbpro\receipt.json` records scene 1 timing out after 300.4 seconds; `nbpro1\receipt.json` records its later resend. Billing remains unresolved.  
    **Correction:** nonzero failure exit, durable PREPARED/SENT/UNKNOWN state, no automatic resend of ambiguous requests, and a recorded reconciliation/resend decision. This trial script must remain outside production automation until fixed.

18. **MAJOR — Gemini outputs cannot be reliably reproduced or resumed.**  
    [gemini_test.py:95](</D:/aai work/granthstudio/scripts/image_trials/gemini_test.py:95>) resets receipts; references silently fall back between sets at line 100. It records neither reference/request hashes nor the actual transmitted JPEG hashes. Images and receipts are overwritten directly; response bytes are labelled PNG without decoding or checking MIME type.  
    **Correction:** preserve attempt history, hash the exact request inputs, validate returned images and publish atomically. Reject existing-output collisions unless verified reuse is intended.

19. **MAJOR — Secret scrubbing is incomplete.**  
    Keeping the key outside Git and in a header is sound. However, [gemini_test.py:48](</D:/aai work/granthstudio/scripts/image_trials/gemini_test.py:48>) truncates errors **before** replacing the complete key. A truncation through the key leaves its prefix visible.  
    **Evidence:** reproduced in memory with a synthetic key; no real key was read.  
    **Correction:** scrub before truncation everywhere. Move key loading from import time ([line 34](</D:/aai work/granthstudio/scripts/image_trials/gemini_test.py:34>)) into execution so help and offline tests need no credential.

20. **MINOR — Repeatability evidence is narrower than “deterministic renderer.”**  
    [p1_run.py:107](</D:/aai work/granthstudio/scripts/blender/p1_run.py:107>) correctly compares decoded pixels. The saved smoke receipt reports frame 12 with pixel difference **0**, despite unequal PNG hashes; that is compatible with differing file metadata. It does not prove sequence consistency, rig determinism or recovery.  
    **Correction:** compare selected isolated renders with their sequence frames; pin tools and state the tolerance. Validate frame bounds. The [single-plane camera scene](</D:/aai work/granthstudio/scripts/blender/p1_scene.py:26>) is suitable for P1 infrastructure testing, but provides no acting or reconstruction evidence for P2.

**Next proper steps, in order**

1. **First: Kimi prepares the bounded P1/P2 contract and repairs the evidence runner offline.**  
   **Deliverable:** reviewable diff, exact acceptance checklist and synthetic tests for stale outputs, failed subprocesses, timeouts, malformed probes and unavailable measurements.  
   **Acceptance:** each injected failure produces a failed receipt and nonzero exit; valid fixtures pass. Codex reviews it.  
   **Unblocks:** trustworthy P1 execution. No paid calls, new art or episode pipeline needed.

2. **Owner supplies the P2 decision packet while that work proceeds.**  
   **Deliverable:** approved blessing passage/beat, character/style master, exact image backend, permitted artistic choices, API spending ceiling and render-cost limit.  
   **Acceptance:** dated decisions tied to exact files/hashes; unresolved items remain blockers.  
   **Unblocks:** bounded P2 asset preparation. The owner need not approve all 21 chapters now.

3. **Kimi specifies minimal prototype schemas and operating limits.**  
   **Deliverable:** P1/P2 manifests, rig/reconstruction contract, receipt format, storage reserve/retention plan, tool pins and backup/restore instructions.  
   **Acceptance:** invalid fixtures are refused; changed inputs invalidate reuse; a copied artifact and receipt verify successfully.  
   **Unblocks:** reproducible prototypes without premature production infrastructure.

4. **Coding agent executes corrected P1 when GPU execution is authorized.**  
   **Deliverable:** 240-frame 1920×1080/24 fps video, Devanagari comparison, hashes, logs, sampled RAM/VRAM, disk use and timing.  
   **Acceptance:** valid ten-second decoded output; repeat/sequence agreement; owner checks typography; forced interruption resumes or fails safely.  
   **Unblocks:** P2 rendering. The existing 24-frame smoke test cannot substitute.

5. **Kimi builds only the approved P2 blessing scene.**  
   **Deliverable:** layered assets, rest-pose reconstruction evidence, minimal rig and visible blessing animation.  
   **Acceptance:** owner records §12 PASS/FAIL against seams, anatomy, movement, identity/style and the previously set cost limit; minor defects are resolved before PASS.  
   **Unblocks:** P3 onward. Failure reopens the decision with the owner; it does not automatically authorize another renderer.

6. **After P2 PASS, harden the P3 asset runner and recovery.**  
   **Deliverable:** request journal, lineage, costs and interruption/recovery evidence.  
   **Acceptance:** forced ambiguous timeout creates UNKNOWN without a second paid call; corrupt outputs are rejected; verified completed work survives restart.  
   **Unblocks:** controlled asset automation and P4/P5.

7. **Owner resolves Hindi and voice/rights inputs; Kimi proves bilingual timing.**  
   **Deliverable:** approved MR/HI lines, one consistent consent record, rights ledger, measured timelines and subtitle samples.  
   **Acceptance:** unequal language durations preserve every approved line and required action; pronunciation and Devanagari receive owner review.  
   **Unblocks:** P6 and the voiced bilingual pilot. IndicF5 stays on hold until consent is supplied.

8. **Complete P7, then P8/P9 before series expansion.**  
   **Deliverable:** bilingual pilot, sustained sequence and one recoverable chapter run, with accepted-output cost and owner-review workload.  
   **Acceptance:** owner quality approval, measured affordability, stable resources, selective invalidation and successful recovery.  
   **Unblocks:** a defensible decision about the remaining chapters.

No files were changed; no GPU, network or project workloads were run. Verification here was static review, saved-evidence inspection, syntax parsing and the synthetic scrub check. Current prices, terms and provider capabilities remain unverified.