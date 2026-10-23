#!/usr/bin/env bash
# First SDXL + IP-Adapter keyframe test of the PROVISIONAL 45-second pilot, on ONE Tesla T4 (GPU 0) of a Kaggle "GPU T4 x2" session. One invocation = one keyframe visual (with its no-reference control):
#
#   LTX_DOWNLOAD_APPROVED="Satvik Sangamkar" LTX_EXPECTED_COMMIT="<reviewed commit, full sha>" VISUAL=vis_s1_kf bash scripts/kaggle/sdxl_first_test.sh
#
# Authorization record: docs/pilot/SDXL_DOWNLOAD_APPROVAL.md (the owner's instruction; the assistant reviewed no licence). Everything that can be refused is refused BEFORE the first clone or
# download: missing approver or commit, wrong commit, dirty tree, bad session deadline, no ffmpeg, little disk, not the planned two-idle-T4 host, a busy port. The weights (~10.7 GB) go to the
# scratch disk and every file is verified against its pinned SHA-256 (any mismatch aborts). The IPAdapter node pack is cloned at its pinned commit and must be clean. One attempt per image:
# a CUDA out-of-memory error stops the stage. A PASS means technically valid images only; style fidelity and identity are judged by a human.
set -euo pipefail

VISUAL="${VISUAL:-vis_s1_kf}"
case "$VISUAL" in vis_s1_kf|vis_s2_kf|vis_s3_kf) ;; *) echo "VISUAL must be vis_s1_kf, vis_s2_kf or vis_s3_kf"; exit 2;; esac
STAGE="sdxl_$VISUAL"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
W="${W:-/kaggle/working}"; COMFY="$W/ComfyUI"; OUT="$W/${STAGE}_evidence"; PINS="$REPO/config/pilot_sdxl_pins.yaml"; LTXPINS="$REPO/config/ltx_098_pins.yaml"
SESSION_MINUTES="${SESSION_MINUTES:-240}"
COMFY_LOWVRAM="${COMFY_LOWVRAM:-0}"      # 1 = start ComfyUI with --lowvram (scenes with 4-5 IP-Adapter references do not fit a 15 GB T4 otherwise); recorded in worker0/launch.txt
case "$COMFY_LOWVRAM" in 0|1) ;; *) echo "COMFY_LOWVRAM must be 0 or 1"; exit 2;; esac
COMFY_FP16_VAE="${COMFY_FP16_VAE:-0}"    # 1 = decode with the pinned fp16-fix VAE in fp16 (--fp16-vae): the fp32 decode ran out of memory next to five references; recorded in launch.txt
case "$COMFY_FP16_VAE" in 0|1) ;; *) echo "COMFY_FP16_VAE must be 0 or 1"; exit 2;; esac
STYLE_SWEEP="${STYLE_SWEEP:-0}"          # 1 = EXPERIMENT: reference-free style sweep (4 seeds x cfg 6.5 and 9.0) instead of the normal keyframe test
case "$STYLE_SWEEP" in 0|1) ;; *) echo "STYLE_SWEEP must be 0 or 1"; exit 2;; esac
SWEEP_SEEDS="${SWEEP_SEEDS:-4}"; SWEEP_CFGS="${SWEEP_CFGS:-6.5,9.0}"
case "$SWEEP_SEEDS" in [1-6]) ;; *) echo "SWEEP_SEEDS must be 1..6"; exit 2;; esac
[[ "$SWEEP_CFGS" =~ ^[0-9]+(\.[0-9]+)?(,[0-9]+(\.[0-9]+)?){0,3}$ ]] || { echo "SWEEP_CFGS must be 1-4 comma separated numbers"; exit 2; }
python -c 'import sys; c=[float(x) for x in sys.argv[1].split(",")]; sys.exit(0 if len(set(c))==len(c) and all(1<=x<=15 for x in c) and len(c)*int(sys.argv[2])<=16 else 1)' "$SWEEP_CFGS" "$SWEEP_SEEDS"   || { echo "SWEEP_CFGS must be distinct values in 1..15 and SWEEP_SEEDS x cfgs at most 16 images"; exit 2; }
REFERENCE_SET="${REFERENCE_SET:-}"       # optional: repository-relative directory with manifest.json (owner-supplied references), e.g. assets/pilot_refs/set_v1
if [ -n "$REFERENCE_SET" ]; then
  [[ "$REFERENCE_SET" =~ ^[A-Za-z0-9_][A-Za-z0-9_./-]*$ && "$REFERENCE_SET" != *..* ]] || { echo "REFERENCE_SET must be a plain repository-relative path"; exit 2; }
  [ -f "$REPO/$REFERENCE_SET/manifest.json" ] || { echo "no manifest.json in $REPO/$REFERENCE_SET: refusing before any download"; exit 2; }
