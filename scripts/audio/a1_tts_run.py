"""Kaggle job: Indic Parler-TTS speech for every Adhyay 1 line in Marathi and Hindi (DRAFT voices, NOT VALIDATED until the owner has listened).
Runs on a Kaggle GPU with Internet ON. Needs the Kaggle SECRET named HF_TOKEN (a read-only Hugging Face token of an account that has accepted the terms of ai4bharat/indic-parler-tts);
the token is never printed or written, and the outputs are scanned for it before they are kept.
Input: a dataset file A1_tts_input.json (jobs: id, speaker, description, text, seed). Output (in /kaggle/working/a1_voice): wav/<lang>/<id>.wav, tts_manifest.json, a1_voice.zip.
Env: ONLY=S1-L1.mr,S1-L1.hi (a small sample), LIMIT=N."""
from __future__ import annotations

import glob
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

WORK = "/kaggle/working"
OUT = f"{WORK}/a1_voice"


def secret() -> str:
    try:
        from kaggle_secrets import UserSecretsClient
        tok = UserSecretsClient().get_secret("HF_TOKEN")
    except Exception as exc:
        raise SystemExit(f"NOT_RUN: the Kaggle secret HF_TOKEN is not available ({type(exc).__name__}). Open this notebook on Kaggle, Add-ons > Secrets, add HF_TOKEN and tick it, then run again.")
    if not tok or len(tok.strip()) < 8:
        raise SystemExit("NOT_RUN: HF_TOKEN is empty")
    return tok.strip()


def main() -> int:
    token = secret()
    os.environ["HF_TOKEN"] = token
    src = glob.glob("/kaggle/input/**/A1_tts_input.json", recursive=True)
    if not src:
        raise SystemExit("NOT_RUN: attach the dataset holding A1_tts_input.json")
    spec = json.load(open(src[0], encoding="utf-8"))
    jobs = spec["jobs"]
    if os.environ.get("ONLY"):
        want = set(os.environ["ONLY"].split(","))
        jobs = [j for j in jobs if j["id"] in want]
    if os.environ.get("LIMIT"):
        jobs = jobs[: int(os.environ["LIMIT"])]
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "git+https://github.com/huggingface/parler-tts.git", "soundfile"], check=True)
    for k in ("USE_TF", "USE_JAX", "USE_FLAX"):                       # Kaggle ships TensorFlow, which needs a newer protobuf than parler-tts installs: keep transformers on PyTorch only
        os.environ[k] = "0"
    os.environ["USE_TORCH"] = "1"
    import soundfile as sf
    import torch
    import transformers
    from parler_tts import ParlerTTSForConditionalGeneration
    from transformers import AutoTokenizer
    dev = "cuda:0" if torch.cuda.is_available() else "cpu"
    print("device", dev, "torch", torch.__version__, "transformers", transformers.__version__, flush=True)
    model = ParlerTTSForConditionalGeneration.from_pretrained(spec["model"], token=token).to(dev)
    tok_prompt = AutoTokenizer.from_pretrained(spec["model"], token=token)
    tok_desc = AutoTokenizer.from_pretrained(model.config.text_encoder._name_or_path)
    sr = model.config.sampling_rate
    shutil.rmtree(OUT, ignore_errors=True)
    rows, t0 = [], time.time()
    for k, j in enumerate(jobs, 1):
        row = {"id": j["id"], "lang": j["lang"], "speaker": j["speaker"], "voice": j["voice"], "text": j["text"], "text_sha256": j["text_sha256"], "seed": j["seed"], "ok": False}
        try:
            torch.manual_seed(j["seed"])
            d = tok_desc(j["description"], return_tensors="pt").to(dev)
            p = tok_prompt(j["text"], return_tensors="pt").to(dev)
            with torch.no_grad():
                gen = model.generate(input_ids=d.input_ids, attention_mask=d.attention_mask, prompt_input_ids=p.input_ids, prompt_attention_mask=p.attention_mask)
            arr = gen.cpu().numpy().squeeze()
            path = f"{OUT}/wav/{j['lang']}/{j['id']}.wav"
            os.makedirs(os.path.dirname(path), exist_ok=True)
            sf.write(path, arr, sr)
            row.update(ok=True, wav=f"wav/{j['lang']}/{j['id']}.wav", sampling_rate=sr, seconds=round(len(arr) / sr, 3), wav_sha256=hashlib.sha256(open(path, "rb").read()).hexdigest())
        except Exception as exc:                                              # a failed line is recorded, never hidden
            row["error"] = f"{type(exc).__name__}: {str(exc).replace(token, '[token]')[:200]}"
        rows.append(row)
        print(f"[{k}/{len(jobs)}] {j['id']} {row.get('seconds')} s {'OK' if row['ok'] else row.get('error')}", flush=True)
    manifest = {"model": spec["model"], "model_commit": getattr(model.config, "_commit_hash", None), "device": dev, "sampling_rate": sr, "split_sha256": spec.get("split_sha256"),
                "status": "DRAFT voices, NOT VALIDATED until the owner has listened", "wall_s": round(time.time() - t0, 1), "lines": rows,
                "ok": sum(1 for r in rows if r["ok"]), "failed": sum(1 for r in rows if not r["ok"])}
    os.makedirs(OUT, exist_ok=True)
    json.dump(manifest, open(f"{OUT}/tts_manifest.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    leaked = [p for p in glob.glob(f"{OUT}/**/*", recursive=True) if os.path.isfile(p) and token.encode() in open(p, "rb").read()]
    if leaked:
        shutil.rmtree(OUT, ignore_errors=True)
        raise SystemExit("the token was found in an output file: outputs deleted")
    shutil.make_archive(f"{WORK}/a1_voice", "zip", OUT)
    print("DONE", manifest["ok"], "ok,", manifest["failed"], "failed,", manifest["wall_s"], "s", flush=True)
    return 0 if manifest["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
