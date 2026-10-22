"""Offline verification of a machine against config/ltx_098_pins.yaml.

Statuses (every check reports exactly one):
  PASS        the local artifact was inspected and equals the pin
  MISMATCH    the local artifact was inspected and differs from the pin
  MISSING     the artifact (file, repo, node class, link target) does not exist locally
  UNVERIFIED  nothing local was given to inspect, or the pin itself is unknown

PASS here means "local files and metadata match the expected values". It is never evidence that the model
runs: a configured expected value (config/models.yaml, the pins file) is not proof of execution, so the
models.yaml checks only compare configuration to pins and are labelled CONFIG. Exit code: 0 only when every
check is PASS; 1 if any MISSING/MISMATCH; 2 if the rest are UNVERIFIED. Standard library + PyYAML only.

Examples:
  python scripts/verify_ltx_pins.py --source comfyui=/kaggle/working/ComfyUI --models-dir /kaggle/working/ComfyUI \
      --workflow wf.json --node-inventory object_info.json --models-yaml config/models.yaml
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

PASS, MISMATCH, MISSING, UNVERIFIED = "PASS", "MISMATCH", "MISSING", "UNVERIFIED"
ROOT = Path(__file__).resolve().parents[1]


def result(name: str, status: str, detail: str = "", kind: str = "LOCAL") -> dict[str, str]:
    return {"check": name, "status": status, "kind": kind, "detail": detail}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 22), b""):
            digest.update(block)
    return digest.hexdigest()


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()  # noqa: S324 (git object id, not security)


def _git(repo: Path, *args: str) -> str | None:
    try:
        done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout.strip() if done.returncode == 0 else None


def check_sources(pins: dict[str, Any], given: dict[str, Path]) -> list[dict[str, str]]:
    out = []
    for name, pin in pins["sources"].items():
        label = f"source:{name}"
        if name not in given:
            out.append(result(label, UNVERIFIED, "no local checkout given (--source NAME=PATH)"))
            continue
        path = given[name]
        if not path.is_dir():
            out.append(result(label, MISSING, f"{path} is not a directory"))
            continue
        head = _git(path, "rev-parse", "HEAD")
        if head is None:
            out.append(result(label, UNVERIFIED, f"{path} is not a readable git checkout"))
        elif head != pin["commit"]:
            out.append(result(label, MISMATCH, f"HEAD {head} != pinned {pin['commit']}"))
        elif _git(path, "status", "--porcelain"):
            out.append(result(label, MISMATCH, "checkout is at the pinned commit but has local modifications"))
        else:
            out.append(result(label, PASS, f"HEAD {head} clean"))
    return out


def find_file(models_dir: Path, entry: dict[str, Any]) -> Path | None:
    for candidate in (models_dir / entry["dest_dir"] / entry["name"], models_dir / entry["name"]):
        if candidate.is_file():
            return candidate
    return None


def check_files(pins: dict[str, Any], models_dir: Path | None) -> list[dict[str, str]]:
    out = []
    for entry in pins["files"]:
        label = f"file:{entry['name']}"
        if not entry.get("sha256"):
            out.append(result(label, UNVERIFIED, "the pin has no published SHA-256"))
            continue
        if models_dir is None:
            out.append(result(label, UNVERIFIED, "no --models-dir given"))
            continue
        path = find_file(models_dir, entry)
        if path is None:
            out.append(result(label, MISSING, f"not found under {models_dir} ({entry['dest_dir']})"))
        elif path.stat().st_size != entry["size_bytes"]:
            out.append(result(label, MISMATCH, f"size {path.stat().st_size} != pinned {entry['size_bytes']}"))
        else:
            actual = sha256_file(path)
            ok = actual == entry["sha256"]
            out.append(result(label, PASS if ok else MISMATCH, f"sha256 {actual}" + ("" if ok else f" != pinned {entry['sha256']}")))
    return out


def inventory_classes(data: Any) -> set[str]:
    if isinstance(data, dict):
        return set(data)           # /object_info: class name -> definition
    if isinstance(data, list):
        return {str(item) for item in data}
    raise ValueError("node inventory must be an object_info dict or a list of class names")


def check_nodes(pins: dict[str, Any], inventory: set[str] | None) -> list[dict[str, str]]:
    out = []
    for node in pins["required_nodes"]:
        label = f"node:{node['class']}"
        if inventory is None:
            out.append(result(label, UNVERIFIED, f"no --node-inventory given (provider {node['provider']}, pin status {node['status']})"))
        elif node["class"] in inventory:
            out.append(result(label, PASS, "present in the supplied inventory"))
        else:
            out.append(result(label, MISSING, f"absent from the inventory (expected provider {node['provider']})"))
    return out


def check_workflow(pins: dict[str, Any], path: Path | None) -> list[dict[str, str]]:
    pin = pins["workflow"]
    if path is None:
        return [result("workflow", UNVERIFIED, "no --workflow given")]
    if not path.is_file():
        return [result("workflow", MISSING, f"{path} not found")]
    data = path.read_bytes()
    out = []
    blob = git_blob_sha(data)
    out.append(result("workflow:identity", PASS if blob == pin["git_blob_sha"] and len(data) == pin["size_bytes"] else MISMATCH,
                      f"git blob {blob}, {len(data)} bytes (pinned {pin['git_blob_sha']}, {pin['size_bytes']})"))
    try:
        doc = json.loads(data)
        nodes = {n["id"]: n for n in doc["nodes"]}
        links = doc["links"]
    except (ValueError, KeyError, TypeError) as exc:
        return [*out, result("workflow:structure", MISMATCH, f"not a ComfyUI UI-format workflow: {exc}")]
    problems = []
    for link in links:
        link_id, src, src_slot, dst, dst_slot = link[:5]
        if src not in nodes or dst not in nodes:
            problems.append(f"link {link_id} references missing node {src}->{dst}")
            continue
        if src_slot >= len(nodes[src].get("outputs", [])):
            problems.append(f"link {link_id}: node {src} has no output slot {src_slot}")
        if dst_slot >= len(nodes[dst].get("inputs", [])):
            problems.append(f"link {link_id}: node {dst} has no input slot {dst_slot}")
    declared = {link[0] for link in links}
    for node in nodes.values():
        for slot in node.get("inputs", []):
            if slot.get("link") is not None and slot["link"] not in declared:
                problems.append(f"node {node['id']} input {slot.get('name')} uses undeclared link {slot['link']}")
    out.append(result("workflow:links", MISMATCH if problems else PASS, "; ".join(problems[:5]) or f"{len(links)} links resolve"))
    known = {n["class"] for n in pins["required_nodes"]} | {"Note", "MarkdownNote"}
    extra = sorted({n["type"] for n in nodes.values()} - known)
    missing = sorted({n["class"] for n in pins["required_nodes"]} - {n["type"] for n in nodes.values()})
    out.append(result("workflow:node_classes", MISMATCH if extra or missing else PASS,
                      f"not in pins: {extra}; pinned but unused: {missing}" if extra or missing else "workflow classes equal the pinned list"))
    named = [str(v) for n in nodes.values() for v in n.get("widgets_values", []) if isinstance(v, str) and v.endswith(".safetensors")]
    expected = [f["name"] for f in pins["files"]]
    stale = [v for v in named if v not in expected and not v.startswith("t5xxl")]
    out.append(result("workflow:model_names", MISMATCH if stale else PASS,
                      f"workflow names {stale} which are not pinned files (checkpoint substitution is "
                      f"{'verified' if pin['checkpoint_substitution_verified'] else 'NOT verified'})" if stale else "all model names are pinned"))
    return out


def check_config(pins: dict[str, Any], models_yaml: Path | None) -> list[dict[str, str]]:
    rule = pins["frame_rule"]
    if models_yaml is None:
        return [result("config:models.yaml", UNVERIFIED, "no --models-yaml given", kind="CONFIG")]
    ltx = yaml.safe_load(models_yaml.read_text(encoding="utf-8"))["ltx"]
    out = []
    bad = [n for n in ltx["frame_counts"] if n < rule["min_frames"] or (n - 1) % rule["frame_step"]]
    out.append(result("config:frame_counts", MISMATCH if bad else PASS,
                      f"{bad} violate 8n+1" if bad else f"all of {ltx['frame_counts']} satisfy {rule['frames']}", kind="CONFIG"))
    checkpoint = next(f for f in pins["files"] if f["role"].startswith("ltx_checkpoint"))
    out.append(result("config:checkpoint_file", PASS if ltx["checkpoint_file"] == checkpoint["name"] else MISMATCH,
                      f"models.yaml {ltx['checkpoint_file']} vs pinned {checkpoint['name']}", kind="CONFIG"))
    configured = ltx.get("checkpoint_sha256")
    out.append(result("config:checkpoint_sha256", UNVERIFIED if configured is None else (PASS if configured == checkpoint["sha256"] else MISMATCH),
                      "models.yaml has no checkpoint_sha256 yet (set only after hashing the downloaded file)" if configured is None
                      else "configured value compared with the pin; a configured hash is not proof the file exists", kind="CONFIG"))
    return out


def run(args: argparse.Namespace) -> tuple[list[dict[str, str]], int]:
    pins = yaml.safe_load(Path(args.pins).read_text(encoding="utf-8"))
    given = dict(item.split("=", 1) for item in args.source)
    inventory = inventory_classes(json.loads(Path(args.node_inventory).read_text(encoding="utf-8"))) if args.node_inventory else None
    results = [
        *check_sources(pins, {k: Path(v) for k, v in given.items()}),
        *check_files(pins, Path(args.models_dir) if args.models_dir else None),
        *check_nodes(pins, inventory),
        *check_workflow(pins, Path(args.workflow) if args.workflow else None),
        *check_config(pins, Path(args.models_yaml) if args.models_yaml else None),
    ]
    statuses = {r["status"] for r in results}
    code = 1 if statuses & {MISMATCH, MISSING} else 2 if UNVERIFIED in statuses else 0
    return results, code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pins", default=str(ROOT / "config" / "ltx_098_pins.yaml"))
    parser.add_argument("--source", action="append", default=[], metavar="NAME=PATH", help="local git checkout of a pinned source")
    parser.add_argument("--models-dir", help="ComfyUI root (or a flat folder) holding the pinned model files")
    parser.add_argument("--workflow", help="local copy of the official workflow JSON")
    parser.add_argument("--node-inventory", help="JSON saved from ComfyUI /object_info (or a list of class names)")
    parser.add_argument("--models-yaml", help="config/models.yaml to compare with the pins (CONFIG only, not proof)")
    parser.add_argument("--json", help="write the machine-readable report here")
    args = parser.parse_args(argv)
    results, code = run(args)
    for r in results:
        print(f"{r['status']:<10} {r['kind']:<6} {r['check']:<44} {r['detail']}")
    print(f"\nexit {code}: " + {0: "all checks PASS (static match only; no inference was run)",
                                1: "MISSING or MISMATCH present", 2: "no failures, but UNVERIFIED checks remain"}[code])
    if args.json:
        Path(args.json).write_text(json.dumps({"exit": code, "results": results}, indent=2), encoding="utf-8")
    return code


if __name__ == "__main__":
    sys.exit(main())
