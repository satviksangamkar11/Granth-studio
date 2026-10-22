#!/usr/bin/env bash
# LTX 0.9.8 I2V compatibility tests on Kaggle "GPU T4 x2" (two NVIDIA Tesla T4), one STAGE per invocation:
#
#   LTX_DOWNLOAD_APPROVED="<name that accepted the licence and signed section E>" \
#   LTX_EXPECTED_COMMIT="<reviewed GranthStudio commit, full sha>" STAGE=gpu0 \
#       bash scripts/kaggle/ltx_first_test.sh
#
#   STAGE=gpu0        one synthetic I2V shot (variant a) on physical GPU 0; GPU 1 must stay idle            (always first)
#   STAGE=gpu1        a DIFFERENT shot (variant b) on GPU 1; GPU 0 must stay idle                           (needs gpu0 PASS)
#   STAGE=concurrent  both workers at once on two distinct shots, fresh projects                            (needs gpu0 and gpu1 PASS)
#   STAGE=retry       controlled output-rejection on GPU 0: the sampler must execute again on a changed seed (needs gpu0 PASS)
#
# Two independent workers, never a pooled 32 GB: each is its own ComfyUI process (CUDA_VISIBLE_DEVICES=<index>, own port, own output/temp/input/user
# directories) with its own GranthStudio project, journal, token and submission namespace. Checkpoint FILES are shared on disk read-only.
# Everything that can be refused is refused BEFORE the first clone or download: missing approval, wrong commit, dirty tree, bad session deadline,
# no ffmpeg, little disk, not exactly two idle Tesla T4 with matching PyTorch/CUDA, an unmet stage prerequisite, a busy port. One attempt per
# invocation; a CUDA out-of-memory error stops the stage (no retry, no alternative configuration). A PASS means decoded clip(s) through the existing
# pipeline plus per-card attribution; the capability stays unvalidated until a human reviews the clips.
set -euo pipefail

: "${LTX_DOWNLOAD_APPROVED:?set LTX_DOWNLOAD_APPROVED to the approver name after signing docs/LTX_098_DOWNLOAD_APPROVAL.md}"
: "${LTX_EXPECTED_COMMIT:?set LTX_EXPECTED_COMMIT to the reviewed GranthStudio commit (full sha)}"
STAGE="${STAGE:-gpu0}"
case "$STAGE" in gpu0|gpu1|concurrent|retry) ;; *) echo "STAGE must be gpu0, gpu1, concurrent or retry"; exit 2;; esac
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
W="${W:-/kaggle/working}"; COMFY="$W/ComfyUI"; OUT="$W/ltx_evidence_$STAGE"; PINS="$REPO/config/ltx_098_pins.yaml"
SESSION_MINUTES="${SESSION_MINUTES:-240}"
mkdir -p "$OUT"; exec > >(tee "$OUT/run_log.txt") 2>&1
echo "stage $STAGE | approved by: $LTX_DOWNLOAD_APPROVED | $(date -u +%FT%TZ)"

echo "== 0. refusals that need no network"
[ "$(git -C "$REPO" rev-parse HEAD)" = "$LTX_EXPECTED_COMMIT" ] || { echo "GranthStudio is at $(git -C "$REPO" rev-parse HEAD), expected $LTX_EXPECTED_COMMIT"; exit 2; }
[ -z "$(git -C "$REPO" status --porcelain)" ] || { echo "the GranthStudio checkout has local modifications"; exit 2; }
case "$SESSION_MINUTES" in ''|*[!0-9]*) echo "SESSION_MINUTES must be an integer"; exit 2;; esac
{ [ "$SESSION_MINUTES" -ge 30 ] && [ "$SESSION_MINUTES" -le 720 ]; } || { echo "SESSION_MINUTES must be 30..720"; exit 2; }
GRANTHSTUDIO_SESSION_DEADLINE="$(python -c "from datetime import datetime,timedelta,timezone;print((datetime.now(timezone.utc)+timedelta(minutes=$SESSION_MINUTES)).isoformat(timespec='seconds'))")"
export GRANTHSTUDIO_SESSION_DEADLINE; echo "session deadline: $GRANTHSTUDIO_SESSION_DEADLINE"
command -v ffmpeg >/dev/null || { echo "ffmpeg is required (VideoHelperSuite encodes the mp4 with it)"; exit 2; }
mkdir -p "$W"; FREE_GB=$(df -BG --output=avail "$W" | tail -1 | tr -dc 0-9); [ "$FREE_GB" -ge 40 ] || { echo "only ${FREE_GB} GB free in $W, need 40"; exit 2; }
freeport() { python -c "import socket;s=socket.socket();s.bind(('127.0.0.1',0));print(s.getsockname()[1]);s.close()"; }
PORT0="$(freeport)"; PORT1="$(freeport)"
[ "$PORT0" != "$PORT1" ] || PORT1="$(freeport)"
for P in $PORT0 $PORT1; do
  python -c "import socket,sys;s=socket.socket();s.settimeout(1);sys.exit(0 if s.connect_ex(('127.0.0.1',$P)) == 0 else 1)" && { echo "something already listens on port $P: refusing"; exit 2; }
