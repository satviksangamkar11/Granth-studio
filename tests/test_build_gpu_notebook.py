"""The generated Kaggle GPU notebook compiles, never prints the token, and keeps its safeguards."""
import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location("build_gpu_all_notebook", Path(__file__).resolve().parents[1] / "scripts" / "kaggle" / "build_gpu_all_notebook.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_cells_compile_and_the_notebook_is_a_gpu_notebook(tmp_path):
    mod.main(str(tmp_path))
    meta = json.loads((tmp_path / "kernel-metadata.json").read_text())
    assert meta["enable_gpu"] and not meta["enable_tpu"] and meta["kernel_type"] == "notebook"
    nb = json.loads((tmp_path / "granthstudio-bench-gpu-all.ipynb").read_text())
    for i, cell in enumerate(nb["cells"]):
        compile("".join(cell["source"]), f"cell{i}", "exec")


def test_the_token_value_is_never_logged_and_failures_cannot_be_silent():
    text = "\n".join([mod.CELL1, mod.CELL2, mod.CELL3, mod.CELL4])
    assert "print(os.environ" not in text and "log(os.environ" not in text and "get_secret(\"HF_TOKEN\"))" not in text.replace("os.environ[\"HF_TOKEN\"] = UserSecretsClient().get_secret(\"HF_TOKEN\");", "")
    assert "raise SystemExit" in mod.CELL4 and "killpg" in mod.CELL1 and "TIMEOUT" in mod.CELL1
    assert "device_map=\"auto\"" in mod.CELL3 and "--target" in mod.CELL3


def test_bench_helpers_flag_blank_images_and_write_receipts_atomically(tmp_path):
    from PIL import Image
    bspec = importlib.util.spec_from_file_location("open_edit_bench", Path(__file__).resolve().parents[1] / "scripts" / "image_trials" / "open_edit_bench.py")
    bench = importlib.util.module_from_spec(bspec)
    bspec.loader.exec_module(bench)
    assert bench.is_blank(Image.new("RGB", (32, 32), "black"))
    painted = Image.new("RGB", (32, 32), "black")
    painted.paste(Image.new("RGB", (16, 32), "white"), (0, 0))
    assert not bench.is_blank(painted)
    bench.write_receipt(tmp_path, {"n": 1})
    bench.write_receipt(tmp_path, {"n": 2})
    assert json.loads((tmp_path / "receipt.json").read_text())["n"] == 2 and not (tmp_path / "receipt.json.tmp").exists()


def test_the_run_starts_from_an_empty_output_folder_and_hidream_setup_failures_stop_the_stage():
    assert "shutil.rmtree(OUT" in mod.CELL1 and "must=True" in mod.CELL3 and "BLANK IMAGE" in mod.CELL4


def test_summary_cell_runs_end_to_end_on_synthetic_outputs(tmp_path):
    """Execute CELL4 against a fake output folder: a good image, a blank one, a truncated PNG and a missing model."""
    from PIL import Image
    out = tmp_path / "all"
    (out / "qwen21").mkdir(parents=True)
    (out / "hidream").mkdir()
    good = Image.new("RGB", (40, 30), "black")
    good.paste(Image.new("RGB", (20, 30), "white"), (0, 0))
    good.save(out / "qwen21" / "qwen21_s1_seed0.png")
    Image.new("RGB", (40, 30), "black").save(out / "qwen21" / "qwen21_s2_seed0.png")
    (out / "hidream" / "hidream_s1.png").write_bytes(b"\x89PNG not really")
    (out / "qwen21" / "receipt.json").write_text(json.dumps({"models": {"qwen21": {"results": [
        {"scene": "1", "file": "qwen21_s1_seed0.png", "blank": False}, {"scene": "2", "file": "qwen21_s2_seed0.png", "blank": True},
        {"scene": "3", "error": "OutOfMemoryError"}]}}}))
    logs = []
    ns = {"OUT": str(out), "json": json, "os": __import__("os"), "shutil": __import__("shutil"), "log": logs.append}
    exec(mod.CELL4, ns)
    assert (out / "compare.png").exists()
    assert any("unreadable image" in line for line in logs) and any("DONE" in line for line in logs)
