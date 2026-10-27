"""Director (D-018 A1-A3): a director model turns the owner's FROZEN research into executable shot plans, and code validates, cross-checks and repairs them.
Flow per scene (each scene is directed ONCE per Adhyay; at most ONE repair round in total, no loops): director -> code validator -> independent reviewers (binary questions
with evidence) -> if the validator or the reviewers block, ONE shot-locked repair round -> validator -> reviewers check the result (a check only, no further repair). A missing or unanswered check never passes. NEED_NEW shots are UNRESOLVED, never success. Nothing is rendered; nothing here is approved.
Output only to canon/director_runs/<name>/ (immutable files, receipt.json); see director_run.py.

  python scripts/source/director_test.py --run-name r3 --scenes 1,4,6 --director nvidia [--model ...] [--reviewers a,b]
  python scripts/source/director_test.py --run-name r4 --scenes 1,4,6 --director kimi --allow-paid     (paid: money guard in kimi_adapter.py)
Keys: read at run time by the provider modules, never printed."""
from __future__ import annotations

import argparse
import atexit
import copy
import hashlib
import importlib.util
import json
import math
import re
import sys
import time
import unicodedata
from collections import Counter, namedtuple
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "canon" / "packets" / "adhyay_01"
RUNS = ROOT / "canon" / "director_runs"
PRESET_DIR = ROOT / "assets" / "v5_presets"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ds = _load("ds", ROOT / "scripts" / "source" / "draft_source.py")
nt = ds.nt

NVIDIA_MODEL = "nvidia/nemotron-3-ultra-550b-a55b"
ONE_CALL = False                                   # set by --one-call: exactly one director call, no re-ask, no repair (the owner decides what happens to a flawed plan)
SHOT_SECONDS = 6                                   # one Builder v2 render = 144 frames at 24 fps
TRANSITIONS = ["cut", "slide", "pan_bridge"]
CLOSEUPS = {"07_character_reaction", "08_emotional_closeup", "10_object_hand_insert"}
NEEDS = ["none", "limb_motion", "walking", "lip_sync", "face_change"]            # what the shot would need beyond a held pose + camera
CLAIM_KINDS = ["person", "prop", "scenery", "light", "pose", "camera", "event"]
STAGING_OK = {"scenery", "light", "pose", "camera"}                              # a STAGING label may never add a person, object or event
# Motion in the ACTION (what happens during the 6 s). The held_pose field may show a raised hand or a smile; the action may not raise it or start one.
MOTION_CORE = (r"lip[- ]?sync|(lips?|mouth)\s+(mov\w*|open\w*|speak\w*|quiver\w*)|(moves?|moving) (his|her|their|the) (lips|mouth|hand|arm|head)"
               r"|(raises?|raising|lifts?|lifting|lowers?|lowering|extends?|extending|reaches?|reaching|points?|pointing)\b"
               r"|(hand|arm|finger)s? (is |are |gets? |being )?(raised|lifted|rising|lowering|moving)|waves?|waving|walks?|walking|runs?|running|claps?|clapping|jumps?|jumping|dances?|dancing|throws?|picks? up|steps? (forward|back)"
               r"|stands? up|rises?|sits? down|turns? (his|her|their) head")
MOTION_WORDS = re.compile(rf"\b({MOTION_CORE}|nods?|nodding|smiles?|smiling|blinks?|blinking)\b", re.I)      # for the action
PERFORMANCE_MOTION = re.compile(rf"\b({MOTION_CORE})\b", re.I)                                                # for the performance text ("smiling held pose" is a static look)
DATE_WORDS = re.compile(r"\b(magh|maagh|saptami|vadya|january|february|april|june|july|august|september|october|november|december)\b|\b(march|may)\b(?=\s+(of\s+)?\d)|\b(in|on|during|since|until|from|by) (march|may)\b|\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b|\b\d{1,2}(st|nd|rd|th)? (of )?(january|february|march|april|may|june|july|august|september|october|november|december)\b", re.I)
INVENTABLE = frozenset("sky cloud clouds sun moon star stars tree trees branch branches leaf leaves river hill hills mountain mountains rain mist fog flower flowers bird birds throat".split())
MATERIALS = frozenset("brass clay copper wooden wood silver gold iron stone steel bronze".split())
# ponytail: INVENTABLE/MATERIALS are small word lists (a heuristic backstop for invented scenery and prop drift); the reviewers' binary questions cover the rest.

# ----------------------------------------------------------------------------- contract v2

ID = {"type": "string", "minLength": 1, "maxLength": 300, "pattern": r"\S"}     # every text field: at most 300 characters (the prompt says so)
REF = {"type": "string", "pattern": r"^A[1-9][0-9]?:[0-9]{1,4}$"}            # chapter-qualified ovi, e.g. A1:84
IMG = {"type": "string", "pattern": r"^[a-z][a-z0-9_]{0,39}$"}
SOURCE = {"type": "string", "pattern": r"^(STAGING|PACKET|A[1-9][0-9]?:[0-9]{1,4})$"}
SHOT = {"type": "object", "additionalProperties": False,
        "required": ["shot_id", "ovi_ids", "preset", "assets", "action", "held_pose", "needs", "performance", "camera", "dialogue", "claims", "staging", "transition_out"],
        "properties": {
            "shot_id": {"type": "string", "pattern": r"^S[0-9]-([1-9]|1[0-6])$"},
            "ovi_ids": {"type": "array", "minItems": 1, "items": REF},
            "preset": {"type": "string"},
            "need_new_reason": {"type": "string", "maxLength": 300},
            "assets": {"type": "object", "additionalProperties": IMG},                    # role -> image_id declared in images_needed
            "action": ID, "held_pose": ID, "performance": ID, "camera": ID,
            "needs": {"type": "array", "minItems": 1, "items": {"enum": NEEDS}},
            "dialogue": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["speaker", "ovi", "marathi", "meaning_en"],
                                                      "properties": {"speaker": ID, "ovi": REF, "marathi": {"type": "string", "minLength": 1, "maxLength": 600}, "meaning_en": ID}}},
            "claims": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["kind", "term", "source"],
                                                  "properties": {"kind": {"enum": CLAIM_KINDS}, "term": ID, "source": SOURCE}}},
            "staging": {"type": "array", "items": {"type": "string", "minLength": 1, "maxLength": 300}},
            "transition_out": {"enum": TRANSITIONS}}}
SCENE = {"type": "object", "additionalProperties": False, "required": ["scene_id", "chapter", "ovi_range", "goal", "turn", "shots", "images_needed"],
         "properties": {
             "scene_id": {"type": "string", "pattern": r"^S[0-9]$"},
             "chapter": {"type": "integer", "minimum": 1},
             "ovi_range": {"type": "array", "minItems": 2, "maxItems": 2, "items": {"type": "integer"}},
             "goal": ID,
             "turn": {"type": "object", "additionalProperties": False, "required": ["ovi", "text"], "properties": {"ovi": REF, "text": ID}},
             "shots": {"type": "array", "minItems": 2, "maxItems": 16, "items": SHOT},
             "images_needed": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["image_id", "description"],
                                                           "properties": {"image_id": IMG, "description": {"type": "string", "minLength": 1, "maxLength": 300}}}}}}


def norm(s: str) -> str:
    return " ".join(str(s).replace("‍", "").replace("‌", "").split())


def qnorm(s: str) -> str:
    """For quote matching only: keep letters and combining marks (matras, virama), drop spaces, danda, punctuation and zero-width joiners. The letters must still match exactly."""
    out = []
    for c in str(s):
        cat = unicodedata.category(c)
        if cat[0] in ("L", "M", "N"):
            out.append(c)
        elif cat != "Cf":                                  # zero-width joiners vanish; spaces, danda and punctuation become ONE word boundary
            out.append(" ")
    return " ".join("".join(out).split())


def quote_in(quote: str, source: str) -> bool:
    """True if the quote's words appear in the source as whole consecutive words (letters must match exactly)."""
    q, s = qnorm(quote), qnorm(source)
    return bool(q) and f" {q} " in f" {s} "


def parse_ref(r) -> tuple | None:
    m = re.fullmatch(r"A([1-9][0-9]?):([0-9]{1,4})", r) if isinstance(r, str) else None
    return (int(m[1]), int(m[2])) if m else None


def words(*texts) -> set:
    return set(re.findall(r"[a-z]+", " ".join(texts).lower()))


def frame_ends(preset_json: dict) -> dict:
    """First and last frame of a preset, derived from its own transform (never from the model): layer roles visible and camera zoom."""
    segs = preset_json["segments"]
    return {"first_roles": sorted(l["asset"] for l in segs[0]["layers"]), "last_roles": sorted(l["asset"] for l in segs[-1]["layers"]),
            "zoom": [segs[0]["camera"]["start"]["zoom"], segs[-1]["camera"]["end"]["zoom"]]}


NEG_WORDS = re.compile(r"\b(no|not|without|never|nor|neither|avoid|avoids|instead of)\b", re.I)
BREAKERS = frozenset("but however yet although while he she they it then who which maharaj".split())      # a contrast word or a new subject ends a negation's reach


def negated(text: str, start: int, matched: str = "") -> bool:
    """True if the word at `start` is inside the reach of a negation: 'no hand, head or lip movement' negates 'lip movement';
    'No lip movement, but he raises his hand' and 'Without walking he raises his hand' do not negate 'raises'."""
    prefix = text[max(0, start - 80):start]
    last = None
    for m in NEG_WORDS.finditer(prefix):
        last = m
    if last is None:
        return False
    tail = prefix[last.end():]
    if re.search(r"[.;:!?]", tail):
        return False
    words = re.findall(r"[a-z']+", tail.lower())
    if re.search(r"\b[A-Z][a-z]+", tail.strip()[1:]) or (words[-1:] == ["and"] and matched.lower().endswith("s") and " " not in matched.strip()):
        return False                                                               # a capitalised name starts a new clause; 'and raises' starts a new predicate
    return len(words) <= 6 and not (set(words) & BREAKERS)