done
echo "fresh ports: worker0 $PORT0, worker1 $PORT1"
receipt_verdict() { python -c "import json,sys;print(json.load(open(sys.argv[1])).get('verdict'))" "$1" 2>/dev/null || echo MISSING; }
need_pass() { # label receipt
  [ "$(receipt_verdict "$2")" = "PASS" ] || { echo "stage prerequisite not met: $1 has no PASS receipt at $2"; exit 2; }
  python -c "import json,sys;r=json.load(open(sys.argv[1]));sys.exit(0 if r.get('harness_commit')==sys.argv[2] else 1)" "$2" "$LTX_EXPECTED_COMMIT" \
    || { echo "$1 was recorded by a different GranthStudio commit: rerun it on $LTX_EXPECTED_COMMIT"; exit 2; }
}
case "$STAGE" in
  gpu1) need_pass "stage gpu0" "$W/ltx_gpu0/test_receipt.json";;
  concurrent) need_pass "stage gpu0" "$W/ltx_gpu0/test_receipt.json"; need_pass "stage gpu1" "$W/ltx_gpu1/test_receipt.json";;
  retry) need_pass "stage gpu0" "$W/ltx_gpu0/test_receipt.json";;
esac

pin() { python - "$PINS" "$1" <<'EOF'
import sys, yaml
doc = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
node = doc
for part in sys.argv[2].split("."):
    node = node[int(part)] if part.isdigit() else node[part]
print(node)
EOF
}

echo "== 1. host: exactly two idle Tesla T4 (indices 0 and 1), PyTorch sees two sm_75 devices, RAM and disk"
nvidia-smi -L | tee "$OUT/nvidia_smi_L.txt"
python "$REPO/scripts/kaggle/host_check.py" --path "$W" --json "$OUT/host_check.json" || { echo "the host is not the planned dual-T4 machine: refusing"; exit 3; }

clone() { # name dir  (checked out at the pinned commit and required to be CLEAN before anything from it is installed or run)
  local repo commit; repo="$(pin sources.$1.repo)"; commit="$(pin sources.$1.commit)"
  [ -d "$2/.git" ] || git clone -q "$repo" "$2"
  git -C "$2" checkout -q --detach "$commit"
  [ "$(git -C "$2" rev-parse HEAD)" = "$commit" ] || { echo "$1 is not at the pinned commit"; exit 4; }
  [ -z "$(git -C "$2" status --porcelain)" ] || { echo "$1 has local modifications: refusing to run unverified code"; exit 4; }
}
echo "== 2. pinned sources (ComfyUI-LTXVideo is only the SOURCE of the official workflow file: it is NOT installed into custom_nodes)"
[ ! -e "$COMFY/custom_nodes/ComfyUI-LTXVideo" ] || { echo "legacy $COMFY/custom_nodes/ComfyUI-LTXVideo exists; this plan installs no LTXVideo node pack: remove it (or use a fresh workspace)"; exit 4; }
clone comfyui "$COMFY"
clone videohelpersuite "$COMFY/custom_nodes/ComfyUI-VideoHelperSuite"
clone kjnodes "$COMFY/custom_nodes/ComfyUI-KJNodes"
clone ltxvideo_nodes "$W/ComfyUI-LTXVideo-src"

echo "== 3. python requirements of the code that actually runs (versions are NOT pinned by the sources; recorded below)"
for r in "$COMFY/requirements.txt" "$COMFY/custom_nodes/ComfyUI-VideoHelperSuite/requirements.txt" "$COMFY/custom_nodes/ComfyUI-KJNodes/requirements.txt"; do
  [ -f "$r" ] && pip install -q -r "$r"
done
pip freeze > "$OUT/pip_freeze.txt"

echo "== 4. weights (pinned revisions, complete SHA-256 verified every stage)"
fetch() { # index
  local name url sha size dest; name="$(pin files.$1.name)"; sha="$(pin files.$1.sha256)"; size="$(pin files.$1.size_bytes)"
  url="$(pin files.$1.source | sed 's#/blob/#/resolve/#')"; dest="$COMFY/$(pin files.$1.dest_dir)"; mkdir -p "$dest"
  [ -f "$dest/$name" ] && [ "$(stat -c %s "$dest/$name")" = "$size" ] || curl -L --fail --retry 5 -C - -o "$dest/$name" "$url"
  echo "$sha  $dest/$name" | sha256sum -c -
}
fetch 0; fetch 1

