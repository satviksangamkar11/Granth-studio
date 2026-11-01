# Adhyay 1 — Phase B approval sheet (one sitting)

Prepared 2026-11-01. Nothing below counts until you approve it with `approve.py` (you type the confirm phrase yourself).
Checked: with these three approvals the script checker goes from **102 errors to 0 errors, 0 problems** (simulated in a scratch copy, not in the repo).

## 1. Omitted ovis: 81 (rev9's 73 + 8 research-only)

| Ovis | Kind | Why |
|---|---|---|
| 1–32 | invocation | prayers to deities and saints (rev9) |
| 33–38 | commentary | exhortation and praise, no story event (rev9) |
| 39–57 | background | earlier saints, books, the author's plan (rev9) |
| 58–69 | background | Shegaon, Patil's request (rev9); ovis 58–60 still feed the Shegaon view in **Scene S1 shot 1** |
| 75–76 | research only (NEW) | Sajjangad origin is hearsay; ovi 76 says there is no strong proof |
| 77–79 | research only (NEW) | Samarth Ramdas returned as Gajanan: devotional belief, not biography (your answer G-5) |
| 80–82 | research only (NEW) | comparison with the births of the Nath yogis |
| 106–107 | commentary | passers-by vs the gem-picker (rev9) |
| 145–146 | closing | next chapter + dedication (rev9) |

## 2. The other 19 ovis that have no core line (`canon/adhyay_01/stage1/coverage_dispositions.json`)

| Ovi | Disposition | Carried by | Source |
|---|---|---|---|
| 71, 72, 73 | merged | S1-L1 | your treatment: "Narrated: his place and caste cannot be traced (70–73)"; 71–73 are the narrator's similes |
| 74 | visual only | caption 1878 (S1-K1) | the date is your on-screen caption, not narrated |
| 83 | visual only | S1 shot 2 | "his coming to Shegaon (74, 83) is shown, not narrated" |
| 85 | merged | S2-L1 | Devidas's lineage detail (Paturkar, Madhyandina) |
| 86 | optional line | S2-L2 | Ritushanti feast |
| 89 | visual only | S2 (his look) | the gourd |
| 90 | visual only | S2 (his look) | the unfired clay chilim |
| 91, 92, 93 | optional lines | S2-L5, S2-L6, S2-L7 | sunrise comparison, digambar, grain-picking |
| 100 | optional line | S3-L5 | their reasoning |
| 101 | merged | S3-L6 | "a wise host never turns a beggar away" |
| 103 | merged | S3-L8 | Bhagavata: true sages may seem eccentric (speaker kept unclear) |
| 105 | optional line | S3-L9 | |
| 111 | optional line | S4-L5 | untimed |
| 125 | optional line | S7-L4 | |
| 131 | optional line | S7-L11 | |

**Note:** the 9 "optional line" ovis are covered only while their optional line stays in the film. If you later cut an optional line, that ovi needs a new disposition.

## 3. S4 line numbers (same file)

S4-L5 (ovi 111) sits before S4-L4 (ovi 112): the order follows the ovis, only the two numbers are swapped. Both ids already name their Marathi and Hindi clips, and S4-L4 is timed. **Proposal: keep the ids as they are** (approved exception). No file changes, no speech regeneration, and the script hash you approved (`e884d3fe…`) stays the same.

## Commands (replace YOUR_NAME)

```bash
cd "/d/aai work/granthstudio" && uv run python scripts/pipeline/approve.py omissions --adhyay 1 --ovis "$(python -c "print(','.join(str(i) for i in list(range(1,70))+list(range(75,83))+[106,107,145,146]))")"
```
```bash
cd "/d/aai work/granthstudio" && uv run python scripts/pipeline/approve.py approve --adhyay 1 --item stage1_omissions --file canon/adhyay_01/stage1/omissions_approved.json --owner "YOUR_NAME" --confirm "I AM THE OWNER AND I APPROVE THIS FILE"
```
```bash
cd "/d/aai work/granthstudio" && uv run python scripts/pipeline/approve.py approve --adhyay 1 --item coverage_dispositions --file canon/adhyay_01/stage1/coverage_dispositions.json --owner "YOUR_NAME" --confirm "I AM THE OWNER AND I APPROVE THIS FILE"
```
```bash
cd "/d/aai work/granthstudio" && uv run python scripts/pipeline/approve.py approve --adhyay 1 --item easy_script --file canon/adhyay_01/script/easy.md --owner "YOUR_NAME" --confirm "I AM THE OWNER AND I APPROVE THIS FILE"
```

To change any row first: tell me, and I update the file before you approve it.
