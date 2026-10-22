"""Marathi and Hindi timelines: Marathi lock, Hindi alignment, protected terms, numeric facts, SRT.

Marathi is the source-language master. Every Marathi line must equal the approved research
text (normalised). Every Hindi line must align to a Marathi line, keep the speaker and shot,
keep the same numeric facts, and render each protected term with an allowed Hindi form.
Automated checks catch detectable discrepancies only (frozen section 5.2).
"""

from __future__ import annotations

import re
from typing import Any

from .canon import Canon
from .config import Project, load_yaml
from .errors import ConfigError, GateFailure
from .integrity import normalize_text
from .research import dialogue_index
from .schemas import validate_document

_DEVANAGARI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")
_NUMBER = re.compile(r"[0-9]+")


def timeline_path(project: Project, adhyay: int, language: str) -> Any:
    return project.episodes_dir / f"adhyay_{adhyay:02d}" / f"{language}.yaml"


def load_timeline(project: Project, adhyay: int, language: str) -> dict[str, Any]:
    document = load_yaml(timeline_path(project, adhyay, language))
    validate_document("timeline", document)
    if document["language"] != language or document["adhyay"] != adhyay:
        raise ConfigError(f"{language}.yaml does not match language/adhyay {language}/{adhyay}")
    return document


def numbers_in(text: str) -> list[str]:
    return _NUMBER.findall(normalize_text(text).translate(_DEVANAGARI_DIGITS))


def check_timelines(
    canon: Canon,
    compiled: dict[str, Any],
    research: dict[str, Any],
    marathi: dict[str, Any],
    hindi: dict[str, Any],
) -> list[str]:
    problems: list[str] = []
    dialogue = dialogue_index(research)
    shots = {shot["shot_id"]: shot for shot in compiled["shots"]}
    episode_lines = {line for shot in compiled["shots"] for line in shot["dialogue_ids"]}

    mr_by_id: dict[str, dict[str, Any]] = {}
    for entry in marathi["entries"]:
        if entry["dialogue_id"] in mr_by_id:
            problems.append(f"Marathi duplicate line {entry['dialogue_id']}")
        mr_by_id[entry["dialogue_id"]] = entry
        if "alignment" in entry:
            problems.append(f"{entry['dialogue_id']}: Marathi lines carry no alignment")
    hi_by_id: dict[str, dict[str, Any]] = {}
    for entry in hindi["entries"]:
        if entry["dialogue_id"] in hi_by_id:
            problems.append(f"Hindi duplicate line {entry['dialogue_id']}")
        hi_by_id[entry["dialogue_id"]] = entry

    if set(mr_by_id) != episode_lines:
        missing = sorted(episode_lines - set(mr_by_id))
        extra = sorted(set(mr_by_id) - episode_lines)
        if missing:
            problems.append(f"Marathi missing lines {missing}")
        if extra:
            problems.append(f"Marathi lines not in any shot {extra}")
    if set(hi_by_id) != set(mr_by_id):
        problems.append(
            f"Hindi and Marathi line sets differ: only-HI {sorted(set(hi_by_id) - set(mr_by_id))}, "
            f"only-MR {sorted(set(mr_by_id) - set(hi_by_id))}"
        )

    for line_id, entry in mr_by_id.items():
        ref = dialogue.get(line_id)
        if ref is None:
            problems.append(f"{line_id}: not in approved research")
            continue
        if entry["speaker"] != ref["speaker"]:
            problems.append(f"{line_id}: speaker differs from approved research")
        if normalize_text(entry["text"]) != normalize_text(ref["text"]):
            problems.append(f"{line_id}: Marathi text differs from approved research (Marathi lock)")
        if entry["shot_id"] not in shots:
            problems.append(f"{line_id}: unknown shot {entry['shot_id']}")
        elif line_id not in shots[entry["shot_id"]]["dialogue_ids"]:
            problems.append(f"{line_id}: placed in {entry['shot_id']} but not listed there")

    protected = [t for t in canon.documents["terminology"]["entries"] if t.get("protected")]
    for line_id, entry in hi_by_id.items():
        alignment = entry.get("alignment")
        if alignment is None:
            problems.append(f"{line_id}: Hindi line has no alignment")
            continue
        if alignment["mr_dialogue_id"] != line_id or line_id not in mr_by_id:
            problems.append(f"{line_id}: Hindi alignment does not point at its Marathi line")
            continue
        mr_line = mr_by_id[line_id]
        if entry["speaker"] != mr_line["speaker"]:
            problems.append(f"{line_id}: Hindi speaker differs from Marathi")
        if entry["shot_id"] != mr_line["shot_id"]:
            problems.append(f"{line_id}: Hindi shot differs from Marathi")
        mr_text = normalize_text(mr_line["text"])
        hi_text = normalize_text(entry["text"])
        if numbers_in(mr_text) != numbers_in(hi_text):
            problems.append(f"{line_id}: numeric facts differ (MR {numbers_in(mr_text)}, HI {numbers_in(hi_text)})")
        for term in protected:
            if normalize_text(term["canonical_name"]) in mr_text:
                allowed = [normalize_text(form) for form in term.get("hi_allowed", [])]
                if not allowed:
                    problems.append(f"{term['id']}: protected term has no Hindi form in canon")
                elif not any(form in hi_text for form in allowed):
                    problems.append(f"{line_id}: protected term {term['id']} lacks an allowed Hindi form")
    return problems


def _timestamp(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, rest = divmod(milliseconds, 3_600_000)
    minutes, rest = divmod(rest, 60_000)
    secs, millis = divmod(rest, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def srt_text(entries: list[dict[str, Any]]) -> str:
    cues: list[str] = []
    cursor = 0.0
    for index, entry in enumerate(entries, start=1):
        duration = entry.get("measured_duration_s")
        if duration is None:
            raise GateFailure(f"{entry['dialogue_id']}: audio duration not measured; subtitles cannot be timed")
        end = cursor + duration
        cues.append(f"{index}\n{_timestamp(cursor)} --> {_timestamp(end)}\n{entry['text']}\n")
        cursor = end
    return "\n".join(cues)
