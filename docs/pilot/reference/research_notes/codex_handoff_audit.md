HANDOFF NEEDS FIXES

**MAJOR — Paid-call prerequisites are ordered inconsistently.** [HANDOFF.md:27](D:/aai%20work/granthstudio/docs/pilot/HANDOFF.md:27) schedules a paid Kimi probe in Phase 0, before the provider adapter and tested `$3` ledger cap in Phase 1 ([line 38](D:/aai%20work/granthstudio/docs/pilot/HANDOFF.md:38)). The approved external plan explicitly requires those safeguards **before any paid call**; `scripts/image_trials/v5_ledger.py:19` currently defines only P1/P2/P3. **Correction:** explicitly defer the probe until the adapter, cap, tests and reconciliation are complete.

**MAJOR — Essential references are machine-local and outside the repo.** `HANDOFF.md:24,29,42,45,47` relies on the approved plan, research prompts, reviews, PDF and financial ledger outside `granthstudio`. Packet copies preserve the immediate director inputs, but do not preserve these other dependencies. **Correction:** identify exact authoritative locations and a preservation/recovery procedure; preserve the approved plan and required research/licence evidence in the repo. Keep secrets external.

**MAJOR — Phase 1’s acceptance gate does not cover its full scope.** `HANDOFF.md:38` requires contract mapping, approval invalidation, immutable runs/resume and a provider adapter/cap. Its acceptance criteria at `:39` cover seven seeded validator failures, with no explicit verification of those additional requirements. A session could declare Phase 1 complete while they remain broken. **Correction:** add acceptance evidence for each of items h–k.

**MAJOR — The prompt instructions contradict their own proposed test.** `HANDOFF.md:29` bans `"invent"` while explicitly requiring the lifted rule `"do not add, assume or invent"`. A literal banned-phrase test rejects the required protective instruction. **Correction:** distinguish permission to invent from prohibitions against invention, with positive and negative examples.

**MAJOR — The Adhyay 2 command is incomplete and misdescribed.** `HANDOFF.md:27` gives `fetch_hj.py --from-raw`; `scripts/source/fetch_hj.py:45,54` requires chapter numbers and reads an existing raw file—it does not fetch through the browser. **Correction:** give the page URL, save location `canon/source_hj/adhyay_02_raw.txt`, then `uv run python scripts/source/fetch_hj.py --from-raw 2`.

**MINOR — Status needs an explicit scope and precedence rule.** `HANDOFF.md:15,61` says “anything rendered” is unfinished and “nothing is committed.” Earlier project work is committed, and `docs/DECISIONS.md:69` records three rendered shots; `docs/PROGRESS.md:479` records a silent preview. PROGRESS ends at the October 24 freeze, whereas the handoff describes October 26. **Correction:** say “new Adhyay 1+2 production work,” identify the current Git checkpoint, and explain that PROGRESS is stale for this work.

**MINOR — “One repair” understates current execution.** `HANDOFF.md:14` describes one repair, but `scripts/source/director_test.py:273` allows a validator repair and `:300` allows an additional reviewer-driven repair. **Correction:** distinguish the two rounds from the future bake-off’s single targeted repair budget.

**MINOR — Several shorthand filenames are ambiguous.** `HANDOFF.md:21,24,38,42,46` omits directories for scripts and original analyses. In particular, `motion.py` has two legitimate implementations/entry points. **Correction:** use full repo-relative paths and map frozen inputs to exact originals.

Path audit below. Repo-relative paths use `D:\aai work\granthstudio`. Grouped rows explicitly enumerate related references.

