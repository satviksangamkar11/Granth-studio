"""ElevenLabs runner checks (no network, no key, no credits): job building, the credit ledger, and a fake API."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_s = importlib.util.spec_from_file_location("a1_eleven", ROOT / "scripts" / "source" / "a1_eleven.py")
el = importlib.util.module_from_spec(_s)
_s.loader.exec_module(el)

PLAN = {"lines": [{"id": "S1-L1", "voice": "narrator", "marathi": "अ ब क ।", "hindi": "अ ब क ।"}, {"id": "S1-L2", "voice": "gajanan", "marathi": "ग", "hindi": "घ"}]}
VMAP = {"mr": {"narrator": "vm1", "gajanan": "vm2"}, "hi": {"narrator": "vh1", "gajanan": "vh2"}}


def test_every_line_becomes_a_marathi_and_a_hindi_job_with_the_planned_text():
    jobs = el.build_jobs(PLAN, ["S1-L1", "S1-L2"], VMAP, "eleven_v4")
    assert [j["id"] for j in jobs] == ["S1-L1.mr", "S1-L1.hi", "S1-L2.mr", "S1-L2.hi"] and jobs[0]["voice_id"] == "vm1" and jobs[1]["voice_id"] == "vh1"
    assert jobs[0]["text"] == "अ ब क." and jobs[0]["credits"] == len(jobs[0]["text"])


def test_an_unknown_line_or_a_missing_voice_is_refused():
    with pytest.raises(SystemExit):
        el.build_jobs(PLAN, ["S9-L9"], VMAP, "m")
    with pytest.raises(SystemExit):
        el.build_jobs(PLAN, ["S1-L2"], {"mr": {"narrator": "x"}, "hi": {}}, "m")


def test_the_test_set_exists_in_the_real_plan_and_is_small():
    plan = json.loads((ROOT / "canon" / "audio" / "A1_audio_plan.json").read_text(encoding="utf-8"))
    ids = {l["id"] for l in plan["lines"]}
    assert set(el.TEST_LINES) <= ids
    vm = {lg: {v: "id" for v in ("narrator", "gajanan", "bankatlal", "damodarpant")} for lg in ("mr", "hi")}
    assert sum(j["credits"] for j in el.build_jobs(plan, el.TEST_LINES, vm, "m")) < el.DEFAULT_CAP


def test_ledger_refuses_past_the_cap_and_while_a_reservation_is_open(tmp_path):
    led = el.Ledger(tmp_path / "l.jsonl", 100)
    led.reserve("a", 60)
    with pytest.raises(SystemExit):
        led.reserve("b", 10)                                     # a is still RESERVED
    led.settle("a", 60, True)
    with pytest.raises(SystemExit):
        led.reserve("b", 50)                                     # 60 + 50 > 100
    led.reserve("b", 40)


def test_run_writes_clips_settles_with_the_reported_cost_and_hides_the_key(tmp_path):
    jobs = el.build_jobs(PLAN, ["S1-L1"], VMAP, "eleven_v4")
    calls = []

    def fake(method, path, key, body=None, timeout=0):
        calls.append((path, body))
        return b"MP3DATA", {"Character-Cost": "5"}

    led = el.Ledger(tmp_path / "l.jsonl", 1000)
    man = el.run(jobs, tmp_path / "out", 1000, "K" * 20, post=fake, ledger=led, probe=lambda p: 2.0)
    assert man["ok"] == 2 and led.committed() == 10 and next((tmp_path / "out" / "mp3" / "mr").glob("S1-L1.mr.*.mp3")).read_bytes() == b"MP3DATA"
    assert calls[0][0].startswith("/v1/text-to-speech/vm1") and calls[0][1]["model_id"] == "eleven_v4"

    def boom(*a, **k):
        raise RuntimeError("HTTP 401: bad key " + "K" * 20)

    man2 = el.run(jobs, tmp_path / "out2", 1000, "K" * 20, post=boom, ledger=el.Ledger(tmp_path / "l2.jsonl", 1000), probe=lambda p: 2.0)
    assert man2["ok"] == 0 and "K" * 20 not in json.dumps(man2) and len(man2["lines"]) == 1      # stops at the first failure


def test_the_simple_script_parses_to_all_62_plan_lines_and_replaces_the_text():
    plan = json.loads((ROOT / "canon" / "audio" / "A1_audio_plan.json").read_text(encoding="utf-8"))
    simple = el.load_simple(ROOT / "docs" / "pilot" / "A1_full_script_simple.md")
    assert {l["id"] for l in plan["lines"]} == set(simple)
    new = el.apply_simple(plan, simple)
    l = next(x for x in new["lines"] if x["id"] == "S2-L4")
    assert l["marathi"].startswith("समर्थ सिद्धयोगी") and "बंडी" in l["hindi"]
    with pytest.raises(SystemExit):
        el.apply_simple(plan, {k: v for k, v in simple.items() if k != "S2-L4"})


def test_a_rerun_reuses_accepted_clips_and_buys_nothing_twice(tmp_path):
    jobs = el.build_jobs(PLAN, ["S1-L1"], VMAP, "eleven_v4")
    calls = []

    def fake(method, path, key, body=None, timeout=0):
        calls.append(path)
        return b"AUDIO" + bytes(len(calls)), {"Character-Cost": "5"}

    led = el.Ledger(tmp_path / "l.jsonl", 1000)
    el.run(jobs, tmp_path / "o", 1000, "K" * 20, post=fake, ledger=led, probe=lambda p: 2.0)
    n = len(calls)
    man = el.run(jobs, tmp_path / "o", 1000, "K" * 20, post=fake, ledger=led, probe=lambda p: 2.0)
    assert len(calls) == n and man["reused"] == 2 and led.committed() == 10
    other = el.build_jobs(PLAN, ["S1-L1"], {"mr": {"narrator": "vNEW"}, "hi": VMAP["hi"]}, "eleven_v4")      # a changed voice is a NEW clip; the accepted one stays
    el.run(other, tmp_path / "o", 1000, "K" * 20, post=fake, ledger=led, probe=lambda p: 2.0)
    assert len(list((tmp_path / "o" / "mp3" / "mr").glob("S1-L1.mr.*.mp3"))) == 2 and len(calls) == n + 1


def test_a_reply_that_is_not_audio_is_not_accepted_and_the_reservation_stays_open(tmp_path):
    jobs = el.build_jobs(PLAN, ["S1-L1"], VMAP, "eleven_v4")

    def bad(path):
        raise RuntimeError("the audio does not decode")

    led = el.Ledger(tmp_path / "l.jsonl", 1000)
    man = el.run(jobs, tmp_path / "o", 1000, "K" * 20, post=lambda *a, **k: (b"not audio", {}), ledger=led, probe=bad)
    assert man["ok"] == 0 and man["lines"][0]["ok"] is False
    with pytest.raises(SystemExit):
        led.reserve("next", 5)                                       # the open reservation blocks further spending until the owner reconciles


def test_an_estimate_is_marked_unconfirmed_when_the_api_reports_no_cost(tmp_path):
    jobs = el.build_jobs(PLAN, ["S1-L1"], VMAP, "eleven_v4")
    led = el.Ledger(tmp_path / "l.jsonl", 1000)
    man = el.run(jobs, tmp_path / "o", 1000, "K" * 20, post=lambda *a, **k: (b"x", {}), ledger=led, probe=lambda p: 2.0)
    assert man["credits_unconfirmed_clips"] == 2 and all(r["credits_confirmed"] is False for r in man["lines"])


def test_measured_needs_every_line_in_both_languages_and_has_the_timing_shape(tmp_path):
    jobs = el.build_jobs(PLAN, ["S1-L1"], VMAP, "eleven_v4")
    man = el.run(jobs, tmp_path / "o", 1000, "K" * 20, post=lambda *a, **k: (b"x", {"Character-Cost": "3"}), ledger=el.Ledger(tmp_path / "l.jsonl", 1000), probe=lambda p: 4.5)
    m = el.measured(man, PLAN, "h" * 64, "eleven_v4")
    assert m["engine"] == "elevenlabs" and m["lines"]["S1-L1"] == {"mr": 4.5, "hi": 4.5} and any("S1-L2" in p for p in m["problems"])
