"""ComfyUI adapter: workflow templates, placeholder rendering, job submission and output tracking.

NOT VALIDATED on this machine. No ComfyUI server, GPU or LTX checkpoint has been run here.
A template runs only when its ``_status`` is ``validated``; the capability gate in config.py
also requires a pinned checkpoint and a passing benchmark receipt.
"""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import ConfigError, IntegrationUnavailable, JobPending, TaskFailed
from .integrity import atomic_write_json, read_json, sha256_file, sha256_obj

CLIENT_ID = "granthstudio"
_PLACEHOLDER = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")


@dataclass(frozen=True)
class WorkflowTemplate:
    name: str
    path: Path
    version: str
    status: str
    text: str
    output_node: str | None = None


def load_template(path: Path) -> WorkflowTemplate:
    if not path.is_file():
        raise ConfigError(f"workflow template missing: {path}")
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ConfigError(f"workflow template {path.name} is not valid JSON: {exc}") from exc
    return WorkflowTemplate(
        name=path.stem,
        path=path,
        version=sha256_file(path),
        status=str(data.get("_status", "unvalidated")),
        text=text,
        output_node=data.get("_output_node"),
    )


def ensure_validated(template: WorkflowTemplate) -> None:
    if template.status != "validated":
        raise IntegrationUnavailable(f"workflow {template.name} status is '{template.status}': NOT VALIDATED")
    graph = json.loads(template.text)
    if not template.output_node or template.output_node not in graph:
        raise ConfigError("validated workflows must designate _output_node")
    for key, node in graph.items():
        if not key.startswith("_") and (not isinstance(node, dict) or not node.get("class_type") or not isinstance(node.get("inputs"), dict)):
            raise ConfigError("expected a ComfyUI API node graph with class_type and inputs")


def render_graph(template: WorkflowTemplate, values: dict[str, str]) -> dict[str, Any]:
    missing = set(_PLACEHOLDER.findall(template.text)) - set(values)
    if missing:
        raise ConfigError(f"unresolved placeholders in {template.name}: {sorted(missing)}")

    def substitute(value):
        if isinstance(value, str):
            match = _PLACEHOLDER.fullmatch(value)
            if match:
                return values[match.group(1)]
            return _PLACEHOLDER.sub(lambda m: str(values[m.group(1)]), value)
        if isinstance(value, list):
            return [substitute(v) for v in value]
        if isinstance(value, dict):
            return {k: substitute(v) for k, v in value.items()}
        return value
    graph = substitute(json.loads(template.text))
    return {key: value for key, value in graph.items() if not key.startswith("_")}


def collect_outputs(history_entry: dict[str, Any]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for _node_id, node in sorted(history_entry.get("outputs", {}).items()):
        for key in ("videos", "gifs", "images"):
            for item in node.get(key, []):
                if "filename" in item:
                    found.append(item)
    return found


class ComfyBackend:
    def __init__(self, base_url: str, timeout_s: float = 30.0, poll_s: float = 2.0, max_wait_s: float = 1800.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s
        self.poll_s = poll_s
        self.max_wait_s = max_wait_s

    def _request(self, method: str, path: str, body: bytes | None = None) -> bytes:
        request = urllib.request.Request(
            self.base_url + path, data=body, method=method, headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_s) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            # Only a 4xx on the submission itself proves nothing was queued. A 4xx on a status
            # poll (proxy/tunnel 404, 403, 429) says nothing about an accepted prompt.
            if 400 <= exc.code < 500 and not path.startswith("/history/"):
                raise TaskFailed(f"ComfyUI HTTP {exc.code} rejected {method} {path}: {exc.reason}") from exc
            # A server error does not establish whether a submitted job was accepted.
            raise IntegrationUnavailable(f"ComfyUI HTTP {exc.code} at {self.base_url}: {exc.reason}") from exc
        except (urllib.error.URLError, OSError) as exc:
            raise IntegrationUnavailable(f"ComfyUI unreachable at {self.base_url}: {exc}") from exc

    def submit(self, graph: dict[str, Any]) -> str:
        body = json.dumps({"prompt": graph, "client_id": CLIENT_ID}).encode("utf-8")
        data = json.loads(self._request("POST", "/prompt", body))
        if "prompt_id" not in data:
            raise TaskFailed(f"ComfyUI rejected the prompt: {data}")
        return str(data["prompt_id"])

    def wait(self, prompt_id: str) -> dict[str, Any]:
        deadline = time.monotonic() + self.max_wait_s
        while time.monotonic() < deadline:
            history = json.loads(self._request("GET", f"/history/{prompt_id}"))
            if prompt_id in history:
                entry = history[prompt_id]
                if entry.get("status", {}).get("status_str") == "error":
                    raise TaskFailed(f"ComfyUI execution error for prompt {prompt_id}")
                return entry
            time.sleep(self.poll_s)
        raise JobPending(f"ComfyUI prompt {prompt_id} remains outstanding after {self.max_wait_s} s; resume polling")

    def fetch(self, item: dict[str, Any], dest: Path) -> None:
        query = urllib.parse.urlencode(
            {"filename": item["filename"], "subfolder": item.get("subfolder", ""), "type": item.get("type", "output")}
        )
        dest.write_bytes(self._request("GET", f"/view?{query}"))


    def execute(self, graph: dict[str, Any], journal: Path) -> dict[str, Any]:
        """Persist intent before POST; an ambiguous submission must be reconciled, never repeated."""
        identity = {"base_url": self.base_url, "graph_sha256": sha256_obj(graph)}
        state = read_json(journal) if journal.exists() else None
        if state and any(state.get(k) != v for k, v in identity.items()):
            raise JobPending("submission journal belongs to different runtime/graph")
        if state and state.get("state") == "submitting":
            raise JobPending("submission outcome unknown; reconcile with ComfyUI before another POST")
        if not state or state.get("state") == "failed":
            state = {**identity, "state": "submitting"}
            atomic_write_json(journal, state)
            try:
                prompt_id = self.submit(graph)
            except IntegrationUnavailable as exc:
                raise JobPending("submission outcome unknown; retained journal for reconciliation") from exc
            except TaskFailed:
                atomic_write_json(journal, {**identity, "state": "failed"})
                raise
            state = {**identity, "state": "submitted", "prompt_id": prompt_id}
            atomic_write_json(journal, state)
        try:
            return self.wait(state["prompt_id"])
        except IntegrationUnavailable as exc:
            raise JobPending("connection lost; retain prompt and resume polling") from exc
        except TaskFailed:
            atomic_write_json(journal, {**state, "state": "failed"})
            raise


def select_video(history: dict[str, Any], output_node: str) -> dict[str, Any]:
    node = history.get("outputs", {}).get(output_node, {})
    candidates = [item for key in ("videos", "gifs") for item in node.get(key, [])
                  if str(item.get("filename", "")).lower().endswith(".mp4")]
    if len(candidates) != 1:
        raise TaskFailed("designated output node must produce exactly one MP4")
    return candidates[0]
