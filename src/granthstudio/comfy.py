"""ComfyUI adapter: workflow templates, placeholder rendering, job submission and output tracking.

NOT VALIDATED on this machine. No ComfyUI server, GPU or LTX checkpoint has been run here.
A template runs only when its ``_status`` is ``validated``; the capability gate in config.py
also requires a pinned checkpoint and a passing benchmark receipt.
"""

from __future__ import annotations

import json
import os
import re
import time
import uuid
from contextlib import contextmanager
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import ConfigError, GateFailure, IntegrationUnavailable, JobPending, TaskFailed
from .integrity import atomic_write_json, read_json, sha256_file, sha256_obj

CLIENT_ID = "granthstudio"
LOCK_WAIT_S = 60.0
NAMESPACE_FILE = ".store_namespace"
_PLACEHOLDER = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")


def _location(journal: Path) -> str:
    return os.path.normcase(str(journal.parent.resolve()))


def store_namespace(journal: Path) -> str:
    """Durable per-store submission namespace bound to the store's location.

    Recovery of the same store (same location, any number of restarts or restores into that place) keeps its
    namespace. A copy or restore into a different location is a fork: it gets a NEW namespace (recording the
    parent) so two stores that are active at once can never share tokens; journals written under the parent
    namespace then need an explicit ``adopt_journal`` before this store may touch their prompts."""
    path = journal.parent / NAMESPACE_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    here = _location(journal)
    with owned(path):
        record, changed = None, False
        if path.is_file():
            text = path.read_text(encoding="utf-8").strip()
            try:
                record = json.loads(text)
                if not isinstance(record, dict) or "namespace" not in record:
                    raise ValueError("not a namespace record")
            except ValueError:
                record, changed = {"namespace": text, "location": here}, True    # BASE-format plain-text id: migrate in place
        if record is None or record.get("location") != here:
            record = {"namespace": uuid.uuid4().hex, "location": here,
                      **({"forked_from": record["namespace"]} if record else {})}
            changed = True
        if changed:
            atomic_write_json(path, record)
        return record["namespace"]


def adopt_journal(journal: Path, authorized_by: str, original_inactive: bool = False) -> dict[str, Any]:
    """Bind a journal written under another (parent) namespace to this store, deliberately.

    Terminal states (failed/rejected/completed) hold nothing outstanding and can be adopted by a named reviewer.
    A submitting/submitted/cancelled journal may still have a live prompt on the server for the original store,
    so adoption additionally needs ``original_inactive=True`` (the operator confirms the original is stopped).
    The old namespace is kept in ``adopted_from``; nothing is resubmitted by adopting."""
    if not authorized_by.strip():
        raise ConfigError("a reviewer name is required to adopt a journal")
    namespace = store_namespace(journal)
    with owned(journal):
        state = read_json(journal)
        if state.get("namespace", namespace) == namespace:
            return state
        if state["state"] not in ("failed", "rejected", "completed") and not original_inactive:
            raise ConfigError(f"journal state {state['state']!r} may belong to a live prompt of the original store; "
                              "confirm the original is inactive to adopt it")
        state = {**state, "namespace": namespace,
                 "submission_namespace": state.get("submission_namespace", state["namespace"]),   # what the server holds
                 "adopted_from": [*state.get("adopted_from", []), {"namespace": state["namespace"], "by": authorized_by.strip()}]}
        atomic_write_json(journal, state)
    return state


if os.name == "nt":
    import msvcrt

    def _try_lock(fd: int) -> None:
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)      # OSError while another handle holds byte 0

    def _unlock(fd: int) -> None:
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
else:
    import fcntl

    def _try_lock(fd: int) -> None:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)   # BlockingIOError (an OSError) while held elsewhere

    def _unlock(fd: int) -> None:
        fcntl.flock(fd, fcntl.LOCK_UN)


