"""Run folders, shot-id mapping and the ONE film manifest for the director (Phase 1 items h, i, j).
- Run folder canon/director_runs/<name>/: every file is write-once, listed with its sha256 in receipt.json; resume verifies each finished file by hash and refuses a changed input.
- map_shot_ids: director ids (S1-1) -> the frozen builder's single-letter ids (^S[A-Z]$) in batches of 26; deterministic, the builder is not touched.
- Film manifest: chapter-qualified sources, canon, plans and assets as hashed items with dependencies; owner approvals are SEPARATE records per kind and go STALE
  when any input (or anything it depends on) changes. Only the owner approves; no code here approves anything by itself."""
from __future__ import annotations

import msvcrt
import os
import re
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from granthstudio import integrity as ig  # noqa: E402  (shared hashing and crash-safe writes)

sha256_file = ig.sha256_file
NAME = re.compile(r"^[A-Za-z0-9_.-]{1,60}$")
APPROVAL_KINDS = ("source", "story_split", "narration", "storyboard", "images", "film")


class RunError(Exception):
    pass


class Run:
    def __init__(self, path: Path):
        self.path = Path(path)
        self._lock = threading.Lock()                       # reviewers and recorders write from several threads
        self._proc = None                                   # the run.lock handle: ONE process at a time may use a run (a crash releases it)

    def acquire(self):
        f = open(self.path / "run.lock", "a+b")
        try:
            f.seek(0)
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            f.close()
            raise RunError("another process is using this run (run.lock is held); two processes may never work on one run")
        self._proc = f

    def release(self):
        if self._proc:
            try:
                self._proc.seek(0)
                msvcrt.locking(self._proc.fileno(), msvcrt.LK_UNLCK, 1)
            except OSError:
                pass
            self._proc.close()
            self._proc = None

    @property
    def receipt(self) -> dict:
        return ig.read_json(self.path / "receipt.json")

    def _save(self, receipt: dict):
        ig.atomic_write_json(self.path / "receipt.json", receipt)

    def has(self, rel: str) -> bool:
        """True only for a finished file whose hash matches the receipt. A file that is on disk but unlisted or changed is an error, never silently reused or overwritten."""
        p = self.path / rel
        listed = self.receipt["files"].get(rel)
        if not p.exists():
            if listed:
                raise RunError(f"{rel} is listed in the receipt but missing")
            return False
        if listed != ig.sha256_file(p):
            raise RunError(f"{rel} does not match the receipt (changed or unlisted)")
        return True

    def write_once(self, rel: str, text: str):
        p = self.path / rel
        with self._lock:
            if p.exists():
                raise RunError(f"{rel} already exists; run files are never overwritten")
            data = text.encode("utf-8")
            ig.atomic_write_bytes(p, data)                  # creates the parent folder (calls/)
            r = self.receipt
            r["files"][rel] = ig.sha256_bytes(data)
            self._save(r)

    def read_json(self, rel: str):
        if not self.has(rel):
            raise RunError(f"{rel} not in this run")
        return ig.read_json(self.path / rel)

    def finish(self, extra: dict):
        with self._lock:
            r = self.receipt
            r.update(extra)
            r["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
            self._save(r)


def open_run(runs_dir: Path, name: str, inputs: dict, resume: bool = False) -> Run:
    if not NAME.match(name):
        raise RunError("run name: letters, digits, _ . - only (max 60)")
    path = Path(runs_dir) / name
    if path.exists():
        if not resume:
            raise RunError(f"run {name} already exists; runs are immutable (use --resume to continue it, or a new name)")
        run = Run(path)
        run.acquire()
        try:
            if run.receipt["inputs"] != inputs:
                raise RunError("the inputs, prompts or models changed since this run started; start a new run")
        except BaseException:
            run.release()
            raise
        return run
    if resume:
        raise RunError(f"run {name} does not exist")
    path.mkdir(parents=True)
    run = Run(path)
    run.acquire()
    try:
        run._save({"run": name, "created": time.strftime("%Y-%m-%d %H:%M:%S"), "inputs": inputs, "files": {}, "status": "STARTED"})
    except BaseException:
        run.release()
        raise
    return run


def directed_elsewhere(runs_dir: Path, current: str, director: str, scenes: list) -> list:
    """Scenes this director already directed in ANOTHER run ('one directing pass per Adhyay')."""
    found = []
    for d in sorted(Path(runs_dir).glob("*/receipt.json")):
        if d.parent.name == current:
            continue
        try:
            r = ig.read_json(d)
        except (OSError, ValueError):
            continue
        if r.get("inputs", {}).get("director") == director:
            safe = re.sub(r"[^A-Za-z0-9.-]", "_", director)[-40:]
            files = r.get("files", {})
            found += [f"{d.parent.name}:scene{n}" for n in scenes if f"a01_scene{n}.json" in files or any(f.startswith(f"calls/scene{n}__{safe}__") for f in files)]    # saved or even only attempted
    return found


def claim_scene(runs_dir: Path, director: str, n: int, run_name: str, redo: bool = False):
    """Interprocess claim, taken BEFORE any paid dispatch: one directing pass per scene per director across ALL runs (atomic create). The same run may continue its own claim."""
    d = Path(runs_dir) / "_claims"
    d.mkdir(parents=True, exist_ok=True)
    f = d / (re.sub(r"[^A-Za-z0-9.-]", "_", director)[-40:] + f"__scene{n}.claim")
    try:
        fd = os.open(f, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        if f.read_text(encoding="utf-8").strip() == run_name:
            return
        if not redo:
            raise RunError(f"scene {n} is already claimed by run {f.read_text(encoding='utf-8').strip()!r} for {director}; each scene is directed once per Adhyay (--redo only on the owner's word)")
        ig.atomic_write_bytes(f, run_name.encode("utf-8"))
        return
    with os.fdopen(fd, "w", encoding="utf-8") as h:
        h.write(run_name)


def map_shot_ids(shot_ids: list) -> dict:
    """S1-1 -> {'batch': 0, 'schema_id': 'SA'} ... in plan order, 26 shots per batch (the builder schema allows one letter). Deterministic; unique within a batch."""
    def key(s):
        m = re.fullmatch(r"S([0-9])-([0-9]{1,2})", s)
        if not m:
            raise ValueError(f"not a director shot id: {s!r}")
        return int(m[1]), int(m[2])
    ordered = sorted(set(shot_ids), key=key)
    if len(ordered) != len(shot_ids):
        raise ValueError("duplicate shot ids")
    return {s: {"batch": i // 26, "schema_id": "S" + chr(ord("A") + i % 26)} for i, s in enumerate(ordered)}


# ----------------------------------------------------------------------------- film manifest

def new_manifest(film: str) -> dict:
    return {"film": film, "items": {}, "deps": {}, "approvals": {}}


def set_item(m: dict, key: str, sha256: str, **meta):
    """key like 'source:A1:ovis', 'canon:A1:final_answers', 'plan:S1', 'asset:maharaj_seated_wide'. Re-setting a changed hash is what makes approvals STALE."""
    m["items"][key] = {"sha256": sha256, **meta}


def add_dep(m: dict, key: str, needs: list):
    m["deps"][key] = sorted(set(m["deps"].get(key, [])) | set(needs))


def _closure(m: dict, keys: list) -> list:
    seen, stack = set(), list(keys)
    while stack:
        k = stack.pop()
        if k not in seen:
            seen.add(k)
            stack += m["deps"].get(k, [])
    return sorted(seen)


def approve(m: dict, kind: str, subject: str, inputs: list, by: str):
    """Records the owner's approval of `subject` against the CURRENT hash of every input and everything those depend on (and which items that was)."""
    if kind not in APPROVAL_KINDS:
        raise ValueError(f"approval kind must be one of {APPROVAL_KINDS}")
    if not by.strip():
        raise ValueError("an approval needs the approver's name")
    keys = _closure(m, inputs)
    missing = [k for k in keys if k not in m["items"]]
    if missing:
        raise ValueError(f"unknown manifest items: {missing}")
    m["approvals"][f"{kind}:{subject}"] = {"by": by, "at": time.strftime("%Y-%m-%d %H:%M:%S"), "roots": sorted(inputs), "inputs": {k: m["items"][k]["sha256"] for k in keys}}


def approval_state(m: dict, kind: str, subject: str) -> str:
    """NONE | APPROVED | STALE (an input or dependency changed or disappeared, or the set of dependencies itself changed, since the owner approved)."""
    a = m["approvals"].get(f"{kind}:{subject}")
    if not a:
        return "NONE"
    same_set = _closure(m, a["roots"]) == sorted(a["inputs"])
    return "APPROVED" if same_set and all(m["items"].get(k, {}).get("sha256") == h for k, h in a["inputs"].items()) else "STALE"


def load_manifest(path: Path, film: str) -> dict:
    return ig.read_json(path) if Path(path).exists() else new_manifest(film)


def save_manifest(path: Path, m: dict):
    ig.atomic_write_json(path, m)


def update_manifest(path: Path, film: str, fn):
    """load -> fn(manifest) -> save as ONE transaction under an interprocess lock, so two runs can never overwrite each other's additions."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path.with_suffix(".lock"), "a+b") as f:
        for _ in range(300):
            try:
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                break
            except OSError:
                time.sleep(0.1)
        else:
            raise RunError("the film manifest is locked by another process")
        try:
            m = load_manifest(path, film)
            fn(m)
            save_manifest(path, m)
        finally:
            f.seek(0)
            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)


def set_packet_items(m: dict, packet_hashes: dict) -> list:
    """The packet files as manifest items (source: = the ovis, canon: = the owner's research); returns their keys."""
    keys = []
    for rel, h in packet_hashes.items():
        key = ("source:A1:" if rel.endswith(".jsonl") else "canon:A1:") + rel
        set_item(m, key, h, path=f"canon/packets/adhyay_01/{rel}")
        keys.append(key)
    return keys


def update_film_manifest(m: dict, packet_hashes: dict, plans: dict):
    """Chapter-qualified sources/canon (packet files), one plan per scene, one asset per declared image, with their dependencies. Approvals are never touched here:
    a changed hash simply makes the owner's earlier approval STALE."""
    src = set_packet_items(m, packet_hashes)
    for n, plan in plans.items():
        pk = f"plan:S{n}"
        set_item(m, pk, ig.sha256_obj(plan), chapter=plan["chapter"], ovi_range=plan["ovi_range"])
        add_dep(m, pk, src)
        for im in plan["images_needed"]:
            ak, sha, old = f"asset:{im['image_id']}", ig.sha256_obj(im["description"]), m["items"].get(f"asset:{im['image_id']}")
            if old and old["sha256"] != sha and set(old.get("scenes", [])) - {n}:
                raise ValueError(f"image {im['image_id']} is declared with different descriptions in scenes {sorted(set(old['scenes']) | {n})}; give it one description or two ids")
            mine = [u for u in im["used_in"]]
            kept = [u for u in (old or {}).get("used_in", []) if not u.startswith(f"S{n}-")]
            same = bool(old) and old["sha256"] == sha
            rebind = bool(old and ((old.get("rebind_needed") and old.get("file") is None) or (not same and old.get("file"))))              # stays set until the owner rebinds a file
            set_item(m, ak, sha, file=(old or {}).get("file") if same else None, rebind_needed=rebind, scenes=sorted(set((old or {}).get("scenes", [])) | {n}), used_in=sorted(set(kept + mine)))   # the owner's file binding survives
            add_dep(m, ak, [pk])
