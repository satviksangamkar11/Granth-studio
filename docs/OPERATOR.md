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
