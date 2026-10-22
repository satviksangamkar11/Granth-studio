#!/usr/bin/env bash
# First real LTX 0.9.8 I2V compatibility test on ONE Kaggle T4 (accelerator: GPU T4 x1, Internet on).
#
#   LTX_DOWNLOAD_APPROVED="<name that signed docs/LTX_098_DOWNLOAD_APPROVAL.md section E>" \
#   LTX_EXPECTED_COMMIT="<the reviewed GranthStudio commit, full sha>" \
#       bash scripts/kaggle/ltx_first_test.sh
#
# This script DOWNLOADS ~16 GB of weights and runs a GPU job. Everything that can be refused is refused BEFORE the first clone or download:
# missing approval, a GranthStudio checkout that is not the expected commit or is dirty, no/invalid session deadline, no ffmpeg, too little
# disk, no single Tesla T4, a busy ComfyUI port. Every revision, URL and hash comes from config/ltx_098_pins.yaml. A PASS means one clip
# decoded through the existing pipeline - the capability remains unvalidated until a human reviews the clip.
set -euo pipefail

: "${LTX_DOWNLOAD_APPROVED:?set LTX_DOWNLOAD_APPROVED to the approver name after signing docs/LTX_098_DOWNLOAD_APPROVAL.md}"
: "${LTX_EXPECTED_COMMIT:?set LTX_EXPECTED_COMMIT to the reviewed GranthStudio commit (full sha)}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
W="${W:-/kaggle/working}"; COMFY="$W/ComfyUI"; OUT="$W/ltx_first_test_evidence"; PINS="$REPO/config/ltx_098_pins.yaml"
PORT=8188; SESSION_MINUTES="${SESSION_MINUTES:-240}"
mkdir -p "$OUT"; exec > >(tee "$OUT/run_log.txt") 2>&1
echo "approved by: $LTX_DOWNLOAD_APPROVED | $(date -u +%FT%TZ)"

echo "== 0. refusals that need no network"
[ "$(git -C "$REPO" rev-parse HEAD)" = "$LTX_EXPECTED_COMMIT" ] || { echo "GranthStudio is at $(git -C "$REPO" rev-parse HEAD), expected $LTX_EXPECTED_COMMIT"; exit 2; }
[ -z "$(git -C "$REPO" status --porcelain)" ] || { echo "the GranthStudio checkout has local modifications"; exit 2; }
case "$SESSION_MINUTES" in ''|*[!0-9]*) echo "SESSION_MINUTES must be an integer"; exit 2;; esac
{ [ "$SESSION_MINUTES" -ge 30 ] && [ "$SESSION_MINUTES" -le 720 ]; } || { echo "SESSION_MINUTES must be 30..720"; exit 2; }
GRANTHSTUDIO_SESSION_DEADLINE="$(python -c "from datetime import datetime,timedelta,timezone;print((datetime.now(timezone.utc)+timedelta(minutes=$SESSION_MINUTES)).isoformat(timespec='seconds'))")"
export GRANTHSTUDIO_SESSION_DEADLINE; echo "session deadline: $GRANTHSTUDIO_SESSION_DEADLINE"
command -v ffmpeg >/dev/null || { echo "ffmpeg is required (VideoHelperSuite encodes the mp4 with it)"; exit 2; }
mkdir -p "$W"; FREE_GB=$(df -BG --output=avail "$W" | tail -1 | tr -dc 0-9); [ "$FREE_GB" -ge 40 ] || { echo "only ${FREE_GB} GB free in $W, need 40"; exit 2; }
if curl -sf "http://127.0.0.1:$PORT/system_stats" >/dev/null 2>&1; then echo "something already serves port $PORT: refusing to use an unknown ComfyUI"; exit 2; fi

pin() { python - "$PINS" "$1" <<'EOF'
import sys, yaml
doc = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
node = doc
for part in sys.argv[2].split("."):
    node = node[int(part)] if part.isdigit() else node[part]
print(node)
EOF
}

echo "== 1. GPU must be a single T4"
nvidia-smi -L | tee "$OUT/nvidia_smi_L.txt"
nvidia-smi -L | grep -q "Tesla T4" || { echo "no Tesla T4 visible: refusing"; exit 3; }
[ "$(nvidia-smi -L | wc -l)" -eq 1 ] || { echo "expected exactly one GPU: refusing"; exit 3; }

clone() { # name dir  (checked out at the pinned commit and required to be CLEAN before anything from it is installed or run)
  local repo commit; repo="$(pin sources.$1.repo)"; commit="$(pin sources.$1.commit)"
  [ -d "$2/.git" ] || git clone -q "$repo" "$2"
  git -C "$2" checkout -q --detach "$commit"
  [ "$(git -C "$2" rev-parse HEAD)" = "$commit" ] || { echo "$1 is not at the pinned commit"; exit 4; }
  [ -z "$(git -C "$2" status --porcelain)" ] || { echo "$1 has local modifications: refusing to run unverified code"; exit 4; }
}
echo "== 2. pinned sources (ComfyUI-LTXVideo is only the SOURCE of the official workflow file: it is NOT installed into custom_nodes)"
clone comfyui "$COMFY"
clone videohelpersuite "$COMFY/custom_nodes/ComfyUI-VideoHelperSuite"
clone kjnodes "$COMFY/custom_nodes/ComfyUI-KJNodes"
clone ltxvideo_nodes "$W/ComfyUI-LTXVideo-src"

