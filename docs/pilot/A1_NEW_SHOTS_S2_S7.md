# Adhyay 1 — 6 new shots for S2 and S7 (PROPOSED, 2026-11-01)

Why: your directive made 5 optional lines core (S2-L2, S2-L6, S2-L7, S7-L4, S7-L11). Re-timed with the real speech (v2: accepted clips + the 4 Bankatlal re-voices), S2 needs **11** shots (was 8) and S7 **12** (was 9). Total **65** shots (was 59). The other 7 scenes are unchanged.
Existing images keep their ids and are all reused once; the 6 new images get the next free ids. Each prompt reuses the exact style, character, place and light text of its neighbouring accepted job. Nothing is generated until you approve.

## S2 — new slot order (11 × 6 s)

| Slot | Time | Image | Lines starting | Ovis |
|---|---|---|---|---|
| 1 | 0–6 s | SH_S2_01 | S2-L1, S2-L2 | 84, 86 |
| 2 | 6–12 s | SH_S2_02 | S2-L3 | 87 |
| 3 | 12–18 s | SH_S2_03 | S2-L4 | 88 |
| 4 | 18–24 s | SH_S2_08 | — | — |
| 5 | 24–30 s | **SH_S2_09 (NEW)** | S2-L6 | 92 |
| 6 | 30–36 s | SH_S2_04 | S2-L7 | 93 |
| 7 | 36–42 s | SH_S2_05 | S2-L8 | 94 |
| 8 | 42–48 s | SH_S2_06 | — | — |
| 9 | 48–54 s | **SH_S2_10 (NEW)** | S2-L9 | 95 |
| 10 | 54–60 s | SH_S2_07 | S2-L10 | 96 |
| 11 | 60–66 s | **SH_S2_11 (NEW)** | — | — |

## S7 — new slot order (12 × 6 s)

| Slot | Time | Image | Lines starting | Ovis |
|---|---|---|---|---|
| 1 | 0–6 s | SH_S7_01 | S7-L1, S7-L3 | 123, 124 |
| 2 | 6–12 s | SH_S7_02 | S7-L4 | 125 |
| 3 | 12–18 s | SH_S7_03 | S7-L5 | 126 |
| 4 | 18–24 s | **SH_S7_10 (NEW)** | S7-L6 | 126 |
| 5 | 24–30 s | SH_S7_04 | S7-L7 | 127 |
| 6 | 30–36 s | SH_S7_05 | S7-L8 | 128 |
| 7 | 36–42 s | SH_S7_06 | S7-L9 | 129 |
| 8 | 42–48 s | SH_S7_07 | S7-L10 | 130 |
| 9 | 48–54 s | **SH_S7_11 (NEW)** | S7-L11 | 131 |
| 10 | 54–60 s | SH_S7_08 | S7-L12 | 132 |
| 11 | 60–66 s | SH_S7_09 | S7-L13 | 133 |
| 12 | 66–72 s | **SH_S7_12 (NEW)** | — | — |

## The 6 new images

| Image | Shows | People | Preset |
|---|---|---|---|
| SH_S2_09 | Medium shot from straight in front, at the ascetic's eye level: the young ascetic seated cross-legged and upright on the road among the used leaf plates, perfectly still, hands resting open on his knees, eyes lowered, a calm face free of any wish; the frayed old vest clearly visible; the house wall and door softly behind him. | GM_v01 | 12_flat_push_in |
| SH_S2_10 | Close-up insert: the young ascetic's right hand holding a single grain of cooked rice between thumb and fingertip just above a used leaf plate, the grain clearly visible; the leaf plate's dry veins and a few scattered grains fill the bottom of the frame; his knee and the road dust soft behind. | GM_v01 | 10_object_hand_insert |
| SH_S2_11 | Low wide view along the village road at ground level, the scattered used leaf plates large in the foreground, the young ascetic small and seated far down the road before Devidas's house, still gathering grains; house roofs, neem trees and the plain beyond; the road otherwise empty. | GM_v01 | 13_flat_pull_out |
| SH_S7_10 | Medium close-up of Damodarpant alone, facing screen-left toward the seated ascetic off frame, bending slightly forward, right hand on his chest in humble offer of service, earnest eager face; the hot pale road and the house wall behind him. | DK_v01 | 12_flat_push_in |
| SH_S7_11 | Medium close-up of the young ascetic seated on the road, speaking with a gentle smile, his right palm turned up and open toward the two visitors off frame at the right, the empty gourd lying beside his knee; the house wall behind. | GM_v01 | 12_flat_push_in |
| SH_S7_12 | Wide view: the half-open door of Devidas's house with its plinth step now empty (Damodarpant has gone inside); Bankatlal waits in the thin shade of a neem tree at the right, looking at the door; the young ascetic sits in the full sun in the left foreground, calm, looking off screen-left. | GM_v01, BA_v01 | 13_flat_pull_out |

Full Flow prompts: `docs/pilot/A1_NEW_SHOTS_S2_S7.json`. Make them at 2K, one tab each, file by exact title, like the 59.
