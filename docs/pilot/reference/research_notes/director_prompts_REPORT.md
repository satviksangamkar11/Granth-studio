# Director prompt research — report (from the Haiku research agent, saved by Claude)

Saved files: 33 prompt files in 8 repo folders here. 23 VERBATIM (MIT/Apache-2.0, attribution required), 10 PARAPHRASE (no licence: rewrite from scratch, never copy). Each file starts with a SOURCE line (URL, commit, licence).

## Repos
| Repo | Licence | Last commit | Stars | Status |
|---|---|---|---|---|
| github.com/HKUDS/ViMax | MIT | 2026-09-30 | 12,750 | saved (6 verbatim) |
| github.com/Ironieser/CineCrew | Apache-2.0 | 2026-09-29 | 15 | saved (5 verbatim) |
| github.com/HITsz-TMG/VideoClaw (was FilmAgent) | MIT | 2026-08-26 | 1,877 | saved (5 verbatim) |
| github.com/X-PLUG/MM_StoryAgent | Apache-2.0 | 2024-08-23 (stale) | 309 | saved (3 verbatim) |
| github.com/showlab/Code2Video | MIT | 2026-08-24 | 2,167 | saved (4 verbatim, off-domain) |
| github.com/EngineeringAI-LAB/Look-Before-Move | none | 2026-09-30 | 4 | paraphrase only |
| github.com/HITsz-TMG/Anim-Director | none | 2026-01-07 | 264 | paraphrase only |
| github.com/showlab/MovieAgent | none | 2025-03-26 | 371 | paraphrase only |
| github.com/HKUDS/VideoAgent | MIT | 2026-07-22 | 1,973 | surveyed, not storyboard |
| ArcReel/ArcReel | AGPL-3.0 | not verified | ≈5.7k | not analysed |
| lichao-sun/Mora | none found | not verified | ≈1.6k | text-to-video only |
Not found as code: StoryAgent (paper only), AesopAgent (paper only), DreamFactory (unrelated project). GitHub search was rate-limited: sweep not exhaustive.

## Where prompts live
ViMax: `agents/*.py` constants (event extraction, character extraction/merge, screenwriter, scene extractor, script planner, enhancer, storyboard artist, camera, best-image selection). CineCrew: `src/agents/<agent>/*.yaml` + `configs/knowledge/rules/common/*.md` (asset IDs as truth anchor, DSL validator). VideoClaw: `FilmAgent/Prompt/`, `COT_Prompt/` (director, screenwriter, actor, cinematographer, review-revise). MM_StoryAgent: `prompts_en.py`, `story_eval/eval_prompts.py`. Look-Before-Move: `Director/director_shot_contract.py`. Anim-Director: `AniMaker/Pipeline/utils/story2script.py` (generate → validator PASS/FAIL + corrected JSON). MovieAgent: `movie_agent/system_prompts.py`.

## Best per stage (agent's ranking)
- Story decomposition: ViMax event_extractor (every detail supported by input); ViMax novel_compressor; VideoClaw COT plan-first; MovieAgent screenwriter (paraphrase); CineCrew story_editor.
- Scene/beat: ViMax scene_extractor (one scene per call); ViMax script_planner; MovieAgent ScenePlanningCoT (paraphrase); VideoClaw director_2; CineCrew dialogue_extraction.
- Shot list/camera: ViMax storyboard_artist (first/motion/last frame, widest first); MovieAgent ShotPlot (paraphrase); Look-Before-Move shot contract (paraphrase); VideoClaw cinematographer (closed list); CineCrew cinematographer.
- Character/continuity: ViMax character_extractor + merge; CineCrew stable asset IDs; VideoClaw director_1 + actor; MM_StoryAgent extract + review.
- Critic: CineCrew anti_hallucination + consistency + meta_anchor (strongest "do not invent"); VideoClaw review/feedback checks; ViMax script_enhancer (preserve story and order); MovieAgent script supervisor (paraphrase).

## Recommended chain for the Granth (untested design)
0. Deterministic ingest (no LLM): {adhyay, ovi_no, text}; numbering checked.
1. Story decomposition per Adhyay: events[] {event_id, summary, ovi_range, key_ovi_ids}; every sentence backed by a cited ovi.
2. Character bible: characters[] {char_id, names_in_text, role, attributes (null when unknown), evidence_ovi}; aliases merged only with evidence.
3. Scene breakdown one per call: scenes[] {scene_id, ovi_range, location (only if stated), char_ids (from bible), beats[] {beat, ovi_ids}}.
4. Shot list: shots[] {shot_id, scene_id, ovi_ids, shot_size, camera_move (closed lists), action (paraphrase of cited ovis only), dialogue (verbatim or "silent")}.
5. Critic: (a) deterministic validator (ids exist, ranges contiguous, dialogue string-matches source); (b) LLM critic per scene with only the cited ovis: PASS/FAIL, unsupported_claims, fix; max two rounds, then human.
6. Assemble plan JSON with citations + coverage report of unused ovis.
Caveats: attribution for verbatim MIT/Apache text; rewrite paraphrase sources; keep verse text exact (no model translation of the source); validate on one Adhyay first.
