"""M10: reference runners bind the executed checkpoint to the approved revision. Fake model libraries only;
no real model is loaded and nothing here validates IndicF5 or IndicTrans2."""
from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

from tests.conftest import REPO

RUNNERS = REPO / "scripts" / "runners"
REV = "a" * 40

FAKES = {
    "numpy.py": "float32 = 'f4'\ndef array(x, dtype=None): return list(x)\n",
    "soundfile.py": "import pathlib\ndef write(path, audio, samplerate, format): pathlib.Path(path).write_bytes(b'RIFFfake')\n",
    "transformers.py": '''
import os
class _Config:
    def __init__(self):
        if os.environ.get("FAKE_COMMIT"): self._commit_hash = os.environ["FAKE_COMMIT"]
class _Model:
    config = _Config()
    def __call__(self, *a, **k): return [0.0, 0.1]
    def to(self, device): return self
    def generate(self, **k): return _T()
class _T:
    def detach(self): return self
    def cpu(self): return self
    def tolist(self): return [[1]]
class AutoModel:
    @staticmethod
    def from_pretrained(name, revision=None, trust_remote_code=False):
        print(f"{name}@{revision}", file=open(os.environ["FAKE_LOG"], "a")); return _Model()
AutoModelForSeq2SeqLM = AutoModel
class _Tok:
    def __call__(self, *a, **k): return _Enc()
    def batch_decode(self, *a, **k): return ["namaste"]
class _Enc(dict):
    def to(self, device): return self
class AutoTokenizer:
    @staticmethod
    def from_pretrained(name, revision=None, trust_remote_code=False): return _Tok()
''',
    "torch.py": "class cuda:\n    @staticmethod\n    def is_available(): return False\nclass no_grad:\n    def __enter__(self): pass\n    def __exit__(self, *a): pass\n",
    "IndicTransToolkit/__init__.py": "",
    "IndicTransToolkit/processor.py": "class IndicProcessor:\n    def __init__(self, inference=True): pass\n    def preprocess_batch(self, t, src_lang, tgt_lang): return t\n    def postprocess_batch(self, d, lang): return d\n",
}


@pytest.fixture
def fakes(tmp_path):
    for name, text in FAKES.items():
        path = tmp_path / "fake" / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text, encoding="utf-8")
    return tmp_path


def run(fakes, script, payload, commit=REV, **env):
    environ = {**os.environ, "PYTHONPATH": str(fakes / "fake"), "FAKE_LOG": str(fakes / "load.log"), **env}
    environ.pop("FAKE_COMMIT", None)
    if commit is not None:
        environ["FAKE_COMMIT"] = commit
    return subprocess.run([sys.executable, str(RUNNERS / script)], input=json.dumps(payload), capture_output=True,
                          text=True, env=environ, timeout=60)


F5 = ("indicf5_runner.py", {"text": "t", "reference_transcript": "r", "model": "ai4bharat/IndicF5", "revision": REV, "language": "mr"},
      "INDICF5_REPO")
T2 = ("indictrans2_runner.py", {"src_lang": "mar_Deva", "tgt_lang": "hin_Deva", "texts": ["x"], "model": "ai4bharat/it2", "revision": REV},
      "INDICTRANS2_CHECKPOINT")


def payload_for(case, fakes):
    script, payload, env = case
    return script, {**payload, "reference_audio": str(fakes / "ref.wav"), "out_path": str(fakes / "out.wav")}, env


@pytest.mark.parametrize("case", [F5, T2], ids=["indicf5", "indictrans2"])
def test_correct_revision_runs_and_records_verified_identity(fakes, case):
    script, payload, _ = payload_for(case, fakes)
    done = run(fakes, script, payload)
    assert done.returncode == 0, done.stderr
    assert json.loads(done.stdout)["verified"] == {"model": payload["model"], "revision": REV}
    assert (fakes / "load.log").read_text().split()[0] == f"{payload['model']}@{REV}"  # loaded at the approved revision


@pytest.mark.parametrize("case", [F5, T2], ids=["indicf5", "indictrans2"])
def test_mismatched_or_missing_revision_evidence_fails_closed(fakes, case):
    script, payload, _ = payload_for(case, fakes)
    wrong = run(fakes, script, payload, commit="b" * 40)
    assert wrong.returncode == 2 and "differs from approved" in wrong.stderr and not wrong.stdout
    missing = run(fakes, script, payload, commit=None)
    assert missing.returncode == 2 and "no revision evidence" in missing.stderr and not missing.stdout
    assert not (fakes / "out.wav").exists()


@pytest.mark.parametrize("case", [F5, T2], ids=["indicf5", "indictrans2"])
def test_environment_cannot_substitute_weights(fakes, case):
    script, payload, env_name = payload_for(case, fakes)
    done = run(fakes, script, payload, **{env_name: "someone/else-unapproved"})
    assert done.returncode == 2 and "refusing to run" in done.stderr
    assert not (fakes / "load.log").exists()  # nothing was loaded
    no_pin = run(fakes, script, {k: v for k, v in payload.items() if k != "revision"})
    assert no_pin.returncode == 2 and not (fakes / "load.log").exists()
