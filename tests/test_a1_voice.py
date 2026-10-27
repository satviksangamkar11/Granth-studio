"""Voice system checks (no model, no network, no audio generation): the job list, text preparation, packaging, and ingestion/measurement of (synthetic) wav files."""
import hashlib
import importlib.util
import json
import wave
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


v = load("a1_voices_t", "scripts/source/a1_voices.py")
vc = load("a1_voice_t", "scripts/source/a1_voice.py")
a1 = load("a1_audio_t2", "scripts/source/a1_audio.py")
PLAN = json.loads((ROOT / "canon" / "audio" / "A1_audio_plan.json").read_text(encoding="utf-8"))
CARD = {"mr": {"Sanjay", "Sunita", "Nikhil", "Radha", "Varun", "Isha"}, "hi": {"Rohit", "Divya", "Aman", "Rani"}}      # the speakers the model card lists


def test_every_line_gets_a_marathi_and_a_hindi_job_with_a_listed_speaker():
    jobs = v.build_jobs(PLAN)
    assert len(jobs) == 2 * len(PLAN["lines"]) and len({j["id"] for j in jobs}) == len(jobs)
    assert {j["lang"] for j in jobs} == {"mr", "hi"}
    for j in jobs:
        assert j["speaker"] in CARD[j["lang"]] and j["speaker"] in j["description"] and j["text"].strip() and j["seed"] >= 0
    assert {j["voice"] for j in jobs} == {"narrator", "gajanan", "bankatlal", "damodarpant"}


def test_marathi_has_four_distinct_voices_and_hindi_shares_one_speaker_by_description_only():
    mr = {k: s for k, (s, d) in v.VOICES["mr"].items()}
    hi = {k: s for k, (s, d) in v.VOICES["hi"].items()}
    assert len(set(mr.values())) == 4
    assert hi["bankatlal"] == hi["damodarpant"] == "Aman" and v.VOICES["hi"]["bankatlal"][1] != v.VOICES["hi"]["damodarpant"][1]


def test_text_preparation_never_changes_a_word():
    import re
    qn = load("dt_for_voice", "scripts/source/director_test.py").qnorm
    for l in PLAN["lines"]:
        for t in (l["marathi"], l["hindi"]):
            assert qn(v.prep_text(t)) == qn(t), t                                          # same letters, only pauses and quote marks differ
    assert v.prep_text("अ ब । क ड") == "अ ब, क ड." and v.prep_text("'नमस्कार' !") == "नमस्कार !"
    assert not re.search(r"[।\"'‘’“”]", " ".join(j["text"] for j in v.build_jobs(PLAN)))


def test_the_kaggle_job_never_prints_or_stores_the_token():
    src = (ROOT / "scripts" / "audio" / "a1_tts_run.py").read_text(encoding="utf-8")
    assert "print(token" not in src and "print(os.environ" not in src and "found in an output file" in src and "get_secret(\"HF_TOKEN\")" in src


def write_wav(path, seconds, rate=24000):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"\x00\x00" * int(rate * seconds))


def make_job(tmp_path, lines, tamper=None):
    folder = tmp_path / "job"
    rows = []
    for lid, mr, hi in lines:
        for lang, secs in (("mr", mr), ("hi", hi)):
            rel = f"wav/{lang}/{lid}.{lang}.wav"
            write_wav(folder / rel, secs)
            rows.append({"id": f"{lid}.{lang}", "lang": lang, "voice": "narrator", "speaker": "Sunita", "text": "t", "ok": True, "wav": rel, "seconds": 999, "wav_sha256": hashlib.sha256((folder / rel).read_bytes()).hexdigest()})
    if tamper:
        rows[0]["wav_sha256"] = "0" * 64
    (folder / "tts_manifest.json").write_text(json.dumps({"model": "m", "sampling_rate": 24000, "lines": rows}), encoding="utf-8")
    return folder


def plan_for(tmp_path, ids):
    f = tmp_path / "plan.json"
    f.write_text(json.dumps({"lines": [{"id": i, "voice": "narrator", "marathi": "t", "hindi": "t", "priority": "core", "scene": "S1"} for i in ids]}), encoding="utf-8")
    return f


def test_ingest_re_measures_durations_from_the_wav_not_from_the_manifest(tmp_path):
    folder = make_job(tmp_path, [("S1-L1", 8.0, 7.0), ("S1-L2", 3.0, 3.5)])
    res = vc.ingest(folder, tmp_path / "w", tmp_path / "m.json", tmp_path / "sheet.md", tmp_path / "audio", plan_for(tmp_path, ["S1-L1", "S1-L2"]))
    m = json.loads((tmp_path / "m.json").read_text(encoding="utf-8"))
    assert res["problems"] == [] and m["lines"]["S1-L1"] == {"mr": 8.0, "hi": 7.0} and m["lines"]["S1-L2"] == {"mr": 3.0, "hi": 3.5}      # the manifest's 999 is ignored
    assert (tmp_path / "audio" / "wav" / "mr" / "S1-L1.mr.wav").exists() and "S1-L1" in (tmp_path / "sheet.md").read_text(encoding="utf-8")


