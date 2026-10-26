"""Story-first planning (owner 2026-10-26): ONE Kimi call reads the whole Adhyay and decides the STORIES (one story, half a story, two or three) and the SCENES inside each story;
code validates the split, Nemotron cross-checks it, and the run STOPS at the owner's gate (approval of the split's exact hash). Only then is each story directed (director_test.py).
The model outputs only {stories, unfilmed_ranges}; code adds chapter, source range and the source hash (a model must never type a hash).
Every ovi of the chapter must be owned exactly once: by one scene, or by an explicit unfilmed range with a reason. Nothing here renders, approves or spends beyond the planner's own calls
(director_test.py --plan-stories: at most TWO director calls: the first answer plus either one JSON re-ask or the single repair round)."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("director_test", ROOT / "scripts" / "source" / "director_test.py")
dt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dt)

ARCS = ["complete", "begins", "continues", "ends", "middle", "uncertain"]
UNFILMED_KINDS = ["invocation", "background", "commentary", "closing", "editorial_omission"]
MAX_SCENES_PER_PART, MAX_SHOTS_PER_PART = 2, 12            # provisional (Codex): direction output must fit max_tokens with reasoning; larger stories are directed in ordered parts

TEXT = {"type": "string", "minLength": 1, "maxLength": 300, "pattern": r"\S"}
RANGE = {"type": "array", "minItems": 2, "maxItems": 2, "items": {"type": "integer", "minimum": 1}}
MODEL_OUT = {
    "type": "object", "additionalProperties": False, "required": ["stories", "unfilmed_ranges"],
    "properties": {
        "stories": {"type": "array", "minItems": 1, "maxItems": 6, "items": {
            "type": "object", "additionalProperties": False, "required": ["story_id", "title", "ovi_range", "arc", "boundary_evidence", "scenes"],
            "properties": {
                "story_id": {"type": "string", "pattern": r"^A[1-9][0-9]?-T[1-9][0-9]?$"},
                "title": TEXT, "ovi_range": RANGE, "arc": {"enum": ARCS},
                "boundary_evidence": {"type": "array", "minItems": 2, "maxItems": 6, "items": {
                    "type": "object", "additionalProperties": False, "required": ["ovi", "reason"], "properties": {"ovi": dt.REF, "reason": TEXT}}},
                "scenes": {"type": "array", "minItems": 1, "maxItems": 9, "items": {
                    "type": "object", "additionalProperties": False, "required": ["scene_id", "ovi_range", "brief", "context_ovi_ids", "shot_budget"],
                    "properties": {"scene_id": {"type": "string", "pattern": r"^S[1-9]$"}, "ovi_range": RANGE, "brief": TEXT,
                                   "context_ovi_ids": {"type": "array", "maxItems": 6, "items": dt.REF}, "shot_budget": {"type": "integer", "minimum": 2, "maximum": 16}}}}}}},
        "unfilmed_ranges": {"type": "array", "maxItems": 12, "items": {
            "type": "object", "additionalProperties": False, "required": ["ovi_range", "kind", "reason"],
            "properties": {"ovi_range": RANGE, "kind": {"enum": UNFILMED_KINDS}, "reason": TEXT}}}}}


def sha_of(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def validate_split(out, ovi_numbers: list, chapter: int) -> tuple[list, list]:
    """(errors, warnings) for the MODEL's output. ovi_numbers: every ovi number of the chapter."""
    errors = [f"{'/'.join(map(str, e.path)) or 'split'}: {e.message}" for e in jsonschema.Draft202012Validator(MODEL_OUT).iter_errors(out)]
    if errors:
        return errors, []
    if not ovi_numbers or sorted(set(ovi_numbers)) != list(range(min(ovi_numbers), max(ovi_numbers) + 1)):
        return ["the chapter's ovi numbers must be a non-empty, contiguous, unique list"], []
    numset = set(ovi_numbers)
    warnings, lo, hi = [], min(ovi_numbers), max(ovi_numbers)
    owner, prev_story_end, prev_scene_no = {}, 0, 0
    ref = lambda n: f"A{chapter}:{n}"

    def own(a, b, label):
        if a > b or a < lo or b > hi:
            errors.append(f"{label}: range [{a}, {b}] is reversed or outside the chapter [{lo}, {hi}]")
            return
        for n in range(a, b + 1):
            if n not in numset:
                errors.append(f"{label}: owns ovi {n}, which does not exist in this chapter")
            elif n in owner:
                errors.append(f"{label}: ovi {n} is already owned by {owner[n]}")
            else:
                owner[n] = label
    for k, st in enumerate(out["stories"], 1):
        sid = st["story_id"]
        if sid != f"A{chapter}-T{k}":
            errors.append(f"{sid}: story ids must be A{chapter}-T1, A{chapter}-T2 ... in order (this is #{k})")
        a, b = st["ovi_range"]
        if a <= prev_story_end:
            errors.append(f"{sid}: stories must be in order and may not overlap (starts at {a} after {prev_story_end})")
        prev_story_end, prev_scene_end = max(prev_story_end, b), a - 1
        for sc in st["scenes"]:
            no = int(sc["scene_id"][1:])
            if no != prev_scene_no + 1:
                errors.append(f"{sc['scene_id']}: scene numbers are chapter-wide and consecutive (expected S{prev_scene_no + 1})")
            prev_scene_no = no
            sa, sb = sc["ovi_range"]
            if sa <= prev_scene_end:
                errors.append(f"{sc['scene_id']}: scenes must be in order inside a story ({sa} after {prev_scene_end})")
            prev_scene_end = max(prev_scene_end, sb)
            own(sa, sb, f"{sid}/{sc['scene_id']}")
            if len(set(sc["context_ovi_ids"])) != len(sc["context_ovi_ids"]):
                errors.append(f"{sc['scene_id']}: context references must be unique")
            for c in sc["context_ovi_ids"]:
                m = re.fullmatch(r"A(\d+):(\d+)", c)
                if int(m[1]) != chapter or not lo <= int(m[2]) <= hi:
                    errors.append(f"{sc['scene_id']}: context {c} is outside chapter {chapter}")
                elif sa <= int(m[2]) <= sb:
                    errors.append(f"{sc['scene_id']}: context {c} lies inside the scene's own range; context points outside it")
        first, last = st["scenes"][0]["ovi_range"][0], st["scenes"][-1]["ovi_range"][1]
        if [a, b] != [first, last]:
            errors.append(f"{sid}: story range {[a, b]} must equal its first scene start to its last scene end {[first, last]}")
        cited = {e["ovi"] for e in st["boundary_evidence"]}
        for need in (ref(a), ref(b)):
            if need not in cited:
                errors.append(f"{sid}: boundary_evidence must cite the story's first and last ovi ({need})")
        for e in cited:
            m = re.fullmatch(r"A(\d+):(\d+)", e)
            if int(m[1]) != chapter or not a <= int(m[2]) <= b:
                errors.append(f"{sid}: boundary evidence {e} is outside the story")
        budget = sum(sc["shot_budget"] for sc in st["scenes"])
        if budget > MAX_SHOTS_PER_PART:
            warnings.append(f"{sid}: {budget} shots in total: it will be directed in several ordered parts")
    for k, u in enumerate(out["unfilmed_ranges"], 1):
        own(u["ovi_range"][0], u["ovi_range"][1], f"unfilmed#{k}({u['kind']})")
    missing = sorted(set(ovi_numbers) - set(owner))
    if missing:
        errors.append(f"ovis not owned by any scene or unfilmed range: {_ranges(missing)}")
    if len(out["stories"]) > 3:
        warnings.append(f"{len(out['stories'])} stories (the owner expected one to three)")
    return errors, warnings


