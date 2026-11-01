# GranthStudio: the automated build loop (handoff for another chat session)

Folder (everything is here): `D:\aai work\granthstudio`. Python: run everything with `uv run python ...` from that folder. Written 2026-10-29. Readiness line: see the last section.

## What it does (the whole system in one picture)
You write a SPEC file (what a module must do) and a small JOB file. One command then runs the loop by API calls only, no Claude tokens:
1. **Coder:** Nemotron 3 Ultra 550B (`nvidia/nemotron-3-ultra-550b-a55b`), thinking ON, effort medium, free NVIDIA endpoint, 14 keys, keys read at run time and never printed. It writes the module AND its tests from the spec.
2. **Test:** the loop writes the files and runs pytest. On failures it sends the REAL pytest output back to the coder.
3. **Three fixing rounds.** If the tests still fail after 3 rounds the loop restores the original files, marks the job `escalate`, writes `_loop/<job>/ESCALATE.md` (last test output) and moves on. Only then does a Claude session need to look at it.
4. **Review layer** (after the tests pass): GLM 5.3 flash (thinking on, effort medium) and Codex (`gpt-6-luna`, effort high, read-only). A `FIX FIRST` report is sent to the coder as a new fixing round; `READY` from every reviewer that answered ends the job.
5. **No Kimi call anywhere. No Haiku agent. No flow-mcp.** Rules: Claude writes no code; Nemotron codes.

## Where the code is
| Piece | File | Tests |
|---|---|---|
| The loop (job runner, 3 rounds, escalate, reviewers) | `scripts/source/fix_loop.py` | `tests/test_fix_loop.py` |
| One-shot coder call (thinking on, 600 s idle timeout, receipts, continuation on length) | `scripts/source/coder_run.py` | `tests/test_coder_run.py`, `tests/test_coder_tools.py` |
| GLM reviewer tool (read-only, never sends secrets paths) | `scripts/source/review_run.py` | `tests/test_review_run.py` |
| Codex reviewer tool | `scripts/source/codex_review.py` | `tests/test_codex_review.py` |
| Key pool and streaming client (do not edit) | `scripts/source/draft_source.py`, `scripts/image_trials/nvidia_trial.py` | `tests/test_draft_source.py` |
| Specs for everything built so far | `docs/pilot/nemotron_specs/*.md` | |
| Review prompts | `docs/pilot/REVIEW_PROMPT_*.md` | |
| Loop work folder (status, rounds, escalations) | `_loop/<job name>/` | |
| Decisions, checklist, rules | `docs/pilot/DECISION_LOG.md`, `docs/pilot/CHECKLIST_BUILD_PIPELINE.md`, `docs/pilot/STAGE1_RULES.md`, `docs/pilot/PIPELINE_README.md` | |

## How to run a job (copy exactly)
1. Write the spec, e.g. `docs/pilot/nemotron_specs/my_thing.md` (what to build, the API, the tests wanted; end with: `Reply with only the FILE blocks: FILE: scripts/x.py  FILE: tests/test_x.py`). Never write words about 3D animation software in a spec (the repo filter refuses them).
2. Write the job file `_loop/jobs/my_thing.json`:
```
{"name": "my_thing",
 "spec": "docs/pilot/nemotron_specs/my_thing.md",
 "files": ["scripts/x.py", "tests/test_x.py"],
 "tests": ["tests/test_x.py"],
 "reference": [],
 "max_rounds": 3,
 "review": true, "review_rounds": 4,
 "reviewers": ["glm", "codex"]}
```
3. Run (from `D:\aai work\granthstudio`):
```
uv run python scripts/source/fix_loop.py --job _loop/jobs/my_thing.json
```
It prints one line per round and a final line `my_thing: passed | passed-no-review | escalate | failed`. Exit code 0 = passed, 3 = escalate, 1 = failed, 2 = bad job. Add `--dry-run` to only validate the job.
4. See the result: `_loop/my_thing/status.json` (state, rounds, tests, reviewer verdicts), `round_<n>.txt` (coder replies), `review_<k>.md` (reviewer reports), `ESCALATE.md` (only when it gave up).

## Check every 30 minutes without Claude tokens
Every job writes `_loop/<job name>/status.json` (state: running | passed | passed-no-review | escalate | failed). To check, open that file (or run `type _loop\<job>\status.json`). On Windows start a job in the background with PowerShell so it survives: `Start-Process uv -ArgumentList "run","python","scripts/source/fix_loop.py","--job","_loop/jobs/<job>.json" -RedirectStandardOutput _loop\<job>.log -WindowStyle Hidden`.
The queue runner `scripts/source/fix_loop_queue.py` (runs all pending jobs and writes `_loop/SUMMARY.md`) is written but NOT YET GREEN (8 of 23 tests fail): do not rely on it until the readiness section says so.

