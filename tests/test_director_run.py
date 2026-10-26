"""Synthetic checks for immutable run folders, shot-id mapping, the film manifest with owner approvals, and the Kimi adapter + P4 money cap. No network, no keys."""
import importlib.util
import json
import urllib.error
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "scripts" / "source"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SRC / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


dr, ka = load("director_run"), load("kimi_adapter")
L = ka.ledger_mod


# ----------------------------------------------------------------------------- run folders

def test_run_files_are_write_once_and_listed_with_hashes(tmp_path):
    run = dr.open_run(tmp_path, "r1", {"director": "kimi"})
    assert not run.has("a.json")
    run.write_once("a.json", '{"x": 1}')
    assert run.has("a.json") and run.read_json("a.json") == {"x": 1}
    with pytest.raises(dr.RunError):
        run.write_once("a.json", "{}")
    with pytest.raises(dr.RunError):
        dr.open_run(tmp_path, "r1", {"director": "kimi"})                       # an existing run is never reopened without --resume


def test_resume_verifies_hashes_and_refuses_changed_inputs_or_tampering(tmp_path):
    run = dr.open_run(tmp_path, "r1", {"director": "kimi"})
    run.write_once("a.json", "{}")
    run.release()
    again = dr.open_run(tmp_path, "r1", {"director": "kimi"}, resume=True)
    assert again.has("a.json")
    again.release()
    with pytest.raises(dr.RunError):
        dr.open_run(tmp_path, "r1", {"director": "other"}, resume=True)         # model/prompt/input changed: start a new run
    (tmp_path / "r1" / "a.json").write_text('{"x": 2}')
    with pytest.raises(dr.RunError):
        again.has("a.json")                                                       # changed after the receipt: never silently reused
    (tmp_path / "r1" / "stray.json").write_text("{}")
    with pytest.raises(dr.RunError):
        again.has("stray.json")                                                   # on disk but unlisted
    with pytest.raises(dr.RunError):
        dr.open_run(tmp_path, "nope", {}, resume=True)


def test_run_names_are_safe(tmp_path):
    for bad in ("../x", "a/b", "", "x" * 61):
        with pytest.raises(dr.RunError):
            dr.open_run(tmp_path, bad, {})


def test_one_directing_pass_per_scene_per_director(tmp_path):
    run = dr.open_run(tmp_path, "r1", {"director": "kimi"})
    run.write_once("a01_scene1.json", "{}")
    assert dr.directed_elsewhere(tmp_path, "r2", "kimi", [1, 4]) == ["r1:scene1"]
    assert dr.directed_elsewhere(tmp_path, "r2", "someone-else", [1]) == []
    assert dr.directed_elsewhere(tmp_path, "r1", "kimi", [1]) == []              # the run itself is resumed, not "elsewhere"


# ----------------------------------------------------------------------------- shot-id mapping

def test_shot_ids_map_deterministically_to_single_letters_in_batches_of_26():
    ids = [f"S{s}-{k}" for s in range(1, 8) for k in range(1, 6)]               # 35 shots
    m = dr.map_shot_ids(ids)
    assert m["S1-1"] == {"batch": 0, "schema_id": "SA"} and m["S1-2"]["schema_id"] == "SB"
    assert m == dr.map_shot_ids(list(reversed(ids)))                              # independent of input order
    assert len({(v["batch"], v["schema_id"]) for v in m.values()}) == 35
    assert max(v["batch"] for v in m.values()) == 1 and all(len(v["schema_id"]) == 2 for v in m.values())
    with pytest.raises(ValueError):
        dr.map_shot_ids(["S1-1", "S1-1"])
    with pytest.raises(ValueError):
        dr.map_shot_ids(["shot1"])


# ----------------------------------------------------------------------------- film manifest

