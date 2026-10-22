"""Filesystem stage scheduler: deterministic task IDs, sealed receipts, atomic outputs, retries and resume.

A task's directory is ``<store>/<stage>/<task_id>``. It is created by renaming a fully written
work directory, so a directory either holds a complete, hash-verified result or does not
exist. A rerun reuses a task only when its receipt and every output hash still verify.
Stale ``.work-*`` directories left by a crash are removed at the start of each run.
"""

from __future__ import annotations

import json
import os
import shutil
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from .errors import CapabilityDisabled, ConfigError, IntegrationUnavailable, TaskFailed
from .integrity import atomic_write_json, read_json, sha256_file, sha256_obj
from .schemas import SchemaError, validate_document

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

    def __post_init__(self) -> None:
        if self.stage not in STAGE_ORDER:
            raise ConfigError(f"unknown stage {self.stage!r}")
        if self.max_attempts < 1:
            raise ConfigError("max_attempts must be at least 1")

    def task_id(self) -> str:
        identity = {
            "stage": self.stage,
            "name": self.name,
            "inputs": self.inputs,
            "workflow_version": self.workflow_version,
        }
        return sha256_obj(identity)[:20]


@dataclass(frozen=True)
class TaskResult:
    stage: str
    name: str
    task_id: str
    status: str
    attempts: int
    detail: str


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Scheduler:
    def __init__(self, store: Path) -> None:
        self.store = store

    def task_dir(self, task: Task) -> Path:
        return self.store / task.stage / task.task_id()

    def _valid_receipt(self, directory: Path) -> dict | None:
        receipt_path = directory / RECEIPT
        if not receipt_path.is_file():
            return None
        try:
            receipt = read_json(receipt_path)
            validate_document("task_receipt", receipt)
        except (SchemaError, ValueError):
            return None
        if receipt["task_id"] != directory.name:
            return None
        for output in receipt["outputs"].values():
            path = directory / output["path"]
            if not path.is_file() or sha256_file(path) != output["sha256"]:
                return None
        return receipt

    def _remove_stale_work(self) -> None:
        for stage in STAGE_ORDER:
            folder = self.store / stage
            if folder.is_dir():
                for stale in folder.glob(".work-*"):
                    shutil.rmtree(stale, ignore_errors=True)

    def status(self, tasks: list[Task]) -> list[TaskResult]:
        results = []
        for task in tasks:
            ok = self._valid_receipt(self.task_dir(task)) is not None
            results.append(
                TaskResult(
                    task.stage,
                    task.name,
                    task.task_id(),
                    "complete" if ok else "missing",
                    0,
                    "verified receipt" if ok else "no valid receipt",
                )
            )
        return results

    def run(self, tasks: list[Task]) -> list[TaskResult]:
        self.store.mkdir(parents=True, exist_ok=True)
        self._remove_stale_work()
        done: set[str] = set()
        results: list[TaskResult] = []
        for task in tasks:
            task_id = task.task_id()
            if any(dep not in done for dep in task.depends_on):
                result = TaskResult(task.stage, task.name, task_id, "blocked", 0, "upstream task not complete")
            else:
                directory = self.task_dir(task)
                if self._valid_receipt(directory) is not None:
                    result = TaskResult(task.stage, task.name, task_id, "resumed", 0, "verified receipt reused")
                else:
                    if directory.exists():
                        shutil.rmtree(directory)
                    result = self._execute(task, task_id, directory)
            if result.status in ("complete", "resumed"):
                done.add(task_id)
            results.append(result)
            self._log(result)
        return results

    def _execute(self, task: Task, task_id: str, directory: Path) -> TaskResult:
        detail = ""
        for attempt in range(1, task.max_attempts + 1):
            work = self.store / task.stage / f".work-{task_id}-{uuid.uuid4().hex[:8]}"
            work.mkdir(parents=True)
            try:
                files = task.run(work)
                self._seal(task, task_id, work, files, attempt)
                os.replace(work, directory)
                return TaskResult(task.stage, task.name, task_id, "complete", attempt, "ok")
            except NOT_RETRYABLE as exc:
                shutil.rmtree(work, ignore_errors=True)
                return TaskResult(task.stage, task.name, task_id, "not_validated", attempt, str(exc))
            except Exception as exc:  # noqa: BLE001 - every failure is recorded and retried
                shutil.rmtree(work, ignore_errors=True)
                detail = f"attempt {attempt}: {type(exc).__name__}: {exc}"
        return TaskResult(task.stage, task.name, task_id, "failed", task.max_attempts, detail)

    def _seal(self, task: Task, task_id: str, work: Path, files: dict[str, str], attempt: int) -> dict:
        if not files:
            raise TaskFailed("task produced no outputs")
        outputs = {}
        for label, name in sorted(files.items()):
            if name == RECEIPT or "/" in name or "\\" in name:
                raise TaskFailed(f"invalid output name {name!r}")
            path = work / name
            if not path.is_file() or path.stat().st_size == 0:
                raise TaskFailed(f"output {label} missing or empty: {name}")
            outputs[label] = {"path": name, "sha256": sha256_file(path)}
        receipt = {
            "schema_version": 1,
            "task_id": task_id,
            "stage": task.stage,
            "name": task.name,
            "inputs": task.inputs,
            "workflow_version": task.workflow_version,
            "outputs": outputs,
            "attempts": attempt,
            "status": "complete",
            "completed_at": _now(),
        }
        validate_document("task_receipt", receipt)
        atomic_write_json(work / RECEIPT, receipt)
        return receipt

    def _log(self, result: TaskResult) -> None:
        line = {"at": _now(), **asdict(result)}
        with (self.store / RUN_LOG).open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(line, ensure_ascii=False) + "\n")
