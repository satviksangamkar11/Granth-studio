"""Files a Flow 2K download (a .tmp in Downloads) into the GranthStudio structure and logs it. usage: file_flow_download.py <tmp path> <IMAGE_ID> <vNN> <flow edit id> <references joined by |> <notes>"""
import datetime
import os
import hashlib
import json
import shutil
import struct
import sys
from pathlib import Path

from PIL import Image

src, iid, ver, edit, refs, notes = sys.argv[1:7]
sub = sys.argv[7] if len(sys.argv) > 7 else "references"
root = Path("D:/aai work/flow_outputs/adhyay_01")
d = Path(src).read_bytes()
assert d[:2] == b"\xff\xd8" and d[-2:] == b"\xff\xd9", "not a complete JPEG"
jpg, png = root / sub / f"{iid}__candidate_{ver}__2K_source.jpg", root / sub / f"{iid}__candidate_{ver}.png"
assert not jpg.exists() and not png.exists(), "refusing to overwrite"
new_sha = hashlib.sha256(d).hexdigest()
for old in root.rglob("*__2K_source.jpg"):
    assert hashlib.sha256(old.read_bytes()).hexdigest() != new_sha, f"this file is identical to {old.name}: the new download has not arrived yet"
import time
assert time.time() - Path(src).stat().st_mtime < 300, "the .tmp is older than 5 minutes: it is not the download you just made"
_probe = Image.open(src)
assert _probe.size == (2752, 1536), f"not 2K: {_probe.size}"          # validate BEFORE copying: no partial filing
_probe.close()
shutil.copy2(src, jpg)
im = Image.open(jpg)
try:
    im.save(png)
except Exception:
    jpg.unlink(missing_ok=True)
    png.unlink(missing_ok=True)
    raise
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
cat = {x["image_id"]: x for x in json.loads(Path("D:/aai work/granthstudio/canon/drafts/A1_image_catalog_v2_DRAFT.json").read_text(encoding="utf-8"))}
rec = {"time": datetime.datetime.now().astimezone().isoformat(), "image_id": iid, "version": ver, "file": str(png), "source_jpg": str(jpg), "pixel_width": im.size[0], "pixel_height": im.size[1],
       "sha256_jpg": sha(jpg), "sha256_png": sha(png), "model_shown": os.environ.get("FLOW_MODEL", "unknown (set FLOW_MODEL)"), "credits_shown": os.environ.get("FLOW_CREDITS", "unknown (set FLOW_CREDITS)"), "references_attached": refs.split("|"),
       "prompt_sha256": hashlib.sha256(cat[iid]["prompt"].encode()).hexdigest() if iid in cat else None, "flow_project": "GranthStudio 31b2d7e8-5ad8-41ba-a878-50860b49a03e", "flow_tile_url_or_id": edit,
       "download": "Flow Download media -> 2K Upscaled (built-in browser leaves it as a .tmp in Downloads)", "operator": "claude", "status": "candidate, not accepted", "notes": notes}
with open(root / "flow_log.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
print("filed", iid, ver, im.size, rec["sha256_jpg"][:12])
