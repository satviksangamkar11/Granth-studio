"""Speech generation, ASR comparison and reviewed audio (frozen sections 5.3 and 5.4).

IndicF5 only produces *candidates*. A voice needs a licence or consent record before it is used.
A candidate becomes timeline audio solely through a named human listening approval bound to the
audio hash and the current script text. ASR output is a diagnostic: it never approves or blocks.
"""
from __future__ import annotations

import os
import shutil
import string
import uuid
from collections import Counter
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from .config import Project, dump_yaml, load_yaml
from .errors import ConfigError, GateFailure, TaskFailed
from .ffmpeg import validate_audio
from .integrity import atomic_write_json, contained_path, normalize_text, read_json, sha256_file, sha256_obj
from .runners import identity_block, require_consistent_identity, require_runner, run_json
from .schemas import validate_document
from .timelines import load_timeline, timeline_path

_EDGE = string.punctuation + "।॥“”‘’…–—"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def voices_path(project: Project) -> Path:
    return project.canon_dir / "voices.yaml"


def voice_root(project: Project) -> Path:
    return project.artifacts_dir / "voices"


def candidate_root(project: Project, language: str) -> Path:
    return project.artifacts_dir / "audio" / "candidates" / language


def load_voices(project: Project) -> list[dict[str, Any]]:
    path = voices_path(project)
    if not path.is_file():
        return []
    data = load_yaml(path)
    validate_document("voices", data)
    seen = set()
    for voice in data["voices"]:
        key = (voice["speaker"], voice["language"])
        if key in seen or voice["voice_id"] in seen:
            raise ConfigError(f"duplicate voice for {key} or id {voice['voice_id']}")
        seen.update({key, voice["voice_id"]})
    return data["voices"]


def voice_for(project: Project, speaker: str, language: str) -> dict[str, Any]:
    """The licensed/consented voice for a speaker. Refuses when none is recorded (frozen 5.3)."""
    voice = next((v for v in load_voices(project) if v["speaker"] == speaker and v["language"] == language), None)
    if voice is None:
        raise GateFailure(f"no licensed or consented {language} voice reference recorded for {speaker} in canon/voices.yaml")
    reference = contained_path(voice_root(project), voice["reference_audio"]["path"])
    if not reference.is_file() or sha256_file(reference) != voice["reference_audio"]["sha256"]:
        raise GateFailure(f"{voice['voice_id']}: reference audio missing or changed")
    validate_audio(reference)
    return voice


def speech_request(section: dict[str, Any], voice: dict[str, Any], entry: dict[str, Any], language: str) -> dict[str, Any]:
    request = {"dialogue_id": entry["dialogue_id"], "language": language, "text": entry["text"],
               "text_sha256": sha256_obj(normalize_text(entry["text"])), "voice_id": voice["voice_id"],
               "voice_model_version": voice["model_version"], "reference_audio_sha256": voice["reference_audio"]["sha256"],
               "reference_transcript": voice["reference_transcript"], "model": section["model"], "revision": section["revision"]}
    request["request_sha256"] = sha256_obj(request)
    return request


def record_path(project: Project, language: str, line_id: str) -> Path:
    return candidate_root(project, language) / f"{line_id}.json"


def generate_speech(project: Project, models: dict[str, Any], adhyay: int, language: str,
                    line_ids: list[str] | None, execute: bool) -> list[str]:
    """Generate speech candidates. Dry run lists the lines; execution needs a validated runner."""
    timeline = load_timeline(project, adhyay, language)
    entries = [e for e in timeline["entries"] if not line_ids or e["dialogue_id"] in line_ids]
    if line_ids and len(entries) != len(set(line_ids)):
        raise ConfigError(f"unknown dialogue ids in {line_ids}")
    if not execute:
        return [e["dialogue_id"] for e in entries]
    section = require_runner(models, "speech", "IndicF5")
    voices = {e["dialogue_id"]: voice_for(project, e["speaker"], language) for e in entries}  # consent first
    # Approved Marathi source, Hindi review, protected terms, numeric facts, attribution and text hashes
    # (one gate, shared with the release path) must hold before any model runner is invoked.
    from .pipeline import load_bundle
    load_bundle(project, models, adhyay)
    done = []
    for entry in entries:
        voice = voices[entry["dialogue_id"]]
        reference = contained_path(voice_root(project), voice["reference_audio"]["path"])
        request = speech_request(section, voice, entry, language)
        root = candidate_root(project, language)
        old = record_path(project, language, entry["dialogue_id"])
        if old.is_file() and read_json(old)["request_sha256"] == request["request_sha256"]:
            continue  # same text, voice and model: the existing candidate is current
        root.mkdir(parents=True, exist_ok=True)
        part = root / f".{entry['dialogue_id']}.{uuid.uuid4().hex}.part.wav"
        try:
            answer = run_json(section, {**request, "reference_audio": str(reference), "out_path": str(part)})
            identity = identity_block(section, answer)   # mismatched evidence rejects the output before it is kept
            if not part.is_file():
                raise TaskFailed(f"{entry['dialogue_id']}: speech runner wrote no audio")
            duration = validate_audio(part)
            digest = sha256_file(part)
            final = root / f"{entry['dialogue_id']}_{digest[:12]}.wav"
            os.replace(part, final)
        finally:
            part.unlink(missing_ok=True)
        atomic_write_json(old, {"schema_version": 1, "dialogue_id": entry["dialogue_id"], "language": language,
            "text_sha256": request["text_sha256"], "request_sha256": request["request_sha256"], "voice_id": voice["voice_id"],
            "model": section["model"], "revision": section["revision"], "audio": {"path": final.name, "sha256": digest},
            "duration_s": duration, "generated_at": _now(),
            "model_identity": identity})
        done.append(entry["dialogue_id"])
    return done


