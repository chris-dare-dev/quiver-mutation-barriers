"""The record of a task that ended: its fields, and how its status is decided.

Nothing here starts a process or reads a file.  The scheduler supplies what it observed (the output of
the task process, how the process ended, what it measured) and writes what comes back.
"""

from __future__ import annotations

import json
import signal
from collections.abc import Callable, Mapping
from typing import Any, NotRequired, TypedDict, cast

from .model import RUNNER_STATUSES, Limits, Status, Task
from .runner import error_lines, parse_result

# keys of a runner's result that have a field of their own in the record; the others go under `detail`
RESULT_FIELDS = frozenset({"status", "value", "predicted", "agrees"})

# keys of a task that say where it stands in its batch, not what it computes
PLACEMENT = frozenset({"set", "group", "cost"})


class Record(TypedDict):
    """One line of results.jsonl (PROTOCOL.md, Records)."""

    task_id: str
    task: dict[str, Any]
    status: str
    value: Any
    predicted: Any
    agrees: bool | None
    detail: dict[str, Any]
    error: str | None
    wall_seconds: float
    cpu_seconds: float
    peak_rss_mb: float
    limits: dict[str, Any]
    memory_guard: str
    exit_code: int | None
    exit_signal: str | None
    started_at: str
    log: str | None
    # the stamp of the run
    run_id: NotRequired[str]
    runner: NotRequired[dict[str, Any]]
    code: NotRequired[dict[str, Any]]


def classify(
    output: str, exit_code: int, *, stopped: Status | None, killed_for_memory: Callable[[], bool]
) -> tuple[Status, dict[str, Any], str | None]:
    """How a task ended, the result its runner printed, and the message to show for a failure.

    `exit_code` is negative for a signal.  `stopped` is the limit at which the scheduler killed the
    process, if it did.  `killed_for_memory` is asked only about a process that someone else killed.
    """
    result = parse_result(output) if exit_code == 0 else None
    if stopped is not None:
        return stopped, {}, None
    if result is not None and result.get("status") in RUNNER_STATUSES:
        return Status(result["status"]), result, None
    if exit_code == -signal.SIGKILL and killed_for_memory():
        return Status.MEMORY, {}, None
    if exit_code > 0:
        return Status.ERROR, {}, error_lines(output) or f"exit status {exit_code}"
    if exit_code < 0:
        return Status.CRASHED, {}, f"ended by signal {signal.Signals(-exit_code).name}"
    return Status.CRASHED, result or {}, "ended without a result"


def make_record(
    task: Task,
    limits: Limits,
    status: Status,
    result: Mapping[str, Any],
    error: str | None,
    *,
    wall_seconds: float,
    cpu_seconds: float,
    peak_rss_mb: float,
    memory_guard: str,
    exit_code: int,
    started_at: str,
    log: str | None,
    stamp: Mapping[str, Any] | None = None,
) -> Record:
    """The record of one task.  `exit_code` is negative for a signal; `stamp` is the same for a whole run."""
    record = {
        "task_id": task.id,
        "task": task.payload,
        "status": str(status),
        "value": result.get("value"),
        "predicted": result.get("predicted", task.payload.get("predicted")),
        "agrees": result.get("agrees"),
        "detail": {key: value for key, value in result.items() if key not in RESULT_FIELDS},
        "error": error,
        "wall_seconds": round(wall_seconds, 3),
        "cpu_seconds": round(cpu_seconds, 3),
        "peak_rss_mb": round(peak_rss_mb, 1),
        "limits": limits.as_dict(),
        "memory_guard": memory_guard,
        "exit_code": exit_code if exit_code >= 0 else None,
        "exit_signal": signal.Signals(-exit_code).name if exit_code < 0 else None,
        "started_at": started_at,
        "log": log,
    }
    return cast(Record, record | dict(stamp or {}))


def answers(record: Mapping[str, Any], task: Mapping[str, Any]) -> bool:
    """Whether a record was computed for this task as it is now.

    The task of the record and `task` must agree on every key that has a value, apart from the place of
    the task in its batch (`set`, `group`, `cost`).  A record computed by another command, or compared
    with another predicted value, says nothing about the task as it is now.
    """

    def essential(payload: Mapping[str, Any]) -> dict[str, Any]:
        kept = {key: value for key, value in payload.items() if key not in PLACEMENT and value is not None}
        return cast(dict[str, Any], json.loads(json.dumps(kept, sort_keys=True)))

    return essential(record["task"]) == essential(task)
