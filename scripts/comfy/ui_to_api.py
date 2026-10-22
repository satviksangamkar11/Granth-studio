"""Convert a ComfyUI UI-format workflow into the API format that comfy.py submits, without inventing anything.

Every connection comes from the UI file's own `links`; every literal comes from its `widgets_values`, matched to input names
by a signature (a table read from source, or - preferred - rebuilt from a running server's /object_info). Anything the UI
file does not determine is either a signature default (reported as DEFAULTED) or an error. Deliberate changes are listed in a
recipe (workflows/comfyui/source/*.recipe.yaml) and reported as OVERRIDE, so nothing is silently different from the official file.

  build   --recipe R [--ui FILE] [--object-info FILE] [--out FILE]   convert and write the API workflow
  compare A B                                                        exit 0 only if two API graphs are identical (underscore keys ignored)

Run `build` on the GPU host with the official file and the server's /object_info, then `compare` the result with the committed
candidate: equal means the candidate is what the real file and the real node definitions produce.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
PRIMITIVES = {"INT", "FLOAT", "STRING", "BOOLEAN"}
UI_ONLY = {"Note", "MarkdownNote"}


class ConversionError(Exception):
    pass


def load_signatures(path: Path) -> dict[str, dict[str, Any]]:
    flat: dict[str, dict[str, Any]] = {}
    for group in yaml.safe_load(path.read_text(encoding="utf-8")).values():
        flat.update(group)
    return flat


def signatures_from_object_info(info: dict[str, Any], used: set[str], ui_trailing: dict[str, int]) -> dict[str, dict[str, Any]]:
    """Signatures from a running server: required then optional inputs in the server's order; forceInput and non-primitive types are links."""
    out = {}
    for name in sorted(used):
        if name not in info:
            raise ConversionError(f"node class {name} is not in the supplied /object_info")
        spec = info[name]
        order = spec.get("input_order") or {k: list(v) for k, v in spec["input"].items()}
        inputs = []
        for section in ("required", "optional"):
            for key in order.get(section, []):
                definition = spec["input"][section][key]
                kind_or_options, options = definition[0], (definition[1] if len(definition) > 1 else {})
                is_widget = isinstance(kind_or_options, list) or (kind_or_options in PRIMITIVES and not options.get("forceInput"))
                entry: dict[str, Any] = {"name": key, "kind": "widget" if is_widget else "link"}
                if is_widget and "default" in options:
                    entry["default"] = options["default"]
                if options.get("control_after_generate"):
                    entry["control_after_generate"] = True
                if isinstance(kind_or_options, list) and "formats" in options:
                    entry["formats"] = options["formats"]
                inputs.append(entry)
        out[name] = {"inputs": inputs, "ui_trailing": ui_trailing.get(name, 0), "outputs": spec.get("output_name", [])}
    return out


def _format_widgets(entry: dict[str, Any], chosen: Any) -> list[dict[str, Any]]:
    extra = []
    for widget in (entry.get("formats") or {}).get(chosen, []):
        extra.append({"name": widget[0], "kind": "widget"})
    return extra


