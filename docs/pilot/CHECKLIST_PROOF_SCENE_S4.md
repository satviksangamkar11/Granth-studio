# CHECKLIST: proof scene S4 (owner 2026-10-27: "scene 4 is okay"; "do not waste any Kimi calls on useless things"). Tick as done; never skip; never redo.

> **CURRENT OWNER RULES (2026-10-27) override any older text in this file:** the EASY script is the owner's only (Kimi never writes, edits or flags it); Kimi Stage 1 = HIGH effort, Stage 2 = LOW; delivery = TWO videos (Marathi, Hindi), same picture, same length (a multi-track master is optional); Nemotron drafts the next code, Claude verifies; Adhyay 1 Stage 1 is not repeated; 59 shots (not 61); Codex runs at medium effort. Master checklist: `CHECKLIST_BUILD_PIPELINE.md`; contracts: `PIPELINE_README.md`.


RULE: every step before step P is FREE (code, tests, dry runs, Codex read-only). Exactly ONE Kimi call (the director for S4), only after steps A-O are ticked and the owner has reconciled the dashboard / confirmed the cap.

## A. Understand what exists (free)
- [x] A1 read S4 in the split run `canon/director_runs/a1_split_rev9/` (shots, ovi ids, budgets)
- [x] A2 read S4 in the audio plan / measured file (lines, Marathi + Hindi durations, crossings, common beat windows)
- [x] A3 read how `scripts/source/director_test.py` builds the scene packet + prompt + validator today

## B. T2 timing verified (free)
- [x] B1 rebuild timing from the accepted clips (`a1_audio.py build --run a1_split_rev9 --measured canon/audio/A1_eleven_measured.json --no-floor`) into a NEW output, compare with the existing one (no silent change)
- [x] B2 table for S4: per shot beat start/end, Marathi/Hindi duration, longer language, crossing
- [ ] B3 owner sees the table (shot count/timeline unchanged = no approval needed)

## C. T3 contract (free, code + tests)
- [x] C1 packet gets shared beat windows + BOTH measured durations + crossing flags per shot (read from the audio plan, never invented)
- [x] C2 director output may NOT contain timings; validator rejects any
- [x] C3 dialogue bound to the approved EASY line ids (not verse substrings) for S4
- [~] C4 (binding file DONE: canon/packets/adhyay_01/final_image_binding.json, 59 sha256; Kimi still declares image ids in images_needed, catalog-pick prompt NOT done; mapping SH_* to ids happens after the plan) image ids: Kimi picks from the catalog ids bound to `final_clean/<SHOT>.png` (binding file with sha256)
- [x] C5 tests added (synthetic fixtures) + full affected suites pass
- [x] C6 Codex read-only review of the diff: READY / fixes applied

## D. Free dry run
- [x] D1 NVIDIA director dry run on S4 (free) to check the contract end to end (no Kimi)
- [x] D2 validator result read by Claude; problems fixed

## P. The ONE paid call
- [x] P1 owner reconciles the Kimi dashboard vs ledger and confirms the cap (the $1 P4 cap is inside $50)
- [x] P2 `reasoning_effort` low, cached prefix first, ids-only output (as far as the contract allows); ledger reservation checked
- [x] P3 run S4 once; receipt saved; validator + Nemotron cross-check
- [ ] P4 owner reads the plan; NEED_NEW items listed

## E. After the plan
- [ ] E1 render 5 shots (Blender or motion.py preset 03) from `final_clean`; E2 mix both languages; E3 subtitles; E4 one master; E5 interrupt/resume test
- [ ] E6 decision log + HANDOFF updated

## Log
- 2026-10-27: B1 new build identical to existing timing+audio plan; S4 crossings: L2 (shot1->2), L3 (3->4), L4 (4->5); Hindi longer on L1,L2,L4. C1: SHARED BEATS block in packet; C2: schema has no timing key (test added); C3: dialogue_plan already forces exact EASY text; 178 director tests pass.
- 2026-10-27 D: free Nemotron dry run canon/director_runs/a1_s4_dry3 (needed --redo: two earlier free S4 dry runs existed; NVIDIA is free). Validator status VALID on the plan after one validator-repair round; result REVIEW_BLOCKED only because the gpt-oss-20b reviewer wrongly says presets 04/05 need limb motion (the validator + preset facts already allow them) and glm-5.3-flash timed out. Cross-scene image manifest refused (sky_morning description clash S4/S5): a one-id-one-description rule to settle before the paid run. Free cost, no Kimi.
- 2026-10-27 C6: Codex review (docs/pilot/CODEX_C6_S4_CONTRACT.md) found 4 defects (multi-cut lists only last shot; exact-boundary false crossing; silent missing seconds; empty binding); all fixed + boundary test; 177 director tests pass. STOP before P: needs owner (dashboard reconcile, cap, one-id-one-description rule, approve S4 split/wording).
- 2026-10-27 P: owner confirmed the $1 cap (P4); ledger had no unreconciled entries; ONE Kimi call (--one-call --effort low --max-tokens 16000), run canon/director_runs/a1_s4_kimi_one: 13,287 in / 4,586 out = $0.0724, P4 committed now $0.685 of $1; validator VALID (0 errors, 3 STAGING warnings), Nemotron cross-check PASS. Plan: S4-1 preset 01 (4 layers), S4-2 preset 02 (4 layers), S4-3 preset 03, S4-4 preset 08, S4-5 preset 03; 9 image ids declared (all new, none reused).
- OWNER RULE (mid-run, same day): saved animation scripts/plans are REUSED wherever they fit; Kimi writes ONLY the new ones. Not implemented yet: today the director always writes a full scene plan and declares new images. Next build: compact contract + library of approved shot plans (preset+image ids+staging) keyed by situation; Kimi called only for shots with no match (NEED_NEW).
