"""Sequential filesystem tasks, content-bound receipts and recoverable atomic outputs."""
from __future__ import annotations

import json
import os
import shutil
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from .errors import CapabilityDisabled, ConfigError, GateFailure, GranthError, IntegrationUnavailable, JobPending, TaskFailed
from .integrity import atomic_write_json, contained_path, read_json, sha256_file, sha256_obj
from .schemas import validate_document

STAGE_ORDER = ("audio", "keyframe", "tier0", "tier1", "tier2", "assembly")
RECEIPT = "task_receipt.json"
RUN_LOG = "run_log.jsonl"
NOT_RETRYABLE = (CapabilityDisabled, IntegrationUnavailable)
RunFn = Callable[[Path], dict[str, str]]

@dataclass
class Task:
    stage: str
    name: str
    inputs: dict[str, str]
    workflow_version: str
    run: RunFn = field(repr=False)
    depends_on: tuple[str, ...] = ()
    max_attempts: int = 1
    preflight: Callable[[], None] | None = field(default=None, repr=False)
    verify: Callable[[Path], None] | None = field(default=None, repr=False)

    def __post_init__(self):
        if self.stage not in STAGE_ORDER or self.max_attempts < 1:
            raise ConfigError("invalid stage or attempt count")

    def task_id(self) -> str:
        return sha256_obj({"stage": self.stage, "name": self.name, "inputs": self.inputs,
                           "workflow_version": self.workflow_version, "depends_on": self.depends_on})[:20]

@dataclass(frozen=True)
class TaskResult:
    stage: str
    name: str
    task_id: str
    status: str
    attempts: int
    detail: str

def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

