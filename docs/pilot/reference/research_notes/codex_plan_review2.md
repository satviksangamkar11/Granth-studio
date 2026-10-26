**Not PASS — rev 3 still has approval gaps.** References below are to the exact [V5_PRODUCTION_PLAN.md](</D:/aai work/granthstudio/docs/pilot/V5_PRODUCTION_PLAN.md>).

- **BLOCKER — Budget enforcement remains underspecified (lines 30–31).** An estimated call can fit while its actual charge exceeds the cap; timeouts can leave billed work unaccounted for. Require worst-case reservations using exact model IDs, pricing and output limits; durable reservation before dispatch; UNKNOWN charges retained until reconciled; all retries through the guard. Before paid use, demonstrate refusal at phase/$50 limits and after interruption or ambiguous timeout.

- **BLOCKER — D-014 blessing audit is not preserved explicitly (lines 41–45).** S-B permits any “approved gesture”; the gate omits the required written blessing-scene audit, seams/halos, minor-issue correction and measured rendering cost against an owner-set limit. Restore that prerequisite before Phase 2 or explicitly propose changing it in D-015. Blender-only and no-full-3D are otherwise consistent.

- **MAJOR — COA test cannot objectively authorize custom rigging (line 41).** “Import → deform → render” has no pinned package/hash, representative fixture, time/attempt limit or failure criteria. Require the approved seated parts, arm/hand deformation and blink, save/reopen, headless rendering of the specified sequence, expected frame count and saved results. Upstream confirms testing on **5.1**, which does not establish **5.2.3** compatibility. [COA Tools upstream](https://github.com/Aodaruma/coa_tools2)

- **MAJOR — Storage correction is incomplete (line 36).** “Beyond the job” lacks a bounded peak-space estimate; a backup location does not prove durable recovery. Require bounded frame chunks, a preflight space check and verified copies of reconstruction assets, manifests, receipts and accepted clips before deleting necessary intermediates.

- **MAJOR — Bilingual timing/release gates remain ambiguous (lines 53–56).** Define durations from measured, aligned semantic beats; trimming must preserve complete speech and required gestures. Rhubarb needs recorded per-language pass/fail criteria. Scratch narration must remain timing-only; final release requires approved, licensed/consented audio.

**Resolved:** source approval now precedes generation; IndicF5 remains explicitly **NOT VALIDATED**; phase caps correctly total $50; the rival-renderer test is removed and fallback switching requires owner approval.

Read-only document verification; no software, renders or guard tests executed.