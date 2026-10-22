# Implementation specification for frozen sections 11, 12 and 14

Status: IMPLEMENTED as specified here (2026-10-22). The frozen document `docs/ARCHITECTURE_V3_1.md` is NOT modified. These sections are implementation specifications under the user's authority (decision D-005). They do not change any frozen rule.

## Section 11: repository structure (proposal P-001, approved)

```
granthstudio/                 Git repository (code, configuration, canon, research, manifests, docs)
  CLAUDE.md  AGENTS.md  .gitignore  pyproject.toml  .gitattributes
  config/      project.yaml  models.yaml  quality_gates.yaml
  canon/       characters.yaml  locations.yaml  terminology.yaml
  research/    adhyay_NN/research.yaml  adhyay_NN/source_receipt.json
  episodes/    adhyay_NN/manifest.yaml  mr.yaml  hi.yaml  compiled.json
  workflows/comfyui/   ltx_i2v_098.json  ltx_flf_098.json   (templates; NOT VALIDATED until exported)
  benchmarks/pilot_af/receipts/   benchmark receipts (small JSON, committed)
  src/granthstudio/   code      schemas/ (JSON Schema, packaged)      tests/
  docs/        architecture, plans, decisions, progress, this specification
  scripts/     reserved (no scripts yet)
../granthstudio-artifacts/     OUTSIDE Git: visuals/, tasks/, reports/, media, temporary renders
```

Rule: large media, checkpoints and temporary renders never enter Git. Hashes and receipts do.

## Section 12: episode manifest contract

Files per adhyay under `episodes/adhyay_NN/`:

- `manifest.yaml` (schema `episode_manifest`): `episode_id` (ep01..), `adhyay`, `research_version` (must equal the approved receipt version), `visuals` (shared visual masters, one entry per `visual_id` with `source` file|keyframe, `path` under the artifacts `visuals/` folder, `sha256`), and `scenes`. Each scene has `scene_id` = `research_scene` (a01_sNN), `location`, `characters` (canon ids), optional `props`, `lighting`, `artistic_flags`, and `shots`.
- Shot fields: `shot_id` (a01_sNN_shMM), `tier` (0 still, 1 LTX I2V, 2 LTX FLF), `visual_id`, `end_visual_id` (tier 2 only), `duration_s`, `frames` (tier 1 and 2; must be in the pinned `frame_counts`), `motion_prompt` (motion only, no new story elements), `dialogue_ids`, and an optional `pilot_shot` label A-F.
- `mr.yaml` and `hi.yaml` (schema `timeline`): one entry per dialogue line with `dialogue_id`, `shot_id`, `speaker`, `text`. Hindi entries also carry `alignment` (`mr_dialogue_id`, `match` exact|adapted, `reviewed`). `measured_duration_s` is filled by the audio stage.

Compilation (`granthstudio episode compile N`) checks every reference, pins the research version, the manifest hash and the canon digest, and writes `compiled.json`. The output is deterministic: the same inputs give the same bytes.

Dependency invalidation (frozen section 16) follows from the pins. A research edit changes `research_sha256` and blocks until re-approval. A canon edit changes the canon digest. A workflow edit changes the task's `workflow_version`, so the scheduler reruns only that task.

## Section 14: CLI interface

`granthstudio [--root DIR] [-v] <command>`. Exit codes: 0 ok; 1 configuration or usage error; 2 refused or gate failed; 3 NOT VALIDATED (nothing was produced).

| Command | Purpose |
|---|---|
| `version` | print version |
| `config` | show resolved paths, LTX capability status and checkpoint pin state |
| `validate` | validate config, models, quality gates, canon, research and manifests |
| `research status N` | approval state and whether the source changed |
| `research approve N --reviewer NAME --confirm` | record an approval version (refused while any item is open or provisional) |
| `canon check` | validate canon, identity decisions and aliases |
| `episode compile N` | compile the manifest into `compiled.json` |
| `timeline check N` | Marathi lock, Hindi alignment, protected terms, numeric facts |
| `plan N` | list the frozen stage plan with deterministic task IDs (no execution) |
| `run N [--execute]` | run the stage plan; without `--execute` it is a dry run |
| `report N` | write the QA report from existing receipts only |
| `ffprobe FILE` | probe a media file |
| `pilot plan N` | map shots A-F and print the recovery check |
| `pilot score DIR` | accepted seconds per GPU-hour from benchmark receipts (decision D-004) |

## Throughput formula (decision D-004)

accepted sec per GPU-hour = (sum of video seconds where accepted = true) / (sum of gpu_seconds_total over all receipts / 3600). Failed renders, retries and rework count in gpu_seconds_total. A receipt with `accepted: null` blocks scoring.

## Open items that remain

- Frame-count rule (O-003): the pinned list is used; the exact rule is not confirmed.
- Numerical acceptance threshold (O-004): not set. No threshold is enforced.
- Manifest fields for lip-sync and language-specific visual variants are not yet specified (not needed for the A-F pilot).
