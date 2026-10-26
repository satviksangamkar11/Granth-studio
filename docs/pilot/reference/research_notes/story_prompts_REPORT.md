# Storytelling research for the director/screenwriter LLM (GranthStudio)

Written by the Haiku research agent on 2026-10-25 and saved by Claude. The agent was refused writing this file, so this is its returned text, lightly condensed.
Goal: rules for how the Shri Gajanan Vijay Granth stories are told. The plot, facts and verse citations stay fixed.
Legend:
- V = checked directly in the repo or paper.
- S = search summary or secondary source; verify before quoting.
- M = general knowledge, not checked.

The GitHub API was rate-limited, so commit SHAs are not recorded. Each prompt file header gives the branch and fetch date.

## 1. Sources
| # | Source | Licence | Status | What it contributes |
|---|---|---|---|---|
| 1 | google-deepmind/dramatron | Apache-2.0 / CC-BY 4.0 | V | Chain: logline → characters → scenes → places → dialogue. Playwrights called the output "formulaic"; useful for structure, not final text |
| 2 | yangkevin2/emnlp22-re3-story-generation | MIT | V (gains S) | Plan → Draft → Rewrite (rerank) → Edit |
| 3 | yangkevin2/doc-story-generation | MIT | V repo / S results | Detailed layered outline, then a controller that keeps the draft faithful (prompts in story_generation/plan_module/outline.py, not extracted) |
| 4 | HKUDS/ViMax | MIT | V | Each scene needs its own conflict or progression; show, don't tell; every shot has a narrative purpose; the first shot sets up the place; at most one line per character per shot |
| 5 | HITsz-TMG/VideoClaw (was FilmAgent) | MIT | V | Each scene gets a dialogue goal so it ends naturally; concise, no clichés, few lines; the shot reviewer breaks up runs of close shots |
| 6 | showlab/MovieAgent | no licence | V | Scene = self-contained unit with a distinct purpose; synopsis split without rewording. **Paraphrase only** |
| 7 | Anim-Director | n/a | S | No code found |
| 8 | Agents' Room (ICLR 2025) | n/a | S | Planning agents before writing agents |
| 10 | THUDM/LongWriter AgentWrite | Apache-2.0 | V | Plan with per-paragraph word counts, then write each paragraph with the plan and the text so far |
| 11 | EQ-bench longform-writing-bench | MIT | V | Judge rubric with 16 criteria plus negative criteria |
| 12 | EQ-bench creative-writing-bench v3 | licence not found | V | 22 criteria and a slop list. **Paraphrase only** |
| 14 | RayVentura/ShortGPT | MIT | V | "Friend telling a story"; one hook line, then facts; "do not end with a moral" |
| 15 | harry0703/MoneyPrinterTurbo | MIT | V | No preamble, no "welcome to this video", no markdown |
| 17–21 | HANNA (Chhun 2022), Chhun 2024, "The Reader is the Metric" 2025, story-eval survey, TTCW | papers | S | Human criteria: Relevance, Coherence, Empathy, Surprise, Engagement, Complexity. Lay readers and expert readers reward different things |
| 22 | local dbc animate skill | local | V | Motion and rhythm rules |
| 23–28 | Kishotenketsu, Story Circle, Save the Cat (M), Pixar rules, oral-formulaic theory, Panchatantra | various | S/M | Structural shapes; refrains help memory; the lesson comes after the tale |

Not found: code for Anim-Director and Agents' Room, and any openly licensed repo for short-form hooks or retention. Vendor retention figures are unverified; do not quote them.