PRESET_MOTION = {"04_character_entrance": re.compile(r"^(walk\w*|enter\w*)$", re.I)}      # the walking-entrance preset exists to show a walking pose with a camera pan


def motion_hit(sh: dict, preset: str):
    """The first asserted (not negated) motion word in the action or performance that this preset cannot show."""
    for rx, text in ((MOTION_WORDS, sh["action"]), (PERFORMANCE_MOTION, sh["performance"])):
        for m in rx.finditer(text):
            if negated(text, m.start(), m.group(0)):
                continue
            if preset in PRESET_MOTION and PRESET_MOTION[preset].match(m.group(0)):
                continue
            return m
    return None


def asserted(rx, text: str):
    """First match of rx that is not negated ('no lip movement occurs' states what does NOT happen, so it is not motion)."""
    for m in rx.finditer(text):
        if not negated(text, m.start(), m.group(0)):
            return m
    return None


def normalise(scene):
    """Documented default: a preset shot that omits 'needs' means ['none'] (the motion check and reviewers still judge the shot). Returns (scene copy, notes)."""
    if not isinstance(scene, dict) or not isinstance(scene.get("shots"), list):
        return scene, []
    out, notes = copy.deepcopy(scene), []
    for sh in out["shots"]:
        if isinstance(sh, dict) and "needs" not in sh and sh.get("preset") != "NEED_NEW":
            sh["needs"] = ["none"]
            notes.append(f"{sh.get('shot_id')}: 'needs' was missing and defaulted to ['none']")
    return out, notes


def speaker_table(addendum_lines: list) -> dict:
    """ovi -> the speaker cell of the owner's dialogue table (e.g. 'Bankatlal → Damodarpant', 'unclear: ...'), ranges expanded."""
    rows = {}
    for l in addendum_lines:
        c = [x.strip() for x in l.split("|")]
        m = re.fullmatch(r"(\d+)(?:-(\d+))?", c[1]) if len(c) > 3 and l.startswith("|") else None
        if m:
            cell = c[2].split("→")[0].strip()
            if cell.lower().startswith("same") and rows:                              # 'same (joint reasoning, ...)' continues the previous row's speakers
                cell = rows[max(rows)]
            for n in range(int(m[1]), int(m[2] or m[1]) + 1):
                rows[n] = cell
    return rows


def validate_scene(scene, presets: dict, ovi_text: dict, scene_range: tuple, ctx: dict, chapter: int = 1, scene_id: str | None = None) -> tuple[list, list]:
    """(errors, warnings). presets: name -> role names; ovi_text: ovi -> Marathi text of the SCENE's range (and only that).
    ctx (all keys required): packet_text (the owner's research the director saw), speakers (registered names), preset_json (name -> preset transform, may be {}),
    prop_materials (term -> material the research fixes, may be {}), speaker_rows (ovi -> speaker cell of the owner's dialogue table, may be {})."""
    errors = [f"{'/'.join(map(str, e.path)) or 'scene'}: {e.message}" for e in jsonschema.Draft202012Validator(SCENE).iter_errors(scene)]
    if errors:
        return errors, []
    warnings, lo, hi = [], scene_range[0], scene_range[1]
    packet_words = words(ctx["packet_text"])
    speakers = {s.lower() for s in ctx["speakers"]} | {"unclear"}

    def in_scene(ref) -> bool:
        p = parse_ref(ref)
        return bool(p) and p[0] == chapter and lo <= p[1] <= hi

    if scene["chapter"] != chapter:
        errors.append(f"chapter must be {chapter}")
    if scene_id and scene["scene_id"] != scene_id:
        errors.append(f"scene_id must be {scene_id}")
    if scene["ovi_range"] != [lo, hi]:
        errors.append(f"ovi_range must be exactly {[lo, hi]}")
    if not in_scene(scene["turn"]["ovi"]):
        errors.append(f"turn.ovi {scene['turn']['ovi']} outside the scene range (chapter {chapter}, ovi {lo}-{hi})")
    images = {}
    for im in scene["images_needed"]:
        if ctx.get("scene_image_prefix") and not im["image_id"].startswith(f"s{scene['scene_id'][1:]}_"):
            errors.append(f"image {im['image_id']} must start with 's{scene['scene_id'][1:]}_' (one scene, one id space: no id is shared between scenes)")
        if im["image_id"] in images:
            errors.append(f"image {im['image_id']} is declared twice")
        images[im["image_id"]] = im["description"]
    used, seen, prev, run, prop_seen = set(), set(), None, 0, {}
    for i, sh in enumerate(scene["shots"]):
        sid = sh["shot_id"]
        if sid in seen or sid != f"{scene['scene_id']}-{i + 1}":
            errors.append(f"{sid}: shot ids must be {scene['scene_id']}-1, -2, ... in order and unique")
        seen.add(sid)
        for r in sh["ovi_ids"]:
            if not in_scene(r):
                errors.append(f"{sid}: {r} is outside the scene (chapter {chapter}, ovi {lo}-{hi})")
        shot_ovis = {parse_ref(r)[1] for r in sh["ovi_ids"] if in_scene(r)}
        preset = sh["preset"]
        if preset == "NEED_NEW":
            if not sh.get("need_new_reason", "").strip():
                errors.append(f"{sid}: NEED_NEW needs need_new_reason")
        elif preset not in presets:
            errors.append(f"{sid}: unknown preset {preset!r} (use one of {sorted(presets)} or NEED_NEW)")
        else:
            if set(sh["assets"]) != set(presets[preset]):
                errors.append(f"{sid}: assets must have exactly the roles {sorted(presets[preset])} for {preset}, got {sorted(sh['assets'])}")
            if sh["needs"] != ["none"]:
                errors.append(f"{sid}: needs {sh['needs']} but preset {preset} gives only a held pose and a camera move; use NEED_NEW")
            m = motion_hit(sh, preset)
            if m:
                errors.append(f"{sid}: action/performance describes motion the renderer cannot do ({m.group(0)!r}); show it as a held pose (held_pose) or use NEED_NEW")
            pj = ctx["preset_json"].get(preset)
            if pj:
                z0, z1 = frame_ends(pj)["zoom"]
                cam = sh["camera"].lower()
                if ("push" in cam or "zoom in" in cam) and z1 < z0 or ("pull" in cam or "zoom out" in cam) and z1 > z0:
                    warnings.append(f"{sid}: camera text {sh['camera']!r} contradicts the preset's zoom {z0} -> {z1}")
                stated = [float(x) for x in re.findall(r"\b\d\.\d+\b", sh["camera"])]
                if [x for x in stated if min(abs(x - z0), abs(x - z1)) > 0.006] or (len(stated) >= 2 and (abs(stated[0] - z0) > 0.006 or abs(stated[-1] - z1) > 0.006)):
                    warnings.append(f"{sid}: camera text states zoom values {stated} but the preset fixes {z0} -> {z1}")
        for role, img in sh["assets"].items():
            used.add(img)
            if img not in images:
                errors.append(f"{sid}: asset {role} uses image {img!r} which images_needed does not declare")
        run = run + 1 if preset == prev else 1
        prev = preset
        if run > 2 and preset != "NEED_NEW":
            warnings.append(f"{sid}: preset {preset} used {run} times in a row")
        if preset in CLOSEUPS and i > 1 and scene["shots"][i - 1]["preset"] in CLOSEUPS and scene["shots"][i - 2]["preset"] in CLOSEUPS:
            warnings.append(f"{sid}: three close-up presets in a row")
        for d in sh["dialogue"]:                                                       # exact Marathi only; paraphrase belongs to the narrator (A3)
            p = parse_ref(d["ovi"])
            if not in_scene(d["ovi"]):
                errors.append(f"{sid}: dialogue {d['ovi']} is not an ovi of this scene (chapter {chapter}, ovi {lo}-{hi})")
            elif p[1] not in shot_ovis:
                errors.append(f"{sid}: dialogue {d['ovi']} is not in this shot's own ovi_ids {sh['ovi_ids']}")
            elif p[1] not in ovi_text:
                errors.append(f"{sid}: no source text for {d['ovi']}")
            elif len(qnorm(d["marathi"]).replace(" ", "")) < 3:
                errors.append(f"{sid}: dialogue {d['ovi']} has an empty or too short Marathi quote")
            elif ctx.get("dialogue_plan") is None and not quote_in(d["marathi"], ovi_text[p[1]]):          # with a plan, the owner's approved spoken line is the authority (checked below)
                errors.append(f"{sid}: dialogue Marathi for {d['ovi']} is not a substring of that ovi's text")
            if d["speaker"].lower() not in speakers:
                errors.append(f"{sid}: speaker {d['speaker']!r} is not a registered character (use a registered name or 'unclear')")
            elif p and p[1] in ctx["speaker_rows"]:                                    # the owner's table fixes (or leaves unclear) who speaks each ovi
                row, who = ctx["speaker_rows"][p[1]].lower(), d["speaker"].lower()
                tokens = [w for w in re.findall(r"[a-z]+", who) if w not in ("shri", "maharaj", "the")] or [who]
                if row.startswith("unclear"):
                    if who != "unclear":
                        errors.append(f"{sid}: the owner's table marks the speaker of {d['ovi']} as unclear; use 'unclear', not {d['speaker']!r}")
                elif who == "unclear":
                    if " and " not in row:                                           # joint speech (two named speakers, not split) may stay 'unclear'
                        errors.append(f"{sid}: the owner's table gives {ctx['speaker_rows'][p[1]]!r} as the speaker of {d['ovi']}, not {d['speaker']!r}")
                elif not any(t.startswith(w) or w.startswith(t) for w in re.findall(r"[a-z]{4,}", row) for t in tokens):
                    errors.append(f"{sid}: the owner's table gives {ctx['speaker_rows'][p[1]]!r} as the speaker of {d['ovi']}, not {d['speaker']!r}")
        claimed = set()
        for c in sh["claims"]:
            t, src, kind = c["term"], c["source"], c["kind"]
            if not (kind == "camera" and src == "STAGING"):                           # a camera claim never licenses scenery words
                claimed |= words(t)
            if src == "STAGING":
                if kind not in STAGING_OK:
                    errors.append(f"{sid}: a STAGING label may not add a {kind} ({t!r}); it needs an ovi or the owner's research")
                elif not (kind == "camera" and preset in presets and not (words(t) & INVENTABLE)):         # the preset fixes the camera move: nothing to approve
                    warnings.append(f"{sid}: STAGING {kind} {t!r} needs the owner's approval")
            elif src == "PACKET":
                if kind == "event":
                    errors.append(f"{sid}: an event ({t!r}) must cite an ovi of this shot, not the general research")
                elif [w for w in re.findall(r"[a-z]+", t.lower()) if len(w) > 2 and w not in packet_words]:
                    errors.append(f"{sid}: {kind} {t!r} is not in the owner's research (cite an ovi, or label it STAGING if it is only scenery/light/pose/camera)")
            else:
                p = parse_ref(src)
                if not in_scene(src):
                    errors.append(f"{sid}: claim {t!r} cites {src}, outside the scene")
                elif kind == "event" and p[1] not in shot_ovis:
                    errors.append(f"{sid}: event {t!r} cites {src}, which this shot does not show")
            if kind == "prop":
                prop_seen.setdefault(t.lower(), set())
        for s in sh["staging"]:
            if not s.startswith("STAGING:"):
                errors.append(f"{sid}: staging line must start with 'STAGING:': {s[:40]!r}")
        if not sh["staging"]:
            warnings.append(f"{sid}: no staging line (every camera/light/pose choice should be labelled STAGING)")
        blob = [sh["action"], sh["performance"], sh["held_pose"], sh["camera"]] + [images.get(img, "") for img in sh["assets"].values()]
        shown_words = set()
        for part in blob:                                                              # a word only counts where the text asserts it ('without clouds' does not show clouds)
            for m in re.finditer(r"[a-z]+", part.lower()):
                if m.group(0) in INVENTABLE and not negated(part.lower(), m.start()):
                    shown_words.add(m.group(0))
        for w in sorted(shown_words - packet_words - claimed):
            errors.append(f"{sid}: {w!r} appears in the shot but not in the owner's research or in any claim (declare it as a claim with an ovi, or STAGING for scenery/light)")
        for term in prop_seen:                                                          # prop material must stay the same across the scene
            for frag in re.split(r"[.;,]", " . ".join(blob).lower()):
                if term in frag:
                    prop_seen[term] |= words(frag) & MATERIALS
    for term, mats in prop_seen.items():
        want = ctx["prop_materials"].get(term)
        if len(mats) > 1 or (want and mats - {want}):
            errors.append(f"prop {term!r} is described with different materials ({sorted(mats)}){' but the research says ' + want if want else ''}")
    for img in sorted(set(images) - used):
        errors.append(f"image {img} is declared in images_needed but no shot uses it")
    texts = [("goal", scene["goal"]), ("turn", scene["turn"]["text"])] + [(im["image_id"], im["description"]) for im in scene["images_needed"]]
    for sh in scene["shots"]:
        texts += [(sh["shot_id"], t) for t in [sh["action"], sh["held_pose"], sh["performance"], sh["camera"], sh.get("need_new_reason", "")] + list(sh["staging"]) + [c["term"] for c in sh["claims"]] + [d["meaning_en"] for d in sh["dialogue"]]]
    for where, t in texts:                                                           # the owner's rule: the year only, never a day or a month
        m = DATE_WORDS.search(t)
        if m:
            errors.append(f"{where}: a day or month ({m.group(0)!r}) appears; only the year may be shown, and only as an on-screen caption")
    target = ctx.get("shots_target")
    if target and len(scene["shots"]) != target:
        errors.append(f"the scene must have exactly {target} shots (the narration timing needs that many 6-second shots), not {len(scene['shots'])}")
    for k, sh in enumerate(scene["shots"], 1):                                     # the picture follows the audio: a shot lists the ovis whose narration starts in it
        need = {f"A{chapter}:{o}" for o in (ctx.get("timeline") or {}).get(k, [])} - set(sh["ovi_ids"])
        if need:
            errors.append(f"{sh['shot_id']}: the narration timeline starts {sorted(need)} in this shot, so its ovi_ids must list them")
    if ctx.get("dialogue_plan") is not None:                                          # dialogue = exactly the planned character lines, in the shot where each starts
        for k, sh in enumerate(scene["shots"], 1):
            want, used = ctx["dialogue_plan"].get(k, []), set()
            for d in sh["dialogue"]:
                p = parse_ref(d["ovi"])
                hit = next((w for w in want if w["id"] not in used and p and w["ovi"] == p[1] and qnorm(d["marathi"]) == qnorm(w["marathi"]) and w["voice"] in d["speaker"].lower()), None)
                if hit is None:
                    errors.append(f"{sh['shot_id']}: dialogue {d['ovi']} by {d['speaker']!r} is not one of the character lines planned for this shot (exact Marathi, that character)")
                else:
                    used.add(hit["id"])
            errors += [f"{sh['shot_id']}: the planned character line {w['id']} (ovi {w['ovi']}, {w['voice']}) is missing from this shot's dialogue" for w in want if w["id"] not in used]
    if not any(scene["turn"]["ovi"] in sh["ovi_ids"] for sh in scene["shots"]):
        warnings.append("the turn ovi is not shown in any shot")
    shown = {parse_ref(r)[1] for sh in scene["shots"] for r in sh["ovi_ids"] if in_scene(r)}
    if set(range(lo, hi + 1)) - shown:
        warnings.append(f"ovis not shown in any shot (the owner approves omissions): {sorted(set(range(lo, hi + 1)) - shown)}")
    if not scene["images_needed"]:
        errors.append("images_needed is empty")
    return errors, warnings


