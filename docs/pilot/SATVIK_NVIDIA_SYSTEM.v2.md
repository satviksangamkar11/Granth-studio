# Satvik NVIDIA System (current, rewritten 2026-10-29 17:55)

Owner's NVIDIA-first build loop. Claude writes short spec files and runs/observes scripts; NVIDIA's free model writes ALL code and tests; a script loops until the tests pass; independent reviewers check the result. Claude writes no code. Folder: `D:\aai work\granthstudio`. Run Python as `uv run python ...` from that folder. The earlier version of this doc is kept as `SATVIK_NVIDIA_SYSTEM.previous.md`.

## 1. Hard rules (owner)
- NO Kimi, NO ElevenLabs, NO Opus. No paid action without the owner's go. Never print or read API keys.
- Coder = Nemotron 3 Ultra only. Nemotron is NEVER a reviewer.
- Claude writes no code (specs, job files, small ops scripts that only wire existing tools are the exception).
- Instagram links are only recorded (`animation_research_tool/instagram_links.txt`), never downloaded, until the owner says run.
- Do not edit this doc unless the owner asks (he asked on 2026-10-29).

## 2. Roles and models
| Role | Model | Settings |
|---|---|---|
| Coder (writes module + tests, fixes) | Nemotron 3 Ultra 550B `nvidia/nemotron-3-ultra-550b-a55b` | free NVIDIA endpoint, 14 keys, thinking on, effort medium |
| Reviewer 1 | Codex Luna `gpt-6-luna` (NOT `gpt-6.1-luna`, it fails auth) | effort medium, read-only, via `codex.cmd` |
| Reviewer 2 | GLM 5.3 Flash `z-ai/glm-5.3-flash` | NVIDIA, thinking OFF, 240 s deadline. Often slow or times out -> NO_REVIEW |
| Reviewer 3 | MiniMax M3.1 Flash `minimaxai/minimax-m3.1-flash` | NVIDIA, thinking OFF, 240 s deadline. Often returns nothing on big prompts -> NO_REVIEW |
| Reviewer 4 (stand-in for GLM/MiniMax, medium effort since 2026-10-29) | Haiku 5.5 medium (`claude -p --model haiku --effort medium` from scripts, or a Claude subagent, read-only) | called by `bulk_review.py` (CLI login was refreshed 2026-10-29 and works). Paid: use only as the owner allows |
| Escalation (3 failures) | Sonnet 5.5 medium (Claude subagent, read-only diagnosis) | diagnosis goes into the spec and the job reruns; if still failing the supervising Claude takes care of it |

## 3. The loop, step by step
1. **Spec** `docs/pilot/nemotron_specs/<name>.md`. It MUST end with the FORMAT block: reply with ONLY `FILE: <path>` blocks, each followed by a fenced ```python block. Without the fences the parser finds no files (this alone escalated 17 jobs once).
2. **Job file** `_loop/jobs/<name>.json`: `{"name","spec","files":[module,test],"tests":[test],"reference":[],"max_rounds":3,"review":false,"reviewers":[],"fixers":["nemotron","nemotron","nemotron"]}`. ALWAYS set `fixers` to Nemotron x3: the default third fixer is Codex, which returns empty replies and wasted rounds.
3. **Run:** `uv run python scripts/source/fix_loop_stable.py --job _loop/jobs/<name>.json` (see section 6 for why `_stable`). Result in `_loop/<job>/status.json`: `running | passed | passed-no-review | escalate | failed`. `passed-no-review` = tests passed, no reviewer ran yet.
4. **Tests/fix:** pytest runs; failures (real output) go back to Nemotron; up to 3 rounds. An empty reply (coder status 0) or a reply missing a required file still costs a round (a retry patch is planned, see section 8).
5. **Escalate:** after 3 failed rounds the job restores the original files and writes `ESCALATE.md`. -> Sonnet 5.5 medium diagnosis (short prioritised list, max 5 items, says which findings to drop) -> `apply_review.py` adds it to the spec and reruns once. Three escalations of the same piece = split the spec into smaller jobs (example: D4 -> wpD4a/b/c, one reply each).
6. **Review** (after tests are green): Luna + GLM + MiniMax via `luna_review.py`, plus Haiku-low when allowed. Findings are merged into the spec as REVIEW FINDINGS; Nemotron fixes them in one pass; the job reruns. An empty/timeout/error reply is NO_REVIEW (neither pass nor fail). DONE = tests green AND the latest reviews have no HIGH/MED.
7. **Supervise:** read only `status.json` and `ESCALATE.md`, never the full coder replies or code. Check every 5-10 minutes.

## 4. The automatic loops
**Current auto loop = the wave loop (`animation_research_tool/_loop/wave_loop.py`), running since 2026-10-29 19:23.** One command, no Claude tokens:
1. **Bulk review** (`bulk_review.py`): Codex Luna (`gpt-6-luna`, medium) 3 pieces per call + Haiku 5.5 medium (`claude -p --model haiku --effort medium`) 4 pieces per call, up to 8 calls in parallel. About 3 minutes for 6 pieces. Writes `_loop/reviews/combined_<id>.md` (headings `LUNA ...:` / `HAIKU ...:`; a file with only `## <id>` = no findings). Only pieces whose code changed after their last review, and whose fix job is not running, are reviewed.
2. **Apply** (`apply_review.py`): for every piece with HIGH/MED findings, appends them to its spec and relaunches its Nemotron fix job (through `fix_loop_stable.py`). All pieces in parallel.
3. **Wait** for the fix jobs, then repeat. A piece whose findings were applied 4 times without going clean is flagged (`_loop/reviews/NEEDS_CLAUDE_<id>.flag`) and skipped; then the supervising Claude takes over (Sonnet 5.5 medium diagnosis).
- Start: `C:\Python314\python.exe animation_research_tool/_loop/wave_loop.py` from the repo folder (system Python, because the repo venv has no `requests`). Log `_loop/wave_run.log`, state `_loop/wave_state.json`.
- Why waves: the first design (below) reviews ONE piece at a time (~5 min each, ~95 min per pass) and applies fixes only in the next cycle, so Nemotron sat idle. Waves review in bulk and fix in parallel.