def _ranges(nums: list) -> str:
    out, start, prev = [], None, None
    for n in nums:
        if start is None:
            start = prev = n
        elif n == prev + 1:
            prev = n
        else:
            out.append(f"{start}-{prev}" if start != prev else str(start))
            start = prev = n
    out.append(f"{start}-{prev}" if start != prev else str(start))
    return ", ".join(out)


def build_macro(out: dict, chapter: int, ovi_numbers: list, source_sha256: str) -> dict:
    """The full, hashed macro: what the owner approves."""
    return {"schema_version": 1, "chapter": chapter, "source_sha256": source_sha256, "source_range": [min(ovi_numbers), max(ovi_numbers)], **out}


def parts(macro: dict) -> list:
    """Code-derived direction parts: ordered groups of whole scenes of one story, at most 2 scenes and 12 shots each (a story is never split just to fit; it is directed in ordered parts)."""
    res = []
    for st in macro["stories"]:
        group, shots, k = [], 0, 0
        for sc in st["scenes"] + [None]:
            if group and (sc is None or len(group) == MAX_SCENES_PER_PART or shots + sc["shot_budget"] > MAX_SHOTS_PER_PART):
                k += 1
                res.append({"story_id": st["story_id"], "part_id": f"{st['story_id']}-P{k}", "scene_ids": [s["scene_id"] for s in group], "shot_budget": shots})
                group, shots = [], 0
            if sc is not None:
                group.append(sc)
                shots += sc["shot_budget"]
    return res


# ----------------------------------------------------------------------------- prompts

