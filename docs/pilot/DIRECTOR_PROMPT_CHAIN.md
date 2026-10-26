# Director prompt chain (APPROVED as D-018, 2026-10-25)

> **AMENDED 2026-10-26 (D-018 A3, owner answers; supersedes the older text below where they differ):** characters speak ONLY exact Marathi ovi words (no paraphrase in dialogue; the narrator carries paraphrase, thoughts and unclear speech); every shot is exactly 6 s from the 11 presets (no variable shot seconds); each scene is directed ONCE with at most one repair round (no revise loops); STAGING may only propose scenery/light/pose/camera and the owner approves it; Kimi is the director and Nemotron only cross-checks. The live prompts are in `scripts/source/director_test.py` (RULES, CAPS, SCHEMA_TEXT, REVIEW_SYS); Phase 2 moves them to `prompts/director/`.


Status: owner approved "as is" on 2026-10-25. No director model has run yet.

Built from two research sets:
- `D:/kaggle_upload/repo_research/director_prompts/REPORT.md`: how film-agent repos break a text into stories, scenes and shots.
- `D:/kaggle_upload/repo_research/story_prompts/REPORT.md`: what makes the telling engaging, and what bores.

The prompts below are written fresh for the Granth. Credit for the ideas:
- ViMax (MIT): event extraction "every detail supported by the input"; one scene per call; show, don't tell; no metaphors.
- CineCrew (Apache-2.0): fixed IDs as the "truth anchor"; repair only unknown IDs; dialogue never paraphrased.
- VideoClaw/FilmAgent (MIT): plan first, then write; review-and-revise loop; scene dialogue goal.
- EQ-bench longform (MIT): negative criteria.
- ShortGPT and MoneyPrinterTurbo (MIT): hook first, no preamble.

No prompt text is copied verbatim from repos without a licence.

## 1. The idea in one picture
```
approved ovis (facts) ─┐
Wikipedia story map ───┤ (a hint only: which stories to expect)
characters / places ───┤ (fixed IDs)
presets index ─────────┘ (closed list of shot types)
        │
  S1 Story map       director model   → events with ovi ranges
  S2 Episode plan    director model   → how this Adhyay is told: hook, order, coverage
  S3 Scene cards     director model   → one call per scene: goal, turn, beats, narration draft
  S4 Shot lists      director model   → one call per scene: preset, assets, action, timing
  S5 Validator       code (no model)  → IDs, ovi numbers, quotes, presets, durations, coverage
  S6 Cross-check     second model     → fidelity and storytelling rubric, PASS/FAIL per scene
       └─ FAIL → director revises once or twice (max 2 rounds) → otherwise goes to the owner
  S7 Owner review (Gate 1)            → approve / mark changes per scene
```
Facts come only from the approved ovis. The Wikipedia summary only tells the director which stories to look for. If it disagrees with the ovis, the ovis win and the mismatch is flagged.

## 2. Inputs (files the code builds; the model never fetches anything)
| File | Contents | Exists? |
|---|---|---|
| `canon/source/adhyay_NN.jsonl` | `{adhyay, ovi, marathi, meaning_en, approved:true}` per ovi, owner-approved | **No.** Adhyay 1 needs it first |
| `canon/characters.yaml` | `char_id`, names as they appear in the text, role, look notes, image refs | **No** (canon is empty) |
| `canon/places.yaml` | `place_id`, name, look notes, image refs | **No** |
| `docs/pilot/research/STORY_MAP_FROM_WIKIPEDIA.md` | expected stories per Adhyay | Yes |
| `assets/v5_presets/index.json` | the 11 shot presets and their asset roles | Yes |

## 3. Shared rule blocks (pasted into every director call)

