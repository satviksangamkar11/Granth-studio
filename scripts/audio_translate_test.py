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
import re
import shutil
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
    return parser


def prepare(workdir: Path):
    from granthstudio.config import dump_yaml, load_models, load_project
    if (workdir / "project").exists():
        raise RuntimeError("the workdir already holds a project: a fresh --workdir is required")
    root = bp.build(workdir / "project")
    artifacts = workdir / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    config = yaml.safe_load((root / "config" / "project.yaml").read_text(encoding="utf-8"))
    config["artifacts_dir"] = str(artifacts)
    (root / "config" / "project.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    project = load_project(root)
    models = load_models(project)
    models["translation"].update(status="validated", command=[sys.executable, str(RUNNER)], model=MODEL, revision=REVISION, timeout_s=3000)
    dump_yaml(root / "config" / "models.yaml", models)
    return load_project(root)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    receipt = {"schema_version": 1, "stage": "audio_translate", "model": MODEL, "revision": REVISION, "started": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "note": "PROVISIONAL TECHNICAL TEST. A PASS means the model ran; Hindi quality is for the human reviewer. Human review: NOT_DONE."}

    def finish(verdict: str, reason: str) -> int:
        receipt.update(verdict=verdict, reason=reason, finished=datetime.now(timezone.utc).isoformat(timespec="seconds"))
        text = json.dumps(receipt, ensure_ascii=False, indent=2)
        if re.search(r"hf_[A-Za-z0-9]{20,}", text):
            text = json.dumps({"verdict": "FAIL", "reason": "a token-like string reached the receipt: withheld"})
        (args.out / "translate_receipt.json").write_text(text, encoding="utf-8")
        print(verdict, "-", reason)
        return 0 if verdict == "PASS" else 1

    if not args.execute:
        return finish("NOT_RUN", "--execute not given")
    try:
        project = prepare(args.workdir)
    except RuntimeError as exc:
        return finish("NOT_RUN", str(exc))
    from granthstudio import translation as tr
    from granthstudio.canon import load_canon
    from granthstudio.config import load_models
    from granthstudio.errors import GranthError
    models = load_models(project)
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
        rows, receipt["review_error"] = [], str(exc)
    hindi = {e["dialogue_id"]: e["text"] for e in yaml.safe_load(
        (project.episodes_dir / "adhyay_01" / "hi.yaml").read_text(encoding="utf-8"))["entries"]}
    receipt["lines"] = [{**row, "assistant_hindi_draft": hindi.get(row["dialogue_id"])} for row in rows]
    candidates = tr.candidates_path(project, 1)
    if candidates.is_file():
        shutil.copyfile(candidates, args.out / "translation_candidates.json")
    if not todo or not all(row["candidate"] for row in rows):
        return finish("FAIL", "not every line has a candidate")
    return finish("PASS", "IndicTrans2 ran at the pinned revision and returned one candidate per line; Hindi correctness awaits the human reviewer")


if __name__ == "__main__":
    raise SystemExit(main())
