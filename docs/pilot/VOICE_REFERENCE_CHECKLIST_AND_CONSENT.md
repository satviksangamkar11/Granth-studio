# Voice-reference recording checklist and consent (UNSIGNED; nothing here is approved)

IndicF5 clones the voice of a reference recording, so it may only ever be given a recording whose speaker has granted explicit permission for AI voice synthesis. No voice is invented, borrowed or substituted; an unlicensed voice is never used. The assistant checks the files technically; it cannot grant or infer consent.

## What to record (one set per language; Marathi first, Hindi if possible)
- Speaker: one person, one voice, the same person who signs the consent below.
- Length: 10 to 15 seconds of continuous speech per language (a few clean sentences, not a list).
- Content: calm, reverent narration pace (the pilot is devotional narration), read from a written script. Save the exact script as a text file. Spoken words and the transcript must match word for word; no filler, no repeated takes in one file.
- Room: quiet, no echo, no music, no fan/traffic, no other voices. Phone held about 20 cm away, steady level, no clipping.
- File: WAV, mono, 24 kHz or higher (48 kHz is fine), 16-bit or better; no noise-reduction or voice-changer apps; names like `narrator_mr_ref.wav` and `narrator_mr_ref.txt`, `narrator_hi_ref.wav`, `narrator_hi_ref.txt`.
- Do not use someone else's recording, a film/audiobook clip or a text-to-speech voice as the reference.

## What the assistant will check on delivery
Duration, sample rate, channels, peak level and clipping, silence ratio, and (with IndicConformer) whether the audio matches the transcript. A failed check means re-record, not a workaround.

## Consent to AI voice synthesis for the GranthStudio provisional pilot
I, ____________________ (full name), am the speaker in the recordings listed below.
Recordings: narrator_mr_ref.wav (Marathi) [ ]   narrator_hi_ref.wav (Hindi) [ ]   (tick what applies)
1. I allow these recordings to be used as a voice reference for AI text-to-speech (IndicF5 or a successor) to narrate the GranthStudio provisional pilot (about 45 seconds, Marathi and Hindi).
2. Scope: this technical pilot and its review; not for release, advertising, other projects or any third party, unless I agree again in writing.
3. The synthetic narration may say only the approved pilot lines.
4. I may withdraw this permission at any time by telling the project owner; generated audio and the reference files are then removed from the project and not used further.
5. The recordings and generated audio are stored only in the project's private storage, not published.
Signature: ____________________   Date: ____________________   Contact: ____________________
If the speaker is the project owner, the owner signs as the speaker.