echo "== 5. traces: VRAM of BOTH cards, compute apps per card, host RAM"
nvidia-smi --query-gpu=timestamp,index,uuid,memory.used --format=csv,noheader,nounits -l 2 > "$OUT/vram_trace.csv" 2>/dev/null &
VRAM_PID=$!
( while true; do nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader,nounits >> "$OUT/apps_trace.csv" 2>/dev/null; sleep 2; done ) &
APPS_PID=$!
( while true; do { date -u +%T; free -m | sed -n 2p; } >> "$OUT/ram_trace.txt"; sleep 5; done ) &
RAM_PID=$!
declare -A WPID
cleanup() { for p in $VRAM_PID $APPS_PID $RAM_PID "${WPID[@]:-}"; do [ -n "$p" ] && kill "$p" 2>/dev/null || true; done; }
trap cleanup EXIT

start_worker() { # index port : one ComfyUI process that can see ONLY that physical card, with its own directories
  local n="$1" port="$2" d="$OUT/worker$1"
  mkdir -p "$d/output" "$d/temp" "$d/input" "$d/user"
  local launch=(python main.py --listen 127.0.0.1 --port "$port" --disable-auto-launch --output-directory "$d/output" --temp-directory "$d/temp"
                --input-directory "$d/input" --user-directory "$d/user")
  printf 'CUDA_VISIBLE_DEVICES=%s ' "$n" > "$d/launch.txt"; printf '%q ' "${launch[@]}" >> "$d/launch.txt"
  ( cd "$COMFY" && CUDA_VISIBLE_DEVICES="$n" "${launch[@]}" > "$d/comfyui.log" 2>&1 ) &
  WPID[$n]=$!
  local ready=0
  for _ in $(seq 1 120); do
    kill -0 "${WPID[$n]}" 2>/dev/null || { echo "worker $n exited early:"; tail -20 "$d/comfyui.log"; exit 5; }
    if curl -sf "http://127.0.0.1:$port/system_stats" > "$d/system_stats.json"; then ready=1; break; fi; sleep 5
  done
  [ "$ready" = 1 ] || { echo "worker $n did not come up; see $d/comfyui.log"; exit 5; }
  # mandatory proof (Linux /proc, no extra tools): this worker's process holds the listening socket, and it really runs with only its card visible
  python "$REPO/scripts/kaggle/port_owner.py" "${WPID[$n]}" "$port" || { echo "cannot prove the answering server is worker $n"; exit 5; }
  tr '\0' '\n' < "/proc/${WPID[$n]}/environ" | grep -qx "CUDA_VISIBLE_DEVICES=$n" || { echo "worker $n does not run with CUDA_VISIBLE_DEVICES=$n"; exit 5; }
  curl -sf "http://127.0.0.1:$port/object_info" > "$d/object_info.json"
  python - "$d/system_stats.json" "$n" "$OUT/host_check.json" <<'EOF'
import json, sys
stats = json.load(open(sys.argv[1])); host = json.load(open(sys.argv[3])); n = int(sys.argv[2])
devices = stats.get("devices", [])
if len(devices) != 1:
    sys.exit(f"worker {n} reports {len(devices)} CUDA devices, expected exactly its own one")
card = next(g for g in host["gpus"] if g["index"] == n)
if abs(devices[0].get("vram_total", 0) / 1048576 - card["memory_total_mb"]) > 0.06 * card["memory_total_mb"]:
    sys.exit(f"worker {n}'s device reports {devices[0].get('vram_total')} bytes, physical card {n} has {card['memory_total_mb']} MiB")
print(f"worker {n}: ComfyUI sees one device {devices[0].get('name')!r}, matching physical GPU {n} ({card['uuid']})")
EOF
}

OFFICIAL="$W/ComfyUI-LTXVideo-src/$(pin workflow.path)"
rebuild_check() { # worker : the converter must reproduce the committed candidate from the OFFICIAL file and that worker's LIVE node definitions
  python "$REPO/scripts/comfy/ui_to_api.py" build --recipe "$REPO/$(pin workflow.recipe)" --ui "$OFFICIAL" \
         --object-info "$OUT/worker$1/object_info.json" --out "$OUT/worker$1/rebuilt_api_workflow.json" | tee "$OUT/worker$1/converter_report.txt"
  python "$REPO/scripts/comfy/ui_to_api.py" compare "$OUT/worker$1/rebuilt_api_workflow.json" "$REPO/$(pin workflow.api_candidate)"
}
client() { # index variant workdir extra-args... : GranthStudio's existing pipeline against that worker only
  local n="$1" variant="$2" workdir="$3"; shift 3
  local port=$PORT0; [ "$n" = 1 ] && port=$PORT1
  python "$REPO/scripts/ltx_first_test.py" --execute --workdir "$workdir" --models-dir "$COMFY" --precision fp32 --gpu-index "$n" --variant "$variant" \
    --comfy-url "http://127.0.0.1:$port" --worker-pid "${WPID[$n]}" --cuda-visible-devices "$n" --comfy-log "$OUT/worker$n/comfyui.log" \
    --official-workflow "$OFFICIAL" --node-inventory "$OUT/worker$n/object_info.json" \
    --source comfyui="$COMFY" --source ltxvideo_nodes="$W/ComfyUI-LTXVideo-src" \
    --source videohelpersuite="$COMFY/custom_nodes/ComfyUI-VideoHelperSuite" --source kjnodes="$COMFY/custom_nodes/ComfyUI-KJNodes" "$@"
}

