"""UNVALIDATED reference runner for IndicF5 (O-007). Never executed on this project.

Written from the model's published usage and NOT checked against a pinned release. Choose and
pin the model revision, confirm the reference-voice licence/consent record in canon/voices.yaml,
run it once on the GPU host, listen to the result, and only then set models.yaml speech.status
to validated. Dependencies (transformers, soundfile, numpy) are installed on the GPU host only.

Contract (see src/granthstudio/runners.py):
  stdin  {"text", "language", "reference_audio", "reference_transcript", "out_path", ...}
  stdout {"sample_rate": int}      (the audio itself is written to out_path)
Environment: INDICF5_REPO = hub id or local directory of the pinned model.
"""
import json
import os
import sys


def main() -> None:
    payload = json.load(sys.stdin)
    import numpy as np
    import soundfile
    from transformers import AutoModel

    model = AutoModel.from_pretrained(os.environ["INDICF5_REPO"], trust_remote_code=True)
    audio = model(payload["text"], ref_audio_path=payload["reference_audio"], ref_text=payload["reference_transcript"])
    audio = np.array(audio, dtype=np.float32)
    soundfile.write(payload["out_path"], audio, samplerate=24000, format="WAV")
    print(json.dumps({"sample_rate": 24000}))


if __name__ == "__main__":
    main()
