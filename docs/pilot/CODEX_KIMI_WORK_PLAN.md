# CODEX KIMI WORK PLAN

> **CURRENT OWNER RULES (2026-10-27) override any older text in this file:** the EASY script is the owner's only (Kimi never writes, edits or flags it); Kimi Stage 1 = HIGH effort, Stage 2 = LOW; delivery = TWO videos (Marathi, Hindi), same picture, same length (a multi-track master is optional); Nemotron drafts the next code, Claude verifies; Adhyay 1 Stage 1 is not repeated; 59 shots (not 61); Codex runs at medium effort. Master checklist: `CHECKLIST_BUILD_PIPELINE.md`; contracts: `PIPELINE_README.md`.


*Proposed contents for `docs/pilot/CODEX_KIMI_WORK_PLAN.md`. This was a read-only review; I did not create or edit the file.*

## 1. Summary

1. **Partly agree** with the pasted advice: two Kimi stages fit the plan, and Kimi may draft bounded animation JSON.
2. The owner supplies the EASY Marathi and Hindi script. Kimi must not write its lines.
3. S4 shows that **low effort can work**: its plan was VALID, with a Nemotron PASS, for $0.0724.
4. S4 is still a draft. Its image choices are not bound to approved files, some presets need missing layers, and nothing has been rendered or owner-approved.
5. Use free checks, reuse, compact outputs and measured comparisons before assigning high effort or chapter cost estimates.

## 2. Claim-by-claim check

| Pasted claim | Finding |
|---|---|
| Kimi should write a story bible and extract assets | **Partly supported.** It can organize chapter-specific facts from the locked source and frozen research. Code should extract known IDs and compare them with the series catalog; the owner resolves canon questions. Do not pay Kimi to re-research settled material. |
| Kimi should write 60+ EASY lines in both languages | **Contradicted by the latest owner answer.** The owner supplies both scripts. Kimi may flag missing ovi coverage, glossary conflicts or unclear speaker links for owner review; it must not replace wording. |
| Kimi should produce every final Flow prompt | **Unsupported as the best use of paid output.** It may supply short beat and image briefs. Code can combine approved character, place, style and reference data into full prompts. Test free NVIDIA briefs with owner review before assigning this work to Kimi. |
| Phase 1 needs high effort; low will drift | **Unproven.** The five-shot S4 director call at low effort returned VALID and Nemotron PASS. That does not prove low is best for chapter planning, but the claimed 15,000–25,000-token high-effort trace and likely truncation are not measured here. Test one small, fixed low/high comparison before changing the default. |
| Use `max_tokens=32768` | **Poor fit for the current P4 cap.** [v5_ledger.py](<D:/aai work/granthstudio/scripts/image_trials/v5_ledger.py:19>) charges a reservation for the *full* output limit at $10 per million tokens. Using S4’s 13,287 counted input tokens, the reservation is `((int(13,287 × 1.1) + 200) × $2/M) + (32,768 × $10/M) = $0.35731`. [CHECKLIST_PROOF_SCENE_S4.md](<D:/aai work/granthstudio/docs/pilot/CHECKLIST_PROOF_SCENE_S4.md:41>) reports P4 committed at $0.685 of $1, leaving $0.315; that request would be refused even if actual output proved short. A larger Chapter 1 input raises the reservation. |
| Kimi is especially strong at spatial JSON | **Unsupported by repository evidence.** Existing preset JSON is a useful constraint, but a renderer and owner must establish whether its proposed movement looks right. |
| Phase 1 $0.60–$1.20, Phase 2 $0.20–$0.45, total $0.80–$1.65 | **Forecasts, not measurements.** The [S4 receipt](<D:/aai work/granthstudio/canon/director_runs/a1_s4_kimi_one/receipt.json:51>) records low effort and a 16,000-token limit; its call used 13,287 input and 4,586 completion tokens, costing `$0.026574 + $0.045860 = $0.072434`. S4 has five shots; Chapter 1 has scenes of different sizes, and there is no measured Stage 1 chapter run under the proposed contract. The provisional $5 chapter cap is a ceiling, not a spending target. |

The current director schema still asks Kimi to write dialogue, claims and `images_needed`; the S4 output consequently declared nine new image IDs. The proposed compact contract and catalog binding are **not yet implemented**. The [S4 review](<D:/aai work/granthstudio/canon/director_runs/a1_s4_kimi_one/REVIEW.md:1>) explicitly says draft, unrendered and unapproved. Presets 01, 02 and 08 selected there require layers or transparent assets that the flat finals do not supply.

## 3. Better allocation of Kimi work

