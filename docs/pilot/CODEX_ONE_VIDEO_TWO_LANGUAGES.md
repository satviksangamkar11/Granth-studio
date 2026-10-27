YES — one picture track can serve both languages, provided the finished mixes and player support are verified.  
The biggest change is to give Kimi the **shared bilingual beat timeline** and finish the audio and delivery pipeline around it.  
Do **not** speed up speech, make Kimi invent timings, or burn language-specific captions into the shared picture.

**Timing.** I compared all 62 measured Marathi/Hindi line pairs. Hindi is longer in 35, Marathi in 24, and three are equal; 28 Marathi clips and 31 Hindi clips individually exceed six seconds. All pairs use the same voice ID across languages. The measured file calls the voices **draft, not owner-validated**, despite having no recorded measurement problems. [Measured manifest](</D:/aai work/granthstudio/canon/audio/A1_eleven_measured.json:2>)

The 59-shot timeline includes **52 core lines**, not all 62: it leaves out ten optional lines. At their scheduled starts, speech crosses the next six-second picture cut in **38 starting shots in each language**. That is permitted: a line can continue over a cut. No included measured clip exceeds its assigned *common beat* in my calculation. A shot labelled “visual only” means no line **starts** there; speech can still be continuing over it. [Timing builder](</D:/aai work/granthstudio/scripts/source/a1_audio.py:158>)

For each scene, the following figures are Marathi / Hindi / common timeline in seconds, followed by the number of starting shots where speech crosses a cut. Scene totals include the plan’s pauses; they are rounded.

- S1: 7.4 / 7.7 / 7.7; 1 crossing shot.
- S2: 41.7 / 42.0 / 43.3; 5.
- S3: 30.2 / 29.9 / 30.6; 4.
- S4: 27.9 / 29.2 / 29.3; 3.
- S5: 37.5 / 41.1 / 41.3; 4.
- S6: 29.0 / 29.5 / 30.5; 4.
- S7: 47.9 / 49.2 / 50.0; 7.
- S8: 28.2 / 28.3 / 28.9; 3.
- S9: 59.5 / 61.5 / 63.6; 7.

In S1 the Marathi/Hindi crossing is the same shot; the same is true for each count above. The maximum difference between corresponding included lines ranges from 0.32 seconds in S1 to 1.52 seconds in S9. The scene figures and budgets are recorded in the [audio plan](</D:/aai work/granthstudio/docs/pilot/A1_audio_plan.md:5>).

**Conclusion on 59 shots:** the current numbers fit the **52 core lines** within every scene’s allocated picture time, assuming the measured files are the final accepted clips. They do not prove that all 62 lines fit, or that every visual cut feels right. Keep the frozen six-second renders; use a suitable continued view or held pose over long lines and add six-second shots only if an approved line or visual beat needs them. Do not shorten or stretch individual renders just to match speech. If the owner wants any optional lines included, rebuild and approve the timing first.

Use this rule: **each shared beat is sized to the longer measured line, followed by the planned pause; both versions start at the same beat.** The shorter version rests in silence or a shared ambience bed until the next beat. The current builder uses a half-second lead, half-second gaps and half-second tail. [Timing code](</D:/aai work/granthstudio/scripts/source/a1_audio.py:31>)

**Audio.** Keep the same cast in both languages, the EASY wording, and shared effects and ambience. Listen especially where the shorter line finishes substantially earlier, and at scene tails: use room tone or a gentle bed where a hard silence feels abrupt. The same cue must be checked against **both** speech windows; the plan disallows effects over speech unless the owner approves ducking. [Final plan](</D:/aai work/granthstudio/docs/pilot/FINAL_PLAN.md:23>)

The existing code is **partly ready**:

- ElevenLabs can produce a measured manifest and export clips into the WAV layout the mixer expects. [Measurement and export](</D:/aai work/granthstudio/scripts/source/a1_eleven.py:214>)
- `a1_voice.py mix` places both languages at the same beat starts, pads each track to picture length and rejects overlap or scene overflow. It produces two separate audio files, not the finished multitrack film. [Mixer](</D:/aai work/granthstudio/scripts/source/a1_voice.py:125>)
- `--target-dbfs -22` is optional active-speech balancing, with gain limits; a subsequent whole-track peak normalization can change the final level. Therefore **−22 dBFS at delivery is not established**: measure the finished tracks and correct the gain stage if required. [Gain and normalization](</D:/aai work/granthstudio/scripts/source/a1_voice.py:113>)
- Still missing from this path: accepted shared bed/effects placement and checking against both languages, finished-track verification, selectable subtitles, and a verified one-file multistream assembly. The repository evidence reviewed does not establish that these are already completed.

