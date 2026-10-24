"""Kaggle TPU benchmark: reference-conditioned keyframes from open image models on a TPU v5e (torch_xla). Technical trial only: nothing here validates a model.

Every step is logged to stdout AND to <out>/run.log (the notebook log page can stay empty on a TPU session), and <out>/receipt.json is rewritten after every
image, so a crash or a time-out still leaves the evidence. Each model runs in its own try block: one failure never hides the others.

Plan per model: build the pipeline on the CPU in bfloat16 (the TPU's native type), run the TEXT ENCODER on the CPU (it does not fit next to the transformer in the
16 GB of one chip), move only the transformer and the VAE to the TPU chip, then denoise there. A model whose parts do not fit is recorded as such.

Usage: python tpu_bench.py --inputs DIR --out DIR --models qwen21,klein,kontext,flux3 --seeds 1
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import sys
import time
import traceback
from pathlib import Path

W, H = 1024, 768
_T0 = time.time()
_LOG = None


def log(msg: str) -> None:
    line = f"[{time.time() - _T0:7.1f}s] {msg}"
    print(line, flush=True)
    if _LOG is not None:
        _LOG.write(line + "\n")
        _LOG.flush()


def is_blank(image) -> bool:
    """A black (or one-colour) picture is the usual silent failure of a half-precision model."""
    lo, hi = image.convert("L").getextrema()
    return hi - lo < 8


def load_refs(inputs: Path, names: list[str]):
    from PIL import Image
    refs = []
    for name in names:
        im = Image.open(inputs / name).convert("RGB")
        im.thumbnail((512, 512))
        refs.append(im)
    return refs


def strip(images, height=512):
    """FLUX.1 Kontext takes one image: put the references side by side."""
    from PIL import Image
    parts = [i.resize((max(1, int(i.width * height / i.height)), height)) for i in images]
    canvas = Image.new("RGB", (sum(p.width for p in parts), height), "white")
    x = 0
    for p in parts:
        canvas.paste(p, (x, 0))
        x += p.width
    return canvas


def tpu_device():
    import torch_xla
    import torch_xla.core.xla_model as xm
    dev = xm.xla_device()
    log(f"TPU device {dev}; torch_xla {torch_xla.__version__}")
    return dev, xm


def to_tpu_and_sync(module, dev, xm, name: str):
    t = time.time()
    module.to(dev)
    xm.mark_step()
    xm.wait_device_ops()
    log(f"{name} moved to the TPU in {time.time() - t:.0f}s")


def pin_execution_device(pipe, dev):
    """Diffusers finds the denoising device from module hooks, and the CPU text-encoder hook would answer 'cpu': pin it to the TPU explicitly."""
    pipe.__class__ = type(pipe.__class__.__name__, (pipe.__class__,), {"_execution_device": property(lambda self: dev)})
    log(f"pipeline execution device pinned to {dev}")


def encoders_on_cpu(pipe, names=("text_encoder", "text_encoder_2")):
    """Keep the big text encoders on the CPU, but let the pipeline believe everything lives on the TPU: the hook moves each call's inputs to the CPU and returns the outputs on the device the call came from."""
    from accelerate.hooks import AlignDevicesHook, add_hook_to_module
    done = []
    for name in names:
        module = getattr(pipe, name, None)
        if module is not None:
            module.to("cpu")
            add_hook_to_module(module, AlignDevicesHook(execution_device="cpu", io_same_device=True), append=True)
            done.append(name)
    log(f"text encoders kept on the CPU through hooks: {done}")


# ---- model runners: build() -> (pipe, generate(pipe, refs, prompt, seed) -> PIL image)

def build_qwen21(dev, xm):
    import torch
    from diffusers import QwenImage21Pipeline
    log("qwen21: loading Qwen/Qwen-Image-2.1 on the CPU (bfloat16)")
    pipe = QwenImage21Pipeline.from_pretrained("Qwen/Qwen-Image-2.1", torch_dtype=torch.bfloat16)
    encoders_on_cpu(pipe)
    pin_execution_device(pipe, dev)
    to_tpu_and_sync(pipe.transformer, dev, xm, "qwen21 transformer")
    to_tpu_and_sync(pipe.vae, dev, xm, "qwen21 vae")

    def generate(pipe, refs, prompt, seed):
        with torch.no_grad():
            out = pipe(prompt=prompt, image=refs, width=W, height=H, num_inference_steps=40,
                       generator=torch.Generator("cpu").manual_seed(seed))
        xm.mark_step()
        return out.images[0]
    return pipe, generate


def build_klein(dev, xm):
    import torch
    from diffusers import Flux2KleinPipeline
    log("klein: loading black-forest-labs/FLUX.2-klein-4B on the CPU (bfloat16)")
    pipe = Flux2KleinPipeline.from_pretrained("black-forest-labs/FLUX.2-klein-4B", torch_dtype=torch.bfloat16)
    encoders_on_cpu(pipe)
    pin_execution_device(pipe, dev)
    to_tpu_and_sync(pipe.transformer, dev, xm, "klein transformer")
    to_tpu_and_sync(pipe.vae, dev, xm, "klein vae")

    def generate(pipe, refs, prompt, seed):
        with torch.no_grad():
            out = pipe(image=refs, prompt=prompt, height=H, width=W, num_inference_steps=4, guidance_scale=1.0,
                       generator=torch.Generator("cpu").manual_seed(seed))
        xm.mark_step()
        return out.images[0]
    return pipe, generate