def scene_status(scene, errors: list) -> str:
    """INVALID (any validator error) | UNRESOLVED (some shot is NEED_NEW: never success) | VALID."""
    if errors or not isinstance(scene, dict):
        return "INVALID"
    return "UNRESOLVED" if any(sh["preset"] == "NEED_NEW" for sh in scene["shots"]) else "VALID"


def finalize(scene: dict) -> dict:
    """Adds the code-derived used_in lists (the model never writes them)."""
    out = copy.deepcopy(scene)
    for im in out["images_needed"]:
        im["used_in"] = [sh["shot_id"] for sh in out["shots"] if im["image_id"] in sh["assets"].values()]
    return out


# ----------------------------------------------------------------------------- inputs

def section(lines: list, start: str, stop: str) -> str:
    """Lines from the first line matching `start` up to (not including) the next line matching `stop`."""
    a = next((i for i, l in enumerate(lines) if re.match(start, l)), None)
    if a is None:
        raise SystemExit(f"section not found: {start}")
    b = next((i for i in range(a + 1, len(lines)) if re.match(stop, lines[i])), len(lines))
    return "\n".join(lines[a:b]).strip()


def dialogue_rows(lines: list, lo: int, hi: int) -> str:
    rows = []
    for l in lines:
        m = re.match(r"^\|\s*(\d+)(?:-(\d+))?\s*\|", l)
        if m:
            a, b = int(m.group(1)), int(m.group(2) or m.group(1))
            if a <= hi and b >= lo:
                rows.append(l)
    return "\n".join(rows)


def scene_ranges(addendum: list) -> dict:
    out = {}
    for l in addendum:
        m = re.match(r"^### Scene (\d+) - .*\(ovi (\d+)-(\d+)\)", l)
        if m:
            out[int(m.group(1))] = (int(m.group(2)), int(m.group(3)))
    return out


def speaker_registry(analysis_lines: list) -> set:
    """Registered names = the bold character headings of section 3 (full heading and the part before ' (')."""
    names = set()
    for l in section(analysis_lines, r"^## 3\. Characters", r"^## 4\.").splitlines():
        m = re.match(r"^\*\*(.+?)\*\*\s*$", l)
        if m:
            names |= {m.group(1).strip(), m.group(1).split(" (")[0].strip()}
    return names


RULES = """FIDELITY (facts)
F1. Facts come only from the MATERIALS below (the owner's frozen research and the Marathi ovis). Every shot lists the ovi numbers it shows as chapter-qualified refs written exactly A<chapter>:<ovi> (e.g. "A1:84"; chapter 1-99, ovi up to four digits), all inside this scene's range. Every spoken line cites its ovi, and that ovi must be one of the shot's own ovi_ids.
F2. Spoken lines: copy the Marathi words EXACTLY from the cited ovi, at least three letters long (spacing, danda and punctuation may differ; every letter and matra must match). Characters speak only exact Marathi words; paraphrase never goes in "dialogue". When the message gives a NARRATION PLAN, a character's spoken Marathi is copied EXACTLY from that plan line (the owner's approved easy wording, which renders the cited ovi's meaning), not from the verse. The speaker must be a REGISTERED SPEAKER, spelled as listed, and must agree with the owner's dialogue table: where the table marks the speaker unclear, write "unclear".
F3. Thoughts, and words the ovis do not clearly give as spoken aloud, are NOT dialogue: do not put them in a character's mouth. Leave them to the narrator and show the moment as a held pose. Motives, feelings and thoughts appear only where an ovi states them; show feeling only through a held pose or a camera choice, and label it STAGING.
F4. Miracles and teaching are shown plainly with the cause the ovi gives; no invented cause (no glow, light rays or slow motion that suggests one).
F5. Every person, object, scenery item, light, pose or event you show is listed in the shot's "claims" with its source: an ovi ref of this scene ("A1:90"); "PACKET" (a person, prop, scenery, light, pose or camera item that the owner's research names; use the research's own words for the term); or "STAGING". STAGING is only for scenery, light, pose or camera proposals (the owner approves each one); it can never add a person, an object, an event, a motive or a cause. An event must cite an ovi of its own shot. Staging lines start with "STAGING:". Do not add people, objects or places the materials do not name: no sky, trees, branches, birds, hands at the throat and the like unless the materials give them or the claim is a STAGING scenery/light proposal.
F6. Every text field is at most 300 characters (a Marathi quote at most 600). No field may be empty.
F7. Keep each prop's material the same in every shot, in the materials' own words (the reviewers also check its look).
F8. Never write a day or a month (no Magh, Saptami, Vadya, no month names) in ANY field, including "turn" and "goal". A year, if the owner's notes ask for one, is an on-screen caption handled outside your plan.
F9. Show a state the verse gives as a state: "ready to fall at his feet" (143) is a readiness, not a completed prostration; do not complete an action the ovi only prepares.
STORYTELLING (the telling only)
T1. The scene must change something (situation, a person's state, or what the viewer understands): that is its "turn".
T2. Vary the kind of shot (the code warns the owner when one preset appears three times in a row or three close-up presets 07, 08, 10 follow each other). Every shot is exactly 6 seconds.
T3. Each shot has exactly one visible action written as a verb phrase of what the VIEWER sees during the 6 s (a camera move or a breathing figure). Anything that would change inside the shot (a hand rising, lips moving, a step, a smile starting) is NOT allowed as an action; show the result as a held pose (in "held_pose" and "performance") instead.
T4. Plain, concrete wording. No metaphor of your own. No sermon the ovis do not state.
T5. Economy: one concise held-pose sentence and one short performance sentence per shot; combine claims only when they share kind and source (keep every distinct factual assertion); do not repeat a restriction across fields.
T6. Coverage: every ovi of the scene's range appears in some shot's ovi_ids. An ovi that only the narrator will tell (introduction, teaching, authority) is attached to the nearest shot, and the shot's performance says briefly that the narrator carries it.
T7. The film must look FULL (owner's rule): choose the presets and catalog images so every shot is a completely drawn scene with background, midground and foreground filled in; prefer layered presets and varied framings; never a figure alone on an empty or plain background unless the catalog says that image is a deliberate close-up.
T8. There is NO limit on the number of images (the owner supplies as many as the film needs): reuse a catalog image for consistency of look when it fits the beat, but never bend a shot to save an image; when a shot needs a better pose, framing or setting, declare it as a new image."""

