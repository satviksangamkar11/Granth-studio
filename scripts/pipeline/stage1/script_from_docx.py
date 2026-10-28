from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def collapse_whitespace(text: str) -> str:
    """Collapse any run of whitespace (including newlines) to a single space and strip ends."""
    return re.sub(r"\s+", " ", text).strip()


def ovis_to_script(adhyay: int, ovis: list[dict[str, Any]]) -> str:
    """
    Convert a list of ovi records into the draft script text.

    Raises ValueError with a clear message for any invalid input.
    """
    if not ovis:
        raise ValueError("ovis list is empty")

    # Validate and collect ovi numbers for duplicate detection
    seen_ovis = set()
    for idx, rec in enumerate(ovis):
        # ovi must be present and be an int (not bool)
        if "ovi" not in rec:
            raise ValueError(f"record at index {idx} missing 'ovi'")
        ovi = rec["ovi"]
        if not isinstance(ovi, int) or isinstance(ovi, bool):
            raise ValueError(f"record at index {idx} has non-int ovi: {ovi!r}")
        if ovi in seen_ovis:
            raise ValueError(f"duplicate ovi: {ovi}")
        seen_ovis.add(ovi)

        # section must be present and be an int (not bool)
        if "section" not in rec:
            raise ValueError(f"record at index {idx} missing 'section'")
        section = rec["section"]
        if not isinstance(section, int) or isinstance(section, bool):
            raise ValueError(f"record at index {idx} has non-int section: {section!r}")

        # simple_marathi and hindi must be present and non-empty after collapsing
        for field in ("simple_marathi", "hindi"):
            if field not in rec:
                raise ValueError(f"record at index {idx} missing '{field}'")
            collapsed = collapse_whitespace(str(rec[field]))
            if not collapsed:
                raise ValueError(f"record at index {idx} has empty '{field}' after collapsing whitespace")

    # Sort by ovi
    sorted_ovis = sorted(ovis, key=lambda r: r["ovi"])

    lines: list[str] = []
    # Header
    lines.append(
        f"# Adhyay {adhyay}: DRAFT script built mechanically from the owner's docx columns (Simple Marathi, Hindi). NOT the owner's final script; speakers are all narrator; every line is core."
    )
    lines.append("")  # blank line after header

    current_section = None
    line_in_section = 0

    for rec in sorted_ovis:
        section = rec["section"]
        ovi = rec["ovi"]
        marathi = collapse_whitespace(str(rec["simple_marathi"]))
        hindi = collapse_whitespace(str(rec["hindi"]))

        if section != current_section:
            current_section = section
            line_in_section = 1
            lines.append(f"## S{current_section}")
        else:
            line_in_section += 1

        lines.append(f"**S{section}-L{line_in_section}** | narrator | ovi {ovi} | core")
        lines.append(f"- Marathi: {marathi}")
        lines.append(f"- Hindi: {hindi}")
        lines.append("")  # blank line after each line block

    script = "\n".join(lines)
    # Ensure a blank line after the last line block (spec: a blank line follows each line block)
    return script + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build draft script from ovis.jsonl")
    parser.add_argument("--adhyay", type=int, required=True, help="Adhyay number (e.g., 2)")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[3],
        help="Repository root (default: repo root inferred from this file)",
    )
    args = parser.parse_args(argv)

    adhyay = args.adhyay
    root = args.root

    input_path = root / "canon" / f"adhyay_{adhyay:02d}" / "source" / "ovis.jsonl"
    output_path = root / "canon" / f"adhyay_{adhyay:02d}" / "script" / "easy.md"

    if not input_path.exists():
        print(f"refused: input file not found: {input_path}", file=sys.stderr)
        return 2

    if output_path.exists():
        print(f"refused: output file already exists: {output_path}", file=sys.stderr)
        return 2

    # Read ovis.jsonl
    ovis: list[dict[str, Any]] = []
    try:
        with input_path.open("r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    ovis.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"refused: invalid JSON on line {line_num}: {e}", file=sys.stderr)
                    return 2
    except OSError as e:
        print(f"refused: cannot read input file: {e}", file=sys.stderr)
        return 2

    # Generate script
    try:
        script_text = ovis_to_script(adhyay, ovis)
    except ValueError as e:
        print(f"refused: {e}", file=sys.stderr)
        return 2

    # Write output
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            f.write(script_text)
    except OSError as e:
        print(f"refused: cannot write output file: {e}", file=sys.stderr)
        return 2

    # Count lines and sections
    num_lines = len(ovis)
    num_sections = len({rec["section"] for rec in ovis})
    print(f"adhyay {adhyay}: {num_lines} lines, {num_sections} sections")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
