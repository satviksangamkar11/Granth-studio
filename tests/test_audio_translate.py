import ast
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


COMMIT = "c" * 40


def fake_git(dirty=""):
    return lambda *a: dirty if a[0] == "status" else COMMIT


STUB = '''import json, sys
p = json.load(sys.stdin)
print(json.dumps({"translations": ["हिंदी " + t[:10] for t in p["texts"]], "verified": {"model": p["model"], "revision": p["revision"]}}, ensure_ascii=True))
'''


def test_the_harness_runs_the_existing_translation_path_and_records_a_receipt_without_a_token(tmp_path, monkeypatch):
    at = load()
    stub = tmp_path / "stub_runner.py"
    stub.write_text(STUB, encoding="utf-8")
    monkeypatch.setattr(at, "RUNNER", stub)
    monkeypatch.setattr(at, "git", fake_git())
    monkeypatch.setenv("HF_TOKEN", "hf_" + "A" * 30)
    assert at.main(["--workdir", str(tmp_path / "w"), "--out", str(tmp_path / "o")]) == 1                    # no --execute: nothing runs
    assert json.loads((tmp_path / "o" / "translate_receipt.json").read_text(encoding="utf-8"))["verdict"] == "NOT_RUN"
    assert at.main(["--execute", "--expected-commit", COMMIT, "--workdir", str(tmp_path / "w2"), "--out", str(tmp_path / "o2")]) == 0
    receipt = json.loads((tmp_path / "o2" / "translate_receipt.json").read_text(encoding="utf-8"))
    assert receipt["verdict"] == "PASS" and len(receipt["lines"]) == 6 and all(r["candidate"] and r["assistant_hindi_draft"] for r in receipt["lines"])
    assert receipt["revision"] == at.REVISION and "hf_" + "A" * 30 not in json.dumps(receipt)
    assert at.main(["--execute", "--expected-commit", COMMIT, "--workdir", str(tmp_path / "w2"), "--out", str(tmp_path / "o3")]) == 1      # a used workdir is refused


def test_a_wrong_identity_from_the_runner_fails_the_stage(tmp_path, monkeypatch):
    at = load()
    stub = tmp_path / "bad_runner.py"
    stub.write_text(STUB.replace('p["revision"]}}', '"0" * 40}}'), encoding="utf-8")
    monkeypatch.setattr(at, "RUNNER", stub)
    monkeypatch.setattr(at, "git", fake_git())
    assert at.main(["--execute", "--expected-commit", COMMIT, "--workdir", str(tmp_path / "w"), "--out", str(tmp_path / "o")]) == 1
    assert json.loads((tmp_path / "o" / "translate_receipt.json").read_text(encoding="utf-8"))["verdict"] == "FAIL"


def test_a_dirty_wrong_or_missing_commit_and_an_in_repo_workdir_are_refused_and_nothing_validated_reaches_disk(tmp_path, monkeypatch):
    at = load()
    stub = tmp_path / "stub_runner.py"
    stub.write_text(STUB, encoding="utf-8")
    monkeypatch.setattr(at, "RUNNER", stub)
    for dirty, commit in (("M x", COMMIT), ("", "d" * 40), ("", None)):
        monkeypatch.setattr(at, "git", fake_git(dirty))
        argv = ["--execute", "--workdir", str(tmp_path / "w"), "--out", str(tmp_path / "o")] + (["--expected-commit", commit] if commit else [])
        assert at.main(argv) == 1
        assert json.loads((tmp_path / "o" / "translate_receipt.json").read_text(encoding="utf-8"))["verdict"] == "NOT_RUN"
    monkeypatch.setattr(at, "git", fake_git())
    assert at.main(["--execute", "--expected-commit", COMMIT, "--workdir", str(REPO / "_never"), "--out", str(tmp_path / "o")]) == 1
    assert not (REPO / "_never").exists()
    assert at.main(["--execute", "--expected-commit", COMMIT, "--workdir", str(tmp_path / "ok"), "--out", str(tmp_path / "o")]) == 0
    assert "status: unvalidated" in (tmp_path / "ok" / "project" / "config" / "models.yaml").read_text(encoding="utf-8").split("translation:")[1].split("speech:")[0]