fi
REFSET_ARGS=(); if [ -n "$REFERENCE_SET" ]; then REFSET_ARGS=(--reference-set "$REPO/$REFERENCE_SET"); fi
STYLE_ANCHOR="${STYLE_ANCHOR:-0}"        # 1 = one style-only anchor reference instead of identity references (config/pilot_sdxl_pins.yaml style_anchor)
case "$STYLE_ANCHOR" in 0|1) ;; *) echo "STYLE_ANCHOR must be 0 or 1"; exit 2;; esac
if [ "$STYLE_ANCHOR" = 1 ]; then REFSET_ARGS+=(--style-anchor); fi
SWEEP_ARGS=(); if [ "$STYLE_SWEEP" = 1 ]; then SWEEP_ARGS=(--style-sweep --sweep-seeds "$SWEEP_SEEDS" --sweep-cfgs "$SWEEP_CFGS"); fi
export PIP_CACHE_DIR="$W/cache/pip" HF_HOME="$W/cache/hf" TORCH_HOME="$W/cache/torch" TMPDIR="$W/cache/tmp"
PUBLISHED=0
publish() { # once, at exit: stop logging (tee flushed), archive, replace any earlier published copy
  [ "$PUBLISHED" = 0 ] || return 0; PUBLISHED=1
  exec >&- 2>&-; [ -z "${TEE_PID:-}" ] || wait "$TEE_PID" 2>/dev/null || true
  (cd "$W" && rm -f "${STAGE}_evidence.tgz" && tar czf "${STAGE}_evidence.tgz" "${STAGE}_evidence") 2>/dev/null || true
  [ -z "${EVIDENCE_DEST:-}" ] || {
    rm -rf "$EVIDENCE_DEST/${STAGE}_evidence" "$EVIDENCE_DEST/${STAGE}_evidence.tgz"
    mkdir -p "$EVIDENCE_DEST/${STAGE}_evidence" && cp -r "$OUT/." "$EVIDENCE_DEST/${STAGE}_evidence/" && cp "$W/${STAGE}_evidence.tgz" "$EVIDENCE_DEST/"
  } 2>/dev/null || true
}
# an earlier success must never survive a refused or failed rerun: invalidate the published copy, the local evidence directory, the archive and the workdir BEFORE anything else
[ -z "${EVIDENCE_DEST:-}" ] || rm -rf "$EVIDENCE_DEST/${STAGE}_evidence" "$EVIDENCE_DEST/${STAGE}_evidence.tgz"
rm -rf "$W/${STAGE}_evidence" "$W/sdxl_work_$VISUAL"; rm -f "$W/${STAGE}_evidence.tgz"
: "${LTX_DOWNLOAD_APPROVED:?set LTX_DOWNLOAD_APPROVED to the approver name (docs/pilot/SDXL_DOWNLOAD_APPROVAL.md)}"
: "${LTX_EXPECTED_COMMIT:?set LTX_EXPECTED_COMMIT to the reviewed GranthStudio commit (full sha)}"
mkdir -p "$OUT" "$W/cache/tmp"; trap publish EXIT; exec > >(tee "$OUT/run_log.txt") 2>&1; TEE_PID=$!
echo "stage $STAGE | approved by: $LTX_DOWNLOAD_APPROVED | $(date -u +%FT%TZ)"