def build_kontext(dev, xm):
    import torch
    from diffusers import FluxKontextPipeline
    log("kontext: loading black-forest-labs/FLUX.1-Kontext-dev on the CPU (bfloat16); gated, needs HF_TOKEN")
    pipe = FluxKontextPipeline.from_pretrained("black-forest-labs/FLUX.1-Kontext-dev", torch_dtype=torch.bfloat16)
    encoders_on_cpu(pipe)
    pin_execution_device(pipe, dev)
    to_tpu_and_sync(pipe.transformer, dev, xm, "kontext transformer")
    to_tpu_and_sync(pipe.vae, dev, xm, "kontext vae")

    def generate(pipe, refs, prompt, seed):
        with torch.no_grad():
            out = pipe(image=strip(refs), prompt=prompt, guidance_scale=2.5, num_inference_steps=28, height=H, width=W,
                       generator=torch.Generator("cpu").manual_seed(seed))
        xm.mark_step()
        return out.images[0]
    return pipe, generate


def build_flux3(dev, xm):
    import torch
    from diffusers import DiffusionPipeline
    log("flux3: loading black-forest-labs/flux-3-image-klein on the CPU (bfloat16); gated, needs HF_TOKEN")
    pipe = DiffusionPipeline.from_pretrained("black-forest-labs/flux-3-image-klein", torch_dtype=torch.bfloat16)
    encoders_on_cpu(pipe)
    pin_execution_device(pipe, dev)
    to_tpu_and_sync(pipe.transformer, dev, xm, "flux3 transformer")
    to_tpu_and_sync(pipe.vae, dev, xm, "flux3 vae")

    def generate(pipe, refs, prompt, seed):
        with torch.no_grad():
            out = pipe(prompt=prompt, image=refs, width=W, height=H, generator=torch.Generator("cpu").manual_seed(seed))
        xm.mark_step()
        return out.images[0]
    return pipe, generate


BUILDERS = {"qwen21": build_qwen21, "klein": build_klein, "kontext": build_kontext, "flux3": build_flux3}
UNSUPPORTED = {"kontext": "FLUX.1 Kontext dev is 12B parameters: its bfloat16 transformer alone is about 24 GB and cannot fit one 16 GB TPU chip; it would need SPMD sharding, which is not implemented here",
               "hidream": "HiDream-O1-Image ships a CUDA-only inference script (device_map='cuda', flash attention); no TPU path exists for it"}


def write_receipt(out: Path, receipt: dict) -> None:
    tmp = out / "receipt.json.tmp"
    tmp.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    os.replace(tmp, out / "receipt.json")


def main() -> int:
    global _LOG
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--models", default="qwen21,klein")
    ap.add_argument("--seeds", type=int, default=1)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    _LOG = open(args.out / "run.log", "a", encoding="utf-8")
    spec = json.loads((args.inputs / "prompts.json").read_text(encoding="utf-8"))
    import torch
    import diffusers
    receipt = {"torch": torch.__version__, "diffusers": diffusers.__version__, "device": "tpu",
               "note": "technical trial; outputs are not validated; human review NOT_DONE", "models": {}}
    try:
        dev, xm = tpu_device()
    except Exception as exc:
        log(f"STOP: no usable TPU through torch_xla: {type(exc).__name__}: {str(exc)[:300]}")
        receipt["error"] = f"no TPU: {type(exc).__name__}: {str(exc)[:300]}"
        write_receipt(args.out, receipt)
        return 2
    for name in [m for m in args.models.split(",") if m]:
        entry = receipt["models"][name] = {"results": [], "error": None}
        if name in UNSUPPORTED:
            entry["error"] = "unsupported: " + UNSUPPORTED[name]
            log(f"{name}: SKIPPED, {entry['error']}")
            write_receipt(args.out, receipt)
            continue
        if name not in BUILDERS:
            entry["error"] = "unknown model"
            continue
        pipe = None
        try:
            t0 = time.time()
            pipe, generate = BUILDERS[name](dev, xm)
            entry["load_s"] = round(time.time() - t0, 1)
            log(f"{name}: ready after {entry['load_s']}s")
            for scene, item in spec["scenes"].items():
                refs = load_refs(args.inputs, item["refs"])
                for seed in range(args.seeds):
                    row = {"scene": scene, "seed": seed}
                    t1 = time.time()
                    log(f"{name}: scene {scene} seed {seed}: generating with {len(refs)} references")
                    try:
                        image = generate(pipe, refs, item["prompt"], seed)
                        path = args.out / f"{name}_s{scene}_seed{seed}.png"
                        image.save(path)
                        row.update(file=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest(), size=list(image.size), blank=is_blank(image))
                    except Exception as exc:
                        row["error"] = f"{type(exc).__name__}: {exc}"[:500]
                        log(f"{name}: scene {scene} seed {seed}: FAILED {row['error']}")
                        traceback.print_exc()
                    row["wall_s"] = round(time.time() - t1, 1)
                    log(f"{name}: scene {scene} seed {seed}: {row.get('file') or row.get('error')} in {row['wall_s']}s" + (" BLANK IMAGE" if row.get("blank") else ""))
                    entry["results"].append(row)
                    write_receipt(args.out, receipt)
        except Exception as exc:
            entry["error"] = f"{type(exc).__name__}: {exc}"[:600]
            log(f"{name}: FAILED while loading or running: {entry['error']}")
            traceback.print_exc()
        finally:
            pipe = generate = None                                   # release the model before the next one loads
            gc.collect()
            try:
                xm.mark_step()
            except Exception:
                pass
        write_receipt(args.out, receipt)
    usable = [r for e in receipt["models"].values() for r in e["results"] if r.get("file") and not r.get("blank")]
    blank = [r for e in receipt["models"].values() for r in e["results"] if r.get("blank")]
    log(f"finished: {len(usable)} usable image(s), {len(blank)} blank, models with errors: {[n for n, e in receipt['models'].items() if e['error']]}")
    return 0 if usable else 3


if __name__ == "__main__":
    sys.exit(main())
