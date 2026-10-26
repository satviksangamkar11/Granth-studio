"""The hybrid puppet harness on synthetic data: strict rig validation, parent/child stacking, white garments surviving the cut, inventory warnings. No API, no key, no network."""
import importlib.util
import json
from pathlib import Path

import pytest
from PIL import Image, ImageDraw

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts" / "image_trials"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rig_mod = load("hybrid_rig")
parts_mod = load("hybrid_puppet_parts")
SIZES = {"part1": (100, 100), "part2": (50, 200)}


def good():
    return {"layers": [{"id": "torso", "part": "part1", "x": 100, "y": 100, "scale": 1, "pivot": [50, 50], "parent": None, "z": 1},
                       {"id": "arm", "part": "part2", "x": 150, "y": 120, "scale": 1, "pivot": [25, 10], "parent": "torso", "z": 2, "evil": "<script>"}],
            "animation": {"duration": 2, "tracks": [{"layer": "arm", "keys": [[0, 0], [1, -80], [2, 0]]}], "extra": 1}}


def test_validate_normalises_and_drops_unknown_fields():
    rig = rig_mod.validate(good(), set(SIZES), SIZES)
    assert "evil" not in rig["layers"][1] and "extra" not in rig["animation"]


@pytest.mark.parametrize("mutate,why", [
    (lambda r: r["layers"][1].__setitem__("part", "part1"), "a part is used twice"),
    (lambda r: r["layers"][1].__setitem__("part", "../etc"), "unknown part"),
    (lambda r: r["layers"][1].__setitem__("id", "Bad Id"), "bad layer id"),
    (lambda r: r["layers"][1].__setitem__("parent", "ghost"), "unknown parent"),
    (lambda r: r["layers"][0].__setitem__("parent", "arm"), "parent cycle"),
    (lambda r: r["layers"][1].__setitem__("scale", float("nan")), "finite"),
    (lambda r: r["layers"][1].__setitem__("x", 99999), "x must"),
    (lambda r: r["animation"].__setitem__("tracks", []), "tracks"),
    (lambda r: r["animation"]["tracks"][0]["keys"].__setitem__(1, [1, -500]), "angle"),
    (lambda r: r["animation"]["tracks"].append({"layer": "arm", "keys": [[0, 0]]}), "repeated"),
    (lambda r: r["animation"]["tracks"][0].__setitem__("keys", [[0, 0], [1, 5], [2, 0]]), "no visible motion"),
])
def test_validate_refuses_bad_rigs(mutate, why):
    rig = good()
    mutate(rig)
    with pytest.raises(ValueError):
        rig_mod.validate(rig, set(SIZES), SIZES)


def test_child_with_lower_z_is_drawn_behind_its_parent_image():
    rig = rig_mod.validate(good(), set(SIZES), SIZES)
    rig["layers"][1]["z"] = 0                                        # arm behind the torso
    svg = rig_mod.build_svg(rig, {"part1": "data:a", "part2": "data:b"}, SIZES, 0.0)
    assert svg.index('href="data:b"') < svg.index('href="data:a"')
    rig["layers"][1]["z"] = 5
    svg = rig_mod.build_svg(rig, {"part1": "data:a", "part2": "data:b"}, SIZES, 0.0)
    assert svg.index('href="data:a"') < svg.index('href="data:b"')


def test_rotation_happens_about_the_pivot_in_canvas_units_and_children_move_with_the_parent():
    rig = rig_mod.validate(good(), set(SIZES), SIZES)
    svg = rig_mod.build_svg(rig, {"part1": "data:a", "part2": "data:b"}, SIZES, 1.0)
    assert "rotate(-80.000 175.00 130.00)" in svg                     # arm pivot: x 150 + 25, y 120 + 10
    assert svg.count("<g transform") == 2 and svg.index("rotate(0.000 150.00 150.00)") < svg.index("rotate(-80")


def test_cut_keeps_an_enclosed_white_garment_and_separates_parts(tmp_path):
    sheet = Image.new("RGB", (900, 500), "white")
    d = ImageDraw.Draw(sheet)
    d.rectangle([40, 40, 240, 200], fill=(180, 110, 60), outline="black", width=4)         # a coloured part
    d.rectangle([330, 40, 560, 200], fill="white", outline="black", width=5)               # a WHITE garment enclosed by its outline
    d.ellipse([650, 60, 850, 260], fill=(60, 40, 30))                                      # a dark part
    for i, (x0, y0) in enumerate([(40, 300), (200, 300), (360, 300), (520, 300)]):
        d.rectangle([x0, y0, x0 + 100, y0 + 120], fill=(100 + i * 30, 90, 60), outline="black", width=3)
    f = tmp_path / "sheet.png"
    sheet.save(f)

    class A:
        pass
    a = A()
    a.sheet, a.out = str(f), str(tmp_path / "parts")
    assert parts_mod.cmd_cut(a) == 0
    meta = json.loads((tmp_path / "parts" / "parts.json").read_text())
    assert len(meta) == 7
    white = [m for m in meta if m["size"][0] > 220 and m["size"][1] < 170][0]          # the garment is its own part and keeps its white interior (alpha 255 inside)
    im = Image.open(tmp_path / "parts" / white["file"]).convert("RGBA")
    assert im.getpixel((im.width // 2, im.height // 2))[3] == 255


def test_cut_warns_when_the_inventory_is_wrong(tmp_path):
    Image.new("RGB", (400, 300), "white").save(tmp_path / "empty.png")

    class A:
        pass
    a = A()
    a.sheet, a.out = str(tmp_path / "empty.png"), str(tmp_path / "p")
    assert parts_mod.cmd_cut(a) == 2


def test_static_nonzero_angle_is_not_motion_and_offcanvas_edge_refused():
    r = good(); r["animation"]["tracks"][0]["keys"] = [[0, 80], [2, 80]]
    with pytest.raises(ValueError):
        rig_mod.validate(r, set(SIZES), SIZES)
    r = good(); r["layers"][1]["x"] = 1000
    with pytest.raises(ValueError):
        rig_mod.validate(r, set(SIZES), SIZES)