MACRO_RULES = """You read ONE whole chapter (Adhyay) of the Marathi scripture Shri Gajanan Vijay and decide how it divides into STORIES and SCENES for a short devotional film.
S1. A STORY is one connected arc of the narrative: the same participants and situation, ending in a consequence or a teaching. A change of place alone is not a new story. The chapter may hold ONE complete story, only a PART of a story (it may begin earlier or continue in the next chapter: say so with "arc"), or two or three stories. Never split or merge only to hit a number.
S2. Inside a story, a SCENE is a stretch of consecutive ovis with one place and time and one change (its turn). Each scene gets a "shot_budget" of 2 to 16 (each shot is 6 seconds; use the smallest budget that tells the scene; the narration timing may later raise it).
S3. EVERY ovi of the chapter belongs to exactly one scene or to exactly one unfilmed range. Invocation, praise, the author's reasoning, lists and closing remarks are unfilmed (a narrator can speak them) unless the ovis themselves show an event; give each unfilmed range its kind and a one-line reason. Do not leave an event of the story unfilmed.
S4. Use only the MATERIALS. Cite ovis as A<chapter>:<n>. Every story's "boundary_evidence" cites its first and last ovi (and any ovi that proves the boundary) with a reason that names what happens there. Do not invent events, people or causes. "context_ovi_ids" lists ovis outside a scene that the director needs to read (for example a shared boundary ovi); an ovi is OWNED by only one scene.
S5. Story ids are A<chapter>-T1, A<chapter>-T2 ... in order; scene ids are S1, S2 ... S9 numbered consecutively across the whole chapter (at most nine); stories and scenes are in reading order and never overlap. Every text field is at most 300 characters; keep reasons and briefs short."""

MACRO_SCHEMA_TEXT = """OUTPUT: ONE JSON object only, with exactly these keys:
{"stories": [{"story_id": "A1-T1", "title": "...", "ovi_range": [first, last], "arc": "complete|begins|continues|ends|middle|uncertain",
              "boundary_evidence": [{"ovi": "A1:84", "reason": "..."}, {"ovi": "A1:144", "reason": "..."}],
              "scenes": [{"scene_id": "S1", "ovi_range": [first, last], "brief": "what happens and what changes", "context_ovi_ids": [], "shot_budget": 4}]}],
 "unfilmed_ranges": [{"ovi_range": [first, last], "kind": "invocation|background|commentary|closing|editorial_omission", "reason": "..."}]}
A story's ovi_range runs from its first scene's first ovi to its last scene's last ovi; if some ovis inside it are not filmed, they appear in unfilmed_ranges. Do NOT output hashes, chapter numbers or anything else.
All shown keys are required; additional keys are forbidden in every object. Ranges are inclusive positive-integer pairs. Limits: 1-6 stories; 1-9 scenes per story and at most 9 scenes in the chapter; 2-6 boundary-evidence entries per story; 0-6 context references per scene (they point OUTSIDE the scene's own range); 0-12 unfilmed ranges. Text values must be nonempty and at most 300 characters."""


def build_macro_prompt(files: dict, ovis: dict, chapter: int) -> tuple[str, str]:
    ana, add = files["analysis"].splitlines(), files["addendum"].splitlines()
    glossary = files["glossary"].splitlines()
    overview = dt.section(ana, r"^## 1\. Chapter overview", r"^## 2\.")
    story_list = dt.section(ana, r"^## 2\. Story list", r"^## 3\.")
    continuity = dt.section(add, r"^## D\.", r"^## E\.")
    gloss = dt.section(glossary, r"^## Adhyay 1$", r"^## Adhyay 2")
    system = f"{MACRO_RULES}\n\n{MACRO_SCHEMA_TEXT}"
    user = (f"CHAPTER {chapter}: ovis {min(ovis)}-{max(ovis)}. Decide the stories and scenes.\n\n"
            f"=== THE MARATHI OVIS (exact text, numbered) ===\n" + "\n".join(f"A{chapter}:{k}: {ovis[k]}" for k in sorted(ovis)) + "\n\n"
            f"=== OWNER'S RESEARCH: chapter overview ===\n{overview}\n\n"
            f"=== EARLIER RESEARCH: candidate story list, not approved boundaries; derive boundaries independently from the numbered ovis ===\n{story_list}\n\n"
            f"=== OWNER'S RESEARCH: continuity ===\n{continuity}\n\n"
            f"=== OWNER'S FINAL ANSWERS (settled) ===\n{files['answers']}\n\n"
            f"=== GLOSSARY (owner, this chapter) ===\n{gloss}\n")
    return system, user


# ----------------------------------------------------------------------------- cross-check: binary questions with evidence

MACRO_QUESTIONS = [
    ("M1", "Does every story and scene boundary reflect what the cited ovis actually say?"),
    ("M2", "Does each story hold ONE connected arc (same participants and situation, one consequence or teaching)?"),
    ("M3", "Are distinct events kept distinguishable: nothing unrelated merged into one scene, and no single event split without a reason?"),
    ("M4", "Are chronology and the arc labels (complete / begins / continues / ends) true to the ovis?"),
    ("M5", "Are the unfilmed ranges (invocation, background, commentary, closing) classified faithfully?"),
    ("M6", "Is every event of the narrative inside a scene, with no event hidden in an unfilmed range?"),
]
MACRO_IDS = {q for q, _ in MACRO_QUESTIONS}
MACRO_REVIEW_SYS = ("You are an independent reviewer of a proposed story/scene split of one chapter of a devotional scripture. Judge ONLY against the MATERIALS (exact Marathi ovis and the owner's research). "
                    "Answer EVERY question with yes or no and cite ovi numbers as evidence. Answer 'no' only when you can name what in the ovis contradicts the split.\n"
                    + "\n".join(f"{q}. {t}" for q, t in MACRO_QUESTIONS)
                    + '\nOUTPUT: ONE JSON object only: {"answers": [{"q": "M1", "where": "macro or a story/scene id", "answer": "yes" or "no", "evidence": "...", "fix": "one sentence, only for no"}]}')