echo "== 0. refusals that need no network"
[ "$(git -C "$REPO" rev-parse HEAD)" = "$LTX_EXPECTED_COMMIT" ] || { echo "GranthStudio is at $(git -C "$REPO" rev-parse HEAD), expected $LTX_EXPECTED_COMMIT"; exit 2; }
[ -z "$(git -C "$REPO" status --porcelain)" ] || { echo "the GranthStudio checkout has local modifications"; exit 2; }
REF="$REPO/assets/ltx_test_inputs/painted_courtyard_01/04_ltx_start_768x512.png"
[ -f "$REF" ] || { echo "reference painting $REF is missing"; exit 2; }
case "$SESSION_MINUTES" in ''|*[!0-9]*) echo "SESSION_MINUTES must be an integer"; exit 2;; esac
{ [ "$SESSION_MINUTES" -ge 30 ] && [ "$SESSION_MINUTES" -le 720 ]; } || { echo "SESSION_MINUTES must be 30..720"; exit 2; }
GRANTHSTUDIO_SESSION_DEADLINE="$(python -c "from datetime import datetime,timedelta,timezone;print((datetime.now(timezone.utc)+timedelta(minutes=$SESSION_MINUTES)).isoformat(timespec='seconds'))")"
export GRANTHSTUDIO_SESSION_DEADLINE; echo "session deadline: $GRANTHSTUDIO_SESSION_DEADLINE"
command -v ffmpeg >/dev/null || { echo "ffmpeg is required"; exit 2; }
mkdir -p "$W"; FREE_GB=$(df -BG --output=avail "$W" | tail -1 | tr -dc 0-9); [ "$FREE_GB" -ge 40 ] || { echo "only ${FREE_GB} GB free in $W, need 40"; exit 2; }
PORT="$(python -c "import socket;s=socket.socket();s.bind(('127.0.0.1',0));print(s.getsockname()[1]);s.close()")"
python -c "import socket,sys;s=socket.socket();s.settimeout(1);sys.exit(0 if s.connect_ex(('127.0.0.1',$PORT)) == 0 else 1)" && { echo "something already listens on port $PORT: refusing"; exit 2; }
echo "port: $PORT"

pin() { python - "$1" "$2" <<'EOF'
import sys, yaml
node = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
for part in sys.argv[2].split("."):
    node = node[int(part)] if part.isdigit() else node[part]
print(node)
EOF
}

echo "== 1. host: two idle Tesla T4, PyTorch sees two sm_75 devices, RAM and disk (this stage uses GPU 0 only)"
nvidia-smi -L | tee "$OUT/nvidia_smi_L.txt"
python "$REPO/scripts/kaggle/host_check.py" --path "$W" --json "$OUT/host_check.json" || { echo "the host is not the planned dual-T4 machine: refusing"; exit 3; }

clone() { # repo commit dir : checked out at the pinned commit and required to be CLEAN before anything from it runs
  [ -d "$3/.git" ] || git clone -q "$1" "$3"
  git -C "$3" checkout -q --detach "$2"
  [ "$(git -C "$3" rev-parse HEAD)" = "$2" ] || { echo "$3 is not at the pinned commit"; exit 4; }
  [ -z "$(git -C "$3" status --porcelain)" ] || { echo "$3 has local modifications: refusing to run unverified code"; exit 4; }
}
echo "== 2. pinned sources: ComfyUI and ComfyUI_IPAdapter_plus"
clone "$(pin "$LTXPINS" sources.comfyui.repo)" "$(pin "$PINS" comfyui.commit)" "$COMFY"
clone "$(pin "$PINS" custom_nodes.0.repo)" "$(pin "$PINS" custom_nodes.0.commit)" "$COMFY/custom_nodes/ComfyUI_IPAdapter_plus"
# ONLY the approved node pack may be present: ComfyUI imports every folder of custom_nodes at startup, so an extra pack could run or override classes
find "$COMFY/custom_nodes" -mindepth 1 -maxdepth 1 -print0 > "$OUT/custom_nodes.list" || { echo "cannot list $COMFY/custom_nodes: refusing"; exit 4; }
while IFS= read -r -d '' entry; do   # find lists EVERY entry, including names that start with one or two dots
  case "$(basename "$entry")" in ComfyUI_IPAdapter_plus|__pycache__|websocket_image_save.py|example_node.py.example|.gitignore) ;; *) echo "unapproved entry in custom_nodes: $entry: refusing"; exit 4;; esac
done < "$OUT/custom_nodes.list"

