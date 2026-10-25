# GranthStudio — merged final plan (proposed D-019; NOT approved)

Sources: D-018 rev 2 (`V5_FINAL_ARCHITECTURE_DRAFT.md`), the owner-pasted D-019 (`D019_PROPOSAL_FROM_OWNER.md`), Codex adversarial review (`D:\kaggle_upload\repo_research\codex_d019.md`), D-012..D-017. Owner confirmed 2026-10-25: **all Nano Banana / Flow image jobs are done manually by the owner** (no image API).

## 1. Verdict
Keep D-018's production approach (owner-made art → asset prep → simplest renderer → ffmpeg finishing → style packs) and add D-019's **source-fidelity layer** (coverage and closure accounting, story + teaching structure, motion chosen by meaning, three gates). Do **not** adopt D-019's API art, Blender-only rendering or a new Kimi-written scene compiler; they contradict D-015/D-017 without a demonstrated need.

## 2. Facts that set the critical path
- The Granth PDF (167 pages) has a legacy non-Unicode Marathi text layer: extracted text is unusable. A machine-readable canon needs OCR or font conversion **plus owner proofreading** of ≈3,668 ovis. Only ovi 84–121 of Adhyay 1 is transcribed, and it is unapproved.
- Existing notes conflict (e.g. ovi 113 speaker; "closed at both ends" vs the incident continuing; a feast reading flagged in verification). They must be settled against page images before anything is filmed.
- Estimate (Codex, unmeasured): 1–2 min proofreading per ovi ≈ 61–122 owner hours for the whole Granth, before art and review.
**Biggest risk: owner editorial and image-making capacity — not the renderer.**

## 3. Pipeline
```
Granth pages → OCR/font conversion → owner proofreading → SOURCE LEDGER (one file per Adhyay: ovi id, page, Marathi, meaning, type tags only where useful)
   → EPISODE PLAN (one file per Adhyay: ordered beats with source spans, story-thread / teaching ids, closure status, coverage disposition per ovi,
     artistic interpretations marked, narration lines MR/HI, audio anchors, shot type + preset + asset roles)
   → GATE 1 source/editorial (owner) → owner makes images in Flow from the style pack's prompt templates
   → asset prep scripts → render per shot: motion.py | parallax.py | Blender Builder v2 (frozen)
   → GATE 2 technical → ffmpeg finishing (grade, grain, border, particles, captions per language, title cards) → MR master + HI master
   → GATE 3 visual + bilingual (owner)
```
Rules kept: canon = approved source only; every ovi gets a disposition (VISUALISED / NARRATED / QUOTED / MERGED_EQUIVALENT / APPROVED_OMISSION); a chapter boundary never invents closure (continuations stay open); philosophy is told by narration, typography, symbols named in the text and contemplative holds — never invented scenes; ambiguity stays neutral in narration; Marathi and Hindi share pictures and meaning, timing and captions may differ.

## 4. Motion policy (by meaning)
M0 held pose + camera + ambient life (default for teaching and devotion) · M1 pose cuts between approved poses (default for action) · M2 hinged limb (only after an owner decision; needs a reviewed builder change) · M3 bespoke (budget gate). Contemplative holds may need a narrow exception to the "minimum zoom 0.12" rule — owner decision.

## 5. Phases (owner's yes before each)
| Phase | Deliverable | Gate | Caps | Owner does |
|---|---|---|---|---|
| **1 Source foundation** (can run beside 2) | OCR/font-conversion trial on 2–3 pages with measured correction minutes; page-linked Unicode ledger for ovi 84–121 + surrounding context; resolved discrepancies; approved MR/HI pilot lines; needed canon entries | no unresolved discrepancy in the pilot span; every pilot assertion traceable | $0 model spend | proofread, settle readings/speakers, approve wording, costume, voice route |
| **2 Visual proof** (can run beside 1) | 15–18 s, one location kit, 3 shots, restrained papercut depth/finish (prep shadows, blur, grain, border, caption sample); then a 2nd shot by image/text swap only | owner judges density, identity, staging, seams, caption shaping, pacing at normal speed next to the reference; reproducible from pinned inputs | 3 image attempts per asset; 1 render retry per shot; $0 Kimi | make images; approve the look once (this amends D-016) |
| **3 60 s bilingual pilot** | episode-plan file for the pilot span; voices (trial ≤2 setup h + ≤2 GPU h); manual timestamps acceptable; MR + HI 60 s masters | meaning and speech complete in both; coverage accounted; resume/cache/backup checks | reconcile the OPEN $0.328 first; existing $50 Kimi ceiling (counting earlier spend) | approve script and contact sheet, hear voices, make art, watch both |
| **4 First full Adhyay**, in sections | whole-chapter ledger + plan approved before production; first 3–5 min section reviewed, then the rest | fidelity, pacing, workload, cost, both releases | separate +$40 Kimi authorisation; chapter image/hour budget from pilot measurements | approve coverage + scripts, make capped art, review both masters |
| **5 Remaining 20**, one at a time | reuse packs, poses, presets | same three gates per chapter | per-chapter budget | approve source/scripts, new designs, final releases only |
Review-time target: ≤10 owner minutes per finished minute (both languages); exceeding it triggers simplification, never skipped fidelity checks.

## 6. Owner decisions (recommendation in bold)
1. Governing plan: **this merged plan; D-015 and D-017 retained.**
2. Source preparation: **chapter by chapter, owner approves; measure the first batch before dates.**
3. Coverage vs 10–20 min: **protect completeness; documented duration exceptions instead of rushing or inventing.**
4. Look and format: **test restrained papercut depth/finish in Phase 2; 16:9 master; vertical excerpts later.**
5. Motion: **held poses + pose cuts now; hinged limbs later only if Phase 2/3 show the need; allow contemplative holds.**
6. Renderer/Kimi: **owner-made art, simplest existing renderer, presets; Kimi only for an approved planning need; no new compiler.**
7. Narration/captions: **Marathi master, owner-reviewed Hindi; matching-language captions; manual timestamps first; voice consent recorded.**
8. Start: **authorise Phases 1 and 2 now; name a backup destination and an owner-hours budget.**