def manifest():
    m = dr.new_manifest("a1-a2")
    dr.set_item(m, "source:A1:ovis", "h-ovis")
    dr.set_item(m, "canon:A1:final_answers", "h-ans")
    dr.set_item(m, "plan:S1", "h-plan")
    dr.set_item(m, "asset:maharaj_wide", "h-img")
    dr.add_dep(m, "plan:S1", ["source:A1:ovis", "canon:A1:final_answers"])
    return m


def test_approvals_are_separate_records_per_kind():
    m = manifest()
    dr.approve(m, "source", "A1", ["source:A1:ovis"], "owner")
    assert dr.approval_state(m, "source", "A1") == "APPROVED"
    assert dr.approval_state(m, "storyboard", "S1") == "NONE" and dr.approval_state(m, "images", "S1") == "NONE"


def test_changing_an_input_or_a_dependency_makes_the_approval_stale():
    m = manifest()
    dr.approve(m, "storyboard", "S1", ["plan:S1"], "owner")
    assert dr.approval_state(m, "storyboard", "S1") == "APPROVED"
    dr.set_item(m, "canon:A1:final_answers", "h-ans-v2")                           # an upstream research file changed
    assert dr.approval_state(m, "storyboard", "S1") == "STALE"
    dr.set_item(m, "canon:A1:final_answers", "h-ans")                              # restored: the approval is valid again
    assert dr.approval_state(m, "storyboard", "S1") == "APPROVED"
    dr.set_item(m, "plan:S1", "h-plan-v2")
    assert dr.approval_state(m, "storyboard", "S1") == "STALE"
    del m["items"]["plan:S1"]
    assert dr.approval_state(m, "storyboard", "S1") == "STALE"


def test_approval_needs_a_known_kind_known_items_and_a_named_approver():
    m = manifest()
    for args in (("vibes", "S1", ["plan:S1"], "owner"), ("source", "A1", ["nope"], "owner"), ("source", "A1", ["plan:S1"], " ")):
        with pytest.raises(ValueError):
            dr.approve(m, *args)


# ----------------------------------------------------------------------------- P4 money cap and reconcile

def test_p4_caps_kimi_director_testing_at_one_dollar(tmp_path):
    assert L.PHASE_CAPS["P4"] == 1.0
    led = L.Ledger(tmp_path / "l.jsonl")
    led.reserve("P4", "kimi-k3.1-pro", 1000, 32000)                               # about $0.32
    led.reserve("P4", "kimi-k3.1-pro", 1000, 32000)
    led.reserve("P4", "kimi-k3.1-pro", 1000, 32000)
    with pytest.raises(L.Refused):
        led.reserve("P4", "kimi-k3.1-pro", 1000, 32000)                           # the fourth would pass $1


def test_reconcile_settles_only_open_or_unknown_reservations(tmp_path):
    led = L.Ledger(tmp_path / "l.jsonl")
    rid = led.reserve("P4", "kimi-k3.1-pro", 1000, 1000)
    assert led.unreconciled() == [rid]
    led.reconcile(rid, 0.01, "dashboard")
    assert led.unreconciled() == [] and led.committed("P4") == pytest.approx(0.01)
    with pytest.raises(L.Refused):
        led.reconcile(rid, 0.01, "again")


# ----------------------------------------------------------------------------- Kimi adapter (fake transport)

KEY = "k" * 32


def agent(tmp_path, post, **kw):
    led = L.Ledger(tmp_path / "l.jsonl")
    return led, ka.make_agent(ledger=led, key=KEY, post=post, **kw)


def ok_post(path, body, key, timeout):
    if path.endswith("estimate-token-count"):
        return {"data": {"total_tokens": 1000}}
    return {"choices": [{"message": {"content": "hello " + key}, "finish_reason": "stop"}], "usage": {"prompt_tokens": 900, "completion_tokens": 100}}