### 3a. FIDELITY RULES
```
FIDELITY RULES (facts)
F1. The approved ovis are the only source of facts. Every name, place, time, number, action, spoken line and outcome must cite ovi numbers.
F2. Refer to people and places ONLY by the IDs in CHARACTERS and PLACES. Never invent, merge, pluralise or re-spell an ID. If someone in the ovis has no ID, list them under "missing_ids"; do not make one up.
F3. Spoken lines: copy the Marathi ovi words exactly, or write a paraphrase and mark it "paraphrase": true. Never put words in a mouth that the ovis do not give.
F4. Motives, feelings and thoughts appear only where an ovi states them.
F5. Miracles are shown plainly, with the cause the ovi gives and no other (no glow, slow motion or light rays that suggest a cause).
F6. Where an ovi is unclear, stay neutral and add it to "questions_for_owner". Do not choose a reading.
F7. The Wikipedia hint is not a source. Use it only to know which stories to expect. If it disagrees with the ovis, follow the ovis and report the mismatch.
F8. Every telling choice that is not a fact (camera, light, a neutral prop such as a lamp, scene order, a held moment) is written on a line starting "STAGING:".
F9. An Adhyay boundary never invents an ending. A story that continues in the next Adhyay stays open.
F10. When a storytelling rule conflicts with a fact, the fact wins.
```

### 3b. STORYTELLING RULES (adapted from the research block, 24 lines)
```
STORYTELLING RULES (the telling only)
T1. Open on the most striking concrete moment of the Adhyay, or the question its ovis raise, within 10 seconds. No intro, no recap, no "welcome".
T2. Raise one open question early and answer it later. Use only questions the ovis raise.
T3. Every scene must change something: the situation, a person's state, or what the viewer understands. Otherwise merge or cut it.
T4. The stakes are what the ovis state (hunger, illness, pride, a vow, a village). Never add a threat.
T5. Build scenes on contrast: ordinary vs miraculous, pride vs humility, noise vs stillness.
T6. Rhythm: alternate one long hold (6–10 s on a face, a gesture, or Maharaj) with short beats (1–3 s). Never use the same scene shape three times in a row.
T7. Each shot has exactly one visible action, written as a verb. Nothing stays still for more than 1 s except the final hold and approved contemplative holds.
T8. Put the emotional peak on the ovi that carries the turn. Hold it 2–3 s, then release.
T9. Show feeling through actions the ovis support. Do not name a feeling in narration when an action can carry it.
T10. Narration: plain, warm, short spoken sentences, like an elder telling the story. No stacked adjectives, no metaphor the ovi lacks, no ornate language.
T11. Teaching comes after the viewer has felt the stake: show the choice and its result, then one short ovi-cited line. Never let a lecture run past one narration beat (8–10 s) without a picture change.
T12. Long teaching passages: narration over typography, symbols named in the text and contemplative holds. Never an invented scene.
T13. Use an ovi-quoted refrain at scene boundaries so listeners can follow along.
T14. Callbacks: bring back one object or sound from an earlier scene at a later turn, only if the ovi names it or it is a neutral STAGING prop.
T15. Every setup shown (a vow, an object, a question) is paid off in the same story, or left out.
T16. Close on the outcome the ovi states, then the closing ovi or a refrain. No moral the ovi does not state, no cliffhanger that invents a threat.
T17. Cut scenes at the end of a narration sentence, never in the middle.
T18. Prefer continuous transitions (the same object carried across the cut) to generic wipes.
T19. Prefer one visual idea that develops through the Adhyay to a list of unrelated pictures.
T20. Consecutive Adhyays never end with the same closing device.
T21. Ask of every shot: is the action clear at normal speed without explanation?
T22. Ask of every scene: would a listener who has not read the ovis still follow it?
T23. Use the ovi's own words for the key line of each scene, quoted and cited.
T24. If a telling choice would change how an ovi is read, drop it.
```

## 4. Stage prompts

