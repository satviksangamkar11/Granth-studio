MINOR — [src/granthstudio/keyframes.py:350](</D:/aai work/granthstudio/src/granthstudio/keyframes.py:350>): rounding breaks exact `total/n`. For total `1.0`, three references receive `0.3333` each, totaling `0.9999`. Use direct division and cover three references in the test.

No blocking issue remains in this narrow code review of `f953ee8`. Numeric substitution, zero-reference checkpoint routing, request hashing, missing-total refusal, placeholder-free compatibility, live-probe rendering, and fp16 opt-in/validation/launch recording are intact. The VAE pin identifies the fp16-fix variant; no existing gate was weakened.

A pinned SDXL GPU run may be authorized. Tests and GPU behavior were not executed or verified in this read-only review; memory fit and visual quality remain unproven.