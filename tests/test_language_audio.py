"""Phase D: translation candidates, voices, speech, ASR and provenance with fake subprocess runners.
Runner outputs, voices and consent records are synthetic fixtures; no real model has run."""
from __future__ import annotations

import json
import subprocess
import sys

import pytest

from granthstudio import speech, translation
from granthstudio.cli import main
from granthstudio.config import load_models, load_yaml
from granthstudio.errors import ConfigError, GateFailure, IntegrationUnavailable, TaskFailed
from granthstudio.integrity import atomic_write_json, read_json, sha256_file, sha256_obj, normalize_text
from granthstudio.pipeline import episode_store, load_bundle, plan_tasks
from granthstudio.runners import require_runner, run_json
from granthstudio.scheduler import Scheduler
from tests.conftest import REPO, have_tool
from tests.test_review_regressions import make_cpu_project

TRANSLATE = '''
import json, sys, pathlib
payload = json.load(sys.stdin)
here = pathlib.Path(__file__).parent
with (here / "calls.log").open("a") as log:
    log.write(json.dumps(payload["texts"]) + "\\n")
table = json.loads((here / "table.json").read_text(encoding="utf-8"))
print(json.dumps({"translations": [table[t] for t in payload["texts"]]}))
'''
TTS = '''
import json, subprocess, sys, pathlib, os
payload = json.load(sys.stdin)
here = pathlib.Path(__file__).parent
with (here / "tts.log").open("a") as log:
    log.write(payload["dialogue_id"] + "\\n")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
                "sine=frequency=330:sample_rate=24000:duration=" + os.environ.get("FAKE_TTS_SECONDS", "0.2"),
                "-c:a", "pcm_s16le", "-f", "wav", payload["out_path"]], check=True)
print(json.dumps({"sample_rate": 24000}))
'''
ASR = '''
import json, os, sys
payload = json.load(sys.stdin)
print(json.dumps({"text": os.environ["FAKE_ASR_TEXT"]}))
'''


def runner_section(tmp_path, name, source, **extra):
    script = tmp_path / f"{name}.py"; script.write_text(source, encoding="utf-8")
    return {"status": "validated", "command": [sys.executable, str(script)], "model": f"synthetic-{name}",
            "revision": "synthetic-1", "timeout_s": 60, **extra}


def set_models(project, **sections):
    models = load_models(project); models.update(sections)
    atomic_write_json(project.root / "config" / "models.yaml", models)
    return models


# ------------------------------------------------------------------ runner contract

def test_runner_sections_refuse_until_validated_and_pinned(project, tmp_path):
    models = load_models(project)
    for key in ("translation", "speech", "asr"):
        with pytest.raises(IntegrationUnavailable, match="NOT VALIDATED"):
            require_runner(models, key, key)
    section = runner_section(tmp_path, "t", TRANSLATE)
    require_runner({"translation": section}, "translation", "t")
    with pytest.raises(IntegrationUnavailable, match="revision is not set"):
        require_runner({"translation": {**section, "revision": None}}, "translation", "t")


def test_run_json_reports_failures_precisely(tmp_path):
    ok = {"command": [sys.executable, "-c", "import sys,json; print(json.dumps({'a': 1}))"], "timeout_s": 30}
    assert run_json(ok, {}) == {"a": 1}
    with pytest.raises(TaskFailed, match="exited 3.*boom"):
        run_json({"command": [sys.executable, "-c", "import sys; sys.stderr.write('boom'); sys.exit(3)"], "timeout_s": 30}, {})
    with pytest.raises(TaskFailed, match="invalid JSON"):
        run_json({"command": [sys.executable, "-c", "print('not json')"], "timeout_s": 30}, {})
    with pytest.raises(TaskFailed, match="exceeded"):
        run_json({"command": [sys.executable, "-c", "import time; time.sleep(5)"], "timeout_s": 0.3}, {})
    with pytest.raises(IntegrationUnavailable, match="not found"):
        run_json({"command": ["no-such-runner-binary"], "timeout_s": 5}, {})