### S1. Story map (one call per Adhyay)
```
ROLE: You are the story editor for a devotional film of one Adhyay of Shri Gajanan Vijay. You break the Adhyay into its events. You do not write scenes yet.
INPUT: <OVIS> approved ovis of Adhyay {N}: number, Marathi, approved English meaning </OVIS>
       <HINT> expected stories from a secondary summary (not a source) </HINT>
       <CHARACTERS>…</CHARACTERS> <PLACES>…</PLACES>
TASK:
1. Give every ovi exactly one type: INVOCATION | STORY | TEACHING | RECAP | PHALASHRUTI | OTHER.
2. Group consecutive STORY ovis into events. One event is one causal chain with one dramatic goal, even if it moves between places.
3. For each event, give: event_id, title (max 8 words), ovi_range, key_ovis (the 1–3 ovis that carry the turn), char_ids, place_ids, cause, outcome (each with ovi numbers), and continues_from / continues_to (another Adhyay) only if the ovis say so.
4. Compare with HINT: list hint stories you found, did not find, or found differently.
{FIDELITY RULES}
OUTPUT: JSON only, matching schema S1. No text before or after.
```
S1 schema: `{adhyay, ovi_types:[{ovi,type}], events:[{event_id, title, ovi_range:[a,b], key_ovis, char_ids, place_ids, cause:{text,ovis}, outcome:{text,ovis}, continues_from, continues_to}], hint_check:[{hint, status: found|missing|different, note}], missing_ids, questions_for_owner}`

### S2. Episode plan (one call per Adhyay; this is the "director" step)
```
ROLE: You are the director. Given the story map, decide HOW this Adhyay is told as a {target_min}-minute film. You are choosing the telling, not changing the facts.
INPUT: S1 output, the OVIS, and the previous Adhyay's closing device (to avoid repeating it).
TASK:
1. Hook: the moment we open on (ovi numbers) and why it pulls the viewer in.
2. Open question: one question raised early, answered later (ovi numbers for both).
3. Shape: the structure for the telling (for example set-up/turn/payoff, or kishotenketsu where the "twist" is an ovi fact that changes how an earlier scene reads). One line on why.
4. Scene list in viewing order: scene_id, event_id, ovi_range, goal, turn (with ovis), scene_shape (setup | held_image | action | reveal | teaching), estimated seconds.
   Change the order from the text only where the ovis do not fix the order, and mark it STAGING.
5. Coverage: give every ovi one disposition: VISUALISED | NARRATED | QUOTED | MERGED_EQUIVALENT | PROPOSE_OMISSION (with reason; only the owner approves omissions).
6. Ending: the outcome ovi and the closing device; it must differ from the previous Adhyay's.
7. Total duration. If the Adhyay will not fit {target_min} without cutting meaning, say so and propose a duration exception. Do not rush or cut meaning.
{FIDELITY RULES}
{STORYTELLING RULES}
OUTPUT: JSON only, schema S2.
```

### S3. Scene card (one call per scene)
```
ROLE: You are the screenwriter. Write ONE scene card for scene {scene_id}. Write only this scene.
INPUT: S2 entry for this scene; only the ovis in its range plus 3 ovis of context on each side; the previous scene card (for continuity); CHARACTERS; PLACES.
TASK:
1. Beats in order (3–8). For each: what we see (one visible action, a verb), char_ids, ovi_ids, and an optional STAGING line.
2. Narration lines for this scene, in Marathi first, then Hindi. Each line has ovi_ids. Mark every line DRAFT (owner approves wording). Key line: quote the ovi.
3. Spoken lines: exact ovi words, or marked paraphrase (F3).
4. The turn: the beat where things change, its ovi number, and the held moment (2–3 s).
5. Refrain or callback, if any (T13, T14).
6. Visuals needed: for each beat, the pose or picture needed (char_id + pose words, or place_id + view), so the owner knows which images to make.
{FIDELITY RULES}
{STORYTELLING RULES}
OUTPUT: JSON only, schema S3.
```

### S4. Shot list (one call per scene)
```
ROLE: You are the cinematographer. Turn the scene card into shots, using ONLY the presets listed.
INPUT: S3 card; PRESETS (name, use, asset roles); narration lines with estimated spoken seconds.
TASK: for each shot give:
- shot_id
- beat index
- ovi_ids
- preset: one name from PRESETS, exactly as written
- assets: role → char_id/place_id + pose words
- action: one verb phrase
- seconds: 2–10; the final hold may run to 12
- narration_line ids it covers
- transition_out: cut | slide | pan_bridge
Rules:
- Open the scene on a wide or establishing preset unless the hook needs a close-up.
- Do not put more than 2 close-up presets (07, 08, 10) in a row.
- Cut on the end of a narration sentence.
- Never ask for lip-sync (not supported).
- If no preset fits a beat, write "preset": "NEED_NEW" and explain. Do not invent a preset name.
{FIDELITY RULES F1–F3, F8}
OUTPUT: JSON only, schema S4.
```

