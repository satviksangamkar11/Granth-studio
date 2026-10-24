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


PNG_MAGIC = bytes([0x89]) + b"PNG" + bytes([13, 10, 26, 10])
PNG = base64.b64encode(PNG_MAGIC + b"0" * 400).decode()
KEY_A, KEY_B = "nvapi-AAAAAAAAAAAAAAAAAAAAAAAA", "nvapi-BBBBBBBBBBBBBBBBBBBBBBBB"


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


def test_the_next_key_is_tried_only_after_an_invalid_key_and_a_rate_limit_stops_the_run():
    t = load()
    calls = []

    def post(url, key, body):
        calls.append(key)
        return (401, "{}") if key == KEY_A else (200, json.dumps({"artifacts": [{"base64": PNG}]}))

    status, response, index = t.call(t.MODELS["flux2-klein-4b"], {"prompt": "p"}, [KEY_A, KEY_B], post)
    assert status == 200 and index == 1 and calls == [KEY_A, KEY_B]
    calls.clear()
    status, response, index = t.call(t.MODELS["flux2-klein-4b"], {"prompt": "p"}, [KEY_A, KEY_B], lambda u, k, b: (calls.append(k), (429, "{}"))[1])
    assert status == 429 and calls == [KEY_A]                                                        # a rate limit never moves to another key


def test_the_scene_prompts_carry_the_frozen_style_and_the_references_exist_and_follow_the_story():
    t = load()
    for scene, spec in t.SCENES.items():
        prompt = t.scene_prompt(scene)
        assert prompt.startswith("1950s vintage Indian devotional book illustration") and "vintage double-line paper border mount" in prompt
        assert all((t.REFS / name).is_file() for name in spec["refs"]) and len(spec["refs"]) <= t.MODELS["flux2-klein-4b"]["max_refs"] + 1
        for name in ("Gajanan", "Devidas", "Bankatlal", "Damodarpant", "Maharaj"):
            assert name not in prompt                                                                # people are named by image number, never by name (names pull learned imagery)
    assert len(t.SCENES[3]["refs"]) == 5 and len(t.SCENES[1]["refs"]) == 2


def test_a_run_writes_images_and_a_receipt_without_any_key_and_reports_failures(tmp_path, monkeypatch):
    t = load()
    monkeypatch.setenv("NVIDIA_API_KEY", KEY_A)
    monkeypatch.delenv("NVIDIA_API_KEYS", raising=False)
    seen = {}

    def post(url, key, body):
        seen.update(url=url, fields=sorted(body))
        return 200, json.dumps({"artifacts": [{"base64": PNG}], "echo": key})

    args = t.argparse.Namespace(model="flux2-klein-4b", seed=1, scenes="1,2", out=str(tmp_path / "o"), dry_run=False)
    assert t.cmd_run(args, post) == 0
    receipt = (tmp_path / "o" / "receipt.json").read_text(encoding="utf-8")
    assert KEY_A not in receipt and "nvapi-" not in receipt and json.loads(receipt)["scenes"][0]["verdict"] == "IMAGE_RETURNED"
    assert (tmp_path / "o" / "scene1_flux2-klein-4b.png").is_file() and seen["fields"] == ["height", "image", "prompt", "seed", "steps", "width"]
    failing = t.argparse.Namespace(model="flux1-kontext-dev", seed=1, scenes="1", out=str(tmp_path / "f"), dry_run=False)
    assert t.cmd_run(failing, lambda u, k, b: (422, json.dumps({"detail": f"bad field, key {k}"}))) == 1
    text = (tmp_path / "f" / "receipt.json").read_text(encoding="utf-8")
    assert "FAILED" in text and KEY_A not in text                                                    # the server's complaint is kept (it names the right fields) with the key scrubbed


def test_a_dry_run_needs_no_key_and_calls_nothing(tmp_path, monkeypatch):
    t = load()
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    monkeypatch.delenv("NVIDIA_API_KEYS", raising=False)
    args = t.argparse.Namespace(model="flux2-klein-4b", seed=1, scenes="1,2,3", out=str(tmp_path), dry_run=True)
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
        assert t.cmd_check_key(None, opener=lambda request: (calls.append(request.get_header("Authorization")), (next(feed), ""))[1]) == code
        assert len(calls) == expected_calls
    assert KEY_A not in capsys.readouterr().out
    raw_png = PNG_MAGIC + b"0" * 200
    assert t.looks_like_an_image_without_a_secret(raw_png, [KEY_A])
    assert not t.looks_like_an_image_without_a_secret(raw_png + KEY_A.encode(), [KEY_A])
    assert not t.looks_like_an_image_without_a_secret(b"not an image" + b"0" * 200, [KEY_A])
    monkeypatch.setenv("NVIDIA_API_KEY", KEY_A)
    smuggled = base64.b64encode(raw_png + KEY_A.encode()).decode()
    args = t.argparse.Namespace(model="flux2-klein-4b", seed=1, scenes="1", out=str(tmp_path / "o"), dry_run=False)
    assert t.cmd_run(args, lambda u, k, b: (200, json.dumps({"artifacts": [{"base64": smuggled}]}))) == 1
    assert not list((tmp_path / "o").glob("*.png"))                                                  # nothing was written