def test_a_wav_that_does_not_match_its_hash_is_a_problem_and_unmeasured(tmp_path):
    folder = make_job(tmp_path, [("S1-L1", 8.0, 7.0)], tamper=True)
    res = vc.ingest(folder, tmp_path / "w", tmp_path / "m.json", tmp_path / "s.md", tmp_path / "a", plan_for(tmp_path, ["S1-L1"]))
    assert any("hash" in p for p in res["problems"])
    assert not (tmp_path / "m.json").exists()                       # fail closed: nothing is published from a bad job


def test_a_missing_job_or_a_wav_path_outside_the_folder_is_a_problem(tmp_path):
    folder = make_job(tmp_path, [("S1-L1", 2.0, 2.0)])
    man = json.loads((folder / "tts_manifest.json").read_text(encoding="utf-8"))
    man["lines"][0]["wav"] = "../outside.wav"
    (folder / "tts_manifest.json").write_text(json.dumps(man), encoding="utf-8")
    res = vc.ingest(folder, tmp_path / "w", tmp_path / "m.json", tmp_path / "s.md", tmp_path / "a", plan_for(tmp_path, ["S1-L1", "S1-L2"]))
    assert any("S1-L2" in p and "missing" in p for p in res["problems"]) and any("leaves" in p for p in res["problems"]) and not (tmp_path / "m.json").exists()


def test_an_archive_with_a_path_trick_is_refused(tmp_path):
    z = tmp_path / "bad.zip"
    with zipfile.ZipFile(z, "w") as f:
        f.writestr("../evil.txt", "x")
    with pytest.raises(SystemExit):
        vc.ingest(z, tmp_path / "w", tmp_path / "m.json", tmp_path / "s.md", tmp_path / "a")


def test_measured_durations_replace_the_estimates_in_the_timing():
    est = a1.dt.speaker_table  # noqa: F841  (module loaded)
    plan = a1.build_plan(a1.dt.load_inputs()[1])
    meas = {"S1-L1": {"mr": 20.0, "hi": 18.0}}
    p2, n = a1.with_measured(plan, meas)
    assert n == 1 and next(l for l in p2["lines"] if l["id"] == "S1-L1")["seconds"] == {"mr": 20.0, "hi": 18.0} and next(l for l in plan["lines"] if l["id"] == "S1-L1")["seconds"]["mr"] < 20


def test_packaging_writes_the_job_the_dataset_and_a_gpu_internet_kernel(tmp_path):
    info = vc.package(ROOT / "canon" / "audio" / "A1_audio_plan.json", tmp_path)
    meta = json.loads((tmp_path / "kernel_a1_tts" / "kernel-metadata.json").read_text(encoding="utf-8"))
    assert info["jobs"] == 2 * len(PLAN["lines"]) and meta["enable_gpu"] is True and meta["enable_internet"] is True and meta["is_private"] is True
    assert meta["dataset_sources"] == ["satviksangamkar54321/granthstudio-a1-tts-input"] and (tmp_path / "kernel_a1_tts" / "a1_tts_run.py").exists()
    assert "HF_TOKEN" not in json.dumps(meta) and (tmp_path / "a1_tts_dataset" / "A1_tts_input.json").exists()