# ------------------------------------------------------------------ translation

@pytest.fixture
def hindi_setup(approved_project, tmp_path):
    hindi = load_yaml(approved_project.episodes_dir / "adhyay_01" / "hi.yaml")
    marathi = load_yaml(approved_project.episodes_dir / "adhyay_01" / "mr.yaml")
    table = {m["text"]: h["text"] for m, h in zip(marathi["entries"], hindi["entries"])}
    (tmp_path / "table.json").write_text(json.dumps(table, ensure_ascii=False), encoding="utf-8")
    set_models(approved_project, translation=runner_section(tmp_path, "translate", TRANSLATE))
    (approved_project.episodes_dir / "adhyay_01" / "hi.yaml").unlink()
    return table, tmp_path


def test_translation_candidates_review_approve_and_bundle_loads(approved_project, hindi_setup):
    table, tmp_path = hindi_setup
    models = load_models(approved_project)
    assert translation.generate_candidates(approved_project, models, 1, execute=False) == ["d_0001", "d_0002"]
    assert not (tmp_path / "calls.log").exists()
    assert translation.generate_candidates(approved_project, models, 1, execute=True) == ["d_0001", "d_0002"]
    assert translation.generate_candidates(approved_project, models, 1, execute=True) == []  # idempotent
    assert len((tmp_path / "calls.log").read_text().splitlines()) == 1
    with pytest.raises(Exception):
        load_bundle(approved_project, models, 1)  # no Hindi timeline yet: nothing is auto-approved
    canon = load_bundle.__globals__["load_canon"](approved_project)
    rows = translation.review_report(approved_project, canon, 1)
    assert [r["problems"] for r in rows] == [[], []]
    with pytest.raises(ConfigError, match="reviewer"):
        translation.approve_translation(approved_project, canon, 1, "d_0001", "  ")
    for line in ("d_0001", "d_0002"):
        entry = translation.approve_translation(approved_project, canon, 1, line, "synthetic-test-only")
        assert entry["alignment"]["source"]["origin"] == "model_candidate"
        assert entry["alignment"]["source"]["model"] == "synthetic-translate"
    bundle = load_bundle(approved_project, models, 1)
    assert [e["dialogue_id"] for e in bundle.timelines["hi"]["entries"]] == ["d_0001", "d_0002"]


def test_translation_checks_block_dropped_numbers_and_protected_terms(approved_project, hindi_setup):
    table, tmp_path = hindi_setup
    bad = {mr: hi.replace("2", "3") if "2" in hi else hi.replace("TERMX-HI", "other") for mr, hi in table.items()}
    (tmp_path / "table.json").write_text(json.dumps(bad, ensure_ascii=False), encoding="utf-8")
    models = load_models(approved_project)
    translation.generate_candidates(approved_project, models, 1, execute=True)
    canon = load_bundle.__globals__["load_canon"](approved_project)
    rows = translation.review_report(approved_project, canon, 1)
    assert "numeric facts differ" in rows[0]["problems"][0] and "protected term term_synth_x" in rows[1]["problems"][0]
    for line, message in (("d_0001", "numeric facts differ"), ("d_0002", "protected term")):
        with pytest.raises(GateFailure, match=message):
            translation.approve_translation(approved_project, canon, 1, line, "synthetic-test-only")
    assert not (approved_project.episodes_dir / "adhyay_01" / "hi.yaml").exists()
    # a human may supply corrected text instead; it is checked the same way and labelled as human text
    fixed = translation.approve_translation(approved_project, canon, 1, "d_0002", "synthetic-test-only", text="TERMX-HI सुधारित")
    assert fixed["alignment"]["source"] == {"origin": "human_text"}
    assert fixed["alignment"]["verification"]["hi_sha256"] == sha256_obj(normalize_text("TERMX-HI सुधारित"))