def _tokens(text: str) -> list[str]:
    return [t for t in (w.strip(_EDGE) for w in normalize_text(text).split()) if t]


def compare_transcript(expected: str, heard: str) -> dict[str, Any]:
    """Word-level difference between the script and what ASR heard. Not a pronunciation judgment."""
    want, got = _tokens(expected), _tokens(heard)
    return {"similarity": SequenceMatcher(None, want, got).ratio() if want or got else 1.0,
            "missing_words": sorted((Counter(want) - Counter(got)).elements()),
            "extra_words": sorted((Counter(got) - Counter(want)).elements())}


def asr_check(project: Project, models: dict[str, Any], adhyay: int, language: str, line_id: str) -> dict[str, Any]:
    section = require_runner(models, "asr", "ASR")
    record = read_json(_record(project, language, line_id))
    entry = next(e for e in load_timeline(project, adhyay, language)["entries"] if e["dialogue_id"] == line_id)
    audio = contained_path(candidate_root(project, language), record["audio"]["path"])
    if sha256_file(audio) != record["audio"]["sha256"]:
        raise GateFailure(f"{line_id}: candidate audio changed")
    heard = run_json(section, {"audio_path": str(audio), "language": language}).get("text")
    if not isinstance(heard, str):
        raise TaskFailed("ASR runner must return {'text': str}")
    report = {"schema_version": 1, "dialogue_id": line_id, "language": language, "audio_sha256": record["audio"]["sha256"],
              "expected_text_sha256": sha256_obj(normalize_text(entry["text"])), "transcript": heard,
              "model": section["model"], "revision": section["revision"], **compare_transcript(entry["text"], heard),
              "enforced": False, "note": "Diagnostic only: ASR cannot judge pronunciation (frozen 5.4)."}
    atomic_write_json(candidate_root(project, language) / f"{line_id}.asr.json", report)
    return report


def validate_alignment(words: Any, script_text: str, duration_s: float) -> list[dict[str, Any]]:
    """Frozen 5.4 word-level alignment checks. Pure: raises GateFailure, returns clean word rows."""
    if not isinstance(words, list) or not all(isinstance(w, dict) for w in words):
        raise GateFailure("aligner must return {'words': [{'word','start_s','end_s'}]}")
    if _tokens(" ".join(str(w.get("word", "")) for w in words)) != _tokens(script_text):
        raise GateFailure("aligned words differ from the script's tokens")
    previous_end = previous_start = 0.0
    for w in words:
        start, end = w.get("start_s"), w.get("end_s")
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and v == v for v in (start, end)):
            raise GateFailure(f"word {w['word']!r}: start_s/end_s must be numbers")
        if start < 0 or end < start:
            raise GateFailure(f"word {w['word']!r}: invalid span {start}..{end}")
        if start < previous_start:
            raise GateFailure(f"word {w['word']!r}: starts before the previous word")
        if start < previous_end - 0.001:
            raise GateFailure(f"word {w['word']!r}: overlaps the previous word")
        previous_start, previous_end = start, max(previous_end, end)
    if words and previous_end > duration_s + 0.001:
        raise GateFailure(f"alignment ends at {previous_end:.3f}s, after the audio ({duration_s:.3f}s)")
    return [{"word": w["word"], "start_s": w["start_s"], "end_s": w["end_s"]} for w in words]


