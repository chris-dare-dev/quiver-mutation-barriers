"""Shared pieces of the scheduler tests: a batch of fake tasks and a way to run it."""

from __future__ import annotations

import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from typing import Any

from taskbatch.config import BatchConfig, parse_config
from taskbatch.memory import MemoryGuard, PollingGuard
from taskbatch.runner import expand
from taskbatch.scheduler import Scheduler
from taskbatch.store import ResultStore

FAKE_RUNNER = Path(__file__).with_name("fake_runner.py")


def fake_config(
    *task_sets: list[dict[str, Any]] | dict[str, Any],
    workers: int = 4,
    memory_budget_mb: int = 800,
    time_seconds: float = 20,
    memory_mb: int = 100,
    tiers: list[dict[str, Any]] | None = None,
) -> BatchConfig:
    """A batch whose task sets are lists of fake-runner items, or tables with "items" and "limits"."""
    sets = [{"kind": "fake", "items": s} if isinstance(s, list) else {"kind": "fake"} | s for s in task_sets]
    return parse_config(
        {
            "name": "fake",
            "scheduler": {"workers": workers, "memory_budget_mb": memory_budget_mb},
            "limits": {"time_seconds": time_seconds, "memory_mb": memory_mb, "tier": tiers or []},
            "tasks": sets,
        }
    )


class Journal:
    """What the fake runner wrote down: which tasks ran, in which order, and when."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def lines(self) -> list[tuple[str, int, float, str]]:
        if not self.path.exists():
            return []
        rows = [line.split(" ", 3) for line in self.path.read_text().splitlines()]
        return [(word, int(pid), float(when), task_id) for word, pid, when, task_id in rows]

    def started(self) -> list[str]:
        return [task_id for word, _, _, task_id in self.lines() if word == "start"]

    def pids(self) -> list[int]:
        return [pid for word, pid, _, _ in self.lines() if word == "start"]

    def intervals(self) -> dict[str, tuple[float, float]]:
        starts = {task_id: when for word, _, when, task_id in self.lines() if word == "start"}
        ends = {task_id: when for word, _, when, task_id in self.lines() if word == "end"}
        return {task_id: (starts[task_id], ends[task_id]) for task_id in ends}


class SchedulerCase(unittest.TestCase):
    """A test case with a run directory, a journal and a fake runner."""

    guard_class: type[MemoryGuard] = PollingGuard

    def setUp(self) -> None:
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.run_dir = Path(scratch.name) / "run"
        self.journal = Journal(Path(scratch.name) / "journal")
        self.runner = (sys.executable, str(FAKE_RUNNER), "--journal", str(self.journal.path))

    def run_batch(self, config: BatchConfig, **options: Any) -> Counter[str]:
        tasks, versions = expand(self.runner, config.description)
        with ResultStore(self.run_dir / "results.jsonl") as store:
            scheduler = Scheduler(
                config=config,
                tasks=tasks,
                store=store,
                run_dir=self.run_dir,
                runner=self.runner,
                guard=self.guard_class(),
                stamp={"run_id": "test", "runner": versions, "code": {"commit": "0" * 40, "dirty": False}},
                **options,
            )
            return scheduler.run()

    def latest(self) -> dict[str, dict[str, Any]]:
        return ResultStore(self.run_dir / "results.jsonl").latest()

    def statuses(self) -> dict[str, str]:
        return {task_id.removeprefix("fake/"): record["status"] for task_id, record in self.latest().items()}
