import importlib.util
from pathlib import Path
from types import SimpleNamespace

spec = importlib.util.spec_from_file_location("draft_source", Path(__file__).resolve().parents[1] / "scripts" / "source" / "draft_source.py")
ds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ds)

OVIS = [{"ovi": 1, "text": "alpha  beta gamma"}, {"ovi": 2, "text": "delta epsilon"}]
FAKE_KEY = "nvapi-" + "x" * 30


def test_extract_json_takes_first_value_of_the_wanted_type():
    assert ds.extract_json('<think>[1]</think>Here:\n```json\n[{"ovi": 1}]\n```', list) == [{"ovi": 1}]
    assert ds.extract_json('ok {"characters": []} done', dict) == {"characters": []}
    assert ds.extract_json('[{"ovi": 1}] see note [x]', list) == [{"ovi": 1}]


def test_escaped_key_is_scrubbed_after_parsing():
    escaped = "\\u006e" + FAKE_KEY[1:]
    parsed = ds.extract_json('[{"ovi": 1, "meaning_en": "' + escaped + '"}]', list)
    assert FAKE_KEY not in str(ds.scrub_obj(parsed, [FAKE_KEY]))


def test_clean_row_drops_model_fields_and_empty_meanings():
    row = ds.clean_row({"ovi": 3, "meaning_en": " text ", "approved": True, "status": "APPROVED"})
    assert row == {"ovi": 3, "meaning_en": "text", "speaker": None, "unclear": False, "note": ""}
    assert ds.clean_row({"ovi": 3, "meaning_en": ""}) is None


def test_check_names_flags_unsupported_out_of_range_and_malformed():
    good = {"char_id": "char_a", "names_in_text": ["beta gamma"], "evidence_ovis": [1]}
    wrong_ovi = {"char_id": "char_b", "names_in_text": ["delta"], "evidence_ovis": [1]}
    invented = {"place_id": "loc_c", "names_in_text": ["zeta"], "evidence_ovis": [2, 9]}
    empty = {"char_id": "char_d", "names_in_text": [""], "evidence_ovis": ["1"]}
    problems = ds.check_names([good, wrong_ovi, invented, empty, "junk"], OVIS)
    assert not any("char_a" in p for p in problems)
    assert any("char_b" in p and "delta" in p for p in problems)
    assert any("loc_c" in p and "out of range [9]" in p for p in problems)
    assert any("loc_c" in p and "zeta" in p for p in problems)
    assert any("char_d" in p and "names_in_text" in p for p in problems)
    assert any("malformed" in p for p in problems)


def test_check_names_survives_non_integer_citations():
    assert any("char_e" in p for p in ds.check_names([{"char_id": "char_e", "names_in_text": ["delta"], "evidence_ovis": [{}, 2]}], OVIS))


def test_clean_chars_allowlists_and_rejects_garbage():
    out = ds.clean_chars({"characters": [{"char_id": "char_a", "approved": True, "status": "APPROVED"}], "places": []})
    assert "approved" not in out["characters"][0] and "status" not in out["characters"][0]
    for bad in ({"characters": "garbage", "places": 17}, {"characters": [], "places": []}, {"characters": [1], "places": []}):
        try:
            ds.clean_chars(bad)
            assert False, bad
        except ValueError:
            pass


def test_clean_problems_distinguishes_no_problems_from_no_check():
    assert ds.clean_problems([]) == []
    assert ds.clean_problems(["unable to check"]) == "NO_CHECK"
    assert ds.clean_problems(None) == "NO_CHECK"
    assert ds.clean_problems([{"id": "char_a", "problem": "role not stated", "ovis": [3, "x"]}]) == [{"id": "char_a", "problem": "role not stated", "ovis": [3]}]


def test_load_done_resumes_checked_rows_from_any_model_pair(tmp_path):
    a = SimpleNamespace(drafter="m1", checker="m2")
    good = {"ovi": 1, "meaning_en": "x", "status": "DRAFT", "drafter": "m1", "checker": "m2", "check": "OK", "check_note": ""}
    lines = [good, {**good, "ovi": 2, "checker": "other"}, {**good, "ovi": 2, "check": "NO_CHECK"}, {"ovi": 2, "meaning_en": None, "status": "DRAFT_FAILED"}, {**good, "ovi": 2, "drafter": "same", "checker": "same"}]
    assert ds.load_done  # rows of a different pair are accepted and keep their own models
    p = tmp_path / "p.jsonl"
    p.write_text("\n".join([__import__("json").dumps(x) for x in lines] + ["not json"]), encoding="utf-8")
    done = ds.load_done(p, a, OVIS)
    assert list(done) == [1, 2] and done[2]["checker"] == "other" and done[2]["check"] == "OK"


