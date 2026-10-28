# SPEC: coder calls send thinking OFF and reasoning effort MEDIUM (owner 2026-10-28). Return exactly THREE files in full:
`scripts/source/draft_source.py`, `scripts/source/nemotron_code.py`, `tests/test_effort_settings.py` (NEW test file; do not touch the existing tests).
Evidence (live probe 2026-10-28): the endpoint accepts for `nvidia/nemotron-3-ultra-550b-a55b` the top-level field `reasoning_effort` ("low"|"medium"|"high") and `chat_template_kwargs: {"enable_thinking": true|false}`; disabling thinking gave 0 reasoning. These fields are NOT proven for other models (GLM) and must NOT be sent to them.
Owner decision (final): defaults are thinking OFF and effort MEDIUM (both fields are sent together by default). The combination off+medium was not in the probe, so keep `--effort none` available to drop the effort field.
## Changes
1. `draft_source.chat_stream(...)`: add an optional last parameter `extra: dict | None = None`. After building `body`, merge `extra` into it, ignoring the protected keys `model`, `messages`, `stream`, `max_tokens`, `temperature`. Everything else unchanged (existing callers and tests keep working).
2. Add to `nemotron_code.py` a pure function `request_extra(model: str, effort: str, thinking: str) -> dict`: for a model whose id starts with `nvidia/nemotron`: returns `{"chat_template_kwargs": {"enable_thinking": thinking == "on"}}` plus `{"reasoning_effort": effort}` when effort is not "none". For any other model returns `{}`.
3. CLI: `--effort` choices low|medium|high|none, default medium; `--thinking` choices on|off, default OFF. `main()` passes `extra=request_extra(a.model, a.effort, a.thinking)` to `ds.chat_stream`. The printed call info line must also show effort and thinking (never a key).
## Tests (synthetic, no network, no key): `request_extra` for nemotron default (medium, thinking off) gives exactly `{"chat_template_kwargs": {"enable_thinking": False}, "reasoning_effort": "medium"}`; effort none gives only chat_template_kwargs; thinking on gives enable_thinking True; GLM id gives {}; unknown id gives {}. `chat_stream` with a fake pool and a monkeypatched `_stream_once` capturing the body: extra merged; protected keys in extra ignored (body temperature stays 0.2, stream True, max_tokens as passed); extra None leaves body as before.
Reply with only the three FILE blocks.