**First auto loop (built by Nemotron, G1/G2/G3/G5/G6, 73 tests pass): `research/pieces/g1_autoloop.py` + `g2_autoloop_cli.py`.** Decision logic WAIT / RELAUNCH / ESCALATE / FIX_TESTS / REVIEW / APPLY / DONE, `--dry-run` per-piece view, `--state-file` for parallel loops. It works (verified by a dry run matching reality) but is STOPPED and replaced by the wave loop because it is sequential. Must be started with system Python, never `uv run` (the reviewer script needs `requests`). Move a stale `_loop/autoloop_state.json` aside before using it.

## 5. Files and tools
- Loop: `scripts/source/fix_loop.py` (shared tool; do not edit casually), `scripts/source/fix_loop_stable.py` (unpatched copy used for every relaunch), `scripts/source/coder_run.py`, `scripts/source/nemotron_code.py` (parser, forbids any file mentioning 3D animation software), `scripts/source/review_run.py`, `scripts/source/codex_review.py`.
- Research tool code: `research/pieces/<module>.py` + `test_<module>.py` (20 pieces A1..F4 plus G1/G2). Specs: `docs/pilot/nemotron_specs/research_<id>.md`. Jobs: `_loop/jobs/research_<id>.json`. Results: `_loop/research_<id>/`. Reviews: `_loop/reviews/` (`combined_<id>.md`, `haiku_*.md`, `sonnet_*.md`).
- Ops scripts (in `D:\aai work\animation_research_tool\_loop`): `check_all.py` (one-call table: job state + each piece's own pytest), `luna_review.py <ids>` (Luna medium + GLM + MiniMax, writes `combined_<id>.md`), `apply_review.py <report> <id>` (appends findings to the spec and relaunches the job with `fix_loop_stable.py`).
- Pause/resume record: `_loop/PAUSED.md`. Checklist: `animation_research_tool/CHECKLIST_MASTER.md` (snapshot between SNAPSHOT_START/END markers: code-verified results only; reviewer opinions listed separately).

## 6. Lessons that cost hours (do not repeat)
- A spec without the fenced FILE format line = no files parsed = escalation.
- Default `fixers` includes Codex = empty replies. Set Nemotron x3.
- Never test a change to the prompt or loop on all jobs at once: an f-string bug once sent literal `{spec}` placeholders to the coder and it overwrote working code in 17 pieces. Test on ONE piece first and keep a `_bak` copy.
- Codex from Python on Windows needs `codex.cmd` (`shutil.which`), plain `codex` raises WinError 2.
- Relaunch jobs through `fix_loop_stable.py`, so a half-patched `fix_loop.py` can never break jobs.
- Do not start a second job on the same files while one is running; one merged review pass per piece.
- Specs that ask for a full rewrite plus fixtures in one reply fail (54 KB reply). Split into stages that each pass before the next.
- Reviewers contradict specs sometimes: the spec's REVIEWER DECISIONS section is binding; the supervisor settles conflicts in writing.

## 7. Status words
`DONE` = code-verified (tests green and latest reviews clean). `BUILT` = exists, not final. `OPEN` = not done. Reviewer opinions never count as DONE.

## 8. Open items at time of writing (19:30)
- Wave loop running on 19 pieces (D4 excluded). Pieces clean by reviewer opinion at 19:29: A1, B2, C1, C3; 15 pieces had findings applied and their Nemotron fix jobs are running. Code-verified: 19 of 20 pieces pass their own tests (check with `check_all.py`).
- D4 split chain (wpD4a/b/c, `_loop/d4_chain.py`): stopped at wpD4b; resume after the 19 pieces are clean.
- `fix_loop.py` retry patch (job `fixloop_retry`): paused. The shared `scripts/source/fix_loop.py` and `tests/test_fix_loop.py` were restored to a 16:07 snapshot (5 of 61 tests failing, pre-existing; the other chat may have newer edits).
- G7a/G7b (loop patches) were stopped as unnecessary after the wave loop.
- Not done yet: integration/early smoke test, 1-2 reels (owner's go to download), Stage 1/2 compatibility check, one semantic audit of a reference video with audio (owner picks), final report. The real Kimi comparison needs the owner's approval.
- Tools: `bulk_review.py`, `wave_loop.py`, `apply_review.py`, `check_all.py` (all in `animation_research_tool/_loop`), plus `luna_review.py` (single-piece reviewer used by the first auto loop).