def test_translation_cli_requires_confirm_and_runner(approved_project, hindi_setup, capsys):
    root = ["--root", str(approved_project.root)]
    assert main([*root, "translate", "candidates", "1"]) == 0
    assert main([*root, "translate", "approve", "1", "--line", "d_0001", "--reviewer", "x"]) == 1
    assert "--confirm" in capsys.readouterr().err
    set_models(approved_project, translation=load_yaml(REPO / "config" / "models.yaml")["translation"])  # shipped state
    assert main([*root, "translate", "candidates", "1", "--execute"]) == 3


# ------------------------------------------------------------------ speech, ASR and provenance

def test_compare_transcript_reports_word_differences_only():
    same = speech.compare_transcript("राम, आला।", "राम आला")
    assert same["similarity"] == 1.0 and same["missing_words"] == [] and same["extra_words"] == []
    diff = speech.compare_transcript("एक दो तीन चार", "एक तीन पांच")
    assert diff["missing_words"] == ["चार", "दो"] and diff["extra_words"] == ["पांच"] and 0 < diff["similarity"] < 1


def write_voices(project, speakers=("chr_synth_a", "chr_synth_b"), consent=True):
    voices = []
    for speaker in speakers:
        for lang in ("mr", "hi"):
            reference = project.artifacts_dir / "voices" / f"{speaker}_{lang}.wav"
            reference.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "sine=frequency=220:sample_rate=24000:duration=0.3",
                            "-c:a", "pcm_s16le", str(reference)], check=True, timeout=20)
            voice = {"voice_id": f"voice_{speaker}_{lang}", "speaker": speaker, "language": lang,
                     "reference_audio": {"path": reference.name, "sha256": sha256_file(reference)},
                     "reference_transcript": "synthetic reference", "model_version": "synthetic-voice-1"}
            if consent:
                voice["consent"] = {"basis": "own_recording", "granted_by": "synthetic-test-only",
                                    "document_ref": "synthetic-consent-record", "recorded_at": "2026-10-22"}
            voices.append(voice)
    atomic_write_json(project.canon_dir / "voices.yaml", {"schema_version": 1, "voices": voices})


@pytest.mark.skipif(not (have_tool("ffmpeg") and have_tool("ffprobe")), reason="media tools missing")
def test_voice_needs_consent_record_and_unchanged_reference(approved_project):
    with pytest.raises(GateFailure, match="no licensed or consented mr voice"):
        speech.voice_for(approved_project, "chr_synth_a", "mr")
    write_voices(approved_project, consent=False)
    with pytest.raises(Exception, match="consent"):
        speech.load_voices(approved_project)
    write_voices(approved_project)
    assert speech.voice_for(approved_project, "chr_synth_a", "mr")["voice_id"] == "voice_chr_synth_a_mr"
    (approved_project.artifacts_dir / "voices" / "chr_synth_a_mr.wav").write_bytes(b"changed")
    with pytest.raises(GateFailure, match="reference audio missing or changed"):
        speech.voice_for(approved_project, "chr_synth_a", "mr")