def test_the_full_audio_mix_places_each_line_at_its_beat_in_both_languages_in_sync(tmp_path):
    rate = 44100
    timing = {"planned_picture_s": 18, "scenes": [
        {"scene": "S1", "planned_shots": 1, "beats": [{"line": "S1-L1", "start_s": 0.5, "voice": "narrator"}]},
        {"scene": "S2", "planned_shots": 2, "beats": [{"line": "S2-L1", "start_s": 0.5, "voice": "narrator"}, {"line": "S2-L2", "start_s": 4.0, "voice": "gajanan"}]}]}
    for lang, secs in (("mr", {"S1-L1": 2.0, "S2-L1": 3.0, "S2-L2": 5.0}), ("hi", {"S1-L1": 1.5, "S2-L1": 2.5, "S2-L2": 4.5})):
        for lid, s in secs.items():
            with wave.open(str(tmp_path / "wav" / lang / f"{lid}.{lang}.wav") if (tmp_path / "wav" / lang).mkdir(parents=True, exist_ok=True) is None else "", "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(rate)
                w.writeframes((b"\x10\x10") * int(rate * s))
    out = {}
    for lang in ("mr", "hi"):
        out[lang] = vc.mix(lang, timing, tmp_path, tmp_path / f"{lang}.wav")
        assert out[lang]["seconds"] == 18 and out[lang]["lines_placed"] == 3
    with wave.open(str(tmp_path / "mr.wav"), "rb") as a, wave.open(str(tmp_path / "hi.wav"), "rb") as b:
        assert a.getnframes() == b.getnframes() == 18 * rate                              # both tracks are exactly the picture length
    assert [i["at_s"] for i in out["mr"]["index"]] == [i["at_s"] for i in out["hi"]["index"]] == [0.5, 6.5, 10.0]      # S2 starts after S1's one 6-second shot


def test_a_clip_that_would_overlap_another_is_refused(tmp_path):
    rate = 44100
    timing = {"planned_picture_s": 12, "scenes": [{"scene": "S1", "planned_shots": 2, "beats": [{"line": "A", "start_s": 0.0, "voice": "n"}, {"line": "B", "start_s": 1.0, "voice": "n"}]}]}
    (tmp_path / "wav" / "mr").mkdir(parents=True)
    for lid in ("A", "B"):
        with wave.open(str(tmp_path / "wav" / "mr" / f"{lid}.mr.wav"), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(rate)
            w.writeframes(b"\x10\x10" * rate * 3)
    with pytest.raises(SystemExit):
        vc.mix("mr", timing, tmp_path, tmp_path / "o.wav")


def test_a_clip_that_would_run_past_its_scene_is_refused_not_truncated(tmp_path):
    rate = 44100
    timing = {"planned_picture_s": 12, "scenes": [{"scene": "S1", "planned_shots": 1, "beats": [{"line": "A", "start_s": 5.5, "voice": "n"}]}, {"scene": "S2", "planned_shots": 1, "beats": []}]}
    (tmp_path / "wav" / "mr").mkdir(parents=True)
    with wave.open(str(tmp_path / "wav" / "mr" / "A.mr.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"\x10\x10" * rate)
    with pytest.raises(SystemExit):
        vc.mix("mr", timing, tmp_path, tmp_path / "o.wav")


def test_without_the_floor_the_planned_shots_follow_the_measured_audio_only():
    import json as _j
    a_spec = importlib.util.spec_from_file_location("a1a2", ROOT / "scripts" / "source" / "a1_audio.py")
    a1 = importlib.util.module_from_spec(a_spec)
    a_spec.loader.exec_module(a1)
    plan = _j.loads((ROOT / "canon" / "audio" / "A1_audio_plan.json").read_text(encoding="utf-8"))
    macro = _j.loads((ROOT / "canon" / "director_runs" / "a1_split_rev8" / "macro_A1.json").read_text(encoding="utf-8"))["macro"]
    with_floor, no_floor = a1.timing(plan, macro), a1.timing(plan, macro, floor=False)
    assert all(s["planned_shots"] == s["audio_needs"] for s in no_floor["scenes"])
    assert all(f["planned_shots"] == max(f["audio_needs"], f["allocation"]) for f in with_floor["scenes"])


def test_balance_brings_quiet_and_loud_clips_to_the_same_speech_level_and_limits_the_gain():
    import numpy as np
    rate = 44100
    t = np.arange(rate) / rate
    quiet = (np.sin(2 * np.pi * 220 * t) * 0.05 * 32768).astype(np.int32)       # about -29 dBFS rms
    loud = (np.sin(2 * np.pi * 220 * t) * 0.35 * 32768).astype(np.int32)        # about -12 dBFS rms
    gq, gl = vc.balance_gain_db(quiet, -22.0), vc.balance_gain_db(loud, -22.0)
    assert gq > 0 > gl
    after_q = 20 * np.log10(0.05 / np.sqrt(2) * 10 ** (gq / 20)) 
    after_l = 20 * np.log10(0.35 / np.sqrt(2) * 10 ** (gl / 20))
    assert abs(after_q - after_l) < 0.6
    assert vc.balance_gain_db(np.zeros(rate, dtype=np.int32), -22.0) == 0.0           # silence is left alone
    faint = (np.sin(2 * np.pi * 220 * t) * 0.03 * 32768).astype(np.int32)              # about -33.5 dBFS rms: needs +11.5 dB, is limited to +10 dB
    assert vc.balance_gain_db(faint, -22.0) == 10.0 and vc.balance_gain_db(quiet * 0 + 40, -22.0) == 0.0      # and a clip below the speech threshold is left alone
