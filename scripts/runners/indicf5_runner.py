"""UNVALIDATED reference runner for IndicF5 (O-007). Never executed on this project.

Written from the model's published usage and NOT checked against a pinned release. Choose and
pin the model revision, confirm the reference-voice licence/consent record in canon/voices.yaml,
run it once on the GPU host, listen to the result, and only then set models.yaml speech.status
to validated. Dependencies (transformers, soundfile, numpy) are installed on the GPU host only.

Contract (see src/granthstudio/runners.py):
  stdin  {"text", "language", "reference_audio", "reference_transcript", "out_path", ...}
  stdout {"sample_rate": int}      (the audio itself is written to out_path)
The payload carries the approved "model" and "revision" (config/models.yaml speech). The model is loaded at
exactly that revision and the loaded checkpoint must prove it (config._commit_hash), otherwise the runner exits
non-zero. INDICF5_REPO, if set, may only restate the approved model; it cannot substitute other weights.
stdout also carries {"verified": {"model", "revision"}}, recorded in the candidate record.
"""
import json
import sys

from _identity import IdentityError, approved_identity, verified_identity


def main() -> None:
    payload = json.load(sys.stdin)
    import numpy as np
    import soundfile
    from transformers import AutoModel

    name, revision = approved_identity(payload, "INDICF5_REPO")
    model = AutoModel.from_pretrained(name, revision=revision, trust_remote_code=True)
    verified = verified_identity(name, revision, getattr(getattr(model, "config", None), "_commit_hash", None))
    audio = model(payload["text"], ref_audio_path=payload["reference_audio"], ref_text=payload["reference_transcript"])
    audio = np.array(audio, dtype=np.float32)
    soundfile.write(payload["out_path"], audio, samplerate=24000, format="WAV")
    print(json.dumps({"sample_rate": 24000, "verified": verified}))


if __name__ == "__main__":
    try:
        main()
    except IdentityError as exc:
        print(f"model identity check failed: {exc}", file=sys.stderr)
        sys.exit(2)