echo "== 3. python requirements (recorded below)"
[ -f "$COMFY/requirements.txt" ] && pip install -q -r "$COMFY/requirements.txt"
[ -f "$COMFY/custom_nodes/ComfyUI_IPAdapter_plus/requirements.txt" ] && pip install -q -r "$COMFY/custom_nodes/ComfyUI_IPAdapter_plus/requirements.txt" || true
pip freeze > "$OUT/pip_freeze.txt"

echo "== 4. weights (pinned revisions; complete SHA-256 verified)"
fetch() { # index
  local name repo rev path sha size dest; name="$(pin "$PINS" files.$1.name)"; repo="$(pin "$PINS" files.$1.repo)"; rev="$(pin "$PINS" files.$1.revision)"
  path="$(python - "$PINS" "$1" <<'EOF'
import sys, yaml
f = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))["files"][int(sys.argv[2])]
print(f.get("path_in_repo", f["name"]))
EOF
)"
  sha="$(pin "$PINS" files.$1.sha256)"; size="$(pin "$PINS" files.$1.size_bytes)"; dest="$COMFY/$(pin "$PINS" files.$1.dest_dir)"; mkdir -p "$dest"
  [ -f "$dest/$name" ] && [ "$(stat -c %s "$dest/$name")" = "$size" ] || curl -L --fail --retry 5 -C - -o "$dest/$name" "https://huggingface.co/$repo/resolve/$rev/$path"
  echo "$sha  $dest/$name" | sha256sum -c -
}
for i in 0 1 2 3; do fetch "$i"; done

echo "== 5. traces: VRAM of both cards, compute apps, host RAM"
: > "$OUT/vram_trace.csv"; : > "$OUT/apps_trace.csv"; : > "$OUT/ram_trace.txt"
nvidia-smi --query-gpu=timestamp,index,uuid,memory.used --format=csv,noheader,nounits -l 2 > "$OUT/vram_trace.csv" 2>/dev/null &
VRAM_PID=$!
( while true; do
    if apps_out="$(nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader,nounits 2>/dev/null)"; then
      echo "#OK" >> "$OUT/apps_trace.csv"; [ -z "$apps_out" ] || echo "$apps_out" >> "$OUT/apps_trace.csv"
    else echo "#FAIL" >> "$OUT/apps_trace.csv"; fi
    sleep 2
  done ) &
APPS_PID=$!
( while true; do { date -u +%T; free -m | sed -n 2p; } >> "$OUT/ram_trace.txt"; sleep 5; done ) &
RAM_PID=$!
WPID=""
cleanup() { for p in $VRAM_PID $APPS_PID $RAM_PID $WPID; do [ -n "$p" ] && kill "$p" 2>/dev/null || true; done; }
trap 'cleanup; publish' EXIT

echo "== 6. worker on GPU 0 only (GPU 1 stays idle)"
D="$OUT/worker0"; mkdir -p "$D/output" "$D/temp" "$D/input" "$D/user"
LAUNCH=(python main.py --listen 127.0.0.1 --port "$PORT" --disable-auto-launch --output-directory "$D/output" --temp-directory "$D/temp" --input-directory "$D/input" --user-directory "$D/user")
if [ "$COMFY_LOWVRAM" = 1 ]; then LAUNCH+=(--lowvram); fi
if [ "$COMFY_FP16_VAE" = 1 ]; then LAUNCH+=(--fp16-vae); fi
printf 'CUDA_VISIBLE_DEVICES=0 ' > "$D/launch.txt"; printf '%q ' "${LAUNCH[@]}" >> "$D/launch.txt"
( cd "$COMFY" && CUDA_VISIBLE_DEVICES=0 exec "${LAUNCH[@]}" > "$D/comfyui.log" 2>&1 ) &
WPID=$!
READY=0
for _ in $(seq 1 120); do
  kill -0 "$WPID" 2>/dev/null || { echo "worker exited early:"; tail -20 "$D/comfyui.log"; exit 5; }
  if curl -sf "http://127.0.0.1:$PORT/system_stats" > "$D/system_stats.json"; then READY=1; break; fi; sleep 5