STATUS=0
case "$STAGE" in
  gpu0|retry)
    echo "== 6. worker 0 (GPU 1 stays idle)"; start_worker 0 "$PORT0"; echo "== 7. live compatibility"; rebuild_check 0
    if [ "$STAGE" = gpu0 ]; then
      echo "== 8. one synthetic I2V shot on GPU 0"; set +e; client 0 a "$W/ltx_gpu0"; STATUS=$?; set -e; RECEIPT="$W/ltx_gpu0/test_receipt.json"
    else
      echo "== 8. controlled output-rejection test on GPU 0"; set +e; client 0 a "$W/ltx_gpu0" --retry-test; STATUS=$?; set -e; RECEIPT="$W/ltx_gpu0/retry_receipt.json"
    fi
    WORKERS="--worker 0=${WPID[0]} --worker 1=0:idle";;
  gpu1)
    echo "== 6. worker 1 (GPU 0 stays idle)"; start_worker 1 "$PORT1"; echo "== 7. live compatibility"; rebuild_check 1
    echo "== 8. a different synthetic I2V shot on GPU 1"; set +e; client 1 b "$W/ltx_gpu1"; STATUS=$?; set -e; RECEIPT="$W/ltx_gpu1/test_receipt.json"
    WORKERS="--worker 1=${WPID[1]} --worker 0=0:idle";;
  concurrent)
    echo "== 6. both workers"; start_worker 0 "$PORT0"; start_worker 1 "$PORT1"; echo "== 7. live compatibility"; rebuild_check 0; rebuild_check 1
    echo "== 8. two distinct shots at the same time (fresh projects, other card allowed busy)"
    rm -rf "$W/ltx_conc0" "$W/ltx_conc1"
    set +e
    client 0 a "$W/ltx_conc0" --allow-other-gpu-busy & C0=$!
    client 1 b "$W/ltx_conc1" --allow-other-gpu-busy & C1=$!
    wait $C0; S0=$?; wait $C1; S1=$?
    set -e
    STATUS=$(( S0 != 0 || S1 != 0 ))
    python "$REPO/scripts/kaggle/concurrent_check.py" --receipt0 "$W/ltx_conc0/test_receipt.json" --receipt1 "$W/ltx_conc1/test_receipt.json" \
      --json "$OUT/concurrent_check.json" || STATUS=1
    RECEIPT="$W/ltx_conc0/test_receipt.json"
    WORKERS="--worker 0=${WPID[0]} --worker 1=${WPID[1]}";;
esac

echo "== 9. which physical card did the work, and did the other stay untouched"
sleep 4
# shellcheck disable=SC2086
python "$REPO/scripts/kaggle/gpu_attribution.py" --vram-trace "$OUT/vram_trace.csv" --apps-trace "$OUT/apps_trace.csv" $WORKERS --json "$OUT/gpu_attribution.json" || STATUS=1

mkdir -p "$OUT/receipts"
for r in "$W"/ltx_gpu0/*.json "$W"/ltx_gpu1/*.json "$W"/ltx_conc0/*.json "$W"/ltx_conc1/*.json; do
  [ -f "$r" ] && cp "$r" "$OUT/receipts/$(basename "$(dirname "$r")")_$(basename "$r")" 2>/dev/null || true
done
for d in gpu0 gpu1 conc0 conc1; do
  cp "$W"/ltx_$d/project/artifacts/tasks/adhyay_01/tier1/*/clip.mp4 "$OUT/clip_$d.mp4" 2>/dev/null || true
  cp "$W"/ltx_$d/project/artifacts/tasks/adhyay_01/pending/*.json "$OUT/journal_$d.json" 2>/dev/null || true
done
nvidia-smi > "$OUT/nvidia_smi_after.txt" || true
cleanup; trap - EXIT; sleep 1
(cd "$W" && tar czf "ltx_evidence_$STAGE.tgz" "ltx_evidence_$STAGE")
echo "stage $STAGE exit status $STATUS; evidence: $W/ltx_evidence_$STAGE.tgz"
exit $STATUS