def clean_macro_review(obj, ids=None) -> dict:
    """PASS | BLOCK | NO_CHECK. All six questions need a well-formed answer with evidence and a real 'where' (macro, a story or scene id); anything else is NO_CHECK."""
    bad = {"verdict": "NO_CHECK", "problems": [], "missing": sorted(MACRO_IDS), "why": "no usable answers (not a JSON object with an 'answers' list)"}
    if not isinstance(obj, dict) or not isinstance(obj.get("answers"), list) or not obj["answers"]:
        return bad
    answered, problems = set(), []
    for a in obj["answers"]:
        w = a.get("where") if isinstance(a, dict) else None
        if not (isinstance(a, dict) and a.get("q") in MACRO_IDS and a.get("answer") in ("yes", "no") and isinstance(a.get("evidence"), str) and re.search(r"\d", a["evidence"])
                and isinstance(w, str) and (w == "macro" or ids is None or w in ids)):               # the evidence must cite at least one ovi number
            why = "an answer was rejected: " + ("not an object" if not isinstance(a, dict) else f"question {a.get('q')!r}, where={str(w)[:60]!r} is not 'macro' or a real story/scene id" if isinstance(w, str) and not (w == "macro" or ids is None or w in ids)
                                                   else "a question id, a yes/no, or the evidence (it must cite an ovi number) is malformed")
            return {**bad, "why": why}
        answered.add(a["q"])
        if a["answer"] == "no":
            problems.append({"where": w, "kind": a["q"], "problem": a["evidence"].strip(), "fix": a.get("fix") if isinstance(a.get("fix"), str) else ""})
    missing = sorted(MACRO_IDS - answered)
    if missing:
        return {"verdict": "NO_CHECK", "problems": problems, "missing": missing, "why": f"questions not answered: {missing}"}
    return {"verdict": "BLOCK" if problems else "PASS", "problems": problems, "missing": []}


def _review(agent, materials: str, out: dict, log: list) -> dict:
    ids = {x for st in out["stories"] for x in [st["story_id"]] + [sc["scene_id"] for sc in st["scenes"]]}
    try:
        obj = dt._ask(agent, MACRO_REVIEW_SYS, materials + "\n\n=== PROPOSED SPLIT ===\n" + json.dumps(out, ensure_ascii=False), log, "macro_review", 16000, must=False)
    except Exception as exc:                                                    # an unreachable reviewer is a missing check, not a crash
        log.append({"step": "macro_review", "agent": agent.name, "error": type(exc).__name__})
        obj = None
    return {"model": agent.name, **clean_macro_review(obj, ids)}


def plan_stories(director, reviewers: list, files: dict, ovis: dict, chapter: int, source_sha256: str, max_tokens: int = 16000) -> dict:
    """One planning pass: at most two director calls (first answer + either one JSON re-ask or the single repair round); the re-review after a repair only checks it."""
    system, materials = build_macro_prompt(files, ovis, chapter)
    numbers = sorted(ovis)
    log, repairs = [], []
    res = {"chapter": chapter, "result": "FAILED", "errors": [], "warnings": [], "macro": None, "macro_sha256": None, "parts": [], "reviews": [], "final_reviews": [], "repairs": repairs, "calls": log}
    out, calls = None, 0
    for attempt in range(2):
        calls += 1
        out = dt._ask(director, system, materials if attempt == 0 else materials + "\n\nYour last reply was not a single JSON object. Reply with ONLY the JSON object.", log, "macro", max_tokens)
        if out is not None:
            break
    if out is None:
        res["errors"] = ["the reply was not a JSON object"]
        return res
    errors, warnings = validate_split(out, numbers, chapter)
    can_repair = calls < 2

    def repair(problems: list, label: str):
        nonlocal out, errors, warnings
        obj = dt._ask(director, system, materials + "\n\nYOUR PREVIOUS SPLIT:\n" + json.dumps(out, ensure_ascii=False) + "\n\nFIX THESE PROBLEMS (check each against the ovis; ignore any that are wrong). Return the full corrected JSON object:\n- "
                      + "\n- ".join(problems[:30]), log, label, max_tokens)
        e2, w2 = validate_split(obj, numbers, chapter) if isinstance(obj, dict) else (["not a JSON object"], [])
        repairs.append({"label": label, "problems_sent": problems[:30], "status": "USED" if not e2 else "REJECTED (still invalid: " + "; ".join(e2[:3]) + ")"})
        if not e2:
            res["split_before_repair"], out, errors, warnings = out, obj, [], w2
    if errors and can_repair and jsonschema.Draft202012Validator(MODEL_OUT).is_valid(out):
        can_repair = False
        repair(errors, "macro_repair")
    res["errors"], res["warnings"] = errors, warnings
    if errors:
        res["result"], res["raw_split"] = "INVALID", out                         # kept for the owner to read; it is NOT a macro and cannot be approved
        return res
    if reviewers:
        reviews = [_review(r, materials, out, log) for r in reviewers]
        final = reviews
        res["reviews"] = reviews
        blocked = [f"[{rv['model'].split('/')[-1]}] {p['where']} {p['kind']}: {p['problem']} Fix: {p['fix']}" for rv in reviews for p in rv["problems"]]
        if blocked and can_repair:
            repair(blocked, "macro_review_repair")
            if repairs and repairs[-1]["status"] == "USED":
                final = res["final_reviews"] = [_review(r, materials, out, log) for r in reviewers]
        verdicts = {r["verdict"] for r in final}
        res["result"] = "REVIEW_BLOCKED" if "BLOCK" in verdicts else "NO_CHECK" if "NO_CHECK" in verdicts else "VALID"
    else:
        res["result"] = "UNREVIEWED"
    macro = build_macro(out, chapter, numbers, source_sha256)
    res.update(macro=macro, macro_sha256=sha_of(macro), parts=parts(macro), errors=errors, warnings=warnings)
    return res


