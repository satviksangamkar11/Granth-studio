# Operator guide

## Setup (Windows, PowerShell or Git Bash)

```bash
cd "D:/aai work/granthstudio"
uv sync                       # creates .venv and installs pyyaml and jsonschema (approved)
uv run granthstudio validate  # validates config, canon, research and manifests
uv run pytest -q              # 58 synthetic tests (about 5 s; needs ffmpeg on PATH for media tests)
```

Artifacts go to `D:\aai work\granthstudio-artifacts` (set in `config/project.yaml`, outside Git).

## Configuration examples

`config/project.yaml`

```yaml
schema_version: 1
artifacts_dir: "../granthstudio-artifacts"
research_dir: "research"
canon_dir: "canon"
episodes_dir: "episodes"
benchmarks_dir: "benchmarks"
timezone: "Asia/Calcutta"
```

`config/models.yaml` (excerpt). `checkpoint_sha256` stays `null` until the official file is hashed on the runtime. While it is `null`, every LTX capability is refused.

```yaml
comfyui:
  base_url: "http://127.0.0.1:8188"
ltx:
  checkpoint_file: ltxv-2b-0.9.8-distilled.safetensors
  checkpoint_sha256: null
  precision: fp16
  frame_counts: [49, 65, 81, 89, 97, 121]
  capabilities: {i2v: unvalidated, flf: unvalidated}
```

A capability may be set to `validated` only after a passing benchmark receipt exists for the same checkpoint hash (see `benchmarks/pilot_af/receipts/`).

`research/adhyay_NN/research.yaml` (structure only, not real content)

```yaml
schema_version: 1
adhyay: 1
scenes:
  - scene_id: a01_s01
    source_refs: ["<reviewed source reference>"]
    location: loc_<approved_location>
    characters: [chr_<approved_character>]
    dialogue:
      - {id: d_0001, speaker: chr_<approved_character>, text: "<approved Marathi line>"}
open_questions:
  - {id: A1-1, status: answered}   # every item must be 'answered' before approval
```

## Operating sequence for one adhyay

1. `uv run granthstudio research status N`
2. A human reviews `research/adhyay_NN/research.yaml`. Then `uv run granthstudio research approve N --reviewer "NAME" --confirm`.
3. `uv run granthstudio episode compile N`
4. `uv run granthstudio timeline check N`
5. `uv run granthstudio plan N` (inspect task IDs; nothing runs)
6. `uv run granthstudio run N --execute`. Exit code 3 means a stage is NOT VALIDATED and nothing was produced for it. Exit code 2 means a gate blocked release.
7. `uv run granthstudio report N` (QA report from receipts only)

## Recovery

- A crashed run leaves only `.work-*` folders, which are removed at the next run. Verified tasks are reused. Re-run `run N --execute` to resume.
- If a visual or research file changes after compilation, the task is refused with a clear message. Re-compile after re-approval.

## What is NOT validated on this machine

- LTX 0.9.8 2B I2V and FLF: no ComfyUI server, GPU or checkpoint has been run. Refused by the capability gate.
- SDXL keyframes, IndicF5 voice and IndicTrans2: adapters exist as explicit NOT VALIDATED stages. They refuse to run and never report success.
- Kaggle T4 execution and the A-F pilot: not run. Requires the user's GO and an upload approval.
