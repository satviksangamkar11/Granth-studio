# Audio access instructions and narrator recording requirements (for the Marathi and Hindi pilot narration)

Nothing here has been done for you: the access acceptances, the token and the recordings are yours. I never read the token and I cannot accept access on your behalf.

## 1. Hugging Face access for the three gated models (about 10 minutes, once)
1. Sign in (or create a free account) at huggingface.co with the account you want to use.
2. Open each model page and press the access button ("Agree and access repository" / "Request access"; for these AI4Bharat repositories the grant is automatic, "gated: auto"):
   - https://huggingface.co/ai4bharat/indictrans2-indic-indic-1B (Marathi -> Hindi translation; a 320 M distilled variant `...-dist-320M` exists)
   - https://huggingface.co/ai4bharat/IndicF5 (speech synthesis)
   - https://huggingface.co/ai4bharat/indic-conformer-600m-multilingual (speech recognition check)
   Read what each page asks you to agree to; the declared licence of all three is MIT, but the access terms are on the page.
3. Create a **read** token: Settings -> Access Tokens -> New token (type "Read"). Do not paste it into this chat.
4. In Kaggle: open the notebook -> Add-ons -> Secrets -> add a secret named `HF_TOKEN` with that value, and attach it to the notebook. The audio stage will read it from the Kaggle secret store only (never printed, never written to the evidence).
5. Tell me "audio access granted" (nothing else). I will then pin the exact model revisions and file hashes (the manifest already lists the revisions) and prepare the audio stage script.

## 2. Narrator: who and what is needed
Simplest compliant route (the pipeline's voice records accept `own_recording`): **you narrate**, or one other person who gives written permission. One narrator, two languages (Marathi and Hindi), because the pilot uses a single narrator voice for both releases. No voice of a third party without their written permission; no bundled or celebrity voices.

Per language (Marathi and Hindi), I need:
| Item | Requirement |
|---|---|
| Reference recording | one clean take of about 8-12 seconds of natural, calm narration (the pace and tone you want the film to have); WAV, 24 kHz or higher, mono, 16-bit; a quiet room, no music, no echo, no clipping, no background voices |
| Exact transcript | the words you actually say, in Devanagari, character-exact (it is stored as the reference transcript; a wrong transcript degrades the cloning) |
| Content | ordinary neutral sentences, NOT the pilot ovis (so the reference does not leak the test lines); for Marathi avoid reading verse metre (read it as plain speech) |
| Consent record | a short signed or typed statement: narrator's full name; date; "I give permission for my voice to be used to synthesize narration in Marathi and Hindi for the GranthStudio pilot videos and for the Granth project that follows, [commercial or non-commercial use: state it], I may withdraw this permission by [method]". If the narrator is you, one sentence plus your name and the date is enough |
| Pronunciation notes (optional) | names and sacred terms and how you say them (Gajanan, Devidas, Bankatlal, Damodarpant, parabrahma) |

Files go in `D:\aai work\voice_references\<language>\` (outside the repository). Tell me the paths; I will hash them, write `canon/voices.yaml` (fields: `voice_id`, `speaker` = the voice-only narrator `chr_narrator`, `language`, `reference_audio` path + SHA-256, `reference_transcript`, `consent` basis/granted_by/document_ref/recorded_at, `model_version`) and the pipeline will refuse to synthesize if any hash changes.

## 3. After the narration works
The same narrator reads the six selected Marathi ovis through IndicF5 (generated speech, not your recording), the Hindi adaptation after your review, and the pipeline measures every duration, checks the audio with the speech recogniser, aligns it and writes both subtitle files. Your own reading of the lines can be recorded as a listening reference but never counts as validation of the speech model.
