"""Markdown research -> structured *draft* (frozen section 4.1). Never invents, never approves.

The importer reads the analysis Markdown that already exists and writes ``research.draft.yaml``.
The draft is deliberately not loadable as research: ``location`` and ``artistic`` may be null,
dialogue text is never filled in (the Markdown only has paraphrases and verse fragments, and the
approved Marathi text must come from the printed edition), question statuses are never
``answered``, and a top-level ``_import`` block carries everything a human must resolve.
``promote`` only renames a fully corrected draft to research.yaml; approval stays a separate
named human step (``research approve``).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .canon import Canon
from .config import Project, dump_yaml, load_yaml
from .errors import ConfigError, GateFailure
from .integrity import atomic_write_json, normalize_text, sha256_file
from .schemas import validate_document

DRAFT_FILE = "research.draft.yaml"
REPORT_FILE = "import_report.json"
_HONORIFICS = {"shri", "sri", "sant", "maharaj", "buva", "pant", "pantji", "ji", "baba", "swami", "the", "of"}
_AMBIGUOUS = re.compile(r"\b(inferred|likely|unclear|CONFLICT|not mentioned|PROVISIONAL|unverified|not stated|not named)\b", re.I)
_OVI = re.compile(r"ovi[s]? ([0-9]+(?:[\-–, ]+[0-9]+)*)")
_BOLD_BULLET = re.compile(r"^- \*\*(.+?)\*\*[:,]? ?(.*)$")


def slug(text: str) -> str | None:
    value = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return value or None


def _ovi_refs(text: str) -> list[str]:
    return sorted({f"ovi {m.group(1).strip().replace('–', '-')}" for m in _OVI.finditer(text)})


def _split_heading(text: str) -> tuple[str, str | None, str]:
    """'Name (देवनागरी), role' / 'Name (देवनागरी) - role' / 'Name - role' -> (name, devanagari, role)."""
    text = text.strip()
    match = re.match(r"^(.*?)\s*\(([^()]*[ऀ-ॿ][^()]*)\)\s*[,\-–:]?\s*(.*)$", text)
    if match:
        return match.group(1).strip(), match.group(2).strip(), match.group(3).strip()
    parts = re.split(r"\s+-\s+|,\s+", text, maxsplit=1)
    return parts[0].strip(), None, parts[1].strip() if len(parts) > 1 else ""


def _split_name(text: str) -> tuple[str, str | None]:
    name, dev, _ = _split_heading(text)
    return name, dev


@dataclass
class Parsed:
    adhyay: int
    source: Path
    overview: str = ""
    scenes: list[dict[str, Any]] = field(default_factory=list)
    frame: list[dict[str, str]] = field(default_factory=list)
    characters: list[dict[str, Any]] = field(default_factory=list)
    places: list[dict[str, Any]] = field(default_factory=list)
    objects: list[dict[str, Any]] = field(default_factory=list)
    time_facts: list[dict[str, Any]] = field(default_factory=list)
    notes: list[dict[str, Any]] = field(default_factory=list)
    dialogue: list[dict[str, Any]] = field(default_factory=list)
    ambiguity: list[dict[str, Any]] = field(default_factory=list)


def _sections(lines: list[str]) -> dict[str, tuple[int, list[str]]]:
    """Level-2 sections keyed by their number ('2', '3', '5a' ...), with start line and body."""
    found: dict[str, tuple[int, list[str]]] = {}
    key, start = None, 0
    for index, line in enumerate(lines):
        match = re.match(r"^## (\d+[a-z]?)\. ", line)
        if match or line.startswith("# "):
            if key:
                found[key] = (start, lines[start + 1:index])
            key, start = (match.group(1) if match else None), index
    if key:
        found[key] = (start, lines[start + 1:])
    return found


def _subsections(body: list[str], prefix: str = "### ") -> list[tuple[str, list[str]]]:
    parts, title, current = [], None, []
    for line in body:
        if line.startswith(prefix):
            if title is not None:
                parts.append((title, current))
            title, current = line[len(prefix):].strip(), []
        elif title is not None:
            current.append(line)
    if title is not None:
        parts.append((title, current))
    return parts


def _bullets(body: list[str]) -> dict[str, str]:
    result = {}
    for line in body:
        match = re.match(r"^- \*\*([^*:]+):\*\* ?(.*)$", line)
        if match:
            result[match.group(1).strip().lower()] = match.group(2).strip()
    return result


def parse_markdown(path: Path, adhyay: int) -> Parsed:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    parsed = Parsed(adhyay=adhyay, source=path)
    sections = _sections(lines)
    for number, (start, body) in sections.items():
        for offset, line in enumerate(body):
            for marker in {m.group(0).lower() for m in _AMBIGUOUS.finditer(line)}:
                if len(parsed.ambiguity) < 200:
                    parsed.ambiguity.append({"line": start + 2 + offset, "marker": marker, "section": number})
    if "1" in sections:
        parsed.overview = " ".join(l.strip() for l in sections["1"][1] if l.strip() and l.strip() != "---")
    story = sections.get("2", (0, []))[1]
    for title, body in _subsections(story):
        match = re.match(r"^Episode (\d+)\s*[-–:]\s*(.+)$", title)
        if match:
            fields = _bullets(body)
            parsed.scenes.append({"kind": "episode", "title": match.group(2).strip(), "ovi_range": fields.get("ovi range", "").rstrip("."),
                                  "retelling": fields.get("retelling", ""), "moral": fields.get("moral/teaching", ""), "fields": fields})
        elif title.lower().startswith("frame"):
            for line in body:
                frame = re.match(r"^- \*\*([A-Z])\. (.+?)\*\* - ovi ([0-9\-–, ]+)\.", line)
                if frame:
                    parsed.frame.append({"label": frame.group(1), "title": frame.group(2), "ovi": frame.group(3).strip()})
    breakdown = sections.get("6", (0, []))[1]
    scene_blocks = [(t, b) for t, b in _subsections(breakdown) if re.match(r"^Scene \d+", t)]
    if scene_blocks:  # the scene-by-scene breakdown supersedes the episode summary
        parsed.scenes = []
        for title, body in scene_blocks:
            match = re.match(r"^Scene \d+\s*[-–:]\s*(.+?)(?:\s*\(ovi ([0-9\-–, ]+)\))?$", title)
            fields = _bullets(body)
            parsed.scenes.append({"kind": "scene", "title": match.group(1).strip() if match else title,
                                  "ovi_range": (match.group(2) or "").strip() if match else "", "fields": fields,
                                  "retelling": "", "moral": ""})
    characters = sections.get("3", (0, []))[1]
    for title, body in _subsections(characters):
        if title.startswith("3.1"):
            block = None
            for line in body:
                head = re.match(r"^\*\*(.+?)\*\*(?: - (.+))?$", line.strip())
                if head:
                    latin, dev, role = _split_heading(head.group(1))
                    block = {"name": latin, "name_devanagari": dev, "suggested_id": ("chr_" + slug(latin)) if slug(latin) else None,
                             "role": role or head.group(2) or "", "lines": []}
                    parsed.characters.append(block)
                elif block is not None and line.strip():
                    block["lines"].append(line.strip())
    places = sections.get("4", (0, []))[1]
    for title, body in _subsections(places):
        kind = title.lower()
        for line in body:
            if not line.startswith("- "):
                continue
            match = _BOLD_BULLET.match(line)
            if not match:
                continue
            name, rest = _split_name(match.group(1))
            record = {"name": name, "name_devanagari": _split_name(match.group(1))[1], "text": line[2:].strip(), "source_refs": _ovi_refs(line)}
            if kind.startswith("places"):
                parsed.places.append({**record, "suggested_id": ("loc_" + slug(name)) if slug(name) else None})
            elif kind.startswith("objects"):
                parsed.objects.append({**record, "suggested_id": ("prp_" + slug(name)) if slug(name) else None})
            elif kind.startswith("time"):
                parsed.time_facts.append(record)
    for number, (start, body) in sections.items():
        if number == "5":
            for line in body:
                match = re.match(r"^(\d+)\. \*\*(.+?):?\*\* ?(.*)$", line)
                if match:
                    text_ = match.group(3)
                    resolved = bool(re.search(r"\b(RESOLVED|CONFIRMED)\b", text_))
                    parsed.notes.append({"id": f"a{adhyay:02d}_n{int(match.group(1)):02d}", "label": match.group(2).strip(": "),
                                         "ovi": ", ".join(r.removeprefix("ovi ") for r in _ovi_refs(match.group(2))) or None,
                                         "source_marks_resolved": resolved, "text": text_})
    dialogue = sections.get("7", (0, []))[1]
    for line in dialogue:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 4 and re.match(r"^[0-9]", cells[0]):
            speaker, _, listener = cells[1].partition("->")
            parsed.dialogue.append({"ovi": cells[0], "speaker_name": speaker.strip(), "listener_name": listener.strip(),
                                    "paraphrase": cells[2], "marathi_anchor": cells[3]})
    return parsed


def parse_questions(path: Path, adhyay: int) -> list[dict[str, Any]]:
    """Open (Part A) and provisional (Part B) items for one adhyay. Answers in the file are not applied."""
    items, part, current_adhyay = [], None, None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# PART A"):
            part = "open"
        elif line.startswith("# PART B"):
            part = "provisional"
        heading = re.match(r"^## Adhyay (\d+)", line)
        if heading:
            current_adhyay = int(heading.group(1))
        match = re.match(r"^\*\*([A-Z]+\d*-\d+[a-z]?)\*\*(?: \[([A-Z\-, ]+)\])?(?: · ovi ([^·]+?))?(?: · (.*))?$", line.strip())
        if match and current_adhyay == adhyay and part:
            # [CONFLICT] and [STILL-OPEN] stay open; only Part B / [PROVISIONAL...] is provisional.
            items.append({"id": match.group(1), "tag": match.group(2),
                          "status": "provisional" if ("PROVISIONAL" in (match.group(2) or "") or part == "provisional") else "open",
                          "ovi": (match.group(3) or "").strip() or None, "text": (match.group(4) or "").strip()})
    return items


def _tokens(name: str) -> set[str]:
    return {t for t in re.findall(r"[a-z]+", name.lower()) if t not in _HONORIFICS and len(t) > 2}


def identity_findings(sets: dict[str, list[dict[str, Any]]], canon: Canon | None) -> list[dict[str, Any]]:
    """Possible duplicate or conflicting identities. Findings only: nothing is ever merged."""
    findings: list[dict[str, Any]] = []
    people = [(label, c) for label, chars in sets.items() for c in chars]
    for i, (label_a, a) in enumerate(people):
        for label_b, b in people[i + 1:]:
            shared = _tokens(a["name"]) & _tokens(b["name"])
            if not shared:
                continue
            same = normalize_text(a["name"]).lower() == normalize_text(b["name"]).lower()
            findings.append({"kind": "same_name" if same else "shared_name_token", "between": [f"{label_a}: {a['name']}", f"{label_b}: {b['name']}"],
                             "detail": ("identical name in more than one place: same person or namesakes?" if same else
                                        f"share {sorted(shared)}: possibly one person under two names, or two people") +
                                       "; record an explicit identity decision, nothing is merged automatically"})
    if canon is not None:
        by_name = {}
        for entry_id, entry in canon.entries.items():
            for name in [entry["canonical_name"], *entry.get("aliases", [])]:
                by_name.setdefault(normalize_text(name).lower(), set()).add(entry_id)
        for label, c in people:
            names = {normalize_text(c["name"]).lower(), normalize_text(c["name_devanagari"] or "").lower()} - {""}
            exact = {i for n in names for i in by_name.get(n, set())}
            tokens = _tokens(c["name"])
            partial = {i for i, e in canon.entries.items() if tokens & _tokens(e["canonical_name"])} - exact
            if exact:
                findings.append({"kind": "canon_match", "between": [f"{label}: {c['name']}", *sorted(exact)],
                                 "detail": "name already in canon: reuse the id after confirming it is the same person"})
            if partial:
                findings.append({"kind": "canon_possible", "between": [f"{label}: {c['name']}", *sorted(partial)],
                                 "detail": "partial name overlap with canon: do not reuse an id without an identity decision"})
    return findings


def build_draft(parsed: Parsed, questions: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    n = parsed.adhyay
    scenes, scene_notes = [], {}
    for index, scene in enumerate(parsed.scenes, start=1):
        scene_id = f"a{n:02d}_s{index:02d}"
        fields = scene["fields"]
        actions, missing = [], ["location", "characters", "dialogue", "visual_details", "continuity", "props"]
        beats = fields.get("action beats", "")
        for number, beat in re.findall(r"\((\d+)\) (.*?)(?= \(\d+\) |$)", beats):
            refs = _ovi_refs(beat)
            actions.append({"id": f"{scene_id}_act{int(number):02d}", "text": beat.strip(), "source_refs": refs,
                            "artistic": False if refs else None})
        if not actions:
            missing.append("actions")
        description = scene["retelling"] or scene["title"]
        scenes.append({"scene_id": scene_id, "source_refs": [f"ovi {scene['ovi_range']}"] if scene["ovi_range"] else [],
                       "location": None, "characters": [], "dialogue": [], "description": description, "props": [],
                       "actions": actions, "visual_details": [], "continuity": []})
        scene_notes[scene_id] = {"title": scene["title"], "location_text": fields.get("location"), "present_text": fields.get("present"),
                                 "time_text": fields.get("time/weather/light") or fields.get("time/light"), "mood_text": fields.get("mood"),
                                 "miracle_text": fields.get("miracle"), "moral": scene["moral"] or None, "missing": missing}
    ledger = []
    for index, row in enumerate(parsed.dialogue, start=1):
        first = re.match(r"^[0-9]+", row["ovi"])
        owner = next((s["scene_id"] for s, src in zip(scenes, parsed.scenes) if first and _within(int(first.group(0)), src["ovi_range"])), None)
        ledger.append({"suggested_id": f"d_{index:04d}", **row, "scene_id": owner, "text": None,
                       "status": "text_missing: copy the exact Marathi verse text from the printed edition",
                       "speaker_unclear": "unclear" in row["speaker_name"].lower()})
    seen = set()
    draft_questions = []
    for q in questions:
        draft_questions.append({"id": q["id"], "status": q["status"], **({"ovi": q["ovi"]} if q["ovi"] else {})})
        seen.add(q["id"])
    for note in parsed.notes:
        # A source note marked RESOLVED stays provisional: only a human sets 'answered'.
        draft_questions.append({"id": note["id"], "status": "provisional" if note["source_marks_resolved"] else "open",
                                **({"ovi": note["ovi"]} if note["ovi"] else {})})
    def facts(items, prefix):
        return [{"id": f"a{n:02d}_{prefix}_{slug(i['name']) or k}", "text": i["text"], "source_refs": i["source_refs"],
                 "artistic": False if i["source_refs"] else None} for k, i in enumerate(items, start=1)]
    draft = {"schema_version": 1, "adhyay": n, "overview": parsed.overview, "scenes": scenes, "open_questions": draft_questions,
             "objects": facts(parsed.objects, "obj"), "time_and_season": facts(parsed.time_facts, "time")}
    for key in ("objects", "time_and_season"):
        if not draft[key]:
            del draft[key]
    todo = {"scenes": scene_notes, "dialogue": ledger,
            "characters_found": [{k: v for k, v in c.items()} for c in parsed.characters],
            "places_found": parsed.places, "frame_sections": parsed.frame,
            "question_text": {**{q["id"]: q["text"] for q in questions}, **{x["id"]: x["label"] + " " + x["text"] for x in parsed.notes}}}
    return draft, todo


def _within(number: int, range_text: str) -> bool:
    match = re.match(r"^\s*(\d+)\s*(?:[-–]\s*(\d+))?", range_text or "")
    if not match:
        return False
    low, high = int(match.group(1)), int(match.group(2) or match.group(1))
    return low <= number <= high


def import_markdown(project: Project, source: Path, adhyay: int, questions_file: Path | None, compare: list[tuple[Path, int]],
                    canon: Canon | None, write: bool) -> dict[str, Any]:
    parsed = parse_markdown(source, adhyay)
    questions = parse_questions(questions_file, adhyay) if questions_file else []
    draft, todo = build_draft(parsed, questions)
    other = {f"adhyay {a}": parse_markdown(p, a).characters for p, a in compare}
    findings = identity_findings({f"adhyay {adhyay}": parsed.characters, **other}, canon)
    missing_total = {k: sum(k in s["missing"] for s in todo["scenes"].values()) for k in
                     ("location", "characters", "dialogue", "visual_details", "actions")}
    statuses = [q["status"] for q in draft["open_questions"]]
    report = {"schema_version": 1, "adhyay": adhyay, "source": str(source), "source_sha256": sha256_file(source),
              "questions_source": str(questions_file) if questions_file else None,
              "counts": {"scenes": len(draft["scenes"]), "frame_sections": len(parsed.frame), "characters_found": len(parsed.characters),
                         "places_found": len(parsed.places), "dialogue_rows": len(todo["dialogue"]),
                         "open_questions": statuses.count("open"), "provisional_items": statuses.count("provisional"),
                         "answered": 0},
              "scenes_missing_field": missing_total,
              "dialogue_text_imported": 0, "ambiguity_markers": len(parsed.ambiguity), "ambiguity_sample": parsed.ambiguity[:25],
              "identity_findings": findings, "approved": False, "written": False,
              "notes": ["Nothing is approved. Questions are never marked answered; a human sets that after resolving them.",
                        "Dialogue text is not imported: copy exact Marathi from the printed edition into each scene."]}
    draft["_import"] = {"source": str(source), "source_sha256": report["source_sha256"], "todo": todo,
                        "instruction": "Fill every null, then delete this _import block and run: research promote"}
    if write:
        folder = project.research_dir / f"adhyay_{adhyay:02d}"
        folder.mkdir(parents=True, exist_ok=True)
        dump_yaml(folder / DRAFT_FILE, draft)
        atomic_write_json(folder / REPORT_FILE, report)
        report["written"] = True
    return report


def draft_blockers(project: Project, adhyay: int) -> list[str]:
    path = project.research_dir / f"adhyay_{adhyay:02d}" / DRAFT_FILE
    if not path.is_file():
        raise ConfigError(f"no draft at {path}")
    draft = load_yaml(path)
    blockers = []
    if "_import" in draft:
        blockers.append("the _import block is still present: review it, then delete it")
    body = {k: v for k, v in draft.items() if k != "_import"}
    try:
        validate_document("research", body)
    except Exception as exc:
        blockers.append(f"schema: {exc}"[:600])
    for scene in draft.get("scenes", []):
        if not scene.get("dialogue"):
            blockers.append(f"{scene['scene_id']}: no dialogue entered (valid only if the scene is silent; confirm)")
    return blockers


def promote_draft(project: Project, adhyay: int) -> Path:
    """Rename a fully corrected draft to research.yaml. This is not approval."""
    folder = project.research_dir / f"adhyay_{adhyay:02d}"
    target = folder / "research.yaml"
    if target.exists():
        raise GateFailure(f"{target} already exists; edit it directly (promote never overwrites research)")
    blockers = [b for b in draft_blockers(project, adhyay) if not b.endswith("confirm)")]
    if blockers:
        raise GateFailure("draft is not ready: " + "; ".join(blockers))
    (folder / DRAFT_FILE).replace(target)
    return target