@pytest.mark.skipif(not (have_tool("ffmpeg") and have_tool("ffprobe")), reason="media tools missing")
def test_speech_asr_approval_and_provenance_reach_the_release(approved_project, tmp_path, monkeypatch):
    current = make_cpu_project(approved_project)
    write_voices(approved_project)
    set_models(approved_project, speech=runner_section(tmp_path, "tts", TTS), asr=runner_section(tmp_path, "asr", ASR))
    models = load_models(approved_project)
    assert speech.generate_speech(approved_project, models, 1, "mr", ["d_0001"], execute=False) == ["d_0001"]
    assert not (tmp_path / "tts.log").exists()
    assert speech.generate_speech(approved_project, models, 1, "mr", ["d_0001"], execute=True) == ["d_0001"]
    assert speech.generate_speech(approved_project, models, 1, "mr", ["d_0001"], execute=True) == []
    assert (tmp_path / "tts.log").read_text().split() == ["d_0001"]
    record = read_json(speech.record_path(approved_project, "mr", "d_0001"))
    assert abs(record["duration_s"] - 0.2) < 0.01 and record["voice_id"] == "voice_chr_synth_a_mr"
    with pytest.raises(GateFailure, match="no speech candidate"):
        speech.approve_speech(approved_project, 1, "mr", "d_0002", "synthetic-test-only")
    monkeypatch.setenv("FAKE_ASR_TEXT", "SYNTH-A says things")
    report = speech.asr_check(approved_project, models, 1, "mr", "d_0001")
    assert report["missing_words"] == ["2"] and report["enforced"] is False and report["similarity"] < 1
    audio = speech.approve_speech(approved_project, 1, "mr", "d_0001", "synthetic-test-only")
    assert audio["provenance"]["origin"] == "generated" and audio["provenance"]["asr_report_sha256"]
    assert audio["speech_reviewed_by"] == "synthetic-test-only"
    scheduler = Scheduler(episode_store(approved_project, 1))
    bundle = load_bundle(approved_project, models, 1)
    tasks = plan_tasks(bundle, scheduler)
    assert all(r.status == "complete" for r in scheduler.run(tasks))
    for lang, expected in (("mr", ["generated", "imported"]), ("hi", ["imported", "imported"])):
        task = next(t for t in tasks if t.name == f"assemble_{lang}")
        directory = scheduler.task_dir(task)
        provenance = read_json(directory / "provenance.json")
        assert [line["audio"]["origin"] for line in provenance["lines"]] == expected
        assert provenance["subtitles_sha256"] == sha256_file(next(directory.glob("*.srt")))
        assert provenance["video_sha256"] == sha256_file(next(directory.glob("*.mp4")))
    hindi = read_json(scheduler.task_dir(next(t for t in tasks if t.name == "assemble_hi")) / "provenance.json")
    assert hindi["lines"][0]["translation"] is None  # fixture Hindi is hand-written, not a model candidate


@pytest.mark.skipif(not (have_tool("ffmpeg") and have_tool("ffprobe")), reason="media tools missing")
def test_speech_approval_refuses_changed_text_and_missing_consent(approved_project, tmp_path):
    make_cpu_project(approved_project)
    write_voices(approved_project)
    set_models(approved_project, speech=runner_section(tmp_path, "tts", TTS))
    models = load_models(approved_project)
    speech.generate_speech(approved_project, models, 1, "hi", ["d_0001"], execute=True)
    path = approved_project.episodes_dir / "adhyay_01" / "hi.yaml"
    document = load_yaml(path); document["entries"][0]["text"] += " बदला"
    atomic_write_json(path, document)
    with pytest.raises(GateFailure, match="script text changed"):
        speech.approve_speech(approved_project, 1, "hi", "d_0001", "synthetic-test-only")
    write_voices(approved_project, speakers=("chr_synth_b",))
    with pytest.raises(GateFailure, match="no licensed or consented hi voice reference recorded for chr_synth_a"):
        speech.generate_speech(approved_project, models, 1, "hi", ["d_0001"], execute=True)


@pytest.mark.skipif(not (have_tool("ffmpeg") and have_tool("ffprobe")), reason="media tools missing")
def test_speech_cli_dry_run_and_confirm_gate(approved_project, tmp_path, capsys):
    make_cpu_project(approved_project)
    write_voices(approved_project)
    root = ["--root", str(approved_project.root)]
    assert main([*root, "speech", "voices"]) == 0
    assert main([*root, "speech", "generate", "1", "--lang", "mr"]) == 0
    assert "would be generated" in capsys.readouterr().out
    assert main([*root, "speech", "generate", "1", "--lang", "mr", "--execute"]) == 3  # speech runner NOT VALIDATED
    assert main([*root, "speech", "approve", "1", "--lang", "mr", "--line", "d_0001", "--reviewer", "x"]) == 1


