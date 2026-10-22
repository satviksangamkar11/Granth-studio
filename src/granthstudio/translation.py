"""Marathi -> Hindi translation candidates and hash-bound human approval (frozen section 5.2).

IndicTrans2 only proposes candidates. A candidate becomes a Hindi timeline line solely through a
named human approval that binds the exact Marathi and Hindi text hashes, after the deterministic
protected-term and numeric-fact checks pass. Nothing here judges meaning.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .canon import Canon
from .config import Project, dump_yaml, load_yaml
from .errors import ConfigError, GateFailure, TaskFailed
from .integrity import atomic_write_json, normalize_text, read_json, sha256_obj
from .runners import record_run_evidence, require_runner, run_json, verify_run_evidence
from .schemas import validate_document
from .timelines import hindi_line_problems, load_timeline, protected_terms, timeline_path

SRC_LANG, TGT_LANG = "mar_Deva", "hin_Deva"  # FLORES-style codes used by IndicTrans2


def candidates_path(project: Project, adhyay: int) -> Path:
    return project.episodes_dir / f"adhyay_{adhyay:02d}" / "translation_candidates.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _mr_hash(text: str) -> str:
    return sha256_obj(normalize_text(text))


def load_candidates(project: Project, adhyay: int) -> dict[str, Any] | None:
    path = candidates_path(project, adhyay)
    if not path.is_file():
        return None
    data = read_json(path)
    validate_document("translation_candidates", data)
    return data


def generate_candidates(project: Project, models: dict[str, Any], adhyay: int, execute: bool) -> list[str]:
    """Translate Marathi lines that have no current candidate. Returns the line ids needing work."""
    marathi = load_timeline(project, adhyay, "mr")
    existing = load_candidates(project, adhyay)
    section = models.get("translation")
    current = {c["dialogue_id"]: c for c in (existing["candidates"] if existing else [])
               if existing and section and (existing["model"], existing["revision"]) == (section["model"], section["revision"])}
    todo = [e for e in marathi["entries"]
            if e["dialogue_id"] not in current or current[e["dialogue_id"]]["mr_sha256"] != _mr_hash(e["text"])]
    if not execute or not todo:
        return [e["dialogue_id"] for e in todo]
    section = require_runner(models, "translation", "IndicTrans2")
    result = run_json(section, {"src_lang": SRC_LANG, "tgt_lang": TGT_LANG, "texts": [e["text"] for e in todo],
                                "model": section["model"], "revision": section["revision"]})
    texts = result.get("translations")
    if not (isinstance(texts, list) and len(texts) == len(todo) and all(isinstance(t, str) and t.strip() for t in texts)):
        raise TaskFailed("translation runner must return one non-empty string per input line")
    outputs = {"candidates": {e["dialogue_id"]: sha256_obj(normalize_text(t)) for e, t in zip(todo, texts)}}
    request_sha = sha256_obj({"texts": [e["text"] for e in todo], "model": section["model"], "revision": section["revision"]})
    identity, evidence_sha = record_run_evidence(project.artifacts_dir / "evidence" / "model_runs", section, request_sha,
                                                 result, outputs)       # per run; each candidate below keeps its own
    for entry, text in zip(todo, texts):
        current[entry["dialogue_id"]] = {"dialogue_id": entry["dialogue_id"], "mr_sha256": _mr_hash(entry["text"]),
                                         "text": text, "candidate_sha256": sha256_obj(normalize_text(text)),
                                         "generated_at": _now(), "model_identity": identity, "evidence_sha256": evidence_sha}
    order = [e["dialogue_id"] for e in marathi["entries"]]
    document = {"schema_version": 1, "adhyay": adhyay, "model": section["model"], "revision": section["revision"],
                "candidates": [current[i] for i in order if i in current]}
    validate_document("translation_candidates", document)
    atomic_write_json(candidates_path(project, adhyay), document)
    return [e["dialogue_id"] for e in todo]


def review_report(project: Project, canon: Canon, adhyay: int) -> list[dict[str, Any]]:
    """Per line: Marathi, candidate, and the deterministic problems. Meaning is left to the reviewer."""
    marathi, found = load_timeline(project, adhyay, "mr"), load_candidates(project, adhyay)
    by_id = {c["dialogue_id"]: c for c in (found["candidates"] if found else [])}
    protected, rows = protected_terms(canon), []
    for entry in marathi["entries"]:
        candidate = by_id.get(entry["dialogue_id"])
        stale = candidate is not None and candidate["mr_sha256"] != _mr_hash(entry["text"])
        problems = (["candidate is stale: the Marathi line changed"] if stale else
                    hindi_line_problems(protected, entry["dialogue_id"], entry["text"], candidate["text"])
                    if candidate else ["no candidate"])
        rows.append({"dialogue_id": entry["dialogue_id"], "marathi": entry["text"],
                     "candidate": candidate["text"] if candidate else None, "problems": problems})
    return rows


def approve_translation(project: Project, canon: Canon, adhyay: int, line_id: str, reviewer: str,
                        text: str | None = None) -> dict[str, Any]:
    """Write one reviewed Hindi line into hi.yaml. ``text`` is a human-edited replacement."""
    if not reviewer.strip():
        raise ConfigError("a reviewer name is required")
    marathi = load_timeline(project, adhyay, "mr")
    mr_entry = next((e for e in marathi["entries"] if e["dialogue_id"] == line_id), None)
    if mr_entry is None:
        raise ConfigError(f"unknown dialogue id {line_id}")
    source: dict[str, Any]
    if text is None:
        found = load_candidates(project, adhyay)
        candidate = next((c for c in (found["candidates"] if found else []) if c["dialogue_id"] == line_id), None)
        if candidate is None or candidate["mr_sha256"] != _mr_hash(mr_entry["text"]):
            raise GateFailure(f"{line_id}: no current candidate to approve; generate one or pass --text")
        text = candidate["text"]
        source = {"origin": "model_candidate", "model": found["model"], "revision": found["revision"],
                  "model_identity": verify_run_evidence(
                      project.artifacts_dir / "evidence" / "model_runs", candidate.get("evidence_sha256"),
                      candidate.get("model_identity"), found["model"], found["revision"],
                      {"candidates": {line_id: candidate["candidate_sha256"]}}, line_id),
                  "evidence_sha256": candidate.get("evidence_sha256"),
                  "candidate_sha256": candidate["candidate_sha256"]}
    else:
        source = {"origin": "human_text"}
    problems = hindi_line_problems(protected_terms(canon), line_id, mr_entry["text"], text)
    if problems:
        raise GateFailure("; ".join(problems))
    entry = {"dialogue_id": line_id, "shot_id": mr_entry["shot_id"], "speaker": mr_entry["speaker"], "text": text.strip(),
             "alignment": {"mr_dialogue_id": line_id,
                           "match": "exact" if normalize_text(text) == normalize_text(mr_entry["text"]) else "adapted",
                           "reviewed": True, "source": source,
                           "verification": {"reviewer": reviewer.strip(), "mr_sha256": _mr_hash(mr_entry["text"]),
                                            "hi_sha256": _mr_hash(text)}}}
    path = timeline_path(project, adhyay, "hi")
    document = load_yaml(path) if path.is_file() else {"schema_version": 1, "language": "hi", "adhyay": adhyay, "entries": []}
    kept = {e["dialogue_id"]: e for e in document["entries"] if e["dialogue_id"] != line_id}
    kept[line_id] = entry  # a changed text drops any older audio block: it no longer matches
    document["entries"] = [kept[e["dialogue_id"]] for e in marathi["entries"] if e["dialogue_id"] in kept]
    validate_document("timeline", document)
    dump_yaml(path, document)
    return entry
