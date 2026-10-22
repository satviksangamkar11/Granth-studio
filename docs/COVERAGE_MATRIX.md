# Architecture coverage matrix (frozen v3.1, 2026-10-22)

Legend: IMPLEMENTED = code plus tests that ran here. ADAPTER = code path present; the external component is NOT VALIDATED and refuses to run. SPEC = specification only. GATED = blocked by a user decision or by research approval.

| Frozen section | Requirement | Where | Status | Evidence |
|---|---|---|---|---|
| 1 | Objective, one episode per adhyay | `episodes/`, `pipeline.py` | IMPLEMENTED | `test_pipeline.py` |
| 2A | Sacred source integrity; no silent invention | `research.py`, `timelines.py` (Marathi lock, approved-only references) | IMPLEMENTED | `test_timelines_and_scheduler.py`, `test_governance.py` |
| 2B | Global canon with stable IDs | `canon.py` | IMPLEMENTED | `test_governance.py` |
| 2C | One visual production, two releases | `episodes.py` (shared visuals), `pipeline.py` (shared clips, two assembly tasks) | IMPLEMENTED | `test_pipeline.py` |
| 2D | Filesystem manifests, no database | all modules; no database library installed | IMPLEMENTED | dependency list: pyyaml, jsonschema |
| 2E | Measured performance | `pilot.py` (D-004 throughput), benchmark receipts | IMPLEMENTED (scoring); measurement GATED | `test_media_comfy_pilot.py` |
| 3 | Stages Input, 00-05 | `pipeline.py`, `scheduler.py` | IMPLEMENTED for compile, scheduler and assembly; audio and keyframes ADAPTER | `test_pipeline.py` |
| 4.1 | Research ingestion, SHA-256 receipt, versions | `research.py` | IMPLEMENTED | `test_governance.py` |
| 4.2 | Global character registry, no automatic merge | `canon.py` | IMPLEMENTED | `test_governance.py` |
| 4.3 | Global visual style, one version | not implemented (style checkpoint OPEN, O-006) | GATED | n/a |
| 4.4 | Canonical reference sheets | not implemented (SDXL OPEN, O-006) | GATED | n/a |
| 5.1 | Marathi dialogue lock | `timelines.py` | IMPLEMENTED | `test_timelines_and_scheduler.py` |
| 5.2 | Hindi adaptation, protected terms, numeric facts, blocks | `timelines.py` (IndicTrans2 itself not integrated) | IMPLEMENTED checks; translation ADAPTER-less (O-007) | `test_timelines_and_scheduler.py` |
| 5.3 | IndicF5 voice | `pipeline.py` audio stage | ADAPTER (NOT VALIDATED) | `test_pipeline.py` |
| 5.4 | Audio timing from measured duration; SRT | `timelines.srt_text` | IMPLEMENTED (needs measured durations) | `test_timelines_and_scheduler.py` |
| 6 | Keyframe batch with conditioning | `pipeline.py` keyframe stage | ADAPTER (NOT VALIDATED) | `test_pipeline.py` |
| 7 Tier 0 | FFmpeg pan/zoom animated stills | `ffmpeg.still_motion_clip` | IMPLEMENTED | `test_media_comfy_pilot.py`, `test_pipeline.py` |
| 7 Tier 1 | LTX 0.9.8 2B I2V | `comfy.py`, `config.require_capability` | ADAPTER (NOT VALIDATED: no checkpoint hash, no passing receipt) | `test_media_comfy_pilot.py` |
| 7 Tier 2 | LTX FLF, gated | `pipeline._ltx_run(flf)` | ADAPTER, disabled by gate | `test_media_comfy_pilot.py` |
| 7 frames | Frame rule | pinned `frame_counts`; formula OPEN (O-003) | GATED | `test_governance.py` |
| 8 | Stage batch order, two workers | stage order enforced in `plan_tasks`; sequential execution only (worker concurrency is benchmark-dependent) | IMPLEMENTED (sequential) | `test_pipeline.py` |
| 9 | Hard rules, bounded retries, receipts, atomic outputs, restart | `scheduler.py`, `qa.py` | IMPLEMENTED | `test_timelines_and_scheduler.py` |
| 9 | Diagnostics logged, not enforced | `qa.write_report` | IMPLEMENTED (no metric computed: status not_computed) | `test_pipeline.py` |
| 10 | Bilingual assembly, separate timelines, four outputs | `pipeline._assembly_run`, `ffmpeg.assemble` | IMPLEMENTED (needs audio) | `test_media_comfy_pilot.py` |
| 11 | Repository structure | SPEC | SPEC (`docs/SPEC_SECTIONS_11_12_14.md`) | n/a |
| 12 | Episode manifest contract | `episodes.py`, schemas | SPEC + IMPLEMENTED | `test_governance.py` |
| 13 | Technology stack | `pyproject.toml`; models pinned in `config/models.yaml` | IMPLEMENTED partly (external tools ADAPTER) | n/a |
| 14 | CLI interface | `cli.py` | SPEC + IMPLEMENTED | `test_foundations.py`, `test_pipeline.py` |
| 15 | Six-shot A-F pilot | `pilot.py` | IMPLEMENTED mapping and scoring; EXECUTION GATED (needs Kaggle T4 and user GO) | `test_media_comfy_pilot.py` |
| 16 | Release and change control | pins: research version, canon digest, workflow version | IMPLEMENTED | `test_governance.py` |
| 17 | Freeze matrix | `docs/` | RECORDED | n/a |
| 18 | Next milestone | pilot on Kaggle | GATED | n/a |

## Missing or incomplete components (explicit)

1. No research is approved. 104 open and 75 provisional items block approval, as the user required. No episode can compile for production until they are resolved.
2. No LTX checkpoint has been downloaded, hashed or run. `checkpoint_sha256` is null. Capability gates refuse.
3. No validated ComfyUI graph exists. `workflows/comfyui/*.json` are stubs marked unvalidated.
4. IndicTrans2 and IndicF5 are not integrated. Their stages refuse to run.
5. SDXL keyframes, the style checkpoint and reference sheets are not integrated.
6. No quality metrics are computed. Diagnostics are recorded as not_computed.
7. Worker concurrency: execution is sequential. Concurrency is benchmark-dependent (frozen section 8).
8. Persistent storage outside Kaggle (O-008) is not configured.
9. Codex review: see `docs/PROGRESS.md` for the installation status.
