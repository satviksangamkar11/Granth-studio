"""Adhyay 1 voices (DRAFT; Indic Parler-TTS, Apache-2.0, NOT VALIDATED until the owner has listened). Builds the text-to-speech job list from the audio plan: every line, in Marathi and in Hindi.
Voice map = speaker names the model card lists (Marathi: Sanjay, Sunita, Nikhil, Radha, Varun, Isha; Hindi: Rohit, Divya, Aman, Rani) plus an English 'description' of the voice.
Hindi has only two male speakers, so Bankatlal and Damodarpant share 'Aman' and differ only by the description (the owner decides after listening).
Text preparation only removes verse marks (danda) and quote marks and adds pauses with commas; it never changes a word."""
from __future__ import annotations

import hashlib
import json
import re

CLEAR = "very clear audio, very close recording with almost no background noise"
VOICES = {
    "mr": {
        "narrator": ("Sunita", f"Sunita's voice is calm, warm and measured, with a slow, even pace and a gentle storyteller's tone, {CLEAR}."),
        "gajanan": ("Sanjay", f"Sanjay's voice is deep, serene and very slow, gentle and composed, with long pauses between phrases, {CLEAR}."),
        "bankatlal": ("Nikhil", f"Nikhil's voice is respectful and clear, at a moderate pace, a little curious and humble, {CLEAR}."),
        "damodarpant": ("Varun", f"Varun's voice is a little higher and lighter, earnest and slightly quicker, {CLEAR}."),
    },
    "hi": {
        "narrator": ("Divya", f"Divya's voice is calm, warm and measured, with a slow, even pace and a gentle storyteller's tone, {CLEAR}."),
        "gajanan": ("Rohit", f"Rohit's voice is deep, serene and very slow, gentle and composed, with long pauses between phrases, {CLEAR}."),
        "bankatlal": ("Aman", f"Aman's voice is respectful and clear, at a moderate pace, a little curious and humble, {CLEAR}."),
        "damodarpant": ("Aman", f"Aman's voice is younger, a little higher and lighter, earnest and slightly quicker, {CLEAR}."),
    },
}
LANGS = ("mr", "hi")


def prep_text(text: str) -> str:
    """Pauses for the model: danda -> comma/full stop, quote marks dropped, spaces collapsed. No word is changed."""
    t = text.replace("’", "").replace("‘", "").replace("“", "").replace("”", "").replace('"', "").replace("'", "")
    t = re.sub(r"\s*।\s*(?=\S)", ", ", t)
    t = re.sub(r"\s*।\s*$", ".", t)
    t = re.sub(r"\s*,\s*,", ",", t)
    t = " ".join(t.split())
    return t if re.search(r"[.?!]$", t) else t + "."


def build_jobs(plan: dict) -> list:
    jobs = []
    for l in plan["lines"]:
        for lang in LANGS:
            speaker, desc = VOICES[lang][l["voice"]]
            text = prep_text(l["marathi"] if lang == "mr" else l["hindi"])
            jobs.append({"id": f"{l['id']}.{lang}", "line": l["id"], "lang": lang, "voice": l["voice"], "speaker": speaker, "description": desc, "text": text,
                         "priority": l["priority"], "scene": l["scene"], "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                         "seed": int(hashlib.sha256((l["id"] + lang).encode()).hexdigest()[:8], 16)})
    return jobs


def build_input(plan: dict) -> dict:
    jobs = build_jobs(plan)
    return {"model": "ai4bharat/indic-parler-tts", "split_sha256": plan.get("split_sha256"), "status": "DRAFT voices, NOT VALIDATED until the owner has listened", "jobs": jobs}


if __name__ == "__main__":
    import sys
    plan = json.loads(open(sys.argv[1], encoding="utf-8").read())
    out = build_input(plan)
    open(sys.argv[2], "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
    print(len(out["jobs"]), "jobs")
