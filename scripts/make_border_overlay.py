"""Regenerate canon/overlays/vintage_double_line_border_1080p.png (the proposed static double-line border of the video-safe style).

1920x1080 RGBA, transparent centre, two sepia-brown lines (outer 6 px at a 36 px inset, inner 3 px at a 52 px inset). Deterministic: the same FFmpeg gives the same bytes;
the committed file's SHA-256 is what canon/style.yaml pins, so a different file is refused, never silently used.

  python scripts/make_border_overlay.py [--out PATH]
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILTER = ("drawbox=x=36:y=36:w=1848:h=1008:color=0x5B3A1FFF:t=6:replace=1,"
          "drawbox=x=52:y=52:w=1816:h=976:color=0x5B3A1FFF:t=3:replace=1")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=ROOT / "canon" / "overlays" / "vintage_double_line_border_1080p.png")
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "color=c=black@0.0:s=1920x1080,format=rgba", "-vf", FILTER, "-frames:v", "1", str(args.out)], check=True)
    print(args.out, hashlib.sha256(args.out.read_bytes()).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