## CURRENT scripts/source/draft_source.py
```python
"""DRAFTS for owner review (decision D-018), never canon: English meanings of one Adhyay's ovis and its characters/places list, from free NVIDIA chat models.
One model drafts, a model of another family checks each meaning; names in the characters list are string-checked against the ovis they cite. Nothing here is approved.

  python scripts/source/draft_source.py --adhyay 1 [--drafter deepseek-ai/deepseek-v4.1-flash] [--checker z-ai/glm-5.3] [--only meanings|characters]

In:  canon/source_hj/adhyay_NN.jsonl (ovis). Out: canon/drafts/aNN_meanings_DRAFT.jsonl, aNN_characters_places_DRAFT.json, aNN_REVIEW.md, aNN_receipt.json.
Keys: nvidia_trial.load_keys (never printed); requests only to NVIDIA hosts, no redirects, every reply scrubbed of keys."""
from __future__ import annotations

import argparse
import http.client
import json
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "image_trials"))
import nvidia_trial as nt  # noqa: E402

URL = "https://integrate.api.nvidia.com/v1/chat/completions"
BATCH = 5
CONTEXT = 3

MEANING_SYS = """You translate Marathi ovis of Shri Gajanan Vijay (by Dasganu) into plain English for a film team.
For each ovi in TRANSLATE give a faithful, close meaning in 1-3 short sentences.
Rules:
- Add nothing: no facts, interpretation, praise or explanation that the ovi does not contain.
- Keep every name as written, transliterated (e.g. Bankatlal, Damodarpant, Devidas). Keep numbers and dates exact.
- If a word or line is unclear, give your best close reading, set "unclear": true and say why in "note".
- "speaker": who is speaking in this ovi if the ovi or the CONTEXT makes it clear, else null. "Dasganu" when the poet speaks.
- CONTEXT ovis are for understanding only; do not translate them.
Output JSON only, no other text: [{"ovi": n, "meaning_en": "...", "speaker": null, "unclear": false, "note": ""}]"""

CHECK_SYS = """You check English meanings of Marathi ovis of Shri Gajanan Vijay.
Judge each meaning against the Marathi ovi itself; CONTEXT ovis are only for understanding.
For each ovi: "OK" if the meaning is faithful and adds nothing; "ISSUE" if anything is missing, added, reversed, mistranslated, or a name, number or the SPEAKER is wrong.
For ISSUE, "note" says what is wrong and gives a corrected meaning. Do not flag style.
Output JSON only, no other text: [{"ovi": n, "verdict": "OK", "note": ""}]"""

CHARCHECK_SYS = """You check a draft list of people and places made from the ovis of one Adhyay of Shri Gajanan Vijay. Use ONLY the ovis given.
Report a problem when: an entry's role, description or name is not stated in its cited ovis; a person or place in the narrated events is missing; two entries are the same person; a person only named in an invocation is listed as a character.
Output JSON only, no other text: {"problems": [{"id": "char_id or place_id or MISSING", "problem": "one sentence", "ovis": [n]}]}  (empty list if none)"""

CHAR_SYS = """You list the people and places of one Adhyay of Shri Gajanan Vijay, using ONLY the ovis given. Do not use outside knowledge of the Granth.
characters: everyone who appears or acts in the narrated events (not people only named in invocations or lists of saints). For each:
  "char_id": snake_case ASCII starting "char_" (e.g. "char_bankatlal"),
  "names_in_text": the exact Marathi spellings used in the ovis (copy them character for character),
  "name_en": transliterated name, "role": one line, only what the ovis state,
  "description": only what the ovis state about age, body, clothing, objects carried; null if nothing is stated,
  "evidence_ovis": the ovi numbers where they appear or are described.
places: every place named or shown in the narrated events: "place_id" ("loc_..."), "names_in_text", "name_en", "description" (only what is stated, else null), "evidence_ovis".
named_only: people or deities only named in invocations or lists: {"name_en": "...", "ovis": [n]}.
questions_for_owner: anything unclear (for example who speaks, or whether two names are one person).
Output JSON only, no other text: {"characters": [], "places": [], "named_only": [], "questions_for_owner": []}"""


def load_ovis(adhyay: int) -> list[dict]:
    path = ROOT / "canon" / "source_hj" / f"adhyay_{adhyay:02d}.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def extract_json(reply: str, kind: type):
    """The first JSON value of type `kind` (list or dict) in a model reply, after dropping <think> blocks and code fences."""
    text = re.sub(r"<think>.*?</think>", "", reply, flags=re.S)
    text = re.sub(r"```(?:json)?", "", text)
    dec = json.JSONDecoder()
    opener = "[" if kind is list else "{"
    i = text.find(opener)
    while i != -1:
        try:
            value, _ = dec.raw_decode(text, i)
            if isinstance(value, kind):
                return value
        except json.JSONDecodeError:
            pass
        i = text.find(opener, i + 1)
    raise ValueError("no JSON in reply")


def scrub_obj(value, keys: list[str]):
    """Scrub keys from every string AFTER JSON decoding (an escaped key like \\u006evapi- only becomes visible once parsed)."""
    if isinstance(value, str):
        return nt.scrub(value, keys)
    if isinstance(value, list):
        return [scrub_obj(v, keys) for v in value]
    if isinstance(value, dict):
        return {nt.scrub(str(k), keys): scrub_obj(v, keys) for k, v in value.items()}
    return value


def save(path: Path, text: str, keys: list[str]) -> None:
    path.write_text(nt.scrub(text, keys), encoding="utf-8")                # every file is scrubbed once more as written


def norm(s: str) -> str:
    return " ".join(s.split())


