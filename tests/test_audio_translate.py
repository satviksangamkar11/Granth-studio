import importlib.util
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def load():
    spec = importlib.util.spec_from_file_location("audio_translate_test", REPO / "scripts" / "audio_translate_test.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["audio_translate_test"] = module
    spec.loader.exec_module(module)
    return module


STUB = '''import json, sys
p = json.load(sys.stdin)
print(json.dumps({"translations": ["हिंदी " + t[:10] for t in p["texts"]], "verified": {"model": p["model"], "revision": p["revision"]}}, ensure_ascii=True))
'''


def test_the_harness_runs_the_existing_translation_path_and_records_a_receipt_without_a_token(tmp_path, monkeypatch):
    at = load()
    stub = tmp_path / "stub_runner.py"
    stub.write_text(STUB, encoding="utf-8")
    monkeypatch.setattr(at, "RUNNER", stub)
    monkeypatch.setenv("HF_TOKEN", "hf_" + "A" * 30)
    assert at.main(["--workdir", str(tmp_path / "w"), "--out", str(tmp_path / "o")]) == 1                    # no --execute: nothing runs
    assert json.loads((tmp_path / "o" / "translate_receipt.json").read_text(encoding="utf-8"))["verdict"] == "NOT_RUN"
    assert at.main(["--execute", "--workdir", str(tmp_path / "w2"), "--out", str(tmp_path / "o2")]) == 0
    receipt = json.loads((tmp_path / "o2" / "translate_receipt.json").read_text(encoding="utf-8"))
    assert receipt["verdict"] == "PASS" and len(receipt["lines"]) == 6 and all(r["candidate"] and r["assistant_hindi_draft"] for r in receipt["lines"])
    assert receipt["revision"] == at.REVISION and "hf_" + "A" * 30 not in json.dumps(receipt)
    assert at.main(["--execute", "--workdir", str(tmp_path / "w2"), "--out", str(tmp_path / "o3")]) == 1      # a used workdir is refused


def test_a_wrong_identity_from_the_runner_fails_the_stage(tmp_path, monkeypatch):
    at = load()
    stub = tmp_path / "bad_runner.py"
    stub.write_text(STUB.replace('p["revision"]}}', '"0" * 40}}'), encoding="utf-8")
    monkeypatch.setattr(at, "RUNNER", stub)
    assert at.main(["--execute", "--workdir", str(tmp_path / "w"), "--out", str(tmp_path / "o")]) == 1
    assert json.loads((tmp_path / "o" / "translate_receipt.json").read_text(encoding="utf-8"))["verdict"] == "FAIL"


def test_the_notebook_takes_the_token_only_from_the_kaggle_secret_and_never_stores_it():
    text = (REPO / "notebooks" / "kaggle_audio_translate_test.ipynb").read_text(encoding="utf-8")
    assert 'get_secret(\\"HF_TOKEN\\")' in text and not re.search(r"hf_[A-Za-z0-9]{20,}", text)
    assert text.index("get_secret") < text.index("clone")                                         # the secret is checked before anything is cloned or installed