@contextmanager
def owned(journal: Path, wait_s: float | None = None):
    """Exclusive journal ownership: an OS lock held on a persistent sibling file for the whole transaction.

    The operating system drops the lock when the owning process dies and never while it lives, so a live
    process is never displaced however long it holds the journal; there is deliberately no age-based
    takeover. A contender waits ``wait_s`` and then gets JobPending. The lock file is never deleted or
    replaced (no reclamation races). An owner that died after recording submission intent leaves state
    "submitting", which forces reconcile rather than a resubmission."""
    wait_s = LOCK_WAIT_S if wait_s is None else wait_s
    lock = journal.with_name(journal.name + ".lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(lock, os.O_RDWR | os.O_CREAT)
    deadline = time.monotonic() + wait_s
    try:
        while True:
            try:
                _try_lock(fd)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise JobPending(f"journal {journal.name} is owned by another process") from None
                time.sleep(0.02)
        try:
            yield
        finally:
            try:
                _unlock(fd)
            except OSError:
                pass
    finally:
        os.close(fd)


SEED_INPUTS = ("seed", "noise_seed")


def generation_closure(graph: dict[str, Any], output_node: str) -> dict[str, dict[str, Any]]:
    """The nodes the designated output depends on, transitively (ComfyUI executes and caches exactly these)."""
    if output_node not in graph:
        raise ConfigError(f"designated output node {output_node!r} is not in the submitted graph")
    seen: dict[str, dict[str, Any]] = {}
    stack = [output_node]
    while stack:
        node_id = stack.pop()
        if node_id in seen or not isinstance(graph.get(node_id), dict):
            continue
        seen[node_id] = graph[node_id]
        for value in (graph[node_id].get("inputs") or {}).values():
            if isinstance(value, list) and len(value) == 2 and isinstance(value[0], str):
                stack.append(value[0])
    return seen


def generation_evidence(graph: dict[str, Any], output_node: str | None) -> dict[str, Any]:
    """Cache-relevant identity of a submission: a hash of the upstream closure of the designated output only,
    plus the integer seed inputs found on that path. Nodes outside the closure (a disconnected SEED placeholder,
    unrelated graph fields) cannot change it. Without a designated output the whole graph is used."""
    if output_node is None:
        return {"fingerprint": sha256_obj(graph), "seed_inputs": [], "scope": "whole_graph"}
    closure = generation_closure(graph, output_node)
    upstream = {k: v for k, v in closure.items() if k != output_node}   # the save node's own fields (filename_prefix...) are not generation inputs
    seeds = [{"node": node_id, "input": name, "value": node["inputs"][name]} for node_id, node in sorted(upstream.items())
             for name in SEED_INPUTS if isinstance((node.get("inputs") or {}).get(name), int)
             and not isinstance(node["inputs"][name], bool)]
    return {"fingerprint": sha256_obj({k: upstream[k] for k in sorted(upstream)}), "seed_inputs": seeds, "scope": "output_closure"}


def generation_seed(journal: Path, base_seed: int) -> int:
    """Seed for the next generation. ComfyUI caches node outputs by class and inputs, so a new prompt_id or
    extra_data does not force fresh inference; after each definitively rejected render the sampler seed input is
    offset by the rejection count (recorded in the journal) so the graph genuinely differs."""
    state = read_json(journal) if journal.is_file() else {}
    return base_seed + len(state.get("rejections", []))


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

    def locate(self, prompt_id: str | None = None, token: str | None = None, namespace: str | None = None) -> tuple[str, str, dict | None] | None:
        """Find a job in the queue or history by prompt id or by the job token sent at submission."""
        def matches(item):
            extra = item[3] if len(item) > 3 and isinstance(item[3], dict) else {}
            return (prompt_id is not None and item[1] == prompt_id) or (
                token is not None and extra.get("granthstudio_job") == token
                and (namespace is None or extra.get("granthstudio_ns") in (None, namespace)))
        queue = json.loads(self._request("GET", "/queue"))
        for where in ("queue_running", "queue_pending"):
            for item in queue.get(where, []):
                if matches(item):
                    return where.removeprefix("queue_"), str(item[1]), None
        for pid, entry in json.loads(self._request("GET", "/history")).items():
            if matches(entry.get("prompt", [None, pid])):
                return "history", pid, entry
        return None

    def submit(self, graph: dict[str, Any], token: str | None = None, namespace: str | None = None) -> str:
        payload = {"prompt": graph, "client_id": CLIENT_ID}
        if token is not None:
            payload["extra_data"] = {"granthstudio_job": token, **({"granthstudio_ns": namespace} if namespace else {})}
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


    def execute(self, graph: dict[str, Any], journal: Path, sampler=None, max_attempts: int | None = None,
                generation: dict[str, Any] | None = None, output_node: str | None = None) -> dict[str, Any]:
        """Persist intent before POST under exclusive journal ownership; an ambiguous submission must be
        reconciled, never repeated. ``max_attempts`` is a durable budget of generations (POSTs) for this journal;
        polling or reconciling an existing prompt never consumes it. ``generation`` (e.g. the seed used) is
        recorded with the attempt."""
        namespace, graph_sha = store_namespace(journal), sha256_obj(graph)
        evidence = generation_evidence(graph, output_node)
        with owned(journal):
            state = read_json(journal) if journal.exists() else None
            if state and state.get("base_url") != self.base_url:
                raise JobPending("submission journal belongs to a different runtime")
            if state and state.get("namespace", namespace) != namespace:
                raise JobPending("submission journal belongs to another store identity (copied or restored elsewhere); "
                                 "adopt it explicitly with 'comfy adopt' before this store touches its prompt")
            if state and state.get("state") in ("submitting", "submitted", "completed", "cancelled") \
                    and state.get("graph_sha256") != graph_sha:
                raise JobPending("submission journal belongs to a different graph")
            if state and state.get("state") == "submitting":
                raise JobPending("submission outcome unknown; run 'comfy reconcile' before another POST")
            if state and state.get("state") == "cancelled":
                raise JobPending("job was cancelled; run 'comfy reconcile' to confirm it stopped before resubmitting")
            if not state or state.get("state") in ("failed", "rejected"):
                # failed: definitive submission/execution failure. rejected: the render completed but its media
                # was judged invalid; its output (and ComfyUI's cached node outputs for it) must not be reused.
                if state and state.get("state") == "rejected":
                    if output_node is not None and not evidence["seed_inputs"]:
                        raise GateFailure("the workflow has no seed input on the path to its designated output, so a retry "
                                          "cannot be shown to differ from the rejected render")
                    if evidence["fingerprint"] in state.get("rejected_fingerprints", []):
                        raise GateFailure("a rejected render cannot be resubmitted with the same generation inputs: ComfyUI "
                                          "would reuse cached node outputs; the seed input on the path to the designated "
                                          "output must change (comfy.generation_seed)")
                attempt = (state or {}).get("attempt", 0) + 1
                caps = [c for c in ((state or {}).get("max_attempts"), max_attempts) if c is not None]
                cap = min(caps) if caps else None      # the journal's established cap is authoritative; callers can only tighten
                if cap is not None and attempt - (state or {}).get("attempt_base", 0) > cap:
                    raise GateFailure(f"generation budget exhausted: {cap} attempt(s) already submitted for "
                                      f"{journal.name}; an authorized reset (comfy reset-budget) is required")
                token = sha256_obj({"base_url": self.base_url, "graph_sha256": graph_sha, "journal": journal.name,
                                    "attempt": attempt, "namespace": namespace})
                carry = {k: state[k] for k in ("rejections", "rejected_fingerprints", "attempt_base", "budget_resets",
                                               "history") if state and k in state}
                state = {**carry, "base_url": self.base_url, "graph_sha256": graph_sha, "namespace": namespace,
                         **({"max_attempts": cap} if cap is not None else {}), "state": "submitting", "job_token": token, "attempt": attempt, "submission_namespace": namespace,
                         "history": [*carry.get("history", []), {"attempt": attempt, "job_token": token,
                                                                 "graph_sha256": graph_sha, "generation": generation or {},
                                                                 "fingerprint": evidence["fingerprint"],
                                                                 "seed_inputs": evidence["seed_inputs"],
                                                                 "scope": evidence["scope"]}]}
                atomic_write_json(journal, state)
                try:
                    prompt_id = self.submit(graph, token, namespace)
                except IntegrationUnavailable as exc:
                    raise JobPending("submission outcome unknown; retained journal for reconciliation") from exc
                except TaskFailed:
                    atomic_write_json(journal, {**state, "state": "failed"})
                    raise
                state = {**state, "state": "submitted", "prompt_id": prompt_id}
                atomic_write_json(journal, state)
        prompt_id = state["prompt_id"]
        try:
            history = self.wait(prompt_id, sampler) if sampler else self.wait(prompt_id)
        except IntegrationUnavailable as exc:
            raise JobPending("connection lost; retain prompt and resume polling") from exc
        except TaskFailed:
            self._settle(journal, prompt_id, "failed")
            raise
        self._settle(journal, prompt_id, "completed")
        return history

    @staticmethod
    def _settle(journal: Path, prompt_id: str, new_state: str) -> None:
        with owned(journal):
            current = read_json(journal)
            if current.get("prompt_id") == prompt_id and current.get("state") == "submitted":
                atomic_write_json(journal, {**current, "state": new_state})


def reject_output(journal: Path, reason: str) -> bool:
    """Record that a *completed* render failed media validation so a fresh generation may be submitted.
    Any other journal state (uncertain submission, still polling, failed) is left untouched: never
    resubmit while the previous job might be active."""
    if not journal.is_file():
        return False
    with owned(journal):
        state = read_json(journal)
        if state.get("state") != "completed":
            return False
        fingerprint = state["history"][-1]["fingerprint"]
        rejection = {"attempt": state["attempt"], "prompt_id": state["prompt_id"], "reason": reason[:500],
                     "graph_sha256": state["graph_sha256"], "fingerprint": fingerprint}
        atomic_write_json(journal, {**state, "state": "rejected", "rejections": [*state.get("rejections", []), rejection],
                                    "rejected_fingerprints": [*state.get("rejected_fingerprints", []), fingerprint]})
    return True


def reset_budget(journal: Path, authorized_by: str) -> dict[str, Any]:
    """Explicit, named reset of the durable generation budget; only when no job is outstanding."""
    if not authorized_by.strip():
        raise ConfigError("a reviewer name is required to reset the generation budget")
    with owned(journal):
        state = read_json(journal)
        if state["state"] not in ("failed", "rejected"):
            raise ConfigError(f"budget can only be reset when no job is outstanding (journal state {state['state']!r})")
        state = {**state, "attempt_base": state["attempt"],
                 "budget_resets": [*state.get("budget_resets", []), {"at_attempt": state["attempt"], "by": authorized_by.strip()}]}
        atomic_write_json(journal, state)
    return state


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
    with owned(journal):
        return _reconcile(backend, journal, declare_lost)


def _reconcile(backend, journal, declare_lost):
    state = read_json(journal)
    if state.get("namespace", store_namespace(journal)) != store_namespace(journal):
        raise JobPending("journal belongs to another store identity; adopt it explicitly before reconciling")
    if state["state"] == "submitting":
        found = (backend.locate(token=state.get("job_token"),
                                namespace=state.get("submission_namespace", state.get("namespace")))
                 if state.get("job_token") else None)
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
    with owned(journal):
        return _cancel(backend, journal)


def _cancel(backend, journal):
    state = read_json(journal)
    if state.get("namespace", store_namespace(journal)) != store_namespace(journal):
        raise JobPending("journal belongs to another store identity; adopt it explicitly before cancelling")
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
