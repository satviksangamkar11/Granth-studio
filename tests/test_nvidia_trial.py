import base64
import importlib.util
import json
import sys

import pytest

from tests.conftest import REPO


def load():
    spec = importlib.util.spec_from_file_location("nvidia_trial", REPO / "scripts" / "image_trials" / "nvidia_trial.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["nvidia_trial"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(autouse=True)
def isolated_key_folder(tmp_path, monkeypatch):
    """Tests never read the owner's real key folder."""
    empty = tmp_path / "no_keys_here"
    empty.mkdir()
    monkeypatch.setenv("NVIDIA_KEYS_DIR", str(empty))


PNG_MAGIC = bytes([0x89]) + b"PNG" + bytes([13, 10, 26, 10])
PNG = base64.b64encode(PNG_MAGIC + b"0" * 400).decode()
KEY_A, KEY_B, KEY_C = ("nvapi-" + c * 24 for c in "ABC")


class FakeClock:
    def __init__(self):
        self.now = 1000.0
        self.sleeps = []

    def clock(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds


def pool_of(t, keys, clock=None, **kw):
    clock = clock or FakeClock()
    return t.KeyPool(keys, clock=clock.clock, sleep=clock.sleep, **kw), clock


def test_keys_come_only_from_the_environment_in_order_and_are_scrubbed_everywhere():
    t = load()
    assert t.keys_from_env({}) == []
    assert t.keys_from_env({"NVIDIA_API_KEY": KEY_A, "NVIDIA_API_KEYS": f"{KEY_A}, {KEY_B}"}) == [KEY_A, KEY_B]
    scrubbed = t.scrub(f"bad key {KEY_A} and {KEY_B} and nvapi-CCCCCCCCCCCCCC", [KEY_A, KEY_B])
    assert KEY_A not in scrubbed and KEY_B not in scrubbed and "nvapi-" not in scrubbed


def test_all_response_shapes_are_read_and_a_text_only_answer_is_not_an_image():
    t = load()
    raw = base64.b64decode(PNG)
    assert t.extract_image({"artifacts": [{"base64": PNG}]}) == raw
    assert t.extract_image({"image": "data:image/png;base64," + PNG}) == raw
    assert t.extract_image({"images": [PNG]}) == raw and t.extract_image({"data": [{"b64_json": PNG}]}) == raw
    assert t.extract_image({"detail": "validation error"}) is None


def test_the_pool_gives_each_key_at_most_ten_requests_per_minute_and_spreads_load_over_all_keys():
    t = load()
    pool, clock = pool_of(t, [KEY_A, KEY_B, KEY_C])
    first_round = [pool.acquire()[0] for _ in range(3)]
    assert sorted(first_round) == [0, 1, 2]                                                          # one request each before any key gets a second
    used = [pool.acquire()[0] for _ in range(27)]                                                    # 30 requests in total = 10 per key, all inside one window
    assert clock.sleeps == [] and sorted(used + first_round).count(0) == 10 and sorted(used + first_round).count(1) == 10 and sorted(used + first_round).count(2) == 10
    index, _ = pool.acquire()                                                                        # the 31st waits until the oldest request of some key leaves the window
    assert clock.sleeps and 0 < sum(clock.sleeps) <= 60.0 + 0.1 and index in (0, 1, 2)


def test_a_429_cools_that_key_for_a_minute_while_others_keep_working_and_a_rejected_key_is_retired():
    t = load()
    pool, clock = pool_of(t, [KEY_A, KEY_B])
    calls = []

    def post(url, key, body):
        calls.append(key)
        if key == KEY_A:
            return 429, "{}"
        return 200, json.dumps({"artifacts": [{"base64": PNG}]})

    status, _, index = t.call(t.MODELS["flux2-klein-4b"], {"prompt": "p"}, pool, post)
    assert status == 200 and index == 1 and calls == [KEY_A, KEY_B] and clock.sleeps == []          # KEY_A cooled, the request went to KEY_B without waiting
    calls.clear()
    t.call(t.MODELS["flux2-klein-4b"], {"prompt": "p"}, pool, post)
    assert calls == [KEY_B]                                                                          # KEY_A is still cooling: not tried again
    clock.now += 61
    calls.clear()
    t.call(t.MODELS["flux2-klein-4b"], {"prompt": "p"}, pool, post)
    assert KEY_A in calls                                                                            # after a minute it is back in the pool
    dead_pool, _ = pool_of(t, [KEY_A, KEY_B])
    status, _, index = t.call(t.MODELS["flux2-klein-4b"], {"prompt": "p"}, dead_pool, lambda u, k, b: (402, "{}") if k == KEY_A else (200, json.dumps({"artifacts": [{"base64": PNG}]})))
    assert status == 200 and index == 1 and dead_pool.live == 1                                      # an out-of-credit key is retired for the run
    all_dead, _ = pool_of(t, [KEY_A])
    status, text, _ = t.call(t.MODELS["flux2-klein-4b"], {"prompt": "p"}, all_dead, lambda u, k, b: (401, "{}"))
    assert status == 401 and "rejected" in text


def test_the_scene_prompts_fit_the_endpoint_limit_keep_the_style_in_short_form_and_name_nobody(tmp_path):
    t = load()
    for scene, spec in t.SCENES.items():
        prompt = t.scene_prompt(scene)
        assert len(prompt) <= 800 and prompt.startswith("1950s") and "gouache" in prompt and "sepia" in prompt
        assert all((t.REFS / name).is_file() for name in spec["refs"]) and len(spec["refs"]) <= t.MODELS["flux2-klein-4b"]["max_refs"] + 1
        for name in ("Gajanan", "Devidas", "Bankatlal", "Damodarpant", "Maharaj"):
            assert name not in prompt                                                                # people are named by image number, never by name (names pull learned imagery)
    assert len(t.SCENES[3]["refs"]) == 5 and len(t.SCENES[1]["refs"]) == 2
    long_limit = t.scene_prompt(1, limit=5000)
    assert long_limit.startswith("1950s vintage Indian devotional book illustration") and "vintage double-line paper border mount" in long_limit    # with room, the full frozen text is used
    with pytest.raises(SystemExit):
        t.scene_prompt(3, limit=100)


def test_the_highest_quality_settings_of_each_model_are_sent_and_recorded():
    t = load()
    body = t.MODELS["flux1-kontext-dev"]["builder"]("p", [t.REFS / "maharaj.jpg"], 1, (1024, 1024))
    assert body["steps"] == 50 and body["cfg_scale"] == 3.5
    body = t.MODELS["flux2-klein-4b"]["builder"]("p", [t.REFS / "maharaj.jpg"], 1, (1152, 768))
    assert body["steps"] == 4 and (body["width"], body["height"]) == (1152, 768)


def test_a_run_uses_variants_in_parallel_writes_images_and_a_receipt_without_any_key_and_reports_failures(tmp_path, monkeypatch):
    t = load()
    monkeypatch.setenv("NVIDIA_API_KEYS", f"{KEY_A},{KEY_B}")
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    seen = {"fields": None, "keys": set()}

    def post(url, key, body):
        seen["fields"] = sorted(body)
        seen["keys"].add(key)
        return 200, json.dumps({"artifacts": [{"base64": PNG}], "echo": key})

    args = t.argparse.Namespace(model="flux2-klein-4b", seed=1, scenes="1,2", variants=2, out=str(tmp_path / "o"), dry_run=False)
    assert t.cmd_run(args, post) == 0
    receipt = (tmp_path / "o" / "receipt.json").read_text(encoding="utf-8")
    parsed = json.loads(receipt)
    assert KEY_A not in receipt and KEY_B not in receipt and "nvapi-" not in receipt and len(parsed["scenes"]) == 4 and parsed["quality_settings"]["steps"] == 4
    assert {i["verdict"] for i in parsed["scenes"]} == {"IMAGE_RETURNED"} and len({i["seed"] for i in parsed["scenes"]}) == 4
    assert (tmp_path / "o" / "scene1_v0_flux2-klein-4b.png").is_file() and (tmp_path / "o" / "scene2_v1_flux2-klein-4b.png").is_file()
    assert seen["fields"] == ["height", "image", "prompt", "seed", "steps", "width"] and len(seen["keys"]) == 2          # both keys were used
    failing = t.argparse.Namespace(model="flux1-kontext-dev", seed=1, scenes="1", variants=1, out=str(tmp_path / "f"), dry_run=False)
    assert t.cmd_run(failing, lambda u, k, b: (422, json.dumps({"detail": f"bad field, key {k}"}))) == 1
    text = (tmp_path / "f" / "receipt.json").read_text(encoding="utf-8")
    assert "FAILED" in text and KEY_A not in text                                                    # the server's complaint is kept (it names the right fields) with the key scrubbed


def test_a_dry_run_needs_no_key_and_calls_nothing(tmp_path, monkeypatch):
    t = load()
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    monkeypatch.delenv("NVIDIA_API_KEYS", raising=False)
    args = t.argparse.Namespace(model="flux2-klein-4b", seed=1, scenes="1,2,3", variants=1, out=str(tmp_path), dry_run=True)
    assert t.cmd_run(args, lambda *a: pytest.fail("no request may be sent")) == 0
    scenes = json.loads((tmp_path / "receipt.json").read_text(encoding="utf-8"))["scenes"]
    assert [s["status"] for s in scenes] == ["DRY_RUN"] * 3 and len(scenes[2]["references"]) == 4      # klein takes at most 4 references: the 5th (location) is dropped and recorded


def test_malformed_keys_are_dropped_redirects_are_refused_and_transport_errors_never_carry_a_key(monkeypatch):
    t = load()
    assert t.keys_from_env({"NVIDIA_API_KEY": KEY_A + chr(10) + "X-Evil: 1"}) == []                   # an embedded newline: the whole value is dropped, never sent, never echoed
    assert t.keys_from_env({"NVIDIA_API_KEYS": f"{KEY_A},short,nvapi-bad key with spaces"}) == [KEY_A]
    assert t._NoRedirect().redirect_request(None, None, 302, "Found", {}, "https://evil.example/") is None
    status, text = t._send(t.urllib.request.Request("https://evil.example/x", headers={"Authorization": f"Bearer {KEY_A}"}), 5)
    assert status == 0 and KEY_A not in text and "outside the approved" in text                       # a URL outside the NVIDIA hosts is never contacted

    def boom(*args, **kwargs):
        raise ValueError(f"Invalid header value {KEY_A}")

    monkeypatch.setattr(t._OPENER, "open", boom)
    status, text = t._send(t.urllib.request.Request("https://ai.api.nvidia.com/v1/genai/x", headers={"Authorization": f"Bearer {KEY_A}"}), 5)
    assert status == 0 and text == "request failed: ValueError" and KEY_A not in text

    def bad_status(*args, **kwargs):
        raise t.http.client.BadStatusLine(f"HTTP/1.1 {KEY_A}")                                        # a malformed status line from the server

    monkeypatch.setattr(t._OPENER, "open", bad_status)
    status, text = t._send(t.urllib.request.Request("https://ai.api.nvidia.com/v1/genai/x", headers={"Authorization": f"Bearer {KEY_A}"}), 5)
    assert status == 0 and text == "request failed: BadStatusLine" and KEY_A not in text


def test_argparse_never_echoes_a_pasted_key(capsys):
    t = load()
    with pytest.raises(SystemExit):
        t.main(["check-key", "--key", KEY_A])
    captured = capsys.readouterr()
    assert KEY_A not in captured.out + captured.err and "nvapi-" not in captured.out + captured.err and "error" in captured.err


def test_check_key_stops_after_a_good_key_or_a_non_auth_status_and_a_response_cannot_smuggle_a_key_into_a_file(tmp_path, monkeypatch, capsys):
    t = load()
    monkeypatch.setenv("NVIDIA_API_KEYS", f"{KEY_A},{KEY_B}")
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    calls = []
    for answers, expected_calls, code in (((200,), 1, 0), ((401, 200), 2, 0), ((429,), 1, 1), ((500,), 1, 1), ((401, 403), 2, 1)):
        calls.clear()
        feed = iter(answers)
        assert t.cmd_check_key(t.argparse.Namespace(all=False), opener=lambda request: (calls.append(request.get_header("Authorization")), (next(feed), ""))[1]) == code
        assert len(calls) == expected_calls
    assert KEY_A not in capsys.readouterr().out
    raw_png = PNG_MAGIC + b"0" * 200
    assert t.looks_like_an_image_without_a_secret(raw_png, [KEY_A])
    assert not t.looks_like_an_image_without_a_secret(raw_png + KEY_A.encode(), [KEY_A])
    assert not t.looks_like_an_image_without_a_secret(b"not an image" + b"0" * 200, [KEY_A])
    monkeypatch.setenv("NVIDIA_API_KEY", KEY_A)
    smuggled = base64.b64encode(raw_png + KEY_A.encode()).decode()
    args = t.argparse.Namespace(model="flux2-klein-4b", seed=1, scenes="1", variants=1, out=str(tmp_path / "o"), dry_run=False)
    assert t.cmd_run(args, lambda u, k, b: (200, json.dumps({"artifacts": [{"base64": smuggled}]}))) == 1
    assert not list((tmp_path / "o").glob("*.png"))                                                  # nothing was written


def test_keys_are_read_from_the_key_folder_after_the_environment_skipping_empty_and_malformed_files(tmp_path, monkeypatch, capsys):
    t = load()
    folder = tmp_path / "keys"
    folder.mkdir()
    (folder / "nvidia_api_key.txt").write_text("", encoding="utf-8")                                   # empty: skipped
    (folder / "nvidia_api_key_2.txt").write_text(KEY_A + chr(10), encoding="utf-8")
    (folder / "nvidia_api_key_10.txt").write_text(KEY_B, encoding="utf-8")
    (folder / "nvidia_api_key_3.txt").write_text("not a key at all", encoding="utf-8")                 # malformed: skipped, never echoed
    (folder / "other.txt").write_text(KEY_A, encoding="utf-8")                                         # wrong name: ignored
    assert t.keys_from_folder(folder) == [KEY_A, KEY_B]                                                # _2 before _10: natural order by name length, then name
    monkeypatch.setenv("NVIDIA_KEYS_DIR", str(folder))
    monkeypatch.setenv("NVIDIA_API_KEY", KEY_B)
    assert t.load_keys() == [KEY_B, KEY_A]                                                             # environment first, folder after, no duplicates
    assert t.keys_from_folder(tmp_path / "missing") == []
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    answers = iter([200, 200])
    assert t.cmd_check_key(t.argparse.Namespace(all=True), opener=lambda request: (next(answers), "")) == 0
    out = capsys.readouterr().out
    assert "2 well-formed key(s) loaded" in out and KEY_A not in out and KEY_B not in out and "not a key" not in out
