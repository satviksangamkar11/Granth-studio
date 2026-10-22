# Operator guide after the CPU corrections

## CPU checks

Use the existing environment; no model downloads are needed:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --junitxml=benchmarks/cpu_review_fixes.xml
.\.venv\Scripts\python.exe -m granthstudio validate
```

Contracts and approval evidence fields: `docs/IMPLEMENTATION_SPEC.md`.
The frozen architecture remains authoritative. Tests use synthetic content only.

## Research and language inputs

Research is a curated structured export of reviewed chapter material. Each scene needs
description, source_refs, location, characters, dialogue, actions, visual_details and
continuity. Fact records explicitly distinguish sourced facts from artistic choices.
Do not remove unresolved questions to make approval pass. No real research has been
approved by the code corrections.

After actual human review, the existing `research approve N --reviewer NAME --confirm`
records the source version. Manifests must cover every approved scene and line in order.
Hindi lines require text-bound semantic review evidence; translation is not generated.

For CPU media integration, timeline entries may reference reviewed per-line audio under
`artifacts/audio/`, with hash, language, speaker, text hash and speech reviewer. These are
measured/decoded and copied to task storage. Without them, TTS remains NOT VALIDATED.

Longer language speech requires explicit reviewed `hold_final_frame` coverage on the
shot. Assembly preserves primary actions and inserts silence/holds at the actual edit
positions. It refuses mismatched audio/video and never truncates speech via `-shortest`.

## Commands and outcomes

Existing commands: `version`, `config`, `validate`, `research status/approve`, `canon check`,
`episode compile`, `timeline check`, `plan`, `run`, `report`, `ffprobe`, `pilot plan/score`.
`plan` and `run` without `--execute` do not generate output.

Exit 0: command succeeded (a dry run or validation is not production approval).
Exit 1: malformed configuration/usage. Exit 2: failed/pending/gated release.
Exit 3: an integration/capability is NOT VALIDATED. A CPU run may be technically complete
while `released=false` because human production GO is absent.

## Recovery

Re-run the same command. Current inputs, dependency identities/output hashes, actual
media and output receipts are checked before reuse. Stale temporary work is discarded;
valid completed tasks are reused. Old receipt formats are intentionally invalidated.

ComfyUI intent/prompt IDs are saved outside temporary work in `tasks/.../pending/`.
After a polling timeout, resume polling that prompt rather than submit another job.
A journal with state `submitting` has an unknown POST result. Inspect the ComfyUI server
to establish whether it accepted the job; record the verified prompt ID with state
`submitted`, or record `failed` only after confirming no outstanding job remains.
Never delete an ambiguous journal just to retry. No real server recovery is validated yet.

## Production authorization

The runner never creates production approval. See `IMPLEMENTATION_SPEC.md` for the
existing-human-evidence contract under `approvals/adhyay_NN.json`. It binds the exact input
snapshot, accepted A-F receipts, pilot plan, explicit FLF GO/NO-GO, throughput budget and
reviewed interruption evidence. Missing/stale evidence leaves `released=false`.

## Remaining gates

LTX, ComfyUI graphs, IndicF5, IndicTrans2, SDXL, visual style, voice rights, semantic
accuracy, Kaggle runtime constraints and persistent external storage remain unvalidated
or absent. No model inference, research approval, GPU execution or production GO was
performed by the CPU correction work.


## D1-D7 evidence compatibility

After a definitive HTTP 4xx rejection, correct the graph/configuration before retrying;
the failed journal is retryable. A timeout/transport/server failure still requires
polling or explicit reconciliation and must not be treated as proof of rejection.

Rebuild pilot approvals after changes to the current compiled Adhyay 1 pilot. Recovery
proof must include actual clean/resumed output paths and hashes under artifact storage,
as documented in `IMPLEMENTATION_SPEC.md`. Old flag-only proof is intentionally invalid.
Point recovery records at the final assembly outputs inside two real scheduler stores:
one clean run and one interrupted-then-resumed run. Copied files are refused.
Do not create replacement approval records without the required human review.

Current correction verification: `benchmarks/claude_d_focused.xml`,
`benchmarks/claude_d_cpu.xml`, and `benchmarks/claude_d_receipt.json`.


## Kaggle and GPU entry points (nothing here has run on a GPU)

Before any GPU spend, in this order. Each step refuses with a precise reason until its inputs exist.

1. Decide and record in `config/`: `runtime.yaml` (resource minimums from a measured run, a durable
   storage provider (O-008), source repositories **and 40-character commits**, package pins, weight
   downloads with SHA-256), `models.yaml` (SDXL checkpoint and identity method (O-006), translation/speech/
   ASR/diagnostics runners (O-007), the LTX runtime inventory), `pilot.yaml` (review criteria (O-005) and
   the throughput budget (O-004)).
2. On the GPU host: `granthstudio runtime bootstrap --execute` (clones the pinned commits, installs pinned
   packages), `runtime fetch NAME` (add `--record` once to learn an unpinned file's hash, then pin it),
   `runtime verify`, `runtime preflight --gpu` (exit 0 only when every GPU check passes).
3. Set `GRANTHSTUDIO_SESSION_DEADLINE` (ISO 8601 with offset) so tasks stop launching near the end of the
   session; unstarted tasks are recorded as `deferred` and resume from receipts.
4. `granthstudio session N` restores the durable export, runs with GPU preflight, writes a run receipt, and
   always exports artifacts back (`--cpu-only` skips the GPU requirement). `runtime export|restore` do the
   same by hand.
5. A hung or unknown ComfyUI job: `comfy reconcile N SHOT` finds it by its job token in the server's queue
   or history. Only `--declare-lost` (after you confirmed on the server that it is gone) allows resubmission.
   `comfy cancel N SHOT` interrupts or dequeues the prompt. `comfy inspect` lists missing nodes and checks
   the pinned-checkpoint binding.

Dual-T4 is refused: `workers.dual_t4` must stay `disabled` until a benchmark justifies a design.

## Approval handoffs (every one needs a named human and `--confirm`)

- Research: `research import FILE.md --adhyay N --questions FINAL.md [--compare OTHER.md:M] [--write]`
  produces a draft that cannot load as research. Fill locations, cast, the exact Marathi dialogue and
  artistic flags; resolve every question; delete the `_import` block; `research check-draft N`;
  `research promote N`; then `research approve N`.
- Visual canon: write `style` and `designs` in `canon/visual_assets.yaml`; `refs import`/`refs generate`/
  `refs collect`; `refs approve ASSET --version V --reviewer R --confirm`. Keyframes follow the same path.
- Hindi: `translate candidates N --execute`, `translate review N`, `translate approve N --line ID`.
- Speech: record each voice's licence/consent in `canon/voices.yaml`; `speech generate`, `speech asr`,
  `speech approve` (after listening).
- Pilot: `pilot run N --execute`, `pilot receipts N`, `pilot review N --shot X --decision accept|reject
  --rating CRITERION=pass|fail|not_assessed`, `pilot receipts N` again, `pilot report N`. For recovery run the
  pilot twice into named stores (`--store clean`; `--store resumed`, interrupted once), then
  `pilot recovery-evidence N --clean clean --resumed resumed --reviewer R --confirm`.
- To validate an LTX capability: after accepted receipts exist, a human sets its `capabilities` entry to
  `validated` and the workflow `_status` to `validated`. The code never does this and never writes
  `approvals/adhyay_NN.json`.

The pilot report states measured, estimated, not_computed and unvalidated values. GPU seconds are
wall-clock estimates of every attempt (failed ones included). It gives no GO/NO-GO.