def split_summary(macro: dict) -> dict:
    """Scene and shot counts and the runtime, computed from the canonical split (never typed by hand). shot_budget is an ALLOCATION; actual shots exist only after direction."""
    rows = [{"scene_id": sc["scene_id"], "story_id": st["story_id"], "ovi_range": sc["ovi_range"], "shots": sc["shot_budget"], "seconds": 6 * sc["shot_budget"]} for st in macro["stories"] for sc in st["scenes"]]
    total = sum(r["shots"] for r in rows)
    return {"stories": len(macro["stories"]), "scenes": len(rows), "shots": total, "seconds": 6 * total, "rows": rows}


def fmt_runtime(seconds: int) -> str:
    return f"{seconds // 60} minutes {seconds % 60} seconds"


def render_doc(template: str, macro: dict, macro_hash: str, edits: dict, reviews: list | None = None) -> str:
    """Fills the owner's story text with numbers and canonical texts taken from the split itself."""
    sm = split_summary(macro)
    table = "\n".join(["| Scene | Ovi | Shots (allocation) | Seconds |", "|---|---|---|---|"] + [f"| {r['scene_id']} | {r['ovi_range'][0]}-{r['ovi_range'][1]} | {r['shots']} | {r['seconds']} |" for r in sm["rows"]]
                       + [f"| **Total** | | **{sm['shots']}** | **{sm['seconds']}** |"])
    st = macro["stories"][0]
    app = ["### Canonical scene briefs (verbatim from the split)", ""] + [f"- **{x['scene_id']}** (ovi {x['ovi_range'][0]}-{x['ovi_range'][1]}, {x['shot_budget']} shots): {x['brief']}" + (f" Context: {', '.join(x['context_ovi_ids'])}." if x["context_ovi_ids"] else "") for x in st["scenes"]]
    app += ["", "### Boundary evidence (verbatim)", ""] + [f"- {e['ovi']}: {e['reason']}" for e in st["boundary_evidence"]]
    app += ["", "### Unfilmed ranges (narrator or omitted, verbatim)", ""] + [f"- ovi {u['ovi_range'][0]}-{u['ovi_range'][1]} [{u['kind']}]: {u['reason']}" for u in macro["unfilmed_ranges"]]
    app += ["", "### Direction notes (handed to the director)", ""] + [f"- {n}" for n in edits.get("direction_notes", [])]
    app += ["", "### Research evidence kept but NOT narrated or shown", ""] + [f"- {k}: {v}" for k, v in edits.get("research_evidence_not_narrated", {}).items()]
    cc = []
    for rv in reviews or []:
        cc.append(f"- `{rv['model']}`: **{rv['verdict']}**" + (f" (reason: {rv['why']})" if rv.get("why") else ""))
        cc += [f"  - {p['where']} [{p['kind']}]: {p['problem']}" for p in rv["problems"]]
    out = template
    per_scene = {f"{{{{{r['scene_id']}_SHOTS}}}}": str(r["shots"]) for r in sm["rows"]}
    for key, val in per_scene.items():
        out = out.replace(key, val)
    for key, val in {"{{CROSSCHECK}}": "\n".join(cc) or "- (no cross-check was run)", "{{TITLE}}": st["title"], "{{HASH}}": macro_hash, "{{SCENES}}": str(sm["scenes"]), "{{SHOTS}}": str(sm["shots"]), "{{SECONDS}}": str(sm["seconds"]),
                     "{{RUNTIME}}": fmt_runtime(sm["seconds"]), "{{TABLE}}": table, "{{APPENDIX}}": "\n".join(app)}.items():
        out = out.replace(key, val)
    return out