ALIGN = '''
import json, sys, pathlib
payload = json.load(sys.stdin)
with (pathlib.Path(__file__).parent / "align.log").open("a") as log:
    log.write(payload["audio_path"] + chr(10))
words = payload["text"].split()
print(json.dumps({"words": [{"word": w, "start_s": 0.01 * i, "end_s": 0.01 * i + 0.009} for i, w in enumerate(words)]}))
'''


def _edit(project, lang, mutate):
    path = project.episodes_dir / "adhyay_01" / f"{lang}.yaml"
    document = load_yaml(path); mutate(document["entries"][0])
    atomic_write_json(path, document)


@pytest.mark.skipif(not (have_tool("ffmpeg") and have_tool("ffprobe")), reason="media tools missing")
@pytest.mark.parametrize("lang,mutate,match", [
    ("mr", lambda e: e.update(text=e["text"] + " बदल"), "Marathi lock"),                      # unapproved Marathi text
    ("hi", lambda e: e.update(text=e["text"] + " बदला"), "Hindi semantic review does not match"),  # stale Hindi review
    ("hi", lambda e: e["alignment"].update(reviewed=False), "Hindi semantic review is not approved"),
    ("mr", lambda e: e.update(speaker="chr_synth_b"), "speaker differs"),                       # dialogue attribution
])
def test_speech_validation_failure_never_invokes_tts(approved_project, tmp_path, lang, mutate, match):
    make_cpu_project(approved_project)
    write_voices(approved_project)
    set_models(approved_project, speech=runner_section(tmp_path, "tts", TTS))
    _edit(approved_project, lang, mutate)
    with pytest.raises(GateFailure, match=match):
        speech.generate_speech(approved_project, load_models(approved_project), 1, lang, ["d_0001"], execute=True)
    assert not (tmp_path / "tts.log").exists()
    assert not speech.candidate_root(approved_project, lang).exists()


@pytest.mark.skipif(not (have_tool("ffmpeg") and have_tool("ffprobe")), reason="media tools missing")
def test_release_alignment_uses_approved_audio_and_rejects_stale_candidates(approved_project, tmp_path):
    make_cpu_project(approved_project)
    write_voices(approved_project)
    set_models(approved_project, speech=runner_section(tmp_path, "tts", TTS), aligner=runner_section(tmp_path, "align", ALIGN))
    models = load_models(approved_project)
    speech.generate_speech(approved_project, models, 1, "mr", ["d_0001"], execute=True)  # candidate, not approved
    release = load_yaml(approved_project.episodes_dir / "adhyay_01" / "mr.yaml")["entries"][0]["audio"]
    report = speech.align_words(approved_project, models, 1, "mr", "d_0001")
    assert report["audio_sha256"] == release["sha256"] and report["audio_source"] == "release"  # not the newer candidate
    assert (speech.candidate_root(approved_project, "mr") / "d_0001.align.json").is_file()
    cand = speech.align_words(approved_project, models, 1, "mr", "d_0001", source="candidate")
    assert cand["audio_sha256"] != release["sha256"] and cand["audio_source"] == "candidate"
    assert (speech.candidate_root(approved_project, "mr") / "d_0001.align.candidate.json").is_file()
    assert read_json(speech.candidate_root(approved_project, "mr") / "d_0001.align.json")["audio_sha256"] == release["sha256"]
    # stale candidate: script text changed after generation
    record = read_json(speech.record_path(approved_project, "mr", "d_0001"))
    record["text_sha256"] = "0" * 64
    atomic_write_json(speech.record_path(approved_project, "mr", "d_0001"), record)
    with pytest.raises(GateFailure, match="stale"):
        speech.align_words(approved_project, models, 1, "mr", "d_0001", source="candidate")
    # release audio bound to other text is refused too
    _edit(approved_project, "mr", lambda e: e["audio"].update(text_sha256="1" * 64))
    with pytest.raises(GateFailure, match="different script text"):
        speech.align_words(approved_project, models, 1, "mr", "d_0001")


