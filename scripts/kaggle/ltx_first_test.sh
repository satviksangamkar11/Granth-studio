#!/usr/bin/env bash
# First real LTX 0.9.8 I2V compatibility test on ONE Kaggle T4 (accelerator: GPU T4 x1, Internet on).
#
#   LTX_DOWNLOAD_APPROVED="<name that signed docs/LTX_098_DOWNLOAD_APPROVAL.md section D>" \
#       bash scripts/kaggle/ltx_first_test.sh
#
# This script DOWNLOADS ~16 GB of weights and runs a GPU job. It refuses to start without the approval variable, without a T4,
# or outside a clone of this repository. Every revision, URL and hash comes from config/ltx_098_pins.yaml (one source of truth);
# nothing is trusted until the bytes on disk match it. The result is test_receipt.json plus an evidence bundle; a PASS means
# one clip decoded through the existing pipeline - the capability remains unvalidated until a human reviews the clip.
set -euo pipefail

: "${LTX_DOWNLOAD_APPROVED:?set LTX_DOWNLOAD_APPROVED to the approver name after signing docs/LTX_098_DOWNLOAD_APPROVAL.md}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
W="${W:-/kaggle/working}"; COMFY="$W/ComfyUI"; OUT="$W/ltx_first_test_evidence"; PINS="$REPO/config/ltx_098_pins.yaml"
mkdir -p "$OUT"; exec > >(tee "$OUT/run_log.txt") 2>&1
echo "approved by: $LTX_DOWNLOAD_APPROVED | repo $(git -C "$REPO" rev-parse HEAD) | $(date -u +%FT%TZ)"

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

clone() { # name dir
  local repo commit; repo="$(pin sources.$1.repo)"; commit="$(pin sources.$1.commit)"
  [ -d "$2/.git" ] || git clone -q "$repo" "$2"
  git -C "$2" checkout -q --detach "$commit"
  [ "$(git -C "$2" rev-parse HEAD)" = "$commit" ] || { echo "$1 is not at the pinned commit"; exit 4; }
}
echo "== 2. pinned sources"
clone comfyui "$COMFY"
clone ltxvideo_nodes "$COMFY/custom_nodes/ComfyUI-LTXVideo"
clone videohelpersuite "$COMFY/custom_nodes/ComfyUI-VideoHelperSuite"
clone kjnodes "$COMFY/custom_nodes/ComfyUI-KJNodes"

echo "== 3. python requirements (versions are NOT pinned by the sources; recorded below)"
for r in "$COMFY/requirements.txt" "$COMFY/custom_nodes/ComfyUI-LTXVideo/requirements.txt" \
         "$COMFY/custom_nodes/ComfyUI-VideoHelperSuite/requirements.txt" "$COMFY/custom_nodes/ComfyUI-KJNodes/requirements.txt"; do
  [ -f "$r" ] && pip install -q -r "$r"
done
pip freeze > "$OUT/pip_freeze.txt"

echo "== 4. weights (pinned revisions, SHA-256 checked)"
fetch() { # index dest_subdir
  local name url sha size dest; name="$(pin files.$1.name)"; sha="$(pin files.$1.sha256)"; size="$(pin files.$1.size_bytes)"
  url="$(pin files.$1.source | sed 's#/blob/#/resolve/#')"; dest="$COMFY/$(pin files.$1.dest_dir)"; mkdir -p "$dest"
  [ -f "$dest/$name" ] && [ "$(stat -c %s "$dest/$name")" = "$size" ] || curl -L --fail --retry 5 -C - -o "$dest/$name" "$url"
  echo "$sha  $dest/$name" | sha256sum -c -
}
fetch 0; fetch 1

echo "== 5. start ComfyUI"
(cd "$COMFY" && nohup python main.py --listen 127.0.0.1 --port 8188 --disable-auto-launch > "$OUT/comfyui.log" 2>&1 &)
for _ in $(seq 1 120); do curl -sf http://127.0.0.1:8188/system_stats > "$OUT/system_stats.json" && break; sleep 5; done
[ -s "$OUT/system_stats.json" ] || { echo "ComfyUI did not come up; see comfyui.log"; exit 5; }
curl -sf http://127.0.0.1:8188/object_info > "$OUT/object_info.json"

OFFICIAL="$COMFY/custom_nodes/ComfyUI-LTXVideo/$(pin workflow.path)"
echo "== 6. the converter must reproduce the committed candidate from the OFFICIAL file and the LIVE node definitions"
python "$REPO/scripts/comfy/ui_to_api.py" build --recipe "$REPO/$(pin workflow.recipe)" --ui "$OFFICIAL" \
       --object-info "$OUT/object_info.json" --out "$OUT/rebuilt_api_workflow.json" | tee "$OUT/converter_report.txt"
python "$REPO/scripts/comfy/ui_to_api.py" compare "$OUT/rebuilt_api_workflow.json" "$REPO/$(pin workflow.api_candidate)"

echo "== 7. first test through the existing pipeline"
set +e
python "$REPO/scripts/ltx_first_test.py" --execute --workdir "$W/ltx_first_test" --models-dir "$COMFY" \
  --official-workflow "$OFFICIAL" --node-inventory "$OUT/object_info.json" \
  --source comfyui="$COMFY" --source ltxvideo_nodes="$COMFY/custom_nodes/ComfyUI-LTXVideo" \
  --source videohelpersuite="$COMFY/custom_nodes/ComfyUI-VideoHelperSuite" --source kjnodes="$COMFY/custom_nodes/ComfyUI-KJNodes"
STATUS=$?
set -e
cp "$W/ltx_first_test/test_receipt.json" "$W/ltx_first_test/pin_report.json" "$OUT/" 2>/dev/null || true
cp "$W"/ltx_first_test/project/artifacts/tasks/adhyay_01/tier1/*/clip.mp4 "$OUT/clip.mp4" 2>/dev/null || true
nvidia-smi > "$OUT/nvidia_smi_after.txt" || true
(cd "$W" && tar czf ltx_first_test_evidence.tgz ltx_first_test_evidence)
echo "first-test exit status $STATUS; evidence: $W/ltx_first_test_evidence.tgz"
exit $STATUS