def revise_split(out: dict, reviewers: list, files: dict, ovis: dict, chapter: int, source_sha256: str, base_hash: str, note: str) -> dict:
    """An owner-directed EDIT of a checked split (no director call, no Kimi spend): the same validation and the same cross-check as a planned split."""
    system, materials = build_macro_prompt(files, ovis, chapter)
    numbers = sorted(ovis)
    log = []
    res = {"chapter": chapter, "result": "FAILED", "errors": [], "warnings": [], "macro": None, "macro_sha256": None, "parts": [], "reviews": [], "final_reviews": [], "repairs": [], "calls": log,
           "revised_from": base_hash, "note": note}
    errors, warnings = validate_split(out, numbers, chapter)
    res["errors"], res["warnings"] = errors, warnings
    if errors:
        res["result"], res["raw_split"] = "INVALID", out
        return res
    if reviewers:
        reviews = [_review(r, materials, out, log) for r in reviewers]
        res["reviews"] = reviews
        verdicts = {r["verdict"] for r in reviews}
        res["result"] = "REVIEW_BLOCKED" if "BLOCK" in verdicts else "NO_CHECK" if "NO_CHECK" in verdicts else "VALID"
    else:
        res["result"] = "UNREVIEWED"
    macro = build_macro(out, chapter, numbers, source_sha256)
    res.update(macro=macro, macro_sha256=sha_of(macro), parts=parts(macro))
    return res


# ----------------------------------------------------------------------------- report and command line

def macro_text(res: dict) -> str:
    L = [f"# Story split, Adhyay {res['chapter']}: {res['result']}", "", "DRAFT for the owner's approval. Nothing is directed, rendered or approved. VALID = the code coverage checks passed and the cross-check answered every question 'yes'.",
         f"Macro hash (what you approve): `{res['macro_sha256']}`", ""]
    for call in res["calls"]:
        L.append(f"- {call.get('step')} `{call.get('agent')}`: HTTP {call.get('status')}, {call.get('wall_s')} s, finish {call.get('finish')}, usage {call.get('usage')}" + (f", error {call['error']}" if call.get("error") else ""))
    if res["errors"]:
        L += ["", "Validator ERRORS:"] + [f"- {e}" for e in res["errors"]]
    if res["warnings"]:
        L += ["", "Warnings:"] + [f"- {w}" for w in res["warnings"]]
    for label, group in (("first split", res["reviews"]), ("repaired split", res["final_reviews"])):
        for rv in group:
            L += ["", f"Reviewer `{rv['model']}` ({label}): **{rv['verdict']}**" + (f", missing {rv['missing']}" if rv.get("missing") else "") + (f" (reason: {rv['why']})" if rv.get("why") else "")]
            L += [f"- {p['where']} [{p['kind']}] {p['problem']} Fix: {p['fix']}" for p in rv["problems"]]
    for rp in res["repairs"]:
        L += ["", f"Repair `{rp['label']}`: **{rp['status']}**"]
    if res.get("raw_split"):
        L += ["", "Rejected raw output (for reading only):", "```json", json.dumps(res["raw_split"], ensure_ascii=False, indent=1)[:6000], "```"]
    m = res["macro"]
    if m:
        L += ["", f"Source: chapter {m['chapter']}, ovi {m['source_range'][0]}-{m['source_range'][1]}", ""]
        for st in m["stories"]:
            L += [f"## {st['story_id']}: {st['title']} (ovi {st['ovi_range'][0]}-{st['ovi_range'][1]}, arc {st['arc']})"]
            L += [f"- boundary {e['ovi']}: {e['reason']}" for e in st["boundary_evidence"]]
            L += [f"- **{sc['scene_id']}** ovi {sc['ovi_range'][0]}-{sc['ovi_range'][1]}, {sc['shot_budget']} shots: {sc['brief']}" + (f" (context {', '.join(sc['context_ovi_ids'])})" if sc["context_ovi_ids"] else "") for sc in st["scenes"]]
            L.append("")
        L += ["## Unfilmed (narrator or omitted)"] + [f"- ovi {u['ovi_range'][0]}-{u['ovi_range'][1]} [{u['kind']}]: {u['reason']}" for u in m["unfilmed_ranges"]]
        L += ["", "## Direction parts (code-derived)"] + [f"- {p['part_id']}: scenes {', '.join(p['scene_ids'])}, {p['shot_budget']} shots" for p in res["parts"]]
    return "\n".join(L) + "\n"