def test_review_never_shows_ok_for_a_failed_row():
    a = SimpleNamespace(adhyay=1, drafter="m1", checker="m2")
    text = ds.review_text(a, OVIS, [{"ovi": 1, "meaning_en": None, "status": "DRAFT_FAILED", "check": "NOT_CHECKED"}], None)
    line = [l for l in text.splitlines() if l.startswith("| 1 |")][0]
    assert "DRAFT_FAILED" in line and "OK" not in line


class _FakeResp:
    status = 200

    def __init__(self, lines):
        self.lines = lines

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def __iter__(self):
        return iter(self.lines)


def test_stream_once_assembles_content_and_ignores_reasoning_and_junk(monkeypatch):
    lines = [b'data: {"choices":[{"delta":{"reasoning_content":"thinking"}}]}\n', b'data: not json\n', b'data: {"choices":[{"delta":{"content":"[{\\"a\\""}}]}\n',
             b'data: {"choices":[{"delta":{"content":": 1}]"},"finish_reason":"stop"}],"usage":{"total_tokens":5,"x":"y"}}\n', b'data: [DONE]\n']
    monkeypatch.setattr(ds.nt._OPENER, "open", lambda req, timeout=None: _FakeResp2(list(lines)))
    status, content, extra = ds._stream_once("k", {})
    assert status == 200 and content == '[{"a": 1}]' and extra == {"finish": "stop", "usage": {"total_tokens": 5}}


def test_stream_once_transport_error_has_no_secret(monkeypatch):
    def boom(req, timeout=None):
        raise OSError("key nvapi-secret in message")
    monkeypatch.setattr(ds.nt._OPENER, "open", boom)
    assert ds._stream_once("k", {}) == (0, "", {"error": "OSError"})




class _FakeResp2(_FakeResp):
    def read1(self, n=-1):
        return self.lines.pop(0) if self.lines else b""


def _run(monkeypatch, lines):
    monkeypatch.setattr(ds.nt._OPENER, "open", lambda req, timeout=None: _FakeResp2(list(lines)))
    return ds._stream_once("k", {})


OK_LINE = b'data: {"choices":[{"delta":{"content":"x"},"finish_reason":"stop"}]}\n'


def test_stream_rejects_length_eof_blank_and_bad_choices(monkeypatch):
    assert _run(monkeypatch, [OK_LINE])[:2] == (200, "x")
    assert _run(monkeypatch, [b'data: {"choices":[{"delta":{"content":"x"},"finish_reason":"length"}]}\n'])[0] == 0
    assert _run(monkeypatch, [b'data: {"choices":[{"delta":{"content":"x"}}]}\n'])[0] == 0          # EOF without a finish_reason
    assert _run(monkeypatch, [b'data: {"choices":[{"delta":{"content":"  "},"finish_reason":"stop"}]}\n'])[0] == 0
    assert _run(monkeypatch, [b'data: {"choices":1}\n', OK_LINE])[:2] == (200, "x")


def test_stream_metadata_is_allowlisted(monkeypatch):
    line = b'data: {"choices":[{"delta":{"content":"x"},"finish_reason":"stop"}],"usage":{"total_tokens":3,"nvapi-abc":4}}\n'
    assert _run(monkeypatch, [line])[2] == {"finish": "stop", "usage": {"total_tokens": 3}}


def test_stream_line_assembled_from_bounded_reads(monkeypatch):
    assert _run(monkeypatch, [OK_LINE[:20], OK_LINE[20:]])[:2] == (200, "x")


def test_stream_deadline_applies_to_a_newline_free_trickle(monkeypatch):
    monkeypatch.setattr(ds, "STREAM_TOTAL_S", -1)
    assert _run(monkeypatch, [b"data: {", b"x" * 10])[:3] == (0, "", {"error": "deadline"})