def test_adapter_reserves_before_dispatch_settles_and_scrubs_the_key(tmp_path):
    seen = {}

    def post(path, body, key, timeout):
        if "chat" in path:
            seen["reserved_before"] = len(led._state())                         # the reservation is already on disk when the call goes out
        return ok_post(path, body, key, timeout)
    led, a = agent(tmp_path, post)
    reply, info = a.call("sys", "user")
    assert seen["reserved_before"] == 1 and KEY not in reply and reply == "hello ***"
    assert info["provider"] == "moonshot" and info["status"] == 200 and info["usage"] == {"prompt_tokens": 900, "completion_tokens": 100}
    assert info["cost_usd"] == pytest.approx(900 * 2 / 1e6 + 100 * 10 / 1e6) and led.unreconciled() == [] and led.committed("P4") == pytest.approx(info["cost_usd"])


def test_adapter_error_is_unknown_at_full_reservation_and_stops_the_next_call(tmp_path):
    def post(path, body, key, timeout):
        if path.endswith("estimate-token-count"):
            return {"data": {"total_tokens": 1000}}
        raise urllib.error.HTTPError("u", 429, "slow down", {}, None)
    led, a = agent(tmp_path, post)
    reply, info = a.call("s", "u")
    assert reply == "" and info["error"] == "HTTP 429" and len(led.unreconciled()) == 1 and led.committed("P4") > 0.3
    with pytest.raises(L.Refused):
        a.call("s", "u")                                                          # no second paid call until the owner reconciles


def test_adapter_refuses_when_counting_fails_or_an_old_reservation_is_open(tmp_path):
    def broken(path, body, key, timeout):
        raise OSError("down")
    led, a = agent(tmp_path, broken)
    with pytest.raises(L.Refused):
        a.call("s", "u")
    assert led.committed() == 0                                                   # nothing was reserved
    led2, a2 = agent(tmp_path / "x", ok_post)
    led2.reserve("P1", "kimi-k3.1-pro", 1000, 1000)                               # an unreconciled reservation from earlier work
    with pytest.raises(L.Refused):
        a2.call("s", "u")


def test_adapter_reply_without_usage_is_unknown(tmp_path):
    def post(path, body, key, timeout):
        return {"data": {"total_tokens": 1000}} if path.endswith("estimate-token-count") else {"choices": [{"message": {"content": "x"}}]}
    led, a = agent(tmp_path, post)
    _, info = a.call("s", "u")
    assert info["error"] == "no usage in reply" and len(led.unreconciled()) == 1


# ----------------------------------------------------------------------------- Codex findings (2026-10-26)

@pytest.mark.parametrize("amount", [float("nan"), float("inf"), -1.0, -0.01, True, "0.1"])
def test_reconcile_rejects_amounts_that_could_disable_the_caps(tmp_path, amount):
    led = L.Ledger(tmp_path / "l.jsonl")
    rid = led.reserve("P4", "kimi-k3.1-pro", 1000, 1000)
    with pytest.raises(L.Refused):
        led.reconcile(rid, amount, "dashboard 2026-10-26")
    with pytest.raises(L.Refused):
        led.reconcile(rid, 0.01, "  ")                                                # a figure needs its source
    assert led.unreconciled() == [rid]


def test_reconcile_first_is_checked_inside_the_reservation_lock(tmp_path):
    led = L.Ledger(tmp_path / "l.jsonl")
    led.reserve("P1", "kimi-k3.1-pro", 1000, 1000)
    led.reserve("P4", "kimi-k3.1-pro", 1000, 1000)                                  # allowed by default
    with pytest.raises(L.Refused):
        led.reserve("P4", "kimi-k3.1-pro", 1000, 1000, require_reconciled=True)