def main() -> int:
    import argparse
    import sys
    import time
    ap = argparse.ArgumentParser(description="Story-first planning: 'plan' = one Kimi call + checks, stops at the owner's gate; 'approve' = record the owner's approval of the split's exact hash.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--run-name", required=True)
    p.add_argument("--resume", action="store_true")
    p.add_argument("--redo", action="store_true", help="plan this chapter again although it was already planned (owner's decision only)")
    p.add_argument("--director", choices=["kimi", "nvidia"], default="kimi")
    p.add_argument("--model", default=None)
    p.add_argument("--allow-paid", action="store_true")
    p.add_argument("--reviewers", default=None, help="comma-separated NVIDIA models; default Nemotron Ultra; '' = none (UNREVIEWED)")
    p.add_argument("--max-tokens", type=int, default=12000)
    v = sub.add_parser("revise", help="owner-directed edit of a checked split (no Kimi call): validate + cross-check, write a new immutable run")
    v.add_argument("--base-run", required=True)
    v.add_argument("--edits", required=True, help="JSON file with the full replacement {stories, unfilmed_ranges, note}")
    v.add_argument("--run-name", required=True)
    v.add_argument("--reviewers", default=None)
    w = sub.add_parser("render", help="write the owner's story text from a template and a split run (numbers come from the data)")
    w.add_argument("--run-name", required=True)
    w.add_argument("--edits", required=True)
    w.add_argument("--template", required=True)
    w.add_argument("--out", required=True)
    q = sub.add_parser("approve")
    q.add_argument("--run-name", required=True)
    q.add_argument("--by", required=True, help="the owner's name; only the owner approves")
    q.add_argument("--override-review", action="store_true", help="approve although the cross-check is not a clean PASS (the owner has answered the missing checks himself)")
    a = ap.parse_args()
    dr = dt._load("director_run", ROOT / "scripts" / "source" / "director_run.py")
    manifest_path = ROOT / "canon" / "film_manifest.json"
    film = "gajanan-vijay-a1-a2"
    if a.cmd == "approve":
        run = dr.Run(dt.RUNS / a.run_name)
        res = run.read_json("macro_A1.json")
        if res["result"] != "VALID" and not a.override_review:
            raise SystemExit(f"the split is {res['result']}, not VALID; the owner may approve it only with --override-review")
        if not res["macro"] or sha_of(res["macro"]) != res["macro_sha256"]:
            raise SystemExit("the saved macro does not match its hash")
        packet_now = dt.verify_packet()
        if packet_now != run.receipt["inputs"]["packet_files"]:
            raise SystemExit("the packet (ovis or research) changed since this split was planned; plan again, then approve")

        def record(m):
            cur = m["items"].get("macro:A1")
            if cur and cur["sha256"] != res["macro_sha256"]:
                raise SystemExit(f"a newer split ({cur.get('run')}) is the manifest's current macro; approve that run, not {a.run_name}")
            dr.set_item(m, "macro:A1", res["macro_sha256"], run=a.run_name)
            dr.add_dep(m, "macro:A1", dr.set_packet_items(m, packet_now))
            dr.approve(m, "story_split", "A1", ["macro:A1"], a.by)
        dr.update_manifest(manifest_path, film, record)
        dr.ig.atomic_write_json(ROOT / "canon" / "story_split_A1.json", {"macro": res["macro"], "macro_sha256": res["macro_sha256"], "parts": res["parts"], "approved_by": a.by,
                                                                          "approved_at": time.strftime("%Y-%m-%d %H:%M:%S"), "from_run": a.run_name})
        print(f"approved story split A1 {res['macro_sha256'][:12]}... by {a.by}; saved canon/story_split_A1.json")
        return 0
    if a.cmd == "render":
        res = dr.Run(dt.RUNS / a.run_name).read_json("macro_A1.json")
        if not res["macro"]:
            raise SystemExit("this run holds no valid macro")
        text = render_doc(Path(a.template).read_text(encoding="utf-8"), res["macro"], res["macro_sha256"], json.loads(Path(a.edits).read_text(encoding="utf-8")), res["reviews"])
        if "{{" in text:
            raise SystemExit("unfilled placeholder left in the template")
        Path(a.out).write_text(text, encoding="utf-8")
        sm = split_summary(res["macro"])
        print(f"wrote {a.out}: {sm['stories']} story, {sm['scenes']} scenes, {sm['shots']} shots, {fmt_runtime(sm['seconds'])}")
        return 0
    keys = dt.nt.load_keys()
    if not keys:
        raise SystemExit("no usable NVIDIA key")
    pool = dt.nt.KeyPool(keys)
    if a.cmd == "revise":
        base = dr.Run(dt.RUNS / a.base_run).read_json("macro_A1.json")
        edits_path = Path(a.edits)
        edits = json.loads(edits_path.read_text(encoding="utf-8"))
        names = tuple(x for x in (dt.NVIDIA_MODEL if a.reviewers is None else a.reviewers).split(",") if x)
        reviewers = [dt.nvidia_agent(pool, keys, x) for x in names]
        packet_hashes = dt.verify_packet()
        files, ovis, _ = dt.load_inputs()
        here = ROOT / "scripts" / "source"
        inputs = {"mode": "revise_split", "base_run": a.base_run, "base_macro_sha256": base["macro_sha256"], "edits_sha256": dt._sha(edits_path), "packet_files": packet_hashes,
                  "reviewers": list(names), "code_sha256": {f: dt._sha(here / f) for f in ("story_split.py", "director_test.py", "director_run.py", "draft_source.py")}}
        run = dr.open_run(dt.RUNS, a.run_name, inputs)
        try:
            res = revise_split({"stories": edits["stories"], "unfilmed_ranges": edits["unfilmed_ranges"]}, [dt.recorded(r, run, 0) for r in reviewers], files, ovis, 1,
                               packet_hashes["adhyay_01_ovis_hj.jsonl"], base["macro_sha256"], edits.get("note", ""))
            run.write_once("macro_A1.json", json.dumps(res, indent=2, ensure_ascii=False))
            run.write_once("MACRO_REVIEW.md", macro_text(res))
            if res["macro"]:
                def propose(m):
                    dr.set_item(m, "macro:A1", res["macro_sha256"], run=a.run_name)
                    dr.add_dep(m, "macro:A1", dr.set_packet_items(m, packet_hashes))
                dr.update_manifest(manifest_path, film, propose)
            run.finish({"status": "REVISED SPLIT, waiting for the owner's approval of its hash", "result": res["result"], "macro_sha256": res["macro_sha256"], "revised_from": base["macro_sha256"]})
        finally:
            run.release()
        print(f"revised story split: {res['result']}; {len(res['errors'])} errors, {len(res['warnings'])} warnings; hash {res['macro_sha256']}")
        for e in res["errors"]:
            print("  ERROR", e)
        return 0 if res["result"] == "VALID" else 1
    if a.director == "kimi":
        if not a.allow_paid:
            raise SystemExit("--director kimi is a paid call: add --allow-paid")
        kimi = dt._load("kimi_adapter", ROOT / "scripts" / "source" / "kimi_adapter.py")
        try:
            director = kimi.make_agent(model=a.model or kimi.MODEL)
        except kimi.ledger_mod.Refused as exc:
            raise SystemExit(f"REFUSED: {exc}")
        settings, default_reviewers = {"model": director.name, "max_tokens": a.max_tokens, "phase": kimi.PHASE}, dt.NVIDIA_MODEL
    else:
        director = dt.nvidia_agent(pool, keys, a.model or dt.NVIDIA_MODEL)
        settings, default_reviewers = {"model": director.name, "max_tokens": a.max_tokens}, "openai/gpt-oss-20b,z-ai/glm-5.3-flash"
    names = tuple(x for x in (default_reviewers if a.reviewers is None else a.reviewers).split(",") if x)
    if director.name in names:
        raise SystemExit("a reviewer must be a different model from the director")
    reviewers = [dt.nvidia_agent(pool, keys, x) for x in names]
    packet_hashes = dt.verify_packet()
    files, ovis, _ = dt.load_inputs()
    here = ROOT / "scripts" / "source"
    inputs = {"mode": "plan_stories", "packet_files": packet_hashes, "director": director.name, "reviewers": list(names), "settings": settings,
              "code_sha256": {**{f: dt._sha(here / f) for f in ("story_split.py", "director_test.py", "director_run.py", "kimi_adapter.py", "draft_source.py")},
                              **{f: dt._sha(ROOT / "scripts" / "image_trials" / f) for f in ("v5_ledger.py", "nvidia_trial.py")}}}
    run = dr.open_run(dt.RUNS, a.run_name, inputs, resume=a.resume)
    try:
        if run.has("macro_A1.json"):
            held = run.read_json("macro_A1.json")["result"]
            print("this run already holds the split:", held)
            return 0 if held == "VALID" else 1
        try:
            dr.claim_scene(dt.RUNS, "macro__" + director.name, 0, a.run_name, a.redo)         # one planning pass per chapter per director, atomic, before any paid dispatch
            res = plan_stories(dt.recorded(director, run, 0), [dt.recorded(r, run, 0) for r in reviewers], files, ovis, 1, packet_hashes["adhyay_01_ovis_hj.jsonl"], a.max_tokens)
        except Exception as exc:
            run.finish({"status": f"STOPPED ({type(exc).__name__}: {str(exc)[:200]})"})
            print("STOPPED:", type(exc).__name__, str(exc)[:200], "| every paid reply is saved; --resume continues without re-buying")
            return 2
        run.write_once("macro_A1.json", json.dumps(res, indent=2, ensure_ascii=False))
        run.write_once("MACRO_REVIEW.md", macro_text(res))
        if res["macro"] and res["macro_sha256"]:
            def propose(m):
                dr.set_item(m, "macro:A1", res["macro_sha256"], run=a.run_name)
                dr.add_dep(m, "macro:A1", dr.set_packet_items(m, packet_hashes))
            dr.update_manifest(manifest_path, film, propose)
        run.finish({"status": "STOPPED AT THE OWNER'S GATE: approve the split's hash before any direction", "result": res["result"], "macro_sha256": res["macro_sha256"]})
    finally:
        run.release()
    print(f"story split: {res['result']}; {len(res['errors'])} errors, {len(res['warnings'])} warnings; hash {res['macro_sha256']}")
    if res["macro"]:
        for st in res["macro"]["stories"]:
            print(f"  {st['story_id']} {st['title']} (ovi {st['ovi_range'][0]}-{st['ovi_range'][1]}, {st['arc']}): scenes " + ", ".join(sc["scene_id"] for sc in st["scenes"]))
    print("STOP: waiting for the owner's approval of this split (story_split.py approve).")
    return 0 if res["result"] == "VALID" else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