done
[ "$READY" = 1 ] || { echo "worker did not come up; see $D/comfyui.log"; exit 5; }
python "$REPO/scripts/kaggle/port_owner.py" "$WPID" "$PORT" --address 127.0.0.1 || { echo "cannot prove the answering server is our worker"; exit 5; }
tr '\0' '\n' < "/proc/$WPID/environ" | grep -qx "CUDA_VISIBLE_DEVICES=0" || { echo "worker does not run with CUDA_VISIBLE_DEVICES=0"; exit 5; }
curl -sf "http://127.0.0.1:$PORT/object_info" > "$D/object_info.json"
python - "$D/system_stats.json" "$OUT/host_check.json" "$D/worker_evidence.json" "$WPID" <<'EOF'
import json, sys
stats = json.load(open(sys.argv[1])); host = json.load(open(sys.argv[2]))
devices = stats.get("devices", [])
if len(devices) != 1:
    sys.exit(f"worker reports {len(devices)} CUDA devices, expected exactly its own one")
card = next(g for g in host["gpus"] if g["index"] == 0)
if abs(devices[0].get("vram_total", 0) / 1048576 - card["memory_total_mb"]) > 0.06 * card["memory_total_mb"]:
    sys.exit("the worker's device does not match physical GPU 0")
print(f"worker: ComfyUI sees one device {devices[0].get('name')!r}, matching physical GPU 0 ({card['uuid']})")
json.dump({"index": 0, "pid": int(sys.argv[4]), "cuda_visible_devices": "0", "visible_devices": 1, "uuid": card["uuid"]}, open(sys.argv[3], "w"))
EOF

echo "== 7. one keyframe (with identity reference) and its no-reference control, through the existing pipeline"
STATUS=0
set +e
python "$REPO/scripts/sdxl_first_test.py" --execute --workdir "$W/sdxl_work_$VISUAL" --models-dir "$COMFY" --comfy-url "http://127.0.0.1:$PORT" --gpu-index 0 --visual "$VISUAL" \
  --reference-image "$REF" --worker-pid "$WPID" --cuda-visible-devices 0 --comfy-log "$D/comfyui.log" "${SWEEP_ARGS[@]}" "${REFSET_ARGS[@]}"
STATUS=$?
set -e

echo "== 8. which card did the work, and did the other stay untouched"
sleep 4
python "$REPO/scripts/kaggle/gpu_attribution.py" --vram-trace "$OUT/vram_trace.csv" --apps-trace "$OUT/apps_trace.csv" --worker "0=$WPID" --worker "1=0:idle" \
  --worker-evidence "$D/worker_evidence.json" --json "$OUT/gpu_attribution.json" || STATUS=1
WORK="$W/sdxl_work_$VISUAL"
mkdir -p "$OUT/receipts"
cp "$WORK/sdxl_receipt.json" "$OUT/receipts/" 2>/dev/null || true
[ -d "$WORK/outputs" ] && cp -r "$WORK/outputs" "$OUT/outputs" 2>/dev/null || true
cp "$WORK"/artifacts/tasks/pending/*.json "$OUT/" 2>/dev/null || true
cp "$WORK"/project/canon/visual_assets.yaml "$OUT/visual_assets.yaml" 2>/dev/null || true
nvidia-smi > "$OUT/nvidia_smi_after.txt" || true
rm -f "$OUT/stage_verdict.json"
if [ "$STATUS" = 0 ] && [ -f "$WORK/sdxl_receipt.json" ]; then   # a final verdict exists only after the client PASS and the per-card attribution both succeeded
  python - "$OUT/stage_verdict.json" "$LTX_EXPECTED_COMMIT" "$STAGE" "$WORK/sdxl_receipt.json" "$STYLE_SWEEP" <<'EOF'
import hashlib, json, sys
out, commit, stage, receipt, sweep = sys.argv[1:]
json.dump({"stage": stage, "verdict": "EXPERIMENT_COMPLETE" if sweep == "1" else "PASS", "commit": commit, "receipts": {receipt: hashlib.sha256(open(receipt, "rb").read()).hexdigest()}}, open(out, "w"), indent=2)
EOF
fi
cleanup; sleep 1
echo "stage $STAGE exit status $STATUS; evidence: $W/${STAGE}_evidence.tgz (archived at exit)"
exit $STATUS
