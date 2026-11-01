import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple


def load_reports(output_dir: str) -> List[Dict[str, Any]]:
    """
    Load COMPLETE reports from all api_log.json files under output_dir.
    Returns list of report dicts with added 'group_id' and 'kind' keys.
    Stable order: by video folder name, then natural order of group_id.
    Raises ValueError on corrupt JSON.
    """
    output_path = Path(output_dir)
    if not output_path.exists():
        return []

    video_folders = sorted([d for d in output_path.iterdir() if d.is_dir()])
    reports = []

    for video_folder in video_folders:
        api_log_path = video_folder / "api_log.json"
        if not api_log_path.exists():
            continue

        try:
            with open(api_log_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Corrupt JSON in {api_log_path}: {e}")

        if not isinstance(data, dict):
            raise ValueError(f"Expected dict in {api_log_path}, got {type(data)}")

        group_ids = sorted(data.keys())
        for group_id in group_ids:
            entry = data[group_id]
            if not isinstance(entry, dict):
                continue
            if entry.get("status") != "COMPLETE":
                continue
            report = entry.get("report")
            if not isinstance(report, dict):
                continue

            kind = "shot"
            if group_id.startswith("event_"):
                kind = "event"
            elif group_id.startswith("pilot_"):
                kind = "pilot"

            report_copy = dict(report)
            report_copy["group_id"] = group_id
            report_copy["kind"] = kind
            reports.append(report_copy)

    return reports


def video_digest_prompt(video_id: str, reports: List[Dict[str, Any]], max_chars: int = 24000) -> str:
    """
    Build a compact evidence table prompt for ONE video.
    """
    lines = []
    for r in reports:
        inferred = r.get("inferred_technique", "UNKNOWN")
        observed = r.get("observed_animation", "UNKNOWN")
        conf = r.get("confidence", "LOW")

        # Skip LOW confidence with nothing visible
        if conf == "LOW":
            obs_lower = observed.lower()
            if "nothing" in obs_lower or "black" in obs_lower or "no visible" in obs_lower:
                continue

        # Skip if both technique and observed are UNKNOWN-like
        if inferred == "UNKNOWN" and observed == "UNKNOWN":
            continue

        group_id = r.get("group_id", "UNKNOWN")
        start_time = r.get("start_time", 0)
        end_time = r.get("end_time", 0)
        evidence_frames = r.get("evidence_frames", [])
        camera = r.get("camera_motion", "UNKNOWN")
        character = r.get("character_motion", "UNKNOWN")
        effects = r.get("visual_effects", "UNKNOWN")
        assets = r.get("required_assets", "UNKNOWN")
        capability = r.get("granthstudio_capability", "UNKNOWN")

        frames_str = ",".join(str(f) for f in evidence_frames) if evidence_frames else "none"
        line = (f"[{group_id} t={start_time}-{end_time}s frames=[{frames_str}]] "
                f"observed: {observed} | technique: {inferred} | camera: {camera} | "
                f"character: {character} | effects: {effects} | assets: {assets} | "
                f"capability: {capability} | conf: {conf}")
        lines.append(line)

    # Truncate if needed
    table = "\n".join(lines)
    if len(table) > max_chars:
        # Keep earliest lines
        kept_lines = []
        current_len = 0
        truncated_count = 0
        for line in lines:
            if current_len + len(line) + 1 <= max_chars:
                kept_lines.append(line)
                current_len += len(line) + 1
            else:
                truncated_count += 1
        table = "\n".join(kept_lines)
        if truncated_count > 0:
            table += f"\n[truncated: {truncated_count} more lines]"

    prompt = f"""Analyze the following evidence table for video {video_id}. Each line is a review group with observed animation, inferred technique, camera, character motion, effects, assets, capability class, and confidence.

EVIDENCE TABLE:
{table}

Return ONE JSON object with this exact schema:
{{
  "video_id": "{video_id}",
  "techniques": [
    {{
      "name": "string",
      "observed": "string",
      "evidence": [{{"group_id": "string", "frames": [int], "time": "start-end"}}],
      "camera": "string",
      "character_performance": "string",
      "effects": "string",
      "required_artwork": "string",
      "capability_class": "V2_REUSE|V2_EXTENSION|V3_ACTION|NEW_ARTWORK|UNKNOWN",
      "when_it_works": "string",
      "when_not_to_use": "string",
      "confidence": "LOW|MEDIUM|HIGH"
    }}
  ],
  "pacing_notes": "string",
  "audio_note": "NOT_ANALYZED"
}}

RULES:
- Use ONLY the table above. Do not hallucinate.
- Cite group_ids and frames for EVERY technique in the evidence array.
- Write "UNKNOWN" instead of guessing.
- Never infer editing software, lenses, hidden rigs, or screenplay text.
- Creative intention is a hypothesis, not fact.
- If a technique appears in multiple groups, merge them into one entry with all evidence.
- Keep pacing_notes concise.
- audio_note MUST be "NOT_ANALYZED".
"""
    return prompt


def parse_json_reply(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract the first JSON object from a reply. Strip code fences and leading prose.
    Returns None if no valid JSON dict found.
    """
    if not text:
        return None

    # Remove code fences
    text = re.sub(r"^```[a-zA-Z]*\n", "", text.strip())
    text = re.sub(r"\n```$", "", text.strip())

    # Find first { and matching }
    start = text.find("{")
    if start == -1:
        return None

    # Simple brace matching
    depth = 0
    end = -1
    for i, ch in enumerate(text[start:], start=start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i
                break

    if end == -1:
        return None

    json_str = text[start:end+1]
    try:
        parsed = json.loads(json_str)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    return None


def cross_video_prompt(digests: List[Dict[str, Any]]) -> str:
    """
    Build cross-video synthesis prompt from per-video digests.
    """
    # Serialize digests compactly
    digest_summaries = []
    for d in digests:
        vid = d.get("video_id", "UNKNOWN")
        techs = d.get("techniques", [])
        summary = f"VIDEO {vid}: {len(techs)} techniques"
        for t in techs:
            name = t.get("name", "unnamed")
            cap = t.get("capability_class", "UNKNOWN")
            conf = t.get("confidence", "LOW")
            evidence = t.get("evidence", [])
            ev_str = ", ".join(f"{e.get('group_id','?')}[{','.join(str(f) for f in e.get('frames',[]))}]" for e in evidence[:3])
            if len(evidence) > 3:
                ev_str += f" +{len(evidence)-3} more"
            summary += f"\n  - {name} ({cap}, {conf}): evidence {ev_str}"
        digest_summaries.append(summary)

    digests_text = "\n\n".join(digest_summaries)

    prompt = f"""Synthesize the following per-video technique digests into a master technique catalog.

PER-VIDEO DIGESTS:
{digests_text}

Return ONE JSON object with this exact schema:
{{
  "recipes": [
    {{
      "name": "string",
      "stage1_lesson": "string",
      "stage2_lesson": "string",
      "required_artwork": "string",
      "capability_class": "V2_REUSE|V2_EXTENSION|V3_ACTION|NEW_ARTWORK|UNKNOWN",
      "videos": ["video_id1", "video_id2"],
      "evidence": [{{"video_id": "string", "group_id": "string", "frames": [int]}}],
      "counterexample": "string",
      "when_not_to_use": "string",
      "confidence": "LOW|MEDIUM|HIGH"
    }}
  ],
  "gaps": ["string"]
}}

RULES:
- Merge the SAME technique across videos but KEEP every source reference in evidence.
- A lesson supported by only ONE video stays single-source (do not generalize).
- Stage 2 lessons may ONLY mention existing presets/assets in GENERAL TERMS.
- When capability_class is NEW_ARTWORK or V3_ACTION, Stage 2 MUST use "NEED_NEW: <missing capability>" (e.g., "NEED_NEW: pose arrangement for X", "NEED_NEW: renderer capability for Y").
- NEVER invent a preset ID.
- Reference music/dialogue is RESEARCH ONLY.
- Kimi gets NO new permissions: no rewriting EASY wording, no invented story events or dialogue, no timings, no music in production.
- counterexample: describe a case where this technique would fail or look wrong.
- gaps: list of missing capabilities or unanswered questions across all videos.
"""
    return prompt


def classify_recipe(recipe: Dict[str, Any]) -> str:
    """
    Classify recipe based on number of unique videos.
    GENERAL: >=3 videos, STYLE_SPECIFIC: exactly 2, EXPERIMENTAL: 1 or 0.
    """
    videos = recipe.get("videos", [])
    unique_videos = set(videos)
    count = len(unique_videos)
    if count >= 3:
        return "GENERAL"
    elif count == 2:
        return "STYLE_SPECIFIC"
    else:
        return "EXPERIMENTAL"


def usage_bucket(recipe: Dict[str, Any]) -> str:
    """
    Determine usage bucket based on classification and capability_class.
    """
    classification = classify_recipe(recipe)
    capability = recipe.get("capability_class", "UNKNOWN")

    if classification == "EXPERIMENTAL":
        return "RESEARCH_ONLY"

    if capability in ("V2_REUSE", "V2_EXTENSION"):
        return "USABLE_NOW"
    elif capability in ("NEW_ARTWORK", "V3_ACTION"):
        return "USEFUL_BUT_BLOCKED"
    else:
        return "RESEARCH_ONLY"


def compile_teacher(output_dir: str, ask: Callable[[str], str], workers: int = 9) -> Dict[str, Any]:
    """
    Main compilation pipeline.
    """
    reports = load_reports(output_dir)

    # Group by video_id
    by_video: Dict[str, List[Dict[str, Any]]] = {}
    for r in reports:
        vid = r.get("video_id", "UNKNOWN")
        by_video.setdefault(vid, []).append(r)

    video_ids = sorted(by_video.keys())
    digests = []
    failed_videos = []

    # Process each video in parallel
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_vid = {}
        for vid in video_ids:
            prompt = video_digest_prompt(vid, by_video[vid])
            future = executor.submit(ask, prompt)
            future_to_vid[future] = vid

        for future in as_completed(future_to_vid):
            vid = future_to_vid[future]
            try:
                reply = future.result()
            except Exception:
                failed_videos.append(vid)
                continue

            parsed = parse_json_reply(reply)
            if parsed is None:
                # Retry once
                prompt = video_digest_prompt(vid, by_video[vid])
                try:
                    reply2 = ask(prompt)
                    parsed = parse_json_reply(reply2)
                except Exception:
                    parsed = None

            if parsed is None:
                failed_videos.append(vid)
                continue

            # Validate required keys
            if not isinstance(parsed.get("techniques"), list):
                failed_videos.append(vid)
                continue

            digests.append(parsed)

    # Cross-video synthesis
    recipes = []
    gaps = []
    if digests:
        cross_prompt = cross_video_prompt(digests)
        cross_reply = ask(cross_prompt)
        cross_parsed = parse_json_reply(cross_reply)
        if cross_parsed is None:
            # Retry once
            cross_reply2 = ask(cross_prompt)
            cross_parsed = parse_json_reply(cross_reply2)

        if cross_parsed and isinstance(cross_parsed.get("recipes"), list):
            for recipe in cross_parsed["recipes"]:
                evidence = recipe.get("evidence", [])
                if not evidence:
                    continue  # Drop recipes without evidence
                classification = classify_recipe(recipe)
                bucket = usage_bucket(recipe)
                recipe["classification"] = classification
                recipe["usage_bucket"] = bucket
                recipes.append(recipe)
            gaps = cross_parsed.get("gaps", [])

    # Build playbook markdown
    playbook_lines = [
        "# Kimi animation teacher (read-only research hints; canon, schema and owner approvals always win)",
        "",
        "## How to use",
        "",
        "This playbook contains research hints derived from video review evidence. "
        "Stage 1 = film direction lessons (shot choices, composition, camera, character performance, image briefs, justified sound). "
        "Stage 2 = animation selection lessons (which EXISTING presets/pose arrangements execute a shot, NEED_NEW when missing). "
        "All lessons are hypotheses. Canon, schema, and owner approvals always win.",
        "",
        "## Stage 1: direction lessons",
        "",
    ]

    # Stage 1: direction lessons (USABLE_NOW or USEFUL_BUT_BLOCKED)
    stage1_recipes = [r for r in recipes if r["usage_bucket"] in ("USABLE_NOW", "USEFUL_BUT_BLOCKED")]
    for recipe in stage1_recipes:
        name = recipe.get("name", "Unnamed")
        lesson = recipe.get("stage1_lesson", "No lesson")
        evidence = recipe.get("evidence", [])
        when_not = recipe.get("when_not_to_use", "UNKNOWN")
        conf = recipe.get("confidence", "LOW")
        classification = recipe.get("classification", "EXPERIMENTAL")

        # Format evidence references
        ev_refs = []
        for e in evidence:
            vid = e.get("video_id", "?")
            gid = e.get("group_id", "?")
            frames = e.get("frames", [])
            frames_str = ",".join(str(f) for f in frames) if frames else "none"
            ev_refs.append(f"video {vid} frames [{frames_str}] ({gid})")
        ev_str = "; ".join(ev_refs) if ev_refs else "no evidence"

        playbook_lines.append(f"### {name}")
        playbook_lines.append(f"**Lesson:** {lesson}")
        playbook_lines.append(f"**Evidence:** {ev_str}")
        playbook_lines.append(f"**When not to use:** {when_not}")
        playbook_lines.append(f"**Confidence:** {conf}")
        playbook_lines.append(f"**Classification:** {classification}")
        playbook_lines.append("")

    playbook_lines.append("## Stage 2: execution lessons")
    playbook_lines.append("")

    # USABLE_NOW recipes with required artwork
    usable_now = [r for r in recipes if r["usage_bucket"] == "USABLE_NOW"]
    for recipe in usable_now:
        name = recipe.get("name", "Unnamed")
        lesson = recipe.get("stage2_lesson", "No lesson")
        artwork = recipe.get("required_artwork", "UNKNOWN")
        evidence = recipe.get("evidence", [])
        ev_refs = []
        for e in evidence:
            vid = e.get("video_id", "?")
            gid = e.get("group_id", "?")
            frames = e.get("frames", [])
            frames_str = ",".join(str(f) for f in frames) if frames else "none"
            ev_refs.append(f"video {vid} frames [{frames_str}] ({gid})")
        ev_str = "; ".join(ev_refs) if ev_refs else "no evidence"

        playbook_lines.append(f"### {name} (USABLE_NOW)")
        playbook_lines.append(f"**Lesson:** {lesson}")
        playbook_lines.append(f"**Required artwork:** {artwork}")
        playbook_lines.append(f"**Evidence:** {ev_str}")
        playbook_lines.append("")

    # USEFUL_BUT_BLOCKED recipes marked NEED_NEW
    useful_blocked = [r for r in recipes if r["usage_bucket"] == "USEFUL_BUT_BLOCKED"]
    for recipe in useful_blocked:
        name = recipe.get("name", "Unnamed")
        lesson = recipe.get("stage2_lesson", "No lesson")
        capability = recipe.get("capability_class", "UNKNOWN")
        evidence = recipe.get("evidence", [])
        ev_refs = []
        for e in evidence:
            vid = e.get("video_id", "?")
            gid = e.get("group_id", "?")
            frames = e.get("frames", [])
            frames_str = ",".join(str(f) for f in frames) if frames else "none"
            ev_refs.append(f"video {vid} frames [{frames_str}] ({gid})")
        ev_str = "; ".join(ev_refs) if ev_refs else "no evidence"

        playbook_lines.append(f"### {name} (USEFUL_BUT_BLOCKED)")
        playbook_lines.append(f"**Lesson:** {lesson}")
        playbook_lines.append(f"**NEED_NEW:** {capability} - missing capability for this technique")
        playbook_lines.append(f"**Evidence:** {ev_str}")
        playbook_lines.append("")

    playbook_lines.append("## Research only")
    playbook_lines.append("")

    experimental = [r for r in recipes if r["usage_bucket"] == "RESEARCH_ONLY"]
    for recipe in experimental:
        name = recipe.get("name", "Unnamed")
        lesson1 = recipe.get("stage1_lesson", "No lesson")
        lesson2 = recipe.get("stage2_lesson", "No lesson")
        evidence = recipe.get("evidence", [])
        ev_refs = []
        for e in evidence:
            vid = e.get("video_id", "?")
            gid = e.get("group_id", "?")
            frames = e.get("frames", [])
            frames_str = ",".join(str(f) for f in frames) if frames else "none"
            ev_refs.append(f"video {vid} frames [{frames_str}] ({gid})")
        ev_str = "; ".join(ev_refs) if ev_refs else "no evidence"

        playbook_lines.append(f"### {name} (EXPERIMENTAL)")
        playbook_lines.append(f"**Stage 1:** {lesson1}")
        playbook_lines.append(f"**Stage 2:** {lesson2}")
        playbook_lines.append(f"**Evidence:** {ev_str}")
        playbook_lines.append("")

    playbook_lines.append("## Sound")
    playbook_lines.append("")
    playbook_lines.append("Audio was only checked for silence; narration, SFX and music are NOT analyzed in this run, so no sound lesson is claimed.")
    playbook_lines.append("")

    playbook_lines.append("## Gaps and uncertainties")
    playbook_lines.append("")
    for gap in gaps:
        playbook_lines.append(f"- {gap}")
    if not gaps:
        playbook_lines.append("(none)")
    playbook_lines.append("")

    playbook_md = "\n".join(playbook_lines)

    techniques_dict = {
        "schema": 1,
        "recipes": recipes,
        "gaps": gaps,
        "failed_videos": failed_videos
    }

    stats = {
        "reports": len(reports),
        "videos": len(video_ids),
        "recipes": len(recipes)
    }

    return {
        "playbook_md": playbook_md,
        "techniques": techniques_dict,
        "failed_videos": failed_videos,
        "stats": stats
    }


def write_outputs(output_dir: str, result: Dict[str, Any]) -> None:
    """
    Write KIMI_ANIMATION_PLAYBOOK.md and MASTER_TECHNIQUES.json (merge into _teacher key).
    Backup existing files as .bak_before_teacher. Atomic tmp+replace. UTF-8.
    Raises ValueError on corrupt existing JSON.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Write playbook
    playbook_path = output_path / "KIMI_ANIMATION_PLAYBOOK.md"
    if playbook_path.exists():
        backup_path = output_path / "KIMI_ANIMATION_PLAYBOOK.md.bak_before_teacher"
        playbook_path.replace(backup_path)

    tmp_playbook = output_path / "KIMI_ANIMATION_PLAYBOOK.md.tmp"
    with open(tmp_playbook, "w", encoding="utf-8") as f:
        f.write(result["playbook_md"])
    tmp_playbook.replace(playbook_path)

    # Write/update MASTER_TECHNIQUES.json
    master_path = output_path / "MASTER_TECHNIQUES.json"
    existing = {}
    if master_path.exists():
        backup_path = output_path / "MASTER_TECHNIQUES.json.bak_before_teacher"
        master_path.replace(backup_path)
        try:
            with open(backup_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Corrupt JSON in {master_path}: {e}")

    existing["_teacher"] = result["techniques"]

    tmp_master = output_path / "MASTER_TECHNIQUES.json.tmp"
    with open(tmp_master, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)
    tmp_master.replace(master_path)


def main(argv: Optional[List[str]] = None, ask: Optional[Callable[[str], str]] = None) -> int:
    """
    CLI entry point.
    --output (required), --workers (default 9), --dry-run (prints stats only, no ask calls).
    If ask is None, build from nvidia_scheduler.NvidiaScheduler.
    Prints JSON stats and exits 0 if failed_videos empty else 1.
    """
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--workers", type=int, default=9)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if args.dry_run:
        reports = load_reports(args.output)
        by_video: Dict[str, int] = {}
        for r in reports:
            vid = r.get("video_id", "UNKNOWN")
            by_video[vid] = by_video.get(vid, 0) + 1
        stats = {
            "reports": len(reports),
            "videos": len(by_video),
            "per_video": by_video
        }
        print(json.dumps(stats, indent=2))
        return 0

    # Build ask from NvidiaScheduler if not provided
    if ask is None:
        # Add repo_parent/animation_research_tool to sys.path
        repo_parent = Path(__file__).resolve().parents[3]  # research/pieces/ -> repo root
        anim_tool_path = repo_parent / "animation_research_tool"
        if str(anim_tool_path) not in sys.path:
            sys.path.insert(0, str(anim_tool_path))

        try:
            from nvidia_scheduler import NvidiaScheduler
        except ImportError as e:
            print(json.dumps({"error": f"Failed to import NvidiaScheduler: {e}"}))
            return 1

        scheduler = NvidiaScheduler(
            model="nvidia/nemotron-3-ultra-550b-a55b",
            read_timeout=900,
            max_calls=60
        )

        def ask_wrapper(prompt: str) -> str:
            try:
                # Add thinking off via chat_template_kwargs
                reply = scheduler.ask(prompt, chat_template_kwargs={"enable_thinking": False})
                return reply or ""
            except Exception:
                return ""

        ask = ask_wrapper

    result = compile_teacher(args.output, ask, workers=args.workers)
    write_outputs(args.output, result)

    stats = result["stats"]
    stats["failed_videos"] = result["failed_videos"]
    print(json.dumps(stats, indent=2))

    return 0 if not result["failed_videos"] else 1


if __name__ == "__main__":
    sys.exit(main())
