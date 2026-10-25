"""Checks the V5 Phase 1 image inbox: expected files present, image readable, 16:9. Usage: python v5_inbox_check.py [--inbox D:/aai work/v5_inbox]"""
import argparse
from pathlib import Path

from PIL import Image

REFS = {"M1_young_ref", "D1_devotee_ref"}      # character references may be portrait
EXPECTED = ["M1_young_ref", "A1_bg_sky", "A1_mid_temple", "A1_fg_frame", "A1_full", "D1_devotee_ref", "C1_p1_wide", "C1_p2_bow", "C1_p3_bless", "C1_p4_react",
            "C2_p1_offer", "C2_p2_hands", "C2_p3_hold", "FX_light_smoke"]


def check(inbox: Path) -> int:
    bad = 0
    for name in EXPECTED:
        f = inbox / f"{name}.png"
        if not f.exists():
            print("MISSING  ", name)
            bad += 1
            continue
        try:
            w, h = Image.open(f).size
        except Exception as exc:
            print("UNREADABLE", name, type(exc).__name__)
            bad += 1
            continue
        ok = (name in REFS and min(w, h) >= 700) or (abs(w / h - 16 / 9) < 0.02 and w >= 1280)
        print("ok       " if ok else "WRONG SIZE", name, f"{w}x{h}")
        bad += 0 if ok else 1
    extra = sorted(p.name for p in inbox.glob("*") if p.stem not in EXPECTED)
    if extra:
        print("not in list (ignored):", ", ".join(extra))
    print("RESULT:", "all good" if not bad else f"{bad} problem(s)")
    return 0 if not bad else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--inbox", default="D:/aai work/v5_inbox")
    a = ap.parse_args()
    p = Path(a.inbox)
    p.mkdir(parents=True, exist_ok=True)
    raise SystemExit(check(p))