**Before Stage 1:** Code locks the checked ovis, owner script, glossary, series bible and hashes. Code checks IDs, duplicate or missing ovis, speaker links and known terms. A free NVIDIA model can flag possible meaning or continuity problems; its findings are advisory. The owner settles them in one batch.

**Stage 1 — chapter decisions:** Reuse an approved split with unchanged input hashes. For a new chapter, Kimi drafts a compact scene map: scene ID, ordered ovi IDs, goal and turn, owner-script line IDs, short image briefs, existing character/place/prop IDs, sound-palette IDs and open questions. No EASY prose, full Flow prompts, timings or long repeated descriptions. Code expands the approved data into prompts and checks coverage; the owner approves meaning, portrayals and briefs. Default **low effort**. Start with a per-scene or small-scene-group limit around **4,096–8,192 completion tokens**, then adjust from actual usage and truncation evidence. One giant chapter response risks a hard-to-recover partial result; isolated scene outputs let accepted work survive a failure.

**Stage 2 — animation:** Code first replays an approved shot plan only when its source, script, timing, image and preset fingerprints match. It then proposes compatible approved presets and catalog images. Send Kimi only unresolved shots with their measured shared beats and approved IDs. Kimi returns IDs, a held pose or staging choice, transition, and `NEED_NEW` with a reason where necessary. Code inserts dialogue, claims, timings and full asset metadata. Default **low effort**, with about **2,048–4,096 completion tokens** for a small unresolved scene; set the actual limit after measuring compact outputs.

Put stable references first in each request. [HANDOFF.md](<D:/aai work/granthstudio/docs/pilot/HANDOFF.md:50>) reports automatic prefix caching, but “sent once per chapter” is inaccurate: each request still sends the prefix, and a discount depends on a cache hit and its lifetime. Keep identical bytes and record counted input, cache evidence if available, output tokens, finish reason and cost. Cache locally approved outputs by exact input hashes; never buy the same decision twice after a valid reply.

For paid calls: free schema and catalog pre-check, free NVIDIA dry run, ledger reservation, **one Kimi call, no automatic repair**. If invalid, truncated or `UNKNOWN`, stop. Reconcile any uncertain charge against the dashboard; the owner decides whether a changed, targeted request is worth buying. Do not silently spend on reviewer-triggered retries.

The provisional **$5 per chapter** needs a chapter-aware ledger rule; [v5_ledger.py](<D:/aai work/granthstudio/scripts/image_trials/v5_ledger.py:19>) currently has phase caps and a $50 total cap, not a chapter cap. A starting allocation to propose is **$1 Stage 1, $3 Stage 2 and $1 owner-controlled contingency**, with the existing P4 $1 cap still binding until explicitly changed. Reserve each request’s worst case before dispatch.

Measure quality on the same small fixed set after each contract change: ovi and script-line coverage, schema validity, unsupported canon claims, asset-role/hash validity, and the owner’s accept rate without edits. Record tokens, cost and time alongside those scores. A cheaper answer is useful only if it passes the same gates.

## 4. What “new animation by Kimi” means

Kimi can draft **data** for an unresolved shot: shot/beat IDs, approved image IDs by required role, preset ID and hash, held pose, transition, and either a `NEED_NEW` reason or a proposed JSON version of a preset. For the approved preset-03 variants, the schema should allow only its single `img` role, 144 frames, one segment, approved easing values, and bounded camera start/end values for push in/out or pan left/right. Use the existing 1.0–1.2 zoom range and test candidate pan/framing bounds against image edges before adding them to the approved whitelist. No arbitrary fields, scripts or new effects.

A proposed JSON file stays **DRAFT** until schema checks, catalog ID and live SHA-256 checks, a full-frame test render, bilingual timing inspection and owner viewing pass. Save an approved version with its JSON hash, renderer version, required asset roles, test-render receipt and owner approval in `assets/v5_presets/`; save approved scene plans under `canon/shot_plans/A<N>/S<x>.json`. Reuse only with verified fingerprints. Start with the flat full-frame image; request a cut-out only when the beat demonstrably needs separate depth or pose. Kimi cannot create missing images, move a limb from a held pose, change Builder v2 or write Python/Blender code. A renderer gap remains a separate decision.

## 5. Improvement experiments

