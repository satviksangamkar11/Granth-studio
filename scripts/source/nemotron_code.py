"""Nemotron drafts code (owner rule 2026-10-27, docs/pilot/PIPELINE_README.md section 6).

  python scripts/source/nemotron_code.py --spec SPEC.md --out SCRATCH_DIR

The spec says what to write and names the tests it must pass. Nemotron (free NVIDIA pool) replies with files; this tool writes ONLY those that pass the path
rules into SCRATCH_DIR. Claude then reads every line, runs the tests and moves the files into the repository: nothing is written into the repository here.
Refused: paths outside the scratch folder, secrets, the protected policy file, anything matching config/codegen_policy.json, anything but .py/.json/.md; specs only from the approved spec root; never into repository code folders; unfinished FILE blocks refused. API keys are read from the usual place at run time."""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = "nvidia/nemotron-3-ultra-550b-a55b"
ALLOWED = {".py", ".json", ".md"}
FORBIDDEN_PART = {"secrets", ".git", ".claude", ".codex"}
CODE_DIRS = {"scripts", "src", "tests", "schemas"}
SPEC_ROOTS = [ROOT / "docs" / "pilot" / "nemotron_specs"]
POLICY_PATH = ROOT / "config" / "codegen_policy.json"
BLOCK = re.compile(r"^FILE:\s*(\S+)\s*\n```[a-zA-Z]*\n(.*?)\n```", re.S | re.M)
FILE_HEADER = re.compile(r"^FILE:\s*(\S+)", re.M)


def load_policy(path: Path | None = None) -> dict:
    """Load and validate the policy file. Raise ValueError on any problem."""
    p = path or POLICY_PATH
    try:
        try:
            text = p.read_text(encoding="utf-8")
        except FileNotFoundError as e:
            raise ValueError("policy file not found") from e
        except (OSError, UnicodeDecodeError) as e:
            raise ValueError(f"policy file unreadable: {e}") from e
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"policy file is not valid JSON: {e}") from e

        if not isinstance(data, dict):
            raise ValueError("policy file must be a JSON object")

        version = data.get("version")
        if not (type(version) is int and version == 1):
            raise ValueError(f"policy version must be the integer 1, got {version!r}")

        ft = data.get("forbidden_text")
        if not isinstance(ft, dict):
            raise ValueError("policy missing 'forbidden_text' object")

        required = {
            "pattern": str,
            "refusal_reason": str,
            "system_rule": str,
            "ignore_case": bool,
            "refused_examples": list,
        }
        for key, typ in required.items():
            if key not in ft:
                raise ValueError(f"policy forbidden_text missing key: {key}")
            if not isinstance(ft[key], typ):
                raise ValueError(f"policy forbidden_text.{key} must be {typ.__name__}")

        if not ft["pattern"]:
            raise ValueError("policy forbidden_text.pattern must be non-empty string")
        if not ft["refusal_reason"]:
            raise ValueError("policy forbidden_text.refusal_reason must be non-empty string")
        if not ft["system_rule"]:
            raise ValueError("policy forbidden_text.system_rule must be non-empty string")
        if not ft["refused_examples"]:
            raise ValueError("policy forbidden_text.refused_examples must be non-empty list")
        if not all(isinstance(x, str) for x in ft["refused_examples"]):
            raise ValueError("policy forbidden_text.refused_examples must be list of strings")

        try:
            flags = re.IGNORECASE if ft["ignore_case"] else 0
            compiled = re.compile(ft["pattern"], flags)
        except re.error as e:
            raise ValueError(f"policy forbidden_text.pattern does not compile: {e}") from e

        return {
            "pattern": compiled,
            "reason": ft["refusal_reason"],
            "rule": ft["system_rule"],
            "examples": ft["refused_examples"],
        }
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"policy unusable: {type(e).__name__}: {e}") from e


try:
    POLICY = load_policy()
    POLICY_ERROR = None
except Exception as e:
    POLICY = None
    POLICY_ERROR = str(e)

SYSTEM = (
    "You write small, plain Python 3.12 modules for the GranthStudio pipeline. Follow the spec exactly and make the given tests pass; the tests are frozen and you must not change them. Use only the standard library plus pyyaml and jsonschema. "
    "No network, no file writes outside what the spec names. Never access secrets/. Never edit the owner's EASY script or any existing Adhyay 1 artifact. "
    + (POLICY["rule"] if POLICY else "Follow config/codegen_policy.json.")
    + " "
    "Rules of the pipeline: Kimi outputs contain no timings, dialogue or claims; Stage 2 selects existing catalog image ids only; Stage 1 effort is HIGH and Stage 2 LOW; tests use synthetic data and tmp files only. "
    "The spec lists every schema or API it relies on; do not assume anything it does not state. Reply with files only, each as:\nFILE: relative/path.py\n```python\n<complete file>\n```\n"
    "No other prose."
)