def test_adapter_refuses_redirects_and_allowlists_provider_metadata(tmp_path):
    assert ka._NoRedirect().redirect_request(None, None, 302, "Found", {}, "https://evil.example/") is None

    def post(path, body, key, timeout):
        if path.endswith("estimate-token-count"):
            return {"data": {"total_tokens": 1000}}
        return {"choices": [{"message": {"content": "x " + key}, "finish_reason": key}], "usage": {"prompt_tokens": 9, "completion_tokens": 1}}
    led, a = agent(tmp_path, post)
    reply, info = a.call("s", "u")
    assert info["finish"] == "other" and KEY not in json.dumps(info) and KEY not in reply and a.secrets == (KEY,)


def test_adapter_non_numeric_usage_is_unknown(tmp_path):
    def post(path, body, key, timeout):
        if path.endswith("estimate-token-count"):
            return {"data": {"total_tokens": 1000}}
        return {"choices": [{"message": {"content": "x"}, "finish_reason": "stop"}], "usage": {"prompt_tokens": "9", "completion_tokens": None}}
    led, a = agent(tmp_path, post)
    assert a.call("s", "u")[1]["error"] == "no usage in reply" and len(led.unreconciled()) == 1


def test_probe_is_one_tiny_reserved_call(tmp_path):
    def post(path, body, key, timeout):
        if path.endswith("estimate-token-count"):
            return {"data": {"total_tokens": 30}}
        assert body["max_tokens"] == 200
        return {"choices": [{"message": {"content": '{"ok": true}'}, "finish_reason": "stop"}], "usage": {"prompt_tokens": 30, "completion_tokens": 6}}
    led, a = agent(tmp_path, post)
    r = ka.probe(a)
    assert r["answered_ok_json"] is True and r["cost_usd"] < 0.001 and led.unreconciled() == [] and led.committed("P4") == pytest.approx(r["cost_usd"])


def test_adding_a_dependency_after_approval_makes_it_stale():
    m = manifest()
    dr.approve(m, "storyboard", "S1", ["plan:S1"], "owner")
    dr.set_item(m, "canon:A1:new_rule", "h-new")
    dr.add_dep(m, "plan:S1", ["canon:A1:new_rule"])
    assert dr.approval_state(m, "storyboard", "S1") == "STALE"


def test_film_manifest_is_built_from_a_run_and_persisted(tmp_path):
    m = dr.new_manifest("film")
    plan = {"chapter": 1, "ovi_range": [10, 11], "images_needed": [{"image_id": "road1", "description": "d", "used_in": ["S1-1"]}]}
    dr.update_film_manifest(m, {"adhyay_01_ovis_hj.jsonl": "h1", "frozen_copies/x.md": "h2"}, {1: plan})
    assert set(m["items"]) == {"source:A1:adhyay_01_ovis_hj.jsonl", "canon:A1:frozen_copies/x.md", "plan:S1", "asset:road1"}
    dr.approve(m, "storyboard", "S1", ["plan:S1"], "owner")
    dr.save_manifest(tmp_path / "m.json", m)
    m2 = dr.load_manifest(tmp_path / "m.json", "film")
    assert dr.approval_state(m2, "storyboard", "S1") == "APPROVED"
    dr.update_film_manifest(m2, {"adhyay_01_ovis_hj.jsonl": "CHANGED", "frozen_copies/x.md": "h2"}, {1: plan})         # a research file changed
    assert dr.approval_state(m2, "storyboard", "S1") == "STALE"


def test_run_files_may_live_in_a_subfolder(tmp_path):
    run = dr.open_run(tmp_path, "r1", {})
    run.write_once("calls/a.json", "{}")
    assert run.has("calls/a.json")


# ----------------------------------------------------------------------------- Codex audit v2 findings

