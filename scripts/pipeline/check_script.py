from __future__ import annotations

import re
import unicodedata
import hashlib
from typing import Any

_HEADER_RE = re.compile(r'^\*\*(S(\d+)-L(\d+))\*\* \| (\S+) \| ovi (\d+) \| (\S+)$')


def parse_script(text: str) -> list[dict[str, Any]]:
    """Parse the EASY script text into a list of line records."""
    lines = text.splitlines()
    records: list[dict[str, Any]] = []
    current_heading = ""
    current_line: dict[str, Any] | None = None

    for line_no, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if stripped.startswith('## S'):
            current_heading = stripped[3:].strip()
            continue

        if stripped.startswith('**S'):
            match = _HEADER_RE.match(stripped)
            if not match:
                records.append({"bad_header": stripped, "line_no": line_no})
                current_line = None
                continue

            full_id, scene_num, line_num, voice, ovi_str, priority = match.groups()
            scene = f"S{scene_num}"
            ovi = int(ovi_str)
            current_line = {
                "id": full_id,
                "scene": scene,
                "voice": voice,
                "ovi": ovi,
                "priority": priority,
                "marathi": "",
                "hindi": "",
                "heading": current_heading,
                "line_no": line_no,
                "n_marathi": 0,
                "n_hindi": 0,
                "line_num": int(line_num),
            }
            records.append(current_line)
            continue

        if current_line is not None:
            if stripped.startswith('- Marathi:'):
                txt = stripped[len('- Marathi:'):].strip()
                current_line["n_marathi"] += 1
                if current_line["n_marathi"] == 1:
                    current_line["marathi"] = txt
            elif stripped.startswith('- Hindi:'):
                txt = stripped[len('- Hindi:'):].strip()
                current_line["n_hindi"] += 1
                if current_line["n_hindi"] == 1:
                    current_line["hindi"] = txt
            # other lines (captions, etc.) are ignored

    return records


def _has_devanagari_letter(s: str) -> bool:
    for ch in s:
        if 0x0900 <= ord(ch) <= 0x097F and unicodedata.category(ch).startswith('L'):
            return True
    return False


def _has_latin_letter(s: str) -> bool:
    for ch in s:
        if ('A' <= ch <= 'Z') or ('a' <= ch <= 'z'):
            return True
    return False


def _has_ascii_digit(s: str) -> bool:
    for ch in s:
        if '0' <= ch <= '9':
            return True
    return False


def check_script(
    lines: list[dict[str, Any]],
    chapter_ovis: set[int],
    unfilmed_ovis: set[int],
    voices: set[str],
    glossary: dict[str, str],
    covered_ovis: set[int] = frozenset(),
    numbering_exceptions: set[str] = frozenset(),
) -> list[str]:
    """Validate parsed script lines and return a list of error messages.

    `covered_ovis`: ovis the owner approved as covered without a core line (visual-only, merged, optional line).
    `numbering_exceptions`: line ids whose out-of-order number the owner approved (the ids keep their existing audio)."""
    errors: list[str] = []
    seen_ids: set[str] = set()
    scene_counters: dict[str, int] = {}
    prev_scene_num = 0
    core_ovis_seen: set[int] = set()
    good_lines = [r for r in lines if "bad_header" not in r]

    if not good_lines:
        errors.append("script has no lines")

    for rec in lines:
        if "bad_header" in rec:
            errors.append(f"line {rec['line_no']}: bad header")
            continue

        id_ = rec["id"]
        scene = rec["scene"]
        voice = rec["voice"]
        ovi = rec["ovi"]
        priority = rec["priority"]
        heading = rec["heading"]
        marathi = rec["marathi"]
        hindi = rec["hindi"]
        n_marathi = rec["n_marathi"]
        n_hindi = rec["n_hindi"]
        line_num = rec["line_num"]

        # duplicate id
        if id_ in seen_ids:
            errors.append(f"{id_}: duplicate id")
        else:
            seen_ids.add(id_)

        # scene order (by numeric part of scene)
        scene_num = int(scene[1:]) if scene.startswith('S') else 0
        if scene_num < prev_scene_num:
            errors.append(f"{id_}: scene order")
        prev_scene_num = scene_num

        # heading mismatch
        if heading != scene:
            errors.append(f"{id_}: heading {heading} does not match the scene")

        # voice registered
        if voice not in voices:
            errors.append(f"{id_}: voice {voice} is not registered")

        # ovi in chapter
        if ovi not in chapter_ovis:
            errors.append(f"{id_}: ovi {ovi} is not in the chapter")

        # priority
        if priority not in ("core", "optional"):
            errors.append(f"{id_}: priority {priority} must be core or optional")

        # bullet counts
        if n_marathi != 1:
            errors.append(f"{id_}: Marathi must have exactly one bullet")
        if n_hindi != 1:
            errors.append(f"{id_}: Hindi must have exactly one bullet")

        # empty
        if marathi == "":
            errors.append(f"{id_}: Marathi is empty")
        if hindi == "":
            errors.append(f"{id_}: Hindi is empty")

        # Devanagari letter
        if not _has_devanagari_letter(marathi):
            errors.append(f"{id_}: Marathi has no Devanagari letter")
        if not _has_devanagari_letter(hindi):
            errors.append(f"{id_}: Hindi has no Devanagari letter")

        # Latin letter
        if _has_latin_letter(marathi):
            errors.append(f"{id_}: Marathi contains a Latin letter")
        if _has_latin_letter(hindi):
            errors.append(f"{id_}: Hindi contains a Latin letter")

        # ASCII digit
        if _has_ascii_digit(marathi):
            errors.append(f"{id_}: Marathi contains an ASCII digit")
        if _has_ascii_digit(hindi):
            errors.append(f"{id_}: Hindi contains an ASCII digit")

        # glossary
        for wrong, right in glossary.items():
            if wrong in marathi:
                errors.append(f"{id_}: Marathi contains '{wrong}', glossary says '{right}'")
            if wrong in hindi:
                errors.append(f"{id_}: Hindi contains '{wrong}', glossary says '{right}'")

        # line numbers consecutive within scene
        expected = scene_counters.get(scene, 1)
        if line_num != expected and id_ not in numbering_exceptions:
            errors.append(f"{id_}: line numbers must be consecutive from 1 within the scene")
        scene_counters[scene] = expected + 1

        # coverage collection
        if priority == "core":
            core_ovis_seen.add(ovi)

        # unfilmed ovi used
        if ovi in unfilmed_ovis:
            errors.append(f"note: ovi {ovi} is unfilmed but line {id_} uses it")

    # coverage: required ovis (chapter minus unfilmed) must have at least one core line
    required_ovis = sorted(chapter_ovis - unfilmed_ovis - set(covered_ovis))
    for ovi in required_ovis:
        if ovi not in core_ovis_seen:
            errors.append(f"ovi {ovi} has no core line")

    return errors


def script_sha256(text: str) -> str:
    """Return SHA-256 hex digest of the UTF-8 encoded text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
