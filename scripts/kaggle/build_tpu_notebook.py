import json, os
CELL1 = '''import subprocess, sys, glob, os, json, time, shutil
T0=time.time(); os.makedirs("/kaggle/working/tpu", exist_ok=True)
LOGF=open("/kaggle/working/tpu/notebook.log","a")
def log(m):
    line=f"[{time.time()-T0:7.1f}s] {m}"; print(line, flush=True); LOGF.write(line+chr(10)); LOGF.flush()
def sh(cmd, tag, **kw):
    log(f"{tag}: START {' '.join(cmd)[:200]}")
    p=subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, **kw)
    for l in p.stdout: log(f"[{tag}] {l.rstrip()[:300]}")
    rc=p.wait(); log(f"{tag}: END exit={rc}"); return rc
os.makedirs("/kaggle/temp/hf", exist_ok=True); os.environ["HF_HOME"]="/kaggle/temp/hf"
log("STEP 1 environment (TPU session)"); sh(["bash","-c","uname -a; python --version; nproc; free -g; df -h /kaggle/working /kaggle/temp; env | grep -i -E 'tpu|xla|pjrt' | cut -c1-160"],"system")
sh(["bash","-c","pip list 2>/dev/null | grep -i -E 'torch|xla|jax|libtpu|diffusers|transformers|accelerate'"],"packages")
PRE_PY = "import torch, torch_xla, torch_xla.core.xla_model as xm; d=xm.xla_device(); a=torch.randn(1024,1024,dtype=torch.bfloat16,device=d); xm.mark_step(); print('torch',torch.__version__,'torch_xla',torch_xla.__version__,'device',d,'sum',float((a@a).sum()))"
rc=sh([sys.executable,"-c",PRE_PY],"tpu-preflight")
if rc!=0: log("STOP: TPU not usable through torch_xla (see the preflight lines above)"); raise SystemExit(2)
'''
CELL2 = '''log("STEP 2 install diffusers (git main) and text-model libraries; torch and torch_xla are NOT touched")
frozen=subprocess.run([sys.executable,"-m","pip","freeze"],capture_output=True,text=True).stdout.splitlines()
pins=[l for l in frozen if l.split("==")[0].lower().replace("_","-") in ("torch","torch-xla","torchvision","libtpu","jax","jaxlib")]
open("/kaggle/working/tpu/constraints.txt","w").write(chr(10).join(pins)+chr(10)); log(f"constraining the accelerator stack: {pins}")
if sh([sys.executable,"-m","pip","install","-q","-c","/kaggle/working/tpu/constraints.txt","git+https://github.com/huggingface/diffusers","transformers>=5.17","accelerate","sentencepiece","protobuf","huggingface_hub"],"pip")!=0: raise SystemExit("STOP: package install failed")
after=[l for l in subprocess.run([sys.executable,"-m","pip","freeze"],capture_output=True,text=True).stdout.splitlines() if l in pins]
if sorted(after)!=sorted(pins): raise SystemExit(f"STOP: the install changed the accelerator stack: before {pins} after {after}")
log("accelerator stack unchanged after the install")
import importlib; importlib.invalidate_caches()
import diffusers, transformers; log(f"diffusers {diffusers.__version__}, transformers {transformers.__version__}")
log("STEP 3 Hugging Face token and gated-repo access (Kontext and FLUX 3 Image Klein)")
ACCESS={}
try:
    from kaggle_secrets import UserSecretsClient
    os.environ["HF_TOKEN"]=UserSecretsClient().get_secret("HF_TOKEN"); log("HF_TOKEN secret found (value never printed)")
    from huggingface_hub import HfApi, hf_hub_download
    log(f"token belongs to Hugging Face user: {HfApi().whoami().get('name')}")
    for key,repo in (("flux3","black-forest-labs/flux-3-image-klein"),("kontext","black-forest-labs/FLUX.1-Kontext-dev")):
        try:
            hf_hub_download(repo,"config.json" if key=="flux3" else "model_index.json"); ACCESS[key]=True; log(f"access OK (gated config file downloaded): {repo}")
            if key=="flux3":
                txt=open(hf_hub_download(repo,"README.md"),encoding="utf-8").read(); i=txt.lower().find("diffusers"); log("FLUX 3 model-card usage text follows:"); print(txt[max(0,i-300):i+3000], flush=True)
        except Exception as e:
            ACCESS[key]=False; log(f"NO ACCESS to {repo}: {type(e).__name__}. Use a token from the account that was granted access (fine-grained: allow reading public gated repos). {key} SKIPPED.")
except Exception as e:
    ACCESS={"flux3":False,"kontext":False}; log(f"HF_TOKEN secret NOT available ({type(e).__name__}): FLUX 3 and Kontext SKIPPED.")
inp=os.path.dirname(glob.glob("/kaggle/input/**/tpu_bench.py", recursive=True)[0]); log(f"inputs at {inp}: {sorted(os.listdir(inp))}")
'''
CELL3 = '''OUT="/kaggle/working/tpu"
models=["qwen21","klein"]+(["flux3"] if ACCESS.get("flux3") else [])+["kontext","hidream"]
log(f"STEP 4 run on the TPU: {models} (kontext: 12B does not fit one chip; hidream: CUDA-only code; both are recorded as unsupported, not run)")
rc=sh([sys.executable,"-u",f"{inp}/tpu_bench.py","--inputs",inp,"--out",OUT,"--models",",".join(models),"--seeds","1"],"tpu_bench")
log(f"tpu_bench exit {rc}")
'''
CELL4 = '''log("STEP 5 summary and comparison sheet")
from PIL import Image, ImageDraw
f=f"{OUT}/receipt.json"; r=json.load(open(f)) if os.path.exists(f) else {}
for m,e in r.get("models",{}).items(): log(f"{m}: load={e.get('load_s')} error={e.get('error')}; results={[(x.get('file') or x.get('error')) + (' BLANK' if x.get('blank') else '') for x in e.get('results',[])]}")
usable={m:{x["scene"]:x["file"] for x in e.get("results",[]) if x.get("file") and not x.get("blank")} for m,e in r.get("models",{}).items()}
names=[m for m,v in usable.items() if v]
if names:
    W,H=480,360; sheet=Image.new("RGB",(W*len(names),(H+16)*3),"white"); d=ImageDraw.Draw(sheet)
    for c,m in enumerate(names):
        for rr,s in enumerate("123"):
            d.text((c*W+4,rr*(H+16)+2),f"{m} scene {s}",fill="black"); fn=usable[m].get(s)
            if fn: sheet.paste(Image.open(f"{OUT}/{fn}").convert("RGB").resize((W,H)),(c*W,rr*(H+16)+16))
    sheet.save(f"{OUT}/compare.png"); log(f"saved {OUT}/compare.png")
else: log("no images were produced: see run.log and receipt.json")
log(f"DONE (tpu_bench exit {rc})")
if rc!=0: raise SystemExit(f"tpu_bench exit {rc}: no usable image or no TPU; see {OUT}/run.log")
'''
cells=[CELL1,CELL2,CELL3,CELL4]
for c in cells: compile(c,"c","exec")
d="kernel_tpu_all"; os.makedirs(d,exist_ok=True); slug="granthstudio-tpu-all"
json.dump({"cells":[{"cell_type":"code","metadata":{},"source":c.splitlines(True),"outputs":[],"execution_count":None} for c in cells],"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"}},"nbformat":4,"nbformat_minor":5},open(f"{d}/{slug}.ipynb","w"))
json.dump({"id":f"satviksangamkar54321/{slug}","title":slug,"code_file":f"{slug}.ipynb","language":"python","kernel_type":"notebook","is_private":True,"enable_gpu":False,"enable_tpu":True,"enable_internet":True,"machine_shape":"TpuV5E8","dataset_sources":["satviksangamkar54321/granthstudio-tpu-inputs"],"competition_sources":[],"kernel_sources":[],"model_sources":[]},open(f"{d}/kernel-metadata.json","w"))
print("ok")