# ------------------------------------------------------------------ Fix 8: verified model provenance

def with_identity(source):
    """Fake runner that reports the identity it 'loaded' via FAKE_VERIFIED ('' = no evidence, else model@revision)."""
    return source.replace("print(json.dumps({", "_v = os.environ.get('FAKE_VERIFIED', '')\n"
        "_m, _, _r = _v.partition('@')\nprint(json.dumps({**({'verified': {'model': _m, 'revision': _r}} if _v else {}), ", 1)


TTS_ID = with_identity(TTS)
TRANSLATE_ID = with_identity("import os\n" + TRANSLATE)
GOOD = "synthetic-tts@synthetic-1"


@pytest.mark.skipif(not (have_tool("ffmpeg") and have_tool("ffprobe")), reason="media tools missing")
def test_verified_identity_survives_runner_candidate_approval_and_release(approved_project, tmp_path, monkeypatch):
    make_cpu_project(approved_project)
    write_voices(approved_project)
    set_models(approved_project, speech=runner_section(tmp_path, "tts", TTS_ID))
    models = load_models(approved_project)
    monkeypatch.setenv("FAKE_VERIFIED", GOOD)
    speech.generate_speech(approved_project, models, 1, "mr", ["d_0001"], execute=True)
    record = read_json(speech.record_path(approved_project, "mr", "d_0001"))
    assert record["model_identity"] == {"status": "verified", "model": "synthetic-tts", "revision": "synthetic-1"}
    audio = speech.approve_speech(approved_project, 1, "mr", "d_0001", "synthetic-test-only")   # approval keeps it
    assert audio["provenance"]["model_identity"] == record["model_identity"]
    scheduler = Scheduler(episode_store(approved_project, 1))
    tasks = plan_tasks(load_bundle(approved_project, models, 1), scheduler)
    assert all(r.status == "complete" for r in scheduler.run(tasks))
    release = read_json(scheduler.task_dir(next(t for t in tasks if t.name == "assemble_mr")) / "provenance.json")
    assert release["lines"][0]["audio"]["model_identity"]["status"] == "verified"
    assert release["lines"][1]["audio"].get("model_identity") is None   # imported audio claims nothing


@pytest.mark.skipif(not (have_tool("ffmpeg") and have_tool("ffprobe")), reason="media tools missing")
def test_missing_or_mismatched_or_tampered_identity_is_never_recorded_as_verified(approved_project, tmp_path, monkeypatch):
    make_cpu_project(approved_project)
    write_voices(approved_project)
    set_models(approved_project, speech=runner_section(tmp_path, "tts", TTS_ID))
    models = load_models(approved_project)
    monkeypatch.setenv("FAKE_VERIFIED", "")                                   # no verification evidence
    speech.generate_speech(approved_project, models, 1, "mr", ["d_0001"], execute=True)
    path = speech.record_path(approved_project, "mr", "d_0001")
    assert read_json(path)["model_identity"] == {"status": "unverified"}
    assert speech.approve_speech(approved_project, 1, "mr", "d_0001", "x")["provenance"]["model_identity"] == {"status": "unverified"}
    path.unlink()
    for old in speech.candidate_root(approved_project, "mr").glob("d_0001_*.wav"):
        old.unlink()
    monkeypatch.setenv("FAKE_VERIFIED", "synthetic-tts@other-revision")       # mismatched identity
    with pytest.raises(GateFailure, match="refusing the output"):
        speech.generate_speech(approved_project, models, 1, "mr", ["d_0001"], execute=True)
    assert not path.exists() and not list(speech.candidate_root(approved_project, "mr").glob("d_0001_*.wav"))
    monkeypatch.setenv("FAKE_VERIFIED", GOOD)
    speech.generate_speech(approved_project, models, 1, "mr", ["d_0001"], execute=True)
    record = read_json(path); record["revision"] = "forged"; atomic_write_json(path, record)   # tampered record
    with pytest.raises(GateFailure, match="different configured model"):
        speech.approve_speech(approved_project, 1, "mr", "d_0001", "x")