def check_names(entries: list, ovis: list[dict]) -> list[str]:
    """Problems: malformed entry, evidence ovi missing/out of range/not an integer, or a names_in_text spelling that appears in none of its cited ovis."""
    text = {o["ovi"]: norm(o["text"]) for o in ovis}
    problems = []
    for e in entries:
        if not isinstance(e, dict):
            problems.append(f"malformed entry: {str(e)[:80]}")
            continue
        ident = e.get("char_id") or e.get("place_id") or "?"
        cited = e.get("evidence_ovis")
        cited = cited if isinstance(cited, list) else []
        valid = [n for n in cited if isinstance(n, int) and not isinstance(n, bool) and n in text]
        bad = [n for n in cited if n not in valid]
        if bad or not cited:
            problems.append(f"{ident}: evidence ovis missing or out of range {bad}")
        cited = valid
        names = e.get("names_in_text")
        if not isinstance(names, list) or not names or not all(isinstance(n, str) and n.strip() for n in names):
            problems.append(f"{ident}: names_in_text missing or not non-empty strings")
            continue
        for name in names:
            if not any(norm(name) in text[n] for n in cited):
                problems.append(f"{ident}: name '{name}' not found in its cited ovis {cited}")
    return problems


STREAM_TOTAL_S = 1200                                              # hard cap for one streamed call; a socket idle for 120 s also ends it


USAGE_FIELDS = ("prompt_tokens", "completion_tokens", "total_tokens")
MAX_SSE_BYTES = 8_000_000


def _stream_once(key: str, body: dict) -> tuple[int, str, dict]:
    """One streamed request: (status, content, extra). Only the fixed NVIDIA URL, no redirects (nt._OPENER). Success needs HTTP 200, a finish_reason of "stop" and non-blank content: a stream that ends
    early, is cut by the token limit, or runs past the deadline is a failure. A transport problem becomes (0, '', {'error': <ExceptionType>})."""
    req = urllib.request.Request(URL, data=json.dumps(body).encode("utf-8"), method="POST",
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json", "Accept": "text/event-stream"})
    parts, usage, finish, buf, total, deadline = [], None, None, b"", 0, time.monotonic() + STREAM_TOTAL_S
    try:
        with nt._OPENER.open(req, timeout=120) as resp:                  # the timeout is per socket read (idle timeout); the deadline below also covers a trickle of bytes
            while True:
                piece = resp.read1(8192)                                  # one network read at a time, so the deadline is checked after every chunk even if bytes trickle in
                if time.monotonic() > deadline:
                    return 0, "", {"error": "deadline"}
                if not piece:
                    break
                total += len(piece)
                buf += piece
                if total > MAX_SSE_BYTES or len(buf) > 1_000_000:
                    return 0, "", {"error": "stream too large"}
                while b"\n" in buf:
                    raw_line, buf = buf.split(b"\n", 1)
                    line = raw_line.decode("utf-8", "replace").strip()
                    if not line.startswith("data:") or line == "data: [DONE]":
                        continue
                    try:
                        chunk = json.loads(line[5:])
                    except ValueError:
                        continue
                    if not isinstance(chunk, dict):
                        continue
                    if isinstance(chunk.get("usage"), dict):
                        usage = chunk["usage"]
                    choices = chunk.get("choices")
                    for ch in choices if isinstance(choices, list) else []:
                        if isinstance(ch, dict):
                            delta = ch.get("delta") if isinstance(ch.get("delta"), dict) else {}
                            if isinstance(delta.get("content"), str):
                                parts.append(delta["content"])
                            if isinstance(ch.get("finish_reason"), str):
                                finish = ch["finish_reason"]
            status = resp.status
    except urllib.error.HTTPError as exc:
        return exc.code, "", {"error": f"HTTP {exc.code}"}
    except (urllib.error.URLError, http.client.HTTPException, OSError, ValueError) as exc:
        return 0, "", {"error": type(exc).__name__}
    content = "".join(parts)
    extra = {"finish": finish if finish in ("stop", "length", "content_filter", "tool_calls") else ("none" if finish is None else "other"),
             "usage": {k: usage[k] for k in USAGE_FIELDS if isinstance(usage, dict) and isinstance(usage.get(k), int)} or None}
    if status == 200 and (finish != "stop" or not content.strip()):
        return 0, "", {**extra, "error": f"incomplete stream (finish={extra['finish']})"}
    return status, content, extra


def chat_stream(pool: nt.KeyPool, keys: list[str], model: str, system: str, user: str, max_tokens: int = 40000) -> tuple[str, dict]:
    """Like chat() but streamed, so the gateway's ~300 s cut for non-streamed calls does not apply. Same key pool rules: 401/402/403 retire a key, 429 cools it for 60 s and the call moves on."""
    body = {"model": model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}], "temperature": 0.2, "max_tokens": max_tokens, "stream": True}
    t0, status, content, extra = time.time(), 0, "", {"error": "no key"}
    for _ in range(3 * len(pool.keys) + 5):
        try:
            index, key = pool.acquire()
        except nt.AllKeysUnavailable:
            break
        status, content, extra = _stream_once(key, body)
        pool.report(index, status)
        if status in nt.REJECTED or status == 429:
            continue
        break
    info = {"model": model, "status": status, "wall_s": round(time.time() - t0, 1), "streamed": True}
    if status != 200 or not content:
        info["error"] = nt.scrub(str(extra.get("error", "empty reply")), keys)
        info["finish"] = extra.get("finish")
        return "", info
    info.update(finish=extra.get("finish"), usage=extra.get("usage"))
    return nt.scrub(content, keys), info


