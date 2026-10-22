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

from .errors import ConfigError, IntegrationUnavailable, TaskFailed
from .integrity import sha256_file

CLIENT_ID = "granthstudio"
_PLACEHOLDER = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")


@dataclass(frozen=True)
class WorkflowTemplate:
    name: str
    path: Path
    version: str
    status: str
    text: str


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
    )


def ensure_validated(template: WorkflowTemplate) -> None:
    if template.status != "validated":
        raise IntegrationUnavailable(f"workflow {template.name} status is '{template.status}': NOT VALIDATED")


def render_graph(template: WorkflowTemplate, values: dict[str, str]) -> dict[str, Any]:
    missing = set(_PLACEHOLDER.findall(template.text)) - set(values)
    if missing:
        raise ConfigError(f"unresolved placeholders in {template.name}: {sorted(missing)}")

    def substitute(match: re.Match[str]) -> str:
        return json.dumps(str(values[match.group(1)]), ensure_ascii=False)[1:-1]

    graph = json.loads(_PLACEHOLDER.sub(substitute, template.text))
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
        raise TaskFailed(f"ComfyUI prompt {prompt_id} did not finish within {self.max_wait_s} s")

    def fetch(self, item: dict[str, Any], dest: Path) -> None:
        query = urllib.parse.urlencode(
            {"filename": item["filename"], "subfolder": item.get("subfolder", ""), "type": item.get("type", "output")}
        )
        dest.write_bytes(self._request("GET", f"/view?{query}"))
