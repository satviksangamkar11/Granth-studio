"""Kaggle-side benchmark: reference-conditioned keyframes from OPEN image-edit models on a T4. Technical trial only: nothing here validates a model.

Inputs dir: prompts.json {"scenes": {"1": {"refs": [...], "prompt": "..."}}} plus the owner's reference JPGs. Output: one PNG per model x scene x seed and receipt.json.
Usage: python open_edit_bench.py --inputs DIR --out DIR --models klein[,qwen] --seeds 2
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import traceback
from pathlib import Path

W, H = 1024, 768
_T0 = time.time()


def log(msg: str) -> None:
    """Timestamped step line with GPU memory, flushed at once so a Kaggle log shows progress live."""
    mem = ""
    try:
        import torch
        if torch.cuda.is_available():
            mem = " | gpu mem " + ", ".join(f"{torch.cuda.memory_allocated(i) / 2**30:.1f}/{torch.cuda.get_device_properties(i).total_memory / 2**30:.0f}GiB" for i in range(torch.cuda.device_count()))
    except Exception:
        pass
    print(f"[{time.time() - _T0:7.1f}s] {msg}{mem}", flush=True)
KLEIN_REPO = "black-forest-labs/FLUX.2-klein-4B"
QWEN_REPO = "Qwen/Qwen-Image-Edit-2511"


def is_blank(image) -> bool:
    """A black or one-colour picture is the usual silent failure of a half-precision model."""
    lo, hi = image.convert("L").getextrema()
    return hi - lo < 8


def scrub(text: str) -> str:
    """Redact anything that looks like a Hugging Face token (and the exact loaded value) before text is persisted."""
    text = re.sub(r"hf_[A-Za-z0-9]{10,}", "hf_***", text)
    value = os.environ.get("HF_TOKEN", "")
    return text.replace(value, "***") if len(value) > 8 else text


def write_receipt(out: Path, receipt: dict) -> None:
    tmp = out / "receipt.json.tmp"
    tmp.write_text(scrub(json.dumps(receipt, indent=2)), encoding="utf-8")
    os.replace(tmp, out / "receipt.json")


def load_refs(inputs: Path, names: list[str]):
    from PIL import Image
    images = []
    for name in names:
        im = Image.open(inputs / name).convert("RGB")
        im.thumbnail((448, 448))
        images.append(im)
    return images


def build_klein():
    import torch
    from diffusers import Flux2KleinPipeline
    pipe = Flux2KleinPipeline.from_pretrained(KLEIN_REPO, torch_dtype=torch.bfloat16)   # bf16: fp16 risks NaN/black on this family
    pipe.enable_sequential_cpu_offload()                    # whole-model offload ran out of memory next to 5 reference latents on a 15 GB T4
    pipe.vae.enable_tiling()
    return pipe, lambda pipe, imgs, prompt, seed: pipe(image=imgs, prompt=prompt, height=H, width=W, num_inference_steps=4, guidance_scale=1.0,
                                                       generator=torch.Generator("cpu").manual_seed(seed)).images[0]


def build_qwen():
    import torch
    from diffusers import QwenImageEditPlusPipeline
    from diffusers.quantizers import PipelineQuantizationConfig
    quant = PipelineQuantizationConfig(quant_backend="bitsandbytes_4bit",
                                       quant_kwargs={"load_in_4bit": True, "bnb_4bit_quant_type": "nf4", "bnb_4bit_compute_dtype": torch.float16},
                                       components_to_quantize=["transformer", "text_encoder"])
    pipe = QwenImageEditPlusPipeline.from_pretrained(QWEN_REPO, torch_dtype=torch.float16, quantization_config=quant)
    import diffusers.pipelines.qwenimage.pipeline_qwenimage_edit_plus as q
    q.VAE_IMAGE_SIZE = 512 * 512                            # default 1024*1024 per reference: five references overflow a 15 GB T4
    pipe.enable_model_cpu_offload()
    pipe.vae.enable_tiling()
    return pipe, lambda pipe, imgs, prompt, seed: pipe(image=imgs, prompt=prompt, height=H, width=W, num_inference_steps=40, true_cfg_scale=4.0,
                                                       negative_prompt=" ", generator=torch.Generator("cpu").manual_seed(seed)).images[0]


def build_kontext():
    """FLUX.1 Kontext dev takes ONE image: the references are placed side by side on one strip. Gated on Hugging Face: needs HF_TOKEN in the environment (Kaggle Secret)."""
    import torch
    from diffusers import FluxKontextPipeline
    from diffusers.quantizers import PipelineQuantizationConfig
    from PIL import Image
    quant = PipelineQuantizationConfig(quant_backend="bitsandbytes_4bit",
                                       quant_kwargs={"load_in_4bit": True, "bnb_4bit_quant_type": "nf4", "bnb_4bit_compute_dtype": torch.bfloat16},
                                       components_to_quantize=["transformer", "text_encoder_2"])
    pipe = FluxKontextPipeline.from_pretrained("black-forest-labs/FLUX.1-Kontext-dev", torch_dtype=torch.bfloat16, quantization_config=quant)
    pipe.enable_model_cpu_offload()

    def run(pipe, imgs, prompt, seed):
        h = 512
        strip = Image.new("RGB", (sum(int(i.width * h / i.height) for i in imgs), h), "white")
        x = 0
        for i in imgs:
            i = i.resize((int(i.width * h / i.height), h)); strip.paste(i, (x, 0)); x += i.width
        return pipe(image=strip, prompt=prompt, guidance_scale=2.5, num_inference_steps=28, height=768, width=1024,
                    generator=torch.Generator("cpu").manual_seed(seed)).images[0]
    return pipe, run


def build_qwen21():
    """Qwen-Image-2.1 (7B, ungated). bf16 whole did not fit a 15 GB T4 (OutOfMemory at the first image), so the transformer is stored in 4-bit NF4 and the text encoder is offloaded."""
    import torch
    from diffusers import QwenImage21Pipeline
    from diffusers.quantizers import PipelineQuantizationConfig
    quant = PipelineQuantizationConfig(quant_backend="bitsandbytes_4bit",
                                       quant_kwargs={"load_in_4bit": True, "bnb_4bit_quant_type": "nf4", "bnb_4bit_compute_dtype": torch.bfloat16},
                                       components_to_quantize=["transformer"])
    pipe = QwenImage21Pipeline.from_pretrained("Qwen/Qwen-Image-2.1", torch_dtype=torch.bfloat16, quantization_config=quant)
    pipe.enable_model_cpu_offload()
    pipe.vae.enable_tiling()
    return pipe, lambda pipe, imgs, prompt, seed: pipe(prompt=prompt, image=imgs, width=W, height=H, num_inference_steps=40,
                                                       generator=torch.Generator("cpu").manual_seed(seed)).images[0]


def build_flux3():
    """FLUX 3 Image Klein (gated on Hugging Face: needs HF_TOKEN). The model card is gated, so the call below is a best guess and may need a fix."""
    import torch
    from diffusers import DiffusionPipeline
    pipe = DiffusionPipeline.from_pretrained("black-forest-labs/flux-3-image-klein", torch_dtype=torch.bfloat16)
    pipe.enable_model_cpu_offload()
    return pipe, lambda pipe, imgs, prompt, seed: pipe(prompt=prompt, image=imgs, width=W, height=H,
                                                       generator=torch.Generator("cpu").manual_seed(seed)).images[0]


BUILDERS = {"klein": build_klein, "qwen": build_qwen, "kontext": build_kontext, "qwen21": build_qwen21, "flux3": build_flux3}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--models", default="klein")
    ap.add_argument("--seeds", type=int, default=2)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    spec = json.loads((args.inputs / "prompts.json").read_text(encoding="utf-8"))
    import torch
    import diffusers
    receipt = {"torch": torch.__version__, "diffusers": diffusers.__version__, "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
               "note": "technical trial; outputs are not validated; human review NOT_DONE", "models": {}}
    for name in args.models.split(","):
        entry = receipt["models"][name] = {"results": [], "error": None}
        try:
            t0 = time.time()
            log(f"{name}: loading model (download + weights)")
            pipe, run = BUILDERS[name]()
            log(f"{name}: model loaded")
            entry["load_s"] = round(time.time() - t0, 1)
            for scene, item in spec["scenes"].items():
                imgs = load_refs(args.inputs, item["refs"])
                for seed in range(args.seeds):
                    t1 = time.time()
                    row = {"scene": scene, "seed": seed}
                    log(f"{name}: scene {scene} seed {seed}: generating with {len(imgs)} reference images")
                    try:
                        image = run(pipe, imgs, item["prompt"], seed)
                        path = args.out / f"{name}_s{scene}_seed{seed}.png"
                        image.save(path)
                        row.update(file=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest(), size=list(image.size),
                                   min_max=[int(v) for v in (image.convert("L").getextrema())], blank=is_blank(image))
                    except Exception as exc:                                  # one failed image must not hide the rest
                        row["error"] = f"{type(exc).__name__}: {exc}"[:400]
                        traceback.print_exc()
                    row["wall_s"] = round(time.time() - t1, 1)
                    entry["results"].append(row)
                    write_receipt(args.out, receipt)
                    log(f"{name}: scene {scene} seed {seed}: done {row.get('file') or row.get('error')} in {row['wall_s']}s")
            del pipe
        except Exception as exc:
            entry["error"] = f"{type(exc).__name__}: {exc}"[:600]
            log(f"{name}: FAILED during load/run: {entry['error']}")
            traceback.print_exc()
        torch.cuda.empty_cache()
        write_receipt(args.out, receipt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