| Path | Exists | Correct location | Note |
|---|---|---|---|
| `docs/pilot/HANDOFF.md` | Yes | Yes | Current review target; another same-named file exists under `D:\kaggle_upload\dbc`. |
| `docs/pilot/NEXT_STEPS_PLAN.md` | Yes | Yes | Contains historical unchecked instructions; latest log must take precedence. |
| `CLAUDE.md` | Yes | Yes | Archived copies elsewhere; see below. |
| `docs/ARCHITECTURE_V3_1.md` | Yes | Yes | Archived copies elsewhere. |
| `docs/DECISIONS.md` | Yes | Yes | A2 present; locally modified. |
| `docs/PROGRESS.md` | Yes | Yes | Stale relative to current work. |
| `docs/pilot/DIRECTOR_PROMPT_CHAIN.md` | Yes | Yes | Present, untracked. |
| `scripts/source/director_test.py` | Yes | Yes | Present, untracked. |
| `tests/test_director_test.py` | Yes | Yes | 12 test functions; appropriate central tests directory. |
| `scripts/source/draft_source.py` | Yes | Yes | Present, untracked. |
| `tests/test_draft_source.py` | Yes | Yes | 15 test functions. |
| `scripts/source/fetch_hj.py` | Yes | Yes | Locally modified; incomplete command in handoff. |
| `seeded_check_test.py` | Yes | Ambiguous shorthand | Actual path: `scripts/source/seeded_check_test.py`. |
| `scripts/image_trials/nvidia_trial.py` | Yes | Yes | KeyPool settings support stated 10/minute and 60-second cooldown. |
| `scripts/image_trials/v5_inbox_check.py` | Yes | Yes | Named location correct. |
| `v5_prep.py` | Yes | Ambiguous shorthand | Actual path: `scripts/image_trials/v5_prep.py`. |
| `v5_watermark.py` | Yes | Ambiguous shorthand | Actual path: `scripts/image_trials/v5_watermark.py`. |
| `v5_blender.py` | Yes | Ambiguous shorthand | Actual path: `scripts/image_trials/v5_blender.py`. |
| `scripts/image_trials/v5_ledger.py` | Yes | Yes | P4 cap absent, as acknowledged. |
| `motion.py` | Yes | Ambiguous shorthand | CLI: `scripts/animation/motion.py`; implementation: `src/granthstudio/motion.py`. Intentional wrapper, not stray duplication. |
| `parallax.py` | Yes | Ambiguous shorthand | Actual path: `scripts/animation/parallax.py`. |
| `tests/test_hybrid_rig.py` | Yes | Yes | Present, untracked. |
| `tests/test_tpu_bench.py` | Yes | Yes | Present. |
| `assets/v5_presets/` | Yes | Yes | 11 numbered presets, plus index and README. |
| `canon/packets/adhyay_01/` | Yes | Yes | All manifest file hashes match. |
| `canon/packets/adhyay_02/` | Yes | Yes | All manifest file hashes match; Marathi ovis absent as disclosed. |
| `adhyay_01_ovis_hj.jsonl` | Yes | Yes, packet context | Under `canon/packets/adhyay_01/`. |
| `presets_index.json` | Yes | Yes, packet context | Under `canon/packets/adhyay_01/`. |
| Packet `MANIFEST.json` files | Yes | Yes | Both present and verified. |
| `canon/source_hj/adhyay_01.jsonl` | Yes | Yes | Working source copy; packet copy is intentional. |
| `canon/director_test/` | Yes | Yes | Mutable current output directory. |
| `canon/director_test/REVIEW.md` | Yes | Yes | Present. |
| `canon/director_test/a01_scene{N}.json` | Yes | Yes | Concrete files for scenes 1, 4 and 6. |
| `canon/director_test/receipt.json` | Yes | Yes | Present. |
| `canon/director_test/*` | Yes | Yes | Overwrite warning matches code. |
| `canon/director_runs/` | Yes | Yes | Preserved-run parent. |
| `canon/director_runs/run2_2026-10-26/` | Yes | Yes | All five recorded output hashes match; 15 shots and 21 image entries confirmed. |
| `canon/director_runs/<name>/` | Template | Yes | Future run name, not a literal missing directory. |
| `canon/drafts/a01_*` | Yes | Yes | Meanings, partials, characters, review and receipt present. |
| `prompts/director/` | **MISSING** | Planned | Explicit Phase 2 deliverable, not completed work. |
| `prompts/director/scene_director_v2.md` | **MISSING** | Planned | Future deliverable. |
| `prompts/director/macro_planner_s1s2.md` | **MISSING** | Planned | Future deliverable. |
| `prompts/director/reviewer_rubric_v2.json` | **MISSING** | Planned | Future deliverable. |
| `prompts/director/repair_prompt.md` | **MISSING** | Planned | Future deliverable. |
| `prompts/director/narration_writer.md` | **MISSING** | Planned | Future deliverable. |
| `prompts/director/sound_cue_rules.md` | **MISSING** | Planned | Future deliverable. |
| `prompts/director/sound_palette.json` | **MISSING** | Planned | Future deliverable. |
| `prompts/director/RESEARCH_MAP.md` | **MISSING** | Planned | Future deliverable. |
| Future prompt-hash `receipt.json` | Not implemented | Unspecified | State exact destination/run ownership. |
| `D:\aai work\secrets\nvidia` | Yes | External, appropriate | Existence only; contents never listed or read. |
| `D:\aai work\secrets\kimi` | Yes | External, appropriate | Existence only; contents never listed or read. |
| `D:\aai work\v5_inbox` | Yes | External, intentional | Owner asset intake needs preservation policy. |
| `D:\aai work\frozen_*` | Yes | External archive | Multiple frozen generations exist; wildcard does not identify authoritative originals. |
| `adhyay_NN_analysis.md` | Yes, concrete versions | Ambiguous shorthand | Examples: `D:\aai work\adhyay_01\adhyay_01_analysis.md`, `...\adhyay_02\adhyay_02_analysis.md`; packet uses versioned `_analysis_v3.md` copies. |
| `D:\aai work\e-shree-gajanan-vijay-granth.pdf` | Yes | External dependency | Authority PDF is outside repo. |
| `C:\Users\Satvik\.claude\plans\elegant-doodling-dream.md` | Yes | External dependency | Approved plan outside repo. |
| `D:\kaggle_upload\v5_ledger.jsonl` | Yes | External mutable state | One open `$0.327824`; settled `$0.857142` matches handoff. Preserve financial history. |
| `D:\kaggle_upload\repo_research\` | Yes | External dependency | Required research/review archive. |
| `...\repo_research\director_prompts\` | Yes | External dependency | Required prompt/licence sources. |
| `story_prompts\` | Yes | Ambiguous shorthand | Actual location: `D:\kaggle_upload\repo_research\story_prompts\`. |
| `...\repo_research\codex_*.md` | Yes | External dependency | Multiple review generations; identify controlling verdicts. |
| `...\repo_research\codex_arch_fast_close.md` | Yes | External dependency | Present. |
| `...\repo_research\codex_best_director.md` | Yes | External dependency | Present. |
| `...\repo_research\codex_audio_design.md` | Yes | External dependency | Present. |
| `...\repo_research\codex_models.md` | Yes | External dependency | Present. |
| `...\repo_research\outside_*.md` | Yes | External dependency | `outside_models.md`, `outside_suggestion.md`. |
| `C:\LAYA_BACKUP_2026-10-18` | Yes | Unrelated housekeeping | Existence only checked; deletion unnecessary for Phase 1 review. |
| `D:\local model` | Yes | Separate project | Existence only checked. |
| `prompt.txt`, `<file>`, `FILE` | Placeholders | Unspecified | Example command arguments, not existing deliverables. |

Duplicate/location observations:

- Archived copies of `CLAUDE.md`, architecture, decisions and progress exist under `D:\kaggle_upload\out_{A1,A2,A3,L1…}`-style output trees. Specifically found: `out_sweep`, `out_sdxl_s2`, `out_sdxl_s3`, `out_sdxl2`, `out_ref1–3`, `out_gpu0_try1`, `out_audio1–3`, `out_ab`, `out_A1–A3`, `out2`, `out2b`, `out3`, `out4`; some also contain `harness_repo`. Three `.claude/worktrees/agent-*` trees also contain older authority files. Label these as historical snapshots.
- `D:\kaggle_upload\dbc\HANDOFF.md` is another same-named handoff; content equivalence was not established.
- No misplaced copies of the named director/source scripts or their tests were found in accessible scanned folders.
- Stray project research outside the repo includes `D:\aai work\adhyay_*`, `frozen_*`, final-answer files, `glossary_user_supplied.md`, research reports and `pilot_refs`. Packet manifests verify the copied inputs, but the handoff should distinguish preserved copies from external-only material.

No files changed. Tests and live API calls were not run; test counts were checked statically. Duplicate coverage excludes inaccessible `D:\kaggle_upload\pt_{v5,tpu,h,g}` folders, dependency/cache trees and links. Secrets, token contents and Downloads were not accessed.