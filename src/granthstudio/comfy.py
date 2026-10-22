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


def node_types(graph: dict[str, Any]) -> set[str]:
    return {node["class_type"] for key, node in graph.items() if not key.startswith("_")}


_WEIGHT_EXTENSIONS = (".safetensors", ".ckpt", ".pt", ".pth", ".gguf")
_WEIGHT_NAME =re.compile(r'"([^"\\]+\.(?:safetensors|ckpt|pt|pth|gguf))"')


def check_checkpoint_binding(template: WorkflowTemplate, checkpoint_file: str) -> None:
    """The graph must load the pinned checkpoint by exact file name and no other LTX weights,
    so an LTX-2 (or any other) graph cannot be substituted for the pinned 0.9.8 workflow."""
    names = set(_WEIGHT_NAME.findall(template.text))
    if checkpoint_file not in names:
        raise ConfigError(f"workflow {template.name} does not load the pinned checkpoint {checkpoint_file}")
    others = sorted(n for n in names - {checkpoint_file} if "ltx" in n.lower())
    if others:
        raise ConfigError(f"workflow {template.name} references other LTX weights {others}")


def select_image(history: dict[str, Any], output_node: str) -> dict[str, Any]:
    node = history.get("outputs", {}).get(output_node, {})
    candidates = [item for item in node.get("images", [])
                  if str(item.get("filename", "")).lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
                  and item.get("type", "output") == "output"]
    if len(candidates) != 1:
        raise TaskFailed("designated output node must produce exactly one saved image")
    return candidates[0]


def execution_seconds(history_entry: dict[str, Any]) -> float | None:
    """Server-side execution time from ComfyUI status messages, when the server reports them."""
    stamps = {}
    for message in history_entry.get("status", {}).get("messages", []):
        if isinstance(message, list) and len(message) == 2 and isinstance(message[1], dict):
            stamps[message[0]] = message[1].get("timestamp")
    start, end = stamps.get("execution_start"), stamps.get("execution_success")
    if isinstance(start, (int, float)) and isinstance(end, (int, float)):
        return (end - start) / 1000
    return None


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

    def system_stats(self) -> dict[str, Any]:
        return json.loads(self._request("GET", "/system_stats"))

    def object_info(self) -> dict[str, Any]:
        return json.loads(self._request("GET", "/object_info"))

    def require_nodes(self, graph: dict[str, Any]) -> None:
        missing = sorted(node_types(graph) - set(self.object_info()))
        if missing:
            raise IntegrationUnavailable(f"ComfyUI at {self.base_url} lacks required nodes {missing}: NOT VALIDATED")

    def require_model_files(self, graph: dict[str, Any]) -> None:
        """Every weight file a node names must be among the options ComfyUI lists for that input.
        Absent definitions or option-less inputs are skipped (tolerant)."""
        info = self.object_info()
        for node_id, node in graph.items():
            if not isinstance(node, dict):
                continue
            definition = info.get(node.get("class_type"))
            sections = ((definition or {}).get("input") or {}) if isinstance(definition, dict) else {}
            for name, value in (node.get("inputs") or {}).items():
                if not (isinstance(value, str) and value.lower().endswith(_WEIGHT_EXTENSIONS)):
                    continue
                spec = next((sections[s][name] for s in ("required", "optional")
                             if isinstance(sections.get(s), dict) and name in sections[s]), None)
                if isinstance(spec, list) and spec and isinstance(spec[0], list) and value not in spec[0]:
                    raise IntegrationUnavailable(f"ComfyUI at {self.base_url} cannot see weight file {value} "
                                                 f"for node {node_id}: NOT VALIDATED")

    def locate(self, prompt_id: str | None = None, token: str | None = None) -> tuple[str, str, dict | None] | None:
        """Find a job in the queue or history by prompt id or by the job token sent at submission."""
        def matches(item):
            extra = item[3] if len(item) > 3 and isinstance(item[3], dict) else {}
            return (prompt_id is not None and item[1] == prompt_id) or (
                token is not None and extra.get("granthstudio_job") == token)
        queue = json.loads(self._request("GET", "/queue"))
        for where in ("queue_running", "queue_pending"):
            for item in queue.get(where, []):
                if matches(item):
                    return where.removeprefix("queue_"), str(item[1]), None
        for pid, entry in json.loads(self._request("GET", "/history")).items():
            if matches(entry.get("prompt", [None, pid])):
                return "history", pid, entry
        return None

    def submit(self, graph: dict[str, Any], token: str | None = None) -> str:
        payload = {"prompt": graph, "client_id": CLIENT_ID}
        if token is not None:
            payload["extra_data"] = {"granthstudio_job": token}
        body = json.dumps(payload).encode("utf-8")
        data = json.loads(self._request("POST", "/prompt", body))
        if "prompt_id" not in data:
            raise TaskFailed(f"ComfyUI rejected the prompt: {data}")
        return str(data["prompt_id"])

    def wait(self, prompt_id: str, sampler=None) -> dict[str, Any]:
        deadline = time.monotonic() + self.max_wait_s
        while time.monotonic() < deadline:
            if sampler is not None:
                sampler()
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


    def execute(self, graph: dict[str, Any], journal: Path, sampler=None) -> dict[str, Any]:
        """Persist intent before POST; an ambiguous submission must be reconciled, never repeated."""
        identity = {"base_url": self.base_url, "graph_sha256": sha256_obj(graph)}
        state = read_json(journal) if journal.exists() else None
        if state and any(state.get(k) != v for k, v in identity.items()):
            raise JobPending("submission journal belongs to different runtime/graph")
        if state and state.get("state") == "submitting":
            raise JobPending("submission outcome unknown; run 'comfy reconcile' before another POST")
        if state and state.get("state") == "cancelled":
            raise JobPending("job was cancelled; run 'comfy reconcile' to confirm it stopped before resubmitting")
        if not state or state.get("state") == "failed":
            attempt = (state or {}).get("attempt", 0) + 1
            token = sha256_obj({**identity, "journal": journal.name, "attempt": attempt})
            state = {**identity, "state": "submitting", "job_token": token, "attempt": attempt}
            atomic_write_json(journal, state)
            try:
                prompt_id = self.submit(graph, token)
            except IntegrationUnavailable as exc:
                raise JobPending("submission outcome unknown; retained journal for reconciliation") from exc
            except TaskFailed:
                atomic_write_json(journal, {**state, "state": "failed"})
                raise
            state = {**state, "state": "submitted", "prompt_id": prompt_id}
            atomic_write_json(journal, state)
        try:
            return self.wait(state["prompt_id"], sampler) if sampler else self.wait(state["prompt_id"])
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