CHARACTER_VOICES = {"bankatlal", "damodarpant", "gajanan"}
CAPS = """RENDERER CAPABILITIES (facts about what can be produced; do not ask for more)
- One shot = exactly ONE render of 144 frames = 6 seconds at 24 fps. A scene is 2-16 shots (12-96 s); the narration timing says how many.
- Pictures are owner-made flat-colour illustrations used as HELD POSES and layers. There is NO limb animation, NO walking cycle, NO lip-sync, NO facial-expression change inside a shot; only gentle breathing/sway, camera push/pan/parallax, and cuts between poses.
- Every image_id starts with the scene prefix, "s<n>_" (e.g. s4_maharaj_seated); ids are never shared between scenes.
- A different pose or expression needs a different image: declare it in "images_needed" and use it in another shot.
- Each shot picks ONE of the presets listed (name exactly). Select presets using their supplied transforms, layer formats and fixed effects: the parameters are fixed, so do not invent zoom values and do not assume that prose can switch an effect off. If no preset matches the treatment the scene needs, use NEED_NEW. "assets" must contain EXACTLY the roles of that preset, each mapped to an image_id declared in "images_needed". An image_id is lowercase letters, digits and underscores, starting with a letter, at most 40 characters (e.g. "maharaj_seated_wide"); its description says who/where, pose and framing. Declare each image once and use every declared image in some shot. If no preset can show what the scene needs, use "preset": "NEED_NEW" with "need_new_reason" and "needs" naming what is missing (do not pretend a preset can do it); the code reports such a scene as UNRESOLVED.
- Transitions between shots: cut | slide | pan_bridge only (no dissolves)."""

SCHEMA_TEXT = """OUTPUT: Return ONE JSON object only (no text before or after, no code fence). Required scene keys: scene_id, chapter, ovi_range, goal, turn, shots, images_needed. EVERY shot MUST contain all 13 keys: shot_id, ovi_ids, preset, assets, action, held_pose, needs, performance, camera, dialogue, claims, staging, transition_out. For every preset shot write "needs": ["none"] explicitly; never omit it. For NEED_NEW, list the unmet capabilities in "needs" and also give need_new_reason. Use "dialogue": [] when nobody speaks. Empty arrays are allowed where appropriate; required keys and text values must never be missing. The shape:
{"scene_id": "S<n>", "chapter": <n>, "ovi_range": [first, last], "goal": "...", "turn": {"ovi": "A<chapter>:<n>", "text": "what changes, as the ovi states it"},
 "shots": [{"shot_id": "S<n>-1", "ovi_ids": ["A1:84"], "preset": "<preset name or NEED_NEW>", "need_new_reason": "only if NEED_NEW", "assets": {"<role>": "<image_id>"},
            "action": "what the viewer sees during the 6 s (verb phrase)", "held_pose": "the pose the picture holds", "needs": ["none"],
            "performance": "what the held pose shows", "camera": "plain words: push in / pan right / hold ...",
            "dialogue": [{"speaker": "<registered name or unclear>", "ovi": "A1:84", "marathi": "exact words from that ovi", "meaning_en": "..."}],
            "claims": [{"kind": "person|prop|scenery|light|pose|camera|event", "term": "...", "source": "A1:84|PACKET|STAGING"}],
            "staging": ["STAGING: ..."], "transition_out": "cut|slide|pan_bridge"}],
 "images_needed": [{"image_id": "short_id", "description": "what the owner must make in Flow"}]}
Constraints: scene_id is "S" plus one digit and equals the scene you were asked for; shot_ids are S<n>-1, S<n>-2 ... consecutive, in order, 2 to 16 shots; "needs" is ["none"] unless the shot would need one of limb_motion, walking, lip_sync, face_change (then the preset is NEED_NEW); images_needed is not empty and has no duplicate image_id; no field is empty."""


def preset_facts(pj: dict) -> str:
    """What a preset really does (from its own JSON): the zoom and the effects that cannot be switched off."""
    z0, z1 = frame_ends(pj)["zoom"]
    atm = {k: v for k, v in (pj.get("atmosphere") or {}).items() if k in ("gloss", "dust", "vignette") and v}
    fx = [f"{k} {v}" for k, v in atm.items()] + (["halo"] if (pj.get("backdrop") or {}).get("halo") else [])
    return f"FIXED zoom {z0:.2f}->{z1:.2f}; fixed effects: {', '.join(fx) or 'none'}"


def _sha_obj(obj) -> str:
    """Same hash as story_split.sha_of (canonical JSON), kept here to avoid a circular import."""
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def _easy():
    import importlib.util as iu
    sp = iu.spec_from_file_location("easy_script", ROOT / "scripts" / "source" / "easy_script.py")
    m = iu.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def load_split(run_name: str, edits_path: Path | None = None, audio_path: Path | None = None, timing_path: Path | None = None, script_path: Path | None = None) -> dict:
    """The approved-split inputs for the director: the macro, the owner's direction notes, the audio plan and the timing plan, all checked to belong to ONE split hash."""
    res = json.loads((RUNS / run_name / "macro_A1.json").read_text(encoding="utf-8"))
    if not res.get("macro"):
        raise SystemExit(f"run {run_name} holds no valid split")
    if _sha_obj(res["macro"]) != res["macro_sha256"]:
        raise SystemExit(f"run {run_name}: the saved macro does not match its recorded hash")
    edits = json.loads((edits_path or ROOT / "canon" / "story_split_edits" / "A1_rev1.json").read_text(encoding="utf-8"))
    if edits["stories"] != res["macro"]["stories"] or edits["unfilmed_ranges"] != res["macro"]["unfilmed_ranges"]:
        raise SystemExit("the edits file does not match the split of this run (the briefs, ranges or budgets differ)")
    audio = json.loads((audio_path or ROOT / "canon" / "audio" / "A1_audio_plan.json").read_text(encoding="utf-8"))
    easy = _easy()                                                                  # the owner's EASY spoken wording replaces the verse as the spoken text (A3 follow-up 8)
    audio = easy.overlay(audio, easy.load_simple(script_path or easy.DEFAULT))
    timing_plan = json.loads((timing_path or ROOT / "canon" / "audio" / "A1_timing_plan.json").read_text(encoding="utf-8"))
    for name, d in (("audio plan", audio), ("timing plan", timing_plan)):
        if d.get("split_sha256") != res["macro_sha256"]:
            raise SystemExit(f"the {name} was built for a different split; rebuild it (a1_audio.py build --run {run_name})")
    return {"macro": res["macro"], "hash": res["macro_sha256"], "edits": edits, "audio": audio, "timing": timing_plan, "script_sha256": easy.script_sha256(script_path or easy.DEFAULT)}