@pytest.mark.parametrize("usage", [{"prompt_tokens": -1000000, "completion_tokens": 0}, {"prompt_tokens": 5, "completion_tokens": -1}, {"prompt_tokens": True, "completion_tokens": 3}])
def test_negative_or_boolean_usage_can_never_create_budget(tmp_path, usage):
    def post(path, body, key, timeout):
        if path.endswith("estimate-token-count"):
            return {"data": {"total_tokens": 1000}}
        return {"choices": [{"message": {"content": "x"}, "finish_reason": "stop"}], "usage": usage}
    led, a = agent(tmp_path, post)
    _, info = a.call("s", "u")
    assert info["error"] == "no usage in reply" and len(led.unreconciled()) == 1 and led.committed("P4") > 0
    rid = led.unreconciled()[0]
    with pytest.raises(L.Refused):
        led.settle(rid, usage)                                                    # the ledger refuses it on its own as well


def test_probe_asks_for_json_mode_and_reports_failure_honestly(tmp_path):
    seen = {}

    def post(path, body, key, timeout):
        if path.endswith("estimate-token-count"):
            return {"data": {"total_tokens": 30}}
        seen["fmt"] = body.get("response_format")
        return {"choices": [{"message": {"content": "sorry, not json"}, "finish_reason": "stop"}], "usage": {"prompt_tokens": 30, "completion_tokens": 6}}
    led = L.Ledger(tmp_path / "l.jsonl")
    a = ka.make_agent(ledger=led, key=KEY, post=post, json_mode=True)
    assert ka.probe(a)["answered_ok_json"] is False and seen["fmt"] == {"type": "json_object"}
    led2 = L.Ledger(tmp_path / "l2.jsonl")
    b = ka.make_agent(ledger=led2, key=KEY, post=lambda p, bd, k, t: seen.update(fmt2=bd.get("response_format")) or ({"data": {"total_tokens": 30}} if p.endswith("count") else {"choices": [{"message": {"content": "{}"}, "finish_reason": "stop"}], "usage": {"prompt_tokens": 1, "completion_tokens": 1}}))
    b.call("s", "u")
    assert seen["fmt2"] is None                                                   # scenes never use JSON mode


def test_images_with_conflicting_descriptions_in_two_scenes_are_refused_and_bindings_survive():
    m = dr.new_manifest("film")
    p1 = {"chapter": 1, "ovi_range": [10, 11], "images_needed": [{"image_id": "maharaj_wide", "description": "Maharaj seated", "used_in": ["S1-1"]}]}
    p4 = {"chapter": 1, "ovi_range": [20, 21], "images_needed": [{"image_id": "maharaj_wide", "description": "Maharaj seated", "used_in": ["S4-2"]}]}
    dr.update_film_manifest(m, {"a.jsonl": "h"}, {1: p1})
    m["items"]["asset:maharaj_wide"]["file"] = "D:/images/maharaj_wide.png"          # the owner delivered the picture
    dr.update_film_manifest(m, {"a.jsonl": "h"}, {4: p4})
    it = m["items"]["asset:maharaj_wide"]
    assert it["used_in"] == ["S1-1", "S4-2"] and it["scenes"] == [1, 4] and it["file"] == "D:/images/maharaj_wide.png"
    clash = {"chapter": 1, "ovi_range": [30, 31], "images_needed": [{"image_id": "maharaj_wide", "description": "a DIFFERENT picture", "used_in": ["S5-1"]}]}
    with pytest.raises(ValueError):
        dr.update_film_manifest(m, {"a.jsonl": "h"}, {5: clash})
    again = dict(p1, images_needed=[{"image_id": "maharaj_wide", "description": "Maharaj seated", "used_in": ["S1-1", "S1-2"]}])
    dr.update_film_manifest(m, {"a.jsonl": "h"}, {1: again})                          # a scene may refine its own use
    assert m["items"]["asset:maharaj_wide"]["used_in"] == ["S1-1", "S1-2", "S4-2"]


