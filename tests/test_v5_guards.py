"""Synthetic checks for the V5 money ledger and the Blender script guard. No API, no key, no Blender."""
import importlib.util
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts" / "image_trials"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


L = load("v5_ledger")
N = 1000                                     # provider-counted input tokens (synthetic)
W = L.cost("kimi-k3.1-pro", int(N * 1.10) + 200, 32000)


def test_reservation_is_written_before_and_settled_after(tmp_path):
    led = L.Ledger(tmp_path / "l.jsonl")
    rid = led.reserve("P1", "kimi-k3.1-pro", N, 32000)
    assert led.committed("P1") == pytest.approx(W)
    led.settle(rid, {"prompt_tokens": 1000, "completion_tokens": 5000})
    assert led.committed("P1") == pytest.approx(L.cost("kimi-k3.1-pro", 1000, 5000))


def test_refuses_at_phase_cap(tmp_path):
    led = L.Ledger(tmp_path / "l.jsonl")
    n = int(15.0 // W)
    for _ in range(n):
        led.reserve("P1", "kimi-k3.1-pro", N, 32000)
    with pytest.raises(L.Refused):
        led.reserve("P1", "kimi-k3.1-pro", N, 32000)
    assert led.committed("P1") <= 15.0


def test_refuses_at_total_cap(tmp_path):
    led = L.Ledger(tmp_path / "l.jsonl")
    with pytest.raises(L.Refused):
        for _ in range(100):
            for ph in ("P1", "P2", "P3"):
                led.reserve(ph, "kimi-k3.1-pro", 900_000, 32000)
    assert led.committed() <= L.TOTAL_CAP + 1e-9


def test_unknown_keeps_full_reservation_and_survives_restart(tmp_path):
    p = tmp_path / "l.jsonl"
    led = L.Ledger(p)
    rid = led.reserve("P1", "kimi-k3.1-pro", N, 32000)
    led.unknown(rid, "timeout")
    assert L.Ledger(p).committed("P1") == pytest.approx(W)


def test_refuses_uncounted_and_unknown_phase(tmp_path):
    led = L.Ledger(tmp_path / "l.jsonl")
    with pytest.raises(L.Refused):
        led.reserve("P1", "kimi-k3.1-pro", 0, 100)
    with pytest.raises(L.Refused):
        led.reserve("P4", "kimi-k3.1-pro", N, 100)


def test_lock_blocks_a_second_holder(tmp_path):
    led = L.Ledger(tmp_path / "l.jsonl")
    other = L.Ledger(tmp_path / "l.jsonl")
    with led._locked():
        L.time.sleep(0)
        import threading
        res = {}
        def try_reserve():
            try:
                other.reserve("P1", "kimi-k3.1-pro", N, 32000)
                res["ok"] = True
            except L.Refused:
                res["ok"] = False
        t = threading.Thread(target=try_reserve)
        t.start()
        t.join(0.5)
        assert "ok" not in res                 # still waiting for the lock
    t.join(5)
    assert res.get("ok") is True


B = load("v5_blender")
SAFE = """import bpy, math
img = bpy.data.images.load(ASSET("temple"))
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
bpy.context.scene.collection.objects.link(cam)
cam.location.z = 10 * math.sin(0.3)
"""


def test_guard_accepts_plain_scene_code():
    assert B.check(SAFE) == []


@pytest.mark.parametrize("bad", [
    "import os", "import subprocess", "from pathlib import Path", "open('x')", "exec('1')", "eval('1')", "__import__('os')",
    "bpy.ops.wm.save_as_mainfile(filepath='x.blend')", "bpy.app.handlers.frame_change_pre.append(f)", "bpy.utils.execfile('x')",
    "x = 'C:/Windows'", "x = '..\\secrets'", "x.__class__", "d = o.driver_add('location')", "n.base_path = 'out'", "getattr(bpy, 'ops')",
])
def test_guard_refuses(bad):
    assert B.check(bad) != []


S = load("v5_schema")
GOOD = {"shot_id": "SA", "frames": 144, "paper": "#f1ebe2",
        "riso": {"inks": ["#e4348c", "#eee42b", "#2680b0", "#1e277b"], "dot_px": 6, "misregister_px": 2, "grain": 0.3},
        "segments": [{"start": 1, "end": 72, "layers": [{"asset": "sky", "depth": 9, "x": 0, "y": 0, "scale": 1.1}],
                      "camera": {"start": {"x": 0, "y": 0, "zoom": 1}, "end": {"x": 0, "y": 0, "zoom": 1.08}}},
                     {"start": 73, "end": 144, "layers": [{"asset": "temple", "depth": 5, "x": 0, "y": -0.1, "scale": 0.8, "blend": "normal"}],
                      "camera": {"start": {"x": 0, "y": 0, "zoom": 1}, "end": {"x": 0.05, "y": 0, "zoom": 1.1}, "ease": "ease_in_out"}}]}


def test_schema_accepts_valid_shot():
    assert S.validate(GOOD, {"sky", "temple"}) == []


@pytest.mark.parametrize("mutate", [
    lambda s: s.__setitem__("frames", 100),
    lambda s: s["segments"][1].__setitem__("start", 80),
    lambda s: s["segments"][0]["layers"][0].__setitem__("asset", "ghost"),
    lambda s: s["segments"][0]["layers"][0].__setitem__("code", "import os"),
    lambda s: s["riso"].__setitem__("dot_px", 99),
    lambda s: s.__setitem__("paper", "red; drop"),
])
def test_schema_refuses(mutate):
    import copy
    s = copy.deepcopy(GOOD)
    mutate(s)
    assert S.validate(s, {"sky", "temple"}) != []


@pytest.mark.parametrize("bad", [
    "from random import _os as o", "import random\nrandom._os.system('x')", "bpy.data.path_resolve('texts')", "img.save_render('x')",
    "bpy.ops.render.render(write_still=True)", "t.as_module()", "from bpy import utils", "n = nodes.new('ShaderNodeScript')",
    "x = ''.join(map(chr, [47]))\nbpy.data.libraries.load(x)",
])
def test_guard_refuses_codex_bypasses(bad):
    assert B.check(bad) != []