def split_scene_override(n: int, split: dict, ovis: dict, chapter: int = 1) -> dict:
    """What replaces the old addendum scene block: the approved brief, read-only context ovis, the narration plan (exact verse), the shot timeline and the owner's direction notes."""
    sid = f"S{n}"
    sc = next(s for st in split["macro"]["stories"] for s in st["scenes"] if s["scene_id"] == sid)
    tm = next(s for s in split["timing"]["scenes"] if s["scene"] == sid)
    lines = [l for l in split["audio"]["lines"] if l["scene"] == sid and l["priority"] == "core"]
    ctx_txt = "\n".join(f"A{chapter}:{c.split(':')[1]}: {ovis[int(c.split(':')[1])]}" for c in sc["context_ovi_ids"]) or "(none)"
    plan = "\n".join(f"{l['id']} [{l['voice']}] ovi {l['ovi']}: {l.get('spoken_marathi', l['marathi'])}" for l in lines)
    captions = "\n".join(f"caption {k['id']}: {k['marathi']} (on screen only)" for k in split["audio"].get("captions", []) if k["scene"] == sid)
    voice_of = {l["id"]: l for l in lines}
    shot_of = {b["line"]: b["shot"] for b in tm["beats"]}
    dplan = {}
    for l in lines:
        if l["voice"] in CHARACTER_VOICES:
            dplan.setdefault(shot_of[l["id"]], []).append({"id": l["id"], "ovi": l["ovi"], "marathi": l.get("spoken_marathi", l["marathi"]), "voice": l["voice"]})
    by_id = {l["id"]: l for l in lines}
    beat_rows = []                                                                  # shared bilingual beats: code-measured, the director never writes timings (schema has no timing key)
    for b in tm["beats"]:
        l = by_id.get(b["line"])
        if not l or not {"mr", "hi"} <= set(l.get("seconds", {})):
            raise SystemExit(f"{sid}: line {b['line']} has no measured Marathi and Hindi seconds; rebuild the audio plan from the measured clips")
        mr, hi = l["seconds"]["mr"], l["seconds"]["hi"]
        last = min(math.ceil(b["end_s"] / SHOT_SECONDS - 1e-9), tm["planned_shots"])        # exclusive end: a line ending exactly on a cut stays in its shot
        crossed = list(range(b["shot"] + 1, last + 1))
        cross = f"; CONTINUES over the cut into shot{'s' if len(crossed) > 1 else ''} {', '.join(map(str, crossed))}" if crossed else ""
        beat_rows.append(f"{b['line']} starts shot {b['shot']} at {b['start_s']:.2f} s, shared beat ends {b['end_s']:.2f} s (Marathi {mr:.2f} s, Hindi {hi:.2f} s, longer: {'Hindi' if hi > mr else 'Marathi' if mr > hi else 'equal'}){cross}")
    bilingual = "\n".join(beat_rows)
    tl = "\n".join(f"shot {x['shot']} ({x['from_s']:.0f}-{x['to_s']:.0f} s): " + (f"narration starts {', '.join(x['lines_starting'])} (ovi {', '.join(map(str, x['ovis']))})" if x["lines_starting"] else "visual only: continue the nearest ovi's picture")
                    + (" | dialogue entries for this shot: " + "; ".join(f"{d['id']} {d['voice']} ovi {d['ovi']}" for d in dplan.get(x["shot"], [])) if dplan.get(x["shot"]) else "") for x in tm["shots"])
    notes = "\n".join(f"- {t}" for t in split["edits"].get("direction_notes", []))
    block = (f"{sid}: ovi {sc['ovi_range'][0]}-{sc['ovi_range'][1]} (approved split {split['hash'][:12]}...). {sc['brief']}\n\n"
             f"READ-ONLY CONTEXT OVIS (not owned by this scene):\n{ctx_txt}\n\n"
             f"NARRATION PLAN (fixed audio: the pictures follow it; the owner's approved EASY spoken Marathi, script {split.get('script_sha256', 'n/a')[:12]}...; each line renders the meaning of the verse ovi it names; a character voice speaks only its own lines). Only lines with a CHARACTER voice (bankatlal, damodarpant, gajanan) go in a shot's \"dialogue\" (speaker exactly that character, Marathi exactly as below, cite that line's ovi); narrator lines are read over the picture and are NOT dialogue:\n{plan}\n{captions}\n\n"
             f"SHOT TIMELINE: direct EXACTLY {tm['planned_shots']} shots (6 s each). A shot's ovi_ids MUST list every ovi whose narration starts in it; a visual-only shot lists the ovi it continues from.\n{tl}\n\n"
             f"SHARED BEATS (ONE picture serves BOTH the Marathi and the Hindi audio; code-measured, read-only; never write timings; a line that CONTINUES over a cut needs a pose and staging that stay true in the next shot too; the shorter language rests in silence):\n{bilingual}\n\n"
             f"DIRECTION NOTES (the owner's):\n{notes}")
    return {"brief_block": block, "shots_target": tm["planned_shots"], "timeline": {x["shot"]: x["ovis"] for x in tm["shots"] if x["ovis"]}, "range": tuple(sc["ovi_range"]), "dialogue_plan": dplan}


def build_prompt(n: int, rng: tuple, files: dict, ovis: dict, presets_index: list, speakers: list, chapter: int = 1, preset_json: dict | None = None, override: dict | None = None) -> tuple[str, str]:
    lo, hi = rng
    add, ana = files["addendum"].splitlines(), files["analysis"].splitlines()
    scene_block = override["brief_block"] if override else section(add, rf"^### Scene {n} - ", r"^### Scene |^## ")
    ovi_block = "\n".join(f"A{chapter}:{k}: {ovis[k]}" for k in range(lo, hi + 1) if k in ovis)
    pjs = preset_json or {}
    preset_block = "\n".join(f"- {p['preset']}: {p['use']} ROLES: {', '.join(p['assets'])}" + (f" | {preset_facts(pjs[p['preset']])}" if p["preset"] in pjs else "") for p in presets_index)
    system = f"You are the director of a devotional motion-comic film about Shri Gajanan Maharaj of Shegaon. You write an executable shot plan for ONE scene.\n\n{RULES}\n\n{CAPS}\n\n{SCHEMA_TEXT}"
    user = (f"SCENE TO DIRECT: scene S{n}, chapter {chapter}, ovi {lo}-{hi}. Use scene_id \"S{n}\", chapter {chapter} and ovi_range [{lo}, {hi}].\n\n"
            f"=== REGISTERED SPEAKERS ===\n" + "\n".join(f"- {s}" for s in speakers) + "\n- unclear\n\n"
            f"=== PRESETS (use these names exactly) ===\n{preset_block}\n\n"
            f"=== SCENE BRIEF ({'approved split, narration and owner notes' if override else 'owner' + chr(39) + 's frozen research, video-gaps addendum'}) ===\n{scene_block}\n\n"
            f"=== DIALOGUE TABLE rows in this scene ===\n{dialogue_rows(add, lo, hi) or '(none)'}\n\n"
            f"=== MARATHI OVIS OF THIS SCENE (exact text; quote only from here) ===\n{ovi_block}\n\n"
            f"=== VISUAL DETAILS STATED IN THE TEXT ===\n{section(add, r'^## C\.', r'^## D\.')}\n\n"
            f"=== CONTINUITY ===\n{section(add, r'^## D\.', r'^## E\.')}\n\n"
            f"=== CHARACTERS ===\n{section(ana, r'^## 3\. Characters', r'^## 4\.')}\n\n"
            f"=== PLACES, OBJECTS, TIME ===\n{section(ana, r'^## 4\. Places', r'^## 5\.')}\n\n"
            f"=== OWNER'S FINAL ANSWERS (settled; do not re-open) ===\n{files['answers']}\n\n"
            f"=== GLOSSARY (owner) ===\n{files['glossary']}\n\n"
            "=== BEFORE YOU ANSWER ===\nVerify every required key in every shot (especially needs and dialogue), that every ovi of the range is in some shot's ovi_ids, and to avoid redundant restrictions while preserving every required factual assertion and safety constraint. Then return the JSON object only.\n")
    return system, user