def chat(pool: nt.KeyPool, keys: list[str], model: str, system: str, user: str) -> tuple[str, dict]:
    body = {"model": model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}], "temperature": 0.2, "max_tokens": 16000}
    t0 = time.time()
    status, resp, _ = nt.call({"url": URL}, body, pool, post=lambda u, k, b: nt.http_post(u, k, b, timeout=320))
    info = {"model": model, "status": status, "wall_s": round(time.time() - t0, 1)}
    try:
        choice = resp["choices"][0]
        content = choice["message"].get("content") or ""
        if status != 200 or not isinstance(content, str):
            raise TypeError
    except (TypeError, KeyError, IndexError, AttributeError):
        info["error"] = nt.scrub(str(resp)[:200], keys)
        return "", info
    info["finish"] = str(choice.get("finish_reason"))
    usage = resp.get("usage")
    info["usage"] = {k: v for k, v in usage.items() if isinstance(v, int)} if isinstance(usage, dict) else None
    return nt.scrub(content, keys), info


def ovi_lines(ovis: list[dict]) -> str:
    return "\n".join(f"{o['ovi']}: {o['text']}" for o in ovis)


def clean_row(r: dict) -> dict | None:
    """Only the allowed fields, type-checked; None if the meaning is missing. Model-supplied fields such as "approved" are dropped."""
    meaning = r.get("meaning_en")
    if not isinstance(meaning, str) or not meaning.strip():
        return None
    speaker = r.get("speaker")
    return {"ovi": r["ovi"], "meaning_en": meaning.strip(), "speaker": speaker if isinstance(speaker, str) and speaker.strip() else None,
            "unclear": r.get("unclear") is True, "note": r.get("note") if isinstance(r.get("note"), str) else ""}


CHAR_FIELDS = ("char_id", "names_in_text", "name_en", "role", "description", "evidence_ovis")
PLACE_FIELDS = ("place_id", "names_in_text", "name_en", "description", "evidence_ovis")


def clean_chars(parsed: dict) -> dict:
    """Allowlisted fields only (a model-supplied "approved"/"status" is dropped); a collection that is not a list of objects raises ValueError."""
    out = {}
    for key, fields in (("characters", CHAR_FIELDS), ("places", PLACE_FIELDS)):
        items = parsed.get(key)
        if not isinstance(items, list) or not all(isinstance(e, dict) for e in items):
            raise ValueError(f"'{key}' is not a list of objects")
        out[key] = [{f: e.get(f) for f in fields} for e in items]
    if not out["characters"]:
        raise ValueError("no characters")
    for key in ("named_only", "questions_for_owner"):
        items = parsed.get(key, [])
        if not isinstance(items, list):
            raise ValueError(f"'{key}' is not a list")
        out[key] = items
    return out


def clean_problems(found):
    """A list of {"id","problem","ovis"} objects (possibly empty = the check found nothing); anything malformed is "NO_CHECK", never an empty list."""
    if not isinstance(found, list) or not all(isinstance(p, dict) and isinstance(p.get("problem"), str) and p["problem"].strip() for p in found):
        return "NO_CHECK"
    return [{"id": str(p.get("id", "")), "problem": p["problem"].strip(), "ovis": [n for n in p.get("ovis") or [] if isinstance(n, int) and not isinstance(n, bool)] if isinstance(p.get("ovis"), list) else []} for p in found]


