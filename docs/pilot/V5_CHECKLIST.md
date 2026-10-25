# V5 checklist (Phase 0 and Phase 1 images)

Plan: `docs/pilot/V5_PRODUCTION_PLAN.md` rev 4 (D-015). Mark each item when done. Images go to **`D:\aai work\v5_inbox\`** (outside the repository). Run the checker after each batch: `python scripts/image_trials/v5_inbox_check.py`.

## A. Owner decisions needed (Phase 0)
- [ ] A1. Approve the exact Adhyay 1 pilot passage (Marathi + Hindi lines) in `SOURCE_APPROVAL_SHEET.md` — send the text.
- [x] A2. Pilot Maharaj: **YOUNG** (owner, 2026-10-25). Attach the young reference sheet for every Maharaj image; mature comes later.
- [ ] A3. Name a backup drive/folder for verified copies.
- [ ] A4. Reference sheets to use for identity (the young/mature parts sheets already sent).

## B. Machine check (Claude, done 2026-10-25)
- [x] NVIDIA RTX 3050 6GB Laptop GPU + AMD Radeon iGPU; 15.3 GB RAM; D: 15.8 GB free; C: 5.7 GB free.
- [x] B1. Blender 5.2.3 EEVEE test render: OK, 1280x720 default scene in 1.76 s (2026-10-25).

## C. Image style block (paste at the start of EVERY prompt; attach the Maharaj reference sheet for his images)
> Flat 2D illustration for a printed devotional film, simple styled figures, bold dark-navy outlines, flat colour fills, limited palette (warm brown skin, white cloth, saffron, indigo, ochre, brick red), no gradients, no photographic texture, no text, no watermark. Calm, respectful expression. 16:9, 1920x1080.

## D. Images to generate (Phase 1, 14 images)
Rules: PNG; 16:9; keep the character the same size and position in all poses of a shot; characters on a **plain white background** unless marked; same reference attached every time. Say how many tries you needed.

### Test 1 — A: temple establishing shot (4 images)
| File | What |
|---|---|
| `A1_bg_sky.png` | distant sky and far hills, no buildings |
| `A1_mid_temple.png` | a small village temple with courtyard, on plain white (no sky) |
| `A1_fg_frame.png` | foreground framing: two pillars/arch and some leaves at the edges, centre empty, on plain white |
| `A1_full.png` | the same scene as one complete picture (backup if layers do not separate well) |

### Test 2 — C: Maharaj blesses a devotee (5 images)
Devotee: one simple village man, white dhoti and shirt, a plain cloth on the head (generate his reference first).
| File | What |
|---|---|
| `D1_devotee_ref.png` | devotee standing, front view, full body, plain white |
| `C1_p1_wide.png` | wide: Maharaj seated, devotee approaching with folded hands (both in frame) |
| `C1_p2_bow.png` | medium: devotee bowing at Maharaj's feet, Maharaj seated |
| `C1_p3_bless.png` | medium: Maharaj seated, right hand raised in blessing, calm |
| `C1_p4_react.png` | close-up: devotee's face, eyes closed, relieved, hands folded |

### Test 3 — C: Maharaj and an object (3 images)
Object: a plain brass water pot (lota). Test shot only, not a canon claim.
| File | What |
|---|---|
| `C2_p1_offer.png` | over-the-shoulder: devotee holds out the lota toward seated Maharaj |
| `C2_p2_hands.png` | close-up: hands passing the lota (devotee's hands, Maharaj's hand) |
| `C2_p3_hold.png` | medium: Maharaj seated holding the lota calmly |

### Extra (1 image)
| `FX_light_smoke.png` | soft light rays and a few smoke curls on plain black (for overlay effects) |

## E. Done when
- [x] Checker reports all files present, PNG, 16:9, readable (13/13, 2026-10-25; Flow sparkle watermark on several images to be painted out).
- [ ] Owner sentence per shot: which images were rejected and why (for cost-per-accepted-shot).
- [ ] Claude + Codex have Phase 0 gates checked; then Phase 1 starts.