def convert(ui: dict[str, Any], signatures: dict[str, dict[str, Any]], overrides: dict[str, Any] | None = None) -> tuple[dict[str, Any], list[str]]:
    report: list[str] = []
    links = {link[0]: link for link in ui["links"]}
    nodes = {str(n["id"]): n for n in ui["nodes"] if n["type"] not in UI_ONLY}
    api: dict[str, Any] = {}
    for node_id, node in sorted(nodes.items(), key=lambda kv: int(kv[0])):
        sig = signatures.get(node["type"])
        if sig is None:
            raise ConversionError(f"node {node_id}: no signature for class {node['type']}")
        values = list(node.get("widgets_values") or [])
        wired = {}
        for index, slot in enumerate(node.get("inputs", [])):
            link_id = slot.get("link")
            if link_id is None:
                continue
            if link_id not in links:
                raise ConversionError(f"node {node_id} input {slot['name']}: link {link_id} is not declared")
            _, src, src_slot, dst, dst_slot, _ = links[link_id]
            if str(dst) != node_id or dst_slot != index:
                raise ConversionError(f"node {node_id} input {slot['name']}: link {link_id} ends at node {dst} slot {dst_slot}, not here (slot {index})")
            source = next((n for n in ui["nodes"] if str(n["id"]) == str(src)), None)
            if source is None or source["type"] in UI_ONLY:
                raise ConversionError(f"node {node_id} input {slot['name']}: link {link_id} comes from a UI-only or missing node")
            if src_slot >= len(source.get("outputs", [])):
                raise ConversionError(f"node {node_id} input {slot['name']}: link {link_id} uses output slot {src_slot} that node {src} lacks")
            wired[slot["name"]] = (str(src), src_slot)
        inputs: dict[str, Any] = {}
        cursor = 0
        plan = list(sig["inputs"])
        index = 0
        while index < len(plan):
            entry = plan[index]
            index += 1
            if entry["kind"] == "link":
                if entry["name"] in wired:
                    inputs[entry["name"]] = list(wired.pop(entry["name"]))
                continue                            # optional and unconnected
            if entry["name"] in wired:
                raise ConversionError(f"node {node_id} {node['type']}: input {entry['name']} is wired in the UI but the signature treats it as a widget")
            if cursor < len(values):
                inputs[entry["name"]] = values[cursor]
                cursor += 1
                if entry.get("control_after_generate"):
                    cursor += 1                     # the UI stores 'fixed'/'randomize' right after the seed
                if entry.get("formats"):            # format-dependent widgets are inserted right after the chosen format
                    plan[index:index] = _format_widgets(entry, inputs[entry["name"]])
            elif "default" in entry:
                inputs[entry["name"]] = entry["default"]
                report.append(f"DEFAULTED node {node_id} {node['type']}.{entry['name']} = {entry['default']!r} (not stored in the UI file)")
            else:
                raise ConversionError(f"node {node_id} {node['type']}: no stored value for widget {entry['name']}")
        if wired:
            raise ConversionError(f"node {node_id} {node['type']}: UI connection(s) {sorted(wired)} match no signature input (a wrong name would drop a wire)")
        leftover = len(values) - cursor
        if leftover != sig.get("ui_trailing", 0):
            raise ConversionError(f"node {node_id} {node['type']}: {leftover} unexplained widget value(s), signature allows {sig.get('ui_trailing', 0)}")
        api[node_id] = {"class_type": node["type"], "inputs": inputs}
    for key, value in (overrides or {}).items():
        node_id, name = key.split(".", 1)
        if node_id not in api or name not in api[node_id]["inputs"]:
            raise ConversionError(f"override {key}: no such node input")
        before = api[node_id]["inputs"][name]
        api[node_id]["inputs"][name] = value
        report.append(f"OVERRIDE node {node_id} {api[node_id]['class_type']}.{name}: {str(before)[:40]!r} -> {str(value)[:60]!r}")
    return api, report


def strip_meta(graph: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in graph.items() if not k.startswith("_")}


def build(recipe_path: Path, ui_path: Path | None, object_info: Path | None, signatures_path: Path) -> tuple[dict[str, Any], list[str]]:
    recipe = yaml.safe_load(recipe_path.read_text(encoding="utf-8"))
    ui = json.loads((ui_path or ROOT / recipe["ui_file"]).read_text(encoding="utf-8"))
    if object_info:
        used = {n["type"] for n in ui["nodes"] if n["type"] not in UI_ONLY}
        trailing = {c: s.get("ui_trailing", 0) for c, s in load_signatures(signatures_path).items()}
        signatures = signatures_from_object_info(json.loads(object_info.read_text(encoding="utf-8")), used, trailing)
        origin = f"live /object_info {object_info.name}"
    else:
        signatures, origin = load_signatures(signatures_path), "source-read signature table"
    api, report = convert(ui, signatures, recipe.get("overrides"))
    report.insert(0, f"signatures: {origin}; {len(api)} nodes, {sum(len(n['inputs']) for n in api.values())} inputs")
    graph = {"_status": "unvalidated", "_output_node": str(recipe["output_node"]),
             "_note": recipe["note"], "_recipe": recipe_path.name, **api}
    return graph, report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build")
    b.add_argument("--recipe", required=True, type=Path)
    b.add_argument("--ui", type=Path)
    b.add_argument("--object-info", type=Path)
    b.add_argument("--signatures", type=Path, default=ROOT / "scripts" / "comfy" / "node_signatures.yaml")
    b.add_argument("--out", type=Path)
    c = sub.add_parser("compare")
    c.add_argument("a", type=Path)
    c.add_argument("b", type=Path)
    args = parser.parse_args(argv)
    if args.command == "build":
        graph, report = build(args.recipe, args.ui, args.object_info, args.signatures)
        print("\n".join(report))
        if args.out:
            args.out.write_text(json.dumps(graph, indent=2) + "\n", encoding="utf-8")
        return 0
    a, b2 = (strip_meta(json.loads(p.read_text(encoding="utf-8"))) for p in (args.a, args.b))
    if a == b2:
        print("IDENTICAL")
        return 0
    for node in sorted(set(a) | set(b2)):
        if a.get(node) != b2.get(node):
            print(f"DIFFERENT node {node}: {a.get(node)} != {b2.get(node)}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