**Kimi’s contract.** It is **partly** in place. Code already supplies fixed six-second slots and identifies where narration starts; Kimi is constrained to held-pose-capable shots. But the current packet gives Marathi wording and shot starts, not both measured line lengths and complete crossing windows. Its schema also asks for Marathi dialogue text, while the final plan identifies a blocker: the validator expects verse substrings instead of approved EASY line IDs. [Director packet](</D:/aai work/granthstudio/scripts/source/director_test.py:520>), [schema](</D:/aai work/granthstudio/scripts/source/director_test.py:68>), [known blocker](</D:/aai work/granthstudio/docs/pilot/FINAL_PLAN.md:42>)

Give Kimi, per scene, the fixed slots, shared beat IDs and start/end windows, both measured durations, and which lines continue across each cut. Require actions and held poses to suit the shared meaning in both languages; code owns timing, dialogue and captions. Kimi chooses presets, images and staging once. Preserve the frozen builder and the owner’s limits on paid calls and reruns. [Final director contract](</D:/aai work/granthstudio/docs/pilot/FINAL_PLAN.md:34>), [decisions](</D:/aai work/granthstudio/docs/DECISIONS.md:71>)

**Captions and delivery.** For a shared picture, create separate selectable Marathi and Hindi subtitle tracks, timed against their respective speech. The current plan specifies the on-screen year **1878** and has Marathi/Hindi caption fields; it does not establish a finished selectable-subtitle workflow. The year can be language-neutral if the owner approves its presentation. [Decision](</D:/aai work/granthstudio/docs/DECISIONS.md:85>), [caption validation](</D:/aai work/granthstudio/scripts/source/a1_audio.py:111>)

Target one master file containing one video stream, two labelled audio streams and two labelled subtitle streams. **MP4/MKV player, YouTube and WhatsApp support: UNKNOWN from the repository evidence reviewed.** Test the actual destinations. If a destination cannot switch tracks, keep the single multitrack master and, only for that destination, export two language-specific delivery copies from the **same picture master**; that does not require directing or rendering two films.

**Decisive test.** Use one scene with crossing speech, such as S4: direct it once, render its five shared shots, and make both language mixes and subtitle tracks. Check every line is complete, beat starts agree, no speech is cut at shot or scene boundaries, both tracks end with the picture, captions match, cues avoid both speech windows, and final loudness and peaks meet the owner’s target. Interrupt the render or assembly, resume it, and compare the result with an uninterrupted run. The plan explicitly lists render recovery as work still to fix. [Recovery backlog](</D:/aai work/granthstudio/docs/pilot/FINAL_PLAN.md:47>)

Two separately directed picture versions would be necessary only if the owner requires incompatible language-specific visuals or timing that cannot be accommodated by shared held poses and cuts. A platform’s inability to switch tracks alone calls for delivery copies, not separate productions.

**Ordered changes**

1. **Owner:** confirm the EASY wording, voice performances and whether the ten optional lines belong in the film. [Final plan](</D:/aai work/granthstudio/docs/pilot/FINAL_PLAN.md:23>)
2. **Claude:** rebuild and verify [timing](</D:/aai work/granthstudio/scripts/source/a1_audio.py:146>) from the accepted hashes; owner approves shot count and timeline.
3. **Claude:** update [director prompt and validator](</D:/aai work/granthstudio/scripts/source/director_test.py:520>) to pass bilingual beat windows and use approved line IDs; owner reviews the contract.
4. **Kimi:** direct one scene against those slots; **owner** approves the scene before the rest.
5. **Claude:** verify [WAV export and mixer](</D:/aai work/granthstudio/scripts/source/a1_eleven.py:232>), correct final loudness behavior and add shared beds/effects with bilingual collision checks; owner approves the sound.
6. **Claude:** generate and verify separate subtitle tracks and neutral year treatment; owner approves wording and appearance.
7. **Claude:** assemble and inspect the one-picture, two-audio, two-subtitle master; test target players and platforms with the owner.
8. **Claude and owner:** run the one-scene interruption/resume and listening test; resolve any failed checks before directing and rendering the remaining scenes. Apply the same process to Adhyay 2 after its own clips and timing are measured.