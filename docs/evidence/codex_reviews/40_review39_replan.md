**MAJOR remains; no BLOCKER found.**

- **MAJOR — `scripts/pilot/make_reference_spec.py:9`**: The shared style block omits the frozen `vintage double-line paper border mount` and negative-style constraints from `canon/style.yaml`. Every generated prompt inherits this reduced style despite the proposal promising unchanged frozen wording. Preserve the frozen constraints, or explicitly propose and obtain approval for the exception.

- **MINOR — `scripts/animation/motion.py:37` and `:40`**: Validation accepts booleans: `fps=True` reaches FFmpeg as `fps=True`, and `duration_s=True` becomes one second. Also, `duration_s=1e-9` passes validation but produces **zero frames** at line 60. Reject booleans and require at least one output frame. NaN and negative duration/zoom values are already rejected.

- **MINOR — `tests/test_motion_toolkit.py:96`**: The “cropped not stretched” test checks dimensions/count/rate only; replacing the crop with stretching would still pass. Compare rendered geometry against an independent crop reference. Endpoint geometry tests have real assertions, but smoothness checks exercise only the Python helper; repeated-render determinism is untested.

- **MINOR — `docs/ARCHITECTURE_V3_2_PROPOSAL.md:9`**: “Push-in the prompt cannot stop” exceeds the evidence. Review 39 explicitly limits that conclusion to the tested prompt. State the observed checkpoint/workflow/prompt result.

Otherwise, `on`, smoothstep, window clamping, upscale ordering and fixed-window `hold` look correct. Preview plans are valid and continuous; scene 1 excludes the visible signature corner. No shell/filter injection route found through validated spec strings. Image paths allow absolute paths and `..`; this CLI provides no path confinement.

All generated prompts include no-text/no-signature/no-watermark rules. Youth/modesty wording and Bankatlal’s correction are consistent; artistic choices remain labelled provisional. No further gate weakening found.

No files changed or rendering/tests run. NVIDIA/Gemini terms and pricing were not externally verified under your no-network restriction.