def check_path(rel: str) -> str | None:
    """None if the path is acceptable inside the scratch folder, else the reason."""
    p = Path(rel)
    if p.is_absolute() or rel.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", rel):
        return "absolute path"
    if ".." in p.parts:
        return "parent folder"
    norm = "/".join(x for x in Path(rel.replace("\\", "/")).parts if x not in ("", ".")).lower()
    if norm == "config/codegen_policy.json":
        return "protected policy file"
    if FORBIDDEN_PART & {x.lower() for x in p.parts}:
        return "forbidden folder"
    if p.suffix.lower() not in ALLOWED:
        return f"extension {p.suffix!r} not allowed"
    return None


def parse_files(reply: str, policy: dict | None = None) -> tuple[dict, list]:
    """({relative path: text} accepted, [(path, reason)] refused)."""
    pol = policy if policy is not None else POLICY
    ok, refused = [], []
    seen_paths = set()

    if pol is None:
        for rel, _ in BLOCK.findall(reply or ""):
            if rel not in seen_paths:
                refused.append((rel, f"policy unavailable: {POLICY_ERROR}"))
                seen_paths.add(rel)
        for rel in FILE_HEADER.findall(reply or ""):
            if rel not in seen_paths:
                refused.append((rel, f"policy unavailable: {POLICY_ERROR}"))
                seen_paths.add(rel)
        return {}, refused

    blocks = list(BLOCK.findall(reply or ""))
    headers = FILE_HEADER.findall(reply or "")

    # Count complete blocks per path
    complete_counts = {}
    for rel, _ in blocks:
        complete_counts[rel] = complete_counts.get(rel, 0) + 1

    # Count headers per path
    header_counts = {}
    for rel in headers:
        header_counts[rel] = header_counts.get(rel, 0) + 1

    for rel, body in blocks:
        why = check_path(rel) or (pol["reason"] if pol["pattern"].search(body) else None)
        if why:
            refused.append((rel, why))
        elif rel in seen_paths:
            refused.append((rel, "duplicate"))
        else:
            ok.append((rel, body.rstrip("\n") + "\n"))
            seen_paths.add(rel)

    # For each path, refuse unfinished blocks: headers beyond complete blocks
    for rel, hcount in header_counts.items():
        ccount = complete_counts.get(rel, 0)
        for _ in range(hcount - ccount):
            refused.append((rel, "unfinished block"))

    return dict(ok), refused


def check_spec(path: Path, roots: list[Path] | None = None) -> str | None:
    """None if the spec file may be sent to the model: a small .md/.txt file that is not under a forbidden folder and lies inside an approved spec root."""
    p = Path(path).resolve()
    if FORBIDDEN_PART & {x.lower() for x in p.parts}:
        return "spec under a forbidden folder"
    if p.suffix.lower() not in {".md", ".txt"}:
        return "spec must be a .md or .txt file"
    if not p.is_file() or p.stat().st_size > 200_000:
        return "spec missing or larger than 200 KB"
    rts = roots if roots is not None else SPEC_ROOTS
    resolved_roots = [Path(r).resolve() for r in rts]
    if not any(p.is_relative_to(r) for r in resolved_roots):
        return "spec outside the approved spec root"
    return None


def check_out(path: Path, roots: list, repo_root: Path | None = None) -> str | None:
    """None if the scratch folder is NEW and lies inside one of the allowed roots, but not inside the repository's tracked source folders."""
    p = Path(path).resolve()
    rr = (repo_root or ROOT).resolve()
    for d in CODE_DIRS:
        code_dir = (rr / d).resolve()
        if p == code_dir or code_dir in p.parents:
            return "scratch folder inside a repository code folder"
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
    ap.add_argument("--spec-root", action="append", default=[], help="approved spec root (default: docs/pilot/nemotron_specs)")
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--max-tokens", type=int, default=20000)
    a = ap.parse_args()
    import tempfile
    spec_roots = [Path(r) for r in a.spec_root] if a.spec_root else SPEC_ROOTS
    why = check_spec(a.spec, spec_roots) or check_out(a.out, a.allow_root or [tempfile.gettempdir()], ROOT)
    if why:
        raise SystemExit(f"refused before any call: {why}")
    if POLICY is None:
        raise SystemExit(f"refused before any call: policy unavailable: {POLICY_ERROR}")
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