def reconcile(backend: ComfyBackend, journal: Path, declare_lost: bool = False) -> dict[str, Any]:
    """Resolve an unknown or cancelled submission from the server's own queue and history.

    A job that cannot be found is only marked failed (resubmittable) when the operator
    declares it lost, because a cleared history would otherwise cause a duplicate GPU job.
    """
    state = read_json(journal)
    if state["state"] == "submitting":
        found = backend.locate(token=state.get("job_token")) if state.get("job_token") else None
        if found:
            state = {**state, "state": "submitted", "prompt_id": found[1]}
        elif declare_lost:
            state = {**state, "state": "failed", "declared_lost": True}
        else:
            raise JobPending("submission not found in queue or history; confirm on the server, then use --declare-lost")
    elif state["state"] == "cancelled":
        found = backend.locate(prompt_id=state["prompt_id"])
        if found and found[0] in ("running", "pending"):
            raise JobPending(f"cancelled prompt {state['prompt_id']} is still {found[0]}")
        succeeded = found is not None and found[2].get("status", {}).get("status_str") == "success"
        state = {**state, "state": "submitted" if succeeded else "failed"}
    atomic_write_json(journal, state)
    return state


def cancel(backend: ComfyBackend, journal: Path) -> dict[str, Any]:
    """Operator cancellation: remove a queued prompt, or interrupt it only when it is the running one."""
    state = read_json(journal)
    if state["state"] != "submitted":
        raise ConfigError(f"only a submitted job can be cancelled (journal state {state['state']!r}); reconcile first")
    found = backend.locate(prompt_id=state["prompt_id"])
    if found and found[0] == "pending":
        backend._request("POST", "/queue", json.dumps({"delete": [state["prompt_id"]]}).encode("utf-8"))
    elif found and found[0] == "running":
        backend._request("POST", "/interrupt", json.dumps({"prompt_id": state["prompt_id"]}).encode("utf-8"))
    state = {**state, "state": "cancelled"}
    atomic_write_json(journal, state)
    return state