def test_scene_claim_is_atomic_across_runs_and_continuable_by_its_own_run(tmp_path):
    dr.claim_scene(tmp_path, "kimi-k3.1-pro", 1, "r1")
    dr.claim_scene(tmp_path, "kimi-k3.1-pro", 1, "r1")                              # the same run may continue
    with pytest.raises(dr.RunError):
        dr.claim_scene(tmp_path, "kimi-k3.1-pro", 1, "r2")                          # another run may not buy the same scene
    dr.claim_scene(tmp_path, "someone-else", 1, "r2")                               # another director is separate
    dr.claim_scene(tmp_path, "kimi-k3.1-pro", 1, "r2", redo=True)                   # only the owner's --redo moves it
    with pytest.raises(dr.RunError):
        dr.claim_scene(tmp_path, "kimi-k3.1-pro", 1, "r1")


def test_a_changed_description_drops_the_owner_file_binding_and_asks_for_a_rebind():
    m = dr.new_manifest("film")
    plan = lambda d: {"chapter": 1, "ovi_range": [10, 11], "images_needed": [{"image_id": "maharaj_wide", "description": d, "used_in": ["S1-1"]}]}
    dr.update_film_manifest(m, {"a.jsonl": "h"}, {1: plan("Maharaj seated")})
    m["items"]["asset:maharaj_wide"]["file"] = "D:/images/seated.png"
    dr.update_film_manifest(m, {"a.jsonl": "h"}, {1: plan("Maharaj seated")})
    assert m["items"]["asset:maharaj_wide"]["file"] == "D:/images/seated.png"
    dr.update_film_manifest(m, {"a.jsonl": "h"}, {1: plan("Maharaj STANDING")})
    it = m["items"]["asset:maharaj_wide"]
    assert it["file"] is None and it["rebind_needed"] is True


def test_two_processes_may_never_work_on_one_run(tmp_path):
    first = dr.open_run(tmp_path, "r1", {"x": 1})
    with pytest.raises(dr.RunError):
        dr.open_run(tmp_path, "r1", {"x": 1}, resume=True)                         # same name, same inputs: still refused while the first holds it
    first.release()
    second = dr.open_run(tmp_path, "r1", {"x": 1}, resume=True)
    second.release()


def test_manifest_updates_are_one_locked_transaction(tmp_path):
    path = tmp_path / "film_manifest.json"
    dr.update_manifest(path, "film", lambda m: dr.set_item(m, "plan:S1", "h1"))
    dr.update_manifest(path, "film", lambda m: dr.set_item(m, "plan:S2", "h2"))      # the second update keeps the first one's additions
    assert set(dr.load_manifest(path, "film")["items"]) == {"plan:S1", "plan:S2"}
    with pytest.raises(ValueError):
        dr.update_manifest(path, "film", lambda m: (_ for _ in ()).throw(ValueError("conflict")))
    assert set(dr.load_manifest(path, "film")["items"]) == {"plan:S1", "plan:S2"}    # a failed update changes nothing


def test_the_rebind_flag_stays_until_the_owner_rebinds():
    m = dr.new_manifest("film")
    plan = lambda d: {"chapter": 1, "ovi_range": [10, 11], "images_needed": [{"image_id": "x", "description": d, "used_in": ["S1-1"]}]}
    dr.update_film_manifest(m, {"a.jsonl": "h"}, {1: plan("seated")})
    m["items"]["asset:x"]["file"] = "D:/images/seated.png"
    dr.update_film_manifest(m, {"a.jsonl": "h"}, {1: plan("standing")})
    dr.update_film_manifest(m, {"a.jsonl": "h"}, {1: plan("standing")})              # an unchanged repeat must not clear it
    assert m["items"]["asset:x"]["rebind_needed"] is True and m["items"]["asset:x"]["file"] is None
    m["items"]["asset:x"]["file"] = "D:/images/standing.png"
    m["items"]["asset:x"]["rebind_needed"] = False                                   # the owner's rebinding
    dr.update_film_manifest(m, {"a.jsonl": "h"}, {1: plan("standing")})
    assert m["items"]["asset:x"]["rebind_needed"] is False and m["items"]["asset:x"]["file"] == "D:/images/standing.png"