## 2. Rules that recur and work
1. **Hook in the first 5–10 s.** Open on the most striking concrete moment, never a title card or recap (#14, #15).
2. **Open loops, then close them.** Use only questions the verses raise (#14, #2, #22).
3. **Every scene has a goal, a conflict and a turn.** A scene that changes nothing is merged or cut (#4, #5, #6).
4. **Stakes come from the story, not from invention.** A victory has a visible cost (Story Circle "Take"). A miracle with no felt need reads like a news bulletin.
5. **Contrast as structure.** Ordinary vs miraculous, pride vs humility, noise vs stillness. A twist must be a verse-stated fact that changes how an earlier scene reads (kishotenketsu "Ten").
6. **Rhythm** (#22):
   - Nothing stays still for more than 1 s except the ending.
   - One action per shot.
   - Keep the climax short, 2–3 s.
   - Don't repeat one scene shape three times.
   - Prefer one evolving visual idea.
7. **Emotion shown through action.** Peaks are held briefly (#4).
8. **Motifs and callbacks.** Decide the ending before writing the middle (Pixar).
9. **Endings pay off every setup.** The teaching is shown as a consequence, not added as a sermon.
10. **Narration voice:** plain, warm, short sentences. Show the choice, then give one verse-cited line. Verse refrains at scene boundaries. No lecture longer than about 8–10 s without a visual change. Teaching comes after the stake.
11. **Plan before prose** (Re3, DOC, AgentWrite, Agents' Room, FilmAgent): director pass → screenwriter pass → shot pass → critic pass.

## 3. What does not work (documented)
1. Formulaic output; letting the model write autonomously (Dramatron).
2. Purple prose, forced poetry, metaphor (both EQ rubrics; ViMax).
3. Naming emotions instead of showing them.
4. Unearned transformations, such as a devotee's change with no verse behind it.
5. Unsurprising, formula-heavy writing; weak or meandering dialogue.
6. An upbeat ending the source does not support.
7. Flat pacing, empty frames, still shots longer than 1 s.
8. Over-explaining: restating the lesson after every beat.
9. Repetition: the same closing device every episode, the same scene shape three times.
10. Generic wipes and irises; continuous physical transitions work better.
11. Ignoring that lay and expert readers want different things.
12. Phrases leaked from training data; check them against the verse text.
13. Melodrama: show emotion only where the verse shows it, and hold it 2–3 s at most.

## 4. Adapting to fixed facts
**Can change (the telling):**
- The entry point.
- Scene order, only where the verses do not fix the order; a flash-forward is marked STAGING.
- The structural shape.
- Pacing, staging and camera.
- Neutral props.
- Narration style.
- Where emotional beats are placed.
- Refrains.
- How the teaching is shown.

**Never changes (the facts):**
- Characters and names.
- Places and times.
- Miracle outcomes and causes (no glow or slow motion that implies a cause).
- Dialogue: verse-quoted, or marked as paraphrase.
- Motives and inner states not stated in the verse.
- Endings: no invented threat, sequel hook or triumph.
- What the teaching says.
- No merging of stories without citing both.

**Pipeline:**
- Each scene card lists the verse numbers, the goal, the turn and a STAGING line for every telling choice.
- The critic separates facts from staging.
- When a borrowed rule conflicts with a fact, the fact wins.

## 5. Ready blocks
The 39-line STORYTELLING RULES block and the 10-question critic rubric are reproduced (adapted) in `D:/aai work/granthstudio/docs/pilot/DIRECTOR_PROMPT_CHAIN.md`.

## 6. Prompt files saved here (licensed sources only)
- dramatron (Apache-2.0): custom_prefixes_cell12.txt
- Re3 (MIT): plan_module_prompt_lines.txt
- ViMax (MIT): screenwriter_prompts.txt, storyboard_artist_system_prompt.txt
- VideoClaw/FilmAgent (MIT): screenwriter_1..5, director_1, director_2, shot_review, COT_script
- LongWriter (Apache-2.0): agentwrite_plan, agentwrite_write
- EQ-bench longform (MIT): criteria, negative criteria, judging prompt, chapter prompts (7 files)
- ShortGPT (MIT): chat_video_script, reddit_generate_script, facts_generator
- MoneyPrinterTurbo (MIT): default_script_system_prompt, build_script_prompt_function

Not saved:
- MovieAgent: no licence.
- EQ creative bench: licence not found.
- slop-score: NOASSERTION.
- DOC: prompt strings not extracted.
- PlotMachines.

## 7. Caveats
- S-level claims need checking against their sources before they are quoted: Re3/DOC gains, HANNA criterion names, Pixar wording and the Story Circle steps.
- The Save the Cat beat names are from memory.
- Rules borrowed from short-form video ("spicy", "no moral") were toned down for devotional material.
