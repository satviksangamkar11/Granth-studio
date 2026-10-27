"""Bind each final clean shot image (SH_*) to its sha256: the ONLY image ids the renderer may resolve. Usage: build_image_binding.py <final_clean dir> <out.json>"""
import hashlib, json, sys
from pathlib import Path

src, out = Path(sys.argv[1]), Path(sys.argv[2])
if out.exists():
    sys.exit(f"{out} exists; refusing to overwrite")
rows = {p.stem: {"file": p.name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size} for p in sorted(src.glob("SH_*.png"))}
if not rows:
    sys.exit(f"no SH_*.png in {src}")
out.write_text(json.dumps({"source_dir": str(src), "count": len(rows), "images": rows}, indent=1), encoding="utf-8")
print(len(rows), "images bound ->", out)
