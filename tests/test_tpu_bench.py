"""tpu_bench helpers on synthetic images (the TPU itself is never touched here)."""
import importlib.util
import json
from pathlib import Path

from PIL import Image

spec = importlib.util.spec_from_file_location("tpu_bench", Path(__file__).resolve().parents[1] / "scripts" / "image_trials" / "tpu_bench.py")
tb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tb)


def test_a_black_or_flat_image_is_blank_and_a_painting_is_not():
    assert tb.is_blank(Image.new("RGB", (64, 64), "black"))
    assert tb.is_blank(Image.new("RGB", (64, 64), (120, 120, 120)))
    half = Image.new("RGB", (64, 64), "black")
    half.paste(Image.new("RGB", (32, 64), "white"), (0, 0))
    assert not tb.is_blank(half)


def test_strip_puts_references_side_by_side_at_one_height():
    out = tb.strip([Image.new("RGB", (100, 50), "red"), Image.new("RGB", (50, 100), "blue")], height=40)
    assert out.height == 40 and out.width == 80 + 20


def test_refs_are_shrunk_and_converted(tmp_path):
    Image.new("L", (2000, 1000), 90).save(tmp_path / "a.jpg")
    (ref,) = tb.load_refs(tmp_path, ["a.jpg"])
    assert ref.mode == "RGB" and max(ref.size) == 512


def test_hidream_is_declared_unsupported_and_every_other_model_has_a_builder():
    assert {"hidream", "kontext"} <= set(tb.UNSUPPORTED) and set(tb.BUILDERS) == {"qwen21", "klein", "kontext", "flux3"}


def test_receipt_is_replaced_atomically(tmp_path):
    tb.write_receipt(tmp_path, {"a": 1})
    tb.write_receipt(tmp_path, {"a": 2})
    assert json.loads((tmp_path / "receipt.json").read_text())["a"] == 2 and not (tmp_path / "receipt.json.tmp").exists()