def load_done(path: Path, a, ovis: list[dict]) -> dict:
    """Valid checked rows from earlier runs, from ANY drafter/checker pair (the pair is kept in each row and shown in the review file); failed and unchecked rows are redone. Malformed lines are skipped."""
    done, valid = {}, {o["ovi"] for o in ovis}
    if not path.is_file():
        return done
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
            row = clean_row(r)
            if (row and r.get("ovi") in valid and r.get("status") == "DRAFT" and isinstance(r.get("drafter"), str) and isinstance(r.get("checker"), str) and r["drafter"] != r["checker"]
                    and r.get("check") in ("OK", "ISSUE") and isinstance(r.get("check_note", ""), str)):
                done[r["ovi"]] = {**row, "drafter": r["drafter"], "checker": r["checker"], "check": r["check"], "check_note": r.get("check_note", ""), "status": "DRAFT"}
        except (ValueError, TypeError, AttributeError):
            continue
    return done


def run_batch(pool, keys, a, ovis, start) -> tuple[list[dict], list[dict]]:
    batch = ovis[start:start + BATCH]
    want = [o["ovi"] for o in batch]
    log = []
    try:
        user = f"CONTEXT:\n{ovi_lines(ovis[max(0, start - CONTEXT):start]) or '(none)'}\n\nTRANSLATE:\n{ovi_lines(batch)}"
        rows = None
        for _ in range(2):                                         # one retry on a bad or incomplete reply
            reply, info = chat(pool, keys, a.drafter, MEANING_SYS, user)
            log.append({"step": "draft", "ovis": [want[0], want[-1]], **info})
            try:
                got = {r["ovi"]: clean_row(r) for r in extract_json(reply, list) if isinstance(r, dict) and r.get("ovi") in want}
            except ValueError:
                continue
            if sorted(got) == want and all(got.values()):
                rows = [scrub_obj(got[n], keys) for n in want]
                break
        if rows is None:
            raise ValueError("no complete draft after 2 tries")
        check_user = (f"CONTEXT:\n{ovi_lines(ovis[max(0, start - CONTEXT):start]) or '(none)'}\n\nCHECK:\n"
                      + "\n\n".join(f"{o['ovi']}: {o['text']}\nMEANING: {r['meaning_en']}\nSPEAKER: {r['speaker']}" for o, r in zip(batch, rows)))
        reply, info = chat(pool, keys, a.checker, CHECK_SYS, check_user)
        log.append({"step": "check", "ovis": [want[0], want[-1]], **info})
        try:
            checks = {c.get("ovi"): c for c in extract_json(reply, list) if isinstance(c, dict)}
        except ValueError:
            checks = {}
        for r in rows:
            c = checks.get(r["ovi"], {})
            verdict = c.get("verdict") if c.get("verdict") in ("OK", "ISSUE") else "NO_CHECK"
            note = c.get("note") if isinstance(c.get("note"), str) else ""
            r.update(drafter=a.drafter, checker=a.checker, check=verdict, check_note=nt.scrub(note, keys), status="DRAFT")
        return rows, log
    except Exception as exc:                                       # a failed batch is recorded, never fatal: the other batches and the receipt are kept
        log.append({"step": "batch_failed", "ovis": [want[0], want[-1]], "error": type(exc).__name__ + ": " + nt.scrub(str(exc), keys)[:120]})
        return [{"ovi": n, "meaning_en": None, "status": "DRAFT_FAILED", "check": "NOT_CHECKED"} for n in want], log


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--adhyay", type=int, required=True)
    ap.add_argument("--drafter", default="deepseek-ai/deepseek-v4.1-flash")
    ap.add_argument("--checker", default="z-ai/glm-5.3")
    ap.add_argument("--only", choices=["meanings", "characters"])
    ap.add_argument("--char-range", help="A-B: send only these ovis to the characters step (shorter input, less thinking); evidence ovis are still checked against the whole Adhyay")
    ap.add_argument("--char-writer", help="model that drafts the characters list (default: --drafter); the whole Adhyay goes in one call, so pick a fast model")
    ap.add_argument("--char-checker", help="model that checks the characters list (default: --checker); must differ from the char writer")
    a = ap.parse_args()
    keys = nt.load_keys()
    if not keys:
        raise SystemExit("no usable NVIDIA key")
    pool = nt.KeyPool(keys)
    if a.drafter == a.checker:
        raise SystemExit("the meanings drafter and checker must be different models")
    char_writer, char_checker = a.char_writer or a.drafter, a.char_checker or a.checker
    if char_writer == char_checker:
        raise SystemExit("the characters writer and checker must be different models")
    ovis = load_ovis(a.adhyay)
    char_ovis = ovis
    if a.char_range:
        lo, hi = (int(x) for x in a.char_range.split("-"))
        char_ovis = [o for o in ovis if lo <= o["ovi"] <= hi]
        if not char_ovis:
            raise SystemExit("--char-range selects no ovis")
    out = ROOT / "canon" / "drafts"
    out.mkdir(parents=True, exist_ok=True)
    stem = out / f"a{a.adhyay:02d}"
    receipt = {"adhyay": a.adhyay, "status": "DRAFT, not approved", "drafter": a.drafter, "checker": a.checker, "calls": []}
    meanings, chars = [], None

    if a.only != "characters":
        partial = stem.with_name(stem.name + "_meanings_PARTIAL.jsonl")      # rows of every finished batch; a restart resumes from it instead of redoing them
        done = load_done(partial, a, ovis)
        starts = [s for s in range(0, len(ovis), BATCH) if not all(o["ovi"] in done for o in ovis[s:s + BATCH])]
        meanings += [done[o["ovi"]] for s in range(0, len(ovis), BATCH) if s not in starts for o in ovis[s:s + BATCH]]
        print(f"resuming: {len(meanings)} meanings already done, {len(starts)} batches to run", flush=True)
        with ThreadPoolExecutor(max_workers=len(keys)) as ex:
            for fut in as_completed([ex.submit(run_batch, pool, keys, a, ovis, s) for s in starts]):
                rows, log = fut.result()
                meanings += rows
                receipt["calls"] += log
                with partial.open("a", encoding="utf-8") as f:
                    f.write(nt.scrub("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), keys))
        meanings.sort(key=lambda r: r["ovi"])
        save(stem.with_name(stem.name + "_meanings_DRAFT.jsonl"), "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in meanings), keys)

    if a.only == "characters":                                          # keep the meanings table in the review file
        meanings = sorted(load_done(stem.with_name(stem.name + "_meanings_PARTIAL.jsonl"), a, ovis).values(), key=lambda r: r["ovi"])

    if a.only != "meanings":
        reply, info = chat_stream(pool, keys, char_writer, CHAR_SYS, ovi_lines(char_ovis))
        receipt["calls"].append({"step": "characters", **info})
        try:
            chars = clean_chars(scrub_obj(extract_json(reply, dict), keys))
            chars["name_check"] = check_names(chars["characters"] + chars["places"], ovis)
            reply2, info2 = chat_stream(pool, keys, char_checker, CHARCHECK_SYS, ovi_lines(char_ovis) + "\n\nDRAFT LIST:\n" + json.dumps({k: chars[k] for k in ("characters", "places")}, ensure_ascii=False))
            receipt["calls"].append({"step": "characters_check", **info2})
            try:
                chars["model_check"] = clean_problems(scrub_obj(extract_json(reply2, dict), keys).get("problems"))
            except ValueError:
                chars["model_check"] = "NO_CHECK"
        except ValueError as exc:
            chars = {"error": f"reply was not the expected JSON ({exc})", "raw": nt.scrub(reply[:4000], keys)}
        chars["status"] = "DRAFT, not approved"
        chars["written_by"], chars["checked_by"] = char_writer, char_checker
        save(stem.with_name(stem.name + "_characters_places_DRAFT.json"), json.dumps(chars, indent=2, ensure_ascii=False), keys)

    save(stem.with_name(stem.name + "_receipt.json"), json.dumps(receipt, indent=2, ensure_ascii=False), keys)
    save(stem.with_name(stem.name + "_REVIEW.md"), review_text(a, ovis, meanings, chars), keys)
    failed = sum(1 for r in meanings if r.get("status") != "DRAFT")
    issues = sum(1 for r in meanings if r.get("check") == "ISSUE")
    print(f"meanings: {len(meanings)} rows, {failed} failed, {issues} flagged by the checker; characters: "
          + ("none" if chars is None else f"{len(chars.get('characters', []))} people, {len(chars.get('places', []))} places, {len(chars.get('name_check', []))} name-check problems"))
    return 1 if failed or (chars and "error" in chars) else 0


def review_text(a, ovis, meanings, chars) -> str:
    by = {r["ovi"]: r for r in meanings}
    cell = lambda s: str(s or "").replace("|", "/").replace("\n", " ")
    lines = [f"# Adhyay {a.adhyay}: DRAFT meanings and characters (owner review; nothing here is approved)", "",
             "Each row names the model that drafted it and the model that checked it. Marathi from hindujagruti.org (to be checked against the printed PDF).", ""]
    if meanings:
        lines += ["## Meanings", "", "| Ovi | Marathi | Draft meaning | Speaker | Check |", "|---|---|---|---|---|"]
        for o in ovis:
            r = by.get(o["ovi"], {})
            if r.get("status") != "DRAFT":
                status = f"**{r.get('status', 'MISSING')}**"
            elif r.get("check") == "ISSUE":
                status = f"**ISSUE:** {r.get('check_note')}"
            else:
                status = r.get("check", "NO_CHECK")
            if r.get("note"):
                status += f" (drafter note: {r['note']})"
            if r.get("drafter"):
                status += f" [drafted by {r['drafter'].split('/')[-1]}, checked by {r['checker'].split('/')[-1]}]"
            lines.append(f"| {o['ovi']} | {cell(o['text'])} | {cell(r.get('meaning_en'))}{' (unclear)' if r.get('unclear') else ''} | {cell(r.get('speaker'))} | {cell(status)} |")
    if chars:
        lines += ["", "## Characters and places", "", "```json", json.dumps(chars, indent=2, ensure_ascii=False), "```"]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    sys.exit(main())
```

## CURRENT scripts/source/nemotron_code.py
```python
"""Nemotron drafts code (owner rule 2026-10-27, docs/pilot/PIPELINE_README.md section 6).

  python scripts/source/nemotron_code.py --spec SPEC.md --out SCRATCH_DIR

The spec says what to write and names the tests it must pass. Nemotron (free NVIDIA pool) replies with files; this tool writes ONLY those that pass the path
rules into SCRATCH_DIR. Claude then reads every line, runs the tests and moves the files into the repository: nothing is written into the repository here.
Refused: paths outside the scratch folder, secrets, Blender/animation code (D-017), anything but .py/.json/.md. API keys are read from the usual place at run time."""
from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = "nvidia/nemotron-3-ultra-550b-a55b"
ALLOWED = {".py", ".json", ".md"}
FORBIDDEN_PART = {"secrets", ".git", ".claude", ".codex"}
FORBIDDEN_TEXT = re.compile(r"\bimport\s+bpy\b|\bfrom\s+bpy\b|\bbpy\.|\bbmesh\b|\bmathutils\b|blender", re.I)       # no model writes Blender/animation code
SYSTEM = ("You write small, plain Python 3.12 modules for the GranthStudio pipeline. Follow the spec exactly and make the given tests pass; the tests are frozen and you must not change them. Use only the standard library plus pyyaml and jsonschema. "
          "No network, no file writes outside what the spec names. Never access secrets/. Never edit the owner's EASY script or any existing Adhyay 1 artifact. Never write animation or Blender code. "
          "Rules of the pipeline: Kimi outputs contain no timings, dialogue or claims; Stage 2 selects existing catalog image ids only; Stage 1 effort is HIGH and Stage 2 LOW; tests use synthetic data and tmp files only. "
          "The spec lists every schema or API it relies on; do not assume anything it does not state. Reply with files only, each as:\nFILE: relative/path.py\n```python\n<complete file>\n```\n"
          "No other prose.")
BLOCK = re.compile(r"^FILE:\s*(\S+)\s*\n```[a-zA-Z]*\n(.*?)\n```", re.S | re.M)


def check_path(rel: str) -> str | None:
    """None if the path is acceptable inside the scratch folder, else the reason."""
    p = Path(rel)
    if p.is_absolute() or rel.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", rel):
        return "absolute path"
    if ".." in p.parts:
        return "parent folder"
    if FORBIDDEN_PART & {x.lower() for x in p.parts}:
        return "forbidden folder"
    if p.suffix.lower() not in ALLOWED:
        return f"extension {p.suffix!r} not allowed"
    return None


def parse_files(reply: str) -> tuple[dict, list]:
    """({relative path: text} accepted, [(path, reason)] refused)."""
    ok, refused = {}, []
    for rel, body in BLOCK.findall(reply or ""):
        why = check_path(rel) or ("Blender/animation code (D-017)" if FORBIDDEN_TEXT.search(body) else None)
        if why:
            refused.append((rel, why))
        elif rel in ok:
            refused.append((rel, "duplicate"))
        else:
            ok[rel] = body.rstrip("\n") + "\n"
    return ok, refused


def check_spec(path: Path) -> str | None:
    """None if the spec file may be sent to the model: a small .md/.txt file that is not under a forbidden folder."""
    p = Path(path).resolve()
    if FORBIDDEN_PART & {x.lower() for x in p.parts}:
        return "spec under a forbidden folder"
    if p.suffix.lower() not in {".md", ".txt"}:
        return "spec must be a .md or .txt file"
    if not p.is_file() or p.stat().st_size > 200_000:
        return "spec missing or larger than 200 KB"
    return None


def check_out(path: Path, roots: list) -> str | None:
    """None if the scratch folder is NEW and lies inside one of the allowed roots, but not inside the repository's tracked source folders."""
    p = Path(path).resolve()
    if p.exists():
        return "scratch folder exists"
    if FORBIDDEN_PART & {x.lower() for x in p.parts}:
        return "scratch folder under a forbidden folder"
    if not any(Path(r).resolve() in p.parents for r in roots):
        return "scratch folder outside the allowed roots"
    return None


def exact_set(files: dict, refused: list, expected: list) -> str | None:
    """None only if the reply holds exactly the expected files and nothing was refused (a partial or surprising reply is never written)."""
    if refused:
        return f"{len(refused)} block(s) refused"
    if set(files) != set(expected):
        return f"reply has {sorted(files)}, expected {sorted(expected)}"
    return None


def write_scratch(files: dict, out: Path) -> list[Path]:
    out = out.resolve()
    written = []
    for rel, text in files.items():
        dest = (out / rel).resolve()
        if out not in dest.parents:
            raise ValueError(f"{rel} escapes the scratch folder")
        if dest.exists():
            raise FileExistsError(f"{dest} exists; draft into a new folder")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        written.append(dest)
    return written


def _ds():
    spec = importlib.util.spec_from_file_location("ds", ROOT / "scripts" / "source" / "draft_source.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("ds", mod)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path, help="NEW scratch folder (must not exist)")
    ap.add_argument("--expect", required=True, help="comma-separated relative paths the reply must contain, exactly")
    ap.add_argument("--allow-root", action="append", default=[], help="folder the scratch folder may live in (default: the system temp folder)")
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--max-tokens", type=int, default=20000)
    a = ap.parse_args()
    import tempfile
    why = check_spec(a.spec) or check_out(a.out, a.allow_root or [tempfile.gettempdir()])
    if why:
        raise SystemExit(f"refused before any call: {why}")
    expected = [x.strip() for x in a.expect.split(",") if x.strip()]
    ds = _ds()
    nt = ds.nt
    keys = nt.load_keys()
    pool = nt.KeyPool(keys)
    reply, info = ds.chat_stream(pool, keys, a.model, SYSTEM, a.spec.read_text(encoding="utf-8"), max_tokens=a.max_tokens)
    reply = nt.scrub(reply or "", keys)
    print({k: info.get(k) for k in ("status", "wall_s", "finish", "error")})
    files, refused = parse_files(reply)
    for rel, why in refused:
        print("REFUSED", rel, why)
    why = exact_set(files, refused, expected)
    if why:
        a.out.mkdir(parents=True)
        (a.out / "RAW_REPLY.txt").write_text(reply, encoding="utf-8")
        print("nothing drafted:", why, "| raw reply saved in", a.out)
        return 1
    for p in write_scratch(files, a.out):
        print("drafted", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
