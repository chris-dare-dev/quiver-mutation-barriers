"""Tasks, limits and outcomes."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class Status(StrEnum):
    """How a task ended.  Every status is terminal: a rerun skips the task unless told to retry it."""

    OK = "ok"  # a value was computed; it agrees with the predicted value, or there is none
    MISMATCH = "mismatch"  # a value was computed and differs from the predicted value
    UNSUPPORTED = "unsupported"  # the runner has no method for this task
    TIMEOUT = "timeout"  # stopped at the time limit
    MEMORY = "memory"  # stopped at the memory limit
    ERROR = "error"  # the runner reported an error
    CRASHED = "crashed"  # the process ended without a result for another reason


# Statuses the runner itself may report; the others are decided by the scheduler.
RUNNER_STATUSES = frozenset({Status.OK, Status.MISMATCH, Status.UNSUPPORTED})

# Statuses that count as the task having been carried out as intended.
COMPLETED_STATUSES = frozenset({Status.OK, Status.UNSUPPORTED})

# Statuses that make a run fail; a task stopped at a limit is neither completed nor failed.
FAILED_STATUSES = frozenset({Status.MISMATCH, Status.ERROR, Status.CRASHED})


@dataclass(frozen=True)
class Limits:
    """The resources one task may use."""

    time_seconds: float
    memory_mb: int

    def as_dict(self) -> dict[str, Any]:
        return {"time_seconds": self.time_seconds, "memory_mb": self.memory_mb}


@dataclass(frozen=True)
class Task:
    """One unit of work, as produced by the runner's expansion of a batch.

    The scheduler reads `id`, `cost`, `set` and `group`; the rest of `payload` is the runner's business
    and is handed back to it unchanged.
    """

    id: str
    kind: str
    cost: float
    set: int
    group: str
    payload: dict[str, Any]

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> Task:
        try:
            return cls(
                id=str(payload["id"]),
                kind=str(payload["kind"]),
                cost=float(payload.get("cost", 0)),
                set=int(payload.get("set", 0)),
                group=str(payload.get("group", payload["kind"])),
                payload=payload,
            )
        except KeyError as missing:
            raise ValueError(f"task without {missing}: {payload!r}") from None