def test_translation_identity_reaches_the_approved_hindi_line_and_rejects_mismatch(approved_project, hindi_setup, monkeypatch):
    table, tmp_path = hindi_setup
    set_models(approved_project, translation=runner_section(tmp_path, "translate", TRANSLATE_ID))
    models = load_models(approved_project)
    canon = load_bundle.__globals__["load_canon"](approved_project)
    monkeypatch.setenv("FAKE_VERIFIED", "synthetic-translate@other")
    with pytest.raises(GateFailure, match="refusing the output"):
        translation.generate_candidates(approved_project, models, 1, execute=True)
    assert not translation.candidates_path(approved_project, 1).exists()
    monkeypatch.setenv("FAKE_VERIFIED", "synthetic-translate@synthetic-1")
    translation.generate_candidates(approved_project, models, 1, execute=True)
    entry = translation.approve_translation(approved_project, canon, 1, "d_0001", "synthetic-test-only")
    assert entry["alignment"]["source"]["model_identity"] == {"status": "verified", "model": "synthetic-translate", "revision": "synthetic-1"}
    translation.approve_translation(approved_project, canon, 1, "d_0002", "synthetic-test-only")
    hindi = load_bundle(approved_project, models, 1).timelines["hi"]["entries"]
    assert [e["alignment"]["source"]["model_identity"]["status"] for e in hindi] == ["verified", "verified"]
    monkeypatch.setenv("FAKE_VERIFIED", "")
    path = translation.candidates_path(approved_project, 1); path.unlink()
    translation.generate_candidates(approved_project, models, 1, execute=True)
    assert translation.approve_translation(approved_project, canon, 1, "d_0002", "x")["alignment"]["source"]["model_identity"] == {"status": "unverified"}  # missing evidence is never "verified"


@pytest.mark.skipif(not (have_tool("ffmpeg") and have_tool("ffprobe")), reason="media tools missing")
def test_speech_evidence_is_content_addressed_and_forgeries_are_refused(approved_project, tmp_path, monkeypatch):
    make_cpu_project(approved_project)
    write_voices(approved_project)
    set_models(approved_project, speech=runner_section(tmp_path, "tts", TTS_ID))
    models = load_models(approved_project)
    monkeypatch.setenv("FAKE_VERIFIED", "")
    speech.generate_speech(approved_project, models, 1, "mr", ["d_0001"], execute=True)       # genuinely unverified run
    path = speech.record_path(approved_project, "mr", "d_0001")
    original = read_json(path)
    assert original["model_identity"] == {"status": "unverified"} and original["evidence_sha256"]
    forged = {**original, "model_identity": {"status": "verified", "model": "synthetic-tts", "revision": "synthetic-1"}}
    atomic_write_json(path, forged)                                  # editable, self-consistent "verified" block
    with pytest.raises(GateFailure, match="stored identity differs from the run evidence"):
        speech.approve_speech(approved_project, 1, "mr", "d_0001", "x")
    atomic_write_json(path, {**forged, "evidence_sha256": None})     # ...or with the evidence pointer removed
    with pytest.raises(GateFailure, match="carries no run evidence"):
        speech.approve_speech(approved_project, 1, "mr", "d_0001", "x")
    atomic_write_json(path, original)
    evidence_file = speech.evidence_root(approved_project) / f"{original['evidence_sha256']}.json"
    body = read_json(evidence_file); body["identity"] = {"status": "verified", "model": "synthetic-tts", "revision": "synthetic-1"}
    atomic_write_json(evidence_file, body)                           # forge the evidence file too
    with pytest.raises(GateFailure, match="integrity check"):
        speech.approve_speech(approved_project, 1, "mr", "d_0001", "x")
    evidence_file.unlink()
    with pytest.raises(GateFailure, match="evidence .* is missing"):
        speech.approve_speech(approved_project, 1, "mr", "d_0001", "x")


