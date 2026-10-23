"""IndicTrans2 Marathi -> Hindi translation test for the PROVISIONAL 45-second pilot, through GranthStudio's existing translation code.

  python scripts/audio_translate_test.py --workdir W --out OUT --execute

The provisional pilot project is built under WORKDIR/project; translation.generate_candidates runs scripts/runners/indictrans2_runner.py (model identity must prove the pinned
revision) over the pilot's Marathi narration lines. The receipt lists, per line, the Marathi text, the model's Hindi candidate, the assistant's Hindi draft and the deterministic
protected-term/numeric checks. A PASS means the model ran and produced one non-empty candidate per line: correctness of the Hindi is judged by the human reviewer, never by this script.
For this run only, the temporary project's models.yaml sets translation.status 'validated' so the existing gate lets the run proceed; the repository keeps 'unvalidated'.
The Hugging Face token is read by the runner from the HF_TOKEN environment variable and is never written to any file or log.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

MODEL, REVISION = "ai4bharat/indictrans2-indic-indic-1B", "24d732922a0a91d0998d5568e3af37b7a21cd705"   # public metadata, 2026-10-23
RUNNER = ROOT / "scripts" / "runners" / "indictrans2_runner.py"
OWNER_NOTE = "provisional technical test; owner instruction 2026-10-23"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


bp = _load("build_pilot_project", ROOT / "scripts" / "pilot" / "build_pilot_project.py")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--workdir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--expected-commit", help="refuse to run unless the checkout is exactly this clean commit (required with --execute)")
    return parser


def prepare(workdir: Path):
    """Build the pilot project and the run-only models dict (translation 'validated' lives in memory only, never on disk)."""
    from granthstudio.config import load_models, load_project
    if (workdir / "project").exists():
        raise RuntimeError("the workdir already holds a project: a fresh --workdir is required")
    if workdir.resolve().is_relative_to(ROOT.resolve()):
        raise RuntimeError("the workdir must be outside the repository")
    root = bp.build(workdir / "project")
    artifacts = workdir / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    config = yaml.safe_load((root / "config" / "project.yaml").read_text(encoding="utf-8"))
    config["artifacts_dir"] = str(artifacts)
    (root / "config" / "project.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    project = load_project(root)
    models = load_models(project)
    models["translation"].update(status="validated", command=[sys.executable, str(RUNNER)], model=MODEL, revision=REVISION, timeout_s=3000)
    return project, models


def contaminated(text: str) -> bool:
    token = os.environ.get("HF_TOKEN", "").strip()
    return bool(re.search(r"hf_[A-Za-z0-9]{20,}", text)) or (len(token) >= 8 and token in text)


def redact(text: str) -> str:
    token = os.environ.get("HF_TOKEN", "").strip()
    text = re.sub(r"hf_[A-Za-z0-9]{20,}", "***", text)
    return text.replace(token, "***") if len(token) >= 8 else text


def git(*args: str) -> str | None:
    """None when git itself fails: a failed status must never read as a clean tree."""
    done = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)
    return done.stdout.strip() if done.returncode == 0 else None


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    receipt = {"schema_version": 1, "stage": "audio_translate", "model": MODEL, "revision": REVISION, "started": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "note": "PROVISIONAL TECHNICAL TEST. A PASS means the model ran; Hindi quality is for the human reviewer. Human review: NOT_DONE."}

    def finish(verdict: str, reason: str) -> int:
        reason = redact(reason)
        receipt.update(verdict=verdict, reason=reason, finished=datetime.now(timezone.utc).isoformat(timespec="seconds"))
        text = json.dumps(receipt, ensure_ascii=False, indent=2)
        if contaminated(text):
            text = json.dumps({"verdict": "FAIL", "reason": "a token-like string reached the receipt: withheld"})
            verdict = "FAIL"
        (args.out / "translate_receipt.json").write_text(text, encoding="utf-8")
        print(verdict, "-", reason)
        return 0 if verdict == "PASS" else 1

    if not args.execute:
        return finish("NOT_RUN", "--execute not given")
    head = git("rev-parse", "HEAD")
    receipt["commit"] = head
    dirty = git("status", "--porcelain")
    if not args.expected_commit or head is None or dirty is None or head != args.expected_commit or dirty:
        return finish("NOT_RUN", f"checkout is not the clean expected commit (HEAD {head}, expected {args.expected_commit})")
    try:
        project, models = prepare(args.workdir)
    except RuntimeError as exc:
        return finish("NOT_RUN", str(exc))
    from granthstudio import translation as tr
    from granthstudio.canon import load_canon
    from granthstudio.errors import GranthError, TaskFailed
    real_run_json = tr.run_json

    def guarded(section, payload):
        result = real_run_json(section, payload)
        if contaminated(json.dumps(result, ensure_ascii=False)):
            raise TaskFailed("a token-like string came back from the runner: nothing was written")
        return result

    tr.run_json = guarded                                                  # the runner's answer is checked before translation.py writes anything to disk
    began = time.monotonic()
    try:
        todo = tr.generate_candidates(project, models, 1, execute=True)
    except GranthError as exc:
        receipt["wall_s"] = round(time.monotonic() - began, 1)
        return finish("FAIL", f"{type(exc).__name__}: {exc}"[:1500])
    receipt["wall_s"] = round(time.monotonic() - began, 1)
    receipt["lines_translated"] = todo
    bp.approve_provisional_canon(project, OWNER_NOTE)
    try:
        rows = tr.review_report(project, load_canon(project), 1)
    except GranthError as exc:
        return finish("FAIL", f"review of the candidates failed: {exc}"[:500])
    hindi = {e["dialogue_id"]: e["text"] for e in yaml.safe_load(
        (project.episodes_dir / "adhyay_01" / "hi.yaml").read_text(encoding="utf-8"))["entries"]}
    receipt["lines"] = [{**row, "assistant_hindi_draft": hindi.get(row["dialogue_id"])} for row in rows]
    found = tr.load_candidates(project, 1)
    expected_ids = [f"d_{i:04d}" for i in range(1, 7)]
    identities = [c.get("model_identity") for c in (found["candidates"] if found else [])]
    if [r["dialogue_id"] for r in rows] != expected_ids or sorted(todo) != expected_ids or not all(r["candidate"] and r["candidate"].strip() for r in rows):
        return finish("FAIL", "the six expected lines d_0001..d_0006 do not all have a non-empty candidate")
    if not identities or not all(i and i.get("status") == "verified" and i.get("revision") == REVISION for i in identities):
        return finish("FAIL", f"model identity is not verified at the pinned revision: {identities}")
    candidates = tr.candidates_path(project, 1).read_text(encoding="utf-8")
    if contaminated(candidates):
        return finish("FAIL", "a token-like string reached the candidates: withheld")
    (args.out / "translation_candidates.json").write_text(candidates, encoding="utf-8")
    return finish("PASS", "IndicTrans2 ran at the pinned revision and returned one candidate per line; Hindi correctness awaits the human reviewer")


if __name__ == "__main__":
    raise SystemExit(main())