## 5. S5 validator (code, no model; Claude writes it, Codex reviews it)
- Every `char_id`, `place_id` and preset name exists in its file.
- Every ovi number is inside the Adhyay. Every event and scene range is contiguous and inside its parent.
- Every ovi has exactly one disposition. PROPOSE_OMISSION is listed for the owner.
- Quoted spoken lines and key lines string-match the approved Marathi text, after whitespace normalisation.
- Every narration line has at least one ovi id.
- Shot seconds are within limits; the scene total is within ±15% of S2's estimate; the Adhyay total is reported.
- No three consecutive scenes share a `scene_shape`. The closing device differs from the previous Adhyay's.
- A list of banned words in English notes (glow, divine light, suddenly, magical, …) is flagged for the critic, not auto-failed.

A failure returns to the model as a precise list (CineCrew pattern: "fix only these; change nothing else"). After 2 rounds it goes to the owner.

## 6. S6 cross-check (a second model, a different family from the director)
The second model receives one scene card + shot list + only the cited ovis. It answers yes or no with a quote for each:
```
FIDELITY
1. Every fact, name, place, number, spoken line and outcome cites an ovi or is marked STAGING?
2. Nothing is claimed that the cited ovis do not support? (list unsupported_claims)
3. No motive or feeling appears without an ovi stating it?
4. The miracle is shown with only the cause the ovi gives?
5. Unclear ovis are left neutral and listed as questions?
STORYTELLING
6. (episode level) Opens within 10 s on an ovi-grounded moment, no intro?
7. The scene has a goal and a turn that changes something?
8. Each shot is one visible action; no still shot longer than 1 s except the approved holds?
9. Feeling is carried by action, not named in narration?
10. Narration has no invented metaphor, stacked adjectives or sermon?
11. Teaching comes as a consequence, with no lecture over one beat without a picture change?
12. Every setup is paid off or dropped?
13. The ending closes on the ovi outcome, with no invented threat or triumph?
14. Shape and closing device are varied?
OUTPUT JSON: {scene_id, verdict: PASS|FAIL, failed:[numbers], unsupported_claims:[{text, why}], fixes:[{where, change}]}
```
- PASS needs 1–5 all yes. 6–14 may fail with a note; the owner decides.
- If the director and the critic still disagree after 2 rounds, both views go to the owner. The models never settle it between themselves.

## 7. Owner review (Gate 1, per Adhyay)
One page per Adhyay:
- the hook and the ending
- the scene list with ovi ranges
- PROPOSE_OMISSION items
- questions_for_owner
- critic notes
- Marathi/Hindi DRAFT narration
- the image list (which poses and places to make in Flow)

The owner approves or marks changes. Nothing goes to images or rendering before this.

## 8. Models (to pick by a small test, not by guess)
- Director: one strong reasoning model on the free NVIDIA endpoints. Critic: a model from a different family, so their blind spots don't overlap.
- Candidates from earlier runs: z-ai/glm-5.3, deepseek-ai/deepseek-v4.1-flash, nvidia/nemotron-3-ultra. (moonshotai/kimi-k2.6 returned 404 on our key.)
- Test: S1 + S2 on Adhyay 1 with 2 director candidates; each output is critiqued by the other. The owner picks by reading. Cost $0 (free endpoints; trial terms flagged before any publishing).
- Calls per Adhyay ≈ 2 + 2 × scenes + critic calls ≈ 20–40. Well inside 14 keys × 10 requests a minute.

## 9. Blocking before any run
1. **Adhyay 1 approved text**: `adhyay_01.jsonl` with Marathi + approved meaning for all 146 ovis. Today only ovi 84–121 is transcribed, and it is unapproved.
2. **characters.yaml / places.yaml** for Adhyay 1: Maharaj, Bankatlal, Damodarpant; Shegaon street, Bankatlal's house.
3. Owner approval of this document, then Codex review of the small runner + validator before they run.
4. Still open, not blocking a private test: rights/Sansthan permission and the NVIDIA trial terms before publishing.
