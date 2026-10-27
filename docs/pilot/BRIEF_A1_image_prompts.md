# Brief: Adhyay 1 image prompt list for Nano Banana (Google Flow) - drafts for the owner

## Goal
The owner makes EVERY image by hand in Nano Banana (Google Flow). Produce the complete, ordered, reuse-minimal list of image prompts for Adhyay 1 of "Shri Gajanan Vijay" so the owner can generate the images directly and move on to animation (code renderer) and audio (ElevenLabs). You write PROMPTS and a catalog; you generate no images, call no paid service and change no repository file except your two output files.

## Read first (repo `D:\aai work\granthstudio`, read-only)
- Story and scenes: `docs/pilot/A1_story_for_approval.md` (ONE story, nine scenes S1-S9, ovi 70-144), `canon/story_split_edits/A1_rev1.json` (direction_notes, scene goals), `docs/pilot/A1_full_script_simple.md` (the owner's EASY spoken script, 62 lines, speakers), `canon/audio/A1_audio_plan.json` (18 sound cues: tells you which props/events matter on screen).
- Frozen research (authoritative; the owner has settled these): `canon/packets/adhyay_01/frozen_copies/adhyay_01_FINAL_answers.md` FIRST (settled decisions), then `adhyay_01_analysis_v3.md`, `adhyay_01__adhyay_01_video_gaps_addendum.md`, `characters_1to12_FINAL.md`, `glossary_user_supplied.md`, `verification_report.md`; ovi text `canon/packets/adhyay_01/adhyay_01_ovis_hj.jsonl`. Where an older passage contradicts a FINAL answer, the FINAL answer wins. Where the research states no value (e.g. Maharaj's numeric age, the metal of the water vessel) do NOT decide it silently: mark it OWNER_CHOICE and propose a default.
- Renderer constraints (so every image is animatable): `assets/v5_presets/README.md`, `index.json`, the 11 preset JSONs (they list the image ROLES each preset needs, e.g. background/midground/foreground/character layers, and what motion is possible), `canon/style.yaml`, D-016 and D-017 in `docs/DECISIONS.md`. The renderer makes 6-second shots (144 frames, 24 fps, 1280x720 target) from still images; there is NO limb animation, lip-sync or facial change inside a shot: pose changes happen between shots, so each needed pose is a separate image.
- Existing look references the owner already made: `D:/aai work/v5_inbox/` and `D:/aai work/pilot_refs/` and `assets/pilot_refs/set_v1` (view a few images to match the established look: flat original art direction; do not invent a new style).
- Never open `D:\aai work\secrets`.

## Rules (hard)
1. Never invent Granth content: every person, object, place, light and event in an image must come from an ovi of that scene, the FINAL answers, or be a clearly labelled STAGING/OWNER_CHOICE proposal (scenery, light, pose, camera only; never a new person, object, event or cause).
2. No dates beyond the year caption 1878; no modern items; no text inside images; no written Marathi in images (captions are added later); respectful depiction of a saint (no halo or supernatural glow unless the research states it).
3. Speakers/dialogue: only the four recurring characters speak (Gajanan Maharaj, Bankatlal Agarwal, Damodarpant Kulkarni, plus the narrator off-screen). Devidas's household, villagers and others are background figures only where the research places them.
4. Reuse hard: one reference sheet per recurring character and per place, then shot images reuse them; list which shot images can be derived from the same character image by changing only the background layer. Give a de-duplicated final count and the reuse map (shot -> image ids per preset role).
5. Consistency block: write ONE reusable style paragraph and ONE visual-identity paragraph per character/place (clothes, colours, build, posture, props) that every prompt for that subject repeats verbatim, so images stay consistent in Nano Banana. Prompts are self-contained English text for Nano Banana, plus 'image reference to attach' instructions (which earlier output to feed back as a reference).
6. Provisional shot list: the exact shot count may change after the voices are timed (current plan 61 shots). Therefore organise shot images by SCENE BEAT (one image per distinct visual beat, with the preset and roles it serves), not by final shot number, and say how many shots each image can cover.

## Output files (write ONLY these two)
1. `docs/pilot/A1_image_prompts.md` - human-readable for the owner: (a) style paragraph, (b) generation order (references first: characters, costume/pose sets, places, props, then scene beat images), (c) for each image: id, kind (character_ref | pose | costume | location | prop | beat_still), scene(s), preset roles it serves, the full Nano Banana prompt, reference images to attach, aspect ratio / layer notes (transparent background where a preset needs a cutout layer), source refs (ovi numbers / FINAL answer ids), OWNER_CHOICE flags, (d) the questions list for the owner (all unsettled looks in ONE list with your proposed default), (e) totals (images by kind, reuse map).
2. `canon/drafts/A1_image_catalog_DRAFT.json` - the same catalog machine-readable: [{image_id, kind, scenes, preset_roles, entities, prompt, references, source_refs, owner_choice, status: "DRAFT_NOT_APPROVED"}].
Mark everything DRAFT, NOT APPROVED; the owner approves.

## Finish with
A reply under 200 words: counts, the 5 biggest owner questions, and anything in the research that blocked you.