echo "== 3. python requirements of the code that actually runs (versions are NOT pinned by the sources; recorded below)"
for r in "$COMFY/requirements.txt" "$COMFY/custom_nodes/ComfyUI-VideoHelperSuite/requirements.txt" "$COMFY/custom_nodes/ComfyUI-KJNodes/requirements.txt"; do
  [ -f "$r" ] && pip install -q -r "$r"
done
pip freeze > "$OUT/pip_freeze.txt"

echo "== 4. weights (pinned revisions, SHA-256 checked)"
fetch() { # index
  local name url sha size dest; name="$(pin files.$1.name)"; sha="$(pin files.$1.sha256)"; size="$(pin files.$1.size_bytes)"
  url="$(pin files.$1.source | sed 's#/blob/#/resolve/#')"; dest="$COMFY/$(pin files.$1.dest_dir)"; mkdir -p "$dest"
  [ -f "$dest/$name" ] && [ "$(stat -c %s "$dest/$name")" = "$size" ] || curl -L --fail --retry 5 -C - -o "$dest/$name" "$url"
  echo "$sha  $dest/$name" | sha256sum -c -
}
fetch 0; fetch 1

echo "== 5. start ComfyUI (arguments recorded; no precision flags: the dtype ComfyUI chooses for a T4 is part of the evidence)"
LAUNCH="python main.py --listen 127.0.0.1 --port $PORT --disable-auto-launch --output-directory $OUT/comfy_output"; echo "$LAUNCH" > "$OUT/comfyui_launch.txt"
nvidia-smi --query-gpu=timestamp,memory.used,memory.total,utilization.gpu --format=csv -l 2 > "$OUT/vram_trace.csv" 2>/dev/null &
VRAM_PID=$!
cd "$COMFY"; $LAUNCH > "$OUT/comfyui.log" 2>&1 &
COMFY_PID=$!; cd "$REPO"
trap 'kill $VRAM_PID 2>/dev/null || true; kill $COMFY_PID 2>/dev/null || true' EXIT
READY=0
for _ in $(seq 1 120); do
  kill -0 $COMFY_PID 2>/dev/null || { echo "ComfyUI exited early:"; tail -20 "$OUT/comfyui.log"; exit 5; }
  if curl -sf "http://127.0.0.1:$PORT/system_stats" > "$OUT/system_stats.json"; then READY=1; break; fi; sleep 5
done
[ "$READY" = 1 ] || { echo "ComfyUI did not come up; see comfyui.log"; exit 5; }
# the port was free before launch and our process is alive; if the server reports its argv it must carry our unique output directory
if grep -q '"argv"' "$OUT/system_stats.json"; then
  grep -q "$OUT/comfy_output" "$OUT/system_stats.json" || { echo "the server on port $PORT is not the ComfyUI this script launched"; exit 5; }
else
  echo "note: /system_stats did not report argv; identity rests on the free port + live process check"
fi
curl -sf "http://127.0.0.1:$PORT/object_info" > "$OUT/object_info.json"

OFFICIAL="$W/ComfyUI-LTXVideo-src/$(pin workflow.path)"
echo "== 6. the converter must reproduce the committed candidate from the OFFICIAL file and the LIVE node definitions"
python "$REPO/scripts/comfy/ui_to_api.py" build --recipe "$REPO/$(pin workflow.recipe)" --ui "$OFFICIAL" \
       --object-info "$OUT/object_info.json" --out "$OUT/rebuilt_api_workflow.json" | tee "$OUT/converter_report.txt"
python "$REPO/scripts/comfy/ui_to_api.py" compare "$OUT/rebuilt_api_workflow.json" "$REPO/$(pin workflow.api_candidate)"

echo "== 7. first test through the existing pipeline"
set +e
python "$REPO/scripts/ltx_first_test.py" --execute --workdir "$W/ltx_first_test" --models-dir "$COMFY" --precision fp32 \
  --official-workflow "$OFFICIAL" --node-inventory "$OUT/object_info.json" --comfy-log "$OUT/comfyui.log" \
  --source comfyui="$COMFY" --source ltxvideo_nodes="$W/ComfyUI-LTXVideo-src" \
  --source videohelpersuite="$COMFY/custom_nodes/ComfyUI-VideoHelperSuite" --source kjnodes="$COMFY/custom_nodes/ComfyUI-KJNodes"
STATUS=$?
set -e
cp "$W/ltx_first_test/test_receipt.json" "$W/ltx_first_test/pin_report.json" "$OUT/" 2>/dev/null || true
cp "$W"/ltx_first_test/project/artifacts/tasks/adhyay_01/tier1/*/clip.mp4 "$OUT/clip.mp4" 2>/dev/null || true
cp "$W"/ltx_first_test/project/artifacts/tasks/adhyay_01/pending/*.json "$OUT/" 2>/dev/null || true
nvidia-smi > "$OUT/nvidia_smi_after.txt" || true
(cd "$W" && tar czf ltx_first_test_evidence.tgz ltx_first_test_evidence)
echo "first-test exit status $STATUS; evidence: $W/ltx_first_test_evidence.tgz"
exit $STATUS