@pytest.mark.skipif(not (have_tool("ffmpeg") and have_tool("ffprobe")), reason="media tools missing")
def test_release_provenance_keeps_the_exact_evidence_pointer(approved_project, tmp_path, monkeypatch):
    make_cpu_project(approved_project)
    write_voices(approved_project)
    set_models(approved_project, speech=runner_section(tmp_path, "tts", TTS_ID))
    models = load_models(approved_project)
    monkeypatch.setenv("FAKE_VERIFIED", GOOD)
    speech.generate_speech(approved_project, models, 1, "mr", ["d_0001"], execute=True)
    evidence = read_json(speech.record_path(approved_project, "mr", "d_0001"))["evidence_sha256"]
    audio = speech.approve_speech(approved_project, 1, "mr", "d_0001", "synthetic-test-only")
    assert audio["provenance"]["evidence_sha256"] == evidence
    scheduler = Scheduler(episode_store(approved_project, 1))
    tasks = plan_tasks(load_bundle(approved_project, models, 1), scheduler)
    assert all(r.status == "complete" for r in scheduler.run(tasks))
    release = read_json(scheduler.task_dir(next(t for t in tasks if t.name == "assemble_mr")) / "provenance.json")
    assert release["lines"][0]["audio"]["evidence_sha256"] == evidence
    assert read_json(speech.evidence_root(approved_project) / f"{evidence}.json")["identity"]["status"] == "verified"


def test_translation_batches_keep_their_own_evidence_and_later_runs_do_not_downgrade(approved_project, hindi_setup, monkeypatch):
    table, tmp_path = hindi_setup
    set_models(approved_project, translation=runner_section(tmp_path, "translate", TRANSLATE_ID))
    models = load_models(approved_project)
    canon = load_bundle.__globals__["load_canon"](approved_project)
    monkeypatch.setenv("FAKE_VERIFIED", "synthetic-translate@synthetic-1")
    translation.generate_candidates(approved_project, models, 1, execute=True)              # batch 1: both verified
    # Marathi line 2 changes -> only it is regenerated, by a run that provides no verification evidence
    mr_path = approved_project.episodes_dir / "adhyay_01" / "mr.yaml"
    document = load_yaml(mr_path); old_text = document["entries"][1]["text"]
    document["entries"][1]["text"] = old_text + " extra"; atomic_write_json(mr_path, document)
    table[old_text + " extra"] = table[old_text]
    (tmp_path / "table.json").write_text(json.dumps(table, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setenv("FAKE_VERIFIED", "")
    assert translation.generate_candidates(approved_project, models, 1, execute=True) == ["d_0002"]
    found = read_json(translation.candidates_path(approved_project, 1))
    first, second = found["candidates"]
    assert first["model_identity"]["status"] == "verified" and second["model_identity"] == {"status": "unverified"}
    assert first["evidence_sha256"] != second["evidence_sha256"]
    assert translation.approve_translation(approved_project, canon, 1, "d_0001", "x")["alignment"]["source"]["model_identity"]["status"] == "verified"
    # tamper: claim verification for the unverified candidate
    found["candidates"][1]["model_identity"] = {"status": "verified", "model": "synthetic-translate", "revision": "synthetic-1"}
    atomic_write_json(translation.candidates_path(approved_project, 1), found)
    with pytest.raises(GateFailure, match="stored identity differs from the run evidence"):
        translation.approve_translation(approved_project, canon, 1, "d_0002", "x")
    # tamper: a candidate text edited after the run is not covered by its evidence
    found["candidates"][1]["model_identity"] = {"status": "unverified"}
    found["candidates"][1]["candidate_sha256"] = "0" * 64
    atomic_write_json(translation.candidates_path(approved_project, 1), found)
    with pytest.raises(GateFailure, match="does not cover this output"):
        translation.approve_translation(approved_project, canon, 1, "d_0002", "x")