class Scheduler:
    def __init__(self, store: Path):
        self.store = store
        self.tasks: dict[str, Task] = {}

    def task_dir(self, task: Task) -> Path:
        return self.store / task.stage / task.task_id()

    def _plan(self, tasks):
        self.tasks = {}
        previous_stage = -1
        for task in tasks:
            if task.task_id() in self.tasks:
                raise ConfigError("duplicate task identity")
            if any(dep not in self.tasks for dep in task.depends_on):
                raise ConfigError("dependencies must precede their task")
            current_stage = STAGE_ORDER.index(task.stage)
            if current_stage < previous_stage:
                raise ConfigError("tasks must follow stage batch order")
            previous_stage = current_stage
            self.tasks[task.task_id()] = task

    def _dependency_hashes(self, task):
        hashes = {}
        for dep in task.depends_on:
            receipt = read_json(self.task_dir(self.tasks[dep]) / RECEIPT)
            hashes[dep] = sha256_obj(receipt["outputs"])
        return hashes

    @staticmethod
    def _output(directory, name):
        if name == RECEIPT or "/" in name or "\\" in name:
            raise TaskFailed(f"invalid task output name {name!r}")
        return contained_path(directory, name)

    def _valid_receipt(self, directory: Path, task: Task) -> dict | None:
        try:
            receipt = read_json(directory / RECEIPT)
            validate_document("task_receipt", receipt)
            expected = {"task_id": task.task_id(), "stage": task.stage, "name": task.name,
                        "inputs": task.inputs, "workflow_version": task.workflow_version,
                        "depends_on": list(task.depends_on), "dependency_hashes": self._dependency_hashes(task)}
            if any(receipt[key] != value for key, value in expected.items()):
                return None
            for output in receipt["outputs"].values():
                path = self._output(directory, output["path"])
                if not path.is_file() or sha256_file(path) != output["sha256"]:
                    return None
            if task.verify:
                task.verify(directory)
            return receipt
        except (GranthError, OSError, ValueError, KeyError):
            return None

    def status(self, tasks: list[Task]) -> list[TaskResult]:
        self._plan(tasks)
        done = set()
        results = []
        for task in tasks:
            ok = False
            try:
                if task.preflight:
                    task.preflight()
                ok = all(dep in done for dep in task.depends_on) and self._valid_receipt(self.task_dir(task), task) is not None
            except (GranthError, OSError, ValueError):
                pass
            if ok:
                done.add(task.task_id())
            results.append(TaskResult(task.stage, task.name, task.task_id(), "complete" if ok else "missing", 0,
                                      "verified current inputs, outputs and dependencies" if ok else "no valid current receipt"))
        return results

    def _remove_stale_work(self):
        for stage in STAGE_ORDER:
            for stale in (self.store / stage).glob(".work-*"):
                shutil.rmtree(stale, ignore_errors=True)

    def run(self, tasks: list[Task]) -> list[TaskResult]:
        self._plan(tasks)
        self.store.mkdir(parents=True, exist_ok=True)
        self._remove_stale_work()
        results = []
        done = set()
        for task in tasks:
            task_id = task.task_id()
            try:
                if any(dep not in done for dep in task.depends_on):
                    result = TaskResult(task.stage, task.name, task_id, "blocked", 0, "upstream task not complete")
                else:
                    if task.preflight:
                        task.preflight()
                    directory = self.task_dir(task)
                    if self._valid_receipt(directory, task) is not None:
                        result = TaskResult(task.stage, task.name, task_id, "resumed", 0, "verified receipt reused")
                    else:
                        if directory.exists():
                            shutil.rmtree(directory)
                        result = self._execute(task, task_id, directory)
            except NOT_RETRYABLE as exc:
                result = TaskResult(task.stage, task.name, task_id, "not_validated", 0, str(exc))
            except (GranthError, OSError, ValueError) as exc:
                result = TaskResult(task.stage, task.name, task_id, "failed", 0, str(exc))
            if result.status in ("complete", "resumed"):
                done.add(task_id)
            results.append(result)
            with (self.store / RUN_LOG).open("a", encoding="utf-8") as handle:
                handle.write(json.dumps({"at": _now(), **asdict(result)}, ensure_ascii=False) + "\n")
        return results

    def _execute(self, task, task_id, directory):
        detail = ""
        for attempt in range(1, task.max_attempts + 1):
            work = self.store / task.stage / f".work-{task_id}-{uuid.uuid4().hex[:8]}"
            work.mkdir(parents=True)
            try:
                files = task.run(work)
                if task.preflight:
                    task.preflight()
                if task.verify:
                    task.verify(work)
                self._seal(task, task_id, work, files, attempt)
                os.replace(work, directory)
                return TaskResult(task.stage, task.name, task_id, "complete", attempt, "ok")
            except JobPending as exc:
                shutil.rmtree(work, ignore_errors=True)
                return TaskResult(task.stage, task.name, task_id, "pending", attempt, str(exc))
            except GateFailure as exc:
                shutil.rmtree(work, ignore_errors=True)
                return TaskResult(task.stage, task.name, task_id, "failed", attempt, str(exc))
            except NOT_RETRYABLE as exc:
                shutil.rmtree(work, ignore_errors=True)
                return TaskResult(task.stage, task.name, task_id, "not_validated", attempt, str(exc))
            except Exception as exc:
                shutil.rmtree(work, ignore_errors=True)
                detail = f"attempt {attempt}: {type(exc).__name__}: {exc}"
        return TaskResult(task.stage, task.name, task_id, "failed", task.max_attempts, detail)

    def _seal(self, task, task_id, work, files, attempt):
        if not files:
            raise TaskFailed("task produced no outputs")
        outputs = {}
        for label, name in sorted(files.items()):
            path = self._output(work, name)
            if not path.is_file() or path.stat().st_size == 0:
                raise TaskFailed(f"output {label} missing or empty")
            outputs[label] = {"path": name, "sha256": sha256_file(path)}
        receipt = {"schema_version": 1, "task_id": task_id, "stage": task.stage, "name": task.name,
                   "inputs": task.inputs, "workflow_version": task.workflow_version, "outputs": outputs,
                   "depends_on": list(task.depends_on), "dependency_hashes": self._dependency_hashes(task),
                   "attempts": attempt, "status": "complete", "completed_at": _now()}
        validate_document("task_receipt", receipt)
        atomic_write_json(work / RECEIPT, receipt)
        return receipt