| Experiment | Done-test | Estimated paid Kimi cost |
|---|---|---:|
| Free NVIDIA short image briefs plus code-built Flow prompts; owner reviews against a few existing accepted shots | Owner accepts briefs and generated prompts without more canon corrections than the Kimi alternative | $0 |
| Kimi versus free briefs on the *same* small scene, only if the free result fails | Owner scores missing facts, edit time and accept rate; retain the cheaper passing method | Roughly $0.02–$0.08 for one compact call |
| Compact Stage 2 on one unresolved scene | Valid JSON, approved IDs only, materially fewer completion tokens than S4’s 4,586 | Roughly $0.02–$0.08 |
| Low/high Stage 1 A/B on one fixed scene, after free preparation | Blind owner review shows a meaningful quality gain that justifies high’s extra tokens | Reserve each call from counted input and its chosen limit; expect under $0.20 actual for the pair, **unverified** |
| Preset-03 variants, starting with one flat image | Full render has no exposed edge, wrong crop or mismatch with the beat; owner approves each variant | $0 if JSON is drafted locally; one targeted Kimi call only if needed |
| Exact-hash replay and changed-input refusal | Unchanged plan triggers zero paid calls; changed image or script hash blocks replay | $0 |

These estimates are experiment budgets to check against the ledger, not promised provider bills.

## 6. Checklist to add to `FINAL_ARCHITECTURE_PLAN.md`

| Item | Who | Owner decision? | Done-test | Cost |
|---|---|---|---|---|
| 1. Record owner script as Stage 1 input, never Kimi output | Claude; owner | Yes, already answered | Contract and checklist agree | Free |
| 2. Resolve stale one-master wording to two same-length language videos | Claude; owner | Yes, already answered | Delivery gate names both exports | Free |
| 3. Lock source, script and canon hashes | Code; owner | Yes | Approved receipt; changed input marks dependents stale | Free |
| 4. Add chapter and stage Kimi caps to ledger | Claude; Codex reviews | Yes for allocation | Reservation refuses an over-cap request | Free |
| 5. Define compact Stage 1 schema | Claude; Codex reviews | Yes for final contract | Coverage and unsupported-claim fixtures fail correctly | Free |
| 6. Test free image briefs against owner review | NVIDIA; owner | Yes for acceptance | Fixed-set scores recorded | Free |
| 7. Run only needed Stage 1 scene groups | Kimi; owner | Yes for output | Valid receipts, owner-approved split and briefs | Capped |
| 8. Build full Flow prompts from approved data | Code; owner | Yes for images | Exact references and canon text checked | Free |
| 9. Define catalog-ID-only Stage 2 schema | Claude; Codex reviews | Yes for contract | Unknown ID, wrong role or changed hash fails | Free |
| 10. Add exact-hash shot-plan replay | Code | No | Same inputs produce no Kimi call | Free |
| 11. Test low/high only on a fixed small scene | Kimi; owner | Yes before spending | Quality and token comparison recorded | Capped |
| 12. Test one bounded preset-03 variant and one real `NEED_NEW` | Kimi if needed; owner | Yes for each | Full render and owner viewing pass | Capped |
| 13. Save approved JSON and render receipts | Claude; owner | Yes | Version, hashes and approval permit replay | Free |
| 14. Export and inspect Marathi and Hindi videos | Claude; owner | Yes | Same picture and length; complete measured speech | Free local render |

## 7. Exact Kimi section for `docs/DECISIONS.md`

> ## Kimi work for Adhyay 1–21 (owner answers, 2026-10-27)
>
> The owner supplies and approves the EASY Marathi and Hindi script. Kimi does not draft or replace its lines. Kimi may organize the locked source and approved script into scene decisions, short image briefs, catalog references and open questions. Code checks coverage and builds full image prompts from approved canon. The owner approves the result in a batch.
>
> Approved shot plans and presets are reused when their input hashes match. Kimi receives only unresolved animation shots. It may draft shot-plan or new preset JSON within the frozen renderer’s supported schema, including bounded preset-03 variants. It may not write animation code or change Builder v2. Every new JSON version needs validation, a test render and owner approval before reuse. Flat images come first; cut-outs are made only for beats that need them.
>
> Kimi’s chapter cap is provisionally $5. Chapter and stage enforcement, the compact output contracts, and low-versus-high quality measurements remain implementation work; the existing P4 $1 cap remains in force until changed. Paid calls have no automatic repair or retry, and uncertain charges are reconciled before another call. Hindi audio is measured and used while its translation status remains labelled `NOT_VALIDATED`. Delivery is two videos made from the same picture timeline, with the same length: one Marathi and one Hindi.

## 8. Risks

The largest immediate risk is treating S4’s VALID result as production approval: its images, layer requirements and owner staging decisions remain open. A second risk is a paid request whose **reservation**, rather than likely actual bill, exceeds the active cap. Prefix-cache savings and the pasted chapter prices are unverified forecasts. Finally, low effort’s S4 success does not establish chapter-wide Marathi/Hindi meaning quality; the owner’s script and the fixed coverage and claim checks remain the release gates.