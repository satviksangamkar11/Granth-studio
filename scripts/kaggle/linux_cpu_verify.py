"""Run the accepted GranthStudio CPU baseline on Linux and write an evidence bundle.

CPU only: nothing here touches a GPU, downloads a model or starts ComfyUI. The script never states that Linux
verification passed unless it ran on a POSIX host and every required test PASSED (not skipped); it labels
whether the host looks like Kaggle. Usage (from the notebook, or by hand on any Linux box):

  python linux_cpu_verify.py --repo /kaggle/working/granthstudio --harness-dir /kaggle/working/harness \
      --baseline f8d5d02f609a68806e8272617d1e04c98cf6040c --out /kaggle/working/linux_cpu_evidence
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

BASELINE = "f8d5d02f609a68806e8272617d1e04c98cf6040c"
# Must PASS (not skip) on Linux; each exercises a POSIX-only path of the baseline.
REQUIRED = [
    "tests/test_ltx_integration.py::test_live_owner_is_never_displaced_by_a_second_real_process",
    "tests/test_ltx_integration.py::test_owner_crash_before_and_after_post_is_recoverable_without_duplicates",
    "tests/test_ltx_integration.py::test_journal_write_failure_before_post_submits_nothing",
    "tests/test_ltx_integration.py::test_threads_in_one_process_also_submit_exactly_once",
    "tests/test_keyframes.py::test_posix_parent_swap_never_touches_an_outside_sentinel",
    "tests/test_keyframes.py::test_symlinked_asset_dir_cannot_escape",
    "tests/test_keyframes.py::test_redirected_references_root_is_refused_without_writes",
    "tests/test_keyframes.py::test_nested_link_and_existing_destination_are_refused_and_untouched",
    "tests/test_keyframes.py::test_junction_planted_before_mkdir_creates_nothing_outside",
    "tests/test_keyframes.py::test_ancestor_swapped_between_pinning_and_open_cannot_redirect_the_write",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def sh(cmd: list[str], cwd: Path | None = None, env: dict | None = None, log: Path | None = None) -> int:
    handle = log.open("a", encoding="utf-8") if log else None
    try:
        done = subprocess.run(cmd, cwd=cwd, env=env, stdout=handle or subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return done.returncode
    finally:
        if handle:
            handle.close()


def output(cmd: list[str], cwd: Path | None = None) -> str:
    try:
        done = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=120)
        return (done.stdout + done.stderr).strip()
    except (OSError, subprocess.SubprocessError) as exc:
        return f"unavailable: {exc}"


def environment() -> dict:
    kaggle = bool(os.environ.get("KAGGLE_KERNEL_RUN_TYPE") or os.environ.get("KAGGLE_URL_BASE") or Path("/kaggle/working").exists())
    return {
        "utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "looks_like_kaggle": kaggle,
        "kaggle_env": {k: os.environ[k] for k in ("KAGGLE_KERNEL_RUN_TYPE", "KAGGLE_DOCKER_IMAGE") if k in os.environ},
        "platform": platform.platform(), "system": platform.system(), "machine": platform.machine(),
        "kernel": output(["uname", "-a"]) if os.name == "posix" else "n/a",
        "python": sys.version, "python_executable": sys.executable,
        "uid": os.getuid() if hasattr(os, "getuid") else None,
        "cpu_count": os.cpu_count(),
        "git": output(["git", "--version"]), "ffmpeg": output(["ffmpeg", "-version"]).splitlines()[:1],
        "ffprobe": output(["ffprobe", "-version"]).splitlines()[:1],
        "gpu_visible": output(["nvidia-smi", "-L"]) if shutil.which("nvidia-smi") else "no nvidia-smi (CPU session)",
        "filesystem": output(["df", "-T", "."]) if os.name == "posix" else "n/a",
        "memory": output(["free", "-m"]) if os.name == "posix" else "n/a",
    }


def parse_junit(path: Path) -> list[dict]:
    rows = []
    for case in ET.parse(path).getroot().iter("testcase"):
        outcome, detail = "passed", ""
        for child in case:
            if child.tag in ("failure", "error", "skipped"):
                outcome = {"failure": "failed", "error": "error", "skipped": "skipped"}[child.tag]
                detail = (child.get("message") or "")[:300]
        cls = case.get("classname", "").replace(".", "/")
        rows.append({"id": f"{cls}.py::{case.get('name')}", "outcome": outcome, "detail": detail})
    return rows


def evaluate(full: list[dict], supplementary: list[dict], required: list[str], posix: bool, kaggle: bool) -> dict:
    by_id = {r["id"]: r for r in full}
    counts = {k: sum(1 for r in full if r["outcome"] == k) for k in ("passed", "failed", "error", "skipped")}
    required_status = {rid: by_id.get(rid, {"outcome": "not_collected"})["outcome"] for rid in required}
    supp = {r["id"]: r["outcome"] for r in supplementary}
    problems = []
    if counts["failed"] or counts["error"]:
        problems.append(f"{counts['failed']} failed, {counts['error']} errors in the full suite")
    problems += [f"required test {rid} was {st}" for rid, st in required_status.items() if st != "passed"]
    problems += [f"supplementary test {tid} was {st}" for tid, st in supp.items() if st != "passed"]
    if not supplementary:
        problems.append("supplementary POSIX tests produced no results")
    if not posix:
        verdict = "INCOMPLETE_NOT_LINUX"
    elif problems:
        verdict = "LINUX_CPU_FAIL"
    else:
        verdict = "LINUX_CPU_PASS_ON_KAGGLE" if kaggle else "LINUX_CPU_PASS_NON_KAGGLE_HOST"
    return {"verdict": verdict, "problems": problems, "counts": counts, "required": required_status,
            "supplementary": supp, "skipped": [{"id": r["id"], "reason": r["detail"]} for r in full if r["outcome"] == "skipped"]}


def ensure_dependencies(log: Path) -> list[str]:
    installed = []
    for module, package in (("yaml", "pyyaml"), ("jsonschema", "jsonschema"), ("pytest", "pytest")):
        try:
            __import__(module)
        except ImportError:
            if sh([sys.executable, "-m", "pip", "install", "-q", package], log=log) != 0:
                raise SystemExit(f"cannot install {package} (is Internet enabled for this session?)")
            installed.append(package)
    return installed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--harness-dir", required=True, type=Path, help="folder holding posix_primitives_tests.py")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--baseline", default=BASELINE)
    parser.add_argument("--harness-sha", default="unknown")
    args = parser.parse_args(argv)
    out = args.out; out.mkdir(parents=True, exist_ok=True)
    log = out / "full_log.txt"; log.write_text("", encoding="utf-8")
    env_info = environment()
    receipt: dict = {"schema_version": 1, "environment": env_info, "baseline_expected": args.baseline, "harness_commit": args.harness_sha,
                     "scope": "CPU only; no GPU, model or ComfyUI was used"}

    def finish(verdict: str, reason: str = "") -> int:
        receipt["verdict"] = verdict
        if reason:
            receipt["reason"] = reason
        receipt["artifacts"] = {p.name: sha256_file(p) for p in sorted(out.iterdir()) if p.is_file() and p.name not in ("receipt.json",)}
        (out / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
        shutil.make_archive(str(out), "zip", out)
        print(f"VERDICT: {verdict} {reason}\nevidence: {out} and {out}.zip")
        return 0 if verdict.startswith("LINUX_CPU_PASS") else 1

    (out / "environment.json").write_text(json.dumps(env_info, indent=2), encoding="utf-8")
    head = output(["git", "rev-parse", "HEAD"], args.repo)
    receipt["source_commit"] = head
    if head != args.baseline:
        return finish("NOT_RUN_WRONG_COMMIT", f"repo HEAD {head} != accepted baseline {args.baseline}")
    if output(["git", "status", "--porcelain"], args.repo):
        return finish("NOT_RUN_DIRTY_TREE", "the checkout has local modifications")
    arch = args.repo / "docs" / "ARCHITECTURE_V3_1.md"
    freeze = json.loads((args.repo / "docs" / "ARCHITECTURE_V3_1.FREEZE.json").read_text(encoding="utf-8"))["sha256"]
    receipt["architecture_sha256"] = sha256_file(arch); receipt["architecture_frozen_sha256"] = freeze
    if receipt["architecture_sha256"] != freeze:
        return finish("NOT_RUN_ARCHITECTURE_CHANGED", "docs/ARCHITECTURE_V3_1.md differs from the frozen hash")
    if sys.version_info < (3, 12):
        return finish("NOT_RUN_PYTHON_TOO_OLD", f"pyproject requires Python >= 3.12, this is {sys.version.split()[0]}")
    try:
        receipt["dependencies_installed_by_this_run"] = ensure_dependencies(log)
    except SystemExit as exc:
        return finish("NOT_RUN_DEPENDENCIES", str(exc))
    env = {**os.environ, "PYTHONPATH": str(args.repo / "src"), "PYTHONDONTWRITEBYTECODE": "1"}
    for name in ("junit_full.xml", "junit_supplementary.xml"):
        (out / name).unlink(missing_ok=True)
    sh([sys.executable, "-m", "pytest", "-q", "-rs", "-p", "no:cacheprovider", f"--junitxml={out / 'junit_full.xml'}"], args.repo, env, log)
    supp_file = args.harness_dir / "posix_primitives_tests.py"
    sh([sys.executable, "-m", "pytest", "-q", "-rs", "-p", "no:cacheprovider", str(supp_file), f"--junitxml={out / 'junit_supplementary.xml'}"],
       args.repo, env, log)
    if not (out / "junit_full.xml").is_file():
        return finish("LINUX_CPU_FAIL", "the full suite produced no JUnit file; see full_log.txt")
    full = parse_junit(out / "junit_full.xml")
    supp = parse_junit(out / "junit_supplementary.xml") if (out / "junit_supplementary.xml").is_file() else []
    receipt["evaluation"] = evaluate(full, supp, REQUIRED, os.name == "posix", env_info["looks_like_kaggle"])
    receipt["pip_freeze"] = output([sys.executable, "-m", "pip", "freeze"]).splitlines()
    verdict = receipt["evaluation"]["verdict"]
    return finish(verdict, "; ".join(receipt["evaluation"]["problems"][:5]))


if __name__ == "__main__":
    sys.exit(main())
