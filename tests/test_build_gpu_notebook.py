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
    assert "load_in_4bit=True" in mod.CELL3 and "t_embedder1" in mod.CELL3 and "--target" in mod.CELL3 and "scenes failed" in mod.CELL3


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


def test_tokens_are_scrubbed_from_every_log_line():
    """Run CELL1's scrub/log on fake secrets (no GPU needed: stop before the accelerator check)."""
    import os
    head = mod.CELL1.split('log("STEP 0')[0]
    ns = {}
    os.environ["HF_TOKEN"] = "plainSecretValue123"
    try:
        exec(head.replace("/kaggle/working/all", (Path(__file__).parent / "_scratch_all").as_posix()), ns)
        ns["log"]("whoami failed: Bearer hf_abcdefghijKLMNOP1234 and plainSecretValue123 end")
        text = (Path(__file__).parent / "_scratch_all" / "notebook.log").read_text()
        assert "hf_abcdefghij" not in text and "plainSecretValue123" not in text and "hf_***" in text and "***" in text
    finally:
        os.environ.pop("HF_TOKEN", None)
        import shutil
        shutil.rmtree(Path(__file__).parent / "_scratch_all", ignore_errors=True)


def test_tee_side_files_are_scrubbed_too():
    import os
    import shutil
    head = mod.CELL1.split('log("STEP 0')[0]
    scratch = Path(__file__).parent / "_scratch_tee"
    os.environ["HF_TOKEN"] = "plainSecretValue123"
    try:
        ns = {}
        exec(head.replace("/kaggle/working/all", scratch.as_posix()), ns)
        tee = scratch / "side.log"
        ns["sh"](["python", "-c", "print('token hf_abcdefghijKLMNOP1234 and plainSecretValue123')"], "t", timeout=60, tee=tee.as_posix())
        text = tee.read_text()
        assert "hf_abcdefghij" not in text and "plainSecretValue123" not in text and "***" in text
    finally:
        os.environ.pop("HF_TOKEN", None)
        shutil.rmtree(scratch, ignore_errors=True)


def test_receipts_never_persist_a_token(tmp_path):
    import os
    bspec = importlib.util.spec_from_file_location("open_edit_bench2", Path(__file__).resolve().parents[1] / "scripts" / "image_trials" / "open_edit_bench.py")
    bench = importlib.util.module_from_spec(bspec)
    bspec.loader.exec_module(bench)
    os.environ["HF_TOKEN"] = "plainSecretValue123"
    try:
        bench.write_receipt(tmp_path, {"models": {"m": {"error": "401 Bearer hf_abcdefghijKLMNOP1234 / plainSecretValue123", "results": [{"error": "x hf_zzzzzzzzzzzz0000"}]}}})
        text = (tmp_path / "receipt.json").read_text()
        assert "hf_abcdefghij" not in text and "hf_zzzzzzzz" not in text and "plainSecretValue123" not in text and "hf_***" in text
    finally:
        os.environ.pop("HF_TOKEN", None)


def test_the_hidream_patch_text_is_valid_python_and_flux3_is_not_run():
    import re
    m = re.search(r"s\.replace\('device_map=\"cuda\"', '(.+?)'\)\)", mod.CELL3)
    assert m, "patch line not found"
    snippet = "model = loader(args.model_path, torch_dtype=torch.bfloat16, " + m.group(1) + ").eval()"
    compile(snippet, "patched_inference", "exec")
    assert "llm_int8_skip_modules" in snippet and "not run on a T4" not in snippet.lower()
    assert 'bench("flux3")' not in mod.CELL3 and "NOT run on a T4" in mod.CELL3


def test_qwen21_and_disk_safeguards_are_present():
    bench = (Path(__file__).resolve().parents[1] / "scripts" / "image_trials" / "open_edit_bench.py").read_text(encoding="utf-8")
    assert "output_resolution=res" in bench and "(512, 384)" in bench and "OutOfMemoryError" in bench
    assert "free_cache" in mod.CELL1 and "free_cache(*c[1])" in mod.CELL3


def test_oom_retry_releases_the_failed_attempts_memory_before_the_smaller_try():
    import weakref
    bspec = importlib.util.spec_from_file_location("open_edit_bench3", Path(__file__).resolve().parents[1] / "scripts" / "image_trials" / "open_edit_bench.py")
    bench = importlib.util.module_from_spec(bspec)
    bspec.loader.exec_module(bench)

    class Boom(Exception):
        pass

    class Payload:
        pass

    seen = {}

    def call(res):
        if res == 512:
            payload = Payload()                                      # stands for the failed call's GPU tensors, pinned by the traceback
            seen["ref"] = weakref.ref(payload)
            raise Boom()
        seen["alive_at_retry"] = seen["ref"]() is not None
        return "image at %d" % res

    assert bench.with_smaller_references(call, oom=Boom, release=lambda: None) == "image at 384"
    assert seen["alive_at_retry"] is False

    def always(res):
        raise Boom()
    try:
        bench.with_smaller_references(always, oom=Boom, release=lambda: None)
        raise AssertionError("must raise")
    except RuntimeError as exc:
        assert "every reference resolution" in str(exc)