def test_a_token_in_a_candidate_withholds_the_evidence_and_fails(tmp_path, monkeypatch):
    at = load()
    stub = tmp_path / "leaky.py"
    stub.write_text(STUB.replace('"हिंदी " + t[:10]', '"hf_" + "B" * 30'), encoding="utf-8")
    monkeypatch.setattr(at, "RUNNER", stub)
    monkeypatch.setattr(at, "git", fake_git())
    assert at.main(["--execute", "--expected-commit", COMMIT, "--workdir", str(tmp_path / "w"), "--out", str(tmp_path / "o")]) == 1
    assert not (tmp_path / "o" / "translation_candidates.json").exists()
    assert "B" * 30 not in (tmp_path / "o" / "translate_receipt.json").read_text(encoding="utf-8")


def test_the_notebook_parses_installs_before_the_secret_exists_and_never_stores_the_token():
    text = (REPO / "notebooks" / "kaggle_audio_translate_test.ipynb").read_text(encoding="utf-8")
    cells = json.loads(text)["cells"]
    for cell in cells:
        if cell["cell_type"] == "code":
            ast.parse("".join(cell["source"]))
    assert not re.search(r"hf_[A-Za-z0-9]{20,}", text)
    assert text.index("pip") < text.index("get_secret") and text.index("clone") < text.index("get_secret")
    assert "must not be in the environment while packages are installed" in text and "--expected-commit" in text


def test_a_leaking_runner_writes_nothing_and_prints_nothing_secret_and_a_failing_git_refuses(tmp_path, monkeypatch, capsys):
    at = load()
    stub = tmp_path / "leaky.py"
    stub.write_text(STUB.replace('"हिंदी " + t[:10]', '"hf_" + "C" * 30'), encoding="utf-8")
    monkeypatch.setattr(at, "RUNNER", stub)
    monkeypatch.setattr(at, "git", fake_git())
    assert at.main(["--execute", "--expected-commit", COMMIT, "--workdir", str(tmp_path / "w"), "--out", str(tmp_path / "o")]) == 1
    assert "C" * 30 not in capsys.readouterr().out
    assert not list((tmp_path / "w").rglob("translation_candidates.json"))                      # never reached the workdir either
    monkeypatch.setattr(at, "git", lambda *a: None)
    assert at.main(["--execute", "--expected-commit", COMMIT, "--workdir", str(tmp_path / "w9"), "--out", str(tmp_path / "o9")]) == 1
    assert not (tmp_path / "w9").exists()
    text = (REPO / "notebooks" / "kaggle_audio_translate_test.ipynb").read_text(encoding="utf-8")
    assert "SAFE = (" in text and "TOKEN\" not in k.upper()" not in text


def test_runner_stderr_is_scrubbed_before_it_is_cut_and_the_env_allowlist_is_enumerated(tmp_path, monkeypatch, capsys):
    at = load()
    stub = tmp_path / "noisy.py"
    stub.write_text("import sys\nsys.stderr.write('hf_' + 'D' * 30 + '!' * 480)\nsys.exit(3)\n", encoding="utf-8")
    monkeypatch.setattr(at, "RUNNER", stub)
    monkeypatch.setattr(at, "git", fake_git())
    assert at.main(["--execute", "--expected-commit", COMMIT, "--workdir", str(tmp_path / "w"), "--out", str(tmp_path / "o")]) == 1
    out = capsys.readouterr().out + (tmp_path / "o" / "translate_receipt.json").read_text(encoding="utf-8")
    assert "D" * 8 not in out and "runner exited 3" in out
    text = (REPO / "notebooks" / "kaggle_audio_translate_test.ipynb").read_text(encoding="utf-8")
    assert 'startswith(' not in text.split("SAFE")[1].split("env[")[0]
