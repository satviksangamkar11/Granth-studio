# Prompt for another agent: plain spoken Marathi and Hindi for the Adhyay 1 film (copy everything below the line)

---

You are helping with a motion-comic film of Adhyay 1 of "Shri Gajanan Vijay" (a Marathi devotional text about Shri Gajanan Maharaj of Shegaon). The film has ONE picture track and TWO narration tracks (Marathi and Hindi). The audience is ordinary family viewers, including children and elders who do not read old Marathi. The current Marathi narration is the original archaic ovi verse read aloud, and the Hindi is a literal draft: BOTH ARE TOO HARD TO UNDERSTAND. We need plain, warm, spoken language.

## Inputs (read only; do not modify)
- `docs/pilot/A1_audio_plan.md` : all 62 lines (id, speaker, ovi, Marathi verse, Hindi draft), grouped in nine scenes S1-S9 with their sound cues. The machine-readable form is `canon/audio/A1_audio_plan.json`.
- Source of truth for meaning: `canon/` Adhyay 1 ovi text (ovi 1-146; story ovi 70-144) and the owner's dialogue table (who may speak).

## Task
For EACH of the 62 lines write two new versions:
1. `mr_simple`: everyday spoken Marathi (the way a grandparent tells the story to a child). Short sentences, common words, no Sanskritised or archaic forms.
2. `hi_simple`: everyday spoken Hindi (Hindustani, not shuddh/Sanskrit-heavy), same meaning, short sentences. Keep honorifics people actually say ("Maharaj", "Gajanan Maharaj", "Bankatlal", "Damodarpant", "Devidas").

## Hard rules
- Same meaning and same speaker as the source line. Add NO event, person, place, number, date, miracle or teaching that is not in the line. Remove nothing that matters: every named person and every action in the line must still be there.
- The year 1878 appears only as an on-screen caption; never write a day or month.
- Where a speaker is unclear in the source, keep the line as narration; do not give it to a character.
- Spoken length: each new line must take about the same time to say as the original or LESS (so the shots already planned still fit). Report the syllable/word count of old vs new per line; flag any line that is longer.
- Divine names and sacred terms (e.g. "Gajanan", "Maharaj", "Shegaon", "bhakt") stay as they are. If a hard word is truly needed, add a short plain explanation inside the sentence.
- No rhyming or poetic ornament; no moralising beyond what the verse says.
- Do NOT touch the teachings (the two sayings and the key spoken instructions): for those lines give the plain version AND mark `keep_original_verse_candidate: true`, because the owner may want the original verse read first and the plain version after.

## Output (one file, JSON array, UTF-8)
`[{"id":"S1-L1","speaker":"narrator","mr_original":"...","mr_simple":"...","hi_original":"...","hi_simple":"...","words_old_mr":N,"words_new_mr":N,"words_old_hi":N,"words_new_hi":N,"keep_original_verse_candidate":false,"notes":"anything the owner should check"}]`
Also give a short list of the 10 lines you were least sure about and why. Mark everything DRAFT, NOT VALIDATED: the owner approves wording.

## Do not
Do not invent dialogue, change who speaks, shorten the story, merge or drop lines, or edit any file in the repository. Return only the JSON and the uncertainty list.
