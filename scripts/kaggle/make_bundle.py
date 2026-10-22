"""Create the git bundle that is uploaded to Kaggle as a private dataset (no remote exists for this repository).

  python scripts/kaggle/make_bundle.py --out D:/kaggle_upload/granthstudio-bundle

Writes <out>/granthstudio.bundle, <out>/BUNDLE_INFO.json and <out>/dataset-metadata.json (owner/slug are the
Kaggle account shown in docs/KAGGLE_RUNBOOK.md). The bundle holds the branch history, so it carries both the
accepted baseline commit and the newer harness scripts. Nothing is uploaded by this script.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

BASELINE = "f8d5d02f609a68806e8272617d1e04c98cf6040c"
ROOT = Path(__file__).resolve().parents[2]


def git(*args: str) -> str:
    done = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)
    if done.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {done.stderr.strip()}")
    return done.stdout.strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--branch", default="sprint/remaining-pipeline")
    parser.add_argument("--owner", default="sangeetasangamkar")
    parser.add_argument("--slug", default="granthstudio-cpu-baseline")
    args = parser.parse_args(argv)
    if git("status", "--porcelain"):
        raise SystemExit("working tree is not clean; commit or stash first")
    git("cat-file", "-e", f"{BASELINE}^{{commit}}")
    if subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", BASELINE, args.branch]).returncode != 0:
        raise SystemExit(f"{BASELINE} is not an ancestor of {args.branch}")
    args.out.mkdir(parents=True, exist_ok=True)
    bundle = args.out / "granthstudio.bundle"
    git("bundle", "create", str(bundle), args.branch)
    git("bundle", "verify", str(bundle))
    info = {"branch": args.branch, "branch_tip": git("rev-parse", args.branch), "accepted_baseline": BASELINE,
            "bundle_sha256": hashlib.sha256(bundle.read_bytes()).hexdigest(), "bundle_bytes": bundle.stat().st_size}
    (args.out / "BUNDLE_INFO.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
    (args.out / "dataset-metadata.json").write_text(json.dumps(
        {"title": "GranthStudio CPU baseline bundle", "id": f"{args.owner}/{args.slug}",
         "licenses": [{"name": "other"}]}, indent=2), encoding="utf-8")
    print(json.dumps(info, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