def align_words(project: Project, models: dict[str, Any], adhyay: int, language: str, line_id: str,
                source: str = "release") -> dict[str, Any]:
    """Word alignment. ``release`` (default) aligns the current approved timeline audio; ``candidate``
    aligns an unapproved candidate and is written separately so it never stands in for release audio."""
    if source not in ("release", "candidate"):
        raise ConfigError(f"alignment source must be 'release' or 'candidate', not {source!r}")
    section = require_runner(models, "aligner", "aligner")
    entry = next((e for e in load_timeline(project, adhyay, language)["entries"] if e["dialogue_id"] == line_id), None)
    if entry is None:
        raise ConfigError(f"unknown dialogue id {line_id}")
    text_hash = sha256_obj(normalize_text(entry["text"]))
    if source == "release":
        approved = entry.get("audio")
        if not approved:
            raise GateFailure(f"{line_id}: no approved timeline audio for {language}; use source='candidate' for candidates")
        if approved["text_sha256"] != text_hash:
            raise GateFailure(f"{line_id}: approved audio is bound to different script text")
        audio = contained_path(project.artifacts_dir / "audio", approved["path"])
        digest, provenance, name = approved["sha256"], approved.get("provenance"), f"{line_id}.align.json"
    else:
        record = read_json(_record(project, language, line_id))
        if record["text_sha256"] != text_hash:
            raise GateFailure(f"{line_id}: candidate record is stale (script text changed since generation)")
        audio = contained_path(candidate_root(project, language), record["audio"]["path"])
        digest, provenance, name = record["audio"]["sha256"], {"request_sha256": record["request_sha256"]}, f"{line_id}.align.candidate.json"
    if not audio.is_file() or sha256_file(audio) != digest:
        raise GateFailure(f"{line_id}: audio missing or changed")
    duration = validate_audio(audio)
    answer = run_json(section, {"audio_path": str(audio), "text": entry["text"], "language": language})
    words = validate_alignment(answer.get("words"), entry["text"], duration)
    report = {"schema_version": 1, "dialogue_id": line_id, "language": language, "audio_sha256": digest,
              "expected_text_sha256": text_hash, "audio_source": source, "audio_provenance": provenance, "words": words,
              "model": section["model"], "revision": section["revision"], "enforced": False,
              "note": "Word-level data only; subtitles stay sentence/phrase level (frozen 5.4)."}
    atomic_write_json(candidate_root(project, language) / name, report)
    return report


def _record(project: Project, language: str, line_id: str) -> Path:
    path = record_path(project, language, line_id)
    if not path.is_file():
        raise GateFailure(f"{line_id}: no speech candidate for {language}; generate one first")
    return path


def approve_speech(project: Project, adhyay: int, language: str, line_id: str, reviewer: str) -> dict[str, Any]:
    """Attach a listened-to candidate to the timeline, bound to its audio hash and the script text."""
    if not reviewer.strip():
        raise ConfigError("a reviewer name is required")
    record = read_json(_record(project, language, line_id))
    path = timeline_path(project, adhyay, language)
    document = load_yaml(path)
    entry = next((e for e in document["entries"] if e["dialogue_id"] == line_id), None)
    if entry is None:
        raise ConfigError(f"unknown dialogue id {line_id}")
    text_hash = sha256_obj(normalize_text(entry["text"]))
    if record["text_sha256"] != text_hash:
        raise GateFailure(f"{line_id}: the script text changed since this speech was generated")
    voice = voice_for(project, entry["speaker"], language)  # consent must still be on record
    if voice["voice_id"] != record["voice_id"]:
        raise GateFailure(f"{line_id}: candidate used voice {record['voice_id']}, canon now says {voice['voice_id']}")
    source = contained_path(candidate_root(project, language), record["audio"]["path"])
    if sha256_file(source) != record["audio"]["sha256"]:
        raise GateFailure(f"{line_id}: candidate audio changed")
    relative = f"generated/{language}/{line_id}_{record['audio']['sha256'][:12]}.wav"
    target = project.artifacts_dir / "audio" / "generated" / language / f"{line_id}_{record['audio']['sha256'][:12]}.wav"
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.is_file():
        tmp = target.with_name(f".{target.name}.{uuid.uuid4().hex}.tmp")
        shutil.copyfile(source, tmp)
        os.replace(tmp, target)
    asr = candidate_root(project, language) / f"{line_id}.asr.json"
    asr_hash = sha256_file(asr) if asr.is_file() and read_json(asr)["audio_sha256"] == record["audio"]["sha256"] else None
    entry["audio"] = {"path": relative, "sha256": record["audio"]["sha256"], "language": language,
                      "speaker": entry["speaker"], "text_sha256": text_hash, "speech_reviewed_by": reviewer.strip(),
                      "provenance": {"origin": "generated", "voice_id": record["voice_id"], "model": record["model"],
                                     "revision": record["revision"], "request_sha256": record["request_sha256"],
                                     "model_identity": require_consistent_identity(
                                         record.get("model_identity"), record["model"], record["revision"], line_id),
                                     "asr_report_sha256": asr_hash}}
    validate_document("timeline", document)
    dump_yaml(path, document)
    return entry["audio"]