## Paste this into the other chat (so Claude only supervises)
```
Project folder: D:\aai work\granthstudio. Read docs/pilot/HANDOFF_LOOP_SYSTEM.md only. Rules: you write NO code; Nemotron writes all code and tests through the loop (scripts/source/fix_loop.py, thinking on). No Kimi calls, no Haiku agents. Use the minimum of tokens: do not read big files; do not poll more than once per 30 minutes. For each job: write the spec file and the job JSON exactly as the handoff says, run the one command, and read ONLY _loop/<job>/status.json. If a job says escalate, read _loop/<job>/ESCALATE.md and give me your opinion in 5 lines; do not fix it yourself. Report in 5 lines.
```

## Limits to remember
- A coder call takes 1 to 10 minutes; a GLM review 5 to 20 minutes; a Codex review a few minutes (Codex has a usage limit).
- The coder tool refuses any file that mentions 3D animation software (a safety rule of this repo).
- Every paid action (ElevenLabs credits, Kimi) needs the owner's go and is NOT part of this loop.

## Readiness (updated at the end of this file by the assistant)
2026-10-29 04:50 IST, verified with real runs:
- READY and proven end to end: `fix_loop.py` (46 of 46 tests pass). Proof job `loop_demo`: Nemotron wrote the module and tests, tests passed in round 0, GLM 5.3 flash review = READY, state `passed` (`_loop/loop_demo/status.json`).
- READY: `coder_run.py` (16 tests), `review_run.py` (40 tests, GLM live-verified), plus the pipeline units built in this batch (crosscheck 15, compare_a1 29, approve 36, check_script_cli 12, aggregate 49, context 26, runner 28).
- NOT YET GREEN: `codex_review.py` works (Codex command verified: model gpt-6-luna, effort high) but 1 of 21 tests fails (secrets-skipped test); `fix_loop_queue.py` 8 of 23 tests fail. Both are ordinary loop jobs: put them in `_loop/jobs/` as escalations if you want the loop to retry them.
- Known gap: a Codex reviewer is only used when a job lists `"reviewers": ["glm", "codex"]` and the Codex tool is green.

## Satvik NVIDIA System (current, updated 2026-10-29 15:45)
The owner's NVIDIA-first fix loop. Claude writes only short specs and runs scripts; NVIDIA's free model writes all code and tests; a script loops until the tests pass. Claude writes no code.

### Hard rules
No Kimi, no ElevenLabs, no Haiku, no Opus. No paid action without the owner's go. Never print or read API keys. Do not edit this doc unless the owner asks. Instagram links are only recorded, never downloaded, until the owner says run.

### Steps
1. **Spec:** one `.md` per piece in `docs/pilot/nemotron_specs/`. It must end with the FORMAT line: reply with only `FILE: <path>` blocks, each followed by a fenced ```python block. Without fences the parser finds no files.
2. **Job file:** `_loop/jobs/<name>.json` (spec path, module + test paths, `max_rounds` 3, `review` false).
3. **Coder:** Nemotron 3 Ultra 550B (`nvidia/nemotron-3-ultra-550b-a55b`), thinking on, effort medium, free NVIDIA endpoint, 14 keys. It is the only coder and never a reviewer.
4. **Test:** `fix_loop.py` runs pytest. On failure the real pytest output goes back to the coder, up to 3 fix rounds.
5. **Escalate:** after 3 failed rounds the job stops, restores the original files and writes `ESCALATE.md`. **Sonnet 5.5 medium** (Claude subagent, read-only) diagnoses it; the diagnosis goes into the spec and the job reruns, then the loop continues.
6. **Run:** `uv run python scripts/source/fix_loop.py --job _loop/jobs/<name>.json`. Result: `_loop/<job>/status.json` (running, passed-no-review, escalate, failed).

### Reviewers (after the tests pass; Nemotron is the coder ONLY, never a reviewer)
1. **Codex Luna:** `gpt-6-luna`, **medium** effort, read-only: `codex.cmd exec -m gpt-6-luna -c model_reasoning_effort=medium --sandbox read-only --skip-git-repo-check -` (prompt on stdin; use `codex.cmd` on Windows).
2. **GLM 5.3 Flash** (`z-ai/glm-5.3-flash`) and **MiniMax M3.1 Flash** (`minimaxai/minimax-m3.1-flash`) via NVIDIA, thinking OFF, 240 s deadline.
Their findings are merged into the spec as REVIEW FINDINGS, Ultra fixes them in one pass, the job reruns. An empty, timed-out or errored reply is NO_REVIEW (neither pass nor fail). Done = tests green and the reviewers report no HIGH/MED.
**Escalation:** if the same problem persists after 3 failed rounds, escalate to **Sonnet 5.5 medium** (Claude subagent, read-only diagnosis); its diagnosis goes into the spec and the loop continues. Sonnet is escalation-only, not a regular reviewer.

### Tools (in `D:\aai work\animation_research_tool\_loop`)
`check_all.py` (one-call status table), `luna_review.py <ids>` (Luna + GLM + MiniMax, writes `_loop/reviews/combined_<id>.md`), `apply_review.py <report> <id>` (adds findings to the spec and relaunches the job).

### Routine
Check every 15 minutes with the one-call table; read only status.json and ESCALATE.md, never full coder replies or code. Keep code-verified results and reviewer opinions separate in the checklist.