def load_inputs():
    fc = PACKET / "frozen_copies"
    files = {"addendum": (fc / "adhyay_01__adhyay_01_video_gaps_addendum.md").read_text(encoding="utf-8"),
             "analysis": (fc / "adhyay_01_analysis_v3.md").read_text(encoding="utf-8"),
             "answers": (fc / "adhyay_01_FINAL_answers.md").read_text(encoding="utf-8"),
             "glossary": (fc / "glossary_user_supplied.md").read_text(encoding="utf-8")}
    ovis = {}
    for line in (PACKET / "adhyay_01_ovis_hj.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            ovis[r["ovi"]] = r["text"]
    presets_index = json.loads((PACKET / "presets_index.json").read_text(encoding="utf-8"))
    return files, ovis, presets_index


def load_preset_json(presets_index: list) -> dict:
    return {p["preset"]: json.loads((PRESET_DIR / f"{p['preset']}.json").read_text(encoding="utf-8")) for p in presets_index if (PRESET_DIR / f"{p['preset']}.json").exists()}


# ----------------------------------------------------------------------------- reviewers: binary questions with evidence

BLOCKING = [  # fidelity and doability: any "no" blocks approval, a missing answer blocks too
    ("Q1", "Is every spoken line the approved line of the NARRATION PLAN (or, when there is no plan, inside the ovi it cites), spoken by the speaker named (not a speaker the materials mark unclear)?"),
    ("Q2", "Is every person, object, place and event shown named in the materials, or else only a labelled STAGING scenery/light/pose/camera proposal (proposals are fine; the owner approves them later)?"),
    ("Q3", "Is every motive, feeling, thought or cause shown stated by an ovi?"),
    ("Q4", "Are miracles and teaching shown with exactly the cause the ovi gives and nothing added?"),
    ("Q5", "Can every shot that uses a preset be made as ONE held pose with a camera move and breathing only (no limb motion, walking, lip-sync or expression change)? Shots marked NEED_NEW are exempt: the code reports them as unresolved."),
    ("Q6", "Does each image description match who, where, costume and props the materials give?"),
    ("Q7", "Do the shots follow the order of events in the ovis?"),
    ("Q8", "Do the shots together cover every event of the scene's ovi range, with nothing important dropped? (Only the narrator may tell an event if its ovi is still listed in a shot.)"),
]
ADVISORY = [  # the telling: recorded for the owner, never blocks
    ("Q9", "Does the scene change something (the 'turn') the viewer can see or understand?"),
    ("Q10", "Do the shots vary in kind (wide/medium held looks and close-ups) instead of repeating one kind of shot?"),
]
RUBRIC_IDS = {q for q, _ in BLOCKING + ADVISORY}
BLOCKING_IDS = {q for q, _ in BLOCKING}
REVIEW_SYS = ("You are an independent reviewer of a shot plan for a devotional film. Judge the SHOT PLAN only against the MATERIALS in the message (the owner's frozen research and the exact Marathi ovis). "
              "Answer EVERY question below (all ten) with yes or no and quote the evidence from the materials or the plan. Answer 'no' only when you can name what in the materials contradicts the plan or fails to support it; do not flag style or taste.\n"
              "BLOCKING QUESTIONS:\n" + "\n".join(f"{q}. {t}" for q, t in BLOCKING) + "\nADVISORY QUESTIONS:\n" + "\n".join(f"{q}. {t}" for q, t in ADVISORY) + f"\n\n{CAPS}\n"
              'OUTPUT: ONE JSON object only: {"answers": [{"q": "Q1", "shot_id": "S1-2 or scene", "answer": "yes" or "no", "evidence": "...", "fix": "one sentence, only for no"}]}  '
              "Give one entry per question with shot_id \"scene\" when the answer is yes everywhere; give one 'no' entry per failing shot (its real shot_id) otherwise.")


class DirectorStop(Exception):
    """A paid or required call ended ambiguously (error, truncation, missing usage): stop the run and keep the evidence."""


def clean_review(obj, shot_ids=None) -> dict:
    """verdict PASS | BLOCK | NO_CHECK. ALL ten questions need at least one well-formed answer with evidence and a real shot_id ('scene' or one of shot_ids);
    anything missing, malformed or unknown is NO_CHECK, never PASS. Only blocking 'no' answers block."""
    bad = {"verdict": "NO_CHECK", "problems": [], "advisory": [], "missing": sorted(RUBRIC_IDS, key=lambda q: int(q[1:]))}
    if not isinstance(obj, dict) or not isinstance(obj.get("answers"), list) or not obj["answers"]:
        return bad
    answered, problems, advisory = set(), [], []
    for a in obj["answers"]:
        sid = a.get("shot_id") if isinstance(a, dict) else None
        if not (isinstance(a, dict) and a.get("q") in RUBRIC_IDS and a.get("answer") in ("yes", "no") and isinstance(a.get("evidence"), str) and a["evidence"].strip()
                and isinstance(sid, str) and (sid == "scene" or shot_ids is None or sid in shot_ids)):
            return bad
        row = {"shot_id": sid, "kind": a["q"], "problem": a["evidence"].strip(), "fix": a.get("fix") if isinstance(a.get("fix"), str) else ""}
        answered.add(a["q"])
        if a["answer"] == "no":
            (problems if a["q"] in BLOCKING_IDS else advisory).append(row)
    missing = sorted(RUBRIC_IDS - answered, key=lambda q: int(q[1:]))
    if missing:
        return {"verdict": "NO_CHECK", "problems": problems, "advisory": advisory, "missing": missing}
    return {"verdict": "BLOCK" if problems else "PASS", "problems": problems, "advisory": advisory, "missing": []}


# ----------------------------------------------------------------------------- agents

Agent = namedtuple("Agent", "name call secrets paid", defaults=(False,))   # call(system, user, max_tokens=None) -> (reply_text, info dict); info: provider/model/status/wall_s/finish/error (+ usage, cost for paid); secrets: strings scrubbed from every parsed reply


def nvidia_agent(pool, keys: list, model: str) -> Agent:
    def call(system, user, max_tokens=None):
        reply, info = ds.chat_stream(pool, keys, model, system, user, **({"max_tokens": max_tokens} if max_tokens else {}))
        return nt.scrub(reply or "", keys), {"provider": "nvidia", "model": model, **info}
    return Agent(model, call, tuple(keys), False)


def recorded(agent: Agent, run, n: int) -> Agent:
    """Writes every completed call (reply + info) to the run folder the moment it returns, and REPLAYS it on resume instead of calling (and paying) again."""
    def call(system, user, max_tokens=None):
        h = hashlib.sha256(json.dumps([agent.name, system, user, max_tokens], ensure_ascii=False).encode()).hexdigest()[:16]
        rel = f"calls/scene{n}__{re.sub(r'[^A-Za-z0-9.-]', '_', agent.name)[-40:]}__{h}.json"
        if run.has(rel):
            d = run.read_json(rel)
            return d["reply"], {**d["info"], "replayed": True}
        k = 0
        if agent.paid:                                                          # identity of the attempt is saved BEFORE dispatch: a crash after the charge can never silently re-buy
            k = 1
            while run.has(f"{rel}.attempt{k}"):
                if not run.has(f"{rel}.refused{k}"):                           # a 'refused' marker proves the money guard stopped that attempt BEFORE anything was sent
                    raise DirectorStop(f"an earlier PAID attempt for this exact request ({rel}) was dispatched but its reply was never saved; it will not be bought again. Check the provider dashboard, then start a new run with --redo")
                k += 1
            run.write_once(f"{rel}.attempt{k}", json.dumps({"agent": agent.name, "at": time.strftime("%Y-%m-%d %H:%M:%S")}))
        try:
            reply, info = agent.call(system, user, max_tokens)
        except BaseException as exc:
            if agent.paid and type(exc).__name__ == "Refused":                  # the money guard refused before any dispatch: nothing was bought
                run.write_once(f"{rel}.refused{k}", json.dumps({"why": str(exc)[:200]}))
            raise
        run.write_once(rel, json.dumps({"reply": reply, "info": info}, ensure_ascii=False))
        return reply, info
    return Agent(agent.name, call, agent.secrets, agent.paid)


def _json(reply, secrets=()):
    try:
        return ds.scrub_obj(ds.extract_json(reply, dict), list(secrets))
    except ValueError:
        return None


def _ask(agent: Agent, system: str, user: str, log: list, label: str, max_tokens=None, must=True):
    """One call. An error, truncation or missing usage stops the run when `must` (the director); a reviewer's failure just yields no answer (NO_CHECK)."""
    reply, info = agent.call(system, user, max_tokens)
    log.append({"step": label, "agent": agent.name, **info})
    if info.get("error") or info.get("finish") != "stop":                       # only a complete, successful reply is used
        if must:
            raise DirectorStop(f"{agent.name} {label}: {info.get('error') or 'reply not complete (finish=' + str(info.get('finish')) + ')'}")
        return None
    return _json(reply, agent.secrets)


def review_plan(agent: Agent, materials: str, plan: dict, log: list) -> dict:
    try:
        obj = _ask(agent, REVIEW_SYS, materials + "\n\n=== SHOT PLAN TO REVIEW ===\n" + json.dumps(plan, ensure_ascii=False), log, "review", 24000, must=False)
    except Exception as exc:                                                    # a reviewer that cannot be reached is a missing check, not a crash
        log.append({"step": "review", "agent": agent.name, "error": type(exc).__name__})
        obj = None
    return {"model": agent.name, **clean_review(obj, {sh["shot_id"] for sh in plan["shots"]})}


# ----------------------------------------------------------------------------- repair: shot-locked

def lock(shot: dict) -> str:
    return hashlib.sha256(json.dumps(shot, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def affected(problems: list, scene: dict) -> tuple[set, bool]:
    """problems: [(shot_id or other, text)] -> (shot ids that fail, whether any problem is scene-level)."""
    ids = {sh["shot_id"] for sh in scene["shots"]}
    hit = {s for s, _ in problems if s in ids}
    return hit, any(s not in ids for s, _ in problems)


def splice(old: dict, reply, ids: set, scene_level: bool = False) -> tuple[dict | None, str]:
    """Shot-locked repair (CineCrew 'change nothing else'). Only the failing shots may change; every other shot is hash-locked; images used by locked shots keep their
    description; 'goal' and 'turn' may change only when a problem is scene-level. Anything else in the reply is refused."""
    allowed = {"shots", "images_needed"} | ({"goal", "turn"} if scene_level else set())
    if not isinstance(reply, dict) or set(reply) - allowed or not isinstance(reply.get("shots", []), list):
        return None, f"the repair may contain only {sorted(allowed)}"
    got = {s.get("shot_id"): s for s in reply.get("shots", []) if isinstance(s, dict)}
    if len(reply.get("shots", [])) != len(ids) or set(got) != set(ids):
        return None, f"the repair must return exactly the shots {sorted(ids)}"
    new = copy.deepcopy(old)
    new["shots"] = [got[s["shot_id"]] if s["shot_id"] in ids else s for s in old["shots"]]
    for k in ("goal", "turn"):
        if k in reply:
            new[k] = reply[k]
    before = {s["shot_id"]: lock(s) for s in old["shots"] if s["shot_id"] not in ids}
    if any(before[s["shot_id"]] != lock(s) for s in new["shots"] if s["shot_id"] not in ids):
        return None, "a locked shot changed"
    imgs = {im["image_id"]: im for im in old["images_needed"]}
    locked_use = {v for s in old["shots"] if s["shot_id"] not in ids for v in s["assets"].values()}
    extra = reply.get("images_needed", [])
    if not isinstance(extra, list):
        return None, "images_needed must be a list"
    for im in extra:
        if not isinstance(im, dict) or not isinstance(im.get("image_id"), str):
            return None, "malformed image entry"
        if im["image_id"] in locked_use and imgs.get(im["image_id"]) != im:
            return None, f"image {im['image_id']} is used by a locked shot and may not change"
        imgs[im["image_id"]] = im
    used = {v for s in new["shots"] for v in (s.get("assets") or {}).values() if isinstance(v, str)}
    new["images_needed"] = [im for k, im in imgs.items() if k in used]          # an image nobody uses any more is dropped
    return new, ""


def preserves_content(old: dict, new: dict) -> list:
    """Reasons a repaired plan is NOT acceptable: it must still show every ovi the original showed, keep a dialogue entry for every ovi the original had one, and still show the turn ovi."""
    def shown(p):
        return {n for sh in p["shots"] for n in sh["ovi_ids"]}

    def spoken(p):
        return Counter((d["ovi"], qnorm(d["marathi"])) for sh in p["shots"] for d in sh["dialogue"])
    why = []
    if shown(old) - shown(new):
        why.append(f"dropped ovis {sorted(shown(old) - shown(new))}")
    lost = spoken(old) - spoken(new)
    if lost:
        why.append(f"dropped dialogue for ovis {sorted({k[0] for k in lost})} ({sum(lost.values())} line(s))")
    if new["turn"]["ovi"] not in shown(new):
        why.append("the turn ovi is not shown")
    return why


REPAIR_CONTRACT = """REPAIR MODE. You are repairing a shot plan you wrote. IGNORE the instruction above to output a whole scene: for this repair output ONLY a patch, ONE JSON object with these keys:
"shots": the corrected versions of exactly the failing shots listed in the message (complete shot objects, same shot_id), nothing else;
"images_needed": optional, only NEW or CHANGED image entries (an image used by a locked shot may not change);
"goal" and "turn": only when a listed problem is scene-level.
Every shot you do not list is LOCKED and stays exactly as it is. The corrected plan must still show every ovi the original showed, keep every spoken line, and keep the turn ovi shown. Fix a problem only if it is real when checked against the materials. All rules above still apply."""


def repair_round(director: Agent, system: str, materials: str, scene: dict, problems: list, check, log: list, label: str) -> tuple[dict | None, list, dict]:
    """The single repair round. Returns (accepted plan or None, its warnings, record). Always shot-locked: scene-level problems unlock only goal/turn/images, never the other shots."""
    ids, scene_level = affected(problems, scene)
    lines = "\n- ".join(f"{s}: {t}" for s, t in problems[:30])
    rec = {"label": label, "problems_sent": [f"{s}: {t}" for s, t in problems[:30]], "scope": sorted(ids) + (["scene-level"] if scene_level else []), "status": "NOT_USED"}
    locked = [sh["shot_id"] for sh in scene["shots"] if sh["shot_id"] not in ids]
    obj = _ask(director, system + "\n\n" + REPAIR_CONTRACT, materials + "\n\nYOUR PLAN (read-only context):\n" + json.dumps(scene, ensure_ascii=False)
               + f"\n\nFAILING SHOTS TO RETURN: {sorted(ids)}. LOCKED SHOTS: {locked}.\nPROBLEMS:\n- " + lines, log, label)
    new, why = splice(scene, obj, ids, scene_level)
    notes = []
    if new is not None:
        new, notes = normalise(new)
    if new is None:
        rec["status"] = f"REJECTED ({why})"
        return None, [], rec
    errs, warns = check(new)
    lost = preserves_content(scene, new) if not errs else []
    if errs:
        rec["status"] = "REJECTED (still invalid: " + "; ".join(errs[:3]) + ")"
    elif lost:
        rec["status"] = "REJECTED (the repair lost content: " + "; ".join(lost) + ")"
    else:
        rec["status"] = "USED"
        return new, notes + warns, rec
    return None, [], rec


def _problem_rows(errors: list) -> list:
    return [((re.match(r"^(S[0-9]-[0-9]{1,2})\b", e) or [None, "scene"])[1], e) for e in errors]


def _review_rows(reviews: list) -> list:
    rows, seen = [], set()
    for rv in reviews:
        for p in rv["problems"]:
            key = (p["shot_id"], p["problem"][:60])
            if key not in seen:
                seen.add(key)
                rows.append((p["shot_id"], f"[{rv['model'].split('/')[-1]}] {p['kind']}: {p['problem']} Fix: {p['fix']}"))
    return rows


def direct_scene(director: Agent, reviewers: list, n: int, rng: tuple, chapter: int, files: dict, ovis: dict, presets_index: list, ctx: dict, override: dict | None = None) -> dict:
    """Directs ONE scene, once: at most TWO director calls in total (the first answer plus either one JSON re-ask or the single repair round)."""
    presets = {p["preset"]: p["assets"] for p in presets_index}
    ovi_text = {k: v for k, v in ovis.items() if rng[0] <= k <= rng[1]}
    system, materials = build_prompt(n, rng, files, ovis, presets_index, sorted(x for x in ctx["speakers"] if "(" not in x), chapter, ctx["preset_json"], override)
    ctx = {**ctx, "packet_text": ctx.get("packet_text") or materials}
    if override:
        ctx = {**ctx, "scene_image_prefix": True, "shots_target": override["shots_target"], "timeline": override["timeline"], "dialogue_plan": override["dialogue_plan"]}
    check = lambda sc: validate_scene(sc, presets, ovi_text, rng, ctx, chapter, f"S{n}")
    log, repairs = [], []
    out = {"scene": n, "chapter": chapter, "range": list(rng), "result": "FAILED", "errors": [], "warnings": [], "plan": None, "calls": log, "reviews": [], "repairs": repairs, "final_reviews": []}
    scene, director_calls = None, 0
    for attempt in range(1 if ONE_CALL else 2):                                 # first answer; one re-ask only if the reply was not JSON (never with --one-call)
        director_calls += 1
        scene = _ask(director, system, materials if attempt == 0 else materials + "\n\nYour last reply was not a single JSON object. Reply with ONLY the JSON object.", log, "generate")
        if scene is not None:
            break
    if scene is None:
        out["errors"] = ["the reply was not a JSON object"]
        return out
    scene, notes = normalise(scene)
    errors, warnings = check(scene)
    warnings = notes + warnings
    can_repair = director_calls < 2 and not ONE_CALL                                           # the owner's limit: no loops, two director calls at most
    if errors:                                                                  # the single repair round, spent here when the validator fails
        if can_repair and jsonschema.Draft202012Validator(SCENE).is_valid(scene):
            can_repair = False
            new, w2, rec = repair_round(director, system, materials, scene, _problem_rows(errors), check, log, "validator_repair")
            repairs.append(rec)
            if new:
                out["plan_before_repair"], scene, errors, warnings = scene, new, [], w2
    out["plan"], out["errors"], out["warnings"] = scene, errors, warnings
    if errors:
        out["result"] = "INVALID"
        return out
    status = scene_status(scene, errors)
    out["status"] = status
    if not reviewers:
        out["result"], out["reviewed"] = "UNREVIEWED", False                    # a skipped cross-check is never a success
        return out
    with ThreadPoolExecutor(max_workers=len(reviewers)) as ex:                  # independent reviewers in parallel
        out["reviews"] = list(ex.map(lambda r: review_plan(r, materials, scene, log), reviewers))
    final = out["reviews"]
    if any(r["verdict"] == "BLOCK" for r in final) and can_repair:               # the single repair round, on the blocked shots only; the re-review below only CHECKS it
        new, w2, rec = repair_round(director, system, materials, scene, _review_rows(final), check, log, "review_repair")
        repairs.append(rec)
        if new:
            out["plan_before_repair"], scene, out["plan"], out["warnings"] = scene, new, new, w2
            with ThreadPoolExecutor(max_workers=len(reviewers)) as ex:
                final = out["final_reviews"] = list(ex.map(lambda r: review_plan(r, materials, scene, log), reviewers))
            status = out["status"] = scene_status(scene, [])
    out["reviewed"] = True
    verdicts = {r["verdict"] for r in final}
    out["result"] = "REVIEW_BLOCKED" if "BLOCK" in verdicts else "NO_CHECK" if "NO_CHECK" in verdicts else status
    return out


# ----------------------------------------------------------------------------- report

def review_text(results: list, model: str) -> str:
    L = [f"# Director run, Adhyay 1 ({len(results)} scenes), director `{model}`", "", "DRAFT shot plans for the owner's review. Nothing is rendered or approved. VALID means the validator found no structural, quoting or provenance error AND every reviewer answered every blocking question 'yes'; it does not mean the plan is good. UNRESOLVED = at least one shot is NEED_NEW (never a success). NO_CHECK = a required check is missing (the owner may answer it). UNREVIEWED = no cross-check was run (never a success).", ""]
    for r in results:
        L += [f"## Scene {r['scene']} (ovi {r['range'][0]}-{r['range'][1]}): {r['result']}", ""]
        for call in r["calls"]:
            L.append(f"- {call.get('step')} `{call.get('agent')}`: HTTP {call.get('status')}, {call.get('wall_s')} s, finish {call.get('finish')}" + (f", error {call['error']}" if call.get("error") else ""))
        if r["errors"]:
            L += ["", "Validator ERRORS:"] + [f"- {e}" for e in r["errors"]]
        if r["warnings"]:
            L += ["", "Warnings (for the owner; STAGING items need your approval):"] + [f"- {w}" for w in r["warnings"]]
        for label, group in (("original plan", r.get("reviews", [])), ("repaired plan", r.get("final_reviews", []))):
            for rv in group:
                L += ["", f"Reviewer `{rv['model']}` ({label}): **{rv['verdict']}**" + (f", missing answers {rv['missing']}" if rv.get("missing") else "")]
                L += [f"- {p['shot_id']} [{p['kind']}] {p['problem']} Fix: {p['fix']}" for p in rv["problems"]]
                L += [f"- advisory {p['shot_id']} [{p['kind']}] {p['problem']}" for p in rv.get("advisory", [])]
        for rp in r.get("repairs", []):
            L += ["", f"Repair `{rp['label']}` (scope {rp['scope']}): **{rp['status']}**"]
        p = r["plan"]
        if p:
            L += ["", f"**Goal:** {p.get('goal')}", f"**Turn ({p.get('turn', {}).get('ovi')}):** {p.get('turn', {}).get('text')}", ""]
            for sh in p.get("shots", []):
                L += [f"### {sh.get('shot_id')}: {sh.get('preset')} (6 s), ovi {sh.get('ovi_ids')}",
                      f"- action: {sh.get('action')}", f"- held pose: {sh.get('held_pose')}", f"- performance: {sh.get('performance')}", f"- camera: {sh.get('camera')}", f"- assets: {json.dumps(sh.get('assets'), ensure_ascii=False)}"]
                if sh.get("need_new_reason"):
                    L.append(f"- NEED_NEW: {sh['need_new_reason']}")
                for d in sh.get("dialogue", []):
                    L.append(f"- dialogue ({d.get('ovi')}, {d.get('speaker')}): {d.get('marathi') or ''} / {d.get('meaning_en')}")
                L += [f"- claims: {json.dumps(sh.get('claims'), ensure_ascii=False)}", f"- staging: {' | '.join(sh.get('staging', []))}", f"- transition out: {sh.get('transition_out')}", ""]
            fin = finalize(p) if jsonschema.Draft202012Validator(SCENE).is_valid(p) else p
            L += ["**Images the owner would need to make:**"] + [f"- {im.get('image_id')}: {im.get('description')} (used in {', '.join(im.get('used_in', []))})" for im in fin.get("images_needed", [])] + [""]
    return "\n".join(L) + "\n"


# ----------------------------------------------------------------------------- main

def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_packet() -> dict:
    """Recomputes every file the packet MANIFEST lists AND every file the director reads; refuses to run if any differs. Returns rel path -> sha256."""
    man = json.loads((PACKET / "MANIFEST.json").read_text(encoding="utf-8"))
    listed = {f["path"]: f["sha256"] for f in man["files"]}
    consumed = ["adhyay_01_ovis_hj.jsonl", "presets_index.json", "frozen_copies/adhyay_01__adhyay_01_video_gaps_addendum.md", "frozen_copies/adhyay_01_analysis_v3.md",
                "frozen_copies/adhyay_01_FINAL_answers.md", "frozen_copies/glossary_user_supplied.md"]
    hashes = {rel: _sha(PACKET / rel) for rel in sorted(set(listed) | set(consumed))}
    bad = [rel for rel, h in listed.items() if hashes[rel] != h]
    if bad:
        raise SystemExit(f"packet files differ from MANIFEST.json: {bad}")
    return hashes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run-name", help="folder under canon/director_runs/; a new name starts a run, an existing one needs --resume")
    ap.add_argument("--resume", action="store_true", help="continue an existing run: finished scenes are verified by hash and skipped; recorded paid replies are replayed, never re-bought")
    ap.add_argument("--scenes", default=None, help="default: 1,4,6 (old addendum split) or every scene of --split-run")
    ap.add_argument("--split-run", default=None, help="direct from the approved split of this run (canon/director_runs/<name>/macro_A1.json) with the audio and timing plans")
    ap.add_argument("--director", choices=["kimi", "nvidia"], default="kimi")
    ap.add_argument("--model", default=None, help="director model (default: kimi-k3.1-pro, or the Nemotron Ultra for --director nvidia)")
    ap.add_argument("--redo", action="store_true", help="direct a scene again although this director already directed it in another run (owner's decision only)")
    ap.add_argument("--allow-paid", action="store_true", help="required for --director kimi (paid; money guard P4 applies)")
    ap.add_argument("--one-call", action="store_true", help="exactly ONE director call per scene: no JSON re-ask, no repair round (the owner decides after reading the validator result)")
    ap.add_argument("--effort", choices=["low", "medium", "high"], default="high", help="Kimi reasoning_effort (default high; the cost lever is low)")
    ap.add_argument("--max-tokens", type=int, default=None, help="Kimi max output tokens (sets the ledger worst case; default the adapter's)")
    ap.add_argument("--probe", action="store_true", help="with --director kimi --allow-paid: ONE tiny call (about $0.01) to confirm the model id works; no run folder")
    ap.add_argument("--reviewers", default=None, help="comma-separated NVIDIA reviewer models; default Nemotron Ultra (or the older pair when Nemotron directs); '' = none (the result is then UNREVIEWED, never VALID)")
    a = ap.parse_args()
    globals()["ONE_CALL"] = a.one_call
    if not a.probe and not a.run_name:
        raise SystemExit("--run-name is required")
    run_mod = _load("director_run", ROOT / "scripts" / "source" / "director_run.py")
    keys = nt.load_keys()
    if not keys:
        raise SystemExit("no usable NVIDIA key")
    pool = nt.KeyPool(keys)
    settings = {}
    if a.director == "kimi":
        if not a.allow_paid:
            raise SystemExit("--director kimi is a paid call: add --allow-paid (the money guard P4, $1, still applies)")
        kimi = _load("kimi_adapter", ROOT / "scripts" / "source" / "kimi_adapter.py")
        try:
            director = kimi.make_agent(model=a.model or kimi.MODEL, json_mode=a.probe, effort=a.effort, max_tokens=a.max_tokens or kimi.MAX_TOKENS)
        except kimi.ledger_mod.Refused as exc:
            raise SystemExit(f"REFUSED: {exc}")
        settings = {"model": director.name, "effort": a.effort, "max_tokens": a.max_tokens or kimi.MAX_TOKENS, "phase": kimi.PHASE}
        default_reviewers = NVIDIA_MODEL
        if a.probe:
            try:
                res = kimi.probe(director)
            except kimi.ledger_mod.Refused as exc:
                print("REFUSED by the money guard:", exc)
                return 2
            print(json.dumps(res, indent=2))
            return 0 if res["answered_ok_json"] and not res["error"] and res["finish"] == "stop" else 1
    else:
        director = nvidia_agent(pool, keys, a.model or NVIDIA_MODEL)
        settings = {"model": director.name}
        default_reviewers = "openai/gpt-oss-20b,z-ai/glm-5.3-flash"
    names = tuple(m for m in (default_reviewers if a.reviewers is None else a.reviewers).split(",") if m)
    if director.name in names:
        raise SystemExit("a reviewer must be a different model from the director")
    reviewers = [nvidia_agent(pool, keys, m) for m in names]
    packet_hashes = verify_packet()
    files, ovis, presets_index = load_inputs()
    split, overrides = None, {}
    if a.split_run:
        split = load_split(a.split_run)
        overrides = {int(sc["scene_id"][1:]): split_scene_override(int(sc["scene_id"][1:]), split, ovis) for st in split["macro"]["stories"] for sc in st["scenes"]}
        ranges = {n: o["range"] for n, o in overrides.items()}
    else:
        ranges = scene_ranges(files["addendum"].splitlines())
    wanted = [int(x) for x in (a.scenes or (",".join(map(str, sorted(ranges))) if a.split_run else "1,4,6")).split(",")]
    if any(n not in ranges for n in wanted):
        raise SystemExit(f"unknown scene; available: {sorted(ranges)}")
    ctx = {"packet_text": "", "speakers": speaker_registry(files["analysis"].splitlines()), "preset_json": load_preset_json(presets_index), "prop_materials": {},
           "speaker_rows": speaker_table(files["addendum"].splitlines())}
    here = ROOT / "scripts" / "source"
    inputs = {"packet_files": packet_hashes, "director": director.name, "reviewers": list(names), "settings": settings, "scenes": wanted,
              "code_sha256": {**{f: _sha(here / f) for f in ("director_test.py", "director_run.py", "kimi_adapter.py", "draft_source.py")},      # the prompts live in director_test.py
                              **{f: _sha(ROOT / "scripts" / "image_trials" / f) for f in ("v5_ledger.py", "nvidia_trial.py")}},
              "presets_sha256": {p: _sha(PRESET_DIR / f"{p}.json") for p in sorted(ctx["preset_json"])},
              "split": {"run": a.split_run, "hash": split["hash"] if split else None, "files": {f: _sha(ROOT / "canon" / f) for f in ("story_split_edits/A1_rev1.json", "audio/A1_audio_plan.json", "audio/A1_timing_plan.json")} if split else {}}}
    run = run_mod.open_run(RUNS, a.run_name, inputs, resume=a.resume)
    atexit.register(run.release)
    todo = [n for n in wanted if not run.has(f"a01_scene{n}.json")]
    done_before = run_mod.directed_elsewhere(RUNS, a.run_name, director.name, todo)
    if done_before and not a.redo:
        raise SystemExit(f"already directed once by {director.name}: {done_before}; each scene is directed once per Adhyay (add --redo only if the owner says so)")
    t0 = time.time()

    def one(n: int) -> dict:
        run_mod.claim_scene(RUNS, director.name, n, a.run_name, a.redo)                # atomic, before any paid dispatch
        r = direct_scene(recorded(director, run, n), [recorded(x, run, n) for x in reviewers], n, ranges[n], 1, files, ovis, presets_index, ctx, overrides.get(n))
        run.write_once(f"a01_scene{n}.json", json.dumps(r, indent=2, ensure_ascii=False))
        return r
    try:
        if a.director == "kimi":                                                # paid calls one scene at a time: stop at the first ambiguous charge
            for n in todo:
                one(n)
        else:
            with ThreadPoolExecutor(max_workers=max(1, len(todo))) as ex:
                list(ex.map(one, todo))
    except Exception as exc:                                                    # DirectorStop, the money guard's Refused, anything else: keep what is saved
        run.finish({"status": f"STOPPED ({type(exc).__name__}: {str(exc)[:200]})"})
        print("STOPPED:", type(exc).__name__, str(exc)[:200], "| finished scenes and every paid reply are saved; --resume continues without re-buying")
        return 2
    allr = [run.read_json(f"a01_scene{n}.json") for n in wanted]
    run.write_once("REVIEW.md" if not run.has("REVIEW.md") else f"REVIEW_{int(time.time())}.md", review_text(allr, director.name))
    plans = {r["scene"]: finalize(r["plan"]) for r in allr if r["result"] in ("VALID", "UNRESOLVED", "UNREVIEWED", "NO_CHECK", "REVIEW_BLOCKED") and r["plan"]}
    if plans and not run.has("shot_id_map.json"):
        run.write_once("shot_id_map.json", json.dumps(run_mod.map_shot_ids([sh["shot_id"] for p in plans.values() for sh in p["shots"]]), indent=2))
    manifest_path = ROOT / "canon" / "film_manifest.json"                       # ONE film manifest (locked transaction); approvals are recorded only by the owner, never here
    try:
        run_mod.update_manifest(manifest_path, "gajanan-vijay-a1-a2", lambda m: run_mod.update_film_manifest(m, packet_hashes, plans))
    except ValueError as exc:                                                   # the results are already saved; the owner resolves the conflict
        run.finish({"status": "MANIFEST_CONFLICT (results saved, film manifest NOT updated)", "manifest_conflict": str(exc)[:300]})
        print("MANIFEST NOT UPDATED:", exc)
        return 1
    run.finish({"status": "DRAFT, not approved; nothing rendered", "wall_s": round(time.time() - t0, 1), "results": {r["scene"]: r["result"] for r in allr}})
    for r in allr:
        print(f"scene {r['scene']} (ovi {r['range'][0]}-{r['range'][1]}): {r['result']}; {len(r['errors'])} errors, {len(r['warnings'])} warnings")
    return 0 if all(r["result"] == "VALID" for r in allr) else 1


if __name__ == "__main__":
    sys.exit(main())
